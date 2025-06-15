import common
import code_provider
import tokenize
import ast
import io




class Preprocessor(code_provider.CodeProvider):
    """
        This class removes comments and docstrings from
        source code.
        And normalize all strings (make one line)
    """

    def __init__(self):
        ...

    def normalize(self, code: str) -> str:
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
        # and also convert all multiline strings to normal
        return ast.unparse(tree)



