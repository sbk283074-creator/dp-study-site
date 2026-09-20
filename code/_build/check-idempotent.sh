#!/bin/sh
# Idempotence check for the CODE platform build.
#
# The build writes `code/<lang>/index.html` and `code/index.html` directly —
# there is no `dist/` staging area, so "the dist matches the deployed file" is
# not a property this layout can have. The property that actually matters is
# idempotence: running the build twice must produce byte-identical output.
#
# It is worth checking mechanically because the output is a 2 MB single file.
# A silent drift (a dropped link, a stale chapter, a changed sort order) is
# invisible by eye and only shows up when a reader notices something missing.
# That is exactly how the `.tb-site` links were lost once already.
#
#   sh code/_build/check-idempotent.sh
#
# Exit 0 = the build is reproducible. Exit 1 = it is not (a diff is printed).
# Override the interpreter with PYTHON=/path/to/python3 if `python3` is not it.

set -u

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
cd "$root" || exit 1

python_bin=${PYTHON:-python3}

if command -v shasum >/dev/null 2>&1; then
  hash() { shasum -a 256; }
elif command -v sha256sum >/dev/null 2>&1; then
  hash() { sha256sum; }
else
  echo "need shasum or sha256sum on PATH" >&2
  exit 1
fi

# Every page the build owns: the hub, plus one book per track.
# `verify/` holds hand-written reference implementations and is not built.
outputs() {
  printf '%s\n' code/index.html
  find code -mindepth 2 -maxdepth 2 -name index.html \
    -not -path 'code/_build/*' -not -path 'code/verify/*'
}

# One "sha256  path" line per output, sorted, so the two snapshots compare.
snapshot() {
  outputs | sort | while IFS= read -r f; do
    if [ -f "$f" ]; then
      printf '%s  %s\n' "$(hash < "$f" | cut -d' ' -f1)" "$f"
    else
      printf 'MISSING  %s\n' "$f"
    fi
  done
}

before=$(snapshot)
count=$(printf '%s\n' "$before" | grep -c . || true)

echo "checking $count built page(s) ..."
echo "--- running: $python_bin build.py (cwd: code/_build) ---"

if ! (cd code/_build && "$python_bin" build.py); then
  echo "FAIL — the build itself exited non-zero" >&2
  exit 1
fi

after=$(snapshot)

if [ "$before" = "$after" ]; then
  echo "OK — idempotent: re-running the build changed nothing across $count page(s)"
  exit 0
fi

echo "FAIL — the build is not reproducible; it changed its own output:" >&2
printf '%s\n' "$before" > "${TMPDIR:-/tmp}/code-build-before.txt"
printf '%s\n' "$after"  > "${TMPDIR:-/tmp}/code-build-after.txt"
diff -u "${TMPDIR:-/tmp}/code-build-before.txt" "${TMPDIR:-/tmp}/code-build-after.txt" >&2 || true
exit 1
