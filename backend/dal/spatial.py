from dal.utils.tiling_engine import BitwiseTilingEngine
from dal.repositories.partition_repo import BinaryPartitionRepo
class SpatialReconciler:
    def __init__(self):
        self.tiler = BitwiseTilingEngine()
        self.repo = BinaryPartitionRepo()
    def map_node(self, node_id: bytes, x: float, y: float, depth: int):
        sig = self.tiler.generate_tile_sig(x, y, depth)
        self.repo.shard_vertex(node_id, sig)
