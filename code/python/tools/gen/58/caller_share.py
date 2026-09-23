"""Chapter 58 -- who calls the hot function.

One field-touching function with four call sites. The count is of calls
attributed to the site that made them, which is what decides whether the
function or a caller is the thing to change.
"""

DOCS = 200
FIELDS = 20

CALL_SITES = ["load_header", "load_body", "load_footer", "validate"]


def touch(field, site, count):
    count[site] = count.get(site, 0) + 1
    return field.strip().lower()


def load_header(doc, count):
    return touch(doc["id"], "load_header", count)


def load_body(doc, count):
    out = []
    for field in doc["fields"]:
        out.append(touch(field, "load_body", count))
    return out


def load_footer(doc, count):
    return touch(doc["tail"], "load_footer", count)


def validate(doc, count):
    """Touches every field the loaders have already touched, plus the tail."""
    for field in doc["fields"]:
        touch(field, "validate", count)
    touch(doc["tail"], "validate", count)
    return True


def make_doc(index):
    return {
        "id": "doc-%d" % index,
        "tail": "tail-%d" % index,
        "fields": ["f%d" % (i % 9) for i in range(FIELDS)],
    }


def run():
    count = {}
    for index in range(DOCS):
        doc = make_doc(index)
        load_header(doc, count)
        load_body(doc, count)
        load_footer(doc, count)
        validate(doc, count)
    return count


def main():
    count = run()
    total = sum(count.values())
    fields = DOCS * FIELDS
    print(f"  documents                           {DOCS}")
    print(f"  fields per document                 {FIELDS}")
    print(f"  fields touched at least once      {fields:>8}")
    print()
    print("    call site       calls   share of all calls")
    for site in CALL_SITES:
        print("    {:<14}{:>8}{:>18.1f}%".format(site, count[site],
                                                100.0 * count[site] / total))
    print("    {:<14}{:>8}{:>18}".format("total", total, "100.0%"))
    print()

    ranked = sorted(CALL_SITES, key=lambda s: -count[s])
    top = ranked[0]
    other = ranked[1]
    per_field = total / fields
    print("    the same function, entered       %6d times" % total)
    print("    to touch                         %6d fields" % fields)
    print("    so each field is touched         %6.2f times" % per_field)
    print()
    print(f"  `touch` is one function entered from {len(CALL_SITES)} places. The largest")
    print(f"  single caller is `{top}` with {count[top]} calls, {100.0 * count[top] / total:.1f}% of")
    print(f"  everything done inside it, and `{other}` is within")
    print(f"  {100.0 * (count[top] - count[other]) / total:.1f} points of that.")
    print()
    print("  the second of those two is the finding. `validate` walks the")
    print("  fields the loaders have just walked, so a walk that has already")
    print("  happened happens again, and a count is what makes a duplicate")
    print("  pass look like work instead of looking like care.")
    print()
    print(f"  halving the cost of `touch` removes {total // 2} units and edits a")
    print(f"  function that {len(CALL_SITES)} call sites share. Deleting the repeat removes")
    print(f"  {count[top]} units and edits one caller. Those are the same size of")
    print("  win, and only one of them is a deletion.")
    print()
    print("  a profile of this program reports one row for `touch`, at 100% of")
    print("  the time, because every call goes through it. The count of who")
    print("  called it is the column a profile does not have, and here it is")
    print("  the column that says what to delete.")


main()
