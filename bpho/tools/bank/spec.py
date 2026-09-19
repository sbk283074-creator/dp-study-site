# -*- coding: utf-8 -*-
"""The 1000-question bank: what it is made of, and why.

THE SHAPE
---------
1000 questions = 40 sections of 25.  Each section is a complete BPhO Round 0 paper:
25 single-answer MCQs, five options, no calculator, no negative marking, one mark
each.  So every section is independently usable as a timed mock, and the whole bank
is 40 mocks deep.

THE MODULE MIX
--------------
The mix is not invented.  It is taken from the one Round 0 paper that exists (2025),
whose 25 questions distribute as

    C 5   H 4   A 3   G 2   K 2   F 2   B 2   L 2   E 1   J 1   D 1

That is the only hard evidence anyone has about how the 25 marks really fall.  Two
deliberate departures from it, both recorded here rather than buried:

  * The 2025 paper tested no capacitors (I) and no fluids (M), yet the official R0
    scope note lists both.  The house rule for this project is that when sources
    disagree we include rather than omit, so I and M are given 40 and 30 questions
    respectively instead of zero.  They are the smallest allocations in the bank,
    which keeps them proportionate to the evidence.
  * Module N (Round 1 insurance) is given NO questions.  The scope rule is that R1
    evidence is not evidence about R0, and a Round 0 mock that contained R1 material
    would be training the wrong thing.  N stays in the curriculum pages and out of
    the bank.

The resulting target totals, summing to exactly 1000:

    A 120   B  80   C 130   D  60   E  50   F  80   G  80
    H 140   I  40   J  50   K  80   L  60   M  30

ALLOCATION
----------
The per-section mixes are produced by proportional apportionment: for section s the
ideal cumulative count of module m is round(target[m] * s / 40), and the section
takes the difference between that and what has already been handed out.  This hits
the totals exactly and spreads each module evenly, so no section is a pile of
circuits and no section is missing the toolkit.

DIFFICULTY
----------
The brief is "the same or harder than BPhO".  That has to be measured against
something, so the gate system scores every question with one function and calibrates
that function on the real 2025 paper and the published sample sheet.  The per-section
requirement is:

    diff 1 (core)        at most 5      -- the real paper has none that are easy
    diff 2 (extension)   no floor       -- the band the measurement puts a question in
    diff 3 (challenge)   at least 6

plus, measured rather than declared:

  * the section median must be at or above the 2025 paper's median;
  * the section must carry at least two questions with a reasoning chain of nine or
    more moves, and its hardest question must score at least 22.0, because the paper
    carries one question at thirteen moves scoring 27.4 and a section with no top end
    is flat even when its median is fine;
  * the non-calculator axes must be real: see NONCALC_PAPER / APPROX_PAPER below.

See gates.py for the scorer.  The diff-2 floor that used to appear here (14) was
removed: it was a guessed proportion, and the measurement is what decides a question's
band now, so a floor on band 2 would contradict the bands of sections whose median sits
above the paper's p75.

FIGURES
-------
The real paper carries 8 figures in 25 questions (Q2, Q7, Q8, Q14, Q20, Q21, Q23,
Q25).  Every section must carry at least 8 hand-drawn inline SVG figures, and a
figure must encode the discriminator the question turns on -- never decoration.

SOURCES
-------
The questions are ORIGINAL.  BPhO papers and other competitions' papers are
copyrighted, so no question is copied, quoted or lightly reworded.  What is borrowed
is the *style and the difficulty*: `STYLE` below records, per module, which
competitions set questions of comparable demand inside the R0 scope, and that
reference is what the author consults when calibrating a new question.  It is a
reading list, not a source of text.
"""

# ── modules ──────────────────────────────────────────────────────────────────
# The in-scope modules, in the site's priority order.  N is deliberately absent:
# it is Round 1 material and a Round 0 paper must not test it.
MODULES = ["A", "H", "I", "L", "M", "B", "C", "D", "E", "F", "G", "K", "J"]

# ── target totals (sum = 1000) ───────────────────────────────────────────────
TARGETS = {
    "A": 120,   # toolkit -- underpins everything, so it carries its weight
    "B": 80,
    "C": 130,   # the single heaviest module on the real paper (5 marks)
    "D": 60,
    "E": 50,
    "F": 80,
    "G": 80,
    "H": 140,   # second heaviest on the real paper (4 marks)
    "I": 40,    # absent from the 2025 paper; included because the scope note lists it
    "J": 50,
    "K": 80,
    "L": 60,
    "M": 30,    # absent from the 2025 paper; included because the scope note lists it
}

N_SECTIONS = 40
PER_SECTION = 25
assert sum(TARGETS.values()) == N_SECTIONS * PER_SECTION, sum(TARGETS.values())

# ── difficulty targets, per section ──────────────────────────────────────────
# These were first written as {2: 14, 3: 6} -- "mirror the real paper's proportions" --
# but that number was guessed, and when the 2025 paper's own bands were counted it
# declares 4 easy, 8 standard and 13 hard out of 25.  A guessed proportion that the
# yardstick itself does not satisfy is not a standard, so the band counts are now
# derived from the measurement instead:
#   * each question's band is the band its measured score falls in, with the 2025
#     paper's own p25 and p75 as the cut-points (see gates.band_of);
#   * a section may carry at most DIFF_MAX[1] questions in the easy band, because the
#     brief is "same or harder", not "same or easier";
#   * it must carry at least DIFF_MIN[3] in the hard band.
DIFF_MAX = {1: 5}          # at most 5 easy questions
DIFF_MIN = {3: 6}          # at least 6 hard questions
FIG_MIN = 8                # at least 8 figure-bearing questions

# ── the non-calculator axes, per section ─────────────────────────────────────
# Round 0 is sat without a calculator, and the scorer has exactly two terms that encode
# that skill: `approx` (the reasoning needs an approximation) and `symbolic` (the answer
# is a formula rather than a number).  Measured with the same scorer, the 2025 paper
# uses one or the other in 16 of its 25 questions and requires an approximation in 10.
#
# The bank as it stood at the difficulty audit (sections 1-5, 125 questions) scored
# 41/125 = 33% and 12/125 = 10% on the same two counts.  So the paper leans on the
# non-calculator axes about twice as hard as the bank did -- and this is a difficulty
# axis, not a stylistic one: a question that requires neither is usually just arithmetic,
# and arithmetic is the one thing a candidate can do slowly instead of wrongly.
#
# Sections 1-5 are GRANDFATHERED at floors they actually meet.  Rewriting 125 published
# questions to close a gap is a different piece of work from closing the gap for the 875
# questions that are still unwritten, and doing the second while the first is tracked is
# strictly better than doing neither.  The remediation of 1-5 is an open item in
# BANK-PLAN section 8.  Every section from 6 on must meet the paper's own profile.
NONCALC_LEGACY = 6         # sections 1-5: the floor the published sections already meet
APPROX_LEGACY = 1
NONCALC_PAPER = 16         # sections 6-40: what the 2025 paper itself achieves, of 25
APPROX_PAPER = 10
LEGACY_SECTIONS = 5        # 1..5 were authored before the audit

# ── style reference, per module ──────────────────────────────────────────────
# Which competitions set questions of comparable difficulty *inside the R0 scope*.
# A reading list for calibration only -- never a source of text.
STYLE = {
    "A": ["Physics Bowl (dimensional analysis / estimation)", "BPhO AS Physics Challenge",
          "Canadian OAPT contest"],
    "B": ["Physics Bowl", "BPhO AS Physics Challenge"],
    "C": ["BPhO AS Physics Challenge", "Physics Bowl", "IB Physics HL paper 2"],
    "D": ["BPhO AS Physics Challenge", "Physics Bowl"],
    "E": ["BPhO AS Physics Challenge", "Physics Bowl"],
    "F": ["Physics Bowl", "BPhO AS Physics Challenge"],
    "G": ["BPhO AS Physics Challenge", "Physics Bowl", "IB Physics HL paper 2"],
    "H": ["Physics Bowl", "BPhO AS Physics Challenge", "IB Physics HL paper 2"],
    "I": ["IB Physics HL paper 2", "BPhO AS Physics Challenge"],
    "J": ["Physics Bowl", "BPhO AS Physics Challenge"],
    "K": ["Physics Bowl", "IB Physics HL paper 2"],
    "L": ["Physics Bowl", "IB Physics HL paper 2", "BPhO AS Physics Challenge"],
    "M": ["Physics Bowl", "IB Physics SL/HL"],
}

MODULE_TITLE = {
    "A": "Toolkit", "B": "Kinematics", "C": "Forces & momentum", "D": "Circular motion",
    "E": "Materials", "F": "Waves", "G": "Optics", "H": "Circuits", "I": "Capacitors",
    "J": "Thermal", "K": "Nuclear", "L": "Quantum & photons", "M": "Fluids",
}


# ── the allocator ────────────────────────────────────────────────────────────

# A per-module, per-section rounding phase.  Without it the apportionment locks into
# a period-4 rhythm -- C, E and J move in quarter-steps, D and L in half-steps, so
# sections 1, 5, 9, ... come out with identical mixes.  Shifting each module's
# rounding boundary by (index + section) mod 4 quarter-steps breaks that, and because
# every phase stays in [0, 1) the totals still close exactly at section 40.
_ORDER = sorted(TARGETS)


def _ideal(target, s, n, m):
    """Ideal cumulative count of module `m` after s sections."""
    # The multiplier on s is coprime with 40, so the phase cycles through 40 distinct
    # values and no two sections share a mix.
    phase = ((s * 17 + _ORDER.index(m) * 29) % 40) / 40.0
    return int(target * s / float(n) + phase)


def allocate():
    """Return a list of N_SECTIONS lists of module codes, 25 each, hitting TARGETS.

    Proportional apportionment: section s gets, of module m, the gap between the
    ideal cumulative count at s and the count actually handed out so far.  The last
    section therefore closes any rounding debt exactly.
    """
    handed = {m: 0 for m in TARGETS}
    out = []
    for s in range(1, N_SECTIONS + 1):
        take = {}
        for m, t in TARGETS.items():
            want = _ideal(t, s, N_SECTIONS, m)
            # a shifting phase can briefly put the ideal below what has already gone
            # out; the module simply takes nothing this section and catches up later.
            take[m] = max(0, want - handed[m])
        total = sum(take.values())
        # rounding can leave the section a question or two short of 25; settle the
        # difference on whichever modules are furthest behind their ideal pace.
        if total != PER_SECTION:
            short = PER_SECTION - total
            ranked = sorted(TARGETS, key=lambda m: (handed[m] + take[m]) / float(TARGETS[m]))
            i = 0
            while short != 0 and i < 400:
                m = ranked[i % len(ranked)]
                if short > 0:
                    take[m] += 1
                    short -= 1
                elif take[m] > 0:
                    take[m] -= 1
                    short += 1
                i += 1
        for m in take:
            handed[m] += take[m]
        out.append([m for m in take for _ in range(take[m])])

    assert all(len(x) == PER_SECTION for x in out), [len(x) for x in out]
    assert handed == TARGETS, handed
    return out


def interleave(modules):
    """Order a section's modules so the paper does not run in blocks.

    Greedy: repeatedly take the module with the most left, preferring one that is
    not the same as the previous entry.  Deterministic, so the order is stable.
    """
    left = {}
    for m in modules:
        left[m] = left.get(m, 0) + 1
    out = []
    prev = None
    while len(out) < len(modules):
        cand = sorted(left, key=lambda m: (-left[m], m))
        pick = None
        for m in cand:
            if left[m] > 0 and m != prev:
                pick = m
                break
        if pick is None:
            pick = cand[0]
        out.append(pick)
        left[pick] -= 1
        prev = pick
    return out


# ── the section table ────────────────────────────────────────────────────────

def sections():
    """The 40-section plan: id, code, ordered module list, per-module counts."""
    raw = allocate()
    out = []
    for i, mods in enumerate(raw, 1):
        ordered = interleave(mods)
        counts = {}
        for m in ordered:
            counts[m] = counts.get(m, 0) + 1
        legacy = i <= LEGACY_SECTIONS
        out.append({
            "n": i,
            "code": "S%02d" % i,
            "paper": "R0-S%02d" % i,
            "id_prefix": "S%02d" % i,
            "modules": ordered,
            "counts": counts,
            # carried on the plan rather than read as a global, so that a section can
            # state the standard it is held to and a gate can report the number it was
            # actually measured against
            "noncalc_min": NONCALC_LEGACY if legacy else NONCALC_PAPER,
            "approx_min": APPROX_LEGACY if legacy else APPROX_PAPER,
        })
    return out


SECTIONS = sections()


def summary():
    lines = []
    lines.append("sections: %d   questions: %d" % (len(SECTIONS), len(SECTIONS) * PER_SECTION))
    tot = {}
    for s in SECTIONS:
        for m, c in s["counts"].items():
            tot[m] = tot.get(m, 0) + c
    lines.append("module totals: " + "  ".join(
        "%s=%d" % (m, tot.get(m, 0)) for m in sorted(tot, key=lambda x: -tot[x])))
    lines.append("distinct modules per section: %s" % (
        sorted(set(len(s["counts"]) for s in SECTIONS))))
    lines.append("")
    for s in SECTIONS:
        lines.append("  %-4s %s" % (s["code"], " ".join(
            "%s%d" % (m, s["counts"][m]) for m in sorted(s["counts"]))))
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
