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
            "verification", "status"]

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

    if marks < rule["min_marks"]:
        fail.append("marks %s < floor %s" % (marks, rule["min_marks"]))
    if subj == "Math AA HL" and q.get("paper") == "P3" and marks < 12:
        fail.append("P3 maths item under 12 marks")

    if len(parts) < rule["min_parts"]:
        fail.append("%d parts < %d required" % (len(parts), rule["min_parts"]))
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

    # ---- length contract -------------------------------------------------
    for field, floor in MIN_WORDS.get(subj, {}).items():
        n = words(q.get(field))
        if n < floor:
            fail.append("%s %d words < %d" % (field, n, floor))
        else:
            med = (medians.get(subj) or {}).get(field)
            if med and n < med * MEDIAN_FRACTION:
                warn.append("%s %d words < %.0f%% of subject median (%d)"
                            % (field, n, MEDIAN_FRACTION * 100, med))

    # Context is everything the student actually reads: the stem, the stimulus
    # and the part texts. A short stem is fine when the parts carry the detail,
    # which is the normal shape for maths and physics.
    context = (words(q.get("question")) + words(stimulus_text(q))
               + sum(words(p.get("text")) for p in parts))
    floor_ctx = MIN_CONTEXT.get(subj, 60)
    if context < floor_ctx:
        fail.append("total context %d words < %d" % (context, floor_ctx))

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
    if subj in ("Math AA HL", "Physics HL"):
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
    env = {"__builtins__": {}, "abs": abs, "min": min, "max": max, "round": round,
           "sum": sum, "pow": pow, "float": float, "int": int}
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
