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
import os
import re
import sys

import gates as G
import sec01

GOOD = [copy.deepcopy(q) for q in sec01.QUESTIONS]


def find(mutated, qid):
    return next(q for q in mutated if q["id"] == qid)


# The words that make the scorer's `approx` flag true, in the spellings the question
# source actually uses.  Both spellings of every entity are listed: `visible()` decodes
# entities before matching, so a raw `&asymp;` matches the "≈" pattern and the entity form
# is redundant -- but a replacement pass runs on the RAW source, where it is not.
APPROX_WORDS = ["≈", "≪", "for small", "small angle", "small parameter",
                "to first order", "first-order", "second order", "negligible",
                "approximately", "roughly", "order of magnitude", "power of ten",
                "estimation", "&asymp;", "&#8776;", "&#8810;", "&lt;&lt;"]


def strip_approx(q):
    """Remove every approximation cue from a question's stem and solution."""
    for w in APPROX_WORDS:
        q["sol"] = q["sol"].replace(w, "x")
        q["stem"] = q["stem"].replace(w, "x")
    q["profile"]["approx"] = False


def score_of(q, figdir=None, mids=None, errs=None):
    """Measure one question the way `gate_section` measures it.

    The score has to be read from the RENDERED text -- the figure placeholder expanded
    and the superscripts repaired -- because that is what the gate feeds the scorer.
    Scoring the raw source gives a different number, and the whole point of re-declaring
    `diff` in a mutant is to agree with the number the gate will compute.  A helper that
    measured the source would silently disagree with the thing it is trying to match.
    """
    figdir = figdir or os.path.join(G.HERE, "fig")
    mids = mids if mids is not None else set()
    errs = errs if errs is not None else []
    stem = G.expand_figs(G.supify(q["stem"]), figdir, mids, errs)
    opts = [G.expand_figs(G.supify(o), figdir, mids, errs) for o in q["opts"]]
    sol = G.expand_figs(G.supify(q["sol"]), figdir, mids, errs)
    return G.difficulty({"sol": sol, "q": stem, "opts": opts,
                         "trap": q.get("trap", ""), "rel": q.get("rel", [])})


# ── each mutant: (name, gate that must fire, what it breaks, mutate fn) ───────
MUTANTS = []


def mutant(name, gate, desc, must_not_fire=False):
    """Register a mutant.

    `must_not_fire=True` is for the INVERSE assertion, and it is not decoration.  Every
    other mutant here proves a gate fires when it should; none of them would have caught
    the duplicate-option check rejecting S02-19, where five genuinely different
    expressions were reported as duplicates because the check folded the case of the
    symbols.  A gate that fires when it should NOT is as broken as one that stays silent,
    and the only way to test that direction is to build content that is correct and
    assert the gate keeps quiet.
    """
    def deco(fn):
        MUTANTS.append((name, gate, desc, fn, must_not_fire))
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


@mutant("structure.duplicate_written_differently", "G1",
        "duplicate an option, writing it with entities instead of plain characters")
def m30(qs):
    # The duplicate check normalises entities, so this IS a duplicate and must be caught.
    # Without this mutant, the case-preserving rewrite of norm_opt could have been
    # "passed" by a check that had simply stopped normalising anything.
    q = find(qs, "S01-17")
    q["opts"][3] = q["opts"][0].replace(" x ", " &times; ").replace("10<sup>", "10 <sup>")


@mutant("structure.case_only_difference", "G1",
        "two options differing only in the case of a symbol, which is NOT a duplicate",
        must_not_fire=True)
def m31(qs):
    # In physics the case IS the symbol: k and K, m and M, r and R are different
    # quantities.  A candidate reads these two options as different expressions, so the
    # duplicate check must stay silent.  It did not, before norm_opt stopped lowercasing.
    q = find(qs, "S01-11")
    q["opts"][2] = "<code>v = k r</code>"
    q["opts"][3] = "<code>v = K r</code>"


# ── the checks added on 2026-09-19: the top end, the bottom end, the non-calculator
#    axes, and the two rules that stop a deep question being declared rather than built.
#
# The whole reason these mutants exist is the one the module docstring gives: a gate
# that has only ever seen content its own author wrote has proved nothing.  G5b, G5c
# and the floor were written in the same session as the questions that satisfy them,
# which is exactly the situation in which a broken check goes unnoticed.

@mutant("difficulty.no_deep_question", "G5",
        "flatten both long chains so nothing in the section has nine moves")
def m32(qs):
    # G5b's first clause.  Renumbering the step markers is enough: `moves` is read off
    # the highest "Step N" in the solution, so capping them at 6 shortens the chain the
    # metric sees.  The profile keeps its longer list, which the one-directional G4
    # check allows -- only an under-declared chain is an error.
    for qid in ("S01-12", "S01-16"):
        q = find(qs, qid)
        q["sol"] = re.sub(r"Step (\d+)",
                          lambda m: "Step %d" % min(int(m.group(1)), 6), q["sol"])


@mutant("difficulty.flat_ceiling", "G5",
        "leave the chains long but strip everything else that makes them hard")
def m33(qs):
    # G5b's second clause, on its own.  Both chains stay at ten moves, so the deep count
    # is still 2 and the first clause stays quiet; what falls is the CEILING, because the
    # score also pays for a symbolic answer, a figure, a named trap and the relations
    # drawn on.  Ten moves alone earn 16.0 + 4.0 + 1.2 = 21.2, under the 22.0 floor.
    for qid in ("S01-12", "S01-16"):
        q = find(qs, qid)
        q["opts"] = ["1", "2", "3", "4", "5"]
        q["stem"] = re.sub(r"\{\{FIG:[^}]+\}\}", "", q["stem"])
        q["profile"]["figure_essential"] = False
        q["profile"]["figure_support"] = False
        q["rel"] = [("A", "one relation only")]
        q["trap"] = "none"


@mutant("difficulty.no_noncalculator_axis", "G5",
        "remove every approximation and every symbolic answer")
def m34(qs):
    # G5c.  Round 0 is sat without a calculator, so `approx` and `symbolic` are the two
    # terms in the scorer that encode the skill the paper is actually for; the gate wants
    # at least six questions per section carrying one of them.
    #
    # Getting this mutant to prove G5c took three attempts, and the two failures are
    # worth keeping because each one proves something about how the gate suite is
    # ORDERED.  A mutant is only evidence about the gate whose message it actually
    # produces -- one caught by a neighbouring clause has demonstrated nothing:
    #
    #   * the first version stripped all twelve carriers.  Three of them left the top
    #     quartile on the way, and the suite printed
    #         caught: G5: only 5 questions reach the 2025 paper's top quartile (15.5)
    #   * the second stripped the twelve and kept their old `diff`.  Six of them changed
    #     band, and the suite printed
    #         caught: G5 S01-03: declared diff 3, but its measured score 14.8 puts it in
    #                            band 2
    #
    # The top-quartile check is reported before the band check, which is reported before
    # G5c, so both had to be made to pass for the third clause to be observable at all.
    # What finally works is the smallest mutation that can move the count:
    #
    #   * SIX questions carry `approx` (five approximation-only, one carrying both).
    #     Stripping the flag from all six leaves SEVEN carriers, not six: S01-09 carries
    #     both axes, so removing its approximation text leaves it a symbolic carrier and
    #     it still counts.  That was the third failure -- the suite printed `*** MISSED
    #     ***`, because seven carriers is one over the minimum and G5c stayed quiet.  The
    #     arithmetic of a mutation has to be done on the MEASURED flags, not on the list
    #     of question ids you thought you had retired.
    #   * TWO symbolic carriers therefore lose their symbolic options as well.  S01-14 is
    #     the one whose score stays in band 3 after the loss and S01-01 is one whose score
    #     stays in band 2, so neither moves the diff distribution.  They are mutated by
    #     REPLACING the options rather than by swapping a glyph: writing "E ÷ 2" for
    #     "E/2" would defeat the detector without changing the question, which tests the
    #     regex rather than the gate.
    #   * every stripped question then has its `diff` re-declared from a fresh
    #     measurement, so the band check agrees and the diff distribution stays legal
    #     (band 1: 2 of at most 5; band 3: 7 of at least 6).
    #
    # Result: five carriers, one under the minimum, and G5c is the finding.
    ref = G.baseline()["R0-2025"]
    figdir = os.path.join(G.HERE, "fig")
    approx_carriers = ("S01-06", "S01-09", "S01-11", "S01-15", "S01-18", "S01-25")
    for qid in approx_carriers:
        strip_approx(find(qs, qid))

    # the two symbolic carriers, stripped of their symbolic options
    sym_carriers = ("S01-01", "S01-14")
    for qid in sym_carriers:
        find(qs, qid)["opts"] = ["1", "2", "3", "4", "5"]

    # re-declare the band on every question that was touched, measured the same way
    # `gate_section` measures it -- same shared marker-id set, same processing order
    mids, errs = set(), []
    scores = {}
    for q in sorted(qs, key=lambda d: d["n"]):
        scores[q["id"]] = score_of(q, figdir, mids, errs)
    for qid in approx_carriers + sym_carriers:
        find(qs, qid)["diff"] = G.band_of(scores[qid], ref)


@mutant("difficulty.too_easy_floor", "G5",
        "leave one question with nothing in it at all")
def m35(qs):
    # The floor added on 2026-09-19.  The 2025 paper's easiest question scores 8.3; this
    # mutant produces an item that is a bare statement with no chain, no formula, no
    # figure and no trap, which is what a worksheet has and a competition does not.
    q = find(qs, "S01-01")
    q["sol"] = "<p>The answer follows from the definition.</p>"
    q["opts"] = ["1", "2", "3", "4", "5"]
    q["trap"] = "none"
    q["rel"] = [("A", "one relation only")]
    q["stem"] = re.sub(r"\{\{FIG:[^}]+\}\}", "", q["stem"])
    q["profile"]["figure_essential"] = False
    q["profile"]["figure_support"] = False
    q["profile"]["approx"] = False
    q["profile"]["symbolic"] = False
    q["profile"]["steps"] = [("relate", "read it off")]
    q["profile"]["relations"] = ["nothing to relate"]


@mutant("profile.deep_without_distinct_relations", "G4",
        "declare a long chain that names only three distinct relations")
def m36(qs):
    # The G4 rule that stops a deep question being PADDING: nine numbered steps on one
    # relation is nine steps of nothing.  Three distinct relations clears the ordinary
    # MIN_RELATIONS bar for diff 3 (which is 2), so only the deep rule can object.
    q = find(qs, "S01-16")
    q["profile"]["relations"] = ["relation one", "relation two", "relation three"]


@mutant("profile.deep_without_a_declared_chain", "G4",
        "walk a nine-move chain without numbering the steps, and declare only five")
def m37(qs):
    # The other half of the same G4 rule.  The steps have to be stripped as well as the
    # profile shortened, because with ten numbered markers the ordinary "profile declares
    # fewer steps than the solution walks" check would fire first and this mutant would
    # be proving that rule instead of this one.  With the markers gone, `moves` falls
    # back to the formula-block count -- which is the case the metric was built for, and
    # the only situation in which this clause can fire on its own.
    q = find(qs, "S01-16")
    q["sol"] = re.sub(r"Step \d+\s*\u2014\s*", "", q["sol"])
    while q["sol"].count('class="formula"') < 9:
        q["sol"] += '<div class="formula">padding relation</div>'
    q["profile"]["steps"] = q["profile"]["steps"][:5]



@mutant("difficulty.no_approximation_required", "G5",
        "answer every approximation with an exact formula")
def m38(qs):
    # The second clause of G5c, and the one that matters more.  The union can be satisfied
    # entirely with symbolic options, so a section can look non-calculator on paper while
    # never once asking for an approximation -- which is the shape the bank actually had
    # at the audit: 33% on the union, 10% on the approximation.
    #
    # The mutation replaces each approximation with an exact answer: the TEXT goes and the
    # options are left alone, so the questions stay symbolic and the union clause still
    # passes.  That is deliberate.  A mutant must produce the message it was written for,
    # and stripping the options as well would make the union clause fire first and prove
    # nothing about this one.
    #
    # Section 1's approximation floor is 1 (its legacy value, measured at 6), so taking
    # every carrier to zero is what it takes to fire the clause -- and the union survives
    # at 7 because the seven symbolic carriers are untouched.
    ref = G.baseline()["R0-2025"]
    figdir = os.path.join(G.HERE, "fig")
    carriers = ("S01-06", "S01-09", "S01-11", "S01-15", "S01-18", "S01-25")
    for qid in carriers:
        strip_approx(find(qs, qid))
    mids, errs = set(), []
    scores = {}
    for q in sorted(qs, key=lambda d: d["n"]):
        scores[q["id"]] = score_of(q, figdir, mids, errs)
    for qid in carriers:
        find(qs, qid)["diff"] = G.band_of(scores[qid], ref)


@mutant("difficulty.section_floor_is_read", "G5",
        "hold section 1 to a non-calculator floor it does not meet")
def m39(qs):
    # This one breaks the STANDARD rather than the content, and that is the point: the
    # floors now live on spec.SECTIONS, and a field nothing reads is worse than no field,
    # because it documents a rule that is not enforced.  The only way to show the plan is
    # consulted is to change the plan and watch the gate report the changed number.
    #
    # Section 1 carries 12 questions with an approximation or a symbolic answer.  Raising
    # its union floor to 13 -- one above what it has, and above the legacy 6 and the paper
    # 16 alike, so neither constant can be mistaken for the source of the message -- must
    # produce a G5c that says "at least 13 wanted".
    #
    # The approximation floor's own clause is proved by difficulty.no_approximation_required
    # above; both fields are read by the same expression, so this mutant covers the pair.
    G.spec.SECTIONS[0]["noncalc_min"] = 13


@mutant("numerics.symbolic_check_with_decimal", "G7",
        "write a symbolic check as a decimal and a fraction of the same quantity",
        must_not_fire=True)
def m40(qs):
    # S01-03's check is sqrt(r) against r**(1/2), both exact, so it never touched the
    # float path.  Rewriting it as 1.5*sqrt(r) against 3*sqrt(r)/2 puts a Float and a
    # free symbol in the same expression, which is exactly the shape that used to raise.
    # The two sides are equal, so the correct verdict is silence: a gate that reports an
    # error here is reporting its own inability to evaluate, not a fault in the content.
    find(qs, "S01-03")["check"] = {"kind": "sym",
                                   "got": "1.5*r**(1/2)", "want": "3*sqrt(r)/2"}


@mutant("numerics.symbolic_check_decimal_is_wrong", "G7",
        "same shape, but the decimal is six per cent out")
def m41(qs):
    # The partner to m40.  Without this, m40 would be satisfied by a branch that returns
    # True unconditionally, and the fix would have traded a false failure for a false
    # pass.  1.6 against 3/2 is out by 6.7 per cent -- four orders of magnitude above the
    # 1e-9 relative tolerance the comparison uses.
    find(qs, "S01-03")["check"] = {"kind": "sym",
                                   "got": "1.6*r**(1/2)", "want": "3*sqrt(r)/2"}


@mutant("scope.rc_charging_in_a_capacitor_question", "G11",
        "ask for an RC time constant, which the official scope note excludes")
def m42(qs):
    # The exact defect that shipped.  S05-21 asked for "the time constant of the circuit",
    # and the official Round 0 note says capacitors mean "not time dependent charging, but
    # a knowledge that Q = CV".  All ten gates of the day passed it, because none of them
    # knew what the paper is allowed to test.
    find(qs, "S01-17")["stem"] = ("<p>A capacitor is charged through a resistor from a "
                                  "supply. What is the time constant of the circuit?</p>")


@mutant("scope.recorded_judgement_is_honoured", "G11",
        "the same wording, with the in-scope justification written down",
        must_not_fire=True)
def m43(qs):
    # The partner to m42, and the reason G11 is allowed to be a crude keyword scan.  A
    # legitimate mention exists: S01-01 says a smooth pulley exerts "no frictional torque",
    # and the word torque is otherwise the signature of out-of-scope rotational dynamics.
    # The escape hatch has to be shown to work, or the gate would teach the author to avoid
    # a WORD rather than to think about a TOPIC.
    q = find(qs, "S01-17")
    q["stem"] = ("<p>A capacitor is charged through a resistor from a supply. What is the "
                 "time constant of the circuit?</p>")
    q["profile"]["scope_note"] = ("The RC wording is quoted only in order to say that this "
                                  "question does not use it; the answer needs Q = CV.")


@mutant("scope.marker_in_a_distractor_counts", "G11",
        "smuggle the out-of-scope idea into a wrong option instead of the stem")
def m44(qs):
    # The scan has to cover every field a candidate reads, not just the stem.  A distractor
    # is where an out-of-scope idea is most likely to survive review, because the author is
    # thinking about the error rather than about the syllabus.
    q = find(qs, "S01-17")
    q["distractors"][2] = ("uses the time constant of the circuit instead of the charge, "
                           "which is the RC answer to a different question")


def main():
    base = G.baseline()
    print("mutation self-test: break one thing, check the right gate notices")
    print("%d mutants\n" % len(MUTANTS))
    missed = []
    for name, gate, desc, fn, must_not in MUTANTS:
        qs = copy.deepcopy(GOOD)
        # The non-calculator floors live on spec.SECTIONS, so a mutant can change the
        # STANDARD as well as the content -- see difficulty.section_floor_is_read.  The
        # plan is therefore snapshotted and restored around every mutant.  Without this,
        # the first mutant that raised a floor would silently change the verdict of every
        # mutant after it, and the suite would report a chain of failures caused by a
        # mutation that had already been undone in every other sense.
        plan = copy.deepcopy(G.spec.SECTIONS)
        try:
            try:
                fn(qs)
            except Exception as e:                  # a mutant that cannot even be built
                missed.append((name, gate, "mutation failed to apply: %s" % e))
                print("  %-42s %-3s  MUTATION ERROR: %s" % (name, gate, e))
                continue
            # ... and the gate call has to be INSIDE the snapshot.  Restoring the plan
            # when the mutant returns puts the standard back before anything reads it,
            # which is exactly how the first version of section_floor_is_read came to
            # report MISSED: it was a mutation nobody ever saw.
            errs, _ = G.gate_section(1, base=base, verbose=False, questions=qs)
        finally:
            G.spec.SECTIONS[:] = plan
        hit = [e for e in errs if e.startswith(gate)]
        if must_not:
            if hit:
                missed.append((name, gate, "false positive: %s" % hit[0]))
                print("  %-42s %-3s  *** FALSE POSITIVE ***  %s"
                      % (name, gate, hit[0][:60]))
            else:
                print("  %-42s %-3s  correctly silent" % (name, gate))
        elif hit:
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
    print("all %d mutants behaved -- every gate has been shown to fail, and the "
          "false-positive guard has been shown to stay quiet" % len(MUTANTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
