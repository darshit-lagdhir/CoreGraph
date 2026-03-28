"""
Parser component initialization.
"""

from .kernel import RecursiveDependencyFlattener, TopologicalAnomaly

__all__ = ["RecursiveDependencyFlattener", "TopologicalAnomaly"]
