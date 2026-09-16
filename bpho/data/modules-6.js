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
<div class="callout callout--key"><p><b>The frequency fact worth stating explicitly.</b> When a wave crosses a boundary into a different medium, its <b>speed and wavelength change but its frequency does not</b>. The frequency is set by the source. So <code>v = fλ</code> at the boundary gives <code>v₁/λ₁ = v₂/λ₂</code>. This is the basis of refraction and it is worth knowing as a sentence.</p></div>`
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
<p>Visible light spans roughly 400 nm (violet) to 700 nm (red). Remembering that visible wavelengths are of order <code>10⁻⁷ m</code> is useful for the photon-energy estimates in module L.</p>`
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
</tbody></table>`
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
<p>where <code>T</code> is the tension and <code>μ</code> the mass per unit length. This is the equation a guitar tuner uses: tightening the string increases <code>T</code>, which raises the frequency. Note the square root — doubling the tension raises the pitch by only a factor of <code>√2</code>.</p>`
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
<p>In reality an antinode sits slightly beyond the open end, so the effective length is a little longer than the physical length. Competition questions sometimes mention this; if they do, add the correction to <code>L</code> before using the formulas.</p>`
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
<p>The choice of <code>sin</code> or <code>cos</code> only shifts the wave along, so it corresponds to a different starting point. It does not change <code>A</code>, <code>ω</code>, <code>k</code> or <code>v</code> at all. Do not be distracted by it.</p>`
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
<p>Note how different 200 and 12 are. That gap is exactly what the wrong options exploit.</p>`
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
<div class="callout callout--warn"><p><b>Kelvin, not Celsius.</b> <code>v ∝ √T</code> requires absolute temperature. Sound travels at about 340 m s⁻¹ at 20 °C, which is 293 K. A question that gives you a Celsius temperature and asks about a speed ratio requires conversion first — and forgetting that is the standard error.</p></div>`
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
<p>So if the amplitude doubles, the intensity quadruples. This is worth connecting to the inverse-square law: from <code>I ∝ 1/r²</code> and <code>I ∝ A²</code>, the amplitude must fall as <code>1/r</code>. Both statements are true and they are consistent, which is a satisfying check.</p>`
    }
  ],

  examples: [
    {
      q: "<p>A string of length 0.80 m is fixed at both ends and vibrates in its third harmonic. What is the wavelength?</p><p>A) 0.27 m &nbsp; B) 0.40 m &nbsp; C) 0.53 m &nbsp; D) 0.80 m &nbsp; E) 2.4 m</p>",
      sol: `<p>Use <code>L = nλ/2</code> with <code>n = 3</code>:</p>
<div class="formula">0.80 = 3λ/2   →   λ = 2 × 0.80/3 = 1.60/3 ≈ 0.53 m</div>
<p><b>Answer: C.</b></p>
<p><b>The picture, which is faster than the formula.</b> In the third harmonic there are three antinodes and four nodes. The four nodes divide the string into three equal segments, each of which is half a wavelength. So each segment is <code>0.80/3 = 0.267 m</code>, and the wavelength is twice that, <code>0.533 m</code> ✓. Sketching the harmonic and counting segments is more reliable than recalling the formula under pressure.</p>
<p><b>The traps.</b> Option A, 0.27 m, is the segment length — half a wavelength — which is the quantity you compute first and then forget to double. Option B, 0.40 m, is the second harmonic's wavelength, and option D, 0.80 m, is the fundamental's. All three are the wavelengths of other harmonics, which is what makes this a good discrimination question.</p>
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
      h: "Refractive index and Snell's law",
      body: `<p>The refractive index of a medium is the ratio of the speed of light in a vacuum to its speed in the medium:</p>
<div class="formula">n = c/c_s</div>
<p>Since light travels fastest in a vacuum, <code>n ≥ 1</code> always. For air, <code>n ≈ 1.00</code> to three significant figures, so air is usually treated as vacuum. For water <code>n = 1.33</code>; for glass it is typically 1.5 to 1.6.</p>
<h3>Snell's law</h3>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂</div>
<p>where <code>θ₁</code> and <code>θ₂</code> are measured from the <b>normal</b>, not from the surface. This is the most common error in the topic: an angle measured from the surface must be converted to an angle from the normal before use.</p>
<div class="callout callout--key"><p><b>What refraction actually is, physically.</b> The frequency is set by the source and cannot change. When light enters a denser medium its speed falls, so <code>λ = v/f</code> falls too. The change of direction is the consequence of the wavefronts bending as one part of the wave slows before the other — exactly like a marching band turning when one flank slows down. That analogy is worth being able to give.</p></div>
<h3>Which way does the ray bend?</h3>
<p>Into a denser medium (<code>n</code> increases), the ray bends <b>towards</b> the normal. Into a less dense medium, it bends <b>away</b> from the normal. A quick check: from air into glass, the ray bends towards the normal, and the angle from the normal decreases.</p>`
    },

    {
      h: "Total internal reflection",
      body: `<p>When light travels from a denser medium to a less dense one, it bends away from the normal. As the angle of incidence increases, the angle of refraction increases faster, and eventually reaches 90° — the refracted ray runs along the surface. Beyond that angle, no light refracts out at all, and all of it reflects back inside. That is <b>total internal reflection</b>.</p>
<p>The angle at which refraction reaches 90° is the <b>critical angle</b>. Setting <code>θ₂ = 90°</code> in Snell's law, so that <code>sin θ₂ = 1</code>:</p>
<div class="formula">n₁ sin θ_c = n₂ × 1        so   sin θ_c = n₂/n₁</div>
<p>When the second medium is air, <code>n₂ ≈ 1</code>, and this simplifies to the form most often used:</p>
<div class="formula">sin θ_c = 1/n</div>
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
<p>Diamond's very small critical angle is why it sparkles: light entering it is reflected internally many times before emerging, so a great deal of light is directed back out towards the viewer.</p>`
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
<p>Because <code>n</code> varies slightly with wavelength — larger for violet, smaller for red — the prism spreads white light into a spectrum. The violet end is deviated more. This is <b>dispersion</b>, and it is the same phenomenon that causes rainbows.</p>`
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
<div class="callout callout--key"><p><b>Why pulse broadening matters.</b> A digital signal is a sequence of pulses. If each pulse spreads out in time, it starts to overlap with its neighbours and the receiver can no longer tell a 1 from a 0. That is why dispersion limits both the maximum length of a fibre link and the maximum data rate. Stating the consequence, not just the mechanism, is what earns the mark.</p></div>`
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
<div class="callout callout--warn"><p><b>Why the fringes move if you use two separate lamps.</b> Two independent lamps have no fixed phase relationship, so the phase difference at any point changes randomly many times per second. The maxima and minima average out and no pattern is seen. This is the standard explanation question on this topic, and it is worth having ready.</p></div>`
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
<h3>How the pattern changes</h3>
<table><thead><tr><th>Change</th><th>Effect on fringe spacing</th></tr></thead><tbody>
<tr><td>Increase <code>λ</code> (red instead of blue)</td><td>spacing increases</td></tr>
<tr><td>Increase <code>D</code> (move screen further away)</td><td>spacing increases</td></tr>
<tr><td>Increase <code>s</code> (slits further apart)</td><td>spacing <b>decreases</b></td></tr>
<tr><td>Use white light</td><td>a white central fringe with coloured fringes either side</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The white-light case, which is sample question S4.</b> With white light, every wavelength gives its own pattern. All wavelengths give a maximum at the centre, so the central fringe is <b>white</b>. Away from the centre the different wavelengths peak at different places, so the fringes are coloured, with red — the longest wavelength — spread furthest. The pattern therefore has a white centre, then coloured fringes whose spacing increases towards the red.</p></div>`
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
<div class="callout callout--warn"><p><b>Do not confuse the two patterns.</b> A <b>double</b> slit gives many evenly spaced fringes of roughly equal brightness. A <b>single</b> slit gives one broad bright band with weak fringes either side. If a question shows you a pattern, the number of fringes and their relative brightness tell you immediately which experiment it came from.</p></div>`
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
<div class="callout callout--good"><p><b>Why gratings are used for spectroscopy.</b> The sharpness of the maxima means two very close wavelengths produce two clearly separated lines, whereas with a double slit they would overlap. That is the practical reason gratings are preferred in a spectrometer, and it is a common "why" question.</p></div>`
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
