from common import jsd
from exceptions import CompilationError
import tokenize
import ast
import io


class Compiler:
    def __init__(self, preprocessor, statement_compiler):
        self.p = preprocessor
        self.sc = statement_compiler

        self.code: list[str] = []

        self.filename: str = ""

    def compile(self, filename: str, code: str) -> str | None:

        # load data
        self.filename = filename

        # preprocess code
        code = self.p.normalize(code)

        # dump normalized code [for debug]
        with open(filename.removesuffix(".py")+"_normalized.py", "w") as f:
            f.write(code)

        # use normalized features like no ; or code after : in line.

        self.code = code.split('\n')

        result = self._compile_block(0, 0)

        if result.code == None:
            raise CompilationError(f"{self.filename}:{result.next}:0: Empty resulting code.")

        # normalize result
        result = self.p.normalize(result.code)

        return result

    def _unpack_string(self, full_line: str) -> tuple[int, str]:
        indent = len(full_line) - len(full_line.lstrip(" "))
        line = full_line[indent:]
        return indent, line

    def _compile_block(self, codeline: int, baseindent: int, new_block = False) -> jsd:
        # print(f"call _compile_block({codeline}, {baseindent}, {new_block})")
        # __import__("time").sleep(0.5)

        if codeline >= len(self.code):
            return jsd(next=codeline, code=None)


        indent, line = self._unpack_string(self.code[codeline])


        if new_block:
            if baseindent < indent:
                # all is ok
                baseindent = indent
            elif baseindent >= indent:
                # error
                raise CompilationError(f"{self.filename}:{codeline}:{indent}: empty block of code.")
        else:
            if baseindent < indent:
                # error
                raise CompilationError(f"{self.filename}:{codeline}:{indent}: Wrong indent uprising.")
            elif baseindent > indent:
                # end of block
                return jsd(next=codeline, code=None)



        # check content
        if line.startswith("if"):

            branches = []

            exp = line[:line.rfind(":")].removeprefix("if").strip()

            if_true = self._compile_block(codeline + 1, indent, new_block = True)
            end_line: int = if_true.next

            branches.append(jsd(exp=exp, code=if_true.code))

            end_indent = None
            end_code = None

            while True:
                if end_line >= len(self.code):
                    break
                end_indent, end_code = self._unpack_string(self.code[end_line])
                if end_indent != indent or not end_code.startswith("elif"):
                    break

                exp = end_code[:end_code.rfind(":")].removeprefix("elif").strip()

                elif_true = self._compile_block(end_line + 1, indent, new_block = True)

                branches.append(jsd(exp=exp, code=elif_true.code))

                end_line = elif_true.next


            else_code = None
            return_line = end_line

            if end_indent is not None and end_indent > indent:
                raise CompilationError(f"{self.filename}:{end_line}:{indent}: Wrong indent uprising.")
            elif end_indent is not None and end_indent < indent:
                ... # end of block
            else:
                # indents are equal
                if end_line < len(self.code):
                    end_indent, end_code = self._unpack_string(self.code[end_line])
                    if end_code.startswith("else"):
                        else_res = self._compile_block(end_line + 1, indent, new_block = True)
                        else_code = else_res.code
                        return_line = else_res.next

            following_code = None

            # compile following code
            follow = self._compile_block(return_line, indent)
            following_code = follow.code
            return_line = follow.next

            exp = else_code

            for b in branches[::-1]:
                exp = f"({b.code}) if ({b.exp}) else {exp}"

            # make false-equal
            exp = f"({exp}) and False"

            # add following code
            if following_code is not None:
                exp = f"({exp}) or ({following_code})"

            return jsd(next=return_line, code=exp)
        elif line.startswith("for"):
            fake_code = f"{line}..."

            # use ast to split it in parts
            tree = ast.parse(fake_code)

            vars_src = iter_src = None
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    vars_src = ast.get_source_segment(fake_code, node.target)
                    iter_src = ast.get_source_segment(fake_code, node.iter)

            if vars_src is None or iter_src is None:
                raise CompilationError(f"{self.filename}:{codeline}:{indent}: For cycle is wrong and wasn't parsed.")

            # supproted only simple for with one variable

            # compile body
            body = self._compile_block(codeline + 1, indent, new_block = True)

            # compile following code

            follow = self._compile_block(body.next, indent)

            # create expression

            exp = f"any((({body.code}) for {vars_src} in ({iter_src})))"

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        else:
            # not keyword

            exp = self.sc.compile(line)

            follow = self._compile_block(codeline + 1, indent)

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)

