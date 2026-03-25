import hashlib
from typing import List, Dict, Any, Optional
from graphql import parse, visit, Visitor, FieldNode

class OSINTQueryAnalyzer(Visitor):
    MAX_STACK_DEPTH = 15

    def __init__(self):
        super().__init__()
        self.requested_fields: List[str] = []
        self.package_targets: List[Dict[str, Any]] = []
        self.field_aliases: Dict[str, str] = {} # Mapping of name -> alias for resolver
        self.max_depth = 0
        self.current_depth = 0

    def enter_field(self, node: FieldNode, key, parent, path, ancestors):
        self.current_depth = len(path) if path else 0
        self.max_depth = max(self.max_depth, self.current_depth)

        if self.current_depth > self.MAX_STACK_DEPTH:
            raise ValueError(f"CRITICAL: GraphQL Recursion Stack Explosion detected (Depth: {self.current_depth})")

        name = node.name.value
        alias = node.alias.value if node.alias else None

        # Track Field-to-Alias mapping for the resolver
        if alias:
            self.field_aliases[name] = alias

        if name in ["repository", "commits", "pullRequests", "stargazers"]:
            args = {}
            if node.arguments:
                for arg in node.arguments:
                    val = getattr(arg.value, 'value', None)
                    args[arg.name.value] = val
                    
            # STRICT ENFORCEMENT: GitHub v4 limits 'first' to 100 nodes.
            if "first" in args and args["first"] > 100:
                 raise ValueError("GraphQL Error: first must be <= 100")

            args['target_alias'] = alias or name
            self.package_targets.append(args)

        self.requested_fields.append(alias or name)

def analyze_query(query_str: str) -> Dict[str, Any]:
    try:
        ast = parse(query_str)
        analyzer = OSINTQueryAnalyzer()
        visit(ast, analyzer)

        return {
            "targets": analyzer.package_targets,
            "max_depth": analyzer.max_depth,
            "fields": list(set(analyzer.requested_fields)),
            "aliases": analyzer.field_aliases
        }
    except Exception as e:
        return {"error": str(e), "targets": [], "max_depth": 0, "fields": []}
