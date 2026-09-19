# -*- coding: utf-8 -*-
"""Figures for BANK SECTION 03 (S03-01 .. S03-25).

Keys are 's03-<QQ>': section 03, question QQ, zero-padded.  Every marker id is prefixed
with the figure key so it cannot collide with any other figure in the bank.

Run `python figs.py 3` from tools/bank to (re)build fig/.

Design rule, carried over from sections 1 and 2: a figure must encode the discriminator
the question turns on, not decorate the apparatus.  So the beam figure shows the two
moment arms rather than a photograph of a beam; the velocity-time graph shows the
compound shape rather than an axis with a line on it; the banked-track figure shows the
tilt of the normal reaction, because that tilt is the whole question.
"""
import math
import os

from svgkit import *


def ell(cx, cy, rx, ry, a0=0, a1=360, c=GREY, sw=1.2, n=40, extra=''):
    """A full or partial ellipse as a sampled polyline.

    Sampled rather than written as an SVG arc: the `A` command's large-arc and sweep
    flags are easy to get wrong and fail silently by enlarging the radius."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / float(n))
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return PL(pts, c, sw, 'none', extra)


def _dash(x1, y1, x2, y2, c=GREY, sw=1.2):
    return L(x1, y1, x2, y2, c, sw, ' stroke-dasharray="5 4"')


def _hatch(x, y0, y1, step=13, dx=11, dy=9, c=INK, sw=1.2):
    """Diagonal hatch ticks, to mark a fixed or rough surface."""
    out = []
    y = y0
    while y < y1:
        out.append(L(x, y, x + dx, y + dy, c, sw))
        y += step
    return out


def f_01():
    """A uniform beam on two supports with a load near one end.

    The discriminator is the LOAD'S MOMENT ARM about the far support.  The stem measures
    the load from A, so the figure must show both arms explicitly -- 2.0 m to A and 4.0 m
    to B -- or the drawing would be decoration.  The beam's weight is drawn at its centre,
    because that is the other moment the working needs.
    """
    W, H = 560, 212
    b = [mk('s03-01-ar')]
    xa, xb = 80.0, 480.0
    pm = (xb - xa) / 6.0                       # px per metre
    xl = xa + 2.0 * pm                         # the load, 2.0 m from A
    xc = (xa + xb) / 2.0                       # the beam's centre
    yb = 120.0                                 # top of the beam

    # supports first, so the beam sits on them
    for x in (xa, xb):
        b.append(PG([(x - 16, 152), (x + 16, 152), (x, 128)], INK, 1.6, '#e6eaf2'))

    # the beam
    b.append(RC(xa, yb, xb - xa, 13, '#d8dee8', INK, 1.8))

    # the load, as a block sitting on the beam
    b.append(RC(xl - 11, yb - 18, 22, 18, '#e8eef8', INK, 1.6))
    b.append(L(xl, 56, xl, yb - 22, BLUE, 2.0, ' marker-end="url(#s03-01-ar)"'))
    b.append(T(xl, 46, '360 N', 11.5, 'middle', BLUE))

    # the beam's own weight, at its centre
    b.append(L(xc, 70, xc, yb - 3, RED, 2.0, ' marker-end="url(#s03-01-ar)"'))
    b.append(T(xc, 60, '240 N', 11.5, 'middle', RED))

    # the two moment arms, which are the point of the figure
    for x1, x2, lab in ((xa, xl, '2.0 m'), (xl, xb, '4.0 m')):
        b.append(L(x1, 186, x2, 186, GREY, 1.2))
        for x in (x1, x2):
            b.append(L(x, 181, x, 191, GREY, 1.2))
        b.append(T((x1 + x2) / 2.0, 202, lab, 11, 'middle', GREY))

    b.append(T(xa, 172, 'A', 12, 'middle', INK, 'bold'))
    b.append(T(xb, 172, 'B', 12, 'middle', INK, 'bold'))
    b.append(T(xa - 34, 124, 'support', 10.5, 'middle', GREY))
    b.append(T(xb + 40, 124, 'support', 10.5, 'middle', GREY))

    return svg(W, H, 'A uniform beam AB of length 6.0 m resting on supports at each end, '
                      'carrying a 360 N load 2.0 m from A and weighing 240 N at its centre; '
                      'the moment arms 2.0 m and 4.0 m are marked', '\n'.join(b))


def f_03():
    """A block held against a rough vertical wall by a horizontal push.

    The discriminator is that the push and the weight are PERPENDICULAR and are linked
    only through friction.  So the figure has to show the push horizontal, the weight
    vertical, the normal reaction horizontal into the block, and friction vertical up the
    wall -- four arrows, no two of them along the same line.
    """
    W, H = 520, 240
    b = [mk('s03-03-ar')]
    xw = 420.0                                 # the wall face
    bx0, bx1 = 318.0, xw                       # the block
    by0, by1 = 100.0, 162.0
    cx, cy = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0

    # the wall: a heavy line with hatching to its right
    b.append(L(xw, 62, xw, 208, INK, 2.6))
    b.extend(_hatch(xw, 62, 208))

    # the block
    b.append(RC(bx0, by0, bx1 - bx0, by1 - by0, '#e8eef8', INK, 1.8))

    # the push, horizontal
    b.append(L(238, cy, bx0 - 4, cy, BLUE, 2.2, ' marker-end="url(#s03-03-ar)"'))
    b.append(T(252, cy - 12, 'push F', 11.5, 'start', BLUE))

    # the normal reaction, horizontal, from the wall into the block
    b.append(L(xw, cy + 18, bx0 + 8, cy + 18, GREEN, 2.2,
               ' marker-end="url(#s03-03-ar)"'))
    b.append(T(xw - 6, cy + 8, 'N', 11.5, 'end', GREEN))

    # friction, vertical up the wall face
    b.append(L(404, by0 - 2, 404, 56, AMBER, 2.2, ' marker-end="url(#s03-03-ar)"'))
    b.append(T(398, 48, 'friction', 11.5, 'end', AMBER))

    # the weight, vertical, through the centre
    b.append(L(cx - 26, by1, cx - 26, 210, RED, 2.2, ' marker-end="url(#s03-03-ar)"'))
    b.append(T(cx - 34, 204, 'mg', 11.5, 'end', RED))

    return svg(W, H, 'A block pressed against a rough vertical wall by a horizontal push '
                      'F; the weight acts vertically downwards, the normal reaction '
                      'horizontally from the wall, and friction vertically upwards',
               '\n'.join(b))


def f_04():
    """A bridge circuit with one arm unknown.

    The discriminator is that balance is a RATIO, not a sum or a product.  So the four
    arms are laid out as two potential dividers meeting at the detector, and every arm
    carries its own value: 3.0, 3.0 and 6.0 k on the known arms, and R on the unknown one.
    """
    W, H = 480, 288
    b = [mk('s03-04-ar')]
    xl, xr = 80.0, 420.0
    xt, xb = 250.0, 250.0
    yt, yb, ym = 62.0, 238.0, 150.0

    # the four arms
    b.append(L(xl, ym, xt, yt, INK, 1.8))
    b.append(L(xt, yt, xr, ym, INK, 1.8))
    b.append(L(xl, ym, xb, yb, INK, 1.8))
    b.append(L(xb, yb, xr, ym, INK, 1.8))

    # the detector branch
    b.append(L(xt, yt, xt, ym - 18, INK, 1.8))
    b.append(L(xt, ym + 18, xb, yb, INK, 1.8))
    b.append(CI(xt, ym, 18, INK, 1.8, '#ffffff'))
    b.append(T(xt, ym + 5, 'G', 12.5, 'middle', INK, 'bold'))

    # The supply: a battery in the left branch, with its outer terminal taken round the
    # bottom of the bridge to the right node.  The first version stopped the wire at x=24
    # and left the battery's far terminal in mid-air -- the diamond was drawn but the
    # circuit was never closed, so a reader looking for the return path found nothing.
    yret = 268.0
    b.append(L(xl, ym, 56, ym, INK, 1.8))
    b.append(L(56, 134, 56, 166, INK, 2.8))
    b.append(L(48, 143, 48, 157, INK, 1.8))
    b.append(L(48, ym, 24, ym, INK, 1.8))
    b.append(L(24, ym, 24, yret, INK, 1.8))
    b.append(L(24, yret, xr, yret, INK, 1.8))
    b.append(L(xr, yret, xr, ym, INK, 1.8))
    b.append(T(20, 126, '12 V', 11.5, 'start', GREY))

    # the arms, drawn as boxes on the midpoints of the diagonals
    arms = [((xl + xt) / 2, (ym + yt) / 2, '3.0 k&#937;', 'start', 96, 92),
            ((xt + xr) / 2, (yt + ym) / 2, '6.0 k&#937;', 'end', 404, 92),
            ((xl + xb) / 2, (ym + yb) / 2, '3.0 k&#937;', 'start', 96, 220),
            ((xb + xr) / 2, (yb + ym) / 2, 'R', 'end', 404, 220)]
    for ax, ay, lab, anch, lx, ly in arms:
        b.append(RC(ax - 17, ay - 9, 34, 18, '#ffffff', INK, 1.7))
        b.append(T(lx, ly, lab, 12, anch, INK))

    # node dots
    for nx, ny in ((xl, ym), (xr, ym), (xt, yt), (xb, yb)):
        b.append(CI(nx, ny, 4, INK, 1.6, INK))

    return svg(W, H, 'A bridge circuit: a 3.0 kilo-ohm and a 3.0 kilo-ohm arm on the left, '
                      'a 6.0 kilo-ohm arm on the upper right, an unknown resistance R on '
                      'the lower right, a galvanometer between the two junctions and a '
                      '12 volt supply across the outer nodes', '\n'.join(b))


def f_06():
    """Velocity against time for the train of S03-06: ramps up, holds, ramps down.

    The discriminator is the COMPOUND SHAPE, and specifically that the three stages are
    NOT equal in area.  A reader who treats the graph as one rectangle at the top speed
    gets 600 m and an average of 10 m/s; the true total is 450 m over 60 s.  So the figure
    has to make both ramps unmistakable and let 20 s, 50 s and 10 m/s be read exactly --
    which is what the two dashed guides do.

    (This figure previously drew an 8.0-second car journey that appears nowhere in the
    question -- a leftover from an earlier draft.  The stem's train is now what is drawn.)
    """
    W, H = 500, 282
    b = [mk('s03-06-ar')]
    x0, y0 = 84.0, 232.0
    ps = 5.5                                   # px per second
    pv = 15.0                                  # px per metre per second
    pts = [(0, 0), (20, 10), (50, 10), (60, 0)]

    for k in range(1, 7):
        b.append(L(x0 + k * 10 * ps, y0, x0 + k * 10 * ps, 56, WALL, 1.0))
    for k in range(1, 6):
        b.append(L(x0, y0 - k * 2 * pv, x0 + 60 * ps, y0 - k * 2 * pv, WALL, 1.0))

    b.append(L(x0, 56, x0, y0, INK, 1.8))
    b.append(L(x0, y0, x0 + 60 * ps, y0, INK, 1.8))

    for t in range(0, 61, 10):
        x = x0 + t * ps
        b.append(L(x, y0, x, y0 + 6, INK, 1.4))
        b.append(T(x, y0 + 21, '%g' % t, 11, 'middle', INK))
    for v in range(0, 11, 2):
        y = y0 - v * pv
        b.append(L(x0 - 6, y, x0, y, INK, 1.4))
        b.append(T(x0 - 10, y + 4, '%g' % v, 11, 'end', INK))

    # the plateau, and the guides that let both its ends be read exactly
    for t in (20, 50):
        b.append(_dash(x0 + t * ps, y0 - 10 * pv, x0 + t * ps, y0))
    b.append(_dash(x0, y0 - 10 * pv, x0 + 20 * ps, y0 - 10 * pv))
    b.append(PL([(x0 + t * ps, y0 - v * pv) for t, v in pts], BLUE, 2.6))

    # NOT <sup>.  `sup` (and `sub`) are HTML foreign-content BREAKOUT tags: inside an
    # inline <svg> the HTML parser closes the svg at that point and parses the rest of
    # the figure as HTML, so the exponent and every later label land outside the graph.
    # It fails silently -- the svg keeps its size, so a size check cannot see it.
    # tspan is the SVG-native way to raise the exponent.
    b.append(T(x0 + 4, 48, 'velocity / m s<tspan font-size="8" dy="-4">-1</tspan>',
               11.5, 'start', GREY))
    b.append(T(x0 + 60 * ps, y0 + 42, 'time / s', 11.5, 'end', GREY))

    return svg(W, H, 'A velocity-time graph for a train over 60 seconds: velocity rises '
                      'uniformly from zero to 10 metres per second over the first 20 '
                      'seconds, holds at 10 metres per second until 50 seconds, and then '
                      'falls uniformly back to zero over the last 10 seconds', '\n'.join(b))


def f_08():
    """A string fixed at both ends, vibrating in its third harmonic.

    The discriminator is the COUNT: three loops, four nodes, so the length holds three
    HALF wavelengths.  The figure has to show the three loops clearly and mark the
    interior nodes, because the whole question is whether the reader counts half
    wavelengths or full ones.
    """
    W, H = 520, 212
    b = [mk('s03-08-ar')]
    x0, x1 = 80.0, 440.0
    yc = 108.0
    amp = 42.0
    half = (x1 - x0) / 3.0                     # px per half wavelength

    # the undisturbed position
    b.append(_dash(x0, yc, x1, yc))

    # the waveform: three half wavelengths, so the loops alternate above and below
    pts = []
    for i in range(121):
        x = x0 + (x1 - x0) * i / 120.0
        pts.append((x, yc - amp * math.sin(math.pi * (x - x0) / half)))
    b.append(PL(pts, BLUE, 2.4))

    # the fixed ends
    for x in (x0, x1):
        b.append(L(x, yc - 58, x, yc + 58, INK, 2.4))
        b.extend(_hatch(x, yc - 58, yc + 58, 13, -11, 9))

    # the interior nodes, which are what the count turns on
    for k in (1, 2):
        b.append(CI(x0 + k * half, yc, 4.5, AMBER, 1.8, '#ffffff'))

    # the antinodes, marked so the three loops are unmistakable
    for k in (0.5, 1.5, 2.5):
        b.append(CI(x0 + k * half, yc - amp * (1 if int(k + 0.5) % 2 else -1), 3.5,
                    GREY, 1.4, '#ffffff'))

    b.append(L(x0, 186, x1, 186, GREY, 1.2))
    for x in (x0, x1):
        b.append(L(x, 181, x, 191, GREY, 1.2))
    b.append(T((x0 + x1) / 2.0, 202, '0.60 m', 11, 'middle', GREY))

    return svg(W, H, 'A string fixed at both ends vibrating with three loops between the '
                      'ends: four nodes including the two fixed ends, and three antinodes '
                      'alternating above and below the rest position', '\n'.join(b))


def f_10():
    """A potential divider with a load across the lower arm.

    The discriminator is that the LOAD CHANGES THE LOWER ARM.  So the load is drawn as a
    second vertical branch beside the lower resistor, both connected between the same two
    rails -- the parallel relationship is the whole point and has to be visible.

    Label placement is part of the figure, not decoration.  The first version centred each
    lower label on its own branch, so the branch WIRE ran vertically through the middle of
    "3.0 k&#937;" and through "load", splitting the text.  The collision linter reported
    "crosses 0px" -- its sampling understated it -- but at 2x the strike-through was
    obvious.  Each label now sits to the side of its wire, which is why the branches are
    120 units apart rather than 70.
    """
    W, H = 600, 264
    b = [mk('s03-10-ar')]
    xt, yb = 60.0, 220.0
    xl, xm, xr = 110.0, 400.0, 520.0

    # the two rails, each drawn once
    b.append(L(xl, xt, xr, xt, INK, 1.8))
    b.append(L(xl, yb, xr, yb, INK, 1.8))
    b.append(L(xl, xt, xl, yb, INK, 1.8))

    # the supply on the left branch.  The label sits below the lower plate: at y = 142 it
    # ran into the short plate at y = 138, which the stroke-collision check caught.
    b.append(L(xl, 126, 84, 126, INK, 2.8))
    b.append(L(xl, 138, 92, 138, INK, 1.8))
    b.append(T(xl - 16, 158, '12 V', 11.5, 'end', GREY))

    # the upper resistor, on the rail between the supply and the first junction
    b.append(RC(220, xt - 8, 46, 16, '#ffffff', INK, 1.7))
    b.append(T(243, 42, '6.0 k&#937;', 12, 'middle', INK))

    # the lower resistor, label clear to the left of its wire
    b.append(L(xm, xt, xm, yb, INK, 1.8))
    b.append(RC(xm - 8, 120, 16, 46, '#ffffff', INK, 1.7))
    b.append(T(xm - 14, 148, '3.0 k&#937;', 12, 'end', INK))

    # the load, in parallel with it, label clear to the right of its wire
    b.append(L(xr, xt, xr, yb, INK, 1.8))
    b.append(RC(xr - 8, 120, 16, 46, '#ffffff', INK, 1.7))
    b.append(T(xr + 14, 148, '3.0 k&#937;', 12, 'start', INK))
    b.append(T(xr + 14, 163, 'load', 10.5, 'start', GREY))

    for nx, ny in ((xm, xt), (xm, yb), (xr, xt), (xr, yb)):
        b.append(CI(nx, ny, 4, INK, 1.6, INK))

    return svg(W, H, 'A 12 volt supply in series with a 6.0 kilo-ohm resistor and a 3.0 '
                      'kilo-ohm resistor, with a 3.0 kilo-ohm load connected in parallel '
                      'with the lower resistor between the same two rails', '\n'.join(b))


def f_15():
    """Force against time for a short, variable push.

    The discriminator is that the impulse is the AREA, and the area is a TRIANGLE.  The
    figure therefore has to make the peak narrow and the sides sloped, and the guides
    have to let 20 N and 0.10 s be read exactly.
    """
    W, H = 500, 274
    b = [mk('s03-15-ar')]
    x0, y0 = 84.0, 222.0
    ps = 1600.0                                # px per second
    pn = 7.5                                   # px per newton

    for k in range(1, 9):
        b.append(L(x0 + k * 40, y0, x0 + k * 40, 56, WALL, 1.0))
    for k in range(1, 7):
        b.append(L(x0, y0 - k * 25, x0 + 320, y0 - k * 25, WALL, 1.0))

    b.append(L(x0, 56, x0, y0, INK, 1.8))
    b.append(L(x0, y0, x0 + 320, y0, INK, 1.8))

    for t, lab in ((0.0, '0'), (0.10, '0.10'), (0.20, '0.20')):
        x = x0 + t * ps
        b.append(L(x, y0, x, y0 + 6, INK, 1.4))
        b.append(T(x, y0 + 21, lab, 11, 'middle', INK))
    for f in range(0, 21, 10):
        y = y0 - f * pn
        b.append(L(x0 - 6, y, x0, y, INK, 1.4))
        b.append(T(x0 - 10, y + 4, str(f), 11, 'end', INK))

    px, py = x0 + 0.10 * ps, y0 - 20 * pn
    b.append(_dash(px, py, px, y0))
    b.append(_dash(x0, py, px, py))
    b.append(PL([(x0, y0), (px, py), (x0 + 320, y0)], BLUE, 2.6))

    b.append(T(x0 + 4, 48, 'force / N', 11.5, 'start', GREY))
    b.append(T(x0 + 320, y0 + 42, 'time / s', 11.5, 'end', GREY))

    return svg(W, H, 'A force-time graph: the force rises linearly from zero to a peak of '
                      '20 newtons at 0.10 seconds and falls linearly back to zero at '
                      '0.20 seconds', '\n'.join(b))


def f_16():
    """A banked track in cross-section, with the forces on the car.

    The discriminator is the TILT OF THE NORMAL REACTION.  On a banked surface the
    normal is perpendicular to the road, so it is not vertical: it has a vertical
    component that carries the weight and a horizontal component that supplies the
    centripetal force.  The figure has to show both the tilt and the two components, or
    it is just a picture of a hill.
    """
    W, H = 540, 252
    b = [mk('s03-16-ar')]
    vx, vy = 160.0, 200.0                      # the vertex where the road meets the ground
    rise, run = 150.0, 200.0                   # tan(theta) = 0.75
    ex, ey = vx + run, vy - rise

    b.append(L(60, vy, 480, vy, INK, 2.0))
    b.append(L(vx, vy, ex, ey, INK, 2.6))

    # the angle, between the road and the horizontal
    b.append(ARC(vx, vy, 54, 0, -36.87, GREY, 1.3, 20))
    b.append(T(vx + 62, vy - 8, '&#952;', 13, 'start', GREY, 'bold'))

    # the car, as a box sitting on the road
    ux, uy = run / math.hypot(run, rise), -rise / math.hypot(run, rise)
    nx, ny = uy, -ux                            # outward normal, pointing away from the ground
    cx, cy = vx + run * 0.5 - nx * 12, vy - rise * 0.5 - ny * 12
    b.append(PG([(cx + ux * 18 + nx * 10, cy + uy * 18 + ny * 10),
                 (cx + ux * 18 - nx * 10, cy + uy * 18 - ny * 10),
                 (cx - ux * 18 - nx * 10, cy - uy * 18 - ny * 10),
                 (cx - ux * 18 + nx * 10, cy - uy * 18 + ny * 10)],
                INK, 1.6, '#dfe8f6'))

    # the weight, vertically down
    b.append(L(cx, cy, cx, cy + 62, RED, 2.2, ' marker-end="url(#s03-16-ar)"'))
    b.append(T(cx + 6, cy + 56, 'mg', 11.5, 'start', RED))

    # the normal reaction, perpendicular to the road
    b.append(L(cx, cy, cx + nx * 54, cy + ny * 54, GREEN, 2.2,
               ' marker-end="url(#s03-16-ar)"'))
    b.append(T(cx + nx * 60, cy + ny * 60 + 4, 'N', 11.5, 'middle', GREEN))

    # The resolution of the normal, drawn as a dashed rectangle with N as its diagonal.
    # The first version drew only the two sides from the tail, so both dashes ended in
    # mid-air and read as stray marks crossing the car rather than as components.  A
    # rectangle whose diagonal is the vector is what makes the resolution unambiguous.
    tx, ty = cx + nx * 54, cy + ny * 54        # the tip of N
    b.append(_dash(cx, cy, cx, ty))            # vertical side  = N cos(theta)
    b.append(_dash(cx, cy, tx, cy))            # horizontal side = N sin(theta)
    b.append(_dash(cx, ty, tx, ty))            # close the rectangle
    b.append(_dash(tx, cy, tx, ty))

    b.append(T(60, 240, 'cross-section of the track, looking along the road',
               10.5, 'start', GREY))

    return svg(W, H, 'A banked track seen in cross-section, with the road surface at an '
                      'angle theta to the horizontal and a car on it; the normal reaction '
                      'is drawn perpendicular to the road with its vertical and '
                      'horizontal components shown dashed', '\n'.join(b))


def f_18():
    """A diffraction grating, with the geometry of the grating equation.

    The discriminator is the LIMIT on the angle: the order is bounded by the fact that
    sin(theta) cannot exceed one.  So the figure has to show the grating, the normal, and
    orders fanning out on both sides with theta measured from the normal -- the geometry
    the bound applies to.
    """
    W, H = 540, 268
    b = [mk('s03-18-ar')]
    gx = 150.0
    yc = 132.0

    # the grating, as a row of slits
    b.append(L(gx, 48, gx, 216, INK, 2.4))
    for k in range(9):
        y = 56 + k * 19
        b.append(L(gx - 5, y, gx + 5, y, INK, 1.8))

    # the incident beam, arriving along the normal
    b.append(L(52, yc, gx - 8, yc, BLUE, 2.2, ' marker-end="url(#s03-18-ar)"'))
    b.append(T(52, yc - 10, '500 nm', 11, 'start', BLUE))

    # The normal is the line PERPENDICULAR to the grating, which for a vertical grating is
    # horizontal.  The first version drew the grating as a vertical plane and then labelled
    # a VERTICAL dashed line "normal" -- that is the grating plane extended, not its normal,
    # and it also ran straight through the "300 lines per millimetre" caption.  At normal
    # incidence the zero order leaves along the normal, so one dashed line is both.
    b.append(_dash(gx + 8, yc, gx + 178, yc, GREY))
    b.append(T(gx + 182, yc + 4, 'normal', 10.5, 'start', GREY))

    # the orders, fanning out from the grating
    for deg, lab, ty in ((25.0, 'first order', -1), (-25.0, 'first order', 1)):
        a = math.radians(deg)
        b.append(L(gx + 8, yc, gx + 150 * math.cos(a), yc - 150 * math.sin(a),
                   GREEN, 2.0, ' marker-end="url(#s03-18-ar)"'))
        b.append(T(gx + 158, yc - 150 * math.sin(a) + (4 if ty > 0 else 0),
                   lab, 10.5, 'start', GREEN))

    # theta, measured from the normal
    b.append(ARC(gx, yc, 60, 0, -25, GREY, 1.3, 18))
    b.append(T(gx + 40, yc - 34, '&#952;', 13, 'start', GREY, 'bold'))

    # clear of the grating, which ends at y = 216
    b.append(T(gx, 240, '300 lines per millimetre', 11, 'middle', GREY))

    return svg(W, H, 'A diffraction grating with the incident beam normal to it, the '
                      'normal drawn dashed and the first order on each side at an angle '
                      'theta to the normal', '\n'.join(b))


def f_19():
    """A converging lens forming a real, inverted, magnified image.

    The discriminator is that the image is REAL and LARGER than the object.  A reader who
    stops at the image distance, or who inverts the magnification ratio, contradicts what
    the rays plainly do -- so the figure has to show all three standard rays converging
    beyond the lens onto an inverted image.
    """
    W, H = 560, 284
    b = [mk('s03-19-ar')]
    yc = 150.0
    xl = 200.0                                 # the lens
    xo = 80.0                                  # the object
    xi = 440.0                                 # the image
    xf1, xf2 = 120.0, 280.0                    # the two focal points
    ho, hi = 30.0, 60.0

    b.append(L(40, yc, 520, yc, INK, 1.4))
    b.append(L(xl, 62, xl, 238, INK, 2.0))
    b.append(PL([(xl - 7, 76), (xl, 60), (xl + 7, 76)], INK, 2.0))
    b.append(PL([(xl - 7, 224), (xl, 240), (xl + 7, 224)], INK, 2.0))

    for xf in (xf1, xf2):
        b.append(CI(xf, yc, 4, GREY, 1.6, '#ffffff'))
        b.append(T(xf, yc + 20, 'F', 12, 'middle', GREY, 'bold'))

    # the object and the image
    b.append(L(xo, yc, xo, yc - ho, INK, 2.4, ' marker-end="url(#s03-19-ar)"'))
    b.append(T(xo, yc - ho - 8, 'object', 11, 'middle', INK))
    b.append(L(xi, yc, xi, yc + hi, BLUE, 2.4, ' marker-end="url(#s03-19-ar)"'))
    b.append(T(xi, yc + hi + 18, 'image', 11, 'middle', BLUE))

    # the three standard rays
    b.append(L(xo, yc - ho, xl, yc - ho, AMBER, 1.8))
    b.append(L(xl, yc - ho, xi, yc + hi, AMBER, 1.8))
    b.append(L(xo, yc - ho, xl, yc + hi, GREEN, 1.8))
    b.append(L(xl, yc + hi, xi, yc + hi, GREEN, 1.8))
    b.append(L(xo, yc - ho, xl, yc, PURPLE, 1.8))
    b.append(L(xl, yc, xi, yc + hi, PURPLE, 1.8))

    b.append(T(520, yc + 18, 'principal axis', 10.5, 'end', GREY))

    return svg(W, H, 'A ray diagram for a converging lens: an object 30 centimetres from '
                      'the lens with a focal length of 20 centimetres, three construction '
                      'rays converging to a real, inverted image twice the height of the '
                      'object', '\n'.join(b))


def f_21():
    """Two capacitors in series across a supply.

    The discriminator is that the CHARGE is common, so the voltages divide in inverse
    proportion to the capacitances.  The figure has to show the two capacitors in series
    -- one path, so no branch can have a different charge -- with their values marked.
    """
    W, H = 520, 232
    b = [mk('s03-21-ar')]
    xl, xr = 70.0, 450.0
    yt, yb = 74.0, 172.0

    # the two plates of each capacitor, and the leads between them
    for cx, lab in ((190.0, '2.0 &#956;F'), (330.0, '6.0 &#956;F')):
        b.append(L(cx - 6, yt - 20, cx - 6, yt + 20, INK, 2.6))
        b.append(L(cx + 6, yt - 20, cx + 6, yt + 20, INK, 2.6))
        b.append(T(cx, yt - 30, lab, 12, 'middle', INK))

    b.append(L(xl, yt, 184, yt, INK, 1.8))
    b.append(L(196, yt, 324, yt, INK, 1.8))
    b.append(L(336, yt, xr, yt, INK, 1.8))
    b.append(L(xl, yb, xr, yb, INK, 1.8))
    # The right-hand vertical.  Without it the two rails simply stop at x = 450 and the
    # series loop is open -- the same defect the bridge figure had.  A "series" circuit
    # that does not close is not a series circuit.
    b.append(L(xr, yt, xr, yb, INK, 1.8))

    # the supply, on the left branch
    b.append(L(xl, yt, xl, 108, INK, 1.8))
    b.append(L(xl - 16, 108, xl + 16, 108, INK, 2.8))
    b.append(L(xl - 8, 120, xl + 8, 120, INK, 1.8))
    b.append(L(xl, 120, xl, yb, INK, 1.8))
    b.append(T(xl - 22, 142, '12 V', 11.5, 'end', GREY))

    return svg(W, H, 'Two capacitors, 2.0 microfarad and 6.0 microfarad, connected in '
                      'series with each other across a 12 volt supply, so that the same '
                      'charge passes through both', '\n'.join(b))


FIGS = {
    's03-01': f_01,
    's03-03': f_03,
    's03-04': f_04,
    's03-06': f_06,
    's03-08': f_08,
    's03-10': f_10,
    's03-15': f_15,
    's03-16': f_16,
    's03-18': f_18,
    's03-19': f_19,
    's03-21': f_21,
}
