"""Chapter 58 -- what a profiler counts, and what it cannot see.

A small text pipeline profiled with cProfile. Only the call counts are
printed, because they are the part of a profile that is the same on every
machine, and the operations inside each function are counted separately.
"""

import cProfile
import pstats

OPS = {}


def bump(name, count=1):
    OPS[name] = OPS.get(name, 0) + count


def normalise(word):
    bump("normalise")
    return word.strip().lower()


def tokenise(text):
    parts = text.split()
    bump("tokenise", len(parts))
    return parts


def keep_long(words):
    out = []
    for word in words:
        bump("keep_long")
        word = normalise(word)
        if len(word) > 3:
            out.append(word)
    return out


def count_words(words):
    counts = {}
    for word in words:
        bump("count_words", 2)
        counts[word] = counts.get(word, 0) + 1
    return counts


def report(text):
    bump("report")
    words = keep_long(tokenise(text))
    return sorted(count_words(words).items())


TEXT = " ".join("word%d" % (i % 40) for i in range(600))
REPEATS = 5

WATCHED = ["report", "tokenise", "keep_long", "count_words", "normalise"]


def profile():
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(REPEATS):
        report(TEXT)
    profiler.disable()
    return pstats.Stats(profiler)


def main():
    stats = profile()
    calls = {}
    for (_file, _line, name), entry in stats.stats.items():
        if name in WATCHED:
            calls[name] = entry[1]

    print(f"  repeats                             {REPEATS}")
    print(f"  words per call                      {len(TEXT.split())}")
    print()
    print("    function        calls   ops per call   total ops")
    for name in WATCHED:
        count = calls.get(name, 0)
        ops = OPS.get(name, 0)
        per = ops // count if count else 0
        print("    {:<16}{:>6}{:>15}{:>12}".format(name, count, per, ops))
    print()

    print("    the order the call counts give you")
    for index, name in enumerate(
            sorted(WATCHED, key=lambda n: -calls.get(n, 0)), 1):
        print("    {:<3}{:<14}{:>7} calls".format(index, name,
                                                 calls.get(name, 0)))
    print()

    print("    the order the operation counts give you")
    for index, name in enumerate(sorted(WATCHED, key=lambda n: -OPS.get(n, 0)),
                                 1):
        print("    {:<3}{:<14}{:>7} operations".format(index, name,
                                                      OPS.get(name, 0)))
    print()

    top_calls = max(WATCHED, key=lambda n: calls.get(n, 0))
    top_ops = max(WATCHED, key=lambda n: OPS.get(n, 0))
    print(f"  `{top_calls}` is called {calls[top_calls]} times and does one thing")
    print(f"  each time. `{top_ops}` is called {calls[top_ops]} times and does")
    print(f"  {OPS[top_ops] // calls[top_ops]} things each time, so the two rankings disagree")
    print("  about which one to look at first.")
    print()
    print("  the profiler counts entries into a function, and it cannot see")
    print("  the loop inside one. `count_words` gets a single row for the")
    print("  whole of its loop body, and `normalise` gets a row per call, so")
    print("  a profile's headline number is a count of how often code was")
    print("  entered -- which is a shape, not a cost.")
    print()
    print("  that is why the profiler's other column exists, and why this")
    print("  chapter does not print it. the time column is the one you want")
    print("  and it is the one that cannot be written into a book, because")
    print("  it changes with the machine. the counts do not, so they are")
    print("  what a measured claim has to rest on.")


main()
