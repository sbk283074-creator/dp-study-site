#!/usr/bin/env python3
"""Upload the question-bank figures to the Internet Archive (free, no credit card).

Robust, resumable uploader:
  * Uses the official `internetarchive` library. `Item.upload_file` PUTs straight
    to s3.us.archive.org and strips `transfer-encoding: chunked` (IA-S3 rejects it),
    so it works where raw boto3 gets HTTP 411.
  * Uploads ONLY the figures referenced by the question bank (tools/figures_manifest.txt),
    mirroring each file to `figures/<rel>` so the live site just needs:
        QB.FIGURE_BASE = "https://archive.org/download/<IDENT>/figures/"
  * Resumable: files already present on IA are skipped (safe to re-run).
  * The IA *metadata* endpoint (archive.org/metadata/...) is pathologically slow
    right now (~60s for the item's JSON), so we touch it exactly ONCE at startup
    (to learn what's already there) and NEVER inside the upload loop. A separate
    monitor thread polls the live count in the background so progress stays visible
    without throttling the upload workers.
  * Logs chunked progress to tools/ia_upload.log and prints a summary.

Credentials (NEVER hard-coded) come from ~/.config/ia.ini (or env). Run:
  python3 tools/upload_figures_ia.py
"""
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from internetarchive import get_item
except ImportError:
    sys.exit("internetarchive is required: pip install internetarchive")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.environ.get("FIGURES_DIR") or os.path.join(REPO, "qbank", "figures")
MANIFEST = os.environ.get("MANIFEST") or os.path.join(REPO, "tools", "figures_manifest.txt")
IDENT = os.environ.get("IA_IDENTIFIER", "dp-qbank-figures")
CHUNK = int(os.environ.get("IA_CHUNK", "500"))
WORKERS = int(os.environ.get("IA_WORKERS", "24"))
RETRIES_SLEEP = int(os.environ.get("IA_RETRIES_SLEEP", "5"))
SHARD = int(os.environ.get("IA_SHARD", "-1"))
SHARDS = int(os.environ.get("IA_SHARDS", "1"))
LOG = os.environ.get("IA_LOG") or os.path.join(REPO, "tools", "ia_upload.log")
TIMEOUT = (15, 120)
RK = {"request_kwargs": {"timeout": TIMEOUT}}
META = {
    "collection": "opensource_media",
    "mediatype": "dataset",
    "title": "DP Question Bank Figures",
    "creator": "DP Learning",
    "license": "other",
}

if not os.path.isfile(MANIFEST):
    sys.exit(f"No manifest at {MANIFEST}. Generate it first.")
if not os.path.isdir(FIGURES_DIR):
    sys.exit(f"No figures dir at {FIGURES_DIR}")


def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


def fetch_item(ident):
    last = None
    for i in range(6):
        try:
            it = get_item(ident, **RK)
            _ = it.metadata  # surface metadata errors early; tolerates ~60s slowness
            return it
        except Exception as e:  # noqa
            last = e
            print(f"  get_item attempt {i + 1}/6 failed: {e}")
            time.sleep(3 * (i + 1))
    raise last


def existing_remote_names(item):
    """One (slow) metadata call at startup to learn what's already uploaded."""
    try:
        return set(f.name for f in item.get_files(**RK))
    except Exception:
        return set()


def main():
    rels = load_manifest()
    if SHARDS > 1 and SHARD >= 0:
        rels = [r for i, r in enumerate(rels) if i % SHARDS == SHARD]
        print(f"[shard {SHARD}/{SHARDS}] this process handles {len(rels)} figures")

    print("Fetching IA item + existing file list (slow metadata endpoint, once)…")
    item = fetch_item(IDENT)
    have = existing_remote_names(item)

    todo = []
    for rel in rels:
        remote = "figures/" + rel
        local = os.path.join(FIGURES_DIR, rel)
        if not os.path.isfile(local):
            print(f"  WARN local missing, skip: {rel}")
            continue
        if remote in have:
            continue
        todo.append((remote, local))

    print(f"Manifest: {len(rels)} | already on IA: {len(have)} | to upload: {len(todo)}")
    if not todo:
        print("Nothing to upload — all referenced figures are already on IA.")
        finish(item)
        return

    log = open(LOG, "w", encoding="utf-8")
    stop = threading.Event()
    cnt = {"done": 0, "failed": 0, "total": len(todo)}

    def monitor():
        while not stop.is_set():
            time.sleep(60)
            try:
                live = len([f.name for f in item.get_files(**RK)
                            if f.name.startswith("figures/")])
            except Exception:
                live = -1
            msg = (f"[{time.strftime('%H:%M:%S')}] MONITOR "
                   f"done={cnt['done']} failed={cnt['failed']} "
                   f"IA_live_figures={live}")
            print(msg)
            log.write(msg + "\n")
            log.flush()

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        mt = threading.Thread(target=monitor, daemon=True)
        mt.start()
        futs = {}
        for remote, local in todo:
            futs[ex.submit(item.upload_file, local, remote,
                          metadata=META, retries=8,
                          retries_sleep=RETRIES_SLEEP,
                          queue_derive=False, verify=False, **RK)] = (remote, local)
        for fut in as_completed(futs):
            remote, _ = futs[fut]
            try:
                resp = fut.result()
                if getattr(resp, "status_code", None) in (200, 201):
                    cnt["done"] += 1
                else:
                    cnt["failed"] += 1
            except Exception as e:  # noqa
                cnt["failed"] += 1
            compl = cnt["done"] + cnt["failed"]
            if compl % CHUNK == 0 or compl == cnt["total"]:
                elapsed = time.time() - t0
                rate = compl / elapsed if elapsed else 0
                msg = (f"[{time.strftime('%H:%M:%S')}] {cnt['done']}/{cnt['total']} ok, "
                       f"{cnt['failed']} failed, {elapsed / 60:.1f} min, {rate:.2f}/s")
                print(msg)
                log.write(msg + "\n")
                log.flush()
    stop.set()
    finish(item, cnt["done"], cnt["failed"])


def finish(item, done=0, failed=0):
    print("\n" + "=" * 60)
    if done:
        print(f"Uploaded {done} new files this run.")
    if failed:
        print(f"{failed} FAILURES occurred (re-run to retry; resumable).")
    try:
        live = len([f.name for f in item.get_files(**RK)
                    if f.name.startswith("figures/")])
    except Exception:
        live = -1
    print(f"Authoritative figure count on IA now: {live}")
    print("Set in qbank/qbank.js:")
    print(f'  QB.FIGURE_BASE = "https://archive.org/download/{IDENT}/figures/"')
    print("=" * 60)


if __name__ == "__main__":
    main()
