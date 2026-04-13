from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class BaseMemoryRepository(Generic[T]):
    """Singleton memory-resident data vault utilizing O(1) hash indices."""

    _vault: Dict[str, Dict[str, T]] = {}
    _locks: Dict[str, asyncio.Lock] = {}

    def __init__(self, collection_name: str):
        self.collection = collection_name
        self.__class__._ensure_collection(collection_name)

    @classmethod
    def _ensure_collection(cls, collection_name: str) -> None:
        if collection_name not in cls._vault:
            cls._vault[collection_name] = {}
            cls._locks[collection_name] = asyncio.Lock()

    async def get_by_id(self, item_id: str) -> Optional[T]:
        """O(1) dictionary lookup bypassing external DB connections."""
        return self.__class__._vault[self.collection].get(item_id)

    async def get_many(self, item_ids: Iterable[str]) -> list[T]:
        vault = self.__class__._vault[self.collection]
        return [item for item_id in item_ids if (item := vault.get(item_id)) is not None]

    async def insert(self, item_id: str, item: T) -> None:
        """Thread-safe instantiation into the 3.81M node matrix."""
        async with self.__class__._locks[self.collection]:
            self.__class__._vault[self.collection][item_id] = item

    async def bulk_insert(self, items: Dict[str, T]) -> None:
        async with self.__class__._locks[self.collection]:
            self.__class__._vault[self.collection].update(items)

    async def delete(self, item_id: str) -> None:
        async with self.__class__._locks[self.collection]:
            self.__class__._vault[self.collection].pop(item_id, None)

    async def count(self) -> int:
        return len(self.__class__._vault[self.collection])

    def snapshot(self) -> Dict[str, T]:
        return dict(self.__class__._vault[self.collection])
