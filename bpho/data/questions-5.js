/* BPhO Round 0 — the 2025 SAMPLE QUESTIONS (S1..S12), rebuilt 2026-09-18.
   The sheet BPhO publishes so candidates can see the style before sitting the paper.
   Twelve single-answer MCQs, non-calculator, no negative marking -- the same format as
   the real thing, just shorter.

   There is no printed answer key for these, so every answer below was derived
   independently and cross-checked against the printed figure. Four of the twelve are
   only decidable from the drawing: the polarity of both cells in S3, the exponent in
   S6, where the extra load sits in S7, and the curvature in S8. Each of those is
   explained inside its own worked solution.

   `rel` lists the modules and topics each question draws on, `key` names the key
   points it turns on (lessons in data/concepts.js), and `paper:"R0-SAMPLE"` lets
   `startMockPaper("R0-SAMPLE", mode)` rebuild the sheet in order.

   Diagrams are inline SVG generated from measured geometry in tools/r0sample/figs.py,
   not traced by hand. */

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([

/* ===================== 2025 Round 0 sample questions ===================== */
/* Derived key:  B B A B B D D E E B B D   (no C -- a 12-question sample has no
   obligation to be uniform; see tools/r0sample/build.py gate 6)  */

{
  id: "R0S-01", module: "K", topic: "Nuclide notation: which of these two nuclei are alike?", diff: 1, paper: "R0-SAMPLE",
  rel: [
    ["K", "Nuclide notation A over Z, and what each number counts"],
    ["K", "Neutron number N = A − Z"],
    ["A", "Comparing two expressions exactly, not approximately"]
  ],
  key: ["nuclide", "ratio", "nocalc"],
  q: `<p>Two nuclei, <sup>3x</sup><sub>2x</sub>Q and <sup>4x</sup><sub>3x</sub>R (<code>x</code> is an integer), have the same:</p>`,
  opts: [`specific charge`, `neutron number`, `proton number`, `mass`, `radius`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> Whether you can read the two numbers in a nuclide symbol and say what each one counts. Nothing here needs arithmetic beyond a subtraction.</p>
<p><b>Step 1 — decode the notation.</b> In the symbol <sup>A</sup><sub>Z</sub>X the superscript is the <b>mass number</b> <code>A</code> — the total count of protons and neutrons — and the subscript is the <b>proton number</b> <code>Z</code>. So the two nuclei are:</p>
<div class="formula">Q:  A = 3x,  Z = 2x
R:  A = 4x,  Z = 3x</div>
<p><b>Step 2 — the neutron number is the difference.</b> Neutrons are the nucleons that are not protons, so</p>
<div class="formula">N = A − Z
Q:  N = 3x − 2x = x
R:  N = 4x − 3x = x</div>
<p>Both come to exactly <code>x</code>. They are equal for <i>every</i> integer <code>x</code>, which is why the question can be answered without ever knowing what <code>x</code> is.</p>
<p><b>Step 3 — eliminate the other four.</b> Each one either fails outright or is merely close:</p>
<p>· <b>Proton number</b> is <code>Z</code>, which is <code>2x</code> against <code>3x</code>. Different.</p>
<p>· <b>Mass</b> is carried almost entirely by the nucleons, so it tracks <code>A</code>: <code>3x</code> against <code>4x</code>. Different.</p>
<p>· <b>Radius</b> follows <code>R ∝ A<sup>1/3</sup></code>, so it follows the cube root of <code>3x</code> against the cube root of <code>4x</code>. Different.</p>
<p>· <b>Specific charge</b> is charge divided by mass. Each proton carries <code>+e</code> and each nucleon contributes about the same mass, so specific charge is proportional to <code>Z/A</code>:</p>
<div class="formula">Q:  Z/A = 2x/3x = 2/3 = 8/12
R:  Z/A = 3x/4x = 3/4 = 9/12</div>
<p>Over a common denominator it is plain that these are not equal — but they are uncomfortably close, which is exactly why this option is on the paper.</p>
<p><b>Answer: B, neutron number.</b></p>
<p><b>The trap.</b> <code>2/3</code> and <code>3/4</code> both look like "about 0.7", and a candidate who rounds before comparing will pick specific charge. Over a common denominator, <code>8/12</code> and <code>9/12</code> are obviously different numbers. The lesson generalises: when two options differ by less than the roughness of your mental arithmetic, put them over a common denominator instead of estimating.</p>
<p><b>Do it the fast way.</b> Only one of the five candidates is built from a <i>difference</i> of the two numbers in the symbol. Three of them (<code>Z</code>, <code>A</code>, and the cube root of <code>A</code>) are functions of a single one of the two numbers, and those are all different between Q and R. Spotting that <code>A − Z</code> is the only combination that can cancel the <code>x</code> settles the question without any calculation at all.</p>
<p><b>Relevant topics:</b> nuclide notation; neutron number; specific charge.</p>`,
  trap: "Round <code>2/3</code> and <code>3/4</code> to 'about 0.7' and call the specific charges equal. Over a common denominator they are <code>8/12</code> and <code>9/12</code> — close, but not equal."
},

{
  id: "R0S-02", module: "F", topic: "Counting half-wavelengths on a string with five antinodes", diff: 1, paper: "R0-SAMPLE",
  rel: [
    ["F", "Stationary waves on a string fixed at both ends"],
    ["F", "Nodes, antinodes and the length of one loop"],
    ["A", "Checking an answer by counting back from it"]
  ],
  key: ["standingwaves", "waves", "ratio"],
  q: `<p>A string has two fixed ends, separated by a distance of 10 m. A stationary wave on the string has five antinodes. What is the wavelength?</p>`,
  opts: [`2 m`, `4 m`, `5 m`, `6 m`, `8 m`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> The single most common slip in standing-wave questions: each <i>loop</i> is half a wavelength, not a whole one.</p>
<p><b>Step 1 — what the ends force.</b> A fixed end cannot move, so it must be a <b>node</b>. With both ends fixed the string carries a whole number of loops, and each loop is one half-wavelength:</p>
<div class="formula">length of one loop = λ/2</div>
<p><b>Step 2 — relate antinodes to loops.</b> Each loop bulges once, and the middle of the bulge is an <b>antinode</b>. So the number of antinodes equals the number of loops. Five antinodes means five loops:</p>
<div class="formula">L = 5 × (λ/2)</div>
<p><b>Step 3 — solve.</b> With <code>L = 10 m</code>:</p>
<div class="formula">10 = 5λ/2   ⇒   λ = 2 × 10 / 5 = 4 m</div>
<p><b>Answer: B, 4 m.</b></p>
<p><b>Check it by going back the other way.</b> If <code>λ = 4 m</code>, one loop is <code>4/2 = 2 m</code> and a 10 m string holds <code>10/2 = 5</code> loops, hence five antinodes. That matches the question, so the answer is consistent.</p>
<p><b>Why the other four are wrong.</b> Option A, 2 m, is the answer you get if you forget the half and write <code>L = 5λ</code> — the loop-then-wrong-length error. The rest are just other numbers. Notice that no option corresponds to counting <i>nodes</i> instead of antinodes: a five-antinode pattern has six nodes, and <code>10/6</code> loops would not give a whole number of loops anyway, which is a useful signal that you have misread the question.</p>
<p><b>The wider point.</b> Every "count the waves" question is a two-step chain: get from what is drawn (nodes, antinodes, loops) to the number of half-wavelengths, then get from that to a length. Write the middle step down explicitly — <code>L = (number of loops) × λ/2</code> — rather than jumping straight to a formula, and the factor of two looks after itself.</p>
<p><b>Relevant topics:</b> stationary waves; nodes and antinodes; conditions at a fixed end.</p>`,
  trap: "Treating each antinode as a whole wavelength and writing <code>L = 5λ</code>, which gives 2 m. Five antinodes means five half-wavelengths."
},

{
  id: "R0S-03", module: "H", topic: "Two cells and two resistors sharing a zero-resistance link", diff: 2, paper: "R0-SAMPLE",
  rel: [
    ["H", "EMF, terminal potential difference and cells in series"],
    ["H", "Kirchhoff's laws and node potentials"],
    ["H", "How a zero-resistance wire ties two points to the same potential"]
  ],
  key: ["kirchhoff", "networks", "seriesparallel", "readdiagram"],
  q: `<p>Calculate the current labelled <code>I</code> in the circuit below.</p><figure class="fig">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 246 116" role="img" aria-label="A circuit: a 3.0 volt cell in series with a 6.0 volt cell along the top wire, both with their long positive plate on the left, two 6.0 ohm resistors in the outer branches, and a plain wire linking the junction between the two cells to the return wire. The current I flows down that link.">
<g transform="translate(-182,-316)">
<defs>
<marker id="s3-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
</defs>
<g stroke="#14181f" stroke-width="2" fill="none">
<line x1="231" y1="345.1" x2="266.3" y2="345.1"/>
<line x1="270.7" y1="345.1" x2="306" y2="345.1"/>
<line x1="306" y1="345.1" x2="341.3" y2="345.1"/>
<line x1="345.7" y1="345.1" x2="381" y2="345.1"/>
<line x1="231" y1="420.1" x2="381" y2="420.1"/>
<line x1="306" y1="345.1" x2="306" y2="420.1"/>
</g>
<g stroke="#14181f" stroke-width="2.4">
<line x1="266.3" y1="337.6" x2="266.3" y2="352.6"/>
<line x1="270.7" y1="341.3" x2="270.7" y2="348.8"/>
<line x1="341.3" y1="337.6" x2="341.3" y2="352.6"/>
<line x1="345.7" y1="341.3" x2="345.7" y2="348.8"/>
</g>
<g stroke="#14181f" stroke-width="2" fill="none">
<line x1="231" y1="345.1" x2="231" y2="367.6"/>
<line x1="231" y1="397.6" x2="231" y2="420.1"/>
<line x1="381" y1="345.1" x2="381" y2="367.6"/>
<line x1="381" y1="397.6" x2="381" y2="420.1"/>
</g>
<rect x="225" y="367.6" width="12" height="30" fill="#e8eefc" stroke="#14181f" stroke-width="2"/>
<rect x="375" y="367.6" width="12" height="30" fill="#e8eefc" stroke="#14181f" stroke-width="2"/>
<circle cx="306" cy="345.1" r="2.6" fill="#14181f"/>
<circle cx="306" cy="420.1" r="2.6" fill="#14181f"/>
<line x1="306" y1="392" x2="306" y2="409" stroke="#b3352f" stroke-width="2" marker-end="url(#s3-ar)"/>
<text x="269.1" y="330.8" font-size="11" text-anchor="middle" fill="#14181f">3.0 V</text>
<text x="344.8" y="330.8" font-size="11" text-anchor="middle" fill="#14181f">6.0 V</text>
<text x="216.7" y="385.6" font-size="11" text-anchor="end" fill="#14181f">6.0 &#937;</text>
<text x="393.6" y="385.6" font-size="11" fill="#14181f">6.0 &#937;</text>
<text x="307.9" y="390.3" font-size="12" fill="#b3352f" font-weight="bold">I</text>
</g>
</svg>
</figure>`,
  opts: [`0.50 A`, `0.75 A`, `1.0 A`, `1.5 A`, `3.0 A`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> A plain wire has no resistance, so it has no potential difference along it. That single fact ties the top junction to the bottom wire and turns one complicated network into two independent loops.</p>
<p><b>Step 1 — read the drawing before doing any algebra.</b> Both cells sit in the top wire, with the link between them. Each cell is drawn the standard way: a <b>long</b> plate for the positive terminal and a <b>short</b> plate for the negative one. In this figure the long plate of each cell is on its <i>left</i> side, so both cells push conventional current leftwards along the top wire. The two 6.0 Ω resistors are in the outer branches, and the link is a bare wire.</p>
<p><b>Step 2 — the link forces two nodes to the same potential.</b> Call the top junction <code>J</code> and the point where the link meets the return wire <code>M</code>. The link is a plain wire, so there is no potential difference along it:</p>
<div class="formula">V(J) = V(M)</div>
<p><b>Step 3 — the left loop on its own.</b> The 3.0 V cell's positive plate is wired to the top-left corner and its negative plate to <code>J</code>. So the top-left corner sits 3.0 V above <code>J</code>. The left resistor runs from that corner down to the return wire, which is at <code>V(M)</code> — and <code>V(M) = V(J)</code>. The whole 3.0 V therefore appears across the left 6.0 Ω resistor, and by Ohm's law:</p>
<div class="formula">I(left branch) = 3.0 V / 6.0 Ω = 0.50 A,  flowing down the left branch</div>
<p><b>Step 4 — the right loop on its own, by the same argument.</b> The 6.0 V cell's negative plate is wired to the top-right corner, so the top-right corner sits 6.0 V <i>below</i> <code>J</code>. Across the right 6.0 Ω resistor:</p>
<div class="formula">I(right branch) = 6.0 V / 6.0 Ω = 1.0 A,  flowing up the right branch</div>
<p><b>Step 5 — add the two contributions in the link.</b> This is the step that decides the question. Follow the currents round:</p>
<p>· The left loop drives its 0.50 A <i>up</i> the link, because its current returns to the cell's negative plate through <code>J</code>.</p>
<p>· The right loop drives its 1.0 A <i>down</i> the link, because its cell pushes current out of its positive plate towards <code>J</code> and then down.</p>
<p>The two loops oppose each other in the link, so the link carries the <b>difference</b>:</p>
<div class="formula">I(link) = 1.0 A − 0.50 A = 0.50 A,  downwards</div>
<p>which is the direction the printed arrow points.</p>
<p><b>Answer: A, 0.50 A.</b></p>
<p><b>Check it with Kirchhoff's first law at the top junction.</b> Current arriving from the right is 1.0 A. Current leaving down the link is 0.50 A. The remaining 0.50 A must leave leftwards along the top wire into the 3.0 V cell's negative plate — and that is exactly the 0.50 A circulating round the left loop. The books balance, so nothing has been double-counted.</p>
<p><b>Why the other four are wrong.</b> Option D, 1.5 A, is the sum of the two branch currents — what you get if you assume both loops drive the link the same way, which the cell polarities forbid. Option E, 3.0 A, comes from dividing the 6.0 V cell by the <i>wrong</i> resistor, or from treating the two 6.0 Ω resistors as a single 2.0 Ω combination in series with both cells. Option C, 1.0 A, is the right-hand branch current alone — right number, wrong question, because it ignores the left loop entirely. Option B, 0.75 A, is the mean of the two branch currents, which has no physical meaning here.</p>
<p><b>The trap.</b> Subtracting the two emfs as <code>6.0 − 3.0 = 3.0 V</code> and then writing <code>3.0/6.0 = 0.50 A</code> reaches the right answer for the wrong reason: the link current is a difference, but of the two <i>branch currents</i> <code>1.0 − 0.50</code>, not of the two voltages. Those two recipes happen to coincide only because both resistors are equal. Change either resistor and the voltage-difference method gives a wrong answer while the branch-current method still works.</p>
<p><b>The transferable rule.</b> Resolve a circuit with a bare wire in it in three moves: mark the nodes the wire joins as one node, find each loop's current from its own emf and its own resistance, then add the loop currents where they share a wire — with their signs, because they may well oppose.</p>
<p><b>Relevant topics:</b> EMF and terminal potential difference; Kirchhoff's first law; cells in series; circuit node potentials.</p>`,
  trap: "Adding the two loop currents in the link to get 1.5 A. Both cells have their long plate on the same side, so they oppose in the link and the currents subtract."
},

{
  id: "R0S-04", module: "G", topic: "Fringe spacing when the whole double-slit apparatus goes under water", diff: 1, paper: "R0-SAMPLE",
  rel: [
    ["G", "Two-source interference and the fringe spacing λD/d"],
    ["G", "Refractive index: what changes and what does not when light enters a medium"],
    ["F", "Frequency is set by the source and does not change at a boundary"]
  ],
  key: ["superposition", "refractive", "ratio", "nocalc"],
  q: `<p>A double-slit diffraction experiment, using monochromatic light, is carried out in air and the fringe spacing <code>w</code> on a distant screen is measured. An identical experiment is set up under still water, which has refractive index <code>n</code>.</p><p>What is the fringe spacing that is measured on the underwater screen?</p>`,
  opts: [`w / n²`, `w / n`, `w`, `nw`, `n²w`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> What actually changes when light enters a denser medium. Almost everyone remembers "the wavelength changes". The question is whether you also remember that the <i>frequency</i> does not — and whether you know which of the two the fringe spacing depends on.</p>
<p><b>Step 1 — quote the fringe spacing.</b> For two slits a distance <code>d</code> apart, viewed on a screen a distance <code>D</code> away:</p>
<div class="formula">w = λD / d</div>
<p>The geometry does not change here: it is the same apparatus, so <code>d</code> and <code>D</code> are the same. Everything therefore depends on what happens to <code>λ</code>.</p>
<p><b>Step 2 — at a boundary the frequency stays put.</b> The frequency of a wave is fixed by its source: the wave arrives at the water surface with the same number of oscillations per second as it left the lamp with. If it did not, wave crests would pile up or vanish at the surface, and they do not. So</p>
<div class="formula">f(water) = f(air) = f</div>
<p><b>Step 3 — but the speed drops, so the wavelength must drop too.</b> The refractive index is defined as the ratio of the speeds:</p>
<div class="formula">n = c / v   ⇒   v = c / n</div>
<p>Since <code>v = fλ</code> and <code>f</code> is unchanged, halving the speed must halve the wavelength:</p>
<div class="formula">λ(water) = v / f = c / (n f) = λ(air) / n</div>
<p><b>Step 4 — put it back into the fringe spacing.</b> With <code>D</code> and <code>d</code> unchanged:</p>
<div class="formula">w(water) = λ(water) D / d = (λ(air)/n) D / d = w / n</div>
<p><b>Answer: B, w / n.</b></p>
<p><b>Why the other four are wrong.</b> Option D, <code>nw</code>, and option E, <code>n²w</code>, have the spacing <i>growing</i> — that is what would happen if the wavelength grew, which it cannot when the wave slows down. Option C, <code>w</code>, would need the wavelength to be unaffected, which would mean the speed was unaffected, contradicting <code>n = c/v</code>. Option A, <code>w/n²</code>, over-corrects: it is what you get by shrinking the wavelength once <i>and</i> shrinking something else along the way, for instance by also dividing the slit separation by <code>n</code> — but <code>d</code> is a distance between slits in the apparatus, not a wavelength, and water does not shrink it.</p>
<p><b>Check the shape of the answer.</b> Put <code>n = 1</code>: the formula gives <code>w</code>, which must be right because <code>n = 1</code> <i>is</i> air. So the correct option has to reduce to <code>w</code> at <code>n = 1</code>; A, B and C all do, and that kills D and E immediately. Then require the spacing to shrink for <code>n &gt; 1</code>, which leaves only <code>w/n</code>.</p>
<p><b>The wider point.</b> Everything about refraction follows from two rules that are worth stating together: the frequency never changes at a boundary, and the speed does. Every other quantity — wavelength, fringe spacing, angle — follows from those two.</p>
<p><b>Relevant topics:</b> two-source interference; fringe spacing; refractive index; the wave equation.</p>`,
  trap: "Multiplying by <code>n</code> instead of dividing. Water makes the light slower, so its wavelength <i>shrinks</i> and the fringes get closer together."
},

{
  id: "R0S-05", module: "H", topic: "Power in one resistor: same two resistors in series, then in parallel", diff: 2, paper: "R0-SAMPLE",
  rel: [
    ["H", "EMF and internal resistance: terminal voltage and lost volts"],
    ["H", "Resistors in series and in parallel"],
    ["H", "Power dissipated in a resistor"]
  ],
  key: ["resistance", "seriesparallel", "ratio", "nocalc"],
  q: `<p>A cell of internal resistance <code>r</code> is connected across two identical resistors, each of resistance <code>4r</code>, in series. The power dissipated in one of the resistors is <code>P<sub>1</sub></code>. The cell is removed and connected across the same two resistors, but this time they are in parallel. The power dissipated in one of the resistors is now <code>P<sub>2</sub></code>.</p><p>Find <code>P<sub>1</sub> / P<sub>2</sub></code>.</p>`,
  opts: [`1`, `4 / 9`, `9 / 16`, `3 / 4`, `16 / 81`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> Whether you keep the internal resistance in the circuit. It is the only other resistance there is, and dropping it changes the answer.</p>
<p>Call the cell's emf <code>E</code>. It is not given and never needs to be: it cancels. The internal resistance <code>r</code>, on the other hand, does <i>not</i> cancel, so carry it through both parts.</p>
<p><b>Part 1 — in series.</b> The two 4<code>r</code> resistors and the internal resistance are all in one loop:</p>
<div class="formula">R(total) = r + 4r + 4r = 9r
I = E / 9r</div>
<p>Both resistors carry this same current, so the power in one of them is</p>
<div class="formula">P₁ = I² × 4r = (E/9r)² × 4r = 4E² / (81r)</div>
<p><b>Part 2 — in parallel.</b> Two identical 4<code>r</code> resistors in parallel are equivalent to half of one:</p>
<div class="formula">4r in parallel with 4r = 4r / 2 = 2r
R(total) = r + 2r = 3r
I = E / 3r</div>
<p>The whole of that current passes through the internal resistance and then splits between the two branches. What both branches share is the <b>voltage</b> across them, so get that first:</p>
<div class="formula">V(across the pair) = I × 2r = (E/3r) × 2r = 2E / 3</div>
<p>Now the power in one resistor is <code>V²/(4r)</code>:</p>
<div class="formula">P₂ = (2E/3)² / (4r) = (4E²/9) / (4r) = E² / (9r)</div>
<p><b>Step 3 — take the ratio.</b></p>
<div class="formula">P₁ / P₂ = [4E² / (81r)] ÷ [E² / (9r)] = (4/81) × 9 = 36/81 = 4/9</div>
<p><b>Answer: B, 4/9.</b></p>
<p><b>Cross-check P₂ a second way.</b> In the parallel case each resistor carries half the total current, <code>E/(6r)</code>. Then <code>P₂ = (E/6r)² × 4r = 4E²/(36r) = E²/(9r)</code>, the same as before. Two independent routes to the same value is the standard guard against a slip in the algebra.</p>
<p><b>Why the other four are wrong.</b> Work out what each represents. <code>9/16</code> is <code>(3/4)²</code>, which is what you get by comparing the two <i>total</i> currents squared and forgetting that the parallel pair splits the current; <code>3/4</code> is that comparison without squaring; <code>1</code> would mean the rearrangement changed nothing, which it plainly does; and <code>16/81</code> is <code>(4/9)²</code> — treating the first ratio as if it were a current ratio and squaring the whole thing again.</p>
<p><b>The trap.</b> Drop <code>r</code> and you would get a series current <code>E/8r</code> giving <code>P₁ = E²/(16r)</code>, and a parallel case where the full <code>E</code> appears across the pair giving <code>P₂ = E²/(4r)</code>. The ratio would then be <code>1/4</code> — which is not among the options. That is a useful signal: the paper is telling you, through its own option list, that the internal resistance is essential to this question.</p>
<p><b>The wider point.</b> In a series chain every element carries the same current, so compute power as <code>I²R</code>. In parallel branches every element has the same voltage across it, so compute power as <code>V²/R</code>. Choosing the wrong one of those two is where most of the marks in this question are lost.</p>
<p><b>Relevant topics:</b> internal resistance; series and parallel combinations; electrical power.</p>`,
  trap: "Leaving the internal resistance out. Keeping it gives <code>4/9</code>; dropping it would give <code>1/4</code>, which is not even on the list."
},

{
  id: "R0S-06", module: "I", topic: "Which combination of units is a farad?", diff: 2, paper: "R0-SAMPLE",
  rel: [
    ["I", "Capacitance and the farad: charge stored per unit potential difference"],
    ["A", "Reducing a compound unit to base SI units"],
    ["A", "Using units to eliminate options"]
  ],
  key: ["capacitors", "units", "dimensions"],
  q: `<p>Which one of the following is a unit of capacitance?</p><p><i>[Hint: capacitance is the charge stored per unit potential difference.]</i></p>`,
  opts: [`V m<sup>−1</sup>`, `C² N<sup>−1</sup>`, `V² s J<sup>−1</sup>`, `s Ω<sup>−1</sup>`, `A² s³ J<sup>−1</sup>`],
  ans: 3,
  sol: `<p><b>What is being tested.</b> Not memorising a list of farad-alikes, but being able to reduce a compound unit you have never seen to something you recognise. The hint is deliberately enough on its own.</p>
<p><b>Step 1 — write the definition as units.</b> Capacitance is charge per unit potential difference, so</p>
<div class="formula">1 farad = 1 coulomb per volt = C / V</div>
<p>Every correct option must be identical to <code>C/V</code>. Take them one at a time.</p>
<p><b>Option A, V m<sup>−1</sup>.</b> Volts per metre is the unit of <i>electric field strength</i>. Not a farad. Gone.</p>
<p><b>Option B, C² N<sup>−1</sup>.</b> Use <code>J = N m</code> to rewrite the farad: <code>C/V = C/(J/C) = C²/J = C²/(N m)</code>. Compare that with <code>C²/N</code>: the option is a farad multiplied by a metre. It differs from a farad by a length, so it is not one. Gone.</p>
<p><b>Option C, V² s J<sup>−1</sup>.</b> Write <code>V = J/C</code>, so <code>V² = J²/C²</code>. Then</p>
<div class="formula">V² s / J = (J²/C²) × s / J = J s / C²</div>
<p>Since <code>1/F = J/C²</code>, this option is <code>s/F</code> — seconds per farad, not farads. Gone.</p>
<p><b>Option D, s Ω<sup>−1</sup>.</b> Resistance is volts per ampere, so <code>Ω<sup>−1</sup> = A/V</code>. Therefore</p>
<div class="formula">s Ω<sup>−1</sup> = s × A / V = (A s) / V = C / V</div>
<p>using the definition of the coulomb as an ampere-second. That is exactly the farad. <b>This one survives.</b></p>
<p><b>Option E, A² s³ J<sup>−1</sup>.</b> Again <code>C = A s</code>, so <code>A² s² = C²</code>, leaving one spare second:</p>
<div class="formula">A² s³ / J = (A² s²) × s / J = C² s / J = F × s</div>
<p>A farad multiplied by a second. The letters are nearly right — the farad is <code>A² s² J<sup>−1</sup></code>, and this option carries <code>s³</code> — but one wrong exponent is enough to make it a different unit entirely. Gone.</p>
<p><b>Answer: D, s Ω<sup>−1</sup>.</b></p>
<p><b>Do it the fast way.</b> You do not need to grind through all five. Ask each option "is this charge divided by potential difference?" Option D is the only one that can be, because <code>Ω<sup>−1</sup></code> is <code>A/V</code> and multiplying by seconds gives <code>A s / V = C/V</code> directly. Start with whichever option has the fewest unfamiliar symbols and work outwards.</p>
<p><b>Why E is worth a second look.</b> It is built to look right: it uses only electrical and mechanical symbols, and it is dimensionally an energy divided by... something. The decisive check is to count the seconds. The farad needs <code>s²</code>; E offers <code>s³</code>. When two options differ only in an exponent, compare the exponents rather than the whole expression.</p>
<p><b>The wider point.</b> The farad, written out in base SI units, is <code>kg<sup>−1</sup> m<sup>−2</sup> s⁴ A²</code>. Nobody memorises that; everybody should be able to derive it from <code>C/V</code> in about three lines. Unit questions are usually a free mark provided you resist the urge to guess.</p>
<p><b>Relevant topics:</b> capacitance; the farad; reducing compound units; dimensional checking.</p>`,
  trap: "Choosing <code>A² s³ J<sup>−1</sup></code> because it is built from the right kind of symbols. The farad is <code>A² s² J<sup>−1</sup></code> — the option has one second too many."
},

{
  id: "R0S-07", module: "C", topic: "Reactions at three rods when a weight is added halfway along an edge", diff: 3, paper: "R0-SAMPLE",
  rel: [
    ["C", "Moments and choosing a good pivot"],
    ["C", "Centre of mass of a uniform triangle"],
    ["C", "Equilibrium of a rigid body under parallel forces"]
  ],
  key: ["moments", "com", "statics", "readdiagram"],
  q: `<p>A uniform rigid metal sheet in the shape of an equilateral triangle has weight <code>W</code> and is supported on horizontal ground by three light inextensible rods of equal length at each of its corners. A weight <code>W</code> (same weight as the sheet) is placed on top of the sheet halfway between two corners, as shown below.</p><p>Find the ratio of reaction forces <code>R : N</code> acting on the rods from the ground.</p><figure class="fig">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 132" role="img" aria-label="A triangular metal sheet seen at an angle, supported at each corner by a rod of equal length, with the reaction arrows drawn pointing up the rods. The two corners on the left and the upper right are labelled R and the lower right corner is labelled N. An unlabelled ring marks the extra load, sitting at the midpoint of the edge that joins the two R corners.">
<g transform="translate(-228,-208)">
<defs>
<marker id="s7-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
</defs>
<polygon points="235,274 377,217 349,303" fill="#e8eefc" stroke="#14181f" stroke-width="2" stroke-linejoin="round"/>
<g stroke="#14181f" stroke-width="2">
<line x1="235" y1="274" x2="235" y2="302.3"/>
<line x1="377" y1="217" x2="377" y2="245.3"/>
<line x1="349" y1="303" x2="349" y2="331.3"/>
</g>
<line x1="235" y1="302.3" x2="235" y2="288" stroke="#2f5fd0" stroke-width="2" marker-end="url(#s7-ar)"/>
<line x1="377" y1="245.3" x2="377" y2="231" stroke="#2f5fd0" stroke-width="2" marker-end="url(#s7-ar)"/>
<line x1="349" y1="331.3" x2="349" y2="317" stroke="#2f5fd0" stroke-width="2" marker-end="url(#s7-ar)"/>
<circle cx="306" cy="245.5" r="4.6" fill="#fdf1e7" stroke="#b3352f" stroke-width="1.8"/>
<text x="381.4" y="235.9" font-size="12" fill="#2f5fd0" font-weight="bold">R</text>
<text x="239.7" y="289.8" font-size="12" fill="#2f5fd0" font-weight="bold">R</text>
<text x="352.3" y="318.1" font-size="12" fill="#2f5fd0" font-weight="bold">N</text>
</g>
</svg>
</figure>`,
  opts: [`5 : 1`, `4 : 1`, `3 : 1`, `5 : 2`, `2 : 1`],
  ans: 3,
  sol: `<p><b>What is being tested.</b> Where you choose to take moments. This question is nearly impossible if you take moments about a corner and very easy if you take them about the right line.</p>
<p><b>Step 1 — set out what carries load.</b> There are two weights, each <code>W</code>, both vertical and both downwards:</p>
<p>· the sheet's own weight, acting at its <b>centre of mass</b>, which for a uniform triangle is the centroid;</p>
<p>· the added weight, acting at the point marked on the diagram, which the stem places halfway between two corners — that is, at the <b>midpoint of one edge</b>.</p>
<p>There are three upward reactions, one per rod. The two rods at the ends of the loaded edge are both labelled <code>R</code>, and the third rod is labelled <code>N</code>.</p>
<p><b>Step 2 — choose the pivot.</b> Take moments about the <i>line of the loaded edge</i> — the line joining the two corners whose rods carry <code>R</code>. Now see what drops out:</p>
<p>· the two reactions <code>R</code> act at points <i>on</i> that line, so their moment arms are zero and they contribute nothing;</p>
<p>· the added weight sits <i>on</i> that line — the midpoint of the edge — so it also contributes nothing.</p>
<p>That is the whole point of the phrase "halfway between two corners". The line only has two things left to balance.</p>
<p><b>Step 3 — the moment balance.</b> Let the triangle have height <code>h</code> measured perpendicular to the loaded edge. The third rod is a distance <code>h</code> from the line, and the centroid of a uniform triangle is one third of the height up from any edge, so its distance is <code>h/3</code>:</p>
<div class="formula">N × h = W × (h/3)
N = W/3</div>
<p><b>Step 4 — vertical equilibrium for R.</b> The total upward force must equal the total weight, and there are two <code>R</code> reactions:</p>
<div class="formula">R + R + N = W + W = 2W
2R = 2W − W/3 = 5W/3
R = 5W/6</div>
<p><b>Step 5 — the ratio.</b></p>
<div class="formula">R : N = 5W/6 : W/3 = 5/6 : 2/6 = 5 : 2</div>
<p><b>Answer: D, 5 : 2.</b></p>
<p><b>Why the two R reactions really are equal.</b> The added weight sits at the midpoint of the edge joining those two corners, so the whole arrangement is symmetric about the perpendicular bisector of that edge — the line from the midpoint through the opposite corner. Reflecting the picture in that line swaps the two <code>R</code> rods and leaves everything else alone, so their forces must be equal. That is what licenses writing <code>2R</code> in step 4; without the midpoint condition the two reactions at the ends of the edge would generally differ.</p>
<p><b>Why the other four are wrong — and how to prove it rather than assert it.</b> Let the added weight sit a fraction <code>u</code> of the height past the loaded edge, measured towards the <code>N</code> corner. Our weight is on the edge, so <code>u = 0</code>. The moment balance about the loaded edge becomes <code>N h = W(h/3) + W(u h)</code>, so <code>N = W(1/3 + u)</code>, and vertical equilibrium gives <code>R = W(5/3 − u)/2</code>. The ratio is therefore</p>
<div class="formula">R / N = (5 − 3u) / (2 + 6u)</div>
<p>At <code>u = 0</code> this is <code>5/2</code>. Now check what each option demands. A ratio of <code>3</code> needs <code>u = −1/21</code>, a ratio of <code>4</code> needs <code>u = −1/9</code>, and a ratio of <code>5</code> needs <code>u = −5/33</code> — all <b>negative</b>, meaning the added weight would have to hang off the sheet just beyond the loaded edge, which is not what the diagram shows. A ratio of <code>2</code> needs <code>u = +1/15</code>, placing the weight a little inboard of the edge rather than on it. Only <code>5 : 2</code> matches the weight being exactly where the stem puts it, at the midpoint of the edge.</p>
<p>Two further sanity checks fall out of the same formula. Setting <code>u = 1/3</code> puts the added weight level with the centroid, and gives <code>R : N = 1 : 1</code> — correct, because the two weights then act at the same point. And setting <code>u = −1/3</code> drives <code>N</code> to zero: put the added weight far enough off the near side and the sheet would tip about the loaded edge. None of those values appears among the options, which is a useful signal that the geometry in the stem is doing real work.</p>
<p><b>The trap.</b> Forgetting the sheet's own weight, and treating the added <code>W</code> as the only load. Then moments about the loaded edge give <code>N = 0</code>, which is plainly wrong — and a ratio of <code>5 : 0</code> is not on the list, which is the paper's way of telling you the sheet's weight is part of the problem.</p>
<p><b>The transferable rule.</b> When a rigid body has several parallel forces, the pivot that makes the most terms vanish is the one lying along the line of as many of them as possible. Choose the pivot last, not first: read the geometry, notice which forces are collinear with the load, and take moments about that line.</p>
<p><b>Relevant topics:</b> moments; centre of mass of a triangle; conditions for equilibrium.</p>`,
  trap: "Leaving out the sheet's own weight. Both the sheet and the added mass contribute, and only the added one sits on the edge, so <code>N</code> is a third of <code>W</code> rather than zero."
},

{
  id: "R0S-08", module: "G", topic: "Which sketch shows how the critical angle varies with refractive index?", diff: 3, paper: "R0-SAMPLE",
  rel: [
    ["G", "Critical angle and total internal reflection"],
    ["G", "Snell's law and refractive index"],
    ["A", "Reading the shape of a graph, not just its trend"]
  ],
  key: ["criticalangle", "snell", "refractive", "graphshape"],
  q: `<p>Consider the boundary between a material with refractive index <code>n</code> and air. Which of the following graphs best describes how the critical angle <code>θ<sub>c</sub></code> changes with <code>n</code>?</p><figure class="fig">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 476 260" role="img" aria-label="Five candidate graphs of the critical angle theta sub c against refractive index n. A falls in a straight line to the axis; B rises and steepens; C runs almost flat and then plunges to the axis; D rises and levels off; E falls steeply at first and then flattens, never reaching the axis. A, C and E each begin with a vertical stroke, which marks n = 1.">
<g transform="translate(-70,-442)">
<defs>
<marker id="s8-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
</defs>
<line x1="78.2" y1="552.1" x2="193.9" y2="552.1" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="78.2" y1="552.1" x2="78.2" y2="460.2" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="125.6" y1="552.1" x2="125.6" y2="492.9" stroke="#2f5fd0" stroke-width="2.2"/>
<polyline points="125.6,492.9 128.1,495.3 130.8,498 134.1,501.3 137.1,504.3 139.6,506.8 142.3,509.5 144.8,512 147.3,514.5 149.8,517 152.3,519.5 155,522.2 157.5,524.7 160.9,528.1 163.9,531.1 166.5,533.7 169.5,536.7 172,539.2 174.5,541.7 177.3,544.5 180.3,547.5 183.3,550.5 184.9,552.1" fill="none" stroke="#2f5fd0" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<text x="141.5" y="461.5" font-size="12" text-anchor="middle" fill="#14181f">A<tspan font-size="8.64" dy="3.12"></tspan></text>
<text x="81.8" y="456.8" font-size="12" fill="#14181f">&#952;<tspan font-size="8.6" dy="2.6">c</tspan></text>
<text x="197.6" y="549.9" font-size="12" fill="#14181f">n</text>
<line x1="246.7" y1="552.1" x2="362.4" y2="552.1" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="246.7" y1="552.1" x2="246.7" y2="460.2" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<polyline points="246.7,552.1 249.3,551.2 251.8,550.2 254.4,549.3 257,548.3 259.8,547.3 262.3,546.3 264.9,545.4 267.7,544.3 270.2,543.4 272.8,542.4 276.9,540.8 279.4,539.8 282,538.8 284.6,537.8 287.1,536.8 289.9,535.7 292.7,534.5 295.3,533.5 297.8,532.4 300.4,531.3 303,530.2 305.7,529 308.5,527.7 311.7,526.2 314.3,525 316.9,523.8 319.4,522.5 322,521.2 325.2,519.5 327.8,518 330.3,516.6 332.9,515 335.7,513.2 338.2,511.4 340.8,509.5 343.4,507.3 345.9,504.9 348.5,502.1 351.1,498.4 353.4,490.1" fill="none" stroke="#2f5fd0" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<text x="310.2" y="461.5" font-size="12" text-anchor="middle" fill="#14181f">B<tspan font-size="8.64" dy="3.12"></tspan></text>
<text x="250.3" y="456.8" font-size="12" fill="#14181f">&#952;<tspan font-size="8.6" dy="2.6">c</tspan></text>
<text x="366.1" y="549.9" font-size="12" fill="#14181f">n</text>
<line x1="415.2" y1="552.1" x2="530.8" y2="552.1" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="415.2" y1="552.1" x2="415.2" y2="460.2" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="462.6" y1="552.1" x2="462.6" y2="492.9" stroke="#2f5fd0" stroke-width="2.2"/>
<polyline points="462.6,492.9 465.1,492.9 467.6,493.1 470.1,493.3 472.6,493.7 475.1,494.2 477.6,494.8 480.1,495.5 482.6,496.3 485.1,497.3 487.6,498.4 490.1,499.6 492.6,501 495.1,502.5 497.7,504.3 500.3,506.4 502.8,508.5 505.3,511 507.8,513.7 510.3,516.9 512.9,520.7 515.4,525.1 517.9,530.6 520.4,538.7 521.9,552.1" fill="none" stroke="#2f5fd0" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<text x="478.5" y="461.3" font-size="12" text-anchor="middle" fill="#14181f">C<tspan font-size="8.64" dy="3.12"></tspan></text>
<text x="418.8" y="456.8" font-size="12" fill="#14181f">&#952;<tspan font-size="8.6" dy="2.6">c</tspan></text>
<text x="534.6" y="549.9" font-size="12" fill="#14181f">n</text>
<line x1="162.5" y1="694.8" x2="278.1" y2="694.8" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="162.5" y1="694.8" x2="162.5" y2="602.9" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<polyline points="162.5,694.8 165,692.7 167.6,690.5 170.4,688.2 172.9,686 175.5,683.9 178.1,681.8 180.9,679.6 184.1,677 186.6,675 189.6,672.6 193.3,669.9 196,667.8 198.6,666 201.4,664 204,662.2 206.5,660.5 209.1,658.8 211.7,657.2 214.2,655.7 216.8,654.2 219.4,652.7 222.6,651.1 225.1,649.8 227.7,648.5 230.3,647.4 233.3,646.2 235.8,645.2 238.4,644.3 241,643.4 243.5,642.7 246.1,642 248.9,641.3 251.4,640.8 254.6,640.3 257.4,639.9 260.2,639.7 262.8,639.5 265.3,639.5 267.9,639.5 269.2,639.5" fill="none" stroke="#2f5fd0" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<text x="225.9" y="604.1" font-size="12" text-anchor="middle" fill="#14181f">D<tspan font-size="8.64" dy="3.12"></tspan></text>
<text x="166" y="599.5" font-size="12" fill="#14181f">&#952;<tspan font-size="8.6" dy="2.6">c</tspan></text>
<text x="281.8" y="692.6" font-size="12" fill="#14181f">n</text>
<line x1="331" y1="694.8" x2="446.6" y2="694.8" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="331" y1="694.8" x2="331" y2="602.9" stroke="#14181f" stroke-width="1.6" marker-end="url(#s8-ar)"/>
<line x1="378.4" y1="694.8" x2="378.4" y2="635.5" stroke="#2f5fd0" stroke-width="2.2"/>
<polyline points="378.4,632.7 380.9,646.4 383.4,651.6 385.9,655.3 388.4,658.3 390.9,660.7 393.4,662.7 395.9,664.5 398.5,666.2 401,667.5 403.5,668.8 406,669.9 408.6,671 411.1,671.9 413.6,672.8 416.1,673.6 418.7,674.3 421.2,675 423.7,675.6 426.3,676.3 428.8,676.8 431.3,677.3 433.8,677.8 436.4,678.3 437.7,678.5" fill="none" stroke="#2f5fd0" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<text x="394.5" y="604.2" font-size="12" text-anchor="middle" fill="#14181f">E<tspan font-size="8.64" dy="3.12"></tspan></text>
<text x="334.5" y="599.5" font-size="12" fill="#14181f">&#952;<tspan font-size="8.6" dy="2.6">c</tspan></text>
<text x="450.3" y="692.6" font-size="12" fill="#14181f">n</text>
</g>
</svg>
</figure>`,
  opts: [`A — falls in a straight line to the axis`, `B — rises, steepening as it goes`, `C — runs almost flat, then plunges to the axis`, `D — rises, then levels off`, `E — falls steeply at first, then flattens without reaching the axis`],
  ans: 4,
  sol: `<p><b>What is being tested.</b> Two things at once: the formula for the critical angle, and the <i>shape</i> of the curve it produces. Every one of the five options gets the trend or the shape wrong in a different way, so quoting the trend alone is not enough.</p>
<p><b>Step 1 — get the relation.</b> The critical angle is the angle of incidence in the denser medium for which the refracted ray grazes the boundary, so the angle of refraction is 90°. Snell's law with the second medium being air, <code>n₂ = 1</code>:</p>
<div class="formula">n sin θ꜀ = 1 × sin 90° = 1
sin θ꜀ = 1 / n
θ꜀ = arcsin(1 / n)</div>
<p><b>Step 2 — direction.</b> As <code>n</code> increases, <code>1/n</code> decreases, so <code>θ꜀</code> decreases. The graph must <b>fall</b>. That immediately removes B and D, which rise.</p>
<p><b>Step 3 — anchor it with angles you can write down exactly.</b> Choose values of <code>n</code> whose reciprocal you know:</p>
<div class="formula">n = 1      →  sin θ꜀ = 1      →  θ꜀ = 90°
n = √2     →  sin θ꜀ = 1/√2   →  θ꜀ = 45°
n = 2      →  sin θ꜀ = 1/2    →  θ꜀ = 30°
n = 4      →  sin θ꜀ = 1/4    →  θ꜀ ≈ 14°</div>
<p>Now read the pattern rather than the individual numbers. Going from <code>n = 1</code> to <code>n = √2</code> — only a 40% rise in <code>n</code> — the angle collapses from 90° to 45°, a drop of 45°. Rising from <code>n = 2</code> to <code>n = 4</code>, a doubling, takes it only from 30° to about 14°, a drop of 16°. So the curve <b>falls very steeply near n = 1 and then flattens out</b> — and since <code>1/n</code> never reaches zero, the curve approaches the axis without ever touching it.</p>
<p><b>Answer: E.</b></p>
<p><b>Step 4 — dispose of the other falling sketch.</b> Option A falls too, so the trend alone cannot separate A from E. Its shape is what condemns it: a straight line running all the way down to the axis. A straight line means <code>θ꜀</code> would reach zero at some finite index, and beyond that index no light could be totally internally reflected at all. That is not what <code>arcsin(1/n)</code> does. Similarly option C is the right direction but the wrong way round in curvature: it says the angle barely changes for small <code>n</code> and then falls off a cliff, whereas the real curve does its falling first.</p>
<p><b>Why A, C and E all start with a short vertical stroke.</b> The critical angle is only defined for <code>n ≥ 1</code> — a material less dense than air has no critical angle against air. The sketches mark the starting index with a vertical stroke rather than letting the curve begin at the origin, and that stroke is the near-vertical part of <code>arcsin(1/n)</code> at <code>n = 1</code>, where the curve really does leave the top of the axis vertically.</p>
<p><b>The trap.</b> Picking A because "the critical angle falls as the refractive index rises" is true, and then stopping. A straight-line decoy is on the paper precisely because a candidate who only checks the direction will take it. Whenever a question says "best describes", the shape is part of the answer.</p>
<p><b>The transferable rule.</b> For any graph of a formula, do three things: get the trend from the formula, check the trend at both ends (here <code>n → 1</code> and <code>n</code> large), and then ask whether the curve should be straight or curved. Curvature is a real, checkable piece of physics, and it is where the marks live.</p>
<p><b>Relevant topics:</b> critical angle; total internal reflection; Snell's law; graph shape.</p>`,
  trap: "Choosing the straight-line graph because it falls, and stopping there. <code>arcsin(1/n)</code> falls steeply and then flattens; it is never a straight line, and it never reaches zero."
},

{
  id: "R0S-09", module: "C", topic: "Energy stored when three springs are displaced sideways by a small amount", diff: 3, paper: "R0-SAMPLE",
  rel: [
    ["C", "Energy stored in a stretched spring, ½kx²"],
    ["E", "Hooke's law and spring constant"],
    ["A", "The small-angle and limiting-case checks"]
  ],
  key: ["secondorder", "hookeslaw", "smallchange", "ratio"],
  q: `<p>Three ideal springs of spring constant <code>k</code> and natural length <code>a</code> are arranged equidistant from a point <code>P</code>, as shown below. The points <code>A</code>, <code>B</code> and <code>C</code> are fixed in the plane of the paper, and are initially each a distance <code>a</code> away from <code>P</code>. The point <code>P</code> is then moved a small distance <code>d</code> perpendicular to the plane of the paper.</p><p>Which of these options gives the best approximation for the total energy stored in the system?</p><figure class="fig">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 152 130" role="img" aria-label="Point P joined to three fixed points A, B and C by three identical springs. A is directly above P, B is down and to the left and C is down and to the right, each the same distance from P and 120 degrees from its neighbours.">
<g transform="translate(-230,-108)">

<path d="M306,192.3 L310.4,185.022 L301.6,177.744 L310.4,170.467 L301.6,163.189 L310.4,155.911 L301.6,148.633 L310.4,141.356 L301.6,134.078 L306,126.8" fill="none" stroke="#14181f" stroke-width="2" stroke-linejoin="round"/>
<path d="M306,192.3 L297.502,192.122 L295.598,203.378 L284.902,199.388 L282.998,210.645 L272.302,206.655 L270.398,217.912 L259.702,213.922 L257.798,225.178 L249.3,225" fill="none" stroke="#14181f" stroke-width="2" stroke-linejoin="round"/>
<path d="M306,192.3 L310.102,199.745 L320.798,195.755 L322.702,207.012 L333.398,203.022 L335.302,214.278 L345.998,210.288 L347.902,221.545 L358.598,217.555 L362.7,225" fill="none" stroke="#14181f" stroke-width="2" stroke-linejoin="round"/>
<circle cx="306" cy="126.8" r="2.8" fill="#14181f"/>
<circle cx="249.3" cy="225" r="2.8" fill="#14181f"/>
<circle cx="362.7" cy="225" r="2.8" fill="#14181f"/>
<circle cx="306" cy="192.3" r="2.8" fill="#14181f"/>
<text x="305.75" y="122.2" font-size="12" text-anchor="middle" fill="#14181f" font-weight="bold">A</text>
<text x="240.65" y="229.2" font-size="12" text-anchor="middle" fill="#14181f" font-weight="bold">B</text>
<text x="371.05" y="229.3" font-size="12" text-anchor="middle" fill="#14181f" font-weight="bold">C</text>
<text x="298.75" y="188.9" font-size="12" text-anchor="middle" fill="#14181f" font-weight="bold">P</text>
</g>
</svg>
</figure>`,
  opts: [`kd<sup>4</sup> / (2a²)`, `3kd<sup>4</sup> / a²`, `3kd<sup>4</sup> / (2a²)`, `3kd<sup>4</sup> / (4a²)`, `3kd<sup>4</sup> / (8a²)`],
  ans: 4,
  sol: `<p><b>What is being tested.</b> Whether you notice that a <i>sideways</i> displacement hardly stretches a spring at all. To first order it stretches it not at all, so the energy is not <code>½kd²</code> — it is much smaller, and you have to look at the next order to find it.</p>
<p><b>Step 1 — set the initial state up, because it is what makes the arithmetic clean.</b> Each spring has natural length <code>a</code>, and <code>P</code> starts a distance <code>a</code> from each of <code>A</code>, <code>B</code> and <code>C</code>. So each spring starts at exactly its natural length: zero extension, zero force, zero stored energy. The whole of the final energy is therefore <i>change</i> in energy, and there is nothing to subtract.</p>
<p><b>Step 2 — the new length.</b> The displacement <code>d</code> is perpendicular to the plane, so it is perpendicular to all three of <code>PA</code>, <code>PB</code> and <code>PC</code>, whatever direction in the plane each of those lies in. Each spring is the hypotenuse of a right-angled triangle with one side <code>a</code> and the other side <code>d</code>:</p>
<div class="formula">L = √(a² + d²)</div>
<p>Note that every spring gets the <i>same</i> new length. That is exactly what "arranged equidistant" is there to guarantee, and it is why the three springs can be treated as three copies of one calculation rather than three separate ones.</p>
<p><b>Step 3 — the extension, to the right order in d.</b> Take out a factor of <code>a</code> and expand for small <code>d</code>:</p>
<div class="formula">L = a √(1 + d²/a²)  ≈  a (1 + d²/(2a²))  =  a + d²/(2a)

extension  x = L − a  ≈  d² / (2a)</div>
<p>This is the step that decides the question. The extension is <b>second order</b> in <code>d</code>, not first order: halve the displacement and the extension falls to a quarter. The reason is geometric — moving <code>P</code> sideways takes the spring from the hypotenuse <code>a</code> to the hypotenuse <code>√(a² + d²)</code>, and the difference of two hypotenuses is a much smaller thing than either of them.</p>
<p><b>Step 4 — the energy, one spring at a time.</b></p>
<div class="formula">U(one spring) = ½ k x² = ½ k (d²/(2a))² = ½ k × d⁴/(4a²) = k d⁴ / (8a²)</div>
<p><b>Step 5 — three springs.</b> Each stores the same amount, so multiply by three:</p>
<div class="formula">U(total) = 3k d⁴ / (8a²)</div>
<p><b>Answer: E, 3kd<sup>4</sup> / (8a²).</b></p>
<p><b>Check the units, because they are the only check available here.</b> The spring constant <code>k</code> has units N m<sup>−1</sup>. So <code>kd⁴/a²</code> has units N m<sup>−1</sup> × m⁴ / m² = N m, which is a joule. Every one of the five options has the same units, so units cannot separate them — the coefficient is the whole question, and that is worth noticing before you spend time on a check that cannot help.</p>
<p><b>Check the dependence on d.</b> All five options are proportional to <code>d⁴</code>, so the paper has already told you the power of <code>d</code>; the difference between the options is only the numerical coefficient: <code>1/2</code>, <code>3</code>, <code>3/2</code>, <code>3/4</code>, <code>3/8</code>. Since the pattern "three springs, each with <code>½kx²</code>, and <code>x = d²/(2a)</code>" produces a factor <code>3 × ½ × 1/4 = 3/8</code>, only E can be right. Two of the options are exactly twice and four times E, which is what a slip in either the <code>½</code> or the square of the <code>½</code> would produce.</p>
<p><b>The trap.</b> Writing <code>½kd²</code> for each spring by reflex. That is the energy of a spring stretched <i>by</i> <code>d</code>, and here the spring is not stretched by <code>d</code> at all — it is stretched by <code>d²/(2a)</code>, which for small <code>d</code> is far smaller. The reflex also fails a sanity check: <code>½kd²</code> grows as fast as the displacement squared, whereas a sideways nudge of a spring that is already almost straight is barely felt.</p>
<p><b>The transferable rule.</b> Whenever a problem says "a small distance <code>d</code>", work out what the small quantity multiplies before you reach for a formula. If the leading term cancels — as it does here, where the first-order change in length vanishes — the answer is governed by the next term, and the resulting energy can be a fourth power rather than a square.</p>
<p><b>Relevant topics:</b> elastic energy in a spring; Hooke's law; the small-change expansion; limiting-case checks.</p>`,
  trap: "Writing <code>½kd²</code> per spring. Moving <code>P</code> perpendicular to the plane changes each spring's length by only <code>d²/(2a)</code>, so the energy goes as <code>d⁴</code>, not <code>d²</code>."
},

{
  id: "R0S-10", module: "A", topic: "How the ring frequency of a rod depends on its length", diff: 2, paper: "R0-SAMPLE",
  rel: [
    ["A", "Dimensional consistency and deriving a relation from units"],
    ["A", "Base units for density and the Young modulus"],
    ["F", "Frequency and the natural vibration of a solid"]
  ],
  key: ["dimensions", "ratio", "nocalc"],
  q: `<p>The frequency <code>f</code> produced by a uniform metal rod when hit by a hammer is dependent only upon its length <code>L</code>, density <code>ρ</code> and Young's modulus <code>E</code>. Find the proportionality relation between <code>f</code> and <code>L</code>.</p>`,
  opts: [`f ∝ 1 / L²`, `f ∝ 1 / L`, `f ∝ 1 / √L`, `f ∝ √L`, `f ∝ L`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> Dimensional analysis. No physics is needed beyond knowing the units of the three quantities named, and the question is precise about which those are: <i>only</i> <code>L</code>, <code>ρ</code> and <code>E</code>. Nothing else may appear, which is what makes the answer unique.</p>
<p><b>Step 1 — write the units of everything.</b> Use mass, length and time as the three base dimensions:</p>
<div class="formula">[f] = T⁻¹                      (a frequency is per second)
[L] = L                        (a length)
[ρ] = M L⁻³                    (mass per unit volume)
[E] = M L⁻¹ T⁻²                (stress, which is force per unit area)</div>
<p>The last one is the only one worth pausing over. Pressure and stress are both force per area, so their units are N m⁻² = (kg m s⁻²) m⁻² = kg m<sup>−1</sup> s<sup>−2</sup>. That is <code>M L⁻¹ T⁻²</code>.</p>
<p><b>Step 2 — suppose a product.</b> Assume the relation is a product of powers, with an unknown dimensionless constant out front that dimensional analysis cannot find (and is not being asked for):</p>
<div class="formula">f = C × Lᵃ ρᵇ Eᶜ</div>
<p><b>Step 3 — match the dimensions one at a time.</b> Put in the dimensions from step 1 and compare exponents:</p>
<div class="formula">T⁻¹  =  (L)ᵃ (M L⁻³)ᵇ (M L⁻¹ T⁻²)ᶜ
     =  M<sup>b+c</sup>  L<sup>a</sup> − 3b − c)  T<sup>−2c</sup></div>
<p>Now equate exponents of each base dimension:</p>
<div class="formula">time:        −1 = −2c            ⇒  c = 1/2
mass:         0 = b + c          ⇒  b = −1/2
length:       0 = a − 3b − c     ⇒  a = 3b + c = −3/2 + 1/2 = −1</div>
<p><b>Step 4 — read off the length dependence.</b> The exponent of <code>L</code> is <code>−1</code>, so</p>
<div class="formula">f = C × L⁻¹ ρ^(−1/2) E<sup>1/2</sup>  =  (C / L) × √(E / ρ)</div>
<p><b>Answer: B, f ∝ 1 / L.</b></p>
<p><b>Sanity-check the two other variables, because they are free.</b> The relation says <code>f ∝ √E</code>, so a stiffer rod rings higher — like a xylophone bar, where a harder material gives a brighter note. It says <code>f ∝ 1/√ρ</code>, so a denser rod rings lower, which is why lead thuds and aluminium pings. Both of those match everyday experience, and they cost nothing to check.</p>
<p><b>Why the other four are wrong.</b> Option A, <code>1/L²</code>, is the string formula <code>f = (1/2L)√(T/μ)</code> leaking in — but that expression contains a <i>tension</i>, and tension is not among the three quantities the question allows. That is the key discipline: the phrase "dependent only upon" is a constraint, and any attempt to import extra physics is outside the problem. Options C, D and E are the other powers of <code>L</code> on the list, and only one exponent can satisfy the length equation in step 3 once <code>b</code> and <code>c</code> are fixed.</p>
<p><b>Do it the fast way.</b> Start with the time equation, because <code>T</code> appears in only one place: <code>E</code> carries <code>T⁻²</code> and nothing else does, so <code>c</code> is forced to be <code>1/2</code> immediately. Then mass fixes <code>b</code> at <code>−1/2</code>. Only then does the length equation need solving, and it needs only <code>a = 3b + c</code>. Three unknowns, three equations, no guesswork.</p>
<p><b>The wider point.</b> Dimensional analysis fixes the form of a relation completely whenever the number of unknowns equals the number of base dimensions. Here three quantities with three unknown exponents meet three independent equations, so the answer is unique up to a pure number — and that is enough to answer the question, even though the constant <code>C</code> remains unknown and unknowable this way.</p>
<p><b>Relevant topics:</b> dimensional analysis; base units of density and the Young modulus; derived relations.</p>`,
  trap: "Quoting <code>f ∝ 1/L²</code> from the stretched-string formula. That expression needs a tension, and tension is not among the three quantities the question allows."
},

{
  id: "R0S-11", module: "D", topic: "Why the ground pushes less hard on a rock at the equator", diff: 2, paper: "R0-SAMPLE",
  rel: [
    ["D", "Circular motion and the centripetal force"],
    ["D", "Apparent weight and the normal reaction force"],
    ["A", "Estimating: rounding each input to one or two significant figures"]
  ],
  key: ["apparentweight", "circular", "ratio", "nocalc"],
  q: `<p>A small rock sitting at the Earth's North pole experiences a normal reaction force <code>N<sub>1</sub></code> from the ground. The same rock at the equator experiences a normal reaction force <code>N<sub>2</sub></code>. The Earth's radius is <code>6 × 10⁶ m</code>.</p><p>Which of these is the best estimate for <code>(N<sub>1</sub> − N<sub>2</sub>) / N<sub>1</sub></code>?</p>`,
  opts: [`3%`, `0.3%`, `0.03%`, `0.003%`, `0.0003%`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> The difference between weight and apparent weight, plus the discipline of estimating. The five options are one power of ten apart, so the whole job is to get the leading digit and the exponent right — and to notice that rounding every input hard is not just allowed but necessary.</p>
<p><b>Step 1 — the pole.</b> The North pole lies <i>on</i> the Earth's axis of rotation, so a rock there has zero distance from the axis. It does not travel in a circle at all; it only turns on the spot. Its acceleration is therefore zero, and the forces on it balance:</p>
<div class="formula">N₁ = mg</div>
<p>This is the step people skip, and it is the one that makes the problem look harder than it is.</p>
<p><b>Step 2 — the equator.</b> Here the rock travels once round a circle of radius <code>R</code> — the Earth's radius — every day. It needs a centripetal force <code>mω²R</code> directed towards the axis, which at the equator is straight down. Two forces act vertically: gravity <code>mg</code> downwards, and the normal reaction <code>N₂</code> upwards. Their <i>resultant</i> supplies the circular motion:</p>
<div class="formula">mg − N₂ = mω²R
N₂ = mg − mω²R</div>
<p>So the ground pushes up with slightly less than the rock's weight — the shortfall being exactly what is needed to keep the rock going round. This is why "apparent weight" is a real effect and not a trick of language.</p>
<p><b>Step 3 — form the ratio the question asks for.</b></p>
<div class="formula">(N₁ − N₂) / N₁ = (mg − (mg − mω²R)) / mg = mω²R / mg = ω²R / g</div>
<p>The mass cancels, which is worth noting: the answer is the same for a pebble and for a person. The rock's mass never enters.</p>
<p><b>Step 4 — estimate, rounding hard on purpose.</b> One day is about <code>8.6 × 10⁴ s</code>, so</p>
<div class="formula">ω = 2π / T ≈ 6.3 / (8.6 × 10⁴) ≈ 7.3 × 10⁻⁵ rad s⁻¹
ω² ≈ (7.3 × 10⁻⁵)² ≈ 5.3 × 10⁻⁹ s⁻²
ω²R ≈ 5.3 × 10⁻⁹ × 6 × 10⁶ ≈ 3.2 × 10⁻² m s⁻²</div>
<p>For the last step, divide by <code>g</code>. Use <code>g ≈ 10 m s⁻²</code> rather than the more accurate value — the options are a factor of ten apart, so the difference between 9.8 and 10 cannot affect which one is right, and the round number is far easier to divide by:</p>
<div class="formula">ω²R / g ≈ 3.2 × 10⁻² / 10 ≈ 3.2 × 10⁻³
        = 0.32%  ≈  0.3%</div>
<p><b>Answer: B, 0.3%.</b></p>
<p><b>Why the rough arithmetic is the right arithmetic.</b> This question is not testing multiplication; it is testing whether you know which terms belong. Everything is rounded to two significant figures, and <code>g</code> is rounded to one, and the answer is still unmistakably 0.3% rather than 3% or 0.03%. A candidate who reaches for a calculator has misread what the question is for.</p>
<p><b>Why the other four are wrong.</b> They differ from the right answer only in the position of the decimal point, so each represents a specific slip: using <code>ω</code> in place of <code>ω²</code>, dropping or adding a factor of ten in the radius, or dividing by <code>g</code> when it should be multiplied. The reassuring thing is that no rearrangement of the correct physics can produce 3%: to get there you would need a radius ten times larger, or the rock to go round in a tenth of the time.</p>
<p><b>The trap.</b> Thinking the pole is special in the opposite direction — that there is an <i>extra</i> force at the pole because it is "the top". There is not: the pole's distinguishing feature is that its distance from the axis is zero, so the centrifugal term vanishes. Equally, do not worry about the sidereal day at <code>86164 s</code> versus the solar day at <code>86400 s</code>: they differ by about 0.3%, which is far below the resolution this question needs. Choosing between them is a distraction.</p>
<p><b>The wider point.</b> "Apparent weight" is the normal reaction, not gravity. At the equator the two differ by <code>ω²R/g</code>; at the pole they coincide. The same reasoning explains the <code>0.3%</code> flattening of the Earth itself, and it is why a launch site near the equator gets a small free boost.</p>
<p><b>Relevant topics:</b> circular motion; apparent weight; centripetal force; estimation.</p>`,
  trap: "Working in <code>ω</code> instead of <code>ω²</code>, or slipping a power of ten in the radius. The options are one decade apart, so the only thing that matters is the exponent."
},

{
  id: "R0S-12", module: "C", topic: "Tension in a chain whose blocks halve in mass going back", diff: 3, paper: "R0-SAMPLE",
  rel: [
    ["C", "Newton's second law applied to a system of connected bodies"],
    ["C", "Identifying which mass a given tension has to accelerate"],
    ["A", "Geometric series and testing a formula at n = 1"]
  ],
  key: ["tailmass", "force", "ratio", "nocalc"],
  q: `<p>A long chain of blocks, connected by light inextensible strings, travels without friction in a straight line on horizontal ground. The front block is being pulled with a force <code>D</code>, causing the entire chain to accelerate at a rate <code>a</code>. The block at the front has mass <code>m</code>, and each other block has half the mass of the block directly in front of it. The tensions in the strings are labelled <code>T<sub>1</sub></code>, <code>T<sub>2</sub></code>, ... from the front, as shown in the diagram.</p><p>Show that <code>T<sub>n</sub> = D − f(n)ma</code>, and select the correct form of the function <code>f(n)</code>.</p><figure class="fig">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 236 44" role="img" aria-label="A chain of blocks on horizontal ground, pulled to the right by a force D. The front block has mass m, the block behind it has mass m over 2 and the one behind that has mass m over 4, with the chain continuing off to the left. T1 labels the string between the front block and the next one, and T2 the string behind that.">
<g transform="translate(-172,-634)">
<defs>
<marker id="s12-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
</defs>
<line x1="178.4" y1="671.8" x2="405.2" y2="671.8" stroke="#14181f" stroke-width="1.6"/>
<g stroke="#14181f" stroke-width="2">
<line x1="178.4" y1="657.7" x2="206.8" y2="657.7"/>
<line x1="235.1" y1="657.7" x2="263.5" y2="657.7"/>
<line x1="291.8" y1="657.7" x2="320.2" y2="657.7"/>
</g>
<rect x="207.2" y="643.9" width="27.5" height="27.5" fill="#e8eefc" stroke="#14181f" stroke-width="2"/>
<rect x="263.9" y="643.9" width="27.5" height="27.5" fill="#e8eefc" stroke="#14181f" stroke-width="2"/>
<rect x="320.6" y="643.9" width="27.5" height="27.5" fill="#e8eefc" stroke="#14181f" stroke-width="2"/>
<line x1="348.5" y1="657.7" x2="387.8" y2="657.7" stroke="#b3352f" stroke-width="2.2" marker-end="url(#s12-ar)"/>
<text x="395.1" y="661.8" font-size="12" fill="#b3352f" font-weight="bold">D</text>
<text x="221" y="654.7" font-size="11" text-anchor="middle" fill="#14181f">m</text>
<line x1="214.5" y1="657.2" x2="227.5" y2="657.2" stroke="#14181f" stroke-width="1"/>
<text x="221" y="666.7" font-size="11" text-anchor="middle" fill="#14181f">4</text>
<text x="277.7" y="654.7" font-size="11" text-anchor="middle" fill="#14181f">m</text>
<line x1="271.2" y1="657.2" x2="284.2" y2="657.2" stroke="#14181f" stroke-width="1"/>
<text x="277.7" y="666.7" font-size="11" text-anchor="middle" fill="#14181f">2</text>
<text x="334.4" y="660.4" font-size="11" text-anchor="middle" fill="#14181f">m</text>
<text x="248.5" y="646.7" font-size="11.5" text-anchor="middle" fill="#14181f">T<tspan font-size="8.28" dy="2.99">2</tspan></text>
<text x="305" y="646.7" font-size="11.5" text-anchor="middle" fill="#14181f">T<tspan font-size="8.28" dy="2.99">1</tspan></text>
</g>
</svg>
</figure>`,
  opts: [`2 − n`, `2<sup>1−n</sup>`, `2 − 2<sup>−n</sup>`, `2 − 2<sup>1−n</sup>`, `1 − 2<sup>−n</sup>`],
  ans: 3,
  sol: `<p><b>What is being tested.</b> A question about <i>which</i> mass a tension has to accelerate. Once that is clear the algebra is short; the options are close enough together that only a correct expression survives.</p>
<p><b>Step 1 — number the blocks and write down their masses.</b> Count from the front, the end being pulled:</p>
<div class="formula">block 1:  m        block 2:  m/2      block 3:  m/4      ...      block n:  m / 2<sup>n−1</sup></div>
<p>Every block has the same acceleration <code>a</code>, because the strings are inextensible and the chain moves as one body.</p>
<p><b>Step 2 — ask what one tension actually has to do.</b> The string carrying <code>Tₙ</code> lies <i>behind</i> block <code>n</code>. Everything it pulls is block <code>n+1</code> and all the blocks behind that. So <code>Tₙ</code> is the force needed to give the whole tail that acceleration:</p>
<div class="formula">Tₙ = (mass behind block n) × a</div>
<p>This is the step the whole question turns on. It is not the force on block <code>n</code>, and it is certainly not the force on the front block.</p>
<p><b>Step 3 — sum the tail.</b> The masses behind block <code>n</code> form a geometric series with first term <code>m/2ⁿ</code> and ratio <code>1/2</code>:</p>
<div class="formula">m/2ⁿ + m/2<sup>n+1</sup> + m/2<sup>n+2</sup> + ... = (m/2ⁿ)(1 + 1/2 + 1/4 + ...) = (m/2ⁿ) × 2 = m / 2<sup>n−1</sup></div>
<p>Check it against the case you can do in your head: for <code>n = 1</code> the tail is everything but the front block, whose total mass is <code>m/2 + m/4 + ... = m</code>. And <code>m/2<sup>1−1</sup> = m</code>. ✓</p>
<p><b>Step 4 — get the tension.</b></p>
<div class="formula">Tₙ = (m / 2<sup>n−1</sup>) × a = ma × 2<sup>1−n</sup></div>
<p><b>Step 5 — eliminate ma in favour of D.</b> The driving force has to accelerate the entire chain. The total mass is <code>m(1 + 1/2 + 1/4 + ...) = 2m</code>, so</p>
<div class="formula">D = 2m × a   ⇒   ma = D / 2</div>
<p><b>Step 6 — reshape into the form the question asks for.</b> Compute <code>D − Tₙ</code>:</p>
<div class="formula">D − Tₙ = 2ma − ma × 2<sup>1−n</sup> = ma (2 − 2<sup>1−n</sup>)</div>
<p>so, writing <code>Tₙ = D − f(n)ma</code>:</p>
<div class="formula">f(n) = 2 − 2<sup>1−n</sup></div>
<p><b>Answer: D, 2 − 2<sup>1−n</sup>.</b></p>
<p><b>Test the formula at n = 1 and n = 2 — this is the whole verification.</b> At <code>n = 1</code>, <code>2<sup>1−1</sup> = 2⁰ = 1</code>, so <code>f(1) = 2 − 1 = 1</code> and</p>
<div class="formula">T₁ = D − ma = 2ma − ma = ma</div>
<p>which agrees with the direct calculation in step 4, <code>T₁ = ma × 2⁰ = ma</code>. ✓ At <code>n = 2</code>, <code>2<sup>1−2</sup> = 1/2</code>, so <code>f(2) = 2 − 1/2 = 3/2</code> and</p>
<div class="formula">T₂ = 2ma − (3/2)ma = ma/2</div>
<p>which agrees with the direct calculation, <code>T₂ = ma × 2⁻¹ = ma/2</code>. ✓ Two values checked, both matching.</p>
<p><b>Why the other four are wrong.</b> Option C, <code>2 − 2<sup>−n</sup></code>, differs from the right answer by a single <code>1</code> in the exponent, and testing it at <code>n = 1</code> kills it: it gives <code>f(1) = 3/2</code>, hence <code>T₁ = ma/2</code>, but you can read <code>T₁ = ma</code> straight off the definition, since the string behind the front block tows a tail of total mass <code>m</code>. Option B, <code>2<sup>1−n</sup></code>, is the tension divided by <code>ma</code> rather than the shortfall <code>f(n)</code> — it is the answer to a different rearrangement. Option E, <code>1 − 2<sup>−n</sup></code>, gives <code>T₁ = 1.5 ma</code>, which is larger than <code>T₁</code> can be. Option A, <code>2 − n</code>, goes negative for <code>n &gt; 2</code>, so it would make the tension exceed the driving force.</p>
<p><b>The trap.</b> Guessing between C and D by eye. They are identical except for one digit in the exponent, and there is no way to tell them apart except by substitution. That is the point: the paper has made the two "obvious" forms adjacent so that only a check will do. Substituting <code>n = 1</code> costs about ten seconds, and the formula for <code>T₁</code> can be written down from what the question says without any algebra at all.</p>
<p><b>The transferable rule.</b> In any connected-bodies problem, first decide <i>which</i> body your unknown force acts across, and then apply Newton's second law to the side of the boundary you have chosen. The rest is algebra. And whenever a multiple-choice list contains two options that differ only in a small detail, stop guessing and substitute a value you can compute independently.</p>
<p><b>Relevant topics:</b> Newton's second law for connected bodies; systems and boundaries; geometric series; testing a formula at the first case.</p>`,
  trap: "Choosing <code>2 − 2<sup>−n</sup></code> because it looks almost identical. Test at <code>n = 1</code>, where the tension behind the front block must be <code>ma</code> — that settles it in one substitution."
}

]);
