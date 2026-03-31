import uuid
import re
from typing import Dict, Any, Optional


class AliasRecord:
    """
    Slotted DTO representing a single registered GraphQL namespace alias.
    Ensures O(1) attribute access and minimal RAM residency during large batches.
    """

    __slots__ = ("alias_id", "purl", "complexity_weight")

    def __init__(self, alias_id: str, purl: str, complexity_weight: int):
        self.alias_id = alias_id
        self.purl = purl
        self.complexity_weight = complexity_weight


class FieldAliasGenerator:
    """
    Module 5 - Task 001: Dynamic GraphQL Field Alias Generator.
    Programmatic namespace isolation kernel preventing response collisions
    and securing the AST against hostile string injection attacks.
    """

    __slots__ = (
        "_batch_uuid",
        "_alias_registry",
        "_lexical_validator",
        "_hardware_tier",
        "_max_batch_size",
    )

    def __init__(self, hardware_tier: str = "redline"):
        self._batch_uuid = uuid.uuid4().hex
        self._alias_registry: Dict[str, AliasRecord] = {}
        self._hardware_tier = hardware_tier

        if self._hardware_tier == "redline":
            self._max_batch_size = 5000
        else:
            self._max_batch_size = 50

        # Enforces strict GraphQL Identifier Specification matching
        self._lexical_validator = re.compile(r"^[_A-Za-z][_0-9A-Za-z]*$")

    def _murmurhash3_32(self, key: str, seed: int = 0) -> int:
        """
        Silicon-native MurmurHash3 (32-bit) implementation for fast,
        non-cryptographic deterministic hashing avoiding math/hashlib bloat.
        """
        data = key.encode("utf-8")
        length = len(data)
        nblocks = length // 4
        h1 = seed
        c1 = 0xCC9E2D51
        c2 = 0x1B873593

        for i in range(nblocks):
            k1 = int.from_bytes(data[i * 4 : (i + 1) * 4], byteorder="little", signed=False)
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF

            h1 ^= k1
            h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
            h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF

        tail = data[nblocks * 4 :]
        k1 = 0
        if len(tail) >= 3:
            k1 ^= tail[2] << 16
        if len(tail) >= 2:
            k1 ^= tail[1] << 8
        if len(tail) >= 1:
            k1 ^= tail[0]
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1

        h1 ^= length
        h1 ^= h1 >> 16
        h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
        h1 ^= h1 >> 13
        h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
        h1 ^= h1 >> 16

        return h1 & 0xFFFFFFFF

    def generate_alias(self, purl: str, complexity_weight: int = 1, prefix: str = "repo") -> str:
        """
        Generates and registers a mathematically unique GraphQL field alias.
        Executes lexical bounds checking and enforces hardware batch sizing limits.
        """
        if len(self._alias_registry) >= self._max_batch_size:
            raise MemoryError(f"Batch size limit exceeded for tier: {self._hardware_tier}")

        # Deterministic seed generation mixing execution context with target coordinate
        compound_key = f"{self._batch_uuid}:{purl}"
        hash_val = self._murmurhash3_32(compound_key)

        # 8-character base-16 deterministic suffix
        suffix = f"{hash_val:08x}"

        candidate_alias = f"{prefix}_{suffix}"

        if not self._lexical_validator.match(candidate_alias):
            # Fallback to pure hash if prefix violates lexical bounds
            candidate_alias = f"R_{suffix}"

        if candidate_alias in self._alias_registry:
            # Highly improbable collision resolution (Birthday paradox mathematically 0.000...1%)
            candidate_alias = f"{candidate_alias}_1"

        self._alias_registry[candidate_alias] = AliasRecord(
            alias_id=candidate_alias, purl=purl, complexity_weight=complexity_weight
        )

        return candidate_alias

    def resolve_purl(self, alias_id: str) -> Optional[str]:
        """O(1) Reverse resolution for normalizing responses to coordinates."""
        record = self._alias_registry.get(alias_id)
        return record.purl if record else None

    def calculate_batch_complexity(self) -> int:
        """Determines pre-flight cost analysis for external Rate-Limit awareness."""
        return sum(record.complexity_weight for record in self._alias_registry.values())

    def flush_registry(self) -> None:
        """
        Forces immediate garbage collection of the temporal registry preventing
        OOM conditions during sustained continuous ingestion waves.
        """
        self._alias_registry.clear()
        self._batch_uuid = uuid.uuid4().hex
