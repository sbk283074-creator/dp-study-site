"""Chapter 10 -- a module's body runs once, and the count proves it.

A module written to a temporary directory, imported a hundred times, with the
body counting its own executions. The count is of body executions, of entries
in `sys.modules`, and of reloads that handed back the same object. Together
they explain why import cost is paid once per process -- and why a reload does
not repair a name that was already bound.
"""

import importlib
import os
import sys
import tempfile

IMPORTS = 100
RELOADS = 5
MODULE = "counter_module"

directory = tempfile.mkdtemp()
with open(os.path.join(directory, MODULE + ".py"), "w", encoding="utf-8") as handle:
    handle.write(
        "import sys\n"
        "sys.BODY_RUNS = getattr(sys, 'BODY_RUNS', 0) + 1\n"
        "VALUE = 40 + sys.BODY_RUNS\n"
    )

sys.path.insert(0, directory)
before = len(sys.modules)

for _ in range(IMPORTS):
    module = importlib.import_module(MODULE)
after_imports = sys.BODY_RUNS

first_object = module
# What `from counter_module import VALUE` would have bound, right here.
bound_earlier = module.VALUE

reused = 0
for _ in range(RELOADS):
    module = importlib.reload(module)
    if module is first_object:
        reused += 1
after_reloads = sys.BODY_RUNS
after = len(sys.modules)

print(f"{IMPORTS} import statements and {RELOADS} reloads for one module on disk")
print()
print(f"{'what is counted':<36}{'count':>8}")
print("-" * 44)
print(f"{'import statements executed':<36}{IMPORTS:>8}")
print(f"{'times the body ran for them':<36}{after_imports:>8}")
print(f"{'times the body ran after reloads':<36}{after_reloads:>8}")
print(f"{'reloads that reused the module object':<36}{reused:>8}")
print(f"{'new entries in sys.modules':<36}{after - before:>8}")
print(f"{'the value the module now holds':<36}{module.VALUE:>8}")
print(f"{'the value a from-import bound':<36}{bound_earlier:>8}")

print()
print(f"The body ran {after_imports} time for {IMPORTS} import statements, because the second")
print("import and every one after it found the module already in `sys.modules`")
print("and returned the object it found there. That is the whole of the import")
print("cache, and it explains the two things people find surprising about it.")
print()
print("A module is a single object shared by everybody who imports it, so a")
print("module-level list that one part of a program appends to is visible to")
print("every other part. And the work at the top of a module -- reading a file,")
print("building a table, opening a connection -- happens once per process,")
print("which is either a saving you are relying on or a cost you forgot about.")
print()
print(f"The reload rows are the other half, and they are the two rows that")
print(f"people get backwards. Reloading runs the body again -- {RELOADS} reloads and")
print(f"the body ran {after_reloads} times in total -- but it reuses the module object")
print(f"rather than replacing it, all {reused} times. What changes is the namespace")
print(f"inside that object: the value it holds moved from {bound_earlier} to {module.VALUE}.")
print()
print(f"A name bound earlier by `from {MODULE} import VALUE` still holds")
print(f"{bound_earlier}, because the from-import copied the value at the moment it")
print("ran. That is the stale name a reload does not repair, and it is why")
print("reloading is not a fix for a module that changed under a running")
print("program.")
