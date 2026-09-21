import ast

SOURCE = "total = price * 1.2 + 5"

print("1. the text you typed")
print("  ", SOURCE)

print("\n2. the AST the parser produced")
tree = ast.parse(SOURCE)
print(ast.dump(tree, indent=2))

print("\n3. the code object the compiler produced")
code = compile(SOURCE, "<demo>", "exec")
print("   co_consts :", code.co_consts)
print("   co_names  :", code.co_names)
print("   co_stacksize:", code.co_stacksize)
