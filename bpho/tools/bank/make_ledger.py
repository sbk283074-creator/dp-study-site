# -*- coding: utf-8 -*-
"""Build ledger.json: the questions a human actually worked through by hand.

The user's instruction was explicit -- "sometimes you should check questions by yourself
to see if the calculation works (don't trust your tool that you write only)".  G7 already
re-evaluates each question's own `check` expression with sympy, but that is still a
machine agreeing with a machine.  The ledger is the record of a person doing the
arithmetic from the question text alone, without looking at the stored answer first.

Every entry carries the working, so the check can be repeated by anyone reading it.
Run:  python make_ledger.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# section number -> {id: (method, working, answer letter)}
#
# The letter is what the working gives, written down BEFORE comparing it with the stored
# key.  If the two disagree, that is the finding -- not something to be tidied away by
# editing the letter.
LEDGER = {1: {
    "S01-01": (
        "solve the two equations of motion and eliminate a",
        "2mg - T = 2ma and T - mg = ma; adding gives mg = 3ma so a = g/3; "
        "T = m(g + a) = m(g + g/3) = 4mg/3",
        "B"),
    "S01-02": (
        "reduce the parallel pair, then divide the supply",
        "3.0k || 6.0k = (3.0 x 6.0)/(3.0 + 6.0) = 2.0k; total 6.0k + 2.0k = 8.0k; "
        "I = 12/8.0k = 1.5 mA; V = 1.5 mA x 2.0k = 3.0 V",
        "C"),
    "S01-03": (
        "balance weight against drag by dimensions",
        "weight ~ rho_w g r^3 and drag ~ rho_air r^2 v^2; equating them cancels r^2 and "
        "one r, leaving v^2 ~ r, so v ~ sqrt(r)",
        "B"),
    "S01-04": (
        "momentum first, then energy in the spring",
        "mu = (m + 3m)v so v = u/4; KE = (1/2)(4m)(u/4)^2 = mu^2/8; "
        "(1/2)kx^2 = mu^2/8 so x^2 = mu^2/(4k) and x = (u/2)sqrt(m/k)",
        "E"),
    "S01-05": (
        "differentiate P(R) and set to zero",
        "P = E^2 R/(R + r)^2; dP/dR = 0 at R = r; then P = E^2 r/(2r)^2 = E^2/(4r)",
        "D"),
    "S01-06": (
        "turn a pressure into a mass through g",
        "p = 1.0e5 Pa is a weight per square metre, so W = 1.0e5 N on 1 m^2; "
        "m = W/g = 1.0e5/10 = 1.0e4 kg",
        "B"),
    "S01-07": (
        "find the speed at h, then double the time to the apex",
        "v^2 = u^2 - 2gh at height h; time from h up to the apex is v/g and the return "
        "takes the same, so the interval is 2v/g = 2sqrt(u^2 - 2gh)/g",
        "E"),
    "S01-08": (
        "take moments about the hinge",
        "weight 20 x 10 = 200 N at 2.0 m; the perpendicular component of T at 4.0 m is "
        "T sin30 = T/2; 200 x 2.0 = (T/2) x 4.0 gives 400 = 2T so T = 200 N",
        "C"),
    "S01-09": (
        "set the contact force to zero at the top",
        "mg - N = mv^2/r and the car leaves when N = 0, so v^2 = rg = 20 x 10 = 200; "
        "v = 14.1 m/s, so it leaves above about 14 m/s",
        "A"),
    "S01-10": (
        "recognise an odd-harmonic series and find its step",
        "a pipe closed at one end gives only odd multiples of f0; the three given "
        "frequencies differ by 200 Hz, and 100, 300, 500, 700 are the odd multiples "
        "1, 3, 5, 7 of 100 Hz, so f0 = 100 Hz",
        "D"),
    "S01-11": (
        "put the critical angle equal to the fixed 45 degrees",
        "TIR needs theta > theta_c with sin(theta_c) = 1/n; the geometry fixes "
        "theta = 45, so the smallest n is the equality case 1/sin45 = 1/(1/sqrt2) = sqrt2",
        "C"),
    "S01-12": (
        "reduce each configuration to one resistance, then divide the two terminal p.d.s",
        "before: 6.0 || 3.0 = 18/9 = 2.0 ohm so R_ext = 6.0 + 2.0 = 8.0 ohm; "
        "I = 12/(8.0 + 1.0) = 4/3 A and V = (4/3)(8.0) = 32/3 V.  "
        "after removing the 3.0 ohm: R_ext = 6.0 + 6.0 = 12.0 ohm, I = 12/13 A, "
        "V = (12/13)(12) = 144/13 V.  ratio = (144/13)/(32/3) = 432/416 = 27/26, "
        "and 27/26 is greater than 1 as it must be, since the load got lighter",
        "A"),
    "S01-13": (
        "set heat lost equal to heat gained",
        "0.20 x 500 x (200 - t) = 0.10 x 4000 x (t - 20); 100(200 - t) = 400(t - 20); "
        "20000 - 100t = 400t - 8000; 28000 = 500t; t = 56 C",
        "E"),
    "S01-14": (
        "share the energy in inverse proportion to mass",
        "equal and opposite momenta, so KE = p^2/2m means KE goes as 1/m; the alpha has "
        "mass number 4 and the recoil A - 4, so the alpha takes (A-4)/((A-4)+4) = "
        "(A-4)/A of E",
        "A"),
    "S01-15": (
        "substitute the constant-volume area into R = rho L / A",
        "volume fixed means A -> A/(1 + x); R' = rho L(1 + x)/(A/(1 + x)) = R(1 + x)^2; "
        "the fractional change is 2x + x^2, which for small x is 2x",
        "B"),
    "S01-16": (
        "one position equation for the whole flight, then the positive root of the quadratic",
        "take up as positive with the origin at the release point: y = u t - g t^2/2.  "
        "Landing is y = -h, so g t^2/2 - u t - h = 0 and t = (u + sqrt(u^2 + 2gh))/g, "
        "the positive root (the other is a time before the throw).  Check with u = 10, "
        "g = 10, h = 120: sqrt(100 + 2400) = 50 so t = 60/10 = 6.0 s, and "
        "y = 10(6) - 5(36) = -120 m, which is the foot of the cliff",
        "A"),
    "S01-17": (
        "add the gravity component and limiting friction, then equate to mg",
        "down the slope: mg sin(theta) = 5.0 x 10 x 0.60 = 30 N; normal reaction "
        "5.0 x 10 x 0.80 = 40 N so limiting friction 0.50 x 40 = 20 N; needed pull "
        "30 + 20 = 50 N; the hanging weight is 10m, so m = 5.0 kg",
        "D"),
    "S01-18": (
        "require the centripetal acceleration to be g, then convert to a period",
        "omega^2 r = g so omega^2 = 10/50 = 0.20 and omega = 0.447 rad/s; "
        "T = 2 pi/omega = 6.283/0.447 = 14.1 s; equivalently T = 2 pi sqrt(r/g) = "
        "2 pi sqrt5 = 14.1 s",
        "C"),
    "S01-19": (
        "take the area of the triangle under the straight region",
        "energy per unit volume = (1/2) x stress x strain = "
        "0.5 x 3.0e8 x 1.5e-3 = 0.5 x 4.5e5 = 2.25e5, which is 2.3e5 J/m^3 to two figures",
        "B"),
    "S01-20": (
        "use sin(theta) <= 1 and round the inequality down",
        "d = 1e-3/500 = 2.0e-6 m and lambda = 6.0e-7 m; d/lambda = 2.0e-6/6.0e-7 = 3.33; "
        "n <= 3.33 so the highest order is 3; the fourth would need sin(theta) = "
        "4 x 0.30 = 1.20, which does not exist",
        "A"),
    "S01-21": (
        "combine the critical angle with Snell's law at the end face",
        "sin(theta_c) = 1.2/1.5 = 0.8; the steepest guided ray makes 90 - theta_c with "
        "the axis, so sin(alpha) = cos(theta_c) = sqrt(1 - 0.64) = 0.6; Snell gives "
        "sin(theta_a) = 1.5 x 0.6 = 0.9, which is also sqrt(1.5^2 - 1.2^2) = sqrt0.81",
        "B"),
    "S01-22": (
        "energy needed divided by power",
        "energy = 1.5 x 4200 x 80 = 504000 J; time = 504000/2000 = 252 s",
        "E"),
    "S01-23": (
        "conserve charge over the new total capacitance",
        "Q = CV = 2.0e-6 x 100 = 2.0e-4 C; the charge is shared over 2.0 + 3.0 = 5.0 uF; "
        "V = 2.0e-4/5.0e-6 = 40 V",
        "C"),
    "S01-24": (
        "add the water pressure to the atmosphere, then use Boyle's law",
        "p_bottom = 1.0e5 + 1000 x 10 x 20 = 1.0e5 + 2.0e5 = 3.0e5 Pa; isothermal, so "
        "p1 V1 = p2 V2 gives 3.0e5 x 1.0 = 1.0e5 x V2 and V2 = 3.0 cm^3",
        "A"),
    "S01-25": (
        "raise one half to the power of the number of half-lives",
        "fraction = (1/2)^1.5 = 1/2^(3/2) = 1/(2 sqrt2) = 1/2.828 = 0.354",
        "D"),
},

2: {
    "S02-01": (
        "match dimensions and take the square root",
        "[v] = L T^-1; [gamma] = N/m = M T^-2; [rho] = M L^-3; [lambda] = L. "
        "Try gamma/(rho lambda): (M T^-2)/((M L^-3)(L)) = (M T^-2)/(M L^-2) = L^2 T^-2; "
        "square root gives L T^-1, which is a speed. The other four: "
        "sqrt(gamma rho/lambda) = M L^-2 T^-1; sqrt(gamma lambda/rho) = L^2 T^-1; "
        "gamma/(rho lambda) = L^2 T^-2; sqrt(gamma rho)/lambda = M L^-5/2 T^-1",
        "C"),
    "S02-02": (
        "write the self-similar relation and solve the quadratic",
        "R_eq = R + R R_eq/(R + R_eq); multiply out: R_eq^2 = R^2 + R R_eq; "
        "R_eq^2 - R R_eq - R^2 = 0; R_eq = R(1 + sqrt5)/2. "
        "Numerical check with R = 1: 1 + 1.618/2.618 = 1 + 0.618 = 1.618, which is the root",
        "A"),
    "S02-03": (
        "photon energy first, then compare with EACH work function before subtracting",
        "hc = 1240 eV nm, so at 400 nm the photon energy is 1240/400 = 3.1 eV.  "
        "Metal A: 3.1 > 2.0 so it emits, and KE_max = 3.1 - 2.0 = 1.1 eV, so the "
        "stopping potential is 1.1 V.  Metal B: 3.1 < 3.5 so nothing is emitted; B's "
        "threshold is 1240/3.5 = 354 nm and 400 nm is longer than that",
        "A"),
    "S02-04": (
        "build the series and sum it",
        "t_0 = sqrt(2h/g). Rebound to h/4 gives a rise-and-fall of 2 sqrt(2(h/4)/g) = "
        "2 x (1/2) sqrt(2h/g) = t_0, so the bounces are t_0, t_0/2, t_0/4, ... "
        "Total = t_0 + t_0(1 + 1/2 + 1/4 + ...) = t_0 + t_0 x 2 = 3 sqrt(2h/g)",
        "B"),
    "S02-05": (
        "divide the two force equations to kill the tension",
        "T cos(theta) = mg and T sin(theta) = m omega^2 L sin(theta) so T = m omega^2 L; "
        "dividing gives 1/cos(theta) = omega^2 L/g, so omega^2 = g/(L cos theta) and "
        "T = 2 pi sqrt(L cos theta/g)",
        "D"),
    "S02-06": (
        "rate of change of momentum",
        "mass arriving per second = rho A v; it carries speed v and leaves with none, so "
        "the momentum destroyed per second is (rho A v)(v) = rho A v^2, and that is the "
        "force. Units: (kg m^-3)(m^2)(m^2 s^-2) = kg m s^-2 = N",
        "E"),
    "S02-07": (
        "write the extension for each wire and equate",
        "e = FL/(AE) for the first. For the second A falls by a factor of four (diameter "
        "halved) and L doubles, so e = F2(2L)/((A/4)E) = 8 F2 L/(AE). Equating: "
        "F L/(AE) = 8 F2 L/(AE) so F2 = F/8",
        "A"),
    "S02-08": (
        "approaching source, so the denominator is v minus the source speed",
        "f' = f v/(v - v_s) = f v/(v - v/5) = f v/((4/5)v) = (5/4) f",
        "A"),
    "S02-09": (
        "apply the minimum-deviation relation and undo the sine",
        "n sin(A/2) = sin((A + D)/2) with A = 60 and n = sqrt2: "
        "sqrt2 x sin30 = sqrt2 x 0.5 = 0.7071 = sin45, so (60 + D)/2 = 45 and D = 30 deg",
        "C"),
    "S02-10": (
        "common voltage, so power goes as 1/R",
        "P_3 = V^2/3 and P_6 = V^2/6, total = V^2(2/6 + 1/6) = V^2/2. "
        "Fraction = (V^2/3)/(V^2/2) = 2/3, and the smaller resistor takes the larger share",
        "B"),
    "S02-11": (
        "count the halvings on a logarithmic axis",
        "800/100 = 8 and 8 = 2^3, so three halvings span the twelve minutes; "
        "T = 12/3 = 4 min. Check: 800 -> 400 -> 200 -> 100 lands on the stated point",
        "C"),
    "S02-12": (
        "reduce from the inside out, keeping the internal resistance in the loop",
        "6 || 6 = 3; R_ext = 3 + 3 = 6; R_total = 6 + 2 = 8; I = 12/8 = 1.5 A; "
        "P = I^2 R = 2.25 x 3 = 6.75 W. Check: terminal p.d. 12 - 3 = 9 V, drop across "
        "the 3 ohm is 4.5 V, leaving 4.5 V across the pair, which 1.5 A gives",
        "B"),
    "S02-13": (
        "momentum through the embedding, then friction doing work to the stop",
        "p = 20 x 300 = 6000 g m/s shared by 2000 g, so V = 3.0 m/s.  "
        "KE after = (1/2)(2.00)(3.0^2) = 9.0 J.  Friction force = mu x 2.00 x 10 = 20 mu, "
        "work over 1.5 m = 30 mu, so 30 mu = 9.0 and mu = 0.30.  "
        "Cross-check: KE before was 900 J, so 99% went in the embedding",
        "A"),
    "S02-14": (
        "conserve charge, then compare the two energies",
        "Q = CV is fixed. C_total = C + 2C = 3C so V_new = Q/(3C) = V/3. "
        "E_before = Q^2/(2C); E_after = Q^2/(6C). Ratio 1/3 remains, so 2/3 is lost. "
        "Check: the result contains no resistance, so a thicker wire loses the same 2/3",
        "E"),
    "S02-15": (
        "floating means submerged fraction equals the density ratio",
        "rho_L V_sub g = rho_b V g so V_sub/V = rho_b/rho_L. Water: 3/4 = rho_b/1000 so "
        "rho_b = 750. Unknown liquid: 1/2 = 750/rho_L so rho_L = 1500 kg/m^3. "
        "Direction: denser liquid holds the block higher, and 1/2 < 3/4",
        "D"),
    "S02-16": (
        "longest wavelength that still gives a minimum",
        "delta = 3.5 - 2.5 = 1.0 m. Minimum needs delta = (n + 1/2)lambda, so the longest "
        "wavelength is at n = 0: lambda = 2 x 1.0 = 2.0 m. f = 340/2.0 = 170 Hz. "
        "Next member: lambda = 1.0/1.5 = 0.67 m giving 510 Hz, so 170 Hz is the lowest",
        "B"),
    "S02-17": (
        "gradient gives stiffness, then convert to the modulus",
        "k = F/x = 40/(2.0e-3) = 2.0e4 N/m. E = (F/x)(L/A) = 2.0e4 x 2.0/(1.0e-7) = "
        "2.0e4 x 2.0e7 = 4.0e11 Pa. Units: (N/m)(m/m^2) = N/m^2 = Pa",
        "C"),
    "S02-18": (
        "reduce to a proportionality before putting anything in",
        "E = hc/lambda and N = P/E, so N = P lambda/(hc) and N is proportional to "
        "P lambda. Doubling P doubles N; halving lambda halves N; the product of the two "
        "factors is 2 x 1/2 = 1, so N is unchanged",
        "C"),
    "S02-19": (
        "divide by the large quantity, then expand",
        "kK/(k + K); divide top and bottom by K: k/(1 + k/K). With x = k/K small and "
        "n = -1, (1 + x)^n = 1 + nx gives 1 - k/K, so the result is k(1 - k/K). "
        "Numerical check with k = 1, K = 100: 100/101 = 0.990099 and 1 - 0.01 = 0.99",
        "A"),
    "S02-20": (
        "count the positions in the ring, then remove the object",
        "Repeated reflection in two planes meeting at 60 deg is rotation in steps of "
        "60 deg, so the bead and its images occupy 360/60 = 6 equally spaced positions. "
        "One of those is the bead, so the number of images is 6 - 1 = 5",
        "C"),
    "S02-21": (
        "count the pairs of levels",
        "Every pair of levels gives a possible photon energy, because a single gamma can "
        "carry the whole difference. With four levels: 3 + 2 + 1 = 6. "
        "The six differences are 7, 6, 4, 3, 2 and 1 MeV, all distinct",
        "D"),
    "S02-22": (
        "subtract the two motions",
        "v_1 - v_2 = g(t + delta_t) - g t = g delta_t, a constant. "
        "Separation = (1/2)g(t + delta_t)^2 - (1/2)g t^2 = g delta_t t + "
        "(1/2)g delta_t^2, which is linear in t. So it grows at a constant rate. "
        "At t = 0 it is already (1/2)g delta_t^2, the head start",
        "B"),
    "S02-23": (
        "pressure balance at the lower mercury surface",
        "rho_oil h = rho_Hg (2x), so x = rho_oil h/(2 rho_Hg). In centimetres: "
        "850 x 16/(2 x 13600) = 13600/27200 = 0.5 cm = 5.0 mm. "
        "Check the size: 0.5/16 = 1/32, and the densities are in the ratio 13600/850 = 16",
        "B"),
    "S02-24": (
        "density times volume, then check against a known mass",
        "V = 10 x 8 x 3 = 240 m^3; m = 1.2 x 240 = 288 kg, about 300 kg. "
        "Check: the same room full of water would be 240 x 1000 = 240000 kg, and air is "
        "about a thousandth as dense, so a few hundred kilograms is right",
        "C"),
    "S02-25": (
        "find the photon energy, double it, subtract the same work function",
        "hf = phi + E_k = 2.0 + 1.0 = 3.0 eV. Halving lambda doubles hf to 6.0 eV. "
        "The work function is a property of the metal, so E_k = 6.0 - 2.0 = 4.0 eV. "
        "Check the direction: the photon energy doubled but the kinetic energy went up by "
        "four, which is what a fixed subtraction does",
        "D"),
},

3: {
    "S03-01": (
        "take moments about B, so the unknown there drops out",
        "uniform beam: the 240 N acts at the 3.0 m midpoint. The load is 2.0 m from A, so "
        "6.0 - 2.0 = 4.0 m from B. F_A x 6.0 = 240 x 3.0 + 360 x 4.0 = 720 + 1440 = 2160; "
        "F_A = 2160/6.0 = 360 N. Check: the two supports carry 600 N, so B has 240 N, and "
        "moments about A give F_B x 6.0 = 240 x 3.0 + 360 x 2.0 = 1440, F_B = 240 N",
        "C"),
    "S03-02": (
        "put each candidate through the base dimensions",
        "[gamma] = N/m = kg s^-2; [rho] = kg m^-3; [r] = m; want s^-1. "
        "gamma/(rho r^3) = (kg s^-2)/((kg m^-3)(m^3)) = (kg s^-2)/kg = s^-2, and the square "
        "root is s^-1, a frequency. Rejected: gamma/(rho r) gives m^2 s^-2, whose root is "
        "m s^-1, a speed; gamma r^3/rho gives m^6 s^-2; gamma rho/r^3 gives kg^2 m^-6 s^-2; "
        "and gamma/(rho r^3) without the root is a frequency squared",
        "D"),
    "S03-03": (
        "set limiting friction equal to the weight",
        "the wall pushes back horizontally with the whole push, so N = F and the limiting "
        "friction is mu N = 0.40 F. On the point of sliding down, 0.40 F = mg = 2.0 x 10 = "
        "20 N, so F = 20/0.40 = 50 N. Check: F = 50 N gives N = 50 N and f_max = 20 N, "
        "exactly the weight, so the block is on the point of moving and no smaller push holds",
        "B"),
    "S03-04": (
        "balance is a ratio between the two dividers",
        "balance needs the detector nodes at the same potential: 3.0/3.0 = 6.0/R, so "
        "R = 6.0 k. Check by potentials: the top node sits at 12 x 6.0/(3.0 + 6.0) = 8.0 V "
        "and the bottom node at 12 x 6.0/(3.0 + 6.0) = 8.0 V, equal, so no current flows "
        "through G",
        "A"),
    "S03-05": (
        "turn the gradient into a rate of climb",
        "a 10% gradient means tan(theta) = 0.10, and at that small angle sin(theta) is also "
        "about 0.10. Rising at 5.0 x 0.10 = 0.50 m/s against a weight of 80 x 10 = 800 N "
        "needs 800 x 0.50 = 400 W. Check the size: lifting 800 N half a metre every second "
        "is 400 J per second",
        "E"),
    "S03-06": (
        "stage the journey, then divide the whole distance by the whole time",
        "stage 1: v = 0.50 x 20 = 10 m/s, s1 = (1/2)(10)(20) = 100 m.  stage 2: s2 = 10 x 30 = 300 m.  "
        "stage 3: t = 10/1.0 = 10 s so s3 = (1/2)(10)(10) = 50 m.  total 450 m in 60 s, so the average is 450/60 = 7.5 m/s",
        "A"),
    "S03-07": (
        "use the elastic result for a stationary target",
        "v_target = 2 m u/(m + 3m) = 2mu/(4m) = u/2. Check against both conservation laws: "
        "the incoming particle keeps (m - 3m)/(4m) u = -u/2, so p_after = m(-u/2) + 3m(u/2) "
        "= mu = p_before; and KE after = (1/2)m(u/2)^2 + (1/2)(3m)(u/2)^2 = mu^2/8 + "
        "3mu^2/8 = mu^2/2 = KE before",
        "A"),
    "S03-08": (
        "count three loops, so the length holds three half wavelengths",
        "the third harmonic has three loops, so L = 3 lambda/2 and lambda = 2L/3 = "
        "2(0.60)/3 = 0.40 m. f = v/lambda = 120/0.40 = 300 Hz. Check: the fundamental is "
        "v/2L = 120/1.2 = 100 Hz and the third harmonic is 3 x 100 = 300 Hz",
        "B"),
    "S03-09": (
        "divide the real depth by the refractive index",
        "for near-normal viewing the apparent depth is real depth / n = 2.4/1.5 = 1.6 m. "
        "Check the direction: a ray leaving the water bends away from the normal, so the "
        "stone is seen higher than it is, and 1.6 is less than 2.4",
        "E"),
    "S03-10": (
        "reduce the loaded pair, then divide the supply",
        "the load puts 3.0 k in parallel with 3.0 k: (3.0 x 3.0)/(3.0 + 3.0) = 1.5 k. "
        "Total 6.0 + 1.5 = 7.5 k, so the parallel section takes 12 x 1.5/7.5 = 2.4 V. "
        "Check against the unloaded divider: without the load the tap gives 12 x 3.0/9.0 = "
        "4.0 V, and loading a divider can only pull the tap down, so 2.4 is less than 4.0",
        "D"),
    "S03-11": (
        "compare the heat available with the heat needed before assuming anything melts",
        "warm the ice to 0 C: 0.20 x 2100 x 10 = 4200 J.  melt it all: 0.20 x 3.3e5 = 66000 J, so 70200 J is needed.  "
        "the water can give at most 0.40 x 4200 x 30 = 50400 J, which is not enough, so ice survives at 0 C.  "
        "heat left for melting = 50400 - 4200 = 46200 J, so 46200/3.3e5 = 0.14 kg melts and 0.20 - 0.14 = 0.060 kg remains",
        "A"),
    "S03-12": (
        "show that volume and mass both go as A",
        "V = (4/3) pi r^3 = (4/3) pi r0^3 A, so the volume is proportional to A, and the "
        "mass is proportional to A as well. Density = mass/volume is therefore independent "
        "of A, so it is unchanged. Check with the two values: A = 27 gives r = 3r0 and "
        "V = 27(4/3)pi r0^3; A = 216 gives r = 6r0 and V = 216(4/3)pi r0^3, the same volume "
        "per nucleon",
        "A"),
    "S03-13": (
        "scale the length, then square it, then multiply back up by N",
        "each small cube has side L N^(-1/3), so one piece has area 6 L^2 N^(-2/3).  "
        "all N together give 6 L^2 N^(1/3), and dividing by the original 6 L^2 leaves N^(1/3).  "
        "check on N = 8: side L/2, eight pieces of area 1.5 L^2 give 12 L^2 against 6 L^2, a factor of 2 = 8^(1/3)",
        "A"),
    "S03-14": (
        "separate the variables, then integrate the speed",
        "a = dv/dt = -kv separates to dv/v = -k dt, so v = u e^(-kt). Distance = integral "
        "of v dt from 0 to infinity = u/k. Check by dimensions: [u/k] = (m s^-1)/(s^-1) = m, "
        "a length. Check the size: a larger k stops the particle sooner, and u/k falls as k "
        "rises",
        "B"),
    "S03-15": (
        "impulse is the area under the force-time graph",
        "the graph is a triangle of base 0.20 s and height 20 N, so impulse = "
        "(1/2) x 0.20 x 20 = 2.0 N s. That is the change in momentum from rest, so "
        "v = 2.0/2.0 = 1.0 m/s. Check the size: an average force of 10 N acting for 0.20 s "
        "on 2.0 kg gives 10 x 0.20/2.0 = 1.0 m/s",
        "D"),
    "S03-16": (
        "divide the resolved equations to remove N and m",
        "resolve: N cos(theta) = mg vertically and N sin(theta) = mv^2/r horizontally. "
        "Dividing gives tan(theta) = v^2/(rg) = 15^2/(30 x 10) = 225/300 = 0.75, and "
        "tan(37 deg) is about 0.75, so theta is 37 deg. Check the direction: a faster car "
        "needs a steeper bank, and 0.75 is just below 1, so the angle is just below 45 deg",
        "A"),
    "S03-17": (
        "rearrange symbolically: stress sets the area, and the area sets the diameter",
        "sigma = mg/A so A = mg/sigma.  A = pi d^2/4, so pi d^2/4 = mg/sigma and d^2 = 4mg/(pi sigma), "
        "giving d = sqrt(4mg/(pi sigma)).  Numeric spot check with m = 1000, g = 10, sigma = 1.0e9: "
        "d^2 = 1.3e-5 m^2 and d = 3.6 mm, which is a sensible cable for a tonne",
        "A"),
    "S03-18": (
        "require sin(theta) not to exceed 1",
        "d = 1 mm/300 = 3.33e-6 m. The highest order is set by sin(theta) <= 1, so "
        "n <= d/lambda = 3.33e-6/5.0e-7 = 6.67 and the largest whole number is 6. "
        "Check the next one: n = 7 would need sin(theta) = 7 x 5.0e-7/3.33e-6 = 1.05, "
        "which does not exist",
        "E"),
    "S03-19": (
        "the lens equation, then a separate ratio",
        "1/v = 1/f - 1/u = 1/20 - 1/30 = (3 - 2)/60 = 1/60, so v = 60 cm. Magnification "
        "m = v/u = 60/30 = 2. Check the region: the object sits between f and 2f, which "
        "gives a real image beyond 2f magnified by more than one, and 2 is more than one",
        "B"),
    "S03-20": (
        "convert the ratings to resistances, then share a common current",
        "R = V^2/P, so R_60 = 240^2/60 = 960 ohm and R_100 = 240^2/100 = 576 ohm. In "
        "series the current is common, so each lamp takes I^2 R and the larger resistance "
        "takes the larger share; 960 is greater than 576, so the 60 W lamp is brighter. "
        "Check numerically: 960:576 = 5:3, total 1536 ohm, I = 240/1536 = 0.156 A, giving "
        "23 W in the 60 W lamp and 14 W in the 100 W lamp",
        "D"),
    "S03-21": (
        "series capacitors share the voltage inversely with C",
        "series capacitors carry the same charge, so V = Q/C makes the voltages inversely "
        "proportional to the capacitances: 2.0 and 6.0 uF share 12 V in the ratio 6:2 = 3:1, "
        "so the 2.0 uF takes 9.0 V. Check: C_series = (2.0 x 6.0)/8.0 = 1.5 uF, "
        "Q = 1.5e-6 x 12 = 1.8e-5 C, and V = Q/C = 1.8e-5/2.0e-6 = 9.0 V",
        "A"),
    "S03-22": (
        "apply the linear expansion relation",
        "delta_L = L0 alpha delta_T = 2.0 x 1.9e-5 x (120 - 20) = 2.0 x 1.9e-5 x 100 = "
        "3.8e-3 m = 3.8 mm. Check the size: the fractional change is 1.9e-5 x 100 = "
        "1.9e-3, about two parts in a thousand, and 1.9e-3 x 2.0 m = 3.8 mm",
        "C"),
    "S03-23": (
        "multiply the mass defect by c squared",
        "E = delta_m c^2 = 3.6e-30 x (3.0e8)^2 = 3.6e-30 x 9.0e16 = 3.24e-13 J. Check the "
        "order: 1e-30 kg is about 0.6 atomic mass units converted wholly, which should be a "
        "few hundred keV to a couple of MeV, and 3.24e-13 J is about 2.0 MeV",
        "B"),
    "S03-24": (
        "photon energy minus the work function, read as volts",
        "photon energy = 1240/400 = 3.1 eV. Maximum kinetic energy = 3.1 - 2.0 = 1.1 eV, "
        "and the stopping potential in volts is numerically the maximum kinetic energy in "
        "electronvolts, so 1.1 V. Check the direction: the stopping potential must be less "
        "than the photon energy, and it is the difference rather than the sum",
        "E"),
    "S03-25": (
        "weight minus the upthrust",
        "weight = 0.50 x 10 = 5.0 N. Upthrust = rho V g = 1000 x 2.0e-4 x 10 = 2.0 N. "
        "Reading = 5.0 - 2.0 = 3.0 N. Check the density: the stone is 0.50/2.0e-4 = "
        "2500 kg/m^3, denser than water, so it sinks and the reading stays positive",
        "D"),
},
4: {
    "S04-01": (
        "find the internal resistance from the lost volts, then re-divide",
        "I = 4.8/12 = 0.40 A; lost volts = 6.0 - 4.8 = 1.2 V, so r = 1.2/0.40 = 3.0 ohm. With "
        "6.0 ohm in place: total 9.0 ohm, I = 6.0/9.0 = 2/3 A, V = (2/3) x 6.0 = 4.0 V. Check "
        "the direction: the new resistor is smaller so the terminal voltage must fall below "
        "4.8 V, and 4.0 V is below it",
        "C"),
    "S04-02": (
        "put the dimensions of each option into GM and r",
        "[G] = N m^2 kg^-2 = (kg m s^-2) m^2 kg^-2 = m^3 kg^-1 s^-2, so [GM] = m^3 s^-2. Then "
        "r^3/GM has dimensions m^3/(m^3 s^-2) = s^2 and its square root is s. Check the "
        "runner-up: GM/r is m^3 s^-2/m = m^2 s^-2, whose root is m/s, a speed and not a time",
        "A"),
    "S04-03": (
        "moments about the foot, then divide friction by the normal reaction",
        "The wall is smooth so it gives only a horizontal R; hence N = W and F = R. Moments "
        "about the foot: R x L sin30 = W x (L/2) cos30, so R = W/(2 tan30) = W/(2/sqrt3) = "
        "W sqrt3/2. Then mu = F/N = R/W = sqrt3/2. Check the limit: a ladder stood upright "
        "needs no friction, and the general expression 1/(2 tan theta) goes to zero as theta "
        "goes to 90 degrees",
        "B"),
    "S04-04": (
        "reduce from the inside out: inner pair, then the branch, then the outer parallel "
        "section, then the total",
        "R4 and R5 in parallel: (12 x 6.0)/(12 + 6.0) = 72/18 = 4.0 ohm. The lower branch is "
        "R3 + 4.0 = 8.0 + 4.0 = 12 ohm. In parallel with R2 = 6.0 ohm: (6.0 x 12)/(18) = "
        "4.0 ohm, so the total is 4.0 + 4.0 = 8.0 ohm and the battery current is 12/8.0 = "
        "1.5 A. The parallel section carries all of it and has 1.5 x 4.0 = 6.0 V across it, so "
        "the lower branch takes 6.0/12 = 0.50 A and NOT the 0.75 A an equal split would give. "
        "Across the inner pair: 0.50 x 4.0 = 2.0 V, so I(R4) = 2.0/12 = 1/6 A. Check by adding "
        "the pair: I(R5) = 2.0/6.0 = 1/3 A, and 1/6 + 1/3 = 1/2 A, which is the branch current",
        "A"),
    "S04-05": (
        "multiply the rate out to a lifetime and read the exponent",
        "70 x 60 = 4200 beats an hour; x 24 = 100800 a day; x 365 = 36792000 a year; "
        "x 80 = 2943360000, which is 2.9 x 10^9. Check by a second route: a rate of about "
        "10^2 a minute, a year of about 5 x 10^5 minutes and 80 years of about 4 x 10^7 "
        "minutes give 10^2 x 4 x 10^7 = 4 x 10^9, the same power of ten",
        "C"),
    "S04-06": (
        "compare the time of flight at the two angles",
        "Time of flight is 2u sin(theta)/g, so the ratio is sin60/sin30 = (sqrt3/2)/(1/2) = "
        "sqrt3. Check the companion quantities: the 60-degree ball rises three times as high, "
        "since sin^2 60 = 3/4 against sin^2 30 = 1/4, but stays up only sqrt3 times as long",
        "A"),
    "S04-07": (
        "resolve the velocity along and perpendicular to the wall",
        "The component along the wall, v sin(theta), is unchanged. The component along the "
        "normal reverses, from +v cos(theta) to -v cos(theta), a change of 2v cos(theta), so "
        "the change in momentum is 2mv cos(theta). Check the limit theta = 0, a head-on "
        "bounce: the expression becomes 2mv, which is right",
        "B"),
    "S04-08": (
        "set gravity equal to the centripetal requirement at the top",
        "At the top the weight and the normal reaction both point to the centre, so "
        "mg + N = mv^2/r. Contact is just lost when N = 0, leaving mg = mv^2/r and "
        "v = sqrt(gr). Check the runner-up: sqrt(2gr) is the speed needed to reach the top "
        "from the bottom, which is a different question",
        "D"),
    "S04-09": (
        "the wave speed is the square root of the tension",
        "v = sqrt(T/mu), so v is proportional to sqrt(T). The tension rises to 121/100 of its "
        "old value, whose square root is 11/10, so the new speed is 40 x 11/10 = 44 m/s. "
        "Check the fraction: 1.1^2 = 1.21, which is exactly the stated 21 per cent rise",
        "E"),
    "S04-10": (
        "Snell at the end face, then the critical condition at the wall",
        "sin i = n sin r at the end face. At the side wall the ray makes an angle 90 - r with "
        "the normal, so total internal reflection needs sin(90 - r) >= 1/n, that is "
        "cos r >= 1/n. The largest sin i comes from the largest r, at cos r = 1/n, giving "
        "sin r = sqrt(1 - 1/n^2) and sin i = n sqrt(1 - 1/n^2) = sqrt(n^2 - 1). Check "
        "n = sqrt2: sin i = 1, the grazing limit, which is the largest value possible",
        "A"),
    "S04-11": (
        "share the supply in the ratio of the two resistances",
        "The same current passes through both arms, so the output across the fixed resistor is "
        "6.0 x 2.0/(1.0 + 2.0) = 6.0 x 2/3 = 4.0 V. Check the direction: the warm thermistor "
        "has fallen to half the fixed resistance, so it takes only a third of the supply and "
        "the output must be above half of 6.0 V, as 4.0 V is",
        "D"),
    "S04-12": (
        "combine the volume and the mass scaling laws",
        "R = r0 A^(1/3), so V = (4/3)pi R^3 is proportional to (A^(1/3))^3 = A. The mass is "
        "proportional to the mass number A. Density is mass over volume, so it goes as A/A, a "
        "constant, and the ratio is 1. Check with 8A: the radius doubles, the volume rises by "
        "2^3 = 8 and the mass rises by 8, leaving the density unchanged",
        "B"),
    "S04-13": (
        "multiply the gradient by the electronic charge",
        "eV = hf - W rearranges to V = (h/e)f - W/e, so the gradient of the graph is h/e. "
        "Then h = e x gradient = 1.6e-19 x 4.0e-15 = 6.4e-34 J s. Check the units: "
        "C x V s = (J/V) x V s = J s. Check the size against the accepted 6.6e-34, which it "
        "matches to two figures",
        "E"),
    "S04-14": (
        "solve the equation for eta and reduce to base units",
        "eta = F/(6 pi r v), and 6 pi is dimensionless. [F] = kg m s^-2, [r] = m and "
        "[v] = m s^-1, so [eta] = kg m s^-2 / (m x m s^-1) = kg m s^-2 / (m^2 s^-1) = "
        "kg m^-1 s^-1. Check against a familiar value: water has a viscosity of about 1e-3 in "
        "these units, and the pascal second is a large viscosity, which fits",
        "C"),
    "S04-15": (
        "the flight time is proportional to the vertical launch speed, and the horizontal "
        "speed is never touched by a bounce",
        "First fall: 20 = 0.5 x 10 x t^2, so t^2 = 4 and t = 2.0 s, giving a first leg of "
        "15 x 2.0 = 30 m. The vertical speed at the first bounce is 10 x 2.0 = 20 m/s; halved "
        "and reversed it is 10 m/s upward, so the second flight lasts 2 x 10/10 = 2.0 s and "
        "covers another 15 x 2.0 = 30 m. Halved again to 5.0 m/s the third flight lasts "
        "1.0 s and covers 15 m. Total 30 + 30 + 15 = 75 m. Check: the ball is in the air "
        "2.0 + 2.0 + 1.0 = 5.0 s and 15 x 5.0 = 75 m, and the three flight times are in the "
        "ratio 2:2:1, which is exactly the ratio of the vertical speeds 20:10:5",
        "D"),
    "S04-16": (
        "resolve in two directions and eliminate one tension",
        "Horizontally T_L sin60 = T_R sin30, so T_L (sqrt3/2) = T_R/2 and T_L = T_R/sqrt3. "
        "Vertically T_L cos60 + T_R cos30 = W, so T_R/(2 sqrt3) + T_R sqrt3/2 = W, giving "
        "T_R (1 + 3)/(2 sqrt3) = T_R (2/sqrt3) = W and T_R = W sqrt3/2. Check the size: the "
        "right-hand wire hangs closer to the vertical, so it carries more than half the "
        "weight, and sqrt3/2 = 0.87 is more than a half",
        "B"),
    "S04-17": (
        "divide the horizontal equation by the vertical one",
        "The bob moves on a circle of radius r = L sin(theta). Vertically T cos(theta) = mg; "
        "horizontally T sin(theta) = m omega^2 r. Dividing gives tan(theta) = "
        "omega^2 L sin(theta)/g, so omega^2 = g/(L cos(theta)) and the period is "
        "2 pi sqrt(L cos(theta)/g). Check the limit theta = 0: the expression becomes "
        "2 pi sqrt(L/g), the simple pendulum, which is right",
        "A"),
    "S04-18": (
        "extension goes inversely with the cross-sectional area",
        "x = FL/(AE), and F, L and E are the same for both wires, so x is proportional to 1/A "
        "and A is proportional to d^2. The second wire has twice the diameter and therefore "
        "four times the area, so one quarter of the extension: the ratio is 1/4. Check the "
        "direction: a thicker wire is stiffer, so its extension must be the smaller, and 1/4 "
        "is smaller",
        "E"),
    "S04-19": (
        "the two resonances are the first and the third harmonic",
        "A pipe closed at one end resonates at f, 3f, 5f, so 400 Hz and 1200 Hz are the first "
        "and third, and 1200 = 3 x 400 confirms the assignment. The fundamental has wavelength "
        "4L, so L = v/(4f) = 340/(4 x 400) = 340/1600 = 0.2125 m, about 0.21 m. Check the "
        "neighbours: 0.85 m would be a quarter of 340/100, a fundamental of 100 Hz rather "
        "than 400 Hz",
        "C"),
    "S04-20": (
        "the critical angle is fixed by the refractive index",
        "The light starts inside the material, so it emerges only while the angle of incidence "
        "stays below the critical angle: sin C = 1/n = 1/sqrt2, so C = 45 degrees. Check the "
        "exactness: sin45 = 1/sqrt2 precisely, so 45 degrees is the exact answer and not a "
        "rounded value",
        "D"),
    "S04-21": (
        "reduce the parallel pair, then use the total resistance",
        "6.0 || 3.0 = (6.0 x 3.0)/(6.0 + 3.0) = 18/9 = 2.0 ohm; total = 2.0 + 2.0 = 4.0 ohm; "
        "I = 6.0/4.0 = 1.5 A. Check the size: with negligible internal resistance the current "
        "must exceed 6.0/6.0 = 1.0 A, the value if the battery saw 6.0 ohm, and 1.5 A does",
        "E"),
    "S04-22": (
        "conserve charge, then divide by the total capacitance",
        "The charge has nowhere to go, so it is still 48 uC, and the two capacitors end up in "
        "parallel, C = 4.0 + 8.0 = 12 uF. Then V = Q/C = 48/12 = 4.0 V. Check the direction: "
        "the shared voltage must be below the original 48/4.0 = 12 V, because the same charge "
        "now sits on more capacitance, and 4.0 V is below it",
        "B"),
    "S04-23": (
        "heat lost equals heat gained",
        "0.40 c (90 - T) = 0.10 c (T - 10), so 36 - 0.4T = 0.1T - 1 and 37 = 0.5T, giving "
        "T = 74 C. Check the position: the masses are in the ratio 4:1, so the final "
        "temperature sits one fifth of the way from 90 towards 10, and 90 - 16 = 74",
        "D"),
    "S04-24": (
        "count the half-lives",
        "24/8.0 = 3 half-lives, so the fraction remaining is (1/2)^3 = 1/8. Check the "
        "distractor: 1/3 is what a linear decay would give, but each half-life halves what is "
        "left rather than removing a fixed amount",
        "C"),
    "S04-25": (
        "equal wavelengths mean equal momenta, then kinetic energy goes as 1/m",
        "lambda = h/p, so equal de Broglie wavelengths mean equal momenta. With KE = p^2/(2m) "
        "and p the same, the kinetic energy is inversely proportional to the mass, so "
        "KE_electron/KE_proton = m_proton/m_electron = 1836. Check the direction: the lighter "
        "particle carries more kinetic energy at the same momentum, and 1836 is more than 1",
        "A"),
},
5: {
    "S05-01": (
        "build the product of powers and write one equation for each base dimension",
        "Suppose the answer is rho^a v^b d^c. Its dimensions are M^a L^(-3a+b+c) T^(-b), and "
        "the target is M T^-1. Mass: a = 1. Time: -b = -1, so b = 1. Length: -3(1) + 1 + c = 0, "
        "so c = 2. The combination is rho v d^2, and substituting back gives "
        "M L^-3 x L T^-1 x L^2 = M T^-1, the lengths cancelling exactly. Check the physics: "
        "density times speed times area is a volume per second times a density, which is a "
        "mass per second",
        "A"),
    "S05-02": (
        "take moments about the hinge",
        "clockwise: 150 N at 2.0 m plus 45 N at 4.0 m = 300 + 180 = 480 N m. Only the vertical "
        "part of the cable tension turns the rod; with a 3-4-5 triangle that part is T x 3/5 "
        "acting at 4.0 m, so (3T/5) x 4.0 = 480, 12T/5 = 480, T = 200 N",
        "C"),
    "S05-03": (
        "the two branch currents give the two midpoint voltages",
        "left branch total 2.0 + 6.0 = 8.0 ohm, so its top 2.0 ohm drops 12 x 2/8 = 3.0 V; "
        "right branch total 6.0 + 3.0 = 9.0 ohm, so its top 6.0 ohm drops 12 x 6/9 = 8.0 V. "
        "X sits 3.0 V below the top rail, Y sits 8.0 V below it, so V_X - V_Y = 8.0 - 3.0 = 5.0 V",
        "E"),
    "S05-04": (
        "multiply out the seconds in a year",
        "365 x 24 x 3600 = 31,536,000 s. log10 of that is 7.5 and it is just under 10^7.5, "
        "so the nearest power of ten is 10^7",
        "B"),
    "S05-05": (
        "area under the v-t graph: two triangles plus a rectangle",
        "triangle 0-5 s = 1/2 x 5 x 20 = 50 m; rectangle 5-15 s = 10 x 20 = 200 m; "
        "triangle 15-19 s = 1/2 x 4 x 20 = 40 m; total = 50 + 200 + 40 = 290 m",
        "D"),
    "S05-06": (
        "three stages: energy on the ramp, work against friction, then momentum through an "
        "inelastic collision",
        "The ramp is smooth, so the kinetic energy at its foot is m g h = 0.50 x 10 x 0.40 = "
        "2.0 J. Friction on the 0.50 kg ball is 0.20 x 0.50 x 10 = 1.0 N, so over 1.0 m it "
        "takes 1.0 J and the kinetic energy at the collision is 2.0 - 1.0 = 1.0 J. Hence "
        "v = sqrt(2 x 1.0 / 0.50) = 2.0 m/s and p = 0.50 x 2.0 = 1.0 kg m/s. Sticking conserves "
        "momentum: V = 1.0 / 0.80 = 1.25 m/s, so the kinetic energy is 0.5 x 0.80 x 1.25^2 = "
        "0.625 J, and the collision destroyed 0.375 J of the 1.0 J. Friction on the combined "
        "mass is 0.20 x 0.80 x 10 = 1.6 N, so the distance is 0.625 / 1.6 = 0.3906 m, which is "
        "0.39 m to two significant figures",
        "D"),
    "S05-07": (
        "energy between lowest and highest points, then taut-string condition at the top",
        "1/2 m u^2 = m g (2r) + 1/2 m v^2, so v^2 = u^2 - 4gr. At the top the string stays taut "
        "if m v^2/r >= m g, i.e. v^2 >= g r, so u^2 - 4gr >= g r, u^2 >= 5gr, u >= sqrt(5gr)",
        "A"),
    "S05-08": (
        "transverse velocity is -wave speed times the local slope",
        "v_y = -v (dy/dx). At Q the slope dy/dx = -0.40, so v_y = -1.5 x (-0.40) = +0.60 m/s, "
        "i.e. 0.60 m/s upward",
        "C"),
    "S05-09": (
        "thin lens formula, then magnification",
        "1/v = 1/f - 1/u = 1/20 - 1/12 = (3-5)/60 = -2/60, so v = -30 cm. "
        "m = -v/u = -(-30)/12 = 2.5",
        "E"),
    "S05-10": (
        "net emf over the total resistance",
        "the cells oppose, so net emf = 12 - 6 = 6 V. Total resistance = 3.0 + 1.0 + 2.0 = "
        "6.0 ohm. I = 6 / 6.0 = 1.0 A",
        "B"),
    "S05-11": (
        "count the half-lives",
        "24 days / 8.0 days = 3 half-lives, so the fraction remaining is (1/2)^3 = 1/8",
        "B"),
    "S05-12": (
        "photon momentum p = h/lambda",
        "p = 6.6 x 10^-34 / (600 x 10^-9) = 1.1 x 10^-27 kg m s^-1",
        "D"),
    "S05-13": (
        "average speed, then convert m/s to km/h",
        "speed = 100 m / 10 s = 10 m/s; multiply by 3.6 gives 36 km/h",
        "A"),
    "S05-14": (
        "time of fall from the height, then the horizontal range",
        "t = sqrt(2h/g) = sqrt(2 x 20 / 10) = 2.0 s; range = 12 x 2.0 = 24 m",
        "C"),
    "S05-15": (
        "Pythagoras for the resultant, then equal and opposite",
        "resultant of 3 N and 4 N at right angles = sqrt(3^2 + 4^2) = 5 N; the equilibrating "
        "force is 5 N opposite to the resultant",
        "E"),
    "S05-16": (
        "radius of the latitude circle, then centripetal acceleration",
        "a point at latitude lambda sits R cos(lambda) from the spin axis, so its a = omega^2 R "
        "cos(lambda); the equatorial value is omega^2 R, and the ratio is cos(lambda)",
        "E"),
    "S05-17": (
        "centre of mass by negative mass",
        "treat the uncut 2a square as mass 4 at (a, a) and the removed a-square as mass 1 at "
        "(a/2, 3a/2); remaining mass 3. x_new = (4a - a/2)/3 = 7a/6; the horizontal shift from "
        "x = a is 7a/6 - a = a/6",
        "B"),
    "S05-18": (
        "fringe spacing beta = lambda D / d",
        "beta = (500 x 10^-9 x 1.5) / (1.0 x 10^-3) = 7.5 x 10^-4 m = 0.75 mm "
        "(convert nm and mm to metres first)",
        "D"),
    "S05-19": (
        "sin of the critical angle is the ratio of the refractive indices",
        "sin(theta_c) = n_air / n_glass = 1.00 / 1.50 = 0.67",
        "A"),
    "S05-20": (
        "intersection of the load line with the diode segment",
        "load line V = 1.0 - 0.1 I_mA; diode line I_mA = 22(V - 0.55)/0.27. Substituting gives "
        "I = 22(0.45 - 0.1 I)/0.27, so 0.27 I = 9.9 - 2.2 I, 2.47 I = 9.9, I = 4.0 mA",
        "C"),
    "S05-21": (
        "network capacitance first, then the charge on the whole chain, then that same "
        "charge on the single capacitor",
        "the 2.0 and 4.0 microfarad capacitors are in parallel, so they add: C_pair = 6.0 uF. "
        "That pair is in series with 3.0 uF, so 1/C = 1/6.0 + 1/3.0 = 0.50 per uF, C = 2.0 uF. "
        "The supply delivers Q = C V = 2.0 x 12 = 24 uC. A series chain carries one charge, so "
        "the 3.0 uF holds all 24 uC and V = 24 / 3.0 = 8.0 V. Check: the pair holds the same "
        "24 uC, so its p.d. is 24/6.0 = 4.0 V, and 8.0 + 4.0 = 12 V, the supply. The bigger "
        "capacitance takes the smaller share, as it must",
        "A"),
    "S05-22": (
        "three stages: warm the ice, melt it, then warm the water; then divide the total by "
        "the power",
        "warming the ice: 0.50 x 2100 x 10 = 10500 J. Melting it, with no temperature change: "
        "0.50 x 3.3 x 10^5 = 165000 J. Warming the water, now with water's own specific heat: "
        "0.50 x 4200 x 20 = 42000 J. Total 10500 + 165000 + 42000 = 217500 J, and at 500 W the "
        "time is 217500 / 500 = 435 s. Check: the melting term alone exceeds the other two put "
        "together, 165000 against 52500, which is the shape a heating curve should have",
        "E"),
    "S05-23": (
        "mass-energy with the given shortcut",
        "E = (defect in u) x (930 MeV per u) = 0.20 x 930 = 186 MeV",
        "B"),
    "S05-24": (
        "photoelectric maximum kinetic energy K_max = hf - phi",
        "K_max = 5.0 eV - 2.0 eV = 3.0 eV",
        "D"),
    "S05-25": (
        "Pascal: the force scales with the piston area",
        "pressure is equal, so F_large / F_small = A_large / A_small = 40 / 2.0 = 20; "
        "F_large = 100 x 20 = 2000 N",
        "A"),
},
6: {
    "S06-01": (
        "parallel the voltmeter with the 8.0 ohm, then divide the supply",
        "values read off the figure: 12 V cell, 4.0 ohm, 8.0 ohm, voltmeter 24 ohm across "
        "the 8.0 ohm; 8.0 || 24 = (8.0 x 24)/(8.0 + 24) = 192/32 = 6.0 ohm; total "
        "4.0 + 6.0 = 10 ohm; I = 12/10 = 1.2 A; the voltmeter reads the p.d. across the "
        "pair, 1.2 x 6.0 = 7.2 V",
        "A"),
    "S06-02": (
        "propagate a small change through a square root",
        "T = 2 pi sqrt(l/g), so T goes as l^(1/2); a 4.0 % change in l becomes "
        "(1/2) x 4.0 % = 2.0 % in T",
        "C"),
    "S06-03": (
        "resolve on the incline, then ADD friction because the block moves up",
        "the figure gives a 30 degree incline; W = 2.0 x 10 = 20 N; along the plane "
        "20 sin 30 = 10 N; perpendicular 20 cos 30 = 17.3 N, so N = 17.3 N; "
        "f = 0.25 x 17.3 = 4.3 N down the slope; constant speed so F = 10 + 4.3 = 14.3 N, "
        "which is 14 N to two significant figures",
        "B"),
    "S06-04": (
        "reduce inside out, then walk back down the p.d.s",
        "6.0 || 3.0 = 18/9 = 2.0; second branch 4.0 + 2.0 = 6.0; 6.0 || 6.0 = 3.0; total "
        "2.0 + 5.0 + 3.0 = 10 ohm; I = 12/10 = 1.2 A; section p.d. 1.2 x 3.0 = 3.6 V; "
        "branch current 3.6/6.0 = 0.60 A; pair p.d. 0.60 x 2.0 = 1.2 V; "
        "I(3.0 ohm) = 1.2/3.0 = 0.40 A; P = 0.40^2 x 3.0 = 0.48 W",
        "D"),
    "S06-05": (
        "estimate a rate times a lifetime, then round on the sqrt(10) boundary",
        "70 x 60 x 24 x 365 = 3.68e7 beats a year; over 80 years that is 2.94e9; the "
        "boundary between 10^9 and 10^10 is sqrt(10) x 10^9 = 3.16e9, and 2.94 is below "
        "it, so the answer is 10^9",
        "E"),
    "S06-06": (
        "area under the velocity-time graph over the whole 12 s",
        "triangle 0.5 x 4.0 x v = 2v; rectangle 6.0 x v = 6v; triangle 0.5 x 2.0 x v = v; "
        "total 9v; 9v/12 = 3v/4",
        "B"),
    "S06-07": (
        "two conservation laws, then divide to eliminate v",
        "mu = 2mv cos(th); (1/2)mu^2 = 2 x (1/2)mv^2 so u = sqrt2 v; then "
        "sqrt2 v = 2v cos(th) gives cos(th) = sqrt2/2 and th = 45 degrees",
        "A"),
    "S06-08": (
        "strain, then stress, then force, then mass",
        "strain = 1.0e-3/2.0 = 5.0e-4; stress = 2.0e11 x 5.0e-4 = 1.0e8 Pa; "
        "F = 1.0e8 x 1.0e-6 = 100 N; m = 100/10 = 10 kg",
        "C"),
    "S06-09": (
        "algebraic superposition, carrying the sign",
        "+3.0 cm and -1.0 cm add to +2.0 cm; with A = 3.0 cm that is 2.0/3.0 of A, "
        "so 2A/3",
        "E"),
    "S06-10": (
        "Snell for the index, then v = c/n",
        "n = sin 60 / sin 30 = (sqrt3/2)/(1/2) = sqrt3 = 1.73; "
        "v = 3.0e8/1.73 = 1.73e8, so 1.7 x 10^8 m/s",
        "D"),
    "S06-11": (
        "find the current, then the power in the internal resistance",
        "I = eps/(R + r); the power dissipated inside the cell is I^2 r = "
        "eps^2 r/(R + r)^2",
        "B"),
    "S06-12": (
        "activity times the interval, valid because lambda t is tiny",
        "lambda t = 1.0e-8 x 60 = 6.0e-7, far below 1, so the number decaying is "
        "N lambda t = 4.0e20 x 6.0e-7 = 2.4e14",
        "A"),
    "S06-13": (
        "carry every conversion, then round on the sqrt(10) boundary",
        "12 x 60 = 720 breaths an hour; 720 x 24 = 17 280 a day; 17 280 x 0.50 = 8640 "
        "litres; the boundary between 10^3 and 10^4 is sqrt(10) x 10^3 = 3162, and 8640 "
        "is above it, so 10^4",
        "E"),
    "S06-14": (
        "subtract the velocities as vectors, then Pythagoras",
        "v_P - v_Q = (15 east) - (20 north); the two are perpendicular, so the magnitude "
        "is sqrt(15^2 + 20^2) = sqrt(625) = 25 m/s",
        "C"),
    "S06-15": (
        "two regimes: accelerating while the string is taut, then friction alone",
        "driving force 2.0 x 10 - 0.20 x 3.0 x 10 = 20 - 6.0 = 14 N over 5.0 kg, so "
        "a = 2.8 m/s^2; after 1.0 m, v^2 = 2 x 2.8 x 1.0 = 5.6; then only friction acts, "
        "a = -0.20 x 10 = -2.0 m/s^2, so s = 5.6/(2 x 2.0) = 1.4 m",
        "D"),
    "S06-16": (
        "friction supplies the centripetal force",
        "mu m g = m v^2/r, so v^2 = mu g r and v = sqrt(mu g r)",
        "A"),
    "S06-17": (
        "linear expansion over the temperature rise",
        "dT = 120 - 20 = 100 K; dL = 2.0 x 1.2e-5 x 100 = 2.4e-3 m = 2.4 mm",
        "E"),
    "S06-18": (
        "receding-source Doppler, then expand to first order",
        "a receding source gives f' = f u/(u + v) = f/(1 + v/u); expanding gives "
        "f(1 - v/u) to first order",
        "B"),
    "S06-19": (
        "apparent depth is the real depth divided by the index",
        "3.0/1.5 = 2.0 m, which is less than the real depth, as a pool must look shallower",
        "C"),
    "S06-20": (
        "combine the pair, take the pair's p.d., then divide by 2.0 ohm",
        "6.0 || 2.0 = 12/8 = 1.5 ohm; total 3.0 + 1.5 = 4.5 ohm; I = 6.0/4.5 = 1.333 A; "
        "pair p.d. = 1.333 x 1.5 = 2.0 V; I(2.0 ohm) = 2.0/2.0 = 1.0 A",
        "D"),
    "S06-21": (
        "charge is conserved and energy is not; compare the two energies",
        "Q = 4.0e-6 x 10 = 4.0e-5 C; energy before = (1/2) x 4.0e-6 x 100 = 2.0e-4 J; "
        "after sharing, C = 10e-6 and V = 4.0e-5/10e-6 = 4.0 V, so the energy is "
        "(1/2) x 10e-6 x 16 = 8.0e-5 J; the fraction lost is "
        "(2.0e-4 - 8.0e-5)/2.0e-4 = 60 %",
        "A"),
    "S06-22": (
        "the plateau is the melting stage; power times time over the mass",
        "plateau 6.0 min = 360 s; E = 150 x 360 = 54 000 J; "
        "L = 54 000/0.30 = 180 000 = 1.8 x 10^5 J/kg",
        "C"),
    "S06-23": (
        "count the half-lives, then halve that many times",
        "24/8.0 = 3 half-lives; (1/2)^3 = 1/8",
        "B"),
    "S06-24": (
        "set the photon energy equal to the work function at threshold",
        "hc/lambda = phi at threshold, so lambda = hc/phi",
        "E"),
    "S06-25": (
        "upthrust equals weight, then cancel g",
        "rho_w x 0.60V x g = m g, so m = 0.60 rho_w V",
        "D"),
},
}


def main():
    import importlib

    out = {}
    missing = []
    for sec_no, entries in sorted(LEDGER.items()):
        mod = importlib.import_module("sec%02d" % sec_no)
        by_id = {q["id"]: q for q in mod.QUESTIONS}
        for qid, (method, working, letter) in sorted(entries.items()):
            if qid not in by_id:
                missing.append(qid)
                continue
            q = by_id[qid]
            stated = "ABCDE"[q["ans"]]
            out[qid] = {
                "section": sec_no,
                "verified": letter == stated,
                "method": method,
                "working": working,
                "hand_answer": letter,
                "stored_answer": stated,
                "agrees": letter == stated,
            }
    if missing:
        raise SystemExit("ledger names questions that do not exist: %s" % missing)
    path = os.path.join(HERE, "ledger.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    bad = [k for k, v in out.items() if not v["agrees"]]
    per_sec = {}
    for v in out.values():
        per_sec[v["section"]] = per_sec.get(v["section"], 0) + 1
    print("ledger: %d questions across %d section(s) (%s), %d agree with the stored key"
          % (len(out), len(per_sec),
             ", ".join("S%02d: %d" % (k, per_sec[k]) for k in sorted(per_sec)),
             len(out) - len(bad)))
    if bad:
        print("DISAGREEMENTS (a human says the stored answer is wrong):")
        for k in bad:
            print("   %s  hand %s  stored %s" % (k, out[k]["hand_answer"], out[k]["stored_answer"]))
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
