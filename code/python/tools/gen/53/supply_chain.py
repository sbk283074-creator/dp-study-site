"""Chapter 53 -- the dependency supply chain.

What you install, what runs when you install it, and the two checks that
are not name checks. The resolution counts are computed from a small
version set rather than asserted, so they move if the version set does.
"""

import itertools

# --- the resolution surface -------------------------------------------

PACKAGES = {
    "pdf-toolkit": ["1.0", "1.1", "1.2", "2.0", "2.1"],
    "color-picker": ["1.0", "1.1", "1.2", "2.0", "2.1"],
    "json-schema": ["1.0", "1.1", "1.2", "2.0", "2.1"],
}


def satisfying(package, constraint):
    out = []
    for v in PACKAGES[package]:
        major = int(v.split(".")[0])
        if constraint == "any":
            out.append(v)
        elif constraint == "major 1" and major == 1:
            out.append(v)
        elif constraint.startswith("==") and v == constraint[2:]:
            out.append(v)
    return out


def surface(spec):
    """The number of distinct sets of versions a fresh install can land on."""
    pools = [satisfying(p, c) for p, c in spec.items()]
    if any(not pool for pool in pools):
        return 0
    return len(list(itertools.product(*pools)))


SPECS = [
    ("no constraint", {p: "any" for p in PACKAGES}, "accepted"),
    ("major 1 only", {p: "major 1" for p in PACKAGES}, "accepted"),
    ("one package pinned", {"pdf-toolkit": "==1.1",
                            "color-picker": "any", "json-schema": "any"},
     "accepted"),
    ("every package pinned", {p: "==1.1" for p in PACKAGES}, "accepted"),
    ("a lock file with hashes", {p: "==1.1" for p in PACKAGES}, "refused"),
]


# --- what runs when you install ---------------------------------------

INSTALL_STEPS = [
    ("python, sdist", "runs the build backend", True),
    ("python, wheel", "unpacks an archive", False),
    ("npm", "runs preinstall, install, postinstall", True),
    ("cargo", "compiles and runs build.rs", True),
    ("go modules", "verifies a checksum", False),
    ("apt / deb", "runs preinst and postinst, as root", True),
]


# --- name checks -------------------------------------------------------

REAL = ["pdf-toolkit", "color-picker", "json-schema", "snowflake-client"]

CANDIDATES = [
    "pdf-toolklt",
    "pdf-toolkitt",
    "pdf-toolkit-pro",
    "colorpicker",
    "color-picker-js",
    "json-chema",
    "json-schemas",
    "snowfake-client",
    "snowflake-clinet",
    "snowflake_client",
    "snowflake-api",
]


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def nearest(name):
    best = min(REAL, key=lambda r: levenshtein(name, r))
    return best, levenshtein(name, best)


def main():
    print("    requirements                 resolutions   a replaced artifact")
    for label, spec, replaced in SPECS:
        print("    {:<29}{:>11}   {}".format(label, surface(spec), replaced))
    print()
    print("  the last two rows have the same number and are not the same")
    print("  thing. a version is a name the publisher chooses and can move;")
    print("  a hash is the bytes. pinning every version narrows the surface")
    print("  to one and still installs whatever is served under that")
    print("  version -- which is the row above it, with a smaller number.")
    print()

    print("    install step                 what the step does")
    for name, what, runs in INSTALL_STEPS:
        print("    {:<29}{}{}".format(name, what,
                                    "" if runs else "  (no package code)"))
    running = [n for n, _, runs in INSTALL_STEPS if runs]
    print()
    print(f"  {len(running)} of the {len(INSTALL_STEPS)} run code the package author wrote,")
    print("  and none of them ask. the two that do not are the two that")
    print("  install a built artefact or check a checksum, and that is the")
    print("  only reason they are different.")
    print()

    print("    candidate name            nearest real name    distance")
    flagged, missed = [], []
    for name in CANDIDATES:
        real, d = nearest(name)
        print("    {:<25}{:<21}{:>2}".format(name, real, d))
        (flagged if d <= 1 else missed).append((name, real, d))
    print()
    print("  a check that flags anything within one edit of a name you")
    print(f"  already use catches {len(flagged)} of the {len(CANDIDATES)} and misses "
          f"{len(missed)}.")
    print()
    print("  the misses are two different kinds. one kind keeps the name")
    print("  you know and changes the part after it:")
    for name, real, d in missed:
        if d > 2 and name.startswith(real.split("-")[0]):
            print(f"    {name}")
    print("  those are the more convincing ones, because they look like an")
    print("  edition of something already in the file. the other kind is a")
    print("  transposition:")
    for name, real, d in missed:
        if d == 2:
            print(f"    {name}  (distance {d} from {real})")
    print("  a swapped pair of letters is two edits, not one, so the check")
    print("  misses the single most common typo there is. a blocklist of")
    print("  names known to be bad would catch 0 of these, because every")
    print("  one of them was fine on the day it was written.")
    print()

    print("  what the two rows above are really about")
    mirrors = 3
    print(f"    artifacts the index can serve for one version   {mirrors}")
    print(f"    accepted without a hash                         {mirrors}")
    print("    accepted with a hash                            1")
    print()
    print("  the name is the part the attacker chooses, and both of the")
    print("  checks above are checks on the name. the hash is the only one")
    print("  that is not, because it is a statement about the artefact")
    print("  rather than about who published it -- and that is also why it")
    print("  is the only one that has to be generated by someone who")
    print("  already had the artefact.")


main()
