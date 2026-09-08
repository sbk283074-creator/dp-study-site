#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export the IB DP question bank from the old platform's SQLite database into
static JS data files consumed by the `qbank/` section of this site.

Source (read-only, never modified):
    <workspace>/dp learning/ib-dp-platform/backend/data/app.db

Output (as .js files that assign globals, NOT .json — the site has to work
over file:// where fetch() is blocked by CORS, so data is loaded by injecting
a <script> tag exactly like assets/js/search-index.js):
    qbank/data/meta.js                   window.QB_META - counts, facets,
                                         knowledge points, exam papers, books
    qbank/data/index.js                  window.QB_INDEX - lightweight rows
                                         used for search / filtering
    qbank/data/physics.js                window.QB_DATA.physics - full records
    qbank/data/mathematics.js            window.QB_DATA.mathematics
    qbank/data/computer-science.js       window.QB_DATA['computer-science']

Usage:
    python3 tools/export_questions.py                 # full export
    python3 tools/export_questions.py --report-only   # print facets, write nothing

Every question gets a `status` of current / legacy / unknown.  See
CURRENT_FROM below for the rule and the reasoning behind it.
"""

import argparse
import collections
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(SITE, "dp learning", "ib-dp-platform", "backend", "data", "app.db")
OUT = os.path.join(SITE, "qbank", "data")

# Columns mirrored from backend/src/questionRepo.js
COLUMNS = [
    "id", "subject", "level", "topic", "subtopic", "paper_type", "command_term",
    "marks", "difficulty", "question", "figure", "answer", "explanation",
    "source", "tags", "authored_by", "created_at", "knowledge_point_ids",
    "answer_figure", "question_image", "answer_image", "figure_image",
    "definition_basis", "book_id", "book_section", "book_page", "in_book_order",
    "source_type", "category", "review_status",
]

# ---------------------------------------------------------------------------
# Subject grouping
# ---------------------------------------------------------------------------
SUBJECT_KEYS = {
    "physics": "physics",
    "mathematics": "mathematics",
    "math aa": "mathematics",
    "maths aa": "mathematics",
    "mathematics: analysis and approaches": "mathematics",
    "computer science": "computer-science",
    "computer science hl": "computer-science",
    "cs": "computer-science",
}
SUBJECT_LABELS = {
    "physics": "Physics HL",
    "mathematics": "Mathematics AA HL",
    "computer-science": "Computer Science HL",
    "other": "Other",
}
SUBJECT_FILES = {
    "physics": "physics.js",
    "mathematics": "mathematics.js",
    "computer-science": "computer-science.js",
    "other": "other.js",
}

# ---------------------------------------------------------------------------
# Currency rule
# ---------------------------------------------------------------------------
# A past-paper question is "current" for the May 2028 session only if it was
# set under the syllabus Lucas will actually be examined on.  First-assessment
# years (verified against the IB subject guides):
#
#   Physics          2025 guide -> first assessment 2027
#   Computer Science 2027 guide -> first assessment 2027
#   Mathematics AA   2021 guide -> first assessment 2021 (next change is 2029)
#
# So anything dated before those years comes from a superseded guide.  It is
# still perfectly good practice for overlapping content, which is why legacy
# questions are imported rather than dropped - they are simply flagged and
# hidden behind a filter by default.
CURRENT_FROM = {
    "physics": 2027,
    "computer-science": 2027,
    "mathematics": 2021,
    "other": 0,
}

YEAR4 = re.compile(r"(19\d{2}|20\d{2})")
YEAR2 = re.compile(r"\b(\d{2})\s*[MN]\b")
SESSION = re.compile(r"\b(may|nov|november)\b", re.I)


def subject_key(raw):
    """Normalise a raw subject string into a stable group key."""
    s = (raw or "").strip().lower()
    if not s:
        return "other"
    if s in SUBJECT_KEYS:
        return SUBJECT_KEYS[s]
    if "physic" in s:
        return "physics"
    if "computer" in s or s == "cs":
        return "computer-science"
    if "math" in s:
        return "mathematics"
    return "other"


def extract_year(source):
    """Pull a 4-digit exam year out of a free-text source string.

    Handles "IB 真题 2016 May Physics HL Paper 1" (2016) and the classified
    code "18M.2.SL.TZO.4" (2018).
    """
    s = source or ""
    m = YEAR4.search(s)
    if m:
        y = int(m.group(1))
        if 1990 <= y <= 2035:
            return y
    m = YEAR2.search(s)
    if m:
        yy = int(m.group(1))
        return 2000 + yy if yy < 70 else 1900 + yy
    return None


def extract_session(source):
    m = SESSION.search(source or "")
    if not m:
        return None
    return "Nov" if m.group(1).lower().startswith("nov") else "May"


def currency(key, year, category=None):
    """Mark a question as current / legacy / unknown for the May 2028 session.

    Curated `topic` and `questionbank` entries are assumed to have been
    written for the guide Lucas will be examined on (the new guide where
    applicable) so they count as current even when the source string has no
    year.  Real past-paper entries are bucketed by year against each
    subject's first-assessment year.
    """
    if category in ("topic", "questionbank"):
        return "current"
    if year is None:
        return "unknown"
    return "current" if year >= CURRENT_FROM.get(key, 0) else "legacy"


def split_images(value):
    """Turn a comma-separated figure path list into a clean array of paths."""
    if not value:
        return []
    out = []
    for part in str(value).split(","):
        p = part.strip()
        if not p:
            continue
        p = re.sub(r"^\/?figures\/", "", p)
        out.append(p)
    return out


def snippet(text, n=220):
    if not text:
        return ""
    s = re.sub(r"\s+", " ", str(text)).strip()
    return s[:n] + ("…" if len(s) > n else "")


def jload(value, default):
    """Safely parse a JSON column; fall back to the default."""
    if not value:
        return default
    try:
        parsed = json.loads(value)
        return parsed if parsed is not None else default
    except (ValueError, TypeError):
        return default


def build_records(conn):
    """Read every question once and return (records, index_rows)."""
    rows = conn.execute(
        "SELECT {} FROM questions".format(", ".join(COLUMNS))
    ).fetchall()

    records = []
    index_rows = []
    for r in rows:
        d = dict(zip(COLUMNS, r))
        key = subject_key(d.get("subject"))
        year = extract_year(d.get("source"))
        status = currency(key, year, d.get("category"))

        q_imgs = split_images(d.get("question_image"))
        a_imgs = split_images(d.get("answer_image"))
        f_imgs = split_images(d.get("figure_image"))
        fig = split_images(d.get("figure"))
        afig = split_images(d.get("answer_figure"))

        kps = jload(d.get("knowledge_point_ids"), [])
        if not isinstance(kps, list):
            kps = []
        tags = jload(d.get("tags"), [])
        if not isinstance(tags, list):
            tags = []

        rec = {
            "id": d.get("id"),
            "subject": d.get("subject"),
            "group": key,
            "level": d.get("level"),
            "topic": d.get("topic"),
            "subtopic": d.get("subtopic"),
            "paper": d.get("paper_type"),
            "command": d.get("command_term"),
            "marks": d.get("marks"),
            "difficulty": d.get("difficulty"),
            "question": d.get("question") or "",
            "answer": d.get("answer") or "",
            "explanation": d.get("explanation") or "",
            "source": d.get("source") or "",
            "year": year,
            "session": extract_session(d.get("source")),
            "status": status,
            "category": d.get("category"),
            "sourceType": d.get("source_type"),
            "authoredBy": d.get("authored_by"),
            "review": d.get("review_status"),
            "tags": tags,
            "kps": kps,
            "basis": d.get("definition_basis"),
            "bookId": d.get("book_id"),
            "bookSection": d.get("book_section"),
            "bookPage": d.get("book_page"),
            "imgQ": q_imgs,
            "imgA": a_imgs,
            "imgF": f_imgs,
            "fig": fig,
            "figA": afig,
        }
        records.append(rec)
        index_rows.append({
            "id": rec["id"],
            "g": key,
            "t": rec["topic"] or "",
            "p": rec["paper"] or "",
            "c": rec["command"] or "",
            "m": rec["marks"],
            "cat": rec["category"] or "",
            "s": 0 if status == "current" else (1 if status == "legacy" else 2),
            "y": year,
            "x": snippet(rec["question"], 200),
            "i": 1 if q_imgs or fig else 0,
        })
    return records, index_rows


def table_exists(conn, name):
    return bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone())


def load_knowledge_points(conn, records):
    if not table_exists(conn, "knowledge_points"):
        return []
    counts = collections.Counter()
    for r in records:
        for k in r["kps"]:
            counts[k] += 1
    out = []
    for row in conn.execute("SELECT * FROM knowledge_points ORDER BY subject, code"):
        d = dict(row)
        out.append({
            "id": d.get("id"),
            "subject": d.get("subject"),
            "group": subject_key(d.get("subject")),
            "code": d.get("code"),
            "theme": d.get("theme"),
            "title": d.get("title"),
            "description": d.get("description"),
            "refs": jload(d.get("refs"), []),
            "count": counts.get(d.get("id"), 0),
        })
    return out


def load_exam_papers(conn):
    if not table_exists(conn, "exam_papers"):
        return []
    out = []
    for row in conn.execute(
        "SELECT * FROM exam_papers ORDER BY created_at DESC"
    ):
        d = dict(row)
        items = []
        if table_exists(conn, "exam_paper_items"):
            items = [r[0] for r in conn.execute(
                "SELECT question_id FROM exam_paper_items WHERE exam_id=? ORDER BY position",
                (d.get("id"),)
            ).fetchall()]
        out.append({
            "id": d.get("id"),
            "subject": d.get("subject"),
            "group": subject_key(d.get("subject")),
            "paper": d.get("paper_type"),
            "name": d.get("name"),
            "createdAt": d.get("created_at"),
            "durationMin": d.get("duration_min"),
            "totalMarks": d.get("total_marks"),
            "numQuestions": d.get("num_questions"),
            "note": d.get("note"),
            "items": items,
        })
    return out


def load_books(conn, records):
    if not table_exists(conn, "books"):
        return []
    counts = collections.Counter(r["bookId"] for r in records if r["bookId"])
    out = []
    for row in conn.execute("SELECT * FROM books ORDER BY subject, title"):
        d = dict(row)
        bid = d.get("id")
        out.append({
            "id": bid,
            "subject": d.get("subject"),
            "group": subject_key(d.get("subject")),
            "title": d.get("title"),
            "publisher": d.get("publisher"),
            "edition": d.get("edition"),
            "hasAnswers": bool(d.get("has_answers")),
            "totalQuestions": d.get("total_questions"),
            "count": counts.get(bid, 0),
        })
    return out


def report(records, kps, exams, books):
    """Print the facet breakdown so the currency rule can be sanity-checked."""
    print("=" * 68)
    print("QUESTION BANK EXPORT REPORT")
    print("=" * 68)
    print("total questions: {}".format(len(records)))

    by_group = collections.defaultdict(list)
    for r in records:
        by_group[r["group"]].append(r)

    for key in ("physics", "mathematics", "computer-science", "other"):
        rs = by_group.get(key)
        if not rs:
            continue
        st = collections.Counter(r["status"] for r in rs)
        print("\n--- {} ({}) ---".format(SUBJECT_LABELS[key], len(rs)))
        print("  status: " + ", ".join(
            "{} {}".format(st[k], k) for k in ("current", "legacy", "unknown") if st[k]))
        print("  raw subject values: " + ", ".join(
            "{} ({})".format(v, c) for v, c in
            collections.Counter(r["subject"] for r in rs).most_common()))
        yr = sorted({r["year"] for r in rs if r["year"]})
        if yr:
            print("  years: {} – {}".format(yr[0], yr[-1]))
        print("  categories: " + ", ".join(
            "{} ({})".format(v or "-", c) for v, c in
            collections.Counter(r["category"] for r in rs).most_common()))
        print("  papers: " + ", ".join(
            "{} ({})".format(v or "-", c) for v, c in
            collections.Counter(r["paper"] for r in rs).most_common(12)))
        tops = collections.Counter(r["topic"] for r in rs).most_common(40)
        print("  topics ({} distinct) top 40:".format(
            len({r["topic"] for r in rs})))
        for v, c in tops:
            print("      {:>5}  {}".format(c, v or "(empty)"))

    print("\nknowledge points: {}".format(len(kps)))
    print("exam papers: {}".format(len(exams)))
    print("books: {}".format(len(books)))
    print("=" * 68)


def write_js(path, prefix, obj):
    """Write `prefix` + JSON + ';' so the file can be loaded via <script>.

    fetch() is unavailable on file:// so every data file is a script that
    assigns a global instead of a bare .json document.
    """
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(prefix)
        json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-only", action="store_true",
                    help="print facets and exit without writing any files")
    ap.add_argument("--db", default=DB, help="path to app.db")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        sys.exit("Database not found: {}".format(args.db))

    conn = sqlite3.connect("file:{}?mode=ro".format(args.db), uri=True)
    conn.row_factory = sqlite3.Row

    records, index_rows = build_records(conn)
    kps = load_knowledge_points(conn, records)
    exams = load_exam_papers(conn)
    books = load_books(conn, records)

    report(records, kps, exams, books)
    if args.report_only:
        conn.close()
        return

    os.makedirs(OUT, exist_ok=True)

    # Full records, one file per subject group.
    groups = collections.defaultdict(list)
    for r in records:
        groups[r["group"]].append(r)

    written = {}
    for key, rs in groups.items():
        rs.sort(key=lambda r: (-(r["year"] or 0), r["id"] or ""))
        fname = SUBJECT_FILES[key]
        path = os.path.join(OUT, fname)
        write_js(path, 'window.QB_DATA=window.QB_DATA||{};window.QB_DATA["{}"]='.format(key, key), rs)
        written[key] = {
            "file": fname,
            "count": len(rs),
            "bytes": os.path.getsize(path),
        }
        print("wrote {} ({:,} questions, {:.1f} MB)".format(
            fname, len(rs), os.path.getsize(path) / 1e6))

    # Facets, computed per subject group.
    facets = {}
    for key, rs in groups.items():
        def distinct(field):
            vals = collections.Counter(r[field] for r in rs if r[field])
            return [{"v": v, "n": c} for v, c in vals.most_common()]
        st = collections.Counter(r["status"] for r in rs)
        facets[key] = {
            "topics": distinct("topic"),
            "papers": distinct("paper"),
            "commands": distinct("command"),
            "categories": distinct("category"),
            "years": sorted({r["year"] for r in rs if r["year"]}),
        }

    meta = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": args.db,
        "total": len(records),
        "currentFrom": CURRENT_FROM,
        "subjects": [
            {
                "key": key,
                "label": SUBJECT_LABELS.get(key, key),
                "file": SUBJECT_FILES[key],
                "count": written[key]["count"],
                "bytes": written[key]["bytes"],
                "current": sum(1 for r in groups[key] if r["status"] == "current"),
                "legacy": sum(1 for r in groups[key] if r["status"] == "legacy"),
                "unknown": sum(1 for r in groups[key] if r["status"] == "unknown"),
            }
            for key in groups
        ],
        "facets": facets,
        "knowledgePoints": kps,
        "examPapers": exams,
        "books": books,
        "statusTotals": dict(collections.Counter(r["status"] for r in records)),
    }

    # NOTE: these MUST be .js globals, not .json — the site runs over file://
    # where fetch() is blocked by CORS, so the data is injected by a <script>
    # tag exactly like assets/js/search-index.js.
    meta_path = os.path.join(OUT, "meta.js")
    write_js(meta_path, "window.QB_META=", meta)

    idx_path = os.path.join(OUT, "index.js")
    write_js(idx_path, "window.QB_INDEX=", index_rows)

    # Clean up any stray .json left over from an earlier (broken) export run.
    for stray in ("meta.json", "index.json"):
        sp = os.path.join(OUT, stray)
        if os.path.exists(sp):
            os.remove(sp)

    print("wrote meta.js, index.js ({:.1f} MB)".format(
        os.path.getsize(idx_path) / 1e6))
    print("status totals: {}".format(meta["statusTotals"]))
    conn.close()


if __name__ == "__main__":
    main()
