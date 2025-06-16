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
        return super().custom_header() + [
            # function to use __i...__ methods
            """
                (
                    __ONE_sync_i_op := lambda a, b, im, m, rm:
                    (
                        (
                            result
                        )
                        if callable(mim := getattr(a, im, None)) and (result := mim(b)) is not NotImplemented else
                        (

                            (
                                result
                            )
                            if callable(mm := getattr(a, m, None)) and (result := mm(b)) is not NotImplemented else
                            (
                                (
                                    result
                                )
                                if callable(mrm := getattr(b, rm, None)) and (result := mrm(a)) is not NotImplemented else
                                (
                                    print(f"ERROR: CANNOT ADD {a} AND {b} ({type(a)}, {type(b)})")
                                    or
                                    NotImplemented
                                )
                            )
                        )
                    )
                )
            """
        ]

    def _set_single(self, target: ast.expr, value: str) -> str:
        if isinstance(target, ast.Attribute):
            return f"setattr({ast.unparse(target.value)}, {repr(target.attr)}, {value}) and False"
        elif isinstance(target, ast.Subscript):
            return f"({ast.unparse(target.value)}).__setitem__({ast.unparse(target.slice)}, ({value})) and False"
        elif isinstance(target, ast.Name):
            return f"({target.id} := ({value})) and False"
        raise ValueError("StatementCompiler._set_single wrong target.")

    def _set_target(self, target: ast.Expr, value: str) -> str:

        if isinstance(target, ast.Tuple):
            # if it is simple tuple set:
            exp = f"(__t{self.seed}_i := iter({value})) and False"
            for e in target.elts:
                sets = self._set_single(e, f"next(__t{self.seed}_i)")
                exp = f"({exp}) or (({sets}) and False)"
            return exp
        elif isinstance(target, ast.Attribute):
            return self._set_single(target, value)
        elif isinstance(target, ast.Subscript):
            return self._set_single(target, value)
        elif isinstance(target, ast.Name):
            return self._set_single(target, value)
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
                methods = {
                    ast.Add: ("__iadd__", "__add__", "__radd__"),
                    ast.Sub: ("__isub__", "__sub__", "__rsub__"),
                    ast.Mult: ("__imul__", "__mul__", "__rmul__"),
                    ast.Div: ("__itruediv__", "__truediv__", "__rtruediv__"),
                    ast.FloorDiv: ("__ifloordiv__", "__floordiv__", "__rfloordiv__"),
                    ast.Mod: ("__imod__", "__mod__", "__rmod__"),
                    ast.Pow: ("__ipow__", "__pow__", "__rpow__"),
                    ast.LShift: ("__ilshift__", "__lshift__", "__rlshift__"),
                    ast.RShift: ("__irshift__", "__rshift__", "__rrshift__"),
                    ast.BitAnd: ("__iand__", "__and__", "__rand__"),
                    ast.BitXor: ("__ixor__", "__xor__", "__rxor__"),
                    ast.BitOr: ("__ior__, " "__or_", "__ror_"),
                }
                # call methods on body
                target = assign.target
                str_target = ast.unparse(assign.target)
                i_method, method, r_method = methods[type(assign.op)]

                exp = f"""
                    [
                        __t{self.seed} := type({str_target}),
                        (
                            {self._set_single(target, f"__t{self.seed}_r")}
                        )
                        if (__t{self.seed}_r := __ONE_sync_i_op(({str_target}), ({value}), {repr(i_method)}, {repr(method)}, {repr(r_method)})) is not NotImplemented else
                        (
                            False
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
