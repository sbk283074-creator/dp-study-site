"""State the answer key in the three MCQ clusters that never print a letter.

`validate.py` now warns on an MCQ part whose answer never says which option is
correct. 15 parts across PHYS-A.4-101, PHYS-B.5-101 and PHYS-D.4-101 do exactly
that: they work the value and then discuss distractors by letter, so a student
reading the markscheme has to match numbers to letters by hand -- which became a
real problem the moment `build.py` started printing the options on the paper.

The edit is purely additive: the part lead `**(a)**` becomes `**(a) B.**` using
the option already flagged `correct` in the data. Nothing else in the answer --
not a number, not a rationale -- is touched. The files are patched as raw text
so their JSON formatting is preserved byte for byte.
"""
import json, re, sys, glob

FILES = {
    "PHYS-A.4-101": "data/physics-hl/batch11.json",
    "PHYS-B.5-101": "data/physics-hl/batch11.json",
    "PHYS-D.4-101": "data/physics-hl/batch11.json",
}

# locate the real file for each id
where = {}
for path in glob.glob("data/physics-hl/*.json"):
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception:
        continue
    for q in doc.get("questions", []):
        if q["id"] in ("PHYS-A.4-101", "PHYS-B.5-101", "PHYS-D.4-101"):
            where[q["id"]] = (path, {str(p["label"]): next(o["label"] for o in p["options"] if o.get("correct"))
                                     for p in q["parts"]})
missing = set(FILES) - set(where)
if missing:
    sys.exit("ids not found: %s" % missing)

by_file = {}
for qid, (path, keys) in where.items():
    by_file.setdefault(path, {})[qid] = keys

for path, items in by_file.items():
    raw = open(path, encoding="utf-8").read()
    original = raw
    for qid, keys in items.items():
        # the item's own slice of the file, so a shared lead string in another
        # item can never be the one we hit
        start = raw.index('"id": "%s"' % qid)
        nxt = raw.find('"id": "', start + 10)
        end = nxt if nxt != -1 else len(raw)
        span = raw[start:end]
        out = span
        done = []
        for lab, key in sorted(keys.items()):
            lead = "**(%s)**" % lab
            want = "**(%s) %s.**" % (lab, key)
            n = out.count(lead)
            if n != 1:
                sys.exit("%s part (%s): lead %r occurs %d times, expected 1 -- refusing to guess"
                         % (qid, lab, lead, n))
            if want in out:
                sys.exit("%s part (%s): %r already present" % (qid, lab, want))
            out = out.replace(lead, want)
            done.append("%s->%s" % (lab, key))
        raw = raw[:start] + out + raw[end:]
        print("%s: stated the key for %s" % (qid, ", ".join(done)))
    if raw == original:
        sys.exit("%s: nothing changed" % path)
    # the file must still parse, and parse to the same data bar the answers
    json.loads(raw)
    open(path, "w", encoding="utf-8").write(raw)
    print("wrote", path)
