/* BPhO Round 0 — question bank, part 3 of 3.
   The expansion wave: 82 questions added across every module,
   weighted towards non-calculator ratio reasoning and multi-step
   chains. Answers are distributed across A–E.

   Note: unlike questions-1/2 the entries here carry no `trap`
   field. Nothing in the app reads it, and the misconception
   discussion lives in the worked solution instead.
*/

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([
/* ===================== MODULE A — toolkit ===================== */

{
  id: "A-11", module: "A", topic: "Ratio reasoning", diff: 2,
  q: "Body X has mass <code>m</code> and speed <code>2v</code>. Body Y has mass <code>4m</code> and speed <code>v</code>. What is the ratio of the kinetic energy of X to that of Y?",
  opts: ["1 : 4", "1 : 2", "2 : 1", "1 : 1", "4 : 1"],
  ans: 3,
  sol: `<p>Write both kinetic energies and divide. Nothing needs a value.</p>
<div class="formula">E_X = ½ m (2v)² = ½ m × 4v² = 2mv²
E_Y = ½ (4m) v² = 2mv²
E_X / E_Y = 1</div>
<p><b>Answer: D, 1 : 1.</b> The two are equal.</p>
<p><b>Why this is a ratio question and not a calculation.</b> The mass went up by
a factor of four and the speed down by a factor of two. But kinetic energy is
proportional to <i>mass</i> and to the <i>square</i> of speed, so the speed change
counts twice: <code>4 × (½)² = 4 × ¼ = 1</code>. The two effects cancel exactly.
Spotting that takes about ten seconds; substituting numbers takes a minute and
gains nothing.</p>
<p><b>The traps.</b> Option B, 1 : 2, is what you get by comparing masses only,
as if the speeds were equal. Option C, 2 : 1, is the same error the other way
round, from comparing speeds only. Option A, 1 : 4, uses the speed ratio as ½
without squaring it, and option E, 4 : 1, uses the mass ratio alone with the
squaring applied to the wrong factor. All four come from treating one of the two
factors as linear when one of them is not.</p>
<p><b>The general rule.</b> When a quantity depends on two variables, change one
at a time and multiply the factors. Kinetic energy is linear in mass and
quadratic in speed, so <code>E ∝ m v²</code> and the ratio is
<code>(m_X/m_Y) × (v_X/v_Y)²</code>.</p>`,
},
{
  id: "A-12", module: "A", topic: "Dimensional analysis", diff: 1,
  q: "Which of the following has the dimensions of power?",
  opts: ["force ÷ velocity", "force × time", "energy × time", "mass × velocity", "force × velocity"],
  ans: 4,
  sol: `<p>Power is energy per second. Work through it in base units and then match.</p>
<div class="formula">power = energy / time = M L² T⁻² / T = M L² T⁻³</div>
<p><b>Answer: E.</b> Force is <code>M L T⁻²</code> and velocity is
<code>L T⁻¹</code>, so their product is <code>M L² T⁻³</code> — power. This is
just <code>P = Fv</code>, which is the form worth remembering because it is one
step instead of three.</p>
<p><b>Where the others lead.</b> Option B, force × time, is
<code>M L T⁻¹</code> — an impulse. Option C, energy × time, is
<code>M L² T⁻¹</code>, which is an energy multiplied by a time and is not a
named quantity at all; dividing would have been right. Option D, mass × velocity,
is momentum, <code>M L T⁻¹</code>. Option A, force ÷ velocity, gives
<code>M T⁻¹</code>, which still carries no length and so cannot be a power.</p>
<p><b>The shortcut that settles these in seconds.</b> Power is a rate, so it must
carry <code>T⁻¹</code>. Of the five options, only A and C involve a time at all,
and C multiplies by time rather than dividing by it. That single observation
narrows five options to one without writing a single base unit down.</p>`,
},
{
  id: "A-13", module: "A", topic: "Estimation", diff: 2,
  q: "Roughly how many times does a human heart beat in a lifetime of 70 years? Take the resting rate as 70 beats per minute.",
  opts: ["3 × 10⁹", "3 × 10⁷", "3 × 10⁸", "3 × 10¹⁰", "3 × 10¹¹"],
  ans: 0,
  sol: `<p>Chain the conversions, rounding hard at every step.</p>
<div class="formula">70 /min × 60 /h ≈ 4 × 10³ per hour
× 24 ≈ 1 × 10⁵ per day
× 365 ≈ 4 × 10⁷ per year  (365 ≈ 3.65 × 10²)
× 70 years ≈ 3 × 10⁹</div>
<p><b>Answer: A, 3 × 10⁹.</b></p>
<p><b>Why rounding each step is safe.</b> Every option differs from the next by a
factor of ten, so you only need the answer to within a factor of three. Rounding
70 × 60 up to 4 × 10³ and 365 down to 3.65 × 10² each cost a few per cent, and the
errors partly cancel. That is the whole discipline of estimation questions: the
options tell you how precise you need to be, and here they tell you not to be.</p>
<p><b>The traps.</b> Option C, 3 × 10⁸, is what you get by losing a factor of ten
somewhere in the chain — usually by treating a day as 2.4 hours rather than 24.
Option B, 3 × 10⁷, is roughly one year's worth of beats: the answer you get by
forgetting the 70 years entirely. Options D and E are ten and a hundred times too
large.</p>
<p><b>An anchor worth keeping.</b> A year is about <code>π × 10⁷</code> seconds,
so a lifetime is about <code>2 × 10⁹</code> seconds. At roughly one beat per
second, that is about <code>2 × 10⁹</code> beats — the same answer by a completely
different route, and a useful check.</p>`,
},
{
  id: "A-14", module: "A", topic: "Ratio reasoning", diff: 1,
  q: "A force <code>F</code> spread over an area <code>A</code> produces a pressure <code>p</code>. What pressure is produced by a force <code>3F</code> spread over an area <code>A/3</code>?",
  opts: ["p/3", "3p", "6p", "p", "9p"],
  ans: 4,
  sol: `<p>Pressure is force divided by area. Apply both changes to the same
formula rather than trying to hold two ratios in your head.</p>
<div class="formula">p' = (3F) / (A/3) = 3F × 3/A = 9 F/A = 9p</div>
<p><b>Answer: E, 9p.</b></p>
<p><b>The one thing to be careful about.</b> Dividing by a third is the same as
multiplying by three, and that is where the marks are lost here. The force change
contributes a factor of 3 and the area change contributes <i>another</i> factor of
3, because the area is in the denominator. The factors multiply:
<code>3 × 3 = 9</code>.</p>
<p><b>The traps.</b> Option B, 3p, is what you get by noticing the force tripled
and stopping. Option D, p, would mean the two changes cancel, which would require
the area to have tripled as well rather than fallen to a third. Option A, p/3, is
the result of dividing by both factors instead of dividing by one and multiplying
by the other. Option C, 6p, comes from adding the factors instead of multiplying
them — a surprisingly common slip when the arithmetic is this easy.</p>
<p><b>The physical picture.</b> Three times the force pushed through one third of
the area is nine times the concentration. That is exactly why a drawing pin has a
broad head and a sharp point: the same force, concentrated a hundredfold.</p>`,
},
{
  id: "A-15", module: "A", topic: "Small-parameter approximations", diff: 2,
  q: "Use the binomial approximation to estimate <code>(0.98)⁵</code>.",
  opts: ["0.10", "0.98", "0.92", "0.99", "0.90"],
  ans: 4,
  sol: `<p>Rewrite it as <code>(1 + x)ⁿ</code> with a negative <code>x</code> and
apply <code>(1 + x)ⁿ ≈ 1 + nx</code>.</p>
<div class="formula">(0.98)⁵ = (1 − 0.02)⁵ ≈ 1 + 5(−0.02) = 1 − 0.10 = 0.90</div>
<p><b>Answer: E, 0.90.</b></p>
<p><b>How good is that?</b> The exact value is 0.9039, so the estimate is out by
about 0.4% — far better than the gap between neighbouring options, which is what
matters on a multiple-choice paper. The error is second order in <code>x</code>,
so it stays small precisely because <code>|x| = 0.02</code> is small.</p>
<p><b>Why the sign matters.</b> A number below one raised to a power gets
<i>smaller</i>, so the answer must be less than 0.98. That immediately rules out
option B. Writing the approximation as <code>1 − nx</code> when the bracket is
<code>(1 − x)</code> is the safe habit: keep the sign inside <code>x</code> and let
the formula do the work.</p>
<p><b>The traps.</b> Option C, 0.92, is <code>1 − 4 × 0.02</code> — a slip in
reading the exponent. Option D, 0.99, comes from applying the approximation as if
<code>n = ½</code>. Option A, 0.10, is the correction term reported as the answer,
which is the error of forgetting the leading 1.</p>`,
},
{
  id: "A-16", module: "A", topic: "Ratio reasoning", diff: 2,
  q: "A wire has resistance <code>R</code>. A second wire of the same material has twice the length and twice the diameter. What is its resistance?",
  opts: ["R/2", "R", "2R", "R/4", "4R"],
  ans: 0,
  sol: `<p>Resistance is proportional to length and inversely proportional to
cross-sectional area, and the area goes as the <i>square</i> of the diameter.</p>
<div class="formula">R = ρL/A     with A ∝ d²
L → 2L   (factor 2)
d → 2d  ⇒  A → 4A   (factor 4, and area is in the denominator)
R' = R × 2 / 4 = R/2</div>
<p><b>Answer: A, R/2.</b></p>
<p><b>The single most important step.</b> Doubling the diameter quadruples the
area, not doubles it. Forgetting that is the whole question: if you take the area
as doubling you get option B, R — unchanged — which is the most popular wrong
answer on this topic.</p>
<p><b>The traps.</b> Option C, 2R, is what you get from the length change alone,
ignoring the diameter. Option D, R/4, applies the factor of 4 from the diameter
but forgets the doubling in length. Option E, 4R, multiplies by both factors
instead of dividing by one of them.</p>
<p><b>A physical way to remember it.</b> A fatter wire is like a wider road: it
lets more current through, so less resistance. But it is the <i>area</i> that
matters, so doubling the width of the road opens four lanes, not two. That is why
mains cables are thick and fuse wires are thin.</p>`,
},
{
  id: "A-17", module: "A", topic: "Graph shape", diff: 2,
  q: "A capacitor is charged from a constant-voltage supply through a resistor. Which best describes the graph of charging current against time?",
  opts: ["A horizontal straight line", "A straight line falling to zero", "A curve falling from a maximum, steep at first, levelling towards zero", "A curve rising from zero towards a maximum", "A curve falling from a maximum, shallow at first, then steep"],
  ans: 2,
  sol: `<p>Think about the two ends of the graph and the direction of the
gradient, and the shape follows without any equation.</p>
<p><b>At t = 0.</b> The capacitor is uncharged, so there is no voltage across it
opposing the supply. The whole supply voltage sits across the resistor, so the
current starts at its maximum, <code>V/R</code>. That eliminates option D, which
starts at zero.</p>
<p><b>As t → ∞.</b> The capacitor charges to the supply voltage, the voltage
across the resistor falls to zero, and so does the current. The curve must
approach the time axis. That eliminates option A.</p>
<p><b>The gradient.</b> The more charge on the capacitor, the more it opposes the
supply, so the current falls fastest when the capacitor is emptiest — at the
start. The curve is steepest at t = 0 and gets shallower. That eliminates option E,
which has the gradient the wrong way round, and option B, whose constant gradient
would mean the opposition never changed.</p>
<p><b>Answer: C.</b> It is exponential decay,
<code>I = (V/R) e<sup>−t/RC</sup></code>, but the shape follows from the physics alone.</p>
<p><b>Why the reasoning beats the formula here.</b> A competition paper will often
give you a family of graphs differing only in starting value and curvature. Asking
three questions — where does it start, where does it end, and does the gradient
grow or shrink — answers all of them in about fifteen seconds and cannot be
misremembered under pressure.</p>`,
},
{
  id: "A-18", module: "A", topic: "Ratio reasoning", diff: 2,
  q: "The gravitational field strength at the surface of a planet of radius <code>R</code> is <code>g</code>. What is it at a distance of <code>2R</code> from the centre?",
  opts: ["2g", "g/2", "g", "g/4", "4g"],
  ans: 3,
  sol: `<p>The field falls off as the inverse square of the distance from the
centre, so doubling the distance quarters it.</p>
<div class="formula">g ∝ 1/r²
g' / g = (R / 2R)² = (½)² = ¼
g' = g/4</div>
<p><b>Answer: D, g/4.</b></p>
<p><b>Note the wording.</b> The question says <i>2R from the centre</i>, which is
one radius above the surface, not two radii above it. If it had meant a height of
2R above the surface the distance from the centre would be 3R and the answer would
be g/9. Reading whether a distance is measured from the centre or from the surface
is exactly the discrimination this topic is testing.</p>
<p><b>The traps.</b> Option B, g/2, is the linear guess — the answer you get by
treating the field as proportional to 1/r rather than 1/r². Option C, g, would
follow from thinking the field is uniform near a planet, which is only true close
to the surface. Options A and E put the ratio the wrong way up, as if the field
grew with distance.</p>
<p><b>What this is and is not.</b> This uses only the inverse-square behaviour,
which is fair game. If you find yourself writing <code>GMm/r²</code> with the
gravitational constant you have moved into field theory, which Round 0 keeps out
of scope — the ratio route never needs <code>G</code> or <code>M</code> at
all.</p>`,
},
{
  id: "A-19", module: "A", topic: "Order of magnitude", diff: 2,
  q: "Which of the following is the best estimate of the kinetic energy of a cyclist and bicycle, of total mass 80 kg, travelling at 10 m s⁻¹?",
  opts: ["4 × 10³ J", "4 × 10² J", "4 × 10⁴ J", "8 × 10³ J", "8 × 10² J"],
  ans: 0,
  sol: `<p>Substitute into <code>E = ½mv²</code> and keep the powers of ten in
view.</p>
<div class="formula">E = ½ × 80 × 10² = 40 × 100 = 4.0 × 10³ J</div>
<p><b>Answer: A, 4 × 10³ J</b> — four kilojoules.</p>
<p><b>The mental route.</b> <code>10² = 100</code>, and half of 80 is 40, so the
answer is <code>40 × 100</code>. Two easy steps, and there is no need to write
anything down.</p>
<p><b>A cross-check worth doing.</b> 4 kJ is about the energy released by dropping
an 80 kg mass through five metres, since <code>mgh = 80 × 10 × 5 = 4000 J</code>.
Cycling along at 10 m s⁻¹ carrying the energy of a five-metre drop feels about
right, and that everyday comparison is what lets you reject an answer that is out
by a factor of ten.</p>
<p><b>The traps.</b> Option D, 8 × 10³, is <code>mv²</code> with the half
forgotten — the single most common slip in this topic. Option B, 4 × 10², is what
you get by using <code>v = 10</code> but treating it as though it were not
squared. Option C, 4 × 10⁴, is a factor ten too large, from a slip in the powers
of ten. Option E combines both errors.</p>
<p><b>Why the half is not optional.</b> Kinetic energy is the area under a
momentum–velocity graph, and momentum grows linearly with speed, so the area is a
triangle — half the rectangle <code>mv × v</code>. The same factor of ½ appears in
elastic strain energy and capacitor energy, for exactly the same reason.</p>`,
},
{
  id: "A-20", module: "A", topic: "Ratio reasoning", diff: 2,
  q: "A spring requires work <code>W</code> to stretch it by an extension <code>x</code>. How much work is needed to stretch the same spring by <code>3x</code>?",
  opts: ["6W", "3W", "9W", "W/3", "27W"],
  ans: 2,
  sol: `<p>The energy stored in a spring goes as the <i>square</i> of the
extension, so tripling the extension multiplies the work by nine.</p>
<div class="formula">W = ½ k x²
W' / W = (3x / x)² = 9
W' = 9W</div>
<p><b>Answer: C, 9W.</b></p>
<p><b>Why it is quadratic and not linear.</b> Two things grow as you stretch
further: the distance you push, and the force you have to push with, since
<code>F = kx</code>. Tripling the extension triples both, and
<code>3 × 3 = 9</code>. That is the physical reason, and it is more reliable under
pressure than recalling the formula.</p>
<p><b>The traps.</b> Option B, 3W, is the linear guess — the answer you get by
treating the force as constant at its original value. It is by far the most
common wrong answer on spring-energy questions. Option A, 6W, comes from adding
the factors instead of multiplying them. Option E, 27W, cubes the ratio, which
would be right for a quantity going as <code>x³</code>. Option D, W/3, puts the
ratio the wrong way up.</p>
<p><b>The graph picture.</b> Force–extension is a straight line through the
origin, and the energy is the area under it — a triangle. Tripling the base
triples the height as well, and the area of a triangle scales as base × height,
so it grows ninefold. Sketching the triangle takes five seconds and settles
it.</p>`,
},

/* ===================== MODULE B — kinematics ===================== */

{
  id: "B-07", module: "B", topic: "Multi-phase motion", diff: 2,
  q: "A train accelerates uniformly from rest at <code>0.40 m s⁻²</code> for 30 s, travels at constant speed for 60 s, then decelerates uniformly to rest in 20 s. What is the total distance travelled?",
  opts: ["1260 m", "900 m", "720 m", "1020 m", "540 m"],
  ans: 3,
  sol: `<p>Three phases. Use the velocity–time graph: each phase is a shape whose
area is the distance.</p>
<div class="formula">Phase 1 (triangle):  v = 0.40 × 30 = 12 m s⁻¹
                     s₁ = ½ × 30 × 12 = 180 m
Phase 2 (rectangle): s₂ = 12 × 60 = 720 m
Phase 3 (triangle):  s₃ = ½ × 20 × 12 = 120 m
Total = 180 + 720 + 120 = 1020 m</div>
<p><b>Answer: D, 1020 m.</b></p>
<p><b>The linking quantity.</b> The speed at the end of phase 1 — 12 m s⁻¹ — is
the speed used throughout phase 2 and the starting speed of phase 3. Computing it
once and reusing it is the whole trick, and forgetting it is what makes
multi-phase questions feel harder than they are.</p>
<p><b>The traps.</b> Option B, 900 m, drops one of the two triangles. Option C,
720 m, counts only the constant-speed phase, ignoring both ramps entirely — the
commonest structural error. Option A, 1260 m, treats the whole 110 s as if the
train were at 12 m s⁻¹ throughout. Option E, 540 m, is a slip in the triangle
areas.</p>
<p><b>Why the graph beats suvat here.</b> Three phases means three equations and
two shared quantities if you do it algebraically. The graph turns each phase into
a shape you can compute in your head, and the total is a single addition. Sketch
it every time.</p>`,
},
{
  id: "B-08", module: "B", topic: "Ratio reasoning", diff: 1,
  q: "Two balls are released from rest at the same instant, one from height <code>h</code> and one from height <code>4h</code>. What is the ratio of their times of fall?",
  opts: ["1 : √2", "1 : 4", "1 : 16", "2 : 1", "1 : 2"],
  ans: 4,
  sol: `<p>For free fall from rest, <code>s = ½gt²</code>, so
<code>t ∝ √s</code>. The time goes as the square root of the height, not as the
height.</p>
<div class="formula">t₁ / t₂ = √(h / 4h) = √(1/4) = ½
so t₁ : t₂ = 1 : 2</div>
<p><b>Answer: E, 1 : 2.</b> The ball from four times the height takes twice as
long.</p>
<p><b>Why the square root appears.</b> The ball is accelerating, so it covers
successive equal distances in ever-shorter times. Quadrupling the distance does
not quadruple the time, because the object is moving faster for most of the extra
distance. That is the physical content, and it is the same square-root behaviour
as in the braking-distance questions — reversed.</p>
<p><b>The traps.</b> Option B, 1 : 4, is the linear guess, treating time as
proportional to height. Option C, 1 : 16, squares the ratio instead of taking its
square root. Option D, 2 : 1, has the ratio upside down. Option A, 1 : √2, is what
you get if you halve the height rather than quadruple it.</p>
<p><b>The cross-check.</b> From <code>h</code> the fall takes <code>t</code>; from
<code>4h</code> it takes <code>2t</code>, and in twice the time at the same
acceleration the ball reaches twice the speed — so it has four times the kinetic
energy, which is exactly <code>mg(4h)</code> against <code>mgh</code>. The energy
and the kinematics agree.</p>`,
},
{
  id: "B-09", module: "B", topic: "Projectile motion", diff: 2,
  q: "A projectile is launched at speed <code>u</code> on level ground. Two launch angles give the same range. If one is 25°, what is the other?",
  opts: ["50°", "65°", "75°", "155°", "115°"],
  ans: 1,
  sol: `<p>The range is <code>R = u² sin 2θ / g</code>. The sine is unchanged when
its argument is replaced by <code>180° −</code> that argument, so two angles give
the same range whenever they add to 45° in the doubled angle — that is, whenever
the angles themselves add to 90°.</p>
<div class="formula">θ₁ + θ₂ = 90°
θ₂ = 90° − 25° = 65°</div>
<p><b>Answer: B, 65°.</b></p>
<p><b>Why complementary angles give the same range.</b> A low angle gives a short
flight time but a large horizontal speed; a high angle gives a long flight but a
small horizontal speed. At complementary angles the two effects trade off exactly,
so the product — the range — is the same. One goes flat and fast, the other high
and slow, and they land in the same place.</p>
<p><b>What is not the same.</b> The two trajectories have very different flight
times and very different maximum heights. A follow-up question will usually ask
about one of those precisely because they differ: the 65° launch stays up far
longer and goes much higher.</p>
<p><b>The traps.</b> Option A, 50°, doubles the angle. Option C, 75°, is the
complement of 15° rather than 25°. Option D, 155°, mistakenly complements to 180°
instead of 90°, and option E, 115°, is 90° + 25° instead of 90° − 25°.</p>
<p><b>The maximum-range fact worth knowing.</b> The range is greatest when
<code>sin 2θ = 1</code>, that is at <code>θ = 45°</code>, where the two
complementary angles coincide. Every other range is achieved twice.</p>`,
},
{
  id: "B-10", module: "B", topic: "Multi-phase motion", diff: 3,
  q: "A car travels the first half of a journey at 20 m s⁻¹ and the second half at 30 m s⁻¹. What is its average speed over the whole journey?",
  opts: ["26 m s⁻¹", "25 m s⁻¹", "24 m s⁻¹", "20 m s⁻¹", "30 m s⁻¹"],
  ans: 2,
  sol: `<p>Average speed is total distance over total time — never the average of
the speeds. Let the total distance be <code>2d</code>, so each half is
<code>d</code>.</p>
<div class="formula">t₁ = d/20      t₂ = d/30
t_total = d/20 + d/30 = (3d + 2d)/60 = 5d/60 = d/12
v_avg = 2d / (d/12) = 24 m s⁻¹</div>
<p><b>Answer: C, 24 m s⁻¹.</b></p>
<p><b>Why the naive average is wrong.</b> The car spends longer on the slow half
than on the fast half, so the slow speed gets more weight. The true average is
therefore below the arithmetic mean of 25 — and it is always below it for any two
different speeds over equal distances.</p>
<p><b>The general result, worth memorising.</b> For two equal <i>distances</i> the
average speed is the harmonic mean,
<code>2v₁v₂/(v₁ + v₂) = 2 × 20 × 30 / 50 = 24</code>. For two equal <i>times</i> it
would be the arithmetic mean, 25. Which mean applies depends on what is held
equal, and a question will often test exactly that distinction.</p>
<p><b>The traps.</b> Option B, 25 m s⁻¹, is the arithmetic mean and is the single
most common wrong answer. Option A, 26, is a guess in the wrong direction. Option
D, 20, and option E, 30, are the two individual speeds, which would only be the
average if one of the halves took no time at all.</p>`,
},
{
  id: "B-11", module: "B", topic: "Ratio reasoning", diff: 1,
  q: "A car's braking distance from speed <code>v</code> is <code>d</code>. With the same braking force, what is the braking distance from speed <code>3v</code>?",
  opts: ["9d", "3d", "6d", "d/3", "27d"],
  ans: 0,
  sol: `<p>Set the work done by the brakes equal to the kinetic energy removed
and read off the proportionality.</p>
<div class="formula">F d = ½ m v²   ⇒   d = m v² / (2F)
d ∝ v²
d' / d = (3v / v)² = 9
d' = 9d</div>
<p><b>Answer: A, 9d.</b></p>
<p><b>Why it matters far beyond the exam.</b> Tripling your speed makes your
stopping distance nine times longer. That is why a 30 km/h zone and a 90 km/h zone
are not three times apart in risk but nine times apart, and why speed limits are
set the way they are. It is the same quadratic dependence as in kinetic energy,
because it <i>is</i> kinetic energy.</p>
<p><b>The traps.</b> Option B, 3d, is the linear guess — the most common wrong
answer, and the one the question exists to catch. Option C, 6d, adds the factors
rather than multiplying them. Option E, 27d, cubes the ratio. Option D, d/3, puts
it upside down.</p>
<p><b>What never needed a value.</b> The mass, the braking force and the original
speed all cancelled or stayed constant. That is the signature of a ratio question:
write the relationship, identify what is fixed, take the ratio. Fifteen seconds,
no numbers.</p>`,
},
{
  id: "B-12", module: "B", topic: "Relative motion", diff: 2,
  q: "Two cars travel in the same direction along a straight road at 25 m s⁻¹ and 15 m s⁻¹. The faster car is 200 m behind. How long does it take to draw level?",
  opts: ["8 s", "20 s", "13 s", "5 s", "50 s"],
  ans: 1,
  sol: `<p>In a chase the gap closes at the <i>difference</i> of the speeds, not
the sum.</p>
<div class="formula">closing speed = 25 − 15 = 10 m s⁻¹
t = 200 / 10 = 20 s</div>
<p><b>Answer: B, 20 s.</b></p>
<p><b>Sum or difference?</b> That single decision is the whole question. If the
cars were approaching head-on the gap would shrink at 40 m s⁻¹ and the answer
would be 5 s — option D, present deliberately. Reading whether the motion is
<i>towards</i> or <i>alongside</i> is what you are being tested on, and it is
worth underlining the words in the question.</p>
<p><b>The formal statement.</b> Relative velocity is vector subtraction,
<code>v_AB = v_A − v_B</code>. For motion in the same direction the two vectors
are parallel, so the subtraction gives the difference of the magnitudes. For
head-on motion they are antiparallel, so it gives the sum. Same formula, opposite
arithmetic, purely because of the geometry.</p>
<p><b>The traps.</b> Option A, 8 s, uses 200/25 — the faster car's speed alone, as
if the other were stationary. Option C, 13 s, is 200/15. Both ignore one vehicle.
Option E, 50 s, is what you get from a slip in the division.</p>`,
},
{
  id: "B-13", module: "B", topic: "Multi-phase motion", diff: 2,
  q: "A stone is thrown vertically upward at 20 m s⁻¹. Ignoring air resistance and taking <code>g = 10 m s⁻²</code>, how high does it rise, and how long is it in the air before returning to the launch height?",
  opts: ["20 m and 2.0 s", "20 m and 4.0 s", "40 m and 4.0 s", "10 m and 2.0 s", "40 m and 8.0 s"],
  ans: 1,
  sol: `<p>Two separate questions. Do the height first, then the time.</p>
<div class="formula">At the top v = 0, so  0 = u² − 2gh
h = u²/2g = 400/20 = 20 m

Time to the top:  v = u − gt  ⇒  0 = 20 − 10t  ⇒  t = 2.0 s
The descent is the mirror image, so total time = 4.0 s</div>
<p><b>Answer: B, 20 m and 4.0 s.</b></p>
<p><b>The symmetry, which halves the work.</b> On the way up the stone decelerates
from 20 to 0; on the way down it accelerates from 0 back to 20 over the same
distance. The two halves take equal times and the stone lands at the speed it was
thrown. So compute the ascent and double it — there is no need to solve a second
quadratic.</p>
<p><b>The traps.</b> Option A, 20 m and 2.0 s, is the commonest error: it gives
the time to the <i>top</i> rather than the total flight time. Option C, 40 m,
comes from <code>u²/g</code> with the factor of 2 dropped. Option D has both
errors. Option E, 40 m and 8.0 s, doubles each correct value.</p>
<p><b>The check that costs nothing.</b> The average speed on the way up is
<code>(20 + 0)/2 = 10 m s⁻¹</code>, and over 2.0 s that gives 20 m ✓. Using the
average speed is faster than the equation and confirms it independently.</p>`,
},
{
  id: "B-14", module: "B", topic: "Graphs", diff: 2,
  q: "The velocity–time graph of a body is a straight line rising from 0 to 8 m s⁻¹ over 4 s, then a straight line falling back to 0 over the next 4 s. What is the total displacement?",
  opts: ["48 m", "64 m", "16 m", "32 m", "24 m"],
  ans: 3,
  sol: `<p>Displacement is the area under the velocity–time graph. The shape is a
triangle with base 8 s and height 8 m s⁻¹.</p>
<div class="formula">s = ½ × base × height = ½ × 8 × 8 = 32 m</div>
<p><b>Answer: D, 32 m.</b></p>
<p><b>Alternatively, two triangles.</b> The first 4 s is a triangle of
<code>½ × 4 × 8 = 16 m</code> and the second is the same, giving 32 m. Either way
works; treating it as one big triangle is one multiplication instead of two.</p>
<p><b>The traps.</b> Option B, 64 m, is what you get from 8 × 8 — the rectangle,
as if the body had travelled at the maximum speed the whole time. That is the
single most common error on area-under-a-graph questions. Option C, 16 m, is one
of the two halves, from stopping after the first triangle. Option A, 48 m, is a
rectangle of half the height. Option E, 24 m, is a slip in the multiplication.</p>
<p><b>Why the area is the displacement.</b> For constant velocity, displacement is
<code>v × t</code>, which is exactly the area of a rectangle of height
<code>v</code> and width <code>t</code>. A varying velocity is just many narrow
rectangles stacked up, so the total area still gives the displacement. The same
argument makes the area under a force–time graph the impulse and the area under a
force–distance graph the work — one idea, three topics.</p>`,
},

/* ===================== MODULE C — forces and momentum ===================== */

{
  id: "C-10", module: "C", topic: "Moments", diff: 2,
  q: `<p>A uniform beam of weight 100 N and length 4.0 m rests on supports at each end. A load of 300 N is placed 1.0 m from the left support. What is the reaction at the right support?</p>
<figure class="fig">
<svg viewBox="0 0 480 236" role="img" aria-label="A uniform beam 4 metres long on supports at each end, carrying its own 100 newton weight at the centre and a 300 newton load 1 metre from the left support.">
<defs>
<marker id="bm-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
<path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/>
</marker>
<marker id="bm-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto">
<path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/>
</marker>
</defs>
<text x="240" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">A uniform beam on two end supports</text>

<line x1="160" y1="52" x2="160" y2="110" stroke="#b3352f" stroke-width="2.4" marker-end="url(#bm-ar)"/>
<text x="160" y="44" text-anchor="middle" font-size="12" font-weight="600" fill="#b3352f">300 N</text>
<line x1="240" y1="86" x2="240" y2="110" stroke="#b3352f" stroke-width="2.4" marker-end="url(#bm-ar)"/>
<text x="240" y="78" text-anchor="middle" font-size="12" font-weight="600" fill="#b3352f">100 N</text>

<rect x="80" y="116" width="320" height="12" fill="#e8eefc" stroke="#1f2937" stroke-width="2"/>
<polygon points="66,128 94,128 80,152" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<polygon points="386,128 414,128 400,152" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="58" y1="152" x2="422" y2="152" stroke="#cbd2dd" stroke-width="1.6"/>
<text x="80" y="172" text-anchor="middle" font-size="12" font-weight="600" fill="#1f7a53">R_L</text>
<text x="400" y="172" text-anchor="middle" font-size="12" font-weight="600" fill="#1f7a53">R_R</text>

<line x1="80" y1="192" x2="160" y2="192" stroke="#7b8494" stroke-width="1.5" marker-start="url(#bm-dim)" marker-end="url(#bm-dim)"/>
<text x="120" y="186" text-anchor="middle" font-size="11.5" font-weight="600" fill="#2f5fd0">1.0 m</text>
<line x1="80" y1="216" x2="400" y2="216" stroke="#7b8494" stroke-width="1.5" marker-start="url(#bm-dim)" marker-end="url(#bm-dim)"/>
<text x="240" y="210" text-anchor="middle" font-size="11.5" font-weight="600" fill="#2f5fd0">4.0 m</text>
</svg>
</figure>`,
  opts: ["200 N", "125 N", "150 N", "75 N", "400 N"],
  ans: 1,
  sol: `<p>Take moments about the left support so that the left reaction has no
moment arm and drops out.</p>
<div class="formula">clockwise: beam  100 × 2.0 = 200 N m
           load   300 × 1.0 = 300 N m
           total clockwise = 500 N m
anticlockwise: R × 4.0
4.0 R = 500  ⇒  R = 125 N</div>
<p><b>Answer: B, 125 N.</b></p>
<p>Now confirm it with vertical equilibrium before trusting it.</p>
<div class="formula">total downward = 100 + 300 = 400 N
R_left = 400 − 125 = 275 N
check about the right support: 275 × 4.0 = 1100
                               100 × 2.0 + 300 × 3.0 = 200 + 900 = 1100 ✓</div>
<p><b>The traps.</b> Option A, 200 N, is what you get by putting the 300 N load at
the midpoint instead of 1.0 m from the end: <code>(300 × 2.0 + 100 × 2.0)/4.0</code>.
Option C, 150 N, is the load at the midpoint with the beam's own weight forgotten.
Option D, 75 N, forgets the beam entirely: <code>300 × 1.0/4.0</code>. Option E,
400 N, is the total load applied at one support — the error of forgetting that two
supports share it.</p>
<p><b>The discipline that prevents the standard error.</b> Always take moments
about the support whose reaction you <i>don't</i> want: it makes that force
vanish from the equation, so you solve for one unknown in one line. Then confirm
with vertical equilibrium, and if you have time, re-take moments about the other
support. Two agreeing routes is worth more than one careful one.</p>`,
},
{
  id: "C-11", module: "C", topic: "Momentum", diff: 1,
  q: "A body of mass <code>2m</code> moving at <code>3v</code> collides head-on with a stationary body of mass <code>m</code>. They stick together. What is their common speed?",
  opts: ["3v", "2v", "1.5v", "6v", "v"],
  ans: 1,
  sol: `<p>Momentum is conserved. The mass <code>m</code> and the speed
<code>v</code> both cancel, so this never needs a number.</p>
<div class="formula">before: p = (2m)(3v) + m × 0 = 6mv
after:  p = (2m + m) V = 3m V
3mV = 6mv  ⇒  V = 2v</div>
<p><b>Answer: B, 2v.</b></p>
<p><b>The sanity check.</b> The combined mass is three times the stationary body
and half the total mass came from the moving one, so the speed must fall — 2v is
below the original 3v ✓. Anything higher than 3v would mean the collision added
momentum, which is impossible.</p>
<p><b>The traps.</b> Option A, 3v, conserves speed rather than momentum. Option C,
1.5v, is <code>6mv / 4m</code> — using a total mass of 4m by miscounting. Option
D, 6v, is the momentum reported as a speed, with the mass division forgotten.
Option E, v, halves it once more.</p>
<p><b>The energy check, which tells you what kind of collision this is.</b>
Before: <code>½(2m)(3v)² = 9mv²</code>. After:
<code>½(3m)(2v)² = 6mv²</code>. A third of the kinetic energy has gone, as it
must when the bodies stick together. Momentum is conserved in every collision;
kinetic energy is not.</p>`,
},
{
  id: "C-12", module: "C", topic: "Impulse", diff: 2,
  q: `<p>A force on a body rises uniformly from 0 to 12 N in 2.0 s, stays at 12 N for 3.0 s, then falls uniformly to 0 in 1.0 s. What is the total impulse?</p>
<figure class="fig">
<svg viewBox="0 0 480 240" role="img" aria-label="A trapezium-shaped force-time graph: rising to 12 newtons in 2 seconds, flat for 3 seconds, then falling to zero in 1 second.">
<text x="240" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Force–time graph for the impulse</text>
<line x1="90" y1="50" x2="90" y2="196" stroke="#1f2937" stroke-width="2"/>
<line x1="90" y1="190" x2="446" y2="190" stroke="#1f2937" stroke-width="2"/>
<polygon points="446,190 436,185 436,195" fill="#1f2937"/>
<polygon points="90,50 85,60 95,60" fill="#1f2937"/>
<polygon points="90,190 203,70 373,70 430,190" fill="#e8eefc" stroke="#2f5fd0" stroke-width="2.5"/>
<line x1="203" y1="70" x2="86" y2="70" stroke="#cbd2dd" stroke-width="1.4" stroke-dasharray="4 4"/>
<line x1="203" y1="70" x2="203" y2="190" stroke="#cbd2dd" stroke-width="1.4" stroke-dasharray="4 4"/>
<line x1="373" y1="70" x2="373" y2="190" stroke="#cbd2dd" stroke-width="1.4" stroke-dasharray="4 4"/>
<text x="82" y="74" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">12</text>
<text x="90" y="208" text-anchor="middle" font-size="12" fill="#4a5262">0</text>
<text x="203" y="208" text-anchor="middle" font-size="12" fill="#4a5262">2.0</text>
<text x="373" y="208" text-anchor="middle" font-size="12" fill="#4a5262">5.0</text>
<text x="430" y="208" text-anchor="middle" font-size="12" fill="#4a5262">6.0</text>
<text x="82" y="44" text-anchor="end" font-size="12.5" fill="#4a5262">F / N</text>
<text x="438" y="212" text-anchor="end" font-size="12.5" fill="#4a5262">t / s</text>
<text x="288" y="150" font-size="12" fill="#4a5262">area = impulse</text>
</svg>
</figure>`,
  opts: ["48 N s", "54 N s", "36 N s", "72 N s", "24 N s"],
  ans: 1,
  sol: `<p>The impulse is the area under the force–time graph. The shape is a
trapezium: split it into the rectangle and the two triangles, or use the average
force.</p>
<div class="formula">trapezium: parallel sides 3.0 s and 6.0 s, height 12 N
area = ½(3.0 + 6.0) × 12 = ½ × 9.0 × 12 = 54 N s</div>
<p><b>Answer: B, 54 N s.</b></p>
<p><b>Check it the other way.</b> The average force over the whole 6.0 s is not
12 N but <code>54 / 6.0 = 9.0 N</code>, because of the ramps at each end. Then
impulse = average force × time = <code>9.0 × 6.0 = 54 N s</code> ✓. Two routes,
one answer.</p>
<p><b>The traps.</b> Option D, 72 N s, is <code>12 × 6.0</code> — treating the
force as constant at its peak and ignoring both ramps. Option A, 48 N s, is
<code>12 × 4.0</code>, which counts only part of the shape. Option C, 36 N s, uses
the 3.0 s plateau alone, forgetting the ramps on either side. Option E, 24 N s, is
one triangle only.</p>
<p><b>How to read these quickly.</b> Sketch the graph and name the shape. A
trapezium is a rectangle plus two triangles, and <code>½(a + b)h</code> is usually
one line of arithmetic. The alternative — integrating — is never needed on a
multiple-choice paper, and recognising the shape is faster than either.</p>`,
},
{
  id: "C-13", module: "C", topic: "Connected bodies", diff: 3,
  q: `<p>A 3.0 kg block on a smooth horizontal table is connected by a light string over a pulley to a hanging 1.0 kg mass. What is the acceleration of the system? Use <code>g = 10 m s⁻²</code>.</p>
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="A 3 kilogram block on a smooth table connected by a string over a pulley at the table edge to a hanging 1 kilogram mass.">
<defs>
<marker id="cb-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
<path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/>
</marker>
<marker id="cb-wt" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
<path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/>
</marker>
</defs>
<text x="240" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Block, string, pulley, hanging mass</text>

<rect x="50" y="140" width="270" height="7" fill="#cbd2dd" stroke="#cbd2dd"/>
<line x1="50" y1="140" x2="320" y2="140" stroke="#1f2937" stroke-width="2"/>
<text x="150" y="170" text-anchor="middle" font-size="11.5" fill="#7b8494">smooth table</text>

<rect x="120" y="108" width="70" height="32" fill="#e8eefc" stroke="#1f2937" stroke-width="2"/>
<text x="155" y="129" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">3.0 kg</text>

<line x1="190" y1="140" x2="306" y2="140" stroke="#a8641a" stroke-width="2"/>
<circle cx="320" cy="140" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<circle cx="320" cy="140" r="2.6" fill="#1f2937"/>
<line x1="334" y1="140" x2="334" y2="196" stroke="#a8641a" stroke-width="2"/>
<text x="296" y="176" text-anchor="end" font-size="11.5" fill="#4a5262">pulley</text>

<rect x="312" y="196" width="44" height="40" fill="#f1f3f7" stroke="#1f2937" stroke-width="2"/>
<text x="334" y="221" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">1.0 kg</text>
<line x1="334" y1="236" x2="334" y2="266" stroke="#b3352f" stroke-width="2.4" marker-end="url(#cb-wt)"/>
<text x="346" y="260" font-size="11.5" font-weight="600" fill="#b3352f">mg</text>

<line x1="206" y1="120" x2="252" y2="120" stroke="#2f5fd0" stroke-width="2.4" marker-end="url(#cb-ar)"/>
<text x="229" y="112" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">a</text>

<text x="282" y="130" text-anchor="middle" font-size="12" font-weight="600" fill="#a8641a">T</text>
<text x="348" y="172" font-size="12" font-weight="600" fill="#a8641a">T</text>

<text x="240" y="290" text-anchor="middle" font-size="11.5" fill="#7b8494">the string is light and the pulley is frictionless</text>
</svg>
</figure>`,
  opts: ["10 m s⁻²", "3.3 m s⁻²", "5.0 m s⁻²", "2.5 m s⁻²", "1.0 m s⁻²"],
  ans: 3,
  sol: `<p>Treat the two masses as one system. The only external force driving the
motion is the weight of the hanging mass; the tension is internal and cancels, and
the table's normal force does no work along the motion.</p>
<div class="formula">driving force = mg = 1.0 × 10 = 10 N
mass accelerated = 3.0 + 1.0 = 4.0 kg
a = 10 / 4.0 = 2.5 m s⁻²</div>
<p><b>Answer: D, 2.5 m s⁻².</b></p>
<p><b>Why the whole-system route is faster.</b> Writing Newton's second law for
each mass gives two simultaneous equations in the tension and the acceleration.
Treating them as one body makes the tension an internal force that cancels, leaving
one equation in one unknown. That is strictly less work and there is less to get
wrong.</p>
<p><b>The limiting checks.</b> If the 3.0 kg block were massless the hanging mass
would fall freely at 10 m s⁻² ✓ (the formula gives 10/1.0). If the hanging mass
were tiny the acceleration would be near zero ✓. Both limits behave correctly,
which confirms the structure.</p>
<p><b>The traps.</b> Option B, 3.3 m s⁻², is <code>10/3.0</code> — using only the
block on the table as the accelerated mass. Option C, 5.0 m s⁻², uses the
difference of the weights, which would be right only if both masses hung. Option
A, 10 m s⁻², is free fall. Option E, 1.0 m s⁻², is a slip in the division.</p>`,
},
{
  id: "C-14", module: "C", topic: "Work", diff: 2,
  q: "A force of 50 N pulls a 4.0 kg block 6.0 m up a rough slope inclined at 30° to the horizontal. The friction force is 10 N. How much work is done against friction, and what is the net work done on the block? Use <code>g = 10 m s⁻²</code>.",
  opts: ["60 J and 120 J", "60 J and 300 J", "120 J and 180 J", "300 J and 60 J", "60 J and 240 J"],
  ans: 0,
  sol: `<p>Two questions, and each needs its own force. Take care over which force
does which work.</p>
<div class="formula">Work against friction = 10 × 6.0 = 60 J

Component of weight down the slope:
  mg sin 30° = 4.0 × 10 × 0.50 = 20 N
Net work = (applied − friction − weight component) × distance
         = (50 − 10 − 20) × 6.0 = 20 × 6.0 = 120 J</div>
<p><b>Answer: A, 60 J and 120 J.</b></p>
<p><b>The distinction that matters.</b> "Work done against friction" is
<code>10 × 6.0</code> — just the friction force over the distance. "Net work" is
the resultant force over the distance, and the resultant must include the
down-slope component of the weight as well. Conflating the two is the usual way
this question is lost.</p>
<p><b>What the net work becomes.</b> By the work–energy theorem the net work is
the change in kinetic energy, so the block gains 120 J of kinetic energy. The
applied force supplied <code>50 × 6.0 = 300 J</code>, of which 60 J went to
friction and <code>20 × 6.0 = 120 J</code> went into gravitational potential
energy — and <code>300 = 60 + 120 + 120</code> ✓. Tracking the energy account in
full is the reliable habit.</p>
<p><b>The traps.</b> Option B, 60 J and 300 J, gives the total work done by the
applied force rather than the net work. Option C doubles the friction. Option D
swaps the two answers.</p>`,
},
{
  id: "C-15", module: "C", topic: "Power", diff: 2,
  q: "A car of mass 1000 kg climbs a hill at a steady 15 m s⁻¹. The hill rises 1 m for every 10 m along the slope, and the total resistive force is 500 N. What power must the engine deliver? Use <code>g = 10 m s⁻²</code>.",
  opts: ["15 kW", "7.5 kW", "22.5 kW", "30 kW", "150 kW"],
  ans: 2,
  sol: `<p>At steady speed there is no acceleration, so the driving force exactly
balances everything opposing it. Find that force, then use <code>P = Fv</code>.</p>
<div class="formula">gravity component: mg sin θ = 1000 × 10 × (1/10) = 1000 N
resistance:                                              500 N
driving force = 1000 + 500 = 1500 N
P = Fv = 1500 × 15 = 22 500 W = 22.5 kW</div>
<p><b>Answer: C, 22.5 kW.</b></p>
<p><b>The gradient, read carefully.</b> "Rises 1 m for every 10 m along the
slope" means <code>sin θ = 1/10</code> — the distance is measured along the
slope, not horizontally. Had it said 1 in 10 horizontally, you would need
<code>tan θ = 0.1</code> and then <code>sin θ</code>, which is very slightly
different. At this gradient the difference is negligible, but a steeper question
would separate the two readings, and that is exactly what a competition paper
likes.</p>
<p><b>Why the mass matters here but not on the flat.</b> On level ground at
constant speed the mass is a decoy. On a hill it is not: the engine has to lift
the weight as well as overcome drag, so the gravitational term is the larger of
the two contributions.</p>
<p><b>The traps.</b> Option B, 7.5 kW, is the power against resistance alone,
forgetting the climb. Option A, 15 kW, is <code>mg sin θ × v</code> with the
resistance dropped. Option D, 30 kW, doubles it. Option E, 150 kW, is
<code>Fv</code> with a factor-of-ten slip.</p>`,
},
{
  id: "C-16", module: "C", topic: "Momentum", diff: 2,
  q: "In a perfectly elastic head-on collision, a body of mass <code>m</code> moving at <code>u</code> strikes a stationary body of mass <code>m</code>. What happens?",
  opts: ["The first rebounds at u/2 and the second moves off at u/2", "Both move off together at u/2", "The first stops and the second moves off at u", "Both move off at u", "The first continues at u and the second stays at rest"],
  ans: 2,
  sol: `<p>Equal masses in a one-dimensional elastic collision swap velocities.
That is the cleanest way to state the result, and it is worth knowing as a fact
rather than deriving it each time.</p>
<div class="formula">momentum:  mu = mv₁ + mv₂
elastic (KE conserved):  u² = v₁² + v₂²
These are satisfied by v₁ = 0, v₂ = u  ✓</div>
<p><b>Answer: C.</b> The incoming body stops dead and the target moves off with
the original speed.</p>
<p><b>Check both conservation laws explicitly.</b> Momentum:
<code>mu = 0 + mu</code> ✓. Kinetic energy:
<code>½mu² = 0 + ½mu²</code> ✓. Both hold, which is what makes this the unique
physical solution.</p>
<p><b>The traps.</b> Option B is the <i>inelastic</i> answer — the result if the
two stuck together, which conserves momentum but throws away half the kinetic
energy. Option A conserves momentum and looks plausible but gives a total kinetic
energy of only <code>¼mu²</code>, which is impossible for an elastic collision.
Option D doubles the momentum. Option E is what happens if nothing collides at
all.</p>
<p><b>Where you have seen this.</b> It is the Newton's cradle. Lift one ball and
one ball leaves at the far end; the middle balls barely move. That is equal masses
swapping velocities, and it is the reason the demo works. A competition question
will often dress this up as a collision between particles or trolleys and expect
you to recognise the swap immediately.</p>`,
},
{
  id: "C-17", module: "C", topic: "Equilibrium", diff: 2,
  q: `<p>A body is held in equilibrium by three forces: 8 N horizontally to the right, 6 N vertically upward, and a third force F. What is the magnitude of F?</p>
<figure class="fig">
<svg viewBox="0 0 460 250" role="img" aria-label="Two perpendicular forces of 8 newtons to the right and 6 newtons upward, their resultant, and the third force needed for equilibrium.">
<text x="230" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Three forces in equilibrium</text>
<line x1="170" y1="150" x2="310" y2="150" stroke="#2f5fd0" stroke-width="3" marker-end="url(#cq17-b)"/>
<line x1="170" y1="150" x2="170" y2="60" stroke="#1f7a53" stroke-width="3" marker-end="url(#cq17-g)"/>
<line x1="170" y1="150" x2="61" y2="220" stroke="#b3352f" stroke-width="3" marker-end="url(#cq17-r)"/>
<line x1="170" y1="150" x2="310" y2="60" stroke="#a8641a" stroke-width="2" stroke-dasharray="6 4"/>
<polyline points="170,134 186,134 186,150" fill="none" stroke="#7b8494" stroke-width="1.5"/>
<text x="240" y="142" font-size="12.5" font-weight="600" fill="#2f5fd0">8 N</text>
<text x="160" y="112" text-anchor="end" font-size="12.5" font-weight="600" fill="#1f7a53">6 N</text>
<text x="320" y="56" font-size="12" fill="#a8641a">resultant = 10 N</text>
<text x="52" y="236" font-size="12.5" font-weight="600" fill="#b3352f">F = ?</text>
<text x="184" y="176" font-size="12" fill="#4a5262">body</text>
<circle cx="170" cy="150" r="4" fill="#1f2937"/>
<defs>
<marker id="cq17-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2f5fd0"/></marker>
<marker id="cq17-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1f7a53"/></marker>
<marker id="cq17-r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#b3352f"/></marker>
</defs>
</svg>
</figure>`,
  opts: ["48 N", "14 N", "2 N", "10 N", "100 N"],
  ans: 3,
  sol: `<p>For equilibrium the resultant is zero, so F must exactly cancel the
other two. The resultant of 8 N and 6 N is found by Pythagoras because they are
perpendicular.</p>
<div class="formula">resultant of the first two = √(8² + 6²) = √(64 + 36) = √100 = 10 N</div>
<p>So F is 10 N, directed opposite to that resultant.</p>
<p><b>Answer: D, 10 N.</b></p>
<p><b>Recognise the triple.</b> 6–8–10 is just the 3–4–5 triangle doubled. Seeing
it immediately saves the arithmetic and is worth practising, because these triples
turn up constantly in vector questions.</p>
<p><b>The traps.</b> Option B, 14 N, adds the two forces as if they were parallel,
which would only be right if they acted in the same direction. Option C, 2 N,
subtracts them, which would be right if they were antiparallel. Option A, 48 N,
multiplies instead of combining as vectors. Option E, 100 N, is the sum of the
squares reported without taking the square root — the classic slip.</p>
<p><b>The general statement.</b> Three forces in equilibrium form a closed
triangle when placed head to tail. Equivalently, any one of them is equal and
opposite to the resultant of the other two. Both phrasings are useful: the
triangle is better for drawing, the resultant is better for calculation.</p>`,
},
{
  id: "C-18", module: "C", topic: "Centre of mass", diff: 2,
  q: `<p>Three masses, 1.0 kg, 2.0 kg and 3.0 kg, sit on a line at x = 0, x = 2.0 m and x = 5.0 m. Where is their centre of mass?</p>
<figure class="fig">
<svg viewBox="0 0 480 232" role="img" aria-label="Three masses of 1, 2 and 3 kilograms on a number line at positions zero, two and five metres, drawn as bars whose heights are proportional to the masses.">
<text x="240" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Three masses on a line</text>

<rect x="56" y="132" width="28" height="18" fill="#e8eefc" stroke="#2f5fd0" stroke-width="2"/>
<rect x="196" y="114" width="28" height="36" fill="#e8eefc" stroke="#2f5fd0" stroke-width="2"/>
<rect x="406" y="96" width="28" height="54" fill="#e8eefc" stroke="#2f5fd0" stroke-width="2"/>
<text x="70" y="124" text-anchor="middle" font-size="11.5" font-weight="600" fill="#2f5fd0">1.0 kg</text>
<text x="210" y="106" text-anchor="middle" font-size="11.5" font-weight="600" fill="#2f5fd0">2.0 kg</text>
<text x="420" y="88" text-anchor="middle" font-size="11.5" font-weight="600" fill="#2f5fd0">3.0 kg</text>

<line x1="56" y1="150" x2="444" y2="150" stroke="#1f2937" stroke-width="2"/>
<line x1="70" y1="144" x2="70" y2="156" stroke="#1f2937" stroke-width="2"/>
<line x1="140" y1="144" x2="140" y2="156" stroke="#1f2937" stroke-width="2"/>
<line x1="210" y1="144" x2="210" y2="156" stroke="#1f2937" stroke-width="2"/>
<line x1="280" y1="144" x2="280" y2="156" stroke="#1f2937" stroke-width="2"/>
<line x1="350" y1="144" x2="350" y2="156" stroke="#1f2937" stroke-width="2"/>
<line x1="420" y1="144" x2="420" y2="156" stroke="#1f2937" stroke-width="2"/>
<text x="70" y="174" text-anchor="middle" font-size="11.5" fill="#7b8494">0</text>
<text x="140" y="174" text-anchor="middle" font-size="11.5" fill="#7b8494">1</text>
<text x="210" y="174" text-anchor="middle" font-size="11.5" fill="#7b8494">2</text>
<text x="280" y="174" text-anchor="middle" font-size="11.5" fill="#7b8494">3</text>
<text x="350" y="174" text-anchor="middle" font-size="11.5" fill="#7b8494">4</text>
<text x="420" y="174" text-anchor="middle" font-size="11.5" fill="#7b8494">5</text>

<text x="240" y="200" text-anchor="middle" font-size="11.5" font-style="italic" fill="#7b8494">position / m</text>
<text x="240" y="222" text-anchor="middle" font-size="11.5" fill="#7b8494">the bar heights are proportional to the masses</text>
</svg>
</figure>`,
  opts: ["1.67 m", "2.33 m", "2.50 m", "3.50 m", "3.17 m"],
  ans: 4,
  sol: `<p>Use the weighted average: multiply each position by its mass, add, and
divide by the total mass.</p>
<div class="formula">x_cm = (1.0×0 + 2.0×2.0 + 3.0×5.0) / (1.0 + 2.0 + 3.0)
     = (0 + 4.0 + 15.0) / 6.0
     = 19.0 / 6.0 ≈ 3.17 m</div>
<p><b>Answer: E, 3.17 m.</b></p>
<p><b>The check that costs nothing.</b> The centre of mass must lie between the
lightest and heaviest positions — here between 0 and 5.0 m — and it must be nearer
the 3.0 kg mass than the 2.0 kg one, so above the midpoint of 2.0 and 5.0. That
narrows it to 3.17 or 3.50 immediately, and the weighted average settles it.</p>
<p><b>The traps.</b> Option B, 2.33 m, is the unweighted average of the three
positions, <code>(0 + 2 + 5)/3</code> — the answer you get by ignoring the masses
entirely. Option C, 2.50 m, is the average of just the two outer positions.
Option D, 3.50 m, is <code>21/6</code>, from a slip in the product for the 3.0 kg
mass. Option A, 1.67 m, is <code>10/6</code>, which forgets the 3.0 kg mass's
large lever arm.</p>
<p><b>Why weighting matters.</b> The 3.0 kg mass contributes three times as much
to the sum as the 1.0 kg one, so the centre of mass is pulled towards it. A
question that gives you three equal masses is really asking you to spot that the
answer is just the average; a question with unequal masses is testing whether you
weight correctly.</p>`,
},

/* ===================== MODULE D — circular motion ===================== */

{
  id: "D-06", module: "D", topic: "Ratio reasoning", diff: 2,
  q: "Two objects move in circles of the same radius. Object B moves at twice the speed of object A. What is the ratio of the centripetal acceleration of B to that of A?",
  opts: ["1/2", "2", "8", "4", "16"],
  ans: 3,
  sol: `<p>Centripetal acceleration is <code>v²/r</code>. The radius is the same
for both, so only the speed matters — and it enters squared.</p>
<div class="formula">a_B / a_A = (v_B² / r) / (v_A² / r) = (v_B / v_A)² = 2² = 4</div>
<p><b>Answer: D, 4.</b></p>
<p><b>Why the square matters physically.</b> Doubling the speed means the
direction of the velocity has to change twice as fast, <i>and</i> the velocity
itself is twice as long. Both effects contribute, so the acceleration required
quadruples. This is the same quadratic behaviour as braking distance, and it is
why cornering at even slightly more than the safe speed is disproportionately
dangerous.</p>
<p><b>The traps.</b> Option B, 2, is the linear guess — the most common wrong
answer. Option C, 8, cubes the ratio. Option A, ½, inverts it. Option E, 16,
squares twice.</p>
<p><b>What cancelled.</b> The radius and the masses. Whenever a question compares
two situations that share a quantity, cancel that quantity before substituting
anything — it is faster and it removes a chance to slip.</p>`,
},
{
  id: "D-07", module: "D", topic: "Conical pendulum", diff: 3,
  q: "A conical pendulum has a string of length 0.80 m at 60° to the vertical. What is the radius of the horizontal circle traced by the bob?",
  opts: ["0.35 m", "0.40 m", "0.80 m", "0.69 m", "0.46 m"],
  ans: 3,
  sol: `<p>The radius is the horizontal component of the string, so it is
<code>ℓ sin θ</code>, not <code>ℓ cos θ</code>. Draw the triangle and label which
side is which.</p>
<div class="formula">r = ℓ sin θ = 0.80 × sin 60° = 0.80 × 0.866 ≈ 0.69 m</div>
<p><b>Answer: D, 0.69 m.</b></p>
<p><b>Sin or cos?</b> That is the whole question, and the answer comes from the
geometry, not from memory. The string is the hypotenuse. The radius is the side
<i>opposite</i> the angle at the top, so it is <code>ℓ sin θ</code>. The vertical
drop is the side <i>adjacent</i> to that angle, so it is <code>ℓ cos θ</code>. At
60° the string is well away from vertical, so the radius must be most of the
string length — 0.69 m is, and 0.40 m is not.</p>
<p><b>The traps.</b> Option B, 0.40 m, is <code>ℓ cos 60°</code> — the vertical
drop, and the answer you get from swapping sin and cos. Option C, 0.80 m, is the
string length itself, which would be right only if the string were horizontal.
Option A, 0.35 m, is a slip in the multiplication. Option E, 0.46 m, is
<code>ℓ tan θ</code> computed wrongly.</p>
<p><b>The quick sense check.</b> If <code>θ = 90°</code> the string is horizontal
and <code>r = ℓ</code>; if <code>θ = 0</code> there is no circle at all and
<code>r = 0</code>. Only <code>ℓ sin θ</code> satisfies both extremes, which
identifies it without any trigonometry.</p>`,
},
{
  id: "D-08", module: "D", topic: "Orbital ratios", diff: 3,
  q: "Two satellites orbit the same planet in circular orbits, satellite B at nine times the radius of satellite A. What is the ratio of the orbital speed of B to that of A?",
  opts: ["1/√3", "1/9", "3", "9", "1/3"],
  ans: 4,
  sol: `<p>Gravity supplies the centripetal force, so <code>v = √(gr)</code>. But
<code>g</code> itself falls as <code>1/r²</code>, so the speed depends on the
radius twice over.</p>
<div class="formula">v = √(g r),  and g ∝ 1/r²
v ∝ √(r / r²) = √(1/r) = r<sup>−1/2</sup>
v_B / v_A = (9)<sup>−1/2</sup> = 1/√9 = 1/3</div>
<p><b>Answer: E, 1/3.</b> The outer satellite moves at a third of the speed.</p>
<p><b>Two dependences, one answer.</b> Moving outward weakens gravity, which on
its own would slow the satellite; it also lengthens the path, which on its own
would need more speed. The first effect wins, and the combination gives
<code>v ∝ 1/√r</code>. Handling the two effects one at a time is far safer than
trying to see the result in one step.</p>
<p><b>The traps.</b> Option B, 1/9, squares instead of taking the square root.
Option C, 3, and option D, 9, put the ratio the wrong way up — a natural mistake,
since "nine times further out" invites "nine times". Option A, 1/√3, uses a radius
ratio of 3 rather than 9.</p>
<p><b>The companion result.</b> The <i>period</i> goes as <code>r<sup>3/2</sup></code>, so
the same factor of 9 in radius gives a factor of 27 in period — nine times further
out, a third of the speed, twenty-seven times the period. Keeping the two
exponents straight is the whole of orbital ratio work.</p>`,
},
{
  id: "D-09", module: "D", topic: "Vertical circle", diff: 3,
  q: "A ball of mass 0.50 kg on a string of length 1.25 m is swung in a vertical circle. What is the tension in the string at the bottom of the circle if the speed there is 6.0 m s⁻¹? Use <code>g = 10 m s⁻²</code>.",
  opts: ["5.0 N", "14.4 N", "19.4 N", "24.4 N", "9.4 N"],
  ans: 2,
  sol: `<p>At the bottom, the centripetal force is the resultant of the tension
(upward, towards the centre) and the weight (downward, away from the centre). So
the tension has to supply the centripetal force <i>and</i> hold up the weight.</p>
<div class="formula">T − mg = mv²/r
T = m(v²/r + g) = 0.50 × (36/1.25 + 10)
  = 0.50 × (28.8 + 10) = 0.50 × 38.8 = 19.4 N</div>
<p><b>Answer: C, 19.4 N.</b></p>
<p><b>The sign is everything.</b> At the <i>top</i> of the circle gravity points
towards the centre, so it helps: <code>T + mg = mv²/r</code>. At the <i>bottom</i>
gravity points away from the centre, so it opposes: <code>T − mg = mv²/r</code>.
Writing the top equation at the bottom gives <code>T = 0.50 × (28.8 − 10) =
9.4 N</code>, which is option E — so fix the geometry before you calculate.</p>
<p><b>The physical reading.</b> The tension is largest at the bottom, where it
must both turn the ball and support its weight. That is why a string is most
likely to break at the bottom of a swing, and why the bottom of a roller-coaster
loop is where riders feel heaviest.</p>
<p><b>The traps.</b> Option B, 14.4 N, is <code>mv²/r</code> alone — the
centripetal force, forgetting the weight. Option A, 5.0 N, is just the weight.
Option E, 9.4 N, is the result of subtracting the weight instead of adding it.</p>`,
},
{
  id: "D-10", module: "D", topic: "Angular speed", diff: 2,
  q: "A point on the rim of a wheel of radius 0.50 m has a linear speed of 4.0 m s⁻¹. What is the angular speed of the wheel?",
  opts: ["8.0 rad s⁻¹", "2.0 rad s⁻¹", "4.0 rad s⁻¹", "0.125 rad s⁻¹", "16 rad s⁻¹"],
  ans: 0,
  sol: `<p>Linear speed and angular speed are linked by <code>v = ωr</code>, so
<code>ω = v/r</code>.</p>
<div class="formula">ω = 4.0 / 0.50 = 8.0 rad s⁻¹</div>
<p><b>Answer: A, 8.0 rad s⁻¹.</b></p>
<p><b>Why radians and not degrees.</b> The relation <code>v = ωr</code> only holds
in radians, because the radian is defined so that arc length equals radius times
angle. In degrees you would need a factor of <code>2π/360</code>. Every circular-
motion formula in this module assumes radians, so a question asking for angular
speed in rad s⁻¹ is the norm rather than an exception.</p>
<p><b>The traps.</b> Option B, 2.0, is <code>v × r</code> — multiplying instead of
dividing. Option C, 4.0, is the linear speed reported unchanged, as if radius did
not matter. Option D, 0.125, is <code>r/v</code>, the reciprocal. Option E, 16,
doubles the answer, perhaps from using the diameter as the radius and then
dividing wrongly.</p>
<p><b>The check that settles the direction.</b> A bigger wheel turning at the same
angular speed gives its rim a bigger linear speed, so <code>v ∝ r</code> at fixed
ω, and therefore <code>ω = v/r</code> — divide by the radius. Writing that
proportionality down before substituting is faster and safer than recalling the
formula.</p>`,
},
{
  id: "D-11", module: "D", topic: "Centripetal force", diff: 2,
  q: "A car of mass 800 kg takes a bend of radius 40 m at 15 m s⁻¹ on a flat road. What frictional force must the tyres provide?",
  opts: ["12 000 N", "300 N", "8000 N", "4500 N", "2250 N"],
  ans: 3,
  sol: `<p>On a flat road friction alone supplies the centripetal force, and the
normal force is vertical, so it cannot help.</p>
<div class="formula">F = mv²/r = 800 × 225 / 40 = 800 × 5.625 = 4500 N</div>
<p><b>Answer: D, 4500 N.</b></p>
<p><b>The mental route.</b> <code>15² = 225</code> and <code>225/40 = 5.625</code>,
then <code>800 × 5.625</code>. Splitting it as <code>8 × 562.5</code> keeps the
arithmetic in one line. Alternatively, note that the required centripetal
acceleration is <code>v²/r = 5.625 m s⁻²</code>, a little over half of
<code>g</code>, so the frictional force is a little over half the car's weight.</p>
<p><b>The physical check.</b> 4500 N against a weight of 8000 N means the tyres
need a coefficient of friction of at least <code>4500/8000 ≈ 0.56</code>. That is
achievable on dry tarmac but marginal in the wet, which is exactly the kind of
judgement a follow-up question would ask for.</p>
<p><b>The traps.</b> Option B, 300 N, is <code>mv/r</code> with the speed not
squared. Option C, 8000 N, is the weight — the answer you get by forgetting this
is a circular-motion question at all. Option A, 12 000 N, is
<code>m v²/r</code> with a slip. Option E, 2250 N, halves the correct value.</p>
<p><b>Why the mass does not cancel here.</b> In the <i>maximum speed</i> question
the mass cancels, because both the required force and the available friction scale
with it. Here you are asked for the force itself, so the mass stays. Knowing which
question you are being asked determines whether to expect a mass in the answer.</p>`,
},
{
  id: "D-12", module: "D", topic: "Ratio reasoning", diff: 2,
  q: "An object moves in a circle at constant speed. If the radius is doubled and the speed is doubled, what happens to the centripetal acceleration?",
  opts: ["It doubles", "It is unchanged", "It quadruples", "It halves", "It increases eightfold"],
  ans: 0,
  sol: `<p>Apply the two changes to <code>a = v²/r</code> one at a time, then
multiply the factors.</p>
<div class="formula">speed doubled  ⇒  v² quadrupled  ⇒  factor 4
radius doubled  ⇒  divide by 2    ⇒  factor ½
net factor = 4 × ½ = 2
a' = 2a</div>
<p><b>Answer: A, it doubles.</b></p>
<p><b>Why doing it one change at a time is the reliable method.</b> Holding one
variable fixed while you vary the other means you never have to manipulate two
symbols at once. It also makes the answer checkable: each factor is a simple
number, and their product is the whole answer.</p>
<p><b>The traps.</b> Option B, unchanged, is what you get if you think the two
changes cancel — which would require the speed to enter linearly rather than
squared. Option C, quadruples, applies the speed change and forgets the radius.
Option D, halves, applies only the radius change. Option E, eightfold, multiplies
by 4 and by 2 instead of by 4 and by ½.</p>
<p><b>The physical reading.</b> Doubling the radius on its own makes the turn
gentler and the acceleration smaller; doubling the speed makes it much larger.
Together the speed effect wins by a factor of two, so the net acceleration still
rises. That ordering — speed matters more than radius because it is squared — is
worth internalising.</p>`,
},

/* ===================== MODULE E — materials ===================== */

{
  id: "E-06", module: "E", topic: "Extension ratio", diff: 2,
  q: "Two wires are made of the same material. Wire P has length <code>L</code> and diameter <code>d</code>. Wire Q has length <code>2L</code> and diameter <code>2d</code>. Both carry the same load <code>F</code>. What is the ratio of the extension of P to the extension of Q?",
  opts: ["1 : 2", "1 : 1", "2 : 1", "4 : 1", "1 : 4"],
  ans: 2,
  sol: `<p>Extension is <code>ΔL = FL/(AE)</code>. Only <code>L</code> and
<code>A</code> differ, and <code>E</code> and <code>F</code> cancel in the ratio.
Take the two changes one at a time.</p>
<div class="formula">length: L → 2L                    ⇒ ΔL doubles  (factor 2)
diameter: d → 2d ⇒ area A → 4A         ⇒ ΔL quarters (factor ¼)
net factor = 2 × ¼ = ½
ΔL_Q = ½ ΔL_P     so     ΔL_P : ΔL_Q = 2 : 1</div>
<p><b>Answer: C, 2 : 1.</b></p>
<p><b>The one thing to get right.</b> Cross-sectional area goes as the
<i>square</i> of the diameter. Doubling the diameter quadruples the area, which
makes the wire four times harder to stretch, and that effect beats the doubling
of the length. Every wrong option here comes from treating the diameter as if it
entered linearly.</p>
<p><b>The traps.</b> Option B, 1 : 1, is what you get by reasoning that "the
length doubles but so does the area, so they cancel" — true only if the area
doubled, which it does not. Option A, 1 : 2, is the ratio written the wrong way
round. Option D, 4 : 1, multiplies by both factors instead of dividing by one of
them. Option E, 1 : 4, is the same slip inverted.</p>
<p><b>A habit worth building.</b> In any "two things change at once" question,
write the proportional dependence first — here <code>ΔL ∝ L/d²</code> — and then
apply the factors. It turns a problem that feels like algebra into one that is
purely arithmetic.</p>`,
},
{
  id: "E-07", module: "E", topic: "Springs in combination", diff: 3,
  q: "A spring of stiffness <code>k</code> is cut into three equal pieces and the three pieces are then joined in parallel. What is the stiffness of the combination?",
  opts: ["27k", "3k", "k/3", "k", "9k"],
  ans: 4,
  sol: `<p>Two separate ideas are being combined here, so do them in order.</p>
<p><b>Step 1 — cutting.</b> For a uniform spring, stiffness is inversely
proportional to length: a piece of length <code>L/n</code> has stiffness
<code>nk</code>. Cutting into thirds gives three pieces each of stiffness
<code>3k</code>. The physical reason is that each third only has to produce one
third of the total extension, so it takes three times the force to stretch it by
a given amount.</p>
<p><b>Step 2 — parallel.</b> Springs in parallel share the same extension and
their forces add, so their stiffnesses add:</p>
<div class="formula">k_total = 3k + 3k + 3k = 9k</div>
<p><b>Answer: E, 9k.</b></p>
<p><b>Why the two effects multiply.</b> Cutting made each piece three times
stiffer; putting three in parallel then made the combination three times stiffer
again. The factors compose as <code>3 × 3 = 9</code>, not as <code>3 + 3</code>.
Questions that chain two rules like this are the standard way of separating
people who know the rules from people who know when to apply them.</p>
<p><b>The traps.</b> Option B, 3k, applies the cutting step and stops. Option C,
k/3, treats parallel springs like parallel resistors — the rule is the opposite:
springs in parallel add, springs in series add their compliances. Option D, k,
assumes the two operations undo each other. Option A, 27k, multiplies by three
three times.</p>
<p><b>Checking it physically.</b> The original spring had length <code>L</code>
and stiffness <code>k</code>. The new arrangement is three short springs side by
side, so it is effectively one spring of length <code>L/3</code> and three times
the cross-section — shorter and thicker, hence much stiffer. Nine times stiffer
is plausible; a third as stiff is not.</p>`,
},
{
  id: "E-08", module: "E", topic: "Strain energy ratio", diff: 2,
  q: "Spring P has stiffness <code>k</code> and is extended by <code>x</code>. Spring Q has stiffness <code>2k</code> and is extended by <code>2x</code>. What is the ratio of the energy stored in P to the energy stored in Q?",
  opts: ["1 : 8", "1 : 4", "1 : 2", "1 : 16", "1 : 1"],
  ans: 0,
  sol: `<p>Write down <code>E = ½ k x²</code> for each and form the ratio. No
numbers are needed.</p>
<div class="formula">E_P = ½ k x²
E_Q = ½ (2k)(2x)² = ½ × 2k × 4x² = 8 × (½ k x²) = 8 E_P
E_P : E_Q = 1 : 8</div>
<p><b>Answer: A, 1 : 8.</b></p>
<p><b>Where the factor of eight comes from.</b> The stiffness doubled, which is
one factor of two. The extension doubled <i>and then got squared</i>, which is
two more factors of two. Total: <code>2 × 2 × 2 = 8</code>. People lose this
question by treating the extension as linear, because <code>½kx²</code> looks
symmetrical in <code>k</code> and <code>x</code>. It is not: only one of them is
squared.</p>
<p><b>The traps.</b> Option B, 1 : 4, comes from squaring the stiffness or from
forgetting one of the two extension factors. Option C, 1 : 2, treats both
variables as linear. Option D, 1 : 16, squares the stiffness as well. Option E,
1 : 1, is the answer you get if you assume a stiffer spring stretched further
must "balance out" somehow — an instinct, not a calculation.</p>
<p><b>The general form.</b> <code>E ∝ k x²</code>, so for any two springs
<code>E₂/E₁ = (k₂/k₁) × (x₂/x₁)²</code>. Committing that single line to memory
settles this whole family of questions.</p>`,
},
{
  id: "E-09", module: "E", topic: "Thermal expansion ratio", diff: 2,
  q: "A steel rod of length <code>L</code> expands by <code>ΔL</code> when its temperature is raised by <code>ΔT</code>. A second rod of the same steel has length <code>3L</code> and is heated by <code>ΔT/3</code>. What is its expansion?",
  opts: ["ΔL", "3ΔL", "ΔL/3", "9ΔL", "ΔL/9"],
  ans: 0,
  sol: `<p>Linear expansion obeys <code>ΔL = α L ΔT</code>. Both <code>L</code>
and <code>ΔT</code> change, and the material does not, so <code>α</code> cancels.</p>
<div class="formula">ΔL₂ = α (3L)(ΔT/3) = α L ΔT × (3 × ⅓) = α L ΔT = ΔL</div>
<p><b>Answer: A, ΔL.</b> The two changes cancel exactly.</p>
<p><b>Why "cancel" is the interesting answer.</b> A longer rod expands more; a
smaller temperature rise expands less. Here the length went up by three and the
temperature rise went down by three, and because the relationship is linear in
<i>both</i> variables the two effects multiply to one. This is the cleanest
possible test of whether you know the formula is a product rather than, say, a
ratio.</p>
<p><b>The traps.</b> Option B, 3ΔL, applies the length change and ignores the
temperature change. Option C, ΔL/3, does the reverse. Option D, 9ΔL, multiplies
by three twice, which would be right only if the temperature entered as a square.
Option E, ΔL/9, is the same error inverted.</p>
<p><b>Extending it.</b> Had the question asked about the rod's <i>volume</i>
instead of its length, the coefficient would be roughly <code>3α</code> and the
answer would still be <code>ΔV</code> — the factor of three in the volume
coefficient and the factor of three in the length would again cancel against the
temperature. Ratio answers often survive changes that look as though they should
matter.</p>`,
},
{
  id: "E-10", module: "E", topic: "Shared load", diff: 3,
  q: "Two vertical wires of the same material and the same length support a load <code>W</code> between them. Wire 1 has cross-sectional area <code>A</code> and wire 2 has area <code>2A</code>. What force does wire 1 carry?",
  opts: ["W/6", "W/2", "2W/3", "W/4", "W/3"],
  ans: 4,
  sol: `<p>This is a two-step problem: a <i>compatibility</i> condition, then a
force balance. Neither step works on its own.</p>
<p><b>Step 1 — both wires extend by the same amount.</b> They are the same
length and hang from the same support, so <code>ΔL₁ = ΔL₂</code>. Using
<code>ΔL = FL/(AE)</code> with <code>L</code> and <code>E</code> identical:</p>
<div class="formula">F₁L/(AE) = F₂L/(2AE)   ⇒   F₁ = F₂/2   ⇒   F₂ = 2F₁</div>
<p><b>Step 2 — the forces must add to the load.</b></p>
<div class="formula">F₁ + F₂ = W   ⇒   F₁ + 2F₁ = W   ⇒   F₁ = W/3</div>
<p><b>Answer: E, W/3.</b></p>
<p><b>The idea that makes this work.</b> Wires in parallel share a displacement,
not a force. The stiffer wire — the thicker one — takes the larger share, in
proportion to its area. Recognising that "same extension" is the constraint,
rather than "same force", is the whole question.</p>
<p><b>The traps.</b> Option B, W/2, assumes the load is shared equally, which
would only be true for identical wires. Option C, 2W/3, is wire 2's share —
correct arithmetic applied to the wrong wire. Option D, W/4, and option A, W/6,
come from inverting the area ratio in step 1, giving
<code>F₁ = 2F₂</code> and then <code>F₁ = 2W/3</code> or similar.</p>
<p><b>A useful check.</b> The thicker wire carries <code>2W/3</code> and the
thinner carries <code>W/3</code>, and the two are in the ratio
<code>2 : 1</code> — exactly the ratio of the areas. If your answer does not
reproduce that ratio, step 1 went wrong.</p>`,
},

/* ===================== MODULE F — waves ===================== */

{
  id: "F-06", module: "F", topic: "Wave speed ratio", diff: 2,
  q: "A string under tension <code>T</code> carries transverse waves at speed <code>v</code>. What tension is needed to double the speed?",
  opts: ["√2 T", "2T", "T/4", "4T", "16T"],
  ans: 3,
  sol: `<p>The speed on a stretched string is <code>v = √(T/μ)</code>, with
<code>μ</code> unchanged. Rearranging on the ratio is quicker than substituting.</p>
<div class="formula">v ∝ √T   ⇒   v₂/v₁ = √(T₂/T₁)
2 = √(T₂/T)   ⇒   T₂/T = 4   ⇒   T₂ = 4T</div>
<p><b>Answer: D, 4T.</b></p>
<p><b>The square root is the entire question.</b> Doubling a speed that depends
on the square root of the tension requires quadrupling the tension. This is worth
internalising as a physical fact too: the extra tension has to do two jobs at
once — accelerate a given element harder <i>and</i> move it faster — so it costs
more than a factor of two.</p>
<p><b>The traps.</b> Option B, 2T, treats <code>v</code> as proportional to
<code>T</code>. Option C, T/4, inverts the relationship, which would make a
tighter string slower — the opposite of what a guitar tells you. Option A,
√2 T, halves the exponent. Option E, 16T, squares twice.</p>
<p><b>Practical reading.</b> A string at 4T is under serious strain; in real
instruments you change pitch far more cheaply by shortening the string, because
<code>f ∝ 1/L</code> is linear. That is why the same note is reached by fretting
rather than by tightening.</p>`,
},
{
  id: "F-07", module: "F", topic: "Harmonics with two changes", diff: 3,
  q: "A string of length <code>L</code> fixed at both ends has fundamental frequency <code>f₀</code>. The string is replaced by one of the same material and thickness but half the length, and the tension is increased by a factor of four. What is the new fundamental frequency?",
  opts: ["8f₀", "2f₀", "4f₀", "f₀", "16f₀"],
  ans: 2,
  sol: `<p>The fundamental of a string fixed at both ends is
<code>f = (1/2L)√(T/μ)</code>. Two variables change; handle them separately and
multiply.</p>
<div class="formula">length halved:  L → L/2   ⇒  factor 2
tension ×4:     T → 4T    ⇒  √4 = factor 2
net factor = 2 × 2 = 4
f' = 4 f₀</div>
<p><b>Answer: C, 4f₀.</b></p>
<p><b>Why the problem specifies "same material and thickness".</b> That is there
to tell you <code>μ</code> is unchanged. If the new string were a different
thickness the mass per unit length would change and the problem would have a
third factor. Reading qualifiers like that is part of the skill — they are not
padding.</p>
<p><b>The traps.</b> Option B, 2f₀, applies one of the two changes and forgets
the other. Option A, 8f₀, uses <code>T</code> rather than <code>√T</code> for
the tension step, giving <code>2 × 4</code>. Option D, f₀, comes from noticing
that "one goes up and one goes down" and concluding they cancel — but the length
going down makes the frequency go <i>up</i>, so both changes push the same way.
Option E, 16f₀, compounds the <code>T</code> error with a squared length.</p>
<p><b>Checking the direction.</b> Shorter and tighter must be higher pitched.
Every option except f₀ says higher, which is a hint that the interesting
distinction here is the size of the factor, not its direction.</p>`,
},
{
  id: "F-08", module: "F", topic: "Phase difference", diff: 2,
  q: "Two points on a progressive wave are separated by a distance of <code>λ/6</code> along the direction of travel. What is the phase difference between them?",
  opts: ["180°", "30°", "120°", "90°", "60°"],
  ans: 4,
  sol: `<p>Phase difference is simply the fraction of a wavelength, turned into
an angle. One whole wavelength is <code>360°</code> or <code>2π</code>.</p>
<div class="formula">Δφ = 360° × (path difference / λ)
    = 360° × (λ/6)/λ = 360°/6 = 60°</div>
<p><b>Answer: E, 60°.</b></p>
<p><b>The single line to remember.</b>
<code>Δφ = 2π × Δx/λ</code>. Every phase question is this line plus arithmetic.
Points a wavelength apart are in phase; points half a wavelength apart are in
antiphase; everything else is a proportion.</p>
<p><b>The traps.</b> Option B, 30°, corresponds to <code>λ/12</code>. Option C,
120°, is <code>λ/3</code> — the answer if you halve the separation or double the
angle. Option D, 90°, is <code>λ/4</code>, the most commonly memorised special
case, and therefore the most commonly misremembered. Option A, 180°, is
<code>λ/2</code>.</p>
<p><b>Why this matters beyond the question.</b> The same fraction governs
interference: two sources with a path difference of <code>λ/6</code> superpose
with a phase offset of 60°, which is how you decide whether the resulting
amplitude is larger or smaller than either alone. Phase is not a separate topic
from superposition; it is the language superposition is written in.</p>`,
},
{
  id: "F-09", module: "F", topic: "Intensity ratio", diff: 2,
  q: "A wave of amplitude <code>A</code> and frequency <code>f</code> in a given medium carries intensity <code>I</code>. A second wave in the same medium has amplitude <code>2A</code> and frequency <code>f/2</code>. What is its intensity?",
  opts: ["I", "2I", "4I", "I/2", "I/4"],
  ans: 0,
  sol: `<p>For a wave in a fixed medium, <code>I = ½ ρ v ω² A²</code>, and
<code>ρ</code> and <code>v</code> are set by the medium. So
<code>I ∝ f² A²</code> and the ratio is pure arithmetic.</p>
<div class="formula">amplitude:  A → 2A   ⇒  A² × 4
frequency: f → f/2  ⇒  f² × ¼
net factor = 4 × ¼ = 1
I' = I</div>
<p><b>Answer: A, I.</b> The two changes cancel.</p>
<p><b>Why "the same medium" is load-bearing.</b> The wave speed is a property of
the medium, not of the source, so halving the frequency does not change
<code>v</code> — it doubles the wavelength instead. That is what lets you treat
everything except <code>f</code> and <code>A</code> as constant. Change the
medium and the whole expression has to be rebuilt.</p>
<p><b>The traps.</b> Option B, 2I, treats intensity as linear in amplitude.
Option C, 4I, applies the amplitude change and forgets the frequency. Option D,
I/2, applies the frequency change linearly. Option E, I/4, uses
<code>f²</code> but with the factor the wrong way up, or squares the amplitude
change without squaring it.</p>
<p><b>The physical picture.</b> A bigger amplitude means each oscillating
particle moves further, and energy goes as the square of that. A lower frequency
means it moves slower, and energy goes as the square of that too. Doubling one
and halving the other leaves the energy flow unchanged — a louder-looking wave
that is not actually louder.</p>`,
},
{
  id: "F-10", module: "F", topic: "Pipes", diff: 3,
  q: "A pipe of length <code>L</code> closed at one end has fundamental frequency <code>f</code>. The closed end is now opened, so the pipe is open at both ends, and at the same time its length is doubled to <code>2L</code>. What is the new fundamental frequency?",
  opts: ["f/2", "2f", "f", "4f", "f/4"],
  ans: 2,
  sol: `<p>Two changes again, but here they genuinely oppose each other, which is
why the answer is not a factor of two or four.</p>
<div class="formula">closed at one end:  λ = 4L    f = v/(4L)
open at both ends:  λ = 2 × length = 2(2L) = 4L
                    f' = v/(4L) = f</div>
<p><b>Answer: C, f.</b> Unchanged.</p>
<p><b>Why it works out that neatly.</b> Opening the closed end converts the pipe
from a quarter-wave resonator into a half-wave resonator, which on its own would
double the frequency. Doubling the length on its own would halve it. The two
factors multiply to one. The result is a pipe twice as long that resonates at
exactly the same pitch — because it now supports a standing wave with the same
wavelength as before.</p>
<p><b>The traps.</b> Option B, 2f, applies the opening and forgets the length.
Option A, f/2, applies the length and forgets the opening. Option D, 4f, doubles
twice, usually from using <code>λ = L</code> for the open pipe. Option E, f/4,
halves twice.</p>
<p><b>The underlying pattern.</b> A closed end is a displacement node and an open
end is a displacement antinode. Once you can sketch that picture, the allowed
wavelengths follow without memorising formulas: closed–open gives odd harmonics
only, open–open gives all of them. Sketch first, then calculate.</p>`,
},

/* ===================== MODULE G — optics ===================== */

{
  id: "G-06", module: "G", topic: "Fringe spacing ratio", diff: 3,
  q: "In a Young's double-slit experiment the fringe spacing on the screen is <code>w</code>. The slit separation is doubled and the screen is moved to half its original distance. What is the new fringe spacing?",
  opts: ["w/2", "w", "w/4", "2w", "4w"],
  ans: 2,
  sol: `<p>Fringe spacing is <code>w = λD/d</code>. Two changes, applied one at a
time.</p>
<div class="formula">separation doubled: d → 2d   ⇒  w halves   (factor ½)
distance halved:    D → D/2  ⇒  w halves   (factor ½)
net factor = ½ × ½ = ¼
w' = w/4</div>
<p><b>Answer: C, w/4.</b></p>
<p><b>Both changes push the same way.</b> That is worth pausing on, because the
instinct is that "one goes up and one goes down" must cancel. They do not:
increasing the slit separation makes the fringes finer, and moving the screen
closer also makes them finer. Two effects that sound different both shrink the
pattern, so the answer must be smaller than <code>w</code> — which already rules
out two of the options before any arithmetic.</p>
<p><b>The traps.</b> Option B, w, is the "they cancel" reflex. Option A, w/2,
applies one change. Option D, 2w, and option E, 4w, have at least one factor
inverted — typically from remembering <code>w ∝ d</code> instead of
<code>w ∝ 1/d</code>.</p>
<p><b>Sanity check without numbers.</b> The wavelength has not changed, so the
only things that can alter the spacing are the geometry of the slits and how far
the pattern has spread by the time it reaches the screen. Finer spacing from
tighter, closer slits is exactly what the picture predicts.</p>`,
},
{
  id: "G-07", module: "G", topic: "Diffraction grating orders", diff: 2,
  q: "A diffraction grating has 500 lines per millimetre. Light of wavelength 600 nm is incident normally on it. What is the highest order of diffraction that can be observed?",
  opts: ["3rd", "2nd", "4th", "5th", "6th"],
  ans: 0,
  sol: `<p>The grating equation is <code>nλ = d sin θ</code>, and the largest
possible value of <code>sin θ</code> is 1. So the largest possible order is
<code>d/λ</code>, rounded down. First you need <code>d</code>.</p>
<div class="formula">d = 1 / (500 per mm) = 1/500 mm = 2.0 × 10⁻⁶ m = 2000 nm
n ≤ d/λ = 2000 / 600 = 3.33…
n_max = 3   (the third order)</div>
<p><b>Answer: A, the 3rd order.</b></p>
<p><b>Rounding down is not a convention, it is physics.</b> The fourth order
would need <code>sin θ = 4 × 600/2000 = 1.2</code>, which no angle satisfies. The
order is cut off because the beam would have to leave at more than 90° to the
normal — geometrically impossible. Whenever a calculation gives you a
<code>sin</code> or <code>cos</code> above 1, the mode, order or ray simply does
not exist.</p>
<p><b>The traps.</b> Option B, 2nd, under-rounds. Option C, 4th, rounds 3.33 up
instead of down. Option D, 5th, and option E, 6th, come from an arithmetic slip
in <code>d</code> — most often treating 500 lines per mm as a spacing of
500 nm rather than 2000 nm.</p>
<p><b>The reciprocal step is where marks are lost.</b> "500 lines per mm" must be
turned into a spacing before it is usable. Writing the units out —
<code>mm⁻¹ → mm → m → nm</code> — costs four seconds and prevents the single most
common error on this topic.</p>`,
},
{
  id: "G-08", module: "G", topic: "Apparent depth", diff: 3,
  q: "A swimming pool has a real depth of 2.0 m and is filled with water of refractive index 4/3. Viewed from directly above, how far below the surface does the bottom appear to be?",
  opts: ["2.0 m", "1.5 m", "2.7 m", "1.3 m", "0.67 m"],
  ans: 1,
  sol: `<p>For near-normal viewing in a medium of refractive index <code>n</code>,
the apparent depth is the real depth divided by <code>n</code>. Deriving it in
one line is safer than quoting it.</p>
<div class="formula">n = real depth / apparent depth
apparent depth = 2.0 / (4/3) = 2.0 × ¾ = 1.5 m</div>
<p><b>Answer: B, 1.5 m.</b></p>
<p><b>Why it only works "from directly above".</b> The result comes from
applying Snell's law to a ray leaving the bottom at a small angle to the normal.
As the viewing angle increases the apparent depth shrinks further, which is why
the qualification matters and why a pool looks shallower still from the side. The
near-normal formula is a limiting case, not a general one.</p>
<p><b>The traps.</b> Option A, 2.0 m, is the answer you get by deciding that
refraction does not change apparent position at all. Option C, 2.7 m, multiplies
by 4/3 instead of dividing — the single most common slip, and it says the water
makes the pool look <i>deeper</i>, which no swimmer has ever observed. Option D,
1.3 m, uses 2/3 instead of 3/4. Option E, 0.67 m, divides by 3.</p>
<p><b>The direction check that catches all of these.</b> Water makes depths look
shallower. Any answer above 2.0 m is wrong before you start, and any answer
below about 1.3 m is too extreme for an index of only 1.33.</p>`,
},
{
  id: "G-09", module: "G", topic: "Speed and wavelength in a medium", diff: 2,
  q: "Light of wavelength 600 nm in air enters a glass block of refractive index 1.5. What are the speed and the wavelength of the light in the glass?",
  opts: ["1.3 × 10⁸ m s⁻¹ and 400 nm", "2.0 × 10⁸ m s⁻¹ and 600 nm", "3.0 × 10⁸ m s⁻¹ and 400 nm", "3.0 × 10⁸ m s⁻¹ and 900 nm", "2.0 × 10⁸ m s⁻¹ and 400 nm"],
  ans: 4,
  sol: `<p>Two things change and one does not. Deciding which is which is the
question.</p>
<div class="formula">n = c/v            ⇒  v = 3.0 × 10⁸ / 1.5 = 2.0 × 10⁸ m s⁻¹
v = fλ, f unchanged  ⇒  λ ∝ v
λ_glass = 600 × (2.0/3.0) = 400 nm</div>
<p><b>Answer: E, 2.0 × 10⁸ m s⁻¹ and 400 nm.</b></p>
<p><b>Frequency is the invariant.</b> It is set by the source and cannot change at
a boundary, because the oscillations on either side have to stay in step
moment by moment. If the frequency changed, wave crests would pile up or vanish
at the interface, which does not happen. Speed and wavelength both drop by the
factor <code>n</code>; frequency does not.</p>
<p><b>The traps.</b> Option B keeps the wavelength at 600 nm, which would mean
the frequency rose — the light changes colour on entering glass, which it does
not. Option C keeps the speed at <code>3.0 × 10⁸</code>, the classic "light
always travels at c" error; <code>c</code> is the speed in a vacuum. Option D
keeps both and additionally scales the wavelength the wrong way. Option A uses
<code>c/n²</code> for the speed.</p>
<p><b>Colour and detection.</b> This is why the frequency, not the wavelength, is
the honest label for a colour: 400 nm in glass is still red light, and it returns
to 600 nm the moment it leaves.</p>`,
},
{
  id: "G-10", module: "G", topic: "Lenses in contact", diff: 3,
  q: "A converging lens of focal length 20 cm is placed in contact with a diverging lens of focal length 30 cm. What is the focal length of the combination?",
  opts: ["50 cm", "60 cm", "12 cm", "10 cm", "−60 cm"],
  ans: 1,
  sol: `<p>Lenses in contact add their <i>powers</i>, not their focal lengths. The
diverging lens has a negative focal length, and that sign is the whole
question.</p>
<div class="formula">P₁ = 1/0.20 = +5.0 D
P₂ = 1/(−0.30) = −3.33 D
P = 5.0 − 3.33 = 1.67 D
f = 1/P = 0.60 m = 60 cm</div>
<p><b>Answer: B, 60 cm.</b></p>
<p><b>Why powers add.</b> Power is the amount of convergence a lens imposes per
unit of aperture, and two thin lenses in contact act on the same ray with almost
no separation, so their effects accumulate directly. Adding focal lengths has no
physical meaning at all.</p>
<p><b>The traps.</b> Option A, 50 cm, adds the focal lengths. Option C, 12 cm, is
the most instructive wrong answer: it is what you get from
<code>1/f = 1/20 + 1/30</code>, i.e. by forgetting that the diverging lens has a
negative focal length. It is a perfectly executed calculation of the wrong
problem, which is exactly what an exam setter wants to catch. Option D, 10 cm,
comes from subtracting the powers in the wrong order on top of that. Option E,
−60 cm, gets the magnitude right and then mis-signs the answer: the combination
is still converging, because +5 D beats −3.33 D.</p>
<p><b>The sign check.</b> The converging lens is the stronger of the two, so the
pair must still converge and the focal length must be positive. That fixes the
sign before you finish the arithmetic.</p>`,
},

/* ===================== MODULE H — circuits ===================== */

{
  id: "H-12", module: "H", topic: "Stretched wire", diff: 3,
  q: "A wire of resistance <code>R</code> is stretched uniformly until its length doubles. Assuming the volume of metal is unchanged, what is its new resistance?",
  opts: ["4R", "2R", "R/2", "8R", "16R"],
  ans: 0,
  sol: `<p>One measurement changes and another follows from it, so this is two
steps. The hidden constraint is conservation of volume.</p>
<div class="formula">volume constant:  A L = A' (2L)   ⇒   A' = A/2
R = ρL/A
R' = ρ(2L)/(A/2) = 4 ρL/A = 4R</div>
<p><b>Answer: A, 4R.</b></p>
<p><b>The constraint is easy to miss because it is not stated as a number.</b>
"Stretched" tells you the wire got longer <i>and thinner</i>, but you have to
supply that yourself from the fact that no metal was added. Once you write
<code>AL = constant</code>, the rest is substitution.</p>
<p><b>The traps.</b> Option B, 2R, uses <code>R ∝ L</code> and forgets that the
area fell. Option C, R/2, uses <code>R ∝ 1/A</code> and forgets the length grew.
Option D, 8R, treats the area as quartering, which would need the length to
quadruple. Option E, 16R, squares the length factor and the area factor
independently.</p>
<p><b>A compact way to hold it.</b> With volume fixed,
<code>R = ρL/A = ρL²/(AL) ∝ L²</code>. Doubling the length therefore quadruples
the resistance, in one line. That form also shows why strain gauges are so
sensitive: a 0.1% stretch changes the resistance by 0.2%.</p>`,
},
{
  id: "H-13", module: "H", topic: "Loaded potential divider", diff: 3,
  q: `<p>A 12 V supply of negligible internal resistance is connected across a 400 Ω resistor and a 600 Ω resistor in series. A 600 Ω load resistor is then connected across the 600 Ω resistor. What is the pd across the load?</p>
<figure class="fig">
<svg viewBox="0 0 460 262" role="img" aria-label="A 12 volt supply across a 400 ohm and a 600 ohm resistor in series, with a 600 ohm load connected across the 600 ohm resistor.">
<text x="230" y="24" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">A divider with a load across the bottom arm</text>

<text x="230" y="42" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f7a53">12 V</text>
<line x1="212" y1="52" x2="248" y2="52" stroke="#1f2937" stroke-width="2.5"/>
<line x1="220" y1="64" x2="240" y2="64" stroke="#1f2937" stroke-width="5"/>
<line x1="230" y1="64" x2="230" y2="86" stroke="#1f2937" stroke-width="2"/>

<rect x="214" y="86" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="256" y="112" font-size="12.5" font-weight="600" fill="#2f5fd0">R₁ = 400 Ω</text>
<line x1="230" y1="130" x2="230" y2="166" stroke="#1f2937" stroke-width="2"/>
<circle cx="230" cy="148" r="3.2" fill="#1f2937"/>
<rect x="214" y="166" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="256" y="192" font-size="12.5" font-weight="600" fill="#2f5fd0">R₂ = 600 Ω</text>
<line x1="230" y1="210" x2="230" y2="228" stroke="#1f2937" stroke-width="2"/>
<circle cx="230" cy="228" r="3.2" fill="#1f2937"/>

<line x1="230" y1="148" x2="370" y2="148" stroke="#1f2937" stroke-width="2"/>
<line x1="370" y1="148" x2="370" y2="170" stroke="#1f2937" stroke-width="2"/>
<rect x="354" y="170" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="370" y1="214" x2="370" y2="228" stroke="#1f2937" stroke-width="2"/>
<line x1="370" y1="228" x2="230" y2="228" stroke="#1f2937" stroke-width="2"/>
<circle cx="370" cy="148" r="3.2" fill="#1f2937"/>
<circle cx="370" cy="228" r="3.2" fill="#1f2937"/>
<text x="394" y="196" font-size="12.5" font-weight="600" fill="#a8641a">600 Ω</text>
<text x="394" y="212" font-size="10.5" fill="#7b8494">load</text>

<text x="230" y="252" text-anchor="middle" font-size="11.5" fill="#7b8494">the load sits in parallel with R₂, so that arm is no longer 600 Ω alone</text>
</svg>
</figure>`,
  opts: ["6.0 V", "7.2 V", "5.1 V", "4.0 V", "3.6 V"],
  ans: 2,
  sol: `<p>The load is in parallel with the 600 Ω resistor, so it changes the
divider itself. Reduce that parallel pair first, then divide.</p>
<div class="formula">600 Ω ∥ 600 Ω = 300 Ω
total = 400 + 300 = 700 Ω
I = 12 / 700 = 0.01714 A
V_out = I × 300 = 5.14 V ≈ 5.1 V</div>
<p><b>Answer: C, 5.1 V.</b></p>
<p><b>Why the order of operations matters.</b> The temptation is to work out the
unloaded output — <code>12 × 600/1000 = 7.2 V</code> — and then try to adjust it.
That route has no reliable adjustment to make. Reducing the network first turns
the problem back into a plain two-resistor divider, which you can then solve
mechanically.</p>
<p><b>The traps.</b> Option B, 7.2 V, ignores the load altogether. Option A,
6.0 V, assumes the matched load halves the output, which is a coincidence of
these particular numbers rather than a rule. Option D, 4.0 V, uses
<code>12 × 300/900</code>, keeping the original total. Option E, 3.6 V, uses
<code>12 × 300/1000</code>, mixing the new branch with the old total.</p>
<p><b>The design lesson.</b> A divider is only stiff when the load resistance is
large compared with the resistors doing the dividing. Here the load equals one of
them, the output sags from 7.2 V to 5.1 V, and any sensor circuit built that way
would read low and drift as the load changed.</p>`,
},
{
  id: "H-14", module: "H", topic: "Power in parallel", diff: 2,
  q: "A resistor <code>R</code> and a resistor <code>2R</code> are connected in parallel across a supply. What is the ratio of the power dissipated in <code>R</code> to the power dissipated in <code>2R</code>?",
  opts: ["1 : 2", "2 : 1", "1 : 1", "4 : 1", "1 : 4"],
  ans: 1,
  sol: `<p>In parallel the pd is the same across both, so the formula with
<code>V</code> in it is the one to use — not the one with <code>I²</code>.</p>
<div class="formula">P = V²/R
P_R : P_2R = (V²/R) : (V²/2R) = 1 : ½ = 2 : 1</div>
<p><b>Answer: B, 2 : 1.</b> The smaller resistor dissipates twice as much.</p>
<p><b>Choosing the right form of the power formula.</b> There are three:
<code>VI</code>, <code>I²R</code> and <code>V²/R</code>. In a parallel circuit
<code>V</code> is the shared quantity, so <code>V²/R</code> makes the comparison
immediate. Using <code>I²R</code> here is not wrong but it is slower, because the
currents differ and you have to work them out first. Picking the form that holds
the common variable fixed is a real time-saver.</p>
<p><b>The traps.</b> Option A, 1 : 2, says the bigger resistor gets more power —
true in series, false in parallel, and the swap is the most common single error in
this topic. Option C, 1 : 1, would mean both draw the same current. Option D,
4 : 1, squares the resistance ratio. Option E, 1 : 4, does both errors at once.</p>
<p><b>Worth memorising as a pair.</b> Series: same current, so
<code>P ∝ R</code> and the larger resistor runs hotter. Parallel: same pd, so
<code>P ∝ 1/R</code> and the smaller resistor runs hotter. Same words, opposite
conclusions — the circuit configuration decides which.</p>`,
},
{
  id: "H-15", module: "H", topic: "Voltmeter loading", diff: 3,
  q: `<p>A 10 V supply of negligible internal resistance is connected in series with two 100 kΩ resistors. A voltmeter of resistance 100 kΩ is connected across one of them. What does the voltmeter read?</p>
<figure class="fig">
<svg viewBox="0 0 460 262" role="img" aria-label="A 10 volt supply across two 100 kilohm resistors in series, with a 100 kilohm voltmeter connected across one of them.">
<text x="230" y="24" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">A voltmeter is a resistor too</text>

<text x="230" y="42" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f7a53">10 V</text>
<line x1="212" y1="52" x2="248" y2="52" stroke="#1f2937" stroke-width="2.5"/>
<line x1="220" y1="64" x2="240" y2="64" stroke="#1f2937" stroke-width="5"/>
<line x1="230" y1="64" x2="230" y2="86" stroke="#1f2937" stroke-width="2"/>

<rect x="214" y="86" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="256" y="112" font-size="12.5" font-weight="600" fill="#2f5fd0">100 kΩ</text>
<line x1="230" y1="130" x2="230" y2="166" stroke="#1f2937" stroke-width="2"/>
<circle cx="230" cy="148" r="3.2" fill="#1f2937"/>
<rect x="214" y="166" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="256" y="192" font-size="12.5" font-weight="600" fill="#2f5fd0">100 kΩ</text>
<line x1="230" y1="210" x2="230" y2="228" stroke="#1f2937" stroke-width="2"/>
<circle cx="230" cy="228" r="3.2" fill="#1f2937"/>

<line x1="230" y1="148" x2="370" y2="148" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="5 4"/>
<line x1="370" y1="148" x2="370" y2="170" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="5 4"/>
<circle cx="370" cy="190" r="20" fill="#ffffff" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="5 4"/>
<text x="370" y="197" text-anchor="middle" font-size="15" font-weight="600" fill="#4a5262">V</text>
<line x1="370" y1="210" x2="370" y2="228" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="5 4"/>
<line x1="370" y1="228" x2="230" y2="228" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="5 4"/>
<circle cx="370" cy="148" r="3.2" fill="#1f2937"/>
<circle cx="370" cy="228" r="3.2" fill="#1f2937"/>
<text x="398" y="194" font-size="12.5" font-weight="600" fill="#a8641a">100 kΩ</text>

<text x="230" y="252" text-anchor="middle" font-size="11.5" fill="#7b8494">attaching the meter changes the very circuit it is measuring</text>
</svg>
</figure>`,
  opts: ["5.0 V", "3.3 V", "6.7 V", "2.5 V", "10 V"],
  ans: 1,
  sol: `<p>A real voltmeter is a resistor, and connecting it changes the circuit
it is measuring. Model it as a parallel branch and re-solve.</p>
<div class="formula">100 kΩ ∥ 100 kΩ = 50 kΩ
total = 50 kΩ + 100 kΩ = 150 kΩ
V_reading = 10 × 50/150 = 3.33 V ≈ 3.3 V</div>
<p><b>Answer: B, 3.3 V.</b></p>
<p><b>The measured value is not the true value.</b> Before the meter is attached
each resistor carries 5 V. Attaching it puts a second path in parallel with one
of them, halves that branch's resistance, and so shifts the balance — the very
act of measuring pulls the answer down by a third. This is not a defect of the
meter, it is what measuring a circuit with a finite-resistance instrument does.</p>
<p><b>The traps.</b> Option A, 5.0 V, is the unloaded value: the answer you get
by treating the voltmeter as invisible. Option C, 6.7 V, assumes the other
resistor now takes the smaller share, reversing the divider. Option D, 2.5 V,
halves the unloaded value as though the two branches were now equal. Option E,
10 V, treats the meter as connected across the supply.</p>
<p><b>When the error is acceptable.</b> The rule of thumb is that the meter
resistance should be at least ten times the resistance it is measuring. Here it
is equal to it, which is about the worst practical case — and is exactly why
high-impedance circuits need electrometers or null methods rather than an
ordinary multimeter.</p>`,
},
{
  id: "H-16", module: "H", topic: "Maximum power transfer", diff: 3,
  q: `<p>A cell of emf 12 V and internal resistance 2.0 Ω is connected to a variable external resistor <code>R</code>. What is the maximum power that can be delivered to <code>R</code>?</p>
<figure class="fig">
<svg viewBox="0 0 460 240" role="img" aria-label="A 12 volt cell with internal resistance 2 ohms connected in a loop with a variable resistor R.">
<defs>
<marker id="vr-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
<path d="M0,0 L7,3.2 L0,6.4 z" fill="#1f2937"/>
</marker>
</defs>
<text x="230" y="24" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">A cell driving a variable load</text>

<line x1="90" y1="80" x2="200" y2="80" stroke="#1f2937" stroke-width="2"/>
<rect x="200" y="72" width="60" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="260" y1="80" x2="390" y2="80" stroke="#1f2937" stroke-width="2"/>
<line x1="188" y1="112" x2="268" y2="50" stroke="#1f2937" stroke-width="1.8" marker-end="url(#vr-ar)"/>
<text x="246" y="138" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">R, variable</text>

<line x1="390" y1="80" x2="390" y2="190" stroke="#1f2937" stroke-width="2"/>
<line x1="390" y1="190" x2="90" y2="190" stroke="#1f2937" stroke-width="2"/>
<line x1="90" y1="190" x2="90" y2="174" stroke="#1f2937" stroke-width="2"/>
<rect x="82" y="140" width="16" height="34" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="90" y1="140" x2="90" y2="120" stroke="#1f2937" stroke-width="2"/>
<line x1="82" y1="120" x2="98" y2="120" stroke="#1f2937" stroke-width="5"/>
<line x1="74" y1="106" x2="106" y2="106" stroke="#1f2937" stroke-width="2.5"/>
<line x1="90" y1="106" x2="90" y2="80" stroke="#1f2937" stroke-width="2"/>
<text x="118" y="111" font-size="12.5" font-weight="600" fill="#b3352f">ε = 12 V</text>
<text x="118" y="162" font-size="12.5" font-weight="600" fill="#b3352f">r = 2.0 Ω</text>

<text x="230" y="222" text-anchor="middle" font-size="11.5" fill="#7b8494">R can be set to any value; the question asks for the best one</text>
</svg>
</figure>`,
  opts: ["18 W", "36 W", "72 W", "9 W", "24 W"],
  ans: 0,
  sol: `<p>Power in <code>R</code> is maximal when <code>R</code> equals the
internal resistance. That is the maximum-power theorem, and it is worth
verifying rather than only quoting.</p>
<div class="formula">P = E²R/(R + r)²
dP/dR = 0  ⇒  R = r = 2.0 Ω
P_max = E²/(4r) = 144 / (4 × 2.0) = 144/8 = 18 W</div>
<p><b>Answer: A, 18 W.</b></p>
<p><b>Why the condition is <code>R = r</code>.</b> Make <code>R</code> very small
and the current is large but almost all the power is wasted inside the cell. Make
<code>R</code> very large and little power is wasted internally but the current is
tiny. The best compromise sits where the two resistances are equal — the point
where the external and internal dissipations balance.</p>
<p><b>The traps.</b> Option B, 36 W, uses <code>E²/(2r)</code>. Option C, 72 W,
is <code>E²/r</code>, the short-circuit dissipation, which is the largest power
the cell can produce but almost none of it reaches <code>R</code>. Option D,
9 W, uses <code>E²/(8r)</code> — a factor of two out. Option E, 24 W, divides by
6 instead of 8.</p>
<p><b>Efficiency is something else.</b> At maximum power the efficiency is only
50%, because the internal resistance dissipates exactly as much as the load. Power
supplies are therefore <i>not</i> designed to run at the maximum-power point;
they use a much lower internal resistance so that most of the power, not half of
it, reaches the load.</p>`,
},

/* ===================== MODULE I — capacitors ===================== */

{
  id: "I-05", module: "I", topic: "Capacitors in series", diff: 2,
  q: "A capacitor of capacitance <code>C</code> and one of capacitance <code>2C</code> are connected in series across a battery. What is the ratio of the pd across <code>C</code> to the pd across <code>2C</code>?",
  opts: ["1 : 4", "1 : 2", "1 : 1", "4 : 1", "2 : 1"],
  ans: 4,
  sol: `<p>In series the charge on both capacitors is the same, so the formula
with <code>Q</code> in it is the one that matters.</p>
<div class="formula">V = Q/C
V_C : V_2C = (Q/C) : (Q/2C) = 1 : ½ = 2 : 1</div>
<p><b>Answer: E, 2 : 1.</b> The smaller capacitor takes the larger share of the
voltage.</p>
<p><b>Why the charge is the same.</b> The two inner plates are isolated from the
battery; charge can only move onto one by leaving the other, so whatever appears
on one appears on the other in equal magnitude. That single observation is what
makes series capacitor problems tractable, and it is why the voltage then divides
in inverse proportion to capacitance.</p>
<p><b>The traps.</b> Option B, 1 : 2, says the bigger capacitor takes more
voltage — the opposite of the truth, and the error you get from thinking of
capacitance as if it were resistance in a divider. Option C, 1 : 1, would mean
equal capacitance. Option D, 4 : 1, squares the ratio. Option A, 1 : 4, is both
errors together.</p>
<p><b>The practical consequence.</b> Capacitors in series have a voltage rating
set by the smallest one, because it hogs the pd. Two nominally identical
capacitors in series across a supply do <i>not</i> reliably share the voltage
equally — manufacturing tolerances mean the smaller one takes more and can be
pushed past its rating. Balancing resistors are used to stop exactly that.</p>`,
},
{
  id: "I-06", module: "I", topic: "RC discharge", diff: 3,
  q: "A capacitor discharges through a resistor. How long does it take for its charge to fall to one eighth of its initial value? Give your answer in terms of the time constant <code>RC</code>.",
  opts: ["3 RC", "8 RC", "2.1 RC", "0.69 RC", "1.4 RC"],
  ans: 2,
  sol: `<p>Discharge is exponential: <code>Q = Q₀ e<sup>−t/RC</sup></code>. Set the ratio
and take logs. Because <code>⅛ = 2⁻³</code> you can also do it by halvings.</p>
<div class="formula">Q/Q₀ = ⅛ = e<sup>−t/RC</sup>
ln(⅛) = −t/RC   ⇒   t = RC × ln 8 = RC × 2.079 ≈ 2.1 RC

check by halvings: half-life = RC ln 2 = 0.693 RC
three halvings: 3 × 0.693 RC = 2.08 RC  ✓</div>
<p><b>Answer: C, 2.1 RC.</b></p>
<p><b>Two routes, same answer — use the one you can check.</b> The logarithm
route is general; the halving route is faster whenever the target fraction is a
power of two, and it gives you a sanity check for free. Doing both and comparing
is cheap insurance.</p>
<p><b>The traps.</b> Option B, 8 RC, treats the decay as linear: "eight times
smaller so eight time constants". Exponential decay never behaves that way — the
first time constant only removes 63% of the charge. Option A, 3 RC, counts three
halvings and then uses <code>RC</code> as the half-life instead of
<code>0.693 RC</code>. Option D, 0.69 RC, is one half-life, which reaches a half,
not an eighth. Option E, 1.4 RC, is two half-lives, reaching a quarter.</p>
<p><b>An anchor worth keeping.</b> <code>ln 2 ≈ 0.693</code>, so the half-life is
about 0.7 time constants; and every additional half-life adds the same 0.7. That
lets you estimate any discharge question in your head to within a few per cent.</p>`,
},
{
  id: "I-07", module: "I", topic: "Charge sharing", diff: 3,
  q: "A capacitor of capacitance <code>C</code> is charged to a pd <code>V</code> and then disconnected from the source. It is then connected in parallel with an uncharged capacitor of capacitance <code>2C</code>, positive plate to positive plate. What fraction of the original stored energy remains?",
  opts: ["1/6", "1/2", "2/3", "1/9", "1/3"],
  ans: 4,
  sol: `<p>Charge is conserved; energy is not. Work out the new pd from the
charge, then recompute the energy — do not try to conserve both.</p>
<div class="formula">initial charge:  Q = CV
combined capacitance:  C + 2C = 3C
new pd:  V' = Q/(3C) = V/3
final energy:  E' = ½(3C)(V/3)² = ½ × 3C × V²/9 = CV²/6
initial energy: E = ½CV²
E'/E = (CV²/6) / (½CV²) = ⅓</div>
<p><b>Answer: E, 1/3.</b></p>
<p><b>Where the other two thirds went.</b> They are dissipated as heat in the
connecting wires and as a spark at the moment of connection. Sharing charge
between capacitors is irreversible: you can never get the original energy back by
reversing the process. This is the standard trap in capacitor problems — charge is
conserved and energy is not, and applying conservation to both gives
contradictory answers.</p>
<p><b>The traps.</b> Option B, 1/2, and option C, 2/3, come from assuming the
energy is shared in proportion to capacitance, as though it were a conserved
substance being poured from one vessel into another. Option D, 1/9, squares the
voltage ratio and forgets that the capacitance went up to <code>3C</code>.
Option A, 1/6, is the ratio of the final energy to <code>CV²</code> rather than to
<code>½CV²</code> — right arithmetic, wrong denominator.</p>
<p><b>A faster route.</b> With <code>Q</code> fixed, <code>E = Q²/(2C)</code>.
Capacitance tripled, so the energy fell to a third. One line instead of four, and
it makes the answer obvious from the start.</p>`,
},
{
  id: "I-08", module: "I", topic: "Dielectric", diff: 2,
  q: "A parallel-plate capacitor with air between its plates is filled with a dielectric of relative permittivity 4 while it remains connected to a battery of fixed pd. What happens to the energy stored?",
  opts: ["It doubles", "It quadruples", "It is unchanged", "It falls to a quarter", "It falls to a half"],
  ans: 1,
  sol: `<p>The battery being connected is the decisive detail: it holds
<code>V</code> fixed while <code>C</code> changes, so the stored energy follows
<code>C</code>.</p>
<div class="formula">C' = εᵣ C = 4C        (V held constant)
E' = ½ C' V² = ½ (4C) V² = 4 × (½CV²) = 4E</div>
<p><b>Answer: B, it quadruples.</b></p>
<p><b>The same question has the opposite answer if you disconnect the battery
first.</b> Then <code>Q</code> is fixed, <code>E = Q²/(2C)</code>, and quadrupling the
capacitance gives <code>E' = E/4</code>. Two versions of one
question, opposite answers, and the only difference is whether the battery is
still attached. If a dielectric question does not tell you which, it is
unanswerable.</p>
<p><b>Why the energy rises here.</b> The dielectric is pulled into the gap by the
field, and as the capacitance rises the battery pushes additional charge onto the
plates. The battery supplies energy, which is why the stored energy can increase
even though nothing about the geometry got bigger.</p>
<p><b>The traps.</b> Option A, doubles, uses <code>√εᵣ</code>. Option C,
unchanged, treats capacitance and energy as independent. Option D, a quarter, is
the correct answer to the <i>disconnected</i> version — very frequently given
when the question says "connected". Option E, a half, halves instead of
quartering.</p>
<p><b>How to avoid the whole family of errors.</b> Write <code>½CV²</code>, then
immediately substitute whichever of <code>C</code> or <code>V</code> is
<i>not</i> fixed — using <code>C = Q/V</code> — before doing anything else. Here
that gives <code>½QV</code> with <code>V</code> fixed and <code>Q ∝ C</code>, so
the answer is four.</p>`,
},
{
  id: "I-09", module: "I", topic: "Charge sharing with numbers", diff: 3,
  q: "A 6.0 μF capacitor is charged to 12 V, disconnected, and then connected across an uncharged 3.0 μF capacitor, positive to positive. What is the final pd across the combination?",
  opts: ["4.0 V", "12 V", "6.0 V", "8.0 V", "9.0 V"],
  ans: 3,
  sol: `<p>Charge is conserved and the two capacitors end up at the same pd.
Write both facts down and solve.</p>
<div class="formula">initial charge: Q = CV = 6.0 μF × 12 V = 72 μC
total capacitance: 6.0 + 3.0 = 9.0 μF
final pd: V' = Q/C_total = 72 μC / 9.0 μF = 8.0 V</div>
<p><b>Answer: D, 8.0 V.</b></p>
<p><b>What "positive to positive" buys you.</b> It tells you the charges add
rather than partially cancel, so the total charge available to redistribute is the
full 72 μC. Connected positive to negative instead, the charges would subtract and
the final pd would be <code>(72 − 36)/9.0 = 4.0 V</code> — exactly option A. The
orientation is not decoration.</p>
<p><b>The traps.</b> Option B, 12 V, assumes the pd is unchanged, which would
violate charge conservation — the combined plates cannot hold 72 μC at 12 V when
their capacitance is 9 μF. Option C, 6.0 V, halves it, treating the two
capacitors as if they were equal. Option E, 9.0 V, uses the capacitance ratio
directly instead of computing the charge.</p>
<p><b>The check that catches everything.</b> After sharing, the 6 μF capacitor
holds <code>6 × 8 = 48 μC</code> and the 3 μF holds <code>3 × 8 = 24 μC</code>,
totalling 72 μC — the original charge. If your final pd does not reproduce the
initial charge when you multiply it back through, it is wrong.</p>`,
},

/* ===================== MODULE J — thermal ===================== */

{
  id: "J-05", module: "J", topic: "Combined gas law ratio", diff: 3,
  q: "A fixed mass of ideal gas has pressure <code>P</code> and volume <code>V</code> at absolute temperature <code>T</code>. The volume is doubled and the absolute temperature is halved. What is the new pressure?",
  opts: ["4P", "P/2", "P", "2P", "P/4"],
  ans: 4,
  sol: `<p>For a fixed mass, <code>PV/T</code> is constant. Rearranging before
substituting keeps the signs straight.</p>
<div class="formula">P' = P × (V/V') × (T'/T)
V' = 2V  ⇒  factor ½
T' = T/2 ⇒  factor ½
P' = P × ½ × ½ = P/4</div>
<p><b>Answer: E, P/4.</b></p>
<p><b>Both changes push the pressure down.</b> Doubling the volume on its own
halves the pressure — molecules hit the walls less often. Halving the absolute
temperature on its own halves it again — they hit the walls less hard, and less
often. So the factors multiply rather than cancel. The instinct that "one goes up
and one goes down, so it cancels" is wrong twice over here, because neither
change is in the numerator.</p>
<p><b>The traps.</b> Option B, P/2, applies one change. Option C, P, assumes
cancellation. Option D, 2P, and option A, 4P, have at least one factor inverted —
most often from reading "temperature halved" as doubling the pressure because
pressure and temperature are proportional. They are, but only when the volume is
held fixed, which it is not.</p>
<p><b>Write the rearranged form, not the original.</b> Going straight from
<code>PV/T = constant</code> invites exactly the inversion errors above.
Expressing the unknown as
<code>P' = P (V/V')(T'/T)</code> makes each factor's direction visible before you
touch a number.</p>`,
},
{
  id: "J-06", module: "J", topic: "Molecular speeds", diff: 3,
  q: "The rms speed of the molecules of gas X, of molar mass <code>M</code>, is <code>v</code> at a certain temperature. Gas Y has molar mass <code>4M</code> and is at the same temperature. What is the rms speed of the molecules of Y?",
  opts: ["v/16", "v/4", "2v", "v", "v/2"],
  ans: 4,
  sol: `<p>Equipartition gives <code>½ m c² = (3/2) kT</code>, so at a fixed
temperature the mean square speed is inversely proportional to molecular mass.</p>
<div class="formula">c_rms ∝ 1/√m
c_Y / c_X = √(M / 4M) = √(1/4) = ½
c_Y = v/2</div>
<p><b>Answer: E, v/2.</b></p>
<p><b>Same temperature means same kinetic energy, not same speed.</b> That is the
whole idea. A heavy molecule at the same temperature as a light one is moving
more slowly, by exactly the factor that keeps <code>½mc²</code> equal. Confusing
"same temperature" with "same speed" is the single most common conceptual error
in this topic.</p>
<p><b>The traps.</b> Option B, v/4, uses <code>1/m</code> instead of
<code>1/√m</code> — a very common slip, because the kinetic energy really is
linear in <code>m</code> while the speed is not. Option C, 2v, inverts the ratio.
Option D, v, assumes equal speeds. Option A, v/16, squares the square-root
relationship.</p>
<p><b>Why this matters physically.</b> The mass dependence of molecular speed is
what makes gaseous diffusion and effusion mass-selective, and it is why
Graham's law of effusion has the same square-root form. It is also why hydrogen,
not oxygen, leaks out of a balloon faster.</p>`,
},
{
  id: "J-07", module: "J", topic: "Mixing", diff: 3,
  q: "A 2.0 kg block of copper at 100 °C is dropped into 3.0 kg of water at 20 °C. There are no heat losses to the surroundings. Taking <code>c</code>(copper) = 400 J kg⁻¹ K⁻¹ and <code>c</code>(water) = 4200 J kg⁻¹ K⁻¹, what is the final temperature?",
  opts: ["35 °C", "30 °C", "20 °C", "25 °C", "22 °C"],
  ans: 3,
  sol: `<p>Energy lost by the copper equals energy gained by the water. Set that
up with the final temperature as the unknown and solve.</p>
<div class="formula">2.0 × 400 × (100 − T) = 3.0 × 4200 × (T − 20)
800(100 − T) = 12 600(T − 20)
80 000 − 800T = 12 600T − 252 000
332 000 = 13 400 T
T = 24.8 °C ≈ 25 °C</div>
<p><b>Answer: D, 25 °C.</b></p>
<p><b>Compare the heat capacities first, and the answer stops surprising you.</b>
The copper can supply <code>2.0 × 400 = 800 J K⁻¹</code>; the water absorbs
<code>3.0 × 4200 = 12 600 J K⁻¹</code>. The water's heat capacity is nearly
sixteen times larger, so even boiling-hot copper barely moves it. Expect an
answer close to 20 °C, and any option near 60 °C is immediately
implausible.</p>
<p><b>The traps.</b> Option B, 30 °C, and option A, 35 °C, come from using the
same specific heat capacity for both substances, which throws away the entire
point of the question. Option C, 20 °C, means no heat was transferred at all.
Option E, 22 °C, is the result of a slip in the temperature differences —
typically writing <code>(T − 100)</code> for the copper.</p>
<p><b>Two habits that prevent almost every error here.</b> Write the heat
<i>capacity</i> (<code>m × c</code>) for each body before writing the equation,
and make sure each bracket is (hotter − colder) so that both sides are positive.
Doing both turns this into a one-line solve.</p>`,
},
{
  id: "J-08", module: "J", topic: "Isothermal compression", diff: 3,
  q: "A fixed mass of ideal gas occupies 2.0 × 10⁻³ m³ at a pressure of 1.0 × 10⁵ Pa. It is compressed <i>isothermally</i> until its pressure is 4.0 × 10⁵ Pa. What is its new volume?",
  opts: ["8.0 × 10⁻³ m³", "5.0 × 10⁻⁴ m³", "1.0 × 10⁻³ m³", "2.5 × 10⁻⁴ m³", "4.0 × 10⁻⁴ m³"],
  ans: 1,
  sol: `<p>"Isothermal" is the instruction that selects which gas law to use:
constant temperature means Boyle's law, <code>PV = constant</code>.</p>
<div class="formula">P₁V₁ = P₂V₂
V₂ = P₁V₁/P₂ = (1.0 × 10⁵ × 2.0 × 10⁻³) / (4.0 × 10⁵)
   = 200 / (4.0 × 10⁵) = 5.0 × 10⁻⁴ m³</div>
<p><b>Answer: B, 5.0 × 10⁻⁴ m³.</b></p>
<p><b>The word "isothermal" carries the physics.</b> Holding the temperature
fixed while compressing means heat must leave the gas — the work done on it would
otherwise raise its temperature. So isothermal compression is necessarily slow
and necessarily involves heat transfer to a reservoir. If the compression were
adiabatic instead, the temperature would rise and the final volume would be
different, because a third variable would be in play.</p>
<p><b>The traps.</b> Option A, 8.0 × 10⁻³ m³, multiplies by the pressure ratio
instead of dividing — it says compressing a gas makes it bigger. Option C,
1.0 × 10⁻³ m³, halves the volume once rather than by the factor of four the
pressure ratio demands. Option D, 2.5 × 10⁻⁴ m³, halves again. Option E,
4.0 × 10⁻⁴ m³, uses the pressure ratio directly on the mantissa.</p>
<p><b>Always check the direction.</b> Pressure went up by a factor of four, so
volume must come down by a factor of four:
<code>2.0 × 10⁻³ / 4 = 0.5 × 10⁻³ = 5.0 × 10⁻⁴</code>. That one line is the whole
question, and it is worth doing before reaching for the formula.</p>`,
},
{
  id: "J-09", module: "J", topic: "Latent heat", diff: 2,
  q: "A 2.0 kW kettle contains 1.5 kg of water initially at 20 °C. Ignoring heat losses, how long does it take to bring the water to the boil and then boil away 0.20 kg of it? Take <code>c</code>(water) = 4200 J kg⁻¹ K⁻¹ and the specific latent heat of vaporisation as 2.26 MJ kg⁻¹.",
  opts: ["960 s", "250 s", "730 s", "480 s", "120 s"],
  ans: 3,
  sol: `<p>Two distinct stages, added. There is no single formula that covers
both, which is precisely the point.</p>
<div class="formula">stage 1 — heat the water to 100 °C:
  Q₁ = mcΔT = 1.5 × 4200 × 80 = 504 000 J
stage 2 — vaporise 0.20 kg at 100 °C:
  Q₂ = mL = 0.20 × 2.26 × 10⁶ = 452 000 J
total: Q = 956 000 J
t = Q/P = 956 000 / 2000 = 478 s ≈ 480 s</div>
<p><b>Answer: D, 480 s.</b></p>
<p><b>The two stages are comparable in size, and that is the surprise.</b>
Boiling away just 13% of the water takes almost as long as heating all of it by
80 K. Latent heats are large — 2.26 MJ kg⁻¹ is roughly five times the energy
needed to heat water from freezing to boiling — so vaporisation dominates
whenever a meaningful mass is involved. Knowing that lets you spot a wildly wrong
answer instantly.</p>
<p><b>The traps.</b> Option B, 250 s, is stage 1 only. Option E, 120 s, is stage
2 alone. Option A, 960 s, doubles the total, usually from applying the 1.5 kg to
the latent-heat stage as well as the heating stage. Option C, 730 s, is a partial
sum with an arithmetic slip.</p>
<p><b>Where the temperature goes in each stage.</b> Heating uses
<code>ΔT</code> and no latent heat; boiling uses <code>L</code> and no
<code>ΔT</code>. Mixing them — writing <code>mc(100 − 20) + 0.20 × 4200 ×
something</code> — is the standard failure. Keep the two lines separate and the
question is mechanical.</p>`,
},

/* ===================== MODULE K — nuclear ===================== */

{
  id: "K-06", module: "K", topic: "Half-life from data", diff: 2,
  q: "The activity of a radioactive sample falls from 800 Bq to 100 Bq in 12 hours. What is the half-life of the sample?",
  opts: ["6 h", "3 h", "4 h", "12 h", "2 h"],
  ans: 2,
  sol: `<p>Count how many halvings take you from 800 to 100, then divide the
elapsed time by that count. No logarithms are needed when the numbers are this
clean.</p>
<div class="formula">800 → 400 → 200 → 100
that is 3 half-lives in 12 h
T½ = 12 / 3 = 4 h</div>
<p><b>Answer: C, 4 h.</b></p>
<p><b>Why counting halvings works.</b> Each half-life is the same length of time
and each one halves the activity, so the number of halvings is just the number of
times you can divide by two before arriving at the final value. When the ratio is
an exact power of two this is far faster — and far less error-prone — than
setting up an exponential and taking logs.</p>
<p><b>The traps.</b> Option B, 3 h, reports the number of halvings rather than
the length of one. Option A, 6 h, counts two halvings, which would take 800 down
to 200 rather than 100. Option D, 12 h, counts a single halving. Option E, 2 h,
counts six halvings, which would leave 12.5 Bq.</p>
<p><b>When you do need the formula.</b> If the ratio is not a power of two — say
800 to 150 — you must use <code>A = A₀ e<sup>−λt</sup></code> with
<code>λ = ln 2 / T½</code>. But the halving count still gives you a bracket to
check the answer against: three half-lives gives 100, so the half-life must be a
little over 4 h.</p>`,
},
{
  id: "K-07", module: "K", topic: "Decay constant", diff: 3,
  q: "A radioactive isotope has decay constant <code>λ</code>. What is its half-life?",
  opts: ["0.693/λ", "λ/0.693", "1/λ", "0.693 λ", "2/λ"],
  ans: 0,
  sol: `<p>Start from the exponential law and set the activity to half.</p>
<div class="formula">N = N₀ e<sup>−λt</sup>
N = N₀/2  ⇒  e<sup>−λt</sup> = ½  ⇒  λt = ln 2
T½ = ln 2 / λ = 0.693 / λ</div>
<p><b>Answer: A, 0.693/λ.</b></p>
<p><b>The distinction that catches people out.</b> <code>1/λ</code> is <i>not</i>
the half-life — it is the <b>mean lifetime</b> <code>τ</code>, the average time a
nucleus survives before decaying. The two differ by a factor of
<code>ln 2 ≈ 0.693</code>: the half-life is shorter, because in an exponential
distribution the median is below the mean. Confusing them is the single most
common slip on this topic, which is why option C is there.</p>
<p><b>The traps.</b> Option B, λ/0.693, inverts the relationship — dimensionally
it gives a rate, not a time, and checking units would rule it out immediately.
Option D, 0.693 λ, multiplies instead of divides and has units of s⁻¹. Option E,
2/λ, uses 2 rather than ln 2.</p>
<p><b>The dimensional check.</b> <code>λ</code> has units s⁻¹, so a half-life
must be <code>constant / λ</code>. That alone eliminates three of the five
options before you start, and it is a habit worth applying to every formula you
quote.</p>`,
},
{
  id: "K-08", module: "K", topic: "Alpha decay equation", diff: 2,
  q: "A uranium-238 nucleus (<code>²³⁸₉₂U</code>) decays by alpha emission. What is the resulting nuclide?",
  opts: ["²³⁴₉₂U", "²³⁴₉₀Th", "²³⁶₉₀Th", "²³⁸₉₀Th", "²³²₈₈Ra"],
  ans: 1,
  sol: `<p>An alpha particle is a helium nucleus, <code>⁴₂He</code>. Both the
nucleon number and the proton number are conserved, so subtract 4 from the top
and 2 from the bottom.</p>
<div class="formula">²³⁸₉₂U → ᴬZX + ⁴₂He
A: 238 = A + 4   ⇒  A = 234
Z: 92  = Z + 2   ⇒  Z = 90   (thorium)
²³⁸₉₂U → ²³⁴₉₀Th + ⁴₂He</div>
<p><b>Answer: B, ²³⁴₉₀Th.</b></p>
<p><b>Two conservation laws, checked separately.</b> Nucleon number (top) and
charge or proton number (bottom) must each balance. Doing them as two separate
one-line subtractions is much safer than trying to recall the product. And the
element is fixed by the <i>proton</i> number: 90 is thorium, whatever the mass
number says.</p>
<p><b>The traps.</b> Option A, ²³⁴₉₂U, subtracts 4 from the nucleon number but
leaves the proton number alone — a decay that would violate charge conservation
outright. Option C, ²³⁶₉₀Th, takes 2 from the top as well. Option D, ²³⁸₉₀Th,
leaves the nucleon number unchanged. Option E, ²³²₈₈Ra, is the product of
<i>two</i> successive alpha decays.</p>
<p><b>Beta decay is the mirror image.</b> In β⁻ decay a neutron becomes a proton,
so the nucleon number is unchanged and the proton number goes <i>up</i> by one.
Keeping the two processes distinct — alpha moves you down-left in the chart,
beta-minus moves you right — prevents most bookkeeping errors in decay-chain
problems.</p>`,
},
{
  id: "K-09", module: "K", topic: "Activity ratio", diff: 3,
  q: "Two samples, X and Y, are of the same radioactive isotope. Initially their activities are in the ratio 4 : 1. What is the ratio of their activities after one half-life has elapsed?",
  opts: ["8 : 1", "2 : 1", "4 : 1", "1 : 1", "16 : 1"],
  ans: 2,
  sol: `<p>Exponential decay is multiplicative: after one half-life <i>every</i>
sample has halved, whatever it started at.</p>
<div class="formula">A_X → ½ A_X ,  A_Y → ½ A_Y
A_X' : A_Y' = (½ × 4) : (½ × 1) = 2 : 0.5 = 4 : 1</div>
<p><b>Answer: C, 4 : 1.</b> Unchanged.</p>
<p><b>The point behind the question.</b> The sample with the larger activity does
lose more nuclei per second in absolute terms — four times as many, in fact. But
it also has four times as many nuclei to lose, so the <i>fraction</i> that decays
per second is identical. The half-life depends on the isotope and on nothing else:
not the mass, not the activity, not the chemical form.</p>
<p><b>The traps.</b> Option B, 2 : 1, halves the ratio itself, as though the
bigger sample were decaying faster in relative terms. Option A, 8 : 1, doubles it.
Option D, 1 : 1, assumes the two converge — which would require the smaller sample
to decay more slowly. Option E, 16 : 1, squares the ratio.</p>
<p><b>Why this matters in practice.</b> It is what makes radiometric dating
possible at all: two samples of the same isotope, whatever their sizes, always
carry the same clock. And it is why you cannot reduce radioactivity by splitting a
sample up.</p>`,
},
{
  id: "K-10", module: "K", topic: "Decay chain", diff: 3,
  q: "A <code>²³⁸₉₂U</code> nucleus decays to <code>²⁰⁶₈₂Pb</code> through a chain involving only alpha and beta-minus decays. How many alpha decays occur in the chain?",
  opts: ["6", "8", "7", "10", "4"],
  ans: 1,
  sol: `<p>Only alpha decay changes the nucleon number, so the mass difference
gives the alpha count immediately. The proton number then fixes the number of
beta decays, and checking it is what confirms the answer.</p>
<div class="formula">ΔA = 238 − 206 = 32
each alpha removes 4  ⇒  number of alphas = 32/4 = 8

check with Z:
8 alphas remove 16 protons:  92 − 16 = 76
need Z = 82, so 82 − 76 = 6 beta-minus decays (each adds 1)  ✓</div>
<p><b>Answer: B, 8.</b></p>
<p><b>Solve on the quantity only one process touches.</b> Alpha decay changes
<code>A</code> by 4 and <code>Z</code> by 2; beta-minus changes <code>Z</code> by
+1 and leaves <code>A</code> alone. Because <code>A</code> is affected by alphas
only, it gives the alpha count directly, with no simultaneous equations. Then
<code>Z</code> confirms it. Doing it in that order is the trick.</p>
<p><b>The traps.</b> Option A, 6, is the number of <i>beta</i> decays — a
perfectly correct calculation of a different quantity, which is exactly why the
question asks for one specifically. Option C, 7, and option D, 10, are arithmetic
slips in the division. Option E, 4, divides 206 by something rather than taking
the difference.</p>
<p><b>The physical check.</b> Eight alpha decays is a lot — it is why the
uranium series passes through so many intermediates before settling at lead, and
why the chain emits far more alpha radiation than a single-step decay would.</p>`,
},

/* ===================== MODULE L — quantum and photons ===================== */

{
  id: "L-06", module: "L", topic: "Photoelectric effect", diff: 3,
  q: "Light of wavelength 200 nm is incident on a metal of work function 4.0 eV. What is the maximum kinetic energy of the emitted electrons?",
  opts: ["4.0 eV", "2.2 eV", "6.2 eV", "10.2 eV", "1.6 eV"],
  ans: 1,
  sol: `<p>Einstein's photoelectric equation, with the photon energy found from
<code>hc/λ</code>. Working in electron-volts keeps the arithmetic small.</p>
<div class="formula">E = hc/λ = 1240 eV nm / 200 nm = 6.2 eV
hf = φ + K_max
K_max = 6.2 − 4.0 = 2.2 eV</div>
<p><b>Answer: B, 2.2 eV.</b></p>
<p><b>The constant that makes this quick.</b> <code>hc = 1240 eV nm</code>.
Wavelength in nanometres divided into 1240 gives photon energy in electron-volts
directly, with no powers of ten to lose. It is worth memorising alongside
<code>hc = 1.99 × 10⁻²⁵ J m</code>, which is the same fact in SI.</p>
<p><b>The traps.</b> Option A, 4.0 eV, is the work function — the energy needed to
escape, not the energy left over. Option C, 6.2 eV, is the photon energy, i.e.
the answer if the work function were zero. Option D, 10.2 eV, adds the two instead
of subtracting. Option E, 1.6 eV, is a slip in the division.</p>
<p><b>What the "maximum" is doing there.</b> 4.0 eV is the <i>minimum</i> energy an
electron needs to leave. Electrons bound below the surface lose more on the way
out, so 2.2 eV is an upper bound and the emitted electrons have a spread of
energies up to it. That spread, not the maximum, is what misled classical
physicists.</p>`,
},
{
  id: "L-07", module: "L", topic: "Photon energy ratio", diff: 2,
  q: "Photon P has wavelength 400 nm and photon Q has wavelength 600 nm. What is the ratio of the energy of P to the energy of Q?",
  opts: ["1 : 1", "2 : 3", "9 : 4", "4 : 9", "3 : 2"],
  ans: 4,
  sol: `<p>Photon energy is <code>E = hc/λ</code>, so it is inversely
proportional to wavelength. Inverting the wavelength ratio is the whole
question.</p>
<div class="formula">E_P / E_Q = λ_Q / λ_P = 600 / 400 = 3/2
E_P : E_Q = 3 : 2</div>
<p><b>Answer: E, 3 : 2.</b> The shorter wavelength carries more energy.</p>
<p><b>Shorter wavelength means higher frequency means more energy.</b> The chain
<code>λ ↓ ⇒ f ↑ ⇒ E ↑</code> is worth running in words every time, because the
reciprocal relationship is easy to invert under pressure. Blue light at 400 nm is
more energetic than red light at 600 nm, which is why ultraviolet causes damage
that visible light does not.</p>
<p><b>The traps.</b> Option B, 2 : 3, uses the wavelength ratio directly and
forgets to invert it — the single most common error here. Option C, 9 : 4, squares
the correct ratio. Option D, 4 : 9, squares the inverted one. Option A, 1 : 1,
treats photon energy as independent of wavelength, which would make the whole
spectrum uniform.</p>
<p><b>The frequency route gives the same answer.</b>
<code>f_P = c/400</code> and <code>f_Q = c/600</code>, so
<code>f_P/f_Q = 600/400 = 3/2</code>, and since <code>E = hf</code> the energy
ratio is identical. Two derivations, one answer — use whichever you find harder
to get wrong.</p>`,
},
{
  id: "L-08", module: "L", topic: "Photon rate", diff: 3,
  q: "A 10 mW laser emits light of wavelength 500 nm. How many photons does it emit each second?",
  opts: ["1.3 × 10¹⁶ s⁻¹", "5.0 × 10¹⁶ s⁻¹", "2.5 × 10¹⁶ s⁻¹", "2.5 × 10¹⁹ s⁻¹", "4.0 × 10¹⁶ s⁻¹"],
  ans: 2,
  sol: `<p>Power is energy per second, so divide the total energy delivered each
second by the energy of one photon.</p>
<div class="formula">E_photon = hc/λ = (6.63 × 10⁻³⁴ × 3.00 × 10⁸)/(500 × 10⁻⁹)
          = 1.989 × 10⁻²⁵ / 5.00 × 10⁻⁷ = 3.98 × 10⁻¹⁹ J
P = 10 mW = 1.0 × 10⁻² J s⁻¹
N = P/E = 1.0 × 10⁻² / 3.98 × 10⁻¹⁹ = 2.5 × 10¹⁶ s⁻¹</div>
<p><b>Answer: C, 2.5 × 10¹⁶ s⁻¹.</b></p>
<p><b>The one conversion that matters.</b> Ten milliwatts is
<code>1.0 × 10⁻²</code> watts, not 10 watts. Getting that wrong shifts the answer
by three orders of magnitude, which is exactly what option D is. Every power-of-ten
error in photon questions comes from a prefix, not from the physics.</p>
<p><b>The traps.</b> Option B, 5.0 × 10¹⁶, doubles the photon energy or halves the
wavelength. Option A, 1.3 × 10¹⁶, uses 1000 nm in the photon energy. Option D,
2.5 × 10¹⁹, reads 10 mW as 10 W. Option E, 4.0 × 10¹⁶, inverts the photon-energy
division.</p>
<p><b>Why the number is so enormous.</b> A single visible photon carries only
about 4 × 10⁻¹⁹ J, so even a faint 10 mW beam involves tens of quadrillions of
them every second. That is why photon-counting experiments need heavily attenuated
sources and why the graininess of light is invisible in everyday experience.</p>`,
},
{
  id: "L-09", module: "L", topic: "de Broglie ratio", diff: 3,
  q: "An electron and a proton have the same kinetic energy. Taking the proton mass to be 1836 times the electron mass, what is the ratio of the de Broglie wavelength of the electron to that of the proton?",
  opts: ["about 43 : 1", "about 1836 : 1", "about 1 : 43", "about 1 : 1", "about 6.6 : 1"],
  ans: 0,
  sol: `<p>De Broglie wavelength is <code>λ = h/p</code>, and momentum is not the
same thing as kinetic energy. Express <code>p</code> in terms of
<code>E_k</code> first.</p>
<div class="formula">E_k = p²/(2m)   ⇒   p = √(2m E_k)
λ = h/√(2m E_k)     ⇒   λ ∝ 1/√m   (at fixed E_k)
λ_e / λ_p = √(m_p/m_e) = √1836 = 42.8 ≈ 43</div>
<p><b>Answer: A, about 43 : 1.</b></p>
<p><b>The square root is the entire question.</b> At equal kinetic energy the
heavier particle has more momentum, by a factor of <code>√1836</code>, not
<code>1836</code>. So the proton's wavelength is only 43 times smaller, not
1836 times smaller. Missing the square root is the standard error and option B
is built for it.</p>
<p><b>The traps.</b> Option B, 1836 : 1, uses the mass ratio directly. Option C,
1 : 43, gets the square root right and then inverts the ratio — the electron is
lighter so it must have the <i>longer</i> wavelength. Option D, 1 : 1, assumes
equal energy means equal wavelength, which is only true for equal masses.
Option E, 6.6 : 1, uses a cube root or mixes up the powers.</p>
<p><b>Why this matters experimentally.</b> Electron microscopes work precisely
because the electron's wavelength at a given accelerating voltage is tens of
times shorter than a proton's would be at the same energy — short enough to
resolve structures far below the wavelength of visible light.</p>`,
},
{
  id: "L-10", module: "L", topic: "Energy levels", diff: 3,
  q: "The energy levels of a certain atom are −10.0 eV, −4.0 eV and −1.5 eV. An electron makes a transition from the −1.5 eV level to the −4.0 eV level. What is the wavelength of the photon emitted?",
  opts: ["830 nm", "310 nm", "500 nm", "250 nm", "1240 nm"],
  ans: 2,
  sol: `<p>The photon carries away the <i>difference</i> between the two levels,
and then <code>λ = hc/E</code>. Two steps, and the first is where the sign
errors live.</p>
<div class="formula">ΔE = (−1.5) − (−4.0) = 2.5 eV
λ = hc/ΔE = 1240 eV nm / 2.5 eV = 496 nm ≈ 500 nm</div>
<p><b>Answer: C, 500 nm.</b></p>
<p><b>The bound-state energies are negative, and that is what confuses people.</b>
An electron dropping from −1.5 eV to −4.0 eV is moving to a <i>lower</i> energy —
more tightly bound — so the difference is <code>2.5 eV</code> released as a
photon. Taking the difference the wrong way round gives −2.5 eV, and a negative
photon energy is an immediate signal that the subtraction is inverted.</p>
<p><b>The traps.</b> Option B, 310 nm, uses the 4.0 eV level as the gap. Option A,
830 nm, uses the 1.5 eV level. Both come from reading a level energy as a
transition energy. Option D, 250 nm, doubles the gap. Option E, 1240 nm, uses
1.0 eV — the difference between −1.5 and −10 taken naively.</p>
<p><b>The check that settles it.</b> A 2.5 eV photon sits in the visible
spectrum, around green. Deep ultraviolet would need several eV and infrared well
under 1 eV, so any answer far from a few hundred nanometres deserves a second
look.</p>`,
},

/* ===================== MODULE M — fluids ===================== */

{
  id: "M-05", module: "M", topic: "Hydrostatic pressure ratio", diff: 2,
  q: "Two columns hold different liquids. Column 1 has density <code>ρ</code> and height <code>2h</code>. Column 2 has density <code>2ρ</code> and height <code>h</code>. What is the ratio of the pressure at the base of column 1 to that at the base of column 2?",
  opts: ["4 : 1", "2 : 1", "1 : 2", "1 : 1", "1 : 4"],
  ans: 3,
  sol: `<p>Hydrostatic pressure is <code>p = ρgh</code>. Two variables change and
the product decides it.</p>
<div class="formula">p₁ = ρ g (2h)   = 2ρgh
p₂ = (2ρ) g h   = 2ρgh
p₁ : p₂ = 1 : 1</div>
<p><b>Answer: D, 1 : 1.</b> The two effects cancel.</p>
<p><b>Why the cancellation is the interesting outcome.</b> Pressure at depth
depends on the <i>weight of the column above</i>, and there are two ways to
increase that weight: make the liquid denser, or make the column taller. They
contribute symmetrically, so halving one and doubling the other leaves the
pressure unchanged. This symmetry is not obvious from the formula alone — you have
to notice that <code>ρ</code> and <code>h</code> enter as a product.</p>
<p><b>The traps.</b> Option B, 2 : 1, compares the heights only. Option C, 1 : 2,
compares the densities only. Option A, 4 : 1, multiplies the two factors of two
instead of dividing one by the other. Option E, 1 : 4, is the same slip
inverted.</p>
<p><b>Atmospheric pressure and gauge pressure.</b> Strictly
<code>p = p_atm + ρgh</code>; the question asks about the pressure due to the
liquid, and both columns sit under the same atmosphere, so it cancels in the
ratio. Being clear about whether you want absolute or gauge pressure matters as
soon as the atmosphere does <i>not</i> cancel.</p>`,
},
{
  id: "M-06", module: "M", topic: "Upthrust and tension", diff: 3,
  q: "A block of density 800 kg m⁻³ and volume 0.0020 m³ is held completely submerged in water of density 1000 kg m⁻³ by a cable. What is the tension in the cable? Take <code>g</code> = 9.8 m s⁻².",
  opts: ["3.9 N", "15.7 N", "19.6 N", "35.3 N", "4.9 N"],
  ans: 0,
  sol: `<p>Three forces act, and the direction of the tension is the part that
needs care: the block is <i>less</i> dense than water, so it would rise and the
cable must hold it down.</p>
<div class="formula">weight   W = ρ_block V g = 800 × 0.0020 × 9.8 = 15.7 N
upthrust U = ρ_water V g = 1000 × 0.0020 × 9.8 = 19.6 N
equilibrium:  U = W + T
T = 19.6 − 15.7 = 3.9 N</div>
<p><b>Answer: A, 3.9 N.</b></p>
<p><b>Decide the direction before you write the equation.</b> Archimedes' principle
gives the upthrust as the weight of displaced fluid — here
<code>1000 × 0.0020 × 9.8</code>, using the <i>fluid's</i> density, not the
block's. Since that exceeds the block's own weight, the block is buoyant and the
cable pulls downward. Writing <code>U = W + T</code> rather than
<code>W = U + T</code> is the whole question.</p>
<p><b>The traps.</b> Option B, 15.7 N, is the weight — the answer if you forget
the upthrust exists. Option C, 19.6 N, is the upthrust, i.e. the weight of
displaced water. Option D, 35.3 N, adds the two, which would be right for a block
<i>denser</i> than water hanging from a cable above. Option E, 4.9 N, uses the
density difference wrongly, as <code>(1000 − 800) × 0.0020 × 9.8 / 2</code>.</p>
<p><b>The short cut.</b> The net upward force is
<code>(ρ_water − ρ_block) V g = 200 × 0.0020 × 9.8 = 3.9 N</code>, which is the
tension directly. Same physics, one line, and it makes the direction obvious.</p>`,
},
{
  id: "M-07", module: "M", topic: "Floating fraction", diff: 2,
  q: "A block of wood floats in water with three quarters of its volume submerged. What fraction of its volume would be submerged if it floated in a liquid of twice the density of water?",
  opts: ["3/8", "3/4", "3/2", "1/8", "5/8"],
  ans: 0,
  sol: `<p>Floating means weight equals upthrust. That single condition gives the
submerged fraction directly, and from it the density of the wood.</p>
<div class="formula">ρ_wood V g = ρ_fluid (fraction × V) g
fraction = ρ_wood / ρ_fluid
in water:   ¾ = ρ_wood/ρ_water   ⇒   ρ_wood = ¾ ρ_water
in the new liquid:  fraction = (¾ ρ_water)/(2 ρ_water) = ⅜</div>
<p><b>Answer: A, 3/8.</b></p>
<p><b>Do it in two short steps rather than one clever one.</b> First read off the
wood's density from the water data — if it floats with three quarters under, it is
three quarters as dense as water. Then apply that density to the new liquid. Trying
to jump straight to the answer invites a sign or inversion error.</p>
<p><b>The traps.</b> Option B, 3/4, assumes the submerged fraction is a property of
the object alone. Option C, 3/2, is greater than one, which would mean the block
had sunk entirely and then some — impossible. Option D, 1/8, divides by two twice.
Option E, 5/8, adds the quarters instead of halving.</p>
<p><b>The sanity check.</b> A denser liquid supports the block better, so less of
it should be submerged. The answer must be less than three quarters, which rules
out two options immediately and is the sort of check that takes two seconds in an
exam.</p>`,
},
{
  id: "M-08", module: "M", topic: "Continuity", diff: 3,
  q: "An incompressible fluid flows steadily along a pipe. At one point the cross-sectional area is <code>A</code> and the speed is <code>v</code>. The pipe then narrows to an area of <code>A/3</code>. What is the speed in the narrow section?",
  opts: ["v", "3v", "v/3", "9v", "v/2"],
  ans: 1,
  sol: `<p>Conservation of mass for an incompressible fluid says the volume flow
rate is the same everywhere: <code>Av = constant</code>.</p>
<div class="formula">A v = (A/3) v'
v' = 3v</div>
<p><b>Answer: B, 3v.</b></p>
<p><b>What "incompressible" buys you.</b> It means the density does not change, so
conserving mass is the same as conserving volume — which is why
<code>Av</code> rather than <code>ρAv</code> is constant. For a gas at high speed
that simplification fails and the density has to stay in the equation.</p>
<p><b>The traps.</b> Option A, v, assumes speed is set by the pump and not by the
geometry — contradicted by anyone who has put a thumb over a hosepipe. Option C,
v/3, inverts the relationship, making the fluid slow down where the pipe is
narrowest. Option D, 9v, squares the area ratio. Option E, v/2, halves it.</p>
<p><b>The consequence that usually follows.</b> Faster flow in the narrow section
means, by Bernoulli, <i>lower</i> pressure there — the result that makes a
Venturi meter, an aerofoil and a perfume atomiser all work. Continuity gives you
the speed; Bernoulli turns that speed into a pressure difference. They are almost
always asked as a pair.</p>`,
},
{
  id: "M-09", module: "M", topic: "Hydraulic press", diff: 3,
  q: "A hydraulic press has pistons of cross-sectional area 0.010 m² and 0.50 m². A force of 100 N is applied to the smaller piston. What force does the larger piston exert?",
  opts: ["2 N", "500 N", "50 000 N", "5000 N", "100 N"],
  ans: 3,
  sol: `<p>Pressure is transmitted equally through the fluid, so
<code>F/A</code> is the same at both pistons.</p>
<div class="formula">F₁/A₁ = F₂/A₂
F₂ = F₁ × A₂/A₁ = 100 × 0.50/0.010 = 100 × 50 = 5000 N</div>
<p><b>Answer: D, 5000 N.</b></p>
<p><b>The mechanical advantage is the area ratio, and nothing else.</b> Here
<code>0.50/0.010 = 50</code>, so the force is multiplied fiftyfold. The ratio is
of <i>areas</i>, so it goes as the square of the diameter ratio — doubling a
piston's diameter quadruples the force it can deliver.</p>
<p><b>The traps.</b> Option B, 500 N, uses a factor of ten, usually from reading
0.010 as 0.10. Option C, 50 000 N, adds a spurious factor of ten the other way.
Option A, 2 N, inverts the ratio entirely, which would make the press a force
<i>reducer</i>. Option E, 100 N, treats the force as transmitted unchanged —
Pascal's principle applied to force rather than to pressure.</p>
<p><b>What you do not get for free.</b> The larger piston moves only one fiftieth
as far as the smaller one, because the volume of fluid displaced is the same on
both sides. Energy is conserved: force is multiplied, distance is divided, and
<code>F × d</code> is unchanged. A hydraulic press is a lever with no moving
parts, and like every lever it obeys the same conservation law.</p>`,
},

/* ===================== MODULE N — insurance ===================== */

{
  id: "N-04", module: "N", topic: "SHM period ratio", diff: 3,
  q: "A mass <code>m</code> on a spring of stiffness <code>k</code> oscillates with period <code>T</code>. The mass is now quadrupled and the spring is replaced by one of twice the stiffness. What is the new period?",
  opts: ["T", "2T", "T/√2", "2√2 T", "√2 T"],
  ans: 4,
  sol: `<p>The period of a mass on a spring is <code>T = 2π√(m/k)</code>. Apply
the two changes to the quantity under the root.</p>
<div class="formula">m → 4m   ⇒  √4 = factor 2
k → 2k   ⇒  1/√2
net factor = 2 / √2 = √2
T' = √2 T</div>
<p><b>Answer: E, √2 T.</b></p>
<p><b>Both changes are inside the square root, so neither gives a whole-number
factor.</b> That is what makes this harder than it looks: quadrupling the mass
alone would double the period, and doubling the stiffness alone would shorten it
by <code>√2</code>, but together they give <code>√2</code> — a factor smaller than
either individual effect. Estimating the answer as "about 1.4 T" is a good way to
check the algebra.</p>
<p><b>The traps.</b> Option B, 2T, applies the mass change and ignores the
stiffness. Option C, T/√2, applies only the stiffness change. Option D, 2√2 T,
multiplies by <code>√2</code> instead of dividing by it — treating a stiffer spring
as making the oscillation slower, which is backwards. Option A, T, has the two
cancelling, which would need them to be exact inverses.</p>
<p><b>The physical reading.</b> A heavier mass accelerates less for the same
restoring force, so it takes longer. A stiffer spring provides more restoring
force, so it takes less time. Here the mass effect wins, but only by a factor of
<code>√2</code> rather than 2.</p>`,
},
{
  id: "N-05", module: "N", topic: "Maximum speed in SHM", diff: 3,
  q: "An object performs simple harmonic motion of amplitude 0.10 m and period 2.0 s. What is its maximum speed?",
  opts: ["0.20 m s⁻¹", "0.31 m s⁻¹", "0.63 m s⁻¹", "0.10 m s⁻¹", "1.6 m s⁻¹"],
  ans: 1,
  sol: `<p>Maximum speed occurs at the equilibrium position and equals
<code>ωA</code>. Find <code>ω</code> from the period first.</p>
<div class="formula">ω = 2π/T = 2π/2.0 = π rad s⁻¹
v_max = ωA = π × 0.10 = 0.314 m s⁻¹ ≈ 0.31 m s⁻¹</div>
<p><b>Answer: B, 0.31 m s⁻¹.</b></p>
<p><b>Why the maximum is at the centre.</b> The object is fastest where all the
energy is kinetic and there is no displacement to store it as potential energy.
At the extremes the speed is momentarily zero. So the amplitude and the angular
frequency together set the peak speed, through the single relation
<code>v_max = ωA</code>.</p>
<p><b>The traps.</b> Option A, 0.20 m s⁻¹, divides the amplitude by the
half-period — an average speed, not a maximum, and averaging over the wrong
interval. Option C, 0.63 m s⁻¹, is <code>2πA</code>: the right expression with the
period forgotten, i.e. <code>ω = 2π</code> instead of <code>2π/T</code>. Option D,
0.10 m s⁻¹, is just the amplitude, dimensionally wrong for a speed. Option E,
1.6 m s⁻¹, multiplies by 2π twice.</p>
<p><b>Average versus maximum, again.</b> Over a full cycle the average
<i>speed</i> is <code>4A/T = 0.20</code> m s⁻¹ — the object travels
<code>4A</code> in one period. That is genuinely a different quantity from
<code>v_max</code>, and the two differ by a factor of <code>π/2</code>. Knowing
which is being asked is most of the question.</p>`,
},
{
  id: "N-06", module: "N", topic: "Pendulum on the Moon", diff: 3,
  q: "A simple pendulum has a period of 2.0 s on the Earth, where <code>g</code> = 9.8 m s⁻². What is its period on the Moon, where <code>g</code> = 1.6 m s⁻²?",
  opts: ["0.81 s", "2.0 s", "12 s", "4.9 s", "3.4 s"],
  ans: 3,
  sol: `<p>The period is <code>T = 2π√(L/g)</code>, and the length does not
change, so <code>T ∝ 1/√g</code>. Forming the ratio removes the need to know
<code>L</code>.</p>
<div class="formula">T_moon/T_earth = √(g_earth/g_moon) = √(9.8/1.6) = √6.125 = 2.475
T_moon = 2.0 × 2.475 = 4.95 s ≈ 4.9 s</div>
<p><b>Answer: D, 4.9 s.</b></p>
<p><b>Weaker gravity means a longer period.</b> The restoring force on a pendulum
comes from gravity itself, so where gravity is weaker the bob accelerates back
towards the centre more gently and each swing takes longer. A pendulum clock
calibrated on Earth would run slow on the Moon by a factor of about 2.5.</p>
<p><b>The traps.</b> Option B, 2.0 s, assumes the period is fixed by the length
alone — a surprisingly common belief, probably from over-learning "the period does
not depend on the mass or the amplitude". It does depend on <code>g</code>.
Option C, 12 s, uses the ratio <code>9.8/1.6</code> without the square root.
Option A, 0.81 s, inverts it, making the Moon's weaker gravity speed the pendulum
up. Option E, 3.4 s, is a partial application of the square root.</p>
<p><b>What genuinely does not matter.</b> The mass of the bob, and — for small
oscillations — the amplitude. Both of those are real results worth knowing, and
they are probably what option B is trading on. The period is set by
<code>L</code> and <code>g</code> alone.</p>`,
},
]);
