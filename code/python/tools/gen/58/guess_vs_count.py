"""Chapter 58 -- where the work is, counted rather than guessed.

A four-phase report in which every phase counts two things: how many
times its loop ran, and how much work it did inside. The first column is
identical for all four phases and the second is not.
"""

ROWS = 400


def load(count):
    out = []
    for i in range(ROWS):
        count["rows"] += 1
        count["work"] += 1
        out.append({"id": i, "name": "row-%d" % i, "value": i % 17})
    return out


def validate(rows, count):
    """Touches every row and keeps every row, so the loop counts stay
    comparable with the phases on either side of it."""
    for row in rows:
        count["rows"] += 1
        count["work"] += 1
        if not isinstance(row["value"], int):
            raise TypeError("value")
    return rows


def render(rows, count):
    out = []
    for row in rows:
        count["rows"] += 1
        count["work"] += 1
        out.append("%s=%s" % (row["name"], row["value"]))
    return out


def join_all(lines, count):
    """The phase whose loop count says nothing about its cost."""
    out = ""
    for line in lines:
        count["rows"] += 1
        count["work"] += len(out)
        out += line + "\n"
    return out


PHASES = [
    ("load", load),
    ("validate", validate),
    ("render", render),
    ("join", join_all),
]


def run():
    counts = {}
    rows = None
    for name, phase in PHASES:
        counts[name] = {"rows": 0, "work": 0}
        if name == "load":
            rows = phase(counts[name])
        else:
            rows = phase(rows, counts[name])
    return counts


def main():
    counts = run()
    print(f"  rows                                {ROWS}")
    print(f"  phases                              {len(PHASES)}")
    print()
    print("    phase      loop iterations   work units   share of the work")
    total = sum(counts[name]["work"] for name, _ in PHASES)
    for name, _ in PHASES:
        share = 100.0 * counts[name]["work"] / total
        print("    {:<11}{:>15}{:>13}{:>15.1f}%".format(
            name, counts[name]["rows"], counts[name]["work"], share))
    print("    {:<11}{:>15}{:>13}{:>15}".format(
        "total", sum(counts[name]["rows"] for name, _ in PHASES), total,
        "100.0%"))
    print()

    print("    the order the loop counts give you")
    for index, (name, _) in enumerate(
            sorted(PHASES, key=lambda p: -counts[p[0]]["rows"]), 1):
        print("    {:<3}{:<12}{:>8}".format(index, name,
                                           counts[name]["rows"]))
    print("    every phase is 400, so this ranking is the order the phases")
    print("    happen to be written in and nothing more.")
    print()

    print("    the order the work counts give you")
    ranked = sorted(PHASES, key=lambda p: -counts[p[0]]["work"])
    for index, (name, _) in enumerate(ranked, 1):
        print("    {:<3}{:<12}{:>10}".format(index, name,
                                             counts[name]["work"]))
    print()

    heaviest = ranked[0][0]
    lightest = ranked[-1][0]
    ratio = counts[heaviest]["work"] / counts[lightest]["work"]
    print(f"  every phase ran its loop exactly {ROWS} times, so the loop count")
    print("  is identical for all four and cannot rank them at all. the work")
    print(f"  count says `{heaviest}` does {ratio:.0f} times the work of")
    print(f"  `{lightest}`, and it is the phase written in one line.")
    print()
    print("  the reason is in the statement the counter sits next to. `join`")
    print("  copies the whole string it has built so far on every iteration,")
    print("  so its work is the sum of all the lengths rather than the number")
    print("  of lines. counting iterations cannot see that, and counting")
    print("  iterations is what a first measurement usually does.")
    print()
    print("  so the first question about any measurement is what unit it")
    print("  counts. a count of loop trips counts how often the code was")
    print("  reached, not what it did, and the two agree only when every trip")
    print("  does the same amount of work -- which is exactly the assumption")
    print("  a slow loop tends to break.")


main()
