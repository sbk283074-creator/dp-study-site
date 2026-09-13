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


def cubic_three_roots():
    """f(x) = x^3 - 3x + 1 cut by y = a at a = 3, a = 1 and a = -1.

    The geometry has to be honest, because the whole question is that the widest
    three-root interval is the one in the MIDDLE of the range, not the two
    tangency levels at its ends. The three span bars at the bottom are drawn
    from the same roots the answer uses, so the picture cannot claim a width the
    arithmetic does not give: 2*sqrt(3) = 3.46 against 3 and 3.
    """
    W, H = 470, 340
    cx, cy = 235, 160
    sx, sy = 52.0, 26.0
    px = lambda x: cx + x * sx
    py = lambda y: cy - y * sy
    r3 = math.sqrt(3.0)

    body = [_arrow_defs()]
    for k in range(-2, 3):
        body.append(_l(px(k), 34, px(k), 250, PANEL2, 1))
        body.append(_t(px(k), 318, str(k), 10.5, MUTED))
    for k in range(-3, 5):
        body.append(_l(96, py(k), 382, py(k), PANEL2, 1))
        body.append(_t(88, py(k) + 4, str(k), 10.5, MUTED, anchor="end"))
    body.append(_l(96, py(0), 382, py(0), INK, 1.6))
    body.append(_l(px(0), 30, px(0), 250, INK, 1.6))
    body.append(_t(392, py(0) + 4, "x", 11.5, INK))
    body.append(_t(px(0) + 15, 36, "y", 11.5, INK))

    pts = []
    for i in range(481):
        x = -2.15 + 4.3 * i / 480.0
        pts.append((px(x), py(x ** 3 - 3 * x + 1)))
    body.append(_p("M " + " L ".join(f"{a:.1f},{b:.1f}" for a, b in pts), stroke=ACCENT, w=2))

    for a, col, wide in ((3.0, MUTED, False), (1.0, HOT, True), (-1.0, MUTED, False)):
        body.append(_l(px(-2.3), py(a), px(2.3), py(a), col, 1.2, dash="6 4"))
        body.append(_t(px(2.42), py(a) + 4, "y = %d" % int(a), 11, col, anchor="end"))
    for x, y in ((-1.0, 3.0), (1.0, -1.0)):
        body.append(_c(px(x), py(y), 3.6, fill=INK, stroke=INK, w=1))
    for x, y in ((-1.0, 3.0), (1.0, -1.0)):
        lab = "local max" if y > 0 else "local min"
        body.append(_t(px(x) + (46 if y > 0 else -52), py(y) + (14 if y > 0 else -12),
                       lab, 10, INK))
    for x in (-r3, 0.0, r3):
        body.append(_c(px(x), py(1.0), 4.0, fill=HOT, stroke=HOT, w=1))

    body.append(_t(120, 272, "width of the three-root interval:", 10.5, MUTED, anchor="start"))
    spans = ((262, -r3, r3, HOT, "a = 1  ->  2*sqrt(3) = 3.46"),
             (284, -1.0, 2.0, MUTED, "a = 3  ->  3"),
             (304, -2.0, 1.0, MUTED, "a = -1 ->  3"))
    for ypix, xa, xb, col, lab in spans:
        body.append(_l(px(xa), ypix, px(xb), ypix, col, 3.4))
        body.append(_l(px(xa), ypix - 5, px(xa), ypix + 5, col, 1.6))
        body.append(_l(px(xb), ypix - 5, px(xb), ypix + 5, col, 1.6))
        body.append(_t(px(xb) + 12, ypix + 4, lab, 10.5, col, anchor="start"))
    return _svg(W, H, "The cubic y = x cubed minus three x plus one, cut by horizontal lines at "
                      "y equals three, y equals one and y equals minus one. The middle line "
                      "gives the widest three-root interval, two root three, while both "
                      "tangency levels give a width of three.", "".join(body))


def spool_pull():
    """A spool on a rough surface, pulled by a string leaving the underside of the hub.

    The angle is drawn to scale and the tangent point is computed from the same
    construction the answer uses (radius perpendicular to the string), so the
    figure cannot imply a moment arm the mechanics does not have.
    """
    W, H = 500, 300
    cx, cy, R, r = 215, 150, 80, 32
    th = math.radians(42.0)
    tx, ty = cx + r * math.sin(th), cy + r * math.cos(th)     # SVG y grows downward
    ux, uy = math.cos(th), -math.sin(th)                       # string direction in SVG

    body = [_arrow_defs()]
    for i in range(14):
        body.append(_l(46 + i * 30, 230, 36 + i * 30, 244, PANEL2, 1.2))
    body.append(_l(40, 230, 468, 230, INK, 2.2))
    body.append(_c(cx, cy, R, fill=PANEL, stroke=INK, w=1.8))
    body.append(_c(cx, cy, r, fill=PANEL2, stroke=MUTED, w=1.4))
    body.append(_c(cx, cy, 3.0, fill=INK, stroke=INK, w=1))
    body.append(_t(cx, cy - 6, "C", 10.5, MUTED))

    body.append(_l(cx, cy, cx, 230, MUTED, 1.2, dash="5 4"))
    body.append(_t(cx + 8, 200, "R", 11, INK, anchor="start"))
    body.append(_l(cx, cy, tx, ty, MUTED, 1.2, dash="5 4"))
    body.append(_t(cx + 0.5 * (tx - cx) + 16, cy + 0.5 * (ty - cy) + 4, "r", 11, INK))

    body.append(_l(tx, ty, tx + 96 * ux, ty + 96 * uy, HOT, 2.2))
    body.append(_t(tx + 108 * ux, ty + 108 * uy, "T", 12.5, HOT))
    body.append(_l(tx, ty, tx + 74, ty, MUTED, 1, dash="4 4"))
    arc = []
    for i in range(13):
        a = th * i / 12.0
        arc.append(f"{tx + 30 * math.cos(a):.1f},{ty + 30 * math.sin(a):.1f}")
    body.append(_p("M " + " L ".join(arc), stroke=MUTED, w=1))
    body.append(_t(tx + 40, ty - 12, "theta", 11.5, INK, anchor="start"))

    body.append(_l(cx, 230, cx, 186, GOOD, 2))
    body.append(_t(cx + 34, 196, "N", 12, GOOD))
    body.append(_l(cx, cy, cx, cy + 58, INK, 1.8))
    body.append(_t(cx - 24, cy + 62, "mg", 11.5, INK))
    body.append(_c(cx, 230, 3.2, fill=INK, stroke=INK, w=1))
    body.append(_t(404, 250, "rough surface", 11, MUTED))
    body.append(_t(96, 44, "string leaves the hub at its underside", 11, MUTED, anchor="start"))
    return _svg(W, H, "A spool of outer radius R resting on a rough horizontal surface. A string "
                      "wound on an inner hub of radius r leaves the underside of the hub and is "
                      "pulled with tension T at an angle theta above the horizontal. The weight "
                      "and the normal reaction at the contact point are shown.", "".join(body))


def jit_cost_curves():
    """Total time against number of executions: pure interpretation vs JIT compilation.

    Both lines are computed from the model the question states, so the crossing
    the candidate reads off the figure is the break-even the algebra gives, and
    the shaded region is where the compiled route actually wins.
    """
    W, H = 470, 300
    ox, oy = 92, 236
    sx, sy = 0.78, 8.0                       # px per execution, px per millisecond
    n_max = 440.0
    interp = lambda n: 0.05 * n              # ms
    jit = lambda n: 6.0 + 0.01 * n           # ms: fixed compile cost, cheaper per run
    n_star = 150.0                           # 0.05n = 6 + 0.01n

    body = [_arrow_defs()]
    for k in range(0, 6):
        body.append(_l(ox, oy - k * 40, ox + n_max * sx, oy - k * 40, PANEL2, 1))
        body.append(_t(ox - 10, oy - k * 40 + 4, "%g" % (k * 5), 10.5, MUTED, anchor="end"))
    for n in (0, 150, 300, 420):
        body.append(_l(ox + n * sx, oy, ox + n * sx, oy + 6, INK, 1.2))
        body.append(_t(ox + n * sx, oy + 22, str(n), 10.5, MUTED))
    body.append(_l(ox - 14, oy, ox + n_max * sx + 12, oy, INK, 1.6, ))
    body.append(_l(ox, oy + 10, ox, 30, INK, 1.6))
    body.append(_t(ox + n_max * sx + 4, oy + 22, "N", 12, INK))
    body.append(_t(ox - 22, 50, "time /ms", 11, INK, anchor="start"))
    body.append(_t(ox + n_max * sx / 2, 288, "number of executions of the loop body", 11, MUTED))

    x0, x1 = ox, ox + n_max * sx
    body.append(_l(x0, oy - interp(0) * sy, x1, oy - interp(n_max) * sy, INK, 2))
    body.append(_l(x0, oy - jit(0) * sy, x1, oy - jit(n_max) * sy, ACCENT, 2))
    by = oy - interp(n_star) * sy
    bx = ox + n_star * sx
    body.append(_c(bx, by, 4.2, fill=HOT, stroke=HOT, w=1))
    body.append(_l(bx, by, bx, oy, HOT, 1, dash="4 4"))
    body.append(_t(bx - 8, by - 14, "break-even, N = 150", 11, HOT, anchor="end"))
    body.append(_t(x1 - 6, oy - interp(n_max) * sy - 12, "interpreted", 11.5, INK, anchor="end"))
    body.append(_t(x1 - 6, oy - jit(n_max) * sy + 20, "compiled once, then run", 11.5,
                   ACCENT, anchor="end"))
    body.append(_t(ox + 16, oy - jit(0) * sy - 12, "compile cost 6 ms", 10.5, ACCENT,
                   anchor="start"))
    for i in range(9):
        xx = bx + 6 + i * 16
        if xx < x1:
            body.append(_l(xx, by + 10 + i * 1.4, xx, oy - 4, BAND, 6))
    body.append(_t(ox + (x1 - bx) / 2 + 40, oy - 16, "compiling is faster", 10.5, HOT))
    return _svg(W, H, "Total running time against the number of times a loop body executes. "
                      "The interpreted line starts at the origin and rises steeply; the "
                      "just-in-time line starts at six milliseconds and rises gently. They "
                      "cross at one hundred and fifty executions, after which compiling is "
                      "faster.", "".join(body))


def improper_singularity():
    """y = 1/x^2 on [-1, 2]: positive everywhere, unbounded at x = 0.

    The point of the figure is the clash it makes visible. The curve never goes
    below the axis, yet the naive evaluation of the antiderivative across the
    interval returns -1.5. Drawing the branch structure is what forces the
    candidate to see that the interval contains a point where the function does
    not exist, and that no signed area can be assigned to what happens there.
    """
    W, H = 660, 300
    x0, x1 = -1.0, 2.0
    ymax = 6.0
    px0, px1, py0, py1 = 70.0, 630.0, 262.0, 26.0

    def sx(x):
        return px0 + (x - x0) / (x1 - x0) * (px1 - px0)

    def sy(y):
        return py0 - (min(y, ymax) / ymax) * (py0 - py1)

    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Graph of y equals 1 over x squared, showing the two branches '
           f'and the vertical asymptote at x equals 0">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
    # grid
    for gx in (-1.0, -0.5, 0.5, 1.0, 1.5, 2.0):
        out.append(f'<line x1="{sx(gx):.1f}" y1="{py1}" x2="{sx(gx):.1f}" y2="{py0}" '
                   f'stroke="#e2e8f0" stroke-width="1"/>')
    for gy in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        out.append(f'<line x1="{px0}" y1="{sy(gy):.1f}" x2="{px1}" y2="{sy(gy):.1f}" '
                   f'stroke="#e2e8f0" stroke-width="1"/>')
    # axes
    out.append(f'<line x1="{px0 - 8}" y1="{py0}" x2="{px1}" y2="{py0}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<line x1="{sx(0):.1f}" y1="{py0}" x2="{sx(0):.1f}" y2="{py1 - 6}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<path d="M {px1} {py0} l -7 -3 l 0 6 z" fill="{INK}"/>')
    out.append(f'<path d="M {sx(0):.1f} {py1 - 6} l -3 7 l 6 0 z" fill="{INK}"/>')

    def branch(a, b, n=240):
        pts = []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            pts.append((sx(x), sy(1.0 / (x * x))))
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        return d

    out.append(f'<path d="{branch(-1.0, -0.075)}" fill="none" stroke="{ACCENT}" stroke-width="2.2"/>')
    out.append(f'<path d="{branch(0.075, 2.0)}" fill="none" stroke="{ACCENT}" stroke-width="2.2"/>')
    # asymptote
    out.append(f'<line x1="{sx(0):.1f}" y1="{py1}" x2="{sx(0):.1f}" y2="{py0}" '
               f'stroke="{HOT}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    out.append(f'<text x="{sx(0) + 8:.1f}" y="{py1 + 16}" font-size="13" fill="{HOT}" '
               f'font-family="Georgia, serif">x = 0   f is not defined here</text>')
    # markers at the endpoints
    for xv, lab in ((-1.0, "(-1, 1)"), (2.0, "(2, 0.25)")):
        out.append(f'<circle cx="{sx(xv):.1f}" cy="{sy(1.0 / (xv * xv)):.1f}" r="3.4" fill="{GOOD}"/>')
        dy = -12 if xv < 0 else 18
        out.append(f'<text x="{sx(xv):.1f}" y="{sy(1.0 / (xv * xv)) + dy:.1f}" font-size="12.5" '
                   f'fill="{GOOD}" text-anchor="middle" font-family="Georgia, serif">{lab}</text>')
    # the impossible answer
    out.append(f'<text x="{sx(1.32):.1f}" y="{sy(2.1):.1f}" font-size="14" fill="{INK}" '
               f'font-family="Georgia, serif">y = 1 / x&#178;  &#8805; 0 everywhere</text>')
    out.append(f'<text x="{sx(1.32):.1f}" y="{sy(1.55):.1f}" font-size="13" fill="{HOT}" '
               f'font-family="Georgia, serif">yet [-1/x] from -1 to 2 = -1.5</text>')
    # axis labels
    for gx in (-1.0, 1.0, 2.0):
        out.append(f'<text x="{sx(gx):.1f}" y="{py0 + 17}" font-size="12" fill="{MUTED}" '
                   f'text-anchor="middle" font-family="Georgia, serif">{gx:g}</text>')
    for gy in (2.0, 4.0, 6.0):
        out.append(f'<text x="{px0 - 12}" y="{sy(gy) + 4:.1f}" font-size="12" fill="{MUTED}" '
                   f'text-anchor="end" font-family="Georgia, serif">{gy:g}</text>')
    out.append('</svg>')
    return "".join(out)


def echo_doppler():
    """A bat, a wall closing at speed u, and the two shifts the echo picks up.

    The single most useful thing this figure does is separate the two stages.
    Candidates who apply the Doppler formula once are almost always applying it
    to the wrong stage: the wall is a moving *observer* on the way out and a
    moving *source* on the way back, and only the second of those is obvious.
    """
    W, H = 660, 250
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="A bat emitting ultrasound towards a wall that is moving towards it, '
           f'showing the outward and reflected journeys">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
    batx, wallx = 96.0, 520.0
    mid = 168.0
    # wall
    out.append(f'<rect x="{wallx}" y="34" width="16" height="182" fill="{PANEL2}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<text x="{wallx + 8}" y="26" font-size="13" fill="{INK}" text-anchor="middle" '
               f'font-family="Georgia, serif">wall</text>')
    # motion arrow on the wall (towards the bat)
    out.append(f'<line x1="{wallx + 44}" y1="{mid - 62}" x2="{wallx + 8}" y2="{mid - 62}" '
               f'stroke="{HOT}" stroke-width="2" marker-end="url(#edarrow)"/>')
    out.append(f'<text x="{wallx + 52}" y="{mid - 57}" font-size="13" fill="{HOT}" '
               f'font-family="Georgia, serif">u</text>')
    # bat
    out.append(f'<circle cx="{batx}" cy="{mid}" r="15" fill="{ACCENT}" opacity="0.15" stroke="{ACCENT}" stroke-width="1.6"/>')
    out.append(f'<text x="{batx}" y="{mid + 5}" font-size="13" fill="{ACCENT}" text-anchor="middle" '
               f'font-family="Georgia, serif">bat</text>')
    # outward wavefronts (compressed ahead, because the wall approaches)
    out.append(f'<g stroke="{ACCENT}" stroke-width="1.6" fill="none">')
    for i, r in enumerate((26, 52, 78, 104, 130)):
        out.append(f'<path d="M {batx + r} {mid - 34} A {r} {r} 0 0 1 {batx + r} {mid + 34}"/>')
    out.append('</g>')
    out.append(f'<text x="{batx + 128}" y="{mid + 74}" font-size="12.5" fill="{ACCENT}" '
               f'font-family="Georgia, serif">emitted, frequency f</text>')
    # reflected wavefronts (compressed further)
    out.append(f'<g stroke="{GOOD}" stroke-width="1.6" fill="none">')
    for r in (34, 66, 98, 130):
        out.append(f'<path d="M {wallx - r} {mid - 30} A {r} {r} 0 0 0 {wallx - r} {mid + 30}"/>')
    out.append('</g>')
    out.append(f'<text x="{wallx - 150}" y="{mid - 62}" font-size="12.5" fill="{GOOD}" '
               f'font-family="Georgia, serif">received echo, frequency f&#8242; &gt; f</text>')
    # the two stages
    out.append(f'<text x="{batx + 66}" y="{mid - 86}" font-size="12.5" fill="{MUTED}" '
               f'font-family="Georgia, serif">stage 1: wall is a moving observer</text>')
    out.append(f'<text x="{wallx - 214}" y="{mid + 104}" font-size="12.5" fill="{MUTED}" '
               f'font-family="Georgia, serif">stage 2: wall is a moving source</text>')
    out.append('<defs><marker id="edarrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" '
               'orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="%s"/></marker></defs>' % HOT)
    out.append('</svg>')
    return "".join(out)


def bdp_window():
    """Why a bigger pipe does not help: the window empties long before the ack.

    The figure plots the same 64 kB window against two link rates and the one
    round-trip time they share. At 100 Mbps the transmission finishes after
    5.2 ms and the sender then sits idle for the remaining 34.8 ms; at 1 Gbps it
    finishes after 0.52 ms and idles for longer. The pipe is not the constraint
    and never was.
    """
    W, H = 660, 250
    left, right = 70.0, 630.0
    y100, y1000 = 96.0, 176.0
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Timeline comparing how long a 64 kilobyte window takes to transmit '
           f'at 100 megabits per second and at 1 gigabit per second against a 40 millisecond '
           f'round trip time">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')

    def sx(t):  # t in ms over a 40 ms round trip
        return left + t / 40.0 * (right - left)

    # RTT bar
    out.append(f'<line x1="{left}" y1="52" x2="{right}" y2="52" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<text x="{left - 10}" y="57" font-size="12" fill="{MUTED}" text-anchor="end" '
               f'font-family="Georgia, serif">RTT</text>')
    out.append(f'<text x="{right}" y="40" font-size="12.5" fill="{INK}" text-anchor="end" '
               f'font-family="Georgia, serif">40 ms round-trip time</text>')

    rows = [("100 Mbps", 5.24288, y100, HOT), ("1 Gbps", 0.524288, y1000, ACCENT)]
    for label, ttx, yy, col in rows:
        out.append(f'<text x="{left - 10}" y="{yy + 4}" font-size="12.5" fill="{MUTED}" '
                   f'text-anchor="end" font-family="Georgia, serif">{label}</text>')
        # busy transmitting
        out.append(f'<rect x="{left}" y="{yy - 13}" width="{sx(ttx) - left:.1f}" height="26" '
                   f'fill="{col}" opacity="0.85"/>')
        # idle waiting
        out.append(f'<rect x="{sx(ttx):.1f}" y="{yy - 13}" width="{right - sx(ttx):.1f}" height="26" '
                   f'fill="{PANEL}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 3"/>')
        out.append(f'<text x="{sx(ttx) + 10:.1f}" y="{yy + 4}" font-size="12" fill="{MUTED}" '
                   f'font-family="Georgia, serif">idle, waiting for the acknowledgement</text>')
        out.append(f'<text x="{left + 6}" y="{yy + 4}" font-size="12" fill="#ffffff" '
                   f'font-family="Georgia, serif">{ttx:.2f} ms</text>')

    out.append(f'<text x="{left}" y="{y1000 + 62}" font-size="13" fill="{INK}" '
               f'font-family="Georgia, serif">throughput = window / RTT = '
               f'64 kB / 40 ms = 13.1 Mbps at both rates</text>')
    out.append(f'<text x="{left}" y="{y1000 + 82}" font-size="12.5" fill="{HOT}" '
               f'font-family="Georgia, serif">the link rate never appears in the answer</text>')
    out.append('</svg>')
    return "".join(out)



FIGURES = {
    "bdp_window": bdp_window,
    "echo_doppler": echo_doppler,
    "improper_singularity": improper_singularity,
    "normal_shaded": normal_shaded,
    "argand_locus": argand_locus,
    "vt_graph": vt_graph,
    "circuit_divider": circuit_divider,
    "data_plot_anomaly": data_plot_anomaly,
    "network_topology": network_topology,
    "bst_chain": bst_chain,
    "standing_wave": standing_wave,
    "cubic_three_roots": cubic_three_roots,
    "spool_pull": spool_pull,
    "jit_cost_curves": jit_cost_curves,
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
