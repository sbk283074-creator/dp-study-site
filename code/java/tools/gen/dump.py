#!/usr/bin/env python3
"""Dump one chapter's program output, once each.

    python3 tools/gen/dump.py 17 18

`verify_examples.py` is the oracle and `sweep.py` is the stability probe; both are
expensive (the harness re-runs every block, and the sweep compiles and runs each
program twice to compare). This is the cheap read: compile once with the gate's
flags, run once, print stdout. Use it to see what a chapter's fixtures actually
say before writing the prose that quotes them.

It proves nothing about stability or about whether a fence matches. Confirm with
`verify_examples.py <NN>-` before assembling, and with `sweep.py` when a block's
value comes from anything a clock or a hash could move.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import javagen as J  # noqa: E402

COMPILE_TIMEOUT = 120
RUN_TIMEOUT = 60


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("usage: dump.py <NN> [NN ...]")
    for d in argv:
        where = HERE / d
        if not where.is_dir():
            raise SystemExit(f"no such generator directory: {where}")
        print(f"\n===== gen/{d} =====")
        for path in sorted(where.glob("*.java")):
            src = path.read_text(encoding="utf-8")
            cls = J.gate.main_class_of(src)
            if cls is None:
                print(f"\n### {path.name} -- no type declaration")
                continue
            fname = cls.split(".")[-1] + ".java"
            with tempfile.TemporaryDirectory() as td:
                work = Path(td)
                (work / fname).write_text(
                    src if src.endswith("\n") else src + "\n", encoding="utf-8")
                c = subprocess.run(
                    [J.JAVAC, "-Xlint:all", "-Werror", f"--release={J.RELEASE}",
                     "-d", "out", fname],
                    capture_output=True, text=True, cwd=work, timeout=COMPILE_TIMEOUT)
                if c.returncode != 0:
                    print(f"\n### {path.name} -- REJECTED by javac --")
                    print(J.LOCATION_RE.sub("", c.stderr.strip())[:1200])
                    continue
                r = subprocess.run([J.JAVA, "-cp", "out", cls], capture_output=True,
                                   text=True, cwd=work, timeout=RUN_TIMEOUT)
                print(f"\n### {path.name}  rc={r.returncode}")
                sys.stdout.write(r.stdout)
                if r.stderr.strip():
                    print("-- stderr --")
                    sys.stdout.write(r.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
