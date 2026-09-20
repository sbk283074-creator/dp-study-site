#!/usr/bin/env python3
"""Compile and run every C/C++ example in the book, and prove the bad ones are bad.

This is the gate that makes the book's central promise checkable: *no example is
taught that has not been built and run*. It reads the fence directives described
in `code/cpp/STYLE.md`:

    ```cpp run           complete program -> compile (-Wall -Wextra -Werror) + run
                         stdout must equal the `text` fence that follows it
    ```cpp run-san       same, plus -fsanitize=address,undefined; must run CLEAN
    ```cpp run-san-catch must be CAUGHT: a non-zero exit or a sanitizer report, and
                         the `text` fence must appear in that report
    ```cpp run-san-leak  must leak. Leak detection is unavailable on macOS, so there
                         it is reported SKIPPED rather than passed
    ```cpp compile       complete program -> compile only (needs stdin, sockets, ...)
    ```cpp bad           MUST NOT COMPILE. Compiles => the gate fails. A "don't do
                         this" example that actually compiles teaches nothing. A
                         following `text` fence, if present, must appear inside the
                         real diagnostic - so a quoted error is verified too.
    ```cpp               a fragment; deliberately not compiled (keep these rare)

`c` is accepted wherever `cpp` is; it selects -std=c17 and the C driver.

Usage
    python3 code/cpp/tools/verify_examples.py              # every chapter
    python3 code/cpp/tools/verify_examples.py 07-pointers  # one chapter (substring)
    python3 code/cpp/tools/verify_examples.py -v           # show every block
    python3 code/cpp/tools/verify_examples.py --dir code/cpp/tools/fixtures good

Exit status is 0 only when every block behaved as declared. A SKIPPED block does
not fail the run but is always printed, so the gap is visible rather than implied.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent / "chapters"

CPP_STD = "c++17"
C_STD = "c17"
RUN_TIMEOUT = 20  # seconds
SAN_FLAGS = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]


# --------------------------------------------------------------------------
# Compilers, and what this platform can actually detect
# --------------------------------------------------------------------------
def pick_compilers(prefer_cxx: str | None) -> tuple[str | None, str | None]:
    """Return (C++ driver, C driver). They are not interchangeable: feeding a .c
    file to clang++ compiles it as C++ and warns -Wdeprecated, which -Werror turns
    into a hard failure."""
    cxx_names = ([prefer_cxx] if prefer_cxx else []) + ["clang++", "g++", "c++"]
    cxx = next((p for p in (shutil.which(n) for n in cxx_names) if p), None)
    cc = next((p for p in (shutil.which(n) for n in ["clang", "gcc", "cc"]) if p), None)
    return cxx, cc


def sanitizer_env() -> dict:
    env = dict(os.environ)
    # Apple's ASan rejects detect_leaks outright ("not supported on this
    # platform") and aborts, which would look like a caught bug. Ask for it only
    # where it exists.
    if sys.platform == "darwin":
        env["ASAN_OPTIONS"] = "abort_on_error=0"
    else:
        env["ASAN_OPTIONS"] = "detect_leaks=1:abort_on_error=0"
    env["UBSAN_OPTIONS"] = "print_stacktrace=0"
    return env


def probe_leak_detection(cxx: str) -> bool:
    """Can this toolchain actually report a leak? Ask it, do not assume."""
    if sys.platform == "darwin":
        # Apple clang ships no LeakSanitizer; skip the compile to save a second.
        return False
    with tempfile.TemporaryDirectory(prefix="leakprobe-") as td:
        src = Path(td) / "p.cpp"
        src.write_text("int main(){ int*p=new int[4]; p[0]=1; return p[0]-1; }\n", encoding="utf-8")
        exe = Path(td) / "p"
        build = subprocess.run([cxx, "-std=c++17", "-fsanitize=address", "-g",
                                "-o", str(exe), str(src)], capture_output=True, text=True)
        if build.returncode != 0:
            return False
        try:
            run = subprocess.run([str(exe)], capture_output=True, text=True,
                                 timeout=RUN_TIMEOUT, env=sanitizer_env(), cwd=td)
        except subprocess.TimeoutExpired:
            return False
        blob = run.stderr or ""
        if "not supported on this platform" in blob:
            return False
        return run.returncode != 0 or "leak" in blob.lower()


# --------------------------------------------------------------------------
# Parsing chapters
# --------------------------------------------------------------------------
class Block:
    __slots__ = ("chapter", "line", "lang", "directive", "code", "expected")

    def __init__(self, chapter, line, lang, directive, code, expected=None):
        self.chapter = chapter
        self.line = line
        self.lang = lang
        self.directive = directive
        self.code = code
        self.expected = expected

    @property
    def where(self) -> str:
        return f"{self.chapter}:{self.line}"

    @property
    def is_c(self) -> bool:
        return self.lang in ("c", "h")

    @property
    def standard(self) -> str:
        return C_STD if self.is_c else CPP_STD


FENCE_RE = re.compile(r"^(\s*)```(.*)$")
# Directives whose following `text` fence is a CLAIM to be verified, not decoration.
# `bad` is in here because a chapter that quotes a compiler error must quote the one
# it actually got; otherwise the "don't do this" example is unverified prose.
WITH_OUTPUT = ("run", "run-san", "run-san-catch", "run-san-leak", "warn", "bad")


def parse_chapter(path: Path) -> list[Block]:
    """Pull every fenced block out of one chapter, in order."""
    lines = path.read_text(encoding="utf-8").split("\n")
    blocks: list[Block] = []
    i = 0

    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1  # step past the closing ---

    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue

        indent, info = m.group(1), m.group(2).strip()
        open_line = i + 1
        i += 1

        body: list[str] = []
        while i < len(lines) and not lines[i].strip().startswith("```"):
            text = lines[i]
            # De-indent, so a fence nested inside a callout still compiles.
            if indent and text.startswith(indent):
                text = text[len(indent):]
            body.append(text)
            i += 1
        i += 1  # step past the closing fence

        parts = info.split()
        lang = parts[0].lower() if parts else ""
        directive = parts[1].lower() if len(parts) > 1 else ""

        if lang not in ("cpp", "c", "h"):
            continue

        # A run block may be followed by a `text` fence holding its expected
        # output. Consume it only for directives that produce output.
        expected = None
        if directive in WITH_OUTPUT:
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                m2 = FENCE_RE.match(lines[j])
                if m2 and m2.group(2).strip().split()[:1] == ["text"]:
                    ind2 = m2.group(1)
                    j += 1
                    exp: list[str] = []
                    while j < len(lines) and not lines[j].strip().startswith("```"):
                        t = lines[j]
                        if ind2 and t.startswith(ind2):
                            t = t[len(ind2):]
                        exp.append(t)
                        j += 1
                    expected = "\n".join(exp)
                    i = j + 1  # consume it, so it is not parsed again

        blocks.append(Block(path.stem, open_line, lang, directive, "\n".join(body), expected))
    return blocks


# --------------------------------------------------------------------------
# Comparing output
# --------------------------------------------------------------------------
def norm(text: str) -> str:
    """Trailing whitespace and trailing newlines are not part of the claim."""
    return "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").split("\n")).strip("\n")


def squash(text: str) -> str:
    """Whitespace-insensitive form, for matching sanitizer reports."""
    return re.sub(r"\s+", " ", text).strip()


def desrc(text: str) -> str:
    """Replace source-file paths with a placeholder.

    Every block is compiled from a temp file whose name and directory change
    between runs, so a diagnostic quoted in a chapter can never match literally.
    The *wording* of the diagnostic is the claim being verified, not the path.
    """
    return re.sub(r"[^\s:'\"]*\.(?:c|cpp|h)\b", "SRC", text)


def matches(expected: str, actual: str) -> bool:
    """Is the documented diagnostic/output present in what we actually got?"""
    return squash(desrc(expected)) in squash(desrc(actual))


# --------------------------------------------------------------------------
# Running one block
# --------------------------------------------------------------------------
class Result:
    __slots__ = ("block", "ok", "note", "detail", "skipped")

    def __init__(self, block, ok, note, detail="", skipped=False):
        self.block = block
        self.ok = ok
        self.note = note
        self.detail = detail
        self.skipped = skipped


def build(block: Block, driver: str, work: Path, sanitize: bool, werror: bool):
    exe = work / "prog"
    cmd = [driver, f"-std={block.standard}", "-Wall", "-Wextra"]
    if werror:
        cmd.append("-Werror")
    if sanitize:
        cmd += SAN_FLAGS
    src = work / ("prog.c" if block.is_c else "prog.cpp")
    src.write_text(block.code + "\n", encoding="utf-8")
    cmd += ["-o", str(exe), str(src)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180), exe


def check_block(block: Block, cxx: str, cc: str, leak_ok: bool) -> Result:
    d = block.directive
    if not d:
        return Result(block, True, "fragment (not compiled)")

    driver = cc if block.is_c else cxx
    if not driver:
        return Result(block, False, f"no {'C' if block.is_c else 'C++'} compiler on PATH")

    with tempfile.TemporaryDirectory(prefix="cppverify-") as td:
        work = Path(td)

        if d == "bad":
            # Deliberately no -Werror: a `bad` block must fail on a real *error*,
            # not on a promoted warning, or the assertion passes for the wrong
            # reason and teaches nothing.
            try:
                proc, _ = build(block, driver, work, sanitize=False, werror=False)
            except subprocess.TimeoutExpired:
                return Result(block, False, "compiler timed out")
            if proc.returncode == 0:
                return Result(block, False, "EXPECTED A COMPILE ERROR, but it built cleanly")
            if "error:" not in proc.stderr:
                return Result(block, False, "failed, but with no 'error:' in the diagnostic",
                              proc.stderr.strip()[:400])
            if block.expected and not matches(block.expected, proc.stderr):
                return Result(block, False,
                              "the diagnostic does not contain the documented phrase",
                              "documented: " + squash(block.expected)[:220]
                              + "\n\nactual: " + squash(proc.stderr)[:400])
            first = next((l for l in proc.stderr.splitlines() if "error:" in l), "")
            return Result(block, True, "correctly rejected", first.strip()[:160])

        if d == "warn":
            # A diagnostic the compiler emits but does not treat as fatal by
            # default - -Wformat, -Wunused-variable, and friends. Compiled with
            # -Wall -Wextra and NO -Werror, because the point of the block is that
            # this is a warning you have to opt into making fatal. The `text`
            # fence, if present, must appear inside the message.
            try:
                proc, _ = build(block, driver, work, sanitize=False, werror=False)
            except subprocess.TimeoutExpired:
                return Result(block, False, "compiler timed out")
            blob = proc.stderr or ""
            if "warning:" not in blob and "error:" not in blob:
                return Result(block, False,
                              "EXPECTED a diagnostic, but the compiler was silent",
                              "build exit=" + str(proc.returncode))
            if block.expected and not matches(block.expected, blob):
                return Result(block, False,
                              "the diagnostic does not contain the documented phrase",
                              "documented: " + squash(block.expected)[:220]
                              + "\n\nactual: " + squash(blob)[:400])
            first = next((l for l in blob.splitlines()
                          if "warning:" in l or "error:" in l), "")
            return Result(block, True, "diagnostic emitted, as documented",
                          first.strip()[:170])

        if d == "compile":
            try:
                proc, _ = build(block, driver, work, sanitize=False, werror=True)
            except subprocess.TimeoutExpired:
                return Result(block, False, "compiler timed out")
            if proc.returncode != 0:
                return Result(block, False, "does not compile", proc.stderr.strip()[:600])
            return Result(block, True, "compiles clean (-Wall -Wextra -Werror)")

        if d in ("run", "run-san", "run-san-catch", "run-san-leak"):
            sanitize = d != "run"

            if d == "run-san-leak" and not leak_ok:
                return Result(block, True,
                              "SKIPPED — this platform has no leak detection "
                              "(macOS ships no LeakSanitizer; use Linux or valgrind)",
                              skipped=True)

            try:
                proc, exe = build(block, driver, work, sanitize=sanitize, werror=True)
            except subprocess.TimeoutExpired:
                return Result(block, False, "compiler timed out")
            if proc.returncode != 0:
                return Result(block, False, "does not compile", proc.stderr.strip()[:600])

            try:
                run = subprocess.run([str(exe)], capture_output=True, text=True,
                                     timeout=RUN_TIMEOUT, env=sanitizer_env(), cwd=work)
            except subprocess.TimeoutExpired:
                return Result(block, False, f"ran longer than {RUN_TIMEOUT}s (infinite loop?)")

            err = run.stderr or ""

            # A sanitizer that refuses to run is an environment problem, never a
            # "caught the bug" result.
            if "not supported on this platform" in err:
                return Result(block, False, "the sanitizer refused to run here",
                              squash(err)[:300])

            if d in ("run-san-catch", "run-san-leak"):
                caught = run.returncode != 0 or "runtime error" in err or "ERROR: " in err \
                    or "SUMMARY: " in err
                if not caught:
                    return Result(block, False,
                                  "EXPECTED a sanitizer report, but the run was clean")
                if block.expected and not matches(block.expected, err):
                    return Result(block, False,
                                  "the sanitizer report does not contain the documented phrase",
                                  "documented: " + squash(block.expected)[:200]
                                  + "\n\nactual: " + squash(err)[:300])
                return Result(block, True, "caught by the sanitizer, as documented")

            if run.returncode != 0:
                return Result(block, False, f"exited {run.returncode}",
                              "\n".join((err or "").strip().splitlines()[-6:])[:600])
            if d == "run-san" and ("runtime error" in err or "ERROR: " in err):
                return Result(block, False, "sanitizer reported a problem on a run-san block",
                              squash(err)[:400])

            if block.expected is None:
                return Result(block, True, "ran clean (no output fence to compare)")
            if norm(run.stdout) != norm(block.expected):
                return Result(block, False, "OUTPUT DOES NOT MATCH the text fence",
                              "documented:\n" + norm(block.expected)[:400]
                              + "\n\nactual:\n" + norm(run.stdout)[:400])
            return Result(block, True, "compiles clean, runs, output matches")

    return Result(block, False, f"unknown directive '{d}'")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Verify every C/C++ example in the book.")
    ap.add_argument("filter", nargs="?", default="", help="only chapters whose name contains this")
    ap.add_argument("-v", "--verbose", action="store_true", help="show every block")
    ap.add_argument("--cc", default=None, help="C++ compiler (default: clang++, g++, c++)")
    ap.add_argument("--dir", default=None,
                    help="read chapters from here instead of code/cpp/chapters")
    args = ap.parse_args()

    chapters_dir = Path(args.dir).resolve() if args.dir else CHAPTERS
    cxx, cc = pick_compilers(args.cc)
    if not cxx:
        print("no C++ compiler on PATH (looked for clang++, g++, c++)", file=sys.stderr)
        return 2

    leak_ok = probe_leak_detection(cxx)

    files = sorted(p for p in chapters_dir.glob("*.md") if args.filter in p.name)
    if not files:
        print(f"no chapters match {args.filter!r} in {chapters_dir}", file=sys.stderr)
        return 2

    print(f"C++ driver : {cxx}")
    print(f"C driver   : {cc or '(none found)'}")
    print(f"leak detect: {'yes' if leak_ok else 'NO — leak blocks will be reported SKIPPED'}")
    print(f"chapters   : {len(files)}\n")

    total = failures = skipped = fragments = 0
    broken: list[str] = []

    for path in files:
        blocks = parse_chapter(path)
        actionable = [b for b in blocks if b.directive]
        frags = len(blocks) - len(actionable)
        if not actionable and not frags:
            continue

        results = [check_block(b, cxx, cc, leak_ok) for b in actionable]
        bad = [r for r in results if not r.ok]
        skips = [r for r in results if r.skipped]
        total += len(results)
        failures += len(bad)
        skipped += len(skips)
        fragments += frags
        if bad:
            broken.append(path.stem)

        mark = "FAIL" if bad else " ok "
        note = []
        if frags:
            note.append(f"{frags} fragment(s)")
        if skips:
            note.append(f"{len(skips)} skipped")
        tail = ("  —  " + ", ".join(note)) if note else ""
        print(f"[{mark}] {path.stem}  —  {len(results) - len(bad)}/{len(results)} block(s){tail}")

        if args.verbose:
            for r in results:
                flag = "SKIP" if r.skipped else ("  ok  " if r.ok else " FAIL ")
                print(f"        {flag} {r.block.where:<26} {r.block.directive:<15} {r.note}")

        for r in bad:
            print(f"        FAIL  {r.block.where}  [{r.block.directive}]  {r.note}")
            if r.detail:
                for ln in r.detail.splitlines()[:14]:
                    print(f"              | {ln}")
            print()
        for r in skips:
            print(f"        SKIP  {r.block.where}  [{r.block.directive}]  {r.note}")

    print("-" * 72)
    if failures:
        print(f"{failures} of {total} blocks FAILED  ->  {', '.join(broken)}")
        print("\nFix the chapter, not the harness. A taught example that does not build")
        print("is a bug with a human cost.")
        return 1

    line = f"all {total} blocks behaved as declared"
    if skipped:
        line += f" ({skipped} skipped — leak detection unavailable here)"
    if fragments:
        line += f" ({fragments} fragments not compiled)"
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
