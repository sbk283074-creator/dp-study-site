#!/usr/bin/env python3
"""Verify every Python example in the book.

This is the Python-track counterpart of code/cpp/tools/verify_examples.py and
code/java/tools/verify_examples.py. It reads a *directive* off each fenced code
block and turns it into a check:

    ```python run     a complete program. Runs it, compares stdout against the
                      `text` fence that immediately follows (if there is one).
    ```python bad     code that must FAIL. Requires a non-zero exit and, if a
                      `text` fence follows, requires the quoted words to appear
                      in stderr. Use for anything the reader should not write.
    ```python throw   an alias of `bad`, for the case where the failure is an
                      exception rather than a syntax error. Same assertions.
    ```python repl    a REPL transcript. Every `>>>` entry is pushed through a
                      real InteractiveConsole and its output compared with the
                      transcript, so a session printed in the book is checked
                      line for line.
    ```python compile code that must PARSE but must not run (a script that needs
                      arguments, opens a socket, blocks on input).
    ```python         a fragment. NOT checked. Use sparingly.

    ```sh run         a shell script. Runs with sh in an empty temp directory and
                      compares stdout against the `text` fence that follows.

A `text` fence belongs to the block directly above it. If the next fence in the
file is anything other than a `text` fence, the block has no expected output and
is only checked for running cleanly.

Usage:
    python3 tools/verify_examples.py               # every chapter
    python3 tools/verify_examples.py 07-           # chapters whose name contains this
    python3 tools/verify_examples.py --self-test   # check the harness itself
    python3 tools/verify_examples.py -v            # show every block
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent / "chapters"          # tools/ -> python/ -> chapters/

FENCE_RE = re.compile(r"^(\s*)```(\w+)?\s*([\w-]*)\s*$")
CLOSE_RE = re.compile(r"^\s*```\s*$")

RUN_TIMEOUT = 20
PYTHON = sys.executable

# Directives this harness knows about. Anything else on a fence is a typo, and a
# typo must fail loudly rather than silently downgrade the block to a fragment.
KNOWN = {"run", "bad", "throw", "repl", "compile", ""}


class Block:
    __slots__ = ("path", "line", "lang", "directive", "code", "expected")

    def __init__(self, path, line, lang, directive, code, expected=None):
        self.path = path
        self.line = line
        self.lang = lang
        self.directive = directive
        self.code = code
        self.expected = expected

    @property
    def label(self):
        return f"{self.path.stem}:{self.line}"


class Result:
    __slots__ = ("block", "ok", "note", "detail", "skipped")

    def __init__(self, block, ok, note, detail="", skipped=False):
        self.block = block
        self.ok = ok
        self.note = note
        self.detail = detail
        self.skipped = skipped


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------
def parse_chapter(path: Path) -> list[Block]:
    """Extract every fenced block, attaching a following `text` fence as output."""
    lines = path.read_text(encoding="utf-8").split("\n")
    blocks: list[Block] = []
    i = 0
    n = len(lines)

    while i < n:
        m = FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        lang = (m.group(2) or "").lower()
        directive = m.group(3) or ""
        start_line = i + 1
        i += 1
        body: list[str] = []
        while i < n and not CLOSE_RE.match(lines[i]):
            body.append(lines[i])
            i += 1
        i += 1  # step over the closing fence

        # A `text` fence immediately after (blank lines allowed) is the expected
        # output of this block.
        expected = None
        j = i
        while j < n and lines[j].strip() == "":
            j += 1
        if j < n:
            m2 = FENCE_RE.match(lines[j])
            if m2 and (m2.group(2) or "").lower() == "text":
                i = j + 1
                exp: list[str] = []
                while i < n and not CLOSE_RE.match(lines[i]):
                    exp.append(lines[i])
                    i += 1
                i += 1
                expected = "\n".join(exp)

        blocks.append(Block(path, start_line, lang, directive, "\n".join(body), expected))

    return blocks


# --------------------------------------------------------------------------
# comparison
# --------------------------------------------------------------------------
def norm(text: str) -> str:
    """Trailing whitespace and trailing newlines are not part of the claim."""
    return "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").split("\n")).strip("\n")


def squash(text: str) -> str:
    """Whitespace-insensitive form, for matching tracebacks."""
    return re.sub(r"\s+", " ", text).strip()


def matches(expected: str, actual: str) -> bool:
    return squash(expected) in squash(actual)


EXCEPTION_LINE_RE = re.compile(r"^[A-Za-z_][\w.]*(?:Error|Exception|Warning|Exit|Interrupt)\b.*$")


def glob_lines_match(documented: str, actual: str) -> bool:
    """Match documented lines against actual, where a bare `...` stands for any
    run of lines.

    This is the other half of the same convention: when a book does print the
    traceback, it prints the first line, then `...` to say "frames elided", then
    the exception line. Those frames name a temp file and cannot be reproduced,
    so `...` has to mean "anything here".

    Returns False unless the documented text actually uses an elision, so this
    can never quietly widen an ordinary comparison.
    """
    d = [l.rstrip() for l in documented.split("\n")]
    a = [l.rstrip() for l in actual.split("\n")]
    if not any(l.strip() == "..." for l in d):
        return False

    # reach[i] = the positions in `actual` reachable after matching d[:i]
    reach = [set() for _ in range(len(d) + 1)]
    reach[0].add(0)
    for i, pattern in enumerate(d):
        for j in reach[i]:
            if pattern.strip() == "...":
                reach[i + 1].update(range(j, len(a) + 1))
            elif j < len(a) and pattern == a[j]:
                reach[i + 1].add(j + 1)
    return len(a) in reach[len(d)]


def repl_output_matches(expected: str, actual: str) -> bool:
    """Does a transcript entry's documented output match what the REPL printed?

    Exception entries are a deliberate special case. Every Python book prints
    the final `SomeError: message` line and leaves out the traceback frames
    above it, because those frames name a temp file and teach the reader
    nothing. So when the documented output is a *single* line that names an
    exception, it is compared against the last line of the actual output rather
    than against the whole traceback.

    When the book does print a traceback, it elides the frames with a bare
    `...` line, and `glob_lines_match` honours that.

    Both are narrow on purpose: a multi-line claim with no elision, or a single
    line that is not an exception, must still match exactly. A wrong exception
    message is still caught -- see `fixtures/bad.md`.
    """
    if norm(expected) == norm(actual):
        return True
    exp = norm(expected)
    if "\n" not in exp and EXCEPTION_LINE_RE.match(exp):
        lines = norm(actual).split("\n")
        return lines[-1].strip() == exp
    return glob_lines_match(exp, norm(actual))


# --------------------------------------------------------------------------
# the REPL
# --------------------------------------------------------------------------
def after_prompt(line: str) -> str:
    """Drop the prompt and AT MOST ONE space after it.

    The real prompts are `>>> ` and `... ` -- three characters plus one space.
    That single space belongs to the prompt; everything after it is the
    reader's own indentation and is semantically load-bearing. Using
    `lstrip()` here flattens `...     print(x)` to `...print(x)`, which turns
    every multi-line statement in every transcript into an IndentationError.
    That bug made 20 correct transcripts look like book defects.
    """
    rest = line[3:]
    return rest[1:] if rest.startswith(" ") else rest


def split_repl(src: str):
    """Split a transcript into [(input, expected_output), ...].

    A `>>>` line opens an entry, `...` continues it, and any following line that
    is not a prompt is the entry's output.
    """
    entries: list[tuple[str, str]] = []
    cur_in: list[str] = []
    cur_out: list[str] = []
    state = None            # None | "in" | "out"

    for line in src.split("\n"):
        if line.startswith(">>>"):
            if state is not None:
                entries.append(("\n".join(cur_in), "\n".join(cur_out).strip("\n")))
            cur_in = [after_prompt(line)]
            cur_out = []
            state = "in"
        elif line.startswith("..."):
            if state == "in":
                cur_in.append(after_prompt(line))
            else:
                cur_out.append(line)
        elif line.strip() == "" and state == "in":
            # A blank line ends a compound statement in the real REPL.
            state = "out"
        elif state is not None:
            state = "out"
            cur_out.append(line)

    if state is not None:
        entries.append(("\n".join(cur_in), "\n".join(cur_out).strip("\n")))

    return entries


def run_repl(src: str):
    """Push every transcript entry through a real InteractiveConsole.

    Returns (ok, detail). Each entry's output is compared separately, so the
    failure message names the entry rather than the whole session.

    Two details make this behave like the real prompt:

    * A compound statement is only complete once the reader presses Enter a
      second time, so the source is terminated with a newline. Without it,
      `codeop` reports the block as incomplete, the console buffers it, and a
      perfectly good `for` loop appears to print nothing.
    * If `push` still reports "more input needed" after a whole entry, the
      transcript itself is truncated -- it is missing the `...` lines that
      carry the rest of the block. That is a defect in the book, so it is
      reported as one rather than surfacing as an empty-output mismatch.
    """
    import code as _code

    console = _code.InteractiveConsole(filename="<transcript>")
    for number, (inp, expected) in enumerate(split_repl(src), start=1):
        source = inp if inp.endswith("\n") else inp + "\n"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                more = console.push(source)
            except SystemExit:
                more = False
        got = buf.getvalue().rstrip("\n")
        if more:
            return False, (f"entry {number} ({inp.splitlines()[0]!r}) is incomplete: the\n"
                           f"console is still waiting for the rest of the block. The\n"
                           f"transcript is missing its `...` continuation lines.")
        if not repl_output_matches(expected, got):
            return False, (f"entry {number} ({inp.splitlines()[0]!r}) does not match\n"
                           f"documented:\n{norm(expected)[:300]}\n\nactual:\n{norm(got)[:300]}")
    return True, ""


# --------------------------------------------------------------------------
# running one block
# --------------------------------------------------------------------------
def run_script(code: str):
    """Run a complete program. Returns (stdout, stderr, exit)."""
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "prog.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(code)
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            proc = subprocess.run([PYTHON, path], capture_output=True, text=True,
                                  cwd=td, timeout=RUN_TIMEOUT, env=env)
        except subprocess.TimeoutExpired:
            return "", f"ran longer than {RUN_TIMEOUT}s (blocking on input?)", 1
        return proc.stdout, proc.stderr, proc.returncode


def run_shell(script: str):
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            proc = subprocess.run(["sh", "-c", script], capture_output=True, text=True,
                                  cwd=td, timeout=RUN_TIMEOUT, env=env)
        except subprocess.TimeoutExpired:
            return "", f"ran longer than {RUN_TIMEOUT}s", 1
        return proc.stdout, proc.stderr, proc.returncode


def check_block(block: Block) -> Result:
    if block.lang not in ("python", "py", "sh"):
        return Result(block, True, "not a Python block", skipped=True)

    d = block.directive
    if d not in KNOWN:
        return Result(block, False,
                      f"UNKNOWN DIRECTIVE {d!r} — a typo must not silently "
                      f"downgrade a block to a fragment",
                      f"known: {', '.join(sorted(x for x in KNOWN if x))}")

    if block.lang == "sh":
        if d not in ("run", ""):
            return Result(block, False, f"unsupported directive for sh: {d!r}")
        if d == "":
            return Result(block, True, "shell fence with no directive (decoration)")
        out, err, rc = run_shell(block.code)
        if rc != 0:
            return Result(block, False, f"script exited {rc}", (err or out).strip()[:400])
        if block.expected is None:
            return Result(block, True, "script ran (no output fence to compare)")
        if norm(out) != norm(block.expected):
            return Result(block, False, "OUTPUT DOES NOT MATCH the text fence",
                          "documented:\n" + norm(block.expected)[:400]
                          + "\n\nactual:\n" + norm(out)[:400])
        return Result(block, True, "script ran, output matches")

    # A bare ```python fence is a fragment and is not checked.
    if d == "":
        return Result(block, True, "fragment (not run)", skipped=True)

    if d == "compile":
        try:
            ast.parse(block.code)
        except SyntaxError as exc:
            return Result(block, False, "does not parse", f"line {exc.lineno}: {exc.msg}")
        return Result(block, True, "parses clean")

    if d == "repl":
        ok, detail = run_repl(block.code)
        if not ok:
            return Result(block, False, "REPL transcript does not match", detail)
        return Result(block, True, "transcript replays exactly")

    if d in ("bad", "throw"):
        out, err, rc = run_script(block.code)
        if rc == 0:
            return Result(block, False, "EXPECTED a failure, but it ran cleanly",
                          out.strip()[:300])
        if block.expected is not None and not matches(block.expected, err):
            return Result(block, False,
                          "stderr does not contain the documented phrase",
                          "documented: " + squash(block.expected)[:220]
                          + "\n\nactual: " + squash(err)[:400])
        last = next((l for l in reversed(err.strip().splitlines()) if l.strip()), "")
        return Result(block, True, f"failed with exit {rc}, as documented", last.strip()[:160])

    # run
    out, err, rc = run_script(block.code)
    if rc != 0:
        return Result(block, False, f"exited {rc}",
                      "\n".join((err or "").strip().splitlines()[-6:])[:600])
    if block.expected is None:
        return Result(block, True, "ran clean (no output fence to compare)")
    if norm(out) != norm(block.expected):
        return Result(block, False, "OUTPUT DOES NOT MATCH the text fence",
                      "documented:\n" + norm(block.expected)[:400]
                      + "\n\nactual:\n" + norm(out)[:400])
    return Result(block, True, "runs, output matches")


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------
def self_test() -> int:
    """Check the harness against fixtures before trusting it.

    `good.md` must pass every block. `bad.md` must fail exactly the blocks it is
    built to fail -- if the count drifts, the harness has gone blind and every
    chapter it ever approved is suspect.
    """
    fixtures = HERE / "fixtures"
    good = fixtures / "good.md"
    bad = fixtures / "bad.md"

    if not good.exists() or not bad.exists():
        print("self-test SKIPPED — fixtures/good.md or fixtures/bad.md is missing",
              file=sys.stderr)
        return 2

    def run_fixture(path: Path):
        blocks = parse_chapter(path)
        actionable = [b for b in blocks if b.directive]
        results = [check_block(b) for b in actionable]
        return results, [r for r in results if not r.ok]

    good_results, good_fail = run_fixture(good)
    print(f"fixtures/good.md: {len(good_results) - len(good_fail)} passed, "
          f"{len(good_fail)} failed")
    for r in good_fail:
        print(f"   FAIL  {r.block.label}  [{r.block.directive}]  {r.note}")
        if r.detail:
            print("      | " + r.detail.replace("\n", "\n      | ")[:400])

    bad_results, bad_fail = run_fixture(bad)
    print(f"fixtures/bad.md: {len(bad_results) - len(bad_fail)} passed, "
          f"{len(bad_fail)} failed")
    for r in bad_fail:
        print(f"   caught  {r.block.label}  [{r.block.directive}]  {r.note}")

    expected_bad = EXPECTED_BAD_FAILURES
    ok = not good_fail and len(bad_fail) == expected_bad

    print()
    if ok:
        print("self-test PASSED — the harness catches what it claims to catch")
        return 0
    print(f"self-test FAILED — good.md failures={len(good_fail)} (want 0), "
          f"bad.md failures={len(bad_fail)} (want {expected_bad})")
    return 1


EXPECTED_BAD_FAILURES = 9


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def run_dir(chapters_dir: Path, filt: str, verbose: bool):
    files = sorted(p for p in chapters_dir.glob("*.md") if filt in p.name)
    if not files:
        print(f"no chapters match {filt!r} in {chapters_dir}", file=sys.stderr)
        return -1, 0, 0, 0, []

    total = failures = fragments = 0
    broken: list[str] = []

    for path in files:
        blocks = parse_chapter(path)
        actionable = [b for b in blocks
                      if b.directive and b.lang in ("python", "py", "sh")]
        frags = len([b for b in blocks if b.lang in ("python", "py") and not b.directive])

        if not actionable and not frags:
            continue

        results = [check_block(b) for b in actionable]
        bad = [r for r in results if not r.ok]
        total += len(results)
        failures += len(bad)
        fragments += frags
        if bad:
            broken.append(path.stem)

        mark = "FAIL" if bad else " ok "
        note = f"  —  {frags} fragment(s)" if frags else ""
        print(f"[{mark}] {path.stem}  —  {len(results) - len(bad)}/{len(results)} block(s){note}")
        for r in bad:
            print(f"        FAIL  {r.block.label}  [{r.block.directive}]  {r.note}")
            if r.detail:
                print("              | " + r.detail.replace("\n", "\n              | ")[:500])
        if verbose:
            for r in results:
                if r.ok and not r.skipped:
                    print(f"        ok    {r.block.label}  [{r.block.directive}]  {r.note}")

    return failures, total, 0, fragments, broken


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify every Python example in the book.")
    ap.add_argument("filter", nargs="?", default="", help="only chapters whose name contains this")
    ap.add_argument("-v", "--verbose", action="store_true", help="show every block")
    ap.add_argument("--dir", default=None,
                    help="read chapters from here instead of code/python/chapters")
    ap.add_argument("--self-test", action="store_true",
                    help="check the harness itself against tools/fixtures")
    args = ap.parse_args()

    chapters_dir = Path(args.dir).resolve() if args.dir else CHAPTERS

    if args.self_test:
        return self_test()

    print(f"Python driver: {PYTHON}")
    print(f"chapters     : {chapters_dir}")

    failures, total, _skipped, fragments, broken = run_dir(chapters_dir, args.filter, args.verbose)
    if failures < 0:
        return 2

    print("-" * 72)
    if failures:
        print(f"{failures} of {total} blocks FAILED  ->  {', '.join(broken)}")
        print("\nFix the chapter, not the harness. A taught example that does not run")
        print("is a bug with a human cost.")
        return 1

    line = f"all {total} blocks behaved as declared"
    if fragments:
        line += f" ({fragments} fragments not run)"
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
