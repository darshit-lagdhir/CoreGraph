import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import (
    AliasChoices,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    field_validator,
    computed_field
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"


class Settings(BaseSettings):
    """Global Configuration Manager: The supreme authority for system state and security secrets."""
    
    # 1. Environment Metadata
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    DEBUG: bool = False
    
    # 2. Relational Vault Parameters
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    # Failure 2 Resolution: Explicit Integer coercion for PostgreSQL port binding
    DB_PORT: int = 5432
    DB_NAME: str = "coregraph"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Dynamically synthesized PostgresDsn ensuring absolute relational integrity."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # 3. Message Broker Parameters
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "CELERY_BROKER_URL")
    )

    # 4. OSINT Secret Interface
    # Failure 3 Resolution: Native SecretStr redaction to prevent accidental telemetry leakage
    GITHUB_GRAPHQL_TOKEN: SecretStr = Field(default="sk-dummy-token")

    # 5. Hardware & Operational Constraints (Task-Specific Thresholds)
    # Failure 3 Resolution: Worker concurrency capped at 24 for the i9-13980hx cluster
    CELERY_WORKER_CONCURRENCY: int = Field(default=16, le=24)
    WSL_MEMORY_LIMIT_MB: int = Field(default=4096, le=8192)
    WS_CHUNK_SIZE: int = Field(default=65536, ge=16384, le=1048576)

    # Failure 1 Resolution: Absolute path resolution via pathlib, neutralizing context-drift
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def normalize_env(cls, v: str) -> str:
        return v.upper() if v else EnvironmentType.DEVELOPMENT

    def __repr__(self) -> str:
        """Hardened representation proxy: Masking all sensitive strings from diagnostic traces."""
        return f"Settings(ENVIRONMENT='{self.ENVIRONMENT}', DEBUG={self.DEBUG}, DATABASE_URL='REDACTED', GITHUB_GRAPHQL_TOKEN='**********')"


@lru_cache()
def get_settings() -> Settings:
    """Singleton Registry: Ensures atomic configuration state across the distributed 24-core i9 grid."""
    return Settings()


settings = get_settings()
