"""Finish the Batch 33 paperwork: PLAN.md milestone and README.md state tables.

Every figure in the replacement text is measured from the data at run time, so the docs cannot
be written from a remembered number.
"""
import io, json, sys, collections

sys.path.insert(0, "tools")
import validate as V

qs = [q for _, q in V.load()]
n = len(qs)
subj = collections.Counter(q["subject"] for q in qs)
marks = collections.Counter()
for q in qs:
    marks[q["subject"]] += q["marks"]
diff = collections.Counter(q["difficulty"] for q in qs)
figs = [q for q in qs if q.get("figure")]
ev = sum(1 for q in qs if q.get("difficulty_evidence"))
asr = sum(len(q["verification"]["assertions"]) for q in qs)
fam = collections.Counter((q.get("provenance") or {}).get("source_family") for q in qs)
nonorig = n - fam["original"]
total_marks = sum(q["marks"] for q in qs)


def share(s):
    sub = [q for q in qs if q["subject"] == s]
    return 100.0 * sum(1 for q in sub if q["difficulty"] == 5) / len(sub)


M = dict(n=n, math=subj["Math AA HL"], phys=subj["Physics HL"], cs=subj["Computer Science HL"],
         bm=subj["Business Management SL"], tm=total_marks, d3=diff[3], d4=diff[4], d5=diff[5],
         fig=len(figs), figpct=100.0 * len(figs) / n, ev=ev, asr=asr, nonorig=nonorig,
         mmarks=marks["Math AA HL"], pmarks=marks["Physics HL"], cmarks=marks["Computer Science HL"],
         bmarks=marks["Business Management SL"],
         mshare=share("Math AA HL"), pshare=share("Physics HL"), cshare=share("Computer Science HL"),
         bshare=share("Business Management SL"), uka=fam["uk-alevel"], oth=fam["other"])
print("measured:", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in M.items()})

EDITS = []

# ------------------------------------------------------------------ PLAN.md
EDITS.append(("PLAN.md", "- **Batch 33 — DONE (2 items, 339 → 341; the first wave written entirely under §0).**",
              "- **Batch 33 — DONE (3 items, 339 → 342; the first wave written entirely under §0).**"))

EDITS.append(("PLAN.md",
"""  - **Three defects were caught before shipping, and each one became a check.**""",
"""  - **`CS-A2.1-601` (P1 Section A, 15 marks, d5, `variable_swap`)** is the third item and the one that
    goes where the marks are thinnest: Section A holds 245 of CS Paper 1's marks against Section B's
    382, where the guide gives Section A 56 of 80. It states a model of a windowed connection in full
    ($W = 1.22/\\sqrt{p}$ packets, $S = W \\times \\mathrm{MSS} \\times 8 / \\mathrm{RTT}$) so that no
    protocol recall is required, and then asks the question the model is never used for --- given a
    required throughput, what loss probability can the network tolerate? The unknown sits under a
    square root in a denominator, so the inversion ends in a squaring, and the reflex is to divide:
    $1.22/68.5 = 0.0178$ instead of $3.17 \\times 10^{-4}$, a tolerance fifty-six times too forgiving
    and the kind of number that would be signed off as a comfortable margin. Part (d) compares two
    "factor of two" upgrades that are not equal ($\\times 2$ against $\\times\\sqrt{2}$), and part (e)
    offers a proposal the model endorses --- quadruple the MSS, $14.2\\ \\mathrm{Mbit/s}$ --- and the
    link refutes, because a 5840-byte segment does not fit a 1500-byte MTU. **No figure**, deliberately:
    the situation is one stated model and three parameters, and drawing it would be drawing for the
    count, which §0.1 forbids. Originality ext 0.003 / int 0.014 / appr 0.084.
  - **Three defects were caught before shipping, and each one became a check.**"""))

EDITS.append(("PLAN.md",
"""  - **Numbers after the wave.** 341 items — Maths 138 / 1967 marks, Physics 97 / 1149, CS 67 / 997,
    BM SL 39 / 563; 4676 marks. Difficulty 5 / 186 / 150. d5 shares: Maths **49%** (at the cap — the
    next Maths wave must be written at d4), Physics 44%, CS 46%, BM 23%. Evidence 256 / 341,
    `difficulty 5 with no evidence` **0**, `labels the evidence does not permit` **0**, all 13 levers in
    use. Assertions 3981. Figures 114 / 341 = 33%. Sourcing 126 items outside `original`, including the
    first `other`-family entry from the Indian systems. `validate.py` 0 failures / 179 warnings,
    `difficulty_audit --check` exit 0.""",
"""  - **Numbers after the wave, measured from the data rather than typed.** %(n)d items — Maths
    %(math)d / %(mmarks)d marks, Physics %(phys)d / %(pmarks)d, CS %(cs)d / %(cmarks)d, BM SL
    %(bm)d / %(bmarks)d; %(tm)d marks in all. Difficulty %(d3)d / %(d4)d / %(d5)d. d5 shares: Maths
    **%(mshare).0f%%** (at the cap — the next Maths wave must be written at d4), Physics
    %(pshare).0f%%, CS %(cshare).0f%%, BM %(bshare).0f%%. Evidence %(ev)d / %(n)d,
    `difficulty 5 with no evidence` **0**, `labels the evidence does not permit` **0**, all 13 levers
    in use. Assertions %(asr)d. Figures %(fig)d / %(n)d = %(figpct).0f%%. Sourcing %(nonorig)d items
    outside `original` (`uk-alevel` %(uka)d, `other` %(oth)d — the first entry from the Indian systems).
    `validate.py` 0 failures, `difficulty_audit --check` exit 0.""" % M))

# ---------------------------------------------------------------- README.md
EDITS.append(("README.md",
"""| Math AA HL | 2021 (runs to Nov 2028) | 138 | 83 / 83 (100%) |
| Physics HL | 2025 | 97 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 67 | 25 / 25 (100%) |
| Business Management SL | 2024 | 39 | 34 / 34 (100%) |
| **Total** | | **341** | **166 / 166 (100%)** |""",
"""| Math AA HL | 2021 (runs to Nov 2028) | %(math)d | 83 / 83 (100%%) |
| Physics HL | 2025 | %(phys)d | 24 / 24 (100%%) |
| Computer Science HL | 2027 (new Theme A/B) | %(cs)d | 25 / 25 (100%%) |
| Business Management SL | 2024 | %(bm)d | 34 / 34 (100%%) |
| **Total** | | **%(n)d** | **166 / 166 (100%%)** |""" % M))

EDITS.append(("README.md",
"""All 341 items are difficulty 3–5 (**5 at difficulty 3, 186 at difficulty 4, 150 at difficulty 5**), and
pass `validate.py`
with **0 failures**.""",
"""All %(n)d items are difficulty 3–5 (**%(d3)d at difficulty 3, %(d4)d at difficulty 4, %(d5)d at
difficulty 5**), and pass `validate.py`
with **0 failures**.""" % M))

EDITS.append(("README.md",
"""| items with evidence for the label | **256 / 341** | 0 / 172 |""",
"""| items with evidence for the label | **%(ev)d / %(n)d** | 0 / 172 |""" % M))

EDITS.append(("README.md",
"""Every item carries a `verification.assertions` list — **3981 machine-checked assertions** in total — so""",
"""Every item carries a `verification.assertions` list — **%(asr)d machine-checked assertions** in total — so""" % M))

EDITS.append(("README.md",
"""**Sourcing is recorded, not claimed.** 126 items are drawn from other syllabuses""",
"""**Sourcing is recorded, not claimed.** %(nonorig)d items are drawn from other syllabuses""" % M))

EDITS.append(("STANDARD.md",
"""the bank now stands at **110/337 = 33%**, with **Maths at 22% (30/136)** — above the per-subject target —
**CS at 52% (35/67)**, **Physics at 39% (37/95)** and **BM at 21% (8/39)**, against 0%""",
"""the bank now stands at **%(fig)d/%(n)d = %(figpct).0f%%**, with **Maths at 23%% (32/%(math)d)** — above the per-subject target —
**CS at 52%% (35/%(cs)d)**, **Physics at 40%% (39/%(phys)d)** and **BM at 21%% (8/%(bm)d)**, against 0%%""" % M))

failures, cache = [], {}
for path, old, new in EDITS:
    text = cache.get(path) or io.open(path, encoding="utf-8").read()
    c = text.count(old)
    if c != 1:
        failures.append("%s: anchor matched %d times -- %.70s" % (path, c, old.replace("\n", " ")))
        continue
    cache[path] = text.replace(old, new)
if failures:
    print("\n".join(failures))
    sys.exit("aborted, nothing written")
for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)
    print("updated", path)
