"""
Structural dependency flattener.
Transforms hierarchical JSON payloads into an iterative stream of nodes and edges.
"""

import asyncio
import logging
from typing import Dict, Any, AsyncGenerator, Set, Tuple

logger = logging.getLogger(__name__)


class TopologicalAnomaly(Exception):
    """Raised when traversal detects depth violation or circular dependency."""

    pass


class RecursiveDependencyFlattener:
    """Iterative stack-based flattener for processing standard dependency layouts."""

    __slots__ = ("_hardware_tier", "_max_depth", "_seen_nodes", "_root_counter")

    def __init__(self, hardware_tier: str = "POTATO", max_depth: int = 100):
        self._hardware_tier = hardware_tier
        self._max_depth = max_depth
        self._seen_nodes: Set[int] = set()
        self._root_counter = 0

    def _is_already_seen(self, node_hash: int) -> bool:
        if node_hash in self._seen_nodes:
            return True
        self._seen_nodes.add(node_hash)
        return False

    def _normalize_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizes strings and bit-packs status flags."""
        name = raw_data.get("name", "").replace("\x00", "").strip()
        version = raw_data.get("version", "0.0.0").replace("\x00", "").strip()

        flags = 0
        if raw_data.get("deprecated"):
            flags |= 1 << 0
        if raw_data.get("vulnerabilities"):
            flags |= 1 << 1

        return {
            "purl": f"pkg:generic/{name}@{version}",
            "name": name,
            "version": version,
            "flags": flags,
        }

    async def flatten_tree(self, payload: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Iterative traversal of the dependency ecosystem.
        Yields parsed nodes and edges as isolated dictionaries to stabilize heap memory.
        """
        self._root_counter += 1
        if self._root_counter % 1000 == 0:
            self._seen_nodes.clear()

        # Stack stores: (current_node_data, current_depth, parent_purl, path_registry)
        stack = [(payload, 0, None, set())]

        while stack:
            if self._hardware_tier != "REDLINE":
                await asyncio.sleep(0.001)

            current_data, current_depth, parent_purl, current_path = stack.pop()

            if current_depth > self._max_depth:
                logger.warning(f"Depth limit {self._max_depth} breached. Pruning branch.")
                continue

            normalized = self._normalize_metadata(current_data)
            purl = normalized["purl"]

            if purl in current_path:
                logger.warning(f"Circular dependency anomaly: {purl}")
                continue

            node_hash = hash(purl)

            if not self._is_already_seen(node_hash):
                yield {"type": "node", "data": normalized}

            if parent_purl:
                yield {"type": "edge", "source": parent_purl, "target": purl}

            next_path = current_path.copy()
            next_path.add(purl)

            dependencies = current_data.get("dependencies", {})
            for dep_name, dep_data in dependencies.items():
                if isinstance(dep_data, dict):
                    if "name" not in dep_data:
                        dep_data["name"] = dep_name
                    stack.append((dep_data, current_depth + 1, purl, next_path))
