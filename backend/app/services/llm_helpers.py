"""Helper functions for LLM service"""

from typing import Optional, Tuple
from app.models.user import User
from app.core.config import settings
from app.core.encryption import decrypt_value
from app.services.llm_service import LLMService


def get_user_llm_service(user: User) -> LLMService:
    """
    Get an LLM service configured with user's API settings.
    Falls back to free Gemini tier if user hasn't configured their own key.

    Args:
        user: User object with llm_provider and llm_api_key_encrypted

    Returns:
        LLMService configured with appropriate API key

    Raises:
        ValueError: If no API key available (user's or fallback)
    """
    # First, try user's own API key
    if user.llm_provider and user.llm_api_key_encrypted:
        api_key = decrypt_value(user.llm_api_key_encrypted)
        return LLMService(
            provider=user.llm_provider,
            api_key=api_key
        )

    # Fallback to free Gemini tier
    if settings.GEMINI_FREE_API_KEY:
        return LLMService(
            provider='google',
            api_key=settings.GEMINI_FREE_API_KEY
        )

    # Legacy fallback to app-level Anthropic key
    if settings.API_KEY:
        return LLMService(
            provider='anthropic',
            api_key=settings.API_KEY
        )

    # No API key available
    raise ValueError(
        "No API key configured. Please go to Settings and add your API key "
        "(OpenAI, Anthropic, or Google Gemini)."
    )


def get_llm_service_with_info(user: User) -> Tuple[LLMService, dict]:
    """
    Get an LLM service and info about which tier is being used.

    Args:
        user: User object

    Returns:
        Tuple of (LLMService, info_dict)
        info_dict contains:
            - using_free_tier: bool
            - provider: str
            - message: str (optional, shown to user)
    """
    # First, try user's own API key
    if user.llm_provider and user.llm_api_key_encrypted:
        api_key = decrypt_value(user.llm_api_key_encrypted)
        return LLMService(
            provider=user.llm_provider,
            api_key=api_key
        ), {
            'using_free_tier': False,
            'provider': user.llm_provider,
        }

    # Fallback to free Gemini tier
    if settings.GEMINI_FREE_API_KEY:
        return LLMService(
            provider='google',
            api_key=settings.GEMINI_FREE_API_KEY
        ), {
            'using_free_tier': True,
            'provider': 'google',
            'message': 'Using free tier (limited). Add your own API key in Settings for better performance.',
        }

    # Legacy fallback to app-level Anthropic key
    if settings.API_KEY:
        return LLMService(
            provider='anthropic',
            api_key=settings.API_KEY
        ), {
            'using_free_tier': True,
            'provider': 'anthropic',
        }

    # No API key available
    raise ValueError(
        "No API key configured. Please go to Settings and add your API key "
        "(OpenAI, Anthropic, or Google Gemini)."
    )


def is_llm_available(user: User) -> bool:
    """
    Check if LLM service is available for the user.

    Args:
        user: User object

    Returns:
        True if LLM is available (user's key or fallback)
    """
    # User has their own key
    if user.llm_provider and user.llm_api_key_encrypted:
        return True

    # Fallback available
    if settings.GEMINI_FREE_API_KEY or settings.API_KEY:
        return True

    return False


def get_llm_status(user: User) -> dict:
    """
    Get the LLM configuration status for a user.

    Args:
        user: User object

    Returns:
        Status dict with configuration info
    """
    has_own_key = bool(user.llm_provider and user.llm_api_key_encrypted)
    has_free_fallback = bool(settings.GEMINI_FREE_API_KEY or settings.API_KEY)

    return {
        'has_own_key': has_own_key,
        'provider': user.llm_provider if has_own_key else None,
        'has_free_fallback': has_free_fallback,
        'is_available': has_own_key or has_free_fallback,
        'using_free_tier': not has_own_key and has_free_fallback,
    }
