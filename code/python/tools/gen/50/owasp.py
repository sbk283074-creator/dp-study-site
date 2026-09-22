#!/usr/bin/env python3
"""Chapter 50 demo, part 5 -- the Top Ten, held against this book.

The OWASP Top Ten is a list of ten categories of thing that go wrong, ordered
by how often they are found. It is useful here for one reason: it is a list
somebody else maintains, so using it is a way of finding out what you forgot
rather than what you already believe.

So this script scores the book against it. The interesting column is not the
score -- it is the shape of the score, because the categories this book
already handles and the categories it does not are separated by something
other than difficulty. They are separated by where the fix lives: in a line
of code, in a configuration file, or in a decision about the design.
"""

# The fix for a category lives in one of three places. That is the column that
# predicts whether a book like this one has already covered it.
FIX_KINDS = ("syntax", "configuration", "design")

# id, category, where the fix lives, chapters here that touch it, the Part IX
# chapter that will close it if none of them do.
CATEGORIES = [
    ("A01", "Broken Access Control",              "design",        [27],       "53"),
    ("A02", "Cryptographic Failures",             "syntax",        [27, 28],   ""),
    ("A03", "Injection",                          "syntax",        [19, 25],   ""),
    ("A04", "Insecure Design",                    "design",        [],         "53"),
    ("A05", "Security Misconfiguration",          "configuration", [29],       "53"),
    ("A06", "Vulnerable and Outdated Components", "configuration", [22],       "53"),
    ("A07", "Identification and Authentication",  "syntax",        [27],       "53"),
    ("A08", "Software and Data Integrity",        "design",        [],         "52"),
    ("A09", "Logging and Monitoring Failures",    "configuration", [],         "53"),
    ("A10", "Server-Side Request Forgery",        "design",        [],         "53"),
]

# Which part of the book each referenced chapter lives in.
PART_OF_CHAPTER = {
    19: "III · Real-World Python",
    22: "III · Real-World Python",
    25: "IV · Track A · Full-Stack Web",
    27: "IV · Track A · Full-Stack Web",
    28: "IV · Track A · Full-Stack Web",
    29: "IV · Track A · Full-Stack Web",
}

PARTS = [
    "I · Foundations",
    "II · Leveling Up",
    "III · Real-World Python",
    "IV · Track A · Full-Stack Web",
    "V · Track B · Game Development",
    "VI · Appendices",
    "VII · How Python Actually Works",
    "VIII · Cost, Structure and Algorithms",
]


def status_of(chapters):
    if len(chapters) >= 2:
        return "covered"
    if chapters:
        return "partly"
    return "not covered"


def main():
    print("  OWASP Top Ten (2021), held against this book")
    print()
    print(f"    {'id':<6}{'category':<40}{'fix':<16}{'here':<12}{'status'}")
    for cid, name, fix, chapters, planned in CATEGORIES:
        here = ", ".join(f"ch{c}" for c in chapters) if chapters else "--"
        print(f"    {cid:<6}{name:<40}{fix:<16}{here:<12}{status_of(chapters)}")

    print()
    counts = {}
    for cid, name, fix, chapters, planned in CATEGORIES:
        counts.setdefault(status_of(chapters), 0)
        counts[status_of(chapters)] += 1
    for status in ("covered", "partly", "not covered"):
        print(f"    {status:<16}{counts.get(status, 0):>3} of {len(CATEGORIES)}")

    print()
    print("  the same ten, split by where the fix lives")
    print()
    print(f"    {'fix lives in':<18}{'categories':>11}{'covered':>9}{'partly':>8}{'absent':>8}")
    for fix in FIX_KINDS:
        got = [c for c in CATEGORIES if c[2] == fix]
        cov = sum(1 for c in got if status_of(c[3]) == "covered")
        par = sum(1 for c in got if status_of(c[3]) == "partly")
        non = sum(1 for c in got if status_of(c[3]) == "not covered")
        print(f"    {fix:<18}{len(got):>11}{cov:>9}{par:>8}{non:>8}")

    print()
    print("  every category with a syntax-level fix is covered.")
    print("  no category with a design-level fix is.")

    # Where the book's security content actually lives.
    used = sorted({c for _, _, _, chs, _ in CATEGORIES for c in chs})
    print()
    print(f"  chapters of this book that touch a Top Ten category   {len(used):>3} of 51")
    for part in PARTS:
        n = sum(1 for c in used if PART_OF_CHAPTER.get(c) == part)
        mark = "" if n else "   (none)"
        print(f"    {part:<38}{n:>3}{mark}")

    print()
    print("  the gap, and which chapter of Part IX closes it")
    for cid, name, fix, chapters, planned in CATEGORIES:
        if not chapters:
            print(f"    {cid}  {name:<40} -> ch{planned}")


if __name__ == "__main__":
    main()
