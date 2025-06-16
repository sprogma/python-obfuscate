from common import jsd
import code_provider
from exceptions import CompilationError
from statement_compiler import StatementCompiler
import re
import tokenize
import ast
import io
import random
import time

"""
    "expression" base output must be False-equal.
    becouse we will join expressions using "or"
    operator, (arrays and tuples cause additional
    space consumption and may be them are slower)
"""

class BlockCompiler(code_provider.CodeProvider):
    def __init__(self, statement_compiler):
        self.sc: StatementCompiler = statement_compiler

        self.filename: str = ""
        self.code: list[str] = []

    def build(self, filename: str, code: str):
        self.filename = filename
        self.code = code.split('\n')

        return self.compile_block(0, 0)

    def custom_imports(self):
        return super().custom_imports() + self.sc.custom_imports() + [
            "contextlib",
            "importlib"
        ]

    def custom_header(self):
        return super().custom_header() + self.sc.custom_header() + [
            # ReturnObject class, used to return from lambdas using exceptions
            '''
                __ONE_cls_ReturnObject := type("__ONE_cls_ReturnObject", (BaseException,),
                {
                    "__init__": lambda self, function, value: [setattr(self, "fn", function), setattr(self, "val", value), None][-1]
                })
            ''',
            # TryExcept decorator, no exec usage.
            # If catch __ONE_cls_ReturnObject exception sets function.__ONE_var_retval on it's value
            '''
                __ONE_sync_try := type("__ONE_cls_sync_try", (__ONE_lib_contextlib.ContextDecorator,),
                {
                    "__enter__": (lambda self: self),
                    "__exit__": (lambda self, *exc:
                    (
                        (
                            (
                                bool(print("Error!"+repr(exc))) and False
                            )
                            if exc[0] != __ONE_cls_ReturnObject else
                            (
                                bool(setattr(exc[1].fn, "__ONE_var_retval", exc[1].val)) or True
                            )
                        )
                        if exc != (None,)*3
                        else False
                    ))
                })
            '''
        ]

    def unpack_string(self, full_line: str) -> tuple[int, str]:
        indent = len(full_line) - len(full_line.lstrip(" "))
        line = full_line[indent:]
        return indent, line

    def compile_block(self, codeline: int, baseindent: int, *, new_block = False, class_body = False) -> jsd:
        # print(f"call _compile_block({codeline}, {baseindent}, {new_block})")
        # __import__("time").sleep(0.5)

        if codeline >= len(self.code):
            if class_body:
                return jsd(next=codeline, dict={})
            else:
                return jsd(next=codeline, code=None)

        indent, line = self.unpack_string(self.code[codeline])
        # print(f"find indent: {indent} <{line}>")

        if line == "":
            ... # skip this line, it's indent don't mean anything
            return self.compile_block(codeline + 1, baseindent, new_block = new_block, class_body = class_body)
        elif new_block:
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
                if class_body:
                    return jsd(next=codeline, dict={})
                else:
                    return jsd(next=codeline, code=None)

        # check content
        if line.startswith("if "):

            branches = []

            exp = line[:line.rfind(":")].removeprefix("if").strip()

            if_true = self.compile_block(codeline + 1, indent, new_block = True)
            end_line: int = if_true.next

            branches.append(jsd(exp=exp, code=if_true.code))

            end_indent = None
            end_code = None

            while True:
                if end_line >= len(self.code):
                    break
                end_indent, end_code = self.unpack_string(self.code[end_line])
                if end_indent != indent or not end_code.startswith("elif"):
                    break

                exp = end_code[:end_code.rfind(":")].removeprefix("elif").strip()

                elif_true = self.compile_block(end_line + 1, indent, new_block = True)

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
                    end_indent, end_code = self.unpack_string(self.code[end_line])
                    if end_code.startswith("else"):
                        else_res = self.compile_block(end_line + 1, indent, new_block = True)
                        else_code = else_res.code
                        return_line = else_res.next

            following_code = None

            # compile following code
            follow = self.compile_block(return_line, indent)
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
            body = self.compile_block(codeline + 1, indent, new_block = True)

            # compile following code

            follow = self.compile_block(body.next, indent)

            # create expression

            exp = f"any((({body.code}) for {vars_src} in ({iter_src})))"

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.startswith("while "):

            exp = line[:line.rfind(":")].removeprefix("while")

            # compile body
            body = self.compile_block(codeline + 1, indent, new_block = True)

            # compile following code

            follow = self.compile_block(body.next, indent)

            # create expression

            exp = f"any((({body.code}) for __ONE_trash in iter(lambda: ({exp}), False)))"

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
                    raise CompilationError(f"{self.filename}:{codeline}:{0}: Wrong import ... statement.")

            # generate expression
            exp = ""

            for mod in data:
                if exp == "":
                    exp = f"(({mod.name} := __ONE_lib_importlib.import_module({repr(mod.module)})) and False)"
                else:
                    exp = f"({exp}) or (({mod.name} := __ONE_lib_importlib.import_module({repr(mod.module)})) and False)"

            follow = self.compile_block(codeline + 1, indent)

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.startswith("from "):
            base = line[:max(line.find(" import "), line.find(" import*"))].removeprefix("from").strip()
            elements = line[max(line.find(" import "), line.find(" import*")):].lstrip().removeprefix("import").split(",")
            data = []
            for e in elements:
                e = e.split()
                if len(e) == 3 and "as" in e:
                    data.append(jsd(element=e[0], name=e[2]))
                elif len(e) == 1:
                    data.append(jsd(element=e[0], name=e[0]))
                else:
                    raise CompilationError(f"{self.filename}:{codeline}:{0}: Wrong from ... import ... statement.")

            exp = f"(__ONE_import := __ONE_lib_importlib.import_module({repr(base)})) and False"
            for e in data:
                exp = f"({exp}) or (({e.name} := __ONE_import.{e.element}) and False)"

            follow = self.compile_block(codeline + 1, indent)

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
            body = self.compile_block(codeline + 1, indent, new_block = True)

            # compile following code

            follow = self.compile_block(body.next, indent, class_body = class_body)

            # create expression
            # use decorator to catch exceptions generated by returns inside function
            if line.startswith("async "):
                fn =   f"""
                            lambda *args, **kvargs : (
                                [
                                    __ONE_var_realfunction := __ONE_sync_try()(lambda {args}: (({body.code}) for __ONE_trash in '_' if True or await fun()).__anext__())),
                                    __ONE_var_realfunction(*args, **kvargs),
                                    getattr(__ONE_var_realfunction, "__ONE_var_retval", None)
                                ][-1]
                            )
                        """
            else:
                fn =   f"""
                            lambda *args, **kvargs : (
                                [
                                    __ONE_var_realfunction := __ONE_sync_try()(lambda {args}: ({body.code})),
                                    __ONE_var_realfunction(*args, **kvargs),
                                    getattr(__ONE_var_realfunction, "__ONE_var_retval", None)
                                ][-1]
                            )
                        """
            if class_body:
                # follow will override function if there is same name
                return jsd(next = follow.next, dict = {name : fn} | follow.dict)
            else:
                exp = f"({name} := {fn}) and False"
                if follow.code is not None:
                    exp = f"({exp}) or ({follow.code})"

                return jsd(next=follow.next, code=exp)
        elif line.startswith("return ") or line == "return":

            val = line.removeprefix("return")

            if val.strip() == "":
                val = "None"

            # compile follow?
            follow = self.compile_block(codeline + 1, indent)

            exp = f"(__ONE_trash for __ONE_trash in '_').throw(__ONE_cls_ReturnObject(__ONE_var_realfunction, ({val}))) and False"

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.startswith("class "):
            # parse arguments
            fake_code = f"{line}..."

            tree = ast.parse(fake_code)

            name = bases = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    name = node.name
                    bases = (*map(ast.unparse, node.bases),)

            if name is None or bases is None:
                raise CompilationError(f"{self.filename}:{codeline}:{0}: Wrong class statement: [this exception impossible]")

            # compile body: collect all functions and other code

            body = self.compile_block(codeline + 1, indent, new_block = True, class_body = True)

            cls_dict = "{" + ",".join(map(lambda x: f"{repr(x[0])}:({x[1]})", body.dict.items())) + "}"
            cls_bases = "(" + "".join(map(lambda x: f"{x},", bases)) + ")"

            exp = f'({name} := type({repr(name)}, {cls_bases}, {cls_dict})) and False'

            follow = self.compile_block(body.next, indent)

            if follow.code is not None:
                exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.startswith("raise "):
            value = line.removeprefix("raise")
            exp = f"(__ONE_trash for __ONE_trash in '_').throw({value}) and False"

            follow = self.compile_block(codeline + 1, indent)

            if follow.code is not None:
                if exp is None:
                    exp = follow.code
                else:
                    exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
        elif line.strip() == "pass":

            follow = self.compile_block(codeline + 1, indent, class_body = class_body)

            if class_body:
                return jsd(next=follow.next, dict=follow.dict)
            else:
                if follow.code is not None:
                    exp = f"{follow.code}"
                else:
                    exp = "False"
                return jsd(next=follow.next, code=exp)
        else:
            # not keyword

            exp = self.sc.compile(line)

            follow = self.compile_block(codeline + 1, indent)

            if follow.code is not None:
                if exp is None:
                    exp = follow.code
                else:
                    exp = f"({exp}) or ({follow.code})"

            return jsd(next=follow.next, code=exp)
