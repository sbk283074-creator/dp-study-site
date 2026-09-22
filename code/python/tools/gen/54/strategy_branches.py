"""Chapter 54 -- the strategy pattern, and what adding a case costs.

The same five shipping methods, written twice: as a chain of comparisons
and as a table. Both are measured, and the measurement of "how many
places mention this name" is taken from the source of the file you are
reading rather than asserted.
"""

import pathlib

CHAIN_ORDER = ["standard", "express", "overnight", "pickup", "freight"]


# --- chain
def cost_chain(order, method, count):
    count[0] = 0

    count[0] += 1
    if method == "standard":
        return order * 1.0

    count[0] += 1
    if method == "express":
        return order * 1.4 + 2.0

    count[0] += 1
    if method == "overnight":
        return order * 2.0 + 8.0

    count[0] += 1
    if method == "pickup":
        return 0.0

    count[0] += 1
    if method == "freight":
        return order * 0.8 + 12.0

    raise ValueError("unknown method: " + method)


# --- default
def cost_chain_default(order, method, count):
    """The same chain with the last branch written as a default, which is
    the version that ships."""
    count[0] = 0

    count[0] += 1
    if method == "express":
        return order * 1.4 + 2.0

    count[0] += 1
    if method == "overnight":
        return order * 2.0 + 8.0

    count[0] += 1
    if method == "pickup":
        return 0.0

    count[0] += 1
    if method == "freight":
        return order * 0.8 + 12.0

    return order * 1.0


# --- table
def rate_standard(order):
    return order * 1.0


def rate_express(order):
    return order * 1.4 + 2.0


def rate_overnight(order):
    return order * 2.0 + 8.0


def rate_pickup(order):
    return 0.0


def rate_freight(order):
    return order * 0.8 + 12.0


RATES = {
    "standard": rate_standard,
    "express": rate_express,
    "overnight": rate_overnight,
    "pickup": rate_pickup,
    "freight": rate_freight,
}


def cost_table(order, method, count):
    count[0] = 1
    try:
        return RATES[method](order)
    except KeyError:
        raise ValueError("unknown method: " + method) from None
# --- end


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
# The chain region stops at the second chain, so that the line count below
# compares one chain against one table. `cost_chain_default` is a variant
# used only by the last table, and counting it here would compare two
# implementations against one.
CHAIN_SRC = SOURCE.split("# --- chain")[1].split("# --- default")[0]
TABLE_SRC = SOURCE.split("# --- table")[1].split("# --- end")[0]

UNKNOWN = ["sameday", "drone", "barge"]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  methods                             {len(CHAIN_ORDER)}")
    print(f"  lines in the chain region           "
          f"{len(CHAIN_SRC.strip().splitlines())}")
    print(f"  lines in the table region           "
          f"{len(TABLE_SRC.strip().splitlines())}")
    print()

    print("    method       comparisons    lines mentioning the name")
    print("                 chain table      chain table")
    total_chain = 0
    for method in CHAIN_ORDER:
        count = [0]
        cost_chain(10.0, method, count)
        total_chain += count[0]
        print("    {:<12}{:>6}{:>6}{:>11}{:>6}".format(
            method, count[0], 1, mentions(CHAIN_SRC, method),
            mentions(TABLE_SRC, method)))
    print()
    print("    {:<12}{:>6}{:>6}".format("total", total_chain, len(CHAIN_ORDER)))
    print()

    print(f"  the chain compares the name {total_chain} times to resolve "
          f"{len(CHAIN_ORDER)} calls,")
    print("  and the table compares it once per call. the chain's cost grows")
    print("  with the number of cases and the table's does not.")
    print()
    print("  the table is also the longer of the two, and it mentions every")
    print("  name twice: once as a function and once as a key. so the usual")
    print("  argument for the pattern -- that it is tidier -- is not what the")
    print("  numbers say. it is more code.")
    print()
    print("  what it buys is in the last table.")
    print()

    print("    an unknown method                the charge it produced")
    for method in UNKNOWN:
        count = [0]
        try:
            cost_chain(10.0, method, count)
            chain = "charged"
        except ValueError:
            chain = "refused"
        default = cost_chain_default(10.0, method, [0])
        count = [0]
        try:
            cost_table(10.0, method, count)
            table = "charged"
        except ValueError:
            table = "refused"
        print("    {:<32}{:<10}{:<13}{}".format(
            method, chain, "charged %.1f" % default, table))
    print()
    print("  both the chain and the table refuse an unknown method. the chain")
    print("  with a default branch charges it the standard rate instead, and")
    print("  nothing anywhere says so -- the request succeeds, the customer is")
    print("  billed, and the only signal is a number that is plausible.")
    print()
    print("  that is the actual difference between the two shapes. it is not")
    print("  line count and it is not speed. a chain has a place where a case")
    print("  can be forgotten, and forgetting it is a *fall-through* to")
    print("  whichever branch happens to be last. a table has no such place,")
    print("  because a missing key is a `KeyError` on the first call.")


main()
