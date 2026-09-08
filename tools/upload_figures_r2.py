#!/usr/bin/env python3
"""Upload the question-bank figures to a Cloudflare R2 bucket.

The qbank references figures as "<FIGURE_BASE>/<path>", where <path> looks like
"physics_hl_p2/2025May_TZ3/q02_p5.jpg". This script mirrors the local tree
`qbank/figures/**` into the bucket under the `figures/` prefix, so the live
site just needs QB.FIGURE_BASE = "https://<public>.<r2.dev>/figures/".

Credentials are read from the environment (NEVER hard-coded):

  R2_ACCOUNT_ID        Cloudflare account ID
  R2_ACCESS_KEY_ID     R2 API token Access Key ID
  R2_SECRET_ACCESS_KEY R2 API token Secret Access Key
  R2_BUCKET            bucket name            (default: dp-figures)
  FIGURES_DIR          local figures root     (default: <repo>/qbank/figures)

Requires: pip install boto3

Run:
  R2_ACCOUNT_ID=xxx R2_ACCESS_KEY_ID=xxx R2_SECRET_ACCESS_KEY=xxx \
      python3 tools/upload_figures_r2.py
"""
import os
import sys
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import boto3
    from botocore.config import Config
except ImportError:
    sys.exit("boto3 is required: pip install boto3")

ACCOUNT = os.environ.get("R2_ACCOUNT_ID")
KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
SECRET = os.environ.get("R2_SECRET_ACCESS_KEY")
BUCKET = os.environ.get("R2_BUCKET", "dp-figures")
FIGURES_DIR = os.environ.get("FIGURES_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qbank", "figures"
)

if not (ACCOUNT and KEY_ID and SECRET):
    sys.exit("Missing env vars: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")

ENDPOINT = f"https://{ACCOUNT}.r2.cloudflarestorage.com"
PREFIX = "figures/"

client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=KEY_ID,
    aws_secret_access_key=SECRET,
    region_name="auto",
    config=Config(retries={"max_attempts": 5}),
)


def files():
    for root, _, names in os.walk(FIGURES_DIR):
        for n in names:
            p = os.path.join(root, n)
            rel = os.path.relpath(p, FIGURES_DIR).replace(os.sep, "/")
            yield p, rel


def upload(p, rel):
    key = PREFIX + rel
    ct = mimetypes.guess_type(rel)[0] or "application/octet-stream"
    client.upload_file(p, BUCKET, key, ExtraArgs={"ContentType": ct})
    return key


def main():
    all_files = list(files())
    total = len(all_files)
    if total == 0:
        sys.exit(f"No figures found under {FIGURES_DIR}")
    print(f"Uploading {total} figures -> s3://{BUCKET}/{PREFIX} (endpoint {ENDPOINT})")
    done = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = [ex.submit(upload, p, rel) for p, rel in all_files]
        for f in as_completed(futs):
            f.result()  # raise on error
            done += 1
            if done % 1000 == 0 or done == total:
                print(f"  {done}/{total} uploaded")
    base = os.environ.get("R2_PUBLIC_URL", f"https://{BUCKET}.{ACCOUNT}.r2.dev")
    print("DONE.")
    print(f"Set in qbank/qbank.js:  QB.FIGURE_BASE = \"{base}/{PREFIX}\"")


if __name__ == "__main__":
    main()
