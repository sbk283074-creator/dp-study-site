"""Chapter 54 -- the adapter pattern, measured as a count of places.

A vendor library whose records are dictionaries with the vendor's own
field names. Two consumers read them: one that reads the vendor's names
directly, and one that reads them behind a single translation. Then the
vendor renames a field, which is the only event the pattern is for.
"""

# what each consumer needs, and the vendor field it comes from
DIRECT_READS = [
    ("name", "user_name"),
    ("joined", "created"),
    ("tier", "plan_code"),
    ("active", "is_enabled"),
]


class VendorV1:
    def fetch(self):
        return [{"user_name": "ada", "created": 1,
                 "plan_code": "pro", "is_enabled": True}]


class VendorV2:
    """The same vendor, one release later."""

    def fetch(self):
        return [{"username": "ada", "created_at": 1,
                 "plan": "pro", "enabled": True}]


def direct(record):
    """Every field read is a place the vendor's names appear."""
    out = {}
    for label, field in DIRECT_READS:
        try:
            out[label] = record[field]
        except KeyError:
            out[label] = "MISSING"
    return out


def translate(record):
    """The one place the vendor's names appear."""
    return {
        "name": record["user_name"],
        "joined": record["created"],
        "tier": record["plan_code"],
        "active": record["is_enabled"],
    }


def adapted(record):
    try:
        return translate(record)
    except KeyError as exc:
        return {"translation failed": "MISSING " + str(exc)}


def survey(consumer, vendor):
    rows = []
    for record in vendor.fetch():
        rows.append(consumer(record))
    return rows


def main():
    print(f"  fields the consumer needs           {len(DIRECT_READS)}")
    print(f"  places the direct version reads one  {len(DIRECT_READS)}")
    print("  places the adapted version reads one 1")
    print()

    for label, vendor in (("vendor v1", VendorV1()), ("vendor v2", VendorV2())):
        print(f"    {label}")
        for name, consumer in (("direct", direct), ("adapted", adapted)):
            rows = survey(consumer, vendor)
            broken = sum(1 for row in rows
                         for value in row.values()
                         if isinstance(value, str) and value.startswith("MISSING"))
            print("      {:<9}{} of {} reads missing".format(
                name, broken, len(rows[0])))
        print()

    print("  under v1 both versions work, and that is the whole reason the")
    print("  pattern gets skipped. the two look identical in the output and")
    print("  the direct one is shorter, so the direct one ships.")
    print()
    print("  under v2 the direct version has four places to change and the")
    print("  adapted version has one. the number that matters is not four; it")
    print("  is that the four are spread across the consumer, wherever a field")
    print("  happened to be needed, and the one is a single function whose")
    print("  whole job is that translation.")
    print()
    print("  the adapter is not an extra layer for its own sake. it is the")
    print("  answer to a question you can ask before writing it: when this")
    print("  dependency changes, how many places will I be looking at? if the")
    print("  answer is one, the adapter is already there and you should keep")
    print("  it. if the answer is one, and it is one because there is only one")
    print("  call site, then the adapter is a layer with nothing to do.")


main()
