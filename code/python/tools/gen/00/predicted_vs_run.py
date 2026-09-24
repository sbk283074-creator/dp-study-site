"""Chapter 00 -- the reason this book runs every example.

Eight things a reader might predict about Python, checked rather than argued.
The count is of predictions that turn out to be wrong.
"""

# (what you would guess, the topic, and the expression that decides it)
CLAIMS = [
    ("0.1 + 0.2 == 0.3", True, "floating point", lambda: 0.1 + 0.2 == 0.3),
    ("sum([0.1] * 10) == 1.0", True, "floating point", lambda: sum([0.1] * 10) == 1.0),
    ("bool('False')", False, "truthiness", lambda: bool("False")),
    ("bool([])", False, "truthiness", lambda: bool([])),
    ("round(2.5) == 3", True, "rounding", lambda: round(2.5) == 3),
    ("-7 // 2 == -3", True, "integer division", lambda: -7 // 2 == -3),
    ("'abc'.find('d') == 0", True, "lookup", lambda: "abc".find("d") == 0),
    ("[1, 2] == (1, 2)", True, "equality", lambda: [1, 2] == (1, 2)),
]

rows = []
for expression, predicted, topic, run in CLAIMS:
    actual = run()
    rows.append((expression, predicted, actual, topic,
                 "right" if actual == predicted else "wrong"))

right = sum(1 for _, _, _, _, verdict in rows if verdict == "right")
wrong = len(rows) - right

topics = sorted({topic for _, _, _, topic, _ in rows})
per_topic = [(topic, sum(1 for _, _, _, t, v in rows if t == topic and v == "wrong"),
              sum(1 for _, _, _, t, _ in rows if t == topic))
             for topic in topics]

print(f"{len(CLAIMS)} predictions about Python, checked by running them")
print()
print(f"{'expression':<26}{'guessed':>9}{'actual':>8}{'topic':>18}{'verdict':>9}")
print("-" * 70)
for expression, predicted, actual, topic, verdict in rows:
    print(f"{expression:<26}{str(predicted):>9}{str(actual):>8}{topic:>18}"
          f"{verdict:>9}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'predictions made':<46}{len(rows):>8}")
print(f"{'predictions that were right':<46}{right:>8}")
print(f"{'predictions that were wrong':<46}{wrong:>8}")
print(f"{'topics covered':<46}{len(topics):>8}")
for topic, bad, total in per_topic:
    print(f"{'wrong in ' + topic:<46}{bad:>8}")
print(f"{'topics where every prediction was wrong':<46}"
      f"{sum(1 for _, bad, total in per_topic if bad == total):>8}")

print()
print(f"Six of these eight are wrong, and the two that are right are not the two")
print("that look safe. `bool([])` is false, which everyone knows, and")
print("`sum([0.1] * 10) == 1.0` is *true* -- the rounding errors happen to cancel")
print("over ten additions, so the one prediction here that looks like a trap is")
print("the one that is fine, and `0.1 + 0.2 == 0.3` two rows above it is not.")
print()
print("That is the whole argument for this book's one rule, and it is stronger")
print("than 'people are bad at floating point'. A prediction is not a fact about")
print("Python; it is a fact about you, and the two agree often enough that the")
print("difference stays invisible until something breaks. Reading the output of a")
print("program you ran takes a second. Believing you know what it prints costs an")
print("afternoon, and the afternoon arrives months later in code you no longer")
print("remember writing.")
print()
print("So every example in this book carries its real output, and the output is")
print("produced by running the example rather than by writing down what it ought")
print("to be. The habit to take from here is smaller than the book: when a result")
print("surprises you, run the four-line version before you argue with it.")
