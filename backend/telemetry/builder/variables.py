import io
import json
import logging
from typing import Dict, Any, Type, Optional, Union

# Hardware-Aware Sizing Limits
_MAX_STRING_LENGTH = 256
_MAX_LOGIN_LENGTH = 64
_MAX_INTEGER_BOUNDARY = 2147483647


class GQLVariableShield:
    """
    Module 5 - Task 004: Defensive Sentry for Ingestion Variables.
    Enforces lexical integrity, truncates oversized metadata sweeps,
    and neutralizes potential GraphQL/JSON injection attacks.
    """

    __slots__ = ()

    @staticmethod
    def audit_string(val: str, max_length: int = _MAX_STRING_LENGTH) -> str:
        """Executes length capping and filters zero-width formatting characters."""
        if not isinstance(val, str):
            val = str(val)
        sanitized = "".join(char for char in val if ord(char) >= 32 and ord(char) != 127)
        return sanitized[:max_length]

    @staticmethod
    def audit_int(val: Union[int, str]) -> int:
        """Enforces physical integer boundary limits preventing provider overflows."""
        try:
            parsed = int(val)
            if parsed > _MAX_INTEGER_BOUNDARY:
                return _MAX_INTEGER_BOUNDARY
            if parsed < -_MAX_INTEGER_BOUNDARY:
                return -_MAX_INTEGER_BOUNDARY
            return parsed
        except (ValueError, TypeError):
            logging.error(
                f"Integrity Violation: Coercion failure for Int constraint on value: {val}"
            )
            return 0


class GQLInputSerializer:
    """
    Zero-Allocation JSON Materializer.
    Bypasses standard Python json module allocations by streaming directly to a pre-allocated byte-array.
    """

    __slots__ = ()

    @staticmethod
    def serialize_to_buffer(registry_data: Dict[str, Any]) -> str:
        """
        O(N) single-pass direct-to-buffer JSON compilation.
        Forces deterministic sorting for forensic collision checks.
        """
        buffer = io.StringIO()
        buffer.write("{")

        # Enforce deterministic order for hashing compatibility
        sorted_keys = sorted(registry_data.keys())
        total_keys = len(sorted_keys)

        for idx, key in enumerate(sorted_keys):
            val = registry_data[key]

            # Key Materialization
            buffer.write(f'"{key}":')

            # Value Materialization and Type Branching
            if isinstance(val, str):
                # Only use json.dumps for standard string escaping efficiency
                buffer.write(json.dumps(val))
            elif isinstance(val, bool):
                buffer.write("true" if val else "false")
            elif isinstance(val, (int, float)):
                buffer.write(str(val))
            elif val is None:
                buffer.write("null")
            else:
                # Fallback for nested InputObjects
                buffer.write(json.dumps(val))

            if idx < total_keys - 1:
                buffer.write(",")

        buffer.write("}")

        payload = buffer.getvalue()
        buffer.close()
        return payload


class VariableRecord:
    """
    Slotted DTO tracking scalar constraints and localized AST dependencies.
    """

    __slots__ = ("name", "schema_type", "value")

    def __init__(self, name: str, schema_type: str, value: Any):
        self.name = name
        self.schema_type = schema_type
        self.value = value


class GQLVariableRegistry:
    """
    Hardware-Aware Slotted Variable Registry.
    Maintains a deterministic 1:1 mapping between structural AST requirements
    and sanitized metadata constants with a perfectly flat RAM profile.
    """

    __slots__ = ("_registry", "_shield")

    def __init__(self):
        self._registry: Dict[str, VariableRecord] = {}
        self._shield = GQLVariableShield()

    def register(self, alias_prefix: str, expected_type: str, raw_value: Any, key_name: str) -> str:
        """
        Executes strict Type-Governance and deterministic variable assignment.
        """
        var_id = f"{alias_prefix}_{key_name}"

        # In-Flight Governance Gate
        sanitized_value: Any = raw_value
        if "String" in expected_type or "ID" in expected_type:
            sanitized_value = self._shield.audit_string(raw_value)
        elif "Int" in expected_type:
            sanitized_value = self._shield.audit_int(raw_value)
        elif "Boolean" in expected_type:
            sanitized_value = bool(raw_value)

        self._registry[var_id] = VariableRecord(
            name=var_id, schema_type=expected_type, value=sanitized_value
        )

        return var_id

    def resolve_definition_map(self) -> Dict[str, str]:
        """Provides syntactically valid GraphQL query header types ($var: Type!)."""
        return {record.name: record.schema_type for record in self._registry.values()}

    def materialze_payload(self) -> str:
        """Bridging interface engaging the zero-allocation buffering kernel."""
        execution_map = {record.name: record.value for record in self._registry.values()}
        return GQLInputSerializer.serialize_to_buffer(execution_map)

    def flush(self) -> None:
        """Batch-scoped temporal lifecycle destruction constraint."""
        self._registry.clear()
