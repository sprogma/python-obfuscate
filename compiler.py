from site import ENABLE_USER_SITE
import common
import tokenize
import io


class Compiler:
    def __init__(self, preprocessor, statement_compiler):
        self.p = preprocessor
        self.sc = statement_compiler

    def compile(self, code: str) -> str:

        # preprocess code
        code = self.p.normalize(code)

        # assume that there is no multiline strings

        code = self._compile_block(code)


        # normalize code
        code = self.p.normalize(code)

        return code

    def _compile_block(self, code: str) -> str:
        if code == "":
            return "False"

        # read content
        if "\n" in code:
            first, other = code.split('\n', 1)
        else:
            first = code
            other = ""
        indent = len(first) - len(first.lstrip(" "))
        line = first[indent:]

        # check content
        if line.startswith("if"):
            raise NotImplementedError()
        else:
            # not keyword

            exp = self.sc.compile(line)

            follow = self._compile_block(other)
            return f"({exp}) or ({follow})"

