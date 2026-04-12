from .quantum_field.virtual_particle_manifold import RelationalVirtualManifold
from .quantum_field.vacuum_polarization_kernel import VacuumPolarizationKernel
from .vacuum_sync import VacuumIntegritySync
from .void_energy_repo import VoidEnergyRepository


class PolarizationFluctuationEngine:
    def __init__(self, node_limit: int):
        self.node_limit = node_limit
        self.stride = 24
        # Main Tensor: [8: node_id, 8: polarization_state, 8: vacuum_potential]
        self.vacuum_tensor = bytearray(self.node_limit * self.stride)
        self.manifold = RelationalVirtualManifold(self.node_limit)
        self.kernel = VacuumPolarizationKernel()
        self.sync = VacuumIntegritySync()
        self.repo = VoidEnergyRepository(self.node_limit)

    def excite_vacuum(self, active_nodes: int):
        cache_limit = 16384 // self.stride
        view = memoryview(self.vacuum_tensor)

        for i in range(0, active_nodes, cache_limit):
            chunk_size = min(cache_limit, active_nodes - i)
            offset = i * self.stride
            chunk_view = view[offset : offset + (chunk_size * self.stride)]

            self.sync.lock_fluctuation(i)
            self.kernel.apply_uehling_potential(chunk_view, chunk_size)
            self.manifold.map_virtual_pair(i, (i + 1) % self.node_limit, 1.05)
            self.sync.release_fluctuation(i)

    def flush_and_verify(self) -> float:
        drift_safe = self.repo.assert_zero_drift()
        return 1.0 if drift_safe else 0.0
