from graphql import parse, visit, Visitor

query = "{ repository(name: \"r\") { name } }"
ast = parse(query)

class MyVisitor(Visitor):
    def enter_field(self, node, *args):
        print(f"ENTERED FIELD: {node.name.value}")

visit(ast, MyVisitor())
print("VISIT COMPLETE")
