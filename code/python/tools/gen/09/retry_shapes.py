"""Chapter 9 -- retry, counted in attempts.

Six failure patterns and a budget of three attempts, under two policies: retry
any exception, or retry only the ones that are worth retrying. The count is of
attempts made, and the case that separates the two policies is the one that
was never going to succeed.
"""

BUDGET = 3


class Transient(Exception):
    """Worth trying again: the next attempt may work."""


class Permanent(Exception):
    """Not worth trying again: the next attempt fails the same way."""


CASES = [
    ("succeeds first try", 0, False),
    ("transient once", 1, False),
    ("transient twice", 2, False),
    ("transient three times", 3, False),
    ("never succeeds", None, False),
    ("permanent failure", 0, True),
]


def call(failures, permanent, number):
    """One attempt. `failures` is how many attempts fail before success."""
    if permanent:
        raise Permanent("the row does not exist")
    if failures is None or number <= failures:
        raise Transient("the service was busy")
    return "ok"


def retry_anything(failures, permanent):
    """Retry on every exception, up to the budget."""
    for number in range(1, BUDGET + 1):
        try:
            return call(failures, permanent, number), "ok", number
        except Exception:
            continue
    return None, "gave up", BUDGET


def retry_transient_only(failures, permanent):
    """Retry the transient errors and give up on the permanent ones at once."""
    for number in range(1, BUDGET + 1):
        try:
            return call(failures, permanent, number), "ok", number
        except Transient:
            continue
        except Permanent:
            return None, "gave up", number
    return None, "gave up", BUDGET


print(f"a budget of {BUDGET} attempts, {len(CASES)} failure patterns")
print()
print(f"{'case':<24}{'retry any':>11}{'outcome':>10}{'retry transient':>17}"
      f"{'outcome':>10}")
print("-" * 72)
total_any = 0
total_transient = 0
for name, failures, permanent in CASES:
    _value, outcome_any, attempts_any = retry_anything(failures, permanent)
    _value, outcome_transient, attempts_transient = retry_transient_only(
        failures, permanent
    )
    total_any += attempts_any
    total_transient += attempts_transient
    print(f"{name:<24}{attempts_any:>11}{outcome_any:>10}"
          f"{attempts_transient:>17}{outcome_transient:>10}")

print("-" * 72)
print(f"{'attempts, total':<24}{total_any:>11}{'':>10}{total_transient:>17}")

print()
print(f"The two policies agree on every pattern except the last, and the last is")
print(f"the one that matters: a failure that will fail the same way next time.")
print(f"Retrying it costs {total_any - total_transient} extra attempts here and buys nothing.")
print()
print("That is the whole design of a retry policy, and it is a count rather than")
print("a judgement call: retry the errors whose next attempt can differ, and")
print("give up on the ones whose next attempt cannot. A policy that retries")
print("everything is not more careful than one that retries the right things --")
print("it is slower, and it turns a clear failure into a delayed one.")
print()
print("The budget is the other half. Three of these patterns exhaust it, and")
print("the ones that do are indistinguishable from each other in the output:")
print("a service that was busy three times and a service that does not exist")
print("both produce a give-up. The exception type is the only thing that tells")
print("them apart, which is why the type is the thing to catch on.")
