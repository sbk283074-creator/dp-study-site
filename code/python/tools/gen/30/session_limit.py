"""Chapter 30 -- a daily limit is a choice about which cards you see.

Twenty cards with known due dates and a session limit of eight. The count is of
cards shown each day, and of the backlog the limit creates.
"""

DUE_OFFSETS = [0] * 12 + [1] * 5 + [2] * 3
LIMIT = 8
DAYS = 4

backlog = 0
rows = []
for day in range(DAYS):
    arriving = sum(1 for offset in DUE_OFFSETS if offset == day)
    due = backlog + arriving
    shown = min(LIMIT, due)
    backlog = due - shown
    rows.append((day + 1, arriving, due, shown, backlog))

first_day_due = rows[0][2]
cleared = next((day for day, _, _, _, left in rows if left == 0), None)

print(f"{len(DUE_OFFSETS)} cards and a session limit of {LIMIT}")
print()
print(f"{'day':<6}{'becoming due':>14}{'due':>8}{'shown':>8}{'backlog after':>16}")
print("-" * 52)
for day, arriving, due, shown, left in rows:
    print(f"{day:<6}{arriving:>14}{due:>8}{shown:>8}{left:>16}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'cards in the deck':<46}{len(DUE_OFFSETS):>8}")
print(f"{'cards due on the first day':<46}{first_day_due:>8}")
print(f"{'session limit':<46}{LIMIT:>8}")
print(f"{'limit needed to clear the first day':<46}{first_day_due:>8}")
print(f"{'days before the backlog clears':<46}{cleared:>8}")
print(f"{'cards shown over the four days':<46}"
      f"{sum(r[3] for r in rows):>8}")
print(f"{'cards never shown':<46}{len(DUE_OFFSETS) - sum(r[3] for r in rows):>8}")

print()
print("Every card is shown eventually -- the limit delays the session rather")
print("than dropping the card -- and that is the whole difference between a")
print("limit and a filter. Twelve cards due on the first day and a limit of")
print("eight leaves four waiting, so a card that came due today is shown")
print("tomorrow, and the backlog is carried rather than discarded.")
print()
print("The number that matters is the third one, because it decides what the")
print("user is told. A dashboard that says 'twelve cards due' is describing the")
print("queue; one that says 'eight cards today, four carried over' is")
print("describing the session. Only the second one is a promise the app can")
print("keep, and the first is how a study app teaches people to stop opening")
print("it.")
print()
print("And the choice of which eight is the real design decision, not the")
print("limit. Showing the oldest first clears the backlog, which is what the")
print("table above does. Showing the newest first starves the oldest cards")
print("permanently -- they stay at the front of the queue while every new card")
print("goes ahead of them, and the backlog never clears. The limit is")
print("arithmetic; the order is the product.")
