import ast

code = """
def example():
    x = 10
    def inner():
        y = 5
        return x + y
    return inner()
"""

# Парсим код в AST
tree = ast.parse(code)

# Обходим дерево и ищем переменные
class VariableVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(f"Function: {node.name}")
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            print(f"Variable assigned: {target.id}")
        self.generic_visit(node)

visitor = VariableVisitor()
visitor.visit(tree)
