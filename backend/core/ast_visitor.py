import ast


class CognitiveComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_AsyncFor(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_With(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_AsyncWith(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def get_cognitive_complexity(source_code: str) -> int:
    try:
        tree = ast.parse(source_code)
        visitor = CognitiveComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity
    except Exception:
        return 0
