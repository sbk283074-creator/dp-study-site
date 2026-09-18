# -*- coding: utf-8 -*-
"""Key-point lessons, part A: the toolkit (module A) and mechanics (B, C, D).

Each concept is written for someone who has met none of it before. `stage` is the
reading level used to order the course; `pre` lists concepts that must be read first.
"""

C = []


def c(i, m, stage, title, pre, summary, body, used):
    C.append(dict(id=i, m=m, stage=stage, t=title, pre=pre, one=summary, body=body.strip(), used=used))


# ───────────────────────────── STAGE 0 · THE TOOLKIT ─────────────────────────────

c("nocalc", "A", 0, "The paper is non-calculator: six ways to get a number by hand", [],
  "No calculator is allowed, so the paper is built so that every answer is reachable by exact algebra, by bracketing, or from a handful of memorised constants.",
  """
<p><b>The rule.</b> Round 0 is 25 questions in 60 minutes with <b>no calculator</b>. That is not an
extra hardship bolted onto the paper — it is a design constraint, and the examiners honour it. It means
every question has a route that never needs you to multiply two three-digit numbers or evaluate an
awkward trig function. If your route needs a calculator, you have missed the intended one. Treat that as
a signal, not as bad luck.</p>

<p><b>1 · Cancel before you multiply.</b> Almost never substitute numbers early. Keep symbols, cancel
what cancels, and only put numbers in at the very end. In this paper most questions collapse to a ratio
in which every awkward constant cancels — that is the whole point of “ratio reasoning”.</p>

<p><b>2 · Keep surds and fractions exact.</b> Write <code>√5/2</code>, not <code>1.118</code>, and
<code>7/12</code>, not <code>0.583</code>. Exact forms compare exactly; decimals compare approximately
and cost you time. Convert to a decimal only on the last line, and only if the options are decimals.</p>

<p><b>3 · To compare two positive quantities, square them.</b> This removes every square root:</p>
<div class="formula">compare 4/√7  with  √2  ?
(4/√7)<sup>2</sup> = 16/7 = 2.286      (√2)<sup>2</sup> = 2
2.286 &gt; 2       =&gt;       4/√7 &gt; √2</div>
<p>Both sides positive, so squaring preserves the order. No root evaluated, nothing memorised. The same
trick orders <code>√3</code>, <code>√5</code>, <code>2</code> or checks whether a candidate answer is
above or below a bound.</p>

<p><b>4 · Compare fractions by cross-multiplying.</b> To decide whether <code>7/12 &lt; 7/8</code>,
compare <code>7 × 8 = 56</code> with <code>7 × 12 = 84</code>: since 56 &lt; 84, <code>7/12 &lt; 7/8</code>.
Never find a common denominator, and never reach for a decimal.</p>

<p><b>5 · Bracket and eliminate — the strongest technique here.</b> You usually do not need the number,
only to know which <i>option</i> it is. Build two crude bounds you can compute instantly and keep only
the option between them:</p>
<div class="formula">4<sup>-0.85</sup>:  the exponent -0.85 lies between -1 and -0.5
4<sup>-1</sup>  = 1/4  = 0.25
4<sup>-1/2</sup> = 1/2  = 0.50
=&gt;  0.25 &lt; 4<sup>-0.85</sup> &lt; 0.50,  and -0.85 is nearer -1
=&gt;  about 0.3.  Options: 0.1, 0.3, 0.5, 0.7, 0.9  =&gt;  B, uniquely.</div>
<p>Two powers of a half, and the question is finished. This is why the options are spaced so widely: they
are meant to be separated by bounds, not by computation.</p>

<p><b>6 · Bound a logarithm rather than evaluate it.</b> You never need <code>log₂3</code>; you need to
know where it sits. Trap 3 between two powers of 2 you can compute:</p>
<div class="formula">2<sup>1.5</sup> = 2√2 ≈ 2.83 &lt; 3 &lt; 2<sup>2</sup> = 4
=&gt;  1.5 &lt; log₂3 &lt; 2
=&gt;  0.5 &lt; log₂(3/2) &lt; 1</div>
<p>That is enough to identify the answer and to reject its neighbours.</p>

<p><b>The constants worth having in your head.</b> You are allowed to know these; the paper gives you
<code>c</code>, <code>e</code>, <code>g</code> and <code>h</code> on the formula sheet:</p>
<div class="formula">√2 = 1.414      √3 = 1.732      √5 = 2.236      √10 = 3.162
π  = 3.14       g  ≈ 10 (use 9.8 only when the options are tight)
2<sup>10</sup> = 1024     ln 2 = 0.693     log₁₀2 = 0.301
sin 30° = ½     sin 45° = 1/√2   sin 60° = √3/2   (same row for cos, reversed)</div>
<p>And one recovery trick: if you need <code>√5</code> and have forgotten it, square candidates.
<code>2.2² = 4.84</code> is low, <code>2.3² = 5.29</code> is high, <code>2.24² = 5.018</code> — so
<code>√5 ≈ 2.236</code>. Squaring is always available when memory is not.</p>

<p><b>Traps.</b> Reaching for decimals out of habit, which costs accuracy and time at once. Substituting
<i>g</i> = 9.8 when the options only differ at one significant figure (use 10, and check with 9.8 only if
two options survive). Evaluating an angle you do not need — in the refraction questions the answer is a
ratio of path lengths, and <code>θ₂</code> never has to be written down. And the worst one: doing a long
multiplication, getting 4.1667, and then rounding it to 4 when what mattered was the fraction
<code>25/6 = 4 + 1/6</code>.</p>
""",
  "Used by the questions where the arithmetic itself is the discriminator: Q5 (keep 25/6 as a fraction), Q14 (√5 by squaring), Q16 (compare by squaring), Q19 (bound the log), Q22 (√√3), Q23 (bracket 4<sup>-0.85</sup>), Q25 (order five fractions).")

c("units", "A", 0, "Quantities, base units and derived units", [],
  "Every physical quantity is a number times a unit, and every unit can be written using seven base units.",
  """
<p>Physics does not measure bare numbers. It measures <b>quantities</b>, and a quantity is always
a number <i>multiplied by a unit</i>: “the length is 3” is meaningless, “the length is 3 metres” is not.
You can treat units like algebraic symbols — multiply them, divide them, cancel them — which is the single
most useful habit in this whole paper.</p>

<p>Seven units are chosen as <b>base units</b> and everything else is built from them. You only need five
here:</p>
<div class="formula">metre      m     length
kilogram   kg    mass
second     s     time
ampere     A     electric current
kelvin     K     temperature</div>

<p>Every other unit is <b>derived</b>, meaning it is defined by an equation that ties it to the base units.
The definitions below are not extra facts to memorise — each one is just an equation you already know,
turned into units:</p>
<div class="formula">force (newton, N)        F = ma            N    = kg m s⁻²
energy (joule, J)        W = Fs            J    = N m    = kg m² s⁻²
power (watt, W)          P = E/t           W    = J s⁻¹  = kg m² s⁻³
pressure (pascal, Pa)    p = F/A           Pa   = N m⁻²  = kg m⁻¹ s⁻²
charge (coulomb, C)      Q = It            C    = A s
potential diff (volt, V) V = E/Q           V    = J C⁻¹  = kg m² s⁻³ A⁻¹
resistance (ohm, Ω)      R = V/I           Ω    = V A⁻¹  = kg m² s⁻³ A⁻²</div>

<p><b>The technique.</b> To find out what a complicated combination of units really is, replace each unit
by its base-unit definition and cancel. Worked example — is <b>W s² m⁻¹</b> a unit of impulse?</p>
<div class="formula">W s² m⁻¹ = (kg m² s⁻³)(s²)(m⁻¹)
         = kg · m²⁻¹ · s⁻³⁺²
         = kg m s⁻¹</div>
<p>Impulse is force × time, so its unit is N s = (kg m s⁻²)(s) = kg m s⁻¹. It matches, so W s² m⁻¹
<i>is</i> a unit of impulse. Nothing was computed numerically — only units were manipulated.</p>

<p><b>Traps.</b> Kilogram is a unit of <i>mass</i>, not of force or weight — the weight of 1 kg is about
9.8 N. And a symbol can mean different things in different places: W is both the unit watt and the
algebraic symbol for work or weight, so read the surrounding text.</p>
""",
  "Q3 asks which option is <i>not</i> a unit of impulse. Every option has to be reduced to base units — including "
  "C V s m⁻¹, which needs the volt definition twice over.")

c("units-elim", "A", 0, "Using units to throw away wrong options", ["units"],
  "Before doing any physics on a multiple-choice question, check which options even have the right units — most papers have a question that dies this way.",
  """
<p>In a five-option question the answer has to have the units of the quantity asked for. Work out those
units first, then test each option. Often three or four options collapse immediately, and the question
becomes trivial.</p>

<p><b>Example (Q1).</b> “Find the work done on the wire.” Work is energy, so the answer must come out in
joules, J = N m. The options are built from stress σ (unit Pa = N m⁻²), strain ε (no unit — it is a ratio
of two lengths), length L (m) and area A (m²):</p>
<div class="formula">σA      → (N m⁻²)(m²)      = N          ← a force, not an energy
σL      → (N m⁻²)(m)       = N m⁻¹     ← neither
εA      → (m²)             = m²        ← an area
½LAσε   → (m)(m²)(N m⁻²)   = N m = J   ← energy ✓</div>
<p>Only one option is an energy at all, so it must be the answer — and you never needed to know the
formula for strain energy. Note that a pure number like ½ carries no units, so it can never rescue an
option whose units are wrong.</p>

<p><b>Why it is safe.</b> An equation that is dimensionally wrong can never be physically right, so
eliminating by units never removes the true answer. It can only fail to narrow things down — in which
case you have lost five seconds.</p>

<p><b>Traps.</b> Angles, strains, refractive indices and ratios are dimensionless, so they vanish from the
check; and a constant such as ½, π or √2 is dimensionless too. Do not expect every option to contain
them.</p>
""",
  "Q1: four of the five options are not energies, so the answer is forced without using the strain-energy formula.")

c("dimensions", "A", 0, "Dimensions: checking and building formulas", ["units"],
  "Dimensions are units with the sizes stripped away; they let you check an equation you half-remember and, better, build one you have never seen.",
  """
<p>A <b>dimension</b> is the <i>kind</i> of quantity something is, written in square brackets and ignoring
numerical factors: [mass] = M, [length] = L, [time] = T, [current] = I. So the newton has dimensions
MLT⁻² whatever units you measure it in.</p>

<p><b>Use 1 — checking.</b> Both sides of any equation must have the same dimensions, and so must all the
terms you add or subtract. This catches sign errors, missing squares and mis-remembered formulas without
any numbers at all.</p>

<p><b>Use 2 — building.</b> If you are told “the pressure depends only on h, c and r”, then
p = (a constant) × h<sup>α</sup> c<sup>β</sup> r<sup>γ</sup> and you can find α, β, γ by matching
dimensions. Write down what you have:</p>
<div class="formula">[p] = M L⁻¹ T⁻²        (pressure = force/area)
[h] = M L² T⁻¹         ( Planck's constant: energy × time, or from E = hf )
[c] = L T⁻¹            (speed)
[r] = L                (separation)</div>
<p>Now substitute and collect up each of M, L, T:</p>
<div class="formula">M L⁻¹ T⁻² = (M L² T⁻¹)ᵃ (L T⁻¹)ᵇ (L)ᶜ
          = Mᵃ · L²ᵃ⁺ᵇ⁺ᶜ · T⁻ᵃ⁻ᵇ
M:   1 =  a
L:  −1 =  2a + b + c
T:  −2 = −a − b</div>
<p>Three equations, three unknowns: a = 1, then b = 1 from the T equation, then c = −4 from the L equation.
So p ∝ h c / r⁴ — the pressure falls off extremely fast, which is why the effect is only measurable at
sub-micron separations. No physics beyond the dimensions of p, h and c was needed.</p>

<p><b>Traps.</b> A dimensionally correct answer need not be right: any dimensionless constant (2, π, ½)
is invisible to this method, and 2πr and r are “the same” dimensionally. Also, sums of quantities must
match term by term — you cannot add a length to an area.</p>
""",
  "Q13 is pure dimensional analysis: the Casimir pressure from h, c and r. The exponents fall out of three simultaneous equations.")

c("stdform", "A", 0, "Standard form and arithmetic with powers of ten", [],
  "Round 0 is non-calculator, so huge and tiny numbers are handled by tracking the power of ten separately from the digits.",
  """
<p>A number in <b>standard form</b> is a × 10<sup>n</sup> where 1 ≤ a &lt; 10. The whole point is that you
can then do the digits and the powers separately:</p>
<div class="formula">multiply:  add the exponents      (2×10³)(3×10⁵) = 6×10⁸
divide:    subtract them          6×10⁸ / 3×10⁵ = 2×10³
power:     multiply the exponent  (2×10³)² = 4×10⁶
root:      halve the exponent     √(9×10⁶) = 3×10³</div>
<p>When a root or a division leaves you with 0.5 × 10<sup>n</sup>, borrow one power of ten from the
exponent: 0.5 × 10⁷ = 5 × 10⁶. And when multiplying gives 60 × 10⁸, carry: 6 × 10⁹.</p>

<p><b>Only keep one significant figure</b> in an estimate. In this paper the options are usually a factor
of 10⁵ apart, so anything more precise is wasted effort and wasted time.</p>

<p><b>A scale to anchor yourself.</b> It is worth knowing a few reference sizes so estimates can be
checked: an atom is about 10⁻¹⁰ m across, a nucleus about 10⁻¹⁵ m; a person is 10² kg and 10⁰ m; the
Earth is about 10⁷ m across and 10²⁵ kg; the Sun is 10³⁰ kg; the age of the universe is about 10¹⁷ s.
Anything you compute can be sanity-checked against these.</p>
""",
  "Q10 needs the volume of the Earth, a mass, and a division by atomic mass — all in powers of ten, no calculator.")

c("estimate", "A", 0, "Order-of-magnitude estimation (Fermi problems)", ["stdform"],
  "An estimate is a calculation where you are only chasing the power of ten, so you are allowed to be brutally rough about everything else.",
  """
<p>An <b>order-of-magnitude</b> question is not asking for the right answer; it is asking whether you can
get to within a factor of ten. The method is always the same:</p>
<ul>
<li>Write the quantity you want as a <b>product of things you can guess</b>.</li>
<li>Guess each one to the nearest power of ten only.</li>
<li>Multiply the powers of ten by adding the exponents.</li>
<li>Sanity-check against something you know.</li>
</ul>
<p><b>Example: how many atoms make up the Earth?</b> Split it into “how many moles” and “how many atoms
per mole”:</p>
<div class="formula">mass of Earth      ≈ 6 × 10²⁴ kg      → 10²⁵ kg
mass of one atom   ≈ 10⁻²⁶ kg         (roughly 10–100 × the proton mass 1.7×10⁻²⁷ kg)
number of atoms    ≈ 10²⁵ / 10⁻²⁶ = 10⁵¹</div>
<p>The options are 10⁵⁰, 10⁵⁵, 10⁶⁰, 10⁶⁵, 10⁷⁰ — the nearest is 10⁵⁰. Notice how far apart the options
are: being out by a factor of 3 changes nothing, being out by 10⁵ does. That is what makes this style of
question safe to answer quickly.</p>

<p><b>Traps.</b> Do not use the density of water for rock (rock is a few times denser — fine at this
precision); do not forget that the Earth is a sphere so the volume has a ⁴⁄₃π in it (about 4, i.e. less
than one power of ten — fine); and do not confuse the mass of an atom with the mass of a nucleon by more
than a factor of 100.</p>
""",
  "Q10 is the classic: Earth mass ÷ mass per atom, with options spread five powers of ten apart.")

c("moles", "A", 0, "Moles, Avogadro's number and counting atoms", ["stdform"],
  "The mole is just a counting unit, like a dozen — it lets you go from a mass you can weigh to a number of atoms you cannot.",
  """
<p>Atoms are far too small to count, so chemists count them in bundles. One <b>mole</b> is
6.02 × 10²³ particles — <b>Avogadro's number</b>, N<sub>A</sub>. That number is chosen so that one mole
of a substance has a mass in grams equal to its <b>relative atomic mass</b> (the number under the element
in the periodic table): carbon-12 has relative atomic mass 12, so 12 g of carbon is exactly one mole and
contains 6.02 × 10²³ atoms.</p>

<p>The only formula you need is a two-step conversion:</p>
<div class="formula">moles  n = mass / molar mass          (molar mass M in g mol⁻¹)
number of particles N = n × N_A</div>
<p>So a two-step chain: <b>mass → moles → number of atoms</b>. For a compound, add up the relative atomic
masses to get the molar mass (water: 2×1 + 16 = 18 g mol⁻¹), and remember that one mole of H₂O contains
one mole of oxygen atoms but two moles of hydrogen atoms.</p>

<p>Worked example — how many atoms in 54 g of water? Moles of water = 54/18 = 3 mol. Each water molecule
has 3 atoms, so moles of atoms = 9 mol. Number of atoms = 9 × 6 × 10²³ ≈ 5 × 10²⁴.</p>

<p><b>Traps.</b> Grams, not kilograms, go with molar mass — mixing them is the classic order-of-magnitude
error (a factor of 1000). And “number of atoms” is not “number of molecules”: multiply by the number of
atoms per molecule.</p>
""",
  "Q10: converting the Earth's mass into a number of atoms runs through moles, or you can bypass it with one atomic mass.")

c("ratio", "A", 0, "Ratio reasoning: let the constants cancel", [],
  "Instead of computing two quantities and dividing, write each as a formula, divide the formulas, and watch the awkward constants disappear.",
  """
<p>When a question asks “by what factor does X change?”, do <b>not</b> calculate X twice. Write X as a
formula, write the ratio, and cancel everything that did not change. This is faster, it is exact, and it
does not need a calculator.</p>

<p><b>Example (Q22, conical pendulum).</b> The string angle goes from 30° to 60° and you want the factor
by which the angular frequency must increase. The formula is ω² = g/(ℓ cos θ) — but you do not need to
believe that yet. Just take the ratio:</p>
<div class="formula">ω₂² / ω₁² = [ g / (ℓ cos 60°) ] / [ g / (ℓ cos 30°) ]
          = cos 30° / cos 60°
          = (√3/2) / (1/2)  = √3
so  ω₂ / ω₁ = √√3</div>
<p>g and ℓ vanished without ever being given values. That is the whole trick: <b>g, m, L, ρ, π and every
other shared constant cancels in a ratio</b>, and square roots of the ratio are how square-rooted
formulas behave.</p>

<p><b>Traps.</b> If the quantity sits under a square root, take the square root of the ratio too — this is
where most candidates lose the mark. And check the direction: “increased <i>by a factor</i>” means
multiply, whereas answering with the ratio the wrong way up gives you the reciprocal.</p>
""",
  "Q9, Q21, Q22 and Q25 are all settled by a ratio rather than a calculation; Q9's answer 4:1 comes from f ∝ 1/R.")

c("surds", "A", 0, "Surds and reciprocals without a calculator", [],
  "A non-calculator paper leaves answers as √2, √3 and fractions of them; you need to manipulate them, not evaluate them.",
  """
<p>A <b>surd</b> is just a square root left unresolved, like √2. You are expected to leave it that way and
compare it with the options symbolically. The handful of moves you need:</p>
<div class="formula">√(ab)  = √a · √b          √8 = √4·√2 = 2√2
√(a/b) = √a / √b          √(8/7) = 2√2 / √7
√a · √a = a              √2 · √2 = 2
1/√a = √a / a            1/√2 = √2/2</div>
<p>That last one, <b>rationalising the denominator</b>, is what turns an option like 4/√7 into
4√7/7 — the same number written the way the answer key wrote it. If your answer looks right but is not
listed, rationalise before you panic.</p>

<p>Approximate values worth memorising, for when you must compare numerically:
√2 ≈ 1.41, √3 ≈ 1.73, √5 ≈ 2.24, and 1/√2 ≈ 0.707.</p>

<p>Worked example (Q16): light takes (4/√7)·a/c to cross a cube. Is that the same as √(8/7)·a/c?
√(8/7) = √8/√7 = 2√2/√7 ≈ 2.83/2.65 ≈ 1.07, while 4/√7 ≈ 1.51. Different — so those two options are not
the same answer even though both contain √7.</p>

<p><b>Traps.</b> √(a + b) is <i>not</i> √a + √b — there is no rule for the root of a sum. And when you
square both sides to compare, keep the direction of any inequality straight.</p>
""",
  "Q16's options are all surds times a/c; picking between them means manipulating roots, not evaluating them.")

c("logs", "A", 0, "Logarithms and indices without a calculator", ["stdform"],
  "A logarithm answers 'what exponent?', and that is exactly the question behind any 'how many half-lives?' problem.",
  """
<p><b>log<sub>b</sub>(x)</b> asks: “b raised to what power gives x?” So log₂(8) = 3 because 2³ = 8. Logs
and powers are inverse operations, which gives you the two rules that matter here:</p>
<div class="formula">log(xy)  = log x + log y           multiplying → adding
log(xⁿ)  = n · log x               a power comes out front
log_b(x) = log x / log b           change of base</div>
<p><b>Why a log appears in decay questions.</b> Exponential decay is N = N₀ · 2<sup>−t/T</sup>: the
unknown t is in the <i>exponent</i>, and the only way to get an exponent down is to take a log of both
sides. “How long until one third has decayed?” means N/N₀ = 2/3, so:</p>
<div class="formula">2/3 = 2<sup>−t/T</sup>
log₂(2/3) = −t/T
t = −T · log₂(2/3) = T · log₂(3/2)</div>
<p>No calculator is needed to recognise the answer — the options are written with logs in them. But it is
worth knowing the size: log₂(3/2) = log₂3 − 1 ≈ 1.585 − 1 = 0.585, so the time is a bit more than half a
half-life, which makes sense because a third decaying is less than half decaying.</p>

<p><b>Traps.</b> log(a/b) = log a − log b, not log a / log b. And the base matters: log₂3 ≈ 1.585 while
log₁₀3 ≈ 0.477 — mixing them changes the answer by a factor of about 3.</p>
""",
  "Q19: the time for one third to decay is T·log₂(3/2), and the options test whether you inverted the fraction.")

c("smallangle", "A", 0, "Small-angle approximations — and knowing when you don't need them", [],
  "For small angles in radians, sin θ ≈ θ, tan θ ≈ θ and cos θ ≈ 1 − θ²/2 — but sometimes an exact zero beats any approximation.",
  """
<p>If θ is small and measured in <b>radians</b> (never degrees — this is the one place the unit really
matters), the trig functions simplify:</p>
<div class="formula">sin θ ≈ θ            tan θ ≈ θ            cos θ ≈ 1 − θ²/2</div>
<p>You can see where these come from: the series for sin θ is θ − θ³/6 + …, so for small θ the first term
dominates and the error is roughly θ³/6 — at θ = 0.1 rad the error is about 0.02 %, at θ = 0.5 rad about
2 %. That is why the approximations are safe for “small” angles and useless at 45°.</p>

<p><b>The more important skill is noticing when an approximation is unnecessary.</b> In Q18 two
projectiles are launched at (45° + α) and (45° − α) and you are asked for the difference in range. The
tempting move is to expand sin(2θ) for each angle and subtract — a page of algebra. But the exact range
formula is R = v² sin(2θ)/g, and:</p>
<div class="formula">sin(2(45°+α)) = sin(90° + 2α) = cos 2α
sin(2(45°−α)) = sin(90° − 2α) = cos 2α</div>
<p>They are <i>identically equal</i>, so the difference is exactly zero for every α, small or not. The
identity sin(90° ± x) = cos x is exact, so no approximation is involved at all.</p>

<p><b>Traps.</b> Using degrees in sin θ ≈ θ gives answers out by a factor of 57. And an approximation
gives you the <i>leading</i> behaviour only — if the true answer is exactly zero, approximating will
leave you with a small spurious term and the wrong option.</p>
""",
  "Q18 says α is small, but the two ranges are <i>exactly</i> equal — the small-angle hint is a decoy.")

c("smallchange", "A", 0, "Relating small changes through a constraint", [],
  "When one length changes by a little, a linked length changes by a related little — differentiate the constraint to find how much.",
  """
<p>Suppose two quantities are locked together by a fixed relationship, and you nudge one by a small
amount. The other shifts by an amount you can get without re-solving the whole problem: take the
relationship and look at how a <i>small change</i> in it must balance.</p>

<p><b>Example (Q24).</b> A ladder of length L leans with its foot x from the wall and its top at height y,
so x² + y² = L² always. Push the foot in by a small distance a (so x changes by −a) and ask how much the
middle rises. If x changes by δx and y by δy, then to first order:</p>
<div class="formula">x² + y² = L²
2x·δx + 2y·δy = 0
δy = −(x/y)·δx</div>
<p>At 45° to the vertical the ladder is at 45° to the horizontal too, so x = y and δy = −δx: pushing the
foot in by a raises the top by exactly a. The centre of mass is at the midpoint, so it rises by half of
that, a/2, and the gain in gravitational potential energy is mg·(a/2) = ½mga.</p>

<p><b>The general recipe:</b> write the constraint, replace each variable by “(change in it)”, throw away
any term containing two small changes multiplied together, and solve. Products of two small quantities
are negligible — that is the only calculus idea being used.</p>

<p><b>Traps.</b> The ratio x/y is <i>not</i> 1 in general; it is only 1 here because the angle happens to
be 45°. At a steeper angle the same push moves the top much less, which is why ladders get hard to move
as they approach vertical.</p>
""",
  "Q24 is a small-change problem in disguise: constraint x²+y²=L², push a, half of it reaches the centre of mass.")

c("limits", "A", 0, "Testing an algebraic answer on limiting cases", [],
  "Put extreme numbers into the algebra — a mass ratio of 1, or infinity — and see which options still make physical sense.",
  """
<p>When the answer is a formula in a symbol, try <b>extreme values</b> of that symbol. Real physics has to
behave sensibly at the extremes, and usually only one candidate formula does.</p>

<p><b>Example (Q12).</b> A body at rest explodes into masses m and am (a &gt; 1); total kinetic energy is E;
what is the kinetic energy of the <i>larger</i> mass? The options include E/(1+a), aE/(1+a²),
a²E/(1+a²), a³E/(1+a³) and E/a. Test a = 1: the two masses are then equal, so by symmetry each takes
exactly half the energy, E/2. Checking:</p>
<div class="formula">E/(1+a)     → E/2   ✓
aE/(1+a²)   → E/2   ✓
a²E/(1+a²)  → E/2   ✓
a³E/(1+a³)  → E/2   ✓
E/a         → E     ✗</div>
<p>Four survive, so try the other extreme, a → ∞ (an almost immovable heavy fragment). Then the heavy
fragment should barely move, so its kinetic energy should tend to 0:</p>
<div class="formula">E/(1+a)     → 0     ✓        (and the light one takes everything)
aE/(1+a²)   → 0     ✓
a²E/(1+a²)  → E     ✗
a³E/(1+a³)  → E     ✗</div>
<p>Two left. Now use the physics properly: momentum is zero before and after, so the two momenta are equal
and opposite, and KE = p²/2m means the lighter mass gets more energy. With equal p, KE ∝ 1/m, so the
energies split as a : 1 in favour of the light one — the heavy mass gets E/(1+a). Two limiting cases plus
one physical fact settles it.</p>

<p><b>Traps.</b> Symmetry tests (a = 1) and extreme tests (a → 0, a → ∞) are cheap and catch most wrong
options, but they rarely catch all of them. Use them to eliminate, then finish with physics.</p>
""",
  "Q12's five options are separated by nothing but two limiting cases plus KE ∝ 1/m at fixed momentum.")

c("graphshape", "A", 0, "Reasoning about the shape of a graph", [],
  "You rarely need to plot a graph — you need its starting value, whether it jumps, its slope, and where it ends.",
  """
<p>A “which graph is it?” question is answered by reading off four features, in this order:</p>
<ul>
<li><b>Value at t = 0</b> — is it zero, or does it start at some finite value?</li>
<li><b>Discontinuities</b> — does the quantity jump when something switches on? A force switching on makes
<i>acceleration</i> jump, but position and velocity stay continuous.</li>
<li><b>Slope</b> — is it increasing, decreasing, or changing sign? The slope of a graph is the rate of
change of the thing plotted.</li>
<li><b>Long-term behaviour</b> — does it settle to a constant, oscillate, or grow?</li>
</ul>
<p><b>Example (Q20).</b> Jerk j = da/dt for a bungee jumper. Before the rope goes taut the only force is
weight, so a = g constant and j = 0. The instant the rope becomes taut a spring force kx switches on, so a
jumps from g downward and j becomes a large negative spike — a jump <i>down</i> from zero. After that the
jumper performs simple harmonic motion: a = −ω²x plus gravity, so j = da/dt is proportional to velocity,
which oscillates. So the graph is: zero, jump down, then an oscillation — and the oscillation must start
at the moment of the jump.</p>

<p><b>The continuity rule is the key idea.</b> Position cannot jump (that would be infinite velocity),
velocity cannot jump (infinite force), but acceleration <i>can</i> jump because force can switch on
suddenly. So jerk, being the rate of change of acceleration, contains a spike or jump at that instant.</p>

<p><b>Traps.</b> Confusing “the graph crosses zero” with “the quantity is zero throughout”, and reading a
graph of a rate as if it were a graph of the quantity itself.</p>
""",
  "Q20 is a graph-shape question about jerk: zero, then a jump, then an oscillation about a shifted value.")

c("counting", "A", 0, "Counting combinations instead of listing them", [],
  "'How many pairs?' is a formula, not a list — and listing is exactly how people lose this mark.",
  """
<p>If you must choose an unordered <b>pair</b> from n objects, the count is:</p>
<div class="formula">number of pairs = C(n,2) = n(n−1)/2</div>
<p>Reason: there are n choices for the first object and (n−1) for the second, giving n(n−1) ordered pairs,
but each unordered pair has been counted twice (A then B, and B then A), so divide by 2.</p>

<p><b>Example (Q11).</b> Ten energy levels, all transitions allowed. A photon is emitted when an electron
drops between <i>two different</i> levels, so each photon energy corresponds to a pair of levels:
C(10,2) = 10 × 9 / 2 = 45. Note the question asks for the number of <i>unique energies</i>, and with
“all transitions possible” and no two gaps deliberately equal, each pair gives a distinct energy — so 45
is the maximum.</p>

<p><b>Traps.</b> Counting 10 × 9 = 90 means you counted each transition twice (3→1 and 1→3 are the same
photon, just emission versus absorption). Counting 100 or 110 means you included “transitions” from a
level to itself, which emit nothing. And “maximum” in the question is a hint that two gaps could
coincide — reducing the count — so the answer is the upper bound.</p>
""",
  "Q11: ten levels, every transition allowed → C(10,2) = 45 photon energies.")

c("search", "A", 0, "Exhaustive search of a small space", [],
  "When there are only a handful of possibilities, list them all in a fixed order instead of hunting for a clever answer.",
  """
<p>Some questions look like puzzles but have a tiny <b>search space</b> — a small number of combinations
to check. The discipline is to enumerate them <b>systematically</b> (largest first, or by the number of
pieces), so you can prove you have not missed one.</p>

<p><b>Example (Q6).</b> Resistors cost: 2 Ω £3, 3 Ω £1, 6 Ω £3, 8 Ω £4, 12 Ω £2; stock unlimited; make
exactly 4 Ω as cheaply as possible. Since 3 Ω is by far the cheapest, look there first:</p>
<div class="formula">three 3 Ω in parallel:  1/R = 1/3+1/3+1/3 = 1   → R = 1 Ω   ... then +3 Ω in series = 4 Ω
cost: 3 × £1 + £1 = £4</div>
<p>Could £3 do it? The only £3-and-under combinations are a single 2 Ω, a single 3 Ω, a single 6 Ω, or
two 3 Ω pieces (£2). Two 3 Ω give only 1.5 Ω in parallel or 6 Ω in series. None is 4 Ω, and no cheaper
combination exists — so £4 is the minimum, proved by exhausting the cheaper cases.</p>

<p><b>The habit.</b> Order the search by cost (or by count), rule out everything cheaper than your best
find, and stop. You have then not merely found an answer, you have shown there is no better one.</p>

<p><b>Traps.</b> Assuming a series chain is the only option (parallel combinations are usually where the
cheap answer hides), and forgetting “stock unlimited” means you may reuse the cheap value as often as you
like.</p>
""",
  "Q6: cheapest exact 4 Ω. The answer hides in a parallel block of the cheapest resistor.")

c("readdiagram", "A", 0, "Read the diagram before quoting a formula", [],
  "Most wrong answers in this paper come from a correct formula applied to the wrong angle, direction or point.",
  """
<p>Before writing anything down, spend ten seconds extracting the diagram's facts explicitly: <b>where is
the angle measured from</b> (the normal, or the surface?), <b>which way do the arrows point</b>, and
<b>which two points</b> is the question asking about.</p>

<p><b>Why it matters (Q2).</b> Snell's law is always quoted with angles from the <b>normal</b>. In the
figure for Q2 the angles θ₁ and θ₂ are drawn from the <b>surface</b>. If θ is measured from the surface
then the angle from the normal is (90° − θ), and sin(90° − θ) = cos θ. So the law becomes:</p>
<div class="formula">n₁ sin(angle from normal) = n₂ sin(angle from normal)
n₁ sin(90° − θ₁) = n₂ sin(90° − θ₂)
n₁ cos θ₁ = n₂ cos θ₂</div>
<p>Four of the five options are what you get by mixing up sines and cosines — the question is purely
testing whether you read the diagram. Note this is also physically sensible: if n₂ &lt; n₁ the ray bends
<i>away</i> from the normal, so θ₂ (from the surface) gets <i>smaller</i>, meaning cos θ₂ gets bigger —
which is exactly what n₁ cos θ₁ = n₂ cos θ₂ says.</p>

<p><b>Also check arrow directions.</b> In Q7 two particles move along a line and the question asks how far
one travels before they meet. If both arrows point the same way you need the <i>difference</i> of the
speeds (closing speed); if they point at each other you need the <i>sum</i>. A single arrow reversed
doubles or halves the answer.</p>

<p><b>Traps.</b> Assuming angles are always from the normal because that is how they are usually drawn,
and assuming a velocity arrow shows position rather than direction of motion.</p>
""",
  "Q2 measures angles from the surface — every wrong option is a sine/cosine mix-up. Q7 depends on arrow directions.")

# ───────────────────────────── STAGE 1 · MECHANICS ─────────────────────────────

c("kinematics", "B", 1, "Speed, velocity and constant acceleration", [],
  "Motion is described by five quantities — s, u, v, a, t — linked by a small number of equations you can derive from a velocity–time graph.",
  """
<p><b>Distance</b> is how far you actually travelled; <b>displacement</b> is how far you ended up from
where you started, with a direction. <b>Speed</b> is distance/time; <b>velocity</b> is displacement/time
and has a direction. For motion in a straight line at constant velocity:</p>
<div class="formula">s = v t        (displacement = velocity × time)</div>
<p>If velocity changes smoothly, <b>acceleration</b> a = (change in velocity)/(time taken). For constant
acceleration the four equations follow from one picture: a velocity–time graph is a straight line, the
area under it is the displacement, and its gradient is a.</p>
<div class="formula">v  = u + at
s  = ut + ½at²
s  = ½(u + v)t        (area of a trapezium)
v² = u² + 2as</div>
<p>Each one relates four of the five quantities s, u, v, a, t and leaves one out, so pick the equation
that omits the quantity you neither know nor want.</p>

<p><b>Example (Q7).</b> Constant speeds, so only s = vt is needed — no acceleration equation at all.
<b>Example (Q21).</b> A ring slides down a smooth rod from rest, so u = 0 and s = ½at² with a equal to the
component of g along the rod (see resolving vectors).</p>

<p><b>Traps.</b> “Starts from rest” means u = 0, and “comes to rest” means v = 0 — easy to miss. Signs
matter: choose a positive direction and give every velocity and acceleration the right sign, including
a = −g when up is positive.</p>
""",
  "Q7 needs only s = vt; Q21 needs s = ½at² with a = g sin 30°.")

c("relvel", "B", 1, "Relative velocity and closing speed", ["kinematics"],
  "What matters in a catch-up problem is not how fast each object moves, but how fast the gap between them shrinks.",
  """
<p>The <b>relative velocity</b> of B as seen by A is v<sub>B</sub> − v<sub>A</sub> (a vector subtraction).
In one dimension it is just a signed difference, and its magnitude tells you the rate at which the
<b>separation</b> changes — the <b>closing speed</b>.</p>
<div class="formula">same direction:   closing speed = |v_B − v_A|     (the difference)
opposite directions: closing speed = |v_B| + |v_A|   (the sum)
time to meet = initial separation / closing speed</div>
<p><b>Example (Q7).</b> Two particles 18 m apart, both moving along the same line in the same direction,
one at 6 m s⁻¹ and the other at 3 m s⁻¹ (as the diagram's arrows show). The gap closes at 6 − 3 =
3 m s⁻¹, so they meet after 18/3 = 6 s, and particle A has travelled 6 × 6 = 36 m. Doing it the long way
— writing s<sub>A</sub> = 6t and s<sub>B</sub> = 18 + 3t and solving — gives the same 36 m; relative
velocity is just the short cut.</p>

<p><b>Traps.</b> Adding speeds when the arrows point the same way (that halves the time), and using the
closing speed to compute the distance travelled by the wrong particle — the time is shared, the distance
is not.</p>
""",
  "Q7: 18 m gap, closing speed 3 m s⁻¹, so 6 s and A travels 36 m.")

c("vectors-resolve", "B", 1, "Resolving vectors into components", ["kinematics"],
  "Any vector can be split into two perpendicular parts, and usually only one of those parts matters.",
  """
<p>Force, velocity and acceleration are <b>vectors</b>: they have direction as well as size. In a
right-angled split, a vector of size F at angle θ to a direction has:</p>
<div class="formula">component along that direction      = F cos θ
component perpendicular to it       = F sin θ</div>
<p>The reason is just trigonometry on the triangle the vector makes — and the check is that when θ = 0 the
whole vector lies along the direction (cos 0 = 1), and when θ = 90° none of it does (cos 90° = 0).</p>

<p><b>On a slope (Q21).</b> A ring slides down a smooth rod at 30° to the horizontal. Gravity mg acts
straight down; split it into a part along the rod and a part perpendicular to it:</p>
<div class="formula">along the rod     : mg sin 30° = mg/2    ← this is what accelerates it
perpendicular     : mg cos 30° = mg√3/2  ← this is what the rod's normal reaction cancels</div>
<p>Because the ring cannot move perpendicular to the rod, the perpendicular forces must balance, and the
acceleration comes only from the along-the-rod component: a = g sin 30° = g/2. This is why things
accelerate more slowly down a gentle slope — the sin factor shrinks.</p>

<p><b>Traps.</b> Using sin where cos is needed. The check that never fails: as the angle goes to zero the
component along the slope must go to zero, so the along-slope component carries sin (of the angle to the
horizontal).</p>
""",
  "Q21: the ring's acceleration down the rod is g sin 30° = g/2, from resolving weight along the rod.")

c("force", "C", 1, "Force and Newton's laws of motion", ["kinematics"],
  "A force is a push or pull; Newton's second law says the resultant force equals mass times acceleration, and that one line drives most of mechanics.",
  """
<p>Forces are pushes or pulls: weight (gravity), tension in a string, the normal reaction from a surface,
friction, drag, and the force from a spring. They are vectors, so forces in different directions have to
be combined by adding components, not by adding sizes.</p>

<p><b>Newton's first law:</b> if the resultant force is zero, velocity is constant (including zero). Things
do not need a force to keep moving — they need one to <i>change</i> their motion.</p>

<p><b>Newton's second law:</b></p>
<div class="formula">F = m a        resultant force (N) = mass (kg) × acceleration (m s⁻²)</div>
<p>Strictly it is “resultant force = rate of change of momentum”, which reduces to ma when the mass is
constant. This is where the newton is defined: 1 N is what accelerates 1 kg at 1 m s⁻².</p>

<p><b>Newton's third law:</b> if A pushes B, B pushes A back with an equal force of the same type in the
opposite direction. The two forces act on <i>different</i> bodies, which is why they do not cancel out in
F = ma — never add a third-law pair into one equation of motion.</p>

<p><b>How to use it.</b> Pick a body, draw every force on it, resolve in the direction of motion, and set
the resultant equal to ma. If the body is in equilibrium, a = 0 and the forces simply balance.</p>

<p><b>Traps.</b> Forgetting weight when nothing mentions it — every body near Earth has mg downwards. And
“normal reaction” is not automatically equal to mg; it equals mg only when nothing else has a vertical
component.</p>
""",
  "Q20 is Newton's second law with a spring force: the acceleration jumps when the rope goes taut, which is what makes the jerk graph jump.")

c("momentum", "C", 1, "Momentum and impulse", ["force"],
  "Momentum is 'mass in motion' (p = mv), and impulse — force × time — is exactly the amount by which momentum changes.",
  """
<p><b>Momentum</b> is defined as:</p>
<div class="formula">p = m v        unit: kg m s⁻¹   (which is the same as N s)</div>
<p>It measures how hard an object is to stop: a heavy truck and a light cyclist at the same speed have
very different momenta. Momentum is a vector, so direction matters and opposite directions subtract.</p>

<p><b>Impulse</b> is force × time, and it equals the change in momentum. It comes straight out of Newton's
second law: F = ma = m(v−u)/t, so multiplying by t:</p>
<div class="formula">F t = m v − m u        impulse = change in momentum</div>
<p>That is why a longer stopping time means a smaller force — the physics behind crumple zones, airbags
and bending your knees when you land. The momentum change is fixed; spreading it over more time reduces
the force.</p>

<p><b>In Q3</b> the question is only about the <i>unit</i> of impulse, which can be written several ways
because it equals force × time:</p>
<div class="formula">N s                = (kg m s⁻²)(s)              = kg m s⁻¹
kg m s⁻¹           base units, the same thing
W s² m⁻¹           = (J s⁻¹)(s²)(m⁻¹) = (N m)(s)(m⁻¹) = N s
C V s m⁻¹          = (C)(J C⁻¹)(s)(m⁻¹) = J s m⁻¹ = N s
Pa m³              = (N m⁻²)(m³) = N m = J        ← energy, NOT impulse</div>
<p>Four of them reduce to N s; the odd one out is an energy.</p>

<p><b>Traps.</b> Momentum and kinetic energy are different quantities with different units (kg m s⁻¹
versus kg m² s⁻²) — do not use them interchangeably. And momentum has a direction: two equal and opposite
momenta give zero total, not double.</p>
""",
  "Q3: four options are impulse units in disguise, one (Pa m³) is an energy.")

c("momcons", "C", 1, "Conservation of momentum", ["momentum"],
  "If no external force acts, the total momentum of a system never changes — even in an explosion where energy is released.",
  """
<p>Conservation of momentum follows from Newton's third law: internal forces come in equal and opposite
pairs, so they cancel when you add up the whole system. Only an <b>external</b> force can change the
total.</p>
<div class="formula">total momentum before = total momentum after</div>
<p><b>Example (Q12).</b> A body at rest explodes into masses m and am. Before: momentum is zero. After:
the two momenta must still add to zero, so they are equal in size and opposite in direction:</p>
<div class="formula">p₁ = −p₂        so |p₁| = |p₂| = p</div>
<p>That single line is the whole physics of the explosion. The chemical energy released does not have to
be shared equally — momentum does, and it is shared equally-and-oppositely whatever the masses.</p>

<p><b>Traps.</b> Momentum is conserved in an explosion; kinetic energy is <i>not</i> (it increases, from
the chemical energy released). And “conserved” applies to the <i>system</i>: if a wall or the Earth is
pushing, momentum is not conserved for your two objects alone.</p>
""",
  "Q12: the two fragments carry equal and opposite momentum, which is what fixes how the energy splits.")

c("ke", "C", 1, "Work, energy and kinetic energy", ["force", "momentum"],
  "Energy is the capacity to do work; a moving body carries ½mv², which can also be written p²/2m — and that second form is often the one you need.",
  """
<p><b>Work</b> is done when a force moves its point of application:</p>
<div class="formula">W = F s cos θ        (θ is the angle between the force and the displacement)</div>
<p>Only the part of the force along the motion does work — carrying a bag horizontally does no work on it,
because the upward force is perpendicular to the horizontal motion (cos 90° = 0).</p>

<p><b>Kinetic energy</b> is the energy a body has because it is moving. Derivation: push a mass from rest
with constant force F over distance s, so work done = Fs; with v² = 2as and F = ma,</p>
<div class="formula">W = F s = (ma)(v²/2a) = ½ m v²
so   KE = ½ m v²        unit: kg m² s⁻² = J</div>
<p><b>The other form.</b> Because p = mv, substituting v = p/m gives:</p>
<div class="formula">KE = ½m(p/m)² = p² / 2m</div>
<p>This is the form that solves explosion and recoil questions, because momentum p is the thing that is
shared. At <b>fixed momentum, KE is inversely proportional to mass</b> — the light fragment gets most of
the energy.</p>

<p><b>Example (Q12).</b> Fragments m and am share momentum equally (size p). Their energies are
p²/2m and p²/2am, so they are in the ratio a : 1. Total E splits as E·a/(a+1) for the light one and
E/(a+1) for the heavy one — a clean result with no algebra beyond the ratio.</p>

<p><b>Traps.</b> KE depends on v², so doubling speed quadruples the energy. And KE is a scalar — it has no
direction, so “total kinetic energy” is a plain sum, never a vector subtraction.</p>
""",
  "Q12: at equal momentum KE ∝ 1/m, so the heavy fragment gets only E/(1+a) of the energy.")

c("pe-gpe", "C", 1, "Gravitational potential energy", ["ke"],
  "Lifting something stores energy mgh; the path does not matter, only the change in height.",
  """
<p>Near the Earth's surface gravity is nearly constant, so the weight of a mass m is mg downwards
(g ≈ 9.8 N kg⁻¹, the gravitational field strength). Lifting it through a height h needs a force mg over a
distance h:</p>
<div class="formula">work done = force × distance = mg × h
Δ(GPE) = m g h        unit: J</div>
<p>Because gravity is a <b>conservative</b> force, only the change in height counts, not the route taken —
climbing stairs or taking a ramp to the same floor stores the same energy.</p>

<p><b>Where is h measured from?</b> For an extended body, use the height of its <b>centre of mass</b>. That
is what makes Q24 work: pushing the ladder's foot in raises its top by a, but the centre of mass is
halfway along the ladder, so it rises by only a/2, and Δ(GPE) = mg × a/2 = ½mga.</p>

<p><b>Traps.</b> Using the height of one end instead of the centre of mass; forgetting the mass (GPE is
not just gh); and mixing up “height above the floor” with “change in height” — only the change appears in
energy bookkeeping.</p>
""",
  "Q24: half of the ladder's rise reaches the centre of mass, giving Δ(GPE) = ½mga.")

c("hookeslaw", "C", 1, "Hooke's law: the spring force", ["force"],
  "Stretch a spring by x and it pulls back with force kx — linear in the extension, which is what makes oscillating systems so predictable.",
  """
<p>For a spring or an elastic rope, the tension is proportional to how much it has been stretched beyond
its natural length:</p>
<div class="formula">F = k x        k = stiffness (N m⁻¹),  x = extension (m)</div>
<p>Doubling the stretch doubles the pull, up to the <b>limit of proportionality</b>; beyond that the
material stops behaving linearly and eventually deforms permanently. Note that x is the <i>extension</i>,
not the total length — a spring of natural length 0.5 m stretched to 0.7 m has x = 0.2 m.</p>

<p>The force always acts to restore the natural length, so as a vector it is:</p>
<div class="formula">F = −k x        (minus because it opposes the displacement)</div>
<p>That minus sign is the whole reason springs oscillate: pull it out and it pulls back, push it in and it
pushes out.</p>

<p><b>Energy stored.</b> Since the force grows from 0 to kx as you stretch, the average force is ½kx and
the work stored is:</p>
<div class="formula">E = ½ F x = ½ k x²        (also: the area under a force–extension graph)</div>

<p><b>Traps.</b> Using the total length as the extension; assuming k is the same for every spring (it
depends on material and dimensions); and applying F = kx to a <i>slack</i> rope — a slack rope exerts no
force at all until it goes taut, which is exactly the switch that makes the bungee question interesting.</p>
""",
  "Q20: before the rope is taut there is no spring force at all; the moment it goes taut, kx switches on and the acceleration jumps.")

c("shm", "C", 1, "Simple harmonic motion", ["hookeslaw", "force"],
  "Whenever the restoring force is proportional to displacement, the motion is sinusoidal with ω² = k/m — and you can write that down without solving anything.",
  """
<p>Put Hooke's law into Newton's second law:</p>
<div class="formula">F = −kx   and   F = ma
ma = −kx      →      a = −(k/m) x</div>
<p>That is the defining equation of <b>simple harmonic motion</b>: acceleration is proportional to
displacement and directed back towards the centre. Comparing with the standard form a = −ω²x:</p>
<div class="formula">ω² = k/m              ω = √(k/m)          T = 2π/ω = 2π√(m/k)</div>
<p>ω is the <b>angular frequency</b> in rad s⁻¹; the frequency in hertz is f = ω/2π and the period is
T = 1/f. Notice that the amplitude does <b>not</b> appear anywhere — a pendulum-style oscillator takes the
same time for a big swing as for a small one.</p>

<p><b>The shortcut.</b> You never need to solve the differential equation. If you can show
a = −(constant) × x, then ω² is that constant, read straight off. This is the standard way to handle
“find the period of…” questions.</p>

<div class="formula">displacement  x = A cos(ωt)          velocity  v = −Aω sin(ωt)
acceleration  a = −Aω² cos(ωt) = −ω²x</div>
<p>So velocity is zero at the extremes and maximum at the centre, while acceleration is maximum at the
extremes and zero at the centre — they are a quarter-cycle out of step.</p>

<p><b>Traps.</b> Confusing ω (rad s⁻¹) with f (Hz) — they differ by 2π. And SHM requires the force to be
<i>proportional</i> to displacement; a constant force like gravity does not produce SHM, it only shifts
the equilibrium position.</p>
""",
  "Q20: once the rope is taut the jumper is an oscillator with ω² = k/m, so acceleration — and therefore jerk — oscillates.")

c("moments", "C", 1, "Moments and the principle of moments", ["force"],
  "A force far from a pivot turns things more effectively: moment = force × perpendicular distance, and equilibrium needs the turning effects to balance.",
  """
<p>The <b>moment</b> (torque) of a force about a point measures its turning effect:</p>
<div class="formula">moment = F × d        d = perpendicular distance from the pivot to the line of action of F
unit: N m   (note: not joules — a moment is not energy, even though the units look the same)</div>
<p>The word <b>perpendicular</b> is what people forget: d is not the distance to where the force is
applied, it is the shortest distance from the pivot to the force's <i>line</i>. Equivalently,
moment = F × (distance along the object) × sin(angle between them).</p>

<p><b>Principle of moments.</b> If a body is not rotating, the total clockwise moment about any point
equals the total anticlockwise moment about that point. You are free to choose the point — and the
clever choice is a point where an unknown force acts, because a force through the pivot has zero moment
and drops out of the equation.</p>

<p><b>Example (Q21).</b> A rod hinged at O is held by a vertical string at its far end ℓ away, at 30° to
the horizontal. Take moments about O so the hinge reaction disappears. The string's tension T is vertical
and acts at horizontal distance ℓ cos 30° from O, so its moment is T·ℓ cos 30°. The ring pushes on the
rod perpendicular to it with force mg cos 30° at distance (ℓ − s) along the rod, where s is how far it
has slid, giving moment mg cos 30°·(ℓ − s). Equating:</p>
<div class="formula">T · ℓ cos 30° = mg cos 30° (ℓ − s)      →      T = mg (1 − s/ℓ)</div>
<p>The cos 30° cancels — which is why the answer is tidier than the setup suggests.</p>

<p><b>Traps.</b> Using the distance along the rod instead of the perpendicular distance; and forgetting a
force entirely. Draw every force first.</p>
""",
  "Q21: moments about the hinge give T = mg(1 − s/ℓ), and with s = ¼gt² that becomes T = mg(1 − gt²/4ℓ).")

c("com", "C", 1, "Centre of mass", ["moments"],
  "For almost every purpose, an extended object behaves as if all its mass were concentrated at one point — the centre of mass.",
  """
<p>The <b>centre of mass</b> is the balance point of a body. Support it there and the body balances; push
it there and the body accelerates without rotating. Formally it is the mass-weighted average position:</p>
<div class="formula">x_cm = ( m₁x₁ + m₂x₂ + … ) / ( m₁ + m₂ + … )</div>
<p>For a <b>uniform</b> body the centre of mass is at its geometric centre: the middle of a uniform rod,
the centre of a uniform disc, the meeting point of the medians of a uniform triangle.</p>

<p><b>Why it matters</b>, in three separate places on this paper:</p>
<ul>
<li><b>Gravity acts there.</b> The weight of a body is a single force mg through the centre of mass, and
its gravitational potential energy is mg × (height of the centre of mass) — Q24.</li>
<li><b>Toppling starts there.</b> A body topples when its centre of mass passes beyond the edge of its
support — Q14.</li>
<li><b>Moments use it.</b> In a moment calculation the weight of an extended body acts as one force at
the centre of mass — Q21, Q24.</li>
</ul>

<p><b>Traps.</b> Assuming the centre of mass is at the geometric centre for a <i>non-uniform</i> body (a
ladder with a heavy rung, a half-full glass); and using the position of one end of a body instead of its
centre when computing GPE.</p>
""",
  "Q14 (toppling) and Q24 (GPE change) both turn on where the centre of mass sits.")

c("statics", "C", 1, "Static equilibrium", ["force", "moments", "vectors-resolve"],
  "For a body at rest, three conditions: forces up = forces down, forces left = forces right, and clockwise moments = anticlockwise moments.",
  """
<p><b>Equilibrium</b> means zero acceleration and zero rotation, so both Newton's second law and the
principle of moments apply with a = 0:</p>
<div class="formula">ΣF (any direction) = 0        resolve in two perpendicular directions
Σmoments (any point) = 0      about any point you like</div>
<p>You get three independent equations, which is why a statics problem can fix three unknowns. Choosing
the point for moments well — through the line of action of an unwanted force — deletes that force from
the equation entirely.</p>

<p><b>Three-force bodies.</b> If exactly three non-parallel forces hold a body in equilibrium, their lines
of action must all pass through a single point. (If they did not, one of them would have a moment about
the intersection of the other two and the body would rotate.) This is a fast way to sketch the direction
of an unknown reaction at a hinge.</p>

<p><b>The standard example</b> is a ladder against a wall: weight mg at the centre, a normal reaction from
the wall (horizontal, if the wall is smooth), and at the floor a normal reaction (vertical) plus friction
(horizontal). Resolve horizontally and vertically, take moments about the foot of the ladder, and the
friction needed at the base falls out.</p>

<p><b>Traps.</b> Putting friction at the wrong end — a <i>smooth</i> wall or floor means no friction there
at all, and “smooth” is a word to circle when you read the question. And forgetting that a reaction from
a surface is perpendicular to that surface.</p>
""",
  "Q24's ladder and Q14's biscuit are both equilibrium problems; Q21's rod uses moments about the hinge.")

c("toppling", "C", 1, "Toppling and the support condition", ["com", "statics"],
  "An object does not fall when it is off-centre — it falls when its centre of mass is no longer above its area of support.",
  """
<p>Weight acts vertically through the centre of mass. If that vertical line — the <b>plumb line</b> — falls
inside the region of contact with the support, the support pushes up on the near side and the body stays
put. Move the body until the plumb line reaches the <b>edge</b> of the support and it is on the point of
toppling; push further and the weight now has a moment about that edge which rotates the body off.</p>
<div class="formula">limiting case:  centre of mass is directly above the pivot edge
beyond that:    the moment of the weight about the edge is unopposed  →  it topples</div>
<p><b>Example (Q14).</b> A thin disc of radius b balances on the rim of a cup of radius 3b/2, placed as far
from the cup's centre as possible. The disc's centre must sit above the rim circle; two circles of radii
b and 3b/2 intersect, and the disc is at the limit when its centre of mass is exactly above the point of
contact. The geometry gives a maximum offset of ((3 − √5)/2)·b — the answer comes from the triangle
formed by the two centres and the contact point, using Pythagoras on a right angle at the contact.</p>

<p><b>The general method.</b> Identify the pivot edge (the last point of contact), then write the
condition “horizontal distance from the pivot to the centre of mass = 0” at the limit.</p>

<p><b>Traps.</b> Using the centre of the support rather than its edge; and forgetting that on a curved rim
there is effectively a single contact point, which becomes the pivot.</p>
""",
  "Q14: the biscuit topples when its centre passes the contact point on the cup's rim.")

c("circular", "D", 1, "Circular motion: angular speed and centripetal force", ["force", "vectors-resolve"],
  "Anything moving in a circle is constantly accelerating towards the centre, so something must be pushing it there with F = mv²/r.",
  """
<p>Even at constant speed, circular motion is accelerated motion, because the <b>direction</b> of the
velocity keeps changing. The acceleration points to the centre — <b>centripetal</b>, “centre-seeking”.</p>

<p>Two descriptions of the same motion. If the body goes round once in period T:</p>
<div class="formula">ω = 2π / T = 2π f        angular speed, rad s⁻¹
v = r ω = 2πr / T        speed along the arc</div>
<p>One full turn is 2π radians, which is why 2π keeps appearing. Then the acceleration and the required
force are:</p>
<div class="formula">a = v² / r = r ω²        towards the centre
F = m v² / r = m r ω²    the resultant force towards the centre</div>
<p><b>Centripetal force is not a new force.</b> It is the <i>name</i> for whatever real force or
combination of forces points to the centre — tension in a string, gravity on a satellite, friction on a
car in a bend, or the horizontal component of tension in a conical pendulum. Never add “centripetal
force” to a free-body diagram as if it were an extra push.</p>

<p><b>Traps.</b> Using diameter instead of radius; mixing ω with f (they differ by 2π); and thinking there
is an outward “centrifugal force” — in an inertial frame there is not; the body is simply trying to go
straight.</p>
""",
  "Q22: the conical pendulum's horizontal force is the centripetal force, and ω² = g/(ℓ cos θ) comes straight from it.")

c("conical", "D", 1, "The conical pendulum", ["circular", "vectors-resolve"],
  "A string tracing out a cone: the vertical component of tension holds the bob up, the horizontal component drives it round, and the ratio gives ω² = g/(ℓ cos θ).",
  """
<p>A bob on a string of length ℓ moves in a horizontal circle with the string at a fixed angle θ to the
vertical. Two facts, and then it is just algebra:</p>
<div class="formula">vertical   (no vertical acceleration):  T cos θ = mg
horizontal (this is the centripetal force): T sin θ = m r ω²   with r = ℓ sin θ</div>
<p>Divide the second by the first to eliminate both T and m:</p>
<div class="formula">tan θ = r ω² / g         and since r = ℓ sin θ
(sin θ / cos θ) = ℓ sin θ · ω² / g
ω² = g / (ℓ cos θ)</div>
<p>Two things worth noticing. The <b>mass cancels</b> — a heavy bob and a light one behave identically. And
as θ → 90° the string becomes horizontal, cos θ → 0 and ω → ∞: you can never actually make a string
perfectly horizontal, because some tension is always needed to hold the weight up.</p>

<p><b>Example (Q22).</b> θ goes from 30° to 60°. Only ω² ∝ 1/cos θ matters:</p>
<div class="formula">ω₂²/ω₁² = cos 30° / cos 60° = (√3/2)/(1/2) = √3
ω₂/ω₁   = √√3</div>
<p>Note the double root: the formula gives ω², so a ratio of ω² means a square root to get ω, and √3
under another root is √√3 — the kind of nested surd the answer key leaves alone.</p>

<p><b>Traps.</b> Using the string length ℓ as the circle radius (the radius is ℓ sin θ); and forgetting to
take the square root when the question asks for ω rather than ω².</p>
""",
  "Q22: factor √√3, because ω² ∝ 1/cos θ and cos 30°/cos 60° = √3.")

c("projectile", "B", 1, "Projectiles: range and complementary angles", ["kinematics", "vectors-resolve"],
  "Split the motion: horizontal at constant speed, vertical under gravity. The range formula then shows that 45° + α and 45° − α land in the same place.",
  """
<p>A projectile is two independent problems sharing a clock. Horizontally there is no acceleration, so
x = v cos θ · t. Vertically the acceleration is −g, so y = v sin θ · t − ½gt². Eliminate t using the time
of flight (from y = 0 again) and you get the <b>range</b>:</p>
<div class="formula">time of flight  t = 2 v sin θ / g
range           R = (v cos θ) t = v² sin(2θ) / g</div>
<p>sin(2θ) is largest when 2θ = 90°, i.e. θ = 45° — the familiar result that 45° gives the maximum range,
and R<sub>max</sub> = v²/g.</p>

<p><b>The symmetry that Q18 uses.</b> Because the formula contains sin(2θ), two angles that add to 90°
give the same range:</p>
<div class="formula">θ₁ = 45° + α  →  2θ₁ = 90° + 2α  →  sin(90° + 2α) = cos 2α
θ₂ = 45° − α  →  2θ₂ = 90° − 2α  →  sin(90° − 2α) = cos 2α</div>
<p>Identical, for every α. So the difference in range is exactly <b>zero</b> — not “small”, not
“approximately zero”. The question tells you α is small, which is a hint to reach for approximations, but
an exact identity beats an approximation every time.</p>

<p><b>Traps.</b> Assuming air resistance is included (it is not, unless stated); using v sin θ for the
horizontal component; and thinking the maximum-height formula is needed here — it is not.</p>
""",
  "Q18: complementary launch angles give identical ranges, so the difference is exactly 0.")
