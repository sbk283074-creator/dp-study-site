"""Chapter 26 -- validation is a list of rules, and the first failure is a choice.

Six request bodies posted to one endpoint, checked by four total rules. The count
is of bodies rejected, of the rules that rejected them, and of bodies that break
more than one rule at once.
"""

RULES = [
    ("title is present", lambda body: "title" in body),
    ("title is a string", lambda body: isinstance(body.get("title"), str)),
    ("title is not blank",
     lambda body: isinstance(body.get("title"), str) and body["title"].strip() != ""),
    ("priority is 1 to 5",
     lambda body: isinstance(body.get("priority"), int)
     and not isinstance(body.get("priority"), bool)
     and 1 <= body["priority"] <= 5),
]

BODIES = [
    ("ordinary", {"title": "write it down", "priority": 3}),
    ("no title", {"priority": 3}),
    ("title is a number", {"title": 42, "priority": 3}),
    ("title is blank", {"title": "   ", "priority": 3}),
    ("priority out of range", {"title": "ship it", "priority": 9}),
    ("priority missing", {"title": "ship it"}),
]

rows = []
for label, body in BODIES:
    broken = [name for name, rule in RULES if not rule(body)]
    rows.append((label, broken, broken[0] if broken else "-"))

print(f"{len(RULES)} rules and {len(BODIES)} bodies posted to one endpoint")
print()
print(f"{'body':<24}{'valid':>7}{'rules broken':>14}   {'rejected by'}")
print("-" * 72)
for label, broken, first in rows:
    print(f"{label:<24}{('yes' if not broken else 'no'):>7}{len(broken):>14}   {first}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'rules defined':<46}{len(RULES):>8}")
print(f"{'bodies posted':<46}{len(rows):>8}")
print(f"{'bodies accepted':<46}"
      f"{sum(1 for r in rows if not r[1]):>8}")
print(f"{'bodies rejected':<46}"
      f"{sum(1 for r in rows if r[1]):>8}")
print(f"{'bodies that break more than one rule':<46}"
      f"{sum(1 for r in rows if len(r[1]) > 1):>8}")
print(f"{'rules that rejected at least one body':<46}"
      f"{len({name for _, broken, _ in rows for name in broken}):>8}")

print()
print("The count of rules broken is the part a hand-written `if` chain hides.")
print("The body with no title breaks three of the four rules, and the body")
print("with a numeric title breaks two. Each of them is rejected by whichever")
print("rule the author happened to check first, so the message the client")
print("receives depends on the order of the checks rather than on what is")
print("wrong.")
print()
print("That is the argument for a declarative model rather than a chain of")
print("ifs. A framework validates every field and reports every failure, so a")
print("client fixing one problem does not discover the next one on the")
print("following request. The status code follows from the kind of rule: the")
print("body is the right shape and the values are wrong is 422, the body is")
print("not the shape at all is 400, and the distinction is worth keeping")
print("because the client can act on one and not the other.")
print()
print("And the last row is the check on the rules themselves. A rule that no")
print("body ever breaks is a rule nobody has tested, and one that every body")
print("breaks is a rule that is wrong. All four of these fire, which is what a")
print("validation test table is for.")
