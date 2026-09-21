#!/usr/bin/env python3
"""Capture the real evidence for ch16: sanitizer verdicts and shell transcripts."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CC = "clang"
C_BASE = ["-std=c17", "-Wall", "-Wextra"]


def run_san(path: Path):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CC] + C_BASE + ["-Werror", "-fsanitize=address,undefined",
                               "-fno-omit-frame-pointer", "-g", "-o", exe, str(path)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=30)
        if b.returncode != 0:
            return None, "BUILD FAILED:\n" + b.stderr, -1
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=25, env=env)
        return r.stdout, r.stderr, r.returncode


def run_plain(path: Path, san=False):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CC] + C_BASE + ["-Werror"]
        if san:
            cmd += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
        cmd += ["-o", exe, str(path)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=30)
        if b.returncode != 0:
            return None, "BUILD FAILED:\n" + b.stderr, -1
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=25, env=env)
        return r.stdout, r.stderr, r.returncode


def diag(path: Path):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CC] + C_BASE + ["-o", exe, str(path)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=30)
        return b.returncode, b.stderr


def shell(script: Path):
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(["sh", str(script)], text=True, capture_output=True,
                           cwd=td, timeout=30)
        return r.stdout, r.stderr, r.returncode


print("### run-san-catch candidates ###")
for f in ["signed_ovf.c", "shift.c", "oob.c", "uaf.c", "doublefree.c", "nullderef.c"]:
    out, err, rc = run_san(HERE / f)
    print(f"===== {f}  rc={rc} =====")
    if out:
        print("-- stdout --"); print(out.rstrip())
    print("-- stderr (first 8 lines) --")
    print("\n".join(err.strip().splitlines()[:8]))
    print()

print("### run / run-san (must be clean) ###")
for f, san in [("unsigned_wrap.c", True), ("clean.c", True), ("alias.c", False)]:
    out, err, rc = run_plain(HERE / f, san=san)
    print(f"===== {f} san={san} rc={rc} =====")
    print("-- stdout --"); print(out.rstrip() if out else "(none)")
    if err.strip():
        print("-- stderr --"); print("\n".join(err.strip().splitlines()[:5]))
    print()

print("### warn ###")
rc, err = diag(HERE / "uninit.c")
print(f"===== uninit.c rc={rc} =====")
print(err.strip()[:600])
print()

print("### shell ###")
for s in ["opt.sh", "ubexit.sh"]:
    out, err, rc = shell(HERE / s)
    print(f"===== {s} rc={rc} =====")
    print("-- stdout --"); print(out.rstrip())
    if err.strip():
        print("-- stderr --"); print(err.strip()[:300])
    print()
