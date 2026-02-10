from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.encryption import encrypt_value, decrypt_value
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.services.kaggle_service import KaggleService
from pydantic import BaseModel


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class KaggleCredentialsRequest(BaseModel):
    kaggle_username: str
    kaggle_key: str


class KaggleCredentialsResponse(BaseModel):
    has_credentials: bool
    kaggle_username: Optional[str] = None
    is_valid: Optional[bool] = None


class LLMSettingsRequest(BaseModel):
    provider: str  # 'openai', 'anthropic', 'google'
    api_key: str


class LLMSettingsResponse(BaseModel):
    has_settings: bool
    provider: Optional[str] = None
    is_configured: bool = False


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    # Check if user already exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access tokens"""
    user = await AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return AuthService.create_tokens(str(user.id))


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token"""
    token_data = AuthService.decode_token(refresh_token)

    if not token_data or token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from uuid import UUID
    user = await AuthService.get_user_by_id(db, UUID(token_data.sub))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return AuthService.create_tokens(str(user.id))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information"""
    return current_user


@router.get("/kaggle-credentials", response_model=KaggleCredentialsResponse)
async def get_kaggle_credentials(
    current_user: User = Depends(get_current_user),
):
    """Check if user has Kaggle credentials stored"""
    has_credentials = bool(
        current_user.kaggle_username and current_user.kaggle_key_encrypted
    )

    return KaggleCredentialsResponse(
        has_credentials=has_credentials,
        kaggle_username=current_user.kaggle_username if has_credentials else None,
    )


@router.post("/kaggle-credentials", response_model=KaggleCredentialsResponse)
async def save_kaggle_credentials(
    credentials: KaggleCredentialsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save Kaggle credentials for the user"""
    # Validate credentials first
    is_valid, message = KaggleService.validate_credentials(
        credentials.kaggle_username,
        credentials.kaggle_key
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Kaggle credentials: {message}"
        )

    # Encrypt and save
    current_user.kaggle_username = credentials.kaggle_username
    current_user.kaggle_key_encrypted = encrypt_value(credentials.kaggle_key)

    await db.commit()
    await db.refresh(current_user)

    return KaggleCredentialsResponse(
        has_credentials=True,
        kaggle_username=current_user.kaggle_username,
        is_valid=True
    )


@router.delete("/kaggle-credentials")
async def delete_kaggle_credentials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove stored Kaggle credentials"""
    current_user.kaggle_username = None
    current_user.kaggle_key_encrypted = None

    await db.commit()

    return {"message": "Kaggle credentials removed"}


# LLM Settings endpoints
@router.get("/llm-settings", response_model=LLMSettingsResponse)
async def get_llm_settings(
    current_user: User = Depends(get_current_user),
):
    """Get user's LLM API settings"""
    has_settings = bool(
        current_user.llm_provider and current_user.llm_api_key_encrypted
    )

    return LLMSettingsResponse(
        has_settings=has_settings,
        provider=current_user.llm_provider if has_settings else None,
        is_configured=has_settings
    )


@router.post("/llm-settings", response_model=LLMSettingsResponse)
async def save_llm_settings(
    settings: LLMSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save LLM API settings for the user"""
    # Validate provider
    valid_providers = ['openai', 'anthropic', 'google']
    if settings.provider not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {valid_providers}"
        )

    # Validate API key by making a test call
    try:
        from app.services.llm_service import get_llm_provider
        provider = get_llm_provider(settings.provider, settings.api_key)
        # Simple validation - just check if provider initializes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API key: {str(e)}"
        )

    # Encrypt and save
    current_user.llm_provider = settings.provider
    current_user.llm_api_key_encrypted = encrypt_value(settings.api_key)

    await db.commit()
    await db.refresh(current_user)

    return LLMSettingsResponse(
        has_settings=True,
        provider=current_user.llm_provider,
        is_configured=True
    )


@router.delete("/llm-settings")
async def delete_llm_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove stored LLM API settings"""
    current_user.llm_provider = None
    current_user.llm_api_key_encrypted = None

    await db.commit()

    return {"message": "LLM settings removed"}


@router.get("/llm-providers")
async def get_available_providers():
    """Get list of available LLM providers"""
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "GPT-4o and other OpenAI models",
                "signup_url": "https://platform.openai.com/signup",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "description": "Claude models for advanced reasoning",
                "signup_url": "https://console.anthropic.com",
                "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"]
            },
            {
                "id": "google",
                "name": "Google AI",
                "description": "Gemini models",
                "signup_url": "https://aistudio.google.com/apikey",
                "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
            }
        ]
    }
