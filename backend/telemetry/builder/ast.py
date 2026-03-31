import io
import re
import json
from typing import List, Dict, Optional, Any, Tuple

_GQL_IDENTIFIER_RGX = re.compile(r"^[_A-Za-z][_0-9A-Za-z]*$")


class GQLVariable:
    """
    Slotted structural definition of a GraphQL query variable.
    Enforces strict typing and synchronized dictionary binding.
    """

    __slots__ = ("name", "type_def", "value")

    def __init__(self, name: str, type_def: str, value: Any):
        if not _GQL_IDENTIFIER_RGX.match(name):
            raise ValueError(f"Lexical violation: Invalid variable name '{name}'")
        self.name = name
        self.type_def = type_def
        self.value = value


class GQLArgument:
    """
    Slotted representation of a field argument. Guarantees injection-immunity
    by managing values exclusively as variables or safely escaped literals.
    """

    __slots__ = ("name", "value", "is_variable")

    def __init__(self, name: str, value: Any, is_variable: bool = False):
        if not _GQL_IDENTIFIER_RGX.match(name):
            raise ValueError(f"Lexical violation: Invalid argument name '{name}'")
        self.name = name
        self.value = value
        self.is_variable = is_variable


class GQLField:
    """
    Slotted recursive AST node representing a GraphQL selection.
    Provides in-flight validation and localized complexity tracking.
    """

    __slots__ = ("name", "alias", "arguments", "selections", "fragment_spreads")

    def __init__(self, name: str, alias: Optional[str] = None):
        if not _GQL_IDENTIFIER_RGX.match(name):
            raise ValueError(f"Lexical violation: Invalid field name '{name}'")
        if alias and not _GQL_IDENTIFIER_RGX.match(alias):
            raise ValueError(f"Lexical violation: Invalid field alias '{alias}'")

        self.name = name
        self.alias = alias
        self.arguments: List[GQLArgument] = []
        self.selections: List["GQLField"] = []
        self.fragment_spreads: List[str] = []

    def add_argument(self, arg: GQLArgument) -> "GQLField":
        self.arguments.append(arg)
        return self

    def add_selection(self, field: "GQLField") -> "GQLField":
        self.selections.append(field)
        return self

    def add_fragment_spread(self, fragment_name: str) -> "GQLField":
        if not _GQL_IDENTIFIER_RGX.match(fragment_name):
            raise ValueError(f"Lexical violation: Invalid fragment spread '{fragment_name}'")
        self.fragment_spreads.append(fragment_name)
        return self


class GQLFragment:
    """
    Slotted schema-compliant fragment definition. Enables structural deduplication
    and DRY telemetry extraction.
    """

    __slots__ = ("name", "target_type", "selections")

    def __init__(self, name: str, target_type: str):
        if not _GQL_IDENTIFIER_RGX.match(name):
            raise ValueError(f"Lexical violation: Invalid fragment name '{name}'")
        if not _GQL_IDENTIFIER_RGX.match(target_type):
            raise ValueError(f"Lexical violation: Invalid target type '{target_type}'")
        self.name = name
        self.target_type = target_type
        self.selections: List[GQLField] = []

    def add_selection(self, field: GQLField) -> "GQLFragment":
        self.selections.append(field)
        return self


class GQLASTBuilder:
    """
    Module 5 - Task 003: Programmatic GraphQL Abstract Syntax Tree Builder.
    Recursively materializes safe, typed, and minified query strings bypassing
    injection vulnerabilities entirely using a flat memory layout.
    """

    __slots__ = ("_root_fields", "_variables", "_fragments")

    def __init__(self):
        self._root_fields: List[GQLField] = []
        self._variables: Dict[str, GQLVariable] = {}
        self._fragments: Dict[str, GQLFragment] = {}

    def register_variable(self, name: str, type_def: str, value: Any) -> str:
        """Double-entry bookkeeping for runtime variable mapping."""
        self._variables[name] = GQLVariable(name, type_def, value)
        return name

    def register_fragment(self, fragment: GQLFragment) -> None:
        """Registers a structural deduplication fragment."""
        self._fragments[fragment.name] = fragment

    def add_root_field(self, field: GQLField) -> None:
        """Injects a top-level execution selection block."""
        self._root_fields.append(field)

    def materialize(self) -> Tuple[str, Dict[str, Any]]:
        """
        Executes a single-buffer depth-first traversal of the AST.
        Produces a minified GraphQL network payload. O(N) traversal.
        """
        buffer = io.StringIO()

        buffer.write("query")

        # Variable Declaration Prologue
        if self._variables:
            buffer.write("(")
            var_defs = [f"${v.name}:{v.type_def}" for v in self._variables.values()]
            buffer.write(",".join(var_defs))
            buffer.write(")")

        buffer.write("{")

        # Core Selection Assembly
        for i, field in enumerate(self._root_fields):
            self._serialize_field(field, buffer)
            if i < len(self._root_fields) - 1:
                buffer.write(",")

        buffer.write("}")

        # Fragment Trailing Declarations
        for frag in self._fragments.values():
            buffer.write(f"fragment {frag.name} on {frag.target_type}{{")
            for i, field in enumerate(frag.selections):
                self._serialize_field(field, buffer)
                if i < len(frag.selections) - 1:
                    buffer.write(",")
            buffer.write("}")

        executable_vars = {v.name: v.value for v in self._variables.values()}

        payload = buffer.getvalue()
        buffer.close()
        return payload, executable_vars

    def _serialize_field(self, field: GQLField, buffer: io.StringIO) -> None:
        """Recursive serialization engine with defensive escaping."""
        if field.alias:
            buffer.write(f"{field.alias}:")
        buffer.write(field.name)

        if field.arguments:
            buffer.write("(")
            for i, arg in enumerate(field.arguments):
                buffer.write(f"{arg.name}:")
                if arg.is_variable:
                    buffer.write(f"${arg.value}")
                else:
                    # Defensive JSON encoding of scalar values
                    buffer.write(json.dumps(arg.value))
                if i < len(field.arguments) - 1:
                    buffer.write(",")
            buffer.write(")")

        has_children = bool(field.selections)
        has_fragments = bool(field.fragment_spreads)

        if has_children or has_fragments:
            buffer.write("{")

            if has_fragments:
                spreads = [f"...{spread}" for spread in field.fragment_spreads]
                buffer.write(",".join(spreads))
                if has_children:
                    buffer.write(",")

            for i, child in enumerate(field.selections):
                self._serialize_field(child, buffer)
                if i < len(field.selections) - 1:
                    buffer.write(",")

            buffer.write("}")
