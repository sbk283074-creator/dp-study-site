# -*- coding: utf-8 -*-
"""BPhO Round 0 -- BANK SECTION 01 (S01-01 .. S01-25).

Twenty-five original questions in the exact Round 0 format: single-answer MCQ, five
options, no calculator, one mark each, no negative marking.  They are NOT taken from
any competition paper -- BPhO's papers and other competitions' papers are copyrighted.
What is borrowed is the style and the difficulty, and `spec.STYLE` records which
competitions set questions of comparable demand inside the R0 scope; that list is what
was consulted while calibrating each question below.

The module mix is the real 2025 paper's mix, so this section is a valid full-length
mock:  A3 B2 C4 D2 E1 F2 G2 H4 I1 J2 K2.

Every question carries, besides the usual fields:

  distractors    five strings index-aligned with `opts`.  The entry at `ans` is
                 "correct"; each of the other four NAMES the error that produces that
                 option.  A question whose wrong options have no nameable cause has
                 filler options, and filler options are the difference between a
                 worksheet and a competition paper.  Gate G2 enforces this.
  profile        the reasoning chain, declared rather than implied: the steps, the
                 relations used, the one insight that unlocks it, and the logical
                 shape.  Gate G4 cross-checks the declaration against the solution
                 text, so a chain cannot be over- or under-stated.
  check          an independent re-derivation.  `expr` is the chosen option's formula
                 evaluated at sample numbers; `want` is the same number obtained from
                 first principles by a different route.  Gate G7 evaluates both with
                 exact arithmetic.

Figures are hand-authored inline SVG in fig/, referenced as {{FIG:key}}.
"""

SECTION = 1

QUESTIONS = [

# ═════════════════════════════════════════════════════════════════════════════
# 1 — C, forces.  The tension in a moving Atwood machine.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 1, "id": "S01-01", "module": "C", "diff": 2,
    "topic": "Atwood machine: the tension in a string that is not in equilibrium",
    "rel": [("C", "Newton's second law applied to each block in turn"),
            ("C", "A light string over a smooth pulley carries one tension throughout"),
            ("A", "Eliminating a shared unknown between two simultaneous equations")],
    "key": ["force", "kinematics", "ratio"],
    "stem": '<p>Two blocks of mass <code>m</code> and <code>2m</code> are joined by a light inextensible string that passes over a smooth fixed pulley, and hang freely. What is the tension in the string while the blocks are moving?</p>',
    "opts": ["mg", "4mg/3", "3mg/2", "2mg/3", "8mg/3"],
    "ans": 1,
    "distractors": [
        "assumes the system is in equilibrium, so the tension must equal the lighter weight",
        "correct",
        "divides the driving force by the heavier mass alone, which gives a = g/2",
        "applies T = m(g - a) to the lighter block, so gets the sign of its acceleration wrong",
        "adds the accelerating term instead of subtracting it on the heavier block",
    ],
    "profile": {
        "steps": [
            ("relate", "both blocks share one acceleration magnitude and the string carries one tension"),
            ("relate", "write F = ma for each block separately, in its own direction of motion"),
            ("eliminate", "add the two equations so the unknown tension cancels and a falls out"),
            ("solve", "put a back into either equation to get the tension"),
        ],
        "relations": ["2mg - T = 2ma", "T - mg = ma", "a = (m2 - m1)g / (m1 + m2)"],
        "insight": "The string is not in equilibrium, so the tension is neither mg nor 2mg. It is the force that makes the LIGHTER block accelerate upward, which means it must exceed mg.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "2*m*g - 2*m*(g/3)", "want": "4*m*g/3"},
    "sol": '''<p><b>What is being tested.</b> Whether you realise that a pulley system in motion is <i>not</i> in equilibrium. The single most common answer to this question is <code>mg</code>, and it is wrong for a reason worth understanding.</p>
<p><b>Step 1 — one acceleration, one tension.</b> The string is inextensible, so if the heavier block descends a distance <code>d</code> the lighter block rises by the same <code>d</code>. Both therefore have the same magnitude of acceleration <code>a</code>, in opposite directions. The string is light, so it has no mass to accelerate, and the pulley is smooth, so it exerts no frictional torque; therefore the tension <code>T</code> is the same on both sides. Two unknowns, <code>a</code> and <code>T</code>.</p>
<p><b>Step 2 — Newton's second law for each block.</b> The heavier block (<code>2m</code>) descends, so its weight wins and the tension opposes it:</p>
<div class="formula">2mg - T = 2ma</div>
<p>The lighter block (<code>m</code>) rises, so the tension wins and its weight opposes it:</p>
<div class="formula">T - mg = ma</div>
<p><b>Step 3 — add to eliminate the tension.</b> Adding the two equations makes <code>T</code> cancel:</p>
<div class="formula">(2mg - T) + (T - mg) = 2ma + ma
mg = 3ma
a = g/3</div>
<p>The acceleration is one third of <code>g</code>, which is plausible: the driving force is the <i>difference</i> of the weights, <code>mg</code>, and it has to accelerate the <i>whole</i> mass, <code>3m</code>.</p>
<p><b>Step 4 — substitute back for the tension.</b> Using the lighter block, because its equation is simpler:</p>
<div class="formula">T = m(g + a) = m(g + g/3) = 4mg/3</div>
<p><b>Answer: B, 4mg/3.</b></p>
<p><b>Check it against the other block.</b> The heavier block should give the same answer: <code>2mg - T = 2mg - 4mg/3 = 2mg/3</code>, and <code>2ma = 2m(g/3) = 2mg/3</code>. They agree, so the value is consistent with both equations rather than with just one.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>mg</b> is the equilibrium answer. It is what you get by setting <code>a = 0</code> above, and it is wrong because the system is visibly accelerating. Note that it is also the <i>weight of the lighter block</i>, which is the trap: the tension must be <i>more</i> than <code>mg</code> or that block could never rise.</p>
<p>· <b>3mg/2</b> comes from dividing the driving force by the heavier mass only, <code>a = mg/2m = g/2</code>. The driving force has to accelerate both blocks, so the correct divisor is the total mass.</p>
<p>· <b>2mg/3</b> comes from using <code>T = m(g - a)</code> on the lighter block. That is the formula for a block <i>descending</i>; the lighter block is rising, so the tension term adds.</p>
<p>· <b>8mg/3</b> comes from adding where you should subtract, <code>T = 2mg + 2ma</code>. Physically that would mean the string pushes the descending block upward harder than gravity pulls it down, which would make it rise.</p>
<p><b>The trap.</b> Both <code>mg</code> and <code>2mg/3</code> look like natural answers because each is a weight in the problem. Neither is a tension in a moving system. A quick sanity test settles it: the lighter block accelerates upward, so the net force on it points upward, so <code>T &gt; mg</code>. Only <code>4mg/3</code> and <code>8mg/3</code> survive that test, and the second would mean the heavier block accelerates upward too.</p>
<p><b>Relevant topics:</b> Newton's second law; connected particles; pulley systems; simultaneous equations.</p>''',
    "trap": "Answering <code>mg</code> because the tension in a stationary string equals the weight. In a moving system the lighter block is accelerating upward, so <code>T</code> must exceed <code>mg</code> — anything less cannot lift it.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 2 — H, circuits.  A potential divider loaded by a real voltmeter.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 2, "id": "S01-02", "module": "H", "diff": 2,
    "topic": "A potential divider measured with a voltmeter that is not ideal",
    "rel": [("H", "The potential divider: the supply splits in the ratio of the resistances"),
            ("H", "A voltmeter is a resistor, and connecting it changes the circuit"),
            ("H", "Resistors in parallel: the combined value is smaller than either"),
            ("A", "Reasoning about which way a measured value must move")],
    "key": ["divider", "seriesparallel", "meters", "resistance"],
    "stem": '<p>A 12 V supply of negligible internal resistance is connected in series with a <code>6.0 k&Omega;</code> resistor and a <code>3.0 k&Omega;</code> resistor. A voltmeter of resistance <code>6.0 k&Omega;</code> is connected across the <code>3.0 k&Omega;</code> resistor. {{FIG:s01-02}}</p><p>What does the voltmeter read?</p>',
    "opts": ["1.5 V", "2.0 V", "3.0 V", "4.0 V", "6.0 V"],
    "ans": 2,
    "distractors": [
        "halves the already-loaded reading, double-counting the meter's effect",
        "reports the parallel resistance value, 2.0, as though it were the voltage",
        "correct",
        "uses the unloaded divider ratio 3/(6+3) and ignores the meter entirely",
        "assumes the divider is balanced and the reading is half the supply",
    ],
    "profile": {
        "steps": [
            ("read", "notice that the meter has a stated resistance, so it draws current"),
            ("relate", "combine the meter with the resistor it is across, in parallel"),
            ("relate", "form the new total resistance and apply the divider ratio"),
            ("solve", "multiply the supply by the new ratio"),
            ("check", "compare with the ideal-meter answer to see which way the reading moved"),
        ],
        "relations": ["R_parallel = R1 R2 / (R1 + R2)", "V_out = V_supply * R_lower / R_total", "I = V / R"],
        "insight": "A real voltmeter is a resistor in parallel with the thing it measures, so it lowers the resistance of that part of the divider and therefore lowers the fraction of the supply across it. The reading must come out BELOW the ideal-meter value of 4.0 V.",
        "shape": "circuit-reduction",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "12*((3*6)/(3+6))/(6+(3*6)/(3+6))", "want": "3"},
    "sol": '''<p><b>What is being tested.</b> Whether you treat a voltmeter as a measuring device that observes without disturbing, or as what it actually is: a resistor connected across the component.</p>
<p><b>Step 1 — the meter is part of the circuit.</b> The question gives its resistance, <code>6.0 k&Omega;</code>, which is the signal that it must be included. It sits in parallel with the <code>3.0 k&Omega;</code> resistor.</p>
<p><b>Step 2 — combine the parallel pair.</b></p>
<div class="formula">R_p = (3.0 x 6.0) / (3.0 + 6.0) = 18 / 9.0 = 2.0 k&Omega;</div>
<p>Note that the pair is smaller than either member, as any parallel combination must be. That is the physical content of "the meter loads the circuit".</p>
<p><b>Step 3 — the divider now splits between 6.0 and 2.0.</b></p>
<div class="formula">R_total = 6.0 + 2.0 = 8.0 k&Omega;
V_out = 12 x (2.0 / 8.0) = 12 x 1/4 = 3.0 V</div>
<p><b>Step 4 — the reading.</b></p>
<div class="formula">V = 3.0 V</div>
<p><b>Step 5 — check the direction of the change.</b> With an ideal voltmeter the divider would give <code>12 x 3/9 = 4.0 V</code>. The real reading is <code>3.0 V</code>, which is lower, as it must be: the meter has reduced the resistance of the lower arm, so the lower arm now takes a smaller share of the supply. Any answer above 4.0 V is impossible, which already eliminates one option before any arithmetic.</p>
<p><b>Answer: C, 3.0 V.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>4.0 V</b> is the ideal-voltmeter answer, <code>12 x 3/(6+3)</code>. It is the most popular wrong answer because it is the answer to the question you expected.</p>
<p>· <b>2.0 V</b> is the parallel resistance <code>2.0 k&Omega;</code> reported as a voltage. A units check kills it: 2.0 is a resistance, not a potential difference.</p>
<p>· <b>1.5 V</b> halves the correct answer, which happens if you halve <code>R_p</code> a second time.</p>
<p>· <b>6.0 V</b> is half the supply, which is what a balanced divider would give. Here the two arms are 6.0 and 2.0, nowhere near balanced.</p>
<p><b>The wider point.</b> Every measurement disturbs what it measures. In Round 0 the disturbance is usually stated as a finite resistance, and the question is really asking whether you will notice. The same idea appears with an ammeter's resistance in series, and with a thermistor whose own resistance changes as it self-heats.</p>
<p><b>Relevant topics:</b> potential dividers; parallel resistance; real meters; loading effects.</p>''',
    "trap": "Computing <code>12 x 3/(6+3) = 4.0 V</code> and never using the <code>6.0 k&Omega;</code> the question supplied. If a resistance is given, something is meant to be done with it.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 3 — A, toolkit.  Dimensional analysis: how a raindrop's terminal speed scales.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 3, "id": "S01-03", "module": "A", "diff": 3,
    "topic": "Dimensional analysis: the terminal speed of a raindrop against its radius",
    "rel": [("A", "Building a quantity from its dimensions alone"),
            ("A", "Dimensions must balance on both sides of an equation"),
            ("M", "Drag on a body moving through a fluid depends on area and speed squared"),
            ("C", "Terminal velocity is the balance of drag against weight")],
    "key": ["dimensions", "ratio", "nocalc"],
    "stem": '<p>A spherical raindrop falls through still air and reaches a terminal speed <code>v</code>. The drag force on the drop depends only on the drop\u2019s radius <code>r</code>, the density of the air <code>&rho;</code> and <code>v</code> itself. The drop is much denser than the air, and the air is much less dense than water (density <code>&rho;<sub>w</sub></code>).</p><p>How does <code>v</code> depend on <code>r</code>?</p>',
    "opts": ["v &prop; r", "v &prop; &radic;r", "v &prop; r&sup2;", "v &prop; 1/&radic;r", "v does not depend on r"],
    "ans": 1,
    "distractors": [
        "takes the drag to be proportional to the radius rather than to the cross-sectional area",
        "correct",
        "takes the drag to be proportional to the volume, i.e. to r cubed, and then misses a factor",
        "inverts the proportionality, which would make bigger drops fall more slowly",
        "concludes from 'the drag depends on r' that the two effects cancel",
    ],
    "profile": {
        "steps": [
            ("relate", "the drag depends on rho, r and v, so build its dimensions and force it to be a force"),
            ("solve", "the exponents come out as rho^1 r^2 v^2, so drag goes as r squared"),
            ("relate", "at terminal speed the drag equals the weight, and the weight goes as r cubed"),
            ("eliminate", "equate the two powers of r and read off the exponent on v"),
            ("solve", "take the square root to get v in terms of r"),
        ],
        "relations": ["F_drag = k rho r^2 v^2", "W = (4/3) pi r^3 rho_w g", "drag = weight at terminal velocity"],
        "insight": "Both the drag and the weight grow with r, but the weight grows faster (r cubed against r squared). The speed has to make up the difference, and it does so as the square root of r.",
        "shape": "dimensional-analysis",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "sqrt(r)", "want": "r**(1/2)"},
    "sol": '''<p><b>What is being tested.</b> Whether you can use dimensions as a tool rather than as a memory test. Nothing in the data booklet gives the drag law; it has to be constructed.</p>
<p><b>Step 1 — build the drag force from its ingredients.</b> Suppose <code>F = k &rho;<sup>a</sup> r<sup>b</sup> v<sup>c</sup></code>. Write the dimensions of each:</p>
<div class="formula">[F] = M L T^-2
[&rho;] = M L^-3      [r] = L      [v] = L T^-1</div>
<p>Matching powers of M, L and T in turn:</p>
<div class="formula">M:  1 = a
T:  -2 = -c        so c = 2
L:  1 = -3a + b + c = -3 + b + 2   so b = 2</div>
<p>So the drag must go as</p>
<div class="formula">F &prop; &rho; r&sup2; v&sup2;</div>
<p>This is the familiar result that drag depends on the <i>cross-sectional area</i>, which is <code>&pi;r&sup2;</code>, not on the radius itself. That distinction is the whole question.</p>
<p><b>Step 2 — at terminal speed, drag balances weight.</b> The drop's weight is</p>
<div class="formula">W = (4/3) &pi; r&sup3; &rho;<sub>w</sub> g</div>
<p>so it goes as <code>r&sup3;</code>. Setting drag equal to weight:</p>
<div class="formula">&rho; r&sup2; v&sup2; &prop; r&sup3; &rho;<sub>w</sub> g</div>
<p><b>Step 3 — collect the powers of r.</b> Divide both sides by <code>r&sup2;</code>:</p>
<div class="formula">v&sup2; &prop; r &times; (&rho;<sub>w</sub> g / &rho;)</div>
<p><b>Step 4 — take the square root.</b> Everything except <code>r</code> is a constant for a given drop and a given air density, so</p>
<div class="formula">v &prop; &radic;r</div>
<p><b>Answer: B, v &prop; &radic;r.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>v &prop; r</b> comes from using <code>r</code> in place of the area in the drag law. It is the single most common slip, and the dimensional analysis above is what rules it out: <code>&rho; r v&sup2;</code> has dimensions <code>M L&#8315;&sup1; T&#8315;&sup2;</code>, which is a pressure, not a force.</p>
<p>· <b>v &prop; r&sup2;</b> comes from dropping the square root at the end, or from treating the weight as going as <code>r&sup3;</code> while the drag goes as <code>r</code>.</p>
<p>· <b>v &prop; 1/&radic;r</b> inverts the answer. It would mean a large drop falls more slowly than a small one, which is the opposite of what happens: this is why drizzle drifts and large drops sting.</p>
<p>· <b>v independent of r</b> would require the drag and the weight to grow at the same rate in <code>r</code>. They do not — <code>r&sup2;</code> against <code>r&sup3;</code>.</p>
<p><b>The wider point.</b> Whenever a question says a quantity depends only on a list of others, dimensions alone may fix the answer. Try it first: it is often faster than the physics, and it is a check on the physics afterwards. Here it gave both the <code>r&sup2;</code> in the drag law and the final square root.</p>
<p><b>Relevant topics:</b> dimensional analysis; drag; terminal velocity; proportional reasoning.</p>''',
    "trap": "Treating the drag as proportional to <code>r</code> rather than to the cross-sectional area <code>r&sup2;</code>. Dimensions settle it immediately: <code>&rho; r v&sup2;</code> is a pressure, not a force.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 4 — C, momentum and energy.  A bullet embedding in a spring-mounted block.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 4, "id": "S01-04", "module": "C", "diff": 3,
    "topic": "An inelastic collision followed by a spring: two conservation laws in a row",
    "rel": [("C", "Momentum is conserved in the collision, kinetic energy is not"),
            ("C", "The combined mass then converts kinetic energy into spring energy"),
            ("E", "Energy stored in a spring is half the stiffness times the square of the extension"),
            ("A", "Deciding which conservation law applies to which stage")],
    "key": ["momcons", "ke", "hookeslaw"],
    "stem": '<p>A bullet of mass <code>m</code> travelling horizontally at speed <code>u</code> strikes and embeds itself in a block of mass <code>3m</code> resting on a frictionless horizontal surface. The block is attached to a fixed spring of stiffness <code>k</code>. {{FIG:s01-04}}</p><p>What is the maximum compression of the spring?</p>',
    "opts": ["u&radic;(m/k)", "(u/4)&radic;(m/k)", "(u/4)&radic;(2m/k)", "2u&radic;(m/k)", "(u/2)&radic;(m/k)"],
    "ans": 4,
    "distractors": [
        "stores the bullet's original kinetic energy, as though the collision were elastic",
        "gets the post-collision speed right but then stores the energy of the bullet alone",
        "counts the bullet plus only one of the three block masses in the moving mass",
        "assumes no momentum is lost, so the post-collision speed is still u",
        "correct",
    ],
    "profile": {
        "steps": [
            ("relate", "the collision is inelastic, so momentum is conserved but kinetic energy is not"),
            ("solve", "momentum conservation gives the common speed immediately after the collision"),
            ("relate", "the kinetic energy of the combined mass is then stored in the spring"),
            ("eliminate", "set the two energies equal and solve for the extension"),
        ],
        "relations": ["m u = (m + 3m) V", "0.5 * (4m) * V^2 = 0.5 * k * x^2", "E_spring = 0.5 k x^2"],
        "insight": "The two stages need different laws. Momentum is conserved in the collision and energy is not; after the collision energy is conserved and momentum is not (the spring exerts an external force). Using the wrong law on either stage is the whole trap.",
        "shape": "conservation",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(4/2)*sqrt(2/8)", "want": "1"},
    "sol": '''<p><b>What is being tested.</b> Whether you keep the two conservation laws apart. This question cannot be done with energy alone, and it cannot be done with momentum alone; it needs each one on the right stage.</p>
<p><b>Step 1 — decide what happens in the collision.</b> The bullet embeds, so bullet and block move off together. Kinetic energy is <i>not</i> conserved (that is what "embeds" means), but no external horizontal force acts during the very short collision, so momentum is.</p>
<div class="formula">m u = (m + 3m) V</div>
<p><b>Step 2 — the common speed.</b></p>
<div class="formula">V = m u / (4m) = u/4</div>
<p>Three quarters of the speed has gone in one step. That is the price of the inelastic collision, and it is where the kinetic energy is lost.</p>
<p><b>Step 3 — now energy, for the compression stage.</b> From here on the surface is frictionless and the only force doing work is the spring, so mechanical energy is conserved. All the kinetic energy of the combined mass becomes spring energy at maximum compression:</p>
<div class="formula">0.5 x (4m) x V&sup2; = 0.5 x k x x&sup2;</div>
<p><b>Step 4 — solve for the compression.</b> Cancel the <code>0.5</code>, substitute <code>V = u/4</code>:</p>
<div class="formula">4m x (u/4)&sup2; = k x&sup2;
4m x u&sup2;/16 = k x&sup2;
m u&sup2; / 4 = k x&sup2;
x = (u/2) &radic;(m/k)</div>
<p><b>Answer: E, (u/2)&radic;(m/k).</b></p>
<p><b>Why the other four are wrong.</b> Each one is the same chain with one step mis-set, which is why they are all dimensionally a length:</p>
<p>· <b>u&radic;(m/k)</b> stores the bullet's <i>original</i> kinetic energy, <code>0.5 m u&sup2;</code>. That is the energy before the collision, most of which has already been lost as heat and sound.</p>
<p>· <b>(u/4)&radic;(m/k)</b> gets <code>V = u/4</code> right but then stores <code>0.5 m V&sup2;</code>, using the bullet's mass alone for the moving mass. The moving mass is <code>4m</code>.</p>
<p>· <b>(u/4)&radic;(2m/k)</b> stores <code>0.5 x (2m) x V&sup2;</code> — the bullet plus only <i>one</i> of the three block masses. You can check the mass directly: with <code>2m</code> the compression comes to <code>(u/4)&radic;(2m/k)</code>, which is <code>1/&radic;2</code> of the correct value, and a compression smaller than the true one would leave the block still moving.</p>
<p>· <b>2u&radic;(m/k)</b> assumes the post-collision speed is still <code>u</code>, so no momentum was lost at all. Putting <code>V = u</code> into <code>x = V&radic;(4m/k)</code> gives exactly this.</p>
<p><b>The trap.</b> The word "embeds" is the instruction. It tells you the collision is perfectly inelastic, so you must run momentum first and energy second. A candidate who writes <code>0.5 m u&sup2; = 0.5 k x&sup2;</code> has used energy across a stage where energy is not conserved, and will get <code>u&radic;(m/k)</code>.</p>
<p><b>Relevant topics:</b> conservation of momentum; inelastic collisions; elastic potential energy; two-stage problems.</p>''',
    "trap": "Applying energy conservation across the collision. The collision is inelastic, so most of the kinetic energy is lost; only momentum survives it. Energy conservation starts <i>after</i> the bullet has embedded.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 5 — H, circuits.  Maximum power transfer to a variable load.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 5, "id": "S01-05", "module": "H", "diff": 2,
    "topic": "Maximum power in a variable load driven by a cell of internal resistance",
    "rel": [("H", "Terminal current of a cell with internal resistance"),
            ("H", "Power dissipated in a resistor is the square of the current times the resistance"),
            ("A", "Maximising a ratio without calculus, by completing a square or AM-GM")],
    "key": ["resistance", "seriesparallel", "nocalc"],
    "stem": '<p>A cell of emf <code>E</code> and internal resistance <code>r</code> is connected to a variable resistor of resistance <code>R</code>. What is the largest power that can be dissipated in the variable resistor?</p>',
    "opts": ["E&sup2;/r", "E&sup2;/(2r)", "E&sup2;/(8r)", "E&sup2;/(4r)", "E&sup2; r"],
    "ans": 3,
    "distractors": [
        "takes the whole emf to appear across the load, i.e. assumes no internal resistance",
        "puts half the emf across the load but forgets that the current also halves",
        "halves the correct answer twice over",
        "correct",
        "multiplies instead of dividing, so the answer is not even a power",
    ],
    "profile": {
        "steps": [
            ("relate", "the current is set by the total resistance, so I = E/(R + r)"),
            ("relate", "the power in the load is I squared R"),
            ("eliminate", "write the power as a function of R and simplify it to a ratio of the form x/(1+x)^2"),
            ("solve", "maximise that ratio by completing the square, which happens at R = r"),
            ("solve", "substitute R = r back to get the maximum power"),
        ],
        "relations": ["I = E / (R + r)", "P = I^2 R", "(1 + x)^2 >= 4x"],
        "insight": "The power is zero both when R is zero (no voltage across the load) and when R is infinite (no current). Something in between must be largest, and completing the square shows it is exactly R = r.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "E**2/(4*r)", "want": "E**2*r/(2*r)**2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can find a maximum without calculus, and whether you notice that the answer cannot be <code>E&sup2;/r</code> on dimensional grounds alone (that is a power, but it is the power the cell would deliver into a short circuit of zero resistance, where the voltage across the load is zero).</p>
<p><b>Step 1 — the current.</b> The cell's internal resistance is in series with the load, so the total resistance is <code>R + r</code>:</p>
<div class="formula">I = E / (R + r)</div>
<p><b>Step 2 — the power in the load.</b></p>
<div class="formula">P = I&sup2; R = E&sup2; R / (R + r)&sup2;</div>
<p><b>Step 3 — tidy it into a shape you can maximise.</b> Divide top and bottom by <code>r&sup2;</code> and write <code>x = R/r</code>:</p>
<div class="formula">P = (E&sup2;/r) x / (1 + x)&sup2;</div>
<p>Everything that depends on <code>R</code> now sits in the factor <code>x/(1+x)&sup2;</code>. Maximising <code>P</code> is the same as maximising that factor.</p>
<p><b>Step 4 — maximise the factor.</b> Expand the denominator:</p>
<div class="formula">(1 + x)&sup2; = 1 + 2x + x&sup2;</div>
<p>Divide by <code>x</code>:</p>
<div class="formula">(1 + x)&sup2; / x = 1/x + 2 + x</div>
<p>The factor is largest when this denominator is smallest. Now <code>1/x + x</code> is the sum of two positive numbers whose product is <code>1</code>, and the sum of two positive numbers with a fixed product is least when they are equal. So the minimum is at <code>x = 1</code>, giving <code>1 + 2 + 1 = 4</code>. Therefore</p>
<div class="formula">x / (1 + x)&sup2; <= 1/4</div>
<p>The maximum is at <code>R = r</code>.</p>
<p><b>Step 5 — substitute back.</b></p>
<div class="formula">P_max = (E&sup2;/r) x (1/4) = E&sup2; / (4r)</div>
<p><b>Answer: D, E&sup2;/(4r).</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>E&sup2;/r</b> is the short-circuit power, obtained by setting <code>R = 0</code>. But with <code>R = 0</code> there is no load to dissipate anything, so that power is all inside the cell.</p>
<p>· <b>E&sup2;/(2r)</b> comes from assuming half the emf appears across the load — true at <code>R = r</code> — while forgetting that the current is also halved. Using <code>P = V&sup2;/R</code> with <code>V = E/2</code> and <code>R = r</code> gives <code>E&sup2;/(4r)</code>; the error is to drop the <code>/R</code>.</p>
<p>· <b>E&sup2;/(8r)</b> halves the correct value a second time.</p>
<p>· <b>E&sup2; r</b> multiplies where it should divide. A quick dimensional check — <code>E&sup2;</code> is (volts)&sup2; = watts &times; ohms — shows that <code>E&sup2;/r</code> is a power and <code>E&sup2;r</code> is not.</p>
<p><b>The wider point.</b> Notice the useful sanity check at the start: the power must vanish at both ends of the range of <code>R</code>. At <code>R = 0</code> the voltage across the load is zero, so <code>P = VI = 0</code>. As <code>R</code> grows without limit the current tends to zero, so again <code>P = 0</code>. A maximum in between is therefore certain, and any option that fails this test is impossible. That kind of reasoning eliminates options before you have done any algebra.</p>
<p><b>Relevant topics:</b> internal resistance; electrical power; maximisation; inequalities.</p>''',
    "trap": "Assuming the maximum power is <code>E&sup2;/r</code>, the short-circuit value. At <code>R = 0</code> there is no potential difference across the load, so the power delivered to it is zero, not a maximum.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 6 — A, toolkit.  Estimation: what the atmosphere weighs.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 6, "id": "S01-06", "module": "A", "diff": 3,
    "topic": "Estimation: the mass of the air standing on a square metre",
    "rel": [("A", "Order-of-magnitude estimation: choosing the right few quantities"),
            ("M", "Pressure is force per unit area, and the atmosphere's weight is what supplies it"),
            ("C", "Weight is mass times gravitational field strength")],
    "key": ["estimate", "ratio", "nocalc"],
    "stem": '<p>The atmospheric pressure at sea level is about 1.0 &times; 10&#8309; Pa, and <code>g</code> is about 10 N kg&#8315;&#185;.</p><p>Which of these is the best estimate of the mass of the air standing on each square metre of the Earth\u2019s surface?</p>',
    "opts": ["10\u00b3 kg", "10\u2074 kg", "10&#8309; kg", "10&#8310; kg", "10&#8311; kg"],
    "ans": 1,
    "distractors": [
        "divides by 100 rather than by 10, i.e. takes g to be 100 N kg to the minus one",
        "correct",
        "reports the pressure in pascals as though it were already a mass",
        "multiplies by g instead of dividing by it",
        "is two factors of ten out, from dividing by g twice",
    ],
    "profile": {
        "steps": [
            ("read", "recognise that the atmosphere is held up by its own weight, so the pressure is that weight per unit area"),
            ("relate", "turn pressure into the weight of a one square metre column"),
            ("relate", "turn that weight into a mass by dividing by g"),
            ("solve", "put in the numbers and round to one significant figure"),
        ],
        "relations": ["p = F / A", "W = m g", "1 atmosphere ~ 10^5 Pa"],
        "insight": "The pressure is a WEIGHT per unit area, not a mass per unit area. The whole question is the single division by g, and forgetting it is what makes the answer ten times too big.",
        "shape": "order-of-magnitude",
        "approx": True,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1.0e5*1/10", "want": "10000"},
    "sol": '''<p><b>What is being tested.</b> Whether you can turn a pressure into a mass, and whether you know that a pressure is a <i>force</i> per unit area. This is an estimation question, so only the power of ten matters.</p>
<p><b>Step 1 — where the pressure comes from.</b> The air above a patch of ground is held up by that ground. So the force the atmosphere exerts on a square metre is exactly the weight of the column of air above it. This is the step people skip, and it is the whole question.</p>
<div class="formula">p = W / A</div>
<p><b>Step 2 — the weight of a one square metre column.</b> With <code>A = 1 m&sup2;</code>:</p>
<div class="formula">W = p A = 10&#8309; N</div>
<p>A hundred thousand newtons per square metre. That is about ten tonnes of force pressing on every square metre, which is why the number is worth pausing over.</p>
<p><b>Step 3 — turn weight into mass.</b></p>
<div class="formula">m = W / g = 10&#8309; / 10 = 10&#8308; kg</div>
<p><b>Step 4 — sanity check.</b> Ten tonnes per square metre sounds enormous until you picture it: the column reaches the top of the atmosphere, roughly 10 km of air at about 1 kg m&#8315;&sup3; near the ground. A 10 km column at that density is <code>10&#8308; m &times; 1 kg m&#8315;&sup3; = 10&#8308; kg m&#8315;&sup2;</code>. The two routes agree, which is a good sign.</p>
<p><b>Answer: B, 10&#8308; kg.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>10&#8309; kg</b> is the pressure in pascals quoted as a mass. It is the mistake of stopping one step early.</p>
<p>· <b>10&#8310; kg</b> comes from multiplying by <code>g</code> instead of dividing. A weight is <i>bigger</i> than the mass that produces it, so multiplying makes the answer move the wrong way.</p>
<p>· <b>10&#179; kg</b> divides by 100, which is what you get by using <code>g = 100</code>.</p>
<p>· <b>10&#8311; kg</b> is two powers of ten out.</p>
<p><b>The wider point.</b> Estimation questions are marked on the power of ten, and the way to be safe is to keep track of the physical meaning of each quantity rather than the symbols. "Pressure is a weight per unit area" is the fact being tested; once you have it, the arithmetic is a single division.</p>
<p><b>Relevant topics:</b> pressure; weight; estimation; orders of magnitude.</p>''',
    "trap": "Quoting <code>10&#8309; kg</code> because the pressure is <code>10&#8309; Pa</code>. A pascal is a newton per square metre, so the pressure gives you a weight, and you must still divide by <code>g</code> to get a mass.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 7 — B, kinematics.  A ball passing the same height twice.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 7, "id": "S01-07", "module": "B", "diff": 3,
    "topic": "A projectile passing the same height on the way up and on the way down",
    "rel": [("B", "Constant-acceleration kinematics: displacement as a function of time"),
            ("B", "The same height is reached twice, and the two times are the roots of one quadratic"),
            ("A", "Reading a physical interval off the difference between two roots")],
    "key": ["kinematics", "surds", "graphshape"],
    "stem": '<p>A ball is thrown vertically upward from ground level with speed <code>u</code>. It passes a point at height <code>h</code> twice: once on the way up and once on the way down. {{FIG:s01-07}}</p><p>What is the time interval between the two passages?</p>',
    "opts": ["&radic;(u&sup2; - 2gh)/g", "u/g", "2&radic;(2gh)/g", "2u/g", "2&radic;(u&sup2; - 2gh)/g"],
    "ans": 4,
    "distractors": [
        "gives only the time from the highest point down to the height h, which is one root's distance from the apex rather than the gap between the roots",
        "gives the time to reach the highest point, which is the midpoint of the interval and not its length",
        "treats the ball as dropped from rest at height h, so the speed at the height is missing",
        "gives the whole flight time from the ground back to the ground",
        "correct",
    ],
    "profile": {
        "steps": [
            ("relate", "write the displacement at time t with the upward direction taken as positive"),
            ("relate", "set the displacement equal to h and rearrange into a quadratic in t"),
            ("solve", "solve the quadratic; the two roots are the two passage times"),
            ("eliminate", "subtract the smaller root from the larger to get the interval"),
        ],
        "relations": ["s = u t - 0.5 g t^2", "quadratic formula", "t2 - t1 = 2 sqrt(u^2 - 2gh) / g"],
        "insight": "The two passages are the two roots of ONE quadratic. You never need the times themselves — only their difference, and in the quadratic formula the square root is exactly half of it.",
        "shape": "symmetry",
        "approx": False,
        "symbolic": True,
        "figure_support": True,
    },
    "check": {"kind": "eval", "expr": "2*sqrt(5**2-2*10*0.8)/10", "want": "0.6"},
    "sol": '''<p><b>What is being tested.</b> Whether you see that "twice" means "two roots of one equation", and whether you can take a difference of roots without grinding out both times separately.</p>
<p><b>Step 1 — write the displacement.</b> Taking upward as positive, and remembering that gravity acts downward:</p>
<div class="formula">s = u t - 0.5 g t&sup2;</div>
<p><b>Step 2 — impose the condition.</b> The ball is at height <code>h</code> when <code>s = h</code>:</p>
<div class="formula">h = u t - 0.5 g t&sup2;</div>
<p>Rearranged into standard form:</p>
<div class="formula">0.5 g t&sup2; - u t + h = 0</div>
<p>This is a quadratic in <code>t</code>, so it has two roots. That is the whole content of "it passes the point twice": one root is the time on the way up, the other the time on the way down.</p>
<p><b>Step 3 — solve the quadratic.</b> With <code>a = 0.5g</code>, <code>b = -u</code>, <code>c = h</code>:</p>
<div class="formula">t = [ u &plusmn; &radic;(u&sup2; - 2gh) ] / g</div>
<p>The two roots are <code>t&#8321; = (u - &radic;(u&sup2; - 2gh))/g</code> and <code>t&#8322; = (u + &radic;(u&sup2; - 2gh))/g</code>.</p>
<p><b>Step 4 — subtract.</b> The interval is</p>
<div class="formula">t&#8322; - t&#8321; = 2&radic;(u&sup2; - 2gh) / g</div>
<p>Notice that <code>u</code> has cancelled entirely from the difference. That is worth pausing on: the interval depends on <code>h</code> and <code>g</code>, but not on how hard the ball was thrown — as long as it is thrown hard enough to get there at all.</p>
<p><b>Answer: E, 2&radic;(u&sup2; - 2gh)/g.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>&radic;(u&sup2; - 2gh)/g</b> is exactly half the answer. It is the time from the apex down to <code>h</code>, because at the apex the speed is zero and the time to fall a distance <code>(u&sup2;/2g - h)</code> is <code>&radic;(2(u&sup2;/2g - h)/g) = &radic;(u&sup2; - 2gh)/g</code>. By symmetry that is also the time from <code>h</code> up to the apex, so the full interval is twice it.</p>
<p>· <b>u/g</b> is the time to reach the highest point — the middle of the interval, not its length.</p>
<p>· <b>2&radic;(2gh)/g</b> drops the <code>u&sup2;</code> term, which is what you get by treating the ball as simply dropped from height <code>h</code>. That would require the ball to have zero speed at <code>h</code>, in which case it would only be there once.</p>
<p>· <b>2u/g</b> is the whole flight time, ground to ground. It is the special case <code>h = 0</code>, and it is the largest the interval can ever be.</p>
<p><b>A quick numerical check.</b> Take <code>u = 5 m/s</code>, <code>g = 10 N kg&#8315;&#185;</code> and <code>h = 0.8 m</code>. Then <code>u&sup2; - 2gh = 25 - 16 = 9</code>, so the interval is <code>2 x 3 / 10 = 0.6 s</code>. Solving the quadratic directly gives roots <code>0.8 s</code> and <code>0.2 s</code>, whose difference is indeed <code>0.6 s</code>. The formula and the two-times route agree.</p>
<p><b>Relevant topics:</b> constant acceleration; quadratic equations; symmetry of projectile motion.</p>''',
    "trap": "Answering <code>&radic;(u&sup2; - 2gh)/g</code> — half the interval. That is the time from the apex down to <code>h</code>, and by symmetry it is also the time from <code>h</code> up to the apex, so the gap between the two passages is twice it.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 8 — C, statics.  Moments about a hinge.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 8, "id": "S01-08", "module": "C", "diff": 2,
    "topic": "A horizontal beam held by an angled stay: moments about the hinge",
    "rel": [("C", "Taking moments about a point removes the unknown forces acting there"),
            ("C", "Only the perpendicular component of a force produces a moment"),
            ("C", "The weight of a uniform beam acts at its midpoint")],
    "key": ["moments", "statics", "com"],
    "stem": '<p>A uniform horizontal beam of mass 20 kg and length 4.0 m is freely hinged to a vertical wall at one end. A light stay wire is attached to the other end and runs to the wall, making an angle of 30&deg; with the beam. {{FIG:s01-08}}</p><p>What is the tension in the stay?</p>',
    "opts": ["50 N", "100 N", "200 N", "115 N", "400 N"],
    "ans": 2,
    "distractors": [
        "multiplies by the sine of the angle instead of dividing by it",
        "takes the stay to be vertical, so the tension is simply half the weight",
        "correct",
        "resolves the tension with the cosine of the angle rather than its sine",
        "takes moments about the far end, so the whole weight acts at the full length",
    ],
    "profile": {
        "steps": [
            ("read", "choose the hinge as the pivot, so the hinge force drops out of the equation"),
            ("relate", "the weight acts at the midpoint, a lever arm of half the length"),
            ("relate", "only the component of the tension perpendicular to the beam makes a moment, and that component is T sin 30 degrees"),
            ("solve", "equate the two moments and solve for T"),
        ],
        "relations": ["sum of moments = 0", "moment = F d sin(theta)", "T sin(30) * L = mg * L/2"],
        "insight": "Choosing the hinge as the pivot is what makes the problem one equation instead of three: the unknown hinge force has zero lever arm there and vanishes.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "20*10/(2*sin(pi/6))", "want": "200"},
    "sol": '''<p><b>What is being tested.</b> Two things at once: that the weight of a uniform beam acts at its midpoint, and that an angled force only produces a moment through the component perpendicular to the beam.</p>
<p><b>Step 1 — choose the pivot.</b> Take moments about the hinge. The beam is in equilibrium, so the total moment about <i>any</i> point is zero, and we are free to pick the most convenient one. The hinge is convenient because the force the hinge exerts acts there: its lever arm is zero, so it contributes nothing and never has to be found.</p>
<p><b>Step 2 — the moment of the weight.</b> The beam is uniform, so its centre of gravity is at its midpoint, a distance <code>L/2 = 2.0 m</code> from the hinge. The weight is</p>
<div class="formula">W = m g = 20 x 10 = 200 N</div>
<p>acting downward, so the moment is</p>
<div class="formula">moment of W = 200 x 2.0 = 400 N m   (clockwise)</div>
<p><b>Step 3 — the moment of the tension.</b> The stay makes 30&deg; with the beam. Only the component of <code>T</code> perpendicular to the beam produces a moment, and that component is <code>T sin 30&deg;</code>. It acts at the far end, a distance <code>L = 4.0 m</code> from the hinge:</p>
<div class="formula">moment of T = T sin 30&deg; x 4.0   (anticlockwise)</div>
<p><b>Step 4 — equate and solve.</b></p>
<div class="formula">T sin 30&deg; x 4.0 = 400
T x 0.5 x 4.0 = 400
2.0 T = 400
T = 200 N</div>
<p><b>Answer: C, 200 N.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>100 N</b> is <code>mg/2</code>: the stay treated as vertical, so the tension is just half the weight. The angle has been ignored.</p>
<p>· <b>50 N</b> multiplies by <code>sin 30&deg;</code> instead of dividing by it, which moves the answer the wrong way. A quick physical check settles it: the stay pulls at 30&deg;, so it must pull <i>harder</i> than a vertical stay would, not less.</p>
<p>· <b>115 N</b> resolves with <code>cos 30&deg;</code> instead of <code>sin 30&deg;</code>. The perpendicular component of a force at angle &theta; to the beam is <code>T sin &theta;</code>; the cosine gives the component <i>along</i> the beam, which produces no moment about the hinge at all.</p>
<p>· <b>400 N</b> takes moments about the far end, so the whole weight acts at the full length <code>L</code> rather than at <code>L/2</code>.</p>
<p><b>The wider point.</b> In every statics question, the first decision is where to put the pivot, and the right answer is "somewhere that removes an unknown". Here that is the hinge. If the question had also asked for the hinge force, you would then resolve horizontally and vertically to find it — the moment equation would already have done the hard part.</p>
<p><b>Relevant topics:</b> moments; equilibrium; centre of gravity; resolving forces.</p>''',
    "trap": "Using the whole weight at the far end. A uniform beam's weight acts at its midpoint, so its moment about the hinge is <code>mg &times; L/2</code>, not <code>mg &times; L</code>.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 9 — D, circular motion.  Losing contact on a hump-backed bridge.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 9, "id": "S01-09", "module": "D", "diff": 3,
    "topic": "The speed at which a car leaves the road on a hump-backed bridge",
    "rel": [("D", "Circular motion: the net inward force is the centripetal force"),
            ("D", "Losing contact is the condition that the normal reaction falls to zero"),
            ("C", "Newton's second law applied along the radius at the top of the arc")],
    "key": ["circular", "force", "limits"],
    "stem": '<p>A car crosses a hump-backed bridge whose top may be taken as an arc of radius 20 m. Take <code>g = 10 N kg&#8315;&#185;</code>.</p><p>Above what speed does the car leave the road at the top of the bridge?</p>',
    "opts": ["14 m/s", "10 m/s", "20 m/s", "200 m/s", "400 m/s"],
    "ans": 0,
    "distractors": [
        "correct",
        "sets the losing-contact condition at N = mg/2 rather than N = 0",
        "uses the diameter 40 m in place of the radius",
        "reports gr without taking the square root",
        "reports 2gr without taking the square root, using the diameter as well",
    ],
    "profile": {
        "steps": [
            ("relate", "at the top of the arc the centre of the circle is below, so the net downward force is mg minus N"),
            ("relate", "that net force is the centripetal force, mv squared over r"),
            ("eliminate", "losing contact means N has fallen to zero, which leaves mg alone to supply the centripetal force"),
            ("solve", "solve for v and evaluate"),
        ],
        "relations": ["mg - N = m v^2 / r", "N = 0 at the limit", "v^2 = g r"],
        "insight": "The car leaves the road exactly when the road has nothing left to push with. Setting N = 0 is the whole question; the rest is rearranging.",
        "shape": "limiting-case",
        "approx": True,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "sqrt(10*20)", "want": "10*sqrt(2)"},
    "sol": '''<p><b>What is being tested.</b> Whether you can identify the "just leaving" condition. It is not a new force appearing; it is an existing force disappearing.</p>
<p><b>Step 1 — the forces at the top of the arc.</b> Two forces act on the car at the top: its weight <code>mg</code> downward, and the normal reaction <code>N</code> from the road upward. The centre of the circular arc is <i>below</i> the car, so the inward (centripetal) direction is downward, and the net inward force is</p>
<div class="formula">F = mg - N</div>
<p><b>Step 2 — that net force is the centripetal force.</b></p>
<div class="formula">mg - N = m v&sup2; / r</div>
<p>Read that equation physically. As <code>v</code> grows, the right-hand side grows, so <code>N</code> must shrink. The road has to push less and less hard the faster the car goes.</p>
<p><b>Step 3 — the limiting condition.</b> The road can only push, never pull. So the smallest <code>N</code> can be is zero, and "just leaving the road" is exactly <code>N = 0</code>:</p>
<div class="formula">mg = m v&sup2; / r</div>
<p><b>Step 4 — solve and evaluate.</b> The mass cancels, which is worth noticing: the answer does not depend on how heavy the car is.</p>
<div class="formula">v&sup2; = g r = 10 x 20 = 200
v = &radic;200 &asymp; 14 m/s</div>
<p><b>Answer: A, 14 m/s.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>10 m/s</b> comes from setting <code>N = mg/2</code> as the losing-contact condition, i.e. from assuming the car leaves when the reaction has merely halved. It leaves when the reaction reaches zero.</p>
<p>· <b>20 m/s</b> uses the diameter <code>2r = 40 m</code> in place of the radius. It is worth checking which one the geometry gives you: the radius is the distance from the car to the centre of the arc, which is 20 m.</p>
<p>· <b>200 m/s</b> is <code>gr</code>, the square root forgotten. A units check catches it: <code>gr</code> has units m&sup2; s&#8315;&sup2;, not m s&#8315;&#185;.</p>
<p>· <b>400 m/s</b> is <code>2gr</code>, so it uses the diameter <i>and</i> forgets the root.</p>
<p><b>The wider point.</b> The same structure appears in a ball whirled in a vertical circle (the string goes slack at the top), in a satellite at the surface, and in a bucket of water swung overhead. In every case, the quantity that can only push or only pull reaches its limit at zero, and setting it to zero gives the threshold.</p>
<p><b>Relevant topics:</b> circular motion; centripetal force; normal reaction; limiting conditions.</p>''',
    "trap": "Looking for a new force to appear. Nothing new happens when the car leaves the road — the normal reaction, which can only push, simply reaches zero. Set <code>N = 0</code>, not <code>N = mg/2</code>.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 10 — F, waves.  Three successive resonances of a closed pipe.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 10, "id": "S01-10", "module": "F", "diff": 2,
    "topic": "Three successive resonances of a pipe closed at one end",
    "rel": [("F", "A pipe closed at one end supports only odd harmonics"),
            ("F", "Successive resonances are separated by twice the fundamental frequency"),
            ("A", "Using the spacing of a sequence rather than its members")],
    "key": ["standingwaves", "waves", "ratio"],
    "stem": '<p>A pipe closed at one end is found to resonate at 300 Hz, 500 Hz and 700 Hz, with no resonance in between. {{FIG:s01-10}}</p><p>What is the fundamental frequency of the pipe?</p>',
    "opts": ["50 Hz", "150 Hz", "200 Hz", "100 Hz", "300 Hz"],
    "ans": 3,
    "distractors": [
        "divides the spacing by 4 instead of by 2",
        "averages the first two resonances, which is not a frequency the pipe supports",
        "reports the spacing itself as the fundamental",
        "correct",
        "reports the lowest resonance given as the fundamental",
    ],
    "profile": {
        "steps": [
            ("read", "recall that a closed pipe supports odd multiples of the fundamental only"),
            ("relate", "so the resonances are f, 3f, 5f and the gap between neighbours is 2f"),
            ("solve", "the gap here is 200 Hz, so the fundamental is 100 Hz"),
            ("check", "confirm that 300, 500 and 700 are the third, fifth and seventh harmonics of 100 Hz"),
        ],
        "relations": ["closed pipe: f, 3f, 5f, ...", "gap between successive resonances = 2f", "lambda = 4L/(2n-1)"],
        "insight": "You never need the pipe's length or the speed of sound. The three given frequencies already contain the fundamental, encoded in the 200 Hz gap between neighbours.",
        "shape": "superposition",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(700-500)/2", "want": "100"},
    "sol": '''<p><b>What is being tested.</b> Whether you know which harmonics a closed pipe can produce. A pipe open at both ends gives all of them; a pipe closed at one end gives only the odd ones, and that single fact answers this question.</p>
<p><b>Step 1 — what a closed pipe allows.</b> The closed end must be a node (the air cannot move there) and the open end an antinode (the air is free to move). The shortest pattern that fits is a quarter wavelength, and every longer one adds a half wavelength:</p>
<div class="formula">L = lambda/4, 3lambda/4, 5lambda/4, ...
f = f&#8320;, 3f&#8320;, 5f&#8320;, ...</div>
<p>where <code>f&#8320;</code> is the fundamental. So the allowed frequencies are the <i>odd</i> multiples of the fundamental.</p>
<p><b>Step 2 — the gap between neighbours.</b> Consecutive allowed frequencies are <code>f&#8320;</code>, <code>3f&#8320;</code>, <code>5f&#8320;</code>, so the gap between any two neighbours is</p>
<div class="formula">3f&#8320; - f&#8320; = 2f&#8320;</div>
<p><b>Step 3 — read the gap off the data.</b> The three given frequencies are 300, 500 and 700 Hz, and the question says there is nothing in between. The gap is</p>
<div class="formula">500 - 300 = 200 Hz   (and 700 - 500 = 200 Hz)</div>
<p>So <code>2f&#8320; = 200 Hz</code> and</p>
<div class="formula">f&#8320; = 100 Hz</div>
<p><b>Step 4 — check.</b> If the fundamental is 100 Hz the odd harmonics are 100, 300, 500, 700, 900 Hz. The three quoted values are exactly the 3rd, 5th and 7th. The 100 Hz resonance itself is simply not among the three that were measured, which is perfectly consistent with the question as worded.</p>
<p><b>Answer: D, 100 Hz.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>300 Hz</b> is the lowest frequency given. It is a resonance, but it is the third harmonic, not the fundamental. This is the most tempting wrong answer, because it is the smallest number on the page.</p>
<p>· <b>200 Hz</b> is the gap. It is <code>2f&#8320;</code>, not <code>f&#8320;</code>.</p>
<p>· <b>150 Hz</b> averages 100 and 200; it is not a frequency this pipe can produce at all.</p>
<p>· <b>50 Hz</b> divides the gap by 4, which would be right for a pipe open at <i>both</i> ends, where the gap is <code>f&#8320;</code>... — no, for an open pipe the gap between successive resonances is <code>f&#8320;</code> itself, so that error does not even arise there. It is simply a factor of two out from the correct answer.</p>
<p><b>The wider point.</b> Whenever a question gives you a <i>sequence</i> of resonances and asks for the fundamental, use the spacing. It is more robust than trying to identify which harmonic each frequency is, and it works even when the lowest resonances have not been measured.</p>
<p><b>Relevant topics:</b> stationary waves in pipes; harmonics; boundary conditions; resonance.</p>''',
    "trap": "Answering <code>300 Hz</code> because it is the smallest frequency given. A closed pipe produces only odd harmonics, and 300 Hz is the third harmonic of a 100 Hz fundamental.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 11 — G, optics.  The smallest refractive index that traps the ray.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 11, "id": "S01-11", "module": "G", "diff": 3,
    "topic": "The minimum refractive index for total internal reflection inside a prism",
    "rel": [("G", "Total internal reflection: the critical angle is set by the refractive index"),
            ("G", "Geometry of a 45-45-90 prism fixes the angle of incidence at the hypotenuse"),
            ("A", "A minimum condition: the equality case of an inequality")],
    "key": ["criticalangle", "snell", "refractive"],
    "stem": '<p>A ray of light enters a glass prism normally through one of the short faces. The prism is a right-angled isosceles triangle, so the ray meets the long face at 45&deg;. {{FIG:s01-11}}</p><p>What is the smallest refractive index the glass can have if the ray is to be totally internally reflected at the long face?</p>',
    "opts": ["1.2", "4/3", "&radic;2", "1.5", "&radic;3"],
    "ans": 2,
    "distractors": [
        "uses the sine of 55 degrees in place of the sine of 45 degrees",
        "quotes the refractive index of water, a familiar value that is below the threshold",
        "correct",
        "quotes a typical glass, which does reflect the ray but is not the smallest value that does",
        "uses 30 degrees in place of 45 degrees",
    ],
    "profile": {
        "steps": [
            ("read", "the ray enters normally, so it is not bent at the first face and travels straight on"),
            ("relate", "the geometry of an isosceles right triangle puts the angle of incidence at the long face at 45 degrees"),
            ("relate", "total internal reflection needs the angle of incidence to exceed the critical angle, so sin(45) must be at least 1/n"),
            ("eliminate", "the threshold is the equality case, which gives the smallest n that works"),
            ("solve", "n = 1 / sin(45) = the square root of 2"),
            ("check", "the options are numbers, so the threshold has to be placed among them: the square root of 2 is about 1.41, which is above 4/3 and below 1.5"),
        ],
        "relations": ["sin(theta_c) = 1/n", "TIR requires theta > theta_c", "n_min = 1/sin(45)",
                      "sqrt(2) is between 4/3 and 1.5"],
        "insight": "The angle of incidence is fixed by the prism's shape, not by the ray. So the only thing that can be varied is the refractive index, and the threshold is the equality case of the critical-angle condition.",
        "shape": "limiting-case",
        "approx": True,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "1/sin(pi/4)", "want": "sqrt(2)"},
    "sol": '''<p><b>What is being tested.</b> Whether you can combine a geometric fact with an optical one. The geometry is supplied by the shape of the prism; the optics by the critical-angle condition.</p>
<p><b>Step 1 — the first face does nothing.</b> The ray enters normally, meaning perpendicular to the surface. A ray along the normal is undeviated by refraction, so it carries on in a straight line inside the glass. No Snell's law calculation is needed here, and trying to do one is a waste of the two minutes.</p>
<p><b>Step 2 — where the ray arrives.</b> The prism is a right-angled isosceles triangle, so its two acute angles are 45&deg;. A ray travelling along one of the short directions meets the long face at 45&deg; to the normal. This is the angle of incidence at the glass-air boundary:</p>
<div class="formula">theta = 45&deg;</div>
<p><b>Step 3 — the condition for total internal reflection.</b> Light inside a medium of refractive index <code>n</code> striking a boundary with air is totally internally reflected if the angle of incidence exceeds the critical angle <code>theta_c</code>, where</p>
<div class="formula">sin theta_c = 1/n</div>
<p>So the requirement is <code>sin 45&deg; &gt; 1/n</code>, or equivalently</p>
<div class="formula">n &gt; 1 / sin 45&deg;</div>
<p><b>Step 4 — the smallest value.</b> The question asks for the smallest <code>n</code>, which is the equality case:</p>
<div class="formula">n_min = 1 / sin 45&deg; = 1 / (1/&radic;2) = &radic;2 &asymp; 1.4</div>
<p><b>Answer: C, &radic;2.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>1.5</b> is a typical glass, and it does give total internal reflection here (since <code>1.5 &gt; &radic;2</code>). It is wrong only because the question asks for the <i>smallest</i> index that works. Reading the question as "will it reflect?" instead of "what is the threshold?" is the trap.</p>
<p>· <b>4/3</b> is the refractive index of water, quoted because it is a familiar number. It is <i>below</i> <code>&radic;2</code>, so a prism made of it would leak the ray out at the long face.</p>
<p>· <b>1.2</b> uses <code>sin 55&deg;</code> in place of <code>sin 45&deg;</code>, and is well below the threshold.</p>
<p>· <b>&radic;3</b> uses 30&deg; instead of 45&deg;. A 30-60-90 prism would indeed have a threshold of <code>1/sin 30&deg; = 2</code>, not <code>&radic;3</code>, so this option is wrong twice over.</p>
<p><b>The wider point.</b> Prisms that turn a beam through 90&deg; or 180&deg; by total internal reflection are common in optical instruments, and they rely on exactly this: the glass must be chosen so that 45&deg; exceeds the critical angle. Ordinary crown glass at <code>n = 1.5</code> clears the threshold with a little room to spare, which is why such prisms are made of it.</p>
<p><b>Relevant topics:</b> total internal reflection; critical angle; prism geometry; threshold conditions.</p>''',
    "trap": "Choosing <code>1.5</code> because that is a typical glass and it does reflect. The question asks for the smallest index that works, which is the equality case <code>1/sin 45&deg; = &radic;2</code>.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 12 — H, circuits.  Reading a resistance off a non-ohmic graph.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 12, "id": "S01-12", "module": "H", "diff": 2,
    "topic": "The resistance of a filament lamp at one point on its characteristic",
    "rel": [("H", "Resistance at a point is the ratio V/I at that point"),
            ("H", "A filament lamp is non-ohmic: its resistance changes with current"),
            ("A", "Reading a value off a graph, and knowing that a gradient is not a ratio")],
    "key": ["resistance", "loggraphs", "readdiagram"],
    "stem": '<p>The graph shows how the current through a filament lamp varies with the potential difference across it. A point on the curve is marked at 6.0 V, 0.40 A. {{FIG:s01-12}}</p><p>What is the resistance of the lamp at that point?</p>',
    "opts": ["2.4 &Omega;", "6.0 &Omega;", "7.5 &Omega;", "15 &Omega;", "24 &Omega;"],
    "ans": 3,
    "distractors": [
        "multiplies the potential difference by the current instead of dividing",
        "divides by a current of 1.0 A, misreading the gridline",
        "reads the current as 0.80 A, taking the wrong gridline",
        "correct",
        "reads the current as 0.25 A, taking the wrong gridline",
    ],
    "profile": {
        "steps": [
            ("read", "the resistance at a point is V divided by I at that point, not the gradient of the graph"),
            ("relate", "the axes are V against I, so V/I is the ratio of the coordinates, while the gradient would be dV/dI"),
            ("solve", "divide 6.0 by 0.40"),
            ("check", "note that because the curve bends over, the resistance rises as the current rises"),
        ],
        "relations": ["R = V / I", "gradient of a V-I graph is not the resistance", "a filament lamp's resistance rises with temperature"],
        "insight": "On a V-I graph the resistance at a point is the RATIO of the coordinates, which is the slope of the line from the origin to the point — not the gradient of the curve.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "6.0/0.40", "want": "15"},
    "sol": '''<p><b>What is being tested.</b> A single distinction that decides a whole family of questions: on a graph of <code>V</code> against <code>I</code>, the resistance is the <i>ratio</i> <code>V/I</code>, which is the slope of the line drawn from the origin to the point — not the gradient of the curve at the point.</p>
<p><b>Step 1 — what resistance means at a point.</b> Resistance is defined by <code>R = V/I</code>. That is a statement about a pair of values, so it applies at one point on the graph, not along a tangent.</p>
<p><b>Step 2 — the two different slopes.</b> The gradient of the curve is <code>dV/dI</code>, which has units of ohms too but is a different quantity. For a straight line through the origin they coincide, which is exactly why the distinction is easy to miss. For a curved characteristic they do not.</p>
<p><b>Step 3 — read the point and divide.</b> The marked point is at <code>V = 6.0 V</code> and <code>I = 0.40 A</code>, so</p>
<div class="formula">R = V / I = 6.0 / 0.40 = 15 &Omega;</div>
<p><b>Step 4 — check it is sensible.</b> A 6.0 V lamp drawing 0.40 A has a resistance of 15 &Omega;, which is a realistic value for a small filament lamp when it is hot. Note also that this is much larger than the lamp's resistance when cold, which is the reason its characteristic curves over rather than being straight.</p>
<p><b>Answer: D, 15 &Omega;.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>2.4 &Omega;</b> is <code>V &times; I</code>, the product instead of the ratio. Units catch it: volts times amperes is watts, not ohms.</p>
<p>· <b>6.0 &Omega;</b> divides by <code>1.0 A</code>, i.e. the number on the axis rather than the current at the point.</p>
<p>· <b>7.5 &Omega;</b> divides by <code>0.80 A</code>, reading the wrong gridline.</p>
<p>· <b>24 &Omega;</b> divides by <code>0.25 A</code>, again a misread gridline.</p>
<p><b>The wider point.</b> The same distinction appears in a stress-strain graph, where Young's modulus is the gradient of the linear part rather than a ratio of coordinates, and in a velocity-time graph, where the gradient is acceleration but the ratio of coordinates is average velocity. Ask which of the two the question wants before you start reading numbers.</p>
<p><b>Relevant topics:</b> resistance; current-voltage characteristics; non-ohmic conductors; reading graphs.</p>''',
    "trap": "Taking the gradient of the curve. On a curved <code>V</code>-<code>I</code> characteristic the gradient <code>dV/dI</code> is not the resistance; the resistance at a point is <code>V/I</code>, the slope of the line from the origin.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 13 — J, thermal.  A hot block quenched in water.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 13, "id": "S01-13", "module": "J", "diff": 2,
    "topic": "Thermal equilibrium between a hot metal block and cooler water",
    "rel": [("J", "Heat gained equals heat lost, once the mixture has settled"),
            ("J", "The heat needed to change a temperature by dT is mc dT"),
            ("A", "Weighting an average by the right quantity: here by heat capacity, not by mass")],
    "key": ["specificheat", "ratio", "nocalc"],
    "stem": '<p>A metal block of mass 0.20 kg and specific heat capacity 500 J kg&#8315;&#185; K&#8315;&#185; is at 200 &deg;C. It is dropped into 0.10 kg of water, of specific heat capacity 4000 J kg&#8315;&#185; K&#8315;&#185;, at 20 &deg;C. The container is an ideal insulator.</p><p>What is the final temperature of the block and water?</p>',
    "opts": ["20 &deg;C", "40 &deg;C", "110 &deg;C", "140 &deg;C", "56 &deg;C"],
    "ans": 4,
    "distractors": [
        "leaves the water at its starting temperature, as though the block made no difference",
        "uses the specific heat capacities but ignores the masses, which is the weighting the wrong way round",
        "takes the plain average of the two starting temperatures",
        "weights by mass but ignores the specific heat capacities",
        "correct",
    ],
    "profile": {
        "steps": [
            ("relate", "in an insulated container the heat lost by the block equals the heat gained by the water"),
            ("relate", "each side is mass times specific heat capacity times the temperature change"),
            ("eliminate", "the unknown final temperature appears on both sides, so collect it on one side"),
            ("solve", "divide to get the final temperature"),
        ],
        "relations": ["Q = m c dT", "heat lost = heat gained", "C = m c is the heat capacity"],
        "insight": "The final temperature is a WEIGHTED average of the two starting temperatures, and the weighting is by heat capacity mc — not by mass, and not by specific heat capacity alone. The metal block has a small mass but a large specific heat capacity, and it is their product that counts.",
        "shape": "conservation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(100*200+400*20)/(100+400)", "want": "56"},
    "sol": '''<p><b>What is being tested.</b> Whether you identify the correct weighting. The answer is a weighted average of 200 &deg;C and 20 &deg;C, and the weights are the heat capacities <code>mc</code>, not the masses and not the specific heat capacities.</p>
<p><b>Step 1 — the principle.</b> In an insulated container no heat escapes, so whatever the block loses the water gains:</p>
<div class="formula">heat lost by block = heat gained by water</div>
<p><b>Step 2 — write each side.</b> Let the final temperature be <code>&theta;</code>. The block cools from 200 &deg;C and the water warms from 20 &deg;C:</p>
<div class="formula">m_block c_block (200 - &theta;) = m_water c_water (&theta; - 20)</div>
<p>It is worth computing each heat capacity separately, because that is the quantity that actually does the weighting:</p>
<div class="formula">C_block = 0.20 x 500 = 100 J K&#8315;&#185;
C_water = 0.10 x 4000 = 400 J K&#8315;&#185;</div>
<p><b>Step 3 — substitute and collect.</b></p>
<div class="formula">100 (200 - &theta;) = 400 (&theta; - 20)
20000 - 100&theta; = 400&theta; - 8000
28000 = 500&theta;</div>
<p><b>Step 4 — solve.</b></p>
<div class="formula">&theta; = 28000 / 500 = 56 &deg;C</div>
<p><b>Answer: E, 56 &deg;C.</b></p>
<p><b>Check the answer is between the two starting values.</b> It must be: energy flows from hot to cold, so the final temperature cannot be above 200 &deg;C or below 20 &deg;C. That single test eliminates two of the options immediately. It is also much closer to 20 &deg;C than to 200 &deg;C, which is right, because the water's heat capacity is four times the block's.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>110 &deg;C</b> is the plain average <code>(200+20)/2</code>. It would be correct only if the two heat capacities were equal, and they are not — 100 against 400.</p>
<p>· <b>140 &deg;C</b> weights by mass alone, giving <code>(0.20 x 200 + 0.10 x 20)/0.30</code>. The specific heat capacities matter as much as the masses.</p>
<p>· <b>40 &deg;C</b> uses the specific heat capacities without the masses. Both factors are needed; only their product has the right units, J K&#8315;&#185;.</p>
<p>· <b>20 &deg;C</b> leaves the water unchanged, as though dropping in a hot block did nothing.</p>
<p><b>The wider point.</b> "Weighted average" questions are common and the weight is easy to get wrong. The safe method is always the same: write the two heat quantities in full, <code>mc&Delta;T</code> on each side, and let the algebra do the weighting for you.</p>
<p><b>Relevant topics:</b> specific heat capacity; thermal equilibrium; conservation of energy.</p>''',
    "trap": "Answering <code>110 &deg;C</code> by averaging the two temperatures. The final temperature is weighted by the heat capacities <code>mc</code>, and here the water's is four times the block's, so the answer sits far nearer 20 &deg;C.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 14 — K, nuclear.  How the energy of an alpha decay is shared.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 14, "id": "S01-14", "module": "K", "diff": 3,
    "topic": "Alpha decay: how the released energy is divided between the two products",
    "rel": [("K", "An alpha particle is a helium nucleus, mass number 4"),
            ("C", "Momentum is conserved, so the two products separate with equal and opposite momenta"),
            ("C", "For a fixed momentum, kinetic energy is inversely proportional to mass"),
            ("A", "Working with ratios so the actual masses are never needed")],
    "key": ["alphabeta", "momcons", "ke"],
    "stem": '<p>A nucleus of mass number <code>A</code> is at rest and decays by emitting an alpha particle. The total kinetic energy given to the two products is <code>E</code>. {{FIG:s01-14}}</p><p>What is the kinetic energy of the alpha particle?</p>',
    "opts": ["E(A - 4)/A", "4E/A", "4E/(A - 4)", "E/2", "E"],
    "ans": 0,
    "distractors": [
        "correct",
        "gives the alpha the share proportional to its own mass rather than to the recoil nucleus's mass",
        "inverts the ratio, so the alpha gets the larger share",
        "splits the energy equally, which would need the two masses to be equal",
        "gives the alpha all the energy, ignoring the recoil entirely",
    ],
    "profile": {
        "steps": [
            ("relate", "the nucleus starts at rest, so the two products must carry equal and opposite momenta"),
            ("relate", "kinetic energy is p squared over 2m, so with equal p the energies are inversely proportional to the masses"),
            ("relate", "the masses are in the ratio 4 to (A - 4), so the energies are in the ratio (A - 4) to 4"),
            ("eliminate", "the alpha therefore takes the fraction (A - 4)/A of the total"),
        ],
        "relations": ["0 = m_alpha v_alpha + M_recoil v_recoil", "KE = p^2 / 2m", "E_alpha / E_recoil = M_recoil / m_alpha"],
        "insight": "Equal and opposite momenta means the LIGHTER fragment carries the larger kinetic energy. The alpha particle gets almost all of it, and the exact fraction follows from the mass ratio without ever knowing the masses in kilograms.",
        "shape": "conservation",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "6*(6-4)/6", "want": "2"},
    "sol": '''<p><b>What is being tested.</b> Whether you realise that the energy released in a decay is <i>shared</i>, and whether you can work out the sharing from momentum conservation alone.</p>
<p><b>Step 1 — momentum.</b> The nucleus is at rest, so its momentum is zero. Momentum is conserved, so the two products must have equal and opposite momenta:</p>
<div class="formula">m_alpha v_alpha = M_recoil v_recoil</div>
<p><b>Step 2 — from momentum to energy.</b> Kinetic energy can be written in terms of momentum:</p>
<div class="formula">KE = p&sup2; / (2m)</div>
<p>Since <code>p</code> is the same for both products, the kinetic energies are <i>inversely</i> proportional to the masses:</p>
<div class="formula">KE_alpha / KE_recoil = M_recoil / m_alpha</div>
<p>The lighter particle moves faster and carries more of the energy. That is the physical content of the question.</p>
<p><b>Step 3 — put in the masses.</b> An alpha particle is a helium nucleus, mass number 4. The recoil nucleus keeps the remaining nucleons:</p>
<div class="formula">m_alpha &prop; 4        M_recoil &prop; A - 4</div>
<p>So the energies are in the ratio <code>(A - 4) : 4</code>. The alpha's share of the total is therefore</p>
<div class="formula">KE_alpha = E x (A - 4) / ((A - 4) + 4) = E (A - 4)/A</div>
<p><b>Step 4 — check the extremes.</b> For a very heavy nucleus, <code>A</code> is large and <code>(A-4)/A</code> is close to 1, so the alpha takes nearly all the energy and the heavy recoil takes almost none — which is right, since a heavy nucleus barely moves. This is why alpha energies measured in a detector are sharply defined even though the decay energy is shared: the sharing is nearly total and depends only on <code>A</code>.</p>
<p><b>Answer: A, E(A - 4)/A.</b></p>
<p><b>A numerical check.</b> Take <code>A = 6</code>, so the recoil has mass number 2, and let <code>E = 6</code> units. The formula gives <code>6 x 2/6 = 2</code>. Directly: the energies are in the ratio <code>2 : 4</code>, i.e. the alpha gets two thirds of nothing of the sort — rather, the alpha's share is <code>(A-4)/A = 2/6</code>, so <code>2</code> units. The two routes agree.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>4E/A</b> gives the alpha the share proportional to its own mass. That is the classic inversion, and it says the alpha carries the <i>smaller</i> part — the opposite of what equal momenta require.</p>
<p>· <b>4E/(A - 4)</b> inverts the ratio outright and is larger than <code>E</code> for any <code>A &lt; 8</code>, which is impossible.</p>
<p>· <b>E/2</b> would need the two fragments to have equal masses. An alpha particle has mass number 4, so that requires <code>A = 8</code> exactly.</p>
<p>· <b>E</b> ignores the recoil altogether, which would violate momentum conservation.</p>
<p><b>Relevant topics:</b> alpha decay; conservation of momentum; kinetic energy in terms of momentum; mass number.</p>''',
    "trap": "Giving the alpha particle the share proportional to its own mass. Equal and opposite momenta mean the LIGHTER fragment carries the larger kinetic energy, so the alpha takes <code>(A-4)/A</code>, not <code>4/A</code>.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 15 — A, toolkit.  Small change: stretching a wire and its resistance.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 15, "id": "S01-15", "module": "A", "diff": 3,
    "topic": "Small change: the resistance of a wire stretched at constant volume",
    "rel": [("A", "Approximating a small power: (1 + x) squared is about 1 + 2x"),
            ("H", "Resistance is resistivity times length over cross-sectional area"),
            ("A", "Holding a quantity constant to get a proportionality: here the volume")],
    "key": ["smallchange", "resistivity", "ratio"],
    "stem": '<p>A uniform wire of resistance <code>R</code> is stretched so that its length increases by a small fraction <code>x</code>. The volume of the wire does not change. {{FIG:s01-15}}</p><p>What is the fractional change in the resistance?</p>',
    "opts": ["x", "2x", "x/2", "4x", "0"],
    "ans": 1,
    "distractors": [
        "assumes the resistance follows the length directly, forgetting that the cross-section shrinks",
        "correct",
        "assumes the resistance follows the cross-section, halving the effect",
        "squares the factor of two, as though both length and area changed by a factor of two",
        "assumes the two effects cancel exactly, which would need the area to fall as fast as the length rises",
    ],
    "profile": {
        "steps": [
            ("relate", "resistance is resistivity times length over area"),
            ("relate", "constant volume means area times length is fixed, so the area is inversely proportional to the length"),
            ("eliminate", "substituting gives resistance proportional to the square of the length"),
            ("solve", "expand the square of (1 + x) and keep the leading term to get 2x"),
        ],
        "relations": ["R = rho L / A", "A L = constant", "R proportional to L^2", "(1+x)^2 ~ 1 + 2x"],
        "insight": "The wire gets longer AND thinner. Both changes push the resistance the same way, so the fractional change is twice what the length alone would suggest — 2x, not x.",
        "shape": "proportionality",
        "approx": True,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(1+0.01)**2", "want": "1.0201"},
    "sol": '''<p><b>What is being tested.</b> Whether you notice that stretching a wire changes <i>two</i> things at once. A candidate who only thinks about the length answers <code>x</code>; the cross-section has other ideas.</p>
<p><b>Step 1 — the resistance formula.</b></p>
<div class="formula">R = &rho; L / A</div>
<p>The resistivity <code>&rho;</code> is a property of the metal and does not change when the wire is stretched. So <code>R</code> depends on <code>L</code> and <code>A</code>, and both of those change.</p>
<p><b>Step 2 — what constant volume does.</b> The volume of the wire is its length times its cross-sectional area, and it is fixed:</p>
<div class="formula">L A = V = constant</div>
<p>So if the length grows, the area must shrink in proportion:</p>
<div class="formula">A = V / L,  so  A &prop; 1/L</div>
<p><b>Step 3 — eliminate the area.</b> Substituting into the resistance formula:</p>
<div class="formula">R = &rho; L / (V/L) = (&rho;/V) L&sup2;</div>
<p>So the resistance is proportional to the <i>square</i> of the length. This is the key step, and it is worth remembering as a fact in its own right: a wire stretched at constant volume has resistance proportional to <code>L&sup2;</code>.</p>
<p><b>Step 4 — apply the small change.</b> The new length is <code>L(1 + x)</code>, so the new resistance is</p>
<div class="formula">R' = R (1 + x)&sup2; = R (1 + 2x + x&sup2;)</div>
<p>Since <code>x</code> is small, <code>x&sup2;</code> is negligible beside <code>2x</code>, so</p>
<div class="formula">R' &asymp; R (1 + 2x),  giving  &Delta;R / R &asymp; 2x</div>
<p><b>Answer: B, 2x.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>x</b> uses the length alone, ignoring that the area has shrunk. Both effects increase the resistance, so the answer must be bigger than <code>x</code>.</p>
<p>· <b>x/2</b> treats the area change as reducing the effect. It does not: a thinner wire has more resistance.</p>
<p>· <b>4x</b> squares the factor of two, which happens if you write <code>(1+x)&sup2; &asymp; (1+2x)&sup2;</code> or otherwise double-count.</p>
<p>· <b>0</b> would require the two effects to cancel, i.e. the area to fall as fast as the length rises in the resistance formula. But the area enters as <code>1/A</code>, so a fractional fall in area gives the same fractional rise in resistance as the same fractional rise in length — they add, they do not cancel.</p>
<p><b>The wider point.</b> "Stretched at constant volume" and "stretched so the length doubles" are different statements, and the difference is the area. Whenever a wire is stretched, ask whether the volume is being held fixed; if it is, the resistance goes as the square of the length.</p>
<p><b>Relevant topics:</b> resistivity; small changes; binomial approximation; proportional reasoning.</p>''',
    "trap": "Answering <code>x</code> by treating the resistance as proportional to the length. The volume is constant, so the cross-section shrinks as the length grows, and <code>R &prop; L&sup2;</code> — the fractional change is <code>2x</code>.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 16 — B, kinematics.  Which velocity-time graph describes a bouncing ball?
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 16, "id": "S01-16", "module": "B", "diff": 1,
    "topic": "Choosing the velocity-time graph of a bouncing ball",
    "rel": [("B", "On a velocity-time graph the gradient is the acceleration, and it stays constant"),
            ("B", "A bounce reverses the velocity but not its magnitude if no energy is lost"),
            ("C", "Each bounce is lower, so the speed after each bounce is smaller")],
    "key": ["graphshape", "kinematics", "readdiagram"],
    "stem": '<p>A ball is released from rest and falls to the ground. It bounces, rises to a smaller height than it started from, and bounces again, each bounce being lower than the last. Air resistance is negligible. {{FIG:s01-16}}</p><p>Which graph shows the velocity <code>v</code> of the ball as a function of time <code>t</code>, taking downward as negative?</p>',
    "opts": [
        "A &mdash; v falls in a straight line to a negative maximum, then jumps back to the same positive value and the pattern repeats unchanged",
        "B &mdash; v falls ever more steeply, becoming negative and growing without limit",
        "C &mdash; v rises to a positive maximum, then falls back to zero once and stays there",
        "D &mdash; v falls in a straight line, jumps to a positive value, returns to zero, and every bounce reaches the same peak",
        "E &mdash; v falls in a straight line, jumps to a smaller positive value, returns to zero, and each bounce is smaller than the one before",
    ],
    "ans": 4,
    "distractors": [
        "keeps the speed constant while falling, and has the ball leave the floor at its arrival speed",
        "treats gravity as though it grew with time, so the slope steepens",
        "starts the ball moving upward, which it never does",
        "reverses the velocity but gives back all the speed at every bounce",
        "correct",
    ],
    "profile": {
        "steps": [
            ("read", "the slope of a velocity-time graph is the acceleration, and free-fall acceleration is constant"),
            ("relate", "so every falling and rising section must be a straight line of the same slope, not a curve"),
            ("relate", "at the bounce the velocity reverses in direction but its magnitude is reduced, because the ball does not reach the same height"),
            ("eliminate", "the peaks must therefore shrink from bounce to bounce"),
        ],
        "relations": ["v = u + a t", "slope of v-t graph = a", "h = v^2 / 2g so height goes as speed squared"],
        "insight": "Two independent facts pin the graph down: the slope is constant everywhere (gravity does not change), and the peak speed after each bounce is smaller (the ball does not come back to the same height). Curves are wrong for the first reason; equal peaks for the second.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "sqrt(0.20/0.80)", "want": "1/2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can read the physics off the <i>shape</i> of a graph. Two features decide it, and they are independent of each other.</p>
<p><b>Step 1 — what the slope means.</b> On a velocity-time graph the gradient is the acceleration. While the ball is in the air the only force on it is its weight, so its acceleration is <code>g</code> downward — the same value on the way up as on the way down, and the same at the top of the flight as anywhere else. In particular the acceleration is <b>not</b> zero at the highest point; only the velocity is.</p>
<p>So every section of the graph between bounces must be a <b>straight line</b>, and every one of those straight lines must have the <b>same</b> slope. A curve anywhere means a changing acceleration, which would need the force to change.</p>
<div class="formula">v = u + a t,  with a = -g throughout the flight</div>
<p><b>Step 2 — what happens at the bounce.</b> The ball hits the floor moving downward and leaves it moving upward, so the velocity reverses sign. The magnitude depends on how much energy the bounce returns: since the ball rises to a smaller height, the rebound speed is smaller.</p>
<p>Using <code>v&sup2; = 2gh</code>, a bounce to a quarter of the height returns half the speed:</p>
<div class="formula">v_rebound / v_arrival = &radic;(h_rebound / h_fall)</div>
<p>So each bounce gives a smaller jump, and the peak speed reached in each flight is smaller than the one before.</p>
<p><b>Step 3 — assemble the shape.</b> Starting from rest: a straight line of slope <code>-g</code> going negative; a jump up to a smaller positive value; a straight line of slope <code>-g</code> back down to zero at the top of the bounce; then the pattern repeats with smaller peaks.</p>
<p><b>Answer: E.</b> It is the only option with straight sections of constant slope <i>and</i> shrinking peaks.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>A</b> has the ball leave the floor at exactly the speed it arrived with. That is a perfectly elastic bounce, so it would rise to the same height — contradicting the question.</p>
<p>· <b>B</b> has the slope steepening, which would mean the acceleration grows as the ball falls. Gravity does not do that.</p>
<p>· <b>C</b> has the ball start off moving upward. It is released from rest, so its velocity starts at zero.</p>
<p>· <b>D</b> gets the shape right but gives every bounce the same peak speed, so the ball would rise to the same height each time.</p>
<p><b>The wider point.</b> A velocity-time graph answers two questions at once, and it is worth asking them separately. The <i>slope</i> tells you about force and acceleration; the <i>value</i> tells you about speed and direction. Most graph-choice questions are decided by one or the other, and the best ones by both.</p>
<p><b>Relevant topics:</b> velocity-time graphs; free fall; bounces and energy loss; interpreting gradients.</p>''',
    "trap": "Choosing the graph with equal peaks. The ball does not return to its starting height, so the speed after each bounce is smaller. Equally, any graph with a <i>curved</i> section is wrong: gravity gives a constant acceleration, so every straight section has the same slope.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 17 — C, forces.  The hanging mass that just moves a block up a slope.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 17, "id": "S01-17", "module": "C", "diff": 2,
    "topic": "Limiting friction: the hanging mass that just starts to move a block",
    "rel": [("C", "Resolving weight into components along and perpendicular to an inclined plane"),
            ("C", "The normal reaction sets the limiting friction through the coefficient"),
            ("C", "At the point of moving, the driving force exactly balances the resisting forces")],
    "key": ["force", "statics", "limits"],
    "stem": '<p>A block of mass 5.0 kg rests on a rough plane inclined at an angle whose sine is 0.60 and cosine is 0.80. The coefficient of friction between block and plane is 0.50. A light string runs from the block, up the slope and over a smooth pulley at the top, and hangs vertically with a mass <code>m</code> on the end. {{FIG:s01-17}}</p><p>Take <code>g = 10 N kg&#8315;&#185;</code>. What is the smallest <code>m</code> for which the block just starts to move up the slope?</p>',
    "opts": ["2.0 kg", "3.0 kg", "4.0 kg", "5.0 kg", "7.0 kg"],
    "ans": 3,
    "distractors": [
        "balances only the friction force and forgets the component of the block's weight along the slope",
        "balances only the component of the block's weight along the slope and forgets friction",
        "uses the normal reaction itself as the force to be balanced",
        "correct",
        "adds the friction force twice",
    ],
    "profile": {
        "steps": [
            ("relate", "resolve the block's weight along and perpendicular to the plane"),
            ("relate", "the perpendicular component is the normal reaction, and the limiting friction is mu times it"),
            ("relate", "just moving means the hanging weight balances the slope component AND the friction"),
            ("solve", "form the equation, cancel g, and solve for m"),
        ],
        "relations": ["W_parallel = mg sin(theta)", "N = mg cos(theta)", "F_friction = mu N", "T = W_parallel + F_friction"],
        "insight": "The hanging weight has to beat TWO things, not one: the component of the block's weight pulling it down the slope, and friction. Missing either gives one of the wrong options, and both are supplied by the numbers in the question.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(5*10*0.6+0.5*5*10*0.8)/10", "want": "5.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you include both resisting forces. The block is held back by its own weight sliding down the slope <i>and</i> by friction, and the hanging mass must overcome both.</p>
<p><b>Step 1 — resolve the block's weight.</b> The plane has sine 0.60 and cosine 0.80, which is the 3-4-5 triangle, so the arithmetic stays clean. The weight of the block is</p>
<div class="formula">W = 5.0 x 10 = 50 N</div>
<p>Resolving along and perpendicular to the plane:</p>
<div class="formula">W_parallel = 50 x 0.60 = 30 N   (down the slope)
W_perpendicular = 50 x 0.80 = 40 N   (into the plane)</div>
<p><b>Step 2 — the normal reaction and the limiting friction.</b> Perpendicular to the plane nothing is accelerating, so the normal reaction balances the perpendicular component:</p>
<div class="formula">N = 40 N</div>
<p>The limiting friction follows from the coefficient:</p>
<div class="formula">F = &mu; N = 0.50 x 40 = 20 N</div>
<p>Its direction opposes the motion that is about to start, so it acts <b>down</b> the slope, the same way as the weight component.</p>
<p><b>Step 3 — the condition for just moving.</b> The string's tension equals the hanging weight, <code>mg</code>. "Just starts to move" means the tension exactly balances the two forces resisting motion:</p>
<div class="formula">m g = W_parallel + F
10 m = 30 + 20 = 50</div>
<p><b>Step 4 — solve.</b></p>
<div class="formula">m = 5.0 kg</div>
<p><b>Answer: D, 5.0 kg.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>3.0 kg</b> balances only the weight component, giving <code>mg = 30</code>. Friction has been left out.</p>
<p>· <b>2.0 kg</b> balances only friction, giving <code>mg = 20</code>. The slope component has been left out.</p>
<p>· <b>4.0 kg</b> uses the normal reaction, 40 N, as the force to be balanced. The normal reaction acts into the plane, not along it, so it cannot be balanced by a pull along the plane at all — it is a coincidence of these numbers that it lands on a plausible value.</p>
<p>· <b>7.0 kg</b> adds friction twice, <code>mg = 30 + 20 + 20</code>.</p>
<p><b>The wider point.</b> Two checks make this kind of question safe. First, draw the free-body diagram and count the forces along the plane: there should be three (tension, weight component, friction). Second, ask which way friction points — it opposes impending motion, so if the block is about to move <i>up</i> the slope, friction acts <i>down</i> it. Getting that direction wrong turns a sum into a difference and produces a plausible but wrong answer.</p>
<p><b>Relevant topics:</b> forces on an inclined plane; limiting friction; resolving vectors; equilibrium conditions.</p>''',
    "trap": "Balancing only the component of the block's weight along the slope. Friction acts down the slope too, so the hanging mass must overcome <code>mg sin&theta; + &mu;mg cos&theta;</code>, not just the first term.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 18 — D, circular motion.  Apparent gravity on a rotating station.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 18, "id": "S01-18", "module": "D", "diff": 2,
    "topic": "Spinning a space station so the rim feels like the Earth's surface",
    "rel": [("D", "Circular motion: acceleration towards the centre is omega squared r"),
            ("D", "Apparent gravity is the centripetal acceleration the floor must supply"),
            ("A", "Converting between angular frequency and period")],
    "key": ["circular", "apparentweight", "ratio"],
    "stem": '<p>A cylindrical space station of radius 50 m spins about its axis. Take <code>g = 10 N kg&#8315;&#185;</code>.</p><p>What period of rotation would make the apparent gravity at the rim equal to <code>g</code>?</p>',
    "opts": ["1.4 s", "2.8 s", "14 s", "20 s", "31 s"],
    "ans": 2,
    "distractors": [
        "uses omega = g/r rather than its square root, giving an angular frequency ten times too large",
        "inverts the ratio, using 2 pi times the square root of g over r",
        "correct",
        "uses the diameter 100 m in place of the radius",
        "uses 2 pi r / g, omitting the square root altogether",
    ],
    "profile": {
        "steps": [
            ("relate", "the floor must supply the centripetal acceleration, so a = omega squared r"),
            ("relate", "set that equal to g to fix the required angular frequency"),
            ("solve", "rearrange for omega, then use T = 2 pi over omega"),
            ("solve", "evaluate, keeping the answer to two significant figures"),
        ],
        "relations": ["a = omega^2 r", "T = 2 pi / omega", "a = g for the rim"],
        "insight": "The quantity set by the design is the ACCELERATION, not the speed or the period. Once you have a = g you have omega, and the period is one more step.",
        "shape": "proportionality",
        "approx": True,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(2*pi/(2*pi*sqrt(5)))**2*50", "want": "10"},
    "sol": '''<p><b>What is being tested.</b> Whether you can go from an acceleration requirement to a period, through the angular frequency. Three quantities are involved and it is easy to lose track of which is which.</p>
<p><b>Step 1 — what "apparent gravity" means.</b> An astronaut standing on the inside of the rim is travelling in a circle. To stay in that circle they need a centripetal acceleration of <code>&omega;&sup2;r</code> directed towards the axis. What they feel as weight is the floor pushing them inward, which is exactly the force providing that acceleration. So the apparent gravity is the centripetal acceleration:</p>
<div class="formula">a = &omega;&sup2; r</div>
<p><b>Step 2 — impose the requirement.</b> We want <code>a = g</code> at the rim, where <code>r = 50 m</code>:</p>
<div class="formula">g = &omega;&sup2; r
10 = &omega;&sup2; x 50
&omega;&sup2; = 0.20</div>
<p><b>Step 3 — angular frequency to period.</b></p>
<div class="formula">&omega; = &radic;0.20 &asymp; 0.45 rad/s
T = 2&pi; / &omega; &asymp; 6.28 / 0.45 &asymp; 14 s</div>
<p>An equivalent route is <code>T = 2&pi;&radic;(r/g)</code>, which some people find easier to remember because it goes straight from the geometry to the period.</p>
<p><b>Answer: C, 14 s.</b></p>
<p><b>Check the answer physically.</b> A period of 14 s is about seven rotations a minute. That is slow enough to be comfortable and fast enough to be useful — which is roughly why proposals of this kind quote periods of this order. If your answer had been a fraction of a second the crew would be centrifuged; if it had been hours the "gravity" would be imperceptible.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>1.4 s</b> comes from <code>&omega; = g/r = 0.20</code> used directly as an angular frequency without taking the square root, which makes <code>&omega;</code> far too small and <code>T</code> far too short.</p>
<p>· <b>2.8 s</b> is <code>2&pi;&radic;(g/r)</code>, the ratio the wrong way up.</p>
<p>· <b>20 s</b> uses the diameter <code>100 m</code> instead of the radius. The centripetal acceleration uses the distance from the axis, which is the radius.</p>
<p>· <b>31 s</b> is <code>2&pi;r/g</code>, with the square root dropped. A units check catches it: <code>r/g</code> has units of s&sup2;, not s.</p>
<p><b>The wider point.</b> Notice that the mass of the astronaut never appeared, and neither did the mass of the station. Apparent gravity set by rotation is independent of mass, which is why a station of any size can be spun to give 1g at a chosen radius.</p>
<p><b>Relevant topics:</b> circular motion; centripetal acceleration; angular frequency and period; apparent weight.</p>''',
    "trap": "Solving <code>&omega; = g/r</code> and stopping. That gives <code>&omega;&sup2;</code>, not <code>&omega;</code>; the square root is easy to lose, and it changes the answer by a factor of about three.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 19 — E, materials.  Energy per unit volume from a stress-strain curve.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 19, "id": "S01-19", "module": "E", "diff": 2,
    "topic": "Strain energy per unit volume as the area under a stress-strain graph",
    "rel": [("E", "Strain energy per unit volume is the area under a stress-strain curve"),
            ("E", "In the linear region that area is half the product of stress and strain"),
            ("A", "Distinguishing an area under a graph from its gradient")],
    "key": ["strainenergy", "stressstrain", "graphshape"],
    "stem": '<p>The graph shows the stress-strain curve for a metal. The straight-line region ends at a stress of 3.0 &times; 10&#8312; Pa and a strain of 1.5 &times; 10&#8315;&sup3;. {{FIG:s01-19}}</p><p>What is the strain energy stored per unit volume at the end of the straight-line region?</p>',
    "opts": ["1.1 &times; 10&#8309; J m&#8315;&sup3;", "2.3 &times; 10&#8309; J m&#8315;&sup3;", "4.5 &times; 10&#8309; J m&#8315;&sup3;", "2.0 &times; 10&#185;&#185; J m&#8315;&sup3;", "4.5 &times; 10&sup2; J m&#8315;&sup3;"],
    "ans": 1,
    "distractors": [
        "halves the answer twice over, dividing by four instead of by two",
        "correct",
        "takes the full product of stress and strain, forgetting the factor of a half",
        "reports the gradient of the line, which is Young's modulus, instead of the area beneath it",
        "loses three powers of ten in the unit conversion",
    ],
    "profile": {
        "steps": [
            ("read", "energy per unit volume is the area under the stress-strain curve, not the gradient"),
            ("relate", "in the straight-line region that area is a triangle, so it is half the base times the height"),
            ("relate", "the base is the strain and the height is the stress"),
            ("solve", "compute half of stress times strain and check the order of magnitude"),
        ],
        "relations": ["energy per unit volume = area under stress-strain graph", "area = 0.5 * stress * strain", "Young's modulus = gradient"],
        "insight": "On this graph the gradient and the area are two different physical quantities with two different units: the gradient is Young's modulus in pascals, the area is energy density in joules per cubic metre. Deciding which the question wants is half the work.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "0.5*3.0e8*1.5e-3", "want": "225000"},
    "sol": '''<p><b>What is being tested.</b> Whether you know what the two features of a stress-strain graph mean. The gradient gives one quantity and the area gives another, and they are easy to confuse because both are read off the same curve.</p>
<p><b>Step 1 — which feature is wanted.</b> Work done on a sample per unit volume is force times distance per unit volume, which is stress times strain — an area under the curve, not a slope. So the answer is the area.</p>
<div class="formula">energy per unit volume = &int; &sigma; d&epsilon;</div>
<p><b>Step 2 — the shape of the region.</b> Up to the end of the straight-line region the graph is a straight line through the origin, so the area beneath it is a triangle:</p>
<div class="formula">area = 0.5 x base x height</div>
<p><b>Step 3 — identify base and height.</b> The horizontal axis is strain, so the base is the strain; the vertical axis is stress, so the height is the stress:</p>
<div class="formula">base = 1.5 x 10&#8315;&sup3;
height = 3.0 x 10&#8312; Pa</div>
<p><b>Step 4 — evaluate.</b></p>
<div class="formula">area = 0.5 x 3.0 x 10&#8312; x 1.5 x 10&#8315;&sup3;
     = 0.5 x 4.5 x 10&#8309;
     = 2.25 x 10&#8309; J m&#8315;&sup3;</div>
<p>To two significant figures this is <code>2.3 x 10&#8309; J m&#8315;&sup3;</code>.</p>
<p><b>Answer: B, 2.3 &times; 10&#8309; J m&#8315;&sup3;.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>4.5 &times; 10&#8309;</b> is the full product <code>&sigma;&epsilon;</code>, the factor of a half forgotten. That product is the area of the whole rectangle, not of the triangle under the line.</p>
<p>· <b>1.1 &times; 10&#8309;</b> divides by four instead of by two, halving twice.</p>
<p>· <b>2.0 &times; 10&#185;&#185;</b> is the gradient, <code>&sigma;/&epsilon; = 3.0&times;10&#8312; / 1.5&times;10&#8315;&sup3; = 2.0&times;10&#185;&#185; Pa</code>. That is Young's modulus, a perfectly sensible quantity that the question did not ask for. Its units give it away: pascals, not joules per cubic metre.</p>
<p>· <b>4.5 &times; 10&sup2;</b> has the right structure but the powers of ten are wrong by a factor of a million.</p>
<p><b>The wider point.</b> When a question gives you a graph, the first question to ask is whether it wants the gradient or the area, because the two answer different physics. Gradient of a displacement-time graph is velocity; area of a velocity-time graph is displacement. Gradient of a stress-strain graph is Young's modulus; area is energy density. Getting into that habit removes a whole class of errors.</p>
<p><b>Relevant topics:</b> stress and strain; Young's modulus; strain energy; interpreting graphs.</p>''',
    "trap": "Reporting the gradient. <code>&sigma;/&epsilon;</code> gives Young's modulus in pascals; the strain energy per unit volume is the <i>area</i> under the curve, in joules per cubic metre. The units tell you which one you have computed.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 20 — F, waves.  The highest order a grating can produce.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 20, "id": "S01-20", "module": "F", "diff": 2,
    "topic": "The highest diffracted order a grating can produce",
    "rel": [("F", "The grating equation relates the order, the wavelength and the spacing"),
            ("F", "The sine of an angle cannot exceed one, which caps the order"),
            ("A", "Turning a lines-per-length figure into a spacing, and rounding the right way")],
    "key": ["superposition", "waves", "limits"],
    "stem": '<p>Monochromatic light of wavelength 600 nm falls normally on a diffraction grating ruled with 500 lines per millimetre. {{FIG:s01-20}}</p><p>What is the highest order of diffracted beam that can be observed?</p>',
    "opts": ["3", "4", "6", "7", "12"],
    "ans": 0,
    "distractors": [
        "correct",
        "rounds 3.3 up to the nearest whole number instead of down",
        "counts the orders on both sides of the straight-through direction",
        "counts the zero order as well as both sides",
        "doubles the count of orders on both sides",
    ],
    "profile": {
        "steps": [
            ("relate", "convert the ruling density into a spacing in metres"),
            ("relate", "write the grating equation for the order n"),
            ("eliminate", "the sine of an angle cannot exceed one, so n is capped at d over lambda"),
            ("solve", "evaluate the cap and round DOWN to a whole number of orders"),
        ],
        "relations": ["d sin(theta) = n lambda", "sin(theta) <= 1", "d = 1 / (lines per metre)"],
        "insight": "The limit comes from geometry, not from the apparatus: no angle has a sine greater than one, so once n lambda exceeds the spacing there is simply nowhere for the beam to go.",
        "shape": "combinatorial",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "floor(1.0e-3/500/(600e-9))", "want": "3"},
    "sol": '''<p><b>What is being tested.</b> Whether you know what stops the orders, and whether you round the right way once you have found the limit.</p>
<p><b>Step 1 — the grating spacing.</b> The ruling density is given per millimetre, so convert to a spacing in metres:</p>
<div class="formula">d = 1 mm / 500 = 1.0 x 10&#8315;&sup3; m / 500 = 2.0 x 10&#8315;&#8310; m</div>
<p>Two micrometres between adjacent slits. It is worth converting the wavelength too, since mixing nanometres with millimetres is a standard way to be out by a factor of a million:</p>
<div class="formula">&lambda; = 600 nm = 6.0 x 10&#8315;&#8311; m</div>
<p><b>Step 2 — the grating equation.</b> A bright beam appears at angle <code>&theta;</code> when the path difference between neighbouring slits is a whole number of wavelengths:</p>
<div class="formula">d sin &theta; = n &lambda;</div>
<p><b>Step 3 — the cap on n.</b> Rearranged,</p>
<div class="formula">sin &theta; = n &lambda; / d</div>
<p>The left-hand side is a sine, and a sine cannot exceed one. So</p>
<div class="formula">n &lambda; / d &le; 1,  giving  n &le; d / &lambda;</div>
<p><b>Step 4 — evaluate and round the right way.</b></p>
<div class="formula">d / &lambda; = (2.0 x 10&#8315;&#8310;) / (6.0 x 10&#8315;&#8311;) = 3.3</div>
<p>So <code>n</code> can be 1, 2 or 3 but not 4 — the fourth order would need <code>sin &theta; = 4&lambda;/d = 4 x 0.30 = 1.20</code>, and a sine cannot reach that. The answer is therefore 3.</p>
<p><b>Answer: A, 3.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>4</b> rounds 3.3 to the nearest whole number. The inequality is <code>n &le; 3.3</code>, so 3.3 is a ceiling, not a target: the fourth order does not exist.</p>
<p>· <b>6</b> counts the three orders on each side of the straight-through direction. Those beams are real — but the question asks for the highest <i>order</i>, which is a label for a beam direction, not a count of beams.</p>
<p>· <b>7</b> adds the zero order to that count. The zero order is the undiffracted beam and is not usually counted as a diffracted order at all.</p>
<p>· <b>12</b> doubles the 6.</p>
<p><b>The wider point.</b> This is a "count the possibilities" question, and the counting is where most of the marks are lost. Two things to be careful about: convert every length to the same unit before dividing, and remember that a limit expressed as an inequality rounds down, not to the nearest.</p>
<p><b>Relevant topics:</b> diffraction gratings; the grating equation; orders of diffraction; limiting conditions.</p>''',
    "trap": "Rounding <code>d/&lambda; = 3.3</code> up to 4. The condition is an inequality — no sine exceeds 1 — so the answer is the largest whole number that satisfies it, which is 3.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 21 — G, optics.  The acceptance angle of an optical fibre.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 21, "id": "S01-21", "module": "G", "diff": 2,
    "topic": "The acceptance angle of a step-index optical fibre",
    "rel": [("G", "Total internal reflection at the core-cladding boundary sets a maximum angle inside the fibre"),
            ("G", "Snell's law at the end face converts that internal angle into an external one"),
            ("A", "Geometry: the angle at the wall and the angle to the axis are complementary")],
    "key": ["criticalangle", "snell", "refractive", "readdiagram"],
    "stem": '<p>A step-index optical fibre has a core of refractive index 1.5 and a cladding of refractive index 1.2. Light enters the flat end face from air. {{FIG:s01-21}}</p><p>What is the sine of the largest angle of incidence at the end face for which light is still guided along the fibre?</p>',
    "opts": ["0.45", "0.9", "0.8", "1.0", "1.2"],
    "ans": 1,
    "distractors": [
        "halves the correct value, as though only the core index mattered",
        "correct",
        "uses the ratio of the two refractive indices, which is the critical-angle sine rather than the acceptance sine",
        "assumes the ray is trapped whatever angle it enters at",
        "quotes the cladding refractive index itself as a sine",
    ],
    "profile": {
        "steps": [
            ("relate", "inside the fibre the ray must strike the wall at more than the critical angle, so sin(theta_c) = n2/n1"),
            ("relate", "the angle at the wall and the angle to the axis are complementary, so cos(angle to axis) = n2/n1"),
            ("relate", "Snell's law at the end face converts the angle inside into the angle outside"),
            ("eliminate", "combining the two gives sin(acceptance) = the square root of n1 squared minus n2 squared"),
            ("solve", "evaluate with n1 = 1.5 and n2 = 1.2"),
        ],
        "relations": ["sin(theta_c) = n2 / n1", "n_air sin(theta_a) = n1 sin(angle inside)", "sin(theta_a) = sqrt(n1^2 - n2^2)"],
        "insight": "There are two boundaries and they are easy to muddle. At the END face it is ordinary refraction; at the WALL it is total internal reflection. The link between them is that the ray's angle to the axis and its angle to the wall add to 90 degrees.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "sqrt(1.5**2-1.2**2)", "want": "0.9"},
    "sol": '''<p><b>What is being tested.</b> Whether you can handle two boundaries in one ray path, and whether you see the geometry that links them.</p>
<p><b>Step 1 — what traps the light.</b> Inside the fibre the ray bounces along the boundary between core and cladding. It stays in the core if it strikes that boundary at more than the critical angle, where</p>
<div class="formula">sin &theta;<sub>c</sub> = n&#8322; / n&#8321; = 1.2 / 1.5 = 0.8</div>
<p>So the ray must meet the wall at an angle of at least <code>&theta;<sub>c</sub></code> measured from the normal to the wall — and the normal to the wall is a radius, perpendicular to the axis.</p>
<p><b>Step 2 — the geometry.</b> Let the ray make an angle <code>&alpha;</code> with the fibre's axis. The angle it makes with the wall's normal is then <code>90&deg; - &alpha;</code>. The trapping condition is</p>
<div class="formula">90&deg; - &alpha; &ge; &theta;<sub>c</sub></div>
<p>so the steepest ray that survives has <code>90&deg; - &alpha; = &theta;<sub>c</sub></code>, i.e. <code>&alpha; = 90&deg; - &theta;<sub>c</sub></code>. Taking the sine:</p>
<div class="formula">sin &alpha; = sin(90&deg; - &theta;<sub>c</sub>) = cos &theta;<sub>c</sub></div>
<p><b>Step 3 — Snell's law at the end face.</b> Light comes from air (index 1) into the core (index <code>n&#8321;</code>), and the angle inside is <code>&alpha;</code>:</p>
<div class="formula">sin &theta;<sub>a</sub> = n&#8321; sin &alpha; = n&#8321; cos &theta;<sub>c</sub></div>
<p><b>Step 4 — eliminate the internal angle.</b> Since <code>sin &theta;<sub>c</sub> = n&#8322;/n&#8321;</code>,</p>
<div class="formula">cos &theta;<sub>c</sub> = &radic;(1 - (n&#8322;/n&#8321;)&sup2;) = &radic;(n&#8321;&sup2; - n&#8322;&sup2;) / n&#8321;</div>
<p>so</p>
<div class="formula">sin &theta;<sub>a</sub> = n&#8321; x &radic;(n&#8321;&sup2; - n&#8322;&sup2;) / n&#8321; = &radic;(n&#8321;&sup2; - n&#8322;&sup2;)</div>
<p>The refractive index of the core has cancelled, which is a good sign — the answer depends on the <i>difference</i> between the two indices. Now put the numbers in:</p>
<div class="formula">sin &theta;<sub>a</sub> = &radic;(1.5&sup2; - 1.2&sup2;) = &radic;(2.25 - 1.44) = &radic;0.81 = 0.9</div>
<p><b>Answer: B, 0.9.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>0.8</b> is <code>n&#8322;/n&#8321;</code>, the sine of the critical angle <i>inside</i> the fibre. It is an angle at the wall, not at the end face, and the two are different angles at different boundaries.</p>
<p>· <b>0.45</b> is half the correct value, as though only the core mattered and the cladding could be ignored.</p>
<p>· <b>1.0</b> would mean every ray entering the end face is guided, which would require the cladding to be absent altogether. With <code>n&#8322;</code> only slightly below <code>n&#8321;</code> the acceptance is indeed close to 1, but not equal to it.</p>
<p>· <b>1.2</b> quotes the cladding index as a sine. A sine of 1.2 does not exist, so the option is impossible on its face.</p>
<p><b>The wider point.</b> The quantity <code>&radic;(n&#8321;&sup2; - n&#8322;&sup2;)</code> is called the numerical aperture, and it is what optical engineers specify for a fibre, because it fixes how much light can be launched into it. Notice that a small difference between the two indices gives a small acceptance angle, which is why single-mode fibres are hard to couple light into.</p>
<p><b>Relevant topics:</b> total internal reflection; Snell's law; critical angle; optical fibres.</p>''',
    "trap": "Using <code>n&#8322;/n&#8321; = 0.8</code> as the answer. That is the sine of the critical angle at the core-cladding <i>wall</i>. The question asks for the acceptance angle at the <i>end face</i>, and converting between them needs the complementary-angle geometry and Snell's law.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 22 — H, circuits.  Heating water: an energy chain across two modules.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 22, "id": "S01-22", "module": "H", "diff": 2,
    "topic": "How long a kettle takes: electrical power meeting thermal capacity",
    "rel": [("H", "Electrical power is the rate of energy transfer"),
            ("J", "The energy needed to raise a mass by a temperature difference is mc dT"),
            ("A", "Linking two modules through the one quantity they share: energy")],
    "key": ["resistance", "specificheat", "nocalc"],
    "stem": '<p>An electric kettle is rated at 2.0 kW. It contains 1.5 kg of water at 20 &deg;C. The specific heat capacity of water is 4200 J kg&#8315;&#185; K&#8315;&#185;, and all the electrical energy goes into the water.</p><p>How long does the water take to reach 100 &deg;C?</p>',
    "opts": ["25 s", "126 s", "315 s", "504 s", "252 s"],
    "ans": 4,
    "distractors": [
        "uses a specific heat capacity of 420 J kg to the minus one K to the minus one, a factor of ten too small",
        "takes the kettle to be 4.0 kW, double its rating",
        "heats the water from 0 degrees rather than from 20, so uses a temperature rise of 100 K",
        "takes the kettle to be 1.0 kW, half its rating",
        "correct",
    ],
    "profile": {
        "steps": [
            ("relate", "the energy needed is mass times specific heat capacity times the temperature rise"),
            ("solve", "the temperature rise is from 20 to 100, which is 80 K, not 100 K"),
            ("relate", "the time is the energy divided by the power"),
            ("solve", "compute the energy, then divide by 2000 W"),
        ],
        "relations": ["Q = m c dT", "P = Q / t", "1 kW = 1000 W"],
        "insight": "The two modules are joined by a single quantity, energy: the kettle supplies it at a fixed rate, and the water absorbs it at a rate set by its heat capacity. The only subtlety is that the temperature RISE is 80 K, not 100 K.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1.5*4200*80/2000", "want": "252"},
    "sol": '''<p><b>What is being tested.</b> Whether you can chain two ideas together. Neither the electrical formula nor the thermal one is hard; the question is whether you connect them through energy.</p>
<p><b>Step 1 — how much energy the water needs.</b></p>
<div class="formula">Q = m c &Delta;T</div>
<p><b>Step 2 — get the temperature rise right.</b> This is where the marks are lost. The water starts at 20 &deg;C and finishes at 100 &deg;C, so the <i>rise</i> is</p>
<div class="formula">&Delta;T = 100 - 20 = 80 K</div>
<p>A temperature difference in kelvin has the same size as in degrees Celsius, so no conversion is needed — but the difference itself must be taken, not the final temperature. Substituting:</p>
<div class="formula">Q = 1.5 x 4200 x 80 = 504000 J</div>
<p><b>Step 3 — the rate at which energy is supplied.</b> A 2.0 kW kettle delivers energy at</p>
<div class="formula">P = 2.0 kW = 2000 W = 2000 J s&#8315;&#185;</div>
<p><b>Step 4 — divide.</b></p>
<div class="formula">t = Q / P = 504000 / 2000 = 252 s</div>
<p><b>Answer: E, 252 s.</b></p>
<p><b>Check it is sensible.</b> Four minutes to boil a litre and a half is exactly what a kettle does. Any answer of a few seconds or a few hours should be rejected on sight, which is a useful first pass before any arithmetic.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>315 s</b> uses <code>&Delta;T = 100 K</code>, heating the water from 0 &deg;C. It is the single most common error here.</p>
<p>· <b>126 s</b> takes the kettle to be 4.0 kW.</p>
<p>· <b>504 s</b> takes the kettle to be 1.0 kW, so the answer is exactly twice the correct one — a neat way to spot it.</p>
<p>· <b>25 s</b> uses a specific heat capacity of 420 rather than 4200.</p>
<p><b>The wider point.</b> Questions that cross modules are usually joined by an energy chain, and the chain is worth writing out explicitly: <i>electrical energy in = thermal energy absorbed</i>. Once that is written, both sides are routine. The same structure appears in a pump raising water, a motor lifting a load, and a heater warming a room.</p>
<p><b>Relevant topics:</b> electrical power; specific heat capacity; energy transfer; unit conversion.</p>''',
    "trap": "Using a temperature rise of 100 K. The water starts at 20 &deg;C, so the rise is 80 K; using 100 K inflates the answer by a quarter, which is exactly the difference between 252 s and 315 s.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 23 — I, capacitors.  Sharing charge between two capacitors.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 23, "id": "S01-23", "module": "I", "diff": 2,
    "topic": "A charged capacitor connected to an uncharged one: where the charge goes",
    "rel": [("I", "Charge stored is capacitance times potential difference"),
            ("I", "Capacitors in parallel add their capacitances"),
            ("C", "Charge is conserved when two isolated conductors are joined")],
    "key": ["capacitors", "charge", "seriesparallel"],
    "stem": '<p>A <code>2.0 &mu;F</code> capacitor is charged to 100 V and then disconnected from the supply. It is connected in parallel with an uncharged <code>3.0 &mu;F</code> capacitor.</p><p>What is the potential difference across the pair once the charge has settled?</p>',
    "opts": ["20 V", "50 V", "40 V", "60 V", "100 V"],
    "ans": 2,
    "distractors": [
        "divides the charge by 10 microfarads, adding a spurious third capacitance",
        "averages the two starting potentials, 100 V and 0 V",
        "correct",
        "takes the charge to be that which the second capacitor would hold at 100 V",
        "assumes no charge moves at all when the two are joined",
    ],
    "profile": {
        "steps": [
            ("relate", "find the charge initially stored on the charged capacitor"),
            ("relate", "charge is conserved: the total charge on the two plates is unchanged by connecting them"),
            ("relate", "in parallel the capacitances add, so the pair is a single capacitor of 5.0 microfarads"),
            ("solve", "divide the conserved charge by the combined capacitance"),
        ],
        "relations": ["Q = C V", "charge is conserved when the two are joined", "C_parallel = C1 + C2"],
        "insight": "The charge is fixed and the capacitance grows, so the potential difference must fall. Nothing else needs to be known — even without the arithmetic, the answer must lie between 0 and 100 V.",
        "shape": "conservation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "2e-6*100/(2e-6+3e-6)", "want": "40"},
    "sol": '''<p><b>What is being tested.</b> Whether you use the right conservation law. The charge on the disconnected plates cannot change; the potential difference can.</p>
<p><b>Step 1 — the charge before connecting.</b> The 2.0 &mu;F capacitor is charged to 100 V, so</p>
<div class="formula">Q = C&#8321; V&#8321; = 2.0 x 10&#8315;&#8310; x 100 = 200 &mu;C</div>
<p><b>Step 2 — what is conserved.</b> When the charged capacitor is disconnected from the supply and joined to the uncharged one, the two plates that are joined together form an isolated piece of conductor. No charge can leave it. So the total charge is still 200 &mu;C, now spread over both capacitors.</p>
<p><b>Step 3 — the combined capacitance.</b> In parallel the capacitances add, because each capacitor has the same potential difference across it and their charges simply add:</p>
<div class="formula">C = C&#8321; + C&#8322; = 2.0 + 3.0 = 5.0 &mu;F</div>
<p><b>Step 4 — the new potential difference.</b></p>
<div class="formula">V = Q / C = 200 &mu;C / 5.0 &mu;F = 40 V</div>
<p><b>Answer: C, 40 V.</b></p>
<p><b>Check the direction of the change.</b> The same charge now sits on a larger capacitance, so the potential difference must be <i>smaller</i> than 100 V. Any answer of 100 V or more is impossible, which removes one option immediately. And the answer must be more than zero, since charge did move. 40 V is the only option in range apart from 20 V and 50 V, and the arithmetic settles which.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>100 V</b> assumes no charge moves at all, which is what would happen if the second capacitor were not connected.</p>
<p>· <b>50 V</b> averages the two starting potentials. There is no reason for the answer to be an average of potentials; the weighting is by capacitance, and the correct weighting gives 40 V.</p>
<p>· <b>60 V</b> uses <code>C&#8322;V = 300 &mu;C</code> as the charge, i.e. the charge the <i>second</i> capacitor would hold at 100 V. The charge present is the one the first capacitor actually stored.</p>
<p>· <b>20 V</b> divides the 200 &mu;C by 10 &mu;F, adding a capacitance that is not there.</p>
<p><b>The wider point.</b> Notice that this question cannot be answered by conservation of energy: joining two capacitors in this way always loses energy (in the resistance of the connecting wire, as heat and radiation). Charge is conserved, energy is not — the mirror image of the bullet-and-block question earlier in this section, where momentum was conserved and energy was not. Knowing which quantity survives a given process is most of the physics.</p>
<p><b>Relevant topics:</b> capacitance; charge conservation; capacitors in parallel; energy dissipation.</p>''',
    "trap": "Averaging the potentials to get 50 V. Charge is conserved, not potential: 200 &mu;C spread over 5.0 &mu;F gives 40 V. Note also that energy is <i>not</i> conserved here — the joining always loses some.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 24 — J, thermal.  A bubble rising through a lake.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 24, "id": "S01-24", "module": "J", "diff": 3,
    "topic": "A bubble rising in a lake: pressure at depth against volume",
    "rel": [("J", "For a fixed mass of gas at constant temperature, pressure times volume is constant"),
            ("M", "Pressure at a depth in a liquid is the atmospheric pressure plus rho g h"),
            ("A", "Working with a ratio of pressures so the actual pressures need not be found")],
    "key": ["specificheat", "ratio", "nocalc"],
    "stem": '<p>A bubble of volume 1.0 cm&sup3; is released from the bottom of a lake 20 m deep. The atmospheric pressure at the surface is 1.0 &times; 10&#8309; Pa, the density of water is 1000 kg m&#8315;&sup3;, and <code>g = 10 N kg&#8315;&#185;</code>. The temperature is the same at the bottom and at the surface. {{FIG:s01-24}}</p><p>What is the volume of the bubble when it reaches the surface?</p>',
    "opts": ["3.0 cm&sup3;", "2.0 cm&sup3;", "4.0 cm&sup3;", "1.5 cm&sup3;", "1.0 cm&sup3;"],
    "ans": 0,
    "distractors": [
        "correct",
        "counts only the water pressure at the bottom and leaves the atmosphere out of the total",
        "adds the atmospheric pressure twice at the bottom",
        "takes the depth to be 5 m rather than 20 m",
        "assumes the pressure is the same at both ends, so the volume cannot change",
    ],
    "profile": {
        "steps": [
            ("relate", "the pressure at the bottom is the atmospheric pressure plus the pressure due to the water above"),
            ("solve", "evaluate rho g h for 20 m of water and add the atmosphere"),
            ("relate", "at constant temperature the pressure and volume are inversely proportional"),
            ("solve", "multiply the original volume by the ratio of the bottom pressure to the surface pressure"),
        ],
        "relations": ["p V = constant at fixed temperature", "p_bottom = p_atm + rho g h", "V2 = V1 p1 / p2"],
        "insight": "Two different physics sit on top of each other here: a hydrostatic pressure from module M and the gas law from module J. The bubble must expand by the ratio of the pressures, and that ratio is 3 because the water column adds twice the atmosphere.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "1.0*(1.0e5+1000*10*20)/1.0e5", "want": "3.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you include the atmosphere. The pressure at a depth is <i>not</i> just the water's contribution — it is the total pressure, and the atmosphere is part of it.</p>
<p><b>Step 1 — the pressure at the bottom.</b> The pressure at a depth <code>h</code> in a liquid is the pressure at the surface plus the weight of the liquid above:</p>
<div class="formula">p_bottom = p_atm + &rho; g h</div>
<p><b>Step 2 — evaluate the two parts.</b></p>
<div class="formula">&rho; g h = 1000 x 10 x 20 = 2.0 x 10&#8309; Pa
p_bottom = 1.0 x 10&#8309; + 2.0 x 10&#8309; = 3.0 x 10&#8309; Pa</div>
<p>So the pressure at the bottom is three atmospheres: one from the air and two from the 20 m of water. That "three" is the whole answer, and it is worth seeing it before doing any algebra.</p>
<p><b>Step 3 — the gas law at constant temperature.</b> The bubble contains a fixed mass of gas (it does not gain or lose air) at a fixed temperature, so</p>
<div class="formula">p&#8321; V&#8321; = p&#8322; V&#8322;</div>
<p>At the surface the pressure is the atmospheric pressure <code>1.0 x 10&#8309; Pa</code>.</p>
<p><b>Step 4 — solve for the new volume.</b></p>
<div class="formula">V&#8322; = V&#8321; x p&#8321; / p&#8322; = 1.0 x (3.0 x 10&#8309;) / (1.0 x 10&#8309;) = 3.0 cm&sup3;</div>
<p><b>Answer: A, 3.0 cm&sup3;.</b></p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>2.0 cm&sup3;</b> uses only the water's contribution, <code>2.0 x 10&#8309; Pa</code>, as the pressure at the bottom. The atmosphere is left out.</p>
<p>· <b>4.0 cm&sup3;</b> adds the atmosphere twice at the bottom, giving <code>4.0 x 10&#8309; Pa</code>.</p>
<p>· <b>1.5 cm&sup3;</b> would correspond to a depth of 5 m, where the water adds half an atmosphere.</p>
<p>· <b>1.0 cm&sup3;</b> leaves the volume unchanged, which would require the pressure to be the same at the bottom as at the surface. It is not — that is why the bubble grows as it rises.</p>
<p><b>A physical check.</b> Divers are taught never to hold their breath while ascending, and this calculation is why: a lungful of air at 20 m expands to three times its volume by the time it reaches the surface. The same physics, with the same factor of three.</p>
<p><b>Relevant topics:</b> pressure in a liquid; the gas laws at constant temperature; ratios; combining modules.</p>''',
    "trap": "Using only <code>&rho;gh</code> as the pressure at depth. The total pressure is <code>p<sub>atm</sub> + &rho;gh</code>; at 20 m the water contributes two atmospheres, so the bubble triples in volume, not doubles.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 25 — K, nuclear.  A fractional number of half-lives.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 25, "id": "S01-25", "module": "K", "diff": 2,
    "topic": "What survives one and a half half-lives",
    "rel": [("K", "After n half-lives the surviving fraction is one half to the power n"),
            ("A", "Fractional powers: a power of three halves is a power of one half then a square root"),
            ("A", "Rationalising a surd into the form the options use")],
    "key": ["expdecay", "surds", "ratio"],
    "stem": '<p>A radioactive source has half-life <code>T</code>.</p><p>What fraction of the original nuclei remain undecayed after a time <code>1.5T</code>?</p>',
    "opts": ["1/2", "1/4", "3/4", "1/(2&radic;2)", "1/8"],
    "ans": 3,
    "distractors": [
        "gives the fraction left after exactly one half-life",
        "gives the fraction left after two half-lives, rounding 1.5 up",
        "adds the one-half-life and two-half-life fractions instead of multiplying them",
        "correct",
        "gives the fraction left after three half-lives",
    ],
    "profile": {
        "steps": [
            ("relate", "after n half-lives the surviving fraction is one half raised to the power n"),
            ("solve", "put n = 1.5 and split the power into one half then a square root"),
            ("solve", "write the result as a single fraction with a rational denominator"),
            ("check", "compare with the one and two half-life values to see the answer lies between them"),
        ],
        "relations": ["N = N0 (1/2)^n", "(1/2)^(3/2) = (1/2) sqrt(1/2)", "1/(2 sqrt 2) = sqrt(2)/4"],
        "insight": "A fractional number of half-lives is not a problem: the law is exponential, so any power works. The only work is turning 1.5 into a half and a square root.",
        "shape": "algebraic-elimination",
        "approx": True,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "sqrt(2)/4", "want": "1/(2*sqrt(2))"},
    "sol": '''<p><b>What is being tested.</b> Whether you are comfortable with a fractional number of half-lives, and whether you can tell "remaining" from "decayed".</p>
<p><b>Step 1 — the decay law.</b> After a time equal to <code>n</code> half-lives, the surviving fraction is</p>
<div class="formula">N / N&#8320; = (1/2)<sup>n</sup></div>
<p>This is just the statement that the quantity halves every time <code>T</code> passes. It is defined for any <code>n</code>, whole or not, because it is an exponential law.</p>
<p><b>Step 2 — put in n = 1.5.</b> Split the power into a half and a square root, since <code>1.5 = 1 + 1/2</code>:</p>
<div class="formula">(1/2)<sup>3/2</sup> = (1/2)<sup>1</sup> x (1/2)<sup>1/2</sup> = (1/2) x 1/&radic;2 = 1 / (2&radic;2)</div>
<p><b>Step 3 — tidy the form.</b> Rationalising the denominator gives an equivalent expression:</p>
<div class="formula">1 / (2&radic;2) = &radic;2 / (2 x 2) = &radic;2 / 4 &asymp; 0.35</div>
<p>So about 35 per cent of the original nuclei remain.</p>
<p><b>Answer: D, 1/(2&radic;2).</b></p>
<p><b>Check it against the whole-number cases.</b> After one half-life, half remains — 0.5. After two, a quarter remains — 0.25. The answer for 1.5 half-lives must lie between those, and <code>0.35</code> does. Any option outside the range <code>0.25</code> to <code>0.5</code> is impossible without any algebra at all, which removes three of the five options immediately.</p>
<p><b>Why the other four are wrong.</b></p>
<p>· <b>1/2</b> is the fraction left after one half-life, i.e. after a shorter time than the question asks about.</p>
<p>· <b>1/4</b> is the fraction left after two half-lives. It rounds 1.5 up to 2, which is not allowed: the decay does not wait for a whole half-life to pass before doing anything.</p>
<p>· <b>3/4</b> adds the one-half-life and two-half-life fractions: <code>1/2 + 1/4 = 3/4</code>. Successive halvings <i>multiply</i>, they do not add. It is also worth noticing that <code>3/4</code> would mean three quarters of the nuclei are still there after the source has halved twice over, which cannot be right.</p>
<p>· <b>1/8</b> is the fraction left after three half-lives, double the time asked about.</p>
<p><b>The wider point.</b> Radioactive decay questions almost always have a quick range check available: the answer must lie between the values for the whole numbers of half-lives either side. Use that first, then do the algebra only on the options that survive.</p>
<p><b>Relevant topics:</b> half-life; exponential decay; fractional powers; surds.</p>''',
    "trap": "Adding the halvings instead of multiplying them, giving <code>1/2 + 1/4 = 3/4</code>. After one and a half half-lives about <code>0.35</code> of the nuclei remain, so any answer above <code>1/2</code> is impossible.",
},

]
