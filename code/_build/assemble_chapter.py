#!/usr/bin/env python3
"""Assemble a chapter from generator sources and their captured stdout.

Why this exists
---------------
The generator pattern removes the *prediction* failure: a block's output is
captured from a real run rather than guessed. This removes the *transcription*
failure too, by never typing the code or the transcript into the chapter at
all. Both are injected byte-exact, so a stale or short `text` fence becomes
structurally impossible rather than merely avoided -- which matters, because
that defect is invisible in the source and only surfaces as a build error.

Usage
-----
    python3 code/_build/assemble_chapter.py \
        --template /tmp/ch45.template.md \
        --gen      code/python/tools/gen/45 \
        --capture  /tmp/captures/45 \
        --out      code/python/chapters/45-core-data-structures.md

The template is the chapter's prose with `<<BLOCK:name>>` markers. Each marker
expands to

    ```python run
    <byte-exact contents of <gen>/name.py>
    ```

    ```text
    <byte-exact contents of <capture>/name.txt>
    ```

The directive defaults to `run`; override per marker with `<<BLOCK:name:repl>>`
or similar. A marker naming a file that does not exist is a hard error, and so
is a marker left unexpanded -- a typo must never publish a placeholder.

Capture the stdout with the *same* interpreter the verifier uses (it prints
`Python driver: ...`), and diff several runs before you assemble.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER = re.compile(r"<<BLOCK:([A-Za-z0-9_.-]+)(?::([A-Za-z0-9_-]+))?>>")


def block(gen: Path, capture: Path, name: str, directive: str) -> str:
    source = gen / f"{name}.py"
    output = capture / f"{name}.txt"
    for path in (source, output):
        if not path.is_file():
            raise SystemExit(f"missing {path}")
    code = source.read_text()
    out = output.read_text()
    if not code.endswith("\n") or not out.endswith("\n"):
        raise SystemExit(f"{name}: source and capture must both end with a newline")
    return f"```python {directive}\n{code}```\n\n```text\n{out}```"


def assemble(template: str, gen: Path, capture: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        name, directive = match.group(1), match.group(2) or "run"
        return block(gen, capture, name, directive)

    text = MARKER.sub(replace, template)
    if "<<BLOCK:" in text:
        # Only reachable if a marker used characters the pattern rejects.
        leftover = [ln for ln in text.splitlines() if "<<BLOCK:" in ln]
        raise SystemExit(f"unexpanded marker(s): {leftover}")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--gen", required=True, type=Path, help="directory of <name>.py")
    parser.add_argument("--capture", required=True, type=Path, help="directory of <name>.txt")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    text = assemble(args.template.read_text(), args.gen, args.capture)
    args.out.write_text(text)
    names = MARKER.findall(args.template.read_text())
    print(f"{len(names)} block(s) injected -> {args.out} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
