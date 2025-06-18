from copyreg import remove_extension
import os
import ast
import sys
from collections import defaultdict, deque


class Combiner:
    def __init__(self, root: str, files: list[str]):
        self.root = root
        self.files = set(map(os.path.abspath, files))
        self.result = None

        print(f"Start combine...")

    def get_local(self, filename: str):
        for suffix in (".py", ".pyc", ".pyd", ".pyo", ".pyw", ".pyx"):
            n1 = os.path.abspath(filename.replace(".", "/") + suffix)
            if n1 in self.files:
                return n1
            n2 = os.path.abspath(filename[: filename.find(".")] + suffix)
            if n2 in self.files:
                return n2
        return None

    def get_imports(self, filename):
        with open(filename, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods |= set(map(lambda x: x.name, node.names))
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    mods |= {node.module}
        return [*filter(None, map(self.get_local, mods))]

    def get_order(self, graph):
        indeg = {x: 0 for x in graph}
        for m, deps in graph.items():
            for d in deps:
                indeg[d] += 1
        q = [m for m, d in indeg.items() if d == 0]
        order = []
        while q:
            m = q.pop()
            order.append(m)
            for m in graph[m]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    q.append(m)
        if len(order) != len(graph):
            raise RuntimeError("import cycle")
        # real order is reversed
        return order[::-1]

    def combine(self):
        # get dependences
        file_deps = {x: self.get_imports(x) for x in self.files}

        # get order
        order = self.get_order(file_deps)

        # combine files
        self.result = self.join(order)

    def save(self, filename):
        if self.result is None:
            raise RuntimeError("Files not combined. (call .combine() first)")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.result)
        print(f"Saved to {filename}")

    def get_result(self):
        if self.result is None:
            raise RuntimeError("Files not combined. (call .combine() first)")
        return self.result

    def remove_local_imports(self, src, module_name):

        class ImportRemover(ast.NodeTransformer):

            def __init__(self, combiner: Combiner):
                self.combiner = combiner

            def visit(self, node):
                if isinstance(node, ast.Import) and any(map(self.combiner.get_local, map(lambda x: x.name, node.names))):
                    return None
                if isinstance(node, ast.ImportFrom) and node.module and self.combiner.get_local(node.module):
                    return None
                self.generic_visit(node)
                return node

        tree = ast.parse(src)

        remover = ImportRemover(self)
        new_tree = remover.visit(tree)

        assert isinstance(new_tree, ast.Module)

        new_tree.body.append(ast.parse(f"{module_name} = type('__ONE_trash', (dict,), {{'__getattribute__':(lambda s,x:s[x])}})(globals().copy())").body[0])

        res = ast.unparse(new_tree)
        return res

    def join(self, order: list[str]):
        parts = []
        for mod in order:
            with open(mod, encoding="utf-8") as f:
                src = f.read()
            parts.append(self.remove_local_imports(src, os.path.basename(mod).removesuffix(".py")))
        return "\n\n".join(parts)
