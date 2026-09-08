#!/bin/sh
# Real TaskForge demo session for chapter 23. Everything written to demo.txt is
# captured from actually running the commands; nothing is hand-written.
set -u
export NO_COLOR=1 TERM=dumb
PY=/Users/lucas.ma/Downloads/PYTHON/verify-venv/bin/python
ROOT=/Users/lucas.ma/Downloads/PYTHON/verify/taskforge
OUT="$ROOT/demo.txt"
cd "$ROOT" || exit 1
rm -f demo.db demo.log fresh.db demo-export.json
: > "$OUT"

export TASKFORGE_DB="sqlite:///$ROOT/demo.db"
export TASKFORGE_LOG="$ROOT/demo.log"

run() {
  printf '$ taskforge %s\n' "$*" >> "$OUT"
  "$PY" -m taskforge "$@" >> "$OUT" 2>&1
  status=$?
  if [ "$status" -ne 0 ]; then
    printf '[exit=%s]\n' "$status" >> "$OUT"
  fi
}

note() { printf '%s\n' "$*" >> "$OUT"; }

note "# TaskForge demo - \$NO_COLOR=1 \$TERM=dumb, TASKFORGE_DB=sqlite:///$ROOT/demo.db"
note ""
run --version
run project add work --description "Day job"
run add "Write the quarterly report" -p work --priority high --due +3d -t writing -t q3
run add "Email Dana about the contract" -p work --due today -n "attach the signed PDF"
run add "Renew passport" -p home --due 2026-08-30 --priority urgent
run list
run list --overdue
run done 2
run tag 3 errands
run report --week
run export demo-export.json
note ""
note "# import into a fresh database"
note '$ export TASKFORGE_DB=sqlite:///.../fresh.db'
TASKFORGE_DB="sqlite:///$ROOT/fresh.db" TASKFORGE_LOG="$ROOT/fresh.log" \
  "$PY" -m taskforge import demo-export.json >> "$OUT" 2>&1
printf '\n' >> "$OUT"
note '$ taskforge list --done        # in the fresh database'
TASKFORGE_DB="sqlite:///$ROOT/fresh.db" TASKFORGE_LOG="$ROOT/fresh.log" \
  "$PY" -m taskforge list --done >> "$OUT" 2>&1
note ""
note "# error path: unknown task id"
run done 999
