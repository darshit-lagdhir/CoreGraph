import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from .bulk_geometry.projection_manifold import RelationalProjectionManifold
from .bulk_geometry.ryu_takayanagi_kernel import RyuTakayanagiKernel
from .holographic_sync import HolographicIntegritySync
from backend.dal.repositories.holographic_correspondence_repo import (
    HolographicCorrespondenceRepository,
)


class BulkBoundaryEngine:
    def __init__(self, node_limit: int):
        self.node_limit = node_limit
        self.stride = 24
        # Main Tensor: [8: node_id, 8: boundary_state, 8: bulk_potential]
        self.projection_tensor = bytearray(self.node_limit * self.stride)
        self.manifold = RelationalProjectionManifold(self.node_limit)
        self.kernel = RyuTakayanagiKernel()
        self.sync = HolographicIntegritySync()
        self.repo = HolographicCorrespondenceRepository(self.node_limit)

    def project_hologram(self, active_nodes: int):
        cache_limit = 16384 // self.stride
        view = memoryview(self.projection_tensor)
        for i in range(0, active_nodes, cache_limit):
            chunk_size = min(cache_limit, active_nodes - i)
            offset = i * self.stride
            chunk_view = view[offset : offset + (chunk_size * self.stride)]
            self.sync.lock_projection(i)
            self.kernel.apply_ads_cft_reduction(chunk_view, chunk_size)
            self.manifold.map_dual_hologram(i, (i + 1) % self.node_limit, 1.08)
            self.sync.release_projection(i)

    def flush_and_verify(self) -> float:
        drift_safe = self.repo.assert_zero_drift()
        return 1.0 if drift_safe else 0.0
