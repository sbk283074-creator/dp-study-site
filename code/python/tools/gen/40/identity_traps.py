print("identity is not value -- three ways they diverge")
print()

print("1. CPython caches small integers, so equal ones are the same object")
print("   int('256') is int('256') ->", int("256") is int("256"))
print("   int('257') is int('257') ->", int("257") is int("257"))
print("   (the cache covers -5..256, and that range is an implementation detail)")
print()

print("2. equal constants in ONE code object are folded into one object")
x = 257
y = 257
print("   257 and 257, reached through two names in one scope ->", x is y)
print()

print("3. strings are only interned when they look like identifiers")
same = "hello"
built = "".join(["hel", "lo"])
print("   'hello' == 'hello' ->", same == built)
print("   'hello' is 'hello' ->", same is built)
print()

print("conclusion: `is` answers a question about identity, and identity is not")
print("something a program may rely on for numbers or for text.")
