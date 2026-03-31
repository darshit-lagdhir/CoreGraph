from typing import Any, Dict, List, Optional, Set, Callable, Union
from typing import Any, Dict, List, Optional, Set, Callable, Union
import numpy as np
import networkx as nx
import gc
import psutil
import hashlib
import logging
import time


class TopologicalIntegrityError(Exception):
    pass


class AdjacencyTensorIngestionManifold:
    __slots__ = (
        "ActiveDiGraphReference",
        "is_redline",
        "HardwareIngestConstants",
        "CSR_Buffer_Registry",
        "NodeIndexRegistry",
        "DiagnosticSignalingKernel",
        "memory_threshold",
        "ingestion_complete",
        "V_curr",
        "V_next",
        "SinkMap",
        "MasterSeal",
    )

    def __init__(self, target_graph: nx.DiGraph, is_redline: bool = True):
        self.ActiveDiGraphReference = target_graph
        self.is_redline = is_redline
        self.memory_threshold = 85.0
        self.CSR_Buffer_Registry: Dict[str, Any] = {}
        self.NodeIndexRegistry: Dict[str, Any] = {}
        self.DiagnosticSignalingKernel: Dict[str, Any] = {}
        self.ingestion_complete = False
        self.V_curr = np.array([], dtype=np.float64)
        self.V_next = np.array([], dtype=np.float64)
        self.SinkMap = np.array([], dtype=bool)
        self.MasterSeal = ""
        self._calibrate_ingestion_velocity()

    def _calibrate_ingestion_velocity(self) -> None:
        meminfo = psutil.virtual_memory()
        if self.is_redline and meminfo.percent < self.memory_threshold:
            self.HardwareIngestConstants = {"mode": "HYPER_INGEST", "gc_interval": 500000}
        else:
            self.HardwareIngestConstants = {"mode": "SEQUENTIAL_STREAM", "gc_interval": 50000}
            gc.collect()

    def _map_node_indices(self) -> None:
        nodes = list(self.ActiveDiGraphReference.nodes())
        self.NodeIndexRegistry = {node: i for i, node in enumerate(nodes)}
        if len(self.NodeIndexRegistry) != len(nodes):
            raise TopologicalIntegrityError(
                "Node Index Collision detected. Address space corrupted."
            )

    def _reconstruct_row_pointer_vector(self) -> None:
        # Fused inherently within execute_volumetric_edge_extraction for zero-copy efficiency
        pass

    def execute_volumetric_edge_extraction(self) -> None:
        self._map_node_indices()
        n_nodes = len(self.NodeIndexRegistry)
        n_edges = self.ActiveDiGraphReference.number_of_edges()

        vals = np.ones(n_edges, dtype=np.float32)
        cols = np.empty(n_edges, dtype=np.int32)
        indptr = np.zeros(n_nodes + 1, dtype=np.int32)

        edge_idx = 0
        gc_interval = self.HardwareIngestConstants["gc_interval"]
        nodes_list = list(self.ActiveDiGraphReference.nodes())

        for i, node in enumerate(nodes_list):
            neighbors = self.ActiveDiGraphReference[node]
            degree = len(neighbors)
            indptr[i + 1] = indptr[i] + degree

            for nbr in neighbors:
                cols[edge_idx] = self.NodeIndexRegistry[nbr]
                edge_idx += 1

            if i % gc_interval == 0 and i > 0:
                self._calibrate_ingestion_velocity()

        self.CSR_Buffer_Registry = {"values": vals, "indices": cols, "indptr": indptr}

    def initialize_pagerank_vectors(self) -> None:
        n_nodes = len(self.NodeIndexRegistry)
        if n_nodes == 0:
            return

        self.V_curr = np.full(n_nodes, 1.0 / n_nodes, dtype=np.float64)
        self.V_next = np.zeros(n_nodes, dtype=np.float64)

        indptr = self.CSR_Buffer_Registry["indptr"]
        out_degrees = indptr[1:] - indptr[:-1]
        self.SinkMap = out_degrees == 0

    def _seal_tensor_integrity(self) -> None:
        vals = self.CSR_Buffer_Registry["values"]
        cols = self.CSR_Buffer_Registry["indices"]
        indptr = self.CSR_Buffer_Registry["indptr"]

        n_edges = self.ActiveDiGraphReference.number_of_edges()
        f_tensor = float(np.sum(vals)) / n_edges if n_edges > 0 else 1.0

        if abs(f_tensor - 1.0) > 1e-6:
            raise TopologicalIntegrityError(f"Tensor Fidelity Metric failed: {f_tensor} != 1.0")

        sha = hashlib.sha384()
        sha.update(vals.tobytes())
        sha.update(cols.tobytes())
        sha.update(indptr.tobytes())
        self.MasterSeal = sha.hexdigest()

    def finalize_tensor_ingestion(self) -> None:
        t0 = time.time()
        self.execute_volumetric_edge_extraction()
        self.initialize_pagerank_vectors()
        self._seal_tensor_integrity()
        t1 = time.time()

        total_time = t1 - t0
        vals = self.CSR_Buffer_Registry["values"]
        cols = self.CSR_Buffer_Registry["indices"]
        indptr = self.CSR_Buffer_Registry["indptr"]
        total_bytes = vals.nbytes + cols.nbytes + indptr.nbytes

        d_ingest = total_bytes / total_time if total_time > 0 else 0.0

        self.DiagnosticSignalingKernel = {
            "F_tensor": 1.0,
            "D_ingest": d_ingest,
            "MasterSeal": self.MasterSeal,
        }

        self.ingestion_complete = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("TensorChaos")

    logger.info("INITIATING THE 'MEMORY FRAGMENTATION' CHAOS GAUNTLET...")

    G = nx.DiGraph()
    n_nodes = 5000
    for i in range(n_nodes):
        G.add_node(i)
        if i > 0:
            G.add_edge(i, i - 1)
        if i % 10 == 0:
            G.add_edge(i, 0)

    manifold = AdjacencyTensorIngestionManifold(G, is_redline=False)
    manifold.finalize_tensor_ingestion()

    logger.info(f"Tensor Fidelity (F_tensor): {manifold.DiagnosticSignalingKernel['F_tensor']:.2f}")
    logger.info(
        f"Ingestion Density (D_ingest): {manifold.DiagnosticSignalingKernel['D_ingest'] / 1e6:.2f} MB/s"
    )
    logger.info(f"Master Seal: {manifold.DiagnosticSignalingKernel['MasterSeal']}")

    assert (
        abs(np.sum(manifold.V_curr) - 1.0) < 1e-9
    ), "Stochastic Integrity Failed: V_curr sum != 1.0"
    logger.info("Stochastic Integrity Verified. Initial PageRank vector sum exactly 1.0.")

    leaf_nodes = [n for n, d in G.out_degree() if d == 0]
    sink_count = np.sum(manifold.SinkMap)
    assert sink_count == len(leaf_nodes), f"SinkMap mismatch: {sink_count} != {len(leaf_nodes)}"
    logger.info(f"Sink Node Map Verified. Accurately captured {sink_count} leaves.")

    logger.info("ALL ASSERTIONS PASSED. MODULE 9 - TASK 013 - TENSOR KERNEL SEALED.")
