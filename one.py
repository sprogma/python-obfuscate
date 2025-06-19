"""
    Main compiler file
"""
import common
import preprocessor
import statement_compiler
import block_compiler
import compiler
import combine
import sys


if __name__ == "__main__":
    args = sys.argv[1:]
    dest = args[args.index("-o") + 1] if "-o" in args else None
    files = [*map(lambda x: x[1], filter(lambda i: i[1] not in ("-o", "-NoPrint") and (i[0] == 0 or args[i[0] - 1] != "-o"), enumerate(args)))]
    debug_print = "-NoPrint" not in args

    if debug_print:
        print("Compile:")
        print(f"    destination: {dest}")
        print(f"    files:       {'; '.join(files)}")

    if len(files) == 0:
        print("No input files.")
        exit(1)

    if debug_print:
        print("Compilation started...")

    # Combine files
    if debug_print:
        print(f"Start combine...")

    c = combine.Combiner(".", files)
    c.combine()
    code = c.get_result()

    if debug_print:
        print("Compile combined result...")

    p = preprocessor.Preprocessor()
    b = block_compiler.BlockCompiler(statement_compiler=statement_compiler.StatementCompiler())

    c = compiler.Compiler(
        preprocessor=p,
        block_compiler=b
    )

    code = c.compile(code)

    if code is None:
        print("Compilation returned null")
    else:
        if dest is None:
            print(code)
        else:
            with open(dest, "w") as file:
                file.write(code)

    if debug_print:
        print("Compilation end.")
        print(f"Writed into {dest}.")
