# -*- coding: utf-8 -*-
"""BPhO Round 0 -- BANK SECTION 03 (S03-01 .. S03-25).

Twenty-five original questions in the exact Round 0 format: single-answer MCQ, five
options, no calculator, one mark each, no negative marking.  They are NOT taken from any
competition paper -- BPhO's papers and other competitions' papers are copyrighted.  What
is borrowed is the style and the difficulty, and `spec.STYLE` records which competitions
set questions of comparable demand inside the R0 scope.

The module mix is the plan's mix for this section, so it is a valid full-length mock:
A3 B2 C4 D1 E1 F2 G2 H3 I1 J2 K2 L1 M1.

This section leans on the two things the brief asks for and the earlier sections could
only partly supply: a much larger share of questions whose answer is a SYMBOLIC or
ratio result rather than a number, and figures that carry the discriminator.  Ten of the
twenty-five carry a figure -- the real paper carries eight.

Same field contract as sec01.py -- see that file's docstring for `distractors`,
`profile` and `check`.

Figures are hand-authored inline SVG in fig/, referenced as {{FIG:key}}.
"""

SECTION = 3

QUESTIONS = [

# ═════════════════════════════════════════════════════════════════════════════
# 1 — C, forces.  A beam on two supports: which support takes the load.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 1, "id": "S03-01", "module": "C", "diff": 3,
    "topic": "A loaded beam on two supports: the reaction at one end",
    "rel": [("C", "Taking moments about a point so that an unknown force drops out"),
            ("C", "A uniform body's weight acting at its centre"),
            ("A", "The moment arm is the perpendicular distance from the pivot, not from an end")],
    "key": ["moments", "beam", "reaction"],
    "stem": '<p>A uniform beam <code>AB</code> is 6.0 m long and weighs 240 N. It rests on a support at <code>A</code> and a support at <code>B</code>. A load of 360 N is placed on the beam 2.0 m from <code>A</code>, as shown. {{FIG:s03-01}}</p><p>What is the upward force exerted by the support at <code>A</code>?</p>',
    "opts": ['300 N',
             '240 N',
             '360 N',
             '480 N',
             '180 N'],
    "ans": 2,
    "distractors": ['splits the total 600 N evenly between the two supports, which would be right only if the load sat at the centre',
                    "takes the beam's own weight alone, halves it, and reports the support at the far end instead of the one asked for",
                    'correct',
                    "uses the load's distance from <code>B</code> as well, so the load's moment arm becomes the whole 6.0 m",
                    "measures the load's moment arm from the centre of the beam rather than from the load's actual position"],
    "profile": {
        "steps": [
            ("relate", "note that the beam is uniform, so its 240 N acts at the midpoint, 3.0 m from either end"),
            ("relate", "choose to take moments about B, so that the unknown force at B never enters the equation"),
            ("eliminate", "the load is 2.0 m from A, so its perpendicular distance from B is 6.0 - 2.0 = 4.0 m"),
            ("solve", "F_A x 6.0 = 240 x 3.0 + 360 x 4.0 = 720 + 1440 = 2160, so F_A = 2160/6.0 = 360 N"),
            ("check", "the two forces must add to 600 N, so B carries 240 N, and moments about A confirm that value"),
            ("check", "the support nearer the load must carry the larger share, which 360 N against 240 N does"),
        ],
        "relations": ["F_A x 6.0 = W_beam x 3.0 + W_load x 4.0",
                      "6.0 - 2.0 = 4.0",
                      "F_A = 2160/6.0"],
        "insight": "The whole problem is read off the diagram. Uniformity puts the beam's 240 N at the 3.0 m midpoint, and the load's moment arm is its perpendicular distance from whichever pivot you choose -- not from the end it was placed from. Get those two arms right and a single moments equation finishes it.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(240*3 + 360*4)/6", "want": "360"},
    "sol": '''<p><b>What is being tested.</b> Whether you can choose the pivot that makes the algebra shortest. Nothing here needs a calculator: every number divides cleanly once the pivot is right.</p>
<p><b>Step 1 — where does the beam's weight act?</b> The beam is uniform, so its weight behaves as though it were all concentrated at the midpoint. The midpoint is 3.0 m from <code>A</code> and 3.0 m from <code>B</code>. This is the fact the whole question rests on; if the beam were not uniform, nothing could be done without more information.</p>
<p><b>Step 2 — choose the pivot.</b> Two forces are unknown, the reactions at <code>A</code> and at <code>B</code>. Taking moments about <code>B</code> gives the reaction at <code>B</code> a moment arm of zero, so it disappears. One equation, one unknown:</p>
<div class="formula">moment about B:  F_A x 6.0 = W_beam x 3.0 + W_load x (distance of the load from B)</div>
<p><b>Step 3 — the load's moment arm.</b> The load is 2.0 m from <code>A</code>, and the beam is 6.0 m long, so its distance from <code>B</code> is <code>6.0 - 2.0 = 4.0 m</code>. Getting this arm right is the whole of the question's difficulty: the load is <i>near</i> <code>A</code>, and a support takes more of a load that is near it, which is the physical check on the answer.</p>
<p><b>Step 4 — put the numbers in.</b></p>
<div class="formula">F_A x 6.0 = 240 x 3.0 + 360 x 4.0
         = 720 + 1440
         = 2160
F_A      = 2160/6.0 = 360 N</div>
<p>So <b>Answer: C.</b></p>
<p><b>Step 5 — check it two ways.</b> First, the forces must add up: the total load is <code>240 + 360 = 600 N</code>, so the other support carries <code>600 - 360 = 240 N</code>. Second, take moments about <code>A</code> with that value: <code>240 x 3.0 + 360 x 2.0 = 720 + 720 = 1440</code>, and the reaction at <code>B</code> gives <code>240 x 6.0 = 1440</code>. The two agree, so 360 N is right.</p>
<p><b>Step 6 — does the size make sense?</b> The load of 360 N sits 2.0 m from <code>A</code>, which is well inside the half of the beam nearest <code>A</code>, and <code>A</code> carries 360 N of the 600 N total. The support nearer the load takes the larger share. That is the physical direction, and it confirms the arithmetic.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>300 N</b> is <code>600/2</code>: the total halved. That is correct only when the load is at the centre, where the two supports are symmetric. Here the load is 2.0 m from <code>A</code> and 4.0 m from <code>B</code>, so the arrangement is not symmetric and an even split is wrong.</p>
<p>&middot; <b>240 N</b> is the reaction at <code>B</code>, and it is also the beam's own weight halved. It is a real number in this problem, which is exactly why it is offered: a candidate who solves for the wrong support, or who forgets the load entirely, lands on it.</p>
<p>&middot; <b>480 N</b> comes from <code>(240 x 3.0 + 360 x 6.0)/6.0</code>. It takes the load's moment arm about <code>B</code> to be the full length of the beam, which would put the load at <code>A</code> itself.</p>
<p>&middot; <b>180 N</b> comes from using 3.0 m for the load as well as for the beam: <code>(240 x 3.0 + 360 x 3.0)/6.0 = 1800/6.0 = 180</code>. It treats the load as though it also sat at the centre.</p>
<p><b>The trap.</b> Reading the load's distance from the end it is measured from, instead of from the pivot you chose. The stem deliberately measures the load from <code>A</code> while the natural pivot is <code>B</code>; the arm you need is the one you did not write down.</p>
<p><b>Relevant topics:</b> the principle of moments; the centre of gravity of a uniform body; choosing a pivot; the two independent checks (forces sum, moments about the other end).</p>''',
    "trap": "Using the load's distance from the end it was measured from as its moment arm. The arm is the perpendicular distance from the pivot you chose, which here is 4.0 m and not 2.0 m.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 2 — A, toolkit.  Dimensional analysis: how fast a droplet vibrates.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 2, "id": "S03-02", "module": "A", "diff": 3,
    "topic": "Dimensional analysis: the vibration frequency of a liquid droplet",
    "rel": [("A", "Matching the base dimensions of both sides of a proposed relation"),
            ("A", "Solving simultaneous equations in the unknown exponents"),
            ("F", "Why a smaller droplet vibrates at a higher frequency")],
    "key": ["dimensions", "droplet", "frequency"],
    "stem": '<p>A small droplet of liquid, left to itself, vibrates about its spherical shape. The frequency <code>f</code> of that vibration depends only on the surface tension <code>&gamma;</code> of the liquid, its density <code>&rho;</code>, and the radius <code>r</code> of the droplet. Which expression is dimensionally a frequency?</p>',
    "opts": ['<code>&radic;(&gamma;/(&rho;r))</code>',
             '<code>&radic;(&gamma;r<sup>3</sup>/&rho;)</code>',
             '<code>&radic;(&gamma;&rho;/r<sup>3</sup>)</code>',
             '<code>&radic;(&gamma;/(&rho;r<sup>3</sup>))</code>',
             '<code>&gamma;/(&rho;r<sup>3</sup>)</code>'],
    "ans": 3,
    "distractors": ["takes the length exponent as -1/2 instead of -3/2, which is the exponent a droplet's vibration does not have",
                    'flips the sign of the length exponent, putting the radius on top where the length equation requires it underneath',
                    'multiplies by the density where the mass equation requires a division, so the sign of the mass equation is wrong',
                    'correct',
                    'gets all three exponents right but leaves out the square root, which makes the quantity a frequency squared'],
    "profile": {
        "steps": [
            ("relate", "write the base dimensions: [f] = T^-1, [gamma] = M T^-2, [rho] = M L^-3, [r] = L"),
            ("relate", "propose f = k gamma^a rho^b r^c and demand that the dimensions match"),
            ("eliminate", "the time equation fixes a on its own; the mass equation then fixes b"),
            ("solve", "the length equation gives c, and c comes out as -3/2"),
            ("check", "assemble the product and confirm the two sides now carry the same dimensions"),
        ],
        "relations": ["[f] = T^-1", "[gamma] = M T^-2", "[rho] = M L^-3",
                      "a + b = 0", "-2a = -1", "-3b + c = 0"],
        "insight": "Time appears in exactly one of the three given quantities, and it appears as T^-2. So the time equation alone forces a = 1/2, and that single power is the only possible source of the square root. Everything else is bookkeeping.",
        "shape": "dimensional-analysis",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "dim", "got": "N m^-1 kg^-1", "want": "s^-2"},
    "sol": '''<p><b>What is being tested.</b> Turning a physical statement into three simultaneous equations and solving them. No formula for a droplet is needed or expected: everything is in the question.</p>
<p><b>Step 1 — write down the dimensions.</b> Read them off the units rather than trying to recall them:</p>
<div class="formula">[f]     = T^-1
[gamma] = N m^-1 = M T^-2
[rho]   = M L^-3
[r]     = L</div>
<p>Surface tension is the only awkward one. A newton is <code>kg m s^-2</code>, so a newton per metre is <code>kg m s^-2 / m = kg s^-2</code>: mass to the first power, time to the minus two, and no length at all.</p>
<p><b>Step 2 — propose the form and match.</b> Assume <code>f = k gamma^a rho^b r^c</code>, with <code>k</code> a dimensionless number that dimensional analysis is allowed not to find. Match each base dimension in turn:</p>
<div class="formula">mass:    a + b = 0
length:  -3b + c = 0
time:    -2a = -1</div>
<p><b>Step 3 — the time equation alone fixes a.</b> <code>-2a = -1</code> gives <code>a = 1/2</code>. That is the whole reason a square root appears, and it is forced: only surface tension carries time, and it carries it as <code>T^-2</code>. If the answer had no square root, it could not be a frequency at all.</p>
<p><b>Step 4 — mass, then length.</b> From <code>a + b = 0</code> we get <code>b = -1/2</code>, so the density sits underneath the root. Then <code>-3b + c = 0</code> gives <code>c = 3b = -3/2</code>: the radius appears as <code>r^(-3/2)</code>, which is the strongest power of the three and the one that makes small droplets buzz.</p>
<p><b>Step 5 — assemble and check.</b></p>
<div class="formula">f = k gamma^(1/2) rho^(-1/2) r^(-3/2)
  = k sqrt(gamma/(rho r^3))</div>
<p>Put the dimensions back in to be sure: <code>gamma/(rho r^3)</code> has units <code>(N/m)/(kg/m^3 x m^3) = N m^-1 kg^-1</code>, and since <code>N = kg m s^-2</code> that is <code>s^-2</code>. Its square root is <code>s^-1</code>, a frequency. So <b>Answer: D.</b></p>
<p><b>The distractors.</b></p>
<p>&middot; <b>&radic;(&gamma;/(&rho;r))</b> is right on mass and time and takes <code>c = -1/2</code>. It is the most tempting wrong answer because it has the right shape — a root, density underneath, radius underneath. It is wrong only in the exponent on <code>r</code>, which is the part of the working that is easiest to rush.</p>
<p>&middot; <b>&radic;(&gamma;r<sup>3</sup>/&rho;)</b> takes <code>c = +3/2</code>, the sign of the length exponent flipped. It would make bigger droplets vibrate faster, which is the wrong way round.</p>
<p>&middot; <b>&radic;(&gamma;&rho;/r<sup>3</sup>)</b> puts the density on top, i.e. <code>b = +1/2</code>. That contradicts the mass equation <code>a + b = 0</code>, which is not <code>a - b = 0</code>.</p>
<p>&middot; <b>&gamma;/(&rho;r<sup>3</sup>)</b> has all three exponents right and no root. Its units are <code>s^-2</code>, so it is a frequency squared. It can be rejected by units alone, without doing any of the exponent algebra — which is worth noticing, because it is the cheapest possible check on any answer of this kind.</p>
<p><b>The trap.</b> Hunting for a remembered formula for a vibrating droplet. There is none worth remembering, and there does not need to be: the three exponents are forced by the dimensions, and the only freedom left is the dimensionless constant in front, which is exactly the part dimensional analysis is not able to supply.</p>
<p><b>Relevant topics:</b> base and derived units; the dimensions of mechanical quantities; simultaneous equations in three unknowns; the limits of dimensional analysis; why small droplets ring at high frequency.</p>''',
    "trap": "Searching for a remembered droplet formula instead of solving the three exponent equations. The time dimension appears only in the surface tension, so it alone forces the 1/2 power and hence the root.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 3 — C, forces.  Holding a block against a wall by pushing on it.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 3, "id": "S03-03", "module": "C", "diff": 3,
    "topic": "Friction against a vertical wall: the smallest push that holds a block up",
    "rel": [("C", "Resolving horizontally to find the normal reaction"),
            ("C", "Limiting friction set by the normal reaction, not by the weight"),
            ("A", "Rearranging a two-equation balance for the one unknown asked for")],
    "key": ["friction", "wall", "limiting"],
    "stem": '<p>A block of mass 2.0 kg is held against a rough vertical wall by a horizontal push <code>F</code>, as shown. The coefficient of friction between the block and the wall is 0.40. The block is on the point of sliding down the wall. {{FIG:s03-03}}</p><p>What is the smallest value of <code>F</code> that can hold the block in place?</p>',
    "opts": ['8.0 N',
             '50 N',
             '20 N',
             '80 N',
             '5.0 N'],
    "ans": 1,
    "distractors": ['multiplies the weight by the coefficient instead of dividing by it, giving mu x mg rather than mg/mu',
                    'correct',
                    'uses the weight itself as the normal reaction and so reports 20 N, the weight rather than the push',
                    'treats the coefficient as though it applied to the mass in kilograms rather than to the force in newtons',
                    'divides the weight by the square of the coefficient, which has no basis in the two balance equations'],
    "profile": {
        "steps": [
            ("relate", "the block is in equilibrium, so the horizontal and vertical forces each balance separately"),
            ("relate", "horizontally the wall's normal reaction equals the push, so N = F"),
            ("relate", "vertically friction must carry the whole weight, so the friction needed is mg = 20 N"),
            ("eliminate", "at the point of sliding the friction is limiting, so friction = mu x N = 0.40 F"),
            ("solve", "put the two together: 0.40 F = 20, so F = 50 N"),
        ],
        "relations": ["N = F", "friction = mg", "friction = mu N", "0.40 F = 20"],
        "insight": "The push does not hold the block up directly. It sets the normal reaction, and the normal reaction sets how much friction is available. So the weight is paid for through the coefficient, and the push you need is the weight divided by mu.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "2*10/0.40", "want": "50"},
    "sol": '''<p><b>What is being tested.</b> Whether you see that the push and the weight act in perpendicular directions, and are connected only through friction. Candidates who treat the push as though it were holding the block up directly get an answer that is out by a factor of <code>1/mu</code>.</p>
<p><b>Step 1 — resolve horizontally.</b> The only horizontal forces are the push <code>F</code> and the wall's normal reaction <code>N</code>. There is no acceleration, so they are equal:</p>
<div class="formula">N = F</div>
<p><b>Step 2 — resolve vertically.</b> The block's weight is <code>mg = 2.0 x 10 = 20 N</code> downwards. It is on the point of sliding <i>down</i>, so friction acts upwards and must carry the whole weight:</p>
<div class="formula">friction = mg = 20 N</div>
<p><b>Step 3 — bring in the friction law.</b> "On the point of sliding" means the friction is at its limiting value, and limiting friction is set by the normal reaction:</p>
<div class="formula">friction = mu N = 0.40 N</div>
<p><b>Step 4 — eliminate N.</b> Substituting <code>N = F</code> from step 1:</p>
<div class="formula">0.40 F = 20
F = 20/0.40 = 50 N</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 5 — check the direction and the size.</b> The coefficient is less than one, so the push must exceed the weight it is supporting: <code>50 N</code> is larger than <code>20 N</code>, as it must be. If the wall were rougher, <code>mu</code> would be larger and the required push would fall — push less hard and the block still holds. That is the right way round.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>8.0 N</b> is <code>mu x mg = 0.40 x 20</code>. It has the right ingredients and the wrong operation: it multiplies where the balance requires a division. It is the classic inversion, and it is the wrong answer offered here that looks most like working.</p>
<p>&middot; <b>20 N</b> is the weight itself. A candidate who forgets that friction is limited — and thinks the push must simply equal the weight — lands here. It also happens to be the normal reaction you would get if the push were 20 N, which makes it look internally consistent.</p>
<p>&middot; <b>80 N</b> is <code>mg/mu^2 = 20/0.25</code>. It divides by the coefficient twice, which no step of the reasoning does.</p>
<p>&middot; <b>5.0 N</b> is <code>mu x mg / 4</code>, or equivalently <code>20 x 0.25</code>. It treats the coefficient as applying to the mass in kilograms rather than to a force, and gets a push smaller than the weight it is meant to support — impossible with a coefficient below one.</p>
<p><b>The trap.</b> The instinct that a bigger push means more friction, so the smallest push is the smallest friction — and therefore a small number. The truth is the other way round: friction is limited by the normal reaction, so a smaller push means less friction available, and below 50 N the block slides.</p>
<p><b>Relevant topics:</b> equilibrium under perpendicular forces; the normal reaction and what sets it; limiting friction; why <code>mu</code> less than one means the holding force exceeds the load.</p>''',
    "trap": "Reading the push as directly supporting the weight. It sets the normal reaction, and the normal reaction sets the friction, so the required push is the weight divided by the coefficient and is larger than the weight.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 4 — H, circuits.  A balanced bridge: the resistance that makes it balance.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 4, "id": "S03-04", "module": "H", "diff": 2,
    "topic": "A balanced bridge: the fourth resistance",
    "rel": [("H", "A bridge balances when the two potential dividers give the same fraction"),
            ("H", "Equal currents in the two arms, so each arm divides its own way"),
            ("A", "Turning a ratio into a single multiplication")],
    "key": ["bridge", "balance", "ratio"],
    "stem": '<p>The bridge below balances: no current flows through the detector <code>G</code> when <code>R</code> has one particular value. {{FIG:s03-04}}</p><p>What is that value of <code>R</code>?</p>',
    "opts": ['6.0 k&Omega;',
             '2.0 k&Omega;',
             '18 k&Omega;',
             '4.5 k&Omega;',
             '3.0 k&Omega;'],
    "ans": 0,
    "distractors": ['correct',
                    'applies the balance ratio with the arms the wrong way up, giving the reciprocal of the required value',
                    'adds the two known resistances in the same arm instead of forming their ratio with the other arm',
                    'halves the product of the two arms, which is what you get by forgetting that one of the ratios must be inverted',
                    'assumes the four arms must all be equal at balance, which is true only when the bridge is symmetric'],
    "profile": {
        "steps": [
            ("relate", "with no current through the detector, the two junctions are at the same potential"),
            ("relate", "so each arm is a potential divider, and the same fraction of the supply appears across the same side in both arms"),
            ("relate", "the ratio of the resistances in the left arm equals the ratio in the right arm"),
            ("solve", "R = 6.0 x 3.0/3.0, i.e. the unknown arm times the ratio the other arm fixes"),
            ("check", "confirm both arms give the same fraction of the supply, which is what balance means"),
        ],
        "relations": ["R1/R2 = R3/R4", "V_left = V_right", "R = R3 x R2/R4"],
        "insight": "No current through the detector means the two junctions sit at the same potential. That turns each arm into a potential divider, and balance is simply the statement that the two dividers give the same fraction — a ratio, not a sum.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "3.0*6.0/3.0", "want": "6.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you can turn "no current in the detector" into a statement about ratios. The bridge is a potential divider used twice, and balance is the two dividers agreeing.</p>
<p><b>Step 1 — what does balance mean?</b> If no current flows through <code>G</code>, then the two junctions it connects are at the same potential. There is a second, equally useful reading: the same current flows through the two resistances of the left arm, and the same current through the two of the right arm.</p>
<p><b>Step 2 — write each arm as a potential divider.</b> Let the supply be <code>V</code>. The left junction sits at <code>V x R2/(R1 + R2)</code> and the right junction at <code>V x R4/(R3 + R4)</code>. Balance says these are equal:</p>
<div class="formula">R2/(R1 + R2) = R4/(R3 + R4)</div>
<p><b>Step 3 — simplify.</b> Cross-multiplying and cancelling the common <code>R2 R4</code> term leaves the form worth remembering:</p>
<div class="formula">R1/R2 = R3/R4
i.e. the ratio of the left arm equals the ratio of the right arm</div>
<p><b>Step 4 — put the numbers in.</b> With <code>R1 = 3.0 k</code>, <code>R2 = 3.0 k</code>, <code>R3 = 6.0 k</code> and <code>R4 = R</code>:</p>
<div class="formula">3.0/3.0 = 6.0/R
1 = 6.0/R
R = 6.0 k&Omega;</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 5 — check by going back to potentials.</b> With a 12 V supply, the left junction is at <code>12 x 3.0/6.0 = 6.0 V</code>, and the right junction is at <code>12 x 6.0/12 = 6.0 V</code>. The two agree, so no current flows through the detector. The check is worth doing because it uses the original condition rather than the simplified ratio, so it cannot inherit a mistake made while simplifying.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2.0 k&Omega;</b> is <code>6.0 x 3.0/9.0</code> — the ratio applied upside down, giving the reciprocal-type answer. Since the left arm has a ratio of 1, the right arm must also have a ratio of 1, so <code>R</code> must equal 6.0 k&Omega; and not something smaller.</p>
<p>&middot; <b>18 k&Omega;</b> is <code>3.0 + 6.0 + 3.0 + ...</code>, or <code>6.0 x 3.0</code>: it forms a sum or a bare product where the balance condition requires a ratio.</p>
<p>&middot; <b>4.5 k&Omega;</b> is <code>3.0 x 3.0/2</code>. It comes from halving a product, which is what happens if you try to use <code>R1 R2 = R3 R4</code> — a condition that is not the balance condition.</p>
<p>&middot; <b>3.0 k&Omega;</b> assumes all four arms are equal. That is true only for a symmetric bridge, and this one is not: the right arm already contains 6.0 k&Omega;.</p>
<p><b>The trap.</b> Reaching for "the products are equal" because it sounds like the balance condition. The balance condition is about ratios. A quick dimensional sanity check helps: every term of the correct relation is a pure number, while <code>R1 R2 = R3 R4</code> compares resistances squared, and nothing in the physics squares anything.</p>
<p><b>Relevant topics:</b> the potential divider; the balanced Wheatstone bridge; the condition for no current in a detector; why a bridge measures a ratio and not an absolute value.</p>''',
    "trap": "Using R1 R2 = R3 R4 because it looks like the balance condition. Balance is about ratios, and it is the ratio of the left arm that must equal the ratio of the right arm.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 5 — A, toolkit.  Estimation: the power a cyclist needs on a hill.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 5, "id": "S03-05", "module": "A", "diff": 2,
    "topic": "Estimation: the power needed to climb a 10% hill on a bicycle",
    "rel": [("A", "Turning a gradient into a vertical speed"),
            ("C", "Power as a rate of doing work against gravity"),
            ("A", "Rounding to one significant figure and judging whether the size is right")],
    "key": ["estimation", "power", "gradient"],
    "stem": '<p>A cyclist and bicycle together have a mass of about 80 kg. The cyclist climbs a hill whose gradient is 10% at a steady 5.0 m/s.</p><p>Which value is the closest estimate of the useful power the cyclist is delivering against gravity?</p>',
    "opts": ['40 W',
             '2000 W',
             '200 W',
             '4000 W',
             '400 W'],
    "ans": 4,
    "distractors": ['takes the full speed of 5.0 m/s as the vertical speed, which is what a 100% gradient would give',
                    'squares the speed, as though the cyclist were gaining kinetic energy rather than height',
                    'uses the whole mass as though it had to be lifted at the vertical speed but takes only half of the height gained',
                    'uses the speed at which the cyclist is moving along the road as the power directly, without the mass',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "a gradient of 10% means the road rises 0.10 m for every metre travelled along it"),
            ("relate", "travelling 5.0 m each second, the cyclist therefore rises 0.10 x 5.0 = 0.50 m each second"),
            ("relate", "the work done against gravity each second is the weight raised through that height, m g h"),
            ("solve", "P = 80 x 10 x 0.50 = 400 W"),
            ("check", "compare with a known figure: a fit cyclist can hold a few hundred watts for a long climb, so 400 W is the right order"),
        ],
        "relations": ["gradient = rise/run", "vertical speed = 0.10 x 5.0 = 0.50 m/s",
                      "P = m g v_vertical", "P = 80 x 10 x 0.50"],
        "insight": "A gradient is a ratio of two lengths, so multiplying it by the speed along the road gives the speed upwards. That one conversion turns an estimation problem into a single multiplication.",
        "shape": "order-of-magnitude",
        "approx": True,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "80*10*0.10*5.0", "want": "400"},
    "sol": '''<p><b>What is being tested.</b> Whether you can convert a gradient into a vertical speed. Everything after that is one multiplication. This is the kind of question the real paper uses to see whether a candidate is comfortable with ratios and units rather than with formulas.</p>
<p><b>Step 1 — what does a gradient of 10% mean?</b> A gradient is a ratio of two lengths, not an angle and not a force. Ten per cent means the road rises <code>0.10 m</code> for every <code>1.0 m</code> travelled <i>along</i> the road. The horizontal distance is not the useful quantity here; the distance along the road is what the speed refers to.</p>
<p>One approximation is being made here and it is worth naming. A gradient is a tangent, while the force that has to be overcome goes as the sine. For a 10&#37; gradient the road is inclined at only about 6&#176;, and at angles that small sin &#952; &#8776; tan &#952; &#8776; &#952;, so the two may be used interchangeably to the accuracy an estimate needs. The paper&#8217;s own constant sheet supplies exactly this small-angle approximation, which is a signal that it is a tool to reach for rather than a liberty taken.</p>
<p><b>Step 2 — turn it into a vertical speed.</b> The cyclist covers <code>5.0 m</code> of road each second. Along that road the rise is one tenth of the distance, so:</p>
<div class="formula">vertical speed = 0.10 x 5.0 = 0.50 m/s</div>
<p>This is the step the whole question turns on. The cyclist is rising half a metre every second, not five metres.</p>
<p><b>Step 3 — the power against gravity.</b> Raising a mass at a steady speed requires force equal to its weight, and power is force times speed:</p>
<div class="formula">P = m g v_vertical
  = 80 x 10 x 0.50
  = 400 W</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 4 — is the size right?</b> A racing cyclist can hold a few hundred watts for an hour, and a club cyclist rather less; professional riders reach about 400 W for a sustained effort. So 400 W is a plausible figure for a hill climb, and it is the kind of cross-check that catches a factor-of-ten slip. The same computation with the full 5.0 m/s as the vertical speed would give 4000 W, which no human can deliver for more than a second or two — and that is exactly how you know it is wrong.</p>
<p><b>Step 5 — what has been left out, and why that is allowed.</b> Rolling resistance and air resistance also take power, so the cyclist's total output is more than 400 W. The question asks for the power delivered <i>against gravity</i>, which is the part the height gain demands. Being clear about which part is being asked for is part of the skill: the estimate is deliberately of the one term you can compute from the data given.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>40 W</b> is <code>80 x 10 x 0.05</code>: the gradient applied twice, or a factor of ten lost. A cyclist climbing at 400 W is a familiar figure, so 40 W should look too small for a hill.</p>
<p>&middot; <b>2000 W</b> is <code>80 x 5.0^2/1</code> in structure — the speed squared rather than the height gained. That is the kinetic-energy form, and it has nothing to do with climbing at a steady speed, where kinetic energy does not change.</p>
<p>&middot; <b>200 W</b> is <code>80 x 10 x 0.25</code>: the vertical speed halved. It comes from treating the 10% gradient as giving a rise of a quarter of a metre per second, which is a factor of two adrift.</p>
<p>&middot; <b>4000 W</b> is <code>80 x 10 x 5.0</code>: the full speed used as the vertical speed, which is what a 100% gradient would give. It is the answer to a different question — climbing a wall at 5.0 m/s.</p>
<p><b>The trap.</b> Multiplying by the gradient the wrong way, or not at all. The phrase "10%" invites you to do something with 0.10; the question is whether you multiply the speed by it or divide by it. Multiplying is right, because a smaller gradient must mean less power, and multiplying by a number below one makes the answer smaller.</p>
<p><b>Relevant topics:</b> gradients as ratios; power as force times speed; work done against gravity; one-significant-figure estimation and the sanity check against a familiar figure.</p>''',
    "trap": "Using the road speed as the vertical speed. A 10% gradient converts 5.0 m/s along the road into only 0.50 m/s upwards, so the power is a factor of ten smaller than the naive answer.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 6 — B, kinematics.  DEEP (10 moves).  A three-stage journey: the average speed
# is the total distance over the total time, which is NOT the mean of the speeds.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 6, "id": "S03-06", "module": "B", "diff": 3,
    "topic": "A three-stage journey: the average speed is a time-weighted mean, not a simple one",
    "rel": [("B", "The area under a velocity-time graph is the distance travelled, stage by stage"),
            ("B", "Each stage is uniform acceleration or uniform velocity, so the standard equations apply within it and only within it"),
            ("B", "Average speed is the whole distance divided by the whole time, so the slow stages carry more weight"),
            ("A", "Keeping the three stages separate in a table rather than trying to write one equation for the journey")],
    "key": ["average", "speed", "stages", "acceleration"],
    "stem": '<p>A train starts from rest and accelerates uniformly at 0.50 m s<sup>-2</sup> for 20 s. It then runs at constant speed for 30 s, and finally decelerates uniformly at 1.0 m s<sup>-2</sup> until it comes to rest.</p><p>What is the average speed for the whole journey?</p>',
    "opts": ['7.5 m s<sup>-1</sup>', '10 m s<sup>-1</sup>', '8.3 m s<sup>-1</sup>', '9.0 m s<sup>-1</sup>', '5.0 m s<sup>-1</sup>'],
    "ans": 0,
    "distractors": ['correct',
                    'gives the speed during the middle stage, which is the greatest speed reached and not the average over the whole journey',
                    'takes the distance covered while slowing down as the speed times the time instead of half of that, which inflates the total distance to 500 m',
                    'leaves the slowing-down stage out of the total time, so 450 m is divided by 50 s instead of 60 s',
                    'takes the average of the starting and finishing speeds, which would be right only if the speed changed uniformly from start to finish with no constant-speed stage'],
    "profile": {
        "steps": [
            ("solve", "take the first stage on its own and find the speed the train reaches at the end of it"),
            ("solve", "find the distance covered during that acceleration, which is half the final speed times the time"),
            ("solve", "find the distance covered during the constant-speed stage"),
            ("solve", "find how long the third stage lasts, since the time is not given directly but the deceleration rate is"),
            ("solve", "find the distance covered during the deceleration, again half the change in speed times the time"),
            ("solve", "add the three distances to get the whole distance"),
            ("solve", "add the three times to get the whole time"),
            ("solve", "divide the whole distance by the whole time, which is what average speed means"),
            ("check", "confirm the average lies between the lowest and highest speeds of the journey"),
            ("check", "confirm the distance ratio between the three stages, which follows from the areas under the velocity-time graph"),
        ],
        "relations": ["v = u + a t",
                      "s = ½ (u + v) t",
                      "s = v t for the constant stage",
                      "average speed = total distance / total time"],
        "insight": "Average speed is total distance over total time, so it is weighted by how long each speed is held and not by how many stages there are. The train spends 30 of its 60 seconds at the top speed, which pulls the average above the midpoint of the range but well below 10.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(100 + 300 + 50)/60", "want": "7.5"},
    "sol": '''<p><b>What is being tested.</b> Whether you know what an average speed is. It is the whole distance divided by the whole time &#8212; nothing else. It is <i>not</i> the mean of the speeds the train happened to travel at, and it is not the speed at any particular moment.</p>
<p><b>Step 1 — the speed at the end of the first stage.</b> The train starts from rest and accelerates at 0.50 m s<sup>-2</sup> for 20 s:</p>
<div class="formula">v = u + a t = 0 + 0.50 &#215; 20 = 10 m s<sup>-1</sup></div>
<p><b>Step 2 — the distance covered while accelerating.</b> Because the acceleration is uniform, the distance is the mean speed over the stage multiplied by the time. The mean of 0 and 10 is 5.0 m s<sup>-1</sup>:</p>
<div class="formula">s<sub>1</sub> = ½ (u + v) t = ½ &#215; 10 &#215; 20 = 100 m</div>
<p><b>Step 3 — the distance covered at constant speed.</b> No acceleration, so distance is simply speed times time:</p>
<div class="formula">s<sub>2</sub> = v t = 10 &#215; 30 = 300 m</div>
<p><b>Step 4 — how long the train takes to stop.</b> The deceleration is 1.0 m s<sup>-2</sup> and the speed must fall from 10 to 0, so</p>
<div class="formula">t<sub>3</sub> = (change in speed) / a = (10 &#8722; 0) / 1.0 = 10 s</div>
<p>This stage's time is not given in the question; it has to be found. That is the step most likely to be skipped.</p>
<p><b>Step 5 — the distance covered while slowing down.</b> Again the speed falls uniformly, so the mean speed over the stage is 5.0 m s<sup>-1</sup>:</p>
<div class="formula">s<sub>3</sub> = ½ &#215; 10 &#215; 10 = 50 m</div>
<p><b>Step 6 — the whole distance.</b></p>
<div class="formula">s = 100 + 300 + 50 = 450 m</div>
<p><b>Step 7 — the whole time.</b></p>
<div class="formula">t = 20 + 30 + 10 = 60 s</div>
<p><b>Step 8 — divide.</b> This is the definition, and it is the only place the answer comes from:</p>
<div class="formula">average speed = 450 / 60 = 7.5 m s<sup>-1</sup></div>
<p>So <b>Answer: A, 7.5 m s<sup>-1</sup>.</b></p>
<p><b>Step 9 — check that the answer is between the extremes.</b> The train never travels slower than 0 or faster than 10, so the average must lie in between. 7.5 does. Note also where it sits: nearer 10 than 0, which is right, because the train spends half its time at the full 10 m s<sup>-1</sup> and only a third of its time below 10.</p>
<p><b>Step 10 — check the areas, which is the same calculation drawn.</b> A velocity-time graph of this journey is a triangle rising from 0 to 10, a rectangle of height 10, then a triangle falling from 10 back to 0. Their areas are 100 m, 300 m and 50 m, and the areas must be in the ratio 2 : 6 : 1. That ratio is worth checking because it exposes the commonest slip in Step 5: if the final triangle were taken as 100 m instead of 50 m, the ratio would read 2 : 6 : 2, and the last two shapes would be the same size even though the train spends three times as long in the middle as it does slowing down. The graph makes the error visible.</p>
<p><b>Why 7.5 and not 6.7 or 5.</b> Two wrong ways of averaging are worth naming, because both feel natural. Averaging the three stage speeds, (5 + 10 + 5)/3, gives 6.7. Averaging the first and last speeds, (0 + 10)/2, gives 5.0. Both are wrong for the same reason: they give every stage equal weight, when what matters is how long each speed was held. The train held 10 m s<sup>-1</sup> for 30 of its 60 seconds. Any average that does not weight by time will come out too low here, and the further the stage times differ, the worse it gets.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>10 m s<sup>-1</sup></b> is the cruising speed. It is the answer to "what is the maximum speed", which is a different question.</p>
<p>&middot; <b>8.3 m s<sup>-1</sup></b> comes from taking the distance covered while slowing as <code>v t</code> = 10 &#215; 10 = 100 m instead of 50 m. That makes the total 500 m and the average 500/60 = 8.3. The speed is not constant during that stage, so <code>v t</code> does not apply to it.</p>
<p>&middot; <b>9.0 m s<sup>-1</sup></b> comes from leaving the slowing-down time out of the total: 450/50 = 9.0. The train does take that 10 s, so it belongs in the denominator.</p>
<p>&middot; <b>5.0 m s<sup>-1</sup></b> is the mean of the starting and finishing speeds, which would be the right average only if the speed changed uniformly from 0 to 10 across the whole journey and then stopped. It does not: there is a long constant stage in the middle.</p>
<p><b>The trap.</b> Averaging the speeds rather than the distances. Three stages invite a simple mean, and the simple mean is wrong whenever the stages last different lengths of time. The safe habit is to tabulate the distance and the time for each stage separately and add the two columns before dividing &#8212; which is also exactly what the area under the velocity-time graph does.</p>
<p><b>Relevant topics:</b> uniform acceleration; the area under a velocity-time graph; average speed as a time-weighted mean; splitting a journey into stages and keeping them separate.</p>''',
    "trap": "Averaging the three stage speeds, or dividing by the wrong total time. Average speed is the whole distance over the whole time; the stages carry weight in proportion to how long they last.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 7 — C, forces.  An elastic collision with a heavier target.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 7, "id": "S03-07", "module": "C", "diff": 3,
    "topic": "Elastic collision: the speed of the heavier target",
    "rel": [("C", "Conservation of momentum in a head-on collision"),
            ("C", "The relative speed of approach equals the relative speed of separation when the collision is elastic"),
            ("A", "Solving two simultaneous equations by substituting one into the other")],
    "key": ["elastic", "collision", "momentum"],
    "stem": '<p>A particle of mass <code>m</code> moves at speed <code>u</code> along a smooth horizontal track. It collides head-on with a stationary particle of mass <code>3m</code>. The collision is perfectly elastic.</p><p>What is the speed of the particle of mass <code>3m</code> immediately after the collision?</p>',
    "opts": ['<code>u/2</code>',
             '<code>u/3</code>',
             '<code>u/4</code>',
             '<code>u</code>',
             '<code>3u/4</code>'],
    "ans": 0,
    "distractors": ['correct',
                    'assumes the incident particle stops dead, which conserves momentum but throws away most of the kinetic energy',
                    'treats the collision as perfectly inelastic, so the two particles move off stuck together',
                    'gives the heavy particle the whole incident speed, which is what an elastic collision between equal masses would do',
                    'splits the incident speed in proportion to the masses rather than solving the two conservation equations'],
    "profile": {
        "steps": [
            ("relate", "write conservation of momentum for the head-on collision: m u = m v1 + 3m v2"),
            ("relate", "write the elastic condition: the relative speed of approach equals the relative speed of separation, u = v2 - v1"),
            ("eliminate", "rearrange the elastic condition to v1 = v2 - u and substitute it into the momentum equation"),
            ("solve", "u = (v2 - u) + 3v2 gives 2u = 4v2 and so v2 = u/2"),
            ("check", "compute the kinetic energy before and after to confirm it is unchanged"),
        ],
        "relations": ["m u = m v1 + 3m v2", "u = v2 - v1", "v1 = v2 - u", "2u = 4v2"],
        "insight": "The elastic condition is the cheap second equation. Written as approach equals separation it is linear and needs no squares, so substituting it into the momentum equation turns a quadratic problem into one line of algebra.",
        "shape": "conservation",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "2*m*u/(m + 3*m)", "want": "u/2"},
    "sol": '''<p><b>What is being tested.</b> Whether you know both conditions an elastic collision satisfies, and whether you use the elastic condition in the form that keeps the algebra linear.</p>
<p><b>Step 1 — momentum.</b> Take the direction of travel as positive. Before the collision the momentum is <code>m u</code>; afterwards it is <code>m v1 + 3m v2</code>, where <code>v1</code> is the final velocity of the light particle (negative if it rebounds) and <code>v2</code> that of the heavy one:</p>
<div class="formula">m u = m v1 + 3m v2
  u = v1 + 3v2</div>
<p><b>Step 2 — the elastic condition.</b> Kinetic energy is conserved, and it is a standard result that for a head-on elastic collision this is equivalent to the relative speed of approach equalling the relative speed of separation. Before, the approach speed is <code>u</code> (the heavy particle is at rest); after, the separation speed is <code>v2 - v1</code>:</p>
<div class="formula">u = v2 - v1</div>
<p>Using this form rather than writing out the kinetic energy is the point of the question. Written with squares, the two equations give a quadratic and one root has to be discarded; written this way, the substitution is one line.</p>
<p><b>Step 3 — eliminate v1.</b> From the elastic condition, <code>v1 = v2 - u</code>. Substituting:</p>
<div class="formula">u = (v2 - u) + 3v2
u = 4v2 - u
2u = 4v2
v2 = u/2</div>
<p>So <b>Answer: A.</b></p>
<p><b>Step 4 — check by conserving energy.</b> With <code>v2 = u/2</code> the momentum equation gives <code>u = v1 + 3u/2</code>, so <code>v1 = -u/2</code>: the light particle rebounds at half its original speed. Now the energies. Before: <code>(1/2) m u^2</code>. After:</p>
<div class="formula">(1/2) m (-u/2)^2 + (1/2)(3m)(u/2)^2
= (1/8) m u^2 + (3/8) m u^2
= (1/2) m u^2</div>
<p>The energies agree, so the answer is consistent with both conditions. The check is worth doing because it uses the energy statement directly, and so cannot inherit a mistake made in the relative-speed form.</p>
<p><b>Step 5 — does the direction make sense?</b> A light particle hitting a heavy one head-on must bounce back, and <code>v1 = -u/2</code> is a rebound. A ball thrown at a wall does exactly this, and the wall is the limit of an infinitely heavy target. The heavy particle moves forwards slowly, at less than the incident speed, which is also what the limit requires.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>u/3</b> comes from assuming the incident particle stops dead: <code>3m v2 = m u</code> gives <code>v2 = u/3</code>. Momentum is conserved, but most of the kinetic energy has vanished, which an elastic collision does not allow.</p>
<p>&middot; <b>u/4</b> is the perfectly inelastic result: the two move off together at <code>m u/(4m) = u/4</code>. It conserves momentum and is the smallest possible final speed, so it is the wrong end of the range.</p>
<p>&middot; <b>u</b> is what an elastic collision between two <i>equal</i> masses gives: the incident particle stops and the target moves off at the full speed. It is correct for that problem, which is why it is worth having in mind — and it is wrong here only because the masses are unequal.</p>
<p>&middot; <b>3u/4</b> splits the speed in the ratio of the masses, giving the heavy particle three quarters of <code>u</code>. Splitting in proportion to mass has no basis in either conservation law; the momentum equation divides by the total mass only in the perfectly inelastic case.</p>
<p><b>The trap.</b> Using conservation of momentum alone. One equation cannot fix two unknown velocities, so a candidate who stops there is forced to guess — and every guess is one of the four wrong options. The elastic condition is not optional.</p>
<p><b>Relevant topics:</b> conservation of momentum in one dimension; elastic and inelastic collisions; the relative-speed condition; kinetic energy as a check on a collision calculation.</p>''',
    "trap": "Stopping after conservation of momentum. Two unknown final velocities need two equations, and the second one is the elastic condition written as approach equals separation.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 8 — F, waves.  Which harmonic is drawn, and what frequency it corresponds to.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 8, "id": "S03-08", "module": "F", "diff": 2,
    "topic": "A string fixed at both ends: the third harmonic and its frequency",
    "rel": [("F", "A string fixed at both ends carries a whole number of half wavelengths"),
            ("F", "The wave speed, frequency and wavelength relation v = f lambda"),
            ("A", "Counting half-wavelengths in a fixed length without a calculator")],
    "key": ["harmonic", "string", "wavelength"],
    "stem": '<p>A string of length 0.60 m is fixed at both ends and vibrates in the pattern shown, which is its third harmonic. The speed of transverse waves on the string is 120 m/s. {{FIG:s03-08}}</p><p>What is the frequency of this vibration?</p>',
    "opts": ['100 Hz',
             '300 Hz',
             '200 Hz',
             '600 Hz',
             '900 Hz'],
    "ans": 1,
    "distractors": ['reports the fundamental frequency, having read the harmonic number as the number of wavelengths in the string',
                    'correct',
                    'reports the second harmonic, which is the pattern with one fewer node than the one drawn',
                    'takes the wavelength to be one third of the string, counting three full wavelengths rather than three half wavelengths',
                    'takes the fundamental and multiplies it by the harmonic number twice over'],
    "profile": {
        "steps": [
            ("relate", "the string is fixed at both ends, so the ends are nodes and the length holds a whole number of half wavelengths"),
            ("relate", "the third harmonic has three half wavelengths in the length, so L = 3 lambda/2"),
            ("solve", "lambda = 2L/3 = 2 x 0.60/3 = 0.40 m"),
            ("solve", "f = v/lambda = 120/0.40 = 300 Hz"),
            ("check", "the fundamental is 100 Hz and the third harmonic is three times it, which agrees"),
        ],
        "relations": ["L = n lambda/2 with n = 3", "lambda = 2L/3 = 0.40 m", "v = f lambda",
                      "f = 120/0.40"],
        "insight": "A fixed end is a node, so the length always holds a whole number of HALF wavelengths. The harmonic number counts those half wavelengths, which is why the third harmonic has wavelength two thirds of the length and not one third.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "120/(2*0.60/3)", "want": "300"},
    "sol": '''<p><b>What is being tested.</b> Whether you count half wavelengths or full ones. Everything else in the question is a single division, so the whole mark turns on that count.</p>
<p><b>Step 1 — what the fixed ends force.</b> A fixed end cannot move, so it must be a node. A node is a point of zero displacement, and successive nodes are half a wavelength apart. So the string's length must contain a whole number of half wavelengths, never a whole number of full ones:</p>
<div class="formula">L = n x lambda/2,  n = 1, 2, 3, ...</div>
<p><b>Step 2 — read the pattern.</b> The drawing shows three half wavelengths along the string: the string crosses the axis twice in between the ends, so there are four nodes in total (two ends and two in between) and three loops. Three loops means <code>n = 3</code>, which is the third harmonic.</p>
<div class="formula">L = 3 lambda/2
lambda = 2L/3 = 2 x 0.60/3 = 0.40 m</div>
<p><b>Step 3 — get the frequency.</b> The wave speed on the string is fixed by its tension and mass per unit length, and does not change when the string is plucked differently. So the same 120 m/s applies:</p>
<div class="formula">v = f lambda
f = v/lambda = 120/0.40 = 300 Hz</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 4 — check against the fundamental.</b> The fundamental is the case <code>n = 1</code>: <code>lambda = 2L = 1.2 m</code>, so <code>f = 120/1.2 = 100 Hz</code>. The third harmonic should be exactly three times that, and <code>3 x 100 = 300 Hz</code>. The two routes agree, which is a strong check because they use different wavelengths.</p>
<p><b>Step 5 — check the direction.</b> A higher harmonic means more loops, a shorter wavelength, and therefore a higher frequency. Going from 100 Hz to 300 Hz as the pattern goes from one loop to three is the right direction, and the ratio 3 matches the ratio of the loop counts.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>100 Hz</b> is the fundamental. It is what you get by taking the wavelength to be <code>2L</code>, which is the <code>n = 1</code> pattern rather than the one drawn. Since the drawing plainly has three loops, the harmonic number has been dropped rather than misread.</p>
<p>&middot; <b>200 Hz</b> is the second harmonic, <code>lambda = L = 0.60 m</code>. It is one loop short of the pattern drawn, so it is the answer to a question about the graph one step to the left.</p>
<p>&middot; <b>600 Hz</b> is <code>120/(0.60/3) = 120/0.20</code>: the wavelength taken to be <code>L/3</code>, which means three <i>full</i> wavelengths in the string. That is the mistake this question exists to catch. Three full wavelengths would need six nodes, and the drawing has four.</p>
<p>&middot; <b>900 Hz</b> is <code>3 x 300</code>: the harmonic number applied twice, once in the wavelength and once again at the end. Multiplying by three twice is a common slip when the working has the number three in it in two different roles.</p>
<p><b>The trap.</b> Reading the harmonic number as the number of full wavelengths in the string. It is the number of half wavelengths. The drawing is the guard against this: four nodes on the string is three half wavelengths, and three half wavelengths is <code>3 lambda/2</code>.</p>
<p><b>Relevant topics:</b> stationary waves on a string; nodes and antinodes; the harmonic series; <code>v = f lambda</code>; why the wave speed does not change with the harmonic.</p>''',
    "trap": "Counting full wavelengths in the string instead of half wavelengths. Three loops is three half wavelengths, so the wavelength is 2L/3 and not L/3 -- a factor of two, and 600 Hz instead of 300 Hz.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 9 — G, optics.  How deep a pool looks.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 9, "id": "S03-09", "module": "G", "diff": 2,
    "topic": "Apparent depth: how far below the surface a submerged object seems to be",
    "rel": [("G", "Light from the object bends away from the normal as it leaves the water"),
            ("G", "Apparent depth is the real depth divided by the refractive index"),
            ("A", "Dividing by a number between one and two and checking the answer is smaller")],
    "key": ["refraction", "apparent", "depth"],
    "stem": '<p>A stone lies on the bottom of a pool of water 2.4 m deep. The refractive index of water is 1.5. An observer looking straight down from directly above sees the stone.</p><p>At what depth below the surface does the stone appear to be?</p>',
    "opts": ['3.6 m',
             '2.4 m',
             '0.80 m',
             '1.2 m',
             '1.6 m'],
    "ans": 4,
    "distractors": ['multiplies by the refractive index instead of dividing by it, which would make the pool look deeper than it is',
                    'reports the real depth, as though the bending of the light made no difference to where the stone appears',
                    'divides the real depth by twice the refractive index, as though the light were bent twice over',
                    'halves the real depth rather than dividing it by the refractive index',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "light leaving the water bends away from the normal, so the ray reaching the eye appears to come from a point nearer the surface"),
            ("relate", "for near-normal viewing the apparent depth is the real depth divided by the refractive index"),
            ("solve", "apparent depth = 2.4/1.5 = 1.6 m"),
            ("check", "the answer is smaller than the real depth, as refraction requires, and the factor is the index"),
        ],
        "relations": ["n = real/apparent", "apparent = 2.4/1.5", "apparent < real"],
        "insight": "Refraction at a plane surface makes a submerged object look shallower by exactly the factor of the refractive index, when the observer looks straight down. The direction is fixed by the physics, so an answer larger than the real depth is already wrong.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "2.4/1.5", "want": "1.6"},
    "sol": '''<p><b>What is being tested.</b> A single relation, applied the right way round. The physics fixes the direction, so the question is really about whether you divide or multiply — and one of those can be ruled out before any arithmetic.</p>
<p><b>Step 1 — what the light does.</b> Light travelling from water into air speeds up, and when a wave speeds up as it crosses a boundary it bends <i>away</i> from the normal. The ray that reaches the observer's eye therefore appears to have come from a point higher up than the stone itself. The stone looks shallower than it is. This is worth fixing first, because it rules out half the options immediately.</p>
<p><b>Step 2 — the relation.</b> For an observer looking straight down, the geometry of the ray gives a particularly clean result:</p>
<div class="formula">n = real depth / apparent depth
so  apparent depth = real depth / n</div>
<p>The refractive index is greater than one, so dividing by it makes the apparent depth smaller than the real one, which is the direction step 1 required. The two agree.</p>
<p><b>Step 3 — put the numbers in.</b></p>
<div class="formula">apparent depth = 2.4/1.5 = 1.6 m</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 4 — check the factor.</b> The index is 1.5, so the stone should look two thirds as far away as it is: <code>2.4 x (2/3) = 1.6</code>. Multiplying by two thirds and dividing by 1.5 are the same operation, so the two routes agree. The answer also sits sensibly between the real depth and the surface, which is where an apparent depth always is.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3.6 m</b> is <code>2.4 x 1.5</code>: the index used as a multiplier. It is the most tempting wrong answer because the arithmetic is identical in shape, but it makes the pool look <i>deeper</i> than it is, which refraction cannot do. This is the distractor the direction check in step 1 eliminates.</p>
<p>&middot; <b>2.4 m</b> is the real depth, unchanged. It is what you get if the refraction at the surface is forgotten altogether — the answer to a question about a stone in a vacuum.</p>
<p>&middot; <b>0.80 m</b> is <code>2.4/3.0</code>: the index applied twice, as though the ray were bent at two surfaces each contributing a full factor. There is only one surface here.</p>
<p>&middot; <b>1.2 m</b> is <code>2.4/2</code>: the depth simply halved, which would be right for an index of exactly 2 and not for 1.5.</p>
<p><b>The trap.</b> Remembering that "something is divided by n" without remembering which thing. The safe route is to fix the direction from the physics first — a submerged object always looks shallower — and then choose the operation that produces a smaller number.</p>
<p><b>Relevant topics:</b> refraction at a plane surface; refractive index; why an object in water looks raised; near-normal viewing and the small-angle condition that makes the relation exact.</p>''',
    "trap": "Multiplying by the refractive index. Dividing is right, because a submerged object always looks shallower, and the direction can be fixed from the physics before any arithmetic is done.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 10 — H, circuits.  A potential divider with something hanging off it.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 10, "id": "S03-10", "module": "H", "diff": 3,
    "topic": "A loaded potential divider: the voltage actually delivered",
    "rel": [("H", "Combining the load with the resistor it sits across, in parallel"),
            ("H", "The unloaded divider ratio as a first approximation, and why the load spoils it"),
            ("A", "Reducing a two-step resistance calculation before touching the numbers")],
    "key": ["divider", "loading", "parallel"],
    "stem": '<p>The circuit below shows a 12 V supply connected to a 6.0 k&Omega; resistor in series with a 3.0 k&Omega; resistor. A 3.0 k&Omega; load is connected in parallel with the 3.0 k&Omega; resistor. {{FIG:s03-10}}</p><p>What is the potential difference across the load?</p>',
    "opts": ['4.0 V',
             '4.8 V',
             '3.0 V',
             '2.4 V',
             '1.2 V'],
    "ans": 3,
    "distractors": ['computes the divider as though nothing were connected across the lower resistor, which is the standard unloaded-divider error',
                    'puts the load in parallel with the 6.0 k&Omega; resistor instead of the 3.0 k&Omega; one',
                    'assumes the two equal 3.0 k&Omega; resistances share the supply equally, ignoring the 6.0 k&Omega; resistor above them',
                    'correct',
                    'halves the correct answer, as though the load took only half of the current reaching its junction'],
    "profile": {
        "steps": [
            ("relate", "the load sits across the 3.0 k resistor, so those two must be combined in parallel first"),
            ("relate", "two equal resistors in parallel give half of one, so the pair is 1.5 k"),
            ("relate", "the circuit is then 6.0 k in series with 1.5 k, a total of 7.5 k"),
            ("solve", "I = 12/7.5 k = 1.6 mA, and V across the load = 1.6 mA x 1.5 k = 2.4 V"),
            ("check", "the loaded output is below the 4.0 V the unloaded divider would give, as loading must reduce it"),
            ("check", "the load equals the resistor it sits across, so it takes half the current reaching that junction"),
        ],
        "relations": ["3.0k || 3.0k = 1.5k", "R_total = 6.0k + 1.5k = 7.5k",
                      "I = 12/7.5k = 1.6 mA", "V = I x 1.5k = 2.4 V"],
        "insight": "A load across the lower arm changes the lower arm. The divider ratio must be recomputed with the parallel combination in place, and the answer must come out BELOW the unloaded value -- that direction is a free check.",
        "shape": "circuit-reduction",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "12*1.5/(6.0 + 1.5)", "want": "2.4"},
    "sol": '''<p><b>What is being tested.</b> Whether you notice that the load is part of the circuit, not an observer of it. A divider's output voltage is only the simple ratio while nothing is drawing current from it.</p>
<p><b>Step 1 — what is in parallel with what.</b> The load is connected across the 3.0 k&Omega; resistor, so the two sit between the same two points and must be combined in parallel. That combination is the new lower arm of the divider:</p>
<div class="formula">3.0k || 3.0k = (3.0 x 3.0)/(3.0 + 3.0) = 9.0/6.0 = 1.5 k&Omega;</div>
<p>Two equal resistors in parallel give half of one, so 1.5 k&Omega; can be written down without any working at all.</p>
<p><b>Step 2 — the total resistance.</b> The upper resistor and the new lower arm are in series, since all the current from the supply passes through both:</p>
<div class="formula">R_total = 6.0 + 1.5 = 7.5 k&Omega;</div>
<p><b>Step 3 — the current.</b></p>
<div class="formula">I = V/R = 12/7.5 k&Omega; = 1.6 mA</div>
<p><b>Step 4 — the voltage across the load.</b> All 1.6 mA passes through the 1.5 k&Omega; combination, and the load is part of that combination, so the voltage across the load is the voltage across the pair:</p>
<div class="formula">V = I R = 1.6 mA x 1.5 k&Omega; = 2.4 V</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 5 — the check that costs nothing.</b> Without the load, the divider would give <code>12 x 3.0/9.0 = 4.0 V</code>. Connecting a load can only ever pull the output down, because it draws current and adds a parallel path. So the answer must be below 4.0 V, and 2.4 V is. It must also be above zero, and it is. An answer of 4.8 V or 6.0 V would be eliminated by this reasoning alone, without any calculation.</p>
<p><b>Step 6 — does the load take a sensible share?</b> The load's 3.0 k&Omega; equals the resistor it sits across, so it takes half the current reaching that junction. The pair's 1.5 k&Omega; against the 6.0 k&Omega; above means the lower arm gets only one fifth of the supply: <code>12/5 = 2.4 V</code>. That agrees, and it is a quicker route once the parallel combination is recognised.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>4.0 V</b> is the unloaded divider, <code>12 x 3.0/9.0</code>. It is the single most common error with this circuit, and it is genuinely wrong: it uses 3.0 k&Omega; as the lower arm when the lower arm is 1.5 k&Omega;.</p>
<p>&middot; <b>4.8 V</b> puts the load across the 6.0 k&Omega; resistor. That gives <code>6.0k || 3.0k = 2.0k</code>, a total of 5.0 k&Omega;, a current of 2.4 mA, and 2.4 mA across the 2.0 k&Omega; combination, which is 4.8 V. It is a fully worked answer to the wrong circuit.</p>
<p>&middot; <b>3.0 V</b> assumes the supply divides equally between the 6.0 k&Omega; resistor and the load's branch. That would need the two to be equal, and 6.0 k&Omega; is not equal to 1.5 k&Omega;.</p>
<p>&middot; <b>1.2 V</b> is exactly half of the correct answer: the load taking half of what actually reaches it, which double-counts the parallel split.</p>
<p><b>The trap.</b> Treating the load as a measuring instrument that reads the divider's output without affecting it. A real voltmeter has a very high resistance precisely so that this approximation is good; a 3.0 k&Omega; load does not, and the whole question is about the difference.</p>
<p><b>Relevant topics:</b> the potential divider; loading and output resistance; parallel and series combination; the direction check that loading always reduces an output voltage.</p>''',
    "trap": "Reading the divider as 12 x 3.0/9.0 = 4.0 V. The load changes the lower arm to 1.5 k, and a loaded divider always delivers less than an unloaded one.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 11 — J, thermal.  DEEP (10 moves).  Ice into warm water, where the first thing
# to establish is whether the heat available can melt all the ice at all.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 11, "id": "S03-11", "module": "J", "diff": 3,
    "topic": "Ice at -10 C into water at 30 C: whether all the ice can melt, and what is left if it cannot",
    "rel": [("J", "The heat needed to warm a solid is its mass times its specific heat capacity times the temperature rise"),
            ("J", "The heat needed to melt a solid is its mass times the specific latent heat of fusion, with no temperature change during the melting"),
            ("J", "The heat given out by cooling water is found the same way, with the water's own specific heat capacity"),
            ("A", "Comparing the heat available with the heat required BEFORE assuming a final temperature, because the answer is a condition and not a number")],
    "key": ["latent", "fusion", "ice", "mixture"],
    "stem": '<p>0.20 kg of ice at &#8722;10 &#176;C is added to 0.40 kg of water at 30 &#176;C in an insulated container. The specific heat capacity of ice is 2100 J kg<sup>-1</sup> K<sup>-1</sup>, of water is 4200 J kg<sup>-1</sup> K<sup>-1</sup>, and the specific latent heat of fusion of ice is 3.3 &#215; 10<sup>5</sup> J kg<sup>-1</sup>.</p><p>What is the final state of the mixture?</p>',
    "opts": ['At 0 &#176;C, with 0.060 kg of ice remaining',
             'At 0 &#176;C, with all the ice melted',
             'At 0 &#176;C, with 0.14 kg of ice remaining',
             'At 22 &#176;C, with all the ice melted',
             'At 0 &#176;C, with none of the ice melted'],
    "ans": 0,
    "distractors": ['correct',
                    'assumes the water holds enough heat to melt all the ice without checking, when 5.0 &#215; 10<sup>4</sup> J is available against 7.0 &#215; 10<sup>4</sup> J needed',
                    'reports the mass that DID melt as the mass that remains, which is the same slip as reading the wrong column of a subtraction',
                    'ignores the latent heat entirely and balances specific heats alone, which gives a spurious temperature of 22 &#176;C',
                    'concludes that because the available heat is less than the heat needed to melt everything, nothing melts at all, overlooking the ice that warms to 0 &#176;C first and the partial melting that follows'],
    "profile": {
        "steps": [
            ("solve", "find the heat needed to bring the ice from its starting temperature up to 0 degrees"),
            ("solve", "find the heat needed to melt ALL of that ice once it is at 0 degrees"),
            ("solve", "add those two to get the heat required to turn the whole lot into water at 0 degrees"),
            ("solve", "find the heat the warm water can give out as it cools to 0 degrees"),
            ("relate", "compare the heat available with the heat required, which is the decision the whole question turns on"),
            ("relate", "conclude from that comparison that the final temperature is 0 degrees and that some ice survives"),
            ("solve", "subtract the warming heat from the heat available, leaving the heat that can actually be spent on melting"),
            ("solve", "divide by the latent heat to get the mass that melts"),
            ("solve", "subtract that from the starting mass to get the mass of ice left"),
            ("check", "confirm the energy balance closes, and that the surviving mass is positive but smaller than the starting mass"),
        ],
        "relations": ["Q = m c &#916;T",
                      "Q = m L",
                      "heat lost by the water = heat gained by the ice",
                      "mass melted = Q_available / L"],
        "insight": "A mixture question with a change of state has two possible answers, and which one applies is decided before any temperature is calculated. Compare the heat the warm body can supply with the heat the cold body needs to complete its change of state; only then does a final temperature exist to be found.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "0.20 - (0.40*4200*30 - 0.20*2100*10)/330000", "want": "0.06"},
    "sol": '''<p><b>What is being tested.</b> Whether you check that the heat available is enough before assuming the ice all melts. Writing down "heat lost equals heat gained" and solving for a temperature is the standard method, and it silently assumes the ice finishes as water. Here it does not, and the assumption has to be tested first.</p>
<p><b>Step 1 — heat the ice up to 0 &#176;C.</b> The ice starts at &#8722;10 &#176;C and cannot melt until it reaches 0 &#176;C. That warming costs</p>
<div class="formula">Q<sub>1</sub> = m c<sub>ice</sub> &#916;T = 0.20 &#215; 2100 &#215; 10 = 4200 J</div>
<p><b>Step 2 — melt all of that ice.</b> Melting happens at a fixed temperature, so the temperature change is zero and only the latent heat matters:</p>
<div class="formula">Q<sub>2</sub> = m L = 0.20 &#215; 3.3 &#215; 10<sup>5</sup> = 6.6 &#215; 10<sup>4</sup> J</div>
<p><b>Step 3 — the whole cost of turning the ice into water at 0 &#176;C.</b></p>
<div class="formula">Q<sub>required</sub> = 4200 + 66000 = 7.0 &#215; 10<sup>4</sup> J</div>
<p><b>Step 4 — what the warm water can supply.</b> The most the water can give up is what it releases on cooling all the way to 0 &#176;C, since the mixture cannot end up below that while ice remains:</p>
<div class="formula">Q<sub>available</sub> = m c<sub>water</sub> &#916;T = 0.40 &#215; 4200 &#215; 30 = 5.0 &#215; 10<sup>4</sup> J</div>
<p><b>Step 5 — the comparison, which decides the whole question.</b></p>
<div class="formula">Q<sub>available</sub> = 5.0 &#215; 10<sup>4</sup> J  &lt;  7.0 &#215; 10<sup>4</sup> J = Q<sub>required</sub></div>
<p>There is not enough heat to melt all the ice. This single line is the question. Everything after it is bookkeeping; everything before it was setup.</p>
<p><b>Step 6 — so what IS the final temperature?</b> Since unmelted ice remains, the mixture is at the only temperature at which ice and water coexist in equilibrium at ordinary pressure: 0 &#176;C. The warm water has been cooled to 0 &#176;C and can go no lower, because any further heat it gave up would have to come from freezing the water that is already there, and the ice is still taking heat in, not giving it out.</p>
<p><b>Step 7 — how much heat is actually spent on melting.</b> Of the 5.0 &#215; 10<sup>4</sup> J the water gives up, 4200 J goes into warming the ice to 0 &#176;C. Only the remainder can melt anything:</p>
<div class="formula">Q<sub>melting</sub> = 50000 &#8722; 4200 = 4.6 &#215; 10<sup>4</sup> J</div>
<p><b>Step 8 — the mass that melts.</b></p>
<div class="formula">m<sub>melted</sub> = Q<sub>melting</sub> / L = 46000 / (3.3 &#215; 10<sup>5</sup>) = 0.14 kg</div>
<p><b>Step 9 — the mass of ice left over.</b></p>
<div class="formula">m<sub>ice</sub> = 0.20 &#8722; 0.14 = 0.060 kg</div>
<p>So <b>Answer: A.</b> The mixture ends at 0 &#176;C with 0.060 kg of ice still present.</p>
<p><b>Step 10 — check the energy balance closes.</b> The water gave up 5.0 &#215; 10<sup>4</sup> J. The ice took 4200 J to warm and 46000 J to melt 0.14 kg, and 4200 + 46000 = 50200 J, which matches the 50000 J available to the accuracy of the latent heat used. The surviving mass is positive, so the answer is consistent with the conclusion of Step 5, and it is smaller than 0.20 kg, so some ice did melt. Both of those had to be true, and both are.</p>
<p><b>A note on the answer's shape.</b> Because the final temperature is pinned at 0 &#176;C by the leftover ice, the answer is not a temperature but a <i>mass</i>. Questions of this kind are usually asked so that one of the two possibilities &#8212; everything melts, or ice survives &#8212; is clearly true, and the skill being tested is working out which. Once the comparison in Step 5 has been made, the rest is arithmetic on a single equation.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>At 0 &#176;C with all the ice melted</b> is the answer you get by assuming rather than checking. It is the most attractive wrong option because it is the outcome most mixture questions have.</p>
<p>&middot; <b>At 0 &#176;C with 0.14 kg of ice remaining</b> takes the mass that melted and reports it as the mass that is left. The subtraction in Step 9 is the whole difference.</p>
<p>&middot; <b>At 22 &#176;C with all the ice melted</b> comes from leaving the latent heat out altogether and balancing <code>m c &#916;T</code> on both sides. Then 0.40 &#215; 4200 &#215; (30 &#8722; T) = 0.20 &#215; 2100 &#215; (T + 10), which solves to 22 &#176;C. It is a perfectly tidy number and it is meaningless here, because it describes ice that melts without any heat being needed to melt it.</p>
<p>&middot; <b>At 0 &#176;C with none of the ice melted</b> comes from the comparison in Step 5 read too strongly. The available heat is indeed less than the heat needed to melt everything &#8212; but that does not mean it melts nothing. 5.0 &#215; 10<sup>4</sup> J is plenty to warm the ice and melt most of it.</p>
<p><b>The trap.</b> Starting with "heat lost equals heat gained" and solving for the final temperature. That equation assumes a single unknown temperature and a single final state, and it cannot represent "some ice remains at 0 &#176;C". The order matters: check whether a complete change of state is possible, then either solve for a temperature or work out how much survives.</p>
<p><b>Relevant topics:</b> specific heat capacity; specific latent heat of fusion; mixtures and the conservation of energy; changes of state and the temperature plateau; testing an assumption before using it.</p>''',
    "trap": "Assuming the ice all melts and solving for a temperature. The heat available, 5.0 x 10^4 J, is less than the 7.0 x 10^4 J needed, so the mixture ends at 0 C with ice remaining.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 12 — K, nuclear.  Why nuclear density does not depend on the size of the nucleus.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 12, "id": "S03-12", "module": "K", "diff": 2,
    "topic": "Nuclear density: why it is the same in every nucleus",
    "rel": [("K", "The nuclear radius law r = r0 A^(1/3)"),
            ("K", "Density as mass divided by volume, with the mass proportional to A"),
            ("A", "Cancelling a common factor of A from a numerator and a denominator")],
    "key": ["nuclear", "density", "radius"],
    "stem": '<p>The radius of a nucleus is given by <code>r = r<sub>0</sub>A<sup>1/3</sup></code>, where <code>A</code> is the nucleon number and <code>r<sub>0</sub></code> is a constant.</p><p>How does the density of nuclear matter change when <code>A</code> increases from 27 to 216?</p>',
    "opts": ['It is unchanged',
             'It increases by a factor of 8',
             'It decreases by a factor of 8',
             'It increases by a factor of 2',
             'It decreases by a factor of 2'],
    "ans": 0,
    "distractors": ['correct',
                    'scales the density with the nucleon number, forgetting that the volume grows in step with the mass',
                    'inverts the previous error, treating the volume as growing faster than the mass so the density falls',
                    'takes the cube root of the change in A and applies it to the density rather than to the radius',
                    'applies the change in the radius to the density directly, when the density depends on the volume and so on the cube of the radius'],
    "profile": {
        "steps": [
            ("relate", "the mass of a nucleus is proportional to A, since nearly all of it is in the nucleons"),
            ("relate", "the volume is proportional to the cube of the radius, so V is proportional to (A^(1/3))^3 = A"),
            ("eliminate", "the density is mass over volume, so A appears on top and underneath"),
            ("solve", "the A cancels, leaving a density that depends only on r0 and the nucleon mass"),
            ("check", "A changing from 27 to 216 is a factor of 8 in A, and the density does not move at all"),
        ],
        "relations": ["m proportional to A", "V proportional to r^3 proportional to A",
                      "rho = m/V proportional to A/A", "rho = m_n/((4/3) pi r0^3)"],
        "insight": "The radius law is written as the cube root of A for exactly this reason: cubing it gives a volume proportional to A, so the mass and the volume grow together and the density cancels out of the problem.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "(216*1)/(r0^3*216)", "want": "1/r0^3"},
    "sol": '''<p><b>What is being tested.</b> Whether you can follow a proportionality through a cube. The radius law is given, so nothing has to be remembered; the whole question is what happens when it is put into the density.</p>
<p><b>Step 1 — the mass.</b> A nucleus is made of <code>A</code> nucleons, each of very nearly the same mass, and the electrons contribute almost nothing. So:</p>
<div class="formula">m proportional to A</div>
<p><b>Step 2 — the volume.</b> A nucleus is very nearly spherical, so its volume is proportional to the cube of its radius:</p>
<div class="formula">V proportional to r^3
r = r0 A^(1/3), so r^3 = r0^3 A
V proportional to r0^3 A</div>
<p>The cube root in the radius law exists precisely so that the volume comes out proportional to <code>A</code>, and not to some awkward power of it. That is worth noticing: the law is written that way because that is the experimental fact, and the convenient algebra is a consequence of the physics rather than the other way round.</p>
<p><b>Step 3 — divide.</b></p>
<div class="formula">rho = m/V
    proportional to A/(r0^3 A)
    = 1/r0^3</div>
<p>The <code>A</code> cancels. The density depends only on the constant <code>r<sub>0</sub></code> and the nucleon mass, and not on how big the nucleus is. So <b>Answer: A</b> — it is unchanged.</p>
<p><b>Step 4 — check with the numbers given.</b> Going from <code>A = 27</code> to <code>A = 216</code> multiplies <code>A</code> by <code>216/27 = 8</code>. The mass goes up by 8 and the volume also goes up by 8, because the volume is proportional to <code>A</code>. So the ratio is <code>8/8 = 1</code>. The density does not move.</p>
<p><b>Step 5 — why this is a striking result.</b> Nuclear matter has the same density in a hydrogen nucleus as in a lead nucleus, about <code>2 x 10^17 kg/m^3</code>. It is a liquid-like incompressibility: adding more nucleons makes the nucleus bigger rather than denser. That is a real physical fact about the strong force, and this question is a way of seeing it fall out of the radius law.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>Increases by a factor of 8</b> scales the density with <code>A</code>. It uses the mass growth and forgets the volume growth, which is the whole content of the question.</p>
<p>&middot; <b>Decreases by a factor of 8</b> is the inverse: it uses the volume growth and forgets the mass. It would be right if the volume grew like <code>A^2</code>, and the radius law is the statement that it does not.</p>
<p>&middot; <b>Increases by a factor of 2</b> applies the cube root of 8 to the density. The cube root of 8 is 2, but it is the <i>radius</i> that doubles, not the density. The density depends on the cube of the radius, and the cube of 2 is 8, which is exactly what cancels the mass.</p>
<p>&middot; <b>Decreases by a factor of 2</b> applies the radius change to the density with the sign reversed. The density has no dependence on the radius left in it at all, so neither a factor of 2 nor its reciprocal can appear.</p>
<p><b>The trap.</b> Treating the density as though it followed the radius. The radius grows as <code>A^(1/3)</code> and the density does not grow at all, because the mass grows in step with the volume. Whenever a quantity cancels, it is worth saying out loud which two things cancelled — here, the <code>A</code> in the mass against the <code>A</code> in the volume.</p>
<p><b>Relevant topics:</b> the nuclear radius law; proportional reasoning through a cube; density as mass over volume; why all nuclei have the same density.</p>''',
    "trap": "Scaling the density with A. The mass goes as A and the volume goes as A too, because the radius law carries a cube root, so the two cancel and the density is independent of the size of the nucleus.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 13 — A, toolkit.  A scaling law stated as a power of N.  The answer is an
# expression, not a number, which is how the real paper asks its scaling questions.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 13, "id": "S03-13", "module": "A", "diff": 3,
    "topic": "Scaling: by what power of N the total surface area grows when a cube is cut into N cubes",
    "rel": [("A", "Cutting a solid into N equal pieces scales every length by one and the same factor, and that factor is the cube root of N"),
            ("A", "Surface area goes as the square of a length, so it goes as the two-thirds power of a volume"),
            ("A", "A result stated as a power of N can be checked against a single numerical case worked out from scratch"),
            ("A", "Multiplying by N and dividing by N to the two thirds leaves a clean power of N, which is what makes the answer presentable")],
    "key": ["scaling", "area", "volume", "power"],
    "stem": '<p>A solid cube is cut up into <code>N</code> identical smaller cubes, where <code>N</code> is a perfect cube.</p><p>By what factor does the total surface area of all the pieces together exceed the surface area of the original cube?</p>',
    "opts": ['N<sup>1/3</sup>', 'N<sup>2/3</sup>', 'N', 'N<sup>1/2</sup>', 'N<sup>3</sup>'],
    "ans": 0,
    "distractors": ['correct',
                    'gives the surface area of ONE of the small cubes as a fraction of the original, which forgets to multiply back up by the number of pieces',
                    'takes the total area as proportional to the number of pieces, which would be right only if each piece kept the original size',
                    'uses a square root, which belongs to a flat shape being sliced into strips rather than to a solid divided in three dimensions',
                    'cubes the number of pieces instead of taking its cube root, so the factor runs away in the wrong direction'],
    "profile": {
        "steps": [
            ("relate", "note that equal pieces of a cube must be similar to it, so every length is divided by one common factor"),
            ("solve", "get that factor from the volumes, since N pieces each of volume V/N means each side is the cube root of N times smaller"),
            ("solve", "write the side of one small cube in terms of the original side"),
            ("solve", "write the surface area of one small cube, which goes as the square of its side"),
            ("solve", "multiply by N to get the total surface area of all the pieces together"),
            ("solve", "collect the powers of N, using that N times N to the minus two thirds is N to the plus one third"),
            ("solve", "divide by the original surface area to leave the factor that was asked for"),
            ("check", "test the formula on a case whose answer can be found by inspection, cutting the cube into eight"),
        ],
        "relations": ["side of a small cube = L N<sup>-1/3</sup>",
                      "surface area of one small cube = 6 (L N<sup>-1/3</sup>)<sup>2</sup>",
                      "total area = N &#215; (area of one small cube)",
                      "factor = N<sup>1/3</sup>"],
        "insight": "Cutting a solid up multiplies its surface area by the cube root of the number of pieces. The cube root appears because the division happens in three dimensions while the quantity being measured lives in two, and the mismatch between those two dimensions is the whole content of the question.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "8*6*(1/2)*(1/2)/6", "want": "2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can tell a length from an area from a volume. The pieces are smaller by a factor in <i>length</i>, but the quantity asked about is an <i>area</i>, and the two do not scale by the same power.</p>
<p><b>Step 1 — what cutting a cube into N cubes does to a length.</b> The pieces are equal and similar to the original, so a single factor <code>k</code> divides every length: side, face diagonal, everything. Finding <code>k</code> is the first job.</p>
<p><b>Step 2 — get that factor from the volumes.</b> Volume goes as the cube of a length, and the N pieces together have the same total volume as the original. So each piece has volume <code>V/N</code>, and</p>
<div class="formula">k<sup>3</sup> = 1/N  &#8658;  k = N<sup>-1/3</sup></div>
<p>If the original side is <code>L</code>, one small cube has side</p>
<div class="formula">L N<sup>-1/3</sup></div>
<p><b>Step 3 — the surface area of one small cube.</b> A cube's surface is six faces, each the square of its side:</p>
<div class="formula">A<sub>one</sub> = 6 (L N<sup>-1/3</sup>)<sup>2</sup> = 6 L<sup>2</sup> N<sup>-2/3</sup></div>
<p>Notice the exponent: squaring a length divides the area by <code>N<sup>2/3</sup></code>, not by <code>N</code>. That mismatch is where the question is won or lost.</p>
<p><b>Step 4 — multiply up to all N pieces.</b></p>
<div class="formula">A<sub>total</sub> = N &#215; 6 L<sup>2</sup> N<sup>-2/3</sup></div>
<p><b>Step 5 — collect the powers of N.</b> Adding the indices, 1 &#8722; 2/3 = 1/3:</p>
<div class="formula">A<sub>total</sub> = 6 L<sup>2</sup> N<sup>1/3</sup></div>
<p><b>Step 6 — divide by the original surface area.</b> The original cube has area <code>6L<sup>2</sup></code>, so the factor is</p>
<div class="formula">A<sub>total</sub> / A<sub>original</sub> = N<sup>1/3</sup></div>
<p>So <b>Answer: A, N<sup>1/3</sup>.</b></p>
<p><b>Step 7 — test it on a case you can picture.</b> Cut a cube into eight by halving it in each direction. Each piece has side <code>L/2</code> and surface area <code>6(L/2)<sup>2</sup> = 1.5 L<sup>2</sup></code>. Eight of them give <code>12 L<sup>2</sup></code>, against the original <code>6 L<sup>2</sup></code>, so the factor is 2. And <code>N<sup>1/3</sup> = 8<sup>1/3</sup> = 2</code>. The formula and the picture agree, which is the check that matters when an answer is a power rather than a number.</p>
<p><b>Step 8 — check the direction and the size.</b> Cutting a solid up can only expose more surface, never less, so the factor must exceed 1 for any <code>N</code> greater than 1. Every candidate power of <code>N</code> with a positive index satisfies that, so this check does not separate the options &#8212; but it does rule out any answer that would come out below 1, and it is worth doing anyway because a slip in the sign of an index is easy to make and easy to miss.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>N<sup>2/3</sup></b> is the ratio of one small cube's area to the original. It is a real quantity and it is the wrong one: the question asks about all the pieces together. It is always smaller than the right answer, which is the quickest way to reject it.</p>
<p>&middot; <b>N</b> would be right if each of the N pieces kept the original area, which would mean the cube had grown rather than been cut. It is far too large.</p>
<p>&middot; <b>N<sup>1/2</sup></b> is what a two-dimensional argument would give: slicing a square into N equal squares multiplies the total perimeter by <code>N<sup>1/2</sup></code>. That is a genuinely correct result for the wrong problem, and it is the most instructive of the four, because it shows exactly what the third dimension is doing.</p>
<p>&middot; <b>N<sup>3</sup></b> cubes the number of pieces instead of taking its cube root. With N = 1000 it would predict a factor of a billion rather than ten, which the sanity check on the direction catches at once.</p>
<p><b>The trap.</b> Assuming that because the pieces are N times smaller in number they must be N times smaller in size. They are not: the length scale falls as the cube root, the area of one piece falls as the two-thirds power, and the total area rises as the cube root. Keeping the three exponents apart is the entire skill, and writing each one down explicitly is the way to keep them apart.</p>
<p><b>Relevant topics:</b> scaling of length, area and volume; similar solids; powers and their indices; checking a symbolic result against a numerical case; why a powder reacts faster than a lump.</p>''',
    "trap": "Treating the area as if it scaled with the same power as the number of pieces, or as the square of it. Lengths fall as the cube root of N, one piece's area falls as the two-thirds power, and the total area rises as the cube root.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 14 — B, kinematics.  A deceleration proportional to the speed.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 14, "id": "S03-14", "module": "B", "diff": 3,
    "topic": "A particle whose deceleration is proportional to its speed: the distance to rest",
    "rel": [("B", "Writing acceleration as v dv/dx to change the variable from time to distance"),
            ("B", "A speed that decays exponentially never quite reaches zero, so the distance is a limit"),
            ("A", "Integrating a simple power and evaluating it between the two limits")],
    "key": ["variable", "deceleration", "distance"],
    "stem": '<p>A particle moves along a straight line with speed <code>v</code>. Throughout its motion its acceleration is <code>a = -kv</code>, where <code>k</code> is a positive constant.</p><p>The particle has speed <code>u</code> at <code>t = 0</code>. How far does it travel before coming to rest?</p>',
    "opts": ['<code>uk</code>',
             '<code>u/k</code>',
             '<code>u/(2k)</code>',
             '<code>2u/k</code>',
             '<code>u/(k ln2)</code>'],
    "ans": 1,
    "distractors": ['multiplies by k rather than dividing, which turns a rate constant into an inverse rate constant',
                    'correct',
                    'halves the answer, as though the particle decelerated uniformly and so took the same distance to lose its speed as it would at a constant rate',
                    'doubles the answer, treating the total distance as twice the distance covered while the speed falls from u to u/2',
                    'uses the time taken for the speed to halve rather than the distance to rest, which brings in a logarithm'],
    "profile": {
        "steps": [
            ("relate", "the acceleration is given in terms of v, so rewrite it as a = v dv/dx to get an equation in x instead of t"),
            ("relate", "v dv/dx = -kv, and dividing by v leaves dv/dx = -k"),
            ("eliminate", "the equation is now separable: dx = -dv/k"),
            ("solve", "integrate between v = u and v = 0 to get x = u/k"),
            ("check", "confirm the dimensions and confirm the answer grows with u and falls as k grows"),
            ("check", "integrate the exponential decay in time instead, and confirm the same u/k comes out"),
        ],
        "relations": ["a = v dv/dx", "v dv/dx = -k v", "dv/dx = -k", "x = -[v/k] from u to 0 = u/k"],
        "insight": "The trick is to stop working with time. Writing acceleration as v dv/dx turns a statement about speed against time into one about speed against distance, and that version separates immediately.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "(0 - u)/(-k)", "want": "u/k"},
    "sol": '''<p><b>What is being tested.</b> Whether you can change the independent variable when the question asks for a distance but the law is about speed. Time is not mentioned anywhere in the answer, which is a strong hint that time should be eliminated.</p>
<p><b>Step 1 — why the given form is awkward.</b> The law <code>a = -kv</code> relates acceleration to speed. In its natural form <code>dv/dt = -kv</code> it tells you how the speed falls with <i>time</i>, and solving it gives <code>v = u e^(-kt)</code>. That is true and useful, but it is not what is asked for, and turning it into a distance needs a further integration. There is a shorter route.</p>
<p><b>Step 2 — change the variable.</b> Acceleration can be written in two ways, and the second is the one for a question about distance:</p>
<div class="formula">a = dv/dt = v dv/dx</div>
<p>The identity comes from the chain rule, <code>dv/dt = (dv/dx)(dx/dt)</code>, and <code>dx/dt</code> is <code>v</code>. Substituting the given law:</p>
<div class="formula">v dv/dx = -k v</div>
<p><b>Step 3 — divide by v.</b> For <code>v</code> not zero this gives:</p>
<div class="formula">dv/dx = -k</div>
<p>Remarkably, the speed has dropped out. The statement is now that the speed falls at a constant rate <i>with distance</i> — a very different statement from a constant deceleration in time, and the reason the answer is not the familiar <code>u^2/(2a)</code>.</p>
<p><b>Step 4 — integrate.</b> Separating and integrating between the starting speed <code>u</code> and rest:</p>
<div class="formula">x = integral of dx = integral from u to 0 of (-dv/k)
  = -[v/k] from u to 0
  = (u - 0)/k
  = u/k</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 5 — check the dimensions and the behaviour.</b> The constant <code>k</code> has units of <code>s^-1</code>, because <code>a = -kv</code> has <code>m s^-2</code> on the left and <code>k</code> times <code>m s^-1</code> on the right. So <code>u/k</code> has units <code>(m s^-1)/(s^-1) = m</code>, a distance. Good. And the behaviour is right in both directions: start faster and you go further; make <code>k</code> larger and the motion is damped harder, so you go less far. Both are what the physics requires.</p>
<p><b>Step 6 — a second route, for confirmation.</b> From <code>v = u e^(-kt)</code>, the distance is the integral of the speed from <code>t = 0</code> to infinity:</p>
<div class="formula">x = integral of u e^(-kt) dt = u/k</div>
<p>The two routes agree, and they use different mathematics — one integrates in space, the other in time. That is the strongest kind of check available here.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>uk</b> is the reciprocal of the right answer, from multiplying by <code>k</code> where the working divides. A quick units check kills it: <code>u k</code> has units <code>m s^-1 x s^-1 = m s^-2</code>, which is an acceleration and not a distance.</p>
<p>&middot; <b>u/(2k)</b> is half the correct answer. It comes from reaching for the constant-deceleration formula <code>x = u^2/(2a)</code> and putting <code>a = ku</code>, which is only the initial value of the deceleration. The deceleration is not constant, so that formula does not apply.</p>
<p>&middot; <b>2u/k</b> is twice the correct answer. It treats the distance to rest as twice the distance covered while the speed halves — plausible-looking, but the speed does not fall linearly, so halving the speed does not take half the distance.</p>
<p>&middot; <b>u/(k ln 2)</b> uses the <i>time</i> to halve the speed. The speed halves after <code>t = ln2/k</code>, and dividing <code>u</code> by that time gives a quantity with the units of an acceleration, not a distance. It is a real quantity from this problem, applied to the wrong question.</p>
<p><b>The trap.</b> Using the constant-acceleration formulas because they are the ones you have practised. They require the acceleration to be constant, and here it falls in step with the speed, so they are simply not applicable. The question deliberately gives a law that is not constant in time, and the identity <code>a = v dv/dx</code> is the tool for that case.</p>
<p><b>Relevant topics:</b> the two forms of acceleration; separating variables; the chain rule in kinematics; why an exponential decay takes infinite time but finite distance.</p>''',
    "trap": "Applying the constant-acceleration formulas. The deceleration falls as the speed falls, so u^2/(2a) is not available, and the identity a = v dv/dx is the way in.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 15 — C, forces.  Impulse as the area under a force-time graph.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 15, "id": "S03-15", "module": "C", "diff": 3,
    "topic": "Impulse from a force-time graph, and the speed it gives a ball",
    "rel": [("C", "Impulse is the area under a force-time graph, and equals the change in momentum"),
            ("C", "Momentum as mass times velocity, so a change in momentum is a change in velocity"),
            ("A", "Taking the area of a triangle without a calculator")],
    "key": ["impulse", "graph", "momentum"],
    "stem": '<p>A ball of mass 2.0 kg is at rest on a smooth horizontal surface. A variable force acts on it for 0.20 s; the graph shows how the force varies with time. {{FIG:s03-15}}</p><p>What is the speed of the ball immediately after the force has acted?</p>',
    "opts": ['2.0 m/s',
             '0.50 m/s',
             '4.0 m/s',
             '1.0 m/s',
             '20 m/s'],
    "ans": 3,
    "distractors": ['reports the impulse as the speed, forgetting that the impulse has to be divided by the mass',
                    'divides by the mass twice, once to get the impulse and once again to get the speed',
                    'reads the peak force as though it had acted for the whole 0.20 s, which gives twice the true impulse',
                    'correct',
                    'reports the peak force as the speed, taking a number off the vertical axis as an answer'],
    "profile": {
        "steps": [
            ("relate", "the impulse delivered is the area under the force-time graph"),
            ("relate", "the graph is a triangle with a base of 0.20 s and a height of 20 N"),
            ("solve", "impulse = (1/2) x 0.20 x 20 = 2.0 N s"),
            ("solve", "the impulse equals the change in momentum, and the ball started from rest, so v = 2.0/2.0 = 1.0 m/s"),
            ("check", "an impulse of 2.0 N s on a 2.0 kg mass must give about 1 m/s, and the units confirm it"),
        ],
        "relations": ["impulse = area under F-t", "area = (1/2) x 0.20 x 20",
                      "impulse = m v", "v = 2.0/2.0"],
        "insight": "A force-time graph pays out momentum as area, exactly as a velocity-time graph pays out distance. The two graphs are read the same way, and the only extra step here is dividing the momentum by the mass.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(0.5*20*0.20)/2.0", "want": "1.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you read a force-time graph the same way as a velocity-time graph, and whether you then complete the step from momentum to speed.</p>
<p><b>Step 1 — what the area means.</b> A force acting for a short time <code>dt</code> changes the momentum by <code>F dt</code>. Adding up all the slivers, the total change in momentum is the whole area under the force-time graph. This area has its own name, the impulse, and its units are newton seconds. Since a newton is a <code>kg m s^-2</code>, a newton second is a <code>kg m s^-1</code> — the units of momentum, as they must be.</p>
<p><b>Step 2 — take the area.</b> The graph is a triangle rising from zero to 20 N and back to zero over 0.20 s:</p>
<div class="formula">impulse = (1/2) x base x height
        = (1/2) x 0.20 x 20
        = 2.0 N s</div>
<p><b>Step 3 — from impulse to speed.</b> The ball starts at rest, so the change in momentum is the final momentum itself:</p>
<div class="formula">impulse = &Delta;p = m &Delta;v
2.0 = 2.0 x v
v = 1.0 m/s</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 4 — check the size.</b> An impulse of 2.0 N s is the same as the momentum of a 2.0 kg ball moving at 1.0 m/s, which is a brisk walking pace — a firm push on a ball for a fifth of a second. A kick in a football match delivers a much larger impulse, of order 10 N s, so 2.0 N s giving 1.0 m/s is the right order for the force and time given.</p>
<p><b>Step 5 — the comparison worth carrying away.</b> Both graph questions in this paper are read the same way. On a velocity-time graph the area is a distance; on a force-time graph the area is a momentum. In each case the vertical axis is a rate of change of the quantity the area gives: velocity is the rate of change of distance, force is the rate of change of momentum. That is not a coincidence, and it is a reliable way to remember which area gives what.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2.0 m/s</b> is the impulse reported as a speed. The number 2.0 appears twice in this problem — once as the impulse and once as the mass — so a candidate who stops after step 2 lands on an answer that looks internally consistent.</p>
<p>&middot; <b>0.50 m/s</b> is <code>2.0/4.0</code>: the mass applied twice. It is the natural slip when both the impulse and the mass are 2.0, since it is easy to divide twice without noticing.</p>
<p>&middot; <b>4.0 m/s</b> reads the peak force of 20 N as though it had acted for the whole 0.20 s. That gives an impulse of <code>20 x 0.20 = 4.0 N s</code> and a speed of 2.0 m/s. It is the rectangle the triangle sits inside, and the graph's triangular shape is the whole reason the answer is not that.</p>
<p>&middot; <b>20 m/s</b> is the peak force itself, read off the vertical axis. It mixes up what the axes mean — the ordinate is a force, not a speed.</p>
<p><b>The trap.</b> Reading the graph as though it were a rectangle. The peak value is the eye-catching number, and multiplying it by the duration is one step with no halving in it. The halving is what the sloping sides demand, and the graph is drawn with slopes on purpose.</p>
<p><b>Relevant topics:</b> impulse and momentum; the area under a force-time graph; the impulse-momentum equation; reading compound areas; the parallel between the two kinds of graph.</p>''',
    "trap": "Treating the force-time graph as a rectangle and using the peak force for the whole duration. The triangular area is half of that, so the impulse and the speed are both half of the naive answer.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 16 — D, circular motion.  The banking angle that needs no friction.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 16, "id": "S03-16", "module": "D", "diff": 3,
    "topic": "A banked track: the angle at which no friction is needed",
    "rel": [("D", "The centripetal force is the horizontal component of the normal reaction"),
            ("C", "Resolving the normal reaction vertically, where it balances the weight"),
            ("A", "Dividing one resolved equation by the other to remove the normal reaction")],
    "key": ["banking", "centripetal", "resolve"],
    "stem": '<p>A circular track of radius 30 m is banked at an angle <code>&theta;</code> to the horizontal, as shown. A car travels round it at 15 m/s without any reliance on friction. Take <code>g = 10 m/s<sup>2</sup></code>. {{FIG:s03-16}}</p><p>What is <code>&theta;</code>?</p>',
    "opts": ['37&deg;',
             '53&deg;',
             '45&deg;',
             '49&deg;',
             '27&deg;'],
    "ans": 0,
    "distractors": ['correct',
                    'inverts the ratio, taking rg/v^2 = 1.33 instead of v^2/(rg) = 0.75',
                    'assumes the horizontal and vertical forces are equal, which would require the ratio to come out as 1',
                    'treats the ratio as a sine rather than a tangent, which is the error the resolution of the normal reaction exists to prevent',
                    'drops the square on the speed, using v/(rg) = 0.5 instead of v^2/(rg) = 0.75'],
    "profile": {
        "steps": [
            ("relate", "the only forces are the weight and the normal reaction, since friction is not to be used"),
            ("relate", "resolve vertically: the vertical component of the normal reaction balances the weight, N cos(theta) = mg"),
            ("relate", "resolve horizontally: the horizontal component supplies the centripetal force, N sin(theta) = mv^2/r"),
            ("eliminate", "divide the horizontal equation by the vertical one, which removes both N and m and leaves tan(theta) = v^2/(rg)"),
            ("solve", "tan(theta) = 225/300 = 0.75, so theta is 37 degrees"),
        ],
        "relations": ["N cos(theta) = mg", "N sin(theta) = m v^2/r",
                      "tan(theta) = v^2/(r g)", "tan(theta) = 225/300 = 0.75"],
        "insight": "The banking angle is the angle between the normal reaction and the vertical, so it is the angle that appears inside the resolved triangle -- which is exactly why the ratio comes out as a tangent rather than a sine. Reading that angle off the diagram correctly is the step that decides the answer.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "sym", "got": "15^2/(30*10)", "want": "3/4"},
    "sol": '''<p><b>What is being tested.</b> Whether you can resolve the normal reaction into components and then combine the two equations in the one way that removes the unknowns. There is no friction in the problem, so the normal reaction is the only force that can point towards the centre.</p>
<p><b>Step 1 — what the normal reaction is doing.</b> On a banked surface the normal reaction is perpendicular to the road, so it is tilted from the vertical by the banking angle <code>&theta;</code>. That tilt is the whole point: part of it holds the car up, and part of it pushes the car towards the centre of the circle. Friction is stated to be unnecessary, so these two components are the entire story.</p>
<div class="formula">vertical:    N cos(theta) = mg
horizontal:  N sin(theta) = m v^2/r</div>
<p>The second equation is the centripetal requirement: the horizontal force must equal <code>m v^2/r</code>.</p>
<p><b>Step 2 — divide one by the other.</b> This is the step the question is really testing. Dividing the horizontal equation by the vertical one cancels <code>N</code> on the left, and cancels <code>m</code> on the right:</p>
<div class="formula">N sin(theta)/N cos(theta) = (m v^2/r)/(m g)
tan(theta) = v^2/(r g)</div>
<p>Two unknowns gone in one operation. Nothing else in the problem is as efficient as this, and it is worth remembering as the standard move whenever two resolved equations share a common force.</p>
<p><b>Step 3 — put the numbers in.</b></p>
<div class="formula">tan(theta) = 15^2/(30 x 10)
           = 225/300
           = 0.75</div>
<p><b>Step 4 — recognise the angle.</b> A tangent of <code>0.75</code> is the 3-4-5 triangle: <code>0.75 = 3/4</code>, so the angle is the one whose sine is <code>3/5</code> and whose cosine is <code>4/5</code>. That angle is <code>37&deg;</code>. So <b>Answer: A.</b></p>
<p><b>Step 5 — check the physics.</b> A steeper bank should allow a faster corner, so the angle should grow with speed and shrink with radius: <code>tan(theta) = v^2/(rg)</code> has <code>v^2</code> on top and <code>r</code> underneath, which is exactly right. The mass does not appear at all, so a loaded lorry and a motorcycle need the same banking angle — a result worth noticing, and one that the division in step 2 produced automatically.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>53&deg;</b> is the angle whose tangent is <code>4/3</code>: the ratio inverted. It corresponds to <code>rg/v^2 = 4/3</code>, which is the equation the other way up. It is a real angle in the 3-4-5 family, which is what makes it convincing.</p>
<p>&middot; <b>45&deg;</b> is what you get from <code>tan(theta) = 1</code>, i.e. from assuming the vertical and horizontal components of the normal reaction are equal. Nothing in the problem says they are; it is an assumption, not a derivation.</p>
<p>&middot; <b>49&deg;</b> treats <code>0.75</code> as a sine rather than a tangent. The vertical and horizontal components of <code>N</code> are its cosine and sine, and it is their <i>ratio</i> that the division produces — that is precisely why a tangent appears and not a sine.</p>
<p>&middot; <b>27&deg;</b> is <code>atan(0.5)</code>: the ratio computed as <code>v/(rg) = 15/30</code>, with the square on the speed dropped. The centripetal force depends on <code>v^2</code>, so the square cannot be dropped.</p>
<p><b>The trap.</b> Writing the centripetal force as <code>N sin(theta)</code> and then also using <code>N = mg</code>. That double-use of the normal reaction throws away the tilt, and it produces an angle that depends on the mass — which the correct answer does not. If your answer has a mass in it, something has gone wrong.</p>
<p><b>Relevant topics:</b> resolving forces on an inclined surface; centripetal acceleration; the banking angle; why the mass cancels; the 3-4-5 triangle as a standard angle.</p>''',
    "trap": "Using N = mg as well as N sin(theta) = mv^2/r, which uses the normal reaction twice and throws away the tilt. Dividing the two resolved equations removes N and m together, and the mass must not appear in the answer.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 17 — E, materials.  The answer is an EXPRESSION, and the five options are
# expressions, which is how the real paper asks its algebraic questions.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 17, "id": "S03-17", "module": "E", "diff": 3,
    "topic": "Sizing a cable from a breaking stress: the diameter as an algebraic expression",
    "rel": [("E", "Stress is force per unit cross-sectional area, and at the limit of what the cable can bear it equals the breaking stress"),
            ("E", "The cross-section of a round cable is a circle, so its area carries the diameter squared and a factor of pi over four"),
            ("C", "The force the cable must bear is the weight of the load, mass times the gravitational field strength"),
            ("A", "Rearranging a formula before substituting, so that the algebraic form can be checked against the options without any arithmetic")],
    "key": ["stress", "cable", "diameter", "expression"],
    "stem": '<p>A steel cable is to support a load of mass <code>m</code>. The breaking stress of the steel is <code>&#963;</code> and the gravitational field strength is <code>g</code>.</p><p>Which expression gives the smallest diameter the cable may have?</p>',
    "opts": ['&#8730;(4mg / (&#960;&#963;))',
             '&#8730;(mg / (&#960;&#963;))',
             '4mg / (&#960;&#963;)',
             '&#8730;(4&#960;mg / &#963;)',
             '&#8730;(4mg&#963; / &#960;)'],
    "ans": 0,
    "distractors": ['correct',
                    'drops the factor of four, which is what appears when the area is written in terms of the diameter rather than the radius',
                    'leaves the square root out, so the answer has the dimensions of an area rather than of a length',
                    'puts pi in the numerator instead of the denominator, inverting the part of the expression that came from the area',
                    'inverts the stress, so the cable would be asked to be thinner the stronger the steel'],
    "profile": {
        "steps": [
            ("relate", "write the stress as the force divided by the cross-sectional area, and note that the cable must be sized so that this equals the breaking stress"),
            ("relate", "identify the force as the weight of the load"),
            ("solve", "rearrange to get the smallest area that will do, which is the load divided by the breaking stress"),
            ("relate", "write the area of the round cross-section in terms of the DIAMETER, which brings in a factor of four over pi"),
            ("solve", "equate the two expressions for the area"),
            ("solve", "rearrange for the diameter squared"),
            ("solve", "take the square root to get the diameter itself, which is the quantity the question wants"),
            ("check", "check the dimensions of the result, which must be a length"),
            ("check", "put numbers in as a spot check, using a load of 1000 kg and a breaking stress of 1.0 x 10^9 Pa"),
        ],
        "relations": ["stress = F / A",
                      "F = m g",
                      "A = &#960; d<sup>2</sup> / 4",
                      "A = m g / &#963;",
                      "d = &#8730;(4 m g / (&#960; &#963;))"],
        "insight": "The factor of four is the whole question. Area in terms of a radius is pi r squared, but the quantity wanted is the diameter, and replacing r by d over two squares the two and turns the formula into pi d squared over four.",
        "shape": "units-consistency",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "4/(pi*(4/pi))", "want": "1"},
    "sol": '''<p><b>What is being tested.</b> Whether you can carry an algebraic rearrangement through to the end without substituting numbers, and whether you know that a circle's area in terms of its <i>diameter</i> is <code>&#960;d<sup>2</sup>/4</code> and not <code>&#960;d<sup>2</sup></code>. The factor of four separates every option in the list.</p>
<p><b>Step 1 — write the condition on the cable.</b> Stress is force per unit area, and the cable is safe so long as the stress in it stays at or below the breaking stress. The smallest diameter comes from the equality case, where the stress is exactly the breaking stress:</p>
<div class="formula">&#963; = F / A</div>
<p>Using the equality rather than an inequality is what turns a design condition into an equation, and it is the standard move in any "smallest that will do" question.</p>
<p><b>Step 2 — the force.</b> The cable hangs a load, so the force in it is that load's weight:</p>
<div class="formula">F = m g</div>
<p><b>Step 3 — the smallest area that will do.</b> Substituting and rearranging:</p>
<div class="formula">A = F / &#963; = m g / &#963;</div>
<p><b>Step 4 — the same area in terms of the diameter.</b> The cross-section is a circle. Its area in terms of the radius is <code>&#960;r<sup>2</sup></code>, and the radius is half the diameter, so</p>
<div class="formula">A = &#960; r<sup>2</sup> = &#960; (d/2)<sup>2</sup> = &#960; d<sup>2</sup> / 4</div>
<p>This is the step the question is built around. Writing <code>&#960;d<sup>2</sup></code> here instead of <code>&#960;d<sup>2</sup>/4</code> makes the cable twice as thick as it needs to be, and it is a mistake that costs real money in a real design.</p>
<p><b>Step 5 — equate the two expressions for the area.</b> They describe the same cross-section, so</p>
<div class="formula">&#960; d<sup>2</sup> / 4 = m g / &#963;</div>
<p><b>Step 6 — rearrange for the diameter squared.</b> Multiply both sides by four and divide by pi:</p>
<div class="formula">d<sup>2</sup> = 4 m g / (&#960; &#963;)</div>
<p><b>Step 7 — take the square root.</b></p>
<div class="formula">d = &#8730;(4 m g / (&#960; &#963;))</div>
<p>So <b>Answer: A, &#8730;(4mg/(&#960;&#963;)).</b></p>
<p><b>Step 8 — check the dimensions.</b> The numerator is a force, in newtons; the denominator is a stress, in newtons per square metre. Force divided by stress is an area, in square metres, and the square root of an area is a length. The expression gives a length, which is what a diameter is. Had the factor of four been forgotten the dimensions would still be right &#8212; which is exactly why the dimensions cannot catch that particular error, and why the factor has to be argued from the geometry rather than checked.</p>
<p><b>Step 9 — put numbers in as a spot check.</b> Take a load of 1000 kg and a breaking stress of <code>1.0 &#215; 10<sup>9</sup></code> Pa, with <code>g</code> = 10 m s<sup>-2</sup>:</p>
<div class="formula">d<sup>2</sup> = 4 &#215; 1000 &#215; 10 / (&#960; &#215; 1.0 &#215; 10<sup>9</sup>) = 4.0 &#215; 10<sup>4</sup> / 3.1 &#215; 10<sup>9</sup> = 1.3 &#215; 10<sup>-5</sup> m<sup>2</sup></div>
<div class="formula">d = &#8730;(1.3 &#215; 10<sup>-5</sup>) = 3.6 &#215; 10<sup>-3</sup> m = 3.6 mm</div>
<p>A 3.6 mm steel cable lifting a tonne is the size one expects: steel is strong, so the cable is thin. Had the factor of four been dropped, the answer would have been 1.8 mm, and had the square root been dropped, the answer would have been an area masquerading as a length. Both are caught by the numbers, and neither is caught by the dimensions alone.</p>
<p><b>Why the answer is asked for as an expression.</b> The real paper asks several of its questions this way, with five expressions rather than five numbers. The reason is that an expression tests the whole rearrangement, whereas a number can sometimes be reached by a route the candidate cannot justify. It also removes the calculator: with the answer left symbolic, no division ever has to be carried out, which is precisely what a non-calculator paper wants.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>&#8730;(mg/(&#960;&#963;))</b> is the radius of the cable, not the diameter. It comes from writing the area as <code>&#960;d<sup>2</sup></code>, or equivalently from forgetting the factor of four. It is the commonest wrong answer, and it is wrong by a factor of two in the diameter, which is a factor of four in the cross-sectional area.</p>
<p>&middot; <b>4mg/(&#960;&#963;)</b> is the diameter <i>squared</i>. It has the dimensions of an area, so it cannot be a diameter, and this is one of the few cases where the dimensions alone reject an option at sight.</p>
<p>&middot; <b>&#8730;(4&#960;mg/&#963;)</b> puts pi in the numerator. The pi came from the area, and the area was in the denominator of the rearrangement, so pi belongs in the denominator. Swapping it is a pure bookkeeping slip.</p>
<p>&middot; <b>&#8730;(4mg&#963;/&#960;)</b> inverts the stress, which would mean that a stronger steel needs a thicker cable. Reading it back as a physical statement is the fastest way to reject it.</p>
<p><b>The trap.</b> Substituting numbers too early. Once numbers are in, a factor of four is invisible; left as symbols, the option list itself shows which factor is present and which is missing. Rearranging first and substituting last is not just tidier, it is the only way to see what the question is really asking.</p>
<p><b>Relevant topics:</b> stress and breaking stress; the area of a circle in terms of its diameter; rearranging formulas symbolically; checking dimensions; why an expression is a better answer than a number in a non-calculator paper.</p>''',
    "trap": "Writing the area as pi d squared instead of pi d squared over four, which loses the factor of four and gives a cable half the diameter it needs.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 18 — F, waves.  The highest order a grating can produce.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 18, "id": "S03-18", "module": "F", "diff": 2,
    "topic": "The highest diffraction order a grating can produce",
    "rel": [("F", "The grating equation d sin(theta) = n lambda"),
            ("F", "The limit sin(theta) is at most 1, which bounds the order"),
            ("A", "Rounding an inequality down rather than to the nearest whole number")],
    "key": ["grating", "order", "limit"],
    "stem": '<p>A diffraction grating has 300 lines per millimetre. Monochromatic light of wavelength 500 nm falls on it normally, as shown. {{FIG:s03-18}}</p><p>What is the highest order of maximum that can be observed?</p>',
    "opts": ['7',
             '12',
             '13',
             '1',
             '6'],
    "ans": 4,
    "distractors": ['rounds the ratio up to the next whole number instead of down, ignoring that a sine cannot exceed one',
                    'doubles the order to count the maxima on both sides of the centre line',
                    'counts both sides of the centre and adds the central maximum as well, giving one more than twice the order',
                    'concludes that only the central maximum can be seen, which would require the wavelength to be longer than the grating spacing',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "the grating spacing is the reciprocal of the line density, so d = 1/(300 per mm) = 3.3 x 10^-6 m"),
            ("relate", "the grating equation is d sin(theta) = n lambda, so n = d sin(theta)/lambda"),
            ("eliminate", "the largest possible value of sin(theta) is 1, which gives the largest possible order"),
            ("solve", "n_max = d/lambda = 3.3 x 10^-6/5.0 x 10^-7 = 6.6"),
            ("check", "an order must be a whole number, and the inequality must not be broken, so the answer rounds DOWN to 6"),
        ],
        "relations": ["d = 1/(300 per mm)", "d sin(theta) = n lambda", "n <= d/lambda",
                      "3.3e-6/5.0e-7 = 6.6"],
        "insight": "The order is capped by the fact that a sine cannot exceed one. The ratio comes out at 6.6, and an inequality rounds DOWN, so the sixth order exists and the seventh does not.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "0.001/300/(500*10**-9)", "want": "20/3"},
    "sol": '''<p><b>What is being tested.</b> Whether you can convert a line density into a spacing, and then recognise that the answer is bounded by an inequality rather than given by an equation.</p>
<p><b>Step 1 — the grating spacing.</b> "300 lines per millimetre" means the lines are one three-hundredth of a millimetre apart:</p>
<div class="formula">d = 1 mm/300
  = 1.0 x 10^-3 m/300
  = 3.3 x 10^-6 m</div>
<p>This is the step where most of the arithmetic lives, and it is worth writing the unit out: <code>d</code> is a length, and it must come out of the reciprocal of a density of lines.</p>
<p><b>Step 2 — the grating equation.</b> Maxima appear where waves from adjacent slits arrive in step:</p>
<div class="formula">d sin(theta) = n lambda</div>
<p>with <code>n</code> a whole number. Rearranged, the order is <code>n = d sin(theta)/lambda</code>.</p>
<p><b>Step 3 — the limit.</b> This is the step the question is built around. The angle of a maximum cannot exceed 90&deg;, so <code>sin(theta)</code> can be at most 1. Substituting that largest possible value gives the largest possible order:</p>
<div class="formula">n_max = d/lambda
      = 3.3 x 10^-6/5.0 x 10^-7
      = 6.6</div>
<p><b>Step 4 — round the inequality down.</b> The statement is not "the order is 6.6"; it is "<code>n</code> must be a whole number no greater than 6.6". The whole numbers satisfying that are <code>0, 1, 2, 3, 4, 5, 6</code>, so the highest order is <b>6</b>. So <b>Answer: E.</b></p>
<p><b>Step 5 — check by putting the order back in.</b> For <code>n = 6</code>, <code>sin(theta) = 6 x 5.0 x 10^-7/3.3 x 10^-6 = 0.90</code>, which is a real angle. For <code>n = 7</code>, <code>sin(theta) = 7 x 5.0 x 10^-7/3.3 x 10^-6 = 1.05</code>, which does not exist. So 6 is the last order that fits, and 7 is one too many. This check is the honest way to settle it, and it takes one line.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>7</b> rounds 6.6 up to the nearest whole number. Rounding to nearest is a habit from measurement, and it is wrong here: the question is about which whole numbers <i>satisfy an inequality</i>, and that always rounds down.</p>
<p>&middot; <b>12</b> doubles the order to count the maxima on both sides of the centre. There are indeed maxima at both <code>+6</code> and <code>-6</code>, but the question asks for the order, which is a property of one maximum and is the same on both sides.</p>
<p>&middot; <b>13</b> is <code>2 x 6 + 1</code>: both sides counted and the central maximum added. It is the right answer to "how many maxima can be seen in total", which is a different question. This pair of options — 12 and 13 — is there to separate the order from the count.</p>
<p>&middot; <b>1</b> concludes that only the central maximum exists. That would require the wavelength to exceed the grating spacing, and here <code>500 nm</code> is much smaller than <code>3300 nm</code>, so plenty of orders fit. Checking that comparison first is a quick way to rule this out.</p>
<p><b>The trap.</b> Rounding 6.6 to 7. The whole question is a limiting case, and in a limiting case the inequality governs, not the arithmetic habit. Whenever the answer must be a whole number and it comes out between two, ask which side the physics allows — here, only the smaller one.</p>
<p><b>Relevant topics:</b> the diffraction grating; the grating equation; the condition <code>sin(theta) &lt;= 1</code>; rounding an inequality; the difference between the order and the number of visible maxima.</p>''',
    "trap": "Rounding the ratio 6.6 up to 7. The order is bounded by sin(theta) at most 1, which is an inequality, and inequalities round DOWN -- the seventh order would need a sine of 1.05.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 19 — G, optics.  A converging lens: where the image is and how big.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 19, "id": "S03-19", "module": "G", "diff": 3,
    "topic": "A converging lens: the linear magnification",
    "rel": [("G", "The lens equation relating object distance, image distance and focal length"),
            ("G", "Magnification as the ratio of image distance to object distance"),
            ("A", "Adding two fractions by putting them over a common denominator")],
    "key": ["lens", "magnification", "image"],
    "stem": '<p>An object is placed 30 cm from a thin converging lens of focal length 20 cm. The ray diagram shows the construction. {{FIG:s03-19}}</p><p>What is the linear magnification produced by the lens?</p>',
    "opts": ['3',
             '2',
             '1.5',
             '0.67',
             '0.5'],
    "ans": 1,
    "distractors": ['divides the image distance by the focal length instead of by the object distance, which mixes two different lengths',
                    'correct',
                    'divides the object distance by the focal length, a ratio that appears in the working but is not the magnification',
                    'uses the focal length over the image distance, which is the reciprocal of a different ratio again',
                    'inverts the magnification, using the object distance over the image distance'],
    "profile": {
        "steps": [
            ("relate", "write the lens equation with a sign convention: 1/f = 1/u + 1/v"),
            ("relate", "the object is outside the focal length, so the image is real and on the far side"),
            ("solve", "1/v = 1/20 - 1/30 = (3 - 2)/60 = 1/60, so v = 60 cm"),
            ("solve", "the magnification is v/u = 60/30 = 2"),
            ("check", "an object between f and 2f gives a real image magnified by more than one, which agrees"),
        ],
        "relations": ["1/f = 1/u + 1/v", "1/v = 1/20 - 1/30", "v = 60 cm", "m = v/u"],
        "insight": "The lens equation gives the image distance, not the magnification. The magnification is a second, separate ratio, and the two lengths that form it are the image and object distances -- not the focal length.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "20/(30 - 20)", "want": "2"},
    "sol": '''<p><b>What is being tested.</b> Whether you keep the lens equation and the magnification separate. They are two different statements, and the first does not give the second.</p>
<p><b>Step 1 — the lens equation.</b> With the usual convention that <code>f</code> is positive for a converging lens and the object is on the incoming side:</p>
<div class="formula">1/f = 1/u + 1/v</div>
<p>where <code>u = 30 cm</code> and <code>f = 20 cm</code>. The object is outside the focal length, so the image will be real and on the far side of the lens, and <code>v</code> should come out positive.</p>
<p><b>Step 2 — solve for the image distance.</b> Put the two fractions over a common denominator of 60:</p>
<div class="formula">1/v = 1/f - 1/u
    = 1/20 - 1/30
    = 3/60 - 2/60
    = 1/60
v   = 60 cm</div>
<p>The image is 60 cm from the lens, on the far side. The sign is right: a positive image distance means a real image, which is what a converging lens gives for an object outside its focal length.</p>
<p><b>Step 3 — the magnification.</b> Linear magnification is the ratio of the image height to the object height, and the ray geometry makes that equal to the ratio of the distances:</p>
<div class="formula">m = v/u
  = 60/30
  = 2</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 4 — check against the general case.</b> Combining the lens equation with <code>m = v/u</code> gives the compact form:</p>
<div class="formula">m = f/(u - f) = 20/(30 - 20) = 2</div>
<p>The two routes agree, which is a worthwhile check because this form never produces <code>v</code> at all. The behaviour also checks out: as the object moves out towards infinity, <code>u - f</code> grows and <code>m</code> falls towards zero, which is what happens when you photograph something very far away. As the object approaches the focal point, <code>m</code> grows without limit, which is the projector case.</p>
<p><b>Step 5 — is the size sensible?</b> The object sits between <code>f = 20 cm</code> and <code>2f = 40 cm</code>, and that is exactly the arrangement that produces a real, inverted, magnified image — the arrangement in a slide projector. So a magnification of 2 with a real image is the right qualitative answer, and it confirms the direction as well as the size.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3</b> is <code>v/f = 60/20</code>. It divides by the focal length rather than by the object distance. Both are lengths in the working, and mixing them up is easy when all three numbers are on the page.</p>
<p>&middot; <b>1.5</b> is <code>u/f = 30/20</code>. The object distance divided by the focal length appears in the working — the object is one and a half focal lengths away — but it is a statement about where the object is, not about how big the image is.</p>
<p>&middot; <b>0.67</b> is <code>f/v = 20/60</code>, the reciprocal of the ratio of image distance to focal length. It is smaller than one, which would mean a diminished image, and the arrangement here does not give one.</p>
<p>&middot; <b>0.5</b> is <code>u/v = 30/60</code>: the magnification upside down. It is the single most common slip with this formula, and it is worth guarding against by noting that a magnification of 0.5 would mean the image is smaller than the object, which contradicts the ray diagram.</p>
<p><b>The trap.</b> Stopping at <code>v</code>. Finding the image distance is the bulk of the arithmetic, so it feels like the end of the question — but the magnification is a second ratio, and the lens equation does not contain it. Reading the ray diagram is the guard: it plainly shows an image taller than the object.</p>
<p><b>Relevant topics:</b> the thin lens equation; real and virtual images; linear magnification; the three standard object positions and the images they give.</p>''',
    "trap": "Stopping at the image distance, or forming the ratio with the focal length. Magnification is v/u, and both lengths in it come from the lens equation's solution, not from the data.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 20 — H, circuits.  Two lamps of different rating in series.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 20, "id": "S03-20", "module": "H", "diff": 2,
    "topic": "Two lamps of different power rating in series: which is brighter",
    "rel": [("H", "A lamp's rated power and voltage fix its resistance"),
            ("H", "In series the current is common, so power goes as resistance"),
            ("A", "Comparing two quantities by computing both rather than by reasoning about one")],
    "key": ["lamps", "series", "power"],
    "stem": '<p>Two filament lamps are marked 60 W and 100 W, both rated for use on 240 V. They are connected in series across a 240 V supply.</p><p>Which lamp is the brighter, and why?</p>',
    "opts": ['The 100 W lamp, because it is rated at the higher power',
             'Neither, because the same current through both makes the powers equal',
             'The 100 W lamp, because its lower resistance lets more current through it',
             'The 60 W lamp, because it has the greater resistance and the current through both is the same',
             'Neither lights, because the two resistances in series are too large for a 240 V supply'],
    "ans": 3,
    "distractors": ['assumes the lamp rated at the higher power must be the brighter, which is true only when the two are in parallel and share the same voltage',
                    'confuses equal current with equal power, when power is the square of the current times the resistance and the resistances differ',
                    'has the argument backwards: in series the same current passes through both lamps, so the larger resistance is the one that takes the larger power',
                    'correct',
                    'thinks two lamps in series cannot work at all, when they simply share the supply and each gets part of the 240 V'],
    "profile": {
        "steps": [
            ("relate", "the markings give each lamp's resistance, since R = V^2/P at its rated voltage"),
            ("solve", "R_60 = 240^2/60 = 960 ohm and R_100 = 240^2/100 = 576 ohm, so the 60 W lamp has the larger resistance"),
            ("relate", "in series the current through both lamps is the same, so the power in each is I^2 R"),
            ("solve", "the same I times the larger R gives the larger power, so the 60 W lamp is brighter"),
            ("check", "the resistances differ by 384 ohm in the expected direction, and the total of 1536 ohm draws a modest current"),
        ],
        "relations": ["R = V^2/P", "240^2/60 = 960 ohm", "240^2/100 = 576 ohm",
                      "P = I^2 R with I common"],
        "insight": "A lamp's marking tells you its resistance, and the higher-power lamp is the LOWER resistance one. In series the current is common, so power follows resistance -- which reverses the ranking you would get in parallel.",
        "shape": "monotonicity",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "57600/60 - 57600/100", "want": "384"},
    "sol": '''<p><b>What is being tested.</b> Whether you can turn a power rating into a resistance, and then notice that the answer to "which is brighter" depends on how the lamps are connected.</p>
<p><b>Step 1 — what the markings mean.</b> "60 W at 240 V" is a statement about the lamp when 240 V is across it. From <code>P = V^2/R</code>:</p>
<div class="formula">R = V^2/P
R_60  = 240^2/60 = 57600/60 = 960 ohm
R_100 = 240^2/100 = 57600/100 = 576 ohm</div>
<p>So the <i>lower</i> rated power belongs to the <i>higher</i> resistance. That inversion is the heart of the question. A 60 W lamp has a thinner, longer filament than a 100 W lamp, and a thinner filament is a larger resistance.</p>
<p><b>Step 2 — what is common in series.</b> In series, the same current passes through both lamps. This is the opposite of parallel, where the same voltage appears across both. So the right form of the power relation is:</p>
<div class="formula">P = I^2 R</div>
<p>with <code>I</code> the same for both lamps.</p>
<p><b>Step 3 — compare.</b> Since <code>I</code> is common and <code>R_60 &gt; R_100</code>, the power in the 60 W lamp is the larger. So <b>Answer: D</b> — the 60 W lamp is brighter.</p>
<p><b>Step 4 — check the numbers.</b> The resistances differ by <code>960 - 576 = 384 ohm</code>, which is the quantity computed in the check. The total resistance is <code>960 + 576 = 1536 ohm</code>, so the current is <code>240/1536 A</code>, which cancels to <code>5/32 A</code>. Because the current is common, the two powers are in the ratio of the resistances, and <code>960 : 576 = 5 : 3</code>. So the 60 W lamp takes five eighths of the total power:</p>
<div class="formula">P_total = V^2/R = 240^2/1536 = 37.5 W
P_60    = (5/8) x 37.5 = 23 W
P_100   = (3/8) x 37.5 = 14 W</div>
<p>Both are well below their ratings, which is right: each lamp only gets part of the 240 V, so neither can reach its rated power. And the 60 W lamp takes the larger share, confirming step 3 numerically.</p>
<p><b>Step 5 — the general rule, which is what makes this memorable.</b> In parallel, the higher-power lamp is brighter, because the voltage is common and <code>P = V^2/R</code> rewards the smaller resistance. In series, the lower-power lamp is brighter, because the current is common and <code>P = I^2 R</code> rewards the larger resistance. The two arrangements give opposite rankings, and the question is testing whether you know which one you are in.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>The 100 W lamp because it is rated higher</b> is the answer for a parallel connection. It is the most common error, and it comes from carrying over a habit without checking the arrangement.</p>
<p>&middot; <b>Neither, because the current is the same</b> is a genuine confusion between a shared quantity and a shared outcome. Equal current does not mean equal power, because the resistances differ. The whole calculation in step 4 shows the powers are 23.5 W and 14.1 W.</p>
<p>&middot; <b>The 100 W lamp because its lower resistance lets more current through</b> has the reasoning backwards. In series there is only one path, so the current cannot be different in the two lamps. The lower resistance carries the same current and therefore dissipates <i>less</i> power.</p>
<p>&middot; <b>Neither lights</b> mistakes a series connection for a fault. Two lamps in series share the supply and both glow, dimly. The total resistance of 1536 ohm draws a perfectly ordinary current from a 240 V supply.</p>
<p><b>The trap.</b> Reasoning from the labels instead of from the circuit. "100 W" is a bigger number than "60 W", and it is very tempting to conclude that the bigger number is the brighter lamp. The label describes a different circuit — the one with 240 V across that lamp alone — and it does not survive being reconnected.</p>
<p><b>Relevant topics:</b> power ratings and what they mean; <code>P = V^2/R</code> and <code>P = I^2 R</code>; series and parallel connections; why the two arrangements rank lamps differently.</p>''',
    "trap": "Assuming the higher-rated lamp is brighter. That is true in parallel, where the voltage is common. In series the current is common and the power goes as resistance, so the 60 W lamp wins.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 21 — I, capacitors.  Two capacitors in series across a supply.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 21, "id": "S03-21", "module": "I", "diff": 3,
    "topic": "Capacitors in series: how the supply divides between them",
    "rel": [("I", "Capacitors in series carry the same charge"),
            ("I", "The charge on each capacitor is the total capacitance times the supply"),
            ("A", "Combining two capacitors in series and taking the reciprocal")],
    "key": ["capacitors", "series", "charge"],
    "stem": '<p>A 2.0 &mu;F capacitor and a 6.0 &mu;F capacitor are connected in series across a 12 V supply, as shown. {{FIG:s03-21}}</p><p>What is the potential difference across the 2.0 &mu;F capacitor?</p>',
    "opts": ['9.0 V',
             '3.0 V',
             '6.0 V',
             '4.0 V',
             '12 V'],
    "ans": 0,
    "distractors": ['correct',
                    'gives the smaller capacitor the smaller share, which is how capacitors behave in parallel and not in series',
                    'splits the supply equally between them, as though the two capacitances were the same',
                    'takes one third of the supply, which is the ratio 1:2 taken the wrong way round',
                    'gives the 2.0 uF capacitor the whole supply, as though the other capacitor were not in the circuit'],
    "profile": {
        "steps": [
            ("relate", "in series the two capacitors carry the same charge, because the charge can only arrive at one plate and leave the other"),
            ("relate", "the series combination is 1/C = 1/C1 + 1/C2, giving C_total = 1.5 uF"),
            ("solve", "the charge on each is Q = C_total V = 1.5 uF x 12 V = 18 uC"),
            ("solve", "the voltage across the 2.0 uF capacitor is Q/C = 18/2.0 = 9.0 V"),
            ("check", "the other capacitor takes 18/6.0 = 3.0 V, and 9.0 + 3.0 = 12 V, which is the whole supply"),
            ("check", "the voltages are in the inverse ratio of the capacitances, 6.0/2.0 = 3, so they split 3:1"),
        ],
        "relations": ["1/C = 1/C1 + 1/C2", "C_total = 1.5 uF", "Q = C V = 18 uC",
                      "V1 = Q/C1 = 9.0 V", "V1 + V2 = 12 V"],
        "insight": "In series the charge is common, so each voltage is that charge divided by that capacitance. The SMALLER capacitor therefore takes the LARGER share of the supply -- the opposite of what the same two components would do in parallel.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "12*6.0/(2.0 + 6.0)", "want": "9.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you know what is common in a series circuit. For resistors in series it is the current; for capacitors in series it is the charge. Getting that one fact right makes the rest a division.</p>
<p><b>Step 1 — what is shared.</b> Two capacitors in series are joined by a single wire between them. That wire is isolated, so no charge can accumulate on it, and the charge that leaves one plate must arrive at the other. So:</p>
<div class="formula">Q1 = Q2 = Q</div>
<p>This is the analogue of equal current in series resistors, and it is the fact the whole question turns on.</p>
<p><b>Step 2 — the combination.</b> The series rule is that the reciprocals add:</p>
<div class="formula">1/C = 1/C1 + 1/C2
    = 1/2.0 + 1/6.0
    = 3/6.0 + 1/6.0
    = 4/6.0
C   = 6.0/4 = 1.5 uF</div>
<p>The combination is smaller than the smallest capacitor, which is the right direction for a series arrangement — adding components in series never increases the total.</p>
<p><b>Step 3 — the common charge.</b> The whole supply appears across the pair, so the charge stored is:</p>
<div class="formula">Q = C V = 1.5 uF x 12 V = 18 uC</div>
<p><b>Step 4 — divide that charge by each capacitance.</b> Both capacitors carry 18 &mu;C, and each has its own voltage:</p>
<div class="formula">V_2 = Q/C1 = 18/2.0 = 9.0 V
V_6 = Q/C2 = 18/6.0 = 3.0 V</div>
<p>The question asks for the 2.0 &mu;F capacitor, so the answer is <b>9.0 V</b>. So <b>Answer: A.</b></p>
<p><b>Step 5 — the check that settles it.</b> The two voltages must add to the supply: <code>9.0 + 3.0 = 12 V</code>. They do, which is a complete check on both voltages at once. A second check on the direction: the smaller capacitance takes the larger voltage, and 2.0 &mu;F is smaller than 6.0 &mu;F, so 9.0 V going to the 2.0 &mu;F capacitor is the right way round.</p>
<p><b>Step 6 — a shortcut worth having.</b> Since the charge is common, <code>V1/V2 = C2/C1</code>: the voltages are in the <i>inverse</i> ratio of the capacitances. Here that is <code>6.0/2.0 = 3</code>, so the voltages are in the ratio 3:1, and with 12 V to share they are 9.0 V and 3.0 V. That route avoids computing the combination or the charge at all.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3.0 V</b> is the voltage across the 6.0 &mu;F capacitor — the other one. It is also what you get by taking the voltages in proportion to the capacitances, which is the parallel rule. In parallel the larger capacitor does take the larger charge, so this confusion has a real source.</p>
<p>&middot; <b>6.0 V</b> splits the supply equally. That would need the two capacitances to be equal, and 2.0 &mu;F and 6.0 &mu;F are not.</p>
<p>&middot; <b>4.0 V</b> is one third of the supply: the ratio 1:2 taken the wrong way round, or the ratio 1:3 applied to the wrong capacitor.</p>
<p>&middot; <b>12 V</b> gives the whole supply to one capacitor, as though the other were not there. If it were alone across the supply that is exactly what it would take, which is why the option is plausible — but then the question would not have mentioned a second capacitor.</p>
<p><b>The trap.</b> Carrying the resistor habit across. In a series resistor circuit the current is common and the voltages go as the resistances, so the <i>larger</i> component takes the larger voltage. In a series capacitor circuit the charge is common and the voltages go as the reciprocal of the capacitance, so the <i>smaller</i> component takes the larger voltage. The two arrangements rank their components in opposite orders, and the question is testing which one you are in.</p>
<p><b>Relevant topics:</b> capacitance and <code>Q = CV</code>; capacitors in series and in parallel; what is common in each kind of connection; the inverse ratio of voltages in series.</p>''',
    "trap": "Applying the parallel rule to a series circuit. In series the charge is common, so the voltages go as the reciprocal of the capacitance and the smaller capacitor takes the larger share.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 22 — J, thermal.  Linear expansion of a metal rod.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 22, "id": "S03-22", "module": "J", "diff": 3,
    "topic": "Linear thermal expansion: how much longer a heated rod becomes",
    "rel": [("J", "Linear expansion is proportional to the original length and to the temperature rise"),
            ("A", "Working with a small coefficient expressed in powers of ten"),
            ("A", "Converting millimetres and metres so the units agree")],
    "key": ["expansion", "linear", "rod"],
    "stem": '<p>A brass rod is 2.0 m long at 20 &deg;C. The coefficient of linear expansion of brass is 1.9 x 10<sup>-5</sup> per &deg;C.</p><p>How much longer is the rod at 120 &deg;C?</p>',
    "opts": ['7.6 mm',
             '4.6 mm',
             '3.8 mm',
             '1.9 mm',
             '0.38 mm'],
    "ans": 2,
    "distractors": ['doubles the expansion coefficient, as though the rod were expanding along two axes at once',
                    'uses the final temperature of 120 degrees rather than the 100 degree rise',
                    'correct',
                    'uses a one metre rod, dropping the stated length of 2.0 m',
                    'is a factor of ten out, from reading the coefficient as 1.9 x 10^-6 per degree'],
    "profile": {
        "steps": [
            ("relate", "the expansion is proportional to the original length and to the temperature change"),
            ("relate", "the temperature RISE is 120 - 20 = 100 degrees, not 120 degrees"),
            ("solve", "the extension is 2.0 x 1.9 x 10^-5 x 100 = 3.8 x 10^-3 m"),
            ("solve", "converting to millimetres gives 3.8 mm"),
            ("check", "a two metre rod growing by a few millimetres over a hundred degrees is the right order for brass"),
            ("check", "the expansion does not depend on the cross-section, only on the length and the material"),
        ],
        "relations": ["dL = L0 alpha dT", "dT = 120 - 20 = 100",
                      "dL = 2.0 x 1.9e-5 x 100", "3.8e-3 m = 3.8 mm"],
        "insight": "The temperature that belongs in the formula is the RISE, not the final reading. Subtracting the starting 20 degrees is worth more marks than all the rest of the arithmetic.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "2.0*0.000019*100", "want": "0.0038"},
    "sol": '''<p><b>What is being tested.</b> A proportionality applied with the right temperature. The physics is one line; the whole question is whether the rise or the reading goes in.</p>
<p><b>Step 1 — the statement.</b> For a solid rod, the change in length is proportional to the original length and to the change in temperature:</p>
<div class="formula">dL = L0 alpha dT</div>
<p>where <code>alpha</code> is the coefficient of linear expansion. The coefficient is a property of the material, so brass's value applies to any brass rod.</p>
<p><b>Step 2 — the temperature change.</b> The rod starts at 20 &deg;C and ends at 120 &deg;C, so:</p>
<div class="formula">dT = 120 - 20 = 100 &deg;C</div>
<p>This is the step to slow down on. The formula needs the <i>change</i> in temperature, and the stem deliberately gives a starting temperature so that a change has to be worked out. Using 120 by mistake inflates the answer by a fifth.</p>
<p><b>Step 3 — put the numbers in.</b></p>
<div class="formula">dL = 2.0 x 1.9 x 10^-5 x 100
   = 3.8 x 10^-3 m</div>
<p>The coefficient is a pure number per degree, so the degrees cancel and the answer comes out in metres, the same unit as <code>L0</code>. That is the unit check: the length unit must be whatever <code>L0</code> was in.</p>
<p><b>Step 4 — convert to a sensible unit.</b> <code>3.8 x 10^-3 m</code> is 3.8 mm. So <b>Answer: C.</b></p>
<p><b>Step 5 — check the size.</b> Brass expands by about nineteen parts per million per degree. Over a hundred degrees that is about nineteen parts in ten thousand, or about two parts in a thousand. Two metres times two parts in a thousand is four millimetres. So 3.8 mm is right, and it is also the right order for something you can measure with a ruler — which is why expansion joints are needed in bridges and railway lines, and why a surveyor's tape is calibrated at a stated temperature.</p>
<p><b>Step 6 — note what the answer does not depend on.</b> The expansion does not depend on the rod's cross-section, only on its length. A thick brass rod and a thin one of the same length expand by the same amount. That is worth noticing because it is not true of every thermal property: heat capacity depends on mass, and expansion does not.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>7.6 mm</b> is twice the correct value. It comes from doubling the coefficient, or from treating the expansion as though it happened along two axes. Linear expansion is a one-dimensional statement, and the coefficient given is for length.</p>
<p>&middot; <b>4.6 mm</b> uses 120 degrees as the change: <code>2.0 x 1.9 x 10^-5 x 120 = 4.6 x 10^-3 m</code>. It is the error the starting temperature of 20 &deg;C exists to catch.</p>
<p>&middot; <b>1.9 mm</b> uses a one-metre rod: <code>1.0 x 1.9 x 10^-5 x 100</code>. The length is in plain sight in the stem, so this is a careless slip rather than a conceptual one — and it is exactly the slip that writing the formula with symbols first prevents.</p>
<p>&middot; <b>0.38 mm</b> is ten times too small, from reading the coefficient as <code>1.9 x 10^-6</code>. The exponent on the coefficient is easy to misread, and the order-of-magnitude check in step 5 catches it: two metres of brass over a hundred degrees gives millimetres, not tenths of a millimetre.</p>
<p><b>The trap.</b> Putting the final temperature into the formula. It is the number that appears in the sentence, so it is the number that gets used. Writing <code>dT = 120 - 20</code> as a separate line is the cheapest possible guard, and it costs a few seconds.</p>
<p><b>Relevant topics:</b> linear thermal expansion; the coefficient of linear expansion; temperature change against temperature reading; why expansion joints exist; the order of magnitude of thermal expansion in metals.</p>''',
    "trap": "Using the final temperature of 120 degrees instead of the 100 degree rise. The formula needs the CHANGE in temperature, and the starting temperature is given precisely so that it has to be subtracted.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 23 — K, nuclear.  The energy released when mass disappears.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 23, "id": "S03-23", "module": "K", "diff": 2,
    "topic": "Mass-energy equivalence: the energy released by a mass defect",
    "rel": [("K", "Mass and energy are related by E = m c^2"),
            ("K", "A decrease in total mass appears as released energy"),
            ("A", "Multiplying numbers in powers of ten and keeping the exponents straight")],
    "key": ["massenergy", "defect", "energy"],
    "stem": '<p>In a nuclear reaction the total mass of the products is less than the total mass of the reactants by <code>3.6 x 10<sup>-30</sup> kg</code>. Take the speed of light as <code>3.0 x 10<sup>8</sup> m/s</code>.</p><p>How much energy is released?</p>',
    "opts": ['1.1 x 10<sup>-21</sup> J',
             '3.2 x 10<sup>-13</sup> J',
             '4.0 x 10<sup>-47</sup> J',
             '2.9 x 10<sup>4</sup> J',
             '3.2 x 10<sup>-14</sup> J'],
    "ans": 1,
    "distractors": ['uses the speed of light rather than its square, so the energy comes out a hundred million times too small',
                    'correct',
                    "divides by the square of the speed of light instead of multiplying, which is the same error with the exponent's sign reversed",
                    'multiplies by the fourth power of the speed of light, squaring c squared a second time',
                    'is a factor of ten out, from misreading the mass defect as 3.6 x 10^-31 kg'],
    "profile": {
        "steps": [
            ("relate", "a decrease in total mass means the missing mass has appeared as energy"),
            ("relate", "the relation is E = m c^2, with m the mass that disappeared"),
            ("solve", "c^2 = (3.0 x 10^8)^2 = 9.0 x 10^16 m^2/s^2"),
            ("solve", "E = 3.6 x 10^-30 x 9.0 x 10^16 = 3.2 x 10^-13 J"),
            ("check", "the answer is a tiny energy for one nucleus, which is why single reactions are not noticeable and a mole of them is"),
        ],
        "relations": ["E = m c^2", "c^2 = 9.0e16", "E = 3.6e-30 x 9.0e16 = 3.2e-13 J"],
        "insight": "The mass defect is tiny and the square of the speed of light is enormous, so the two nearly cancel in the exponent. Keeping the powers of ten straight is the whole of the arithmetic.",
        "shape": "units-consistency",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "3.6*10**(-30)*9.0*10**16", "want": "3.24*10**(-13)"},
    "sol": '''<p><b>What is being tested.</b> A single relation, plus the discipline of handling powers of ten. There is no physics beyond <code>E = m c^2</code>, so the mark turns on the arithmetic.</p>
<p><b>Step 1 — why a mass defect gives energy.</b> Mass and energy are two forms of the same thing, related by <code>E = m c^2</code>. When a reaction produces less mass than it started with, the missing mass has not vanished: it has been converted into energy and carried away by the products. So the mass to use is the <i>decrease</i>, not either total.</p>
<div class="formula">E = m c^2</div>
<p><b>Step 2 — square the speed of light.</b> Do this as a separate line, because it is where the powers of ten get mangled:</p>
<div class="formula">c^2 = (3.0 x 10^8)^2
    = 9.0 x 10^16 m^2/s^2</div>
<p><b>Step 3 — multiply.</b></p>
<div class="formula">E = 3.6 x 10^-30 x 9.0 x 10^16
  = 32.4 x 10^-14
  = 3.2 x 10^-13 J</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 4 — check the units.</b> A kilogram times a square metre per square second is <code>kg m^2 s^-2</code>, which is a joule. The units work out, so the relation has been applied in the right form. A dimensional check on this relation is worth doing because the numbers are so far from everyday experience that intuition cannot help.</p>
<p><b>Step 5 — check the size.</b> <code>3.2 x 10^-13 J</code> is about two million electronvolts, which is exactly the scale of energy released in a single nuclear transition. For one nucleus that is vanishingly small in everyday terms; for a mole of nuclei it is <code>3.2 x 10^-13 x 6 x 10^23 = 2 x 10^11 J</code>, which is the output of a large power station for a minute. The huge factor between one nucleus and a mole is why nuclear energy is worth harnessing at all, and it is a useful thing to carry in mind as a sanity check.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1.1 x 10^-21 J</b> is <code>3.6 x 10^-30 x 3.0 x 10^8</code>: the speed of light used unsquared. The square is the whole content of the relation, and dropping it makes the answer smaller by a factor of <code>3 x 10^8</code>.</p>
<p>&middot; <b>4.0 x 10^-47 J</b> is <code>3.6 x 10^-30/9.0 x 10^16</code>: divided by <code>c^2</code> instead of multiplied. It is the same confusion as the previous option but with the exponent's sign flipped, and it is a very small number — smaller than any single nuclear energy, which is a reason to distrust it.</p>
<p>&middot; <b>2.9 x 10^4 J</b> is <code>3.6 x 10^-30 x 8.1 x 10^33</code>: <code>c^4</code> rather than <code>c^2</code>. It is enormous for one nucleus, and no single nuclear reaction releases tens of thousands of joules.</p>
<p>&middot; <b>3.2 x 10^-14 J</b> is exactly ten times too small, from reading the mass defect as <code>3.6 x 10^-31</code>. It is the right answer to a slightly different question, which is the hardest kind of distractor to spot.</p>
<p><b>The trap.</b> Losing track of the exponents. Multiplying <code>10^-30</code> by <code>10^16</code> is easy; the mistake comes earlier, in squaring <code>3.0 x 10^8</code> and getting <code>9.0 x 10^16</code> rather than <code>9.0 x 10^8</code> or <code>6.0 x 10^16</code>. Squaring the coefficient and doubling the exponent as two separate operations is what keeps it straight.</p>
<p><b>Relevant topics:</b> mass-energy equivalence; the mass defect and binding energy; powers of ten; the electronvolt as a nuclear energy unit; why the energy of one nucleus is tiny and of a mole is not.</p>''',
    "trap": "Dropping the square on c, or squaring it twice. The relation is E = m c^2 with c^2 = 9.0 x 10^16, and keeping the exponent on that one line is the whole of the arithmetic.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 24 — L, quantum.  The stopping potential of a photocell.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 24, "id": "S03-24", "module": "L", "diff": 2,
    "topic": "The photoelectric effect: the stopping potential for a given wavelength",
    "rel": [("L", "Photon energy from wavelength, using hc as a single constant"),
            ("L", "The photoelectric equation: photon energy equals work function plus maximum kinetic energy"),
            ("I", "A stopping potential in volts is numerically the kinetic energy in electronvolts")],
    "key": ["photoelectric", "stopping", "workfunction"],
    "stem": '<p>Light of wavelength 400 nm falls on a metal surface whose work function is 2.0 eV.</p><p>What is the stopping potential for the emitted photoelectrons?</p>',
    "opts": ['3.1 V',
             '5.1 V',
             '2.0 V',
             '0.55 V',
             '1.1 V'],
    "ans": 4,
    "distractors": ['reports the photon energy, which is the first quantity computed in the working rather than the last',
                    'adds the work function to the photon energy instead of subtracting it, giving an electron more energy than the light supplied',
                    'reports the work function, which is a property of the metal and does not depend on the light at all',
                    'halves the maximum kinetic energy, as though the electron took only part of what was available',
                    'correct'],
    "profile": {
        "steps": [
            ("relate", "the photon energy is hc/lambda, and hc can be carried as 1240 eV nm"),
            ("solve", "hf = 1240/400 = 3.1 eV"),
            ("relate", "the photoelectric equation: hf = phi + E_k,max, so the electron keeps the difference"),
            ("solve", "E_k,max = 3.1 - 2.0 = 1.1 eV"),
            ("check", "the stopping potential in volts equals the kinetic energy in electronvolts, so it is 1.1 V"),
        ],
        "relations": ["hf = hc/lambda", "hc = 1240 eV nm", "hf = 1240/400 = 3.1 eV",
                      "hf = phi + E_k,max", "E_k = 1.1 eV"],
        "insight": "The stopping potential is numerically equal to the maximum kinetic energy in electronvolts, because the work done by one volt on one electron is exactly one electronvolt. So the physics is finished once the kinetic energy is known.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1240/400 - 2.0", "want": "1.1"},
    "sol": '''<p><b>What is being tested.</b> The photoelectric equation applied to the energy of the electron rather than to the light, and the conversion from energy to potential that the electronvolt makes trivial.</p>
<p><b>Step 1 — the photon energy.</b> Photon energy is <code>hf</code>, and since <code>f = c/&lambda;</code> it is also <code>hc/&lambda;</code>. The combination <code>hc</code> is a constant, and in the units that make this question easy it is:</p>
<div class="formula">hc = 1240 eV nm</div>
<p>which is worth carrying in mind, because it turns a wavelength in nanometres straight into an energy in electronvolts with one division:</p>
<div class="formula">hf = 1240/400 = 3.1 eV</div>
<p><b>Step 2 — the photoelectric equation.</b> An electron needs the work function just to escape, and whatever is left over becomes its kinetic energy:</p>
<div class="formula">hf = phi + E_k,max
E_k,max = hf - phi
        = 3.1 - 2.0
        = 1.1 eV</div>
<p>The subtraction is not optional. A photon with 3.1 eV cannot give an electron 3.1 eV of motion, because 2.0 eV has already been spent on getting it out of the metal.</p>
<p><b>Step 3 — from energy to stopping potential.</b> To stop an electron of kinetic energy <code>E_k</code> you must do work <code>E_k</code> on it. The work done in moving an electron through a potential difference <code>V</code> is <code>eV</code>, and the electronvolt is <i>defined</i> as the work done on one electron by one volt. So the numbers coincide:</p>
<div class="formula">eV_stop = E_k,max
V_stop = E_k,max in electronvolts = 1.1 V</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 4 — check the size.</b> The photon energy is 3.1 eV and the work function 2.0 eV, so the electron can keep 1.1 eV — about a third of what arrived. The stopping potential of 1.1 V is a typical laboratory value for a photocell, and it is worth noting that it is less than the photon energy, which is always true and is a quick check on any answer of this kind.</p>
<p><b>Step 5 — check what the answer does not depend on.</b> The stopping potential is a property of the <i>light</i> and the metal together, and not of how intense the light is. Brighter light of the same wavelength emits more electrons per second, but every one of them has the same maximum kinetic energy, so the stopping potential is unchanged. That is one of the facts that the wave picture of light cannot explain and the photon picture can.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3.1 V</b> is the photon energy in electronvolts. It is the first number computed, and stopping there is the most natural error in the question: the work function has been ignored, so the electron is credited with energy it spent escaping.</p>
<p>&middot; <b>5.1 V</b> adds the work function instead of subtracting it. It gives the electron more energy than the photon brought, which is impossible, and a moment's thought about conservation rules it out without any arithmetic.</p>
<p>&middot; <b>2.0 V</b> is the work function. It is a real number in this problem and it is in electronvolts, so it looks like a legitimate answer — but it is a property of the metal, and the question is about the light.</p>
<p>&middot; <b>0.55 V</b> is half the correct value. It would be right if only half the available energy reached the electron, and the photoelectric equation has no such halving in it.</p>
<p><b>The trap.</b> Answering with the photon energy. The question gives a wavelength and asks for a voltage, and the photon energy sits in the middle of the working as an intermediate. Intermediates are what the wrong options are made of, and the discipline is to keep going until the quantity named in the question has been produced.</p>
<p><b>Relevant topics:</b> the photoelectric effect; the work function; photon energy and wavelength; the stopping potential; why intensity changes the current but not the stopping potential.</p>''',
    "trap": "Answering with the photon energy. The work function has to come off it, and the stopping potential is the leftover kinetic energy in electronvolts -- always less than the photon energy.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 25 — M, fluids.  What a spring balance reads when the object is submerged.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 25, "id": "S03-25", "module": "M", "diff": 3,
    "topic": "Upthrust: what a spring balance reads with the load under water",
    "rel": [("M", "Upthrust equals the weight of the fluid displaced, so it is density times volume times g"),
            ("C", "The balance reads the resultant of the weight and the upthrust"),
            ("A", "Deciding the sign of the upthrust before doing the arithmetic")],
    "key": ["upthrust", "submerged", "balance"],
    "stem": '<p>A stone has a volume of <code>2.0 x 10<sup>-4</sup> m<sup>3</sup></code> and a mass of 0.50 kg. It is lowered until it is completely under water and weighed on a spring balance. The density of water is 1000 kg/m<sup>3</sup> and <code>g = 10 m/s<sup>2</sup></code>.</p><p>What does the balance read?</p>',
    "opts": ['5.0 N',
             '2.0 N',
             '7.0 N',
             '3.0 N',
             '0 N'],
    "ans": 3,
    "distractors": ["reports the stone's true weight, as though the water exerted no upward force at all",
                    'reports the upthrust itself, which is one of the two forces acting rather than their resultant',
                    'adds the upthrust to the weight instead of subtracting it, which would make the stone seem heavier under water',
                    'correct',
                    'concludes that the stone floats, which it cannot, since its density is well above that of water'],
    "profile": {
        "steps": [
            ("relate", "the balance reads the force the stone exerts on it, which is the resultant of the weight and the upthrust"),
            ("solve", "the true weight is mg = 0.50 x 10 = 5.0 N downwards"),
            ("relate", "the upthrust is the weight of the water displaced, rho V g"),
            ("solve", "upthrust = 1000 x 2.0 x 10^-4 x 10 = 2.0 N upwards"),
            ("solve", "the reading is the difference, 5.0 - 2.0 = 3.0 N"),
            ("check", "the reading must be below the true weight and above zero, and 3.0 N satisfies both bounds"),
        ],
        "relations": ["W = mg = 5.0 N", "upthrust = rho V g = 2.0 N", "reading = W - upthrust"],
        "insight": "Two forces act on the stone and the balance feels their resultant. The upthrust must be subtracted, and its size is fixed by the volume of water pushed aside -- not by the stone's own weight.",
        "shape": "superposition",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "0.50*10 - 1000*0.0002*10", "want": "3.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you identify the forces on the stone and combine them with the right signs. The arithmetic is one subtraction; the whole question is the sign.</p>
<p><b>Step 1 — the two forces.</b> With the stone hanging at rest under water, exactly two forces act on it: its weight downwards and the upthrust from the water upwards. Since it is not accelerating, the balance must supply whatever is needed to make up the difference. The balance therefore reads the <i>resultant</i>:</p>
<div class="formula">reading = weight - upthrust</div>
<p>Fixing the sign first is worth doing, because a sign error produces an answer that is physically impossible and easy to spot if you look for it.</p>
<p><b>Step 2 — the true weight.</b></p>
<div class="formula">W = m g = 0.50 x 10 = 5.0 N</div>
<p><b>Step 3 — the upthrust.</b> Archimedes' principle: the upthrust equals the weight of the fluid displaced. The stone is completely submerged, so it displaces its own volume of water:</p>
<div class="formula">upthrust = rho_water x V x g
         = 1000 x 2.0 x 10^-4 x 10
         = 2.0 N</div>
<p>Notice that the stone's own mass does not appear in this line at all. The upthrust is fixed by how much water is pushed out of the way, and a stone of the same volume but twice the mass would feel exactly the same 2.0 N.</p>
<p><b>Step 4 — combine.</b></p>
<div class="formula">reading = 5.0 - 2.0 = 3.0 N</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 5 — check the direction and the size.</b> The reading must be less than the true weight, because the water pushes up and helps. It must be greater than zero, because the stone sinks. <code>3.0 N</code> satisfies both: it is less than 5.0 N and more than nothing. Any answer above 5.0 N, or negative, or exactly zero, fails one of these bounds without any calculation — and two of the options do exactly that.</p>
<p><b>Step 6 — confirm that the stone really does sink.</b> Its density is <code>0.50/(2.0 x 10^-4) = 2500 kg/m^3</code>, which is two and a half times the density of water. So the weight exceeds the upthrust by a factor of two and a half, and the stone sinks. That is consistent with the reading of 3.0 N being positive. A stone of the same volume with a mass below 0.20 kg would float, and the balance would read zero.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>5.0 N</b> is the stone's true weight. It is what the balance reads in air, and it is the answer if the upthrust is forgotten. This is the commonest error, and the whole point of the question is that weighing under water gives a smaller number.</p>
<p>&middot; <b>2.0 N</b> is the upthrust by itself. It is a force in the problem and it is in newtons, so it looks like a candidate — but the balance does not read the upthrust, it reads the resultant of the upthrust and the weight.</p>
<p>&middot; <b>7.0 N</b> adds the two forces. That would mean the stone is <i>heavier</i> under water than in air, which contradicts the everyday experience of lifting something in a bath. The sign check in step 5 rules it out immediately.</p>
<p>&middot; <b>0 N</b> is the reading for a floating object, where the upthrust exactly balances the weight. This stone has a density of <code>2500 kg/m^3</code> against water's 1000, so it cannot float; the balance would read zero only if the stone's mass were 0.20 kg or less.</p>
<p><b>The trap.</b> Using the stone's weight to compute the upthrust. The upthrust depends on the volume of water displaced, and the volume is given separately for exactly this reason. A stone twice as dense but the same size would feel the same upthrust, and a stone twice the volume would feel twice as much.</p>
<p><b>Relevant topics:</b> Archimedes' principle; upthrust and displaced fluid; density and floating; combining two forces with opposite signs; the apparent weight of a submerged body.</p>''',
    "trap": "Forgetting the upthrust, or adding it instead of subtracting it. The balance reads the resultant of the weight and the upthrust, so the reading must be less than the true weight and greater than zero.",
},

]
