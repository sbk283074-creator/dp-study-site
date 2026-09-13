#!/usr/bin/env python3
"""Originality gate for the Challenge Bank (PLAN.md section 5).

Compares every question in data/ against
  (a) the 9,969 questions in the existing bank   (dp learning/.../data/app.db)
  (b) the un-imported generated batches          (dp learning/.../backend/generated/*.json)
  (c) every other question already in this bank

Method: word-level 5-gram Jaccard over normalised text (LaTeX and punctuation
stripped). Thresholds: reject at >= 0.35 within the same subject, >= 0.50 across
subjects.

    python3 tools/similarity_check.py              # report only
    python3 tools/similarity_check.py --write      # also fill in `originality` in data/
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB = ROOT.parent / "dp learning" / "ib-dp-platform" / "backend" / "data" / "app.db"
GENERATED = ROOT.parent / "dp learning" / "ib-dp-platform" / "backend" / "generated"

N = 5
SAME_SUBJECT_REJECT = 0.35
CROSS_SUBJECT_REJECT = 0.50
# Inside this bank the threshold is tighter: the same author, the same house
# style and often the same syllabus bullet, so shared phrasing means more here
# than it does against a 9,969-question past-paper corpus.
INTERNAL_REJECT = 0.25

SUBJECT_ALIASES = {
    "math aa hl": "maths", "math aa": "maths", "mathematics": "maths", "maths aa": "maths",
    "physics hl": "physics", "physics": "physics",
    "computer science hl": "cs", "computer science": "cs", "cs": "cs",
    "business management sl": "business", "business management": "business",
}


def family(subject):
    s = (subject or "").lower().strip()
    return SUBJECT_ALIASES.get(s, s.split(":")[0].split(" ")[0])


def normalise(text):
    """Strip LaTeX scaffolding and punctuation, keep the words."""
    if not text:
        return []
    t = str(text)
    t = re.sub(r"\\[a-zA-Z]+", " ", t)          # LaTeX commands
    t = re.sub(r"[{}$&\\\\]", " ", t)            # math delimiters and escapes
    t = re.sub(r"<[^>]+>", " ", t)               # any HTML
    t = re.sub(r"[^a-z0-9]+", " ", t.lower())
    return t.split()


def grams(words, n=N):
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def question_text(q):
    parts = [q.get("question", "")]
    parts += [p.get("text", "") for p in (q.get("parts") or [])]
    if isinstance(q.get("stimulus"), str):
        parts.append(q["stimulus"])
    elif isinstance(q.get("stimulus"), dict):
        parts.append(q["stimulus"].get("body", ""))
    return " ".join(str(p) for p in parts)


# ---------------------------------------------------------------------------
# Approach-level similarity.
#
# Word 5-grams cannot see that "Maclaurin series of e^(sin x)" and "Taylor
# expansion of e^(cos x) at 0" are the same question by method: the shared
# words are function words, so the Jaccard is ~0.02 and the lexical gate waves
# both through. Conversely two flywheel questions, one solved by energy and one
# by angular impulse, share almost all their nouns and get flagged while being
# genuinely different questions.
#
# The remedy is to compare the declared solution skeleton instead: each item
# states the 3-6 steps of its own solution, and we match those steps to each
# other. Two questions that walk the same steps are the same question however
# they are dressed up; two that reach similar-looking answers by different
# routes are not.
#
# Only items that declare a skeleton take part, so this is purely additive and
# leaves the pre-existing bank exactly as it was.
# ---------------------------------------------------------------------------
STEP_MATCH = 0.34          # above this, two steps count as the same step
APPROACH_REJECT = 0.50     # shared fraction of solution structure that is too much

# Function words carry no method signal and would inflate every comparison.
STOP = {"the", "a", "an", "of", "to", "in", "for", "and", "or", "with", "by",
        "from", "as", "is", "are", "it", "that", "this", "then", "be", "on",
        "at", "its", "into", "over", "under", "each", "per"}


SUFFIXES = ("ations", "ation", "tion", "sion", "ions", "ing", "ings", "ed",
            "es", "al", "ive", "ment", "ance", "ence", "ly", "ity", "ies", "s")


def stem(w):
    """Crude suffix stripper. Enough to land 'expand', 'expands', 'expanding'
    and 'expansion' on the same token, which is the whole point here: the same
    step described with a different part of speech is still the same step."""
    for suf in SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def tok_match(a, b):
    """True if two tokens name the same idea."""
    if a == b:
        return True
    sa, sb = stem(a), stem(b)
    if len(sa) >= 4 and sa == sb:
        return True
    n = min(len(sa), len(sb))
    return n >= 4 and sa[:n] == sb[:n]


def step_tokens(step):
    return {w for w in normalise(step) if w not in STOP and len(w) > 2}


def skeleton_of(q):
    skel = (q.get("verification") or {}).get("solution_skeleton")
    if not isinstance(skel, list) or not skel:
        return []
    return [step_tokens(s) for s in skel]


def step_sim(a, b):
    """Fuzzy Jaccard between two steps: the fraction of tokens on each side
    that name something the other side also names."""
    if not a or not b:
        return 0.0
    ab = sum(1 for x in a if any(tok_match(x, y) for y in b))
    ba = sum(1 for y in b if any(tok_match(y, x) for x in a))
    return (ab + ba) / (len(a) + len(b))


def approach_similarity(sa, sb):
    """Overlap of two solution skeletons, 0..1.

    Each step in A is matched greedily to its best unused step in B; matches
    below STEP_MATCH are discarded. The score is the matched weight as a
    fraction of the combined length of both skeletons, so a short skeleton
    matching a short one scores the same as a long one matching a long one.
    """
    if not sa or not sb:
        return 0.0
    used, total = set(), 0.0
    for a in sa:
        best, bj = 0.0, -1
        for j, b in enumerate(sb):
            if j in used:
                continue
            s = step_sim(a, b)
            if s > best:
                best, bj = s, j
        if bj >= 0 and best >= STEP_MATCH:
            used.add(bj)
            total += best
    return 2 * total / (len(sa) + len(sb))


def load_corpus():
    """Return [(id, subject_family, label, gram_set), ...]"""
    corpus = []
    if DB.exists():
        con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
        for qid, subject, topic, question in con.execute(
                "select id, subject, topic, question from questions"):
            corpus.append((qid, family(subject), "bank:%s/%s" % (subject, topic or ""),
                           grams(normalise(question))))
        con.close()
    if GENERATED.is_dir():
        for f in sorted(GENERATED.glob("*.json")):
            try:
                payload = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            items = payload.get("questions", payload) if isinstance(payload, dict) else payload
            for q in items:
                if not isinstance(q, dict):
                    continue
                corpus.append((q.get("id", f.stem), family(q.get("subject")),
                               "generated:%s" % f.name, grams(normalise(q.get("question", "")))))
    return corpus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write scores back into data/*.json")
    args = ap.parse_args()

    corpus = load_corpus()
    print("Corpus: %d existing questions." % len(corpus))

    # index the corpus by family to cut comparisons
    by_family = {}
    for item in corpus:
        by_family.setdefault(item[1], []).append(item)

    files = sorted(DATA.glob("*/*.json"))
    # Pass 1: index this bank so every item can be checked against every other.
    mine = []
    for f in files:
        payload = json.loads(f.read_text(encoding="utf-8"))
        for q in payload.get("questions", []):
            mine.append((q["id"], q.get("subject"), grams(normalise(question_text(q))),
                         skeleton_of(q)))

    # Pass 2: external comparison, then internal comparison.
    failures = 0
    for f in files:
        payload = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for q in payload.get("questions", []):
            own = grams(normalise(question_text(q)))
            fam = family(q.get("subject"))
            best = (0.0, None, None)
            for other_fam, items in by_family.items():
                for oid, ofam, label, ograms in items:
                    s = jaccard(own, ograms)
                    if s > best[0]:
                        best = (s, oid, label)
            score, oid, label = best

            best_int = (0.0, None)
            for oid2, osubj, ograms, _oskel in mine:
                if oid2 == q["id"]:
                    continue
                s = jaccard(own, ograms)
                if s > best_int[0]:
                    best_int = (s, oid2)
            internal, internal_id = best_int

            # Approach-level comparison: same method, different words.
            best_app = (0.0, None)
            my_skel = skeleton_of(q)
            if my_skel:
                for oid2, osubj, _ograms, oskel in mine:
                    if oid2 == q["id"] or not oskel:
                        continue
                    s = approach_similarity(my_skel, oskel)
                    if s > best_app[0]:
                        best_app = (s, oid2)
            approach, approach_id = best_app

            q.setdefault("originality", {})
            q["originality"]["max_similarity"] = round(score, 3)
            q["originality"]["nearest_bank_id"] = str(oid) if oid else None
            q["originality"]["nearest_bank_label"] = label
            q["originality"]["max_internal_similarity"] = round(internal, 3)
            q["originality"]["nearest_internal_id"] = internal_id
            if my_skel:
                q["originality"]["max_approach_similarity"] = round(approach, 3)
                q["originality"]["nearest_approach_id"] = approach_id
            q["originality"]["checked_at"] = "2026-09-11"
            changed = True

            external_fail = score >= SAME_SUBJECT_REJECT
            internal_fail = internal >= INTERNAL_REJECT
            approach_fail = bool(my_skel) and approach >= APPROACH_REJECT
            if external_fail or internal_fail or approach_fail:
                failures += 1
            verdict = "FAIL" if (external_fail or internal_fail or approach_fail) else "PASS"
            app_str = ("  appr %.3f (%s)" % (approach, approach_id)) if my_skel else ""
            print("%-22s ext %.3f  int %.3f (%s)%s  %s  [nearest ext: %s]"
                  % (q["id"], score, internal, internal_id, app_str, verdict, oid))
            if internal_fail:
                print("      ! too close to %s inside this bank" % internal_id)
            if external_fail:
                print("      ! too close to %s in the existing corpus" % oid)
            if approach_fail:
                print("      ! same solution approach as %s (%.3f >= %.2f)"
                      % (approach_id, approach, APPROACH_REJECT))
        if args.write and changed:
            f.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n%d question(s) above threshold (external %.2f / internal %.2f)."
          % (failures, SAME_SUBJECT_REJECT, INTERNAL_REJECT))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
