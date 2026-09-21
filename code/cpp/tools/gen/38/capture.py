#!/usr/bin/env python3
"""Capture real output and diagnostics for chapter 38 (SQLite)."""
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
LIBS = ["-lsqlite3"]
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 90


def run(name: str, sanitize: bool = False):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror"] + (SAN if sanitize else []) + \
              ["-o", exe, str(HERE / name)] + LIBS
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            print(f"--- {name}: BUILD FAILED (rc={b.returncode}) ---")
            print(b.stderr[:1500])
            return None, None, b.returncode
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td,
                           timeout=TIMEOUT, env=env)
        return r.stdout, r.stderr, r.returncode


def diagnostic(name: str):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(HERE / name)] + LIBS
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return b.stderr, b.returncode


def show(label: str, out, err=None, rc=None):
    print(f"===== {label} =====")
    if out is None:
        print("(no build)")
    else:
        sys.stdout.write(out)
    if err:
        print(f"-- stderr (rc={rc}) --")
        sys.stdout.write(err[:1200])
    print()


targets = sys.argv[1:] or ["version.cpp", "exec.cpp", "inject.cpp", "prepare.cpp",
                           "affinity.cpp", "fk.cpp", "atomic.cpp", "nul.cpp",
                           "named.cpp", "errmsg.cpp", "durable.cpp"]

for t in targets:
    out, err, rc = run(t)
    print(f"===== {t} (rc={rc}) =====")
    sys.stdout.write(out or "")
    if err.strip():
        print("-- stderr --")
        sys.stdout.write(err[:800])
    print()

print("===== static_dangle.cpp (sanitized, must be caught) =====")
out, err, rc = run("static_dangle.cpp", sanitize=True)
sys.stdout.write(out or "")
print(f"rc={rc}")
for line in (err or "").splitlines():
    if "ERROR" in line or "SUMMARY" in line or "runtime error" in line:
        print("  " + line.strip()[:160])
print()

blob, rc = diagnostic("badbind.cpp")
print(f"===== badbind.cpp (must be rejected, rc={rc}) =====")
for line in blob.splitlines():
    if "error:" in line:
        print("  " + re.sub(r"^.*error:", "error:", line).strip()[:200])
print()
