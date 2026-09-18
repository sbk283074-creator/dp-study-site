# -*- coding: utf-8 -*-
"""Key-point lessons, part C: electricity (H, I) and quantum & nuclear physics (K, L)."""

C = []


def c(i, m, stage, title, pre, summary, body, used):
    C.append(dict(id=i, m=m, stage=stage, t=title, pre=pre, one=summary, body=body.strip(), used=used))


# ───────────────────────────── STAGE 4 · ELECTRICITY ─────────────────────────────

c("charge", "H", 4, "Charge, current, potential difference and emf", [],
  "Current is the rate of flow of charge; potential difference is energy per coulomb given up; emf is energy per coulomb supplied.",
  """
<p><b>Charge</b> Q is a property of matter, measured in coulombs (C). The electron carries
−1.6 × 10⁻¹⁹ C, so ordinary charges are enormous numbers of electrons.</p>

<p><b>Current</b> is the rate at which charge flows past a point:</p>
<div class="formula">I = ΔQ / Δt        unit: ampere (A) = C s⁻¹</div>
<p>By convention current flows from positive to negative round the outside of a circuit — the opposite
way to the electrons, a historical accident that never causes trouble so long as you are consistent.</p>

<p><b>Potential difference</b> (pd, “voltage”) between two points is the energy transferred per unit charge
moving between them:</p>
<div class="formula">V = W / Q        unit: volt (V) = J C⁻¹</div>
<p>So a 6 V cell gives 6 J of energy to every coulomb that passes through it, and a component with 6 V
across it takes 6 J from every coulomb.</p>

<p><b>emf</b> (electromotive force) is not a force at all, despite the name — it is the energy per coulomb
the <i>source</i> supplies, converting chemical (or mechanical) energy into electrical energy. It is also
measured in volts. A real cell has internal resistance r, so the pd across its terminals is ε − Ir; when
the internal resistance is negligible (as in Q8) the terminal pd equals ε exactly.</p>

<p><b>Traps.</b> Thinking emf and pd are the same thing (emf is supplied, pd is delivered — they are equal
only with no internal resistance and no current); and thinking current gets “used up” round a circuit —
the same current returns to the cell, it just has less energy per coulomb.</p>
""",
  "Q8: a cell of emf ε with negligible internal resistance, so the loop is driven by ε.")

c("resistance", "H", 4, "Resistance and Ohm's law", ["charge"],
  "Resistance measures how hard it is to push current through something: R = V/I, and for an ohmic conductor it is a constant.",
  """
<p>The <b>resistance</b> of a component is the ratio of the pd across it to the current through it:</p>
<div class="formula">R = V / I        unit: ohm (Ω) = V A⁻¹</div>
<p>Physically, electrons drifting through a metal collide with the vibrating ions and lose energy; that
opposition is resistance.</p>

<p><b>Ohm's law</b> is a statement about certain materials, not a definition: for a metal at constant
temperature, V is proportional to I, so R is a constant and the V–I graph is a straight line through the
origin. A filament lamp is <i>not</i> ohmic — as it gets hotter its resistance rises and the graph curves.</p>

<p><b>Power</b> dissipated in a resistor combines P = VI with V = IR:</p>
<div class="formula">P = VI = I²R = V²/R        unit: watt (W)</div>

<p><b>Two ways of thinking about it.</b> Electrically, R = V/I. Mechanically, a longer or thinner conductor
has more resistance — which is what the resistivity formula makes precise.</p>

<p><b>Traps.</b> Assuming R is constant for every component (lamps and diodes are not ohmic); and quoting
Ohm's law as V = IR as if it were always true — it is the <i>definition</i> of R in general, but the
statement “R does not depend on V” is the actual law.</p>
""",
  "Q6, Q8 and Q25 all need resistances combined; Q23 is about a resistance that changes with light.")

c("resistivity", "H", 4, "Resistivity: R = ρL/A", ["resistance"],
  "Resistance doubles with length and halves with cross-sectional area; resistivity ρ is the material constant that ties them together.",
  """
<p>The resistance of a uniform wire depends on its shape as well as its material:</p>
<div class="formula">R = ρ L / A        ρ = resistivity (Ω m),  L = length,  A = cross-sectional area</div>
<p><b>Longer</b> wire → more collisions along the way → bigger R (proportional to L). <b>Fatter</b> wire →
more parallel routes for the current → smaller R (inversely proportional to A), just like a wider pipe
carries water more easily. Copper is about 1.7 × 10⁻⁸ Ω m; nichrome about 100 times more.</p>

<p><b>The competing effect that Q9 is built on.</b> For wires of the same material and length, making a
wire fatter changes two things at once:</p>
<div class="formula">A ↑   →   mass per unit length  μ = ρ_density · A   ↑     →  wave speed √(T/μ) ↓
A ↑   →   electrical resistance R = ρ_elec · L / A   ↓</div>
<p>Two different ρ symbols appear here — density and resistivity — which is a genuine trap in this
question. Read each symbol in context.</p>

<p><b>Traps.</b> Using diameter instead of area (A = πr², so doubling the diameter quarters the
resistance); and confusing the two ρ's.</p>
""",
  "Q9: the frequency ratio 2:1 forces an area ratio of 1:4, which forces a resistance ratio of 4:1.")

c("seriesparallel", "H", 4, "Resistors in series and in parallel", ["resistance"],
  "Series shares one current and adds the resistances; parallel shares one voltage and adds the reciprocals.",
  """
<p><b>Series</b> — components in one chain. The same current flows through each, and the voltages add:</p>
<div class="formula">R_total = R₁ + R₂ + …
V_total = V₁ + V₂ + …        I is the same everywhere</div>
<p><b>Parallel</b> — components side by side between the same two nodes. Each has the same pd across it, and
the currents add:</p>
<div class="formula">1/R_total = 1/R₁ + 1/R₂ + …        V is the same across each branch
for two:  R_total = R₁R₂ / (R₁ + R₂)      ("product over sum")</div>
<p>Where the reciprocal rule comes from: in parallel the currents add, I = I₁ + I₂, and each branch has the
same V, so V/R = V/R₁ + V/R₂ — divide through by V and you have it.</p>

<p><b>Two checks you should always run:</b></p>
<ul>
<li>A parallel combination is always <b>less than the smallest</b> branch — more routes means less
opposition. If you get a bigger number you have used the series formula.</li>
<li>Two equal resistors R in parallel give exactly R/2; three equal give R/3; n equal give R/n.</li>
</ul>
<p><b>Example (Q6).</b> Three 3 Ω resistors in parallel give 3/3 = 1 Ω; put that in series with one more
3 Ω and you have 4 Ω for 4 × £1 = £4.</p>

<p><b>Traps.</b> Adding parallel resistances directly; and forgetting that the “product over sum” shortcut
only works for <i>two</i> branches.</p>
""",
  "Q6 (three 3 Ω in parallel = 1 Ω, then +3 Ω in series) and Q25 (a 3×3 grid of twelve).")

c("networks", "H", 4, "Reducing a network: symmetry, folds and bridges", ["seriesparallel"],
  "Most 'impossible' networks collapse if you spot two nodes at the same potential — anything joining them carries no current and can simply be deleted.",
  """
<p>Series and parallel rules alone cannot reduce every network — Q25's 3 × 3 grid of twelve identical
resistors is the classic example. The extra weapon is <b>symmetry</b>.</p>

<p><b>Rule 1 — equal potentials carry nothing.</b> If two nodes must be at the same potential, a resistor
joining them has no pd across it, so no current flows through it, so it can be removed (or shorted —
either way nothing changes).</p>

<p><b>Rule 2 — the balanced Wheatstone bridge.</b> If R₁/R₂ = R₃/R₄ in a bridge, the middle resistor carries
no current:</p>
<div class="formula">R₁   R₂
  ╲ ╱
   ╳        no current in the middle arm when R₁/R₂ = R₃/R₄
   ╱ ╲
R₃   R₄</div>

<p><b>Finding the equal potentials.</b> Two symmetry arguments do the work:</p>
<ul>
<li><b>Mirror symmetry.</b> If the network and the terminals are both unchanged by a reflection, mirrored
nodes sit at equal potentials — so you can fold the network in half.</li>
<li><b>Antisymmetry.</b> If a reflection <i>swaps</i> the terminals, then (choosing the zero of potential
halfway between) mirrored nodes sit at equal and opposite potentials, V and −V. A node that the
reflection leaves <i>fixed</i> therefore has V = −V, so V = 0.</li>
</ul>

<p><b>Example (Q25), the pair QT.</b> Current enters at Q on the top edge and leaves at T on the bottom
edge. Left–right reflection leaves both terminals where they are, so columns mirror and can be folded.
Top–bottom reflection <i>swaps</i> Q and T, so the nodes it leaves fixed — the centre and the two middle-row
side nodes — are all at 0 V. The two resistors joining the centre to those side nodes therefore carry no
current: delete them. What is left reduces by series and parallel to ½ Ω from Q to the zero node and ½ Ω
from the zero node to T, giving:</p>
<div class="formula">R(QT) = ½ + ½ = 1 Ω        (exactly, no algebra)</div>
<p>The same treatment on the other four pairs gives QS = 7/12, PS = 7/8, PR = 5/4, PU = 3/2 — five values,
of which 1 Ω is the median.</p>

<p><b>Traps.</b> Assuming every grid reduces by series/parallel alone (this one does not); and merging nodes
that are not connected — you may short together nodes at equal potential, but you must not merge nodes
merely because they look symmetric in a drawing where the terminals break the symmetry.</p>
""",
  "Q25: the median of PR, PS, PU, QS, QT is QT = 1 Ω, found by symmetry rather than by solving nine nodal equations.")

c("meters", "H", 4, "Ideal ammeters and voltmeters", ["charge", "seriesparallel"],
  "An ideal ammeter is a wire (0 Ω) and an ideal voltmeter is a gap (∞ Ω) — which means each one silently deletes part of the circuit.",
  """
<p><b>Ammeters</b> measure the current through themselves, so they go <b>in series</b> with the component.
To avoid changing what they measure, an ideal ammeter has <b>zero resistance</b> — it is just a piece of
wire. Consequence: anything connected in parallel with an ideal ammeter is <b>short-circuited</b> and
carries no current.</p>

<p><b>Voltmeters</b> measure the pd between two points, so they go <b>in parallel</b> with the component. To
avoid drawing current away, an ideal voltmeter has <b>infinite resistance</b> — it is a gap. Consequence:
anything in series with an ideal voltmeter carries no current, so that branch is dead.</p>

<p><b>The move that solves Q8.</b> Look at the diagram and delete what the meters kill. The ammeter is in
parallel with one of the three resistors, so that resistor is shorted out of existence. The voltmeter sits
in a lead that feeds a junction, so that lead carries nothing. What survives is one simple loop: the cell
and two resistors of R in series.</p>
<div class="formula">loop resistance = R + R = 2R
current         I = ε / (2R)        ← the ammeter reading
pd across one R   = I R = ε/2        ← the voltmeter reading</div>
<p>The whole question is the two deletions; the arithmetic afterwards is one line.</p>

<p><b>Traps.</b> Treating the meters as extra resistors to add in; and misreading where each meter is
connected — a meter drawn in parallel with a resistor kills it, whereas one drawn in series merely stops
that branch.</p>
""",
  "Q8: two of the five components do nothing once you apply what 'ideal' means — the answer is ε/2 and ε/(2R).")

c("kirchhoff", "H", 4, "Kirchhoff's two laws", ["charge", "resistance"],
  "Charge cannot pile up at a junction and energy cannot appear from nowhere: those two facts give the two circuit laws.",
  """
<p><b>Kirchhoff's first law</b> (current law) — at any junction:</p>
<div class="formula">Σ I in = Σ I out</div>
<p>Because charge is conserved and cannot accumulate at a point. A node with three wires, two bringing
3 A and 2 A, must send 5 A down the third.</p>

<p><b>Kirchhoff's second law</b> (voltage law) — round any closed loop:</p>
<div class="formula">Σ emf = Σ (IR)        (sum of the rises = sum of the drops)</div>
<p>Because energy is conserved: a coulomb that gains energy in the cell must lose exactly as much going
round the rest of the loop and come back to the same potential.</p>

<p><b>How to use them.</b> Label a current in every branch (direction is arbitrary — a negative answer just
means it flows the other way), write the current law at each junction, write the voltage law round each
independent loop, and solve. Two rules of thumb: the current law at a junction of two branches says the
currents are equal, and components in parallel always share the same pd.</p>

<p><b>Traps.</b> Getting the sign wrong when going round a loop — fix a direction and treat every drop
against that direction as positive, every rise as negative, consistently. And writing more loop equations
than there are independent loops.</p>
""",
  "Q8 can be done with Kirchhoff's laws, though spotting what the ideal meters delete is faster.")

c("divider", "H", 4, "The potential divider", ["seriesparallel", "resistance"],
  "Two resistors in series split the supply voltage in proportion to their resistances — the basis of every sensor circuit.",
  """
<p>Put two resistors R₁ and R₂ in series across a supply V. The same current I = V/(R₁ + R₂) flows through
both, so the pd across R₂ is:</p>
<div class="formula">V_out = I R₂ = V · R₂ / (R₁ + R₂)</div>
<p>So the bigger resistor takes the bigger share of the voltage. Three quick consequences: if the two are
equal the output is half the supply; if R₂ is tiny the output is nearly 0; if R₂ is huge the output is
nearly the whole supply.</p>

<p><b>Why it matters.</b> Replace one resistor with a sensor whose resistance changes — an LDR (light), a
thermistor (temperature), a strain gauge — and the output voltage becomes a measurable signal that tracks
the physical quantity. That is how almost every analogue sensor is read.</p>

<p>In Q23 the LDR is the sensing element: its resistance falls as the light gets brighter, so the voltage
across it reports the light level.</p>

<p><b>Traps.</b> Using the total resistance instead of just R₂ in the numerator; and forgetting that the
output is measured across one resistor, not across the pair.</p>
""",
  "Q23: an LDR whose resistance depends on light is the classic divider sensor.")

c("capacitors", "I", 4, "Capacitance and Q = CV", ["charge"],
  "A capacitor stores charge: the charge stored is proportional to the pd across it, and the constant is the capacitance.",
  """
<p>A <b>capacitor</b> is two conducting plates separated by an insulator. Push charge onto one plate and an
equal amount is pushed off the other, so equal and opposite charges ±Q sit on the plates and energy is
stored in the electric field between them.</p>
<div class="formula">C = Q / V        unit: farad (F) = C V⁻¹
Q = C V</div>
<p>A 100 μF capacitor at 6 V holds Q = 100 × 10⁻⁶ × 6 = 6 × 10⁻⁴ C. The farad is a huge unit, so real
capacitors are quoted in μF, nF or pF.</p>

<p><b>How many electrons is that?</b> Divide by the elementary charge e = 1.6 × 10⁻¹⁹ C. This is the bridge
that Q17 uses: a capacitor charged to a potential V holds N = Q/e = CV/e electrons' worth of charge.</p>

<p><b>Energy stored.</b> The pd rises from 0 to V as charge builds, so the average pd during charging is
V/2 and:</p>
<div class="formula">E = ½ Q V = ½ C V²</div>
<p>For a parallel-plate capacitor, C = ε₀ε_r A/d — bigger plates and a smaller gap give more capacitance.</p>

<p><b>Traps.</b> Saying “a capacitor stores charge” loosely — the <i>net</i> charge is zero, it stores equal
and opposite charges on the two plates. And confusing C (capacitance, a fixed property) with Q (charge,
which changes).</p>
""",
  "Q17: the number of photoelectrons needed is Q/e, with Q = CV and V the stopping potential.")

c("loggraphs", "H", 4, "Log–log graphs: the gradient is the power", ["stdform"],
  "If y = kxⁿ, plotting log y against log x gives a straight line whose gradient is n — a way to read a power law straight off a graph.",
  """
<p>Take logarithms of both sides of y = k xⁿ:</p>
<div class="formula">y = k xⁿ
log y = log k + n log x</div>
<p>That is the equation of a straight line in the variables (log x, log y): intercept log k and
<b>gradient n</b>. So a log–log plot turns any power law into a straight line whose slope is the
exponent — which is how you discover a power law from data.</p>

<p><b>Example (Q23).</b> The graph shows log(R/Ω) against log(I/W m⁻²), passing through (0, 5.2) and
(4, 1.8):</p>
<div class="formula">gradient = (1.8 − 5.2) / (4 − 0) = −3.4 / 4 = −0.85
so   R ∝ I<sup>−0.85</sup></div>
<p>The negative gradient says what you would expect of an LDR: brighter light, lower resistance.</p>

<p><b>Using it without a calculator.</b> Halving the distance to a point source makes the intensity 4 times
larger, so <code>R/R₀ = 4<sup>−0.85</sup></code>. That number has no mental evaluation, and it does not need
one — <b>bracket it</b>. The exponent −0.85 lies between −1 and −3/4, and for a base bigger than 1 a more
negative power is a smaller number, so</p>
<div class="formula">4<sup>−1</sup>  &lt;  4<sup>−0.85</sup>  &lt;  4<sup>−3/4</sup>
 1/4    &lt;  4<sup>−0.85</sup>  &lt;  1 / 4<sup>3/4</sup></div>
<p>The right-hand bound is easy because <code>4<sup>3/4</sup> = (2²)<sup>3/4</sup> = 2<sup>3/2</sup> = 2√2 = 2 × 1.414 = 2.83</code>,
so</p>
<div class="formula">0.25  &lt;  4<sup>−0.85</sup>  &lt;  1 / 2.83  =  0.354</div>
<p>Of the options 0.1, 0.3, 0.5, 0.7, 0.9, <b>only 0.3 lies between 0.25 and 0.354</b>. Two powers you can
do in your head settle the question, and the gradient never had to be known to better than “about −0.85”.
This is what a non-calculator paper asks of you: bound the answer, then let the options do the rounding.</p>

<p><b>Traps.</b> Reading the gradient as the gradient of the original curve (it is not); getting the axes
the wrong way round (that gives you 1/n); and using log₁₀ versus ln inconsistently — the <i>gradient</i>
is the same either way, but only if both axes use the same base.</p>
""",
  "Q23: gradient −0.85, intensity × 4, so R ≈ 0.3 R₀.")

c("inversesquare", "F", 3, "Point sources and the inverse-square law", [],
  "Light from a point source spreads over the surface of an expanding sphere, so the intensity falls as 1/d² — halve the distance and you get four times the intensity.",
  """
<p>A point source radiating power P fills an ever-growing sphere. At distance d the power is spread over
the sphere's area 4πd², so the <b>intensity</b> (power per unit area) is:</p>
<div class="formula">I = P / (4π d²)          unit: W m⁻²</div>
<p>The light is not lost — it is spread thinner. Double the distance and the same power covers four times
the area, so the intensity is a quarter. Halve the distance and it is four times brighter:</p>
<div class="formula">I₂ / I₁ = (d₁ / d₂)²</div>
<p>This is why moving a lamp twice as close does not make a photo twice as bright but four times, and why
the inverse-square law appears in gravity, electrostatics and sound as well — anywhere something spreads
out evenly in three dimensions.</p>

<p><b>In Q23</b> the distance to the point source is halved, so the intensity rises by a factor of 4, and
the LDR's resistance then follows from the power law read off the log–log graph.</p>

<p><b>Traps.</b> Using 1/d instead of 1/d²; and applying the law to an extended or focused source, where it
does not hold.</p>
""",
  "Q23: halving the distance multiplies the intensity by 4 before the LDR's power law is applied.")

# ───────────────────────────── STAGE 5 · QUANTUM AND NUCLEAR ─────────────────────────────

c("photons", "L", 5, "Photons: light arrives in packets of energy hf", [],
  "Light is quantised: its energy comes in packets of hf, so a higher frequency means more energy per packet, not more light.",
  """
<p>A <b>photon</b> is one packet of electromagnetic energy. Its energy is fixed by the frequency alone:</p>
<div class="formula">E = h f = h c / λ        h = 6.63 × 10⁻³⁴ J s  (Planck's constant)</div>
<p>The constant h is tiny, which is why we do not notice the graininess of light in everyday life: a
40 W lamp emits roughly 10²⁰ photons every second.</p>

<p><b>Two consequences worth internalising:</b></p>
<ul>
<li><b>Higher frequency, more energy per photon.</b> Blue light (short λ, high f) carries more energy per
photon than red. That is why ultraviolet can cause sunburn and radio waves cannot.</li>
<li><b>Brighter means more photons, not more energetic photons.</b> Turning up the intensity at a fixed
frequency delivers more packets of the same size.</li>
</ul>
<p>That second point is the heart of the photoelectric effect, and it is what classical wave physics got
wrong.</p>

<p><b>Units check.</b> h has units J s; multiplied by f (s⁻¹) it gives J ✓. Alternatively h is an
<i>action</i> — energy × time — which is also angular momentum, and its dimensions are M L² T⁻¹.</p>

<p><b>Traps.</b> Using λ in the wrong place — E = hc/λ means <i>longer</i> wavelength means <i>less</i>
energy. And confusing “intensity” (number of photons) with “frequency” (energy per photon).</p>
""",
  "Q11 (photons from transitions between energy levels) and Q17 (photoelectrons).")

c("levels", "L", 5, "Atomic energy levels and transitions", ["photons"],
  "Electrons in an atom can only occupy certain energies; jumping between two levels emits or absorbs a photon whose energy is exactly the gap.",
  """
<p>Quantum mechanics restricts an atom's electrons to a set of discrete <b>energy levels</b> — rungs on a
ladder, not a ramp. An electron cannot sit between them. Level n = 1 is the <b>ground state</b> (lowest);
higher n are excited states; n = ∞ means the electron has escaped (ionisation).</p>

<p>When an electron drops from a higher level E₂ to a lower one E₁, the lost energy leaves as a single
photon:</p>
<div class="formula">h f = E₂ − E₁        ( emission:  downwards )
h f = E₁ − E₂ ...    ( absorption: upwards, photon of exactly this energy is needed )</div>
<p>So each transition produces light of one precise frequency — which is why atoms give <b>line spectra</b>
rather than a continuous rainbow, and why each element has its own fingerprint of lines.</p>

<p><b>Counting transitions (Q11).</b> With ten levels and every transition allowed, each photon energy
corresponds to a <i>pair</i> of levels, so there are C(10,2) = 45 possible photon energies. Note that
“maximum” is doing work in the question: two different pairs could accidentally have the same gap, which
would reduce the count — 45 is the upper bound.</p>

<p><b>Traps.</b> Counting 90 (counting each transition twice, once per direction); counting 100 (including
“transitions” from a level to itself, which emit nothing); and thinking all 45 photons have different
frequencies guaranteed rather than at most.</p>
""",
  "Q11: ten levels, all transitions allowed → at most C(10,2) = 45 photon energies.")

c("photoelectric", "L", 5, "The photoelectric effect", ["photons"],
  "Shine light on a metal and electrons come out — but only above a threshold frequency, and instantly, which wave theory cannot explain.",
  """
<p><b>The observations.</b> Light above a certain <b>threshold frequency</b> f₀ knocks electrons out of a
metal surface. Below f₀ nothing happens, no matter how bright the light or how long you wait. Above f₀ the
electrons appear immediately.</p>

<p><b>Why this killed the wave picture.</b> If light were a continuous wave, energy would arrive steadily
and even dim low-frequency light should eventually build up enough to eject an electron. It never does.
The explanation is that light arrives in photons of energy hf, and one photon is absorbed by one
electron:</p>
<div class="formula">h f = φ + KE_max        (energy conservation for one photon, one electron)</div>
<p>Here <b>φ</b> (phi) is the <b>work function</b>, the energy needed just to get an electron out of the
surface; φ = h f₀. Whatever is left over becomes the electron's kinetic energy:</p>
<div class="formula">KE_max = h f − φ = h (f − f₀)</div>
<p><b>Reading the equation:</b></p>
<ul>
<li>Below threshold (hf &lt; φ): no emission at all, however intense the light.</li>
<li>Increasing the <b>frequency</b> raises KE_max — the electrons come out faster.</li>
<li>Increasing the <b>intensity</b> raises the <i>number</i> emitted, not their maximum energy — more
photons, same energy each.</li>
</ul>

<p><b>Traps.</b> Thinking brighter light gives faster electrons (it gives more electrons); and using the
photon energy as the electron's kinetic energy without subtracting the work function.</p>
""",
  "Q17: photoelectrons emitted from a capacitor plate, with KE_max = h(f − f₀).")

c("stopping", "L", 5, "Stopping potential", ["photoelectric", "charge"],
  "Apply a reverse voltage until even the fastest photoelectron cannot reach the other side — that voltage measures the electrons' maximum kinetic energy.",
  """
<p>In a photoelectric experiment, make the collector negative relative to the emitting plate. Electrons
now have to climb an electric potential hill. Slow ones fall back; increase the reverse voltage until even
the <i>fastest</i> fail to arrive and the current falls to zero. That voltage is the <b>stopping
potential</b> V_s.</p>

<p>An electron of charge e climbing through a potential difference V gains potential energy eV, so the
condition “just stopped” is that its kinetic energy is exactly used up:</p>
<div class="formula">e V_s = KE_max = h f − φ = h (f − f₀)
V_s = h (f − f₀) / e</div>
<p>Two things to notice. The stopping potential depends on <b>frequency only</b>, not on intensity — a
direct experimental confirmation of the photon picture. And a plot of V_s against f is a straight line of
gradient h/e, which is how h is measured.</p>

<p><b>Example (Q17).</b> Light of frequency f hits a capacitor plate of threshold f₀. The emitted electrons
charge the capacitor until its pd reaches the stopping potential, at which point further electrons can no
longer cross. So the final pd is V_s = h(f − f₀)/e, the charge stored is Q = CV_s, and the number of
electrons that crossed is:</p>
<div class="formula">N = Q / e = C V_s / e = C h (f − f₀) / e²</div>
<p>The e² in the answer is not a typo — one e converts energy to a voltage, the other converts charge to a
number of electrons. That is exactly the kind of thing a units check confirms: C × J C⁻¹ / C is a pure
number ✓.</p>

<p><b>Traps.</b> Forgetting the second division by e when the question asks for a <i>number</i> of
electrons; and using KE_max where the question needs the voltage.</p>
""",
  "Q17: the number of photoelectrons is Ch(f − f₀)/e² — two factors of e, for two different reasons.")

c("nuclide", "K", 5, "Nuclide notation and the nuclear equation", [],
  "ᵃ_Z X: the top number counts nucleons, the bottom counts protons; both are conserved in every nuclear reaction.",
  """
<p>A nuclide is written <b>ᴬ_Z X</b>, where X is the element symbol:</p>
<div class="formula">A  mass number  = protons + neutrons     (roughly the mass, in u)
Z  proton number = atomic number          (this defines the element)
neutrons = A − Z</div>
<p>So ²³⁸₉₂U has 92 protons and 146 neutrons. The chemical identity is set by Z alone; changing Z makes a
different element, changing only the neutron count makes an <b>isotope</b> of the same element.</p>

<p><b>Two conservation rules govern every nuclear equation:</b></p>
<div class="formula">total A is conserved      (nucleons are neither created nor destroyed)
total Z is conserved      (charge is conserved)</div>
<p>Strictly, mass–energy is conserved and a little mass becomes energy — but the <i>count</i> of nucleons is
conserved exactly, which is the bookkeeping you need.</p>

<p><b>Traps.</b> Mixing up which number is which (top = mass, bottom = charge); and thinking the element
symbol follows A rather than Z.</p>
""",
  "Q4: tracking ²³⁸₉₂U down to ²⁰⁶₈₂Pb is pure A/Z bookkeeping.")

c("alphabeta", "K", 5, "Alpha and beta-minus decay", ["nuclide"],
  "Alpha removes 4 from A and 2 from Z; beta-minus leaves A alone and adds 1 to Z — a neutron turning into a proton.",
  """
<p><b>Alpha decay.</b> The nucleus ejects a helium nucleus, ⁴₂He — two protons and two neutrons bound
together:</p>
<div class="formula">ᴬ_Z X  →  ᴬ⁻⁴_{Z−2} Y  +  ⁴₂He
A decreases by 4,   Z decreases by 2</div>
<p>Alpha particles are heavy, doubly charged and highly ionising, so they are stopped by a sheet of paper
or a few centimetres of air.</p>

<p><b>Beta-minus decay.</b> A neutron in the nucleus turns into a proton, emitting an electron (the
β⁻ particle) and an antineutrino:</p>
<div class="formula">n  →  p  +  e⁻  +  ν̄
ᴬ_Z X  →  ᴬ_{Z+1} Y  +  e⁻  +  ν̄
A unchanged,   Z increases by 1</div>
<p>Note the mass number does not change: a neutron has become a proton, so the nucleon count is the same
but the charge has gone up by one. The electron is created in the process — it was not orbiting inside the
nucleus beforehand.</p>

<p>(Beta-<i>plus</i> is the mirror image: a proton becomes a neutron, emitting a positron, so Z goes down
by 1. Gamma emission changes neither A nor Z — it just releases surplus energy.)</p>

<p><b>Traps.</b> Changing A in a beta decay; and getting the sign of the Z change wrong — β⁻ makes the
nucleus more positive, because a negative electron carrying away negative charge leaves positive charge
behind.</p>
""",
  "Q4: eight alphas take A from 238 to 206, and six beta-minus decays repair Z from 76 back to 82.")

c("decayseries", "K", 5, "Decay series: working out how many of each", ["alphabeta", "nuclide"],
  "The mass number only changes with alpha decays, so count those first — then let the proton number tell you how many betas are needed.",
  """
<p>When a heavy nucleus decays through a chain of alphas and beta-minus decays to a known end product, the
two conservation rules give you two equations and there is a fixed order to solve them:</p>
<ul>
<li><b>Step 1 — use A to count the alphas.</b> Only alpha decay changes A (−4 each), so
n<sub>α</sub> = (A<sub>start</sub> − A<sub>end</sub>)/4.</li>
<li><b>Step 2 — work out what the alphas did to Z.</b> Each alpha takes 2 off.</li>
<li><b>Step 3 — use the gap in Z to count the betas.</b> Each β⁻ adds 1.</li>
</ul>
<p><b>Example (Q4).</b> ²³⁸₉₂U → ²⁰⁶₈₂Pb:</p>
<div class="formula">ΔA = 238 − 206 = 32        →  n_α = 32 / 4 = 8 alpha decays
those 8 alphas remove 8 × 2 = 16 from Z
predicted Z after the alphas: 92 − 16 = 76
actual final Z: 82, so Z must rise by 82 − 76 = 6
n_β = 6 beta-minus decays</div>
<p><b>Always check the direction.</b> Alpha decays take Z <i>down</i> too far (76 versus the needed 82), so
the betas have to push it back up — beta-minus, not beta-plus. Had the arithmetic left Z too high you
would have needed β⁺ decays, and the question says β⁻ only, which is itself a consistency check.</p>

<p><b>Traps.</b> Doing the Z bookkeeping before the A bookkeeping (you cannot count betas until you know how
many alphas there were); and forgetting that each alpha changes Z as well as A.</p>
""",
  "Q4: 8 alphas and 6 beta-minus decays, found in that order.")

c("expdecay", "K", 5, "Exponential decay and half-life", ["logs", "stdform"],
  "Radioactive decay is random per nucleus but perfectly predictable in bulk: a fixed fraction decays per unit time, giving a constant half-life.",
  """
<p>Each nucleus decays at random, but with a fixed probability per second. For a large sample that gives a
simple law: in each fixed interval, the same <i>fraction</i> of what remains decays. The number left is
therefore:</p>
<div class="formula">N = N₀ · 2<sup>−t/T</sup> = N₀ · (½)<sup>t/T</sup>
equivalently  N = N₀ e<sup>−λt</sup>     with  λ = ln 2 / T</div>
<p>where T is the <b>half-life</b> — the time for half the sample to go — and λ is the decay constant.</p>

<p><b>Why “half-life” and not “life”.</b> The time to go from N₀ to N₀/2 is the same as from N₀/2 to
N₀/4, and from N₀/4 to N₀/8. Halving takes a fixed time however much you have, so the quantity never
actually reaches zero — it just keeps halving.</p>

<p><b>Finding a time (Q19).</b> “One third has decayed” means two thirds <i>remain</i>, so N/N₀ = 2/3. Take
logs to bring t down out of the exponent:</p>
<div class="formula">2/3 = 2<sup>−t/T</sup>
log₂(2/3) = −t/T
t = T · log₂(3/2)        (using −log(x) = log(1/x))</div>
<p>Sanity check: log₂(3/2) ≈ 0.585, so the time is a bit over half a half-life — sensible, since
one-third decaying is less than half decaying.</p>

<p><b>Traps.</b> Using 1/3 as the fraction remaining when a third has <i>decayed</i> (two thirds remain);
and writing (2/3)T — a common wrong option — which would only be right if decay were linear rather than
exponential.</p>
""",
  "Q19: t = T·log₂(3/2), and the options test exactly this confusion.")

c("casimir", "L", 5, "The Casimir effect", ["dimensions"],
  "Two uncharged plates in a vacuum attract each other: the vacuum itself has fluctuating fields, and between the plates only certain fluctuations fit.",
  """
<p>Quantum field theory says the vacuum is not empty — electromagnetic fields fluctuate even with no
photons present. Put two perfectly conducting plates very close together and only fluctuations whose
half-wavelength fits a whole number of times into the gap can exist between them. Outside, all
fluctuations are allowed. More modes outside than inside means more radiation pressure pushing the plates
together than pushing them apart, so they <b>attract</b>.</p>

<p>The effect is tiny and only measurable at sub-micron separations. The exact result is:</p>
<div class="formula">p = π² ħ c / 240 r⁴        (ħ = h / 2π)</div>
<p>Note the r⁴ in the denominator: halve the gap and the pressure multiplies by 16. That steep dependence
is why the effect is invisible at everyday distances and dominant below a micron.</p>

<p><b>What Q13 actually asks.</b> Not for the formula — for the <i>dependence on r</i>, assuming the
pressure depends only on h, c and r. Dimensional analysis gives p ∝ h c / r⁴, which matches the true
result's dependence on r. Two honest caveats: dimensional analysis cannot tell h from ħ (they differ only
by the dimensionless 2π), and it cannot produce the numerical factor π²/240. It gives the power law and
nothing else — which is all the question wants.</p>
""",
  "Q13: the Casimir pressure from h, c and r — dimensional analysis gives p ∝ 1/r⁴.")
