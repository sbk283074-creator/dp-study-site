#!/usr/bin/env python3
"""Capture the real evidence for ch15. Prints every diagnostic and transcript.

Run before writing prose, so the chapter quotes measured values rather than
guessed ones. Mirrors what tools/verify_examples.py will do.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CC, CXX = "clang", "clang++"
CFLAGS = ["-std=c17", "-Wall", "-Wextra"]
CXXFLAGS = ["-std=c++17", "-Wall", "-Wextra"]


def run_c(src: Path, werror=True):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CC] + CFLAGS + (["-Werror"] if werror else []) + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td)
        if b.returncode != 0:
            return None, b.stderr, b.returncode
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=20)
        return r.stdout, r.stderr, r.returncode


def run_cxx(src: Path):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + CXXFLAGS + ["-Werror", "-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td)
        if b.returncode != 0:
            return None, b.stderr, b.returncode
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=20)
        return r.stdout, r.stderr, r.returncode


def show(label: str, src: str, kind="c"):
    p = HERE / src
    out, err, rc = (run_c(p) if kind == "c" else run_cxx(p))
    print(f"===== {label} ({src}) rc={rc} =====")
    if out is None:
        print("-- BUILD FAILED --")
        print(err.strip()[:900])
    else:
        print("-- stdout --")
        print(out.rstrip())
        if err.strip():
            print("-- stderr --")
            print(err.strip()[:600])
    print()


print("### run blocks ###")
for f in ["subst.c", "noparen.c", "sideeffect.c", "strpaste.c", "dowhile.c",
          "cond.c", "predef.c"]:
    show(f, f)

print("### cpp block ###")
show("vs_cpp", "vs_cpp.cpp", "cxx")

print("### bad blocks (no -Werror) ###")
for f in ["dangle.c", "error_demo.c", "toofew.c"]:
    p = HERE / f
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CC] + CFLAGS + ["-o", exe, str(p)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td)
        print(f"===== {f} rc={b.returncode} =====")
        print(b.stderr.strip()[:700])
        print()

print("### warn block (no -Werror) ###")
p = HERE / "redef.c"
with tempfile.TemporaryDirectory() as td:
    exe = os.path.join(td, "prog")
    cmd = [CC] + CFLAGS + ["-o", exe, str(p)]
    b = subprocess.run(cmd, text=True, capture_output=True, cwd=td)
    print(f"===== redef.c rc={b.returncode} =====")
    print(b.stderr.strip()[:700])
    print()
