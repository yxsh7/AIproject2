"""Base AI model utilities for the application"""
import logging
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def get_ai_chat_model(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
):
    """
    Get a configured AI chat model based on settings or parameters

    Args:
        provider: AI provider ("openai" or "anthropic") - defaults to settings
        model_name: Model name - defaults to settings
        temperature: Temperature for generation - defaults to settings

    Returns:
        Configured LLM instance (ChatOpenAI or ChatAnthropic)

    Raises:
        ValueError: If required API key is missing or provider is unsupported
    """
    provider = provider or settings.AI_MODEL_PROVIDER
    model_name = model_name or settings.AI_MODEL_NAME
    temperature = temperature if temperature is not None else settings.AI_MODEL_TEMPERATURE

    if provider == "openai":
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        llm_kwargs = {
            "model": model_name,
            "openai_api_key": api_key,
            "temperature": temperature,
            "max_tokens": settings.AI_MODEL_MAX_TOKENS,
        }

        # Add base_url if using OpenRouter or custom endpoint
        if settings.OPENAI_API_BASE:
            llm_kwargs["base_url"] = settings.OPENAI_API_BASE

        llm = ChatOpenAI(**llm_kwargs)
        logger.info(f"Initialized AI model: OpenAI/{model_name}")
        return llm

    elif provider == "anthropic":
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")

        llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            temperature=temperature,
            max_tokens=settings.AI_MODEL_MAX_TOKENS,
        )
        logger.info(f"Initialized AI model: Anthropic/{model_name}")
        return llm

    else:
        raise ValueError(f"Unsupported AI provider: {provider}. Use 'openai' or 'anthropic'.")


def check_ai_available() -> bool:
    """
    Check if AI functionality is available (API key configured)

    Returns:
        True if at least one AI provider is configured
    """
    if settings.AI_MODEL_PROVIDER == "openai":
        return bool(settings.OPENAI_API_KEY)
    elif settings.AI_MODEL_PROVIDER == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    return False


def get_ai_status() -> dict:
    """
    Get detailed AI configuration status

    Returns:
        Dict with configuration details
    """
    return {
        "provider": settings.AI_MODEL_PROVIDER,
        "model": settings.AI_MODEL_NAME,
        "available": check_ai_available(),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
        "custom_base_url": bool(settings.OPENAI_API_BASE),
    }
