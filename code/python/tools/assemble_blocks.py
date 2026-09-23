#!/usr/bin/env python3
"""Assemble a chapter from a template, replacing block markers with verified fences.

A marker is a line on its own:

    <!--BLOCK:name-->

Each marker is replaced by the source of ``tools/gen/<chapter>/<name>.py``,
followed by the output that program produces **right now**:

    ```python run
    <the source that ran>
    ```

    ```text
    <its captured stdout>
    ```

Because the source in the fence is byte-for-byte the file that was executed
and the `text` fence is its live output, the block cannot drift, cannot be
paraphrased by accident, and passes verify_examples.py by construction.

Usage:
    python3 tools/assemble_blocks.py <template.md> <chapters/out.md> <NN>

The chapter number ``NN`` selects the ``tools/gen/NN`` directory.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

MARKER = re.compile(r"^<!--BLOCK:(\w+)-->$", re.M)


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    template_path = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])
    chapter = sys.argv[3]

    tools_root = pathlib.Path(__file__).resolve().parent
    gen_dir = tools_root / "gen" / chapter
    template = template_path.read_text()

    missing = []

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        program = gen_dir / f"{name}.py"
        if not program.exists():
            missing.append(str(program))
            return f"<!--MISSING BLOCK: {name}-->"

        source = program.read_text().rstrip("\n")
        if "```" in source:
            raise SystemExit(f"{program}: source contains a fence marker")

        proc = subprocess.run(
            [sys.executable, str(program)],
            capture_output=True,
            text=True,
            cwd=str(program.parent),
        )
        if proc.returncode != 0:
            raise SystemExit(
                f"{program.name} exited {proc.returncode}:\n{proc.stderr}"
            )
        if proc.stderr.strip():
            raise SystemExit(
                f"{program.name} wrote to stderr (the reader would see output "
                f"the book does not show):\n{proc.stderr}"
            )

        output = proc.stdout.rstrip("\n")
        return f"```python run\n{source}\n```\n\n```text\n{output}\n```"

    assembled = MARKER.sub(replace, template)
    out_path.write_text(assembled)

    if missing:
        for path in missing:
            print(f"  missing program: {path}", file=sys.stderr)
        return 1

    blocks = len(MARKER.findall(template))
    words = len(assembled.split())
    print(f"  wrote {out_path} — {blocks} verified block(s), {words} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
