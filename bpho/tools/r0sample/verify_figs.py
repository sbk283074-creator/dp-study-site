#!/usr/bin/env python3
"""Gate the generated figures: every drawn coordinate must lie inside the viewBox.

This is the check that would have caught the original defect -- a viewBox of
0 0 206 100 wrapped around strokes sitting at x = 231..381. The drawing was
silently empty, and an empty figure looks exactly like a working one until you
rasterise it. Comparing every coordinate against the box is cheap and total.

Also re-runs the shape checks that matter for the physics: the S7 load must sit at
the midpoint of the edge joining the two R rods, and the S8 sketches must have the
curvature they claim.
"""
import glob
import html
import os
import re
import sys

DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig')
MARGIN = 0.5

TAG = re.compile(r'<(line|rect|circle|polyline|polygon|text)\b([^>]*)>')
TEXT_EL = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.S)
ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')

errors = []


def pts_of(tag, a, tm_content=''):
    out = []
    if tag == 'line':
        out.append((float(a['x1']), float(a['y1'])))
        out.append((float(a['x2']), float(a['y2'])))
    elif tag in ('rect',):
        x, y, w, h = float(a['x']), float(a['y']), float(a['width']), float(a['height'])
        out += [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    elif tag == 'circle':
        cx, cy, r = float(a['cx']), float(a['cy']), float(a['r'])
        out += [(cx - r, cy - r), (cx + r, cy + r)]
    elif tag in ('polyline', 'polygon'):
        for pair in a['points'].split():
            xs, ys = pair.split(',')
            out.append((float(xs), float(ys)))
    elif tag == 'text':
        # A text anchor only fixes one end; estimate the other from the content and
        # the font size (0.55 em per glyph is a good average for this face) and honour
        # text-anchor. A flat allowance is far too crude: it fails a 5-glyph label and
        # passes a 20-glyph one.
        x, y = float(a['x']), float(a['y'])
        fs = float(a.get('font-size', 12))
        body = html.unescape(re.sub(r'<[^>]+>', '', tm_content))
        w = max(1, len(body)) * fs * 0.55
        anchor = a.get('text-anchor', 'start')
        if anchor == 'middle':
            x0, x1 = x - w / 2, x + w / 2
        elif anchor == 'end':
            x0, x1 = x - w, x
        else:
            x0, x1 = x, x + w
        out += [(x0, y - fs), (x1, y + fs * 0.3)]
    return out


for path in sorted(glob.glob(os.path.join(DIR, '*.svg'))):
    name = os.path.basename(path)
    svg = open(path, encoding='utf-8').read()
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        errors.append('%s: no viewBox' % name)
        continue
    W, H = float(m.group(1)), float(m.group(2))
    if '<svg' not in svg or 'aria-label=' not in svg:
        errors.append('%s: missing aria-label' % name)
    if 'xmlns=' not in svg:
        errors.append('%s: missing xmlns' % name)

    # The bodies are written in raw PDF coordinates and shifted into the viewBox by
    # a translate() group, so the checker has to apply it too.
    tm0 = re.search(r'transform="translate\(([-\d.]+),([-\d.]+)\)"', svg)
    ox, oy = (float(tm0.group(1)), float(tm0.group(2))) if tm0 else (0.0, 0.0)

    outside = 0
    worst = None
    text_body = {m.start(): m.group(2) for m in TEXT_EL.finditer(svg)}
    for tm in TAG.finditer(svg):
        tag, attrs = tm.group(1), dict(ATTR.findall(tm.group(2)))
        try:
            ps = pts_of(tag, attrs, text_body.get(tm.start(), ''))
        except KeyError:
            continue
        for (px, py) in ps:
            x, y = px + ox, py + oy
            if x < -MARGIN or y < -MARGIN or x > W + MARGIN or y > H + MARGIN:
                outside += 1
                d = max(-x, -y, x - W, y - H)
                if worst is None or d > worst[0]:
                    worst = (d, tag, x, y)
    if outside:
        errors.append('%s: %d coordinates outside the %gx%g viewBox (worst %s at %.1f,%.1f)'
                      % (name, outside, W, H, worst[1], worst[2], worst[3]))
    else:
        print('%-12s viewBox %gx%-4g  all coordinates inside' % (name, W, H))

# ---- S7: the load marker must sit at the midpoint of the R-R edge ------------
s7 = open(os.path.join(DIR, 'r0s-07.svg'), encoding='utf-8').read()
poly = re.search(r'<polygon points="([^"]+)"', s7)
if poly:
    v = [tuple(float(t) for t in p.split(',')) for p in poly.group(1).split()]
    circ = re.search(r'<circle cx="([\d.-]+)" cy="([\d.-]+)"', s7)
    cx, cy = float(circ.group(1)), float(circ.group(2))
    mid01 = ((v[0][0] + v[1][0]) / 2.0, (v[0][1] + v[1][1]) / 2.0)
    d = ((cx - mid01[0]) ** 2 + (cy - mid01[1]) ** 2) ** 0.5
    status = 'OK' if d < 1.0 else 'MISPLACED'
    print('r0s-07 load marker: %s  - ring at (%.1f,%.1f), midpoint of the R-R edge (%.1f,%.1f), off by %.2f'
          % (status, cx, cy, mid01[0], mid01[1], d))
    if d >= 1.0:
        errors.append('r0s-07: load marker is not at the midpoint of the edge joining the two R corners')

# ---- S8: which sketch actually has the arcsin(1/n) shape? -------------------
s8 = open(os.path.join(DIR, 'r0s-08.svg'), encoding='utf-8').read()
curves = {}
for pm in re.finditer(r'<polyline points="([^"]+)"', s8):
    p = [tuple(float(t) for t in q.split(',')) for q in pm.group(1).split()]
    xs = [a for a, b in p]
    curves[(round(min(xs)), round(max(xs)))] = p
# panel x spans, in the same order as the figure's own panels A..E
PANEL = {'A': (78.2, 193.9), 'B': (246.7, 362.4), 'C': (415.2, 530.8),
         'D': (162.5, 278.1), 'E': (331.0, 446.6)}
print()
for L in 'ABCDE':
    p = None
    for (lo, hi), q in curves.items():
        if lo >= PANEL[L][0] - 2 and hi <= PANEL[L][1] + 2:
            p = q
            break
    if p is None:
        continue
    ys = [b for a, b in p]
    ytop = 460.2 if L in 'ABC' else 602.9
    ybase = 552.1 if L in 'ABC' else 694.8
    # normalise: v = 1 at the top of the ink, 0 on the axis
    lo, hi = min(ys), max(ys)
    v = [(ybase - b) / (ybase - ytop) for b in ys]
    x = [a for a, b in p]
    drops = [v[i] - v[i + 1] for i in range(len(v) - 1)]
    xs = [x[i + 1] - x[i] for i in range(len(x) - 1)]
    slope = [d / s for d, s in zip(drops, xs) if s > 0]
    dec = sum(1 for d in drops if d > 0) > sum(1 for d in drops if d < 0)
    first, last = abs(slope[0]), abs(slope[-1])
    ratio = (first / last) if last > 1e-9 else 99.0
    if 0.7 <= ratio <= 1.4:
        shape = 'straight'
    elif ratio > 1.4:
        shape = 'flattens'          # steeper at the start than at the end
    else:
        shape = 'steepens'
    reaches_zero = v[-1] < 0.05
    print('%s: %-11s |slope| %.3f -> %.3f (x%.2f)  %-9s %s'
          % (L, 'DECREASING' if dec else 'increasing', first, last, ratio, shape,
             'reaches the axis' if reaches_zero else 'stops short of the axis'))

print()
if errors:
    print('!! FIGURE GATE FAILED (%d)' % len(errors))
    for e in errors:
        print('   -', e)
    sys.exit(1)
print('all figure gates passed')
