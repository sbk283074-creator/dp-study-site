# -*- coding: utf-8 -*-
"""Key-point lessons, part B: materials (E), thermal physics (J), waves and optics (F, G)."""

C = []


def c(i, m, stage, title, pre, summary, body, used):
    C.append(dict(id=i, m=m, stage=stage, t=title, pre=pre, one=summary, body=body.strip(), used=used))


# ───────────────────────────── STAGE 2 · MATERIALS ─────────────────────────────

c("stressstrain", "E", 2, "Stress, strain and the Young modulus", ["force"],
  "Stress is force per area and strain is extension per length; their ratio (below the limit of proportionality) is the Young modulus — a stiffness that depends only on the material.",
  """
<p>Pull on a wire and it stretches. To talk about it independently of how thick or how long the wire is,
two ratios are defined:</p>
<div class="formula">stress  σ = F / A          force per cross-sectional area, unit Pa (= N m⁻²)
strain  ε = ΔL / L         extension per original length, no unit (a ratio of two lengths)</div>
<p>Strain is dimensionless and is often quoted as a percentage. These two let you compare a thick short
wire with a thin long one of the same material.</p>

<p><b>Hooke's law in material form.</b> Up to the limit of proportionality, stress is proportional to
strain, and the constant is a property of the <i>material</i>, not the sample:</p>
<div class="formula">E = σ / ε        the Young modulus, unit Pa</div>
<p>Steel is about 2 × 10¹¹ Pa, copper about 1 × 10¹¹ Pa, rubber far lower. A large Young modulus means a
stiff material — a big stress for a small strain. You can connect it back to the spring constant: since
σ = F/A and ε = ΔL/L,</p>
<div class="formula">F/A = E · ΔL/L     →     F = (EA/L) · ΔL
so k = EA / L      — thicker and shorter means stiffer, as expected</div>

<p><b>Traps.</b> Confusing stress with force (stress is per unit area) — this is exactly what Q1 tests.
And strain is the extension divided by the <i>original</i> length, not the final length.</p>
""",
  "Q1's options are combinations of σ, ε, L and A; knowing that σ is a pressure and ε is dimensionless is half the question.")

c("strainenergy", "E", 2, "Elastic strain energy", ["stressstrain", "ke"],
  "The energy stored in a stretched wire is the area under its force–extension graph: ½FΔL, which in material form is ½σε × volume.",
  """
<p>While you stretch a wire the force is not constant — it grows from 0 up to the final force F as Hooke's
law is obeyed. So the work done is (average force) × (extension):</p>
<div class="formula">W = ½ F ΔL        (the area of the triangle under a straight force–extension graph)</div>
<p>Now rewrite it in material language. F = σA and ΔL = εL, so:</p>
<div class="formula">W = ½ (σA)(εL) = ½ σ ε (A L) = ½ σ ε V        where V = AL is the volume of the wire</div>
<p>That is the answer to Q1: ½LAσε. And it makes sense dimensionally — σ is a pressure (J m⁻³) and ε is
dimensionless, so σεV is an energy: <i>energy stored per unit volume</i> is a neat way to read ½σε.</p>

<p><b>Two ways to check it.</b> Units: Pa × (no unit) × m³ = N m⁻² × m³ = N m = J ✓. Limiting case: double
the stress at fixed strain and you store twice as much energy, which the ½ × σ × ε × V form gives
directly.</p>

<p><b>Traps.</b> Using F·ΔL instead of ½F·ΔL — the half is there because the force builds up from zero,
and forgetting it is the single commonest error in this topic. And strain energy is not the same as the
total work if the material has passed its elastic limit: some energy is dissipated as heat and the wire
stays stretched.</p>
""",
  "Q1: ½LAσε, which is ½ × stress × strain × volume — or just ½ × final force × extension.")

c("specificheat", "J", 2, "Specific heat capacity: Q = mcΔT", ["ke"],
  "Warming something up takes energy proportional to its mass and to the temperature rise; the constant of proportionality is the material's specific heat capacity.",
  """
<p><b>Heat</b> is energy in transit because of a temperature difference; <b>temperature</b> is how hot
something is. They are different quantities, and the equation linking them is:</p>
<div class="formula">Q = m c ΔT        Q energy (J),  m mass (kg),  ΔT temperature change (K or °C),
c = specific heat capacity, J kg⁻¹ K⁻¹</div>
<p>Water's value is unusually large, 4200 J kg⁻¹ K⁻¹: it takes 4200 J to warm 1 kg of water by 1 °C. That
is why water is used as a coolant, and why coastal climates are mild. Copper is about 385, so it warms up
more than ten times faster for the same energy input.</p>

<p>Note that a change in kelvin equals the same change in degrees Celsius, so ΔT can be read straight off
a Celsius thermometer — you only need the absolute scale for gas laws.</p>

<p><b>Energy balance.</b> In an insulated cup, energy lost by the hot body = energy gained by the cold one.
Write one side as mcΔT for each body and equate. This is the whole method for “what is the final
temperature?” questions.</p>

<p><b>Traps.</b> Using grams instead of kilograms when c is quoted per kilogram — a factor of 1000. And
forgetting that if the final temperature is not given, the hot body cools only as far as the shared final
temperature, not to 0 °C.</p>
""",
  "Q15: the water can only give up mcΔT = 0.5 × 4200 × 20 = 42 kJ before it reaches 0 °C.")

c("latentheat", "J", 2, "Specific latent heat: Q = mL", ["specificheat"],
  "Melting needs energy with no change in temperature at all — the latent heat — so a two-stage calculation is needed whenever ice is involved.",
  """
<p>Put energy into ice at 0 °C and it melts into water at 0 °C: the temperature does not budge, yet
energy was absorbed. It went into breaking the bonds of the solid structure, not into making molecules
move faster (which is what temperature measures). The energy per kilogram is the <b>specific latent
heat</b>:</p>
<div class="formula">Q = m L          L (fusion, ice → water) ≈ 3.3 × 10⁵ J kg⁻¹
L (vaporisation, water → steam) ≈ 2.3 × 10⁶ J kg⁻¹</div>
<p>Latent heat of fusion for ice is about 80 times the energy needed to warm the same water by 1 °C —
which is why melting ice is so effective at cooling drinks, and why “just a few ice cubes” is a
substantial energy sink.</p>

<p><b>Example (Q15).</b> 500 g of water at 20 °C, ice cubes of 25 g at 0 °C, and we want the largest
number of cubes such that all the ice just melts (final temperature 0 °C). Energy available from the
water cooling to 0 °C:</p>
<div class="formula">Q = mcΔT = 0.5 × 4200 × 20 = 42 000 J
per cube: Q = mL = 0.025 × 3.3×10⁵ = 8250 J
how many cubes?  bracket the division instead of evaluating it:
5 cubes need 5 × 8250 = 41 250 J  ≤  42 000 J   ✓  enough
6 cubes need 6 × 8250 = 49 500 J   &gt;  42 000 J   ✗  not enough
→  5 whole cubes</div>
<p>The answer is 5, not 6: the sixth cube would not fully melt, so the final state would be ice and water
together at 0 °C — which contradicts “so that all the ice melts”. Whenever a question asks for a number
of discrete objects, <b>round down</b> and then sanity-check the boundary case.</p>

<p><b>Traps.</b> Forgetting the second stage — once the ice has melted it is water at 0 °C and must then
be warmed to the final temperature, which costs extra mcΔT. (Here the final temperature is 0 °C, so that
stage is free.) And using the latent heat of vaporisation when the change is melting.</p>
""",
  "Q15: 5 cubes, because 6 would need 49.5 kJ and only 42 kJ is available.")

# ───────────────────────────── STAGE 3 · WAVES AND OPTICS ─────────────────────────────

c("waves", "F", 3, "What a wave is: wavelength, frequency and speed", [],
  "A wave carries energy without carrying matter; wavelength, frequency and speed are tied together by v = fλ.",
  """
<p>In a wave, the particles of the medium oscillate about fixed positions while the <b>pattern</b> travels.
Nothing is transported except energy and information.</p>
<div class="formula">λ  wavelength (m)     distance between two successive crests
f  frequency (Hz)     number of complete cycles per second
T  period (s)         time for one cycle, T = 1/f
v  speed (m s⁻¹)      how fast the pattern travels</div>
<p>In one period the pattern advances one wavelength, so speed = distance/time = λ/T = fλ:</p>
<div class="formula">v = f λ</div>
<p>For light in a vacuum, v = c = 3.0 × 10⁸ m s⁻¹ and that never changes; changing the medium changes λ,
not f. <b>Frequency is set by the source and stays constant when a wave crosses a boundary</b> — this is
the fact that makes refraction work.</p>

<p><b>Traps.</b> Thinking the medium travels with the wave (a floating boat bobs up and down, it does not
surf along); and thinking frequency changes at a boundary — it is the wavelength that changes.</p>
""",
  "Q5's path difference has to be compared with λ = 1.8 m; Q9's first harmonic uses v = fλ.")

c("superposition", "F", 3, "Superposition and interference", ["waves"],
  "When two waves overlap the displacements simply add — and whether the result is big or zero depends on how the crests line up.",
  """
<p>The <b>principle of superposition</b> says that where two waves meet, the resultant displacement is the
algebraic sum of the individual displacements. Nothing else happens: the waves pass through each other
and carry on unchanged.</p>
<div class="formula">crest meets crest  (in phase)        →  amplitudes add      →  constructive
crest meets trough (out of phase)    →  amplitudes subtract →  destructive</div>
<p>With two equal amplitudes A, perfect constructive interference gives 2A and perfect destructive gives
0. With unequal amplitudes you never get complete cancellation.</p>

<p><b>Partial interference.</b> If the waves are part-way between in-phase and out-of-phase, you get
something in between — “mostly constructive” or “mostly destructive”. That is what Q5 asks about, which
is why “not enough information” is the wrong answer: the path difference in wavelengths tells you exactly
where on the spectrum you are.</p>

<p><b>Traps.</b> Thinking waves “bounce off” each other (they pass through); and assuming interference
needs two separate sources — a single source split along two paths (as here) works perfectly well, which
is the whole point of coherence.</p>
""",
  "Q5: two waves from the same source arrive with a path difference of 7.5 m out of λ = 1.8 m.")

c("pathphase", "F", 3, "From path difference to phase difference", ["superposition", "waves"],
  "Divide the path difference by the wavelength: the whole number tells you nothing, and the fraction tells you exactly how the waves combine.",
  """
<p>If one wave has travelled further than the other by a distance Δx, that extra distance corresponds to a
certain fraction of a cycle. Since one full wavelength is one full cycle:</p>
<div class="formula">phase difference (in cycles) = Δx / λ
phase difference (radians)   = 2π · Δx/λ
phase difference (degrees)   = 360° · Δx/λ</div>
<p>The <b>whole-number part is irrelevant</b>: being 3 wavelengths behind is the same as being in step,
because the wave repeats. Only the <b>fractional part</b> matters:</p>
<div class="formula">fraction 0      →  in phase             →  fully constructive
fraction ½      →  exactly out of step  →  fully destructive
fraction ¼ or ¾ →  quarter-cycle off    →  in between</div>
<p><b>Example (Q5).</b> λ = 1.8 m and Δx = 7.5 m:</p>
<div class="formula">7.5 / 1.8 = 75/18 = 25/6 = 4 + 1/6 of a cycle
whole part: 4            (irrelevant — the wave repeats)
fraction:   1/6 of a cycle</div>
<p>Cancel the fraction first: 75/18 divides by 3 top and bottom, giving 25/6, and 25/6 is 4 with 1 left over,
so the excess is <b>one sixth of a cycle</b> — no division to carry out. Compare 1/6 against the
quarter-cycle midpoint by cross-multiplying: 1 × 4 &lt; 6 × 1, so 1/6 &lt; 1/4 and the waves are
nearer in step than out of step. The result is <b>mostly constructive</b>. You can see the same thing without
any arithmetic: 7.5 m is 4 whole wavelengths (7.2 m) plus 0.3 m, and 0.3 m out of 1.8 m is a sixth of a
cycle — far from the half-cycle needed for cancellation.</p>

<p><b>Traps.</b> Forgetting to discard the whole number of wavelengths (the commonest error); and converting
to radians when the question only needs the fraction — the fraction of a cycle is the direct answer.</p>
""",
  "Q5: 7.5/1.8 = 4 + 1/6 wavelengths → excess 1/6, which is under the 1/4 midpoint → mostly constructive.")

c("coherence", "F", 3, "Coherence: what two sources need in order to interfere", ["superposition", "waves"],
  "Two sources only produce a steady interference pattern if they keep a constant phase relationship — which in practice means the same frequency and a fixed phase difference.",
  """
<p><b>Coherence</b> means a constant phase difference. Two sources are coherent when they have the same
frequency and their phase difference does not drift. If the phase difference wanders, the interference
pattern shifts around faster than the eye (or detector) can follow and you just see an average — no
visible pattern.</p>

<p>Because of this, interference in school physics is almost always produced by taking <b>one</b> source
and splitting it into two paths: a single lamp behind a double slit, a single laser in a split-beam
arrangement, or — as in Q5 — the same source sending waves along two routes to the same detector.
Splitting one source guarantees coherence, because the two copies start in phase.</p>

<p>The reason two separate lamps cannot do it: their atoms emit in random, unrelated bursts, so the phase
difference changes randomly millions of times a second.</p>

<p><b>Traps.</b> Thinking “coherent” means “same amplitude” (it does not — equal amplitude is a separate
condition that only decides whether cancellation is <i>complete</i>); and thinking lasers are coherent
because they are bright (they are coherent because of how the light is generated).</p>
""",
  "Q5 states both waves come from the same source — that is what licenses the interference calculation.")

c("standingwaves", "F", 3, "Standing waves on a string", ["waves", "superposition"],
  "Fix a string at both ends and only certain wavelengths fit; the lowest is half a wavelength per loop, giving f₁ = (1/2L)√(T/μ).",
  """
<p>Send waves along a string fixed at both ends and they reflect from the ends. The forward and backward
waves superpose, and at most frequencies the result is a mess. At certain frequencies, though, the
reflected wave lines up with the incoming one and a <b>standing wave</b> forms: a pattern that does not
travel, with points that never move (<b>nodes</b>) and points of maximum swing (<b>antinodes</b>).</p>

<p>The condition is that the string length must contain a whole number of half-wavelengths, because a
node is needed at each fixed end:</p>
<div class="formula">L = n λ / 2        n = 1, 2, 3, …
λ_n = 2L / n
f_n = v / λ_n = n v / (2L)        with  v = √(T/μ)</div>
<p>The lowest, n = 1, is the <b>first harmonic</b> (fundamental): one loop, nodes only at the ends,</p>
<div class="formula">f₁ = (1 / 2L) √(T / μ)</div>
<p>The set of allowed frequencies is f₁, 2f₁, 3f₁ … — all integer multiples, which is why a stringed
instrument sounds musical.</p>

<p><b>Traps.</b> Using L = λ for the first harmonic (it is L = λ/2); confusing harmonics (n = 1, 2, 3…)
with the number of loops or nodes; and forgetting that the wave speed v depends on tension and mass per
unit length, not on the frequency you drive it at.</p>
""",
  "Q9: two wires of the same length and material under the same force; f₁ ∝ 1/√(μ) and μ ∝ A.")

c("lineardensity", "F", 3, "Mass per unit length and wave speed on a string", ["standingwaves", "waves"],
  "The speed of a wave on a string is √(T/μ): tighter is faster, heavier is slower — and μ = ρA links it to the wire's thickness.",
  """
<p>Two things control how fast a transverse wave runs along a string: the tension T pulling it straight,
and the mass per unit length μ (linear density) resisting being accelerated sideways:</p>
<div class="formula">v = √(T / μ)        μ = mass / length, unit kg m⁻¹</div>
<p>Check the extremes: more tension → faster (a tight guitar string sounds higher); more mass per metre →
slower (the bass strings on a piano are thick and heavy). Dimensional check: T is a force, kg m s⁻²; μ is
kg m⁻¹; T/μ has units m² s⁻², so √(T/μ) is a speed ✓.</p>

<p><b>Connecting μ to the wire's size.</b> A wire of cross-sectional area A made of a material of density ρ
has mass per unit length:</p>
<div class="formula">μ = ρ A          (mass of one metre = density × volume of one metre = ρ × A × 1)</div>
<p>Put the two together with the resistance formula R = ρ<sub>e</sub>L/A and the dependencies start to
compete, which is exactly what Q9 is built on: a fatter wire is heavier (lower frequency) but has lower
resistance.</p>

<p><b>Traps.</b> Using the wire's total mass instead of mass per unit length; and using the electrical
resistivity symbol ρ for density — they share a letter, so always check which one the question means.</p>
""",
  "Q9: μ = ρA means a thicker wire lowers f₁, while R = ρL/A means it also lowers R; the ratio of the two effects gives 4:1.")

c("refractive", "G", 3, "Refractive index and the normal", ["waves"],
  "The refractive index n says how much a medium slows light down; angles in optics are measured from the normal, the line at 90° to the surface.",
  """
<p>Light travels at c = 3.0 × 10⁸ m s⁻¹ in a vacuum and more slowly in matter. The <b>refractive
index</b> of a medium is the ratio:</p>
<div class="formula">n = c / v        (≥ 1;  air ≈ 1.00,  water ≈ 1.33,  glass ≈ 1.5)</div>
<p>The bigger n is, the more the medium slows light, and the more sharply a ray bends on entering it.</p>

<p><b>The normal.</b> Every refraction question uses angles measured from the <b>normal</b> — an imaginary
line drawn at 90° to the surface at the point where the ray hits. This convention is not optional: the
sine rule of refraction only works with angles from the normal. If a diagram gives you the angle from the
surface, convert it: (angle from normal) = 90° − (angle from surface).</p>

<p><b>Which way does it bend?</b> Entering a <i>denser</i> medium (higher n) the ray slows and bends
<b>towards</b> the normal, so the angle to the normal gets smaller. Entering a less dense medium it bends
<b>away</b> from the normal. That single rule is a check on every answer.</p>

<p><b>Traps.</b> Measuring from the surface by mistake — the single most common optics error, and the
entire point of Q2. And thinking n is a property of the ray rather than of the medium.</p>
""",
  "Q2 asks for Snell's law with angles drawn from the surface; the whole question is this convention.")

c("snell", "G", 3, "Snell's law", ["refractive", "waves"],
  "n₁ sin θ₁ = n₂ sin θ₂ — the product of refractive index and the sine of the angle to the normal is conserved across a boundary.",
  """
<p>When a ray crosses from medium 1 into medium 2, the angles to the normal and the refractive indices are
linked by:</p>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂        so   sin θ₁ / sin θ₂ = n₂ / n₁</div>
<p><b>Where it comes from.</b> The frequency must be the same on both sides (it is set by the source), but
the speed changes from c/n₁ to c/n₂, so the wavelength changes in the same ratio. Matching the wavefronts
up along the boundary — the same number of crests must arrive on each side in the same time — gives
sin θ₁ / sin θ₂ = v₁ / v₂ = n₂ / n₁, which rearranges to the law above.</p>

<p><b>Sanity checks that catch sign and inversion errors:</b></p>
<ul>
<li>Going into a denser medium (n₂ &gt; n₁) means sin θ₂ &lt; sin θ₁, so the ray bends towards the normal ✓.</li>
<li>Hitting the boundary head-on (θ₁ = 0) gives θ₂ = 0: no bending along the normal ✓.</li>
<li>Swapping the two media must invert the ratio ✓.</li>
</ul>

<p><b>Worked (Q16).</b> Air to glass, n₂ = √2, angle of incidence 30°:</p>
<div class="formula">1 · sin 30° = √2 · sin θ₂
sin θ₂ = 0.5 / √2 = 1/(2√2) = 0.354</div>
<p><b>Stop here.</b> The paper is non-calculator, and θ₂ itself — about 20.7° — is a number
you cannot produce without a calculator and are never asked for. What you need is the <i>direction</i>:
<code>sin θ₂ = 0.354 &lt; sin 30° = 0.5</code>, so θ₂ &lt; 30°, so the ray has
bent <b>towards</b> the normal on entering the glass. That single inequality is the whole physical content of
the step, and it needs no arcsine. Carrying <code>sin θ₂</code> forward as an exact surd is also what
lets the next step give <code>cos θ₂</code> from <code>sin² + cos² = 1</code> without ever
evaluating an angle.</p>

<p><b>Traps.</b> Writing n₁ sin θ₂ = n₂ sin θ₁ (inverted — check it by asking which medium gives the
smaller angle); and using degrees/radians inconsistently when evaluating trig functions.</p>
""",
  "Q2 (with angles from the surface) and Q16 (finding the refracted angle in a glass cube).")

c("lightspeed", "G", 3, "Speed of light in a medium", ["refractive", "snell"],
  "v = c/n is the definition of refractive index, so the time to cross a thickness d at an angle is d' / v where d' is the actual path length.",
  """
<p>From the definition n = c/v, the speed in a medium of index n is:</p>
<div class="formula">v = c / n        (glass with n = 1.5: 2 × 10⁸ m s⁻¹, two thirds of c)</div>
<p><b>Time of flight.</b> Speed is constant inside a uniform medium, so time = distance/speed. But the
distance is the <i>path length travelled</i>, not the straight-through thickness — if the ray crosses at
an angle, it travels further.</p>

<p><b>Example (Q16).</b> A cube of side a, light entering at 30° to the normal, and we want the time to
reach the opposite face. From Snell's law the refracted angle θ₂ satisfies sin θ₂ = sin 30°/√2, so
cos θ₂ = √(1 − ⅛) = √(7/8). The ray travels along the hypotenuse, so the distance is a/cos θ₂ and:</p>
<div class="formula">path length = a / cos θ₂ = a / √(7/8) = a√(8/7)
speed       = c / n = c/√2
time        = a√(8/7) / (c/√2) = a·√(8/7)·√2 / c = a√(16/7) / c = 4a / (√7 c)</div>
<p>Note it is longer than a/c, as it must be: the ray goes slower than c and also travels further than a.</p>

<p><b>Traps.</b> Using the thickness a as the path length (that only works for a ray at 90° incidence);
and dividing by c instead of by c/n.</p>
""",
  "Q16: the time is (4/√7)·a/c — longer than a/c for two separate reasons.")
