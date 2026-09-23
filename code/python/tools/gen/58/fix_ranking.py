"""Chapter 58 -- the order to make the fixes in.

Six fixes to one report, each with the work it removes and the lines it
changes. Both of those are counted, so the order is not a matter of taste.
"""

TOTAL_WORK = 206970

# name, work removed, lines changed
FIXES = [
    ("a join for the string", 184335, 2),
    ("a global memo", 60000, 40),
    ("a set for the dedupe", 19700, 3),
    ("a check off the hot path", 400, 1),
    ("a cached format string", 200, 4),
    ("fewer rows to start with", 200, 6),
]


def per_line(fix):
    return fix[1] / fix[2]


def main():
    print(f"  work in the report                 {TOTAL_WORK}")
    print(f"  fixes considered                    {len(FIXES)}")
    print()
    print("    {:<33}{:>11}{:>8}{:>11}".format("fix", "work removed", "lines",
                                                "per line"))
    for name, work, lines in FIXES:
        print("    {:<33}{:>11}{:>8}{:>11.0f}".format(name, work, lines,
                                                   work / lines))
    print()

    by_work = sorted(FIXES, key=lambda fix: -fix[1])
    by_line = sorted(FIXES, key=lambda fix: -per_line(fix))
    print("    {:<24}{:>10}   {:<24}{:>10}".format(
        "ranked by work removed", "", "ranked by work per line", ""))
    for left, right in zip(by_work, by_line):
        print("    {:<24}{:>10}   {:<24}{:>10.0f}".format(
            left[0], left[1], right[0], per_line(right)))
    print()

    moved = [index for index, (left, right) in
             enumerate(zip(by_work, by_line), 1) if left[0] != right[0]]
    print(f"  the two orders disagree in {len(moved)} of the {len(FIXES)} positions.")
    print()

    top = by_work[0]
    second = by_work[1]
    alt = by_line[1]
    print(f"  both orders put `{top[0]}` first, and it is the one")
    print(f"  everybody finds: {top[1]} units and {top[2]} lines.")
    print()
    print(f"  they part company at the second move. `{second[0]}` removes")
    print(f"  {second[1]} units in {second[2]} lines; `{alt[0]}` removes {alt[1]} in")
    print(f"  {alt[2]}. The first is worth {second[1] / alt[1]:.1f} times the work and costs")
    print(f"  {second[2] / alt[2]:.1f} times the lines, so per line it is the worse of the")
    print(f"  two -- {per_line(second):.0f} against {per_line(alt):.0f}.")
    print()
    print("  the ranking to use is the second one, and the reason is not that")
    print("  small changes are safer. It is that a fix has to survive review")
    print("  before it removes anything, and the lines changed is the part of")
    print("  that cost which is countable. Work removed per line changed is a")
    print("  real ratio, and it is the one that orders the list here.")
    print()
    print("  the two fixes at the bottom are the ones a reader reaches for")
    print("  first, because they are the ones with an obvious better spelling.")
    print(f"  Together they are {FIXES[4][1] + FIXES[5][1]} units out of {TOTAL_WORK}, so the")
    print("  order they appear in does not matter at all.")


main()
