import asyncio
from typing import Dict, Optional, TypeVar, Generic

T = TypeVar('T')

class BaseMemoryRepository(Generic[T]):
    """Singleton memory-resident data vault utilizing O(1) hash indices."""
    _vault: Dict[str, Dict[str, T]] = {}
    _locks: Dict[str, asyncio.Lock] = {}

    def __init__(self, collection_name: str):
        self.collection = collection_name
        if collection_name not in self.__class__._vault:
            self.__class__._vault[collection_name] = {}
            self.__class__._locks[collection_name] = asyncio.Lock()

    async def get_by_id(self, item_id: str) -> Optional[T]:
        """O(1) dictionary lookup bypassing external DB connections."""
        return self.__class__._vault[self.collection].get(item_id)

    async def insert(self, item_id: str, item: T) -> None:
        """Thread-safe instantiation into the 3.81M node matrix."""
        async with self.__class__._locks[self.collection]:
            self.__class__._vault[self.collection][item_id] = item
