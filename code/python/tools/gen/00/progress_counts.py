"""Chapter 00 -- a progress list is only useful if you count what is missing.

A tracker for the first twelve chapters, kept by hand. The count is of chapters
in each state, and of the chapters that have no state at all.
"""

CHAPTERS = [
    "01-getting-started", "02-variables-and-types", "03-strings-and-formatting",
    "04-control-flow", "05-collections", "06-functions", "07-comprehensions",
    "08-files-and-paths", "09-errors-and-exceptions", "10-modules-and-venv",
    "11-testing-and-debugging", "12-oop-i",
]

# The state of each chapter, as it was written down after each session. Three
# chapters are missing because they were added to the book after the list was
# started and nobody went back to it.
STATUS = {
    "01-getting-started": "done",
    "02-variables-and-types": "done",
    "03-strings-and-formatting": "done",
    "04-control-flow": "done",
    "05-collections": "in progress",
    "06-functions": "in progress",
    "07-comprehensions": "in progress",
    "08-files-and-paths": "untouched",
    "09-errors-and-exceptions": "untouched",
}

STATES = ["done", "in progress", "untouched"]

missing = [name for name in CHAPTERS if name not in STATUS]
unknown = sorted({state for state in STATUS.values()} - set(STATES))

print(f"{len(CHAPTERS)} chapters, {len(STATUS)} of them written down")
print()
print(f"{'state':<20}{'chapters':>10}")
print("-" * 30)
for state in STATES:
    print(f"{state:<20}{sum(1 for v in STATUS.values() if v == state):>10}")
print(f"{'(no state)':<20}{len(missing):>10}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'chapters in the book':<46}{len(CHAPTERS):>8}")
print(f"{'chapters with a state':<46}{len(STATUS):>8}")
print(f"{'chapters with no state':<46}{len(missing):>8}")
print(f"{'distinct states used':<46}{len(set(STATUS.values())):>8}")
print(f"{'states the tracker defines':<46}{len(STATES):>8}")
print(f"{'states used but not defined':<46}{len(unknown):>8}")
for state in STATES:
    print(f"{'chapters marked ' + state:<46}"
          f"{sum(1 for v in STATUS.values() if v == state):>8}")
print(f"{'share of the book with a state':<46}"
      f"{round(100 * len(STATUS) / len(CHAPTERS)):>7}%")

print()
print("The last line of the table is the one a hand-kept tracker never shows you,")
print("and it is the only number that matters. Three chapters have no state at")
print("all -- not 'untouched', which is a decision, but absent, which is not.")
print("They were added to the book after the list was started, and a list cannot")
print("tell you about a row that was never written.")
print()
print("So the useful measurement is not how many chapters are done. It is the")
print("difference between the number of chapters that exist and the number the")
print("tracker knows about, and it only works if both numbers come from somewhere")
print("other than the tracker. A list that counts itself is always complete.")
print()
print("That is the same discipline as the examples in this book, applied to your")
print("own work. Keep the list next to the thing it describes rather than in place")
print("of it, count the gap in both directions, and treat a chapter that is")
print("missing as more interesting than one that is late -- being late is a")
print("schedule, and being missing is a blind spot.")
