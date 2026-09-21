class Counter:
    step = 1                      # lives on the class

    def __init__(self):
        self.value = 0            # lives on the instance

    def bump(self):
        self.value += self.step


c = Counter()
d = Counter()

print("where attributes live")
print("  c.__dict__            ->", c.__dict__)
print("  'step' in Counter.__dict__ ->", "step" in Counter.__dict__)
print("  'bump' in Counter.__dict__ ->", "bump" in Counter.__dict__)
print("  'bump' in c.__dict__       ->", "bump" in c.__dict__)
print()

print("reading c.step finds it on the class:")
print("  c.step ->", c.step)
print()

c.step = 10
print("after `c.step = 10` -- this creates an INSTANCE attribute:")
print("  c.__dict__     ->", c.__dict__)
print("  c.step         ->", c.step)
print("  d.step         ->", d.step, " (untouched)")
print("  Counter.step   ->", Counter.step, " (untouched)")
print()

print("the lookup order is: instance dict, then type, then the MRO")
print("  c.bump() ->", end=" ")
c.bump()
print(c.value)
print("  ...and `bump` was found on the type, not on c. That is why a bound")
print("  method knows which instance to pass as `self`.")
