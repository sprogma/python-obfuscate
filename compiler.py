import common


class Compiler:
    def __init__(self, preprocessor, statement_compiler):
        self.p = preprocessor
        self.sc = statement_compiler

    def compile(self, code: str) -> str:

        # preprocess code
        code = self.p.normalize(code)

        code = self._compile_block(code)

        # normalize code
        code = self.p.normalize(code)

        return code

    def _compile_block(self, code: str) -> str:

        stmts = code.split("\n")

        stmts = [*map(self.sc.compile, stmts)]

        return " or ".join(map(lambda x: f"({x})", stmts))

