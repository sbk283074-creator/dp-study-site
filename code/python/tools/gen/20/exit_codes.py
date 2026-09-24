"""Chapter 20 -- the exit code is the only part of the output a scheduler reads.

Five runs of the same job: one that worked, one that found nothing to do, and
three that failed in different ways. Each is reported by a tool that always
exits 0 and by one that says what happened. The count is of failures the caller
can actually see.
"""

RUNS = [
    ("everything worked", "success"),
    ("no files matched the pattern", "nothing to do"),
    ("the input directory does not exist", "bad input"),
    ("permission denied writing the report", "bad environment"),
    ("the remote API returned 500", "transient failure"),
]

CODES = {
    "success": 0,
    "nothing to do": 0,
    "bad input": 2,
    "bad environment": 3,
    "transient failure": 75,
}

FAILURES = [kind for _, kind in RUNS if kind != "success" and kind != "nothing to do"]


def always_zero(kind):
    return 0


def honest(kind):
    return CODES[kind]


def visible(exit_code):
    return exit_code != 0


print(f"{len(RUNS)} runs of one job")
print()
print(f"{'run':<38}{'kind':>18}{'always 0':>10}{'honest':>8}")
print("-" * 74)
for label, kind in RUNS:
    print(f"{label:<38}{kind:>18}{always_zero(kind):>10}{honest(kind):>8}")

print()
print(f"{'what is counted':<40}{'always 0':>12}{'honest':>8}")
print("-" * 60)
print(f"{'runs':<40}{len(RUNS):>12}{len(RUNS):>8}")
print(f"{'runs that failed':<40}{len(FAILURES):>12}{len(FAILURES):>8}")
print(f"{'failures the caller can see':<40}"
      f"{sum(visible(always_zero(k)) for _, k in RUNS if k in FAILURES):>12}"
      f"{sum(visible(honest(k)) for _, k in RUNS if k in FAILURES):>8}")
print(f"{'distinct exit codes used':<40}{1:>12}{len(set(CODES.values())):>8}")
print(f"{'codes that mean try again later':<40}{0:>12}{1:>8}")

print()
print("A tool that always exits 0 is not lying about the work, it is lying")
print("about the outcome. That column holds the same number on every row, so")
print("whatever the job did, the caller sees one value. Under cron, or in a")
print("shell chain, or as a step in CI, that value is the whole report -- the")
print("job is not read, it is trusted.")
print()
print(f"The honest column carries {len(set(CODES.values()))} distinct codes, and the shape of them is the")
print("point. Zero means it worked. A small number means the caller asked for")
print("something impossible, which no amount of retrying fixes. 75 means the")
print("job could not run and should be tried again later -- that is the one")
print("that separates a transient failure from a permanent one, and it is the")
print("difference between a retry loop that helps and one that hammers a")
print("broken endpoint forever.")
print()
print("So write the exit code first and the message second. The message is for")
print("the person who runs it by hand; the code is for everything that runs it")
print("without one. And when the job is a chain, `set -e` or `&&` is what makes")
print("the code load-bearing -- a step that fails must stop the steps after it,")
print("or the code is decoration.")
