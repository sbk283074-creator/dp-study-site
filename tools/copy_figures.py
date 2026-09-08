#!/usr/bin/env python3
"""Copy only the figures actually referenced by questions into qbank/figures.

Source: ../dp learning/ib-dp-platform/backend/public/figures
Target: qbank/figures   (relative paths preserved, e.g. physics_hl_p1/2016May_HL/q01_p2.jpg)

Skips files that already exist with the same size, so it is safe to re-run.
"""
import os
import sqlite3
import shutil
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(SITE, "dp learning", "ib-dp-platform", "backend", "data", "app.db")
SRC = os.path.join(SITE, "dp learning", "ib-dp-platform", "backend", "public", "figures")
DST = os.path.join(SITE, "qbank", "figures")

IMG_FIELDS = ("question_image", "answer_image", "figure_image", "figure", "answer_figure")


def main():
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    paths = set()
    for row in con.execute("select %s from questions" % ",".join(IMG_FIELDS)):
        for v in row:
            if v and isinstance(v, str):
                for p in v.split(","):
                    p = p.strip()
                    if p:
                        paths.add(p)
    con.close()
    print("referenced figures: %d" % len(paths), flush=True)

    done = 0
    copied = 0
    skipped = 0
    missing = []
    total_bytes = 0
    for p in sorted(paths):
        src = os.path.join(SRC, p)
        dst = os.path.join(DST, p)
        done += 1
        if not os.path.exists(src):
            missing.append(p)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src):
                skipped += 1
            else:
                shutil.copyfile(src, dst)
                copied += 1
                total_bytes += os.path.getsize(src)
        except OSError as e:
            print("ERR %s: %s" % (p, e), flush=True)
        if done % 2000 == 0:
            print("  %d/%d  copied=%d skipped=%d  %.2f GB"
                  % (done, len(paths), copied, skipped, total_bytes / 1e9), flush=True)

    print("DONE copied=%d skipped=%d missing=%d  %.2f GB" % (copied, skipped, len(missing), total_bytes / 1e9), flush=True)
    if missing:
        with open(os.path.join(SITE, "tools", "_missing_figures.txt"), "w") as fh:
            fh.write("\n".join(missing))
        print("missing list written to tools/_missing_figures.txt", flush=True)


if __name__ == "__main__":
    main()
