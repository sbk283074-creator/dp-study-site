#!/usr/bin/env python3
"""Quality, length and format gate for the Challenge Bank (see STANDARD.md).

    python3 tools/validate.py                 # full report, exit 1 on any FAIL
    python3 tools/validate.py --subject "Math AA HL"
    python3 tools/validate.py --stats         # length distribution per subject

This is the auditor. A question that passes needs no separate read-through
before publishing; a question that fails must be fixed or dropped.

Hard floors are static constants, calibrated once against the published corpus
so that adding a thin question can never lower the bar. Soft targets are the
running per-subject median, so a batch that is technically compliant but
noticeably thinner than the rest of the bank still gets flagged.
"""

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SYLLABUS = json.loads((ROOT / "tools" / "syllabus.json").read_text(encoding="utf-8"))

SUBJECTS = {
    "Math AA HL": {"prefix": "MATH", "min_marks": 6, "min_parts": 3},
    "Physics HL": {"prefix": "PHYS", "min_marks": 6, "min_parts": 3},
    "Computer Science HL": {"prefix": "CS", "min_marks": 6, "min_parts": 2},
    "Business Management SL": {"prefix": "BM", "min_marks": 10, "min_parts": 3},
}

# Calibrated against the 20 published questions. These are the absolute floor:
# a new question may not be materially thinner than the thinnest existing one
# in the same subject.
MIN_WORDS = {
    "Math AA HL": {"answer": 190, "markscheme_notes": 125, "explanation": 195},
    "Physics HL": {"answer": 155, "markscheme_notes": 125, "explanation": 205},
    "Computer Science HL": {"answer": 440, "markscheme_notes": 125, "explanation": 200},
    "Business Management SL": {"answer": 345, "markscheme_notes": 155, "explanation": 220},
}
MEDIAN_FRACTION = 0.80          # warn below 80% of the running subject median
# Everything the student reads: stem + stimulus + part texts. The floor is
# per-subject because a terse maths question is normal while a thin Business
# Management stimulus is not.
MIN_CONTEXT = {"Math AA HL": 30, "Physics HL": 100,
               "Computer Science HL": 140, "Business Management SL": 160}

REQUIRED = ["id", "subject", "level", "syllabus_ref", "topic", "subtopic", "paper", "marks",
            "difficulty", "challenge_mechanism", "command_terms", "question", "parts",
            "answer", "markscheme_notes", "explanation", "provenance", "originality",
            "verification", "status", "created_at"]

# ---------------------------------------------------------------------------
# Question type: which paper carries which kinds of question, and what each
# kind must look like. Added 2026-09-11 once topic coverage hit 100%: the live
# gap is paper and question type, not syllabus bullet.
#
# Legacy items carry no `question_type`. Those are left completely alone, so an
# item only enters these rules when it declares a type.
# ---------------------------------------------------------------------------
QUESTION_TYPES = {"mcq", "data_based", "structured", "extended_response",
                  "case_study", "problem_solving"}

# (subject, paper) -> the types that paper actually contains.
PAPER_TYPES = {
    ("Physics HL", "P1"): {"mcq", "data_based"},
    ("Physics HL", "P2"): {"structured", "extended_response"},
    ("Math AA HL", "P1"): {"structured", "extended_response"},
    ("Math AA HL", "P2"): {"structured", "extended_response"},
    ("Math AA HL", "P3"): {"problem_solving"},
    ("Computer Science HL", "P1"): {"structured", "extended_response"},
    ("Computer Science HL", "P2"): {"case_study"},
    ("Business Management SL", "P1"): {"case_study"},
    ("Business Management SL", "P2"): {"structured", "extended_response", "data_based"},
}

# Per-type overrides. Anything not listed falls back to the subject rule.
# MCQ floors scale with the size of the cluster: an MCQ cluster has to give a
# real route to every key, not just "B".
TYPE_RULES = {
    "mcq": {"min_marks": 1, "min_parts": 1, "per_part_answer": 45,
            "base_notes": 80, "per_part_notes": 15,
            "base_expl": 110, "per_part_expl": 15,
            "per_part_context": 35, "min_context": 40},
    "data_based": {"min_marks": 8, "min_parts": 4},
    "problem_solving": {"min_marks": 12, "min_parts": 3},
    "case_study": {"min_marks": 10, "min_parts": 3},
}

# A data-based question is not a data-based question without data, and not
# without at least one part on uncertainty, graphing or experimental critique.
DATA_BASED_TERMS = {"state", "describe", "suggest", "evaluate", "determine", "calculate",
                    "plot", "draw", "estimate", "justify", "comment", "explain"}
DATA_BASED_EVIDENCE = ("uncertainty", "error bar", "resolution", "best-fit", "gradient",
                       "intercept", "anomal", "linearis", "lineariz", "scatter",
                       "significant figure", "random error", "systematic")

# Recognised IB command terms. Anything outside this list is flagged: an
# invented command term is a question that does not know what it is asking for.
COMMAND_TERMS = {
    "analyse", "annotate", "apply", "calculate", "comment", "compare",
    "compare and contrast", "complete", "construct", "contrast", "deduce", "define",
    "demonstrate", "derive", "describe", "design", "determine", "discuss", "distinguish",
    "draw", "estimate", "evaluate", "examine", "explain", "explore", "find", "formulate",
    "hence", "identify", "interpret", "investigate", "justify", "label", "list", "measure",
    "outline", "plot", "predict", "present", "prove", "quantify", "recall", "recognise",
    "show", "show that", "sketch", "solve", "state", "suggest", "summarise", "synthesise",
    "to what extent", "use", "write down", "copy and complete", "recommend",
}
# A recall term carrying many marks, or an evaluative term carrying one, usually
# means the marks and the demand have not been thought through together.
LOW_TERM_MAX_MARKS = {"state": 3, "list": 3, "define": 2, "label": 2, "identify": 3,
                      "write down": 2, "recall": 2, "recognise": 2, "complete": 3,
                      "copy and complete": 3}
HIGH_TERM_MIN_MARKS = {"explain": 2, "analyse": 2, "compare": 2, "contrast": 2,
                       "compare and contrast": 2, "discuss": 2, "evaluate": 3, "examine": 2,
                       "justify": 2, "to what extent": 3, "assess": 3, "derive": 2,
                       "prove": 2, "show that": 2, "comment": 2, "suggest": 2}
BM_EVALUATIVE = {"analyse", "evaluate", "discuss", "justify", "to what extent", "examine",
                 "assess", "compare", "recommend"}

VAGUE_MECHANISM = {"multi-step", "multi step", "challenging", "hard", "difficult", "complex",
                   "long", "synthesis", "application", "requires thinking", "advanced",
                   "synoptic", "demanding"}

# ---------------------------------------------------------------------------
# Difficulty evidence (introduced 2026-09-13, STANDARD.md 2.2-2.5).
#
# Until this point `difficulty` was a self-declared 3/4/5 backed by nothing but
# a >=10-word string -- a check that a claim had been *typed*, not that it was
# *true*. Measured on introduction: 46% of the bank (79/172) claimed difficulty
# 5, Physics HL claimed 62%, no item claimed 3, and not one item carried any
# evidence. These rules make the label something an item has to earn.
# ---------------------------------------------------------------------------
LEVER_TYPES = {
    "implicit_dependence", "variable_swap", "exceptional_parameter",
    "decoy_technique", "binding_constraint", "partial_cancellation",
    "non_governing_variable", "derived_limit", "aggregate_recovery",
    "wrong_design_cost", "quant_vs_judgement", "non_obvious_tool",
    "seeded_anomaly",
}
SOURCE_FAMILIES = {
    "original", "ib", "china-gaokao", "china-qiangji", "china-competition",
    "uk-alevel", "uk-further-maths", "us-ap", "singapore-alevel", "other",
}
# The closed `topic` vocabulary, per subject. Names follow the guide each subject
# is pinned to (see SUBJECTS in build.py). The Computer Science entries are the
# two themes of the 2027 guide; A1 "Computer Fundamentals" and B2 "Programming"
# are strands *within* those themes, not themes themselves.
TOPICS = {
    "Math AA HL": {
        "Topic 1: Number and algebra",
        "Topic 2: Functions",
        "Topic 3: Geometry and trigonometry",
        "Topic 4: Statistics and probability",
        "Topic 5: Calculus",
    },
    "Physics HL": {
        "Theme A: Space, time and motion",
        "Theme B: The particulate nature of matter",
        "Theme C: Wave behaviour",
        "Theme D: Fields",
        "Theme E: Nuclear and quantum physics",
    },
    "Computer Science HL": {
        "Theme A: Concepts of computer science",
        "Theme B: Computational thinking and problem-solving",
    },
    "Business Management SL": {
        "Unit 1: Introduction to business management",
        "Unit 2: Human resource management",
        "Unit 3: Finance and accounts",
        "Unit 4: Marketing",
        "Unit 5: Operations management",
        "Unit 6: The SL Toolkit",
    },
}
# The rubric of STANDARD.md 2.3, as a table: label -> the score it needs.
# The maximum is 9, not 10: the mark-distribution test that used to carry the
# tenth point was withdrawn (see the note in difficulty_score), so the same
# thresholds are now a slightly larger fraction of what is attainable. That is
# the correct direction -- the withdrawn test could be passed without evidence.
DIFFICULTY_MIN_SCORE = {3: 4, 4: 6, 5: 8}
DIFFICULTY_MAX_SCORE = 9
# Assertions per mark. The bank median is 0.62, so 0.5 is a real discriminator
# rather than a formality: it separates items whose numbers were machine-checked
# in proportion to the marks on offer from those where they were not.
ASSERTION_DENSITY = 0.5
# Two evidence fields this similar are one statement written twice.
PARAPHRASE_LIMIT = 0.60
EVIDENCE_MIN_WORDS = 8
# The date the difficulty standard took force (STANDARD.md 2.2-2.5, 4.7). Items
# written before it are grandfathered: their label is unbacked and they warn.
# Items written from this date onwards must carry difficulty_evidence, or they
# fail -- otherwise "no new batch may add to the backlog" is a slogan rather
# than a rule. All 172 items in the bank carry created_at, and the 164
# grandfathered ones are dated 2026-09-10 and 2026-09-11.
STANDARD_EFFECTIVE = "2026-09-13"
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "so", "as", "of", "to", "in",
    "on", "at", "by", "for", "with", "from", "into", "is", "are", "was", "were", "be", "been",
    "it", "its", "this", "that", "these", "those", "there", "here", "not", "no", "do", "does",
    "did", "can", "cannot", "will", "would", "must", "should", "may", "might", "you", "your",
    "they", "their", "them", "we", "our", "he", "she", "his", "her", "one", "two", "both",
    "which", "what", "when", "where", "why", "how", "all", "any", "each", "every", "some",
    "more", "most", "less", "least", "other", "same", "such", "only", "also", "very", "just",
    "because", "instead", "however", "therefore", "thus", "hence", "about", "after", "before",
}

MARK_ANNOTATION = re.compile(r"\(\s*(?:M|A|R|C)\d+\s*\)|\(\s*AG\s*\)")
ENTITY = re.compile(r"&[a-zA-Z]{2,10};|&#\d{1,5};")
CODE_PATTERNS = {
    "Math AA HL": re.compile(r"\b(?:SL|AHL)\s*(\d+\.\d+)\b"),
    "Physics HL": re.compile(r"\b([A-E]\.\d)\b"),
    "Computer Science HL": re.compile(r"\b([AB][1-4]\.\d+)\b"),
    "Business Management SL": re.compile(r"\b([1-6]\.\d+)\b"),
}


def words(s):
    if not s:
        return 0
    t = re.sub(r"\\[a-zA-Z]+", " ", str(s))
    t = re.sub(r"[${}\\]", " ", t)
    return len(t.split())


def stimulus_text(q):
    stim = q.get("stimulus")
    if isinstance(stim, str):
        return stim
    if isinstance(stim, dict):
        return " ".join(str(stim.get(k, "")) for k in ("title", "body")) + \
               " ".join(str(stim.get("table", "")))
    return ""


def normalise_term(term):
    return " ".join(str(term or "").lower().split())


def _toks(s):
    """Content words only, so two statements that say the same thing in
    different grammar land on the same token set."""
    return {w for w in re.findall(r"[a-z0-9.]+", str(s).lower()) if w not in STOPWORDS}


def _overlap(a, b):
    """Jaccard over content words; 0.0 when either side is empty."""
    a, b = _toks(a), _toks(b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def difficulty_score(q):
    """Score an item out of DIFFICULTY_MAX_SCORE (STANDARD.md 2.3).

    Returns (score, breakdown, notes, info). `notes` are defects that surface as
    warnings and therefore fail a --strict run; `info` is observation for the
    audit report only, because a --strict batch must not fail on a hint.
    """
    br, notes, info = {}, [], []
    ev = q.get("difficulty_evidence") or {}
    np_ = str(ev.get("naive_path") or "").strip()
    fp = str(ev.get("failure_point") or "").strip()
    wa = str(ev.get("wrong_answer") or "").strip()
    parts = q.get("parts") or []
    marks = q.get("marks") or 0

    # 1 -- the trap is located, and is not the path written twice.
    if words(fp) >= EVIDENCE_MIN_WORDS and _overlap(fp, np_) < PARAPHRASE_LIMIT:
        br["failure_point"] = 2
    else:
        br["failure_point"] = 0
        if not fp:
            notes.append("no failure_point")
        elif words(fp) < EVIDENCE_MIN_WORDS:
            notes.append("failure_point under %d words" % EVIDENCE_MIN_WORDS)
        else:
            notes.append("failure_point restates naive_path")

    # 2 -- the trap has a stated outcome, and it is a third distinct statement
    #      rather than the path or the failure written again.
    #
    #      An earlier version of this test FAILED any item whose wrong_answer
    #      reused a number from the answer. That was unsound and was caught by
    #      the first batch of real evidence: PHYS-A.1-102 is a 5-mark MCQ
    #      cluster whose distractors are all readings of the same graph, so its
    #      trap values (0, 70.5, 73.5 m s^-1 and m) are necessarily also
    #      intermediates inside a 400-word worked answer. A check that fires on
    #      correct work is worse than no check. The overlap is now a warning to
    #      confirm by hand.
    if not wa:
        br["wrong_answer"] = 0
        notes.append("no wrong_answer")
    elif words(wa) < EVIDENCE_MIN_WORDS:
        br["wrong_answer"] = 0
        notes.append("wrong_answer under %d words" % EVIDENCE_MIN_WORDS)
    elif _overlap(wa, np_) >= PARAPHRASE_LIMIT or _overlap(wa, fp) >= PARAPHRASE_LIMIT:
        br["wrong_answer"] = 0
        notes.append("wrong_answer restates naive_path or failure_point")
    else:
        br["wrong_answer"] = 2
        nums = NUMBER.findall(wa)
        ans_nums = set(NUMBER.findall(str(q.get("answer") or "")))
        if nums and all(n in ans_nums for n in nums):
            info.append("every number in wrong_answer also appears in the answer -- "
                        "worth confirming by hand that the trap does not actually yield "
                        "the right result")

    # 3 -- the claim names an actual first move.
    if words(np_) >= EVIDENCE_MIN_WORDS:
        br["naive_path"] = 2
    else:
        br["naive_path"] = 0
        notes.append("naive_path missing or under %d words" % EVIDENCE_MIN_WORDS)

    # 4 -- structure. "Long lead-in, trivial finish" is the commonest way a
    #      question is easier than it reads; only 10 of the 172 pre-standard
    #      items have a strictly heaviest first part, so this test bites.
    if len(parts) >= 2:
        first = parts[0].get("marks") or 0
        rest = max((p.get("marks") or 0) for p in parts[1:])
        if first > rest:
            br["arc"] = 0
            notes.append("the first part is the heaviest -- no arc")
        else:
            br["arc"] = 2
    else:
        br["arc"] = 0
        notes.append("fewer than two parts, so no arc to judge")

    # 5 -- WITHDRAWN from scoring. This test used to require the final part to
    #      carry at least its equal share of the marks, and it was worth one
    #      point. It was withdrawn after it fired on the first eight items to
    #      carry real evidence: MATH-AHL4.9-101, CS-A2.2-101 and CS-B4.1-101
    #      all end on 3 marks against an average of 3.2 to 3.4, and in every
    #      one of them the short final part is the conceptual climax -- the
    #      hash-table judgement, the "looks like a simplification and is not"
    #      redesign, the "judge the model rather than use it" question.
    #
    #      The test measured mark distribution, not difficulty, and it measured
    #      it anti-correlated: across the bank it flags 20% of the difficulty-5
    #      items against 9% of the difficulty-4 items, so keeping it would have
    #      systematically penalised the hardest work. The mark-shape signal is
    #      real and is reported, but a --strict batch must not fail on it, so it
    #      goes to `info`. Test 4 already catches the anti-pattern that matters
    #      (a heavy first part).
    if parts:
        last = parts[-1].get("marks") or 0
        share = sum((p.get("marks") or 0) for p in parts) / len(parts)
        if last < share:
            info.append("the final part is lighter than an average part "
                        "(%.1f vs %.1f marks) -- a shape note, not a difficulty "
                        "finding" % (last, share))

    # 6 -- verification density.
    n_assert = len((q.get("verification") or {}).get("assertions") or [])
    if marks and n_assert / marks >= ASSERTION_DENSITY:
        br["assertions"] = 1
    else:
        br["assertions"] = 0
        notes.append("assertions per mark %.2f < %.2f"
                     % ((n_assert / marks) if marks else 0.0, ASSERTION_DENSITY))

    return sum(br.values()), br, notes, info


def max_label_for(score):
    """The highest `difficulty` the rubric permits at this score (None if the
    evidence does not reach even difficulty 3)."""
    best = None
    for label in sorted(DIFFICULTY_MIN_SCORE):
        if score >= DIFFICULTY_MIN_SCORE[label]:
            best = label
    return best


def check_difficulty(q, fail, warn):
    """The label must be earned. Absent evidence on an item written before the
    standard is grandfathered as a warning -- the backlog belongs to
    tools/difficulty_audit.py -- but an item written from STANDARD_EFFECTIVE
    onwards must carry it, and evidence that is present but does not support
    the label is a failure whatever the date."""
    ev = q.get("difficulty_evidence")
    label = q.get("difficulty")
    if not isinstance(ev, dict) or not ev:
        created = str(q.get("created_at") or "")[:10]
        if created >= STANDARD_EFFECTIVE:
            fail.append("no difficulty_evidence, and this item was created %s -- the "
                        "standard has been in force since %s, so it may not ship "
                        "(STANDARD.md 4.7)" % (created, STANDARD_EFFECTIVE))
        else:
            warn.append("no difficulty_evidence (pre-standard item, created %s; "
                        "difficulty %r is unbacked -- see tools/difficulty_audit.py)"
                        % (created or "unknown", label))
        return
    lt = str(ev.get("lever_type") or "").strip()
    if lt not in LEVER_TYPES:
        fail.append("difficulty_evidence.lever_type %r is not in the taxonomy" % lt)
    for k in ("naive_path", "failure_point", "wrong_answer"):
        if not str(ev.get(k) or "").strip():
            fail.append("difficulty_evidence.%s is empty" % k)
    score, br, notes, _info = difficulty_score(q)
    allowed = max_label_for(score)
    # A claim of difficulty 4 or more is a claim that the item defeats a
    # prepared student, and that claim is only complete if all three evidence
    # fields do their own job: the path, the break, and the outcome it yields.
    # A rubric that merely sums to a threshold lets one hollow field be
    # absorbed by the others -- a verbatim restatement of naive_path still
    # scored 7 of 9, which permitted difficulty 4. That is how a label becomes
    # a slogan again, so completeness is a floor of its own, not a summand.
    if isinstance(label, int) and label >= 4:
        hollow = [k for k in ("naive_path", "failure_point", "wrong_answer")
                  if br.get(k) != 2]
        if hollow:
            fail.append("difficulty %d requires all three evidence fields to be "
                        "substantive and mutually distinct; hollow: %s"
                        % (label, ", ".join(hollow)))
    if allowed is None:
        fail.append("difficulty_evidence scores %d/%d, below the floor for any label"
                    % (score, DIFFICULTY_MAX_SCORE))
    elif isinstance(label, int) and label > allowed:
        fail.append("difficulty %d is not earned: the evidence scores %d/%d, which permits at most %d"
                    % (label, score, DIFFICULTY_MAX_SCORE, allowed))
    for n in notes:
        warn.append("difficulty_evidence: " + n)


def check_topic(q, fail, warn):
    """The `topic` label must come from the closed vocabulary for its subject.

    Every item carries a `topic`, and it is the label a learner filters by, so a
    near-miss label silently splits one topic into two and makes the filter lie.
    That is not hypothetical: before this check existed the bank used three
    different labels for Computer Science Theme A ("Concepts of computer
    science", "Computer fundamentals", "Systems in organisations") and two for
    Theme B, and two for BM Unit 3 ("Unit 3:" and "Topic 3:"). The theme names
    below are taken from the guides the bank is pinned to -- for Computer
    Science, the 2027 guide, which defines exactly two themes and places
    "Computer Fundamentals" (A1) and "Programming" (B2) *inside* them as
    strands. See tools/normalise_topics.py for the migration that fixed the
    labels that had drifted.
    """
    subj = q.get("subject", "")
    topic = q.get("topic")
    allowed = TOPICS.get(subj)
    if not topic:
        fail.append("no topic label")
        return
    if allowed is None:
        warn.append("no topic vocabulary defined for subject %r" % subj)
        return
    if topic not in allowed:
        near = sorted(allowed, key=lambda t: -_overlap(t, topic))[0] if allowed else ""
        fail.append("topic %r is not in the vocabulary for %s (did you mean %r?)"
                    % (topic, subj, near))


def check_sourcing(q, fail, warn):
    """Sourcing must be recorded, and a non-original claim must name its
    origin -- otherwise "we draw on other syllabuses" is untestable."""
    prov = q.get("provenance") or {}
    fam = prov.get("source_family")
    if fam is None or not str(fam).strip():
        warn.append("provenance.source_family missing (pre-standard item)")
        return
    fam = str(fam).strip()
    if fam not in SOURCE_FAMILIES:
        fail.append("provenance.source_family %r is not in the list" % fam)
    elif fam != "original" and not str(prov.get("resource_origin") or "").strip():
        fail.append("source_family %r with no provenance.resource_origin naming the source" % fam)


def check(q, seen_ids, medians):
    fail, warn = [], []
    qid = q.get("id", "?")
    subj = q.get("subject", "")
    rule = SUBJECTS.get(subj, {"prefix": "?", "min_marks": 6, "min_parts": 3})

    for k in REQUIRED:
        if not q.get(k):
            fail.append("missing %s" % k)
    if qid in seen_ids:
        fail.append("duplicate id")
    seen_ids.add(qid)

    if subj not in SUBJECTS:
        fail.append("unknown subject %r" % subj)

    # id prefix
    prefix = rule["prefix"]
    if not str(qid).startswith(prefix + "-") and not str(qid).startswith(prefix):
        warn.append("id does not start with %s-" % prefix)

    marks = q.get("marks", 0) or 0
    parts = q.get("parts") or []
    # Type-aware floors. A question that declares no type is a legacy item and
    # keeps the plain subject floor.
    qtype = q.get("question_type")
    trule = TYPE_RULES.get(qtype, {}) if qtype else {}
    min_marks = trule.get("min_marks", rule["min_marks"])
    min_parts = trule.get("min_parts", rule["min_parts"])
    nparts = max(1, len(parts))

    if marks < min_marks:
        fail.append("marks %s < floor %s" % (marks, min_marks))
    if subj == "Math AA HL" and q.get("paper") == "P3" and marks < 12:
        fail.append("P3 maths item under 12 marks")

    if len(parts) < min_parts:
        fail.append("%d parts < %d required" % (len(parts), min_parts))
    psum = sum(p.get("marks", 0) or 0 for p in parts)
    if parts and psum != marks:
        fail.append("part marks sum %d != marks %d" % (psum, marks))
    for p in parts:
        label = p.get("label", "?")
        if not p.get("label"):
            fail.append("part without label")
        if not p.get("command_term"):
            warn.append("part (%s) has no command term" % label)
        if words(p.get("text")) < 8:
            warn.append("part (%s) very short" % label)

    if q.get("difficulty") not in (3, 4, 5):
        fail.append("difficulty %r not in 3-5" % q.get("difficulty"))

    # ---- difficulty must be earned, and sourcing must be recorded ---------
    check_difficulty(q, fail, warn)
    check_topic(q, fail, warn)
    check_sourcing(q, fail, warn)

    # ---- length contract -------------------------------------------------
    # MCQ clusters are judged per MCQ, not against a 15-mark extended response.
    if qtype == "mcq":
        floors = {
            "answer": trule["per_part_answer"] * nparts,
            "markscheme_notes": trule["base_notes"] + trule["per_part_notes"] * nparts,
            "explanation": trule["base_expl"] + trule["per_part_expl"] * nparts,
        }
        use_median = False
    else:
        floors = MIN_WORDS.get(subj, {})
        use_median = True

    for field, floor in floors.items():
        n = words(q.get(field))
        if n < floor:
            fail.append("%s %d words < %d" % (field, n, floor))
        elif use_median:
            med = (medians.get(subj) or {}).get(field)
            if med and n < med * MEDIAN_FRACTION:
                warn.append("%s %d words < %.0f%% of subject median (%d)"
                            % (field, n, MEDIAN_FRACTION * 100, med))

    # Context is everything the student actually reads: the stem, the stimulus
    # and the part texts. A short stem is fine when the parts carry the detail,
    # which is the normal shape for maths and physics.
    context = (words(q.get("question")) + words(stimulus_text(q))
               + sum(words(p.get("text")) for p in parts))
    if qtype == "mcq":
        floor_ctx = max(trule["min_context"], trule["per_part_context"] * nparts)
    else:
        floor_ctx = MIN_CONTEXT.get(subj, 60)
    if context < floor_ctx:
        fail.append("total context %d words < %d" % (context, floor_ctx))

    # ---- question type ---------------------------------------------------
    # Only items that declare a type are checked here; the 114 legacy items
    # predate the field and are deliberately left untouched.
    if qtype is not None:
        if qtype not in QUESTION_TYPES:
            fail.append("unknown question_type %r" % qtype)
        else:
            allowed = PAPER_TYPES.get((subj, q.get("paper")))
            if allowed and qtype not in allowed:
                fail.append("%s on %s %s: that paper contains %s"
                            % (qtype, subj, q.get("paper"), "/".join(sorted(allowed))))

        if qtype == "mcq":
            for p in parts:
                lab = p.get("label", "?")
                opts = p.get("options") or []
                if len(opts) != 4:
                    fail.append("part (%s): MCQ needs exactly 4 options, has %d"
                                % (lab, len(opts)))
                labels = [str(o.get("label", "")) for o in opts]
                if labels != ["A", "B", "C", "D"]:
                    fail.append("part (%s): option labels must be A,B,C,D not %s"
                                % (lab, ",".join(labels) or "none"))
                ncorrect = sum(1 for o in opts if o.get("correct"))
                if ncorrect != 1:
                    fail.append("part (%s): %d options marked correct, need exactly 1"
                                % (lab, ncorrect))
                for o in opts:
                    # Reject a genuinely blank option only. A bare number is a
                    # perfectly good MCQ option ("A. 1.33"), and `words()`
                    # would strip the LaTeX from "1.71 $\Omega$" and leave one
                    # token, so neither count is the right test here.
                    if not str(o.get("text") or "").strip():
                        fail.append("part (%s) option %s: empty text"
                                    % (lab, o.get("label", "?")))
                    # A distractor with no stated purpose is not a distractor,
                    # it is noise. This is what makes an MCQ hard rather than
                    # merely guessable.
                    if words(o.get("rationale")) < 8:
                        fail.append("part (%s) option %s: rationale under 8 words"
                                    % (lab, o.get("label", "?")))
                if (p.get("marks") or 0) != 1:
                    fail.append("part (%s): MCQ worth %s mark(s), must be 1"
                                % (lab, p.get("marks")))

        if qtype == "data_based":
            stim = q.get("stimulus")
            has_data = isinstance(stim, dict) and bool(stim.get("table"))
            has_fig = isinstance(q.get("figure"), dict)
            if not (has_data or has_fig):
                fail.append("data_based item with no data table and no figure")
            blob = " ".join(str(x) for x in (
                q.get("question", ""), stimulus_text(q), q.get("answer", ""),
                " ".join(p.get("text", "") for p in parts))).lower()
            if not any(e in blob for e in DATA_BASED_EVIDENCE):
                fail.append("data_based item with no uncertainty/graph/anomaly language")
            if not any(e in blob for e in ("uncertainty", "error bar", "resolution")):
                warn.append("data_based item never mentions uncertainty")

        # ---- solution skeleton (drives the approach-level similarity gate) --
        skel = (q.get("verification") or {}).get("solution_skeleton")
        if not isinstance(skel, list) or not skel:
            fail.append("no verification.solution_skeleton (required once question_type is set)")
        else:
            if not (3 <= len(skel) <= 6):
                fail.append("solution_skeleton has %d steps, need 3-6" % len(skel))
            for i, s in enumerate(skel):
                if words(s) < 3:
                    fail.append("solution_skeleton step %d too vague: %r" % (i + 1, s))
            if len(set(" ".join(str(s).lower().split()) for s in skel)) < len(skel):
                fail.append("solution_skeleton has duplicate steps")

    # ---- command terms ---------------------------------------------------
    terms = [normalise_term(t) for t in (q.get("command_terms") or [])]
    terms += [normalise_term(p.get("command_term")) for p in parts]
    terms = [t for t in terms if t]
    for t in terms:
        base = t.split("(")[0].strip()
        if base not in COMMAND_TERMS and t not in COMMAND_TERMS:
            warn.append("unrecognised command term %r" % t)
    for p in parts:
        t = normalise_term(p.get("command_term")).split("(")[0].strip()
        m = p.get("marks") or 0
        if t in LOW_TERM_MAX_MARKS and m > LOW_TERM_MAX_MARKS[t]:
            warn.append("part (%s): '%s' worth %d marks" % (p.get("label"), t, m))
        if t in HIGH_TERM_MIN_MARKS and m < HIGH_TERM_MIN_MARKS[t]:
            warn.append("part (%s): '%s' worth only %d mark(s)" % (p.get("label"), t, m))
    if subj == "Business Management SL" and not (set(terms) & BM_EVALUATIVE):
        warn.append("no AO3/AO4 command term (analyse/evaluate/discuss/justify...)")

    # ---- syllabus reference ---------------------------------------------
    nodes = SYLLABUS["subjects"].get(subj, {}).get("nodes", {})
    pat = CODE_PATTERNS.get(subj)
    haystack = " ".join(str(q.get(k, "")) for k in ("syllabus_ref", "subtopic", "topic"))
    codes = sorted(set(pat.findall(haystack))) if pat else []
    if not codes:
        warn.append("no syllabus code found in syllabus_ref/subtopic")
    for c in codes:
        if c not in nodes:
            fail.append("syllabus code %s not in the %s map" % (c, subj))
    # The field itself must yield a recognised code. Checking the haystack alone
    # is not enough: a malformed ref such as "Z.9" never matches the subject
    # pattern, so it is silently skipped and the item passes on whatever code
    # `topic` happens to carry. Kept separate from the loop above so a malformed
    # ref and an out-of-map code stay distinguishable in the report.
    ref = str(q.get("syllabus_ref", "") or "").strip()
    if pat and ref and not pat.findall(ref):
        fail.append("syllabus_ref %r yields no %s syllabus code" % (ref, subj))
    if subj == "Business Management SL":
        hl_only = SYLLABUS["subjects"][subj].get("hl_only", {})
        for c in codes:
            if c in hl_only:
                fail.append("HL-only BM content %s (%s)" % (c, hl_only[c]))
        # Scan only student-visible prose. syllabus_ref/topic/subtopic are
        # authoring notes and legitimately name HL-only tools in order to rule
        # them out ("force field analysis is HL, so use SWOT here").
        visible = " ".join(str(x) for x in (
            q.get("question", ""), q.get("answer", ""), q.get("markscheme_notes", ""),
            q.get("explanation", ""), q.get("challenge_mechanism", ""),
            stimulus_text(q), " ".join(p.get("text", "") for p in q.get("parts", [])),
        ))
        low = visible.lower()
        for tool in SYLLABUS["subjects"][subj].get("hl_only_tools", []):
            if tool in low and "hl" not in low.split(tool)[0][-40:]:
                warn.append("possible HL-only toolkit tool: '%s'" % tool)

    # ---- the answer must actually be a markscheme ------------------------
    # MCQ keys are one mark each and carry no method marks, so the annotation
    # discipline does not apply; the per-option rationale is the markscheme.
    if subj in ("Math AA HL", "Physics HL") and qtype != "mcq":
        n_ann = len(MARK_ANNOTATION.findall(q.get("answer", "") or ""))
        if n_ann == 0:
            fail.append("answer has no IB mark annotations ((M1)(A1)(R1)(AG))")
        elif parts and n_ann < len(parts):
            warn.append("only %d mark annotations for %d parts" % (n_ann, len(parts)))
        elif n_ann < marks / 3:
            warn.append("%d mark annotations for %d marks" % (n_ann, marks))

    # ---- challenge mechanism --------------------------------------------
    mech = (q.get("challenge_mechanism") or "").strip()
    if len(mech.split()) < 10:
        fail.append("challenge_mechanism too short to name a mechanism")
    elif any(v in mech.lower() for v in VAGUE_MECHANISM) and len(mech.split()) < 20:
        warn.append("challenge_mechanism may be vague")

    # ---- markup hygiene --------------------------------------------------
    blob = " ".join(str(q.get(k, "")) for k in
                    ("question", "answer", "markscheme_notes", "explanation"))
    if subj in ("Math AA HL", "Physics HL") and blob.count("$") % 2:
        fail.append("unpaired $ in maths")
    if ENTITY.search(blob):
        fail.append("HTML entity present (use literal characters)")
    if "<script" in blob.lower():
        fail.append("script tag in content")

    # `blob` covers the prose fields only. Figures and stimuli are markup too, and
    # an HTML entity inside a figure SVG renders inconsistently in exactly the
    # same way -- but fix_json.py decodes it at the start of every pipeline run,
    # so the hole never surfaced as a failure; it surfaced as an unexplained diff
    # in a file nobody had edited. Checked separately from `blob` so that the
    # unpaired-$ test above is not applied to SVG coordinates.
    extras = []
    fig = q.get("figure")
    if isinstance(fig, dict):
        extras += [str(fig.get(k) or "") for k in ("content", "caption")]
    st = q.get("stimulus")
    if isinstance(st, dict):
        extras += [str(st.get(k) or "") for k in ("body", "title", "table")]
    elif isinstance(st, str):
        extras.append(st)
    markup = " ".join(extras)
    if ENTITY.search(markup):
        fail.append("HTML entity present in figure/stimulus (use literal characters)")
    if "<script" in markup.lower():
        fail.append("script tag in figure/stimulus")
    # A figure must be hand-authored vector markup. The IBO presents questions
    # "in the form of words, symbols, diagrams or tables"; a charting library's
    # output, or a raster image produced by an image model, is neither authored
    # here nor reproducible from the JSON alone. Reject the fingerprints.
    low = markup.lower()
    for marker in ("<canvas", "plotly", "matplotlib", "chart.js", "chartjs",
                   "highcharts", "echarts", "vega", "bokeh", "data:image/"):
        if marker in low:
            fail.append("figure looks machine-generated (%s) -- hand-author the SVG" % marker)
            break

    # ---- originality ------------------------------------------------------
    orig = q.get("originality") or {}
    if orig.get("max_similarity") is None:
        warn.append("originality not yet scanned")
    elif orig["max_similarity"] >= 0.35:
        fail.append("similarity %.3f >= 0.35" % orig["max_similarity"])
    internal = orig.get("max_internal_similarity")
    if internal is not None and internal >= 0.25:
        fail.append("internal similarity %.3f >= 0.25 (duplicate of another item here)"
                    % internal)

    # ---- provenance -------------------------------------------------------
    prov = q.get("provenance") or {}
    if not prov.get("inspired_by"):
        fail.append("no provenance.inspired_by")
    if prov.get("inspired_by") not in ("original", None) and not prov.get("adaptation"):
        fail.append("borrowed item with no adaptation note")

    # ---- verification ------------------------------------------------------
    ver = q.get("verification") or {}
    if not ver.get("method"):
        fail.append("no verification method")
    assertions = ver.get("assertions") or []
    if not assertions and subj in ("Math AA HL", "Physics HL"):
        warn.append("no verification.assertions (arithmetic not machine-checked)")
    for expr in assertions:
        ok, err = evaluate(expr)
        if err:
            fail.append("assertion error: %s" % err)
        elif not ok:
            fail.append("assertion false: %s" % expr)

    if q.get("status") not in ("draft", "reviewed", "published"):
        warn.append("status %r not draft/reviewed/published" % q.get("status"))
    elif q.get("status") == "draft":
        warn.append("still draft")

    return fail, warn


def evaluate(expr):
    """Run one verification assertion. Returns (bool, error_or_None)."""
    # Curated namespace: pure functions only, no builtins. `comb` and `factorial`
    # are included so that combinatorial identities can be machine-checked the
    # same way arithmetic ones are. `all` and `any` are included because the
    # natural assertion for a sequence or a counting item is a universal one --
    # "for every k in range(...)" -- and without them authors are forced into
    # obscure encodings such as min([...]) that hide the intent. Both are pure
    # and side-effect free, so admitting them widens what can be *expressed*
    # without weakening what is *checked*.
    env = {"__builtins__": {}, "abs": abs, "min": min, "max": max, "round": round,
           "sum": sum, "pow": pow, "float": float, "int": int, "len": len,
           "range": range, "comb": math.comb, "factorial": math.factorial,
           "all": all, "any": any}
    env.update({k: getattr(math, k) for k in
                ("sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "log",
                 "log10", "exp", "radians", "degrees", "pi", "e", "hypot", "fabs")})
    env["G"] = 6.674e-11
    env["g"] = 9.81
    env["c"] = 2.998e8
    env["e_charge"] = 1.602e-19
    env["approx"] = lambda a, b, tol=1e-6: abs(a - b) <= tol * max(1.0, abs(b))
    env["pct"] = lambda a, b: abs(a - b) <= 0.01 * max(1e-9, abs(b))
    try:
        return bool(eval(expr, env)), None      # noqa: S307 - curated namespace
    except Exception as exc:
        return False, "%s: %s" % (expr, exc)


def load():
    rows = []
    for f in sorted(DATA.glob("*/*.json")):
        if f.name.startswith("_"):
            continue
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print("FAIL  %s: unreadable (%s)" % (f, e))
            continue
        for q in payload.get("questions", []):
            rows.append((f, q))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--subject", help="filter by exact subject name")
    ap.add_argument("--quiet", action="store_true", help="only print failures")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as failures (use for newly written batches)")
    args = ap.parse_args()

    rows = load()
    if args.subject:
        rows = [(f, q) for f, q in rows if q.get("subject") == args.subject]

    medians = {}
    for subj in SUBJECTS:
        medians[subj] = {}
        for field in ("answer", "markscheme_notes", "explanation"):
            vals = [words(q.get(field)) for _, q in rows if q.get("subject") == subj]
            if vals:
                medians[subj][field] = statistics.median(vals)

    if args.stats:
        print("%-22s %-22s %5s %5s %5s %5s" % ("id", "subject", "stem", "ans", "msn", "expl"))
        for _, q in rows:
            print("%-22s %-22s %5d %5d %5d %5d" % (
                q.get("id", "?"), q.get("subject", ""), words(q.get("question")),
                words(q.get("answer")), words(q.get("markscheme_notes")),
                words(q.get("explanation"))))
        print("\nsubject medians (soft targets at %d%%):" % (MEDIAN_FRACTION * 100))
        for subj, m in medians.items():
            if m:
                print("  %-24s ans %d · msn %d · expl %d"
                      % (subj, m["answer"], m["markscheme_notes"], m["explanation"]))
        return 0

    seen, n_fail, n_warn = set(), 0, 0
    for f, q in rows:
        fail, warn = check(q, seen, medians)
        if args.strict:
            fail = fail + ["(warning) " + w for w in warn]
            warn = []
        n_fail += len(fail)
        n_warn += len(warn)
        flag = "FAIL" if fail else ("ok  " if not warn else "ok* ")
        if not (args.quiet and not fail):
            print("%s %-22s %-4s %3s marks  %s" % (
                flag, q.get("id", "?"), q.get("difficulty"), q.get("marks"), f.name))
            for x in fail:
                print("      x " + x)
            for w in warn:
                print("      ! " + w)

    print("\n%d questions · %d failure(s) · %d warning(s)%s"
          % (len(rows), n_fail, n_warn, "  [strict]" if args.strict else ""))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
