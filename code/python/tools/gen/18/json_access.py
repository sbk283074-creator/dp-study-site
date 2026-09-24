"""Chapter 18 -- reading JSON that is not shaped the way you hoped.

One response document, ten paths into it, walked twice: once with square
brackets and once with a walker that returns None. The count is of paths that
raise, and of paths that hand back a null the caller has to notice.
"""

RESPONSE = {
    "user": {"id": 7, "name": "ada", "email": None},
    "items": [{"sku": "A1", "qty": 2}, {"sku": "B2"}],
    "page": {"next": None, "total": 3},
}


def walk(value, *steps):
    """Follow dict keys and list indexes, giving up with None at any step."""
    for step in steps:
        if isinstance(step, int):
            if not isinstance(value, list) or step >= len(value):
                return None
            value = value[step]
        else:
            if not isinstance(value, dict):
                return None
            value = value.get(step)
        if value is None:
            return None
    return value


PATHS = [
    ("user.id", lambda r: r["user"]["id"], ("user", "id")),
    ("user.name", lambda r: r["user"]["name"], ("user", "name")),
    ("user.email", lambda r: r["user"]["email"], ("user", "email")),
    ("user.phone", lambda r: r["user"]["phone"], ("user", "phone")),
    ("items[0].sku", lambda r: r["items"][0]["sku"], ("items", 0, "sku")),
    ("items[1].qty", lambda r: r["items"][1]["qty"], ("items", 1, "qty")),
    ("items[5].sku", lambda r: r["items"][5]["sku"], ("items", 5, "sku")),
    ("page.next", lambda r: r["page"]["next"], ("page", "next")),
    ("page.total", lambda r: r["page"]["total"], ("page", "total")),
    ("page.count", lambda r: r["page"]["count"], ("page", "count")),
]


def show(value):
    if value is None:
        return "null"
    return str(value)


def direct(step):
    try:
        return show(step(RESPONSE))
    except (KeyError, IndexError, TypeError) as error:
        return type(error).__name__


rows = []
for label, step, path in PATHS:
    rows.append((label, direct(step), show(walk(RESPONSE, *path))))

raised = sum(1 for _, left, _ in rows if left.endswith("Error"))
nulls = sum(1 for _, left, _ in rows if left == "null")
values = len(rows) - raised - nulls

print(f"{len(rows)} paths into one response document")
print()
print(f"{'path':<18}{'brackets':>14}{'walker':>12}")
print("-" * 44)
for label, left, right in rows:
    print(f"{label:<18}{left:>14}{right:>12}")

print()
print(f"{'what is counted':<44}{'count':>8}")
print("-" * 52)
print(f"{'paths probed':<44}{len(rows):>8}")
print(f"{'paths that raised an exception':<44}{raised:>8}")
print(f"{'paths that returned a null instead':<44}{nulls:>8}")
print(f"{'paths that returned a usable value':<44}{values:>8}")
print(f"{'paths the walker raised on':<44}{0:>8}")

print()
print("The exceptions are the loud half, and they are not one exception. Three")
print("paths raise KeyError and one raises IndexError, so the `except KeyError`")
print("that looks like it covers this does not: the list index is a different")
print("failure with a different name, and it arrives from the same expression.")
print()
print("The null column is the quiet half and it is the more expensive one. Two")
print("paths succeed and hand back None -- the key is present and its value is")
print("null, which is not the same thing as the key being absent, and the")
print("difference does not show up here. It shows up three functions later, as")
print("a TypeError on a value somebody assumed was a string.")
print()
print("A walker that returns None for every miss collapses all of it into one")
print("outcome, and that is the trade: no crashes, and no way to tell 'absent'")
print("from 'present but null' from 'wrong type'. Pick per field. Use the")
print("walker for the fields you can do without, and check the ones you cannot")
print("with an explicit `if key not in data: raise` so the failure lands at the")
print("boundary where the response arrived.")
