import re
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator


class DriverCoordinateAnomaly(Exception):
    """Raised when PURL resolution fails due to malformed input."""

    pass


class BaseRegistryDriver:
    """Abstract template defining the Registry Adapter Kernel interface."""

    __slots__ = ("hardware_tier", "_client", "_purl_cache", "_rate_limits", "_telemetry")

    def __init__(self, hardware_tier: str, client: Any):
        self.hardware_tier = hardware_tier
        self._client = client
        self._purl_cache: set = set()
        self._telemetry: Dict[str, Any] = {
            "manifests_processed": 0,
            "versions_extracted": 0,
            "anomalies_flagged": 0,
        }

    async def fetch_metadata(self, purl: str) -> AsyncGenerator[Dict[str, Any], None]:
        raise NotImplementedError

    def resolve_purl_to_url(self, purl: str) -> str:
        raise NotImplementedError


class NPMRegistryDriver(BaseRegistryDriver):
    """
    Registry-Native Extraction Kernel for the NPM Ecosystem.
    Implements Streaming Iteration, Forensic Signal Hooking, and Semantic Resolution.
    """

    __slots__ = ("_base_url", "_seen_maintainers")

    def __init__(self, hardware_tier: str, client: Any):
        super().__init__(hardware_tier, client)
        self._base_url = "https://registry.npmjs.org"
        self._seen_maintainers: Dict[str, str] = {}

        if self.hardware_tier == "redline":
            self._rate_limits = {"concurrent": 50, "delay": 0.01}
        elif self.hardware_tier == "potato":
            self._rate_limits = {"concurrent": 5, "delay": 0.2}
        else:
            self._rate_limits = {"concurrent": 20, "delay": 0.05}

    def resolve_purl_to_url(self, purl: str) -> str:
        if not purl.startswith("pkg:npm/"):
            raise DriverCoordinateAnomaly(f"Invalid NPM PURL prefix: {purl}")

        parts = purl.replace("pkg:npm/", "").split("@")[0].split("/")

        if len(parts) == 1:
            name = parts[0]
        elif len(parts) == 2:
            name = f"{parts[0]}%2F{parts[1]}"
        else:
            raise DriverCoordinateAnomaly(f"Malformed NPM identity in PURL: {purl}")

        return f"{self._base_url}/{name}"

    async def fetch_metadata(self, purl: str) -> AsyncGenerator[Dict[str, Any], None]:
        url = self.resolve_purl_to_url(purl)

        try:
            payload = await self._client.get(url)
            if not payload or "versions" not in payload:
                return

            self._telemetry["manifests_processed"] += 1

            async for record in self._parse_npm_manifest(payload):
                yield record

        except Exception as e:
            self._telemetry["anomalies_flagged"] += 1
            # Propagate or log based on client integration configuration

    async def _parse_npm_manifest(
        self, payload: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        versions_dict = payload.get("versions", {})
        package_name = payload.get("name", "unknown")

        for v_key, v_data in versions_dict.items():
            self._telemetry["versions_extracted"] += 1

            record = {
                "purl": f"pkg:npm/{package_name}@{v_key}",
                "name": package_name,
                "version": v_key,
                "timestamp": int(
                    payload.get("time", {}).get(v_key, "1970-01-01T00:00:00.000Z")[:4] != "1970"
                ),
                "dependencies": v_data.get("dependencies", {}),
                "forensic_signals": self._extract_forensic_signals(package_name, v_data),
            }
            yield record

    def _extract_forensic_signals(
        self, package_name: str, version_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        signals = {
            "dist_integrity": version_data.get("dist", {}).get("integrity"),
            "dist_shasum": version_data.get("dist", {}).get("shasum"),
            "maintainers": version_data.get("maintainers", []),
            "flags": 0,
        }

        # Maintainer Drift Detection
        if signals["maintainers"]:
            primary_maintainer = signals["maintainers"][0].get("email", "")
            if package_name in self._seen_maintainers:
                if self._seen_maintainers[package_name] != primary_maintainer:
                    signals["flags"] |= 1 << 2  # Flag matching maintainer drift
            else:
                self._seen_maintainers[package_name] = primary_maintainer

        if not signals["dist_integrity"]:
            signals["flags"] |= 1 << 4  # Missing integrity hash

        return signals

    def resolve_constraint(
        self, package_name: str, constraint: str, available_versions: List[str]
    ) -> Optional[str]:
        if not constraint or constraint == "*":
            return available_versions[-1] if available_versions else None

        # Simplified runtime resolution for ^ and ~ prefixes mapped against static caches
        clean_constraint = re.sub(r"[\^~>=<xu]", "", constraint).strip()

        for v in reversed(available_versions):
            if v.startswith(clean_constraint):
                return v

        return None
