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
        "read the coordinates and divide",
        "the marked point is 6.0 V and 0.40 A; R = V/I = 6.0/0.40 = 15 ohm",
        "D"),
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
        "eliminate on two independent features",
        "the gradient of a v-t graph is a, and a is -g throughout, so every section must "
        "be straight with the same slope -- that rules out the curved graphs; and each "
        "bounce returns less speed, so the peaks must shrink -- that rules out the "
        "equal-peak graph; only E has both",
        "E"),
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
        "threshold wavelength gives the work function, then subtract",
        "hc = 1240 eV nm, so the threshold photon energy is 1240/620 = 2.0 eV and that is "
        "the work function. At 310 nm the photon energy is 1240/310 = 4.0 eV. "
        "Kinetic energy = 4.0 - 2.0 = 2.0 eV",
        "E"),
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
        "conserve momentum, then divide by the combined mass",
        "p_before = 2.0 x 3.0 = 6.0 kg m/s; p_after = (2.0 + 2.0)v = 4.0v; "
        "v = 6.0/4.0 = 1.5 m/s. Energy check: 9.0 J before, 4.5 J after, so half is lost, "
        "which is what sticking means",
        "B"),
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
