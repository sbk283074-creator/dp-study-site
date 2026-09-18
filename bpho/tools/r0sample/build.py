# -*- coding: utf-8 -*-
"""Assemble qs.py + the generated figures into bpho/data/questions-5.js.

Run:  python build.py      (from tools/r0sample)
Gate: answer vs the independently derived key · sol states the same letter ·
      five distinct options · no leftover figure placeholders · no caret or ASCII
      exponents · every decimal hand-computable · ids unique · n = 1..12.
"""
import io
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import qs
from keys import KEYS

FIGDIR = os.path.join(HERE, 'fig')
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'data', 'questions-5.js'))

QS = sorted(qs.QUESTIONS, key=lambda d: d['n'])

# The key derived from first principles and from the printed figures, then checked
# against the sheet's own geometry. See the qs.py docstring for the four questions
# that are only decidable from the drawing (S3, S6, S7, S8).
#
# NOTE: unlike the past paper this is NOT a copy of a printed answer key -- BPhO
# publishes the sample questions without one. It is our own derivation, so it is
# recorded here as the single source of truth that the gate compares against.
OFFICIAL = dict(zip(range(1, 13), "B B A B B D D E E B B D".split()))
LET = "ABCDE"
EXPECTED = "BBABBDDEEBBD"

# ── non-calculator allowlist ──────────────────────────────────────────────
# Round 0 is non-calculator, so every decimal in visible text must be one the reader
# can produce by hand. Accept if it is (a) at most 2 significant figures, (b) exactly
# a fraction with denominator <= 20, or (c) listed here with the hand route stated.
CALC_OK = {}

# Numbers only a calculator produces. These may appear ONLY where the surrounding
# sentence tells the reader not to compute them. A bare one is a defect.
CALC_FLAGGED = set()
FLAG_PHRASES = [
    "without a calculator", "would need a calculator", "nothing here needs",
    "no step above needed", "for the record", "never have to write down",
    "not asked for", "left unnumbered", "do not evaluate", "rather than evaluate",
    "stop there", "reach for a decimal", "on a calculator",
]


def load_fig(key):
    p = os.path.join(FIGDIR, key + '.svg')
    if not os.path.exists(p):
        raise SystemExit("missing figure " + key)
    return io.open(p, encoding='utf-8').read().rstrip()


def expand(text, used):
    def rep(m):
        key = m.group(1)
        used.add(key)
        return load_fig(key)
    return re.sub(r'\{\{FIG:([A-Za-z0-9\-]+)\}\}', rep, text)


# `x^n` and `x^(n/m)` read as literal carets on screen. Turn them into real superscripts.
_SUP = re.compile(r'([A-Za-z0-9\)\]])\^\(?([^()<>\s,;]+)\)?')


def supify(text):
    return _SUP.sub(lambda m: m.group(1) + '<sup>' + m.group(2) + '</sup>', text)


def js_str(s):
    """Content for a JS template literal."""
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')


def quote_list(items):
    return '[' + ', '.join('`' + js_str(it) + '`' for it in items) + ']'


errors = []
used_figs = set()
blocks = []

for d in QS:
    q = expand(supify(d['stem']), used_figs)
    opts = [expand(supify(o), used_figs) for o in d['opts']]
    sol = expand(supify(d['sol']), used_figs)
    trap = supify(d['trap'])

    # --- gate 1: answer letter agrees with the derived key
    want = OFFICIAL[d['n']]
    if LET[d['ans']] != want:
        errors.append("%s: bank says %s, derived key says %s" % (d['id'], LET[d['ans']], want))
    # --- gate 2: the worked solution states the same letter
    found = re.findall(r'Answer: ([A-E])', sol)
    if not found:
        errors.append("%s: solution never states 'Answer: <letter>'" % d['id'])
    elif found[-1] != want:
        errors.append("%s: solution says %s, derived key says %s" % (d['id'], found[-1], want))
    # --- gate 3: options well-formed
    if len(opts) != 5:
        errors.append("%s: %d options" % (d['id'], len(opts)))
    if len(set(opts)) != len(opts):
        errors.append("%s: duplicate option text" % d['id'])
    # --- gate 4: no leftover placeholders, and every question is keyed
    for label, txt in (('stem', q), ('sol', sol), *[('opt%d' % i, o) for i, o in enumerate(opts)]):
        if '{{FIG' in txt:
            errors.append("%s: unresolved figure placeholder in %s" % (d['id'], label))
    if d['id'] not in KEYS:
        errors.append("%s: no key points assigned" % d['id'])
    # --- gate 5: notation lint — literal caret powers and ASCII unit exponents
    for label, txt in (('stem', q), ('sol', sol), ('trap', trap)):
        for m in re.finditer(r'[A-Za-z0-9\)\]]\^', txt):
            errors.append("%s: caret notation %r in %s" % (d['id'], txt[m.start():m.start() + 8], label))
        for m in re.finditer(r'\b[mMs]\s*-\s*[123]\b', txt):
            errors.append("%s: ascii exponent %r in %s" % (d['id'], m.group(0), label))

    # --- gate 5b: non-calculator lint -------------------------------------
    # Every decimal in the visible text must be one the reader can produce by hand.
    # NOTE: the SVG is deliberately NOT stripped. A figure label is exactly as visible
    # as a sentence, and on the past paper an evaluated 20.7 degrees sat in an axis
    # label where no candidate could produce it.
    def visible(t):
        return re.sub(r'<[^>]+>', ' ', t)

    for label, txt in (('stem', q), ('sol', sol), ('trap', trap)):
        vt = visible(txt)
        for m in re.finditer(r'(?<![\w.])(\d+\.\d+)(?![\w])', vt):
            v = m.group(1)
            if v in CALC_OK:
                continue
            if len(v.replace('.', '').lstrip('0')) <= 2:
                continue
            # A "simple fraction" must be simple in BOTH parts: 20.7 is 207/10, whose
            # denominator is 10, so a denominator-only test waves through every
            # one-decimal number.
            fr = Fraction(v)
            if fr.denominator <= 20 and fr.numerator <= 40:
                continue
            # Scope the flag test to the ENCLOSING SENTENCE, not a fixed window.
            a = max(vt.rfind('.', 0, m.start()), vt.rfind('!', 0, m.start()),
                    vt.rfind('?', 0, m.start()))
            ends = [e for e in (vt.find('.', m.end()), vt.find('!', m.end()),
                                vt.find('?', m.end())) if e >= 0]
            b = min(ends) if ends else len(vt)
            sent = vt[a + 1:b + 1].lower()
            if v in CALC_FLAGGED:
                if any(ph in sent for ph in FLAG_PHRASES):
                    continue
                errors.append("%s: %s in %s is calculator-only and nothing in its sentence says so -- %s"
                              % (d['id'], v, label, ' '.join(vt[a + 1:b + 1].split())[:95]))
                continue
            errors.append("%s: decimal %s in %s is neither 2-sig-fig nor a small fraction "
                          "nor in CALC_OK -- %s"
                          % (d['id'], v, label, ' '.join(vt[max(0, m.start() - 60):m.end() + 30].split())[:85]))

    rel = ',\n    '.join('["%s", "%s"]' % (a, b) for a, b in d['rel'])
    kp = ', '.join('"%s"' % k for k in KEYS[d['id']]) if d['id'] in KEYS else '"MISSING"'
    blocks.append(
        "{\n"
        "  id: \"%s\", module: \"%s\", topic: \"%s\", diff: %d, paper: \"R0-SAMPLE\",\n"
        "  rel: [\n    %s\n  ],\n  key: [%s],\n"
        "  q: `%s`,\n"
        "  opts: %s,\n"
        "  ans: %d,\n"
        "  sol: `%s`,\n"
        "  trap: \"%s\"\n"
        "}" % (d['id'], d['module'], d['topic'], d['diff'], rel, kp,
               js_str(q), quote_list(opts), d['ans'], js_str(sol),
               js_str(trap).replace('"', "'")))

# --- gate 6: whole-set invariants
ids = [d['id'] for d in QS]
if len(set(ids)) != len(ids):
    errors.append("duplicate ids")
if [d['n'] for d in QS] != list(range(1, 13)):
    errors.append("question numbers are not 1..12 in order")
dist = {L: sum(1 for d in QS if LET[d['ans']] == L) for L in LET}

# The 2025 paper uses all five letters, so the past paper's build gates on that. This
# sheet does NOT: it is a 12-question sample with no obligation to be uniform, and it
# genuinely has no answer C. Asserting "every letter appears" here would fail a
# correct bank, and "fixing" the bank to satisfy it would falsify the record. So the
# gate pins the derived distribution exactly instead -- any future edit that flips an
# answer is caught, which is what the gate was ever for.
got = ''.join(LET[d['ans']] for d in QS)
if got != EXPECTED:
    errors.append("answer sequence is %s, derived key is %s" % (got, EXPECTED))
if dist['C'] != 0:
    errors.append("a C answer appeared: the sample sheet has none")

all_figs = {f[:-4] for f in os.listdir(FIGDIR) if f.endswith('.svg')}
unused = sorted(all_figs - used_figs)

print("questions:", len(QS))
print("answer sequence:", got, dist)
print("figures used:", len(used_figs), sorted(used_figs), " unused:", unused)
if errors:
    print("\n!! GATE FAILED (%d)" % len(errors))
    for e in errors:
        print("   -", e)
    sys.exit(1)
print("\nall gates passed")

HEAD = """/* BPhO Round 0 — the 2025 SAMPLE QUESTIONS (S1..S12), rebuilt 2026-09-18.
   The sheet BPhO publishes so candidates can see the style before sitting the paper.
   Twelve single-answer MCQs, non-calculator, no negative marking -- the same format as
   the real thing, just shorter.

   There is no printed answer key for these, so every answer below was derived
   independently and cross-checked against the printed figure. Four of the twelve are
   only decidable from the drawing: the polarity of both cells in S3, the exponent in
   S6, where the extra load sits in S7, and the curvature in S8. Each of those is
   explained inside its own worked solution.

   `rel` lists the modules and topics each question draws on, `key` names the key
   points it turns on (lessons in data/concepts.js), and `paper:"R0-SAMPLE"` lets
   `startMockPaper("R0-SAMPLE", mode)` rebuild the sheet in order.

   Diagrams are inline SVG generated from measured geometry in tools/r0sample/figs.py,
   not traced by hand. */

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([

/* ===================== 2025 Round 0 sample questions ===================== */
/* Derived key:  B B A B B D D E E B B D   (no C -- a 12-question sample has no
   obligation to be uniform; see tools/r0sample/build.py gate 6)  */

"""

out = HEAD + ",\n\n".join(blocks) + "\n\n]);\n"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, 'w', encoding='utf-8').write(out)
print("wrote", OUT, len(out), "bytes")
