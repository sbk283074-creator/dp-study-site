"""Chapter 58 -- the scenario. A slow report.

Five phases, each counting its own work, and four candidate fixes. The
count is of the work each fix removes, which is what decides the order to
try them in.
"""

ROWS = 200


def load(count):
    out = []
    for i in range(ROWS):
        count["load"] += 1
        out.append({"id": i, "name": "row-%d" % i, "v": i % 13})
    return out


def dedupe(rows, count):
    """Every row against every row already kept."""
    kept = []
    for row in rows:
        for other in kept:
            count["dedupe"] += 1
            if other["id"] == row["id"]:
                break
        else:
            kept.append(row)
    return kept


def render(rows, count):
    out = []
    for row in rows:
        count["render"] += 1
        out.append("%s=%d" % (row["name"], row["v"]))
    return out


def join_all(lines, count):
    out = ""
    for line in lines:
        count["join"] += len(out)
        out += line + "\n"
    return out


def write(text, count):
    for _line in text.splitlines():
        count["write"] += 1
    return len(text)


PHASES = [
    ("load", load),
    ("dedupe", dedupe),
    ("render", render),
    ("join", join_all),
    ("write", write),
]


def measure():
    count = {name: 0 for name, _ in PHASES}
    rows = None
    for name, phase in PHASES:
        if name == "load":
            rows = phase(count)
        elif name == "write":
            phase(rows, count)
        else:
            rows = phase(rows, count)
    return count


def fixed_dedupe():
    count = {name: 0 for name, _ in PHASES}
    count["load"] = ROWS
    rows = [{"id": i, "name": "row-%d" % i, "v": i % 13} for i in range(ROWS)]
    seen = set()
    for row in rows:
        count["dedupe"] += 1
        seen.add(row["id"])
    return count


def fixed_join():
    lines = ["row-%d=%d" % (i, i % 13) for i in range(ROWS)]
    out = "".join(line + "\n" for line in lines)
    count = {name: 0 for name, _ in PHASES}
    count["join"] = len(out) + ROWS
    return count


def main():
    count = measure()
    total = sum(count.values())
    print(f"  rows                                {ROWS}")
    print(f"  phases                              {len(PHASES)}")
    print()
    print("    phase      work units   share")
    for name, _ in PHASES:
        share = 100.0 * count[name] / total
        print("    {:<11}{:>10}{:>9.1f}%".format(name, count[name], share))
    print("    {:<11}{:>10}{:>9}".format("total", total, "100.0%"))
    print()

    print("    the work each candidate fix removes")
    fixes = []
    dedupe = fixed_dedupe()
    removed = count["dedupe"] - dedupe["dedupe"]
    fixes.append(("a set for the dedupe", removed))
    join = fixed_join()
    removed_join = count["join"] - join["join"]
    fixes.append(("a join for the string", removed_join))
    fixes.append(("a cached format string", count["render"]))
    fixes.append(("fewer rows to start with", count["load"]))
    for name, removed in sorted(fixes, key=lambda f: -f[1]):
        print("    {:<30}{:>10}  {:.1f}% of the total".format(
            name, removed, 100.0 * removed / total))
    print()

    ranked = sorted(fixes, key=lambda f: -f[1])
    print(f"  `{ranked[0][0]}` removes {ranked[0][1]} work units and")
    print(f"  `{ranked[-1][0]}` removes {ranked[-1][1]}, so the order to try")
    print("  them in is not the order they look easiest in.")
    print()
    print("  the two that matter are both loops that look like one line. the")
    print("  dedupe is a nested loop with a `break`, which reads as a scan")
    print("  and is quadratic; the join is a `+=` on a string, which reads as")
    print("  an append and copies the whole string every time. neither is")
    print("  visible by reading, and both are visible by counting.")
    print()
    print("  the two that do not matter are the ones a reader would reach for")
    print("  first, because they are the ones with an obvious better")
    print("  spelling. the format string can be cached and the row count can")
    print("  be trimmed, and together they are a few hundred units out of a")
    print("  number in the hundreds of thousands.")
    print()
    print("  that is the whole reason to measure before optimising. the four")
    print("  fixes are all correct, all worth doing eventually, and only two")
    print("  of them change the answer.")


main()
