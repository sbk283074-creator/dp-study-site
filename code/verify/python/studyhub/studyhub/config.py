from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STUDYHUB_", env_file=".env")

    database_url: str = "sqlite+pysqlite:///./studyhub.db"
    secret_key: str = "dev-only-insecure-secret"
    session_cookie_name: str = "studyhub_session"
    session_ttl_seconds: int = 60 * 60 * 24 * 30
    cookie_secure: bool = False  # True behind HTTPS in production
    new_cards_per_day: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
