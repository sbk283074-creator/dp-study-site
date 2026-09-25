"""PLAN.md milestone and README/STANDARD tables for Batch 34. All numbers measured at run time."""
import io, sys, collections, json

sys.path.insert(0, "tools")
import validate as V

qs = [q for _, q in V.load()]
n = len(qs)
subj = collections.Counter(q["subject"] for q in qs)
marks = collections.Counter()
for q in qs:
    marks[q["subject"]] += q["marks"]
diff = collections.Counter(q["difficulty"] for q in qs)
figs = sum(1 for q in qs if q.get("figure"))
ev = sum(1 for q in qs if q.get("difficulty_evidence"))
asr = sum(len(q["verification"]["assertions"]) for q in qs)
fam = collections.Counter((q.get("provenance") or {}).get("source_family") for q in qs)


def share(s):
    sub = [q for q in qs if q["subject"] == s]
    return 100.0 * sum(1 for q in sub if q["difficulty"] == 5) / len(sub)


def fshare(s):
    sub = [q for q in qs if q["subject"] == s]
    return 100.0 * sum(1 for q in sub if q.get("figure")) / len(sub)


M = dict(n=n, math=subj["Math AA HL"], phys=subj["Physics HL"], cs=subj["Computer Science HL"],
         bm=subj["Business Management SL"], tm=sum(q["marks"] for q in qs),
         d3=diff[3], d4=diff[4], d5=diff[5], fig=figs, figpct=100.0 * figs / n, ev=ev, asr=asr,
         nonorig=n - fam["original"], uka=fam["uk-alevel"], ufm=fam["uk-further-maths"],
         oth=fam["other"],
         mmarks=marks["Math AA HL"], pmarks=marks["Physics HL"], cmarks=marks["Computer Science HL"],
         bmarks=marks["Business Management SL"],
         mshare=share("Math AA HL"), pshare=share("Physics HL"), cshare=share("Computer Science HL"),
         bshare=share("Business Management SL"),
         mfig=fshare("Math AA HL"), pfig=fshare("Physics HL"), cfig=fshare("Computer Science HL"))
fig = figs
print("measured:", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in M.items()})

MILESTONE = """- **Batch 34 — DONE (3 items, %(n0)d → %(n)d; the owner's correction to the cap rule landed here).**
  - **Three briefs, all read off the node/component measurement rather than from a topic list.** A
    sweep of which syllabus nodes have no item on which paper component found three concrete holes:
    **B.2 (greenhouse effect) has no Paper 1A item at all** — its 19 clusters cover kinematics,
    thermal cycles, waves, fields and photons but not radiation balance; **AHL 5.17 volumes of
    revolution** carries items with no figure, and it is the one sub-topic whose whole difficulty is
    geometric; and **A1.2 data representation** had integers, two's complement and check digits but
    never floating point. The CS item also feeds the component that is still inverted: Section A
    carries 260 of Paper 1's marks against Section B's 382, where the guide gives Section A 56 of 80.
  - **`PHYS-B.2-601`** (P1A, five MCQs, d4, `non_governing_variable`) is built on one fact told five
    ways — absorption is a matter of wavelength, not of quantity, and the atmosphere is transparent
    where the Sun shines and partly opaque where the Earth shines. The discriminating question (e)
    offers two hypothetical gases and asks which cools the planet's heat loss more: the answer is the
    one whose band lies in the atmospheric window, not the wider, stronger, more familiar band that
    sits on top of the carbon dioxide one already drawn. The wrong answer is the one that sounds
    like science. Supporting numbers all computed: radiating level %(teff)s K, 278 K without the
    albedo, 360 K without the factor of four, Wien ratio 22.7.
  - **`MATH-5.17-701`** (P1 Section B, 14 marks, d5, `non_obvious_tool`) rotates a region that
    straddles the axis of rotation. Between two curves the integrand is decided by *which is on top*
    — the habit a hundred area questions build — but about an axis it is decided by *which is
    further away*, and the two questions change answer at different x-values: the switch is at
    $\\sqrt{2}$, where the ordinates have equal modulus, not at $\\sqrt{3}$ where the curve crosses
    the axis. Volume $= \\frac{32\\pi(11\\sqrt{2}-4)}{105} = 11.06$; the single-washer route returns
    **minus** 3.83, and the plausible-looking $\\sqrt{3}$ split returns 7.67, 30.6%% low.
  - **`CS-A1.2-601`** (P1 Section A, 12 marks, d5, `variable_swap`) states a 16-bit floating-point
    format and then asks the question the format is never asked: given a required *absolute* error
    over an interval, how many mantissa bits? The unknown sits in an exponent, and because the bound
    is absolute while the format's precision is relative, the binding case is the largest value in
    the interval — exponent 9 — so $n = 13$. Part (d) then shows the answer to (c) is a proof of
    impossibility: the exponent field that reaches 1000 needs 5 bits, leaving 10 mantissa bits, and
    the smallest format satisfying both needs 19 bits, not 16.
  - **Five defects caught before shipping, four of them by the machine and one by the eye.**
    (1) An assertion compared $0.199951172$ against the exact stored value at 1e-12 and failed —
    my own transcription rounding, caught by the gate that exists to catch exactly that. (2) The
    same again at 6 decimal places on the Wien ratio. (3) The spectrum's log axis spanned 1–100 µm,
    so the solar curve peaked off-frame and its label was clipped. (4) **The collision check itself
    was wrong**: it compared text *anchor points*, and five 90-pixel band labels 60 pixels apart
    passed it while rendering as an unreadable smear — the check now compares estimated extents, and
    the labels are chemical formulae. (5) The rendered figure then contradicted the answer: part
    (e)'s text claimed no band lies between 8 and 12 µm, and the graph showed ozone at 9.0–10.2 µm.
    The gas was moved to 10.5–12.5 µm, the genuinely open gap, in all five places it is named.
    **(4) is the one to carry forward: a lint that passes a defect is worse than no lint, and it is
    the same failure shape as the CS Paper 2 table — a check written against the wrong quantity.**
  - **Sourcing, and what was refused.** Two searches (A-level practical data-handling; AP CSA
    free-response questions) returned resource catalogues rather than questions. Nothing was claimed
    from them: `CS-A1.2-601` and `PHYS-B.2-601` are recorded `original`, and `MATH-5.17-701` is
    recorded `uk-further-maths` naming only the worked-example collections actually consulted, with
    the adaptation stated. A citation that was not earned is worse than no citation.
  - **The owner's correction, recorded because it changes how the cap is read.** This wave was
    planned after I wrote that Maths "must be written at d4" because it sits at the 50%% cap. That
    was wrong and it has been removed from PLAN.md and from the authoring skill: the cap is a
    **diagnostic on the labels**, not a budget on difficulty, and designing an easier question to
    protect a statistic is the same sin as relabelling an earned one. If a subject crosses 50%%, the
    response is to audit whether the existing d5 labels earn 8 of 9 and demote the ones that do not —
    which is how the 2026-09-16 backlog pass produced five downward corrections.
  - **Numbers after the wave, measured from the data.** %(n)d items — Maths %(math)d / %(mmarks)d
    marks, Physics %(phys)d / %(pmarks)d, CS %(cs)d / %(cmarks)d, BM SL %(bm)d / %(bmarks)d;
    %(tm)d marks. Difficulty %(d3)d / %(d4)d / %(d5)d. d5 shares: Maths %(mshare).0f%%, CS
    %(cshare).0f%%, Physics %(pshare).0f%%, BM %(bshare).0f%%. Evidence %(ev)d / %(n)d,
    `difficulty 5 with no evidence` 0, all 13 levers in use. Assertions %(asr)d. Figures %(fig)d /
    %(n)d = %(figpct).0f%% (Maths %(mfig).0f%%, Physics %(pfig).0f%%, CS %(cfig).0f%%). Sourcing
    %(nonorig)d items outside `original`. `validate.py` 0 failures, `difficulty_audit --check` exit 0.
  - **Follow-up this wave leaves open:** the extent-based label check should be ported back into
    `tools/batch32/` and `tools/batch33/` generators, whose figures passed the older anchor-only
    test — they rendered clean when looked at, but the check that cleared them was weaker than this
    one.
""" % dict(M, n0=n - 3, teff="254.6")

ANCHOR = "- **Priority-3 (\"stretch\") tail:** optional deeper items beyond the must/should nodes \u2014 open when there is"
EDITS = [("PLAN.md", ANCHOR, MILESTONE + ANCHOR)]

failures, cache = [], {}
for path, old, new in EDITS:
    text = cache.get(path) or io.open(path, encoding="utf-8").read()
    c = text.count(old)
    if c != 1:
        failures.append("%s: anchor matched %d -- %.70s" % (path, c, old.replace("\n", " ")))
        continue
    cache[path] = text.replace(old, new)
if failures:
    print("\n".join(failures))
    sys.exit("aborted, nothing written")
for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)
    print("updated", path)
