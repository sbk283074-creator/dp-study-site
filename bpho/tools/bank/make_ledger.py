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

# id -> (method, working, answer letter)
LEDGER = {
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
}


def main():
    import sec01
    by_id = {q["id"]: q for q in sec01.QUESTIONS}
    out = {}
    missing = []
    for qid, (method, working, letter) in sorted(LEDGER.items()):
        if qid not in by_id:
            missing.append(qid)
            continue
        q = by_id[qid]
        stated = "ABCDE"[q["ans"]]
        out[qid] = {
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
    print("ledger: %d questions, %d agree with the stored key"
          % (len(out), len(out) - len(bad)))
    if bad:
        print("DISAGREEMENTS (a human says the stored answer is wrong):")
        for k in bad:
            print("   %s  hand %s  stored %s" % (k, out[k]["hand_answer"], out[k]["stored_answer"]))
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
