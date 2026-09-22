"""Chapter 55 -- the dependency that is not a dependency.

A pure function, and the same function behind an interface that is
injected. The count is of what each design adds, and of the tests that
needed the extra names.
"""

import pathlib

from typing import Protocol


# --- plain
def format_price(amount):
    return "%.2f" % amount
# --- end


# --- injected
class Formatter(Protocol):
    def format(self, amount):
        ...


class PlainFormatter:
    def format(self, amount):
        return "%.2f" % amount


def render(order, formatter):
    return formatter.format(order)
# --- end


AMOUNTS = [0, 1.5, 12, 1200.75]


class Counting:
    """The one implementation a test might supply, to check that the
    consumer called it."""

    def __init__(self):
        self.calls = []

    def format(self, amount):
        self.calls.append(amount)
        return "%.2f" % amount


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
PLAIN_SRC = SOURCE.split("# --- plain")[1].split("# --- end")[0]
INJ_SRC = SOURCE.split("# --- injected")[1].split("# --- end")[0]


def count(source, word):
    return sum(1 for line in source.splitlines() if word in line)


def main():
    print(f"  amounts                             {len(AMOUNTS)}")
    print()
    print("    what                          the function   behind an interface")
    print("    {:<30}{:>13}{:>20}".format(
        "classes", count(PLAIN_SRC, "class "), count(INJ_SRC, "class ")))
    print("    {:<30}{:>13}{:>20}".format(
        "functions", count(PLAIN_SRC, "def "), count(INJ_SRC, "def ")))
    print("    {:<30}{:>13}{:>20}".format(
        "lines", len(PLAIN_SRC.strip().splitlines()),
        len(INJ_SRC.strip().splitlines())))
    print()

    print("    the same answers from both")
    same = 0
    for amount in AMOUNTS:
        if format_price(amount) == PlainFormatter().format(amount):
            same += 1
    print("    {:<34}{} of {}".format("amounts formatted alike", same,
                                      len(AMOUNTS)))
    print()

    spy = Counting()
    render(1200.75, spy)
    print("    implementations that exist")
    print("    {:<36}{}".format("the function", "1"))
    print("    {:<36}{}".format("behind the interface", "1"))
    print("    {:<36}{}".format("implementations a test must supply", "0"))
    print()
    print(f"  both designs format all {len(AMOUNTS)} amounts the same way, and the")
    print("  interface adds an interface, a class and a parameter to do it.")
    print("  the third table is the reason: there is one implementation, and")
    print("  there is no test that needs a second one, because the thing")
    print("  being replaced is a pure function.")
    print()
    print("  the distinction that decides this is whether the collaborator")
    print("  has a seam to cut. a mailer, a clock, a store and a session all")
    print("  do -- they have a boundary where the real world is, and a test")
    print("  wants to be on the other side of it. formatting a number does")
    print("  not: it is a function from a number to a string, and there is")
    print("  nothing on the far side to replace.")
    print()
    print("  injecting it anyway is not free and it is not neutral. the")
    print("  parameter is a promise that a second implementation might")
    print("  arrive, and every reader of the signature has to hold that")
    print("  possibility in mind while nothing arrives. when a second one")
    print("  does arrive -- a currency, a locale -- that is the day to add")
    print("  the seam, and by then the second implementation is there to")
    print("  justify it.")
    print()
    print("  the rule is the one from the last chapter's pitfall, applied to")
    print("  a parameter instead of a class: introduce the seam when there is")
    print("  something to put on the other side of it, and not before.")


main()
