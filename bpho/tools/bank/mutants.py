# -*- coding: utf-8 -*-
"""Prove the gates have teeth.

The brief was explicit: "don't trust your tool that you write only".  A gate suite that
reports "all gates passed" on the very content its author wrote has proved nothing --
it may be measuring nothing at all.  The only way to know a gate works is to break a
question in a specific way and watch that specific gate fire.

So: take the real Section 1, which passes.  For each mutation below, break exactly one
thing, re-run the whole suite, and assert that the expected gate complains.  A mutation
that slips through is a hole in the gate suite and is reported as a failure here.

Run:  python mutants.py
"""
import copy
import sys

import gates as G
import sec01

GOOD = [copy.deepcopy(q) for q in sec01.QUESTIONS]


def find(mutated, qid):
    return next(q for q in mutated if q["id"] == qid)


# ── each mutant: (name, gate that must fire, what it breaks, mutate fn) ───────
MUTANTS = []


def mutant(name, gate, desc):
    def deco(fn):
        MUTANTS.append((name, gate, desc, fn))
        return fn
    return deco


@mutant("structure.duplicate_id", "G1", "give two questions the same id")
def m1(qs):
    find(qs, "S01-07")["id"] = "S01-06"


@mutant("structure.six_options", "G1", "give a question six options")
def m2(qs):
    q = find(qs, "S01-03")
    q["opts"] = q["opts"] + ["v is proportional to r cubed"]


@mutant("structure.two_options_alike", "G1", "make two options read the same")
def m3(qs):
    q = find(qs, "S01-12")
    q["opts"][1] = q["opts"][0]


@mutant("structure.out_of_scope_module", "G1", "set a module to one that is out of scope")
def m4(qs):
    find(qs, "S01-09")["module"] = "N"


@mutant("structure.wrong_mix", "G1", "swap two questions between modules")
def m5(qs):
    find(qs, "S01-09")["module"] = "A"


@mutant("structure.answer_out_of_range", "G1", "point the key at option F")
def m6(qs):
    find(qs, "S01-05")["ans"] = 5


@mutant("distractors.filler_option", "G2", "replace a distractor with filler")
def m7(qs):
    q = find(qs, "S01-08")
    q["distractors"][0] = "wrong"


@mutant("distractors.not_marked_correct", "G2", "forget to mark the key as correct")
def m8(qs):
    q = find(qs, "S01-11")
    q["distractors"][q["ans"]] = "uses the wrong angle"


@mutant("distractors.two_identical_errors", "G2", "give two wrong options the same cause")
def m9(qs):
    q = find(qs, "S01-19")
    q["distractors"][0] = q["distractors"][2]


@mutant("agreement.key_disagrees_with_solution", "G3",
        "state an answer in the solution that is not the stored key")
def m10(qs):
    q = find(qs, "S01-01")
    q["sol"] = q["sol"].replace("Answer: B", "Answer: C")


@mutant("agreement.no_answer_stated", "G3", "remove the 'Answer: <letter>' line")
def m11(qs):
    q = find(qs, "S01-13")
    q["sol"] = q["sol"].replace("Answer: E", "And so we are done.")


@mutant("notation.caret_survives_to_reader", "G3",
        "write a caret supify() cannot repair (space after the ^)")
def m12(qs):
    # NOT `omega^2` -- that one is silently repaired upstream by supify(), so the
    # reader never sees a caret and there is no defect to catch.  The first version of
    # this mutant used `omega^2` and reported MISSED, which was the correct answer to
    # the wrong question.  The real failure mode is a caret the repair MISSES.
    q = find(qs, "S01-18")
    q["sol"] = q["sol"] + "<p>since omega^ 2 r = g</p>"


@mutant("notation.ascii_exponent", "G3", "write 10 m-3 instead of 10 m to the minus 3")
def m13(qs):
    q = find(qs, "S01-19")
    q["sol"] = q["sol"] + "<p>units are J m-3</p>"


@mutant("calculator.decimal_in_solution", "G3",
        "put an evaluated root in the solution with nothing to justify it")
def m14(qs):
    q = find(qs, "S01-17")
    q["sol"] = q["sol"] + "<p>The normal reaction is 40.3113 newtons.</p>"


@mutant("profile.too_few_steps", "G4", "declare fewer steps than the difficulty demands")
def m15(qs):
    q = find(qs, "S01-04")
    q["profile"]["steps"] = q["profile"]["steps"][:2]


@mutant("profile.approx_mismatch", "G4",
        "claim an approximation the solution does not make")
def m16(qs):
    q = find(qs, "S01-08")
    q["profile"]["approx"] = True


@mutant("profile.unknown_shape", "G4", "name a reasoning shape that does not exist")
def m17(qs):
    find(qs, "S01-14")["profile"]["shape"] = "vibes"


@mutant("profile.thin_insight", "G4", "cut the insight down to nothing")
def m18(qs):
    find(qs, "S01-22")["profile"]["insight"] = "it is just energy"


@mutant("profile.figure_claim_without_figure", "G4",
        "claim a load-bearing figure where the stem has none")
def m19(qs):
    q = find(qs, "S01-05")
    q["profile"]["figure_essential"] = True


@mutant("difficulty.band_contradicts_score", "G5",
        "declare a hard question easy, against its measured score")
def m20(qs):
    find(qs, "S01-14")["diff"] = 1


@mutant("difficulty.all_easy", "G5", "declare every question easy")
def m21(qs):
    for q in qs:
        q["diff"] = 1


@mutant("similarity.clone", "G6", "rebuild one question on another's logic")
def m22(qs):
    victim, donor = find(qs, "S01-23"), find(qs, "S01-14")
    victim["key"] = list(donor["key"])
    victim["profile"] = copy.deepcopy(donor["profile"])
    victim["rel"] = list(donor["rel"])
    victim["sol"] = donor["sol"]
    victim["check"] = copy.deepcopy(donor["check"])
    victim["ans"] = donor["ans"]
    victim["opts"] = list(donor["opts"])
    victim["distractors"] = list(donor["distractors"])
    victim["trap"] = donor["trap"]


@mutant("numerics.wrong_check", "G7", "make the independent check disagree")
def m23(qs):
    q = find(qs, "S01-20")
    q["check"] = {"kind": "eval", "expr": "floor(1.0e-3/500/(600e-9))", "want": "4"}


@mutant("numerics.missing_check", "G7", "remove the independent check")
def m24(qs):
    find(qs, "S01-21")["check"] = None


@mutant("numerics.unparseable_check", "G7", "write a check that cannot be parsed")
def m25(qs):
    find(qs, "S01-24")["check"] = {"kind": "eval", "expr": "this is not maths", "want": "3"}


@mutant("figures.missing_placeholder", "G8", "point the stem at a figure that does not exist")
def m26(qs):
    q = find(qs, "S01-10")
    q["stem"] = q["stem"].replace("{{FIG:s01-10}}", "{{FIG:s01-nope}}")


@mutant("figures.placeholder_left_unresolved", "G3", "leave a placeholder the expander misses")
def m27(qs):
    q = find(qs, "S01-15")
    q["stem"] = q["stem"] + "{{FIG}}"


@mutant("balance.all_one_letter", "G9", "make every answer the same letter")
def m28(qs):
    for q in qs:
        q["ans"] = 0
        q["distractors"] = ["correct"] + ["a distinct named error %d" % i for i in range(1, 5)]


@mutant("markup.unbalanced_tag", "G3", "leave a tag open")
def m29(qs):
    q = find(qs, "S01-06")
    q["sol"] = q["sol"] + "<p>and so the answer follows"


def main():
    base = G.baseline()
    print("mutation self-test: break one thing, check the right gate notices")
    print("%d mutants\n" % len(MUTANTS))
    missed = []
    for name, gate, desc, fn in MUTANTS:
        qs = copy.deepcopy(GOOD)
        try:
            fn(qs)
        except Exception as e:                      # a mutant that cannot even be built
            missed.append((name, gate, "mutation failed to apply: %s" % e))
            print("  %-42s %-3s  MUTATION ERROR: %s" % (name, gate, e))
            continue
        errs, _ = G.gate_section(1, base=base, verbose=False, questions=qs)
        hit = [e for e in errs if e.startswith(gate)]
        if hit:
            print("  %-42s %-3s  caught: %s" % (name, gate, hit[0][:78]))
        else:
            missed.append((name, gate, "gate did not fire"))
            print("  %-42s %-3s  *** MISSED ***  %s" % (name, gate, desc))
    print()
    if missed:
        print("FAILED: %d mutant(s) slipped through" % len(missed))
        for name, gate, why in missed:
            print("   %s (%s): %s" % (name, gate, why))
        return 1
    print("all %d mutants were caught -- every gate has been shown to fail" % len(MUTANTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
