#!/usr/bin/env python3
"""Shared generator for a machine-verified Java chapter.

Why this exists
---------------
`STYLE.md` says a `text` fence below a block is a *claim the gate checks*, not
prose. A claim typed by hand is a claim that is sometimes wrong, and the failure
is invisible in the source: the chapter renders exactly as if the transcript had
been verified. So nothing here is typed. Every source block is read off disk and
every transcript is captured from a real `javac`/`java` run, byte-exact, and the
same is true of every quoted diagnostic.

The directives are exactly the ones `tools/verify_examples.py` honours:

    run          compiles with -Xlint:all -Werror --release 21; stdout is the fence
    run-files    the same, for a listing split by `// ===== Name.java =====` banners
    compile      must build, is never run
    bad          javac must reject it; the quoted line must appear in the error
    warn         compiles without -Werror; stderr must be non-empty and quoted
    throw        compiles, then exits non-zero with the quoted text on stderr
    sh run       a self-contained shell script run in an empty directory

The JDK is located by importing the gate itself rather than by a second probe.
That is deliberate: a capture taken under one JDK and checked under another is a
chapter that can pass here and fail on the reader's machine.

Usage, from a chapter's own generator
-------------------------------------
    HERE = Path(__file__).resolve().parent
    OUT  = HERE.parent.parent.parent / "chapters"
    gen  = Gen(HERE, OUT, "04-operators-and-casting.md")

    BLOCKS = {
        "arith": gen.run("Arithmetic.java"),
        "lossy": gen.bad("BadCast.java", "possible lossy conversion"),
    }
    gen.write(TEMPLATE, BLOCKS)

`Gen.write` refuses a block that was built but never referenced, and refuses a
marker with no block. A typo in a marker name and a marker you forgot to write
are different mistakes, and only checking both directions catches both.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Import the gate, not a copy of it. `verify_examples` runs its own JDK probe at
# import time; if that finds nothing, nothing here can be captured either.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import verify_examples as gate  # noqa: E402

if gate.JDK_HOME is None:
    raise SystemExit(
        "no working JDK found; set JAVA_HOME or install a JDK.\n"
        "A /usr/bin/javac that prints an install prompt is not a JDK, and is\n"
        "rejected on purpose: a JDK that exists but cannot compile is worse than\n"
        "none, because every block would fail for a reason unrelated to the book."
    )

JAVAC = gate.JAVAC
JAVA = gate.JAVA
JDK_HOME = gate.JDK_HOME
RELEASE = gate.RELEASE
RUN_TIMEOUT = gate.RUN_TIMEOUT

# javac writes an absolute path into a randomly-named temporary directory, so the
# location prefix can never appear in a fence -- it is different on every run.
LOCATION_RE = re.compile(r"^.*?\.java:\d+: ")

BANNER = "// ===== {name} ====="

MAX_WIDTH = 89  # the house ceiling for a table; prose lines are allowed to run on


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


def quote(blob: str, contains: str, lines: int = 1) -> str:
    """The line (or `lines`) the `text` fence quotes, with the path prefix gone.

    The harness checks `norm(quoted) in norm(real)`, so a quote is a substring of
    the real diagnostic rather than a paraphrase of it -- and stripping the
    location prefix is what keeps the quote stable, since the temp directory name
    is not.
    """
    rows = blob.splitlines()
    for i, row in enumerate(rows):
        if contains in row:
            chunk = [LOCATION_RE.sub("", r) for r in rows[i:i + lines]]
            return "\n".join(r.rstrip() for r in chunk).strip()
    raise SystemExit(f"no {contains!r} anywhere in the diagnostic:\n{blob}")


class Gen:
    """One chapter: its block sources, its runs, and the chapter it writes."""

    def __init__(self, here: Path, chapters_dir: Path, out_name: str) -> None:
        self.here = here
        self.out_dir = chapters_dir
        self.out_name = out_name
        self.audit: list[str] = []
        # The most recent `run-files` listing, kept so that a later
        # `sh run-project` can be seeded with it -- exactly as the harness does
        # when it walks a chapter and remembers the last multi-file listing.
        self._project: dict[str, str] | None = None

    # -- sources ---------------------------------------------------------
    def read(self, name: str) -> str:
        path = self.here / name
        if not path.is_file():
            raise SystemExit(f"missing source {path}")
        return path.read_text(encoding="utf-8").rstrip("\n")

    def listing(self, names: list[str]) -> str:
        """A multi-file listing: each file introduced by a banner.

        The banner is a valid Java comment, so the listing is still exactly the
        code a reader would type -- but it is a *separator*, not a file's contents.
        """
        out: list[str] = []
        for name in names:
            out.append(BANNER.format(name=name))
            out.append(self.read(name))
        return "\n\n".join(out)

    # -- compilation -----------------------------------------------------
    def _compile(self, work: Path, names: list[str], *, werror: bool) -> subprocess.CompletedProcess:
        cmd = [JAVAC, "-Xlint:all", f"--release={RELEASE}"]
        if werror:
            cmd.append("-Werror")
        cmd += ["-d", "out", *names]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=work,
                              timeout=RUN_TIMEOUT * 3)

    def _run(self, work: Path, cls: str) -> subprocess.CompletedProcess:
        return subprocess.run([JAVA, "-cp", "out", cls], capture_output=True,
                              text=True, cwd=work, timeout=RUN_TIMEOUT)

    @staticmethod
    def _write(work: Path, files: dict[str, str]) -> None:
        for name, src in files.items():
            (work / name).write_text(src + "\n", encoding="utf-8")

    @staticmethod
    def _pick_main(files: dict[str, str]) -> str:
        for src in files.values():
            if gate.MAIN_RE.search(src):
                cls = gate.main_class_of(src)
                if cls:
                    return cls
        for src in files.values():
            cls = gate.main_class_of(src)
            if cls:
                return cls
        raise SystemExit("no `main` method and no type declaration found in the listing")

    def _files_for(self, name: str) -> dict[str, str]:
        """Mirror the harness: the file is named after the type holding `main`."""
        src = self.read(name)
        cls = gate.main_class_of(src)
        if cls is None:
            raise SystemExit(f"{name}: no type declaration found")
        return {cls.split(".")[-1] + ".java": src}

    # -- directives ------------------------------------------------------
    def run(self, name: str) -> str:
        files = self._files_for(name)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            self._write(work, files)
            c = self._compile(work, list(files), werror=True)
            if c.returncode != 0:
                raise SystemExit(f"{name} does not compile:\n{c.stderr}")
            cls = self._pick_main(files)
            r = self._run(work, cls)
            if r.returncode != 0:
                raise SystemExit(f"{name} exited {r.returncode}:\n{r.stderr}")
        return self._note(name, fence("java", "run", files[next(iter(files))], r.stdout))

    def run_files(self, names: list[str]) -> str:
        files = {n: self.read(n) for n in names}
        self._project = files
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            self._write(work, files)
            c = self._compile(work, list(files), werror=True)
            if c.returncode != 0:
                raise SystemExit(f"{names} do not compile together:\n{c.stderr}")
            cls = self._pick_main(files)
            r = self._run(work, cls)
            if r.returncode != 0:
                raise SystemExit(f"{names} exited {r.returncode}:\n{r.stderr}")
        return self._note(names[0], fence("java", "run-files", self.listing(names), r.stdout))

    def compile(self, name: str) -> str:
        files = self._files_for(name)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            self._write(work, files)
            c = self._compile(work, list(files), werror=True)
            if c.returncode != 0:
                raise SystemExit(f"{name} was expected to compile:\n{c.stderr}")
        return self._note(name, fence("java", "compile", files[next(iter(files))]))

    def bad(self, name: str, contains: str, lines: int = 1) -> str:
        files = self._files_for(name)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            self._write(work, files)
            c = self._compile(work, list(files), werror=True)
        if c.returncode == 0:
            raise SystemExit(f"{name} was supposed to be rejected, but javac accepted it")
        if "error:" not in c.stderr:
            raise SystemExit(f"{name}: javac failed without an `error:` line:\n{c.stderr}")
        return self._note(name, fence("java", "bad", files[next(iter(files))],
                                      quote(c.stderr, contains, lines)))

    def warn(self, name: str, contains: str, lines: int = 1) -> str:
        files = self._files_for(name)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            self._write(work, files)
            c = self._compile(work, list(files), werror=False)
        if c.returncode != 0:
            raise SystemExit(f"{name} was expected to warn, but it did not compile:\n{c.stderr}")
        if not c.stderr.strip():
            raise SystemExit(f"{name} compiled silently, so there is no warning to quote")
        return self._note(name, fence("java", "warn", files[next(iter(files))],
                                      quote(c.stderr, contains, lines)))

    def throw(self, name: str, contains: str, lines: int = 1) -> str:
        files = self._files_for(name)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            self._write(work, files)
            c = self._compile(work, list(files), werror=True)
            if c.returncode != 0:
                raise SystemExit(f"{name} does not compile:\n{c.stderr}")
            cls = self._pick_main(files)
            r = self._run(work, cls)
        if r.returncode == 0:
            raise SystemExit(f"{name} was supposed to die, but it exited 0")
        return self._note(name, fence("java", "throw", files[next(iter(files))],
                                      quote(r.stderr, contains, lines)))

    def sh(self, name: str, directive: str = "run") -> str:
        """A self-contained shell script, run in an empty directory with the JDK on PATH.

        With `directive="run-project"` the directory is first seeded with the files of
        the most recent `run_files` listing in this chapter, and those are compiled
        into `out/` -- which is exactly what the harness does for the same directive.
        A `sh run-project` block must therefore come *after* the listing it drives.
        """
        import os
        script = self.read(name)
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            if directive == "run-project":
                if not self._project:
                    raise SystemExit(f"{name}: `sh run-project` needs a `run-files` "
                                     f"listing earlier in the chapter")
                self._write(work, self._project)
                c = self._compile(work, list(self._project), werror=True)
                if c.returncode != 0:
                    raise SystemExit(f"{name}: the project does not compile:\n{c.stderr}")
            path = work / "_block.sh"
            path.write_text(script + "\n", encoding="utf-8")
            env = dict(os.environ)
            env["PATH"] = f"{JDK_HOME}/bin:{env.get('PATH', '')}"
            env["JAVA_HOME"] = str(JDK_HOME)
            try:
                r = subprocess.run(["sh", str(path)], capture_output=True, text=True,
                                   cwd=work, timeout=RUN_TIMEOUT, env=env)
            except subprocess.TimeoutExpired:
                raise SystemExit(f"{name}: timed out after {RUN_TIMEOUT}s "
                                 f"(a block that leaves a server running will do this)")
        if r.returncode != 0:
            raise SystemExit(f"{name} exited {r.returncode}:\n"
                             f"  stdout: {r.stdout.strip()[:400]}\n"
                             f"  stderr: {r.stderr.strip()[:400]}")
        return self._note(name, fence("sh", directive, script, r.stdout))

    # -- bookkeeping -----------------------------------------------------
    def _note(self, name: str, block: str) -> str:
        """Check the captured transcript before it is ever assembled."""
        body = block.split("```text\n", 1)
        if len(body) == 1:
            return block
        text = body[1].rsplit("```", 1)[0]
        rows = text.splitlines()
        wide = [r for r in rows if len(r) > MAX_WIDTH]
        trailing = [r for r in rows if r != r.rstrip()]
        if trailing:
            self.audit.append(f"{name}: {len(trailing)} line(s) with trailing whitespace")
        if wide:
            self.audit.append(f"{name}: {len(wide)} line(s) over {MAX_WIDTH} columns "
                              f"(longest {max(len(r) for r in wide)})")
        if not text.strip():
            self.audit.append(f"{name}: the transcript is empty")
        return block

    def write(self, template: str, blocks: dict[str, str]) -> None:
        # A fence written *around* a marker is a duplicate of what `fence()` already
        # produces. It is an easy habit to fall into, because the template reads
        # like the finished chapter -- and it is silently destructive, since the
        # fence header ends up as the first line of the program body and javac then
        # reports `illegal character: '`'` on line 1. Strip it rather than merely
        # refusing it: the generated fence carries the right directive, and the
        # template's did not have to.
        redundant = re.compile(
            r"```[A-Za-z0-9_+-]*\s+[A-Za-z0-9_-]+\n(@@[A-Za-z0-9_.-]+@@)\n```\n")
        template, stripped = redundant.subn(r"\1\n", template)
        if stripped:
            print(f"note: stripped {stripped} redundant fence(s) written around a marker")

        # A marker inside a fence that holds anything else is a real mistake.
        nested = []
        inside = False
        for line in template.splitlines():
            if line.lstrip().startswith("```"):
                inside = not inside
                continue
            if inside and "@@" in line:
                nested.append(line.strip())
        if nested:
            raise SystemExit(f"marker(s) written inside a fence that has other content "
                             f"in it: {nested}")

        body = template
        unused = [k for k in blocks if f"@@{k}@@" not in body]
        if unused:
            raise SystemExit(f"block(s) built but never referenced in the template: {unused}")
        for key, value in blocks.items():
            body = body.replace(f"@@{key}@@", value.rstrip("\n"))
        leftover = sorted(set(re.findall(r"@@([A-Za-z0-9_.-]+)@@", body)))
        if leftover:
            raise SystemExit(f"unsubstituted placeholder(s): {leftover}")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        out = self.out_dir / self.out_name
        out.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
        words = len(re.findall(r"\b[\w'-]+\b", body))
        print(f"wrote {out.name}: {len(body.splitlines())} lines, ~{words} words, "
              f"{len(blocks)} block(s)")
        if self.audit:
            print("audit notes:")
            for line in self.audit:
                print(f"  - {line}")
        else:
            print("audit: no over-wide lines, no trailing whitespace, no empty transcripts")
