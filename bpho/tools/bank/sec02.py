# -*- coding: utf-8 -*-
"""BPhO Round 0 -- BANK SECTION 02 (S02-01 .. S02-25).

Twenty-five original questions in the exact Round 0 format: single-answer MCQ, five
options, no calculator, one mark each, no negative marking.  They are NOT taken from any
competition paper -- BPhO's papers and other competitions' papers are copyrighted.  What
is borrowed is the style and the difficulty, and `spec.STYLE` records which competitions
set questions of comparable demand inside the R0 scope.

The module mix is the plan's mix for this section, so it is a valid full-length mock:
A3 B2 C2 D1 E2 F2 G2 H3 I1 K2 L3 M2.  Unlike section 1 it draws on L (quantum) and M
(fluids), which the 2025 paper happened to omit but the official R0 scope note lists.

Same field contract as sec01.py -- see that file's docstring for `distractors`,
`profile` and `check`.

Figures are hand-authored inline SVG in fig/, referenced as {{FIG:key}}.
"""

SECTION = 2

QUESTIONS = [

# ═════════════════════════════════════════════════════════════════════════════
# 1 — A, toolkit.  Dimensional analysis of a capillary ripple.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 1, "id": "S02-01", "module": "A", "diff": 3,
    "topic": "Dimensional analysis: the speed of a capillary ripple",
    "rel": [("A", "Matching the base dimensions of both sides of a proposed relation"),
            ("A", "Solving simultaneous equations in the unknown exponents"),
            ("F", "Why a short ripple's speed depends on wavelength at all")],
    "key": ["dimensions", "surface", "ripple"],
    "stem": '<p>Very short ripples on deep water are held in shape by surface tension rather than by gravity. The speed <code>v</code> of such a ripple is found to depend only on the surface tension <code>&gamma;</code> of the water, on its density <code>&rho;</code>, and on the wavelength <code>&lambda;</code>. Which expression is dimensionally a speed?</p>',
    "opts": ["<code>&#8730;(&gamma;&rho;/&lambda;)</code>",
             "<code>&#8730;(&gamma;&lambda;/&rho;)</code>",
             "<code>&#8730;(&gamma;/&rho;&lambda;)</code>",
             "<code>&gamma;/(&rho;&lambda;)</code>",
             "<code>&#8730;(&gamma;&rho;)/&lambda;</code>"],
    "ans": 2,
    "distractors": [
        "multiplies by the density instead of dividing by it, which flips the sign of the mass equation",
        "inverts the length exponent, taking the power of &lambda; as +1/2 where the length equation gives -1/2",
        "correct",
        "gets all three exponents right but forgets that v is a speed, so the square root is missing",
        "takes the root first and divides by &lambda; afterwards, which shifts the length exponent by a half",
    ],
    "profile": {
        "steps": [
            ("relate", "write the base dimensions of the four quantities: [v] = L T^-1, [gamma] = M T^-2, [rho] = M L^-3, [lambda] = L"),
            ("relate", "propose v = k gamma^a rho^b lambda^c and demand that the dimensions match on both sides"),
            ("eliminate", "the time equation fixes a on its own, and the mass equation then fixes b"),
            ("solve", "back-substitute into the length equation to get c, and notice that c comes out negative"),
            ("solve", "assemble the three powers into one product and simplify the exponents into a square root"),
        ],
        "relations": ["[v] = L T^-1", "[gamma] = M T^-2",
                      "a + b = 0", "-2a = -1", "-3b + c = 1"],
        "insight": "The time equation fixes a = 1/2 on its own, and that is the only place a square root can come from. Mass then pins b to -1/2, and the length equation hands over c.",
        "shape": "dimensional-analysis",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "dim", "got": "N m^-1 kg^-1 m^3 m^-1", "want": "m^2 s^-2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can turn a physical statement into three simultaneous equations and solve them, without knowing or remembering any formula for a ripple. Everything needed is in the question.</p>
<p><b>Step 1 — write down the dimensions.</b> Read them off the units rather than trying to recall them:</p>
<div class="formula">[v] = L T^-1
[gamma] = N m^-1 = M T^-2
[rho] = M L^-3
[lambda] = L</div>
<p>The surface tension is the only awkward one. A newton is <code>kg m s^-2</code>, so a newton per metre is <code>kg m s^-2 / m = kg s^-2</code>: mass to the first power, time to the minus two, and no length at all.</p>
<p><b>Step 2 — propose the form and match.</b> Assume the answer is a product of powers, <code>v = k gamma^a rho^b lambda^c</code>, with <code>k</code> a dimensionless number that dimensional analysis cannot find. Match each base dimension in turn:</p>
<div class="formula">mass:         a + b = 0
length:       -3b + c = 1
time:         -2a = -1</div>
<p><b>Step 3 — the time equation alone fixes a.</b> <code>-2a = -1</code> gives <code>a = 1/2</code>. That is the whole reason a square root appears, and it is forced by the time dimension: only surface tension carries time, and it carries it as <code>T^-2</code>.</p>
<p><b>Step 4 — mass, then length.</b> From <code>a + b = 0</code>, <code>b = -1/2</code>: the speed goes <i>down</i> as the water gets denser, which is what a heavy liquid ought to do. Substituting into the length equation, <code>-3(-1/2) + c = 1</code>, so <code>c = 1 - 3/2 = -1/2</code>. The exponent on wavelength is negative.</p>
<p><b>Step 5 — assemble.</b></p>
<div class="formula">v = k gamma^(1/2) rho^(-1/2) lambda^(-1/2)
  = k sqrt(gamma / (rho lambda))</div>
<p>So <b>Answer: C.</b> The <code>1/2</code> powers are not decoration: they are what the three equations produce, and a solution without a square root is already suspicious.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>&#8730;(&gamma;&rho;/&lambda;)</b> divides by the density where it should multiply, i.e. takes <code>b = +1/2</code>. That contradicts the mass equation, which is <code>a + b = 0</code> and not <code>a - b = 0</code>.</p>
<p>&middot; <b>&#8730;(&gamma;&lambda;/&rho;)</b> is right on mass and time but takes <code>c = +1/2</code>, the wrong sign on the wavelength. It is the most tempting wrong answer because it has the right shape — a root, and &lambda; on top.</p>
<p>&middot; <b>&gamma;/(&rho;&lambda;)</b> has all three exponents right and no square root. It fails on inspection: surface tension is <code>kg s^-2</code> and density times wavelength is <code>kg m^-2</code>, so this combination is <code>m^2 s^-2</code> — a squared speed, not a speed.</p>
<p>&middot; <b>&#8730;(&gamma;&rho;)/&lambda;</b> takes the root and then divides by the wavelength as well, which makes the length exponent <code>-3/2</code> instead of <code>-1/2</code>.</p>
<p><b>The trap.</b> Reaching for a remembered formula. There is no need to know anything about ripples: the three equations are forced by the dimensions, and the only freedom left over is the dimensionless constant <code>k</code>, which is exactly the part dimensional analysis is allowed not to know.</p>
<p><b>Relevant topics:</b> base and derived units; the dimensions of mechanical quantities; simultaneous equations in three unknowns; the limits of dimensional analysis.</p>''',
    "trap": "Hunting for a remembered ripple formula. The exponents are forced by the dimensions, so the only thing you cannot derive is the dimensionless constant in front.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 2 — H, circuits.  The resistance of an infinite resistor ladder.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 2, "id": "S02-02", "module": "H", "diff": 3,
    "topic": "An endless resistor ladder: resistance between the input terminals",
    "rel": [("H", "Combining a series resistor with a parallel branch"),
            ("H", "The resistance of a network does not depend on how far away its end is"),
            ("A", "Solving a quadratic, and choosing the root that is physically possible")],
    "key": ["ladder", "selfsimilar", "quadratic"],
    "stem": '<p>The network below repeats the same two-resistor section without end: a resistor <code>R</code> in series, then a resistor <code>R</code> in parallel with whatever follows. {{FIG:s02-02}}</p><p>What is the resistance measured between the two terminals on the left?</p>',
    "opts": ["<code>R(1 + &#8730;5)/2</code>",
             "<code>R(1 + &#8730;3)</code>",
             "<code>2R</code>",
             "<code>R&#8730;2</code>",
             "<code>R(3 + &#8730;5)/2</code>"],
    "ans": 0,
    "distractors": [
        "correct",
        "doubles the linear term, solving R^2 - 2R R_eq - 2R^2 = 0 instead of the equation the circuit actually gives",
        "assumes the endless chain must have endless resistance, which ignores that each added section is in parallel with what came before",
        "takes the geometric mean of the series and parallel branches instead of solving for the fixed point",
        "takes the larger root of the quadratic, which is the one the physics excludes",
    ],
    "profile": {
        "steps": [
            ("relate", "notice that adding one more section to the front leaves the network unchanged, because it was already endless"),
            ("relate", "write the total as one series R in front of the parallel combination of R and the same total again"),
            ("eliminate", "clear the fraction to turn the fixed-point relation into a quadratic in the total"),
            ("solve", "solve the quadratic and reject the negative root, leaving the positive one"),
            ("check", "confirm the surviving root is positive and larger than a single section, as it must be"),
        ],
        "relations": ["R_eq = R + (R R_eq)/(R + R_eq)", "R_eq^2 - R R_eq - R^2 = 0",
                      "R_eq = R(1 + sqrt(5))/2"],
        "insight": "The chain is endless, so one more section makes no difference to it. That self-similarity turns an infinite network into a single equation in one unknown.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "sym",
              "got": "1 + ((1 + sqrt(5))/2)/(1 + (1 + sqrt(5))/2)",
              "want": "(1 + sqrt(5))/2"},
    "sol": '''<p><b>What is being tested.</b> Whether you spot that an endless network is unchanged when you add a section to it. Once you see that, the problem is one equation; without it, there is nothing to write down at all.</p>
<p><b>Step 1 — the self-similarity.</b> Call the resistance of the whole endless ladder <code>R_eq</code>. Now look at what the ladder is made of: a resistor <code>R</code> in series with a branch that has a resistor <code>R</code> in parallel with <i>the rest of the ladder</i>. But the rest of the ladder is the same endless ladder, so its resistance is also <code>R_eq</code>. The network contains itself.</p>
<p><b>Step 2 — write the fixed-point relation.</b></p>
<div class="formula">R_eq = R + (R x R_eq)/(R + R_eq)</div>
<p>The first term is the series resistor. The second is <code>R</code> in parallel with <code>R_eq</code>, which is <code>product over sum</code>.</p>
<p><b>Step 3 — clear the fraction.</b> Multiply through by <code>R + R_eq</code>:</p>
<div class="formula">R_eq(R + R_eq) = R(R + R_eq) + R R_eq
R R_eq + R_eq^2 = R^2 + R R_eq + R R_eq
R_eq^2 - R R_eq - R^2 = 0</div>
<p>The <code>R R_eq</code> terms do not cancel on the right — there are two of them, and only one on the left.</p>
<p><b>Step 4 — solve and choose the root.</b></p>
<div class="formula">R_eq = (R +/- sqrt(R^2 + 4R^2))/2
     = R(1 +/- sqrt(5))/2</div>
<p>So <b>Answer: A</b>, <code>R(1 + &#8730;5)/2</code>, which is about <code>1.618R</code>. The minus root is <code>-0.618R</code>, a negative resistance, which no passive network can have; that is the physics choosing between the two roots for you.</p>
<p><b>Step 5 — check the size of the answer.</b> It must exceed <code>R</code> (there is a resistor in series) and must be less than <code>2R</code> (the parallel branch is smaller than the <code>R</code> in it). <code>1.618R</code> sits between the two, and <code>&#8730;5</code> is about <code>2.24</code>, so <code>1.618</code> is right. This one sanity check removes three of the five options.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>R(1 + &#8730;3)</b> comes from <code>R_eq^2 - 2R R_eq - 2R^2 = 0</code>, i.e. doubling the linear term. It appears if you treat the parallel branch as <code>R</code> in parallel with <code>2R_eq</code>.</p>
<p>&middot; <b>2R</b> assumes an endless chain has endless resistance. It does not: each added section is in parallel with everything after it, so the total is pulled back down. The answer is finite, and less than <code>2R</code>.</p>
<p>&middot; <b>R&#8730;2</b> is the geometric mean of <code>R</code> and <code>2R</code>. It looks plausible and is about <code>1.414R</code>, which is inside the allowed range, so the range check alone does not kill it — the algebra does.</p>
<p>&middot; <b>R(3 + &#8730;5)/2</b> is <code>2.618R</code>, the larger root of the <i>other</i> quadratic. It is greater than <code>2R</code>, so the range check rejects it immediately.</p>
<p><b>The trap.</b> Trying to add up infinitely many sections. The sum does not converge term by term in any convenient way; the fixed-point argument is what makes the problem finite. Whenever a structure repeats endlessly, ask what stays the same when you add one more copy.</p>
<p><b>Relevant topics:</b> series and parallel combinations; self-similar networks; quadratic equations; choosing the root with physical meaning.</p>''',
    "trap": "Trying to sum the sections one at a time. The endless ladder is a fixed point of the relation 'one more section', and that is the only route to a finite equation.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 3 — L, quantum.  DEEP (10 moves).  One wavelength, two metals: the photon
# energy has to be compared with EACH work function before anything else is done.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 3, "id": "S02-03", "module": "L", "diff": 3,
    "topic": "One wavelength on two metals: which one emits, and what the stopping potential is",
    "rel": [("L", "The photon energy hc/lambda fixes the greatest kinetic energy an emitted electron can have"),
            ("L", "A metal emits only if the photon energy exceeds its work function, so every metal has a threshold wavelength"),
            ("L", "The stopping potential in volts is numerically equal to the maximum kinetic energy in electronvolts"),
            ("A", "Working in electronvolt nanometres so that hc is a single remembered number and no unit conversion is needed")],
    "key": ["photoelectric", "work function", "stopping potential", "threshold"],
    "stem": '<p>Light of wavelength 400 nm falls on two clean metal surfaces. Metal A has a work function of 2.0 eV and metal B has a work function of 3.5 eV.</p><p>Which statement is correct?</p>',
    "opts": ['Only A emits, and its stopping potential is 1.1 V',
             'Both metals emit, with stopping potentials of 1.1 V for A and 0.40 V for B',
             'Only B emits, with a stopping potential of 0.40 V',
             'Neither metal emits, because 400 nm is longer than either threshold wavelength',
             'Both metals emit, and the two stopping potentials are equal'],
    "ans": 0,
    "distractors": ['correct',
                    'subtracts B\'s work function from the photon energy and keeps the negative result as a magnitude, when a negative kinetic energy means no electron is emitted at all',
                    'swaps the two work functions, so the metal with the larger one is taken to be the one that emits',
                    'compares the wavelength with the threshold wavelengths without working them out: 400 nm is SHORTER than A\'s threshold of 620 nm, so A emits',
                    'assumes the stopping potential is set by the light alone, when it is set by the difference between the photon energy and the work function of that particular metal'],
    "profile": {
        "steps": [
            ("relate", "write the photon energy as hc over lambda, keeping hc in electronvolt nanometres"),
            ("solve", "put the wavelength in and get the photon energy in electronvolts"),
            ("relate", "compare that energy with metal A's work function before doing anything else, since emission is a threshold condition and not a subtraction that always works"),
            ("solve", "subtract A's work function to get the greatest kinetic energy of an electron leaving A"),
            ("solve", "convert that kinetic energy into a stopping potential, which is a one-to-one correspondence in these units"),
            ("relate", "compare the same photon energy with metal B's work function"),
            ("solve", "find the wavelength that would just free an electron from B, to show why 400 nm is not enough"),
            ("check", "confirm that A's own threshold wavelength is longer than 400 nm, which is the same statement in the other direction"),
            ("check", "note that the stopping potential does not depend on the intensity, so a brighter source changes nothing"),
            ("check", "confirm that the two metals cannot share a stopping potential, since that would need their work functions to be equal"),
        ],
        "relations": ["E = hc / &#955;",
                      "E in eV = 1240 / &#955; in nm",
                      "KE_max = hf &#8722; &#966;",
                      "e V_s = KE_max",
                      "&#955;_threshold = hc / &#966;"],
        "insight": "Emission is a threshold, not a subtraction. A negative value of hf minus phi does not mean electrons come out slowly; it means none come out at all, and that has to be checked separately for each metal before any kinetic energy is calculated.",
        "shape": "limiting-case",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1240/400 - 2.0", "want": "1.1"},
    "sol": '''<p><b>What is being tested.</b> Whether you treat the photoelectric equation as a subtraction that always produces an answer, or as a threshold condition that can fail. Here it fails for one of the two metals, and the whole question turns on noticing that.</p>
<p><b>Step 1 — the photon energy, in a form that needs no calculator.</b> The energy of a photon is <code>hc/&#955;</code>. Rather than converting joules to electronvolts at the end, it is far quicker to remember the product in the units the answer wants:</p>
<div class="formula">hc = 1240 eV nm</div>
<p>This is worth carrying in the head for this paper: it turns every photon-energy question into a single division.</p>
<p><b>Step 2 — evaluate it.</b> With <code>&#955;</code> = 400 nm:</p>
<div class="formula">E = 1240 / 400 = 3.1 eV</div>
<p><b>Step 3 — compare with metal A's work function.</b> Metal A needs 2.0 eV to release an electron, and the photon brings 3.1 eV. Since 3.1 &gt; 2.0, electrons are emitted. This comparison is the step that decides whether the rest of the calculation is meaningful at all.</p>
<p><b>Step 4 — the greatest kinetic energy for A.</b> The work function is the price of getting the electron out; whatever is left over becomes kinetic energy:</p>
<div class="formula">KE_max = E &#8722; &#966;_A = 3.1 &#8722; 2.0 = 1.1 eV</div>
<p>This is the <i>maximum</i> kinetic energy. Electrons deeper in the metal need more than the work function to escape, so they come out slower; 1.1 eV is the ceiling, reached by the electrons at the surface.</p>
<p><b>Step 5 — the stopping potential for A.</b> A stopping potential <code>V_s</code> just prevents the fastest electrons from reaching the collector, so <code>e V_s = KE_max</code>. In electronvolts and volts that ratio is one to one:</p>
<div class="formula">e V_s = 1.1 eV  &#8658;  V_s = 1.1 V</div>
<p>The stopping potential is a property of the light and the metal together &#8212; never of the light alone.</p>
<p><b>Step 6 — now compare with metal B.</b> Metal B needs 3.5 eV, and the photon still brings only 3.1 eV. The difference is negative, and a negative kinetic energy is not a small kinetic energy:</p>
<div class="formula">E &#8722; &#966;_B = 3.1 &#8722; 3.5 = &#8722;0.40 eV</div>
<p>No electron can leave B. The number &#8722;0.40 eV is not a result, it is a statement that the condition failed.</p>
<p><b>Step 7 — the threshold wavelength for B, which says the same thing in the other direction.</b> The longest wavelength that can just free an electron from B is</p>
<div class="formula">&#955;_threshold(B) = hc / &#966;_B = 1240 / 3.5 = 354 nm</div>
<p>400 nm is longer than 354 nm, so its photons carry less energy than B needs. That is why B stays dark.</p>
<p><b>Step 8 — the same check for A.</b> Metal A's threshold is <code>1240/2.0 = 620 nm</code>, and 400 nm is comfortably shorter than that, so A emits with room to spare. Writing the condition both ways &#8212; energy above work function, wavelength below threshold &#8212; is a good habit, because the two forms catch different arithmetic slips.</p>
<p><b>Step 9 — the check that costs nothing.</b> The stopping potential is fixed by the photon energy and the work function. It does not depend on how intense the light is. Making the source brighter sends more electrons per second past the same barrier, but it does not make any single electron faster, so <code>V_s</code> is unchanged. Any option that would move with the intensity is wrong for that reason alone.</p>
<p><b>Step 10 — could the two stopping potentials be equal?</b> Only if the two work functions were equal, since the photon energy is the same for both. They are 2.0 eV and 3.5 eV, so the difference is 1.5 eV and no common value exists.</p>
<p>So <b>Answer: A.</b> Only A emits, and its stopping potential is 1.1 V.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>Both emit, at 1.1 V and 0.40 V</b> is the most dangerous option, because every number in it is arithmetically right. It comes from taking the magnitude of 3.1 &#8722; 3.5 and reporting 0.40 eV as if it were a kinetic energy. That is exactly the mistake the question is aimed at: the photoelectric equation has a domain, and outside it the answer is "no emission", not a smaller number.</p>
<p>&middot; <b>Only B emits</b> swaps the work functions. B has the larger work function, so it is the harder metal to empty, not the easier one. A quick sanity check disposes of it: a metal with a bigger work function can never emit when a smaller-work-function metal does not, under the same light.</p>
<p>&middot; <b>Neither emits</b> reasons about wavelengths without working out the thresholds. Metal A's threshold is 620 nm, and 400 nm is shorter than that, so A emits. It is true that 400 nm is longer than B's threshold of 354 nm &#8212; but that is only half the comparison.</p>
<p>&middot; <b>Both emit, with equal stopping potentials</b> would require the two work functions to be equal. They differ by 1.5 eV.</p>
<p><b>The trap.</b> Running the photoelectric equation for every metal and reporting whatever comes out. The equation only means anything when the photon energy exceeds the work function; below that it produces a negative number that has no physical reading at all. Checking the threshold first takes one comparison and saves the whole question.</p>
<p><b>Relevant topics:</b> the photoelectric effect; work function and threshold frequency; <code>hc</code> in electronvolt nanometres; stopping potential; why intensity affects the current but not the maximum kinetic energy.</p>''',
    "trap": "Subtracting the work function from the photon energy for both metals and keeping the negative answer as a magnitude. A negative kinetic energy means no electron is emitted, not a slow one.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 4 — B, kinematics.  A bouncing ball and the geometric series in time.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 4, "id": "S02-04", "module": "B", "diff": 3,
    "topic": "A bouncing ball: total time before the bouncing dies away",
    "rel": [("B", "Time of fall from rest under constant acceleration"),
            ("B", "Rebound height fixes the speed of rebound, and so the time to the next bounce"),
            ("A", "Summing a geometric series and knowing when it converges")],
    "key": ["bounce", "geometric", "freefall"],
    "stem": '<p>A ball is released from rest at a height <code>h</code> above a hard floor. After each bounce it rises to exactly one quarter of the height from which it fell, and it never stops perfectly. Neglecting air resistance, what is the total time from release until the bouncing has died away?</p>',
    "opts": ["<code>2&#8730;(2h/g)</code>",
             "<code>3&#8730;(2h/g)</code>",
             "<code>4&#8730;(2h/g)</code>",
             "<code>(1 + &#8730;2)&#8730;(2h/g)</code>",
             "<code>(5/2)&#8730;(2h/g)</code>"],
    "ans": 1,
    "distractors": [
        "counts only the first drop and the first rebound, and stops the series there",
        "correct",
        "uses a ratio of 1/2 for the whole series, as if each bounce took half as long as the previous drop rather than half the height being involved",
        "treats each bounce as a single traversal rather than a rise followed by an equal fall",
        "adds three terms of the series and stops, taking the infinite tail to be negligible",
    ],
    "profile": {
        "steps": [
            ("relate", "time the first drop from rest: t = sqrt(2h/g)"),
            ("relate", "use the rebound height to get the rebound speed, and hence the time to rise and fall back"),
            ("eliminate", "collect the times into a geometric series with a common ratio of 1/2"),
            ("solve", "sum the series to infinity and simplify"),
            ("check", "confirm the total is finite and greater than the first drop"),
        ],
        "relations": ["t_fall = sqrt(2h/g)", "v_rebound = sqrt(2g h_n)",
                      "t_n = 2 sqrt(2 h_n/g)", "ratio = 1/2", "sum = a/(1 - r)"],
        "insight": "Each rebound takes half as long as the previous one, because time goes as the square root of height and the heights fall by a factor of four. The times therefore form a geometric series with ratio 1/2.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1 + 2*(1/2)/(1 - 1/2)", "want": "3"},
    "sol": '''<p><b>What is being tested.</b> Whether you can build a series out of the physics and then sum it, rather than trying to add bounce after bounce by hand.</p>
<p><b>Step 1 — the first drop.</b> The ball falls from rest through <code>h</code> under gravity:</p>
<div class="formula">h = 0.5 g t^2
t_0 = sqrt(2h/g)</div>
<p><b>Step 2 — how long one bounce takes.</b> After a bounce the ball rises to a height <code>h_n</code> and falls back. The time to rise to <code>h_n</code> from rest is <code>&#8730;(2h_n/g)</code>, and the fall back takes exactly the same time, because the motion is the same reversed. So one complete bounce lasts</p>
<div class="formula">t_n = 2 sqrt(2 h_n / g)</div>
<p>This factor of two is the single most common place to go wrong: a bounce is up <i>and</i> down.</p>
<p><b>Step 3 — the heights fall by a factor of four.</b> The first rebound reaches <code>h/4</code>, the next <code>h/16</code>, and so on. But time goes as the square root of height, so</p>
<div class="formula">t_1 = 2 sqrt(2(h/4)/g) = 2 sqrt(2h/g) x (1/2) = t_0
t_2 = t_0 x (1/2)
t_3 = t_0 x (1/4)</div>
<p>The heights fall by four, so the times fall by two. The times form a geometric series with common ratio <code>1/2</code>.</p>
<p><b>Step 4 — sum to infinity.</b></p>
<div class="formula">T = t_0 + t_1 + t_2 + ...
  = t_0 + t_0(1/2) + t_0(1/4) + ...
  = t_0 [ 1 + (1/2 + 1/4 + 1/8 + ...) ]
  = t_0 [ 1 + 1 ]
  = 3 t_0</div>
<p>The bracket in the second line is <code>a/(1 - r)</code> with <code>a = 1/2</code> and <code>r = 1/2</code>, which is <code>1</code>. So</p>
<div class="formula">T = 3 sqrt(2h/g)</div>
<p>So <b>Answer: B.</b></p>
<p><b>Step 5 — check it is sensible.</b> The total must be finite (the heights die away fast) and must be bigger than <code>t_0</code>. It is three times <code>t_0</code>: one drop, plus a first bounce that takes as long as the drop, plus the rest. Both conditions hold.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2&#8730;(2h/g)</b> counts the drop and the first bounce and stops. It leaves out the whole infinite tail, which adds exactly one more <code>t_0</code>.</p>
<p>&middot; <b>4&#8730;(2h/g)</b> uses a ratio of <code>1/2</code> on the <i>heights</i> rather than on the times. That would be right if the height fell by a factor of two each time, which would mean a ratio of <code>1/&#8730;2</code> in the times, and a sum of <code>1 + 2/(1 - 1/&#8730;2)</code> — much larger than 4.</p>
<p>&middot; <b>(1 + &#8730;2)&#8730;(2h/g)</b> takes each bounce as a single traversal. It is about <code>2.4</code> times <code>t_0</code>, which is the right order of magnitude, so only the algebra separates it from the correct answer.</p>
<p>&middot; <b>(5/2)&#8730;(2h/g)</b> adds three terms and stops. The tail is not negligible: it contributes <code>t_0/2</code>, which is exactly what this option is missing.</p>
<p><b>The trap.</b> Bouncing balls invite you to add up bounces. Almost every such question is really a geometric series question, and the physics only has to supply the ratio. Here the ratio comes from <code>time proportional to the square root of height</code>, which is why it is <code>1/2</code> and not <code>1/4</code>.</p>
<p><b>Relevant topics:</b> free fall from rest; the symmetry of rise and fall; geometric series and their sums; the square-root relation between time and height.</p>''',
    "trap": "Using the ratio of the heights as the ratio of the times. Time goes as the square root of height, so a factor of four in height is a factor of two in time.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 5 — D, circular motion.  The conical pendulum.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 5, "id": "S02-05", "module": "D", "diff": 3,
    "topic": "Conical pendulum: the period as a function of the cone angle",
    "rel": [("D", "The centripetal force is the horizontal component of the tension"),
            ("C", "Resolving the tension vertically, where the bob has no acceleration"),
            ("A", "Eliminating the tension between the two equations")],
    "key": ["conical", "resolve", "period"],
    "stem": '<p>A small bob hangs on a light inextensible string of length <code>L</code>. The bob is set moving in a horizontal circle so that the string sweeps out a cone, making a constant angle <code>&theta;</code> with the vertical. {{FIG:s02-05}}</p><p>What is the period of the motion?</p>',
    "opts": ["<code>2&pi;&#8730;(L/g)</code>",
             "<code>2&pi;&#8730;(L sin&theta;/g)</code>",
             "<code>2&pi;&#8730;(L/(g cos&theta;))</code>",
             "<code>2&pi;&#8730;(L cos&theta;/g)</code>",
             "<code>2&pi;&#8730;(g/(L cos&theta;))</code>"],
    "ans": 3,
    "distractors": [
        "treats the cone as a vertical hang, so the angle drops out of the answer entirely",
        "uses the radius of the circle, L sin(theta), in place of the length of the string",
        "inverts the cosine factor, which would make the period grow without limit as the string approached horizontal",
        "correct",
        "inverts the whole expression, so the answer has the dimensions of a speed per length rather than a time",
    ],
    "profile": {
        "steps": [
            ("relate", "resolve the tension: vertically it balances the weight, horizontally it supplies the centripetal force"),
            ("relate", "write the radius of the circle in terms of the string length and the cone angle"),
            ("eliminate", "divide the two equations to remove the tension, and replace a with omega^2 r"),
            ("solve", "rearrange for omega and convert to a period"),
            ("check", "test the small-angle limit against the ordinary pendulum"),
            ("check", "confirm the period is independent of the mass and shortens as the cone opens"),
        ],
        "relations": ["T cos(theta) = mg", "T sin(theta) = m omega^2 L sin(theta)",
                      "omega^2 = g/(L cos(theta))", "Period = 2 pi / omega"],
        "insight": "The sine cancels between the radius and the horizontal force, which is why the radius never appears in the answer. What is left is the cosine: the string has to hold the weight as well as turn the bob.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "sym",
              "got": "(2*pi/(2*pi*sqrt(L*cos(theta)/g)))**2*L*cos(theta)",
              "want": "g"},
    "sol": '''<p><b>What is being tested.</b> Whether you can resolve a force into two directions that do different jobs — one of which is not accelerating at all — and then eliminate the force between them.</p>
<p><b>Step 1 — set up the two directions.</b> The bob moves in a horizontal circle at constant speed. That tells you two things at once:</p>
<div class="formula">vertically:     no acceleration at all
horizontally:   accelerating towards the centre, a = omega^2 r</div>
<p>Only two forces act: the weight <code>mg</code> downwards and the tension <code>T</code> along the string. Resolve the tension into a vertical component <code>T cos&theta;</code> and a horizontal component <code>T sin&theta;</code>.</p>
<p><b>Step 2 — vertical.</b> Nothing accelerates vertically, so the vertical forces balance:</p>
<div class="formula">T cos(theta) = mg</div>
<p><b>Step 3 — horizontal.</b> The horizontal component of the tension is the entire centripetal force. The radius of the circle is <code>r = L sin&theta;</code>, the horizontal distance from the pivot to the bob:</p>
<div class="formula">T sin(theta) = m omega^2 r = m omega^2 L sin(theta)</div>
<p><b>Step 4 — divide to kill the tension.</b> Both equations contain <code>T</code>, and dividing one by the other removes it. The <code>sin&theta;</code> also cancels, which is the pleasant surprise of this problem:</p>
<div class="formula">(T sin(theta))/(T cos(theta)) = (m omega^2 L sin(theta))/(mg)
tan(theta) = omega^2 L sin(theta)/g
1/cos(theta) = omega^2 L/g
omega^2 = g/(L cos(theta))</div>
<p>The radius has vanished. The bob could be going round a circle of any size; what fixes the period is only how far the string is tilted.</p>
<p><b>Step 5 — convert to a period.</b></p>
<div class="formula">omega = sqrt(g/(L cos(theta)))
Period = 2 pi / omega = 2 pi sqrt(L cos(theta)/g)</div>
<p>So <b>Answer: D.</b></p>
<p><b>Step 6 — test the limit.</b> As <code>&theta;</code> tends to zero the string hangs vertically, <code>cos&theta;</code> tends to 1, and the period tends to <code>2&pi;&#8730;(L/g)</code> — exactly the small-swing period of an ordinary pendulum. That is a strong check, because a conical pendulum with a very narrow cone really is almost an ordinary pendulum. As <code>&theta;</code> approaches 90 degrees the period falls towards zero, which is also right: a nearly horizontal string needs an enormous speed to hold the bob up.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2&pi;&#8730;(L/g)</b> is the limit answer, not the general one. It is what you get by ignoring <code>&theta;</code> altogether.</p>
<p>&middot; <b>2&pi;&#8730;(L sin&theta;/g)</b> uses the radius as though it were the pendulum length. The radius does appear in the force equation, but it cancels.</p>
<p>&middot; <b>2&pi;&#8730;(L/(g cos&theta;))</b> inverts the cosine. That would make the period grow without limit as the string approached horizontal, when in fact the bob must go round faster and faster. The limit check rejects it.</p>
<p>&middot; <b>2&pi;&#8730;(g/(L cos&theta;))</b> inverts the whole expression. Its dimensions are the reciprocal of a time, so it cannot be a period at all.</p>
<p><b>The trap.</b> Treating <code>sin&theta;</code> and <code>cos&theta;</code> as interchangeable because both are "just the angle". They are attached to different jobs: the cosine carries the weight, the sine carries the centripetal force. Mixing them up is the whole difficulty of this question.</p>
<p><b>Relevant topics:</b> resolving forces; centripetal acceleration; motion in a horizontal circle; the small-angle limit of the simple pendulum.</p>''',
    "trap": "Swapping sin and cos. The cosine component of the tension holds the weight up; the sine component turns the bob. They are not interchangeable.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 6 — C, forces and momentum.  A water jet, and the force that stops it.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 6, "id": "S02-06", "module": "C", "diff": 3,
    "topic": "A water jet striking a wall: the force from a rate of momentum loss",
    "rel": [("C", "Force as rate of change of momentum, rather than mass times acceleration"),
            ("M", "Mass flow rate through a pipe of cross-section A at speed v"),
            ("A", "Checking the dimensions of a proposed expression")],
    "key": ["jet", "momentumrate", "flow"],
    "stem": '<p>Water of density <code>&rho;</code> flows steadily along a pipe of internal cross-sectional area <code>A</code> with speed <code>v</code>. It leaves the pipe and strikes a flat wall head-on, coming to rest against it. What is the average force the water exerts on the wall?</p>',
    "opts": ["<code>&rho;Av</code>",
             "<code>2&rho;Av<sup>2</sup></code>",
             "<code>&rho;Av<sup>2</sup>/2</code>",
             "<code>&rho;A<sup>2</sup>v</code>",
             "<code>&rho;Av<sup>2</sup></code>"],
    "ans": 4,
    "distractors": [
        "uses the mass flow rate and stops there, so the answer is a mass per second rather than a force",
        "applies the momentum change twice, as though the water rebounded at the same speed instead of coming to rest",
        "starts from the kinetic energy and uses half m v squared instead of the change in momentum",
        "squares the area instead of the speed, confusing the cross-section with the rate at which water arrives",
        "correct",
    ],
    "profile": {
        "steps": [
            ("relate", "find the mass of water arriving per second: density times area times speed"),
            ("relate", "that mass arrives carrying speed v, so the momentum arriving per second is rho A v times v"),
            ("eliminate", "the water leaves with no momentum, so the whole of that momentum is destroyed each second"),
            ("check", "force is rate of change of momentum, so the momentum per second IS the force"),
            ("check", "verify the units of the result come out as newtons"),
        ],
        "relations": ["mass per second = rho A v", "momentum per second = rho A v x v",
                      "F = dp/dt"],
        "insight": "A steady stream destroys momentum at a constant rate, and a rate of momentum destruction is a force. There is no acceleration to calculate and no mass to weigh.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "dim", "got": "kg m^-3 m^2 m s^-1 m s^-1", "want": "kg m s^-2"},
    "sol": '''<p><b>What is being tested.</b> Whether you can use <code>F = dp/dt</code> directly, without inventing an acceleration. A stream of fluid has no single mass and no single acceleration, and trying to find either is the wrong road.</p>
<p><b>Step 1 — how much water arrives each second.</b> In one second the water travels a distance <code>v</code>, so the volume that reaches the wall is a cylinder of length <code>v</code> and cross-section <code>A</code>:</p>
<div class="formula">volume per second = A v
mass per second = rho A v</div>
<p><b>Step 2 — how much momentum that water carries.</b> Momentum is mass times velocity, so the momentum arriving each second is</p>
<div class="formula">momentum per second = (rho A v) x v = rho A v^2</div>
<p><b>Step 3 — the water stops, so all of it goes.</b> The water does not bounce and does not splash back in this model: it comes to rest against the wall. So every kilogram-metre-per-second that arrives is destroyed. The rate at which momentum is destroyed is <code>&rho;Av&sup2;</code>.</p>
<p><b>Step 4 — read off the force.</b> Newton's second law in its momentum form says the force equals the rate of change of momentum, so</p>
<div class="formula">F = dp/dt = rho A v^2</div>
<p>So <b>Answer: E.</b></p>
<p><b>Step 5 — a dimensional check.</b> The units of <code>&rho;Av&sup2;</code> are <code>(kg m^-3)(m^2)(m^2 s^-2) = kg m s^-2</code>, which is a newton. The units of the runner-up option, <code>&rho;Av</code>, are <code>kg s^-1</code> — a mass per second, which is not a force at all. The dimensions settle it without any physics.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>&rho;Av</b> stops one step early. It is the mass flow rate, and it is the right quantity to start from — but it still has to be multiplied by the speed to become a momentum flow.</p>
<p>&middot; <b>2&rho;Av&sup2;</b> is right for a jet that rebounds elastically at the same speed, because then the momentum change is <code>mv - (-mv) = 2mv</code>. The question says the water comes to rest, so the factor of two does not belong.</p>
<p>&middot; <b>&rho;Av&sup2;/2</b> is <code>&frac12;mv&sup2;</code> in disguise, i.e. the kinetic energy arriving per second. Energy per second is a power, in watts, not a force.</p>
<p>&middot; <b>&rho;A&sup2;v</b> squares the area instead of the speed. It is dimensionally a force as well, which is what makes it dangerous: the dimensions alone cannot separate it from the right answer, only the physics can.</p>
<p><b>The trap.</b> Reaching for <code>F = ma</code> and hunting for the mass. In a continuous flow the natural quantity is the <i>rate</i>, and the rate of momentum change is already a force. Writing <code>F = dp/dt</code> at the start turns this into a two-line question.</p>
<p><b>Relevant topics:</b> Newton's second law in momentum form; mass flow rate; impulse; dimensional checking as a way to eliminate options.</p>''',
    "trap": "Searching for a mass and an acceleration. In a steady flow the momentum is destroyed at a constant rate, and that rate is the force.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 7 — E, materials.  A wire re-specified in both length and diameter.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 7, "id": "S02-07", "module": "E", "diff": 2,
    "topic": "Extension of a wire when both the length and the diameter are changed",
    "rel": [("E", "Young's modulus as stress over strain"),
            ("E", "Extension proportional to length and inversely proportional to area"),
            ("A", "Area goes as the square of the diameter, so halving d quarters A")],
    "key": ["youngsmodulus", "extension", "scaling"],
    "stem": '<p>A wire of length <code>L</code> and diameter <code>d</code> extends by <code>e</code> when a load <code>F</code> is hung on it. A second wire of the same material has length <code>2L</code> and diameter <code>d/2</code>. What load is needed to make it extend by the same amount <code>e</code>?</p>',
    "opts": ["<code>F/8</code>", "<code>F/4</code>", "<code>F/2</code>", "<code>2F</code>", "<code>F</code>"],
    "ans": 0,
    "distractors": [
        "correct",
        "halves the length effect but forgets that the area has fallen to a quarter",
        "halves the answer twice over, as though both the doubled length and the quartered area made the wire easier to stretch",
        "doubles the length effect and doubles the area effect again, instead of reversing one of them",
        "assumes that changing the dimensions of a wire cannot change the load needed for a given extension",
    ],
    "profile": {
        "steps": [
            ("relate", "write the extension in terms of the load, the length, the area and Young's modulus"),
            ("relate", "replace the diameter by half of itself and square it, so the area becomes a quarter"),
            ("eliminate", "put the new length and the new area into the same formula and cancel Young's modulus"),
            ("check", "confirm that a longer, thinner wire needs LESS load for the same extension"),
        ],
        "relations": ["e = F L/(A E)", "A = pi d^2/4", "e_new = F_new (2L)/((A/4) E)"],
        "insight": "The diameter enters squared, so halving it quarters the area and makes the wire four times as easy to stretch; doubling the length only doubles that. The two effects compound to a factor of eight.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1/(2/(1/4.0))", "want": "1/8.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you can track two changes at once and remember which way each one pushes the answer. The arithmetic is trivial; the bookkeeping is the question.</p>
<p><b>Step 1 — write the relation once.</b> Young's modulus is stress over strain, and rearranging it for the extension gives the working form:</p>
<div class="formula">E = (F/A)/(e/L)  so  e = F L/(A E)</div>
<p>The extension grows with the load and with the length, and shrinks as the area grows. All three dependences are worth saying out loud, because they are what the question is really about.</p>
<p><b>Step 2 — the new area.</b> The cross-section is a circle, so <code>A = &pi;d&sup2;/4</code>. The diameter enters <b>squared</b>. The new wire has diameter <code>d/2</code>, so</p>
<div class="formula">A_new = pi (d/2)^2/4 = (1/4) A</div>
<p>The area is a quarter of the original, not a half. This is the step the question is built around.</p>
<p><b>Step 3 — put both changes in.</b> The same extension <code>e</code> is wanted from the new wire, so solve for the new load:</p>
<div class="formula">e = F_new (2L)/((A/4) E)
  = F_new x 8L/(A E)</div>
<p>For the original wire, <code>e = F L/(A E)</code>. Setting the two equal:</p>
<div class="formula">F L/(A E) = F_new x 8L/(A E)
F = 8 F_new
F_new = F/8</div>
<p>So <b>Answer: A</b>.</p>
<p><b>Step 4 — check the direction.</b> The new wire is twice as long, which makes it stretch more easily, and four times thinner in area, which makes it stretch much more easily. Both changes make it more compliant, so it must need a <i>smaller</i> load for the same extension. Any answer above <code>F</code> is therefore wrong on sight, which removes two of the five options before any algebra.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>F/4</b> accounts for the area alone and ignores the doubled length.</p>
<p>&middot; <b>F/2</b> treats the halved diameter as a halved area. That is the error of forgetting to square, and it is the most common one in this question.</p>
<p>&middot; <b>2F</b> reverses one of the two effects: it takes the doubled length as making the wire stiffer, which is backwards.</p>
<p>&middot; <b>F</b> assumes the geometry cannot matter. A wire is not a rigid body: its dimensions are exactly what sets how far it stretches.</p>
<p><b>The trap.</b> Halving the diameter and halving the area feel like the same statement, and they are not. Every time a diameter, a radius or a side appears in a formula, ask whether it is squared.</p>
<p><b>Relevant topics:</b> Young's modulus; stress and strain; the area of a circle; scaling arguments and their direction.</p>''',
    "trap": "Treating a halved diameter as a halved area. The area goes as the square of the diameter, so it falls to a quarter.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 8 — F, waves.  The Doppler shift from an approaching source.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 8, "id": "S02-08", "module": "F", "diff": 2,
    "topic": "Doppler shift: the frequency heard from a source closing at v/5",
    "rel": [("F", "The Doppler relation for a source moving towards a stationary observer"),
            ("F", "Why the observed frequency rises: the waves are crowded into a shorter distance"),
            ("A", "Forming and simplifying a ratio of two speeds")],
    "key": ["doppler", "ratio", "sound"],
    "stem": '<p>A car sounding its horn at a steady frequency travels in a straight line towards a stationary observer at a steady speed of <code>v/5</code>, where <code>v</code> is the speed of sound in air. What is the ratio of the frequency the observer hears to the frequency the horn emits?</p>',
    "opts": ["<code>5/4</code>", "<code>4/5</code>", "<code>6/5</code>",
             "<code>25/16</code>", "<code>5/6</code>"],
    "ans": 0,
    "distractors": [
        "correct",
        "uses the receding form v/(v + u), which is the shift heard after the car has gone past",
        "adds the speed ratio to 1 instead of forming v/(v - u)",
        "applies the shift twice, as though the sound were reflected back off the observer",
        "inverts the fraction, putting v - u on the top instead of the bottom",
    ],
    "profile": {
        "steps": [
            ("relate", "recognise that the source is closing, so the observed frequency must rise"),
            ("relate", "write the Doppler relation for a moving source and a stationary observer"),
            ("eliminate", "substitute u = v/5 and cancel the common factor of v"),
            ("check", "confirm the ratio is greater than 1, as it must be for an approaching source"),
        ],
        "relations": ["f' = f v/(v - u)", "u = v/5", "f'/f = 1/(1 - 1/5)"],
        "insight": "A closing source crowds its waves into a shorter stretch of air, so the same number of waves arrives per second as would arrive from a faster wave train. The speed of the waves is unchanged; only the spacing is.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1/(1 - 1/5.0)", "want": "1.25"},
    "sol": '''<p><b>What is being tested.</b> Whether you know which way the shift goes and which quantity sits in the denominator. Both mistakes are caught by one question asked at the start: should the answer be bigger than 1 or smaller?</p>
<p><b>Step 1 — decide the direction before writing anything.</b> The car is closing on the observer. Each successive wave crest is emitted from a point slightly nearer than the last, so the crests are crowded together. Crowded crests mean a shorter wavelength, and with the wave speed unchanged a shorter wavelength means a higher frequency. So <code>f'/f</code> must be <b>greater than 1</b>.</p>
<p><b>Step 2 — write the relation.</b> For a source moving at speed <code>u</code> towards a stationary observer, with sound speed <code>v</code>:</p>
<div class="formula">f' = f v/(v - u)</div>
<p>The <code>v - u</code> is in the denominator precisely because the crowding makes the apparent wavelength <i>shorter</i>, and a shorter wavelength means a larger frequency.</p>
<p><b>Step 3 — substitute and simplify.</b> With <code>u = v/5</code>:</p>
<div class="formula">f'/f = v/(v - v/5)
     = v/((4/5)v)
     = 5/4</div>
<p>The common factor of <code>v</code> cancels, which is why the answer does not depend on the speed of sound at all. So <b>Answer: A</b>.</p>
<p><b>Step 4 — the check from step 1.</b> <code>5/4 = 1.25</code>, which is greater than 1. The direction check passes. It also rules out <code>4/5</code>, <code>5/6</code> and any other value below 1 in one stroke.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>4/5</b> is the receding answer, <code>v/(v + u)</code>. It is exactly what the observer hears <i>after</i> the car has passed, and it is the single most common wrong answer here.</p>
<p>&middot; <b>6/5</b> comes from <code>1 + u/v = 1 + 1/5</code>. It adds the ratio to one instead of forming <code>v/(v - u)</code>. Numerically it is close to the right answer, which is what makes it dangerous.</p>
<p>&middot; <b>25/16</b> is <code>(5/4)&sup2;</code>, the shift applied twice. That is the answer for a source whose sound reflects back from a moving observer, not for a single journey.</p>
<p>&middot; <b>5/6</b> inverts the fraction, putting <code>v - u</code> on top. The ratio would then be below 1, contradicting the direction check.</p>
<p><b>The trap.</b> Trying to remember whether the source speed goes on the top or the bottom. Do not remember: decide the direction first. Closing means higher, so the answer must exceed 1, and only one arrangement of <code>v</code> and <code>v - u</code> gives that.</p>
<p><b>Relevant topics:</b> the Doppler effect for a moving source; wavelength and frequency at fixed wave speed; ratio simplification; limiting and direction checks.</p>''',
    "trap": "Reciting the Doppler formula without deciding which way the shift goes. Closing means higher, and that one fact fixes where v - u belongs.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 9 — G, optics.  A prism at minimum deviation.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 9, "id": "S02-09", "module": "G", "diff": 2,
    "topic": "A prism at minimum deviation: finding the deviation from the refractive index",
    "rel": [("G", "The prism relation at minimum deviation, n sin(A/2) = sin((A + D)/2)"),
            ("G", "Why minimum deviation happens when the ray passes symmetrically"),
            ("A", "Undoing a sine, and knowing that a sine of 1/2 does not mean an angle of 1/2")],
    "key": ["prism", "refraction", "sine"],
    "stem": '<p>A ray of monochromatic light passes through a glass prism of refracting angle <code>60&deg;</code> and refractive index <code>&#8730;2</code>. The prism is turned until the deviation is as small as it can be. What is the angle of minimum deviation?</p>',
    "opts": ["<code>45&deg;</code>", "<code>60&deg;</code>", "<code>30&deg;</code>",
             "<code>15&deg;</code>", "<code>22.5&deg;</code>"],
    "ans": 2,
    "distractors": [
        "reports (A + D)/2, the angle the ray makes inside the prism, and stops before undoing the half",
        "assumes the deviation equals the prism angle, which happens only for one particular glass",
        "correct",
        "subtracts A/2 twice instead of once, removing 30 degrees from the answer a second time",
        "divides (A + D) by four instead of by two, halving the half-angle",
    ],
    "profile": {
        "steps": [
            ("relate", "recall that at minimum deviation the ray passes symmetrically, so the angle inside is A/2, and write Snell's law in the minimum-deviation form"),
            ("eliminate", "take the inverse sine to get (A + D)/2"),
            ("solve", "double it and subtract A to isolate D"),
            ("check", "confirm the answer is positive and smaller than the prism angle"),
        ],
        "relations": ["n sin(A/2) = sin((A + D)/2)", "A = 60 deg", "n = sqrt(2)"],
        "insight": "At minimum deviation the ray crosses the prism symmetrically, which is what turns the general two-surface refraction problem into one Snell's law at one face.",
        "shape": "diagram-geometry",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "2*degrees(asin(sqrt(2)*sin(radians(30)))) - 60", "want": "30"},
    "sol": '''<p><b>What is being tested.</b> Whether you know the minimum-deviation relation and, more importantly, whether you can undo it in the right order. The physics is one line; the algebra is where marks are lost.</p>
<p><b>Step 1 — what "minimum deviation" buys you.</b> In general a ray is refracted at two faces and the deviation depends on the angle of incidence. But there is one incidence angle at which the deviation is least, and at that angle the ray passes through the prism <b>symmetrically</b>: it makes the same angle with both faces. That symmetry is what makes the problem solvable, because it means the ray inside makes an angle <code>A/2</code> with each normal, and Snell's law only has to be applied once.</p>
<div class="formula">n sin(A/2) = sin((A + D)/2)</div>
<p><b>Step 2 — substitute the numbers.</b> With <code>A = 60&deg;</code> and <code>n = &#8730;2</code>:</p>
<div class="formula">sqrt(2) sin(30 deg) = sin((60 deg + D)/2)
sqrt(2) x 1/2 = sin((60 deg + D)/2)
1/sqrt(2) = sin((60 deg + D)/2)</div>
<p><b>Step 3 — undo the sine.</b> The angle whose sine is <code>1/&#8730;2</code> is <code>45&deg;</code>:</p>
<div class="formula">(60 deg + D)/2 = 45 deg
60 deg + D = 90 deg
D = 30 deg</div>
<p>So <b>Answer: C.</b></p>
<p><b>Step 4 — check the answer is possible.</b> A deviation of <code>30&deg;</code> is positive, which it must be for a ray passing through a prism, and it is smaller than the prism angle, which is typical for a moderately refracting glass. A negative or absurdly large answer would mean an arithmetic slip.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>45&deg;</b> is the value of <code>(A + D)/2</code>. It is the right number at the wrong stage: the half-angle has been found and then reported as though it were the deviation.</p>
<p>&middot; <b>60&deg;</b> assumes <code>D = A</code>. That is true only for the one glass whose index makes it so, and this is not that glass. It is a tempting answer because the prism angle is the only other angle in the question.</p>
<p>&middot; <b>15&deg;</b> subtracts <code>A/2</code> a second time, so it removes 30 degrees twice from the 60.</p>
<p>&middot; <b>22.5&deg;</b> divides <code>(A + D)</code> by four instead of two, which halves the half-angle.</p>
<p><b>The trap.</b> Treating <code>sin&theta;</code> as if it were <code>&theta;</code>. The sine of 30 degrees is a half, and the angle whose sine is a half is 30 degrees — but the angle whose sine is <code>1/&#8730;2</code> is <b>45</b> degrees, not <code>0.707</code> degrees and not 30. Writing the inverse sine explicitly, and keeping the degree signs attached, prevents the whole family of slips.</p>
<p><b>Relevant topics:</b> refraction at a plane surface; the prism relation; minimum deviation; inverse trigonometric functions.</p>''',
    "trap": "Treating sin(theta) as though it were theta. The angle whose sine is 1/sqrt(2) is 45 degrees, and that is the step the question is really testing.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 10 — H, circuits.  How the power divides between parallel resistors.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 10, "id": "S02-10", "module": "H", "diff": 2,
    "topic": "Parallel resistors: which one takes the larger share of the power",
    "rel": [("H", "Resistors in parallel share the same potential difference"),
            ("H", "Power dissipated as V squared over R, so the smaller resistance takes more"),
            ("A", "Forming a fraction from two ratios and simplifying it")],
    "key": ["parallel", "power", "fraction"],
    "stem": '<p>A <code>6 &Omega;</code> resistor and a <code>3 &Omega;</code> resistor are connected in parallel across a battery of negligible internal resistance. What fraction of the total power supplied by the battery is dissipated in the <code>3 &Omega;</code> resistor?</p>',
    "opts": ["<code>1/3</code>", "<code>2/3</code>", "<code>1/2</code>",
             "<code>4/9</code>", "<code>5/6</code>"],
    "ans": 1,
    "distractors": [
        "divides the power in proportion to resistance, so the smaller resistor is given the smaller share",
        "correct",
        "splits the power equally, as though the two resistors carried the same current",
        "squares the resistance ratio instead of taking it to the first power",
        "adds the two fractions 1/3 and 1/2 together rather than forming a proper share",
    ],
    "profile": {
        "steps": [
            ("relate", "note that parallel resistors share the same potential difference, so write the power as V^2/R"),
            ("relate", "form the two powers in terms of the common V"),
            ("eliminate", "add them to get the total, then divide one by the total"),
            ("check", "confirm the smaller resistance takes the larger share, as it must"),
        ],
        "relations": ["P = V^2/R", "P_3 = V^2/3", "P_6 = V^2/6",
                      "fraction = P_3/(P_3 + P_6)"],
        "insight": "In parallel the voltage is what is common, so power goes as 1/R and the smaller resistor takes the bigger share. In series the current is common and the ordering reverses.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(1/3.0)/((1/3.0) + (1/6.0))", "want": "2/3.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you know which quantity is shared. That single decision sets the direction of the answer before any arithmetic is done.</p>
<p><b>Step 1 — what is common, and therefore which form of the power to use.</b> Resistors in parallel have the <b>same potential difference</b> across them. So the useful form of the power is the one containing <code>V</code>:</p>
<div class="formula">P = V^2/R</div>
<p>The other form, <code>P = I&sup2;R</code>, would be the wrong choice here, because the currents are not equal.</p>
<p><b>Step 2 — the two powers.</b> With a common <code>V</code>:</p>
<div class="formula">P_3 = V^2/3      P_6 = V^2/6</div>
<p>The <code>3 &Omega;</code> resistor dissipates twice the power of the <code>6 &Omega;</code> one, because <code>V&sup2;</code> is divided by a smaller number.</p>
<p><b>Step 3 — the fraction.</b></p>
<div class="formula">P_total = V^2/3 + V^2/6 = V^2(2/6 + 1/6) = V^2/2
fraction = P_3/P_total = (V^2/3)/(V^2/2) = 2/3</div>
<p>The <code>V&sup2;</code> cancels, which is why the answer does not depend on the battery voltage. So <b>Answer: B</b>.</p>
<p><b>Step 4 — check the direction.</b> The <code>3 &Omega;</code> resistor is the smaller one, so in parallel it must take the larger share. <code>2/3</code> is more than a half, which is consistent. Any answer below <code>1/2</code> is wrong on sight, and that removes <code>1/3</code> and <code>4/9</code> immediately.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/3</b> divides the power in proportion to the resistances, giving the smaller resistor the smaller share. That is the rule for resistors in <i>series</i>, where the current is common and <code>P = I&sup2;R</code>. Here it is exactly backwards.</p>
<p>&middot; <b>1/2</b> splits the power equally, which would need the two resistances to be equal.</p>
<p>&middot; <b>4/9</b> is <code>(2/3)&sup2;</code>, the resistance ratio squared. There is no squared ratio in this problem.</p>
<p>&middot; <b>5/6</b> is <code>1/3 + 1/2</code>, adding two fractions that were never shares of the same total.</p>
<p><b>The trap.</b> The direction question — "does the smaller resistor take more or less?" — is worth answering before touching the algebra, because in parallel the answer is "more" and in series it is "less". Getting that right converts a five-option guess into a two-option calculation.</p>
<p><b>Relevant topics:</b> parallel circuits; the two forms of the power equation; choosing the form that matches the shared quantity; simplifying algebraic fractions.</p>''',
    "trap": "Dividing power in proportion to resistance. That is the series rule. In parallel the voltage is common, so power goes as 1/R and the smaller resistor takes more.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 11 — K, nuclear.  Half-life off a logarithmic activity axis.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 11, "id": "S02-11", "module": "K", "diff": 3,
    "topic": "Half-life from a decay curve plotted with a logarithmic activity axis",
    "rel": [("K", "Exponential decay plots as a straight line when the activity axis is logarithmic"),
            ("A", "Equal ratios occupy equal distances on a logarithmic axis"),
            ("K", "Turning a ratio into a number of half-lives by expressing it as a power of two")],
    "key": ["decay", "half-life", "logarithm"],
    "stem": '''<p>The activity of a pure radioactive source is measured over twelve minutes. The results are plotted with the activity on a <b>logarithmic</b> scale and the time on a linear scale. {{FIG:s02-11}}</p>
<p>The plotted points lie on a straight line. What is the half-life of the source?</p>''',
    "opts": ["<code>1.5</code> min", "<code>3</code> min", "<code>4</code> min",
             "<code>6</code> min", "<code>12</code> min"],
    "ans": 2,
    "distractors": [
        "divides the twelve minutes by the factor of eight, treating a ratio as a count of half-lives",
        "counts four halvings where the sequence 800 to 400 to 200 to 100 has only three",
        "correct",
        "takes the whole twelve minutes as two halvings, which would need the activity to fall by a factor of four",
        "takes the time to reach the last plotted point as the half-life itself",
    ],
    "profile": {
        "steps": [
            ("relate", "a straight line on a logarithmic axis means the activity is multiplied by the same factor in every equal interval, which is what exponential decay does"),
            ("relate", "read the two stated activities as a ratio rather than a difference: 800 divided by 100"),
            ("eliminate", "express that ratio as a power of two to turn it into a number of halvings"),
            ("solve", "divide the twelve minutes by the number of halvings"),
            ("check", "step the activity down one halving at a time and confirm it lands on the stated point"),
        ],
        "relations": ["A = A_0 (1/2)^(t/T)", "800/100 = 8", "8 = 2^3", "T = 12/3"],
        "insight": "On a logarithmic axis the only quantity you can read off is a ratio, and a ratio of eight is three halvings. The vertical distance between the points is proportional to the number of halvings, not to the change in activity.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "12/log(8, 2)", "want": "4"},
    "sol": '''<p><b>What is being tested.</b> Whether you know what a logarithmic axis is <i>for</i>. On a log axis equal ratios occupy equal distances, so an exponential decay plots as a straight line and its halvings become equal steps that can simply be counted.</p>
<p><b>Step 1 — why the straight line matters.</b> A straight line on a log plot means the activity is multiplied by the same factor in every equal interval of time. That is exactly what exponential decay does:</p>
<div class="formula">A = A_0 (1/2)^(t/T)</div>
<p>Take logarithms of both sides and the right-hand side becomes linear in <code>t</code>, with slope fixed by <code>T</code>. So the straightness of the graph is not a coincidence to be noted — it is the statement that the decay is exponential, and it licenses the method that follows.</p>
<p><b>Step 2 — read a ratio, not a difference.</b> The activity does not fall by 700 kBq. It falls by a <i>factor</i>:</p>
<div class="formula">800/100 = 8</div>
<p>On a linear axis the difference would be the useful quantity. Here it is not: the gap between 100 and 200 is the same size as the gap between 400 and 800, so a fall of 50 kBq and a fall of 400 kBq are drawn identically.</p>
<p><b>Step 3 — turn the factor into a number of halvings.</b> One halving divides by two, two halvings divide by four, three divide by eight:</p>
<div class="formula">8 = 2^3</div>
<p>So three halvings carry the activity from 800 kBq down to 100 kBq.</p>
<p><b>Step 4 — divide.</b> Those three halvings occupy the twelve minutes between the two stated points:</p>
<div class="formula">T = 12/3 = 4 min</div>
<p>So <b>Answer: C</b>.</p>
<p><b>Step 5 — check it against the graph.</b> Start at 800 kBq. After one half-life, 400 kBq; after two, 200 kBq; after three, 100 kBq — which is the stated point at twelve minutes. So four minutes per halving lands exactly on both labelled points, and it is the only value that does.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1.5 min</b> divides twelve by the factor eight, treating a ratio as though it were a count. Eight is how much the activity is divided by, not how many times.</p>
<p>&middot; <b>3 min</b> counts four halvings where there are three. The chain 800 &rarr; 400 &rarr; 200 &rarr; 100 has three steps, not four, because the number of steps is one fewer than the number of values in the chain.</p>
<p>&middot; <b>6 min</b> takes the whole twelve minutes as two halvings, which would be right only if the activity had fallen by a factor of four, to 200 kBq.</p>
<p>&middot; <b>12 min</b> takes the time to reach the last plotted point as the half-life itself. After one half-life the activity must have halved, and it has not.</p>
<p><b>The trap.</b> Reading a logarithmic axis as though it were linear. Everything about the drawing looks like an ordinary graph, and the natural instinct is to measure the fall in kBq. On a log axis that measurement is meaningless; the only quantity with a physical meaning is the ratio of the two values, and the only way to use it is as a power of two.</p>
<p><b>Relevant topics:</b> exponential decay; half-life; logarithmic scales and the reading of graphs; powers of two.</p>''',
    "trap": "Reading the logarithmic axis as linear and measuring the fall in kBq. On a log axis a fall of 700 kBq and a fall of 50 kBq can be the same vertical distance, so only the ratio is meaningful.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 12 — H, circuits.  The internal resistance is inside the loop.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 12, "id": "S02-12", "module": "H", "diff": 3,
    "topic": "Power in one resistor of a network driven by a cell with internal resistance",
    "rel": [("H", "Reducing a parallel pair and then adding the series resistance"),
            ("H", "The internal resistance of the source is part of the same series loop"),
            ("H", "Choosing the form of the power equation that matches the quantity you know")],
    "key": ["internal", "parallel", "power"],
    "stem": '''<p>A cell of electromotive force <code>12 V</code> and internal resistance <code>2 &Omega;</code> is connected to two <code>6 &Omega;</code> resistors in parallel with each other, and that combination in series with a <code>3 &Omega;</code> resistor. {{FIG:s02-12}}</p>
<p>What is the power dissipated in the <code>3 &Omega;</code> resistor?</p>''',
    "opts": ["<code>4.5 W</code>", "<code>6.75 W</code>", "<code>12 W</code>",
             "<code>13.5 W</code>", "<code>18 W</code>"],
    "ans": 1,
    "distractors": [
        "reports the power wasted inside the source, which is a real quantity but not the one asked for",
        "correct",
        "leaves the internal resistance out of the loop, giving a current of 2 A instead of 1.5 A",
        "reports the total power delivered to the external circuit, not the power in the single 3 ohm resistor",
        "reports the total power supplied by the cell, including the power wasted inside it",
    ],
    "profile": {
        "steps": [
            ("relate", "reduce the parallel pair: two equal resistors in parallel give half of one of them"),
            ("relate", "add the series 3 ohm resistor to the parallel combination to get the external resistance"),
            ("relate", "add the internal resistance, because it lies in the same loop and carries the same current"),
            ("solve", "divide the electromotive force by the total resistance to get the current"),
            ("solve", "square the current and multiply by the resistance of interest to get the power"),
            ("check", "confirm the potential differences round the loop: terminal p.d. minus the drop across the 3 ohm resistor must equal the drop across the pair"),
        ],
        "relations": ["6 || 6 = 3", "R_ext = 3 + 3 = 6", "R_total = 6 + 2 = 8",
                      "I = E/(R_ext + r)", "P = I^2 R"],
        "insight": "The internal resistance carries the same current as everything else, so it belongs in the denominator of the current calculation. Every wrong option except one is a real power somewhere in this circuit, measured at the wrong place.",
        "shape": "circuit-reduction",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
        "figure_support": True,
    },
    "check": {"kind": "eval", "expr": "(12/((6*6/(6+6)) + 3 + 2))**2 * 3", "want": "6.75"},
    "sol": '''<p><b>What is being tested.</b> Two habits at once: reducing a network from the inside out, and refusing to forget that the source has resistance of its own. The second habit is what separates the correct answer from the most popular wrong one.</p>
<p><b>Step 1 — reduce the parallel pair.</b> The two <code>6 &Omega;</code> resistors carry the same potential difference, and they are equal, so the combination is half of one of them:</p>
<div class="formula">1/R_p = 1/6 + 1/6 = 2/6
R_p = 3 &Omega;</div>
<p><b>Step 2 — add the series resistor.</b> The parallel combination and the <code>3 &Omega;</code> resistor carry the same current, so their resistances add:</p>
<div class="formula">R_ext = 3 + 3 = 6 &Omega;</div>
<p><b>Step 3 — the internal resistance is in the loop too.</b> The current flows through the source as well as through the external circuit, so the <code>2 &Omega;</code> is in series with everything else:</p>
<div class="formula">R_total = 6 + 2 = 8 &Omega;</div>
<p>This is the step that most candidates skip, and it is worth pausing on. The electromotive force is the energy per unit charge supplied by the source <i>including</i> what it spends on its own resistance. Only the terminal potential difference is available to the external circuit, and the terminal p.d. is not 12 V.</p>
<p><b>Step 4 — the current.</b></p>
<div class="formula">I = E/R_total = 12/8 = 1.5 A</div>
<p><b>Step 5 — the power in the 3 &Omega; resistor.</b> The current is known and the resistance is known, so the form of the power equation to use is the one without a voltage in it:</p>
<div class="formula">P = I^2 R = (1.5)^2 x 3 = 2.25 x 3 = 6.75 W</div>
<p>So <b>Answer: B</b>.</p>
<p><b>Step 6 — check the potential differences round the loop.</b> The terminal p.d. is <code>12 - 1.5 x 2 = 9 V</code>. Across the <code>3 &Omega;</code> resistor the drop is <code>1.5 x 3 = 4.5 V</code>. That leaves <code>9 - 4.5 = 4.5 V</code> across the parallel pair, and <code>1.5 A</code> through <code>3 &Omega;</code> gives <code>4.5 V</code>. The two agree, so the reduction was consistent. As a second check, the total power supplied is <code>12 x 1.5 = 18 W</code>, of which <code>1.5^2 x 2 = 4.5 W</code> is wasted internally and <code>13.5 W</code> reaches the external circuit — and <code>13.5 = 6.75 + 6.75</code>, the two halves of the external circuit splitting the power equally because both are <code>3 &Omega;</code>.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>4.5 W</b> is the power dissipated inside the source, <code>I^2 r</code>. It is a real and relevant quantity — it is the whole reason the terminal p.d. is not 12 V — but it is not the power in the <code>3 &Omega;</code> resistor.</p>
<p>&middot; <b>12 W</b> comes from leaving the internal resistance out, so that <code>I = 12/6 = 2 A</code> and <code>P = 2^2 x 3 = 12 W</code>. This is the most common error: the source is treated as ideal. A current of 2 A would also imply a terminal p.d. of 12 V, which cannot be right when 2 A is flowing through a 2 &Omega; internal resistance.</p>
<p>&middot; <b>13.5 W</b> is the total power delivered to the external circuit. It is right about the current and wrong about the location: the external circuit contains the parallel pair as well as the series resistor.</p>
<p>&middot; <b>18 W</b> is the total power supplied by the cell, internal loss included.</p>
<p><b>The trap.</b> Every one of the four wrong options is a genuine power in this circuit. Nothing is arithmetically wrong with any of them; they are answers to four different questions. The work is therefore not the calculation but the identification — decide which quantity the question asks for, and say so in words, before touching a formula.</p>
<p><b>Relevant topics:</b> resistors in series and in parallel; electromotive force and internal resistance; the terminal potential difference; the two forms of the power equation.</p>''',
    "trap": "Treating the cell as ideal and using 12 V across the external circuit. The internal resistance carries the same current, so it belongs in the denominator: 12/8, not 12/6.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 13 — C, forces.  DEEP (10 moves).  A bullet embeds, and then friction removes
# what is left of the kinetic energy.  Momentum first, energy second, and the
# two must not be mixed.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 13, "id": "S02-13", "module": "C", "diff": 3,
    "topic": "A bullet embedding in a block: momentum first, then friction, then the coefficient",
    "rel": [("C", "Momentum is conserved through the embedding, even though most of the kinetic energy is not"),
            ("C", "After the collision the only horizontal force is friction, so friction doing work is what removes the remaining kinetic energy"),
            ("C", "The friction force on a block sliding on level ground is the coefficient times the whole weight, because the normal reaction balances it"),
            ("A", "Dividing out a common factor before substituting, so the arithmetic stays exact and no decimals accumulate")],
    "key": ["momentum", "collision", "friction", "energy"],
    "stem": '<p>A bullet of mass 20 g travelling horizontally at 300 m/s embeds itself in a block of mass 1980 g resting on a rough horizontal surface. The block and bullet then slide 1.5 m before coming to rest. Take <code>g</code> = 10 m s<sup>-2</sup>.</p><p>What is the coefficient of friction between the block and the surface?</p>',
    "opts": ['0.30', '0.60', '0.20', '0.15', '0.45'],
    "ans": 0,
    "distractors": ['correct',
                    'takes the kinetic energy as the speed squared times the mass, leaving out the factor of one half, which doubles the coefficient',
                    'leaves the speed unsquared, dividing the speed itself by g and the distance instead of the square of the speed',
                    'takes the sliding distance as 3.0 m, twice the value given, which halves the coefficient',
                    'takes the sliding distance as 1.0 m, which raises the coefficient by half again'],
    "profile": {
        "steps": [
            ("relate", "recognise that the embedding is a collision, so momentum is the quantity that carries across it and kinetic energy is not"),
            ("solve", "write the momentum before the collision and the momentum after it, with the bullet and block moving together afterwards"),
            ("solve", "solve for the common speed, keeping the masses in kilograms"),
            ("solve", "work out the kinetic energy of the block and bullet immediately after the collision"),
            ("relate", "note that the only horizontal force from then on is friction, and write that force in terms of the coefficient and the weight"),
            ("solve", "write the work done by friction over the sliding distance"),
            ("solve", "equate that work to the kinetic energy and solve for the coefficient"),
            ("check", "find the fraction of the original kinetic energy lost in the embedding, which must be almost all of it"),
            ("check", "check the dimensions of the result, since a coefficient of friction has none"),
            ("check", "check the sense of the answer: a larger coefficient must give a shorter slide for the same collision"),
        ],
        "relations": ["m u = (m + M) V",
                      "KE = ½ (m + M) V<sup>2</sup>",
                      "F_friction = &#956; (m + M) g",
                      "work = F d",
                      "KE lost in the embedding = (M / (m + M)) &#215; KE_before"],
        "insight": "Two different conservation laws apply at two different moments. Momentum carries the motion through the embedding, because the collision is far too brief for friction to matter; energy carries it from there to the stop, because from then on the only thing acting is friction. Using energy across the embedding, or momentum after it, is what makes this question go wrong.",
        "shape": "conservation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(0.020*300/2.0)*(0.020*300/2.0)/(2*10*1.5)", "want": "0.30"},
    "sol": '''<p><b>What is being tested.</b> Whether you know which conservation law belongs to which part of the motion. The embedding is a collision: momentum survives it and kinetic energy does not. The slide afterwards is friction doing work: energy is the right tool there and momentum is not. The question cannot be done with one law alone.</p>
<p><b>Step 1 — what carries across the embedding.</b> The bullet embeds in a time so short that friction has no chance to change anything. Momentum is therefore conserved through the collision, and the bullet and block move off together as one object of mass <code>m + M</code>.</p>
<p><b>Step 2 — write the momentum balance.</b> Before, only the bullet moves; after, both move at a common speed <code>V</code>:</p>
<div class="formula">m u = (m + M) V</div>
<p><b>Step 3 — the common speed.</b> With <code>m</code> = 20 g, <code>u</code> = 300 m s<sup>-1</sup> and <code>M</code> = 1980 g, so that <code>m + M</code> = 2000 g. The grams cancel in the ratio, so the speed needs no unit conversion at all:</p>
<div class="formula">V = m u / (m + M) = (20 &#215; 300) / 2000 = 6000 / 2000 = 3.0 m s<sup>-1</sup></div>
<p>A drop from 300 m s<sup>-1</sup> to 3.0 m s<sup>-1</sup> looks violent, and it is: this is where nearly all the energy goes.</p>
<p><b>Step 4 — the kinetic energy just after the collision.</b> Energy needs SI units, so the combined mass becomes 2000 g = 2.00 kg at this point. This is the energy that friction now has to remove:</p>
<div class="formula">KE = ½ (m + M) V<sup>2</sup> = ½ &#215; 2.00 &#215; (3.0)<sup>2</sup> = 9.0 J</div>
<p><b>Step 5 — the friction force.</b> The block slides on level ground, so the normal reaction equals the total weight and the friction force is</p>
<div class="formula">F = &#956; (m + M) g = &#956; &#215; 2.00 &#215; 10 = 20&#956; N</div>
<p><b>Step 6 — the work friction does over the slide.</b> Friction opposes the motion, so it removes energy, and over the distance <code>d</code> = 1.5 m:</p>
<div class="formula">work = F d = 20&#956; &#215; 1.5 = 30&#956; J</div>
<p><b>Step 7 — equate and solve.</b> All the kinetic energy has gone by the time the block stops:</p>
<div class="formula">30&#956; = 9.0  &#8658;  &#956; = 9.0 / 30 = 0.30</div>
<p>So <b>Answer: A, 0.30.</b></p>
<p><b>Step 8 — check the energy bookkeeping across the whole event.</b> Back in kilograms, the bullet's original kinetic energy was</p>
<div class="formula">KE_before = ½ m u<sup>2</sup> = ½ &#215; 0.020 &#215; (300)<sup>2</sup> = 900 J</div>
<p>and only 9.0 J came out of the collision. So 891 J, or 99% of it, went into deforming the block and heating it. That is characteristic of an embedding: the fraction of kinetic energy that survives is <code>m/(m + M)</code>, here 0.020/2.00 = 1/100. Whenever a light fast object hits a heavy slow one and sticks, expect almost all the energy to be lost, and expect the common speed to be tiny compared with the incoming speed.</p>
<p><b>Step 9 — check the dimensions.</b> The numerator is a kinetic energy, in kg m<sup>2</sup> s<sup>-2</sup>; the denominator is a force times a distance, which is also kg m<sup>2</sup> s<sup>-2</sup>. The quotient is a pure number, which is what a coefficient of friction has to be. Had the result come out with units, something would have been added that should have been multiplied.</p>
<p><b>Step 10 — check the sense.</b> A rougher surface must stop the block sooner. Rearranging the same equation gives <code>d = V<sup>2</sup>/(2&#956;g)</code>, in which <code>d</code> falls as <code>&#956;</code> rises. So a coefficient of 0.60 would give a slide of 0.75 m, and 0.15 would give 3.0 m. That one line settles the direction of every wrong option that changes <code>&#956;</code>, and it is worth doing before looking at the list.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>0.60</b> comes from taking the kinetic energy as <code>(m + M)V<sup>2</sup></code> without the one half, which doubles everything downstream. It is the commonest slip in this whole family of questions.</p>
<p>&middot; <b>0.20</b> comes from using <code>V</code> in place of <code>V<sup>2</sup></code>: dividing 3.0 by 10 and by 1.5 gives 0.20. The speed has to be squared, because kinetic energy goes as the square.</p>
<p>&middot; <b>0.15</b> comes from using 3.0 m for the slide, twice the distance given, which halves the coefficient. The slide is 1.5 m.</p>
<p>&middot; <b>0.45</b> comes from using 1.0 m for the slide, which raises the coefficient by half. Both this and 0.15 come from misreading <code>d</code> rather than from any error in the physics, which is why the question states it in the first line of the stem.</p>
<p><b>The trap.</b> Applying energy conservation across the collision. It is the obvious move &#8212; energy is conserved in so many problems that it feels safe &#8212; and here it is simply false. If the collision were treated as elastic the block would leave at almost 300 m s<sup>-1</sup>, the slide would be kilometres long and no option would be close. The signature of an embedding is that momentum is the only thing that survives it.</p>
<p><b>Relevant topics:</b> conservation of momentum in a perfectly inelastic collision; the fraction of kinetic energy lost; work done by friction; the normal reaction on level ground; checking dimensions and direction as a habit.</p>''',
    "trap": "Using conservation of energy across the embedding. The collision is perfectly inelastic and loses 99% of the kinetic energy; only momentum carries across it, and energy takes over from the moment the block starts to slide.",
},


# ═════════════════════════════════════════════════════════════════════════════
# 14 — I, capacitors.  Charge is conserved when the plates are isolated.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 14, "id": "S02-14", "module": "I", "diff": 3,
    "topic": "The fraction of stored energy lost when a charged capacitor is joined to an uncharged one",
    "rel": [("I", "Charge is conserved when isolated plates are joined, but energy is not"),
            ("I", "Capacitors in parallel share a common potential difference and their capacitances add"),
            ("I", "The energy stored in a capacitor, and why the loss does not depend on the wire")],
    "key": ["capacitor", "charge", "energy"],
    "stem": '''<p>A capacitor of capacitance <code>C</code> is charged to a potential difference <code>V</code> and then disconnected from the supply. It is connected across an uncharged capacitor of capacitance <code>2C</code>. {{FIG:s02-14}}</p>
<p>What fraction of the energy originally stored is dissipated in the connecting wires?</p>''',
    "opts": ["<code>0</code>", "<code>1/4</code>", "<code>1/3</code>", "<code>1/2</code>",
             "<code>2/3</code>"],
    "ans": 4,
    "distractors": [
        "conserves energy as well as charge, which would leave the potential difference unchanged",
        "uses half the original potential difference by treating the second capacitor as having the same capacitance as the first",
        "reports the fraction of the energy that remains rather than the fraction lost",
        "assumes a fixed half of the stored energy is always lost whenever two capacitors are joined",
        "correct",
    ],
    "profile": {
        "steps": [
            ("relate", "identify what is conserved: the supply is removed, so the plates are isolated and the total charge cannot change"),
            ("relate", "after joining, the two capacitors are in parallel and therefore share one potential difference"),
            ("eliminate", "add the capacitances and divide the conserved charge by the total capacitance to get the new potential difference"),
            ("relate", "write the energy stored before joining in terms of the original charge and capacitance"),
            ("solve", "write the energy stored afterwards and take the ratio to the original"),
            ("check", "confirm the fraction lost lies between zero and one, and that the potential difference has fallen"),
        ],
        "relations": ["Q = C V", "Q_after = Q_before", "C_total = C + 2C = 3C",
                      "V_new = Q/(3C)", "E = Q^2/(2C)"],
        "insight": "Removing the supply is what makes the problem solvable: it converts charge into the conserved quantity. Once charge is fixed, the potential difference must fall when the capacitance rises, and it is that fall which costs the energy.",
        "shape": "conservation",
        "approx": False,
        "symbolic": True,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "1 - (3*(1/3)**2)", "want": "2/3"},
    "sol": '''<p><b>What is being tested.</b> Whether you can identify which quantity is conserved before doing any algebra. Charge is conserved here and energy is not, and that single decision fixes the whole solution.</p>
<p><b>Step 1 — what is conserved.</b> The supply has been removed before the connection is made, so the plates are isolated. No charge can leave them and none can arrive: the total charge is fixed.</p>
<div class="formula">Q = C V</div>
<p>Energy is <i>not</i> conserved. When the connection is made, charge flows through the wire, which has resistance; the current heats the wire and radiates. The final state is therefore not the one that conserves energy, and any solution that assumes it is will be wrong.</p>
<p><b>Step 2 — what the connection does.</b> Joining the upper plates to each other and the lower plates to each other puts the two capacitors in parallel, so they must end at the same potential difference <code>V_new</code>, and the total charge is shared between them:</p>
<div class="formula">C_total = C + 2C = 3C</div>
<p><b>Step 3 — the new potential difference.</b> The same charge now sits on a larger capacitance:</p>
<div class="formula">V_new = Q/C_total = CV/(3C) = V/3</div>
<p>The potential difference has fallen to a third. It had to fall: the same charge on three times the capacitance means one third of the potential difference.</p>
<p><b>Step 4 — the energy before.</b> Working in terms of <code>Q</code> and <code>C</code> avoids carrying the factor of a half through the ratio, but either form will do:</p>
<div class="formula">E_before = Q^2/(2C)</div>
<p><b>Step 5 — the energy after, and the fraction lost.</b></p>
<div class="formula">E_after = Q^2/(2 x 3C) = Q^2/(6C)
E_after/E_before = (1/6)/(1/2) = 1/3</div>
<p>One third of the energy remains, so two thirds has been dissipated:</p>
<div class="formula">fraction lost = 1 - 1/3 = 2/3</div>
<p>So <b>Answer: E</b>.</p>
<p><b>Step 6 — check it is sensible.</b> The fraction lost must lie between zero and one. It cannot be zero, because the potential difference fell and energy goes as the square of the potential difference. It cannot be one, because charge is still stored and the capacitors are still charged to <code>V/3</code>. Two thirds sits comfortably inside those bounds. A second check: the result does not contain the resistance of the wire. That is right — the wire only decides how <i>fast</i> the energy is lost, not how much. A thicker wire loses the same two thirds, just more quickly.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>0</b> conserves energy as well as charge. That would require the potential difference to be unchanged, which is impossible when the same charge now occupies three times the capacitance.</p>
<p>&middot; <b>1/4</b> comes from taking the new potential difference as <code>V/2</code>, which is what you get by treating the second capacitor as having capacitance <code>C</code> rather than <code>2C</code>. With <code>V_new = V/2</code> the final energy would be three eighths of the initial and the loss one quarter.</p>
<p>&middot; <b>1/3</b> is the fraction that <i>remains</i>. It is the ratio <code>E_after/E_before</code>, reported without the final subtraction.</p>
<p>&middot; <b>1/2</b> is the folk belief that exactly half the energy is always lost when capacitors are joined. It happens to be true for two equal capacitors, and it is the reason the belief exists — but here the capacitances are in the ratio one to two, so it does not apply.</p>
<p><b>The trap.</b> Assuming that energy is conserved because the problem says nothing about friction or resistance. Something always dissipates the difference when isolated conductors at different potentials are joined, and the amount does not depend on what that something is. The energy is genuinely gone from the circuit, and the only way to find the answer is to conserve the quantity that <i>is</i> conserved.</p>
<p><b>Relevant topics:</b> capacitance and charge; capacitors in parallel; energy stored in a capacitor; conservation of charge in an isolated system.</p>''',
    "trap": "Conserving energy as well as charge. When isolated plates at different potentials are joined, charge is conserved but the potential difference must fall, and the difference in energy is always dissipated.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 15 — M, fluids.  Floating: the submerged fraction is the density ratio.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 15, "id": "S02-15", "module": "M", "diff": 3,
    "topic": "Density of a liquid from the submerged fractions of a floating block",
    "rel": [("M", "A floating body displaces its own weight of fluid, which is Archimedes' principle"),
            ("M", "The submerged fraction of the volume equals the ratio of the two densities"),
            ("M", "Why the block's volume and the gravitational field strength both cancel")],
    "key": ["floating", "density", "upthrust"],
    "stem": '''<p>A solid block floats in water of density <code>1000 kg m<sup>-3</sup></code> with three quarters of its volume below the surface. The same block floats in an unknown liquid with half of its volume below the surface.</p>
<p>What is the density of the unknown liquid?</p>''',
    "opts": ["<code>500 kg m<sup>-3</sup></code>", "<code>750 kg m<sup>-3</sup></code>",
             "<code>1000 kg m<sup>-3</sup></code>", "<code>1500 kg m<sup>-3</sup></code>",
             "<code>2000 kg m<sup>-3</sup></code>"],
    "ans": 3,
    "distractors": [
        "takes the submerged fraction in the unknown liquid as the density itself",
        "reports the density of the block, which the water alone determines",
        "assumes the unknown liquid has the same density as water because the block still floats",
        "correct",
        "inverts the ratio, multiplying by the submerged fraction instead of dividing by it",
    ],
    "profile": {
        "steps": [
            ("relate", "a floating body is in equilibrium, so the upthrust equals its weight"),
            ("relate", "write the upthrust as the weight of the displaced liquid, and the weight as the weight of the whole block"),
            ("eliminate", "cancel the block's volume and the gravitational field strength, leaving the submerged fraction equal to the density ratio"),
            ("relate", "use the water case to find the density of the block"),
            ("solve", "use the unknown-liquid case to find the density of the liquid"),
            ("check", "confirm the denser liquid submerges the block less, as the two fractions say it does"),
        ],
        "relations": ["upthrust = weight", "rho_L V_sub g = rho_b V g",
                      "V_sub/V = rho_b/rho_L", "3/4 = rho_b/1000"],
        "insight": "The block floats in both liquids, so its weight is the same in each. That fixes the upthrust, and the upthrust fixes how much liquid must be pushed aside. A denser liquid needs to be pushed aside in smaller quantity.",
        "shape": "ratio-cancellation",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1000*(3/4)/(1/2)", "want": "1500"},
    "sol": '''<p><b>What is being tested.</b> Whether you can set up the floating condition once and then reuse it, instead of treating the two liquids as two separate problems. The block does not change, and that is the thread that joins the two cases.</p>
<p><b>Step 1 — the floating condition.</b> The block is in equilibrium, so the upward force from the liquid exactly balances its weight:</p>
<div class="formula">upthrust = weight of the block</div>
<p><b>Step 2 — write both sides in full.</b> The upthrust is the weight of the liquid pushed aside, and the weight of the block is the weight of its whole volume:</p>
<div class="formula">rho_L V_sub g = rho_b V g</div>
<p>Here <code>V_sub</code> is the submerged volume, <code>V</code> is the block's total volume, <code>rho_L</code> is the density of the liquid and <code>rho_b</code> that of the block.</p>
<p><b>Step 3 — cancel.</b> The gravitational field strength appears on both sides and goes. The volume of the block also appears on both sides, so only the <i>fraction</i> of it that is submerged survives:</p>
<div class="formula">V_sub/V = rho_b/rho_L</div>
<p>This is the whole physics of the problem in one line, and it is worth reading in words: <b>the submerged fraction equals the ratio of the two densities</b>. Nothing else matters — not the shape of the block, not its size, not the value of <code>g</code>.</p>
<p><b>Step 4 — find the density of the block from the water.</b> With three quarters submerged in water:</p>
<div class="formula">3/4 = rho_b/1000
rho_b = 750 kg m^-3</div>
<p><b>Step 5 — find the density of the unknown liquid.</b> The block is the same, so <code>rho_b</code> is still <code>750</code>. Now half the volume is submerged:</p>
<div class="formula">1/2 = 750/rho_L
rho_L = 750/(1/2) = 1500 kg m^-3</div>
<p>So <b>Answer: D</b>.</p>
<p><b>Step 6 — check the direction.</b> The unknown liquid is denser than water, so it should hold the block higher, and it does: half submerged against three quarters. If the answer had come out below <code>1000</code> the block would have had to sink deeper, contradicting the given fraction. That direction check costs nothing and catches the inversion error immediately.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>500 kg m<sup>-3</sup></b> takes the submerged fraction, one half, and reads it directly as a density in hundreds. The fraction is a pure number and carries no units of its own.</p>
<p>&middot; <b>750 kg m<sup>-3</sup></b> is the density of the block. It is the right number at the wrong stage: the water gives it, and the question asks about the liquid.</p>
<p>&middot; <b>1000 kg m<sup>-3</sup></b> assumes that because the block still floats the liquid must be water. It floats in both, but at different depths, and that difference is the entire information content of the second sentence.</p>
<p>&middot; <b>2000 kg m<sup>-3</sup></b> inverts the ratio: <code>750/(3/4)</code> instead of <code>750/(1/2)</code>, which puts the denser liquid on the wrong side of the comparison.</p>
<p><b>The trap.</b> Treating the two floats as unrelated. The temptation is to write the floating condition twice from scratch, and in doing so to introduce a second unknown. The block's density is common to both cases, so the first case is not a separate question — it is the step that supplies the number the second case needs.</p>
<p><b>Relevant topics:</b> Archimedes' principle; the floating condition; density and relative density; cancelling common factors in a physical relation.</p>''',
    "trap": "Treating the submerged fraction as a density. It is a pure number, and it equals the ratio of the block's density to the liquid's — so the liquid's density is found by dividing, not by reading the fraction off.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 16 — F, waves.  The lowest frequency at which a point is a minimum.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 16, "id": "S02-16", "module": "F", "diff": 3,
    "topic": "Two-source interference: the lowest frequency for which a given point is a minimum",
    "rel": [("F", "The wave equation, and the wavelength it gives at a stated frequency"),
            ("F", "Constructive and destructive interference in terms of the path difference"),
            ("A", "Choosing the extremal member of a family, and checking it really is the extremal one")],
    "key": ["interference", "pathdiff", "wave"],
    "stem": '''<p>Two loudspeakers <code>S1</code> and <code>S2</code> are driven by the same oscillator and therefore emit sound in phase. The speed of sound in air is <code>340 m s<sup>-1</sup></code>. A microphone at the point <code>P</code> is <code>2.5 m</code> from <code>S1</code> and <code>3.5 m</code> from <code>S2</code>. {{FIG:s02-16}}</p>
<p>What is the <b>lowest</b> frequency at which the sound heard at <code>P</code> is a minimum?</p>''',
    "opts": ["<code>85 Hz</code>", "<code>170 Hz</code>", "<code>340 Hz</code>",
             "<code>510 Hz</code>", "<code>680 Hz</code>"],
    "ans": 1,
    "distractors": [
        "takes the destructive condition as a quarter of a wavelength rather than an odd number of half-wavelengths",
        "correct",
        "uses the constructive condition, so the point would be a maximum instead of a minimum",
        "is a minimum, but not the lowest one: it is the second member of the family",
        "is a maximum, because the path difference is exactly two wavelengths",
    ],
    "profile": {
        "steps": [
            ("relate", "write the path difference as the difference of the two stated distances"),
            ("relate", "state the destructive condition: an odd number of half-wavelengths"),
            ("eliminate", "recognise that the longest wavelength satisfying the condition is the one with the smallest odd number of halves"),
            ("solve", "turn that wavelength into a frequency using the wave equation"),
            ("solve", "confirm the frequency is the lowest by showing the next member of the family is higher"),
            ("check", "verify that at the chosen frequency the path difference is exactly half a wavelength"),
        ],
        "relations": ["path difference = 3.5 - 2.5", "delta = (n + 1/2) lambda",
                      "lambda = 2 delta", "f = v/lambda"],
        "insight": "The lowest frequency means the longest wavelength, and the longest wavelength that still gives a minimum is the one with the smallest odd number of half-wavelengths. Choosing the extremal member of the family is the whole question; the arithmetic afterwards is trivial.",
        "shape": "superposition",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "340/(2*(3.5 - 2.5))", "want": "170"},
    "sol": '''<p><b>What is being tested.</b> Whether you can handle a whole family of answers and pick the right member of it. Any number of frequencies make <code>P</code> a minimum; the question asks for the lowest, and that is a separate decision from the physics.</p>
<p><b>Step 1 — the path difference.</b> The two waves travel different distances to reach <code>P</code>, and only the difference matters:</p>
<div class="formula">delta = 3.5 - 2.5 = 1.0 m</div>
<p>The two distances themselves are never used again. What matters is how much further one wave has travelled than the other.</p>
<p><b>Step 2 — the condition for a minimum.</b> A minimum needs the two waves to arrive in antiphase, which happens when one has travelled an odd number of half-wavelengths further than the other:</p>
<div class="formula">delta = (n + 1/2) lambda,  n = 0, 1, 2, ...</div>
<p>With a whole number of wavelengths the waves arrive in step and the point is a maximum. With an odd number of <i>half</i>-wavelengths they arrive exactly out of step.</p>
<p><b>Step 3 — the lowest frequency is the longest wavelength.</b> Since <code>f = v/lambda</code> at fixed <code>v</code>, asking for the lowest frequency is the same as asking for the longest wavelength. Rearranging the condition:</p>
<div class="formula">lambda = delta/(n + 1/2)</div>
<p>The right-hand side is largest when the denominator is smallest, and the smallest allowed denominator is <code>1/2</code>, at <code>n = 0</code>. So the longest wavelength that gives a minimum is</p>
<div class="formula">lambda = 1.0/(1/2) = 2.0 m</div>
<p><b>Step 4 — the frequency.</b></p>
<div class="formula">f = v/lambda = 340/2.0 = 170 Hz</div>
<p>So <b>Answer: B</b>.</p>
<p><b>Step 5 — confirm it is the lowest.</b> The next member of the family has <code>n = 1</code>, giving <code>lambda = 1.0/(3/2) = 0.67 m</code> and <code>f = 510 Hz</code>. Every later member is shorter still, so <code>170 Hz</code> is the lowest and there is nothing below it that works.</p>
<p><b>Step 6 — check against the condition.</b> At <code>170 Hz</code> the wavelength is <code>2.0 m</code> and the path difference is <code>1.0 m</code>, which is exactly <code>lambda/2</code>. That is the <code>n = 0</code> member of the family, and it does give a minimum. As a second check, at <code>85 Hz</code> the wavelength would be <code>4.0 m</code> and the path difference would be only <code>lambda/4</code> — not a minimum at all, which is why the answer cannot be below <code>170 Hz</code>.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>85 Hz</b> takes the minimum condition as a quarter of a wavelength. Half a wavelength is what puts two waves out of step, because a half-wavelength shift is a phase shift of <code>180&deg;</code>.</p>
<p>&middot; <b>340 Hz</b> uses the constructive condition: at this frequency the wavelength is <code>1.0 m</code>, exactly the path difference, so the two waves arrive in step and <code>P</code> is a maximum.</p>
<p>&middot; <b>510 Hz</b> is a genuine minimum — the wavelength is <code>0.67 m</code> and the path difference is one and a half wavelengths — but it is the <i>second</i> member of the family, not the lowest. This is the most dangerous option, because it satisfies the physics and fails only the word "lowest".</p>
<p>&middot; <b>680 Hz</b> gives a wavelength of <code>0.5 m</code>, so the path difference is two wavelengths and the point is again a maximum.</p>
<p><b>The trap.</b> Answering the physics and stopping. The condition <code>delta = (n + 1/2)lambda</code> has infinitely many solutions, and every one of them is a minimum. Reading the question as "find a frequency" rather than "find the lowest frequency" is what makes <code>510 Hz</code> look right. The extremal word in the question is doing as much work as the formula.</p>
<p><b>Relevant topics:</b> the wave equation; path difference; constructive and destructive superposition; selecting the extremal member of a family of solutions.</p>''',
    "trap": "Finding any frequency that gives a minimum rather than the lowest one. The condition has infinitely many solutions; the word 'lowest' selects the n = 0 member, which is the longest wavelength.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 17 — E, materials.  The Young modulus from the gradient of a force-extension graph.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 17, "id": "S02-17", "module": "E", "diff": 3,
    "topic": "The Young modulus from a force-extension graph and the dimensions of the wire",
    "rel": [("E", "Stress as force per unit area and strain as extension per unit length"),
            ("E", "The Young modulus as stress divided by strain, and the gradient as stiffness"),
            ("A", "Rearranging a quotient of quotients, and keeping the units consistent")],
    "key": ["youngmod", "stress", "gradient"],
    "stem": '''<p>The graph shows how the extension of a wire varies with the applied force, up to the limit of proportionality. The wire has an unstretched length of <code>2.0 m</code> and a cross-sectional area of <code>1.0 x 10<sup>-7</sup> m<sup>2</sup></code>. {{FIG:s02-17}}</p>
<p>What is the Young modulus of the material of the wire?</p>''',
    "opts": ["<code>1.0 x 10<sup>11</sup> Pa</code>", "<code>2.0 x 10<sup>11</sup> Pa</code>",
             "<code>4.0 x 10<sup>11</sup> Pa</code>", "<code>8.0 x 10<sup>11</sup> Pa</code>",
             "<code>1.6 x 10<sup>12</sup> Pa</code>"],
    "ans": 2,
    "distractors": [
        "takes the strain as the extension multiplied by the length instead of divided by it",
        "takes the strain as the extension itself, so the length of the wire never enters",
        "correct",
        "uses a length of 1.0 m instead of 2.0 m, which doubles the strain and so halves the modulus",
        "uses a length of 0.5 m, which halves the strain and so doubles the modulus again",
    ],
    "profile": {
        "steps": [
            ("relate", "read the gradient of the straight line as the stiffness, in newtons per metre"),
            ("relate", "write the stress as the force divided by the cross-sectional area"),
            ("relate", "write the strain as the extension divided by the unstretched length"),
            ("eliminate", "divide stress by strain and collect the terms to get modulus = (F/x) times (L/A)"),
            ("solve", "substitute the gradient, the length and the area"),
            ("check", "confirm the units reduce to pascals and that the magnitude is typical of a metal"),
        ],
        "relations": ["k = F/x", "stress = F/A", "strain = x/L", "E = stress/strain",
                      "E = (F/x)(L/A)"],
        "insight": "The gradient of the graph gives stiffness, and stiffness is the only thing the graph can give. Turning stiffness into the Young modulus needs the length and the area as well, and the direction of the length is the thing to get right: the modulus is stiffness times length divided by area.",
        "shape": "graph-reading",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "(40/(2.0*10**-3)) * (2.0/(1.0*10**-7))", "want": "4.0e11"},
    "sol": '''<p><b>What is being tested.</b> Whether you can move between the three quantities that all describe the same wire — stiffness, stress and strain — and the Young modulus, which is the only one of them that belongs to the <i>material</i> rather than to the particular wire.</p>
<p><b>Step 1 — read the gradient.</b> The graph is a straight line through the origin, so the wire obeys Hooke's law over the range shown. The gradient is the stiffness:</p>
<div class="formula">k = F/x = 40/(2.0 x 10^-3) = 2.0 x 10^4 N m^-1</div>
<p>The extension must be converted to metres here. Dividing 40 by 2.0 without converting would give a stiffness a thousand times too large, and that error survives all the way to the final answer.</p>
<p><b>Step 2 — stress.</b> Stress is the force per unit area of cross-section:</p>
<div class="formula">stress = F/A = 40/(1.0 x 10^-7) = 4.0 x 10^8 Pa</div>
<p><b>Step 3 — strain.</b> Strain is the fractional extension, and it is a ratio of two lengths, so it has no units:</p>
<div class="formula">strain = x/L = (2.0 x 10^-3)/2.0 = 1.0 x 10^-3</div>
<p><b>Step 4 — the Young modulus.</b></p>
<div class="formula">E = stress/strain = (4.0 x 10^8)/(1.0 x 10^-3) = 4.0 x 10^11 Pa</div>
<p>So <b>Answer: C</b>.</p>
<p>It is worth seeing the same calculation in one line, because the single line is where the direction of <code>L</code> becomes visible:</p>
<div class="formula">E = (F/A)(L/x) = (F/x)(L/A) = 2.0 x 10^4 x (2.0/(1.0 x 10^-7)) = 4.0 x 10^11 Pa</div>
<p><b>Step 6 — check the units and the magnitude.</b> The units of <code>(F/x)(L/A)</code> are <code>(N m<sup>-1</sup>)(m/m<sup>2</sup>) = N m<sup>-2</sup></code>, which is the pascal. So the arithmetic cannot be out by a unit. And <code>4.0 x 10<sup>11</sup> Pa</code> is <code>400 GPa</code>, which is the right order for a metal — steel is around <code>200 GPa</code> and this material is stiffer, which is unremarkable. An answer of <code>4.0 x 10<sup>8</sup></code> or <code>4.0 x 10<sup>14</sup></code> would have to be wrong on sight.</p>
<p><b>The distractors.</b> All four are the correct formula with one quantity misplaced, which is why they are close enough to be tempting.</p>
<p>&middot; <b>1.0 x 10<sup>11</sup> Pa</b> takes the strain as <code>xL</code>, multiplying by the length instead of dividing. The strain is a <i>fraction</i>, so it must be smaller than the extension, not larger.</p>
<p>&middot; <b>2.0 x 10<sup>11</sup> Pa</b> takes the strain as <code>x</code> alone. The length of the wire then never enters the calculation, which cannot be right: two wires of the same material and area but different lengths stretch by different amounts under the same force.</p>
<p>&middot; <b>8.0 x 10<sup>11</sup> Pa</b> uses a length of <code>1.0 m</code> rather than <code>2.0 m</code>, so the strain comes out twice as large and the modulus twice as small.</p>
<p>&middot; <b>1.6 x 10<sup>12</sup> Pa</b> uses <code>0.5 m</code>, which halves the strain and doubles the modulus relative to the correct value.</p>
<p><b>The trap.</b> Reading the gradient and stopping. The gradient gives the stiffness of <i>this wire</i>; the Young modulus is a property of <i>the material</i>, and the two are related only through the length and the area. A second wire of the same material, twice as long and with the same area, would have half the stiffness and exactly the same Young modulus — which is the clearest statement of why the extra step is needed.</p>
<p><b>Relevant topics:</b> Hooke's law and the force-extension graph; stress, strain and the Young modulus; the gradient of a straight-line graph; unit consistency in a compound formula.</p>''',
    "trap": "Reporting the gradient as the answer. The gradient is the stiffness of this wire, which depends on its length and area; the Young modulus is a property of the material alone.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 18 — L, quantum.  How the photon rate depends on power and wavelength.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 18, "id": "S02-18", "module": "L", "diff": 2,
    "topic": "How the number of photons emitted per second depends on power and wavelength",
    "rel": [("L", "The energy of a single photon is inversely proportional to its wavelength"),
            ("L", "The photon rate is the beam power divided by the energy of one photon"),
            ("A", "Combining two changes to a product by multiplying their separate factors")],
    "key": ["photon", "power", "rate"],
    "stem": '''<p>A laser emits monochromatic light of wavelength <code>&lambda;</code> at a power <code>P</code>. The wavelength is then <b>halved</b> and the power is <b>doubled</b>.</p>
<p>By what factor does the number of photons emitted per second change?</p>''',
    "opts": ["<code>1/4</code>", "<code>1/2</code>", "<code>1</code>", "<code>2</code>",
             "<code>4</code>"],
    "ans": 2,
    "distractors": [
        "multiplies the two changes together instead of dividing one by the other",
        "applies only the change in wavelength and ignores the change in power",
        "correct",
        "applies only the change in power and ignores the change in wavelength",
        "adds the two factors rather than combining them",
    ],
    "profile": {
        "steps": [
            ("relate", "write the energy of one photon as hc divided by the wavelength"),
            ("relate", "write the number emitted per second as the beam power divided by the energy of one photon"),
            ("eliminate", "collect the result to show that the rate is proportional to the product of the power and the wavelength"),
            ("solve", "apply the two changes separately: doubling the power doubles the rate, halving the wavelength halves it"),
            ("check", "combine the two factors and confirm they cancel exactly"),
        ],
        "relations": ["E = hc/lambda", "N = P/E", "N = P lambda/(hc)",
                      "N proportional to P lambda"],
        "insight": "The photon rate is a product of the power and the wavelength, so the two changes act in opposite directions. Neither change alone gives the answer, and the question is designed so that each one alone is one of the wrong options.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "(2*P*L/2)/(P*L)", "want": "1"},
    "sol": '''<p><b>What is being tested.</b> Whether you can reduce a physical situation to a proportionality before putting any numbers in. No value of the power, the wavelength or Planck's constant is needed, and none is given.</p>
<p><b>Step 1 — the energy of one photon.</b></p>
<div class="formula">E = hc/lambda</div>
<p>A shorter wavelength means a more energetic photon. Halving the wavelength therefore <i>doubles</i> the energy each photon carries.</p>
<p><b>Step 2 — the number of photons per second.</b> A beam of power <code>P</code> delivers <code>P</code> joules each second, and each photon takes <code>E</code> of those joules:</p>
<div class="formula">N = P/E = P lambda/(hc)</div>
<p><b>Step 3 — the proportionality.</b> The constants <code>h</code> and <code>c</code> do not change, so they can be dropped when only a ratio is wanted:</p>
<div class="formula">N proportional to P lambda</div>
<p>This is the whole question in one line. The photon rate is proportional to the <i>product</i> of the power and the wavelength — not to either one alone.</p>
<p><b>Step 4 — apply the two changes.</b> Doubling <code>P</code> doubles <code>N</code>. Halving <code>&lambda;</code> halves <code>N</code>, because a more energetic photon means fewer of them are needed to carry the same energy.</p>
<p><b>Step 5 — combine.</b></p>
<div class="formula">factor = 2 x (1/2) = 1</div>
<p>The two changes cancel exactly, and the photon rate is unchanged. So <b>Answer: C</b>.</p>
<p>It is worth seeing the cancellation in one line, because it shows the answer does not depend on either number:</p>
<div class="formula">N_new/N_old = (2P)(lambda/2)/(P lambda) = 1</div>
<p><b>The distractors.</b></p>
<p>&middot; <b>1/4</b> multiplies the two factors together as <code>2 x (1/2)</code> read as though both were divisions. The power change increases the rate and the wavelength change decreases it, so the factors act in opposite directions.</p>
<p>&middot; <b>1/2</b> applies only the wavelength change. It is the right reasoning with half the question missing.</p>
<p>&middot; <b>2</b> applies only the power change. Same omission, opposite half.</p>
<p>&middot; <b>4</b> adds the two factors instead of multiplying them: <code>2 + 2</code>, treating the halving as another doubling.</p>
<p><b>The trap.</b> Handling the two changes one at a time and then reporting the first one. The question states two changes, and both have to be carried through. The safe habit is to write the proportionality down before touching the factors: once <code>N proportional to P&lambda;</code> is on the page, the cancellation is mechanical and the partial answers stop being tempting.</p>
<p><b>Relevant topics:</b> photon energy; the wave equation applied to light; power as energy per unit time; proportionality and the combination of factors.</p>''',
    "trap": "Applying only one of the two changes. The photon rate is proportional to the power times the wavelength, so both changes act, and here they cancel exactly.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 19 — A, toolkit.  The first-order behaviour of a series combination.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 19, "id": "S02-19", "module": "A", "diff": 3,
    "topic": "The first-order approximation to a series combination when one term dominates",
    "rel": [("A", "Expanding a quotient by dividing top and bottom by the dominant quantity"),
            ("A", "Using the small-parameter result (1 + x)^n approximately 1 + nx from the data sheet"),
            ("E", "The stiffness of two springs joined end to end, and why it is less than either")],
    "key": ["smallparam", "series", "approximation"],
    "stem": '''<p>Two springs of stiffness <code>k</code> and <code>K</code> are joined end to end, so that the pair is stretched by pulling on the two free ends. The combined stiffness is</p>
<div class="formula">k_combined = kK/(k + K)</div>
<p>In the case where <code>K</code> is very much larger than <code>k</code>, which expression is correct <b>to first order</b> in the small ratio <code>k/K</code>?</p>''',
    "opts": ["<code>k(1 - k/K)</code>", "<code>k(1 + k/K)</code>", "<code>k(1 - K/k)</code>",
             "<code>K(1 - k/K)</code>", "<code>k</code>"],
    "ans": 0,
    "distractors": [
        "correct",
        "gets the sign of the correction wrong, making the combination stiffer than the softer spring",
        "inverts the small ratio, so the correction is not small at all",
        "keeps the stiffer spring as the leading term, which contradicts the limit the question states",
        "gives only the leading term and drops the correction the question asks for",
    ],
    "profile": {
        "steps": [
            ("relate", "notice that when one stiffness greatly exceeds the other, the combination is dominated by the softer one"),
            ("eliminate", "divide numerator and denominator of the combination by the larger stiffness to expose the small ratio"),
            ("relate", "recognise the resulting form as one over a quantity close to one"),
            ("solve", "expand that form with the small-parameter result supplied on the data sheet"),
            ("check", "take the limit of the larger stiffness going to infinity and confirm the expression reduces to the softer stiffness exactly"),
        ],
        "relations": ["k_combined = kK/(k + K)", "divide by K", "(k/K)/(1 + k/K)",
                      "(1 + x)^-1 = 1 - x + ..."],
        "insight": "Dividing top and bottom by the LARGE stiffness is what turns the expression into the standard small-parameter form. Dividing by the small one instead gives a ratio greater than one and the approximation has no meaning.",
        "shape": "limiting-case",
        "approx": True,
        "symbolic": True,
        "figure_essential": False,
    },
    "check": {"kind": "sym", "got": "k*(1 - k/K)", "want": "k - k**2/K"},
    "sol": '''<p><b>What is being tested.</b> Whether you can turn an expression into the standard small-parameter form, and then use the expansion the data sheet provides. Both halves are needed: the data sheet gives <code>(1 + x)<sup>n</sup> &asymp; 1 + nx</code>, but it does not tell you what <code>x</code> is.</p>
<p><b>Step 1 — what the limit should look like.</b> Before any algebra, ask what the physics demands. Two springs end to end are always <i>softer</i> than either one alone, because each contributes its own stretch. If one spring is very stiff and the other is soft, the stiff one barely stretches at all, so the pair behaves like the soft one alone — but still a little softer. So the answer must start with <code>k</code> and be slightly less than it.</p>
<p><b>Step 2 — divide by the large quantity.</b> This is the step that decides the question. Dividing numerator and denominator by <code>K</code>:</p>
<div class="formula">k_combined = kK/(k + K) = k/(1 + k/K)</div>
<p>Dividing by <code>k</code> instead would give <code>K/(1 + K/k)</code>, in which the small parameter appears upside down as a large one, and the expansion would be useless.</p>
<p><b>Step 3 — recognise the form.</b> The result is <code>k</code> multiplied by <code>(1 + x)<sup>-1</sup></code> with <code>x = k/K</code>, which is small by the statement of the question.</p>
<p><b>Step 4 — expand.</b> The data sheet supplies the result for a small parameter, with <code>n = -1</code>:</p>
<div class="formula">(1 + x)^n = 1 + nx
(1 + k/K)^-1 = 1 - k/K</div>
<p>So</p>
<div class="formula">k_combined = k(1 - k/K) = k - k^2/K</div>
<p>So <b>Answer: A</b>.</p>
<p><b>Step 5 — check the limits.</b> Let <code>K</code> grow without bound. The correction term <code>k<sup>2</sup>/K</code> goes to zero and the expression reduces to exactly <code>k</code>, which is the physically required answer and confirms the leading term. Now let <code>K</code> fall towards <code>k</code>: the correction is then of order one, the expansion is no longer valid, and the answer correctly becomes unreliable — as it should, since the approximation was only ever claimed for small <code>k/K</code>. Two limits, both correct, and neither needed any arithmetic beyond reading the expression.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>k(1 + k/K)</b> gets the sign of the correction wrong, making the combination <i>stiffer</i> than the softer spring. Step 1 rules this out on physical grounds without any algebra: joining springs end to end cannot stiffen the pair.</p>
<p>&middot; <b>k(1 - K/k)</b> inverts the small ratio. The correction is then huge, and the expression is not an approximation at all.</p>
<p>&middot; <b>K(1 - k/K)</b> keeps the stiffer spring as the leading term. It reduces to <code>K</code> in the limit, which would mean the very stiff spring is doing all the stretching.</p>
<p>&middot; <b>k</b> gives the leading term only. It is the correct limit, and it is not what the question asks for: "to first order" means the leading term <i>plus</i> the first correction.</p>
<p><b>The trap.</b> Expanding in the wrong variable. The small parameter has to be the ratio of the smaller quantity to the larger one, and which of the two you divide by decides whether the small parameter even appears. A useful habit is to write down what the small parameter is going to be <i>before</i> starting the algebra — here <code>k/K</code>, because the question says so — and then to divide by whatever makes it appear.</p>
<p><b>Relevant topics:</b> the small-parameter approximations supplied on the data sheet; combining springs in series; reducing an expression to standard form by dividing through; checking an approximation against its limiting cases.</p>''',
    "trap": "Dividing by the smaller quantity, which puts the small parameter upside down and makes the expansion meaningless. Divide by the larger one so that the ratio is small.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 20 — G, optics.  Images in two plane mirrors, counted by the angular symmetry.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 20, "id": "S02-20", "module": "G", "diff": 3,
    "topic": "The number of images of a point object between two plane mirrors at an angle",
    "rel": [("G", "A plane mirror forms an image as far behind it as the object is in front"),
            ("G", "Each image is itself an object for the other mirror, so the reflections repeat"),
            ("A", "Counting the members of a symmetric family round a full turn, and excluding the object itself")],
    "key": ["mirror", "image", "symmetry"],
    "stem": '''<p>Two plane mirrors are arranged with their reflecting surfaces facing each other, meeting along a common vertical edge at an angle of <code>60&deg;</code>. A small illuminated bead is placed between them, well away from the edge.</p>
<p>How many images of the bead are formed?</p>''',
    "opts": ["<code>3</code>", "<code>4</code>", "<code>5</code>", "<code>6</code>",
             "<code>11</code>"],
    "ans": 2,
    "distractors": [
        "divides a straight angle by 60 degrees, treating the two mirrors as a single flat surface",
        "counts one fewer image than the geometry gives, by stopping the chain of reflections too early",
        "correct",
        "counts the object itself as one of the images in the ring",
        "doubles the count before subtracting, which is the rule for two separate parallel mirrors",
    ],
    "profile": {
        "steps": [
            ("relate", "each mirror forms an image of the bead at the mirror-image position behind that mirror"),
            ("relate", "each of those images acts as an object for the other mirror, so the reflections continue round the edge"),
            ("eliminate", "the chain closes when it has gone once round the edge, so the positions are spaced at the mirror angle round a full turn"),
            ("solve", "divide a full turn by the mirror angle to get the number of equally spaced positions"),
            ("solve", "remove the one position that is the bead itself, since it is not an image"),
            ("check", "confirm that the division is exact, so the ring closes with no half-formed image left over"),
        ],
        "relations": ["image distance = object distance", "n = 360/theta", "images = n - 1",
                      "360/60 = 6"],
        "insight": "The reflections do not stop after two bounces: every image is itself an object for the other mirror. The chain closes when it has gone once round the edge, which turns the problem into counting the members of a ring spaced at the mirror angle.",
        "shape": "symmetry",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "360/60 - 1", "want": "5"},
    "sol": '''<p><b>What is being tested.</b> Whether you realise that a plane mirror does not stop after one reflection. Each image is a perfectly good object as far as the other mirror is concerned, so the reflections go round and round until the geometry closes them off.</p>
<p><b>Step 1 — one mirror on its own.</b> A plane mirror forms an image as far behind the reflecting surface as the object is in front of it, on the perpendicular through the object. With one mirror the bead would have exactly one image.</p>
<p><b>Step 2 — the second mirror reflects the first image.</b> That image is now an object for the second mirror, which forms its own image of it. That second image is in turn an object for the first mirror, and so on. The chain does not stop after two steps.</p>
<p><b>Step 3 — what closes the chain.</b> The reflections are all mirror images in one of the two mirror planes, and the two planes meet along the edge at <code>60&deg;</code>. Reflecting repeatedly in two planes that meet at an angle is the same as rotating the original bead about the edge in steps of that angle. So the images and the bead itself lie at equal angular intervals all the way round the edge:</p>
<div class="formula">angular step = 60&deg;</div>
<p><b>Step 4 — how many positions are there?</b> A full turn contains</p>
<div class="formula">360/60 = 6</div>
<p>equal steps, so there are six positions in the ring.</p>
<p><b>Step 5 — remove the bead itself.</b> One of those six positions is the bead, not an image of it. The number of images is therefore</p>
<div class="formula">images = 6 - 1 = 5</div>
<p>So <b>Answer: C</b>.</p>
<p><b>Step 6 — check that the ring closes.</b> The division is exact: six steps of <code>60&deg;</code> come back to the start with nothing left over. That matters. If the angle had been, say, <code>50&deg;</code>, then <code>360/50 = 7.2</code>, the ring would not close, and one of the reflections would fall outside the region between the mirrors and not be seen at all. The question's <code>60&deg;</code> is chosen precisely so that this ambiguity does not arise, and a candidate who checks the division has confirmed that the simple count is the right one to use.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3</b> divides <code>180&deg;</code> by <code>60&deg;</code>. That would be right if the two mirrors formed a single flat surface — that is, if the angle between them were <code>180&deg;</code> rather than <code>60&deg;</code>.</p>
<p>&middot; <b>4</b> counts the reflections one short, as though the chain stopped after each mirror had been used twice.</p>
<p>&middot; <b>6</b> is <code>360/60</code> without the subtraction: the bead itself has been counted as one of its own images. There are six <i>positions</i> in the ring and five <i>images</i>.</p>
<p>&middot; <b>11</b> is <code>2 x 6 - 1</code>, the form that belongs to two separate parallel mirrors, where each mirror images the other's images independently. With the mirrors at an angle the two chains are not independent — they are the same chain.</p>
<p><b>The trap.</b> Assuming each mirror contributes exactly one image. The reflections multiply rather than add, because an image can be reflected again. The reliable way to think about it is to stop counting mirrors and start counting positions in the ring: the geometry of the wedge, not the number of mirrors, decides how many there are.</p>
<p><b>Relevant topics:</b> reflection at a plane surface; the position of an image in a plane mirror; multiple reflections between inclined mirrors; rotational symmetry about an axis.</p>''',
    "trap": "Counting one image per mirror. Each image is an object for the other mirror, so the reflections continue until the geometry closes the chain round the edge.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 21 — K, nuclear.  Counting the gamma energies a set of levels can produce.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 21, "id": "S02-21", "module": "K", "diff": 3,
    "topic": "The number of distinct gamma photon energies from a set of nuclear energy levels",
    "rel": [("K", "A gamma photon carries the energy difference between the two levels involved"),
            ("K", "A nucleus may drop straight to any lower level or by way of intermediate ones"),
            ("A", "Counting the pairs in a set without listing them, and checking they are distinct")],
    "key": ["gammalines", "levels", "counting"],
    "stem": '''<p>A nucleus has four energy levels, at <code>0</code>, <code>1.0</code>, <code>3.0</code> and <code>7.0 MeV</code> above the ground state. A nucleus in the <code>7.0 MeV</code> level can drop to any lower level, emitting one gamma photon of the corresponding energy. It may drop straight to a lower level or by way of one or more intermediate levels. {{FIG:s02-21}}</p>
<p>How many <b>different</b> gamma photon energies can be observed?</p>''',
    "opts": ["<code>3</code>", "<code>4</code>", "<code>5</code>", "<code>6</code>",
             "<code>12</code>"],
    "ans": 3,
    "distractors": [
        "counts only the transitions that start from the top level and ignores the rest",
        "counts only the transitions that end at the ground state",
        "counts the pairs but assumes two of the six differences happen to be equal",
        "correct",
        "counts every pair in both directions, as though a downward transition and an upward one were different",
    ],
    "profile": {
        "steps": [
            ("relate", "a gamma photon carries exactly the energy difference between the two levels involved"),
            ("relate", "the nucleus may drop directly to any lower level, or by way of intermediate levels, so every ordered pair of levels is available"),
            ("eliminate", "reduce the list of possibilities to the differences between every pair of levels"),
            ("solve", "count the pairs without listing them: three from the top level, two from the next, one from the next"),
            ("solve", "add those up to get the number of possible transitions"),
            ("check", "work out the six differences explicitly and confirm that no two of them coincide"),
        ],
        "relations": ["E_gamma = E_upper - E_lower", "pairs = 3 + 2 + 1",
                      "differences: 7, 6, 4, 3, 2, 1 MeV"],
        "insight": "A transition is available between any two levels, not only between neighbours, because the nucleus can always take an intermediate route. That turns the question into counting the pairs in a set of four things, which is six.",
        "shape": "combinatorial",
        "approx": False,
        "symbolic": False,
        "figure_essential": True,
    },
    "check": {"kind": "eval", "expr": "4*3/2", "want": "6"},
    "sol": '''<p><b>What is being tested.</b> Whether you see that a transition is possible between <i>any</i> two levels, not just between neighbours. Once that is clear the physics is over and the question becomes a counting one.</p>
<p><b>Step 1 — what a gamma photon carries.</b> When the nucleus drops from one level to another it loses energy, and that energy leaves as one photon:</p>
<div class="formula">E_gamma = E_upper - E_lower</div>
<p>So every observable photon energy is a difference between two of the four levels.</p>
<p><b>Step 2 — which pairs are available.</b> The nucleus in the <code>7.0 MeV</code> level has three possible destinations: <code>3.0</code>, <code>1.0</code> and <code>0</code>. If it goes to <code>3.0 MeV</code> it is then in the <code>3.0 MeV</code> level, from which it can go to <code>1.0</code> or to <code>0</code>. And from <code>1.0 MeV</code> it can go to <code>0</code>. So every pair of levels is reachable, directly or by stages.</p>
<p><b>Step 3 — the count.</b> Counting the destinations level by level:</p>
<div class="formula">from 7.0 MeV: 3 destinations
from 3.0 MeV: 2 destinations
from 1.0 MeV: 1 destination
total = 3 + 2 + 1 = 6</div>
<p>So <b>Answer: D</b>.</p>
<p><b>Step 4 — the six energies, written out.</b> This is the step that turns a count into an answer, because the question asks for different <i>energies</i>, not for different transitions:</p>
<div class="formula">7.0 - 0 = 7.0 MeV      7.0 - 1.0 = 6.0 MeV
7.0 - 3.0 = 4.0 MeV    3.0 - 0 = 3.0 MeV
3.0 - 1.0 = 2.0 MeV    1.0 - 0 = 1.0 MeV</div>
<p><b>Step 5 — check that no two coincide.</b> The six values are <code>1.0</code>, <code>2.0</code>, <code>3.0</code>, <code>4.0</code>, <code>6.0</code> and <code>7.0 MeV</code> — all different. So six transitions give six distinct photon energies, and the count of transitions and the count of energies agree. That agreement is not automatic, and the next paragraph is about why.</p>
<p><b>Step 6 — the point of the check.</b> Suppose the levels had been at <code>0</code>, <code>1.0</code>, <code>2.5</code> and <code>4.0 MeV</code>. There would still be six transitions, but two of them would both give <code>1.5 MeV</code>, so only five distinct photon energies would be observed. The number of <i>transitions</i> and the number of <i>energies</i> are different questions, and the question asked for energies. Working the six differences out is the only way to be sure they are distinct, and it costs one line.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>3</b> counts only the transitions leaving the top level, which is the first line of the count rather than the whole of it.</p>
<p>&middot; <b>4</b> counts only the transitions arriving at the ground state, one from each level. That is the other half of the same mistake: it counts by destination instead of by pair, and each way of counting on its own misses the others.</p>
<p>&middot; <b>5</b> is the count you get by assuming two of the six differences coincide. It is the right method with an unjustified subtraction — and the explicit list in Step 4 shows there is nothing to subtract.</p>
<p>&middot; <b>12</b> counts each pair in both directions, as though dropping from <code>7.0</code> to <code>1.0</code> and rising from <code>1.0</code> to <code>7.0</code> were two different emissions. A rising transition absorbs a photon; it does not emit one.</p>
<p><b>The trap.</b> Assuming the nucleus must cascade one level at a time. It does not — a single photon can carry away the whole difference between any two levels — and equally, it is not restricted to the four differences between neighbouring levels. Both the "only neighbours" picture and the "one per level" picture give four or fewer, and both are wrong.</p>
<p><b>Relevant topics:</b> nuclear energy levels; gamma emission; photon energy as a level difference; counting the pairs in a set.</p>''',
    "trap": "Counting only transitions between neighbouring levels. A single gamma photon can carry the difference between any two levels, so every pair contributes a possible energy.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 22 — B, kinematics.  How the separation of two falling balls varies.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 22, "id": "S02-22", "module": "B", "diff": 2,
    "topic": "How the separation of two balls released in succession changes while both fall",
    "rel": [("B", "Two bodies with the same acceleration have a constant relative velocity"),
            ("B", "The separation is the head start plus the relative speed times the elapsed time"),
            ("A", "Reasoning about how a quantity varies without evaluating it at every instant")],
    "key": ["freefall", "separation", "relative"],
    "stem": '''<p>Two identical steel balls are released from rest from the same height above the ground. The second is released a short time <code>&Delta;t</code> after the first. Air resistance is negligible.</p>
<p>While both balls are still falling, how does the distance between them change?</p>''',
    "opts": ["It stays constant, because both balls fall with the same acceleration.",
             "It increases at a constant rate.",
             "It increases at an increasing rate.",
             "It decreases at a constant rate.",
             "It decreases at an increasing rate."],
    "ans": 1,
    "distractors": [
        "confuses equal accelerations with equal speeds, when equal accelerations mean the SPEED DIFFERENCE is constant",
        "correct",
        "assumes the separation behaves like the distance each ball falls, which grows as the square of the time",
        "takes the second ball to be closing the gap, which would need it to be the faster of the two",
        "combines the closing direction with the accelerating shape, so both parts are wrong",
    ],
    "profile": {
        "steps": [
            ("relate", "both balls have the same downward acceleration, so their speeds differ by a fixed amount at every instant"),
            ("relate", "that fixed difference is the speed the first ball has already gained in the time between the releases"),
            ("eliminate", "a constant difference in speed means a constant rate of change of separation"),
            ("solve", "write the separation as the head start plus the relative speed multiplied by the elapsed time"),
            ("check", "confirm the expression gives the head start at the instant of the second release, and grows from there"),
        ],
        "relations": ["a = g for both", "v_rel = g delta_t", "separation = g delta_t t + (1/2) g delta_t^2"],
        "insight": "Equal accelerations cancel when you subtract one motion from the other, so what is left is a constant relative velocity. The separation therefore grows at a steady rate, not an accelerating one.",
        "shape": "monotonicity",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "10*0.5", "want": "5"},
    "sol": '''<p><b>What is being tested.</b> Whether you can reason about a difference of two motions rather than about each motion separately. Both balls are accelerating, and that is what makes the question feel harder than it is.</p>
<p><b>Step 1 — the speeds.</b> At any instant after the second ball is released, both balls have been falling for different lengths of time. With <code>t</code> measured from the release of the second ball:</p>
<div class="formula">v_1 = g(t + delta_t)      v_2 = g t</div>
<p>Both speeds are growing, and they are growing at the same rate.</p>
<p><b>Step 2 — subtract.</b> The difference between them does not grow at all:</p>
<div class="formula">v_1 - v_2 = g(t + delta_t) - g t = g delta_t</div>
<p>Every term in <code>t</code> has cancelled. The speed difference is fixed, and it equals the speed the first ball had already gained during the delay. This is the whole question: equal accelerations cancel in the difference.</p>
<p><b>Step 3 — what a constant speed difference means.</b> If the first ball is always moving <code>g&Delta;t</code> faster than the second, then the gap between them opens at that rate and at no other rate. The separation is therefore <i>increasing at a constant rate</i>.</p>
<p><b>Step 4 — write the separation down.</b> The first ball has been falling for <code>t + &Delta;t</code> and the second for <code>t</code>, so</p>
<div class="formula">separation = (1/2) g (t + delta_t)^2 - (1/2) g t^2
           = (1/2) g (2 t delta_t + delta_t^2)
           = g delta_t t + (1/2) g delta_t^2</div>
<p>The <code>t<sup>2</sup></code> terms have cancelled, leaving something linear in <code>t</code>. A linear function of time grows at a constant rate, which confirms Step 3 by a second route.</p>
<p><b>Step 5 — check the two limits.</b> At <code>t = 0</code>, the instant the second ball is released, the separation is <code>&frac12;g&Delta;t&sup2;</code> — the head start, and not zero. As <code>t</code> grows, the separation grows without limit at the steady rate <code>g&Delta;t</code>. Both of those are what the physical picture demands: the balls are already apart when the second is released, and they never come back together. So <b>Answer: B</b>.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>Constant separation</b> is the most common answer, and it comes from a real confusion: equal accelerations do not mean equal speeds. They mean the speeds stay <i>equally different</i>. The balls are at different points of the same journey, and the journey is getting longer for both of them at the same rate.</p>
<p>&middot; <b>Increasing at an increasing rate</b> transfers the shape of the distance fallen — which does grow as the square of the time — onto the separation. The squared terms cancel when the two motions are subtracted, so the separation is linear, not quadratic.</p>
<p>&middot; <b>Decreasing at a constant rate</b> has the second ball closing the gap. That would require the second ball to be the faster one, which cannot happen when it was released later and both accelerate identically.</p>
<p>&middot; <b>Decreasing at an increasing rate</b> gets both the direction and the shape wrong.</p>
<p><b>The trap.</b> Reasoning about one ball and then the other instead of about the difference. Each ball on its own is genuinely accelerating, and every statement you can make about either one is about a quantity that grows as the square of the time. The only way to see the linear behaviour is to subtract first and look at what survives.</p>
<p><b>Relevant topics:</b> free fall from rest; relative velocity; the difference between acceleration and velocity; combining two motions with the same acceleration.</p>''',
    "trap": "Assuming equal accelerations mean equal speeds. They mean the speed DIFFERENCE is constant, so the gap opens at a steady rate rather than accelerating.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 23 — M, fluids.  A U-tube: oil on one side, mercury displaced on both.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 23, "id": "S02-23", "module": "M", "diff": 3,
    "topic": "The displacement of mercury in a U-tube when an oil column is added to one arm",
    "rel": [("M", "Pressure at the same level in a continuous liquid is the same on both sides"),
            ("M", "The pressure added by a column of liquid is the density times the depth"),
            ("A", "Handling a level that moves down on one side and up on the other by the same amount")],
    "key": ["utube", "pressure", "column"],
    "stem": '''<p>A U-tube of uniform cross-section contains mercury of density <code>13600 kg m<sup>-3</sup></code>. Oil of density <code>850 kg m<sup>-3</sup></code> is then poured carefully into one arm until the column of oil is <code>16 cm</code> deep. The mercury in that arm falls, and the mercury in the other arm rises by the same amount.</p>
<p>By how far does the mercury level in the oil-filled arm fall?</p>''',
    "opts": ["<code>2.5 mm</code>", "<code>5.0 mm</code>", "<code>10 mm</code>",
             "<code>20 mm</code>", "<code>40 mm</code>"],
    "ans": 1,
    "distractors": [
        "halves the displacement a second time, applying the factor of two twice over",
        "correct",
        "uses the displacement itself as the difference in mercury levels, forgetting that the other arm moves too",
        "multiplies by two instead of dividing, so the difference in levels is taken as half the displacement",
        "has both the factor of two and the arithmetic the wrong way round",
    ],
    "profile": {
        "steps": [
            ("relate", "choose a level in the mercury and require the pressure to be the same on both sides of it"),
            ("relate", "the oil column adds a pressure equal to its density times its depth times the gravitational field strength"),
            ("relate", "the mercury surface falls in one arm and rises in the other, so the difference in mercury levels is twice the displacement of either surface"),
            ("eliminate", "equate the two pressures and cancel the gravitational field strength"),
            ("solve", "rearrange for the displacement and substitute the densities and the depth"),
            ("check", "confirm the displacement is much smaller than the oil column, as it must be for a liquid fourteen times denser"),
        ],
        "relations": ["p_oil = rho_oil g h", "p_Hg = rho_Hg g (2x)",
                      "rho_oil h = 2 rho_Hg x", "x = rho_oil h/(2 rho_Hg)"],
        "insight": "The factor of two comes from the geometry, not from the physics: when the mercury leaves one arm it does not vanish, it arrives in the other, so the difference in levels is twice the movement of either surface.",
        "shape": "algebraic-elimination",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "850*16/(2*13600)", "want": "0.5"},
    "sol": '''<p><b>What is being tested.</b> Whether you set the pressure balance up at the right place, and whether you remember that the mercury has to go somewhere. The first is physics, the second is bookkeeping, and both have to be right.</p>
<p><b>Step 1 — where to compare pressures.</b> Take the level of the mercury surface in the arm that has risen, and extend that level across to the other arm. The mercury below that level is a single connected body of liquid at rest, so the pressure must be the same at that level on both sides.</p>
<p><b>Step 2 — the left-hand side.</b> Above that level in the oil-filled arm there is the oil column, of depth <code>h</code>, plus the mercury. The oil adds</p>
<div class="formula">p_oil = rho_oil g h</div>
<p>Everything above the oil, the air, presses on both arms equally, so it cancels and can be ignored.</p>
<p><b>Step 3 — the right-hand side.</b> On the other side the only liquid above the chosen level is mercury, and its depth is the difference between the two mercury surfaces. Call the distance the surface in the oil-filled arm fell <code>x</code>. The mercury has not been lost: the volume that left one arm arrived in the other, and the arms have the same cross-section, so the other surface rose by <code>x</code> as well. The difference in levels is therefore</p>
<div class="formula">difference in levels = 2x</div>
<p>and the pressure it provides is</p>
<div class="formula">p_Hg = rho_Hg g (2x)</div>
<p>This factor of two is the whole of the bookkeeping, and leaving it out gives an answer twice as large as it should be.</p>
<p><b>Step 4 — equate and cancel.</b> The pressures at the chosen level are equal:</p>
<div class="formula">rho_oil g h = rho_Hg g (2x)</div>
<p>The gravitational field strength appears on both sides and goes. Nothing in the problem needed a value for <code>g</code>, and that is a sign the setup is right.</p>
<p><b>Step 5 — solve.</b> Rearranging, and working in centimetres so that <code>h = 16</code> and <code>x</code> comes out in centimetres:</p>
<div class="formula">x = rho_oil h/(2 rho_Hg) = (850 x 16)/(2 x 13600)
  = 13600/27200 = 0.5 cm = 5.0 mm</div>
<p>So <b>Answer: B</b>.</p>
<p><b>Step 6 — check the size.</b> The oil column is <code>16 cm</code> deep and the mercury moves only <code>0.5 cm</code>. Mercury is about sixteen times as dense as this oil, and the level difference is twice the displacement, so a displacement of exactly one thirty-second of the oil column is what the densities demand. That is <code>0.5 cm</code>, and it is what came out. If the answer had been of the same order as <code>16 cm</code> the balance would have been set up wrongly.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>2.5 mm</b> is half the correct answer: the factor of two has been applied twice, once in the equation and again in the arithmetic.</p>
<p>&middot; <b>10 mm</b> comes from forgetting that the other arm moves. Using <code>rho_oil h = rho_Hg x</code> gives <code>13600/13600 = 1.0 cm</code>. It is the most likely error and it is out by exactly a factor of two.</p>
<p>&middot; <b>20 mm</b> multiplies by two instead of dividing, which is the same as taking the level difference to be half the displacement — the geometry upside down.</p>
<p>&middot; <b>40 mm</b> has the factor of two inverted and the arithmetic wrong as well, being four times the correct answer.</p>
<p><b>The trap.</b> Treating the mercury surface as though it were held still on the other side. It is not: the two arms are connected, so any mercury that leaves one arrives in the other. The same reasoning appears wherever a liquid is displaced in a tube of uniform bore, and the factor of two is always twice the movement of a single surface, never the movement itself.</p>
<p><b>Relevant topics:</b> pressure in a liquid; the pressure balance in a U-tube; the manometer; why the gravitational field strength cancels in a ratio of columns.</p>''',
    "trap": "Forgetting that the other arm rises. The difference in mercury levels is TWICE the displacement of one surface, so leaving out the factor of two doubles the answer.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 24 — A, toolkit.  An order-of-magnitude estimate of the mass of air in a room.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 24, "id": "S02-24", "module": "A", "diff": 3,
    "topic": "An order-of-magnitude estimate of the mass of air in a room",
    "rel": [("A", "Estimating a volume from everyday dimensions and keeping only the leading figure"),
            ("M", "Mass as density multiplied by volume, with the density of air of order one kilogram per cubic metre"),
            ("A", "Checking an estimate against a known mass rather than against a formula")],
    "key": ["estimate", "density", "air"],
    "stem": '''<p>A classroom measures about <code>10 m</code> by <code>8 m</code> by <code>3 m</code>. The density of air is about <code>1.2 kg m<sup>-3</sup></code>.</p>
<p>Which value is the best estimate of the mass of the air in the room?</p>''',
    "opts": ["<code>3 kg</code>", "<code>30 kg</code>", "<code>300 kg</code>",
             "<code>3000 kg</code>", "<code>30000 kg</code>"],
    "ans": 2,
    "distractors": [
        "reads the density of air as one gram per cubic metre, out by a factor of a thousand",
        "drops one of the three dimensions when working out the volume",
        "correct",
        "takes the density of air to be about that of water",
        "compounds the density error with a volume error, so the estimate is far too large on both counts",
    ],
    "profile": {
        "steps": [
            ("relate", "the mass is the density of the air multiplied by the volume it occupies"),
            ("relate", "estimate the volume as the product of the three dimensions of the room"),
            ("eliminate", "round the density of air to one kilogram per cubic metre, which is all an estimate needs"),
            ("solve", "multiply the rounded density by the volume"),
            ("check", "compare the answer with the mass of water that would fill the same room, which must be far greater"),
        ],
        "relations": ["m = rho V", "V = 10 x 8 x 3", "rho_air about 1 kg m^-3",
                      "m about 1 x 240"],
        "insight": "The density of air is the one number worth carrying in your head: about one kilogram per cubic metre. Everything else follows from the room's dimensions, and both are easy to remember because both are close to one.",
        "shape": "order-of-magnitude",
        "approx": True,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "1.2*10*8*3", "want": "288"},
    "sol": '''<p><b>What is being tested.</b> Whether you can produce a defensible number for a quantity nobody has measured, and then say whether it is sensible. An estimate is not a guess: it is a calculation from rounded inputs, and its value lies in the check at the end.</p>
<p><b>Step 1 — what the answer is made of.</b> The air fills the room, so its mass is the density multiplied by the volume:</p>
<div class="formula">m = rho V</div>
<p><b>Step 2 — the volume.</b> The room is a box, so the volume is the product of its three dimensions:</p>
<div class="formula">V = 10 x 8 x 3 = 240 m^3</div>
<p><b>Step 3 — the density of air.</b> This is the one fact the question requires you to have. Air is about <code>1.2 kg m<sup>-3</sup></code>, and for an estimate it is worth rounding to <code>1 kg m<sup>-3</sup></code> straight away, because the dimensions are themselves only known to one figure.</p>
<p><b>Step 4 — multiply.</b></p>
<div class="formula">m = 1 x 240 = 240 kg</div>
<p>So the answer is a few hundred kilograms. So <b>Answer: C</b>.</p>
<p><b>Step 5 — check it against something known.</b> This is the step that makes the estimate worth anything. If the room were filled with water instead, the mass would be <code>240 m<sup>3</sup></code> times <code>1000 kg m<sup>-3</sup></code>, which is <code>240000 kg</code> — about two hundred and forty tonnes. Air is roughly a thousandth as dense as water, so a few hundred kilograms is the right kind of answer, and the option <code>3000 kg</code> is an order of magnitude too big. A second check: a few hundred kilograms is the mass of a small car. A classroom's air weighing about as much as a car is surprising, but it is not absurd, and that is exactly the sort of reaction a good estimate should provoke.</p>
<p><b>The distractors.</b> Every wrong option is a factor of ten from the answer, which is what makes the question a test of estimation rather than of arithmetic — the digits are all correct, and only the position of the decimal point differs.</p>
<p>&middot; <b>3 kg</b> reads the density of air as about one <i>gram</i> per cubic metre rather than one kilogram. The density of air is <code>1.2 kg m<sup>-3</sup></code>, which is <code>1200 g m<sup>-3</sup></code>.</p>
<p>&middot; <b>30 kg</b> drops one of the three dimensions, so the volume comes out as <code>24 m<sup>3</sup></code> instead of <code>240 m<sup>3</sup></code>. The room has three dimensions and all three must be used.</p>
<p>&middot; <b>3000 kg</b> takes the density of air to be around <code>10 kg m<sup>-3</sup></code>, which is nearer the density of a dense gas under pressure than of the air in a room.</p>
<p>&middot; <b>30000 kg</b> compounds the density error with a volume error, so the estimate is too large on two counts at once.</p>
<p><b>The trap.</b> Treating the estimate as finished once the multiplication is done. The multiplication is the easy part; the check against a known mass is what tells you whether the decimal point is in the right place, and it is the only defence against being out by a factor of ten — which, on a five-option question whose options are all powers of ten apart, is the difference between the right answer and every wrong one.</p>
<p><b>Relevant topics:</b> density and mass; order-of-magnitude estimation; checking an answer against a familiar quantity; significant figures in an estimate.</p>''',
    "trap": "Stopping at the multiplication. An estimate is only worth something once it has been compared with a known mass; without that check, a factor of ten is invisible.",
},

# ═════════════════════════════════════════════════════════════════════════════
# 25 — L, quantum.  What halving the wavelength does to the photoelectron energy.
# ═════════════════════════════════════════════════════════════════════════════
{
    "n": 25, "id": "S02-25", "module": "L", "diff": 3,
    "topic": "The maximum kinetic energy of photoelectrons when the wavelength is halved",
    "rel": [("L", "The photoelectric equation: the photon energy is shared between the work function and the electron"),
            ("L", "Halving the wavelength doubles the photon energy"),
            ("A", "Recognising that a fixed subtraction makes the response to a change more than proportional")],
    "key": ["photoelectric", "workfunction", "photon"],
    "stem": '''<p>The work function of a metal surface is <code>2.0 eV</code>. Light of wavelength <code>&lambda;</code> incident on the surface produces photoelectrons whose maximum kinetic energy is <code>1.0 eV</code>.</p>
<p>The wavelength of the incident light is then halved. What is the new maximum kinetic energy of the photoelectrons?</p>''',
    "opts": ["<code>1.0 eV</code>", "<code>2.0 eV</code>", "<code>3.0 eV</code>",
             "<code>4.0 eV</code>", "<code>6.0 eV</code>"],
    "ans": 3,
    "distractors": [
        "assumes the kinetic energy is unchanged, which would need the photon energy to be unchanged too",
        "doubles the kinetic energy in step with the frequency, ignoring the work function",
        "reports the original photon energy, which is the work function plus the original kinetic energy",
        "correct",
        "reports the new photon energy and forgets to subtract the work function",
    ],
    "profile": {
        "steps": [
            ("relate", "write the photoelectric equation, with the photon energy shared between escaping and moving"),
            ("relate", "find the original photon energy by adding the work function to the observed kinetic energy"),
            ("relate", "halving the wavelength doubles the photon energy, because photon energy goes as the reciprocal of the wavelength"),
            ("eliminate", "recognise that the work function does not change, because it is a property of the metal rather than of the light"),
            ("solve", "subtract the same work function from the doubled photon energy"),
            ("check", "confirm that the kinetic energy has more than doubled, which is what a fixed subtraction from a doubled quantity requires"),
        ],
        "relations": ["hf = phi + E_k", "hf = hc/lambda", "E_k = hc/lambda - phi",
                      "hf_new = 2 hf_old"],
        "insight": "The work function is a fixed toll that every electron pays. Doubling the photon energy does not double what is left over, because the toll is unchanged — it takes a smaller share of a bigger payment.",
        "shape": "proportionality",
        "approx": False,
        "symbolic": False,
        "figure_essential": False,
    },
    "check": {"kind": "eval", "expr": "2*(1.0 + 2.0) - 2.0", "want": "4.0"},
    "sol": '''<p><b>What is being tested.</b> Whether you treat the work function as a fixed subtraction or as something that scales with the light. It does not scale: it is a property of the metal, and the same toll is paid whatever arrives.</p>
<p><b>Step 1 — the photoelectric equation.</b> One photon is absorbed by one electron. The energy has to do two things: get the electron out of the metal, and give it whatever is left as kinetic energy:</p>
<div class="formula">hf = phi + E_k</div>
<p>where <code>&phi;</code> is the work function and <code>E_k</code> is the maximum kinetic energy.</p>
<p><b>Step 2 — the original photon energy.</b> This is the step that makes the rest possible. The question gives the kinetic energy and the work function, but not the photon energy, so it has to be found:</p>
<div class="formula">hf = 2.0 + 1.0 = 3.0 eV</div>
<p><b>Step 3 — what halving the wavelength does.</b> Photon energy is <code>hc/&lambda;</code>, so it is inversely proportional to the wavelength. Halving <code>&lambda;</code> doubles <code>hf</code>:</p>
<div class="formula">hf_new = 2 x 3.0 = 6.0 eV</div>
<p><b>Step 4 — the work function does not change.</b> This is the crux. The work function is the energy needed to remove an electron from that particular metal. It depends on the metal and not on the light, so the same <code>2.0 eV</code> is subtracted as before.</p>
<p><b>Step 5 — subtract.</b></p>
<div class="formula">E_k,new = 6.0 - 2.0 = 4.0 eV</div>
<p>So <b>Answer: D</b>.</p>
<p><b>Step 6 — check that the increase is more than proportional.</b> The photon energy doubled, from <code>3.0</code> to <code>6.0 eV</code>, but the kinetic energy went from <code>1.0</code> to <code>4.0 eV</code> — a factor of four, not two. That is not an error: it is what a fixed subtraction does. The work function took one third of the original photon energy and takes only one third of the new one... in fact it takes <code>2.0</code> of <code>6.0</code>, which is one third, so the share it takes has fallen, and the share left for the electron has risen. Whenever a fixed amount is subtracted from a quantity that has grown, the remainder grows by more than the original factor. The direction of the answer is therefore right, and so is its size.</p>
<p><b>The distractors.</b></p>
<p>&middot; <b>1.0 eV</b> assumes the kinetic energy is unchanged. That would require the photon energy to be unchanged, which contradicts halving the wavelength.</p>
<p>&middot; <b>2.0 eV</b> doubles the kinetic energy in step with the photon energy. It treats the work function as though it too had doubled, or as though it did not exist.</p>
<p>&middot; <b>3.0 eV</b> is the original photon energy. It is a real quantity and a useful intermediate step, which is exactly why it is offered — but the question asks for the kinetic energy, not for the photon energy.</p>
<p>&middot; <b>6.0 eV</b> is the new photon energy with the work function never subtracted. The electron cannot leave with all of it; getting out of the metal costs energy, and that cost is the whole content of the work function.</p>
<p><b>The trap.</b> Scaling everything in proportion. A candidate who notices that halving the wavelength doubles the photon energy may double the kinetic energy as well, and the answer looks reasonable. It is wrong because the photoelectric equation is not a proportion — it is a proportion with a constant taken away, and a constant taken away breaks proportionality.</p>
<p><b>Relevant topics:</b> the photoelectric effect; the work function; photon energy and wavelength; the threshold frequency; why a fixed subtraction destroys proportionality.</p>''',
    "trap": "Doubling the kinetic energy because the photon energy doubled. The work function is a fixed subtraction, so the remainder grows by MORE than the factor the photon energy grew by.",
},

]
