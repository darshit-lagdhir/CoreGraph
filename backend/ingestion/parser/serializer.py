import time
import hashlib
from typing import Dict, Any, List, Tuple, Set


class TopologicalIntegrityAnomaly(Exception):
    """Raised when edge targets do not exist in the node registry or historical index."""

    pass


class UniversalStreamingSerializer:
    __slots__ = (
        "hardware_tier",
        "batch_limit",
        "_node_registry",
        "_anomaly_log",
        "_current_worker_id",
    )

    def __init__(self, hardware_tier: str, worker_id: int):
        self.hardware_tier = hardware_tier
        self._current_worker_id = worker_id
        self._node_registry: Set[str] = set()
        self._anomaly_log: List[Dict[str, Any]] = []

        if self.hardware_tier == "redline":
            self.batch_limit = 5000
        else:
            self.batch_limit = 250

    def _generate_signature(self, source_hash_input: str) -> int:
        timestamp_ms = int(time.time() * 1000)
        worker_mask = (self._current_worker_id & 0xFF) << 56
        time_mask = (timestamp_ms & 0xFFFFFFFFFF) << 16

        h = hashlib.sha256(source_hash_input.encode("utf-8")).digest()
        hash_mask = int.from_bytes(h[:2], byteorder="big") & 0xFFFF

        return worker_mask | time_mask | hash_mask

    def _validate_entity(self, entity: Dict[str, Any]) -> bool:
        purl = entity.get("purl", "")
        if not purl or not isinstance(purl, str) or not purl.startswith("pkg:"):
            self._anomaly_log.append({"entity": purl, "reason": "Invalid or missing PURL"})
            return False

        timestamp = entity.get("timestamp", 0)
        if not isinstance(timestamp, (int, float)) or timestamp < 0:
            self._anomaly_log.append({"entity": purl, "reason": "Invalid timestamp constraints"})
            return False

        return True

    def audit_batch_topology(
        self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]
    ) -> None:
        batch_nodes = {n.get("purl") for n in nodes if n.get("purl")}
        self._node_registry.update(batch_nodes)

        for edge in edges:
            target = edge.get("target")
            if target not in self._node_registry:
                raise TopologicalIntegrityAnomaly(f"Dangling dependency target detected: {target}")

    def serialize_batch(
        self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]
    ) -> Tuple[List[Tuple], List[Tuple]]:
        serialized_nodes = []
        serialized_edges = []

        for node in nodes:
            if self._validate_entity(node):
                purl = node.get("purl", "")
                sig = self._generate_signature(purl)

                serialized_nodes.append(
                    (
                        purl,
                        node.get("name", ""),
                        node.get("version", ""),
                        node.get("risk_flags", 0),
                        sig,
                    )
                )

        for edge in edges:
            serialized_edges.append(
                (edge.get("source", ""), edge.get("target", ""), edge.get("requirement", ""))
            )

        return serialized_nodes, serialized_edges

    def get_anomalies(self) -> List[Dict[str, Any]]:
        anomalies = self._anomaly_log.copy()
        self._anomaly_log.clear()
        return anomalies
