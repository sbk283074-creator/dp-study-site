"""Chapter 10 -- what `from module import *` actually brings.

Two modules with identical contents, one of which declares `__all__`. The
count is of names the star import delivers and of names it delivers that the
module never meant to export. The result is that the imported name `os` is
the leak, and `__all__` is what stops it.
"""

import os
import sys
import tempfile

BODY = (
    "VALUE = 1\n"
    "_helper = 2\n"
    "import os\n"
    "def public():\n"
    "    return 1\n"
    "def _private():\n"
    "    return 2\n"
)

directory = tempfile.mkdtemp()
PLAIN = "plainmod"
DECLARED = "declaredmod"

with open(os.path.join(directory, PLAIN + ".py"), "w", encoding="utf-8") as handle:
    handle.write(BODY)

with open(os.path.join(directory, DECLARED + ".py"), "w", encoding="utf-8") as handle:
    handle.write("__all__ = ['VALUE', 'public']\n" + BODY)

sys.path.insert(0, directory)


def defined_names(module_name):
    """Every non-dunder name in the module's namespace."""
    namespace = {}
    exec(f"import {module_name}", namespace)
    module = namespace[module_name]
    return sorted(name for name in vars(module) if not name.startswith("__"))


def star_names(module_name):
    """Every name a star import puts into the importing namespace."""
    namespace = {}
    exec(f"from {module_name} import *", namespace)
    return sorted(name for name in namespace if not name.startswith("__"))


EXPECTED = {"VALUE", "public"}

print(f"{'module':<12}{'names in it':>12}{'delivered':>11}{'unexpected':>12}")
print("-" * 47)
for label, module_name in (("plain", PLAIN), ("declared", DECLARED)):
    defined = defined_names(module_name)
    delivered = star_names(module_name)
    unexpected = [name for name in delivered if name not in EXPECTED]
    print(f"{label:<12}{len(defined):>12}{len(delivered):>11}{len(unexpected):>12}")

print()
print(f"The plain module is delivered as: {', '.join(star_names(PLAIN))}")
print(f"The declared module is delivered as: {', '.join(star_names(DECLARED))}")
print()
print("Both modules hold the same five names. The star import takes three of")
print("them from the first and two from the second, so it drops two names from")
print("the plain module and three from the declared one. What the plain module")
print("drops is the two names that begin with an underscore -- a leading")
print("underscore is the convention that says a name is not for other modules,")
print("and the star import is the one place the convention is enforced.")
print()
print("The name to look at is `os`. It is in the plain module's namespace")
print("because the module imported it, and the star import hands it to whoever")
print("wrote the import line. So a module that imports `os` for its own use")
print("silently gives `os` to every file that star-imports it, and a name in")
print("the importing file that meant something else is quietly replaced.")
print()
print("That is what `__all__` is for, and it is not a documentation feature:")
print("it is the list of names the star import is allowed to deliver, and")
print("without it the answer is 'every name that does not start with an")
print("underscore', which includes every module the module imports.")
