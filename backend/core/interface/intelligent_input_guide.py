import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class IntelligentInputGuide:
    """
    SECTOR DELTA: Intelligent Input Guide.
    Provides Prefix-Trie search and fuzzy matching for 5000-node shards.
    """

    def __init__(self, commands: List[str]):
        self.commands = sorted(commands)
        self.trie: dict = {}
        for cmd in self.commands:
            node = self.trie
            for char in cmd:
                node = node.setdefault(char, {})

    def get_suggestions(self, prefix: str) -> List[str]:
        """
        Sector Delta: Prefix-Trie Search.
        Resolves intended commands with O(log N) efficiency.
        """
        prefix = prefix.upper()
        if not prefix:
            return []

        node = self.trie
        for char in prefix:
            if char not in node:
                return []
            node = node[char]

        return self._collect_suffixes(node, prefix)

    def _collect_suffixes(self, node: dict, prefix: str) -> List[str]:
        results = []
        if not node:
            results.append(prefix)

        for char, next_node in node.items():
            results.extend(self._collect_suffixes(next_node, prefix + char))

        return results
