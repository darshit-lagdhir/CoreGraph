import re
from typing import List, Dict, Any, Tuple
from backend.telemetry.builder.ast import GQLASTBuilder, GQLField, GQLFragment


class TelemetryASTFragmenter:
    """
    Module 5 - Task 005: Dynamic AST Fragmentation Kernel.
    Implements Silicon-Safety partitioning, predicting heap residency utilizing
    Multiplicative Entropic weights, and preventing parser/OOM collapse.
    """

    __slots__ = (
        "_hardware_tier",
        "_residency_ceiling",
        "_entropy_weight",
        "_parser_expansion_factor",
    )

    def __init__(self, hardware_tier: str = "redline"):
        self._hardware_tier = hardware_tier
        self._entropy_weight = 64  # Average bytes per atomic telemetry payload block
        self._parser_expansion_factor = 6.5  # PyDict overhead expansion ratio vs raw JSON string

        # Hardware-Aware Safety Valve Thresholds
        if self._hardware_tier == "redline":
            self._residency_ceiling = 80 * 1024 * 1024  # 80MB buffer limit
        else:
            self._residency_ceiling = 10 * 1024 * 1024  # 10MB buffer limit

    def _predict_heap_residency(self, builder: GQLASTBuilder) -> int:
        """
        Residency Prediction Oracle.
        Executes a recursive descent tracking cumulative structural connections against
        the entropic weight limits, translating GraphQL AST to byte bounds.
        """
        total_estimated_nodes = 0
        for root_field in builder._root_fields:
            total_estimated_nodes += self._traverse_and_count(root_field)

        raw_json_estimate = total_estimated_nodes * self._entropy_weight
        projected_heap = int(raw_json_estimate * self._parser_expansion_factor)

        # Apply 20% cushion to safely counter unpredictable Leviathan payloads
        return int(projected_heap * 1.20)

    def _traverse_and_count(self, field: GQLField) -> int:
        """Recursive node-to-byte expansion counter."""
        node_count = 1
        connection_multiplier = 1

        for arg in field.arguments:
            if arg.name in ("first", "last") and isinstance(arg.value, int):
                connection_multiplier = arg.value

        child_count = 0
        for child in field.selections:
            child_count += self._traverse_and_count(child)

        node_count += child_count * connection_multiplier
        return node_count

    def _surgical_minification(self, raw_payload: str) -> str:
        """
        Payload Optimization Manifold.
        Strips entropic whitespace while preserving structural string boundaries.
        """
        # Remove whitespace outside of strings
        minified = re.sub(r'(\s+)(?=(?:[^"]|"[^"]*")*$)', "", raw_payload)
        return minified

    def _sync_variable_subset(
        self, fragment_builder: GQLASTBuilder, original_vars_map: Dict[str, Any]
    ) -> None:
        """
        Variable Synchronization Bridge.
        Migrates only deeply required dynamic variables to the new fragmented builder
        preventing external provider validation rejections due to orphaned variables.
        """
        required_vars = set()

        def _scan_for_vars(field: GQLField):
            for arg in field.arguments:
                if arg.is_variable:
                    required_vars.add(arg.value)
            for child in field.selections:
                _scan_for_vars(child)

        for root in fragment_builder._root_fields:
            _scan_for_vars(root)

        for var_name in required_vars:
            if var_name in original_vars_map:
                fragment_builder.register_variable(
                    name=original_vars_map[var_name].name,
                    type_def=original_vars_map[var_name].type_def,
                    value=original_vars_map[var_name].value,
                )

    def _greedy_split(self, builder: GQLASTBuilder) -> List[GQLASTBuilder]:
        """
        Recursive Partitioning Doctrine.
        Bisects universal AST payloads at the Object level yielding isolated network segments.
        """
        fragments: List[GQLASTBuilder] = []

        if not builder._root_fields:
            return fragments

        midpoint = len(builder._root_fields) // 2

        # Leviathan Handling: Irreducible atomic block exceeding limits
        if midpoint == 0:
            fragments.append(builder)
            return fragments

        left_split = builder._root_fields[:midpoint]
        right_split = builder._root_fields[midpoint:]

        left_builder = GQLASTBuilder()
        right_builder = GQLASTBuilder()

        for field in left_split:
            left_builder.add_root_field(field)
        for field in right_split:
            right_builder.add_root_field(field)

        # Re-attach shared telemetry structural logic
        for frag_name, frag_obj in builder._fragments.items():
            left_builder.register_fragment(frag_obj)
            right_builder.register_fragment(frag_obj)

        self._sync_variable_subset(left_builder, builder._variables)
        self._sync_variable_subset(right_builder, builder._variables)

        # Recursive safety check against new bounds
        for new_builder in (left_builder, right_builder):
            if self._predict_heap_residency(new_builder) > self._residency_ceiling:
                fragments.extend(self._greedy_split(new_builder))
            else:
                fragments.append(new_builder)

        return fragments

    def fragment_ast(self, universal_builder: GQLASTBuilder) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Primary Regulatory Intake.
        Projects constraints, executes Object splitting, ensures variable sync and yields minified artifacts.
        """
        projected_residency = self._predict_heap_residency(universal_builder)

        if projected_residency <= self._residency_ceiling:
            raw_payload, execution_vars = universal_builder.materialize()
            return [(self._surgical_minification(raw_payload), execution_vars)]

        fragmented_builders = self._greedy_split(universal_builder)
        materialized_fragments = []

        for builder in fragmented_builders:
            raw_payload, execution_vars = builder.materialize()
            optimized_payload = self._surgical_minification(raw_payload)
            materialized_fragments.append((optimized_payload, execution_vars))

        return materialized_fragments
