#!/usr/bin/env python3
"""Capture real output and diagnostics for chapter 39 (HTML templates)."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
TIMEOUT = 90


def run(name: str):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror", "-o", exe, str(HERE / name)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            print(f"--- {name}: BUILD FAILED ---")
            print(b.stderr[:1500])
            return None, None, b.returncode
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return r.stdout, r.stderr, r.returncode


def diagnostic(name: str):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(HERE / name)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return b.stderr, b.returncode


for t in sys.argv[1:] or ["naive.cpp", "escape.cpp", "order.cpp", "attr.cpp",
                          "template.cpp", "truncate.cpp", "types.cpp"]:
    out, err, rc = run(t)
    print(f"===== {t} (rc={rc}) =====")
    sys.stdout.write(out or "")
    if err.strip():
        print("-- stderr --")
        sys.stdout.write(err[:600])
    print()

blob, rc = diagnostic("types_bad.cpp")
print(f"===== types_bad.cpp (must be rejected, rc={rc}) =====")
for line in blob.splitlines():
    if "error:" in line:
        print("  " + re.sub(r"^.*error:", "error:", line).strip()[:220])
print()
