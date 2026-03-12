"""
config.py — Application settings loaded from environment variables.
Uses pydantic-settings for typed configuration with .env file support.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration. Reads from .env file and environment variables."""

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ANTHROPIC_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    APP_NAME: str = "Ide/AI"

    # OAuth — leave empty to disable a provider
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    # Email — Resend
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@ideaforge.dev"
    INBOX_DOMAIN: str = "inbox.ideaforge.dev"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def async_database_url(self) -> str:
        """Return DATABASE_URL with the asyncpg driver scheme.

        Railway provides ``postgresql://...`` but SQLAlchemy's async engine
        requires ``postgresql+asyncpg://...``. This property handles the
        conversion automatically so the raw env var works in both environments.
        """
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
