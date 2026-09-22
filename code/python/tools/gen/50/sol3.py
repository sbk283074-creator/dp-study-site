#!/usr/bin/env python3
"""Exercise 3 -- STRIDE one element, and check it against the matrix.

The six questions applied to a single component of an upload service, then
the same component run through the applicability matrix. The two counts are
not the same number, and the difference is the point of the exercise.
"""
import itertools

STRIDE = (
    "Spoofing", "Tampering", "Repudiation",
    "Information disclosure", "Denial of service", "Elevation of privilege",
)

APPLICABLE = {
    "external entity": ("Spoofing", "Repudiation"),
    "process": STRIDE,
    "data store": ("Tampering", "Repudiation", "Information disclosure", "Denial of service"),
    "data flow": ("Tampering", "Information disclosure", "Denial of service"),
}

# The component under study, and the threats a person actually wrote down
# after thinking about it for ten minutes.
ELEMENT = "upload service"
KIND = "process"
WRITTEN = [
    ("Spoofing", "a forged session cookie reaches the handler"),
    ("Tampering", "the filename is used as a path"),
    ("Tampering", "the content type is trusted over the bytes"),
    ("Information disclosure", "uploaded files are served without a session check"),
    ("Denial of service", "no size limit before the body is buffered"),
]

OTHER_ELEMENTS = [
    ("browser", "external entity"),
    ("object store", "data store"),
    ("browser->upload service", "data flow"),
    ("upload service->object store", "data flow"),
]


def main():
    print(f"  element                             {ELEMENT} ({KIND})")
    print()
    print("  the six questions, answered by hand")
    answered = {cat for cat, _ in WRITTEN}
    for cat in STRIDE:
        hits = [d for c, d in WRITTEN if c == cat]
        mark = "x" if hits else "."
        detail = hits[0] if hits else ""
        print(f"    {mark} {cat:<26}{detail}")
    print()
    print(f"  questions with an answer            {len(answered)} of {len(STRIDE)}")
    print(f"  threats written down                {len(WRITTEN)}")
    print(f"  questions left blank                {len(STRIDE) - len(answered)}"
          f"   {sorted(set(STRIDE) - answered)}")

    print()
    print("  the same element against the matrix")
    applies = APPLICABLE[KIND]
    print(f"    a {KIND} attracts {len(applies)} of the {len(STRIDE)} questions")
    print(f"    all {len(STRIDE)} were asked here, which cost nothing extra")
    print(f"    and found {len(STRIDE) - len(answered)} question(s) nobody had an answer for")

    # The same arithmetic for the whole diagram, for comparison.
    cells = len(OTHER_ELEMENTS) * len(STRIDE)
    applicable = sum(len(APPLICABLE[k]) for _, k in OTHER_ELEMENTS)
    print()
    print("  the rest of the diagram, for scale")
    for name, kind in OTHER_ELEMENTS:
        print(f"    {name:<30}{kind:<18}{len(APPLICABLE[kind])} of {len(STRIDE)}")
    print(f"    cells {cells}, applicable {applicable}"
          f"   ({applicable / cells:.1%})")

    print()
    print("  the matrix is a checklist for completeness. It does not rank,")
    print("  and it does not know which of your answers are wrong.")


if __name__ == "__main__":
    main()
