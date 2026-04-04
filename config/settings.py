"""
Central configuration from environment (.env / process env).
"""

from __future__ import annotations
from utils.logger import setup_logger
from functools import lru_cache
from typing import Optional
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = setup_logger(__name__)

def _secret_plain(secret: Optional[SecretStr]) -> Optional[str]:
    if secret is None:
        return None
    v = secret.get_secret_value().strip()
    return v or None


class GitCanvasSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    github_token: Optional[SecretStr] = Field(default=None)
    openai_api_key: Optional[SecretStr] = Field(default=None)
    gemini_api_key: Optional[SecretStr] = Field(default=None)

    @field_validator("github_token", "openai_api_key", "gemini_api_key", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    def github_token_value(self) -> Optional[str]:
        return _secret_plain(self.github_token)

    def openai_api_key_value(self) -> Optional[str]:
        return _secret_plain(self.openai_api_key)

    def gemini_api_key_value(self) -> Optional[str]:
        return _secret_plain(self.gemini_api_key)

    @property
    def has_github_token(self) -> bool:
        return self.github_token_value() is not None

    @property
    def has_any_llm_key(self) -> bool:
        return bool(self.openai_api_key_value() or self.gemini_api_key_value())

    def log_backend_warnings(self) -> None:
        """Log non-fatal configuration issues when starting the API."""
        if not self.has_github_token:
            logger.warning(
                "GITHUB_TOKEN is not set: GitHub requests use anonymous rate limits "
                "unless clients send Authorization: Bearer <token>."
            )
        if not self.has_any_llm_key:
            logger.warning(
                "Neither OPENAI_API_KEY nor GEMINI_API_KEY is set: "
                "the Streamlit AI roast feature has no cloud LLM keys in this environment."
            )


@lru_cache
def get_settings() -> GitCanvasSettings:
    return GitCanvasSettings()
