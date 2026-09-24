"""Chapter 29 -- liveness asks if the process is alive, readiness asks if it can work.

Six checks a deployed service can make, split between the two probes. The count is
of dependencies each probe looks at, and of what the orchestrator does when one of
them is down.
"""

CHECKS = [
    ("config file parsed", "readiness", True, True),
    ("database reachable", "readiness", True, True),
    ("migrations applied", "readiness", True, True),
    ("cache reachable", "readiness", False, True),
    ("event loop responsive", "liveness", True, False),
    ("not shutting down", "liveness", True, False),
]

PROBES = ["liveness", "readiness"]
rows = list(CHECKS)


def probe_passes(probe):
    return all(ok for _, which, ok, _ in rows if which == probe)


print(f"{len(rows)} checks, {len(PROBES)} probes")
print()
print(f"{'check':<28}{'probe':>12}{'a dependency':>14}{'result':>9}")
print("-" * 63)
for name, probe, ok, dependency in rows:
    print(f"{name:<28}{probe:>12}{('yes' if dependency else 'no'):>14}"
          f"{('ok' if ok else 'FAIL'):>9}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'checks defined':<46}{len(rows):>8}")
for probe in PROBES:
    print(f"{'checks in the ' + probe + ' probe':<46}"
          f"{sum(1 for _, p, _, _ in rows if p == probe):>8}")
for probe in PROBES:
    print(f"{'dependencies the ' + probe + ' probe checks':<46}"
          f"{sum(1 for _, p, _, d in rows if p == probe and d):>8}")
print(f"{'checks currently failing':<46}"
      f"{sum(1 for _, _, ok, _ in rows if not ok):>8}")
print(f"{'liveness passes':<46}"
      f"{('yes' if probe_passes('liveness') else 'no'):>8}")
print(f"{'readiness passes':<46}"
      f"{('yes' if probe_passes('readiness') else 'no'):>8}")

print()
print("The two probes answer different questions and must not share their")
print("checks. Liveness asks whether the process is still able to run, and the")
print("answer decides one thing: restart it. Readiness asks whether it can")
print("serve a request right now, and the answer decides a different thing:")
print("stop sending it traffic, and leave it running.")
print()
print("That is why the dependency counts are the numbers to look at. The")
print("liveness probe checks zero dependencies, so a cache that is down makes")
print("readiness fail and liveness pass -- the instance leaves the load")
print("balancer and is not restarted. If liveness checked the database")
print("instead, a database outage would fail the probe on every healthy")
print("process at the same moment, and the orchestrator would restart the")
print("whole fleet into the same outage. That is how a two-minute blip becomes")
print("an afternoon.")
print()
print("The other rule is about cost. A readiness check runs every few seconds")
print("for the life of the service, so it has to be cheap and it must not be")
print("the thing that fails first. Opening a database connection per call is a")
print("load generator wearing a health check's name; asking the pool for a")
print("connection and returning it is a check.")
