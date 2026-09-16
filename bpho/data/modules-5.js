/* BPhO Round 0 — curriculum, part 5 of 6.
   Modules D (circular motion) and E (materials and elasticity). */

window.BPHO_MODULES = (window.BPHO_MODULES || []).concat([

{
  code: "D",
  title: "Mechanics — circular motion",
  short: "Circular motion",
  priority: 3,
  tier: "Tier A — named in the official Round 0 scope, and tested by sample question S11",
  why: "Officially named in the Round 0 scope, even though AQA files circular motion under Year 13. That discrepancy is a gift: it means the topic is definitely in play while many candidates will not have covered it. It is also formulaic — once you recognise the shape, the algebra is two lines.",
  warn: "<p><b>Gravitational fields are excluded, but orbital ratios are fair.</b> BPhO rules out gravitational fields as a topic. However, you can still be asked about the <i>ratio</i> of two orbital periods by equating <code>mv²/r</code> to <code>mg</code> at the surface — that is circular motion, not field theory. Do not stray into potential or escape velocity.</p>",

  sections: [
    {
      h: "Angular speed and radians",
      body: `<p>For motion in a circle, it is more natural to describe rotation by angle than by distance. The <b>angular speed</b> <code>ω</code> is the rate of change of angle, measured in radians per second.</p>
<div class="formula">ω = v/r = 2πf = 2π/T</div>
<p>where <code>v</code> is the linear speed, <code>r</code> the radius, <code>f</code> the frequency in revolutions per second, and <code>T</code> the period.</p>
<h3>Why radians and not degrees</h3>
<p>A radian is defined so that the arc length equals the radius: <code>s = rθ</code>. That clean relationship is what makes <code>ω = v/r</code> true without any conversion factor. In degrees the same relationship would need a factor of <code>π/180</code>, which is why every formula in this module assumes radians.</p>
<div class="formula">2π radians = 360°        1 rad ≈ 57.3°</div>
<div class="callout callout--key"><p><b>The conversion worth being able to do in your head.</b> Revs per minute to radians per second: multiply by <code>2π/60 ≈ 0.105</code>. So 3000 rpm is about <code>3000 × 0.105 = 315 rad s⁻¹</code>. That estimate is usually enough to choose between options.</p></div>`
    },

    {
      h: "Centripetal acceleration",
      body: `<p>An object moving in a circle at constant <i>speed</i> is still accelerating, because its <i>velocity</i> is changing direction. The acceleration points towards the centre of the circle, and its magnitude is</p>
<div class="formula">a = v²/r = ω²r</div>
<h3>Where the formula comes from</h3>
<p>Take two instants separated by a small time <code>Δt</code>, during which the object turns through a small angle <code>Δθ</code>. The velocity vector has constant magnitude <code>v</code> but has rotated through <code>Δθ</code>, so the change in velocity has magnitude</p>
<div class="formula">Δv ≈ v Δθ</div>
<p>because a small rotation of a vector of length <code>v</code> changes it by <code>v</code> times the angle, exactly as a small arc of a circle of radius <code>v</code>. Dividing by the time:</p>
<div class="formula">a = Δv/Δt = v (Δθ/Δt) = vω</div>
<p>And since <code>ω = v/r</code>, this gives <code>a = v²/r</code> ✓.</p>
<div class="callout callout--key"><p><b>The direction is the whole point.</b> The acceleration is perpendicular to the velocity at every instant, pointing at the centre. That is why the <i>speed</i> stays constant while the velocity changes — a force perpendicular to the motion does no work, so kinetic energy is unchanged. This connection to the work–energy idea is worth stating explicitly if a question asks you to explain why the speed does not change.</p></div>
<h3>The two forms of the acceleration, and why both are right</h3>
<p>You will see <code>a = v²/r</code> and <code>a = ω²r</code>. They are identical: substitute <code>v = ωr</code> into the first and you get <code>(ωr)²/r = ω²r</code>. Use whichever the question hands you. If angular speed is given, use <code>ω²r</code> directly and skip converting to <code>v</code> — fewer steps, fewer slips.</p>
<div class="callout callout--warn"><p><b>Acceleration, not force.</b> A frequent error is to write <code>mv²/r</code> and call it the acceleration. <code>mv²/r</code> has units of newtons; the acceleration is <code>v²/r</code> (m s⁻²). Keep the two separate: acceleration is what the velocity does, force is mass times that.</p></div>`
    },

    {
      h: "The centripetal force is not a new force",
      body: `<p>This is the single most important conceptual point in the module, and the one that competition questions target.</p>
<p>By Newton's second law, a body with acceleration <code>v²/r</code> must have a resultant force in that direction of magnitude</p>
<div class="formula">F = mv²/r = mω²r</div>
<p>But this is <b>not</b> an extra force to be added to the others. It is the <i>name for the resultant</i> of the forces that are already acting. The physics is always: identify the real forces, resolve towards the centre, set the total equal to <code>mv²/r</code>.</p>
<table><thead><tr><th>Situation</th><th>What supplies the centripetal force</th></tr></thead><tbody>
<tr><td>Car turning on a flat road</td><td>friction between the tyres and the road</td></tr>
<tr><td>Car turning on a banked track</td><td>the horizontal component of the normal contact force</td></tr>
<tr><td>Mass on a string swung in a circle</td><td>the tension in the string</td></tr>
<tr><td>Satellite in orbit</td><td>gravity</td></tr>
<tr><td>Electron in an atom (classical model)</td><td>the electrostatic attraction to the nucleus</td></tr>
<tr><td>Clothes in a spin dryer</td><td>the normal force from the drum wall</td></tr>
</tbody></table>
<div class="callout callout--bad"><p><b>The error to avoid.</b> Do not draw a "centripetal force" arrow on a free-body diagram alongside the tension and the weight. That double-counts. Draw only the real forces, then note that their resultant must be <code>mv²/r</code>.</p></div>
<div class="callout callout--warn"><p><b>On centrifugal force.</b> A question may mention it. In an inertial frame there is no outward force — the sensation of being pushed outward in a turning car is the consequence of your own inertia, not a force. If the question is set in a rotating frame then a centrifugal term is legitimate bookkeeping, but Round 0 works in inertial frames.</p></div>`
    },

    {
      h: "Force resolution for circular motion",
      body: `<p>This is the standard question shape and it is worth learning as a procedure.</p>
<h3>Horizontal circle: the conical pendulum</h3>
<p>A mass hangs on a string of length <code>ℓ</code> and swings in a horizontal circle, with the string making an angle <code>θ</code> to the vertical. Resolve vertically and horizontally.</p>
<p><b>Vertically</b>, there is no acceleration, so the vertical component of tension balances the weight:</p>
<div class="formula">T cos θ = mg</div>
<p><b>Horizontally</b>, the horizontal component of tension is the centripetal force. The radius of the circle is <code>r = ℓ sin θ</code>:</p>
<div class="formula">T sin θ = mv²/r = mω² ℓ sin θ</div>
<p>Dividing the second by the first eliminates <code>T</code> and the <code>sin θ</code> cancels:</p>
<div class="formula">tan θ = ω²ℓ sin θ / g   →   cos θ = g/(ω²ℓ)</div>
<p>And since <code>ω = 2π/T</code>, this gives the period of the conical pendulum:</p>
<div class="formula">T = 2π √(ℓ cos θ / g)</div>
<div class="callout callout--good"><p><b>Note what happened to the mass.</b> It cancelled completely. The period of a conical pendulum does not depend on the mass of the bob, exactly as for a simple pendulum. Whenever a mass cancels in a circular-motion problem, that is a signal the answer is robust and worth remembering.</p></div>
<h3>The general procedure</h3>
<ol class="steps">
<li>Draw the free-body diagram with only the real forces.</li>
<li>Resolve <b>vertically</b> and set it equal to zero (unless the motion is a vertical circle, in which case it is <code>mv²/r</code> at top and bottom only).</li>
<li>Resolve <b>horizontally towards the centre</b> and set it equal to <code>mv²/r</code>.</li>
<li>Divide one equation by the other to eliminate the unknown force — usually tension or the normal contact force.</li>
<li>Substitute <code>v = ωr</code> or <code>ω = 2π/T</code> to get the quantity asked for.</li>
</ol>`
    },

    {
      h: "Vertical circles",
      body: `<p>In a vertical circle the speed is not constant, and the centripetal force is the resultant of gravity and whatever else is acting. The question almost always asks about the <b>top</b> of the circle, because that is where the condition for completing the loop is decided.</p>
<h3>Minimum speed at the top of a loop</h3>
<p>At the top, gravity acts downward, towards the centre. If the object is on the inside of a track, the normal force also acts towards the centre. So</p>
<div class="formula">N + mg = mv²/r</div>
<p>The minimum speed for the object to stay in contact is the speed at which <code>N</code> just falls to zero — the object is on the verge of losing contact:</p>
<div class="formula">mg = mv²/r   →   v_min = √(gr)</div>
<p>Below this speed the object cannot complete the loop; it leaves the track.</p>
<div class="callout callout--key"><p><b>For a ball on a string rather than a track</b> the condition is the same but the reasoning differs slightly: the string can only pull, so the tension must be at least zero. The result <code>v_min = √(gr)</code> is identical. Note that the mass cancels in both cases — the minimum speed depends only on the radius.</p></div>
<h3>At the bottom</h3>
<p>At the bottom, gravity acts downward but the normal force acts upward, so</p>
<div class="formula">N − mg = mv²/r   →   N = m(g + v²/r)</div>
<p>The contact force is larger than the weight. This is why you feel heavier at the bottom of a dip in the road, and why a loop-the-loop track must be strongest at its lowest point.</p>
<h3>The energy link between bottom and top</h3>
<p>By conservation of energy, the speed needed at the bottom to just complete the loop is <code>√(5gr)</code>. The top needs <code>√(gr)</code>; rising through height <code>2r</code> costs kinetic energy <code>2mgr</code>. So <code>½m v_bottom² = ½m(gr) + 2mgr = 2.5 mgr</code>, giving <code>v_bottom = √(5gr)</code>. This is a favourite derivation and worth reproducing on blank paper.</p>
<div class="callout callout--warn"><p><b>String versus rigid track.</b> On the inside of a rigid track the normal force can point either way, so the limiting case is <code>N = 0</code> at the top. On a string the tension can only pull, never push, so the same <code>v = √(gr)</code> applies but for the opposite reason — the string goes slack if the speed drops below it. Same answer, mirror-image reasoning.</p></div>`
    },

    {
      h: "Banking and cornering",
      body: `<p>On a banked track the surface is tilted so that the normal contact force has a horizontal component pointing towards the centre of the turn. That component supplies the centripetal force, so friction is not needed at all at the design speed.</p>
<p>Resolve for a track banked at angle <code>θ</code>, with no friction:</p>
<div class="formula">Vertically:      N cos θ = mg
Horizontally:    N sin θ = mv²/r</div>
<p>Divide the second by the first:</p>
<div class="formula">tan θ = v²/(rg)</div>
<p>So the design speed for a given bank angle is <code>v = √(rg tan θ)</code>. Above that speed friction must help inward; below it, friction must act outward to stop the car sliding down the banking.</p>
<h3>The leaning cyclist</h3>
<p>A cyclist leaning into a turn at angle <code>θ</code> from the vertical has the same equation, <code>tan θ = v²/(rg)</code>. The reason is the same: the resultant of the normal force and friction must point from the contact point through the centre of mass, and that resultant supplies the centripetal force.</p>
<div class="callout callout--key"><p><b>The result worth memorising.</b> <code>tan θ = v²/(rg)</code> for both banking and leaning, with no dependence on mass. It is the same equation in two disguises, and recognising that saves you deriving it twice.</p></div>
<h3>What happens away from the design speed</h3>
<p>The equation <code>tan θ = v²/(rg)</code> holds only at the one speed where friction does nothing. Above it, friction must act down the slope (inward and downward) to add centripetal force; below it, friction acts up the slope to keep the car from sliding down the banking. A banked track is only "safe without friction" at a single speed.</p>
<div class="callout callout--bad"><p><b>Two slips to avoid.</b> First, applying a flat-road friction argument to a banked track and ignoring the horizontal component of the normal force. Second, writing <code>N = mg</code> on a bank — it is not, because part of the weight is balanced by the vertical component of <code>N</code> while part of <code>N</code> is horizontal. On a bank, <code>N = mg/cos θ</code>, which exceeds the weight.</p></div>`
    },

    {
      h: "Apparent weight and latitude",
      body: `<p>This was sample question S11, and it is a neat application of circular motion to a familiar situation.</p>
<p>A person standing on the Earth's surface is moving in a circle about the Earth's axis. At latitude <code>λ</code>, the radius of that circle is <code>R cos λ</code>, where <code>R</code> is the Earth's radius. So the person needs a centripetal force directed towards the axis.</p>
<p>The forces acting are the true weight <code>mg</code> (towards the Earth's centre) and the normal contact force <code>N</code> from the ground (radially outward). The resultant must point towards the axis. At the <b>equator</b>, <code>λ = 0</code>, the geometry is simplest:</p>
<div class="formula">mg − N = mω²R   →   N = m(g − ω²R)</div>
<p>So the apparent weight is <b>less</b> than the true weight at the equator.</p>
<p>At the <b>poles</b>, the person is on the axis of rotation, so the radius of the circular path is zero and no centripetal force is needed:</p>
<div class="formula">N = mg</div>
<p>So the apparent weight equals the true weight at the poles.</p>
<div class="callout callout--key"><p><b>The conclusion, and it is counter-intuitive.</b> You weigh slightly less at the equator than at the poles — about 0.3% less. Two effects contribute: the centripetal requirement reduces the normal force, and the Earth's equatorial bulge means <code>R</code> is larger there so <code>g</code> is smaller. A question may ask about either or both.</p></div>
<h3>Estimating the size of the effect</h3>
<p>With <code>ω = 2π/86400 ≈ 7.3 × 10⁻⁵ rad s⁻¹</code> and <code>R = 6.4 × 10⁶ m</code>:</p>
<div class="formula">ω²R ≈ (7.3 × 10⁻⁵)² × 6.4 × 10⁶ ≈ 3.4 × 10⁻² m s⁻²</div>
<p>That is about 0.34% of <code>g</code>, which is the size of the effect. Estimating it takes about thirty seconds with the powers of ten, and it is the kind of calculation a competition question will expect.</p>
<h3>The general case at latitude λ</h3>
<p>Away from the equator the path about the Earth's axis has radius <code>R cos λ</code>, so the required centripetal force is <code>mω²R cos λ</code> directed horizontally towards the axis. This has a component along the local vertical that reduces the normal force by roughly <code>mω²R cos²λ</code>. The effect is maximal at the equator and vanishes at the poles, matching the two limits already derived.</p>
<div class="callout callout--key"><p><b>Two effects, both reduce equatorial weight.</b> The centripetal effect found above removes about 0.34%. Separately, the Earth's spin makes it bulge, so <code>R</code> is larger at the equator and <code>g</code> is genuinely smaller there too — another ~0.2%. Knowing both lets you explain the full ~0.5% difference a question may ask about.</p></div>`
    },

    {
      h: "Orbital motion by equating forces",
      body: `<p>For a satellite in a circular orbit, gravity supplies the centripetal force. Writing <code>g</code> for the gravitational field strength at the orbital radius:</p>
<div class="formula">mg = mv²/r   →   v = √(gr)</div>
<p>The mass of the satellite cancels, which is why all satellites at the same altitude orbit at the same speed.</p>
<h3>The ratio technique, which is what Round 0 actually asks</h3>
<p>From <code>v = √(gr)</code> and <code>T = 2πr/v</code>:</p>
<div class="formula">T = 2π √(r³/g)</div>
<p>If two orbits have radii <code>r₁</code> and <code>r₂</code> and the field strength at each radius follows <code>g ∝ 1/r²</code>, then</p>
<div class="formula">T ∝ r^(3/2)</div>
<p>So a satellite at four times the orbital radius has a period <code>4^(3/2) = 8</code> times as long. That is Kepler's third law, and you have just derived it from circular motion alone — without any field theory.</p>
<div class="callout callout--warn"><p><b>Stay on the right side of the scope boundary.</b> BPhO excludes gravitational fields. Deriving <code>T ∝ r^(3/2)</code> from <code>mv²/r = mg</code> is circular motion and is fair. Discussing gravitational potential energy, escape velocity, or field lines is field theory and is not. If a question asks for a ratio of periods, do it this way.</p></div>`
    },

    {
      h: "Estimating in rotating systems — drums, centrifuges, swings",
      body: `<p>The circular-motion ideas above are most useful on the paper when they let you <b>estimate</b> an acceleration or force in an unfamiliar rotating situation. The recipe is always the same: find the radius, find the angular speed (often from a stated rpm), then compute <code>a = ω²r</code> or <code>F = mω²r</code>.</p>
<h3>The washing-machine drum</h3>
<p>A drum of radius 0.25 m spinning at 1200 rpm. Convert: <code>f = 1200/60 = 20 Hz</code>, so <code>ω = 2π × 20 ≈ 126 rad s⁻¹</code>. Then</p>
<div class="formula">a = ω²r ≈ (126)² × 0.25 ≈ 1.6 × 10⁴ × 0.25 ≈ 4 × 10³ m s⁻²</div>
<p>That is about 400 g — the clothes are pressed against the drum wall with a force some four hundred times their weight. This is exactly why water is forced out through the holes: the water cannot get the centripetal force it needs from the drum and so it travels straight, leaving the cloth behind.</p>
<h3>The laboratory centrifuge</h3>
<p>The same arithmetic explains why a centrifuge at, say, 10 000 rpm with a 0.10 m radius produces accelerations of order 10⁵ m s⁻² — enough to sediment particles that gravity alone would take days to settle. The point for the paper is not the biology but the scaling: acceleration grows with the <b>square</b> of the angular speed, so doubling the rpm quadruples the effective g.</p>
<div class="callout callout--key"><p><b>The estimation reflex.</b> When a rotating-system question gives you an rpm and a radius and asks for an acceleration or a multiple of g, your job is to convert rpm to Hz (divide by 60), multiply by 2π for ω, square it, and multiply by r. No mass needed for the acceleration; add the mass only if a force is asked for.</p></div>
<div class="callout callout--warn"><p><b>The units trap recurs here.</b> <code>ω²r</code> with ω in rpm gives a nonsense answer — rpm is not radians per second. The conversion <code>× 2π/60</code> is mandatory. A question that offers options differing by factors of 60 or 3600 is testing exactly whether you remembered it.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A car of mass 1200 kg goes round a bend of radius 50 m at a speed of 20 m s⁻¹. What is the minimum coefficient of friction between the tyres and the road needed to prevent skidding?</p><p>A) 0.20 &nbsp; B) 0.40 &nbsp; C) 0.80 &nbsp; D) 1.6 &nbsp; E) 4.0</p>",
      sol: `<p><b>Step 1 — the required centripetal force.</b></p>
<div class="formula">F = mv²/r = 1200 × 400/50 = 9600 N</div>
<p><b>Step 2 — the normal force.</b> On a flat road, <code>N = mg = 1200 × 10 = 12 000 N</code>.</p>
<p><b>Step 3 — the coefficient.</b> Friction must supply the centripetal force, so <code>μN ≥ mv²/r</code>:</p>
<div class="formula">μ ≥ 9600/12 000 = 0.80</div>
<p><b>Answer: C.</b></p>
<p><b>The shortcut, which avoids all the arithmetic.</b> Notice that the mass cancelled at step 3. In general:</p>
<div class="formula">μmg = mv²/r   →   μ = v²/(rg) = 400/(50 × 10) = 0.80</div>
<p>No mass, no force in newtons, and the whole thing is one line of mental arithmetic. This is exactly the ratio reasoning from module A: whenever you see a mass appearing on both sides, cancel it before substituting numbers.</p>
<p><b>The physical check.</b> A coefficient of 0.8 is high but achievable for a dry road on good tyres; wet roads are nearer 0.4, which is why the same bend at 20 m s⁻¹ would be marginal in the rain. Option B, 0.40, is the answer you would get if you forgot to square the speed, and it corresponds to a physically plausible wet-road value — which is what makes it a good distractor.</p>`,
      tag: "Cornering — with the mass cancelling"
    },
    {
      q: "<p>A ball on a string is swung in a vertical circle of radius 0.80 m. What is the minimum speed it must have at the top of the circle to maintain contact with the circular path? Use <code>g = 10 m s⁻²</code>.</p><p>A) 2.0 m s⁻¹ &nbsp; B) 2.8 m s⁻¹ &nbsp; C) 4.0 m s⁻¹ &nbsp; D) 8.0 m s⁻¹ &nbsp; E) 16 m s⁻¹</p>",
      sol: `<p>At the top of the circle, gravity acts towards the centre. The minimum speed is the one at which the tension just falls to zero — the ball is on the verge of leaving the circular path:</p>
<div class="formula">mg = mv²/r   →   v² = gr</div>
<div class="formula">v = √(10 × 0.80) = √8 ≈ 2.8 m s⁻¹</div>
<p><b>Answer: B.</b></p>
<p><b>The mass cancels, again.</b> Notice that the answer does not depend on the mass of the ball at all — only on the radius and <code>g</code>. A heavy ball and a light ball need the same minimum speed.</p>
<p><b>The trap.</b> Option C, 4.0 m s⁻¹, is <code>gr</code> rather than <code>√(gr)</code> — the answer you get from forgetting the square root. Option D, 8.0 m s⁻¹, is <code>2gr</code> and is close to the answer for a different question: the minimum speed at the <i>bottom</i> needed to reach the top. Keeping those two results apart is worth a moment's care.</p>
<p><b>The related result worth knowing.</b> By conservation of energy, the speed at the bottom must be <code>√(5gr)</code> for the ball to just complete the loop, which for <code>r = 0.80 m</code> is <code>√40 ≈ 6.3 m s⁻¹</code>. The factor of 5 comes from combining the energy change over a height of <code>2r</code> with the minimum top speed — a standard derivation and a good exercise.</p>`,
      tag: "Vertical circle — minimum speed at the top"
    },
    {
      q: "<p>A conical pendulum has a string of length 0.50 m making an angle of 60° with the vertical. What is its period? Use <code>g = 10 m s⁻²</code> and take <code>π ≈ 3.1</code>.</p><p>A) 0.79 s &nbsp; B) 1.0 s &nbsp; C) 1.4 s &nbsp; D) 1.6 s &nbsp; E) 2.2 s</p>",
      sol: `<p>Use the result derived in the module:</p>
<div class="formula">T = 2π √(ℓ cos θ / g)</div>
<p>With <code>cos 60° = 0.50</code>:</p>
<div class="formula">ℓ cos θ = 0.50 × 0.50 = 0.25 m
T = 2 × 3.1 × √(0.25/10) = 6.2 × √0.025</div>
<p>And <code>√0.025 = 0.158</code>, so</p>
<div class="formula">T ≈ 6.2 × 0.158 ≈ 0.98 s</div>
<p><b>Answer: B, approximately 1.0 s.</b></p>
<p><b>The sanity check.</b> Note that <code>ℓ cos θ</code> is the <b>vertical height</b> of the bob below the suspension point — here <code>0.50 × 0.50 = 0.25 m</code>. So the conical pendulum has exactly the same period as a simple pendulum of length 0.25 m. That equivalence is the cleanest way to remember the formula: <i>a conical pendulum behaves like a simple pendulum whose length is the vertical drop</i>.</p>
<p>A simple pendulum of length 0.25 m has period <code>2π√(0.25/10) = 2π × 0.158 ≈ 1.0 s</code> ✓.</p>
<p><b>The trap.</b> Option A, 0.79 s, comes from using <code>ℓ = 0.50 m</code> directly without the <code>cos θ</code> factor. Option D, 1.6 s, comes from using <code>ℓ/cos θ = 1.0 m</code> instead of <code>ℓ cos θ</code> — dividing where you should multiply. Both are the same kind of error, and both are prevented by the physical reading: the bob sits 0.25 m below the pivot, so the effective length is 0.25 m.</p>`,
      tag: "Conical pendulum — the effective-length insight"
    },
    {
      q: "<p>Two satellites orbit the Earth in circular orbits. Satellite B orbits at four times the radius of satellite A. What is the ratio of the period of B to the period of A?</p><p>A) 2 &nbsp; B) 4 &nbsp; C) 6 &nbsp; D) 8 &nbsp; E) 16</p>",
      sol: `<p>Start from the force balance: gravity supplies the centripetal force.</p>
<div class="formula">mg = mv²/r   →   v = √(gr)</div>
<p>Now use the period, <code>T = 2πr/v</code>, and substitute for <code>v</code>:</p>
<div class="formula">T = 2πr/√(gr) = 2π √(r/g)</div>
<p>Since the field strength itself follows <code>g ∝ 1/r²</code>, we get <code>√(r/g) ∝ √(r · r²) = r^(3/2)</code>. So</p>
<div class="formula">T ∝ r^(3/2)</div>
<p>Taking the ratio with <code>r_B = 4r_A</code>:</p>
<div class="formula">T_B/T_A = 4^(3/2) = (√4)³ = 2³ = 8</div>
<p><b>Answer: D.</b></p>
<p><b>The trap.</b> Option B, 4, is what you get by assuming the period is proportional to the radius — a linear guess. Option E, 16, comes from using <code>r²</code>, which is the field-strength dependence rather than the period dependence. Option A, 2, is <code>√4</code>, the result of forgetting that the period has both the <code>2πr</code> factor and the <code>1/v</code> factor.</p>
<p><b>What this is and is not.</b> This is Kepler's third law, derived from circular motion alone. It uses only <code>mv²/r = mg</code> and <code>g ∝ 1/r²</code>, which are fair game. If you find yourself writing <code>GMm/r²</code> with the gravitational constant, you have moved into field theory, which BPhO excludes from Round 0 — the derivation above avoids that entirely.</p>
<p><b>The physical reading.</b> A satellite eight times further out takes eight times as long. The Moon, at about 60 Earth radii, has a period of about 27 days, and <code>60^(3/2) ≈ 465</code> times the period of a low-Earth satellite of about 90 minutes gives roughly 29 days — close enough to confirm the law with a rough mental estimate.</p>`,
      tag: "Orbital period ratio — Kepler from circular motion"
    },

    {
      q: "<p>Two objects, 1 and 2, each move in a horizontal circle of the same radius <code>R</code> and have the same mass <code>m</code>. The centripetal force on object 2 is four times that on object 1. What is the ratio <code>v₂/v₁</code> of their speeds?</p><p>A) 1 &nbsp; B) 2 &nbsp; C) 4 &nbsp; D) ½ &nbsp; E) 16</p>",
      sol: `<p>Centripetal force is <code>F = mv²/r</code>. With the same mass and the same radius, <code>F ∝ v²</code>, so <code>v ∝ √F</code>.</p>
<div class="formula">v₂/v₁ = √(F₂/F₁) = √4 = 2</div>
<p><b>Answer: B, 2.</b></p>
<p><b>The trap.</b> Option C, 4, is the ratio of the <i>forces</i>, offered to anyone who forgets that speed enters as a <i>square</i> and so the speed ratio is the <i>square root</i> of the force ratio. Option A, 1, would follow from thinking the speed is independent of the force. Option D, ½, is the inverse, the result of flipping the ratio. Option E, 16, is the force ratio squared — a double squaring error.</p>
<p><b>The physical reading.</b> Doubling the speed quadruples the required centripetal force. This is the same <code>v²</code> dependence that makes stopping distance grow with the square of the speed, and it is why a small increase in cornering speed demands a much larger frictional grip from the tyres.</p>`,
      tag: "Ratio of speeds for the same radius — the v² dependence"
    },

    {
      q: "<p>A roller-coaster car of mass <code>500 kg</code> passes over the top of a vertical loop of radius <code>8.0 m</code> at a speed of <code>12 m s⁻¹</code>. Take <code>g = 10 m s⁻²</code>. What is the normal force exerted by the track on the car at the top?</p><p>A) 1000 N &nbsp; B) 4000 N &nbsp; C) 5000 N &nbsp; D) 9000 N &nbsp; E) 14000 N</p>",
      sol: `<p>At the top of the loop both gravity and the normal force point towards the centre, so they add to supply the centripetal force:</p>
<div class="formula">N + mg = mv²/r</div>
<p>Solve for N:</p>
<div class="formula">N = m(v²/r − g) = 500 × (144/8.0 − 10) = 500 × (18 − 10) = 500 × 8 = 4000 N</div>
<p><b>Answer: B, 4000 N.</b></p>
<p><b>The traps.</b> Option C, 5000 N, is just the weight <code>mg</code> — the mistake of thinking the track only has to support the car's weight. Option D, 9000 N, is the full centripetal force <code>mv²/r = 500 × 18</code> — the error of forgetting to subtract the weight, i.e. treating gravity as if it acted outward. Option E, 14000 N, is <code>mv²/r + mg</code>, a sign error from writing <code>N − mg = mv²/r</code> (the bottom-of-the-loop equation) at the top. Keep the geometry straight: at the top both forces point inward and add.</p>
<p><b>The sanity check.</b> The centripetal force needed is 9000 N and gravity already supplies 5000 N of it, so the track need only supply the remaining 4000 N. That is why a car can stay on the track at the top even when it feels lightest — gravity is doing most of the turning.</p>`,
      tag: "Force needed in a loop — normal force at the top"
    },

    {
      q: "<p>A conical pendulum has a string of length <code>1.2 m</code>. The bob moves in a horizontal circle of radius <code>0.60 m</code>. What angle does the string make with the vertical?</p><p>A) 30° &nbsp; B) 45° &nbsp; C) 60° &nbsp; D) 90° &nbsp; E) 26.6°</p>",
      sol: `<p>In a conical pendulum the radius of the horizontal circle is the horizontal component of the string: <code>r = ℓ sin θ</code>. Hence</p>
<div class="formula">sin θ = r/ℓ = 0.60/1.2 = 0.50   →   θ = 30°</div>
<p><b>Answer: A, 30°.</b></p>
<p><b>The traps.</b> Option C, 60°, comes from writing <code>cos θ = r/ℓ</code> — confusing the adjacent and opposite sides of the triangle. Option E, 26.6°, comes from using <code>tan θ = r/ℓ = 0.5</code>; that is the wrong ratio because <code>tan θ = r / (vertical drop)</code>, not <code>r/ℓ</code>. Option D, 90°, would mean the string horizontal, which is impossible for a real conical pendulum because then tension could have no vertical component to balance the weight. Always draw the triangle and label which side is the radius.</p>
<p><b>The quick check.</b> The vertical drop is <code>ℓ cos θ = 1.2 × cos 30° ≈ 1.04 m</code>, and <code>tan θ = 0.60/1.04 ≈ 0.577</code>, which is <code>tan 30°</code> ✓ — consistent. If you had found 60° the vertical drop would be <code>1.2 × 0.5 = 0.60 m</code> and <code>tan</code> would be 1.0, contradicting the geometry.</p>`,
      tag: "Conical pendulum angle — which trig ratio"
    }
  ],

  traps: [
    "Drawing a separate 'centripetal force' arrow on a free-body diagram. It is the resultant of the real forces, not an additional one.",
    "Using degrees in <code>ω = 2πf</code>. The formula assumes radians.",
    "Setting the vertical resolution equal to <code>mv²/r</code> in a vertical circle. Only the direction towards the centre gets <code>mv²/r</code>.",
    "Forgetting that in a conical pendulum the effective length is <code>ℓ cos θ</code>, the vertical drop, not <code>ℓ</code>.",
    "Using <code>v²/r</code> for the acceleration when the angular speed is given. Use <code>ω²r</code> directly rather than converting.",
    "Assuming the period of an orbit goes as the radius rather than as <code>r^(3/2)</code>.",
    "Straying into gravitational potential or escape velocity, which are field theory and excluded from Round 0.",
    "Forgetting that the mass cancels in nearly every circular-motion result, and doing unnecessary arithmetic."
  ],

  checklist: [
    { id: "D1", flag: "NEW", text: "Angular speed <code>ω = v/r = 2πf = 2π/T</code>; radian measure; converting revs per minute to rad s⁻¹." },
    { id: "D2", flag: "NEW", text: "Centripetal acceleration <code>a = v²/r = ω²r</code>, and the derivation from the rotation of the velocity vector." },
    { id: "D3", flag: "NEW", text: "Centripetal force <code>F = mv²/r = mω²r</code>, and the recognition that it is a resultant rather than a new force." },
    { id: "D4", flag: "NEW", text: "Force resolution for circular motion: the conical pendulum, a string at an angle, and finding the period. The five-step procedure." },
    { id: "D5", flag: "NEW", text: "Vertical circles; the minimum speed at the top <code>√(gr)</code>; the normal force at the bottom." },
    { id: "D6", flag: "NEW", text: "Banking and cornering; the lean angle of a cyclist; <code>tan θ = v²/(rg)</code> in both cases." },
    { id: "D7", flag: "NEW", text: "Apparent weight variation with latitude; the pole versus equator comparison, and estimating the size of the effect." },
    { id: "D8", flag: "NEW", text: "Orbital motion by equating <code>mv²/r</code> to <code>mg</code>; the period and speed ratios, and <code>T ∝ r^(3/2)</code>." },
    { id: "D9", flag: "R1-ONLY", text: "Kepler-style orbital ratios involving gravitational potential or orbital energy. Field theory — insurance only, and mostly out of scope." },
    { id: "D10", flag: "CORE", text: "Estimating centripetal acceleration and force in unfamiliar rotating situations, such as a washing machine drum or a centrifuge." }
  ]
},

{
  code: "E",
  title: "Materials and elasticity",
  short: "Materials",
  priority: 3,
  tier: "Tier A — inside AQA AS §3.4.7, and one sample-paper question",
  why: "Short and self-contained, with two items that are genuinely new to you: Young's modulus and thermal expansion. Neither is in the IB syllabus, which means they are pure added value. The stress–strain material is also unusually well suited to graph-reading questions, which are quick marks.",
  warn: "<p><b>Two things here are not in the IB.</b> Young's modulus and the stress–strain family are A-level content that the IB does not teach, and thermal expansion <code>ℓ = ℓ₀(1 + αΔT)</code> is likewise absent. Treat both as new learning rather than revision, even though the underlying ideas are simple.</p>",

  sections: [
    {
      h: "Density",
      body: `<p>Density is mass per unit volume:</p>
<div class="formula">ρ = m/V</div>
<p>in <code>kg m⁻³</code>. For a regular solid you can measure the dimensions; for an irregular solid you use the immersion method from module M: weigh it in air, weigh it in water, and the upthrust gives the volume.</p>
<table><thead><tr><th>Material</th><th>Density / kg m⁻³</th></tr></thead><tbody>
<tr><td>Air (at room temperature)</td><td>1.2</td></tr>
<tr><td>Water</td><td>1000</td></tr>
<tr><td>Aluminium</td><td>2700</td></tr>
<tr><td>Steel</td><td>7800</td></tr>
<tr><td>Lead</td><td>11 300</td></tr>
<tr><td>Mercury</td><td>13 600</td></tr>
</tbody></table>
<p>Knowing the order of magnitude of these is useful for sanity-checking answers. If a question about a steel block yields a density of 300 kg m⁻³, something has gone wrong.</p>
<h3>Density is an intensive property</h3>
<p>Density does not depend on how much material you have — cut a steel block in half and each half still has density 7800 kg m⁻³. That is what makes it a property of the <i>material</i>, like the Young modulus, rather than of the <i>sample</i>. It also means that for a uniform object, mass and volume always scale together: double the volume and you double the mass.</p>
<div class="callout callout--warn"><p><b>The unit trap.</b> <code>1 g cm⁻³ = 1000 kg m⁻³</code>. A density quoted as <code>7.8 g cm⁻³</code> for steel is <code>7800 kg m⁻³</code>, not 7.8. The factor of 1000 is the single most common slip when converting between the two units, and questions will offer both forms as options.</p></div>`
    },

    {
      h: "Hooke's law and springs",
      body: `<p>For many materials, up to a limit, extension is proportional to the applied force:</p>
<div class="formula">F = kΔL</div>
<p>where <code>k</code> is the <b>spring constant</b> or stiffness, in <code>N m⁻¹</code>. A stiff spring has a large <code>k</code>.</p>
<p>The <b>limit of proportionality</b> is the point beyond which the graph stops being a straight line. The <b>elastic limit</b> is the point beyond which the material does not return to its original length when the load is removed. These are not always the same point, and a question may ask you to distinguish them.</p>
<h3>Springs in series and in parallel</h3>
<table><thead><tr><th>Arrangement</th><th>Combined stiffness</th><th>Physical reason</th></tr></thead><tbody>
<tr><td>Parallel</td><td><code>k_total = k₁ + k₂</code></td><td>Each spring shares the load, so the combination is stiffer</td></tr>
<tr><td>Series</td><td><code>1/k_total = 1/k₁ + 1/k₂</code></td><td>Each spring stretches in turn, so the combination is softer</td></tr>
</tbody></table>
<div class="callout callout--key"><p><b>Note that this is the opposite of the resistor rules in one respect and the same in another.</b> Springs in parallel add, like resistors in series. Springs in series reciprocal-add, like resistors in parallel. It is the same pair of structures, mapped onto each other. If you remember the resistor rules you already know these.</p></div>
<h3>Why series is softer</h3>
<p>Put two identical springs in series and hang a load. Each spring experiences the <b>same force</b>, so each stretches by the same amount. The total extension is doubled, so the effective stiffness is halved. That reasoning is worth being able to give, because the parallel case has the mirror-image argument.</p>
<h3>The limit of proportionality versus the elastic limit</h3>
<p>These two limits are close but not the same, and a question may ask you to distinguish them. The <b>limit of proportionality</b> is where the force–extension graph stops being a straight line — a geometric fact about the graph. The <b>elastic limit</b> is where the material stops returning to its original length on unloading — a physical fact about the material. You can pass the limit of proportionality and still recover fully; pass the elastic limit and you have a permanent set.</p>
<div class="callout callout--key"><p><b>Why Hooke's law holds at all.</b> It is the linear regime of interatomic forces. Stretch a bond a little and the restoring force is proportional to the displacement — exactly like a tiny spring at every bond. Push far enough and the relationship bends, which is the limit of proportionality in macroscopic language.</p></div>`
    },

    {
      h: "Elastic strain energy",
      body: `<p>Stretching a spring requires work. Because the force rises from zero to <code>F</code> as the extension increases, the work is the area of a triangle on a force–extension graph:</p>
<div class="formula">E = ½FΔL = ½kx²</div>
<p>where <code>x</code> is the extension <code>ΔL</code>.</p>
<div class="callout callout--key"><p><b>The factor of ½ is the same one as everywhere else.</b> It appears because the force ramps linearly from zero. You met it in kinetic energy <code>½mv²</code>, in capacitor energy <code>½QV</code>, and here. Whenever a graph is a straight line through the origin and you want the area, you get a factor of ½.</p></div>
<h3>The non-linear case</h3>
<p>If the force–extension graph is not a straight line, the stored energy is still the area under the curve — but you can no longer use the triangle formula. Questions sometimes give a graph and ask for the energy as the area of a trapezium or a counted number of squares. Read the axes carefully: a graph of force against extension has area in joules, but a graph of force against <i>length</i> does not.</p>
<h3>Energy conversions</h3>
<p>Elastic strain energy converts to kinetic and gravitational energy in many problems: a spring launching a projectile, a bungee jumper, a bow. The method is always conservation of energy, with <code>½kx²</code> as one of the terms.</p>
<h3>Deriving E = ½kx² from the average force</h3>
<p>The force grows linearly from 0 to <code>F = kx</code> as the spring stretches. The work done is the average force times the distance: <code>(0 + kx)/2 × x = ½kx²</code>. Equivalently it is the area of the triangle under the force–extension graph. The factor of ½ is unavoidable because the force is not constant — it is zero at the start.</p>
<div class="callout callout--bad"><p><b>The error to avoid.</b> Writing <code>Fx = kx²</code> for the stored energy uses the final force throughout, ignoring that the force started at zero. That overestimates the energy by a factor of 2. Whenever you see a force–extension graph, take the <i>area</i>, and for a triangle the area is half the base times the height.</p></div>`
    },

    {
      h: "Stress, strain and the Young modulus",
      body: `<p>Hooke's law describes a particular spring. To describe a <b>material</b>, independently of the shape of the sample, we need two normalised quantities.</p>
<div class="formula">tensile stress  σ = F/A          (units: Pa)
tensile strain  ε = ΔL/L         (dimensionless)</div>
<p>Stress is force per unit cross-sectional area, so it does not depend on how thick the sample is. Strain is fractional extension, so it does not depend on how long the sample is. Dividing them gives a property of the material alone:</p>
<div class="formula">Young modulus  E = σ/ε = FL/(AΔL)</div>
<p>with units of pascals, because strain is dimensionless. Typical values are of order <code>10¹⁰</code> to <code>10¹¹ Pa</code> for metals.</p>
<div class="callout callout--key"><p><b>Why the Young modulus is more useful than the spring constant.</b> Two wires of the same steel but different lengths and thicknesses have different spring constants, so the spring constant does not characterise the steel. They have the <b>same</b> Young modulus, because the geometry cancelled. That is the whole point of the quantity, and it is the sentence a question asking "why" wants.</p></div>
<h3>The gradient of a stress–strain graph</h3>
<p>Rearranging, <code>σ = Eε</code>. So a graph of stress against strain is a straight line through the origin with gradient <code>E</code>. That is the standard way the Young modulus is measured, and the straight portion of the graph is exactly the region where Hooke's law holds.</p>`
    },

    {
      h: "Stress–strain graphs",
      body: `<p>The shape of the stress–strain graph is a material's signature. Learn the features and what each one means.</p>
<table><thead><tr><th>Feature</th><th>What it marks</th></tr></thead><tbody>
<tr><td>Straight portion from the origin</td><td>Hooke's law holds; gradient is the Young modulus</td></tr>
<tr><td>Limit of proportionality</td><td>The end of the straight portion — the graph starts to curve</td></tr>
<tr><td>Elastic limit</td><td>Beyond this, permanent deformation occurs on unloading</td></tr>
<tr><td>Yield point</td><td>A sudden increase in strain for little increase in stress</td></tr>
<tr><td>Ultimate tensile stress</td><td>The highest point of the curve — the maximum stress the material can bear</td></tr>
<tr><td>Fracture point</td><td>Where the material breaks</td></tr>
</tbody></table>
<h3>Comparing material types</h3>
<table><thead><tr><th>Type</th><th>Behaviour</th><th>Examples</th></tr></thead><tbody>
<tr><td>Ductile</td><td>Large plastic deformation before fracture; can be drawn into wires</td><td>copper, mild steel</td></tr>
<tr><td>Brittle</td><td>Little or no plastic deformation; fractures suddenly</td><td>glass, cast iron, ceramics</td></tr>
<tr><td>Polymeric</td><td>Curved graph, large strain, often returns slowly</td><td>rubber, polythene</td></tr>
</tbody></table>
<div class="callout callout--good"><p><b>The comparison question.</b> When asked to compare two materials from their graphs, the useful comparisons are: which has the larger Young modulus (steeper initial gradient), which is stronger (higher ultimate tensile stress), and which is more brittle (less strain before fracture). Answer in those three terms and you have covered the physics.</p></div>
<div class="callout callout--warn"><p><b>Do not confuse stress with force and strain with extension.</b> The ultimate tensile <i>stress</i> is a fixed property of a material; the breaking <i>force</i> depends on the cross-sectional area. A thick and a thin wire of the same steel break at the same stress but different forces. Questions exploit this distinction regularly.</p></div>
<h3>The three comparisons a question will ask</h3>
<p>When two materials are compared from their graphs, the useful quantities are: the initial gradient (the Young modulus — steeper is stiffer), the height of the curve at its peak (the ultimate tensile stress — higher is stronger), and the strain at fracture (smaller is more brittle). Answer in exactly those three terms and you have covered the physics.</p>
<div class="callout callout--good"><p><b>Reading a curve you have never seen.</b> Even an unfamiliar material graph yields to the same questions: where does it stop being straight (limit of proportionality)? Does it then curve gently (ductile) or break almost immediately (brittle)? Does it return to the origin on unloading (elastic) or leave a gap (plastic)? The features are the same vocabulary for every material.</p></div>`
    },

    {
      h: "Thermal expansion",
      body: `<p>Materials expand when heated. For a rod of original length <code>ℓ₀</code>:</p>
<div class="formula">ℓ = ℓ₀(1 + αΔT)</div>
<p>so the change in length is</p>
<div class="formula">Δℓ = α ℓ₀ ΔT</div>
<p>where <code>α</code> is the coefficient of linear expansion, with units of <code>K⁻¹</code>.</p>
<div class="callout callout--key"><p><b>The units of α, and why they matter.</b> A fractional change per kelvin, so <code>K⁻¹</code>. Typical values are of order <code>10⁻⁵ K⁻¹</code> for metals, which means a one-metre steel bar lengthens by about <code>10⁻⁵ × 1 × 1 = 10 μm</code> for each kelvin. Small per kelvin, but significant over tens of degrees and tens of metres — which is why bridges and railway tracks have expansion gaps.</p></div>
<p>Note that <code>ΔT</code> is the same number in kelvin and in degrees Celsius, because a temperature <i>difference</i> is the same on both scales. So you never need to convert for this formula. That is a small but useful saving under time pressure.</p>
<h3>Where thermal expansion appears</h3>
<ul class="tight">
<li><b>Expansion gaps</b> in railway tracks, bridges and concrete roads — the gap must be large enough to absorb the expansion over the expected temperature range.</li>
<li><b>Bimetallic strips</b> — two metals with different <code>α</code> bonded together bend when heated, and this is used in thermostats.</li>
<li><b>Thermal stress</b> — if expansion is prevented, the constraint generates a large stress. This is the next section and it is the more interesting problem.</li>
<li><b>Precision measurement</b> — a pendulum clock's period depends on the length of its rod, so temperature changes make it drift. This is why Invar, with a very small <code>α</code>, is used in clocks and measuring instruments.</li>
</ul>`
    },

    {
      h: "Combined thermal expansion and stress",
      body: `<p>This is the combination that competition questions like, because it links two apparently separate topics. It is also entirely absent from the IB, so it is a clean advantage.</p>
<h3>The setup</h3>
<p>A rod is held rigidly at both ends so that it cannot expand. Its temperature is raised by <code>ΔT</code>. It <i>wants</i> to expand by <code>α ℓ₀ ΔT</code>, but it is prevented. The result is a compressive stress.</p>
<h3>The derivation</h3>
<p>The prevented expansion is the same as an imposed compressive strain:</p>
<div class="formula">strain = Δℓ/ℓ₀ = αΔT</div>
<p>And from the definition of the Young modulus, <code>σ = Eε</code>, so</p>
<div class="formula">thermal stress  σ = E α ΔT</div>
<h3>Why this produces enormous stresses</h3>
<p>Take steel with <code>E ≈ 2 × 10¹¹ Pa</code> and <code>α ≈ 1.2 × 10⁻⁵ K⁻¹</code>. For a temperature rise of 30 K:</p>
<div class="formula">σ = 2 × 10¹¹ × 1.2 × 10⁻⁵ × 30 ≈ 7 × 10⁷ Pa</div>
<p>That is about 70 MPa — comparable to the yield stress of mild steel. So a fully constrained steel rail heated by 30 °C can buckle or fracture. That is precisely why rails are laid with gaps, or pre-stressed under tension.</p>
<div class="callout callout--good"><p><b>The general lesson, and it generalises usefully.</b> Whenever a constraint prevents a natural change, the constraint generates a stress proportional to how much change was prevented. The same structure appears in a rod prevented from contracting when cooled, in a wire whose ends are fixed, and in a bimetallic strip. Recognising the pattern is worth more than memorising <code>EαΔT</code>.</p></div>
<div class="callout callout--warn"><p><b>Check whether the question says the rod is free or constrained.</b> If free, use <code>Δℓ = αℓ₀ΔT</code> and there is no stress. If constrained, use <code>σ = EαΔT</code> and there is no change in length. A question that gives you both <code>α</code> and <code>E</code> is usually a constrained one, because a free rod needs only <code>α</code>.</p></div>
<h3>A second way to remember σ = EαΔT</h3>
<p>Treat the prevented expansion as if it had happened and then been compressed back. The free expansion would be strain <code>αΔT</code>; compressing the rod back to its original length imposes that same strain in the opposite sense. Hooke's law in material form is <code>σ = Eε</code>, so the stress is <code>E × αΔT</code>. Seeing it as "reverse the free expansion" makes the formula derivable rather than memorised.</p>
<div class="callout callout--key"><p><b>The everyday pay-off.</b> This is why a thermostat bimetallic strip bends (two <code>α</code>s fighting), why glass cracks if heated unevenly (the hot side wants to expand but the cold side restrains it, generating stress), and why large structures are built with expansion joints or deliberate pre-stress. The same <code>EαΔT</code> underlies all three.</p></div>`
    }
  ],

  examples: [
    {
      q: "<p>A wire of length 2.0 m and cross-sectional area <code>1.0 × 10⁻⁶ m²</code> extends by 1.0 mm when a force of 100 N is applied. What is the Young modulus of the material?</p><p>A) <code>1.0 × 10¹⁰ Pa</code> &nbsp; B) <code>2.0 × 10¹⁰ Pa</code> &nbsp; C) <code>5.0 × 10¹⁰ Pa</code> &nbsp; D) <code>2.0 × 10¹¹ Pa</code> &nbsp; E) <code>5.0 × 10¹¹ Pa</code></p>",
      sol: `<p>Use <code>E = FL/(AΔL)</code> directly, working in powers of ten separately.</p>
<p><b>Stress.</b></p>
<div class="formula">σ = F/A = 100/(1.0 × 10⁻⁶) = 1.0 × 10⁸ Pa</div>
<p><b>Strain.</b> The extension is 1.0 mm = <code>1.0 × 10⁻³ m</code> over an original length of 2.0 m:</p>
<div class="formula">ε = ΔL/L = 1.0 × 10⁻³/2.0 = 5.0 × 10⁻⁴</div>
<p><b>Young modulus.</b></p>
<div class="formula">E = σ/ε = 1.0 × 10⁸ / 5.0 × 10⁻⁴ = 2.0 × 10¹¹ Pa</div>
<p><b>Answer: D.</b></p>
<p><b>The sanity check that requires no calculation.</b> Young moduli for metals are of order <code>10¹⁰</code> to <code>10¹¹ Pa</code>. Option E at <code>5 × 10¹¹</code> is higher than any common metal, and options A and B are a whole order of magnitude too low for a metal. Only C and D are plausible, and the mental arithmetic picks D.</p>
<p><b>The trap.</b> Option B, <code>2.0 × 10¹⁰</code>, is what you get by forgetting to convert millimetres to metres — using <code>ΔL = 1.0</code> instead of <code>1.0 × 10⁻³</code>. That is the single most common error in this topic, and it is always a unit conversion rather than a physics mistake. Convert every length to metres before substituting.</p>`,
      tag: "Young modulus — the unit-conversion trap"
    },
    {
      q: "<p>A steel rail is fixed rigidly at both ends so that it cannot expand. The temperature rises by 40 K. For steel, <code>α = 1.2 × 10⁻⁵ K⁻¹</code> and <code>E = 2.0 × 10¹¹ Pa</code>. What is the thermal stress developed?</p><p>A) <code>4.8 × 10⁴ Pa</code> &nbsp; B) <code>9.6 × 10⁵ Pa</code> &nbsp; C) <code>4.8 × 10⁷ Pa</code> &nbsp; D) <code>9.6 × 10⁷ Pa</code> &nbsp; E) <code>2.4 × 10⁹ Pa</code></p>",
      sol: `<p><b>Step 1 — the prevented strain.</b> If the rail were free it would expand by <code>αΔT</code> as a fraction of its length:</p>
<div class="formula">strain = αΔT = 1.2 × 10⁻⁵ × 40 = 4.8 × 10⁻⁴</div>
<p><b>Step 2 — the stress.</b> The constraint imposes that strain, so</p>
<div class="formula">σ = E × strain = 2.0 × 10¹¹ × 4.8 × 10⁻⁴ = 9.6 × 10⁷ Pa</div>
<p><b>Answer: D.</b></p>
<p><b>Why the answer is so large, and why that is the point of the question.</b> <code>9.6 × 10⁷ Pa</code> is about 96 MPa, which is comparable to the yield stress of mild steel. So a constrained steel rail heated by 40 K is in genuine danger of buckling. That is why real rails are laid with expansion gaps, or pre-tensioned so that they are in tension when cold and merely relaxed when hot.</p>
<p><b>The traps.</b> Option C, <code>4.8 × 10⁷</code>, is the strain multiplied by <code>10¹¹</code> but with the exponent mis-added — a powers-of-ten slip, which is the most likely error in a question with this many exponents. Option A, <code>4.8 × 10⁴</code>, is the strain itself, reported as a stress; option B is the strain times <code>10⁹</code>.</p>
<p><b>The technique that avoids the slips.</b> Handle the powers of ten separately from the leading digits. The digits here are <code>1.2 × 40 = 48</code>, then <code>48 × 2.0 = 96</code>. The powers are <code>10⁻⁵ × 10¹¹ = 10⁶</code>. So the answer is <code>96 × 10⁶ = 9.6 × 10⁷</code> ✓. Doing it in two separate streams is far more reliable than trying to track exponents inside a single calculation.</p>`,
      tag: "Thermal stress — combining two modules"
    },
    {
      q: "<p>Two identical springs, each of stiffness 200 N m⁻¹, are connected in series. What load is needed to extend the combination by 0.10 m?</p><p>A) 5 N &nbsp; B) 10 N &nbsp; C) 20 N &nbsp; D) 40 N &nbsp; E) 80 N</p>",
      sol: `<p><b>Step 1 — combined stiffness.</b> In series, the reciprocals add:</p>
<div class="formula">1/k_total = 1/200 + 1/200 = 2/200   →   k_total = 100 N m⁻¹</div>
<p><b>Step 2 — the load.</b></p>
<div class="formula">F = k_total × x = 100 × 0.10 = 10 N</div>
<p><b>Answer: B.</b></p>
<p><b>The physical reasoning, which is faster than the formula.</b> Both springs experience the same force <code>F</code>, so each stretches by <code>F/200</code>. The total extension is twice that, <code>2F/200 = F/100</code>. Setting this equal to 0.10 m gives <code>F = 10 N</code> ✓. Note that the effective stiffness halved, from 200 to 100 — putting springs in series makes the combination softer.</p>
<p><b>The trap.</b> Option D, 40 N, is what you get by treating the springs as if they were in parallel, where the stiffness would be 400 N m⁻¹ and the load would be 40 N. Getting series and parallel the wrong way round is the error this question is designed to catch.</p>
<p><b>The cross-check on the other arrangement.</b> If the same two springs were in parallel, each would stretch by the full 0.10 m under a force of <code>200 × 0.10 = 20 N</code>, so the total would be 40 N. That confirms the direction: parallel needs more force, so parallel is stiffer. Building that intuition means you never need to recall which rule is which.</p>`,
      tag: "Springs in series — and the direction of the rule"
    },
    {
      q: "<p>A wire of unstretched length 1.5 m is stretched to 1.8 m. What is the strain?</p><p>A) 0.17 &nbsp; B) 0.20 &nbsp; C) 0.30 &nbsp; D) 1.2 &nbsp; E) 1.8</p>",
      sol: `<p>Strain is the extension divided by the <b>original</b> length:</p>
<div class="formula">ε = ΔL/L₀ = (1.8 − 1.5)/1.5 = 0.3/1.5 = 0.20</div>
<p><b>Answer: B.</b></p>
<p><b>The trap, and it is the most common error in the whole of materials.</b> Option A, 0.17, comes from dividing the extension by the <b>final</b> length — <code>0.3/1.8 = 0.167</code>. The definition of strain uses the original length, always. A question that gives you both lengths is deliberately testing whether you know which one goes in the denominator.</p>
<p><b>The other distractors.</b> Option C, 0.30, is the extension in metres, not a strain — reporting a length where a ratio is wanted. Option D, 1.2, is <code>1.8/1.5</code>, the ratio of lengths rather than the fractional change. Option E, 1.8, is just the final length.</p>
<p><b>Why strain is dimensionless.</b> It is a length divided by a length, so the units cancel. That means you should never report strain with a unit — and if you find yourself writing one, something has gone wrong. It is often expressed as a percentage: here, 20%.</p>`,
      tag: "Strain — which length goes in the denominator"
    }
  ],

  traps: [
    "Dividing the extension by the final length instead of the original length when computing strain.",
    "Forgetting to convert millimetres to metres, or pascals to megapascals, before substituting into <code>E = FL/(AΔL)</code>.",
    "Getting springs in series and parallel the wrong way round. Series makes the combination softer.",
    "Using <code>Fx</code> instead of <code>½Fx</code> for elastic strain energy — the force ramps from zero.",
    "Confusing stress with force and strain with extension. Stress and strain are properties of the material; force and extension depend on the sample's geometry.",
    "Using <code>Δℓ = αℓ₀ΔT</code> for a constrained rod. A constrained rod has no length change and instead develops <code>σ = EαΔT</code>.",
    "Converting ΔT from Celsius to kelvin unnecessarily. A temperature difference is the same on both scales.",
    "Assuming a material with a larger Young modulus is stronger. Stiffness and strength are different properties — the Young modulus is the gradient, the ultimate tensile stress is the height."
  ],

  checklist: [
    { id: "E1", flag: "CORE", text: "Density <code>ρ = m/V</code>; the density of water and of common metals; finding density by weighing in air and in water." },
    { id: "E2", flag: "CORE", text: "Hooke's law <code>F = kΔL</code>; the limit of proportionality versus the elastic limit; what the spring constant means physically." },
    { id: "E3", flag: "NEW", text: "Springs in series and in parallel, with the physical reasoning for each and the direction check." },
    { id: "E4", flag: "NEW", text: "Elastic strain energy <code>½FΔL = ½kx²</code> as the area under a force–extension graph, including the non-linear case." },
    { id: "E5", flag: "NEW", text: "Tensile stress <code>F/A</code> and tensile strain <code>ΔL/L₀</code>, and why each is independent of the sample's geometry." },
    { id: "E6", flag: "NEW", text: "The Young modulus <code>E = σ/ε = FL/(AΔL)</code>, with units of pascals, and why it is more useful than the spring constant." },
    { id: "E7", flag: "NEW", text: "Stress–strain graphs: the limit of proportionality, elastic limit, yield point, ultimate tensile stress and fracture point." },
    { id: "E8", flag: "NEW", text: "Breaking stress and ultimate tensile strength; why they are material properties while breaking force is not." },
    { id: "E9", flag: "CORE", text: "Elastic strain energy converting to kinetic and gravitational energy, solved by conservation of energy." },
    { id: "E10", flag: "NEW", text: "Thermal expansion <code>Δℓ = αℓ₀ΔT</code>, the units of α, and why ΔT needs no conversion. <b>Not in the IB syllabus.</b>" },
    { id: "E11", flag: "NEW", text: "Thermal stress <code>σ = EαΔT</code> for a constrained rod, and the expansion-gap application. <b>Not in the IB syllabus.</b>" },
    { id: "E12", flag: "R1-ONLY", text: "Scaling laws for beams and rods, such as stiffness proportional to width times thickness cubed. Round 1 material — insurance only." }
  ]
}

]);
