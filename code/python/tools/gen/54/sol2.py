"""Chapter 54 -- practice 2.

Where a dependency's names appear. Three consumers written twice: once
reading the vendor's field names wherever they are needed, and once
behind a single translation. The count is of functions that mention a
vendor name, taken from the source of the file you are reading.
"""

import pathlib

VENDOR_FIELDS = ["customer_name", "amount_cents", "currency_code",
                 "captured_at", "refundable"]


class Gateway:
    """A stand-in for a payment library. Its records are dictionaries
    with its own names, and it renames them in v2."""

    def __init__(self, version):
        self.version = version

    def charges(self):
        if self.version == 1:
            return [{"customer_name": "Ada", "amount_cents": 1200,
                     "currency_code": "GBP", "captured_at": 1,
                     "refundable": True}]
        return [{"customer": "Ada", "amount_minor": 1200,
                 "currency": "GBP", "captured": 1, "refundable": True}]


# --- direct
def direct_summary(charge):
    return {"who": charge["customer_name"],
            "amount": charge["amount_cents"] / 100}


def direct_receipt(charge):
    return {"total": charge["amount_cents"],
            "in": charge["currency_code"]}


def direct_audit(charge):
    return {"when": charge["captured_at"],
            "refundable": charge["refundable"]}


DIRECT_CONSUMERS = [direct_summary, direct_receipt, direct_audit]
# --- direct


# --- adapted
def translate(charge):
    """The one place the vendor's names appear."""
    return {"who": charge["customer_name"],
            "minor": charge["amount_cents"],
            "currency": charge["currency_code"],
            "when": charge["captured_at"],
            "can_refund": charge["refundable"]}


def summary(charge):
    row = translate(charge)
    return {"who": row["who"], "amount": row["minor"] / 100}


def receipt(charge):
    row = translate(charge)
    return {"total": row["minor"], "in": row["currency"]}


def audit(charge):
    row = translate(charge)
    return {"when": row["when"], "can_refund": row["can_refund"]}


ADAPTED_CONSUMERS = [summary, receipt, audit]
ADAPTED_FUNCTIONS = [translate, summary, receipt, audit]
# --- adapted


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
DIRECT_SRC = SOURCE.split("# --- direct")[1].split("# --- direct")[0]
ADAPTED_SRC = SOURCE.split("# --- adapted")[1].split("# --- adapted")[0]


def body_of(source, name):
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("def " + name):
            out = []
            for line in lines[i + 1:]:
                if line.startswith("def ") or line.startswith("# ---"):
                    break
                out.append(line)
            return out
    return []


def mentions(source, name):
    return sum(1 for line in body_of(source, name)
               for field in VENDOR_FIELDS if field in line)


def main():
    print(f"  vendor fields                       {len(VENDOR_FIELDS)}")
    print(f"  consumers                           {len(DIRECT_CONSUMERS)}")
    print()

    print("    consumer           vendor names read   functions that read one")
    SUMMARY = {}
    for label, names in (("direct", DIRECT_CONSUMERS),
                         ("adapted", ADAPTED_FUNCTIONS)):
        source = DIRECT_SRC if label == "direct" else ADAPTED_SRC
        per = {fn.__name__: mentions(source, fn.__name__) for fn in names}
        total = sum(per.values())
        touched = sum(1 for n in per.values() if n)
        SUMMARY[label] = (total, touched, len(names))
        print("    {:<19}{:>11}   {} of {}".format(
            label, total, touched, len(names)))
    print()

    print("    function                       vendor names in its body")
    for label, source, names in (("direct", DIRECT_SRC, DIRECT_CONSUMERS),
                                 ("adapted", ADAPTED_SRC, ADAPTED_FUNCTIONS)):
        for fn in names:
            print("    {:<31}{}".format(
                fn.__name__, mentions(source, fn.__name__)))
    print()

    for version in (1, 2):
        gateway = Gateway(version)
        print("    gateway v%d" % version)
        for label, consumers in (("direct", DIRECT_CONSUMERS),
                                 ("adapted", ADAPTED_CONSUMERS)):
            outcomes = []
            for fn in consumers:
                for charge in gateway.charges():
                    try:
                        fn(charge)
                        outcomes.append("ok")
                    except KeyError as exc:
                        outcomes.append("KeyError " + str(exc))
            broken = sum(1 for o in outcomes if o != "ok")
            print("      {:<9}{} of {} consumers broken".format(
                label, broken, len(consumers)))
    print()
    d_reads, d_funcs, _ = SUMMARY["direct"]
    a_reads, a_funcs, _ = SUMMARY["adapted"]
    print(f"  the direct version reads {d_reads} vendor fields across "
          f"{d_funcs} functions. the")
    print(f"  adapted one reads {a_reads} in {a_funcs}. the second number is the one to")
    print("  write down, because it is the number of places a rename touches,")
    print("  and it is the number the adapter divides.")
    print()
    print("  so the count to write down is the number of functions that")
    print("  mention a vendor name, because that is the number of places a")
    print("  rename touches. with one consumer the two are equal and the")
    print("  adapter is a layer with nothing to do. with three it is the")
    print("  difference between one edit and three, and the three are in")
    print("  functions whose job is something else.")
    print()
    print("  the question to ask before writing the adapter is therefore not")
    print("  whether the dependency might change. it is how many consumers")
    print("  read it, because that is the number the adapter divides.")


main()
