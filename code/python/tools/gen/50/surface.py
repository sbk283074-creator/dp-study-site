#!/usr/bin/env python3
"""Chapter 50 demo, part 3 -- the attack surface is not the endpoint count.

Every parameter a handler reads is an input an attacker controls, and the
count of those is what the attacker gets to choose from -- not the count of
URLs. The gap between the two is where this script lives: nineteen routes,
but how many inputs?

The second half is the part worth internalising. A framework validates what
it can see in the signature, and it sees path parameters best: they are
typed in the decorator and rejected before the handler runs. Body fields and
query strings are validated only if somebody wrote the rule, and headers are
not validated at all -- which is a problem, because that is where the
credential arrives.

Each input is (name, where it arrives, what checks it).
"""

CHECKS = ("type", "range", "enum", "schema", "none")

ROUTES = [
    ("GET", "/health", "none", []),
    ("GET", "/decks", "session", [
        ("limit", "query", "range"), ("offset", "query", "range"),
        ("sort", "query", "enum"), ("q", "query", "none")]),
    ("GET", "/decks/{deck_id}", "owner", [
        ("deck_id", "path", "type")]),
    ("POST", "/decks", "session", [
        ("title", "body", "type"), ("description", "body", "none"),
        ("tags", "body", "schema")]),
    ("PUT", "/decks/{deck_id}", "owner", [
        ("deck_id", "path", "type"), ("title", "body", "type"),
        ("description", "body", "none")]),
    ("DELETE", "/decks/{deck_id}", "owner", [
        ("deck_id", "path", "type")]),
    ("GET", "/decks/{deck_id}/cards", "owner", [
        ("deck_id", "path", "type"), ("limit", "query", "range"),
        ("offset", "query", "range")]),
    ("POST", "/decks/{deck_id}/cards", "owner", [
        ("deck_id", "path", "type"), ("front", "body", "type"),
        ("back", "body", "type"), ("image_url", "body", "none"),
        ("tags", "body", "schema")]),
    ("PUT", "/cards/{card_id}", "owner", [
        ("card_id", "path", "type"), ("front", "body", "type"),
        ("back", "body", "type"), ("image_url", "body", "none")]),
    ("DELETE", "/cards/{card_id}", "owner", [
        ("card_id", "path", "type")]),
    ("GET", "/search", "session", [
        ("q", "query", "none"), ("limit", "query", "range"),
        ("offset", "query", "range"), ("lang", "query", "enum")]),
    ("POST", "/login", "none", [
        ("email", "body", "type"), ("password", "body", "none")]),
    ("POST", "/register", "none", [
        ("email", "body", "type"), ("password", "body", "none"),
        ("display_name", "body", "none")]),
    ("POST", "/reset", "none", [
        ("email", "body", "type")]),
    ("GET", "/me", "session", [
        ("Authorization", "header", "none")]),
    ("POST", "/upload", "none", [
        ("file", "file", "type"), ("filename", "body", "none")]),
    ("GET", "/export", "owner", [
        ("deck_id", "query", "type"), ("format", "query", "enum"),
        ("token", "query", "none")]),
    ("GET", "/admin/users", "admin", [
        ("email", "query", "none"), ("limit", "query", "range"),
        ("offset", "query", "range")]),
    ("GET", "/admin/logs", "admin", [
        ("q", "query", "none"), ("since", "query", "none"),
        ("limit", "query", "range")]),
]

# The routes that are supposed to run before anyone has logged in.
PREAUTH = {"/health", "/login", "/register", "/reset"}

WHERE = ("path", "query", "body", "header", "file")


def main():
    routes = len(ROUTES)
    inputs = [(r[1], i) for r in ROUTES for i in r[3]]
    total = len(inputs)

    print(f"  routes                             {routes:>3}")
    print(f"  untrusted inputs                   {total:>3}"
          f"   ({total / routes:.1f} per route)")

    print()
    print("  where the inputs arrive")
    for where in WHERE:
        got = [i for _, i in inputs if i[1] == where]
        unchecked = [i for i in got if i[2] == "none"]
        share = f"{len(got) / total:>6.1%}" if total else "  n/a"
        print(f"    {where:<8} {len(got):>3}  {share}   unchecked {len(unchecked):>2}"
              f" of {len(got)}")

    print()
    print("  what checks each input")
    for check in CHECKS:
        got = [i for _, i in inputs if i[2] == check]
        note = {
            "type": "rejected by the framework if the type is wrong",
            "range": "a bound somebody wrote down",
            "enum": "one of a set somebody wrote down",
            "schema": "a nested model, field by field",
            "none": "arrives as text and is used as text",
        }[check]
        print(f"    {check:<7} {len(got):>3}   {note}")

    unchecked = [i for _, i in inputs if i[2] == "none"]
    real_rule = [i for _, i in inputs if i[2] in ("range", "enum", "schema")]
    type_only = [i for _, i in inputs if i[2] == "type"]
    print()
    print(f"  with a rule somebody chose         {len(real_rule):>3}"
          f"   ({len(real_rule) / total:.1%})")
    print(f"  with the framework's type check    {len(type_only):>3}"
          f"   ({len(type_only) / total:.1%})")
    print(f"  with no check at all               {len(unchecked):>3}"
          f"   ({len(unchecked) / total:.1%})")

    print()
    print("  the routes with the most inputs")
    ranked = sorted(ROUTES, key=lambda r: (-len(r[3]), r[1]))
    for method, path, _, ins in ranked[:5]:
        print(f"    {len(ins):>2} inputs   {method:<6} {path}")
    top3 = sum(len(r[3]) for r in ranked[:3])
    print(f"    top three routes carry {top3} of {total} inputs ({top3 / total:.1%})")

    print()
    print("  routes that read input with no authorization check")
    for method, path, authz, ins in ROUTES:
        if authz == "none":
            verdict = "expected -- runs before login" if path in PREAUTH else "NOT expected"
            print(f"    {method:<6} {path:<18} {verdict}")


if __name__ == "__main__":
    main()
