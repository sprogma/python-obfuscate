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

        if "," in exp:
            ...

        res = inner
        return res

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

                print(*ops,sep="\n")

                # join resulting ops
                exp = self._normalize_assignment_chain(*ops)

                return exp
        return stm


c = StatementCompiler()

y = 3

print(c.compile("a, b = 1, 2"))
exit(0)

print(eval(c.compile("a,b = 1, 2")))


print(c.compile("z = x = 5 + 6 * y"))
print(eval(c.compile("z = x = 5 + 6 * y")))

print(c.compile("y + 5 == 8"))
print(eval(c.compile("y + 5 == 8")))

a = [1, 2, 3]

print(c.compile("a[0] = 5 + 6 * y"))
print(eval(c.compile("a[0] = 5 + 6 * y")))