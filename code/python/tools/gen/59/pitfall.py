"""Chapter 59 -- the cache whose key is different every time.

Five cache designs over fifty calls that alternate between two arguments.
The count is of answers that came back computed for the wrong arguments,
and of entries that can never be found again.
"""

CALLS = 50
ARGS = [7, 8]
STAMP = [0]


def value(arg):
    return arg * 3


def on_the_arguments(args, cache):
    if args not in cache:
        cache[args] = value(args[0])
    return cache[args]


def on_the_text(args, cache):
    key = str(args)
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


def on_the_length(args, cache):
    key = len(args)
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


def on_a_changing_number(args, cache):
    """The key includes a value that is different on every call."""
    STAMP[0] += 1
    key = (args, STAMP[0])
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


def on_a_list(args, cache):
    key = list(args)
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


DESIGNS = [
    ("the arguments", on_the_arguments),
    ("the arguments as text", on_the_text),
    ("how many arguments there are", on_the_length),
    ("the arguments plus a counter", on_a_changing_number),
    ("the arguments as a list", on_a_list),
]


def main():
    print(f"  calls                               {CALLS}")
    print(f"  arguments alternate between         {ARGS}")
    print()
    print("    what the key is                correct   wrong   entries   verdict")
    results = {}
    for name, design in DESIGNS:
        cache = {}
        correct = 0
        wrong = 0
        raised = ""
        for index in range(CALLS):
            arg = ARGS[index % len(ARGS)]
            try:
                got = design((arg,), cache)
            except TypeError as exc:
                raised = type(exc).__name__
                break
            if got == value(arg):
                correct += 1
            else:
                wrong += 1
        if raised:
            verdict = raised
            correct = 0
        elif wrong:
            verdict = "wrong answers"
        else:
            verdict = "correct"
        results[name] = (correct, wrong, len(cache), verdict)
        print("    {:<30}{:>8}{:>8}{:>10}   {}".format(
            name, correct, wrong, len(cache), verdict))
    print()

    bad = [name for name, row in results.items() if row[1] > 0]
    dead = [name for name, row in results.items() if row[2] == CALLS]
    print(f"  {len(bad)} of the {len(DESIGNS)} designs answers the wrong question on half the")
    print(f"  calls, and it is not the one with the worst key.")
    print()
    print("  `how many arguments there are` is the one to look at. Both")
    print(f"  arguments are one element long, so the key is {1} every time, and the")
    print("  second argument is served the first argument's answer for the rest")
    print(f"  of the run: {results['how many arguments there are'][1]} answers out of {CALLS} that no cache")
    print("  reports as anything other than a hit.")
    print()
    print(f"  `the arguments plus a counter` is the opposite failure and it is")
    print(f"  the one that looks harmless. It is never wrong, and it holds")
    print(f"  {results['the arguments plus a counter'][2]} entries for {CALLS} calls, because every call builds a key")
    print("  that no later call can produce. That is a memory leak with a hit")
    print("  rate of zero, and it is the reason a cache should be bounded even")
    print("  when it is correct.")
    print()
    print("  the last row raises `TypeError`, which makes it the only design")
    print("  here that fails loudly. A key has to be hashable and a list is not,")
    print("  so a mutable argument cannot survive a single call -- which makes")
    print("  it the least dangerous mistake on this list, because it is the only")
    print("  one a test would catch on the first line.")
    print()
    print("  none of the five is separated by a hit count. Two of them answer")
    print(f"  every call correctly and one of those never reuses an entry: {len(dead)} of")
    print(f"  the {len(DESIGNS)} holds a fresh entry for every call it has ever served. The")
    print("  column that separates them is the count of answers computed for the")
    print("  wrong arguments, and no cache reports that column about itself.")


main()
