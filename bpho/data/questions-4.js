/* BPhO Round 0 — the 2025 past paper, rebuilt 2026-09-17.
   This is the only real Round 0 paper in existence, so it is the single best guide to what the
   exam actually asks: 25 single-answer MCQs, 60 minutes, no calculator, no negative marking.

   Every one of the 25 answers below has been checked against the official answer key printed on
   page 10 of the paper, and every worked solution states its letter explicitly. `rel` lists the
   modules and topics each question actually draws on, so the site can surface the topics that
   really come up. Each question carries `paper:"R0-2025"` so
   `startMockPaper("R0-2025", mode)` can assemble them in paper order.

   `key` names the key points each question turns on; the lessons behind them live in
   data/concepts.js. Each has a full lesson in tools/paper2025/concepts_a/b/c.py.

   Diagrams are inline SVG generated from computed geometry (angles from Snell's law, node
   positions from the printed figure) rather than traced by hand. */

window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || []).concat([

/* ===================== 2025 Round 0 past paper ===================== */
/* Answer key as printed:  E C C B C B C E A A | A A D D B B E A C D | A A B A E  */

{
  id: "R0-01", module: "E", topic: "Work done stretching a wire", diff: 1, paper: "R0-2025",
  rel: [
    ["E", "Elastic strain energy: ½ × stress × strain × volume"],
    ["E", "Stress, strain and the Young modulus"],
    ["A", "Using units to eliminate options"]
  ],
  key: ["stressstrain", "strainenergy", "units-elim"],
  q: `<p>A uniform elastic wire of length <code>L</code> and cross-section <code>A</code> is subject to a tensile stress <code>σ</code>, which results in a tensile strain <code>ε</code>. Find the work done on the wire.</p>`,
  opts: [`LAσε`, `σA / (εL)`, `σL / (2εA)`, `εA / (σL)`, `½LAσε`],
  ans: 4,
  sol: `<p><b>What is being tested.</b> The factor of ½ in stored energy — where it comes from, and whether you check units before choosing between two options that differ by nothing else.</p>
<p><b>Step 1 — turn stress and strain into force and extension.</b> The definitions do the work for you:</p>
<div class="formula">σ = F / A   ⇒   F = σA          (the force on the wire)
ε = ΔL / L  ⇒   ΔL = εL         (how far it stretches)</div>
<p><b>Step 2 — the work done is the area under the force–extension graph.</b> A wire obeying Hooke's law does not jump to its full load: the force rises from zero to <code>σA</code> exactly in step with the extension growing from zero to <code>εL</code>. The graph is therefore a triangle, and the work done is its area:</p>
<div class="formula">W = ½ × base × height = ½ × (εL) × (σA) = ½ LAσε</div>
<p><b>Step 3 — the same answer from energy density, as a cross-check.</b> The strain energy stored per unit volume is <code>½σε</code>; multiply by the volume <code>AL</code> and you recover <code>½LAσε</code>. Two independent routes, one answer.</p>
<figure class="fig">
<svg viewBox="0 0 480 246" role="img" aria-label="A force against extension graph: a straight line from the origin up to the point where the force is sigma A and the extension is epsilon L, with the triangular area beneath it shaded.">
<defs>
<marker id="f1-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f1-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f1-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f1-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f1-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="70" y1="196" x2="392" y2="196" stroke="#14181f" stroke-width="1.8" marker-end="url(#f1-ar)"/>
<line x1="70" y1="196" x2="70" y2="34" stroke="#14181f" stroke-width="1.8" marker-end="url(#f1-ar)"/>
<polygon points="70,196 392,62 392,196" fill="#e8eefc" stroke="#2f5fd0" stroke-width="2.2"/>
<line x1="70" y1="62" x2="392" y2="62" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="5 4"/>
<text x="62" y="66" text-anchor="end" font-size="12.5" font-weight="600" fill="#b3352f">σA</text>
<text x="62" y="200" text-anchor="end" font-size="12.5" fill="#7b8494">0</text>
<text x="392" y="214" text-anchor="middle" font-size="12.5" font-weight="600" fill="#b3352f">εL</text>
<text x="62" y="28" text-anchor="end" font-size="12" font-style="italic" fill="#4a5262">force</text>
<text x="400" y="230" text-anchor="end" font-size="12" font-style="italic" fill="#4a5262">extension</text>
<text x="231" y="139" text-anchor="middle" font-size="13" font-weight="600" fill="#2f5fd0">area = ½ · σA · εL</text>
</svg>
<figcaption><b>The force rises in step with the extension.</b> Because the wire behaves elastically, the force grows linearly from zero to <code>σA</code> as the extension grows from zero to <code>εL</code>, so the work done is the shaded triangle — not the rectangle you would get if the full force were applied throughout.</figcaption>
</figure>
<p><b>Answer: E, ½LAσε.</b></p>
<p><b>Why the other four are wrong.</b> Option A is the same product with the ½ thrown away: <code>LAσε</code> is the work you would do if the wire took its full load from the first instant and never resisted gradually — which is precisely what an elastic body does not do. The other three are not energies at all. B, <code>σA/(εL)</code>, has the units of <code>N m⁻¹</code> — a stiffness. C, <code>σL/(2εA)</code>, has <code>N m⁻³</code>. D, <code>εA/(σL)</code>, has <code>m³ N⁻¹</code>. None of those is a joule.</p>
<p><b>Do it the fast way.</b> You never need the ½ versus no-½ decision to be a coin toss. Check the limiting case <code>ε → 0</code>: with no stretch, no work has been done, so the answer must vanish. B does the opposite — it diverges — and dies immediately. Then A and E are the only survivors, and the triangle versus rectangle argument settles them.</p>
<p><b>The wider point.</b> The ½ keeps appearing wherever two quantities grow together from zero: <code>½kx²</code>, <code>½mv²</code>, <code>½QV</code>, <code>½CV²</code>, and here <code>½σε</code> per unit volume. Any stored-energy expression with no ½ still on the table deserves a second look.</p>
<p><b>Relevant topics:</b> strain energy; stress and strain; dimensional checking.</p>`,
  trap: "Picking <code>LAσε</code> and dropping the ½. The energy stored in a gradually loaded elastic wire is half the final force times the final extension."
},

{
  id: "R0-02", module: "G", topic: "Snell's law with angles measured from the surface", diff: 1, paper: "R0-2025",
  rel: [
    ["G", "Refraction and Snell's law"],
    ["G", "Refractive index and the normal"],
    ["A", "Reading the diagram before quoting a formula"]
  ],
  key: ["refractive", "snell", "readdiagram", "nocalc"],
  q: `<p>The diagram below shows the refraction of a light ray travelling from a medium with refractive index <code>n₁</code> into a medium with refractive index <code>n₂</code>. Which equation relates the angles <code>θ₁</code> and <code>θ₂</code>?</p><figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="A ray crossing a horizontal boundary between medium n1 above and n2 below, drawn with both angles marked between the ray and the boundary surface rather than between the ray and the normal.">
<defs>
<marker id="f2-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f2-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f2-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f2-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f2-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="40" y1="170.0" x2="452" y2="170.0" stroke="#14181f" stroke-width="2"/>
<line x1="178.0" y1="62.6" x2="240.0" y2="170.0" stroke="#2f5fd0" stroke-width="2.6" marker-end="url(#f2-arA)"/>
<line x1="240.0" y1="170.0" x2="352.5" y2="269.2" stroke="#2f5fd0" stroke-width="2.6" marker-end="url(#f2-arA)"/>
<path d="M174.0,170.0 A66.0,66.0 0 0 1 207.0,112.8" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<path d="M306.0,170.0 A66.0,66.0 0 0 0 289.5,213.7" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<text x="165" y="123" text-anchor="middle" font-size="14" font-style="italic" font-weight="600" fill="#b3352f">θ₁</text>
<text x="324" y="222" text-anchor="middle" font-size="14" font-style="italic" font-weight="600" fill="#b3352f">θ₂</text>
<text x="118" y="154" text-anchor="middle" font-size="13.5" font-style="italic" fill="#14181f">n₁</text>
<text x="118" y="198" text-anchor="middle" font-size="13.5" font-style="italic" fill="#14181f">n₂</text>
<text x="300" y="156" text-anchor="middle" font-size="11.5" fill="#7b8494">surface</text>
</svg>
<figcaption><b>θ₁ and θ₂ are measured from the <i>surface</i>, not from the normal.</b> Drawn to scale for <code>n₁ = 1.5</code>, <code>n₂ = 1</code> and <code>θ₁ = 60°</code>. <code>θ₂</code> is drawn to scale but left unnumbered: this paper is non-calculator and no option asks for its value. All you need from the sketch is the <i>comparison</i> — <code>θ₂ &lt; θ₁</code>, so the ray meets the surface more steeply and has bent <i>away</i> from the normal on leaving the denser medium.</figcaption>
</figure>`,
  opts: [`n₁ sin θ₁ = n₂ sin θ₂`, `n₁ sin θ₂ = n₂ sin θ₁`, `n₁ cos θ₁ = n₂ cos θ₂`, `n₁ cos θ₂ = n₂ cos θ₁`, `n₁ sin θ₁ = n₂ cos θ₂`],
  ans: 2,
  sol: `<p><b>The whole question is in the diagram.</b> In this figure the two angles are drawn between each ray and the <b>surface</b>, not between each ray and the normal. Every textbook writes Snell's law in the normal form, and quoting it from memory is what makes this question catch people: option A is the formula you have written a hundred times, applied to angles that are not the ones it belongs to.</p>
<p><b>Convert, then use Snell.</b> Let <code>i</code> and <code>r</code> be the angles to the normal. Since the normal is perpendicular to the surface,</p>
<div class="formula">i = 90° − θ₁          r = 90° − θ₂
n₁ sin i = n₂ sin r
n₁ sin(90° − θ₁) = n₂ sin(90° − θ₂)
n₁ cos θ₁ = n₂ cos θ₂</div>
<p><b>Answer: C, n₁ cos θ₁ = n₂ cos θ₂.</b></p>
<p><b>Check it against a case you know.</b> The figure is drawn for <code>n₁ = 1.5</code> and <code>n₂ = 1</code> with <code>θ₁ = 60°</code>. Then <code>cos θ₂ = 1.5 × cos 60° = 0.75</code> — and <b>stop there</b>. You do not need θ₂ itself: “41.4°” is a number no one can produce without a calculator, and nothing in this question asks for it. What you need is only whether θ₂ is larger or smaller than θ₁, which <code>cos θ₂ = 0.75 &gt; cos 60° = 0.5</code> answers immediately: cos θ₂ is bigger, so θ₂ is the smaller angle, so the ray bent away from the normal. (Snell in the normal form says the same thing: <code>1.5 sin 30° = 0.75 = 1 × sin θ₂′</code> where θ₂′ = 48.6° from the normal — again a number you never have to write down.) The ray leaves the glass at a smaller angle to the surface, bending away from the normal — exactly as light does on the way out of a denser medium.</p>
<p><b>The limiting case that kills A.</b> Slide the incident ray down until it travels along the interface: <code>θ₁ → 90°</code>. In this picture that means the ray is travelling parallel to the boundary, and it should keep travelling parallel to it — nothing in the problem singles out either side. Option C gives <code>cos θ₁ → 0</code>, hence <code>cos θ₂ → 0</code>, hence <code>θ₂ → 90°</code>: still along the boundary. ✔ Option A would give <code>sin θ₂ = n₁/n₂</code>, a definite angle to the surface, so the same limiting ray would suddenly refract — nonsense.</p>
<p><b>Where the other options come from.</b> A is Snell's law with the angles to the normal — the wrong angles for this diagram. B is A with the refractive indices swapped. D is C with the indices swapped. E mixes a sine with a cosine, which no physical law does.</p>
<p><b>The transferable rule.</b> Before substituting into any standard formula, read which angle the diagram actually marks. A marked angle is a fact about the figure; a remembered formula is a fact about a different figure until you have checked the two agree.</p>
<p><b>Relevant topics:</b> refraction; Snell's law; refractive index; the small-angle and limiting-case checks.</p>`,
  trap: "Answering with the remembered <code>n₁ sin θ₁ = n₂ sin θ₂</code>. The diagram measures both angles from the surface, so the equation is <code>n₁ cos θ₁ = n₂ cos θ₂</code>."
},

{
  id: "R0-03", module: "A", topic: "Which of these is not a unit of impulse", diff: 2, paper: "R0-2025",
  rel: [
    ["A", "Base units and derived-unit reduction"],
    ["C", "Impulse = Ft = change of momentum"],
    ["A", "Dimensional consistency"]
  ],
  key: ["units", "momentum", "dimensions"],
  q: `<p>Which of these is <b>not</b> a unit of impulse?</p>
<table><tbody><tr><td><b>A</b></td><td>N s</td><td><b>B</b></td><td>W s² m⁻¹</td><td><b>C</b></td><td>Pa m³</td></tr><tr><td><b>D</b></td><td>kg m s⁻¹</td><td><b>E</b></td><td>C V s m⁻¹</td><td></td><td></td></tr></tbody></table>`,
  opts: [`N s`, `W s² m⁻¹`, `Pa m³`, `kg m s⁻¹`, `C V s m⁻¹`],
  ans: 2,
  sol: `<p><b>Read the negative.</b> Three of the five are genuine units of impulse and you are asked for the odd one out. Note that this is a “which is not” question: a slip here costs a mark you had already earned.</p>
<p><b>Fix the target.</b> Impulse is force × time, and it equals the change in momentum, so its dimensions are those of momentum:</p>
<div class="formula">[impulse] = N s = kg m s⁻¹</div>
<p><b>Reduce all five to base units.</b> Use <code>N = kg m s⁻²</code>, <code>W = J s⁻¹ = kg m² s⁻³</code>, <code>Pa = N m⁻² = kg m⁻¹ s⁻²</code>, <code>C V = J = kg m² s⁻²</code>.</p>
<div class="formula">A  N s             = kg m s⁻² · s        = kg m s⁻¹   ✔
B  W s² m⁻¹       = kg m² s⁻³ · s² · m⁻¹ = kg m s⁻¹   ✔
C  Pa m³          = kg m⁻¹ s⁻² · m³     = kg m² s⁻²   ✘  (= J)
D  kg m s⁻¹                              = kg m s⁻¹   ✔
E  C V s m⁻¹      = kg m² s⁻² · s · m⁻¹ = kg m s⁻¹   ✔</div>
<p><b>Answer: C, Pa m³</b> — which reduces to the joule. Pascal cubic metres is a unit of energy (it is the work done by a pressure pushing out a volume), not of impulse.</p>
<p><b>Why B and E look wrong but are not.</b> They are the ones that make this question worth setting. B is a watt second squared per metre: the awkwardness is only in the presentation, not in the physics. E is a coulomb volt second per metre, and since a coulomb volt <i>is</i> a joule there is nothing exotic in it either. Both collapse to <code>kg m s⁻¹</code>. There are infinitely many combinations of units that do.</p>
<p><b>The technique that settles it in fifteen seconds.</b> Do not judge a unit by how familiar it looks. Convert it. Judge it only after it is in base units, and if a candidate contains a joule (or anything that reduces to one) you know immediately that it is energy, not momentum.</p>
<p><b>Relevant topics:</b> base and derived units; impulse and momentum; dimensional consistency.</p>`,
  trap: "Rejecting <code>W s² m⁻¹</code> or <code>C V s m⁻¹</code> because they do not look like <code>N s</code>. Both reduce to <code>kg m s⁻¹</code>; it is <code>Pa m³</code> that reduces to an energy."
},

{
  id: "R0-04", module: "K", topic: "Alpha and beta accounting in a decay series", diff: 1, paper: "R0-2025",
  rel: [
    ["K", "Alpha and beta-minus decay"],
    ["K", "Conservation of mass number and charge"],
    ["K", "Decay series and the nuclear equation"]
  ],
  key: ["nuclide", "alphabeta", "decayseries"],
  q: `<p>Uranium-238 (²³⁸₉₂U) decays to lead-206 (²⁰⁶₈₂Pb) via a series of alpha and beta minus decays only. How many beta minus decays occur in total?</p>`,
  opts: [`4`, `6`, `8`, `10`, `12`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> That an alpha decay and a beta decay change the two nuclear numbers differently — and that a decay series has to balance both of them.</p>
<p><b>The two bookkeeping rules.</b> An alpha particle is a helium nucleus, so</p>
<div class="formula">alpha (α):   A → A − 4,   Z → Z − 2
beta minus (β⁻): A → A,      Z → Z + 1</div>
<p><b>Step 1 — count the alphas from the mass number.</b> Only alpha decay changes <code>A</code>, and each one removes 4:</p>
<div class="formula">ΔA = 238 − 206 = 32
number of alphas = 32 / 4 = 8</div>
<p><b>Step 2 — see where those eight alphas leave the charge.</b> Eight alphas remove <code>8 × 2 = 16</code> units of charge:</p>
<div class="formula">Z after the alphas = 92 − 16 = 76</div>
<p><b>Step 3 — close the gap with beta minus decays.</b> Lead-206 has <code>Z = 82</code>, so the series must gain <code>82 − 76 = 6</code> units of charge, and a beta minus decay is the only step here that adds one:</p>
<div class="formula">number of beta minus decays = 82 − 76 = 6</div>
<p><b>Answer: B, 6.</b></p>
<p><b>Check the whole equation.</b> Eight alphas and six beta-minuses:</p>
<div class="formula">A: 238 − 8(4) = 206            ✔
Z: 92 − 8(2) + 6(1) = 82       ✔</div>
<p>Both nuclear numbers balance, so the count is right.</p>
<p><b>Where the wrong options come from.</b> Option C, 8, is the number of alphas — the answer to a question that was not asked, and the commonest slip of all: the two numbers feel interchangeable but only one of them is 8. Options D, 10, and E, 12, come from arithmetic on the charge gap with the wrong particle: treating a beta decay as though it changed the charge by 2 (the alpha's step) gives <code>16/2 + … </code> type answers, and A, 4, is half the correct count, as if a beta decay carried two units of charge.</p>
<p><b>The wider point.</b> Every nuclear reaction balances <code>A</code> and <code>Z</code> separately. Do the two sums independently — mass number first, because only the alpha moves it, then charge — and then verify by adding both columns back up.</p>
<p><b>Relevant topics:</b> alpha and beta decay; conservation laws in nuclear decay; decay series.</p>`,
  trap: "Reporting 8, the number of alpha decays. The question asks for the beta minus decays, which the charge balance alone fixes at 6."
},

{
  id: "R0-05", module: "F", topic: "Interference at a given path difference", diff: 2, paper: "R0-2025",
  rel: [
    ["F", "Superposition and path difference"],
    ["F", "Phase difference in radians and degrees"],
    ["F", "Coherence and the two-source conditions"]
  ],
  key: ["waves", "superposition", "pathphase", "coherence", "nocalc"],
  q: `<p>Two coherent waves of equal amplitude and wavelength 1.8 m, originating from the same source, arrive at the same detector with a path difference of 7.5 m. Which of these options describes the type of interference that occurs at the detector?</p>`,
  opts: [`fully destructive`, `mostly destructive`, `mostly constructive`, `fully constructive`, `not enough information`],
  ans: 2,
  sol: `<p><b>Turn the path difference into a number of wavelengths.</b> That single step decides everything:</p>
<div class="formula">Δx / λ = 7.5 / 1.8 = 75/18 = 25/6 = 4 + 1/6 wavelengths</div>
<p><b>Do that division as a fraction, not on a calculator.</b> 7.5/1.8 = 75/18; both divide by 3, so it is 25/6, and 25/6 = 4 remainder 1, so <b>4 whole wavelengths plus 1/6</b>. The “4” is what misleads people who reach for a decimal and see 4.1667. Keeping the fraction makes the remainder obvious — and the remainder is the only part that matters. Four whole wavelengths contribute nothing — a shift of a whole wavelength is a shift of a whole cycle. What is left over is the fractional part:</p>
<div class="formula">fractional part = 1/6 of a wavelength
phase difference = 2π × 1/6 = 60°</div>
<p><b>Six degrees of a cycle is a long way from half a cycle.</b> At 60° the two waves are much more in step than out of step. The resultant amplitude is</p>
<div class="formula">2A cos(φ/2) = 2A cos 30° = 1.73A</div>
<p>against <code>2A</code> for perfect reinforcement — 87% of it. That is “mostly constructive”.</p>
<p><b>Answer: C, mostly constructive.</b></p>
<p><b>Why not fully constructive.</b> That requires the path difference to be a whole number of wavelengths, and 25/6 is not a whole number. The test that makes this quick: compare the remainder 1/6 against the midpoint 1/4. Since 1/6 &lt; 1/4 (cross-multiply: 4 &lt; 6), the shift is closer to “in step” than to “out of step” — so the answer is “mostly”, on the constructive side. No decimal needed anywhere.</p>
<p><b>Why not E, not enough information.</b> The two waves are coherent, they come from the same source, and they arrive with equal amplitude. Given the wavelength and the path difference, the phase relationship at the detector is completely determined. What is <i>not</i> determined is the absolute amplitude — you cannot say the detector reads 1.73A without knowing A — but the question asks about the type of interference, which is a question about phase, and phase is fixed.</p>
<p><b>The general rule worth carrying into the exam.</b> Work in fractions of a wavelength: a whole number gives fully constructive, a half-odd number (<code>n + ½</code>) gives fully destructive, and anything else is “mostly” whichever side of the midpoint it falls. Then convert to radians (×2π) or degrees (×360°) only if the question asks for them.</p>
<p><b>Relevant topics:</b> superposition; path and phase difference; coherence; interference conditions.</p>`,
  trap: "Turning 7.5/1.8 into 4.1667 on a calculator, rounding it to 4, and calling it fully constructive — or treating “from the same source” as a reason to doubt the information given."
},

{
  id: "R0-06", module: "H", topic: "Cheapest network of exactly 4 Ω", diff: 3, paper: "R0-2025",
  rel: [
    ["H", "Resistors in series and in parallel"],
    ["H", "Equivalent resistance of a network"],
    ["A", "Searching a small space exhaustively instead of guessing"]
  ],
  key: ["resistance", "seriesparallel", "search"],
  q: `<p>A resistor shop sells individual resistors (the stock is unlimited). The price for each resistor is as follows: 2 Ω for £3, 3 Ω for £1, 6 Ω for £3, 8 Ω for £4, 12 Ω for £2.</p><p>What is the least you would need to spend to make a combination of resistors equivalent to exactly 4 Ω?</p>`,
  opts: [`£3`, `£4`, `£5`, `£6`, `£7`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> Whether you can search a small space of possibilities systematically. The physics — series and parallel — is trivial; the mark is for being organised under time pressure.</p>
<p><b>Step 1 — find the obvious solution so you know the price you have to beat.</b> The parallel combination that everyone spots is</p>
<div class="formula">6 Ω ∥ 12 Ω = (6 × 12)/(6 + 12) = 4 Ω,  cost £3 + £2 = £5</div>
<p>So the answer is at most £5. Options D (£6) and E (£7) can be ignored from here on, and the remaining question is whether £3 or £4 can do it.</p>
<p><b>Step 2 — ask what £3 can buy, exhaustively.</b> With £3 you can buy any of these (there is no change to save, so nothing else fits):</p>
<div class="formula">one 2 Ω (£3) or one 6 Ω (£3), or three 3 Ω (£3) or one 12 Ω + one 3 Ω (£3),
plus any network you like built only from 3 Ω resistors</div>
<p>Now list what each of those can actually make:</p>
<div class="formula">one 2 Ω                      → 2 Ω
one 6 Ω                      → 6 Ω
one 12 Ω                     → 12 Ω
one 12 Ω and one 3 Ω         → 15 Ω   or   2.4 Ω
one 3 Ω                      → 3 Ω
two 3 Ω                      → 6 Ω    or   1.5 Ω
three 3 Ω (any arrangement)  → 9 Ω, 4.5 Ω, 2 Ω, 1 Ω</div>
<p>Not one of those is 4 Ω, and nesting the network differently cannot help: with n identical equal resistors the achievable values are a short, fixed list, and a lone 2 Ω, 6 Ω or 12 Ω cannot be turned into 4 Ω by itself. <b>So £3 is impossible.</b></p>
<p><b>Step 3 — hit exactly £4.</b> Buy four 3 Ω resistors for £4 and put three of them in parallel:</p>
<div class="formula">three 3 Ω in parallel: 3 / 3 = 1 Ω
in series with the fourth:  1 Ω + 3 Ω = 4 Ω,  cost 4 × £1 = £4</div>
<figure class="fig">
<svg viewBox="0 0 480 252" role="img" aria-label="A schematic: three three-ohm resistors in parallel between two rails, giving one ohm, followed in series by a single three-ohm resistor.">
<defs>
<marker id="f6-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f6-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f6-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f6-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f6-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="70" y1="58.0" x2="214" y2="58.0" stroke="#14181f" stroke-width="2"/>
<line x1="70" y1="146.0" x2="214" y2="146.0" stroke="#14181f" stroke-width="2"/>
<line x1="70" y1="58.0" x2="70" y2="146.0" stroke="#14181f" stroke-width="2"/>
<line x1="252" y1="58.0" x2="252" y2="146.0" stroke="#14181f" stroke-width="2"/>
<rect x="91.0" y="79.0" width="18" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<line x1="100.0" y1="58.0" x2="100.0" y2="79" stroke="#14181f" stroke-width="2"/>
<line x1="100.0" y1="125" x2="100.0" y2="146.0" stroke="#14181f" stroke-width="2"/>
<rect x="133.0" y="79.0" width="18" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<line x1="142.0" y1="58.0" x2="142.0" y2="79" stroke="#14181f" stroke-width="2"/>
<line x1="142.0" y1="125" x2="142.0" y2="146.0" stroke="#14181f" stroke-width="2"/>
<rect x="175.0" y="79.0" width="18" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<line x1="184.0" y1="58.0" x2="184.0" y2="79" stroke="#14181f" stroke-width="2"/>
<line x1="184.0" y1="125" x2="184.0" y2="146.0" stroke="#14181f" stroke-width="2"/>
<text x="100" y="48.0" text-anchor="middle" font-size="11.5" font-weight="600" fill="#4a5262">3 Ω</text>
<text x="142" y="48.0" text-anchor="middle" font-size="11.5" font-weight="600" fill="#4a5262">3 Ω</text>
<text x="184" y="48.0" text-anchor="middle" font-size="11.5" font-weight="600" fill="#4a5262">3 Ω</text>
<line x1="40" y1="102.0" x2="70" y2="102.0" stroke="#14181f" stroke-width="2"/>
<circle cx="40.0" cy="102.0" r="3.6" fill="#14181f"/>
<line x1="252" y1="102.0" x2="300" y2="102.0" stroke="#14181f" stroke-width="2"/>
<rect x="300.0" y="91.0" width="64" height="22" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<line x1="364" y1="102.0" x2="424" y2="102.0" stroke="#14181f" stroke-width="2"/>
<circle cx="424.0" cy="102.0" r="3.6" fill="#14181f"/>
<text x="332" y="86.0" text-anchor="middle" font-size="11.5" font-weight="600" fill="#4a5262">3 Ω</text>
<text x="142" y="180.0" text-anchor="middle" font-size="13" font-weight="600" fill="#1f7a53">three in parallel: 3/3 = 1 Ω, cost £3</text>
<text x="332" y="136.0" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f7a53">one in series: +3 Ω</text>
<text x="240" y="238" text-anchor="middle" font-size="14" font-weight="600" fill="#1f7a53">R = 1 Ω + 3 Ω = 4 Ω for £4</text>
</svg>
<figcaption><b>The winning combination.</b> Three 3 Ω resistors side by side give <code>3/3 = 1 Ω</code>; one more 3 Ω in series brings it to exactly <code>4 Ω</code>. Three of them cost £1 each, the fourth another £1.</figcaption>
</figure>
<p>There is a second £4 solution, worth seeing because it shows the same price from a different direction: buy one 12 Ω and two 3 Ω, put the 3 Ω pair in series and that across the 12 Ω —</p>
<div class="formula">12 Ω ∥ (3 Ω + 3 Ω) = 12 Ω ∥ 6 Ω = 4 Ω,  cost £2 + £1 + £1 = £4</div>
<p><b>Answer: B, £4.</b></p>
<p><b>Why the other options are wrong.</b> A, £3, is impossible — the complete list above shows it. C, £5, is the answer for anyone who stops at the first combination they think of (6 Ω ∥ 12 Ω); it is a real solution, just not the cheapest. D, £6, is what you get by building 4 Ω out of two 2 Ω resistors in series, or three 12 Ω in parallel: correct, and twice the price. E, £7, is 3 Ω + (2 Ω ∥ 2 Ω), or many other dearer versions of the same idea.</p>
<p><b>The habit that makes this safe.</b> Price first, physics second. Establish an upper bound by finding any solution, then work upward from the cheapest purchase that could possibly do the job, and eliminate. One cheap combination that must be beaten plus one exhaustive list of what the cheaper budget can buy is a complete proof — and it takes less time than hoping a cleverer network will occur to you.</p>
<p><b>Relevant topics:</b> series and parallel resistors; equivalent resistance; systematic search under time pressure.</p>`,
  trap: "Settling for £5 because <code>6 Ω ∥ 12 Ω = 4 Ω</code> springs to mind. Four 3 Ω resistors do it for £4 — three in parallel make 1 Ω, and one in series adds the other 3 Ω."
},

{
  id: "R0-07", module: "B", topic: "Relative velocity: catching up", diff: 1, paper: "R0-2025",
  rel: [
    ["B", "Relative velocity and closing speed"],
    ["B", "Motion at constant velocity: s = vt"],
    ["A", "Reading the direction of a velocity arrow"]
  ],
  key: ["kinematics", "relvel", "readdiagram"],
  q: `<p>Two particles A &amp; B travel along a straight line at a constant speed with velocities as shown in the diagram. Their initial separation is 18 m. How far does particle A travel before colliding with B?</p><figure class="fig">
<svg viewBox="0 0 480 160" role="img" aria-label="Two dots on a horizontal line, A moving right at six metres per second and B also moving right at three metres per second, with the eighteen metre gap between them marked by a dimension line.">
<defs>
<marker id="f7-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f7-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f7-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f7-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f7-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="90.0" y1="62.0" x2="218.0" y2="62.0" stroke="#14181f" stroke-width="2.4" marker-end="url(#f7-ar)"/>
<line x1="330.0" y1="62.0" x2="394.0" y2="62.0" stroke="#14181f" stroke-width="2.4" marker-end="url(#f7-ar)"/>
<circle cx="90.0" cy="62.0" r="3.6" fill="#14181f"/>
<circle cx="330.0" cy="62.0" r="3.6" fill="#14181f"/><text x="154.0" y="50.0" text-anchor="middle" font-size="13" font-weight="600" fill="#14181f">A · 6 m s⁻¹</text>
<text x="370.0" y="50.0" text-anchor="middle" font-size="13" font-weight="600" fill="#14181f">B · 3 m s⁻¹</text>
<line x1="90.0" y1="68.0" x2="90.0" y2="120.0" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="4 4"/>
<line x1="330.0" y1="68.0" x2="330.0" y2="120.0" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="4 4"/>
<line x1="90.0" y1="120.0" x2="330.0" y2="120.0" stroke="#7b8494" stroke-width="1.5" marker-start="url(#f7-dimS)" marker-end="url(#f7-dim)"/>
<text x="210.0" y="140.0" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">initial separation 18 m</text>
</svg>
<figcaption><b>Read the arrows before you reach for a formula.</b> The two velocity arrows point the same way. That single observation decides which arithmetic applies — and the diagram is the only place it is stated.</figcaption>
</figure>`,
  opts: [`18 m`, `27 m`, `36 m`, `45 m`, `54 m`],
  ans: 2,
  sol: `<p><b>Read the arrows before you do any arithmetic.</b> Both velocity arrows point the same way: A moves at 6 m s⁻¹ with B ahead of it at 3 m s⁻¹. Same direction, so the gap closes only at the difference:</p>
<div class="formula">closing speed = 6 − 3 = 3 m s⁻¹</div>
<p><b>Step 1 — time to close 18 m at 3 m s⁻¹.</b></p>
<div class="formula">t = 18 / 3 = 6 s</div>
<p><b>Step 2 — how far A travels in that time.</b> A moves at its own 6 m s⁻¹, not at the closing speed:</p>
<div class="formula">s_A = 6 × 6 = 36 m</div>
<p><b>Answer: C, 36 m.</b></p>
<p><b>Check it in one line.</b> In 6 s, B travels <code>3 × 6 = 18 m</code>. A started 18 m behind, so it must travel B's 18 m plus the 18 m gap it has to make up:</p>
<div class="formula">s_A = 18 + 18 = 36 m   ✔</div>
<p>Both routes agree, which is the point of doing the check: the second one catches an error in the first if you have mixed up which speed belongs to whom.</p>
<p><b>The trap the paper is hunting.</b> If the two particles were approaching each other, the closing speed would be <code>6 + 3 = 9 m s⁻¹</code>, the time would be <code>18/9 = 2 s</code>, and A would travel 12 m. <b>12 m is not among the options.</b> That is deliberate: it is a signal, not an accident. If your working leads to 12 m, you have read the diagram as two particles approaching, and you should go back and look at the arrowheads rather than look for your answer in the list.</p>
<p><b>Where the other options come from.</b> A, 18 m, is the distance B travels in the same 6 s (or A's own share of the initial separation). D, 45 m, and E, 54 m, are the results of using the wrong speed for A: 54 m is <code>9 m s⁻¹ × 6 s</code> — the closing speed of a head-on approach carried through the correct same-direction time — and B, 27 m, is the mean of the two speeds (4.5 m s⁻¹) sustained for the full 6 s.</p>
<p><b>The general method for a catch-up question.</b> Set up <code>v_A t = v_B t + gap</code> and solve once. For this paper that is <code>6t = 3t + 18</code>, so <code>3t = 18</code>, <code>t = 6 s</code>, then substitute back for whichever distance is asked. One equation, no simultaneous reasoning, and it never confuses the two speeds.</p>
<p><b>Relevant topics:</b> relative velocity; constant-velocity kinematics; reading a velocity diagram.</p>`,
  trap: "Adding the speeds and getting 12 m — which is not an option. The arrows show the particles travelling the same way, so the closing speed is 6 − 3 = 3 m s⁻¹."
},

{
  id: "R0-08", module: "H", topic: "Ideal voltmeter and ammeter readings", diff: 3, paper: "R0-2025",
  rel: [
    ["H", "Ideal ammeter (zero resistance) and ideal voltmeter (infinite resistance)"],
    ["H", "Series and parallel networks, emf and potential difference"],
    ["H", "Kirchhoff's laws without algebra"]
  ],
  key: ["charge", "meters", "kirchhoff"],
  q: `<p>A cell of emf <code>ε</code> (and negligible internal resistance) is connected to an ideal voltmeter, an ideal ammeter and three resistors <code>R</code> as shown below. What are the readings on the voltmeter and ammeter respectively?</p><figure class="fig">
<svg viewBox="0 0 470 288" role="img" aria-label="A circuit: a cell in series with a resistor in the top branch, a resistor from the left node to a middle node, an ammeter from that middle node to the right node, and a voltmeter from the left node to the middle node with a resistor from the middle node to the right node.">
<defs>
<marker id="f8-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f8-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f8-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f8-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f8-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="70.0" y1="60.0" x2="70.0" y2="240.0" stroke="#14181f" stroke-width="2"/>
<line x1="400.0" y1="60.0" x2="400.0" y2="240.0" stroke="#14181f" stroke-width="2"/>
<line x1="70.0" y1="60.0" x2="150" y2="60.0" stroke="#14181f" stroke-width="2"/>
<line x1="152" y1="44.0" x2="152" y2="76.0" stroke="#14181f" stroke-width="2.6"/>
<line x1="164" y1="52.0" x2="164" y2="68.0" stroke="#14181f" stroke-width="2.6"/>
<line x1="166" y1="60.0" x2="250" y2="60.0" stroke="#14181f" stroke-width="2"/>
<rect x="250.0" y="48.0" width="70" height="24" fill="#ffffff" stroke="#14181f" stroke-width="2"/><line x1="320" y1="60.0" x2="400.0" y2="60.0" stroke="#14181f" stroke-width="2"/>
<line x1="70.0" y1="140.0" x2="112" y2="140.0" stroke="#14181f" stroke-width="2"/>
<rect x="112.0" y="128.0" width="70" height="24" fill="#ffffff" stroke="#14181f" stroke-width="2"/><line x1="182" y1="140.0" x2="250.0" y2="140.0" stroke="#14181f" stroke-width="2"/>
<circle cx="302" cy="140.0" r="18" fill="#ffffff" stroke="#14181f" stroke-width="2.2"/>
<text x="302" y="145.0" text-anchor="middle" font-size="13" font-weight="600" fill="#14181f">A</text>
<line x1="320" y1="140.0" x2="400.0" y2="140.0" stroke="#14181f" stroke-width="2"/>
<line x1="250.0" y1="140.0" x2="250.0" y2="240.0" stroke="#14181f" stroke-width="2"/>
<line x1="70.0" y1="240.0" x2="152" y2="240.0" stroke="#14181f" stroke-width="2"/>
<circle cx="170" cy="240.0" r="18" fill="#ffffff" stroke="#14181f" stroke-width="2.2"/>
<text x="170" y="245.0" text-anchor="middle" font-size="13" font-weight="600" fill="#14181f">V</text>
<line x1="188" y1="240.0" x2="250.0" y2="240.0" stroke="#14181f" stroke-width="2"/>
<line x1="250.0" y1="240.0" x2="300" y2="240.0" stroke="#14181f" stroke-width="2"/>
<rect x="300.0" y="228.0" width="70" height="24" fill="#ffffff" stroke="#14181f" stroke-width="2"/><line x1="370" y1="240.0" x2="400.0" y2="240.0" stroke="#14181f" stroke-width="2"/>
<circle cx="70.0" cy="140.0" r="3.6" fill="#14181f"/>
<circle cx="70.0" cy="240.0" r="3.6" fill="#14181f"/>
<circle cx="250.0" cy="140.0" r="3.6" fill="#14181f"/>
<circle cx="250.0" cy="240.0" r="3.6" fill="#14181f"/>
<circle cx="400.0" cy="60.0" r="3.6" fill="#14181f"/>
<circle cx="400.0" cy="140.0" r="3.6" fill="#14181f"/>
<circle cx="400.0" cy="240.0" r="3.6" fill="#14181f"/>
<text x="158" y="34.0" font-size="14" font-style="italic" font-weight="600" fill="#14181f">ε</text>
<text x="285" y="42.0" text-anchor="middle" font-size="13.5" font-style="italic" fill="#14181f">R</text>
<text x="147" y="122.0" text-anchor="middle" font-size="13.5" font-style="italic" fill="#14181f">R</text>
<text x="335" y="222.0" text-anchor="middle" font-size="13.5" font-style="italic" fill="#14181f">R</text>
</svg>
<figcaption><b>The circuit as printed.</b> Five components, two of them meters. Before you write anything down, decide what an <i>ideal</i> ammeter and an <i>ideal</i> voltmeter each do to the branch they sit in.</figcaption>
</figure>`,
  opts: [`ε/3 , ε/(3R)`, `ε/3 , ε/(2R)`, `ε/3 , ε/R`, `ε/2 , ε/(3R)`, `ε/2 , ε/(2R)`],
  ans: 4,
  sol: `<p><b>What is being tested.</b> Whether you know what “ideal” means for each meter — and whether you can then see that two of the five drawn components are doing nothing at all.</p>
<p><b>Step 1 — let the meters simplify the circuit for you.</b></p>
<div class="formula">ideal ammeter:   resistance 0    ⇒ the branch it sits in is a short circuit
ideal voltmeter: resistance ∞    ⇒ the branch it sits in carries no current</div>
<p>The ammeter is in parallel with the bottom resistor, so that resistor has zero potential difference across it and carries no current. The voltmeter is in series in the bottom-left lead, so that lead carries no current either — and since it carries none, the junction it connects to is not fed from there. What survives is a single loop:</p>
<div class="formula">cell ε → top resistor R → right-hand node
right-hand node → (ammeter, 0 Ω) → middle node → middle resistor R → left-hand node → back to the cell</div>
<p><b>Step 2 — the loop.</b> Two resistors of <code>R</code> in series with the cell, so the total resistance is <code>2R</code> and the current is</p>
<div class="formula">I = ε / (2R)</div>
<p>Every element in that loop carries this same current, the ammeter included. So:</p>
<div class="formula">ammeter reading = I = ε / (2R)</div>
<p><b>Step 3 — the voltmeter.</b> It is connected across the middle resistor, whose resistance is <code>R</code> and whose current is <code>I</code>:</p>
<div class="formula">V = I R = (ε / 2R) × R = ε / 2</div>
<p><b>Answer: E — voltmeter ε/2, ammeter ε/(2R).</b></p>
<p><b>Cross-check by potential.</b> The cell lifts the potential by <code>ε</code>; the two equal resistors in the loop divide it equally, so each takes <code>ε/2</code>. The voltmeter spans one of them and reads <code>ε/2</code>. The bottom resistor, with no current, takes no share of the potential difference at all — which is exactly why it can be ignored.</p>
<p><b>Why the other options fail.</b> A, B and C all quote a current of <code>ε/(2R)</code> or <code>ε/R</code> paired with a voltmeter reading of <code>ε/3</code>. That <code>ε/3</code> comes from treating all three resistors as carrying the loop current and sharing the emf in three equal parts — which cannot happen, because the ammeter's zero resistance takes the bottom resistor out of the circuit. C and D pair a current with a voltage that belong to different assumptions about the network, and A assumes a total resistance of <code>3R</code>, i.e. the naive “three resistors in series”.</p>
<p><b>The habit to take away.</b> In any question with a meter drawn on it, ask two questions before you do anything else: which branch has <i>zero</i> resistance (that resistor is shorted out), and which branch has <i>infinite</i> resistance (that resistor carries nothing). Most “impossible” circuit questions in Round 0 are two-component questions wearing three resistors.</p>
<p><b>Relevant topics:</b> ideal meters; series and parallel networks; emf and potential difference; node reasoning.</p>`,
  trap: "Using all three resistors and reading a total resistance of 3R. The ideal ammeter short-circuits the resistor beside it, so the cell drives current through two resistors, not three."
},

{
  id: "R0-09", module: "F", topic: "First-harmonic frequency against resistance", diff: 3, paper: "R0-2025",
  rel: [
    ["F", "Standing waves: f = (1/2L)√(T/μ)"],
    ["F", "Mass per unit length μ = ρA"],
    ["H", "Resistance of a uniform wire R = ρL/A"],
    ["A", "Ratio reasoning — the shared constants cancel"]
  ],
  key: ["standingwaves", "lineardensity", "resistivity", "ratio"],
  q: `<p>Two uniform metal wires of the same length are made from the same material. Separately, the wires are subject to the same force on both ends, and the first harmonic frequency of each is measured. The frequencies are in the ratio 2 : 1. What is the ratio of their electrical resistances?</p><p><i>[Hint: the speed of a transverse wave on a string is v = √(T/μ).]</i></p>`,
  opts: [`4 : 1`, `3 : 1`, `√3 : 1`, `2 : 1`, `√2 : 1`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> A two-step chain of proportionality — waves, through density, to electrical resistance — where every shared constant cancels, so you never need a value.</p>
<p><b>Step 1 — write the frequency in terms of the wire's geometry.</b> The first harmonic on a string fixed at both ends has half a wavelength along the wire, so</p>
<div class="formula">f = v / (2L),  v = √(T/μ),  μ = ρA

  ⇒  f = (1 / 2L) √( T / (ρA) )</div>
<p><b>Step 2 — keep only what differs.</b> The two wires share the length <code>L</code>, the tension <code>T</code>, the material (so <code>ρ</code> is the same) and the working frequency formula. Everything cancels except the cross-section:</p>
<div class="formula">f ∝ 1 / √A       ⇒       A ∝ 1 / f²</div>
<p><b>Step 3 — the frequency ratio becomes an area ratio.</b> With <code>f₁ : f₂ = 2 : 1</code>:</p>
<div class="formula">A₁ / A₂ = (1/f₁²) / (1/f₂²) = (f₂ / f₁)² = (1/2)² = 1/4</div>
<p>So wire 2 has four times the cross-sectional area of wire 1. The wire that sounds the higher note is the thinner one.</p>
<p><b>Step 4 — convert area into electrical resistance.</b> For a uniform wire of resistivity <code>ρ_e</code>,</p>
<div class="formula">R = ρ_e L / A   ⇒   R ∝ 1 / A  (same L, same material)
R₁ / R₂ = A₂ / A₁ = 4</div>
<p><b>Answer: A, 4 : 1.</b></p>
<p><b>The physical reading.</b> Doubling the frequency means quartering the area, and a quarter of the area is four times the resistance. Thin, high-pitched, high-resistance; thick, low-pitched, low-resistance. If your answer has the thicker wire with the higher frequency, or the ratio the wrong way up, this sentence tells you so without any algebra.</p>
<p><b>Why the other options are wrong — and a one-line argument that kills them all.</b> The chain above gives <code>R ∝ f²</code>, and the frequency ratio is 2, so the resistance ratio must be <code>2² = 4</code>. Only option A is 4 (or 1/4). D, 2 : 1, is what you get by forgetting the square in <code>A ∝ 1/f²</code> — that is, by treating the wave speed as independent of the cross-section, which would make the frequencies depend on nothing at all. E, √2 : 1, comes from applying the square root at the wrong stage of the chain; B and C are combinations that cannot arise from a chain of powers of the ratio 2.</p>
<p><b>The general method.</b> When a question gives you no numbers, write the quantity you want as a product of powers of the given quantities (<code>R ∝ fⁿ</code>), and read the exponent off the algebra. Then the ratio is <code>(ratio)ⁿ</code>. Nothing needs a calculator, and a slip in the exponents shows up immediately as a ratio that is not a power of the given one.</p>
<p><b>Relevant topics:</b> standing waves and the first harmonic; wave speed on a wire; mass per unit length; resistivity; ratio reasoning.</p>`,
  trap: "Getting the ratio the wrong way up, or forgetting the square. The higher-pitched wire is thinner (f ∝ 1/√A) and thinner means more resistance, so R ∝ f² and the answer is 4 : 1."
},

{
  id: "R0-10", module: "A", topic: "Estimating the number of atoms in the Earth", diff: 2, paper: "R0-2025",
  rel: [
    ["A", "Order-of-magnitude estimation and powers of ten"],
    ["A", "Moles and Avogadro's number"],
    ["A", "Standard-form arithmetic without a calculator"]
  ],
  key: ["stdform", "estimate", "moles"],
  q: `<p>Estimate the number of atoms which make up the Earth.</p>`,
  opts: [`10⁵⁰`, `10⁵⁵`, `10⁶⁰`, `10⁶⁵`, `10⁷⁰`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> Whether you can turn a fact you know (the mass of the Earth) plus a fact you can make (the mass of a typical atom) into an order of magnitude — and whether you resist the urge to look for a calculator you are not allowed to have.</p>
<p><b>Step 1 — the mass of the Earth.</b> This is worth knowing as an anchor: <code>M⊕ ≈ 6 × 10²⁴ kg</code>.</p>
<p><b>Step 2 — the mass of a typical atom.</b> The Earth is mostly iron, oxygen, silicon and magnesium, so a typical nucleus has a mass number of a few tens; take <code>A ≈ 30</code>. One atomic mass unit is about <code>1.7 × 10⁻²⁷ kg</code>, so</p>
<div class="formula">m_atom ≈ 30 × 1.7 × 10⁻²⁷ kg ≈ 5 × 10⁻²⁶ kg</div>
<p><b>Step 3 — divide.</b></p>
<div class="formula">N = M / m_atom = (6 × 10²⁴) / (5 × 10⁻²⁶)
  = (6/5) × 10⁵⁰
  ≈ 1.2 × 10⁵⁰</div>
<p><b>Answer: A, about 10⁵⁰ atoms.</b></p>
<p><b>The same estimate through moles, which is faster if you are comfortable with Avogadro.</b> A mole of typical rock weighs about 30 g, so 1 kg of rock contains roughly <code>6 × 10²³ / 0.03 ≈ 2 × 10²⁵</code> atoms. Multiply by the mass of the Earth:</p>
<div class="formula">N ≈ (6 × 10²⁴ kg) × (2 × 10²⁵ atoms kg⁻¹) ≈ 1.2 × 10⁵⁰</div>
<p><b>Carry this anchor:</b> a kilogram of ordinary rock contains of order <code>10²⁵</code> atoms. It converts a hard question into one multiplication.</p>
<p><b>Why the answer does not depend on the composition.</b> Suppose the Earth were pure iron, <code>A = 56</code>: then <code>N ≈ 6.4 × 10⁴⁹</code>. Suppose it were pure oxygen, <code>A = 16</code>: <code>N ≈ 2.2 × 10⁵⁰</code>. Both are <code>10⁵⁰</code> to the nearest power of ten. The options differ by factors of <code>10⁵</code>, so an estimate good to within a factor of a hundred is easily enough — you are choosing between <code>10⁵⁰</code> and <code>10⁵⁵</code>, not between 1.2 and 1.3.</p>
<p><b>Where the other options come from.</b> <code>10⁵⁵</code> and beyond require an error of several orders of magnitude — the usual source is mishandling the atomic mass. Using the mass of a single nucleon (<code>1.7 × 10⁻²⁷ kg</code>) instead of an atom still lands you at <code>4 × 10⁵¹</code>, which is still nearest to <code>10⁵⁰</code>: that is the point about robustness. Only a slip in the exponents — writing the atomic mass as <code>10⁻²² kg</code>, say, or losing the <code>10²³</code> in Avogadro and treating it as <code>10²⁰</code> — gets you to <code>10⁵⁵</code> or beyond.</p>
<p><b>The technique.</b> In an estimation question, collect the powers of ten first and the leading digits second. Do not tidy up. <code>(6 × 10²⁴)/(5 × 10⁻²⁶)</code> is <code>(6/5) × 10⁵⁰</code> and that is already an answer to the precision the options demand.</p>
<p><b>Relevant topics:</b> estimation; Avogadro and the mole; standard form; rounding to an order of magnitude.</p>`,
  trap: "Reaching for a calculator — which is not permitted. The options are five powers of ten apart, so all the question wants is the exponent, and that comes from (6 × 10²⁴)/(5 × 10⁻²⁶)."
},

{
  id: "R0-11", module: "L", topic: "Counting the possible photon energies", diff: 2, paper: "R0-2025",
  rel: [
    ["L", "Energy levels and photon emission"],
    ["L", "hf = E₁ − E₂ for a transition"],
    ["A", "Counting combinations instead of listing them"]
  ],
  key: ["photons", "levels", "counting"],
  q: `<p>The first ten energy levels of an atom are labelled <code>n = 1, 2, …, 10</code>. Assuming all transitions are possible, find the maximum number of unique photon energies corresponding to transitions between <code>n = 10</code> and <code>n = 1</code>.</p>`,
  opts: [`45`, `55`, `90`, `100`, `110`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> Whether you can see that this is a counting question in disguise. There is no physics beyond <code>hf = E₁ − E₂</code>; the mark is for setting the count up correctly and not double-counting.</p>
<p><b>Step 1 — one photon per pair of levels.</b> The atom emits a photon when it drops from a higher level to a lower one, and the photon energy is fixed by which two levels are involved:</p>
<div class="formula">hf = E_upper − E_lower</div>
<p>So every pair of distinct levels contributes one possible photon energy. A pair, not an ordered pair: the transition from <code>n = 5</code> down to <code>n = 2</code> and the transition from <code>n = 2</code> up to <code>n = 5</code> describe the same energy gap, and only the downward one emits.</p>
<p><b>Step 2 — count the pairs.</b> With ten levels there are</p>
<div class="formula">C(10, 2) = 10 × 9 / 2 = 45</div>
<p>ways of choosing two distinct levels.</p>
<p><b>Answer: A, 45.</b></p>
<p><b>Where the word “maximum” comes from.</b> In a real atom two different pairs can happen to have the same energy gap, and then two transitions produce identical photons and the count of <i>unique</i> energies is smaller. The question says “maximum”, which tells you to assume no such coincidences: 45 is the largest the count can be, achieved when all 45 gaps are different.</p>
<p><b>Where the wrong options come from — and how to catch them.</b> All four of the others are products that count something slightly different:</p>
<div class="formula">100 = 10 × 10   ordered pairs including a level with itself (no transition)
 90 = 10 × 9     ordered pairs — each gap counted twice, once each way
110 = 11 × 10    ordered pairs across eleven levels
 55 = 11 × 10 / 2 the unbiased pair count, but with eleven levels instead of ten</div>
<p><b>Answer: A, 45.</b></p>
<p><b>The check that takes two seconds.</b> Whatever method you use, try it on three levels. Three levels give three pairs — 3→2, 3→1, 2→1 — so the formula must produce 3 when <code>n = 3</code>. <code>n(n−1)/2 = 3</code> ✔; <code>n² = 9</code> ✘; <code>n(n−1) = 6</code> ✘. Counting formulae are easy to verify on a tiny case and almost impossible to check by staring at them.</p>
<p><b>Relevant topics:</b> energy levels and photon energies; the transition rule; combinations and counting.</p>`,
  trap: "Counting ordered pairs (90) or pairs including a level with itself (100). A photon energy belongs to an unordered pair of distinct levels: C(10,2) = 45."
},

{
  id: "R0-12", module: "C", topic: "How the energy of an explosion is shared", diff: 3, paper: "R0-2025",
  rel: [
    ["C", "Conservation of momentum in an explosion"],
    ["C", "Kinetic energy written as p²/2m"],
    ["A", "Testing an algebraic answer on limiting cases"]
  ],
  key: ["momcons", "ke", "limits"],
  q: `<p>A body, initially at rest, explodes into two fragments of masses <code>m</code> and <code>am</code> where <code>a &gt; 1</code>. The total kinetic energy after the explosion is <code>E</code>. Find the kinetic energy of the larger mass.</p>`,
  opts: [`E/(1 + a)`, `aE/(1 + a²)`, `a²E/(1 + a²)`, `a³E/(1 + a³)`, `E/a`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> The consequence of momentum conservation in an explosion — and the discipline to test an algebraic answer rather than trust it.</p>
<p><b>Step 1 — the momenta are equal and opposite.</b> The body started at rest, so the total momentum is zero before and after. Call the speed of the smaller fragment <code>v₁</code> and of the larger <code>v₂</code>:</p>
<div class="formula">m v₁ = (am) v₂        ⇒        v₁ = a v₂</div>
<p>The lighter fragment is the faster one, by exactly the mass ratio.</p>
<p><b>Step 2 — write both kinetic energies through the shared momentum.</b> This is the step that makes the algebra clean. Both fragments carry the same magnitude of momentum, <code>p</code>, so use <code>KE = p²/2m</code>:</p>
<div class="formula">KE(small) = p² / (2m)
KE(large) = p² / (2am)</div>
<p>Same <code>p</code>, twice the mass, so the larger fragment takes the <i>smaller</i> share of the energy.</p>
<p><b>Step 3 — total, then ratio.</b></p>
<div class="formula">E = p²/(2m) + p²/(2am) = (p²/2m)(1 + 1/a) = (p²/2m) · (a + 1)/a</div>
<p>Divide the kinetic energy of the larger mass by the total:</p>
<div class="formula">KE(large) / E = [p²/(2am)] / [ (p²/2m)(a+1)/a ]
              = [1/(am)] × [am/(a+1)]
              = 1/(a + 1)</div>
<p><b>Answer: A, KE(larger) = E/(1 + a).</b></p>
<p><b>Test it the way you should test every algebraic answer — on the ends.</b></p>
<div class="formula">a → 1:  the masses are equal, so the energy splits equally.
        E/(1 + a) → E/2   ✔
a → ∞:  the big fragment is infinitely heavy, so it barely moves and
        takes almost no kinetic energy.  E/(1 + a) → 0   ✔</div>
<p>Both limits are right, and they already kill two options outright. Option C gives <code>E</code> as <code>a → ∞</code> — all the energy in the heaviest fragment, which is exactly backwards. Option D does the same. Option E, <code>E/a</code>, gives <code>E</code> at <code>a = 1</code>, where equal masses must split the energy equally: dead.</p>
<p><b>One numerical case to separate the last two.</b> The <code>a → 1</code> limit does not distinguish A from B, because <code>a/(1 + a²) → 1/2</code> as well. Put <code>a = 2</code>: masses <code>m</code> and <code>2m</code>, so <code>v₁ = 2v₂</code>, and the kinetic energies go as <code>m(2v)² = 4mv²</code> for the light one and <code>2m v²</code> for the heavy one — a 2:1 split, with the heavy fragment taking one third:</p>
<div class="formula">A:  E/(1 + 2) = E/3 = 0.333E        ✔
B:  2E/(1 + 4) = 0.400E            ✘</div>
<p><b>Answer: A.</b></p>
<p><b>The physical reading worth keeping.</b> Momentum is shared; energy is not. Two fragments of unequal mass fly apart with equal and opposite momenta, and because <code>KE = p²/2m</code>, the <i>lighter</i> fragment carries most of the kinetic energy. At <code>a = 2</code> the light fragment gets two thirds. Option B, <code>aE/(1+a²)</code>, is the value you get by assuming the energy is shared in proportion to mass — the misconception the question is built to detect.</p>
<p><b>Relevant topics:</b> momentum conservation in an explosion; kinetic energy in terms of momentum; limiting-case testing.</p>`,
  trap: "Assuming the heavier fragment takes the larger share of the energy. Equal momenta and <code>KE = p²/2m</code> mean the heavier one takes <code>E/(1+a)</code> — less than half."
},

{
  id: "R0-13", module: "A", topic: "Casimir pressure by dimensions", diff: 2, paper: "R0-2025",
  rel: [
    ["A", "Dimensional analysis: forming a product from the given quantities"],
    ["A", "The dimensions of h, c and pressure"],
    ["L", "Quantum effects and the Casimir effect"]
  ],
  key: ["dimensions", "casimir"],
  q: `<p>The pressure <code>p</code> exerted on two closely spaced parallel plates due to quantum effects is dependent only upon Planck's constant <code>h</code>, the speed of light <code>c</code> and the plate separation <code>r</code>. Find the proportionality relation between <code>p</code> and <code>r</code>.</p>`,
  opts: [`p ∝ 1/r`, `p ∝ 1/r²`, `p ∝ 1/r³`, `p ∝ 1/r⁴`, `p ∝ 1/r⁵`],
  ans: 3,
  sol: `<p><b>What is being tested.</b> Pure dimensional analysis — “dependent only upon” is the instruction to ignore the physics and match dimensions. AQA does not examine this, so it is cheap BPhO-specific marks.</p>
<p><b>Step 1 — write the dimensions of everything involved.</b></p>
<div class="formula">pressure   [p] = N m⁻² = kg m⁻¹ s⁻²  =  M L⁻¹ T⁻²
Planck     [h] = J s    = kg m² s⁻¹   =  M L² T⁻¹
light      [c] = m s⁻¹                =  L T⁻¹
separation [r] = m                    =  L</div>
<p><b>Step 2 — assume a product form and match each base dimension.</b> Put <code>p = k h<sup>α</sup> c<sup>β</sup> r<sup>γ</sup></code> with <code>k</code> a dimensionless constant:</p>
<div class="formula">M:   α = 1
L:   2α + β + γ = −1
T:  −α − β = −2</div>
<p><b>Step 3 — solve the columns in order.</b></p>
<div class="formula">from M:      α = 1
from T:      β = 2 − α = 1
from L:      γ = −1 − 2α − β = −1 − 2 − 1 = −4</div>
<p><b>Answer: D, p ∝ 1/r⁴.</b> The full form is <code>p = k h c / r⁴</code>, and the physics adds nothing to the exponent: the real result is <code>p = π²ħc / (240 r⁴)</code>.</p>
<p><b>Why the tidy answer is the right one.</b> If you have met the Casimir effect you may know that the force falls off as <code>1/r⁴</code>; dimensional analysis has just produced it without any quantum electrodynamics. That is the point of the technique, and it is why the question can be set at all in a non-calculator paper.</p>
<p><b>Where the neighbouring options come from.</b> Every wrong option is an offspring of one sign or one term in the L equation. Writing the length dimension of pressure as <code>+1</code> instead of <code>−1</code> — a pressure is a force per area, so the area's <code>m⁻²</code> is easy to drop — gives <code>2 + 1 + γ = +1</code>, so <code>γ = −2</code>: option B. Losing the <code>2α</code> contribution of <code>h</code> gives <code>β + γ = −1</code>, so <code>γ = −2</code> again. Adding instead of subtracting the <code>hc</code> contributions gives <code>γ = −5</code>: option E. Option C is the value you get with a single exponent error, and A is essentially unforced.</p>
<p><b>The technique, stated once for the whole paper.</b> Three base dimensions means three equations, which means you can solve for three unknown exponents. Write the four rows out in full — pressure, h, c, r — solve the mass row first because it is always the shortest, then time, then length. Do not try to do it in your head: the question is worth one mark and the tableau takes twenty seconds.</p>
<p><b>Relevant topics:</b> dimensional analysis; the dimensions of h and c; the Casimir effect as a quantum pressure.</p>`,
  trap: "Getting one exponent wrong by writing the length dimension of pressure as positive. Force per area means <code>M L⁻¹ T⁻²</code>, and that <code>L⁻¹</code> is what makes the answer <code>1/r⁴</code> rather than <code>1/r²</code>."
},

{
  id: "R0-14", module: "C", topic: "How far a biscuit can be pushed before it falls", diff: 3, paper: "R0-2025",
  rel: [
    ["C", "Toppling and the centre of mass"],
    ["C", "Statics: stable equilibrium and the support condition"],
    ["A", "Geometry of intersecting circles; small-change reasoning"]
  ],
  key: ["com", "toppling", "statics", "nocalc"],
  q: `<p>A thin uniform circular biscuit of radius <code>b</code> is balanced horizontally on the thin circular rim of a teacup, which has radius <code>3b/2</code>, positioned as far as possible from the cup's centre. It is then slowly pushed inwards towards the centre of the teacup. What is the maximum distance it can be pushed before it falls?</p>`,
  opts: [`((√3 − 1)/2) b`, `((5 − √3)/5) b`, `((√5 − 2)/3) b`, `((3 − √5)/2) b`, `((√3 − 1)/3) b`],
  ans: 3,
  sol: `<p><b>What is being tested.</b> That “falling over” is a statement about the centre of mass and the shape of the support, not about how much of the biscuit is over the cup.</p>
<p><b>Step 1 — what is actually holding the biscuit up.</b> The cup's rim is a circle, not a disc, so the biscuit touches it only where the rim passes underneath: at the two points where the rim circle crosses the biscuit's edge. Call them P and Q. Those two points are the whole support, and by the standard toppling argument the biscuit stays up while its centre of mass lies inside the convex hull of the contact points — here the region bounded by the chord PQ and the arc between them.</p>
<figure class="fig">
<svg viewBox="0 0 480 268" role="img" aria-label="A large circle for the cup rim and a smaller circle for the biscuit overlapping it, with the two crossing points joined by a dashed chord, the two centres marked O and C, and the radii R and b dimensioned.">
<defs>
<marker id="f14-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f14-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f14-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f14-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f14-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<circle cx="196.0" cy="158.0" r="99.0" fill="none" stroke="#14181f" stroke-width="2.2"/>
<circle cx="295.0" cy="158.0" r="66.0" fill="#e8eefc" fill-opacity="0.55" stroke="#2f5fd0" stroke-width="2.2"/>
<line x1="273.0" y1="95.8" x2="273.0" y2="220.2" stroke="#5b3fa8" stroke-width="2.2" stroke-dasharray="6 4"/>
<circle cx="273.0" cy="95.8" r="3.4" fill="#5b3fa8"/>
<circle cx="273.0" cy="220.2" r="3.4" fill="#5b3fa8"/>
<circle cx="196.0" cy="158.0" r="4.2" fill="#14181f"/>
<circle cx="295.0" cy="158.0" r="4.2" fill="#14181f"/>
<line x1="196.0" y1="158.0" x2="97.0" y2="158.0" stroke="#7b8494" stroke-width="1.4" marker-start="url(#f14-dimS)" marker-end="url(#f14-dim)"/>
<line x1="295.0" y1="158.0" x2="361.0" y2="158.0" stroke="#7b8494" stroke-width="1.4" marker-start="url(#f14-dimS)" marker-end="url(#f14-dim)"/>
<line x1="196.0" y1="210.0" x2="295.0" y2="210.0" stroke="#2f5fd0" stroke-width="1.5" marker-start="url(#f14-dimS)" marker-end="url(#f14-dim)"/>
<line x1="196.0" y1="158.0" x2="196.0" y2="210.0" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="4 4"/>
<line x1="295.0" y1="158.0" x2="295.0" y2="210.0" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="4 4"/>
<text x="138" y="148" text-anchor="middle" font-size="12" font-weight="600" fill="#4a5262">R = 3b/2</text>
<text x="329" y="148" text-anchor="middle" font-size="12" font-weight="600" fill="#4a5262">b</text>
<text x="210" y="228" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">d = R at the start</text>
<text x="178" y="172" text-anchor="end" font-size="13.5" font-weight="600" fill="#14181f">O</text>
<text x="297" y="148" text-anchor="start" font-size="13.5" font-weight="600" fill="#2f5fd0">C</text>
<text x="283.0" y="99.8" font-size="13" font-weight="600" fill="#5b3fa8">P</text>
<text x="283.0" y="224.2" font-size="13" font-weight="600" fill="#5b3fa8">Q</text>
<text x="67" y="176" text-anchor="start" font-size="11.5" fill="#7b8494">cup rim</text>
<text x="255" y="260" text-anchor="middle" font-size="11.5" fill="#2f5fd0">biscuit</text>
</svg>
<figcaption><b>The geometry of the balance.</b> The rim (radius <code>R</code>) crosses the biscuit's edge (radius <code>b</code>) at P and Q. The biscuit stays up while its centre of mass C lies inside the segment cut off by the chord PQ — so it falls the moment C reaches that chord.</figcaption>
</figure>
<p><b>Step 2 — write that condition as a distance.</b> Let the cup's centre be O (rim radius <code>R = 3b/2</code>), the biscuit's centre of mass C (radius <code>b</code>), and <code>OC = d</code>. For two circles whose centres are <code>d</code> apart, the common chord — the line PQ — lies at distance</p>
<div class="formula">m = (d² + R² − b²) / (2d)</div>
<p>from O. The biscuit's centre of mass is at distance <code>d</code> from O, so the limiting position is</p>
<div class="formula">m = d   ⇒   d² + R² − b² = 2d²   ⇒   d² = R² − b²</div>
<p><b>Step 3 — evaluate with R = 3b/2.</b></p>
<div class="formula">d_min = √(R² − b²) = √(9b²/4 − b²) = √(5b²/4) = (√5 / 2) b ≈ 1.118 b</div>
<p><b>Step 4 — where does it start?</b> “As far as possible from the cup's centre” while still balanced means the centre of mass is over the rim itself:</p>
<div class="formula">d_start = R = 1.5 b</div>
<p>(You can check the sense of that against Step 3: <code>d_start = 1.5b &gt; d_min = 1.118b</code>, so there is room to push.)</p>
<p><b>Step 5 — subtract.</b></p>
<div class="formula">distance pushed = d_start − d_min = 1.5b − (√5/2) b = ((3 − √5)/2) b ≈ 0.382 b</div>
<p><b>Answer: D, ((3 − √5)/2) b.</b></p>
<p><b>Getting there without a calculator.</b> The options are decimals, so at the very end you do have to
turn a surd into one — but you never need long division. Recover <code>√5</code> by squaring candidates:
<code>2.2² = 4.84</code> (too small), <code>2.3² = 5.29</code> (too big), <code>2.24² = 5.018</code>
(just over), so <code>√5 ≈ 2.236</code>. Then</p>
<div class="formula">(3 − √5)/2 ≈ (3 − 2.236)/2 = 0.764/2 = 0.382</div>
<p>and 0.382 is option D. Notice what you did <i>not</i> need: <code>1.118b</code> in Step 3, any decimal
for <code>√(5)/2</code>, or a single division harder than halving 0.764.</p>
<p><b>The stronger check, which needs no number at all.</b> Square to compare instead of evaluating. The
answer must be <code>(3 − √5)/2</code>, so it must satisfy <code>√5 = 3 − 2×</code>(the answer). Test
option A, 0.366: <code>3 − 2(0.366) = 2.268</code>, and <code>2.268² = 5.14 ≠ 5</code>. Test option D,
0.382: <code>3 − 2(0.382) = 2.236</code>, and <code>2.236² = 5.00</code> ✓. Squaring settles it exactly,
and it is the technique to reach for whenever the options are decimals but the answer is a surd.</p>
<p><b>The limiting case that checks the whole derivation.</b> Make the cup exactly as wide as the biscuit: <code>R = b</code>. Then the general result gives</p>
<div class="formula">d_min = √(R² − b²) = 0,  so the push is R − 0 = b</div>
<p>A biscuit the size of the rim can be pushed a full radius off centre before it topples — it is supported until its centre reaches the rim's centre. That is clearly right, and only an expression built on <code>√(R² − b²)</code> behaves that way.</p>
<p><b>Why the other options are wrong.</b> All four are of the same shape — a surd over a small integer — so they cannot be separated by inspection. The two checks above do it: the answer must be smaller than <code>1.5b</code>, must vanish in the limit <code>b = R</code>, and evaluates at <code>0.382b</code>. Option A, 0.366b, is close enough to tempt you and comes from using <code>√3</code> in place of <code>√5</code>, i.e. from a wrong chord relation; B, 0.654b, is much too large; C, 0.079b, is much too small; E, 0.244b, sits between but fails the <code>b = R</code> test. Doing the general case first — <code>d_min = √(R² − b²)</code> before substituting — is what makes this safe, because the general form can be checked against an easy case and the specific numbers cannot.</p>
<p><b>The habit.</b> In any toppling question, ask first: what are the contact points, and what is the shape whose inside the centre of mass must lie in? A pencil on a table has one line of contact and falls at once; a box has an area and falls when its centre passes the edge; here the contact is an arc, and the answer is a chord condition. The shape of the support is the whole question.</p>
<p><b>Relevant topics:</b> toppling and the centre of mass; stable equilibrium; the geometry of intersecting circles.</p>`,
  trap: "Treating the support as the overlap area between the biscuit and the cup. The rim is a circle, so the support is the arc where the rim passes under the biscuit, and balance fails when the centre of mass reaches the chord joining those two points."
},

{
  id: "R0-15", module: "J", topic: "How many ice cubes the water can melt", diff: 2, paper: "R0-2025",
  rel: [
    ["J", "Specific heat capacity and Q = mcΔT"],
    ["J", "Specific latent heat of fusion and Q = mL"],
    ["A", "Integer answers and no-calculator arithmetic"]
  ],
  key: ["specificheat", "latentheat", "stdform"],
  q: `<p>An insulated cup contains 500 g of water at 20 °C. Identical ice cubes, each of mass 25 g and at 0 °C, are added to the cup. What is the maximum number of cubes that can be added so that, at equilibrium, the mixture is entirely liquid?</p><p>Specific heat capacity of water = 4 × 10³ J kg⁻¹ K⁻¹<br>Specific latent heat of fusion of ice = 3 × 10⁵ J kg⁻¹</p>`,
  opts: [`4`, `5`, `6`, `7`, `8`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> The two-stage thermal calculation — cool the water, melt the ice — and the discipline to keep an integer answer an integer.</p>
<p><b>Step 1 — how much energy the water can give up.</b> The best case for melting ice is that the water is cooled all the way to 0 °C:</p>
<div class="formula">Q_available = mcΔT = 0.5 kg × (4 × 10³ J kg⁻¹ K⁻¹) × 20 K
            = 4.0 × 10⁴ J</div>
<p><b>Step 2 — what one cube costs to melt.</b> Ice at 0 °C needs no warming; it only needs melting:</p>
<div class="formula">Q_per cube = mL = 0.025 kg × (3 × 10⁵ J kg⁻¹) = 7.5 × 10³ J</div>
<p><b>Step 3 — divide, then round <i>down</i>.</b></p>
<div class="formula">n_max = (4.0 × 10⁴) / (7.5 × 10³) = 5.33…</div>
<p>The mixture must be <b>entirely liquid</b> at equilibrium, so there must be no ice left. Six cubes would need <code>6 × 7.5 × 10³ = 4.5 × 10⁴ J</code>, more than the water can supply, so some ice would survive at 0 °C and the mixture would be part ice. Five cubes is the largest number that can be fully melted.</p>
<p><b>Answer: B, 5.</b></p>
<p><b>Check that the fifth cube really does melt, and what is left over.</b> Five cubes cost <code>5 × 7.5 × 10³ = 3.75 × 10⁴ J</code>, leaving</p>
<div class="formula">Q_left = 4.0 × 10⁴ − 3.75 × 10⁴ = 2.5 × 10³ J</div>
<p>The final mixture is <code>0.500 + 5 × 0.025 = 0.625 kg</code> of water, and 2.5 × 10³ J warms it by</p>
<div class="formula">ΔT = Q / (mc) = 2.5 × 10³ / (0.625 × 4 × 10³) ≈ 1 °C</div>
<p>So the cup settles at about 1 °C, all liquid, with the whole calculation consistent. That is a useful thing to notice: the paper's rounded data (<code>4 × 10³</code> rather than 4200) makes the fifth-cube case land very close to 0 °C, which is exactly what “maximum” means.</p>
<p><b>Why the other options are wrong.</b> C, 6, is the rounding error the question is built around: <code>5.33</code> rounds to 5 for a physical count, and rounding it up to 6 leaves ice floating in the cup — with the mixture then not entirely liquid, which is the condition the question set. D, 7, and E, 8, would leave several cubes of ice. A, 4, is what you get by making one of the two calculations slightly harder for yourself — for example by cooling the water only to some intermediate temperature, or by including a warming term for the melted ice when there is no energy left to do it.</p>
<p><b>The general shape of a melting-ice question.</b> Energy available: <code>m_water c ΔT</code>. Energy cost: <code>m_ice L</code> (plus <code>m_ice c ΔT</code> afterwards, if the melt-water ends above 0 °C). The limiting number of cubes comes from dividing the first by the second and rounding towards zero whenever the question insists that nothing solid is left. Watch the units in one place: the mass must be in kilograms for both formulae, and 500 g and 25 g both invite you to forget that.</p>
<p><b>Relevant topics:</b> specific heat capacity; latent heat of fusion; two-stage thermal equilibrium; integer constraints.</p>`,
  trap: "Rounding 5.33 up to 6. Six cubes need more energy than the water has, so ice would be left at 0 °C and the mixture would not be entirely liquid."
},

{
  id: "R0-16", module: "G", topic: "Time of flight through a glass cube", diff: 3, paper: "R0-2025",
  rel: [
    ["G", "Snell's law and the angle of refraction"],
    ["G", "Speed of light in a medium: v = c / n"],
    ["A", "Surds and reciprocals without a calculator"]
  ],
  key: ["snell", "lightspeed", "surds", "nocalc"],
  q: `<p>A ray of light is incident on a glass cube of side length <code>a</code> and refractive index <code>√2</code>. The angle of incidence is 30°. Find the time taken for the light to travel to the opposite face.</p>`,
  opts: [`√(8/7) · a/c`, `(4/√7) · a/c`, `(√2/3) · a/c`, `(4/√3) · a/c`, `(4/√2) · a/c`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> A three-line calculation where each line is a separate idea: refract the ray, slow it down, and measure the path — plus enough surd algebra to land on one of five similar-looking fractions.</p>
<p><b>Step 1 — find the angle inside the glass.</b> Here the 30° is the angle of incidence measured from the normal, as usual. Snell's law gives</p>
<div class="formula">n₁ sin θ₁ = n₂ sin θ₂
1 × sin 30° = √2 × sin θ₂
sin θ₂ = 0.5 / √2 = 1 / (2√2)</div>
<p><b>Do not evaluate the angle.</b> “θ₂ = 20.7°” would need a calculator and nothing here needs it: keep <code>sin θ₂ = 1/(2√2)</code> and carry it forward. All you should conclude at this point is the direction — the ray bends <i>towards</i> the normal on entering the glass, because it enters a denser medium, so <code>θ₂ &lt; 30°</code>. That single inequality is what does the work later.</p>
<p><b>Step 2 — how far it travels inside.</b> The ray enters through one face and leaves through the opposite face, a distance <code>a</code> away. Because the ray is at angle <code>θ₂</code> to the normal, the path is the hypotenuse of a right-angled triangle whose adjacent side is <code>a</code>:</p>
<div class="formula">path = a / cos θ₂</div>
<figure class="fig">
<svg viewBox="0 0 480 290" role="img" aria-label="A square glass block with a ray meeting the top face at thirty degrees to the normal, refracting to a steeper path inside the block and leaving through the bottom face, with the side labelled a.">
<defs>
<marker id="f16-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f16-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f16-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f16-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f16-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<rect x="150.0" y="84.0" width="176.0" height="176.0" fill="#e8eefc" fill-opacity="0.5" stroke="#14181f" stroke-width="2.2"/>
<line x1="238.0" y1="40.0" x2="238.0" y2="136.0" stroke="#cbd2dd" stroke-width="1.5" stroke-dasharray="6 5"/>
<line x1="200.0" y1="18.2" x2="238.0" y2="84.0" stroke="#2f5fd0" stroke-width="2.6" marker-end="url(#f16-arA)"/>
<line x1="238.0" y1="84.0" x2="304.5" y2="260.0" stroke="#2f5fd0" stroke-width="2.6" marker-end="url(#f16-arA)"/>
<path d="M238.0,38.0 A46.0,46.0 0 0 0 215.0,44.2" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<path d="M238.0,130.0 A46.0,46.0 0 0 0 254.3,127.0" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<text x="202" y="56" text-anchor="middle" font-size="12.5" font-weight="600" fill="#b3352f">30°</text>
<text x="272" y="136" text-anchor="middle" font-size="12.5" font-weight="600" fill="#b3352f">θ₂</text>
<text x="202" y="232" font-size="13.5" font-style="italic" fill="#14181f">n = √2</text>
<line x1="130.0" y1="84.0" x2="130.0" y2="260.0" stroke="#7b8494" stroke-width="1.4" marker-start="url(#f16-dimS)" marker-end="url(#f16-dim)"/>
<text x="120.0" y="177" text-anchor="end" font-size="13" font-weight="600" fill="#4a5262">a</text>
<text x="270.5" y="188" text-anchor="end" font-size="11.5" fill="#4a5262">path = a / cos θ₂</text>
<circle cx="304.5" cy="260.0" r="4" fill="#b3352f"/>
</svg>
<figcaption><b>Why the path is <code>a / cos θ₂</code>.</b> The ray enters the top face and leaves through the opposite face a distance <code>a</code> below it, so the distance it covers inside the glass is <code>a / cos θ₂</code>, at speed <code>c/√2</code>. The angle itself is left as <code>θ₂</code>: this paper is non-calculator, and <code>cos θ₂</code> is obtained exactly from <code>sin² θ₂ + cos² θ₂ = 1</code> rather than from an evaluated angle.</figcaption>
</figure>
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
<div class="formula">bounds squared:        2          &lt;  t<sup>2</sup>  &lt;  8/3 = 2.67
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
<p><b>Relevant topics:</b> Snell's law; speed of light in a medium; geometric path length; surd manipulation.</p>`,
  trap: "Using <code>v = c</code> inside the glass, or taking the path as <code>a</code> rather than <code>a/cos θ₂</code>. Both errors give <code>√(8/7)·a/c</code>, which is on the list."
},

{
  id: "R0-17", module: "L", topic: "How many photoelectrons charge the capacitor", diff: 3, paper: "R0-2025",
  rel: [
    ["L", "The photoelectric equation hf = φ + KE_max"],
    ["L", "Stopping potential: eV_s = h(f − f₀)"],
    ["I", "Q = CV for a parallel-plate capacitor"]
  ],
  key: ["photoelectric", "stopping", "capacitors"],
  q: `<p>An uncharged, isolated parallel plate capacitor has capacitance <code>C</code>. Monochromatic light of frequency <code>f</code> is incident on one of the metal plates, which has threshold frequency <code>f₀</code>. Emitted photoelectrons are then captured by the other plate. Once the capacitor charge has reached a steady value, how many electrons have been transferred between the plates? (<code>h</code> is Planck's constant and <code>e</code> is the magnitude of the electron charge.)</p>`,
  opts: [`Ch(f + f₀)/e`, `Cf₀(f + f₀)/e²`, `Ch(f − f₀)/e`, `Cf(f + f₀)/e²`, `Ch(f − f₀)/e²`],
  ans: 4,
  sol: `<p><b>What is being tested.</b> Two ideas linked by one sentence: the capacitor stops collecting charge when its own voltage is high enough to stop the fastest photoelectrons, and the number of electrons is the charge divided by <code>e</code> — not the charge itself.</p>
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
<p><b>Relevant topics:</b> the photoelectric effect; stopping potential and the threshold frequency; <code>Q = CV</code>; dimensional checking.</p>`,
  trap: "Stopping at <code>Ch(f − f₀)/e</code> — that is the charge on the plates. The question asks how many electrons, so divide by <code>e</code> once more."
},

{
  id: "R0-18", module: "B", topic: "Ranges at complementary angles", diff: 3, paper: "R0-2025",
  rel: [
    ["B", "Projectile range and the 45° maximum"],
    ["A", "Small-angle approximations — and knowing when they are unnecessary"],
    ["A", "Turning points: why a first-order change can vanish"]
  ],
  key: ["projectile", "smallangle", "limits"],
  q: `<p>Two particles are projected from ground level at the same speed <code>v</code>, but at two different angles to the horizontal: <code>(π/4 + α)</code> and <code>(π/4 − α)</code>, where <code>α</code> itself is a small angle in radians. Find the difference between the horizontal ranges of the two particles.</p>`,
  opts: [`0`, `αv²/g`, `2αv²/g`, `αv²/(2g)`, `4αv²/g`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> Whether you reach for the small-angle approximations because the question offers <code>α ≪ 1</code>, or whether you notice that the answer is exactly zero and no approximation can improve on it.</p>
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
<p><b>Relevant topics:</b> projectile range; the 45° maximum; stationary points; when not to use the small-angle approximations.</p>`,
  trap: "Expanding in α and picking a first-order term. The range is stationary at 45°, so the difference is exactly zero — options B, C, D and E are all linear in α and all impossible."
},

{
  id: "R0-19", module: "K", topic: "Time for one third to decay", diff: 2, paper: "R0-2025",
  rel: [
    ["K", "Exponential decay and the half-life"],
    ["K", "Half-life from data"],
    ["A", "Logarithms without a calculator"]
  ],
  key: ["expdecay", "logs", "nocalc"],
  q: `<p>The half-life of a radioactive substance is <code>T</code>. What is the time taken for one third of the substance to decay?</p>`,
  opts: [`(2/3) T`, `√(2/3) · T`, `T log₂(3/2)`, `T log₂(3)`, `T<sup>2/3</sup>`],
  ans: 2,
  sol: `<p><b>What is being tested.</b> Whether you read “one third decays” as “two thirds remain” — the single sentence that decides the question — and whether you can handle a logarithm with no calculator.</p>
<p><b>Step 1 — restate what is left.</b></p>
<div class="formula">one third decayed   ⇒   1 − 1/3 = 2/3 remains</div>
<p><b>Step 2 — apply the decay law.</b> After time <code>t</code> the fraction remaining is <code>(1/2)<sup>t/T</sup></code>:</p>
<div class="formula">(1/2)<sup>t/T</sup> = 2/3</div>
<p><b>Step 3 — take logs of both sides.</b></p>
<div class="formula">(t/T) log 2 = log(2/3)     … taking logs and using log(1/2) = −log 2
t / T = log(3/2) / log 2
t = T log₂(3/2)</div>
<p><b>Answer: C, T log₂(3/2).</b></p>
<p><b>Read the answer to check it — by bounding, not by calculating.</b> You cannot evaluate
<code>log₂3</code> without a calculator, and you do not need to. Trap 3 between two powers of 2 you can
compute in your head:</p>
<div class="formula">2<sup>1.5</sup> = 2 × √2 = 2 × 1.414 = 2.83 &lt; 3 &lt; 2<sup>2</sup> = 4
=&gt;   1.5 &lt; log₂3 &lt; 2
=&gt;   0.5 &lt; log₂3 − 1 &lt; 1
=&gt;   0.5 &lt; log₂(3/2) &lt; 1,   so  t is between 0.5T and 1T</div>
<p>That is exactly what the physics demands: less than half the substance has decayed, so less than one
half-life has elapsed — and more than none has, so more than zero. The bounds give you the answer's
<i>whereabouts</i>, which is all a multiple-choice question ever asks for. (For the record
<code>log₂3 = 1.585</code> and <code>t = 0.585T</code>, but note that no step above needed either number.)</p>
<p><b>Why the other options are wrong.</b> A, <code>(2/3)T</code>, assumes the decay is linear in time — at <code>t = (2/3)T</code> it would have the substance decaying at a constant rate, which is not what radioactive decay does. D, <code>T log₂3</code> (a little under <code>2T</code>, by the bound above), is the answer to a different question: it is the time for two thirds to have decayed, i.e. one third remaining, because it comes from <code>(1/2)<sup>t/T</sup> = 1/3</code>. That is the single most common slip here, and it is why the question says “one third decay” rather than “one third remaining”. E, <code>T<sup>2/3</sup></code>, is dimensionally impossible — a half-life raised to a power is not a time — so it dies on inspection. B, <code>√(2/3) T ≈ 0.82T</code>, is a third plausible-looking number with no derivation behind it; you cannot get a square root out of an exponential decay law.</p>
<p><b>Carry the general form.</b> If a fraction <code>f</code> remains,</p>
<div class="formula">t = T log₂(1/f)</div>
<p>Check it on two cases you know by heart: <code>f = 1/2</code> gives <code>t = T log₂2 = T</code> ✔, and <code>f = 1/4</code> gives <code>2T</code> ✔. A general formula that reproduces the standard cases is worth remembering, and these two are the ones it will be tested against.</p>
<p><b>How to do <code>log₂(3/2)</code> without a calculator.</b> Split it: <code>log₂(3/2) = log₂3 − 1</code>, and <code>log₂3</code> is between <code>log₂2 = 1</code> and <code>log₂4 = 2</code>, closer to 1.5 than to 2 — so for the record 0.585 is plausible before you compute anything. If the options had required the value rather than the expression, that bracket would be enough to choose.</p>
<p><b>Relevant topics:</b> exponential decay; half-life; the decay law in index form; logarithms.</p>`,
  trap: "Reading one third decayed as one third remaining and answering <code>T log₂3 ≈ 1.6T</code>. Two thirds remains, so <code>t = T log₂(3/2)</code>, which the bounds put between <code>0.5T</code> and <code>1T</code> — less than a half-life is wrong; <i>under one</i> half-life is right."
},

{
  id: "R0-20", module: "C", topic: "Jerk of a bungee jumper against time", diff: 3, paper: "R0-2025",
  rel: [
    ["C", "Newton's second law, including a spring force"],
    ["C", "Hooke's law and the onset of simple harmonic motion"],
    ["A", "Reasoning about graph shape: jumps, turning points, limits"]
  ],
  key: ["force", "hookeslaw", "shm", "graphshape"],
  q: `<p>Jerk is defined as the rate of change of acceleration with respect to time, <code>j = da/dt</code>.</p><p>A bungee jumper attached to a slack rope falls from a height. Once the rope is taut, it acts as an ideal spring which subsequently brings the jumper to instantaneous rest. Which of the following graphs shows the jerk <code>j</code> as a function of time <code>t</code>, up to this moment?</p>`,
  opts: [`<svg class="gopt" viewBox="0 0 182 126" role="img" aria-label="A jerk graph that jumps at the dashed line and then falls in a straight line to zero.">
<defs>
<marker id="gA-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="gA-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="gA-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="gA-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="gA-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="22" y1="96" x2="162" y2="96" stroke="#14181f" stroke-width="1.7" marker-end="url(#gA-ar)"/>
<line x1="22" y1="96" x2="22" y2="14" stroke="#14181f" stroke-width="1.7" marker-end="url(#gA-ar)"/>
<line x1="55" y1="96" x2="55" y2="30" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="5 4"/>
<polyline points="55.0,30.0 142.0,94.0" fill="none" stroke="#2f5fd0" stroke-width="2.6" stroke-linejoin="round"/>
<text x="156" y="113" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">t</text>
<text x="15" y="18" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">j</text>
</svg>`, `<svg class="gopt" viewBox="0 0 182 126" role="img" aria-label="A smooth hump that starts on the axis and returns to the axis.">
<defs>
<marker id="gB-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="gB-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="gB-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="gB-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="gB-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="22" y1="96" x2="162" y2="96" stroke="#14181f" stroke-width="1.7" marker-end="url(#gB-ar)"/>
<line x1="22" y1="96" x2="22" y2="14" stroke="#14181f" stroke-width="1.7" marker-end="url(#gB-ar)"/>
<polyline points="55.0,94.0 66.0,62.0 78.0,34.0 92.0,24.0 106.0,30.0 122.0,56.0 142.0,94.0" fill="none" stroke="#2f5fd0" stroke-width="2.6" stroke-linejoin="round"/>
<text x="156" y="113" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">t</text>
<text x="15" y="18" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">j</text>
</svg>`, `<svg class="gopt" viewBox="0 0 182 126" role="img" aria-label="A triangle: jerk rising in a straight line from zero to a peak and falling back to zero.">
<defs>
<marker id="gC-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="gC-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="gC-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="gC-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="gC-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="22" y1="96" x2="162" y2="96" stroke="#14181f" stroke-width="1.7" marker-end="url(#gC-ar)"/>
<line x1="22" y1="96" x2="22" y2="14" stroke="#14181f" stroke-width="1.7" marker-end="url(#gC-ar)"/>
<polyline points="55.0,94.0 95.0,24.0 142.0,94.0" fill="none" stroke="#2f5fd0" stroke-width="2.6" stroke-linejoin="round"/>
<text x="156" y="113" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">t</text>
<text x="15" y="18" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">j</text>
</svg>`, `<svg class="gopt" viewBox="0 0 182 126" role="img" aria-label="Jerk jumping at the dashed line, rising to a rounded peak and then falling to zero.">
<defs>
<marker id="gD-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="gD-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="gD-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="gD-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="gD-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="22" y1="96" x2="162" y2="96" stroke="#14181f" stroke-width="1.7" marker-end="url(#gD-ar)"/>
<line x1="22" y1="96" x2="22" y2="14" stroke="#14181f" stroke-width="1.7" marker-end="url(#gD-ar)"/>
<line x1="50" y1="96" x2="50" y2="62" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="5 4"/>
<polyline points="50.0,62.0 58.0,40.0 70.0,26.0 88.0,22.0 104.0,30.0 122.0,58.0 146.0,94.0" fill="none" stroke="#2f5fd0" stroke-width="2.6" stroke-linejoin="round"/>
<text x="156" y="113" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">t</text>
<text x="15" y="18" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">j</text>
</svg>`, `<svg class="gopt" viewBox="0 0 182 126" role="img" aria-label="Jerk jumping at the dashed line and then decaying steadily towards zero.">
<defs>
<marker id="gE-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="gE-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="gE-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="gE-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="gE-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="22" y1="96" x2="162" y2="96" stroke="#14181f" stroke-width="1.7" marker-end="url(#gE-ar)"/>
<line x1="22" y1="96" x2="22" y2="14" stroke="#14181f" stroke-width="1.7" marker-end="url(#gE-ar)"/>
<line x1="52" y1="96" x2="52" y2="28" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="5 4"/>
<polyline points="52.0,28.0 78.0,34.0 104.0,48.0 128.0,68.0 150.0,90.0" fill="none" stroke="#2f5fd0" stroke-width="2.6" stroke-linejoin="round"/>
<text x="156" y="113" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">t</text>
<text x="15" y="18" text-anchor="end" font-size="11.5" font-style="italic" fill="#4a5262">j</text>
</svg>`],
  ans: 3,
  sol: `<p><b>What is being tested.</b> The shape of a graph you have never seen before, built from two pieces of ordinary physics: free fall, then a spring. Every wrong option breaks one specific feature of that shape, so the method is to establish the features first.</p>
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
<figure class="fig">
<svg viewBox="0 0 480 244" role="img" aria-label="Jerk against time: zero during free fall, a jump at the moment the rope becomes taut, a rounded maximum, and a return to zero at the instant the jumper comes to rest.">
<defs>
<marker id="fs20-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="fs20-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="fs20-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="fs20-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="fs20-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="62.0" y1="202.0" x2="442.0" y2="202.0" stroke="#14181f" stroke-width="1.8" marker-end="url(#fs20-ar)"/>
<line x1="62.0" y1="202.0" x2="62.0" y2="40.0" stroke="#14181f" stroke-width="1.8" marker-end="url(#fs20-ar)"/>
<line x1="62.0" y1="202.0" x2="152.0" y2="202.0" stroke="#7b8494" stroke-width="4"/>
<line x1="152.0" y1="202.0" x2="152.0" y2="62" stroke="#7b8494" stroke-width="1.5" stroke-dasharray="6 5"/>
<path d="M152.0,132 C190,80 220,64 258,66 C306,68 372,128 414,200" fill="none" stroke="#2f5fd0" stroke-width="2.8" stroke-linejoin="round"/>
<circle cx="152.0" cy="132" r="3.6" fill="#2f5fd0"/>
<text x="70.0" y="190.0" font-size="11.5" fill="#7b8494">free fall: a = g, so j = 0</text>
<text x="72.0" y="52" font-size="11.5" font-weight="600" fill="#b3352f">rope goes taut: j jumps</text>
<text x="442" y="52" text-anchor="end" font-size="11.5" font-weight="600" fill="#2f5fd0">a = 0: speed greatest, so |j| greatest</text>
<text x="436.0" y="220.0" text-anchor="end" font-size="12" font-style="italic" fill="#4a5262">t</text>
<text x="54.0" y="46.0" text-anchor="end" font-size="12" font-style="italic" fill="#4a5262">j</text>
<text x="390" y="190.0" text-anchor="end" font-size="11.5" font-weight="600" fill="#1f7a53">v = 0: at rest, j = 0</text>
</svg>
<figcaption><b>The graph the correct option has to have.</b> Flat at zero while the rope is slack; a discontinuous jump at the instant it goes taut; a rise to a maximum as the jumper is still speeding up; and a return to exactly zero at the moment of instantaneous rest.</figcaption>
</figure>
<p><b>Why E is wrong even though it has the jump.</b> E starts at a high value at the dashed line and decays steadily towards the axis. It is missing the initial rise — and, more fundamentally, a monotonic decay of that kind is the signature of an exponential, which comes from a first-order process. The motion after the rope goes taut is simple harmonic, whose speed is a sinusoid, so the jerk must rise to a maximum and return to zero at a definite time, not creep towards the axis.</p>
<p><b>Why A is wrong.</b> A jumps and then falls to zero in a straight line, so the jerk would be linear in time. Since <code>j ∝ v</code>, that would force the speed to be linear in time — constant acceleration — which is the opposite of what a spring does.</p>
<p><b>The method for any “which graph” question.</b> Do not try to plot the function. Instead, list the features the correct graph must have and test each option against them:</p>
<div class="formula">1. flat at zero during free fall                        (all five pass)
2. a jump, not a smooth start, at the rope's tautness   (removes B, C)
3. an initial rise before the fall                      (removes E, A)
4. a return to exactly zero at instantaneous rest       (removes E)</div>
<p>Four features, and each option fails at a named one. That is worth more than any amount of sketching, and it is how this question is meant to be answered in the two and a half minutes available.</p>
<p><b>Relevant topics:</b> Newton's second law with a spring; Hooke's law; the onset of simple harmonic motion; graph-shape reasoning; rates of change.</p>`,
  trap: "Assuming the jerk is zero when the rope goes taut because the acceleration is momentarily unchanged. The acceleration is continuous, but its <i>rate of change</i> jumps — that is the whole point of the question."
},

{
  id: "R0-21", module: "C", topic: "Moments", diff: 3, paper: "R0-2025",
  rel: [
    ["C", "Moments"],
    ["C", "Inclined plane"],
    ["B", "Uniform acceleration"],
    ["A", "Ratio reasoning"]
  ],
  key: ["vectors-resolve", "kinematics", "moments", "statics"],
  q: `<p>A light inextensible string is attached to one end of a rigid rod of negligible weight and of length <code>ℓ</code>, with its other end freely hinged at O. The other end of the string is attached to the ceiling, so that the string is vertical, and the rod makes an angle of 30° to the horizontal. A small smooth ring of mass <code>m</code> is released from rest at the upper end of the rod and slides downwards along it.</p><figure class="fig">
<svg viewBox="0 0 480 262" role="img" aria-label="A rod hinged at its lower-left end at O making thirty degrees with the horizontal, with a vertical string from the ceiling down to its upper end where a small ring of mass m is released.">
<line x1="40" y1="42" x2="446" y2="42" stroke="#14181f" stroke-width="2.2"/>
<line x1="60" y1="42" x2="48" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="92" y1="42" x2="80" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="124" y1="42" x2="112" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="156" y1="42" x2="144" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="188" y1="42" x2="176" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="220" y1="42" x2="208" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="252" y1="42" x2="240" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="284" y1="42" x2="272" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="316" y1="42" x2="304" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="348" y1="42" x2="336" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="380" y1="42" x2="368" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="412" y1="42" x2="400" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="444" y1="42" x2="432" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="340.9" y1="86.0" x2="340.9" y2="42" stroke="#14181f" stroke-width="2"/>
<line x1="88.0" y1="232.0" x2="340.9" y2="86.0" stroke="#14181f" stroke-width="2.8"/>
<line x1="88.0" y1="232.0" x2="288.0" y2="232.0" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="6 5"/>
<path d="M154.0,232.0 A66.0,66.0 0 0 1 145.2,199.0" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<text x="174.0" y="216.0" font-size="12.5" font-weight="600" fill="#b3352f">30°</text>
<circle cx="340.9" cy="86.0" r="7.5" fill="#ffffff" stroke="#14181f" stroke-width="2.4"/>
<text x="354.9" y="80.0" font-size="13.5" font-style="italic" font-weight="600" fill="#14181f">m</text>
<text x="200" y="153" font-size="13.5" font-style="italic" fill="#14181f">ℓ</text>
<circle cx="88.0" cy="232.0" r="4.6" fill="#14181f"/>
<text x="72.0" y="238.0" font-size="13.5" font-weight="600" fill="#14181f">O</text>
<text x="340.9" y="30" text-anchor="middle" font-size="11.5" fill="#7b8494">ceiling</text>
<text x="350.9" y="64" font-size="12" fill="#4a5262">string</text>
</svg>
<figcaption><b>The rod is held still by the string; the ring slides along it.</b> Note which end the ring starts at, and that the rod keeps the ring at a fixed angle — the motion is one-dimensional along the rod, not vertical.</figcaption>
</figure><p>Given that the tension in the string <code>T</code> at time <code>t</code> (while the ring is in motion) is <code>T = mg(1 − kt²)</code>, select the correct expression for <code>k</code>.</p>`,
  opts: [`g / 4ℓ`, `g / 2ℓ`, `g / ℓ`, `g / (√2 ℓ)`, `√3 g / (2ℓ)`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> One realisation unlocks the whole question: <b>the rod does not move</b>. "
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
<figure class="fig">
<svg viewBox="0 0 480 262" role="img" aria-label="A rod hinged at its lower-left end at O making thirty degrees with the horizontal, with a vertical string from the ceiling down to its upper end where a small ring of mass m is released.">
<line x1="40" y1="42" x2="446" y2="42" stroke="#14181f" stroke-width="2.2"/>
<line x1="60" y1="42" x2="48" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="92" y1="42" x2="80" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="124" y1="42" x2="112" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="156" y1="42" x2="144" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="188" y1="42" x2="176" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="220" y1="42" x2="208" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="252" y1="42" x2="240" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="284" y1="42" x2="272" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="316" y1="42" x2="304" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="348" y1="42" x2="336" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="380" y1="42" x2="368" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="412" y1="42" x2="400" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="444" y1="42" x2="432" y2="30" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="340.9" y1="86.0" x2="340.9" y2="42" stroke="#14181f" stroke-width="2"/>
<line x1="88.0" y1="232.0" x2="340.9" y2="86.0" stroke="#14181f" stroke-width="2.8"/>
<line x1="88.0" y1="232.0" x2="288.0" y2="232.0" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="6 5"/>
<path d="M154.0,232.0 A66.0,66.0 0 0 1 145.2,199.0" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<text x="174.0" y="216.0" font-size="12.5" font-weight="600" fill="#b3352f">30°</text>
<circle cx="340.9" cy="86.0" r="7.5" fill="#ffffff" stroke="#14181f" stroke-width="2.4"/>
<text x="354.9" y="80.0" font-size="13.5" font-style="italic" font-weight="600" fill="#14181f">m</text>
<text x="200" y="153" font-size="13.5" font-style="italic" fill="#14181f">ℓ</text>
<circle cx="88.0" cy="232.0" r="4.6" fill="#14181f"/>
<text x="72.0" y="238.0" font-size="13.5" font-weight="600" fill="#14181f">O</text>
<text x="340.9" y="30" text-anchor="middle" font-size="11.5" fill="#7b8494">ceiling</text>
<text x="350.9" y="64" font-size="12" fill="#4a5262">string</text>
</svg>
<figcaption><b>The rod is held still by the string; the ring slides along it.</b> Note which end the ring starts at, and that the rod keeps the ring at a fixed angle — the motion is one-dimensional along the rod, not vertical.</figcaption>
</figure>
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
            "<code>s = ½at²</code> from rest; reading a given algebraic form for a boundary condition.</p>`,
  trap: "Taking the rod to rotate, or treating the ring as falling vertically with <code>a = g</code>. The rod is held still by the string; the ring accelerates at <code>g sin 30° = g/2</code> along it."
},

{
  id: "R0-22", module: "D", topic: "Conical pendulum", diff: 2, paper: "R0-2025",
  rel: [
    ["D", "Conical pendulum"],
    ["D", "Angular speed"],
    ["D", "Centripetal force"],
    ["A", "Ratio reasoning"]
  ],
  key: ["circular", "conical", "ratio", "nocalc"],
  q: `<p>A conical pendulum consists of a bob attached to a light inextensible string of length<code>ℓ</code>, with the upper end fixed. The bob moves in a horizontal circle so that the string makes an angle of 30° to the vertical. By what factor must the angular frequency be increased for this angle to double to 60°?</p>`,
  opts: [`√√3`, `√2`, `√3`, `2`, `3`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> Whether you know the conical-pendulum result well enough to use it "
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
<div class="formula">ω₂ / ω₁ = √√3 = 3<sup>1/4</sup> ≈ 1.32</div>
<p><b>Answer: A, √√3.</b></p>
<p><b>You can pick it out without evaluating the fourth root at all.</b> Raise each option to the fourth
power — the answer must give exactly 3, and fourth powers are just squaring twice:</p>
<div class="formula">A  √√3  →  (√√3)<sup>4</sup> = 3            ✔
B  √2   →  (√2)<sup>4</sup>  = 4            ✘
C  √3   →  (√3)<sup>4</sup>  = 9            ✘
D  2    →  2<sup>4</sup>     = 16           ✘
E  3    →  3<sup>4</sup>     = 81           ✘</div>
<p>One line, no arithmetic beyond 2² = 4 and 3² = 9. If you do want the size of it, take it in two easy
square roots: <code>√3 = 1.732</code>, then find the number whose square is 1.732 — <code>1.3² = 1.69</code>
is low and <code>1.32² = 1.742</code> is high, so it is about <code>1.316</code>. Either way you land on A.</p>
<figure class="fig">
<svg viewBox="0 0 480 250" role="img" aria-label="A conical pendulum: a string from a fixed point making thirty degrees with the vertical, with the bob on a dashed horizontal circle, and a second fainter string at sixty degrees with a larger circle.">
<defs>
<marker id="f22-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f22-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f22-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f22-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f22-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="60" y1="30" x2="440" y2="30" stroke="#14181f" stroke-width="2.2"/>
<line x1="76" y1="30" x2="64" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="108" y1="30" x2="96" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="140" y1="30" x2="128" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="172" y1="30" x2="160" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="204" y1="30" x2="192" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="236" y1="30" x2="224" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="268" y1="30" x2="256" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="300" y1="30" x2="288" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="332" y1="30" x2="320" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="364" y1="30" x2="352" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="396" y1="30" x2="384" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="428" y1="30" x2="416" y2="18" stroke="#cbd2dd" stroke-width="1.6"/>
<line x1="200.0" y1="48.0" x2="200.0" y2="126.0" stroke="#cbd2dd" stroke-width="1.5" stroke-dasharray="6 5"/>
<ellipse cx="200.0" cy="183.09996299037243" rx="78.0" ry="15" fill="none" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="5 5"/>
<ellipse cx="200.0" cy="126.00000000000001" rx="135.1" ry="18" fill="none" stroke="#cbd2dd" stroke-width="1.4" stroke-dasharray="5 5"/>
<line x1="200.0" y1="48.0" x2="278.0" y2="183.1" stroke="#14181f" stroke-width="2.4"/>
<line x1="200.0" y1="48.0" x2="335.1" y2="126.0" stroke="#7b8494" stroke-width="1.8" stroke-dasharray="7 5"/>
<line x1="200.0" y1="183.1" x2="278.0" y2="183.1" stroke="#2f5fd0" stroke-width="1.6" marker-start="url(#f22-dimS)" marker-end="url(#f22-dim)"/>
<path d="M200.0,110.0 A62.0,62.0 0 0 1 231.0,101.7" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<path d="M200.0,110.0 A62.0,62.0 0 0 0 253.7,79.0" fill="none" stroke="#7b8494" stroke-width="1.4" stroke-dasharray="5 4"/>
<text x="240.0" y="130.0" font-size="12.5" font-weight="600" fill="#b3352f">30°</text>
<text x="252.0" y="104.0" font-size="12.5" font-weight="600" fill="#7b8494">60°</text>
<circle cx="278.0" cy="183.1" r="7.5" fill="#ffffff" stroke="#14181f" stroke-width="2.4"/>
<circle cx="335.1" cy="126.0" r="6" fill="#ffffff" stroke="#7b8494" stroke-width="1.8"/>
<text x="278.0" y="209.1" text-anchor="middle" font-size="12" font-weight="600" fill="#2f5fd0">r = ℓ sin 30°</text>
<text x="335.1" y="152.0" text-anchor="middle" font-size="11.5" fill="#7b8494">r = ℓ sin 60°</text>
<text x="223" y="116" font-size="13" font-style="italic" fill="#14181f">ℓ</text>
<circle cx="200.0" cy="48.0" r="4" fill="#14181f"/>
</svg>
<figcaption><b>Doubling the angle from 30° to 60° nearly doubles the radius</b> — <code>ℓ sin 30° = 0.50ℓ</code> becomes <code>ℓ sin 60° = 0.87ℓ</code> — while the height of the bob above the pivot falls from <code>0.87ℓ</code> to <code>0.50ℓ</code>. Every one of those changes is packed into <code>ω² = g/(ℓ cos θ)</code>.</figcaption>
</figure>
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
<div class="formula">ω = √( g / (ℓ cos θ) )  ∝  (cos θ)<sup>−1/2</sup></div>
<p>Then the factor is <code>(cos θ₁ / cos θ₂)<sup>1/2</sup></code> and no other quantity can appear. That is why the 
            "options are pure numbers with no <code>g</code> or <code>ℓ</code> in them — a useful clue that 
            "you are on the right track.</p>
<p><b>Relevant topics:</b> conical pendulum; resolving tension into vertical and radial components; 
            "<code>ω² = g/(ℓ cos θ)</code>; ratio reasoning with a square root.</p>`,
  trap: "Reporting <code>cos 30°/cos 60° = √3</code> as the answer. That is the factor for <code>ω²</code>; the question asks about <code>ω</code>, so you must take the square root: <code>√√3</code>."
},

{
  id: "R0-23", module: "H", topic: "Log–log graphs", diff: 3, paper: "R0-2025",
  rel: [
    ["A", "Graph shape"],
    ["F", "Intensity ratio"],
    ["H", "Potential divider"],
    ["A", "Order of magnitude"]
  ],
  key: ["loggraphs", "inversesquare", "divider", "nocalc"],
  q: `<p>The resistance <code>R</code> of a light-dependent resistor (LDR) depends on the lightintensity <code>I</code>. A logarithmic plot relating these variables is shown below.</p><figure class="fig">
<svg viewBox="0 0 480 268" role="img" aria-label="A straight line on a graph of log R against log I, falling from 5.2 on the vertical axis at zero on the horizontal axis to 1.8 at four on the horizontal axis.">
<defs>
<marker id="f23-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f23-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f23-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f23-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f23-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="122.0" y1="216.0" x2="452.0" y2="216.0" stroke="#14181f" stroke-width="1.8" marker-end="url(#f23-ar)"/>
<line x1="122.0" y1="216.0" x2="122.0" y2="40" stroke="#14181f" stroke-width="1.8" marker-end="url(#f23-ar)"/>
<text x="452.0" y="256.0" text-anchor="end" font-size="12" font-style="italic" fill="#4a5262">log(I / W m⁻²)</text>
<text x="114.0" y="42" text-anchor="end" font-size="12" font-style="italic" fill="#4a5262">log(R / Ω)</text><line x1="122.0" y1="62.0" x2="396.0" y2="188.0" stroke="#2f5fd0" stroke-width="2.6"/>
<line x1="116.0" y1="62.0" x2="128.0" y2="62.0" stroke="#14181f" stroke-width="1.8"/>
<text x="110.0" y="67.0" text-anchor="end" font-size="13" font-weight="600" fill="#b3352f">5.2</text>
<line x1="116.0" y1="188.0" x2="128.0" y2="188.0" stroke="#14181f" stroke-width="1.8"/>
<text x="110.0" y="193.0" text-anchor="end" font-size="13" font-weight="600" fill="#b3352f">1.8</text>
<line x1="122.0" y1="210.0" x2="122.0" y2="222.0" stroke="#14181f" stroke-width="1.8"/>
<text x="122.0" y="240.0" text-anchor="middle" font-size="13" font-weight="600" fill="#b3352f">0</text>
<line x1="396.0" y1="210.0" x2="396.0" y2="222.0" stroke="#14181f" stroke-width="1.8"/>
<text x="396.0" y="240.0" text-anchor="middle" font-size="13" font-weight="600" fill="#b3352f">4</text>
<text x="130.0" y="54.0" font-size="11.5" fill="#7b8494">(0, 5.2)</text>
<text x="388.0" y="214.0" text-anchor="end" font-size="11.5" fill="#7b8494">(4, 1.8)</text>
</svg>
<figcaption><b>A straight line on log–log axes</b>, so <code>R ∝ I<sup>n</sup></code> with <code>n</code> equal to the gradient. Both scales are logarithmic, and the two end points are marked. (Reading the gradient off the plot is part of the question; what you then do with a fractional power is the rest of it.)</figcaption>
</figure><p>A point light source placed a distance <code>d</code> from the LDR illuminates it, and its resistance is measured to be <code>R₀</code>. Which of the following is a good approximation for the LDR resistance when the distance to the light source is halved?</p>`,
  opts: [`0.1 R₀`, `0.3 R₀`, `0.5 R₀`, `0.7 R₀`, `0.9 R₀`],
  ans: 1,
  sol: `<p><b>What is being tested.</b> Two separations that are usually taught apart and are here "
            "combined: reading a power law off a log–log plot, and knowing how a point source's intensity 
            "falls with distance. Neither step is hard; the difficulty is that the answer is not a round 
            "number, so you cannot guess it — you have to commit to the arithmetic.</p>
<p><b>Step 1 — read the gradient off the log–log plot.</b> On log axes a power law <code>R ∝ I<sup>n</sup></code> is a 
            "straight line of gradient <code>n</code>. The line runs from <code>(0, 5.2)</code> to 
            "<code>(4, 1.8)</code>, so</p>
<div class="formula">n = (1.8 − 5.2) / (4 − 0) = −3.4 / 4 = −0.85</div>
<div class="formula">R ∝ I<sup>−0.85</sup></div>
<p>Note the two things that make log axes worth using: the intercept (the “5.2”) is irrelevant to this 
            "question, and the units inside the logarithm are handled for you by the axis labels.</p>
<p><b>Step 2 — what halving the distance does to the intensity.</b> A point source spreads its power over a 
            "sphere of area <code>4πd²</code>, so</p>
<div class="formula">I ∝ 1 / d²        ⇒        d → d/2  gives  I → 4I</div>
<p><b>Step 3 — combine.</b></p>
<div class="formula">R_new / R₀ = (4I / I)<sup>−0.85</sup> = 4<sup>−0.85</sup></div>
<p><b>Now bracket it — do not try to compute it.</b> <code>4<sup>−0.85</sup></code> has no mental evaluation, and
it does not need one. The exponent −0.85 lies between −1 and −3/4, and for a base bigger than 1 a more
negative power is a smaller number, so</p>
<div class="formula">4<sup>−1</sup>      &lt;  4<sup>−0.85</sup>  &lt;  4<sup>−3/4</sup>
   1/4      &lt;  4<sup>−0.85</sup>  &lt;  1 / 4<sup>3/4</sup></div>
<p>and the right-hand bound is easy:
<code>4<sup>3/4</sup> = (2²)<sup>3/4</sup> = 2<sup>3/2</sup> = 2√2 = 2 × 1.414 = 2.83</code>, so</p>
<div class="formula">0.25  &lt;  4<sup>−0.85</sup>  &lt;  1/2.83  =  0.354</div>
<p>Of the five options — 0.1, 0.3, 0.5, 0.7, 0.9 — <b>only 0.3 lies between 0.25 and 0.354</b>. The
question is settled by two powers you can do in your head, and the gradient never had to be read to
better than “about −0.9”. That is the whole trick of this paper: bound the answer, then let the options
do the rounding.</p>
<p><b>Answer: B, 0.3 R₀.</b></p>
<p><b>The robustness check that matters most here.</b> Suppose you read the gradient as exactly 
            "<code>−1</code> instead of <code>−0.85</code> — a very reasonable mis-reading of a hand-drawn 
            "graph. Then</p>
<div class="formula">R_new / R₀ = 4<sup>−1</sup> = 0.25</div>
<p>and the nearest option is still <code>0.3 R₀</code>. So the answer does not depend on reading the gradient 
            "to two decimal places; it only depends on the gradient being close to <code>−1</code> and clearly 
            "not close to <code>0</code> or <code>−2</code>. That is what “a good approximation” in the 
            "question is telling you.</p>
<p><b>Where the wrong options come from.</b></p>
<div class="formula">C = 0.5 R₀   used I ∝ 1/d, not 1/d²  →  2<sup>−0.85</sup> ≈ 0.55
A = 0.1 R₀   used I ∝ 1/d³, or 4<sup>−1.7</sup> ≈ 0.1
D = 0.7 R₀   treated the change as small — as if the axes were linear
E = 0.9 R₀   almost no change at all</div>
<p>C is the one to watch for: “halve the distance, so halve the intensity” is the single most common error 
            "in this topic, and the option is sitting there to reward it.</p>
<p><b>The method for any log–log question.</b> Do three things in this order, and never multiply numbers 
            "before you have done all three:</p>
<div class="formula">1. gradient of the line  →  the power n in  y ∝ x<sup>n</sup>
2. what the physics does to x  →  the factor by which x changes
3. raise that factor to the power n</div>
<p><b>Relevant topics:</b> log–log plots and power laws; inverse-square law for a point source; estimating 
            "powers of 2 without a calculator.</p>`,
  trap: "Halving the distance and halving the intensity — that error leads straight to option C, 0.5R₀ — or trying to evaluate <code>4<sup>−0.85</sup></code> directly. Bracket it: it lies between <code>4<sup>−1</sup> = 0.25</code> and <code>4<sup>−3/4</sup> = 1/(2√2) = 0.354</code>, and 0.3 is the only option in that window."
},

{
  id: "R0-24", module: "C", topic: "Centre of mass", diff: 3, paper: "R0-2025",
  rel: [
    ["C", "Centre of mass"],
    ["C", "Equilibrium"],
    ["A", "Small-parameter approximations"],
    ["A", "Geometric approximation"]
  ],
  key: ["com", "pe-gpe", "smallchange"],
  q: `<p>A uniform ladder of mass <code>m</code> rests against a wall in static equilibrium at an angleof 45° to the vertical. The base of the ladder is pushed a small distance <code>a</code> towards the wall. Which of these options gives the best approximation for the change in gravitational potential energy of the ladder?</p>`,
  opts: [`½ mga`, `(1/√2) mga`, `mga`, `√2 mga`, `2 mga`],
  ans: 0,
  sol: `<p><b>What is being tested.</b> Whether you see that the ladder's gravitational potential energy "
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
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="A ladder resting against a wall at forty-five degrees, its centre of mass marked, with the height of the centre of mass, the base distance and the push towards the wall all dimensioned.">
<defs>
<marker id="f24-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#14181f"/></marker>
<marker id="f24-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#2f5fd0"/></marker>
<marker id="f24-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#b3352f"/></marker>
<marker id="f24-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="#7b8494"/></marker>
<marker id="f24-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="#7b8494"/></marker>
</defs>
<line x1="396.0" y1="20" x2="396.0" y2="248.0" stroke="#14181f" stroke-width="2.4"/>
<line x1="56" y1="248.0" x2="440" y2="248.0" stroke="#14181f" stroke-width="2.4"/>
<line x1="176.0" y1="248.0" x2="396.0" y2="28.0" stroke="#14181f" stroke-width="3"/>
<circle cx="286.0" cy="138.0" r="4.6" fill="#14181f"/>
<text x="276" y="126" text-anchor="middle" font-size="12.5" font-weight="600" fill="#5b3fa8">G</text>
<line x1="286.0" y1="138.0" x2="396.0" y2="138.0" stroke="#cbd2dd" stroke-width="1.3" stroke-dasharray="5 4"/>
<line x1="176.0" y1="282.0" x2="396.0" y2="282.0" stroke="#2f5fd0" stroke-width="1.5" marker-start="url(#f24-dimS)" marker-end="url(#f24-dim)"/>
<line x1="176.0" y1="248.0" x2="176.0" y2="288.0" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="4 4"/>
<line x1="396.0" y1="248.0" x2="396.0" y2="288.0" stroke="#cbd2dd" stroke-width="1.2" stroke-dasharray="4 4"/>
<text x="286" y="302.0" text-anchor="middle" font-size="12.5" font-weight="600" fill="#2f5fd0">x = L sin θ</text>
<line x1="112" y1="138.0" x2="286.0" y2="138.0" stroke="#7b8494" stroke-width="1.4" marker-start="url(#f24-dimS)" marker-end="url(#f24-dim)"/>
<text x="199" y="130" text-anchor="middle" font-size="12.5" font-weight="600" fill="#4a5262">h = (L/2) cos θ</text>
<path d="M396.0,102.0 A74.0,74.0 0 0 0 343.7,80.3" fill="none" stroke="#b3352f" stroke-width="1.8"/>
<text x="338" y="122" font-size="12.5" font-weight="600" fill="#b3352f">45°</text>
<line x1="176.0" y1="234.0" x2="228.0" y2="234.0" stroke="#1f7a53" stroke-width="2.4" marker-end="url(#f24-ar)"/>
<text x="236.0" y="240.0" font-size="12.5" font-weight="600" fill="#1f7a53">push a</text>
</svg>
<figcaption><b>The centre of mass is half way up the ladder</b>, so its height is <code>h = (L/2) cos θ</code>. At 45° a small push <code>a</code> towards the wall raises it by <code>(a/2) tan 45° = a/2</code> — the top of the ladder rises by the full <code>a</code>, the centre by half of that.</figcaption>
</figure>
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
            "<code>mgh</code>; small-change approximations; the geometry of a ladder against a wall.</p>`,
  trap: "Forgetting that only the centre of mass matters, which gives <code>mga</code> (option C). Also note that 45° to the vertical is 45° to the horizontal, so <code>cot θ = 1</code>."
},

{
  id: "R0-25", module: "H", topic: "Network reduction", diff: 3, paper: "R0-2025",
  rel: [
    ["H", "Network reduction"],
    ["H", "Series and parallel"],
    ["A", "Ratio reasoning"]
  ],
  key: ["seriesparallel", "networks", "ratio", "nocalc"],
  q: `<p>Consider the arrangement of 12 identical resistors below. The equivalent resistance is measuredbetween the following pairs of points: PR, PS, PU, QS, QT. Which measurement gives the median (middle value) resistance?</p><figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="A square grid of nine nodes joined by twelve identical resistors, labelled P, Q and R along the top row, S at the centre, and T and U along the bottom row.">
<line x1="128.0" y1="72.0" x2="352.0" y2="72.0" stroke="#14181f" stroke-width="2"/>

<line x1="128.0" y1="164.0" x2="352.0" y2="164.0" stroke="#14181f" stroke-width="2"/>

<line x1="128.0" y1="256.0" x2="352.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<line x1="128.0" y1="72.0" x2="128.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<line x1="240.0" y1="72.0" x2="240.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<line x1="352.0" y1="72.0" x2="352.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<rect x="158.0" y="62.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="270.0" y="62.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="158.0" y="154.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="270.0" y="154.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="158.0" y="246.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="270.0" y="246.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="118.0" y="95.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="118.0" y="187.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="230.0" y="95.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="230.0" y="187.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="342.0" y="95.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="342.0" y="187.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<circle cx="128.0" cy="72.0" r="3.6" fill="#14181f"/>
<circle cx="128.0" cy="164.0" r="3.6" fill="#14181f"/>
<circle cx="128.0" cy="256.0" r="3.6" fill="#14181f"/>
<circle cx="240.0" cy="72.0" r="3.6" fill="#14181f"/>
<circle cx="240.0" cy="164.0" r="3.6" fill="#14181f"/>
<circle cx="240.0" cy="256.0" r="3.6" fill="#14181f"/>
<circle cx="352.0" cy="72.0" r="3.6" fill="#14181f"/>
<circle cx="352.0" cy="164.0" r="3.6" fill="#14181f"/>
<circle cx="352.0" cy="256.0" r="3.6" fill="#14181f"/>
<text x="128" y="56" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">P</text>
<text x="240" y="56" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">Q</text>
<text x="352" y="56" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">R</text>
<text x="262" y="150" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">S</text>
<text x="240" y="284" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">T</text>
<text x="352" y="284" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">U</text>
</svg>
<figcaption><b>A 3 × 3 grid of nodes with all twelve resistors identical.</b> The labels sit on the nodes: P, Q, R along the top; S at the centre; T and U along the bottom. Every line you can see is one resistor.</figcaption>
</figure>`,
  opts: [`PR`, `PS`, `PU`, `QS`, `QT`],
  ans: 4,
  sol: `<p><b>What is being tested.</b> This looks like five brutal network calculations, and it is "
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
<figure class="fig">
<svg viewBox="0 0 480 300" role="img" aria-label="A square grid of nine nodes joined by twelve identical resistors, labelled P, Q and R along the top row, S at the centre, and T and U along the bottom row.">
<line x1="128.0" y1="72.0" x2="352.0" y2="72.0" stroke="#14181f" stroke-width="2"/>

<line x1="128.0" y1="164.0" x2="352.0" y2="164.0" stroke="#14181f" stroke-width="2"/>

<line x1="128.0" y1="256.0" x2="352.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<line x1="128.0" y1="72.0" x2="128.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<line x1="240.0" y1="72.0" x2="240.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<line x1="352.0" y1="72.0" x2="352.0" y2="256.0" stroke="#14181f" stroke-width="2"/>
<rect x="158.0" y="62.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="270.0" y="62.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="158.0" y="154.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="270.0" y="154.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="158.0" y="246.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="270.0" y="246.0" width="52" height="20" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="118.0" y="95.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="118.0" y="187.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="230.0" y="95.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="230.0" y="187.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="342.0" y="95.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<rect x="342.0" y="187.0" width="20" height="46" fill="#ffffff" stroke="#14181f" stroke-width="2"/>
<circle cx="128.0" cy="72.0" r="3.6" fill="#14181f"/>
<circle cx="128.0" cy="164.0" r="3.6" fill="#14181f"/>
<circle cx="128.0" cy="256.0" r="3.6" fill="#14181f"/>
<circle cx="240.0" cy="72.0" r="3.6" fill="#14181f"/>
<circle cx="240.0" cy="164.0" r="3.6" fill="#14181f"/>
<circle cx="240.0" cy="256.0" r="3.6" fill="#14181f"/>
<circle cx="352.0" cy="72.0" r="3.6" fill="#14181f"/>
<circle cx="352.0" cy="164.0" r="3.6" fill="#14181f"/>
<circle cx="352.0" cy="256.0" r="3.6" fill="#14181f"/>
<text x="128" y="56" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">P</text>
<text x="240" y="56" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">Q</text>
<text x="352" y="56" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">R</text>
<text x="262" y="150" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">S</text>
<text x="240" y="284" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">T</text>
<text x="352" y="284" text-anchor="middle" font-size="14" font-weight="600" fill="#5b3fa8">U</text>
</svg>
<figcaption><b>A 3 × 3 grid of nodes with all twelve resistors identical.</b> The labels sit on the nodes: P, Q, R along the top; S at the centre; T and U along the bottom. Every line you can see is one resistor.</figcaption>
</figure>
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
<div class="formula">R_QS = 7/12 Ω</div>
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
<div class="formula">QS = 7/12      PS = 7/8      QT = 1      PR = 5/4      PU = 3/2</div>
<p>Order them <b>by cross-multiplying, never by converting to decimals</b> — that is the whole point of
keeping them as fractions. <code>7/12</code> against <code>7/8</code>: compare <code>7 × 8 = 56</code> with
<code>7 × 12 = 84</code>, so <code>7/12 &lt; 7/8</code>. <code>7/8</code> against <code>1</code>:
<code>7 &lt; 8</code>. <code>1</code> against <code>5/4</code>: <code>4 &lt; 5</code>. And <code>5/4</code>
against <code>3/2</code>: <code>10 &lt; 12</code>. So the order is</p>
<div class="formula">7/12  &lt;  7/8  &lt;  1  &lt;  5/4  &lt;  3/2
 QS       PS      QT     PR      PU
                   ↑
              the median</div>
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
            "balanced Wheatstone bridge; identifying a median without evaluating every term.</p>`,
  trap: "Trying to evaluate all five networks by brute force, or assuming the median follows the alphabetical order of the labels. Fold on the symmetry axis first — QT reduces to a balanced bridge and is exactly <code>1 Ω</code>."
}

]);
