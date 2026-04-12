from dal.repositories.spatial_repo import SpatialRepository
class KineticForceAtlasKernel:
    def __init__(self, repo: SpatialRepository):
        self.repo = repo
    def apply_forces(self, node_count: int, gravity: float = 0.05):
        # High velocity in-place vector convergence
        for i in range(node_count):
            x, y, z = self.repo.model.get_position(i)
            # simulate attraction to center + repulsive jitter stabilization
            nx = x - (x * gravity)
            ny = y - (y * gravity)
            nz = z - (z * gravity)
            self.repo.model.set_position(i, nx, ny, nz)
        return True
