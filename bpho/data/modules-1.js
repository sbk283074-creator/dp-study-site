/* BPhO Round 0 — curriculum, part 1 of 6.
   Module A: working skills and mathematical toolkit. */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "A",
  title: "Working skills and mathematical toolkit",
  short: "Toolkit",
  priority: 1,
  tier: "Tier A — official sample paper and BPhO's own constant sheet",
  why: "This is not a topic, it is the reason the paper is hard. Twenty-five questions in sixty minutes with no calculator means about two and a half minutes each. The questions that look impossible are almost never testing obscure physics — they are testing whether you reach for a ratio, a dimensional argument or a limiting case instead of grinding out arithmetic you have no calculator for.",
  warn: "<p><b>Read this whole module before any other.</b> Dimensional analysis alone accounts for about one question in six on the official sample paper, and the AQA specification states outright that <i>dimensional analysis is not required</i> at A-level. So this is material you cannot pick up from a textbook — it is BPhO-specific, and it is cheap.</p>",

  sections: [
    {
      h: "Why the toolkit outranks every topic",
      body: `<p>The paper is 25 single-answer multiple-choice questions, 60 minutes, no calculator. That works out at 2.4 minutes per question including reading time. Two consequences follow, and everything in this module is a response to one of them.</p>
<ul class="tight">
<li><b>You cannot compute your way out.</b> Any question that needs long division is a question you have already lost. The winning move is almost always to divide two expressions so the awkward constants cancel, leaving a ratio.</li>
<li><b>You can always eliminate.</b> There is no negative marking, so a blank is strictly worse than a guess. And a surprising number of wrong options can be killed without doing any physics at all — by checking units, by checking a limiting case, or by checking which graph has the right shape.</li>
</ul>
<p>The official sample paper confirms this. Question S10 is a pure dimensional-analysis question. S8 and S12 both turn on limiting cases. S9 is built on the geometric approximation below. None of these would appear on a standard A-level paper.</p>
<div class="callout callout--key"><p><b>The strategic point.</b> If you learn only one thing in the whole two weeks, learn to ask, before writing anything down: <i>is this a ratio question, a dimensions question, or an elimination question?</i> Most of the paper is one of those three.</p></div>`
    },

    {
      h: "Step 1 — Reduce any unit to base units",
      body: `<p>There are seven SI base units. Round 0 will only ever need the first six.</p>
<table><thead><tr><th>Quantity</th><th>Unit</th><th>Symbol</th></tr></thead><tbody>
<tr><td>mass</td><td>kilogram</td><td>kg</td></tr>
<tr><td>length</td><td>metre</td><td>m</td></tr>
<tr><td>time</td><td>second</td><td>s</td></tr>
<tr><td>electric current</td><td>ampere</td><td>A</td></tr>
<tr><td>temperature</td><td>kelvin</td><td>K</td></tr>
<tr><td>amount of substance</td><td>mole</td><td>mol</td></tr>
<tr><td>luminous intensity</td><td>candela</td><td>cd</td></tr>
</tbody></table>
<p>Everything else is built from these. The technique is always the same: <b>take the defining equation, substitute the base-unit form of everything on the right, and simplify.</b> Do it once for each unit below and you will never need to look them up again.</p>
<table><thead><tr><th>Unit</th><th>Defining equation</th><th>In base units</th></tr></thead><tbody>
<tr><td>N — newton</td><td><code>F = ma</code></td><td>kg m s⁻²</td></tr>
<tr><td>J — joule</td><td><code>W = Fs</code></td><td>kg m² s⁻²</td></tr>
<tr><td>W — watt</td><td><code>P = W/t</code></td><td>kg m² s⁻³</td></tr>
<tr><td>Pa — pascal</td><td><code>p = F/A</code></td><td>kg m⁻¹ s⁻²</td></tr>
<tr><td>C — coulomb</td><td><code>Q = It</code></td><td>A s</td></tr>
<tr><td>V — volt</td><td><code>V = W/Q</code></td><td>kg m² s⁻³ A⁻¹</td></tr>
<tr><td>Ω — ohm</td><td><code>R = V/I</code></td><td>kg m² s⁻³ A⁻²</td></tr>
<tr><td>F — farad</td><td><code>C = Q/V</code></td><td>kg⁻¹ m⁻² s⁴ A²</td></tr>
<tr><td>T — tesla</td><td><code>F = BIL</code></td><td>kg s⁻² A⁻¹</td></tr>
</tbody></table>
<h3>Two of them worked in full</h3>
<p><b>Volt.</b> A volt is a joule per coulomb. A joule is kg m² s⁻², and a coulomb is A s. So</p>
<div class="formula">1 V = 1 J C⁻¹ = (kg m² s⁻²) / (A s) = kg m² s⁻³ A⁻¹</div>
<p><b>Farad.</b> This one is worth doing slowly because it comes up in the sample paper. Capacitance is charge per volt, so a farad is a coulomb per volt. Substituting the volt we just found:</p>
<div class="formula">1 F = 1 C V⁻¹ = (A s) / (kg m² s⁻³ A⁻¹) = A² s⁴ kg⁻¹ m⁻²</div>
<p>Note the negative exponents on kg and m. That is what makes the farad recognisable when it appears inside a dimensional-analysis answer: a positive power of kg or m in a capacitance context is a sign you have slipped.</p>
<div class="callout callout--warn"><p><b>Prefixes.</b> T (10¹²), G (10⁹), M (10⁶), k (10³), c (10⁻²), m (10⁻³), μ (10⁻⁶), n (10⁻⁹), p (10⁻¹²), f (10⁻¹⁵). Note that <code>m</code> is both metre and milli- and <code>f</code> is both femto- and the farad symbol. Context decides, but the paper will not be ambiguous.</p></div>`
    },

    {
      h: "Step 2 — Dimensional analysis: deriving the form of a relationship",
      body: `<p>This is the single most valuable technique in the module. The question gives you a list of physical quantities and asks for the form of the relationship between them, with no numbers. You do not need to know any physics — only the units.</p>
<h3>The method, in five moves</h3>
<ol class="steps">
<li><b>List the quantities the answer can depend on</b>, with their dimensions. The question almost always names them.</li>
<li><b>Assume a product form</b>: <code>result = k × (quantity 1)<sup>a</sup> × (quantity 2)<sup>b</sup> × …</code> where <code>k</code> is a dimensionless constant.</li>
<li><b>Write the dimensions of both sides</b>, using M, L, T for mass, length and time (add I for current and Θ for temperature if needed).</li>
<li><b>Equate the exponents</b> of M, L, T separately. That gives you a set of simultaneous equations.</li>
<li><b>Solve for a, b, c.</b> Then state the answer with <code>k</code> left unknown.</li>
</ol>
<div class="callout callout--bad"><p><b>The limitation, and it is tested.</b> Dimensional analysis gives you the <i>form</i> of the relationship but never the dimensionless constant. The period of a pendulum comes out as <code>T = k√(ℓ/g)</code>, and the method cannot tell you that <code>k = 2π</code>. If an option offers you <code>2π√(ℓ/g)</code> and another offers <code>√(ℓ/g)</code>, the dimensional argument alone cannot separate them — you have to know the physics, or use a limiting case.</p></div>
<h3>Worked derivation: speed of a wave on a stretched string</h3>
<p>Suppose the speed <code>v</code> of a transverse wave on a string depends only on the tension <code>T</code> and the mass per unit length <code>μ</code>. Find the form of the relationship.</p>
<ol class="steps">
<li>Quantities: <code>v</code> (m s⁻¹), <code>T</code> (N = kg m s⁻²), <code>μ</code> (kg m⁻¹).</li>
<li>Assume <code>v = k T<sup>a</sup> μ<sup>b</sup></code>.</li>
<li>Dimensions: left side is L T⁻¹. Right side is (M L T⁻²)<sup>a</sup> (M L⁻¹)<sup>b</sup> = M<sup>a+b</sup> L<sup>a−b</sup> T<sup>−2a</sup>.</li>
<li>Equate: for M, <code>a + b = 0</code>. For L, <code>a − b = 1</code>. For T, <code>−2a = −1</code>.</li>
<li>From T: <code>a = ½</code>. Then from M: <code>b = −½</code>. Check L: <code>½ − (−½) = 1</code> ✓.</li>
</ol>
<div class="formula">v = k √(T/μ)</div>
<p>The physics supplies <code>k = 1</code>, so <code>v = √(T/μ)</code> — which is the standard result, and you have just derived it without knowing anything about waves.</p>
<h3>The same method on a pendulum</h3>
<p>Period <code>T</code> depends on length <code>ℓ</code>, mass <code>m</code> and gravitational field strength <code>g</code>. Assume <code>T = k ℓ<sup>a</sup> m<sup>b</sup> g<sup>c</sup></code>.</p>
<div class="formula">L⁰ M⁰ T¹ = L<sup>a</sup> · M<sup>b</sup> · (L T⁻²)<sup>c</sup>
M: b = 0
L: a + c = 0
T: −2c = 1  →  c = −½,  so a = ½</div>
<p>Mass cancels out entirely, which is the physical fact that the period of a pendulum does not depend on the mass of the bob. The result is <code>T = k√(ℓ/g)</code>. Note how the method discovered a physical fact — mass independence — as a by-product.</p>`
    },

    {
      h: "Step 3 — Checking an equation for dimensional consistency",
      body: `<p>The other half of dimensional analysis, and the faster of the two. Every additive term in a correct equation must have identical dimensions. If it does not, the equation is wrong — no exceptions, no physics required.</p>
<p>So when a question asks "which of these expressions could be correct", you do not evaluate anything. You check the dimensions of each option and discard the ones that fail.</p>
<h3>The three checks worth doing, in order</h3>
<ol class="tight">
<li><b>Do the additive terms match?</b> In <code>a = b + c</code>, the dimensions of <code>b</code> and <code>c</code> must be the same as each other.</li>
<li><b>Do the two sides match?</b> Reduce the whole left side and the whole right side.</li>
<li><b>Does a special function have a dimensionless argument?</b> Anything inside <code>sin</code>, <code>cos</code>, <code>tan</code>, <code>log</code> or <code>exp</code> must be dimensionless. An expression containing <code>sin(ωt)</code> is fine because <code>ωt</code> is dimensionless; <code>sin(mv)</code> cannot be right.</li>
</ol>
<div class="callout callout--key"><p><b>Watch the trig functions.</b> An angle is dimensionless, which means <code>sin θ</code>, <code>tan θ</code> and <code>θ</code> all have the same dimensions. This is exactly why the small-angle approximations are legitimate: they are replacing one dimensionless quantity with another.</p></div>
<h3>One worked check</h3>
<p>Is <code>v² = u² + 2as</code> dimensionally consistent?</p>
<ul class="tight">
<li><code>v²</code> is (m s⁻¹)² = m² s⁻².</li>
<li><code>u²</code> is also m² s⁻² ✓.</li>
<li><code>2as</code> is (m s⁻²)(m) = m² s⁻² ✓.</li>
</ul>
<p>All three terms agree, so the equation survives the check. Dimensional consistency does not prove an equation is right — a wrong equation can still balance — but inconsistency proves it is wrong. That asymmetry is what makes it a useful filter on a multiple-choice paper.</p>`
    },

    {
      h: "Step 4 — Ratio reasoning",
      body: `<p>Most Round 0 questions ask for something like "the speed becomes <i>n</i> times the original" or "the ratio of the two powers is". The point is that the awkward constants are the <b>same</b> in both situations, so they divide out. You never compute them.</p>
<h3>The method</h3>
<ol class="steps">
<li>Write the relevant equation in symbolic form.</li>
<li>Write it again for the second situation.</li>
<li>Divide one by the other. Everything that did not change cancels.</li>
<li>Substitute the ratio of the changed quantities and simplify.</li>
</ol>
<h3>Worked example: stopping distance</h3>
<p>A car travelling at speed <code>v</code> skids to rest in distance <code>s</code>. What happens to <code>s</code> if the initial speed is tripled, with the same braking force?</p>
<p>Use the work–energy idea: the braking force does work over the stopping distance, removing the kinetic energy.</p>
<div class="formula">Fs = ½mv²   →   s = mv² / (2F)</div>
<p>Now take the ratio of the two situations. The mass and the force are unchanged:</p>
<div class="formula">s₂ / s₁ = (v₂/v₁)² = 3² = 9</div>
<p>The stopping distance is nine times as long. No numbers, no calculator, about fifteen seconds. That is the whole point of the technique.</p>
<div class="callout callout--good"><p><b>Train the reflex.</b> Whenever a question says "how many times", "the ratio of", or "by what factor", stop calculating and start dividing. If you find yourself multiplying out <code>9.81</code>, you have misread the question.</p></div>`
    },

    {
      h: "Step 5 — The small-parameter approximations",
      body: `<p>BPhO prints these on its own constant sheet. That is a strong signal: they are <b>expected tools</b>, not optional tricks. If a question contains something like <code>(1 + x)²</code> where <code>x</code> is small, you are meant to expand it.</p>
<table><thead><tr><th>Approximation</th><th>Valid when</th><th>Where it comes from</th></tr></thead><tbody>
<tr><td><code>(1 + x)ⁿ ≈ 1 + nx</code></td><td>x much less than 1</td><td>Binomial expansion, first two terms</td></tr>
<tr><td><code>1/(1 + x)ⁿ ≈ 1 − nx</code></td><td>x much less than 1</td><td>The same, with n negative</td></tr>
<tr><td><code>eˣ ≈ 1 + x</code></td><td>x much less than 1</td><td>Taylor series of the exponential</td></tr>
<tr><td><code>tan θ ≈ sin θ ≈ θ</code></td><td>θ small, <b>in radians</b></td><td>Taylor series of the trig functions</td></tr>
<tr><td><code>cos θ ≈ 1 − θ²/2</code></td><td>θ small, in radians</td><td>Taylor series; note the second-order term is needed</td></tr>
<tr><td><code>√(a² + d²) − a ≈ d²/2a</code></td><td>d much less than a</td><td>The binomial approximation in geometric dress</td></tr>
</tbody></table>
<h3>Deriving the geometric one, so you never have to memorise it</h3>
<p>Factor out the large quantity:</p>
<div class="formula">√(a² + d²) = a √(1 + d²/a²) = a (1 + d²/a²)<sup>1/2</sup></div>
<p>Apply <code>(1 + x)ⁿ ≈ 1 + nx</code> with <code>x = d²/a²</code> and <code>n = ½</code>:</p>
<div class="formula">≈ a (1 + ½ · d²/a²) = a + d²/(2a)</div>
<p>Subtract the <code>a</code> and you have it: <code>√(a² + d²) − a ≈ d²/(2a)</code>.</p>
<div class="callout callout--key"><p><b>When you will actually use it.</b> Any time a point is displaced a small distance <code>d</code> from a symmetric position and you need the change in a distance that was originally <code>a</code>. The classic case is a mass hanging from a string, pulled slightly sideways — the string length hardly changes, but the <i>difference</i> between the new distance and the old is second order in <code>d</code>, and that is the whole content of the question. Sample question S9 is exactly this shape.</p></div>
<div class="callout callout--warn"><p><b>Radians, not degrees.</b> <code>tan θ ≈ θ</code> fails completely if <code>θ</code> is in degrees. Twenty degrees is 0.35 rad, and <code>tan 20° = 0.364</code> while <code>20</code> is nonsense. When you use these, convert first or work in radians throughout.</p></div>`
    },

    {
      h: "Step 6 — Order-of-magnitude estimation",
      body: `<p>Some questions have options that differ by powers of ten. Then you do not need an accurate answer — you need to know whether the quantity is nearer 10³ or 10⁶. Get within a factor of three and you can pick.</p>
<h3>The technique</h3>
<ol class="tight">
<li>Break the unknown into a product of things you can estimate.</li>
<li>Round each factor aggressively to a power of ten, or to something you can multiply in your head.</li>
<li>Multiply the powers of ten separately from the leading digits.</li>
<li>Check the units at the end to be sure you have not built the wrong quantity.</li>
</ol>
<h3>Worked estimate: mass of the Earth's atmosphere</h3>
<p>Atmospheric pressure is about <code>10⁵ Pa</code>, which is a force per unit area of <code>10⁵ N m⁻²</code>. The atmosphere's weight is the pressure times the Earth's surface area.</p>
<div class="formula">surface area = 4πr² ≈ 4 × 3 × (6.4 × 10⁶)² ≈ 5 × 10¹⁴ m²
weight ≈ 10⁵ × 5 × 10¹⁴ = 5 × 10¹⁹ N
mass = weight / g ≈ 5 × 10¹⁹ / 10 = 5 × 10¹⁸ kg</div>
<p>So the answer is of order <code>10¹⁸ kg</code>. The published value is about <code>5.1 × 10¹⁸ kg</code>, so this estimate is good to better than 2%. That took about forty seconds and no calculator.</p>
<h3>Useful anchors to keep in your head</h3>
<table><thead><tr><th>Quantity</th><th>Order of magnitude</th></tr></thead><tbody>
<tr><td>Radius of the Earth</td><td>6.4 × 10⁶ m</td></tr>
<tr><td>Earth–Sun distance</td><td>1.5 × 10¹¹ m</td></tr>
<tr><td>Mass of the Earth</td><td>6 × 10²⁴ kg</td></tr>
<tr><td>Mass of the atmosphere</td><td>5 × 10¹⁸ kg</td></tr>
<tr><td>Atmospheric pressure</td><td>10⁵ Pa</td></tr>
<tr><td>Speed of sound in air</td><td>340 m s⁻¹</td></tr>
<tr><td>Density of water</td><td>10³ kg m⁻³</td></tr>
<tr><td>Density of air</td><td>about 1.2 kg m⁻³</td></tr>
<tr><td>Length of a day</td><td>86 400 s ≈ 10⁵ s</td></tr>
<tr><td>Power of a human at rest</td><td>about 100 W</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>A cold anchor worth adding.</b> Seconds in a year: 365 × 24 × 3600 ≈ 3.15 × 10⁷, so just remember 10⁷. Since a day is ≈ 10⁵ s, any long-time estimate checks itself: a decade is 10⁸ s, a human lifetime about 10⁹ s. On an estimation question these let you kill options that are off by a factor of a thousand without doing any physics — the difference between 10⁷ and 10¹⁰ is usually a clean eliminator.</p></div>`
    },

    {
      h: "Step 7 — Graph-shape reasoning",
      body: `<p>Questions of the form "which graph best shows how X varies with Y" appear on the sample paper (S8) and are among the quickest marks on the paper, provided you reason about shape rather than plotting points.</p>
<h3>Four things to ask, in order</h3>
<ol class="steps">
<li><b>What happens at zero?</b> Does the curve pass through the origin, or does it start somewhere else? A non-zero intercept usually means a physical offset — a work function, a background count rate, an internal resistance.</li>
<li><b>What happens as it gets large?</b> Does it grow without limit, approach a plateau, or fall away? Terminal speed is the plateau case; inverse-square laws are the falling case.</li>
<li><b>Is there an asymptote?</b> A curve that approaches a line without reaching it has a very distinctive look — flattening towards horizontal, or bending towards vertical.</li>
<li><b>Straight or curved?</b> If straight, does it pass through the origin? Proportional means straight <i>and</i> through the origin; linear only means straight.</li>
</ol>
<h3>Two shapes worth recognising on sight</h3>
<table><thead><tr><th>Relationship</th><th>Shape</th><th>Typical appearance</th></tr></thead><tbody>
<tr><td><code>y ∝ 1/x</code></td><td>rectangular hyperbola</td><td>Falls steeply at small x, flattens towards the axis</td></tr>
<tr><td><code>y ∝ 1/x²</code></td><td>steeper hyperbola</td><td>Falls even faster, hugs the axis sooner</td></tr>
<tr><td><code>y = kx²</code></td><td>parabola through origin</td><td>Flat at first, then rises rapidly</td></tr>
<tr><td><code>y = a(1 − e<sup>−kx</sup>)</code></td><td>saturating growth</td><td>Rises through origin, flattens to a plateau at <code>a</code></td></tr>
<tr><td><code>y = kx + c</code></td><td>straight line, non-zero intercept</td><td>Straight but does not pass through the origin</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The fastest discriminator.</b> Find the value at <code>x = 0</code> and the behaviour as <code>x → ∞</code>. Between them, those two facts kill at least two options on almost every graph question.</p></div>`
    },

    {
      h: "Step 8 — Limiting cases",
      body: `<p>Substitute an extreme value into each option and see which ones die. This is the most reliable elimination tool on a multiple-choice paper, and it needs no calculation at all.</p>
<h3>The standard substitutions</h3>
<table><thead><tr><th>Substitution</th><th>What it tests</th></tr></thead><tbody>
<tr><td><code>m → 0</code></td><td>Does the answer still make sense if the mass vanishes? Many wrong options give a non-zero result where zero is required.</td></tr>
<tr><td><code>θ → 0</code></td><td>Does it reduce to the obvious small-angle answer?</td></tr>
<tr><td><code>n → 1</code></td><td>In optics, this removes a boundary entirely, so nothing should happen.</td></tr>
<tr><td><code>d → 0</code></td><td>If the separation vanishes, the quantity should vanish too — unless it is supposed to diverge.</td></tr>
<tr><td><code>r → ∞</code></td><td>Tests the large-distance behaviour: fields and intensities should fall to zero.</td></tr>
</tbody></table>
<h3>Worked elimination: the range of a projectile</h3>
<p>Four options are offered for the horizontal range of a projectile launched at speed <code>u</code> and angle <code>θ</code> on level ground. Which can you eliminate without doing the derivation?</p>
<div class="formula">A) u sin 2θ / g    B) u² sin 2θ / g    C) u² sin θ / g    D) u² sin 2θ / g²</div>
<ul class="tight">
<li><b>Check the dimensions of each.</b> <code>u²/g</code> is (m² s⁻²)/(m s⁻²) = m ✓. Option A has <code>u/g</code> = s, which is a time, not a distance — eliminate.</li>
<li><b>Option D</b> has <code>u²/g²</code> = m² s⁻² / m² s⁻⁴ = s², a time squared — eliminate.</li>
<li><b>Check the small-angle limit.</b> At <code>θ = 0</code> the projectile goes nowhere, so the range must be zero. Options B and C both give zero ✓.</li>
<li><b>Check the maximum.</b> The range should be largest at <code>θ = 45°</code>. Option C, <code>sin θ</code>, peaks at <code>θ = 90°</code>, which is a vertical shot with zero range — eliminate.</li>
</ul>
<p>Option B survives all four checks in about thirty seconds. Notice that the actual derivation — eliminating time between the vertical and horizontal equations — never happened.</p>`
    },

    {
      h: "Step 9 — Elimination and guessing",
      body: `<p>Round 0 has <b>no negative marking</b>. A blank scores zero with certainty; a guess with two options eliminated scores 0.5 on average. Leaving anything blank is a strictly worse strategy, and it is the single most common way people fall short of the qualifying line.</p>
<h3>An elimination order that works under time pressure</h3>
<ol class="steps">
<li><b>Units.</b> Ten seconds. Reduce each option to base units and kill any that is the wrong kind of quantity. Options that differ by a factor of <code>g</code>, or that are a time where a length is required, fall immediately.</li>
<li><b>Powers of ten.</b> Fifteen seconds. If the options differ by orders of magnitude, estimate and pick the nearest.</li>
<li><b>Limiting cases.</b> Twenty seconds. Substitute zero or infinity and see what breaks.</li>
<li><b>Sign and direction.</b> Five seconds. Is a negative answer physically possible here? Options often include the sign-flipped version of the right answer.</li>
<li><b>Then</b> — and only then — do the physics.</li>
</ol>
<div class="callout callout--good"><p><b>Budget rule.</b> If you have spent more than three minutes on a question, mark your best guess and move on. Two easy questions later in the paper are worth more than the one you are stuck on. Come back only if time remains.</p></div>
<div class="callout callout--bad"><p><b>The arithmetic trap.</b> Do not start long multiplication. Every question on this paper has been designed so that either the numbers cancel or an estimate suffices. If you are doing long division, you have taken a wrong turn — stop and look for the ratio.</p></div>`
    },

    {
      h: "The numbers to know cold",
      body: `<p>The formula booklet is permitted, but at 2.4 minutes a question there is no time to look things up. These are the ones that appear often enough to be worth memorising.</p>
<table><thead><tr><th>Constant</th><th>Value</th><th>How to remember it</th></tr></thead><tbody>
<tr><td><code>g</code></td><td>9.81 N kg⁻¹</td><td>Use 10 for estimation; 9.81 only when a question is precise</td></tr>
<tr><td><code>c</code></td><td>3.00 × 10⁸ m s⁻¹</td><td>Light travels 30 cm in a nanosecond</td></tr>
<tr><td><code>e</code></td><td>1.60 × 10⁻¹⁹ C</td><td>Same digits as the eV conversion — one fact, two uses</td></tr>
<tr><td><code>h</code></td><td>6.63 × 10⁻³⁴ J s</td><td>Note <code>hc ≈ 2 × 10⁻²⁵ J m</code>, very useful for photon energy in wavelength form</td></tr>
<tr><td>1 eV</td><td>1.60 × 10⁻¹⁹ J</td><td>Identical to <code>e</code>; that is the definition</td></tr>
<tr><td>Radius of the Earth</td><td>≈ 6.4 × 10⁶ m</td><td>Roughly 6400 km</td></tr>
<tr><td>Earth–Sun distance</td><td>≈ 1.5 × 10¹¹ m</td><td>Roughly 8 light-minutes</td></tr>
<tr><td>Length of a day</td><td>86 400 s</td><td>Roughly 10⁵ s — use the approximation</td></tr>
<tr><td>Density of water</td><td>1000 kg m⁻³</td><td>1 g cm⁻³, the same fact</td></tr>
<tr><td>Atmospheric pressure</td><td>≈ 1.0 × 10⁵ Pa</td><td>About 10⁵, so a 1 cm² patch carries about 10 N</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The one combination worth memorising separately:</b> <code>hc ≈ 2.0 × 10⁻²⁵ J m</code>. Then photon energy in joules is <code>hc/λ</code>, and for a 500 nm photon that is <code>2 × 10⁻²⁵ / 5 × 10⁻⁷ = 4 × 10⁻¹⁹ J</code>, which is about 2.5 eV. That whole calculation is a mental one.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A simple pendulum has a bob of mass <code>m</code> on a string of length <code>ℓ</code>. Its period is believed to depend on <code>m</code>, <code>ℓ</code> and <code>g</code>. Use dimensional analysis to determine which of these is the correct form.</p><p>A) <code>T = k√(ℓ/g)</code> &nbsp; B) <code>T = k√(ℓg)</code> &nbsp; C) <code>T = kℓ/g</code> &nbsp; D) <code>T = kmℓ/g</code> &nbsp; E) <code>T = k√(mℓ/g)</code></p>",
      sol: `<p>Write the dimensions of each quantity: <code>T</code> is a time, L⁰M⁰T¹. The length <code>ℓ</code> is L. The mass <code>m</code> is M. The field strength <code>g</code> is an acceleration, L T⁻².</p>
<p>Assume <code>T = k ℓ<sup>a</sup> m<sup>b</sup> g<sup>c</sup></code> and match exponents:</p>
<div class="formula">L: a + c = 0
M: b = 0
T: −2c = 1  →  c = −½,  hence a = ½</div>
<p>So <code>T = k ℓ<sup>1/2</sup> g<sup>−1/2</sup> = k√(ℓ/g)</code>. Mass does not appear at all, which is correct physics — a pendulum's period is independent of the mass of the bob.</p>
<p><b>Answer: A.</b></p>
<p>Notice how quickly the others die on the same check. B has <code>ℓg</code> = L² T⁻², whose square root is L T⁻¹, a speed. C is L/(L T⁻²) = T², a time squared. D carries an extra M. E carries an M under a square root. Only A is a time.</p>`,
      tag: "Dimensional analysis — the sample-paper shape"
    },
    {
      q: "<p>A capacitor of capacitance <code>C</code> is charged to a potential difference <code>V</code>. Which of the following expressions could <b>not</b> represent the energy stored?</p><p>A) <code>½CV²</code> &nbsp; B) <code>½QV</code> &nbsp; C) <code>Q²/2C</code> &nbsp; D) <code>CV</code> &nbsp; E) <code>QV/2</code></p>",
      sol: `<p>Energy is a joule, which in base units is kg m² s⁻². Check each option.</p>
<p>First get the dimensions of <code>C</code> and <code>V</code> from Step 1: <code>C</code> is A² s⁴ kg⁻¹ m⁻² and <code>V</code> is kg m² s⁻³ A⁻¹.</p>
<ul class="tight">
<li><code>CV²</code>: (A² s⁴ kg⁻¹ m⁻²)(kg² m⁴ s⁻⁶ A⁻²) = kg m² s⁻² ✓</li>
<li><code>QV</code>: <code>Q = CV</code>, so this is the same as <code>CV²</code> ✓</li>
<li><code>Q²/C</code>: (A² s²)²/(A² s⁴ kg⁻¹ m⁻²) = A⁴ s⁴ · kg m² / (A² s⁴) = A² kg m², which still carries A² — <b>but</b> <code>Q²/C = C²V²/C = CV²</code>, so it is dimensionally fine ✓</li>
<li><code>CV</code>: kg m² s⁻³ A⁻¹ × A² s⁴ kg⁻¹ m⁻² = A s = coulombs. That is a <b>charge</b>, not an energy ✗</li>
</ul>
<p><b>Answer: D.</b> <code>CV</code> is the charge stored, <code>Q</code>. It is the single most common distractor on capacitor questions, because it looks structurally similar to the energy expressions and is a genuine physical quantity — just the wrong one.</p>
<p><b>The quick route:</b> recognise that options A, B and E are all the same thing up to a factor of 2, so if one is right they all are. Since the question asks for the one that is <i>not</i> energy, and a multiple-choice question cannot have three correct answers, the odd one out must be D or C. Then check which is a charge.</p>`,
      tag: "Dimensional consistency + reading the options"
    },
    {
      q: "<p>A car of mass <code>m</code> brakes from speed <code>v</code> to rest in distance <code>d</code>. The same car, loaded to twice the mass but with the same braking force, brakes from speed <code>2v</code>. What is the new stopping distance?</p><p>A) <code>d</code> &nbsp; B) <code>2d</code> &nbsp; C) <code>4d</code> &nbsp; D) <code>8d</code> &nbsp; E) <code>16d</code></p>",
      sol: `<p>Set the work done by the braking force equal to the kinetic energy removed:</p>
<div class="formula">Fd = ½mv²  →  d = mv²/(2F)</div>
<p>Take the ratio of the new situation to the old. The force <code>F</code> is unchanged, and the factor ½ cancels:</p>
<div class="formula">d₂/d₁ = (m₂/m₁) × (v₂/v₁)² = 2 × 2² = 8</div>
<p><b>Answer: D, 8d.</b></p>
<p>The mass contributes linearly because kinetic energy is proportional to mass. The speed contributes quadratically because kinetic energy goes as <code>v²</code>. Multiplying the two factors gives 8.</p>
<p><b>How to get this wrong.</b> The tempting error is to treat both changes as linear and answer <code>4d</code> — that is option C, which is there for exactly that reason. The second trap is to notice the <code>v²</code> and answer <code>4d</code> from the speed alone, forgetting the mass. Do not compute anything: this is a ratio question and the ratio takes fifteen seconds.</p>`,
      tag: "Ratio reasoning — no calculator needed"
    },
    {
      q: "<p>Two points on a horizontal line are separated by a distance <code>2a</code>. A mass hangs from the midpoint on a string of total length <code>2a</code>, so that each half of the string has length <code>a</code> and the mass sits directly between the two points. The mass is now displaced horizontally by a small distance <code>d</code>. By how much does the length of the string change?</p><p>A) <code>d</code> &nbsp; B) <code>d²/a</code> &nbsp; C) <code>d²/2a</code> &nbsp; D) <code>d²/4a</code> &nbsp; E) <code>d²/a²</code></p>",
      sol: `<p>Consider one half of the string. Before the displacement it has length <code>a</code> and is horizontal. After a horizontal displacement <code>d</code> of the lower end, that half forms the hypotenuse of a right triangle with legs <code>a</code> and <code>d</code>.</p>
<p>So the new length of that half is <code>√(a² + d²)</code>. Apply the approximation:</p>
<div class="formula">√(a² + d²) = a(1 + d²/a²)<sup>1/2</sup> ≈ a(1 + d²/2a²) = a + d²/(2a)</div>
<p>So each half stretches by <code>d²/(2a)</code>. There are two halves, so the total string length increases by <code>2 × d²/(2a) = d²/a</code>.</p>
<p><b>Answer: B, <code>d²/a</code>.</b></p>
<p><b>The trap.</b> Option C is the change in <i>one half</i>, and it is the number most people arrive at first because they only look at the triangle they drew. The question asks about the whole string, which has two halves. Read what is being asked — this distinction is a favourite of the sample paper's style.</p>
<p><b>The deeper point.</b> The length change is second order in <code>d</code>, not first order. That is why a hanging mass on a taut string barely moves vertically when you push it sideways: the string has almost no slack to give. This fact is the whole basis of the small-oscillation analysis of a pendulum, and it is why the restoring force is proportional to displacement rather than constant.</p>`,
      tag: "The geometric approximation — sample question S9's shape"
    },
    {
      q: "<p>Estimate the number of air molecules in a room measuring 5 m × 4 m × 3 m. Use the fact that one mole of any gas occupies about 24 litres at room temperature and pressure, and that Avogadro's number is about <code>6 × 10²³</code>.</p><p>A) 10²⁵ &nbsp; B) 10²⁶ &nbsp; C) 10²⁷ &nbsp; D) 10²⁸ &nbsp; E) 10²⁹</p>",
      sol: `<p><b>Step 1 — volume of the room.</b></p>
<div class="formula">5 × 4 × 3 = 60 m³</div>
<p>One litre is <code>10⁻³ m³</code>, so the room holds <code>6 × 10⁴</code> litres.</p>
<p><b>Step 2 — number of moles.</b> Divide by the molar volume:</p>
<div class="formula">6 × 10⁴ / 24 = 2500 = 2.5 × 10³ mol</div>
<p><b>Step 3 — number of molecules.</b> Multiply by Avogadro's number:</p>
<div class="formula">2.5 × 10³ × 6 × 10²³ = 15 × 10²⁶ = 1.5 × 10²⁷</div>
<p><b>Answer: C, 10²⁷.</b></p>
<p><b>The technique being tested.</b> You do not need to know Avogadro's number precisely, only that it is of order 10²³. The arithmetic is <code>2.5 × 6 = 15</code> and <code>10³ × 10²³ = 10²⁶</code>, both mental. Then the leading factor of 1.5 places the answer at <code>1.5 × 10²⁷</code>, comfortably nearest option C.</p>
<p><b>Why the distractors are all powers of ten.</b> This is the signature of an estimation question: the options differ by a factor of ten, so you are not being asked for a precise value, only for the right order of magnitude. An estimate good to a factor of three is always enough. If you had been asked to distinguish 10²⁷ from 10²⁸ you would need a much better estimate, and the question would have to give you more information.</p>
<p><b>The error to avoid.</b> The commonest slip is to lose track of the litres-to-cubic-metres conversion and work with 60 litres rather than 60 000. That gives an answer four orders of magnitude too small, which lands you on option A. Convert units first, in writing, before doing any arithmetic.</p>`,
      tag: "Order-of-magnitude estimation"
    },
    {
      q: "<p>A ball is thrown at speed <code>u</code> at an angle <code>θ</code> to the horizontal on level ground. Which of these could be the correct expression for the maximum height reached?</p><p>A) <code>u² sin²θ / 2g</code> &nbsp; B) <code>u² sin 2θ / g</code> &nbsp; C) <code>u sin θ / g</code> &nbsp; D) <code>u² cos²θ / 2g</code> &nbsp; E) <code>u² tan θ / 2g</code></p>",
      sol: `<p>Do not derive it. Eliminate.</p>
<ul class="tight">
<li><b>Dimensions.</b> A height must be a length, so each option must reduce to m. <code>u²/g</code> = (m s⁻¹)²/(m s⁻²) = m ✓. Option C is <code>u/g</code> = s, a time — eliminate.</li>
<li><b>Vertical limit.</b> At <code>θ = 90°</code> the ball goes straight up and should reach its greatest height, <code>u²/2g</code>. Option D has <code>cos²θ</code>, which is <b>zero</b> at 90°, giving zero height for a vertical throw — eliminate. Option B has <code>sin 2θ</code>, which is also zero at 90° — eliminate.</li>
<li><b>Horizontal limit.</b> At <code>θ = 0</code> the ball is thrown horizontally from ground level and never rises, so the height must be zero. Option E has <code>tan θ</code>, which is zero at 0° ✓ but diverges at 90° — eliminate.</li>
<li><b>Option A</b> gives <code>u²/2g</code> at 90° ✓ and zero at 0° ✓. It survives.</li>
</ul>
<p><b>Answer: A.</b></p>
<p>Confirm with the derivation: at the top, the vertical velocity is zero, so <code>0 = (u sin θ)² − 2gh</code>, giving <code>h = u² sin²θ / 2g</code> ✓.</p>
<p><b>The lesson.</b> Four of the five options were killed by two facts — what happens at <code>θ = 0</code> and what happens at <code>θ = 90°</code>. That is about forty seconds of work, and it did not require knowing that the vertical component is <code>u sin θ</code>. On a multiple-choice paper, being able to eliminate is worth more than being able to derive.</p>`,
      tag: "Limiting cases — the fastest elimination tool"
    },

    {
      q: "<p>The speed <code>v</code> of a transverse wave on a string is known to depend only on the tension <code>T</code> in the string and the mass per unit length <code>μ</code>. By dimensional analysis, which is the correct form?</p><p>A) <code>k√(T/μ)</code> &nbsp; B) <code>k√(μ/T)</code> &nbsp; C) <code>k T/μ</code> &nbsp; D) <code>k√(Tμ)</code> &nbsp; E) <code>k(T/μ)²</code></p>",
      sol: `<p>Write the dimensions. Tension is a force, so <code>T</code> = M L T⁻². Mass per unit length <code>μ</code> is M L⁻¹. The speed <code>v</code> we are after has dimensions L T⁻¹.</p>
<p>Now check the dimensions of each option.</p>
<ul class="tight">
<li><b>A</b> <code>T/μ</code> = (M L T⁻²)/(M L⁻¹) = L² T⁻², so <code>√(T/μ)</code> = L T⁻¹ — a speed ✓</li>
<li><b>B</b> <code>μ/T</code> = (M L⁻¹)/(M L T⁻²) = L⁻² T², so <code>√(μ/T)</code> = L⁻¹ T — not a speed ✗</li>
<li><b>C</b> <code>T/μ</code> = L² T⁻², which is a speed <i>squared</i>, not a speed ✗</li>
<li><b>D</b> <code>Tμ</code> = (M L T⁻²)(M L⁻¹) = M² T⁻², so <code>√(Tμ)</code> = M T⁻¹ — still carries a mass dimension ✗</li>
<li><b>E</b> <code>(T/μ)²</code> = (L² T⁻²)² = L⁴ T⁻⁴ — neither a speed nor its square ✗</li>
</ul>
<p><b>Answer: A.</b> Dimensional analysis gives <code>v = k√(T/μ)</code>, and the physics fixes <code>k = 1</code>, so the standard result <code>v = √(T/μ)</code> falls straight out of the units alone.</p>
<p><b>Why the others are there.</b> B is the slip you make if you write <code>μ</code> over <code>T</code> instead of <code>T</code> over <code>μ</code>. C is the dimensional form of <code>v²</code> — the trap for anyone who forgets to take the square root. D keeps the square root but multiplies the two quantities instead of dividing, leaving a spurious M. E double-squares and is the distant distractor. The fast kill: D and E both fail the mass check, and a wave speed must not depend on how you choose to measure mass — so they die first.</p>`,
      tag: "Dimensional analysis — a less obvious quantity"
    },

    {
      q: "<p>A ball is dropped from rest and falls through air whose resistance is not negligible and increases with the speed. Which graph best shows the ball's speed <code>v</code> against time <code>t</code>?</p><p>A) a straight line through the origin<br>B) a parabola through the origin that curves upward<br>C) a curve through the origin that rises then flattens to a horizontal plateau<br>D) a horizontal line at a fixed non-zero speed<br>E) a curve that rises steeply and then falls back towards zero</p>",
      sol: `<p>Reason about the two ends of the graph — the value at <code>t = 0</code> and the behaviour as <code>t → ∞</code>. Those two facts kill four of the five options without any derivation.</p>
<ul class="tight">
<li><b>At t = 0</b> the ball is released from rest, so <code>v = 0</code>. The graph must pass through the origin. Option D is a horizontal line at a non-zero speed, so it never reaches the origin — eliminate.</li>
<li><b>As t → ∞</b> air resistance grows until it balances the weight, the resultant force becomes zero, and the ball stops accelerating, settling at a constant terminal speed. So the curve must approach a horizontal plateau. Option A (straight line) keeps rising without limit — true only with no drag — eliminate. Option B (parabola, <code>v ∝ t²</code>) rises even faster and also has no plateau; it is in fact the shape of <i>displacement</i> under constant acceleration, not speed — eliminate. Option E falls back towards zero, which would mean the ball slows to a stop, but nothing pushes it upward, so that is unphysical — eliminate.</li>
<li><b>Option C</b> starts at the origin and flattens to a horizontal plateau: exactly the terminal-speed shape.</li>
</ul>
<p><b>Answer: C.</b></p>
<p><b>The traps.</b> A is the no-resistance answer (<code>v = gt</code>), the most common mistake because students reach for <code>v = u + at</code> by reflex. B confuses speed with distance fallen (<code>s = ½gt²</code>). D forgets the ball starts from rest. E imagines a restoring force that does not exist. The real derivation — solving <code>mg − kv = m dv/dt</code> — was never needed; the two endpoints did all the work, which is the whole point of Step 7.</p>`,
      tag: "Graph-shape elimination — terminal speed"
    }
  ],

  traps: [
    "Assuming dimensional analysis can give you the numerical constant. It gives the form only. <code>T = k√(ℓ/g)</code> and the method cannot tell you <code>k = 2π</code>.",
    "Using degrees in the small-angle approximations. <code>tan θ ≈ θ</code> requires radians; in degrees it is simply false.",
    "Forgetting that angles are dimensionless. This is legitimate and it is why <code>sin θ</code> and <code>θ</code> can be equated in the small-angle limit.",
    "Computing in a ratio question. If the question says 'how many times', the constants cancel — reaching for numbers means you have misread it.",
    "Answering the intermediate quantity instead of the asked one. The <code>d²/2a</code> versus <code>d²/a</code> trap in the string example is the archetype: check whether the question wants one part or the whole.",
    "Leaving a blank. There is no negative marking; a blank is a guaranteed zero.",
    "Spending more than three minutes on one question. The paper is designed so that some questions are meant to be skipped and returned to.",
    "Treating <code>cos θ ≈ 1</code> as sufficient when the second-order term matters. Use <code>cos θ ≈ 1 − θ²/2</code> whenever the <i>change</i> in a quantity is what the question is about."
  ],

  checklist: [
    { id: "A1", flag: "CORE", text: "SI base units: kg, m, s, A, K, mol — know which quantities they measure and which are derived." },
    { id: "A2", flag: "NEW", text: "Reduce any derived unit to base units — N, J, W, Pa, C, V, Ω, F, T. Do all nine from memory in under three minutes." },
    { id: "A3", flag: "CORE", text: "SI prefixes T, G, M, k, c, m, μ, n, p, f, and converting to and from standard form." },
    { id: "A4", flag: "CORE", text: "Unit conversions: joules to eV and back; joules to kilowatt-hours." },
    { id: "A5", flag: "NEW", text: "Dimensional analysis: derive the form of a relationship by equating base units. Be able to do the pendulum and the stretched-string derivations on blank paper." },
    { id: "A6", flag: "NEW", text: "Dimensional consistency checking: test whether a given equation can possibly be correct, including the additive-terms rule." },
    { id: "A7", flag: "CORE", text: "Ratio reasoning: set up a ratio so shared constants cancel. Do not compute." },
    { id: "A8", flag: "CORE", text: "The small-parameter approximations, all six, including deriving <code>√(a² + d²) − a ≈ d²/2a</code> from the binomial expansion." },
    { id: "A9", flag: "CORE", text: "Order-of-magnitude estimation and Fermi problems. Track powers of ten separately from leading digits." },
    { id: "A10", flag: "CORE", text: "Graph-shape reasoning: value at zero, behaviour at infinity, asymptotes, and whether a straight line passes through the origin." },
    { id: "A11", flag: "CORE", text: "Limiting-case checking: substitute m → 0, θ → 0, n → 1 and eliminate options." },
    { id: "A12", flag: "CORE", text: "Elimination order under time pressure: units, then powers of ten, then limits, then sign. Never leave a blank." },
    { id: "A13", flag: "CORE", text: "Mental arithmetic on the standard constants: g, c, e, h, hc, Earth radius, length of a day, density of water." },
    { id: "A14", flag: "R1-ONLY", text: "Uncertainties: absolute, fractional and percentage; combining uncertainties; error bars; uncertainty in a gradient. Round 1 material — insurance only." }
  ]
}

]);
