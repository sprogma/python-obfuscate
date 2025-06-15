from common import jsd
from exceptions import CompilationError
from preprocessor import Preprocessor
from statement_compiler import StatementCompiler
import random
import tokenize
import time
import ast
import io


class Compiler:
    def __init__(self, preprocessor, statement_compiler):
        self.p: Preprocessor = preprocessor
        self.sc: StatementCompiler = statement_compiler

        self.code: list[str] = []

        self.filename: str = ""

        self.seed = str(random.randint(0, 999999999) + int(time.time() * 1000))

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
        if line.startswith("if "):

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
        elif line.startswith("for "):

            fake_code = f"{line}..."

            # use ast to split it in parts
            tree = ast.parse(fake_code)

            vars_src = iter_src = None
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    vars_src = ast.get_source_segment(fake_code, node.target)
                    iter_src = ast.get_source_segment(fake_code, node.iter)
                    break

            if vars_src is None or iter_src is None:
                raise CompilationError(f"{self.filename}:{codeline}:{indent}: For cycle is wrong and wasn't parsed.")

            # compile body
            body = self._compile_block(codeline + 1, indent, new_block = True)

            # compile following code

            follow = self._compile_block(body.next, indent)

            # create expression

            exp = f"any((({body.code}) for {vars_src} in ({iter_src})))"

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.startswith("import "):
            # using good (strict) syntax of import ... statement
            # split by ","
            modules = line.removeprefix("import").split(",")
            data = []
            for mod in modules:
                # for some reason, python throws an error if module or class name is "as"
                mod = mod.split()
                if len(mod) == 3 and "as" in mod:
                    data.append(jsd(module=mod[0], name=mod[2]))
                elif len(mod) == 1:
                    data.append(jsd(module=mod[0], name=mod[0]))
                else:
                    raise CompilationError(f"{self.filename}:{codeline}:{0}: Wrong import statement.")

            # generate expression
            exp = ""

            for mod in data:
                if exp == "":
                    exp = f"(({mod.name} := __import__({repr(mod.module)})) and False)"
                else:
                    exp = f"({exp}) or (({mod.name} := __import__({repr(mod.module)})) and False)"

            follow = self._compile_block(codeline + 1, indent)

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.startswith("def ") or line.startswith("async "):
            fake_code = f"{line.removeprefix('async').lstrip()}..."

            tree = ast.parse(fake_code)

            name = args = None

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    signature = node.args
                    parts: list[str] = []

                    # posonlyargs (after them there are "/")
                    if signature.posonlyargs:
                        parts.extend(map(lambda x: x.arg, signature.posonlyargs))
                        parts.append("/")

                    # base args
                    parts.extend(map(lambda x: x.arg, signature.args))

                    # check if there is one-starred arguments
                    if signature.vararg:
                        parts.append(f"*{signature.vararg.arg}")
                    elif signature.kwonlyargs:
                        parts.append("*")

                    # key-value args
                    parts.extend(map(lambda x: x.arg, signature.kwonlyargs))

                    # dynamic key-value (**)
                    if signature.kwarg:
                        parts.append(f"**{signature.kwarg.arg}")

                    # fill defaults in last positional arguments
                    val_args_len = len(signature.posonlyargs) + len(signature.args)
                    for i, default in enumerate(signature.defaults, val_args_len - len(signature.defaults)):
                        parts[i] = f"{parts[i]}={ast.unparse(default)}"

                    # key-value defaults
                    offset = val_args_len + bool(signature.vararg or signature.kwonlyargs) # add one space for "*"" or "*abc"
                    for i, default in enumerate(signature.kw_defaults):
                        if default is not None:
                            parts[offset + i] = f"{parts[offset + i]}={ast.unparse(default)}"

                    args = ", ".join(parts)

                    name = node.name
                    break

            if name is None or args is None:
                raise CompilationError(f"{self.filename}:{codeline}:{0}: Wrong def statement: [this exception impossible]")

            # compile body
            body = self._compile_block(codeline + 1, indent, new_block = True)

            # compile following code

            follow = self._compile_block(body.next, indent)

            # create expression

            if line.startswith("async "):
                exp = f"({name} := (lambda {args}: (({body.code}) for __t{self.seed} in '_' if True or await fun()).__anext__())) and False"
            else:
                exp = f"({name} := (lambda {args}: ({body.code}))) and False"

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        else:
            # not keyword

            exp = self.sc.compile(line)

            follow = self._compile_block(codeline + 1, indent)

            if follow.code is not None:
                if exp is None:
                    exp = follow.code
                else:
                    exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)

