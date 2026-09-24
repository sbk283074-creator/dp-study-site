"""Chapter 26 -- a route is a pattern, and the order you register them is a decision.

Eight path patterns and seven requests, matched by a hand-rolled matcher. The
count is of requests that match more than one pattern, which is where the order
starts to matter.
"""

PATTERNS = [
    ("/", "root"),
    ("/items", "list items"),
    ("/items/{item_id}", "one item"),
    ("/items/{item_id}/tags", "tags of one item"),
    ("/items/new", "new item form"),
    ("/users/{user_id}", "one user"),
    ("/users/me", "current user"),
    ("/files/{path:path}", "any file"),
]

REQUESTS = [
    ("/", "root"),
    ("/items", "list items"),
    ("/items/42", "one item"),
    ("/items/new", "new item form"),
    ("/items/42/tags", "tags of one item"),
    ("/users/me", "current user"),
    ("/files/a/b/c", "any file"),
]


def matches(pattern, path):
    if pattern.endswith("{path:path}"):
        prefix = pattern[: -len("{path:path}")]
        return path.startswith(prefix) and len(path) > len(prefix)
    want = pattern.strip("/").split("/") if pattern != "/" else []
    have = path.strip("/").split("/") if path != "/" else []
    if len(want) != len(have):
        return False
    for expected, actual in zip(want, have):
        if expected.startswith("{") and expected.endswith("}"):
            continue
        if expected != actual:
            return False
    return True


rows = []
for path, intended in REQUESTS:
    hits = [label for pattern, label in PATTERNS if matches(pattern, path)]
    rows.append((path, hits, hits[0] if hits else "-", intended))

print(f"{len(PATTERNS)} patterns and {len(REQUESTS)} requests")
print()
print(f"{'request':<20}{'matches':>8}   {'first registered':<18}{'intended'}")
print("-" * 57)
for path, hits, first, intended in rows:
    print(f"{path:<20}{len(hits):>8}   {first:<18}{intended}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'patterns registered':<46}{len(PATTERNS):>8}")
print(f"{'requests tried':<46}{len(rows):>8}")
print(f"{'requests matching exactly one pattern':<46}"
      f"{sum(1 for r in rows if len(r[1]) == 1):>8}")
print(f"{'requests matching more than one pattern':<46}"
      f"{sum(1 for r in rows if len(r[1]) > 1):>8}")
print(f"{'requests where the first match is not the intended one':<46}"
      f"{sum(1 for r in rows if r[2] != r[3]):>8}")

print()
print("Two requests match more than one pattern, and both of them are the case")
print("the chapter warns about. `/items/new` matches `/items/{item_id}` as well")
print("as `/items/new`, because `new` is a perfectly good item id as far as the")
print("matcher is concerned. `/users/me` matches `/users/{user_id}` in the same")
print("way. Nothing is ambiguous to the framework -- it takes the first")
print("registered pattern that matches, and moves on.")
print()
print("So the order in the file is the routing table. A literal path must be")
print("registered before the parameterised path it is a special case of, or the")
print("parameterised one wins and the handler for `new` is never called. The")
print("failure is quiet: `/items/new` returns a 404 from the item lookup rather")
print("than a 500, so it looks like missing data rather than a routing mistake.")
print()
print("That is also why a route table is worth reading as a list rather than")
print("trusting the decorators to be in the right order. And it is the reason")
print("the chapter puts routers in the plan early: once an app has forty path")
print("operations across six files, the order is no longer something you can")
print("see, and the special cases have to be grouped where they are declared.")
