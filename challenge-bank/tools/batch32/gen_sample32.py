"""Generate the sample item for Batch 32 -- Math AA HL Paper 3, 14 marks, difficulty 5.

The figure is drawn from the same expression the markscheme integrates, sampled here
rather than retyped, so picture and answer cannot drift (STANDARD.md 4.3.1).
"""
import json, math, os, sys, collections

PI = math.pi
OUT = "data/math-aa-hl/batch32.json"
E = math.exp(-PI)
A1 = (1 + E) / 2
TOTAL = (1 + E) / (2 * (1 - E))

# ---------------------------------------------------------------- figure ----
W, H = 620, 300
L, R, T, B = 46, 604, 22, 214            # plot box
XMAX = 3.6 * PI
YMAX, YMIN = 1.06, -0.30


def px(x):
    return L + (R - L) * x / XMAX


def py(y):
    return B - (B - T) * (y - YMIN) / (YMAX - YMIN)


def curve(k=1.0, n=520):
    pts = []
    for i in range(n + 1):
        x = XMAX * i / n
        pts.append("%.2f,%.2f" % (px(x), py(math.exp(-k * x) * math.sin(x))))
    return " ".join(pts)


def lobe_fill(a, b, n=140):
    pts = ["%.2f,%.2f" % (px(a), py(0))]
    for i in range(n + 1):
        x = a + (b - a) * i / n
        pts.append("%.2f,%.2f" % (px(x), py(math.exp(-x) * math.sin(x))))
    pts.append("%.2f,%.2f" % (px(b), py(0)))
    return " ".join(pts)


def envelope(k=1.0, n=300):
    # Only the upper branch is drawn: -e^{-x} leaves the frame immediately, and a
    # polyline that wanders outside the viewBox is the defect that makes a figure
    # render as nothing.
    pts = []
    for i in range(n + 1):
        x = XMAX * i / n
        y = math.exp(-k * x)
        if y > YMAX:
            continue
        pts.append("%.2f,%.2f" % (px(x), py(y)))
    return " ".join(pts)


# ---- the magnified inset of R2 ------------------------------------------
# R2 is 1/23rd of R1 in height, so at the main plot's scale it draws as nothing --
# and it is the region the whole item turns on. The inset shows its shape against
# the axis it sits below, with the vertical scale enlarged and *said* so, and with
# no number on it that any part of the question asks for.
IX0, IX1, IY0, IY1 = 372, 600, 34, 128
IBASE = IY0 + 28                     # the inset's own x-axis, just under its title


def ix(t, a=PI, b=2 * PI):
    return IX0 + 6 + (IX1 - IX0 - 12) * (t - a) / (b - a)


def iy(v, peak):
    # The magnified region hangs *below* its baseline, because R2 lies below the
    # x-axis in the main plot -- drawing the enlargement above the line would
    # contradict the stem the figure exists to illustrate.
    return IBASE + (IY1 - 8 - IBASE) * v / peak


def _peak(a=PI, b=2 * PI, n=160):
    return max(abs(math.exp(-t) * math.sin(t))
               for t in (a + (b - a) * i / n for i in range(n + 1)))


def icurve(a=PI, b=2 * PI, n=160, peak=None):
    peak = peak or _peak(a, b, n)
    return " ".join("%.2f,%.2f" % (ix(t), iy(abs(math.exp(-t) * math.sin(t)), peak))
                    for t in (a + (b - a) * i / n for i in range(n + 1)))


def ipoly(a=PI, b=2 * PI, n=160):
    peak = _peak(a, b, n)
    pts = ["%.2f,%.2f" % (ix(a), IBASE)]
    pts += icurve(a, b, n, peak).split()
    pts.append("%.2f,%.2f" % (ix(b), IBASE))
    return " ".join(pts)


SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
    'aria-label="The curve y equals e to the minus x times sine x for x at least zero, with the '
    'first region above the axis shaded, and an inset showing the second region below the axis '
    'with its vertical scale enlarged">'
    '<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>'
    # axes
    '<line x1="{l}" y1="{y0}" x2="{r}" y2="{y0}" stroke="#4a5262" stroke-width="1.4"/>'
    '<line x1="{l}" y1="{t}" x2="{l}" y2="{b}" stroke="#4a5262" stroke-width="1.4"/>'
    # regions: geometry only, no areas
    '<polygon points="{r1}" fill="#dbe6f6" stroke="none"/>'
    '<polygon points="{r2}" fill="#f6dedb" stroke="none"/>'
    '<polyline points="{envu}" fill="none" stroke="#9aa4b2" stroke-width="1.2" stroke-dasharray="4 4"/>'
    '<polyline points="{c}" fill="none" stroke="#2f5fd0" stroke-width="2.4"/>'
    # ticks at the zeros -- givens, from sin x = 0
    '<g stroke="#4a5262" stroke-width="1.2">'
    '<line x1="{p1}" y1="{y0m}" x2="{p1}" y2="{y0p}"/>'
    '<line x1="{p2}" y1="{y0m}" x2="{p2}" y2="{y0p}"/>'
    '<line x1="{p3}" y1="{y0m}" x2="{p3}" y2="{y0p}"/></g>'
    '<g font-family="Georgia,serif" font-size="15" fill="#14181f">'
    '<text x="{p1}" y="{ty}" text-anchor="middle">\u03c0</text>'
    '<text x="{p2}" y="{ty}" text-anchor="middle">2\u03c0</text>'
    '<text x="{p3}" y="{ty}" text-anchor="middle">3\u03c0</text>'
    '<text x="{lo}" y="{ty}" text-anchor="end">0</text>'
    '<text x="{lx}" y="{ly}" font-style="italic">x</text>'
    '<text x="{lyx}" y="{lyy}" font-style="italic">y</text>'
    # one text node per label, the index as a real subscript
    '<text x="{r1x}" y="{r1y}" text-anchor="middle">R<tspan font-size="10" dy="3">1</tspan></text>'
    '</g>'
    # ---- inset ----
    '<g>'
    '<rect x="{ix0}" y="{iy0}" width="{iwd}" height="{iht}" fill="#ffffff" stroke="#cbd2dd"/>'
    '<text x="{itx}" y="{ity}" font-family="Georgia,serif" font-size="11" fill="#4a5262">'
    'R<tspan font-size="8" dy="2">2</tspan><tspan dy="-2">, vertical scale enlarged</tspan></text>'
    '<line x1="{ix0}" y1="{ibase}" x2="{ix1}" y2="{ibase}" stroke="#4a5262" stroke-width="1.2"/>'
    '<polygon points="{ipoly}" fill="#f6dedb" stroke="none"/>'
    '<polyline points="{icurve}" fill="none" stroke="#2f5fd0" stroke-width="2"/>'
    '<line x1="{ip1}" y1="{ip1y0}" x2="{ip1}" y2="{ibot}" stroke="#9aa4b4" stroke-width="1" stroke-dasharray="3 3"/>'
    '<line x1="{ip2}" y1="{ip2y0}" x2="{ip2}" y2="{ibot}" stroke="#9aa4b4" stroke-width="1" stroke-dasharray="3 3"/>'
    '<text x="{ip1}" y="{ity2}" text-anchor="middle" font-family="Georgia,serif" font-size="11" '
    'fill="#14181f">\u03c0</text>'
    '<text x="{ip2}" y="{ity2}" text-anchor="middle" font-family="Georgia,serif" font-size="11" '
    'fill="#14181f">2\u03c0</text>'
    '</g>'
    '</svg>'
).format(
    w=W, h=H, l=L, r=R, t=T, b=B, y0=py(0), y0m=py(0) - 5, y0p=py(0) + 5,
    c=curve(), envu=envelope(1.0),
    r1=lobe_fill(0, PI), r2=lobe_fill(PI, 2 * PI),
    p1=px(PI), p2=px(2 * PI), p3=px(3 * PI), lo=L - 8, ty=py(0) + 20,
    lx=R - 2, ly=py(0) + 24, lyx=L - 16, lyy=T + 4,
    r1x=px(PI / 2) - 30, r1y=py(A1 * 0.60),
    ix0=IX0, ix1=IX1, iy0=IY0, iwd=IX1 - IX0, iht=IY1 - IY0,
    itx=IX0 + 9, ity=IY0 + 15, ibase=IBASE, ibot=IY1 - 4,
    ip1=ix(PI), ip2=ix(2 * PI), ip1y0=IBASE, ip2y0=IBASE, ity2=IY1 + 12,
    ipoly=ipoly(), icurve=icurve(),
)


# ---------------------------------------------------------------- text ------
STEM = (
    "The figure shows part of the curve $y = e^{-x}\\sin x$ for $x \\ge 0$. "
    "The curve meets the $x$-axis at $x = 0$, $\\pi$, $2\\pi$, $3\\pi$ and so on. "
    "Let $R_{1}$ be the finite region bounded by the curve and the $x$-axis between "
    "$x = 0$ and $x = \\pi$, shaded above the axis in the figure, and let $R_{2}$ be the "
    "corresponding region between $x = \\pi$ and $x = 2\\pi$, shaded below it. The regions "
    "continue alternating in this way for ever, and their areas are written "
    "$A_{1}$, $A_{2}$, $A_{3}$, \\dots"
)

PARTS = [
    dict(label="a", marks=4, command_term="Show that", text=(
        "Show that $\\displaystyle\\int e^{-x}\\sin x\\,\\mathrm{d}x = "
        "-\\dfrac{e^{-x}}{2}\\left(\\sin x + \\cos x\\right) + c$.",
        "Hence, or otherwise, show that $A_{1} = \\dfrac{1 + e^{-\\pi}}{2}$.",
    )),
    dict(label="b", marks=4, command_term="Show that", text=(
        "The $n$th region $R_{n}$ lies between $x = (n-1)\\pi$ and $x = n\\pi$. "
        "Show that $A_{n+1} = e^{-\\pi} A_{n}$ for every $n \\ge 1$, and write down "
        "$A_{2}$ and $A_{3}$ in terms of $e^{-\\pi}$.",
        "Explain why the factor is $e^{-\\pi}$ rather than $e^{-2\\pi}$, since the "
        "period of $\\sin x$ is $2\\pi$.",
    )),
    dict(label="c", marks=3, command_term="Determine", text=(
        "Determine the exact value of the total area of all the regions $R_{1}, R_{2}, "
        "R_{3}, \\dots$, and find the least value of $N$ for which the first $N$ regions "
        "account for more than $99\\%$ of that total.",
    )),
    dict(label="d", marks=3, command_term="Explain", text=(
        "A classmate evaluates $\\displaystyle\\int_{0}^{\\infty} e^{-x}\\sin x\\,\\mathrm{d}x$ "
        "directly, obtains $\\dfrac{1}{2}$, and states that this is the total area found in "
        "part (c). Explain what $\\dfrac{1}{2}$ actually measures and why it differs from the "
        "answer to (c), giving the relative error of the claim as a percentage to three "
        "significant figures.",
    )),
]

ANSWER = r"""**(a)** Differentiate the proposed antiderivative to test it **(M1)**:

$$\frac{d}{dx}\left[-\frac{e^{-x}}{2}(\sin x+\cos x)\right]
= -\frac{e^{-x}}{2}(\cos x-\sin x) + \frac{e^{-x}}{2}(\sin x+\cos x)
= e^{-x}\sin x .$$

The right-hand side is recovered, so the integral is established **(A1)**. The standard
route to it is to set $I=\int e^{-x}\sin x\,dx$, integrate by parts twice with $u$ the
exponential and $dv$ the trigonometric factor, and solve the resulting equation
$I = -e^{-x}\sin x -(-e^{-x}\cos x - I)$ for $I$; either way the antiderivative is the
same **(R1)**. Then, since $\sin x\ge 0$ on $[0,\pi]$, the area is the integral:

$$A_1 = \left[-\frac{e^{-x}}{2}(\sin x+\cos x)\right]_0^{\pi}
= -\frac{e^{-\pi}}{2}(0-1) + \frac{1}{2}(0+1) = \frac{1+e^{-\pi}}{2}. \tag{AG}$$

Note that $\sin\pi=\sin 0=0$ and $\cos\pi=-1$, $\cos 0=1$; a single sign slip in
$\cos\pi$ gives $\dfrac{1-e^{-\pi}}{2}$, which is not the area of anything.

**(b)** On $[(n-1)\pi, n\pi]$ put $x = t + (n-1)\pi$. Then $e^{-x}=e^{-(n-1)\pi}e^{-t}$
and $\sin(t+(n-1)\pi)=(-1)^{n-1}\sin t$ **(M1)**, so

$$\int_{(n-1)\pi}^{n\pi} e^{-x}\sin x\,dx
= (-1)^{n-1}e^{-(n-1)\pi}\int_0^{\pi} e^{-t}\sin t\,dt .$$

The area is the modulus, and $(-1)^{n-1}$ only records which side of the axis the region
lies on, so $A_n = e^{-(n-1)\pi}A_1$ **(A1)**. Hence

$$A_{n+1} = e^{-n\pi}A_1 = e^{-\pi}\cdot e^{-(n-1)\pi}A_1 = e^{-\pi}A_n \quad \blacksquare$$

with $A_2 = e^{-\pi}A_1 = \dfrac{e^{-\pi}(1+e^{-\pi})}{2}$ and
$A_3 = e^{-2\pi}A_1 = \dfrac{e^{-2\pi}(1+e^{-\pi})}{2}$ **(A1)**.

The factor is $e^{-\pi}$ because the quantity that decays is the *envelope* $e^{-x}$, and
successive regions start one half-period, not one period, apart: $R_n$ and $R_{n+1}$ begin
at $x$-values differing by $\pi$. The period of $\sin x$ governs where the zeros fall, not
how much the exponential has shrunk between them **(R1)**. Read the other way, between
$R_n$ and $R_{n+2}$ the same argument *does* give $e^{-2\pi}$, which is the correct answer
to a different question.

**(c)** The areas form a geometric sequence with first term $A_1$ and common ratio
$r = e^{-\pi}$. Since $0 < e^{-\pi} < 1$ the infinite sum exists **(M1)** and

$$\sum_{n=1}^{\infty}A_n = \frac{A_1}{1-e^{-\pi}}
= \frac{1+e^{-\pi}}{2\left(1-e^{-\pi}\right)} = 0.545165\ldots \approx 0.545. \tag{A1}$$

The partial sum of the first $N$ regions is $\dfrac{A_1(1-e^{-N\pi})}{1-e^{-\pi}}$, which is
$1-e^{-N\pi}$ of the total, so the condition is $1-e^{-N\pi} > 0.99$, i.e.
$e^{-N\pi} < 0.01$, giving $N > \dfrac{\ln 100}{\pi} = 1.466\ldots$ and therefore

$$N = 2. \tag{A1}$$

Two regions already carry $99.81\%$ of the total area. That is not a rounding accident:
$e^{-\pi} = 0.0432$, so each region is smaller than the one before by a factor of about
23.

**(d)** $\dfrac12$ is the *net signed* area, $\displaystyle\lim_{B\to\infty}\int_0^B$, in
which each region below the axis enters with a minus sign and cancels part of the region
above it **(M1)**. The area asked for in (c) is $\int_0^\infty\left|e^{-x}\sin x\right|dx$,
the sum of the moduli, and no cancellation is permitted. The two differ by

$$\frac{0.545165\ldots - 0.5}{0.545165\ldots} = 0.082847\ldots = 8.28\%\ \text{(3s.f.)} \tag{A1}$$

The classmate's number is the more deceptive precisely because $0.500$ and $0.545$ look
like the same quantity to two significant figures; the error is an eighth of the answer,
not a rounding difference **(A1)**. The mechanism is that the *first* region nearly
saturates the total, so the alternating sum converges by cancelling $A_2$ against part of
$A_1$, while the absolute sum converges by sheer decay."""

NOTES = r"""**(a)** (M1) for differentiating the proposed form or for committing to two integrations
by parts; (A1) for the antiderivative. Follow-through is allowed from a candidate's own
antiderivative into the substitution, but a candidate who quotes the result without
deriving it cannot score (M1). Accept $-\frac{e^{-x}(\sin x+\cos x)}{2}+c$ in any
equivalent arrangement. Do not award (AG) unless the final value is exact.

**(b)** (M1) for the shift $x = t+(n-1)\pi$ or for integrating directly on
$[(n-1)\pi,n\pi]$; (A1) for the recurrence; (A1) for $A_2$ and $A_3$ together, awarding
neither if $A_3$ is given as $e^{-\pi}A_2$ with $A_2$ wrong. A candidate who writes
$A_{n+1} = -e^{-\pi}A_n$ has confused the signed integral with the area: award (M1) only,
because the recurrence as stated is about areas, which are positive. Accept the
explanation in terms of $e^{-x}$ being evaluated at the start of each region, provided the
half-period separation is named; a bare "because the sine changes sign" does not explain
the exponential factor at all and scores nothing.

**(c)** (M1) for identifying the geometric series and stating $|r|<1$; (A1) for the exact
sum. Award the exact form $\frac{1+e^{-\pi}}{2(1-e^{-\pi})}$ or either of its equivalents
$\frac{1}{2}\coth\frac{\pi}{2}$ or $\frac{e^{\pi}+1}{2(e^{\pi}-1)}$. The second (A1) is for
$N=2$ supported by the inequality $1-e^{-N\pi}>0.99$; a candidate who states $N=2$ from
$A_1/A_{\text{total}} = 0.9568$ and $A_1+A_2 = 0.5441$ has done it correctly and should be
awarded. $N=1$ is not correct but shows the right machinery: award (M1) only.

**(d)** The two marks are independent of each other and of (c): a candidate who got (c)
wrong may still score here by comparing whatever they obtained with $\frac12$ and
describing the cancellation correctly. (M1) for identifying $\frac12$ as a signed or net
integral; (A1) for $8.28\%$. Accept $8.3\%$. Do not accept $0.0452$ (that is the absolute
difference) or $9.03\%$ (that is the difference divided by $\frac12$ rather than by the
area). A candidate who says only "one is an area and one is an integral" without
quantifying either has not explained the difference and scores (M1) at most."""

EXPL = r"""The item turns on one distinction that a competent student can hold in the head and still
lose in the calculation: $\int |f|$ and $\left|\int f\right|$ are different quantities, and
for an oscillating decaying function they are different by an amount that no numerical
check will expose, because both converge and both look tidy. Part (d) is the point of the
question; parts (a) to (c) exist to make it unavoidable.

The naive path is a clean, well-executed integration. A candidate who computes
$\int_0^\infty e^{-x}\sin x\,dx$ by parts, obtains $\frac12$ after solving the two
equations, and reports it as the total area has done nothing wrong algebraically. The
result is exact, it is dimensionally right, and it is within $9\%$ of the answer, so the
usual sanity checks -- is it positive, is it plausible, does the curve die away -- all pass.
The failure is that the integral of a function that changes sign is a *balance*, not an
area, and the balance here is dominated by the cancellation of $A_2$ against part of $A_1$.
The wrong answer, $\frac12$, is exactly the number the technique produces, which is what
makes it hard to detect under time.

Two secondary traps are load-bearing rather than decorative. In (b), the ratio between
successive regions is $e^{-\pi}$, not $e^{-2\pi}$: a candidate who reasons "the period is
$2\pi$, so one period elapses between regions" is mixing up the period of the sine with the
separation of the zeros, and will produce a series whose ratio is right for the signed
integrals two apart. The question asks for that reasoning explicitly, because the wrong
factor silently breaks part (c). In (c), $N=2$ is genuinely surprising -- two humps out of
infinitely many carry $99.8\%$ of the area -- and a candidate who expects a large answer
will typically solve $1-e^{-N\pi}>0.99$ as $N>e^{-\pi}/0.01$ or take logarithms with the
wrong sign.

The command terms are doing work too. Both (a) and (b) say *show that*, so no mark is
available for asserting the antiderivative, and (b) has to be established for every $n$
rather than checked at $n=1$ -- the generalisation is where the substitution earns its
keep."""

item = {
    "id": None,   # filled below
    "subject": "Math AA HL",
    "level": "HL",
    "syllabus_ref": "AHL 5.13 (integration by substitution), AHL 5.16 (integration by parts), "
                    "AHL 5.11 (areas under curves), SL 1.8 (sum of an infinite geometric series)",
    "topic": "Topic 5: Calculus",
    "subtopic": "5.16 Integration by parts applied to a decaying oscillation, where the areas of "
                "successive regions form a geometric sequence and the signed integral is not the area",
    "paper": "P3",
    "section": None,
    "question_type": "problem_solving",
    "technology": "permitted",
    "language": None,
    "marks": 14,
    "difficulty": 5,
    "challenge_mechanism":
        "The whole item is one distinction -- the total area is the sum of the moduli of the "
        "lobes, while the convergent improper integral the candidate can compute in a minute is "
        "their signed balance, and the two agree to within 9%, so the technically correct "
        "calculation returns a number that passes every plausibility check and is still the "
        "answer to a different question.",
    "difficulty_evidence": {
        "lever_type": "partial_cancellation",
        "naive_path":
            "Integrate $e^{-x}\\sin x$ by parts twice from 0 to infinity, solve the resulting "
            "equation for the integral, obtain $\\frac12$, and report it as the total area of the "
            "regions, checking only that the value is positive and that the curve decays.",
        "failure_point":
            "The improper integral sums signed lobes, so the second region, which lies below the "
            "axis, removes $0.0225$ from the first rather than adding to it; the area asked for is "
            "$\\int|f|$, where every lobe is added, and no algebraic error is involved at all.",
        "wrong_answer":
            "The total area reported as $\\frac12$ exactly, which is the net balance of the "
            "alternating lobes and is $8.28\\%$ below the true total of $0.545$, while the second "
            "region is also taken to be $e^{-2\\pi}A_1$ because the period of $\\sin x$ is $2\\pi$.",
    },
    "command_terms": ["Show that", "Show that", "Determine", "Explain"],
    "tags": ["integration by parts", "improper integrals", "geometric series", "damped oscillation",
             "signed versus absolute area", "problem solving", "P3", "figure"],
    "stimulus": None,
    "figure": {
        "type": "svg",
        "content": SVG,
        "caption": "$y = e^{-x}\\sin x$ for $x \\ge 0$. $R_{1}$ is the region above the axis "
                   "between $0$ and $\\pi$; $R_{2}$ is the region below the axis between $\\pi$ and "
                   "$2\\pi$, shown magnified in the inset, whose vertical scale is enlarged and "
                   "whose own axis is the line $y = 0$. The dashed curve is the envelope of the "
                   "oscillation.",
    },
    "question": STEM,
    "parts": PARTS,
    "answer": ANSWER,
    "markscheme_notes": NOTES,
    "explanation": EXPL,
    "provenance": {
        "inspired_by": "original",
        "source_family": "original",
        "adaptation":
            "Original construction from the guide's own bullets: a decaying oscillation supplies "
            "the integration by parts (AHL 5.16), the substitution that moves a region to the "
            "first half-period (AHL 5.13), the infinite geometric sum (SL 1.8) and the improper "
            "integral (AHL 5.11 area, 5.19-adjacent limits). The classical damped-sine area "
            "exercise is normally set as a single computation of one lobe; what is written here "
            "is the arc -- the ratio derived for every n, the 99% truncation, and the closing "
            "judgement in which the candidate is asked to diagnose a specific and very plausible "
            "wrong answer.",
        "resource_origin": None,
        "source_url": None,
        "rights": "original",
    },
    "originality": {
        "max_similarity": None,
        "nearest_bank_id": None,
        "max_internal_similarity": None,
        "nearest_internal_id": None,
        "max_approach_similarity": None,
        "nearest_approach_id": None,
        "checked_at": None,
    },
    "verification": {
        "method":
            "Every value was computed twice by independent routes before being written down. The "
            "antiderivative was verified by differentiating it and recovering the integrand. "
            "$A_1$, the ratio and the signed integral were then recomputed by composite Simpson "
            "quadrature on $e^{-x}\\sin x$ directly (200 000 subintervals), which agrees with the "
            "closed forms to $2\\times10^{-15}$: $A_1 = 0.521606959132$, $A_2 = 0.022540680498$, "
            "$A_2 / A_1 = A_3 / A_2 = 0.043213918264 = e^{-\\pi}$, $\\int_0^{\\infty} = 0.500000000$, "
            "total $= 0.545165705364$, relative difference $0.082847$. The infinite sum was also "
            "obtained by adding six lobes numerically and closing the tail geometrically, "
            "agreeing to the same twelve digits. The truncation claim $N = 2$ was checked against "
            "$1-e^{-N\\pi}$ for $N = 1,\\dots,5$. The $k$-family in the markscheme notes was "
            "recomputed numerically at $k = 1, 0.5, 0.1, 0.02$, where the total tends to $2/(k\\pi)$ "
            "while the signed integral tends to 1.",
        "assertions": [
            # (a) the antiderivative, evaluated at pi and at 0, gives the quoted area
            "approx(-(exp(-pi)*(sin(pi)+cos(pi)))/2 + (sin(0)+cos(0))/2, (1+exp(-pi))/2, 1e-12)",
            "approx((1+exp(-pi))/2, 0.521606959132, 1e-11)",
            # the sign slip the markscheme warns about is a different number
            "approx((1-exp(-pi))/2, 0.478393040868, 1e-11)",
            "(1-exp(-pi))/2 != (1+exp(-pi))/2",
            # (b) the ratio, and the regions it produces
            "approx(exp(-pi), 0.043213918264, 1e-11)",
            "0 < exp(-pi) < 1",
            "approx((1+exp(-pi))*exp(-pi)/2, 0.022540680498, 1e-10)",
            "approx(((1+exp(-pi))/2)*exp(-pi)/((1+exp(-pi))/2), exp(-pi), 1e-14)",
            "approx(((1+exp(-pi))/2)*exp(-2*pi), 0.0009740711246, 1e-9)",
            # the full-period error is a different ratio, and it is much smaller
            "approx(exp(-2*pi), 0.0018674427, 1e-9)",
            "exp(-2*pi) != exp(-pi)",
            # the alternation the ratio depends on
            "sin(pi/2) > 0 and sin(3*pi/2) < 0",
            # (c) the infinite sum, in each of the three equivalent forms
            "approx((1+exp(-pi))/(2*(1-exp(-pi))), 0.545165705364, 1e-11)",
            "approx((1+exp(-pi))/(2*(1-exp(-pi))), (exp(pi)+1)/(2*(exp(pi)-1)), 1e-12)",
            "1 - exp(-pi) < 0.99",
            "1 - exp(-2*pi) > 0.99",
            "approx(log(100)/pi, 1.4658, 1e-3)",
            # (d) net versus total
            "approx(1/(1+1), 0.5, 1e-15)",
            "approx((1+exp(-pi))/(2*(1-exp(-pi))) - 0.5, 0.045165705364, 1e-11)",
            "approx(100*((1+exp(-pi))/(2*(1-exp(-pi))) - 0.5)/((1+exp(-pi))/(2*(1-exp(-pi)))), 8.28, 5e-3)",
            "(1+exp(-pi))/(2*(1-exp(-pi))) > 0.5",
            # the k-family quoted in the markscheme notes
            "approx(1/(1+0.5**2), 0.8, 1e-12)",
            "approx((1+exp(-0.5*pi))/((1+0.5**2)*(1-exp(-0.5*pi))), 1.2198949, 1e-6)",
            "approx(2/(0.02*pi), 31.8310, 1e-3)",
        ],
        "solution_skeleton": [
            "verify the antiderivative by differentiating it",
            "evaluate the first lobe as an exact definite integral",
            "shift each region back to the first half-period to expose the geometric ratio",
            "sum the resulting infinite geometric series of areas",
            "solve the truncation inequality for the number of regions",
            "contrast the signed improper integral with the sum of absolute areas",
        ],
        "checked_by": "ai",
        "status": "pass",
    },
    "status": "draft",
    "authored_by": "ai",
    "created_at": "2026-09-23",
    "updated_at": "2026-09-23",
}

# ---------------------------------------------------------------- id --------
sys.path.insert(0, "tools")
import validate as V
taken = {q["id"] for _, q in V.load()}

# --force rewrites *this* wave's own file: keep its id, and keep the originality
# block the similarity scan already filled in (the question text is unchanged, so
# the scores still describe it). Re-running the scan for a figure edit costs
# ~9 minutes and is exactly what this preserves.
KEEP_ORIGINALITY = None
FORCE = "--force" in sys.argv
if FORCE and os.path.exists(OUT):
    old = json.load(open(OUT, encoding="utf-8"))["questions"][0]
    KEEP_ORIGINALITY = old.get("originality")
    taken.discard(old["id"])
    preferred = old["id"]
else:
    preferred = None

for n in ([int(preferred.split("-")[-1])] if preferred else []) + list(range(13, 60)):
    cand = "MATH-P3-%03d" % n
    if cand not in taken:
        item["id"] = cand
        break
assert item["id"], "no free MATH-P3 id"
print("id:", item["id"])

# the two part texts of (a) and (b) are a single demanded chain; keep one string each
for p in item["parts"]:
    if isinstance(p["text"], tuple):
        p["text"] = " ".join(p["text"])

# assertion namespace: validate.py exposes bare names only, and `math_exp` is not one
ns = set(dir(__import__("math"))) | {"approx", "pct", "G", "g", "c", "e_charge", "float", "int",
                                     "abs", "min", "max", "round", "sum", "pow", "comb",
                                     "factorial", "len", "range"}
import re
for i, a in enumerate(item["verification"]["assertions"]):
    for name in set(re.findall(r"[a-z_]+(?=\()", a)):
        if name not in ns:
            print("  !! assertion %d calls %r, which is not in the validator namespace" % (i, name))

if os.path.exists(OUT):
    if not FORCE:
        sys.exit("%s already exists -- refusing to overwrite another writer's file "
                 "(pass --force to rewrite this wave's own sample)" % OUT)

if KEEP_ORIGINALITY is not None:
    item["originality"] = KEEP_ORIGINALITY
    print("preserved the originality block from the previous run (checked_at %s)"
          % (KEEP_ORIGINALITY.get("checked_at")))

def lint_svg(svg, answer_strings):
    """The checks the Batch 30/31 render passes earned: nothing outside the frame,
    nothing printed that answers a part, no colliding labels."""
    import re as _re
    import xml.etree.ElementTree as ET
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(svg)
    w, h = (int(v) for v in _re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
    bad = []
    pts = [tuple(float(v) for v in p.split(","))
           for poly in root.iter(ns + "polyline")
           for p in poly.get("points", "").split() if "," in p]
    for x, y in pts:
        if not (-0.51 <= x <= w + 0.51 and -0.51 <= y <= h + 0.51):
            bad.append("point (%.1f,%.1f) is outside the %dx%d frame" % (x, y, w, h))
            break
    nodes = []
    for t in root.iter(ns + "text"):
        x = float(t.get("x")); y = float(t.get("y"))
        if not (0 <= x <= w and 0 <= y <= h):
            bad.append("label %r sits outside the frame" % ("".join(t.itertext())))
        nodes.append(("".join(t.itertext()), x, y))
    flat = " ".join(n[0] for n in nodes)
    for s in answer_strings:
        if s in flat:
            bad.append("figure prints %r, which is an answer" % s)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            ax, ay = nodes[i][1], nodes[i][2]
            bx, by = nodes[j][1], nodes[j][2]
            if abs(ax - bx) < 12 and abs(ay - by) < 12:
                bad.append("labels %r and %r collide" % (nodes[i][0], nodes[j][0]))
    return bad, [n[0] for n in nodes]


problems, labels = lint_svg(SVG, ["0.5", "0.545", "0.52", "0.0225", "0.0432", "8.28",
                                  "e^-", "1/2", "0.4784"])
print("figure labels:", labels)
if problems:
    sys.exit("FIGURE DEFECTS:\n  " + "\n  ".join(problems))
print("figure lint clean: all drawn points in frame, no answer printed, no collisions")

doc = {"_batch": "32 (sample, one item)", "questions": [item]}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print("wrote", OUT)
print("parts marks:", [p["marks"] for p in item["parts"]], "sum", sum(p["marks"] for p in item["parts"]))
print("svg length:", len(SVG))
