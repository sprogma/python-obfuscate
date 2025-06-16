# one compiler supporting:

- [X] Expressions
    - [X] simple expressions (already in one line)
- [ ] Assign operator
    - [X] base assign operator (x = expr)
    - [X] assign operator chains (x = y = expr)
    - [X] tuple assign operators (x, y = expr)
    - [ ] nested tuple assign operators (x, (y, z) = expr)
    - [ ] starred assign operators (x, *y, z = expr)
    - [X] index assign (x[5] = expr)
    - [X] attribute assign (x.y = expr)
    - [X] tuple attribute assign (x.y, x.z = expr)
    - [X] tuple index assign (a[0], a[3] = expr)
    - [X] opertation assign (a += 1)
- [X] Branches
    - [X] if
    - [X] else
    - [X] elif
- [ ] Loops
    - [X] base for loop
    - [X] while loop
    - [X] tuple for loop     (for x, y in ...)
    ### hard to implement
    - [ ] continue
    - [ ] break
    - [ ] else after loops
- [ ] Import
    - [X] import
    - [X] from import
    - [ ] from import *
- [ ] Decorators
    - [ ] function simple
    - [ ] function with parameters
    - [ ] class simple
    - [ ] class with parameters
- [ ] Classes
    - [X] only functions
    - [X] inheritance
    - [ ] class in class
    - [ ] constants in class body
    - [ ] code in class body
    - [ ] zero argument super()
- [ ] Functions
    - [X] simple no arguments
    - [X] simple arguments (only vars)
    - [X] special arguments ("/", "*", "**")
    - [X] default values
    - [X] return
    - [ ] try / except
    - [ ] yield
- [ ] Async
    - [X] keyword and simple logic
    - [X] return
    - [ ] try / except
- [ ] Keywords
    - [X] import
    - [X] from import
    - [X] if
    - [X] elif
    - [X] else
    - [X] for
    - [X] while
    - [X] pass
    - [X] def
    - [X] class
    - [X] return
    - [X] lambda
    - [X] await
    - [ ] assert
    ### hard to implement
    - [ ] yield
    - [ ] global
    - [ ] nonlocal
    - [X] raise
    - [ ] try
    - [ ] continue
    - [ ] break
    - [X] async
- [ ] Multiple files

## self compiling status:
not yet.
### need to implement
- multiple files

