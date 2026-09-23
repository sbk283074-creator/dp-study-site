"""Solution 1 -- which of five loops to fix.

A report builder is instrumented by counting rather than by timing. The
count is of the work each of its five loops does, in the unit that loop
works in.
"""

ROWS = 200


def build(rows, count):
    parsed = []
    for row in rows:
        count["parse"] += 1
        parsed.append(row.split(","))
    kept = []
    for row in parsed:
        for other in kept:
            count["dedupe"] += 1
            if other[0] == row[0]:
                break
        else:
            kept.append(row)
    enriched = []
    for row in kept:
        count["enrich"] += 1
        enriched.append({"id": row[0], "n": len(row)})
    ordered = merge_sort(enriched, count)
    lines = []
    for row in ordered:
        count["format"] += 1
        lines.append("%s:%d" % (row["id"], row["n"]))
    return lines


def merge_sort(items, count):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], count)
    right = merge_sort(items[mid:], count)
    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        count["sort"] += 1
        if left[i]["id"] <= right[j]["id"]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


LOOPS = ["parse", "dedupe", "enrich", "sort", "format"]


def main():
    rows = ["id-%d,%d" % (i, i % 7) for i in range(ROWS)]
    count = {name: 0 for name in LOOPS}
    lines = build(rows, count)
    total = sum(count.values())
    print(f"  rows                                {ROWS}")
    print(f"  lines produced                      {len(lines)}")
    print()
    print("    loop        work units   share")
    for name in LOOPS:
        print("    {:<12}{:>10}{:>9.1f}%".format(name, count[name],
                                                100.0 * count[name] / total))
    print("    {:<12}{:>10}{:>9}".format("total", total, "100.0%"))
    print()

    ranked = sorted(LOOPS, key=lambda name: -count[name])
    top = ranked[0]
    per_row = [name for name in LOOPS if name != top and count[name] == ROWS]
    sort_name = [name for name in LOOPS if name not in per_row and name != top][0]
    print(f"  `{top}` does {count[top]} of the {total} units, {100.0 * count[top] / total:.1f}% of the")
    print(f"  work. The other four together do {total - count[top]}.")
    print()
    print(f"  {len(per_row)} of those four do exactly {ROWS} units, one per row, and the")
    print(f"  fourth is `{sort_name}` at {count[sort_name]}, or about {count[sort_name] // ROWS}")
    print(f"  units per row. Only `{top}` grows with the square of the row")
    print("  count, and it is the only one of the five that contains a")
    print("  second loop.")
    print()
    print("  that is the answer the instrumentation was there to produce, and")
    print("  it is not visible in the source. Four of the five loops are two")
    print("  or three lines and the fifth is two or three lines as well; the")
    print("  difference is that one of them compares a row against rows")
    print("  already kept, so its count grows with the square.")
    print()
    print("  the fix replaces the kept-list scan with a set of the ids seen")
    print(f"  so far. `{top}` then costs {ROWS} units like the others and the report")
    print(f"  falls from {total} units to about {total - count[top] + ROWS}. Nothing else in")
    print("  the function needs to change, and the counts are what says so.")


main()
