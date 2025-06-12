import common
import code_provider
import re
import tokenize
import io



class StatementCompiler(code_provider.CodeProvider):
    """
        This class must compile single statement into expression
    """


    def custom_header(self):
        return """
            ()
    """

    def _normalize_assignment_chain(self, exp: str, *chain: (str)) -> str:
        if not chain:
            return exp

        inner = self._normalize_assignment_chain(*chain)

        tok = [*tokenize.tokenize(io.BytesIO(exp.encode()).readline)]

        # is exp - tuple assignment.
        if any(map(lambda x: x.type == tokenize.OP and x.string == ",", tok)):
            # create generator from inner chain
            gen = f"({inner})"
            raise NotImplementedError()
        else:
            if any(map(lambda x: x.type == tokenize.OP and x.string == "[", tok)):
                raise NotImplementedError()
            elif any(map(lambda x: x.type == tokenize.OP and x.string == ".", tok)):
                raise NotImplementedError()
            else:
                return f"{exp} := ({inner})"

    def compile(self, stm: str) -> str:
        is_base_assign = lambda x: x.type == tokenize.OP and x.string == "="
        is_self_assign = lambda x: x.type == tokenize.OP and x.string in ("+=", "-=", "*=", "/=", "%=", "**=")
        is_any_assign = lambda x: is_base_assign(x) or is_self_assign(x)

        # tokenize string
        tok = [*tokenize.tokenize(io.BytesIO(stm.encode()).readline)]

        # is there assignement operator?
        if any(map(is_any_assign, tok)):
            # is there one of "+=", "-=", ...
            if any(map(is_self_assign, tok)):
                # in this case there cannot be chain of a = b = c expressions.
                raise NotImplementedError("+=, -=, ... statements.")
            else:
                ops = [[]]
                for i in tok:
                    if is_base_assign(i):
                        ops.append([])
                    elif i.type != tokenize.ENCODING:
                        ops[-1].append(i)

                ops = [*map(tokenize.untokenize, ops)]

                # join resulting ops
                exp = self._normalize_assignment_chain(*ops)

                return exp
        return stm
