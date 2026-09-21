import ast, dis, sys
print("python", sys.version.split()[0])
print("--- ast.dump(ast.parse('total = price * 1.2 + 5'))")
print(ast.dump(ast.parse("total = price * 1.2 + 5"), indent=2)[:400])
print("--- constant folding")
c = compile("x = 1 + 2 * 3", "<s>", "exec")
print("co_consts:", c.co_consts)
print("--- dis of a simple function")
def add(a, b):
    return a + b
dis.dis(add)
print("--- dis of a loop")
def total(xs):
    s = 0
    for x in xs:
        s += x
    return s
dis.dis(total)
