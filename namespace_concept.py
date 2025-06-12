import inspect
import ast
import textwrap
from types import FunctionType

class _Return(Exception):
    """«Исключение»-носитель результата return."""
    def __init__(self, value):
        self.value = value

def make_sharedable(func, shared_dict_name="_SHARED"):
    src = textwrap.dedent(inspect.getsource(func))
    mod = ast.parse(src)
    func_def = mod.body[0]  # предполагаем, что это FunctionDef

    # 1) Подмена всех `return X` → `raise _Return(X)`
    class RetRewriter(ast.NodeTransformer):
        def visit_Return(self, node: ast.Return):
            val = node.value or ast.Constant(None)
            return ast.Raise(
                exc=ast.Call(
                    func=ast.Name(id="_Return", ctx=ast.Load()),
                    args=[val],
                    keywords=[]
                ),
                cause=None
            )
    func_def = RetRewriter().visit(func_def)
    ast.fix_missing_locations(func_def)

    # 2) Собираем новый список команд внутри функции
    new_body = []

    # 2.1) Загрузить общие локалы
    new_body.append(
        ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Call(func=ast.Name("locals", ast.Load()),
                                   args=[], keywords=[]),
                    attr="update", ctx=ast.Load()),
                args=[ast.Name(id=shared_dict_name, ctx=ast.Load())],
                keywords=[]
            )
        )
    )
    # 2.2) Инициализировать __ret
    new_body.append(
        ast.Assign(
            targets=[ast.Name(id="__ret", ctx=ast.Store())],
            value=ast.Constant(None)
        )
    )

    # 2.3) Основной try/except/finally
    try_body = func_def.body[:]  # оригинальный (с подменённым return)
    handlers = [
        # перехват «_return» и сохранение результата
        ast.ExceptHandler(
            type=ast.Name(id="_Return", ctx=ast.Load()),
            name="e",
            body=[
                ast.Assign(
                    targets=[ast.Name(id="__ret", ctx=ast.Store())],
                    value=ast.Attribute(
                        value=ast.Name(id="e", ctx=ast.Load()),
                        attr="value", ctx=ast.Load()
                    )
                )
            ]
        ),
        # перехват всего остального — просто перекидываем,
        # но важно, что finally всё равно выполнится
        ast.ExceptHandler(
            type=ast.Name(id="BaseException", ctx=ast.Load()),
            name=None,
            body=[
                ast.Raise(exc=None, cause=None)
            ]
        )
    ]
    # finally – синхронизация shared
    final_body = [
        # _SHARED.clear()
        ast.Expr(ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=shared_dict_name, ctx=ast.Load()),
                attr="clear", ctx=ast.Load()),
            args=[], keywords=[]
        )),
        # _SHARED.update(locals())
        ast.Expr(ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=shared_dict_name, ctx=ast.Load()),
                attr="update", ctx=ast.Load()),
            args=[ast.Call(func=ast.Name("locals", ast.Load()), args=[], keywords=[])],
            keywords=[]
        ))
    ]
    new_body.append(
        ast.Try(body=try_body, handlers=handlers,
                orelse=[], finalbody=final_body)
    )

    # 2.4) Наконец — return __ret
    new_body.append(
        ast.Return(value=ast.Name(id="__ret", ctx=ast.Load()))
    )

    # Подменяем тело функции
    func_def.body = new_body
    ast.fix_missing_locations(func_def)

    # 3) Собираем новый модуль и компилируем
    new_mod = ast.Module(body=[func_def], type_ignores=[])
    code = compile(new_mod, filename=func.__code__.co_filename, mode="exec")

    # 4) Готовим namespace для exec
    ns = {}
    ns.update(func.__globals__)
    ns["_Return"] = _Return
    if shared_dict_name not in ns:
        ns[shared_dict_name] = {}

    # 5) Выполняем и возвращаем новую версию функции
    exec(code, ns)
    return ns[func_def.name]


# ===== Проверка =====
if __name__ == "__main__":
    def f():
        a += 1
        if a == 2:
            raise ValueError("boom!")
        if a < 5:
            return a
        return a * 10

    f2 = make_sharedable(f, "_SHARED")
    f2.__globals__['_SHARED']['a'] = 0

    print(f2())  # 1
    try:
        print(f2())  # здесь a==2 → будет ValueError
    except ValueError as e:
        print("caught:", e)

    # Даже после исключения в f2, _SHARED['a'] уже = 2
    print("after exception, a =", f2.__globals__['_SHARED']['a'])

    # Дальше продолжает нормально работать
    print(f2())  # 3
    print(f2())  # 4
    print(f2())  # 5 → return 5*10 = 50
    print("final shared:", f2.__globals__['_SHARED'])