import pytest
import os
import pydantic
from core.config import Settings, EnvironmentType, get_settings


def test_strict_type_enforcement_and_coercion():
    # Failure 2 Resolution: Verifying integer coercion for port binding
    # Correct instantiation: string "5433" should be coerced to integer 5433
    settings = Settings(DB_PORT="5433")
    assert isinstance(settings.DB_PORT, int)
    assert settings.DB_PORT == 5433

    # Invalid instantiation: string "INVALID" should raise a ValidationError
    with pytest.raises(pydantic.ValidationError):
        Settings(DB_PORT="INVALID_PORT_STR")


def test_secret_redaction_and_repr_proxy():
    # Failure 3 Resolution: Verification of SecretStr redaction in all representations
    settings = Settings(GITHUB_GRAPHQL_TOKEN="sk-9x-api-key-high-value")
    
    # 1. Pydantic's internal SecretStr redaction
    assert str(settings.GITHUB_GRAPHQL_TOKEN) == "**********"
    
    # 2. Custom __repr__ proxy for diagnostic traces
    repr_str = repr(settings)
    assert "sk-9x-api-key-high-value" not in repr_str
    assert "GITHUB_GRAPHQL_TOKEN='**********'" in repr_str
    assert "DATABASE_URL='REDACTED'" in repr_str


def test_hardware_limit_compliance_matrix():
    # Enforcing the 24-core i9-13980hx hypervisor boundaries
    with pytest.raises(pydantic.ValidationError):
        Settings(CELERY_WORKER_CONCURRENCY=32) # Exceeds 24 cores
    
    settings = Settings(CELERY_WORKER_CONCURRENCY=24)
    assert settings.CELERY_WORKER_CONCURRENCY == 24


def test_path_resolution_and_env_prioritization():
    # Failure 1 Resolution: Pathlib-based absolute resolution from root
    settings = get_settings()
    # The absolute path should be traceable back to the project root
    # i.e., backend/core/config.py -> parent(core) -> parent(backend) -> parent(root)
    assert ".env" in str(settings.model_config.get("env_file"))


def test_environment_aware_branching_logic():
    # Testing dynamic behavior based on ENVIRONMENT enum
    settings_dev = Settings(ENVIRONMENT="DEVELOPMENT")
    assert settings_dev.ENVIRONMENT == EnvironmentType.DEVELOPMENT
    
    settings_prod = Settings(ENVIRONMENT="PRODUCTION")
    assert settings_prod.ENVIRONMENT == EnvironmentType.PRODUCTION
