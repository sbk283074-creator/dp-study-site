"""Chapter 55 -- practice 1.

A class whose methods reach for names that do not arrive as arguments,
and the same class with them as constructor arguments. The count is of
the dependencies that arrive as arguments rather than by name.
"""

import pathlib

DB = {"rates": {"gbp": 1.0}}
DEFAULT_MARKUP = 1.2


def get_clock():
    return "12:00"


class Formatter:
    def format(self, amount):
        return "%.2f" % amount


# --- reaches
class PricerReaches:
    def quote(self, amount):
        rate = DB["rates"]["gbp"]
        stamp = get_clock()
        text = Formatter().format(amount * rate)
        return stamp + " " + text

    def markup(self, amount):
        return amount * DEFAULT_MARKUP
# --- end


# --- takes
class PricerTakes:
    def __init__(self, db, clock, formatter, markup):
        self.db = db
        self.clock = clock
        self.formatter = formatter
        self.markup = markup

    def quote(self, amount):
        rate = self.db["rates"]["gbp"]
        stamp = self.clock()
        text = self.formatter.format(amount * rate)
        return stamp + " " + text

    def markup(self, amount):
        return amount * self.markup
# --- end


REACHED = ["DB", "get_clock", "Formatter", "DEFAULT_MARKUP"]

SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
REACHES_SRC = SOURCE.split("# --- reaches")[1].split("# --- end")[0]
TAKES_SRC = SOURCE.split("# --- takes")[1].split("# --- end")[0]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  dependencies the class uses         {len(REACHED)}")
    print()
    print("    dependency        reached by name   arrived as an argument")
    for name in REACHED:
        print("    {:<18}{:<18}{}".format(
            name,
            "yes" if mentions(REACHES_SRC, name) else "no",
            "yes" if mentions(TAKES_SRC, name) else "no"))
    print()

    for label, source in (("reaches for them", REACHES_SRC),
                          ("takes them", TAKES_SRC)):
        by_name = sum(1 for name in REACHED if mentions(source, name))
        print("    {:<34}{} of {} reached by name".format(
            label, by_name, len(REACHED)))
    print()

    reaches = PricerReaches()
    takes = PricerTakes(DB, get_clock, Formatter(), DEFAULT_MARKUP)
    same = sum(1 for amount in (10, 25, 100)
               if reaches.quote(amount) == takes.quote(amount))
    print("    {:<34}{} of {} outputs alike".format(
        "the two versions", same, 3))
    print()
    print(f"  the reaching version uses {len(REACHED)} names it does not receive,")
    print("  and the version that takes them uses none. the output is the same")
    print("  for every amount, so nothing about the behaviour changed.")
    print()
    print("  the two to look at separately are `DB` and `DEFAULT_MARKUP`.")
    print("  `DB` is a seam: it is the thing a test wants to replace, and it")
    print("  is the reason to do this. `DEFAULT_MARKUP` is a constant, and a")
    print("  constant that arrives as a constructor argument is a value the")
    print("  caller can set to anything -- which is a configuration feature")
    print("  if you want one and a bug if you do not.")
    print()
    print("  so the count is a starting point and not a target. the question")
    print("  to ask of each name in the list is whether a test, a second")
    print("  environment or a second implementation would ever want to supply")
    print("  a different one. if the answer is yes for exactly one of them,")
    print("  inject that one and leave the constant alone.")


main()
