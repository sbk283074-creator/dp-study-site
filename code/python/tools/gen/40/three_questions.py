a = [1, 2, 3]
b = [1, 2, 3]
c = a

print("three questions you can ask about any value")
print("  identity : a is c      ->", a is c)
print("  identity : a is b      ->", a is b)
print("  type     : type(a) is type(b) ->", type(a) is type(b))
print("  value    : a == b      ->", a == b)
print()
print("a and b are equal values that are different objects.")
print("a and c are the same object, so they cannot help being equal.")
