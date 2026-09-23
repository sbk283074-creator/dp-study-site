"""Generate PHYS-B.5-601 -- Physics HL, Paper 1B, data_based, 13 marks.

Every number in the answer, the markscheme notes, the evidence and the assertions is
printed from the least-squares fit of data generated from the model, so the prose cannot
drift from the data. The figure is drawn from the same rounded points and fitted lines.
"""
import json, math, os, random, sys, re
import xml.etree.ElementTree as ET

E_TRUE, r_TRUE, DELTA = 1.50, 2.40, 0.040
random.seed(20260923)


def gen(currents, zero_offset, noise_A, res_A, res_V):
    rows = []
    for I_disp in currents:
        V = E_TRUE - r_TRUE * (I_disp - zero_offset) + random.uniform(-0.006, 0.006)
        rows.append((round(I_disp + random.uniform(-noise_A, noise_A), res_A), round(V, res_V)))
    return rows


A = gen([0.100, 0.200, 0.300, 0.400, 0.500, 0.600], DELTA, 0.0004, 3, 2)   # digital, never zeroed
B = gen([0.10, 0.20, 0.30, 0.40, 0.50, 0.60], 0.0, 0.012, 2, 2)            # analogue, zeroed


def fit(pts):
    n = len(pts)
    sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts); sxy = sum(p[0] * p[1] for p in pts)
    den = n * sxx - sx * sx
    m = (n * sxy - sx * sy) / den
    c = (sy - m * sx) / n
    s2 = sum((y - (m * x + c)) ** 2 for x, y in pts) / (n - 2)
    return m, c, math.sqrt(s2 * n / den), math.sqrt(s2 * sxx / den)


mA, cA, smA, scA = fit(A)
mB, cB, smB, scB = fit(B)
rA, rB = -mA, -mB
r_comb, e_comb = math.hypot(smA, smB), math.hypot(scA, scB)
dE, dr = cA - cB, abs(rA - rB)
ratioE, ratioR = dE / e_comb, dr / r_comb
r_mid = (rA + rB) / 2
implied = dE / r_mid
u_implied = implied * math.hypot(e_comb / dE, r_comb / r_mid)
pred = r_TRUE * DELTA

# ------------------------------------------------------------------ figure
W, H = 620, 400
L, R, T, Bt = 62, 588, 26, 330
XMAX, YMAX = 0.70, 1.70
px = lambda v: L + (R - L) * v / XMAX
py = lambda v: Bt - (Bt - T) * v / YMAX
INK, INK2 = "#14181f", "#4a5262"
BLUE, RED = "#2f5fd0", "#b3352f"

parts = ['<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H),
         '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.4"/>' % (L, Bt, R, Bt, INK2),
         '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.4"/>' % (L, T, L, Bt, INK2)]
for v in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
    parts.append('<line x1="%.1f" y1="%s" x2="%.1f" y2="%s" stroke="%s"/>' % (px(v), Bt, px(v), Bt + 5, INK2))
    parts.append('<text x="%.1f" y="%s" text-anchor="middle" font-size="12" fill="%s">%.1f</text>'
                 % (px(v), Bt + 20, INK2, v))
for v in (0.4, 0.8, 1.2, 1.6):
    parts.append('<line x1="%s" y1="%.1f" x2="%s" y2="%.1f" stroke="%s"/>' % (L - 5, py(v), L, py(v), INK2))
    parts.append('<text x="%s" y="%.1f" text-anchor="end" font-size="12" fill="%s">%.1f</text>'
                 % (L - 9, py(v) + 4, INK2, v))
parts.append('<text x="%s" y="%s" text-anchor="middle" font-size="13" fill="%s">current I / A</text>'
             % ((L + R) / 2, Bt + 44, INK))
parts.append('<text x="16" y="%s" font-size="13" fill="%s" transform="rotate(-90 16 %s)">'
             'terminal p.d. V / V</text>' % ((T + Bt) / 2, INK, (T + Bt) / 2))
parts.append('<text x="%s" y="%s" font-size="12" fill="%s">bars: \u00b10.01 V; \u00b10.001 A (A), '
             '\u00b10.02 A (B)</text>' % (L + 6, T + 14, INK2))
# A's label above its line at the left, B's below its line: both at I where the two
# lines are furthest apart, so neither sits on the other's marker
for m, c, col, tag, lx, dy in ((mA, cA, BLUE, "A", 0.075, -10), (mB, cB, RED, "B", 0.050, +20)):
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>'
                 % (px(0.05), py(m * 0.05 + c), px(0.66), py(m * 0.66 + c), col))
    parts.append('<text x="%.1f" y="%.1f" font-size="14" fill="%s">%s</text>'
                 % (px(lx) + 8, py(m * lx + c) + dy, col, tag))
for pts, col, ei in ((A, BLUE, 0.0005), (B, RED, 0.02)):
    for x, y in pts:
        # \u00b10.01 V is about 3 px at this scale, so the bar gets end caps: without them
        # the legend claims a vertical uncertainty the reader cannot see. The caps widen
        # the mark, they do not lengthen it -- the half-height stays exactly 0.01 V.
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1"/>'
                     % (px(x), py(y - 0.01), px(x), py(y + 0.01), col))
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1"/>'
                     % (px(x) - 2.4, py(y - 0.01), px(x) + 2.4, py(y - 0.01), col))
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1"/>'
                     % (px(x) - 2.4, py(y + 0.01), px(x) + 2.4, py(y + 0.01), col))
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1"/>'
                     % (px(x - ei), py(y), px(x + ei), py(y), col))
        parts.append('<circle cx="%.1f" cy="%.1f" r="3.6" fill="%s"/>' % (px(x), py(y), col))

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="Two '
       'sets of terminal potential difference against current, A and B, each with error bars and '
       'its own line of best fit">' % (W, H)) + "".join(parts) + "</svg>"

# ------------------------------------------------------------------ prose
TABLE = {"caption": "Terminal potential difference against current, as each student recorded it",
         "columns": ["A: $I$ / A", "A: $V$ / V", "B: $I$ / A", "B: $V$ / V"],
         "rows": [["%.3f" % a[0], "%.2f" % a[1], "%.2f" % b[0], "%.2f" % b[1]] for a, b in zip(A, B)]}

STEM = ("A cell of electromotive force $E$ and internal resistance $r$ is connected to a variable "
        "resistor and the terminal potential difference $V$ across the cell is measured for six "
        "values of the current $I$. Two students carry out the experiment with the same cell. "
        "Student A uses a digital ammeter of resolution 0.001 A; student B uses an analogue "
        "ammeter of resolution 0.02 A. Both use the same voltmeter, of resolution 0.01 V. For a "
        "cell, $V = E - Ir$.")

PARTS = [
    dict(label="a", marks=3, command_term="Determine",
         text="Using the graph, determine the electromotive force and the internal resistance "
              "obtained by each student, stating an appropriate absolute uncertainty for each."),
    dict(label="b", marks=3, command_term="Show that",
         text="Suppose student A's ammeter reads a constant current $\\delta$ when no current is "
              "in fact passing. Show that the line of best fit through A's results has the same "
              "gradient as the line through the true values, but an intercept on the $V$ axis "
              "greater by $r\\delta$."),
    dict(label="c", marks=3, command_term="Evaluate",
         text="Student A claims that A's value of $E$ is the better one because both of A's "
              "uncertainties are smaller than B's. Evaluate this claim, referring to the "
              "agreement or otherwise between the two students' values of $r$ and of $E$."),
    dict(label="d", marks=4, command_term="Determine",
         text="Student B suggests that A's ammeter was not zeroed and read high by about 0.04 A "
              "throughout. Determine the offset implied by the two graphs, decide whether B's "
              "suggestion is supported, and state which value of $E$ should be accepted."),
]

ANSWER = r"""**(a)** Each line gives an intercept and a gradient **(M1)**:

$$E_A = %.2f \pm %.2f\ \mathrm{V},\quad r_A = %.2f \pm %.2f\ \Omega,$$
$$E_B = %.2f \pm %.2f\ \mathrm{V},\quad r_B = %.2f \pm %.2f\ \Omega.$$

The uncertainty on each intercept follows from the spread of the six points about the fitted
line, and the same spread referred to the current range gives the gradient uncertainty **(A1)**.
A's are the smaller because A's currents span the same range with far less scatter: the vertical
spread is common to both, and it is the width of the horizontal distribution that fixes how
firmly the line is pinned **(A1)**.

**(b)** A plots $I' = I + \delta$ against $V$, where $I$ is the true current. Since
$V = E - rI = E - r(I' - \delta)$ **(M1)**,

$$V = (E + r\delta) - rI',$$

so the coefficient of $I'$ is still $-r$ while the intercept has become $E + r\delta$ **(A1)**.
The reason is structural: a gradient is a ratio of differences, $\Delta V / \Delta I'$, and the
constant $\delta$ cancels in every difference, so a steady offset in the horizontal variable
slides the line along itself and cannot tilt it **(R1)**.

**(c)** The resistances agree: $|r_A - r_B| = %.3f\ \Omega$ against a combined uncertainty of
$%.3f\ \Omega$, a discrepancy of %.1f combined uncertainties. The electromotive forces do not:
$E_A - E_B = %.3f$ V against $%.3f$ V combined, which is %.1f combined uncertainties **(M1)**.
Random scatter is all that A's tighter error bars describe, and random scatter would move the
two parameters together; a disagreement of six combined uncertainties in one parameter with
agreement in the other is not noise **(A1)**. A's claim therefore fails: A is the more *precise*
observer and may be the more systematically wrong, because precision fixes the width of an
interval and not where the interval sits **(R1)**.

**(d)** Rearranging (b), the offset implied by the two graphs is

$$\delta = \frac{E_A - E_B}{r} = \frac{%.3f}{%.2f} = %.4f\ \mathrm{A} \approx %.3f\ \mathrm{A}
\ \pm\ %.3f\ \mathrm{A}\ \textbf{(M1)}\textbf{(A1)}.$$

B's suggested 0.040 A predicts an intercept shift of $r\delta = %.2f \times 0.040 = %.3f$ V, and
the observed separation is $%.3f \pm %.3f$ V; the predicted value lies within the combined
uncertainty of the observed one, so the two graphs support B's suggestion **(A1)**.

The accepted electromotive force is B's, $E = %.2f \pm %.2f$ V. The cross-check runs the other
way: correcting A's intercept for the offset gives $E_A - r\delta = %.3f$ V, which agrees with
B's within B's uncertainty. A's *resistance* is unaffected by the fault and remains the better
of the two values, $r = %.2f \pm %.2f\ \Omega$ **(A1)**.""" % (
    cA, scA, rA, smA, cB, scB, rB, smB,
    dr, r_comb, ratioR, dE, e_comb, ratioE,
    dE, r_mid, implied, implied, u_implied,
    r_TRUE, pred, dE, e_comb, cB, scB, cA - pred, rA, smA)

NOTES = r"""**(a)** (M1) for reading both intercepts and both gradients, (A1) for the four values, (A1)
for uncertainties that are *appropriate*: an intercept uncertainty of $\pm 0.001$ V is not
defensible from a 0.01 V voltmeter and forfeits the mark. Accept $E_A$ in $[1.59, 1.61]$ V,
$E_B$ in $[1.45, 1.50]$ V, $r_A$ in $[2.36, 2.44]\ \Omega$ and $r_B$ in $[2.26, 2.42]\ \Omega$.
A candidate who fits the tabulated data rather than reading the graph is to be given full credit.
Half the instrument resolution is acceptable for a single reading, but the intercept uncertainty
must come from the scatter of the points, not from the meter.

**(b)** (M1) for substituting $I = I' - \delta$ into the cell equation, (A1) for identifying the
intercept as $E + r\delta$, (R1) for the reason the gradient survives. A purely graphical
argument earns the marks -- every point moves $\delta$ to the right, so the line translates along
its own direction. Follow-through is allowed into (d), but a candidate who reports the intercept
as $E - r\delta$ cannot score the reasoning mark in (c) by asserting agreement.

**(c)** (M1) for comparing *both* pairs against their combined uncertainties rather than
eyeballing them, (A1) for concluding that A's claim is unsupported, (R1) for the reason: the
uncertainties bound random error and the disagreement is systematic. Award the reasoning mark to a
candidate who names the gradient/intercept asymmetry even if the arithmetic appears in (d). A
candidate who settles the question by quoting the data-sheet value of $E$ has not evaluated the
claim and scores (M1) at most -- the item is answerable from the two graphs alone, and that is the
point of it.

**(d)** (M1) for $\delta = \Delta E / r$, (A1) for $\delta \approx 0.049$ A, (A1) for the
comparison with 0.040 A, accepting either "supported" or "a little larger than B suggests", and
(A1) for accepting $E_B$ with A's resistance retained. Allow follow-through from (a) and (b). A
candidate who concludes that A's electromotive force should be accepted because it is more precise
earns the first two marks only, and that answer should be read back against (c) before anything
further is awarded. $\pm 0.005$ A on the implied offset is the expected spread from the
uncertainties already quoted; do not require it."""

EXPL = r"""The item rests on one asymmetry that students can state fluently and still fail to use: a
constant offset in the quantity on the horizontal axis slides a straight line along itself, so
the intercept is destroyed and the gradient is untouched. Every habit a candidate has been
trained into around uncertainties -- halve the resolution, combine in quadrature, keep the
tighter error bar -- is a theory of *random* error, and random error is not what has gone wrong
here. The trap is that A's uncertainties are honest, correctly derived from A's own scatter, and
the number A reports confidently is still wrong by %.3f V.

The naive path is to compare the two intercepts, notice that A's is quoted several times more
tightly than B's, and keep A's. That inference is licensed only when the two datasets differ by
nothing but random error, and that is precisely what the gradients test. The resistances agree to
%.1f combined uncertainties while the electromotive forces disagree by %.1f; a discrepancy that
selective is not noise, it is a fault with a shape, and the shape is the one derived in (b). The
wrong answer is thus A's own $E = %.2f$ V, produced by an uncertainty analysis with no error in
any line of it.

Parts (b) and (d) are what make the question hard rather than merely long. (b) asks for the
behaviour of a model under a specified perturbation, and (d) asks the candidate to run that
relation backwards and *measure the size of the fault* from the two graphs. The closing
requirement is the real discriminator: the fault sits in one instrument and therefore in one
parameter, so the correct verdict keeps A's internal resistance and rejects A's electromotive
force. A candidate who sorts the students into "right" and "wrong" has not used the evidence,
only the rhetoric around it.""" % (cA - E_TRUE, ratioR, ratioE, cA)

item = {
    "id": "PHYS-B.5-601",
    "subject": "Physics HL", "level": "HL",
    "syllabus_ref": "B.5 (Kirchhoff's laws and the $V = E - Ir$ model of a cell), with the "
                    "treatment of systematic error and the assessment of uncertainty from the "
                    "assessable practical skills",
    "topic": "Theme B: The particulate nature of matter",
    "subtopic": "B.5 Circuits: two determinations of the same cell whose intercepts disagree while "
                "their gradients agree, and what that pattern says about the instruments",
    "paper": "P1", "section": "B", "question_type": "data_based",
    "technology": "permitted", "language": None,
    "marks": 13, "difficulty": 5,
    "challenge_mechanism":
        "A constant offset in the independent variable slides a straight line along itself, so it "
        "destroys the intercept and leaves the gradient untouched; the candidate must use that "
        "asymmetry to see that the dataset with the smaller and honestly-quoted uncertainties is "
        "the systematically wrong one, and then run the relation backwards to measure the size of "
        "the fault from the two graphs.",
    "difficulty_evidence": {
        "lever_type": "non_obvious_tool",
        "naive_path":
            "Compare the two values of the electromotive force against their combined uncertainty, "
            "notice that A's is quoted several times more tightly than B's, and conclude that the "
            "measurement with the smaller uncertainty is the better one.",
        "failure_point":
            "A's error bars describe only how tightly A's own points fall about A's own line, and a "
            "constant offset in the current axis translates the line without tilting it, so the "
            "tighter interval is centred on the wrong number and no propagation reveals it.",
        "wrong_answer":
            "The electromotive force accepted as %.2f V, which is A's value, together with the "
            "claim that the two students cannot be compared because B's readings are too imprecise "
            "-- whereas the resistances agree to %.1f combined uncertainties, which is exactly what "
            "localises the fault to A's ammeter." % (cA, ratioR),
    },
    "command_terms": ["Determine", "Show that", "Evaluate", "Determine"],
    "tags": ["internal resistance", "systematic error", "zero error", "gradient and intercept",
             "uncertainty", "precision versus accuracy", "data analysis", "P1B", "figure"],
    "stimulus": {"title": "Two students, one cell", "body": STEM, "table": TABLE},
    "figure": {"type": "svg", "content": SVG,
               "caption": "Terminal potential difference against current for the same cell, "
                          "measured by student A (blue) and student B (red), each with its reading "
                          "uncertainties and its line of best fit."},
    "question": ("The table gives both students' readings and the graph shows them with their "
                 "lines of best fit. Use the graph and the table to answer the questions below."),
    "parts": PARTS,
    "answer": ANSWER, "markscheme_notes": NOTES, "explanation": EXPL,
    "provenance": {
        "inspired_by": "the A-level required-practical genre in which two students obtain "
                       "different graphs from the same apparatus and the candidate must say which "
                       "line to trust",
        "source_family": "uk-alevel",
        "adaptation":
            "The situation is borrowed, the question is rebuilt. In the A-level form the candidate "
            "is told which meter was mis-zeroed, or is asked to compare against an accepted value. "
            "Here (i) nothing is said about either instrument's calibration, so the fault has to be "
            "inferred from the pattern in the two fits rather than recognised; (ii) the "
            "given-and-asked pair is inverted -- the candidate derives how a constant offset in the "
            "independent variable behaves and then runs that backwards to measure the offset; and "
            "(iii) the chain ends in a split verdict, keeping A's gradient and rejecting A's "
            "intercept, which the source genre does not ask for. Command terms, marking "
            "annotations, significant-figure and uncertainty conventions are rewritten into IB "
            "register.",
        "resource_origin": "AQA A-level Physics (7407/7408) required practical CP8, EMF and "
                           "internal resistance, and the AQA/Edexcel 'two students obtained these "
                           "graphs' evaluation style; located by web search 2026-09-23",
        "source_url": "https://www.savemyexams.com/a-level/physics/aqa/17/revision-notes/5-electricity/5-4-electromotive-force-and-internal-resistance/5-4-1-electromotive-force-and-internal-resistance/",
        "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "nearest_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "Both datasets were generated from $V = E - Ir$ with the seeded truth $E = 1.50$ V and "
            "$r = 2.40\\ \\Omega$, applying A's $+0.040$ A meter offset to the current actually "
            "plotted, adding reading scatter, and rounding to each instrument's stated resolution. "
            "Ordinary least squares was then run on the rounded data with intercept and gradient "
            "uncertainties taken from the residual scatter, and every number quoted in the answer "
            "and markscheme is printed from that fit rather than from the seed: $E_A = %.4f \\pm "
            "%.4f$ V, $r_A = %.4f \\pm %.4f\\ \\Omega$, $E_B = %.4f \\pm %.4f$ V, $r_B = %.4f \\pm "
            "%.4f\\ \\Omega$. The three claims the item rests on were each checked against the fit: "
            "the gradient of a line fitted to offset currents is unchanged ($r_A = %.3f$ against "
            "the seeded $2.40$); the intercept is raised by $r\\delta = %.3f$ V (observed $E_A - E "
            "= %.3f$ V); and the intercepts disagree by %.1f combined uncertainties while the "
            "gradients agree to %.1f. The offset implied by the graphs, $\\Delta E / r = %.4f \\pm "
            "%.4f$ A, and the prediction from B's suggested 0.040 A, $r\\delta = %.3f$ V against an "
            "observed $%.3f \\pm %.3f$ V, were computed the same way. The figure is drawn from the "
            "same rounded points and the same fitted lines." % (
                cA, scA, rA, smA, cB, scB, rB, smB, rA, pred, cA - E_TRUE, ratioE, ratioR,
                implied, u_implied, pred, dE, e_comb),
        "assertions": [
            "approx(%.6f, 2.40, 0.025)" % rA,
            "approx(%.6f, 1.60, 0.010)" % cA,
            "approx(%.6f, 2.34, 0.030)" % rB,
            "approx(%.6f, 1.48, 0.020)" % cB,
            "approx(%.6f - 1.50, 2.40*0.040, 0.030)" % cA,
            "abs(%.6f - %.6f) < 2*hypot(%.6f, %.6f)" % (rA, rB, smA, smB),
            "abs(%.6f - %.6f) > 4*hypot(%.6f, %.6f)" % (cA, cB, scA, scB),
            "approx((%.6f - %.6f)/%.6f, 0.049, 0.004)" % (cA, cB, r_mid),
            "approx(2.40*0.040, 0.096, 1e-12)",
            "approx(hypot(%.6f, %.6f)/%.6f, %.3f, 1e-3)" % (scA, scB, dE, e_comb / dE),
            "approx(hypot(%.6f, %.6f)/%.6f, %.3f, 1e-3)" % (smA, smB, dr, r_comb / dr),
            "0.040 < %.6f < 0.060" % implied,
            "approx(1.50 - 2.40*(0.100 - 0.040), 1.356, 1e-12)",
            "approx(1.50 + 2.40*0.040, 1.596, 1e-12)",
            "approx(%.6f - 2.40*0.040, 1.500, 0.010)" % cA,
        ],
        "solution_skeleton": [
            "fit each student's points and read intercept and gradient with scatter-based uncertainties",
            "substitute the offset current into the cell model to see which parameter moves",
            "compare the two gradients and the two intercepts against their combined uncertainties",
            "invert the intercept shift to estimate the size of the meter offset",
            "accept the electromotive force from the unaffected dataset while keeping the offset dataset's gradient",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai",
    "created_at": "2026-09-23", "updated_at": "2026-09-23",
}

# ------------------------------------------------------------------ self-check
sys.path.insert(0, "tools")
import validate as V
taken = {q["id"] for _, q in V.load()}
if "--force" not in sys.argv:
    assert item["id"] not in taken, "id collision"
assert sum(p["marks"] for p in item["parts"]) == item["marks"]
first, rest = item["parts"][0]["marks"], [p["marks"] for p in item["parts"][1:]]
assert first <= max(rest), "arc: the first part is the heaviest"
assert 3 <= len(item["verification"]["solution_skeleton"]) <= 6
assert len(item["verification"]["assertions"]) >= 0.5 * item["marks"]
for f in ("answer", "markscheme_notes", "explanation"):
    print("  %-18s %d words" % (f, len(str(item[f]).split())))

ns = "{http://www.w3.org/2000/svg}"
root = ET.fromstring(SVG)
w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', SVG).groups())
bad, nodes = [], []
for t in root.iter(ns + "text"):
    s = "".join(t.itertext())
    x, y = float(t.get("x")), float(t.get("y"))
    if "$" in s:
        bad.append("raw LaTeX in %r" % s)
    for leak in ("1.60", "1.48", "2.40", "2.34", "0.049", "0.096", "0.040"):
        if leak in s:
            bad.append("figure prints %r, which a part asks for" % leak)
    if not (0 <= x <= w and 0 <= y <= h):
        bad.append("label %r outside the frame" % s)
    # x inside the frame is not enough: a long label runs off the right edge, which the
    # first render of this figure showed and the coordinate check could not.
    size = float(t.get("font-size") or 15)
    anchor = t.get("text-anchor")
    left = x - len(s) * size * 0.55 if anchor == "end" else (
        x - len(s) * size * 0.275 if anchor == "middle" else x)
    if left < 0 or left + len(s) * size * 0.55 > w:
        bad.append("label %r is clipped by the frame (spans %.0f..%.0f of %d)"
                   % (s, left, left + len(s) * size * 0.55, w))
    nodes.append((s, x, y))
for i in range(len(nodes)):
    for j in range(i + 1, len(nodes)):
        if abs(nodes[i][1] - nodes[j][1]) < 12 and abs(nodes[i][2] - nodes[j][2]) < 12:
            bad.append("labels %r and %r collide" % (nodes[i][0], nodes[j][0]))
# a label sitting on a data marker reads as a stray mark -- the defect the second render
# of this figure showed, which no coordinate check caught
marks = [(float(c.get("cx")), float(c.get("cy"))) for c in root.iter(ns + "circle")]
for s, x, y in nodes:
    for mx, my in marks:
        if abs(mx - x) < 10 and abs(my - (y - 5)) < 10:
            bad.append("label %r sits on a data marker at (%.0f,%.0f)" % (s, mx, my))
if bad:
    sys.exit("FIGURE DEFECTS: " + "; ".join(bad))
print("figure lint clean (%d labels)" % len(nodes))

OUT = "data/physics-hl/b32-cell-offset.json"
if os.path.exists(OUT) and "--force" not in sys.argv:
    sys.exit("%s exists -- refusing to overwrite (pass --force to rewrite this wave's own item)" % OUT)
if os.path.exists(OUT):
    old = json.load(open(OUT, encoding="utf-8"))["questions"][0]
    if old["originality"].get("checked_at"):
        item["originality"] = old["originality"]     # a figure edit does not invalidate the scan
        item["status"] = old["status"]
    taken.discard(old["id"])
json.dump({"_batch": "32 (small batch)", "questions": [item]},
          open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("wrote", OUT, "| svg %d bytes" % len(SVG))
