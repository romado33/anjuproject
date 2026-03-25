"""Shared OpenAI client factory."""

from openai import OpenAI

from config.settings import Settings, get_settings


def get_openai_client(settings: Settings | None = None) -> OpenAI:
    s = settings or get_settings()
    if not s.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to .env or enable offline mode (OFFLINE_MODE=true)."
        )
    return OpenAI(api_key=s.openai_api_key)
