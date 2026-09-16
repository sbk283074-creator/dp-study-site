/* BPhO Round 0 — curriculum, part 4 of 6.
   Modules B (kinematics) and C (forces, momentum, energy, statics). */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "B",
  title: "Mechanics — kinematics",
  short: "Kinematics",
  priority: 2,
  tier: "Tier A — inside AQA AS §3.4, and tested by the sample paper",
  why: "You have covered all of this in Chinese 初中 and 高中 physics, so the content is revision rather than new learning. The problem is speed: the equations are familiar enough to be done slowly and carefully, and Round 0 does not reward careful. This module is about making the familiar instant, and about the multi-phase and relative-motion problems that Chinese schooling tends to under-weight.",
  warn: null,

  sections: [
    {
      h: "The four equations, and how to choose between them",
      body: `<p>For motion with constant acceleration there are four equations, each of which omits exactly one of the five quantities. That is the key to choosing: <b>look at what the question does not mention.</b></p>
<table><thead><tr><th>Equation</th><th>Omits</th><th>Use when you have</th></tr></thead><tbody>
<tr><td><code>v = u + at</code></td><td><code>s</code></td><td>the two velocities and the time</td></tr>
<tr><td><code>s = ½(u + v)t</code></td><td><code>a</code></td><td>the two velocities and the time, and you want distance</td></tr>
<tr><td><code>s = ut + ½at²</code></td><td><code>v</code></td><td>initial velocity, acceleration and time; you want distance</td></tr>
<tr><td><code>v² = u² + 2as</code></td><td><code>t</code></td><td>the two velocities and the distance — <b>no time given or wanted</b></td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The single most useful habit in this module.</b> Before writing anything, ask: <i>is time mentioned?</i> If not, use <code>v² = u² + 2as</code>. That one reflex handles a large fraction of kinematics questions, and it is where students most often waste time by trying to find the time first.</p></div>
<h3>Sign conventions</h3>
<p>Choose a positive direction and stick to it for the whole question. If you take upward as positive, then <code>g</code> is <code>−9.81 m s⁻²</code>. A displacement that comes out negative means the object finished below where it started. Most errors in this module are sign errors, and writing the convention at the top of your working prevents nearly all of them.</p>
<h3>The special case <code>u = 0</code></h3>
<p>Objects released from rest are extremely common, and the equations simplify usefully:</p>
<div class="formula">v = at        s = ½at²        v² = 2as</div>
<p>From the last two you can get the useful proportionalities <code>s ∝ t²</code> and <code>v ∝ √s</code>, both of which are the kind of relationship a ratio question will ask about.</p>`
    },

    {
      h: "Motion graphs",
      body: `<p>Three facts, and they should be automatic rather than derived.</p>
<table><thead><tr><th>Graph</th><th>Gradient gives</th><th>Area under gives</th></tr></thead><tbody>
<tr><td>displacement–time</td><td>velocity</td><td>nothing meaningful</td></tr>
<tr><td>velocity–time</td><td>acceleration</td><td>displacement</td></tr>
<tr><td>acceleration–time</td><td>—</td><td>change in velocity</td></tr>
</tbody></table>
<div class="callout callout--warn"><p><b>Area below the axis counts as negative.</b> On a velocity–time graph, a section below the time axis represents displacement in the opposite direction, and it subtracts from the total displacement. It does <b>not</b> subtract from the distance travelled, which is the sum of the magnitudes. A question asking for "distance" and one asking for "displacement" can have different answers from the same graph.</p></div>
<h3>Reading shapes</h3>
<ul class="tight">
<li><b>Horizontal line on a v–t graph:</b> constant velocity, zero acceleration.</li>
<li><b>Straight sloping line on a v–t graph:</b> uniform acceleration. The steeper the line, the larger the acceleration.</li>
<li><b>Curve on a v–t graph:</b> changing acceleration. A curve flattening out means the acceleration is decreasing — the object is approaching terminal speed.</li>
<li><b>Parabola on an s–t graph:</b> uniform acceleration, because <code>s ∝ t²</code>.</li>
</ul>`
    },

    {
      h: "Multi-phase motion",
      body: `<p>BPhO likes problems where an object accelerates, then travels at constant speed, then decelerates, and sometimes returns. The method is always the same: <b>split into phases, and treat the end of one phase as the start of the next.</b></p>
<h3>The method</h3>
<ol class="steps">
<li>Draw a velocity–time sketch. This is not optional — it prevents almost all structural errors.</li>
<li>Label each phase with its own <code>u</code>, <code>v</code>, <code>a</code>, <code>s</code>, <code>t</code>.</li>
<li>Note which quantities are <b>shared</b> between adjacent phases. Usually the final velocity of one phase is the initial velocity of the next.</li>
<li>Solve the phase with the most information first, then work outward.</li>
<li>Check the total distance against the area under your sketch.</li>
</ol>
<div class="callout callout--key"><p><b>The eliminating-time trick.</b> In multi-phase problems the unknown is often the total time, and setting up equations for it produces a quadratic. If instead you use <code>v² = u² + 2as</code> on each phase, time never appears, and the whole problem becomes linear. This is the single most useful technique in the module.</p></div>`
    },

    {
      h: "Projectile motion",
      body: `<p>The governing idea is that the horizontal and vertical motions are <b>completely independent</b>. Gravity acts only vertically, so the horizontal velocity is constant throughout (ignoring air resistance).</p>
<table><thead><tr><th>Direction</th><th>Acceleration</th><th>Equation</th></tr></thead><tbody>
<tr><td>horizontal</td><td>zero</td><td><code>x = u cos θ × t</code></td></tr>
<tr><td>vertical</td><td><code>g</code> downward</td><td><code>y = u sin θ × t − ½gt²</code></td></tr>
</tbody></table>
<p>The only quantity shared between the two is <b>time</b>, and that is what makes projectile problems solvable: find the time from one direction, then substitute it into the other.</p>
<h3>The standard results, for level ground</h3>
<div class="formula">time of flight  T = 2u sin θ / g
maximum height  H = u² sin²θ / (2g)
range           R = u² sin 2θ / g</div>
<p>Note that the range is a maximum at <code>θ = 45°</code>, and that two angles summing to 90° give the same range. Both facts are worth knowing, because they let you check an answer.</p>
<h3>Launch from a height, and landing on a slope</h3>
<p>Two variations that appear on competition papers:</p>
<ul class="tight">
<li><b>Launch from a height:</b> the vertical equation becomes <code>−h = u sin θ × t − ½gt²</code>, where <code>h</code> is the launch height. Solve the quadratic for <code>t</code>, then use the horizontal equation.</li>
<li><b>Landing on a slope:</b> the condition is that the landing point lies on the slope, so <code>y/x = tan α</code> where <code>α</code> is the slope angle. That gives one equation in <code>t</code>.</li>
</ul>
<div class="callout callout--good"><p><b>The independence fact answers a classic question.</b> If a bullet is fired horizontally and another is dropped from the same height at the same instant, they hit the ground together. Both start with zero vertical velocity and both accelerate downward at <code>g</code>. The horizontal motion is irrelevant to the time of fall. This is a favourite conceptual question and it is worth being able to state in one sentence.</p></div>`
    },

    {
      h: "Relative motion",
      body: `<p>This is the part of the module that is genuinely new relative to the IB, and it is cheap once you see it as vector subtraction.</p>
<p>The velocity of A relative to B is</p>
<div class="formula">v_AB = v_A − v_B</div>
<p>Subtract the vectors. If they are at an angle to each other, that means drawing a triangle and using Pythagoras and trigonometry.</p>
<h3>The standard problem shapes</h3>
<ol class="steps">
<li><b>Two bodies moving at an angle.</b> Draw the two velocity vectors tail to tail, then draw the vector from the tip of <code>v_B</code> to the tip of <code>v_A</code>. That is <code>v_AB</code>. Its magnitude comes from the cosine rule or Pythagoras, its direction from trigonometry.</li>
<li><b>Crossing a current.</b> A boat that can make speed <code>v</code> in still water crossing a river flowing at <code>u</code>. To land directly opposite, the boat must aim upstream so that its upstream component cancels <code>u</code>. The crossing time is then <code>w/√(v² − u²)</code> where <code>w</code> is the river width.</li>
<li><b>Closing speed.</b> Two bodies approaching each other at speeds <code>v₁</code> and <code>v₂</code> along the same line have a closing speed of <code>v₁ + v₂</code>. If they are chasing, the closing speed is the difference.</li>
<li><b>Bearings.</b> A bearing is measured clockwise from north. If a question gives velocities as bearings, convert to components with east as <code>x</code> and north as <code>y</code> before subtracting.</li>
</ol>
<div class="callout callout--key"><p><b>Why relative motion is worth the time.</b> It is a small amount of new content that yields a disproportionately reliable mark, because the questions are formulaic once the vector subtraction is understood. Most students find it unfamiliar, which is precisely why it is a good investment.</p></div>`
    },

    {
      h: "Free fall, bounces, and terminal speed",
      body: `<h3>Successive bounces</h3>
<p>When a ball bounces, the speed after the bounce is a fixed fraction of the speed before it, governed by the coefficient of restitution. If that fraction is <code>e</code>, then after <code>n</code> bounces the speed is <code>e^n u</code>.</p>
<p>Since the height reached goes as the square of the speed, and the time of flight is proportional to the speed:</p>
<div class="formula">h_n / h_0 = e^(2n)        t_n / t_0 = e^n</div>
<p>So the heights form a geometric series with ratio <code>e²</code>, while the times form one with ratio <code>e</code>. Summing a geometric series to infinity gives the total time and the total distance, which is a standard competition question.</p>
<h3>Terminal speed</h3>
<p>As an object falls, drag increases with speed. Eventually drag balances weight:</p>
<div class="formula">drag = mg   →   acceleration = 0</div>
<p>From then on the object moves at constant speed — the terminal speed. The approach is asymptotic, so strictly it is never quite reached, which is why the velocity–time graph curves smoothly towards a horizontal line rather than meeting it.</p>
<div class="callout callout--warn"><p><b>The graph question that follows.</b> A skydiver's velocity–time graph: steep initial slope, then a gradual flattening to a plateau. If the parachute opens, there is an abrupt vertical drop in velocity followed by a new, lower plateau. Being able to sketch this and explain each feature is a common question, and the explanation is always "the drag force changed, so the balance point changed".</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A stone is dropped from rest from the top of a cliff and takes 3.0 s to reach the ground. How tall is the cliff? Use <code>g = 10 m s⁻²</code>.</p><p>A) 15 m &nbsp; B) 30 m &nbsp; C) 45 m &nbsp; D) 60 m &nbsp; E) 90 m</p>",
      sol: `<p>Released from rest, so <code>u = 0</code>, and we want distance given acceleration and time. Use <code>s = ut + ½at²</code>, which reduces to <code>s = ½gt²</code>:</p>
<div class="formula">s = ½ × 10 × 3² = ½ × 10 × 9 = 45 m</div>
<p><b>Answer: C.</b></p>
<p><b>The trap.</b> Option E, 90 m, comes from forgetting the factor of ½. Option B, 30 m, comes from using <code>s = gt²</code> with a slip, or from computing <code>v = gt = 30</code> and reporting that as the distance — which is the final speed in m s⁻¹, not the distance in metres.</p>
<p><b>The check that costs nothing.</b> After 3 s the speed is <code>10 × 3 = 30 m s⁻¹</code>. Starting from rest and accelerating uniformly, the average speed is <code>15 m s⁻¹</code>. Over 3 s that is <code>45 m</code> ✓. Using the average speed is often faster than the equation, and it is a good independent check.</p>`,
      tag: "Free fall — and the average-speed shortcut"
    },
    {
      q: "<p>A car accelerates uniformly from rest to 20 m s⁻¹ in 8.0 s, travels at a constant 20 m s⁻¹ for 14 s, then decelerates uniformly to rest in 6.0 s. What is the total distance travelled?</p><p>A) 340 m &nbsp; B) 380 m &nbsp; C) 420 m &nbsp; D) 460 m &nbsp; E) 500 m</p>",
      sol: `<p>Split into three phases and use the fact that the area under a velocity–time graph is the distance. Each phase is a simple shape.</p>
<p><b>Phase 1 — acceleration.</b> A triangle of base 8.0 s and height 20 m s⁻¹:</p>
<div class="formula">s₁ = ½ × 8.0 × 20 = 80 m</div>
<p><b>Phase 2 — constant speed.</b> A rectangle:</p>
<div class="formula">s₂ = 20 × 14 = 280 m</div>
<p><b>Phase 3 — deceleration.</b> A triangle of base 6.0 s and height 20 m s⁻¹:</p>
<div class="formula">s₃ = ½ × 6.0 × 20 = 60 m</div>
<p><b>Total.</b> <code>80 + 280 + 60 = 420 m</code>.</p>
<p><b>Answer: C.</b></p>
<p><b>The technique being tested.</b> Notice that no suvat equation was used at all. The graph-area approach is faster and less error-prone for multi-phase motion, because each phase is a shape you can compute instantly — two triangles and a rectangle. Build the habit of sketching the graph before writing anything.</p>
<p><b>The trap.</b> Option A, 340 m, comes from treating the acceleration and deceleration phases as if they had no distance at all, or from forgetting one triangle entirely. Option E, 500 m, is what you get by treating the whole 28 s as if the car travelled at 20 m s⁻¹ throughout, ignoring both ramps. Both are common structural errors rather than arithmetic slips.</p>
<p><b>The average-speed cross-check.</b> The total time is <code>8 + 14 + 6 = 28 s</code>, and the total distance is 420 m, so the average speed is <code>420/28 = 15 m s⁻¹</code>. That is three quarters of the maximum speed, which is exactly what you would expect for a profile that ramps up and down at the ends. The check is free and confirms the structure.</p>`,
      tag: "Multi-phase motion — solved by graph areas"
    },
    {
      q: "<p>A ball is thrown horizontally at 15 m s⁻¹ from a cliff 20 m high. How far from the base of the cliff does it land? Use <code>g = 10 m s⁻²</code>.</p><p>A) 15 m &nbsp; B) 21 m &nbsp; C) 30 m &nbsp; D) 42 m &nbsp; E) 60 m</p>",
      sol: `<p><b>Step 1 — find the time of flight from the vertical motion.</b> The initial vertical velocity is zero, because the throw is horizontal:</p>
<div class="formula">h = ½gt²   →   20 = ½ × 10 × t²   →   t² = 4   →   t = 2.0 s</div>
<p><b>Step 2 — find the horizontal distance.</b> The horizontal velocity is constant at 15 m s⁻¹:</p>
<div class="formula">x = 15 × 2.0 = 30 m</div>
<p><b>Answer: C.</b></p>
<p><b>The conceptual point.</b> The horizontal speed of 15 m s⁻¹ played no part in finding the time. The fall time depends only on the height and <code>g</code>. So a ball thrown horizontally at 15 m s⁻¹ and one thrown at 50 m s⁻¹ from the same height would land at the same instant, just at different distances.</p>
<p><b>The trap.</b> Option A, 15 m, is the speed, not a distance. Option E, 60 m, comes from using <code>t = 4.0 s</code> — the mistake of forgetting to take the square root when solving <code>t² = 4</code>. Watch for that specifically; it is the most common slip in this type of problem.</p>`,
      tag: "Projectile from a height"
    },
    {
      q: "<p>A boat can travel at 5.0 m s⁻¹ in still water. It crosses a river 60 m wide in which the current flows at 3.0 m s⁻¹. If the boat aims directly across, how long does the crossing take, and how far downstream does it land?</p><p>A) 12 s, 36 m &nbsp; B) 15 s, 45 m &nbsp; C) 12 s, 60 m &nbsp; D) 20 s, 60 m &nbsp; E) 15 s, 36 m</p>",
      sol: `<p><b>Crossing time.</b> The boat's velocity across the river is 5.0 m s⁻¹, and the current does not affect this component at all — it acts along the river, perpendicular to the crossing direction. So</p>
<div class="formula">t = width / crossing speed = 60/5.0 = 12 s</div>
<p><b>Drift downstream.</b> During those 12 s the current carries the boat downstream at 3.0 m s⁻¹:</p>
<div class="formula">drift = 3.0 × 12 = 36 m</div>
<p><b>Answer: A.</b></p>
<p><b>The key insight.</b> The two perpendicular motions are independent, exactly as in projectile motion. The crossing time is determined solely by the boat's own speed and the width. The current affects only how far downstream the boat ends up.</p>
<p><b>The variant worth knowing.</b> If instead the boat wants to land directly opposite, it must aim upstream at an angle. Its upstream component must cancel the current: <code>5 sin θ = 3</code>, so <code>sin θ = 0.6</code>, giving <code>θ = 37°</code> upstream of the perpendicular. The crossing speed is then the perpendicular component <code>5 cos θ = 4.0 m s⁻¹</code>, so the crossing takes <code>60/4 = 15 s</code> — longer, which is why option B appears as a distractor.</p>`,
      tag: "Relative motion — crossing a current"
    },
    {
      q: "<p>A ball is dropped from a height <code>h</code> and rebounds to a height <code>h/4</code>. What fraction of its kinetic energy is retained in the bounce?</p><p>A) 1/4 &nbsp; B) 1/2 &nbsp; C) 3/4 &nbsp; D) 1/16 &nbsp; E) 4</p>",
      sol: `<p>The height reached depends on the launch speed through <code>v² = 2gh</code>, so <code>h ∝ v²</code>. Since kinetic energy is <code>½mv²</code>, it is also proportional to <code>v²</code>, and therefore proportional to <code>h</code>.</p>
<div class="formula">E_after / E_before = h_after / h_before = (h/4)/h = 1/4</div>
<p><b>Answer: A, one quarter.</b></p>
<p><b>The trap.</b> Option B, 1/2, is the most common wrong answer, and it comes from assuming the <i>speed</i> halves. It does not — the height quarters, so the speed halves, and the energy quarters. Working in terms of height directly avoids the confusion entirely.</p>
<p><b>The general principle.</b> For a bouncing ball, height, kinetic energy and the square of the speed all change by the same factor. The speed itself changes by the square root of that factor. Keeping track of which quantities are linear and which are quadratic is the whole skill here, and it is the same skill as in the power questions in module H.</p>`,
      tag: "Energy and height — the linear versus quadratic distinction"
    }
  ],

  traps: [
    "Using a suvat equation when the acceleration is not constant. These four equations apply only to uniform acceleration.",
    "Forgetting to choose and state a sign convention, then mixing signs within one question.",
    "Treating the area below the time axis on a v–t graph as positive distance. It is negative displacement.",
    "Forgetting to take the square root when solving for <code>t</code> from <code>s = ½gt²</code>.",
    "Assuming the horizontal speed affects the fall time of a projectile. It does not.",
    "Adding the boat's speed and the current's speed when they are perpendicular. Only components along the same direction add.",
    "Confusing the final speed with the distance travelled in free fall. <code>v = gt</code> gives m s⁻¹; <code>s = ½gt²</code> gives m."
  ],

  checklist: [
    { id: "B1", flag: "CORE", text: "Displacement, speed, velocity, acceleration; the difference between average and instantaneous values." },
    { id: "B2", flag: "CORE", text: "The four uniform-acceleration equations, and choosing between them by asking whether time is mentioned." },
    { id: "B3", flag: "CORE", text: "Motion graphs: gradient of s–t is velocity, gradient of v–t is acceleration, area under v–t is displacement (negative below the axis)." },
    { id: "B4", flag: "CORE", text: "Free fall and <code>g</code>; energy retention on successive bounces, and the geometric series for total time and distance." },
    { id: "B5", flag: "CORE", text: "Multi-phase motion, solved by graph areas or by using <code>v² = u² + 2as</code> on each phase to eliminate time." },
    { id: "B6", flag: "CORE", text: "Projectile motion: independence of the directions, launch from a height, and landing on a slope." },
    { id: "B7", flag: "NEW", text: "Relative motion: vector subtraction, crossing a current, closing speed, and bearings." },
    { id: "B8", flag: "CORE", text: "Terminal speed and the qualitative treatment of drag, including the skydiver velocity–time graph." }
  ]
},

{
  code: "C",
  title: "Mechanics — forces, momentum, energy and statics",
  short: "Forces & momentum",
  priority: 2,
  tier: "Tier A — inside AQA AS §3.4, and two sample-paper questions",
  why: "The largest module on the list and almost entirely familiar from your Chinese schooling. The two things that need genuine new work are the systematic moments-by-axis technique, which the sample paper tested, and the habit of answering with a ratio rather than a number. Everything else is revision at speed.",
  warn: null,

  sections: [
    {
      h: "Vectors and resolution",
      body: `<p>A vector has magnitude and direction. The single technique you need is <b>resolution into perpendicular components</b>: replacing one vector with two at right angles to each other.</p>
<div class="formula">A_x = A cos θ        A_y = A sin θ</div>
<p>where <code>θ</code> is measured from the <code>x</code> axis. If the angle is given from the <code>y</code> axis instead, the sine and cosine swap — always check what the angle is measured from.</p>
<h3>On an inclined plane</h3>
<p>This is where resolution earns its keep. For a body on a slope of angle <code>θ</code>, the weight <code>mg</code> resolves into:</p>
<ul class="tight">
<li><b>along the slope:</b> <code>mg sin θ</code> — this is the component that accelerates the body down the slope</li>
<li><b>perpendicular to the slope:</b> <code>mg cos θ</code> — this is balanced by the normal contact force</li>
</ul>
<div class="callout callout--warn"><p><b>The most common error in the whole of mechanics.</b> Students write <code>mg cos θ</code> for the component down the slope. Check the limit: as the slope becomes flat, <code>θ → 0</code>, and the component down the slope must go to <b>zero</b>. Only <code>mg sin θ</code> does that. Always test a limit — it takes two seconds and catches the error every time.</p></div>
<h3>Equilibrium of three forces</h3>
<p>If three coplanar forces act at a point and the body is in equilibrium, the three vectors placed head-to-tail form a <b>closed triangle</b>. That turns a force problem into a geometry problem, which is usually faster. Watch for the 3–4–5 triangle and for equilateral arrangements, because they are chosen deliberately.</p>`
    },

    {
      h: "Newton's laws and free-body diagrams",
      body: `<h3>The three laws</h3>
<ol class="tight">
<li><b>First law:</b> a body remains at rest or moves at constant velocity unless acted on by a resultant force. This is the definition of an inertial frame and the reason equilibrium means zero resultant.</li>
<li><b>Second law:</b> the resultant force equals the rate of change of momentum, <code>F = Δ(mv)/Δt</code>. For constant mass this is <code>F = ma</code>.</li>
<li><b>Third law:</b> if A exerts a force on B, then B exerts an equal and opposite force on A, of the same type, acting on a different body.</li>
</ol>
<div class="callout callout--key"><p><b>The third-law test.</b> A pair of third-law forces must be (i) the same <i>type</i> of force, (ii) equal in magnitude, (iii) opposite in direction, and (iv) acting on <b>two different bodies</b>. A book resting on a table: the weight of the book and the normal force from the table are equal and opposite but they are <b>not</b> a third-law pair, because both act on the book. The third-law partner of the book's weight is the gravitational pull the book exerts on the Earth.</p></div>
<h3>Free-body diagrams</h3>
<p>Draw one body. Draw every force acting <b>on</b> it as an arrow starting from the body. Do not draw forces it exerts on other things. Then resolve and apply <code>F = ma</code> in each direction.</p>
<p>The discipline of drawing the diagram before writing any equation is not optional at competition level, where the forces are rarely all aligned.</p>`
    },

    {
      h: "Connected bodies",
      body: `<p>This was sample question S12, and it recurs. The method has two routes and you should know both.</p>
<h3>Route 1 — whole system, then one body</h3>
<ol class="steps">
<li><b>Treat everything as one system</b> to find the acceleration. Internal forces — the tension in a connecting string, the contact force between blocks — cancel and disappear.</li>
<li><b>Then isolate one body</b> and apply <code>F = ma</code> to it alone to find the internal force.</li>
</ol>
<h3>Route 2 — simultaneous equations</h3>
<p>Write <code>F = ma</code> for each body separately, with the tension as an unknown, and solve. Slower, but safer when the geometry is unusual.</p>
<h3>Lifts and apparent weight</h3>
<p>The scale reading is the normal contact force, not the weight. If the lift accelerates upward with acceleration <code>a</code>:</p>
<div class="formula">N − mg = ma   →   N = m(g + a)</div>
<p>So the reading is larger than <code>mg</code>. If the lift accelerates downward, <code>N = m(g − a)</code> and the reading is smaller. If the cable breaks, <code>a = g</code> and <code>N = 0</code> — apparent weightlessness, even though gravity is still acting.</p>
<div class="callout callout--key"><p><b>The sentence that answers the conceptual version.</b> A person in free fall feels weightless not because gravity has stopped but because there is no normal contact force pushing on them. Weight and apparent weight are different things, and only the second is what a scale measures.</p></div>
<h3>Pulleys</h3>
<p>For two masses <code>m₁</code> and <code>m₂</code> hanging over a frictionless pulley, with <code>m₁ &gt; m₂</code>:</p>
<div class="formula">a = (m₁ − m₂)g / (m₁ + m₂)        T = 2m₁m₂g/(m₁ + m₂)</div>
<p>Note the useful check: if <code>m₂ = 0</code>, then <code>a = g</code> ✓. If <code>m₁ = m₂</code>, then <code>a = 0</code> ✓. Both limits are satisfied, which is how you know the formulas are right.</p>`
    },

    {
      h: "Friction",
      body: `<p>Friction opposes relative sliding and is at most proportional to the normal contact force:</p>
<div class="formula">F_friction ≤ μN</div>
<p>The inequality is the important part. Static friction takes whatever value is needed to prevent sliding, up to a maximum of <code>μN</code>. Once sliding begins, kinetic friction is roughly constant at about <code>μN</code>, and it is usually slightly less than the maximum static value.</p>
<h3>Why a block on a slope is the standard problem</h3>
<p>Resolve along and perpendicular to the slope:</p>
<ul class="tight">
<li>Down the slope: <code>mg sin θ</code></li>
<li>Perpendicular: <code>N = mg cos θ</code></li>
<li>Friction available: <code>μmg cos θ</code></li>
</ul>
<p>The block slides when <code>mg sin θ &gt; μmg cos θ</code>, which simplifies to</p>
<div class="formula">tan θ &gt; μ</div>
<p>The mass cancels. This is why the sliding angle depends on the materials but not on how heavy the block is — a result worth knowing because it is counter-intuitive and therefore likely to be asked.</p>
<div class="callout callout--good"><p><b>Qualitative friction questions.</b> Many competition questions ask what happens to friction when something changes, without numbers. The answer always follows from asking "is the object still in equilibrium?" If yes, friction adjusts to maintain equilibrium. If no, friction is at its maximum and the object accelerates. Getting that distinction right is most of the marks.</p></div>`
    },

    {
      h: "Momentum and impulse",
      body: `<p>Momentum is mass times velocity, and it is a vector:</p>
<div class="formula">p = mv</div>
<p>In any collision or explosion where no external resultant force acts, total momentum is conserved. This is one of the most reliable tools in mechanics because it applies whether or not the collision is elastic.</p>
<h3>Force as rate of change of momentum</h3>
<p>Newton's second law in its more general form:</p>
<div class="formula">F = Δ(mv)/Δt        impulse = FΔt = Δ(mv)</div>
<p>This form matters when mass changes — a rocket, a conveyor belt being loaded, a raindrop growing as it falls. In those cases <code>F = ma</code> is wrong and <code>F = Δ(mv)/Δt</code> is right.</p>
<h3>Graphically</h3>
<p>The <b>area under a force–time graph</b> is the impulse, and therefore the change in momentum. This is the direct analogue of the area under a force–displacement graph being work done, and the two are worth learning together.</p>
<h3>Collisions and explosions</h3>
<table><thead><tr><th>Type</th><th>Momentum</th><th>Kinetic energy</th></tr></thead><tbody>
<tr><td>elastic</td><td>conserved</td><td>conserved</td></tr>
<tr><td>inelastic</td><td>conserved</td><td>reduced</td></tr>
<tr><td>explosion</td><td>conserved (zero before, zero after)</td><td>increased, from stored energy</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The explosion case confuses people.</b> An explosion starts with total momentum zero and must end with total momentum zero, so the fragments fly apart with equal and opposite momenta. Kinetic energy, by contrast, <i>increases</i> — it comes from chemical or elastic energy stored in the object. Momentum conservation and energy conservation are separate statements, and confusing them is the most common error in this topic.</p></div>`
    },

    {
      h: "Work, energy and power",
      body: `<h3>Work done by a force</h3>
<div class="formula">W = Fs cos θ</div>
<p>where <code>θ</code> is the angle between the force and the displacement. Note the three cases that follow:</p>
<ul class="tight">
<li><code>θ = 0</code>: work is <code>Fs</code>, the force is doing work on the object.</li>
<li><code>θ = 90°</code>: work is <b>zero</b>. A force perpendicular to the motion does no work — this is why the centripetal force does no work on a body in circular motion, and why the normal force does no work on a block sliding on a horizontal surface.</li>
<li><code>θ = 180°</code>: work is negative. Friction does negative work, removing kinetic energy.</li>
</ul>
<h3>Work done by a variable force</h3>
<p>The area under a <b>force–displacement graph</b> is the work done. This is why the elastic strain energy of a spring is the area of a triangle, <code>½Fx</code>, rather than <code>Fx</code>.</p>
<h3>Power</h3>
<div class="formula">P = ΔW/Δt = Fv</div>
<p>The <code>Fv</code> form is the one to use for a vehicle moving at constant speed against a resistive force: at constant speed, the driving force equals the resistance, so the power needed is <code>Fv</code>.</p>
<div class="callout callout--key"><p><b>The relationship worth internalising.</b> Because <code>P = Fv</code>, a car at constant engine power produces a driving force that is inversely proportional to its speed. That is why acceleration falls off at high speed, and why a car climbing a hill at constant power must change down a gear — reducing the speed increases the force available.</p></div>
<h3>Conservation of energy</h3>
<div class="formula">ΔEp = mgΔh        Ek = ½mv²</div>
<p>In a closed system the total energy is constant. In practice, energy "lost" to friction is not destroyed — it becomes internal energy, warming the surfaces. Tracking where the energy went, rather than only how much, is what distinguishes a good answer on a competition paper.</p>`
    },

    {
      h: "Moments — the axis technique",
      body: `<p>This is the part of module C that genuinely needs new work, and the sample paper tested it. It is also the technique that unlocks the entire statics family, so it repays the time.</p>
<h3>The definition</h3>
<div class="formula">moment = force × perpendicular distance from the axis</div>
<p>The perpendicular distance is measured from the line of action of the force to the axis, not to the point where the force is applied. Getting that wrong is the classic error.</p>
<h3>The principle of moments</h3>
<p>For a body in rotational equilibrium, about <b>any</b> chosen axis:</p>
<div class="formula">total clockwise moment = total anticlockwise moment</div>
<h3>The technique: choose the axis that eliminates an unknown</h3>
<p>This is the whole trick, and it is worth stating as a procedure.</p>
<ol class="steps">
<li><b>Identify the unknowns</b> — usually reaction forces at supports, or a tension in a tie.</li>
<li><b>Pick an axis through the point where the most awkward unknown acts.</b> A force acting through the axis has zero perpendicular distance, so its moment is zero, and it drops out of the equation entirely.</li>
<li><b>Take moments about that point.</b> Write clockwise equals anticlockwise.</li>
<li><b>Solve for the one remaining unknown.</b></li>
<li><b>If you need the other unknown, take moments about a different point</b>, or resolve vertically.</li>
</ol>
<div class="callout callout--key"><p><b>Why this works, and why you are allowed to do it.</b> The principle of moments holds about <i>every</i> axis when a body is in equilibrium. So you are free to choose whichever axis makes the algebra easiest. It is not a trick or an approximation — it is a consequence of equilibrium. Choosing the axis through an unknown is simply choosing the axis that gives you the most information for the least work.</p></div>
<h3>Worked shape: a plank on two supports</h3>
<p>A uniform plank of weight <code>W</code> and length <code>L</code> rests on supports at both ends. A load <code>P</code> is placed at distance <code>x</code> from the left support. Find the reaction at the right support.</p>
<p>Take moments about the <b>left support</b>, because that eliminates the left reaction:</p>
<div class="formula">R_right × L = W × (L/2) + P × x
R_right = (WL/2 + Px) / L</div>
<p>The left reaction never appeared. That is the technique working exactly as intended.</p>
<div class="callout callout--warn"><p><b>Two things to be careful about.</b> First, a uniform plank's weight acts at its <b>midpoint</b>, so the moment arm is <code>L/2</code> — a frequent omission. Second, if the plank is not uniform, or has an additional mass stuck to it, you must find the combined centre of mass first and treat the total weight as acting there.</p></div>
<h3>Couples</h3>
<p>Two equal, opposite, parallel forces whose lines of action are separated by distance <code>d</code> form a couple. The resultant force is zero, but there is a resultant moment:</p>
<div class="formula">moment of a couple = Fd</div>
<p>Because the resultant force is zero, a couple produces pure rotation with no translation. This is what a screwdriver applies to a screw, and it is the reason a couple's moment is the same about every axis — a fact worth knowing because it removes the need to choose an axis at all.</p>`
    },

    {
      h: "Centre of mass",
      body: `<p>The centre of mass is the point at which the whole weight of a body can be taken to act. For a uniform regular solid it is at the geometric centre; for a composite body it is found by combining the parts.</p>
<h3>Composite bodies</h3>
<p>Treat each part as a point mass at its own centre of mass, then find the weighted average position:</p>
<div class="formula">x_cm = (m₁x₁ + m₂x₂ + …) / (m₁ + m₂ + …)</div>
<h3>The added-mass problem</h3>
<p>A common competition shape: a uniform object has an extra mass stuck to one end, and you must find the new centre of mass, then use it in a moments calculation. The procedure is:</p>
<ol class="steps">
<li>Find the centre of mass of the composite using the weighted-average formula.</li>
<li>Treat the total weight as acting at that point.</li>
<li>Then apply the moments technique as usual.</li>
</ol>
<div class="callout callout--key"><p><b>Where this leads.</b> The tipping condition follows directly. A body tips when its centre of mass passes beyond the edge of its base of support. Setting the moment about the pivot edge to zero gives the critical value of the added mass or the critical angle — and that is the form the question usually takes.</p></div>
<h3>Uniform regular solids — know these</h3>
<table><thead><tr><th>Shape</th><th>Centre of mass</th></tr></thead><tbody>
<tr><td>Uniform rod</td><td>midpoint</td></tr>
<tr><td>Uniform rectangular plate</td><td>intersection of the diagonals</td></tr>
<tr><td>Uniform triangle</td><td>intersection of the medians, one third up from the base</td></tr>
<tr><td>Uniform disc or sphere</td><td>geometric centre</td></tr>
<tr><td>Uniform semicircular plate</td><td><code>4r/3π</code> from the diameter</td></tr>
<tr><td>Uniform solid hemisphere</td><td><code>3r/8</code> from the flat face</td></tr>
</tbody></table>`
    }
  ],

  examples: [
    {
      q: "<p>A uniform beam of length 4.0 m and weight 200 N rests on two supports, one at each end. A load of 300 N is placed 1.0 m from the left support. What is the reaction force at the right support?</p><p>A) 125 N &nbsp; B) 175 N &nbsp; C) 250 N &nbsp; D) 375 N &nbsp; E) 500 N</p>",
      sol: `<p><b>Choose the axis to eliminate the left reaction.</b> Take moments about the left support, so the unknown force there has zero moment arm.</p>
<p><b>Moments clockwise</b> (both the beam's weight and the load act downward, so about the left support they both rotate clockwise):</p>
<ul class="tight">
<li>Beam weight 200 N acts at the midpoint, 2.0 m from the left support: moment <code>= 200 × 2.0 = 400 N m</code></li>
<li>Load 300 N acts 1.0 m from the left support: moment <code>= 300 × 1.0 = 300 N m</code></li>
<li>Total clockwise <code>= 700 N m</code></li>
</ul>
<p><b>Moment anticlockwise:</b> the right reaction <code>R</code> acts 4.0 m from the left support: moment <code>= R × 4.0</code>.</p>
<p><b>Equate and solve:</b></p>
<div class="formula">4.0R = 700   →   R = 175 N</div>
<p><b>Answer: B.</b></p>
<p><b>The check.</b> Resolve vertically: the total downward force is <code>200 + 300 = 500 N</code>, so the left reaction is <code>500 − 175 = 325 N</code>. Now verify by taking moments about the right support: clockwise <code>= 325 × 4.0 = 1300</code>; anticlockwise <code>= 200 × 2.0 + 300 × 3.0 = 400 + 900 = 1300</code> ✓. The two agree, which confirms the answer.</p>
<p><b>The trap.</b> Option C, 250 N, is what you get by putting the beam's weight at the right support, or by forgetting the beam's weight entirely and computing <code>300 × 1/4 = 75</code> plus something. The commonest error is to forget the beam's own weight, which would give <code>300 × 1/4 = 75 N</code> — not even an option, which is a hint that you have missed something.</p>`,
      tag: "Moments — the axis technique"
    },
    {
      q: "<p>A block of mass 2.0 kg slides down a slope inclined at 30° to the horizontal. The coefficient of friction between the block and the slope is 0.20. What is the acceleration of the block? Use <code>g = 10 m s⁻²</code>.</p><p>A) 1.7 m s⁻² &nbsp; B) 3.3 m s⁻² &nbsp; C) 5.0 m s⁻² &nbsp; D) 6.7 m s⁻² &nbsp; E) 8.7 m s⁻²</p>",
      sol: `<p><b>Step 1 — resolve the weight.</b> Down the slope: <code>mg sin 30° = 2.0 × 10 × 0.5 = 10 N</code>. Perpendicular to the slope: <code>mg cos 30° = 2.0 × 10 × 0.866 = 17.3 N</code>.</p>
<p><b>Step 2 — friction.</b> The normal force equals the perpendicular component (since there is no acceleration perpendicular to the slope), so</p>
<div class="formula">F_friction = μN = 0.20 × 17.3 = 3.46 N</div>
<p><b>Step 3 — resultant force down the slope.</b></p>
<div class="formula">F_net = 10 − 3.46 = 6.54 N</div>
<p><b>Step 4 — acceleration.</b></p>
<div class="formula">a = F_net/m = 6.54/2.0 = 3.3 m s⁻²</div>
<p><b>Answer: B.</b></p>
<p><b>The limit check that catches the standard error.</b> If you had used <code>mg cos θ</code> for the component down the slope, you would get <code>a = 8.7 m s⁻²</code> — option E, which is larger than <code>g sin θ</code> and therefore impossible for a block sliding <i>down</i> a slope with friction. Any answer larger than <code>g sin θ = 5.0 m s⁻²</code> is wrong, because friction can only reduce the acceleration. That single check eliminates D and E instantly.</p>
<p><b>Note what cancelled.</b> The mass appeared in both the driving force and the friction, so it divided out of the final acceleration. That is not an accident — for a sliding block, the acceleration is independent of mass. Only the numbers here happened to require the mass to be given; the answer would be the same for any mass.</p>`,
      tag: "Friction on a slope"
    },
    {
      q: "<p>A ball of mass 0.20 kg travelling at 8.0 m s⁻¹ strikes a wall perpendicularly and rebounds at 6.0 m s⁻¹. The contact time is 0.040 s. What is the average force exerted by the wall?</p><p>A) 10 N &nbsp; B) 30 N &nbsp; C) 40 N &nbsp; D) 70 N &nbsp; E) 100 N</p>",
      sol: `<p><b>Step 1 — the change in momentum.</b> Take the initial direction as positive. Then the initial momentum is <code>+0.20 × 8.0 = +1.6 kg m s⁻¹</code> and the final momentum is <code>−0.20 × 6.0 = −1.2 kg m s⁻¹</code>.</p>
<div class="formula">Δp = −1.2 − 1.6 = −2.8 kg m s⁻¹</div>
<p><b>Step 2 — the force.</b></p>
<div class="formula">F = Δp/Δt = 2.8/0.040 = 70 N</div>
<p><b>Answer: D.</b></p>
<p><b>The trap, and it is the whole point of the question.</b> The magnitudes of the momenta are 1.6 and 1.2, and their difference is 0.4 — which would give a force of 10 N, option A. That is wrong because the ball <b>reverses direction</b>, so the two momenta have opposite signs and must be <i>added</i>, not subtracted. Writing the sign convention down before starting is what prevents this.</p>
<p><b>Why the question includes a rebound at a different speed.</b> A perfect elastic bounce would give equal speeds, and then the change in momentum would be <code>2mv</code>, which is easy to spot. By making the rebound slower, the question forces you to handle the signs properly rather than relying on a memorised pattern.</p>
<p><b>The physical reading.</b> The wall must do more than stop the ball; it must also push it back the other way. So the impulse required is larger than the ball's initial momentum, and 70 N is consistent with that.</p>`,
      tag: "Impulse and the sign convention"
    },
    {
      q: "<p>Two blocks, of mass 3.0 kg and 1.0 kg, are connected by a light string over a frictionless pulley. They hang vertically. What is the acceleration of the system? Use <code>g = 10 m s⁻²</code>.</p><p>A) 2.5 m s⁻² &nbsp; B) 5.0 m s⁻² &nbsp; C) 7.5 m s⁻² &nbsp; D) 10 m s⁻² &nbsp; E) 20 m s⁻²</p>",
      sol: `<p>Use the whole-system approach. The driving force is the <i>difference</i> in weights, and the mass being accelerated is the <i>total</i> mass:</p>
<div class="formula">a = (m₁ − m₂)g / (m₁ + m₂) = (3.0 − 1.0) × 10 / (3.0 + 1.0) = 20/4.0 = 5.0 m s⁻²</div>
<p><b>Answer: B.</b></p>
<p><b>Why the tension disappears.</b> The tension pulls the 3.0 kg block backward and the 1.0 kg block forward with the same magnitude. When you treat the two as one system, those two contributions cancel, which is why the whole-system route is faster.</p>
<p><b>The limit checks.</b> If <code>m₂</code> were zero, the 3.0 kg block would fall freely and <code>a = g = 10 m s⁻²</code> ✓. If the masses were equal, the system would be balanced and <code>a = 0</code> ✓. Both limits are satisfied by the formula, which confirms its structure.</p>
<p><b>The trap.</b> Option C, 7.5 m s⁻², is what you get by using the difference in weights but only the larger mass in the denominator — <code>20/3.0 = 6.7</code>, or with a slip, 7.5. Option D, 10 m s⁻², is the free-fall answer you get by ignoring the smaller mass entirely. Both are there deliberately.</p>
<p><b>The follow-up you should be able to do.</b> The tension is <code>T = 2m₁m₂g/(m₁ + m₂) = 2 × 3 × 1 × 10/4 = 15 N</code>. Check it on the smaller block: the tension upward minus its weight <code>1 × 10 = 10 N</code> gives a net <code>5 N</code>, and <code>5/1.0 = 5.0 m s⁻²</code> ✓. That is the same acceleration, which confirms both results.</p>`,
      tag: "Connected bodies — pulley"
    },
    {
      q: "<p>A car of mass 1200 kg travels at a constant 20 m s⁻¹ against a total resistive force of 600 N. What power must the engine deliver?</p><p>A) 6 kW &nbsp; B) 12 kW &nbsp; C) 24 kW &nbsp; D) 240 kW &nbsp; E) 30 kW</p>",
      sol: `<p>At constant speed the driving force exactly balances the resistive force, so the driving force is 600 N. Use <code>P = Fv</code>:</p>
<div class="formula">P = 600 × 20 = 12 000 W = 12 kW</div>
<p><b>Answer: B.</b></p>
<p><b>Why the mass is irrelevant.</b> The mass is given as a distractor. At constant speed there is no acceleration, so no resultant force and no use for the mass. If the question had asked about acceleration, the mass would matter. Recognising which quantities are needed and which are decoys is part of the skill.</p>
<p><b>The trap.</b> Option D, 240 kW, comes from computing <code>½mv²</code> — the kinetic energy — and misreading it as a power. Option C, 24 kW, is that value divided by something arbitrary. Notice that the kinetic energy is not being changed at all here, since the speed is constant, so no energy is going into kinetic energy. All the engine's output is being dissipated against the resistive forces.</p>
<p><b>The extension worth doing.</b> If the car now accelerates at 1.0 m s⁻² at the same speed, the driving force must be <code>600 + 1200 × 1.0 = 1800 N</code>, so the power needed jumps to <code>1800 × 20 = 36 kW</code> — three times as much. That is why cars have a lower top speed uphill, and it is the kind of extension a competition question would ask.</p>`,
      tag: "Power at constant speed"
    },
    {
      q: "<p>A uniform metre rule of weight 2.0 N is pivoted at the 30 cm mark. A mass of 0.40 kg is hung from the 10 cm mark. At which mark must a second mass of 0.10 kg be hung for the rule to balance? Use <code>g = 10 m s⁻²</code>.</p><p>A) 50 cm &nbsp; B) 60 cm &nbsp; C) 70 cm &nbsp; D) 80 cm &nbsp; E) 90 cm</p>",
      sol: `<p><b>Sketch it and write every distance as a signed offset from the pivot.</b> That single practice removes almost all errors here, because the distances must be measured from the <b>pivot</b> and not from the ends of the rule.</p>
<p>The pivot is at the 30 cm mark. So:</p>
<ul class="tight">
<li>The rule's own weight, 2.0 N, acts at its midpoint, the 50 cm mark — that is <code>50 − 30 = 20 cm = 0.20 m</code> to the <b>right</b> of the pivot. Moment: <code>2.0 × 0.20 = 0.40 N m</code> clockwise.</li>
<li>The 0.40 kg mass weighs <code>0.40 × 10 = 4.0 N</code> and hangs at the 10 cm mark — that is <code>30 − 10 = 20 cm = 0.20 m</code> to the <b>left</b>. Moment: <code>4.0 × 0.20 = 0.80 N m</code> anticlockwise.</li>
</ul>
<p><b>Which side does the second mass go on?</b> The anticlockwise moment (0.80) exceeds the clockwise moment (0.40), so the rule would rotate anticlockwise. The second mass must therefore hang to the <b>right</b> to add clockwise moment. Rather than guessing, set up the equation and let the algebra confirm it — if you assume the right and the answer comes out positive, the assumption was right.</p>
<p>Let the second mass hang <code>d</code> metres to the right of the pivot. Its weight is <code>0.10 × 10 = 1.0 N</code>.</p>
<div class="formula">0.80 = 0.40 + 1.0d
1.0d = 0.40
d = 0.40 m</div>
<p>So the mass hangs 0.40 m to the right of the pivot, which is the <b>30 + 40 = 70 cm</b> mark.</p>
<p><b>Answer: C.</b></p>
<p><b>The check.</b> Take moments about the pivot again with the answer in place. Clockwise: rule <code>0.40</code> plus the second mass <code>1.0 × 0.40 = 0.40</code>, total <code>0.80</code>. Anticlockwise: <code>0.80</code> ✓. The two sides balance.</p>
<p><b>The traps.</b> Option A, 50 cm, is the rule's centre of mass — the answer you get by forgetting the second mass entirely. Option B, 60 cm, comes from measuring the 0.40 m from the wrong end of the rule. Both are structural errors about <i>where distances are measured from</i>, which is why the sketch matters more than the arithmetic.</p>`,
      tag: "Moments with a pivot — and the value of a sketch"
    }
  ],

  traps: [
    "Using <code>mg cos θ</code> for the component of weight down a slope. It is <code>mg sin θ</code>; check the limit <code>θ → 0</code>.",
    "Measuring the moment arm to the point of application rather than perpendicular to the line of action.",
    "Forgetting the beam's own weight, or putting it at the end instead of the midpoint.",
    "Subtracting momenta instead of adding them when a body reverses direction. Write the sign convention down first.",
    "Using <code>F = ma</code> when mass is changing. Use <code>F = Δ(mv)/Δt</code> instead.",
    "Confusing momentum conservation with energy conservation. An explosion conserves momentum but increases kinetic energy.",
    "Treating weight and apparent weight as the same thing. A scale measures the normal contact force.",
    "Thinking a force perpendicular to the motion does work. It does not — <code>cos 90° = 0</code>.",
    "Guessing which side of a pivot a mass goes on instead of writing signed distances and letting the algebra decide."
  ],

  checklist: [
    { id: "C1", flag: "CORE", text: "Scalars and vectors; resolution into perpendicular components; components on an inclined plane, with the <code>θ → 0</code> limit check." },
    { id: "C2", flag: "CORE", text: "Equilibrium of two or three coplanar forces at a point; the closed triangle of forces." },
    { id: "C3", flag: "CORE", text: "Newton's three laws; <code>F = ma</code>; free-body diagrams; the third-law pair test." },
    { id: "C4", flag: "CORE", text: "Connected bodies: pulleys, chains of blocks, towing, and apparent weight in a lift. Both the whole-system route and the simultaneous-equations route." },
    { id: "C5", flag: "CORE", text: "Friction, qualitatively and quantitatively; the sliding condition <code>tan θ &gt; μ</code>; the equilibrium versus maximum-friction distinction." },
    { id: "C6", flag: "CORE", text: "Momentum <code>p = mv</code> and conservation in one dimension, including the sign convention for reversing bodies." },
    { id: "C7", flag: "CORE", text: "<code>F = Δ(mv)/Δt</code> and impulse <code>FΔt = Δ(mv)</code>; when <code>F = ma</code> fails because mass changes." },
    { id: "C8", flag: "CORE", text: "The area under a force–time graph is impulse, and the area under a force–displacement graph is work done." },
    { id: "C9", flag: "CORE", text: "Elastic versus inelastic collisions and explosions; momentum conserved in both, kinetic energy not." },
    { id: "C10", flag: "CORE", text: "Work <code>W = Fs cos θ</code> and the three angle cases; power <code>P = ΔW/Δt = Fv</code>." },
    { id: "C11", flag: "CORE", text: "Variable forces: work as the area under a force–displacement graph." },
    { id: "C12", flag: "CORE", text: "Efficiency as useful output over total input, and why it is always less than one." },
    { id: "C13", flag: "CORE", text: "Conservation of energy; <code>ΔEp = mgΔh</code>; <code>Ek = ½mv²</code>; accounting for energy lost to resistive forces." },
    { id: "C14", flag: "R1-ONLY", text: "Rocket and variable-mass thrust problems using <code>F = v dm/dt</code>. Round 1 material — insurance only." },
    { id: "C15", flag: "CORE", text: "Centre of mass; uniform regular solids; composite bodies and the weighted-average formula." },
    { id: "C16", flag: "NEW", text: "Moment of a force as <code>F ×</code> perpendicular distance; the principle of moments; couples and the moment of a couple." },
    { id: "C17", flag: "NEW", text: "The axis technique: choose the axis through an unknown to eliminate it. Be able to explain why this is legitimate." },
    { id: "C18", flag: "CORE", text: "Multi-support equilibrium; plank, ladder and hinged-rod problems; the vertical-resolution check." },
    { id: "C19", flag: "NEW", text: "Combined centre-of-mass and moments problems with an added mass, including the tipping condition." }
  ]
}

]);
