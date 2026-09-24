#!/usr/bin/env python3
"""Sweep one chapter's generator sources.

    python3 tools/gen/sweep.py 04

For every `<Name>.java` in the directory it compiles with the gate's own flags
(`-Xlint:all -Werror --release 21`), runs it twice, and reports one line per file:
compile status, exit code, stderr size, the widest output line, and whether the
output was identical across the two runs.

Then it prints each program's stdout in full. The summary proves a program
*runs*; only reading its output proves it says what the chapter is about to
claim. That second step is the one that catches a wrong table, and it is not
automatable.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import javagen as J  # noqa: E402


def build(work: Path, fname: str, werror: bool):
    cmd = [J.JAVAC, "-Xlint:all", f"--release={J.RELEASE}"]
    if werror:
        cmd.append("-Werror")
    cmd += ["-d", "out", fname]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=work, timeout=60)


def probe(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    cls = J.gate.main_class_of(src)
    if cls is None:
        return {"name": path.name, "note": "no type declaration"}
    fname = cls.split(".")[-1] + ".java"
    row: dict = {"name": path.name, "cls": cls}
    runs = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            (work / fname).write_text(src if src.endswith("\n") else src + "\n", encoding="utf-8")
            c = build(work, fname, werror=True)
            if c.returncode != 0:
                row["compile"] = "REJECTED"
                row["diag"] = c.stderr
                # a second attempt without -Werror separates "warns" from "errors"
                c2 = build(work, fname, werror=False)
                row["warns_only"] = c2.returncode == 0
                return row
            row["compile"] = "ok"
            r = subprocess.run([J.JAVA, "-cp", "out", cls], capture_output=True,
                               text=True, cwd=work, timeout=60)
            runs.append((r.returncode, r.stdout, r.stderr))
    (rc1, out1, err1), (rc2, out2, _) = runs
    row["rc"] = rc1
    row["stderr"] = len(err1.strip())
    row["maxw"] = max((len(line) for line in out1.splitlines()), default=0)
    row["stable"] = "stable" if out1 == out2 else "UNSTABLE"
    row["stdout"] = out1
    row["err"] = err1
    # what the same file says without -Werror: a warning worth quoting in a `warn` block
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        (work / fname).write_text(src if src.endswith("\n") else src + "\n", encoding="utf-8")
        c2 = build(work, fname, werror=False)
        row["warn_text"] = c2.stderr.strip()
    return row


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    dirs = argv or [p.name for p in sorted(here.iterdir()) if p.is_dir() and p.name.isdigit()]
    for d in dirs:
        where = here / d
        if not where.is_dir():
            raise SystemExit(f"no such generator directory: {where}")
        print(f"\n===== gen/{d} =====")
        for path in sorted(where.glob("*.java")):
            row = probe(path)
            if "note" in row:
                print(f"{row['name']:<24} {row['note']}")
                continue
            if row["compile"] == "REJECTED":
                kind = "warns (no -Werror)" if row.get("warns_only") else "rejected by javac"
                print(f"{row['name']:<24} {kind}")
                for line in row["diag"].splitlines():
                    if "error:" in line or "warning:" in line:
                        print("    " + J.LOCATION_RE.sub("", line.strip())[:110])
                continue
            flag = "" if row["stable"] == "stable" else "   <-- UNSTABLE"
            warn = ""
            if row.get("warn_text"):
                first = row["warn_text"].splitlines()[0]
                warn = "   [warns: " + J.LOCATION_RE.sub("", first.strip())[:70] + "]"
            print(f"{row['name']:<24} rc={row['rc']} stderr={row['stderr']} "
                  f"maxw={row['maxw']} {row['stable']}{flag}{warn}")
        print("\n--- output ---")
        for path in sorted(where.glob("*.java")):
            row = probe(path)
            if row.get("stdout"):
                print(f"\n### {row['name']}")
                sys.stdout.write(row["stdout"])
            if row.get("err", "").strip():
                print(f"\n### {row['name']} -- stderr --")
                sys.stdout.write(row["err"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
