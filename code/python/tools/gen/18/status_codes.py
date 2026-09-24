"""Chapter 18 -- status codes are not two cases, they are four.

Seventeen status codes a client will actually meet, classified by the class they
belong to, by whether raise_for_status() raises on them, and by whether retrying
could ever help. The count is of failures that are permanent.
"""

CODES = [200, 201, 204, 301, 304, 400, 401, 403, 404, 408, 409, 422, 429,
         500, 502, 503, 504]

RETRYABLE = {408, 429, 500, 502, 503, 504}


def classify(code):
    return f"{code // 100}xx"


def raises(code):
    return 400 <= code < 600


def retry(code):
    return code in RETRYABLE


rows = [(code, classify(code), raises(code), retry(code)) for code in CODES]

print(f"{len(rows)} status codes")
print()
print(f"{'code':<8}{'class':>8}{'raise_for_status':>18}{'retry could help':>18}")
print("-" * 52)
for code, group, does_raise, could_retry in rows:
    print(f"{code:<8}{group:>8}{('yes' if does_raise else 'no'):>18}"
          f"{('yes' if could_retry else 'no'):>18}")

by_class = {}
for code, group, _, _ in rows:
    by_class[group] = by_class.get(group, 0) + 1

raised = [code for code, _, does_raise, _ in rows if does_raise]
permanent = [code for code, _, does_raise, could_retry in rows
             if does_raise and not could_retry]

print()
print(f"{'what is counted':<44}{'count':>8}")
print("-" * 52)
for group in ("2xx", "3xx", "4xx", "5xx"):
    print(f"{'codes in class ' + group:<44}{by_class[group]:>8}")
print(f"{'codes raise_for_status raises on':<44}{len(raised):>8}")
print(f"{'codes a retry could ever fix':<44}{len(RETRYABLE):>8}")
print(f"{'failures that are permanent':<44}{len(permanent):>8}")

print()
print("The class counts are the first correction. There are four classes, not")
print("two, and the two that are not errors matter: a 3xx is a successful")
print("answer that says 'look elsewhere', and 304 is a success that carries no")
print("body at all. A client that tests `if status == 200` throws both away.")
print()
print(f"The raise row is the second correction. {len(raised)} of the {len(rows)} codes raise,")
print("and they are not all the same kind of problem. Retrying the whole group")
print(f"is the reflex, and {len(permanent)} of those {len(raised)} will return the same failure")
print("every time: a malformed request, a missing credential, a name that is")
print("not there. Retrying a 404 costs a round trip and buys nothing.")
print()
print(f"The retry rows are the number worth keeping. Only {len(RETRYABLE)} codes are worth a")
print("second attempt -- the timeouts, the rate limit, and the server errors --")
print("and the decision has to be made on the code, not on the fact that")
print("something went wrong. Retry on 408, 429 and 5xx with backoff; give up")
print("immediately on everything else and report what the body said.")
