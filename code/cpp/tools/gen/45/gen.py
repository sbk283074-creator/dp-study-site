#!/usr/bin/env python3
"""Build the Chapter 45 capstone once, run everything it claims, and write the chapter.

Nothing in `45-capstone-a-the-complete-web-service.md` is transcribed by hand. The
listing is spliced from the real files in `srv/`, and every `text` fence is the output a
run actually produced -- so the chapter cannot drift from the code beside it.

    python3 tools/gen/45/gen.py

Re-run it after touching any file under `srv/` or `sh/`.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRV = HERE / "srv"
SH = HERE / "sh"
BOOK = HERE.parent.parent
CHAPTER = BOOK / "chapters" / "45-capstone-a-the-complete-web-service.md"
TEMPLATE = HERE / "chapter.md"
DUMP = HERE / "out"

# The order a reader meets them, which is also the order the chapter explains them in.
LISTING_ORDER = [
    "Makefile",
    "config.hpp",
    "log.hpp",
    "http.hpp",
    "store.hpp",
    "auth.hpp",
    "views.hpp",
    "app.hpp",
    "framework.hpp",
    "units.cpp",
    "tests.cpp",
    "service.cpp",
]

SCRIPTS = ["config.sh", "acceptance.sh", "load.sh"]


def work_dir(root: Path) -> Path:
    """Copy the sources (never the binaries) into `root`."""
    root.mkdir(parents=True, exist_ok=True)
    for name in LISTING_ORDER:
        shutil.copy(SRV / name, root / name)
    return root


def make(root: Path) -> None:
    proc = subprocess.run(["make"], cwd=root, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise SystemExit("the project did not build:\n" + proc.stdout + proc.stderr)


def run(root: Path, command: list[str], timeout: int = 30) -> str:
    proc = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise SystemExit(f"{command} exited {proc.returncode}:\nSTDOUT\n{proc.stdout}\nSTDERR\n{proc.stderr}")
    return proc.stdout


def build_listing() -> str:
    blocks = []
    for name in LISTING_ORDER:
        blocks.append(f"/* ===== {name} ===== */\n" + (SRV / name).read_text(encoding="utf-8").rstrip("\n"))
    return "\n\n".join(blocks) + "\n"


def main() -> int:
    # Inside the tree, not in `/tmp`: this sandbox refuses temp-directory writes.
    with tempfile.TemporaryDirectory(prefix="ch45-", dir=HERE) as td:
        root = work_dir(Path(td) / "build")
        make(root)
        suite = run(root, ["./prog"])

        scripts = {}
        for name in SCRIPTS:
            with tempfile.TemporaryDirectory(prefix="ch45-sh-", dir=HERE) as sd:
                seeded = work_dir(Path(sd))
                make(seeded)
                script = seeded / "run.sh"
                script.write_text((SH / name).read_text(encoding="utf-8"), encoding="utf-8")
                scripts[name] = run(seeded, ["sh", "run.sh"], timeout=60)

        # Keep every captured transcript on disk: when a fence later looks wrong the
        # capture is evidence, and re-running the whole pipeline to see one number is
        # a waste of four builds.
        DUMP.mkdir(exist_ok=True)
        (dump / "suite.txt").write_text(suite, encoding="utf-8")
        for name, value in scripts.items():
            (dump / name.replace(".sh", ".txt")).write_text(value, encoding="utf-8")

    text = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "@@LISTING@@": build_listing().rstrip("\n"),
        "@@SUITE@@": suite.rstrip("\n"),
        "@@CONFIG@@": scripts["config.sh"].rstrip("\n"),
        "@@ACCEPTANCE@@": scripts["acceptance.sh"].rstrip("\n"),
        "@@LOAD@@": scripts["load.sh"].rstrip("\n"),
    }
    for token, value in replacements.items():
        if token not in text:
            raise SystemExit(f"template is missing {token}")
        text = text.replace(token, value)

    CHAPTER.write_text(text, encoding="utf-8")
    print(f"wrote {CHAPTER.relative_to(BOOK)} ({len(text.split())} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
