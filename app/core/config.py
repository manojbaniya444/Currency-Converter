"""Configuration settings for the application."""

from typing import Any, Dict, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings."""

    PROJECT_NAME: str = "Currency Converter App"
    VERSION: str = "0.1.0"
    DEV_MODE: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="info")

    EXCHANGE_API_KEY: Optional[str] = None
    EXCHANGE_API_URL: str = Field(default="https://api.exchangerate-api.com/v4/latest")

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_TTL: int = Field(default=3600)

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate the log level setting."""
        allowed_levels = ["debug", "info", "warning", "error"]
        if v.lower() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.lower()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    def dict_for_docs(self) -> Dict[str, Any]:
        """Return a dict of settings for documentation."""
        return {
            "app_name": self.PROJECT_NAME,
            "version": self.VERSION,
            "dev_mode": self.DEV_MODE,
            "debug": self.DEBUG,
        }


settings = Settings()
