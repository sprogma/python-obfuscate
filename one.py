"""
    Main compiler file
"""
import common
import preprocessor
import statement_compiler
import compiler
import sys



if __name__ == "__main__":
    args = sys.argv[1:]
    dest = args[args.index("-o") + 1] if "-o" in args else "./res.py"
    files = [*map(lambda x: x[1], filter(lambda i: i[1] != "-o" and (i[0] == 0 or args[i[0] - 1] != "-o"), enumerate(args)))]
    print("Compile:")
    print(f"    destination: {dest}")
    print(f"    files:       {'; '.join(files)}")

    if len(files) == 0:
        print("No input files.")
        exit(1)

    if len(files) > 1:
        print("Not implemented compilation of multiple files")
        exit(1)

    print("Compilation started...")

    for name in files:
        print(f"Compiling {name}...")
        with open(name, "r") as file:
            content = file.read()

        p = preprocessor.Preprocessor()
        sc = statement_compiler.StatementCompiler()

        c = compiler.Compiler(
            preprocessor=p,
            statement_compiler=sc
        )

        code = c.compile(content)

        with open(dest, "w") as file:
            file.write(code)

    print("Compilation end.")
