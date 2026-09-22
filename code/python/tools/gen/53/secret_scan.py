"""Chapter 53 -- secret scanning.

Three detectors over twelve config lines. The credential-shaped values
are built from a seeded generator rather than written out, so that this
file -- which is published -- contains no string that a secret scanner
would flag, and so that the sample values are identical on every machine.
Nothing here prints a full value; the report shows a redaction, which is
what a scanner report is supposed to show.
"""

import math
import re
import string

HEX = "0123456789abcdef"
ALNUM = string.ascii_letters + string.digits
UPPER = string.ascii_uppercase + string.digits
BASE64 = string.ascii_letters + string.digits + "+/"


class Stream:
    """A linear congruential generator, so the samples are the same
    everywhere. The high bits are used because the low bits of an LCG
    are the ones with the short period."""

    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF

    def _step(self):
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state

    def body(self, n, alphabet):
        out = []
        for _ in range(n):
            out.append(alphabet[(self._step() >> 15) % len(alphabet)])
        return "".join(out)


S = Stream(53)

# --- the twelve lines -------------------------------------------------
#
# (name, value, does it really carry a credential)
LINES = [
    ("DB_PASSWORD", "hunter2", True),
    ("STRIPE_KEY", "sk-" + S.body(24, ALNUM), True),
    ("AWS_ACCESS_KEY_ID", "AKIA" + S.body(16, UPPER), True),
    ("SESSION_SIGNING_KEY", S.body(32, HEX), True),
    ("OAUTH_CLIENT_SECRET", S.body(30, BASE64), True),
    ("WEBHOOK_URL", "https://hooks.internal/services/" + S.body(32, BASE64), True),
    ("BUILD_HASH", S.body(40, HEX), False),
    ("REQUEST_ID_SALT", S.body(24, ALNUM), False),
    ("CDN_ASSET_DIGEST", S.body(64, HEX), False),
    ("TOKEN_BUDGET", "5000", False),
    ("LOG_LEVEL", "info", False),
    ("REGION", "eu-west-1", False),
]

# --- the three detectors ----------------------------------------------

# one: a list of formats someone wrote down, after an incident
PREFIXES = ["sk-", "pk_", "ghp_", "xoxb-", "AKIA", "ASIA"]
PREFIX = re.compile("|".join(re.escape(p) for p in PREFIXES) + r"[A-Za-z0-9]{12,}")

# two: the name of the setting, and not its value at all
KEYWORD = re.compile(r"password|passwd|secret|token|api[_-]?key|signing", re.I)

# three: find a candidate token, then ask how surprising it is
TOKEN = re.compile(r"[A-Za-z0-9_\-+/]{16,}")
# 3.0 sits between the two populations rather than on top of either: a
# word-shaped password measures about 2.8, a random hex string about 3.5.
ENTROPY_FLOOR = 3.0


def entropy(value):
    if not value:
        return 0.0
    counts = {}
    for ch in value:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def detect(name, value):
    candidate = TOKEN.search(value)
    return {
        "prefix": bool(PREFIX.search(value)),
        "keyword": bool(KEYWORD.search(name)),
        "entropy": bool(candidate) and entropy(candidate.group(0)) >= ENTROPY_FLOOR,
    }


def redact(value):
    """A scanner report shows enough to find the line and not enough to
    use the value."""
    return value[:4] + "\u2026" if len(value) > 8 else value


DETECTORS = ["prefix", "keyword", "entropy"]
FOUND = {name: detect(name, value) for name, value, _ in LINES}
REAL = [(n, v) for n, v, real in LINES if real]
FAKE = [(n, v) for n, v, real in LINES if not real]


def hits(pairs, detector):
    return [n for n, v in pairs if FOUND[n][detector]]


def main():
    print(f"  config lines                       {len(LINES):>3}")
    print(f"  lines that really carry one         {len(REAL):>3}")
    print()

    print("    line                    prefix  keyword  entropy  reported as")
    for name, value, real in LINES:
        d = FOUND[name]
        mark = {"prefix": "yes", "keyword": "yes", "entropy": "yes"}
        row = "    {:<22}".format(name)
        for key in DETECTORS:
            row += "{:>7}".format(mark[key] if d[key] else "-")
        row += "  " + redact(value)
        print(row)
    print()

    print("    detector     of the %d   false alarms" % len(REAL))
    union = set()
    for key in DETECTORS:
        got = hits(REAL, key)
        union.update(got)
        print("    {:<10}{:>9}{:>14}".format(key, len(got), len(hits(FAKE, key))))
    print("    {:<10}{:>9}{:>14}".format("all three", len(union), len(
        [n for n, v in FAKE if any(FOUND[n][k] for k in DETECTORS)])))
    print()

    print("  what each detector missed")
    for key in DETECTORS:
        missed = [n for n, v in REAL if not FOUND[n][key]]
        print("    {:<9} {}".format(key, "  ".join(missed) if missed else "(nothing)"))
    print()

    print("  what each detector flagged that is not a credential")
    for key in DETECTORS:
        wrong = hits(FAKE, key)
        print("    {:<9} {}".format(key, "  ".join(wrong) if wrong else "(nothing)"))
    print()

    print("  the three detectors are not three attempts at the same thing.")
    print("  they look at different parts of the line.")
    print()
    print("  the prefix detector reads the value and knows a handful of")
    print(f"  formats. it found {len(hits(REAL, 'prefix'))} of the {len(REAL)} and raised "
          f"{len(hits(FAKE, 'prefix'))}")
    print("  false alarms -- because a format it does not have written")
    print("  down is invisible to it, and the formats are issued by")
    print("  whoever runs the service.")
    print()
    by_kw = [n for n, v in REAL if not FOUND[n]["keyword"]]
    purpose_named = [n for n in by_kw if "KEY" not in n.upper()]
    key_named = [n for n in by_kw if "KEY" in n.upper()]
    print("  the keyword detector reads the name and not the value at")
    print(f"  all. it found {len(hits(REAL, 'keyword'))} of the {len(REAL)}. one of the misses is")
    print(f"  `{purpose_named[0]}`, a credential whose name describes what")
    print("  it is for rather than what it is -- and the name is chosen")
    print("  by whoever wrote the config, so this detector's recall is")
    print("  a property of other people's habits. the other "
          f"{len(key_named)} are")
    print("  " + " and ".join("`" + n + "`" for n in key_named) + ",")
    print("  both of which have \"key\" in the name: the list holds")
    print("  `api key` and not `key`, because a bare `key` flags every")
    print("  config file that has one. the detector is exactly as wide")
    print("  as the words someone chose, and it also flagged")
    print(f"  `{hits(FAKE, 'keyword')[0]}`, which is a number.")
    print()
    by_ent = [n for n, v in REAL if not FOUND[n]["entropy"]]
    print("  the entropy detector reads the value and knows nothing about")
    print(f"  formats or names. it found {len(hits(REAL, 'entropy'))} of the {len(REAL)} and flagged")
    print(f"  {len(hits(FAKE, 'entropy'))} of the {len(FAKE)} that are not credentials, because a")
    print("  build hash is a random string and so is a key. it is the")
    print("  only one that finds a credential nobody has seen before,")
    print("  and the only one that cannot tell one from a checksum.")
    if by_ent:
        print(f"  the one it misses is `{by_ent[0]}`, and its value is a word:")
        print("  entropy is high when the characters vary, and a password a")
        print("  person chose is the one value in this file that does not.")
    print()
    print(f"  the union finds all {len(union)} and costs "
          f"{len([n for n, v in FAKE if any(FOUND[n][k] for k in DETECTORS)])} false alarms --")
    print("  and what all three depend on is the same thing: a corpus")
    print("  someone chose. that is the blocklist argument from the")
    print("  injection chapter, and it ends the same way. detection is a")
    print("  backstop for a credential that has already leaked. the fix")
    print("  is that it was never in the file.")


main()
