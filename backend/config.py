"""
Runtime configuration loaded from environment / `.env`.

Uses pydantic-settings so values are validated once at startup and can be
imported anywhere as `from config import settings`.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    cache_dir: str = "cache"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def cache_dir_path(self) -> Path:
        root = Path(__file__).resolve().parent
        p = Path(self.cache_dir)
        return p if p.is_absolute() else root / p

    @property
    def cache_vocals_dir(self) -> Path:
        return self.cache_dir_path / "vocals"


settings = Settings()
