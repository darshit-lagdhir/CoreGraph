from .base import EcosystemAdapter
from .pypi import PyPIAdapter
from .github import GitHubAdapter
from .dispatcher import RegistryDispatcher

__all__ = [
    'EcosystemAdapter',
    'PyPIAdapter',
    'GitHubAdapter',
    'RegistryDispatcher'
]
