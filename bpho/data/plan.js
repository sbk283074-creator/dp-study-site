/* BPhO Round 0 — the 14-day plan.
   Day 1 = 16 September 2026. Day 14 = 29 September 2026.
   Non-UK sitting is 2 October, so 30 Sep – 1 Oct are buffer. */

window.BPHO_PLAN = [

  {
    day: 1, date: "Wed 16 Sep", mins: 150,
    title: "The toolkit, part 1 — units and dimensional analysis",
    focus: "Nothing else on this list works until these are automatic. Dimensional analysis is roughly one question in six on the sample paper and AQA explicitly does not teach it, so this is pure added value.",
    mods: ["A"],
    tasks: [
      "Learn the seven SI base units and the prefixes from tera to femto. Write them out from memory three times.",
      "Practise reducing N, J, W, Pa, C, V, Ω, F, T to base units until you can do any of them in under 20 seconds.",
      "Dimensional analysis proper: derive the form of a relationship by balancing base units. Do the period-of-a-pendulum and speed-of-a-wave-on-a-string derivations on blank paper.",
      "Dimensional consistency checking: take five equations you know and prove each one balances; then take three wrong ones and find the offending term.",
      "Work A1–A6 in the checklist, then do the module A practice questions tagged core."
    ]
  },

  {
    day: 2, date: "Thu 17 Sep", mins: 150,
    title: "The toolkit, part 2 — ratio reasoning and estimation; capacitors",
    focus: "Most Round 0 questions ask for a ratio, which means the shared constants cancel and you never touch a calculator. Then the shortest module in the whole paper.",
    mods: ["A", "I"],
    tasks: [
      "Ratio reasoning drill: for each of the four uniform-acceleration equations, work out how s, v and t change when u doubles, or a halves. Never compute a value.",
      "Memorise the six small-parameter approximations. Then do the geometric one — √(a²+d²) − a ≈ d²/2a — from scratch using the binomial expansion, so you can rebuild it if you forget.",
      "Order-of-magnitude practice: estimate the number of breaths in a lifetime, the mass of the atmosphere, the power of a human heart. Get within a factor of three.",
      "Graph-shape reasoning: sketch v against t for five motions you can describe in words. Then do the reverse — read a graph and say what the object did.",
      "Capacitors: Q = CV, series and parallel combinations, energy ½QV = ½CV², and the farad in base units. This is a 45-minute module. Do I1–I4.",
      "Module A and I practice questions."
    ]
  },

  {
    day: 3, date: "Fri 18 Sep", mins: 150,
    title: "Cheap wins — quantum phenomena and fluids",
    focus: "Two short modules that BPhO names explicitly. Both are formula-light and near-certain to appear. Take the marks cheaply and bank them.",
    mods: ["L", "M"],
    tasks: [
      "Photon model: E = hf = hc/λ. Convert between eV and joules until it is reflex.",
      "Photoelectric effect from first principles: why intensity cannot change the maximum kinetic energy but frequency can. Be able to explain this in two sentences.",
      "hf = φ + Ek(max). Threshold frequency, work function, stopping potential — and the graph of Ek against f, whose gradient is h and intercept is −φ.",
      "de Broglie λ = h/mv and electron diffraction. Line spectra as evidence for discrete levels, hf = E₁ − E₂.",
      "Fluids: pressure with depth, Archimedes' principle, floating and sinking, apparent weight when immersed, density by weighing in water.",
      "Modules L and M practice questions."
    ]
  },

  {
    day: 4, date: "Sat 19 Sep", mins: 165,
    title: "Circuits, part 1 — the foundations",
    focus: "The single highest-frequency topic in the paper: roughly one question in five. Two days is the right allocation. Today is everything except the awkward network problems.",
    mods: ["H"],
    tasks: [
      "Definitions from the ground up: I = ΔQ/Δt, V = W/Q, R = V/I. Say out loud what each one means physically, not just how to compute it.",
      "I–V characteristics of an ohmic conductor, a filament lamp and a semiconductor diode. Sketch all three and explain the shape of each.",
      "Resistivity ρ = RA/L, and why metal resistance rises with temperature. Then thermistors and LDRs, including their use in potential dividers.",
      "Superconductivity: critical temperature, zero resistance, and the applications. This is inside AQA AS §3.5.1.3, so it counts as Year 12 material.",
      "Series and parallel rules for resistance, current and voltage. Cells in series and identical cells in parallel.",
      "Power and energy: E = IVt and P = IV = I²R = V²/R. Know when each form is the convenient one.",
      "Work H1–H6 and H8, H9 in the checklist. Then the core module H practice questions."
    ]
  },

  {
    day: 5, date: "Sun 20 Sep", mins: 165,
    title: "Circuits, part 2 — the questions that actually get asked",
    focus: "The sample paper's circuit questions were not standard textbook exercises. They were: a cell reconfigured from series to parallel, two opposing EMFs in one loop, and a cell with internal resistance. Learn those three shapes.",
    mods: ["H"],
    tasks: [
      "Kirchhoff's laws as conservation of charge and conservation of energy. Use them to solve a two-loop circuit without any shortcut.",
      "EMF and internal resistance: ε = I(R + r), terminal potential difference, and the graph of terminal p.d. against current. Do the derivation, not just the formula.",
      "The reconfiguration problem: the same cell placed in series versus in parallel across the same pair of resistors. Work out the ratio of power dissipated in each case symbolically.",
      "Two opposing EMFs in a single loop: determine the direction and magnitude of the current, and then the power in each element.",
      "Diodes in AC circuits and half-wave rectification; average power for a square supply versus a sinusoidal one. Note that a sinusoidal average over a half-cycle is not zero and is not V₀/2.",
      "Equivalent resistance of awkward networks: a bridge, a square with both diagonals, a sliding contact round a loop.",
      "Work H10–H15, H17 in the checklist. Then the extension and challenge module H practice questions."
    ]
  },

  {
    day: 6, date: "Mon 21 Sep", mins: 150,
    title: "Kinematics — mostly revision, but at speed",
    focus: "You have done all of this in Chinese schooling. The content is not the problem; doing it in 2.4 minutes without a calculator is. Today is about fluency and about the multi-phase problems that BPhO likes.",
    mods: ["B"],
    tasks: [
      "The four uniform-acceleration equations, and — more usefully — knowing which one to reach for based on what is missing from the question.",
      "Motion graphs: gradient of s–t is velocity, gradient of v–t is acceleration, area under v–t is displacement. Do not re-derive this; make it instant.",
      "Multi-phase motion: accelerate, then constant, then decelerate, then return. Solve by eliminating time rather than by chaining equations.",
      "Projectile motion: independence of the horizontal and vertical directions, launch from a height, and landing on a slope.",
      "Relative motion: bearings, range-and-bearing problems, closing speed. This is genuinely new relative to the IB, and it is cheap once you see it as vector subtraction.",
      "Terminal speed and drag, qualitatively. Free fall and energy retention on successive bounces.",
      "Module B practice questions, all of them, timed at 2.5 minutes each."
    ]
  },

  {
    day: 7, date: "Tue 22 Sep", mins: 165,
    title: "Forces and momentum",
    focus: "Large module, familiar content. Today is the first-principles rebuild: vectors, Newton's laws, connected bodies, then the momentum family.",
    mods: ["C"],
    tasks: [
      "Vectors: addition, resolution into perpendicular components, and components on an inclined plane. Be able to resolve without drawing a triangle every time.",
      "Equilibrium of two or three coplanar forces at a point, and the closed triangle of forces. Spot the questions where the triangle is 3–4–5 or equilateral.",
      "Newton's three laws, F = ma, and free-body diagrams. Draw the diagram before writing any equation, every time.",
      "Connected bodies: pulleys, chains of blocks, towing, and lifts with apparent weight. This is Sample S12 and it recurs.",
      "Friction, qualitatively and quantitatively. Be able to say what changes when a surface is lubricated.",
      "Momentum p = mv and conservation in one dimension; elastic versus inelastic collisions; explosions. Then F = Δ(mv)/Δt, impulse FΔt = Δ(mv), and the area under a force–time graph.",
      "Work C1–C9 in the checklist, then the module C practice questions tagged core and extension."
    ]
  },

  {
    day: 8, date: "Wed 23 Sep", mins: 150,
    title: "Energy, work and power",
    focus: "The energy family is where ratio reasoning pays off most: questions ask how far something travels when its speed doubles, not what the distance is.",
    mods: ["C"],
    tasks: [
      "Work W = Fs cos θ, and the area under a force–displacement graph as work done by a variable force.",
      "Power P = ΔW/Δt = Fv. Know why the second form is the one for a vehicle at constant speed against drag.",
      "Conservation of energy with ΔEp = mgΔh and Ek = ½mv², including energy lost to resistive forces. Track where the energy went, not just how much.",
      "Efficiency as useful output over input, and the fact that it can never exceed one.",
      "Ratio practice: what happens to the stopping distance when the speed doubles? When the mass doubles? Answer without numbers.",
      "Work C10–C13 in the checklist, then the module C practice questions tagged core and challenge."
    ]
  },

  {
    day: 9, date: "Thu 24 Sep", mins: 165,
    title: "Moments, centre of mass, and materials",
    focus: "Moments-by-axis is the single technique that unlocks the whole statics family, and the sample paper tested it. Materials is short but contains two things the IB never teaches you.",
    mods: ["C", "E"],
    tasks: [
      "Moment of a force as F × perpendicular distance; the principle of moments; couples. Then the technique itself: choose the axis that makes an unknown vanish, and say why that is allowed.",
      "Multi-support equilibrium. Work through a plank on two supports, a ladder against a wall, and a hinged rod. For each, state which axis you chose and what it killed.",
      "Centre of mass of uniform regular solids and composite bodies; combined centre-of-mass and moments problems with an added mass.",
      "Density ρ = m/V, and finding density by weighing an object in water.",
      "Hooke's law F = kΔL, stiffness, springs in series and parallel, and elastic strain energy ½FΔL = ½kx² as the area under a force–extension graph.",
      "Stress and strain, and Young's modulus E = FL/(AΔL). Stress–strain graphs, elastic versus plastic, brittle fracture, breaking stress. The IB does not teach this.",
      "Thermal expansion ℓ = ℓ₀(1 + αΔT), then a combined expansion-and-Young's-modulus problem such as an expansion gap in a rail. Also not in the IB.",
      "Work C15–C19 and E1–E11 in the checklist, then the module C and E practice questions."
    ]
  },

  {
    day: 10, date: "Fri 25 Sep", mins: 165,
    title: "Circular motion and waves",
    focus: "Both are pattern topics: once you recognise the shape, the algebra is short. Circular motion is named in the official scope even though AQA files it under Year 13, and the sample paper tested it.",
    mods: ["D", "F"],
    tasks: [
      "Angular speed ω = v/r = 2πf and radian measure. Be able to switch between revs per minute and radians per second without thinking.",
      "Centripetal acceleration a = v²/r = ω²r, and the force F = mv²/r. Understand that the force is not a new force — it is whatever force is already acting, redirected.",
      "Force resolution for circular motion: the conical pendulum and a string at an angle, then find the period. This is the standard question shape.",
      "Vertical circles and the minimum speed at the top of a loop; banking and cornering; the lean angle of a cyclist.",
      "Apparent weight against latitude, poles versus equator — Sample S11.",
      "Waves: v = fλ, f = 1/T, phase difference in radians, degrees and fractions of a cycle. Longitudinal versus transverse and polarisation as evidence.",
      "Stationary waves on strings, L = nλ/2, harmonics, and the first-harmonic frequency f = (1/2ℓ)√(T/μ). Stationary waves in pipes, open and closed.",
      "The wave equation y = A cos(ωt + kx) and the classic trap of maximum particle speed ωA versus wave speed v. They are different quantities and options will mix them.",
      "Modules D and F practice questions."
    ]
  },

  {
    day: 11, date: "Sat 26 Sep", mins: 165,
    title: "Optics",
    focus: "A formulaic module. Refraction and total internal reflection are near-guaranteed; the interference material is where the competition-style thinking lives.",
    mods: ["G"],
    tasks: [
      "Refractive index n = c/c_s and Snell's law n₁ sin θ₁ = n₂ sin θ₂. Note that n of air is 1 and BPhO will expect you to use that.",
      "Total internal reflection and the critical angle sin θ_c = n₂/n₁ — Sample S8. Practise finding the range of angles for which a ray emerges.",
      "Prisms: refraction through two faces, the range of incident angles that allow emergence, and the minimum-deviation idea.",
      "Optical fibres: step index, cladding, material and modal dispersion, pulse broadening, absorption. Mostly descriptive, so learn the vocabulary.",
      "Path difference and coherence. Then Young's double slit, fringe spacing w = λD/s, and what happens to the fringes in white light — Sample S4.",
      "Single-slit diffraction, qualitatively: how the central maximum width depends on λ and on slit width. Then the diffraction grating d sin θ = nλ.",
      "Module G practice questions."
    ]
  },

  {
    day: 12, date: "Sun 27 Sep", mins: 150,
    title: "Nuclear physics, then thermal",
    focus: "Nuclear is small and self-contained; only K1–K6 and K14 are in scope. Thermal is last on purpose — its evidence is the weakest on the whole list, so it must not displace anything above it.",
    mods: ["K", "J"],
    tasks: [
      "Nuclear notation ᴬ_Z X, proton number, nucleon number, isotopes. Then specific charge of nuclei and ions, and the charge and mass of the proton, neutron and electron — Sample S1.",
      "Alpha and beta decay equations, and why beta-minus decay requires an antineutrino. The strong force: short-range attraction around 3 fm, very-short-range repulsion around 0.5 fm.",
      "Properties, absorption and relative hazard of alpha, beta and gamma. Background radiation, and how to subtract it from a count rate.",
      "Specific heat capacity Q = mcΔT and specific latent heat Q = mL. Calorimetry and energy balance in a mixture — the classic problem is a hot object dropped into cold water.",
      "The ideal gas law pV = nRT and simple processes with pV constant. Pressure, force and equilibrium in pistons and diaphragms.",
      "Thermal expansion as a second visit, now linked to stress. If a rod is constrained, expansion becomes stress — work out the stress for a given temperature rise.",
      "Work K1–K6, K14 and J1–J3, J5–J7, J9 in the checklist, then the module K and J practice questions."
    ]
  },

  {
    day: 13, date: "Mon 28 Sep", mins: 120,
    title: "Full timed mock — the real thing",
    focus: "Today is a rehearsal, not a study day. The point is to find out what the clock does to you, because that is the constraint that decides the score.",
    mods: [],
    tasks: [
      "Start the 25-question mock from the Practice page. Phone away, calculator away, paper and pen only. 60 minutes, hard stop.",
      "Mark it immediately and write down the score before looking at anything else.",
      "Go through every question you got wrong and classify the miss: did not know it, knew it but too slow, misread the question, or arithmetic slip. The four have different fixes.",
      "Re-do the ones you knew but ran out of time on, untimed, to confirm the knowledge is actually there.",
      "For anything in the did-not-know category, go straight back to that module and re-read only that section.",
      "Do not learn anything new today."
    ]
  },

  {
    day: 14, date: "Tue 29 Sep", mins: 120,
    title: "Repair and technique — the last day",
    focus: "No new content. Fix the misses from yesterday, drill the numbers, and make the exam technique automatic so the clock stops costing you marks.",
    mods: [],
    tasks: [
      "Re-read the reference page: the paper format, the constants, and the approximation list. Say the approximation list out loud from memory.",
      "Drill the constants that come up most: g, c, e, h, the eV conversion, Earth's radius, the length of a day. You should be able to quote all of them.",
      "Re-do every practice question you have ever got wrong on this site. Not the ones you got right.",
      "Technique rehearsal on ten fresh questions: for each one, before calculating, ask whether a ratio would do, whether dimensional analysis would do, and whether two options can be killed by a limiting case.",
      "Confirm your sitting details — date, time, venue, permitted materials, and whether the formula booklet is supplied or you bring your own.",
      "Close the laptop by early evening. Sleep is worth more than one more past paper.",
      "If and only if everything above is genuinely finished, skim module N for insurance. It is Round 1 material and is not required for 11/25."
    ]
  },

  {
    day: 15, date: "Wed 30 Sep", mins: 90,
    title: "Buffer day (only if your sitting is 2 October)",
    focus: "There is a two-day gap between Day 14 and the non-UK sitting on 2 October. Use it, but lightly — this is the point where extra work starts to cost more than it gains.",
    mods: [],
    tasks: [
      "A second timed mock, ideally a different random draw from the bank. Mark it and compare with Day 13.",
      "Only if the second score is below the first, spend an hour on the topic where the losses cluster. Otherwise stop.",
      "Light review of the approximation list and the constants. Nothing new.",
      "Rest. Do not attempt to learn a new module in the last 48 hours."
    ]
  },

  {
    day: 16, date: "Thu 1 Oct", mins: 45,
    title: "Rest and logistics",
    focus: "Deliberately near-empty. The last day before the paper should be administration and sleep, not physics.",
    mods: [],
    tasks: [
      "Confirm the logistics: time, venue, transport, what you are allowed to bring.",
      "Skim the reference page once, slowly, and then stop.",
      "No practice questions. No new content.",
      "Sleep early."
    ]
  }

];
