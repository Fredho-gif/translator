"""settings.py — Réglages modifiables via variables d'environnement ou .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    deepl_api_key: str | None = None
    network_timeout_seconds: int = 20
    parallel_translations: int = 5
    log_level: str = "INFO"


settings = Settings()