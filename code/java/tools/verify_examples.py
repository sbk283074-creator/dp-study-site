#!/usr/bin/env python3
"""Compile and run every Java example in the book, and prove the bad ones are bad.

This is the gate that makes the book's central promise checkable: *no example is
taught that has not been built and run*. It reads the fence directives described
in `code/java/STYLE.md`:

    ```java run         complete program -> javac -Xlint:all -Werror --release 21
                        then java; stdout must equal the `text` fence below it
    ```java bad         MUST NOT COMPILE. Compiles => the gate fails. A following
                        `text` fence must appear inside the real diagnostic, so a
                        quoted compiler error is verified too.
    ```java warn        compiles with -Xlint:all but NO -Werror; the `text` fence
                        must appear in the diagnostic. For "the compiler warns".
    ```java throw       must DIE: non-zero exit and the `text` fence must appear in
                        stderr. For uncaught exceptions the JVM reports.
    ```java compile     complete program -> compile only (sockets, stdin, ...)
    ```java             a fragment; deliberately not compiled (keep these rare)

Any directive may carry a `-files` suffix, which marks the block as a *multi-file
listing* rather than a single program. Each file is introduced by a banner that is
also a valid Java comment:

    ```java run-files
    // ===== Note.java =====
    ...

    // ===== Main.java =====
    ...
    ```

Every file is written into a temp directory and all of them are compiled together,
so a missing definition is a compiler error, exactly as it would be for the reader.
Java has no separate link step; unlike the C++ harness there is nothing to link.

    ```sh run           a shell script. Runs with `sh` in an empty temp directory
                        with the JDK on PATH; stdout must equal the `text` fence.
    ```sh run-project   the same, but the directory is first seeded with the files
                        of the most recent multi-file listing in the chapter and
                        that listing is compiled into out/.

Usage:
    python3 tools/verify_examples.py                  # every chapter
    python3 tools/verify_examples.py 03-strings       # one chapter (slug orNN-slug)
    python3 tools/verify_examples.py --self-test      # prove the gate still works

Exit code is non-zero if anything failed, so this can be wired into a commit hook.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = ROOT / "chapters"
FIXTURES_DIR = ROOT / "tools" / "fixtures"

RUN_TIMEOUT = 20          # seconds; a block that hangs is a failure
RELEASE = "21"

# --------------------------------------------------------------------------
# finding a JDK
# --------------------------------------------------------------------------

def find_jdk() -> Path | None:
    """Return a directory containing bin/javac, or None.

    The macOS /usr/bin/javac is a stub that prints an install prompt and exits
    non-zero, so a candidate is accepted only if `javac -version` actually runs.
    That check is the whole point: a JDK that exists but cannot compile is worse
    than no JDK, because every block would fail for a reason unrelated to the
    chapter and the gate would look strict while proving nothing.
    """
    candidates: list[Path] = []
    env = os.environ.get("JAVA_HOME")
    if env:
        candidates.append(Path(env) / "bin" / "javac")
    candidates += [Path(p) for p in sorted(glob.glob(
        "/Users/lucas.ma/.workbuddy/binaries/java/jdk-*/Contents/Home/bin/javac"))]
    candidates += [Path(p) for p in sorted(glob.glob(
        "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/javac"))]
    candidates += [Path(p) for p in sorted(glob.glob(
        "/opt/homebrew/opt/openjdk*/bin/javac"))]
    which = shutil.which("javac")
    if which:
        candidates.append(Path(which))
    for c in candidates:
        try:
            r = subprocess.run([str(c), "-version"], capture_output=True,
                               text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if r.returncode == 0 and "javac" in (r.stdout + r.stderr):
            return c.parent.parent
    return None


JDK_HOME = find_jdk()
JAVAC = str(JDK_HOME / "bin" / "javac") if JDK_HOME else None
JAVA = str(JDK_HOME / "bin" / "java") if JDK_HOME else None

# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

FENCE_RE = re.compile(r"^(\s*)```([A-Za-z0-9_+-]*)(?:\s+([A-Za-z0-9_-]+))?\s*$")
CLOSE_RE = re.compile(r"^\s*```\s*$")

JAVA_DIRECTIVES = {"run", "compile", "bad", "warn", "throw"}
SH_DIRECTIVES = {"run", "run-project"}


def parse_blocks(text: str) -> list[dict]:
    """Pull every fenced block out of a chapter, with its directive.

    A `text` fence immediately after a directive block is that block's expected
    output. 'Immediately' means next fence in the file: blank lines are skipped,
    prose and other fences are not. That adjacency rule is deliberate -- see the
    STYLE.md section of the same name for the failure it prevents.
    """
    lines = text.splitlines()
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        lang, directive = m.group(2).lower(), (m.group(3) or "")
        body: list[str] = []
        i += 1
        while i < len(lines) and not CLOSE_RE.match(lines[i]):
            body.append(lines[i])
            i += 1
        i += 1
        blocks.append({
            "lang": lang,
            "directive": directive,
            "body": "\n".join(body),
            "line": m.lastindex and i or i,
            "expected": None,
        })
    # attach expected output: the next fence, if it is a bare `text`
    for idx, b in enumerate(blocks):
        if not b["directive"]:
            continue
        j = idx + 1
        while j < len(blocks) and blocks[j]["lang"] == "text" and not blocks[j]["body"].strip():
            j += 1
        if j < len(blocks) and blocks[j]["lang"] == "text" and not blocks[j]["directive"]:
            b["expected"] = blocks[j]["body"]
            blocks[j]["consumed"] = True
    return [b for b in blocks if not b.get("consumed")]


TYPE_RE = re.compile(r"^\s*(?:public\s+|final\s+|abstract\s+|sealed\s+|non-sealed\s+)*"
                     r"(?:class|record|enum|interface)\s+(\w+)", re.M)
MAIN_RE = re.compile(r"\bstatic\s+void\s+main\s*\(")
PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)


def main_class_of(source: str) -> str | None:
    """The type that holds `main`, qualified by its package if it has one."""
    pkg = PACKAGE_RE.search(source)
    names = [(m.start(), m.group(1)) for m in TYPE_RE.finditer(source)]
    main_at = None
    for m in MAIN_RE.finditer(source):
        main_at = m.start()
        break
    if main_at is None:
        # No static main: still name the file after the type, so that a program
        # with a deliberately wrong `main` fails at *launch*, which is the lesson,
        # rather than at compile time with a file-name error that hides it.
        if not names:
            return None
        cls = names[0][1]
        return f"{pkg.group(1)}.{cls}" if pkg else cls
    before = [n for n in names if n[0] < main_at]
    if not before:
        return None
    cls = before[-1][1]
    return f"{pkg.group(1)}.{cls}" if pkg else cls


BANNER_RE = re.compile(r"^\s*(?://|/\*)\s*=+\s*([\w./-]+)\s*=+\s*(?:\*/)?\s*$")


def split_listing(body: str) -> dict[str, str] | None:
    """Split a `-files` listing into {filename: source} using its banners."""
    files: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        m = BANNER_RE.match(line)
        if m:
            if current:
                files[current] = "\n".join(buf).strip("\n")
            current = m.group(1)
            buf = []
            continue
        if current is None:
            return None       # content before the first banner: refuse to guess
        buf.append(line)
    if current:
        files[current] = "\n".join(buf).strip("\n")
    return files or None


# --------------------------------------------------------------------------
# running
# --------------------------------------------------------------------------

def norm(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.replace("\r\n", "\n").strip("\n").split("\n"))


def diff_report(expected: str, actual: str) -> str:
    e, a = norm(expected).split("\n"), norm(actual).split("\n")
    out = [f"expected {len(e)} line(s), got {len(a)}"]
    for k in range(max(len(e), len(a))):
        ev = e[k] if k < len(e) else "<missing>"
        av = a[k] if k < len(a) else "<missing>"
        if ev != av:
            out.append(f"  line {k + 1}:")
            out.append(f"    expected: {ev!r}")
            out.append(f"    actual  : {av!r}")
    return "\n".join(out)


class Runner:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def ok(self, msg: str = "") -> None:
        self.passed += 1
        print(f"  PASS  {msg}".rstrip())

    def fail(self, msg: str) -> None:
        self.failed += 1
        print(f"  FAIL  {msg}")
        print()

    def skip(self, msg: str) -> None:
        self.skipped += 1
        print(f"  SKIP  {msg}")

    def compile(self, work: Path, files: list[str], *, werror: bool) -> subprocess.CompletedProcess:
        cmd = [JAVAC, "-Xlint:all", f"--release={RELEASE}"]
        if werror:
            cmd.append("-Werror")
        cmd += ["-d", "out", *files]
        return subprocess.run(cmd, capture_output=True, text=True,
                              cwd=work, timeout=RUN_TIMEOUT * 3)

    def run_java(self, work: Path, cls: str) -> subprocess.CompletedProcess:
        return subprocess.run([JAVA, "-cp", "out", cls], capture_output=True,
                              text=True, cwd=work, timeout=RUN_TIMEOUT)

    # -- java ------------------------------------------------------------
    def java_block(self, block: dict) -> None:
        directive = block["directive"]
        multi = directive.endswith("-files")
        base = directive[: -len("-files")] if multi else directive
        where = f"java {directive}"

        if multi:
            files = split_listing(block["body"])
            if files is None:
                self.fail(f"{where}: multi-file listing has no `// ===== name =====` banners")
                return
        else:
            cls = main_class_of(block["body"]) or "Main"
            fname = cls.split(".")[-1] + ".java"
            files = {fname: block["body"].strip("\n")}

        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            for name, src in files.items():
                (work / name).write_text(src + "\n", encoding="utf-8")
            names = list(files)

            if base == "compile":
                c = self.compile(work, names, werror=True)
                if c.returncode == 0:
                    self.ok(f"{where}: compiles")
                else:
                    self.fail(f"{where}: expected it to compile\n{c.stderr.strip()[:600]}")
                return

            if base == "bad":
                c = self.compile(work, names, werror=True)
                if c.returncode == 0:
                    self.fail(f"{where}: compiled, but the chapter says it must not")
                    return
                if "error:" not in c.stderr:
                    self.fail(f"{where}: javac failed without an `error:` line\n{c.stderr.strip()[:600]}")
                    return
                if block["expected"] and norm(block["expected"]) not in norm(c.stderr):
                    self.fail(f"{where}: quoted diagnostic not found in the real one\n"
                              f"    quoted: {norm(block['expected'])[:200]!r}\n"
                              f"    real  : {c.stderr.strip()[:400]!r}")
                    return
                self.ok(f"{where}: rejected by javac as promised")
                return

            if base == "warn":
                c = self.compile(work, names, werror=False)
                if c.returncode != 0:
                    self.fail(f"{where}: expected a warning but it did not compile\n"
                              f"{c.stderr.strip()[:600]}")
                    return
                if not c.stderr.strip():
                    self.fail(f"{where}: compiled silently, so there is no warning to quote")
                    return
                if block["expected"] and norm(block["expected"]) not in norm(c.stderr):
                    self.fail(f"{where}: quoted warning not found in the real diagnostic\n"
                              f"    quoted: {norm(block['expected'])[:200]!r}\n"
                              f"    real  : {c.stderr.strip()[:400]!r}")
                    return
                self.ok(f"{where}: warns as promised")
                return

            # run / throw
            c = self.compile(work, names, werror=True)
            if c.returncode != 0:
                self.fail(f"{where}: does not compile\n{c.stderr.strip()[:600]}")
                return
            cls = None
            for name, src in files.items():
                if MAIN_RE.search(src):
                    cls = main_class_of(src)
                    break
            if cls is None:
                # no static main anywhere: name the first type anyway, so a
                # deliberately wrong `main` reaches the launcher and fails there
                for name, src in files.items():
                    cls = main_class_of(src)
                    if cls:
                        break
            if cls is None:
                self.fail(f"{where}: no `main` method found in the listing")
                return
            r = self.run_java(work, cls)

            if base == "throw":
                if r.returncode == 0:
                    self.fail(f"{where}: exited 0, but the chapter says it must die")
                    return
                if block["expected"] and norm(block["expected"]) not in norm(r.stderr):
                    self.fail(f"{where}: expected message not in stderr\n"
                              f"    quoted: {norm(block['expected'])[:200]!r}\n"
                              f"    stderr: {r.stderr.strip()[:400]!r}")
                    return
                self.ok(f"{where}: died with the promised message")
                return

            if r.returncode != 0:
                self.fail(f"{where}: ran but exited {r.returncode}\n{r.stderr.strip()[:600]}")
                return
            if block["expected"] is None:
                self.ok(f"{where}: ran clean (no output fence to compare)")
                return
            if norm(block["expected"]) != norm(r.stdout):
                self.fail(f"{where}: stdout differs from the `text` fence\n"
                          f"{diff_report(block['expected'], r.stdout)}")
                return
            self.ok(f"{where}: output matches")

    # -- shell -----------------------------------------------------------
    def sh_block(self, block: dict, project_files: dict[str, str] | None) -> None:
        directive = block["directive"]
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            if directive == "run-project":
                if not project_files:
                    self.fail("sh run-project: no multi-file listing earlier in this chapter")
                    return
                for name, src in project_files.items():
                    (work / name).write_text(src + "\n", encoding="utf-8")
                c = self.compile(work, list(project_files), werror=True)
                if c.returncode != 0:
                    self.fail(f"sh run-project: the project does not compile\n{c.stderr.strip()[:600]}")
                    return
            script = work / "_block.sh"
            script.write_text(block["body"].strip("\n") + "\n", encoding="utf-8")
            env = dict(os.environ)
            env["PATH"] = f"{JDK_HOME}/bin:{env.get('PATH', '')}"
            env["JAVA_HOME"] = str(JDK_HOME)
            try:
                r = subprocess.run(["sh", str(script)], capture_output=True, text=True,
                                   cwd=work, timeout=RUN_TIMEOUT, env=env)
            except subprocess.TimeoutExpired:
                self.fail(f"sh {directive}: timed out after {RUN_TIMEOUT}s "
                          f"(a block that leaves a server running will do this)")
                return
            if r.returncode != 0:
                self.fail(f"sh {directive}: exited {r.returncode}\n"
                          f"    stdout: {r.stdout.strip()[:300]!r}\n"
                          f"    stderr: {r.stderr.strip()[:300]!r}")
                return
            if block["expected"] is None:
                self.ok(f"sh {directive}: ran clean (no output fence to compare)")
                return
            if norm(block["expected"]) != norm(r.stdout):
                self.fail(f"sh {directive}: stdout differs\n"
                          f"{diff_report(block['expected'], r.stdout)}")
                return
            self.ok(f"sh {directive}: output matches")

    # -- dispatch --------------------------------------------------------
    def chapter(self, path: Path) -> tuple[int, int, int]:
        before = (self.passed, self.failed, self.skipped)
        blocks = parse_blocks(path.read_text(encoding="utf-8"))
        active = [b for b in blocks if b["directive"]]
        print(f"\n{path.name}  ({len(active)} block(s))")
        project_files: dict[str, str] | None = None
        for b in active:
            if b["lang"] == "java":
                multi = b["directive"].endswith("-files")
                base = b["directive"][: -len("-files")] if multi else b["directive"]
                if base not in JAVA_DIRECTIVES:
                    self.fail(f"java {b['directive']}: unknown directive")
                    continue
                if multi and base == "run":
                    project_files = split_listing(b["body"])
                self.java_block(b)
            elif b["lang"] in ("sh", "bash"):
                if b["directive"] not in SH_DIRECTIVES:
                    continue
                self.sh_block(b, project_files)
            else:
                self.fail(f"{b['lang']} {b['directive']}: unsupported language for a directive")
        return (self.passed - before[0], self.failed - before[1], self.skipped - before[2])


# --------------------------------------------------------------------------
# fixtures / self-test
# --------------------------------------------------------------------------

EXPECTED_BAD_FAILURES = 5

GOOD = """```java run
public class Main {
    public static void main(String[] args) {
        System.out.println("two plus two = " + (2 + 2));
    }
}
```

```text
two plus two = 4
```

```java warn
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List items = List.of(1);
        System.out.println(items.size());
    }
}
```

```text
warning: [rawtypes] found raw type: List
```

```java throw
public class Main {
    public static void main(String[] args) {
        String s = null;
        System.out.println(s.length());
    }
}
```

```text
NullPointerException
```

```java compile
public class Main {
    public static void main(String[] args) throws Exception {
        java.net.ServerSocket s = new java.net.ServerSocket(0);
        System.out.println(s.getLocalPort() > 0);
        s.close();
    }
}
```

```java run-files
// ===== Note.java =====
public record Note(String title) {}

// ===== Main.java =====
public class Main {
    public static void main(String[] args) {
        Note n = new Note("first");
        System.out.println(n);
    }
}
```

```text
Note[title=first]
```

```sh run
echo "shell works"
```

```text
shell works
```
"""

BAD = """```java bad
public class Main {
    public static void main(String[] args) {
        int x = "not a number";
    }
}
```

```java run
public class Main {
    public static void main(String[] args) {
        System.out.println("this output fence is wrong");
    }
}
```

```text
a completely different string
```

```java run
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List items = List.of(1);
        System.out.println(items.size());
    }
}
```

```java throw
public class Main {
    public static void main(String[] args) {
        System.out.println("exits zero, so throw cannot pass");
    }
}
```

```java warn
public class Main {
    public static void main(String[] args) {
        System.out.println("compiles silently, so there is no warning to quote");
    }
}
```

```sh run
echo one
```

```text
two
```
"""


def self_test() -> int:
    if not JDK_HOME:
        print("self-test FAILED: no working JDK found")
        return 1
    print(f"JDK: {JDK_HOME}\n")
    # The fixtures live on disk so they can be read and extended; the constants
    # above are the seed for a fresh checkout, not the copy the gate uses.
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    good, bad = FIXTURES_DIR / "good.md", FIXTURES_DIR / "bad.md"
    if not good.exists():
        good.write_text(GOOD, encoding="utf-8")
    if not bad.exists():
        bad.write_text(BAD, encoding="utf-8")
    try:
        r = Runner()
        p, f, s = r.chapter(good)
        print(f"\nfixtures/good.md: {p} passed, {f} failed, {s} skipped")
        if f:
            print("self-test FAILED: good.md must pass completely")
            return 1

        r2 = Runner()
        p2, f2, s2 = r2.chapter(bad)
        print(f"fixtures/bad.md: {p2} passed, {f2} failed, {s2} skipped")
        if f2 != EXPECTED_BAD_FAILURES:
            print(f"self-test FAILED: expected {EXPECTED_BAD_FAILURES} failures in "
                  f"bad.md, got {f2}")
            return 1
        print("self-test PASSED")
        return 0
    finally:
        pass


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter", nargs="?", help="chapter slug or number prefix")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not JDK_HOME:
        print("No working JDK found. This book is compiled, so the gate cannot run\n"
              "without one. Set JAVA_HOME or install a JDK; a /usr/bin/javac that\n"
              "prints an install prompt is not a JDK and is deliberately rejected.")
        return 2

    print(f"JDK: {JDK_HOME}")

    if args.chapter:
        want = args.chapter
        matches = [p for p in sorted(CHAPTERS_DIR.glob("*.md"))
                   if p.stem == want or p.stem.startswith(want)]
        if not matches:
            print(f"no chapter matches {want!r}")
            return 2
        targets = matches[:1]
    else:
        targets = sorted(CHAPTERS_DIR.glob("*.md"))

    runner = Runner()
    for path in targets:
        runner.chapter(path)

    total = runner.passed + runner.failed + runner.skipped
    print()
    print("-" * 60)
    print(f"{runner.passed}/{total} blocks behaved as declared"
          + (f"  [{runner.skipped} skipped]" if runner.skipped else ""))
    if runner.failed:
        print(f"{runner.failed} FAILED")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
