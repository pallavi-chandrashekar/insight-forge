"""Helper functions for LLM service"""

from typing import Optional
from app.models.user import User
from app.core.encryption import decrypt_value
from app.services.llm_service import LLMService


def get_user_llm_service(user: User) -> LLMService:
    """
    Get an LLM service configured with user's API settings.

    Args:
        user: User object with llm_provider and llm_api_key_encrypted

    Returns:
        LLMService configured with user's API key

    Raises:
        ValueError: If user hasn't configured LLM settings
    """
    if not user.llm_provider or not user.llm_api_key_encrypted:
        raise ValueError(
            "LLM not configured. Please go to Settings and add your API key."
        )

    api_key = decrypt_value(user.llm_api_key_encrypted)

    return LLMService(
        provider=user.llm_provider,
        api_key=api_key
    )


def get_llm_service_optional(user: User) -> Optional[LLMService]:
    """
    Get an LLM service if user has configured it, otherwise None.

    Args:
        user: User object

    Returns:
        LLMService or None if not configured
    """
    try:
        return get_user_llm_service(user)
    except ValueError:
        return None
