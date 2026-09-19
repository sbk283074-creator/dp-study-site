#!/usr/bin/env python3
"""Notation audit across every bank section.

The gate lints carets, ASCII exponents, tag balance and decimals.  It has never looked
at the ROOT SYMBOL, which is the one glyph whose meaning depends on what follows it:
`&#8730;` renders as a bare radical with NO overbar, so

    &#8730;(hc/G)      ->  sqrt(hc/G)      unambiguous
    &#8730;hc/G        ->  sqrt(hc)/G  or  sqrt(hc/G)   AMBIGUOUS
    &#8730;2           ->  sqrt(2)         conventional, fine

This script prints every radical with its radicand, flags the ambiguous ones, and sweeps
for the other notation drifts (mixed glyph forms, odd entities, entity-vs-character).
"""
import html as _html
import io
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates as G

SECTIONS = range(1, 8)

# every way a radical can be written in this corpus
RAD_FORMS = [
    ("U+221A char", "\u221a"),
    ("&#8730;", "&#8730;"),
    ("&#x221A;", "&#x221a;"),
    ("&radic;", "&radic;"),
    ("sqrt(", "sqrt("),
]

TAG_RE = re.compile(r"<[^>]+>")
ENT_RE = re.compile(r"&#?[A-Za-z0-9]+;")


def plain(s):
    """Roughly what the reader sees: tags stripped, entities decoded."""
    return _html.unescape(TAG_RE.sub("", s or ""))


def fields(q):
    """(label, raw) for everything a reader can meet, plus the profile prose."""
    yield "stem", q.get("stem", "")
    for i, o in enumerate(q.get("opts", [])):
        yield "opt%d" % i, o
    yield "sol", q.get("sol", "")
    yield "trap", q.get("trap", "")
    yield "topic", q.get("topic", "")
    for i, r in enumerate(q.get("rel", []) or []):
        yield "rel%d" % i, (r[1] if isinstance(r, (list, tuple)) and len(r) > 1 else "")
    p = q.get("profile") or {}
    for i, s in enumerate(p.get("steps") or []):
        yield "pstep%d" % i, (s[1] if isinstance(s, (list, tuple)) and len(s) > 1 else str(s))
    for i, s in enumerate(p.get("relations") or []):
        yield "prel%d" % i, s
    yield "pinsight", p.get("insight", "")


def radicand_after(text, idx):
    """The token(s) the radical is supposed to cover, as written.

    Returns (radicand, verdict).  A parenthesised group is unambiguous.  A single
    alphanumeric token is conventional.  Anything else that contains an operator is
    ambiguous, because the radical has no overbar to show where it ends.
    """
    rest = text[idx:]
    if not rest:
        return "", "empty"
    if rest[0] == "(":
        depth = 0
        for k, ch in enumerate(rest):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return rest[:k + 1], "ok-parens"
        return rest[:40], "UNBALANCED"
    # a bare token: letters, digits, dots, unicode superscripts
    m = re.match(r"[\w.\u00b0-\u00be\u2070-\u209f\u2190-\u22ff]+", rest)
    tok = m.group(0) if m else rest[0]
    tail = rest[len(tok):]
    # what immediately follows decides whether the token was the whole radicand
    if re.match(r"\s*[\u00b7\u00d7*/+\u2212-]", tail):
        return tok + tail[:12].rstrip(), "AMBIGUOUS"
    return tok, "ok-token"


def main():
    print("=" * 78)
    print("1. EVERY RADICAL, WITH ITS RADICAND")
    print("=" * 78)
    total = 0
    ambiguous = []
    for n in SECTIONS:
        mod = G.load_section(n)
        for q in mod.QUESTIONS:
            for label, raw in fields(q):
                for form_name, form in RAD_FORMS:
                    start = 0
                    while True:
                        i = raw.find(form, start)
                        if i < 0:
                            break
                        start = i + 1
                        # a radical inside a <code> is still read by the candidate
                        vis = plain(raw)
                        # map raw index to visible index
                        before = plain(raw[:i])
                        vi = len(before)
                        rad, verdict = radicand_after(vis, vi)
                        total += 1
                        if verdict in ("AMBIGUOUS", "UNBALANCED", "empty"):
                            ambiguous.append((q["id"], label, form_name, rad, verdict))
                        print("  %-8s %-7s %-11s %-14s %s"
                              % (q["id"], label, form_name,
                                 repr(rad[:14]), verdict if verdict.startswith("ok") else "** " + verdict))
    print("\n  radicals found: %d   suspicious: %d" % (total, len(ambiguous)))

    print()
    print("=" * 78)
    print("2. MIXED FORMS -- the same glyph written two ways in one section")
    print("=" * 78)
    for n in SECTIONS:
        mod = G.load_section(n)
        seen = {}
        for q in mod.QUESTIONS:
            blob = " ".join(raw for _, raw in fields(q))
            for form_name, form in RAD_FORMS:
                if form in blob:
                    seen.setdefault(form_name, []).append(q["id"])
        if len(seen) > 1:
            print("  S%02d: " % n + "  |  ".join("%s in %s" % (k, ",".join(v)) for k, v in seen.items()))
        elif seen:
            print("  S%02d: only %s" % (n, list(seen)[0]))
    print()

    print("=" * 78)
    print("3. ENTITY HYGIENE")
    print("=" * 78)
    known = set()
    odd = {}
    for n in SECTIONS:
        mod = G.load_section(n)
        for q in mod.QUESTIONS:
            for label, raw in fields(q):
                for m in ENT_RE.finditer(raw or ""):
                    e = m.group(0)
                    known.add(e)
                    ch = _html.unescape(e)
                    # an entity that decodes to itself is unknown to Python's table
                    if ch == e:
                        odd.setdefault(e, []).append(q["id"])
                    # a control or replacement char means a mistyped code point
                    if ch and (ord(ch[0]) < 32 or ord(ch[0]) == 0xFFFD):
                        odd.setdefault(e + " (control!)", []).append(q["id"])
    print("  distinct entities in use: %d" % len(known))
    print("  " + " ".join(sorted(known)))
    if odd:
        print("\n  UNKNOWN / SUSPECT:")
        for e, ids in sorted(odd.items()):
            print("    %-12s %s" % (e, ",".join(sorted(set(ids))[:8])))
    else:
        print("  no unknown or control entities")

    print()
    print("=" * 78)
    print("4. CHARACTER vs ENTITY for the same symbol")
    print("=" * 78)
    # symbols that appear BOTH as a literal character and as a numeric entity
    pairs = [("\u221a", "&#8730;", "root"), ("\u00b7", "&#183;", "middle dot"),
             ("\u00d7", "&#215;", "times"), ("\u03b8", "&#952;", "theta"),
             ("\u00bd", "&#189;", "one half"), ("\u2248", "&#8776;", "approx"),
             ("\u2212", "&#8722;", "minus"), ("\u00b0", "&#176;", "degree"),
             ("\u0394", "&#916;", "Delta"), ("\u03bb", "&#955;", "lambda"),
             ("\u03c1", "&#961;", "rho"), ("\u2264", "&#8804;", "le"),
             ("\u2265", "&#8805;", "ge"), ("\u00b2", "&#178;", "sup 2")]
    for ch, ent, name in pairs:
        where_ch, where_ent = [], []
        for n in SECTIONS:
            mod = G.load_section(n)
            for q in mod.QUESTIONS:
                for label, raw in fields(q):
                    if ch in (raw or ""):
                        where_ch.append(q["id"])
                    if ent in (raw or ""):
                        where_ent.append(q["id"])
        if where_ch and where_ent:
            print("  %-10s BOTH: character in %d question(s), entity in %d"
                  % (name, len(set(where_ch)), len(set(where_ent))))
        elif where_ch:
            print("  %-10s character only (%d)" % (name, len(set(where_ch))))
        elif where_ent:
            print("  %-10s entity only (%d)" % (name, len(set(where_ent))))
        else:
            print("  %-10s unused" % name)

    print()
    print("=" * 78)
    print("5. SUSPICIOUS NOTATION PATTERNS")
    print("=" * 78)
    pats = [
        (r"&#\d+[^;0-9]", "entity missing its semicolon"),
        (r"&\w+\b(?!;)", "named entity missing its semicolon"),
        (r"\b10\s*\^\s*\d", "ten-to-the written with a caret"),
        (r"[a-zA-Z]\d\b", "ASCII exponent (a digit glued to a unit)"),
        (r"\bsqrt\b", "spelled-out sqrt"),
        (r"\*\*", "programming power operator"),
        (r"(?<![<\w])\.\.\.", "ellipsis instead of a symbol"),
        (r"\bpi\b", "spelled-out pi"),
        (r"\btheta\b|\blambda\b|\brho\b|\balpha\b|\bbeta\b|\bgamma\b|\bmu\b|\bomega\b",
         "Greek letter spelled out"),
        (r"<sup>\s*</sup>", "empty superscript"),
        (r"<sub>\s*</sub>", "empty subscript"),
        (r"[<>]{2,}", "double angle bracket"),
    ]
    for rx, why in pats:
        hits = []
        for n in SECTIONS:
            mod = G.load_section(n)
            for q in mod.QUESTIONS:
                for label, raw in fields(q):
                    for m in re.finditer(rx, raw or ""):
                        ctx = (raw or "")[max(0, m.start() - 22):m.start() + 22]
                        hits.append((q["id"], label, m.group(0), ctx.replace("\n", " ")))
        if hits:
            print("\n  %s -- %d hit(s)" % (why, len(hits)))
            for h in hits[:12]:
                print("    %-8s %-8s %-10s ...%s..." % h)
        else:
            print("  %-52s none" % why)


if __name__ == "__main__":
    main()
