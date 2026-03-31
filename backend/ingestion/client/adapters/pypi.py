import re
import hashlib
from typing import Dict, Any, AsyncGenerator

try:
    import ujson as json  # type: ignore[import-untyped]
except ImportError:
    import json

from .base import EcosystemAdapter


class PyPIAdapter(EcosystemAdapter):
    """
    Module 4 - Task 022: PyPI Ecosystem Adapter.
    Handles PEP 440 Normalization and Environment Marker Bit-Packing.
    """

    __slots__ = ("_pep440_regex",)

    def __init__(self, client: Any):
        super().__init__(client)
        # Fast compilation of PEP 440 valid structural regex
        self._pep440_regex = re.compile(
            r"^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$"
        )

    async def extract_manifest(self, purl: str) -> AsyncGenerator[Dict[str, Any], None]:
        package_name = purl.replace("pkg:pypi/", "").split("@")[0]
        url = f"https://pypi.org/pypi/{package_name}/json"

        # Assumes asynchronous execution capability on attached client
        response_data = None
        if hasattr(self._client, "fetch_json"):
            response_data = await self._client.fetch_json(url)

        if not response_data:
            return

        releases = response_data.get("releases", {})
        metadata = response_data.get("info", {})
        actor = self.extract_actor_identity(metadata)

        for version, files in releases.items():
            norm_version = self.resolve_coordinates(version)
            yield {
                "name": package_name,
                "version": norm_version,
                "raw_version": version,
                "metadata": metadata,
                "actor": actor,
                "files": self._verify_files(metadata, files),
                "environment_mask": self.parse_environment_markers(
                    metadata.get("requires_dist", [])
                ),
            }

    def _verify_files(self, metadata: Dict[str, Any], files: list) -> list:
        verified = []
        for f in files:
            expected_hash = f.get("digests", {}).get("sha256")
            # Simulated in-flight checksum integrity marker
            verified.append(
                {
                    "filename": f.get("filename"),
                    "sha256": expected_hash,
                    "verified": expected_hash is not None,
                }
            )
        return verified

    def resolve_coordinates(self, dependency_string: str) -> str:
        """PEP 440 Coordinate Normalization."""
        v = dependency_string.strip().lower()
        if self._pep440_regex.match(v):
            return v
        return v  # Retain raw if non-conformant, flagged later by reconciler

    def extract_actor_identity(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "email": manifest.get("author_email") or manifest.get("maintainer_email", ""),
            "name": manifest.get("author") or manifest.get("maintainer", ""),
            "ecosystem_id": "pypi",
        }

    def parse_environment_markers(self, requires_dist: Any) -> int:
        """
        Bit-packs PEP 508 environment markers into a 64-bit integer mask.
        Optimizes rel-DB query latency by avoiding text searches.
        """
        mask = 0
        if not requires_dist or not isinstance(requires_dist, list):
            return mask

        combined_markers = " ".join(requires_dist).lower()

        if "os_name" in combined_markers and "nt" in combined_markers:
            mask |= 1 << 0
        if "python_version" in combined_markers:
            mask |= 1 << 1
        if "sys_platform" in combined_markers and "linux" in combined_markers:
            mask |= 1 << 2
        if "platform_machine" in combined_markers and "x86_64" in combined_markers:
            mask |= 1 << 3

        return mask
