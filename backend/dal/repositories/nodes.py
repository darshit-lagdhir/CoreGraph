from backend.dal.repositories.base import BaseMemoryRepository
from backend.dal.models import VirtualNode

class NodeRepository(BaseMemoryRepository[VirtualNode]):
    """Strict O(1) Index Manifold for 3.81M Node Subsets"""
    def __init__(self):
        super().__init__("nodes")
        self._name_index = {} # Secondary O(1) search index to prevent linear scans

    async def insert_node(self, node: VirtualNode):
        await self.insert(node.id, node)
        self._name_index[node.name] = node.id

    async def get_by_name(self, name: str) -> VirtualNode | None: # type: ignore
        node_id = self._name_index.get(name)
        if node_id:
            return await self.get_by_id(node_id)
        return None
