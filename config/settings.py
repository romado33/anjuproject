"""Application settings loaded from environment (no secrets in code)."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime configuration. All paths are resolved relative to project root."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_chat_model: str = Field(default="gpt-4o")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    classification_confidence_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    chroma_persist_directory: str = Field(default="data/chroma_db")
    case_store_path: str = Field(default="data/cases.sqlite3")
    mock_integration_latency_seconds: float = Field(default=0.15, ge=0.0)
    log_level: str = Field(default="INFO")
    offline_demo: bool = Field(
        default=False,
        description="Force keyword-based routing (no OpenAI calls).",
    )
    luminee_book_demo_url: str = Field(
        default="https://www.anjusoftware.com/eclinical/luminee/",
        description="Marketing / demo request URL for Luminee (sidebar promo).",
    )
    luminee_protocol_summarizer_url: str = Field(
        default="https://luminee-prod1tm1.anjuclinical.com/login",
        description="Luminee Hub / Protocol Summarizer entry (sidebar promo).",
    )
    integration_settings_path: str = Field(
        default="data/integration_settings.json",
        description="JSON file for adapter base URLs and parameters (Integrations page).",
    )

    @property
    def project_root(self) -> Path:
        return _project_root()

    def chroma_path(self) -> Path:
        p = Path(self.chroma_persist_directory)
        if not p.is_absolute():
            p = self.project_root / p
        return p

    def case_store_full_path(self) -> Path:
        p = Path(self.case_store_path)
        if not p.is_absolute():
            p = self.project_root / p
        return p

    def integration_settings_full_path(self) -> Path:
        p = Path(self.integration_settings_path)
        if not p.is_absolute():
            p = self.project_root / p
        return p

    def use_offline_mode(self) -> bool:
        """Offline when forced or when no API key is configured."""
        return self.offline_demo or not self.openai_api_key.strip()


def get_settings() -> Settings:
    return Settings()
