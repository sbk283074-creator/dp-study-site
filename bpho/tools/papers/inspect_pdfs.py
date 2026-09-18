# -*- coding: utf-8 -*-
"""Look at the built PDFs: how many pages each one really has, and render a page to a PNG.

    PY=/Users/lucas.ma/.workbuddy-ai/binaries/python/envs/default/bin/python
    $PY tools/papers/inspect_pdfs.py                        # page counts for every file
    $PY tools/papers/inspect_pdfs.py bank-s01-markscheme.pdf 1   # render one page

Why this exists next to build_pdfs.js, which already counts pages: the build counts them
by scanning the raw bytes, and a count is only as good as the thing counting it.  This
opens each file with a real PDF parser and reports what it finds, so the two counts can be
compared.  They agree on every file -- 11/34, 6/16, 12/28, 10/31, 10/32.

The render mode is the more valuable half.  Every PDF defect found so far was found by
rendering a page and *looking* at it -- a markscheme whose first solution had been pushed
to page 2 by `break-inside: avoid`, leaving the heading over half a blank sheet.  No page
count would ever have shown that.
"""
import os
import sys

import fitz  # PyMuPDF

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "papers")
OUT = os.path.normpath(OUT)


def counts():
    total = 0
    files = sorted(f for f in os.listdir(OUT) if f.endswith(".pdf"))
    if not files:
        print("no PDFs in " + OUT + " -- run tools/papers/build_pdfs.js first")
        return
    for f in files:
        d = fitz.open(os.path.join(OUT, f))
        total += d.page_count
        print("%-34s %3d pages  %7.0f KB" % (f, d.page_count,
                                             os.path.getsize(os.path.join(OUT, f)) / 1024))
        d.close()
    print("%-34s %3d pages" % ("TOTAL", total))


def render(pdf, page, zoom=1.6):
    d = fitz.open(os.path.join(OUT, pdf))
    if not 1 <= int(page) <= d.page_count:
        raise SystemExit("%s has %d pages, cannot render page %s" % (pdf, d.page_count, page))
    pix = d[int(page) - 1].get_pixmap(matrix=fitz.Matrix(float(zoom), float(zoom)))
    out = "/tmp/pdfpage-%s-%s.png" % (pdf.replace(".pdf", ""), page)
    pix.save(out)
    print("%s page %s of %d -> %s  (%dx%d)" % (pdf, page, d.page_count, out, pix.width, pix.height))
    d.close()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 1.6)
    else:
        counts()
