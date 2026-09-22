"""Chapter 55 -- the locator, measured by what the signature says.

A report that asks a global registry for what it needs, and the same
report taking the same three things as arguments. The count is of the
dependencies the signature names, and of the callers one change reaches.
"""

import inspect

NEEDS = ["store", "clock", "mailer"]

CALLERS = ["the nightly job", "the webhook handler", "the admin button",
           "the report page"]


class Locator:
    """The global. `get` answers with whatever is registered, and the
    caller learns nothing from the answer."""

    def __init__(self):
        self._factories = {}
        self._overrides = {}

    def register(self, name, factory):
        self._factories[name] = factory

    def override(self, name, value):
        self._overrides[name] = value

    def get(self, name):
        if name in self._overrides:
            return self._overrides[name]
        return self._factories[name]()


LOCATOR = Locator()
LOCATOR.register("store", lambda: "the real store")
LOCATOR.register("clock", lambda: "the real clock")
LOCATOR.register("mailer", lambda: "the real mailer")


class ReportWithLocator:
    def build(self):
        store = LOCATOR.get("store")
        clock = LOCATOR.get("clock")
        mailer = LOCATOR.get("mailer")
        return [store, clock, mailer]


class ReportWithArguments:
    def __init__(self, store, clock, mailer):
        self.store = store
        self.clock = clock
        self.mailer = mailer

    def build(self):
        return [self.store, self.clock, self.mailer]


def named_in(signature):
    return [name for name in signature.parameters if name != "self"]


def main():
    print(f"  dependencies the report needs       {len(NEEDS)}")
    print(f"  callers                             {len(CALLERS)}")
    print()

    locator_sig = inspect.signature(ReportWithLocator.build)
    arguments_sig = inspect.signature(ReportWithArguments.__init__)

    LOCATOR.override("store", "a test store")
    changed = 0
    for _ in CALLERS:
        if ReportWithLocator().build()[0] == "a test store":
            changed += 1

    print("    design                  names in the signature   one change reaches")
    print("    {:<24}{:<25}{}".format(
        "a locator",
        "%d of %d" % (len(named_in(locator_sig)), len(NEEDS)),
        "%d of %d callers" % (changed, len(CALLERS))))
    print("    {:<24}{:<25}{}".format(
        "constructor arguments",
        "%d of %d" % (len(named_in(arguments_sig)), len(NEEDS)),
        "1 caller"))
    print()
    print("  the locator names no dependency in the signature, and that is")
    print("  the property it is chosen for. the bill arrives in the third")
    print(f"  column: one override reached all {changed} callers, because they all")
    print("  read the same global. a change that was meant for one test")
    print("  reaches production code, and the signature of the thing that")
    print("  changed says nothing about it.")
    print()
    print("  the count of zero in the first column is not a coincidence")
    print("  either. a dependency that is fetched inside a method body is not")
    print("  a dependency the caller knows about, so the caller cannot")
    print("  provide it, cannot replace it, and cannot read the method and")
    print("  find out -- the method body is the only place it appears.")
    print()
    print("  the third failure is where the error surfaces. `get` raises")
    print("  `KeyError` on a name nobody registered, and it raises it in the")
    print("  middle of `build`, after the object exists, in a frame that")
    print("  belongs to the report rather than to the wiring. a constructor")
    print("  argument fails at the call site that forgot it, which is the")
    print("  place somebody has to look anyway.")


main()
