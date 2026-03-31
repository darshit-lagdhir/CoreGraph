from typing import Any, Dict, List, Optional, Set, Callable, Union
from typing import Any, Dict, List, Optional, Set, Callable, Union
import numpy as np
import networkx as nx
import gc
import psutil
import hashlib
import logging
import time
from scipy.sparse import csr_matrix


class TopologicalInconsistencyError(Exception):
    pass


class GraphTopologyReorientationManifold:
    """
    Executes the In-Memory Topological Reorientation and Reverse Adjacency Synthesis.
    Performs CSR Matrix Transposition for downstream impact reachability prep.
    """

    __slots__ = (
        "ForwardAdjacencyReference",
        "ReverseAdjacencyBuffer",
        "HardwareReorientConstants",
        "DiagnosticSignalingKernel",
        "NodeIndexRegistry",
        "ImpactSources",
        "DownstreamSuperHubs",
        "is_redline",
        "memory_threshold",
        "reorientation_complete",
        "F_syn",
        "D_syn",
        "ReverseMasterSeal",
    )

    def __init__(
        self, forward_csr_tensor: csr_matrix, node_registry: dict, is_redline: bool = True
    ):
        self.ForwardAdjacencyReference = forward_csr_tensor
        self.NodeIndexRegistry = node_registry
        self.ReverseAdjacencyBuffer = None
        self.ImpactSources = np.array([], dtype=np.int32)
        self.DownstreamSuperHubs = np.array([], dtype=np.int32)
        self.is_redline = is_redline
        self.memory_threshold = 85.0
        self.reorientation_complete = False
        self.DiagnosticSignalingKernel: Dict[str, Any] = {}
        self.F_syn = 0.0
        self.D_syn = 0.0
        self.ReverseMasterSeal = ""
        self._calibrate_reorientation_velocity()

    def _calibrate_reorientation_velocity(self) -> None:
        meminfo = psutil.virtual_memory()
        if self.is_redline and meminfo.percent < self.memory_threshold:
            self.HardwareReorientConstants = {"mode": "HYPER_TRANSPOSE", "gc_force": False}
        else:
            self.HardwareReorientConstants = {"mode": "SECTOR_BASED_REVERSAL", "gc_force": True}
            gc.collect()

    def execute_matrix_inversion(self) -> None:
        # Zero-Copy topological inversion via sparse transposition
        self.ReverseAdjacencyBuffer = self.ForwardAdjacencyReference.transpose().tocsr()

    def _map_impact_provenance(self) -> None:
        # Forward sink (out degree 0) -> Reverse source
        fwd_indptr = self.ForwardAdjacencyReference.indptr
        fwd_out_degrees = fwd_indptr[1:] - fwd_indptr[:-1]
        self.ImpactSources = np.where(fwd_out_degrees == 0)[0].astype(np.int32)

        # Super-Hubs = massive out-degree in REVERSE graph (things many others depend on)
        rev_indptr = self.ReverseAdjacencyBuffer.indptr
        rev_out_degrees = rev_indptr[1:] - rev_indptr[:-1]

        # Identify those in the top 99.9%
        hub_threshold = np.percentile(rev_out_degrees, 99.9) if len(rev_out_degrees) > 0 else 0
        if hub_threshold > 0:
            self.DownstreamSuperHubs = np.where(rev_out_degrees >= hub_threshold)[0].astype(
                np.int32
            )
        else:
            self.DownstreamSuperHubs = np.array([], dtype=np.int32)

    def _run_integrity_reconciliation(self) -> None:
        fwd_edges = self.ForwardAdjacencyReference.nnz
        rev_edges = self.ReverseAdjacencyBuffer.nnz

        self.F_syn = float(rev_edges) / fwd_edges if fwd_edges > 0 else 1.0
        if abs(self.F_syn - 1.0) > 1e-6:
            raise TopologicalInconsistencyError(
                f"Edge Conservation Check Failed: {rev_edges} != {fwd_edges}"
            )

        sha = hashlib.sha384()
        sha.update(self.ReverseAdjacencyBuffer.data.tobytes())
        sha.update(self.ReverseAdjacencyBuffer.indices.tobytes())
        sha.update(self.ReverseAdjacencyBuffer.indptr.tobytes())
        self.ReverseMasterSeal = sha.hexdigest()

    def finalize_topology_reorientation(self) -> None:
        t0 = time.time()

        self.execute_matrix_inversion()
        self._map_impact_provenance()
        self._run_integrity_reconciliation()

        if self.HardwareReorientConstants["gc_force"]:
            gc.collect()

        t1 = time.time()
        duration = t1 - t0

        # Calculate D_syn
        mat = self.ReverseAdjacencyBuffer
        total_bytes = mat.data.nbytes + mat.indices.nbytes + mat.indptr.nbytes
        self.D_syn = total_bytes / duration if duration > 0 else 0.0

        self.DiagnosticSignalingKernel = {
            "EdgesReversed": self.ReverseAdjacencyBuffer.nnz,
            "ReachabilityDensity": self.D_syn,
            "SynthesisFidelity": self.F_syn,
            "HubCount": len(self.DownstreamSuperHubs),
            "SourceCount": len(self.ImpactSources),
            "TopologySeal": self.ReverseMasterSeal,
        }

        self.reorientation_complete = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("TranspositionChaos")

    logger.info("INITIATING THE 'DIRECTIONAL CORRUPTION' CHAOS GAUNTLET...")

    # 1. Relational Symmetry & Hub Discovery Audit Setup
    n_nodes = 12000
    rows = []
    cols = []
    data = []

    hub_node = 0
    # Create star topology onto Hub. In Forward: leaf depends on Hub. Edge: (Leaf) -> (Hub)
    for i in range(1, 10001):
        rows.append(i)
        cols.append(hub_node)
        data.append(1.0)

    for i in range(10001, 12000):
        rows.append(i)  # Leaf nodes pointing to previous
        cols.append(i - 1)
        data.append(1.0)

    forward_tensor = csr_matrix((data, (rows, cols)), shape=(n_nodes, n_nodes))
    node_registry = {i: i for i in range(n_nodes)}

    manifold = GraphTopologyReorientationManifold(forward_tensor, node_registry, is_redline=True)
    manifold.finalize_topology_reorientation()

    # 2. Assert Edge Conservation
    assert manifold.F_syn == 1.0, f"Conservation Failed: {manifold.F_syn}"
    logger.info(f"Relational Symmetry Verified. Edge synthesis fidelity: {manifold.F_syn}")

    # 3. Assert Hub Discovery
    assert hub_node in manifold.DownstreamSuperHubs, "Super-Hub logic failed to flag index 0."
    logger.info(f"Downstream Super-Hub Discovery Verified. Core library flagged successfully.")

    # 4. Terminal Source Verification
    # Hub node has out-degree=0 in Forward Graph. It becomes impact source.
    assert hub_node in manifold.ImpactSources, "Failed to identify forward sinks as impact sources."
    logger.info(
        f"Terminal Source Verification Passed. Mapped {len(manifold.ImpactSources)} impact nodes."
    )

    # 5. Potato Tier Audit
    manifold_potato = GraphTopologyReorientationManifold(
        forward_tensor, node_registry, is_redline=False
    )
    manifold_potato.finalize_topology_reorientation()
    assert manifold_potato.HardwareReorientConstants["gc_force"] is True
    logger.info("Potato Tier Transpose logic verified. Aggressive GC scheduling activated.")

    logger.info("ALL ASSERTIONS PASSED. MODULE 9 - TASK 015 - TOPOLOGY KERNEL SEALED.")
