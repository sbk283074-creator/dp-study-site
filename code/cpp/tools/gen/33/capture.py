#!/usr/bin/env python3
"""Build and run every ch33 source, printing what each really produced.

Exploration only: the authority is tools/gen/33/gen.py, which embeds these
same measurements into the chapter. Everything here is C++23 unless noted.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CXX = "clang++"
BASE = ["-std=c++23", "-Wall", "-Wextra"]


def run(name: str, werror: bool = True, sanitize: bool = False):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + (["-Werror"] if werror else []) + \
              (["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
               if sanitize else []) + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=90)
        if b.returncode != 0:
            print(f"--- {name}: BUILD FAILED (rc={b.returncode}) ---")
            for line in b.stderr.strip().splitlines()[:8]:
                print("   ", line)
            print()
            return
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td,
                           timeout=30, env=env)
        print(f"--- {name}: rc={r.returncode} ---")
        if r.stdout:
            for line in r.stdout.rstrip("\n").splitlines():
                print("   ", line)
        if r.stderr.strip():
            print("   STDERR:")
            for line in r.stderr.strip().splitlines()[:5]:
                print("     ", line)
        print()


def shell(name: str):
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(["sh", str(HERE / name)], text=True, capture_output=True,
                           cwd=td, timeout=90)
        print(f"--- {name}: rc={r.returncode} ---")
        for line in r.stdout.rstrip("\n").splitlines():
            print("   ", line)
        if r.stderr.strip():
            print("   STDERR:")
            for line in r.stderr.strip().splitlines()[:5]:
                print("     ", line)
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for n in sys.argv[1:]:
            if n.endswith(".sh"):
                shell(n)
            else:
                run(n, werror=not n.startswith(("concept_violation", "format_bad")),
                    sanitize=n.startswith("span_dangle"))
            if n == "expected_throw.cpp":
                pass
        sys.exit(0)

    shell("stdcheck.sh")
    shell("features.sh")
    for n in ["concept.cpp", "overload.cpp", "span.cpp", "ranges.cpp", "lazy.cpp",
              "format.cpp", "spaceship.cpp", "expected.cpp", "designated.cpp"]:
        run(n)
    for n in ["concept_violation.cpp", "format_bad.cpp"]:
        run(n, werror=False)
    run("span_dangle.cpp", sanitize=True)
    run("expected_throw.cpp")
