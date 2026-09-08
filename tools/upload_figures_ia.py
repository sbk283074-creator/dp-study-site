#!/usr/bin/env python3
"""Upload the question-bank figures to the Internet Archive (free, no credit card).

Mirrors `qbank/figures/**` into an IA item under the `figures/` prefix so the live
site just needs:

    QB.FIGURE_BASE = "https://archive.org/download/<IDENTIFIER>/figures/"

Uses concurrent uploads (boto3 threads) against IA's S3 endpoint for speed; the
item is created first via the IA metadata API.

Credentials from the environment (NEVER hard-coded):

  IA_EMAIL        archive.org account email
  IA_PASSWORD     archive.org account password
  IA_IDENTIFIER   item identifier (default: dp-qbank-figures)
  FIGURES_DIR     local figures root (default: <repo>/qbank/figures)

Requires: pip install internetarchive boto3

Run:
  IA_EMAIL=you@x.com IA_PASSWORD='...' IA_IDENTIFIER=dp-qbank-figures \
      python3 tools/upload_figures_ia.py
"""
import os
import sys
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from internetarchive import get_session
except ImportError:
    sys.exit("internetarchive is required: pip install internetarchive")
try:
    import boto3
    from botocore.config import Config
except ImportError:
    sys.exit("boto3 is required: pip install boto3")

EMAIL = os.environ.get("IA_EMAIL")
PASSWORD = os.environ.get("IA_PASSWORD")
IDENT = os.environ.get("IA_IDENTIFIER", "dp-qbank-figures")
FIGURES_DIR = os.environ.get("FIGURES_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qbank", "figures"
)

if not (EMAIL and PASSWORD):
    sys.exit("Missing env vars: IA_EMAIL, IA_PASSWORD")
os.environ.setdefault("IAS3_ACCESS_KEY", EMAIL)
os.environ.setdefault("IAS3_SECRET_KEY", PASSWORD)

if not os.path.isdir(FIGURES_DIR):
    sys.exit(f"No figures found under {FIGURES_DIR}")

# 1) Create the item (IA metadata API)
print(f"Creating IA item '{IDENT}' ...")
session = get_session()
meta = {
    "collection": "opensource_media",
    "mediatype": "dataset",
    "title": "DP Question Bank Figures",
    "creator": "DP Learning",
    "license": "other",
}
resp = session.post(f"https://archive.org/metadata/{IDENT}", json=meta)
print("item create status:", resp.status_code, resp.text[:200] if resp.status_code >= 400 else "")

# 2) Collect local files
files = []
for root, _, names in os.walk(FIGURES_DIR):
    for n in names:
        p = os.path.join(root, n)
        rel = os.path.relpath(p, FIGURES_DIR).replace(os.sep, "/")
        files.append((p, rel))
total = len(files)
if total == 0:
    sys.exit("No figure files to upload")
print(f"Uploading {total} figures -> s3.us.archive.org / bucket '{IDENT}'")

# 3) Concurrent upload
s3 = boto3.client(
    "s3",
    endpoint_url="https://s3.us.archive.org",
    aws_access_key_id=EMAIL,
    aws_secret_access_key=PASSWORD,
    region_name="us-east-1",
    config=Config(retries={"max_attempts": 6}, max_pool_connections=16),
)


def upload_one(item):
    p, rel = item
    ct = mimetypes.guess_type(rel)[0] or "application/octet-stream"
    s3.upload_file(p, IDENT, f"figures/{rel}", ExtraArgs={"ContentType": ct})
    return rel


done = 0
failed = []
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = [ex.submit(upload_one, f) for f in files]
    for f in as_completed(futs):
        try:
            f.result()
            done += 1
            if done % 2000 == 0 or done == total:
                print(f"  {done}/{total} uploaded")
        except Exception as e:  # noqa
            failed.append(str(e))

if failed:
    print(f"\n{len(failed)} uploads failed. First errors:")
    for e in failed[:5]:
        print("  ", e)
    sys.exit(f"{len(failed)} uploads failed — re-run to resume (IA is resumable per file).")

print("\nDONE.")
print(f"Set in qbank/qbank.js:  QB.FIGURE_BASE = \"https://archive.org/download/{IDENT}/figures/\"")
