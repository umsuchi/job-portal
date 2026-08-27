"""Application settings, loaded from environment (see .env.example)."""
from __future__ import annotations

from functools import lru_cache
from typing import List
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Database -----------------------------------------------------------
    database_url: str = Field(alias="DATABASE_URL")

    # --- Auth ---------------------------------------------------------------
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # --- AI -----------------------------------------------------------------
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-120b", alias="GROQ_MODEL")
    groq_timeout_seconds: float = Field(default=12.0, alias="GROQ_TIMEOUT_SECONDS")
    suggestions_cache_ttl_minutes: int = Field(
        default=60, alias="SUGGESTIONS_CACHE_TTL_MINUTES"
    )

    # --- App ----------------------------------------------------------------
    # Kept as a raw string: pydantic-settings tries to JSON-decode complex
    # types straight from the env file, which a comma-separated list is not.
    cors_origins_raw: str = Field(default="", alias="CORS_ORIGINS")
    env: str = Field(default="development", alias="ENV")

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.env.lower() in {"production", "prod"}

    @property
    def async_database_url(self) -> str:
        """Normalize a pasted Postgres URL into an asyncpg-compatible one.

        Neon hands out ``postgresql://...?sslmode=require&channel_binding=require``.
        asyncpg does not understand libpq's ``sslmode``/``channel_binding`` query
        args, so they are stripped here and TLS is requested via ``connect_args``
        in ``db/session.py`` instead.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

    @property
    def sync_database_url(self) -> str:
        """psycopg-free sync URL, used only by Alembic's offline mode."""
        return self.async_database_url.replace("+asyncpg", "")

    @property
    def requires_ssl(self) -> bool:
        return "sslmode=disable" not in self.database_url and not self.is_sqlite

    @property
    def is_sqlite(self) -> bool:
        return self.async_database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
