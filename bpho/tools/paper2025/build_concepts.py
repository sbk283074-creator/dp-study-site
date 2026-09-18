# -*- coding: utf-8 -*-
"""Emit bpho/data/concepts.js from the hand-authored lessons in concepts_*.py.

Run:  python build_concepts.py
Gate: unique ids · every prerequisite exists · no cycles · a prerequisite never sits
      in a later stage · every question's key points resolve · every concept is used
      by at least one question.
"""
import io
import re
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import concepts_a
import concepts_b
import concepts_c
from keys import KEYS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "concepts.js")

CONCEPTS = concepts_a.C + concepts_b.C + concepts_c.C
errors = []

# ── gate 1: unique ids
ids = [x["id"] for x in CONCEPTS]
for i in sorted(set(i for i in ids if ids.count(i) > 1)):
    errors.append("duplicate concept id: %s" % i)
by_id = {x["id"]: x for x in CONCEPTS}

# ── gate 2: prerequisites exist, and never sit in a later stage
for x in CONCEPTS:
    for p in x["pre"]:
        if p not in by_id:
            errors.append("%s: unknown prerequisite %r" % (x["id"], p))
        elif by_id[p]["stage"] > x["stage"]:
            errors.append("%s: prerequisite %s is in a later stage (%d > %d)"
                          % (x["id"], p, by_id[p]["stage"], x["stage"]))
        if p == x["id"]:
            errors.append("%s: lists itself as a prerequisite" % x["id"])

# ── gate 3: no cycles (depth-first, three-state marking)
WHITE, GREY, BLACK = 0, 1, 2
mark = {i: WHITE for i in ids}


def dfs(u, stack):
    mark[u] = GREY
    for v in by_id[u]["pre"]:
        if v not in by_id:
            continue
        if mark[v] == GREY:
            errors.append("prerequisite cycle: %s" % " → ".join(stack + [u, v]))
        elif mark[v] == WHITE:
            dfs(v, stack + [u])
    mark[u] = BLACK


for i in ids:
    if mark[i] == WHITE:
        dfs(i, [])

# ── gate 3b: notation lint — literal caret powers in a lesson
for x in CONCEPTS:
    for m in re.finditer(r'\^', x["body"]):
        errors.append("%s: caret notation %r in body" % (x["id"], x["body"][m.start():m.start() + 10]))

# ── gate 3c: non-calculator lint ------------------------------------------
# Round 0 is non-calculator, so a lesson may only show a decimal the reader can
# produce by hand. Accept if it is (a) at most 2 significant figures, (b) exactly a
# fraction with denominator <= 20, or (c) listed below with the hand route. Everything
# else fails, so a calculator-only number cannot creep into the teaching layer.
CALC_OK = {
    # memorised constants, and the rounded forms of them used for comparison
    "1.414": "sqrt2, standard",       "1.41":  "sqrt2 rounded, in the 'worth memorising' list",
    "1.732": "sqrt3, standard",       "1.73":  "sqrt3 rounded, in the 'worth memorising' list",
    "2.236": "sqrt5, standard",       "2.24":  "sqrt5 rounded, in the 'worth memorising' list",
    "3.162": "sqrt10, standard",      "3.14":  "pi to 3 s.f.",
    "0.693": "ln 2, standard",        "0.301": "log10 2, standard",
    "0.707": "1/sqrt2, in the 'worth memorising' list",
    "0.477": "log10 3, quoted only to show that the base matters",
    "6.02":  "Avogadro's number, 6.02 x 10^23",
    "6.63":  "Planck's constant, 6.63 x 10^-34",
    "1.33":  "refractive index of water, a datum",
    # recovered by squaring a 2-dp candidate, with the square shown
    "4.84":  "2.2^2,  the squaring check",   "5.29":  "2.3^2, the squaring check",
    "5.018": "2.24^2, the squaring check",
    # one small-integer division
    "2.286": "16/7, shown as '= 16/7 = 2.286'",
    # numbers the text explicitly tells you not to use, or not to write
    "4.1667": "25/6, named in the sentence 'the worst one: doing a long multiplication'",
    "1.585":  "log2 3, in the sentence 'worth knowing the size'",
    "0.585":  "log2(3/2), same sentence",
    "0.354":  "1/(2*sqrt2), followed immediately by 'Stop here ... left unnumbered'",
    "1.118":  "sqrt5/2, named as the wrong thing to write instead of the surd",
    "0.583":  "7/12, named as the wrong thing to write instead of the fraction",
    "1.07":   "2*sqrt2/sqrt7, shown as 2.83/2.65 to compare two options",
    "1.51":   "4/sqrt7, the same comparison",
    "2.65":   "sqrt7, from 2.65^2 = 7.02",
    "2.83":   "2*sqrt2 = 2 x 1.414, the upper bracket",
}
# Numbers only a calculator produces. These may appear ONLY where the surrounding
# text tells the reader not to compute them -- that is the whole point of printing
# 20.7 degrees at all. A bare one is a defect.
CALC_FLAGGED = {"41.4", "48.6", "20.7", "1.585", "0.585", "4.1667"}
FLAG_PHRASES = [
    "without a calculator", "would need a calculator", "nothing here needs",
    "no step above needed", "for the record", "never have to write down",
    "not asked for", "left unnumbered", "do not evaluate", "rather than evaluate",
    "stop there", "reach for a decimal", "on a calculator",
]

for x in CONCEPTS:
    txt = re.sub(r'<[^>]+>', ' ', x["body"])
    for m in re.finditer(r'(?<![\w.])(\d+\.\d+)(?![\w])', txt):
        v = m.group(1)
        if v in CALC_OK:
            continue
        if len(v.replace('.', '').lstrip('0')) <= 2:
            continue
        # simple in BOTH parts: 20.7 is 207/10, so a denominator-only test would
        # wave through every one-decimal number
        fr = Fraction(v)
        if fr.denominator <= 20 and fr.numerator <= 40:
            continue
        # Scope the flag test to the ENCLOSING SENTENCE, not a fixed window: a bare
        # "20.7" must not pass because a flagged one sits sixty characters away.
        _a = max(txt.rfind('.', 0, m.start()), txt.rfind('!', 0, m.start()),
                 txt.rfind('?', 0, m.start()))
        _ends = [e for e in (txt.find('.', m.end()), txt.find('!', m.end()),
                             txt.find('?', m.end())) if e >= 0]
        _b = min(_ends) if _ends else len(txt)
        sent = txt[_a + 1:_b + 1].lower()
        if v in CALC_FLAGGED:
            if any(ph in sent for ph in FLAG_PHRASES):
                continue
            errors.append("%s: %s is calculator-only and nothing in its sentence says so -- %s"
                          % (x["id"], v, ' '.join(txt[_a + 1:_b + 1].split())[:95]))
            continue
        ctx = txt[max(0, m.start() - 60):m.end() + 30].replace('\n', ' ')
        errors.append("%s: decimal %s is neither 2-sig-fig nor a small fraction nor in "
                      "CALC_OK -- %s" % (x["id"], v, ' '.join(ctx.split())[:85]))

# ── gate 4: the question → key-point mapping resolves both ways
for qid, ks in KEYS.items():
    if len(set(ks)) != len(ks):
        errors.append("%s: repeated key point" % qid)
    for k in ks:
        if k not in by_id:
            errors.append("%s: unknown key point %r" % (qid, k))

used_by = {i: [] for i in ids}
for qid in sorted(KEYS):
    for k in KEYS[qid]:
        if k in used_by:
            used_by[k].append(qid)
for i in ids:
    if not used_by[i]:
        errors.append("concept %s is not used by any question" % i)

if errors:
    print("GATE FAILED:")
    for e in errors:
        print("  -", e)
    raise SystemExit(1)


def js_str(s):
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def arr(items):
    return "[" + ", ".join('"%s"' % i for i in items) + "]"


lines = []
lines.append("/* BPhO Round 0 — key points.")
lines.append("")
lines.append("   Generated by tools/paper2025/build_concepts.py from concepts_a/b/c.py. Edit those,")
lines.append("   never this file. Each entry is a self-contained lesson written for someone meeting")
lines.append("   the idea for the first time: what the quantity is, where the formula comes from,")
lines.append("   what each symbol and unit means, and the trap the paper is setting.")
lines.append("")
lines.append("   `stage` orders the course (0 toolkit · 1 mechanics · 2 materials & thermal ·")
lines.append("   3 waves & optics · 4 electricity · 5 quantum & nuclear). `pre` lists what must be")
lines.append("   read first; it is acyclic and never points at a later stage. `q` is the reverse")
lines.append("   index: which of the 25 past-paper questions use this point.")
lines.append("")
lines.append("   %d key points, used %d times across the paper." % (len(CONCEPTS), sum(len(v) for v in used_by.values())))
lines.append("*/")
lines.append("window.BPHO_CONCEPTS = [")

order = sorted(CONCEPTS, key=lambda x: (x["stage"], ids.index(x["id"])))
for n, x in enumerate(order):
    lines.append("  {")
    lines.append('    id: "%s", m: "%s", stage: %d, t: "%s",' % (x["id"], x["m"], x["stage"], x["t"]))
    lines.append("    pre: %s," % arr(x["pre"]))
    lines.append('    one: "%s",' % js_str(x["one"]).replace('"', "'"))
    lines.append("    body: `%s`," % js_str(x["body"]))
    lines.append('    used: "%s",' % js_str(x["used"]).replace('"', "'"))
    lines.append("    q: %s" % arr(sorted(used_by[x["id"]])))
    lines.append("  }" + ("," if n < len(order) - 1 else ""))
lines.append("];")
lines.append("")
lines.append("/* question → key points, the forward direction of the same index */")
lines.append("window.BPHO_QKEYS = {")
for n, qid in enumerate(sorted(KEYS)):
    lines.append('  "%s": %s%s' % (qid, arr(KEYS[qid]), "," if n < len(KEYS) - 1 else ""))
lines.append("};")
lines.append("")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("concepts:", len(CONCEPTS), "→", OUT)
print("links:   ", sum(len(v) for v in used_by.values()))
for st in sorted(set(x["stage"] for x in CONCEPTS)):
    grp = [x for x in order if x["stage"] == st]
    print("  stage %d: %2d  %s" % (st, len(grp), ", ".join(x["id"] for x in grp)))
