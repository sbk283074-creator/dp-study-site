/* BPhO Round 0 — study guidance.
   One entry per module: what you must already be able to do before it makes
   sense (prereq), which modules to read first (before), and a three-question
   readiness self-test you can take before starting.

   `after` is not stored — it is derived from `before` when rendering, so the
   dependency graph can never get out of step with itself.

   Self-tests are deliberately three-option and conceptual. They are a gate,
   not a score: if you miss one, read the module rather than guess again. */

window.BPHO_GUIDANCE = {

  /* ------------------------------------------------------------------ A */
  A: {
    prereq: `<p>Nothing. This is the starting point, and it is the reason the paper is hard rather than merely long. You need to be able to handle numbers in standard form without a calculator, check that an answer has the right <i>units</i>, and round aggressively to get an answer to within a factor of two.</p>
<p>If you can already look at <code>3 × 10⁸</code> and <code>3 × 10⁷</code> and know which is a year in seconds without working it out, you are ready.</p>`,
    before: [],
    starter: [
      { q: "Roughly how many seconds are there in a year?", opts: ["3 × 10⁷", "3 × 10⁶", "3 × 10⁸"], ans: 0,
        why: "365 × 24 × 3600 ≈ 3.15 × 10⁷. A useful anchor: a year is about π × 10⁷ seconds." },
      { q: "Which of these has the dimensions of power?", opts: ["force × velocity", "force × time", "energy × time"], ans: 0,
        why: "P = Fv. Force × time is impulse; energy × time has no standard name." },
      { q: "A quantity has units of m s⁻². What kind of quantity is it?", opts: ["an acceleration", "a speed", "a force"], ans: 0,
        why: "Metres per second per second. Speed is m s⁻¹ and force is kg m s⁻²." },
    ],
  },

  /* ------------------------------------------------------------------ B */
  B: {
    prereq: `<p>Comfortable rearranging <code>v = u + at</code> and reading a velocity–time graph: gradient is acceleration, area is displacement. You should not need to stop and think about which is which.</p>
<p>Do the Toolkit module first — half of kinematics questions are really questions about whether your answer has the right units.</p>`,
    before: ["A"],
    starter: [
      { q: "An object accelerates from rest at 2 m s⁻² for 3 s. What is its final speed?", opts: ["6 m s⁻¹", "3 m s⁻¹", "12 m s⁻¹"], ans: 0,
        why: "v = u + at = 0 + 2 × 3 = 6 m s⁻¹." },
      { q: "On a velocity–time graph, what does the area under the line give?", opts: ["displacement", "acceleration", "average speed"], ans: 0,
        why: "Area is velocity × time. The gradient gives acceleration." },
      { q: "A ball is thrown straight up and caught at the same height. Ignoring air resistance, how does its speed on return compare with its launch speed?", opts: ["the same", "greater", "smaller"], ans: 0,
        why: "Energy is conserved and there is no drag, so it returns at the launch speed, directed downwards." },
    ],
  },

  /* ------------------------------------------------------------------ C */
  C: {
    prereq: `<p>Newton's second law in the form <code>F = ma</code>, and the idea that momentum <code>p = mv</code> is conserved when no external force acts. You should know the difference between an elastic and an inelastic collision without looking it up.</p>
<p>Kinematics first: forces questions usually end with you needing a velocity or a displacement.</p>`,
    before: ["A", "B"],
    starter: [
      { q: "Momentum is conserved in a collision when…", opts: ["no net external force acts", "the collision is elastic", "kinetic energy is conserved"], ans: 0,
        why: "Momentum conservation needs zero net external force. Elasticity is about kinetic energy, a separate condition." },
      { q: "Two objects collide and stick together. What is conserved?", opts: ["momentum only", "kinetic energy only", "both"], ans: 0,
        why: "Sticking together is the definition of a perfectly inelastic collision: momentum is conserved, kinetic energy is not." },
      { q: "A 2 N force acts on a 4 kg mass. What is its acceleration?", opts: ["0.5 m s⁻²", "2 m s⁻²", "8 m s⁻²"], ans: 0,
        why: "a = F/m = 2/4 = 0.5 m s⁻²." },
    ],
  },

  /* ------------------------------------------------------------------ D */
  D: {
    prereq: `<p>You need <code>F = ma</code> to be automatic, because circular motion is nothing more than <code>F = ma</code> applied to something whose acceleration points sideways. The leap is accepting that an object at <i>constant speed</i> can still be accelerating.</p>
<p>Do Forces first. Circular motion questions are forces questions wearing a costume.</p>`,
    before: ["B", "C"],
    starter: [
      { q: "An object moves in a circle at constant speed. In which direction does its acceleration point?", opts: ["towards the centre", "along its velocity", "it has no acceleration"], ans: 0,
        why: "The speed is constant but the direction changes, so there is an inward (centripetal) acceleration." },
      { q: "If the speed doubles at the same radius, the centripetal acceleration…", opts: ["quadruples", "doubles", "halves"], ans: 0,
        why: "a = v²/r — the speed is squared, so doubling it gives a factor of four." },
      { q: "What provides the centripetal force for a car cornering on a flat road?", opts: ["friction on the tyres", "gravity", "the engine"], ans: 0,
        why: "On a flat road only friction points towards the centre of the turn." },
    ],
  },

  /* ------------------------------------------------------------------ E */
  E: {
    prereq: `<p>Hooke's law (<code>F = kx</code>) and the ability to read a straight-line graph. The one genuinely new idea is <i>stress</i> and <i>strain</i>, which are force and extension rewritten so that the size of the sample does not matter.</p>
<p>Forces first — every materials question is an equilibrium or an energy question in disguise.</p>`,
    before: ["C"],
    starter: [
      { q: "Hooke's law relates…", opts: ["force and extension", "force and mass", "stress and temperature"], ans: 0,
        why: "F = kx, valid up to the limit of proportionality." },
      { q: "A spring of stiffness k is extended by x. How much energy is stored?", opts: ["½kx²", "kx²", "½kx"], ans: 0,
        why: "The area under a force–extension graph: ½ × F × x = ½ × kx × x = ½kx²." },
      { q: "Doubling the diameter of a wire makes its cross-sectional area…", opts: ["four times as large", "twice as large", "half as large"], ans: 0,
        why: "Area goes as the square of the diameter. This single fact drives most materials ratio questions." },
    ],
  },

  /* ------------------------------------------------------------------ F */
  F: {
    prereq: `<p>The wave equation <code>v = fλ</code>, and the difference between a progressive wave (which carries energy along) and a stationary wave (which stores it in place). Nothing else is needed.</p>
<p>Toolkit first: wave questions are full of unit conversions and factors of two.</p>`,
    before: ["A"],
    starter: [
      { q: "At constant wave speed, doubling the frequency makes the wavelength…", opts: ["halve", "double", "stay the same"], ans: 0,
        why: "v = fλ, so λ = v/f. Doubling f halves λ." },
      { q: "A string fixed at both ends vibrates in its fundamental mode. How does the wavelength compare with the string length L?", opts: ["λ = 2L", "λ = L", "λ = L/2"], ans: 0,
        why: "A fixed end is a node, so the fundamental has one antinode in the middle: half a wavelength fits on the string." },
      { q: "Two identical waves superpose exactly in phase. What happens to the amplitude?", opts: ["it doubles", "it is unchanged", "it becomes zero"], ans: 0,
        why: "Constructive interference: crest on crest. Exactly out of phase would give zero." },
    ],
  },

  /* ------------------------------------------------------------------ G */
  G: {
    prereq: `<p>Snell's law and the fact that <i>frequency never changes</i> when light crosses a boundary — speed and wavelength do, frequency does not. That one sentence settles most optics questions.</p>
<p>Do Waves first. Refraction is a change of wave speed, and it is much easier once waves make sense.</p>`,
    before: ["F"],
    starter: [
      { q: "Light passes from air into glass. Which quantity is unchanged?", opts: ["frequency", "speed", "wavelength"], ans: 0,
        why: "Frequency is set by the source. Speed and wavelength both fall by the factor n." },
      { q: "For light going from air into a medium, the refractive index is…", opts: ["sin i / sin r", "sin r / sin i", "sin i × sin r"], ans: 0,
        why: "Snell's law: n₁ sin θ₁ = n₂ sin θ₂, so with n₁ = 1, n = sin i / sin r." },
      { q: "Fringe spacing is λD/d. Doubling the slit separation d makes the fringes…", opts: ["half as far apart", "twice as far apart", "unchanged"], ans: 0,
        why: "Spacing is inversely proportional to d." },
    ],
  },

  /* ------------------------------------------------------------------ H */
  H: {
    prereq: `<p>Ohm's law, and the two rules for combining resistors (series adds, parallel reciprocal-adds). You need to be able to look at a network and say which parts are in series and which are in parallel without redrawing it slowly.</p>
<p>Toolkit first — circuit questions are where powers of ten and unit prefixes go to die.</p>`,
    before: ["A"],
    starter: [
      { q: "Two resistors of resistance R are connected in parallel. What is their combined resistance?", opts: ["R/2", "2R", "R"], ans: 0,
        why: "1/R_total = 1/R + 1/R = 2/R, so R_total = R/2." },
      { q: "A resistor of resistance R carries current I. How much power does it dissipate?", opts: ["I²R", "IR", "I²/R"], ans: 0,
        why: "P = VI and V = IR, so P = I²R." },
      { q: "Two components are in series. Which quantity is necessarily the same in both?", opts: ["current", "potential difference", "power"], ans: 0,
        why: "Series means the same charge flows through both. The pd is shared." },
    ],
  },

  /* ------------------------------------------------------------------ I */
  I: {
    prereq: `<p>Circuits first, without exception. Capacitors are the one topic where students consistently apply resistor rules backwards: capacitors in <i>parallel</i> add, capacitors in <i>series</i> reciprocal-add.</p>
<p>You also need <code>V = Q/C</code> to be as automatic as <code>V = IR</code>.</p>`,
    before: ["H"],
    starter: [
      { q: "Capacitance is defined as…", opts: ["charge per unit pd", "pd per unit charge", "charge × pd"], ans: 0,
        why: "C = Q/V. It is how much charge the capacitor stores per volt." },
      { q: "Two capacitors of capacitance C are connected in series. What is their combined capacitance?", opts: ["C/2", "2C", "C"], ans: 0,
        why: "1/C_total = 1/C + 1/C = 2/C, so C_total = C/2 — the opposite of the parallel rule." },
      { q: "A capacitor C is charged to a pd V. How much energy is stored?", opts: ["½CV²", "CV²", "½CV"], ans: 0,
        why: "The area under a charge–pd graph. Forgetting the ½ is the single most common capacitor slip." },
    ],
  },

  /* ------------------------------------------------------------------ J */
  J: {
    prereq: `<p>The difference between <i>heat</i> (energy in transit) and <i>temperature</i>, and the habit of converting to kelvin before using any gas law. Using °C in <code>pV = nRT</code> is the classic own goal.</p>
<p>Toolkit first: thermal questions lean heavily on standard form and on reading large and small numbers correctly.</p>`,
    before: ["A"],
    starter: [
      { q: "Specific heat capacity connects which three quantities?", opts: ["energy, mass and temperature change", "energy and mass only", "temperature and mass only"], ans: 0,
        why: "Q = mcΔT. It is the energy needed per kilogram per kelvin." },
      { q: "Absolute zero is approximately…", opts: ["−273 °C", "0 °C", "−100 °C"], ans: 0,
        why: "−273.15 °C, or 0 K. Always convert before using a gas law." },
      { q: "A fixed mass of gas is heated at constant volume so that its absolute temperature doubles. What happens to the pressure?", opts: ["it doubles", "it halves", "it is unchanged"], ans: 0,
        why: "At constant volume p ∝ T, with T in kelvin." },
    ],
  },

  /* ------------------------------------------------------------------ K */
  K: {
    prereq: `<p>Nuclear notation — being able to read <code>ᴬZX</code> and say how many protons and neutrons that is. Plus the ability to halve a number repeatedly without a calculator, since that is all half-life questions ask.</p>
<p>Toolkit first. Standard form is not optional here.</p>`,
    before: ["A"],
    starter: [
      { q: "An alpha particle is…", opts: ["a helium nucleus", "an electron", "a proton"], ans: 0,
        why: "⁴₂He: two protons and two neutrons." },
      { q: "After three half-lives, what fraction of a sample remains?", opts: ["1/8", "1/3", "1/6"], ans: 0,
        why: "½ × ½ × ½ = ⅛. Halve once per half-life." },
      { q: "In beta-minus decay, what happens to the nucleon number?", opts: ["it is unchanged", "it falls by 1", "it falls by 4"], ans: 0,
        why: "A neutron becomes a proton, so A is unchanged and Z rises by one." },
    ],
  },

  /* ------------------------------------------------------------------ L */
  L: {
    prereq: `<p>Energy in joules and in electron-volts, and comfort with very small numbers. The conceptual hurdle is accepting that light arrives in packets: one photon gives all its energy to one electron, and intensity changes how many packets arrive, not how much each carries.</p>
<p>Toolkit first — <code>hc = 1240 eV nm</code> only helps if standard form is second nature.</p>`,
    before: ["A"],
    starter: [
      { q: "The energy of a photon of frequency f is…", opts: ["hf", "hλ", "h/f"], ans: 0,
        why: "E = hf, equivalently E = hc/λ." },
      { q: "In the photoelectric effect, increasing the intensity at fixed frequency increases…", opts: ["the number of electrons emitted per second", "the maximum kinetic energy of each electron", "both"], ans: 0,
        why: "More photons, same energy each. The maximum kinetic energy depends on frequency alone." },
      { q: "Halving the wavelength of light makes the photon energy…", opts: ["twice as large", "half as large", "unchanged"], ans: 0,
        why: "E = hc/λ, so energy is inversely proportional to wavelength." },
    ],
  },

  /* ------------------------------------------------------------------ M */
  M: {
    prereq: `<p>Pressure as force per unit area, and density. The new idea is Archimedes' principle: upthrust equals the weight of fluid displaced. Most floating questions are that one sentence plus algebra.</p>
<p>Forces first — you will resolve forces on a floating or submerged object.</p>`,
    before: ["C"],
    starter: [
      { q: "The pressure at depth h in a liquid of density ρ is…", opts: ["ρgh", "ρg/h", "ρh/g"], ans: 0,
        why: "The weight of the column of liquid above, per unit area." },
      { q: "The upthrust on a submerged object equals…", opts: ["the weight of fluid displaced", "the weight of the object", "the object's mass × g"], ans: 0,
        why: "Archimedes' principle. Note it is the fluid's density that sets the upthrust, not the object's." },
      { q: "A block floats with three quarters of its volume submerged. What is its density relative to the fluid?", opts: ["three quarters", "four thirds", "one half"], ans: 0,
        why: "Floating: weight = upthrust, so ρ_object V = ρ_fluid × (¾ V), giving ρ_object = ¾ ρ_fluid." },
    ],
  },

  /* ------------------------------------------------------------------ N */
  N: {
    prereq: `<p><b>Read this module last, and only if the rest is secure.</b> It is insurance against BPhO Round 1 material appearing in Round 0, not core content. Circular motion and waves first: SHM is what you get when you project circular motion onto a line.</p>
<p>If you are scoring below about 14/25 on mocks, this module is not where your next hour should go.</p>`,
    before: ["D", "F"],
    starter: [
      { q: "In simple harmonic motion, how does the acceleration relate to the displacement?", opts: ["proportional to it and opposite in direction", "proportional to it and in the same direction", "constant"], ans: 0,
        why: "a = −ω²x. The minus sign is what makes it an oscillation rather than an exponential runaway." },
      { q: "The period of a simple pendulum depends on…", opts: ["its length and g", "its mass and length", "its amplitude"], ans: 0,
        why: "T = 2π√(L/g). Mass and (small) amplitude do not appear — but g does, which surprises people." },
      { q: "In SHM, where is the speed greatest?", opts: ["at the equilibrium position", "at the extremes", "a quarter of the way out"], ans: 0,
        why: "All the energy is kinetic at the centre; at the extremes the speed is momentarily zero." },
    ],
  },
};
