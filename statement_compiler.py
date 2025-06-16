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
            (True)
    """

    def _set_target(self, target: ast.Expr, value: str) -> str:

        if isinstance(target, ast.Tuple):
            # if it is simple tuple set:
            exp = f"(__t{self.seed}_i := iter({value})) and False"
            for e in target.elts:
                str_e = ast.unparse(e)
                exp = f"({exp}) or (({str_e} := next(__t{self.seed}_i)) and False)"
            return exp
        elif isinstance(target, ast.Attribute):
            raise NotImplementedError("attribute set")
        elif isinstance(target, ast.Subscript):
            return f"({ast.unparse(target.value)}).__setitem__({ast.unparse(target.slice)}, ({value})) and False"
        elif isinstance(target, ast.Name):
            return f"({target.id} := ({value})) and False"
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
                value = ast.unparse(assign.value)
                i_methods = {
                    ast.Add: "__iadd__",
                    ast.Sub: "__isub__",
                    ast.Mult: "__imul__",
                    ast.Div: "__itruediv__",
                    ast.FloorDiv: "__ifloordiv__",
                    ast.Mod: "__imod__",
                    ast.Pow: "__ipow__",
                    ast.LShift: "__ilshift__",
                    ast.RShift: "__irshift__",
                    ast.BitAnd: "__iand__",
                    ast.BitXor: "__ixor__",
                    ast.BitOr: "__ior__"
                }
                methods = {
                    ast.Add: "__add__",
                    ast.Sub: "__sub__",
                    ast.Mult: "__mul__",
                    ast.Div: "__truediv__",
                    ast.FloorDiv: "__floordiv__",
                    ast.Mod: "__mod__",
                    ast.Pow: "__pow__",
                    ast.LShift: "__lshift__",
                    ast.RShift: "__rshift__",
                    ast.BitAnd: "__and__",
                    ast.BitXor: "__xor__",
                    ast.BitOr: "__or__"
                }

                # call methods on body
                target = ast.unparse(assign.target)
                i_method = i_methods[type(assign.op)]
                method = methods[type(assign.op)]

                exp = f"""
                    [
                        __t{self.seed} := type({target}),
                        (
                            {target} := __t{self.seed}.{i_method}({target}, {value})
                        )
                        if hasattr({target}, {repr(i_method)})
                        else
                        (
                            {target} := __t{self.seed}.{method}({target}, {value})
                        )
                    ].__len__() == 0
                """

                return exp
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
