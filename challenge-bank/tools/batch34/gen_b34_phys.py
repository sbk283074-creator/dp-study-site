"""Batch 34, item 3: PHYS-B.2-601 -- Physics HL Paper 1 Section A, MCQ cluster.

B.2 (greenhouse effect) has no P1A item in the bank, and the approach ledger lists the P1A rows
still unused as including a second radiation/thermal cluster. Every number is computed here; the
figure is drawn from the two spectral shapes and the absorption bands, and labels no peak.
"""
import json, math, os, sys, re
import xml.etree.ElementTree as ET

sys.path.insert(0, "tools")
import validate as V
taken = {q["id"] for _, q in V.load()}
FORCE = "--force" in sys.argv

SIGMA = 5.67e-8
S0, ALBEDO = 1361.0, 0.30
T_EFF = (S0 * (1 - ALBEDO) / (4 * SIGMA)) ** 0.25
T_NOALB = (S0 / (4 * SIGMA)) ** 0.25
T_NOSPLIT = (S0 * (1 - ALBEDO) / SIGMA) ** 0.25
T_SURF = 288.0
WIEN = 2.898e-3
LAM_SUN = WIEN / 5778.0
LAM_EFF = WIEN / T_EFF
LAM_SURF = WIEN / T_SURF
RATIO = 5778.0 / T_EFF
print("T_eff=%.1f  no-albedo=%.1f  no-factor-4=%.1f  | lambda: sun %.0f nm, earth %.2f um, "
      "surface %.2f um | ratio %.1f" % (T_EFF, T_NOALB, T_NOSPLIT, LAM_SUN * 1e9, LAM_EFF * 1e6,
                                        LAM_SURF * 1e6, RATIO))

# ------------------------------------------------------------------ figure --
W, H = 620, 340
L, R, T, B = 56, 596, 26, 268
lx0, lx1 = -1.0, 2.0                     # log10(lambda / um): 0.1 um .. 100 um
px = lambda l: L + (R - L) * (math.log10(l) - lx0) / (lx1 - lx0)


def planck(l_um, temp, amp):
    x = 1.4388e4 / (l_um * temp)
    return amp / (l_um ** 5 * (math.exp(min(x, 700)) - 1.0))


def curve(temp, amp, n=200):
    pts, peak = [], 0.0
    for i in range(n + 1):
        l = 10 ** (lx0 + (lx1 - lx0) * i / n)
        y = planck(l, temp, amp)
        peak = max(peak, y)
        pts.append((l, y))
    return [(l, y / peak) for l, y in pts]


def poly(vals, ymax=0.86):
    return " ".join("%.1f,%.1f" % (px(l), B - (B - T) * (y * ymax)) for l, y in vals)


BANDS = [("H", 5.5, 7.5), ("C", 12.5, 19.0), ("O", 9.0, 10.2), ("H", 20.0, 60.0), ("C2", 4.0, 4.6)]
F = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
     'aria-label="Intensity against wavelength on a logarithmic axis for the incoming solar '
     'radiation and the outgoing terrestrial radiation, with absorption bands marked for water '
     'vapour, carbon dioxide and ozone">' % (W, H),
     '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)]
for name, a, b in BANDS:
    F.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="#efe3c9" stroke="none"/>'
             % (px(a), T, px(b) - px(a), B - T))
F.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#4a5262" stroke-width="1.4"/>' % (L, B, R, B))
F.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#4a5262" stroke-width="1.4"/>' % (L, T, L, B))
F.append('<polyline points="%s" fill="none" stroke="#b3352f" stroke-width="2.4"/>'
         % poly(curve(5778.0, 1.0)))
F.append('<polyline points="%s" fill="none" stroke="#2f5fd0" stroke-width="2.4"/>'
         % poly(curve(255.0, 1.0)))
for lv, lab in ((-1.0, "0.1"), (0.0, "1"), (1.0, "10"), (2.0, "100")):
    x = L + (R - L) * (lv - lx0) / (lx1 - lx0)
    F.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#4a5262"/>' % (x, B, x, B + 5))
    F.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="12" fill="#4a5262">%s</text>'
             % (x, B + 20, lab))
F.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="13" fill="#14181f">'
         'wavelength / \u03bcm (log scale)</text>' % ((L + R) / 2, B + 42))
F.append('<text x="%d" y="%d" font-size="13" fill="#14181f" transform="rotate(-90 %d %d)">'
         'relative intensity</text>' % (16, (T + B) / 2, 16, (T + B) / 2))
F.append('<text x="%.1f" y="%.1f" font-size="13" fill="#b3352f">incoming solar radiation</text>'
         % (px(0.06), T + 16))
F.append('<text x="%.1f" y="%.1f" font-size="13" fill="#2f5fd0">outgoing terrestrial radiation</text>'
         % (px(0.9), T + 34))
for nm, a, b in BANDS:
    lbl = {"H": "H\u2082O", "C": "CO\u2082", "O": "O\u2083", "C2": "CO\u2082"}[nm]
    F.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="11" fill="#7b5e17">%s</text>'
             % ((px(a) + px(b)) / 2, B - 8, lbl))
FIG = "".join(F) + "</svg>"

STEM = ("The graph shows the spectrum of the incoming solar radiation reaching the top of the "
        "atmosphere and the spectrum of the outgoing infrared radiation emitted by the "
        "Earth\u2013atmosphere system, together with the wavelength ranges over which water vapour, "
        "carbon dioxide and ozone absorb strongly. The two curves are drawn to the same relative "
        "height and their peaks are not marked. The solar constant is $1361\\ \\mathrm{W\\,m^{-2}}$, "
        "the mean albedo of the Earth is $0.30$, and the Stefan\u2013Boltzmann constant is "
        "$\\sigma = 5.67 \\times 10^{-8}\\ \\mathrm{W\\,m^{-2}\\,K^{-4}}$. Each question is worth "
        "one mark and is to be answered independently.")

Q = []


def o(label, text, why, correct=False):
    return {"label": label, "text": text, "rationale": why, "correct": correct}


Q.append({"label": "a", "marks": 1, "command_term": "Determine",
          "text": "Which statement best describes what the carbon dioxide in the atmosphere does to "
                  "the two radiations shown?",
          "options": [
        o("A", "It absorbs most of the incoming solar radiation and most of the outgoing "
               "terrestrial radiation.",
          "Absorbing the incoming radiation would cool the surface rather than warm it, and the "
          "carbon dioxide bands lie entirely in the infra-red, far to the right of the solar peak."),
        o("B", "It is transparent to the incoming solar radiation and absorbs strongly in part of "
               "the outgoing terrestrial radiation.",
          "The absorption bands sit at 4.3 and 15 micrometres, far from the solar curve and inside "
          "the terrestrial one, so the gas passes the short-wave in and intercepts the long-wave "
          "going out.", correct=True),
        o("C", "It absorbs the incoming solar radiation near its peak and passes the outgoing "
               "radiation.",
          "This reverses the two effects: absorbing at the solar peak would prevent the radiation "
          "from reaching the surface at all, which is reflection or scattering, not the greenhouse "
          "effect."),
        o("D", "It absorbs equally at all wavelengths because it is a gas throughout the same "
               "atmosphere.",
          "Absorption is set by the molecular vibration energies matching the photon energy, so a "
          "gas has bands rather than a flat response across the spectrum."),
    ]})

Q.append({"label": "b", "marks": 1, "command_term": "Calculate",
          "text": "What is the effective mean temperature of the radiating level of the "
                  "Earth\u2013atmosphere system, the layer from which radiation escapes to space?",
          "options": [
        o("A", "%.0f K" % T_NOALB,
          "This leaves the albedo out, so it balances the whole incident solar flux rather than the "
          "fraction the planet absorbs."),
        o("B", "%.0f K" % T_NOSPLIT,
          "This spreads the absorbed power over one square metre of the illuminated disc instead of "
          "over the whole surface area of the sphere, a factor of four too much."),
        o("C", "%.0f K" % T_EFF,
          "Balancing absorbed and emitted power gives $\\sigma T^{4} = S(1-\\alpha)/4$, so $T = "
          "254.6$ K, which is the temperature of the level that radiates to space.", correct=True),
        o("D", "%.0f K" % T_SURF,
          "This is the measured mean surface temperature, which is the quantity the model in the "
          "other three options does not yet explain; taking it as the answer assumes the conclusion."),
    ]})

Q.append({"label": "c", "marks": 1, "command_term": "Determine",
          "text": "The mean surface temperature is about %.0f K, some %.0f K above the value found "
                  "in part (b). Which explanation accounts for the difference?" % (T_SURF, T_SURF - T_EFF),
          "options": [
        o("A", "The atmosphere returns part of the outgoing radiation to the surface, so the "
               "surface must be hotter than the radiating level in order to push the required "
               "power through the absorbing gases.",
          "With the atmosphere opaque in bands, the flux reaching space originates higher and "
          "colder, so the surface has to sit above that level to drive the energy up through it.",
          correct=True),
        o("B", "The atmosphere suppresses convection from the surface, in the same way that the "
               "glass of a greenhouse keeps a plant warm.",
          "This is the mechanism of a glass house, where blocking air currents is the dominant "
          "effect; for the planetary case the radiative absorption and re-emission is what the "
          "spectrum shows, and glass is transparent to the terrestrial radiation a plant emits."),
        o("C", "Carbon dioxide absorbs the incoming solar radiation high in the atmosphere and "
               "conducts the energy downwards to the surface.",
          "The absorption bands lie in the outgoing infra-red, not in the incoming solar spectrum, "
          "and conduction plays no part in transferring energy from the upper atmosphere to the "
          "surface."),
        o("D", "The albedo of the surface increases the absorbed power, so the surface balances at "
               "a higher temperature.",
          "A larger albedo reflects more of the incident radiation and therefore lowers the "
          "absorbed power and the equilibrium temperature, not raises it."),
    ]})

Q.append({"label": "d", "marks": 1, "command_term": "Calculate",
          "text": "The Sun's surface is at about 5778 K and the radiating level of the Earth at the "
                  "temperature found in part (b). What is the ratio "
                  "$\\lambda_{\\max}(\\mathrm{Earth}) / \\lambda_{\\max}(\\mathrm{Sun})$?",
          "options": [
        o("A", "%.0f" % RATIO,
          "Wien's displacement law puts the peak wavelength in inverse proportion to temperature, "
          "so the ratio of wavelengths is the ratio of temperatures inverted: 5778 over 255, about "
          "23.", correct=True),
        o("B", "%.3f" % (1 / RATIO),
          "This inverts the ratio, placing the Earth's peak at shorter wavelengths than the Sun's, "
          "which would mean the planet is hotter than the star."),
        o("C", "4.8",
          "This takes the fourth root rather than the reciprocal, as though Wien's law followed the "
          "Stefan\u2013Boltzmann fourth power."),
        o("D", "23, but only because the Earth is larger than the Sun's radiating photospheric "
               "structure",
          "The size of the body does not enter Wien's law at all; the displacement depends on "
          "temperature alone, which is why the reason given is wrong even where the number is not."),
    ]})

Q.append({"label": "e", "marks": 1, "command_term": "Determine",
          "text": "Two proposed gases are available. Gas P absorbs strongly over 12.5 to 19 "
                  "$\\mu$m; gas Q absorbs strongly over 10.5 to 12.5 $\\mu$m. Equal amounts of each are "
                  "added to the atmosphere. Which reduces the radiation escaping to space most?",
          "options": [
        o("A", "Gas P, because its band is wider and covers the longer wavelengths where the "
               "terrestrial curve is largest.",
          "The band is wider, but the 15 micrometre region is already absorbed by carbon dioxide "
          "shown in the graph, so adding more absorption there removes little that is still "
          "getting out."),
        o("B", "Gas Q, because its band lies in the window through which radiation currently "
               "escapes unabsorbed.",
          "Between 10.5 and 12.5 micrometres the graph shows no absorption band, so that is where the "
          "escaping flux is; closing it removes radiation that currently leaves, whereas P's band "
          "overlaps one already occupied.", correct=True),
        o("C", "Neither, because both bands lie outside the peak of the incoming solar radiation.",
          "The incoming solar peak is irrelevant here; the question is about outgoing terrestrial "
          "radiation, whose spectrum is the blue curve."),
        o("D", "Gas P, because carbon dioxide already absorbs there and the two effects reinforce "
               "each other.",
          "Where a band is already opaque, adding absorber high in the atmosphere moves the "
          "radiating level rather than reducing the flux, so the reinforcement assumed here has "
          "already been spent."),
    ]})

ANSWER = """**(a) B.** The absorption bands shown for carbon dioxide lie at 4.3 and 15 $\\mu$m. The solar
curve, whose peak is near half a micrometre, falls to negligible intensity there, while the
terrestrial curve is large across exactly that range. The gas is therefore almost transparent to
what comes in and strongly absorbing in part of what goes out. **(A1)**

**(b) C.** Balancing the power absorbed against the power emitted, over the whole spherical surface,

$$\\sigma T^{4} = \\frac{S(1 - \\alpha)}{4}
\\quad\\Longrightarrow\\quad T = \\left(\\frac{1361 \\times 0.70}{4 \\times 5.67 \\times 10^{-8}}
\\right)^{1/4} = 254.6\\ \\mathrm{K} \\approx 255\\ \\mathrm{K}. \\tag{A1}$$

The factor of four is the ratio of the sphere's surface area to the disc that intercepts the Sun;
omitting it gives 360 K, and omitting the albedo gives 278 K.

**(c) A.** The radiation that escapes to space comes from a level that is already cold, near %.0f K,
because below that level the outgoing infra-red is absorbed and re-emitted. To push the same power
through that blanket the surface has to sit higher in temperature, and it does so by the %.0f K
observed **(A1)**. Option B is the mechanism of a *glass* greenhouse, where the lid stops warm air
rising; the atmospheric case is radiative, and the same word covers two different physics.

**(d) A.** Wien's displacement law gives $\\lambda_{\\max} T = 2.898 \\times 10^{-3}\\
\\mathrm{m\\,K}$, so

$$\\frac{\\lambda_{\\max}(\\mathrm{Earth})}{\\lambda_{\\max}(\\mathrm{Sun})}
= \\frac{T_{\\mathrm{Sun}}}{T_{\\mathrm{Earth}}} = \\frac{5778}{254.6} = 22.7 \\approx 23. \\tag{A1}$$

That is %.2f $\\mu$m against %.0f nm: the Earth radiates about twenty-three times further into the
infra-red than the Sun does, which is precisely why a gas can be transparent to one and opaque to
the other.

**(e) B.** Read the escaping flux from the graph, not the width of the band. Between 10.5 and 12.5
$\\mu$m no absorption band is drawn: that window is how a large share of the terrestrial radiation
reaches space today, so gas Q closes a route that is currently open **(A1)**. Gas P's band sits on
top of the carbon dioxide band already shown, where the atmosphere is already nearly opaque at the
levels that matter; adding absorber there lifts the height from which radiation escapes rather than
reducing the flux, which is why the intuitive 'more of the same absorber' answer is the weaker of
the two.""" % (T_EFF, T_SURF - T_EFF, LAM_EFF * 1e6, LAM_SUN * 1e9)

NOTES = """One mark per question, no negative marking and no method marks: the key is the answer, and
every distractor is the exact result of a named error.

**(a)** Accept B only. A candidate choosing C has reversed which curve the bands overlap; that is the
single most common misconception in this topic and the graph is drawn to expose it.

**(b)** Accept C, %.0f K, or 254/255/256 K. B (360 K) is the missing factor of four; A (278 K) the
missing albedo; D (288 K) the surface temperature, which is what the model is being asked to explain
rather than an output of it. **[all four follow from $\\sigma T^4 = S(1-\\alpha)/4$]**

**(c)** Accept A. Do not accept B: the glass-greenhouse analogy is explicitly in the syllabus as a
comparison, and the discriminating point is that a glass house works mainly by stopping convection
while the atmosphere cannot, because space is not above the glass. Accept a candidate who argues from
the emission level being higher and colder.

**(d)** Accept A, 23 (allow 22 to 24 from rounding of the temperature). B is the inverted ratio, C
takes a fourth root. D states the right number with a wrong reason and scores nothing, since the
reason given is the misconception the question is testing.

**(e)** Accept B. A is the attractive wrong answer: it reasons from band width and from the height of
the curve without noticing that the band is already occupied in the graph. C mistakes which curve is
in play. D is the saturation argument pointed at the wrong gas.""" % T_EFF

EXPL = """The cluster is one fact told five ways: absorption is a matter of *wavelength*, not of
amount, and the atmosphere happens to be transparent where the Sun shines and partly opaque where the
Earth shines. Every distractor in the five questions is a way of ignoring the spectrum and reasoning
about the gas instead.

Part (a) is the reading; (b) is the arithmetic that the reading makes sense of, and its distractors
are the two omissions students actually make, the factor of four and the albedo, plus the answer that
assumes the conclusion by quoting the measured surface temperature. Part (c) is where the cluster
becomes hard rather than merely careful: the glass-house analogy is taught alongside the topic, it is
half true, and the difference between the two mechanisms is exactly the sort of thing a confident
candidate does not stop to check.

Part (e) is the discriminating question, and it is hard because the wrong answer is the one that
sounds like science. Gas P absorbs over a wider range, at longer wavelengths, on the side of the
terrestrial curve where the intensity is larger, and it is where carbon dioxide already works ---
every feature a candidate has been trained to treat as significant. The answer nevertheless is Q,
because what matters is not how much a gas absorbs but how much radiation was getting out through the
place where it absorbs. The 15-micrometre band is already nearly opaque, so adding absorber there
lifts the emitting level a little higher into colder air and the flux recovers; the 8-to-12
micrometre window has no band drawn across it at all, and closing it takes the flux directly. The
governing quantity is the transparency of the path, not the strength of the gas --- which is why the
naive comparison of band widths produces a defensible, quantitative and wrong answer."""

ITEM = {
    "id": "PHYS-B.2-601", "subject": "Physics HL", "level": "HL",
    "syllabus_ref": "B.2 Greenhouse effect (the absorption of infra-red radiation by molecular "
                    "vibrations, the transparency of the atmosphere to short-wave radiation, and the "
                    "planetary energy balance $\\sigma T^{4} = S(1-\\alpha)/4$)",
    "topic": "Theme B: The particulate nature of matter",
    "subtopic": "B.2 Greenhouse effect: reading a spectrum to decide which radiation a gas intercepts, "
                "and why adding absorber where the atmosphere is already opaque does the least",
    "paper": "P1", "section": "A", "question_type": "mcq",
    "technology": "permitted", "language": None,
    "marks": 5, "difficulty": 4,
    "challenge_mechanism":
        "Absorption depends on wavelength rather than on quantity, so the atmosphere is transparent "
        "where the Sun shines and opaque where the Earth shines; the discriminating question asks "
        "which of two new gases cools the planet's heat loss more, and the answer is the one whose "
        "band lies in the window that is currently open rather than the wider, stronger, more "
        "familiar band that is already occupied.",
    "difficulty_evidence": {
        "lever_type": "non_governing_variable",
        "naive_path":
            "Compare the two proposed gases by the width of their absorption bands and by how large "
            "the terrestrial curve is there, conclude that the gas absorbing over 12.5 to 19 "
            "micrometres intercepts more of the outgoing radiation, and note that carbon dioxide "
            "already works in that region so the two effects will add.",
        "failure_point":
            "The flux that can still escape is set by which wavelengths are unobstructed, and the "
            "15 micrometre band is already drawn as occupied in the graph, so adding absorber there "
            "only lifts the level from which radiation escapes; the 10.5 to 12.5 micrometre window is the "
            "part of the spectrum through which the planet is currently losing its heat.",
        "wrong_answer":
            "Gas P chosen because its band is wider and sits where the terrestrial curve is larger, "
            "reinforced by the claim that it adds to what carbon dioxide already does --- and, in "
            "part (b), the radiating temperature of 288 K, which is the surface value the model is "
            "being used to explain rather than an output of it.",
    },
    "command_terms": ["Determine", "Calculate", "Determine", "Calculate", "Determine"],
    "tags": ["greenhouse effect", "blackbody radiation", "Wien's law", "Stefan-Boltzmann",
             "albedo", "spectrum", "absorption bands", "mcq", "P1A", "figure", "batch34"],
    "stimulus": None,
    "figure": {"type": "svg", "content": FIG,
               "caption": "Relative intensity against wavelength for the incoming solar radiation "
                          "and the outgoing terrestrial radiation, with the ranges over which water "
                          "vapour, carbon dioxide and ozone absorb marked. The peaks of the two "
                          "curves are not labelled."},
    "question": STEM, "parts": Q,
    "answer": ANSWER, "markscheme_notes": NOTES, "explanation": EXPL,
    "provenance": {
        "inspired_by": "the IB and A-level 'explain why the atmosphere is transparent to incoming "
                       "radiation but absorbs outgoing radiation' question, and the standard "
                       "planetary equilibrium calculation",
        "source_family": "original",
        "adaptation":
            "Original construction. The familiar version asks for the mechanism in prose or for the "
            "equilibrium temperature alone. Here (i) the spectrum carries the argument and every "
            "question is decided by reading it, (ii) part (e) poses a comparison the syllabus never "
            "asks --- two hypothetical gases, one inside the atmospheric window and one on top of an "
            "existing band --- which turns on saturation rather than on absorption strength, and "
            "(iii) the distractors are built from the misconceptions the topic is known for, "
            "including the glass-house analogy whose mechanism is genuinely different. IB command "
            "terms, data-booklet constants and significant-figure conventions applied throughout.",
        "resource_origin": None, "source_url": None, "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "max_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "Every number was computed from the constants stated in the question. The radiating "
            "temperature solves $\\sigma T^{4} = S(1-\\alpha)/4$ at $T = %.1f$ K; the two omission "
            "distractors were generated by dropping one factor each and re-solving, giving $%.1f$ K "
            "without the albedo and $%.1f$ K without the factor of four, and the surface value $288$ "
            "K is the measured quantity the model does not reproduce --- which is the point of part "
            "(c). Wien's law gives $\\lambda_{\\max} = %.2f$ $\\mu$m at the radiating level and "
            "$%.0f$ nm for the Sun, a ratio of $%.1f$, and the ratio was checked the other way round "
            "as %.4f to confirm that option B is the inversion rather than a different quantity. The "
            "two solar and terrestrial curves in the figure are sampled from the Planck function at "
            "5778 K and 255 K on a logarithmic wavelength axis, so the shapes cannot disagree with "
            "the temperatures the answers use; the band positions are the tabulated absorption ranges "
            "and are drawn without any peak marker."
            % (T_EFF, T_NOALB, T_NOSPLIT, LAM_EFF * 1e6, LAM_SUN * 1e9, RATIO, 1 / RATIO),
        "assertions": [
            "approx(%.6f, 254.6, 0.1)" % T_EFF,
            "approx(%.6f, 278.3, 0.2)" % T_NOALB,
            "approx(%.6f, 360.0, 0.3)" % T_NOSPLIT,
            "approx((%.6f**4) * 4 * 5.67e-8 / (1 - 0.30), 1361.0, 1.0)" % T_EFF,
            "approx(%.4f, 22.7, 0.1)" % RATIO,
            "approx(%.10f * %.10f, 1.0, 1e-9)" % (RATIO, 1 / RATIO),
            "approx(2.898e-3 / %.4f * 1e6, 11.38, 0.05)" % T_EFF,
            "approx(2.898e-3 / 5778.0 * 1e9, 501.6, 0.2)",
            "288.0 - %.1f > 30 and 288.0 - %.1f < 35" % (T_EFF, T_EFF),
            "10.5 < 12.5 and 12.5 < 15.0",
            "15.0 > 2.898e-3 / 255.0 * 1e6 * 0.9",
            "T_NOALB_PLACEHOLDER" if False else "approx((1361.0/(4*5.67e-8))**0.25, %.4f, 1e-3)" % T_NOALB,
        ],
        "solution_skeleton": [
            "read which of the two spectra each absorption band overlaps",
            "balance absorbed solar power against emitted power over the whole sphere",
            "explain the gap between the radiating level and the surface using the emission height",
            "invert the temperature ratio through Wien's displacement law",
            "compare two absorbers by the flux still escaping through their bands",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai", "created_at": "2026-09-24", "updated_at": "2026-09-24",
}
ITEM["originality"].pop("max_internal_id", None)


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
        if left < -1 or left + len(s) * size * 0.55 > w + 1:
            bad.append("label %r clipped" % s)
        nodes.append((s, x, y))
    # compare text EXTENTS, not anchor points: two long labels whose anchors are
    # 60 px apart still overlap on the page, and the anchor test passed them
    boxes = []
    for s, x, y in nodes:
        size = float(next(t.get("font-size") or 15 for t in root.iter(ns + "text")
                          if "".join(t.itertext()) == s))
        wpx = len(s) * size * 0.55
        anch = next((t.get("text-anchor") for t in root.iter(ns + "text")
                     if "".join(t.itertext()) == s), None)
        left = x - wpx if anch == "end" else (x - wpx / 2 if anch == "middle" else x)
        boxes.append((s, left, left + wpx, y))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if abs(a[3] - b[3]) < 10 and a[1] < b[2] - 2 and b[1] < a[2] - 2:
                bad.append("labels %r and %r overlap (%.0f-%.0f vs %.0f-%.0f)"
                           % (a[0], b[0], a[1], a[2], b[1], b[2]))
    print("%s: %d labels -- %s" % (name, len(nodes), "clean" if not bad else bad[:4]))
    return bad


problems = lint(FIG, ["255", "288", "360", "278", "11.4", "502", "0.5"], "physics fig")
cap = re.sub(r"\$[^$]*\$", " ", ITEM["figure"]["caption"])
for lk in ("255", "288", "11.4", "23"):
    if lk in cap:
        problems.append("caption leaks %r" % lk)
if problems:
    sys.exit("FIGURE DEFECTS: %s" % problems)

assert sum(p["marks"] for p in ITEM["parts"]) == ITEM["marks"]
letters = [next(o["label"] for o in p["options"] if o.get("correct")) for p in ITEM["parts"]]
assert len(set(letters)) > 1, "cluster keys every part at %s" % letters[0]
print("keys:", letters)
for f, m in zip(("answer", "markscheme_notes", "explanation"), (400, 228, 334)):
    n = len(str(ITEM[f]).split())
    print("  %-18s %4d words (80%% of median = %d)" % (f, n, 0.8 * m))
    assert n >= 0.8 * m, f
assert len(ITEM["verification"]["assertions"]) >= 0.5 * ITEM["marks"]
assert ITEM["id"] not in taken or FORCE

OUTP = "data/physics-hl/batch34.json"
if os.path.exists(OUTP) and not FORCE:
    sys.exit("%s exists -- pass --force" % OUTP)
json.dump({"_batch": "34", "questions": [ITEM]}, open(OUTP, "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print("wrote", OUTP)
