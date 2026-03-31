import abc
from typing import Dict, Any, AsyncGenerator


class EcosystemAdapter(abc.ABC):
    """
    Module 4 - Task 022: Base Ecosystem Adapter.
    Polymorphic interface for cross-registry extraction.
    """

    __slots__ = ("_client",)

    def __init__(self, client: Any):
        self._client = client

    @abc.abstractmethod
    async def extract_manifest(self, purl: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronously streams version records from the native registry."""
        yield {}

    @abc.abstractmethod
    def resolve_coordinates(self, dependency_string: str) -> str:
        """Translates ecosystem-specific version constraints into normalized formats."""
        return dependency_string

    @abc.abstractmethod
    def extract_actor_identity(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts the Social Chain of Custody for the dependency maintainers."""
        return {}
