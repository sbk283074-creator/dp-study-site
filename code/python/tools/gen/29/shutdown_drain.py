"""Chapter 29 -- a deploy is a signal, and the requests in flight are the question.

Six requests in flight when the shutdown signal arrives, each with a known number
of ticks left. The count is of requests that finish, with a grace period and
without one.
"""

REQUESTS = [
    ("GET /items", 3),
    ("POST /items", 8),
    ("GET /items/42", 2),
    ("GET /reports", 25),
    ("POST /checkout", 12),
    ("GET /health", 1),
]

GRACE = 10

rows = [(label, ticks, ticks <= GRACE) for label, ticks in REQUESTS]
finished = [label for label, _, ok in rows if ok]
abandoned = [label for label, _, ok in rows if not ok]
slowest = max(ticks for _, ticks, _ in rows)

print(f"{len(rows)} requests in flight when the shutdown signal arrives")
print()
print(f"{'request':<20}{'ticks left':>12}{'finishes in ' + str(GRACE):>20}")
print("-" * 52)
for label, ticks, finishes in rows:
    print(f"{label:<20}{ticks:>12}{('yes' if finishes else 'no'):>20}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'requests in flight':<46}{len(rows):>8}")
print(f"{'grace period in ticks':<46}{GRACE:>8}")
print(f"{'requests that finish inside the grace period':<46}{len(finished):>8}")
print(f"{'requests abandoned inside the grace period':<46}{len(abandoned):>8}")
print(f"{'ticks the slowest request needs':<46}{slowest:>8}")
print(f"{'grace needed to finish every request':<46}{slowest:>8}")
print(f"{'requests that finish with no grace period':<46}{0:>8}")

print()
print("A grace period of ten ticks is enough for four of the six, and the two")
print("it cuts are the report and the checkout. That is the shape of the")
print("problem: the requests that are expensive are the ones a customer")
print("noticed, and they are exactly the ones a short grace period kills.")
print()
print("So the grace period is set by the slowest endpoint and not by the")
print("average. Ten ticks here looks generous against a mean of eight and a")
print("half, and it is not enough -- the number that matters is the twenty-five")
print("of the report. A deploy that kills a checkout mid-write is not a fast")
print("deploy, it is a data problem with a timestamp.")
print()
print("There is a second grace period and it is the one people miss. The")
print("orchestrator has its own timeout before it sends SIGKILL, and the")
print("application has its own drain timeout. If the orchestrator's is shorter,")
print("the process is killed while it is still draining and the application's")
print("setting never applies -- which is the same as having none. The two")
print("numbers have to be set together, with the application's strictly")
print("smaller, and the order is what makes the drain real.")
