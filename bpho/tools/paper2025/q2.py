# -*- coding: utf-8 -*-
"""2025 Round 0 past paper — questions 6 to 10."""

QUESTIONS = [

{
    "id": "R0-06", "n": 6, "module": "H", "topic": "Cheapest network of exactly 4 Ω", "diff": 3,
    "rel": [
        ("H", "Resistors in series and in parallel"),
        ("H", "Equivalent resistance of a network"),
        ("A", "Searching a small space exhaustively instead of guessing"),
    ],
    "stem": "<p>A resistor shop sells individual resistors (the stock is unlimited). The price for each "
            "resistor is as follows: 2 Ω for £3, 3 Ω for £1, 6 Ω for £3, 8 Ω for £4, 12 Ω for £2.</p>"
            "<p>What is the least you would need to spend to make a combination of resistors equivalent to "
            "exactly 4 Ω?</p>",
    "fig": None,
    "opts": ["£3", "£4", "£5", "£6", "£7"],
    "ans": 1,
    "sol": """<p><b>What is being tested.</b> Whether you can search a small space of possibilities systematically. The physics — series and parallel — is trivial; the mark is for being organised under time pressure.</p>
<p><b>Step 1 — find the obvious solution so you know the price you have to beat.</b> The parallel combination that everyone spots is</p>
<div class="formula">6 Ω ∥ 12 Ω = (6 × 12)/(6 + 12) = 4 Ω,  cost £3 + £2 = £5</div>
<p>So the answer is at most £5. Options D (£6) and E (£7) can be ignored from here on, and the remaining question is whether £3 or £4 can do it.</p>
<p><b>Step 2 — ask what £3 can buy, exhaustively.</b> With £3 you can buy any of these (there is no change to save, so nothing else fits):</p>
<div class="formula">one 2 Ω (£3) or one 6 Ω (£3), or three 3 Ω (£3) or one 12 Ω + one 3 Ω (£3),
plus any network you like built only from 3 Ω resistors</div>
<p>Now list what each of those can actually make:</p>
<div class="formula">one 2 Ω                      → 2 Ω
one 6 Ω                      → 6 Ω
one 12 Ω                     → 12 Ω
one 12 Ω and one 3 Ω         → 15 Ω   or   2.4 Ω
one 3 Ω                      → 3 Ω
two 3 Ω                      → 6 Ω    or   1.5 Ω
three 3 Ω (any arrangement)  → 9 Ω, 4.5 Ω, 2 Ω, 1 Ω</div>
<p>Not one of those is 4 Ω, and nesting the network differently cannot help: with n identical equal resistors the achievable values are a short, fixed list, and a lone 2 Ω, 6 Ω or 12 Ω cannot be turned into 4 Ω by itself. <b>So £3 is impossible.</b></p>
<p><b>Step 3 — hit exactly £4.</b> Buy four 3 Ω resistors for £4 and put three of them in parallel:</p>
<div class="formula">three 3 Ω in parallel: 3 / 3 = 1 Ω
in series with the fourth:  1 Ω + 3 Ω = 4 Ω,  cost 4 × £1 = £4</div>
{{FIG:r0-06}}
<p>There is a second £4 solution, worth seeing because it shows the same price from a different direction: buy one 12 Ω and two 3 Ω, put the 3 Ω pair in series and that across the 12 Ω —</p>
<div class="formula">12 Ω ∥ (3 Ω + 3 Ω) = 12 Ω ∥ 6 Ω = 4 Ω,  cost £2 + £1 + £1 = £4</div>
<p><b>Answer: B, £4.</b></p>
<p><b>Why the other options are wrong.</b> A, £3, is impossible — the complete list above shows it. C, £5, is the answer for anyone who stops at the first combination they think of (6 Ω ∥ 12 Ω); it is a real solution, just not the cheapest. D, £6, is what you get by building 4 Ω out of two 2 Ω resistors in series, or three 12 Ω in parallel: correct, and twice the price. E, £7, is 3 Ω + (2 Ω ∥ 2 Ω), or many other dearer versions of the same idea.</p>
<p><b>The habit that makes this safe.</b> Price first, physics second. Establish an upper bound by finding any solution, then work upward from the cheapest purchase that could possibly do the job, and eliminate. One cheap combination that must be beaten plus one exhaustive list of what the cheaper budget can buy is a complete proof — and it takes less time than hoping a cleverer network will occur to you.</p>
<p><b>Relevant topics:</b> series and parallel resistors; equivalent resistance; systematic search under time pressure.</p>""",
    "trap": "Settling for £5 because <code>6 Ω ∥ 12 Ω = 4 Ω</code> springs to mind. Four 3 Ω resistors do it for £4 — three in parallel make 1 Ω, and one in series adds the other 3 Ω.",
},

{
    "id": "R0-07", "n": 7, "module": "B", "topic": "Relative velocity: catching up", "diff": 1,
    "rel": [
        ("B", "Relative velocity and closing speed"),
        ("B", "Motion at constant velocity: s = vt"),
        ("A", "Reading the direction of a velocity arrow"),
    ],
    "stem": "<p>Two particles A &amp; B travel along a straight line at a constant speed with velocities as shown in "
            "the diagram. Their initial separation is 18 m. How far does particle A travel before colliding with "
            "B?</p>{{FIG:r0-07}}",
    "fig": None,
    "opts": ["18 m", "27 m", "36 m", "45 m", "54 m"],
    "ans": 2,
    "sol": """<p><b>Read the arrows before you do any arithmetic.</b> Both velocity arrows point the same way: A moves at 6 m s⁻¹ with B ahead of it at 3 m s⁻¹. Same direction, so the gap closes only at the difference:</p>
<div class="formula">closing speed = 6 − 3 = 3 m s⁻¹</div>
<p><b>Step 1 — time to close 18 m at 3 m s⁻¹.</b></p>
<div class="formula">t = 18 / 3 = 6 s</div>
<p><b>Step 2 — how far A travels in that time.</b> A moves at its own 6 m s⁻¹, not at the closing speed:</p>
<div class="formula">s_A = 6 × 6 = 36 m</div>
<p><b>Answer: C, 36 m.</b></p>
<p><b>Check it in one line.</b> In 6 s, B travels <code>3 × 6 = 18 m</code>. A started 18 m behind, so it must travel B's 18 m plus the 18 m gap it has to make up:</p>
<div class="formula">s_A = 18 + 18 = 36 m   ✔</div>
<p>Both routes agree, which is the point of doing the check: the second one catches an error in the first if you have mixed up which speed belongs to whom.</p>
<p><b>The trap the paper is hunting.</b> If the two particles were approaching each other, the closing speed would be <code>6 + 3 = 9 m s⁻¹</code>, the time would be <code>18/9 = 2 s</code>, and A would travel 12 m. <b>12 m is not among the options.</b> That is deliberate: it is a signal, not an accident. If your working leads to 12 m, you have read the diagram as two particles approaching, and you should go back and look at the arrowheads rather than look for your answer in the list.</p>
<p><b>Where the other options come from.</b> A, 18 m, is the distance B travels in the same 6 s (or A's own share of the initial separation). D, 45 m, and E, 54 m, are the results of using the wrong speed for A: 54 m is <code>9 m s⁻¹ × 6 s</code> — the closing speed of a head-on approach carried through the correct same-direction time — and B, 27 m, is the mean of the two speeds (4.5 m s⁻¹) sustained for the full 6 s.</p>
<p><b>The general method for a catch-up question.</b> Set up <code>v_A t = v_B t + gap</code> and solve once. For this paper that is <code>6t = 3t + 18</code>, so <code>3t = 18</code>, <code>t = 6 s</code>, then substitute back for whichever distance is asked. One equation, no simultaneous reasoning, and it never confuses the two speeds.</p>
<p><b>Relevant topics:</b> relative velocity; constant-velocity kinematics; reading a velocity diagram.</p>""",
    "trap": "Adding the speeds and getting 12 m — which is not an option. The arrows show the particles travelling the same way, so the closing speed is 6 − 3 = 3 m s⁻¹.",
},

{
    "id": "R0-08", "n": 8, "module": "H", "topic": "Ideal voltmeter and ammeter readings", "diff": 3,
    "rel": [
        ("H", "Ideal ammeter (zero resistance) and ideal voltmeter (infinite resistance)"),
        ("H", "Series and parallel networks, emf and potential difference"),
        ("H", "Kirchhoff's laws without algebra"),
    ],
    "stem": "<p>A cell of emf <code>ε</code> (and negligible internal resistance) is connected to an ideal "
            "voltmeter, an ideal ammeter and three resistors <code>R</code> as shown below. What are the readings "
            "on the voltmeter and ammeter respectively?</p>{{FIG:r0-08}}",
    "fig": None,
    "opts": ["ε/3 , ε/(3R)", "ε/3 , ε/(2R)", "ε/3 , ε/R", "ε/2 , ε/(3R)", "ε/2 , ε/(2R)"],
    "ans": 4,
    "sol": """<p><b>What is being tested.</b> Whether you know what “ideal” means for each meter — and whether you can then see that two of the five drawn components are doing nothing at all.</p>
<p><b>Step 1 — let the meters simplify the circuit for you.</b></p>
<div class="formula">ideal ammeter:   resistance 0    ⇒ the branch it sits in is a short circuit
ideal voltmeter: resistance ∞    ⇒ the branch it sits in carries no current</div>
<p>The ammeter is in parallel with the bottom resistor, so that resistor has zero potential difference across it and carries no current. The voltmeter is in series in the bottom-left lead, so that lead carries no current either — and since it carries none, the junction it connects to is not fed from there. What survives is a single loop:</p>
<div class="formula">cell ε → top resistor R → right-hand node
right-hand node → (ammeter, 0 Ω) → middle node → middle resistor R → left-hand node → back to the cell</div>
<p><b>Step 2 — the loop.</b> Two resistors of <code>R</code> in series with the cell, so the total resistance is <code>2R</code> and the current is</p>
<div class="formula">I = ε / (2R)</div>
<p>Every element in that loop carries this same current, the ammeter included. So:</p>
<div class="formula">ammeter reading = I = ε / (2R)</div>
<p><b>Step 3 — the voltmeter.</b> It is connected across the middle resistor, whose resistance is <code>R</code> and whose current is <code>I</code>:</p>
<div class="formula">V = I R = (ε / 2R) × R = ε / 2</div>
<p><b>Answer: E — voltmeter ε/2, ammeter ε/(2R).</b></p>
<p><b>Cross-check by potential.</b> The cell lifts the potential by <code>ε</code>; the two equal resistors in the loop divide it equally, so each takes <code>ε/2</code>. The voltmeter spans one of them and reads <code>ε/2</code>. The bottom resistor, with no current, takes no share of the potential difference at all — which is exactly why it can be ignored.</p>
<p><b>Why the other options fail.</b> A, B and C all quote a current of <code>ε/(2R)</code> or <code>ε/R</code> paired with a voltmeter reading of <code>ε/3</code>. That <code>ε/3</code> comes from treating all three resistors as carrying the loop current and sharing the emf in three equal parts — which cannot happen, because the ammeter's zero resistance takes the bottom resistor out of the circuit. C and D pair a current with a voltage that belong to different assumptions about the network, and A assumes a total resistance of <code>3R</code>, i.e. the naive “three resistors in series”.</p>
<p><b>The habit to take away.</b> In any question with a meter drawn on it, ask two questions before you do anything else: which branch has <i>zero</i> resistance (that resistor is shorted out), and which branch has <i>infinite</i> resistance (that resistor carries nothing). Most “impossible” circuit questions in Round 0 are two-component questions wearing three resistors.</p>
<p><b>Relevant topics:</b> ideal meters; series and parallel networks; emf and potential difference; node reasoning.</p>""",
    "trap": "Using all three resistors and reading a total resistance of 3R. The ideal ammeter short-circuits the resistor beside it, so the cell drives current through two resistors, not three.",
},

{
    "id": "R0-09", "n": 9, "module": "F", "topic": "First-harmonic frequency against resistance", "diff": 3,
    "rel": [
        ("F", "Standing waves: f = (1/2L)√(T/μ)"),
        ("F", "Mass per unit length μ = ρA"),
        ("H", "Resistance of a uniform wire R = ρL/A"),
        ("A", "Ratio reasoning — the shared constants cancel"),
    ],
    "stem": "<p>Two uniform metal wires of the same length are made from the same material. Separately, the wires "
            "are subject to the same force on both ends, and the first harmonic frequency of each is measured. The "
            "frequencies are in the ratio 2 : 1. What is the ratio of their electrical resistances?</p>"
            "<p><i>[Hint: the speed of a transverse wave on a string is v = √(T/μ).]</i></p>",
    "fig": None,
    "opts": ["4 : 1", "3 : 1", "√3 : 1", "2 : 1", "√2 : 1"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> A two-step chain of proportionality — waves, through density, to electrical resistance — where every shared constant cancels, so you never need a value.</p>
<p><b>Step 1 — write the frequency in terms of the wire's geometry.</b> The first harmonic on a string fixed at both ends has half a wavelength along the wire, so</p>
<div class="formula">f = v / (2L),  v = √(T/μ),  μ = ρA

  ⇒  f = (1 / 2L) √( T / (ρA) )</div>
<p><b>Step 2 — keep only what differs.</b> The two wires share the length <code>L</code>, the tension <code>T</code>, the material (so <code>ρ</code> is the same) and the working frequency formula. Everything cancels except the cross-section:</p>
<div class="formula">f ∝ 1 / √A       ⇒       A ∝ 1 / f²</div>
<p><b>Step 3 — the frequency ratio becomes an area ratio.</b> With <code>f₁ : f₂ = 2 : 1</code>:</p>
<div class="formula">A₁ / A₂ = (1/f₁²) / (1/f₂²) = (f₂ / f₁)² = (1/2)² = 1/4</div>
<p>So wire 2 has four times the cross-sectional area of wire 1. The wire that sounds the higher note is the thinner one.</p>
<p><b>Step 4 — convert area into electrical resistance.</b> For a uniform wire of resistivity <code>ρ_e</code>,</p>
<div class="formula">R = ρ_e L / A   ⇒   R ∝ 1 / A  (same L, same material)
R₁ / R₂ = A₂ / A₁ = 4</div>
<p><b>Answer: A, 4 : 1.</b></p>
<p><b>The physical reading.</b> Doubling the frequency means quartering the area, and a quarter of the area is four times the resistance. Thin, high-pitched, high-resistance; thick, low-pitched, low-resistance. If your answer has the thicker wire with the higher frequency, or the ratio the wrong way up, this sentence tells you so without any algebra.</p>
<p><b>Why the other options are wrong — and a one-line argument that kills them all.</b> The chain above gives <code>R ∝ f²</code>, and the frequency ratio is 2, so the resistance ratio must be <code>2² = 4</code>. Only option A is 4 (or 1/4). D, 2 : 1, is what you get by forgetting the square in <code>A ∝ 1/f²</code> — that is, by treating the wave speed as independent of the cross-section, which would make the frequencies depend on nothing at all. E, √2 : 1, comes from applying the square root at the wrong stage of the chain; B and C are combinations that cannot arise from a chain of powers of the ratio 2.</p>
<p><b>The general method.</b> When a question gives you no numbers, write the quantity you want as a product of powers of the given quantities (<code>R ∝ fⁿ</code>), and read the exponent off the algebra. Then the ratio is <code>(ratio)ⁿ</code>. Nothing needs a calculator, and a slip in the exponents shows up immediately as a ratio that is not a power of the given one.</p>
<p><b>Relevant topics:</b> standing waves and the first harmonic; wave speed on a wire; mass per unit length; resistivity; ratio reasoning.</p>""",
    "trap": "Getting the ratio the wrong way up, or forgetting the square. The higher-pitched wire is thinner (f ∝ 1/√A) and thinner means more resistance, so R ∝ f² and the answer is 4 : 1.",
},

{
    "id": "R0-10", "n": 10, "module": "A", "topic": "Estimating the number of atoms in the Earth", "diff": 2,
    "rel": [
        ("A", "Order-of-magnitude estimation and powers of ten"),
        ("A", "Moles and Avogadro's number"),
        ("A", "Standard-form arithmetic without a calculator"),
    ],
    "stem": "<p>Estimate the number of atoms which make up the Earth.</p>",
    "fig": None,
    "opts": ["10⁵⁰", "10⁵⁵", "10⁶⁰", "10⁶⁵", "10⁷⁰"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> Whether you can turn a fact you know (the mass of the Earth) plus a fact you can make (the mass of a typical atom) into an order of magnitude — and whether you resist the urge to look for a calculator you are not allowed to have.</p>
<p><b>Step 1 — the mass of the Earth.</b> This is worth knowing as an anchor: <code>M⊕ ≈ 6 × 10²⁴ kg</code>.</p>
<p><b>Step 2 — the mass of a typical atom.</b> The Earth is mostly iron, oxygen, silicon and magnesium, so a typical nucleus has a mass number of a few tens; take <code>A ≈ 30</code>. One atomic mass unit is about <code>1.7 × 10⁻²⁷ kg</code>, so</p>
<div class="formula">m_atom ≈ 30 × 1.7 × 10⁻²⁷ kg ≈ 5 × 10⁻²⁶ kg</div>
<p><b>Step 3 — divide.</b></p>
<div class="formula">N = M / m_atom = (6 × 10²⁴) / (5 × 10⁻²⁶)
  = (6/5) × 10⁵⁰
  ≈ 1.2 × 10⁵⁰</div>
<p><b>Answer: A, about 10⁵⁰ atoms.</b></p>
<p><b>The same estimate through moles, which is faster if you are comfortable with Avogadro.</b> A mole of typical rock weighs about 30 g, so 1 kg of rock contains roughly <code>6 × 10²³ / 0.03 ≈ 2 × 10²⁵</code> atoms. Multiply by the mass of the Earth:</p>
<div class="formula">N ≈ (6 × 10²⁴ kg) × (2 × 10²⁵ atoms kg⁻¹) ≈ 1.2 × 10⁵⁰</div>
<p><b>Carry this anchor:</b> a kilogram of ordinary rock contains of order <code>10²⁵</code> atoms. It converts a hard question into one multiplication.</p>
<p><b>Why the answer does not depend on the composition.</b> Suppose the Earth were pure iron, <code>A = 56</code>: then <code>N ≈ 6.4 × 10⁴⁹</code>. Suppose it were pure oxygen, <code>A = 16</code>: <code>N ≈ 2.2 × 10⁵⁰</code>. Both are <code>10⁵⁰</code> to the nearest power of ten. The options differ by factors of <code>10⁵</code>, so an estimate good to within a factor of a hundred is easily enough — you are choosing between <code>10⁵⁰</code> and <code>10⁵⁵</code>, not between 1.2 and 1.3.</p>
<p><b>Where the other options come from.</b> <code>10⁵⁵</code> and beyond require an error of several orders of magnitude — the usual source is mishandling the atomic mass. Using the mass of a single nucleon (<code>1.7 × 10⁻²⁷ kg</code>) instead of an atom still lands you at <code>4 × 10⁵¹</code>, which is still nearest to <code>10⁵⁰</code>: that is the point about robustness. Only a slip in the exponents — writing the atomic mass as <code>10⁻²² kg</code>, say, or losing the <code>10²³</code> in Avogadro and treating it as <code>10²⁰</code> — gets you to <code>10⁵⁵</code> or beyond.</p>
<p><b>The technique.</b> In an estimation question, collect the powers of ten first and the leading digits second. Do not tidy up. <code>(6 × 10²⁴)/(5 × 10⁻²⁶)</code> is <code>(6/5) × 10⁵⁰</code> and that is already an answer to the precision the options demand.</p>
<p><b>Relevant topics:</b> estimation; Avogadro and the mole; standard form; rounding to an order of magnitude.</p>""",
    "trap": "Reaching for a calculator — which is not permitted. The options are five powers of ten apart, so all the question wants is the exponent, and that comes from (6 × 10²⁴)/(5 × 10⁻²⁶).",
},

]
