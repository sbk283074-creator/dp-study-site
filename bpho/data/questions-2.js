/* BPhO Round 0 — question bank, part 2 of 2.
   Modules H–N. Round 0 format: five options, no calculator, one mark each. */

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([

/* ===================== MODULE H — circuits ===================== */

{
  id: "H-01", module: "H", topic: "Series and parallel", diff: 1,
  q: `<p>Two 6.0 Ω resistors are connected in parallel, and this combination is connected in series with a 3.0 Ω resistor. What is the total resistance?</p>
<figure class="fig">
<svg viewBox="0 0 460 220" role="img" aria-label="A circuit with two 6 ohm resistors in parallel, connected in series with a 3 ohm resistor.">
<text x="230" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Two 6 Ω in parallel, in series with 3 Ω</text>
<line x1="70" y1="134" x2="70" y2="60" stroke="#1f2937" stroke-width="2"/>
<line x1="70" y1="60" x2="390" y2="60" stroke="#1f2937" stroke-width="2"/>
<line x1="390" y1="60" x2="390" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="390" y1="170" x2="70" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="70" y1="170" x2="70" y2="146" stroke="#1f2937" stroke-width="2"/>
<line x1="56" y1="146" x2="84" y2="146" stroke="#1f2937" stroke-width="2"/>
<line x1="62" y1="134" x2="78" y2="134" stroke="#1f2937" stroke-width="4.5"/>
<rect x="140" y="52" width="40" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="160" y="44" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">3.0 Ω</text>
<line x1="300" y1="60" x2="300" y2="88" stroke="#1f2937" stroke-width="2"/>
<rect x="292" y="88" width="16" height="36" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="300" y1="124" x2="300" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="360" y1="60" x2="360" y2="88" stroke="#1f2937" stroke-width="2"/>
<rect x="352" y="88" width="16" height="36" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="360" y1="124" x2="360" y2="170" stroke="#1f2937" stroke-width="2"/>
<text x="286" y="112" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">6.0 Ω</text>
<text x="346" y="112" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">6.0 Ω</text>
<circle cx="300" cy="60" r="3" fill="#1f2937"/>
<circle cx="360" cy="60" r="3" fill="#1f2937"/>
<circle cx="300" cy="170" r="3" fill="#1f2937"/>
<circle cx="360" cy="170" r="3" fill="#1f2937"/>
<text x="230" y="196" text-anchor="middle" font-size="11.5" fill="#7b8494">reduce the parallel pair first</text>
</svg>
</figure>`,
  opts: ["6.0 Ω", "15 Ω", "4.5 Ω", "9.0 Ω", "3.0 Ω"],
  ans: 0,
  sol: `<p><b>Step 1 — the parallel pair.</b> For two equal resistors in parallel the combined resistance is half of one:</p>
<div class="formula">R_parallel = (6.0 × 6.0)/(6.0 + 6.0) = 36/12 = 3.0 Ω</div>
<p><b>Step 2 — add the series resistor.</b></p>
<div class="formula">R_total = 3.0 + 3.0 = 6.0 Ω</div>
<p><b>Answer: A.</b></p>
<p><b>The two sanity checks, both free.</b> The parallel combination must be smaller than 6.0 Ω ✓ (it is 3.0 Ω). The total must therefore be more than 3.0 Ω and less than 9.0 Ω ✓ (it is 6.0 Ω). Those checks eliminate options B and E before any calculation.</p>
<p><b>The traps.</b> Option B, 15 Ω, comes from treating the parallel resistors as if they were in series — <code>6 + 6 + 3 = 15</code>. Option C, 4.5 Ω, is a slip in the parallel calculation. Option D, 9.0 Ω, is <code>6 + 3</code>, ignoring the second resistor entirely.</p>
<p><b>The shortcut worth knowing.</b> For <code>n</code> identical resistors of value <code>R</code> in parallel, the combination is <code>R/n</code>. So two 6 Ω resistors give 3 Ω immediately, with no arithmetic. That fact covers a surprising number of questions.</p>`,
  trap: "Adding parallel resistors instead of reciprocal-adding, or forgetting the sanity checks."
},
{
  id: "H-02", module: "H", topic: "Power", diff: 1,
  q: "A 3.0 Ω resistor is connected across a 12 V supply of negligible internal resistance. What power is dissipated in the resistor?",
  opts: ["48 W", "4.0 W", "36 W", "144 W", "24 W"],
  ans: 0,
  sol: `<p>The voltage across the resistor is the supply voltage, so use the form of the power equation containing <code>V</code> and <code>R</code>:</p>
<div class="formula">P = V²/R = 12²/3.0 = 144/3.0 = 48 W</div>
<p><b>Answer: A.</b></p>
<p><b>Why this form rather than <code>I²R</code>.</b> The question gives voltage and resistance directly. Using <code>P = I²R</code> would require computing the current first — an unnecessary extra step that introduces an extra chance of error. Choosing the form that uses only the quantities you were given is the discipline.</p>
<p><b>The check by the other route.</b> The current is <code>I = V/R = 12/3.0 = 4.0 A</code>. Then <code>P = I²R = 16 × 3.0 = 48 W</code> ✓. Both routes agree.</p>
<p><b>The traps.</b> Option B, 4.0 W, is the current in amperes reported as a power. Option C, 36 W, is what you get from <code>V²/R</code> with a slip in the squares. Option D, 144 W, is <code>V²</code> without dividing by <code>R</code>. Option E, 24 W, is <code>2VR</code>, which has no physical basis.</p>
<p><b>The practical context.</b> 48 W is a realistic value for a small heating element or a bright lamp. Checking the answer against physical intuition — is this a plausible power for a mains-powered device? — is a fast way to catch a slip.</p>`,
  trap: "Using a form of the power equation that requires quantities you were not given."
},
{
  id: "H-03", module: "H", topic: "Internal resistance", diff: 2,
  q: `<p>A cell of EMF 9.0 V and internal resistance 1.0 Ω is connected to an 8.0 Ω resistor. What is the terminal potential difference of the cell?</p>
<figure class="fig">
<svg viewBox="0 0 460 240" role="img" aria-label="A cell of EMF 9 volts with internal resistance 1 ohm driving an 8 ohm resistor, with a voltmeter connected across the cell terminals.">
<text x="230" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">The voltmeter reads the terminal pd</text>

<line x1="100" y1="70" x2="210" y2="70" stroke="#1f2937" stroke-width="2"/>
<line x1="270" y1="70" x2="380" y2="70" stroke="#1f2937" stroke-width="2"/>
<rect x="210" y="62" width="60" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="240" y="52" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">R = 8.0 Ω</text>

<line x1="380" y1="70" x2="380" y2="190" stroke="#1f2937" stroke-width="2"/>
<line x1="380" y1="190" x2="100" y2="190" stroke="#1f2937" stroke-width="2"/>

<line x1="100" y1="70" x2="100" y2="96" stroke="#1f2937" stroke-width="2"/>
<line x1="84" y1="96" x2="116" y2="96" stroke="#1f2937" stroke-width="2.5"/>
<line x1="92" y1="110" x2="108" y2="110" stroke="#1f2937" stroke-width="5"/>
<line x1="100" y1="110" x2="100" y2="130" stroke="#1f2937" stroke-width="2"/>
<rect x="92" y="130" width="16" height="34" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="100" y1="164" x2="100" y2="190" stroke="#1f2937" stroke-width="2"/>
<text x="128" y="101" font-size="12.5" font-weight="600" fill="#b3352f">ε = 9.0 V</text>
<text x="128" y="152" font-size="12.5" font-weight="600" fill="#b3352f">r = 1.0 Ω</text>

<line x1="100" y1="70" x2="34" y2="70" stroke="#7b8494" stroke-width="1.6" stroke-dasharray="5 4"/>
<line x1="34" y1="70" x2="34" y2="113" stroke="#7b8494" stroke-width="1.6" stroke-dasharray="5 4"/>
<line x1="100" y1="190" x2="34" y2="190" stroke="#7b8494" stroke-width="1.6" stroke-dasharray="5 4"/>
<line x1="34" y1="190" x2="34" y2="147" stroke="#7b8494" stroke-width="1.6" stroke-dasharray="5 4"/>
<circle cx="34" cy="130" r="17" fill="#ffffff" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="5 4"/>
<text x="34" y="136" text-anchor="middle" font-size="14" font-weight="600" fill="#4a5262">V</text>
<circle cx="100" cy="70" r="3" fill="#1f2937"/>
<circle cx="100" cy="190" r="3" fill="#1f2937"/>

<text x="230" y="222" text-anchor="middle" font-size="11.5" fill="#7b8494">both ε and r sit inside the cell; the voltmeter is across the pair</text>
</svg>
</figure>`,
  opts: ["7.0 V", "9.0 V", "1.0 V", "8.0 V", "4.5 V"],
  ans: 3,
  sol: `<p><b>Step 1 — total resistance.</b></p>
<div class="formula">R_total = R + r = 8.0 + 1.0 = 9.0 Ω</div>
<p><b>Step 2 — current.</b></p>
<div class="formula">I = ε/R_total = 9.0/9.0 = 1.0 A</div>
<p><b>Step 3 — terminal potential difference.</b> This is the EMF minus the internal loss:</p>
<div class="formula">V = ε − Ir = 9.0 − (1.0 × 1.0) = 8.0 V</div>
<p><b>Answer: D.</b></p>
<p><b>The cross-check.</b> The external resistor has 1.0 A through 8.0 Ω, so <code>V = IR = 8.0 V</code> ✓. The two routes must agree, and taking the second one when time allows is a free error check.</p>
<p><b>Why the terminal p.d. is less than the EMF.</b> The EMF is the energy given to each coulomb by the cell; the terminal p.d. is what remains after the cell's own internal resistance has taken its share. The difference, <code>Ir = 1.0 V</code>, is dissipated inside the cell as heat.</p>
<p><b>The traps.</b> Option B, 9.0 V, is the EMF, which a voltmeter would read only with no current flowing. Option C, 1.0 V, is the internal loss alone — the amount lost, not the amount delivered. Option A, 7.0 V, comes from subtracting the full internal resistance rather than the loss.</p>`,
  trap: "Reporting the EMF when the terminal potential difference is asked for."
},
{
  id: "H-04", module: "H", topic: "Opposing EMFs", diff: 2,
  q: `<p>Two cells of EMF 6.0 V and 2.0 V are connected in a single loop with a 4.0 Ω resistor, opposing each other. The cells have negligible internal resistance. What is the current in the loop?</p>
<figure class="fig">
<svg viewBox="0 0 460 250" role="img" aria-label="A single loop containing a 6 volt cell and a 2 volt cell connected positive-to-positive, in series with a 4 ohm resistor.">
<defs>
<marker id="oe-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
<path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/>
</marker>
</defs>
<text x="230" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Two cells in one loop</text>

<line x1="100" y1="76" x2="210" y2="76" stroke="#1f2937" stroke-width="2"/>
<line x1="270" y1="76" x2="380" y2="76" stroke="#1f2937" stroke-width="2"/>
<rect x="210" y="68" width="60" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="240" y="58" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">R = 4.0 Ω</text>

<line x1="380" y1="76" x2="380" y2="196" stroke="#1f2937" stroke-width="2"/>
<line x1="380" y1="196" x2="308" y2="196" stroke="#1f2937" stroke-width="2"/>
<line x1="292" y1="196" x2="188" y2="196" stroke="#1f2937" stroke-width="2"/>
<line x1="172" y1="196" x2="100" y2="196" stroke="#1f2937" stroke-width="2"/>
<line x1="100" y1="196" x2="100" y2="76" stroke="#1f2937" stroke-width="2"/>

<line x1="172" y1="180" x2="172" y2="212" stroke="#1f2937" stroke-width="5"/>
<line x1="188" y1="176" x2="188" y2="216" stroke="#1f2937" stroke-width="2.5"/>
<text x="176" y="166" text-anchor="middle" font-size="12" font-weight="600" fill="#1f7a53">6.0 V</text>

<line x1="292" y1="176" x2="292" y2="216" stroke="#1f2937" stroke-width="2.5"/>
<line x1="308" y1="180" x2="308" y2="212" stroke="#1f2937" stroke-width="5"/>
<text x="304" y="166" text-anchor="middle" font-size="12" font-weight="600" fill="#a8641a">2.0 V</text>

<line x1="164" y1="76" x2="124" y2="76" stroke="#2f5fd0" stroke-width="2.4" marker-end="url(#oe-ar)"/>
<text x="144" y="64" text-anchor="middle" font-size="11.5" fill="#2f5fd0">I</text>

<circle cx="100" cy="76" r="3" fill="#1f2937"/>
<circle cx="100" cy="196" r="3" fill="#1f2937"/>
<circle cx="188" cy="196" r="3" fill="#1f2937"/>
<circle cx="292" cy="196" r="3" fill="#1f2937"/>

<text x="230" y="240" text-anchor="middle" font-size="11.5" fill="#7b8494">note which terminal of each cell is positive</text>
</svg>
</figure>`,
  opts: ["4.0 A", "2.0 A", "0.50 A", "1.5 A", "1.0 A"],
  ans: 4,
  sol: `<p>Because the cells oppose each other, the net EMF is their <b>difference</b>:</p>
<div class="formula">ε_net = 6.0 − 2.0 = 4.0 V</div>
<p>The total resistance in the loop is 4.0 Ω, so</p>
<div class="formula">I = ε_net/R = 4.0/4.0 = 1.0 A</div>
<p><b>Answer: E.</b></p>
<p><b>Which way does the current flow, and what happens to the smaller cell?</b> The 6.0 V cell drives the current, so it flows in the direction that cell pushes. The 2.0 V cell is therefore being driven <i>against</i> its own EMF, which means it is absorbing energy rather than supplying it — it is being charged. If the question asks about energy flow, that is the answer.</p>
<p><b>The traps.</b> Option B, 2.0 A, is what you get from <b>adding</b> the EMFs: <code>8.0/4.0 = 2.0</code>. That is the answer for cells connected the same way round, not opposing. Option A, 4.0 A, is the net EMF reported as a current.</p>
<p><b>The energy check, worth doing once.</b> The large cell delivers <code>6.0 × 1.0 = 6.0 W</code>. The resistor dissipates <code>I²R = 4.0 W</code>. The small cell absorbs <code>2.0 × 1.0 = 2.0 W</code>. And <code>6.0 = 4.0 + 2.0</code> ✓. Energy conservation checks out, which confirms both the magnitude and the direction.</p>`,
  trap: "Adding opposing EMFs. Opposing sources give the difference, and the smaller one absorbs energy."
},
{
  id: "H-05", module: "H", topic: "Reconfiguring cells", diff: 3,
  q: "Two identical cells, each of EMF <code>ε</code> and internal resistance <code>r</code>, drive a fixed external resistor <code>R</code> where <code>R</code> is much larger than <code>r</code>. The cells can be connected in series or in parallel. What is the ratio of the power delivered to <code>R</code> in the series case to that in the parallel case?",
  opts: ["8", "2", "1", "4", "16"],
  ans: 3,
  sol: `<p>Since <code>R ≫ r</code>, the internal resistance is a negligible part of the total in both cases, so <code>R_total ≈ R</code>.</p>
<p><b>Series.</b> The EMFs add, so the current is <code>2ε/R</code>, and</p>
<div class="formula">P_series ≈ (2ε/R)² R = 4ε²/R</div>
<p><b>Parallel.</b> The EMF is that of one cell, so the current is <code>ε/R</code>, and</p>
<div class="formula">P_parallel ≈ (ε/R)² R = ε²/R</div>
<p><b>Ratio.</b> <code>P_series/P_parallel = 4</code>.</p>
<p><b>Answer: D.</b></p>
<p><b>Why the factor is 4 and not 2.</b> Power goes as the <b>square</b> of the current, so doubling the EMF quadruples the power. Answering 2 is the single most common error on this type of question, and option B is there for exactly that reason.</p>
<p><b>Why the <code>R ≫ r</code> condition is essential.</b> If <code>r</code> were comparable to <code>R</code>, the parallel arrangement's much smaller internal resistance would start to matter. The exact forms are:</p>
<div class="formula">P_series = 4ε²R/(R + 2r)²      P_parallel = ε²R/(R + r/2)²</div>
<p>Setting <code>R = r</code> in these gives the <b>same</b> power for both arrangements, which is the boundary case between the two regimes and a neat result worth verifying.</p>
<p><b>The practical reading.</b> Series is better for a high-resistance load such as a lamp; parallel is better for a low-resistance, high-current load such as a starter motor, because reducing the internal resistance matters more than raising the EMF.</p>`,
  trap: "Answering 2 because the voltage doubled. Power depends on the square of the current."
},
{
  id: "H-06", module: "H", topic: "Resistivity", diff: 2,
  q: "A wire of length 2.0 m and cross-sectional area <code>1.0 × 10⁻⁶ m²</code> is made of a material of resistivity <code>1.7 × 10⁻⁸ Ω m</code>. What is its resistance?",
  opts: ["0.068 Ω", "0.34 Ω", "3.4 Ω", "0.017 Ω", "0.034 Ω"],
  ans: 4,
  sol: `<p>Use <code>R = ρL/A</code>:</p>
<div class="formula">R = (1.7 × 10⁻⁸ × 2.0)/(1.0 × 10⁻⁶)</div>
<p>Handle the digits and the powers separately. Digits: <code>1.7 × 2.0 = 3.4</code>. Powers: <code>10⁻⁸/10⁻⁶ = 10⁻²</code>. So</p>
<div class="formula">R = 3.4 × 10⁻² Ω = 0.034 Ω</div>
<p><b>Answer: E.</b></p>
<p><b>The sanity check that does not need a calculation.</b> Copper has a resistivity of order <code>10⁻⁸ Ω m</code>, and a metre of thin copper wire has a resistance of order hundredths of an ohm. So the answer must be small — well under 1 Ω. That eliminates options B and C immediately.</p>
<p><b>The traps.</b> Option B, 0.34 Ω, is a factor of ten too large — the most likely error with exponents this small. Option C, 3.4 Ω, is a hundred times too large. Option D, 0.017 Ω, is the answer for a 1 m wire. Option A, 0.068 Ω, is double the correct answer.</p>
<p><b>Why the powers-of-ten discipline matters so much here.</b> There are three exponents in play (<code>10⁻⁸</code>, <code>10⁻⁶</code>, and the implicit <code>10⁰</code> on the length), and tracking them inside a single calculation is where errors happen. Writing the digits and the powers as two separate streams, as above, is the reliable method.</p>`,
  trap: "Powers-of-ten errors. Compute the leading digits and the exponents separately."
},
{
  id: "H-07", module: "H", topic: "Rectification", diff: 3,
  q: `<p>A sinusoidal supply of peak voltage 10 V is connected through a diode to a 5.0 Ω resistor, so that half-wave rectification occurs. What is the average power dissipated in the resistor?</p>
<figure class="fig">
<svg viewBox="0 0 480 420" role="img" aria-label="A half-wave rectifier circuit, with the input sine wave and the half-wave rectified output drawn below it.">
<text x="240" y="24" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Half-wave rectification</text>

<circle cx="100" cy="110" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<path d="M89 110 Q94.5 101 100 110 Q105.5 119 111 110" fill="none" stroke="#1f2937" stroke-width="1.6"/>
<line x1="100" y1="96" x2="100" y2="75" stroke="#1f2937" stroke-width="2"/>
<line x1="100" y1="124" x2="100" y2="145" stroke="#1f2937" stroke-width="2"/>
<line x1="100" y1="75" x2="200" y2="75" stroke="#1f2937" stroke-width="2"/>
<polygon points="200,64 200,86 236,75" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="236" y1="64" x2="236" y2="86" stroke="#1f2937" stroke-width="3"/>
<line x1="236" y1="75" x2="380" y2="75" stroke="#1f2937" stroke-width="2"/>
<line x1="380" y1="75" x2="380" y2="145" stroke="#1f2937" stroke-width="2"/>
<line x1="380" y1="145" x2="260" y2="145" stroke="#1f2937" stroke-width="2"/>
<rect x="200" y="137" width="60" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="200" y1="145" x2="100" y2="145" stroke="#1f2937" stroke-width="2"/>
<text x="80" y="114" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">a.c. supply</text>
<text x="218" y="56" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">diode</text>
<text x="230" y="172" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">R = 5.0 Ω</text>

<line x1="55" y1="290" x2="452" y2="290" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="55" y1="240" x2="445" y2="240" stroke="#e2e6ed" stroke-width="1.2" stroke-dasharray="5 4"/>
<line x1="55" y1="340" x2="445" y2="340" stroke="#e2e6ed" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="50" y="244" text-anchor="end" font-size="11" fill="#7b8494">10 V</text>
<text x="50" y="294" text-anchor="end" font-size="11" fill="#7b8494">0</text>
<text x="50" y="344" text-anchor="end" font-size="11" fill="#7b8494">−10 V</text>
<text x="456" y="294" font-size="11.5" font-style="italic" fill="#7b8494">t</text>

<path d="M60 290 C94.6 223.3 120.4 223.3 155 290 C189.6 356.7 215.4 356.7 250 290 C284.6 223.3 310.4 223.3 345 290 C379.6 356.7 410.4 356.7 440 290"
 fill="none" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="6 4"/>
<path d="M60 290 C94.6 223.3 120.4 223.3 155 290 L250 290 C284.6 223.3 310.4 223.3 345 290 L440 290"
 fill="none" stroke="#2f5fd0" stroke-width="2.6"/>

<line x1="60" y1="378" x2="100" y2="378" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="6 4"/>
<text x="108" y="382" font-size="11.5" fill="#4a5262">supply voltage</text>
<line x1="250" y1="378" x2="290" y2="378" stroke="#2f5fd0" stroke-width="2.6"/>
<text x="298" y="382" font-size="11.5" fill="#4a5262">voltage across R</text>
</svg>
</figure>`,
  opts: ["10 W", "5.0 W", "20 W", "2.5 W", "40 W"],
  ans: 1,
  sol: `<p>For a sinusoid of peak voltage <code>V₀</code>, the average of <code>V²</code> over a full cycle is <code>V₀²/2</code>. Half-wave rectification allows current during only half the cycle, so the average of <code>V²</code> falls to <code>V₀²/4</code>.</p>
<div class="formula">P_avg = V₀²/(4R) = 100/(4 × 5.0) = 100/20 = 5.0 W</div>
<p><b>Answer: B.</b></p>
<p><b>The three cases, worth having side by side.</b></p>
<table><thead><tr><th>Supply</th><th>Average of <code>V²</code></th><th>Average power here</th></tr></thead><tbody>
<tr><td>full sine wave</td><td><code>V₀²/2</code></td><td>10 W</td></tr>
<tr><td>half-wave rectified</td><td><code>V₀²/4</code></td><td><b>5.0 W</b></td></tr>
<tr><td>square wave <code>±V₀</code></td><td><code>V₀²</code></td><td>20 W</td></tr>
</tbody></table>
<p>Both of the other values appear as options, which is what makes the question discriminate properly.</p>
<p><b>The mistake to avoid.</b> Do not average the <i>voltage</i> and then square it. The average of a sinusoid is zero, so that route gives zero power — plainly wrong. You must average the <b>square</b> of the voltage, which is never negative. The distinction between the mean and the mean square is exactly what this topic tests.</p>
<p><b>The physical reading.</b> Half-wave rectification halves the average power, because the resistor is doing nothing for half of every cycle. That is a real inefficiency, and it is why practical rectifier circuits use four diodes in a bridge to rectify both half-cycles.</p>`,
  trap: "Averaging the voltage rather than its square, or forgetting that half-wave rectification halves the power again."
},
{
  id: "H-08", module: "H", topic: "Potential divider", diff: 1,
  q: `<p>A 2.0 kΩ resistor and a 4.0 kΩ resistor are connected in series across a 12 V supply. What is the potential difference across the 4.0 kΩ resistor?</p>
<figure class="fig">
<svg viewBox="0 0 460 262" role="img" aria-label="A 12 volt supply connected across a 2 kilohm and a 4 kilohm resistor in series, with the output taken across the 4 kilohm resistor.">
<text x="230" y="24" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">A potential divider</text>

<text x="230" y="42" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f7a53">12 V</text>
<line x1="220" y1="52" x2="240" y2="52" stroke="#1f2937" stroke-width="5"/>
<line x1="212" y1="64" x2="248" y2="64" stroke="#1f2937" stroke-width="2.5"/>
<line x1="230" y1="64" x2="230" y2="86" stroke="#1f2937" stroke-width="2"/>
<line x1="220" y1="52" x2="104" y2="52" stroke="#1f2937" stroke-width="2"/>
<line x1="104" y1="52" x2="104" y2="228" stroke="#1f2937" stroke-width="2"/>
<line x1="104" y1="228" x2="230" y2="228" stroke="#1f2937" stroke-width="2"/>
<rect x="214" y="86" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="256" y="112" font-size="12.5" font-weight="600" fill="#2f5fd0">R₁ = 2.0 kΩ</text>
<line x1="230" y1="130" x2="230" y2="166" stroke="#1f2937" stroke-width="2"/>
<circle cx="230" cy="148" r="3.2" fill="#1f2937"/>
<rect x="214" y="166" width="32" height="44" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="256" y="192" font-size="12.5" font-weight="600" fill="#2f5fd0">R₂ = 4.0 kΩ</text>
<line x1="230" y1="210" x2="230" y2="228" stroke="#1f2937" stroke-width="2"/>
<circle cx="230" cy="228" r="3.2" fill="#1f2937"/>

<line x1="230" y1="148" x2="392" y2="148" stroke="#2f5fd0" stroke-width="1.8"/>
<line x1="230" y1="228" x2="392" y2="228" stroke="#2f5fd0" stroke-width="1.8"/>
<line x1="392" y1="148" x2="392" y2="228" stroke="#2f5fd0" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="404" y="193" font-size="12.5" font-weight="600" fill="#2f5fd0">V_out</text>

<text x="230" y="252" text-anchor="middle" font-size="11.5" fill="#7b8494">the supply splits in the ratio of the two resistances</text>
</svg>
</figure>`,
  opts: ["8.0 V", "4.0 V", "6.0 V", "12 V", "3.0 V"],
  ans: 0,
  sol: `<p>Use the potential divider formula with the output across <code>R₂ = 4.0 kΩ</code>:</p>
<div class="formula">V_out = V_in × R₂/(R₁ + R₂) = 12 × 4.0/(2.0 + 4.0) = 12 × 4.0/6.0 = 8.0 V</div>
<p><b>Answer: A.</b></p>
<p><b>The reasoning that gives it in five seconds.</b> The two resistors are in a 1:2 ratio, so they split the 12 V in a 1:2 ratio — that is, 4 V and 8 V. The larger voltage goes across the larger resistance. So the 4.0 kΩ resistor takes 8.0 V and the 2.0 kΩ takes 4.0 V.</p>
<p><b>The traps.</b> Option B, 4.0 V, is the voltage across the <i>other</i> resistor — the answer you get from putting the wrong resistance in the numerator. Option C, 6.0 V, is the equal split, which would require equal resistances.</p>
<p><b>Why the kilohms do not need converting.</b> The formula contains the ratio <code>R₂/(R₁ + R₂)</code>, which is dimensionless. Since both resistances are in the same unit, the units cancel and no conversion is needed. That is a genuine time-saver and worth noticing.</p>
<p><b>The limiting checks.</b> If the 4.0 kΩ resistor were much larger than the other, the output would approach the full 12 V. If it were much smaller, the output would approach zero. Here it is twice the other, so the output is two thirds of the supply ✓.</p>`,
  trap: "Putting the wrong resistance in the numerator of the divider formula."
},
{
  id: "H-09", module: "H", topic: "Network reduction", diff: 3,
  q: `<p>A wire loop of total resistance 12 Ω has a sliding contact that can be moved round it. What is the maximum equivalent resistance measurable between the contact and a fixed point on the loop?</p>
<figure class="fig">
<svg viewBox="0 0 460 258" role="img" aria-label="A circular wire loop with a fixed point A and a movable contact B, dividing the loop into two arcs.">
<text x="230" y="24" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">One loop, two arcs, one measurement</text>

<circle cx="190" cy="138" r="78" fill="none" stroke="#e2e6ed" stroke-width="1.5"/>
<path d="M190 60 A78 78 0 0 1 257.5 177" fill="none" stroke="#2f5fd0" stroke-width="3.2"/>
<path d="M190 60 A78 78 0 1 0 257.5 177" fill="none" stroke="#a8641a" stroke-width="3.2"/>

<circle cx="190" cy="60" r="4.2" fill="#1f2937"/>
<circle cx="257.5" cy="177" r="4.2" fill="#1f2937"/>
<text x="190" y="48" text-anchor="middle" font-size="13" font-weight="700" fill="#14181f">A</text>
<text x="272" y="190" font-size="13" font-weight="700" fill="#14181f">B</text>

<text x="274" y="104" font-size="12.5" font-weight="600" fill="#2f5fd0">12x</text>
<text x="106" y="182" text-anchor="end" font-size="12.5" font-weight="600" fill="#a8641a">12(1 − x)</text>
<text x="274" y="120" font-size="10.5" fill="#7b8494">shorter arc</text>
<text x="106" y="198" text-anchor="end" font-size="10.5" fill="#7b8494">longer arc</text>

<text x="230" y="244" text-anchor="middle" font-size="11.5" fill="#7b8494">both arcs connect the same pair of points, so they are in parallel</text>
</svg>
</figure>`,
  opts: ["6.0 Ω", "3.0 Ω", "12 Ω", "1.5 Ω", "4.0 Ω"],
  ans: 1,
  sol: `<p>The contact divides the loop into two arcs. If a fraction <code>x</code> of the total length lies on one side, the arc resistances are <code>12x</code> and <code>12(1 − x)</code>.</p>
<p>These two arcs are in <b>parallel</b> between the two measurement points, so</p>
<div class="formula">R_eq = xR(1 − x)R/(xR + (1 − x)R) = x(1 − x)R</div>
<p>with <code>R = 12 Ω</code>. The product <code>x(1 − x)</code> is maximised at <code>x = ½</code>, where it equals ¼. So</p>
<div class="formula">R_max = ¼ × 12 = 3.0 Ω</div>
<p><b>Answer: B.</b></p>
<p><b>Check the extremes.</b> At <code>x = 0</code> or <code>x = 1</code> the contact coincides with the fixed point, so the resistance is zero ✓. At the midpoint the answer is <code>R/4</code> ✓. Both limits match the formula, which confirms the structure.</p>
<p><b>The traps.</b> Option C, 12 Ω, is the resistance of the whole loop — the answer you get by forgetting that the two arcs are in parallel. Option A, 6.0 Ω, is <code>R/2</code>, which is what you get by taking the arithmetic mean of the two arc resistances rather than their parallel combination.</p>
<p><b>Why the technique matters more than the result.</b> The move here is recognising that two paths between the same pair of points must be in parallel. That same recognition is what collapses a balanced bridge, a square with diagonals, and most other awkward networks. The specific result <code>R/4</code> is worth remembering, but the technique is worth more.</p>`,
  trap: "Adding the two arcs instead of combining them in parallel."
},
{
  id: "H-10", module: "H", topic: "Power in series", diff: 2,
  q: "A 2.0 Ω resistor and a 4.0 Ω resistor are connected in series with a battery. What is the ratio of the power dissipated in the 4.0 Ω resistor to that in the 2.0 Ω resistor?",
  opts: ["4", "0.5", "2", "1", "8"],
  ans: 2,
  sol: `<p>In series, the <b>current</b> is the same through both resistors, so use the form of the power equation containing <code>I</code>:</p>
<div class="formula">P = I²R</div>
<p>Since <code>I²</code> is common, <code>P ∝ R</code>:</p>
<div class="formula">P₄/P₂ = R₄/R₂ = 4.0/2.0 = 2</div>
<p><b>Answer: C.</b></p>
<p><b>The general result, which is the real content of the question.</b> In a <b>series</b> circuit the largest resistance dissipates the most power. In a <b>parallel</b> circuit the largest resistance dissipates the <b>least</b>. Getting that backwards is extremely common, and the reason is that the shared quantity is different: current in series, voltage in parallel.</p>
<p><b>Why the parallel case reverses.</b> In parallel the voltage is shared, so <code>P = V²/R</code> and power is <b>inversely</b> proportional to resistance. The 4.0 Ω resistor would then dissipate <i>half</i> the power of the 2.0 Ω one — a ratio of 0.5, which is option B, present as a distractor.</p>
<p><b>How to remember it.</b> Ask which quantity is common. If it is the current (series), use <code>I²R</code> and the bigger resistor wins. If it is the voltage (parallel), use <code>V²/R</code> and the smaller resistor wins. That reasoning takes five seconds and never fails.</p>`,
  trap: "Using P = V²/R in a series circuit, which reverses the answer."
},
{
  id: "H-11", module: "H", topic: "Superconductivity", diff: 1,
  q: "Which of the following is a correct statement about superconductivity?",
  opts: ["Below a critical temperature the resistance becomes exactly zero", "Resistance falls gradually to a small but non-zero value", "The material becomes an insulator below the critical temperature", "The critical temperature is the same for all superconductors", "Resistance is exactly zero at all temperatures above the critical temperature"],
  ans: 0,
  sol: `<p>Below a critical temperature, a superconductor has <b>exactly zero</b> resistance — not small, zero.</p>
<p><b>Answer: A.</b></p>
<p><b>Why "exactly zero" is the important phrase.</b> A current started in a closed superconducting loop persists indefinitely with no source and no measurable decay. That is qualitatively different from a merely small resistance, which would cause the current to die away over time. The distinction is the whole content of the definition.</p>
<p><b>Why the others are wrong.</b> Option B describes ordinary metallic behaviour, where resistance falls with temperature but never reaches zero. Option C reverses the effect entirely. Option D is false because the critical temperature varies enormously between materials — from a few kelvin for the classic superconductors to well above 77 K for the high-temperature ones, which is what made them commercially useful. Option E is backwards.</p>
<p><b>Why this is in scope.</b> Superconductivity sits inside AQA AS §3.5.1.3, which makes it part of "Year 12 topics" and therefore fair game for Round 0. It was promoted from insurance material to core content for exactly that reason.</p>
<p><b>The applications follow from the definition.</b> Zero resistance means no resistive heating, so a superconducting electromagnet can carry a large current indefinitely without needing continuous cooling to remove heat — and can therefore produce much stronger fields than a conventional one. Loss-free power transmission is the other standard application.</p>`,
  trap: "Saying the resistance becomes 'very small'. It becomes exactly zero, which is qualitatively different."
},

/* ===================== MODULE I — capacitors ===================== */

{
  id: "I-01", module: "I", topic: "Capacitance", diff: 1,
  q: "A capacitor of capacitance 5.0 μF is charged to a potential difference of 12 V. What charge is stored on one plate?",
  opts: ["2.4 μC", "60 μC", "0.42 μC", "600 μC", "17 μC"],
  ans: 1,
  sol: `<p>Use <code>Q = CV</code>:</p>
<div class="formula">Q = 5.0 × 10⁻⁶ × 12 = 60 × 10⁻⁶ C = 60 μC</div>
<p><b>Answer: B.</b></p>
<p><b>The mental route.</b> <code>5 × 12 = 60</code>, and the prefix <code>μ</code> carries through unchanged. There is no need to write the powers of ten at all if both quantities are handled in their prefixed forms consistently.</p>
<p><b>The meaning of "on one plate".</b> The two plates carry equal and opposite charges, so the net charge on a capacitor is always zero. When a question asks about "the charge on a capacitor", it means the magnitude on one plate. The phrasing matters because a question could ask about the net charge, and the answer would then be zero.</p>
<p><b>The traps.</b> Option A, 2.4 μC, comes from dividing instead of multiplying. Option D, 600 μC, is a factor of ten too large. Option E, 17 μC, is <code>12/5 × 7</code>-ish, an arithmetic slip.</p>
<p><b>The related quantities to keep distinct.</b> Charge <code>Q</code> in coulombs, potential difference <code>V</code> in volts, capacitance <code>C</code> in farads. The farad is a coulomb per volt, so <code>60 μC / 12 V = 5 μF</code> ✓ — a quick confirmation that the three quantities are consistent.</p>`,
  trap: "Dividing by V instead of multiplying, or confusing the charge on one plate with the net charge."
},
{
  id: "I-02", module: "I", topic: "Capacitors in parallel", diff: 1,
  q: "A 2.0 μF capacitor and a 3.0 μF capacitor are connected in parallel. What is the combined capacitance?",
  opts: ["2.5 μF", "1.2 μF", "6.0 μF", "5.0 μF", "0.83 μF"],
  ans: 3,
  sol: `<p>Capacitors in parallel add:</p>
<div class="formula">C_total = C₁ + C₂ = 2.0 + 3.0 = 5.0 μF</div>
<p><b>Answer: D.</b></p>
<p><b>Why parallel adds, physically.</b> In parallel, both capacitors have the same potential difference, so the total charge stored is the sum of the individual charges. Putting capacitors in parallel is equivalent to making one capacitor with a larger plate area, and larger area means more capacitance.</p>
<p><b>The contrast with series.</b> In series the capacitors carry the same charge and the voltages add, giving <code>1/C = 1/2 + 1/3</code>, so <code>C = 1.2 μF</code> — which is option B, present deliberately. Note that the series combination is smaller than the smaller capacitor, which is the standard sanity check.</p>
<p><b>The memory hook.</b> Capacitors combine the <b>opposite</b> way to resistors: parallel adds, series reciprocal-adds. Springs behave the same way as capacitors. If you remember one of the three, you can reconstruct the others by asking which quantity is shared.</p>
<p><b>The traps.</b> Option B, 1.2 μF, is the series result. Option A, 2.5 μF, is the arithmetic mean. Option E, 0.83 μF, is the reciprocal of the sum.</p>`,
  trap: "Using the series rule for a parallel arrangement. Capacitors are the opposite of resistors."
},
{
  id: "I-03", module: "I", topic: "Energy stored", diff: 2,
  q: "A 4.0 μF capacitor is charged to a potential difference of 10 V. How much energy is stored?",
  opts: ["200 μJ", "400 μJ", "20 μJ", "2.0 mJ", "40 μJ"],
  ans: 0,
  sol: `<p>Use <code>E = ½CV²</code>:</p>
<div class="formula">E = ½ × 4.0 × 10⁻⁶ × 10² = ½ × 4.0 × 10⁻⁶ × 100 = 200 × 10⁻⁶ J = 200 μJ</div>
<p><b>Answer: A.</b></p>
<p><b>Why the factor of ½ is there.</b> Charging a capacitor means pushing charge onto a plate that is already at a potential, and the potential rises from zero to <code>V</code> as the charge accumulates. The work done is the area of a triangle on a charge–voltage graph, which gives the factor of ½. The same factor appears in kinetic energy, elastic strain energy and here — it is the signature of a quantity ramping linearly from zero.</p>
<p><b>The traps.</b> Option B, 400 μJ, is <code>CV²</code> without the half — the answer you get by assuming the charge was pushed on at full voltage throughout. Option D, 2.0 mJ, is a factor of ten too large, from treating the microfarad as a millifarad.</p>
<p><b>The cross-check by another route.</b> The charge is <code>Q = CV = 40 μC</code>. Then <code>E = ½QV = ½ × 40 × 10⁻⁶ × 10 = 200 μJ</code> ✓. Taking the second route when time allows is a free confirmation.</p>
<p><b>The practical magnitude.</b> 200 μJ is a very small amount of energy — about the kinetic energy of a grain of sand falling a few centimetres. Capacitors store far less energy than batteries of comparable size, which is why they are used for short bursts of power rather than long-term storage.</p>`,
  trap: "Using CV² instead of ½CV². The voltage ramps from zero, so the factor of ½ is required."
},
{
  id: "I-04", module: "I", topic: "Capacitors in series", diff: 1,
  q: "Two capacitors of 6.0 μF each are connected in series. What is the combined capacitance?",
  opts: ["1.5 μF", "12 μF", "6.0 μF", "3.0 μF", "36 μF"],
  ans: 3,
  sol: `<p>For two capacitors in series, use the product-over-sum form:</p>
<div class="formula">C_series = (6.0 × 6.0)/(6.0 + 6.0) = 36/12 = 3.0 μF</div>
<p>Or equivalently, for two <i>identical</i> capacitors in series the combination is half of one: <code>6.0/2 = 3.0 μF</code>.</p>
<p><b>Answer: D.</b></p>
<p><b>Why series reduces capacitance.</b> In series the capacitors carry the same charge, and the total voltage is the sum of the individual voltages. A larger voltage for the same charge means a smaller capacitance — so the combination is always smaller than the smallest individual capacitor. Putting capacitors in series is equivalent to increasing the plate separation, which reduces capacitance.</p>
<p><b>The sanity check.</b> The answer must be less than 6.0 μF. That eliminates options B and C immediately, and the identical-capacitor shortcut confirms 3.0 μF.</p>
<p><b>The traps.</b> Option B, 12 μF, is the parallel result. Option A, 1.5 μF, is a quarter rather than a half. Option E, 36 μF, is the product without dividing by the sum.</p>
<p><b>The rule worth remembering.</b> For <code>n</code> identical capacitors of value <code>C</code> in series, the combination is <code>C/n</code>. Exactly the same as for identical resistors in parallel, which is a useful parallel to notice.</p>`,
  trap: "Using the parallel rule for a series arrangement, or forgetting the sanity check."
},

/* ===================== MODULE J — thermal ===================== */

{
  id: "J-01", module: "J", topic: "Specific heat capacity", diff: 1,
  q: "How much energy is needed to raise the temperature of 0.50 kg of a metal of specific heat capacity <code>900 J kg⁻¹ K⁻¹</code> by 20 K?",
  opts: ["90 kJ", "18 kJ", "4.5 kJ", "9.0 kJ", "1.8 kJ"],
  ans: 3,
  sol: `<p>Use <code>Q = mcΔT</code>:</p>
<div class="formula">Q = 0.50 × 900 × 20 = 9000 J = 9.0 kJ</div>
<p><b>Answer: D.</b></p>
<p><b>The mental route.</b> <code>0.5 × 900 = 450</code>, then <code>450 × 20 = 9000</code>. Both steps are easy, and tracking the thousands separately keeps the arithmetic clean.</p>
<p><b>The trap.</b> Option B, 18 kJ, is exactly double and comes from using <code>m = 1.0 kg</code> instead of 0.50 kg. Option C, 4.5 kJ, is half the correct answer. Both are factors-of-two slips, which are the commonest error in this topic after <code>ΔT</code> mistakes.</p>
<p><b>Why ΔT needs no conversion.</b> A temperature <i>change</i> of 20 K is the same as a change of 20 °C. Only absolute temperatures need the 273 conversion, and this formula uses a difference. So there is no conversion step here at all — a genuine saving.</p>
<p><b>A physical anchor for the magnitude.</b> 9 kJ would raise 0.5 kg of water by about 4.3 K, since water's specific heat capacity is 4200 against the metal's 900. So for the same energy, the metal heats up nearly five times as much. That is why metals feel hot quickly and water takes a long time to boil.</p>`,
  trap: "Using the final temperature instead of the temperature change, or a factor-of-two error in the mass."
},
{
  id: "J-02", module: "J", topic: "Latent heat", diff: 1,
  q: "How much energy is needed to melt 0.20 kg of ice at 0 °C? The specific latent heat of fusion of water is <code>3.34 × 10⁵ J kg⁻¹</code>.",
  opts: ["6.7 kJ", "67 kJ", "670 kJ", "33 kJ", "134 kJ"],
  ans: 1,
  sol: `<p>Use <code>Q = mL</code>:</p>
<div class="formula">Q = 0.20 × 3.34 × 10⁵ = 6.68 × 10⁴ J ≈ 67 kJ</div>
<p><b>Answer: B.</b></p>
<p><b>The mental route.</b> <code>0.2 × 3.34 = 0.668</code>, then <code>× 10⁵ = 6.68 × 10⁴</code>. Converting to kilojoules gives 66.8 kJ.</p>
<p><b>Why there is no temperature term.</b> Melting happens at constant temperature. The energy goes into breaking the bonds holding the molecules in their lattice, not into increasing their kinetic energy — which is why the temperature does not change during the phase transition. Using <code>Q = mcΔT</code> here would be wrong, because <code>ΔT</code> is zero.</p>
<p><b>The comparison that matters.</b> The latent heat of <b>vaporisation</b> of water is <code>2.26 × 10⁶ J kg⁻¹</code>, nearly seven times the latent heat of fusion. So boiling 0.20 kg of water would take about 450 kJ against the 67 kJ needed to melt the same mass. Melting only loosens the molecular arrangement; boiling separates the molecules entirely. That comparison is a common question.</p>
<p><b>The traps.</b> Option A, 6.7 kJ, is a factor of ten too small — a powers-of-ten slip, which is the most likely error with an exponent of <code>10⁵</code>. Option D, 33 kJ, uses <code>m = 0.1 kg</code>. Option E, 134 kJ, uses <code>m = 0.4 kg</code>.</p>`,
  trap: "Using Q = mcΔT for a phase change, or a powers-of-ten slip with the latent heat."
},
{
  id: "J-03", module: "J", topic: "Ideal gas law", diff: 2,
  q: "A fixed mass of gas occupies 1.0 m³ at a pressure of <code>1.0 × 10⁵ Pa</code> and a temperature of 300 K. What volume does it occupy at a pressure of <code>2.0 × 10⁵ Pa</code> and a temperature of 600 K?",
  opts: ["1.0 m³", "2.0 m³", "0.50 m³", "4.0 m³", "0.25 m³"],
  ans: 0,
  sol: `<p>For a fixed mass of gas, <code>pV/T</code> is constant, so <code>p₁V₁/T₁ = p₂V₂/T₂</code>. Rearranging:</p>
<div class="formula">V₂ = V₁ × (p₁/p₂) × (T₂/T₁) = 1.0 × (1.0/2.0) × (600/300) = 1.0 × 0.5 × 2.0 = 1.0 m³</div>
<p><b>Answer: A.</b></p>
<p><b>Reason about the two effects separately, and the answer becomes obvious.</b> Doubling the pressure alone would halve the volume, to 0.50 m³. Doubling the absolute temperature alone would double the volume, back to 1.0 m³. The two effects exactly cancel, so the volume is unchanged. Doing it in two conceptual steps is both faster and far less error-prone than substituting into the combined formula.</p>
<p><b>Why this is a good question.</b> The answer being the same as the starting volume feels wrong to many candidates, who expect that changing two variables must change the result. Recognising that the changes are in opposite directions and of equal magnitude is the insight being tested.</p>
<p><b>The traps.</b> Option B, 2.0 m³, is the answer you get from applying only the temperature change. Option C, 0.50 m³, is the answer from applying only the pressure change. Option E, 0.25 m³, applies the pressure ratio twice.</p>
<p><b>The kelvin reminder.</b> The temperatures here are already in kelvin. Had they been given in Celsius, converting first would be essential — and the ratio would be quite different, since 600 °C is 873 K.</p>`,
  trap: "Applying only one of the two changes, or inverting the temperature ratio."
},
{
  id: "J-04", module: "J", topic: "Pressure and equilibrium", diff: 2,
  q: "A gas is trapped in a cylinder by a piston of area <code>0.010 m²</code> and mass 5.0 kg. The atmospheric pressure is <code>1.0 × 10⁵ Pa</code>. What is the pressure of the gas? Use <code>g = 10 m s⁻²</code>.",
  opts: ["5.0 × 10⁵ Pa", "1.5 × 10⁵ Pa", "1.05 × 10⁵ Pa", "1.0 × 10⁵ Pa", "1.005 × 10⁵ Pa"],
  ans: 2,
  sol: `<p>At equilibrium, the gas pressure supports both the atmosphere and the piston's weight. The pressure from the piston is its weight divided by the area:</p>
<div class="formula">p_piston = mg/A = (5.0 × 10)/0.010 = 50/0.010 = 5000 Pa</div>
<p>So the total gas pressure is</p>
<div class="formula">p = 1.0 × 10⁵ + 5.0 × 10³ = 1.05 × 10⁵ Pa</div>
<p><b>Answer: C.</b></p>
<p><b>Why the area matters here but not in hydrostatics.</b> In a liquid at depth, the area cancelled out of the derivation of <code>p = ρgh</code>. Here the piston's weight is fixed but the area over which it is spread is not, so the area genuinely matters. Noticing which situation you are in is part of the question.</p>
<p><b>The traps.</b> Option D, <code>1.0 × 10⁵ Pa</code>, is the atmospheric pressure alone, forgetting the piston. Option E, <code>1.005 × 10⁵ Pa</code>, is what you get from using the piston's <i>mass</i> rather than its weight. Option B, <code>1.5 × 10⁵ Pa</code>, and option A are arithmetic slips.</p>
<p><b>The related shape worth knowing.</b> For a gas trapped in a tube by a column of liquid, the same structure applies with <code>p = p_atm + ρgh</code>. That links this module directly back to module M, and a question that combines the two is exactly the kind of linking question a competition paper likes.</p>`,
  trap: "Using the piston's mass rather than its weight, or forgetting the atmospheric pressure."
},

/* ===================== MODULE K — nuclear ===================== */

{
  id: "K-01", module: "K", topic: "Nuclear notation", diff: 1,
  q: "How many neutrons are there in a nucleus of <code>²³⁵₉₂U</code>?",
  opts: ["327", "92", "235", "143", "235.0"],
  ans: 3,
  sol: `<p>The superscript is the nucleon number <code>A</code>, the total number of protons and neutrons. The subscript is the proton number <code>Z</code>.</p>
<div class="formula">neutrons = A − Z = 235 − 92 = 143</div>
<p><b>Answer: D.</b></p>
<p><b>The notation convention, worth stating explicitly.</b> <code>A</code> is the larger number and goes on top; <code>Z</code> is the smaller number and goes underneath. A common slip is to swap them, which would give 92 as the neutron count — option B, present as a distractor.</p>
<p><b>Why uranium-235 is important.</b> It is the fissile isotope used in nuclear reactors, and it makes up only about 0.7% of natural uranium, the rest being uranium-238. That low abundance is why enrichment is needed. The nuclear notation is the entry point to all of that.</p>
<p><b>The traps.</b> Option B, 92, is the proton number, not the neutron count. Option C, 235, is the nucleon number. Option A, 327, is <code>A + Z</code>, which is what you get by adding instead of subtracting. Option E is the nucleon number expressed with a spurious decimal.</p>
<p><b>The related skill.</b> Given a notation, you should be able to state the number of protons, the number of neutrons, and the charge on the bare nucleus (<code>+Ze</code>) without hesitation. Those three facts cover nearly every question that begins with a nuclear symbol.</p>`,
  trap: "Swapping A and Z, or adding them instead of subtracting."
},
{
  id: "K-02", module: "K", topic: "Specific charge", diff: 2,
  q: "What is the specific charge of a proton? Use <code>e = 1.6 × 10⁻¹⁹ C</code> and <code>m_p = 1.67 × 10⁻²⁷ kg</code>.",
  opts: ["5.7 × 10⁸ C kg⁻¹", "1.8 × 10¹¹ C kg⁻¹", "4.8 × 10⁷ C kg⁻¹", "1.6 × 10⁻¹⁹ C kg⁻¹", "9.6 × 10⁷ C kg⁻¹"],
  ans: 4,
  sol: `<p>Specific charge is charge divided by mass:</p>
<div class="formula">Q/m = 1.6 × 10⁻¹⁹ / 1.67 × 10⁻²⁷</div>
<p>Handle the digits and the powers separately. Digits: <code>1.6/1.67 ≈ 0.96</code>. Powers: <code>10⁻¹⁹/10⁻²⁷ = 10⁸</code>. So</p>
<div class="formula">Q/m ≈ 9.6 × 10⁷ C kg⁻¹</div>
<p><b>Answer: E.</b></p>
<p><b>Why this value is worth memorising.</b> It appears whenever a charged particle is deflected in a field, and it lets you compare the deflection of different particles instantly. The electron's specific charge is about 1800 times larger, at <code>1.8 × 10¹¹ C kg⁻¹</code> — option B, present as the electron's value.</p>
<p><b>Why the electron's value is so much larger.</b> The electron carries the same magnitude of charge as the proton but in about <code>1/1800</code> of the mass. That is why electrons are deflected far more than protons in the same field, and it is the basis of the historical measurement of the electron's mass-to-charge ratio.</p>
<p><b>The nucleus comparison.</b> A helium nucleus, <code>⁴₂He</code>, has specific charge <code>2e/(4u) = e/(2u)</code> — half the proton's, at <code>4.8 × 10⁷ C kg⁻¹</code> (option C). A nucleus always has a lower specific charge than a lone proton, because neutrons add mass without adding charge.</p>
<p><b>The remaining two options.</b> Option A, <code>5.7 × 10⁸ C kg⁻¹</code>, is the proton's specific charge multiplied by about six — the sort of number you reach by dividing the mass by the charge instead of the other way round and then adjusting the power of ten to compensate. Option D, <code>1.6 × 10⁻¹⁹ C kg⁻¹</code>, is simply the charge <code>e</code> on its own: the elementary charge, not a charge-to-mass ratio at all. It is there to catch anyone who reads "specific charge" as "charge" and stops. The units in the answer — <code>C kg⁻¹</code> rather than <code>C</code> — rule it out before any arithmetic.</p>`,
  trap: "Confusing the proton's specific charge with the electron's, which is about 1800 times larger."
},
{
  id: "K-03", module: "K", topic: "Alpha decay", diff: 2,
  q: "A nucleus of <code>²²⁶₈₈Ra</code> undergoes alpha decay. What is the resulting nucleus?",
  opts: ["²²²₈₆Rn", "²²²₈₈Ra", "²²⁶₈₆Rn", "²²²₈₄Po", "²³⁰₉₀Th"],
  ans: 0,
  sol: `<p>An alpha particle is <code>⁴₂He</code>. Balance <code>A</code> and <code>Z</code> separately:</p>
<div class="formula">A: 226 = A_daughter + 4   →   A_daughter = 222
Z:  88 = Z_daughter + 2   →   Z_daughter = 86</div>
<p>The element with <code>Z = 86</code> is radon, Rn.</p>
<p><b>Answer: A, <code>²²²₈₆Rn</code>.</b></p>
<p><b>The structural pattern, which lets you answer without arithmetic.</b> Alpha decay always reduces <code>A</code> by 4 and <code>Z</code> by 2, so the daughter is always four mass units lighter and two places to the <b>left</b> in the periodic table. Recognising that pattern narrows the options instantly.</p>
<p><b>The traps.</b> Option B, <code>²²²₈₈Ra</code>, has the right <code>A</code> but the wrong <code>Z</code> — the error of removing mass without removing protons. Option C, <code>²²⁶₈₆Rn</code>, has the right <code>Z</code> but forgot to reduce <code>A</code>. Both are single-omission errors and both are present deliberately.</p>
<p><b>Where this leads.</b> Radon-222 is itself radioactive, and it is the gas that seeps from granite rocks and accounts for the largest single contribution to background radiation in many regions. The decay chain continues through polonium to lead-206, and the whole series is a standard topic in module K's background-radiation section.</p>`,
  trap: "Changing only one of A or Z. Both must be reduced by the alpha particle's contribution."
},
{
  id: "K-04", module: "K", topic: "Beta decay", diff: 2,
  q: "Carbon-14, <code>¹⁴₆C</code>, undergoes beta-minus decay. What is the proton number of the daughter nucleus?",
  opts: ["6", "5", "7", "14", "8"],
  ans: 2,
  sol: `<p>In beta-minus decay a neutron converts into a proton, emitting an electron and an antineutrino:</p>
<div class="formula">n → p + e⁻ + ν̄</div>
<p>The nucleon number <code>A</code> is unchanged, and the proton number <code>Z</code> <b>increases by 1</b>:</p>
<div class="formula">¹⁴₆C → ¹⁴₇N + ⁰₋₁e + ν̄</div>
<p><b>Answer: C, Z = 7</b>, which is nitrogen.</p>
<p><b>The sign trap, and it is the whole point of the question.</b> It is tempting to think that emitting a negatively charged particle must reduce the nuclear charge. It does not — the electron is <i>created</i> in the decay rather than removed from the nucleus, and the proton count simultaneously increases. Getting this backwards gives <code>Z = 5</code>, which is option B.</p>
<p><b>Why the antineutrino is essential.</b> If only an electron were emitted, its energy would be fixed by the mass difference between parent and daughter. In practice beta particles emerge with a <b>continuous range</b> of energies up to a maximum, and momentum would not balance either. Both problems are solved by a third, nearly massless neutral particle carrying away the missing energy and momentum. That is the historical argument for the neutrino.</p>
<p><b>The balancing check.</b> On the right, <code>A = 14 + 0 = 14</code> ✓ and <code>Z = 7 + (−1) = 6</code> ✓. The electron's <code>Z</code> of −1 is what makes the books balance.</p>`,
  trap: "Thinking the proton number decreases because a negative electron is emitted. It increases."
},
{
  id: "K-05", module: "K", topic: "Mass–energy equivalence", diff: 2,
  q: "A nuclear reaction converts a mass of 0.010 u into energy. How much energy is released? Use <code>1 u ≡ 931 MeV</code>.",
  opts: ["1.5 × 10⁻¹² MeV", "0.010 MeV", "93 MeV", "931 MeV", "9.3 MeV"],
  ans: 4,
  sol: `<p>Use the conversion directly:</p>
<div class="formula">E = 0.010 × 931 = 9.31 MeV</div>
<p><b>Answer: E, about 9.3 MeV.</b></p>
<p><b>Why the conversion is worth memorising.</b> Nuclear masses are quoted in <code>u</code> and nuclear energies in MeV, so <code>1 u ≡ 931 MeV</code> lets you move between them with one multiplication. Converting to kilograms and using <code>E = mc²</code> would take three steps and introduce three chances of a powers-of-ten error. On a no-calculator paper that difference is decisive.</p>
<p><b>Why the conversion factor is 931.</b> Substituting <code>1 u = 1.66 × 10⁻²⁷ kg</code> and <code>c = 3.00 × 10⁸ m s⁻¹</code> into <code>E = mc²</code> gives <code>1.49 × 10⁻¹⁰ J</code>. Dividing by <code>1.6 × 10⁻¹⁹</code> to convert to electron volts gives <code>9.3 × 10⁸ eV</code>, or 931 MeV.</p>
<p><b>The physical magnitude check.</b> A few MeV per nuclear reaction is typical — compare a chemical reaction, where the energy release is of order a few eV. The ratio of about a million is why nuclear energy is so much more concentrated than chemical energy. If your answer had come out in the electron-volt range, the conversion would have gone wrong.</p>
<p><b>The traps.</b> Option B is the mass defect reported as an energy. Option D, 931 MeV, is the conversion factor itself, corresponding to a mass defect of 1 u — far too large for a single reaction.</p>`,
  trap: "Using E = mc² with kilograms when the u to MeV conversion would do it in one step."
},

/* ===================== MODULE L — quantum ===================== */

{
  id: "L-01", module: "L", topic: "Photon energy", diff: 1,
  q: "What is the energy of a photon of wavelength 500 nm? Use <code>hc = 2.0 × 10⁻²⁵ J m</code>.",
  opts: ["2.0 × 10⁻¹⁹ J", "4.0 × 10⁻¹⁹ J", "1.0 × 10⁻¹⁹ J", "4.0 × 10⁻²⁵ J", "6.0 × 10⁻¹⁹ J"],
  ans: 1,
  sol: `<p>Use <code>E = hc/λ</code> with the wavelength in metres:</p>
<div class="formula">E = 2.0 × 10⁻²⁵ / (500 × 10⁻⁹) = 2.0 × 10⁻²⁵ / (5.0 × 10⁻⁷)</div>
<p>Digits: <code>2.0/5.0 = 0.40</code>. Powers: <code>10⁻²⁵/10⁻⁷ = 10⁻¹⁸</code>. So</p>
<div class="formula">E = 4.0 × 10⁻¹⁹ J</div>
<p><b>Answer: B.</b></p>
<p><b>Convert to electron volts as a check.</b> <code>4.0 × 10⁻¹⁹ / 1.6 × 10⁻¹⁹ = 2.5 eV</code>. A 500 nm photon is green light, and green photons do carry about 2.5 eV. That matches the table in the curriculum and confirms the answer.</p>
<p><b>The traps.</b> Option A, <code>2.0 × 10⁻¹⁹</code>, is a factor of two too small. Option D is <code>hc</code> reported as an energy. All the options are within an order of magnitude, so this is a genuine calculation rather than an estimate — but the powers-of-ten discipline still makes it fast.</p>
<p><b>Why <code>hc = 2.0 × 10⁻²⁵ J m</code> is worth memorising.</b> It converts a two-step calculation into one step. Photon energy in joules is <code>hc/λ</code>, and for any visible wavelength you can do the division mentally. The exact value is <code>1.99 × 10⁻²⁵</code>, so rounding to 2.0 introduces less than 1% error — negligible at this level.</p>`,
  trap: "Forgetting to convert nanometres to metres, which changes the answer by a factor of 10⁹."
},
{
  id: "L-02", module: "L", topic: "Photoelectric effect", diff: 1,
  q: "Light of photon energy 4.0 eV falls on a metal of work function 2.5 eV. What is the maximum kinetic energy of the emitted electrons?",
  opts: ["2.5 eV", "6.5 eV", "4.0 eV", "1.5 eV", "0.6 eV"],
  ans: 3,
  sol: `<p>Use Einstein's photoelectric equation:</p>
<div class="formula">hf = φ + E_k(max)
E_k(max) = 4.0 − 2.5 = 1.5 eV</div>
<p><b>Answer: D.</b></p>
<p><b>Why subtraction and not addition.</b> The photon delivers 4.0 eV to one electron. The electron must spend 2.5 eV escaping the metal, and whatever remains becomes kinetic energy. So the two quantities subtract. Option B, 6.5 eV, is the sum, which would mean the electron gains energy by escaping — physically impossible.</p>
<p><b>The threshold check.</b> Emission occurs only if <code>hf &gt; φ</code>, that is, if the photon energy exceeds the work function. Here <code>4.0 &gt; 2.5</code> ✓, so emission happens. If the question had given a photon energy below 2.5 eV, the correct answer would be that no electrons are emitted at all — a trap worth watching for.</p>
<p><b>The traps.</b> Option C, 4.0 eV, is the photon energy before subtracting the work function. Option A, 2.5 eV, is the work function itself. Option E, 0.6 eV, is a division rather than a subtraction.</p>
<p><b>The related quantity.</b> The stopping potential needed to just prevent these electrons from reaching the anode would be 1.5 V, since <code>eV_s = E_k(max)</code> and the energy is in electron volts. That is the whole convenience of the unit: the stopping potential in volts is numerically equal to the maximum kinetic energy in electron volts.</p>`,
  trap: "Adding the work function instead of subtracting it, or missing that emission requires hf > φ."
},
{
  id: "L-03", module: "L", topic: "de Broglie", diff: 2,
  q: "An electron moves with speed <code>v</code>. If its speed is doubled, what happens to its de Broglie wavelength?",
  opts: ["It doubles", "It halves", "It is unchanged", "It falls to a quarter", "It quadruples"],
  ans: 1,
  sol: `<p>The de Broglie wavelength is</p>
<div class="formula">λ = h/mv</div>
<p>Since <code>h</code> and <code>m</code> are constant, <code>λ ∝ 1/v</code>. Doubling the speed halves the wavelength.</p>
<p><b>Answer: B.</b></p>
<p><b>The inverse relationship is the point.</b> Faster particles have shorter wavelengths. This is why electron microscopes use high accelerating voltages: shorter wavelengths mean better resolution, because the diffraction limit improves as the wavelength falls.</p>
<p><b>The traps.</b> Option A, doubling, is the error of assuming a direct proportionality. Option D, falling to a quarter, is what you would get if the wavelength depended on <code>v²</code> — which it does not, because <code>λ = h/p</code> and momentum is linear in speed at non-relativistic energies.</p>
<p><b>The momentum form is the more fundamental one.</b> <code>λ = h/p</code> holds even at relativistic speeds, where <code>p = mv</code> does not. For Round 0 the non-relativistic form is sufficient, but knowing that the fundamental relationship is with momentum rather than with speed is worth noting.</p>
<p><b>The magnitude check.</b> A typical electron accelerated through 100 V has a wavelength of about 0.12 nm, comparable to atomic spacing. That is why crystals work as diffraction gratings for electrons, and why the effect is unobservable for macroscopic objects — a cricket ball's wavelength is some twenty orders of magnitude smaller than a nucleus.</p>`,
  trap: "Assuming the wavelength is proportional to speed rather than inversely proportional."
},
{
  id: "L-04", module: "L", topic: "Electron volt", diff: 1,
  q: "An energy of <code>3.2 × 10⁻¹⁹ J</code> is equivalent to how many electron volts? Use <code>e = 1.6 × 10⁻¹⁹ C</code>.",
  opts: ["2.0 eV", "3.2 eV", "5.1 eV", "0.50 eV", "20 eV"],
  ans: 0,
  sol: `<p>Divide by the charge on an electron:</p>
<div class="formula">E = 3.2 × 10⁻¹⁹ / 1.6 × 10⁻¹⁹ = 2.0 eV</div>
<p><b>Answer: A.</b></p>
<p><b>Why the division works.</b> An electron volt is defined as the energy gained by an electron accelerated through one volt, which is <code>eV = 1.6 × 10⁻¹⁹ J</code>. So converting joules to electron volts means dividing by that number, and converting the other way means multiplying. The factor is the same in both directions.</p>
<p><b>Why the numbers were chosen to be clean.</b> <code>3.2/1.6 = 2.0</code> exactly, and the powers of ten cancel completely. That is characteristic of a paper written for mental arithmetic — when a question gives you an awkward-looking number like <code>3.2 × 10⁻¹⁹</code>, it is usually because the division comes out cleanly.</p>
<p><b>The traps.</b> Option B, 3.2 eV, is the number left unchanged, which is what you get from forgetting to divide. Option E, 20 eV, is a powers-of-ten slip. Option C, 5.1 eV, comes from dividing by the wrong constant.</p>
<p><b>The physical context.</b> 2.0 eV is a typical visible-photon energy — a red photon carries about 1.8 eV. So this question is effectively asking you to recognise that <code>3.2 × 10⁻¹⁹ J</code> is a plausible photon energy, which is a useful cross-check on the arithmetic.</p>`,
  trap: "Multiplying by e instead of dividing, or a powers-of-ten slip."
},
{
  id: "L-05", module: "L", topic: "Line spectra", diff: 2,
  q: "An electron in a hydrogen atom falls from an energy level of −1.5 eV to a level of −3.4 eV. What is the energy of the emitted photon?",
  opts: ["4.9 eV", "1.9 eV", "3.4 eV", "1.5 eV", "0.90 eV"],
  ans: 1,
  sol: `<p>The photon carries the energy difference between the levels:</p>
<div class="formula">E = E_initial − E_final = (−1.5) − (−3.4) = 1.9 eV</div>
<p><b>Answer: B.</b></p>
<p><b>The sign handling, which is where this goes wrong.</b> Energy levels are quoted as negative numbers, measured from the zero of an electron at rest infinitely far away. The electron is <i>losing</i> energy by falling to a lower level, and that lost energy is emitted as a photon. Subtracting the more negative number from the less negative one gives a positive result, which is what an emitted photon must have.</p>
<p><b>The traps.</b> Option A, 4.9 eV, is the <b>sum</b> of the two magnitudes, which would correspond to ionising the atom from the lower level rather than to a transition between them. Option C, 3.4 eV, is the ionisation energy from the lower level. Option D, 1.5 eV, is the magnitude of the upper level.</p>
<p><b>Why line spectra matter.</b> Because the levels are discrete, only certain photon energies are possible, so a gas discharge emits sharp bright lines rather than a continuous spectrum. That observation is the <b>evidence</b> for quantised energy levels, and a question phrased as "what does the existence of line spectra tell us" wants that sentence rather than a calculation.</p>
<p><b>Where this goes next.</b> In a real hydrogen spectrum the visible lines are the Balmer series, arising from transitions down to the <code>n = 2</code> level at −3.4 eV. The transition here, from −1.5 eV to −3.4 eV, is one of those — a red line at about 656 nm, which is why hydrogen discharge tubes glow pink.</p>`,
  trap: "Adding the magnitudes instead of subtracting, or getting the sign of the emitted photon wrong."
},

/* ===================== MODULE M — fluids ===================== */

{
  id: "M-01", module: "M", topic: "Pressure with depth", diff: 1,
  q: "What is the pressure due to the water alone at a depth of 5.0 m in a lake? Take <code>ρ = 1000 kg m⁻³</code> and <code>g = 10 m s⁻²</code>.",
  opts: ["5.0 × 10⁴ Pa", "5.0 × 10⁵ Pa", "500 Pa", "5.0 × 10³ Pa", "1.0 × 10⁵ Pa"],
  ans: 0,
  sol: `<p>Use <code>p = ρgh</code>:</p>
<div class="formula">p = 1000 × 10 × 5.0 = 5.0 × 10⁴ Pa</div>
<p><b>Answer: A.</b></p>
<p><b>Read the question carefully — it says "due to the water alone".</b> The <b>total</b> pressure at that depth would include the atmosphere pressing down on the surface, giving <code>5.0 × 10⁴ + 1.0 × 10⁵ = 1.5 × 10⁵ Pa</code>. A question that asks for the pressure due to the liquid wants only the <code>ρgh</code> term. Getting this distinction right is half the marks in this topic.</p>
<p><b>Why the depth is 5 m and not the total depth of the lake.</b> Pressure at depth depends only on how far below the surface you are, not on how deep the lake goes below you. So a point 5 m down in a shallow pond and a point 5 m down in the ocean experience the same water pressure.</p>
<p><b>The traps.</b> Option B, <code>5.0 × 10⁵ Pa</code>, is a factor of ten too large — a powers-of-ten slip. Option C, 500 Pa, and option D, <code>5.0 × 10³ Pa</code>, are factors of 100 and 10 too small.</p>
<p><b>The physical anchor.</b> Every 10 m of water adds roughly one atmosphere of pressure, since <code>1000 × 10 × 10 = 10⁵ Pa</code>. So 5 m of water is about half an atmosphere, which is the right order and confirms the answer.</p>`,
  trap: "Including atmospheric pressure when the question asks for the pressure due to the liquid alone."
},
{
  id: "M-02", module: "M", topic: "Floating fraction", diff: 1,
  q: "A block of density <code>750 kg m⁻³</code> floats in water of density <code>1000 kg m⁻³</code>. What percentage of its volume is above the water surface?",
  opts: ["20%", "75%", "50%", "33%", "25%"],
  ans: 4,
  sol: `<p>For a floating body, upthrust equals weight, which gives the submerged fraction directly:</p>
<div class="formula">V_submerged/V = ρ_block/ρ_water = 750/1000 = 0.75</div>
<p>So 75% is submerged, which means <b>25% is above the surface</b>.</p>
<p><b>Answer: E.</b></p>
<p><b>The trap, and it is the whole question.</b> Option B, 75%, is the submerged fraction — the number you calculate first. The question asks for the fraction <i>above</i> the water. This kind of inversion is one of the commonest ways to lose a mark on a question you actually understood, and it is worth pausing on the wording every time.</p>
<p><b>The sanity check.</b> The block is less dense than water, so it should float with more than half submerged but not by much — 75/25 is right for a density ratio of 0.75. If your answer had the block floating with only a sliver submerged, the density ratio would have to be much smaller.</p>
<p><b>The general result.</b> The submerged fraction equals the ratio of the object's density to the fluid's density. So an ice cube (917 kg m⁻³) floats in water with about 92% submerged — which is why icebergs show only a small fraction above the surface, and why that hidden fraction is dangerous to shipping.</p>`,
  trap: "Reporting the submerged fraction when the question asks for the fraction above the surface."
},
{
  id: "M-03", module: "M", topic: "Density by weighing", diff: 2,
  q: "An object weighs 8.0 N in air and 6.0 N when fully immersed in water. What is its density? Take <code>ρ_water = 1000 kg m⁻³</code>.",
  opts: ["2000 kg m⁻³", "1333 kg m⁻³", "4000 kg m⁻³", "8000 kg m⁻³", "1000 kg m⁻³"],
  ans: 2,
  sol: `<p>The upthrust is the difference between the two weighings:</p>
<div class="formula">upthrust = 8.0 − 6.0 = 2.0 N</div>
<p>Divide the true weight by the upthrust and the unknown volume and <code>g</code> both cancel:</p>
<div class="formula">ρ_object/ρ_water = W/(W − W') = 8.0/(8.0 − 6.0) = 8.0/2.0 = 4.0</div>
<div class="formula">ρ_object = 4.0 × 1000 = 4000 kg m⁻³</div>
<p><b>Answer: C.</b></p>
<p><b>Why this is a ratio question.</b> You never needed the volume and you never needed <code>g</code>. The two weighings give the density ratio directly. If you started by computing <code>V</code> from <code>2.0 = 1000 × V × 9.81</code>, you took the long route and probably ran out of time.</p>
<p><b>The physical check.</b> A density of 4000 kg m⁻³ is between aluminium (2700) and steel (7800), which is plausible for a dense mineral or a ceramic. If your answer had come out at 500 kg m⁻³ it would be less dense than water, and the object could not have sunk — so the answer must exceed 1000.</p>
<p><b>The traps.</b> Option A, 2000 kg m⁻³, is <code>W/(W − W')</code> with a slip, or the answer you get from using <code>W'</code> in the numerator. Option B, 1333 kg m⁻³, comes from inverting the ratio. Option D, 8000 kg m⁻³, is <code>8.0/1.0</code>, using the wrong difference.</p>`,
  trap: "Computing the volume when the two weighings already give the density ratio directly."
},
{
  id: "M-04", module: "M", topic: "Archimedes' principle", diff: 1,
  q: "A body of volume <code>2.0 × 10⁻³ m³</code> is fully submerged in water. What is the upthrust on it? Take <code>ρ = 1000 kg m⁻³</code> and <code>g = 10 m s⁻²</code>.",
  opts: ["10 N", "2.0 N", "200 N", "20 N", "0.20 N"],
  ans: 3,
  sol: `<p>The upthrust equals the weight of fluid displaced, and since the body is fully submerged the displaced volume is its own volume:</p>
<div class="formula">upthrust = ρ_fluid V g = 1000 × 2.0 × 10⁻³ × 10 = 20 N</div>
<p><b>Answer: D.</b></p>
<p><b>The critical point: it is the fluid's density, not the object's.</b> This is the single most common error in the module. A steel block and a wooden block of the same volume, both fully submerged, experience <b>exactly the same upthrust</b> — even though the steel is far heavier. Only the volume matters, because only the volume determines how much fluid is pushed out of the way.</p>
<p><b>Why the upthrust does not depend on depth.</b> For an incompressible fluid, the pressure difference between the top and bottom of the object is the same at any depth, because both pressures increase by the same amount as you go deeper. So the upthrust is the same however deep the object sits. This is counter-intuitive and worth being able to state.</p>
<p><b>The traps.</b> Option B, 2.0 N, and option E, 0.20 N, are powers-of-ten slips. Option A, 10 N, is <code>ρV</code> without the <code>g</code> — a mass reported as a force.</p>
<p><b>The floating comparison.</b> If this body had a weight of 20 N, it would be neutrally buoyant — hovering fully submerged. If its weight were less than 20 N, it would float with part of its volume above the surface. So the upthrust sets the threshold for floating, and comparing it with the weight answers every floating question.</p>`,
  trap: "Using the object's density instead of the fluid's. Upthrust depends on displaced volume only."
},

/* ===================== MODULE N — insurance ===================== */

{
  id: "N-01", module: "N", topic: "SHM period", diff: 2,
  q: "<b>Insurance question.</b> A mass of 0.50 kg hangs on a spring of stiffness <code>200 N m⁻¹</code>. What is the period of oscillation? Take <code>π ≈ 3.1</code>.",
  opts: ["0.31 s", "0.050 s", "3.1 s", "0.63 s", "0.16 s"],
  ans: 0,
  sol: `<p>Use the mass–spring period:</p>
<div class="formula">T = 2π√(m/k) = 2 × 3.1 × √(0.50/200) = 6.2 × √0.0025</div>
<p>And <code>√0.0025 = 0.050</code>, so</p>
<div class="formula">T = 6.2 × 0.050 = 0.31 s</div>
<p><b>Answer: A.</b></p>
<p><b>Why this question is flagged as insurance.</b> Simple harmonic motion has no Round 0 evidence — it is not in the scope statement and AQA places it in Year 13. But the 2022 Round 1 Section 1 paper contained two SHM questions, so it is a Round 1 favourite. This is exactly the situation the insurance module exists for.</p>
<p><b>The connection to module A.</b> Dimensional analysis alone gives <code>T = k√(m/k)</code> — you derived that in the toolkit module. The only thing the method could not supply was the constant <code>2π</code>, which has to come from the physics. That is a good illustration of both the power and the limitation of dimensional reasoning.</p>
<p><b>The traps.</b> Option B, 0.050 s, is <code>√(m/k)</code> alone, without the <code>2π</code>. Option C, 3.1 s, is <code>π</code> — a distraction from the given value. Option E, 0.16 s, is roughly half the correct answer.</p>
<p><b>The key property to remember.</b> The period does <b>not</b> depend on the amplitude. Doubling the amplitude doubles the maximum speed but leaves the period unchanged. That fact is the standard conceptual question on this topic.</p>`,
  trap: "Forgetting the 2π, or thinking the period depends on the amplitude."
},
{
  id: "N-02", module: "N", topic: "Pendulum", diff: 2,
  q: "<b>Insurance question.</b> A simple pendulum has a length of 2.5 m. What is its period? Take <code>g = 10 m s⁻²</code> and <code>π ≈ 3.1</code>.",
  opts: ["0.50 s", "1.6 s", "6.3 s", "3.1 s", "2.0 s"],
  ans: 3,
  sol: `<p>For small oscillations, use</p>
<div class="formula">T = 2π√(ℓ/g) = 2 × 3.1 × √(2.5/10) = 6.2 × √0.25 = 6.2 × 0.5 = 3.1 s</div>
<p><b>Answer: D.</b></p>
<p><b>The numbers were chosen to be clean.</b> <code>2.5/10 = 0.25</code> and <code>√0.25 = 0.5</code> exactly, so the only multiplication needed is <code>2π × 0.5 = π</code>. That is why the answer is numerically equal to the value of <code>π</code> — a coincidence of the chosen length, not a general rule.</p>
<p><b>The small-angle condition, which is the physics behind the formula.</b> The period formula assumes the restoring force is proportional to the displacement, which requires <code>sin θ ≈ θ</code>. That is the small-angle approximation from module A. At large amplitudes the motion is not simple harmonic and the period becomes longer. A question that gives a large amplitude is testing whether you notice this.</p>
<p><b>The mass does not appear.</b> The period of a pendulum is independent of the mass of the bob. That follows from the derivation — gravity accelerates all masses equally — and it is worth stating, because a question may include a mass as a distractor.</p>
<p><b>The traps.</b> Option C, 6.3 s, is <code>2π</code> with the square root omitted. Option A, 0.50 s, is <code>√(ℓ/g)</code> alone. Option B, 1.6 s, is <code>π/2</code>.</p>`,
  trap: "Thinking the period depends on the mass of the bob, or forgetting the 2π."
},
{
  id: "N-03", module: "N", topic: "SHM acceleration", diff: 2,
  q: "<b>Insurance question.</b> A simple harmonic oscillator has amplitude <code>A</code> and angular frequency <code>ω</code>. What is its maximum acceleration?",
  opts: ["ω²A", "ωA", "ωA²", "ω²A²", "A/ω²"],
  ans: 0,
  sol: `<p>The displacement is <code>x = A cos ωt</code>. Differentiating twice gives the acceleration:</p>
<div class="formula">v = −Aω sin ωt
a = −Aω² cos ωt</div>
<p>The maximum magnitude occurs when <code>cos ωt = ±1</code>, giving</p>
<div class="formula">a_max = ω²A</div>
<p><b>Answer: A.</b></p>
<p><b>The comparison with the maximum speed, which is the point of the question.</b> The maximum speed is <code>ωA</code> and the maximum acceleration is <code>ω²A</code>. So the acceleration carries an extra factor of <code>ω</code> and has units of <code>m s⁻²</code> rather than <code>m s⁻¹</code>. Option B, <code>ωA</code>, is the maximum <i>speed</i> — the distractor that catches anyone who has not checked the units.</p>
<p><b>The dimensional check, which settles it instantly.</b> Acceleration must have units of <code>m s⁻²</code>. Since <code>ω</code> has units <code>s⁻¹</code> and <code>A</code> has units <code>m</code>, only <code>ω²A</code> gives <code>s⁻² × m</code> ✓. Option C, <code>ωA²</code>, would be <code>m² s⁻¹</code> — wrong. Option D would be <code>m² s⁻²</code> — wrong.</p>
<p><b>The defining equation, worth connecting.</b> Since <code>a = −ω²x</code>, the maximum acceleration is <code>ω²A</code> at the extremes of the motion, where the displacement is greatest. At the centre, where <code>x = 0</code>, the acceleration is zero and the speed is maximum. That alternation between the two extremes is the signature of simple harmonic motion.</p>`,
  trap: "Confusing maximum speed ωA with maximum acceleration ω²A. Check the units."
}

]);
