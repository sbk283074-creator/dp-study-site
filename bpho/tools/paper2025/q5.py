# -*- coding: utf-8 -*-
"""2025 Round 0 past paper — questions 21 to 25."""

QUESTIONS = [

{
    "id": "R0-21", "n": 21, "module": "C", "topic": "Moments", "diff": 3,
    "rel": [
        ("C", "Moments"),
        ("C", "Inclined plane"),
        ("B", "Uniform acceleration"),
        ("A", "Ratio reasoning"),
    ],
    "stem": "<p>A light inextensible string is attached to one end of a rigid rod of negligible weight and of "
            "length <code>ℓ</code>, with its other end freely hinged at O. The other end of the string is "
            "attached to the ceiling, so that the string is vertical, and the rod makes an angle of 30° to the "
            "horizontal. A small smooth ring of mass <code>m</code> is released from rest at the upper end of "
            "the rod and slides downwards along it.</p>{{FIG:r0-21}}"
            "<p>Given that the tension in the string <code>T</code> at time <code>t</code> (while the ring is in "
            "motion) is <code>T = mg(1 − kt²)</code>, select the correct expression for <code>k</code>.</p>",
    "fig": None,
    "opts": ["g / 4ℓ", "g / 2ℓ", "g / ℓ", "g / (√2 ℓ)", "√3 g / (2ℓ)"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> One realisation unlocks the whole question: <b>the rod does not move</b>. "
            "The hinge fixes O and the inextensible vertical string fixes the upper end, so a rigid rod of fixed 
            "length is held at 30° for ever. The ring is therefore just a bead sliding down a smooth incline 
            "that happens to be held up by a string — and the tension is found from moments, not from forces 
            "on the ring.</p>
<p><b>Step 0 — read the given form before doing any algebra.</b> You are told <code>T = mg(1 − kt²)</code>. 
            "At <code>t = 0</code> the ring is at the upper end, i.e. a distance <code>ℓ</code> from the hinge, 
            "and the given form says <code>T = mg</code>. So whatever you derive must collapse to <code>mg</code> 
            "when the ring sits at the top. That single check is worth doing first, because it fixes the 
            "normalisation and it kills several candidate mistakes immediately.</p>
<p><b>Step 1 — how fast does the ring move?</b> The rod is smooth, so the only force with a component along 
            "it is gravity:</p>
<div class="formula">a = g sin 30° = g / 2</div>
<p>Released from rest, the distance <code>s</code> slid down from the upper end is</p>
<div class="formula">s = ½ a t² = ½ (g/2) t² = g t² / 4</div>
<p>so its distance from the hinge O is</p>
<div class="formula">r = ℓ − s = ℓ − g t² / 4</div>
<p><b>Step 2 — the normal reaction.</b> The ring has no acceleration perpendicular to the rod, so the 
            "perpendicular component of gravity is balanced by the normal reaction:</p>
<div class="formula">N = mg cos 30°</div>
<p><b>Step 3 — moments about O for the rod.</b> The rod is weightless and static, so the moments must balance. 
            "Two forces act at a distance from O:</p>
<div class="formula">tension T, vertical, at the upper end  →  lever arm ℓ cos 30°
normal reaction N, perpendicular to the rod, at distance r  →  lever arm r</div>
<div class="formula">T · ℓ cos 30° = N · r = mg cos 30° · r</div>
<p>and the <code>cos 30°</code> cancels — which is the pretty part of this question, because it means the 
            "30° never survives into the answer:</p>
<div class="formula">T = mg r / ℓ = mg (ℓ − g t²/4) / ℓ = mg (1 − g t² / 4ℓ)</div>
<p><b>Answer: A, k = g / 4ℓ.</b></p>
{{FIG:r0-21}}
<p><b>The <code>t = 0</code> check works.</b> Putting <code>r = ℓ</code> gives <code>T = mg</code>, exactly as 
            "the given form requires. And as the ring reaches the hinge, <code>r → 0</code> and the tension 
            "falls to zero — with no ring left on the rod there is nothing for the string to hold up.</p>
<p><b>Dimensions, as a second check.</b> <code>kt²</code> must be dimensionless, so <code>k</code> is a 
            "<code>1/time²</code>. Every option is <code>g</code> divided by a length, which is exactly 
            "<code>s⁻²</code>, so dimensions alone cannot separate them — you have to get the factor right. 
            "That is deliberate.</p>
<p><b>Where the wrong options come from.</b> All five options are <code>g/ℓ</code> times a pure number, so 
            "every wrong answer is one specific slip in Step 1:</p>
<div class="formula">A  0.25 g/ℓ   correct:                s = ½(g sin 30°)t² = g t²/4
B  0.50 g/ℓ   took a = g:            s = ½ g t²          (forgot sin 30°)
C  1.00 g/ℓ   took a = g, forgot ½:  s = g t²            (two slips)
D  0.71 g/ℓ   a spurious √2
E  0.87 g/ℓ   a spurious √3 — e.g. reaching for cos 30° instead of sin 30°</div>
<p>B is by far the most tempting, because “released from rest, so <code>s = ½gt²</code>” is an reflex. It is 
            "wrong here only because gravity does not act along the rod.</p>
<p><b>A third route, if you distrust the moment arm.</b> Resolve instead of taking moments about O: the rod is 
            "weightless and static, so the hinge reaction plus <code>T</code> plus <code>N</code> must sum to 
            "zero. Taking moments is faster and it removes the hinge reaction entirely, which is why it is the 
            "right first move on any question involving a hinged body.</p>
<p><b>Relevant topics:</b> moments about a hinge; resolution along and perpendicular to an incline; 
            "<code>s = ½at²</code> from rest; reading a given algebraic form for a boundary condition.</p>""",
    "trap": "Taking the rod to rotate, or treating the ring as falling vertically with <code>a = g</code>. The rod is held still by the string; the ring accelerates at <code>g sin 30° = g/2</code> along it.",
},

{
    "id": "R0-22", "n": 22, "module": "D", "topic": "Conical pendulum", "diff": 2,
    "rel": [
        ("D", "Conical pendulum"),
        ("D", "Angular speed"),
        ("D", "Centripetal force"),
        ("A", "Ratio reasoning"),
    ],
    "stem": "<p>A conical pendulum consists of a bob attached to a light inextensible string of length"
            "<code>ℓ</code>, with the upper end fixed. The bob moves in a horizontal circle so that the string "
            "makes an angle of 30° to the vertical. By what factor must the angular frequency be increased for "
            "this angle to double to 60°?</p>",
    "fig": None,
    "opts": ["√√3", "√2", "√3", "2", "3"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> Whether you know the conical-pendulum result well enough to use it "
            "as a ratio, and whether you remember that it gives <code>ω²</code>, not <code>ω</code>. The 
            "question is deliberately phrased as “by what factor”, which is a loud hint that nothing except 
            "the ratio matters — <code>ℓ</code>, <code>g</code> and <code>m</code> all cancel.</p>
<p><b>Step 1 — the standard result, derived in two lines.</b> With the string at angle <code>θ</code> to the 
            "vertical and the bob on a circle of radius <code>r = ℓ sin θ</code>:</p>
<div class="formula">vertical:    T cos θ = mg
horizontal:  T sin θ = m ω² r = m ω² ℓ sin θ</div>
<p>The second line gives <code>T = m ω² ℓ</code> directly (the <code>sin θ</code> cancels on both sides). 
            "Substituting into the first:</p>
<div class="formula">m ω² ℓ cos θ = mg    ⇒    ω² = g / (ℓ cos θ)</div>
<p><b>Step 2 — take the ratio, not the values.</b> For two angles at the same <code>ℓ</code>:</p>
<div class="formula">ω₂ / ω₁ = √[ cos θ₁ / cos θ₂ ] = √[ cos 30° / cos 60° ]</div>
<div class="formula">cos 30° = √3 / 2 ,   cos 60° = 1 / 2
cos 30° / cos 60° = √3</div>
<div class="formula">ω₂ / ω₁ = √√3 = 3^(1/4) ≈ 1.32</div>
<p><b>Answer: A, √√3.</b></p>
{{FIG:r0-22}}
<p><b>Why the answer is so small — the physical check.</b> Doubling the angle from 30° to 60° sounds like a 
            "dramatic change, and two things do change a lot: the radius grows from <code>0.50ℓ</code> to 
            "<code>0.87ℓ</code> and the bob drops from <code>0.87ℓ</code> to <code>0.50ℓ</code> below the 
            "pivot. But <code>ω² ∝ 1/cos θ</code>, and <code>cos θ</code> only falls by a factor of 
            "<code>√3 ≈ 1.73</code>. Taking the square root halves that in log terms and leaves a factor of 
            "just <code>1.32</code>. If you find yourself writing down “about 1.7” or “about 2”, you have 
            "most likely reported <code>ω²</code>’s ratio as if it were <code>ω</code>’s.</p>
<p><b>Where the wrong options come from.</b></p>
<div class="formula">C = √3 = 1.732   the exact ratio of ω² — the square root was forgotten
E = 3            tan 60° / tan 30°  — reaching for tan instead of cos
D = 2            the angle itself doubled, so “the factor must be 2”
B = √2 = 1.414   a near-miss decoy sitting just above the true 1.32</div>
<p>C is the one to worry about: it is a fully correct calculation of the wrong quantity. Whenever a question 
            "asks “by what factor” about a quantity that appears squared, write down explicitly whether you 
            "have just found <code>X</code> or <code>X²</code> before you look at the options.</p>
<p><b>The method.</b> For any “<code>θ</code> changes, what happens to <code>ω</code>” question, rearrange 
            "the governing equation so the changing quantity stands alone:</p>
<div class="formula">ω = √( g / (ℓ cos θ) )  ∝  (cos θ)^(−1/2)</div>
<p>Then the factor is <code>(cos θ₁ / cos θ₂)^(1/2)</code> and no other quantity can appear. That is why the 
            "options are pure numbers with no <code>g</code> or <code>ℓ</code> in them — a useful clue that 
            "you are on the right track.</p>
<p><b>Relevant topics:</b> conical pendulum; resolving tension into vertical and radial components; 
            "<code>ω² = g/(ℓ cos θ)</code>; ratio reasoning with a square root.</p>""",
    "trap": "Reporting <code>cos 30°/cos 60° = √3</code> as the answer. That is the factor for <code>ω²</code>; the question asks about <code>ω</code>, so you must take the square root: <code>√√3</code>.",
},

{
    "id": "R0-23", "n": 23, "module": "H", "topic": "Log–log graphs", "diff": 3,
    "rel": [
        ("A", "Graph shape"),
        ("F", "Intensity ratio"),
        ("H", "Potential divider"),
        ("A", "Order of magnitude"),
    ],
    "stem": "<p>The resistance <code>R</code> of a light-dependent resistor (LDR) depends on the light"
            "intensity <code>I</code>. A logarithmic plot relating these variables is shown below.</p>"
            "{{FIG:r0-23}}"
            "<p>A point light source placed a distance <code>d</code> from the LDR illuminates it, and its "
            "resistance is measured to be <code>R₀</code>. Which of the following is a good approximation for "
            "the LDR resistance when the distance to the light source is halved?</p>",
    "fig": None,
    "opts": ["0.1 R₀", "0.3 R₀", "0.5 R₀", "0.7 R₀", "0.9 R₀"],
    "ans": 1,
    "sol": """<p><b>What is being tested.</b> Two separations that are usually taught apart and are here "
            "combined: reading a power law off a log–log plot, and knowing how a point source's intensity 
            "falls with distance. Neither step is hard; the difficulty is that the answer is not a round 
            "number, so you cannot guess it — you have to commit to the arithmetic.</p>
<p><b>Step 1 — read the gradient off the log–log plot.</b> On log axes a power law <code>R ∝ I^n</code> is a 
            "straight line of gradient <code>n</code>. The line runs from <code>(0, 5.2)</code> to 
            "<code>(4, 1.8)</code>, so</p>
<div class="formula">n = (1.8 − 5.2) / (4 − 0) = −3.4 / 4 = −0.85</div>
<div class="formula">R ∝ I^(−0.85)</div>
<p>Note the two things that make log axes worth using: the intercept (the “5.2”) is irrelevant to this 
            "question, and the units inside the logarithm are handled for you by the axis labels.</p>
<p><b>Step 2 — what halving the distance does to the intensity.</b> A point source spreads its power over a 
            "sphere of area <code>4πd²</code>, so</p>
<div class="formula">I ∝ 1 / d²        ⇒        d → d/2  gives  I → 4I</div>
<p><b>Step 3 — combine.</b></p>
<div class="formula">R_new / R₀ = (4I / I)^(−0.85) = 4^(−0.85)</div>
<p>Now the arithmetic, done the way you would do it without a calculator. Write it in base 2:</p>
<div class="formula">4^0.85 = 2^1.70 = 2 × 2^0.70</div>
<p>and <code>2^0.70</code> is a little above <code>2^0.5 = 1.41</code> and a little below 
            "<code>2^0.75 = 1.68</code>; call it <code>1.62</code>. So</p>
<div class="formula">4^0.85 ≈ 2 × 1.62 = 3.25        ⇒        4^(−0.85) ≈ 1 / 3.25 ≈ 0.31</div>
<p><b>Answer: B, 0.3 R₀.</b></p>
<p><b>The robustness check that matters most here.</b> Suppose you read the gradient as exactly 
            "<code>−1</code> instead of <code>−0.85</code> — a very reasonable mis-reading of a hand-drawn 
            "graph. Then</p>
<div class="formula">R_new / R₀ = 4^(−1) = 0.25</div>
<p>and the nearest option is still <code>0.3 R₀</code>. So the answer does not depend on reading the gradient 
            "to two decimal places; it only depends on the gradient being close to <code>−1</code> and clearly 
            "not close to <code>0</code> or <code>−2</code>. That is what “a good approximation” in the 
            "question is telling you.</p>
<p><b>Where the wrong options come from.</b></p>
<div class="formula">C = 0.5 R₀   used I ∝ 1/d, not 1/d²  →  2^(−0.85) ≈ 0.55
A = 0.1 R₀   used I ∝ 1/d³, or 4^(−1.7) ≈ 0.095
D = 0.7 R₀   treated the change as small — as if the axes were linear
E = 0.9 R₀   almost no change at all</div>
<p>C is the one to watch for: “halve the distance, so halve the intensity” is the single most common error 
            "in this topic, and the option is sitting there to reward it.</p>
<p><b>The method for any log–log question.</b> Do three things in this order, and never multiply numbers 
            "before you have done all three:</p>
<div class="formula">1. gradient of the line  →  the power n in  y ∝ x^n
2. what the physics does to x  →  the factor by which x changes
3. raise that factor to the power n</div>
<p><b>Relevant topics:</b> log–log plots and power laws; inverse-square law for a point source; estimating 
            "powers of 2 without a calculator.</p>""",
    "trap": "Halving the distance and halving the intensity. A point source obeys <code>I ∝ 1/d²</code>, so halving <code>d</code> <i>quadruples</i> <code>I</code>; that error leads straight to option C.",
},

{
    "id": "R0-24", "n": 24, "module": "C", "topic": "Centre of mass", "diff": 3,
    "rel": [
        ("C", "Centre of mass"),
        ("C", "Equilibrium"),
        ("A", "Small-parameter approximations"),
        ("A", "Geometric approximation"),
    ],
    "stem": "<p>A uniform ladder of mass <code>m</code> rests against a wall in static equilibrium at an angle"
            "of 45° to the vertical. The base of the ladder is pushed a small distance <code>a</code> towards "
            "the wall. Which of these options gives the best approximation for the change in gravitational "
            "potential energy of the ladder?</p>",
    "fig": None,
    "opts": ["½ mga", "(1/√2) mga", "mga", "√2 mga", "2 mga"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> Whether you see that the ladder's gravitational potential energy "
            "depends on exactly one thing — the height of its centre of mass — and whether you can get that 
            "height change from the geometry without differentiating anything. The word “small” is the key: 
            "it tells you to use a first-order (linear) approximation, so a single derivative is the whole 
            "calculation.</p>
<p><b>Step 1 — the only variable that matters.</b> The ladder is uniform, so its centre of mass is at its 
            "midpoint. If the ladder has length <code>L</code> and makes angle <code>θ</code> with the 
            "horizontal, the centre of mass is at height</p>
<div class="formula">h = (L / 2) sin θ        ⇒        U = mg (L/2) sin θ</div>
<p>and the foot of the ladder is a horizontal distance <code>x = L cos θ</code> from the wall.</p>
<p><b>Step 2 — relate a change in <code>x</code> to a change in <code>h</code>.</b> Differentiate both with 
            "respect to <code>θ</code> and divide:</p>
<div class="formula">dh/dθ = (L/2) cos θ ,      dx/dθ = −L sin θ
dh/dx = −(1/2) cot θ</div>
<p>The minus sign is the physics: pushing the foot <i>towards</i> the wall (<code>x</code> decreasing) makes 
            "the centre of mass go <i>up</i>.</p>
<p><b>Step 3 — evaluate at 45°.</b> Here “45° to the vertical” is the same thing as 45° to the horizontal, 
            "since the wall and the floor are perpendicular. So <code>cot 45° = 1</code>:</p>
<div class="formula">Δh = −(1/2) cot 45° · Δx = −(1/2)(−a) = a / 2</div>
<div class="formula">ΔU = mg Δh = (1/2) m g a</div>
<p><b>Answer: A, ½ mga.</b></p>
{{FIG:r0-24}}
<p><b>The tidy check.</b> The centre of mass rises by exactly half of <code>a</code> — half because the centre 
            "of mass is at the middle of the ladder. Here is the same result without calculus: when the foot 
            "moves in by <code>a</code>, the <i>top</i> of the ladder slides up the wall by <code>a</code> at 
            "45° (the top and foot swap equal amounts of horizontal and vertical). The middle rises half as 
            "much as the top, so <code>Δh = a/2</code>. Two routes, same answer.</p>
<p><b>The general result, and why it makes sense.</b></p>
<div class="formula">ΔU = ½ m g a cot θ</div>
<p>This is the sanity check that catches most slips. If the ladder is nearly vertical 
            "(<code>θ → 90°</code>), <code>cot θ → 0</code>: nudging the foot barely lifts the middle at all, 
            "which is right. If the ladder is nearly flat (<code>θ → 0</code>), <code>cot θ → ∞</code>: a 
            "tiny push lifts the middle enormously, which is also right. At 45° the factor is exactly 1, so 
            "the answer is the clean-looking <code>½mga</code>. Any answer with a <code>√2</code> in it should 
            "make you suspicious, because 45° is precisely the angle at which the sine and cosine are equal 
            "and the square roots cancel.</p>
<p><b>Where the wrong options come from.</b></p>
<div class="formula">C = mga        forgot the centre of mass is at the middle (used the top of the ladder)
B = mga/√2     picked up a spurious sin 45° factor
D = √2 mga     picked up a spurious 1/cos 45° factor
E = 2 mga      over-corrected in both directions at once</div>
<p>C is the trap with real physics content: it is the change in potential energy of the <i>top</i> of the 
            "ladder, not of the ladder. Whenever a uniform body is involved, the factor of <code>½</code> from 
            "the centre of mass is the single easiest thing to lose.</p>
<p><b>Relevant topics:</b> centre of mass of a uniform body; gravitational potential energy 
            "<code>mgh</code>; small-change approximations; the geometry of a ladder against a wall.</p>""",
    "trap": "Forgetting that only the centre of mass matters, which gives <code>mga</code> (option C). Also note that 45° to the vertical is 45° to the horizontal, so <code>cot θ = 1</code>.",
},

{
    "id": "R0-25", "n": 25, "module": "H", "topic": "Network reduction", "diff": 3,
    "rel": [
        ("H", "Network reduction"),
        ("H", "Series and parallel"),
        ("A", "Ratio reasoning"),
    ],
    "stem": "<p>Consider the arrangement of 12 identical resistors below. The equivalent resistance is measured"
            "between the following pairs of points: PR, PS, PU, QS, QT. Which measurement gives the median "
            "(middle value) resistance?</p>{{FIG:r0-25}}",
    "fig": None,
    "opts": ["PR", "PS", "PU", "QS", "QT"],
    "ans": 4,
    "sol": """<p><b>What is being tested.</b> This looks like five brutal network calculations, and it is "
            "deliberately built so that it is not. Every one of the five pairs sits on a symmetry axis of the 
            "grid, so each can be reduced by <b>folding</b> — and once folded, three of the five collapse to 
            "plain series and parallel. Recognising the symmetry is the entire question.</p>
<p><b>Set-up.</b> Call every resistor <code>1 Ω</code>; only the ratios matter. Label the nine nodes as a 
            "3 × 3 grid:</p>
<div class="formula">P —— Q —— R          row 0
|    |    |
• —— S —— •          row 1
|    |    |
• —— T —— U          row 2</div>
<p>Twelve resistors: six horizontal (two per row) and six vertical (two per column).</p>
{{FIG:r0-25}}
<p><b>The two symmetries.</b></p>
<div class="formula">M  : reflect in the vertical centre line   P↔R,  A↔B,  C↔U,  and Q, S, T fixed
D  : reflect in the diagonal P–S–U           Q↔A,  R↔C,  B↔T,  and P, S, U fixed</div>
<p>Under <b>M</b> a mirrored pair of resistors becomes two in parallel, i.e. <code>½ Ω</code>. Under <b>D</b> 
            "the same is true. That single rule does all the work.</p>
<p><b>QT — reduce by M.</b> Q and T are both fixed by M, so the excitation is symmetric and 
            "<code>V(P) = V(R)</code>, <code>V(A) = V(B)</code>, <code>V(C) = V(U)</code>. Fold:</p>
<div class="formula">Q—P and Q—R  →  ½ Ω          Q—S  stays 1 Ω
A—S and S—B  →  ½ Ω          S—T  stays 1 Ω
C—T and T—U  →  ½ Ω
P—A and R—B  →  ½ Ω          A—C and B—U  →  ½ Ω</div>
<p>The folded circuit is a Wheatstone bridge whose upper arms are <code>½ + ½ = 1 Ω</code> (via P, A) and 
            "<code>1 Ω</code> (via S), and whose lower arms are <code>1 Ω</code> (via C) and <code>1 Ω</code> 
            "— so it is <b>balanced</b> and the <code>½ Ω</code> link between A and S carries no current. 
            "Remove it:</p>
<div class="formula">R_QT = (1 + 1) ∥ (1 + 1) = 2 ∥ 2 = 1 Ω</div>
<p><b>QS — reduce by M.</b> Same fold; now measure between Q and S. The direct resistor 
            "<code>Q—S = 1 Ω</code> is in parallel with everything else, so the answer must be <i>below</i> 
            "<code>1 Ω</code>. Solving the same folded bridge (inject 1 A at Q, extract at S) gives</p>
<div class="formula">V_C = ¾ V_A ,   V_A = (V_Q + 2 V_S)/4 ,   V_S = (V_Q + 2 V_A)/4
⇒  V_A = 2V_Q/7 ,  and at Q:  2(V_Q − 9V_Q/14) + V_Q = 1
⇒  V_Q = 7/12</div>
<div class="formula">R_QS = 7/12 Ω ≈ 0.583 Ω</div>
<p><b>PR — reduce by M, antisymmetrically.</b> Now P and R are a mirrored <i>pair</i>, so the excitation is 
            "antisymmetric: <code>V(Q) = V(S) = V(T) = ½(V_P + V_R)</code>, and those three axis nodes sit at 
            "the same potential, so the links Q—S and S—T carry no current. Consider the left half with the 
            "axis held at <code>V/2</code>, taking <code>V_P = V</code>:</p>
<div class="formula">P—A = 1,  A—C = 1,  P—axis = 1,  A—axis = 1,  C—axis = 1
node A:  3V_A − V_C = 3V/2
node C:  2V_C = V_A + V/2        ⇒  V_A = 7V/10,  V_C = 3V/5
I from P = (V − V_A) + (V − V/2) = 0.3V + 0.5V = 4V/5</div>
<div class="formula">R_PR = V / (4V/5) = 5/4 Ω = 1.25 Ω</div>
<p><b>PS and PU — reduce by D.</b> Both P and U are fixed by the diagonal reflection, so fold along the 
            "diagonal: <code>Q</code> merges with <code>A</code>, <code>R</code> with <code>C</code>, 
            "<code>B</code> with <code>T</code>, and every merged pair of resistors becomes <code>½ Ω</code>. 
            "The folded circuit is a chain with one bypass:</p>
<div class="formula">P —½— QA —½— RC —½— TB —½— U
          QA —½— S —½— TB</div>
<p>For <b>PU</b> (measure P to U): by symmetry <code>V_S = V_RC</code>, and solving gives 
            "<code>V_RC = ½V_P</code>, <code>V_QA = ⅔V_P</code>, so with 1 A injected, 
            "<code>2(V_P − ⅔V_P) = 1</code> and</p>
<div class="formula">R_PU = 3/2 Ω = 1.5 Ω</div>
<p>For <b>PS</b> (measure P to S): the same folded circuit gives <code>V_QA = 3/8</code>, 
            "<code>V_RC = 1/4</code>, <code>V_TB = 1/8</code> with 1 A injected at P, so</p>
<div class="formula">R_PS = 7/8 Ω = 0.875 Ω</div>
<p><b>Now take the median.</b></p>
<div class="formula">QS   = 7/12  ≈ 0.583     (smallest)
PS   = 7/8   = 0.875
QT   = 1     = 1.000     ←  middle of five
PR   = 5/4   = 1.250
PU   = 3/2   = 1.500     (largest)</div>
<p><b>Answer: E, QT.</b></p>
<p><b>Two shortcuts that get you there faster.</b> First, you never needed PS, PU or PR to any precision: 
            "QS is obviously the smallest (Q and S are joined by a single resistor with the rest of the grid in 
            "parallel, so it is under <code>1 Ω</code>), and PU is obviously the largest (P and U are opposite 
            "corners, the longest journey through the grid). PR and PS bracket <code>1 Ω</code>. So the median 
            "is whichever of PS, QT, PR is the middle one — and since <code>R_PS &lt; 1</code> 
            "(P and S are diagonal neighbours, closer than the opposite corners) while <code>R_PR</code> spans 
            "a whole row, QT at exactly <code>1 Ω</code> is the only candidate that can sit in the middle.</p>
<p>Second, and worth internalising: <b>QT = 1 Ω exactly</b>, i.e. the whole grid measured across its axis is 
            "equivalent to a single resistor. That is not a coincidence — it is the balanced-bridge result, and 
            "it is the sort of clean number a paper setter builds a question around.</p>
<p><b>Where the wrong options come from.</b> Each names a different pair, so there is no arithmetic to slip 
            "on; the only way to get this wrong is to guess the ordering instead of establishing it. The 
            "ordering is by “how far apart are the two nodes in the grid”, tempered by how many parallel 
            "routes exist — which is why QT, a two-step journey straight down the axis with a balanced bridge, 
            "lands exactly in the middle.</p>
<p><b>Relevant topics:</b> symmetry folding of resistor networks; series and parallel combinations; the 
            "balanced Wheatstone bridge; identifying a median without evaluating every term.</p>""",
    "trap": "Trying to evaluate all five networks by brute force, or assuming the median follows the alphabetical order of the labels. Fold on the symmetry axis first — QT reduces to a balanced bridge and is exactly <code>1 Ω</code>.",
},

]

