import sys

a = []
print("a = []      -> getrefcount:", sys.getrefcount(a))
b = a
print("b = a       -> getrefcount:", sys.getrefcount(a))
c = [a, a]
print("c = [a, a]  -> getrefcount:", sys.getrefcount(a))
del b
print("del b       -> getrefcount:", sys.getrefcount(a))
c.clear()
print("c.clear()   -> getrefcount:", sys.getrefcount(a))
print()
print("Every number above is one higher than the count you can see by")
print("reading the code, because passing `a` to getrefcount() creates a")
print("reference for the duration of the call.")
print()
print("`del b` is not what freed the list `b` pointed at. It dropped one")
print("reference; the object goes away when the last one drops.")
