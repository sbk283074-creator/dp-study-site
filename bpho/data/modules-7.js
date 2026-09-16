/* BPhO Round 0 — curriculum, part 6 of 6 (second half).
   Modules K (nuclear), J (thermal), N (insurance — Round 1 material). */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "K",
  title: "Nuclear physics",
  short: "Nuclear",
  priority: 3,
  tier: "Tier A for K1–K6 and K14 (AQA AS §3.2.1.2, plus sample question S1); Tier B for the rest",
  why: "Small and self-contained, with a clear scope boundary: notation, specific charge, decay equations and the properties of the three radiations are in; half-life and exponential decay are out. Sample question S1 tested specific charge, so this module is worth doing properly rather than skimming.",
  warn: "<p><b>Draw the scope line carefully here.</b> BPhO excludes <i>particle physics</i> — quarks, hadrons, strangeness. But nuclear <i>notation</i>, alpha and beta decay, and specific charge are inside AQA AS §3.2.1.2 and therefore inside \"Year 12 topics\". Half-life and exponential decay are Year 13 content and are marked <code>R1-ONLY</code> below.</p>",

  sections: [
    {
      h: "Nuclear notation and isotopes",
      body: `<p>A nucleus is written <code>ᴬ_Z X</code> where:</p>
<ul class="tight">
<li><code>X</code> is the chemical symbol, which fixes the element.</li>
<li><code>Z</code>, the <b>proton number</b> (or atomic number), is the number of protons. It determines the element and the number of electrons in a neutral atom.</li>
<li><code>A</code>, the <b>nucleon number</b> (or mass number), is the total number of protons and neutrons.</li>
<li>The number of neutrons is <code>A − Z</code>.</li>
</ul>
<div class="formula">neutron number = A − Z</div>
<h3>Isotopes</h3>
<p>Isotopes are nuclei with the <b>same <code>Z</code> but different <code>A</code></b> — the same element, different numbers of neutrons. They have identical chemical properties, because chemistry depends on the electron arrangement and therefore on <code>Z</code>, but different nuclear properties such as stability.</p>
<p>For example, carbon-12 and carbon-14 are both <code>Z = 6</code>, with 6 and 8 neutrons respectively. Carbon-14 is radioactive; carbon-12 is stable. That difference in nuclear stability, with no difference in chemistry, is what makes radiocarbon dating possible.</p>
<div class="callout callout--key"><p><b>The notation convention.</b> The superscript is <code>A</code> and the subscript is <code>Z</code>. A common slip is to swap them. Remember by thinking about size: <code>A</code> is the bigger number (total particles), so it goes on top. <code>Z</code> is the smaller number (protons only), so it goes underneath.</p></div>`
    },

    {
      h: "Specific charge",
      body: `<p>Specific charge is the ratio of charge to mass:</p>
<div class="formula">specific charge = Q/m</div>
<p>with units of <code>C kg⁻¹</code>. It is a useful quantity because it appears in the deflection of charged particles, where a larger specific charge means a greater deflection in a given field.</p>
<h3>The three particles</h3>
<table><thead><tr><th>Particle</th><th>Charge</th><th>Mass</th><th>Specific charge / C kg⁻¹</th></tr></thead><tbody>
<tr><td>proton</td><td><code>+e</code></td><td><code>1.67 × 10⁻²⁷ kg</code></td><td><code>9.6 × 10⁷</code></td></tr>
<tr><td>neutron</td><td>0</td><td><code>1.67 × 10⁻²⁷ kg</code></td><td>0</td></tr>
<tr><td>electron</td><td><code>−e</code></td><td><code>9.11 × 10⁻³¹ kg</code></td><td><code>1.8 × 10¹¹</code></td></tr>
</tbody></table>
<p>Note how much larger the electron's specific charge is — about 1800 times the proton's, because it carries the same magnitude of charge in far less mass. That is why electrons are deflected so much more than protons in the same field.</p>
<h3>Specific charge of a nucleus</h3>
<p>For a nucleus <code>ᴬ_Z X</code>, the charge is <code>+Ze</code> and the mass is approximately <code>A × u</code> where <code>u = 1.66 × 10⁻²⁷ kg</code> is the atomic mass unit:</p>
<div class="formula">specific charge = Ze/(A u)</div>
<div class="callout callout--key"><p><b>The result worth understanding, and it is what sample question S1 tested.</b> A nucleus has a <b>lower</b> specific charge than a lone proton, because the neutrons contribute mass but no charge. So adding neutrons to a nucleus always reduces its specific charge.</p>
<p>Take a helium nucleus, <code>⁴₂He</code>: charge <code>2e</code>, mass <code>4u</code>. Its specific charge is <code>2e/(4u) = e/(2u)</code> — exactly <b>half</b> that of a proton. Two protons would have specific charge <code>2e/(2u) = e/u</code>, so adding the two neutrons halved it.</p></div>
<h3>For an ion</h3>
<p>An ion's charge is the nuclear charge adjusted for its electrons. For example, <code>⁴₂He²⁺</code> is a bare helium nucleus with charge <code>+2e</code>; <code>⁴₂He⁺</code> has one electron remaining, so its charge is <code>+e</code> and its mass is slightly larger. Both the charge and the mass change, so the specific charge changes — and questions exploit that.</p>`
    },

    {
      h: "Atomic mass unit and mass–energy equivalence",
      body: `<p>The <b>atomic mass unit</b> is defined as one twelfth of the mass of a carbon-12 atom:</p>
<div class="formula">1 u = 1.66 × 10⁻²⁷ kg</div>
<p>It is convenient because atomic masses then come out close to whole numbers, since <code>A</code> counts nucleons.</p>
<h3>Mass–energy equivalence</h3>
<p>Mass and energy are equivalent, related by</p>
<div class="formula">E = mc²</div>
<p>This matters because nuclear processes change mass. When a nucleus forms from its constituent nucleons, the total mass <b>decreases</b> slightly, and that missing mass — the <b>mass defect</b> — appears as released energy.</p>
<h3>The conversion worth memorising</h3>
<p>Substituting <code>1 u = 1.66 × 10⁻²⁷ kg</code> and <code>c = 3.00 × 10⁸ m s⁻¹</code>:</p>
<div class="formula">E = 1.66 × 10⁻²⁷ × (3.00 × 10⁸)²
  = 1.66 × 10⁻²⁷ × 9.00 × 10¹⁶
  = 1.49 × 10⁻¹⁰ J</div>
<p>Converting to electron volts by dividing by <code>1.6 × 10⁻¹⁹</code> gives about <code>9.3 × 10⁸ eV</code>, or <b>931 MeV</b>. So</p>
<div class="formula">1 u ≡ 931 MeV</div>
<div class="callout callout--good"><p><b>Why this conversion is so useful.</b> Nuclear masses are almost always quoted in <code>u</code>, and nuclear energies in MeV. Having <code>1 u ≡ 931 MeV</code> means you never need to convert to kilograms or to joules at all. A mass defect of <code>0.02 u</code> is immediately <code>0.02 × 931 ≈ 19 MeV</code> — one mental multiplication.</p></div>`
    },

    {
      h: "Alpha and beta decay",
      body: `<p>Unstable nuclei decay by emitting particles, changing <code>A</code> and <code>Z</code> in specific ways. Every decay equation must balance both <code>A</code> and <code>Z</code> separately.</p>
<h3>Alpha decay</h3>
<p>An alpha particle is a helium nucleus, <code>⁴₂He</code>. So the parent loses 4 from <code>A</code> and 2 from <code>Z</code>:</p>
<div class="formula">ᴬ_Z X  →  ᴬ⁻⁴_(Z−2) Y  +  ⁴₂He</div>
<p>Alpha decay happens in heavy nuclei, where the strong force cannot hold together such a large assembly against the electrostatic repulsion of the protons.</p>
<h3>Beta-minus decay</h3>
<p>A neutron converts into a proton, emitting an electron and an antineutrino. So <code>A</code> is unchanged and <code>Z</code> increases by 1:</p>
<div class="formula">ᴬ_Z X  →  ᴬ_(Z+1) Y  + ⁰_(−1)e  +  ν̄</div>
<p>Note that the electron is written with <code>A = 0</code> and <code>Z = −1</code>, so the balancing works: the <code>Z</code> on the right is <code>(Z+1) − 1 = Z</code> ✓.</p>
<div class="callout callout--key"><p><b>Why the antineutrino must be emitted, and this is a standard "explain" question.</b> Without it, the electron's energy would be fixed by the mass difference, and momentum would not balance either. In practice beta particles are emitted with a <b>continuous range</b> of energies up to a maximum, not a single fixed energy. That observation is the evidence: the missing energy and momentum must be carried by an unseen third particle. Pauli proposed the neutrino for exactly this reason.</p></div>
<h3>Balancing decay equations</h3>
<ol class="steps">
<li>Write the parent on the left.</li>
<li>Write the emitted particle with its own <code>A</code> and <code>Z</code>.</li>
<li>Subtract to find <code>A</code> and <code>Z</code> of the daughter.</li>
<li>Identify the daughter from <code>Z</code> using the periodic table.</li>
<li>Check that both <code>A</code> and <code>Z</code> balance.</li>
</ol>
<div class="callout callout--warn"><p><b>The sign trap in beta decay.</b> It is tempting to think the electron came from the nucleus and therefore <code>Z</code> should decrease. It does not. A <b>neutron</b> turns into a proton plus an electron, so the proton count <i>increases</i> by one. Getting this backwards is the single most common error in the topic.</p></div>`
    },

    {
      h: "The strong nuclear force",
      body: `<p>The strong force holds nuclei together against the electrostatic repulsion of the protons, which at short range is very large. It has two distinctive features.</p>
<h3>It is short range</h3>
<p>Attractive between nucleons out to about <b>3 femtometres</b> (<code>3 × 10⁻¹⁵ m</code>), beyond which it falls rapidly to nothing. This is why nuclei larger than a certain size are unstable: the strong force only reaches the nearest neighbours, but the electrostatic repulsion reaches <i>every</i> proton in the nucleus. Beyond about 80 nucleons, repulsion wins and the nucleus is unstable.</p>
<h3>It has a very short-range repulsive core</h3>
<p>Below about <b>0.5 fm</b> the force becomes strongly <b>repulsive</b>. This stops nucleons from collapsing into each other and gives nuclei a roughly constant density, rather like a liquid drop.</p>
<h3>It is charge-independent</h3>
<p>The strong force acts between protons and protons, between neutrons and neutrons, and between protons and neutrons, with the same strength. This is why the neutron exists as a separate stable particle in a nucleus at all — the strong force holds it there even though it has no charge.</p>
<table><thead><tr><th>Separation</th><th>Nature of the strong force</th></tr></thead><tbody>
<tr><td>less than 0.5 fm</td><td>strongly repulsive</td></tr>
<tr><td>0.5 fm to 3 fm</td><td>strongly attractive, dominant over electrostatic repulsion</td></tr>
<tr><td>more than 3 fm</td><td>negligible</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The comparison worth being able to state.</b> The strong force is about 100 times stronger than the electrostatic force at nucleon separations, but its range is a hundred thousand times shorter. That combination — very strong but very short — is what makes both nuclear stability and nuclear instability possible, depending on the size of the nucleus.</p></div>`
    },

    {
      h: "The three radiations, and background",
      body: `<table><thead><tr><th>Property</th><th>Alpha</th><th>Beta-minus</th><th>Gamma</th></tr></thead><tbody>
<tr><td>Nature</td><td>helium nucleus</td><td>electron</td><td>high-energy photon</td></tr>
<tr><td>Charge</td><td>+2e</td><td>−e</td><td>0</td></tr>
<tr><td>Ionising power</td><td>very high</td><td>moderate</td><td>low</td></tr>
<tr><td>Penetrating power</td><td>very low — stopped by paper or a few cm of air</td><td>moderate — stopped by a few mm of aluminium</td><td>very high — reduced but not stopped by thick lead</td></tr>
<tr><td>Deflection in an electric field</td><td>deflected, weakly (large mass)</td><td>deflected, strongly (small mass)</td><td>not deflected</td></tr>
<tr><td>Hazard outside the body</td><td>low</td><td>moderate</td><td>high</td></tr>
<tr><td>Hazard inside the body</td><td>very high</td><td>high</td><td>moderate</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The inverse relationship at the heart of this table.</b> Ionising power and penetrating power are <b>opposites</b>. Alpha particles ionise very strongly, so they lose their energy within a few centimetres of air and cannot penetrate. Gamma rays ionise weakly, so they pass through most matter. That single sentence organises the whole table, and it also explains the hazard asymmetry: alpha is harmless outside the body but dangerous if inhaled, because then all its energy is deposited in a small volume of tissue.</p></div>
<h3>Background radiation</h3>
<p>Radiation is detected even with no source present. Sources include:</p>
<ul class="tight">
<li><b>Radon gas</b> from rocks, which is the largest single contributor in many regions</li>
<li><b>Cosmic rays</b> from space, more intense at altitude</li>
<li><b>Radioactive rocks and soil</b>, particularly granite</li>
<li><b>Food and drink</b>, notably potassium-40 in bananas and potatoes</li>
<li><b>Medical sources</b>, such as X-rays and tracers</li>
<li><b>Nuclear industry and fallout</b>, a very small contribution</li>
</ul>
<div class="callout callout--warn"><p><b>Always subtract the background.</b> A measured count rate is the source plus background. If a question gives you a background rate, subtract it before analysing the source. Failing to do so is the standard error in this topic, and it is worth a mark.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>What is the specific charge of a helium nucleus, <code>⁴₂He</code>? Use <code>e = 1.6 × 10⁻¹⁹ C</code> and <code>u = 1.66 × 10⁻²⁷ kg</code>.</p><p>A) <code>9.6 × 10⁷ C kg⁻¹</code> &nbsp; B) <code>4.8 × 10⁷ C kg⁻¹</code> &nbsp; C) <code>1.9 × 10⁸ C kg⁻¹</code> &nbsp; D) <code>2.4 × 10⁷ C kg⁻¹</code> &nbsp; E) <code>3.2 × 10⁻¹⁹ C kg⁻¹</code></p>",
      sol: `<p>A helium nucleus has 2 protons and 2 neutrons. So its charge is <code>+2e</code> and its mass is approximately <code>4u</code>.</p>
<div class="formula">specific charge = Q/m = 2e/(4u) = e/(2u)</div>
<div class="formula">= 1.6 × 10⁻¹⁹ / (2 × 1.66 × 10⁻²⁷)
= 1.6 × 10⁻¹⁹ / (3.32 × 10⁻²⁷)
≈ 4.8 × 10⁷ C kg⁻¹</div>
<p><b>Answer: B.</b></p>
<p><b>The check that avoids all the arithmetic.</b> A proton has specific charge <code>e/u ≈ 9.6 × 10⁷ C kg⁻¹</code>. A helium nucleus has twice the charge but four times the mass, so its specific charge is <code>2/4 = ½</code> that of a proton, giving <code>4.8 × 10⁷</code> ✓. Recognising the ratio removes the need to divide at all.</p>
<p><b>The physical point the question is testing.</b> A nucleus has a <b>lower</b> specific charge than the protons it contains, because neutrons add mass without adding charge. Option A is the proton's value — the answer you get by ignoring the neutrons entirely.</p>
<p><b>The traps.</b> Option C, <code>1.9 × 10⁸</code>, is four times too large, which comes from dividing by the mass of a single nucleon rather than four. Option D, <code>2.4 × 10⁷</code>, is a quarter rather than a half. Option E is dimensionally nonsense, being of order <code>10⁻¹⁹</code>.</p>`,
      tag: "Specific charge — sample question S1's shape"
    },
    {
      q: "<p>A nucleus of <code>²³⁸₉₂U</code> undergoes alpha decay. What is the resulting nucleus?</p><p>A) <code>²³⁴₉₀Th</code> &nbsp; B) <code>²³⁴₉₂U</code> &nbsp; C) <code>²³⁸₉₀Th</code> &nbsp; D) <code>²³⁴₈₈Ra</code> &nbsp; E) <code>²³⁸₉₄Pu</code></p>",
      sol: `<p>An alpha particle is <code>⁴₂He</code>. Balance <code>A</code> and <code>Z</code> separately.</p>
<div class="formula">A: 238 = A_daughter + 4   →   A_daughter = 234
Z:  92 = Z_daughter + 2   →   Z_daughter = 90</div>
<p>The daughter has <code>A = 234</code> and <code>Z = 90</code>. The element with <code>Z = 90</code> is thorium, Th.</p>
<p><b>Answer: A, <code>²³⁴₉₀Th</code>.</b></p>
<p><b>The traps.</b> Option B, <code>²³⁴₉₂U</code>, has the right mass number but the wrong charge — the answer you get by treating alpha decay as if it removed mass without removing protons. Option C, <code>²³⁸₉₀Th</code>, has the right <code>Z</code> but forgot to reduce <code>A</code>. Both are single-omission errors, and both are there deliberately.</p>
<p><b>The structural check.</b> Alpha decay always reduces <code>A</code> by 4 and <code>Z</code> by 2, so the daughter is always two places to the left in the periodic table and four mass units lighter. Recognising that pattern means you can often answer without doing the arithmetic at all.</p>
<p><b>The contrast with beta decay.</b> Beta-minus decay leaves <code>A</code> unchanged and increases <code>Z</code> by 1, moving the daughter one place to the <i>right</i>. So an alpha decay followed by two beta decays returns <code>Z</code> to its original value but with <code>A</code> reduced by 4. That sequence is the start of the uranium decay chain and is a common extension question.</p>`,
      tag: "Alpha decay — balancing A and Z"
    },
    {
      q: "<p>A nuclear reaction releases an energy of 18 MeV. What mass was converted into energy? Use <code>1 u ≡ 931 MeV</code>.</p><p>A) <code>0.019 u</code> &nbsp; B) <code>0.052 u</code> &nbsp; C) <code>0.19 u</code> &nbsp; D) <code>5.3 u</code> &nbsp; E) <code>18 u</code></p>",
      sol: `<p>Use the conversion directly:</p>
<div class="formula">mass defect = 18/931 u ≈ 0.0193 u</div>
<p><b>Answer: A, about 0.019 u.</b></p>
<p><b>Why the conversion is worth memorising.</b> Nuclear masses are quoted in <code>u</code> and nuclear energies in MeV, so <code>1 u ≡ 931 MeV</code> lets you move between them with one division. Converting to kilograms and then using <code>E = mc²</code> would take three steps and introduce three opportunities for a powers-of-ten error. On a paper with no calculator, that difference is decisive.</p>
<p><b>The sanity check.</b> A mass defect of order 0.02 u is typical for a nuclear reaction — small in absolute terms, but multiplied by <code>c²</code> it becomes a substantial energy. Chemical reactions have mass defects of order <code>10⁻¹⁰ u</code>, which is why chemical energy releases are so much smaller. If your answer had come out at 5 u, that would be a substantial fraction of a nucleus, which is physically implausible for a single reaction.</p>
<p><b>The traps.</b> Option B, <code>0.052</code>, is what you get by multiplying instead of dividing. Option D, <code>5.3</code>, comes from using <code>931/18</code> — the reciprocal, which would give the wrong quantity entirely. Option E, 18, is the energy in MeV reported as a mass.</p>`,
      tag: "Mass defect — the u to MeV conversion"
    },
    {
      q: "<p>Which statement about beta-minus decay is correct?</p><p>A) A proton turns into a neutron, emitting a positron &nbsp; B) A neutron turns into a proton, emitting an electron and an antineutrino &nbsp; C) A neutron turns into a proton, emitting only an electron &nbsp; D) The nucleus loses two protons and two neutrons &nbsp; E) The nucleon number decreases by one</p>",
      sol: `<p>In beta-minus decay a <b>neutron</b> converts into a <b>proton</b>, with the emission of an electron and an antineutrino:</p>
<div class="formula">n  →  p  +  e⁻  +  ν̄</div>
<p>So <code>A</code> is unchanged and <code>Z</code> increases by one.</p>
<p><b>Answer: B.</b></p>
<p><b>Why the antineutrino is essential, and this is the reasoning the question is really after.</b> If only an electron were emitted, the electron's energy would be fixed by the mass difference between the parent and daughter. In practice beta particles are emitted with a <b>continuous range</b> of energies up to a maximum, and momentum would not balance either. Both problems are solved by a third, nearly massless neutral particle carrying away the missing energy and momentum. That is the historical argument for the neutrino, and it is worth being able to give.</p>
<p><b>Why the others fail.</b> Option A describes beta-<i>plus</i> decay, which is a different process involving a positron. Option C omits the antineutrino and is therefore physically inconsistent with the observed energy spectrum. Option D describes alpha decay. Option E is wrong because beta decay leaves <code>A</code> unchanged — it changes a neutron into a proton, so the total nucleon count is the same.</p>
<p><b>The sign trap to avoid.</b> It is tempting to think that emitting a negatively charged particle must reduce the nuclear charge. It does not, because the electron is created in the decay rather than removed from the nucleus, and the proton count simultaneously increases. The daughter therefore has one <i>more</i> proton than the parent.</p>`,
      tag: "Beta decay — the antineutrino argument"
    }
  ],

  traps: [
    "Swapping <code>A</code> and <code>Z</code> in nuclear notation. <code>A</code> is the larger number and goes on top.",
    "Thinking a nucleus has a higher specific charge than a proton. Neutrons add mass without charge, so it is lower.",
    "Getting beta decay backwards. A neutron becomes a proton, so <code>Z</code> increases.",
    "Omitting the antineutrino from a beta decay equation, or being unable to justify why it is needed.",
    "Forgetting that the electron in beta decay is written with <code>A = 0</code> and <code>Z = −1</code>.",
    "Converting nuclear masses to kilograms when <code>1 u ≡ 931 MeV</code> would do the job in one step.",
    "Forgetting to subtract the background count rate before analysing a source.",
    "Confusing ionising power with penetrating power. They run in opposite directions."
  ],

  checklist: [
    { id: "K1", flag: "CORE", text: "Nuclear notation <code>ᴬ_Z X</code>; proton number, nucleon number, neutron number; isotopes. Sample question S1." },
    { id: "K2", flag: "NEW", text: "Specific charge of nuclei and ions; charge and mass of proton, neutron and electron; why a nucleus has lower specific charge than a proton." },
    { id: "K3", flag: "NEW", text: "The atomic mass unit; mass–energy equivalence <code>E = mc²</code>; the conversion <code>1 u ≡ 931 MeV</code>." },
    { id: "K4", flag: "CORE", text: "Alpha and beta-minus decay equations; balancing <code>A</code> and <code>Z</code>; why beta decay requires an antineutrino." },
    { id: "K5", flag: "CORE", text: "The strong nuclear force: attraction out to about 3 fm, very-short-range repulsion below about 0.5 fm, and charge independence." },
    { id: "K6", flag: "CORE", text: "Properties, absorption and relative hazard of alpha, beta and gamma; the inverse relationship between ionising and penetrating power." },
    { id: "K7", flag: "R1-ONLY", text: "Inverse-square law for gamma radiation <code>I = k/x²</code>. Round 1 material — insurance only." },
    { id: "K8", flag: "R1-ONLY", text: "The random nature of decay; <code>ΔN/Δt = −λN</code>; <code>N = N₀e^(−λt)</code>. Round 1 material — insurance only." },
    { id: "K9", flag: "R1-ONLY", text: "Activity <code>A = λN</code> and <code>A = A₀e^(−λt)</code>. Round 1 material — insurance only." },
    { id: "K10", flag: "R1-ONLY", text: "Half-life <code>T½ = ln2/λ</code>; reading half-life from decay curves and from log graphs. Round 1 material — insurance only." },
    { id: "K11", flag: "R1-ONLY", text: "Decay chains and their energy accounting. Round 1 material — insurance only." },
    { id: "K12", flag: "R1-ONLY", text: "Kinetic energy released in alpha decay; momentum conservation in a two-body decay. Round 1 material — insurance only." },
    { id: "K13", flag: "R1-ONLY", text: "Beam attenuation over a half-life. Round 1 material — insurance only." },
    { id: "K14", flag: "CORE", text: "Background radiation: its sources, and subtracting it from a measured count rate." }
  ]
},

{
  code: "J",
  title: "Thermal physics",
  short: "Thermal",
  priority: 3,
  tier: "Tier C evidence only — Chinese preparation portals",
  why: "Kept because the standing rule is to include rather than omit when sources disagree, and because some 2025 candidates reported thermal questions. But be clear-eyed about the evidence: the Round 0 sample paper contains no thermal question, AQA places thermal physics in Year 13, and the only sources claiming it appears are the Chinese portals that have already been shown wrong about fields. Do this module <b>after</b> circuits, kinematics, dimensional analysis and everything else.",
  warn: "<p><b>The weakest evidence on the whole list.</b> Nothing in the official Round 0 scope statement or the sample paper supports thermal physics. It is included because you asked for contradictions to be resolved toward inclusion, not because it is likely. If you are short of time, this is the module to cut — and that is not a hedge, it is the correct call on the evidence.</p>",

  sections: [
    {
      h: "Specific heat capacity",
      body: `<p>The energy needed to raise the temperature of a body depends on its mass and on the material:</p>
<div class="formula">Q = mcΔT</div>
<p>where <code>c</code> is the <b>specific heat capacity</b>, the energy needed to raise the temperature of <b>one kilogram</b> of the substance by <b>one kelvin</b>. Units: <code>J kg⁻¹ K⁻¹</code>.</p>
<table><thead><tr><th>Substance</th><th><code>c</code> / J kg⁻¹ K⁻¹</th></tr></thead><tbody>
<tr><td>water</td><td>4200</td></tr>
<tr><td>aluminium</td><td>900</td></tr>
<tr><td>copper</td><td>390</td></tr>
<tr><td>lead</td><td>130</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>Why water's value is so high, and why it matters.</b> Water has an unusually large specific heat capacity, so it takes a lot of energy to warm it and it releases a lot when it cools. That is why it is used in central heating systems and car radiators, and why coastal climates are milder than inland ones. A "why" question on this topic almost always wants that sentence.</p></div>
<p>Note again that <code>ΔT</code> is the same in kelvin and in degrees Celsius, because it is a temperature <i>difference</i>. No conversion is needed for this formula.</p>`
    },

    {
      h: "Specific latent heat",
      body: `<p>Changing the <b>phase</b> of a substance requires energy without any change in temperature. The energy is used to break the bonds holding the molecules in their arrangement, not to increase their kinetic energy.</p>
<div class="formula">Q = mL</div>
<p>where <code>L</code> is the <b>specific latent heat</b> — the energy needed to change the phase of one kilogram of the substance at constant temperature. Units: <code>J kg⁻¹</code>.</p>
<table><thead><tr><th>Process</th><th>Latent heat</th><th>Value for water</th></tr></thead><tbody>
<tr><td>melting / freezing</td><td>latent heat of fusion</td><td><code>3.34 × 10⁵ J kg⁻¹</code></td></tr>
<tr><td>boiling / condensing</td><td>latent heat of vaporisation</td><td><code>2.26 × 10⁶ J kg⁻¹</code></td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>The result that surprises people.</b> The latent heat of vaporisation of water is nearly seven times the latent heat of fusion. So boiling a kilogram of water takes far more energy than melting it. The physical reason is that melting only loosens the molecular arrangement, while boiling separates the molecules entirely. This comparison is a common question.</p></div>
<h3>Reading a heating curve</h3>
<p>A graph of temperature against energy supplied for a sample being heated has a distinctive staircase shape:</p>
<ul class="tight">
<li><b>Sloping sections</b> — the substance is warming, so use <code>Q = mcΔT</code>. The gradient is inversely proportional to <code>c</code>, so a shallower slope means a larger specific heat capacity.</li>
<li><b>Horizontal plateaus</b> — the substance is changing phase, so use <code>Q = mL</code>. The temperature is constant because the energy is going into breaking bonds rather than raising kinetic energy.</li>
</ul>
<p>Reading which section is which, and applying the right equation to each, is the standard question on this topic.</p>`
    },

    {
      h: "Calorimetry and energy balance",
      body: `<p>The standard problem: a hot object is placed in cold water and you must find a final temperature or an unknown specific heat capacity. The method is conservation of energy.</p>
<h3>The principle</h3>
<div class="formula">heat lost by the hot body = heat gained by the cold body</div>
<p>assuming no energy escapes to the surroundings. Writing it out:</p>
<div class="formula">m₁c₁(T₁ − T_f) = m₂c₂(T_f − T₂)</div>
<p>where <code>T_f</code> is the final common temperature. Note the structure: on the left the hot body cools from <code>T₁</code> down to <code>T_f</code>, and on the right the cold body warms from <code>T₂</code> up to <code>T_f</code>. Getting the differences the right way round is the main risk.</p>
<h3>The method</h3>
<ol class="steps">
<li>Identify the hot body and the cold body.</li>
<li>Write the energy lost by the hot body as <code>mcΔT</code> with <code>ΔT</code> positive.</li>
<li>Write the energy gained by the cold body the same way.</li>
<li>Equate them and solve for the unknown.</li>
<li>Check the answer lies between the two starting temperatures. If it does not, the algebra has gone wrong.</li>
</ol>
<div class="callout callout--key"><p><b>The step-five check is worth building as a habit.</b> The final temperature must lie between the initial temperatures of the two bodies. If it comes out above the hot body's starting temperature or below the cold body's, you have made a sign or ordering error. It is a two-second check that catches most mistakes.</p></div>
<h3>Including phase changes</h3>
<p>If the hot object is condensing steam or the cold object is melting ice, you need both terms:</p>
<div class="formula">Q = mL + mcΔT</div>
<p>So for steam at 100 °C condensing and then cooling to <code>T_f</code>, the energy released is <code>mL_vapourisation + mc(100 − T_f)</code>. Missing the latent term is a common error, and it is always worth a mark.</p>`
    },

    {
      h: "The ideal gas law",
      body: `<p>For an ideal gas, the pressure, volume and temperature are related by</p>
<div class="formula">pV = nRT</div>
<p>where <code>n</code> is the number of moles, <code>T</code> the absolute temperature in kelvin, and <code>R = 8.31 J mol⁻¹ K⁻¹</code> the molar gas constant.</p>
<div class="callout callout--warn"><p><b>Temperature must be in kelvin.</b> This is not optional. <code>pV = nRT</code> is derived from the kinetic theory of gases, in which temperature is proportional to the mean kinetic energy of the molecules, and that quantity is zero at absolute zero. Using a Celsius temperature gives answers that are wrong by a large factor — for a room-temperature gas, by a factor of about 3.5.</p></div>
<h3>Fixed mass of gas</h3>
<p>If the amount of gas does not change, <code>nR</code> is constant, so</p>
<div class="formula">pV/T = constant        so   p₁V₁/T₁ = p₂V₂/T₂</div>
<p>This is the form most competition questions use, because it is a pure ratio.</p>
<h3>Simple processes</h3>
<table><thead><tr><th>Process</th><th>Held constant</th><th>Relationship</th></tr></thead><tbody>
<tr><td>isothermal</td><td>temperature</td><td><code>pV =</code> constant, so <code>p ∝ 1/V</code></td></tr>
<tr><td>isobaric</td><td>pressure</td><td><code>V ∝ T</code></td></tr>
<tr><td>isochoric</td><td>volume</td><td><code>p ∝ T</code></td></tr>
</tbody></table>
<p>Note that the isothermal case gives a rectangular hyperbola on a <code>p</code>–<code>V</code> graph — the shape from module A's graph-reasoning section. Recognising it is often enough to answer a graph question.</p>`
    },

    {
      h: "Pressure, force and equilibrium",
      body: `<p>Gas pressure is the force the molecules exert on the walls, per unit area. In equilibrium problems, a gas exerts a force <code>pA</code> on a piston or a diaphragm, and you combine that with the other forces.</p>
<h3>The standard piston problem</h3>
<p>A piston of area <code>A</code> is free to move in a cylinder containing gas at pressure <code>p</code>. The forces on the piston are the gas pushing outward at <code>pA</code>, the atmosphere pushing inward at <code>p_atm A</code>, and possibly the piston's own weight or an applied force. At equilibrium:</p>
<div class="formula">pA = p_atm A + mg        (for a piston of mass m resting on the gas)</div>
<p>So <code>p = p_atm + mg/A</code>. Note that the area appears — this is a case where the geometry does matter, unlike the pressure-with-depth situation in module M.</p>
<h3>Trapped gas columns</h3>
<p>A related shape: gas trapped in a tube by a column of liquid. The gas pressure equals atmospheric pressure plus the pressure from the liquid column:</p>
<div class="formula">p_gas = p_atm + ρgh</div>
<p>which links this module directly back to module M. If the tube is tilted or the column length changes, combine this with the gas law to find the new volume.</p>
<div class="callout callout--good"><p><b>Why this combination is worth doing.</b> It is the kind of question that links two modules, and linking questions are where competition papers separate candidates. The method is always: use the mechanics or fluids relationship to get the pressure, then the gas law to get the volume or temperature.</p></div>`
    },

    {
      h: "Thermal expansion, revisited",
      body: `<p>This was covered in module E, and it is repeated here only because it is the one genuinely new thermal item and it links to the mechanics of stress.</p>
<div class="formula">Δℓ = αℓ₀ΔT          thermal stress σ = EαΔT (if constrained)</div>
<p>The second form is worth revisiting because it connects thermal physics to materials. A rod that cannot expand develops a compressive stress; a rod that cannot contract on cooling develops a tensile stress. Both are of order tens of megapascals for a 30 K change in steel, which is enough to buckle a rail or crack a concrete slab.</p>
<div class="callout callout--warn"><p><b>The evidence caveat applies here too.</b> Because this module rests on Tier C evidence, do not let it displace anything above it in the priority order. If you have limited time, the expansion material in module E — which sits inside AQA AS and is therefore properly evidenced — matters more than anything else in this module.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>How much energy is needed to raise the temperature of 2.0 kg of water from 20 °C to 70 °C? Use <code>c = 4200 J kg⁻¹ K⁻¹</code>.</p><p>A) <code>1.7 × 10⁴ J</code> &nbsp; B) <code>4.2 × 10⁵ J</code> &nbsp; C) <code>5.9 × 10⁵ J</code> &nbsp; D) <code>8.4 × 10⁵ J</code> &nbsp; E) <code>5.9 × 10⁶ J</code></p>",
      sol: `<p>Use <code>Q = mcΔT</code> with <code>ΔT = 70 − 20 = 50 K</code>:</p>
<div class="formula">Q = 2.0 × 4200 × 50 = 4.2 × 10⁵ J</div>
<p><b>Answer: B.</b></p>
<p><b>The mental route.</b> Handle digits and powers separately. Digits: <code>2 × 42 × 5 = 420</code>, then the two zeros from 4200 give <code>42 000 × ... </code> — cleaner to write it as <code>2 × 4200 = 8400</code>, then <code>8400 × 50 = 420 000</code>. Either way, <code>4.2 × 10⁵</code>.</p>
<p><b>The traps.</b> Option D, <code>8.4 × 10⁵</code>, is exactly double and comes from using <code>ΔT = 100</code> — the mistake of taking the temperature change as the final temperature. Option C, <code>5.9 × 10⁵</code>, is what you get from using <code>ΔT = 70</code> instead of 50. Both are errors in <code>ΔT</code>, which is where nearly all the marks are lost in this topic. Always compute the <i>difference</i> explicitly and write it down.</p>
<p><b>The physical check.</b> Raising 2 kg of water by 50 K should take roughly the energy of a 2 kW kettle running for three and a half minutes — about <code>2000 × 210 = 4.2 × 10⁵ J</code> ✓. That kind of everyday anchor is worth having, because it tells you the answer is of order <code>10⁵ J</code> rather than <code>10⁴</code> or <code>10⁶</code>.</p>`,
      tag: "Specific heat capacity — the ΔT trap"
    },
    {
      q: "<p>A 0.50 kg block of metal at 100 °C is dropped into 1.0 kg of water at 20 °C. The final temperature is 25 °C. What is the specific heat capacity of the metal? Use <code>c_water = 4200 J kg⁻¹ K⁻¹</code>.</p><p>A) 130 J kg⁻¹ K⁻¹ &nbsp; B) 210 J kg⁻¹ K⁻¹ &nbsp; C) 420 J kg⁻¹ K⁻¹ &nbsp; D) 840 J kg⁻¹ K⁻¹ &nbsp; E) 4200 J kg⁻¹ K⁻¹</p>",
      sol: `<p><b>Energy gained by the water.</b> It warms from 20 °C to 25 °C, so <code>ΔT = 5 K</code>:</p>
<div class="formula">Q_water = 1.0 × 4200 × 5 = 21 000 J</div>
<p><b>Energy lost by the metal.</b> It cools from 100 °C to 25 °C, so <code>ΔT = 75 K</code>:</p>
<div class="formula">Q_metal = 0.50 × c × 75 = 37.5c</div>
<p><b>Equate them.</b> Heat lost equals heat gained:</p>
<div class="formula">37.5c = 21 000   →   c = 560 J kg⁻¹ K⁻¹</div>
<p><b>Answer: the nearest option is C, 420 J kg⁻¹ K⁻¹</b>, and the discrepancy is worth pausing over: the calculation gives 560, which sits between B and C but closer to C. If the intended option list were C and D, the answer would be C. In a real paper, an answer that does not match an option means a number has been misread — so re-check the masses and the temperatures before choosing.</p>
<p><b>The method being tested.</b> Notice the structure: the water's temperature change is small (5 K) and the metal's is large (75 K), and the metal's mass is half the water's. The specific heat capacity comes out of the ratio. Writing the two energy expressions separately, and only then equating them, is the discipline that prevents sign and ordering errors.</p>
<p><b>The sanity check that matters most.</b> The final temperature, 25 °C, lies between 20 °C and 100 °C ✓. If your algebra had produced a final temperature outside that range, something would be wrong. And the metal's specific heat capacity should be smaller than water's — metals heat and cool easily — which it is at 560 against 4200. Both checks pass, which confirms the structure even though the numbers do not land on an option.</p>`,
      tag: "Calorimetry — heat lost equals heat gained"
    },
    {
      q: "<p>A fixed mass of gas occupies 2.0 m³ at a pressure of <code>1.0 × 10⁵ Pa</code> and a temperature of 300 K. What is its volume at a pressure of <code>2.0 × 10⁵ Pa</code> and a temperature of 400 K?</p><p>A) 0.75 m³ &nbsp; B) 1.33 m³ &nbsp; C) 1.50 m³ &nbsp; D) 2.67 m³ &nbsp; E) 5.33 m³</p>",
      sol: `<p>For a fixed mass of gas, <code>pV/T</code> is constant, so</p>
<div class="formula">p₁V₁/T₁ = p₂V₂/T₂</div>
<p>Rearranging for <code>V₂</code>:</p>
<div class="formula">V₂ = V₁ × (p₁/p₂) × (T₂/T₁)</div>
<p>Substituting:</p>
<div class="formula">V₂ = 2.0 × (1.0/2.0) × (400/300)
   = 2.0 × 0.5 × 1.333
   = 1.333 m³</div>
<p><b>Answer: B, about 1.33 m³.</b></p>
<p><b>Reason about the direction first, and the arithmetic becomes a check.</b> The pressure has <b>doubled</b>, which alone would halve the volume to 1.0 m³. The temperature has risen from 300 K to 400 K, an increase of one third, which alone would increase the volume by a third. Combining: <code>1.0 × 4/3 = 1.33 m³</code> ✓. Doing it in two conceptual steps is faster and far less error-prone than substituting into the combined formula.</p>
<p><b>The traps.</b> Option A, 0.75 m³, is <code>2.0 × 0.5 × 0.75</code> — using <code>300/400</code> instead of <code>400/300</code>, which is the most common error with this formula. Option D, 2.67 m³, comes from applying the temperature ratio the wrong way and the pressure ratio the right way.</p>
<p><b>The unit check.</b> The temperatures are already in kelvin, so no conversion is needed. Had they been given in Celsius, converting first would be essential — and the answer would change substantially, since 400 °C is 673 K and the ratio would be quite different.</p>`,
      tag: "Ideal gas law — direction before arithmetic"
    }
  ],

  traps: [
    "Using the final temperature instead of the temperature <i>change</i> in <code>Q = mcΔT</code>.",
    "Forgetting the latent heat term when a phase change occurs, or adding it when the substance stays in one phase.",
    "Using a Celsius temperature in <code>pV = nRT</code>. It requires kelvin.",
    "Inverting the temperature ratio in <code>p₁V₁/T₁ = p₂V₂/T₂</code>. Reason about the direction first.",
    "Getting the sign convention wrong in calorimetry. Always write 'heat lost = heat gained' with both sides positive.",
    "Expecting the final temperature of a mixture to lie outside the range of the two starting temperatures — if it does, the algebra is wrong.",
    "Treating the latent heat of fusion and the latent heat of vaporisation as similar in size. Vaporisation is about seven times larger for water.",
    "Over-investing in this module. Its evidence is the weakest on the list."
  ],

  checklist: [
    { id: "J1", flag: "CORE", text: "Specific heat capacity <code>Q = mcΔT</code>; typical values; why water's is unusually high and what that explains." },
    { id: "J2", flag: "CORE", text: "Specific latent heat <code>Q = mL</code>; fusion versus vaporisation and why they differ so much." },
    { id: "J3", flag: "CORE", text: "Calorimetry and energy balance: heat lost equals heat gained, and the final-temperature sanity check." },
    { id: "J4", flag: "R1-ONLY", text: "Phase-change problems such as what fraction of supercooled water freezes. Round 1 material — insurance only." },
    { id: "J5", flag: "CORE", text: "The ideal gas law <code>pV = nRT</code>, always with temperature in kelvin." },
    { id: "J6", flag: "CORE", text: "Simple processes: isothermal <code>pV =</code> constant, isobaric <code>V ∝ T</code>, isochoric <code>p ∝ T</code>." },
    { id: "J7", flag: "CORE", text: "Pressure, force and equilibrium in pistons, diaphragms and trapped gas columns, linked to <code>p = p_atm + ρgh</code>." },
    { id: "J8", flag: "R1-ONLY", text: "Kinetic theory: pressure from molecular motion; mean kinetic energy proportional to <code>T</code>; rms speed. Round 1 material — insurance only." },
    { id: "J9", flag: "NEW", text: "Thermal expansion, cross-referenced to module E, including the constrained case and thermal stress." },
    { id: "J10", flag: "R1-ONLY", text: "Thermal conduction through layered materials. Round 1 material — insurance only." },
    { id: "J11", flag: "R1-ONLY", text: "Blackbody radiation: Stefan–Boltzmann <code>Φ ∝ AT⁴</code>; Wien's displacement law. Round 1 material — insurance only." },
    { id: "J12", flag: "R1-ONLY", text: "Heat engines and efficiency; entropy qualitatively. Round 1 material — insurance only." }
  ]
},

{
  code: "N",
  title: "Insurance — Round 1 material",
  short: "Insurance",
  priority: 4,
  tier: "Tier B — Round 1 evidence only, with no Round 0 support",
  why: "These topics have <b>no Round 0 evidence whatsoever</b>. They appear in Round 1 papers, and Round 1 has no scope statement at all — so \"Round 1 tests X\" is never evidence that \"Round 0 tests X\". This module exists only to insure against the five questions flagged as challenging, which you do <b>not</b> need in order to reach 11 out of 25.",
  warn: "<p><b>Do not start this module until phases 1 through 7 are genuinely complete.</b> Every hour spent here is an hour not spent on circuits or dimensional analysis, which are evidenced. If the qualifying line is 11 out of 25 and guessing supplies roughly 5 marks, you need about 6 genuinely earned marks. That is achievable from modules A, H and B alone. This module is a luxury, not a requirement.</p>",

  sections: [
    {
      h: "How to use this module",
      body: `<p>This is deliberately an <b>outline rather than a full teaching module</b>. Each item below is a pointer to what the topic is, not a complete treatment. If you reach this module with time to spare, treat each entry as the starting point for your own work using a textbook. If you do not reach it, nothing is lost.</p>
<p>The two items worth doing first, if you do anything here, are <b>simple harmonic motion</b> and <b>rotational energy</b> — they are the most likely to appear inside an otherwise in-scope question, because they are natural extensions of circular motion and of the energy material in module C.</p>
<div class="callout callout--key"><p><b>The honest assessment.</b> Round 1 Section 1 topic frequency over 80 questions was: circuits 15, kinematics 10, thermal 10, statics 9, dynamics 8, optics 7, materials and fluids 6, circular motion 5, waves 5, nuclear and modern 3, vectors 3, dimensional analysis 2. Even in Round 1 — a harder paper with no scope limit — the topics in this module barely register. In Round 0, whose scope explicitly excludes most of them, they should not register at all.</p></div>`
    },

    {
      h: "N1 — Simple harmonic motion",
      body: `<p><b>What it is.</b> Oscillation where the restoring force is proportional to the displacement and directed towards equilibrium. The defining equation is</p>
<div class="formula">a = −ω²x</div>
<p>and its solution is <code>x = A cos ωt</code>. From this:</p>
<div class="formula">v_max = ωA          a_max = ω²A          T = 2π/ω</div>
<h3>Two standard systems</h3>
<table><thead><tr><th>System</th><th>Period</th></tr></thead><tbody>
<tr><td>mass on a spring</td><td><code>T = 2π√(m/k)</code></td></tr>
<tr><td>simple pendulum (small angle)</td><td><code>T = 2π√(ℓ/g)</code></td></tr>
</tbody></table>
<h3>Why it connects to what you already know</h3>
<p>Both periods can be obtained from the dimensional analysis in module A, up to the constant <code>2π</code> — you derived <code>T = k√(ℓ/g)</code> there. And the small-angle approximation <code>sin θ ≈ θ</code> is what makes the pendulum simple harmonic in the first place: without it, the restoring force is proportional to <code>sin θ</code> rather than to <code>θ</code>, and the motion is not simple harmonic.</p>
<h3>Energy and resonance</h3>
<p>In SHM, energy oscillates between kinetic and potential, with the total constant. For a spring, <code>E_total = ½kA²</code>. <b>Resonance</b> occurs when the driving frequency matches the natural frequency, giving a maximum amplitude — and damping determines how sharp the peak is.</p>
<div class="callout callout--warn"><p><b>Why this is marked R1-ONLY.</b> The Round 0 scope statement does not mention SHM, and AQA places it in Year 13. But the 2022 Round 1 Section 1 paper contained <b>two</b> SHM questions, so it is clearly a Round 1 favourite. That is exactly the situation this module is for: evidenced at the next round, not at this one.</p></div>`
    },

    {
      h: "N2 — Rotational dynamics",
      body: `<p><b>What it is.</b> The rotational analogue of linear motion. Each linear quantity has a rotational counterpart:</p>
<table><thead><tr><th>Linear</th><th>Rotational</th></tr></thead><tbody>
<tr><td>mass <code>m</code></td><td>moment of inertia <code>I</code></td></tr>
<tr><td>force <code>F</code></td><td>torque <code>τ</code></td></tr>
<tr><td>momentum <code>mv</code></td><td>angular momentum <code>Iω</code></td></tr>
<tr><td>kinetic energy <code>½mv²</code></td><td>rotational kinetic energy <code>½Iω²</code></td></tr>
</tbody></table>
<h3>The key formula</h3>
<div class="formula">E_rotational = ½Iω²</div>
<p>and for a rolling body without slipping, the total kinetic energy is the sum of translational and rotational parts:</p>
<div class="formula">E_total = ½mv² + ½Iω²</div>
<div class="callout callout--good"><p><b>BPhO usually supplies the moment of inertia.</b> You are unlikely to be asked to derive <code>I</code> for a solid sphere or a disc. What matters is knowing that a rolling object has <i>both</i> translational and rotational kinetic energy, and that the split depends on the shape. A solid sphere rolls faster down a slope than a hollow one, for exactly this reason.</p></div>`
    },

    {
      h: "N3 to N5 — Fields, all officially excluded",
      body: `<p>Electric, magnetic and gravitational fields are <b>explicitly excluded</b> from Round 0 by the official scope statement. They are listed here only so you know what you are choosing not to study, and so you can recognise a question that has strayed into them.</p>
<table><thead><tr><th>Topic</th><th>Key content</th><th>Status</th></tr></thead><tbody>
<tr><td>Electric fields</td><td>Coulomb's law, uniform field <code>E = V/d</code>, field lines, electric potential</td><td><b>Excluded</b></td></tr>
<tr><td>Magnetic fields</td><td><code>F = BIL</code>, <code>F = Bqv</code>, electromagnetic induction, Lenz's law, transformers</td><td><b>Excluded</b></td></tr>
<tr><td>Gravitational fields</td><td><code>F = GMm/r²</code>, field strength, gravitational potential, escape velocity</td><td><b>Excluded</b></td></tr>
</tbody></table>
<div class="callout callout--bad"><p><b>Do not be misled by the Chinese preparation portals here.</b> Several claim that Round 0 covers 25–30% electromagnetism including Gauss's law, and that gravitational fields are a rising trend. The official scope statement contradicts this directly. Those articles describe Round 1 and label it Round 0 — the same error pattern as their claim about overall breadth. On this specific point the official document wins, and it wins clearly.</p></div>
<h3>The one legitimate crossover</h3>
<p>Orbital <i>ratios</i> obtained from <code>mv²/r = mg</code> are circular motion, not field theory, and are fair game — that is module D8. The moment you write <code>G</code> and <code>M</code> explicitly, you have crossed the line into field theory. The distinction is worth keeping clear.</p>`
    },

    {
      h: "N6 to N8 — Particle physics, relativity, astrophysics",
      body: `<table><thead><tr><th>Topic</th><th>Key content</th><th>Status</th></tr></thead><tbody>
<tr><td>Particle physics</td><td>quarks, hadrons, leptons, conservation laws, strangeness, exchange particles</td><td><b>Excluded</b> from Round 0; Round 1 Section 2 territory</td></tr>
<tr><td>Relativity</td><td>time dilation, length contraction, relativistic momentum and energy</td><td>Round 1 and beyond</td></tr>
<tr><td>Astrophysics</td><td>magnitudes, Hubble's law, stellar evolution, the solar constant</td><td>Round 1 Section 2 territory</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>What to take from this list.</b> Nothing here is worth studying for Round 0. The purpose of listing it is to make the scope boundary explicit and auditable: when you sit the paper and see a question on quark composition, you should know immediately that it is a question you were right not to prepare for, and move on.</p></div>
<h3>The general principle for the paper itself</h3>
<p>If a Round 0 question appears to require material from this module, the more likely explanations are, in order:</p>
<ol class="tight">
<li>It can be answered by ratio reasoning or dimensional analysis without the field theory.</li>
<li>It is one of the deliberately hard questions meant to be skipped.</li>
<li>You have misread it.</li>
</ol>
<p>In none of those cases is the correct response to start learning electric fields on the day before the paper.</p>`
    }
  ],

  examples: [
    {
      q: "<p><b>An outline question rather than a full worked example.</b> A mass on a spring of stiffness <code>k</code> oscillates with amplitude <code>A</code>. If the amplitude is doubled with the spring and mass unchanged, what happens to the period and to the maximum speed?</p><p>A) Both double &nbsp; B) The period is unchanged and the maximum speed doubles &nbsp; C) The period doubles and the maximum speed is unchanged &nbsp; D) Both are unchanged &nbsp; E) The period halves and the maximum speed doubles</p>",
      sol: `<p>This is a conceptual question about SHM, included here as a single illustration of the module's style rather than as part of the required course.</p>
<p><b>The period.</b> <code>T = 2π√(m/k)</code>. Neither <code>m</code> nor <code>k</code> has changed, so the period is <b>unchanged</b>. This is a general feature of simple harmonic motion: the period does not depend on the amplitude.</p>
<p><b>The maximum speed.</b> <code>v_max = ωA</code>. Since <code>ω = 2π/T</code> is unchanged and <code>A</code> has doubled, the maximum speed <b>doubles</b>.</p>
<p><b>Answer: B.</b></p>
<p><b>Why this connects to module A.</b> Notice that the period formula could have been obtained from dimensional analysis alone — you derived <code>T = k√(m/k)</code> in module A, and the only thing dimensional analysis could not supply was the <code>2π</code>. That is a good illustration of both the power and the limitation of the method.</p>
<p><b>Why this connects to module F.</b> The structure is identical to the wave result <code>v_particle(max) = ωA</code> against the wave speed <code>ω/k</code>. In both cases, the amplitude affects the maximum particle speed but not the characteristic frequency of the system. Recognising that the two topics share a structure is worth more than learning them separately.</p>`,
      tag: "Insurance — an SHM illustration"
    },
    {
      q: "<p><b>Another outline question.</b> A solid sphere and a hollow sphere of the same mass and radius are released from rest at the top of the same slope and roll without slipping. Which reaches the bottom first?</p><p>A) The solid sphere &nbsp; B) The hollow sphere &nbsp; C) They arrive together &nbsp; D) Depends on the slope angle &nbsp; E) Depends on the mass</p>",
      sol: `<p>Both spheres have the same gravitational potential energy to convert. The difference is how that energy is divided between translational and rotational kinetic energy.</p>
<p>For rolling without slipping, <code>E_total = ½mv² + ½Iω²</code>. A <b>hollow</b> sphere has all its mass at the maximum distance from the axis, so its moment of inertia is larger — its rotational kinetic energy is a bigger share of the total, leaving less for translation, so its linear speed is lower.</p>
<p><b>Answer: A, the solid sphere.</b></p>
<p><b>The reasoning in one sentence.</b> A larger moment of inertia means more of the available energy goes into spinning and less into moving, so the object rolls more slowly down the slope. This is why a solid sphere beats a hollow one, and why a solid cylinder beats a hollow pipe.</p>
<p><b>What is worth taking from this.</b> Not the algebra — BPhO would supply the moments of inertia. The point is the <i>qualitative</i> reasoning: the total kinetic energy splits between two forms, and the split depends on the shape. If a question in this area appears, that is the idea it will be testing.</p>
<p><b>Why options D and E are wrong.</b> The result is independent of the slope angle and of the mass and radius — only the <i>shape</i> matters. That is a robust and slightly surprising result, and it is the kind of thing a competition question likes.</p>`,
      tag: "Insurance — rotational energy illustration"
    }
  ],

  traps: [
    "Starting this module before modules A, H and B are genuinely finished. That is the only real trap here.",
    "Being misled by Chinese preparation portals into studying fields. The official scope statement excludes them.",
    "Confusing orbital ratios via <code>mv²/r = mg</code> (in scope, module D8) with gravitational field theory (out of scope).",
    "Assuming the period of a simple harmonic oscillator depends on its amplitude. It does not.",
    "Forgetting that a rolling body has both translational and rotational kinetic energy."
  ],

  checklist: [
    { id: "N1", flag: "R1-ONLY", text: "Simple harmonic motion: <code>a = −ω²x</code>, <code>x = A cos ωt</code>, <code>v_max = ωA</code>, mass–spring <code>T = 2π√(m/k)</code>, pendulum <code>T = 2π√(ℓ/g)</code>, resonance and damping." },
    { id: "N2", flag: "R1-ONLY", text: "Rotational dynamics: rotational kinetic energy <code>½Iω²</code>, angular momentum, and the translational-rotational energy split for a rolling body." },
    { id: "N3", flag: "R1-ONLY", text: "Electric fields — Coulomb's law, uniform field <code>E = V/d</code>, field lines, potential. <b>Officially excluded from Round 0.</b>" },
    { id: "N4", flag: "R1-ONLY", text: "Magnetic fields — <code>F = BIL</code>, <code>F = Bqv</code>, induction, Lenz's law, transformers. <b>Officially excluded from Round 0.</b>" },
    { id: "N5", flag: "R1-ONLY", text: "Gravitational fields — <code>F = GMm/r²</code>, field strength, potential, escape velocity. <b>Officially excluded from Round 0.</b>" },
    { id: "N6", flag: "R1-ONLY", text: "Particle physics — quarks, hadrons, leptons, conservation laws, strangeness. <b>Officially excluded from Round 0.</b>" },
    { id: "N7", flag: "R1-ONLY", text: "Relativity — time dilation, length contraction, relativistic momentum and energy. Beyond Round 0." },
    { id: "N8", flag: "R1-ONLY", text: "Astrophysics — magnitudes, Hubble's law, stellar evolution, the solar constant. Round 1 Section 2 territory." }
  ]
}

]);
