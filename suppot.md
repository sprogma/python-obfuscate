# one compiler supporting:

- [X] Expressions
    - [X] simple expressions (already in one line)
- [ ] Assign operator
    - [X] base assign operator (x = expr)
    - [X] assign operator chains (x = y = expr)
    - [ ] tuple assign operators (x, y = expr)
    - [ ] starred assign operators (x, *y, z = expr)
    - [X] index assign (x[5] = expr)
    - [ ] attribute assign (x.y = expr)
- [X] Branches
    - [X] if
    - [X] else
    - [X] elif
- [ ] Loops
    - [X] base for loop
    - [ ] while loop
    - [X] tuple for loop     (for x, y in ...)
    ### hard to implement
    - [ ] continue
    - [ ] break
    - [ ] else after loops
- [ ] Import
    - [X] import
    - [ ] from import
    - [ ] from import *
- [ ] Decorators
    - [ ] function simple
    - [ ] function with parameters
    - [ ] class simple
    - [ ] class with parameters
- [ ] Classes
    - [ ] function simple
    - [ ] function with parameters
    - [ ] class simple
    - [ ] class with parameters
- [ ] Async
    - [X] keyword and simple logic
    - [ ] return
    - [ ] try / except
- [ ] Keywords
    - [X] import
    - [ ] from import
    - [X] if
    - [X] elif
    - [X] else
    - [ ] for
    - [ ] while
    - [X] def
    - [ ] class
    - [X] return
    - [X] lambda
    - [X] await
    - [ ] assert
    ### hard to implement
    - [ ] yield
    - [ ] global
    - [ ] nonlocal
    - [ ] raise
    - [ ] try
    - [ ] continue
    - [ ] break
    - [X] async
- [ ] Multiple files

## self compiling status:
not yet.
### need to implement
- from import
- classes (partly)
- multiple files

