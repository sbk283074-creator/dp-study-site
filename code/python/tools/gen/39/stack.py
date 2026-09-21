import dis

def add(a, b):
    return a + b

def add_both(a, b):
    return a + b, a - b

print("co_stacksize of add      :", add.__code__.co_stacksize)
print("co_stacksize of add_both :", add_both.__code__.co_stacksize)

print("\nadd:")
dis.dis(add)
print("\nadd_both:")
dis.dis(add_both)
