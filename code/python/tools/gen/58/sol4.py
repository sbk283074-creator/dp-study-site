"""Solution 4 -- a benchmark that checks itself.

Four designs run through a harness that asserts how many times the code
under test was entered. The harness reports which designs measure what
they claim to.
"""

CALLS = [0]


def work(text):
    CALLS[0] += 1
    return len(text.split())


TEXTS = ["a b c"] * 30
CACHE = {}


def memoised(text):
    if text not in CACHE:
        CACHE[text] = work(text)
    return CACHE[text]


for _text in TEXTS:
    memoised(_text)
CALLS[0] = 0


def the_loop():
    for text in TEXTS:
        work(text)


def the_warm_cache():
    for text in TEXTS:
        memoised(text)


def a_copy_of_the_input():
    TEXTS[:]


def the_wrong_function():
    for text in TEXTS:
        len(text)


DESIGNS = [
    ("the loop", the_loop, len(TEXTS)),
    ("the warm cache", the_warm_cache, len(TEXTS)),
    ("a copy of the input", a_copy_of_the_input, len(TEXTS)),
    ("len instead of work", the_wrong_function, len(TEXTS)),
]


def bench(design, expected):
    """Run one design and report how many times the function was entered."""
    CALLS[0] = 0
    design()
    entered = CALLS[0]
    return entered, entered == expected


def main():
    print(f"  inputs                              {len(TEXTS)}")
    print(f"  designs                             {len(DESIGNS)}")
    print()
    print("    design                  declared   entered   verdict")
    passed = 0
    for name, design, expected in DESIGNS:
        entered, ok = bench(design, expected)
        passed += 1 if ok else 0
        verdict = "measures it" if ok else "measures something else"
        print("    {:<24}{:>8}{:>10}   {}".format(name, expected, entered,
                                                 verdict))
    print()
    print(f"  {passed} of the {len(DESIGNS)} designs measure what they declare. The other")
    print(f"  {len(DESIGNS) - passed} produce a number that is a real measurement of a real")
    print("  thing, and not of the thing they were written to measure.")
    print()
    print("  the harness is four lines and it is the part that matters. It")
    print("  resets the counter, runs the design, and compares the counter")
    print("  against the number the design declares. A design that cannot")
    print("  pass that comparison is not a slow benchmark; it is not a")
    print("  benchmark, and the difference is invisible in the source of any")
    print("  of the four above.")
    print()
    print("  the declared count is also the assumption the design rests on.")
    print(f"  Writing `{len(TEXTS)}` beside a loop over {len(TEXTS)} texts is a claim about")
    print("  the input, and the harness checks that claim against the run")
    print("  rather than against the reader's confidence.")
    print()
    print("  so the pattern for any measurement worth keeping is: count")
    print("  something the code under test controls, declare what that count")
    print("  should be, and fail loudly when it is not. The number a benchmark")
    print("  prints is worth as much as the check standing beside it.")


main()
