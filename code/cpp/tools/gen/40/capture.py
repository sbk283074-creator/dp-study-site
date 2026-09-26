#!/usr/bin/env python3
"""Capture real output and diagnostics for chapter 40 (concurrency)."""
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
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 90


def run(name: str, sanitize: bool = False):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror"] + (SAN if sanitize else []) + ["-o", exe, str(HERE / name)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            print(f"--- {name}: BUILD FAILED ---")
            print(b.stderr[:1200])
            return None, None, b.returncode
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT, env=env)
        return r.stdout, r.stderr, r.returncode


def diagnostic(name: str):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(HERE / name)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return b.stderr, b.returncode


for t in sys.argv[1:] or ["join.cpp", "capture.cpp", "mutex.cpp", "scoped.cpp",
                          "deadlock.cpp", "atomic.cpp", "tls.cpp", "futures.cpp"]:
    out, err, rc = run(t)
    print(f"===== {t} (rc={rc}) =====")
    sys.stdout.write(out or "")
    if (err or "").strip():
        print("-- stderr --")
        sys.stdout.write((err or "")[:500])
    print()

for t in ["capture_bad.cpp", "dangling.cpp"]:
    out, err, rc = run(t, sanitize=True)
    print(f"===== {t} (sanitized, rc={rc}) =====")
    sys.stdout.write(out or "")
    for line in (err or "").splitlines():
        if "ERROR" in line or "SUMMARY" in line:
            print("  " + line.strip()[:150])
    print()

with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(["sh", str(HERE / "race.sh")], text=True, capture_output=True,
                       cwd=td, timeout=180)
    print(f"===== race.sh (rc={r.returncode}) =====")
    sys.stdout.write(r.stdout)
    if r.stderr.strip():
        print("-- stderr --")
        sys.stdout.write(r.stderr[:400])
    print()

blob, rc = diagnostic("badmutex.cpp")
print(f"===== badmutex.cpp (must be rejected, rc={rc}) =====")
for line in blob.splitlines():
    if "error:" in line:
        print("  " + re.sub(r"^.*error:", "error:", line).strip()[:200])
print()
