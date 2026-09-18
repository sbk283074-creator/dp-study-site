# -*- coding: utf-8 -*-
"""Assemble q1..q5 + generated figures into bpho/data/questions-4.js."""
import io, re, os, sys, json
from fractions import Fraction

# Everything resolves beside this file. The generator used to import from and read
# figures out of /tmp/bpho25, which made the committed questions-4.js unreproducible
# as soon as /tmp was cleared.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q1, q2, q3, q4, q5
from keys import KEYS

FIGDIR = os.path.join(HERE, 'fig')
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'data', 'questions-4.js'))
QS = q1.QUESTIONS + q2.QUESTIONS + q3.QUESTIONS + q4.QUESTIONS + q5.QUESTIONS
QS.sort(key=lambda d: d['n'])

OFFICIAL = dict(zip(range(1, 26),
    "E C C B C B C E A A "
    "A A D D B B E A C D "
    "A A B A E".split()))
LET = "ABCDE"

# ── non-calculator allowlist ──────────────────────────────────────────────
# Round 0 is non-calculator, so every decimal in the visible text of a solution
# must be one the reader can produce by hand. Gate 5b accepts a decimal if it is:
#   (a) at most 2 significant figures      -- reading off a graph, halving, given data;
#   (b) exactly a fraction with denominator <= 20  -- pure mental arithmetic;
#   (c) listed below, where the entry states the hand route.
# An entry here is a CLAIM that the number is hand-computable, so the comment has
# to say how. Anything else fails the build.
CALC_OK = {
    # ── irrational constants worth knowing ────────────────────────────────
    "1.414":  "sqrt2, standard",
    "1.732":  "sqrt3, standard",
    "1.73":   "sqrt3 to 2 dp, shown as a rough size only",
    # ── recovered by squaring a 2-dp candidate (the text shows the check) ─
    "2.236":  "sqrt5, from 2.236^2 = 5.00",
    "2.65":   "sqrt7, from 2.65^2 = 7.02",
    # ── one small-integer division ────────────────────────────────────────
    "1.14":   "8/7",
    "2.29":   "16/7",
    "2.67":   "8/3",
    "5.33":   "16/3, from 40/7.5 = 400/75",
    "7.02":   "2.65^2, the squaring check",
    # ── one operation on a memorised constant ─────────────────────────────
    "2.83":   "2*sqrt2 = 2 x 1.414",
    "0.354":  "1/(2*sqrt2) = 1/2.83",
    "0.764":  "3 - sqrt5 = 3 - 2.236",
    "0.382":  "(3 - sqrt5)/2 = 0.764/2",
    "1.118":  "sqrt5/2 = 2.236/2",
    "2.268":  "3 - 2(0.366), one subtraction",
    # ── squaring checks, each shown with its square ───────────────────────
    "4.84":   "2.2^2,  the squaring check",
    "5.29":   "2.3^2,  the squaring check",
    "5.018":  "2.24^2, the squaring check",
    "5.14":   "2.268^2, the squaring check",
    "1.69":   "1.3^2,  the squaring check",
    "1.742":  "1.32^2, the squaring check",
    "1.32":   "3^(1/4), by squaring candidates: 1.3^2 = 1.69 low, 1.32^2 = 1.742 high",
    "1.316":  "3^(1/4), same squaring bracket, quoted as 'about'",
    # ── option values read off the paper, never computed ─────────────────
    "1.069":  "option A as printed",
    "0.366":  "option A as printed",
    # ── numbers the text explicitly tells you NOT to compute ─────────────
    "1.633":  "sqrt(8/3), quoted only as an upper bound",
}

# ── numbers only a calculator produces ────────────────────────────────────
# These may appear ONLY where the surrounding text tells the reader not to
# compute them — that is the point of printing them at all: the sentence around
# 41.4 degrees is teaching that you do not need it. A bare one is a defect.
CALC_FLAGGED = {"41.4", "48.6", "20.7", "1.585", "0.585", "4.1667"}

# Any of these within reach of the number counts as flagging it.
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
    return open(p, encoding='utf-8').read().rstrip()


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
    return s.replace('\\', '\\\\').replace('`', "\\`").replace('${', '\\${')


def quote_list(items):
    out = []
    for it in items:
        out.append('`' + js_str(it) + '`')
    return '[' + ', '.join(out) + ']'


errors = []
used_figs = set()
blocks = []
for d in QS:
    q = expand(supify(d['stem']), used_figs)
    opts = [expand(supify(o), used_figs) for o in d['opts']]
    sol = expand(supify(d['sol']), used_figs)
    trap = supify(d['trap'])

    # --- gate 1: answer letter agrees with the official key
    want = OFFICIAL[d['n']]
    if LET[d['ans']] != want:
        errors.append("%s: bank says %s, official key says %s" % (d['id'], LET[d['ans']], want))
    # --- gate 2: the worked solution states the same letter
    found = re.findall(r'Answer: ([A-E])', sol)
    if not found:
        errors.append("%s: solution never states 'Answer: <letter>'" % d['id'])
    elif found[-1] != want:
        errors.append("%s: solution says %s, official key says %s" % (d['id'], found[-1], want))
    # --- gate 3: options well-formed
    if len(opts) != 5:
        errors.append("%s: %d options" % (d['id'], len(opts)))
    if len(set(opts)) != len(opts):
        errors.append("%s: duplicate option text" % d['id'])
    # --- gate 4: no leftover placeholders
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
    # Round 0 is non-calculator. Every decimal in the visible text of a solution
    # must therefore be one the reader can produce by hand. See CALC_OK above.
    # NOTE: the SVG is deliberately NOT stripped here. A figure label is just as
    # visible as a sentence, and one of them was printing an evaluated 20.7 degrees
    # as an angle label — a number no candidate can produce. Stripping the SVG first
    # (as an earlier version did) hides exactly that class of defect. Only the
    # attribute text inside tags is removed.
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
            # A "simple fraction" must be simple in BOTH parts. 20.7 is 207/10, whose
            # denominator is 10 -- so a denominator-only test waves through every
            # one-decimal number, which is how 20.7 sat in a figure label unnoticed.
            fr = Fraction(v)
            if fr.denominator <= 20 and fr.numerator <= 40:
                continue
            # Scope the flag test to the ENCLOSING SENTENCE, not a fixed window. A
            # window is too coarse: a bare "20.7" will pass simply because a legitimately
            # flagged "rather than evaluate 20.7" sits sixty characters away.
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
    kp = d['id'] not in KEYS and 'MISSING' or ', '.join('"%s"' % k for k in KEYS[d['id']])
    blocks.append(
        "{\n"
        "  id: \"%s\", module: \"%s\", topic: \"%s\", diff: %d, paper: \"R0-2025\",\n"
        "  rel: [\n    %s\n  ],\n  key: [%s],\n"
        "  q: `%s`,\n"
        "  opts: %s,\n"
        "  ans: %d,\n"
        "  sol: `%s`,\n"
        "  trap: \"%s\"\n"
        "}" % (d['id'], d['module'], d['topic'], d['diff'], rel, kp,
               js_str(q), quote_list(opts), d['ans'], js_str(sol),
               js_str(trap).replace('"', "'")))

# --- gate 6: whole-bank invariants
ids = [d['id'] for d in QS]
if len(set(ids)) != len(ids):
    errors.append("duplicate ids")
if [d['n'] for d in QS] != list(range(1, 26)):
    errors.append("question numbers are not 1..25 in order")
dist = {L: sum(1 for d in QS if LET[d['ans']] == L) for L in LET}
for L in LET:
    if dist[L] == 0:
        errors.append("no question has answer " + L)

all_figs = {f[:-4] for f in os.listdir(FIGDIR) if f.endswith('.svg')}
unused = sorted(all_figs - used_figs)

print("questions:", len(QS))
print("answer spread:", dist, "(official paper distribution)")
print("figures used:", len(used_figs), " unused:", unused)
if errors:
    print("\n!! GATE FAILED (%d)" % len(errors))
    for e in errors:
        print("   -", e)
    sys.exit(1)
print("\nall gates passed")

HEAD = """/* BPhO Round 0 — the 2025 past paper, rebuilt 2026-09-17.
   This is the only real Round 0 paper in existence, so it is the single best guide to what the
   exam actually asks: 25 single-answer MCQs, 60 minutes, no calculator, no negative marking.

   Every one of the 25 answers below has been checked against the official answer key printed on
   page 10 of the paper, and every worked solution states its letter explicitly. `rel` lists the
   modules and topics each question actually draws on, so the site can surface the topics that
   really come up. Each question carries `paper:"R0-2025"` so
   `startMockPaper("R0-2025", mode)` can assemble them in paper order.

   `key` names the key points each question turns on; the lessons behind them live in
   data/concepts.js. Each has a full lesson in tools/paper2025/concepts_a/b/c.py.

   Diagrams are inline SVG generated from computed geometry (angles from Snell's law, node
   positions from the printed figure) rather than traced by hand. */

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([

/* ===================== 2025 Round 0 past paper ===================== */
/* Answer key as printed:  E C C B C B C E A A | A A D D B B E A C D | A A B A E  */

"""

out = HEAD + ",\n\n".join(blocks) + "\n\n]);\n"
io.open(OUT, 'w', encoding='utf-8').write(out)
print("wrote", OUT, len(out), "bytes")
