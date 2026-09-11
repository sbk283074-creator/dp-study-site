#!/usr/bin/env python3
"""Run the whole pipeline in one command (see STANDARD.md section 5).

    python3 tools/ship.py                    # repair, build, validate, scan, rebuild
    python3 tools/ship.py --skip-similarity  # skip the slow 12,796-question scan

Stops at the first failing stage and returns non-zero, so it can be run at the
end of every batch without reading the output unless something breaks.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

STAGES = [
    ("repair JSON", [PY, "tools/fix_json.py"], True),
    ("build site", [PY, "build.py"], True),
    ("quality gate", [PY, "tools/validate.py"], True),
    ("originality gate", [PY, "tools/similarity_check.py", "--write"], False),
    ("rebuild with scores", [PY, "build.py"], True),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-similarity", action="store_true")
    args = ap.parse_args()

    for name, cmd, always in STAGES:
        if not always and args.skip_similarity:
            print("\n--- %s: SKIPPED ---" % name, flush=True)
            continue
        print("\n--- %s ---" % name, flush=True)
        r = subprocess.run(cmd, cwd=str(ROOT))
        if r.returncode != 0:
            print("\nSTOP: '%s' failed (exit %d)." % (name, r.returncode), flush=True)
            print("Nothing has been published; fix the failures above and re-run.", flush=True)
            return r.returncode
    print("\nAll stages passed. site/ is up to date.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
