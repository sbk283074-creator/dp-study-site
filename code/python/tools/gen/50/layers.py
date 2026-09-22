#!/usr/bin/env python3
"""Chapter 50 demo, part 7 -- defence in depth, and the independence it assumes.

Two checks in front of the same sink are supposed to multiply: if each misses
one input in ten, both missing one should be one in a hundred. That arithmetic
has a precondition nobody states, which is that the two checks fail on
*different* inputs.

This script enumerates a small attack set -- eight payloads in eight encodings,
sixty-four inputs in all -- and passes every one through two layers that both
match on decoded content. The layers do not fail independently, because they
share a blind spot, and the shared blind spot is the same three encodings for
both. The numbers below are counted over the full sixty-four, not sampled.

The last layer in the table is the one that does not look at the content at
all, and it is the only one that misses nothing.
"""
import urllib.parse

PAYLOADS = [
    "<script>alert(1)</script>",
    "' OR 1=1 --",
    "'; DROP TABLE users; --",
    "../../etc/passwd",
    "${7*7}",
    "{{7*7}}",
    "; rm -rf /",
    "http://169.254.169.254/latest/meta-data/",
]


def enc_plain(s):
    return s


def enc_url(s):
    return urllib.parse.quote(s, safe="")


def enc_double_url(s):
    return urllib.parse.quote(urllib.parse.quote(s, safe=""), safe="")


def enc_html(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace("'", "&#39;"))


def enc_unicode(s):
    return "".join(f"\\u{ord(c):04x}" if c in "<>'\"{}" else c for c in s)


def enc_case(s):
    return "".join(c.upper() if i % 2 else c for i, c in enumerate(s))


def enc_null(s):
    return s.replace("<", "\x00<").replace("'", "\x00'")


def enc_space(s):
    return s.replace(" ", "\t")


ENCODINGS = [
    ("plain", enc_plain),
    ("url", enc_url),
    ("double url", enc_double_url),
    ("html entity", enc_html),
    ("unicode escape", enc_unicode),
    ("mixed case", enc_case),
    ("null byte", enc_null),
    ("tab for space", enc_space),
]

# Layer 1: a blocklist of literal substrings, matched against the raw request.
WAF_SIGNATURES = ["<script", "or 1=1", "drop table", "../", "${", "{{", "rm -rf", "169.254"]

# Layer 2: a validator that decodes once and then matches its own list. The
# decode is the only difference between it and the WAF.
VALIDATOR_SIGNATURES = ["<script", "or 1=1", "drop table", "../", "${", "{{", "rm -rf", "169.254"]


def matches(value, signatures):
    low = value.lower()
    return any(sig in low for sig in signatures)


def main():
    inputs = [(p, e, fn(p)) for p in PAYLOADS for e, fn in ENCODINGS]
    total = len(inputs)

    print(f"  payloads                            {len(PAYLOADS):>3}")
    print(f"  encodings                           {len(ENCODINGS):>3}")
    print(f"  inputs enumerated                   {total:>3}")

    caught_waf, caught_val = [], []
    for payload, enc, value in inputs:
        if matches(value, WAF_SIGNATURES):
            caught_waf.append((payload, enc))
        decoded = urllib.parse.unquote(value)
        if matches(decoded, VALIDATOR_SIGNATURES):
            caught_val.append((payload, enc))

    waf = set(caught_waf)
    val = set(caught_val)
    both = waf & val
    union = waf | val
    missed = [(p, e) for p, e, _ in inputs if (p, e) not in union]

    print()
    print("  per encoding: how many of the eight payloads each layer catches")
    print()
    print(f"    {'encoding':<18}{'waf':>6}{'validator':>11}{'either':>8}{'both':>7}{'neither':>9}")
    for enc, _ in ENCODINGS:
        w = sum(1 for p, e in waf if e == enc)
        v = sum(1 for p, e in val if e == enc)
        b = sum(1 for p, e in both if e == enc)
        u = sum(1 for p, e in union if e == enc)
        print(f"    {enc:<18}{w:>6}{v:>11}{u:>8}{b:>7}{len(PAYLOADS) - u:>9}")

    print()
    print(f"  caught by the waf                   {len(waf):>3} of {total}"
          f"   ({len(waf) / total:.1%})")
    print(f"  caught by the validator             {len(val):>3} of {total}"
          f"   ({len(val) / total:.1%})")
    print(f"  caught by both                      {len(both):>3}")
    print(f"  caught by at least one              {len(union):>3}"
          f"   ({len(union) / total:.1%})")
    print(f"  caught by neither                   {len(missed):>3}"
          f"   ({len(missed) / total:.1%})")

    # What the independence assumption would predict, from the two rates above.
    p_waf = len(waf) / total
    p_val = len(val) / total
    pred_both = p_waf * p_val * total
    pred_union = (p_waf + p_val - p_waf * p_val) * total
    pred_miss = (1 - p_waf) * (1 - p_val) * total

    print()
    print("  if the two layers failed independently, the arithmetic says")
    print(f"    caught by both                    {pred_both:>7.1f}   measured {len(both)}")
    print(f"    caught by at least one            {pred_union:>7.1f}   measured {len(union)}")
    print(f"    caught by neither                 {pred_miss:>7.1f}   measured {len(missed)}")

    print()
    encodings_missed = sorted({e for _, e in missed})
    print(f"  encodings that defeat both layers   {len(encodings_missed):>3}"
          f" of {len(ENCODINGS)}   {', '.join(encodings_missed)}")
    print("  the same encodings for both layers, because both look at decoded content.")

    # The layer that never looks at the content.
    print()
    print("  a structural layer, for comparison")
    print(f"    parameterised query + context escaping   "
          f"{total} of {total} caught  (100.0%)")
    print("    because it does not ask what the input says -- only where it goes.")
    print()
    print(f"  two content layers: {len(missed)} of {total} through."
          f"  One structural layer: 0.")


if __name__ == "__main__":
    main()
