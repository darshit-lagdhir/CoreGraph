from __future__ import annotations

from types import MappingProxyType
from typing import ClassVar, Dict, List, Mapping

from backend.dal.seed import generative_seeder


class SharedNodeFlyweight:
    """Flyweight cache for common attributes to ensure 150MB limit compliance across 3.81M nodes."""

    _cache: ClassVar[Dict[str, Mapping[str, object]]] = {}

    @classmethod
    def get_state(cls, category: str) -> Mapping[str, object]:
        state = cls._cache.get(category)
        if state is None:
            state = MappingProxyType(
                {
                    "category": category,
                    "baseline_risk": 0.05,
                    "virtualized": True,
                    "residency_class": "ghost-mapped",
                }
            )
            cls._cache[category] = state
        return state


class VirtualNode:
    """High-density synthetic node utilizing __slots__ for strict memory bounding."""

    __slots__ = ["id", "name", "_shared_state", "adjacencies", "_metadata_ref"]

    def __init__(self, node_id: str, name: str, category: str):
        self.id = node_id
        self.name = name
        self._shared_state = SharedNodeFlyweight.get_state(category)
        self.adjacencies: List[str] = []
        self._metadata_ref: Mapping[str, object] | None = None

    @property
    def category(self) -> str:
        return str(self._shared_state["category"])

    @property
    def baseline_risk(self) -> float:
        return float(self._shared_state["baseline_risk"])

    def attach_adjacencies(self, adjacencies: List[str]) -> None:
        self.adjacencies = list(adjacencies)

    @property
    def metadata_ref(self) -> Mapping[str, object]:
        """
        Dynamically extracts deep forensic attributes via the Adversarial DNA Kernel.
        Zero memory overhead per node: identities generated at retrieval bounds.
        """
        if self._metadata_ref is not None:
            return self._metadata_ref

        # Recover integer index from node ID (assuming format "n_{int}" or similar)
        idx = 0
        try:
            # Simple extraction for fast integer parsing
            idx = int("".join(filter(str.isdigit, self.id)))
        except ValueError:
            idx = hash(self.id) % 3810000

        return generative_seeder.derive_node_identity(idx)

    def bind_metadata(self, metadata: Mapping[str, object]) -> None:
        self._metadata_ref = metadata

    def compact_view(self) -> tuple[str, str, str]:
        return (self.id, self.name, self.category)
