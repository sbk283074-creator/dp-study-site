#!/usr/bin/env python3
"""Build and run every ch32 source, printing what each really produced.

Exploration only: the authority is tools/gen/32/gen.py, which embeds these
same measurements into the chapter.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]


def run(name: str, werror: bool = True):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + (["-Werror"] if werror else []) + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=60)
        if b.returncode != 0:
            print(f"--- {name}: BUILD FAILED (rc={b.returncode}) ---")
            for line in b.stderr.strip().splitlines()[:8]:
                print("   ", line)
            print()
            return
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=30)
        print(f"--- {name}: rc={r.returncode} ---")
        if r.stdout:
            for line in r.stdout.rstrip("\n").splitlines():
                print("   ", line)
        if r.stderr.strip():
            print("   STDERR:", r.stderr.strip()[:300])
        print()


if __name__ == "__main__":
    names = sys.argv[1:] or ["categories.cpp", "tracked.cpp", "constmove.cpp",
                             "nomove_return.cpp", "collapse.cpp", "universal.cpp",
                             "forward.cpp", "mymove.cpp", "moveonly.cpp",
                             "autorr.cpp", "vecgrowth.cpp"]
    for n in names:
        run(n)
    for n in ["bindrvalue.cpp", "movefail.cpp"]:
        run(n, werror=False)
