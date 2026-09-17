# -*- coding: utf-8 -*-
"""Assemble q1..q5 + generated figures into bpho/data/questions-4.js."""
import re, os, sys, json
sys.path.insert(0, '/tmp/bpho25')
import q1, q2, q3, q4, q5
from keys import KEYS

FIGDIR = '/tmp/bpho25/fig'
QS = q1.QUESTIONS + q2.QUESTIONS + q3.QUESTIONS + q4.QUESTIONS + q5.QUESTIONS
QS.sort(key=lambda d: d['n'])

OFFICIAL = dict(zip(range(1, 26),
    "E C C B C B C E A A "
    "A A D D B B E A C D "
    "A A B A E".split()))
LET = "ABCDE"


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
os.makedirs('/tmp/bpho25/out', exist_ok=True)
open('/tmp/bpho25/out/questions-4.js', 'w', encoding='utf-8').write(out)
print("wrote /tmp/bpho25/out/questions-4.js", len(out), "bytes")
