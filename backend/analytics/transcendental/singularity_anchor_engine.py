import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from .metaphysics.ontological_reversion_manifold import RelationalOntologicalManifold  # noqa: E402
from .metaphysics.axiomatic_persistence_kernel import AxiomaticPersistenceKernel  # noqa: E402
from .transcendental_sync import TranscendentalIntegritySync  # noqa: E402
from backend.dal.repositories.existence_repo import ExistenceRepository  # noqa: E402


class SingularityAnchorEngine:
    def __init__(self, node_limit: int):
        self.node_limit = node_limit
        self.stride = 24
        # Main Tensor: [8: node_id, 8: existential_state, 8: identity_potential]
        self.reversion_tensor = bytearray(self.node_limit * self.stride)
        self.manifold = RelationalOntologicalManifold(self.node_limit)
        self.kernel = AxiomaticPersistenceKernel()
        self.sync = TranscendentalIntegritySync()
        self.repo = ExistenceRepository(self.node_limit)

    def anchor_existence(self, active_nodes: int):
        cache_limit = 16384 // self.stride
        view = memoryview(self.reversion_tensor)
        for i in range(0, active_nodes, cache_limit):
            chunk_size = min(cache_limit, active_nodes - i)
            offset = i * self.stride
            chunk_view = view[offset : offset + (chunk_size * self.stride)]
            self.sync.lock_identity(i)
            self.kernel.apply_ontological_reversion(chunk_view, chunk_size)
            self.manifold.map_axiomatic_state(i, (i + 1) % self.node_limit, 1.99)
            self.sync.release_identity(i)

    def flush_and_verify(self) -> float:
        drift_safe = self.repo.assert_zero_drift()
        return 1.0 if drift_safe else 0.0
