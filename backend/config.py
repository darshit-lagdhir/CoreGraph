import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute path for .env to ensure stability across execution contexts
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    GITHUB_GRAPHQL_TOKEN: str
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
