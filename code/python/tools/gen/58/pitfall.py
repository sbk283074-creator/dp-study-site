"""Chapter 58 -- the benchmark that measures something else.

Six benchmark designs, each declared to measure the same function over
the same fifty inputs. The count is of how many times that function was
actually entered, which is what decides whether the number means
anything.
"""

CALLS = [0]


def parse(text):
    CALLS[0] += 1
    return len(text.split())


TEXTS = ["a b c"] * 50
CACHE = {}


def cached_parse(text):
    if text not in CACHE:
        CACHE[text] = parse(text)
    return CACHE[text]


for _text in TEXTS:
    cached_parse(_text)
CALLS[0] = 0


def warm_the_cache():
    for text in TEXTS:
        cached_parse(text)


def the_loop():
    for text in TEXTS:
        parse(text)


def copy_the_input():
    TEXTS[:]


def an_empty_loop():
    for text in []:
        parse(text)


def the_wrong_function():
    for text in TEXTS:
        len(text)


def one_call_not_fifty():
    parse(TEXTS[0])


BENCHMARKS = [
    ("the loop over the texts", the_loop),
    ("the memoised wrapper", warm_the_cache),
    ("a copy of the input", copy_the_input),
    ("an empty loop", an_empty_loop),
    ("len() instead of parse()", the_wrong_function),
    ("one call, not fifty", one_call_not_fifty),
]

DECLARED = 50


def main():
    print(f"  inputs                              {len(TEXTS)}")
    print(f"  benchmarks                          {len(BENCHMARKS)}")
    print()
    print("    benchmark                    declared   parse() was entered")
    rows = []
    for name, benchmark in BENCHMARKS:
        CALLS[0] = 0
        benchmark()
        rows.append((name, CALLS[0]))
        print("    {:<29}{:>8}{:>22}".format(name, DECLARED, CALLS[0]))
    print()

    right = sum(1 for _, entered in rows if entered == DECLARED)
    zero = sum(1 for _, entered in rows if entered == 0)
    verb = "enters" if right == 1 else "enter"
    print(f"  {right} of the {len(BENCHMARKS)} benchmarks {verb} the function as many")
    print(f"  times as it claims. {zero} of them never enter it at all, and the")
    print("  number each one produces is a real measurement of something --")
    print("  a dict lookup, a list copy, an empty loop, `len`, or one call")
    print("  instead of fifty.")
    print()
    print("  none of those six designs would look wrong in a file. every one")
    print("  of them is a loop, or a call, inside a timer, and the only thing")
    print("  that separates them is whether the code under test is the code")
    print("  that ran.")
    print()
    print("  that is what makes this the first trap of the subject. a")
    print("  measurement is a claim, and the claim has two halves: this is")
    print("  the number, and this is what produced it. the second half is")
    print("  the one that goes missing, and the way to keep it is to count")
    print("  something the code under test controls -- entries, comparisons,")
    print("  containers -- and check that the count is what you expected")
    print("  before you look at the number at all.")


main()
