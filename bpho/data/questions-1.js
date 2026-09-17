/* BPhO Round 0 — question bank, part 1 of 2.
   Modules A–G. Round 0 format: five options, no calculator, one mark each, no negative marking.
   Each question has a full worked solution and a note on where the wrong options come from. */

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([

/* ===================== MODULE A — toolkit ===================== */

{
  id: "A-01", module: "A", topic: "Base units", diff: 1,
  q: "Which of the following gives the watt in SI base units?",
  opts: ["kg m s⁻³", "kg m² s⁻²", "kg m² s⁻³", "kg m⁻¹ s⁻²", "kg² m² s⁻³"],
  ans: 2,
  sol: `<p>A watt is a joule per second. Work through it from the definitions.</p>
<div class="formula">J = N m = (kg m s⁻²) × m = kg m² s⁻²
W = J/s = kg m² s⁻² / s = kg m² s⁻³</div>
<p><b>Answer: C.</b></p>
<p><b>The distractors.</b> Option B, <code>kg m² s⁻²</code>, is the joule — the answer you get by forgetting to divide by time. Option D, <code>kg m⁻¹ s⁻²</code>, is the pascal. Option A has the exponent on <code>s</code> wrong by one, which is what happens if you treat a joule as <code>s⁻²</code> rather than <code>s⁻³</code> after dividing by time.</p>
<p><b>The fast route.</b> Power is <code>P = Fv</code>, so the units are <code>N × m s⁻¹ = kg m s⁻² × m s⁻¹ = kg m² s⁻³</code>. Two steps instead of three, and it uses a form of the power equation you already know.</p>`,
  trap: "Reporting the joule when the question asks for the watt. Always check whether a division by time is needed."
},
{
  id: "A-02", module: "A", topic: "Base units", diff: 1,
  q: "Which of the following gives the pascal in SI base units?",
  opts: ["kg m⁻¹ s⁻³", "kg m² s⁻²", "kg m⁻¹ s⁻²", "kg m s⁻²", "kg² m⁻¹ s⁻²"],
  ans: 2,
  sol: `<p>Pressure is force per unit area:</p>
<div class="formula">Pa = N/m² = (kg m s⁻²)/m² = kg m⁻¹ s⁻²</div>
<p><b>Answer: C.</b></p>
<p><b>The distractors, diagnosed.</b> Option B is the joule, option D is the newton, and option A has the exponent on <code>s</code> wrong by one — the error you make by forgetting that the newton already contains <code>s⁻²</code>.</p>
<p><b>Why the negative exponent on length matters.</b> Dividing by <code>m²</code> reduces the power of length by two, from <code>m¹</code> to <code>m⁻¹</code>. Writing the division out explicitly rather than doing it in your head is the safest way to avoid a slip.</p>
<p><b>A useful cross-check.</b> Energy density is also a pressure: <code>J/m³ = kg m² s⁻²/m³ = kg m⁻¹ s⁻²</code> ✓. Two different routes to the same base units is a good confirmation.</p>`,
  trap: "Losing track of the negative power of length that comes from dividing by area."
},
{
  id: "A-03", module: "A", topic: "Dimensional analysis", diff: 2,
  q: "A mass <code>m</code> on a spring of stiffness <code>k</code> oscillates. Which of the following has the dimensions of frequency?",
  opts: ["√(km)", "√(m/k)", "k/m", "√(k/m)", "m/k"],
  ans: 3,
  sol: `<p>A frequency has dimensions of <code>T⁻¹</code>. Work out the dimensions of each option and see which matches.</p>
<p>The stiffness <code>k</code> comes from <code>F = kx</code>, so <code>k = F/x</code>, giving dimensions <code>(kg m s⁻²)/m = kg s⁻²</code>. So:</p>
<div class="formula">√(k/m) = √(kg s⁻² / kg) = √(s⁻²) = s⁻¹ ✓</div>
<p><b>Answer: D.</b></p>
<p><b>Why the others fail.</b> Option B, <code>√(m/k)</code>, is <code>√(s²) = s</code> — a time, not a frequency, so it is the reciprocal of what is wanted. Option C, <code>k/m</code>, is <code>s⁻²</code>, which is a frequency squared. Option A, <code>√(km)</code>, is <code>√(kg² s⁻²) = kg s⁻¹</code>, which still carries a mass. Option E, <code>m/k</code>, is <code>s²</code>.</p>
<p><b>What dimensional analysis cannot tell you.</b> The exact result is <code>f = (1/2π)√(k/m)</code>. The method gives the form but never the dimensionless constant, and the <code>2π</code> has to come from the physics. If a question offers both <code>√(k/m)</code> and <code>(1/2π)√(k/m)</code>, dimensions alone cannot separate them.</p>
<p><b>The general lesson.</b> When you need a frequency and the only quantities available are a mass and a stiffness, the answer must involve <code>√(k/m)</code> — there is no other way to get rid of the mass and leave a <code>s⁻¹</code>. That reasoning takes fifteen seconds.</p>`,
  trap: "Confusing a period with a frequency. They are reciprocals, and both options are usually present."
},
{
  id: "A-04", module: "A", topic: "Dimensional consistency", diff: 2,
  q: "In the following, <code>s</code> is a distance, <code>v</code> a speed, <code>a</code> an acceleration and <code>t</code> a time. Which equation <b>cannot</b> be correct?",
  opts: ["v = s/t", "a = s/t", "a = v/t", "v² = 2as", "s = ½at²"],
  ans: 1,
  sol: `<p>Check the dimensions of each option, remembering that every additive term must match.</p>
<table><thead><tr><th>Option</th><th>Right-hand side</th><th>Needed</th><th>Verdict</th></tr></thead><tbody>
<tr><td>B: <code>a = s/t</code></td><td><code>m/s = m s⁻¹</code></td><td><code>m s⁻²</code></td><td><b>fails</b></td></tr>
<tr><td>A: <code>v = s/t</code></td><td><code>m s⁻¹</code></td><td><code>m s⁻¹</code></td><td>ok</td></tr>
<tr><td>C: <code>a = v/t</code></td><td><code>m s⁻¹/s = m s⁻²</code></td><td><code>m s⁻²</code></td><td>ok</td></tr>
<tr><td>D: <code>v² = 2as</code></td><td><code>m s⁻² × m = m² s⁻²</code></td><td><code>m² s⁻²</code></td><td>ok</td></tr>
<tr><td>E: <code>s = ½at²</code></td><td><code>m s⁻² × s² = m</code></td><td><code>m</code></td><td>ok</td></tr>
</tbody></table>
<p><b>Answer: B.</b> <code>s/t</code> is a speed, not an acceleration, so option B cannot be correct.</p>
<p><b>Why the question is easy once you have the habit.</b> Notice that B and C together show the pattern: dividing a speed by a time gives an acceleration, but dividing a distance by a time gives only a speed. One extra division by time is needed, and option B omits it.</p>
<p><b>The important caveat.</b> Dimensional consistency does not <i>prove</i> an equation is right — a wrong equation can still balance, for instance <code>v = 3s/t</code>. What it does is prove an equation is <i>wrong</i> when it fails. That asymmetry is what makes it a useful filter on a multiple-choice paper.</p>`,
  trap: "Trying to verify the correct equations instead of hunting for the one that fails. Look for the mismatch."
},
{
  id: "A-05", module: "A", topic: "Ratio reasoning", diff: 1,
  q: "A car brakes to rest from speed <code>v</code> in distance <code>d</code>. With the same braking force and mass, what is the braking distance from speed <code>2v</code>?",
  opts: ["d/2", "2d", "d", "8d", "4d"],
  ans: 4,
  sol: `<p>Set the work done by the braking force equal to the kinetic energy removed:</p>
<div class="formula">Fd = ½mv²   →   d = mv²/(2F)</div>
<p>Everything except <code>v</code> is unchanged, so <code>d ∝ v²</code>. Doubling the speed multiplies the distance by four.</p>
<p><b>Answer: E, 4d.</b></p>
<p><b>Why the answer is 4 and not 2.</b> Braking distance depends on the <i>square</i> of the speed, because the energy to be removed is <code>½mv²</code>. This is why speed limits matter so much more than they appear to: going from 30 to 60 km/h quadruples the braking distance, not doubles it.</p>
<p><b>The trap.</b> Option B, 2d, is the linear guess and is the most common wrong answer. If you catch yourself reasoning "twice the speed, twice the distance", stop and ask what quantity is conserved — it is energy, and energy goes as the square of speed.</p>
<p><b>The technique being tested.</b> Notice that the mass and the force never needed values, and neither did <code>v</code>. This is pure ratio reasoning: write the relationship, identify what is constant, and take the ratio. Fifteen seconds, no calculator.</p>`,
  trap: "Treating a quadratic relationship as linear. Energy goes as v², so distances and heights do too."
},
{
  id: "A-06", module: "A", topic: "Small-parameter approximations", diff: 2,
  q: "Use the binomial approximation to estimate <code>(1.01)¹⁰</code>.",
  opts: ["1.20", "1.01", "1.10", "1.00", "2.00"],
  ans: 2,
  sol: `<p>Apply <code>(1 + x)ⁿ ≈ 1 + nx</code> with <code>x = 0.01</code> and <code>n = 10</code>:</p>
<div class="formula">(1.01)¹⁰ ≈ 1 + 10 × 0.01 = 1.10</div>
<p><b>Answer: C.</b></p>
<p><b>How accurate is that?</b> The exact value is 1.1046, so the approximation is good to about 0.4%. The error is second order in <code>x</code>, so it is small precisely because <code>x</code> is small — which is the condition for the approximation to be valid.</p>
<p><b>Why this matters on a no-calculator paper.</b> You could not compute <code>(1.01)¹⁰</code> by hand in reasonable time. The approximation turns it into one multiplication. BPhO supplies these approximations on its constant sheet precisely because it expects you to use them.</p>
<p><b>The trap.</b> Option B, 1.01, is the answer you get by ignoring the exponent <code>n</code> entirely — applying the approximation as if <code>n = 1</code>. Option A, 1.20, is what you get from <code>1 + nx</code> with <code>n = 20</code>, or from a slip in reading the exponent.</p>
<p><b>The related forms worth knowing.</b> <code>1/(1 + x)ⁿ ≈ 1 − nx</code>, and <code>eˣ ≈ 1 + x</code>. All three come from the same idea: when a small quantity is raised to a power, only the first-order term matters.</p>`,
  trap: "Forgetting the exponent n and applying the approximation as if it were (1+x)."
},
{
  id: "A-07", module: "A", topic: "Geometric approximation", diff: 2,
  q: "Two points are 2.0 m apart. A point <code>d = 0.10 m</code> from the midpoint is joined to one of them. By how much does this distance exceed 1.0 m?",
  opts: ["0.050 m", "0.005 m", "0.100 m", "0.0005 m", "0.010 m"],
  ans: 1,
  sol: `<p>The geometry is a right triangle with legs <code>a = 1.0 m</code> and <code>d = 0.10 m</code>, so the hypotenuse is <code>√(a² + d²)</code>. Use the approximation</p>
<div class="formula">√(a² + d²) − a ≈ d²/(2a) = 0.01/2.0 = 0.005 m</div>
<p><b>Answer: B, 0.005 m.</b></p>
<p><b>Confirm it directly.</b> <code>√(1.0² + 0.10²) = √1.01 = 1.00499</code>, so the excess is 0.00499 m ≈ 0.005 m ✓. The approximation is accurate to better than 0.2% here.</p>
<p><b>Where the approximation comes from.</b> Factor out <code>a</code> and expand: <code>a(1 + d²/a²)^(1/2) ≈ a(1 + d²/2a²) = a + d²/2a</code>. It is the binomial approximation applied to a geometric quantity, and being able to rebuild it means you never need to memorise it.</p>
<p><b>The traps.</b> Option C, 0.100 m, is <code>d</code> itself — the error of assuming the hypotenuse grows linearly with the displacement. Option E, 0.010 m, is <code>d²/a</code>, missing the factor of 2. Both are the kind of error that comes from not deriving the result.</p>
<p><b>The physical significance.</b> The excess is <b>second order</b> in <code>d</code>, not first order. That is why a mass hanging on a taut string barely moves vertically when you push it sideways: the string has almost no slack. This fact is the basis of the small-oscillation analysis of a pendulum.</p>`,
  trap: "Assuming a distance grows linearly with a small displacement. It grows quadratically."
},
{
  id: "A-08", module: "A", topic: "Order of magnitude", diff: 1,
  q: "Which is the best estimate of the mass of an adult human, in kilograms?",
  opts: ["10⁴", "10¹", "10³", "10⁰", "10²"],
  ans: 4,
  sol: `<p>An adult human has a mass of roughly 70 kg. In powers of ten, that is <code>7 × 10¹</code>, which is nearest to <code>10²</code>.</p>
<p><b>Answer: E.</b></p>
<p><b>The subtlety worth noting.</b> Strictly, 70 kg is nearer to <code>10²</code> on a logarithmic scale, because <code>10¹ = 10</code> and <code>10² = 100</code>, and 70 is much closer to 100 than to 10. If the options had included <code>10¹·⁵ ≈ 30</code>, the choice would be harder — but with only powers of ten available, <code>10²</code> is correct.</p>
<p><b>Why order-of-magnitude questions appear.</b> On a no-calculator paper, a question whose options span several powers of ten is answerable by estimation alone. The skill is to have a bank of familiar magnitudes: a human 10² kg, a car 10³ kg, a room 10² m³, the Earth 10²⁴ kg.</p>
<p><b>The traps.</b> Option B, 10¹ kg, would be a large dog or a small child. Option C, 10³ kg, is a small car. Option A, 10⁴ kg, is a large truck. Each is a plausible-sounding magnitude for a different object, which is what makes the question discriminate.</p>
<p><b>Anchors worth memorising.</b> Density of water 10³ kg m⁻³; atmospheric pressure 10⁵ Pa; the Earth's radius 6.4 × 10⁶ m; a day 10⁵ s. These five cover a surprising number of estimation questions.</p>`,
  trap: "Confusing the mass of a human with the mass of a car or a small child. Keep a few anchors."
},
{
  id: "A-09", module: "A", topic: "Graph shape", diff: 2,
  q: "A ball is released from rest in air and falls, experiencing air resistance. Which best describes the graph of its velocity against time?",
  opts: ["A curve rising from the origin with increasing gradient", "A straight line through the origin", "A curve rising from the origin with decreasing gradient, approaching a horizontal line", "A horizontal straight line", "A curve falling from a maximum value to zero"],
  ans: 2,
  sol: `<p>At the instant of release the velocity is zero, so the graph must start at the origin. That eliminates option D immediately.</p>
<p>Initially there is no air resistance, so the acceleration is <code>g</code> and the gradient is at its steepest. As the ball speeds up, the drag force grows, so the resultant force falls and the acceleration decreases. The gradient therefore <b>decreases</b> with time.</p>
<p>Eventually drag balances weight, the acceleration reaches zero, and the velocity becomes constant. The curve approaches a horizontal asymptote — the terminal velocity.</p>
<p><b>Answer: C.</b></p>
<p><b>Why the answer must have a decreasing gradient.</b> The only mechanism available is drag, and drag always opposes motion and grows with speed. So the acceleration can only decrease, never increase. That rules out option A on physical grounds alone, without any analysis.</p>
<p><b>The traps.</b> Option B is free fall in a vacuum, which is not what the question describes. Option A would require the acceleration to grow, which drag cannot cause. Option E describes an object thrown upward and returning, not one released from rest.</p>
<p><b>How to answer graph questions quickly.</b> Ask three things in order: what is the value at zero, is the gradient increasing or decreasing, and what happens at large times. Those three questions answer almost every graph question on this paper.</p>`,
  trap: "Drawing free-fall behaviour when drag is present. Drag can only reduce the acceleration."
},
{
  id: "A-10", module: "A", topic: "Estimation", diff: 1,
  q: "Which is closest to the number of seconds in a year?",
  opts: ["3 × 10⁹", "3 × 10⁶", "3 × 10⁸", "3 × 10⁵", "3 × 10⁷"],
  ans: 4,
  sol: `<p>Multiply the three factors, rounding aggressively:</p>
<div class="formula">365 days × 24 hours × 3600 seconds
≈ 400 × 25 × 3600
= 10 000 × 3600
= 3.6 × 10⁷</div>
<p>Refining to 365 × 24 × 3600 gives <code>3.15 × 10⁷</code>, so the answer is <code>3 × 10⁷</code>.</p>
<p><b>Answer: E.</b></p>
<p><b>The rounding trick that makes it fast.</b> Rounding 365 up to 400 and 24 up to 25 turns the multiplication into <code>400 × 25 = 10 000</code>, which is trivial. The overestimate from rounding up is partly cancelled by the fact that 3600 is slightly more than 3500. The estimate lands within 15% of the true value with no long multiplication at all.</p>
<p><b>Why this matters.</b> Questions about rates over a year — energy consumption, decay counts, light travel — all need this conversion, and doing it in ten seconds rather than sixty is the difference between finishing the paper and not.</p>
<p><b>A related anchor worth having.</b> A year is about <code>π × 10⁷</code> seconds — that is, 3.14 × 10⁷. The coincidence with <code>π</code> makes it memorable, and it is accurate to 0.4%. If you can recall that one fact, every year-based estimation becomes immediate.</p>
<p><b>Where the wrong options come from.</b> Option C, <code>3 × 10⁸</code>, is the number of seconds in a year to the wrong power — it is what you get by multiplying <code>365 × 24 × 360</code>, i.e. dropping a zero from the seconds-per-hour factor. Option B, <code>3 × 10⁶</code>, is roughly the number of seconds in a <i>month</i>, and option D, <code>3 × 10⁵</code>, roughly a day and a half — both are the result of losing a factor of ten or a hundred somewhere in the chain. Option A, <code>3 × 10⁹</code>, is a year counted in the wrong direction by two powers of ten. Because every option differs only by a power of ten, the question is really testing whether you tracked the exponents rather than whether you can multiply.</p>`,
  trap: "Attempting the full multiplication instead of rounding. Track the powers of ten separately."
},

/* ===================== MODULE B — kinematics ===================== */

{
  id: "B-01", module: "B", topic: "Free fall", diff: 1,
  q: "An object is released from rest and falls freely. How far has it fallen after 2.0 s? Use <code>g = 10 m s⁻²</code>.",
  opts: ["20 m", "10 m", "40 m", "5 m", "45 m"],
  ans: 0,
  sol: `<p>Released from rest, so <code>u = 0</code>, and we want distance given time and acceleration:</p>
<div class="formula">s = ut + ½at² = 0 + ½ × 10 × 2.0² = ½ × 10 × 4 = 20 m</div>
<p><b>Answer: A.</b></p>
<p><b>The average-speed check.</b> After 2.0 s the speed is <code>10 × 2.0 = 20 m s⁻¹</code>. Starting from rest and accelerating uniformly, the average speed is <code>10 m s⁻¹</code>. Over 2.0 s that gives 20 m ✓. This route is often faster than the equation, and it confirms the answer independently.</p>
<p><b>The traps.</b> Option B, 10 m, is the average speed in m s⁻¹ rather than a distance. Option C, 40 m, is what you get from forgetting the factor of ½. Option E, 45 m, is the distance for 3.0 s — a misreading of the time.</p>
<p><b>The general result worth remembering.</b> For an object released from rest, <code>s = ½gt²</code>, so the distance goes as the <b>square</b> of the time. After 1 s it has fallen 5 m, after 2 s 20 m, after 3 s 45 m. Those three numbers are worth memorising, because they let you answer a whole family of questions instantly.</p>`,
  trap: "Forgetting the factor of ½, or reporting the final speed as a distance."
},
{
  id: "B-02", module: "B", topic: "Uniform acceleration", diff: 1,
  q: "A car travelling at 30 m s⁻¹ brakes uniformly to rest in a distance of 45 m. What is the magnitude of its deceleration?",
  opts: ["10 m s⁻²", "5 m s⁻²", "15 m s⁻²", "20 m s⁻²", "30 m s⁻²"],
  ans: 0,
  sol: `<p>Time is not mentioned and not wanted, so use the equation that omits it:</p>
<div class="formula">v² = u² + 2as
0 = 30² + 2a(45)
0 = 900 + 90a
a = −10 m s⁻²</div>
<p>So the deceleration is <code>10 m s⁻²</code>.</p>
<p><b>Answer: A.</b></p>
<p><b>Why the choice of equation matters.</b> The question gives the initial speed, the final speed and the distance. That is exactly the set of quantities for which <code>v² = u² + 2as</code> is designed, and the fact that time is absent is the signal to use it. If you had tried to find the time first, you would have needed a second equation and twice the work.</p>
<p><b>The physical sanity check.</b> A deceleration of <code>10 m s⁻²</code> is slightly more than <code>g</code>, which is a very hard stop — comparable to emergency braking on a high-friction surface. For comparison, a comfortable stop is around <code>5 m s⁻²</code>. So the answer is physically plausible but at the extreme end, which is what a 45 m stopping distance from 30 m s⁻¹ implies.</p>
<p><b>The traps.</b> Option B, 5 m s⁻², is the comfortable-stop value and is what you get from a factor-of-two slip. Option C, 15 m s⁻², comes from using <code>a = v/t</code> with an incorrectly computed time.</p>`,
  trap: "Using a suvat equation that contains time when time is neither given nor wanted."
},
{
  id: "B-03", module: "B", topic: "Multi-phase motion", diff: 2,
  q: "A train accelerates uniformly from rest at 0.50 m s⁻² for 20 s, then travels at constant speed for 30 s. What is the total distance travelled?",
  opts: ["400 m", "300 m", "350 m", "450 m", "500 m"],
  ans: 0,
  sol: `<p><b>Phase 1 — acceleration.</b> From rest with <code>a = 0.50 m s⁻²</code> for 20 s:</p>
<div class="formula">s₁ = ½at² = ½ × 0.50 × 400 = 100 m
v = at = 0.50 × 20 = 10 m s⁻¹</div>
<p><b>Phase 2 — constant speed.</b> The train travels at the speed it reached, 10 m s⁻¹, for 30 s:</p>
<div class="formula">s₂ = 10 × 30 = 300 m</div>
<p><b>Total.</b> <code>100 + 300 = 400 m</code>.</p>
<p><b>Answer: A.</b></p>
<p><b>The graph route, which is faster and safer.</b> Sketch velocity against time. Phase 1 is a triangle of base 20 s and height 10 m s⁻¹, giving <code>½ × 20 × 10 = 100 m</code>. Phase 2 is a rectangle 30 s wide and 10 m s⁻¹ tall, giving 300 m. Total 400 m. Two shapes, two mental multiplications, no suvat at all.</p>
<p><b>The traps.</b> Option B, 300 m, counts only the constant-speed phase — the error of forgetting the acceleration phase entirely. Option C, 350 m, comes from treating the acceleration phase as if the train already had its final speed for half the time.</p>
<p><b>The key linking quantity.</b> The velocity at the end of phase 1 is the initial velocity of phase 2. Recognising and computing that shared quantity is the essential step in every multi-phase problem, and forgetting it is what makes these questions feel harder than they are.</p>`,
  trap: "Forgetting that the final speed of one phase is the initial speed of the next."
},
{
  id: "B-04", module: "B", topic: "Projectile motion", diff: 1,
  q: "A ball is thrown horizontally from a cliff 45 m high. How long does it take to reach the ground? Use <code>g = 10 m s⁻²</code>.",
  opts: ["4.5 s", "1.5 s", "2.0 s", "3.0 s", "9.0 s"],
  ans: 3,
  sol: `<p>The throw is horizontal, so the initial <b>vertical</b> velocity is zero. The vertical motion is therefore free fall from rest:</p>
<div class="formula">h = ½gt²
45 = ½ × 10 × t²
45 = 5t²
t² = 9
t = 3.0 s</div>
<p><b>Answer: D.</b></p>
<p><b>What the horizontal speed would have contributed: nothing.</b> The time of fall depends only on the height and <code>g</code>. That is why the question can omit the horizontal speed entirely and still be answerable — and why a ball thrown horizontally at 100 m s⁻¹ from the same cliff would land at the same instant, just much further out.</p>
<p><b>The trap.</b> Option A, 4.5 s, is what you get from a slip in the algebra — for example solving <code>t² = 20</code> or forgetting the ½ in a way that leaves <code>t² = 45/10 × ... </code>. Option E, 9.0 s, is <code>t²</code> reported as <code>t</code>, the classic error of failing to take the square root.</p>
<p><b>The habit that prevents it.</b> Write <code>t² = ...</code> on one line and <code>t = √(...)</code> on the next, as separate steps. Doing both at once is where the square root gets lost.</p>`,
  trap: "Forgetting to take the square root, or thinking the horizontal speed affects the fall time."
},
{
  id: "B-05", module: "B", topic: "Relative motion", diff: 1,
  q: "Two cars travel directly towards each other on a straight road, at 20 m s⁻¹ and 30 m s⁻¹. They are initially 500 m apart. How long until they meet?",
  opts: ["10 s", "5 s", "16.7 s", "20 s", "25 s"],
  ans: 0,
  sol: `<p>Because they approach each other, their speeds <b>add</b> to give the closing speed:</p>
<div class="formula">closing speed = 20 + 30 = 50 m s⁻¹
time = 500/50 = 10 s</div>
<p><b>Answer: A.</b></p>
<p><b>Why the speeds add.</b> In the frame of one car, the other approaches at the sum of the two speeds. Equivalently, in a fixed frame, the gap closes by 20 m each second from one car and 30 m each second from the other, so 50 m of the gap disappears every second.</p>
<p><b>The contrast worth noting.</b> If instead one car were <i>chasing</i> the other at 30 m s⁻¹ behind a car doing 20 m s⁻¹, the closing speed would be the <b>difference</b>, 10 m s⁻¹, and the time to catch up would be 50 s. Same numbers, opposite operation, because the geometry changed. Reading whether the motion is approaching or chasing is the whole question.</p>
<p><b>The traps.</b> Option C, 16.7 s, is <code>500/30</code> — using only one car's speed. Option E, 25 s, is <code>500/20</code>. Both ignore the other car entirely, which is the error the question is designed to catch.</p>
<p><b>The general principle.</b> Relative velocity is vector subtraction: <code>v_AB = v_A − v_B</code>. For head-on motion the vectors point in opposite directions, so the subtraction produces a sum of magnitudes.</p>`,
  trap: "Using the difference of speeds for approaching bodies. Approaching means add, chasing means subtract."
},
{
  id: "B-06", module: "B", topic: "Bounces and energy", diff: 2,
  q: "A ball is dropped from a height of 2.0 m and rebounds to a height of 0.50 m. What fraction of its kinetic energy is retained in the bounce?",
  opts: ["2", "1/2", "1/16", "3/4", "1/4"],
  ans: 4,
  sol: `<p>At the ground, the kinetic energy equals the gravitational energy lost in falling, so <code>Ek ∝ h</code>. The same relationship holds on the way up. Therefore the fraction of kinetic energy retained equals the fraction of height regained:</p>
<div class="formula">E_after/E_before = h_after/h_before = 0.50/2.0 = 1/4</div>
<p><b>Answer: E.</b></p>
<p><b>Why the height ratio works directly.</b> For a fall from height <code>h</code>, the impact speed satisfies <code>v² = 2gh</code>, so <code>v ∝ √h</code>. Since kinetic energy is <code>½mv²</code>, it goes as <code>v²</code>, and therefore as <code>h</code> directly. The square root in the speed and the square in the energy cancel exactly.</p>
<p><b>The trap.</b> Option B, 1/2, is the most common wrong answer, and it comes from assuming the <i>speed</i> halves. It does not — the height quarters, so the speed halves and the energy quarters. Working in terms of height from the start avoids the confusion entirely.</p>
<p><b>The general rule worth holding onto.</b> For a bouncing ball: height, kinetic energy and the square of the speed all change by the same factor; the speed itself changes by the square root of that factor. Keeping track of which quantities are linear and which are quadratic is the whole skill, and it is the same skill as in the power questions in module H.</p>`,
  trap: "Reporting the ratio of speeds when the question asks about energy. Energy goes as the square of speed."
},

/* ===================== MODULE C — forces, momentum, energy ===================== */

{
  id: "C-01", module: "C", topic: "Inclined plane", diff: 1,
  q: "A block of weight 100 N rests on a smooth slope inclined at 30° to the horizontal. What is the component of its weight acting down the slope?",
  opts: ["100 N", "87 N", "50 N", "25 N", "43 N"],
  ans: 2,
  sol: `<p>Resolve the weight along and perpendicular to the slope:</p>
<div class="formula">down the slope:        mg sin θ = 100 × sin 30° = 100 × 0.50 = 50 N
perpendicular:         mg cos θ = 100 × cos 30° = 100 × 0.87 = 87 N</div>
<p><b>Answer: C, 50 N.</b></p>
<p><b>The limit check that prevents the standard error.</b> As the slope becomes flat, <code>θ → 0</code>, and the component down the slope must go to <b>zero</b>. Only <code>mg sin θ</code> does that. If you had written <code>mg cos θ</code>, you would get 87 N — option B — which would mean a block on a horizontal surface has a force pulling it along. That is plainly wrong.</p>
<p><b>Why the two components are 50 and 87 rather than 50 and 50.</b> They must satisfy <code>(mg sin θ)² + (mg cos θ)² = (mg)²</code>, which is Pythagoras. Here <code>50² + 87² = 2500 + 7569 = 10 069 ≈ 100²</code> ✓. So the check is available: square both components and add; the result must be the square of the weight.</p>
<p><b>The traps.</b> Option B is the cosine component, the swap error. Option E, 43 N, is <code>100 sin 25°</code>, a misreading of the angle. Option D, 25 N, is <code>100 sin 30° / 2</code>.</p>
<p><b>Why this matters so much.</b> The <code>sin</code>-versus-<code>cos</code> swap on an inclined plane is the single most common error in mechanics. The limit check takes two seconds and catches it every time. Make it automatic.</p>`,
  trap: "Writing mg cos θ for the component down the slope. Check the θ → 0 limit."
},
{
  id: "C-02", module: "C", topic: "Moments", diff: 1,
  q: "A uniform beam of weight 400 N and length 6.0 m rests on two supports, one at each end. A load of 200 N is placed at the midpoint. What is the reaction force at each support?",
  opts: ["300 N each", "200 N each", "400 N each", "600 N each", "100 N each"],
  ans: 0,
  sol: `<p>The arrangement is symmetric, so each support carries half the total load.</p>
<div class="formula">total downward force = 400 + 200 = 600 N
each reaction = 600/2 = 300 N</div>
<p><b>Answer: A, 300 N each.</b></p>
<p><b>Confirm by taking moments.</b> Take moments about the left support, which eliminates the left reaction:</p>
<div class="formula">clockwise: beam weight 400 × 3.0 = 1200 N m
clockwise: load 200 × 3.0 = 600 N m
total clockwise = 1800 N m
anticlockwise: R_right × 6.0</div>
<div class="formula">6.0 R_right = 1800   →   R_right = 300 N ✓</div>
<p>The two routes agree, which is the check to build as a habit.</p>
<p><b>Why the symmetry shortcut is legitimate.</b> Both the beam's weight and the load act at the midpoint, so the entire load is applied at the centre. The arrangement is left–right symmetric about that point, so the two supports must share equally. Recognising symmetry before calculating is a genuine time-saver.</p>
<p><b>The traps.</b> Option B, 200 N each, accounts for the load but forgets the beam's own weight. Option C, 400 N each, accounts for the beam but forgets the load. Option D, 600 N each, is the total force applied to each support — the error of not halving.</p>`,
  trap: "Forgetting the beam's own weight, which acts at the midpoint for a uniform beam."
},
{
  id: "C-03", module: "C", topic: "Momentum", diff: 1,
  q: "A 2.0 kg trolley moving at 3.0 m s⁻¹ collides with a stationary 1.0 kg trolley and they move off together. What is their common speed?",
  opts: ["1.0 m s⁻¹", "2.0 m s⁻¹", "3.0 m s⁻¹", "1.5 m s⁻¹", "6.0 m s⁻¹"],
  ans: 1,
  sol: `<p>Momentum is conserved in the collision. Before:</p>
<div class="formula">p = 2.0 × 3.0 + 1.0 × 0 = 6.0 kg m s⁻¹</div>
<p>After, the combined mass is 3.0 kg moving at <code>v</code>:</p>
<div class="formula">6.0 = 3.0 v   →   v = 2.0 m s⁻¹</div>
<p><b>Answer: B.</b></p>
<p><b>The kinetic energy check, which tells you the collision is inelastic.</b> Before: <code>½ × 2.0 × 3.0² = 9.0 J</code>. After: <code>½ × 3.0 × 2.0² = 6.0 J</code>. So 3.0 J of kinetic energy has been lost, which is expected for a collision in which the bodies stick together. If the question had asked whether kinetic energy was conserved, the answer would be no.</p>
<p><b>Why momentum is always conserved here.</b> The trolleys exert equal and opposite forces on each other, and there is no external resultant force in the horizontal direction. Momentum conservation applies whether the collision is elastic or not — it is kinetic energy that is not always conserved.</p>
<p><b>The traps.</b> Option A, 1.0 m s⁻¹, comes from dividing the momentum by the wrong mass. Option D, 1.5 m s⁻¹, is the <i>average</i> of the initial speeds of the two trolleys, which is not a physically meaningful quantity here. Option E, 6.0 m s⁻¹, is the momentum itself reported as a speed.</p>`,
  trap: "Dividing the momentum by the wrong mass, or assuming kinetic energy is conserved in a sticking collision."
},
{
  id: "C-04", module: "C", topic: "Impulse", diff: 2,
  q: "A force acting on a body rises uniformly from zero to 20 N over 0.50 s, then falls uniformly back to zero over the next 0.50 s. What is the total impulse delivered?",
  opts: ["10 N s", "5 N s", "20 N s", "2.5 N s", "40 N s"],
  ans: 0,
  sol: `<p>The impulse is the area under the force–time graph. The graph is a triangle with base 1.0 s and height 20 N:</p>
<div class="formula">impulse = ½ × base × height = ½ × 1.0 × 20 = 10 N s</div>
<p><b>Answer: A.</b></p>
<p><b>The alternative reading, which is a good check.</b> The average force over the whole second is 10 N — half the peak, because the shape is symmetric. So <code>impulse = average force × time = 10 × 1.0 = 10 N s</code> ✓. Two routes, same answer.</p>
<p><b>Why the area is the impulse.</b> Impulse is <code>FΔt</code> for a constant force, and the area of a rectangle of height <code>F</code> and width <code>Δt</code> is exactly that. For a varying force the same reasoning applies to each narrow strip, and the total is the area. This is the direct analogue of work being the area under a force–displacement graph.</p>
<p><b>The traps.</b> Option C, 20 N s, is <code>F × t</code> using the peak force and the full time — the answer you get by ignoring the triangular shape. Option B, 5 N s, is the area of just one of the two triangles. Option D, 2.5 N s, is a quarter of the answer.</p>
<p><b>How to spot the shape fast.</b> Sketch the graph. A force that rises from zero and returns to zero over a total time <code>T</code> traces a triangle of area <code>½ F_peak T</code>. Recognising that shape removes the need to think about the two halves separately.</p>`,
  trap: "Using the peak force rather than the average. For a triangular profile the average is half the peak."
},
{
  id: "C-05", module: "C", topic: "Work", diff: 1,
  q: "A force of 30 N pushes a box 4.0 m along a horizontal floor. What is the work done by this force?",
  opts: ["80 J", "40 J", "120 J", "200 J", "20 J"],
  ans: 2,
  sol: `<p>The force is in the direction of motion, so <code>cos θ = 1</code>:</p>
<div class="formula">W = Fs cos θ = 30 × 4.0 × 1 = 120 J</div>
<p><b>Answer: C.</b></p>
<p><b>The question this one is quietly testing.</b> The presence of friction would not change the work done <i>by the applied force</i> — friction is a separate force doing its own (negative) work. If the question had asked for the <i>net</i> work, you would subtract the friction's contribution. Reading which force's work is asked for is the skill.</p>
<p><b>The extension worth doing.</b> If the floor exerted 10 N of friction, the net work would be <code>(30 − 10) × 4.0 = 80 J</code> — option A. That is the kinetic energy gained by the box. The applied force does 120 J, friction removes 40 J, and the difference becomes kinetic energy. Tracking the energy account in that way is what a good answer looks like.</p>
<p><b>The traps.</b> Option B, 40 J, is the work done against friction alone. Option E, 20 J, is the net force in newtons reported as an energy. Option D, 200 J, is <code>30 × 4.0 × ... </code> with a factor slip.</p>
<p><b>Why the angle matters.</b> If the 30 N force had been applied at 60° to the horizontal, the work would be <code>30 × 4.0 × cos 60° = 60 J</code>. The <code>cos θ</code> factor is not decoration — it is what makes the definition of work directional.</p>`,
  trap: "Confusing the work done by one force with the net work done on the body."
},
{
  id: "C-06", module: "C", topic: "Power", diff: 1,
  q: "A pump raises 100 kg of water through a height of 10 m in 20 s. What is the minimum power required? Use <code>g = 10 m s⁻²</code>.",
  opts: ["50 W", "1000 W", "500 W", "5000 W", "200 W"],
  ans: 2,
  sol: `<p><b>Step 1 — the work done.</b> The pump must supply the gravitational potential energy:</p>
<div class="formula">W = mgΔh = 100 × 10 × 10 = 10 000 J</div>
<p><b>Step 2 — the power.</b></p>
<div class="formula">P = W/t = 10 000/20 = 500 W</div>
<p><b>Answer: C.</b></p>
<p><b>Why "minimum".</b> The question says minimum because a real pump also has to overcome friction and give the water kinetic energy as it leaves. The figure of 500 W is the useful output power; the input power would be larger, and the ratio is the efficiency. That distinction is worth noting, because a follow-up question might ask for the efficiency given an input power.</p>
<p><b>The traps.</b> Option B, 1000 W, comes from using <code>t = 10 s</code>. Option D, 5000 W, is what you get from omitting the factor of <code>g</code> incorrectly or using <code>mgh × 5</code>. Option E, 200 W, is <code>mgh/t</code> with a slip in the powers of ten.</p>
<p><b>The alternative route using force and speed.</b> The pump must exert a force equal to the weight, <code>100 × 10 = 1000 N</code>, and lift it at <code>10/20 = 0.5 m s⁻¹</code>. Then <code>P = Fv = 1000 × 0.5 = 500 W</code> ✓. Both routes give the same answer, which is a good confirmation and a reminder that <code>P = Fv</code> is often the faster form.</p>`,
  trap: "Reporting the energy in joules when power in watts is asked for. Divide by the time."
},
{
  id: "C-07", module: "C", topic: "Connected bodies", diff: 2,
  q: "Masses of 4.0 kg and 2.0 kg hang on either side of a frictionless pulley, connected by a light string. What is the acceleration of the system? Use <code>g = 10 m s⁻²</code>.",
  opts: ["5.0 m s⁻²", "3.3 m s⁻²", "6.7 m s⁻²", "10 m s⁻²", "1.7 m s⁻²"],
  ans: 1,
  sol: `<p>Use the whole-system approach: the driving force is the <b>difference</b> in weights, and the mass being accelerated is the <b>total</b> mass.</p>
<div class="formula">a = (m₁ − m₂)g / (m₁ + m₂) = (4.0 − 2.0) × 10 / (4.0 + 2.0) = 20/6.0 ≈ 3.3 m s⁻²</div>
<p><b>Answer: B.</b></p>
<p><b>Why the tension cancels.</b> The tension pulls the heavier mass backward and the lighter mass forward with the same magnitude. Treating the two as one system makes those two contributions cancel, which is exactly why the whole-system route is faster than writing two simultaneous equations.</p>
<p><b>The limit checks.</b> If the 2.0 kg mass were removed, the 4.0 kg mass would fall freely and <code>a = g = 10 m s⁻²</code> ✓. If the two masses were equal, the system would balance and <code>a = 0</code> ✓. Both limits are satisfied, which confirms the formula's structure.</p>
<p><b>The traps.</b> Option A, 5.0 m s⁻², comes from using the correct numerator but only the heavier mass in the denominator: <code>20/4.0 = 5.0</code>. Option C, 6.7 m s⁻², is <code>20/3.0</code>. Option D, 10 m s⁻², is free fall, which ignores the lighter mass entirely.</p>
<p><b>The follow-up worth being able to do.</b> The tension is <code>2m₁m₂g/(m₁ + m₂) = 2 × 4 × 2 × 10/6 = 26.7 N</code>. Check on the lighter mass: tension up 26.7 N minus weight 20 N gives a net 6.7 N, and <code>6.7/2.0 = 3.3 m s⁻²</code> ✓. The same acceleration, which confirms both results.</p>`,
  trap: "Using only the heavier mass in the denominator. The whole system is being accelerated."
},
{
  id: "C-08", module: "C", topic: "Friction on a slope", diff: 2,
  q: "A block rests on a slope. The coefficient of static friction between block and slope is 0.50. At what angle does the block start to slide?",
  opts: ["45°", "30°", "27°", "60°", "22°"],
  ans: 2,
  sol: `<p>The block is on the point of sliding when the component of weight down the slope just equals the maximum friction:</p>
<div class="formula">mg sin θ = μmg cos θ</div>
<p>The mass cancels, leaving</p>
<div class="formula">tan θ = μ = 0.50</div>
<p>So <code>θ = tan⁻¹(0.50) ≈ 27°</code>.</p>
<p><b>Answer: C.</b></p>
<p><b>Why the mass cancels, and why that matters.</b> A heavy block and a light block slide at the same angle, because both the driving force and the friction scale with the mass. This is counter-intuitive and it is exactly the kind of result a competition question rewards you for knowing.</p>
<p><b>Reading tan⁻¹(0.5) without a calculator.</b> Recall that <code>tan 30° ≈ 0.577</code> and <code>tan 45° = 1</code>. Since 0.50 is less than 0.577, the angle must be less than 30°. That eliminates B, C and D immediately, and a rough interpolation between 0 (tan 0 = 0) and 30° puts it near 27°.</p>
<p><b>The traps.</b> Option B, 30°, is the answer you get by recalling <code>tan 30° = 0.577</code> and rounding carelessly, or by assuming the slide angle is always 30°. Option A, 45°, would require <code>μ = 1</code>.</p>
<p><b>The general result worth memorising.</b> <code>tan θ = μ</code> for the sliding angle, independent of mass. Rearranged, the coefficient of friction equals the tangent of the angle at which an object just begins to slide — which is a genuinely useful experimental method for measuring <code>μ</code>.</p>`,
  trap: "Thinking a heavier block slides at a smaller angle. The mass cancels, so it does not."
},
{
  id: "C-09", module: "C", topic: "Centre of mass", diff: 1,
  q: "A 2.0 kg mass is placed at position <code>x = 0</code> and a 6.0 kg mass at <code>x = 4.0 m</code>. Where is the centre of mass of the system?",
  opts: ["3.5 m", "1.0 m", "2.0 m", "3.0 m", "4.0 m"],
  ans: 3,
  sol: `<p>Use the weighted-average formula:</p>
<div class="formula">x_cm = (m₁x₁ + m₂x₂)/(m₁ + m₂)
     = (2.0 × 0 + 6.0 × 4.0)/(2.0 + 6.0)
     = 24/8.0
     = 3.0 m</div>
<p><b>Answer: D.</b></p>
<p><b>The physical reasoning that gives the answer instantly.</b> The centre of mass must lie closer to the heavier mass. Since the 6.0 kg mass is three times the 2.0 kg mass, the centre of mass is three times closer to it. The separation is 4.0 m, so it sits <code>4.0 × 2/(2 + 6) = 1.0 m</code> from the 6.0 kg mass, which is at <code>4.0 − 1.0 = 3.0 m</code> ✓. That reasoning takes five seconds and needs no formula.</p>
<p><b>The traps.</b> Option C, 2.0 m, is the simple average of the positions — the answer you get by ignoring the masses entirely. Option A, 3.5 m, comes from using the ratio 3:1 in the wrong direction. Option E, 4.0 m, is the position of the heavier mass itself.</p>
<p><b>The sanity check.</b> The centre of mass must lie between the two masses, so between 0 and 4.0 m, and nearer the heavier one, so greater than 2.0 m. That narrows the answer to 3.0 or 3.5 immediately, and the ratio settles it.</p>`,
  trap: "Taking a simple average of positions instead of a weighted average by mass."
},

/* ===================== MODULE D — circular motion ===================== */

{
  id: "D-01", module: "D", topic: "Centripetal acceleration", diff: 1,
  q: "An object moves in a circle of radius 5.0 m at a constant speed of 10 m s⁻¹. What is its acceleration?",
  opts: ["5.0 m s⁻²", "2.0 m s⁻²", "50 m s⁻²", "100 m s⁻²", "20 m s⁻²"],
  ans: 4,
  sol: `<p>Use <code>a = v²/r</code>:</p>
<div class="formula">a = 10²/5.0 = 100/5.0 = 20 m s⁻²</div>
<p><b>Answer: E.</b></p>
<p><b>Why there is an acceleration even at constant speed.</b> The <i>speed</i> is constant but the <i>velocity</i> is not, because its direction is changing continuously. The acceleration points towards the centre of the circle and is perpendicular to the velocity at every instant.</p>
<p><b>The consequence worth stating.</b> Because the acceleration is perpendicular to the motion, the force causing it does no work. That is why the kinetic energy — and therefore the speed — stays constant. If a question asks why the speed does not change, that is the answer.</p>
<p><b>The traps.</b> Option B, 2.0 m s⁻², is <code>v/r</code> rather than <code>v²/r</code>. Option C, 50 m s⁻², is <code>vr</code>. Option D, 100 m s⁻², is <code>v²</code> with the division omitted. Each corresponds to a specific slip in the formula.</p>
<p><b>The magnitude check.</b> An acceleration of <code>20 m s⁻²</code> is about twice <code>g</code>. For a car cornering at 10 m s⁻¹ on a 5.0 m radius, that is a demanding turn — the sort of thing you would feel strongly. If your answer had come out as a small fraction of <code>g</code>, that would suggest a slip.</p>`,
  trap: "Using v/r instead of v²/r, or forgetting to divide by the radius at all."
},
{
  id: "D-02", module: "D", topic: "Angular speed", diff: 2,
  q: "A wheel rotates at 3000 revolutions per minute. What is its angular speed in radians per second? Take <code>π ≈ 3.1</code>.",
  opts: ["100 rad s⁻¹", "50 rad s⁻¹", "3000 rad s⁻¹", "18 600 rad s⁻¹", "310 rad s⁻¹"],
  ans: 4,
  sol: `<p>Convert revolutions per minute to revolutions per second, then to radians per second:</p>
<div class="formula">3000 rev/min = 50 rev/s
ω = 2πf = 2 × 3.1 × 50 = 310 rad s⁻¹</div>
<p><b>Answer: E.</b></p>
<p><b>The one-step version.</b> Multiply revs per minute by <code>2π/60 ≈ 0.105</code>: <code>3000 × 0.105 ≈ 315</code>. Slightly different from 310 because of the rounded <code>π</code>, but the same to two significant figures — and it takes one multiplication instead of two.</p>
<p><b>Why radians and not degrees.</b> The relationship <code>ω = 2πf</code> assumes radians, because a radian is defined so that the arc length equals the radius. In degrees the formula would need a factor of <code>360/2π</code>. Every formula in this module assumes radians.</p>
<p><b>The traps.</b> Option B, 50 rad s⁻¹, is the frequency in revolutions per second — the answer you get by forgetting the <code>2π</code>. Option D, 18 600 rad s⁻¹, is <code>2π × 3000</code>, the error of forgetting to convert minutes to seconds. Both are single-omission errors and both are deliberately present.</p>
<p><b>An anchor worth having.</b> 3000 rpm is a typical car engine speed at motorway cruising, and <code>300 rad s⁻¹</code> is the right order for that. Knowing the physical context lets you spot an answer that is out by a factor of 60.</p>`,
  trap: "Forgetting the 2π, or forgetting to convert minutes to seconds. Both give plausible-looking answers."
},
{
  id: "D-03", module: "D", topic: "Cornering", diff: 2,
  q: "A car goes round a bend of radius 20 m on a flat road. The coefficient of friction between the tyres and the road is 0.50. What is the maximum speed at which the car can take the bend without skidding? Use <code>g = 10 m s⁻²</code>.",
  opts: ["100 m s⁻¹", "14 m s⁻¹", "20 m s⁻¹", "5.0 m s⁻¹", "10 m s⁻¹"],
  ans: 4,
  sol: `<p>Friction supplies the centripetal force. At the maximum speed, friction is at its limit:</p>
<div class="formula">μmg = mv²/r</div>
<p>The mass cancels:</p>
<div class="formula">v² = μrg = 0.50 × 20 × 10 = 100
v = 10 m s⁻¹</div>
<p><b>Answer: E.</b></p>
<p><b>Why the mass cancels, and what that means physically.</b> Both the required centripetal force and the available friction are proportional to the mass, so a heavy car and a light car can take the bend at the same maximum speed. That is a genuinely counter-intuitive result and it is worth being able to state.</p>
<p><b>The traps.</b> Option B, 14 m s⁻¹, is <code>√(μrg)</code> with <code>r = 20</code> but <code>μ = 1.0</code> — or, more likely, the answer you get from forgetting the square root and computing <code>√(0.5 × 20 × 10 × 2)</code>. Option D, 5.0 m s⁻¹, is <code>μrg/2</code>. Option A, 100 m s⁻¹, is <code>v²</code> reported as <code>v</code>.</p>
<p><b>The wet-road comparison.</b> On a wet road <code>μ</code> might be 0.25 instead of 0.50, which would give <code>v = √(0.25 × 20 × 10) = √50 ≈ 7.1 m s⁻¹</code>. So halving the friction reduces the maximum speed by a factor of <code>√2</code>, not by half — because the speed depends on the square root of <code>μ</code>. That is another instance of the square-root behaviour that questions like to test.</p>`,
  trap: "Forgetting the square root, or trying to include the mass when it cancels."
},
{
  id: "D-04", module: "D", topic: "Vertical circle", diff: 2,
  q: "A ball on a string is swung in a vertical circle of radius 1.6 m. What is the minimum speed it must have at the top to keep the string taut? Use <code>g = 10 m s⁻²</code>.",
  opts: ["16 m s⁻¹", "4.0 m s⁻¹", "2.0 m s⁻¹", "8.0 m s⁻¹", "1.6 m s⁻¹"],
  ans: 1,
  sol: `<p>At the top, gravity acts towards the centre. The minimum speed is the one at which the tension just falls to zero:</p>
<div class="formula">mg = mv²/r   →   v² = gr</div>
<div class="formula">v = √(10 × 1.6) = √16 = 4.0 m s⁻¹</div>
<p><b>Answer: B.</b></p>
<p><b>The mass cancels, again.</b> The answer depends only on the radius and <code>g</code>. A heavy ball and a light ball need the same minimum speed to keep the string taut.</p>
<p><b>The traps.</b> Option A, 16 m s⁻¹, is <code>gr</code> without the square root. Option C, 2.0 m s⁻¹, is <code>gr/8</code>. Option E, 1.6 m s⁻¹, is the radius itself.</p>
<p><b>The related result worth knowing, and worth keeping separate.</b> For the ball to complete the whole loop, its speed at the <b>bottom</b> must be <code>√(5gr) = √(5 × 10 × 1.6) = √80 ≈ 8.9 m s⁻¹</code>. The factor of 5 comes from combining the energy change over a height of <code>2r</code> with the minimum speed at the top. Confusing the top and bottom results is a common error — note that the bottom speed is more than twice the top speed.</p>
<p><b>The sanity check on the direction.</b> The bottom speed must be greater than the top speed, since the ball loses kinetic energy as it rises. Any answer that violates that is wrong.</p>`,
  trap: "Confusing the minimum speed at the top (√(gr)) with the minimum at the bottom (√(5gr))."
},
{
  id: "D-05", module: "D", topic: "Orbital ratios", diff: 3,
  q: "Two satellites orbit the Earth in circular orbits. Satellite B orbits at twice the radius of satellite A. What is the ratio of the period of B to the period of A?",
  opts: ["2.0", "2.8", "4.0", "1.4", "8.0"],
  ans: 1,
  sol: `<p>Gravity supplies the centripetal force, so <code>mg = mv²/r</code>, giving <code>v = √(gr)</code>. Substituting into <code>T = 2πr/v</code>:</p>
<div class="formula">T = 2πr/√(gr) = 2π √(r/g)</div>
<p>Since <code>g ∝ 1/r²</code>, we get <code>T ∝ √(r · r²) = r^(3/2)</code>. Taking the ratio with <code>r_B = 2r_A</code>:</p>
<div class="formula">T_B/T_A = 2^(3/2) = (√2)³ = 2.83</div>
<p><b>Answer: B, 2.8.</b></p>
<p><b>How to get <code>2^(3/2)</code> without a calculator.</b> Split the exponent: <code>2^(3/2) = 2¹ × 2^(1/2) = 2 × 1.41 = 2.83</code>. That is two easy steps rather than one awkward one, and it works for any fractional exponent.</p>
<p><b>The traps.</b> Option A, 2.0, is the linear guess — period proportional to radius. Option C, 4.0, is <code>r²</code>, which is the dependence of <code>g</code> rather than of the period. Option D, 1.4, is <code>√2</code>, the answer you get by forgetting the <code>2πr</code> factor in the period.</p>
<p><b>What this is, and what it is not.</b> This is Kepler's third law, derived from circular motion alone — no field theory required. BPhO excludes gravitational fields from Round 0, so a question will be phrased as a ratio like this one rather than asking for <code>GMm/r²</code>. Staying on this side of the boundary is the point of the exercise.</p>`,
  trap: "Assuming the period is proportional to the radius. It goes as r^(3/2)."
},

/* ===================== MODULE E — materials ===================== */

{
  id: "E-01", module: "E", topic: "Young modulus", diff: 2,
  q: "A wire of length 3.0 m and cross-sectional area <code>2.0 × 10⁻⁶ m²</code> extends by 3.0 mm under a load of 200 N. What is the Young modulus of the material?",
  opts: ["1.0 × 10¹² Pa", "1.0 × 10¹⁰ Pa", "1.0 × 10¹¹ Pa", "2.0 × 10¹¹ Pa", "5.0 × 10¹⁰ Pa"],
  ans: 2,
  sol: `<p>Use <code>E = FL/(AΔL)</code>, handling digits and powers of ten separately.</p>
<p><b>Stress.</b></p>
<div class="formula">σ = F/A = 200/(2.0 × 10⁻⁶) = 1.0 × 10⁸ Pa</div>
<p><b>Strain.</b> The extension is 3.0 mm = <code>3.0 × 10⁻³ m</code> over an original length of 3.0 m:</p>
<div class="formula">ε = ΔL/L = 3.0 × 10⁻³/3.0 = 1.0 × 10⁻³</div>
<p><b>Young modulus.</b></p>
<div class="formula">E = σ/ε = 1.0 × 10⁸ / 1.0 × 10⁻³ = 1.0 × 10¹¹ Pa</div>
<p><b>Answer: C.</b></p>
<p><b>The numbers were chosen to cancel, and noticing that saves time.</b> The length 3.0 m and the extension 3.0 mm mean the strain is exactly <code>10⁻³</code>. And the area <code>2.0 × 10⁻⁶</code> with a force of 200 N gives exactly <code>10⁸</code>. Both are clean, which is the signature of a paper designed for mental arithmetic.</p>
<p><b>The order-of-magnitude check.</b> Young moduli for metals are of order <code>10¹⁰</code> to <code>10¹¹ Pa</code>. Option A at <code>10¹²</code> is too stiff for any common metal, and option B at <code>10¹⁰</code> is at the soft end. Only A and D are plausible.</p>
<p><b>The trap.</b> Option B, <code>10¹⁰</code>, is the answer you get from forgetting to convert millimetres to metres — using <code>ΔL = 3.0</code> instead of <code>3.0 × 10⁻³</code>. Unit conversion, not physics, is where the marks are lost in this topic.</p>`,
  trap: "Forgetting to convert millimetres to metres before computing strain."
},
{
  id: "E-02", module: "E", topic: "Springs", diff: 1,
  q: "Two springs of stiffness 100 N m⁻¹ and 300 N m⁻¹ are connected in parallel. What is the combined stiffness?",
  opts: ["600 N m⁻¹", "75 N m⁻¹", "200 N m⁻¹", "133 N m⁻¹", "400 N m⁻¹"],
  ans: 4,
  sol: `<p>Springs in parallel add:</p>
<div class="formula">k_total = k₁ + k₂ = 100 + 300 = 400 N m⁻¹</div>
<p><b>Answer: E.</b></p>
<p><b>Why parallel adds.</b> In parallel, both springs stretch by the same amount, so each contributes its own force. The total force for a given extension is the sum, so the combination is stiffer than either spring alone. That is the physical reason for the addition.</p>
<p><b>The contrast with series.</b> In series the springs experience the same force and stretch in turn, so the total extension is the sum of the individual extensions. The combined stiffness is then <b>less</b> than either: here <code>1/k = 1/100 + 1/300</code> gives <code>k = 75 N m⁻¹</code> — which is option B, present deliberately as the series answer.</p>
<p><b>The memory hook.</b> Springs behave the same way as capacitors and the opposite way to resistors. Parallel: springs and capacitors add, resistors reciprocal-add. If you remember one of the three, you can reconstruct the others.</p>
<p><b>The traps.</b> Option B, 75 N m⁻¹, is the series result. Option D, 133 N m⁻¹, is the arithmetic mean. Option A, 600 N m⁻¹, is the product, which has no physical meaning here.</p>`,
  trap: "Using the series rule for a parallel arrangement. Parallel springs are stiffer than either one."
},
{
  id: "E-03", module: "E", topic: "Elastic strain energy", diff: 1,
  q: "A spring of stiffness 200 N m⁻¹ is stretched by 0.10 m. How much elastic strain energy is stored?",
  opts: ["0.50 J", "2.0 J", "20 J", "1.0 J", "10 J"],
  ans: 3,
  sol: `<p>Use <code>E = ½kx²</code>:</p>
<div class="formula">E = ½ × 200 × 0.10² = ½ × 200 × 0.010 = 1.0 J</div>
<p><b>Answer: D.</b></p>
<p><b>Why the factor of ½.</b> The force rises linearly from zero to <code>kx</code> as the spring stretches, so the work done is the area of a triangle on a force–extension graph, <code>½ × base × height = ½ × x × kx</code>. The same factor of ½ appears in kinetic energy, capacitor energy and here — it is the signature of a quantity that ramps linearly from zero.</p>
<p><b>The trap.</b> Option B, 2.0 J, is <code>kx²</code> without the half — the answer you get by using the full final force throughout the stretch. Option C, 20 J, comes from forgetting to square the extension. Option E, 10 J, is <code>kx²</code> with a different slip.</p>
<p><b>The non-linear caveat.</b> If the spring were stretched beyond its elastic limit, the force–extension graph would curve and the triangle formula would no longer apply. The energy would still be the area under the curve, but it would have to be found by other means. A question that gives you a graph is testing exactly that.</p>
<p><b>Where this energy goes.</b> Released, it converts to kinetic energy or gravitational potential energy. A spring launching a projectile is the standard case: <code>½kx² = ½mv²</code>, so <code>v = x√(k/m)</code>. That derivation appears often and is worth being able to do.</p>`,
  trap: "Using kx² instead of ½kx². The force ramps from zero, so the factor of ½ is required."
},
{
  id: "E-04", module: "E", topic: "Thermal expansion", diff: 2,
  q: "A steel rail 20 m long is heated through 25 K. If <code>α = 1.2 × 10⁻⁵ K⁻¹</code>, by how much does it expand?",
  opts: ["60 mm", "0.60 mm", "6.0 mm", "2.4 mm", "12 mm"],
  ans: 2,
  sol: `<p>Use <code>Δℓ = αℓ₀ΔT</code>:</p>
<div class="formula">Δℓ = 1.2 × 10⁻⁵ × 20 × 25</div>
<p>Handle the digits and the powers separately. Digits: <code>1.2 × 20 × 25 = 600</code>. Powers: <code>10⁻⁵</code>. So</p>
<div class="formula">Δℓ = 600 × 10⁻⁵ m = 6.0 × 10⁻³ m = 6.0 mm</div>
<p><b>Answer: C.</b></p>
<p><b>The mental route.</b> Note that <code>20 × 25 = 500</code>, and <code>1.2 × 500 = 600</code>. Then <code>600 × 10⁻⁵ = 6 × 10⁻³</code>. Two clean steps.</p>
<p><b>Why ΔT needs no conversion.</b> A temperature <i>difference</i> of 25 K is the same as a difference of 25 °C. Only absolute temperatures need the 273 conversion, and this formula uses a difference. So you never need to convert here — a small but real saving under time pressure.</p>
<p><b>The traps.</b> Option B, 0.60 mm, is a factor of ten too small — a powers-of-ten slip, which is the most likely error with an exponent as small as <code>10⁻⁵</code>. Option A, 60 mm, is a factor of ten too large. Option D, 2.4 mm, is the expansion for a 10 K rise.</p>
<p><b>The physical significance.</b> 6 mm over 20 m sounds small, but a rail is constrained at both ends. That 6 mm of prevented expansion would generate a thermal stress of <code>EαΔT = 2 × 10¹¹ × 1.2 × 10⁻⁵ × 25 = 6 × 10⁷ Pa</code> — about 60 MPa, which is a substantial fraction of the yield stress of steel. That is why expansion gaps exist.</p>`,
  trap: "Powers-of-ten slips. Handle the digits and the exponents as two separate streams."
},
{
  id: "E-05", module: "E", topic: "Strain", diff: 1,
  q: "A wire of unstretched length 2.00 m is stretched to a length of 2.02 m. What is the strain?",
  opts: ["0.020", "0.010", "0.99", "1.01", "0.0099"],
  ans: 1,
  sol: `<p>Strain is the extension divided by the <b>original</b> length:</p>
<div class="formula">ε = ΔL/L₀ = (2.02 − 2.00)/2.00 = 0.02/2.00 = 0.010</div>
<p><b>Answer: B, 0.010 — which is 1%.</b></p>
<p><b>Why the original length goes in the denominator.</b> Strain is defined as the fractional change relative to the <i>starting</i> length. Using the final length would give <code>0.02/2.02 = 0.0099</code> — option E — which is close but wrong, and the closeness is what makes it a good distractor.</p>
<p><b>Strain has no units.</b> It is a length divided by a length, so the units cancel. If you find yourself writing a unit next to a strain, something has gone wrong. It is often expressed as a percentage: here, 1%.</p>
<p><b>The traps.</b> Option A, 0.020, is the extension in metres — a length reported where a ratio is wanted. Option C, 0.99, and option D, 1.01, are the ratios <code>L₀/L</code> and <code>L/L₀</code> rather than the fractional <i>change</i>. Option E is the final-length error described above.</p>
<p><b>Why the distinction matters at competition level.</b> A question that gives you both the original and the final length is deliberately testing whether you know which one belongs in the denominator. The two answers differ by only 1% here, but they are different answers, and only one is right.</p>`,
  trap: "Dividing the extension by the final length. The definition of strain uses the original length."
},

/* ===================== MODULE F — waves ===================== */

{
  id: "F-01", module: "F", topic: "Wave speed", diff: 1,
  q: "A sound wave of frequency 500 Hz has a wavelength of 0.68 m. What is its speed?",
  opts: ["34 m s⁻¹", "340 m s⁻¹", "3400 m s⁻¹", "170 m s⁻¹", "680 m s⁻¹"],
  ans: 1,
  sol: `<p>Use <code>v = fλ</code>:</p>
<div class="formula">v = 500 × 0.68 = 340 m s⁻¹</div>
<p><b>Answer: B.</b></p>
<p><b>The answer is the speed of sound in air, which is the point.</b> The question is designed so that the numbers reproduce a known physical value. That is a useful confirmation: if a sound-wave calculation gives 34 m s⁻¹ or 3400 m s⁻¹, you know immediately that a power of ten has slipped.</p>
<p><b>The mental route.</b> <code>500 × 0.68 = 5 × 68 = 340</code>. Converting the decimal multiplication into whole numbers is a reliable trick for this kind of arithmetic.</p>
<p><b>The traps.</b> Option A, 34 m s⁻¹, and option C, 3400 m s⁻¹, are both powers-of-ten errors in opposite directions. Option D, 170 m s⁻¹, is <code>fλ/2</code>. Option E, 680 m s⁻¹, is <code>f × λ × 2</code>.</p>
<p><b>The inverse relationship worth noting.</b> For a fixed speed, <code>f ∝ 1/λ</code>. So a sound wave of twice the frequency has half the wavelength. That ratio relationship is what a competition question would ask, rather than a numerical substitution.</p>`,
  trap: "Powers-of-ten errors. Check the answer against a known physical value such as 340 m s⁻¹."
},
{
  id: "F-02", module: "F", topic: "Stationary waves on strings", diff: 1,
  q: "A string of length 0.60 m is fixed at both ends and vibrates in its fundamental mode. What is the wavelength?",
  opts: ["1.8 m", "0.60 m", "0.30 m", "2.4 m", "1.2 m"],
  ans: 4,
  sol: `<p>In the fundamental mode there is one antinode at the centre and nodes at both ends, so the string holds exactly half a wavelength:</p>
<div class="formula">L = λ/2   →   λ = 2L = 2 × 0.60 = 1.2 m</div>
<p><b>Answer: E.</b></p>
<p><b>The picture, which is faster than the formula.</b> Sketch the fundamental: a single hump between two fixed ends. One hump is half a wavelength, so the wavelength is twice the string length. That sketch takes three seconds and cannot be misremembered.</p>
<p><b>The traps.</b> Option B, 0.60 m, is the string length itself — the error of assuming one full wavelength fits on the string. Option C, 0.30 m, is <code>L/2</code>, which is the wavelength of the <i>second</i> harmonic. Option D, 2.4 m, is <code>4L</code>, which would be the wavelength of a closed pipe's fundamental, not a string's.</p>
<p><b>The general rule.</b> For the <code>n</code>th harmonic, <code>λ = 2L/n</code>. So the fundamental has the <b>longest</b> wavelength, and higher harmonics have progressively shorter ones. That ordering is a useful check: if your calculated wavelength for the third harmonic is longer than for the fundamental, something is wrong.</p>
<p><b>The frequency follows immediately.</b> <code>f = v/λ = v/2L</code>. If the wave speed were 240 m s⁻¹, the fundamental frequency would be <code>240/1.2 = 200 Hz</code>.</p>`,
  trap: "Assuming one whole wavelength fits on the string. The fundamental is half a wavelength."
},
{
  id: "F-03", module: "F", topic: "Wave equation", diff: 2,
  q: "A wave is described by <code>y = 0.10 cos(200t − 5x)</code> in SI units. What is the speed of the wave?",
  opts: ["0.025 m s⁻¹", "20 m s⁻¹", "1000 m s⁻¹", "40 m s⁻¹", "200 m s⁻¹"],
  ans: 3,
  sol: `<p>Read the coefficients: <code>ω = 200 rad s⁻¹</code> and <code>k = 5 rad m⁻¹</code>. The wave speed is</p>
<div class="formula">v = ω/k = 200/5 = 40 m s⁻¹</div>
<p><b>Answer: D.</b></p>
<p><b>Why <code>v = ω/k</code> works.</b> The wave speed is <code>fλ</code>. Since <code>f = ω/2π</code> and <code>λ = 2π/k</code>, the product is <code>(ω/2π)(2π/k) = ω/k</code>. The <code>2π</code> factors cancel, which is exactly why this form is worth knowing — it avoids computing <code>f</code> and <code>λ</code> separately.</p>
<p><b>The trap, and it is the whole point of the question.</b> Option B, 20 m s⁻¹, is <code>ωA = 200 × 0.10</code> — the <b>maximum particle speed</b>, not the wave speed. Option E, 200 m s⁻¹, is <code>ω</code> itself, and option C, 1000 m s⁻¹, is <code>ω × k</code>.</p>
<p><b>The physical distinction worth stating.</b> The particles of the medium oscillate up and down at up to 20 m s⁻¹, while the disturbance itself travels along at 40 m s⁻¹. These are different things with different values, and there is no general relationship between them — changing the amplitude would change the particle speed without touching the wave speed.</p>`,
  trap: "Confusing ωA (maximum particle speed) with ω/k (wave speed)."
},
{
  id: "F-04", module: "F", topic: "Maximum particle speed", diff: 2,
  q: "For the wave <code>y = 0.10 cos(200t − 5x)</code> in SI units, what is the maximum speed of a particle of the medium?",
  opts: ["2.0 m s⁻¹", "40 m s⁻¹", "20 m s⁻¹", "200 m s⁻¹", "0.50 m s⁻¹"],
  ans: 2,
  sol: `<p>The displacement is <code>y = A cos(ωt)</code> for a given particle, so its velocity has maximum magnitude <code>ωA</code>:</p>
<div class="formula">v_max = ωA = 200 × 0.10 = 20 m s⁻¹</div>
<p><b>Answer: C.</b></p>
<p><b>Why the particle speed is not the wave speed.</b> The wave speed is <code>ω/k = 40 m s⁻¹</code> — option B, present as a distractor. The two quantities happen to differ by a factor of two here, but there is no general relationship between them. If the amplitude were doubled to 0.20 m, the particle speed would become 40 m s⁻¹ while the wave speed remained at exactly 40 m s⁻¹ — a coincidence, not a rule.</p>
<p><b>Why the amplitude affects one but not the other.</b> The wave speed is set by the medium — tension and mass per unit length for a string, or density and stiffness for a solid. The particle speed depends on how far each particle has to travel in a cycle, which is the amplitude. Shaking a rope harder makes the wave taller and the particles faster, but the disturbance still travels at the same speed.</p>
<p><b>The traps.</b> Option A, 2.0 m s⁻¹, is <code>Aω/10</code>, a powers-of-ten slip. Option D, 200 m s⁻¹, is <code>ω</code> without multiplying by the amplitude.</p>`,
  trap: "Assuming the particle speed equals the wave speed. They are independent quantities."
},
{
  id: "F-05", module: "F", topic: "Closed pipes", diff: 2,
  q: "A pipe closed at one end has a fundamental frequency of 200 Hz. What is the frequency of the next higher harmonic it can produce?",
  opts: ["800 Hz", "400 Hz", "300 Hz", "600 Hz", "100 Hz"],
  ans: 3,
  sol: `<p>A pipe closed at one end has a node at the closed end and an antinode at the open end, so the length contains an <b>odd</b> number of quarter-wavelengths. It therefore supports only odd harmonics: <code>f, 3f, 5f, …</code></p>
<p>The next harmonic after the fundamental is the third:</p>
<div class="formula">f₃ = 3 × 200 = 600 Hz</div>
<p><b>Answer: D.</b></p>
<p><b>Why the even harmonics are absent.</b> A length of <code>2λ/4 = λ/2</code> would require a node at both ends, and an open end cannot provide a node. The boundary condition itself forbids the even harmonics — they are not merely weak, they do not exist.</p>
<p><b>The trap.</b> Option B, 400 Hz, is the second harmonic, which does not exist in a closed pipe. It is the answer you get by assuming all harmonics are present, as in a string or an open pipe. This is the single most common error on this topic.</p>
<p><b>The comparison with an open pipe.</b> An open pipe of the same length would have a fundamental of 400 Hz, because <code>f = v/2L</code> against <code>v/4L</code>. So a closed pipe sounds an octave <b>lower</b> than an open one of the same length, and its harmonic series is missing every other note. That is why a stopped organ pipe has a different tone colour, not merely a lower pitch.</p>`,
  trap: "Assuming a closed pipe supports all harmonics. It supports odd harmonics only."
},

/* ===================== MODULE G — optics ===================== */

{
  id: "G-01", module: "G", topic: "Critical angle", diff: 1,
  q: "Light travels in a medium of refractive index 1.5. What is the critical angle at the boundary with air? Take <code>sin 42° ≈ 0.669</code>.",
  opts: ["60°", "30°", "49°", "42°", "90°"],
  ans: 3,
  sol: `<p>Use <code>sin θ_c = n₂/n₁</code> with <code>n₂ = 1</code> for air:</p>
<div class="formula">sin θ_c = 1/1.50 = 0.667</div>
<p>So <code>θ_c ≈ 42°</code>.</p>
<p><b>Answer: D.</b></p>
<p><b>Why the answer must be less than 45°.</b> Note that <code>1/1.5 = 2/3 = 0.667</code>, which is less than <code>sin 45° = 0.707</code>. Since sine increases with angle in this range, the critical angle must be below 45°. That single observation eliminates C, D and E without any calculation.</p>
<p><b>The trap.</b> Option C, 49°, is the critical angle for a water–air boundary, where <code>sin θ_c = 1/1.33 = 0.752</code>. Confusing the two is a common slip, and it is worth knowing both values: 42° for glass, 49° for water.</p>
<p><b>The direction condition.</b> A critical angle exists only for light travelling from the denser medium to the less dense one. Light going from air into glass simply refracts and has no critical angle at all. If a question describes light <i>entering</i> a medium and asks about total internal reflection, the premise is wrong.</p>
<p><b>Why this matters practically.</b> Glass's critical angle of 42° is what makes optical fibres and prisms work. Any ray striking the internal surface at more than 42° is perfectly reflected, with no loss — which is why a prism can act as a 100% efficient mirror, unlike a silvered surface.</p>`,
  trap: "Confusing the glass–air critical angle (42°) with the water–air one (49°)."
},
{
  id: "G-02", module: "G", topic: "Snell's law", diff: 1,
  q: "Light in air strikes a glass surface (<code>n = 1.5</code>) at an angle of incidence of 30°. What is the angle of refraction? Take <code>sin 19.5° ≈ 0.334</code>.",
  opts: ["48°", "30°", "15°", "45°", "19.5°"],
  ans: 4,
  sol: `<p>Apply Snell's law with <code>n₁ = 1</code> for air:</p>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂
1 × sin 30° = 1.5 × sin θ₂
0.50 = 1.5 sin θ₂
sin θ₂ = 0.333</div>
<p>So <code>θ₂ ≈ 19.5°</code>.</p>
<p><b>Answer: E.</b></p>
<p><b>Why the ray bends towards the normal.</b> Entering a denser medium, the light slows down, so the ray bends towards the normal and the angle decreases from 30° to 19.5°. That directional check is free: any answer larger than 30° would mean the ray bent away from the normal, which would require entering a less dense medium.</p>
<p><b>The traps.</b> Option B, 30°, is the angle of incidence unchanged — the error of forgetting to apply Snell's law at all. Option D, 45°, and option A, 48°, are larger than the incident angle and therefore in the wrong direction. Option C, 15°, is a plausible-looking but incorrect division.</p>
<p><b>The reason the angle is not simply divided by n.</b> Snell's law relates the <i>sines</i>, not the angles. So <code>sin θ₂ = sin θ₁/n</code>, not <code>θ₂ = θ₁/n</code>. Dividing 30 by 1.5 would give 20°, which is close to the right answer — a coincidence that makes this a genuinely dangerous error on a multiple-choice paper.</p>
<p><b>Where the small-angle approximation would mislead.</b> For small angles, <code>sin θ ≈ θ</code>, so the approximation would suggest <code>θ₂ ≈ θ₁/n</code>. That is why 20° looks tempting. At 30° the approximation is already noticeably inaccurate, and the exact answer is 19.5°.</p>`,
  trap: "Dividing the angle by n instead of dividing the sine by n."
},
{
  id: "G-03", module: "G", topic: "Young's double slit", diff: 2,
  q: "In a Young's double slit experiment the slits are 1.0 mm apart and the screen is 2.0 m from the slits. Light of wavelength 500 nm is used. What is the fringe spacing?",
  opts: ["0.50 mm", "1.0 mm", "2.0 mm", "0.25 mm", "4.0 mm"],
  ans: 1,
  sol: `<p>Use <code>w = λD/s</code>, with everything in metres:</p>
<div class="formula">λ = 500 nm = 5.0 × 10⁻⁷ m
s = 1.0 mm = 1.0 × 10⁻³ m
D = 2.0 m</div>
<div class="formula">w = (5.0 × 10⁻⁷ × 2.0)/(1.0 × 10⁻³)
  = 1.0 × 10⁻⁶/1.0 × 10⁻³
  = 1.0 × 10⁻³ m = 1.0 mm</div>
<p><b>Answer: B.</b></p>
<p><b>The mental route.</b> Digits: <code>5 × 2/1 = 10</code>. Powers: <code>10⁻⁷ × 10⁰/10⁻³ = 10⁻⁴</code>. So <code>10 × 10⁻⁴ = 10⁻³ m</code> ✓. Keeping the two streams separate avoids the exponent arithmetic going wrong.</p>
<p><b>The magnitude check.</b> Fringe spacings in a classroom demonstration are of order a millimetre — visible to the naked eye. An answer in micrometres or centimetres would be wrong, and that check alone removes options D and E.</p>
<p><b>The traps.</b> Option A, 0.50 mm, is <code>λD/2s</code> — treating <code>w</code> as the distance from the centre to the first fringe rather than the spacing between adjacent fringes. Option C, 2.0 mm, is exactly double, from inverting the slit separation.</p>
<p><b>The change question worth being able to answer in ten seconds.</b> If the light were changed to 400 nm blue, the spacing would fall to <code>1.0 × 400/500 = 0.8 mm</code>. If the screen moved to 3.0 m, it would rise to <code>1.0 × 3.0/2.0 = 1.5 mm</code>. Both are pure ratio reasoning — no need to redo the calculation.</p>`,
  trap: "Using λD/2s, which gives the distance to the first fringe rather than the fringe spacing."
},
{
  id: "G-04", module: "G", topic: "Diffraction grating", diff: 2,
  q: "A diffraction grating has a slit spacing of <code>2.0 × 10⁻⁶ m</code>. Light of wavelength 500 nm is incident normally. What is the angle of the first-order maximum? Take <code>sin 14.5° ≈ 0.25</code>.",
  opts: ["7.0°", "30°", "14.5°", "45°", "60°"],
  ans: 2,
  sol: `<p>Use <code>d sin θ = nλ</code> with <code>n = 1</code>:</p>
<div class="formula">2.0 × 10⁻⁶ × sin θ = 1 × 5.0 × 10⁻⁷
sin θ = 5.0 × 10⁻⁷/2.0 × 10⁻⁶ = 0.25</div>
<p>So <code>θ ≈ 14.5°</code>.</p>
<p><b>Answer: C.</b></p>
<p><b>The second-order check, which is worth doing as a habit.</b> With <code>n = 2</code> the sine would be 0.50, giving 30° — option B, present as a distractor. Note that the second-order angle is <b>not</b> twice the first-order angle: it is <code>sin θ</code> that doubles, not <code>θ</code>. That non-linearity is exactly what the question is testing.</p>
<p><b>The maximum-order check.</b> Since <code>sin θ ≤ 1</code>, we need <code>n ≤ d/λ = 2.0 × 10⁻⁶/5.0 × 10⁻⁷ = 4</code>. So orders 0 through 4 are visible, and the first order is comfortably within range. If a question asks how many orders are visible, the answer is 5 — counting the zeroth.</p>
<p><b>The traps.</b> Option A, 7.0°, is roughly half the first-order angle, from a slip in the ratio. Option D, 45°, would require <code>sin θ = 0.707</code>, which corresponds to <code>d/λ ≈ 1.41</code>.</p>
<p><b>Why gratings give sharper maxima than double slits.</b> With many slits, contributions only reinforce when the path difference is <i>exactly</i> a whole number of wavelengths. A small departure from that condition makes the contributions cancel almost completely, so the maxima are narrow and well separated — which is why gratings are used in spectrometers.</p>`,
  trap: "Assuming the second-order angle is twice the first-order angle. It is sin θ that doubles."
},
{
  id: "G-05", module: "G", topic: "Refractive index", diff: 1,
  q: "Light travels through a medium at <code>2.0 × 10⁸ m s⁻¹</code>. What is the refractive index of the medium?",
  opts: ["3.0", "0.67", "2.0", "1.0", "1.5"],
  ans: 4,
  sol: `<p>Use <code>n = c/c_s</code>:</p>
<div class="formula">n = (3.0 × 10⁸)/(2.0 × 10⁸) = 1.5</div>
<p><b>Answer: E.</b></p>
<p><b>Why n must be greater than 1.</b> Light travels fastest in a vacuum, so <code>c_s ≤ c</code> always, which means <code>n ≥ 1</code>. Option B, 0.67, is the reciprocal and is physically impossible. That check eliminates it immediately.</p>
<p><b>The traps.</b> Option B, 0.67, is <code>c_s/c</code> — the ratio inverted. Option C, 2.0, is a plausible-looking but incorrect value. Option D, 1.0, would mean the light is travelling at <code>c</code>, which contradicts the question. Option A, 3.0, is the numerator alone.</p>
<p><b>The physical meaning of 1.5.</b> A refractive index of 1.5 is typical of glass. It means light travels at two thirds of its vacuum speed inside the glass. This is also why the critical angle for glass is 42°: the same factor of 1.5 appears in <code>sin θ_c = 1/n</code>.</p>
<p><b>The wavelength consequence, which is often asked as a follow-up.</b> The frequency is unchanged when light enters the glass, so from <code>v = fλ</code> the wavelength must fall by the same factor. So the same light has a wavelength in glass that is <code>1/1.5</code> of its vacuum wavelength. That fact underlies the water-immersion question in module G of the curriculum.</p>`,
  trap: "Inverting the ratio. The refractive index is always greater than or equal to 1."
}

]);
