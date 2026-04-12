import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from .quantum_logic.entanglement_entropy_manifold import EntanglementEntropyManifold
from .quantum_logic.bell_inequality_kernel import BellInequalityKernel
from .entanglement_sync import EntanglementIntegritySync
from backend.dal.repositories.entangled_state_repo import EntangledStateRepository


class NonLocalCorrelationEngine:
    def __init__(self, node_limit: int):
        self.node_limit = node_limit
        self.stride = 24
        # Main Tensor: [8: node_id, 8: entanglement_state, 8: chsh_potential]
        self.correlation_tensor = bytearray(self.node_limit * self.stride)
        self.manifold = EntanglementEntropyManifold(self.node_limit)
        self.kernel = BellInequalityKernel()
        self.sync = EntanglementIntegritySync()
        self.repo = EntangledStateRepository(self.node_limit)

    def establish_correlation(self, active_nodes: int):
        cache_limit = 16384 // self.stride
        view = memoryview(self.correlation_tensor)
        for i in range(0, active_nodes, cache_limit):
            chunk_size = min(cache_limit, active_nodes - i)
            offset = i * self.stride
            chunk_view = view[offset : offset + (chunk_size * self.stride)]
            self.sync.lock_correlation(i)
            self.kernel.apply_chsh_violation(chunk_view, chunk_size)
            self.manifold.map_entangled_pair(i, (i + 1) % self.node_limit, 1.05)
            self.sync.release_correlation(i)

    def flush_and_verify(self) -> float:
        drift_safe = self.repo.assert_zero_drift()
        return 1.0 if drift_safe else 0.0
