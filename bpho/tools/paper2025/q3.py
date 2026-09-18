# -*- coding: utf-8 -*-
"""2025 Round 0 past paper — questions 11 to 15."""

QUESTIONS = [

{
    "id": "R0-11", "n": 11, "module": "L", "topic": "Counting the possible photon energies", "diff": 2,
    "rel": [
        ("L", "Energy levels and photon emission"),
        ("L", "hf = E₁ − E₂ for a transition"),
        ("A", "Counting combinations instead of listing them"),
    ],
    "stem": "<p>The first ten energy levels of an atom are labelled <code>n = 1, 2, …, 10</code>. Assuming all "
            "transitions are possible, find the maximum number of unique photon energies corresponding to "
            "transitions between <code>n = 10</code> and <code>n = 1</code>.</p>",
    "fig": None,
    "opts": ["45", "55", "90", "100", "110"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> Whether you can see that this is a counting question in disguise. There is no physics beyond <code>hf = E₁ − E₂</code>; the mark is for setting the count up correctly and not double-counting.</p>
<p><b>Step 1 — one photon per pair of levels.</b> The atom emits a photon when it drops from a higher level to a lower one, and the photon energy is fixed by which two levels are involved:</p>
<div class="formula">hf = E_upper − E_lower</div>
<p>So every pair of distinct levels contributes one possible photon energy. A pair, not an ordered pair: the transition from <code>n = 5</code> down to <code>n = 2</code> and the transition from <code>n = 2</code> up to <code>n = 5</code> describe the same energy gap, and only the downward one emits.</p>
<p><b>Step 2 — count the pairs.</b> With ten levels there are</p>
<div class="formula">C(10, 2) = 10 × 9 / 2 = 45</div>
<p>ways of choosing two distinct levels.</p>
<p><b>Answer: A, 45.</b></p>
<p><b>Where the word “maximum” comes from.</b> In a real atom two different pairs can happen to have the same energy gap, and then two transitions produce identical photons and the count of <i>unique</i> energies is smaller. The question says “maximum”, which tells you to assume no such coincidences: 45 is the largest the count can be, achieved when all 45 gaps are different.</p>
<p><b>Where the wrong options come from — and how to catch them.</b> All four of the others are products that count something slightly different:</p>
<div class="formula">100 = 10 × 10   ordered pairs including a level with itself (no transition)
 90 = 10 × 9     ordered pairs — each gap counted twice, once each way
110 = 11 × 10    ordered pairs across eleven levels
 55 = 11 × 10 / 2 the unbiased pair count, but with eleven levels instead of ten</div>
<p><b>Answer: A, 45.</b></p>
<p><b>The check that takes two seconds.</b> Whatever method you use, try it on three levels. Three levels give three pairs — 3→2, 3→1, 2→1 — so the formula must produce 3 when <code>n = 3</code>. <code>n(n−1)/2 = 3</code> ✔; <code>n² = 9</code> ✘; <code>n(n−1) = 6</code> ✘. Counting formulae are easy to verify on a tiny case and almost impossible to check by staring at them.</p>
<p><b>Relevant topics:</b> energy levels and photon energies; the transition rule; combinations and counting.</p>""",
    "trap": "Counting ordered pairs (90) or pairs including a level with itself (100). A photon energy belongs to an unordered pair of distinct levels: C(10,2) = 45.",
},

{
    "id": "R0-12", "n": 12, "module": "C", "topic": "How the energy of an explosion is shared", "diff": 3,
    "rel": [
        ("C", "Conservation of momentum in an explosion"),
        ("C", "Kinetic energy written as p²/2m"),
        ("A", "Testing an algebraic answer on limiting cases"),
    ],
    "stem": "<p>A body, initially at rest, explodes into two fragments of masses <code>m</code> and <code>am</code> "
            "where <code>a &gt; 1</code>. The total kinetic energy after the explosion is <code>E</code>. Find the "
            "kinetic energy of the larger mass.</p>",
    "fig": None,
    "opts": ["E/(1 + a)", "aE/(1 + a²)", "a²E/(1 + a²)", "a³E/(1 + a³)", "E/a"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> The consequence of momentum conservation in an explosion — and the discipline to test an algebraic answer rather than trust it.</p>
<p><b>Step 1 — the momenta are equal and opposite.</b> The body started at rest, so the total momentum is zero before and after. Call the speed of the smaller fragment <code>v₁</code> and of the larger <code>v₂</code>:</p>
<div class="formula">m v₁ = (am) v₂        ⇒        v₁ = a v₂</div>
<p>The lighter fragment is the faster one, by exactly the mass ratio.</p>
<p><b>Step 2 — write both kinetic energies through the shared momentum.</b> This is the step that makes the algebra clean. Both fragments carry the same magnitude of momentum, <code>p</code>, so use <code>KE = p²/2m</code>:</p>
<div class="formula">KE(small) = p² / (2m)
KE(large) = p² / (2am)</div>
<p>Same <code>p</code>, twice the mass, so the larger fragment takes the <i>smaller</i> share of the energy.</p>
<p><b>Step 3 — total, then ratio.</b></p>
<div class="formula">E = p²/(2m) + p²/(2am) = (p²/2m)(1 + 1/a) = (p²/2m) · (a + 1)/a</div>
<p>Divide the kinetic energy of the larger mass by the total:</p>
<div class="formula">KE(large) / E = [p²/(2am)] / [ (p²/2m)(a+1)/a ]
              = [1/(am)] × [am/(a+1)]
              = 1/(a + 1)</div>
<p><b>Answer: A, KE(larger) = E/(1 + a).</b></p>
<p><b>Test it the way you should test every algebraic answer — on the ends.</b></p>
<div class="formula">a → 1:  the masses are equal, so the energy splits equally.
        E/(1 + a) → E/2   ✔
a → ∞:  the big fragment is infinitely heavy, so it barely moves and
        takes almost no kinetic energy.  E/(1 + a) → 0   ✔</div>
<p>Both limits are right, and they already kill two options outright. Option C gives <code>E</code> as <code>a → ∞</code> — all the energy in the heaviest fragment, which is exactly backwards. Option D does the same. Option E, <code>E/a</code>, gives <code>E</code> at <code>a = 1</code>, where equal masses must split the energy equally: dead.</p>
<p><b>One numerical case to separate the last two.</b> The <code>a → 1</code> limit does not distinguish A from B, because <code>a/(1 + a²) → 1/2</code> as well. Put <code>a = 2</code>: masses <code>m</code> and <code>2m</code>, so <code>v₁ = 2v₂</code>, and the kinetic energies go as <code>m(2v)² = 4mv²</code> for the light one and <code>2m v²</code> for the heavy one — a 2:1 split, with the heavy fragment taking one third:</p>
<div class="formula">A:  E/(1 + 2) = E/3 = 0.333E        ✔
B:  2E/(1 + 4) = 0.400E            ✘</div>
<p><b>Answer: A.</b></p>
<p><b>The physical reading worth keeping.</b> Momentum is shared; energy is not. Two fragments of unequal mass fly apart with equal and opposite momenta, and because <code>KE = p²/2m</code>, the <i>lighter</i> fragment carries most of the kinetic energy. At <code>a = 2</code> the light fragment gets two thirds. Option B, <code>aE/(1+a²)</code>, is the value you get by assuming the energy is shared in proportion to mass — the misconception the question is built to detect.</p>
<p><b>Relevant topics:</b> momentum conservation in an explosion; kinetic energy in terms of momentum; limiting-case testing.</p>""",
    "trap": "Assuming the heavier fragment takes the larger share of the energy. Equal momenta and <code>KE = p²/2m</code> mean the heavier one takes <code>E/(1+a)</code> — less than half.",
},

{
    "id": "R0-13", "n": 13, "module": "A", "topic": "Casimir pressure by dimensions", "diff": 2,
    "rel": [
        ("A", "Dimensional analysis: forming a product from the given quantities"),
        ("A", "The dimensions of h, c and pressure"),
        ("L", "Quantum effects and the Casimir effect"),
    ],
    "stem": "<p>The pressure <code>p</code> exerted on two closely spaced parallel plates due to quantum effects "
            "is dependent only upon Planck's constant <code>h</code>, the speed of light <code>c</code> and the "
            "plate separation <code>r</code>. Find the proportionality relation between <code>p</code> and "
            "<code>r</code>.</p>",
    "fig": None,
    "opts": ["p ∝ 1/r", "p ∝ 1/r²", "p ∝ 1/r³", "p ∝ 1/r⁴", "p ∝ 1/r⁵"],
    "ans": 3,
    "sol": """<p><b>What is being tested.</b> Pure dimensional analysis — “dependent only upon” is the instruction to ignore the physics and match dimensions. AQA does not examine this, so it is cheap BPhO-specific marks.</p>
<p><b>Step 1 — write the dimensions of everything involved.</b></p>
<div class="formula">pressure   [p] = N m⁻² = kg m⁻¹ s⁻²  =  M L⁻¹ T⁻²
Planck     [h] = J s    = kg m² s⁻¹   =  M L² T⁻¹
light      [c] = m s⁻¹                =  L T⁻¹
separation [r] = m                    =  L</div>
<p><b>Step 2 — assume a product form and match each base dimension.</b> Put <code>p = k h^α c^β r^γ</code> with <code>k</code> a dimensionless constant:</p>
<div class="formula">M:   α = 1
L:   2α + β + γ = −1
T:  −α − β = −2</div>
<p><b>Step 3 — solve the columns in order.</b></p>
<div class="formula">from M:      α = 1
from T:      β = 2 − α = 1
from L:      γ = −1 − 2α − β = −1 − 2 − 1 = −4</div>
<p><b>Answer: D, p ∝ 1/r⁴.</b> The full form is <code>p = k h c / r⁴</code>, and the physics adds nothing to the exponent: the real result is <code>p = π²ħc / (240 r⁴)</code>.</p>
<p><b>Why the tidy answer is the right one.</b> If you have met the Casimir effect you may know that the force falls off as <code>1/r⁴</code>; dimensional analysis has just produced it without any quantum electrodynamics. That is the point of the technique, and it is why the question can be set at all in a non-calculator paper.</p>
<p><b>Where the neighbouring options come from.</b> Every wrong option is an offspring of one sign or one term in the L equation. Writing the length dimension of pressure as <code>+1</code> instead of <code>−1</code> — a pressure is a force per area, so the area's <code>m⁻²</code> is easy to drop — gives <code>2 + 1 + γ = +1</code>, so <code>γ = −2</code>: option B. Losing the <code>2α</code> contribution of <code>h</code> gives <code>β + γ = −1</code>, so <code>γ = −2</code> again. Adding instead of subtracting the <code>hc</code> contributions gives <code>γ = −5</code>: option E. Option C is the value you get with a single exponent error, and A is essentially unforced.</p>
<p><b>The technique, stated once for the whole paper.</b> Three base dimensions means three equations, which means you can solve for three unknown exponents. Write the four rows out in full — pressure, h, c, r — solve the mass row first because it is always the shortest, then time, then length. Do not try to do it in your head: the question is worth one mark and the tableau takes twenty seconds.</p>
<p><b>Relevant topics:</b> dimensional analysis; the dimensions of h and c; the Casimir effect as a quantum pressure.</p>""",
    "trap": "Getting one exponent wrong by writing the length dimension of pressure as positive. Force per area means <code>M L⁻¹ T⁻²</code>, and that <code>L⁻¹</code> is what makes the answer <code>1/r⁴</code> rather than <code>1/r²</code>.",
},

{
    "id": "R0-14", "n": 14, "module": "C", "topic": "How far a biscuit can be pushed before it falls", "diff": 3,
    "rel": [
        ("C", "Toppling and the centre of mass"),
        ("C", "Statics: stable equilibrium and the support condition"),
        ("A", "Geometry of intersecting circles; small-change reasoning"),
    ],
    "stem": "<p>A thin uniform circular biscuit of radius <code>b</code> is balanced horizontally on the thin "
            "circular rim of a teacup, which has radius <code>3b/2</code>, positioned as far as possible from the "
            "cup's centre. It is then slowly pushed inwards towards the centre of the teacup. What is the maximum "
            "distance it can be pushed before it falls?</p>",
    "fig": None,
    "opts": ["((√3 − 1)/2) b", "((5 − √3)/5) b", "((√5 − 2)/3) b", "((3 − √5)/2) b", "((√3 − 1)/3) b"],
    "ans": 3,
    "sol": """<p><b>What is being tested.</b> That “falling over” is a statement about the centre of mass and the shape of the support, not about how much of the biscuit is over the cup.</p>
<p><b>Step 1 — what is actually holding the biscuit up.</b> The cup's rim is a circle, not a disc, so the biscuit touches it only where the rim passes underneath: at the two points where the rim circle crosses the biscuit's edge. Call them P and Q. Those two points are the whole support, and by the standard toppling argument the biscuit stays up while its centre of mass lies inside the convex hull of the contact points — here the region bounded by the chord PQ and the arc between them.</p>
{{FIG:r0-14}}
<p><b>Step 2 — write that condition as a distance.</b> Let the cup's centre be O (rim radius <code>R = 3b/2</code>), the biscuit's centre of mass C (radius <code>b</code>), and <code>OC = d</code>. For two circles whose centres are <code>d</code> apart, the common chord — the line PQ — lies at distance</p>
<div class="formula">m = (d² + R² − b²) / (2d)</div>
<p>from O. The biscuit's centre of mass is at distance <code>d</code> from O, so the limiting position is</p>
<div class="formula">m = d   ⇒   d² + R² − b² = 2d²   ⇒   d² = R² − b²</div>
<p><b>Step 3 — evaluate with R = 3b/2.</b></p>
<div class="formula">d_min = √(R² − b²) = √(9b²/4 − b²) = √(5b²/4) = (√5 / 2) b ≈ 1.118 b</div>
<p><b>Step 4 — where does it start?</b> “As far as possible from the cup's centre” while still balanced means the centre of mass is over the rim itself:</p>
<div class="formula">d_start = R = 1.5 b</div>
<p>(You can check the sense of that against Step 3: <code>d_start = 1.5b &gt; d_min = 1.118b</code>, so there is room to push.)</p>
<p><b>Step 5 — subtract.</b></p>
<div class="formula">distance pushed = d_start − d_min = 1.5b − (√5/2) b = ((3 − √5)/2) b ≈ 0.382 b</div>
<p><b>Answer: D, ((3 − √5)/2) b.</b></p>
<p><b>Getting there without a calculator.</b> The options are decimals, so at the very end you do have to
turn a surd into one — but you never need long division. Recover <code>√5</code> by squaring candidates:
<code>2.2² = 4.84</code> (too small), <code>2.3² = 5.29</code> (too big), <code>2.24² = 5.018</code>
(just over), so <code>√5 ≈ 2.236</code>. Then</p>
<div class="formula">(3 − √5)/2 ≈ (3 − 2.236)/2 = 0.764/2 = 0.382</div>
<p>and 0.382 is option D. Notice what you did <i>not</i> need: <code>1.118b</code> in Step 3, any decimal
for <code>√(5)/2</code>, or a single division harder than halving 0.764.</p>
<p><b>The stronger check, which needs no number at all.</b> Square to compare instead of evaluating. The
answer must be <code>(3 − √5)/2</code>, so it must satisfy <code>√5 = 3 − 2×</code>(the answer). Test
option A, 0.366: <code>3 − 2(0.366) = 2.268</code>, and <code>2.268² = 5.14 ≠ 5</code>. Test option D,
0.382: <code>3 − 2(0.382) = 2.236</code>, and <code>2.236² = 5.00</code> ✓. Squaring settles it exactly,
and it is the technique to reach for whenever the options are decimals but the answer is a surd.</p>
<p><b>The limiting case that checks the whole derivation.</b> Make the cup exactly as wide as the biscuit: <code>R = b</code>. Then the general result gives</p>
<div class="formula">d_min = √(R² − b²) = 0,  so the push is R − 0 = b</div>
<p>A biscuit the size of the rim can be pushed a full radius off centre before it topples — it is supported until its centre reaches the rim's centre. That is clearly right, and only an expression built on <code>√(R² − b²)</code> behaves that way.</p>
<p><b>Why the other options are wrong.</b> All four are of the same shape — a surd over a small integer — so they cannot be separated by inspection. The two checks above do it: the answer must be smaller than <code>1.5b</code>, must vanish in the limit <code>b = R</code>, and evaluates at <code>0.382b</code>. Option A, 0.366b, is close enough to tempt you and comes from using <code>√3</code> in place of <code>√5</code>, i.e. from a wrong chord relation; B, 0.654b, is much too large; C, 0.079b, is much too small; E, 0.244b, sits between but fails the <code>b = R</code> test. Doing the general case first — <code>d_min = √(R² − b²)</code> before substituting — is what makes this safe, because the general form can be checked against an easy case and the specific numbers cannot.</p>
<p><b>The habit.</b> In any toppling question, ask first: what are the contact points, and what is the shape whose inside the centre of mass must lie in? A pencil on a table has one line of contact and falls at once; a box has an area and falls when its centre passes the edge; here the contact is an arc, and the answer is a chord condition. The shape of the support is the whole question.</p>
<p><b>Relevant topics:</b> toppling and the centre of mass; stable equilibrium; the geometry of intersecting circles.</p>""",
    "trap": "Treating the support as the overlap area between the biscuit and the cup. The rim is a circle, so the support is the arc where the rim passes under the biscuit, and balance fails when the centre of mass reaches the chord joining those two points.",
},

{
    "id": "R0-15", "n": 15, "module": "J", "topic": "How many ice cubes the water can melt", "diff": 2,
    "rel": [
        ("J", "Specific heat capacity and Q = mcΔT"),
        ("J", "Specific latent heat of fusion and Q = mL"),
        ("A", "Integer answers and no-calculator arithmetic"),
    ],
    "stem": "<p>An insulated cup contains 500 g of water at 20 °C. Identical ice cubes, each of mass 25 g and at "
            "0 °C, are added to the cup. What is the maximum number of cubes that can be added so that, at "
            "equilibrium, the mixture is entirely liquid?</p>"
            "<p>Specific heat capacity of water = 4 × 10³ J kg⁻¹ K⁻¹<br>"
            "Specific latent heat of fusion of ice = 3 × 10⁵ J kg⁻¹</p>",
    "fig": None,
    "opts": ["4", "5", "6", "7", "8"],
    "ans": 1,
    "sol": """<p><b>What is being tested.</b> The two-stage thermal calculation — cool the water, melt the ice — and the discipline to keep an integer answer an integer.</p>
<p><b>Step 1 — how much energy the water can give up.</b> The best case for melting ice is that the water is cooled all the way to 0 °C:</p>
<div class="formula">Q_available = mcΔT = 0.5 kg × (4 × 10³ J kg⁻¹ K⁻¹) × 20 K
            = 4.0 × 10⁴ J</div>
<p><b>Step 2 — what one cube costs to melt.</b> Ice at 0 °C needs no warming; it only needs melting:</p>
<div class="formula">Q_per cube = mL = 0.025 kg × (3 × 10⁵ J kg⁻¹) = 7.5 × 10³ J</div>
<p><b>Step 3 — divide, then round <i>down</i>.</b></p>
<div class="formula">n_max = (4.0 × 10⁴) / (7.5 × 10³) = 5.33…</div>
<p>The mixture must be <b>entirely liquid</b> at equilibrium, so there must be no ice left. Six cubes would need <code>6 × 7.5 × 10³ = 4.5 × 10⁴ J</code>, more than the water can supply, so some ice would survive at 0 °C and the mixture would be part ice. Five cubes is the largest number that can be fully melted.</p>
<p><b>Answer: B, 5.</b></p>
<p><b>Check that the fifth cube really does melt, and what is left over.</b> Five cubes cost <code>5 × 7.5 × 10³ = 3.75 × 10⁴ J</code>, leaving</p>
<div class="formula">Q_left = 4.0 × 10⁴ − 3.75 × 10⁴ = 2.5 × 10³ J</div>
<p>The final mixture is <code>0.500 + 5 × 0.025 = 0.625 kg</code> of water, and 2.5 × 10³ J warms it by</p>
<div class="formula">ΔT = Q / (mc) = 2.5 × 10³ / (0.625 × 4 × 10³) ≈ 1 °C</div>
<p>So the cup settles at about 1 °C, all liquid, with the whole calculation consistent. That is a useful thing to notice: the paper's rounded data (<code>4 × 10³</code> rather than 4200) makes the fifth-cube case land very close to 0 °C, which is exactly what “maximum” means.</p>
<p><b>Why the other options are wrong.</b> C, 6, is the rounding error the question is built around: <code>5.33</code> rounds to 5 for a physical count, and rounding it up to 6 leaves ice floating in the cup — with the mixture then not entirely liquid, which is the condition the question set. D, 7, and E, 8, would leave several cubes of ice. A, 4, is what you get by making one of the two calculations slightly harder for yourself — for example by cooling the water only to some intermediate temperature, or by including a warming term for the melted ice when there is no energy left to do it.</p>
<p><b>The general shape of a melting-ice question.</b> Energy available: <code>m_water c ΔT</code>. Energy cost: <code>m_ice L</code> (plus <code>m_ice c ΔT</code> afterwards, if the melt-water ends above 0 °C). The limiting number of cubes comes from dividing the first by the second and rounding towards zero whenever the question insists that nothing solid is left. Watch the units in one place: the mass must be in kilograms for both formulae, and 500 g and 25 g both invite you to forget that.</p>
<p><b>Relevant topics:</b> specific heat capacity; latent heat of fusion; two-stage thermal equilibrium; integer constraints.</p>""",
    "trap": "Rounding 5.33 up to 6. Six cubes need more energy than the water has, so ice would be left at 0 °C and the mixture would not be entirely liquid.",
},

]
