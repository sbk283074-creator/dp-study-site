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
<p>This is the same structure as the formula for two resistors in parallel. Worth knowing because it is faster than dealing with reciprocals under time pressure.</p>`
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
<h3>Where the energy goes</h3>
<p>When a capacitor charges through a resistor, exactly half the energy supplied by the battery ends up stored in the capacitor, and the other half is dissipated as heat in the resistance. This is true regardless of the size of the resistance, which is a surprising result and a favourite of competition questions. The reason is that the battery supplies <code>QV</code> while the capacitor stores <code>½QV</code>.</p>`
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
<div class="callout callout--good"><p><b>The gradient is <code>h</code> for every metal.</b> That is the point of plotting it: the gradient gives a fundamental constant of nature, while the intercept characterises the particular metal. Questions often give you two metals on one graph and ask which has the larger work function — the answer is whichever line has its horizontal intercept further to the right.</p></div>`
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
</tbody></table>`
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
<div class="callout callout--warn"><p><b>Watch the signs.</b> Energy levels are usually quoted as negative numbers, measured from the zero of an electron at rest infinitely far away. The energy <i>released</i> when falling from −3.4 eV to −13.6 eV is <code>(−3.4) − (−13.6) = 10.2 eV</code>. Do not get this the wrong way round; the emitted photon has positive energy.</p></div>`
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
<div class="callout callout--key"><p><b>The duality statement worth memorising.</b> Light and matter each exhibit both wave and particle behaviour; which one you observe depends on the experiment. Interference and diffraction reveal the wave nature; the photoelectric effect and the discrete energy transfers reveal the particle nature.</p></div>`
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
<p>The total pressure at depth in a liquid open to the atmosphere is <code>p_total = p_atmospheric + ρgh</code>, because the atmosphere is pressing down on the surface too. Unless a question says otherwise, <code>p_atmospheric</code> is about <code>1.0 × 10⁵ Pa</code>.</p>`
    },

    {
      h: "Archimedes' principle",
      body: `<p>Any body immersed in a fluid experiences an upward force called upthrust, equal to the weight of fluid it displaces:</p>
<div class="formula">upthrust = ρ_fluid × V_displaced × g</div>
<h3>Where it comes from</h3>
<p>Pressure increases with depth, so the bottom of a submerged object is pressed upward harder than the top is pressed downward. The difference is the upthrust. This is why the force depends on the volume of the object rather than on its mass or its material — only the volume determines how much fluid is pushed out of the way.</p>
<div class="callout callout--warn"><p><b>Density in the formula is the fluid's, not the object's.</b> This is the single most common error in this module. A steel block and a wooden block of the same volume, fully submerged, experience exactly the same upthrust, even though the steel is far heavier.</p></div>
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
<div class="callout callout--good"><p><b>Worked in numbers.</b> An object weighs 5.0 N in air and 3.0 N in water. Then <code>ρ_object/ρ_water = 5.0/(5.0 − 3.0) = 2.5</code>, so the density is <code>2500 kg m⁻³</code> — the right order for a rock or a piece of glass. If it weighed 0 N in water it would be neutrally buoyant, and the formula would diverge, which correctly signals that the object is not fully submerged.</p></div>`
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
<div class="callout callout--key"><p><b>Why the tipping condition matters.</b> A floating body tips when its centre of mass passes beyond the centre of buoyancy. That is why a boat loaded too far to one side capsizes, and it is exactly the kind of physical reasoning a competition question rewards.</p></div>`
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
