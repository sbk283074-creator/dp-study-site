/* BPhO Round 0 — curriculum, part 6 of 6 (first half).
   Modules F (waves) and G (optics). */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "F",
  title: "Waves",
  short: "Waves",
  priority: 3,
  tier: "Tier A — inside AQA AS §3.3, and one sample-paper question",
  why: "A pattern topic. Once you can recognise which of four or five shapes a question is, the algebra is short and the marks are reliable. The one genuine trap is the difference between the maximum speed of a particle in the medium and the speed of the wave itself, which appears constantly and which options are designed to confuse.",
  warn: null,

  sections: [
    {
      h: "The vocabulary, precisely",
      body: `<p>Waves questions are lost more often to loose vocabulary than to hard physics. Fix these definitions first.</p>
<table><thead><tr><th>Quantity</th><th>Meaning</th><th>Note</th></tr></thead><tbody>
<tr><td>Displacement</td><td>distance of a particle from its equilibrium position</td><td>can be positive or negative</td></tr>
<tr><td>Amplitude <code>A</code></td><td>maximum displacement from equilibrium</td><td>not the peak-to-peak distance, which is <code>2A</code></td></tr>
<tr><td>Wavelength <code>λ</code></td><td>distance between consecutive points in phase</td><td>crest to crest, or any equivalent pair</td></tr>
<tr><td>Period <code>T</code></td><td>time for one complete oscillation</td><td><code>T = 1/f</code></td></tr>
<tr><td>Frequency <code>f</code></td><td>number of oscillations per second</td><td>in hertz; unchanged when a wave crosses a boundary</td></tr>
<tr><td>Speed <code>v</code></td><td>speed at which the wave pattern advances</td><td><code>v = fλ</code></td></tr>
<tr><td>Phase</td><td>the stage of the cycle a particle is at</td><td>measured in radians, degrees or fractions of a cycle</td></tr>
</tbody></table>
<div class="formula">v = fλ        f = 1/T</div>
<h3>Phase difference</h3>
<p>Two points separated by a distance <code>Δx</code> along the wave have a phase difference</p>
<div class="formula">Δφ = 2π Δx/λ</div>
<p>So a separation of half a wavelength corresponds to <code>π</code> radians, or 180°, or half a cycle. A separation of a whole wavelength corresponds to <code>2π</code> radians, or 360°, which is the same as being in phase. Being able to move between radians, degrees and fractions of a cycle is worth drilling, because questions use all three.</p>
<div class="callout callout--key"><p><b>The frequency fact worth stating explicitly.</b> When a wave crosses a boundary into a different medium, its <b>speed and wavelength change but its frequency does not</b>. The frequency is set by the source. So <code>v = fλ</code> at the boundary gives <code>v₁/λ₁ = v₂/λ₂</code>. This is the basis of refraction and it is worth knowing as a sentence.</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> The most common slip is to treat <code>f</code> and <code>v</code> as interchangeable: they are not. Frequency is set by the source (how often it shakes); speed is set by the medium (how fast the disturbance travels). When a wave crosses from one medium to another its speed and wavelength change, but its frequency — and therefore its period — is untouched. If you ever produce a calculation where the frequency changed at a boundary, you have made an error.</p></div>
<p>中文对照: 位移 displacement, 振幅 amplitude, 波长 wavelength, 频率 frequency, 周期 period, 相位 phase, 波速 wave speed. 记住 <code>v = fλ</code>：波速 = 频率 × 波长。</p>`
    },

    {
      h: "Transverse, longitudinal, and polarisation",
      body: `<h3>The distinction</h3>
<ul class="tight">
<li><b>Transverse:</b> the oscillations are perpendicular to the direction of energy transfer. Examples: light, waves on a string, seismic S-waves.</li>
<li><b>Longitudinal:</b> the oscillations are parallel to the direction of energy transfer, producing compressions and rarefactions. Examples: sound, seismic P-waves, ultrasound.</li>
</ul>
<h3>Polarisation, and why it matters</h3>
<p>Polarisation restricts the oscillations to a single plane. It is possible only for transverse waves, because a longitudinal wave's oscillations are already along the direction of travel — there is no perpendicular plane to restrict.</p>
<p>So <b>the fact that light can be polarised is evidence that light is a transverse wave.</b> That is the sentence most questions on this topic want.</p>
<div class="callout callout--key"><p><b>The reverse argument, which is also testable.</b> Sound cannot be polarised. So if an experiment appears to polarise sound, the conclusion is that the "sound" is not a longitudinal wave, or that the experiment is measuring something else. Reasoning in the negative direction is a common competition move.</p></div>
<h3>The electromagnetic spectrum</h3>
<p>All electromagnetic waves travel at the same speed in a vacuum, <code>c = 3.00 × 10⁸ m s⁻¹</code>, and they differ only in frequency and wavelength. From longest wavelength to shortest:</p>
<p>radio, microwave, infrared, visible, ultraviolet, X-ray, gamma.</p>
<p>Visible light spans roughly 400 nm (violet) to 700 nm (red). Remembering that visible wavelengths are of order <code>10⁻⁷ m</code> is useful for the photon-energy estimates in module L.</p>
<div class="callout callout--key"><p><b>A quick test for any wave.</b> Ask: are the oscillations across the direction of travel (transverse) or along it (longitudinal)? Compressions and rarefactions mean longitudinal (sound); crests and troughs mean transverse (string, light). This single classification tells you immediately whether polarisation can occur at all.</p></div>
<p>中文对照: 横波 transverse wave, 纵波 longitudinal wave, 偏振 polarisation, 压缩 compression, 稀疏 rarefaction. 横波可以偏振，纵波不能。</p>`
    },

    {
      h: "Reflection, refraction and transmission at a boundary",
      body: `<p>When a wave meets a boundary between two media, three things can happen at once: part is <b>reflected</b> back into the first medium, part is <b>transmitted</b> (and usually <b>refracted</b>) into the second, and part may be absorbed. Which dominates depends on how abruptly the wave speed changes at the boundary.</p>
<div class="formula">reflection: angle of incidence = angle of reflection
refraction (mechanical): sin θ₁ / sin θ₂ = v₁ / v₂</div>
<p>The refraction rule for a mechanical wave is the wave-speed analogue of Snell's law: the ray bends towards the normal when it enters the slower medium, because <code>v₂ &lt; v₁</code> makes <code>sin θ₂ &lt; sin θ₁</code>. (For light this becomes <code>n₁ sin θ₁ = n₂ sin θ₂</code>; the optics module covers the light version — the physics is identical, only the labels differ.)</p>
<h3>Fixed end versus free end</h3>
<p>For a wave on a string the reflection depends on what the end is doing:</p>
<ul class="tight">
<li><b>Fixed end</b> (the string tied down): the end cannot move, so the reflected pulse comes back <b>inverted</b> — a crest reflects as a trough. This is a phase change of <code>π</code> (half a cycle).</li>
<li><b>Free end</b> (the string attached to a frictionless ring on a vertical pole): the end moves freely, so the reflected pulse comes back <b>upright</b> — no phase change.</li>
</ul>
<p>This is exactly why a string fixed at both ends has nodes at the ends: the fixed end is a reflection site with a <code>π</code> phase flip, which is what forces the displacement to zero there.</p>
<h3>How much is reflected?</h3>
<p>When the two media have very different wave speeds, most of the energy reflects (think of a wave hitting a wall). When the speeds match, almost nothing reflects and the wave passes through smoothly. This mismatch is why a change in mass per unit length along a string produces a partial reflection at the join — it is how a wave "knows" a boundary is there.</p>
<div class="callout callout--key"><p><b>中文对照.</b> 反射 reflection, 折射 refraction, 透射 transmission, 边界 boundary, 波速 wave speed. 固定端 fixed end 反射会反相（倒转），自由端 free end 反射不反相。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Do not assume "reflected = inverted" everywhere. Inversion happens at a fixed (or slower-medium) boundary; at a free (or faster-medium) boundary the reflection is upright. The sign of the phase change depends on which medium is "stiffer", not on the wave itself.</p></div>`
    },

    {
      h: "Superposition and stationary waves",
      body: `<h3>The principle of superposition</h3>
<p>Where two waves meet, the resultant displacement is the vector sum of the individual displacements. That is all. Two crests add to give a bigger crest; a crest and a trough cancel.</p>
<h3>How a stationary wave forms</h3>
<p>Send a wave down a string and reflect it. The incident and reflected waves travel in opposite directions with the same frequency and amplitude, so they superpose. The result is a pattern that does not travel — a <b>stationary wave</b> — with fixed points of zero displacement and fixed points of maximum displacement.</p>
<table><thead><tr><th>Feature</th><th>Definition</th><th>Spacing</th></tr></thead><tbody>
<tr><td>Node</td><td>a point of permanently zero displacement</td><td>nodes are <code>λ/2</code> apart</td></tr>
<tr><td>Antinode</td><td>a point of maximum displacement</td><td>antinodes are <code>λ/2</code> apart</td></tr>
<tr><td>Node to adjacent antinode</td><td>—</td><td><code>λ/4</code></td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The energy distinction, which is a favourite conceptual question.</b> In a <b>progressive</b> wave, energy is transferred through the medium. In a <b>stationary</b> wave, energy is not transferred — it sloshes back and forth between the nodes, being entirely kinetic at the antinodes and entirely potential at the extremes. This is why a stationary wave can exist on a string whose ends are fixed: no energy needs to leave.</p></div>
<h3>Comparing the two</h3>
<table><thead><tr><th>Property</th><th>Progressive wave</th><th>Stationary wave</th></tr></thead><tbody>
<tr><td>Amplitude</td><td>the same everywhere</td><td>varies from zero at nodes to a maximum at antinodes</td></tr>
<tr><td>Wavelength</td><td><code>λ</code> is the distance between consecutive crests</td><td>twice the node spacing</td></tr>
<tr><td>Energy transfer</td><td>yes, along the wave</td><td>no net transfer</td></tr>
<tr><td>Phase</td><td>points a wavelength apart are in phase</td><td>all points between adjacent nodes are in phase; points either side of a node are in antiphase</td></tr>
</tbody></table>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Superposition does not mean "the larger wave wins". Where a crest meets a trough of equal size the displacement is exactly zero at that instant — but both waves pass through each other unchanged afterwards. Waves in a linear medium do not collide; they superimpose and continue. Never add amplitudes as if one destroyed the other.</p></div>
<p>中文对照: 叠加 superposition, 驻波 stationary wave, 波节 node, 波腹 antinode. 相干波叠加才会形成稳定驻波。</p>`
    },

    {
      h: "Interference and path difference",
      body: `<p>Two coherent waves arriving at the same point add by superposition. Whether they reinforce or cancel depends on their <b>path difference</b> — the extra distance one has travelled — expressed in wavelengths.</p>
<table><thead><tr><th>Path difference</th><th>Phase relation</th><th>Result</th></tr></thead><tbody>
<tr><td><code>nλ</code> (whole number of wavelengths)</td><td>in phase</td><td>constructive — a maximum</td></tr>
<tr><td><code>(n + ½)λ</code> (odd number of half-wavelengths)</td><td>in antiphase</td><td>destructive — a minimum</td></tr>
</tbody></table>
<p>The link between path difference and phase difference is</p>
<div class="formula">Δφ = 2π × (path difference) / λ</div>
<p>so a path difference of <code>λ/2</code> corresponds to <code>π</code> radians (antiphase), and a path difference of <code>λ</code> corresponds to <code>2π</code> (back in phase). This is the same <code>2π Δx/λ</code> from the phase-difference formula at the start of the module — now <code>Δx</code> is a difference in route length rather than a separation along one wave.</p>
<h3>Why coherence matters</h3>
<p>For a steady pattern the two waves must be <b>coherent</b>: same frequency and a constant phase difference. If two independent sources have a phase difference that jitters randomly, the maxima and minima wander and average out to a uniform glow. That is why interference needs either one source split into two paths or two locked sources.</p>
<div class="callout callout--key"><p><b>中文对照.</b> 干涉 interference, 路程差 path difference, 相干 coherent, 相长干涉 constructive, 相消干涉 destructive. 路程差为 nλ 时相长，为 (n+½)λ 时相消。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> A common slip is to read "a half-wavelength path difference" as destructive but then forget any starting phase. If the two waves already start in antiphase (as at a fixed reflection boundary), a further path difference of <code>λ/2</code> brings them back into phase. Always count the total phase: reflection flip plus path delay.</p></div>`
    },

    {
      h: "Stationary waves on strings",
      body: `<p>Both ends of a stretched string are fixed, so both ends must be <b>nodes</b>. That constraint is what selects which wavelengths are allowed.</p>
<p>For the string to fit with nodes at both ends, its length must contain a whole number of half-wavelengths:</p>
<div class="formula">L = n λ/2        so   λ = 2L/n        for n = 1, 2, 3, …</div>
<p>Each value of <code>n</code> is a <b>harmonic</b>, and the corresponding frequency follows from <code>v = fλ</code>:</p>
<div class="formula">f = v/λ = nv/(2L)</div>
<table><thead><tr><th>Harmonic</th><th><code>n</code></th><th>Wavelength</th><th>Frequency</th><th>Nodes</th><th>Antinodes</th></tr></thead><tbody>
<tr><td>1st (fundamental)</td><td>1</td><td><code>2L</code></td><td><code>v/2L</code></td><td>2</td><td>1</td></tr>
<tr><td>2nd</td><td>2</td><td><code>L</code></td><td><code>v/L</code></td><td>3</td><td>2</td></tr>
<tr><td>3rd</td><td>3</td><td><code>2L/3</code></td><td><code>3v/2L</code></td><td>4</td><td>3</td></tr>
</tbody></table>
<p>Note the counting rule: for the <code>n</code>th harmonic there are <code>n+1</code> nodes and <code>n</code> antinodes.</p>
<h3>The first harmonic in terms of tension and mass per unit length</h3>
<p>Combining <code>f = v/2L</code> with the wave speed on a string <code>v = √(T/μ)</code>:</p>
<div class="formula">f₁ = (1/2L) √(T/μ)</div>
<p>where <code>T</code> is the tension and <code>μ</code> the mass per unit length. This is the equation a guitar tuner uses: tightening the string increases <code>T</code>, which raises the frequency. Note the square root — doubling the tension raises the pitch by only a factor of <code>√2</code>.</p>
<div class="callout callout--key"><p><b>The proportionality worth memorising.</b> For a fixed length and total mass, <code>f₁ ∝ √T</code> and <code>f₁ ∝ 1/√μ</code>. So to raise the pitch by an octave (double <code>f</code>) you must increase the tension by a factor of 4, or quarter the mass per unit length. A guitarist does the first by turning a tuning peg; the second is why bass strings are thicker or wound with metal.</p></div>
<p>中文对照: 谐波 harmonic, 基频 fundamental frequency, 节点 node, 腹点 antinode, 张力 tension. 第 n 谐波有 n+1 个节点、n 个腹点。</p>`
    },

    {
      h: "Stationary waves in pipes",
      body: `<p>The constraint in a pipe is on the air, and the boundary condition depends on whether the end is open or closed.</p>
<ul class="tight">
<li>At an <b>open</b> end, the air is free to move, so there is an <b>antinode</b>.</li>
<li>At a <b>closed</b> end, the air cannot move, so there is a <b>node</b>.</li>
</ul>
<h3>Pipe open at both ends</h3>
<p>Antinodes at both ends, so the length contains a whole number of half-wavelengths — exactly like a string:</p>
<div class="formula">L = nλ/2        f = nv/(2L)        all harmonics present</div>
<h3>Pipe closed at one end</h3>
<p>One node and one antinode, so the length contains an <b>odd</b> number of quarter-wavelengths:</p>
<div class="formula">L = (2n − 1)λ/4        f = (2n − 1)v/(4L)        only odd harmonics</div>
<div class="callout callout--key"><p><b>The result worth remembering, because it feels asymmetric.</b> A closed pipe supports only <b>odd</b> harmonics — the fundamental, the third, the fifth, and so on. The even ones are absent. And for the same length, a closed pipe has a fundamental frequency <b>half</b> that of an open pipe, because <code>v/4L</code> against <code>v/2L</code>. Both facts follow directly from the boundary conditions, and both are commonly asked.</p></div>
<h3>End correction</h3>
<p>In reality an antinode sits slightly beyond the open end, so the effective length is a little longer than the physical length. Competition questions sometimes mention this; if they do, add the correction to <code>L</code> before using the formulas.</p>
<div class="callout callout--key"><p><b>Counting without the formula.</b> Draw the boundary conditions: closed end = node, open end = antinode. A closed pipe of length <code>L</code> fits a quarter wavelength at its fundamental (node to antinode), so <code>L = λ/4</code>; each higher odd mode adds another half wavelength. An open pipe fits a half wavelength (antinode to antinode), so <code>L = λ/2</code>. Sketching the pattern beats algebra under pressure, and it is what the exam expects you to do in your head.</p></div>
<p>中文对照: 管 pipe, 闭管 closed pipe, 开管 open pipe, 奇次谐波 odd harmonics. 闭管只支持奇次谐波，基频是开管的一半。</p>`
    },

    {
      h: "The wave equation, and reading off quantities",
      body: `<p>A travelling wave is often written in the form</p>
<div class="formula">y = A cos(ωt + kx)</div>
<p>where <code>y</code> is the displacement of a particle, <code>A</code> the amplitude, and</p>
<div class="formula">ω = 2πf        (angular frequency, rad s⁻¹)
k = 2π/λ       (wave number, rad m⁻¹)</div>
<p>The question is almost always "extract the amplitude, frequency, wavelength and speed from this expression", and the method is purely one of recognition:</p>
<ol class="steps">
<li>The number multiplying the cosine is <code>A</code>.</li>
<li>The number multiplying <code>t</code> is <code>ω</code>, so <code>f = ω/2π</code>.</li>
<li>The number multiplying <code>x</code> is <code>k</code>, so <code>λ = 2π/k</code>.</li>
<li>Then <code>v = fλ = ω/k</code>.</li>
</ol>
<div class="callout callout--key"><p><b>The step people forget: <code>v = ω/k</code>.</b> This follows from <code>fλ = (ω/2π)(2π/k) = ω/k</code>. It is the fastest route from the equation to the speed, and it avoids computing <code>f</code> and <code>λ</code> separately.</p></div>
<h3>The sign in the bracket</h3>
<p>A <code>−</code> sign between the terms, <code>cos(ωt − kx)</code>, means the wave travels in the <code>+x</code> direction. A <code>+</code> sign, <code>cos(ωt + kx)</code>, means it travels in the <code>−x</code> direction. That is worth knowing because a question may ask which way a given wave is going.</p>
<h3>Sine or cosine</h3>
<p>The choice of <code>sin</code> or <code>cos</code> only shifts the wave along, so it corresponds to a different starting point. It does not change <code>A</code>, <code>ω</code>, <code>k</code> or <code>v</code> at all. Do not be distracted by it.</p>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> The coefficient of <code>x</code> is <code>k = 2π/λ</code>, not <code>λ</code>, and the coefficient of <code>t</code> is <code>ω = 2πf</code>, not <code>f</code>. A question will happily offer <code>λ = 3</code> when the equation actually says <code>k = 3</code>, betting you forget the <code>2π</code>. Always convert: <code>λ = 2π/k</code> and <code>f = ω/2π</code>. Also check the sign in the bracket before declaring a direction.</p></div>
<p>中文对照: 波数 wave number k, 角频率 angular frequency ω, 行波 travelling wave. <code>v = ω/k</code> 直接得波速。</p>`
    },

    {
      h: "Maximum particle speed versus wave speed",
      body: `<p>This is the classic trap of the module, and the options are always designed around it.</p>
<p>A particle in the medium oscillates up and down. Its displacement is <code>y = A cos(ωt)</code>, so its velocity is the derivative, whose maximum magnitude is</p>
<div class="formula">v_particle(max) = ωA</div>
<p>The <b>wave</b> speed, by contrast, is how fast the pattern moves:</p>
<div class="formula">v_wave = fλ = ω/k</div>
<p>These are <b>different quantities with different values</b>, and they are usually not equal.</p>
<table><thead><tr><th></th><th>Symbol</th><th>Depends on</th></tr></thead><tbody>
<tr><td>Maximum particle speed</td><td><code>ωA</code></td><td>amplitude and frequency</td></tr>
<tr><td>Wave speed</td><td><code>ω/k = fλ</code></td><td>the medium only — tension and mass per unit length for a string</td></tr>
</tbody></table>
<div class="callout callout--bad"><p><b>The conceptual difference worth stating.</b> Changing the amplitude of a wave on a string changes the maximum particle speed but does <b>not</b> change the wave speed. The wave speed is set by the medium. If you shake a rope harder you make the wave taller and the particles faster, but the disturbance still travels at the same speed. That sentence answers the standard question.</p></div>
<h3>Worked reading</h3>
<p>For <code>y = 0.02 cos(600t − 3x)</code> in SI units:</p>
<ul class="tight">
<li><code>A = 0.02 m</code></li>
<li><code>ω = 600 rad s⁻¹</code>, so <code>f = 600/2π ≈ 95 Hz</code></li>
<li><code>k = 3 rad m⁻¹</code>, so <code>λ = 2π/3 ≈ 2.1 m</code></li>
<li><code>v_wave = ω/k = 600/3 = 200 m s⁻¹</code></li>
<li><code>v_particle(max) = ωA = 600 × 0.02 = 12 m s⁻¹</code></li>
</ul>
<p>Note how different 200 and 12 are. That gap is exactly what the wrong options exploit.</p>
<div class="callout callout--key"><p><b>The cleanest one-line check.</b> Wave speed depends on the medium; particle speed depends on the wave's amplitude and frequency. Shake the same rope harder (larger <code>A</code>) and the particles move faster, but the wave still crawls along at the same speed. So if a question changes only the amplitude, the wave speed cannot change — and the answer that scales with <code>A</code> is the particle speed, not the wave speed.</p></div>
<p>中文对照: 质点速度 particle speed, 波速 wave speed. 振幅变大只让质点更快，不改变波速。</p>`
    },

    {
      h: "Wave speed on a string, and the speed of sound in a gas",
      body: `<h3>On a string</h3>
<div class="formula">v = √(T/μ)</div>
<p>where <code>T</code> is the tension in newtons and <code>μ</code> the mass per unit length in <code>kg m⁻¹</code>. Note that <code>μ</code> can be found from the total mass and length of the string: <code>μ = m/L</code>.</p>
<p>This is the same result you derived by dimensional analysis in module A, which is worth noting: the method gave the form <code>√(T/μ)</code> without any knowledge of waves.</p>
<h3>In a gas</h3>
<div class="formula">v = √(γP/ρ)</div>
<p>where <code>P</code> is the pressure, <code>ρ</code> the density, and <code>γ</code> the ratio of the specific heats (about 1.4 for air). For air at atmospheric pressure this gives about <code>330 m s⁻¹</code>, which is the right order.</p>
<h3>Temperature dependence</h3>
<p>For an ideal gas at constant pressure, heating increases the volume, so the density falls. Since <code>v ∝ 1/√ρ</code> and <code>ρ ∝ 1/T</code>, we get</p>
<div class="formula">v ∝ √T</div>
<p>where <code>T</code> is the <b>absolute</b> temperature in kelvin. This is why sound travels faster on a hot day. Note that <code>v ∝ √T</code> means doubling the absolute temperature increases the speed by only a factor of <code>√2 ≈ 1.41</code>.</p>
<div class="callout callout--warn"><p><b>Kelvin, not Celsius.</b> <code>v ∝ √T</code> requires absolute temperature. Sound travels at about 340 m s⁻¹ at 20 °C, which is 293 K. A question that gives you a Celsius temperature and asks about a speed ratio requires conversion first — and forgetting that is the standard error.</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong, twice over.</b> First, the temperature dependence is <code>v ∝ √T</code> with <i>absolute</i> temperature. If a question gives 20 °C and 40 °C, the ratio is <code>√293 / √313</code>, not <code>√20 / √40</code>. Using Celsius makes the speed ratio look like <code>√0.5 ≈ 0.7</code> — a decrease — when it actually rises slightly. Second, do not confuse <code>v = √(γP/ρ)</code> with the string formula; they share the square root but nothing else.</p></div>
<p>中文对照: 波速 wave speed, 弦 string, 气体 gas, 开尔文 kelvin. 升温使声速略增，用绝对温度。</p>`
    },

    {
      h: "Intensity and the inverse-square law",
      body: `<p>Intensity is power per unit area, in <code>W m⁻²</code>:</p>
<div class="formula">I = P/A</div>
<p>For a source radiating equally in all directions, the power spreads over a sphere of area <code>4πr²</code>, so</p>
<div class="formula">I = P/(4πr²)        so   I ∝ 1/r²</div>
<p>That is the inverse-square law, and it follows purely from geometry.</p>
<h3>Using it as a ratio, which is what questions ask</h3>
<div class="formula">I₂/I₁ = (r₁/r₂)²</div>
<p>So doubling the distance quarters the intensity; trebling it reduces the intensity to one ninth.</p>
<div class="callout callout--key"><p><b>The assumption worth stating.</b> The inverse-square law requires the source to radiate equally in all directions, or at least to be small compared with the distance. A long fluorescent tube is not a point source, so the law does not apply to it near the tube. Competition questions sometimes test whether you notice this.</p></div>
<h3>Amplitude and intensity</h3>
<p>Intensity is proportional to the square of the amplitude:</p>
<div class="formula">I ∝ A²</div>
<p>So if the amplitude doubles, the intensity quadruples. This is worth connecting to the inverse-square law: from <code>I ∝ 1/r²</code> and <code>I ∝ A²</code>, the amplitude must fall as <code>1/r</code>. Both statements are true and they are consistent, which is a satisfying check.</p>
<div class="callout callout--key"><p><b>Two links, one chain.</b> From <code>I ∝ A²</code> and <code>I ∝ 1/r²</code>, the amplitude of a spherical wave falls as <code>A ∝ 1/r</code>. So doubling the distance halves the amplitude but quarters the intensity. A question that asks about amplitude change when the distance doubles wants <code>½</code>, not <code>¼</code> — keep straight which quantity is being asked.</p></div>
<p>中文对照: 强度 intensity, 振幅 amplitude, 反平方定律 inverse-square law. 距离加倍 → 强度变 ¼，振幅变 ½。</p>`
    },

    {
      h: "The Doppler effect",
      body: `<p>When the source or the observer moves, the frequency measured is not the frequency emitted. The effect is everyday for sound: an approaching ambulance sounds higher in pitch as it comes, lower as it recedes.</p>
<h3>The two distinct cases</h3>
<p>The physics differs depending on <i>who</i> moves, because motion of the source changes the <b>wavelength</b> while motion of the observer changes the <b>rate at which wavefronts arrive</b>.</p>
<table><thead><tr><th>Case</th><th>Formula (speeds small compared with wave speed <code>v</code>)</th></tr></thead><tbody>
<tr><td>Source moves towards stationary observer at speed <code>v_s</code></td><td><code>f' = f · v / (v − v_s)</code></td></tr>
<tr><td>Source moves away</td><td><code>f' = f · v / (v + v_s)</code></td></tr>
<tr><td>Observer moves towards stationary source at speed <code>v_o</code></td><td><code>f' = f · (v + v_o) / v</code></td></tr>
<tr><td>Observer moves away</td><td><code>f' = f · (v − v_o) / v</code></td></tr>
</tbody></table>
<p>The sign rule is the thing to memorise, not the four formulas separately: <b>towards</b> → frequency goes <b>up</b>; <b>away</b> → frequency goes <b>down</b>. A source moving towards you crowds the wavefronts ahead (shorter wavelength), so the same wave speed now carries more cycles per second. An observer moving towards the source simply meets wavefronts more often.</p>
<h3>Why the two formulas are different</h3>
<p>For a moving <i>source</i> the wave speed in the medium is unchanged, but the wavelength is: <code>λ' = (v − v_s)/f</code> in front, so <code>f' = v/λ' = v f /(v − v_s)</code>. For a moving <i>observer</i> the wavelength is unchanged, but the relative speed of wavefronts to the observer is <code>v + v_o</code>, so <code>f' = (v + v_o)/λ</code>. Same direction of shift, different algebra — which is exactly why a question will offer you the wrong formula as a distractor.</p>
<div class="callout callout--key"><p><b>中文对照.</b> 多普勒效应 Doppler effect, 波源 source, 观察者 observer, 频率 frequency. 靠近 → 频率升高，远离 → 频率降低。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> The single biggest trap is swapping the source and observer formulas. If the <i>source</i> moves, the wavelength changes and the denominator of <code>v/(v ∓ v_s)</code> is what moves. If the <i>observer</i> moves, the wavelength is fixed and the numerator of <code>(v ± v_o)/v</code> is what moves. Pick the wrong one and you get a distractor option. Also note: for light the classical formulas are replaced by the relativistic Doppler shift, which is <b>not</b> Round 0 material — use these mechanical formulas for sound only.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A string of length 0.80 m is fixed at both ends and vibrates in its third harmonic. What is the wavelength?</p><p>A) 0.27 m &nbsp; B) 0.40 m &nbsp; C) 0.53 m &nbsp; D) 0.80 m &nbsp; E) 2.4 m</p>",
      sol: `<p>Use <code>L = nλ/2</code> with <code>n = 3</code>:</p>
<div class="formula">0.80 = 3λ/2   →   λ = 2 × 0.80/3 = 1.60/3 ≈ 0.53 m</div>
<p><b>Answer: C.</b></p>
<p><b>The picture, which is faster than the formula.</b> In the third harmonic there are three antinodes and four nodes. The four nodes divide the string into three equal segments, each of which is half a wavelength. So each segment is <code>0.80/3 = 0.267 m</code>, and the wavelength is twice that, <code>0.533 m</code> ✓. Sketching the harmonic and counting segments is more reliable than recalling the formula under pressure.</p>
<p><b>The traps.</b> Option A, 0.27 m, is the segment length — half a wavelength — which is the quantity you compute first and then forget to double. Option B, <code>0.40 m</code>, is the <b>fourth</b> harmonic's wavelength, and option D, <code>0.80 m</code>, is the <b>second</b> harmonic's — equal to the string length itself. All three are the wavelengths of other harmonics, which is what makes this a good discrimination question.</p>
<p><b>The general check.</b> Higher harmonics have <b>shorter</b> wavelengths, so the third harmonic must have a wavelength less than the fundamental's 1.60 m and less than the second harmonic's 0.80 m. That eliminates D and E immediately and leaves only A, B or C — and the segment argument settles it.</p>`,
      tag: "Harmonics on a string"
    },
    {
      q: "<p>A wave is described by <code>y = 0.05 cos(400t − 4x)</code> in SI units. What is the speed of the wave?</p><p>A) 0.01 m s⁻¹ &nbsp; B) 20 m s⁻¹ &nbsp; C) 100 m s⁻¹ &nbsp; D) 1600 m s⁻¹ &nbsp; E) 0.05 m s⁻¹</p>",
      sol: `<p>Read the coefficients: <code>ω = 400 rad s⁻¹</code> and <code>k = 4 rad m⁻¹</code>. The wave speed is</p>
<div class="formula">v = ω/k = 400/4 = 100 m s⁻¹</div>
<p><b>Answer: C.</b></p>
<p><b>The same answer by the longer route, as a check.</b> <code>f = ω/2π = 400/6.28 ≈ 63.7 Hz</code>, and <code>λ = 2π/k = 6.28/4 ≈ 1.57 m</code>. Then <code>v = fλ = 63.7 × 1.57 ≈ 100 m s⁻¹</code> ✓. The <code>2π</code> factors cancel, which is exactly why <code>v = ω/k</code> is worth knowing directly.</p>
<p><b>The trap, and it is the whole point of the question.</b> Option B, 20 m s⁻¹, is <code>ωA = 400 × 0.05</code> — the <b>maximum particle speed</b>, not the wave speed. Option A, 0.01 m s⁻¹, is <code>Aω</code> with a slip, and option E is the amplitude itself. The distinction between the speed of the pattern and the speed of the particles is the single most tested idea in this module.</p>
<p><b>Notice that the two speeds differ by a factor of five here.</b> There is no general relationship between them — you could change the amplitude to 0.5 m and the particle speed would become 200 m s⁻¹ while the wave speed stayed at exactly 100 m s⁻¹. That independence is the physical content.</p>`,
      tag: "Wave equation — and the particle-speed trap"
    },
    {
      q: "<p>A pipe closed at one end and open at the other has a fundamental frequency of 150 Hz. What is the frequency of the next higher harmonic it can produce?</p><p>A) 225 Hz &nbsp; B) 300 Hz &nbsp; C) 450 Hz &nbsp; D) 600 Hz &nbsp; E) 900 Hz</p>",
      sol: `<p>A closed pipe supports only <b>odd</b> harmonics: the fundamental, the third, the fifth, and so on.</p>
<p>The next higher harmonic after the first is therefore the <b>third</b>, whose frequency is three times the fundamental:</p>
<div class="formula">f₃ = 3 × 150 = 450 Hz</div>
<p><b>Answer: C.</b></p>
<p><b>Why the even harmonics are missing.</b> In a closed pipe there is a node at the closed end and an antinode at the open end, so the length must contain an odd number of quarter-wavelengths: <code>L = λ/4, 3λ/4, 5λ/4, …</code>. A length of <code>2λ/4 = λ/2</code> would require a node at both ends, which an open end cannot provide. The boundary condition itself forbids the even harmonics.</p>
<p><b>The traps.</b> Option B, 300 Hz, is the second harmonic, which does not exist in a closed pipe — it is the answer you get by assuming all harmonics are present, as in an open pipe or a string. Option A, 225 Hz, comes from multiplying by 1.5 instead of 3.</p>
<p><b>The comparison worth knowing.</b> An open pipe of the same length would have a fundamental of <code>2 × 150 = 300 Hz</code>, because <code>f = v/2L</code> against <code>v/4L</code>. So a closed pipe sounds an octave lower than an open pipe of the same length, and its harmonic series is missing every other note. That is why a stopped organ pipe sounds different in character from an open one, not merely lower.</p>`,
      tag: "Closed pipe — odd harmonics only"
    },
    {
      q: "<p>A sound source produces a power of 0.20 W uniformly in all directions. What is the intensity at a distance of 4.0 m? Take <code>π ≈ 3.1</code>.</p><p>A) <code>1.0 × 10⁻³ W m⁻²</code> &nbsp; B) <code>2.5 × 10⁻³ W m⁻²</code> &nbsp; C) <code>1.0 × 10⁻² W m⁻²</code> &nbsp; D) <code>4.0 × 10⁻³ W m⁻²</code> &nbsp; E) <code>5.0 × 10⁻² W m⁻²</code></p>",
      sol: `<p>The power spreads over a sphere of radius 4.0 m:</p>
<div class="formula">A = 4πr² = 4 × 3.1 × 16 = 198.4 m² ≈ 200 m²</div>
<p>Then</p>
<div class="formula">I = P/A = 0.20/200 = 1.0 × 10⁻³ W m⁻²</div>
<p><b>Answer: A.</b></p>
<p><b>The mental route, which avoids the multiplication.</b> Note that <code>4πr²</code> with <code>π ≈ 3</code> is approximately <code>12r² = 12 × 16 ≈ 190</code>, and rounding to 200 costs nothing at this precision. Then <code>0.20/200 = 10⁻³</code>. Two round numbers, no long multiplication.</p>
<p><b>The traps.</b> Option B, <code>2.5 × 10⁻³</code>, is what you get from forgetting the factor of 4 — using <code>πr²</code>, the area of a circle rather than a sphere. Option C, <code>1.0 × 10⁻²</code>, is ten times too large, which comes from a powers-of-ten slip in the division.</p>
<p><b>The extension worth doing.</b> What is the intensity at 8.0 m? By the inverse-square law it is a quarter of the value at 4.0 m, so <code>2.5 × 10⁻⁴ W m⁻²</code>. No need to redo the area calculation — the ratio <code>(4/8)² = ¼</code> gives it immediately. That is exactly the ratio reasoning from module A, and it is the fastest route whenever the distance changes rather than the source.</p>`,
      tag: "Intensity — inverse square"
    },

    {
      q: "<p>Two strings A and B have the same length and the same tension, but string B has four times the mass per unit length of string A. What is the ratio <code>f_B / f_A</code> of their fundamental frequencies?</p><p>A) <code>1/4</code> &nbsp; B) <code>1/2</code> &nbsp; C) <code>1</code> &nbsp; D) <code>2</code> &nbsp; E) <code>4</code></p>",
      sol: `<p>The fundamental frequency of a stretched string is</p>
<div class="formula">f = (1/2L) √(T/μ)</div>
<p>Both strings share <code>L</code> and <code>T</code>, so the only differing quantity is <code>μ</code>. Frequency is therefore inversely proportional to the square root of the mass per unit length:</p>
<div class="formula">f ∝ 1/√μ</div>
<p>With <code>μ_B = 4 μ_A</code>:</p>
<div class="formula">f_B / f_A = √(μ_A / μ_B) = √(1/4) = 1/2</div>
<p><b>Answer: B, <code>1/2</code>.</b></p>
<p><b>The trap.</b> Option E, <code>4</code>, is what you get if you forget the square root and use <code>f ∝ μ</code> instead of <code>f ∝ 1/√μ</code> — the heavier string vibrates more slowly, not faster. Option A, <code>1/4</code>, comes from using <code>f ∝ 1/μ</code> (inverting but dropping the root). Both are structural errors in the proportionality, which is exactly what this question probes. No arithmetic was needed — only the square-root dependence.</p>
<p><b>The check.</b> A heavier string stores more inertia per unit length, so it oscillates slower; the answer must be less than 1. That alone eliminates D and E before any formula is written.</p>`,
      tag: "Frequency ratio — no calculator"
    },

    {
      q: "<p>A string of length 1.20 m is fixed at both ends and vibrates in its third harmonic. How many nodes does the standing-wave pattern have, counting the fixed ends?</p><p>A) 2 &nbsp; B) 3 &nbsp; C) 4 &nbsp; D) 5 &nbsp; E) 6</p>",
      sol: `<p>For the <code>n</code>th harmonic on a string fixed at both ends there are <code>n + 1</code> nodes (including both ends). The third harmonic has <code>n = 3</code>, so the node count is</p>
<div class="formula">nodes = 3 + 1 = 4</div>
<p>Check from the geometry: <code>L = nλ/2</code> gives <code>λ = 2L/n = 2 × 1.20 / 3 = 0.80 m</code>. Nodes are spaced <code>λ/2 = 0.40 m</code> apart, and the number of nodes along the string is <code>L / (λ/2) + 1 = 1.20 / 0.40 + 1 = 4</code> ✓.</p>
<p><b>Answer: C.</b></p>
<p><b>The traps.</b> Option B, 3, is the number of <b>antinodes</b> in the third harmonic (there are <code>n</code> antinodes) — a quantity you compute on the way and then mislabel. Option A, 2, is the node count of the first harmonic, and option D, 5, is the node count of the fourth harmonic. Each distractor is a genuine count from a different mode, which is what makes this a clean discrimination question.</p>
<p><b>The rule to learn.</b> <code>n</code>th harmonic → <code>n</code> antinodes and <code>n + 1</code> nodes. Fix that pair and every node/antinode question becomes a one-line lookup.</p>`,
      tag: "Standing-wave node count"
    },

    {
      q: "<p>A stationary source emits sound of frequency <code>f</code>. An observer moves directly towards the source at speed <code>v_o</code>, where <code>v_o</code> is much smaller than the wave speed <code>v</code>. What is the observed frequency <code>f'</code>?</p><p>A) <code>f v / (v − v_o)</code> &nbsp; B) <code>f (v − v_o) / v</code> &nbsp; C) <code>f (v + v_o) / v</code> &nbsp; D) <code>f v / (v + v_o)</code> &nbsp; E) <code>f</code></p>",
      sol: `<p>The observer moving <b>towards</b> the source meets wavefronts more often, so the observed frequency must be <b>higher</b> than <code>f</code>. With the wavelength unchanged at <code>λ = v/f</code>, the relative speed of wavefronts to the moving observer is <code>v + v_o</code>, giving</p>
<div class="formula">f' = (v + v_o) / λ = (v + v_o) / (v/f) = f (v + v_o) / v</div>
<p><b>Answer: C.</b></p>
<p><b>The trap — and it is the whole point.</b> Option A, <code>f v / (v − v_o)</code>, is the formula for a <b>source</b> moving towards a stationary observer, not a moving observer. The two look similar and both raise the pitch, which is exactly why they are offered side by side: if you cannot tell who is moving, you cannot tell which formula applies. Here the observer moves, so the wavelength is fixed and the <b>numerator</b> carries the <code>v_o</code>; for a moving source the wavelength changes and the <b>denominator</b> carries it.</p>
<p><b>Why the others die.</b> B has <code>v − v_o</code> in the numerator, which would <i>lower</i> the frequency — that is the observer moving <b>away</b>. D is the source moving away. E is no motion at all. Only C gives a higher frequency with the speed in the numerator where a moving observer puts it.</p>
<p><b>The direction rule.</b> Towards → up; away → down. Once you know the direction of the shift you have already killed B, D and E, leaving only A and C to distinguish by asking who is moving.</p>`,
      tag: "Doppler — moving observer"
    }
  ],

  traps: [
    "Confusing the maximum particle speed <code>ωA</code> with the wave speed <code>ω/k</code>. They are different quantities and usually different values.",
    "Using amplitude where peak-to-peak distance is meant, or the reverse. Peak-to-peak is <code>2A</code>.",
    "Thinking the amplitude affects the wave speed. On a string the speed depends only on tension and mass per unit length.",
    "Assuming a closed pipe supports all harmonics. It supports odd harmonics only.",
    "Forgetting to double the segment length when finding a wavelength from a harmonic diagram.",
    "Using <code>v ∝ √T</code> with a Celsius temperature. It requires kelvin.",
    "Assuming a wave changes frequency when it crosses a boundary. Speed and wavelength change; frequency does not.",
    "Using <code>πr²</code> instead of <code>4πr²</code> for the area a point source's power spreads over."
  ],

  checklist: [
    { id: "F1", flag: "CORE", text: "Progressive wave vocabulary: amplitude, wavelength, frequency, period, phase, phase difference — precisely defined." },
    { id: "F2", flag: "CORE", text: "<code>v = fλ</code> and <code>f = 1/T</code>; phase difference <code>Δφ = 2πΔx/λ</code>; moving between radians, degrees and fractions of a cycle." },
    { id: "F3", flag: "CORE", text: "Longitudinal versus transverse; polarisation as evidence of transversality, and the reverse argument." },
    { id: "F4", flag: "CORE", text: "The electromagnetic spectrum; all EM waves travel at <code>c</code> in a vacuum; visible wavelengths of order <code>10⁻⁷ m</code>." },
    { id: "F5", flag: "CORE", text: "Superposition, and the formation of stationary waves by reflection; node and antinode spacing; the energy distinction from a progressive wave." },
    { id: "F6", flag: "CORE", text: "Stationary waves on strings: <code>L = nλ/2</code>, harmonics, and the node and antinode counting rules." },
    { id: "F7", flag: "CORE", text: "The first harmonic frequency <code>f = (1/2L)√(T/μ)</code>, and how tension and mass per unit length affect pitch." },
    { id: "F8", flag: "CORE", text: "Stationary waves in pipes: open at both ends versus closed at one end, and the odd-harmonics-only result." },
    { id: "F9", flag: "R1-ONLY", text: "Beats and beat frequency. Round 1 material — insurance only." },
    { id: "F10", flag: "CORE", text: "The wave equation <code>y = A cos(ωt + kx)</code>: extract <code>A</code>, <code>ω</code>, <code>k</code>, then <code>f</code>, <code>λ</code> and <code>v = ω/k</code>." },
    { id: "F11", flag: "CORE", text: "Maximum particle speed <code>ωA</code> versus wave speed <code>ω/k</code>, and why changing the amplitude does not change the wave speed." },
    { id: "F12", flag: "CORE", text: "Wave speed on a string <code>v = √(T/μ)</code>; speed of sound in a gas <code>v = √(γP/ρ)</code>; the temperature dependence <code>v ∝ √T</code> in kelvin." },
    { id: "F13", flag: "R1-ONLY", text: "The Doppler effect. Round 1 material — insurance only." },
    { id: "F14", flag: "CORE", text: "Intensity <code>P/A</code>, the inverse-square law for a point source, and <code>I ∝ A²</code>." }
  ]
},

{
  code: "G",
  title: "Optics",
  short: "Optics",
  priority: 3,
  tier: "Tier A — inside AQA AS §3.3.2, and two sample-paper questions",
  why: "A formulaic module with two near-guaranteed question types: refraction with total internal reflection, and Young's double slit. The sample paper tested both — S8 is a critical-angle question and S4 is an interference question. Learn the patterns and the marks are reliable.",
  warn: null,

  sections: [
    {
      h: "The law of reflection",
      body: `<p>The simplest optical rule: a ray reflected from a smooth surface leaves at the same angle it arrived, measured from the <b>normal</b> (the line perpendicular to the surface).</p>
<div class="formula">θ_incidence = θ_reflection</div>
<ul class="tight">
<li><b>Specular reflection</b> (a mirror): the surface is smooth on the scale of the wavelength, so all rays obey the law and a clear image forms.</li>
<li><b>Diffuse reflection</b> (paper, wall): the surface is rough, so each bit reflects at its own local normal and the reflected light scatters — no image, just illumination.</li>
</ul>
<h3>Plane mirrors and images</h3>
<p>A plane mirror forms a <b>virtual</b> image: the object and image are the same size, the same distance behind the mirror as the object is in front, and the image is laterally inverted (left–right swapped). "Virtual" means the rays do not actually pass through the image point — they only appear to come from there, so the image cannot be projected onto a screen.</p>
<div class="callout callout--key"><p><b>中文对照.</b> 反射定律 law of reflection, 镜面反射 specular reflection, 漫反射 diffuse reflection, 平面镜 plane mirror, 虚像 virtual image. 入射角等于反射角，均从法线量起。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Always measure from the normal, never from the surface. A ray hitting a surface at 30° to the surface has an angle of incidence of 60° from the normal, and reflects 60° from the normal — which is 30° to the surface on the other side. Mixing up "to the surface" and "to the normal" is the standard reflection error.</p></div>`
    },

    {
      h: "Refractive index and Snell's law",
      body: `<p>The refractive index of a medium is the ratio of the speed of light in a vacuum to its speed in the medium:</p>
<div class="formula">n = c/c_s</div>
<p>Since light travels fastest in a vacuum, <code>n ≥ 1</code> always. For air, <code>n ≈ 1.00</code> to three significant figures, so air is usually treated as vacuum. For water <code>n = 1.33</code>; for glass it is typically 1.5 to 1.6.</p>
<h3>Snell's law</h3>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂</div>
<p>where <code>θ₁</code> and <code>θ₂</code> are measured from the <b>normal</b>, not from the surface. This is the most common error in the topic: an angle measured from the surface must be converted to an angle from the normal before use.</p>
<div class="callout callout--key"><p><b>What refraction actually is, physically.</b> The frequency is set by the source and cannot change. When light enters a denser medium its speed falls, so <code>λ = v/f</code> falls too. The change of direction is the consequence of the wavefronts bending as one part of the wave slows before the other — exactly like a marching band turning when one flank slows down. That analogy is worth being able to give.</p></div>
<h3>Which way does the ray bend?</h3>
<p>Into a denser medium (<code>n</code> increases), the ray bends <b>towards</b> the normal. Into a less dense medium, it bends <b>away</b> from the normal. A quick check: from air into glass, the ray bends towards the normal, and the angle from the normal decreases.</p>
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="A ray of light passing from air into glass, bending towards the normal so the angle of refraction is smaller than the angle of incidence.">
<defs>
<marker id="cr-r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#b3352f"/></marker>
<marker id="cr-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2f5fd0"/></marker>
</defs>
<text x="240" y="24" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">Refraction: the ray bends towards the normal</text>
<rect x="50" y="60" width="380" height="90" fill="#f7f8fa"/>
<rect x="50" y="150" width="380" height="106" fill="#eef2fb"/>
<line x1="50" y1="150" x2="430" y2="150" stroke="#1f2937" stroke-width="2"/>
<line x1="240" y1="46" x2="240" y2="252" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="6 5"/>
<text x="248" y="54" font-size="11.5" fill="#7b8494">normal</text>
<line x1="150" y1="60" x2="240" y2="150" stroke="#b3352f" stroke-width="2.5" marker-end="url(#cr-r)"/>
<line x1="240" y1="150" x2="298" y2="256" stroke="#2f5fd0" stroke-width="2.5" marker-end="url(#cr-b)"/>
<line x1="240" y1="150" x2="330" y2="60" stroke="#cbd2dd" stroke-width="1.5" stroke-dasharray="5 4"/>
<path d="M240,90 A60,60 0 0 0 198,108" fill="none" stroke="#7b8494" stroke-width="1.4"/>
<path d="M240,210 A60,60 0 0 0 268,203" fill="none" stroke="#7b8494" stroke-width="1.4"/>
<text x="204" y="132" text-anchor="end" font-size="12" font-weight="600" fill="#b3352f">θ₁ = 45°</text>
<text x="276" y="196" font-size="12" font-weight="600" fill="#2f5fd0">θ₂ ≈ 28°</text>
<text x="62" y="82" font-size="12" fill="#4a5262">air   n₁ = 1.00</text>
<text x="62" y="242" font-size="12" fill="#4a5262">glass  n₂ = 1.50</text>
<text x="146" y="52" font-size="12" fill="#b3352f">incident ray</text>
<text x="306" y="272" font-size="12" fill="#2f5fd0">refracted ray</text>
<text x="336" y="56" font-size="12" fill="#9aa4b4">reflected (faint)</text>
</svg>
<figcaption><b>Both angles are measured from the normal.</b> Entering the denser medium the ray slows, so it turns <i>towards</i> the normal and <code>θ₂ &lt; θ₁</code>. A useful check: any answer with <code>θ₂ &gt; θ₁</code> on entering glass is wrong before you finish the arithmetic. Note also that Snell's law relates the <i>sines</i>, not the angles — <code>θ₂</code> is not <code>θ₁/n</code>.</figcaption>
</figure>
<div class="callout callout--key"><p><b>Why <code>n = c/c_s</code> and Snell are the same law.</b> From <code>v = fλ</code> with fixed frequency, <code>λ = v/f</code>, so a slower medium has a shorter wavelength. Snell's law <code>n₁ sin θ₁ = n₂ sin θ₂</code> rearranges to <code>sin θ₁ / sin θ₂ = n₂/n₁ = (c/v₂)/(c/v₁) = v₁/v₂</code> — exactly the mechanical refraction rule with speeds. Light bending is just wave speed changing at a boundary.</p></div>
<p>中文对照: 折射率 refractive index, 斯涅尔定律 Snell's law, 法线 normal, 入射角 angle of incidence. 光从光疏到光密介质会向法线偏折。</p>`
    },

    {
      h: "Total internal reflection",
      body: `<p>When light travels from a denser medium to a less dense one, it bends away from the normal. As the angle of incidence increases, the angle of refraction increases faster, and eventually reaches 90° — the refracted ray runs along the surface. Beyond that angle, no light refracts out at all, and all of it reflects back inside. That is <b>total internal reflection</b>.</p>
<p>The angle at which refraction reaches 90° is the <b>critical angle</b>. Setting <code>θ₂ = 90°</code> in Snell's law, so that <code>sin θ₂ = 1</code>:</p>
<div class="formula">n₁ sin θ_c = n₂ × 1        so   sin θ_c = n₂/n₁</div>
<p>When the second medium is air, <code>n₂ ≈ 1</code>, and this simplifies to the form most often used:</p>
<div class="formula">sin θ_c = 1/n</div>
<figure class="fig">
<svg viewBox="0 0 480 320" role="img" aria-label="Two rays inside glass hitting the surface: one below the critical angle refracts out into the air, one above it is totally internally reflected.">
<defs>
<marker id="ct-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2f5fd0"/></marker>
<marker id="ct-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1f7a53"/></marker>
</defs>
<text x="240" y="26" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">Total internal reflection: two incidence angles</text>
<rect x="40" y="50" width="400" height="110" fill="#f7f8fa"/>
<rect x="40" y="160" width="400" height="96" fill="#eef2fb"/>
<line x1="40" y1="160" x2="440" y2="160" stroke="#1f2937" stroke-width="2"/>
<line x1="140" y1="54" x2="140" y2="250" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="6 5"/>
<line x1="360" y1="54" x2="360" y2="250" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="6 5"/>
<line x1="112" y1="220" x2="140" y2="160" stroke="#2f5fd0" stroke-width="2.5" marker-end="url(#ct-b)"/>
<line x1="140" y1="160" x2="213" y2="70" stroke="#2f5fd0" stroke-width="2.5" marker-end="url(#ct-b)"/>
<line x1="274" y1="220" x2="360" y2="160" stroke="#1f7a53" stroke-width="2.5" marker-end="url(#ct-g)"/>
<line x1="360" y1="160" x2="232" y2="70" stroke="#1f7a53" stroke-width="2.5" marker-end="url(#ct-g)"/>
<path d="M140,220 A60,60 0 0 1 115,214" fill="none" stroke="#7b8494" stroke-width="1.4"/>
<path d="M140,100 A60,60 0 0 1 178,113" fill="none" stroke="#7b8494" stroke-width="1.4"/>
<path d="M360,220 A60,60 0 0 1 311,194" fill="none" stroke="#7b8494" stroke-width="1.4"/>
<text x="108" y="236" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">θ₁ = 25°</text>
<text x="194" y="106" font-size="12" font-weight="600" fill="#2f5fd0">θ₂ ≈ 39°</text>
<text x="264" y="216" text-anchor="end" font-size="12" font-weight="600" fill="#1f7a53">θ₁ = 55°</text>
<text x="50" y="68" font-size="12" fill="#4a5262">air   n = 1.00</text>
<text x="50" y="248" font-size="12" fill="#4a5262">glass  n = 1.50</text>
<line x1="56" y1="282" x2="84" y2="282" stroke="#2f5fd0" stroke-width="3"/>
<text x="92" y="286" font-size="12" fill="#2f5fd0">θ₁ = 25° &lt; θ_c: refracts out, bending away</text>
<line x1="56" y1="304" x2="84" y2="304" stroke="#1f7a53" stroke-width="3"/>
<text x="92" y="308" font-size="12" fill="#1f7a53">θ₁ = 55° &gt; θ_c: totally internally reflected</text>
</svg>
<figcaption><b>Above the critical angle, nothing gets out.</b> Inside the glass the ray bends <i>away</i> from the normal as it tries to escape. At <code>θ_c</code> the refracted ray would run along the surface; beyond it, refraction is impossible and <b>all</b> the light reflects back inside. For glass <code>sin θ_c = 1/1.5 ≈ 0.667</code>, so <code>θ_c ≈ 42°</code> — and the two rays above sit either side of it.</figcaption>
</figure>
<h3>The two conditions for total internal reflection</h3>
<ol class="tight">
<li>Light must be travelling from a denser medium to a less dense one. It cannot happen the other way.</li>
<li>The angle of incidence must exceed the critical angle.</li>
</ol>
<div class="callout callout--key"><p><b>Sample question S8 tests exactly this.</b> A typical form is: light enters a prism or a block at some angle, and you must determine whether it emerges from the far face or undergoes total internal reflection there. The method is always the same — work out the angle of incidence at the second face using geometry, compare it with the critical angle, and decide.</p></div>
<h3>Critical angles worth knowing</h3>
<table><thead><tr><th>Interface</th><th><code>n</code></th><th>Critical angle</th></tr></thead><tbody>
<tr><td>water → air</td><td>1.33</td><td>49°</td></tr>
<tr><td>glass (n = 1.5) → air</td><td>1.50</td><td>42°</td></tr>
<tr><td>diamond → air</td><td>2.42</td><td>24°</td></tr>
</tbody></table>
<p>Diamond's very small critical angle is why it sparkles: light entering it is reflected internally many times before emerging, so a great deal of light is directed back out towards the viewer.</p>
<div class="callout callout--key"><p><b>Worked critical-angle estimate, no calculator.</b> For glass <code>n = 1.5</code>, <code>sin θ_c = 1/1.5 = 2/3 ≈ 0.667</code>. Since <code>sin 42° ≈ 0.669</code>, <code>θ_c ≈ 42°</code>. The key is to compare <code>1/n</code> with familiar sines: <code>sin 30° = 0.5</code>, <code>sin 45° ≈ 0.707</code>. If <code>1/n</code> lies between them, the critical angle lies between 30° and 45°. That brackets the answer without any calculator.</p></div>
<p>中文对照: 全内反射 total internal reflection, 临界角 critical angle. 光从光密到光疏且入射角大于临界角时发生。</p>`
    },

    {
      h: "Prisms",
      body: `<p>A prism is just two refracting surfaces, and the analysis is two applications of Snell's law with a geometry step between them.</p>
<h3>The method</h3>
<ol class="steps">
<li>Apply Snell's law at the first face to find the angle of refraction inside the prism.</li>
<li>Use the prism's geometry to find the angle of incidence at the second face. For a prism of apex angle <code>A</code>, the relationship is <code>r₁ + r₂ = A</code>, where <code>r₁</code> and <code>r₂</code> are the internal angles at the two faces.</li>
<li>Compare <code>r₂</code> with the critical angle. If <code>r₂</code> exceeds it, total internal reflection occurs at the second face and no light emerges there.</li>
<li>If <code>r₂</code> is below the critical angle, apply Snell's law again to find the angle of emergence.</li>
</ol>
<div class="callout callout--key"><p><b>The geometry identity <code>r₁ + r₂ = A</code> is worth memorising.</b> It comes from the triangle formed by the two normals and the apex, and it is the step most people miss. Without it you cannot get from the first face to the second.</p></div>
<h3>Range of angles for emergence</h3>
<p>A question may ask for the range of incident angles for which light emerges from the second face at all. The boundary case is <code>r₂ = θ_c</code>, which via <code>r₁ + r₂ = A</code> gives <code>r₁ = A − θ_c</code>, and then Snell's law at the first face gives the limiting incident angle. That is the whole calculation, and it is a standard competition question.</p>
<h3>Dispersion</h3>
<p>Because <code>n</code> varies slightly with wavelength — larger for violet, smaller for red — the prism spreads white light into a spectrum. The violet end is deviated more. This is <b>dispersion</b>, and it is the same phenomenon that causes rainbows.</p>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> When applying <code>r₁ + r₂ = A</code>, both <code>r₁</code> and <code>r₂</code> are the <b>internal</b> angles measured from the normal <i>inside</i> the glass. A common slip is to use the external incidence angle as <code>r₁</code>. The first face always refracts the ray <i>towards</i> the normal on entry (going glass-wards from air), so <code>r₁ &lt; θ₁</code>. Compute <code>r₁</code> from Snell first; do not reuse the incidence angle.</p></div>
<p>中文对照: 棱镜 prism, 顶角 apex angle, 色散 dispersion. 紫光偏折最大，红光最小。</p>`
    },

    {
      h: "Optical fibres",
      body: `<p>An optical fibre guides light by repeated total internal reflection. Most of the questions are descriptive rather than numerical, so learn the vocabulary and the reasons.</p>
<h3>Structure</h3>
<p>A central <b>core</b> of higher refractive index surrounded by <b>cladding</b> of slightly lower refractive index. Light in the core striking the boundary at more than the critical angle is totally internally reflected and stays in the core. The cladding also protects the surface from scratches, which would otherwise destroy the reflection.</p>
<h3>The two kinds of dispersion</h3>
<table><thead><tr><th>Type</th><th>Cause</th><th>Effect</th></tr></thead><tbody>
<tr><td>Modal dispersion</td><td>different rays travel by different paths — some zigzag more than others, so they cover different distances</td><td>The pulse spreads out in time, blurring the signal. Reduced by using a monomode fibre with a very thin core.</td></tr>
<tr><td>Material dispersion</td><td>different wavelengths travel at different speeds, because <code>n</code> depends on wavelength</td><td>The pulse spreads because its different colour components arrive at different times. Reduced by using a very pure monochromatic source.</td></tr>
</tbody></table>
<h3>Other loss mechanisms</h3>
<ul class="tight">
<li><b>Absorption</b> — the glass absorbs some of the light, particularly at certain wavelengths. Fibres are made from very pure glass and used at wavelengths where absorption is minimal.</li>
<li><b>Scattering</b> — imperfections in the glass deflect light out of the core.</li>
</ul>
<div class="callout callout--key"><p><b>Why pulse broadening matters.</b> A digital signal is a sequence of pulses. If each pulse spreads out in time, it starts to overlap with its neighbours and the receiver can no longer tell a 1 from a 0. That is why dispersion limits both the maximum length of a fibre link and the maximum data rate. Stating the consequence, not just the mechanism, is what earns the mark.</p></div>
<div class="callout callout--good"><p><b>The acceptance cone.</b> Only rays entering the core within a certain angle are trapped by total internal reflection; this range is set by the difference in refractive index between core and cladding. A larger index step gives a wider acceptance cone and better light capture. Stating the role of the core–cladding index difference is what turns a description into an explanation.</p></div>
<p>中文对照: 光纤 optical fibre, 纤芯 core, 包层 cladding, 脉冲展宽 pulse broadening. 阶跃折射率 step-index 光纤靠全内反射导光。</p>`
    },

    {
      h: "Lenses — converging and diverging, real and virtual images",
      body: `<p>A lens bends rays by refraction at two curved surfaces. The two types behave oppositely.</p>
<table><thead><tr><th></th><th>Converging (convex, positive)</th><th>Diverging (concave, negative)</th></tr></thead><tbody>
<tr><td>Shape</td><td>thicker in the middle</td><td>thinner in the middle</td></tr>
<tr><td>Action on parallel rays</td><td>brings them to a focus at the focal point <code>F</code></td><td>spreads them as if from a focal point in front</td></tr>
<tr><td>Image for a real object</td><td>real and inverted if the object is beyond <code>f</code>; virtual, upright and magnified if inside <code>f</code> (a magnifying glass)</td><td>always virtual, upright and diminished</td></tr>
</tbody></table>
<h3>Real versus virtual images</h3>
<ul class="tight">
<li><b>Real image:</b> the rays actually converge at the image point. It can be projected onto a screen and is always inverted for a single converging lens. Formed when the object is beyond the focal length.</li>
<li><b>Virtual image:</b> the rays only <i>appear</i> to diverge from the image point; they never meet there. It cannot be projected, is upright, and is what you see when using a magnifying glass or a diverging lens.</li>
</ul>
<h3>The three principal rays (for sketching)</h3>
<ol class="tight">
<li>A ray parallel to the axis leaves through the focal point (converging) or as if from the focal point (diverging).</li>
<li>A ray through the centre of the lens is undeviated.</li>
<li>A ray through the near focal point emerges parallel to the axis (converging).</li>
</ol>
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="Ray diagram for a converging lens with the object beyond 2F, showing a real inverted image formed beyond the far focal point.">
<defs>
<marker id="cl-r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#b3352f"/></marker>
<marker id="cl-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1f7a53"/></marker>
</defs>
<text x="240" y="26" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">Converging lens: object beyond 2F</text>
<line x1="30" y1="170" x2="466" y2="170" stroke="#cbd2dd" stroke-width="1.5"/>
<path d="M280,78 Q301,170 280,262 Q259,170 280,78 z" fill="#dbe6fb" stroke="#2f5fd0" stroke-width="2"/>
<circle cx="190" cy="170" r="3.5" fill="#1f2937"/>
<circle cx="370" cy="170" r="3.5" fill="#1f2937"/>
<circle cx="100" cy="170" r="3" fill="#9aa4b4"/>
<circle cx="460" cy="170" r="3" fill="#9aa4b4"/>
<text x="190" y="190" text-anchor="middle" font-size="12" fill="#4a5262">F</text>
<text x="370" y="190" text-anchor="middle" font-size="12" fill="#4a5262">F′</text>
<text x="100" y="190" text-anchor="middle" font-size="12" fill="#9aa4b4">2F</text>
<text x="460" y="190" text-anchor="middle" font-size="12" fill="#9aa4b4">2F′</text>
<polyline points="70,124 280,124 437,204" fill="none" stroke="#2f5fd0" stroke-width="2"/>
<line x1="70" y1="124" x2="437" y2="204" stroke="#a8641a" stroke-width="2"/>
<polyline points="70,124 280,204 437,204" fill="none" stroke="#5b3fa8" stroke-width="2"/>
<line x1="70" y1="170" x2="70" y2="124" stroke="#b3352f" stroke-width="3" marker-end="url(#cl-r)"/>
<line x1="437" y1="170" x2="437" y2="204" stroke="#1f7a53" stroke-width="3" marker-end="url(#cl-g)"/>
<text x="64" y="118" text-anchor="end" font-size="12" font-weight="600" fill="#b3352f">object</text>
<text x="446" y="222" text-anchor="end" font-size="12" font-weight="600" fill="#1f7a53">image</text>
<text x="286" y="72" font-size="12" fill="#2f5fd0">converging lens</text>
</svg>
<figcaption><b>Three rays, one crossing point.</b> A ray parallel to the axis leaves through <b>F′</b>; a ray through the centre goes straight on; a ray through <b>F</b> emerges parallel. All three meet at the image, which is <b>real</b> (the rays genuinely converge there, so it can be projected on a screen) and <b>inverted</b>. Move the object inside <code>F</code> and the rays diverge instead — the image flips to virtual, upright and magnified, which is the magnifying glass.</figcaption>
</figure>
<div class="callout callout--key"><p><b>中文对照.</b> 凸透镜 converging lens, 凹透镜 diverging lens, 实像 real image, 虚像 virtual image, 焦点 focal point. 凸透镜物距大于焦距成倒立实像，小于焦距成正立虚像。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Do not assume a converging lens always makes a real image. Place the object inside the focal length (closer than <code>f</code>) and the image flips to virtual, upright and magnified — that is the magnifying glass. The "real vs virtual" outcome depends on where the object sits relative to <code>f</code>, not on the lens type alone (a diverging lens is always virtual, but a converging lens can be either).</p></div>`
    },

    {
      h: "The thin lens formula and magnification",
      body: `<p>For a thin lens the object distance <code>u</code>, image distance <code>v</code> and focal length <code>f</code> are linked by</p>
<div class="formula">1/u + 1/v = 1/f</div>
<p>and the linear magnification is the image height over the object height, equal to the ratio of distances:</p>
<div class="formula">m = v/u</div>
<p>Using the convention below, a negative <code>v</code> means a virtual image (same side as the object); a negative <code>m</code> means an inverted image.</p>
<h3>A sign convention that avoids pain</h3>
<p>For Round 0 the cleanest convention is: distances are positive if measured in the direction of the outgoing (image-side) light. With that rule a converging lens has <code>f &gt; 0</code>; a real image has <code>v &gt; 0</code>; a virtual image has <code>v &lt; 0</code>. The formula then works without extra case-switching.</p>
<h3>The ratios worth knowing cold (no calculator)</h3>
<table><thead><tr><th>Object position</th><th>Image position</th><th>Magnification</th><th>Image type</th></tr></thead><tbody>
<tr><td><code>u = 2f</code></td><td><code>v = 2f</code></td><td><code>m = −1</code></td><td>real, inverted, same size</td></tr>
<tr><td><code>u &gt; 2f</code></td><td><code>f &lt; v &lt; 2f</code></td><td><code>|m| &lt; 1</code></td><td>real, inverted, diminished</td></tr>
<tr><td><code>f &lt; u &lt; 2f</code></td><td><code>v &gt; 2f</code></td><td><code>|m| &gt; 1</code></td><td>real, inverted, magnified</td></tr>
<tr><td><code>u &lt; f</code></td><td><code>v &lt; 0</code></td><td><code>m &gt; 1</code> (upright)</td><td>virtual, upright, magnified</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>中文对照.</b> 薄透镜公式 thin lens formula, 放大率 magnification, 物距 object distance u, 像距 image distance v. <code>m = v/u</code>，负号表示倒立。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> The formula is <code>1/u + 1/v = 1/f</code>, <i>not</i> <code>u + v = f</code> and <i>not</i> <code>1/(u+v)</code>. Taking reciprocals is the step people skip. And when the object is inside the focal length, <code>v</code> comes out negative — that negative sign is the signal "virtual", not a mistake to throw away. Keep it; it is the answer.</p></div>`
    },

    {
      h: "Lens power, and the eye and camera qualitatively",
      body: `<p>The <b>power</b> of a lens measures how strongly it bends rays. It is the reciprocal of the focal length, in metres:</p>
<div class="formula">P = 1/f        (f in metres, P in dioptres, D)</div>
<p>A short-focal-length lens is powerful (large <code>P</code>); a long-focal-length lens is weak (small <code>P</code>). A converging lens has positive power; a diverging lens has negative power. Lenses placed in contact simply add their powers:</p>
<div class="formula">P_total = P₁ + P₂</div>
<p>This is why two weak lenses together can be treated as one lens of combined power — and why opticians prescribe a single number of dioptres.</p>
<h3>The eye</h3>
<p>The eye is a converging-lens system: the cornea and the flexible crystalline lens focus light onto the retina at the back. To see objects at different distances the ciliary muscles change the lens's curvature, altering its focal length — this is <b>accommodation</b>.</p>
<ul class="tight">
<li><b>Short sight (myopia):</b> the eye is too strong or too long, so distant objects focus in front of the retina. Corrected with a <b>diverging</b> lens.</li>
<li><b>Long sight (hyperopia):</b> the eye is too weak or too short, so near objects focus behind the retina. Corrected with a <b>converging</b> lens.</li>
</ul>
<h3>The camera</h3>
<p>A camera is the same idea with a fixed lens focusing onto a sensor or film; the aperture controls how much light enters, and focusing moves the lens to change <code>v</code> for the object distance <code>u</code>. Both the eye and the camera are single converging-lens imagers — the only difference is that the eye accommodates <code>f</code> while the camera moves <code>v</code>.</p>
<div class="callout callout--key"><p><b>中文对照.</b> 屈光度 power (dioptre), 眼睛 eye, 相机 camera, 视网膜 retina, 晶状体 crystalline lens, 近视 myopia, 远视 hyperopia, 调节 accommodation. 近视用凹透镜矫正，远视用凸透镜矫正。</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Power is <code>1/f</code> with <code>f</code> in <b>metres</b>. A focal length of 50 cm is <code>f = 0.50 m</code>, so <code>P = 2.0 D</code> — not 0.02 D (that would be using centimetres) and not 50 D (that would be using the number 50 directly). Watch the unit conversion; it is the only arithmetic step here.</p></div>`
    },

    {
      h: "Path difference and coherence",
      body: `<h3>Path difference</h3>
<p>If two waves travel different distances to the same point, the difference in those distances is the <b>path difference</b>. What matters is the path difference in wavelengths:</p>
<table><thead><tr><th>Path difference</th><th>Result</th></tr></thead><tbody>
<tr><td><code>nλ</code> (whole number of wavelengths)</td><td>constructive interference — a maximum</td></tr>
<tr><td><code>(n + ½)λ</code> (odd number of half-wavelengths)</td><td>destructive interference — a minimum</td></tr>
</tbody></table>
<h3>Coherence</h3>
<p>For a stable interference pattern, the two sources must be <b>coherent</b>: the same frequency, and a constant phase difference. Ordinary light sources are not coherent, because they emit in random bursts. This is why a single source is split into two paths — in Young's experiment by passing it through two slits, in a thin film by reflection from the front and back surfaces.</p>
<div class="callout callout--warn"><p><b>Why the fringes move if you use two separate lamps.</b> Two independent lamps have no fixed phase relationship, so the phase difference at any point changes randomly many times per second. The maxima and minima average out and no pattern is seen. This is the standard explanation question on this topic, and it is worth having ready.</p></div>
<div class="callout callout--key"><p><b>Path difference versus phase difference.</b> A path difference of one wavelength is a phase difference of <code>2π</code> (back in phase, constructive); half a wavelength is <code>π</code> (antiphase, destructive). The conversion is <code>Δφ = 2π × (path difference)/λ</code>. When a question gives you a path difference in metres, divide by <code>λ</code> first, then decide constructive or destructive from the remainder.</p></div>
<p>中文对照: 路程差 path difference, 相干 coherent, 相位差 phase difference. 路程差 nλ 相长，(n+½)λ 相消。</p>`
    },

    {
      h: "Young's double slit",
      body: `<p>Light passes through a single slit first to make it coherent, then through two narrow slits. The two sets of waves overlap and form a pattern of evenly spaced bright and dark fringes on a distant screen.</p>
<div class="formula">w = λD/s</div>
<p>where <code>w</code> is the fringe spacing — the distance between adjacent bright fringes — <code>λ</code> the wavelength, <code>D</code> the distance from the slits to the screen, and <code>s</code> the separation of the slits.</p>
<h3>Where it comes from</h3>
<p>For a point on the screen at angle <code>θ</code> from the centre, the path difference is <code>s sin θ</code>. Maxima occur when this is a whole number of wavelengths:</p>
<div class="formula">s sin θ = nλ</div>
<p>For small angles, <code>sin θ ≈ tan θ = x/D</code> where <code>x</code> is the distance from the centre of the pattern. So</p>
<div class="formula">s x/D = nλ   →   x = nλD/s</div>
<p>The spacing between consecutive maxima is therefore <code>λD/s</code> ✓. Notice that the small-angle approximation from module A is doing real work here — that is why BPhO supplies it.</p>
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="Geometry of Young's double slit experiment: two slits a distance s apart, a screen a distance D away, and the fringe spacing w marked on the screen.">
<text x="240" y="24" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">Young's double slit: where w = λD/s comes from</text>
<rect x="84" y="40" width="12" height="78" fill="#1f2937"/>
<rect x="84" y="122" width="12" height="56" fill="#1f2937"/>
<rect x="84" y="182" width="12" height="78" fill="#1f2937"/>
<text x="30" y="36" font-size="11.5" fill="#7b8494">double slit</text>
<rect x="344" y="40" width="9" height="220" fill="#e2e6ed" stroke="#cbd2dd" stroke-width="1"/>
<line x1="96" y1="150" x2="344" y2="150" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="5 5"/>
<line x1="90" y1="120" x2="340" y2="110" stroke="#2f5fd0" stroke-width="2"/>
<line x1="90" y1="180" x2="340" y2="110" stroke="#a8641a" stroke-width="2"/>
<line x1="90" y1="120" x2="106" y2="176" stroke="#5b3fa8" stroke-width="1.4" stroke-dasharray="4 4"/>
<line x1="90" y1="180" x2="106" y2="176" stroke="#5b3fa8" stroke-width="3.5"/>
<text x="114" y="196" font-size="11.5" fill="#5b3fa8">path difference = s sin θ</text>
<line x1="70" y1="120" x2="70" y2="180" stroke="#7b8494" stroke-width="1.5"/>
<line x1="64" y1="120" x2="76" y2="120" stroke="#7b8494" stroke-width="1.5"/>
<line x1="64" y1="180" x2="76" y2="180" stroke="#7b8494" stroke-width="1.5"/>
<text x="58" y="154" text-anchor="end" font-size="12" font-weight="600" fill="#4a5262">s</text>
<line x1="90" y1="272" x2="344" y2="272" stroke="#7b8494" stroke-width="1.5"/>
<line x1="90" y1="266" x2="90" y2="278" stroke="#7b8494" stroke-width="1.5"/>
<line x1="344" y1="266" x2="344" y2="278" stroke="#7b8494" stroke-width="1.5"/>
<text x="217" y="290" text-anchor="middle" font-size="12" fill="#4a5262">D</text>
<line x1="386" y1="110" x2="386" y2="150" stroke="#7b8494" stroke-width="1.5"/>
<line x1="380" y1="110" x2="392" y2="110" stroke="#7b8494" stroke-width="1.5"/>
<line x1="380" y1="150" x2="392" y2="150" stroke="#7b8494" stroke-width="1.5"/>
<text x="398" y="134" font-size="12" font-weight="600" fill="#4a5262">w</text>
<line x1="353" y1="150" x2="378" y2="150" stroke="#1f2937" stroke-width="5"/>
<line x1="353" y1="110" x2="378" y2="110" stroke="#1f2937" stroke-width="3.5"/>
<line x1="353" y1="190" x2="378" y2="190" stroke="#1f2937" stroke-width="3.5"/>
<line x1="353" y1="70" x2="378" y2="70" stroke="#9aa4b4" stroke-width="2.5"/>
<line x1="353" y1="230" x2="378" y2="230" stroke="#9aa4b4" stroke-width="2.5"/>
<text x="424" y="52" text-anchor="end" font-size="11.5" fill="#7b8494">screen</text>
</svg>
<figcaption><b>Maxima where the path difference is a whole number of wavelengths.</b> The two rays arrive at a screen point with path difference <code>s sin θ</code> (purple construction). Bright fringes sit at <code>s sin θ = nλ</code>. For the small angles involved, <code>sin θ ≈ x/D</code>, so consecutive maxima are separated by <code>w = λD/s</code>. <b>Read the graph as ratios:</b> finer slits or a farther screen widen the fringes; pushing the slits apart narrows them.</figcaption>
</figure>
<h3>How the pattern changes</h3>
<table><thead><tr><th>Change</th><th>Effect on fringe spacing</th></tr></thead><tbody>
<tr><td>Increase <code>λ</code> (red instead of blue)</td><td>spacing increases</td></tr>
<tr><td>Increase <code>D</code> (move screen further away)</td><td>spacing increases</td></tr>
<tr><td>Increase <code>s</code> (slits further apart)</td><td>spacing <b>decreases</b></td></tr>
<tr><td>Use white light</td><td>a white central fringe with coloured fringes either side</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The white-light case, which is sample question S4.</b> With white light, every wavelength gives its own pattern. All wavelengths give a maximum at the centre, so the central fringe is <b>white</b>. Away from the centre the different wavelengths peak at different places, so the fringes are coloured, with red — the longest wavelength — spread furthest. The pattern therefore has a white centre, then coloured fringes whose spacing increases towards the red.</p></div>
<div class="callout callout--key"><p><b>Why the small-angle approximation is safe.</b> Typical numbers: <code>D = 2 m</code>, <code>s = 0.5 mm</code>, so <code>x ≈ nλD/s</code>. For the first fringe with <code>λ = 600 nm</code>, <code>x ≈ 2.4 mm</code>, so <code>tan θ = x/D ≈ 0.0012</code> — far smaller than the ~0.1 where <code>sin θ ≈ tan θ</code> starts to fail. The approximation is not a fudge; it is exact to the precision the answer needs.</p></div>
<p>中文对照: 杨氏双缝 Young's double slit, 条纹间距 fringe spacing, 白光 white light. 中央条纹为白色，两侧呈彩色。</p>`
    },

    {
      h: "Single-slit diffraction",
      body: `<p>Pass light through a single narrow slit and it spreads out. The pattern is not a set of evenly spaced fringes but a broad <b>central maximum</b> flanked by much weaker secondary maxima.</p>
<p>For a slit of width <code>a</code>, the first minimum occurs at angle <code>θ</code> where</p>
<div class="formula">a sin θ = λ</div>
<p>So the angular width of the central maximum is approximately <code>2λ/a</code>.</p>
<h3>How the pattern changes</h3>
<table><thead><tr><th>Change</th><th>Effect on the central maximum</th></tr></thead><tbody>
<tr><td>Wider slit</td><td>narrower central maximum</td></tr>
<tr><td>Narrower slit</td><td>wider central maximum</td></tr>
<tr><td>Longer wavelength</td><td>wider central maximum</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The inverse relationship is the point.</b> Diffraction is <i>more</i> pronounced when the slit is <i>narrower</i> and comparable to the wavelength. A very wide slit diffracts hardly at all, which is why you do not see light bending around doorways. This counter-intuitive inverse dependence is the standard question, and it is the reason the marks are usually qualitative rather than numerical.</p></div>
<div class="callout callout--warn"><p><b>Do not confuse the two patterns.</b> A <b>double</b> slit gives many evenly spaced fringes of roughly equal brightness. A <b>single</b> slit gives one broad bright band with weak fringes either side. If a question shows you a pattern, the number of fringes and their relative brightness tell you immediately which experiment it came from.</p></div>
<div class="callout callout--key"><p><b>Combining with the double slit.</b> In a real double-slit setup each slit has finite width, so the overall pattern is the sharp double-slit fringes <i>enveloped</i> by the broader single-slit diffraction curve. The single-slit minima can actually wipe out some double-slit maxima — "missing orders". The inverse dependence <code>width ∝ λ/a</code> is the qualitative fact most often tested.</p></div>
<p>中文对照: 单缝衍射 single-slit diffraction, 中央极大 central maximum, 缺级 missing order. 缝越窄，衍射越显著。</p>`
    },

    {
      h: "The diffraction grating",
      body: `<p>A grating has many thousands of narrow, equally spaced slits. The maxima are in the same positions as for two slits, but they are far <b>sharper</b>, because contributions from many slits only reinforce when the path difference is exactly a whole number of wavelengths.</p>
<div class="formula">d sin θ = nλ</div>
<p>where <code>d</code> is the slit spacing — the distance from one slit to the next, not the width of a slit — and <code>n</code> is the order of the maximum, starting at zero for the straight-through direction.</p>
<h3>Finding d from the grating specification</h3>
<p>Gratings are usually specified in lines per millimetre. If a grating has <code>N</code> lines per millimetre, then</p>
<div class="formula">d = 1/N mm = (1/N) × 10⁻³ m</div>
<p>For example, 500 lines per millimetre gives <code>d = 1/500 mm = 2 × 10⁻⁶ m</code>. Getting this conversion right is the main arithmetic hurdle in grating questions.</p>
<h3>The maximum order</h3>
<p>Since <code>sin θ</code> cannot exceed 1, the largest possible order satisfies <code>n ≤ d/λ</code>. So a grating with <code>d = 2 × 10⁻⁶ m</code> and light of <code>λ = 500 nm = 5 × 10⁻⁷ m</code> can give orders up to <code>2 × 10⁻⁶/5 × 10⁻⁷ = 4</code>. So orders 0, 1, 2, 3 and 4 are visible — and a question asking "how many orders are visible" wants 5, not 4, because the zeroth order counts.</p>
<div class="callout callout--good"><p><b>Why gratings are used for spectroscopy.</b> The sharpness of the maxima means two very close wavelengths produce two clearly separated lines, whereas with a double slit they would overlap. That is the practical reason gratings are preferred in a spectrometer, and it is a common "why" question.</p></div>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Two conversions trip people up. First, <code>d</code> is the spacing between adjacent slits, found from lines per unit length — it is <b>not</b> the slit width. Second, keep units consistent: convert lines per mm to <code>d</code> in metres before using <code>d sin θ = nλ</code>. A grating of 500 lines/mm gives <code>d = 2 × 10⁻⁶ m</code>, not <code>2 × 10⁻³ m</code>. Also remember the zeroth order when counting visible orders.</p></div>
<p>中文对照: 衍射光栅 diffraction grating, 光栅常量 grating spacing d, 级次 order. 级次 n 满足 n ≤ d/λ。</p>`
    }
  ],

  examples: [
    {
      q: "<p>Light travels from glass of refractive index 1.50 into air. What is the critical angle? Take <code>sin 41.8° ≈ 0.667</code> and <code>sin 48.2° ≈ 0.745</code>.</p><p>A) 30.0° &nbsp; B) 41.8° &nbsp; C) 45.0° &nbsp; D) 48.2° &nbsp; E) 60.0°</p>",
      sol: `<p>Use <code>sin θ_c = n₂/n₁</code> with <code>n₂ = 1</code> for air and <code>n₁ = 1.50</code>:</p>
<div class="formula">sin θ_c = 1/1.50 = 0.667</div>
<p>So <code>θ_c ≈ 41.8°</code>.</p>
<p><b>Answer: B.</b></p>
<p><b>Why the answer must be less than 45°.</b> Notice that <code>1/1.5 = 2/3</code>, which is less than <code>sin 45° = 0.707</code>. Since sine increases with angle in this range, the critical angle must be less than 45°. That single observation eliminates C, D and E without any calculation, leaving only A or B. Then <code>2/3</code> against the given values picks B.</p>
<p><b>The traps.</b> Option D, 48.2°, is the critical angle for water (<code>sin θ_c = 1/1.33 = 0.752</code>) — a value worth knowing so you do not confuse the two. Option C, 45°, is the angle at which <code>sin θ = cos θ</code>, a tempting round number with no physical significance here.</p>
<p><b>The direction check.</b> Critical angle only exists for light going from the denser medium to the less dense one. Light going from air into glass has no critical angle at all — it simply refracts. If a question asks about light entering a medium, total internal reflection is not available.</p>`,
      tag: "Critical angle — the sample paper's shape"
    },
    {
      q: "<p>In a Young's double slit experiment the slits are 0.50 mm apart and the screen is 2.0 m away. Light of wavelength 600 nm is used. What is the fringe spacing?</p><p>A) 0.60 mm &nbsp; B) 1.2 mm &nbsp; C) 2.4 mm &nbsp; D) 4.8 mm &nbsp; E) 6.0 mm</p>",
      sol: `<p>Use <code>w = λD/s</code>, converting everything to metres:</p>
<div class="formula">λ = 600 nm = 6.0 × 10⁻⁷ m
s = 0.50 mm = 5.0 × 10⁻⁴ m
D = 2.0 m</div>
<div class="formula">w = (6.0 × 10⁻⁷ × 2.0) / (5.0 × 10⁻⁴)
  = (12 × 10⁻⁷) / (5.0 × 10⁻⁴)
  = 2.4 × 10⁻³ m = 2.4 mm</div>
<p><b>Answer: C.</b></p>
<p><b>The mental route.</b> Handle digits and powers separately. Digits: <code>6 × 2/5 = 2.4</code>. Powers: <code>10⁻⁷ × 10⁰/10⁻⁴ = 10⁻³</code>. So <code>2.4 × 10⁻³ m</code> ✓. Two separate streams, no long division.</p>
<p><b>The sanity check on the magnitude.</b> Fringe spacings in a real demonstration are of order a millimetre — visible to the naked eye on a screen a couple of metres away. An answer in micrometres or in centimetres would be wrong, and that check alone removes A and E.</p>
<p><b>The traps.</b> Option B, 1.2 mm, comes from using <code>λD/2s</code> — treating <code>w</code> as the distance from the centre to the first fringe rather than the distance between adjacent fringes. Option D, 4.8 mm, is exactly double, from inverting the slit separation. Both are structural errors rather than arithmetic ones, which is why identifying the formula first matters.</p>
<p><b>The change question worth being able to answer.</b> If the light were changed to 400 nm blue, the spacing would fall to <code>2.4 × 400/600 = 1.6 mm</code>. If the screen were moved to 3.0 m, the spacing would rise to <code>2.4 × 3/2 = 3.6 mm</code>. Both are pure ratio reasoning, and both take ten seconds.</p>`,
      tag: "Young's double slit — the sample paper's shape"
    },
    {
      q: "<p>A diffraction grating has 500 lines per millimetre. Monochromatic light of wavelength 500 nm is incident normally. What is the angle of the second-order maximum? Take <code>sin 30° = 0.50</code>.</p><p>A) 15° &nbsp; B) 30° &nbsp; C) 45° &nbsp; D) 60° &nbsp; E) 90°</p>",
      sol: `<p><b>Step 1 — the slit spacing.</b> 500 lines per millimetre means</p>
<div class="formula">d = 1/500 mm = 2.0 × 10⁻³ mm = 2.0 × 10⁻⁶ m</div>
<p><b>Step 2 — apply the grating equation</b> with <code>n = 2</code>:</p>
<div class="formula">d sin θ = nλ
2.0 × 10⁻⁶ × sin θ = 2 × 5.0 × 10⁻⁷
2.0 × 10⁻⁶ sin θ = 1.0 × 10⁻⁶
sin θ = 0.50</div>
<p>So <code>θ = 30°</code>.</p>
<p><b>Answer: B.</b></p>
<p><b>The trap.</b> Option A, 15°, is the <b>first-order</b> angle: with <code>n = 1</code> you get <code>sin θ = 0.25</code>, which is about 14.5°. Reading the order correctly is half the question. Note also that the second-order angle is not twice the first-order angle — <code>sin θ</code> doubles, not <code>θ</code>, which is exactly the kind of non-linearity the small-angle approximation would wrongly smooth over.</p>
<p><b>The maximum-order check, worth doing as a habit.</b> Since <code>sin θ ≤ 1</code>, we need <code>n ≤ d/λ = 2.0 × 10⁻⁶/5.0 × 10⁻⁷ = 4</code>. So orders 0, 1, 2, 3 and 4 are all visible, and the second order is comfortably within range. If the question had asked for the fifth order, the answer would be that it does not exist.</p>
<p><b>The conversion discipline.</b> The whole difficulty of this question is the lines-per-millimetre conversion. Write <code>d = 1/500 mm</code> explicitly and then convert to metres in a separate step, rather than trying to do both at once. That is where nearly all the lost marks are.</p>`,
      tag: "Diffraction grating — the order and the spacing"
    },
    {
      q: "<p>In a Young's double slit experiment, the whole apparatus is immersed in water of refractive index 1.33. What happens to the fringe spacing?</p><p>A) It increases by a factor of 1.33 &nbsp; B) It is unchanged &nbsp; C) It decreases by a factor of 1.33 &nbsp; D) It decreases by a factor of 1.77 &nbsp; E) It increases by a factor of 1.77</p>",
      sol: `<p>The fringe spacing is <code>w = λD/s</code>. Immersing the apparatus changes the wavelength of the light but not <code>D</code> or <code>s</code>.</p>
<p>In water, the speed of light falls to <code>c/1.33</code>. The frequency is set by the source and cannot change, so from <code>v = fλ</code> the wavelength must fall by the same factor:</p>
<div class="formula">λ_water = λ_air/1.33</div>
<p>So the fringe spacing falls by a factor of 1.33.</p>
<p><b>Answer: C.</b></p>
<p><b>Why the frequency cannot change.</b> This is the key step and it is worth stating explicitly. The frequency is determined by the source; the medium cannot create or destroy oscillations. So if the speed falls, the wavelength must fall with it. That is the same reasoning as for any wave crossing a boundary, and it is the reason <code>n = c/c_s</code> can be written as <code>n = λ_air/λ_medium</code>.</p>
<p><b>The trap.</b> Option A is the answer you get by reasoning that water has a higher refractive index and therefore "more refraction", so the fringes should spread. The opposite is true. Option D, a factor of 1.77, comes from using <code>1.33²</code>, which has no basis here.</p>
<p><b>The physical reading.</b> Shorter wavelength means the waves are more tightly packed, so the maxima occur at smaller angles and the pattern is compressed. The fringes get closer together, and the pattern becomes harder to resolve. That is a real experimental effect and it is why interferometry is easier in air than in a liquid.</p>`,
      tag: "Wavelength in a medium — frequency does not change"
    },

    {
      q: "<p>Light in air (refractive index 1.00) strikes a glass surface (refractive index 1.50) at an angle of incidence of 30° to the normal. What is the angle of refraction? Use <code>sin 30° = 0.50</code> and <code>sin 19.5° ≈ 0.33</code>.</p><p>A) 19.5° &nbsp; B) 30° &nbsp; C) 35° &nbsp; D) 42° &nbsp; E) 60°</p>",
      sol: `<p>Snell's law, with the ray going from air into the denser glass:</p>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂
1.00 × sin 30° = 1.50 × sin θ₂
sin θ₂ = 0.50 / 1.50 = 1/3 ≈ 0.333</div>
<p>From the value given, <code>sin 19.5° ≈ 0.33</code>, so <code>θ₂ ≈ 19.5°</code>.</p>
<p><b>Answer: A.</b></p>
<p><b>The no-calculator reasoning.</b> Going into a denser medium, the ray bends <i>towards</i> the normal, so the refracted angle must be <b>less</b> than the incident 30°. That eliminates C, D and E immediately. Between A (19.5°) and B (30°, unchanged), bending towards the normal means the angle must shrink, so A. The arithmetic only confirmed what the direction rule already told you.</p>
<p><b>The traps.</b> B is "no refraction at all" — the answer if you forget Snell entirely. D, 42°, is the critical angle of this glass (<code>sin θ_c = 1/1.5</code>), a value worth knowing so you do not confuse it with a refraction angle. E, 60°, is what you get by inverting the ratio: <code>sin θ₂ = 1.5 × 0.5</code> — using <code>n₁/n₂</code> the wrong way round.</p>`,
      tag: "Snell's law — ratio, no calculator"
    },

    {
      q: "<p>A converging lens of focal length <code>f</code> forms an image of an object placed at distance <code>2f</code>. The object is then moved to distance <code>3f</code>. By what factor does the magnification change?</p><p>A) it doubles &nbsp; B) it halves &nbsp; C) it is unchanged &nbsp; D) it becomes one third &nbsp; E) it becomes two thirds</p>",
      sol: `<p>Use the lens formula <code>1/u + 1/v = 1/f</code> and <code>m = v/u</code>. First case, <code>u = 2f</code>:</p>
<div class="formula">1/v = 1/f − 1/(2f) = 1/(2f)   →   v = 2f
m₁ = v/u = 2f / 2f = 1</div>
<p>Second case, <code>u = 3f</code>:</p>
<div class="formula">1/v = 1/f − 1/(3f) = 2/(3f)   →   v = 3f/2
m₂ = v/u = (3f/2) / (3f) = 1/2</div>
<p>So the magnification changes from 1 to <code>1/2</code> — it halves.</p>
<p><b>Answer: B, it halves.</b></p>
<p><b>The ratio route, which is faster.</b> The image distance at <code>u = 2f</code> is <code>2f</code> (a fact worth knowing: object at 2f gives an image at 2f, same size). At <code>u = 3f</code> the image is between <code>f</code> and <code>2f</code>; computing gives <code>v = 1.5f</code>. Then <code>m₂/m₁ = (1.5f/3f) / (2f/2f) = 0.5/1 = ½</code>. No full reciprocal algebra needed if you know the <code>u = 2f</code> special case.</p>
<p><b>The traps.</b> D, "one third", comes from confusing the magnification with the object-distance ratio <code>f/3f = 1/3</code>. E, "two thirds", is the ratio <code>v₂/v₁ = (1.5f)/(2f) = 3/4</code> — wrong quantity again. Both distractors use a real ratio from the problem but apply it to the wrong thing, which is the standard lens-formula trap.</p>`,
      tag: "Lens formula — magnification ratio"
    },

    {
      q: "<p>The speed of light in a certain transparent medium is measured to be <code>2.0 × 10⁸ m s⁻¹</code>. The speed of light in a vacuum is <code>3.0 × 10⁸ m s⁻¹</code>. What is the refractive index of the medium?</p><p>A) 0.67 &nbsp; B) 1.5 &nbsp; C) 1.33 &nbsp; D) 2.0 &nbsp; E) 3.0</p>",
      sol: `<p>The refractive index is the ratio of the speed in a vacuum to the speed in the medium:</p>
<div class="formula">n = c / c_s = (3.0 × 10⁸) / (2.0 × 10⁸) = 3.0 / 2.0 = 1.5</div>
<p><b>Answer: B, 1.5.</b></p>
<p><b>The no-calculator check.</b> The medium is slower than vacuum (as every medium must be), so <code>n</code> must be <b>greater than 1</b>. That alone eliminates A (0.67), which is the reciprocal <code>c_s/c</code> — the single most common slip, because it is tempting to divide the smaller number by the larger. Options C (1.33, water), D (2.0) and E (3.0) are all physically possible indices but do not match the given speeds; only B does.</p>
<p><b>The conceptual link.</b> Since <code>n = c/c_s</code> and the frequency cannot change across a boundary, this is also <code>n = λ_vacuum / λ_medium</code>. A refractive index of 1.5 means the wavelength inside the medium is two-thirds of its vacuum value — which is exactly why the fringe spacing in Young's experiment shrinks when immersed in liquid (see the existing example on that topic).</p>`,
      tag: "Refractive index from speed"
    }
  ],

  traps: [
    "Measuring angles from the surface instead of from the normal. Snell's law needs angles from the normal.",
    "Applying total internal reflection in the wrong direction. It requires travel from denser to less dense.",
    "Forgetting the prism geometry step <code>r₁ + r₂ = A</code>, which is needed to get from the first face to the second.",
    "Using <code>w = λD/2s</code> for fringe spacing, which gives the distance to the first fringe rather than between adjacent fringes.",
    "Forgetting to convert lines per millimetre to a slit spacing in metres for a diffraction grating.",
    "Assuming the second-order angle is twice the first-order angle. It is <code>sin θ</code> that doubles, not <code>θ</code>.",
    "Thinking the wavelength of light is unchanged in a medium. The frequency is unchanged; the wavelength is not.",
    "Confusing a single-slit pattern (one broad maximum with weak fringes) with a double-slit pattern (many evenly spaced fringes)."
  ],

  checklist: [
    { id: "G1", flag: "CORE", text: "Refractive index <code>n = c/c_s</code>; <code>n</code> of air is 1; which way a ray bends entering a denser medium." },
    { id: "G2", flag: "CORE", text: "Snell's law <code>n₁ sin θ₁ = n₂ sin θ₂</code>, with angles measured from the normal." },
    { id: "G3", flag: "CORE", text: "Total internal reflection and the critical angle <code>sin θ_c = n₂/n₁</code>, including the two conditions required." },
    { id: "G4", flag: "R1-ONLY", text: "Refractive index of a mixture of two liquids. Round 1 material — insurance only." },
    { id: "G5", flag: "NEW", text: "Prisms: refraction through two faces, the geometry <code>r₁ + r₂ = A</code>, and the range of incident angles for emergence." },
    { id: "G6", flag: "NEW", text: "Optical fibres: step index, cladding, modal and material dispersion, pulse broadening, and absorption." },
    { id: "G7", flag: "CORE", text: "Path difference and coherence; why two independent lamps give no stable pattern." },
    { id: "G8", flag: "CORE", text: "Young's double slit: <code>w = λD/s</code>, how the pattern changes with each variable, and the white-light case." },
    { id: "G9", flag: "CORE", text: "Single-slit diffraction: the central maximum width varying inversely with slit width, qualitatively." },
    { id: "G10", flag: "CORE", text: "The diffraction grating <code>d sin θ = nλ</code>, converting lines per millimetre to <code>d</code>, and the maximum visible order." },
    { id: "G11", flag: "R1-ONLY", text: "Resolving power and telescope aperture. Round 1 material — insurance only." },
    { id: "G12", flag: "R1-ONLY", text: "Radiation pressure and the force exerted by light. Round 1 material — insurance only." },
    { id: "G13", flag: "R1-ONLY", text: "Multiple reflections between mirrors and the geometric series of intensities. Round 1 material — insurance only." }
  ]
}

]);
