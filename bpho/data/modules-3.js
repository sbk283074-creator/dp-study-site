/* BPhO Round 0 — curriculum, part 3 of 6.
   Module H: electricity and circuits. The highest-frequency topic in the paper. */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "H",
  title: "Electricity and circuits",
  short: "Circuits",
  priority: 1,
  tier: "Tier A — inside AQA AS §3.5, and three sample-paper questions",
  why: "Circuits are the highest-frequency topic in the paper: in the Round 1 Section 1 papers, which are the closest available proxy, circuits account for 15 of 80 questions — nearly one in five. The official sample paper devotes three of its twelve questions to circuits. If you give any single module extra time, give it to this one.",
  warn: "<p><b>The sample-paper circuit questions were not textbook exercises.</b> They were a cell reconfigured from series to parallel, two opposing EMFs in one loop, and a cell with internal resistance. Standard A-level practice rarely covers the first two. Learn those three shapes specifically — they are in the worked examples below.</p>",

  sections: [
    {
      h: "The three definitions, from the ground up",
      body: `<p>Every circuit question is built on three definitions. Know what each one <i>means</i>, not just how to compute it, because competition questions ask about meaning.</p>
<table><thead><tr><th>Quantity</th><th>Definition</th><th>What it really says</th></tr></thead><tbody>
<tr><td>Current <code>I = ΔQ/Δt</code></td><td>rate of flow of charge</td><td>How much charge passes a point each second. Measured in amperes, where <code>1 A = 1 C s⁻¹</code>.</td></tr>
<tr><td>Potential difference <code>V = W/Q</code></td><td>energy transferred per unit charge</td><td>How much energy each coulomb gives up between two points. Measured in volts, where <code>1 V = 1 J C⁻¹</code>.</td></tr>
<tr><td>Resistance <code>R = V/I</code></td><td>the ratio of p.d. to current</td><td>How much p.d. is needed per ampere. Measured in ohms.</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The sentence to remember about potential difference.</b> A volt is a joule per coulomb. So a 12 V battery gives 12 joules of energy to every coulomb that passes through it. That single reframing answers a whole family of conceptual questions about what p.d. means.</p></div>
<h3>Ohm's law is not a definition</h3>
<p>Resistance is <i>defined</i> as <code>V/I</code> for any component. Ohm's law is the separate, empirical statement that for a metallic conductor at constant temperature, <code>V</code> is proportional to <code>I</code> — that is, <code>R</code> is constant. Many components do not obey it.</p>
<div class="callout callout--warn"><p><b>This distinction is tested.</b> A question asking "does this component obey Ohm's law" is asking whether its <code>I</code>–<code>V</code> graph is a straight line through the origin. A filament lamp does not, because its resistance changes as it heats. A diode does not, because it conducts in only one direction.</p></div>`
    },

    {
      h: "I–V characteristics of the three standard components",
      body: `<p>You should be able to sketch all three from memory and explain the shape of each in one sentence.</p>
<h3>Ohmic conductor — a straight line through the origin</h3>
<p>Current is proportional to potential difference, so the graph is a straight line. Gradient is <code>1/R</code>. The metal stays at constant temperature because the current is small.</p>
<h3>Filament lamp — a curve that flattens</h3>
<p>At first the graph is nearly straight. As the current rises the filament heats up, the lattice ions vibrate more, and electrons collide with them more often. Resistance rises, so the graph <b>bends over</b> and becomes less steep. It is not a straight line at any appreciable current.</p>
<h3>Semiconductor diode — one-sided</h3>
<p>In forward bias, almost nothing happens until about 0.6 V (for silicon), then the current rises very sharply. In reverse bias, only a tiny leakage current flows. So the graph is flat, flat, flat, then a sudden vertical rise on the forward side.</p>
<table><thead><tr><th>Component</th><th>Shape</th><th>Reason</th></tr></thead><tbody>
<tr><td>Ohmic resistor</td><td>straight line, through origin</td><td>constant resistance</td></tr>
<tr><td>Filament lamp</td><td>curve bending towards the current axis</td><td>resistance rises as the filament heats</td></tr>
<tr><td>Diode</td><td>flat in reverse, sharp rise in forward</td><td>conducts in one direction only</td></tr>
<tr><td>Thermistor (NTC)</td><td>resistance falls with temperature</td><td>more charge carriers released as it warms</td></tr>
</tbody></table>
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="Graph of current against potential difference for three components: a straight line for an ohmic resistor, a curve that flattens for a filament lamp, and a flat-then-sharp curve for a diode.">
<text x="240" y="24" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">I–V characteristics of the three standard components</text>
<line x1="110" y1="46" x2="110" y2="238" stroke="#1f2937" stroke-width="2"/>
<line x1="46" y1="230" x2="454" y2="230" stroke="#1f2937" stroke-width="2"/>
<polygon points="454,230 444,225 444,235" fill="#1f2937"/>
<polygon points="110,46 105,56 115,56" fill="#1f2937"/>
<path d="M110,230 L286,72" fill="none" stroke="#2f5fd0" stroke-width="2.5"/>
<path d="M110,230 Q205,108 340,88" fill="none" stroke="#a8641a" stroke-width="2.5"/>
<path d="M54,232 L150,230 Q176,228 186,140 L192,70" fill="none" stroke="#1f7a53" stroke-width="2.5"/>
<text x="296" y="70" font-size="12" font-weight="600" fill="#2f5fd0">ohmic resistor</text>
<text x="348" y="98" font-size="12" font-weight="600" fill="#a8641a">filament lamp</text>
<text x="200" y="60" font-size="12" font-weight="600" fill="#1f7a53">diode</text>
<text x="446" y="250" text-anchor="end" font-size="12.5" fill="#4a5262">V</text>
<text x="100" y="42" text-anchor="end" font-size="12.5" fill="#4a5262">I</text>
<text x="102" y="246" text-anchor="end" font-size="12" fill="#7b8494">O</text>
<text x="196" y="152" font-size="11.5" fill="#7b8494">≈0.6 V</text>
<text x="36" y="264" font-size="11.5" fill="#7b8494">reverse bias</text>
<text x="238" y="142" font-size="11.5" fill="#7b8494">flattens → R rises</text>
</svg>
<figcaption><b>Read the shape, not the numbers.</b> A straight line through the origin means constant resistance. A curve that <i>flattens</i> as <code>V</code> rises means resistance is <b>increasing</b> — the filament is heating. A curve that is flat then shoots up at a threshold means one-way conduction — a diode. The direction of the bend is the whole answer.</figcaption>
</figure>
<div class="callout callout--good"><p><b>The direction of the bend is the giveaway.</b> If a graph of <code>I</code> against <code>V</code> flattens as <code>V</code> rises, the resistance is increasing — a lamp. If it steepens sharply at a threshold, it is a diode. There is no third option on this paper.</p></div>`
    },

    {
      h: "Resistivity, temperature, thermistors and superconductivity",
      body: `<p>Resistance depends on the geometry of the component and on the material. Those two dependencies separate cleanly:</p>
<div class="formula">R = ρL/A</div>
<p>where <code>ρ</code> is the <b>resistivity</b> — a property of the material alone — <code>L</code> is the length and <code>A</code> the cross-sectional area. Rearranged, <code>ρ = RA/L</code>, with units <code>Ω m</code>.</p>
<h3>Why a long thin wire has high resistance</h3>
<p>Doubling the length doubles the resistance, because the charge has twice as far to travel through the lattice. Doubling the cross-sectional area halves the resistance, because there are twice as many available paths. Both facts fall straight out of the formula, which is why it is worth remembering as a piece of physics rather than as a formula.</p>
<h3>Temperature dependence</h3>
<ul class="tight">
<li><b>Metals:</b> resistance <b>rises</b> with temperature. The ions vibrate more vigorously and collide with the drifting electrons more often. This is why a filament lamp's resistance when hot is much higher than when cold — typically ten times higher.</li>
<li><b>NTC thermistors:</b> resistance <b>falls</b> as temperature rises. Heating the semiconductor releases more charge carriers, and that effect outweighs the increased scattering. The temperature coefficient is negative, hence NTC — negative temperature coefficient.</li>
<li><b>LDRs:</b> resistance falls as light intensity rises, for the same reason: photons liberate additional charge carriers.</li>
</ul>
<h3>Superconductivity</h3>
<p>Below a critical temperature, certain materials have <b>exactly zero</b> resistance. Not small — zero. A current, once started in a superconducting loop, persists indefinitely without any source.</p>
<p>The critical temperature is different for every material. For the classic superconductors such as niobium alloys it is only a few kelvin, so liquid helium is needed; the discovery of materials with critical temperatures above 77 K (the boiling point of nitrogen) made superconducting technology much cheaper to operate.</p>
<p>Applications follow directly from zero resistance: powerful electromagnets with no resistive heating and therefore no need for continuous cooling, and loss-free power transmission over long distances. <b>This is inside AQA AS §3.5.1.3</b>, which means it counts as Year 12 material and is fair game for Round 0.</p>
<div class="callout callout--key"><p><b>The exam point about superconductivity is usually qualitative.</b> A question is more likely to ask why a superconducting magnet is advantageous than to ask for a numerical calculation. The answer is that there is no resistive heating, so no energy is wasted and much stronger fields are possible.</p></div>`
    },

    {
      h: "Series and parallel",
      body: `<p>Two rules sets, and they are worth deriving rather than memorising, because derivations are what the harder questions require.</p>
<h3>Series — one path</h3>
<p>The same current passes through every component, because there is only one route. The potential differences add up to the supply voltage.</p>
<div class="formula">I is the same everywhere
V_total = V₁ + V₂ + …
R_total = R₁ + R₂ + …</div>
<h3>Parallel — several paths</h3>
<p>Every component has the same potential difference across it, because they share the same two nodes. The currents add, since charge must be conserved at a junction.</p>
<div class="formula">V is the same across each branch
I_total = I₁ + I₂ + …
1/R_total = 1/R₁ + 1/R₂ + …</div>
<p>For exactly two resistors in parallel, the product-over-sum form is faster:</p>
<div class="formula">R_parallel = R₁R₂ / (R₁ + R₂)</div>
<figure class="fig">
<svg viewBox="0 0 480 268" role="img" aria-label="Two circuits side by side: in series a single loop with two resistors, in parallel two branches across the same cell.">
<text x="128" y="28" text-anchor="middle" font-size="13" font-weight="600" fill="#14181f">Series — one path</text>
<text x="360" y="28" text-anchor="middle" font-size="13" font-weight="600" fill="#14181f">Parallel — several paths</text>
<line x1="240" y1="40" x2="240" y2="248" stroke="#e2e6ed" stroke-width="1.5" stroke-dasharray="5 5"/>
<polyline points="56,134 56,70 200,70 200,190 56,190 56,146" fill="none" stroke="#1f2937" stroke-width="2"/>
<line x1="42" y1="146" x2="70" y2="146" stroke="#1f2937" stroke-width="2"/>
<line x1="49" y1="134" x2="63" y2="134" stroke="#1f2937" stroke-width="4.5"/>
<rect x="96" y="62" width="28" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<rect x="144" y="62" width="28" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="110" y="100" text-anchor="middle" font-size="12" fill="#4a5262">R₁</text>
<text x="158" y="100" text-anchor="middle" font-size="12" fill="#4a5262">R₂</text>
<polygon points="76,64 88,70 76,76" fill="#2f5fd0"/>
<text x="82" y="58" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">I</text>
<text x="128" y="218" text-anchor="middle" font-size="11.5" fill="#4a5262">same I through both</text>
<text x="128" y="236" text-anchor="middle" font-size="11.5" fill="#4a5262">R = R₁ + R₂</text>
<polyline points="270,134 270,70 450,70 450,190 270,190 270,146" fill="none" stroke="#1f2937" stroke-width="2"/>
<line x1="256" y1="146" x2="284" y2="146" stroke="#1f2937" stroke-width="2"/>
<line x1="263" y1="134" x2="277" y2="134" stroke="#1f2937" stroke-width="4.5"/>
<line x1="330" y1="70" x2="330" y2="110" stroke="#1f2937" stroke-width="2"/>
<line x1="330" y1="138" x2="330" y2="190" stroke="#1f2937" stroke-width="2"/>
<rect x="322" y="110" width="16" height="28" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="400" y1="70" x2="400" y2="110" stroke="#1f2937" stroke-width="2"/>
<line x1="400" y1="138" x2="400" y2="190" stroke="#1f2937" stroke-width="2"/>
<rect x="392" y="110" width="16" height="28" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="348" y="130" font-size="12" fill="#4a5262">R₁</text>
<text x="418" y="130" font-size="12" fill="#4a5262">R₂</text>
<polygon points="324,86 330,96 336,86" fill="#2f5fd0"/>
<polygon points="394,86 400,96 406,86" fill="#2f5fd0"/>
<text x="318" y="80" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">I₁</text>
<text x="412" y="80" font-size="12" font-weight="600" fill="#2f5fd0">I₂</text>
<text x="360" y="218" text-anchor="middle" font-size="11.5" fill="#4a5262">same V across each branch</text>
<text x="360" y="236" text-anchor="middle" font-size="11.5" fill="#4a5262">1/R = 1/R₁ + 1/R₂</text>
</svg>
<figcaption><b>What is shared decides everything.</b> In <b>series</b> the current is common, so the potential differences add. In <b>parallel</b> the potential difference is common, so the currents add. Every "which resistor dissipates more power?" question is answered by asking which quantity is shared — and the same logic gives the two instant sanity checks: series total is <i>larger</i> than the largest resistor, parallel total is <i>smaller</i> than the smallest.</figcaption>
</figure>
<div class="callout callout--key"><p><b>Two facts that eliminate options instantly.</b> The total resistance of a series combination is always <b>larger</b> than the largest individual resistance. The total resistance of a parallel combination is always <b>smaller</b> than the smallest individual resistance. If an option violates either, it is wrong — no calculation needed.</p></div>
<h3>Cells in series and in parallel</h3>
<table><thead><tr><th>Arrangement</th><th>EMF</th><th>Internal resistance</th></tr></thead><tbody>
<tr><td><code>n</code> identical cells in series</td><td><code>nε</code></td><td><code>nr</code></td></tr>
<tr><td><code>n</code> identical cells in parallel</td><td><code>ε</code></td><td><code>r/n</code></td></tr>
</tbody></table>
<p>Series gives more voltage; parallel gives more current capability because the internal resistance is divided. That trade-off is the whole content of the reconfiguration question below.</p>`
    },

    {
      h: "Energy and power",
      body: `<p>Four forms of the same relationship. Knowing which to reach for is the skill.</p>
<div class="formula">E = IVt          P = IV = I²R = V²/R</div>
<table><thead><tr><th>Use this form</th><th>When</th></tr></thead><tbody>
<tr><td><code>P = I²R</code></td><td>Current is the same through the components — <b>series</b> circuits. Here power is proportional to resistance, so the largest resistor dissipates the most.</td></tr>
<tr><td><code>P = V²/R</code></td><td>Voltage is the same across the components — <b>parallel</b> circuits. Here power is inversely proportional to resistance, so the <i>smallest</i> resistor dissipates the most.</td></tr>
<tr><td><code>P = IV</code></td><td>You know the supply voltage and the total current.</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The result worth memorising, because it feels wrong.</b> In a series circuit the largest resistance dissipates the most power. In a parallel circuit the largest resistance dissipates the <b>least</b>. Students who have not thought this through get it backwards about half the time, and it appears on every competition paper.</p></div>
<h3>Average power for alternating supplies</h3>
<p>For a sinusoidal supply of peak voltage <code>V₀</code>, the voltage squared is positive on both half-cycles, and its average over a full cycle is <code>V₀²/2</code>. So</p>
<div class="formula">average power = V₀²/(2R) = ½ × (peak power)</div>
<p>For a square wave alternating between <code>+V₀</code> and <code>−V₀</code>, the voltage squared is <code>V₀²</code> at every instant, so the average power equals the peak power — no factor of ½ at all.</p>
<p>If a diode half-wave rectifies a sinusoidal supply, current flows during only half the cycle, so the average power falls to <code>V₀²/(4R)</code>.</p>
<div class="callout callout--warn"><p><b>Do not use the average voltage.</b> The average of a sinusoid over a full cycle is zero, which would give zero power — obviously wrong. You must average the <i>square</i> of the voltage, which is never negative. This is precisely why the quantity is the mean square and not the mean.</p></div>`
    },

    {
      h: "Kirchhoff's laws",
      body: `<p>Two conservation statements, and every circuit question is an application of one or both.</p>
<h3>First law — conservation of charge</h3>
<p>At any junction, the sum of currents entering equals the sum leaving. Charge does not pile up at a node.</p>
<div class="formula">Σ I_in = Σ I_out</div>
<h3>Second law — conservation of energy</h3>
<p>Around any closed loop, the sum of EMFs equals the sum of potential drops. Going round a loop and returning to the start must leave you at the same potential.</p>
<div class="formula">Σ ε = Σ IR</div>
<h3>The sign convention that avoids most mistakes</h3>
<ol class="steps">
<li><b>Choose a direction</b> for each loop, clockwise or anticlockwise. It does not matter which.</li>
<li><b>Going through a source from − to + counts as +ε.</b> From + to − counts as −ε.</li>
<li><b>Going through a resistor in the direction of the current counts as −IR.</b> Against the current counts as +IR.</li>
<li><b>If the current you solve for comes out negative</b>, the real current flows the other way. That is not an error — it is the method telling you the direction.</li>
</ol>
<div class="callout callout--good"><p><b>The reason the sign convention matters.</b> Most circuit errors on competition papers are sign errors, not physics errors. Writing the loop direction down explicitly and following the three rules above removes almost all of them.</p></div>`
    },

    {
      h: "EMF and internal resistance",
      body: `<p>Real sources have resistance inside them. Charge passing through the source loses some energy there before it ever reaches the external circuit. That gives the defining relationship:</p>
<div class="formula">ε = I(R + r)   →   ε = IR + Ir</div>
<p>where <code>ε</code> is the EMF, <code>R</code> the external resistance and <code>r</code> the internal resistance. The quantity <code>IR</code> is the <b>terminal potential difference</b> — what a voltmeter across the battery actually reads.</p>
<div class="formula">V_terminal = ε − Ir</div>
<p>So the terminal p.d. <b>falls</b> as the current rises. This is why headlights dim momentarily when a car's starter motor draws a large current.</p>
<h3>The graph</h3>
<p>Plot terminal p.d. against current. From <code>V = ε − Ir</code>, this is a straight line with:</p>
<ul class="tight">
<li><b>vertical intercept</b> = <code>ε</code>, the EMF (measured at zero current, when there is no <code>Ir</code> loss)</li>
<li><b>gradient</b> = <code>−r</code>, the negative of the internal resistance</li>
</ul>
<figure class="fig">
<svg viewBox="0 0 480 240" role="img" aria-label="Left: a cell with internal resistance r driving an external resistor R, with a voltmeter across R. Right: terminal potential difference against current, a straight line with intercept epsilon and gradient minus r.">
<text x="240" y="24" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">Internal resistance: the circuit, and the V–I line</text>
<line x1="56" y1="116" x2="56" y2="80" stroke="#1f2937" stroke-width="2"/>
<line x1="56" y1="80" x2="196" y2="80" stroke="#1f2937" stroke-width="2"/>
<line x1="196" y1="80" x2="196" y2="190" stroke="#1f2937" stroke-width="2"/>
<line x1="196" y1="190" x2="56" y2="190" stroke="#1f2937" stroke-width="2"/>
<line x1="56" y1="190" x2="56" y2="166" stroke="#1f2937" stroke-width="2"/>
<line x1="42" y1="128" x2="70" y2="128" stroke="#1f2937" stroke-width="2"/>
<line x1="48" y1="116" x2="62" y2="116" stroke="#1f2937" stroke-width="4.5"/>
<line x1="56" y1="128" x2="56" y2="140" stroke="#1f2937" stroke-width="2"/>
<rect x="48" y="140" width="16" height="26" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="74" y="158" font-size="12" font-weight="600" fill="#b3352f">r</text>
<rect x="34" y="104" width="46" height="76" fill="none" stroke="#cbd2dd" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="57" y="100" text-anchor="middle" font-size="11.5" fill="#7b8494">cell</text>
<rect x="112" y="72" width="32" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="128" y="64" text-anchor="middle" font-size="12" fill="#4a5262">R</text>
<line x1="112" y1="80" x2="112" y2="142" stroke="#1f2937" stroke-width="2"/>
<line x1="144" y1="80" x2="144" y2="142" stroke="#1f2937" stroke-width="2"/>
<circle cx="128" cy="142" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="128" y="147" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">V</text>
<polygon points="84,74 96,80 84,86" fill="#2f5fd0"/>
<text x="90" y="68" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">I</text>
<line x1="300" y1="86" x2="300" y2="196" stroke="#1f2937" stroke-width="2"/>
<line x1="300" y1="190" x2="456" y2="190" stroke="#1f2937" stroke-width="2"/>
<polygon points="456,190 446,185 446,195" fill="#1f2937"/>
<polygon points="300,86 295,96 305,96" fill="#1f2937"/>
<line x1="300" y1="96" x2="430" y2="190" stroke="#2f5fd0" stroke-width="2.5"/>
<line x1="300" y1="96" x2="290" y2="96" stroke="#cbd2dd" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="290" y="100" text-anchor="end" font-size="12" font-weight="600" fill="#2f5fd0">ε</text>
<text x="430" y="208" text-anchor="middle" font-size="11.5" fill="#4a5262">ε/r</text>
<text x="454" y="208" text-anchor="end" font-size="12.5" fill="#4a5262">I</text>
<text x="292" y="82" text-anchor="end" font-size="12.5" fill="#4a5262">V</text>
<text x="378" y="130" font-size="11.5" fill="#4a5262">gradient = −r</text>
<text x="150" y="228" text-anchor="middle" font-size="11.5" fill="#4a5262">V_terminal = ε − Ir</text>
</svg>
<figcaption><b>The cell is an EMF in series with its own resistance.</b> Only the terminal p.d. is available to the external circuit, and it <i>falls</i> as the current rises — which is why headlights dim when the starter motor draws a big current. Plot <code>V</code> against <code>I</code> and you get a straight line: the intercept is <code>ε</code> (read at zero current, where there is no <code>Ir</code> loss) and the gradient is <code>−r</code>.</figcaption>
</figure>
<div class="callout callout--key"><p><b>The maximum power transfer result.</b> For a fixed EMF and internal resistance driving an external resistor <code>R</code>, the current is <code>ε/(R + r)</code>, so the power in <code>R</code> is</p>
<div class="formula">P = ε²R/(R + r)²</div>
<p>This is maximised when <code>R = r</code>, giving <code>P_max = ε²/(4r)</code>. It is a standard competition result, and the algebra is a good exercise in ratio reasoning.</p></div>
<figure class="fig">
<svg viewBox="0 0 460 300" role="img" aria-label="A graph of the power delivered to the load against the ratio of load resistance to internal resistance. The curve rises steeply, peaks at a ratio of one, and then falls away slowly.">
<text x="230" y="22" text-anchor="middle" font-size="13.5" font-weight="600" fill="#14181f">Power delivered to R against R/r</text>

<line x1="70" y1="72" x2="70" y2="252" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="64" y1="250" x2="448" y2="250" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="64" y1="80" x2="448" y2="80" stroke="#e2e6ed" stroke-width="1.2" stroke-dasharray="5 4"/>
<line x1="107" y1="80" x2="107" y2="250" stroke="#e2e6ed" stroke-width="1.2" stroke-dasharray="5 4"/>

<polyline points="70,250 73.7,193.7 75.6,172.9 77.4,155.6 79.3,141.2 88.5,98.9 97.8,83.4 107,80 125.5,86.8 144,98.9 181,122.5 218,141.2 292,166.7 366,182.8 440,193.7" fill="none" stroke="#2f5fd0" stroke-width="2.6"/>

<circle cx="107" cy="80" r="4.2" fill="#1f7a53"/>
<text x="114" y="72" font-size="12" font-weight="600" fill="#1f7a53">R = r</text>

<text x="66" y="62" text-anchor="end" font-size="11.5" fill="#4a5262">P / P_max</text>
<text x="62" y="84" text-anchor="end" font-size="11" fill="#7b8494">1</text>
<text x="62" y="254" text-anchor="end" font-size="11" fill="#7b8494">0</text>
<text x="70" y="268" text-anchor="middle" font-size="11" fill="#7b8494">0</text>
<text x="107" y="268" text-anchor="middle" font-size="11" fill="#7b8494">1</text>
<text x="144" y="268" text-anchor="middle" font-size="11" fill="#7b8494">2</text>
<text x="255" y="268" text-anchor="middle" font-size="11" fill="#7b8494">5</text>
<text x="440" y="268" text-anchor="middle" font-size="11" fill="#7b8494">10</text>
<text x="255" y="290" text-anchor="middle" font-size="11.5" font-style="italic" fill="#7b8494">R / r</text>
</svg>
<figcaption><b>The curve is the whole story in one picture.</b> The axes are both ratios, so this single curve covers every cell and every load. It rises almost vertically at first — a very small external resistance already draws a useful current — then peaks sharply at <code>R = r</code> and falls away slowly and asymmetrically. The fall is slow because a large <code>R</code> merely chokes the current, whereas a small <code>R</code> burns the energy inside the cell. Read the efficiency off the same point: at the peak the internal resistance dissipates exactly as much as the load, so only <b>50%</b> of the power reaches <code>R</code>.</figcaption>
</figure>
<h3>The short-circuit limit</h3>
<p>If <code>R = 0</code>, the current is <code>ε/r</code> and the terminal p.d. is zero — all the energy is being dissipated inside the source. That is a short circuit, and it is why the result matters practically.</p>`
    },

    {
      h: "Two opposing EMFs in one loop",
      body: `<p>This was one of the sample-paper questions, and it is not a standard A-level exercise. The structure is simple once you have seen it: two sources in the same loop pushing in opposite directions, so the net EMF is their <b>difference</b>, and the current is that net EMF divided by the total resistance in the loop.</p>
<div class="formula">I = (ε₁ − ε₂) / R_total</div>
<h3>The method</h3>
<ol class="steps">
<li><b>Identify which source is larger.</b> The current flows in the direction that the larger EMF drives.</li>
<li><b>Subtract</b> the smaller EMF from the larger to get the net driving EMF.</li>
<li><b>Add up all resistances</b> in the loop, including any internal resistances.</li>
<li><b>Divide.</b> Then use the current to find potential differences or powers in individual components.</li>
</ol>
<figure class="fig">
<svg viewBox="0 0 480 240" role="img" aria-label="A single loop containing a resistor and two cells whose positive plates face opposite ways, so the cells oppose each other.">
<text x="240" y="26" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">Two opposing EMFs in one loop</text>
<line x1="100" y1="70" x2="380" y2="70" stroke="#1f2937" stroke-width="2"/>
<line x1="380" y1="70" x2="380" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="380" y1="170" x2="250" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="240" y1="170" x2="140" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="130" y1="170" x2="100" y2="170" stroke="#1f2937" stroke-width="2"/>
<line x1="100" y1="170" x2="100" y2="70" stroke="#1f2937" stroke-width="2"/>
<rect x="220" y="62" width="40" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<text x="240" y="54" text-anchor="middle" font-size="12" fill="#4a5262">R</text>
<line x1="250" y1="156" x2="250" y2="184" stroke="#1f2937" stroke-width="2"/>
<line x1="240" y1="162" x2="240" y2="178" stroke="#1f2937" stroke-width="4.5"/>
<line x1="130" y1="156" x2="130" y2="184" stroke="#1f2937" stroke-width="2"/>
<line x1="140" y1="162" x2="140" y2="178" stroke="#1f2937" stroke-width="4.5"/>
<text x="246" y="204" text-anchor="middle" font-size="12" font-weight="600" fill="#b3352f">ε₁ = 6.0 V</text>
<text x="134" y="204" text-anchor="middle" font-size="12" font-weight="600" fill="#1f7a53">ε₂ = 2.0 V</text>
<polygon points="192,64 180,70 192,76" fill="#2f5fd0"/>
<text x="186" y="58" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">I</text>
<text x="330" y="112" text-anchor="middle" font-size="12" fill="#4a5262">net EMF = ε₁ − ε₂</text>
<text x="330" y="132" text-anchor="middle" font-size="12" fill="#4a5262">I = (ε₁ − ε₂) / R</text>
</svg>
<figcaption><b>Opposing sources subtract.</b> Both cells sit in the same loop, but their positive plates face opposite ways, so their EMFs act against each other and the net driving EMF is the <i>difference</i>. The larger cell drives the current; the smaller one is driven <i>against</i> its own EMF, so it <b>absorbs</b> energy rather than supplying it — it is charging. If the two EMFs were equal, the net EMF would be zero and no current would flow at all.</figcaption>
</figure>
<div class="callout callout--warn"><p><b>The trap.</b> If the two EMFs are equal, the net EMF is zero and no current flows — even though both sources are working and there are resistors in the loop. Students often want to add the EMFs, or to assume that a circuit with two batteries must have current in it. Neither is true.</p></div>
<div class="callout callout--key"><p><b>Where the energy goes.</b> The smaller EMF is being <i>driven</i> by the larger one, which means it is absorbing energy rather than supplying it. If it is a rechargeable cell, it is charging. That is the physical content of the question, and it is worth stating explicitly if the question asks you to explain rather than calculate.</p></div>`
    },

    {
      h: "Reconfiguring cells — the sample paper's question shape",
      body: `<p>The sample paper asked what happens when a cell arrangement is switched from series to parallel across the same resistors. The key is that <b>both the EMF and the internal resistance change</b>, and they change in opposite directions.</p>
<table><thead><tr><th>Arrangement of <code>n</code> identical cells</th><th>Net EMF</th><th>Net internal resistance</th><th>Effect on current in a fixed load</th></tr></thead><tbody>
<tr><td>series</td><td><code>nε</code></td><td><code>nr</code></td><td>much larger EMF, but more loss inside</td></tr>
<tr><td>parallel</td><td><code>ε</code></td><td><code>r/n</code></td><td>same EMF as one cell, but far less internal loss</td></tr>
</tbody></table>
<h3>When parallel wins</h3>
<p>If the external resistance <code>R</code> is much smaller than <code>r</code> — a high-current load such as a starter motor — the <code>Ir</code> loss dominates and reducing <code>r</code> matters more than raising <code>ε</code>. Parallel wins.</p>
<h3>When series wins</h3>
<p>If <code>R</code> is much larger than <code>r</code> — a low-current load such as a lamp — the internal loss is negligible and the extra EMF from series gives nearly four times the power for two cells. Series wins.</p>
<div class="callout callout--key"><p><b>The general lesson.</b> Never assume one arrangement is better. Work out the current from <code>I = ε_net/(R + r_net)</code> in each case, then compare <code>I²R</code>. The answer depends on the ratio of <code>R</code> to <code>r</code>, and the question will usually be constructed so that one ratio makes the comparison clean.</p></div>`
    },

    {
      h: "Diodes and rectification",
      body: `<p>A diode conducts in one direction only. In forward bias above roughly 0.6 V it conducts freely; in reverse bias it blocks almost completely.</p>
<p>Put a diode in series with a resistor across an AC supply and the current flows during only one half of each cycle. That is <b>half-wave rectification</b>: the output is a series of pulses rather than a smooth flow, and the current is unidirectional.</p>
<h3>Average power after half-wave rectification</h3>
<p>Take a sinusoidal supply of peak voltage <code>V₀</code> and a resistor <code>R</code>.</p>
<table><thead><tr><th>Case</th><th>Average of <code>V²</code></th><th>Average power</th></tr></thead><tbody>
<tr><td>Full sine wave</td><td><code>V₀²/2</code></td><td><code>V₀²/(2R)</code></td></tr>
<tr><td>Half-wave rectified sine</td><td><code>V₀²/4</code></td><td><code>V₀²/(4R)</code></td></tr>
<tr><td>Square wave, <code>±V₀</code></td><td><code>V₀²</code></td><td><code>V₀²/R</code></td></tr>
</tbody></table>
<p>So half-wave rectification halves the average power, and a square wave gives twice the average power of a sinusoid of the same peak value.</p>
<div class="callout callout--warn"><p><b>The mistake to avoid.</b> Do not take the average of the voltage and then square it. The average of a sinusoid is zero, so that route gives zero power, which is plainly wrong. Average the <b>square</b> of the voltage. The distinction between the mean and the mean square is exactly what this topic is testing.</p></div>`
    },

    {
      h: "Awkward networks — finding equivalent resistance",
      body: `<p>The competition version of circuit analysis is a network that is not a simple series–parallel combination. Three shapes are worth knowing.</p>
<h3>A bridge</h3>
<p>Four resistors in a diamond with a fifth across the middle. If the middle resistor carries no current — which happens when the ratios on the two arms match, <code>R₁/R₂ = R₃/R₄</code> — you can delete it and the network becomes two parallel branches in series. If it does carry current, the problem is not solvable by series–parallel rules alone and you need Kirchhoff's laws.</p>
<h3>A square with both diagonals</h3>
<p>By symmetry, the two nodes on the diagonal you are measuring between are at the same potential as the corresponding nodes across the other diagonal. Points at the same potential can be joined, which collapses the network into something simple. <b>Symmetry is the technique</b>, and it is worth looking for before reaching for algebra.</p>
<h3>A sliding contact round a loop</h3>
<p>A wire loop of total resistance <code>R</code> with a contact that divides it into two arcs. If the contact is a fraction <code>x</code> of the way round, the two arcs have resistances <code>xR</code> and <code>(1−x)R</code>, and they are in <b>parallel</b>:</p>
<div class="formula">R_eq = xR(1−x)R / (xR + (1−x)R) = x(1−x)R</div>
<p>This is a lovely result: the equivalent resistance is zero when the contact is at either end, and a maximum of <code>R/4</code> at the midpoint.</p>
<div class="callout callout--good"><p><b>Look for symmetry before you look for algebra.</b> On a timed paper, the network questions are constructed so that a symmetry argument collapses them. If you find yourself writing three simultaneous equations, stop and look for equal potentials.</p></div>`
    },

    {
      h: "The potential divider",
      body: `<p>Two resistors in series across a supply split the voltage in proportion to their resistances:</p>
<div class="formula">V_out = V_in × R₂/(R₁ + R₂)</div>
<p>where <code>V_out</code> is measured across <code>R₂</code>. Note that the output is proportional to the resistance <b>across which it is measured</b> — this is the part people get backwards.</p>
<h3>Where the formula comes from — one line, no new physics</h3>
<p>The same current <code>I</code> flows through both resistors because they are in series. The p.d. across the lower one is <code>V_out = IR₂</code>, and the total supply is <code>V_in = I(R₁ + R₂)</code>. Divide the first by the second and the current cancels:</p>
<div class="formula">V_out / V_in = R₂ / (R₁ + R₂)</div>
<figure class="fig">
<svg viewBox="0 0 480 290" role="img" aria-label="A potential divider: two resistors in series across a supply, with the output voltage taken across the lower resistor R2.">
<text x="240" y="26" text-anchor="middle" font-size="14" font-weight="600" fill="#14181f">The potential divider</text>
<line x1="150" y1="50" x2="350" y2="50" stroke="#1f2937" stroke-width="2"/>
<line x1="150" y1="255" x2="350" y2="255" stroke="#1f2937" stroke-width="2"/>
<line x1="250" y1="50" x2="250" y2="90" stroke="#1f2937" stroke-width="2"/>
<rect x="242" y="90" width="16" height="42" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="250" y1="132" x2="250" y2="170" stroke="#1f2937" stroke-width="2"/>
<circle cx="250" cy="170" r="4" fill="#2f5fd0"/>
<rect x="242" y="170" width="16" height="42" fill="#ffffff" stroke="#1f2937" stroke-width="2"/>
<line x1="250" y1="212" x2="250" y2="255" stroke="#1f2937" stroke-width="2"/>
<line x1="150" y1="50" x2="150" y2="128" stroke="#1f2937" stroke-width="2"/>
<line x1="136" y1="128" x2="164" y2="128" stroke="#1f2937" stroke-width="2"/>
<line x1="142" y1="148" x2="158" y2="148" stroke="#1f2937" stroke-width="4.5"/>
<line x1="150" y1="148" x2="150" y2="255" stroke="#1f2937" stroke-width="2"/>
<line x1="250" y1="170" x2="330" y2="170" stroke="#1f2937" stroke-width="2"/>
<circle cx="334" cy="170" r="4.5" fill="#1f2937"/>
<line x1="310" y1="172" x2="310" y2="253" stroke="#5b3fa8" stroke-width="1.5" stroke-dasharray="4 4"/>
<polygon points="310,172 305,182 315,182" fill="#5b3fa8"/>
<polygon points="310,253 305,243 315,243" fill="#5b3fa8"/>
<text x="268" y="118" font-size="12" font-weight="600" fill="#4a5262">R₁</text>
<text x="268" y="198" font-size="12" font-weight="600" fill="#4a5262">R₂</text>
<text x="126" y="142" text-anchor="end" font-size="12.5" font-weight="600" fill="#b3352f">V_in</text>
<text x="322" y="216" font-size="12.5" font-weight="600" fill="#5b3fa8">V_out</text>
<text x="344" y="164" font-size="12" fill="#4a5262">output</text>
<polygon points="244,62 250,74 256,62" fill="#2f5fd0"/>
<text x="264" y="70" font-size="12" font-weight="600" fill="#2f5fd0">I</text>
<text x="240" y="280" text-anchor="middle" font-size="11.5" fill="#4a5262">V_out = V_in × R₂ / (R₁ + R₂)</text>
</svg>
<figcaption><b>The output follows the resistor you measure across.</b> The same current passes through both resistors, so the supply divides in proportion to the resistances — <b>not</b> equally. Because the formula is a ratio of two resistances, the units cancel, so kilohms never need converting. Sanity-check with the limits: make <code>R₂</code> much larger than <code>R₁</code> and the output approaches the full supply.</figcaption>
</figure>
<p>so <code>V_out = V_in × R₂/(R₁ + R₂)</code>. It is just Ohm's law applied twice with the same current. Once you see it that way, the "output is proportional to the resistor you measure across" fact is obvious rather than something to memorise backwards — and it is why, in the thermistor example below, swapping which resistor the output is taken across flips the answer.</p>
<h3>Why dividers matter</h3>
<p>They turn a change in resistance into a change in voltage, which is what makes sensors usable. Put a thermistor in a divider and the output voltage becomes a measure of temperature. Put an LDR in and it becomes a measure of light level. In both cases the direction of the response depends on which resistor the output is taken across:</p>
<ul class="tight">
<li>Thermistor in the <b>top</b> position: as temperature rises, its resistance falls, so the voltage across the bottom resistor <b>rises</b>.</li>
<li>Thermistor in the <b>bottom</b> position: as temperature rises, its resistance falls, so the voltage across it <b>falls</b>.</li>
</ul>
<div class="callout callout--key"><p><b>The zero-output limit.</b> If either resistor is zero, the output is either the full supply or zero. If <code>R₂</code> is very large compared with <code>R₁</code>, the output approaches the full supply voltage. If <code>R₂</code> is very small, the output approaches zero. Those two limits let you sanity-check any divider answer instantly.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A cell of EMF 6.0 V and internal resistance 0.50 Ω is connected to an external resistor of 2.5 Ω. What is the terminal potential difference of the cell?</p><p>A) 5.0 V &nbsp; B) 5.5 V &nbsp; C) 6.0 V &nbsp; D) 4.5 V &nbsp; E) 1.0 V</p>",
      sol: `<p><b>Step 1 — total resistance.</b></p>
<div class="formula">R_total = R + r = 2.5 + 0.5 = 3.0 Ω</div>
<p><b>Step 2 — current.</b></p>
<div class="formula">I = ε/R_total = 6.0/3.0 = 2.0 A</div>
<p><b>Step 3 — terminal p.d.</b> The terminal p.d. is the EMF minus the internal loss:</p>
<div class="formula">V = ε − Ir = 6.0 − (2.0 × 0.5) = 6.0 − 1.0 = 5.0 V</div>
<p><b>Answer: A.</b></p>
<p><b>Check by the other route.</b> The external resistor has 2.0 A through 2.5 Ω, so <code>V = IR = 5.0 V</code> ✓. The two routes must agree, and taking the second one when you have time is a free error check.</p>
<p><b>The traps.</b> Option C is the EMF, which is what a voltmeter would read only if no current were flowing. Option E is the internal loss alone (<code>Ir = 1.0 V</code>), which is the amount <i>lost</i>, not the amount delivered. Both are there deliberately.</p>`,
      tag: "Internal resistance — the standard calculation"
    },
    {
      q: "<p>Two cells, of EMF 4.5 V and 1.5 V respectively, are connected in a single loop with a 3.0 Ω resistor. Each cell has negligible internal resistance. The two cells oppose each other. What is the current in the loop, and which way does the energy flow in the smaller cell?</p><p>A) 2.0 A; the 1.5 V cell supplies energy &nbsp; B) 1.0 A; the 1.5 V cell absorbs energy &nbsp; C) 1.0 A; the 1.5 V cell supplies energy &nbsp; D) 2.0 A; the 1.5 V cell absorbs energy &nbsp; E) 0.5 A; the 1.5 V cell absorbs energy</p>",
      sol: `<p><b>Net EMF.</b> The cells oppose, so subtract:</p>
<div class="formula">ε_net = 4.5 − 1.5 = 3.0 V</div>
<p><b>Current.</b> The only resistance in the loop is 3.0 Ω:</p>
<div class="formula">I = 3.0/3.0 = 1.0 A</div>
<p><b>Direction and energy flow.</b> The larger cell drives the current. The smaller cell is being driven <i>against</i> its own EMF, so charge is forced through it from + to −. That means it is absorbing energy rather than supplying it — it is being charged.</p>
<p><b>Answer: B.</b></p>
<p><b>The trap.</b> Option D has the right current magnitude but the wrong energy statement, and option C has the right current but claims the small cell supplies energy. The calculation of the current is the easy part; the question is really testing whether you know that an opposing EMF absorbs energy.</p>
<p><b>The physical check.</b> If the smaller cell were supplying energy too, it would be adding to the drive rather than opposing it, and the EMFs would add. The fact that the question says they <i>oppose</i> settles the direction immediately: the larger one wins, and the smaller one is a load.</p>
<p><b>An extension worth doing.</b> The power delivered by the large cell is <code>4.5 × 1.0 = 4.5 W</code>. The power dissipated in the resistor is <code>I²R = 3.0 W</code>. The power absorbed by the small cell is <code>1.5 × 1.0 = 1.5 W</code>. And <code>4.5 = 3.0 + 1.5</code> ✓. Energy conservation checks out, which is a good habit to build.</p>`,
      tag: "Two opposing EMFs — the sample paper's shape"
    },
    {
      q: "<p>Two identical cells, each of EMF <code>ε</code> and internal resistance <code>r</code>, are available to drive a fixed external resistor <code>R</code>. They can be connected either in series or in parallel. If <code>R</code> is much larger than <code>r</code>, which arrangement delivers more power to <code>R</code>, and by roughly what factor?</p><p>A) Parallel, by a factor of 2 &nbsp; B) Series, by a factor of 2 &nbsp; C) Series, by a factor of 4 &nbsp; D) Parallel, by a factor of 4 &nbsp; E) The same</p>",
      sol: `<p>Since <code>R</code> is much larger than <code>r</code>, the internal resistance is a negligible part of the total, so <code>R_total ≈ R</code> in both cases.</p>
<p><b>Series.</b> Net EMF <code>2ε</code>, so</p>
<div class="formula">I_series ≈ 2ε/R   →   P_series = I²R ≈ 4ε²/R</div>
<p><b>Parallel.</b> Net EMF <code>ε</code>, so</p>
<div class="formula">I_parallel ≈ ε/R   →   P_parallel = I²R ≈ ε²/R</div>
<p><b>Ratio.</b> <code>P_series/P_parallel ≈ 4</code>.</p>
<p><b>Answer: C, series by a factor of 4.</b></p>
<p><b>Why the factor is 4 and not 2.</b> Power goes as the square of the current, so doubling the EMF quadruples the power. This is the single most common error on this type of question — answering 2 because the voltage doubled.</p>
<p><b>Why the <code>R ≫ r</code> condition matters.</b> If <code>r</code> were comparable to <code>R</code>, the parallel arrangement's much smaller internal resistance would start to matter, and the comparison would need the full expression. The general forms are:</p>
<div class="formula">P_series = 4ε²R/(R + 2r)²      P_parallel = ε²R/(R + r/2)²</div>
<p>Setting <code>R = r</code> in these gives the same power for both arrangements, which is a neat result and worth verifying as an exercise. It is the boundary case between the two regimes.</p>`,
      tag: "Reconfiguring cells — the sample paper's other shape"
    },
    {
      q: "<p>A resistor of 6 Ω and a resistor of 3 Ω are connected in parallel, and the combination is connected in series with a 4 Ω resistor across a 12 V supply of negligible internal resistance. What is the current drawn from the supply?</p><p>A) 1.2 A &nbsp; B) 1.5 A &nbsp; C) 2.0 A &nbsp; D) 2.4 A &nbsp; E) 3.0 A</p>",
      sol: `<p><b>Step 1 — parallel combination.</b> Use product over sum:</p>
<div class="formula">R_parallel = (6 × 3)/(6 + 3) = 18/9 = 2 Ω</div>
<p><b>Step 2 — total resistance.</b> The parallel pair is in series with the 4 Ω:</p>
<div class="formula">R_total = 2 + 4 = 6 Ω</div>
<p><b>Step 3 — current.</b></p>
<div class="formula">I = V/R_total = 12/6 = 2.0 A</div>
<p><b>Answer: C.</b></p>
<p><b>The sanity checks, done in five seconds each.</b> The parallel combination must be smaller than 3 Ω, the smaller of the two ✓ (it is 2 Ω). The total must therefore be more than 4 Ω and less than 10 Ω ✓ (it is 6 Ω). The current must be less than <code>12/4 = 3 A</code> ✓ and more than <code>12/10 = 1.2 A</code> ✓. Options A and E are eliminated before any real work.</p>
<p><b>Where the wrong answers come from.</b> Option A is what you get from <code>12/(6+3+4)</code>, treating the parallel resistors as if they were in series. Option B comes from <code>12/(6+2)</code>. Both are arithmetic slips on the structure, not on the numbers, which is why identifying the structure first matters.</p>`,
      tag: "Series–parallel combination"
    },
    {
      q: "<p>A 100 W lamp designed for 230 V is connected across a 115 V supply. Assuming its resistance stays constant, what power does it dissipate?</p><p>A) 100 W &nbsp; B) 50 W &nbsp; C) 25 W &nbsp; D) 200 W &nbsp; E) 400 W</p>",
      sol: `<p>Use <code>P = V²/R</code>. The resistance is unchanged, so power is proportional to the square of the voltage:</p>
<div class="formula">P₂/P₁ = (V₂/V₁)² = (115/230)² = (½)² = ¼</div>
<p>So <code>P₂ = 100/4 = 25 W</code>.</p>
<p><b>Answer: C.</b></p>
<p><b>Why not B.</b> Halving the voltage halves the current as well, and the power is the product of the two — so the power falls by a factor of four, not two. Answering 50 W is the classic mistake, and it comes from thinking of power as proportional to voltage rather than to voltage squared.</p>
<p><b>The caveat the question hands you.</b> It says to assume the resistance stays constant. In reality a lamp's resistance falls substantially at lower temperature, so the actual power at 115 V would be rather more than 25 W. The question supplies the assumption precisely to remove that complication, but noticing it shows you understand that a filament lamp does not obey Ohm's law.</p>
<p><b>Generalise it.</b> Halving the voltage gives a quarter of the power. Doubling gives four times. That ratio behaviour is the whole question, and it takes ten seconds without a calculator.</p>`,
      tag: "Power ratio — no calculator needed"
    },
    {
      q: "<p>A potential divider consists of a fixed 4.0 kΩ resistor in series with a thermistor, with the output taken across the thermistor. The supply is 12 V. At 20 °C the thermistor has resistance 4.0 kΩ. At 60 °C its resistance falls to 1.0 kΩ. What happens to the output voltage as the temperature rises from 20 °C to 60 °C?</p><p>A) It rises from 6.0 V to 9.6 V &nbsp; B) It falls from 6.0 V to 2.4 V &nbsp; C) It rises from 6.0 V to 12 V &nbsp; D) It falls from 6.0 V to 0 V &nbsp; E) It stays at 6.0 V</p>",
      sol: `<p>The output is taken across the <b>thermistor</b>, which is in the bottom position. So</p>
<div class="formula">V_out = V_in × R_thermistor / (R_fixed + R_thermistor)</div>
<p><b>At 20 °C.</b> Both resistances are 4.0 kΩ, so the divider splits the supply equally:</p>
<div class="formula">V_out = 12 × 4/(4 + 4) = 6.0 V</div>
<p><b>At 60 °C.</b> The thermistor is now 1.0 kΩ:</p>
<div class="formula">V_out = 12 × 1/(4 + 1) = 12/5 = 2.4 V</div>
<p><b>Answer: B.</b> The output falls from 6.0 V to 2.4 V.</p>
<p><b>The reasoning, which is what the question is really testing.</b> An NTC thermistor's resistance falls as it warms. The output is taken across it, so less resistance across the output means less voltage across it. The output falls. You could have predicted the direction without computing anything.</p>
<p><b>The trap.</b> Option A is what you get if the thermistor were in the <i>top</i> position: then the voltage across the fixed resistor would rise as the thermistor's resistance fell, going from 6.0 V to 9.6 V. Both options are present, and the only way to choose correctly is to read which resistor the output is taken across.</p>
<p><b>The limiting check.</b> If the thermistor's resistance fell to zero, the output would fall to zero. If it rose without limit, the output would approach 12 V. Both limits are consistent with the answer, which is a good confirmation.</p>`,
      tag: "Potential divider with a thermistor"
    },
    {
      q: "<p>A square wire loop of total resistance 8.0 Ω has a sliding contact that can be moved round it. What is the maximum equivalent resistance measurable between the contact and one fixed corner of the loop?</p><p>A) 1.0 Ω &nbsp; B) 2.0 Ω &nbsp; C) 4.0 Ω &nbsp; D) 8.0 Ω &nbsp; E) 16 Ω</p>",
      sol: `<p>Let the contact divide the loop into two arcs. If a fraction <code>x</code> of the total length lies on one side, the two arc resistances are <code>8x</code> and <code>8(1 − x)</code>.</p>
<p>These two arcs are in <b>parallel</b> between the two measurement points, so</p>
<div class="formula">R_eq = xR(1 − x)R / (xR + (1 − x)R) = x(1 − x)R</div>
<p>with <code>R = 8.0 Ω</code>. The product <code>x(1 − x)</code> is maximised at <code>x = ½</code>, where it equals ¼. So</p>
<div class="formula">R_max = ¼ × 8.0 = 2.0 Ω</div>
<p><b>Answer: B.</b></p>
<p><b>Check the extremes.</b> At <code>x = 0</code> or <code>x = 1</code> the contact is at the fixed corner, so both measurement points coincide and the resistance is zero ✓. At the midpoint the answer is <code>R/4</code> ✓. Both limits match the formula, which confirms the structure.</p>
<p><b>The trap.</b> Option D, 8.0 Ω, is the resistance of the whole loop — the answer you get if you forget that the two arcs are in parallel and add them instead. Option C, 4.0 Ω, is <code>R/2</code>, which is what you get by taking the arithmetic mean of the two arc resistances instead of their parallel combination.</p>
<p><b>Why this matters.</b> The result <code>R/4</code> for a sliding contact on a loop is worth remembering in its own right, and the technique — identifying that two paths between the same pair of points must be in parallel — is the general move for all network questions.</p>`,
      tag: "Network reduction — sliding contact"
    },
    {
      q: "<p>A potential divider consists of two equal resistors <code>R</code> in series across a supply <code>V</code>, with the output taken across the lower resistor. The lower resistor is then replaced by one of resistance <code>3R</code>. By what factor does the output voltage change?</p><p>A) 1/2 &nbsp; B) 2/3 &nbsp; C) 3/2 &nbsp; D) 2 &nbsp; E) 3</p>",
      sol: `<p><b>Before the change.</b> The two resistors are equal, so the divider splits the supply equally and the output across the lower one is</p>
<div class="formula">V_old = V × R/(R + R) = V/2</div>
<p><b>After the change.</b> The lower resistor is now <code>3R</code>; the top one is still <code>R</code>:</p>
<div class="formula">V_new = V × 3R/(R + 3R) = V × 3/4 = 3V/4</div>
<p><b>The factor.</b> Divide the new by the old and the supply <code>V</code> cancels:</p>
<div class="formula">V_new / V_old = (3V/4) / (V/2) = (3/4) × (2/1) = 3/2</div>
<p><b>Answer: C — the output increases by a factor of 3/2.</b></p>
<p><b>The reasoning without arithmetic.</b> The output is proportional to the resistor you measure across. That resistor grew from <code>R</code> to <code>3R</code>, a factor of 3, but it grew relative to a fixed total, so the voltage ratio cannot triple — the denominator grew too. The clean way to see it is exactly the algebra above, which takes about ten seconds and needs no calculator.</p>
<p><b>The trap.</b> Option B, 2/3, is the old value divided by the new — the inverse factor, for anyone who wrote the ratio the wrong way round. Option D, 2, is what you get if you notice the resistor tripled but forget that the total also increased and simply say "the output tripled". Option E, 3, is the change in the <i>resistor</i>, not the change in the <i>voltage</i>. All three are the same underlying error: conflating the resistance ratio with the voltage ratio. This is the divider analogue of the series/parallel power warning — the shared quantity is current, not voltage, so nothing scales in lockstep with a single resistance.</p>`,
      tag: "Potential divider — ratio reasoning, no calculator"
    },
    {
      q: "<p>A cell of EMF 12 V and internal resistance 1.0 Ω is connected to an external resistor of 5.0 Ω. What power is dissipated inside the cell itself?</p><p>A) 4.0 W &nbsp; B) 24 W &nbsp; C) 20 W &nbsp; D) 2.0 W &nbsp; E) 10 W</p>",
      sol: `<p><b>Step 1 — the current.</b> The total resistance in the circuit is the external resistor plus the internal resistance:</p>
<div class="formula">R_total = R + r = 5.0 + 1.0 = 6.0 Ω
I = ε/R_total = 12/6.0 = 2.0 A</div>
<p><b>Step 2 — power inside the cell.</b> The internal resistance <code>r</code> is where the cell's own losses happen. The power dissipated there is</p>
<div class="formula">P_internal = I²r = (2.0)² × 1.0 = 4.0 W</div>
<p>Equivalently, the "lost volts" (电位损失) are <code>Ir = 2.0 V</code>, and the lost power is <code>(lost volts) × I = 2.0 × 2.0 = 4.0 W</code> — the same number, which is a free check.</p>
<p><b>Answer: A.</b></p>
<p><b>The traps.</b> Option B, 24 W, is <code>εI</code> — the total power the cell supplies, to both the external resistor and to itself. Option C, 20 W, is <code>I²R</code>, the power delivered to the external resistor. Option D, 2.0 W, is the lost volts alone, <code>Ir</code>, without the extra factor of <code>I</code> that turns a voltage into a power. The question asks specifically for the power <i>inside the cell</i>, which is the <code>I²r</code> term in the energy balance <code>εI = I²R + I²r</code>.</p>
<p><b>The general point.</b> The EMF times the current is the total rate at which the cell converts chemical energy; part goes to the load (<code>I²R</code>) and part is wasted heating the cell (<code>I²r</code>). Check the energy balance: <code>εI = 24 W = 20 W + 4 W</code> ✓. This is exactly the "lost volts" picture made quantitative — the 2.0 V lost internally is not a voltage you can use, and multiplied by the current it is 4 W of heat you did not want.</p>`,
      tag: "Internal resistance — lost volts and power inside the cell"
    }
  ],

  traps: [
    "Answering the EMF when the question asks for the terminal potential difference. They differ by <code>Ir</code>.",
    "Adding EMFs that are opposed. Two opposing sources give the <i>difference</i>, not the sum.",
    "Assuming a circuit with two batteries must have current. If the EMFs are equal and opposed, the current is zero.",
    "Forgetting that power goes as the square of the current or voltage, so doubling gives a factor of 4 and halving gives a factor of ¼.",
    "Using <code>P = I²R</code> in a parallel circuit. Use <code>P = V²/R</code> there, because the voltage is the shared quantity.",
    "Thinking the largest resistance always dissipates the most power. That is true in series only; in parallel it dissipates the least.",
    "Taking the average of a sinusoidal voltage rather than the average of its square. The former is zero and gives nonsense.",
    "Forgetting to include internal resistance in the total when computing the current.",
    "Treating a parallel combination as a series one, or forgetting that the total parallel resistance is always less than the smallest individual resistance."
  ],

  checklist: [
    { id: "H1", flag: "CORE", text: "Definitions from first principles: <code>I = ΔQ/Δt</code>, <code>V = W/Q</code>, <code>R = V/I</code>, and what each one means physically." },
    { id: "H2", flag: "CORE", text: "I–V characteristics of an ohmic conductor, a filament lamp and a semiconductor diode, and the reason for each shape." },
    { id: "H3", flag: "NEW", text: "Thermistors (NTC) and LDRs; how resistance varies with temperature and light; their use in potential dividers, including the direction of the output change." },
    { id: "H4", flag: "CORE", text: "Superconductivity: critical temperature, exactly zero resistance, and the practical applications. Inside AQA AS §3.5.1.3." },
    { id: "H5", flag: "CORE", text: "Resistivity <code>ρ = RA/L</code>; why resistance depends on length and area; the effect of temperature on a metal." },
    { id: "H6", flag: "CORE", text: "Resistors in series and in parallel, including the product-over-sum shortcut and the two sanity checks on each." },
    { id: "H7", flag: "NEW", text: "Equivalent resistance of awkward networks: a balanced bridge, a square with both diagonals, a sliding contact round a loop. Look for symmetry first." },
    { id: "H8", flag: "CORE", text: "Energy and power: <code>E = IVt</code> and <code>P = IV = I²R = V²/R</code>, and knowing which form suits series and which suits parallel." },
    { id: "H9", flag: "CORE", text: "Cells in series and identical cells in parallel, including how the net internal resistance changes." },
    { id: "H10", flag: "NEW", text: "Kirchhoff's laws as conservation of charge and energy, with the sign convention written down explicitly." },
    { id: "H11", flag: "NEW", text: "EMF and internal resistance: <code>ε = I(R + r)</code>, terminal p.d. <code>ε − Ir</code>, and the graph of terminal p.d. against current." },
    { id: "H12", flag: "NEW", text: "Reconfiguring cells from series to parallel across the same resistors, and comparing the power delivered in each case." },
    { id: "H13", flag: "NEW", text: "Two opposing EMFs in one loop: net EMF, current direction, and recognising that the smaller source absorbs energy." },
    { id: "H14", flag: "CORE", text: "The potential divider <code>V_out = V_in R₂/(R₁ + R₂)</code>, including the limiting cases and the sensor applications." },
    { id: "H15", flag: "NEW", text: "Diodes in AC circuits; half-wave rectification; average power for square, sinusoidal and half-wave-rectified supplies." },
    { id: "H16", flag: "R1-ONLY", text: "Charge accumulated as <code>∫I dt</code> with a time-varying current. Round 1 material — insurance only." },
    { id: "H17", flag: "CORE", text: "Electrical heating, and comparing power dissipation between configurations using ratio reasoning." }
  ]
}

]);
