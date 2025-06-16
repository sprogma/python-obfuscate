from common import jsd
import code_provider
from exceptions import CompilationError
from preprocessor import Preprocessor
from statement_compiler import StatementCompiler
from block_compiler import BlockCompiler
import random
import tokenize
import time
import ast
import io


class Compiler:
    def __init__(self, preprocessor, block_compiler):
        self.p: Preprocessor = preprocessor
        self.b: BlockCompiler = block_compiler

    def compile(self, filename: str, code: str) -> str | None:

        # preprocess code
        code = self.p.normalize(code)

        # dump normalized code [for debug]
        with open(filename.removesuffix(".py")+"_normalized.py", "w") as f:
            f.write(code)

        # compiler uses normalized features like no ; or code after : in line.
        result = self.b.build(filename, code)

        if result.code == None:
            raise CompilationError(f"{filename}:{result.next}:0: Empty resulting code.")


        imports, headers = self._collect_headers()

        # merge result with headers from components
        program = result.code
        # insert headers in reverse order
        for header in headers:
            program = f"(({header}) and False) or ({program})"
        for lib in imports:
            program = f"((__ONE_lib_{lib} := __import__({repr(lib)})) and False) or ({program})"

        print(program)
        print()
        print()

        # normalize result
        program = self.p.normalize(program)

        return program

    def _collect_headers(self) -> tuple[list[str], list[str]]:
        components: list[code_provider.CodeProvider] = [self.p, self.b]
        inc, head = [], []
        for obj in components:
            inc.extend(obj.custom_imports())
            head.extend(obj.custom_header())
        # remove duplicates
        inc = [*set(inc)]
        return inc, head

