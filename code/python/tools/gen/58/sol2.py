"""Solution 2 -- deciding between two sorts that both claim to be n log n.

Both are counted at four sizes and the ratios decide. The claim is true
for one of them and false for the other.
"""

SIZES = [200, 400, 800, 1600]


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
        count[0] += 1
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def insertion_sort(items, count):
    out = list(items)
    for i in range(1, len(out)):
        value = out[i]
        j = i - 1
        while j >= 0:
            count[0] += 1
            if out[j] <= value:
                break
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = value
    return out


SORTS = [
    ("merge sort", merge_sort),
    ("insertion sort", insertion_sort),
]


def main():
    print(f"  sizes                               {len(SIZES)}")
    print()
    counts = {name: [] for name, _ in SORTS}
    print("    size       merge sort   insertion sort")
    for size in SIZES:
        items = list(range(size, 0, -1))
        cells = []
        for name, sort in SORTS:
            count = [0]
            sort(items, count)
            counts[name].append(count[0])
            cells.append(count[0])
        print("    {:>6}{:>15}{:>17}".format(size, *cells))
    print()

    print("    growth when the size doubles")
    print("    {:<18}{:>9}   {}".format("", "ratio", "shape"))
    verdict = {}
    for name, _ in SORTS:
        series = counts[name]
        ratios = [series[i + 1] / series[i] for i in range(len(series) - 1)]
        average = sum(ratios) / len(ratios)
        shape = "n log n" if average < 2.6 else "quadratic"
        verdict[name] = (average, shape)
        print("    {:<18}{:>8.2f}x   {}".format(name, average, shape))
    print()

    wrong = [name for name, _ in SORTS if verdict[name][1] != "n log n"]
    good = "merge sort"
    bad = wrong[0]
    print(f"  the claim under test is that both are n log n, and the ratios")
    print(f"  reject it for {len(wrong)} of the {len(SORTS)}: {', '.join(wrong)}.")
    print()
    print("  the counts are exact integers, so the verdict does not depend on")
    print("  the machine, on the interpreter, or on how many times the program")
    print(f"  was run. Doubling the size multiplies merge sort's comparisons by")
    print(f"  {verdict[good][0]:.2f} and multiplies insertion sort's by {verdict[bad][0]:.2f}.")
    print()
    print("  the reverse-ordered input is the case insertion sort is worst at,")
    print("  and that is deliberate. A benchmark that runs the best case is")
    print("  the pitfall from earlier in this chapter wearing a different hat.")
    print("  An average over random inputs would land between the two, and a")
    print("  number between two complexity classes is not one of them.")
    print()
    print("  the first size already shows the two are different, and it cannot")
    print(f"  show why. At {SIZES[0]} the counts differ by a factor of")
    print(f"  {counts['insertion sort'][0] / counts['merge sort'][0]:.1f}, and at {SIZES[-1]} by")
    print(f"  {counts['insertion sort'][-1] / counts['merge sort'][-1]:.0f}. A single size cannot tell you which of those")
    print("  factors keeps growing, and the ratios can. A claim about growth")
    print("  needs at least three sizes to check and four to be sure the last")
    print("  ratio is not a fluke.")


main()
