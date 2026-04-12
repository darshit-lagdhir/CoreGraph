import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from .finality.stationarity_manifold import RelationalStationarityManifold
from .finality.stationarity_anchor_kernel import StationarityAnchorKernel
from .universal_sync import UniversalIntegritySync
from backend.dal.repositories.universal_hardened_repo import UniversalHardenedRepository


class UniversalHardeningEngine:
    def __init__(self, node_limit: int):
        self.node_limit = node_limit
        self.stride = 24
        # Main Tensor: [8: node_id, 8: architectural_state, 8: sovereignty_potential]
        self.hardening_tensor = bytearray(self.node_limit * self.stride)
        self.manifold = RelationalStationarityManifold(self.node_limit)
        self.kernel = StationarityAnchorKernel()
        self.sync = UniversalIntegritySync()
        self.repo = UniversalHardenedRepository(self.node_limit)

    def execute_absolute_hardening(self, active_nodes: int):
        cache_limit = 16384 // self.stride
        view = memoryview(self.hardening_tensor)
        for i in range(0, active_nodes, cache_limit):
            chunk_size = min(cache_limit, active_nodes - i)
            offset = i * self.stride
            chunk_view = view[offset : offset + (chunk_size * self.stride)]
            self.sync.lock_hardening(i)
            self.kernel.apply_absolute_hardening(chunk_view, chunk_size)
            self.manifold.map_sovereign_state(i, (i + 1) % self.node_limit, 2.0)
            self.sync.release_hardening(i)

    def flush_and_verify(self) -> float:
        drift_safe = self.repo.assert_zero_drift()
        return 1.0 if drift_safe else 0.0
