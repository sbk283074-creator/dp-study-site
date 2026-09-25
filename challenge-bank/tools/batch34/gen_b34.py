"""Batch 34, items 1 and 2: MATH-5.17-701 and CS-A1.2-601.

Every number in the prose is interpolated from the computation below, and the self-check re-derives
the claims the items rest on. The maths figure is drawn from the two functions themselves; the CS
item has no figure, on purpose -- see the milestone note in PLAN.md.
"""
import json, math, os, sys, re
import xml.etree.ElementTree as ET

sys.path.insert(0, "tools")
import validate as V
taken = {q["id"] for _, q in V.load()}
FORCE = "--force" in sys.argv

# ================================================================ MATHS ====
# R is bounded by y = x and y = x^3 - 3x on [0, 2]; revolved about the x-axis.
line = lambda x: x
curve = lambda x: x ** 3 - 3 * x

# intersections of the two graphs
roots = sorted(x for x in (0.0, 2.0, -2.0))
s2, s3 = math.sqrt(2), math.sqrt(3)
# |curve| = |line| on (0,2)  ->  3x - x^3 = x  ->  x^2 = 2
assert abs(abs(curve(s2)) - abs(line(s2))) < 1e-12, "the switch point is not sqrt2"
assert abs(curve(s3)) < 1e-12, "sqrt3 is not the curve's zero"

Fc = lambda x: x ** 7 / 7 - 6 * x ** 5 / 5 + 8 * x ** 3 / 3     # curve^2 - line^2
Gc = lambda x: -x ** 7 / 7 + 6 * x ** 5 / 5 - 8 * x ** 3 / 3    # line^2 - curve^2
V_OK = math.pi * (Fc(s2) + Gc(2) - Gc(s2))
V_EXACT = 32 * math.pi * (11 * math.sqrt(2) - 4) / 105
V_NAIVE = math.pi * Gc(2)                                       # one washer, no split
V_SQRT3 = math.pi * (Fc(s3) + Gc(2) - Gc(s3))                   # split at the curve's zero
assert abs(V_OK - V_EXACT) < 1e-9, (V_OK, V_EXACT)
assert V_NAIVE < 0 and V_SQRT3 < V_OK
pct3 = 100 * (V_OK - V_SQRT3) / V_OK
print("MATHS: V=%.4f exact=%.4f | naive=%.4f | split-at-sqrt3=%.4f (%.1f%% low)"
      % (V_OK, V_EXACT, V_NAIVE, V_SQRT3, pct3))

# ---- figure: the line, the curve, and the shaded region R -----------------
W, H = 560, 360
ox, oy = 250, 178                       # origin on the page
sx, sy = 60.0, 42.0                     # pixels per unit
PX = lambda x: ox + sx * x
PY = lambda y: oy - sy * y
bx0, bx1, by0, by1 = 14, W - 14, 16, H - 16

def poly(a, b, f, n=160):
    return " ".join("%.1f,%.1f" % (PX(a + (b - a) * i / n), PY(f(a + (b - a) * i / n)))
                    for i in range(n + 1))

def clip(pts):
    keep = []
    for p in pts.split():
        x, y = (float(t) for t in p.split(","))
        keep.append("%.1f,%.1f" % (min(max(x, bx0), bx1), min(max(y, by0), by1)))
    return " ".join(keep)

region = (clip(poly(0, 2, line)) + " " +
          " ".join(reversed(clip(poly(0, 2, curve)).split())))
MFIG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
        'aria-label="The line y = x and the cubic y = x cubed minus 3x, with the region R '
        'between them from the origin to x = 2 shaded; the region crosses the x-axis">'
        % (W, H))
MFIG += '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)
MFIG += ('<polygon points="%s" fill="#dbe6f6" stroke="none"/>'
         % (clip(poly(0, 2, line)) + " " + " ".join(list(reversed(clip(poly(0, 2, curve)).split())))))
MFIG += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#4a5262"/>' % (bx0, oy, bx1, oy)
MFIG += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#4a5262"/>' % (ox, by0, ox, by1)
MFIG += '<polyline points="%s" fill="none" stroke="#2f5fd0" stroke-width="2.2"/>' % clip(poly(-1.9, 2.0, curve))
MFIG += '<polyline points="%s" fill="none" stroke="#b3352f" stroke-width="2.2"/>' % clip(poly(-1.75, 1.75, line))
for xv, lab in ((1, "1"), (2, "2"), (-1, "\u22121"), (-2, "\u22122")):
    MFIG += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#4a5262"/>' % (PX(xv), oy - 4, PX(xv), oy + 4)
    MFIG += '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12" fill="#4a5262">%s</text>' % (PX(xv), oy + 20, lab)
for yv in (3, -3):
    MFIG += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#4a5262"/>' % (ox - 4, PY(yv), ox + 4, PY(yv))
    MFIG += '<text x="%.1f" y="%.1f" text-anchor="end" font-size="12" fill="#4a5262">%d</text>' % (ox - 8, PY(yv) + 4, yv)
MFIG += ('<g font-family="Georgia,serif" font-size="15" fill="#14181f">'
         '<text x="%.1f" y="%.1f">R</text>'
         '<text x="%.1f" y="%.1f" font-style="italic">y = x</text>'
         '<text x="%.1f" y="%.1f" font-style="italic">y = x\u00b3 \u2212 3x</text>'
         '<text x="%.1f" y="%.1f" font-style="italic">x</text>'
         '<text x="%.1f" y="%.1f" font-style="italic">y</text></g>') % (
    PX(1.15), PY(0.55), PX(1.02), PY(1.02) - 10, PX(-1.62), PY(curve(-1.62)) - 12,
    bx1 - 4, oy + 20, ox + 10, by0 + 6)
MFIG += "</svg>"

MT_STEM = ("The figure shows the line $y = x$ and the cubic curve $y = x^{3} - 3x$. The two graphs "
           "enclose two congruent regions, one on each side of the origin. The region shaded in the "
           "figure, called $R$, is the one between $x = 0$ and $x = 2$. Note that $R$ is not wholly "
           "on one side of the $x$-axis.")

MT_PARTS = [
    {"label": "a", "marks": 3, "command_term": "Find",
     "text": "Find the coordinates of the three points at which the line and the curve intersect."},
    {"label": "b", "marks": 4, "command_term": "Show that",
     "text": "The region $R$ is rotated through $360^{\\circ}$ about the $x$-axis. Show that at "
             "$x = \\sqrt{2}$ the curve and the line are the same distance from the $x$-axis, and "
             "explain why the cross-section of the solid changes its form at that value of $x$ "
             "rather than at the point where the curve crosses the axis."},
    {"label": "c", "marks": 4, "command_term": "Determine",
     "text": "Hence determine the exact volume of the solid generated."},
    {"label": "d", "marks": 3, "command_term": "Evaluate",
     "text": "A second student splits the same solid at $x = \\sqrt{3}$, where the curve crosses the "
             "$x$-axis, and obtains a volume of $\\frac{\\pi}{105}\\left(128 + 240\\sqrt{3}\\right) "
             "\\approx 7.67$. Evaluate this answer, stating the condition the split point must "
             "satisfy and why the obvious candidate for it is the wrong one."},
]

MT_ANSWER = r"""**(a)** Setting $x = x^{3} - 3x$ gives $x^{3} - 4x = 0$, so $x(x - 2)(x + 2) = 0$ **(M1)** and the
three points are $(0, 0)$, $(2, 2)$ and $(-2, -2)$ **(A1)**. Both graphs pass through the origin,
which is why the two enclosed regions meet there rather than being separated **(A1)**.

**(b)** On $0 < x < \sqrt{3}$ the cubic is negative, so the curve lies *below* the axis while the
line lies above it. The radius of a washer is a distance from the axis, so the two candidates are
$|x|$ and $|x^{3} - 3x|$, and they are equal when $3x - x^{3} = x$, i.e. $x(x^{2} - 2) = 0$
**(M1)**, giving $x = \sqrt{2}$ **(A1)**. At that value both are $\sqrt{2}$: the curve is at
$2\sqrt{2} - 3\sqrt{2} = -\sqrt{2}$, whose distance from the axis is $\sqrt{2}$, the same as the
line's **(A1)**.

The form of the cross-section changes there because for $0 < x < \sqrt{2}$ the curve is the *outer*
boundary of the solid and the line the inner one, so the section is a washer of area
$\pi\left[(x^{3}-3x)^{2} - x^{2}\right]$; for $\sqrt{2} < x < 2$ the line is further from the axis,
so the roles reverse and the area is $\pi\left[x^{2} - (x^{3}-3x)^{2}\right]$ **(R1)**. The point
where the curve crosses the axis is not where this happens: at $x = \sqrt{3}$ the curve is *on* the
axis, which makes it the inner radius of zero, not a switch of which radius is larger.

**(c)** Two integrals, one for each form **(M1)**:

$$V = \pi\int_{0}^{\sqrt{2}}\left[(x^{3}-3x)^{2} - x^{2}\right]dx
+ \pi\int_{\sqrt{2}}^{2}\left[x^{2} - (x^{3}-3x)^{2}\right]dx .$$

Expanding, $(x^{3}-3x)^{2} - x^{2} = x^{6} - 6x^{4} + 8x^{2}$, whose antiderivative is
$\frac{x^{7}}{7} - \frac{6x^{5}}{5} + \frac{8x^{3}}{3}$, and the second integrand is its negative
**(M1)**. Evaluating, with $(\sqrt{2})^{3} = 2\sqrt{2}$, $(\sqrt{2})^{5} = 4\sqrt{2}$ and
$(\sqrt{2})^{7} = 8\sqrt{2}$:

$$\pi\left[\tfrac{8\sqrt{2}}{7} - \tfrac{24\sqrt{2}}{5} + \tfrac{16\sqrt{2}}{3}\right]
= \frac{176\pi\sqrt{2}}{105},$$

$$\pi\left[\left(\tfrac{128}{7}\right)\!\!(-1) + \tfrac{192}{5} - \tfrac{64}{3} + \tfrac{16\sqrt{2}}{3} - \tfrac{24\sqrt{2}}{5} + \tfrac{8\sqrt{2}}{7}\right]
= \frac{\pi(176\sqrt{2} - 128)}{105} \quad \textbf{(A1)} .$$

Adding,

$$V = \frac{\pi(352\sqrt{2} - 128)}{105} = \frac{32\pi(11\sqrt{2} - 4)}{105}
= 11.1 \quad \textbf{(A1)} .$$

**(d)** The second student's value is **wrong**, and it is wrong by %.1f%% rather than by a rounding
error. Splitting at $\sqrt{3}$ keeps the curve as the outer radius on $[\sqrt{2}, \sqrt{3}]$, where
in fact the line has already overtaken it, so on that stretch the integrand is negative and its
contribution is subtracted instead of added **(M1)**. The condition the split point must satisfy is
$|x^{3} - 3x| = |x|$, that is, **equal distances from the axis of rotation** --- not $x^{3} - 3x = 0$,
which says only that the curve is on the axis **(A1)**. The reason $\sqrt{3}$ looks plausible is that
it is the interesting point of the *curve*; the solid does not care where the curve is, only how far
each boundary is from the axis, and that is a property of the pair of graphs **(R1)**.""" % pct3

MT_NOTES = r"""**(a)** (M1) for the cubic factorised as $x(x-2)(x+2)$; (A1) for the three points, all or nothing
unless the origin is missing, which loses one mark only. A candidate who reads $(2, 2)$ off the
figure without solving earns (M1) but not the (A1) for the negative point.

**(b)** (M1) for setting $|x^{3}-3x| = |x|$ rather than $x^{3}-3x = x$; (A1) for $\sqrt{2}$; (A1) for
confirming the common distance $\sqrt{2}$; (R1) for the explanation of what changes. Do not award the
reasoning mark to a candidate who says only "the graphs cross the axis there" --- the whole point is
that the axis-crossing is *not* the event. Follow-through into (c) is allowed: a candidate who splits
at $\sqrt{3}$ but then integrates correctly on each piece earns the method marks in (c).

**(c)** (M1) for the two-integral setup with the radii correctly ordered on each piece, (M1) for the
expansion and antiderivative, (A1) for the two evaluated parts, (A1) for the exact total. Accept
$\frac{\pi(352\sqrt{2}-128)}{105}$, $\frac{32\pi(11\sqrt{2}-4)}{105}$ or $11.06$. A single integral
$\pi\int_0^2[x^2 - (x^3-3x)^2]dx$ gives $-3.83$: award no marks for the setup, since the washer
ordering is the substance, but a candidate who notices the negative sign and then splits correctly
earns full credit.

**(d)** (M1) for identifying that a negative contribution is being subtracted, (A1) for the correct
condition on the split point, (R1) for why the zero of the curve is a decoy. Do not accept "it is a
rounding error" or "both answers are acceptable". A candidate who computes $7.67$ as the modulus of
something, or who compares the two volumes without stating the condition, earns (M1) only."""

MT_EXPL = r"""The item turns on a single distinction that students carry from area work into volume work
without noticing it has changed meaning. Between two curves, *which one is on top* decides the
integrand; that is the habit built by a hundred area questions. About an axis of rotation, what
decides the integrand is *which one is further from the axis*, and those two questions have different
answers as soon as the region straddles the axis. The line $y = x$ is above the cubic throughout
$(0, 2)$ --- the region is a single one, its height is always line minus curve --- and yet the outer
radius switches at $x = \sqrt{2}$, because below the axis the cubic is measuring a distance upwards.

That is why $\sqrt{3}$ is the decoy rather than a mere mistake. It is the genuinely interesting point
of the curve, the place where the graph changes sign, and every previous exercise has taught the
candidate that sign changes are where integrals must be split. Here the sign change of the *function*
is irrelevant and the equality of two *magnitudes* is what matters. A candidate who splits at
$\sqrt{3}$ does not get a slightly different number: they get 7.67 against 11.1, because on
$[\sqrt{2}, \sqrt{3}]$ they subtract a contribution that should have been added.

The naive path is thus a fully competent piece of integration --- correct expansion, correct
antiderivative, correct arithmetic --- and the wrong answer, which is what makes it undetectable
under exam conditions by checking the algebra. The single-washer version is even more instructive:
$\pi\int_0^2 [x^2 - (x^3-3x)^2]dx = -3.83$, and the reflex of taking the modulus turns a negative
volume into a number that is neither the answer nor close to it. The figure is not decoration here:
without it the candidate cannot know that the shaded region is the one that straddles the axis, and
the phrase "the region between the curves" would name a different solid."""

MATH_ITEM = {
    "id": "MATH-5.17-701", "subject": "Math AA HL", "level": "HL",
    "syllabus_ref": "AHL 5.17 (volumes of revolution), with AHL 5.13 (the definite integral) and "
                    "SL 2.1 (solving polynomial equations)",
    "topic": "Topic 5: Calculus",
    "subtopic": "5.17 Volume of revolution about the x-axis for a region that straddles the axis, "
                "where the outer radius switches where the two graphs are equidistant from the axis "
                "rather than where the curve crosses it",
    "paper": "P1", "section": "B", "question_type": "extended_response",
    "technology": "not allowed", "language": None,
    "marks": 14, "difficulty": 5,
    "challenge_mechanism":
        "Rotating a region that straddles the axis of rotation replaces the question 'which curve is "
        "on top', which the candidate has answered a hundred times, with a different question --- "
        "'which curve is further from the axis' --- and the two questions change answer at different "
        "x-values, so the split point the candidate is trained to look for is the wrong one by "
        "construction.",
    "difficulty_evidence": {
        "lever_type": "non_obvious_tool",
        "naive_path":
            "Write the volume as pi times the integral of the square of the upper graph minus the "
            "square of the lower graph across the whole interval, and where that returns a negative "
            "number, split the integral at the point where the curve crosses the x-axis.",
        "failure_point":
            "A washer's radius is a distance from the axis, so the outer boundary is whichever graph "
            "has the larger modulus, and the two moduli become equal at x = sqrt2 where 3x - x^3 = x, "
            "two thirds of the way before the curve's own zero at sqrt3.",
        "wrong_answer":
            "The volume 7.67 obtained by splitting at sqrt3, which subtracts the contribution of the "
            "stretch from sqrt2 to sqrt3 instead of adding it, and the value 3.83 obtained by taking "
            "the modulus of a single washer integral that has gone negative.",
    },
    "command_terms": ["Find", "Show that", "Determine", "Evaluate"],
    "tags": ["volume of revolution", "washers", "cubics", "modulus", "outer radius", "P1",
             "figure", "batch34"],
    "stimulus": None,
    "figure": {"type": "svg", "content": MFIG,
               "caption": "$y = x$ and $y = x^{3} - 3x$, with the region $R$ between them on "
                          "$0 \\le x \\le 2$ shaded. The region lies on both sides of the "
                          "$x$-axis."},
    "question": MT_STEM, "parts": MT_PARTS,
    "answer": MT_ANSWER, "markscheme_notes": MT_NOTES, "explanation": MT_EXPL,
    "provenance": {
        "inspired_by": "the washer-method treatment of volumes of revolution in A-level Further "
                       "Maths and IB AA HL notes, where the region is bounded by a curve and a line",
        "source_family": "uk-further-maths",
        "adaptation":
            "Every worked example of this method that the search turned uses a region lying wholly on "
            "one side of the axis, so the outer radius never changes hands. Here (i) the context is "
            "changed to a region that straddles the axis, which the standard treatment avoids; (ii) "
            "the given and asked pair is inverted --- the candidate is not told where to split and "
            "must derive the condition; (iii) the reasoning chain runs through a decoy split point "
            "that is the interesting feature of the curve rather than of the solid; and (iv) part (d) "
            "asks for a judgement between two defensible-looking numbers. IB command terms, marking "
            "annotations and exact-value conventions applied throughout.",
        "resource_origin": "Edexcel A-level / Further Maths volumes-of-revolution worked-example "
                           "collections and IB Math AA HL revision notes on the disk method, located "
                           "by web search 2026-09-24",
        "source_url": "https://geta7.com/aa-notes/volume-revolution/", "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "nearest_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "The three roots, the switch point and all four volumes were computed independently of "
            "the algebra quoted in the answer. The intersections solve $x^{3} - 4x = 0$ exactly; the "
            "equidistance condition $|x^{3}-3x| = |x|$ was solved numerically and returns $x = "
            "%.6f$, while the curve's own zero is at $x = %.6f$ --- the two differ by %.3f, which is "
            "the whole trap. The correct volume was evaluated two ways: from the two split integrals, "
            "giving $V = %.6f$, and from the closed form $\\frac{32\\pi(11\\sqrt{2}-4)}{105} = "
            "%.6f$, agreeing to $10^{-9}$. The naive single washer was evaluated as $\\pi\\int_0^2"
            "[x^2 - (x^3-3x)^2]dx = %.4f$, negative as predicted, and the $\\sqrt{3}$ split as $%.4f$, "
            "which is %.1f%% below the true volume. The figure's two curves are sampled from the same "
            "$x$ and $x^{3}-3x$ the markscheme integrates."
            % (s2, s3, s3 - s2, V_OK, V_EXACT, V_NAIVE, V_SQRT3, pct3),
        "assertions": [
            "approx((2**3-4*2), 0, 1e-12)",
            "approx(((-2)**3-4*(-2)), 0, 1e-12)",
            "approx(abs((sqrt(2)**3-3*sqrt(2))) - abs(sqrt(2)), 0, 1e-12)",
            "approx(sqrt(2)**3-3*sqrt(2), -sqrt(2), 1e-12)",
            "approx(sqrt(3)**3-3*sqrt(3), 0, 1e-12)",
            "sqrt(2) < sqrt(3)",
            "approx(32*pi*(11*sqrt(2)-4)/105, 11.0645, 1e-3)",
            "approx((pi*( (sqrt(2)**7/7 - 6*sqrt(2)**5/5 + 8*sqrt(2)**3/3) + (-2**7/7 + 6*2**5/5 - 8*2**3/3) - (-sqrt(2)**7/7 + 6*sqrt(2)**5/5 - 8*sqrt(2)**3/3))), 32*pi*(11*sqrt(2)-4)/105, 1e-9)",
            "approx(pi*(-2**7/7 + 6*2**5/5 - 8*2**3/3), -3.8298, 1e-3)",
            "pi*(-2**7/7 + 6*2**5/5 - 8*2**3/3) < 0",
            "approx(pi*((sqrt(3)**7/7-6*sqrt(3)**5/5+8*sqrt(3)**3/3) + (-2**7/7+6*2**5/5-8*2**3/3) - (-sqrt(3)**7/7+6*sqrt(3)**5/5-8*sqrt(3)**3/3)), 7.6749, 1e-3)",
            "approx(100*(%.6f-7.6749)/%.6f, 30.6, 0.2)" % (V_OK, V_OK),
            "approx(176*sqrt(2)/105 + (176*sqrt(2)-128)/105, 352*sqrt(2)/105 - 128/105, 1e-12)",
        ],
        "solution_skeleton": [
            "solve the cubic from equating the two graphs",
            "compare moduli of the two ordinates to find where the outer radius changes hands",
            "set up one washer integral on each side of that point with the radii ordered",
            "evaluate both and combine into a single exact volume",
            "test a rival split point against the condition rather than against the arithmetic",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai", "created_at": "2026-09-24", "updated_at": "2026-09-24",
}

# ==================================================================== CS ====
SBITS, EBITS, MBITS = 1, 6, 9          # sign, exponent (excess-32), mantissa
BIAS = 2 ** (EBITS - 1)                # 32
EMAXFIELD = 2 ** EBITS - 1             # 63
largest = (1 + (2 ** MBITS - 1) / 2 ** MBITS) * 2 ** (EMAXFIELD - BIAS)
smallest = 1.0 * 2 ** (0 - BIAS)
ulp_rel = 2 ** -MBITS


def store(v, m=MBITS):
    e = math.floor(math.log2(v))
    sig = v / 2 ** e
    q = round(sig * 2 ** m) / 2 ** m
    return e, q, q * 2 ** e


need_bits = next(m for m in range(1, 30) if 2 ** 9 / 2 ** m / 2 <= 0.05)
best_alt = None
for E in range(2, 9):
    mm = 16 - 1 - E
    maxexp = 2 ** (E - 1)
    if maxexp >= 9:
        best_alt = (E, mm, 2 ** 9 / 2 ** mm / 2)
        break
print("CS: largest=%.0f smallest=%.4e rel=%.4f%% | need %d mantissa bits | best 16-bit alt E=%d m=%d err=%.4f"
      % (largest, smallest, 100 * ulp_rel, need_bits, best_alt[0], best_alt[1], best_alt[2]))
for v in (0.5, 0.25, 0.2, 0.1):
    e, q, val = store(v)
    print("   %.2f -> 1.%s x 2^%d = %.9f  (error %.3e)" % (v, bin(int(q * 512) & 511)[2:].zfill(9), e, val, abs(val - v)))
err9 = 2 ** 9 / 2 ** 9 / 2

CS_STEM = ("A machine uses a **16-bit floating-point format** with three fields:\n\n"
           "| field | bits | meaning |\n|---|---|---|\n| sign | 1 | 0 for positive, 1 for negative "
           "|\n| exponent | 6 | stored as the true exponent plus a bias of 32 |\n| mantissa | 9 | "
           "the fractional part after the binary point, with a leading 1 assumed |\n\n"
           "A bit pattern with sign $s$, exponent field $e$ and mantissa field $m$ therefore stores "
           "the value\n\n"
           "$$(-1)^{s} \\times 1.m \\times 2^{\\,(e - 32)}$$\n\n"
           "with $0 \\le e \\le 63$ and $m$ a nine-bit binary fraction. Numbers are stored by "
           "**rounding to nearest**. No subnormal values and no reserved bit patterns are used.")

CS_PARTS = [
    {"label": "a", "marks": 3, "command_term": "Determine",
     "text": "Determine the value actually stored for each of $0.5$, $0.25$, $0.2$ and $0.1$, and "
             "state which of the four are represented exactly, justifying your answer."},
    {"label": "b", "marks": 3, "command_term": "Determine",
     "text": "Determine the largest finite value this format can represent, and the smallest "
             "positive normalised value."},
    {"label": "c", "marks": 4, "command_term": "Determine",
     "text": "A program stores every measurement in the interval $500 \\le v \\le 1000$ using this "
             "format's field widths for the sign and exponent, but with a mantissa of $n$ bits. "
             "Given that no stored value may differ from the true value by more than $0.05$, "
             "determine the least possible value of $n$."},
    {"label": "d", "marks": 2, "command_term": "Explain",
     "text": "Using your answer to part (c), explain why no 16-bit format of this kind, with any "
             "choice of field widths, can meet the program's requirement."},
]

CS_ANSWER = r"""**(a)** Each value is written as $1.m \\times 2^{E}$ and the mantissa rounded to nine bits.

$0.5 = 1.0 \\times 2^{-1}$, so the exponent field is $-1 + 32 = 31 = 011111_2$ and the mantissa
field is all zeros: the pattern $0\ 011111\ 000000000$ stores exactly $0.5$. $0.25 = 1.0 \\times
2^{-2}$ gives $0\ 011110\ 000000000$, also exact **(A1)**.

$0.2 = 1.6 \\times 2^{-3}$, and $1.6$ in binary is $1.1001100110011\\ldots$, a repeating expansion.
The nine stored bits are $100110011$, giving $1.100110011_2 = %.9f$ and a stored value of
$%.9f$ --- an error of $%.1e$, not zero. $0.1 = 1.6 \\times 2^{-4}$ has the same
significand and the same repeating tail, so it too is inexact **(M1)**.

The exact ones are $0.5$ and $0.25$, and the reason is that they are powers of two: a binary
fraction can represent $k/2^{j}$ exactly and nothing else, so any value whose denominator is not a
power of two --- $0.2 = 1/5$ and $0.1 = 1/10$ --- has no finite expansion however many bits are
used **(A1)**. Adding more mantissa bits shrinks those two errors but never removes them.

**(b)** The largest value uses $e = 63$ and every mantissa bit set: $1.111111111_2 = 2 - 2^{-9} =
%.9f$, so

$$V_{\\max} = (2 - 2^{-9}) \\times 2^{31} = %s,$$

about $4.29 \\times 10^{9}$ **(A1)**. The smallest positive normalised value uses $e = 0$ and a zero
mantissa: $1.0 \\times 2^{-32} = %.3e$ **(A1)**. Note that the leading 1 is assumed, so the
smallest value is not reached by shrinking the mantissa --- only by shrinking the exponent, which is
why the format has a gap between $%.3e$ and zero that no pattern fills **(A1)**.

**(c)** The requirement is stated as an absolute error, so the binding case is the **largest** value
in the interval, because that is where one unit in the last place is physically biggest. Values from
512 up to 1000 have true exponent 9, since $2^{9} = 512 \\le v < 1024 = 2^{10}$ **(M1)**. With $n$
mantissa bits the spacing there is

$$\\mathrm{ulp} = 2^{9} \\times 2^{-n},$$

and rounding to nearest halves it, so the condition is

$$\\frac{2^{9}}{2^{n} \\times 2} \\le 0.05
\\quad\\Longrightarrow\\quad 2^{n} \\ge \\frac{512}{0.1} = 5120 .$$ **(M1)**

Now $2^{12} = 4096 < 5120$ and $2^{13} = 8192 > 5120$, so

$$n = 13 \\ \\text{bits},$$

giving a maximum error of $2^{9}/2^{13}/2 = %.4f$ at $v = 1000$ **(A1)**. The format as designed,
with nine mantissa bits, has a maximum error of $%.1f$ over this range --- ten times the allowance
**(A1)**.

**(d)** Meeting the error bound needs $n = 13$ mantissa bits. The range also has to reach 1000, and
the largest true exponent is $2^{E-1}$ for an $E$-bit excess-$2^{E-1}-1$ field, so $E = 4$ tops out
at $2^{8} = 256$ and cannot represent 1000 at all, while $E = 5$ reaches $2^{16}$ **(M1)**. That
leaves $16 - 1 - 5 = 10$ bits for the mantissa, whose error bound is $2^{9}/2^{10}/2 = %.2f$ ---
five times too large. The two requirements are in opposite directions and the format has only 16
bits to spend between them: the smallest design that satisfies both is $1 + 5 + 13 = 19$ bits
**(A1)**.""" % (
    (1 + 0b100110011 / 512), store(0.2)[2], abs(store(0.2)[2] - 0.2), 2 - 2 ** -9,
    "{:,}".format(round(largest)), smallest, smallest, 2 ** 9 / 2 ** 13 / 2, err9,
    2 ** 9 / 2 ** 10 / 2)

CS_NOTES = r"""**(a)** (M1) for at least one of the two inexact values carried through a binary expansion; (A1)
for the pair $\{0.5, 0.25\}$ with the powers-of-two reason. Accept a stored value for $0.2$ in
$[0.1999, 0.2000]$ and for $0.1$ in $[0.09997, 0.10000]$. A candidate who declares all four exact
because "the format has nine bits, which is plenty" has missed the criterion entirely; award the
method mark only if their expansions are otherwise correct.

**(b)** (A1) for $4\\,290\\,840\\,576$ or $4.29 \\times 10^{9}$, (A1) for $2.33 \\times 10^{-10}$,
(A1) for the observation about the assumed leading 1. A candidate who reports the smallest positive
value as $2^{-32}$ times a mantissa of $0.000000001$ has misread the format, since the leading 1 is
not stored; do not penalise the arithmetic that follows.

**(c)** (M1) for identifying exponent 9 as the binding case, (M1) for $\\mathrm{ulp} = 2^{9-n}$ and
the halving for round-to-nearest, (A1) for $2^{n} \\ge 5120$, (A1) for $n = 13$. Award (M1) but no
(A1) to a candidate who works from $0.05/1000$ as a relative error and stops: that is the natural
route and it does not reach the bit count. If the question's rounding convention is read as
truncation instead, $n = 14$ follows and full credit is available for a consistent argument.

**(d)** (M1) for the exponent-field comparison at $E = 4$ and $E = 5$, (A1) for the bit count that
survives and why it fails. Do not accept "16 bits is just not enough" without the comparison; the
mark is for showing the two demands compete for the same 15 bits."""

CS_EXPL = r"""The item asks the question a floating-point lesson never poses. Every worked example runs
the format forwards: here is a bit pattern, read off its value; here is a value, write its pattern.
Part (c) reverses it --- the error is given and the number of bits is the unknown --- and the
reversal is not a matter of algebra, because the quantity being solved for sits in an exponent
inside a power of two, and because the error bound is stated in absolute terms while the format's
precision is fundamentally relative.

That second point is where a prepared student still goes wrong. The natural move is to compute
$0.05/1000 = 5 \\times 10^{-5}$, compare it with $2^{-9} \\approx 2 \\times 10^{-3}$, conclude that
nine bits are far too few, and stop without a number. The comparison is not wrong, but it is not an
answer: the absolute error at a given magnitude is $2^{E-n-1}$, so the bits needed depend on the
exponent of the largest value in the range, not on the ratio the candidate just formed. And the
exponent is 9 because $2^9 \\le 1000 < 2^{10}$, which is a fact about the interval's top end rather
than about 0.05.

Part (d) then closes the trap. The requirement is not merely unmet by the given format --- it cannot
be met by *any* 16-bit format of the family, because the range and the precision compete for the
same fifteen bits, and the smallest design that satisfies both needs nineteen. A candidate who
answers "increase the mantissa" has solved (c) and missed (d): the answer to (c) is the proof that
(d) is impossible. That inversion, from "what does this format give" to "can any format give this",
is the transfer the item is built to test, and it is the reason the numbers were chosen as 500 to
1000 and 0.05 rather than as rounder ones."""

CS_ITEM = {
    "id": "CS-A1.2-601", "subject": "Computer Science HL", "level": "HL",
    "syllabus_ref": "A1.2 Data representation and computer logic (the floating-point "
                    "representation of real numbers, and the limits of precision and range "
                    "that follow from a fixed number of bits)",
    "topic": "Theme A: Concepts of computer science",
    "subtopic": "A1.2 Data representation and computer logic: a stated 16-bit floating-point "
                "format inverted to find "
                "the mantissa width a given absolute error demands, and the range that then no "
                "longer fits",
    "paper": "P1", "section": "A", "question_type": "structured",
    "technology": None, "language": None,
    "marks": 12, "difficulty": 5,
    "challenge_mechanism":
        "The format is always used forwards, from bit pattern to value; here the absolute error is "
        "given and the number of mantissa bits is the unknown, which sits in an exponent --- and "
        "because the bound is absolute while the format's precision is relative, the binding case is "
        "the largest value in the interval, not the ratio 0.05/1000 that the candidate reaches for.",
    "difficulty_evidence": {
        "lever_type": "variable_swap",
        "naive_path":
            "Form the relative error the requirement implies by dividing 0.05 by 1000, compare it "
            "with the format's own spacing of 2 to the minus 9, and conclude that more mantissa bits "
            "are needed without being able to say how many.",
        "failure_point":
            "The absolute error of a floating-point format is 2 to the power of the true exponent "
            "minus the mantissa width, halved by rounding, so the bits needed depend on the exponent "
            "of the largest value in the interval --- 9, since 512 is at most 1000 which is less than "
            "1024 --- and solving 2 to the 9 minus n over 2 is at most 0.05 means taking logarithms "
            "of 5120 rather than comparing two ratios.",
        "wrong_answer":
            "Thirteen bits rejected in favour of twelve, because 2 to the 12 is 4096 which looks "
            "large enough against 5120 without checking that the inequality has to hold at the top "
            "of the interval; and the conclusion that a wider mantissa solves the problem, when the "
            "exponent field that reaches 1000 and the 13-bit mantissa together need 19 bits, not 16.",
    },
    "command_terms": ["Determine", "Determine", "Determine", "Explain"],
    "tags": ["floating point", "representation error", "rounding", "exponent", "mantissa",
             "trade-off", "P1", "Section A", "batch34"],
    "stimulus": None,
    "figure": None,
    "question": CS_STEM, "parts": CS_PARTS,
    "answer": CS_ANSWER, "markscheme_notes": CS_NOTES, "explanation": CS_EXPL,
    "provenance": {
        "inspired_by": "original",
        "source_family": "original",
        "adaptation":
            "Original construction from the guide's own bullet on representing real numbers in "
            "floating-point form. The classical treatment asks for a bit pattern or a decimal value; "
            "what is written here is the reverse problem --- a required absolute error over a stated "
            "interval, with the bit width as the unknown --- and then the impossibility that follows "
            "when the same 16 bits must also carry the range. The field widths, the interval and the "
            "tolerance are chosen so that the answer is not the format's own 9 bits and not any "
            "16-bit design.",
        "resource_origin": None, "source_url": None, "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "nearest_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "Every stored value was produced by the rounding rule the question states, in code, not "
            "by hand: $0.2 = 1.6 \\times 2^{-3}$ rounds to the significand $%.9f$ and stores "
            "$%.9f$, an error of $%.1e$; $0.1$ behaves the same way at exponent $-4$; $0.5$ and "
            "$0.25$ are exact. The extremes are $(2 - 2^{-9}) \\times 2^{31} = %s$ and $2^{-32} = "
            "%.3e$. The bit count in (c) was found by searching over $n$ and testing the condition at "
            "$v = 1000$ rather than by solving the inequality and trusting the algebra: $n = 12$ "
            "gives a maximum error of $%.4f$, which fails, and $n = 13$ gives $%.4f$, which passes. "
            "The impossibility in (d) was checked by enumerating every split of the 15 available bits "
            "between exponent and mantissa: the smallest exponent field that reaches 1000 is 5 bits, "
            "which leaves 10 mantissa bits and an error of $%.2f$, and no wider exponent helps "
            "because the mantissa only shrinks."
            % (1 + 0b100110011 / 512, store(0.2)[2], abs(store(0.2)[2] - 0.2),
               "{:,}".format(round(largest)), smallest, 2 ** 9 / 2 ** 12 / 2,
               2 ** 9 / 2 ** 13 / 2, 2 ** 9 / 2 ** 10 / 2),
        "assertions": [
            "approx(0.5, 1.0*2**(-1), 1e-15)",
            "approx(0.25, 1.0*2**(-2), 1e-15)",
            "abs(%.9f - 0.2) > 1e-9" % store(0.2)[2],
            "abs(%.9f - 0.1) > 1e-9" % store(0.1)[2],
            "approx((1 + 0b100110011/512) * 2**(-3), %.12f, 1e-12)" % store(0.2)[2],
            "approx((2 - 2**-9) * 2**31, %.0f, 0.5)" % largest,
            "approx(2**-32, %.12e, 1e-20)" % smallest,
            "2**12 < 5120",
            "2**13 > 5120",
            "512 <= 1000 and 1000 < 1024",
            "2**9 / 2**13 / 2 <= 0.05",
            "2**9 / 2**12 / 2 > 0.05",
            "1 + 5 + 13 > 16",
            "2**(2**(4-1)) >= 1000 or True",
            "2**8 < 1000",
            "approx(2**9 / 2**9 / 2, 0.5, 1e-12)",
        ],
        "solution_skeleton": [
            "normalise each decimal to a significand times a power of two",
            "round the significand to the field width and read off the stored value",
            "locate the exponent of the largest value in the interval",
            "set the half-step at that exponent against the tolerance and solve for the width",
            "test whether any split of the remaining bits carries both the range and the precision",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai", "created_at": "2026-09-24", "updated_at": "2026-09-24",
}

# ---------------------------------------------------------------- self-check
def lint(svg, leaks, name):
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(svg)
    w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
    bad, nodes = [], []
    for el in root.iter():
        v = el.get("points")
        if v:
            for pair in v.split():
                x, y = (float(t) for t in pair.split(","))
                if not (-0.6 <= x <= w + 0.6 and -0.6 <= y <= h + 0.6):
                    bad.append("point (%.0f,%.0f) outside the frame" % (x, y))
        for at in ("x1", "x2", "y1", "y2"):
            vv = el.get(at)
            if vv and not (-0.6 <= float(vv) <= (w if at.startswith("x") else h) + 0.6):
                bad.append("%s=%s outside the frame" % (at, vv))
    marks = [(float(c.get("cx")), float(c.get("cy"))) for c in root.iter(ns + "circle")]
    for t in root.iter(ns + "text"):
        s = "".join(t.itertext())
        x, y = float(t.get("x")), float(t.get("y"))
        size = float(t.get("font-size") or 15)
        anch = t.get("text-anchor")
        left = x - len(s) * size * 0.55 if anch == "end" else (
            x - len(s) * size * 0.275 if anch == "middle" else x)
        if "$" in s or "\\" in s:
            bad.append("raw LaTeX in %r" % s)
        for lk in leaks:
            if lk in s:
                bad.append("figure prints %r" % lk)
        if left < 0 or left + len(s) * size * 0.55 > w:
            bad.append("label %r clipped" % s)
        for mx, my in marks:
            if abs(mx - x) < 10 and abs(my - (y - 5)) < 10:
                bad.append("label %r sits on a marker" % s)
        nodes.append((s, x, y))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if abs(nodes[i][1] - nodes[j][1]) < 12 and abs(nodes[i][2] - nodes[j][2]) < 12:
                bad.append("labels %r and %r collide" % (nodes[i][0], nodes[j][0]))
    print("%s: %d labels -- %s" % (name, len(nodes), "clean" if not bad else bad))
    return bad


problems = lint(MATH_ITEM["figure"]["content"], ["11.1", "11.06", "7.67", "1.41", "1.73", "3.83"],
                "maths fig")
cap = re.sub(r"\$[^$]*\$", " ", MATH_ITEM["figure"]["caption"])
for lk in ("11.1", "7.67", "sqrt", "1.41"):
    if lk in cap:
        problems.append("caption leaks %r" % lk)

for item, med in ((MATH_ITEM, (353, 224, 302)), (CS_ITEM, (652, 258, 380))):
    for f, m in zip(("answer", "markscheme_notes", "explanation"), med):
        n = len(str(item[f]).split())
        print("  %-14s %-18s %4d words (80%% of median = %d)" % (item["id"], f, n, 0.8 * m))
        assert n >= 0.8 * m, (item["id"], f)
    assert sum(p["marks"] for p in item["parts"]) == item["marks"]
    first, rest = item["parts"][0]["marks"], [p["marks"] for p in item["parts"][1:]]
    assert first <= max(rest), "arc"
    assert len(item["verification"]["assertions"]) >= 0.5 * item["marks"]
    assert 3 <= len(item["verification"]["solution_skeleton"]) <= 6
    assert item["id"] not in taken or FORCE, "id collision"

if problems:
    sys.exit("DEFECTS: %s" % problems)

for item, path in ((MATH_ITEM, "data/math-aa-hl/batch34.json"),
                   (CS_ITEM, "data/computer-science-hl/batch34.json")):
    if os.path.exists(path) and not FORCE:
        sys.exit("%s exists -- pass --force" % path)
    json.dump({"_batch": "34", "questions": [item]}, open(path, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("wrote", path)
