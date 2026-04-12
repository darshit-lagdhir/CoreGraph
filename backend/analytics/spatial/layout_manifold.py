from dal.repositories.spatial_repo import SpatialRepository
from .force_atlas_kernel import KineticForceAtlasKernel

class GeometricLayoutManifold:
    def __init__(self, repo: SpatialRepository):
        self.repo = repo
        self.kernel = KineticForceAtlasKernel(repo)
    def compute_layout(self, node_count: int, iterations: int = 1):
        for _ in range(iterations):
            self.kernel.apply_forces(node_count)
        return True
