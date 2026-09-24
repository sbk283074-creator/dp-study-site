"""Chapter 27 -- an exception handler is a mapping, and the default is 500.

Eight failures a service can raise, five of them mapped to a status code by hand.
The count is of failures that reach the client as something other than a 500, and
of failures where the client is told the wrong thing.
"""

FAILURES = [
    ("NotFound", 404, True, "the row is not there"),
    ("Forbidden", 403, True, "the caller may not touch this row"),
    ("Unauthorized", 401, True, "no token, or an expired one"),
    ("Conflict", 409, True, "the name is already taken"),
    ("ValidationError", 422, True, "the values are the wrong kind"),
    ("IntegrityError", 409, False, "a database constraint refused the write"),
    ("TimeoutError", 504, False, "an upstream call timed out"),
    ("ConnectionError", 503, False, "the database is unreachable"),
]

rows = []
for name, intended, handled, _ in FAILURES:
    rows.append((name, intended, handled, intended if handled else 500))

print(f"{len(rows)} failures a service can raise")
print()
print(f"{'failure':<20}{'intended':>10}{'handler':>10}{'client sees':>14}")
print("-" * 54)
for name, intended, handled, seen in rows:
    print(f"{name:<20}{intended:>10}{('yes' if handled else 'no'):>10}{seen:>14}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'failures listed':<46}{len(rows):>8}")
print(f"{'failures with a handler':<46}"
      f"{sum(1 for r in rows if r[2]):>8}")
print(f"{'failures that reach the client as 500':<46}"
      f"{sum(1 for r in rows if r[3] == 500):>8}")
print(f"{'failures whose intended code is 4xx':<46}"
      f"{sum(1 for r in rows if r[1] < 500):>8}")
print(f"{'failures whose intended code is 5xx':<46}"
      f"{sum(1 for r in rows if r[1] >= 500):>8}")
print(f"{'failures where the client sees the wrong code':<46}"
      f"{sum(1 for r in rows if r[1] != r[3]):>8}")

print()
print("A 500 is the correct default and an uninformative answer. The three")
print("failures without a handler are not crashes -- the service knows exactly")
print("what happened -- but the client is told 'something went wrong on our")
print("side', which is true and useless. A timeout becomes a 500 instead of a")
print("504, a write that broke a constraint becomes a 500 instead of a 409,")
print("and a database that is down becomes a 500 instead of a 503.")
print()
print("That matters because the code is the part a client acts on. 504 and 503")
print("say the request may work later; 409 says it will not until something")
print("changes; 500 says only that the caller cannot tell. A client that")
print("retries on 5xx will retry all three, including the one that will never")
print("succeed.")
print()
print("So the mapping is part of the API, and it belongs in one place: an")
print("exception handler per class, registered at startup, so the translation")
print("is visible rather than scattered through the endpoints. And the count to")
print("watch is the last row -- the number of failures that reach the client as")
print("something other than what the service meant.")
