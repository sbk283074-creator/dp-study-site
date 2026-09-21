#!/usr/bin/env python3
"""Check each language track against its declared standard in TRACK-STANDARD.md.

    python3 _build/check-standard.py               # every track with a chapters/ dir
    python3 _build/check-standard.py python cpp    # just these
    python3 _build/check-standard.py --no-verify   # skip running each harness
    python3 _build/check-standard.py --self-test   # prove this checker can fail

`kind` in _build/languages.json picks the bar: "full" or "mini". They are different
bars, not one bar at two strengths -- see TRACK-STANDARD.md, Part 2.

Exit code is 0 only if every checked track conforms. This is a gate, so it carries
a --self-test: a criterion this checker cannot fail is not a criterion.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLATFORM = HERE.parent
REGISTRY = HERE / "languages.json"

FENCE_RE = re.compile(r"^\s*```(\S+)\s+(\S+)\s*$")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

# A layer is located by the PART TITLE in parts.json, using these markers. Teaching
# descriptors inside a chapter called "OOP II" does not satisfy the internals layer:
# the layer is a part, so a reader can find it and the outline states the intent.
LAYER_MARKERS = {
    "internals": ("internals", "actually works", "under the hood", "runtime"),
    "cost": ("algorithms", "complexity", "data structures"),
    "security": ("security", "hardening"),
    "architecture": ("architecture", "patterns", "design"),
    "performance": ("performance", "scale", "profiling"),
}

FULL_LAYER_MIN = {"internals": 3, "cost": 4, "security": 2, "architecture": 2, "performance": 2}
MINI_LAYER_MIN = {"security": 1, "performance": 1}

REQUIRED_FM = ("chapter", "part", "title", "summary", "minutes", "tags")


class Report:
    def __init__(self, track, kind):
        self.track, self.kind = track, kind
        self.rows = []          # (ok, criterion, detail)

    def add(self, ok, criterion, detail=""):
        self.rows.append((ok, criterion, detail))

    @property
    def failures(self):
        return [r for r in self.rows if not r[0]]

    def show(self):
        state = "PASS" if not self.failures else "FAIL"
        print(f"\n=== {self.track}  [{self.kind}]  -> {state}")
        for ok, crit, detail in self.rows:
            mark = "  ok  " if ok else " FAIL "
            print(f"{mark} {crit}{('  ' + detail) if detail else ''}")
        return not self.failures


def parse_front(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def section(body: str, heading: str) -> str:
    if heading not in body:
        return ""
    return body.split(heading, 1)[1].split("\n## ", 1)[0]


def directive_count(body: str) -> int:
    """Fences carrying a directive, e.g. ```python run / ```cpp run-san."""
    return sum(1 for line in body.split("\n") if FENCE_RE.match(line))


def chapter_role(title: str, part_title: str) -> str:
    """Which template a chapter is graded on.

    The book has three, and grading all of them on the lesson template would
    measure the wrong artifact:

      project   a build. Carries a Milestone checklist, not exercises.
      appendix  reference material -- a cookbook, a problem bank, a wrap-up.
                Carries its own structure (numbered problems, scenario tables).
      orientation  ch00, "how to use this book". Not a lesson: it has no topic to
                teach, so it is held to front matter, takeaways and a verified
                block and not to the lesson devices.
      teaching  everything else: the lesson template applies in full.
    """
    if re.search(r"CAPSTONE|\bPROJECT\s*:", title, re.I):
        return "project"
    if re.search(r"start here", part_title, re.I):
        return "orientation"
    if re.search(r"appendices|where next", part_title, re.I):
        return "appendix"
    return "teaching"


def check_chapter(path: Path, kind: str, part_title: str = "") -> list[tuple[bool, str]]:
    """Per-chapter depth. Returns [(ok, criterion)] -- unit-testable on its own."""
    text = path.read_text(encoding="utf-8")
    fm = parse_front(text)
    body = text[FM_RE.match(text).end():] if FM_RE.match(text) else text
    role = chapter_role(fm.get("title", ""), part_title)
    out = []

    missing = [k for k in REQUIRED_FM if k not in fm]
    out.append((not missing, "front matter complete", ",".join(missing)))

    take = [l for l in section(body, "## Key takeaways").split("\n") if l.strip().startswith("- ")]
    need = 6 if kind == "full" else 4
    out.append((len(take) >= need, f"Key takeaways >= {need}", f"got {len(take)}"))

    if role == "project":
        out.append(("## Milestone checklist" in body, "project chapter has a milestone checklist", ""))
    elif role == "teaching":
        prac = [l for l in section(body, "## Practice").split("\n") if l.strip().startswith("- [")]
        need = 4 if kind == "full" else 3
        out.append((len(prac) >= need, f"Practice >= {need}", f"got {len(prac)}"))
    else:
        out.append((True, "appendix chapter: own structure", "not graded on Practice"))

    if kind == "full" and role in ("teaching", "project"):
        has_pair = ":::scenario" in body and ":::solution" in body
        out.append((has_pair, "scenario+solution pair", ""))
        # The house callout kinds include pitfall, danger and warning, and the
        # strongest mistakes get `danger`. The criterion is "at least one callout
        # naming a real mistake", so all three satisfy it.
        out.append((bool(re.search(r"^:::(pitfall|danger|warning)\b", body, re.M)),
                    "pitfall-family callout", ""))

    verified = directive_count(body)
    out.append((verified >= 1, ">= 1 verified block", f"got {verified}"))

    # Callouts do NOT nest in this builder: an opener consumes lines until the first
    # bare `:::`, and the inner text is then converted recursively. So a
    # `:::solution` inside a `:::scenario` is correctly closed by ONE `:::`, and
    # counting openers against closers would flag the house pattern. The invariant
    # that actually matters is weaker and still catches the real bug -- a callout
    # with no closing marker at all swallows the rest of the chapter.
    openers = [i for i, l in enumerate(body.split("\n")) if re.match(r"^:::(\w+)", l)]
    closers = [i for i, l in enumerate(body.split("\n")) if re.match(r"^:::\s*$", l)]
    orphan = [i + 1 for i in openers if not any(c > i for c in closers)]
    out.append((not orphan, "every callout has a closing marker",
                "" if not orphan else f"unclosed at line(s) {orphan[:3]}"))
    return out


def check_track(entry: dict, run_harness: bool) -> Report:
    tid = entry["id"]
    kind = entry.get("kind", "full")
    rep = Report(tid, kind)
    lang_dir = PLATFORM / tid
    chapters_dir = lang_dir / "chapters"

    if not chapters_dir.is_dir():
        rep.add(False, "chapters/ exists", "not started")
        return rep

    chaps = sorted(chapters_dir.glob("*.md"))
    rep.add(True, "chapters/ exists", f"{len(chaps)} chapter(s)")

    # ---- size ----
    if kind == "full":
        lo, hi = 55, 70
        rep.add(lo <= len(chaps) <= hi, f"chapters in {lo}-{hi}", f"got {len(chaps)}")
    else:
        lo, hi = 12, 22
        rep.add(lo <= len(chaps) <= hi, f"chapters in {lo}-{hi}", f"got {len(chaps)}")

    words = [len(c.read_text(encoding="utf-8").split()) for c in chaps]
    if words:
        med = statistics.median(words)
        floor = 2400 if kind == "full" else 1800
        rep.add(med >= floor, f"median words >= {floor}", f"got {int(med)}")

    # ---- parts, and the layers they declare ----
    parts_file = lang_dir / "parts.json"
    parts = json.loads(parts_file.read_text(encoding="utf-8")) if parts_file.exists() else {}
    rep.add(parts_file.exists(), "parts.json exists", "")

    fronts = [parse_front(c.read_text(encoding="utf-8")) for c in chaps]
    per_part = {}
    for fm in fronts:
        p = fm.get("part")
        per_part[p] = per_part.get(p, 0) + 1

    # "Start Here" is orientation, not teaching, so the word floor does not apply to
    # it. Every other part is held to it.
    if kind == "full":
        short = [c.name for c, w, fm in zip(chaps, words, fronts)
                 if w < 1500 and "start here" not in parts.get(fm.get("part"), "").lower()]
        rep.add(not short, "no teaching chapter < 1500 words", ",".join(short[:3]))

    # Chapters are numbered 00..NN. A gap means a chapter is planned but unwritten,
    # which is the normal state of a track under construction -- reported, not hidden.
    nums = sorted(int(m.group(1)) for m in
                  (re.match(r"^(\d+)-", c.name) for c in chaps) if m)
    if nums:
        gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in nums]
        rep.add(not gaps, "chapter numbers contiguous", f"missing {gaps[:6]}")

    found = {}
    for pnum, title in parts.items():
        low = title.lower()
        for layer, markers in LAYER_MARKERS.items():
            if any(m in low for m in markers):
                found[layer] = found.get(layer, 0) + per_part.get(pnum, 0)

    mins = FULL_LAYER_MIN if kind == "full" else MINI_LAYER_MIN
    for layer, minimum in mins.items():
        have = found.get(layer, 0)
        rep.add(have >= minimum, f"layer '{layer}' >= {minimum} chapters", f"got {have}")

    # ---- projects and capstones ----
    titles = [parse_front(c.read_text(encoding="utf-8")).get("title", "") for c in chaps]
    caps = [t for t in titles if re.search(r"CAPSTONE", t, re.I)]
    projs = [t for t in titles if re.search(r"PROJECT|CAPSTONE", t, re.I)]
    need_caps = 2 if kind == "full" else 1
    rep.add(len(caps) >= need_caps, f"capstones >= {need_caps}", f"got {len(caps)}")
    if kind == "full":
        rep.add(len(projs) >= 3, "projects >= 3", f"got {len(projs)}")

    # ---- per-chapter depth, aggregated ----
    bad = []
    for c, fm in zip(chaps, fronts):
        pt = parts.get(fm.get("part"), "")
        for ok, crit, _ in check_chapter(c, kind, pt):
            if not ok:
                bad.append(f"{c.name}: {crit}")
    rep.add(not bad, "per-chapter depth on every chapter",
            "" if not bad else f"{len(bad)} issue(s), first: {bad[0]}")

    # ---- verification ----
    harness = lang_dir / "tools" / "verify_examples.py"
    rep.add(harness.exists(), "tools/verify_examples.py exists", "")
    style = (lang_dir / "STYLE.md")
    rep.add(style.exists() and "run" in style.read_text(encoding="utf-8"),
            "STYLE.md documents directives", "")

    if run_harness and harness.exists():
        py = sys.executable
        try:
            st = subprocess.run([py, str(harness), "--self-test"], capture_output=True,
                                text=True, timeout=600, cwd=lang_dir)
            rep.add(st.returncode == 0, "harness --self-test passes",
                    "" if st.returncode == 0 else st.stdout.strip().split("\n")[-1][:70])
        except subprocess.TimeoutExpired:
            rep.add(False, "harness --self-test passes", "timed out")
        try:
            run = subprocess.run([py, str(harness)], capture_output=True, text=True,
                                 timeout=900, cwd=lang_dir)
            tail = run.stdout.strip().split("\n")[-1] if run.stdout.strip() else ""
            rep.add(run.returncode == 0, "harness reports 0 failures", tail[:80])
        except subprocess.TimeoutExpired:
            rep.add(False, "harness reports 0 failures", "timed out")
    elif run_harness:
        rep.add(False, "harness --self-test passes", "no harness")
    else:
        rep.add(True, "harness checks", "skipped (--no-verify)")

    return rep


# --------------------------------------------------------------------------
# self-test: the checker must be able to fail
# --------------------------------------------------------------------------
def self_test() -> int:
    """Two claims, each with a partner that must not pass."""
    print("check-standard self-test")
    ok = True

    # 1. A chapter with nothing in it must be flagged on every depth criterion.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        thin = Path(td) / "01-thin.md"
        thin.write_text("---\nchapter: 1\npart: 1\ntitle: Thin\n---\n\nJust prose.\n",
                        encoding="utf-8")
        issues = [c for o, c, _ in check_chapter(thin, "full") if not o]
        print(f"  thin chapter flagged on {len(issues)} criteria: {issues[:4]}")
        if len(issues) < 5:
            print("  FAIL: a chapter with no takeaways, practice, pitfall or code passed")
            ok = False

        rich = Path(td) / "02-rich.md"
        body = ["---", "chapter: 2", "part: 1", "title: Rich", "summary: s",
                "minutes: 30", "tags: [a]", "---", ""]
        body += ["```python run", "print(1)", "```", ""]
        body += [":::scenario S", "text", ":::solution", "fix", ":::", ":::pitfall P", "text", ":::", ""]
        body += ["## Key takeaways"] + [f"- point {i}" for i in range(7)] + [""]
        body += ["## Practice"] + [f"- [ ] ex {i}" for i in range(5)] + [""]
        rich.write_text("\n".join(body), encoding="utf-8")
        issues = [c for o, c, _ in check_chapter(rich, "full") if not o]
        print(f"  rich chapter flagged on {len(issues)} criteria: {issues}")
        if issues:
            print("  FAIL: a conforming chapter was flagged")
            ok = False

    # 2. Layer classification must find a layer when named and not when absent.
    for title, layer, want in (("VIII · Algorithms & Complexity", "cost", True),
                               ("IX · Security", "security", True),
                               ("V · Track B · Game", "security", False)):
        low = title.lower()
        got = any(m in low for m in LAYER_MARKERS[layer])
        status = "ok" if got == want else "FAIL"
        print(f"  {status}: {title!r} -> layer {layer} = {got} (want {want})")
        if got != want:
            ok = False

    print("\nself-test " + ("PASSED -- the checker catches what it claims" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tracks", nargs="*", help="track ids; default all with chapters/")
    ap.add_argument("--no-verify", action="store_true", help="skip running each harness")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    langs = json.loads(REGISTRY.read_text(encoding="utf-8"))["languages"]
    if args.tracks:
        langs = [l for l in langs if l["id"] in args.tracks]
    else:
        langs = [l for l in langs if (PLATFORM / l["id"] / "chapters").is_dir()]

    if not langs:
        print("no tracks with chapters/ to check")
        return 0

    results = [check_track(l, not args.no_verify) for l in langs]
    print("=" * 72)
    for r in results:
        r.show()
    print("\n" + "=" * 72)
    failing = [r for r in results if r.failures]
    print(f"{len(results) - len(failing)}/{len(results)} track(s) conform to TRACK-STANDARD.md")
    for r in failing:
        print(f"  FAIL {r.track} [{r.kind}] — {len(r.failures)} unmet criterion(a)")
    return 0 if not failing else 1


if __name__ == "__main__":
    sys.exit(main())
