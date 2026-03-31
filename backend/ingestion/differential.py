import hashlib
import math
from enum import IntEnum
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict

try:
    import ujson  # type: ignore[import-untyped]
except ImportError:
    import json as ujson


class DeltaSignal(IntEnum):
    NO_CHANGE = 0
    METADATA_DELTA = 1
    VERSION_DELTA = 2
    TOPOLOGICAL_DELTA = 3
    PATHOGEN_DELTA = 4


class DifferentialStateEngine:
    """
    Module 4 - Task 018: Differential State Engine.
    Hardware-aware incremental synchronization kernel for detecting chronological drift.
    """

    __slots__ = (
        "_registry",
        "_hardware_tier",
        "_state_cache",
        "_cache_limit",
        "_entropy_weights",
        "_salt",
    )

    def __init__(self, registry: Any, hardware_tier: str = "redline"):
        self._registry = registry
        self._hardware_tier = hardware_tier
        self._salt = b"coregraph_differential_v1"
        self._entropy_weights = {"description": 0.6, "keywords": 0.2, "license": 0.2}

        if self._hardware_tier == "redline":
            self._cache_limit = 50000
            self._state_cache: Dict[int, Tuple[Tuple[int, int, int], float]] = {}
        else:
            self._cache_limit = 5000
            self._state_cache = OrderedDict()

    def _hash_64(self, payload: str) -> int:
        """Generates a fast 64-bit integer hash utilizing BLAKE2b (simulating XXHash64 collision resistance)."""
        h = hashlib.blake2b(digest_size=8, salt=self._salt)
        h.update(payload.encode("utf-8"))
        return int.from_bytes(h.digest(), byteorder="little")

    def calculate_state_fingerprint(self, manifest: Dict[str, Any]) -> Tuple[int, int, int]:
        """
        Calculates the Hash Cascade: (Metadata Hash, Version Hash, Topology Hash).
        Zero-copy optimization by serializing selective dictionary views.
        """
        serializer = ujson.dumps

        # 1. Metadata Fingerprint
        meta_payload = {
            "name": manifest.get("name", ""),
            "description": parse_to_str(manifest.get("description", "")),
            "maintainers": manifest.get("maintainers", []),
            "license": parse_to_str(manifest.get("license", "")),
            "keywords": manifest.get("keywords", []),
        }
        meta_hash = self._hash_64(serializer(meta_payload))

        # 2. Version History Fingerprint
        versions = manifest.get("versions", {})
        version_keys = sorted(versions.keys()) if isinstance(versions, dict) else []
        version_hash = self._hash_64(serializer(version_keys))

        # 3. Topology Fingerprint (Direct Dependencies of latest)
        dist_tags = manifest.get("dist-tags", {})
        latest_version = dist_tags.get("latest") if isinstance(dist_tags, dict) else None

        topology_hash = 0
        if latest_version and isinstance(versions, dict) and latest_version in versions:
            latest_data = versions[latest_version]
            if isinstance(latest_data, dict):
                deps = latest_data.get("dependencies", {})
                topology_hash = self._hash_64(serializer(deps))

        return (meta_hash, version_hash, topology_hash)

    def evaluate_delta(
        self, purl_hash: int, current_fingerprint: Tuple[int, int, int]
    ) -> DeltaSignal:
        """
        O(1) Delta Evaluation against the state ledger cache.
        Returns the granular invalidation signal.
        """
        historical_state = self._get_cached_state(purl_hash)
        if not historical_state:
            self._update_cache(purl_hash, current_fingerprint, 0.0)
            return DeltaSignal.VERSION_DELTA  # Treat as new insertion

        hist_meta, hist_vers, hist_topo = historical_state[0]
        curr_meta, curr_vers, curr_topo = current_fingerprint

        # Determine highest severity delta
        if curr_topo != hist_topo:
            self._update_cache(purl_hash, current_fingerprint, historical_state[1])
            return DeltaSignal.TOPOLOGICAL_DELTA
        elif curr_vers != hist_vers:
            self._update_cache(purl_hash, current_fingerprint, historical_state[1])
            return DeltaSignal.VERSION_DELTA
        elif curr_meta != hist_meta:
            self._update_cache(purl_hash, current_fingerprint, historical_state[1])
            return DeltaSignal.METADATA_DELTA

        # Fluid Equilibrium maintained.
        return DeltaSignal.NO_CHANGE

    def _get_cached_state(self, purl_hash: int) -> Optional[Tuple[Tuple[int, int, int], float]]:
        if purl_hash in self._state_cache:
            if self._hardware_tier == "potato":
                # Move to end as LRU in Python 3.2+
                self._state_cache.move_to_end(purl_hash)  # type: ignore
            return self._state_cache[purl_hash]
        return None

    def _update_cache(
        self, purl_hash: int, fingerprint: Tuple[int, int, int], entropy: float
    ) -> None:
        self._state_cache[purl_hash] = (fingerprint, entropy)
        if self._hardware_tier == "potato" and len(self._state_cache) > self._cache_limit:
            self._state_cache.popitem(last=False)  # type: ignore

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        if not text:
            return 0.0
        probabilities = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in probabilities)

    def decorate_with_risk_delta(self, manifest: Dict[str, Any], purl_hash: int) -> Dict[str, Any]:
        """
        Calculates Metadata Delta Entropy (E_delta) to detect Shadow Updates.
        Applies behavioral drift signals to the record.
        """
        desc = parse_to_str(manifest.get("description", ""))
        kw_raw = manifest.get("keywords", [])
        kw = "".join(kw_raw) if isinstance(kw_raw, list) else parse_to_str(kw_raw)
        lic = parse_to_str(manifest.get("license", ""))

        s_desc = self._calculate_shannon_entropy(desc)
        s_kw = self._calculate_shannon_entropy(kw)
        s_lic = self._calculate_shannon_entropy(lic)

        total_entropy = s_desc + s_kw + s_lic
        if total_entropy == 0:
            return manifest

        # Retrieve historical entropy from state cache
        historical_state = self._get_cached_state(purl_hash)
        hist_entropy = historical_state[1] if historical_state else 0.0

        # E_delta calculation based on Engineering Spec 018
        e_delta = 0.0
        if hist_entropy > 0:
            desc_diff = abs(s_desc - (hist_entropy * 0.6)) / total_entropy
            kw_diff = abs(s_kw - (hist_entropy * 0.2)) / total_entropy
            lic_diff = abs(s_lic - (hist_entropy * 0.2)) / total_entropy
            e_delta_desc = self._entropy_weights["description"] * desc_diff
            e_delta_kw = self._entropy_weights["keywords"] * kw_diff
            e_delta_lic = self._entropy_weights["license"] * lic_diff
            e_delta = e_delta_desc + e_delta_kw + e_delta_lic

        manifest["_coregraph_telemetry"] = {
            "current_entropy": total_entropy,
            "delta_entropy": e_delta,
            "pathogen_flag": e_delta > 0.5,  # Arbitrary pathogen threshold for high deviation
        }

        # Update cache with new baseline entropy
        if historical_state:
            fingerprint = historical_state[0]
            self._update_cache(purl_hash, fingerprint, total_entropy)

        return manifest


def parse_to_str(val: Any) -> str:
    if isinstance(val, str):
        return val
    elif isinstance(val, dict) and "type" in val:
        return str(val.get("type", ""))
    return str(val)
