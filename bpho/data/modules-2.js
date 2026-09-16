/* BPhO Round 0 — curriculum, part 2 of 6.
   Modules I (capacitors), L (quantum phenomena), M (fluids). */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "I",
  title: "Capacitors",
  short: "Capacitors",
  priority: 2,
  tier: "Tier A — named explicitly in the official Round 0 scope",
  why: "A short module with a high return. BPhO names <code>Q = CV</code> in its own scope statement, so capacitors are definitely in play, and the sample paper devotes a question to expressing the farad in base units. Everything you need fits in about forty minutes of work.",
  warn: "<p><b>RC circuits are excluded.</b> Charging and discharging curves, time constants and exponential decay are <i>not</i> on this paper — the official scope rules them out, and the 2024 Round 1 Section 2 paper tests exactly that material, which confirms it belongs to the next round. Do not spend time on them.</p>",

  sections: [
    {
      h: "Capacitance defined",
      body: `<p>A capacitor stores charge. The more charge you put on it, the higher the potential difference across it, and for a given capacitor those two are proportional:</p>
<div class="formula">Q = CV</div>
<p>where <code>Q</code> is the charge on one plate in coulombs, <code>V</code> is the potential difference in volts, and <code>C</code> is the <b>capacitance</b> in farads. Capacitance is a property of the construction of the capacitor — the area of the plates, their separation, and the material between them — not of how it is being used.</p>
<p>One farad is one coulomb per volt. That is a very large capacitance for a real component, so in practice you meet microfarads (μF), nanofarads (nF) and picofarads (pF).</p>
<h3>What the capacitance actually measures</h3>
<p>Because <code>C = Q/V</code>, capacitance is literally how much charge the capacitor can hold per volt across it — a kind of electrical "capacity" (电容, the 中文 name says it directly). A larger capacitance means more charge stored for the same voltage. For a parallel-plate capacitor, two things set the size of <code>C</code>: a bigger plate area <code>A</code> gives more room to park charge, and a smaller plate separation <code>d</code> means the opposite charges sit closer and attract each other more strongly, so more charge piles up at the same voltage. Sliding an insulating material (a dielectric, 电介质) between the plates also raises <code>C</code>. You do not need the formula <code>C = εA/d</code> for Round 0, but the qualitative direction is worth knowing: <b>more area, smaller gap, better dielectric → larger capacitance</b>.</p>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> Do not confuse "capacitance" with "charge". A 10 μF capacitor does not "contain 10 μC" — it contains <code>10 μF × V</code> microcoulombs, whatever <code>V</code> happens to be. Capacitance is a property of the object; charge depends on how you use it. The 中文 picture: capacitance is the bucket (its size), charge is the water you poured in.</p></div>
<div class="callout callout--key"><p><b>Read <code>Q</code> carefully.</b> The charge <code>Q</code> in the equation is the magnitude of the charge on <i>one</i> plate. The two plates carry equal and opposite charges, so the total net charge on a capacitor is always zero. When a question asks about charge, it means the charge on one plate.</p></div>`
    },

    {
      h: "The farad in base units",
      body: `<p>The sample paper asks for this, so it is worth having automatic. Work from the definition outward.</p>
<ol class="steps">
<li>Capacitance is charge per volt: <code>1 F = 1 C V⁻¹</code>.</li>
<li>Charge is current times time: <code>1 C = 1 A s</code>.</li>
<li>A volt is a joule per coulomb: <code>1 V = 1 J C⁻¹</code>. A joule is <code>kg m² s⁻²</code>.</li>
<li>Substitute: <code>1 V = kg m² s⁻² / (A s) = kg m² s⁻³ A⁻¹</code>.</li>
<li>Substitute again into the farad:</li>
</ol>
<div class="formula">1 F = (A s) / (kg m² s⁻³ A⁻¹) = kg⁻¹ m⁻² s⁴ A²</div>
<p>The signature is the <b>negative exponents on kg and m</b>. Capacitance is the only common electrical unit where mass and length appear in the denominator. If you derive something in a capacitance context and mass comes out positive, you have made an error.</p>`
    },

    {
      h: "Capacitors in series and in parallel",
      body: `<p>This is the part that trips people up, because the rules are the <b>opposite</b> of the resistor rules. Learn why rather than memorising which is which.</p>
<h3>Parallel — the plates add up</h3>
<p>Two capacitors in parallel have their top plates joined together and their bottom plates joined together, so both are at the same potential difference <code>V</code>. The total charge stored is the sum of the individual charges:</p>
<div class="formula">Q_total = Q₁ + Q₂ = C₁V + C₂V = (C₁ + C₂)V
so  C_parallel = C₁ + C₂</div>
<p>This makes sense physically: putting capacitors in parallel is equivalent to making one capacitor with a larger plate area, and larger area means more capacitance.</p>
<h3>Series — the reciprocals add</h3>
<p>Two capacitors in series carry the <b>same charge</b> <code>Q</code>, because the isolated middle section cannot gain or lose charge. The voltages add:</p>
<div class="formula">V = V₁ + V₂ = Q/C₁ + Q/C₂ = Q(1/C₁ + 1/C₂)
so  1/C_series = 1/C₁ + 1/C₂</div>
<p>Physically this is equivalent to increasing the separation between the plates, which reduces capacitance. So the combined capacitance is always <b>smaller</b> than the smallest individual capacitance.</p>
<div class="callout callout--key"><p><b>The memory hook.</b> Capacitors combine the opposite way to resistors. Resistors in series add; capacitors in series reciprocal-add. If you can remember that a capacitor is a resistor with the rules swapped, you never need to think about which is which.</p></div>
<h3>Two capacitors in series, the quick form</h3>
<p>For exactly two capacitors the reciprocal expression rearranges to the product-over-sum form:</p>
<div class="formula">C_series = C₁C₂ / (C₁ + C₂)</div>
<p>This is the same structure as the formula for two resistors in parallel. Worth knowing because it is faster than dealing with reciprocals under time pressure.</p>
<h3>A quick numerical feel</h3>
<p>Suppose <code>C₁ = 2 μF</code> and <code>C₂ = 6 μF</code>. In parallel: <code>C = 2 + 6 = 8 μF</code>. In series: <code>1/C = 1/2 + 1/6 = 4/6 = 2/3</code>, so <code>C = 3/2 = 1.5 μF</code>. Note the pattern: parallel gives the <i>sum</i> (bigger), series gives a value <i>smaller than either</i> (1.5 μF is less than both 2 and 6). If your series answer ever comes out larger than the smaller capacitor, you have inverted something.</p>
<div class="callout callout--bad"><p><b>How to get this wrong.</b> The most common slip is to add capacitors in series the way you add resistors in series — straight addition. That is backwards. Resistors in series add; capacitors in series reciprocal-add. If a question says "two capacitors in series" and one option is simply <code>C₁ + C₂</code>, that is the resistor rule misapplied, and it is a trap.</p></div>`
    },

    {
      h: "Energy stored",
      body: `<p>Charging a capacitor means pushing charge onto a plate that is already at a potential, so the work done is not simply <code>QV</code> — the voltage rises from zero to <code>V</code> as the charge accumulates.</p>
<h3>The derivation</h3>
<p>Plot potential difference against charge. It is a straight line through the origin with gradient <code>1/C</code>. The work done to add a small charge <code>dq</code> at potential <code>v</code> is <code>v dq</code>, so the total energy is the area under the graph — a triangle:</p>
<div class="formula">E = ½ × base × height = ½ × Q × V</div>
<p>Substituting <code>Q = CV</code> gives the three equivalent forms, all of which appear as options:</p>
<div class="formula">E = ½QV = ½CV² = Q²/(2C)</div>
<div class="callout callout--key"><p><b>Why the half.</b> A common wrong option is <code>QV</code> with no half. That would be the energy if the charge had been pushed on at full voltage throughout. It was not — the average voltage during charging is <code>V/2</code>. The factor of ½ is the signature of a linear ramp, and it appears in the same way in the elastic strain energy <code>½FΔL</code> and the kinetic energy <code>½mv²</code>.</p></div>
<h3>Why all three forms are the same thing</h3>
<p>The three expressions are not three different energies — they are the same energy written in terms of different pairs of variables. Start from <code>E = ½QV</code>. Substitute <code>Q = CV</code> and you get <code>E = ½(CV)V = ½CV²</code>. Substitute <code>V = Q/C</code> instead and you get <code>E = ½Q(Q/C) = Q²/(2C)</code>. So all three follow from the single fact <code>Q = CV</code> plus the ½ from the triangle. On a multiple-choice paper this matters because the options often offer all three forms and you must recognise that they are equivalent, not competing.</p>
<div class="callout callout--good"><p><b>Which form to reach for.</b> Pick the form that contains only the quantity held constant. If the charge is fixed (isolated capacitor), use <code>Q²/2C</code>. If the voltage is fixed (still connected to the battery), use <code>½CV²</code>. If you are given both <code>Q</code> and <code>V</code>, use <code>½QV</code>. Choosing the wrong form is exactly how you miss a hidden change in the other variable.</p></div>
<h3>Where the energy goes</h3>
<p>When a capacitor charges through a resistor, exactly half the energy supplied by the battery ends up stored in the capacitor, and the other half is dissipated as heat in the resistance. This is true regardless of the size of the resistance, which is a surprising result and a favourite of competition questions. The reason is that the battery supplies <code>QV</code> while the capacitor stores <code>½QV</code>.</p>`
    },

    {
      h: "Changing the capacitor: separating plates or inserting a dielectric",
      body: `<p>Competition questions love to ask what happens to the charge, voltage and stored energy when you alter the capacitor itself. The trick is to fix which quantity is held constant first — that decides everything else.</p>
<h3>Case 1 — isolated capacitor (charge fixed)</h3>
<p>If the capacitor is disconnected from the battery, the charge <code>Q</code> cannot change. Now separate the plates: the capacitance falls, because moving the plates apart reduces <code>C</code> (smaller gap → larger capacitance, so bigger gap → smaller <code>C</code>). Since <code>Q = CV</code> with <code>Q</code> fixed, the voltage <code>V</code> must rise. The energy, using the constant-charge form, is</p>
<div class="formula">E = Q²/(2C)</div>
<p>With <code>Q</code> fixed and <code>C</code> smaller, the energy <b>increases</b>. Where did the energy come from? You did mechanical work pulling the oppositely-charged plates apart against their attraction. So an isolated capacitor stores more energy when you pull its plates apart.</p>
<h3>Case 2 — connected to the battery (voltage fixed)</h3>
<p>If the capacitor stays connected to the battery, the voltage <code>V</code> is held fixed by the battery. Separate the plates and <code>C</code> falls again. Now <code>Q = CV</code> with <code>V</code> fixed means the charge <code>Q</code> <b>falls</b> — charge flows back to the battery. The energy, using the constant-voltage form, is</p>
<div class="formula">E = ½CV²</div>
<p>With <code>V</code> fixed and <code>C</code> smaller, the energy <b>decreases</b>. This is the opposite outcome to Case 1, which is exactly why you must state which case you are in.</p>
<h3>Inserting a dielectric</h3>
<p>Sliding an insulating slab between the plates raises the capacitance by a factor <code>k</code> (the dielectric constant, 介电常数). Isolated, <code>Q</code> fixed so <code>V</code> drops to <code>V/k</code> and the energy drops to <code>E/k</code>. Connected to the battery, <code>V</code> fixed so <code>Q</code> rises to <code>kQ</code> and the energy rises to <code>kE</code>. The direction always flips with the case.</p>
<div class="callout callout--warn"><p><b>The error to avoid.</b> Never say "the energy doubles" without saying which quantity is held constant. For the same physical change (plates pulled apart), the energy goes <i>up</i> if isolated and <i>down</i> if connected. The single word "isolated" or "connected" determines the answer, and questions are written so that both outcomes appear as options.</p></div>`
    },

    {
      h: "The half-energy rule when charging from a battery",
      body: `<p>A subtle and frequently-tested result: when you charge a capacitor from a battery of fixed voltage <code>V</code>, the battery supplies energy <code>QV</code> but only <code>½QV</code> ends up stored. The missing half is lost as heat in the resistance of the circuit (or, in the ideal limit, radiated away). This holds for <i>any</i> resistance, large or small.</p>
<p>Why does it not depend on the resistance? The energy stored depends only on the final state <code>(Q, V)</code>, via <code>½QV</code>. The battery always supplies <code>QV</code> because it moves total charge <code>Q</code> across the fixed potential difference <code>V</code>. The gap between them is fixed by the geometry of the charge–voltage line, not by how fast the charge arrives. So whether the resistor is 1 Ω or 1 MΩ, exactly half the battery's energy is dissipated.</p>
<div class="callout callout--key"><p><b>How a question uses this.</b> If asked "what fraction of the battery's energy is stored" in a single charging from fixed voltage, the answer is always <code>½</code>. If instead the capacitor is already charged to <code>V</code> and you reconnect it to <code>2V</code> to double the voltage, the extra energy stored is <code>½C(2V)² − ½CV² = 3·½CV²</code> while the battery supplies the extra charge <code>CV</code> at the higher average voltage — a different bookkeeping, so do not blindly reuse the ½.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A 4 μF capacitor and a 12 μF capacitor are connected first in series and then in parallel. What is the ratio of the series combination to the parallel combination?</p><p>A) 1 : 3 &nbsp; B) 3 : 16 &nbsp; C) 1 : 4 &nbsp; D) 4 : 3 &nbsp; E) 3 : 4</p>",
      sol: `<p><b>Parallel:</b> capacitances simply add.</p>
<div class="formula">C_parallel = 4 + 12 = 16 μF</div>
<p><b>Series:</b> use the product-over-sum form.</p>
<div class="formula">C_series = (4 × 12)/(4 + 12) = 48/16 = 3 μF</div>
<p><b>Ratio:</b> <code>3 : 16</code>.</p>
<p><b>Answer: B.</b></p>
<p><b>The sanity check.</b> The series combination must be smaller than the smaller capacitor (3 μF &lt; 4 μF ✓), and the parallel combination must be larger than the larger capacitor (16 μF &gt; 12 μF ✓). Those two facts alone eliminate any option where the series value exceeds 4 or the parallel value is below 12.</p>
<p><b>The trap.</b> Option E, <code>3 : 4</code>, comes from getting the ratio the wrong way round, and option D, <code>4 : 3</code>, from doing that and using the series value alone. Write the ratio in the order the question asks for it.</p>`,
      tag: "Series and parallel — with a sanity check"
    },
    {
      q: "<p>A capacitor of capacitance <code>C</code> is charged to a potential difference <code>V</code>. It is then disconnected from the supply and the separation of its plates is doubled, with the charge remaining constant. What happens to the energy stored?</p><p>A) It halves &nbsp; B) It is unchanged &nbsp; C) It doubles &nbsp; D) It quadruples &nbsp; E) It falls to a quarter</p>",
      sol: `<p>Two things change when the plates are separated: the capacitance falls, and the potential difference rises. Charge cannot change because the capacitor is isolated.</p>
<p>Doubling the separation halves the capacitance, so <code>C₂ = C/2</code>. Since <code>Q</code> is fixed and <code>Q = CV</code>, the potential difference must double: <code>V₂ = 2V</code>.</p>
<p>Now use the form of the energy that involves only <code>Q</code> and <code>C</code>, so that no hidden dependence creeps in:</p>
<div class="formula">E = Q²/(2C)</div>
<p>With <code>Q</code> fixed and <code>C</code> halved, the denominator halves, so <code>E</code> doubles.</p>
<p><b>Answer: C.</b></p>
<p><b>Why you must choose the right form.</b> If you use <code>E = ½CV²</code> and only notice that <code>C</code> halves, you get <code>E</code> halved — option A. If you only notice that <code>V</code> doubles, you get <code>E</code> quadrupled — option D. Both are there. The discipline is to pick the form of the equation containing only quantities you know are constant, which here is <code>Q</code>.</p>
<p><b>The physics.</b> You are doing work pulling the plates apart, because opposite charges attract. That mechanical work is exactly the extra energy stored. The capacitor acts as a device that converts mechanical work into stored electrical energy.</p>`,
      tag: "Choosing the right form of the energy equation"
    },
    {
      q: "<p>Which of the following gives the base units of the farad?</p><p>A) <code>kg m² s⁻³ A⁻²</code> &nbsp; B) <code>kg⁻¹ m⁻² s⁴ A²</code> &nbsp; C) <code>kg m² s⁻³ A⁻¹</code> &nbsp; D) <code>kg⁻¹ m⁻² s³ A²</code> &nbsp; E) <code>kg⁻¹ m⁻² s⁴ A⁻¹</code></p>",
      sol: `<p>Build it from the definitions.</p>
<div class="formula">1 F = 1 C V⁻¹
1 C = 1 A s
1 V = 1 J C⁻¹ = (kg m² s⁻²)/(A s) = kg m² s⁻³ A⁻¹</div>
<p>Substitute the volt into the farad:</p>
<div class="formula">1 F = (A s) / (kg m² s⁻³ A⁻¹)
    = A s × kg⁻¹ m⁻² s³ A
    = kg⁻¹ m⁻² s⁴ A²</div>
<p><b>Answer: B.</b></p>
<p><b>The signature to look for.</b> Negative exponents on kg and m. Capacitance is the only common electrical unit where mass and length appear in the denominator, so if your working produces a positive power of kg in a capacitance context, you have slipped.</p>
<p><b>The other options, diagnosed.</b> A is the <b>ohm</b> — the same as B but with the signs on kg and m flipped. C is the <b>volt</b>, which is a very common confusion because the farad and the volt are one reciprocal apart. D has the power of <code>s</code> wrong by one, which is what you get if you forget that a joule is <code>s⁻²</code> and not <code>s⁻¹</code>. E has the power of A wrong by one.</p>
<p><b>How to answer this in twenty seconds.</b> You do not need to remember the farad at all — you need to remember the volt, because it is far more common. Then the farad is <code>C/V</code>, and one substitution gives the answer. Deriving beats recalling, especially under time pressure when memory is less reliable.</p>`,
      tag: "Base units — the sample paper's capacitor question"
    },
    {
      q: "<p>Two identical capacitors, each of capacitance <code>C</code>, are connected in series across a battery of EMF <code>V</code>. What is the total energy stored in the pair?</p><p>A) <code>CV²</code> &nbsp; B) <code>½CV²</code> &nbsp; C) <code>¼CV²</code> &nbsp; D) <code>2CV²</code> &nbsp; E) <code>CV²/8</code></p>",
      sol: `<p><b>Step 1 — combined capacitance.</b> Two equal capacitors in series give</p>
<div class="formula">1/C_total = 1/C + 1/C = 2/C   →   C_total = C/2</div>
<p><b>Step 2 — energy.</b> The total potential difference across the pair is <code>V</code>, so</p>
<div class="formula">E = ½ C_total V² = ½ × (C/2) × V² = ¼ CV²</div>
<p><b>Answer: C.</b></p>
<p><b>The trap.</b> Option B, <code>½CV²</code>, is what you get by treating the pair as a single capacitor of capacitance <code>C</code>. Option A comes from using <code>CV²</code> without the half. Both are there for a reason.</p>
<p><b>An independent check.</b> Each capacitor carries the same charge and has half the voltage across it, so each stores <code>½C(V/2)² = CV²/8</code>. Two of them give <code>CV²/4</code> ✓. The two routes agree, which is a good habit: whenever a combination question has a second route, take it and compare.</p>`,
      tag: "Series combination feeding the energy formula"
    },

    {
      q: "<p>Two 4 μF capacitors are connected in parallel, and that combination is connected in series with an 8 μF capacitor. The whole network is charged to 10 V. What is the total energy stored?</p><p>A) 100 μJ &nbsp; B) 200 μJ &nbsp; C) 400 μJ &nbsp; D) 800 μJ &nbsp; E) 50 μJ</p>",
      sol: `<p><b>Step 1 — equivalent capacitance.</b> The parallel pair: <code>4 + 4 = 8 μF</code>. Now that 8 μF is in series with the other 8 μF:</p>
<div class="formula">C_eq = (8 × 8)/(8 + 8) = 64/16 = 4 μF</div>
<p><b>Step 2 — energy.</b> The whole network is at 10 V, so</p>
<div class="formula">E = ½ C_eq V² = ½ × 4 × 10⁻⁶ × 10² = ½ × 4 × 10⁻⁶ × 100 = 2.0 × 10⁻⁴ J = 200 μJ</div>
<p><b>Answer: B, 200 μJ.</b></p>
<p><b>The trap.</b> Option C, 400 μJ, is what you get if you stop after finding the parallel pair (8 μF) and forget the series step entirely — you use <code>C = 8 μF</code> instead of 4 μF. Option D, 800 μJ, comes from the same 8 μF but omitting the ½. Always finish the combination before touching the energy formula; the energy question is really a combination question wearing a disguise.</p>
<p><b>The quick sanity check.</b> The series step must reduce the capacitance below the smaller branch (8 μF), so <code>C_eq</code> must be under 8 μF. Any answer using a capacitance of 8 μF or more is automatically wrong.</p>`,
      tag: "Combination plus energy — finish the network first"
    },

    {
      q: "<p>A capacitor is charged to a potential difference V and stores energy E. It remains connected to the battery, and the plate separation is then doubled. What happens to the stored energy?</p><p>A) It halves &nbsp; B) It is unchanged &nbsp; C) It doubles &nbsp; D) It quadruples &nbsp; E) It falls to a quarter</p>",
      sol: `<p>The capacitor stays connected to the battery, so the voltage <code>V</code> is fixed. Doubling the plate separation halves the capacitance: <code>C₂ = C/2</code>.</p>
<p>Use the constant-voltage form of the energy:</p>
<div class="formula">E = ½CV²   →   E₂ = ½(C/2)V² = ½ · E</div>
<p>So the stored energy <b>halves</b>.</p>
<p><b>Answer: A.</b></p>
<p><b>Why you must name the case.</b> If the capacitor had been <i>isolated</i> (disconnected, charge fixed), the same doubling of separation would have <i>doubled</i> the energy — that is option C, which is the trap. Both outcomes appear as options precisely because the answer hinges on the single word "connected". Here "remains connected to the battery" pins the voltage, so the energy follows <code>½CV²</code> and falls.</p>
<p><b>Physical picture.</b> With the battery holding the voltage fixed, pulling the plates apart forces charge to flow back into the battery, so the capacitor ends up with less charge and less stored energy.</p>`,
      tag: "Changing the capacitor — voltage held constant"
    },

    {
      q: "<p>A 2 μF capacitor is charged to 10 V and then disconnected from the supply. It is connected in parallel with an uncharged 3 μF capacitor. What is the final common potential difference across both?</p><p>A) 2 V &nbsp; B) 4 V &nbsp; C) 6 V &nbsp; D) 8 V &nbsp; E) 10 V</p>",
      sol: `<p><b>Step 1 — initial charge.</b> On the 2 μF capacitor: <code>Q = CV = 2 × 10⁻⁶ × 10 = 20 μC</code>. The 3 μF capacitor is uncharged.</p>
<p><b>Step 2 — after connecting.</b> Charge is conserved (no battery in the loop): total charge is still 20 μC. The two capacitors are now in parallel, so they share the same voltage <code>V_f</code> and the combined capacitance is <code>2 + 3 = 5 μF</code>.</p>
<div class="formula">V_f = Q_total / C_total = 20 μC / 5 μF = 4 V</div>
<p><b>Answer: B, 4 V.</b></p>
<p><b>The trap.</b> Option E, 10 V, is the original voltage — it ignores the fact that charge is now shared over a larger total capacitance. Option C, 6 V, is a meaningless average of the two capacitances. The key idea: the total charge is fixed, so adding capacitance at fixed charge <i>lowers</i> the voltage (<code>V = Q/C</code>).</p>
<p><b>The redistribution check.</b> After connection, the 2 μF capacitor holds <code>2 × 4 = 8 μC</code> and the 3 μF holds <code>3 × 4 = 12 μC</code>; they sum to 20 μC, confirming conservation. The charge has simply moved from one plate group to the other until the voltages equalised.</p>`,
      tag: "Charge sharing between capacitors at equilibrium"
    },

    {
      q: "<p>A capacitor stores a charge of 30 μC when the potential difference across it is 10 V. What is the energy stored?</p><p>A) 150 μJ &nbsp; B) 300 μJ &nbsp; C) 75 μJ &nbsp; D) 30 μJ &nbsp; E) 600 μJ</p>",
      sol: `<p>Use the form containing the two given quantities, <code>Q</code> and <code>V</code>:</p>
<div class="formula">E = ½QV = ½ × 30 × 10⁻⁶ × 10 = 150 × 10⁻⁶ J = 150 μJ</div>
<p><b>Answer: A, 150 μJ.</b></p>
<p><b>Check with the other two forms.</b> First find <code>C = Q/V = 30 μC / 10 V = 3 μF</code>. Then <code>½CV² = ½ × 3 × 10⁻⁶ × 100 = 150 μJ</code> ✓, and <code>Q²/(2C) = (30×10⁻⁶)² / (2 × 3×10⁻⁶) = 900×10⁻¹² / 6×10⁻⁶ = 150 μJ</code> ✓. All three forms agree — they must, because they are the same energy.</p>
<p><b>The trap.</b> Option B, 300 μJ, is the missing-half error: <code>QV</code> without the ½. This is the single most common capacitor slip, and it is offered here on purpose. Option C would be a quarter, option D is just the charge misread as an energy, and option E is <code>QV</code> in the wrong unit.</p>`,
      tag: "Energy — all three forms agree"
    }
  ],

  traps: [
    "Using <code>QV</code> instead of <code>½QV</code> for the energy. The factor of ½ is because the voltage ramps up from zero.",
    "Getting series and parallel the wrong way round. Capacitors are the opposite of resistors: series reciprocal-adds.",
    "Forgetting that two capacitors in series carry the <i>same</i> charge, not the same voltage.",
    "Choosing <code>E = ½CV²</code> in a problem where the charge is constant and the capacitance changes. Use <code>Q²/2C</code> instead, or you will miss the hidden change in <code>V</code>.",
    "Confusing the farad with the volt in base units. They differ by exactly one reciprocal.",
    "Spending time on RC charging and discharging. It is explicitly excluded from Round 0."
  ],

  checklist: [
    { id: "I1", flag: "CORE", text: "<code>Q = CV</code>; definition of capacitance; the farad as one coulomb per volt." },
    { id: "I2", flag: "NEW", text: "Capacitors in series and in parallel, including the product-over-sum shortcut for two in series, and the sanity check on each." },
    { id: "I3", flag: "NEW", text: "Energy stored: <code>½QV = ½CV² = Q²/2C</code>, and knowing which form to use when charge or voltage is the constant." },
    { id: "I4", flag: "NEW", text: "Expressing the farad in base units as <code>kg⁻¹ m⁻² s⁴ A²</code>, derived from the definitions rather than memorised." },
    { id: "I5", flag: "R1-ONLY", text: "Capacitors connected to multiple EMFs; charge distribution across a network. Round 1 material — insurance only." },
    { id: "I6", flag: "SKIP", text: "RC charging and discharging curves, time constants, exponential decay. <b>Explicitly excluded from Round 0.</b> Do not study." }
  ]
},

{
  code: "L",
  title: "Quantum phenomena and photons",
  short: "Quantum & photons",
  priority: 2,
  tier: "Tier A — named in the official Round 0 scope",
  why: "The photoelectric effect is named explicitly in BPhO's Round 0 scope statement, which makes this one of the safest modules on the list. The physics is also unusually clean: one equation, one graph, and a small number of conceptual questions that repeat in the same form year after year.",
  warn: null,

  sections: [
    {
      h: "The photon model",
      body: `<p>Light arrives in discrete packets called photons. A photon of frequency <code>f</code> carries energy</p>
<div class="formula">E = hf = hc/λ</div>
<p>where <code>h</code> is the Planck constant, <code>6.63 × 10⁻³⁴ J s</code>. The two forms are equivalent because <code>c = fλ</code>.</p>
<p>The key structural point, and the one that all the conceptual questions turn on: <b>the energy of a photon depends only on its frequency, not on how many photons there are.</b> Intensity is the number of photons arriving per second. Frequency is the energy each one carries.</p>
<div class="callout callout--key"><p><b>The combination worth memorising.</b> <code>hc ≈ 2.0 × 10⁻²⁵ J m</code>. Then the energy of a visible photon of wavelength <code>λ</code> is <code>2 × 10⁻²⁵ / λ</code>. For 500 nm that is <code>4 × 10⁻¹⁹ J</code>, about 2.5 eV. This turns a two-step calculation into one mental step, which matters when there is no calculator.</p></div>
<h3>Photon energies in electron volts</h3>
<table><thead><tr><th>Radiation</th><th>Wavelength</th><th>Photon energy</th></tr></thead><tbody>
<tr><td>Infrared</td><td>1000 nm</td><td>1.2 eV</td></tr>
<tr><td>Red light</td><td>700 nm</td><td>1.8 eV</td></tr>
<tr><td>Green light</td><td>500 nm</td><td>2.5 eV</td></tr>
<tr><td>Blue light</td><td>400 nm</td><td>3.1 eV</td></tr>
<tr><td>Ultraviolet</td><td>200 nm</td><td>6.2 eV</td></tr>
</tbody></table>
<h3>The quick photon-energy rule in eV</h3>
<p>Because <code>hc = 2.0 × 10⁻²⁵ J m</code> and <code>1 eV = 1.6 × 10⁻¹⁹ J</code>, the photon energy in electron volts is</p>
<div class="formula">E(eV) = hc/(λ × 1.6 × 10⁻¹⁹) = 2.0 × 10⁻²⁵ / (1.6 × 10⁻¹⁹ λ) = 1.24 × 10⁻⁶ / λ = 1240 eV·nm / λ</div>
<p>where <code>λ</code> is in nanometres. This is worth memorising as a single number: a 620 nm photon (red) carries about <code>1240/620 = 2 eV</code>, and the energy scales as <code>1/λ</code>. Shorter wavelength means higher energy — which is why ultraviolet (shorter λ) is what knocks electrons out, while infrared (longer λ) cannot.</p>
<div class="callout callout--key"><p><b>The mental route.</b> Divide 1240 by the wavelength in nm; the result is the photon energy in eV. No joules, no powers of ten. For a 500 nm photon: <code>1240/500 ≈ 2.5 eV</code>, matching the table above. Use this constantly.</p></div>
<p>Notice that visible photons all carry a few electron volts. This is why the photoelectric effect for most metals needs ultraviolet: typical work functions are 2 to 5 eV, so red light often simply does not have enough energy per photon.</p>`
    },

    {
      h: "The photoelectric effect",
      body: `<p>Shine light on a clean metal surface and, above a certain frequency, electrons come off. The effect has four features that classical wave theory cannot explain, and each one is a standard question.</p>
<h3>Feature 1 — there is a threshold frequency</h3>
<p>Below a certain frequency, no electrons are emitted at all, no matter how intense the light or how long you wait. Classical wave theory predicts that energy accumulates, so eventually electrons should come off. They do not.</p>
<h3>Feature 2 — emission is instantaneous</h3>
<p>Above the threshold, electrons appear immediately, with no measurable delay. Wave theory predicts a delay while energy builds up.</p>
<h3>Feature 3 — the maximum kinetic energy depends on frequency, not intensity</h3>
<p>Increase the intensity and you get <i>more</i> electrons, but the fastest ones are no faster. Increase the frequency and the fastest electrons get faster.</p>
<h3>Feature 4 — the maximum kinetic energy is independent of intensity</h3>
<p>Doubling the intensity doubles the number of photons, hence the number of electrons, but each electron still receives exactly one photon's worth of energy.</p>
<div class="callout callout--key"><p><b>The single sentence that answers most of these questions.</b> One photon interacts with one electron. So the energy available to any individual electron is <code>hf</code>, and increasing the intensity only increases the <i>number</i> of such interactions, not the energy of each one.</p></div>
<h3>Einstein's equation</h3>
<p>An electron needs a minimum energy to escape the metal — the <b>work function</b> <code>φ</code>. Whatever is left over becomes kinetic energy. For the most energetic electrons, nothing is lost to collisions on the way out, so</p>
<div class="formula">hf = φ + E_k(max)</div>
<p>Rearranged into straight-line form:</p>
<div class="formula">E_k(max) = hf − φ</div>
<p>So a graph of maximum kinetic energy against frequency is a straight line with <b>gradient h</b> and <b>vertical intercept −φ</b>. The horizontal intercept is the threshold frequency <code>f₀ = φ/h</code>.</p>
<div class="callout callout--good"><p><b>The gradient is <code>h</code> for every metal.</b> That is the point of plotting it: the gradient gives a fundamental constant of nature, while the intercept characterises the particular metal. Questions often give you two metals on one graph and ask which has the larger work function — the answer is whichever line has its horizontal intercept further to the right.</p></div>
<h3>The threshold frequency and the threshold wavelength</h3>
<p>Set <code>E_k(max) = 0</code> in Einstein's equation to find the minimum frequency that just ejects an electron:</p>
<div class="formula">hf₀ = φ   →   f₀ = φ/h</div>
<p>Below <code>f₀</code> no electron is emitted at all, however bright the beam. In wavelength terms, since <code>f = c/λ</code>, there is a longest wavelength <code>λ_max = c/f₀ = hc/φ</code> that can still cause emission. Red light has a long wavelength and low energy; if <code>λ &gt; λ_max</code> the photon is simply too weak, no matter how intense the light.</p>
<div class="callout callout--key"><p><b>The test.</b> A question may give you a work function in eV and ask for the threshold wavelength. Convert <code>φ</code> to joules (multiply by <code>1.6 × 10⁻¹⁹</code>), then <code>λ_max = hc/φ</code> — or use the 1240 eV·nm rule directly: <code>λ_max(nm) = 1240/φ(eV)</code>. That avoids converting units entirely.</p></div>`
    },

    {
      h: "Stopping potential",
      body: `<p>To measure the maximum kinetic energy, apply a reverse potential difference until the current just falls to zero. At that point even the fastest electrons have been turned back, so the electrical work done equals their kinetic energy:</p>
<div class="formula">eV_s = E_k(max)</div>
<p>So <code>E_k(max) = eV_s</code>, which is why energies in this topic are usually quoted in electron volts — the stopping potential in volts is numerically the maximum kinetic energy in electron volts. That is the whole convenience of the unit.</p>
<h3>The photoelectric effect in one table</h3>
<table><thead><tr><th>Change</th><th>Effect on number of electrons</th><th>Effect on max kinetic energy</th></tr></thead><tbody>
<tr><td>Increase intensity</td><td>increases</td><td><b>no change</b></td></tr>
<tr><td>Increase frequency</td><td>no change (if above threshold)</td><td>increases linearly</td></tr>
<tr><td>Decrease wavelength</td><td>no change</td><td>increases</td></tr>
<tr><td>Change the metal to one with a larger φ</td><td>no change</td><td>decreases</td></tr>
</tbody></table>
<div class="callout callout--good"><p><b>Reading the stopping potential off a graph of current against voltage.</b> The photocurrent falls to zero at the reverse voltage <code>−V_s</code>. The kinetic energy of the fastest electron equals <code>eV_s</code>, so <code>V_s = E_k(max)/e</code>. In practice you often just read <code>V_s</code> in volts and quote the kinetic energy in eV with the same number — that is the whole convenience of the electron volt, and it is why stopping-potential questions and eV questions are the same calculation wearing different labels.</p></div>`
    },

    {
      h: "Ionisation, excitation and line spectra",
      body: `<p>Electrons in an atom can only occupy certain discrete energy levels. That single fact explains line spectra, and it is the piece of evidence that killed the classical model of the atom.</p>
<ul class="tight">
<li><b>Excitation</b> — an electron is raised from a lower level to a higher one within the atom, without escaping. It requires exactly the energy difference between the two levels.</li>
<li><b>Ionisation</b> — an electron is removed from the atom entirely. It requires at least the ionisation energy.</li>
</ul>
<p>When an electron falls from a higher level to a lower one, it emits a photon carrying exactly the energy difference:</p>
<div class="formula">hf = E₁ − E₂</div>
<p>Because the levels are discrete, only certain photon energies are possible, so a gas discharge emits sharp bright lines rather than a continuous spread of colours. Conversely, a gas absorbs photons at exactly those same energies, which produces dark lines in a continuous spectrum.</p>
<div class="callout callout--key"><p><b>The exam point.</b> Line spectra are <i>evidence</i> for discrete energy levels. A question phrased as "what does the existence of line spectra tell us" wants that sentence, not a calculation. A question phrased as "what is the wavelength of the photon emitted in the transition from −3.4 eV to −13.6 eV" wants the energy difference, then <code>λ = hc/ΔE</code>.</p></div>
<div class="callout callout--warn"><p><b>Watch the signs.</b> Energy levels are usually quoted as negative numbers, measured from the zero of an electron at rest infinitely far away. The energy <i>released</i> when falling from −3.4 eV to −13.6 eV is <code>(−3.4) − (−13.6) = 10.2 eV</code>. Do not get this the wrong way round; the emitted photon has positive energy.</p></div>
<h3>A worked transition</h3>
<p>In hydrogen the levels are roughly <code>E₁ = −13.6 eV, E₂ = −3.4 eV, E₃ = −1.51 eV</code>, approaching 0 from below as <code>n</code> grows. An electron falling from <code>n = 3</code> to <code>n = 2</code> releases</p>
<div class="formula">ΔE = E₃ − E₂ = (−1.51) − (−3.4) = 1.89 eV</div>
<p>and the photon wavelength is <code>λ = hc/ΔE = 1240 eV·nm / 1.89 eV ≈ 656 nm</code> — the red line of the Balmer series. Going all the way from a free electron (<code>n = ∞</code>, energy 0) to <code>n = 1</code> releases 13.6 eV, which is the ionisation energy of hydrogen.</p>
<div class="callout callout--key"><p><b>Bigger drop, bluer light.</b> Transitions ending at the ground state (<code>n = 1</code>) release the most energy and give the shortest wavelengths (the Lyman series, ultraviolet). Transitions ending at <code>n = 2</code> give the visible Balmer series. The pattern — larger energy gap, shorter wavelength — is what you need for the qualitative questions.</p></div>`
    },

    {
      h: "Wave–particle duality and de Broglie",
      body: `<p>Light behaves as a wave in interference experiments and as a particle in the photoelectric effect. De Broglie proposed that matter does the same, with a wavelength given by</p>
<div class="formula">λ = h/mv</div>
<p>where <code>mv</code> is the momentum of the particle. Electron diffraction through a thin crystal confirms this: electrons produce interference patterns, so they must have a wavelength, and the measured wavelength matches <code>h/mv</code>.</p>
<h3>Why you do not see this with a cricket ball</h3>
<p>For a mass of 0.16 kg moving at 30 m s⁻¹, the momentum is about 5 kg m s⁻¹, giving</p>
<div class="formula">λ ≈ 6.6 × 10⁻³⁴ / 5 ≈ 1.3 × 10⁻³⁴ m</div>
<p>That is some twenty orders of magnitude smaller than an atomic nucleus. No obstacle is fine enough to diffract it, so the wave behaviour is completely unobservable. For an electron accelerated through 100 V the wavelength is about 0.12 nm, comparable to atomic spacing — which is why crystals work as diffraction gratings for electrons.</p>
<div class="callout callout--key"><p><b>The duality statement worth memorising.</b> Light and matter each exhibit both wave and particle behaviour; which one you observe depends on the experiment. Interference and diffraction reveal the wave nature; the photoelectric effect and the discrete energy transfers reveal the particle nature.</p></div>
<div class="callout callout--warn"><p><b>Do not mix up the two wavelengths.</b> A photon's wavelength comes from <code>λ = c/f = hc/E</code> (it travels at speed <code>c</code>). A matter particle's wavelength comes from <code>λ = h/mv</code> (it has rest mass). Both reduce to "momentum = h/λ", but you obtain the momentum differently: <code>p = E/c</code> for a photon, <code>p = mv</code> for an electron. Questions test exactly this distinction, so decide which particle you are dealing with before writing a formula.</p></div>`
    },

    {
      h: "The electron-volt",
      body: `<p>The electron volt (eV, 电子伏特) is not a different kind of energy — it is a unit of energy, chosen because atomic and photon energies are tiny in joules. By definition, <b>one electron volt is the energy gained by a single electron accelerated through a potential difference of 1 volt</b>:</p>
<div class="formula">1 eV = e × 1 V = 1.60 × 10⁻¹⁹ J</div>
<p>So an electron accelerated through 5 V gains 5 eV = <code>8.0 × 10⁻¹⁹ J</code>. The convenience is that in this topic almost every energy — photon energies, work functions, kinetic energies of photoelectrons — comes out as a small number of eV, and the stopping potential in volts is numerically the kinetic energy in eV.</p>
<h3>Converting both ways</h3>
<ul class="tight">
<li><b>J → eV:</b> divide by <code>1.6 × 10⁻¹⁹</code>. So <code>3.2 × 10⁻¹⁹ J = 2 eV</code>.</li>
<li><b>eV → J:</b> multiply by <code>1.6 × 10⁻¹⁹</code>. So <code>2.5 eV = 4.0 × 10⁻¹⁹ J</code>.</li>
</ul>
<p>For photon energies, the 1240 eV·nm rule folds the conversion in: <code>E(eV) = 1240/λ(nm)</code>. For wavelength, <code>λ(nm) = 1240/E(eV)</code>.</p>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> The electron volt is an energy, not a voltage. Writing "the kinetic energy is 2 V" is wrong; it is 2 eV. Only the stopping potential is measured in volts, and it equals the kinetic energy in eV numerically — but they are different quantities with different units. Keep the distinction in your head even when the numbers match.</p></div>`
    },

    {
      h: "Photon momentum",
      body: `<p>A photon has no mass, yet it carries momentum. Combining <code>E = pc</code> (the energy–momentum relation for a massless particle) with <code>E = hf = hc/λ</code> gives</p>
<div class="formula">p = E/c = hf/c = h/λ</div>
<p>So a photon's momentum is <code>h/λ</code> — inversely proportional to its wavelength. A shorter-wavelength (bluer, higher-energy) photon carries more momentum. This is the particle side of light made quantitative: when light reflects off a surface it pushes on it, and the pressure it exerts is the rate of momentum transfer.</p>
<h3>Why this matters</h3>
<p>Photon momentum explains the <b>radiation pressure</b> (辐射压) that makes comet tails point away from the Sun and that is proposed for solar sails. It also appears in the Compton effect, where a photon bounces off an electron and loses energy — concrete proof that photons carry momentum, not just energy.</p>
<div class="callout callout--key"><p><b>Comparing a photon to an electron.</b> Both obey <code>p = h/λ</code>, but the momentum is found differently. For a photon, <code>p = E/c</code>. For an electron of speed <code>v</code>, <code>p = mv</code> (non-relativistic). A 500 nm photon has momentum <code>6.6 × 10⁻³⁴ / 5 × 10⁻⁷ ≈ 1.3 × 10⁻²⁷ kg m s⁻¹</code> — tiny, which is why light pressure is only noticeable at astronomical scales.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>Light of wavelength 400 nm falls on a metal of work function 2.0 eV. What is the maximum kinetic energy of the emitted electrons? Use <code>hc = 2.0 × 10⁻²⁵ J m</code>.</p><p>A) 1.1 eV &nbsp; B) 1.5 eV &nbsp; C) 3.1 eV &nbsp; D) 5.1 eV &nbsp; E) 0.8 eV</p>",
      sol: `<p><b>Photon energy.</b> Use the memorised combination <code>hc = 2.0 × 10⁻²⁵ J m</code>:</p>
<div class="formula">E = hc/λ = 2.0 × 10⁻²⁵ / 400 × 10⁻⁹ = 5.0 × 10⁻¹⁹ J</div>
<p><b>Convert to eV.</b> Divide by <code>1.6 × 10⁻¹⁹</code>:</p>
<div class="formula">E = 5.0 × 10⁻¹⁹ / 1.6 × 10⁻¹⁹ = 3.1 eV</div>
<p><b>Subtract the work function.</b></p>
<div class="formula">E_k(max) = 3.1 − 2.0 = 1.1 eV</div>
<p><b>Answer: A.</b></p>
<p><b>Note what the numbers were designed to do.</b> <code>5.0/1.6 = 3.125</code> is close enough to 3.1 for a multiple-choice answer, and the subtraction is easy. This is a paper written for mental arithmetic — the numbers are always chosen to cancel or to be round.</p>
<p><b>The trap.</b> Option C is the photon energy before subtracting the work function. Option D comes from <i>adding</i> instead of subtracting. Read the question: it asks for the kinetic energy, not the total energy delivered.</p>`,
      tag: "Photoelectric equation — the core calculation"
    },
    {
      q: "<p>The intensity of monochromatic light striking a metal surface is doubled, with the frequency unchanged and above the threshold. What happens?</p><p>A) The maximum kinetic energy of the electrons doubles &nbsp; B) The maximum kinetic energy is unchanged and the number of electrons per second doubles &nbsp; C) Both double &nbsp; D) Neither changes &nbsp; E) The threshold frequency doubles</p>",
      sol: `<p>Intensity is the number of photons arriving per second. Doubling it doubles the number of photons, so twice as many electrons can be liberated — the photocurrent doubles.</p>
<p>But each electron still absorbs exactly <b>one</b> photon, and the energy of that photon is <code>hf</code>, which has not changed. So the energy available to each electron is unchanged, and therefore the maximum kinetic energy is unchanged.</p>
<p><b>Answer: B.</b></p>
<p><b>Why this is the classic conceptual question.</b> It is the clearest test of whether you have actually understood the photon model or are just manipulating the equation. A wave model predicts that doubling the intensity doubles the energy delivered and therefore should increase the energy of the emitted electrons — it does not, and that failure is the historical reason the photon model was needed.</p>
<p><b>Option E diagnosed.</b> The threshold frequency depends only on the work function of the metal, which is a material property. Nothing about the light source can change it.</p>`,
      tag: "Conceptual — the intensity question"
    },
    {
      q: "<p>A graph of maximum kinetic energy of photoelectrons against the frequency of the incident light is plotted for two different metals. The two lines are parallel. What does this tell you?</p><p>A) The two metals have the same work function &nbsp; B) The two metals have the same threshold frequency &nbsp; C) The Planck constant is the same for both, and the work functions differ &nbsp; D) The intensity was the same in both experiments &nbsp; E) The two metals have the same stopping potential</p>",
      sol: `<p>The equation is <code>E_k = hf − φ</code>. Comparing with <code>y = mx + c</code>, the gradient <code>m</code> is <code>h</code> and the intercept <code>c</code> is <code>−φ</code>.</p>
<p>Parallel lines have the same gradient. So both metals give the same <code>h</code> — which is reassuring, since <code>h</code> is a constant of nature — while the different intercepts mean different work functions.</p>
<p><b>Answer: C.</b></p>
<p><b>Why the others fail.</b> If the work functions were the same, the lines would coincide rather than be parallel. Same threshold frequency would also mean coincident lines, since <code>f₀ = φ/h</code>. Option D is irrelevant: intensity affects the <i>number</i> of electrons and never appears in this equation. Option E is wrong because the stopping potential is <code>E_k(max)/e</code>, which varies with frequency and differs between the two metals.</p>
<p><b>The reading skill.</b> Whenever a question shows a graph, identify the gradient and the intercept in terms of physical quantities before looking at the options. Here that step alone identifies the answer.</p>`,
      tag: "Graph interpretation — gradient and intercept"
    },
    {
      q: "<p>An electron is accelerated from rest through a potential difference of 200 V. What is its de Broglie wavelength? Use <code>h = 6.6 × 10⁻³⁴ J s</code>, <code>m_e = 9.1 × 10⁻³¹ kg</code>, <code>e = 1.6 × 10⁻¹⁹ C</code>.</p><p>A) 0.087 nm &nbsp; B) 0.87 nm &nbsp; C) 8.7 nm &nbsp; D) 0.017 nm &nbsp; E) 1.7 nm</p>",
      sol: `<p><b>Step 1 — kinetic energy.</b> The electrical work done is <code>eV</code>:</p>
<div class="formula">E_k = 1.6 × 10⁻¹⁹ × 200 = 3.2 × 10⁻¹⁷ J</div>
<p><b>Step 2 — momentum.</b> From <code>E_k = p²/2m</code>, we get <code>p = √(2mE_k)</code>:</p>
<div class="formula">p = √(2 × 9.1 × 10⁻³¹ × 3.2 × 10⁻¹⁷)
  = √(5.8 × 10⁻⁴⁷)
  ≈ 7.6 × 10⁻²⁴ kg m s⁻¹</div>
<p><b>Step 3 — de Broglie wavelength.</b></p>
<div class="formula">λ = h/p = 6.6 × 10⁻³⁴ / 7.6 × 10⁻²⁴ ≈ 8.7 × 10⁻¹¹ m = 0.087 nm</div>
<p><b>Answer: A.</b></p>
<p><b>The estimate route, without a calculator.</b> Note that <code>2mE_k ≈ 2 × 9 × 3.2 × 10⁻⁴⁸ = 58 × 10⁻⁴⁸</code>, and <code>√58 ≈ 7.6</code>. Then <code>6.6/7.6 ≈ 0.87</code>, and the powers give <code>10⁻³⁴/10⁻²³ = 10⁻¹¹</code>. So <code>0.87 × 10⁻¹⁰ = 0.087 nm</code>.</p>
<p><b>The physical check.</b> 0.087 nm is comparable to atomic spacing, which is why 200 V electrons diffract from crystals and 20 000 V electrons do not (they are too fast, so their wavelength is too short). Any answer of order nanometres or larger is physically wrong for this accelerating voltage — that alone kills options B, C and E.</p>`,
      tag: "de Broglie — with the no-calculator route"
    },

    {
      q: "<p>The work function of a metal is 2.0 eV. What is the longest wavelength of light that can still eject photoelectrons from it?</p><p>A) 310 nm &nbsp; B) 496 nm &nbsp; C) 620 nm &nbsp; D) 1240 nm &nbsp; E) 2480 nm</p>",
      sol: `<p>The threshold condition is <code>hf₀ = φ</code>, or in wavelength form <code>λ_max = hc/φ</code>. Using the 1240 eV·nm rule with <code>φ = 2.0 eV</code>:</p>
<div class="formula">λ_max = 1240 / 2.0 = 620 nm</div>
<p><b>Answer: C, 620 nm.</b></p>
<p><b>The trap.</b> Option B, 496 nm, is <code>1240/2.5</code> — it comes from using a work function of 2.5 eV. If you misread the number, you land here. Option D, 1240 nm, is <code>1240/1.0</code>, i.e. using φ = 1.0 eV. Option A is half of the right answer, and option E is double — both are ordering slips. The 1240 rule removes the unit conversion, so the only arithmetic is a single division; check you divided by the right φ.</p>
<p><b>The physics.</b> Light of wavelength longer than 620 nm (redder, lower energy) cannot free an electron no matter how bright it is. This is exactly why red light often fails to cause the photoelectric effect while violet does.</p>`,
      tag: "Threshold wavelength from the work function"
    },

    {
      q: "<p>Light of wavelength 300 nm shines on a metal of work function 2.0 eV. What stopping potential is needed to reduce the photocurrent to zero?</p><p>A) 1.1 V &nbsp; B) 2.1 V &nbsp; C) 4.1 V &nbsp; D) 6.1 V &nbsp; E) 2.0 V</p>",
      sol: `<p><b>Photon energy</b> (1240 eV·nm rule):</p>
<div class="formula">E = 1240 / 300 ≈ 4.13 eV</div>
<p><b>Maximum kinetic energy</b> of the photoelectrons:</p>
<div class="formula">E_k(max) = 4.13 − 2.0 = 2.13 eV</div>
<p>The stopping potential in volts is numerically the kinetic energy in eV, so <code>V_s ≈ 2.1 V</code>.</p>
<p><b>Answer: B, 2.1 V.</b></p>
<p><b>The trap.</b> Option C, 4.1 V, is the photon energy before subtracting the work function — the classic "forgot to subtract φ" slip. Option E, 2.0 V, is the work function itself masquerading as an answer. Both are there deliberately. You must subtract <code>φ</code> from <code>hf</code>, never add it and never drop it.</p>
<p><b>Sanity check.</b> 300 nm is ultraviolet, well above threshold (620 nm), so emission occurs and the stopping potential is positive — consistent with a real answer around 2 V.</p>`,
      tag: "Stopping potential — full calculation"
    },

    {
      q: "<p>What is the momentum of a photon of wavelength 600 nm? Use <code>h = 6.6 × 10⁻³⁴ J s</code>.</p><p>A) 1.1 × 10⁻²⁷ kg m s⁻¹ &nbsp; B) 1.1 × 10⁻²⁶ kg m s⁻¹ &nbsp; C) 1.1 × 10⁻²⁸ kg m s⁻¹ &nbsp; D) 3.3 × 10⁻²⁷ kg m s⁻¹ &nbsp; E) 1.1 × 10⁻²⁵ kg m s⁻¹</p>",
      sol: `<p>Convert the wavelength to metres: <code>600 nm = 6.0 × 10⁻⁷ m</code>. Then</p>
<div class="formula">p = h/λ = 6.6 × 10⁻³⁴ / (6.0 × 10⁻⁷) = 1.1 × 10⁻²⁷ kg m s⁻¹</div>
<p><b>Answer: A.</b></p>
<p><b>Why the others are powers of ten off.</b> This is an estimation question in disguise: the options differ by factors of ten, so the test is whether you converted nm → m correctly and kept the exponent straight. Forget the ×10⁻⁹ and you are off by 10⁹; slip the exponent by one place and you land on B, C or E. Option D, <code>3.3 × 10⁻²⁷</code>, is the momentum of a 200 nm photon, a different wavelength entirely.</p>
<p><b>The physical point.</b> Photon momentum is genuinely tiny — about 10⁻²⁷ kg m s⁻¹ — which is why you never feel the pressure of ordinary light, but it adds up for a whole star bearing on a comet tail.</p>`,
      tag: "Photon momentum — watch the powers of ten"
    },

    {
      q: "<p>An electron in a hydrogen atom falls from the n = 2 level (energy −3.4 eV) to the n = 1 level (energy −13.6 eV). What is the wavelength of the emitted photon?</p><p>A) 122 nm &nbsp; B) 656 nm &nbsp; C) 365 nm &nbsp; D) 103 nm &nbsp; E) 91 nm</p>",
      sol: `<p>The energy released is the positive difference between the levels:</p>
<div class="formula">ΔE = E₂ − E₁ = (−3.4) − (−13.6) = 10.2 eV</div>
<p>Now use the 1240 eV·nm rule in reverse:</p>
<div class="formula">λ = 1240 / 10.2 ≈ 121.6 nm ≈ 122 nm</div>
<p><b>Answer: A, 122 nm.</b></p>
<p><b>Why the other options are real spectral lines.</b> Option B, 656 nm, is the red Balmer line from <code>n = 3 → 2</code> — a different transition entirely. Option C, 365 nm, is the Balmer limit (<code>n = ∞ → 2</code>). Option E, 91 nm, is the Lyman limit (<code>n = ∞ → 1</code>), the shortest possible Lyman wavelength. So these are not random numbers; each is a genuine hydrogen wavelength, and the question is really testing whether you picked the right pair of levels.</p>
<p><b>The sign check.</b> Always subtract the lower (more negative) level from the higher one: <code>(−3.4) − (−13.6) = +10.2 eV</code>. If you reverse it you get −10.2 eV, a negative photon energy, which is impossible.</p>`,
      tag: "Line spectrum — energy difference to wavelength"
    }
  ],

  traps: [
    "Thinking intensity affects the maximum kinetic energy. It affects the number of electrons only.",
    "Thinking the threshold frequency depends on the light source. It is a property of the metal.",
    "Adding the work function instead of subtracting it. <code>E_k = hf − φ</code>.",
    "Sign errors in energy-level transitions. Levels are negative; the emitted photon energy is the positive difference.",
    "Forgetting to convert joules to electron volts, or the reverse. Divide by <code>1.6 × 10⁻¹⁹</code> to go from J to eV.",
    "Confusing ionisation with excitation. Ionisation removes the electron; excitation raises it within the atom.",
    "Using <code>E = ½mv²</code> when the question gives momentum or wavelength — go through <code>p = h/λ</code> instead."
  ],

  checklist: [
    { id: "L1", flag: "CORE", text: "Photon model: <code>E = hf = hc/λ</code>, and the memorised combination <code>hc ≈ 2.0 × 10⁻²⁵ J m</code>." },
    { id: "L2", flag: "CORE", text: "The photoelectric effect: threshold frequency, work function, stopping potential, and the four features that classical theory cannot explain." },
    { id: "L3", flag: "CORE", text: "<code>hf = φ + E_k(max)</code> and the graph of <code>E_k</code> against <code>f</code>, with gradient <code>h</code> and intercept <code>−φ</code>." },
    { id: "L4", flag: "CORE", text: "Why intensity cannot change the maximum kinetic energy but frequency can. Be able to say it in one sentence." },
    { id: "L5", flag: "CORE", text: "Ionisation and excitation; the electron volt; converting eV to joules and back." },
    { id: "L6", flag: "NEW", text: "Line spectra as evidence for discrete energy levels; <code>hf = E₁ − E₂</code>; emission versus absorption spectra." },
    { id: "L7", flag: "NEW", text: "Wave–particle duality; de Broglie <code>λ = h/mv</code>; electron diffraction; why the effect is unobservable for macroscopic objects." },
    { id: "L8", flag: "R1-ONLY", text: "Annihilation and pair production, and the energies involved. Round 1 material — insurance only." },
    { id: "L9", flag: "SKIP", text: "Quark composition, hadron and lepton classification, strangeness, exchange particles. This is the particle physics that BPhO explicitly excludes." }
  ]
},

{
  code: "M",
  title: "Fluids and pressure",
  short: "Fluids",
  priority: 2,
  tier: "Tier A — inside AQA AS §3.4, and tested by the sample paper",
  why: "Short, concrete, and heavily revision for you: buoyancy and pressure are covered thoroughly in Chinese 初中物理. The competition-style twist is the combination of Archimedes' principle with moments and with apparent weight, which is where the marks are actually decided.",
  warn: null,

  sections: [
    {
      h: "Pressure",
      body: `<p>Pressure is force per unit area:</p>
<div class="formula">p = F/A</div>
<p>measured in pascals, where <code>1 Pa = 1 N m⁻²</code>. In base units, <code>kg m⁻¹ s⁻²</code>.</p>
<p>The reason a knife cuts and a drawing pin works is that a small area concentrates a given force into a high pressure. That is the whole content of the concept at this level.</p>
<h3>Pressure with depth</h3>
<p>Consider a column of fluid of height <code>h</code> and cross-sectional area <code>A</code>. Its volume is <code>Ah</code>, so its mass is <code>ρAh</code> and its weight is <code>ρAhg</code>. The pressure it exerts at the base is that weight divided by the area:</p>
<div class="formula">p = ρAhg / A = ρgh</div>
<p>Note what cancelled: the area. This is the derivation, and it is worth being able to reproduce, because it shows that</p>
<div class="callout callout--key"><p><b>The pressure at depth depends only on the depth and the density — not on the shape or width of the container.</b> A narrow tube and a wide lake, both 1 m deep, have exactly the same pressure at the bottom. This counter-intuitive result is a favourite competition question.</p></div>
<div class="callout callout--good"><p><b>Magnitude anchor.</b> Atmospheric pressure is about <code>1.0 × 10⁵ Pa</code> — roughly the weight of the whole atmosphere, or equivalently the pressure at the bottom of 10 m of water (<code>ρgh = 1000 × 10 × 10 = 10⁵ Pa</code>). So every 10 m of water adds one extra atmosphere of pressure. This is why a water barometer would need to be about 10 m tall, while a mercury barometer (13.6× denser) needs only 760 mm.</p></div>
<p>The total pressure at depth in a liquid open to the atmosphere is <code>p_total = p_atmospheric + ρgh</code>, because the atmosphere is pressing down on the surface too. Unless a question says otherwise, <code>p_atmospheric</code> is about <code>1.0 × 10⁵ Pa</code>.</p>`
    },

    {
      h: "Archimedes' principle",
      body: `<p>Any body immersed in a fluid experiences an upward force called upthrust, equal to the weight of fluid it displaces:</p>
<div class="formula">upthrust = ρ_fluid × V_displaced × g</div>
<h3>Where it comes from</h3>
<p>Pressure increases with depth, so the bottom of a submerged object is pressed upward harder than the top is pressed downward. The difference is the upthrust. This is why the force depends on the volume of the object rather than on its mass or its material — only the volume determines how much fluid is pushed out of the way.</p>
<div class="callout callout--warn"><p><b>Density in the formula is the fluid's, not the object's.</b> This is the single most common error in this module. A steel block and a wooden block of the same volume, fully submerged, experience exactly the same upthrust, even though the steel is far heavier.</p></div>
<div class="callout callout--good"><p><b>Maximum upthrust = weight of the whole object's volume of fluid.</b> A fully submerged object displaces its entire volume, so its upthrust is the largest it can ever experience. A floating object displaces only part of its volume, so its upthrust is smaller — exactly equal to its weight. If you are asked "what is the upthrust on this object", first ask whether it is fully submerged or floating; the displaced volume is different in the two cases, and using the full volume for a floating object overcounts.</p></div>
<h3>Floating and sinking</h3>
<table><thead><tr><th>Situation</th><th>Comparison</th><th>Result</th></tr></thead><tbody>
<tr><td>Object sinks to the bottom</td><td><code>ρ_object &gt; ρ_fluid</code></td><td>weight exceeds the maximum possible upthrust</td></tr>
<tr><td>Object floats in equilibrium</td><td><code>ρ_object &lt; ρ_fluid</code></td><td>partially submerged; upthrust equals weight</td></tr>
<tr><td>Object hovers, fully submerged</td><td><code>ρ_object = ρ_fluid</code></td><td>neutrally buoyant</td></tr>
</tbody></table>
<p>For a floating object, the fraction submerged follows immediately from the equilibrium condition:</p>
<div class="formula">ρ_object V g = ρ_fluid V_submerged g   →   V_submerged / V = ρ_object / ρ_fluid</div>
<p>So an ice cube of density 917 kg m⁻³ floats in water with about 92% of its volume below the surface. This fraction result is used constantly.</p>`
    },

    {
      h: "Apparent weight and finding density by weighing in water",
      body: `<p>A body weighed while immersed appears lighter, because the scale reading is the true weight minus the upthrust:</p>
<div class="formula">apparent weight = true weight − upthrust</div>
<p>This gives a very neat method for finding the density of an irregular solid, and the reasoning is worth following because it is a standard question shape.</p>
<ol class="steps">
<li>Weigh the object in air: <code>W = mg = ρ_object V g</code>.</li>
<li>Weigh it fully immersed in water: <code>W' = W − ρ_water V g</code>.</li>
<li>The <b>difference</b> is the upthrust, which gives the volume: <code>W − W' = ρ_water V g</code>, so <code>V = (W − W')/(ρ_water g)</code>.</li>
<li>Divide the true weight by the upthrust and the <code>g</code> cancels:</li>
</ol>
<div class="formula">ρ_object / ρ_water = W / (W − W')</div>
<p>So the ratio of the two weighings gives the relative density directly, with no need to know the volume at all.</p>
<div class="callout callout--good"><p><b>Worked in numbers.</b> An object weighs 5.0 N in air and 3.0 N in water. Then <code>ρ_object/ρ_water = 5.0/(5.0 − 3.0) = 2.5</code>, so the density is <code>2500 kg m⁻³</code> — the right order for a rock or a piece of glass. If it weighed 0 N in water it would be neutrally buoyant, and the formula would diverge, which correctly signals that the object is not fully submerged.</p></div>
<div class="callout callout--warn"><p><b>What if the object is denser than water?</b> Then it sinks, and when resting on the bottom the support reads its full weight, because although an upthrust acts, it is smaller than the weight. The weighing-in-water method above assumes the object is fully submerged but still suspended (not resting on the bottom), so the upthrust is genuinely subtracted from the reading. If the object touches the bottom, the normal force from the bottom also helps support it and the simple <code>W − W'</code> formula no longer gives the upthrust.</p></div>`
    },

    {
      h: "Fluids combined with moments",
      body: `<p>The competition-style version of this module is a problem where a floating object is loaded off-centre, or a submerged object is suspended from a beam. Then you need Archimedes' principle <i>and</i> moments together, and the trick is always the same: <b>decide whether you are treating the object as a whole or taking moments about a point</b>, and do not mix the two.</p>
<h3>The standard structure</h3>
<ol class="steps">
<li><b>Resolve vertically first</b> to find the upthrust. If the object floats, upthrust equals total weight.</li>
<li><b>Find the centre of buoyancy</b> — the centre of mass of the displaced fluid, which is the centroid of the submerged volume.</li>
<li><b>Take moments about a chosen point.</b> Usually the pivot or the edge, because that eliminates an unknown contact force.</li>
<li><b>Check the limit.</b> If the added mass grows, at what point does the object tip or sink? Setting the restoring moment to zero gives the condition.</li>
</ol>
<div class="callout callout--key"><p><b>Why the tipping condition matters.</b> A floating body tips when its centre of mass passes beyond the centre of buoyancy. That is why a boat loaded too far to one side capsizes, and it is exactly the kind of physical reasoning a competition question rewards.</p></div>
<div class="callout callout--warn"><p><b>Common slip.</b> When taking moments, use the <i>true</i> weight of the object, not its apparent weight, for the gravitational moment — the upthrust is a separate force acting at the centre of buoyancy. Students often subtract the upthrust from the weight and then also apply an upthrust force, double-counting. Keep the two forces separate: weight down at the centre of mass, upthrust up at the centre of buoyancy.</p></div>`
    },

    {
      h: "Atmospheric and gauge pressure",
      body: `<p>Pressure is quoted in two ways, and the distinction is tested.</p>
<ul class="tight">
<li><b>Absolute pressure</b> (绝对压强) is the true pressure, including the atmosphere pressing down from above: <code>p_abs = p_atm + ρgh</code> for a point at depth <code>h</code> in a liquid open to the air.</li>
<li><b>Gauge pressure</b> (表压) is the pressure <i>above</i> atmospheric — what a pressure gauge actually reads, because the gauge itself is surrounded by air: <code>p_gauge = ρgh</code>.</li>
</ul>
<p>So gauge pressure at depth is just <code>ρgh</code>; absolute pressure adds the ~<code>10⁵ Pa</code> of the atmosphere. Tyre pressure is quoted as gauge pressure (the excess over atmospheric), while a diver must compare their lung pressure to the absolute pressure of the surrounding water.</p>
<div class="callout callout--key"><p><b>Always check which one the question wants.</b> "Pressure at 10 m depth" without qualification usually means absolute, so add <code>10⁵ Pa</code>. "Extra pressure due to the water" means gauge, so just <code>ρgh</code>. Getting these swapped is a routine way to be off by exactly one atmosphere — about <code>10⁵ Pa</code> — which is far larger than any rounding error.</p></div>
<h3>Worked</h3>
<p>At 10 m below the surface of water, gauge pressure is <code>ρgh = 1000 × 10 × 10 = 10⁵ Pa</code>, i.e. one atmosphere. Absolute pressure is <code>10⁵ + 10⁵ = 2 × 10⁵ Pa</code>, or two atmospheres. Every further 10 m adds another atmosphere.</p>`
    },

    {
      h: "Hydraulic systems and Pascal's principle",
      body: `<p>Pascal's principle (帕斯卡原理): a pressure change applied to an enclosed fluid is transmitted undiminished to every part of the fluid and to the walls of its container. This is the basis of the hydraulic press (液压机).</p>
<p>Suppose a force <code>F₁</code> is applied to a small piston of area <code>A₁</code>, producing pressure <code>p = F₁/A₁</code>. That same pressure acts on a large piston of area <code>A₂</code>, producing an output force <code>F₂ = p A₂ = F₁ (A₂/A₁)</code>. So</p>
<div class="formula">F₁/A₁ = F₂/A₂   →   F₂ = F₁ × A₂/A₁</div>
<p>The force is multiplied by the area ratio. Because the fluid is (nearly) incompressible, the small piston moves a large distance while the large piston moves a small distance, and the work in equals the work out: <code>F₁ d₁ = F₂ d₂</code> (you trade distance for force, exactly like a lever).</p>
<div class="callout callout--warn"><p><b>How to get this wrong.</b> The pressure is the same on both pistons, not the force. Students sometimes write <code>F₁ = F₂</code> — that would be true only if the areas were equal. The force scales with area; the pressure does not. Also, a hydraulic system is not a way to get free energy, only a way to trade force for distance, so the work is conserved.</p></div>`
    },

    {
      h: "Viscosity, drag and terminal speed (qualitative)",
      body: `<p>Viscosity (粘度) is a fluid's internal resistance to flow — thick honey has high viscosity, water has low. It is the fluid analogue of friction. When an object moves through a viscous fluid it experiences a drag force opposing its motion; for a small sphere moving slowly the drag is <code>F_drag = 6πηrv</code> (Stokes' law, 斯托克斯定律), proportional to the speed <code>v</code>, the radius <code>r</code> and the viscosity <code>η</code>.</p>
<p>Because the drag grows with speed, a falling object does not accelerate forever. It reaches a <b>terminal speed</b> when the drag plus upthrust balance its weight, so the net force is zero and it falls at constant speed thereafter. This is the same idea as terminal velocity in air, only the drag law is different.</p>
<div class="callout callout--key"><p><b>Round 0 scope.</b> Treat viscosity qualitatively: drag increases with speed; there is a terminal speed where forces balance; a more viscous fluid (or a larger, faster object) gives greater drag and a lower terminal speed. Bernoulli's equation and its full derivation are <b>beyond Round 0</b> — do not reach for it. The competition question will ask about direction and limiting behaviour, not a Stokes'-law calculation.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A block of wood of density 600 kg m⁻³ floats in water of density 1000 kg m⁻³. What fraction of its volume is above the water surface?</p><p>A) 20% &nbsp; B) 40% &nbsp; C) 60% &nbsp; D) 67% &nbsp; E) 80%</p>",
      sol: `<p>For a floating object, upthrust equals weight. Let the total volume be <code>V</code> and the submerged volume be <code>V_s</code>:</p>
<div class="formula">ρ_water V_s g = ρ_wood V g
V_s / V = ρ_wood / ρ_water = 600/1000 = 0.6</div>
<p>So 60% is submerged, which means <b>40% is above the surface</b>.</p>
<p><b>Answer: B.</b></p>
<p><b>The trap.</b> Option C, 60%, is the submerged fraction, which is the number you calculate first. The question asks for the fraction <i>above</i> the water. This kind of inversion is one of the most common ways to lose a mark on a question you actually understood.</p>
<p><b>The sanity check.</b> The wood is less dense than water, so it should float with more than half submerged but not by much — 60/40 is right for a density ratio of 0.6. If your answer had the block floating with only a sliver submerged, the density ratio would have to be much smaller.</p>`,
      tag: "Floating fraction — and reading what is asked"
    },
    {
      q: "<p>An object weighs 12 N in air. When fully immersed in water it weighs 9 N. When fully immersed in an unknown liquid it weighs 8 N. What is the density of the unknown liquid?</p><p>A) 750 kg m⁻³ &nbsp; B) 1000 kg m⁻³ &nbsp; C) 1250 kg m⁻³ &nbsp; D) 1333 kg m⁻³ &nbsp; E) 1500 kg m⁻³</p>",
      sol: `<p><b>In water.</b> The upthrust is <code>12 − 9 = 3 N</code>. Since upthrust is <code>ρ_fluid V g</code>, this tells us <code>ρ_water V g = 3 N</code>.</p>
<p><b>In the unknown liquid.</b> The upthrust is <code>12 − 8 = 4 N</code>, so <code>ρ_liquid V g = 4 N</code>.</p>
<p><b>Divide one by the other.</b> The volume <code>V</code> and <code>g</code> are the same in both cases, so they cancel:</p>
<div class="formula">ρ_liquid / ρ_water = 4/3   →   ρ_liquid = (4/3) × 1000 = 1333 kg m⁻³</div>
<p><b>Answer: D.</b></p>
<p><b>Why this is a ratio question.</b> Note that you never needed the volume, and you never needed <code>g</code>. The two weighings give the ratio of the densities directly. If you started by computing <code>V</code> from <code>3 = 1000 × V × 9.81</code>, you took the long route and probably ran out of time.</p>
<p><b>The physical check.</b> The unknown liquid gives a bigger upthrust for the same volume, so it must be denser than water. That eliminates options A and B immediately, before any calculation.</p>`,
      tag: "Apparent weight — solved as a ratio"
    },
    {
      q: "<p>A rectangular block floats in water with 80% of its volume submerged. It is then placed in a liquid of density 1600 kg m⁻³. What fraction of its volume is now submerged?</p><p>A) 40% &nbsp; B) 50% &nbsp; C) 64% &nbsp; D) 80% &nbsp; E) 125%</p>",
      sol: `<p><b>Step 1 — find the density of the block.</b> From the water case, the submerged fraction equals the density ratio:</p>
<div class="formula">ρ_block / ρ_water = 0.80   →   ρ_block = 800 kg m⁻³</div>
<p><b>Step 2 — apply it to the new liquid.</b> The submerged fraction in any fluid is the ratio of the block's density to that fluid's density:</p>
<div class="formula">V_s/V = ρ_block / ρ_liquid = 800/1600 = 0.50</div>
<p><b>Answer: B, 50%.</b></p>
<p><b>Why the answer cannot be E.</b> A fraction submerged can never exceed 1 — if the block's density were greater than the liquid's, it would sink rather than float, and "fraction submerged" would stop being the right description. Option E at 125% is physically impossible, and recognising that instantly removes it.</p>
<p><b>The general principle.</b> Doubling the fluid density halves the submerged fraction. That inverse relationship is worth holding onto: a denser fluid supports the same weight with less displaced volume, so less of the object needs to be under the surface.</p>`,
      tag: "Floating fraction — chained ratio"
    },
    {
      q: "<p>Two identical buckets are filled to the same depth: one with water, one with mercury of density 13 600 kg m⁻³. Both are cylindrical and identical in size. Which exerts the greater pressure on the base of its bucket?</p><p>A) Water &nbsp; B) Mercury &nbsp; C) They are equal &nbsp; D) Depends on the total mass of liquid &nbsp; E) Depends on the shape of the base</p>",
      sol: `<p>Use <code>p = ρgh</code>. The depth <code>h</code> is the same and <code>g</code> is the same, so the pressure is proportional to density. Mercury is about 13.6 times denser, so it exerts about 13.6 times the pressure.</p>
<p><b>Answer: B.</b></p>
<p><b>Why not C.</b> The tempting error is to think "same depth, so same pressure", which would be true if both liquids had the same density. It is the density that makes the difference, and mercury's is extreme — the same reason a mercury barometer is only 760 mm tall while a water barometer would need to be about 10 m.</p>
<p><b>Why not D or E.</b> The derivation <code>p = ρgh</code> showed that the cross-sectional area cancelled. So the total mass of liquid and the shape of the base are both irrelevant to the pressure at depth — only depth and density matter. This is the counter-intuitive result worth internalising.</p>
<p><b>A note on the distinction.</b> The pressure depends only on <code>ρgh</code>, but the <b>force</b> on the base is pressure times area. If the buckets have the same base area, the mercury bucket also has the greater force. If the base areas differed, the comparison of forces would need that extra factor while the comparison of pressures would not.</p>`,
      tag: "Pressure with depth — what does and does not matter"
    },

    {
      q: "<p>What is the absolute pressure at a depth of 20 m below the surface of water? Take atmospheric pressure as 1.0 × 10⁵ Pa and g = 10 m s⁻².</p><p>A) 2.0 × 10⁵ Pa &nbsp; B) 3.0 × 10⁵ Pa &nbsp; C) 1.0 × 10⁵ Pa &nbsp; D) 4.0 × 10⁵ Pa &nbsp; E) 2.0 × 10⁶ Pa</p>",
      sol: `<p>Gauge pressure from the water column:</p>
<div class="formula">p_gauge = ρgh = 1000 × 10 × 20 = 2.0 × 10⁵ Pa</div>
<p>Absolute pressure adds the atmosphere pressing on the surface:</p>
<div class="formula">p_abs = p_atm + p_gauge = 1.0 × 10⁵ + 2.0 × 10⁵ = 3.0 × 10⁵ Pa</div>
<p><b>Answer: B, 3.0 × 10⁵ Pa</b> (three atmospheres: one from the air, two from the water).</p>
<p><b>The trap.</b> Option A, <code>2.0 × 10⁵ Pa</code>, is the gauge pressure — the water only, with the atmosphere omitted. Option C is the atmosphere alone. The question asks for absolute pressure, so you must add the <code>10⁵ Pa</code> from the air; leaving it off is the single most common error here and it is wrong by a full atmosphere.</p>
<p><b>The physical check.</b> Every 10 m of water is one extra atmosphere, so 20 m of water is two atmospheres on top of the one already present — three in total. If your answer were under <code>10⁵ Pa</code> you would be claiming a point underwater feels less pressure than the surface, which is absurd.</p>`,
      tag: "Absolute versus gauge pressure at depth"
    },

    {
      q: "<p>In a hydraulic press a force of 100 N is applied to a piston of area 0.01 m². The output piston has area 0.10 m². What force does the output piston exert, assuming the fluid is ideal?</p><p>A) 10 N &nbsp; B) 100 N &nbsp; C) 1000 N &nbsp; D) 10 000 N &nbsp; E) 100 000 N</p>",
      sol: `<p>By Pascal's principle the pressure is the same throughout the fluid. The input pressure is</p>
<div class="formula">p = F₁/A₁ = 100 / 0.01 = 10 000 Pa</div>
<p>The output force is this pressure times the larger area:</p>
<div class="formula">F₂ = p A₂ = 10 000 × 0.10 = 1000 N</div>
<p>Equivalently, in one step: <code>F₂ = F₁ × A₂/A₁ = 100 × 0.10/0.01 = 100 × 10 = 1000 N</code>.</p>
<p><b>Answer: C, 1000 N.</b></p>
<p><b>The trap.</b> Option A, 10 N, is the result of inverting the ratio (<code>F₁ × A₁/A₂</code>) — it makes the larger piston produce less force, which violates the whole point of the device. Option B, 100 N, forgets to multiply by the area ratio at all. The force scales with area, so a ten-times larger piston gives a ten-times larger force.</p>
<p><b>The conservation note.</b> The press trades force for distance: the output piston moves only one-tenth as far as the input, so <code>F₁ d₁ = F₂ d₂</code> and no energy is created. If an option suggested 10 000 N you would be claiming ten times the input work for free.</p>`,
      tag: "Hydraulic press — Pascal's principle"
    },

    {
      q: "<p>A metal block of volume 2.0 × 10⁻³ m³ and density 8000 kg m⁻³ is fully submerged in water of density 1000 kg m⁻³ (g = 10 m s⁻²). What is its apparent weight while submerged?</p><p>A) 20 N &nbsp; B) 140 N &nbsp; C) 160 N &nbsp; D) 180 N &nbsp; E) 100 N</p>",
      sol: `<p>True weight of the block:</p>
<div class="formula">W = ρ_obj V g = 8000 × 2.0 × 10⁻³ × 10 = 160 N</div>
<p>Upthrust = weight of displaced water (use the <i>fluid's</i> density, not the block's):</p>
<div class="formula">U = ρ_water V g = 1000 × 2.0 × 10⁻³ × 10 = 20 N</div>
<p>Apparent weight = true weight − upthrust:</p>
<div class="formula">W_apparent = 160 − 20 = 140 N</div>
<p><b>Answer: B, 140 N.</b></p>
<p><b>The trap.</b> Option A, 20 N, is the upthrust alone — the force the water exerts, not the reading on a support. Option C, 160 N, is the true weight in air, ignoring buoyancy entirely. Option D, 180 N, wrongly adds the upthrust to the weight. The support reads the true weight minus the upward buoyant force.</p>
<p><b>The density check.</b> Because the block is eight times denser than water, it sinks, and the upthrust is only one-eighth of its weight — so the apparent weight is <code>7/8</code> of the true weight, i.e. 140 N, consistent with <code>160 × 7/8</code>.</p>`,
      tag: "Upthrust and apparent weight of a submerged block"
    }
  ],

  traps: [
    "Using the density of the object instead of the fluid in the upthrust formula.",
    "Reporting the submerged fraction when the question asks for the fraction above the surface.",
    "Forgetting that upthrust depends on the <i>displaced volume</i>, so a partially submerged object displaces less than its full volume.",
    "Computing the volume when the question only needs a ratio. Two weighings give the density ratio directly.",
    "Assuming pressure at depth depends on the amount of liquid or the shape of the container. Only depth and density matter.",
    "Forgetting to add atmospheric pressure when the question asks for the total pressure at depth in an open liquid.",
    "Assuming a submerged object experiences the same upthrust regardless of how deep it is. For an incompressible fluid, it does — upthrust depends on volume, not depth."
  ],

  checklist: [
    { id: "M1", flag: "CORE", text: "Pressure <code>p = F/A</code>, and pressure with depth <code>p = ρgh</code>, derived from the weight of a fluid column." },
    { id: "M2", flag: "CORE", text: "Archimedes' principle: upthrust equals the weight of fluid displaced, and it depends on volume, not on the object's mass or material." },
    { id: "M3", flag: "CORE", text: "Floating and sinking; the fraction submerged equals the density ratio <code>ρ_object/ρ_fluid</code>." },
    { id: "M4", flag: "CORE", text: "Apparent weight when immersed; finding density by weighing in air and in water; the ratio <code>ρ_object/ρ_water = W/(W − W')</code>." },
    { id: "M5", flag: "R1-ONLY", text: "Layered immiscible liquids; pressure at depth through several layers. Round 1 material — insurance only." },
    { id: "M6", flag: "R1-ONLY", text: "Bodies of non-uniform density in equilibrium, such as a cone with linearly varying density. Round 1 material — insurance only." }
  ]
}

]);
