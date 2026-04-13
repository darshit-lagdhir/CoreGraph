from __future__ import annotations

from typing import ClassVar, Dict, Iterable, List

from backend.dal.models import VirtualNode
from backend.dal.repositories.base import BaseMemoryRepository


class NodeRepository(BaseMemoryRepository[VirtualNode]):
    """Strict O(1) Index Manifold for 3.81M Node Subsets"""

    _name_index: ClassVar[Dict[str, str]] = {}
    _category_index: ClassVar[Dict[str, set[str]]] = {}

    def __init__(self):
        super().__init__("nodes")
        self.__class__._category_index.setdefault("__all__", set())

    async def insert_node(self, node: VirtualNode) -> None:
        await self.insert(node.id, node)
        self.__class__._name_index[node.name] = node.id
        self.__class__._category_index.setdefault(node.category, set()).add(node.id)
        self.__class__._category_index["__all__"].add(node.id)

    async def get_by_name(self, name: str) -> VirtualNode | None:  # type: ignore
        node_id = self.__class__._name_index.get(name)
        if node_id:
            return await self.get_by_id(node_id)
        return None

    async def get_by_category(self, category: str) -> list[VirtualNode]:
        node_ids = self.__class__._category_index.get(category, set())
        return await self.get_many(node_ids)

    async def insert_virtual_node(
        self,
        node_id: str,
        name: str,
        category: str,
        adjacencies: Iterable[str] | None = None,
    ) -> VirtualNode:
        node = VirtualNode(node_id=node_id, name=name, category=category)
        if adjacencies is not None:
            node.attach_adjacencies(list(adjacencies))
        await self.insert_node(node)
        return node

    async def all_nodes(self) -> List[VirtualNode]:
        return list(self.snapshot().values())
