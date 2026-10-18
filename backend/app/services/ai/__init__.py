import logging
from app.config import settings
from app.services.ai.provider import AIProvider
from app.services.ai.fallback_provider import FallbackAIProvider
from app.services.ai.gemini_provider import GeminiAIProvider
from app.services.ai.ollama_provider import OllamaAIProvider

logger = logging.getLogger(__name__)


def get_ai_provider() -> AIProvider:
    """Returns the configured AI provider. Falls back to FallbackAIProvider if unavailable or unconfigured."""
    provider_name = getattr(settings, "AI_PROVIDER", "ollama").lower().strip()
    ollama_key = getattr(settings, "OLLAMA_API_KEY", "").strip()
    gemini_key = getattr(settings, "GEMINI_API_KEY", "").strip()

    if provider_name == "ollama" and ollama_key and not ollama_key.startswith("PASTE_"):
        return OllamaAIProvider(
            api_key=ollama_key,
            model=getattr(settings, "OLLAMA_MODEL", "glm-5.3-flash"),
            base_url=getattr(settings, "OLLAMA_BASE_URL", "https://ollama.com"),
        )
    elif provider_name == "gemini" and gemini_key:
        return GeminiAIProvider(api_key=gemini_key)
    
    return FallbackAIProvider()


__all__ = ["AIProvider", "get_ai_provider", "FallbackAIProvider", "GeminiAIProvider", "OllamaAIProvider"]

