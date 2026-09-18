# -*- coding: utf-8 -*-
"""2025 Round 0 past paper — questions 1 to 5."""

QUESTIONS = [

{
    "id": "R0-01", "n": 1, "module": "E", "topic": "Work done stretching a wire", "diff": 1,
    "rel": [
        ("E", "Elastic strain energy: ½ × stress × strain × volume"),
        ("E", "Stress, strain and the Young modulus"),
        ("A", "Using units to eliminate options"),
    ],
    "stem": "<p>A uniform elastic wire of length <code>L</code> and cross-section <code>A</code> is subject to a "
            "tensile stress <code>σ</code>, which results in a tensile strain <code>ε</code>. Find the work done on "
            "the wire.</p>",
    "fig": None,
    "opts": ["LAσε", "σA / (εL)", "σL / (2εA)", "εA / (σL)", "½LAσε"],
    "ans": 4,
    "sol": """<p><b>What is being tested.</b> The factor of ½ in stored energy — where it comes from, and whether you check units before choosing between two options that differ by nothing else.</p>
<p><b>Step 1 — turn stress and strain into force and extension.</b> The definitions do the work for you:</p>
<div class="formula">σ = F / A   ⇒   F = σA          (the force on the wire)
ε = ΔL / L  ⇒   ΔL = εL         (how far it stretches)</div>
<p><b>Step 2 — the work done is the area under the force–extension graph.</b> A wire obeying Hooke's law does not jump to its full load: the force rises from zero to <code>σA</code> exactly in step with the extension growing from zero to <code>εL</code>. The graph is therefore a triangle, and the work done is its area:</p>
<div class="formula">W = ½ × base × height = ½ × (εL) × (σA) = ½ LAσε</div>
<p><b>Step 3 — the same answer from energy density, as a cross-check.</b> The strain energy stored per unit volume is <code>½σε</code>; multiply by the volume <code>AL</code> and you recover <code>½LAσε</code>. Two independent routes, one answer.</p>
{{FIG:r0-01}}
<p><b>Answer: E, ½LAσε.</b></p>
<p><b>Why the other four are wrong.</b> Option A is the same product with the ½ thrown away: <code>LAσε</code> is the work you would do if the wire took its full load from the first instant and never resisted gradually — which is precisely what an elastic body does not do. The other three are not energies at all. B, <code>σA/(εL)</code>, has the units of <code>N m⁻¹</code> — a stiffness. C, <code>σL/(2εA)</code>, has <code>N m⁻³</code>. D, <code>εA/(σL)</code>, has <code>m³ N⁻¹</code>. None of those is a joule.</p>
<p><b>Do it the fast way.</b> You never need the ½ versus no-½ decision to be a coin toss. Check the limiting case <code>ε → 0</code>: with no stretch, no work has been done, so the answer must vanish. B does the opposite — it diverges — and dies immediately. Then A and E are the only survivors, and the triangle versus rectangle argument settles them.</p>
<p><b>The wider point.</b> The ½ keeps appearing wherever two quantities grow together from zero: <code>½kx²</code>, <code>½mv²</code>, <code>½QV</code>, <code>½CV²</code>, and here <code>½σε</code> per unit volume. Any stored-energy expression with no ½ still on the table deserves a second look.</p>
<p><b>Relevant topics:</b> strain energy; stress and strain; dimensional checking.</p>""",
    "trap": "Picking <code>LAσε</code> and dropping the ½. The energy stored in a gradually loaded elastic wire is half the final force times the final extension.",
},

{
    "id": "R0-02", "n": 2, "module": "G", "topic": "Snell's law with angles measured from the surface", "diff": 1,
    "rel": [
        ("G", "Refraction and Snell's law"),
        ("G", "Refractive index and the normal"),
        ("A", "Reading the diagram before quoting a formula"),
    ],
    "stem": "<p>The diagram below shows the refraction of a light ray travelling from a medium with refractive "
            "index <code>n₁</code> into a medium with refractive index <code>n₂</code>. Which equation relates the "
            "angles <code>θ₁</code> and <code>θ₂</code>?</p>{{FIG:r0-02}}",
    "fig": None,
    "opts": ["n₁ sin θ₁ = n₂ sin θ₂", "n₁ sin θ₂ = n₂ sin θ₁", "n₁ cos θ₁ = n₂ cos θ₂",
             "n₁ cos θ₂ = n₂ cos θ₁", "n₁ sin θ₁ = n₂ cos θ₂"],
    "ans": 2,
    "sol": """<p><b>The whole question is in the diagram.</b> In this figure the two angles are drawn between each ray and the <b>surface</b>, not between each ray and the normal. Every textbook writes Snell's law in the normal form, and quoting it from memory is what makes this question catch people: option A is the formula you have written a hundred times, applied to angles that are not the ones it belongs to.</p>
<p><b>Convert, then use Snell.</b> Let <code>i</code> and <code>r</code> be the angles to the normal. Since the normal is perpendicular to the surface,</p>
<div class="formula">i = 90° − θ₁          r = 90° − θ₂
n₁ sin i = n₂ sin r
n₁ sin(90° − θ₁) = n₂ sin(90° − θ₂)
n₁ cos θ₁ = n₂ cos θ₂</div>
<p><b>Answer: C, n₁ cos θ₁ = n₂ cos θ₂.</b></p>
<p><b>Check it against a case you know.</b> The figure is drawn for <code>n₁ = 1.5</code> and <code>n₂ = 1</code> with <code>θ₁ = 60°</code>. Then <code>cos θ₂ = 1.5 × cos 60° = 0.75</code> — and <b>stop there</b>. You do not need θ₂ itself: “41.4°” is a number no one can produce without a calculator, and nothing in this question asks for it. What you need is only whether θ₂ is larger or smaller than θ₁, which <code>cos θ₂ = 0.75 &gt; cos 60° = 0.5</code> answers immediately: cos θ₂ is bigger, so θ₂ is the smaller angle, so the ray bent away from the normal. (Snell in the normal form says the same thing: <code>1.5 sin 30° = 0.75 = 1 × sin θ₂′</code> where θ₂′ = 48.6° from the normal — again a number you never have to write down.) The ray leaves the glass at a smaller angle to the surface, bending away from the normal — exactly as light does on the way out of a denser medium.</p>
<p><b>The limiting case that kills A.</b> Slide the incident ray down until it travels along the interface: <code>θ₁ → 90°</code>. In this picture that means the ray is travelling parallel to the boundary, and it should keep travelling parallel to it — nothing in the problem singles out either side. Option C gives <code>cos θ₁ → 0</code>, hence <code>cos θ₂ → 0</code>, hence <code>θ₂ → 90°</code>: still along the boundary. ✔ Option A would give <code>sin θ₂ = n₁/n₂</code>, a definite angle to the surface, so the same limiting ray would suddenly refract — nonsense.</p>
<p><b>Where the other options come from.</b> A is Snell's law with the angles to the normal — the wrong angles for this diagram. B is A with the refractive indices swapped. D is C with the indices swapped. E mixes a sine with a cosine, which no physical law does.</p>
<p><b>The transferable rule.</b> Before substituting into any standard formula, read which angle the diagram actually marks. A marked angle is a fact about the figure; a remembered formula is a fact about a different figure until you have checked the two agree.</p>
<p><b>Relevant topics:</b> refraction; Snell's law; refractive index; the small-angle and limiting-case checks.</p>""",
    "trap": "Answering with the remembered <code>n₁ sin θ₁ = n₂ sin θ₂</code>. The diagram measures both angles from the surface, so the equation is <code>n₁ cos θ₁ = n₂ cos θ₂</code>.",
},

{
    "id": "R0-03", "n": 3, "module": "A", "topic": "Which of these is not a unit of impulse", "diff": 2,
    "rel": [
        ("A", "Base units and derived-unit reduction"),
        ("C", "Impulse = Ft = change of momentum"),
        ("A", "Dimensional consistency"),
    ],
    "stem": "<p>Which of these is <b>not</b> a unit of impulse?</p>\n"
            "<table><tbody>"
            "<tr><td><b>A</b></td><td>N s</td><td><b>B</b></td><td>W s² m⁻¹</td><td><b>C</b></td><td>Pa m³</td></tr>"
            "<tr><td><b>D</b></td><td>kg m s⁻¹</td><td><b>E</b></td><td>C V s m⁻¹</td><td></td><td></td></tr>"
            "</tbody></table>",
    "fig": None,
    "opts": ["N s", "W s² m⁻¹", "Pa m³", "kg m s⁻¹", "C V s m⁻¹"],
    "ans": 2,
    "sol": """<p><b>Read the negative.</b> Three of the five are genuine units of impulse and you are asked for the odd one out. Note that this is a “which is not” question: a slip here costs a mark you had already earned.</p>
<p><b>Fix the target.</b> Impulse is force × time, and it equals the change in momentum, so its dimensions are those of momentum:</p>
<div class="formula">[impulse] = N s = kg m s⁻¹</div>
<p><b>Reduce all five to base units.</b> Use <code>N = kg m s⁻²</code>, <code>W = J s⁻¹ = kg m² s⁻³</code>, <code>Pa = N m⁻² = kg m⁻¹ s⁻²</code>, <code>C V = J = kg m² s⁻²</code>.</p>
<div class="formula">A  N s             = kg m s⁻² · s        = kg m s⁻¹   ✔
B  W s² m⁻¹       = kg m² s⁻³ · s² · m⁻¹ = kg m s⁻¹   ✔
C  Pa m³          = kg m⁻¹ s⁻² · m³     = kg m² s⁻²   ✘  (= J)
D  kg m s⁻¹                              = kg m s⁻¹   ✔
E  C V s m⁻¹      = kg m² s⁻² · s · m⁻¹ = kg m s⁻¹   ✔</div>
<p><b>Answer: C, Pa m³</b> — which reduces to the joule. Pascal cubic metres is a unit of energy (it is the work done by a pressure pushing out a volume), not of impulse.</p>
<p><b>Why B and E look wrong but are not.</b> They are the ones that make this question worth setting. B is a watt second squared per metre: the awkwardness is only in the presentation, not in the physics. E is a coulomb volt second per metre, and since a coulomb volt <i>is</i> a joule there is nothing exotic in it either. Both collapse to <code>kg m s⁻¹</code>. There are infinitely many combinations of units that do.</p>
<p><b>The technique that settles it in fifteen seconds.</b> Do not judge a unit by how familiar it looks. Convert it. Judge it only after it is in base units, and if a candidate contains a joule (or anything that reduces to one) you know immediately that it is energy, not momentum.</p>
<p><b>Relevant topics:</b> base and derived units; impulse and momentum; dimensional consistency.</p>""",
    "trap": "Rejecting <code>W s² m⁻¹</code> or <code>C V s m⁻¹</code> because they do not look like <code>N s</code>. Both reduce to <code>kg m s⁻¹</code>; it is <code>Pa m³</code> that reduces to an energy.",
},

{
    "id": "R0-04", "n": 4, "module": "K", "topic": "Alpha and beta accounting in a decay series", "diff": 1,
    "rel": [
        ("K", "Alpha and beta-minus decay"),
        ("K", "Conservation of mass number and charge"),
        ("K", "Decay series and the nuclear equation"),
    ],
    "stem": "<p>Uranium-238 (²³⁸₉₂U) decays to lead-206 (²⁰⁶₈₂Pb) via a series of alpha and beta minus decays "
            "only. How many beta minus decays occur in total?</p>",
    "fig": None,
    "opts": ["4", "6", "8", "10", "12"],
    "ans": 1,
    "sol": """<p><b>What is being tested.</b> That an alpha decay and a beta decay change the two nuclear numbers differently — and that a decay series has to balance both of them.</p>
<p><b>The two bookkeeping rules.</b> An alpha particle is a helium nucleus, so</p>
<div class="formula">alpha (α):   A → A − 4,   Z → Z − 2
beta minus (β⁻): A → A,      Z → Z + 1</div>
<p><b>Step 1 — count the alphas from the mass number.</b> Only alpha decay changes <code>A</code>, and each one removes 4:</p>
<div class="formula">ΔA = 238 − 206 = 32
number of alphas = 32 / 4 = 8</div>
<p><b>Step 2 — see where those eight alphas leave the charge.</b> Eight alphas remove <code>8 × 2 = 16</code> units of charge:</p>
<div class="formula">Z after the alphas = 92 − 16 = 76</div>
<p><b>Step 3 — close the gap with beta minus decays.</b> Lead-206 has <code>Z = 82</code>, so the series must gain <code>82 − 76 = 6</code> units of charge, and a beta minus decay is the only step here that adds one:</p>
<div class="formula">number of beta minus decays = 82 − 76 = 6</div>
<p><b>Answer: B, 6.</b></p>
<p><b>Check the whole equation.</b> Eight alphas and six beta-minuses:</p>
<div class="formula">A: 238 − 8(4) = 206            ✔
Z: 92 − 8(2) + 6(1) = 82       ✔</div>
<p>Both nuclear numbers balance, so the count is right.</p>
<p><b>Where the wrong options come from.</b> Option C, 8, is the number of alphas — the answer to a question that was not asked, and the commonest slip of all: the two numbers feel interchangeable but only one of them is 8. Options D, 10, and E, 12, come from arithmetic on the charge gap with the wrong particle: treating a beta decay as though it changed the charge by 2 (the alpha's step) gives <code>16/2 + … </code> type answers, and A, 4, is half the correct count, as if a beta decay carried two units of charge.</p>
<p><b>The wider point.</b> Every nuclear reaction balances <code>A</code> and <code>Z</code> separately. Do the two sums independently — mass number first, because only the alpha moves it, then charge — and then verify by adding both columns back up.</p>
<p><b>Relevant topics:</b> alpha and beta decay; conservation laws in nuclear decay; decay series.</p>""",
    "trap": "Reporting 8, the number of alpha decays. The question asks for the beta minus decays, which the charge balance alone fixes at 6.",
},

{
    "id": "R0-05", "n": 5, "module": "F", "topic": "Interference at a given path difference", "diff": 2,
    "rel": [
        ("F", "Superposition and path difference"),
        ("F", "Phase difference in radians and degrees"),
        ("F", "Coherence and the two-source conditions"),
    ],
    "stem": "<p>Two coherent waves of equal amplitude and wavelength 1.8 m, originating from the same source, "
            "arrive at the same detector with a path difference of 7.5 m. Which of these options describes the "
            "type of interference that occurs at the detector?</p>",
    "fig": None,
    "opts": ["fully destructive", "mostly destructive", "mostly constructive", "fully constructive",
             "not enough information"],
    "ans": 2,
    "sol": """<p><b>Turn the path difference into a number of wavelengths.</b> That single step decides everything:</p>
<div class="formula">Δx / λ = 7.5 / 1.8 = 75/18 = 25/6 = 4 + 1/6 wavelengths</div>
<p><b>Do that division as a fraction, not on a calculator.</b> 7.5/1.8 = 75/18; both divide by 3, so it is 25/6, and 25/6 = 4 remainder 1, so <b>4 whole wavelengths plus 1/6</b>. The “4” is what misleads people who reach for a decimal and see 4.1667. Keeping the fraction makes the remainder obvious — and the remainder is the only part that matters. Four whole wavelengths contribute nothing — a shift of a whole wavelength is a shift of a whole cycle. What is left over is the fractional part:</p>
<div class="formula">fractional part = 1/6 of a wavelength
phase difference = 2π × 1/6 = 60°</div>
<p><b>Six degrees of a cycle is a long way from half a cycle.</b> At 60° the two waves are much more in step than out of step. The resultant amplitude is</p>
<div class="formula">2A cos(φ/2) = 2A cos 30° = 1.73A</div>
<p>against <code>2A</code> for perfect reinforcement — 87% of it. That is “mostly constructive”.</p>
<p><b>Answer: C, mostly constructive.</b></p>
<p><b>Why not fully constructive.</b> That requires the path difference to be a whole number of wavelengths, and 25/6 is not a whole number. The test that makes this quick: compare the remainder 1/6 against the midpoint 1/4. Since 1/6 &lt; 1/4 (cross-multiply: 4 &lt; 6), the shift is closer to “in step” than to “out of step” — so the answer is “mostly”, on the constructive side. No decimal needed anywhere.</p>
<p><b>Why not E, not enough information.</b> The two waves are coherent, they come from the same source, and they arrive with equal amplitude. Given the wavelength and the path difference, the phase relationship at the detector is completely determined. What is <i>not</i> determined is the absolute amplitude — you cannot say the detector reads 1.73A without knowing A — but the question asks about the type of interference, which is a question about phase, and phase is fixed.</p>
<p><b>The general rule worth carrying into the exam.</b> Work in fractions of a wavelength: a whole number gives fully constructive, a half-odd number (<code>n + ½</code>) gives fully destructive, and anything else is “mostly” whichever side of the midpoint it falls. Then convert to radians (×2π) or degrees (×360°) only if the question asks for them.</p>
<p><b>Relevant topics:</b> superposition; path and phase difference; coherence; interference conditions.</p>""",
    "trap": "Turning 7.5/1.8 into 4.1667 on a calculator, rounding it to 4, and calling it fully constructive — or treating “from the same source” as a reason to doubt the information given.",
},

]
