#!/usr/bin/env python3
"""Chapter 48 scenario -- twenty hours, eight topics, and one typo.

A student has an exam in the morning. Eight topics are on the syllabus, each
with an estimated cost in hours and an estimated marks gain, and there are
twenty hours left. That is a 0/1 knapsack, and it is the same table as the
rucksack in the earlier section with the units relabelled.

The second half is a smaller problem that uses a different DP from the same
chapter: the student's revision list has a topic name spelled wrong, and the
syllabus is the dictionary. That is edit distance.
"""
import random


TOPICS = [
    ("mechanics", 8, 45),
    ("electromagnetism", 8, 26),
    ("thermodynamics", 8, 18),
    ("circuits", 5, 33),
    ("waves", 3, 23),
    ("optics", 3, 20),
    ("units", 2, 12),
    ("history", 8, 10),
]
HOURS = 20
SYLLABUS = [name for name, _, _ in TOPICS]


def plan_table(topics, hours):
    """Same recurrence as the rucksack: table[i][h] is the best marks
    obtainable from the first i topics with h hours to spend."""
    n = len(topics)
    table = [[0] * (hours + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        name, cost, marks = topics[i - 1]
        for h in range(hours + 1):
            skip = table[i - 1][h]
            if cost > h:
                table[i][h] = skip
            else:
                table[i][h] = max(skip, table[i - 1][h - cost] + marks)
    return table


def plan_pick(topics, hours, table):
    h = hours
    chosen = []
    for i in range(len(topics), 0, -1):
        if table[i][h] != table[i - 1][h]:
            name, cost, marks = topics[i - 1]
            chosen.append((name, cost, marks))
            h -= cost
    return list(reversed(chosen))


def plan_greedy(topics, hours):
    """The student's instinct: revise whatever gives the most marks per hour
    first."""
    ranked = sorted(topics, key=lambda t: t[2] / t[1], reverse=True)
    chosen, spent = [], 0
    for name, cost, marks in ranked:
        if spent + cost <= hours:
            chosen.append((name, cost, marks))
            spent += cost
    return chosen


table = plan_table(TOPICS, HOURS)
optimal = plan_pick(TOPICS, HOURS, table)
greedy = plan_greedy(TOPICS, HOURS)

print("Part 1 -- the plan")
print()
print(f"  {len(TOPICS)} topics, {HOURS} hours available")
print()
print(f"  {'topic':<18}{'hours':>7}{'marks':>7}{'marks/hour':>13}")
print("-" * 45)
for name, cost, marks in TOPICS:
    print(f"  {name:<18}{cost:>7}{marks:>7}{marks / cost:>13.1f}")
print()
print(f"  {'plan':<18}{'hours':>7}{'marks':>7}{'topics':>9}")
print("-" * 45)
print(f"  {'greedy':<18}{sum(c for _, c, _ in greedy):>7}"
      f"{sum(m for _, _, m in greedy):>7}{len(greedy):>9}")
print(f"  {'optimal':<18}{sum(c for _, c, _ in optimal):>7}"
      f"{sum(m for _, _, m in optimal):>7}{len(optimal):>9}")
print()
print("  greedy picks  :", ", ".join(name for name, _, _ in greedy))
print("  optimal picks :", ", ".join(name for name, _, _ in optimal))
print()
greedy_hours = sum(c for _, c, _ in greedy)
optimal_hours = sum(c for _, c, _ in optimal)
print(f"  the greedy spends {greedy_hours} hours and leaves {HOURS - greedy_hours} unused;")
print(f"  the optimal spends {optimal_hours} and leaves {HOURS - optimal_hours}.")
print()
print("The greedy's *ordering* is not the mistake -- every item it takes is")
print("a reasonable item, and it takes them in the right order. The mistake")
print("is that it commits to four small ones before it ever considers the")
print("single biggest prize on the list, and by then 13 of the 20 hours are")
print("gone while mechanics needs 8. The optimum drops `units`, the")
print("second-smallest item, and spends that room on `mechanics` instead.")
print()
print("That is the whole failure mode in one line: a greedy rule cannot")
print("afford to wait, and the best subset sometimes requires waiting.")
lost = sum(m for _, _, m in optimal) - sum(m for _, _, m in greedy)
print()
print(f"  marks lost to the greedy : {lost} of "
      f"{sum(m for _, _, m in optimal)} "
      f"({100 * lost / sum(m for _, _, m in optimal):.0f}%)")
print()
print(f"{lost} marks out of {sum(m for _, _, m in optimal)} is not a rounding error. The")
print("greedy loses more than a quarter of the achievable total -- and it")
print("loses it while *using less* of the resource. That last part is the")
print("counterintuitive bit, and it is worth sitting with: the greedy plan")
print(f"is not merely worse, it is smaller. It had {HOURS} hours and spent")
print(f"{greedy_hours}, because once the small items were in there was nothing")
print("left that fit.")
print()
print("A student who followed the greedy would finish with four topics")
print("revised, seven hours unused, and no way to tell that the plan was")
print("suboptimal -- the hours went unused one at a time, and each refusal")
print("looked sensible in isolation.")
print()
print()
print("Part 2 -- the typo, and a different DP")


def edit_distance(a, b):
    m, n = len(a), len(b)
    previous = list(range(n + 1))
    for i in range(1, m + 1):
        current = [i] + [0] * n
        for j in range(1, n + 1):
            current[j] = min(previous[j] + 1,
                             current[j - 1] + 1,
                             previous[j - 1] + (a[i - 1] != b[j - 1]))
        previous = current
    return previous[n]


TYPED = "circuts"
print()
print(f"  the revision list says {TYPED!r}")
print()
print(f"  {'syllabus topic':<18}{'distance':>10}")
print("-" * 28)
distances = sorted((edit_distance(TYPED, name), name) for name in SYLLABUS)
for distance, name in distances:
    marker = "  <- closest" if (distance, name) == distances[0] else ""
    print(f"  {name:<18}{distance:>10}{marker}")
print()
print("The answer is not found by comparing lengths or first letters. The")
print("closest topic is the one where the student dropped a single letter,")
print("and the edit distance finds it without being told what a dropped")
print("letter is -- which is the property that makes the recurrence worth")
print("knowing rather than just the answer it produces.")
print()
print("It also handles the cases that a simpler rule does not, and it has a")
print("real limitation worth naming. If the student had swapped two adjacent")
print("letters instead of dropping one, the distance would be 2 rather than")
print("1, because plain Levenshtein has no transposition operation:")
print()
SWAPPED = "cricuits"
print(f"  {'typed':<12}{'closest':>12}{'distance':>10}")
print("-" * 34)
print(f"  {TYPED!r:<12}{'circuits':>12}{edit_distance(TYPED, 'circuits'):>10}")
print(f"  {SWAPPED!r:<12}{'circuits':>12}"
      f"{edit_distance(SWAPPED, 'circuits'):>10}")
print()
print("A transposition is two edits, not one, so a misspelling that is a")
print("single swap costs more than one that is a single omission -- which is")
print("the opposite of what a reader expects. That is not an oversight:")
print("adding a transposition move gives Damerau-Levenshtein, which needs a")
print("larger state and one more lookback in the recurrence. Most spell")
print("checkers use that version; the recurrence here is the one that fits")
print("on a page.")
print()
print("This is the same table as Part 1 with the units changed again. Hours")
print("and marks became characters; the budget became a length. The")
print("recurrence did not change shape, which is the point of the chapter:")
print("once the state is right, the code is almost mechanical.")
print()
print()
print("Part 3 -- why the plan cannot be found by a smarter greedy")
print()
print("It is tempting to look for a better greedy rule -- ratio first, then")
print("longest first, then a tie-break. That search is a dead end, and the")
print("reason is worth stating because it applies to every knapsack-shaped")
print("problem:")
print()
print("  a greedy rule is a rule about one topic at a time, and the value of")
print("  a topic depends on which other topics are in the plan. With 20 hours")
print("  and 8 topics, the choices interact, and no per-topic score can see")
print("  the interaction.")
print()
print("The DP does not need to see it either. It just refuses to commit: it")
print("keeps the best answer for *every* budget, so when the last topic is")
print("considered the answer for 20 hours is already sitting in the table,")
print("built out of answers for 15 and 14 hours, which were built out of")
print("smaller ones. The interaction is encoded in the second index.")
print()
count = 0
for hours in range(1, 31):
    t = plan_table(TOPICS, hours)
    g = plan_greedy(TOPICS, hours)
    if t[len(TOPICS)][hours] != sum(m for _, _, m in g):
        count += 1
print(f"  budgets 1..30 hours, greedy disagrees with the DP on {count} of them")
print()
print(f"{count} of 30 budgets -- {100 * count / 30:.0f}% of the range -- from the same eight")
print("topics. The failure is not a corner case at one awkward budget; it is")
print("the ordinary behaviour of the rule.")


# A check the reader can see: the DP answer is an upper bound on the greedy
# one, always, because the greedy plan is a valid plan.
rng = random.Random(4)
violations = 0
for _ in range(200):
    topics = [(f"t{i}", rng.randint(1, 9), rng.randint(5, 50))
              for i in range(rng.randint(3, 8))]
    hours = rng.randint(5, 25)
    t = plan_table(topics, hours)
    g = plan_greedy(topics, hours)
    if sum(m for _, _, m in g) > t[len(topics)][hours]:
        violations += 1
print()
print(f"  200 random instances, greedy beating the DP : {violations}")
print("  (it cannot: the greedy plan is a legal plan, so the DP's optimum is")
print("   at least as good. A greedy that wins would mean the DP was wrong.)")
