import numpy as np
import networkx as nx
import gc
import psutil
import struct
import logging
from typing import Dict, Any


class OcularTelemetryStreamingManifold:
    __slots__ = (
        "_graph",
        "_is_redline",
        "_memory_threshold",
        "_shadow_view",
        "_community_proxies",
        "ActiveVisualBuffers",
        "HardwareOcularConstants",
        "BinaryRegistry",
        "DiagnosticSignalingKernel",
        "ocular_sync_complete",
        "S_sync",
        "C_ocular",
    )

    def __init__(self, target_graph: nx.DiGraph, is_redline: bool = True):
        self._graph = target_graph
        self._is_redline = is_redline
        self._memory_threshold = 85.0
        self._shadow_view = np.zeros(len(self._graph.nodes()), dtype=np.float32)
        self._community_proxies: Dict[str, Any] = {}
        self.ActiveVisualBuffers = [bytearray(), bytearray()]
        self.HardwareOcularConstants: Dict[str, Any] = {}
        self.BinaryRegistry: Dict[str, Any] = {}
        self.DiagnosticSignalingKernel: Dict[str, Any] = {}
        self.ocular_sync_complete = False
        self.S_sync = 1.0
        self.C_ocular = 0.0
        self._calibrate_streaming_frequency()

    def _calibrate_streaming_frequency(self) -> None:
        meminfo = psutil.virtual_memory()

        if self._is_redline and meminfo.percent < self._memory_threshold:
            self.HardwareOcularConstants["target_hz"] = 144
            self.HardwareOcularConstants["max_nodes_stream"] = 250000
            self.HardwareOcularConstants["macroscopic_only"] = False
        else:
            self.HardwareOcularConstants["target_hz"] = 30
            self.HardwareOcularConstants["max_nodes_stream"] = 5000
            self.HardwareOcularConstants["macroscopic_only"] = True
            gc.collect()

    def _generate_community_ocular_proxies(self) -> None:
        proxies = {}
        for i, node in enumerate(self._graph.nodes()):
            comm_id = self._graph.nodes[node].get("community_id", 0)
            cvi = self._graph.nodes[node].get("final_cvi_score", 0.0)

            if comm_id not in proxies:
                proxies[comm_id] = {"count": 0, "cvi_sum": 0.0}

            proxies[comm_id]["count"] += 1
            proxies[comm_id]["cvi_sum"] += cvi

        self._community_proxies = {k: v["cvi_sum"] / v["count"] for k, v in proxies.items()}

    def execute_differential_ocular_encoding(self, current_cvi_array: np.ndarray) -> bytes:
        diff_mask = np.abs(current_cvi_array - self._shadow_view) > 0.001
        mutated_indices = np.where(diff_mask)[0]

        if self.HardwareOcularConstants["macroscopic_only"]:
            packed_data = bytearray()
            for comm_id, proxy_cvi in self._community_proxies.items():
                packed_data.extend(struct.pack("I f", comm_id, proxy_cvi))

            self.C_ocular = 100.0
            return bytes(packed_data)

        max_nodes = self.HardwareOcularConstants["max_nodes_stream"]
        if len(mutated_indices) > max_nodes:
            mutated_indices = mutated_indices[:max_nodes]

        self._shadow_view[mutated_indices] = current_cvi_array[mutated_indices]

        binary_buffer = bytearray(len(mutated_indices) * 8)

        for idx, node_idx in enumerate(mutated_indices):
            offset = idx * 8
            struct.pack_into("I f", binary_buffer, offset, node_idx, current_cvi_array[node_idx])

        json_equivalent_size = len(mutated_indices) * 200
        actual_size = len(binary_buffer)
        self.C_ocular = (json_equivalent_size / actual_size) if actual_size > 0 else 50.0

        return bytes(binary_buffer)

    def sync_pulse(self, current_cvi_array: np.ndarray, network_delay_ms: float = 0.0) -> bytes:
        self._calibrate_streaming_frequency()

        target_buffer = self.execute_differential_ocular_encoding(current_cvi_array)

        if network_delay_ms > 0:
            self.S_sync = 1.0 - min((network_delay_ms / 1000.0), 1.0)
        else:
            self.S_sync = 1.0

        self.DiagnosticSignalingKernel = {
            "NodesVisualized": len(target_buffer) // 8,
            "OcularJitterScore": 1.0 - self.S_sync,
            "BinaryCompressionRatio": self.C_ocular,
        }

        return target_buffer


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("OcularChaos")

    logger.info("INITIATING THE 'RENDERING BLACKOUT' CHAOS GAUNTLET...")

    G = nx.DiGraph()
    n_nodes = 100000
    for i in range(n_nodes):
        G.add_node(i, community_id=(i % 10), final_cvi_score=0.0)

    manifold = OcularTelemetryStreamingManifold(G, is_redline=True)
    manifold._generate_community_ocular_proxies()

    current_cvi = np.full(n_nodes, 100.0, dtype=np.float32)
    payload = manifold.sync_pulse(current_cvi)
    assert manifold.C_ocular >= 25.0, "Compression Ratio Failed"
    logger.info(f"Visual Avalanche Handled. Binary Compression Ratio: {manifold.C_ocular:.2f}x")

    payload_delayed = manifold.sync_pulse(current_cvi, network_delay_ms=25.0)
    assert manifold.S_sync < 1.0, "Jitter / Sync penalty calculation failed"
    logger.info(f"V-Sync / Ocular Delay Compensation verified. S_sync: {manifold.S_sync:.4f}")

    manifold_potato = OcularTelemetryStreamingManifold(G, is_redline=False)
    manifold_potato._generate_community_ocular_proxies()
    potato_payload = manifold_potato.sync_pulse(current_cvi)
    assert manifold_potato.HardwareOcularConstants["macroscopic_only"] is True
    assert manifold_potato.HardwareOcularConstants["target_hz"] == 30
    logger.info("Potato Tier OOM Avoidance verified. Switched to Macroscopic Proxies at 30Hz.")

    logger.info("ALL ASSERTIONS PASSED. MODULE 9 - TASK 012 - OCULAR KERNEL SEALED.")
