import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, RootModel


class NormalizedDependency(BaseModel):
    name: str
    version_range: str
    ecosystem: str


class BaseEcosystemClient(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    def normalize_package_name(self, name: str) -> str:
        """Returns the canonical ID of the package within the ecosystem."""
        pass

    @abstractmethod
    def normalize_version(self, version: str) -> str:
        """Strips 'v' prefixes and metadata for point-version comparison."""
        pass

    @abstractmethod
    async def fetch_metadata(self, name: str) -> Dict[str, Any]:
        """Retrieves raw metadata from the registry."""
        pass

    @abstractmethod
    def resolve_dependencies(
        self, metadata: Dict[str, Any], version: Optional[str] = None
    ) -> List[NormalizedDependency]:
        """Extracts dependencies mapping to internal normalized models."""
        pass


class PyPIClient(BaseEcosystemClient):
    def normalize_package_name(self, name: str) -> str:
        # PEP 503: lower(), replace [-_.]+ with -
        return re.sub(r"[-_.]+", "-", name).lower()

    def normalize_version(self, version: str) -> str:
        # PEP 440 strip: focus on major.minor.patch
        match = re.search(r"(\d+\.\d+\.\d+)", version)
        return match.group(1) if match else version

    async def fetch_metadata(self, name: str) -> Dict[str, Any]:
        url = f"https://pypi.org/pypi/{name}/json"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()  # type: ignore

    def resolve_dependencies(
        self, metadata: Dict[str, Any], version: Optional[str] = None
    ) -> List[NormalizedDependency]:
        # Utilizing 'info' -> 'requires_dist'
        info = metadata.get("info", {})
        requires_dist = info.get("requires_dist") or []

        deps = []
        for dist in requires_dist:
            # Simple parsing: 'requests (>=2.28.0)' or 'requests'
            # Extra parsing (security/tests) omitted for foundational logic
            parts = re.split(r"\s+\(", dist.strip(")"))
            name = parts[0].strip()
            v_range = parts[1] if len(parts) > 1 else "*"

            deps.append(
                NormalizedDependency(
                    name=self.normalize_package_name(name),
                    version_range=v_range,
                    ecosystem="pypi",
                )
            )
        return deps


class GoClient(BaseEcosystemClient):
    def normalize_package_name(self, name: str) -> str:
        # Go modules are case-sensitive but often stored lowercased in some proxies.
        # However, it maintains the case from the module path.
        return name.strip("/")

    def normalize_version(self, version: str) -> str:
        # Go pseudo-versions v0.0.0-2019...
        clean = version.lstrip("v")
        match = re.search(r"(\d+\.\d+\.\d+)", clean)
        return match.group(1) if match else clean

    async def fetch_metadata(self, name: str) -> Dict[str, Any]:
        # Using deps.dev for unified Go representation
        url = f"https://api.deps.dev/v3/systems/go/packages/{name.replace('/', '%2f')}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()  # type: ignore

    def resolve_dependencies(
        self, metadata: Dict[str, Any], version: Optional[str] = None
    ) -> List[NormalizedDependency]:
        # deps.dev specific mapping
        versions = metadata.get("versions", [])
        if not versions:
            return []

        # Select latest or target version
        # target = versions[0]  # simplified find

        deps: List[NormalizedDependency] = []
        # Go dependencies require secondary recursive resolve via deps.dev
        # For simplicity, we define the schema here.
        return deps


class EcosystemFactory:
    _clients = {
        "npm": PyPIClient,  # Placeholder for structural mapping
        "pypi": PyPIClient,
        "go": GoClient,
    }

    @classmethod
    def get_client(cls, ecosystem: str, client: httpx.AsyncClient) -> BaseEcosystemClient:
        client_cls = cls._clients.get(ecosystem.lower())
        if not client_cls:
            raise ValueError(f"Ecosystem {ecosystem} not supported in the Universal Parser.")
        return client_cls(client)
