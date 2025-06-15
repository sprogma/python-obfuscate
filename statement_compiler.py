from common import jsd
import code_provider
from exceptions import CompilationError
import re
import tokenize
import ast
import io
import random
import time



class StatementCompiler(code_provider.CodeProvider):
    """
        This class must compile single statement into expression
    """


    def __init__(self):
        self.seed = str(random.randint(0, 999999999) + int(time.time() * 1000))


    def custom_header(self):
        return """
            ()
    """

    def _set_target(self, target: ast.Expr, value: str) -> str:

        if isinstance(target, ast.Tuple):
            raise NotImplementedError("tuple set")
        elif isinstance(target, ast.Attribute):
            raise NotImplementedError("attribute set")
        elif isinstance(target, ast.Name):
            return f"(({target.id} := ({value})) and False)"
        raise ValueError("StatementCompiler._set_target wrong target.")

    def compile(self, stm: str) -> str | None:

        tree = ast.parse(stm)

        assign = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) or isinstance(node, ast.AugAssign) or isinstance(node, ast.AnnAssign):
                if assign is not None:
                    raise CompilationError("Error: Two assign nodes in one statement. [Impossible]")
                assign = node

        # is there assignement operator?
        if assign is not None:
            if isinstance(assign, ast.AugAssign):
                # in this case there cannot be chain of a = b = c expressions.
                raise NotImplementedError("+=, -=, ... statements.")
            else:
                targets = []
                value = None
                if isinstance(assign, ast.AnnAssign):
                    # there is only one target
                    targets.append(assign.target)
                    if assign.value is not None:
                        value =  ast.get_source_segment(stm, assign.value) # or use ast.unparse
                else:
                    targets.extend(assign.targets)

                    value =  ast.get_source_segment(stm, assign.value) # or use ast.unparse

                if value is None:
                    return None

                targets = [*map(lambda x: jsd(code=ast.get_source_segment(stm, x), ast=x), targets)]

                value_var = f"__t{self.seed}";

                exp = f"({value_var} := ({value})) and False"

                # assign value to all
                for t in targets:
                    tset = self._set_target(t.ast, value_var)
                    exp = f"({exp}) or ({tset})"

                return exp

        else:
            # still, need make expression false-equal
            return f"({stm}) and False"
