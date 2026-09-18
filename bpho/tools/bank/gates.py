# -*- coding: utf-8 -*-
"""The bank's quality gate.

WHAT THIS IS FOR
----------------
Writing 1000 competition questions is not a writing problem, it is a *control*
problem.  Anyone can produce 1000 plausible-looking MCQs; the difficulty is
producing 1000 that are each (a) correct, (b) genuinely hard, (c) not restatements
of each other, and (d) provably so.  This file is the instrument that decides those
four things, and it is deliberately built so that it can be *shown to fail* --
see mutants.py, which breaks known-good questions and asserts the gate catches
each break.

THE TEN GATES
-------------
  G1  structure        ids, counts, five distinct options, ans in range, module mix
                       matches the evidence-based section plan, required fields
  G2  distractors      every wrong option must encode a NAMED plausible error.
                       This is the gate that stops filler options, and filler
                       options are what separate a worksheet from a competition.
  G3  agreement        the solution's stated letter equals `ans`; notation lint
                       (no caret powers, no ASCII exponents); balanced markup;
                       and the non-calculator lint -- every decimal in visible text
                       must be hand-computable
  G4  profile          the authored reasoning profile must agree with the solution
                       text: you may not declare five steps for a two-step solution,
                       and you may not claim an approximation the solution does not use
  G5  difficulty       one scorer, calibrated on the real 2025 paper and the published
                       sample sheet.  A section's median must reach the 2025 paper's
                       median and no question may fall below its 25th percentile.
  G6  similarity       fingerprints the LOGIC, not the words: which relations are used,
                       in what shape, solved for what.  Near-duplicates are flagged
                       even when no sentence is shared.
  G7  numerics         every question declares a machine-checkable assertion, which is
                       re-evaluated here by an independent route (exact rational
                       arithmetic / symbolic equivalence / dimensional analysis)
  G8  figures          placeholders resolve; every drawn coordinate lies inside the
                       viewBox; marker ids unique across the section; no label struck
                       through by a curve or ray
  G9  balance          the answer letters are spread, as on the real paper
  G10 hand-check       the ledger of questions a human actually worked through

WHAT IT CANNOT DO
-----------------
It cannot tell whether a question is *interesting*, and it cannot verify physics
that has no computable consequence.  G5 is a proxy: it measures the shape of a
solution, not its elegance.  G7 only checks the route the author declared -- if the
author's route is wrong in the same way as the author's answer, G7 agrees with both.
That is exactly why G10 exists and why the ledger is not optional.  Every section
ships with hand-checked questions and the count is gated.

USAGE
-----
    python gates.py papers          # calibration table for the two real papers
    python gates.py sec01           # gate one section
    python gates.py all             # gate every section present
"""

from __future__ import annotations

import glob
import html as _html
import json
import math
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import spec  # noqa: E402

try:
    import sympy  # noqa: E402
    HAVE_SYMPY = True
except Exception:                                    # pragma: no cover
    HAVE_SYMPY = False

LET = "ABCDE"

# ── tunables, all in one place ───────────────────────────────────────────────

MIN_STEPS = {1: 2, 2: 3, 3: 4}          # declared reasoning steps, by difficulty
MIN_RELATIONS = {1: 1, 2: 2, 3: 2}      # distinct relations, by difficulty
MIN_INSIGHT = 40                        # characters
MIN_DISTRACTOR = 18                     # characters per named error
MIN_TRAP = 30

SIM_JACCARD = 0.62                      # logic-fingerprint overlap that counts as a duplicate
TEXT_SHINGLE = 0.42                     # secondary, cheap signal for accidental reuse
SHAPE_MAX = 5                           # questions allowed to share one reasoning shape
SHAPE_KINDS_MIN = 7                     # distinct shapes required in a 25-question section
LETTER_MIN = 2                          # each of A..E at least this often per section
LETTER_MAX = 10
TOP_QUARTILE_MIN = 6                    # questions at or above the 2025 paper's p75
HANDCHECK_MIN = 5                       # hand-worked questions required per section

SHAPES = {
    "ratio-cancellation", "limiting-case", "symmetry", "conservation",
    "dimensional-analysis", "graph-reading", "diagram-geometry", "algebraic-elimination",
    "superposition", "order-of-magnitude", "circuit-reduction", "units-consistency",
    "monotonicity", "proportionality", "combinatorial",
}

# ── the non-calculator allowlist, carried over from tools/r0sample/build.py ──
# Constants that any candidate for this paper carries in their head.  These are not
# computed values, so the lint has no business objecting to them.  The list is
# deliberately short: everything else must be an exact consequence of the data.
CALC_OK = {
    # pi and its common multiples
    "3.14", "3.142", "6.28", "6.283", "1.57", "9.42", "12.57",
    # square roots of the small integers
    "1.41", "1.414", "1.73", "1.732", "2.24", "2.236", "2.45", "2.65",
    "2.83", "3.16", "3.162",
    # g, to both the A-level and the olympiad habit
    "9.81", "9.8",
}
FLAG_PHRASES = [
    "without a calculator", "would need a calculator", "nothing here needs",
    "no step above needed", "for the record", "never have to write down",
    "not asked for", "left unnumbered", "do not evaluate", "rather than evaluate",
    "stop there", "reach for a decimal", "on a calculator", "a standard approximation",
]


def _sentence_at(t: str, pos: int) -> str:
    """The sentence containing position `pos`.

    A full stop only ends a sentence when whitespace or the end of the string follows
    it.  Otherwise the stop is a DECIMAL POINT, and splitting there cuts formulas in
    half -- which is exactly how "1.44" lost sight of the "1.2" it is the square of,
    and got reported as not hand-computable.
    """
    starts = [0] + [m.end() for m in re.finditer(r"[.!?](?=\s|$)", t)]
    a = max(s for s in starts if s <= pos)
    m = re.search(r"[.!?](?=\s|$)", t[a:])
    b = a + (m.end() if m else len(t) - a)
    return t[a:b]


def _hand_from_data(v: str, sent: str) -> bool:
    """Is this decimal an exact square or product of numbers already on the page?

    "1.44" is not a calculator output when the sentence also says "1.2": squaring a
    one-decimal number is mental arithmetic.  Without this rule the lint cannot tell
    an exact consequence from an evaluated root, and it objects to both.  It still
    rejects 0.4472 and 6.2831, which is what it is for.
    """
    try:
        target = Fraction(v)
    except (ValueError, ZeroDivisionError):
        return False
    nums = []
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w])", sent):
        try:
            nums.append(Fraction(m.group(1)))
        except ValueError:
            continue
    for a in nums:
        if a * a == target:
            return True
    for i, a in enumerate(nums):
        for b in nums[i + 1:]:
            if a * b == target:
                return True
    return False


# ═════════════════════════════════════════════════════════════════════════════
# text helpers
# ═════════════════════════════════════════════════════════════════════════════

def visible(t: str) -> str:
    """Tag-stripped text.  SVG is deliberately NOT removed: a figure label is exactly
    as visible as a sentence, and the 2025 paper's own defect was an evaluated angle
    sitting in an axis label where no candidate could have produced it."""
    return _html.unescape(re.sub(r"<[^>]+>", " ", t))


def norm_opt(s: str) -> str:
    """Option text reduced to what a candidate would read, for duplicate detection.

    Case is PRESERVED, deliberately.  The first version lowercased everything, which is
    the natural instinct for text comparison and is wrong for this domain: in physics the
    case IS part of the symbol.  `k` and `K`, `m` and `M`, `r` and `R` are different
    quantities, and `M` and `m` are even different prefixes on the same unit.  Folding
    case made S02-19's five genuinely distinct options -- k(1 - k/K), k(1 + k/K),
    k(1 - K/k), K(1 - k/K), k -- all read as "k(1 - k/k)" and reported three duplicates
    that do not exist.

    A candidate looking at that option list sees five different expressions, so a
    duplicate check that cannot see the difference is measuring the wrong reader.
    """
    s = visible(s)
    s = s.replace("−", "-").replace("–", "-").replace("×", "x").replace("·", "*")
    s = re.sub(r"\s+", " ", s)
    return s.strip().rstrip(".")


def tags_balanced(t: str) -> str | None:
    """Return an error string if the markup is unbalanced, else None."""
    void = {"br", "hr", "img", "input", "meta", "link", "path", "line", "circle",
            "rect", "polyline", "polygon", "use", "marker", "source"}
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>", t):
        closing, name, _attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if name in void or selfclose:
            continue
        if closing:
            if not stack:
                return "stray </%s>" % name
            if stack[-1] != name:
                return "expected </%s>, found </%s>" % (stack[-1], name)
            stack.pop()
        else:
            stack.append(name)
    if stack:
        return "unclosed <%s>" % stack[-1]
    return None


SUP_RE = re.compile(r"([A-Za-z0-9\)\];])\^(?:\(([^()<>]+)\)|([^()<>\s,;/]+))")


def supify(t: str) -> str:
    """`x^n` reads as a literal caret on screen.  Turn it into a real superscript.

    The base may end in `;`, because the base is usually an HTML ENTITY: `&lambda;^2`,
    `&omega;^2`, `&theta;^2`.  Without `;` in the class the repair silently skips every
    one of them -- the caret survives to the reader and only the lint notices, which is
    exactly how S02-03 was caught.

    The exponent comes in two forms, and they need separate alternatives:

      * parenthesised -- `e^(-kt)`, `r^(-3/2)`, `x^(a b)` -- which MAY contain a slash;
      * bare -- `x^2`, `10^-5`, `T^-1` -- which may NOT.

    A single class that allowed `/` in the bare form mis-parsed the most ordinary unit
    notation there is.  `m^2/s^2` matched `m` + `^` + `2/s`, swallowed the `/s`, and left
    an orphaned `^2` behind; `(3.0 x 10^8)^2` consumed the closing bracket as an optional
    trailing paren, so the following `)^2` had no base left to attach to.  Both were
    invisible in the source and only surfaced as surviving carets on S03-23.
    """
    return re.sub(SUP_RE,
                  lambda m: m.group(1) + "<sup>" + (m.group(2) or m.group(3)) + "</sup>",
                  t)


# Forms that must come out of supify with no caret left.  Asserted at run time, because
# the failure mode is a caret the reader sees and no test otherwise looks for.
SUP_FORMS = [
    "x^2", "10^-5", "T^-1", "&lambda;^2", "&omega;^2",
    "m^2/s^2", "m s^-2", "10^16 m^2/s^2", "(3.0 x 10^8)^2", "9.0 x 10^16",
    "e^(-kt)", "r^(-3/2)", "x^(a b)", "A^(1/3)", "(1 + x)^n", "V^2/R",
    "s^-1", "kg m^-3", "240^2/60", "2.0 x 10^-4 m^3", "r0^3",
]


def supify_selfcheck():
    """Raise if any known notation form leaves a caret behind."""
    bad = [f for f in SUP_FORMS if "^" in supify(f)]
    if bad:
        raise SystemExit("supify left a caret in: %s" % ", ".join(repr(b) for b in bad))


# ═════════════════════════════════════════════════════════════════════════════
# G5 -- the difficulty scorer
# ═════════════════════════════════════════════════════════════════════════════

STEP_RE = re.compile(r"Step\s*(\d+)\s*[—\-–:]")
FORMULA_RE = re.compile(r'class="formula"')
APPROX_RE = re.compile(r"≈|≪|for small|small angle|small parameter|to first order|"
                       r"first-order|second order|negligible|approximately|roughly|"
                       r"order of magnitude|power of ten|estimation", re.I)
SYM_OPT_RE = re.compile(r"[A-Za-z]\s*[/*^]|</?sup>|<code>|√|∝|π|θ|λ|ρ|σ|ε|μ|ω|α|β|γ|Δ")
# Where the solution stops reasoning and starts explaining the wrong answers.  Both
# headings are in use: Section 1 writes "Why the other four are wrong.", Section 2 writes
# "The distractors."  The approximation scan must stop here, because a bullet explaining
# a distractor mentions approximations in order to REJECT them -- "(5/2)sqrt(2h/g) adds
# three terms and stops, taking the tail to be negligible" is evidence that the intended
# path does NOT approximate.  Scanning through it flagged S02-04 as approximate when its
# whole point is the exact sum of a geometric series.
DISTRACTOR_RE = re.compile(
    r"<b>\s*(?:the\s+distractors|why\s+the\s+other\s+(?:four|three|two)\s+are\s+wrong"
    r"|why\s+the\s+others?\s+are\s+wrong|the\s+wrong\s+options?)\b", re.I)


def features(q: dict) -> dict:
    """Measure a question from its own text.  Works identically on a 2025 question and
    on a newly authored one -- that is the whole point, since the calibration has to be
    like-for-like."""
    sol = q.get("sol", "") or ""
    stem = q.get("q") or q.get("stem", "") or ""
    opts = q.get("opts", []) or []
    rel = q.get("rel", []) or []

    # Text-content regexes must run on the ENTITY-DECODED text.  The question data is
    # HTML, so "approximately" is written &asymp;, a root is &radic; and a theta is
    # &theta;.  Matching the raw source silently misses every one of them: the first
    # version of this function reported four questions as "does not approximate" when
    # their solutions plainly do.  Tag-structure regexes (STEP_RE, FORMULA_RE) still
    # need the raw text, so both are kept.
    vis_sol = visible(sol)

    steps = [int(m.group(1)) for m in STEP_RE.finditer(sol)]
    n_steps = max(steps) if steps else 0
    n_formula = len(FORMULA_RE.findall(sol))
    # How long is the reasoning chain?  Counting numbered "Step N" markers alone makes
    # the metric a measure of TYPOGRAPHY: the 2025 paper's own Q20 (the jerk graph) and
    # Q25 (the twelve-resistor network) are among its hardest questions and both score
    # near the bottom, purely because their solutions do not number their steps.  Each
    # <div class="formula"> block is normally one relation applied, so when the
    # numbering is absent the formula blocks are the better estimate of chain length.
    moves = n_steps if n_steps >= 2 else max(n_steps, n_formula)
    # The approximation flag describes the INTENDED path, so it is read off the reasoning
    # only -- never off the distractor commentary, which names approximations in order to
    # reject them.  See DISTRACTOR_RE.
    m_dis = DISTRACTOR_RE.search(sol)
    approx = bool(APPROX_RE.search(visible(sol[:m_dis.start()] if m_dis else sol)))
    fig = "<svg" in stem
    trap = len(visible(q.get("trap", "") or "").strip())
    sym_opts = sum(1 for o in opts if SYM_OPT_RE.search(visible(o)))
    symbolic = sym_opts >= 3
    relmods = len(set(str(m) for m, _ in rel))
    # does the solution actually eliminate the wrong options, or just assert the right one?
    elim = len(re.findall(r"·\s*<b>|·\s*<i>", sol))
    return {
        "n_steps": n_steps, "moves": moves, "n_formula": n_formula, "approx": approx,
        "fig": fig, "trap_len": trap, "symbolic": symbolic, "relmods": relmods,
        "elim": elim, "sol_len": len(vis_sol),
    }


def difficulty(q: dict) -> float:
    """A single number for 'how much work is this', in the same units for every
    question in the bank and in both real papers.

    The weights are a judgement, and they are recorded here rather than hidden:
    the length of the reasoning chain dominates, because that is what the paper is
    actually testing; a required approximation and a symbolic answer both add real
    load; a figure that must be read adds a little; a named trap adds a little.

    Two terms were REMOVED after measuring them against the real paper, because a
    metric the yardstick cannot earn is not a measurement:

      * "elim" counted the "· <b>option</b>" bullets in a solution.  It scored 0.00
        on all 25 questions of the 2025 paper and 2.40 on average on mine -- a free
        +2.40 for my own writing style, and it flattered my section by inflating the
        median gap against the real paper from +1.3 to +3.7.
      * "moves" was capped at 6.  The 2025 paper's hardest question walks 13 moves,
        so the cap truncated the real paper and nothing of mine, which again flattered
        my section.  The cap is now 12.
    """
    f = features(q)
    s = 0.0
    s += 1.60 * min(f["moves"], 12)
    s += 1.00 * min(f["n_formula"], 4)
    s += 2.00 * (1 if f["approx"] else 0)
    s += 1.50 * (1 if f["symbolic"] else 0)
    s += 1.00 * (1 if f["fig"] else 0)
    s += 0.80 * (1 if f["trap_len"] >= MIN_TRAP else 0)
    s += 1.20 * min(f["relmods"], 3)
    return round(s, 2)


def median(xs):
    xs = sorted(xs)
    if not xs:
        return 0.0
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def band_of(score: float, ref: dict) -> int:
    """The difficulty band a measured score falls in.

    The cut-points are the 2025 paper's OWN quartiles, so band 2 means "typical of the
    real paper" rather than "typical of this bank".  That makes the declared band on a
    question a consequence of the measurement instead of a claim about it -- which is
    what stops a section from being labelled easy while measuring hard, or the reverse.
    """
    if score <= ref["p25"]:
        return 1
    if score <= ref["p75"]:
        return 2
    return 3


def percentile(xs, p):
    xs = sorted(xs)
    if not xs:
        return 0.0
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def baseline(papers_json=None):
    """Score the two real papers.  This is the yardstick the brief implies by
    'the same or even harder than BPhO'."""
    p = papers_json or os.path.join(HERE, "papers.json")
    data = json.load(open(p, encoding="utf-8"))
    qs = data["questions"]
    out = {}
    for tag in sorted(set(q["paper"] for q in qs)):
        sc = [difficulty(q) for q in qs if q["paper"] == tag]
        out[tag] = {
            "n": len(sc), "median": median(sc), "p25": percentile(sc, 25),
            "p75": percentile(sc, 75), "min": min(sc), "max": max(sc), "scores": sc,
        }
    return out


# ═════════════════════════════════════════════════════════════════════════════
# G6 -- logic similarity
# ═════════════════════════════════════════════════════════════════════════════

REL_CANON = [
    (re.compile(r"v\s*=\s*u\s*\+\s*a\s*t|v\s*=\s*u\+at", re.I), "kin.vuat"),
    (re.compile(r"s\s*=\s*u\s*t\s*\+|s\s*=\s*½|s\s*=\s*1/2", re.I), "kin.suvat"),
    (re.compile(r"v\s*\^?2\s*=\s*u\s*\^?2\s*\+\s*2", re.I), "kin.v2u2as"),
    (re.compile(r"F\s*=\s*m\s*a", re.I), "force.ma"),
    (re.compile(r"\bW\s*=\s*F\s*d|\bW\s*=\s*F\s*s|work\s*=\s*force", re.I), "energy.work"),
    (re.compile(r"p\s*=\s*m\s*v|momentum\s*=\s*mass", re.I), "momentum.mv"),
    (re.compile(r"\bP\s*=\s*V\s*I|\bP\s*=\s*I\s*V", re.I), "elec.pvi"),
    (re.compile(r"\bV\s*=\s*I\s*R|V\s*=\s*IR", re.I), "elec.vir"),
    (re.compile(r"\bP\s*=\s*I\s*\^?2\s*R|I\s*\^?2\s*R", re.I), "elec.pi2r"),
    (re.compile(r"\bP\s*=\s*V\s*\^?2\s*/\s*R", re.I), "elec.pv2r"),
    (re.compile(r"\bQ\s*=\s*C\s*V", re.I), "elec.qcv"),
    (re.compile(r"E\s*=\s*h\s*f|hf\s*=\s*|h\s*f\s*=|photon energy", re.I), "quant.hf"),
    (re.compile(r"work function|φ\s*=|threshold frequency", re.I), "quant.workfn"),
    (re.compile(r"n\s*1\s*sin|sin\s*θ\s*1|snell|n\s*sin\s*θ\s*=", re.I), "optics.snell"),
    (re.compile(r"sin\s*θ\s*c\s*=|critical angle", re.I), "optics.crit"),
    (re.compile(r"1\s*/\s*f\s*=|f\s*=\s*1\s*/\s*T", re.I), "wave.freq"),
    (re.compile(r"v\s*=\s*f\s*λ|v\s*=\s*f\s*lambda|c\s*=\s*f\s*λ", re.I), "wave.vfl"),
    (re.compile(r"λ\s*=\s*2\s*L|wavelength.*half", re.I), "wave.string"),
    (re.compile(r"mv\s*\^?2\s*/\s*r|centripetal|F\s*=\s*m\s*ω", re.I), "circ.centripetal"),
    (re.compile(r"GM\s*/\s*r|gravitational field|g\s*=\s*GM", re.I), "grav.inverse"),
    (re.compile(r"E\s*=\s*m\s*c\s*\^?2", re.I), "nuc.emc2"),
    (re.compile(r"half-?life|λ\s*=\s*ln\s*2|decay constant", re.I), "nuc.halflife"),
    (re.compile(r"A\s*=\s*A\s*0\s*\(?1\s*/\s*2|A\s*=\s*A₀", re.I), "nuc.decay"),
    (re.compile(r"Q\s*=\s*m\s*c\s*Δ|specific heat|ΔT", re.I), "therm.shc"),
    (re.compile(r"latent heat|mL\b", re.I), "therm.latent"),
    (re.compile(r"ρ\s*=\s*m\s*/\s*V|density\s*=", re.I), "fluid.density"),
    (re.compile(r"p\s*=\s*ρ\s*g\s*h|pressure.*depth|ρgh", re.I), "fluid.hydro"),
    (re.compile(r"F\s*=\s*k\s*x|hooke", re.I), "mat.hooke"),
    (re.compile(r"Young|E\s*=\s*σ\s*/\s*ε|stress.*strain", re.I), "mat.young"),
    (re.compile(r"m\s*1\s*d\s*1\s*=\s*m\s*2\s*d\s*2|moments|lever", re.I), "stat.moments"),
    (re.compile(r"1\s*/\s*2\s*m\s*v\s*\^?2|½\s*m\s*v", re.I), "energy.ke"),
    (re.compile(r"m\s*g\s*h|potential energy", re.I), "energy.pe"),
    (re.compile(r"pressure\s*=\s*force\s*/\s*area|p\s*=\s*F\s*/\s*A", re.I), "fluid.press"),
    (re.compile(r"frequency.*ratio|same speed|wave speed", re.I), "wave.speed"),
    (re.compile(r"dimension|base unit|units of", re.I), "toolkit.dim"),
    (re.compile(r"\(1\s*\+\s*x\)\s*n|small angle|tan\s*θ\s*≈", re.I), "toolkit.approx"),
    (re.compile(r"power\s*=\s*energy\s*/\s*time|P\s*=\s*E\s*/\s*t", re.I), "energy.power"),
]


def rel_tokens(q: dict) -> set:
    """Canonical names of the physics relations a question actually uses, read from
    its solution text.  Canonicalising means two questions that use 'P = VI' and
    'P = I V' land on the same token."""
    blob = visible(q.get("sol", "") or "") + " " + visible(q.get("q") or q.get("stem", "") or "")
    out = set()
    for rx, name in REL_CANON:
        if rx.search(blob):
            out.add(name)
    return out


def fingerprint(q: dict) -> frozenset:
    """The logic of a question, as a set of positive features.  No words from the
    question's own prose: two questions with the same fingerprint are the same
    reasoning with the numbers changed, however differently they are written.

    The first version returned (shape, rel_tokens, depth, approx, fig) and scored it by
    Jaccard.  It did not work, and the reason is worth keeping: rel_tokens is nearly
    EMPTY (0-2 tokens per question, because most "rel" sentences are prose and match
    none of the canonical formula patterns), while depth/approx/fig are near-CONSTANTS
    across a section (depth 4, approx False, fig False for almost everything).  So the
    score came from one real feature plus three constants, and any two questions that
    happened to share a shape collided: S01-04 (a bullet embedding in a spring) and
    S01-14 (alpha decay) were reported as "the same reasoning chain" purely because
    both said "conservation" and both had four steps.

    Three changes fix that:
      * the curated `key` tags carry the concepts, and both corpora have them (2-5 per
        question), so they become the body of the fingerprint;
      * the chain length is bucketed, so it separates short from long rather than
        contributing the same constant to every pair;
      * a flag is added only when it is TRUE.  Two questions both not using an
        approximation do not thereby share reasoning.
    """
    f = features(q)
    prof = q.get("profile") or {}
    feats = set()
    for k in (q.get("key") or []):
        feats.add("key:" + str(k).strip().lower())
    for t in rel_tokens(q):
        feats.add("rel:" + t)
    if prof.get("shape"):
        feats.add("shape:" + str(prof["shape"]))
    n = f["n_steps"] or f["moves"]
    feats.add("depth:" + ("short" if n <= 2 else "mid" if n <= 4 else "long"))
    if f["approx"]:
        feats.add("approx")
    if f["symbolic"]:
        feats.add("symbolic")
    if f["fig"]:
        feats.add("fig")
    return frozenset(feats)


def fp_label(fp) -> str:
    """Readable rendering of a logic fingerprint for an error message.

    `fingerprint()` returns a frozenset, not a tuple.  The G6 message used to do
    `fingerprint(a)[0]`, which is a leftover from the 5-tuple version -- and because a
    passing section produces no G6 findings, that line never executed until the
    mutation test reached it.  A crash in the reporting path is still a crash.
    """
    items = sorted(fp)
    s = "{" + ", ".join(items) + "}"
    return s if len(s) <= 150 else s[:147] + "...}"


def jaccard(a, b) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))


def shingles(t: str, k: int = 5) -> set:
    words = re.findall(r"[a-z0-9]+", visible(t).lower())
    words = [w for w in words if w not in ("the", "a", "of", "is", "and", "to", "in", "that")]
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def text_overlap(a: dict, b: dict) -> float:
    sa = shingles((a.get("q") or a.get("stem", "")) + " " + a.get("sol", ""))
    sb = shingles((b.get("q") or b.get("stem", "")) + " " + b.get("sol", ""))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))


# ═════════════════════════════════════════════════════════════════════════════
# G7 -- independent re-evaluation
# ═════════════════════════════════════════════════════════════════════════════

DIM_BASE = ["kg", "m", "s", "A", "K", "mol", "cd"]
DIM_DERIVED = {
    "N": (1, 1, -2, 0, 0, 0, 0), "J": (1, 2, -2, 0, 0, 0, 0), "W": (1, 2, -3, 0, 0, 0, 0),
    "Pa": (1, -1, -2, 0, 0, 0, 0), "Hz": (0, 0, -1, 0, 0, 0, 0),
    "C": (0, 0, 1, 1, 0, 0, 0), "V": (1, 2, -3, -1, 0, 0, 0),
    "F": (-1, -2, 4, 2, 0, 0, 0), "Ω": (1, 2, -3, -2, 0, 0, 0),
    "T": (1, 0, -2, -1, 0, 0, 0), "H": (1, 2, -2, -2, 0, 0, 0),
    "ohm": (1, 2, -3, -2, 0, 0, 0),
}


def dim_of(expr: str):
    """Base-dimension vector of a unit expression like 'A^2 s^3 J^-1' or 'N/C'.

    Raises ValueError on anything it does not understand -- an unparsed dimension is a
    gate failure, never a silent pass.
    """
    s = _html.unescape(expr)
    s = s.replace("−", "-").replace("·", "*").replace("²", "^2").replace("³", "^3")
    s = s.replace("⁻", "-").replace("¹", "1").replace("⁰", "0")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        raise ValueError("empty unit expression")
    vec = [0] * 7
    # split into factors on * and /, keeping the operator
    s = s.replace(" ", "*") if (" " in s and "/" not in s and "*" not in s) else s
    tokens = re.findall(r"([*/]?)\s*([A-Za-zΩ]+)\s*(?:\^\s*(-?\d+))?", s)
    if not tokens:
        raise ValueError("cannot tokenize %r" % expr)
    for op, name, exp in tokens:
        e = int(exp) if exp not in (None, "") else 1
        if op == "/":
            e = -e
        if name in DIM_BASE:
            v = [0] * 7
            v[DIM_BASE.index(name)] = 1
        elif name in DIM_DERIVED:
            v = list(DIM_DERIVED[name])
        else:
            raise ValueError("unknown unit %r in %r" % (name, expr))
        for i in range(7):
            vec[i] += v[i] * e
    return tuple(vec)


def _sympify(t: str):
    """sympify with every free symbol declared POSITIVE.

    Without this, sympy leaves sqrt(u**2) as Abs(u) and a perfectly correct symbolic
    check reports a mismatch.  Every physical quantity here is positive, so the
    declaration is not a fudge -- it is the physics."""
    reserved = {"sqrt", "pi", "E", "I", "Rational", "Integer", "oo", "sin", "cos", "tan",
                "log", "exp", "Abs", "Symbol",
                # functions a physics check may legitimately call.  Anything not listed
                # here becomes a free Symbol, and then "floor(3.3)" fails with the
                # unhelpful "'Symbol' object is not callable".
                "floor", "ceiling", "Max", "Min", "sign", "factorial", "root",
                "asin", "acos", "atan", "atan2", "sinh", "cosh", "tanh", "ln",
                "Piecewise", "Eq", "Ne", "Sum", "Product", "N",
                # angle converters.  sympy has no `radians`/`degrees`, so an author who
                # writes a prism check the way the physics reads --
                # "2*degrees(asin(sqrt(2)*sin(radians(30)))) - 60" -- gets them bound as
                # free Symbols and the check dies with "'Symbol' object is not callable".
                # Supplying them is not a convenience: writing the check in the units the
                # problem is stated in is what makes it an independent route.
                "radians", "degrees"}
    names = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", t))
    local = {n: sympy.Symbol(n, positive=True) for n in names if n not in reserved}
    local.setdefault("radians", lambda d: sympy.sympify(d) * sympy.pi / 180)
    local.setdefault("degrees", lambda r: sympy.sympify(r) * 180 / sympy.pi)
    return sympy.sympify(t, locals=local)


def _is_boolean(x) -> bool:
    """True if sympy handed back a truth value rather than a number.

    `parse_expr` routes the text through Python's parser, so prose containing a Python
    keyword ("is not", "in", "and") silently becomes a bool.  Arithmetic on it then
    raises TypeError deep inside sympy, with a message that says nothing about the
    actual mistake."""
    try:
        return isinstance(x, sympy.logic.boolalg.BooleanAtom)
    except AttributeError:
        return isinstance(x, bool)


def _has_float(x) -> bool:
    """Does this expression contain an inexact number anywhere inside it?"""
    try:
        return bool(x.has(sympy.Float))
    except Exception:
        try:
            return isinstance(x, float)
        except Exception:
            return False


def _equal(a, b) -> bool:
    """Are two check results the same, allowing for inexact numbers?

    `simplify(got - want) != 0` is the right test for exact algebra, and the wrong test
    the moment a float appears: an author who writes an expected value as a decimal --
    "0.7071067811865476" for sqrt(2)/2 -- is stating the answer to the precision a
    double carries, and the subtraction leaves -5.55e-17 rather than 0.  Demanding
    bit-exactness there would fail a correct check for having been written in the units
    the question is stated in.

    So: exact when both sides are exact, and a tight RELATIVE tolerance (1e-9) as soon
    as either side is a float.  The tolerance is far tighter than any distinction a
    five-option paper can draw -- a genuinely wrong check is out by percent, not by
    parts in a billion -- so this cannot launder a wrong answer into a pass.
    """
    if _has_float(a) or _has_float(b):
        fa, fb = complex(sympy.N(a)), complex(sympy.N(b))
        return abs(fa - fb) <= 1e-9 * max(1.0, abs(fb), abs(fa))
    return sympy.simplify(a - b) == 0


def check_numeric(chk: dict) -> str | None:
    """Re-evaluate the author's assertion by a route that does not use the solution."""
    kind = chk.get("kind")
    if kind == "eval":
        if not HAVE_SYMPY:
            return "sympy unavailable, cannot run 'eval' check"
        try:
            got = sympy.simplify(_sympify(chk["expr"]))
            want = _sympify(chk["want"])
        except Exception as e:
            return "cannot parse check expression: %s" % e
        # A check that is not maths can still PARSE -- `parse_expr` runs the text through
        # Python's own parser first, so "this is not maths" comes back as the boolean
        # False (the `is not` identity operator), and then `False - 3` raises.  Report it
        # instead of crashing: a crash aborts the whole suite and hides every later
        # finding, which is precisely how the mutation test found this.
        if _is_boolean(got) or _is_boolean(want):
            return ("check expression did not evaluate to a number -- it parsed as %r "
                    "(bare truth value; the text probably contains a Python keyword "
                    "such as 'is not')" % (got,))
        # ONE comparison, guarded.  The previous version had the numeric branch inside a
        # try and then repeated the same comparison outside it, unguarded -- so anything
        # that was not a plain number took the unprotected path.
        try:
            if not _equal(got, want):
                return "check says %s but the expression evaluates to %s" % (want, got)
        except Exception as e:
            return "check could not be evaluated: %s" % e
        return None
    if kind == "sym":
        if not HAVE_SYMPY:
            return "sympy unavailable, cannot run 'sym' check"
        try:
            a = _sympify(chk["got"])
            b = _sympify(chk["want"])
        except Exception as e:
            return "cannot parse symbolic check: %s" % e
        if _is_boolean(a) or _is_boolean(b):
            return ("symbolic check did not evaluate to an expression -- parsed as %r"
                    % (a,))
        try:
            if not _equal(a, b):
                return "symbolic check failed: %s is not equal to %s" % (a, b)
        except Exception as e:
            return "symbolic check could not be evaluated: %s" % e
        return None
    if kind == "dim":
        try:
            a = dim_of(chk["got"])
            b = dim_of(chk["want"])
        except ValueError as e:
            return "dimensional check unparseable: %s" % e
        if a != b:
            return "dimensions differ: %s vs %s" % (a, b)
        return None
    return "unknown check kind %r" % kind


# ═════════════════════════════════════════════════════════════════════════════
# G8 -- figures
# ═════════════════════════════════════════════════════════════════════════════

TAG_RE = re.compile(r"<(line|rect|circle|path|polyline|polygon|text)\b([^>]*)>", re.S)
TEXT_EL = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)
ATTR = re.compile(r"([\w:-]+)\s*=\s*\"([^\"]*)\"")
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _attrs(s):
    return dict(ATTR.findall(s))


def arc_points(x0, y0, rx, ry, phi_deg, large, sweep, x1, y1, n=18):
    """Sample an SVG elliptical arc.  Handling this properly is not optional: a
    tokenizer that drops the 'A' command re-reads the arc's seven numbers as a line
    and *invents* a stroke across the figure, which is how a previous session spent an
    hour chasing a defect that did not exist."""
    if rx == 0 or ry == 0:
        return [(x0, y0), (x1, y1)]
    phi = math.radians(phi_deg)
    cosp, sinp = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x0 - x1) / 2.0, (y0 - y1) / 2.0
    x1p = cosp * dx2 + sinp * dy2
    y1p = -sinp * dx2 + cosp * dy2
    rx, ry = abs(rx), abs(ry)
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cosp * cxp - sinp * cyp + (x0 + x1) / 2.0
    cy = sinp * cxp + cosp * cyp + (y0 + y1) / 2.0

    def ang(ux, uy, vx, vy):
        d = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy) or 1)
        a = math.acos(max(-1.0, min(1.0, d)))
        return -a if ux * vy - uy * vx < 0 else a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    out = []
    for i in range(n + 1):
        th = th1 + dth * i / float(n)
        ex, ey = rx * math.cos(th), ry * math.sin(th)
        out.append((cosp * ex - sinp * ey + cx, sinp * ex + cosp * ey + cy))
    return out


def path_points(d: str):
    """Every point a stroke passes through."""
    toks = re.findall(r"([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:e-?\d+)?)", d)
    seq = []
    for cmd, num in toks:
        seq.append(cmd if cmd else float(num))
    pts, cur = [], (0.0, 0.0)
    i, cmd = 0, None
    while i < len(seq):
        if isinstance(seq[i], str):
            cmd = seq[i]
            i += 1
        if cmd is None:
            break
        up = cmd.upper()
        rel = cmd.islower()
        try:
            if up == "Z":
                cmd = None
                continue
            if up == "M":
                x, y = seq[i], seq[i + 1]
                i += 2
                cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
                pts.append(cur)
                cmd = "l" if rel else "L"
            elif up == "L":
                x, y = seq[i], seq[i + 1]
                i += 2
                nxt = (cur[0] + x, cur[1] + y) if rel else (x, y)
                pts += _lerp(cur, nxt)
                cur = nxt
            elif up == "H":
                x = seq[i]
                i += 1
                nxt = (cur[0] + x, cur[1]) if rel else (x, cur[1])
                pts += _lerp(cur, nxt)
                cur = nxt
            elif up == "V":
                y = seq[i]
                i += 1
                nxt = (cur[0], cur[1] + y) if rel else (cur[0], y)
                pts += _lerp(cur, nxt)
                cur = nxt
            elif up in ("C", "S", "Q", "T"):
                npar = {"C": 6, "S": 4, "Q": 4, "T": 2}[up]
                vals = seq[i:i + npar]
                i += npar
                if rel:
                    vals = [v + (cur[0] if k % 2 == 0 else cur[1]) for k, v in enumerate(vals)]
                end = (vals[-2], vals[-1])
                pts += _lerp(cur, end, 10)
                cur = end
            elif up == "A":
                rx, ry, rot, la, sw, x, y = seq[i:i + 7]
                i += 7
                end = (cur[0] + x, cur[1] + y) if rel else (x, y)
                pts += arc_points(cur[0], cur[1], rx, ry, rot, int(la), int(sw), end[0], end[1])
                cur = end
            else:
                i += 1
        except (IndexError, TypeError, ValueError):
            break
    return pts


def _lerp(a, b, n=6):
    return [(a[0] + (b[0] - a[0]) * k / float(n), a[1] + (b[1] - a[1]) * k / float(n))
            for k in range(1, n + 1)]


def svg_strokes(svg: str):
    """Every stroked point in the figure, plus the viewBox translation."""
    m = re.search(r'transform="translate\(([-\d.]+)[ ,]+([-\d.]+)\)"', svg)
    ox, oy = (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)
    pts = []
    for tm in re.finditer(r"<(line|path|polyline|polygon|circle|rect)\b([^>]*?)/?>", svg, re.S):
        tag, a = tm.group(1), _attrs(tm.group(2))
        try:
            if tag == "line":
                pts += _lerp((float(a["x1"]), float(a["y1"])), (float(a["x2"]), float(a["y2"])), 12)
            elif tag == "path":
                if a.get("fill", "none") != "none":
                    continue
                pts += path_points(a.get("d", ""))
            elif tag in ("polyline", "polygon"):
                v = [tuple(float(t) for t in p.split(",")) for p in a["points"].split()]
                for k in range(len(v) - 1):
                    pts += _lerp(v[k], v[k + 1], 6)
            elif tag == "circle":
                cx, cy, r = float(a["cx"]), float(a["cy"]), float(a["r"])
                if a.get("fill", "none") != "none":
                    continue
                for k in range(48):
                    th = 2 * math.pi * k / 48.0
                    pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
            elif tag == "rect":
                # a filled rect is a background panel, not a stroke: it must not be
                # treated as geometry that can cross a label sitting on top of it
                if a.get("fill", "none") != "none":
                    continue
                x, y, w, h = (float(a["x"]), float(a["y"]), float(a["width"]), float(a["height"]))
                for k in range(13):
                    pts += _lerp((x, y + h * k / 12.0), (x + w, y + h * k / 12.0), 4)
        except (KeyError, ValueError):
            continue
    return [(p[0] + ox, p[1] + oy) for p in pts], (ox, oy)


def svg_text_boxes(svg: str, oxy=(0.0, 0.0)):
    """Glyph-band boxes for every text label.

    The band is y - 0.74*fs .. y + 0.04*fs, NOT the full ascender/descender box.  A
    descender allowance makes every label that sits just above a boundary line a false
    positive, which buries the real hits."""
    ox, oy = oxy
    out = []
    for m in TEXT_EL.finditer(svg):
        a = _attrs(m.group(1))
        try:
            x, y = float(a["x"]) + ox, float(a["y"]) + oy
        except (KeyError, ValueError):
            continue
        fs = float(a.get("font-size", 12))
        body = _html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
        body = re.sub(r"\s+", " ", body).strip()
        if not body:
            continue
        w = max(1, len(body)) * fs * 0.55
        anchor = a.get("text-anchor", "start")
        if anchor == "middle":
            x0, x1 = x - w / 2, x + w / 2
        elif anchor == "end":
            x0, x1 = x - w, x
        else:
            x0, x1 = x, x + w
        out.append({"x0": x0, "x1": x1, "y0": y - 0.74 * fs, "y1": y + 0.04 * fs,
                    "text": body, "fs": fs, "y": y})
    return out


def figure_errors(key: str, svg: str, marker_ids: set):
    """Everything that can be checked about one figure without a human looking at it."""
    errs = []
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        return ["%s: no viewBox" % key]
    W, H = float(m.group(1)), float(m.group(2))
    if "<svg" not in svg:
        errs.append("%s: no <svg>" % key)
    if "aria-label=" not in svg:
        errs.append("%s: no aria-label (screen readers get nothing)" % key)
    if "xmlns=" not in svg:
        errs.append("%s: no xmlns" % key)
    if "<figure" not in svg:
        errs.append("%s: not wrapped in <figure class=\"fig\">" % key)

    # marker ids must be unique across the WHOLE section: HTML has no id namespace,
    # so two figures defining id="a" collide and one silently gets the wrong arrowhead
    for mid in re.findall(r'<marker[^>]*\bid="([^"]+)"', svg):
        if mid in marker_ids:
            errs.append("%s: marker id %r already used elsewhere in this section" % (key, mid))
        marker_ids.add(mid)
    for ref in set(re.findall(r"url\(#([^)]+)\)", svg)):
        if ref not in set(re.findall(r'<marker[^>]*\bid="([^"]+)"', svg)):
            errs.append("%s: reference to marker %r that this figure never defines" % (key, ref))

    strokes, oxy = svg_strokes(svg)
    boxes = svg_text_boxes(svg, oxy)

    # every drawn coordinate inside the box
    out = 0
    for (x, y) in strokes:
        if x < -0.5 or y < -0.5 or x > W + 0.5 or y > H + 0.5:
            out += 1
    for b in boxes:
        if b["x0"] < -0.5 or b["x1"] > W + 0.5 or b["y0"] < -0.5 or b["y1"] > H + 0.5:
            out += 1
    if out:
        errs.append("%s: %d coordinates outside the %gx%g viewBox (silently blank figure)"
                    % (key, out, W, H))

    # a curve or ray drawn THROUGH a label
    INSET = 0.5
    for b in boxes:
        hit = 0
        for (x, y) in strokes:
            if (b["x0"] + INSET) < x < (b["x1"] - INSET) and (b["y0"] + INSET) < y < (b["y1"] - INSET):
                hit += 1
        if hit >= 2:
            errs.append("%s: stroke passes through the label %r (%d sampled points)"
                        % (key, b["text"][:32], hit))

    # label over label
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
            oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
            if ox > 1.0 and oy > 0.5:
                errs.append("%s: labels %r and %r overlap by %.1fx%.1f"
                            % (key, a["text"][:22], b["text"][:22], ox, oy))
    return errs


def expand_figs(text: str, figdir: str, marker_ids: set, errs: list):
    """Replace {{FIG:key}} with the figure's SVG, gating each one."""
    def rep(m):
        key = m.group(1)
        p = os.path.join(figdir, key + ".svg")
        if not os.path.exists(p):
            # Tagged G8, not G3.  G3 owns malformed markup (a `{{FIG}}` with no key);
            # whether the named figure actually EXISTS is the figure gate's business.
            # This line used to be untagged, which meant the defect was real but could
            # not be attributed to any gate -- and the mutation test, which asserts a
            # specific gate fires, reported a false MISSED on a genuinely caught bug.
            errs.append("G8: a stem references figure %r, which does not exist" % key)
            return "<!-- MISSING FIGURE %s -->" % key
        svg = open(p, encoding="utf-8").read().rstrip()
        errs.extend(figure_errors(key, svg, marker_ids))
        return svg
    return re.sub(r"\{\{FIG:([A-Za-z0-9\-_]+)\}\}", rep, text)


# ═════════════════════════════════════════════════════════════════════════════
# the section gate
# ═════════════════════════════════════════════════════════════════════════════

def load_section(n: int):
    mod = __import__("sec%02d" % n)
    return mod


def gate_section(n: int, base=None, verbose=True, questions=None):
    """Run all ten gates on one section.  Returns (errors, stats).

    `questions` overrides the module's own list.  It exists for mutants.py, which
    deliberately breaks a known-good question and asserts that the right gate notices.
    A gate suite that has never been shown to fail is not evidence of anything.
    """
    base = base or baseline()
    plan = spec.SECTIONS[n - 1]
    errs = []
    mod = load_section(n)
    qs = sorted(questions if questions is not None else mod.QUESTIONS,
                key=lambda d: d["n"])
    figdir = os.path.join(HERE, "fig")
    marker_ids = set()

    # ---- G1 structure ------------------------------------------------------
    if len(qs) != spec.PER_SECTION:
        errs.append("G1: section has %d questions, the plan says %d"
                    % (len(qs), spec.PER_SECTION))
    seen_ids = set()
    mix = {}
    for i, q in enumerate(qs, 1):
        qid = q.get("id") or "%s-%02d" % (plan["id_prefix"], i)
        q["id"] = qid
        if qid in seen_ids:
            errs.append("G1 %s: duplicate id" % qid)
        seen_ids.add(qid)
        if q.get("n") != i:
            errs.append("G1 %s: n=%r but sits at position %d" % (qid, q.get("n"), i))
        if q.get("module") not in spec.MODULES:
            errs.append("G1 %s: module %r is not an in-scope module" % (qid, q.get("module")))
        mix[q.get("module")] = mix.get(q.get("module"), 0) + 1
        if q.get("diff") not in (1, 2, 3):
            errs.append("G1 %s: diff %r must be 1, 2 or 3" % (qid, q.get("diff")))
        opts = q.get("opts") or []
        if len(opts) != 5:
            errs.append("G1 %s: %d options, Round 0 has five" % (qid, len(opts)))
        if len({norm_opt(o) for o in opts}) != len(opts):
            errs.append("G1 %s: two options read the same" % qid)
        if not isinstance(q.get("ans"), int) or not (0 <= q["ans"] < 5):
            errs.append("G1 %s: ans %r out of range" % (qid, q.get("ans")))
        for fld in ("topic", "stem", "sol", "trap"):
            if not str(q.get(fld, "")).strip():
                errs.append("G1 %s: %s is empty" % (qid, fld))
        if not q.get("rel"):
            errs.append("G1 %s: rel is empty -- nothing says what it draws on" % qid)
        else:
            for code, _t in q["rel"]:
                if code not in spec.MODULES + ["N"]:
                    errs.append("G1 %s: rel names unknown module %r" % (qid, code))
        if not q.get("key"):
            errs.append("G1 %s: key is empty" % qid)

    if mix != plan["counts"]:
        errs.append("G1: module mix is %s, the section plan says %s"
                    % (dict(sorted(mix.items())), dict(sorted(plan["counts"].items()))))

    # ---- G2 distractors ----------------------------------------------------
    for q in qs:
        d = q.get("distractors")
        if not d or len(d) != 5:
            errs.append("G2 %s: need five index-aligned distractors, got %r"
                        % (q["id"], None if d is None else len(d)))
            continue
        # A gate must survive malformed input rather than crash on it: an out-of-range
        # key is already reported by G1, so index with it only once it is known good.
        if not isinstance(q.get("ans"), int) or not (0 <= q["ans"] < len(d)):
            continue
        if d[q["ans"]] != "correct":
            errs.append("G2 %s: distractors[%d] must be 'correct', is %r"
                        % (q["id"], q["ans"], d[q["ans"]]))
        for i, s in enumerate(d):
            if i == q["ans"]:
                continue
            if len(str(s).strip()) < MIN_DISTRACTOR:
                errs.append("G2 %s: option %s has no named error (%r) -- filler options "
                            "are what a worksheet has and a competition does not"
                            % (q["id"], LET[i], s))
        wrong = [d[i] for i in range(5) if i != q["ans"]]
        if len(set(wrong)) < 4:
            errs.append("G2 %s: the four wrong options do not encode four distinct errors" % q["id"])

    # ---- G3 agreement, notation, non-calculator ----------------------------
    for q in qs:
        stem = expand_figs(supify(q["stem"]), figdir, marker_ids, errs)
        opts = [expand_figs(supify(o), figdir, marker_ids, errs) for o in q["opts"]]
        sol = expand_figs(supify(q["sol"]), figdir, marker_ids, errs)
        trap = supify(q.get("trap", ""))
        q["_stem"], q["_opts"], q["_sol"] = stem, opts, sol

        for label, txt in (("stem", stem), ("sol", sol), ("trap", trap)) + tuple(
                ("opt%d" % i, o) for i, o in enumerate(opts)):
            if "{{FIG" in txt:
                errs.append("G3 %s: unresolved figure placeholder in %s" % (q["id"], label))
            bal = tags_balanced(txt)
            if bal:
                errs.append("G3 %s: markup not balanced in %s -- %s" % (q["id"], label, bal))

        found = re.findall(r"Answer:\s*([A-E])", sol)
        # index LET only once the key is known to be a valid index; G1 reports it if not
        ans_ok = isinstance(q.get("ans"), int) and 0 <= q["ans"] < len(LET)
        if not found:
            errs.append("G3 %s: the solution never states 'Answer: <letter>'" % q["id"])
        elif ans_ok and found[-1] != LET[q["ans"]]:
            errs.append("G3 %s: solution says %s, ans field says %s"
                        % (q["id"], found[-1], LET[q["ans"]]))

        # Notation lint.  These two checks look at DIFFERENT texts, on purpose.
        #
        # The caret check tests the RENDERED text, because supify() already rewrites
        # every `x^2` into `<sup>2</sup>` upstream.  Linting the pre-repair source would
        # be a check that can never fail -- and a gate that cannot fail is worse than no
        # gate at all, because it reports safety it never tested.  The mutation test
        # caught exactly that: the check had been passing vacuously all along.  What is
        # worth testing is whether the repair COVERED everything, so the question is
        # "did a caret survive to the reader?"  supify needs a non-space character
        # after `^`, so `x^ 2` survives it -- and that is a real defect.
        for label, txt in (("stem", visible(stem)), ("sol", visible(sol)),
                           ("trap", visible(trap))):
            for m in re.finditer(r"\^", txt):
                errs.append("G3 %s: a caret survives to the reader in %s -- %r "
                            "(write <sup> in the source, or remove the space after ^)"
                            % (q["id"], label, txt[max(0, m.start() - 8):m.start() + 6]))
        # The ASCII-exponent check tests the MARKUP text instead: there, a correct
        # `m<sup>-3</sup>` still shows its <sup> tag and cannot be confused with a
        # plainly written `m-3`.  Running it on rendered text would turn every correct
        # superscript into a false positive.
        for label, txt in (("stem", stem), ("sol", sol), ("trap", trap)):
            for m in re.finditer(r"\b[mMs]\s*-\s*[123]\b", txt):
                errs.append("G3 %s: ASCII exponent %r in %s" % (q["id"], m.group(0), label))

        # non-calculator lint: every decimal the reader can see must be hand-computable
        for label, txt in (("stem", stem), ("sol", sol), ("trap", trap)) + tuple(
                ("opt%d" % i, o) for i, o in enumerate(opts)):
            vt = visible(txt)
            for m in re.finditer(r"(?<![\w.])(\d+\.\d+)(?![\w])", vt):
                v = m.group(1)
                if v in CALC_OK:
                    continue
                if len(v.replace(".", "").lstrip("0")) <= 2:
                    continue
                # A single decimal place is a half, a quarter, a fifth or a tenth -- it is
                # mental arithmetic by construction, and no calculator is implied.  This
                # matters because the fraction exemption below is a NUMERATOR cap, and
                # 22.5 = 45/2 is rejected by it for having a numerator of 45.  Rejecting
                # 22.5 (half of the correct 45 degrees, in S02-09) is plainly wrong.
                if re.fullmatch(r"\d+\.\d", v):
                    continue
                fr = Fraction(v)
                if fr.denominator <= 20 and fr.numerator <= 40:
                    continue
                sent = _sentence_at(vt, m.start()).lower()
                if v in CALC_OK or any(ph in sent for ph in FLAG_PHRASES):
                    continue
                if _hand_from_data(v, sent):
                    continue
                errs.append("G3 %s: decimal %s in %s is not hand-computable and nothing "
                            "in its sentence says so -- %s"
                            % (q["id"], v, label, " ".join(_sentence_at(vt, m.start()).split())[:80]))

    # ---- G4 profile --------------------------------------------------------
    for q in qs:
        p = q.get("profile")
        if not p:
            errs.append("G4 %s: no profile -- the reasoning chain is undeclared" % q["id"])
            continue
        steps = p.get("steps") or []
        want_steps = MIN_STEPS[q["diff"]]
        if len(steps) < want_steps:
            errs.append("G4 %s: diff %d needs >= %d reasoning steps, profile has %d"
                        % (q["id"], q["diff"], want_steps, len(steps)))
        rels = p.get("relations") or []
        if len(set(rels)) < MIN_RELATIONS[q["diff"]]:
            errs.append("G4 %s: diff %d needs >= %d distinct relations, profile has %d"
                        % (q["id"], q["diff"], MIN_RELATIONS[q["diff"]], len(set(rels))))
        if len(str(p.get("insight", "")).strip()) < MIN_INSIGHT:
            errs.append("G4 %s: insight is missing or too thin (the one idea that unlocks it)"
                        % q["id"])
        if p.get("shape") not in SHAPES:
            errs.append("G4 %s: shape %r is not one of the known shapes" % (q["id"], p.get("shape")))

        f = features({"sol": q["_sol"], "q": q["_stem"], "opts": q["_opts"],
                      "trap": q.get("trap", ""), "rel": q.get("rel", [])})
        # the declared chain may not be shorter than the chain the solution actually walks
        if f["n_steps"] and len(steps) < f["n_steps"]:
            errs.append("G4 %s: profile declares %d steps but the solution walks %d "
                        "('Step %d' appears in it)" % (q["id"], len(steps), f["n_steps"], f["n_steps"]))
        if q["diff"] >= 2 and f["n_steps"] < 2:
            errs.append("G4 %s: diff %d but the solution shows no numbered steps" % (q["id"], q["diff"]))
        if bool(p.get("approx")) != bool(f["approx"]):
            errs.append("G4 %s: profile says approx=%s but the solution %s"
                        % (q["id"], p.get("approx"),
                           "uses an approximation" if f["approx"] else "does not approximate"))
        if p.get("figure_essential") and "<svg" not in q["_stem"]:
            errs.append("G4 %s: figure_essential is set but the stem carries no figure" % q["id"])
        if "<svg" in q["_stem"] and not p.get("figure_essential") and not p.get("figure_support"):
            errs.append("G4 %s: the stem has a figure but the profile does not say whether "
                        "it is essential or only supporting" % q["id"])

    # ---- G5 difficulty -----------------------------------------------------
    ref = base.get("R0-2025") or base.get(sorted(base)[0])
    scores = [difficulty({"sol": q["_sol"], "q": q["_stem"], "opts": q["_opts"],
                          "trap": q.get("trap", ""), "rel": q.get("rel", [])}) for q in qs]
    # "the same or even harder", tested at three points of the distribution rather
    # than asserted once.  Every one of these is a place a section can be too easy.
    sec_median = median(scores)
    if sec_median < ref["median"]:
        errs.append("G5: section median %.1f is below the 2025 paper's %.1f"
                    % (sec_median, ref["median"]))
    sec_p25 = percentile(scores, 25)
    if sec_p25 < ref["p25"]:
        errs.append("G5: section 25th percentile %.1f is below the 2025 paper's %.1f -- "
                    "the easier end of the section is easier than the real paper's"
                    % (sec_p25, ref["p25"]))
    # How many questions sit below the paper's own p25?  The paper has six, by
    # definition.  A section is not wrong to have a few -- it is wrong to have many,
    # because that is the section drifting easy at the bottom.
    easy = [(qs[i]["id"], scores[i]) for i in range(len(qs)) if scores[i] < ref["p25"]]
    if len(easy) > 7:
        errs.append("G5: %d question(s) below the 2025 paper's 25th percentile (%.1f); the "
                    "paper itself has only 6, so the section is drifting easy: %s"
                    % (len(easy), ref["p25"], ", ".join("%s=%.1f" % b for b in easy[:6])))
    # the top end must be real, not just the middle
    top = [qs[i]["id"] for i in range(len(qs)) if scores[i] >= ref["p75"]]
    if len(top) < TOP_QUARTILE_MIN:
        errs.append("G5: only %d question(s) reach the 2025 paper's top quartile (%.1f); "
                    "at least %d wanted -- the brief is 'same or harder'"
                    % (len(top), ref["p75"], TOP_QUARTILE_MIN))
    # the declared band on each question must be the band its score actually falls in
    for i, q in enumerate(qs):
        want = band_of(scores[i], ref)
        if q["diff"] != want:
            errs.append("G5 %s: declared diff %d, but its measured score %.1f puts it in "
                        "band %d (the 2025 paper's p25 and p75 are %.1f and %.1f)"
                        % (q["id"], q["diff"], scores[i], want, ref["p25"], ref["p75"]))
    dist = {}
    for q in qs:
        dist[q["diff"]] = dist.get(q["diff"], 0) + 1
    for k, mx in spec.DIFF_MAX.items():
        if dist.get(k, 0) > mx:
            errs.append("G5: %d questions at diff %d, at most %d allowed" % (dist.get(k, 0), k, mx))
    for k, mn in spec.DIFF_MIN.items():
        if dist.get(k, 0) < mn:
            errs.append("G5: %d questions at diff %d, at least %d required" % (dist.get(k, 0), k, mn))
    g5_stats = {"median": sec_median, "p25": sec_p25, "min": min(scores), "max": max(scores),
                "top_quartile": len(top), "bands": dist}

    # ---- G6 similarity -----------------------------------------------------
    for i in range(len(qs)):
        for j in range(i + 1, len(qs)):
            a, b = qs[i], qs[j]
            ja = jaccard(fingerprint(a), fingerprint(b))
            to = text_overlap(a, b)
            if ja >= SIM_JACCARD:
                errs.append("G6 %s ~ %s: logic fingerprint %.2f overlap (%s | %s) -- "
                            "same reasoning chain, different numbers"
                            % (a["id"], b["id"], ja, fp_label(fingerprint(a)),
                               fp_label(fingerprint(b))))
            elif to >= TEXT_SHINGLE:
                errs.append("G6 %s ~ %s: wording overlap %.2f (no shared logic, but the "
                            "sentences are too close)" % (a["id"], b["id"], to))

    # A section that is 25 rewordings of one trick is a worksheet, not a paper.  The
    # shape is the authored statement of what KIND of reasoning unlocks the question.
    shape_counts = {}
    for q in qs:
        sh = (q.get("profile") or {}).get("shape", "?")
        shape_counts[sh] = shape_counts.get(sh, 0) + 1
    for sh, c in sorted(shape_counts.items()):
        if c > SHAPE_MAX:
            errs.append("G6: %d questions share the shape %r, at most %d allowed -- "
                        "the section is repetitive" % (c, sh, SHAPE_MAX))
    if len(shape_counts) < SHAPE_KINDS_MIN:
        errs.append("G6: only %d distinct reasoning shapes in the section, at least %d wanted"
                    % (len(shape_counts), SHAPE_KINDS_MIN))

    # ---- G7 numerics -------------------------------------------------------
    for q in qs:
        chk = q.get("check")
        if not chk:
            errs.append("G7 %s: no check -- the answer is not independently re-derived" % q["id"])
            continue
        msg = check_numeric(chk)
        if msg:
            errs.append("G7 %s: %s" % (q["id"], msg))

    # ---- G8 figures --------------------------------------------------------
    n_fig = sum(1 for q in qs if "<svg" in q["_stem"])
    if n_fig < spec.FIG_MIN:
        errs.append("G8: only %d questions carry a figure, the plan asks for %d"
                    % (n_fig, spec.FIG_MIN))

    # ---- G9 balance --------------------------------------------------------
    # A malformed key (non-int, or out of range) is G1's business to report.  G9 must
    # survive it -- crashing here would abort the whole suite and hide every later
    # finding, which is exactly what the mutation test caught.
    letters = [LET[q["ans"]] if isinstance(q.get("ans"), int) and 0 <= q["ans"] < len(LET)
               else "?" for q in qs]
    for L in LET:
        c = letters.count(L)
        if c < LETTER_MIN:
            errs.append("G9: answer %s appears %d time(s), at least %d wanted" % (L, c, LETTER_MIN))
        if c > LETTER_MAX:
            errs.append("G9: answer %s appears %d times, at most %d wanted" % (L, c, LETTER_MAX))

    # ---- G10 hand-check ledger --------------------------------------------
    ledger_path = os.path.join(HERE, "ledger.json")
    ledger = json.load(open(ledger_path, encoding="utf-8")) if os.path.exists(ledger_path) else {}
    checked = [q["id"] for q in qs if ledger.get(q["id"], {}).get("verified")]
    if len(checked) < HANDCHECK_MIN:
        errs.append("G10: only %d of 25 questions are hand-checked, at least %d required "
                    "(the tool cannot verify its own physics)" % (len(checked), HANDCHECK_MIN))

    stats = {
        "section": n, "code": plan["code"], "n": len(qs),
        "mix": dict(sorted(mix.items())),
        "diff": dict(sorted(dist.items())),
        "figures": n_fig,
        "letters": "".join(letters),
        "scores": scores,
        "median": sec_median,
        "ref_median": ref["median"], "ref_p25": ref["p25"],
        "handchecked": len(checked),
    }
    if verbose:
        print("section %s  n=%d  figures=%d  hand-checked=%d"
              % (stats["code"], stats["n"], stats["figures"], stats["handchecked"]))
        print("  mix        " + " ".join("%s%d" % (m, c) for m, c in stats["mix"].items()))
        print("  difficulty " + " ".join("d%s=%d" % (k, v) for k, v in stats["diff"].items()))
        print("  answers    %s" % stats["letters"])
        print("  score      median %.1f (2025 paper %.1f)   p25 %.1f (paper %.1f)   min %.1f"
              % (sec_median, ref["median"], percentile(scores, 25), ref["p25"], min(scores)))
        print("  hardest    " + ", ".join(
            "%s=%.1f" % (qs[k]["id"], v) for k, v in
            sorted(enumerate(scores), key=lambda t: -t[1])[:4]))
    return errs, stats


# ═════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════

def cmd_papers():
    base = baseline()
    print("difficulty scorer, calibrated on the only two real Round 0 documents\n")
    print("%-10s %4s %8s %8s %8s %8s %8s" % ("paper", "n", "median", "p25", "p75", "min", "max"))
    for tag, b in sorted(base.items()):
        print("%-10s %4d %8.1f %8.1f %8.1f %8.1f %8.1f"
              % (tag, b["n"], b["median"], b["p25"], b["p75"], b["min"], b["max"]))
    data = json.load(open(os.path.join(HERE, "papers.json"), encoding="utf-8"))
    qs = [q for q in data["questions"] if q["paper"] == "R0-2025"]
    print("\nthe 2025 paper, hardest first:")
    for q in sorted(qs, key=lambda q: -difficulty(q)):
        f = features(q)
        print("  %-8s %-2s d%d  score %5.1f   chain %d  formulas %d  approx %d  sym %d  rel %d"
              % (q["id"], q["module"], q["diff"], difficulty(q),
                 f["moves"], f["n_formula"], f["approx"], f["symbolic"], f["relmods"]))
    return 0


def cmd_section(n):
    errs, _st = gate_section(n)
    print()
    if errs:
        print("!! GATE FAILED (%d)" % len(errs))
        for e in errs:
            print("   -", e)
        return 1
    print("all gates passed")
    return 0


def cmd_all():
    ns = sorted(int(re.search(r"(\d+)", os.path.basename(p)).group(1))
                for p in glob.glob(os.path.join(HERE, "sec[0-9][0-9].py")))
    if not ns:
        print("no section sources found (sec01.py, sec02.py, ...)")
        return 0
    base = baseline()
    bad = 0
    for n in ns:
        print("=" * 74)
        errs, _st = gate_section(n, base=base)
        if errs:
            bad += 1
            print("!! GATE FAILED (%d)" % len(errs))
            for e in errs:
                print("   -", e)
        else:
            print("  all gates passed")
    print("=" * 74)
    print("%d of %d sections pass" % (len(ns) - bad, len(ns)))
    return 1 if bad else 0


if __name__ == "__main__":
    supify_selfcheck()
    arg = sys.argv[1] if len(sys.argv) > 1 else "papers"
    if arg == "papers":
        sys.exit(cmd_papers())
    if arg == "all":
        sys.exit(cmd_all())
    m = re.match(r"(?:sec)?(\d+)$", arg)
    if m:
        sys.exit(cmd_section(int(m.group(1))))
    print(__doc__)
    sys.exit(2)
