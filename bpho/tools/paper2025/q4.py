# -*- coding: utf-8 -*-
"""2025 Round 0 past paper — questions 16 to 20."""

QUESTIONS = [

{
    "id": "R0-16", "n": 16, "module": "G", "topic": "Time of flight through a glass cube", "diff": 3,
    "rel": [
        ("G", "Snell's law and the angle of refraction"),
        ("G", "Speed of light in a medium: v = c / n"),
        ("A", "Surds and reciprocals without a calculator"),
    ],
    "stem": "<p>A ray of light is incident on a glass cube of side length <code>a</code> and refractive index "
            "<code>√2</code>. The angle of incidence is 30°. Find the time taken for the light to travel to the "
            "opposite face.</p>",
    "fig": None,
    "opts": ["√(8/7) · a/c", "(4/√7) · a/c", "(√2/3) · a/c", "(4/√3) · a/c", "(4/√2) · a/c"],
    "ans": 1,
    "sol": """<p><b>What is being tested.</b> A three-line calculation where each line is a separate idea: refract the ray, slow it down, and measure the path — plus enough surd algebra to land on one of five similar-looking fractions.</p>
<p><b>Step 1 — find the angle inside the glass.</b> Here the 30° is the angle of incidence measured from the normal, as usual. Snell's law gives</p>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂
1 × sin 30° = √2 × sin θ₂
sin θ₂ = 0.5 / √2 = 1 / (2√2)</div>
<p><b>Do not evaluate the angle.</b> “θ₂ = 20.7°” would need a calculator and nothing here needs it: keep <code>sin θ₂ = 1/(2√2)</code> and carry it forward. All you should conclude at this point is the direction — the ray bends <i>towards</i> the normal on entering the glass, because it enters a denser medium, so <code>θ₂ &lt; 30°</code>. That single inequality is what does the work later.</p>
<p><b>Step 2 — how far it travels inside.</b> The ray enters through one face and leaves through the opposite face, a distance <code>a</code> away. Because the ray is at angle <code>θ₂</code> to the normal, the path is the hypotenuse of a right-angled triangle whose adjacent side is <code>a</code>:</p>
<div class="formula">path = a / cos θ₂</div>
{{FIG:r0-16}}
<p><b>Step 3 — the speed inside the glass.</b></p>
<div class="formula">v = c / n = c / √2</div>
<p><b>Step 4 — assemble, keeping <code>cos θ₂</code> exact.</b> Rather than evaluate 20.7°, use <code>sin² + cos² = 1</code>:</p>
<div class="formula">cos θ₂ = √(1 − 1/8) = √(7/8) = √7 / (2√2)</div>
<div class="formula">t = path / v = [a / cos θ₂] × [√2 / c]
  = a √2 / (c · √7/(2√2))
  = 2√2 · √2 · a / (√7 c)
  = 4a / (√7 c)</div>
<p><b>Answer: B, (4/√7) · a/c.</b> As a rough size, <code>√7 ≈ 2.65</code> (because <code>2.65² = 7.02</code>), so the light takes about <code>4/2.65 ≈ 1.5 a/c</code> — longer than <code>a/c</code>, as it must be, since it travels further than <code>a</code> and it travels more slowly. But you can reach B without that division at all, which is the point of the next check.</p>
<p><b>Identifying B without evaluating anything.</b> Two crude bounds, both from facts you already have.</p>
<p><i>Lower bound.</i> The path through the glass is longer than <code>a</code> (the ray is not normal to the
face), and the speed is <code>c/√2</code>, so <code>t &gt; a/(c/√2) = √2 · a/c</code>.</p>
<p><i>Upper bound.</i> You know <code>θ₂ &lt; 30°</code>, so <code>cos θ₂ &gt; cos 30° = √3/2</code>, so the
path <code>a/cos θ₂ &lt; 2a/√3</code>, and</p>
<div class="formula">t = (path) / (c/√2)  &lt;  (2a/√3) · (√2/c)  =  √(8/3) · a/c</div>
<p>So the answer lies strictly between <code>√2 = 1.414</code> and <code>√(8/3) = 1.633</code>. Now compare
the five options <b>by squaring them</b> — no roots, no decimals:</p>
<div class="formula">bounds squared:        2          &lt;  t^2  &lt;  8/3 = 2.67
A  √(8/7)   →   8/7   = 1.14     too small
B  4/√7     →  16/7   = 2.29     ✔  inside
C  √2/3     →   2/9   = 0.22     too small
D  4/√3     →  16/3   = 5.33     too big
E  4/√2     →  16/2   = 8.00     too big</div>
<p>B is the only one that fits, and the decision used nothing but two inequalities and five easy divisions.
This is what “non-calculator” actually asks of you: bound the answer, then test the options against the
bounds. The full derivation above is how you <i>confirm</i> it; the bounds are how you <i>find</i> it in
forty seconds.</p>
<p><b>Where the wrong options come from.</b> A, <code>√(8/7) a/c = 1.069 a/c</code>, is exactly <code>a/(cos θ₂ · c)</code>: the correct path, travelled at speed <code>c</code> — that is, with the refractive index forgotten in the speed but kept in the angle. It is the most instructive of the four wrong answers, because it is right in three places and wrong in one. C, D and E are the other combinations of the same ingredients: the depth <code>a</code> against the diagonal <code>a√2</code>, and the speed <code>c</code> against <code>c/√2</code>.</p>
<p><b>The method.</b> Always write the time as <code>t = path / speed</code> before substituting anything, and write both the path and the speed as multiples of <code>a</code> and <code>c</code>. Then the answer is forced to be <code>(something) × a/c</code>, and the only question left is which surd the something is. That is exactly the form all five options take, which is a strong hint that the paper expects this route.</p>
<p><b>Relevant topics:</b> Snell's law; speed of light in a medium; geometric path length; surd manipulation.</p>""",
    "trap": "Using <code>v = c</code> inside the glass, or taking the path as <code>a</code> rather than <code>a/cos θ₂</code>. Both errors give <code>√(8/7)·a/c</code>, which is on the list.",
},

{
    "id": "R0-17", "n": 17, "module": "L", "topic": "How many photoelectrons charge the capacitor", "diff": 3,
    "rel": [
        ("L", "The photoelectric equation hf = φ + KE_max"),
        ("L", "Stopping potential: eV_s = h(f − f₀)"),
        ("I", "Q = CV for a parallel-plate capacitor"),
    ],
    "stem": "<p>An uncharged, isolated parallel plate capacitor has capacitance <code>C</code>. Monochromatic "
            "light of frequency <code>f</code> is incident on one of the metal plates, which has threshold "
            "frequency <code>f₀</code>. Emitted photoelectrons are then captured by the other plate. Once the "
            "capacitor charge has reached a steady value, how many electrons have been transferred between the "
            "plates? (<code>h</code> is Planck's constant and <code>e</code> is the magnitude of the electron "
            "charge.)</p>",
    "fig": None,
    "opts": ["Ch(f + f₀)/e", "Cf₀(f + f₀)/e²", "Ch(f − f₀)/e", "Cf(f + f₀)/e²", "Ch(f − f₀)/e²"],
    "ans": 4,
    "sol": """<p><b>What is being tested.</b> Two ideas linked by one sentence: the capacitor stops collecting charge when its own voltage is high enough to stop the fastest photoelectrons, and the number of electrons is the charge divided by <code>e</code> — not the charge itself.</p>
<p><b>Step 1 — when does the flow stop?</b> As electrons accumulate on the far plate, that plate goes negative relative to the illuminated one, and the potential difference opposes further electrons. The flow stops when the potential difference is exactly the stopping potential for the most energetic electrons:</p>
<div class="formula">eV_s = hf − hf₀ = h(f − f₀)
V_s = h(f − f₀) / e</div>
<p><b>Step 2 — the steady charge on the plates.</b> When the p.d. across the capacitor reaches <code>V_s</code>,</p>
<div class="formula">Q = C V_s = C h (f − f₀) / e</div>
<p><b>Step 3 — turn charge into a number of electrons.</b> Each electron carries charge <code>e</code>, so</p>
<div class="formula">N = Q / e = C h (f − f₀) / e²</div>
<p><b>Answer: E, Ch(f − f₀)/e².</b></p>
<p><b>Check the dimensions — five options, and only one survives.</b> A capacitance has units of <code>C V⁻¹</code>, and since <code>1 V = 1 J C⁻¹</code> we can write <code>F = C² J⁻¹</code>. Meanwhile <code>hf</code> is an energy, so <code>h(f − f₀)</code> has units of J. Therefore</p>
<div class="formula">[C h(f − f₀)] = (C² J⁻¹)(J) = C²        ⇒ [C h(f − f₀) / e²] = dimensionless ✔</div>
<p>A number of electrons has to be dimensionless, and E is the only option that is. Option C comes out with units of <code>C²/C = C</code> — a charge, which is what option C in fact is: it is <code>Q</code>, the charge on the plates, one step short of the answer.</p>
<p><b>Where the wrong options come from.</b> A and C add the two frequencies instead of subtracting — but the photoelectric effect is about the <i>excess</i> above the threshold, so a sum has no meaning here. B and D lose the Planck constant altogether: an answer containing no <code>h</code> cannot depend on the energy of the photon, and the whole physical content of the question is that it does. D also uses <code>f(f + f₀)</code>, mixing a frequency with a squared frequency against an <code>e²</code> — it fails the dimensional check twice over.</p>
<p><b>The trap worth naming.</b> The difference between C and E is a single division by <code>e</code>, and it is the difference between “charge” and “number of electrons”. Read the question's last word. Whenever a question ends with “how many electrons”, “how many photons” or “how many particles”, expect the answer to require a division by the charge or the energy of one particle.</p>
<p><b>The wider point about this combination.</b> Round 0 likes questions where two standard pieces of Year 12 physics meet — here the photoelectric effect and a capacitor. Neither part is hard; the mark is for noticing that the second part exists. Sketch the setup: light in, electrons out of one plate, onto the other, and the capacitor voltage grows until it forbids any more. That picture gives the sequence of the three steps above without any algebra.</p>
<p><b>Relevant topics:</b> the photoelectric effect; stopping potential and the threshold frequency; <code>Q = CV</code>; dimensional checking.</p>""",
    "trap": "Stopping at <code>Ch(f − f₀)/e</code> — that is the charge on the plates. The question asks how many electrons, so divide by <code>e</code> once more.",
},

{
    "id": "R0-18", "n": 18, "module": "B", "topic": "Ranges at complementary angles", "diff": 3,
    "rel": [
        ("B", "Projectile range and the 45° maximum"),
        ("A", "Small-angle approximations — and knowing when they are unnecessary"),
        ("A", "Turning points: why a first-order change can vanish"),
    ],
    "stem": "<p>Two particles are projected from ground level at the same speed <code>v</code>, but at two different "
            "angles to the horizontal: <code>(π/4 + α)</code> and <code>(π/4 − α)</code>, where <code>α</code> "
            "itself is a small angle in radians. Find the difference between the horizontal ranges of the two "
            "particles.</p>",
    "fig": None,
    "opts": ["0", "αv²/g", "2αv²/g", "αv²/(2g)", "4αv²/g"],
    "ans": 0,
    "sol": """<p><b>What is being tested.</b> Whether you reach for the small-angle approximations because the question offers <code>α ≪ 1</code>, or whether you notice that the answer is exactly zero and no approximation can improve on it.</p>
<p><b>Step 1 — write the range.</b> For a projectile launched and landing at the same height,</p>
<div class="formula">R = v² sin 2θ / g</div>
<p><b>Step 2 — double both angles.</b> The doubling is where the question is won:</p>
<div class="formula">2(π/4 + α) = π/2 + 2α
2(π/4 − α) = π/2 − 2α</div>
<p><b>Step 3 — use the complementary-angle identity.</b></p>
<div class="formula">sin(π/2 + 2α) = cos 2α
sin(π/2 − 2α) = cos 2α</div>
<p>Both ranges are <code>v² cos 2α / g</code>. Their difference is zero.</p>
<p><b>Answer: A, 0.</b> And note the scope: this is not an approximation and it is not particular to small <code>α</code>. The two angles are complementary to 45°, and for any two angles that add to 90° the ranges are equal — that is one of the classic projectile results, and here it is being exploited with <code>α</code> small merely to make the pairs look less obviously related.</p>
<p><b>Why the answer is exactly zero — the calculus reading.</b> The range is stationary at 45°:</p>
<div class="formula">dR/dθ = (2v² / g) cos 2θ,  which is zero at θ = 45°</div>
<p>Because the top of the range-versus-angle curve is flat at 45°, moving the launch angle by <code>±α</code> changes the range only at order <code>α²</code> — and the two shifts give the same quadratic correction, so even that cancels. Nothing linear in <code>α</code> can appear.</p>
<p><b>That single observation kills four options at once.</b> Options B, C, D and E are all proportional to <code>α</code> — first order in <code>α</code>. Since the range has a flat maximum at 45°, a first-order change is impossible, and all four must be wrong. On a question like this, the shape of the answer is enough; you do not need to do the algebra at all.</p>
<p><b>Where they come from, and why the paper put the approximations in the data sheet.</b> The formula sheet offers <code>sin θ ≈ θ</code>, <code>cos θ ≈ 1 − θ²/2</code> and the binomial approximations. A tempting route is to expand <code>v² sin 2θ / g</code> in <code>α</code>; done carelessly — replacing <code>cos 2θ</code> by 1 when differentiating, or keeping only one of the two shifts — it produces <code>2αv²/g</code>, <code>4αv²/g</code> and their halves, which is exactly the wrong-option set. The approximations are on the sheet because other questions need them; the skill here is noticing that this one does not.</p>
<p><b>The habit this question rewards.</b> When a formula contains a special angle — 45°, 30°, <code>π/4</code> — look for the symmetry or the stationary point before you expand. One line of trigonometry beat a page of approximation, and the answer is exact rather than approximate.</p>
<p><b>Relevant topics:</b> projectile range; the 45° maximum; stationary points; when not to use the small-angle approximations.</p>""",
    "trap": "Expanding in α and picking a first-order term. The range is stationary at 45°, so the difference is exactly zero — options B, C, D and E are all linear in α and all impossible.",
},

{
    "id": "R0-19", "n": 19, "module": "K", "topic": "Time for one third to decay", "diff": 2,
    "rel": [
        ("K", "Exponential decay and the half-life"),
        ("K", "Half-life from data"),
        ("A", "Logarithms without a calculator"),
    ],
    "stem": "<p>The half-life of a radioactive substance is <code>T</code>. What is the time taken for one third "
            "of the substance to decay?</p>",
    "fig": None,
    "opts": ["(2/3) T", "√(2/3) · T", "T log₂(3/2)", "T log₂(3)", "T^(2/3)"],
    "ans": 2,
    "sol": """<p><b>What is being tested.</b> Whether you read “one third decays” as “two thirds remain” — the single sentence that decides the question — and whether you can handle a logarithm with no calculator.</p>
<p><b>Step 1 — restate what is left.</b></p>
<div class="formula">one third decayed   ⇒   1 − 1/3 = 2/3 remains</div>
<p><b>Step 2 — apply the decay law.</b> After time <code>t</code> the fraction remaining is <code>(1/2)^(t/T)</code>:</p>
<div class="formula">(1/2)^(t/T) = 2/3</div>
<p><b>Step 3 — take logs of both sides.</b></p>
<div class="formula">(t/T) log 2 = log(2/3)     … taking logs and using log(1/2) = −log 2
t / T = log(3/2) / log 2
t = T log₂(3/2)</div>
<p><b>Answer: C, T log₂(3/2).</b></p>
<p><b>Read the answer to check it — by bounding, not by calculating.</b> You cannot evaluate
<code>log₂3</code> without a calculator, and you do not need to. Trap 3 between two powers of 2 you can
compute in your head:</p>
<div class="formula">2^1.5 = 2 × √2 = 2 × 1.414 = 2.83 &lt; 3 &lt; 2^2 = 4
=&gt;   1.5 &lt; log₂3 &lt; 2
=&gt;   0.5 &lt; log₂3 − 1 &lt; 1
=&gt;   0.5 &lt; log₂(3/2) &lt; 1,   so  t is between 0.5T and 1T</div>
<p>That is exactly what the physics demands: less than half the substance has decayed, so less than one
half-life has elapsed — and more than none has, so more than zero. The bounds give you the answer's
<i>whereabouts</i>, which is all a multiple-choice question ever asks for. (For the record
<code>log₂3 = 1.585</code> and <code>t = 0.585T</code>, but note that no step above needed either number.)</p>
<p><b>Why the other options are wrong.</b> A, <code>(2/3)T</code>, assumes the decay is linear in time — at <code>t = (2/3)T</code> it would have the substance decaying at a constant rate, which is not what radioactive decay does. D, <code>T log₂3</code> (a little under <code>2T</code>, by the bound above), is the answer to a different question: it is the time for two thirds to have decayed, i.e. one third remaining, because it comes from <code>(1/2)^(t/T) = 1/3</code>. That is the single most common slip here, and it is why the question says “one third decay” rather than “one third remaining”. E, <code>T^(2/3)</code>, is dimensionally impossible — a half-life raised to a power is not a time — so it dies on inspection. B, <code>√(2/3) T ≈ 0.82T</code>, is a third plausible-looking number with no derivation behind it; you cannot get a square root out of an exponential decay law.</p>
<p><b>Carry the general form.</b> If a fraction <code>f</code> remains,</p>
<div class="formula">t = T log₂(1/f)</div>
<p>Check it on two cases you know by heart: <code>f = 1/2</code> gives <code>t = T log₂2 = T</code> ✔, and <code>f = 1/4</code> gives <code>2T</code> ✔. A general formula that reproduces the standard cases is worth remembering, and these two are the ones it will be tested against.</p>
<p><b>How to do <code>log₂(3/2)</code> without a calculator.</b> Split it: <code>log₂(3/2) = log₂3 − 1</code>, and <code>log₂3</code> is between <code>log₂2 = 1</code> and <code>log₂4 = 2</code>, closer to 1.5 than to 2 — so 0.585 is plausible before you compute anything. If the options had required the value rather than the expression, that bracket would be enough to choose.</p>
<p><b>Relevant topics:</b> exponential decay; half-life; the decay law in index form; logarithms.</p>""",
    "trap": "Reading one third decayed as one third remaining and answering <code>T log₂3 ≈ 1.6T</code>. Two thirds remains, so <code>t = T log₂(3/2)</code>, which the bounds put between <code>0.5T</code> and <code>1T</code> — less than a half-life is wrong; <i>under one</i> half-life is right.",
},

{
    "id": "R0-20", "n": 20, "module": "C", "topic": "Jerk of a bungee jumper against time", "diff": 3,
    "rel": [
        ("C", "Newton's second law, including a spring force"),
        ("C", "Hooke's law and the onset of simple harmonic motion"),
        ("A", "Reasoning about graph shape: jumps, turning points, limits"),
    ],
    "stem": "<p>Jerk is defined as the rate of change of acceleration with respect to time, <code>j = da/dt</code>.</p>"
            "<p>A bungee jumper attached to a slack rope falls from a height. Once the rope is taut, it acts as an "
            "ideal spring which subsequently brings the jumper to instantaneous rest. Which of the following "
            "graphs shows the jerk <code>j</code> as a function of time <code>t</code>, up to this moment?</p>",
    "fig": None,
    "opts": ["{{FIG:r0-20-A}}", "{{FIG:r0-20-B}}", "{{FIG:r0-20-C}}", "{{FIG:r0-20-D}}", "{{FIG:r0-20-E}}"],
    "ans": 3,
    "sol": """<p><b>What is being tested.</b> The shape of a graph you have never seen before, built from two pieces of ordinary physics: free fall, then a spring. Every wrong option breaks one specific feature of that shape, so the method is to establish the features first.</p>
<p><b>Phase 1 — the rope is slack.</b> The jumper is in free fall, so <code>a = g</code>, a constant. Therefore</p>
<div class="formula">j = da/dt = 0          all the way through phase 1</div>
<p><b>The moment the rope goes taut.</b> This is the key instant, and the dashed line in options A, D and E marks it. At that instant the extension is zero, so the spring force is zero, and the acceleration is still <code>g</code> — the acceleration itself is continuous. But from that instant the acceleration begins to change, so the jerk jumps <b>discontinuously</b> from 0 to a finite value.</p>
<p><b>That one sentence removes options B and C.</b> Both of them leave the origin of jerk at zero at the moment the rope goes taut, which would mean the jumper's acceleration carries on unchanged even though a spring has just started pulling on it. And C is piecewise straight, which would require the acceleration to change quadratically with time — a linear jerk is not what a spring produces.</p>
<p><b>Phase 2 — the rope stretches.</b> Take downwards as positive and let <code>x</code> be the extension:</p>
<div class="formula">ma = mg − kx      ⇒      a = g − ω² x,   ω² = k/m
j = da/dt = −ω² v</div>
<p>So the jerk is proportional to the jumper's speed (with a minus sign, i.e. it acts to reduce the acceleration).</p>
<p><b>What does the speed do just after the rope goes taut?</b> At that instant the acceleration is <code>g</code>, still downwards, so the jumper is <i>still speeding up</i>. The speed keeps growing for a moment. Therefore <code>|j| ∝ v</code> grows too: the curve must <b>rise</b> before it falls. This is the feature that separates D from E.</p>
<p><b>How the phase ends.</b> The jumper's speed peaks when the acceleration passes through zero — at the equilibrium position of the oscillation that follows — and then decreases. The phase ends at the lowest point, where the jumper is instantaneously at rest:</p>
<div class="formula">v = 0  ⇒  j = −ω² v = 0</div>
<p>So the curve must come back to exactly zero at the end, and it never changes sign in between, because the velocity is always downwards.</p>
<p><b>Answer: D</b> — the graph that jumps to a finite value at the dashed line, rises to a rounded maximum, and returns smoothly to zero.</p>
{{FIG:r0-20-sol}}
<p><b>Why E is wrong even though it has the jump.</b> E starts at a high value at the dashed line and decays steadily towards the axis. It is missing the initial rise — and, more fundamentally, a monotonic decay of that kind is the signature of an exponential, which comes from a first-order process. The motion after the rope goes taut is simple harmonic, whose speed is a sinusoid, so the jerk must rise to a maximum and return to zero at a definite time, not creep towards the axis.</p>
<p><b>Why A is wrong.</b> A jumps and then falls to zero in a straight line, so the jerk would be linear in time. Since <code>j ∝ v</code>, that would force the speed to be linear in time — constant acceleration — which is the opposite of what a spring does.</p>
<p><b>The method for any “which graph” question.</b> Do not try to plot the function. Instead, list the features the correct graph must have and test each option against them:</p>
<div class="formula">1. flat at zero during free fall                        (all five pass)
2. a jump, not a smooth start, at the rope's tautness   (removes B, C)
3. an initial rise before the fall                      (removes E, A)
4. a return to exactly zero at instantaneous rest       (removes E)</div>
<p>Four features, and each option fails at a named one. That is worth more than any amount of sketching, and it is how this question is meant to be answered in the two and a half minutes available.</p>
<p><b>Relevant topics:</b> Newton's second law with a spring; Hooke's law; the onset of simple harmonic motion; graph-shape reasoning; rates of change.</p>""",
    "trap": "Assuming the jerk is zero when the rope goes taut because the acceleration is momentarily unchanged. The acceleration is continuous, but its <i>rate of change</i> jumps — that is the whole point of the question.",
},

]
