from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelProvider(StrEnum):
    FAKE = "fake"
    OLLAMA = "ollama"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_purchase_workflow"
    frontend_origin: str = "http://localhost:5173"
    identity_signing_secret: str = "development-identity-signing-secret"
    identity_jwt_signing_secret: str = "development-jwt-signing-secret-change-me"
    identity_access_token_minutes: int = 15
    workflow_model_provider: ModelProvider = ModelProvider.FAKE
    workflow_model_name: str = "qwen3:8b"
    workflow_model_base_url: str | None = None
    workflow_model_timeout_seconds: float = 30.0
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
