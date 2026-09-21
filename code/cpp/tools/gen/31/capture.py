#!/usr/bin/env python3
"""Build and run every ch31 source, printing what each really produced.

Exploration only: the authority is tools/gen/31/gen.py, which embeds these
same measurements into the chapter.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]


def run(name: str, sanitize: bool = False, werror: bool = True):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + (["-Werror"] if werror else []) + \
              (SAN if sanitize else []) + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=60)
        if b.returncode != 0:
            print(f"--- {name}: BUILD FAILED (rc={b.returncode}) ---")
            for line in b.stderr.strip().splitlines()[:6]:
                print("   ", line)
            print()
            return None
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td,
                           timeout=30, env=env)
        print(f"--- {name}: rc={r.returncode} ---")
        if r.stdout:
            print("STDOUT:")
            for line in r.stdout.rstrip("\n").splitlines():
                print("   ", line)
        if r.stderr.strip():
            print("STDERR (first 6):")
            for line in r.stderr.strip().splitlines()[:6]:
                print("   ", line)
        print()
        return r


if __name__ == "__main__":
    for f in ["noops.cpp", "vec2.cpp", "stream.cpp", "compound.cpp",
              "subscript.cpp", "functor.cpp", "arrow.cpp", "shortcircuit.cpp",
              "fixedvec.cpp", "ring.cpp", "traits.cpp"]:
        run(f)
    for f in ["member_only.cpp", "newop.cpp", "eqonly.cpp", "stream_member.cpp",
              "chain.cpp", "sortrange.cpp", "notiter.cpp"]:
        run(f, werror=False)
    run("invalidate.cpp", sanitize=True)
