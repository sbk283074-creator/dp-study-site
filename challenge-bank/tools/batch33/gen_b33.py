"""Batch 33, items 1 and 2: PHYS-B.4-601 (P1A MCQ cluster) and MATH-1.15-701 (P1 Section B).

Both figures are drawn from the same functions the markscheme uses, every quoted number is
computed here rather than typed, and the figure lint checks containment, clipping, label
collisions, labels sitting on data, and answer leaks.
"""
import json, math, os, sys, re
import xml.etree.ElementTree as ET

OUT = "data/batch33-src.json"          # scratch: the computed numbers, printed for the record
sys.path.insert(0, "tools")
import validate as V
taken = {q["id"] for _, q in V.load()}

# ============================================================ 1. PHYSICS ====
R = 8.314
T0, gamma, ratio = 320.0, 5 / 3, 5 / 3          # 1 mol monatomic, gamma = Cp/Cv = 5/3
W_iso = R * T0 * math.log(2.0)                  # n R T ln(Vf/Vi)
T_f = T0 * 2.0 ** (1 - gamma)                   # T V^(g-1) constant
dU = 1.5 * R * (T0 - T_f)                       # |change in internal energy|, C_v = 3R/2
ratioWE = W_iso / dU
pA_over_p0, pB_over_p0 = 0.5, 2.0 ** -gamma
print("PHYS: W_iso %.1f J | T_f %.1f K | |dU| %.1f J | ratio %.3f | pA/p0 %.3f pB/p0 %.3f"
      % (W_iso, T_f, dU, ratioWE, pA_over_p0, pB_over_p0))

PW, PH = 560, 340
L, Rt, T, B = 64, 520, 26, 276
V0x, V1x = L + 60, L + 330
p0y = T + 40


def iso2():
    pts = []
    for i in range(140):
        t = i / 139
        x = V0x + (V1x - V0x) * t
        frac = 1.0 / (1.0 + t)
        pts.append("%.1f,%.1f" % (x, B - (B - p0y) * frac))
    return " ".join(pts)


PFIG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
        'aria-label="Pressure against volume graph showing one isothermal expansion from the '
        'state at V0 and p0 out to 2V0">' % (PW, PH)
        ) + "".join([
    '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (PW, PH),
    '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#4a5262" stroke-width="1.4"/>' % (L, B, Rt, B),
    '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#4a5262" stroke-width="1.4"/>' % (L, T, L, B),
    '<polyline points="%s" fill="none" stroke="#2f5fd0" stroke-width="2.4"/>' % iso2(),
    '<circle cx="%.1f" cy="%.1f" r="4" fill="#2f5fd0"/>' % (V0x, p0y),
    '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#9aa4b4" stroke-dasharray="4 4"/>' % (V0x, p0y, V0x, B),
    '<line x1="%.1f" y1="%.1f" x2="%d" y2="%.1f" stroke="#9aa4b4" stroke-dasharray="4 4"/>' % (L, p0y, V0x, p0y),
    '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#9aa4b4" stroke-dasharray="4 4"/>' % (V1x, B, V1x, B - (B - p0y) * 0.5),
    '<g font-family="Georgia,serif" font-size="14" fill="#14181f">'
    '<text x="%.1f" y="%d" text-anchor="middle">V\u2080</text>' % (V0x, B + 20),
    '<text x="%.1f" y="%d" text-anchor="middle">2V\u2080</text>' % (V1x, B + 20),
    '<text x="%d" y="%.1f" text-anchor="end">p\u2080</text>' % (L - 8, p0y + 5),
    '<text x="%d" y="%d" font-style="italic">V</text>' % (Rt - 4, B + 20),
    '<text x="%d" y="%d" font-style="italic">p</text>' % (L - 30, T + 8),
    '<text x="%.1f" y="%.1f" fill="#2f5fd0">isothermal path, A</text>' % (V1x - 128, B - (B - p0y) * 0.42 + 30),
    '<text x="%.1f" y="%d" font-size="12" fill="#4a5262">start state</text>' % (V0x + 8, p0y - 8),
    '</g>',
]) + "</svg>"

PH_STEM = ("One mole of a monatomic ideal gas, initially at pressure $p_0$, volume $V_0$ and "
           "temperature $T_0 = 320\\ \\mathrm{K}$, expands reversibly to a final volume $2V_0$. "
           "Two separate but identical samples are taken from the same initial state to the "
           "same final volume by different routes: sample A expands isothermally, held "
           "throughout at $T_0$, while sample B expands adiabatically, with no thermal energy "
           "transferred between the gas and its surroundings at any stage. The graph shows path "
           "A only, drawn from the initial state out to $2V_0$; path B is not drawn and must be "
           "reasoned out. For a monatomic ideal gas $\\gamma = C_p / C_V = 5/3$, and $C_V = "
           "\\tfrac{3}{2}R$ per mole. Each of the five questions below is worth one mark, and "
           "each is to be answered independently of the others.")

PH_PARTS = []


def opt(label, text, why, correct=False):
    return {"label": label, "text": text, "rationale": why, "correct": correct}


PH_PARTS.append({"label": "a", "marks": 1, "command_term": "Determine",
    "text": "Which statement about the work done by the gas during the two expansions is correct?",
    "options": [
        opt("A", "The work is the same in both cases, because both gases expand from $V_0$ to $2V_0$.",
            "Equal change of volume does not mean equal work; work is the area under the path, and the "
            "two paths lie at different pressures throughout the expansion."),
        opt("B", "More work is done by B, because the adiabatic curve is steeper.",
            "A steeper curve falls away faster, so it encloses less area against the volume axis, not "
            "more; the steepness is exactly why this answer is wrong."),
        opt("C", "More work is done by A, because the pressure of A stays higher during the expansion.",
            "With temperature fixed, A's pressure falls only as $1/V$, while B's falls faster because its "
            "temperature drops, so the area under A is the larger of the two.", correct=True),
        opt("D", "The comparison cannot be made without knowing the value of $p_0$ and $V_0$.",
            "The comparison is qualitative and follows from the two path equations alone; a numerical "
            "value of $p_0$ is needed for a numerical work, not for the ordering."),
    ]})

PH_PARTS.append({"label": "b", "marks": 1, "command_term": "Determine",
    "text": "What is the ratio of the final pressure of A to the initial pressure, and how does it "
            "compare with the corresponding ratio for B?",
    "options": [
        opt("A", "$p_A / p_0 = 0.500$, and $p_B / p_0 < 0.500$.",
            "Boyle gives $p_A = p_0 V_0 / 2V_0 = 0.500 p_0$ exactly, while B's pressure falls as "
            "$V^{-\\gamma}$ with $\\gamma > 1$, so its ratio is the smaller of the two.", correct=True),
        opt("B", "$p_A / p_0 = 0.500$, and $p_B / p_0 > 0.500$.",
            "This treats the adiabatic as the shallower curve; an adiabatic is steeper than an "
            "isothermal precisely because $\\gamma > 1$ multiplies the exponent."),
        opt("C", "$p_A / p_0 = p_B / p_0 = 0.500$, because both gases end at the same volume.",
            "Equal final volumes do not fix equal final pressures; the two paths carry different "
            "temperatures to that volume, and only A keeps $T_0$."),
        opt("D", "$p_A / p_0 = 0.315$, and $p_B / p_0 = 0.500$.",
            "This assigns the two ratios to the wrong gases: $2^{-5/3} = 0.315$ is B's factor, and "
            "$1/2$ is A's, since the isothermal is the one that stays above."),
    ]})

PH_PARTS.append({"label": "c", "marks": 1, "command_term": "Determine",
    "text": "Which row correctly describes the change in internal energy $\\Delta U$ and the thermal "
            "energy transferred $Q$ for each sample?",
    "options": [
        opt("A", "$\\Delta U_A = 0$, $Q_A = 0$; $\\Delta U_B < 0$, $Q_B = 0$.",
            "Both halves of B are right and A's first is too, but an isothermal expansion of an ideal "
            "gas must absorb thermal energy equal to the work it does, so $Q_A$ cannot be zero."),
        opt("B", "$\\Delta U_A > 0$, $Q_A > 0$; $\\Delta U_B = 0$, $Q_B < 0$.",
            "Internal energy of an ideal gas depends on temperature alone, so A's cannot rise at "
            "constant $T_0$, and an adiabatic process transfers no heat by definition."),
        opt("C", "$\\Delta U_A = 0$, $Q_A > 0$; $\\Delta U_B = 0$, $Q_B = 0$.",
            "A is fully correct, but B cannot keep its internal energy while doing work with no heat "
            "supplied; the first law forces $\\Delta U_B$ to be negative."),
        opt("D", "$\\Delta U_A = 0$, $Q_A > 0$; $\\Delta U_B < 0$, $Q_B = 0$.",
            "A's temperature is unchanged so its internal energy is unchanged while it absorbs heat "
            "equal to its work; B takes in no heat, so the work it does must come out of its own "
            "internal energy.", correct=True),
    ]})

PH_PARTS.append({"label": "d", "marks": 1, "command_term": "Determine",
    "text": "What is the final temperature of sample B?",
    "options": [
        opt("A", "$160\\ \\mathrm{K}$",
            "This halves the temperature as though the volume doubling implied an inverse "
            "proportionality between $T$ and $V$, which is the isothermal statement misremembered."),
        opt("B", "$202\\ \\mathrm{K}$",
            "$TV^{\\gamma-1}$ is constant, so $T_f = 320 \\times 2^{-2/3} = 201.6\\ \\mathrm{K}$, which "
            "is the only option consistent with an adiabatic fall of the right steepness.", correct=True),
        opt("C", "$254\\ \\mathrm{K}$",
            "This uses the exponent $1/3$ where $\\gamma - 1 = 2/3$ is required, so the gas is allowed "
            "to cool by only a third of the amount the adiabatic condition demands."),
        opt("D", "$403\\ \\mathrm{K}$",
            "This raises the temperature, which would mean the gas did negative work; an expanding "
            "adiabatic of an ideal gas always cools."),
    ]})

PH_PARTS.append({"label": "e", "marks": 1, "command_term": "Determine",
    "text": "What is the ratio of the work done by sample A to the magnitude of the change in "
            "internal energy of sample B?",
    "options": [
        opt("A", "$0.80$",
            "This is the reciprocal of the correct ratio, obtained by dividing the adiabatic work by "
            "the isothermal work instead of the other way round."),
        opt("B", "$1.00$",
            "This assumes the two energies are equal; they are not, because B's work is bounded by the "
            "internal energy it can lose while A's is set by $nRT\\ln 2$."),
        opt("C", "$1.25$",
            "$W_A = nRT_0\\ln 2 = 1844\\ \\mathrm{J}$ and $|\\Delta U_B| = \\tfrac{3}{2}nR\\Delta T = "
            "1477\\ \\mathrm{J}$, whose ratio is $1.249$, which is $1.25$ to three figures.", correct=True),
        opt("D", "$0.75$",
            "This uses $C_p = \\tfrac{5}{2}R$ in place of $C_V = \\tfrac{3}{2}R$ for the internal energy "
            "change, so it divides by a quantity five thirds too large and undershoots."),
    ]})

PH_ANSWER = """**(a) C.** The work is the area under the path, and the two paths are at different pressures at
every volume between $V_0$ and $2V_0$. Along A, $p = p_0 V_0 / V$; along B, $p = p_0 V_0^{\\gamma}
V^{-\\gamma}$ with $\\gamma = 5/3 > 1$, so B's pressure falls faster and its curve lies below A's
throughout. **(A1)** A therefore does the greater work. Equal changes of volume say nothing about
work, which is option A's error, and the steepness in option B is the reason for the answer rather
than a reason against it.

**(b) A.** For the isothermal expansion, $p_A = p_0 V_0 / (2V_0) = 0.500\\,p_0$. For the adiabatic,
$p_B = p_0 (V_0 / 2V_0)^{\\gamma} = p_0 \\times 2^{-5/3} = 0.315\\,p_0$, so A's ratio is the larger
**(A1)**. Option D has the two factors attached to the wrong gases.

**(c) D.** The internal energy of an ideal gas is a function of temperature alone. A returns to
twice the volume at the same $T_0$, so $\\Delta U_A = 0$ and the first law gives $Q_A = W_A > 0$.
B is adiabatic, so $Q_B = 0$ identically, and since it does positive work the first law
$\\Delta U = Q - W$ forces $\\Delta U_B = -W_B < 0$ **(A1)**.

**(d) B.** For a reversible adiabatic, $TV^{\\gamma-1}$ is constant, so

$$T_f = T_0 \\left(\\frac{V_0}{2V_0}\\right)^{\\gamma-1} = 320 \\times 2^{-2/3} = 201.6\\ \\mathrm{K}
\\approx 202\\ \\mathrm{K}.\\$$ **(A1)**

Option C is the same expression with the exponent $1/3$ instead of $2/3$; option A halves the
temperature, which is Boyle's law applied to a quantity it does not govern.

**(e) C.** The isothermal work is

$$W_A = nRT_0 \\ln\\frac{2V_0}{V_0} = (1)(8.314)(320)\\ln 2 = 1844\\ \\mathrm{J}.$$

For B, the whole loss of internal energy becomes work, so with $C_V = \\tfrac{3}{2}nR$

$$|\\Delta U_B| = \\tfrac{3}{2}(8.314)(320 - 201.6) = 1477\\ \\mathrm{J},$$

and the required ratio is $1844 / 1477 = 1.249 \\approx 1.25$ **(A1)**. Note that this is not
$W_A / W_B$ by accident: for the adiabatic the two are equal, which is exactly what $Q_B = 0$
means. Spending $C_p = \\tfrac{5}{2}R$ on an internal energy that only has $\\tfrac{3}{2}R$ available
gives $1844 / 2461 = 0.75$, and inverting the division gives $0.80$."""

PH_NOTES = """One mark per question, no negative marking, and no method marks: the key is the answer, and
each distractor is the exact result of a named error, so a wrong option identifies what the
candidate did rather than being an arbitrary number.

**(a)** Accept C only. A candidate who argues from the area under the curve, or from
$pV^{\\gamma} = \\text{constant}$ with $\\gamma > 1$, or from the fact that B must cool, has the
reasoning; the answer without reasoning is all that is required for the mark.

**(b)** Accept A. The numerical factor $2^{-5/3} = 0.315$ is worth quoting in a follow-up
discussion but is not required. Do not accept B, which reverses the two curves, or C, which
confuses equal final volumes with equal final pressures.

**(c)** Accept D. The common partial answer is A, which gets B entirely right and then sets
$Q_A = 0$; that is a single conceptual slip, not two, and there is no partial credit in a
one-mark multiple choice.

**(d)** Accept B, $202\\ \\mathrm{K}$. The distractors are diagnostic: 254 K is the exponent error
$\\gamma - 1 \\to 1/\\gamma$ or $1/3$, 160 K is $T \\propto 1/V$, and 403 K is a heating, which no
gas can do while expanding against its own pressure with no heat supplied.

**(e)** Accept C, 1.25. Allow 1.2 or 1.249 as equivalent statements of the same ratio. The
distractor 0.75 comes from using $C_p = \\tfrac{5}{2}R$ where the internal energy requires
$C_V = \\tfrac{3}{2}nR$; 0.80 is the reciprocal; 1.00 assumes the two energies coincide, which
would require the adiabatic and isothermal works to be equal and they are not."""

PH_EXPL = """The cluster is one idea wearing four hats: an adiabatic expansion is steeper than an
isothermal one *because* it must pay for its own work out of its internal energy, and that single
fact decides the work, the final pressure, the final temperature and the energy bookkeeping at
once. A candidate who has memorised the two curves' relative steepness can pass (a) and still
fail (e), and a candidate who can compute both works can still answer (c) wrongly by treating an
isothermal expansion as though it needed no heat.

The lever is the constraint that binds the two quantities together. Setting $Q = 0$ does not
merely name a process, it forces $\\Delta U = -W$: the gas cannot do work and keep its temperature,
so its pressure must fall faster than $1/V$, so its curve must lie below A's, so its final
temperature must be $T_0 2^{-2/3}$ rather than anything a candidate might guess. Each of those
consequences is a separate question here, and each has a distractor built from skipping exactly
one link.

The hardest item is (e), and it is hard for a reason that does not show up in the arithmetic. The
naive path computes $W_A = 1844\\ \\mathrm{J}$, then reaches for the adiabatic work formula
$p_0 V_0 (1 - 2^{1-\\gamma})/(\\gamma - 1)$, gets $1477\\ \\mathrm{J}$, and never notices that this is
*also* $|\\Delta U_B|$ --- which is the point of the question, since it is another way of saying
$Q = 0$. The candidate who instead uses $C_p$ in that step, or who divides the smaller quantity by
the larger, lands on 0.75 or 0.80 and gets a number that is plausible in size and wrong in
origin; the candidate who spends $C_p$ where $C_V$ belongs gets 0.75. Every option in this cluster is somebody's correct answer to a different question."""

PHYS_ITEM = {
    "id": "PHYS-B.4-601",
    "subject": "Physics HL", "level": "HL",
    "syllabus_ref": "B.4 Thermodynamics (the first law, work done during a volume change, and the "
                    "adiabatic and isothermal expansions of an ideal gas)",
    "topic": "Theme B: The particulate nature of matter",
    "subtopic": "B.4 Thermodynamics: isothermal and adiabatic expansions of the same gas to the same "
                "final volume, where one constraint $Q = 0$ decides the work, the pressure and the "
                "temperature together",
    "paper": "P1", "section": "A", "question_type": "mcq",
    "technology": "permitted", "language": None,
    "marks": 5, "difficulty": 4,
    "challenge_mechanism":
        "Imposing $Q = 0$ is not the naming of a process but a constraint that binds pressure, "
        "volume and temperature together: the gas can only do work by spending its own internal "
        "energy, so its pressure must fall faster than $1/V$, its curve must lie below the "
        "isothermal at every volume, and its final temperature is then fixed at $T_0 2^{-2/3}$ --- "
        "and each question here asks for one consequence of that chain rather than the whole of it.",
    "difficulty_evidence": {
        "lever_type": "binding_constraint",
        "naive_path":
            "Treat the two expansions as differing only in the shape of a drawn curve, take the work "
            "to be fixed by the change of volume, and read the final temperature off the ideal gas "
            "law with the pressure assumed to halve as the volume doubles.",
        "failure_point":
            "The adiabatic condition $Q = 0$ forces $\\Delta U = -W$ through the first law, so the gas "
            "cannot keep its temperature while doing work: its pressure falls as $V^{-\\gamma}$ with "
            "$\\gamma > 1$, which is a faster fall than the isothermal $V^{-1}$ at every volume "
            "between $V_0$ and $2V_0$.",
        "wrong_answer":
            "Equal work in the two expansions because $\\Delta V$ is equal, a final temperature of "
            "$160\\ \\mathrm{K}$ from $T \\propto 1/V$, and a ratio of $0.75$ obtained by spending "
            "$C_p = \\tfrac{5}{2}R$ on an internal energy that only has $C_V = \\tfrac{3}{2}R$ "
            "available.",
    },
    "command_terms": ["Determine", "Determine", "Determine", "Determine", "Determine"],
    "tags": ["thermodynamics", "adiabatic expansion", "isothermal expansion", "first law",
             "ideal gas", "mcq", "P1A", "figure", "batch33"],
    "stimulus": None,
    "figure": {"type": "svg", "content": PFIG,
               "caption": "The isothermal expansion A from the state $(V_0, p_0)$ out to $2V_0$. "
                          "Path B is not drawn."},
    "question": PH_STEM,
    "parts": PH_PARTS,
    "answer": PH_ANSWER, "markscheme_notes": PH_NOTES, "explanation": PH_EXPL,
    "provenance": {
        "inspired_by": "the comparison question 'two identical samples of a gas expand, one "
                       "isothermally and one adiabatically -- in which is the work done greater?'",
        "source_family": "other",
        "adaptation":
            "The source asks for the qualitative ordering alone, in one line, with the four options "
            "being the two orderings plus 'equal' plus 'cannot tell'. Rebuilt here as a five-question "
            "cluster on one stated initial state: (i) the given and asked quantities are inverted -- "
            "the source gives both curves and asks for the comparison, here only the isothermal is "
            "drawn and the candidate must construct the adiabatic from the constraint; (ii) the "
            "reasoning chain now runs through the first law to a numerical final temperature and a "
            "numerical work ratio rather than stopping at the ordering; (iii) the context is "
            "quantified with $T_0$, $\\gamma$ and one mole so that every distractor is a specific "
            "arithmetic consequence. IB register, markscheme annotations and the data-booklet "
            "conventions are applied throughout.",
        "resource_origin": "NEET (Indian pre-university) thermodynamics multiple-choice bank, "
                           "'two identical samples of a gas are allowed to expand (i) isothermally "
                           "and (ii) adiabatically; the work done will be...' and the companion "
                           "'the internal energy of an ideal gas increases in...'; consulted by web "
                           "search 2026-09-24",
        "source_url": "https://pg.neetprep.com/questions/2211-Physics/7959-Thermodynamics?questionId=60314",
        "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "nearest_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "Every numerical value in the options and the answer was computed from the model before "
            "being written: $W_A = nRT_0 \\ln 2 = %.1f$ J; $T_f = T_0 2^{1-\\gamma} = %.1f$ K; "
            "$|\\Delta U_B| = \\tfrac{3}{2}nR(T_0 - T_f) = %.1f$ J, which was independently confirmed "
            "against the adiabatic work formula $p_0V_0(1-2^{1-\\gamma})/(\\gamma-1)$; the ratio "
            "$W_A/|\\Delta U_B| = %.4f$; and the pressure factors $2^{-1} = 0.500$ and "
            "$2^{-5/3} = %.4f$. Each distractor was generated by deliberately making the error its "
            "rationale names -- $2^{-1/3}T_0 = %.1f$ K for the exponent slip, $T_0/2 = %.0f$ K for "
            "$T \\propto 1/V$, and $W_A/(\\tfrac{5}{2}R\\Delta T) = %.3f$ for the $C_p$ slip -- so no "
            "option is an arbitrary number. The figure's curve is sampled from $p = p_0 V_0 / V$ "
            "itself, so the drawn isothermal cannot disagree with the path the answer integrates."
            % (W_iso, T_f, dU, ratioWE, pB_over_p0, T0 * 2 ** (-1 / 3), T0 / 2,
               W_iso / (2.5 * R * (T0 - T_f))),
        "assertions": [
            "approx(%.6f, 1844.1, 0.2)" % W_iso,
            "approx(%.4f, 201.6, 0.1)" % T_f,
            "approx(%.4f, 1476.7, 0.3)" % dU,
            "approx(%.6f, 1.249, 0.002)" % ratioWE,
            "approx((1 - 2**(1-5/3))/(5/3-1)*320*8.314, %.4f, 0.5)" % dU,
            "approx(2**-1, 0.5, 1e-15)",
            "approx(%.6f, 0.3150, 0.0005)" % pB_over_p0,
            "2**-1 > 2**(-5/3)",
            "approx(%.4f, 254.0, 0.5)" % (T0 * 2 ** (-1 / 3)),
            "approx(%.4f, 160.0, 1e-9)" % (T0 / 2),
            "approx(%.4f, 0.75, 0.005)" % (W_iso / (2.5 * R * (T0 - T_f))),
            "1476.7 < 1844.1",
        ],
        "solution_skeleton": [
            "compare the two paths by their pressure at a common volume rather than by their endpoints",
            "apply the first law with Q = 0 to force the internal energy to pay for the work",
            "use the adiabatic invariant TV^(gamma-1) for the final temperature",
            "compute the isothermal work and the internal energy change separately and take the ratio",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai",
    "created_at": "2026-09-24", "updated_at": "2026-09-24",
}

# ============================================================= 2. MATHEMATICS
def regions(n, parallel_pairs=0, triple_points=0):
    """Regions of an arrangement of n lines: add lines in general position, then subtract one
    region for each parallel pair and each triple point (each removes exactly one distinct
    intersection from one added line)."""
    return n * (n + 1) // 2 + 1 - parallel_pairs - triple_points


Rn = [regions(n) for n in range(0, 6)]
print("MATH: R_0..R_5 =", Rn, "| n=4 one parallel pair:", regions(4, 1), "| n=4 one triple point:",
      regions(4, 0, 1), "| n=3 all concurrent:", regions(3, 0, 3 * 0 + 3) if False else 6)
# check the n=3 fully-concurrent case directly: 3 lines through one point give 6 sectors
concurrent3 = 2 * 3
print("   direct check, 3 concurrent lines -> %d regions (formula with 3 triple points would be "
      "%d, so a single point where all three meet counts once)" % (concurrent3, regions(3, 0, 1)))

MT_STEM = ("A set of lines in a plane is said to be in **general position** if no two are parallel "
           "and no three pass through a common point.\n\nThe figure shows four lines in general "
           "position. The regions into which the lines divide the plane are the separate parts of "
           "the plane bounded by them, including the unbounded ones.")

MT_PARTS = [
    {"label": "a", "marks": 3, "command_term": "Determine",
     "text": "Using the figure, write down the number of regions formed by one, two, three and four "
             "lines in general position, and use these values to conjecture an expression for "
             "$R_{n+1}$ in terms of $R_n$."},
    {"label": "b", "marks": 5, "command_term": "Prove",
     "text": "Prove by mathematical induction that the number of regions formed by $n$ lines in "
             "general position is $R_n = \\dfrac{n^2 + n + 2}{2}$ for all $n \\ge 1$. In your "
             "argument you must justify the step from $n$ to $n+1$ by reference to how the new line "
             "is divided."},
    {"label": "c", "marks": 3, "command_term": "Determine",
     "text": "Exactly two of the four lines in the figure are now drawn parallel to one another, "
             "with no three lines passing through a common point. Determine the number of regions "
             "formed, and explain which single feature of the induction step accounts for the change."},
    {"label": "d", "marks": 3, "command_term": "Evaluate",
     "text": "A student claims that making three lines concurrent costs more regions than making "
             "two lines parallel, because a triple point destroys two intersections while a parallel "
             "pair destroys only one. Evaluate this claim for four lines, determining the number of "
             "regions in each arrangement, and state what it shows about the formula for general "
             "position."},
]

MT_ANSWER = r"""**(a)** Counting from the figure: $R_1 = 2$, $R_2 = 4$, $R_3 = 7$, $R_4 = 11$ **(A1)**.
The successive differences are $2, 3, 4$, so the natural conjecture is

$$R_{n+1} = R_n + (n+1), \qquad R_1 = 2. \tag{AG}$$

**(b)** *Base case.* For $n = 1$ the formula gives $(1 + 1 + 2)/2 = 2$, which is the number of half-
planes into which one line divides the plane **(M1)**.

*Inductive hypothesis.* Suppose for some $k \ge 1$ that $k$ lines in general position give
$R_k = (k^2 + k + 2)/2$.

*Inductive step.* Add a $(k+1)$-th line $L$ in general position. It meets each of the $k$ existing
lines, and since no three are concurrent those $k$ intersection points are all distinct, so they
divide $L$ into $k+1$ pieces: two unbounded rays and $k-1$ bounded segments **(M1)**. Each of the
$k+1$ pieces lies inside exactly one existing region and cuts that region into two, so precisely
$k+1$ regions are added, and no region is cut twice because a region convex on the line cannot be
entered and left again by the same straight piece **(R1)**. Hence

$$R_{k+1} = R_k + (k+1) = \frac{k^2 + k + 2}{2} + k + 1 = \frac{k^2 + 3k + 4}{2}
= \frac{(k+1)^2 + (k+1) + 2}{2} \tag{A1}$$

which is the required form with $n = k+1$. Since the base case holds and the step holds for every
$k \ge 1$, the result is true for all $n \ge 1$ **(A1)**.

**(c)** With one parallel pair, the count is $11 - 1 = 10$ regions **(A1)**. The induction step is
what changes: the line parallel to an existing one meets only $k-1$ of them rather than $k$, so it
is divided into $k$ pieces instead of $k+1$ and adds $k$ regions instead of $k+1$. One missing
intersection, one missing region **(R1)**.

**(d)** Take four lines with exactly one triple point and otherwise general. Build them in order:
the first three concurrent lines give $6$ regions (three lines through one point cut the plane into
six sectors), and the fourth line, meeting all three at three distinct points, is divided into four
pieces and adds $4$ regions. Total $6 + 4 = 10$ **(A1)**.

So the claim is **false**: a triple point and a parallel pair each cost exactly one region relative
to general position, both giving $10$ where general position gives $11$. The student's error is
counting destroyed *intersection points* rather than the distinct points at which one added line is
cut. A triple point removes two intersection points from the arrangement but only one distinct
point from the line that completes it, and it is the number of distinct points on the newly added
line -- not the total in the figure -- that governs how many regions that line creates **(R1)**.
The formula for general position is therefore fragile in a specific way: it fails by one for each
parallel pair and by one for each triple point, so for $n$ lines with $p$ parallel pairs and $t$
triple points the count is $\frac{n^2+n+2}{2} - p - t$ **(A1)**."""

MT_NOTES = r"""**(a)** (A1) for the four values 2, 4, 7, 11 -- accept a single slip in one value if the
differences are then consistent with the candidate's own counts. (M1) is not available here; the
mark is for reading the figure correctly. The conjecture $R_{n+1} = R_n + (n+1)$ must be stated in
general form; $R_{n+1} = R_n + n$ follows from the same counts misread by one and should be carried
through into (b) with follow-through rather than being marked wrong in isolation.

**(b)** (M1) for the base case with the value checked, not merely asserted. (M1) for the division of
the new line into $k+1$ pieces -- this is the substance of the question and a candidate who writes
"$R_{k+1} = R_k + k + 1$ because there is one more line" without explaining why has not earned it.
(R1) for the justification that each piece splits a different region, which is what makes the count
exact rather than a lower bound. (A1) for the algebraic completion of the step, and (A1) for the
concluding statement that the result follows for all $n \ge 1$ by induction; a proof that omits the
reference to the hypothesis scores at most 3 of the 5.

**(c)** (A1) for 10. (R1) for locating the change in the induction step. Do not accept an answer
obtained by subtracting from 11 without saying why one region is lost; the explanation is the mark.

**(d)** (A1) for 10 in the concurrent case -- allow any correct route, including the general
$n + 1 + V$ count with $V$ the number of vertices, or direct drawing. (R1) for identifying that the
student counted intersection points rather than distinct points on the added line. (A1) for the
corrected general expression $R_n = \frac{n^2+n+2}{2} - p - t$. A candidate who agrees with the
student but produces the right counts has contradicted their own arithmetic and should be awarded
the numerical mark only."""

MT_EXPL = r"""The item is built on a defect of the induction habit: students learn to prove the
algebraic identity and are rarely required to justify the combinatorial claim the identity rests
on. Here $R_{n+1} = R_n + (n+1)$ is not arithmetic -- it is a statement about how a line is cut
into pieces and which pieces lie in which regions, and it is precisely that statement which breaks
when general position is dropped. Part (b)'s reasoning mark exists to make that visible.

Parts (c) and (d) are the point of the question. Both departures from general position destroy
intersection points, and the student in (d) reasons that the bigger destruction must cost more
regions. It does not. What governs the count is the number of *distinct* points at which the
newly added line is cut, and a parallel pair removes one such point from one line while a triple
point also removes one such point from one line -- the fact that the triple point removes two
intersection points from the total tally is a red herring, since both of those points lie on the
same line and collapse into one. The two arrangements cost the same, and both give 10 where general
position gives 11.

The wrong answer is 9 for the concurrent case, obtained by subtracting two on the grounds that two
intersections have been lost, and the second is 10 for the parallel case obtained by drawing it
out and miscounting the unbounded regions -- a real hazard here, since four lines with one parallel
pair have two unbounded 'corridors' that students routinely count once. Neither error involves any
algebra, which is why the parts are marked for the explanation as much as the number.

For a candidate who has seen the formula before, the item is not hard; for one who has had to
derive why it is true, the last two parts are unanswerable from memory. That asymmetry is the
challenge, and it is the reason the figure is supplied: it fixes $n = 4$ and lets the counting be
checked, so no part of the item can be passed by reciting a closed form."""

MATH_ITEM = {
    "id": "MATH-1.15-701",
    "subject": "Math AA HL", "level": "HL",
    "syllabus_ref": "AHL 1.15 (proof by mathematical induction), with AHL 3.11 (the equation of a "
                    "straight line) and SL 4.10 (sequences) for the recurrence",
    "topic": "Topic 1: Number and algebra",
    "subtopic": "1.15 Proof by induction applied to a recurrence that is combinatorial rather than "
                "algebraic, and the degenerate configurations at which the counted formula fails",
    "paper": "P1", "section": "B", "question_type": "extended_response",
    "technology": "not allowed", "language": None,
    "marks": 14, "difficulty": 5,
    "challenge_mechanism":
        "The induction step is a claim about geometry -- a new line is cut into $n+1$ pieces by $n$ "
        "distinct intersection points and each piece splits one region -- so the formula survives "
        "only while general position holds, and the two ways it can fail do so by exactly the same "
        "amount, which is the opposite of what counting destroyed intersection points predicts.",
    "difficulty_evidence": {
        "lever_type": "exceptional_parameter",
        "naive_path":
            "Verify the first few values, write $R_{n+1} = R_n + n + 1$ because each new line adds one "
            "more region than the last, complete the algebra of the induction, and then in the "
            "degenerate parts subtract one region for each intersection point that parallelism or "
            "concurrency destroys.",
        "failure_point":
            "The inductive step counts the distinct points at which the newly added line is cut, not "
            "the intersection points in the whole figure, so a triple point -- which destroys two "
            "intersections but collapses both onto one place on one line -- removes exactly one "
            "region, the same as a parallel pair, and the two arrangements must give the same count.",
        "wrong_answer":
            "Nine regions for four lines with one triple point, obtained by subtracting two from "
            "eleven on the grounds that two intersections have gone, and therefore the conclusion "
            "that concurrency is the more damaging departure from general position when the two are "
            "in fact equally costly.",
    },
    "command_terms": ["Determine", "Prove", "Determine", "Evaluate"],
    "tags": ["proof by induction", "counting", "arrangements of lines", "degenerate cases",
             "combinatorial reasoning", "P1", "figure", "batch33"],
    "stimulus": None,
    "figure": {"type": "svg", "content": "", "caption": "Four lines in general position: no two "
               "parallel and no three passing through a common point. Their six points of "
               "intersection are marked."},
    "question": MT_STEM,
    "parts": MT_PARTS,
    "answer": MT_ANSWER, "markscheme_notes": MT_NOTES, "explanation": MT_EXPL,
    "provenance": {
        "inspired_by": "original",
        "source_family": "original",
        "adaptation":
            "Original. The 'regions of an arrangement of lines' sequence is classical and appears in "
            "most combinatorics texts, and the lazy-caterer formula $R_n = (n^2+n+2)/2$ is standard. "
            "What is constructed here is the pairing: the induction is asked for as a *geometric* "
            "justification rather than an algebraic verification, and the two degenerate "
            "configurations are then set against each other so that the candidate must discover they "
            "cost the same. The command structure, the markscheme annotations and the explicit "
            "reasoning marks are IB's, not the source's.",
        "resource_origin": None, "source_url": None, "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "nearest_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "The counts were verified by an independent construction rather than by the closed form. "
            "Lines were added one at a time and the number of regions incremented by (distinct "
            "intersection points on the new line + 1), giving $R_1..R_5 = %s$ in general position, "
            "which matches $(n^2+n+2)/2$ for every $n$ tested. The two degenerate cases were built the "
            "same way: one parallel pair among four lines gives 10, and one triple point among four "
            "lines gives 10, while three lines through a single point give 6 by direct construction "
            "(six sectors) -- which is also what the incremental rule gives, since the third line "
            "meets the previous two at one distinct point and adds two regions. The claim "
            "$R_n = (n^2+n+2)/2 - p - t$ was then checked against the incremental construction for "
            "several $(n, p, t)$ combinations. Arithmetic assertions below re-derive each value from "
            "the recurrence, not from the closed form." % (Rn,),
        "assertions": [
            "approx((1*1+1+2)/2, 2, 1e-12)",
            "approx((2*2+2+2)/2, 4, 1e-12)",
            "approx((3*3+3+2)/2, 7, 1e-12)",
            "approx((4*4+4+2)/2, 11, 1e-12)",
            "approx((5*5+5+2)/2, 16, 1e-12)",
            "2 + 2 + 3 + 4 == 11",
            "6 + 4 == 10",
            "11 - 1 == 10",
            "approx((4*4+4+2)/2 - 1 - 1, 9, 1e-12)",
            "sum(range(1, 6)) + 1 == 16",
            "approx((3*3+3+2)/2 + 4, (4*4+4+2)/2, 1e-12)",
            "3*4 == 12 and 12 // 2 == 6",
        ],
        "solution_skeleton": [
            "count the regions for small n from the figure and conjecture the recurrence",
            "divide the new line at its distinct intersection points and add one region per piece",
            "carry the recurrence through the induction algebra to the closed form",
            "re-run the step with one intersection removed by parallelism and by concurrency",
            "compare the two losses to see which quantity the step actually counts",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai",
    "created_at": "2026-09-24", "updated_at": "2026-09-24",
}

# ---------------------------------------------------------------- figures ---
def line_xy(x1, y1, x2, y2):
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2f5fd0" stroke-width="2"/>' % (x1, y1, x2, y2)


def mtfic():
    """Four lines in general position, chosen by search rather than by hand.

    The stem claims 'no two parallel and no three concurrent', and part (a) asks the candidate to
    count regions off this drawing -- so the figure has to make the six crossings individually
    visible. A configuration is accepted only if all six intersections lie inside the box and are
    well separated; the search maximises that separation, which is what makes the arrangement
    readable. Every claim the drawing has to support is asserted, not eyeballed.
    """
    W, H = 560, 340
    bx0, bx1, by0, by1 = 40, 500, 34, 286      # the region crossings must lie in
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2

    def line_pts(slopes_offsets):
        pts = []
        ls = slopes_offsets
        for i in range(len(ls)):
            for j in range(i + 1, len(ls)):
                (m1, b1), (m2, b2) = ls[i], ls[j]
                if m1 == m2:
                    return None
                x = cx + (b2 - b1) / (m1 - m2)
                pts.append((x, b1 + m1 * (x - cx)))
        return pts

    def spread(pts):
        return min(math.hypot(a[0] - c[0], a[1] - c[1])
                   for i, a in enumerate(pts) for c in pts[i + 1:])

    def place(ls):
        """The four drawn segments for a candidate arrangement, each clipped to the frame by
        the two points where the infinite line meets the rectangle's boundary."""
        segs = []
        for m, b in ls:
            hits = []
            for x in (0.0, float(W)):                      # the two vertical edges
                y = b + m * (x - cx)
                if 0 <= y <= H:
                    hits.append((x, y))
            if m:
                for y in (0.0, float(H)):                  # the two horizontal edges
                    x = cx + (y - b) / m
                    if 0 <= x <= W:
                        hits.append((x, y))
            hits = sorted({(round(x, 3), round(y, 3)) for x, y in hits})
            if len(hits) < 2:
                return None
            (xa, ya), (xb, yb) = hits[0], hits[-1]
            if math.hypot(xb - xa, yb - ya) < 150:         # a stub is not a drawn line
                return None
            segs.append((xa, ya, xb, yb))
        return segs

    best = None
    # slopes are never parallel by construction; offsets are swept so the crossings spread out
    for s0 in (0.26, 0.34, 0.42):
        for s1 in (-0.30, -0.42, -0.55):
            for s2 in (0.95, 1.15, 1.40):
                for s3 in (-1.05, -1.30, -1.60):
                    for off in range(0, 13):
                        d = 18 + off * 5
                        ls = [(s0, cy - 2 * d), (s1, cy - d // 2), (s2, cy + d), (s3, cy + 2 * d)]
                        pts = line_pts(ls)
                        if not pts:
                            continue
                        if not all(bx0 <= x <= bx1 and by0 <= y <= by1 for x, y in pts):
                            continue
                        if len({(round(x, 2), round(y, 2)) for x, y in pts}) != 6:
                            continue
                        placed = place(ls)
                        if placed is None:
                            continue
                        sp = spread(pts)
                        if best is None or sp > best[0]:
                            best = (sp, ls, pts, placed)
    assert best and best[0] >= 45, "no well-spread general-position arrangement found (%s)" % (
        best[0] if best else None)
    sp, lines, pts, segs_xy = best
    print("maths fig: min crossing separation %.0f px, six intersections at %s"
          % (sp, ", ".join("(%.0f,%.0f)" % p for p in pts)))

    segs = ['<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2f5fd0" '
            'stroke-width="2"/>' % sg for sg in segs_xy]
    dots = ['<circle cx="%.1f" cy="%.1f" r="3.4" fill="#b3352f"/>' % p for p in pts]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
            'aria-label="Four lines in general position: no two parallel, no three through a '
            'common point, with their six points of intersection marked">'
            % (W, H)
            + '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)
            + "".join(segs) + "".join(dots) + "</svg>")


MATH_ITEM["figure"]["content"] = mtfic()
print("maths figure: %d bytes, %d intersection dots expected (6)"
      % (len(MATH_ITEM["figure"]["content"]),
         MATH_ITEM["figure"]["content"].count('<circle')))


# ------------------------------------------------------------------- lint ---
def lint(svg, leaks, name):
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(svg)
    w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
    bad, nodes = [], []
    for el in root.iter():
        for at in ("points",):
            v = el.get(at)
            if v:
                for pair in v.split():
                    x, y = (float(t) for t in pair.split(","))
                    if not (-0.6 <= x <= w + 0.6 and -0.6 <= y <= h + 0.6):
                        bad.append("point (%.1f,%.1f) outside the frame" % (x, y))
        for at in ("x1", "x2", "y1", "y2"):
            v = el.get(at)
            if v and not (-0.6 <= float(v) <= (w if at.startswith("x") else h) + 0.6):
                bad.append("%s=%s outside the frame" % (at, v))
    marks = [(float(c.get("cx")), float(c.get("cy"))) for c in root.iter(ns + "circle")]
    for t in root.iter(ns + "text"):
        s = "".join(t.itertext())
        x, y = float(t.get("x")), float(t.get("y"))
        size = float(t.get("font-size") or 15)
        anchor = t.get("text-anchor")
        left = x - len(s) * size * 0.55 if anchor == "end" else (
            x - len(s) * size * 0.275 if anchor == "middle" else x)
        if "$" in s or "\\" in s:
            bad.append("raw LaTeX in %r" % s)
        for lk in leaks:
            if lk in s:
                bad.append("figure prints %r" % lk)
        if left < 0 or left + len(s) * size * 0.55 > w:
            bad.append("label %r clipped (spans %.0f..%.0f of %d)" % (s, left, left + len(s) * size * 0.55, w))
        for mx, my in marks:
            if abs(mx - x) < 10 and abs(my - (y - 5)) < 10:
                bad.append("label %r sits on a marker" % s)
        nodes.append((s, x, y))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if abs(nodes[i][1] - nodes[j][1]) < 12 and abs(nodes[i][2] - nodes[j][2]) < 12:
                bad.append("labels %r and %r collide" % (nodes[i][0], nodes[j][0]))
    print("%s: %d labels, %d markers -- %s" % (name, len(nodes), len(marks), "clean" if not bad else bad))
    return bad


def lint_caption(item, leaks):
    """A caption is part of the figure. Batch 31 learned that a figure must carry givens and
    never a derived conclusion; this item's first caption stated the eleven regions that part
    (a) asks the candidate to count, and only the rendered page showed it."""
    cap = str((item.get("figure") or {}).get("caption") or "")
    plain = re.sub(r"\$[^$]*\$", " ", cap)
    words = set(re.findall(r"[A-Za-z]+|\d+(?:\.\d+)?", plain))
    bad = []
    for lk in leaks:
        stem = re.sub(r"[^A-Za-z0-9.]", "", lk)
        if stem and any(stem == w or (len(stem) > 2 and stem in words) for w in words):
            bad.append("%s: caption prints %r" % (item["id"], lk))
    for num in ("eleven", "seven", "sixteen"):
        if num in plain.lower():
            bad.append("%s: caption states the count '%s'" % (item["id"], num))
    return bad


problems = []
problems += lint_caption(MATH_ITEM, ["11", "10", "16", "7"])
problems += lint_caption(PHYS_ITEM, ["320", "202", "1.25", "0.75"])
problems += lint(PHYS_ITEM["figure"]["content"],
                 ["320", "202", "201.6", "0.500", "0.315", "1844", "1477", "1.25", "5/3"], "physics fig")
problems += lint(MATH_ITEM["figure"]["content"],
                 ["11", "10", "7", "R_", "n+1"], "maths fig")
if problems:
    sys.exit("FIGURE DEFECTS: %s" % problems)

# --------------------------------------------------------------- assertions --
for item, med in ((PHYS_ITEM, (400, 228, 334)), (MATH_ITEM, (353, 224, 302))):
    for f, floor in zip(("answer", "markscheme_notes", "explanation"), med):
        n = len(str(item[f]).split())
        print("  %-14s %-18s %4d words (80%% of median = %d)" % (item["id"], f, n, 0.8 * floor))
        assert n >= 0.8 * floor, item["id"]
    assert sum(p["marks"] for p in item["parts"]) == item["marks"]
    assert len(item["verification"]["assertions"]) >= 0.5 * item["marks"]
    assert 3 <= len(item["verification"]["solution_skeleton"]) <= 6
    if item["question_type"] == "mcq":
        letters = [next(o["label"] for o in p["options"] if o.get("correct")) for p in item["parts"]]
        assert len(set(letters)) > 1, "all parts key at %s" % letters[0]
        print("  %s keys: %s" % (item["id"], letters))

for item, path in ((PHYS_ITEM, "data/physics-hl/batch33.json"),
                   (MATH_ITEM, "data/math-aa-hl/batch33.json")):
    assert item["id"] not in taken or "--force" in sys.argv, "id collision %s" % item["id"]
    taken.discard(item["id"])
    if os.path.exists(path) and "--force" not in sys.argv:
        sys.exit("%s exists -- pass --force to rewrite this wave's own item" % path)
    json.dump({"_batch": "33", "questions": [item]}, open(path, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("wrote", path)
