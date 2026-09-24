"""Chapter 62 -- a plan is arithmetic, and it has to reconcile with its list.

Thirty days of work, written down the way a plan gets written down. The count is
of days covered, of days carrying more than one topic, and of the gap between
what the plan claims and what it lists.
"""

DAYS_IN_MONTH = 30

# What the plan says about itself, in the sentence at the top of it.
CLAIMED_DAYS = 30
CLAIMED_TOPICS = 30

# (day, topic). Four days carry two topics, which is how the list grew past the
# sentence above it without anybody noticing.
PLAN = [
    (1, "variables and types"), (2, "strings and formatting"),
    (3, "control flow"), (4, "collections"),
    (5, "functions"), (6, "comprehensions"), (6, "generators"),
    (7, "files and paths"), (8, "errors and exceptions"),
    (9, "modules and imports"), (10, "testing"),
    (11, "classes and attributes"), (12, "dunder methods"),
    (13, "inheritance"), (13, "composition"),
    (14, "dataclasses"), (15, "typing"), (16, "the standard library"),
    (17, "regular expressions"), (18, "dates and times"),
    (19, "csv and json"), (20, "sqlite"), (20, "an ORM by hand"),
    (21, "http and requests"), (22, "an API client"),
    (23, "concurrency"), (24, "asyncio"),
    (25, "packaging"), (26, "a command-line tool"),
    (27, "profiling"), (27, "optimisation"),
    (28, "logging"), (29, "deployment"), (30, "a project of your own"),
]

entries = len(PLAN)
days_used = {day for day, _ in PLAN}
busy_days = sorted(day for day in days_used
                   if sum(1 for other, _ in PLAN if other == day) > 1)
empty_days = sorted(set(range(1, DAYS_IN_MONTH + 1)) - days_used)
topics = [topic for _, topic in PLAN]
repeated = sorted({topic for topic in topics if topics.count(topic) > 1})

print(f"a {DAYS_IN_MONTH}-day plan, {entries} entries")
print()
print(f"{'day':>4}   topics")
print("-" * 40)
for day in sorted(days_used):
    on_day = [topic for other, topic in PLAN if other == day]
    print(f"{day:>4}   {', '.join(on_day)}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'days in the month':<46}{DAYS_IN_MONTH:>8}")
print(f"{'days the plan claims to fill':<46}{CLAIMED_DAYS:>8}")
print(f"{'topics the plan claims to cover':<46}{CLAIMED_TOPICS:>8}")
print(f"{'entries in the list':<46}{entries:>8}")
print(f"{'days the list actually fills':<46}{len(days_used):>8}")
print(f"{'days carrying more than one topic':<46}{len(busy_days):>8}")
print(f"{'days with nothing on them':<46}{len(empty_days):>8}")
print(f"{'distinct topics':<46}{len(set(topics)):>8}")
print(f"{'topics listed more than once':<46}{len(repeated):>8}")
print(f"{'entries beyond the claim':<46}{entries - CLAIMED_TOPICS:>8}")
print(f"{'the plan reconciles':<46}"
      f"{int(entries == CLAIMED_TOPICS and len(days_used) == CLAIMED_DAYS):>8}")

print()
print("The list is fine and the sentence above it is wrong, which is the usual")
print("way a plan fails. Thirty days are filled, so the day count reconciles;")
print(f"thirty-four topics are listed, so the topic count does not. Four days carry")
print("two entries -- days " + ", ".join(str(day) for day in busy_days) + " -- and")
print("the sentence was written before they were.")
print()
print("None of this is a problem with the plan. It is a problem with reading the")
print("plan's summary instead of the plan. A number at the top of a document is")
print("a claim about the document, and it stops being true the moment the")
print("document changes, silently, because nothing connects the two.")
print()
print("Which is why the useful habit at the end of a book is the same one it")
print("started with. Count the thing rather than repeating what was said about")
print("it: days filled against days available, topics listed against topics")
print("claimed, entries against slots. The plan above is a good thirty days of")
print("work. It is just not the thirty days it says it is, and the difference is")
print("four topics that would have been found in ten seconds by anyone who")
print("counted.")
