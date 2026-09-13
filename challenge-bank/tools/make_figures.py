#!/usr/bin/env python3
"""Inline SVG figures for the Challenge Bank questions.

Everything here is plain Python string building -- no plotting library, no
external graphics tool, no image files, no rasterisation. Each function returns
the inline SVG that `build.py` already knows how to render when
`figure.type == "svg"` (see `figure_html()` in build.py).

Why code rather than a drawing tool: the geometry has to be *right*, because the
question turns on it. A normal curve whose shaded band does not sit at the z
values the stem quotes is worse than no figure. Generating the path from the
same function the answer uses means the picture and the arithmetic cannot drift.

Colours match the palette the pre-existing figures use:

    ink     #1e293b   axes, outlines, primary text
    muted   #64748b   secondary text, dashed guides
    panel   #f1f5f9   light fill
    panel2  #e2e8f0   slightly darker fill
    band    #bfdbfe   shaded region under a curve
    accent  #2563eb   the quantity under discussion
    hot     #dc2626   the trap, the anomaly
    good    #16a34a   a correct or reference value
    warn    #f59e0b   a flagged reading

Usage:
    python3 tools/make_figures.py --list
    python3 tools/make_figures.py --write          # -> data/_figures.json
    python3 tools/make_figures.py --print NAME     # one SVG on stdout
"""

import json
import math
import pathlib
import sys

INK = "#1e293b"
MUTED = "#64748b"
PANEL = "#f1f5f9"
PANEL2 = "#e2e8f0"
BAND = "#bfdbfe"
ACCENT = "#2563eb"
HOT = "#dc2626"
GOOD = "#16a34a"
WARN = "#f59e0b"
FONT = "ui-sans-serif, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


# ---------------------------------------------------------------- primitives

def _svg(w, h, label, body):
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}">'
        f'<g font-family="{FONT}">{body}</g></svg>'
    )


def _t(x, y, s, size=12, fill=INK, anchor="middle", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{fill}"{w}>{s}</text>')


def _tsup(x, y, base, sup, size=12, fill=INK, anchor="end"):
    """Text with a raised superscript -- for units such as m s^-1."""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}">'
            f'{base}<tspan dy="-4" font-size="{size * 0.72:.1f}">{sup}</tspan></text>')


def _tr(x, y, s, angle, size=11, fill=INK, anchor="middle"):
    """Text rotated about its own anchor -- for labels that run along a line."""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" '
            f'transform="rotate({angle} {x} {y})">{s}</text>')


def _l(x1, y1, x2, y2, stroke=INK, w=1.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{w}"{d}/>')


def _c(cx, cy, r, fill="none", stroke=INK, w=1.4):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{w}"/>')


def _p(d, fill="none", stroke=INK, w=1.4, dash=None, extra=""):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"'
            f'{ds}{extra}/>')


def _r(x, y, w, h, fill=PANEL, stroke=INK, sw=1.3, rx=3):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def _poly(pts, fill="none", stroke=INK, w=1.4):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'


def _arrow_defs(marker_id="ah", stroke=INK):
    return (f'<defs><marker id="{marker_id}" viewBox="0 0 10 10" refX="8" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M1 1L8 5L1 9" fill="none" stroke="{stroke}" stroke-width="1.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')


# ------------------------------------------------------------------- figures

def normal_shaded():
    """Standard normal curve with the band between z = -1.2 and z = 1.6 shaded.

    The path is generated from the same exp(-z^2/2) the answer uses, so the band
    edges land exactly on the z values quoted in the stem.
    """
    W, H = 470, 236
    x0, x1 = 48, 442          # pixel extent of the z axis
    base, peak = 186, 44      # y of the axis, and of the curve maximum
    lo, hi = -3.4, 3.4

    def X(z):
        return x0 + (z - lo) / (hi - lo) * (x1 - x0)

    def Y(z):
        return base - (base - peak) * math.exp(-z * z / 2.0)

    a, b = -1.2, 1.6

    def curve(za, zb, step):
        pts, z = [], za
        while z <= zb + 1e-9:
            pts.append((X(z), Y(z)))
            z += step
        return pts

    body = []
    band = [(X(a), base)] + curve(a, b, 0.02) + [(X(b), base)]
    body.append(_poly(band, fill=BAND, stroke="none", w=0))
    body.append(_l(x0, base, x1 + 8, base, INK, 1.6))
    body.append(_p("M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in curve(lo, hi, 0.04)),
                   stroke=INK, w=1.7))
    for z, lab in ((a, "-1.2"), (b, "1.6")):
        body.append(_l(X(z), base, X(z), Y(z), ACCENT, 1.2, dash="4 3"))
        body.append(_t(X(z), base + 18, lab, 12, ACCENT))
    body.append(_l(X(0), base, X(0), Y(0), MUTED, 1.1, dash="4 3"))
    body.append(_t(X(0), base + 18, "0", 12, MUTED))
    body.append(_t(x1 + 14, base + 4, "z", 12, INK, anchor="start"))
    body.append(_t(X(0.2), peak - 8, "standard normal", 11, MUTED, anchor="start"))
    body.append(_t((X(a) + X(b)) / 2, base - 14, "shaded area", 11, ACCENT))
    return _svg(W, H, "Standard normal curve with the region between z equals minus 1.2 "
                      "and z equals 1.6 shaded", "".join(body))


def argand_locus():
    """Argand diagram: the circle |z - (3 + 2i)| = 2 and the ray arg z = pi/4."""
    W, H = 430, 372
    sc = 52.0
    ox = 40 + 0.8 * sc          # pixel x of Re = 0
    oy = 279.2                  # pixel y of Im = 0

    def X(re):
        return ox + re * sc

    def Y(im):
        return oy - im * sc

    body = [_arrow_defs()]
    # gridlines at integer Re and Im
    for re in range(1, 6):
        body.append(_l(X(re), Y(-0.8), X(re), Y(4.6), PANEL2, 1))
    for im in range(1, 5):
        body.append(_l(X(-0.8), Y(im), X(5.6), Y(im), PANEL2, 1))
    # axes
    body.append(_l(X(-0.8), Y(0), X(5.6) + 10, Y(0), INK, 1.6))
    body.append(_l(X(0), Y(-0.8), X(0), Y(4.6) - 10, INK, 1.6))
    body.append(_t(X(5.6) + 14, Y(0) + 4, "Re", 12, INK, anchor="start"))
    body.append(_t(X(0), Y(4.6) - 18, "Im", 12, INK))
    body.append(_t(X(1), Y(0) + 16, "1", 11, MUTED))
    body.append(_t(X(3), Y(0) + 16, "3", 11, MUTED))
    body.append(_t(X(0) - 12, Y(2) + 4, "2", 11, MUTED))
    # the circle
    body.append(_c(X(3), Y(2), 2 * sc, fill="none", stroke=ACCENT, w=1.7))
    body.append(_c(X(3), Y(2), 3.4, fill=ACCENT, stroke=ACCENT, w=1))
    body.append(_t(X(3) + 8, Y(2) - 10, "3 + 2i", 11, ACCENT, anchor="start"))
    # the ray arg z = pi/4 -- the label sits beyond the end of the ray, clear of it
    body.append(_l(X(0), Y(0), X(4.4), Y(4.4), HOT, 1.5, dash="6 4"))
    body.append(_t(X(4.4) + 10, Y(4.4) + 6, "arg z = pi/4", 11, HOT, anchor="start"))
    # intersections with the circle
    r7 = math.sqrt(7.0)
    for sgn, dy in ((1, -12), (-1, 18)):
        re = (5 + sgn * r7) / 2.0
        body.append(_c(X(re), Y(re), 4.2, fill=HOT, stroke=HOT, w=1))
        body.append(_t(X(re) + 10, Y(re) + dy, "P" if sgn > 0 else "Q", 12, HOT, anchor="start"))
    return _svg(W, H, "Argand diagram showing the circle with centre three plus two i and "
                      "radius two, cut twice by the half-line arg z equals pi over four",
                "".join(body))


def vt_graph():
    """Velocity-time graph for a three-stage motion: accelerate, cruise, reverse."""
    W, H = 470, 250
    t0x, sct = 70.0, 30.0        # pixel x of t = 0, and px per second
    v0y, scv = 175.0, 12.0       # pixel y of v = 0, and px per (m/s)

    def X(t):
        return t0x + t * sct

    def Y(v):
        return v0y - v * scv

    body = [_arrow_defs()]
    # Shaded areas go down first. Painting them after the axes buried the "12"
    # tick label under the reverse-phase triangle.
    body.append(_poly([(X(0), Y(0)), (X(3), Y(9)), (X(3), Y(0))], fill="#dbeafe", stroke="none", w=0))
    body.append(_poly([(X(3), Y(0)), (X(3), Y(9)), (X(8), Y(9)), (X(8), Y(0))],
                      fill="#dbeafe", stroke="none", w=0))
    body.append(_poly([(X(8), Y(0)), (X(8), Y(9)), (X(11), Y(0))], fill="#dbeafe", stroke="none", w=0))
    body.append(_poly([(X(11), Y(0)), (X(12), Y(-3)), (X(12), Y(0))], fill="#fecaca", stroke="none", w=0))
    # axes
    body.append(_l(X(-0.5), Y(0), X(12.4), Y(0), INK, 1.6))
    body.append(_l(X(0), Y(-5), X(0), Y(10.5), INK, 1.6))
    # Ticks every 1 m/s, so that the quoted values 9 and -3 each land on a tick.
    for t in range(1, 13):
        body.append(_l(X(t), Y(0), X(t), Y(0) + 4, MUTED, 1))
    for v in range(-4, 11):
        if v:
            body.append(_l(X(0) - 4, Y(v), X(0), Y(v), MUTED, 1))
    body.append(_t(X(12.4) + 5, Y(0) + 4, "t / s", 12, INK, anchor="start"))
    body.append(_tsup(X(0) - 9, Y(10.5) - 4, "v / m s", "-1", 12, INK, anchor="end"))
    for t in (3, 8, 12):
        body.append(_t(X(t), Y(0) + 16, str(t), 11, MUTED))
    for v in (9, -3):
        body.append(_t(X(0) - 8, Y(v) + 4, str(v), 11, MUTED, anchor="end"))
    # the motion itself
    body.append(_p(f"M {X(0):.1f},{Y(0):.1f} L {X(3):.1f},{Y(9):.1f} L {X(8):.1f},{Y(9):.1f} "
                   f"L {X(12):.1f},{Y(-3):.1f}", stroke=INK, w=1.8))
    for t, v in ((0, 0), (3, 9), (8, 9), (12, -3)):
        body.append(_c(X(t), Y(v), 3.2, fill=INK, stroke=INK, w=1))
    body.append(_t(X(1.5), Y(3), "A", 11, ACCENT))
    body.append(_t(X(5.5), Y(4), "B", 11, ACCENT))
    body.append(_t(X(9.4), Y(3), "C", 11, ACCENT))
    body.append(_t(X(11.35), Y(-2.6), "D", 11, HOT))
    return _svg(W, H, "Velocity-time graph rising to nine metres per second at three seconds, "
                      "held to eight seconds, then falling to minus three at twelve seconds",
                "".join(body))


def circuit_divider():
    """Cell driving two series resistors, with a voltmeter across the second."""
    W, H = 520, 234
    L, R, T, B = 96, 360, 74, 208
    VMX = R + 78                 # x of the voltmeter centre, clear of the R2 labels
    body = [_arrow_defs(), _arrow_defs("accent", ACCENT)]
    # wires
    body.append(_p(f"M {L},{T} L {R},{T}", stroke=INK, w=1.6))
    body.append(_p(f"M {R},{T} L {R},{B}", stroke=INK, w=1.6))
    body.append(_p(f"M {R},{B} L {L},{B}", stroke=INK, w=1.6))
    body.append(_p(f"M {L},{B} L {L},{T}", stroke=INK, w=1.6))
    # cell on the left branch
    body.append(_l(L - 13, 128, L + 13, 128, INK, 2.4))
    body.append(_l(L - 7, 146, L + 7, 146, INK, 2.4))
    body.append(_l(L - 7, 128, L - 7, 146, INK, 1.6))
    body.append(_l(L + 7, 128, L + 7, 146, INK, 1.6))
    body.append(_t(L - 20, 138, "E", 12, INK, anchor="end"))
    body.append(_t(L - 20, 152, "r", 11, MUTED, anchor="end"))
    # R1 on the top branch
    body.append(_r(190, T - 13, 84, 26, fill=PANEL, stroke=INK))
    body.append(_t(232, T - 20, "R1", 12, INK))
    body.append(_t(232, T + 34, "R1 = 4.0 ohm", 10.5, MUTED))
    # R2 on the right branch -- labels to the left of the branch, inside the loop,
    # so that they cannot collide with the voltmeter sitting outside it
    body.append(_r(R - 13, 116, 26, 84, fill=PANEL, stroke=INK))
    body.append(_t(R - 22, 148, "R2", 12, INK, anchor="end"))
    body.append(_t(R - 22, 162, "R2 = 6.0 ohm", 10.5, MUTED, anchor="end"))
    # voltmeter across R2
    body.append(_p(f"M {R},116 L {VMX},116 L {VMX},{158 - 22}", stroke=MUTED, w=1.3))
    body.append(_p(f"M {R},200 L {VMX},200 L {VMX},{158 + 22}", stroke=MUTED, w=1.3))
    body.append(_c(VMX, 158, 22, fill="#fff", stroke=MUTED, w=1.3))
    body.append(_t(VMX, 163, "V", 14, MUTED, weight="500"))
    # current direction on the bottom wire
    body.append(_p(f"M 150,{B} L 206,{B}", stroke=ACCENT, w=1.5, extra=' marker-end="url(#accent)"'))
    body.append(_t(178, B - 9, "I", 12, ACCENT))
    return _svg(W, H, "A cell of e m f E and internal resistance r driving two series resistors "
                      "R1 and R2, with a voltmeter connected across R2", "".join(body))


def data_plot_anomaly():
    """Extension against hanging mass, with a best-fit line and one bad reading.

    The line is generated from the gradient the answer uses (0.0405 cm per g),
    so the flagged point really is the one that misses the line.
    """
    W, H = 470, 300
    x0, x1 = 66, 430
    y0, y1 = 246, 52
    mx0, mx1 = 0, 320          # mass axis, grams
    ex0, ex1 = 0.0, 13.0       # extension axis, cm

    def X(m):
        return x0 + (m - mx0) / (mx1 - mx0) * (x1 - x0)

    def Y(e):
        return y0 - (e - ex0) / (ex1 - ex0) * (y0 - y1)

    pts = [(50, 2.0), (100, 4.1), (150, 6.1), (200, 8.1), (250, 11.4), (300, 12.2)]
    body = [_arrow_defs()]
    for m in range(50, 301, 50):
        body.append(_l(X(m), y0, X(m), y0 + 4, MUTED, 1))
        body.append(_t(X(m), y0 + 17, str(m), 10.5, MUTED))
    for e in range(2, 13, 2):
        body.append(_l(x0 - 4, Y(e), x0, Y(e), MUTED, 1))
        body.append(_t(x0 - 9, Y(e) + 4, str(e), 10.5, MUTED, anchor="end"))
    body.append(_l(x0, y0, x1 + 8, y0, INK, 1.6))
    body.append(_l(x0, y0, x0, y1 - 8, INK, 1.6))
    body.append(_t(x1 + 6, y0 + 4, "m / g", 11.5, INK, anchor="start"))
    body.append(_t(x0 - 6, y1 - 14, "x / cm", 11.5, INK, anchor="end"))
    # Best fit through the good readings only. The label runs along the line, offset
    # perpendicular to it, which is the one band of the plot that is guaranteed empty.
    body.append(_l(X(0), Y(0.0), X(310), Y(0.0405 * 310), ACCENT, 1.6))
    ang = math.degrees(math.atan2(Y(0.0405 * 310) - Y(0.0), X(310) - X(0)))
    th = math.radians(ang)
    body.append(_tr(X(100) + 11 * math.sin(th), Y(0.0405 * 100) - 11 * math.cos(th),
                    "line of best fit", ang, 10.5, ACCENT))
    for m, e in pts:
        bad = (m == 250)
        body.append(_c(X(m), Y(e), 4.4, fill=HOT if bad else INK, stroke=HOT if bad else INK, w=1))
    body.append(_t(X(250) - 12, Y(11.4) - 13, "reading X", 10.5, HOT, anchor="end"))
    return _svg(W, H, "Scatter plot of spring extension against hanging mass, showing a straight "
                      "line through the origin with one reading well above the line",
                "".join(body))


def network_topology():
    """A two-subnet office network: router, two switches, hosts."""
    W, H = 500, 292
    body = [_arrow_defs()]

    def host(x, y, lab):
        return (_r(x - 17, y - 12, 34, 24, fill=PANEL, stroke=INK, rx=3)
                + _t(x, y + 4, lab, 10.5, INK))

    # router
    body.append(_r(196, 32, 108, 40, fill="#dbeafe", stroke=ACCENT, sw=1.5, rx=6))
    body.append(_t(250, 57, "router", 12, ACCENT, weight="500"))
    # switches
    body.append(_r(86, 132, 96, 36, fill=PANEL, stroke=INK, rx=6))
    body.append(_t(134, 155, "switch A", 11.5, INK))
    body.append(_r(318, 132, 96, 36, fill=PANEL, stroke=INK, rx=6))
    body.append(_t(366, 155, "switch B", 11.5, INK))
    # links
    body.append(_l(250, 72, 250, 102, INK, 1.5))
    body.append(_l(250, 102, 134, 102, INK, 1.5))
    body.append(_l(250, 102, 366, 102, INK, 1.5))
    body.append(_l(134, 102, 134, 132, INK, 1.5))
    body.append(_l(366, 102, 366, 132, INK, 1.5))
    # The router needs an interface in each subnet -- it is the default gateway for
    # both, so the two subnets are routed, not joined by a separate transit link.
    body.append(_t(196, 96, "192.168.10.1 / 26", 10, ACCENT, anchor="end"))
    body.append(_t(304, 96, "192.168.10.65 / 26", 10, ACCENT, anchor="start"))
    # hosts
    for i, x in enumerate((86, 134, 182)):
        body.append(_l(x, 168, x, 200, INK, 1.4))
        body.append(host(x, 218, f"PC{i + 1}"))
    for i, x in enumerate((318, 366, 414)):
        body.append(_l(x, 168, x, 200, INK, 1.4))
        body.append(host(x, 218, f"PC{i + 4}"))
    # subnet labels
    body.append(_t(134, 258, "192.168.10.0 / 26", 11, ACCENT))
    body.append(_t(134, 274, "network address", 9.5, MUTED))
    body.append(_t(366, 258, "192.168.10.64 / 26", 11, ACCENT))
    body.append(_t(366, 274, "network address", 9.5, MUTED))
    return _svg(W, H, "Office network with a router joined to two switches, three hosts on each "
                      "switch, and the two subnets labelled", "".join(body))


def bst_chain():
    """Two binary search trees over the same five keys: balanced, then degenerate."""
    W, H = 500, 290
    body = [_arrow_defs()]

    def node(x, y, key, fill=PANEL, stroke=INK, tc=INK):
        return (_c(x, y, 17, fill=fill, stroke=stroke, w=1.5)
                + _t(x, y + 4.5, str(key), 11.5, tc, weight="500"))

    def edge(x1, y1, x2, y2):
        return _l(x1, y1 + 17, x2, y2 - 17, MUTED, 1.3)

    # left: balanced
    L = [(120, 66, 30), (62, 132, 20), (178, 132, 45), (120, 198, 35), (236, 198, 50)]
    body.append(_t(120, 30, "tree A - insertion order 30, 20, 45, 35, 50", 10.5, MUTED))
    body.append(edge(*L[0][:2], *L[1][:2]))
    body.append(edge(*L[0][:2], *L[2][:2]))
    body.append(edge(*L[1][:2], *L[3][:2]))
    body.append(edge(*L[2][:2], *L[4][:2]))
    for x, y, k in L:
        body.append(node(x, y, k))
    body.append(_l(20, 240, 240, 240, PANEL2, 1.4))
    body.append(_t(130, 262, "height 3", 11, GOOD))

    # right: degenerate
    Rx = 380
    body.append(_t(380, 30, "tree B - insertion order 20, 30, 35, 45, 50", 10.5, MUTED))
    prev = None
    for i, k in enumerate((20, 30, 35, 45, 50)):
        x = Rx + 12 + i * 14
        y = 62 + i * 40
        if prev:
            body.append(_l(prev[0] + 14, prev[1] + 14, x - 12, y - 14, MUTED, 1.3))
        body.append(node(x, y, k))
        prev = (x, y)
    body.append(_l(320, 240, 480, 240, PANEL2, 1.4))
    body.append(_t(400, 262, "height 5", 11, HOT))
    return _svg(W, H, "Two binary search trees over the same five keys: one balanced with height "
                      "three, and one built from sorted keys forming a chain of height five",
                "".join(body))


def standing_wave():
    """A string fixed at both ends, showing the third harmonic."""
    W, H = 470, 200
    x0, x1 = 60, 410
    mid = 108
    body = [_arrow_defs()]
    # walls
    body.append(_l(x0, 52, x0, 164, INK, 3))
    body.append(_l(x1, 52, x1, 164, INK, 3))
    for i in range(1, 6):
        body.append(_l(x0 - 13, 52 + i * 18, x0, 52 + i * 18, PANEL2, 1))
        body.append(_l(x1, 52 + i * 18, x1 + 13, 52 + i * 18, PANEL2, 1))
    body.append(_l(x0, mid, x1, mid, MUTED, 1.1, dash="5 4"))
    # third harmonic: three half-wavelengths across the string
    pts = []
    n = 240
    for i in range(n + 1):
        u = i / n
        x = x0 + u * (x1 - x0)
        y = mid - 46 * math.sin(3 * math.pi * u)
        pts.append((x, y))
    body.append(_p("M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts), stroke=ACCENT, w=1.8))
    for i in range(4):
        u = i / 3.0
        body.append(_c(x0 + u * (x1 - x0), mid, 3.6, fill=INK, stroke=INK, w=1))
    body.append(_t((x0 + x1) / 2, 186, "string fixed at both ends", 11, MUTED))
    # Leaders, so that each label points at the feature it names rather than
    # floating in whatever space happened to be free.
    ax = x0 + (x1 - x0) / 6.0                 # first antinode
    body.append(_l(ax, mid - 46 - 5, ax - 26, 30, MUTED, 1, dash="3 3"))
    body.append(_t(ax - 30, 26, "antinode", 10.5, ACCENT, anchor="end"))
    nx = x0 + 2 * (x1 - x0) / 3.0             # the second interior node
    body.append(_l(nx, mid + 6, nx + 40, 172, MUTED, 1, dash="3 3"))
    body.append(_t(nx + 44, 176, "node", 10.5, INK, anchor="start"))
    return _svg(W, H, "A string fixed at both ends vibrating in three half-wavelengths, with "
                      "four nodes marked", "".join(body))


FIGURES = {
    "normal_shaded": normal_shaded,
    "argand_locus": argand_locus,
    "vt_graph": vt_graph,
    "circuit_divider": circuit_divider,
    "data_plot_anomaly": data_plot_anomaly,
    "network_topology": network_topology,
    "bst_chain": bst_chain,
    "standing_wave": standing_wave,
}


def build():
    return {name: fn() for name, fn in FIGURES.items()}


def main(argv):
    if "--list" in argv:
        for name in FIGURES:
            print(name)
        return 0
    if "--print" in argv:
        name = argv[argv.index("--print") + 1]
        print(build()[name])
        return 0
    if "--write" in argv:
        out = pathlib.Path(__file__).resolve().parent.parent / "data" / "_figures.json"
        out.write_text(json.dumps(build(), indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {len(FIGURES)} figures to {out}")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
