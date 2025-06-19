# One compiler:

compiles Python code into one line. (In Python syntax, it's an expression)
doesn't use any eval/exec - so it's really a compiler, not an interpreter.

## Python constructions supported:
see support.md

## Example

examples/example.py
```python
class Bank:
    def __init__(self, money, percent):
        self.percent = percent
        self.start_money = money
        self.money = money
        self.multiplier = 1.0 + percent / 100.0

    def add_year(self):
        self.money *= self.multiplier

    def add_years(self, n):
        for year in range(n):
            self.add_year()

    def get_profit(self):
        return self.money - self.start_money

    def __repr__(self):
        return f"Bank(${self.money:,}, {self.percent}%)"


bank = Bank(100_000, 7)
bank.add_years(17)
print(bank, bank.get_profit())
```

resulting in

examples/example_res.py
```python
(__ONE_lib_importlib := __import__('importlib')) and False or ((__ONE_lib_contextlib := __import__('contextlib')) and False or ((__ONE_sync_try := type('__ONE_cls_sync_try', (__ONE_lib_contextlib.ContextDecorator,), {'__enter__': lambda self: self, '__exit__': lambda self, *exc: (bool(print('Error!' + repr(exc))) and False if exc[0] != __ONE_cls_ReturnObject else bool(setattr(exc[1].fn, '__ONE_var_retval', exc[1].val)) or True) if exc != (None,) * 3 else False})) and False or ((__ONE_cls_ReturnObject := type('__ONE_cls_ReturnObject', (BaseException,), {'__init__': lambda self, function, value: [setattr(self, 'fn', function), setattr(self, 'val', value), None][-1]})) and False or ((__ONE_sync_i_op := (lambda a, b, im, m, rm: result if callable((mim := getattr(a, im, None))) and (result := mim(b)) is not NotImplemented else result if callable((mm := getattr(a, m, None))) and (result := mm(b)) is not NotImplemented else result if callable((mrm := getattr(b, rm, None))) and (result := mrm(a)) is not NotImplemented else print(f'ERROR: CANNOT ADD {a} AND {b} ({type(a)}, {type(b)})') or NotImplemented)) and False or ((Bank := type('Bank', (), {'__init__': lambda *args, **kvargs: [(__ONE_var_realfunction := __ONE_sync_try()(lambda self, money, percent: ((__t1751211561767 := percent) and False or (setattr(self, 'percent', __t1751211561767) and False)) or (((__t1751211561767 := money) and False or (setattr(self, 'start_money', __t1751211561767) and False)) or (((__t1751211561767 := money) and False or (setattr(self, 'money', __t1751211561767) and False)) or ((__t1751211561767 := (1.0 + percent / 100.0)) and False or (setattr(self, 'multiplier', __t1751211561767) and False)))))), __ONE_var_realfunction(*args, **kvargs), getattr(__ONE_var_realfunction, '__ONE_var_retval', None)][-1], 'add_year': lambda *args, **kvargs: [(__ONE_var_realfunction := __ONE_sync_try()(lambda self: [(__t1751211561767 := type(self.money)), setattr(self, 'money', __t1751211561767_r) and False if (__t1751211561767_r := __ONE_sync_i_op(self.money, self.multiplier, '__imul__', '__mul__', '__rmul__')) is not NotImplemented else False].__len__() == 0)), __ONE_var_realfunction(*args, **kvargs), getattr(__ONE_var_realfunction, '__ONE_var_retval', None)][-1], 'add_years': lambda *args, **kvargs: [(__ONE_var_realfunction := __ONE_sync_try()(lambda self, n: any((self.add_year() and False for year in range(n))))), __ONE_var_realfunction(*args, **kvargs), getattr(__ONE_var_realfunction, '__ONE_var_retval', None)][-1], 'get_profit': lambda *args, **kvargs: [(__ONE_var_realfunction := __ONE_sync_try()(lambda self: (__ONE_trash for __ONE_trash in '_').throw(__ONE_cls_ReturnObject(__ONE_var_realfunction, self.money - self.start_money)) and False)), __ONE_var_realfunction(*args, **kvargs), getattr(__ONE_var_realfunction, '__ONE_var_retval', None)][-1], '__repr__': lambda *args, **kvargs: [(__ONE_var_realfunction := __ONE_sync_try()(lambda self: (__ONE_trash for __ONE_trash in '_').throw(__ONE_cls_ReturnObject(__ONE_var_realfunction, f'Bank(${self.money:,}, {self.percent}%)')) and False)), __ONE_var_realfunction(*args, **kvargs), getattr(__ONE_var_realfunction, '__ONE_var_retval', None)][-1]})) and False or (((__t1751211561767 := Bank(100000, 7)) and False or ((bank := __t1751211561767) and False)) or (bank.add_years(17) and False or (print(bank, bank.get_profit()) and False or ((__t1751211561767 := type('__ONE_trash', (dict,), {'__getattribute__': lambda s, x: s[x]})(globals().copy())) and False or ((example := __t1751211561767) and False))))))))))
```

## Usage

To reproduce this example:
```powershell
./run.ps1 ./examples/example.py ./examples/example_res.py
# or ./run.ps1 -Files ./examples/example.py -Destination ./examples/example_res.py
```
or with python:
```bash
python3 ./one.py ./examples/example.py -o ./examples/example_res.py
# or "py" for windows
```
or with one liner :)   (works on linux, on windows code is too big to pass into program arguments)
```bash
python3 -c "$(cat examples/self.py)" examples/example.py examples/example_res.py
```

Documentation for run.ps1:
```powershell
Get-Help -Full ./run.ps1
```

Documentation for one.py:
```bash
python3 ./one.py --help
```

## Notes
To get better results you can pass result into minifier, for example.