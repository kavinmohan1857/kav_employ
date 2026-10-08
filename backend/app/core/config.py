from datetime import date
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "KavEmploy API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://kavemploy:kavemploy@localhost:5433/kavemploy"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    candidate_graduation_date: date = date(2026, 5, 1)
    candidate_skills: list[str] = []

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
