# -*- coding: utf-8 -*-
"""Key points added by the 2025 SAMPLE questions (R0S-01..R0S-12).

Four ideas the sample sheet needs that the past paper never called for. Each is a
full lesson in the same shape as concepts_a/b/c: what it is, where it comes from,
the symbols and units, a worked example, and the trap.

  secondorder     stage 0  the sample sheet's S9. smallchange teaches you to throw
                           away products of two small quantities; this one covers the
                           case where the first-order term is zero and those products
                           are the whole answer.
  apparentweight  stage 1  S11. The normal reaction is not the weight, and the gap
                           between them is what circular motion costs.
  tailmass        stage 1  S12. Which mass a given string has to accelerate.
  criticalangle   stage 3  S8. theta_c = arcsin(1/n) and, just as importantly, the
                           shape of that curve.
"""

C = [

{
    "id": "secondorder", "m": "A", "stage": 0,
    "t": "When the leading term cancels: energies that scale as the fourth power",
    "pre": ["smallchange", "surds"],
    "one": "Sometimes a small change produces no first-order effect at all, and the answer is governed by the "
           "term you were told to throw away — which is why a sideways nudge of a spring stores so little energy.",
    "body": """<p><b>The idea.</b> The point of a small-change expansion is that the first-order term usually dominates and everything smaller can be dropped. But occasionally the first-order term <b>vanishes</b>. When that happens the product-of-two-small-quantities term — the one you were told to discard — is not a correction to the answer; it <i>is</i> the answer, and it is much smaller than a first-order estimate would suggest.</p>
<p><b>Where it comes from.</b> Take a spring of natural length <code>a</code> and stretch it to length <code>L</code>. The extension is <code>L − a</code>. Now suppose the increase in <code>L</code> comes not from stretching the spring along its own direction but from moving one end <b>sideways</b> — perpendicular to the spring. The spring becomes the hypotenuse of a right-angled triangle whose other two sides are <code>a</code> and <code>d</code>:</p>
<div class="formula">L = √(a² + d²)</div>
<p>The hypotenuse grows with <code>d</code>, but very slowly at first. Pull out a factor of <code>a</code> and expand:</p>
<div class="formula">L = a √(1 + d²/a²)
  ≈ a (1 + d²/(2a²))
  = a + d²/(2a)

extension  x = L − a ≈ d² / (2a)</div>
<p><b>Read the power of the small quantity.</b> There is no term proportional to <code>d</code> at all. The extension is <b>second order</b> in <code>d</code>. Halve <code>d</code> and the extension falls to a quarter, not a half. That is the whole point, and it is why a sideways displacement is such an inefficient way to store energy in a stretched spring.</p>
<p><b>Symbols and units.</b> <code>a</code> and <code>d</code> are lengths, in metres; <code>x</code> is the extension, also in metres. The expression <code>d²/(2a)</code> is (m²)/m = m, so the units are right. The spring constant <code>k</code> is in N m⁻¹, so the energy <code>½kx²</code> comes out in N m = J.</p>
<p><b>Worked example (S9 of the sample sheet).</b> Three ideal springs of constant <code>k</code> and natural length <code>a</code> run from a point <code>P</code> to three fixed points <code>A</code>, <code>B</code>, <code>C</code>, each a distance <code>a</code> from <code>P</code>. So every spring starts at its natural length and stores nothing. Then <code>P</code> moves a small distance <code>d</code> perpendicular to the plane of <code>A</code>, <code>B</code> and <code>C</code>.</p>
<p>The perpendicular displacement is square to all three springs, so each one becomes a hypotenuse <code>√(a² + d²)</code> — the same for all three, which is exactly why the question says "equidistant". Each spring's extension is <code>d²/(2a)</code>, so each stores</p>
<div class="formula">½ k x² = ½ k (d²/(2a))² = ½ k × d⁴/(4a²) = k d⁴ / (8a²)</div>
<p>and the total is</p>
<div class="formula">U = 3 k d⁴ / (8a²)</div>
<p><b>Traps.</b> The first is treating the extension as <code>d</code> and writing <code>½kd²</code> per spring, which is the energy of a spring stretched <i>along</i> its own length by <code>d</code> — a different physical situation. The second is squaring carelessly: the extension is <code>d²/(2a)</code>, so the energy contains <code>(d²)²</code>, which is <code>d⁴</code>, and it also contains <code>(1/2)² = 1/4</code> from the denominator. Both the factor of four and the fourth power come from the same place, and dropping either gives an answer that is wrong by a factor you can see in the option list.</p>
<p><b>The general rule.</b> Before applying a small-change expansion, check whether the leading term cancels. Two tests catch it every time: does the expression depend on the sign of the small quantity? (If <code>+d</code> and <code>−d</code> give the same answer, the first-order term cannot be present.) And is there a symmetry that forces the change to vanish to first order? A sideways nudge of a spring, a sideways nudge of a pendulum bob, and the volume change of a squeezed sphere all share this behaviour.</p>
<p><b>Where the sample sheet uses it:</b> S9.</p>""",
    "used": "S9 asks for the energy stored in three springs after a small perpendicular displacement — the extension is second order in the displacement, so the energy is fourth order.",
},

{
    "id": "apparentweight", "m": "D", "stage": 1,
    "t": "Apparent weight: the normal reaction is not the weight",
    "pre": ["circular", "force"],
    "one": "The reading of a scale is the normal reaction, not mg. Wherever something is travelling in a circle, "
           "the normal reaction is smaller than the weight by exactly the centripetal force required.",
    "body": """<p><b>The idea.</b> "Weight" is the gravitational pull <code>mg</code>. What you actually <i>feel</i>, and what a scale reads, is the <b>normal reaction</b> <code>N</code> the surface pushes back with. In most school problems the two are equal, and it is easy to forget that this is a <i>result</i>, not a definition. Under circular motion they differ, and the difference is the whole content of this page.</p>
<p><b>Where it comes from.</b> Newton's second law, applied to the vertical direction, for a mass sitting on the ground at latitude where it must travel in a circle of radius <code>r</code> about the Earth's axis with angular speed <code>ω</code>:</p>
<div class="formula">resultant downward force = centripetal requirement
mg − N = m ω² r</div>
<p>So</p>
<div class="formula">N = mg − m ω² r</div>
<p>The surface pushes up with <i>less</i> than the weight. The missing force is not lost; it is the net downward force that keeps the object going round in a circle. If <code>ω²r</code> ever reached <code>g</code>, then <code>N</code> would fall to zero — nothing would be needed from the ground, and the object would float. That is the condition for being in orbit, and it is why astronauts are weightless rather than outside gravity.</p>
<p><b>Symbols and units.</b> <code>m</code> in kg, <code>g</code> in m s⁻², <code>ω</code> in rad s⁻¹, <code>r</code> in m. Then <code>mω²r</code> is kg × s⁻² × m = kg m s⁻² = N, a force. ✓ The quantity <code>ω²r</code> is an acceleration, and comparing it with <code>g</code> is often the fastest way to see how big an effect it is.</p>
<p><b>Worked example (S11 of the sample sheet).</b> A rock sits at the North pole and then at the equator; the Earth's radius is given as <code>6 × 10⁶ m</code>. Find <code>(N₁ − N₂)/N₁</code>.</p>
<p>At the pole the rock is <b>on the axis of rotation</b>, so <code>r = 0</code>: it does not travel in a circle at all and the centripetal term vanishes. Hence <code>N₁ = mg</code>. This is the step people miss — the pole is special not because it is "the top" but because its distance from the axis is zero.</p>
<p>At the equator <code>r = R</code>, and the required centripetal force is directed towards the axis, which at the equator means straight down. So <code>mg − N₂ = mω²R</code>.</p>
<div class="formula">(N₁ − N₂) / N₁ = (mg − (mg − mω²R)) / mg = ω²R / g</div>
<p>The mass cancels, so a pebble and a person give the same answer. Now estimate. One day is about <code>8.6 × 10⁴ s</code>:</p>
<div class="formula">ω = 2π / T ≈ 6.3 / (8.6 × 10⁴) ≈ 7.3 × 10⁻⁵ rad s⁻¹
ω²R / g ≈ (7.3 × 10⁻⁵)² × 6 × 10⁶ / 10 ≈ 3.2 × 10⁻³ ≈ 0.3%</div>
<p><b>Traps.</b> The first is adding the centripetal term instead of subtracting it, which would mean the ground pushes harder at the equator than at the pole. The second is using the sidereal day (86164 s) rather than the solar day (86400 s); the difference is about 0.3%, far below the resolution of a question whose options are a factor of ten apart. The third, and the one the sample sheet is testing, is slipping a power of ten: all five options differ only in where the decimal point sits.</p>
<p><b>Related effects worth knowing.</b> The same <code>ω²R/g</code> governs the Earth's equatorial bulge — the planet is about 0.3% wider across the equator than pole to pole. It is also why launch sites near the equator get a small free boost, and why the effective value of <code>g</code> measured at the equator is slightly smaller than at the pole for two reasons, not one.</p>
<p><b>Where the sample sheet uses it:</b> S11.</p>""",
    "used": "S11 compares the normal reaction on a rock at the pole with the same rock at the equator; the ratio comes out as the centripetal acceleration divided by g.",
},

{
    "id": "tailmass", "m": "C", "stage": 1,
    "t": "What a string has to drag: the mass on the far side of the boundary",
    "pre": ["force", "ratio"],
    "one": "A tension is the force one string applies at one place, so it accelerates only the mass on the far side of "
           "that string — not the whole chain, and not the block it is tied to.",
    "body": """<p><b>The idea.</b> In a chain of connected bodies the hard part is never the algebra; it is deciding <i>which</i> mass each unknown force is responsible for. Get that right and Newton's second law finishes the job in one line.</p>
<p><b>Where it comes from.</b> A light inextensible string does two things: it transmits a force along itself, and it guarantees that the bodies at its two ends share an acceleration. So if you cut the chain at a string and look at everything on the far side, the only horizontal force on that group is the tension in the cut string. Everything on the near side is irrelevant to it.</p>
<p><b>The rule.</b> For a string lying immediately <i>behind</i> block <code>n</code> (counting from the pulled end):</p>
<div class="formula">T(n) = (total mass on the far side of that string) × a</div>
<p>Every body in the chain has the same acceleration <code>a</code>, so this is just Newton's second law applied to a system whose only external horizontal force is the one tension.</p>
<p><b>Symbols and units.</b> Masses in kg, acceleration in m s⁻², so <code>T</code> comes out in kg m s⁻² = N. The driving force <code>D</code> obeys the same law applied to the whole chain at once.</p>
<p><b>A geometric series, in one line.</b> Say the masses halve going back from the front. Number from the front so block 1 has mass <code>m</code>, block 2 has <code>m/2</code>, block 3 has <code>m/4</code>, and block <code>n</code> has <code>m/2<sup>n−1</sup></code>. The mass behind block <code>n</code> is</p>
<div class="formula">m/2ⁿ + m/2<sup>n+1</sup> + m/2<sup>n+2</sup> + ...  =  (m/2ⁿ) × (1 + 1/2 + 1/4 + ...)  =  (m/2ⁿ) × 2  =  m / 2<sup>n−1</sup></div>
<p>The sum <code>1 + 1/2 + 1/4 + ... = 2</code> is worth remembering: a chain that halves forever weighs exactly twice its first link, and no more.</p>
<p><b>Worked example (S12 of the sample sheet).</b> The chain is pulled with force <code>D</code> and accelerates at <code>a</code>. The whole chain has mass <code>2m</code>, so <code>D = 2ma</code>, giving <code>ma = D/2</code>. The tension behind block <code>n</code> is</p>
<div class="formula">Tₙ = (m / 2<sup>n−1</sup>) a = ma × 2<sup>1−n</sup></div>
<p>To write it as <code>D − f(n)ma</code>, compute the shortfall:</p>
<div class="formula">D − Tₙ = 2ma − ma × 2<sup>1−n</sup> = ma (2 − 2<sup>1−n</sup>)   ⇒   f(n) = 2 − 2<sup>1−n</sup></div>
<p><b>Verify it at the first case, always.</b> At <code>n = 1</code>, <code>2<sup>1−1</sup> = 1</code>, so <code>T₁ = D − ma = ma</code>. And you can write <code>T₁</code> down without any algebra: the string behind the front block tows a tail of total mass <code>m/2 + m/4 + ... = m</code>, so <code>T₁ = ma</code>. ✓ The two agree, and the check costs ten seconds.</p>
<p><b>Traps.</b> Taking <code>Tₙ</code> to be the force accelerating block <code>n</code> itself, rather than the tail behind it. Confusing <code>ma</code> with <code>D</code> — the whole chain's mass is <code>2m</code>, so <code>ma</code> is only half the driving force. And when a multiple-choice list offers two formulas that differ in one digit of an exponent, do not choose between them by eye: substitute <code>n = 1</code> and compare with the value you can derive from first principles.</p>
<p><b>Where the sample sheet uses it:</b> S12.</p>""",
    "used": "S12 draws the strings of a chain whose masses halve going back from the pulled end, and asks which tension formula is right.",
},

{
    "id": "criticalangle", "m": "G", "stage": 3,
    "t": "The critical angle, and the shape of the curve against refractive index",
    "pre": ["snell", "refractive"],
    "one": "Going from a medium of index n into air, the critical angle satisfies sin θ꜀ = 1/n — so it starts at 90° "
           "just above n = 1, falls steeply, and flattens without ever reaching zero.",
    "body": """<p><b>The idea.</b> When light tries to leave a dense medium at a shallow enough angle to the boundary, it does not leave at all: it is all reflected back. That angle is the critical angle, and its size depends on the refractive index.</p>
<p><b>Where it comes from.</b> Snell's law for light going from a medium of index <code>n</code> into air (<code>n = 1</code>):</p>
<div class="formula">n sin θ₁ = 1 × sin θ₂</div>
<p>Total internal reflection begins at the incident angle for which the refracted ray grazes the boundary, so <code>θ₂ = 90°</code> and <code>sin θ₂ = 1</code>:</p>
<div class="formula">n sin θ꜀ = 1
sin θ꜀ = 1 / n
θ꜀ = arcsin(1 / n)</div>
<p><b>Read the formula for its behaviour, not just its value.</b> Three facts follow immediately, and questions about this relation are almost always testing one of them rather than the arithmetic:</p>
<p>· <b>Direction.</b> As <code>n</code> increases, <code>1/n</code> decreases, so <code>θ꜀</code> decreases. A denser medium traps light more easily.</p>
<p>· <b>Steep at the start.</b> At <code>n = 1</code> there is no denser medium, no critical angle, and the curve leaves the top of the axis vertically. That is why the correct sketch has a near-vertical opening stroke: the function is only defined for <code>n ≥ 1</code>, and its slope there is infinite.</p>
<p>· <b>Never reaches zero.</b> To make <code>1/n</code> zero you would need infinite <code>n</code>, which no material has. The curve approaches the axis asymptotically and never touches it.</p>
<p>These sections are shown here at the same scale for clarity, so the curves can be compared directly:</p>
<p><b>Angles worth knowing exactly.</b> Pick values of <code>n</code> whose reciprocals you recognise:</p>
<div class="formula">n = 1   →  θ꜀ = 90°   (the grazing case)
n = √2  →  sin θ꜀ = 1/√2 = 0.707  →  θ꜀ = 45°
n = 2   →  sin θ꜀ = 1/2  →  θ꜀ = 30°
n = 3   →  sin θ꜀ = 1/3  →  θ꜀ ≈ 19°</div>
<p><b>Symbols and units.</b> <code>n</code> is dimensionless, being a ratio of two speeds. <code>θ꜀</code> is an angle, quoted in degrees here. Since <code>sin θ꜀ = 1/n</code>, the only value with an exact round-number answer is <code>n = 2</code> giving 30°, plus <code>n = √2</code> giving 45° and <code>n = 1</code> giving 90°. That is enough to pin the shape down, and a competition question will be answerable with just those.</p>
<p><b>Worked example (S8 of the sample sheet).</b> Which sketch shows how <code>θ꜀</code> changes with <code>n</code>? Two of the five rise, so they are gone. Of the three that fall, one is a <b>straight line</b> running down to the axis, one is <b>flat and then plunging</b>, and one <b>falls steeply and then flattens</b>. Only the last has the shape of <code>arcsin(1/n)</code>. The straight-line option would mean the critical angle reaches zero at some finite index, after which total internal reflection would be impossible — which is not what the function does. The flat-then-plunging option has the curvature the wrong way round: it says the angle barely changes for small <code>n</code>, whereas in fact that is where it changes fastest.</p>
<p><b>Traps.</b> Answering only the direction of the trend. "It falls" is true of three of the five options, so it cannot decide the question: the <b>curvature</b> and the <b>endpoint</b> are the physics being tested. The second trap is using <code>sin θ꜀ = n</code> instead of <code>1/n</code>, which reverses the trend entirely and would make the critical angle grow without limit.</p>
<p><b>Where it is seen in practice.</b> A diamond (about 2.4) has a critical angle near 25°, which is why it sparkles so much: light entering the top face is reflected internally many times before escaping. Water (about 1.33) has one near 49°, which is why the surface of a pool looks like a mirror when you look at it from underneath at a shallow angle.</p>
<p><b>Where the sample sheet uses it:</b> S8.</p>""",
    "used": "S8 asks which of five sketches shows how the critical angle changes with refractive index; only the steep-then-flattening curve matches arcsin of one over n.",
},

]
