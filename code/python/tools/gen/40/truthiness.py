print("__bool__ is consulted first; __len__ is the fallback")


class ByBool:
    def __bool__(self):
        return False


class ByLen:
    def __len__(self):
        return 0


class Both:
    def __bool__(self):
        return True

    def __len__(self):
        return 0


print("  bool(ByBool()) ->", bool(ByBool()))
print("  bool(ByLen())  ->", bool(ByLen()))
print("  bool(Both())   ->", bool(Both()), " <- __bool__ wins over len == 0")
print()

print("the falsy family:")
for v in (False, None, 0, 0.0, 0j, "", b"", [], (), {}, set(), frozenset()):
    print(f"  {type(v).__name__:9s} {v!r:13s} -> {bool(v)}")
print()

print("and the truthy values that surprise people:")
for v in (0.1, -1, "0", "False", [0], (0,), {0: 0}, float("nan")):
    print(f"  {type(v).__name__:9s} {v!r:13s} -> {bool(v)}")
print()

print("the trap: 0 and None are both falsy, and they mean different things")
for v in (0, None, 3):
    print(f"  v = {str(v):5s}  bool(v) = {str(bool(v)):5s}  v is None = {v is None}")
print()
print("  `if not v:` collapses 0 and None into one branch.")
print("  `if v is None:` keeps them apart. Pick one deliberately, because")
print("  'the count is zero' and 'there is no count' are different facts.")
