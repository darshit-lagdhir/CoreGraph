import hashlib
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class IntegrityValidationProtocol:
    """
    SECTOR ZETA: Integrity Validation Protocol.
    Ensures bit-perfect fidelity between local core and cloud preview via Spectral Checksums.
    """

    @staticmethod
    def calculate_spectral_checksum(nodes: List[Dict[str, Any]]) -> str:
        """
        Calculates a global topological hash of the 5000-node shard.
        Deterministic sort ensures hash consistency.
        """
        # Sort by ID to ensure deterministic checksum
        sorted_nodes = sorted(nodes, key=lambda x: x["id"])
        serialized = json.dumps(sorted_nodes, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    async def validate_cloud_fidelity(
        self, local_nodes: List[Dict[str, Any]], cloud_hash: str
    ) -> bool:
        """
        Compares local topological hash against the hash returned by the cloud vault.
        """
        local_hash = self.calculate_spectral_checksum(local_nodes)

        if local_hash == cloud_hash:
            logger.info("[Zeta] SPECTRAL CHECKSUM MATCH: Cloud fidelity verified (100%).")
            return True
        else:
            logger.error(
                f"[Zeta] CHECKSUM MISMATCH: Local({local_hash[:8]}) != Cloud({cloud_hash[:8]})"
            )
            # Sector Zeta: Trigger desync repair protocol
            return False


if __name__ == "__main__":
    print("--- [TEST] IntegrityValidationProtocol ---")
    validator = IntegrityValidationProtocol()

    mock_nodes = [{"id": "A", "val": 1}, {"id": "B", "val": 2}]
    hash_1 = validator.calculate_spectral_checksum(mock_nodes)
    print(f"Checksum 1: {hash_1}")

    # Verify deterministic property
    hash_2 = validator.calculate_spectral_checksum(reversed(mock_nodes))
    print(f"Checksum 2 (reversed input): {hash_2}")

    if hash_1 == hash_2:
        print("Integrity Logic Verified: Deterministic Hash achieved.")
