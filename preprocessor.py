import common
import ast




class Preprocessor:
    """
        This class removes comments and docstrings from
        source code.
    """

    @staticmethod
    def preprocess(code: str) -> str:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            # remove docstrigns
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)) and ast.get_docstring(node, clean=False) is not None):
                if (    node.body and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                    node.body.pop(0)

        # ast.unparse removes all comments
        return ast.unparse(tree)
