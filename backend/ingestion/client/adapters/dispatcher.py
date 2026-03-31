from typing import Dict, Any, Optional
from .base import EcosystemAdapter
from .pypi import PyPIAdapter
from .github import GitHubAdapter

class RegistryDispatcher:
    """
    Module 4 - Task 022: Universal Adapter Registry.
    O(1) Polymorphic dispatch routing between the Global Intake Scheduler 
    and the physical network extraction drivers.
    """
    __slots__ = ('_adapters', '_client_pool')
    _instance: Optional['RegistryDispatcher'] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> 'RegistryDispatcher':
        if cls._instance is None:
            cls._instance = super(RegistryDispatcher, cls).__new__(cls)
        return cls._instance

    def __init__(self, client_pool: Any = None):
        if hasattr(self, '_adapters'):
            return
            
        self._client_pool = client_pool
        
        # Pre-compiled mapping array preventing dict allocation on every request
        self._adapters: Dict[str, EcosystemAdapter] = {
            'pkg:pypi': PyPIAdapter(self._client_pool),
            'pkg:github': GitHubAdapter(self._client_pool)
        }

    def register_adapter(self, prefix: str, adapter: EcosystemAdapter) -> None:
        """Inject runtime-defined ecosystems."""
        self._adapters[prefix] = adapter

    def get_adapter(self, purl: str) -> Optional[EcosystemAdapter]:
        """
        O(1) Ecosystem resolution via PURL prefixes.
        E.g., 'pkg:pypi/requests' returns the active PyPIAdapter instantiation.
        """
        if purl.startswith('pkg:'):
            prefix = purl.split('/')[0]
            return self._adapters.get(prefix)
        return None
