#!/usr/bin/env python3
"""High-signal radical-scope audit.

A radical has no overbar when written as `&#8730;` / `&radic;` / the character, so its
SCOPE is carried entirely by parentheses.  Three shapes:

  ok        `&#8730;(hc/G)`     parenthesised -- the scope is explicit
  ok        `&#8730;2`, `&#8730;r`   a single token -- conventional reading
  DANGER    `&#8730;hc`, `&#8730;2gh`, `&#8730;hc/G`   a multi-symbol radicand with no
            parentheses, where the author may have meant a larger scope than the reader
            will infer

This prints only the DANGER cases, from fields the candidate actually reads, with enough
context to judge.  `sqrt(...)` is never ambiguous and is reported separately.
"""
import html as _html
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates as G

TAG_RE = re.compile(r"<[^>]+>")
RAD = ("\u221a", "&#8730;", "&#x221a;", "&radic;")
# a radical with an EXPLICIT argument is fine and is skipped
EXPLICIT = re.compile(r"(?:\u221a|&#8730;|&#x221a;|&radic;)\s*\(")


def plain(s):
    return _html.unescape(TAG_RE.sub("", s or ""))


def displayed(q):
    """Only what the candidate meets.  Profile prose is author-facing, not shown."""
    yield "stem", q.get("stem", "")
    for i, o in enumerate(q.get("opts", [])):
        yield "opt%d" % i, o
    yield "sol", q.get("sol", "")
    yield "trap", q.get("trap", "")
    yield "topic", q.get("topic", "")
    for i, r in enumerate(q.get("rel", []) or []):
        yield "rel%d" % i, (r[1] if isinstance(r, (list, tuple)) and len(r) > 1 else "")


def main():
    danger = []
    single = []
    n_sqrt = 0
    for n in range(1, 8):
        mod = G.load_section(n)
        for q in mod.QUESTIONS:
            for label, raw in displayed(q):
                vis = plain(raw)
                # every radical in the RENDERED text, so entity and character look alike
                for m in re.finditer(r"\u221a", vis):
                    i = m.start()
                    rest = vis[i + 1:]
                    if not rest:
                        continue
                    if rest[0] in "(":
                        continue                      # explicit scope
                    if rest[0].isspace():
                        danger.append((q["id"], label, rest[:26], "radical then SPACE"))
                        continue
                    tok = re.match(r"[\w.\u00b0-\u00be\u2070-\u209f]+", rest)
                    tok = tok.group(0) if tok else rest[0]
                    after = rest[len(tok):]
                    ctx = vis[max(0, i - 30):i + 30].replace("\n", " ")
                    # a bare token of 2+ chars that mixes letters, or is a digit run plus
                    # letters, is a product the radical may or may not cover
                    if len(tok) > 1 and re.search(r"[A-Za-z]", tok):
                        danger.append((q["id"], label, "\u221a" + tok + after[:10], ctx))
                    elif len(tok) > 1 and re.match(r"^\d+$", tok) and re.match(r"\s*[/*]", after):
                        # sqrt(200) / x  -- a bare multi-digit number then an operator
                        danger.append((q["id"], label, "\u221a" + tok + after[:10], ctx))
                    else:
                        single.append((q["id"], label, "\u221a" + tok))
                for m in re.finditer(r"sqrt\s*\(", raw or ""):
                    n_sqrt += 1

    print("=" * 78)
    print("A. RADICALS WITH AN AMBIGUOUS OR SUSPICIOUS SCOPE")
    print("=" * 78)
    if not danger:
        print("  none -- every radical is either parenthesised or covers a single token")
    for d in danger:
        print("  %-8s %-7s %-18s %s" % (d[0], d[1], d[2], d[3] if len(d) > 3 else ""))
    print("\n  flagged: %d" % len(danger))

    print()
    print("=" * 78)
    print("B. RADICALS THAT COVER A SINGLE TOKEN (conventional, listed for review)")
    print("=" * 78)
    from collections import Counter
    c = Counter(s[2] for s in single)
    for tok, k in sorted(c.items(), key=lambda t: -t[1]):
        print("  %-14s x%d" % (tok, k))
    print("\n  distinct single-token radicands: %d   total radicals: %d"
          % (len(c), len(single) + len(danger)))
    print("  spelled-out sqrt( occurrences in the displayed text: %d" % n_sqrt)

    print()
    print("=" * 78)
    print("C. WHERE EACH RADICAL FORM IS USED (consistency)")
    print("=" * 78)
    for n in range(1, 8):
        mod = G.load_section(n)
        forms = {}
        for q in mod.QUESTIONS:
            for label, raw in displayed(q):
                for f, name in (("&#8730;", "&#8730;"), ("&radic;", "&radic;"),
                                ("\u221a", "char \u221a"), ("&#x221a;", "&#x221A;")):
                    if f in (raw or ""):
                        forms.setdefault(name, set()).add(q["id"])
        print("  S%02d  " % n + ("  ".join("%s (%d qs)" % (k, len(v)) for k, v in forms.items())
                                 or "no radicals"))


if __name__ == "__main__":
    main()
