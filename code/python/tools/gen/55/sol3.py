"""Chapter 55 -- practice 3.

Six modules, three concrete types, and the wiring in two places. The
count is of the modules that name a concrete type, and the last table is
what moving the wiring into one module does to it.
"""

CONCRETE = ["SqlStore", "StripeGateway", "CsvWriter"]

# --- in the callers
ROUTES = """\
from stores import SqlStore
from gateways import StripeGateway


def checkout(request):
    store = SqlStore()
    gateway = StripeGateway()
    return store.save(request, gateway)
"""

NIGHTLY = """\
from stores import SqlStore


def run():
    return SqlStore().sweep()
"""

REPORTS = """\
from stores import SqlStore
from writers import CsvWriter


def monthly():
    return CsvWriter().write(SqlStore().all())
"""

ORDERS = """\
def total(order):
    return sum(line.amount for line in order.lines)
"""

PRICING = """\
def price(amount, rate):
    return amount * rate
"""
# --- end


# --- in a composition root
ROUTES_AFTER = """\
def checkout(request, store, gateway):
    return store.save(request, gateway)
"""

NIGHTLY_AFTER = """\
def run(store):
    return store.sweep()
"""

REPORTS_AFTER = """\
def monthly(store, writer):
    return writer.write(store.all())
"""

COMPOSITION = """\
from gateways import StripeGateway
from stores import SqlStore
from writers import CsvWriter

STORE = SqlStore()
GATEWAY = StripeGateway()
WRITER = CsvWriter()
"""
# --- end


BEFORE = [
    ("routes", ROUTES), ("nightly", NIGHTLY), ("reports", REPORTS),
    ("orders", ORDERS), ("pricing", PRICING),
]

AFTER = [
    ("routes", ROUTES_AFTER), ("nightly", NIGHTLY_AFTER),
    ("reports", REPORTS_AFTER), ("orders", ORDERS), ("pricing", PRICING),
    ("composition", COMPOSITION),
]


def named(source):
    return [name for name in CONCRETE if name in source]


def main():
    print(f"  modules                             {len(BEFORE)}")
    print(f"  concrete types                      {len(CONCRETE)}")
    print()
    print("    module            names, with the wiring in the callers")
    for label, source in BEFORE:
        found = named(source)
        print("    {:<18}{}".format(
            label, ", ".join(found) if found else "nothing concrete"))
    print()
    print("    module            names, with the wiring in one module")
    for label, source in AFTER:
        found = named(source)
        print("    {:<18}{}".format(
            label, ", ".join(found) if found else "nothing concrete"))
    print()

    print("    where the wiring lives       modules naming a type   references")
    for label, modules in (("in the callers", BEFORE),
                           ("in a composition root", AFTER)):
        holders = sum(1 for _, source in modules if named(source))
        references = sum(len(named(source)) for _, source in modules)
        print("    {:<29}{:<23}{}".format(
            label, "%d of %d" % (holders, len(modules)), references))
    print()
    print("  the count that matters is the second column, and it goes from")
    print("  three modules to one. that is the number of places a change to")
    print("  the database reaches, and it is the number to measure before")
    print("  and after.")
    print()
    print("  the reference count drops as well, from five to three, and it")
    print("  drops for a different reason: with the wiring in the callers")
    print("  each caller names what it needs, so `SqlStore` is named three")
    print("  times. in one module each type is named once.")
    print()
    print("  the fourth column of the table is the one that does not move.")
    print("  `orders` and `pricing` name nothing concrete in either design,")
    print("  and they are the modules the refactor was for. a module that")
    print("  takes its dependencies can be moved, tested and read without")
    print("  anything else changing, and the composition root is the price")
    print("  of having several of them.")
    print()
    print("  so the exercise has a stopping rule. count the modules that")
    print("  name a concrete type. if it is one, the composition root is")
    print("  already there. if it is more than one, each extra module is a")
    print("  place the next change has to visit.")


main()
