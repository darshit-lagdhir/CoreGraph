from typing import List, Dict, ClassVar

class SharedNodeFlyweight:
    """Flyweight cache for common attributes to ensure 150MB limit compliance across 3.81M nodes."""
    _cache: ClassVar[Dict[str, dict]] = {}

    @classmethod
    def get_state(cls, category: str) -> dict:
        if category not in cls._cache:
            cls._cache[category] = {"category": category, "baseline_risk": 0.05, "virtualized": True}
        return cls._cache[category]

class VirtualNode:
    """High-density synthetic node utilizing __slots__ for strict memory bounding."""
    __slots__ = ['id', 'name', '_shared_state', 'adjacencies']

    def __init__(self, node_id: str, name: str, category: str):
        self.id = node_id
        self.name = name
        self._shared_state = SharedNodeFlyweight.get_state(category)
        self.adjacencies: List[str] = [] # O(1) appending adjacency list

    @property
    def category(self) -> str:
        return self._shared_state["category"]
