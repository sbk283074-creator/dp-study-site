"""Chapter 53 -- the scenario.

One feature, the password reset link, and the six mistakes it can make.
Each design adds fixes and the fixes live in different parts of the
flow, which is the point: the six are in six places and no two of them
are in the same file.
"""

SECRET = "0123456789abcdef"


def probes(guess, secret, constant):
    """How many bytes the comparison examines before it answers."""
    if constant:
        return len(secret)
    for i in range(min(len(guess), len(secret))):
        if guess[i] != secret[i]:
            return i + 1
    return min(len(guess), len(secret)) + 1


def wrong_guesses(secret):
    out = []
    for i in range(len(secret)):
        c = "z" if secret[i] != "z" else "y"
        out.append(secret[:i] + c + secret[i + 1:])
    return out


def observe(fixes):
    """The mistakes this design makes, in the order the flow reaches them."""
    made = []

    # the reply to a reset request, for an address that exists and for
    # one that does not
    replies = ["a link has been sent", "a link has been sent"]
    if "uniform response" not in fixes:
        replies[1] = "no account with that address"
    if replies[0] != replies[1]:
        made.append("the reply says whether the account exists")

    # the token comparison
    counts = [probes(g, SECRET, "constant-time" in fixes)
              for g in wrong_guesses(SECRET)]
    if len(set(counts)) > 1:
        made.append("the comparison stops at the first difference")

    # the token, presented a second time
    if "single-use token" not in fixes:
        made.append("the token still works a second time")

    # a session that was opened before the reset
    if "invalidate sessions" not in fixes:
        made.append("the old session survives the reset")

    # the target the reset form redirects to
    target = "//evil.com"
    if "redirect allow-list" not in fixes and target.startswith("//"):
        made.append("the redirect target comes from the request")

    # the line written when the reset completes
    if "field allow-list" not in fixes:
        made.append("the log line is built from the request body")

    return made


MISTAKES = [
    ("the reply says whether the account exists", "the handler"),
    ("the comparison stops at the first difference", "the comparison"),
    ("the token still works a second time", "the token store"),
    ("the old session survives the reset", "the session store"),
    ("the redirect target comes from the request", "the redirect"),
    ("the log line is built from the request body", "the logger"),
]

DESIGNS = [
    ("A", set()),
    ("B", {"constant-time"}),
    ("C", {"constant-time", "single-use token", "invalidate sessions"}),
    ("D", {"constant-time", "single-use token", "invalidate sessions",
           "uniform response", "redirect allow-list", "field allow-list"}),
]


def main():
    print(f"  mistakes the feature can make       {len(MISTAKES)}")
    print(f"  places they live in                 "
          f"{len(set(place for _, place in MISTAKES))}")
    print(f"  designs                             {len(DESIGNS)}")
    print()

    print("    {:<45}".format("mistake") +
          "".join("{:>7}".format(name) for name, _ in DESIGNS))
    made_by = {}
    for label, fixes in DESIGNS:
        made_by[label] = observe(fixes)
    for text, _ in MISTAKES:
        row = "    {:<45}".format(text)
        for label, _ in DESIGNS:
            row += "{:>7}".format("made" if text in made_by[label] else "-")
        print(row)
    print()
    print("    {:<45}".format("mistakes made") +
          "".join("{:>7}".format(len(made_by[label])) for label, _ in DESIGNS))
    print()

    counts = [probes(g, SECRET, False) for g in wrong_guesses(SECRET)]
    flat = [probes(g, SECRET, True) for g in wrong_guesses(SECRET)]
    print("  the comparison, for each of the "
          f"{len(counts)} single-byte-wrong guesses")
    for label, values in (("stopping at the first difference", counts),
                          ("always the whole secret", flat)):
        print("    " + label)
        for i in range(0, len(values), 8):
            print("      " + " ".join("{:>2}".format(v)
                                      for v in values[i:i + 8]))
    print()
    print(f"  the first row takes {len(set(counts))} different values and the second "
          f"takes {len(set(flat))},")
    print("  so the answer is a function of the guess in one of them and not")
    print("  in the other. that is the whole of the attack: the reply is")
    print("  still only yes or no, and the *work* behind it is what leaks.")
    print()

    print("    {:<46}{}".format("mistake", "the fix goes in"))
    for text, place in MISTAKES:
        print("    {:<46}{}".format(text, place))
    print()
    print(f"  {len(MISTAKES)} mistakes, "
          f"{len(set(place for _, place in MISTAKES))} places, and the four designs are")
    print("  not four versions of one decision. each column adds a fix")
    print("  somewhere else in the flow, and a review that reads one file")
    print("  finds the mistakes that happen to be in that file.")
    print()
    print("  that is why this chapter is not a list of topics. every one of")
    print("  these is a place, and a feature is the unit that reaches all of")
    print("  them -- which also means the only way to check a feature is to")
    print("  walk it from the request to the row and to the log, and ask at")
    print("  each step which parser or which check is reading the value now.")


main()
