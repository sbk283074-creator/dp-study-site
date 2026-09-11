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
            mine.append((q["id"], q.get("subject"), grams(normalise(question_text(q)))))

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
            for oid2, osubj, ograms in mine:
                if oid2 == q["id"]:
                    continue
                s = jaccard(own, ograms)
                if s > best_int[0]:
                    best_int = (s, oid2)
            internal, internal_id = best_int

            q.setdefault("originality", {})
            q["originality"]["max_similarity"] = round(score, 3)
            q["originality"]["nearest_bank_id"] = str(oid) if oid else None
            q["originality"]["nearest_bank_label"] = label
            q["originality"]["max_internal_similarity"] = round(internal, 3)
            q["originality"]["nearest_internal_id"] = internal_id
            q["originality"]["checked_at"] = "2026-09-11"
            changed = True

            external_fail = score >= SAME_SUBJECT_REJECT
            internal_fail = internal >= INTERNAL_REJECT
            if external_fail or internal_fail:
                failures += 1
            verdict = "FAIL" if (external_fail or internal_fail) else "PASS"
            print("%-22s ext %.3f  int %.3f (%s)  %s  [nearest ext: %s]"
                  % (q["id"], score, internal, internal_id, verdict, oid))
            if internal_fail:
                print("      ! too close to %s inside this bank" % internal_id)
            if external_fail:
                print("      ! too close to %s in the existing corpus" % oid)
        if args.write and changed:
            f.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n%d question(s) above threshold (external %.2f / internal %.2f)."
          % (failures, SAME_SUBJECT_REJECT, INTERNAL_REJECT))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
