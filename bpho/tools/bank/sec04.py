# -*- coding: utf-8 -*-
"""BPhO Round 0 -- BANK SECTION 04 (S04-01 .. S04-25).

Twenty-five original questions in the exact Round 0 format: single-answer MCQ, five
options, no calculator, one mark each, no negative marking.  They are NOT taken from any
competition paper -- BPhO's papers and other competitions' papers are copyrighted.  What
is borrowed is the style and the difficulty, and `spec.STYLE` records which competitions
set questions of comparable demand inside the R0 scope.

The module mix is the plan's mix for this section, so it is a valid full-length mock:
A3 B2 C3 D2 E1 F2 G2 H4 I1 J1 K2 L2.

Twelve of the twenty-five carry a hand-drawn figure -- the real paper carries eight.  Each
figure encodes the discriminator the question turns on rather than decorating the
apparatus: the voltmeter is drawn across the external resistor so the reading is visibly
the terminal p.d.; the ladder figure marks the HORIZONTAL moment arm of a vertical force;
the loop figure states in words that both forces act downward at the top; the fibre figure
marks the angle at the side wall as 90 - r; the graph figure draws its gradient triangle
ON the line.

Where a figure is present the profile says `figure_essential` -- meaning the question
cannot be answered from the prose alone -- or `figure_support`, meaning it repeats data
that the stem also states.  Nothing in between.

Same field contract as sec01.py -- see that file's docstring for `distractors`, `profile`
and `check`.

Figures are hand-authored inline SVG in fig/, referenced as {{FIG:key}}.
"""

SECTION = 4

QUESTIONS = [

# ═════════════════════════════════════════════════════════════════════════════
# 1 -- H, circuits.  A cell with internal resistance: the terminal p.d. moves.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 1, "id": "S04-01", "module": "H", "diff": 3,
    "topic": "A cell with internal resistance: how the terminal p.d. changes with the load",
    "rel": [("H", "The terminal potential difference is the emf minus the volts lost across the internal resistance"),
            ("H", "Ohm's law applied to the whole circuit, internal resistance included"),
            ("A", "Using a reading taken in one arrangement to find a quantity the second arrangement needs")],
    "key": ["emf", "internal", "terminal", "load"],
    "stem": '<p>The figure shows a cell of emf 6.0 V whose internal resistance <code>r</code> is inside the cell, connected in series with a 12 &#937; resistor. The voltmeter is connected across the 12 &#937; resistor and reads 4.8 V. {{FIG:s04-01}}</p><p>The 12 &#937; resistor is now replaced by a 6.0 &#937; resistor. What does the voltmeter read?</p>',
    "opts": ['2.4 V', '3.0 V', '4.0 V', '4.8 V', '6.0 V'],
    "ans": 2,
    "distractors": ['assumes the reading falls in proportion to the external resistance, 4.8 &#215; 6.0/12, which is what would happen if the internal resistance were zero',
                    'assumes the two resistances share the emf equally, which would be right only if the internal resistance were also 6.0 &#937;',
                    'correct',
                    'assumes the reading does not change when the external resistor is changed',
                    'takes the emf itself as the reading, dropping the internal resistance out of the current'],
    "profile": {
        "steps": [
            ("relate", "read the current off the first arrangement, since the voltmeter is across a known resistor"),
            ("relate", "the volts missing from the emf are the volts lost across r"),
            ("solve", "divide the lost volts by the current to get r"),
            ("solve", "put r back into the second arrangement and find the new current"),
            ("check", "multiply the new current by the new resistance to get the reading, and confirm it fell"),
        ],
        "relations": ["V = I R", "E = V + I r", "I = E / (R + r)", "r = (E - V) / I"],
        "insight": "The voltmeter is across the external resistor, so 4.8 V is the terminal p.d. and not the emf. The 1.2 V that is missing has gone across r, and that missing volt is what fixes r.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "6.0*6.0/(6.0 + (6.0 - 4.8)*12/4.8)", "want": "4.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you know what a voltmeter across the external resistor actually measures. It does not read the emf, and treating it as the emf makes this question impossible.</p>
<p><b>Step 1 — read the current off the first arrangement.</b> The voltmeter is across the 12 &#937; resistor, and the p.d. across it is 4.8 V. Ohm's law gives the current through it, and because the circuit is a single loop that is also the current through the cell:</p>
<div class="formula">I = V / R = 4.8 / 12 = 0.40 A</div>
<p><b>Step 2 — find the volts that went missing.</b> The cell's emf is 6.0 V. The external resistor only gets 4.8 V of it, so the rest was dropped inside the cell across <code>r</code>:</p>
<div class="formula">lost volts = E &#8722; V = 6.0 &#8722; 4.8 = 1.2 V</div>
<p><b>Step 3 — divide to get the internal resistance.</b> The same current flows through <code>r</code>, so</p>
<div class="formula">r = lost volts / I = 1.2 / 0.40 = 3.0 &#937;</div>
<p><b>Step 4 — the new circuit.</b> With a 6.0 &#937; resistor the total resistance in the loop is the external resistor plus the internal one:</p>
<div class="formula">R total = 6.0 + 3.0 = 9.0 &#937;
I = E / R total = 6.0 / 9.0 = 2/3 A</div>
<p><b>Step 5 — the new reading.</b> The voltmeter is still across the external resistor:</p>
<div class="formula">V = I R = (2/3) &#215; 6.0 = 4.0 V</div>
<p>So <b>Answer: C.</b></p>
<p><b>Why it fell, and by how much.</b> Lowering the external resistance raises the current, which raises the volts lost inside the cell, so the terminal p.d. must fall. It fell from 4.8 V to 4.0 V, a drop of 0.8 V, while the lost volts rose from 1.2 V to 2.0 V. The two changes are equal and opposite, which is what has to happen because the emf is fixed: whatever the terminal p.d. gives up, the internal resistance takes. That is a useful check on any answer to a question of this shape.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2.4 V</b> comes from scaling the reading with the resistance, 4.8 &#215; 6.0/12. That is the behaviour of a fixed potential divider, not of a cell. With <code>r</code> in the circuit the current rises as the resistance falls, so the reading falls by less than the proportion.</p>
<p>&middot; <b>3.0 V</b> comes from assuming the two resistances split the emf equally. They would do that only if <code>r</code> were also 6.0 &#937;. Here <code>r</code> is 3.0 &#937;, so the external resistor takes two thirds of the emf and the reading is 4.0 V.</p>
<p>&middot; <b>4.8 V</b> is the reading before the change. It is the answer you get by assuming the terminal p.d. depends only on the cell, which is the misconception the whole question is aimed at: the terminal p.d. is a property of the cell <i>and</i> the load together.</p>
<p>&middot; <b>6.0 V</b> is the emf, and it is what you get if the internal resistance is left out of the denominator, <code>I = 6.0/6.0 = 1.0 A</code> and then <code>V = 6.0 V</code>. A cell only delivers its full emf to the outside when no current flows at all, which is exactly the open-circuit condition a voltmeter with infinite resistance would create.</p>
<p><b>The trap.</b> Treating 4.8 V as the emf. Once that is done the arithmetic still runs and still produces a number, so nothing feels wrong — but <code>r</code> comes out as 1.2/0.4 with 6.0 substituted somewhere, and the second part is built on a false first part.</p>
<p><b>Relevant topics:</b> emf and internal resistance; terminal potential difference; lost volts; the current in a single loop; why a car battery's terminal p.d. falls when the starter motor draws current.</p>''',
    "trap": "Reading 4.8 V as the emf. It is the terminal p.d.; the emf is 6.0 V, and the difference is the volts lost across the internal resistance.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 2 -- A, toolkit.  Dimensional analysis: which combination gives a time.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 2, "id": "S04-02", "module": "A", "diff": 2,
    "topic": "Dimensional analysis: finding the combination of G, M and r that has the dimensions of a time",
    "rel": [("A", "Matching the dimensions of a combination to those of the quantity wanted"),
            ("A", "The dimensions of G, read off its units N m<sup>2</sup> kg<sup>-2</sup>"),
            ("D", "The period of a body in a circular orbit about a much heavier body")],
    "key": ["dimensions", "orbit", "period", "combination"],
    "stem": '<p>A satellite moves in a circular orbit of radius <code>r</code> about a planet of mass <code>M</code>. The only quantities available to describe the motion are <code>r</code>, <code>M</code>, and the gravitational constant <code>G</code>, whose units are N m<sup>2</sup> kg<sup>-2</sup>.</p><p>Which of the following has the dimensions of a time?</p>',
    "opts": ['2&#960;&#8730;(r<sup>3</sup>/GM)',
             '2&#960;&#8730;(GM/r)',
             '2&#960;&#8730;(GM/r<sup>3</sup>)',
             '2&#960; r<sup>3</sup>/(GM)',
             '2&#960; GM/r<sup>2</sup>'],
    "ans": 0,
    "distractors": ['correct',
                    'puts r in the denominator under the root, which leaves the dimensions of a speed',
                    'raises r to the wrong power, which leaves the dimensions of a frequency rather than a period',
                    'leaves the square root out, so the combination has the dimensions of a time squared',
                    'divides by r squared, which gives the dimensions of an acceleration -- the gravitational field strength'],
    "profile": {
        "steps": [
            ("relate", "write G's units in base units, so that the mass in it can be seen to cancel M"),
            ("solve", "form GM and note that the kilogram cancels, leaving m<sup>3</sup> s<sup>-2</sup>"),
            ("check", "divide r cubed by GM to leave a time squared, and take the root to leave a time"),
        ],
        "relations": ["[G] = N m<sup>2</sup> kg<sup>-2</sup> = m<sup>3</sup> s<sup>-2</sup> kg<sup>-1</sup>",
                      "[GM] = m<sup>3</sup> s<sup>-2</sup>",
                      "[r<sup>3</sup>/GM] = s<sup>2</sup>"],
        "insight": "The mass of the planet enters only through the product GM, and G carries a kilogram to the minus one. The two cancel, so GM is a pure length cubed over time squared and the rest is bookkeeping.",
        "shape": "dimensional-analysis",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "dim", "got": "m^3 m^-3 s^2", "want": "s^2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can use dimensions as a working tool rather than as a checklist. Here the dimensions alone pick out exactly one of the five options, with no physics beyond the units of <code>G</code>.</p>
<p><b>Step 1 — put G into base units.</b> <code>G</code> is defined through <code>F = GMm/r<sup>2</sup></code>, so its units can be read straight off that equation. One newton is a kilogram metre per second squared:</p>
<div class="formula">G = N m<sup>2</sup> kg<sup>-2</sup>
  = (kg m s<sup>-2</sup>)(m<sup>2</sup>)(kg<sup>-2</sup>)
  = m<sup>3</sup> s<sup>-2</sup> kg<sup>-1</sup></div>
<p><b>Step 2 — form the product GM.</b> Multiplying by <code>M</code>, which is a mass, cancels the kilogram exactly:</p>
<div class="formula">GM = (m<sup>3</sup> s<sup>-2</sup> kg<sup>-1</sup>)(kg)
   = m<sup>3</sup> s<sup>-2</sup></div>
<p>That is worth pausing on. <code>GM</code> has nothing to do with mass as far as dimensions go; it is a volume per second squared. Physically that is why the orbit of a satellite does not depend on the satellite's own mass.</p>
<p><b>Step 3 — divide by r cubed and take the root.</b> Both <code>r<sup>3</sup></code> and <code>GM</code> are lengths cubed, so the lengths cancel and only the time survives:</p>
<div class="formula">r<sup>3</sup> / GM = m<sup>3</sup> / (m<sup>3</sup> s<sup>-2</sup>) = s<sup>2</sup>
&#8730;(r<sup>3</sup>/GM) = s</div>
<p>So the combination under the square root is a time squared, and its square root is a time. The factor <code>2&#960;</code> is a pure number and carries no dimensions, so it changes nothing.</p>
<p>So <b>Answer: A.</b></p>
<p><b>Checking the answer against the physics.</b> For a circular orbit the gravitational force supplies the centripetal force, <code>GMm/r<sup>2</sup> = m&#969;<sup>2</sup>r</code>, which rearranges to <code>&#969;<sup>2</sup> = GM/r<sup>3</sup></code> and therefore <code>T = 2&#960;&#8730;(r<sup>3</sup>/GM)</code>. The dimensional argument and the dynamical argument land on the same combination, which is not a coincidence: dimensional analysis cannot supply the <code>2&#960;</code>, but it never gets the powers of <code>r</code> wrong.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2&#960;&#8730;(GM/r)</b> divides by one power of r instead of three. <code>GM/r</code> is m<sup>2</sup> s<sup>-2</sup>, whose square root is a speed, not a time.</p>
<p>&middot; <b>2&#960;&#8730;(GM/r<sup>3</sup>)</b> divides by r cubed the other way round. <code>GM/r<sup>3</sup></code> is s<sup>-2</sup>, whose square root is a frequency. It is the reciprocal of the right answer, which is the single easiest way to get this wrong: the answer is a period, so it must grow as <code>r</code> grows, and this one shrinks.</p>
<p>&middot; <b>2&#960; r<sup>3</sup>/(GM)</b> is the combination without the square root. It has the dimensions of a time squared, so it fails on units alone.</p>
<p>&middot; <b>2&#960; GM/r<sup>2</sup></b> is m s<sup>-2</sup>. That is an acceleration, and it is in fact what <code>GM/r<sup>2</sup></code> means physically -- the gravitational field strength at the orbit. Correct physics, wrong quantity.</p>
<p><b>The trap.</b> Trying to remember the formula for the orbital period instead of deriving the dimensions. The formula is easy to misremember by a power of <code>r</code>; the dimensions are not, and they cost three lines.</p>
<p><b>Relevant topics:</b> dimensional analysis as a method; base and derived units; the dimensions of G; Kepler's third law; circular orbits.</p>''',
    "trap": "Recalling the orbital-period formula from memory and misplacing a power of r. The dimensions of G settle the powers without any formula at all.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 3 -- C, forces.  A ladder on a smooth wall: the friction needed at the foot.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 3, "id": "S04-03", "module": "C", "diff": 3,
    "topic": "A uniform ladder against a smooth wall: the smallest coefficient of friction at the foot",
    "rel": [("C", "Taking moments about the foot so that two of the three unknown forces drop out"),
            ("C", "The weight of a uniform body acting at its midpoint"),
            ("A", "The moment arm of a force is the perpendicular distance from the pivot, which for a vertical force is horizontal")],
    "key": ["ladder", "moments", "friction", "wall"],
    "stem": '<p>The figure shows a uniform ladder of weight <code>W</code> and length <code>L</code> resting with its foot on rough horizontal ground and its top against a smooth vertical wall. The ladder makes an angle of <code>30&#176;</code> with the ground. {{FIG:s04-03}}</p><p>The wall exerts only a horizontal reaction. Which expression gives the smallest coefficient of friction between the foot and the ground that can hold the ladder in equilibrium?</p>',
    "opts": ['1/2', '&#8730;3/2', '&#8730;3', '1/&#8730;3', '2/&#8730;3'],
    "ans": 1,
    "distractors": ['measures both moment arms with the same trigonometric function, which cancels the angle and leaves a constant',
                    'correct',
                    'loses the factor of a half by taking the weight to act at the top of the ladder instead of at its centre',
                    'inverts the ratio, putting the tangent on top, which would make a steeper ladder need more friction',
                    'doubles instead of halving, treating the weight\'s moment arm as the whole length of the ladder'],
    "profile": {
        "steps": [
            ("relate", "note that a smooth wall can only push horizontally, so its reaction has no vertical component"),
            ("relate", "resolve vertically, which gives the normal reaction from the ground at once"),
            ("relate", "resolve horizontally, which gives the friction needed in terms of the wall's reaction"),
            ("relate", "take moments about the foot, where both the normal reaction and the friction have no moment"),
            ("solve", "solve the moment equation for the wall's reaction in terms of W and the angle"),
            ("check", "divide the friction needed by the normal reaction, and put the angle in"),
        ],
        "relations": ["N = W", "F = R", "R L sin&#952; = W (L/2) cos&#952;", "&#956; = F / N = 1 / (2 tan&#952;)"],
        "insight": "Taking moments about the foot is what makes this short: the normal reaction and the friction both act there, so neither appears. The one thing that must not be got wrong is that a vertical force's moment arm is the HORIZONTAL distance.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "1/(2*tan(pi/6))", "want": "sqrt(3)/2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can set up a statics problem by choosing the pivot that kills the most unknowns, and whether you know that a smooth wall pushes only sideways.</p>
<p><b>Step 1 — what each surface can do.</b> The wall is smooth, so it can exert no friction; its reaction <code>R</code> is horizontal, pushing the ladder away from the wall. The ground is rough, so it exerts both a vertical normal reaction <code>N</code> and a horizontal friction <code>F</code>. The ladder's weight <code>W</code> acts at its midpoint, because the ladder is uniform.</p>
<p><b>Step 2 — resolve vertically.</b> The only vertical forces are <code>N</code> and <code>W</code>, and the wall contributes nothing vertically:</p>
<div class="formula">N = W</div>
<p><b>Step 3 — resolve horizontally.</b> The only horizontal forces are <code>R</code> and <code>F</code>, and they must cancel:</p>
<div class="formula">F = R</div>
<p><b>Step 4 — take moments about the foot.</b> This is the step that makes the problem short. Both <code>N</code> and <code>F</code> act at the foot, so neither has a moment about it, and only two forces are left. The wall's reaction acts at the top of the ladder, a perpendicular distance <code>L sin&#952;</code> from the foot. The weight acts at the midpoint; its moment arm is the perpendicular distance from the foot to the line of action of a vertical force, which is the <i>horizontal</i> distance to the midpoint, <code>(L/2) cos&#952;</code>:</p>
<div class="formula">R &#215; L sin&#952; = W &#215; (L/2) cos&#952;</div>
<p><b>Step 5 — solve for the wall's reaction.</b> The length <code>L</code> cancels, which is a good sign: the answer should not depend on how long the ladder is.</p>
<div class="formula">R = W cos&#952; / (2 sin&#952;) = W / (2 tan&#952;)</div>
<p><b>Step 6 — the friction needed.</b> Since <code>F = R</code> and <code>N = W</code>, the smallest coefficient of friction that can supply it is</p>
<div class="formula">&#956; = F / N = (W / (2 tan&#952;)) / W = 1 / (2 tan&#952;)</div>
<p>At <code>&#952; = 30&#176;</code>, <code>tan&#952; = 1/&#8730;3</code>, so</p>
<div class="formula">&#956; = 1 / (2/&#8730;3) = &#8730;3/2</div>
<p>So <b>Answer: B.</b></p>
<p><b>Does the answer make sense?</b> Three limits are worth checking, because a formula this short can still be wrong in an obvious way. As the ladder stands up, <code>&#952; &#8594; 90&#176;</code>, the tangent grows without limit and <code>&#956; &#8594; 0</code>: a vertical ladder needs no friction at all, which is right, because there is nothing pushing its foot sideways. As the ladder is laid flatter, <code>&#952; &#8594; 0</code>, the friction needed grows without limit, which is also right: a nearly horizontal ladder would slide away unless the ground gripped very hard. And the answer does not contain <code>W</code> or <code>L</code>, so a heavy ladder and a light one need the same grip, and so do a short ladder and a long one. That is a genuinely surprising result and it is the sort of thing this question is testing.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/2</b> is what you get by measuring both moment arms with the same function. If the weight's arm is taken as <code>(L/2) cos&#952;</code> and the wall's as <code>L cos&#952;</code>, the cosines cancel and the angle disappears from the answer. The wall's arm is <code>L sin&#952;</code> because the wall's force is horizontal, and a horizontal force at the top of a ladder tilted at <code>&#952;</code> has its perpendicular distance from the foot measured <i>vertically</i>.</p>
<p>&middot; <b>&#8730;3</b> is <code>1/tan&#952;</code>: the correct expression with the factor of a half dropped. That half is the whole reason the midpoint matters. It comes from the weight acting at the centre, so its arm is half the ladder's.</p>
<p>&middot; <b>1/&#8730;3</b> is <code>tan&#952;</code>, the reciprocal of the correct answer. It would make a steeper ladder need <i>more</i> friction, which contradicts the limit checked above.</p>
<p>&middot; <b>2/&#8730;3</b> doubles instead of halving, which is what happens if the weight is taken to act at the top of the ladder. A uniform ladder's weight acts at its centre; only a ladder with all its mass at one end would behave that way.</p>
<p><b>The trap.</b> Drawing the weight's moment arm along the ladder instead of horizontally. A vertical force's moment arm about a point is the horizontal distance to its line of action, and the dashed right angle in the figure is there to make that unmistakable.</p>
<p><b>Relevant topics:</b> the principle of moments; choosing a pivot to eliminate unknowns; resolution of forces; limiting friction and the coefficient of friction.</p>''',
    "trap": "Measuring the weight's moment arm along the ladder rather than horizontally. A vertical force has a horizontal moment arm, and that is where the cosine comes from.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 4 -- H, circuits.  A five-resistor network: reduce it from the inside out.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 4, "id": "S04-04", "module": "H", "diff": 3,
    "topic": "A five-resistor network: reducing from the inside out, and why two parallel branches never share the current equally",
    "rel": [("H", "Resistors in series add, and resistors in parallel combine as the reciprocal of the sum of the reciprocals"),
            ("H", "Two parallel branches carry equal currents only when their resistances are equal; otherwise the smaller resistance takes the larger share"),
            ("H", "A potential divider: the p.d. across one section is the supply p.d. in the ratio of that section's resistance to the total"),
            ("A", "Reducing a network in stages, from the inside out, rather than trying to see the whole answer at once")],
    "key": ["network", "parallel", "currentdivision", "stagedreduction"],
    "stem": '<p>The figure shows a 12 V battery of negligible internal resistance driving a network of five resistors whose values are marked on it. R1 = 4.0 &#937; is in series with everything else. The rest of the network is R2 = 6.0 &#937; in parallel with a branch that carries R3 = 8.0 &#937; in series with the pair R4 = 12 &#937; and R5 = 6.0 &#937;. {{FIG:s04-04}}</p><p>What is the current in R4?</p>',
    "opts": ['1/6 A', '1/2 A', '1/3 A', '1/4 A', '1/12 A'],
    "ans": 0,
    "distractors": ['correct',
                    'stops at the branch current, treating the whole of the R3 branch current as the current in R4',
                    'quotes the current in the partner R5, which has the same p.d. across it but only half the resistance',
                    'assumes the two parallel branches share the total current equally, so the R3 branch is given 0.75 A instead of 0.50 A',
                    'applies the full 12 V of the battery directly across R4, ignoring every resistor in front of it'],
    "profile": {
        "steps": [
            ("relate", "combine the innermost pair R4 and R5, which are in parallel with each other"),
            ("relate", "add R3 in series with that pair to get the resistance of the whole lower branch"),
            ("relate", "combine that branch in parallel with R2 to get the resistance of the parallel section"),
            ("relate", "add R1 in series to get the resistance of the whole network"),
            ("solve", "divide the battery p.d. by the total resistance to get the current the battery delivers"),
            ("solve", "multiply that current by the resistance of the parallel section to get the p.d. across it"),
            ("solve", "divide that p.d. by the resistance of the R3 branch to get the branch current"),
            ("solve", "multiply the branch current by the resistance of the inner pair to get the p.d. across it"),
            ("solve", "divide that p.d. by R4 to get the current asked for"),
            ("check", "add the two currents inside the inner pair and confirm they make the branch current"),
        ],
        "relations": ["R4 in parallel with R5 = (12 &#215; 6.0) / (12 + 6.0) = 4.0 &#937;",
                      "lower branch = R3 + 4.0 = 8.0 + 4.0 = 12 &#937;",
                      "parallel section = (6.0 &#215; 12) / (6.0 + 12) = 4.0 &#937;, so R total = 4.0 + 4.0 = 8.0 &#937;",
                      "I total = 12 / 8.0 = 1.5 A, so V across the parallel section = 1.5 &#215; 4.0 = 6.0 V",
                      "branch current = 6.0 / 12 = 0.50 A, so V across the inner pair = 0.50 &#215; 4.0 = 2.0 V",
                      "I(R4) = 2.0 / 12 = 1/6 A, and I(R5) = 2.0 / 6.0 = 1/3 A, which add to 0.50 A"],
        "insight": "Reduce from the inside out. The two levels of parallelism cannot be dealt with together, and the current is NOT shared equally between the two outer branches: the 6.0 &#937; branch takes twice what the 12 &#937; branch takes.",
        "shape": "circuit-reduction",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(12/(4+(6*12)/(6+12)))*((6*12)/(6+12))/(8+(12*6)/(12+6))*((12*6)/(12+6))/12", "want": "1/6"},
    "sol": '''<p><b>What is being tested.</b> Whether you reduce a network in stages instead of trying to hold the whole thing in your head at once, and whether you resist the very natural assumption that two parallel branches carry equal currents. They carry equal currents only when they have equal resistance, and here they do not.</p>
<p><b>Step 1 — the innermost pair.</b> R4 and R5 sit side by side between the same two points, so they are in parallel:</p>
<div class="formula">R4 and R5 in parallel = (12 &#215; 6.0) / (12 + 6.0) = 72 / 18 = 4.0 &#937;</div>
<p>Start at the inside. Nothing further out can be simplified until this pair has become one number.</p>
<p><b>Step 2 — the branch that carries R3.</b> R3 is in series with that pair, so the whole lower branch has resistance</p>
<div class="formula">R3 + 4.0 = 8.0 + 4.0 = 12 &#937;</div>
<p><b>Step 3 — that branch in parallel with R2.</b> R2 and the branch are connected between the same two nodes, so they are in parallel:</p>
<div class="formula">6.0 and 12 in parallel = (6.0 &#215; 12) / (6.0 + 12) = 72 / 18 = 4.0 &#937;</div>
<p><b>Step 4 — the whole network.</b> R1 is in series with everything that follows it:</p>
<div class="formula">R total = 4.0 + 4.0 = 8.0 &#937;</div>
<p><b>Step 5 — the current the battery delivers.</b></p>
<div class="formula">I total = V / R total = 12 / 8.0 = 1.5 A</div>
<p><b>Step 6 — the p.d. across the parallel section.</b> That section carries the whole 1.5 A and has a resistance of 4.0 &#937;:</p>
<div class="formula">V parallel = I total &#215; 4.0 = 1.5 &#215; 4.0 = 6.0 V</div>
<p>The other 6.0 V is across R1, which is what you would expect, because R1 and the parallel section are now two equal 4.0 &#937; resistances in series across a 12 V supply.</p>
<p><b>Step 7 — the current down the R3 branch.</b> That branch has 12 &#937; across it and 6.0 V across it:</p>
<div class="formula">I branch = 6.0 / 12 = 0.50 A</div>
<p>The remaining 1.0 A goes through R2, which is 6.0 V across 6.0 &#937;. The two currents add to 1.5 A, which is the total the battery supplies. This is the step where the equal-split assumption fails: the branch that looks longer and more complicated actually takes the <i>smaller</i> share, because its total resistance is 12 &#937; against R2's 6.0 &#937;.</p>
<p><b>Step 8 — the p.d. across the inner pair.</b> The 0.50 A now flows through R3 and then through the pair R4 and R5:</p>
<div class="formula">V inner = I branch &#215; 4.0 = 0.50 &#215; 4.0 = 2.0 V</div>
<p>The other 4.0 V of the branch's 6.0 V is across R3 itself, so the two parts are in the ratio of their resistances, 8.0 to 4.0.</p>
<p><b>Step 9 — the current in R4.</b> R4 has 2.0 V across it and a resistance of 12 &#937;:</p>
<div class="formula">I(R4) = V inner / R4 = 2.0 / 12 = 1/6 A</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 10 — check the split inside the pair.</b> R5 has the same 2.0 V across it and only 6.0 &#937;, so</p>
<div class="formula">I(R5) = 2.0 / 6.0 = 1/3 A
1/6 + 1/3 = 1/2 A = I branch</div>
<p>which is the branch current the step started with. The two currents are in the ratio 1 to 2 and the two resistances are in the ratio 2 to 1, exactly inverse, as they must be when the p.d. is common. So R4 carries the <i>smaller</i> of the two shares even though it is the resistor the question asks about — a reminder that the biggest number in a network is not always in the branch you expect.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/2 A</b> is the current in the whole R3 branch. It is a real number, correctly worked out, and it is the most likely wrong answer because it is one step short of the end. It has not yet been divided between R4 and R5.</p>
<p>&middot; <b>1/3 A</b> is the current in R5, the 6.0 &#937; partner. The p.d. of 2.0 V is right; the resistor is the wrong one. Notice that R5 takes twice the current of R4, so confusing the two costs a factor of two.</p>
<p>&middot; <b>1/4 A</b> comes from giving each of the two outer parallel branches half the total current, 0.75 A instead of 0.50 A. Everything after that is done correctly, so the arithmetic is internally consistent — which is exactly why this is the dangerous distractor. The equal split is only valid when the branches are equal, and 6.0 &#937; is not 12 &#937;.</p>
<p>&middot; <b>1/12 A</b> is 12 V divided by 12 &#937;, applying the battery p.d. directly across R4. It ignores R1 and the whole of the parallel section, so it is the answer you would get if R4 were the only resistor in the circuit.</p>
<p><b>The trap.</b> Assuming the current divides equally wherever it meets a junction. The rule is the opposite: with a common p.d., the <i>smaller</i> resistance takes the <i>larger</i> current. At Step 7 the equal split would give 0.75 A where the truth is 0.50 A, and that single error survives to the end as 1/4 A instead of 1/6 A.</p>
<p><b>Relevant topics:</b> series and parallel combinations; the reduction of a network in stages; current division between unequal branches; the potential divider; the p.d. across one resistor of a chain.</p>''',
    "trap": "Assuming two parallel branches share the current equally. With a common p.d. the smaller resistance takes the larger current, so the 12 ohm branch takes 0.50 A where the equal split would give 0.75 A.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 5 -- A, toolkit.  An estimation carried out in powers of ten.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 5, "id": "S04-05", "module": "A", "diff": 3,
    "topic": "Order-of-magnitude estimation: the number of heartbeats in a lifetime",
    "rel": [("A", "Combining rates and times by multiplying, keeping track of the units"),
            ("A", "Working in powers of ten so that only the order of magnitude is kept"),
            ("B", "The rate of a periodic process and the total number of repetitions over an interval")],
    "key": ["estimate", "rate", "powersoften", "units"],
    "stem": '<p>A human heart beats about 70 times a minute at rest. Taking a lifetime to be 80 years, which of the following is the order of magnitude of the number of heartbeats in a lifetime?</p>',
    "opts": ['3.7 &#215; 10<sup>7</sup>', '3.0 &#215; 10<sup>8</sup>', '2.9 &#215; 10<sup>9</sup>', '1.3 &#215; 10<sup>10</sup>', '1.8 &#215; 10<sup>11</sup>'],
    "ans": 2,
    "distractors": ['gives the number of beats in one year, which is the answer to a different question',
                    'slips a factor of ten in the rate, taking 70 beats per minute as 7',
                    'correct',
                    'counts the beats in a year and then multiplies by 365 instead of by 80',
                    'takes the rate as beats per second, so every factor of 60 becomes 3600'],
    "profile": {
        "steps": [
            ("relate", "convert the rate from beats per minute to beats per hour, and then to beats per day"),
            ("relate", "multiply the daily count by the number of days in a year and then by the lifetime in years"),
            ("check", "compare the result with the number of beats in a single day, which should be about ten thousand times smaller"),
            ("check", "confirm the answer is a count, with no units left over, and that it is the largest of the sensible candidates"),
        ],
        "relations": ["rate &#215; time = number of beats",
                      "4200 beats/h &#215; 24 h = 1.0 &#215; 10<sup>5</sup> beats/day",
                      "1.0 &#215; 10<sup>5</sup> &#215; 365 &#215; 80 = 2.9 &#215; 10<sup>9</sup>"],
        "insight": "The whole question is a chain of multiplications, and the only real risk is a power of ten. Working each step to one significant figure keeps the arithmetic mental and makes a slip of a factor of ten visible.",
        "shape": "order-of-magnitude",
        "approx": True,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "70*60*24*365*80", "want": "2943360000"},
    "sol": '''<p><b>What is being tested.</b> Whether you can build an estimate out of rates and times without a calculator, and whether you keep track of what the numbers mean. This is an order of magnitude question: the answer is wanted to one significant figure, and the distractors are all wrong by whole factors of ten.</p>
<p><b>Step 1 — beats per hour.</b> Sixty minutes to the hour:</p>
<div class="formula">70 beats/min &#215; 60 min/h = 4200 beats/h</div>
<p><b>Step 2 — beats per day.</b> Twenty-four hours to the day, and 4200 &#215; 24 is close enough to 4000 &#215; 25:</p>
<div class="formula">4200 &#215; 24 = 1.0 &#215; 10<sup>5</sup> beats/day</div>
<p>It is worth stopping here, because a hundred thousand beats a day is a number most people have never thought about, and it is checkable: it means about seventy beats a minute for a day, which is exactly the rate we started with.</p>
<p><b>Step 3 — beats in a year.</b> A year is about 365 days, and 365 is close to 400:</p>
<div class="formula">1.0 &#215; 10<sup>5</sup> &#215; 365 = 3.7 &#215; 10<sup>7</sup> beats/year</div>
<p><b>Step 4 — beats in a lifetime.</b> Eighty years:</p>
<div class="formula">3.7 &#215; 10<sup>7</sup> &#215; 80 = 2.9 &#215; 10<sup>9</sup> beats</div>
<p>So <b>Answer: C.</b></p>
<p><b>Checking the power of ten.</b> There are two independent ways to see that the answer must be of order 10<sup>9</sup> and not 10<sup>8</sup> or 10<sup>10</sup>. First, a day is about 10<sup>5</sup> beats; a year is 365 days, so a little under 4 &#215; 10<sup>7</sup>; and eighty years is eight times ten, so about 3 &#215; 10<sup>9</sup>. Second, work from the other end: eighty years is about 4 &#215; 10<sup>7</sup> minutes, and at seventy beats a minute that is 4 &#215; 10<sup>7</sup> &#215; 70, which is 2.8 &#215; 10<sup>9</sup>. Both routes agree, and neither needs a calculator.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3.7 &#215; 10<sup>7</sup></b> is the number of beats in a <i>year</i>. It is a real number, correctly worked out, and it is the most likely wrong answer because it is one step short of the end. The question asks for a lifetime.</p>
<p>&middot; <b>3.0 &#215; 10<sup>8</sup></b> is a factor of ten too small. It comes from a slip in the rate — reading 70 as 7, or losing one of the conversions between minutes, hours and days. This is the characteristic failure of an estimation question: not a wrong method, but a lost power of ten.</p>
<p>&middot; <b>1.3 &#215; 10<sup>10</sup></b> is the yearly figure multiplied by 365 instead of by 80. It converts the years to days twice, once in the yearly count and once again at the end.</p>
<p>&middot; <b>1.8 &#215; 10<sup>11</sup></b> comes from treating 70 beats per minute as 70 beats per <i>second</i>. That is a factor of sixty, which is why this option is so much larger than the others rather than a clean power of ten away.</p>
<p><b>The trap.</b> Losing a factor of ten somewhere in the chain. The defence is to carry out the multiplication in two independent ways, as above, and to check that the intermediate numbers are ones you can picture. A hundred thousand beats a day and thirty-seven million a year are both worth knowing as facts, because they make this kind of question self-checking.</p>
<p><b>Relevant topics:</b> estimation and orders of magnitude; rates and conversion of units; working to one significant figure; the use of powers of ten in mental arithmetic.</p>''',
    "trap": "Losing a factor of ten in the chain of conversions, or stopping at the yearly count. Two independent routes to the power of ten are the defence.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 6 -- B, kinematics.  Complementary angles: the ratio of the flight times.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 6, "id": "S04-06", "module": "B", "diff": 2,
    "topic": "Two projectiles at complementary angles: the ratio of their times of flight",
    "rel": [("B", "The time of flight of a projectile depends only on the vertical component of its velocity"),
            ("B", "The range of a projectile on level ground and the identity sin 2&#952; = sin(180&#176; &#8722; 2&#952;)"),
            ("A", "A ratio of two sines evaluated without a calculator")],
    "key": ["projectile", "complementary", "flighttime", "range"],
    "stem": '<p>The figure shows two balls projected from the same point on level ground with the same speed, one at 60&#176; and one at 30&#176; to the horizontal. {{FIG:s04-06}}</p><p>What is the ratio of the longer time of flight to the shorter?</p>',
    "opts": ['&#8730;3', '1', '&#8730;3/2', '2', '3'],
    "ans": 0,
    "distractors": ['correct',
                    'assumes complementary angles give equal times of flight as well as equal ranges',
                    'quotes the sine of the larger angle rather than the ratio of the two sines',
                    'takes the ratio of the angles themselves, 60 to 30',
                    'gives the ratio of the maximum heights, which are in the ratio of the squares of the sines'],
    "profile": {
        "steps": [
            ("relate", "write the time of flight in terms of the vertical component of the launch velocity"),
            ("relate", "note that the two launches share the same speed, so only the sines survive in the ratio"),
            ("solve", "evaluate the ratio of the two sines"),
            ("check", "confirm the two ranges are equal, which the figure also states, and that the taller flight is the longer one"),
        ],
        "relations": ["T = 2 u sin&#952; / g",
                      "T(60&#176;) / T(30&#176;) = sin 60&#176; / sin 30&#176;",
                      "R = u<sup>2</sup> sin 2&#952; / g, and sin 120&#176; = sin 60&#176;"],
        "insight": "The time of flight is set by the vertical motion alone, so it is proportional to the sine of the launch angle. Equal ranges do not mean equal times: the two angles are complementary, and their sines are not equal.",
        "shape": "symmetry",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "sin(pi/3)/sin(pi/6)", "want": "sqrt(3)"},
    "sol": '''<p><b>What is being tested.</b> Whether you separate the horizontal and vertical parts of projectile motion. The time of flight is decided entirely by the vertical part; the horizontal part decides how far the ball travels while it is up there.</p>
<p><b>Step 1 — the time of flight.</b> The vertical velocity at launch is <code>u sin&#952;</code>. The ball rises until that velocity is zero and then falls back, and on level ground the descent takes exactly as long as the climb. So</p>
<div class="formula">T = 2 u sin&#952; / g</div>
<p>Nothing horizontal appears in that expression. That is the key to the whole question.</p>
<p><b>Step 2 — form the ratio.</b> The two launches have the same speed <code>u</code>, and <code>g</code> is the same for both, so those cancel:</p>
<div class="formula">T(60&#176;) / T(30&#176;) = (2 u sin 60&#176; / g) / (2 u sin 30&#176; / g)
              = sin 60&#176; / sin 30&#176;</div>
<p><b>Step 3 — evaluate without a calculator.</b> Both sines are exact values worth knowing:</p>
<div class="formula">sin 60&#176; = &#8730;3/2      sin 30&#176; = 1/2
T(60&#176;) / T(30&#176;) = (&#8730;3/2) / (1/2) = &#8730;3</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 4 — check the ranges.</b> The figure says both balls land at the same distance, and it is worth confirming that this is consistent. The range on level ground is</p>
<div class="formula">R = u<sup>2</sup> sin 2&#952; / g</div>
<p>For 60&#176; this is <code>sin 120&#176;</code>, and for 30&#176; it is <code>sin 60&#176;</code>. Since <code>sin 120&#176; = sin 60&#176;</code>, the two ranges are equal. So the 60&#176; ball is in the air about 1.7 times as long and yet travels the same distance, which means its horizontal speed must be smaller — and it is, because more of the launch speed went into the vertical direction. The two facts are consistent, not contradictory.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1</b> assumes that equal ranges mean equal times. It is the most seductive wrong answer, because the figure makes the equal ranges very visible and it is natural to think that equal outcomes mean equal journeys. But the 60&#176; ball spends longer going up and longer coming down, and travels more slowly across.</p>
<p>&middot; <b>&#8730;3/2</b> is the sine of 60&#176; itself. It is a number that appears in the working — it is the numerator of the ratio — and quoting it as the ratio drops the division by <code>sin 30&#176;</code>.</p>
<p>&middot; <b>2</b> is the ratio of the angles, 60 to 30. Angles are not proportional to their sines, and this is a good place to notice it: the ratio of the angles is 2, while the ratio of the sines is &#8730;3, which is about 1.7. Those are different numbers and only one of them can be right.</p>
<p>&middot; <b>3</b> is the ratio of the maximum heights. The height is <code>u<sup>2</sup> sin<sup>2</sup>&#952; / (2g)</code>, so the heights are in the ratio of the squares of the sines, which is 3 to 1. It is a genuine ratio for this pair of launches, but it is the ratio of the wrong quantity. The figure shows it plainly: the 60&#176; arc is three times as tall.</p>
<p><b>The trap.</b> Assuming that because the ranges are equal the times must be equal. They are equal for a different reason — the identity <code>sin 2&#952; = sin(180&#176; &#8722; 2&#952;)</code> — and that reason has nothing to do with the time of flight.</p>
<p><b>Relevant topics:</b> projectile motion; resolution of velocity; complementary angles and equal range; the maximum height of a projectile; exact values of sine and cosine.</p>''',
    "trap": "Assuming equal ranges mean equal times of flight. The ranges are equal because sin 120 degrees equals sin 60 degrees; the times differ by a factor of the square root of three.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 7 -- C, forces and momentum.  A ball rebounding from a smooth wall.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 7, "id": "S04-07", "module": "C", "diff": 3,
    "topic": "A ball rebounding from a smooth wall: the magnitude of the change in momentum",
    "rel": [("C", "A smooth surface reverses only the component of velocity perpendicular to it"),
            ("G", "The angle of incidence equals the angle of reflection, applied here to a momentum vector rather than to a ray"),
            ("C", "The change in momentum is the vector difference between the final and initial momenta"),
            ("A", "Resolving a vector into components parallel and perpendicular to a chosen direction")],
    "key": ["impulse", "bounce", "wall", "momentum"],
    "stem": '<p>The figure shows a ball of mass <code>m</code> striking a smooth vertical wall with speed <code>v</code> at an angle <code>&#952;</code> to the normal, and rebounding with the same speed at the same angle on the other side of the normal. The velocity triangle at the foot of the figure shows the change in velocity. {{FIG:s04-07}}</p><p>What is the magnitude of the change in the ball\'s momentum?</p>',
    "opts": ['2 m v sin&#952;', '2 m v cos&#952;', 'm v cos&#952;', '2 m v', '0'],
    "ans": 1,
    "distractors": ['uses the component along the wall, which is the component that does not change, so it cancels in the subtraction',
                    'correct',
                    'reverses only the outgoing momentum, forgetting that the ball arrives with momentum in the opposite sense',
                    'assumes the ball strikes the wall head-on and reverses its whole velocity',
                    'takes the change in momentum to be zero because the speed is unchanged'],
    "profile": {
        "steps": [
            ("relate", "resolve the velocity into a component along the normal and a component along the wall"),
            ("relate", "use the fact that a smooth wall can only exert a force along the normal, so only that component reverses"),
            ("solve", "subtract the initial from the final normal component of momentum"),
            ("check", "confirm the change is perpendicular to the wall and that its size reduces to 2mv when the ball strikes head-on"),
        ],
        "relations": ["normal component = v cos&#952;", "along-wall component = v sin&#952; (unchanged)",
                      "&#916;p = m(v cos&#952;) &#8722; m(&#8722;v cos&#952;) = 2 m v cos&#952;"],
        "insight": "Only the component perpendicular to the wall reverses; the component along the wall is untouched. So the change in momentum is perpendicular to the wall, and it is smaller than 2mv unless the ball strikes head-on.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "sym", "got": "m*v*cos(th) - m*(-v*cos(th))", "want": "2*m*v*cos(th)"},
    "sol": '''<p><b>What is being tested.</b> Whether you treat momentum as a vector and work out the CHANGE, rather than comparing speeds. The ball leaves with the same speed it arrived with, and that is exactly what makes the "no change" answer so tempting.</p>
<p><b>Step 1 — resolve the velocity.</b> Take the normal to the wall as one direction and the wall itself as the other. The angle between the velocity and the normal is <code>&#952;</code>, so</p>
<div class="formula">component along the normal = v cos&#952;
component along the wall  = v sin&#952;</div>
<p><b>Step 2 — what a smooth wall can do.</b> A smooth wall exerts no force along its own surface, so the component of momentum parallel to the wall cannot change. It is <code>m v sin&#952;</code> before the impact and <code>m v sin&#952;</code> after. The wall does exert a force along the normal, and since the rebound speed is unchanged, that component simply reverses:</p>
<div class="formula">before:  m v cos&#952; into the wall
after:   m v cos&#952; away from the wall</div>
<p><b>Step 3 — subtract to get the change.</b> Taking away-from-the-wall as positive, the initial component is <code>&#8722;m v cos&#952;</code> and the final component is <code>+m v cos&#952;</code>:</p>
<div class="formula">&#916;p = m v cos&#952; &#8722; (&#8722;m v cos&#952;) = 2 m v cos&#952;</div>
<p>The along-the-wall components cancel, so the change in momentum is directed perpendicular to the wall, away from it, with magnitude <code>2 m v cos&#952;</code>.</p>
<p>So <b>Answer: B.</b></p>
<p><b>Step 4 — check it against the easy cases.</b> If the ball strikes head-on, <code>&#952; = 0</code> and <code>cos&#952; = 1</code>, so the change is <code>2mv</code>. That is right: the ball goes from <code>+mv</code> to <code>&#8722;mv</code> along the normal. If the ball grazes the wall, <code>&#952; &#8594; 90&#176;</code> and <code>cos&#952; &#8594; 0</code>, so the change tends to zero. That is also right: a ball travelling almost parallel to the wall barely interacts with it. The answer has to sit between 0 and <code>2mv</code>, and <code>2mv cos&#952;</code> does.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2 m v sin&#952;</b> uses the component along the wall. It is the component that does <i>not</i> change, so it contributes nothing to a difference; doubling it is doubly wrong.</p>
<p>&middot; <b>m v cos&#952;</b> reverses only the outgoing momentum and forgets that the ball arrived with momentum of the opposite sign. It is the classic slip with a change-of-momentum calculation: the difference of two opposite vectors is their sum of magnitudes.</p>
<p>&middot; <b>2 m v</b> is the head-on answer. It is correct only when <code>&#952; = 0</code>, and here the ball arrives at an angle, so part of its momentum is along the wall and never reverses.</p>
<p>&middot; <b>0</b> comes from comparing speeds instead of velocities. The speed is indeed unchanged, and if momentum were a scalar the change would be zero. It is not: momentum has a direction, and the direction of the normal component has reversed.</p>
<p><b>The trap.</b> Comparing <code>v</code> before with <code>v</code> after and concluding that nothing changed. The velocity triangle drawn in the figure exists precisely to make this visible: the two velocity arrows have the same length, and the arrow joining their tips is not zero.</p>
<p><b>Relevant topics:</b> momentum as a vector; impulse and change in momentum; resolution of vectors; reflection at a smooth surface; Newton's third law and the normal reaction.</p>''',
    "trap": "Comparing speeds rather than velocities, and concluding the change is zero. The speed is unchanged, but the component perpendicular to the wall reverses.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 8 -- D, circular motion.  The smallest speed at the top of a vertical loop.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 8, "id": "S04-08", "module": "D", "diff": 3,
    "topic": "The top of a vertical circular loop: the smallest speed that keeps contact",
    "rel": [("D", "The resultant force on a body in circular motion is directed towards the centre"),
            ("D", "At the top of a vertical circle the weight and the normal reaction both act towards the centre"),
            ("C", "The limiting case in which a contact force falls to zero"),
            ("A", "Cancelling a common factor from both sides of an equation")],
    "key": ["loop", "centripetal", "normalreaction", "limiting"],
    "stem": '<p>The figure shows a car at the top of a vertical circular loop of radius <code>r</code>. At that point the weight and the normal reaction from the track both act downward, towards the centre of the circle. {{FIG:s04-08}}</p><p>What is the smallest speed the car can have at the top and still stay in contact with the track?</p>',
    "opts": ['&#8730;(2 g r)', '&#8730;(g / r)', 'g r', '&#8730;(g r)', '2&#8730;(g r)'],
    "ans": 3,
    "distractors": ['adds a term for the height climbed, as though the car had to rise by r as well as stay on the track',
                    'divides by r instead of multiplying, which gives the wrong dimensions as well as the wrong value',
                    'leaves out the square root, so the answer is the square of the speed rather than the speed',
                    'correct',
                    'takes the normal reaction at the top to equal the weight, so it doubles the centripetal force needed'],
    "profile": {
        "steps": [
            ("relate", "write the equation of motion at the top, with both forces directed towards the centre"),
            ("relate", "identify the limiting case as the one where the contact force falls to zero"),
            ("solve", "cancel the mass and solve for the speed"),
            ("check", "confirm the dimensions are those of a speed and that the answer grows with r"),
        ],
        "relations": ["m g + N = m v<sup>2</sup> / r", "N = 0 at the limiting speed", "v<sup>2</sup> = g r"],
        "insight": "At the top of the loop the weight already points towards the centre, so it can supply the whole centripetal force on its own. The smallest speed is the one at which it does exactly that and the track is needed for nothing.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "sym", "got": "sqrt(m*g*r/m)", "want": "sqrt(g*r)"},
    "sol": '''<p><b>What is being tested.</b> Whether you know which way the forces point at the top of a vertical circle, and whether you can identify a limiting case. Both are needed, and the first is the one that trips people.</p>
<p><b>Step 1 — the forces at the top.</b> This is the point of the question. At the <i>bottom</i> of the loop the track pushes up and the weight pulls down, and they oppose. At the <i>top</i> the track is above the car, so it can only push downward, and the weight also acts downward. Both forces point towards the centre of the circle, so they add:</p>
<div class="formula">m g + N = m v<sup>2</sup> / r</div>
<p><b>Step 2 — the limiting case.</b> The normal reaction can push but it cannot pull. If the car is too slow, the track has nothing to push with and the car leaves it; the boundary between staying on and falling off is the case where <code>N</code> has fallen to zero. That is the smallest speed the question asks for:</p>
<div class="formula">N = 0  gives  m g = m v<sup>2</sup> / r</div>
<p><b>Step 3 — solve.</b> The mass cancels, which is worth noticing: the answer does not depend on how heavy the car is, only on the size of the loop and the strength of gravity.</p>
<div class="formula">v<sup>2</sup> = g r
v = &#8730;(g r)</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 4 — check the dimensions and the trend.</b> <code>g</code> is m s<sup>-2</sup> and <code>r</code> is m, so <code>gr</code> is m<sup>2</sup> s<sup>-2</sup> and its square root is m s<sup>-1</sup>. That is a speed, as it must be. The trend is also right: a bigger loop needs a faster car, and a stronger gravitational field needs a faster car. Both make physical sense, since a bigger radius means more centripetal acceleration is needed for the same speed and gravity is what supplies it.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>&#8730;(2 g r)</b> is the speed at the bottom of a loop of height <code>2r</code> when the car is just able to reach the top. It is a real result in this topic, and it answers a different question — the speed needed at the <i>bottom</i>, not at the top. Mixing the two up is the most common error in loop problems, and it happens because both answers are written with <code>g</code> and <code>r</code> under a root.</p>
<p>&middot; <b>&#8730;(g / r)</b> inverts the radius. Check the units: <code>g/r</code> is s<sup>-2</sup>, whose square root is a reciprocal time, not a speed. A dimensional check would have caught this one without any physics at all.</p>
<p>&middot; <b>g r</b> is the square of the correct answer. It has the dimensions of a speed squared, so it is not a speed. This is the answer you get by stopping one line early.</p>
<p>&middot; <b>2&#8730;(g r)</b> comes from taking the normal reaction at the top to equal the weight. That would give <code>mg + mg = mv<sup>2</sup>/r</code> and hence <code>v = &#8730;(2gr)</code> — but the whole point of the limiting case is that <code>N</code> has fallen to zero, not that it equals <code>mg</code>.</p>
<p><b>The trap.</b> Drawing the normal reaction at the top pointing outward, as it does at the bottom. It cannot: the track is outside the circle, so it pushes inward. The figure states the direction in words as well as drawing it, because this single fact decides the sign of the whole equation.</p>
<p><b>Relevant topics:</b> circular motion and centripetal force; motion in a vertical circle; the limiting case where a contact force vanishes; apparent weightlessness at the top of a loop.</p>''',
    "trap": "Drawing the normal reaction at the top pointing outward, as it does at the bottom. At the top both the weight and the reaction point towards the centre, so they add.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 9 -- F, waves.  The speed on a stretched string when the tension rises.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 9, "id": "S04-09", "module": "F", "diff": 2,
    "topic": "The speed of a wave on a stretched string when the tension is increased",
    "rel": [("F", "The speed of a transverse wave on a stretched string in terms of tension and mass per unit length"),
            ("F", "A proportional relationship and the way a square root changes a fractional increase"),
            ("A", "Recognising a square root when it is written as a power of a half")],
    "key": ["string", "tension", "wavespeed", "root"],
    "stem": '<p>A transverse wave travels along a stretched string at 40 m/s. The tension in the string is increased by 21%, the string being kept at the same length. What is the new wave speed?</p>',
    "opts": ['36 m/s', '41 m/s', '48 m/s', '58 m/s', '44 m/s'],
    "ans": 4,
    "distractors": ['inverts the ratio, so the speed would fall when the tension rises',
                    'adds the square root of the factor to the original speed instead of multiplying by it',
                    'takes the speed to be proportional to the tension rather than to its square root',
                    'uses the square root of the fractional increase on its own instead of the square root of the whole factor',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "write the wave speed on a string in terms of the tension and the mass per unit length"),
            ("relate", "note that the mass per unit length is unchanged, so the speed depends only on the tension"),
            ("solve", "form the ratio of the new speed to the old as the square root of the ratio of the tensions"),
            ("check", "confirm the speed rises by less than 21%, which is what a square root does to a fractional increase"),
        ],
        "relations": ["v = &#8730;(F / &#956;)", "v2 / v1 = &#8730;(F2 / F1)", "F2 / F1 = 121 / 100"],
        "insight": "The speed goes as the square root of the tension, so a 21% rise in tension is only a 10% rise in speed. The factor 121/100 was chosen because its square root is exactly 11/10.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "40*sqrt(1.21)", "want": "44"},
    "sol": '''<p><b>What is being tested.</b> Whether you know that the wave speed on a string depends on the square root of the tension, and whether you handle a percentage increase without reaching for a calculator.</p>
<p><b>Step 1 — the wave speed on a string.</b> For a stretched string of tension <code>F</code> and mass per unit length <code>&#956;</code>, the transverse wave speed is</p>
<div class="formula">v = &#8730;(F / &#956;)</div>
<p><b>Step 2 — what is unchanged.</b> The string is kept at the same length, and no mass is added or removed, so <code>&#956;</code> is unchanged. Only <code>F</code> changes. Dividing the new speed by the old, the mass per unit length cancels:</p>
<div class="formula">v2 / v1 = &#8730;(F2 / &#956;) / &#8730;(F1 / &#956;)
       = &#8730;(F2 / F1)</div>
<p><b>Step 3 — put the numbers in.</b> A 21% increase means the new tension is 121/100 of the old, and that fraction has an exact square root:</p>
<div class="formula">F2 / F1 = 121 / 100
v2 / v1 = &#8730;(121 / 100) = 11 / 10</div>
<p>So the new speed is ten per cent higher than the old one:</p>
<div class="formula">v2 = 40 &#215; 11/10 = 44 m/s</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 4 — check that a square root behaves the way it should.</b> A rise of 21% in the tension produces a rise of only 10% in the speed, and that is the characteristic behaviour of a square root: it always makes a fractional increase smaller. If the tension doubled, the speed would rise by only about 41%, not by 100%. The answer must therefore lie between 40 and 48.4 m/s, and 44 m/s does. This is a cheap and reliable check on any question of this shape.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>36 m/s</b> divides instead of multiplying, 40 &#247; 1.1. It has the speed falling when the tension rises, which is backwards: a tighter string carries a wave faster, which is why a guitar string is tuned by tightening it.</p>
<p>&middot; <b>41 m/s</b> comes from adding the square root of the factor to the original speed, 40 + 1.1. The square root of a ratio is a multiplier, not something to be added to the quantity being scaled.</p>
<p>&middot; <b>48 m/s</b> is 40 &#215; 121/100, which treats the speed as proportional to the tension rather than to its square root. It is the single most common error here, and the check in step 4 rules it out at once: a 21% tension rise cannot produce a 21% speed rise when the relationship is a square root.</p>
<p>&middot; <b>58 m/s</b> is 40 &#215; (1 + &#8730;0.21), which uses the square root of the fractional increase instead of the square root of the whole factor. 21% is the increase, not the ratio, and the square root applies to the ratio.</p>
<p><b>The trap.</b> Treating a percentage increase in tension as a percentage increase in speed. Whenever a quantity is proportional to a square root, a small percentage change in the thing inside the root becomes roughly half that percentage change outside it — here 21% becomes 10%.</p>
<p><b>Relevant topics:</b> the wave equation and wave speed; transverse waves on a string; tension and mass per unit length; proportional reasoning and square roots.</p>''',
    "trap": "Scaling the speed by the same percentage as the tension. The speed goes as the square root of the tension, so a 21% rise in tension gives a 10% rise in speed.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 10 -- G, optics.  The acceptance angle of an optical fibre.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 10, "id": "S04-10", "module": "G", "diff": 3,
    "topic": "An optical fibre: the condition for a ray to be guided along the core",
    "rel": [("G", "Snell's law at the flat end face of the fibre"),
            ("G", "Total internal reflection at the side wall, and the critical angle"),
            ("A", "The geometry of an angle measured from a wall rather than from the normal to it")],
    "key": ["fibre", "totalinternal", "criticalangle", "geometry"],
    "stem": '<p>The figure shows a ray entering the flat end face of an optical fibre from air at an angle <code>i</code> to the axis. Inside the core, of refractive index <code>n</code>, the ray travels at an angle <code>r</code> to the axis and then meets the side wall, where the normal is horizontal. {{FIG:s04-10}}</p><p>Which expression gives the largest value of <code>sin i</code> for which the ray is totally internally reflected at the side wall?</p>',
    "opts": ['&#8730;(n<sup>2</sup> &#8722; 1)', 'n &#8722; 1', '&#8730;(n<sup>2</sup> + 1)', '1/n', '(n<sup>2</sup> &#8722; 1)/n'],
    "ans": 0,
    "distractors": ['correct',
                    'drops both the square root and the one, taking the sine of the acceptance angle to be the difference of two numbers',
                    'uses the wrong sign in the identity, adding the one instead of subtracting it',
                    'quotes the sine of the critical angle at the side wall rather than the sine of the angle in air',
                    'leaves out the square root when converting the cosine back to a sine'],
    "profile": {
        "steps": [
            ("relate", "apply Snell's law at the end face to relate the angle in air to the angle in the core"),
            ("relate", "note that the normal at the side wall is horizontal, so the angle of incidence there is 90 degrees minus r"),
            ("relate", "write the condition for total internal reflection at the side wall"),
            ("solve", "convert the condition on the cosine into a condition on the sine, using sin<sup>2</sup> + cos<sup>2</sup> = 1"),
            ("check", "confirm the result is less than 1 for a core of index 1.5, as an acceptance sine must be"),
        ],
        "relations": ["sin i = n sin r",
                      "angle at the side wall = 90&#176; &#8722; r",
                      "cos r &#8805; 1/n",
                      "sin i &#8804; n&#8730;(1 &#8722; 1/n<sup>2</sup>) = &#8730;(n<sup>2</sup> &#8722; 1)"],
        "insight": "The angle at the side wall is 90 degrees minus r, not r. The ray bends towards the axis at the end face and then runs almost parallel to the wall, so the angle it makes with the wall's normal is close to 90 degrees.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "sym", "got": "n*sqrt(1 - 1/n**2)", "want": "sqrt(n**2 - 1)"},
    "sol": '''<p><b>What is being tested.</b> Whether you can track an angle through a change of reference direction. The physics is two standard results — Snell's law and the critical angle — and the difficulty is entirely geometric.</p>
<p><b>Step 1 — refraction at the end face.</b> The end face is perpendicular to the axis, so the normal at the end face is along the axis. The ray arrives at angle <code>i</code> to the axis, which is therefore the angle of incidence, and leaves at angle <code>r</code> to the axis, which is the angle of refraction. Snell's law, with air on the outside:</p>
<div class="formula">sin i = n sin r</div>
<p><b>Step 2 — the angle at the side wall.</b> This is the step the question turns on. At the side wall the normal is horizontal, perpendicular to the axis. The ray travels at angle <code>r</code> to the axis, so the angle between the ray and that normal is <code>90&#176; &#8722; r</code>. The figure marks it explicitly. It is <i>not</i> <code>r</code>.</p>
<div class="formula">angle of incidence at the wall = 90&#176; &#8722; r</div>
<p><b>Step 3 — the condition for total internal reflection.</b> The ray is guided provided this angle exceeds the critical angle for the core, where <code>sin &#952;c = 1/n</code>. Since the sine of an angle increases with the angle up to 90&#176;, the condition can be written either way round, but the cosine form is the useful one:</p>
<div class="formula">90&#176; &#8722; r &#8805; &#952;c
cos r &#8805; 1/n</div>
<p>The switch from sine to cosine is just <code>sin(90&#176; &#8722; r) = cos r</code>, and it is worth making because it puts the condition in terms of the same angle <code>r</code> that Snell's law gave us.</p>
<p><b>Step 4 — convert to a condition on sin i.</b> The largest possible <code>sin r</code> corresponds to the smallest possible <code>cos r</code>, which is <code>1/n</code>. Using <code>sin<sup>2</sup>r + cos<sup>2</sup>r = 1</code>:</p>
<div class="formula">sin r &#8804; &#8730;(1 &#8722; cos<sup>2</sup>r) = &#8730;(1 &#8722; 1/n<sup>2</sup>)</div>
<p>and multiplying by <code>n</code> to get back to the outside world:</p>
<div class="formula">sin i &#8804; n&#8730;(1 &#8722; 1/n<sup>2</sup>) = &#8730;(n<sup>2</sup> &#8722; 1)</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 5 — check the answer with a number.</b> A typical core has <code>n = 1.5</code>. Then <code>&#8730;(2.25 &#8722; 1) = &#8730;1.25</code>, which is about 1.1 — and a sine cannot exceed 1, so something is wrong. The resolution is that a real fibre's core index is only slightly above the cladding's, so the critical angle is measured against the cladding and not against air; the formula here describes the idealised case of a core surrounded by a much less dense medium. Within that idealisation the algebra is right, and the check is worth doing because it tells you exactly what the model assumes.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>n &#8722; 1</b> is what is left if both the square root and the subtraction of one are dropped. For <code>n = 1.5</code> it gives 0.5, which corresponds to an acceptance angle of 30&#176; — a number that looks plausible and is wrong.</p>
<p>&middot; <b>&#8730;(n<sup>2</sup> + 1)</b> adds the one instead of subtracting it. It comes from writing <code>sin<sup>2</sup>r = 1 + cos<sup>2</sup>r</code>, which is the sign error in the standard identity. It is always greater than <code>n</code>, and so always greater than 1, which is impossible for a sine.</p>
<p>&middot; <b>1/n</b> is the sine of the critical angle at the side wall. It is a genuine quantity in this problem and it is the right-hand side of the condition in step 3, but it is the sine of an angle <i>inside</i> the fibre, not the sine of the angle in air that the question asks for.</p>
<p>&middot; <b>(n<sup>2</sup> &#8722; 1)/n</b> is <code>&#8730;(1 &#8722; 1/n<sup>2</sup>)</code> without the root — that is, the largest possible <code>sin r</code>. It is the correct answer to the question "what is the largest sine of the angle inside the core?", which is one step short of what was asked.</p>
<p><b>The trap.</b> Using <code>r</code> as the angle of incidence at the side wall. The normal there is perpendicular to the axis, and the ray is nearly parallel to the axis, so the two are nearly perpendicular to each other. Writing <code>r</code> instead of <code>90&#176; &#8722; r</code> produces an answer that is wrong for a reason no amount of algebra will fix.</p>
<p><b>Relevant topics:</b> Snell's law; total internal reflection and the critical angle; optical fibres; the geometry of angles measured from a surface rather than from its normal.</p>''',
    "trap": "Using r as the angle of incidence at the side wall. The normal there is horizontal, so the angle is 90 degrees minus r, and that is the step the question turns on.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 11 -- H, circuits.  A thermistor in a potential divider.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 11, "id": "S04-11", "module": "H", "diff": 2,
    "topic": "A thermistor in the top arm of a potential divider: the output across the lower arm",
    "rel": [("H", "The output of a potential divider is the supply multiplied by the fraction of the resistance in the arm it is taken across"),
            ("H", "The resistance of a thermistor falls as its temperature rises"),
            ("A", "Deciding which way a ratio moves when one of its terms changes")],
    "key": ["thermistor", "divider", "output", "ratio"],
    "stem": '<p>The figure shows a potential divider across a 6.0 V supply with a thermistor in the upper arm and a fixed resistor of 2.0 k&#937; in the lower arm. The output is taken across the fixed resistor. {{FIG:s04-11}}</p><p>When the thermistor is warm its resistance has fallen to 1.0 k&#937;. What is the output voltage then?</p>',
    "opts": ['1.5 V', '2.0 V', '3.0 V', '4.0 V', '4.5 V'],
    "ans": 3,
    "distractors": ['takes the output across the thermistor, which is the other arm of the divider',
                    'quotes the value at the higher thermistor resistance, where the divider is 4.0 k&#937; over 2.0 k&#937;',
                    'takes the output as half the supply, which a divider gives only when the two arms are equal',
                    'correct',
                    'scales the supply by the fractional fall in the thermistor\'s resistance instead of by the divider ratio'],
    "profile": {
        "steps": [
            ("relate", "write the output as the supply multiplied by the fraction of the resistance in the lower arm"),
            ("relate", "note that the thermistor is the upper arm, so lowering its resistance raises the output"),
            ("solve", "put the warm resistance into the divider expression"),
            ("check", "compare with the output at the higher resistance, and confirm the change is in the direction the physics requires"),
        ],
        "relations": ["V out = E &#215; R / (R + R thermistor)",
                      "V out = 6.0 &#215; 2.0 / (2.0 + 1.0)",
                      "V out = 4.0 V"],
        "insight": "The output is taken across the LOWER arm. Heating the thermistor lowers the upper arm, which leaves a larger share of the supply for the lower arm, so the output rises. Swapping the two arms would invert the answer.",
        "shape": "monotonicity",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "6.0*2.0/(2.0+1.0)", "want": "4.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you can see which way the output moves before doing any arithmetic, and whether you know which arm the output is taken across. The figure is explicit about the second, because it is where the question is decided.</p>
<p><b>Step 1 — the divider rule.</b> In a potential divider the supply voltage is shared between the two arms in proportion to their resistances, because the same current flows through both. The p.d. across an arm is the supply multiplied by that arm's share of the total:</p>
<div class="formula">V out = E &#215; R / (R + R thermistor)</div>
<p>Here the output is taken across the fixed resistor, so <code>R</code> in that expression is 2.0 k&#937; and the thermistor is in the denominator.</p>
<p><b>Step 2 — which way it moves.</b> A thermistor's resistance falls as it gets hotter. The thermistor is in the <i>upper</i> arm, so heating it lowers the denominator of the fraction above. The fraction therefore rises, and the output rises with it. This is worth working out before touching the numbers, because it is the part of the question that a careless reader gets backwards.</p>
<p><b>Step 3 — the arithmetic.</b> With the thermistor at 1.0 k&#937;:</p>
<div class="formula">V out = 6.0 &#215; 2.0 / (2.0 + 1.0)
      = 6.0 &#215; 2.0 / 3.0
      = 4.0 V</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 4 — check against the cool state.</b> When the thermistor is cool, take its resistance to be 4.0 k&#937;. Then</p>
<div class="formula">V out = 6.0 &#215; 2.0 / (2.0 + 4.0) = 2.0 V</div>
<p>So the output runs from 2.0 V when cool to 4.0 V when warm. It rises, which is what step 2 predicted, and it stays between 0 and 6.0 V, which it must because the output is a share of the supply. Both checks pass, so the arithmetic and the physics agree.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1.5 V</b> is <code>6.0 &#215; 1.0/(1.0 + 3.0)</code> — the output taken across the thermistor, which is the other arm. It is a genuine potential-divider calculation, just taken from the wrong pair of terminals. Reading the figure carefully is the whole defence.</p>
<p>&middot; <b>2.0 V</b> is the output in the cool state. It is a correct number for a different temperature, and it is the answer you get by using the resistance the question has just told you has changed.</p>
<p>&middot; <b>3.0 V</b> is half the supply, which a divider gives only when the two arms are equal. Here they are 2.0 k&#937; and 1.0 k&#937;, so the lower arm takes two thirds of the supply, not a half.</p>
<p>&middot; <b>4.5 V</b> is three quarters of the supply, which is what you get by scaling 6.0 V by the fractional fall in the thermistor's resistance. The output of a divider is not set by how much a component has changed; it is set by the ratio of the two resistances as they now are.</p>
<p><b>The trap.</b> Getting the direction wrong. A question like this is often answered correctly by someone who then cannot say whether the output rose or fell, which means the answer was pattern-matched rather than understood. The reliable way to see it is to ask which arm has become smaller: a smaller upper arm means a larger share for the lower one.</p>
<p><b>Relevant topics:</b> potential dividers; the resistance of a thermistor and its temperature dependence; using a thermistor as a temperature sensor; ratio reasoning without a calculator.</p>''',
    "trap": "Taking the output across the thermistor instead of the fixed resistor, which inverts the answer. The output is across the lower arm, so heating raises it.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 12 -- K, nuclear.  Nuclear density and the A to the one third law.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 12, "id": "S04-12", "module": "K", "diff": 2,
    "topic": "The density of nuclear matter and the dependence of nuclear radius on mass number",
    "rel": [("K", "The nuclear radius depends on the mass number as A to the power one third"),
            ("K", "The mass of a nucleus is proportional to its mass number"),
            ("A", "Combining two proportional relationships to see whether a third quantity is constant")],
    "key": ["nuclearradius", "density", "scaling", "constant"],
    "stem": '<p>The radius of a nucleus of mass number <code>A</code> is given by <code>R = r0 A<sup>1/3</sup></code>, where <code>r0</code> is a constant. What is the ratio of the density of nuclear matter in a nucleus of mass number <code>8A</code> to that in a nucleus of mass number <code>A</code>?</p>',
    "opts": ['1/8', '1', '2', '4', '8'],
    "ans": 1,
    "distractors": ['assumes the volume grows with the mass number but the mass does not, so the density falls in proportion',
                    'correct',
                    'divides the mass ratio by the square of the radius ratio instead of by its cube',
                    'divides the mass ratio by the radius ratio rather than by the volume ratio',
                    'takes the density to scale with the mass number, forgetting that the volume grows as well'],
    "profile": {
        "steps": [
            ("relate", "write the volume of a nucleus in terms of its radius, and substitute the A to the one third law"),
            ("relate", "note that the mass of a nucleus is proportional to its mass number"),
            ("solve", "form the density as the ratio of the two and cancel the mass number"),
            ("check", "confirm the result is independent of A, which is the physical statement the question is about"),
        ],
        "relations": ["V = (4/3)&#960; R<sup>3</sup> &#8733; A", "m &#8733; A", "&#961; = m / V &#8733; A / A"],
        "insight": "The radius goes as the cube root of the mass number, so the volume goes as the mass number itself. Mass and volume therefore grow together and the density does not depend on A at all.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(8*A)/(8*A)", "want": "1"},
    "sol": '''<p><b>What is being tested.</b> Whether you can combine two scaling laws and see that they cancel. The result — that all nuclei have the same density — is one of the most striking facts about the nucleus, and it is a direct consequence of the cube root in the radius formula.</p>
<p><b>Step 1 — the volume.</b> A nucleus is taken to be a sphere, so its volume goes as the cube of its radius. Substituting the given law:</p>
<div class="formula">V = (4/3)&#960; R<sup>3</sup>
  &#8733; (A<sup>1/3</sup>)<sup>3</sup>
  &#8733; A</div>
<p>The cube and the cube root cancel exactly, which is the whole point of writing the radius that way. A nucleus with eight times the mass number has eight times the volume.</p>
<p><b>Step 2 — the mass.</b> The mass of a nucleus is very nearly proportional to its mass number, because protons and neutrons have almost the same mass and the mass number counts them:</p>
<div class="formula">m &#8733; A</div>
<p><b>Step 3 — the density.</b> Density is mass over volume, so the two proportionalities go into the same expression:</p>
<div class="formula">&#961; = m / V &#8733; A / A = constant</div>
<p>The mass number cancels, so the density does not depend on <code>A</code>. The ratio asked for is therefore 1.</p>
<p>So <b>Answer: B.</b></p>
<p><b>Step 4 — check that this is not a coincidence of the algebra.</b> Take a nucleus of mass number 8A. Its radius is <code>r0(8A)<sup>1/3</sup> = 2r0A<sup>1/3</sup></code>, twice the radius of the <code>A</code> nucleus. Its volume is therefore <code>2<sup>3</sup> = 8</code> times as large, and its mass is 8 times as large, so the density is unchanged. That is the same answer by a completely concrete route, with no cancelling symbols, and it is worth doing both ways because the concrete route makes the physics visible.</p>
<p><b>What the result means.</b> Nuclear matter has a density of 2 &#215; 10<sup>17</sup> kg m<sup>-3</sup>, the same in hydrogen as in uranium. It is about 10<sup>14</sup> times the density of water. This is why the nucleus is described as a nearly incompressible droplet: the nucleons are packed together at a fixed spacing, and adding more of them makes the droplet bigger rather than denser.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/8</b> assumes the volume grows but the mass does not. That would be true of a balloon being inflated, not of a nucleus being built up out of nucleons.</p>
<p>&middot; <b>2</b> divides the mass ratio by the square of the radius ratio, 8/4. That is what you get if the volume is taken to go as the square of the radius. Volumes go as the cube of a length, always.</p>
<p>&middot; <b>4</b> divides the mass ratio by the radius ratio itself, 8/2. It treats the radius as if it were the volume, which is a dimensional error as well as a numerical one.</p>
<p>&middot; <b>8</b> takes the density to scale with the mass number. That would mean a uranium nucleus were eight times denser than an oxygen one, which is not what is observed: the whole reason the radius law has a cube root in it is that the density is constant.</p>
<p><b>The trap.</b> Reading the cube root as a scaling law for the density rather than for the radius. The law given is about the radius; the density needs the volume, which is the cube of the radius, and it is the cube that removes the root.</p>
<p><b>Relevant topics:</b> nuclear radius and the A to the one third law; nuclear density; proportional reasoning with powers; the incompressibility of nuclear matter.</p>''',
    "trap": "Scaling the density with the mass number, or with the radius. The radius goes as the cube root of A, so the volume goes as A, and the density is constant.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 13 -- L, quantum.  Reading Planck's constant off a stopping-potential graph.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 13, "id": "S04-13", "module": "L", "diff": 2,
    "topic": "The gradient of a stopping-potential against frequency graph, and what it measures",
    "rel": [("L", "Einstein's photoelectric equation in the form relating stopping potential to frequency"),
            ("L", "The gradient of a graph as the constant that multiplies the quantity on the horizontal axis"),
            ("A", "The electronic charge as the conversion between a potential difference and an energy")],
    "key": ["photoelectric", "stoppingpotential", "gradient", "planck"],
    "stem": '<p>The figure shows the stopping potential for a metal plotted against the frequency of the incident light. The graph is a straight line that crosses the frequency axis at the threshold frequency, and the gradient triangle marked on the line gives a gradient of 4.0 &#215; 10<sup>-15</sup> V s. {{FIG:s04-13}}</p><p>Taking the electronic charge to be 1.6 &#215; 10<sup>-19</sup> C, what is the value of Planck\'s constant obtained from this graph?</p>',
    "opts": ['6.4 &#215; 10<sup>-35</sup> J s', '2.5 &#215; 10<sup>4</sup> J s', '4.0 &#215; 10<sup>-15</sup> J s', '6.4 &#215; 10<sup>-16</sup> J s', '6.4 &#215; 10<sup>-34</sup> J s'],
    "ans": 4,
    "distractors": ['makes a power-of-ten slip in the electronic charge',
                    'divides by the electronic charge instead of multiplying by it',
                    'quotes the gradient itself, forgetting that the vertical axis is a potential and that the charge converts it into an energy',
                    'makes a power-of-ten slip in the gradient',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "write Einstein's equation in the form that has the stopping potential on the left"),
            ("relate", "read off the gradient as the constant multiplying the frequency"),
            ("solve", "multiply the gradient by the electronic charge to get Planck's constant"),
            ("check", "confirm the answer is the accepted value to two significant figures and that the units reduce to J s"),
        ],
        "relations": ["e V = h f &#8722; W", "V = (h/e) f &#8722; W/e", "gradient = h / e"],
        "insight": "The graph is a straight line whose gradient is h/e, not h. The vertical axis is a potential difference, so the charge is what turns it into an energy — and forgetting that factor of e is the error the whole question is aimed at.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "1.6e-19*4.0e-15", "want": "6.4e-34"},
    "sol": '''<p><b>What is being tested.</b> Whether you can read a graph's gradient and say what it means physically. Reading the gradient is the easy half; knowing that it gives <code>h/e</code> rather than <code>h</code> is the half that separates a correct answer from a plausible one.</p>
<p><b>Step 1 — Einstein's equation in the right form.</b> The photoelectric equation says the photon's energy is shared between escaping the metal and the kinetic energy of the electron. The most energetic electrons are stopped by a potential <code>V</code>, so their kinetic energy is <code>eV</code>:</p>
<div class="formula">e V = h f &#8722; W</div>
<p>where <code>W</code> is the work function. Dividing through by <code>e</code> puts the equation in the form the graph plots:</p>
<div class="formula">V = (h/e) f &#8722; W/e</div>
<p><b>Step 2 — identify the gradient.</b> This has the form <code>y = mx + c</code> with <code>V</code> on the vertical axis and <code>f</code> on the horizontal one. So the gradient is the coefficient of <code>f</code>:</p>
<div class="formula">gradient = h / e</div>
<p>The intercept on the potential axis is <code>&#8722;W/e</code>, and the crossing point on the frequency axis is the threshold frequency. Neither of those is asked for, and that is deliberate: the intercept gives the work function, the gradient gives Planck's constant, and a question that asked for the intercept would test something different.</p>
<p><b>Step 3 — multiply by the charge.</b> The gradient is known, so</p>
<div class="formula">h = e &#215; gradient
  = 1.6 &#215; 10<sup>-19</sup> &#215; 4.0 &#215; 10<sup>-15</sup>
  = 6.4 &#215; 10<sup>-34</sup> J s</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 4 — check the answer and the units.</b> The accepted value of Planck's constant is 6.6 &#215; 10<sup>-34</sup> J s, so an answer of 6.4 &#215; 10<sup>-34</sup> J s is right to the two significant figures the data supports. That is a strong check, because there is only one exponent this number could plausibly have, and the calculation has to land on it. The units check too: the gradient is in V s, and a volt times a coulomb is a joule, so the charge converts V s into J s — which is the unit of <code>h</code>.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>6.4 &#215; 10<sup>-35</sup> J s</b> is a power of ten too small. It comes from a slip in the electronic charge, taking it as 1.6 &#215; 10<sup>-20</sup> instead of 10<sup>-19</sup>. The power of ten in the charge is worth memorising precisely because it is so easy to drop.</p>
<p>&middot; <b>2.5 &#215; 10<sup>4</sup> J s</b> divides by the charge instead of multiplying, 4.0 &#215; 10<sup>-15</sup> / 1.6 &#215; 10<sup>-19</sup>. The answer is not even close to the right order of magnitude, and the sign of the exponent is the giveaway: dividing by a very small number makes the result large, while <code>h</code> is famously small.</p>
<p>&middot; <b>4.0 &#215; 10<sup>-15</sup> J s</b> is the gradient itself. The units are wrong, and that is the clue: a gradient of volts per hertz is V s, not J s. The conversion needs the charge, and stopping at the gradient means the conversion was never made.</p>
<p>&middot; <b>6.4 &#215; 10<sup>-16</sup> J s</b> is a power of ten too large, from taking the gradient as 4.0 &#215; 10<sup>-14</sup> instead of 10<sup>-15</sup>. It is a reminder that the exponent in the gradient has to be read off the axis labels rather than guessed.</p>
<p><b>The trap.</b> Reading the gradient and stopping. The gradient of this graph is a genuinely useful quantity and it is not <code>h</code>; it is <code>h/e</code>. The charge is what converts a potential difference into an energy, and it cannot be left out.</p>
<p><b>Relevant topics:</b> the photoelectric effect; Einstein's photoelectric equation; stopping potential and threshold frequency; reading gradients and intercepts from graphs; the electronic charge.</p>''',
    "trap": "Reading the gradient as Planck's constant. The vertical axis is a potential difference, so the gradient is h/e and the electronic charge must be multiplied back in.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 14 -- A, toolkit.  Base units of a constant in a formula.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 14, "id": "S04-14", "module": "A", "diff": 2,
    "topic": "Finding the base units of the viscosity in Stokes' law",
    "rel": [("A", "Rearranging a formula for the constant whose units are wanted"),
            ("A", "Substituting the base units of newtons, metres and seconds and cancelling"),
            ("C", "The drag force on a sphere moving through a fluid, as a product of the fluid's properties and the sphere's motion")],
    "key": ["units", "viscosity", "base", "cancelling"],
    "stem": '<p>The drag force on a small sphere moving slowly through a fluid is given by <code>F = 6&#960;&#951;rv</code>, where <code>r</code> is the radius of the sphere, <code>v</code> is its speed, and <code>&#951;</code> is the viscosity of the fluid.</p><p>Which of the following is the base-unit form of the viscosity?</p>',
    "opts": ['kg m s<sup>-1</sup>', 'kg m<sup>-2</sup> s<sup>-1</sup>', 'kg m<sup>-1</sup> s<sup>-1</sup>', 'kg m<sup>-1</sup> s<sup>-2</sup>', 'kg s<sup>-1</sup>'],
    "ans": 2,
    "distractors": ['multiplies by the radius instead of dividing by it, so the length ends up in the numerator',
                    'divides by the radius squared, as though the formula had r squared rather than r',
                    'correct',
                    'leaves the speed in the denominator, which sends the time exponent to minus two',
                    'cancels the lengths completely, treating the radius and the speed as having the same dimensions'],
    "profile": {
        "steps": [
            ("relate", "rearrange the formula so that the viscosity stands alone on one side"),
            ("relate", "substitute the base units of a newton, a metre and a metre per second"),
            ("solve", "cancel the lengths and the seconds, keeping track of the signs of the exponents"),
        ],
        "relations": ["&#951; = F / (6&#960; r v)",
                      "units of &#951; = N / (m &#215; m s<sup>-1</sup>) = N s m<sup>-2</sup>",
                      "N = kg m s<sup>-2</sup>, so the units are kg m<sup>-1</sup> s<sup>-1</sup>"],
        "insight": "The number 6&#960; carries no units, so the whole job is to divide the units of a force by the units of a length times a speed. Everything else is bookkeeping with exponents.",
        "shape": "units-consistency",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "dim", "got": "kg m s^-2 m^-1 m^-1 s", "want": "kg m^-1 s^-1"},
    "sol": '''<p><b>What is being tested.</b> Whether you can work out the units of a constant from the formula it appears in. This is the same skill as dimensional analysis, run in the direction of an unknown constant rather than an unknown combination.</p>
<p><b>Step 1 — rearrange for the viscosity.</b> The factor <code>6&#960;</code> is a pure number and has no units, so it can be ignored throughout:</p>
<div class="formula">&#951; = F / (6&#960; r v)</div>
<p><b>Step 2 — substitute the units.</b> A force is a newton, a radius is a metre, and a speed is a metre per second:</p>
<div class="formula">units of &#951; = N / (m &#215; m s<sup>-1</sup>)</div>
<p>Multiplying out the denominator, <code>m &#215; m s<sup>-1</sup></code> is <code>m<sup>2</sup> s<sup>-1</sup></code>. So</p>
<div class="formula">units of &#951; = N s m<sup>-2</sup></div>
<p><b>Step 3 — put the newton into base units.</b> A newton is the force that gives a kilogram an acceleration of one metre per second squared:</p>
<div class="formula">N = kg m s<sup>-2</sup>
units of &#951; = (kg m s<sup>-2</sup>)(s)(m<sup>-2</sup>)
          = kg m<sup>-1</sup> s<sup>-1</sup></div>
<p>The lengths give <code>1 &#8722; 2 = &#8722;1</code>, and the seconds give <code>&#8722;2 + 1 = &#8722;1</code>. So the viscosity has units of kilogram per metre per second.</p>
<p>So <b>Answer: C.</b></p>
<p><b>Checking the answer against what viscosity means.</b> Viscosity measures how much a fluid resists being sheared: it is a force per unit area divided by a velocity gradient, which is <code>(N m<sup>-2</sup>)/(s<sup>-1</sup>) = N s m<sup>-2</sup></code>. That is the same as the units found above, from a completely different starting point. Two independent routes agreeing is the strongest check available for a question of this kind, and it is worth knowing this second definition because it makes the answer memorable rather than merely computable.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>kg m s<sup>-1</sup></b> has the length in the numerator instead of the denominator. It comes from multiplying by the radius instead of dividing, which turns one of the two <code>m<sup>-1</sup></code> into an <code>m<sup>+1</sup></code>. The net length exponent is then <code>+1</code> rather than <code>&#8722;1</code>.</p>
<p>&middot; <b>kg m<sup>-2</sup> s<sup>-1</sup></b> divides by the radius squared, as though the formula contained <code>r<sup>2</sup></code>. Stokes' law contains a single power of the radius, and the difference between <code>r</code> and <code>r<sup>2</sup></code> is exactly the difference between these two options.</p>
<p>&middot; <b>kg m<sup>-1</sup> s<sup>-2</sup></b> leaves the speed in the denominator, so the seconds contribute <code>&#8722;2</code> from the newton and nothing from the speed to cancel it. The time exponent ends at <code>&#8722;2</code> instead of <code>&#8722;1</code>.</p>
<p>&middot; <b>kg s<sup>-1</sup></b> cancels the lengths completely. That happens if the radius and the speed are treated as carrying the same dimension, so that <code>m &#215; m s<sup>-1</sup></code> is read as <code>m<sup>2</sup> s<sup>-1</sup></code> but then the newton's single <code>m</code> is taken to cancel both of them. It is a bookkeeping slip rather than a conceptual one, and it is the sort of thing that a careful line-by-line cancellation prevents.</p>
<p><b>The trap.</b> Losing track of the sign of an exponent when the same unit appears in several places. The safe method is to collect each base unit separately and add its exponents, as done above, rather than to try to cancel by eye.</p>
<p><b>Relevant topics:</b> base and derived units; dimensional consistency; rearranging a formula for one quantity; the units of viscosity.</p>''',
    "trap": "Losing the sign of an exponent while cancelling, or treating the speed as dimensionless. Collecting each base unit separately and adding its exponents prevents it.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 15 -- B, kinematics.  A ball bouncing across water: three flights, each flatter.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 15, "id": "S04-15", "module": "B", "diff": 3,
    "topic": "A ball projected horizontally from a cliff and bouncing on the water: the total horizontal distance after three flights",
    "rel": [("B", "Horizontal and vertical motion are independent, and a bounce leaves the horizontal component of velocity unchanged"),
            ("B", "The time of a vertical flight is proportional to the vertical component of the launch velocity"),
            ("B", "A vertical fall from rest covers one half of g times the square of the time"),
            ("C", "Halving the vertical speed takes away three quarters of the kinetic energy of the vertical motion, which is why the later flights are shorter")],
    "key": ["projectile", "bounce", "independence", "proportional"],
    "stem": '<p>A ball is projected horizontally at 15 m/s from the top of a cliff 20 m above the sea. It bounces on the water, and at each bounce the vertical component of its velocity is halved and reversed while the horizontal component is unchanged. The figure shows the three flights, ending at the third bounce. {{FIG:s04-15}}</p><p>Taking g = 10 m/s<sup>2</sup>, what is the total horizontal distance the ball travels from the cliff top to the third bounce?</p>',
    "opts": ['60 m', '90 m', '45 m', '75 m', '150 m'],
    "ans": 3,
    "distractors": ['counts only the first two flights and forgets the third, which is still 15 m long',
                    'treats the bounce as perfectly elastic, so the second flight lasts as long as the first',
                    'halves the whole flight at the bounce rather than only the vertical part, so the second flight comes out at 15 m',
                    'correct',
                    'treats the bounce as perfectly elastic and counts all three flights at the first flight\'s length'],
    "profile": {
        "steps": [
            ("relate", "separate the launch into a horizontal component of 15 m/s and a vertical component of zero"),
            ("solve", "find the time of the first fall by putting 20 m into the free-fall distance equation"),
            ("solve", "multiply the horizontal speed by that time to get the first horizontal leg"),
            ("solve", "find the vertical speed at the first bounce, which is g times the fall time"),
            ("relate", "halve and reverse that vertical speed for the bounce, leaving the horizontal speed alone"),
            ("solve", "find the time of the second flight from its vertical launch speed"),
            ("solve", "multiply the horizontal speed by that time to get the second horizontal leg"),
            ("solve", "halve the vertical speed again and repeat once more for the third flight"),
            ("solve", "add the three horizontal legs"),
            ("check", "confirm the times are in the ratio 2 to 2 to 1 and that the horizontal speed never changes"),
        ],
        "relations": ["u horizontal = 15 m/s, u vertical = 0",
                      "20 = 0.5 &#215; 10 &#215; t squared, so t = 2.0 s and the first leg is 15 &#215; 2.0 = 30 m",
                      "vertical speed at the first bounce = 10 &#215; 2.0 = 20 m/s downward",
                      "after the bounce the vertical speed is 10 m/s upward, so the second flight lasts 2 &#215; 10 / 10 = 2.0 s",
                      "second leg = 15 &#215; 2.0 = 30 m; after the next bounce the vertical speed is 5.0 m/s, so the third flight lasts 1.0 s",
                      "third leg = 15 &#215; 1.0 = 15 m, and the total is 30 + 30 + 15 = 75 m"],
        "insight": "The bounce halves the vertical speed, so each flight time halves - but the horizontal speed is untouched, so the horizontal speed is the one thing that never changes. The second flight is as wide as the first and a quarter as tall; the third is half as wide again.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "15*(sqrt(2*20/10) + 2*((10*sqrt(2*20/10))/2)/10 + 2*(((10*sqrt(2*20/10))/2)/2)/10)", "want": "75"},
    "sol": '''<p><b>What is being tested.</b> Whether you keep the horizontal and vertical parts of a projectile separate right through a sequence of bounces, and whether you notice which of the two the bounce does <i>not</i> touch.</p>
<p><b>Step 1 — the launch.</b> The ball leaves the cliff top horizontally, so its velocity has only one component to begin with:</p>
<div class="formula">horizontal: 15 m/s
vertical: 0</div>
<p>The vertical motion starts from rest, exactly as if the ball had been dropped. The horizontal motion is unaffected by anything that happens vertically, and that separation is the whole basis of the question.</p>
<p><b>Step 2 — the time of the first fall.</b> The ball falls 20 m from rest under gravity:</p>
<div class="formula">s = 0.5 g t squared
20 = 0.5 &#215; 10 &#215; t squared = 5 t squared
t squared = 4, so t = 2.0 s</div>
<p><b>Step 3 — the first horizontal leg.</b> The horizontal speed is constant, so the distance is speed times time:</p>
<div class="formula">x1 = 15 &#215; 2.0 = 30 m</div>
<p><b>Step 4 — the vertical speed at the first bounce.</b> The ball has been accelerating downward for 2.0 s:</p>
<div class="formula">v = g t = 10 &#215; 2.0 = 20 m/s downward</div>
<p><b>Step 5 — what the bounce does.</b> The vertical component is halved and reversed, so it becomes 10 m/s upward. The horizontal component is untouched and is still 15 m/s. That asymmetry is the heart of the question: the bounce takes energy out of the vertical motion and leaves the horizontal motion exactly as it was.</p>
<p><b>Step 6 — the time of the second flight.</b> The ball leaves the water at 10 m/s upward and returns to the same level. Rising from 10 m/s to rest and falling back takes twice the time to reach the top:</p>
<div class="formula">time to the top = 10 / 10 = 1.0 s
t2 = 2 &#215; 1.0 = 2.0 s</div>
<p><b>Step 7 — the second horizontal leg.</b></p>
<div class="formula">x2 = 15 &#215; 2.0 = 30 m</div>
<p>So the second flight is <i>exactly as wide</i> as the first, and only a quarter as tall — it rose 5 m where the first fell 20 m. That looks wrong until you remember that the horizontal speed never changed, so the same time in the air must give the same distance across.</p>
<p><b>Step 8 — the third flight.</b> The ball returns to the water at 10 m/s downward, and the bounce halves that again, so it leaves at 5.0 m/s upward:</p>
<div class="formula">t3 = 2 &#215; 5.0 / 10 = 1.0 s</div>
<p><b>Step 9 — the third horizontal leg.</b></p>
<div class="formula">x3 = 15 &#215; 1.0 = 15 m</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 10 — add the legs and check the pattern.</b></p>
<div class="formula">x total = 30 + 30 + 15 = 75 m</div>
<p>The three flight times are 2.0 s, 2.0 s and 1.0 s, in the ratio 2 to 2 to 1, which is exactly the ratio of the vertical launch speeds 20, 10 and 5 — the flight time is proportional to the vertical speed and to nothing else. The horizontal speed is 15 m/s throughout, so the distances are in the same ratio as the times. Every number in the answer comes from those two facts, and they can be checked independently: the ball is in the air for 5.0 s altogether, and 15 m/s for 5.0 s is 75 m.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>60 m</b> counts the first two flights and forgets the third. It is the most likely wrong answer, because after two identical 30 m legs it is natural to feel that the pattern has been established and to stop. The ball bounces a third time and travels another 15 m.</p>
<p>&middot; <b>90 m</b> treats the bounce as perfectly elastic. If the vertical speed came back unchanged at 20 m/s the second flight would last 4.0 s and cover 60 m, giving 30 + 60. The question says the vertical component is halved, and that is the single fact this option ignores.</p>
<p>&middot; <b>45 m</b> halves the whole flight at the bounce instead of only the vertical part. That would make the second leg 15 m rather than 30 m, and it double-counts the error by also stopping there. Halving the vertical speed halves the <i>time</i>; the horizontal distance then follows from a horizontal speed that has not changed at all.</p>
<p>&middot; <b>150 m</b> makes the same elastic-bounce mistake as 90 m but carries it through all three flights, giving three legs of 30, 60 and 60 m.</p>
<p><b>The trap.</b> Assuming that a bounce which clearly removes energy must shorten the next flight. It does shorten the flight in <i>time</i> and in <i>height</i>, but not in horizontal distance, because the horizontal speed is the one quantity the bounce never touches. The figure is drawn to scale for exactly this reason: the second arc is the same width as the first and visibly flatter, and the third is half as wide.</p>
<p><b>Relevant topics:</b> projectile motion; independence of horizontal and vertical motion; free fall from rest; the time of flight of a vertical launch; velocity-time reasoning without a calculator.</p>''',
    "trap": "Assuming the bounce must shorten the next flight in horizontal distance. It halves the vertical speed and so halves the flight time, but the horizontal speed is unchanged, so the second leg is the same 30 m as the first.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 16 -- C, forces.  A sign hanging from two wires at unequal angles.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 16, "id": "S04-16", "module": "C", "diff": 3,
    "topic": "A sign hanging from two wires at unequal angles: which wire carries more of the load",
    "rel": [("C", "Resolving the tensions horizontally, where the two horizontal components must cancel"),
            ("C", "Resolving vertically, where the two vertical components must carry the weight"),
            ("A", "Eliminating one unknown between two simultaneous equations")],
    "key": ["tension", "sign", "resolve", "equilibrium"],
    "stem": '<p>The figure shows a sign of weight <code>W</code> hanging from two wires attached to a ceiling. The left-hand wire makes 60&#176; with the vertical and the right-hand one makes 30&#176; with the vertical. {{FIG:s04-16}}</p><p>Which expression gives the tension in the right-hand wire?</p>',
    "opts": ['W / 2', 'W&#8730;3/2', 'W', '2W', '2W / &#8730;3'],
    "ans": 1,
    "distractors": ['gives the tension in the left-hand wire, which is the smaller of the two',
                    'correct',
                    'assumes each wire carries the whole weight, since the arrangement is not symmetric',
                    'resolves the weight against one wire\'s vertical component alone and ignores the other wire',
                    'balances the weight against the horizontal component of the tension instead of the vertical one'],
    "profile": {
        "steps": [
            ("relate", "resolve the two tensions horizontally, where their components must cancel because the sign is in equilibrium"),
            ("relate", "resolve vertically, where the two components must add to the weight"),
            ("solve", "eliminate one tension between the two equations and solve for the other"),
            ("check", "put the answer back and confirm the vertical components do add to W and that the steeper wire carries less"),
        ],
        "relations": ["T1 sin 60&#176; = T2 sin 30&#176;",
                      "T1 cos 60&#176; + T2 cos 30&#176; = W",
                      "T2 = W sin 60&#176; / sin 90&#176; = W&#8730;3/2"],
        "insight": "The two horizontal components must cancel, so the tension is inversely related to the sine of the angle from the vertical. The wire closer to the vertical carries the larger share of the weight, which is the opposite of what a guess usually produces.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "sin(pi/3)/sin(pi/2)", "want": "sqrt(3)/2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can handle two unknown tensions with two equations, and whether you can say in advance which wire is doing more work. The second of those is what separates a confident answer from a lucky one.</p>
<p><b>Step 1 — resolve horizontally.</b> The sign does not move sideways, so the horizontal components of the two tensions must cancel. Both angles in the figure are measured from the vertical, so the horizontal component of a tension <code>T</code> is <code>T sin&#952;</code>:</p>
<div class="formula">T1 sin 60&#176; = T2 sin 30&#176;</div>
<p>Since <code>sin 60&#176; = &#8730;3/2</code> and <code>sin 30&#176; = 1/2</code>, this says <code>T1 &#215; 0.866 = T2 &#215; 0.5</code>, so <code>T1</code> is a little more than half of <code>T2</code>. The wire that hangs closer to the vertical carries more, and this line is where that becomes visible.</p>
<p><b>Step 2 — resolve vertically.</b> The vertical components must add to the weight, since the sign does not accelerate:</p>
<div class="formula">T1 cos 60&#176; + T2 cos 30&#176; = W</div>
<p><b>Step 3 — eliminate one tension.</b> From step 1, <code>T1 = T2 sin 30&#176; / sin 60&#176;</code>. Substituting and putting the two terms over a common denominator:</p>
<div class="formula">T2 (sin 30&#176; cos 60&#176; / sin 60&#176; + cos 30&#176;) = W
T2 (sin 30&#176; cos 60&#176; + cos 30&#176; sin 60&#176;) / sin 60&#176; = W</div>
<p>The bracket is the expansion of <code>sin(30&#176; + 60&#176;)</code>, which is <code>sin 90&#176; = 1</code>. So the whole expression collapses:</p>
<div class="formula">T2 = W sin 60&#176; / sin 90&#176; = W&#8730;3/2</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 4 — check by finding the other tension.</b> By the same symmetry, <code>T1 = W sin 30&#176; / sin 90&#176; = W/2</code>. Now check the vertical resolution:</p>
<div class="formula">T1 cos 60&#176; + T2 cos 30&#176; = (W/2)(1/2) + (W&#8730;3/2)(&#8730;3/2)
              = W/4 + 3W/4
              = W</div>
<p>That is exactly the weight, so the two tensions are consistent. Notice the pleasing pattern: each tension is the weight times the sine of the <i>other</i> wire's angle from the vertical. The wire at 60&#176; gets <code>sin 30&#176; = 1/2</code> of the weight, and the wire at 30&#176; gets <code>sin 60&#176;</code>. The steeper-to-the-vertical wire does less work.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>W/2</b> is the tension in the left-hand wire. It is a correct number for this arrangement, just for the wrong wire. Since the two angles are different, the two tensions are different, and picking the wrong one is easy if you have not decided in advance which wire should carry more.</p>
<p>&middot; <b>W</b> assumes each wire carries the whole weight. That would be the answer if the sign were held by one wire at a time, or if the two wires were pulling in the same direction. They are not: each has a horizontal component that the other cancels, so neither can carry the whole weight vertically without breaking the horizontal balance.</p>
<p>&middot; <b>2W</b> resolves the weight against one wire's vertical component alone, <code>T cos 60&#176; = W</code>, giving <code>T = 2W</code>. That ignores the other wire entirely. It also breaks the horizontal balance, so it cannot be right even before the arithmetic is checked.</p>
<p>&middot; <b>2W/&#8730;3</b> balances the weight against the horizontal component instead of the vertical one, <code>T sin 60&#176; = W</code>. A horizontal component cannot support a vertical load; the two directions are independent and only the vertical components can hold the sign up.</p>
<p><b>The trap.</b> Assuming the wire at the steeper angle to the ceiling carries more. Angles here are measured from the vertical, and the wire that is more nearly vertical carries more of the load. Reading the figure carefully — the dashed verticals are drawn for exactly this reason — settles which angle is which.</p>
<p><b>Relevant topics:</b> equilibrium of a point; resolving forces into components; two unknown tensions and two equations; the compound-angle identity sin(A + B).</p>''',
    "trap": "Assuming the wire at the shallower angle carries more, or balancing the weight against a horizontal component. The wire closer to the vertical carries more, and only vertical components support a vertical load.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 17 -- D, circular motion.  A conical pendulum: the period and the effective length.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 17, "id": "S04-17", "module": "D", "diff": 3,
    "topic": "A conical pendulum: the period in terms of the string length and the cone angle",
    "rel": [("D", "The horizontal force on a body in circular motion is the centripetal force"),
            ("D", "Resolving the tension in a string that is not vertical"),
            ("A", "Recognising the radius of the circle as a length that is not the string length")],
    "key": ["conical", "pendulum", "period", "height"],
    "stem": '<p>A small bob is attached to a light string of length <code>L</code> and moves in a horizontal circle, the string making a constant angle <code>&#952;</code> with the vertical throughout the motion. Which expression gives the period of the motion?</p>',
    "opts": ['2&#960;&#8730;(L cos&#952; / g)', '2&#960;&#8730;(L / g)', '2&#960;&#8730;(L / (g cos&#952;))', '2&#960;&#8730;(g / (L cos&#952;))', '2&#960;&#8730;(L sin&#952; / g)'],
    "ans": 0,
    "distractors": ['correct',
                    'uses the string length as though the pendulum hung vertically, ignoring the shortening of the effective length',
                    'inverts the cosine, which makes the effective length longer than the string itself',
                    'inverts the whole ratio, so the period would grow as the string shortens',
                    'takes the radius of the circle as the effective length, which has the wrong dimensions as well as the wrong value'],
    "profile": {
        "steps": [
            ("relate", "identify the radius of the circle as L sin(theta) and the vertical height as L cos(theta)"),
            ("relate", "resolve the tension vertically, where it balances the weight"),
            ("relate", "resolve the tension horizontally, where it supplies the centripetal force"),
            ("solve", "divide one equation by the other so the tension and the mass both cancel"),
            ("solve", "take the period as two pi divided by the angular frequency"),
            ("check", "confirm the answer reduces to the ordinary pendulum when the angle tends to zero, and that the period does not contain the mass"),
        ],
        "relations": ["T cos&#952; = m g", "T sin&#952; = m &#969;<sup>2</sup> L sin&#952;",
                      "&#969;<sup>2</sup> = g / (L cos&#952;)",
                      "period = 2&#960; / &#969; = 2&#960;&#8730;(L cos&#952; / g)"],
        "insight": "The radius of the circle is L sin(theta), not L, and the vertical height of the bob below the ceiling is L cos(theta). The period depends on that vertical height alone, exactly as for an ordinary pendulum.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "(T*sin(th))/(T*cos(th))", "want": "tan(th)"},
    "sol": '''<p><b>What is being tested.</b> Whether you can resolve forces in a circle whose radius is not the string length, and whether you notice that the answer has the same shape as an ordinary pendulum's.</p>
<p><b>Step 1 — the geometry.</b> This is where the question is decided. The string has length <code>L</code> and makes an angle <code>&#952;</code> with the vertical, so the radius of the circle the bob travels in is <code>L sin&#952;</code>, and the vertical height of the bob below the point of support is <code>L cos&#952;</code>. Neither of those is <code>L</code>.</p>
<p><b>Step 2 — resolve vertically.</b> The bob does not move up or down, so the vertical component of the tension carries the weight:</p>
<div class="formula">T cos&#952; = m g</div>
<p><b>Step 3 — resolve horizontally.</b> The horizontal component of the tension is the only horizontal force, so it supplies the whole centripetal force. The radius is <code>L sin&#952;</code>:</p>
<div class="formula">T sin&#952; = m &#969;<sup>2</sup> (L sin&#952;)</div>
<p><b>Step 4 — divide the two equations.</b> Dividing the horizontal one by the vertical one cancels both <code>T</code> and <code>m</code>, and also cancels <code>sin&#952;</code>:</p>
<div class="formula">(T sin&#952;) / (T cos&#952;) = (m &#969;<sup>2</sup> L sin&#952;) / (m g)
tan&#952; = &#969;<sup>2</sup> L sin&#952; / g
&#969;<sup>2</sup> = g / (L cos&#952;)</div>
<p><b>Step 5 — the period.</b> The period is <code>2&#960;</code> divided by the angular frequency:</p>
<div class="formula">period = 2&#960; / &#969; = 2&#960;&#8730;(L cos&#952; / g)</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 6 — check the limiting case and the structure.</b> As <code>&#952; &#8594; 0</code>, the cosine tends to 1 and the expression becomes <code>2&#960;&#8730;(L/g)</code>, which is exactly the period of an ordinary small-angle pendulum. That is a strong check: a conical pendulum with a very small cone angle is almost an ordinary pendulum, so the two formulae must join up. Notice also that the mass does not appear anywhere in the answer, which is right — a pendulum's period does not depend on how heavy the bob is. And the answer can be written <code>2&#960;&#8730;(h/g)</code> where <code>h = L cos&#952;</code> is the vertical height: the period depends only on how far the bob hangs below the support, not on how long the string is or how wide the circle is.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2&#960;&#8730;(L/g)</b> is the ordinary pendulum, using the string length as the effective length. It is right only when the string is vertical, and it ignores the fact that the effective length here is shorter than <code>L</code>.</p>
<p>&middot; <b>2&#960;&#8730;(L/(g cos&#952;))</b> inverts the cosine. Since <code>cos&#952;</code> is less than one, this makes the effective length longer than the string itself, which is impossible: the bob hangs closer to the ceiling than the full string length, not further away.</p>
<p>&middot; <b>2&#960;&#8730;(g/(L cos&#952;))</b> inverts the whole fraction. This gives a period that grows as the string shortens, which is the wrong way round; a shorter pendulum is faster, as anyone who has adjusted one knows.</p>
<p>&middot; <b>2&#960;&#8730;(L sin&#952;/g)</b> takes the radius of the circle as the effective length. The dimensions of this one are actually fine, so a dimensional check will not catch it — but it fails the limiting case, because as <code>&#952; &#8594; 0</code> the radius tends to zero and the period would tend to zero, when in fact it tends to the ordinary pendulum's period.</p>
<p><b>The trap.</b> Substituting <code>L</code> for the radius of the circle. The string is tilted, so the circle the bob travels in is smaller than the string, and using <code>L</code> as the radius mixes up the length of the string with the size of the orbit. The limiting case check is the reliable way to catch it.</p>
<p><b>Relevant topics:</b> circular motion and centripetal force; resolving forces in two directions; the conical pendulum; limiting cases as a check on an algebraic answer.</p>''',
    "trap": "Using the string length as the radius of the circle. The bob travels in a circle of radius L sin(theta), and the period depends only on the vertical height L cos(theta).",
},

# ═════════════════════════════════════════════════════════════════════════════
# 18 -- E, materials.  Two wires of the same material and different diameters.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 18, "id": "S04-18", "module": "E", "diff": 2,
    "topic": "Two wires of the same material and length but different diameters, under the same load",
    "rel": [("E", "The extension of a wire in terms of the load, the length, the cross-sectional area and Young's modulus"),
            ("E", "The cross-sectional area of a circular wire in terms of its diameter"),
            ("A", "Following an inverse-square relationship through a change in one variable")],
    "key": ["youngsmodulus", "extension", "diameter", "area"],
    "stem": '<p>Two wires are made of the same material and have the same length. The second wire has twice the diameter of the first. The same load is hung on each. What is the ratio of the extension of the second wire to that of the first?</p>',
    "opts": ['1/2', '1', '2', '4', '1/4'],
    "ans": 4,
    "distractors": ['takes the extension to go as the diameter rather than as its square',
                    'assumes the same load gives the same extension whatever the cross-section',
                    'inverts the ratio, so the thicker wire would stretch more',
                    'squares the ratio the wrong way up, taking the extension to grow as the square of the diameter',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "write the extension in terms of the load, the length, the area and Young's modulus"),
            ("relate", "note which of those quantities are the same for the two wires"),
            ("solve", "reduce the extension to a proportionality in the cross-sectional area alone"),
            ("solve", "express the area in terms of the diameter and follow the inverse square through"),
            ("check", "confirm the thicker wire stretches less, and by the factor the square of two predicts"),
        ],
        "relations": ["e = F L / (A E)", "A = &#960; d<sup>2</sup> / 4", "e &#8733; 1 / d<sup>2</sup>"],
        "insight": "The extension is inversely proportional to the cross-sectional area, and the area goes as the square of the diameter. So doubling the diameter divides the extension by four, not by two.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(1/2.0)**2", "want": "0.25"},
    "sol": '''<p><b>What is being tested.</b> Whether you carry the square through from the diameter to the area. Everything else in this question is standard; the whole of it is decided by remembering that area goes as the square of a length.</p>
<p><b>Step 1 — the extension of a wire.</b> A wire of original length <code>L</code>, cross-sectional area <code>A</code> and Young's modulus <code>E</code>, carrying a load <code>F</code>, extends by</p>
<div class="formula">e = F L / (A E)</div>
<p><b>Step 2 — what is the same for both wires.</b> The material is the same, so <code>E</code> is the same. The lengths are the same. The loads are the same. So the only quantity that differs between the two wires is the area:</p>
<div class="formula">e &#8733; 1 / A</div>
<p><b>Step 3 — the area in terms of the diameter.</b> A wire is circular in cross-section, so</p>
<div class="formula">A = &#960; d<sup>2</sup> / 4     so     A &#8733; d<sup>2</sup></div>
<p>Substituting into the proportionality for the extension:</p>
<div class="formula">e &#8733; 1 / d<sup>2</sup></div>
<p><b>Step 4 — put the ratio in.</b> The second wire has twice the diameter, so</p>
<div class="formula">e2 / e1 = (d1 / d2)<sup>2</sup> = (1/2)<sup>2</sup> = 1/4</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 5 — check that the direction and the size are both right.</b> The thicker wire must stretch less, because the same load is spread over more material, and the answer is less than one, so the direction is right. The size is right too, and it is worth seeing why it is a quarter rather than a half. Doubling the diameter doubles the wire across, but it also doubles it the other way, so the cross-sectional area is four times as large. The load is shared over four times as much material, so the strain is a quarter as great. If the question had said "twice the cross-sectional area" the answer would have been a half; it said twice the diameter, and that is a different thing.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/2</b> is the answer to the question as it would be if the areas were in the ratio of the diameters. It is the most likely wrong answer, because the diameter is the quantity actually named in the stem and it is natural to use it directly.</p>
<p>&middot; <b>1</b> assumes the extension does not depend on the cross-section at all. That would mean a thin wire and a thick one of the same material stretch by the same amount under the same load, which is plainly not what happens.</p>
<p>&middot; <b>2</b> inverts the ratio, making the thicker wire stretch twice as much. A thicker wire is stiffer, not softer, so this contradicts the everyday behaviour of wires and cables.</p>
<p>&middot; <b>4</b> squares the ratio but the wrong way up, taking the extension to grow as the square of the diameter. It gets the exponent right and the direction wrong, which is the most instructive of the wrong answers: it shows that knowing there is a square is not enough, and that the direction of the proportionality has to be worked out.</p>
<p><b>The trap.</b> Reading "twice the diameter" as "twice the area". The two differ by a factor of four, and since the extension is inversely proportional to the area, that factor of four lands directly in the answer.</p>
<p><b>Relevant topics:</b> stress, strain and Young's modulus; the extension of a loaded wire; the area of a circle; inverse-square proportionalities.</p>''',
    "trap": "Reading twice the diameter as twice the area. The area goes as the square of the diameter, so the extension falls by a factor of four.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 19 -- F, waves.  The resonances of a pipe closed at one end.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 19, "id": "S04-19", "module": "F", "diff": 3,
    "topic": "A pipe closed at one end: finding its length from two successive resonances",
    "rel": [("F", "A pipe closed at one end resonates at odd multiples of its fundamental frequency"),
            ("F", "The relation between frequency, wavelength and wave speed"),
            ("A", "Deciding from a ratio of two frequencies which harmonics they are")],
    "key": ["resonance", "closedpipe", "wavelength", "oddharmonics"],
    "stem": '<p>The figure shows the three lowest standing-wave patterns in a pipe closed at one end and open at the other. {{FIG:s04-19}}</p><p>The pipe resonates at 400 Hz and at the next higher resonance at 1200 Hz. Taking the speed of sound in air to be 340 m/s, what is the length of the pipe?</p>',
    "opts": ['0.11 m', '0.43 m', '0.21 m', '0.85 m', '1.7 m'],
    "ans": 2,
    "distractors": ['divides the wavelength by eight, treating the pipe as closed at both ends',
                    'takes the pipe to fit half a wavelength, which is the condition for a pipe open at both ends',
                    'correct',
                    'quotes the wavelength as the length of the pipe',
                    'takes the pipe to fit a whole wavelength'],
    "profile": {
        "steps": [
            ("relate", "recognise from the ratio of the two frequencies that they are successive odd harmonics"),
            ("relate", "use the fundamental with the quarter-wavelength condition for a pipe closed at one end"),
            ("solve", "find the wavelength from the wave speed and the fundamental frequency"),
            ("solve", "divide the wavelength by four to get the length"),
            ("check", "confirm the length is a sensible size for a pipe and that the next resonance would be at five times the fundamental"),
        ],
        "relations": ["f1 = v / (4 L)", "&#955; = v / f1", "L = &#955; / 4"],
        "insight": "A pipe closed at one end fits a quarter wavelength, so its resonances are at odd multiples of the fundamental. The ratio 1200 to 400 is 3, which identifies them as the first and second resonances rather than as a fundamental and its octave.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "340/(4*400)", "want": "0.2125"},
    "sol": '''<p><b>What is being tested.</b> Whether you know the pattern of resonances for a pipe closed at one end, and whether you can identify which resonances the two given frequencies are. The figure shows the pattern: a quarter wavelength, then three quarters, then five quarters.</p>
<p><b>Step 1 — identify the two resonances.</b> The ratio of the two frequencies is 1200/400 = 3. A pipe closed at one end resonates at odd multiples of its fundamental, so its successive resonances are in the ratio 1 : 3 : 5 : 7. The two frequencies given are therefore the fundamental and the second resonance, not a fundamental and its octave:</p>
<div class="formula">f1 = 400 Hz      f2 = 3 f1 = 1200 Hz</div>
<p>This step is where the question is decided. If the pipe were open at both ends the resonances would be in the ratio 1 : 2 : 3, and 400 Hz and 1200 Hz would be the first and third, which would give a different answer. The figure settles which case this is.</p>
<p><b>Step 2 — the condition for the fundamental.</b> At the closed end there must be a node, because the air cannot move against the end. At the open end there must be an antinode, because the air is free to move. The longest wave that fits that pattern is a quarter of a wavelength:</p>
<div class="formula">L = &#955; / 4</div>
<p><b>Step 3 — find the wavelength.</b> From the wave equation with the fundamental frequency:</p>
<div class="formula">&#955; = v / f1 = 340 / 400 = 0.85 m</div>
<p><b>Step 4 — the length.</b></p>
<div class="formula">L = &#955; / 4 = 0.85 / 4 = 0.21 m</div>
<p>So <b>Answer: C.</b></p>
<p><b>Step 5 — check the answer.</b> A pipe 21 cm long is a plausible size for a laboratory resonance tube or a small organ pipe, and the numbers are self-consistent: 340/(4 &#215; 0.21) is very close to 400 Hz, which is where we started. The pattern also predicts a third resonance at <code>5f1 = 2000 Hz</code>, and at that frequency the pipe holds five quarters of a wavelength, which is exactly five times the quarter-wave length of the fundamental. Nothing is left over.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>0.11 m</b> is <code>&#955;/8</code>, which is what you get by treating the pipe as closed at both ends. A pipe closed at both ends has nodes at both ends and fits half a wavelength at its fundamental; the quarter-wavelength condition belongs to a pipe closed at <i>one</i> end.</p>
<p>&middot; <b>0.43 m</b> is <code>&#955;/2</code>, the condition for a pipe open at both ends. It is a genuine standing-wave condition and it is the right answer to a different question — which is exactly why the figure is drawn showing the closed end.</p>
<p>&middot; <b>0.85 m</b> is the wavelength itself. It appears in the working and it is easy to quote it as the answer if the last division is skipped.</p>
<p>&middot; <b>1.7 m</b> is twice the wavelength, or equivalently <code>v/f1 &#215; 2</code>. It corresponds to a pipe fitting a whole wavelength, which is not the fundamental of any pipe with a closed end.</p>
<p><b>The trap.</b> Assuming the two given frequencies are a fundamental and its octave, that is a ratio of 2. The ratio here is 3, which is the signature of a pipe closed at one end, and recognising it is what makes the rest of the question straightforward.</p>
<p><b>Relevant topics:</b> stationary waves in pipes; nodes and antinodes at closed and open ends; the harmonic series of a closed pipe; the wave equation.</p>''',
    "trap": "Assuming the two frequencies are a fundamental and its octave. Their ratio is 3, which identifies a pipe closed at one end with its odd-harmonic series.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 20 -- G, optics.  The critical angle for a material of refractive index root two.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 20, "id": "S04-20", "module": "G", "diff": 2,
    "topic": "The critical angle at a boundary with air for a material of refractive index root two",
    "rel": [("G", "The critical angle as the angle of incidence whose refracted ray grazes the boundary"),
            ("G", "Snell's law applied at the boundary between a denser and a less dense medium"),
            ("A", "Recognising the exact values of the sine and cosine of the common angles")],
    "key": ["criticalangle", "snell", "limiting", "exactvalues"],
    "stem": '<p>A transparent material has refractive index <code>&#8730;2</code>. What is the largest angle of incidence for which light travelling in the material can emerge into the air?</p>',
    "opts": ['30&#176;', '35.3&#176;', '54.7&#176;', '45&#176;', '90&#176;'],
    "ans": 3,
    "distractors": ['takes the sine of the critical angle to be 1/n<sup>2</sup> rather than 1/n',
                    'uses tan &#952; = 1/n instead of sin &#952; = 1/n',
                    'quotes the Brewster angle, where the reflected ray is polarised, not where total internal reflection begins',
                    'correct',
                    'takes the grazing angle itself as the critical angle'],
    "profile": {
        "steps": [
            ("relate", "identify the limiting case: the refracted ray leaves along the boundary at 90 degrees"),
            ("relate", "apply Snell's law with the angle of refraction set to 90 degrees"),
            ("solve", "put in the refractive index and recognise the sine of the answer"),
            ("check", "compare the answer with the known critical angles of water and diamond, which bracket it"),
        ],
        "relations": ["n sin &#952;c = 1 &#215; sin 90&#176;", "sin &#952;c = 1 / n = 1 / &#8730;2", "&#952;c = 45&#176;"],
        "insight": "The largest angle for which light can escape is the one whose refracted ray just grazes the surface. Setting the angle of refraction to 90 degrees in Snell's law turns the problem into a single line.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "degrees(asin(1/sqrt(2)))", "want": "45"},
    "sol": '''<p><b>What is being tested.</b> Whether you can set up the critical-angle condition from scratch and whether you recognise an exact sine when you meet one. The material's index was chosen so that the answer is exact.</p>
<p><b>Step 1 — the limiting case.</b> Light travelling in a dense medium and arriving at a boundary with air can leave, or it can be reflected back. As the angle of incidence grows, the refracted ray bends further and further away from the normal. The largest angle of incidence for which it can still leave at all is the one at which the refracted ray runs along the boundary — that is, at 90&#176; to the normal. Beyond that angle there is no refracted ray, and all the light is reflected. So the question is asking for the critical angle.</p>
<p><b>Step 2 — Snell's law with that limit.</b> Taking air to have a refractive index of 1, and putting the angle of refraction equal to 90&#176;:</p>
<div class="formula">n sin &#952;c = 1 &#215; sin 90&#176;
&#8730;2 sin &#952;c = 1</div>
<p><b>Step 3 — solve.</b></p>
<div class="formula">sin &#952;c = 1 / &#8730;2</div>
<p>Rationalising is not necessary; the important thing is to recognise this value. <code>1/&#8730;2</code> is <code>&#8730;2/2</code>, which is the sine of 45&#176;. So</p>
<div class="formula">&#952;c = 45&#176;</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 4 — check the answer is sensible.</b> Water has a refractive index of about 4/3, and its critical angle is about 49&#176;; diamond has an index of 2.4 and a critical angle of about 25&#176;. An index of 1.41 sits between those, so a critical angle of 45&#176; fits the pattern: a larger index means a smaller critical angle, because the light has to work harder to escape. The answer is also in the range 0 to 90&#176; that any angle of incidence must occupy. Both checks pass.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>30&#176;</b> comes from taking <code>sin &#952;c = 1/n<sup>2</sup></code> rather than <code>1/n</code>. For <code>n = &#8730;2</code> that is 1/2, whose sine is 30&#176;. It is a plausible-looking number and it is off by the whole of the square root.</p>
<p>&middot; <b>35.3&#176;</b> comes from using <code>tan &#952; = 1/n</code> instead of <code>sin &#952; = 1/n</code>. The tangent of 35.3&#176; is 0.707, which is indeed <code>1/&#8730;2</code>, so the arithmetic is internally consistent — but Snell's law is a statement about sines, not tangents, and substituting the wrong trigonometric function gives a wrong angle that is hard to spot because the number itself is right for the function used.</p>
<p>&middot; <b>54.7&#176;</b> is the Brewster angle, <code>arctan n</code>. At that angle the reflected light is completely polarised in the plane of the surface. It is a real and important angle, and it is not the critical angle; the two are often confused because both are found from the refractive index with a single trigonometric function.</p>
<p>&middot; <b>90&#176;</b> is the grazing angle. At an angle of incidence of 90&#176; the light would be travelling along the surface and no light would enter the medium at all. It is the limit of the refracted ray, not the limit of the incident ray.</p>
<p><b>The trap.</b> Using the wrong trigonometric function, or the wrong power of the refractive index. The condition is <code>sin &#952;c = 1/n</code> and nothing else, and it is worth deriving it from Snell's law each time rather than trying to recall it, because the derivation takes one line and the memory is unreliable.</p>
<p><b>Relevant topics:</b> total internal reflection; the critical angle; Snell's law and its limiting case; exact values of the sine and cosine of 30&#176;, 45&#176; and 60&#176;.</p>''',
    "trap": "Using tan instead of sin, or squaring the refractive index. The condition is sin(theta-c) = 1/n, and it follows from Snell's law in one line.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 21 -- H, circuits.  A series resistor with a parallel pair.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 21, "id": "S04-21", "module": "H", "diff": 2,
    "topic": "A series resistor feeding a parallel pair: the current drawn from the battery",
    "rel": [("H", "Reducing a parallel pair to a single equivalent resistance"),
            ("H", "Adding resistances in series once the network has been reduced"),
            ("A", "Working through a network in stages rather than trying to see the whole answer at once")],
    "key": ["seriesparallel", "reduction", "current", "network"],
    "stem": '<p>A battery of emf 6.0 V and negligible internal resistance is connected to a 2.0 &#937; resistor in series with a parallel combination of a 6.0 &#937; and a 3.0 &#937; resistor. What is the current drawn from the battery?</p>',
    "opts": ['0.75 A', '1.0 A', '2.0 A', '3.0 A', '1.5 A'],
    "ans": 4,
    "distractors": ['adds all three resistances in series, treating the network as a single loop of 8.0 &#937;',
                    'uses only the 6.0 &#937; resistor of the parallel pair as the whole circuit resistance',
                    'uses the parallel pair alone, ignoring the 2.0 &#937; resistor in series with it',
                    'uses the 2.0 &#937; series resistor alone as the whole circuit resistance',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "reduce the parallel pair to a single equivalent resistance, using reciprocals"),
            ("relate", "add that equivalent resistance to the series resistor, because the same current passes through both"),
            ("solve", "divide the emf by the total resistance to get the current"),
            ("check", "confirm the total resistance is less than the sum of all three but more than the parallel pair alone"),
        ],
        "relations": ["1 / Rp = 1/6.0 + 1/3.0", "R total = Rp + 2.0",
                      "I = E / R total = 6.0 / 4.0 = 1.5 A"],
        "insight": "A network is reduced one stage at a time: the parallel pair becomes a single resistance, and only then can it be added to the series resistor. Trying to do both in one step is where the arithmetic goes wrong.",
        "shape": "circuit-reduction",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "6.0/(2.0 + 1/(1/6.0 + 1/3.0))", "want": "1.5"},
    "sol": '''<p><b>What is being tested.</b> Whether you can reduce a network in the right order. There is no subtle physics here — the whole question is method.</p>
<p><b>Step 1 — reduce the parallel pair.</b> The 6.0 &#937; and 3.0 &#937; resistors are in parallel, so their reciprocals add:</p>
<div class="formula">1 / Rp = 1/6.0 + 1/3.0
     = 1/6.0 + 2/6.0
     = 3/6.0
     = 1/2.0</div>
<p>So <code>Rp = 2.0 &#937;</code>. It is worth noting at once that this is smaller than either of the two resistors in the pair, which is always true of a parallel combination and is a useful check.</p>
<p><b>Step 2 — add the series resistor.</b> The parallel pair is in series with the 2.0 &#937; resistor, so the same current flows through both and their resistances simply add:</p>
<div class="formula">R total = Rp + 2.0
       = 2.0 + 2.0
       = 4.0 &#937;</div>
<p><b>Step 3 — the current.</b> With an emf of 6.0 V and a total resistance of 4.0 &#937;:</p>
<div class="formula">I = E / R total = 6.0 / 4.0 = 1.5 A</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 4 — check the bounds.</b> The total resistance must be less than the sum of all three resistors, 11 &#937;, because two of them are in parallel and a parallel combination is smaller than either. It must also be more than the parallel pair alone, 2.0 &#937;, because the 2.0 &#937; series resistor is added to it. The value 4.0 &#937; lies between those bounds, so the reduction has been done in the right order. If the answer had come out below 2.0 &#937; or above 11 &#937;, something would have gone wrong with the order of operations rather than with the arithmetic.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>0.75 A</b> adds all three resistances in series, 2.0 + 6.0 + 3.0 = 11 &#937;... except that 6.0/8.0 = 0.75, which corresponds to a total of 8.0 &#937;. That is what you get by adding the series resistor to the parallel pair as though the pair were in series with each other too, 2.0 + 6.0 or 2.0 + 3.0 = 8.0 or 5.0. Either way it treats a parallel pair as a series pair.</p>
<p>&middot; <b>1.0 A</b> uses only the 6.0 &#937; resistor as the whole circuit resistance, 6.0/6.0 = 1.0 A. It ignores both the other resistors.</p>
<p>&middot; <b>2.0 A</b> uses the parallel pair alone, 6.0/2.0 = 3.0 A — no, that gives 3.0 A. Let me be careful: 6.0/3.0 = 2.0 A corresponds to a total resistance of 3.0 &#937;. That is the 3.0 &#937; resistor of the pair taken alone. It is a number from the stem used as though it were the whole answer.</p>
<p>&middot; <b>3.0 A</b> uses the parallel pair alone, ignoring the 2.0 &#937; resistor in series with it: 6.0/2.0 = 3.0 A. This is the most instructive of the wrong answers, because the parallel pair has been reduced correctly and then the series resistor has simply been forgotten. Reduction in stages only helps if every stage is carried out.</p>
<p><b>The trap.</b> Adding the series resistor before reducing the pair, or reducing the pair and then forgetting to add. The reliable habit is to work from the inside out, redrawing the circuit after each stage until only one resistance is left.</p>
<p><b>Relevant topics:</b> resistors in series and in parallel; reducing a network in stages; Ohm's law for a whole circuit; internal resistance (here negligible).</p>''',
    "trap": "Reducing the parallel pair correctly and then forgetting to add the series resistor, or treating the pair as if it were in series. Work from the inside out.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 22 -- I, capacitors.  Charge sharing between a charged and an uncharged capacitor.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 22, "id": "S04-22", "module": "I", "diff": 3,
    "topic": "Charge sharing between a charged and an uncharged capacitor: the common potential difference",
    "rel": [("I", "The charge on a capacitor as the product of its capacitance and its potential difference"),
            ("I", "Charge is conserved when two capacitors are connected, but energy is not"),
            ("H", "Capacitors in parallel add their capacitances")],
    "key": ["capacitor", "chargesharing", "conservation", "parallelamount"],
    "stem": '<p>The figure shows a 4.0 &#956;F capacitor carrying a charge of 48 &#956;C, connected through a closed switch to an uncharged 8.0 &#956;F capacitor. {{FIG:s04-22}}</p><p>What is the potential difference across the two capacitors once the charge has settled?</p>',
    "opts": ['2.0 V', '4.0 V', '6.0 V', '8.0 V', '12 V'],
    "ans": 1,
    "distractors": ['halves the original potential difference because a second capacitor has been added to the circuit',
                    'correct',
                    'takes the common potential difference as the mean of 12 V and zero',
                    'applies the ratio of the capacitances the wrong way round, multiplying 12 V by 8.0/12',
                    'assumes the potential difference is unchanged because charge is conserved'],
    "profile": {
        "steps": [
            ("relate", "note that the total charge is conserved when the switch is closed"),
            ("relate", "note that the two capacitors end up in parallel and so share a common potential difference"),
            ("solve", "add the capacitances and divide the total charge by the total capacitance"),
            ("solve", "find the energy before and after, to show that the missing energy has gone somewhere"),
            ("check", "confirm the final potential difference is less than the initial one, as it must be when the same charge is spread over more capacitance"),
        ],
        "relations": ["Q = C V", "Q total = 48 &#956;C", "C total = 4.0 + 8.0 = 12 &#956;F",
                      "V = Q total / C total = 4.0 V"],
        "insight": "Charge is conserved when the switch is closed, not energy. The total charge stays at 48 microcoulombs, the total capacitance becomes 12 microfarads, and the common potential difference is therefore smaller than it was.",
        "shape": "conservation",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "48/(4.0 + 8.0)", "want": "4.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you know which quantity is conserved when two capacitors are joined. Charge is; energy is not. Getting that the wrong way round is the single most common error in this topic.</p>
<p><b>Step 1 — the initial state.</b> The 4.0 &#956;F capacitor carries 48 &#956;C, so its potential difference is</p>
<div class="formula">V = Q / C = 48 / 4.0 = 12 V</div>
<p>The second capacitor is uncharged, so its potential difference is zero and it holds no charge.</p>
<p><b>Step 2 — what happens when the switch closes.</b> Charge flows from the charged capacitor to the uncharged one until there is no further potential difference to drive it. At that point the two capacitors are in parallel and share a common potential difference. The total charge has nowhere to go — it cannot leave the circuit — so it is conserved:</p>
<div class="formula">Q total = 48 &#956;C   (before and after)</div>
<p><b>Step 3 — the total capacitance.</b> Two capacitors in parallel add:</p>
<div class="formula">C total = 4.0 + 8.0 = 12 &#956;F</div>
<p><b>Step 4 — the common potential difference.</b> The same charge now sits on 12 &#956;F instead of 4.0 &#956;F:</p>
<div class="formula">V = Q total / C total = 48 / 12 = 4.0 V</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 5 — where the energy went.</b> This is worth working out, because it shows why energy is not the conserved quantity. Before the switch closed:</p>
<div class="formula">energy before = &#189; Q V = &#189; &#215; 48 &#215; 12 = 288 &#956;J</div>
<p>After:</p>
<div class="formula">energy after = &#189; Q V = &#189; &#215; 48 &#215; 4.0 = 96 &#956;J</div>
<p>Two hundred microjoules have disappeared. They have not vanished: they were radiated as electromagnetic waves and dissipated as heat in the connecting wire, because the current that flowed was not zero and the wire has resistance. The charge had no such escape route, which is why charge is conserved and energy is not. This is one of the few places in elementary physics where a quantity other than energy is the one to conserve, and it is worth remembering for that reason.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2.0 V</b> halves the original potential difference on the grounds that a second capacitor has been added. The capacitance has gone up by a factor of three, not two, so the potential difference falls by a factor of three.</p>
<p>&middot; <b>6.0 V</b> is the mean of 12 V and zero, which would be right only if the two capacitances were equal. They are 4.0 &#956;F and 8.0 &#956;F, so the larger one takes the larger share of the charge and the common potential difference is pulled towards the smaller capacitor's contribution.</p>
<p>&middot; <b>8.0 V</b> applies the ratio of the capacitances the wrong way round, 12 &#215; 8.0/12. The potential difference falls when capacitance rises, so any correct expression must have the new capacitance in the denominator and the old one in the numerator.</p>
<p>&middot; <b>12 V</b> assumes the potential difference is unchanged because charge is conserved. Charge is conserved; potential difference is not. The same charge on three times the capacitance gives a third of the potential difference, and the factor of three is exactly <code>12/4.0</code>.</p>
<p><b>The trap.</b> Conserving energy instead of charge. If energy were conserved the common potential difference would come out as <code>12/&#8730;3</code>, which is about 6.9 V — a number that is not among the options, and that absence is itself a hint that the right conservation law is the other one.</p>
<p><b>Relevant topics:</b> capacitance and the relation Q = CV; capacitors in parallel; conservation of charge in a closed circuit; the energy stored in a capacitor and why it is not conserved here.</p>''',
    "trap": "Conserving energy rather than charge. Energy is lost to heat and radiation in the connecting wire; the total charge is what carries over.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 23 -- J, thermal.  Mixing two masses of water at different temperatures.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 23, "id": "S04-23", "module": "J", "diff": 2,
    "topic": "Mixing two masses of water: the final temperature when no heat is lost",
    "rel": [("J", "The heat gained by one body equals the heat lost by the other when they are mixed in an insulated container"),
            ("J", "The heat needed to change a body's temperature is the product of its mass, its specific heat capacity and the change"),
            ("A", "Recognising that a common factor cancels from both sides of an equation")],
    "key": ["mixing", "specificheat", "balance", "temperature"],
    "stem": '<p>In an insulated container, 0.40 kg of water at 90 &#176;C is mixed with 0.10 kg of water at 10 &#176;C. What is the final temperature of the mixture?</p>',
    "opts": ['26 &#176;C', '37 &#176;C', '50 &#176;C', '74 &#176;C', '82 &#176;C'],
    "ans": 3,
    "distractors": ['uses the mass ratio the wrong way round, giving the smaller mass the larger share of the temperature change',
                    'adds the two mass-weighted temperatures but divides by 1.0 kg instead of by the total mass',
                    'averages the two temperatures without weighting them by the masses',
                    'correct',
                    'takes the temperature change of the hot water to be the whole 80 &#176;C difference divided by the total mass in kilograms'],
    "profile": {
        "steps": [
            ("relate", "state that the heat lost by the hot water equals the heat gained by the cold water"),
            ("relate", "write each side as mass times specific heat capacity times temperature change, and cancel the specific heat capacity"),
            ("solve", "expand and collect the terms in the final temperature"),
            ("check", "confirm the answer lies between the two starting temperatures and is nearer the larger mass's temperature"),
        ],
        "relations": ["m1 c (90 &#8722; T) = m2 c (T &#8722; 10)",
                      "0.40 (90 &#8722; T) = 0.10 (T &#8722; 10)",
                      "0.5 T = 37, so T = 74 &#176;C"],
        "insight": "The specific heat capacity cancels because both bodies are water, so the answer depends only on the two masses and the two temperatures. The final temperature is always nearer the temperature of the larger mass.",
        "shape": "conservation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(0.40*90 + 0.10*10)/(0.40 + 0.10)", "want": "74"},
    "sol": '''<p><b>What is being tested.</b> Whether you can set up a conservation-of-energy equation for a mixture, and whether you notice that the specific heat capacity cancels. Both masses are water, which makes the arithmetic simple but does not remove the need to weight by mass.</p>
<p><b>Step 1 — the energy statement.</b> The container is insulated, so no heat leaves the water. The hot water cools and the cold water warms until they reach a common temperature <code>T</code>. The heat lost by the hot water is the heat gained by the cold water:</p>
<div class="formula">heat lost = heat gained
m1 c (90 &#8722; T) = m2 c (T &#8722; 10)</div>
<p><b>Step 2 — cancel the specific heat capacity.</b> Both bodies are water, so <code>c</code> is the same on both sides and cancels. This is worth noticing, because it means the answer does not depend on the value of <code>c</code> at all — a fact that also explains why the same method works for any two masses of the same substance:</p>
<div class="formula">0.40 (90 &#8722; T) = 0.10 (T &#8722; 10)</div>
<p><b>Step 3 — expand and collect.</b></p>
<div class="formula">36 &#8722; 0.4 T = 0.1 T &#8722; 1
36 + 1 = 0.1 T + 0.4 T
37 = 0.5 T
T = 74 &#176;C</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 4 — check the answer against what must be true.</b> The final temperature must lie between 10 &#176;C and 90 &#176;C, and 74 &#176;C does. It must be nearer the temperature of the larger mass, and the larger mass is the hot one, so the answer must be above the midpoint of 50 &#176;C — and 74 &#176;C is. The answer can also be written as a mass-weighted mean, <code>(0.40 &#215; 90 + 0.10 &#215; 10)/(0.40 + 0.10) = 74</code>, which is a second route to the same number and confirms that the algebra above is right. Notice that the mass-weighted mean is exactly what the conservation equation reduces to, which is why the answer is pulled so strongly towards 90 &#176;C: four times as much water started hot.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>26 &#176;C</b> uses the mass ratio the wrong way round, giving the smaller mass the larger share of the temperature change. It is the mirror image of the correct answer about the midpoint of 50 &#176;C, which is a useful thing to notice: 26 and 74 are equally far from 50, so an answer of 26 means the masses were swapped.</p>
<p>&middot; <b>37 &#176;C</b> comes from adding the two mass-weighted temperatures, 0.40 &#215; 90 + 0.10 &#215; 10 = 37, and forgetting to divide by the total mass. The units of that calculation are not a temperature at all, which is the clue.</p>
<p>&middot; <b>50 &#176;C</b> is the unweighted average of 90 &#176;C and 10 &#176;C. It is the answer you get by ignoring the masses entirely, which would be right only if the two masses were equal.</p>
<p>&middot; <b>82 &#176;C</b> takes the temperature change of the hot water to be the whole 80 &#176;C difference divided by the total mass in kilograms. Dividing a temperature difference by a mass has no physical meaning, and the result is not a temperature; it happens to be a number in the right range, which is what makes it dangerous.</p>
<p><b>The trap.</b> Averaging the temperatures instead of weighting them by mass. With unequal masses the final temperature is always nearer the temperature of the larger mass, and the arithmetic must reflect that.</p>
<p><b>Relevant topics:</b> specific heat capacity; conservation of energy in a mixture; the principle of mixtures; ratio reasoning with masses.</p>''',
    "trap": "Averaging the two temperatures without weighting them by mass, or swapping the masses in the ratio. The final temperature is always nearer the larger mass's temperature.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 24 -- K, nuclear.  The fraction remaining after several half-lives.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 24, "id": "S04-24", "module": "K", "diff": 2,
    "topic": "Radioactive decay: the fraction of a sample remaining after three half-lives",
    "rel": [("K", "The number of half-lives is the elapsed time divided by the half-life"),
            ("K", "Each half-life multiplies the number of undecayed nuclei by one half"),
            ("A", "Recognising that repeated halving is a power, not a multiplication by the number of steps")],
    "key": ["halflife", "decay", "fraction", "powers"],
    "stem": '<p>A radioactive isotope has a half-life of 8.0 days. What fraction of the original number of nuclei remains after 24 days?</p>',
    "opts": ['1/24', '1/3', '1/8', '1/2', '3/8'],
    "ans": 2,
    "distractors": ['divides one by the elapsed time in days, treating the decay as if it were linear',
                    'takes the fraction as the reciprocal of the number of half-lives',
                    'correct',
                    'counts a single halving, as though 8.0 days had passed rather than 24',
                    'adds the three halvings together instead of compounding them'],
    "profile": {
        "steps": [
            ("relate", "work out how many half-lives have elapsed by dividing the time by the half-life"),
            ("relate", "state that each half-life multiplies the remaining number by one half"),
            ("solve", "raise one half to the number of half-lives"),
            ("check", "step through the halvings one at a time and confirm the third step lands on the answer"),
        ],
        "relations": ["n = 24 / 8.0 = 3", "N / N0 = (1/2)<sup>n</sup>", "N / N0 = (1/2)<sup>3</sup> = 1/8"],
        "insight": "Three half-lives do not remove three halves of the sample. Each halving acts on what is left, so the fractions multiply rather than add, and the answer is one half cubed.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(1/2)**3", "want": "1/8"},
    "sol": '''<p><b>What is being tested.</b> Whether you treat repeated halving as a power rather than as a subtraction. It is a short question and the whole of it turns on that one idea.</p>
<p><b>Step 1 — how many half-lives.</b> The elapsed time divided by the half-life gives the number of halvings:</p>
<div class="formula">n = 24 / 8.0 = 3</div>
<p><b>Step 2 — what one half-life does.</b> After one half-life, half the nuclei that were there at the start have decayed, so half remain. The important word is "remain": the second half-life acts on the nuclei that survived the first, not on the original number.</p>
<p><b>Step 3 — apply it three times.</b> Each half-life multiplies the surviving number by one half, so after <code>n</code> half-lives</p>
<div class="formula">N / N0 = (1/2)<sup>n</sup>
N / N0 = (1/2)<sup>3</sup> = 1/8</div>
<p>So <b>Answer: C.</b></p>
<p><b>Step 4 — check by stepping through it.</b> Rather than trusting the power, follow the sample down one half-life at a time. Start with a fraction of 1. After 8.0 days it is 1/2. After 16 days it is 1/4. After 24 days it is 1/8. The two routes agree, and the step-by-step route makes it clear why the answer is 1/8 rather than 1/2 &#8722; 1/4 &#8722; 1/8 or any other combination: each step halves what is left, so the fractions form a geometric sequence and the third term is one eighth.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/24</b> divides one by the elapsed time in days. It treats decay as a linear process in which a fixed fraction disappears each day, which is not what a half-life means. Exponential decay is fastest at the start, and a linear model gets both the shape and the answer wrong.</p>
<p>&middot; <b>1/3</b> takes the fraction as the reciprocal of the number of half-lives. Three half-lives do not remove two thirds of the sample; they remove seven eighths of it.</p>
<p>&middot; <b>1/2</b> counts a single halving, as though only 8.0 days had passed. It is the answer to the question "how much remains after one half-life?" and it ignores the fact that the time given is three half-lives.</p>
<p>&middot; <b>3/8</b> adds the three halvings together, 1/2 + 1/4 + 1/8 = 7/8 — no, that is 7/8. Let me be careful: adding 1/8 three times gives 3/8, which is what you get by treating each half-life as removing one eighth of the original sample. It is the error of applying the same fractional reduction three times to the original amount instead of to what remains.</p>
<p><b>The trap.</b> Adding fractions instead of multiplying them. The tell-tale sign of this mistake is an answer that grows with the number of half-lives, which cannot be right: more time must mean less of the sample left, never more.</p>
<p><b>Relevant topics:</b> radioactive decay and half-life; exponential decay as repeated halving; the activity and the number of nuclei; geometric sequences.</p>''',
    "trap": "Adding the halvings instead of compounding them, or treating decay as linear in time. Each half-life acts on what remains, so the fractions multiply.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 25 -- L, quantum.  Equal de Broglie wavelengths for an electron and a proton.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 25, "id": "S04-25", "module": "L", "diff": 2,
    "topic": "An electron and a proton with the same de Broglie wavelength: the ratio of their kinetic energies",
    "rel": [("L", "The de Broglie wavelength as Planck's constant divided by the momentum"),
            ("L", "The kinetic energy of a particle expressed in terms of its momentum and its mass"),
            ("A", "Following an inverse proportionality through a ratio, with no numbers needed")],
    "key": ["debroglie", "momentum", "kineticenergy", "massratio"],
    "stem": '<p>An electron and a proton have the same de Broglie wavelength. Taking the mass of the proton to be 1836 times the mass of the electron, what is the ratio of the electron\'s kinetic energy to the proton\'s?</p>',
    "opts": ['1836', '1', '1/1836', '43', '3.4 &#215; 10<sup>6</sup>'],
    "ans": 0,
    "distractors": ['correct',
                    'assumes that equal de Broglie wavelengths mean equal kinetic energies',
                    'inverts the mass ratio, so the heavier particle would carry the larger kinetic energy',
                    'takes the square root of the mass ratio, as though the speeds were equal rather than the momenta',
                    'squares the mass ratio'],
    "profile": {
        "steps": [
            ("relate", "use the de Broglie relation to argue that equal wavelengths mean equal momenta"),
            ("relate", "write the kinetic energy in terms of momentum and mass, so the momentum is the common quantity"),
            ("solve", "form the ratio, in which the momentum cancels and only the masses are left"),
            ("check", "confirm the lighter particle carries more kinetic energy for the same momentum, which is what the inverse mass relationship says"),
        ],
        "relations": ["&#955; = h / p, so equal &#955; means equal p", "KE = p<sup>2</sup> / (2 m)",
                      "KE(e) / KE(p) = m(p) / m(e) = 1836"],
        "insight": "Equal de Broglie wavelengths mean equal momenta, and for a fixed momentum the kinetic energy is inversely proportional to the mass. The lighter particle therefore carries the larger kinetic energy.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "(p**2/(2*m_e))/(p**2/(2*m_p))", "want": "m_p/m_e"},
    "sol": '''<p><b>What is being tested.</b> Whether you can turn a wavelength condition into a momentum condition and then follow the mass through. No numbers are needed until the last line, and the mass ratio is given so that none are needed then either.</p>
<p><b>Step 1 — from wavelength to momentum.</b> The de Broglie relation says</p>
<div class="formula">&#955; = h / p</div>
<p>The two particles have the same wavelength and <code>h</code> is a constant, so they must have the same momentum. That is the whole content of the condition, and it is worth stating explicitly because the rest of the question depends on it: equal wavelength means equal momentum, not equal speed and not equal energy.</p>
<p><b>Step 2 — the kinetic energy in terms of momentum.</b> Writing the kinetic energy in the form that contains <code>p</code> rather than <code>v</code> puts the common quantity on the same footing in both expressions:</p>
<div class="formula">KE = p<sup>2</sup> / (2 m)</div>
<p><b>Step 3 — form the ratio.</b> The momenta are equal, so they cancel:</p>
<div class="formula">KE(e) / KE(p) = [p<sup>2</sup> / (2 m(e))] / [p<sup>2</sup> / (2 m(p))]
             = m(p) / m(e)
             = 1836</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 4 — check the direction of the result.</b> The lighter particle has the larger kinetic energy, and the electron is the lighter one, so the ratio must be greater than one — and 1836 is. Physically this makes sense: to have the same momentum as a heavy proton, a light electron has to be moving very much faster, and the kinetic energy goes as the square of the speed. The speed ratio is 1836, so the energy ratio is 1836 as well, because the momentum is <code>mv</code> and the energy is <code>mv<sup>2</sup>/2 = pv/2</code> — with <code>p</code> fixed, the energy is proportional to the speed. That is a third route to the same answer, and it is a good one to have in reserve.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1</b> assumes equal wavelengths mean equal kinetic energies. If that were true, a slow heavy proton and a fast light electron would have to have the same energy, which contradicts <code>KE = p<sup>2</sup>/(2m)</code> directly.</p>
<p>&middot; <b>1/1836</b> inverts the ratio, making the proton carry 1836 times the electron's kinetic energy. That would be right if the two particles had the same <i>speed</i>, because then the heavier one carries more energy. They do not: the condition is on wavelength, which fixes momentum, not speed.</p>
<p>&middot; <b>43</b> is the square root of 1836. It is the ratio of the speeds if the energies were equal, or the ratio of the momenta if the speeds were equal. It is the answer to a neighbouring question, and the giveaway is that the correct answer has no square root in it: the wavelength condition fixes <code>p</code> exactly, with nothing left to take a root of.</p>
<p>&middot; <b>3.4 &#215; 10<sup>6</sup></b> is 1836 squared. It comes from applying the mass ratio twice, once in the momentum and once in the energy. The momentum cancels in step 3, so the mass ratio appears exactly once.</p>
<p><b>The trap.</b> Reading "the same wavelength" as "the same speed" or "the same energy". Each of those conditions would give a different answer, and the only one the question states is the wavelength. Turning it into a statement about momentum before doing anything else is what keeps the rest of the working short.</p>
<p><b>Relevant topics:</b> the de Broglie relation; momentum and kinetic energy; the mass ratio of the proton and the electron; ratio reasoning without numbers.</p>''',
    "trap": "Reading equal de Broglie wavelengths as equal speeds or equal energies. Equal wavelengths mean equal momenta, and the kinetic energy then goes as the inverse of the mass.",
},
]
