# -*- coding: utf-8 -*-
"""BPhO Round 0 -- BANK SECTION 05 figures (s05-01 .. s05-25).

Hand-authored inline SVG, emitted to fig/ by figs.py.  Every figure encodes the
discriminator its question turns on, never decoration:

  s05-02  the 3-4-5 geometry of the stay, so the perpendicular arm is 2.4 m
  s05-03  two independent dividers hanging off one supply, midpoints X and Y
  s05-05  the velocity-time graph itself, and nothing else carries the numbers
  s05-06  which mass the normal reaction belongs to
  s05-07  the bottom and the top of the vertical circle, one radius apart times two
  s05-08  the snapshot, whose SLOPE at each labelled point is the whole question
  s05-09  object inside the focal length, so the image cannot be on the far side
  s05-10  the diode's own characteristic -- the load line is the candidate's job
  s05-15  the square with its corner removed, and the corner it was removed from
  s05-16  the latitude angle, which is the angle in cos^2
  s05-20  the two cells facing each other, not aiding
  s05-25  the two piston areas, whose ratio is 20 and whose ratio squared is 400

Rules that fail silently if broken: marker ids carry the figure key (HTML has no id
namespace), colours are literal hex (a CSS variable resolves against the svg and comes
out black), and no <sup>/<sub> inside the markup (they are HTML breakout tags and the
parser closes the svg at them).
"""
import math

from svgkit import (ARC, CI, INK, GREY, BLUE, RED, GREEN, AMBER, PURPLE, PANEL,
                    WALL, L, PA, PG, PL, RC, T, mk, svg)

P = 's05'


def _dim(x1, y1, x2, y2, label, off=0.0, c=GREY, size=11.0):
    """A dimension line with end ticks and a centred label.

    Kept local, exactly as figs01..04 keep it, rather than promoted to svgkit: the
    shared module is imported by five figure files and a change there would have to be
    re-verified against every one of them.
    """
    out = [L(x1, y1, x2, y2, c, 1.2)]
    if abs(x2 - x1) > abs(y2 - y1):
        for x in (x1, x2):
            out.append(L(x, y1 - 5, x, y1 + 5, c, 1.2))
        out.append(T((x1 + x2) / 2.0, y1 + 15 + off, label, size, 'middle', c))
    else:
        for y in (y1, y2):
            out.append(L(x1 - 5, y, x1 + 5, y, c, 1.2))
        out.append(T(x1 - 9, (y1 + y2) / 2.0 + 4 + off, label, size, 'end', c))
    return out


def _hatch_down(y, x0, x1, step=13, dx=-9, dy=9, c=GREY, sw=1.0):
    """Ticks going down-and-left, for a rough horizontal surface at y."""
    out = []
    x = x0
    while x < x1:
        out.append(L(x, y, x + dx, y + dy, c, sw))
        x += step
    return out


def _ar(key, colour=INK):
    """A marker id that cannot collide with any other figure's.

    The id is what `mk` is given and is referenced verbatim as url(#...), so the two
    have to be written from one place.  House convention (figs01..03) is '<key>-ar'.
    """
    return mk('%s-%s-ar' % (P, key), colour)


# ═════════════════════════════════════════════════════════════════════════════
# 02 — a rod hinged at a wall, held horizontal by a cable (3-4-5)
# ═════════════════════════════════════════════════════════════════════════════
def f02():
    ar = _ar('02', RED)
    b = []
    # wall, hatched
    b.append(RC(28, 16, 12, 164, WALL))
    for i in range(0, 82, 12):
        b.append(L(28, 16 + i * 2, 40, 26 + i * 2, GREY, 0.9))
    b.append(L(40, 16, 40, 180, INK, 2.2))
    # rod A(40,140) -> B(200,140); 160 px = 4.0 m
    b.append(L(40, 140, 200, 140, INK, 3.0))
    # hinge
    b.append(CI(40, 140, 5, INK, 1.6, 'none'))
    b.append(T(20, 156, 'A', 12))
    # cable C(40,20) -> B(200,140): rise 120 px = 3.0 m, length 200 px = 5.0 m
    b.append(L(40, 20, 200, 140, BLUE, 2.0))
    b.append(CI(40, 20, 4, BLUE, 1.4, 'none'))
    b.append(T(40, 9, 'C', 12, 'middle'))
    b.append(T(206, 136, 'B', 12))
    # the loads
    b.append(L(120, 140, 120, 172, RED, 1.8, ' marker-end="url(#%s-ar)"' % ('%s-02' % P)))
    b.append(T(112, 190, '150 N', 11.5, 'middle', RED))
    b.append(L(200, 140, 200, 170, RED, 1.8, ' marker-end="url(#%s-ar)"' % ('%s-02' % P)))
    b.append(T(206, 186, '45 N', 11.5, 'start', RED))
    # the three lengths
    b.append(T(120, 132, '4.0 m', 11.5, 'middle'))
    b.append(T(60, 92, '3.0 m', 11.5, 'start'))
    b.append(T(150, 66, '5.0 m', 11.5, 'middle', BLUE))
    return svg(240, 200,
               'A horizontal rod hinged to a wall at A and held by a cable from B to a '
               'point C three metres above A. The rod is four metres long, the cable is '
               'five metres long, a weight of 150 newtons acts at the middle and a load '
               'of 45 newtons hangs from B.',
               ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 03 — two dividers across one supply, with an ideal voltmeter between X and Y
# ═════════════════════════════════════════════════════════════════════════════
def f03():
    b = []
    # supply
    b.append(L(40, 150, 40, 210, INK, 2.0))
    b.append(L(30, 176, 50, 176, INK, 2.6))
    b.append(L(24, 170, 36, 170, INK, 2.6))
    b.append(T(6, 182, '12 V', 11.5))
    # top rail and bottom rail
    b.append(L(40, 150, 240, 150, INK, 2.0))
    b.append(L(40, 210, 240, 210, INK, 2.0))
    # left branch: 2.0 then 6.0, midpoint X
    b.append(L(90, 150, 90, 168, INK, 1.8))
    b.append(RC(80, 168, 20, 14, PANEL, INK, 1.6))
    b.append(T(74, 180, '2.0', 10.5, 'end'))
    b.append(L(90, 182, 90, 194, INK, 1.8))
    b.append(RC(80, 194, 20, 14, PANEL, INK, 1.6))
    b.append(T(74, 206, '6.0', 10.5, 'end'))
    b.append(L(90, 208, 90, 210, INK, 1.8))
    # right branch: 6.0 then 3.0, midpoint Y
    b.append(L(190, 150, 190, 168, INK, 1.8))
    b.append(RC(180, 168, 20, 14, PANEL, INK, 1.6))
    b.append(T(206, 180, '6.0', 10.5, 'start'))
    b.append(L(190, 182, 190, 194, INK, 1.8))
    b.append(RC(180, 194, 20, 14, PANEL, INK, 1.6))
    b.append(T(206, 206, '3.0', 10.5, 'start'))
    b.append(L(190, 208, 190, 210, INK, 1.8))
    # midpoints -- labels sit in the clear gap, off the vertical wires
    b.append(CI(90, 188, 3.4, BLUE, 1.4, BLUE))
    b.append(CI(190, 188, 3.4, BLUE, 1.4, BLUE))
    b.append(T(104, 177, 'X', 12, 'middle', BLUE))
    b.append(T(176, 177, 'Y', 12, 'middle', BLUE))
    # the ideal voltmeter between them
    b.append(L(90, 188, 120, 188, BLUE, 1.6))
    b.append(L(160, 188, 190, 188, BLUE, 1.6))
    b.append(CI(140, 188, 16, BLUE, 1.8, 'none'))
    b.append(T(140, 194, 'V', 13, 'middle', BLUE))
    b.append(T(140, 136, 'ideal', 10.5, 'middle', GREY))
    return svg(250, 230,
               'A 12 volt supply feeds two branches in parallel. The left branch is 2.0 '
               'ohms above its midpoint X and 6.0 ohms below it; the right branch is 6.0 '
               'ohms above its midpoint Y and 3.0 ohms below it. An ideal voltmeter '
               'bridges X and Y.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 05 — the velocity-time graph, and the axes carry every number
# ═════════════════════════════════════════════════════════════════════════════
def f05():
    b = []
    x0, y0, x1, y1 = 56, 44, 244, 158          # plot box
    b.append(L(x0, y0, x0, y1, INK, 1.8))
    b.append(L(x0, y1, x1, y1, INK, 1.8))
    # axis titles well clear of the plot and the tick numbers
    b.append(T(8, 16, 'velocity', 11.5))
    b.append(T(8, 28, '/ m s', 10.5, 'start', GREY))
    b.append(T(148, 192, 'time / s', 11.5, 'middle'))
    # 20 m/s gridline (top of the y-axis) and its number, left of the axis
    b.append(L(x0, y0, x1, y0, GREY, 0.9, ' stroke-dasharray="4 4"'))
    b.append(T(x0 - 6, y0 + 4, '20', 11, 'end'))
    b.append(T(x0 - 6, y1 + 4, '0', 11, 'end'))
    # time marks: 0, 5, 15, 19
    def X(t):
        return x0 + (x1 - x0) * t / 22.0
    for t in (5, 15, 19):
        b.append(L(X(t), y1, X(t), y1 + 5, INK, 1.4))
        b.append(T(X(t), y1 + 18, str(t), 11, 'middle'))
    # the graph itself
    b.append(PL([(X(0), y1), (X(5), y0), (X(15), y0), (X(19), y1)], BLUE, 2.4))
    b.append(T(X(2.5), y0 - 10, 'accelerating', 10.5, 'middle', GREY))
    b.append(T(X(10), y0 - 10, 'steady', 10.5, 'middle', GREY))
    b.append(T(X(17), y0 - 10, 'braking', 10.5, 'middle', GREY))
    return svg(280, 208,
               'A velocity-time graph. The velocity rises in a straight line from zero '
               'to 20 metres per second over the first 5 seconds, stays at 20 metres per '
               'second until 15 seconds, then falls in a straight line back to zero at '
               '19 seconds.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 06 — two blocks, a string and a pulley: which mass sets the normal reaction
# ═════════════════════════════════════════════════════════════════════════════
def f06():
    """The discriminator is WHERE the rough surface begins.

    The ramp is smooth, so the ball keeps every joule of the 2.0 J it gained on the way
    down; friction starts only at the foot of the ramp, and the hatching shows that the
    rough surface then continues PAST the second ball, so the combined mass is still
    being retarded after the collision.  A figure that hatched the whole floor would
    hide the fact that the first stretch is the only place friction does work before the
    collision.
    """
    ar = _ar('06', BLUE)
    b = []
    yS, xR, xC = 190.0, 220.0, 370.0

    # the ramp and its height
    b.append(PA('M110,70 L220,190 L110,190 z', INK, 1.8, 'none'))
    b += _dim(80, 70, 80, 190, '0.40 m')
    b.append(T(150, 134, 'smooth', 10.5, 'end', GREY))

    # the floor, rough from the foot of the ramp onwards
    b.append(L(60, yS, 560, yS, INK, 1.8))
    b += _hatch_down(yS, 224, 558)
    b.append(T(468, 220, 'rough, mu = 0.20', 11, 'middle', GREY))

    # the first ball, released from rest at the top
    b.append(CI(110, 70, 7, BLUE, 1.6, '#dbe6fb'))
    b.append(T(122, 56, '0.50 kg', 11.5, 'start', BLUE, 'bold'))
    b.append(L(250, 174, 332, 174, BLUE, 2.0, ' marker-end="url(#%s-ar)"' % (P + '-06')))

    # the second ball, at rest
    b.append(CI(370, 182, 8, RED, 1.6, '#fbe0de'))
    b.append(T(370, 158, '0.30 kg, at rest', 11, 'middle', RED))

    # the 1.0 m of rough surface before the collision
    b.append(L(xR, 240, xC, 240, GREY, 1.2))
    for x in (xR, xC):
        b.append(L(x, 235, x, 245, GREY, 1.2))
        b.append(L(x, 201, x, 240, GREY, 1.2, ' stroke-dasharray="4 4"'))
    b.append(T(295, 258, '1.0 m', 11, 'middle', GREY))

    # after the collision
    b.append(L(384, 190, 500, 190, GREY, 2.0,
               ' stroke-dasharray="7 5" marker-end="url(#%s-ar)"' % (P + '-06')))
    b.append(T(442, 178, 'how far?', 11, 'middle', BLUE, 'bold'))

    return svg(580, 300,
               'A 0.50 kilogram ball released from rest at the top of a smooth ramp 0.40 '
               'metres high; it reaches a rough horizontal surface, slides 1.0 metre and '
               'then sticks to a 0.30 kilogram ball at rest, the two continuing over the '
               'same rough surface',
               ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 07 — a vertical circle: the string must still be taut at the top
# ═════════════════════════════════════════════════════════════════════════════
def f07():
    ar = _ar('07', BLUE)
    cx, cy, r = 130, 118, 66
    b = []
    b.append(CI(cx, cy, r, GREY, 1.2, 'none'))
    b.append(L(cx, cy - r, cx, cy + r, GREY, 0.9, ' stroke-dasharray="4 4"'))
    b.append(L(cx, cy, cx + r, cy, GREY, 0.9, ' stroke-dasharray="4 4"'))
    b.append(T(cx + 8, cy + 4, 'r', 11.5, 'start', GREY))
    # the particle at the bottom, speed u
    b.append(CI(cx, cy + r, 7, BLUE, 1.6, BLUE))
    b.append(L(cx, cy + r + 12, cx + 44, cy + r + 12, BLUE, 1.6,
               ' marker-end="url(#%s-ar)"' % ('%s-07' % P)))
    b.append(T(cx + 24, cy + r + 30, 'u', 12, 'middle', BLUE))
    b.append(T(cx - 12, cy + r + 30, 'lowest', 10.5, 'end', GREY))
    # the particle at the top, ghosted
    b.append(CI(cx, cy - r, 7, INK, 1.6, PANEL))
    b.append(T(cx + 14, cy - r - 8, 'highest', 10.5, 'start', GREY))
    b.append(L(cx, cy - r - 20, cx, cy - r - 34, GREY, 1.2))
    return svg(230, 232,
               'A particle on a light string describing a vertical circle of radius r. '
               'Its speed at the lowest point is u and the string must remain taut all '
               'the way round, including at the highest point, two radii above.',
               ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 08 — a snapshot of a right-travelling wave; the slope is the velocity
# ═════════════════════════════════════════════════════════════════════════════
def f08():
    ar = _ar('08', BLUE)
    b = []
    x0, ymid, x1, amp = 40, 96, 300, 46
    pts = []
    for i in range(241):
        t = i / 240.0
        pts.append((x0 + (x1 - x0) * t, ymid - amp * math.sin(2 * math.pi * 1.5 * t)))
    b.append(PL(pts, INK, 2.2))
    b.append(L(x0 - 8, ymid, x1, ymid, GREY, 1.0, ' stroke-dasharray="5 4"'))
    # labelled points at fixed fractions of a wavelength
    def pt(phase):
        return (x0 + (x1 - x0) * phase / (2 * math.pi) * (2 * math.pi / 1.5) / (2 * math.pi / 1.5),
                ymid)
    # place P..T at phases 0, pi/2, pi, 3pi/2 and one off-crest point
    names = [('P', 0.0), ('Q', math.pi / 2.0), ('R', math.pi), ('S', 3 * math.pi / 2.0),
             ('T', 0.25)]
    for nm, ph in names:
        frac = (ph / (2 * math.pi)) / 1.5
        x = x0 + (x1 - x0) * frac
        y = ymid - amp * math.sin(1.5 * 2 * math.pi * frac)
        b.append(CI(x, y, 4.6, RED, 1.4, RED))
        b.append(T(x, ymid + 62, nm, 12, 'middle', RED))
        b.append(L(x, ymid + 44, x, ymid + 52, GREY, 0.9, ' stroke-dasharray="3 3"'))
    b.append(L(x1 - 46, 30, x1 - 10, 30, BLUE, 1.6,
               ' marker-end="url(#%s-ar)"' % ('%s-08' % P)))
    b.append(T(x1 - 78, 34, 'travel', 10.5, 'start', BLUE))
    return svg(316, 190,
               'A snapshot of a transverse wave travelling to the right along a string. '
               'Five points P, Q, R, S and T are marked on it: P sits on a crest, Q and '
               'S where the string crosses the axis, R in a trough, and T part way up a '
               'rising flank.',
               ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 09 — a converging lens with the object inside its focal length
# ═════════════════════════════════════════════════════════════════════════════
def f09():
    b = []
    y = 104
    b.append(L(24, y, 290, y, INK, 1.6))
    b.append(PA('M150,%g Q138,%g 138,%g Q138,%g 150,%g Q162,%g 162,%g Q162,%g 150,%g Z'
                % (y - 42, y - 20, y, y + 20, y + 42, y + 20, y, y - 20, y - 42),
                BLUE, 2.0, '#dbe6fb'))
    # object 12 cm to the left of the lens
    b.append(L(102, y, 102, y - 38, INK, 2.4))
    b.append(L(102, y - 38, 108, y - 30, INK, 1.8))
    b.append(L(102, y - 38, 96, y - 30, INK, 1.8))
    b.append(T(102, y + 20, 'object', 10.5, 'middle'))
    # scale bar: 48 px = 12 cm, so 4 px = 1 cm
    b.append(L(102, y + 34, 150, y + 34, GREY, 1.2))
    b.append(L(102, y + 30, 102, y + 38, GREY, 1.2))
    b.append(L(150, y + 30, 150, y + 38, GREY, 1.2))
    b.append(T(126, y + 52, '12 cm', 11, 'middle', GREY))
    # the focal length, drawn to the RIGHT of the lens so it cannot be read as
    # an image position: 80 px = 20 cm
    b.append(L(150, y + 74, 230, y + 74, AMBER, 1.4))
    b.append(L(150, y + 70, 150, y + 78, AMBER, 1.4))
    b.append(L(230, y + 70, 230, y + 78, AMBER, 1.4))
    b.append(T(190, y + 94, 'f = 20 cm', 11, 'middle', AMBER))
    b.append(T(150, y - 52, 'converging lens', 10.5, 'middle', BLUE))
    return svg(300, 220,
               'A converging lens of focal length 20 centimetres with an object 12 '
               'centimetres to its left. The scale bar shows the object distance and the '
               'focal length is drawn below the axis for scale.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 10 — the diode's own I-V characteristic
# ═════════════════════════════════════════════════════════════════════════════
def f10():
    b = []
    x0, y0, x1, y1 = 54, 24, 250, 180          # plot box; 10 mA = 40 px, 1 V = 60 px
    b.append(L(x0, y0, x0, y1, INK, 1.8))
    b.append(L(x0, y1, x1, y1, INK, 1.8))
    b.append(T(4, 40, 'current', 11.5))
    b.append(T(4, 54, '/ mA', 10.5, 'start', GREY))
    b.append(T(150, y1 + 33, 'potential difference / V', 11, 'middle'))
    for v in (0.2, 0.4, 0.6, 0.8, 1.0):
        x = x0 + 196 * v
        b.append(L(x, y1, x, y1 + 4, INK, 1.2))
        b.append(T(x, y1 + 16, ('%.1f' % v), 10.5, 'middle'))
    for i in (10, 20, 30, 40):
        y = y1 - 4 * i
        b.append(L(x0 - 4, y, x0, y, INK, 1.2))
        b.append(T(x0 - 8, y + 4, str(i), 10.5, 'end'))
    # the characteristic: flat, then a knee near 0.6 V, then steep; drawn to pass
    # through (0.8 V, 22 mA) exactly, which is where the 100 ohm load line crosses,
    # and to reach 40 mA at 1.0 V.
    pts = [(x0 + 196 * v / 100.0, y1) for v in range(0, 56, 4)]
    for v10 in range(56, 83, 2):
        v = v10 / 100.0
        mA = 22.0 * (v - 0.55) / (0.82 - 0.55)
        pts.append((x0 + 196 * v, y1 - 4 * mA))
    for v10 in range(83, 101, 2):
        v = v10 / 100.0
        mA = 22.0 + (v - 0.82) / 0.18 * 18.0
        pts.append((x0 + 196 * v, y1 - 4 * mA))
    b.append(PL(pts, BLUE, 2.4))
    b.append(T(x0 + 96, y1 - 96, 'diode', 11, 'middle', BLUE))
    return svg(270, 224,
               'The current-voltage characteristic of a diode. The current is negligible '
               'up to about 0.6 volts, then rises steeply; the drawn curve passes through '
               '22 milliamps at 0.8 volts and 40 milliamps at 1.0 volts.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 15 — a square lamina with one corner removed
# ═════════════════════════════════════════════════════════════════════════════
def f15():
    b = []
    big = 132
    x0, y0 = 44, 30
    b.append(RC(x0, y0, big, big, PANEL, INK, 2.0))
    b.append(RC(x0, y0, big / 2.0, big / 2.0, WALL, GREY, 1.2))
    b.append(L(x0, y0, x0 + big / 2.0, y0 + big / 2.0, GREY, 1.0,
               ' stroke-dasharray="4 4"'))
    b.append(T(x0 + 26, y0 + 40, 'cut', 10.5, 'middle', GREY))
    # the remaining L, outlined to show the true shape
    b.append(PL([(x0 + big / 2.0, y0), (x0 + big, y0), (x0 + big, y0 + big),
                 (x0, y0 + big), (x0, y0 + big / 2.0), (x0 + big / 2.0, y0 + big / 2.0),
                 (x0 + big / 2.0, y0)], INK, 2.4))
    # the original centre
    b.append(CI(x0 + big / 2.0, y0 + big / 2.0, 4, BLUE, 1.4, BLUE))
    b.append(T(x0 + big / 2.0 + 10, y0 + big / 2.0 + 4, 'centre of the', 10, 'start', BLUE))
    b.append(T(x0 + big / 2.0 + 10, y0 + big / 2.0 + 17, 'whole square', 10, 'start', BLUE))
    # dimensions
    b.append(L(x0, y0 + big + 14, x0 + big, y0 + big + 14, GREY, 1.2))
    b.append(L(x0, y0 + big + 10, x0, y0 + big + 18, GREY, 1.2))
    b.append(L(x0 + big, y0 + big + 10, x0 + big, y0 + big + 18, GREY, 1.2))
    b.append(T(x0 + big / 2.0, y0 + big + 32, '2a', 11.5, 'middle'))
    b.append(L(x0 - 14, y0, x0 - 14, y0 + big / 2.0, GREY, 1.2))
    b.append(L(x0 - 18, y0, x0 - 10, y0, GREY, 1.2))
    b.append(L(x0 - 18, y0 + big / 2.0, x0 - 10, y0 + big / 2.0, GREY, 1.2))
    b.append(T(x0 - 20, y0 + big / 4.0, 'a', 11.5, 'end'))
    return svg(240, 196,
               'A square lamina of side 2a with a square of side a removed from its '
               'upper-left corner. The centre of the original, uncut square is marked.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 16 — the latitude, which is the angle inside the cosine
# ═════════════════════════════════════════════════════════════════════════════
def f16():
    cx, cy, r = 118, 108, 74
    b = []
    b.append(CI(cx, cy, r, INK, 1.8, '#eef3fb'))
    # equator and axis
    b.append(L(cx - r, cy, cx + r, cy, INK, 1.6))
    b.append(L(cx, cy - r - 14, cx, cy + r + 14, GREY, 1.2, ' stroke-dasharray="5 4"'))
    b.append(T(cx - r - 4, cy - 6, 'equator', 10.5, 'end', GREY))
    # the point at latitude lambda
    lam = math.radians(45)
    px, py = cx + r * math.cos(lam), cy - r * math.sin(lam)
    b.append(L(cx, cy, px, py, INK, 1.4))
    b.append(CI(px, py, 5, RED, 1.5, RED))
    # radius to the axis, which is r cos(lambda)
    ax = cx
    b.append(L(px, py, ax, py, BLUE, 2.0))
    b.append(T((px + ax) / 2.0, py - 8, 'r cos', 11, 'middle', BLUE))
    b.append(ARC(cx, cy, 30, -lam * 180 / math.pi, 0, RED, 1.4))
    b.append(T(cx + 34, cy - 16, 'lat.', 11, 'start', RED))
    # the rotation arrow
    b.append(PA('M%g,%g A%g,%g 0 0 1 %g,%g' % (cx - r - 10, cy - 22, r + 16, 26,
                                               cx + r + 10, cy - 22),
                GREY, 1.4, 'none', ' marker-end="url(#s05-16-ar)"'))
    b.append(T(cx, cy - r - 26, 'rotation', 10, 'middle', GREY))
    return svg(240, 216,
               'A sphere rotating about a vertical axis. A point at latitude lambda is '
               'marked; its distance from the rotation axis is r times cos lambda, while '
               'its distance from the centre is r.',
               mk('s05-16-ar', GREY) + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 20 — two cells in opposition
# ═════════════════════════════════════════════════════════════════════════════
def f20():
    b = []
    b.append(RC(36, 62, 208, 116, 'none', INK, 1.8))
    # top rail: the 3.0 ohm resistor
    b.append(L(36, 62, 92, 62, INK, 1.8))
    b.append(RC(92, 52, 34, 20, PANEL, INK, 1.8))
    b.append(T(109, 44, '3.0', 10.5, 'middle'))
    b.append(L(126, 62, 244, 62, INK, 1.8))
    # right side: the 12 V cell, positive UP
    b.append(L(244, 62, 244, 92, INK, 1.8))
    b.append(L(234, 100, 254, 100, INK, 2.6))
    b.append(L(240, 108, 248, 108, INK, 2.6))
    b.append(L(244, 108, 244, 130, INK, 1.8))
    b.append(T(258, 104, '12 V, 1.0', 10.5, 'start'))
    b.append(T(258, 118, 'internal', 10, 'start', GREY))
    # bottom rail
    b.append(L(244, 178, 36, 178, INK, 1.8))
    # left side: the 6 V cell, positive DOWN -- that is what opposition means
    b.append(L(36, 178, 36, 152, INK, 1.8))
    b.append(L(44, 144, 28, 144, INK, 2.6))
    b.append(L(38, 136, 34, 136, INK, 2.6))
    b.append(L(36, 136, 36, 62, INK, 1.8))
    b.append(T(50, 140, '6.0 V, 2.0', 10.5, 'start'))
    b.append(T(50, 154, 'internal', 10, 'start', GREY))
    b.append(T(140, 110, 'the cells face', 11, 'middle', RED))
    b.append(T(140, 124, 'opposite ways', 11, 'middle', RED))
    return svg(322, 200,
               'A single loop containing a 3.0 ohm resistor, a 12 volt cell of internal '
               'resistance 1.0 ohm with its positive terminal uppermost, and a 6.0 volt '
               'cell of internal resistance 2.0 ohms with its positive terminal '
               'lowermost, so the two cells oppose each other.',
               '\n'.join(b))


def f22():
    """The discriminator is the RELATIVE SIZE of the three stages.

    The bar for melting the ice is more than three times the other two bars put
    together, and it is the stage with no temperature change in it -- so a candidate
    who leaves the latent heat out is looking at a figure that says so.  The bars are
    drawn to scale and are not labelled with their values: the figure shows which stage
    dominates, the arithmetic is still the candidate's job.
    """
    b = []
    base = 200.0
    px = 150.0 / 165000.0                    # pixels per joule
    for x, e in ((110, 10500), (240, 165000), (370, 42000)):
        h = e * px
        b.append(RC(x, base - h, 76, h, '#dbe6fb', INK, 1.4))
    b.append(L(70, base, 520, base, INK, 1.8))
    for x, one, two in ((148, 'warm the ice', '&#8722;10 to 0 &#176;C'),
                        (278, 'melt the ice', 'at 0 &#176;C'),
                        (408, 'warm the water', '0 to 20 &#176;C')):
        b.append(T(x, 218, one, 10.5, 'middle', INK))
        b.append(T(x, 232, two, 10.5, 'middle', GREY))
    b.append(T(295, 258, 'the three stages, drawn in proportion to the energy each needs',
               10.5, 'middle', AMBER))
    return svg(560, 272,
               'Three bars, drawn to scale, showing the energy needed for the three '
               'stages of turning ice at minus ten degrees into water at twenty degrees: '
               'melting the ice is by far the largest',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 25 — a hydraulic jack: two areas whose ratio is twenty
# ═════════════════════════════════════════════════════════════════════════════
def f25():
    ar = _ar('25', RED)
    b = []
    # the fluid
    b.append(RC(40, 96, 210, 56, '#dbe6fb', INK, 1.6))
    # the narrow limb
    b.append(RC(74, 40, 30, 60, PANEL, INK, 1.6))
    b.append(RC(74, 74, 30, 14, '#dbe6fb', INK, 1.2))
    b.append(RC(74, 74, 30, 14, BLUE, 'none', 0))
    b.append(RC(72, 62, 34, 12, BLUE, INK, 1.6))
    b.append(T(89, 54, '2.0 sq cm', 10.5, 'middle'))
    b.append(L(89, 40, 89, 22, RED, 1.8, ' marker-end="url(#%s-ar)"' % ('%s-25' % P)))
    b.append(T(96, 30, '100 N', 11.5, 'start', RED))
    # the wide limb
    b.append(RC(186, 66, 64, 44, PANEL, INK, 1.6))
    b.append(RC(186, 66, 64, 44, '#dbe6fb', INK, 1.2))
    b.append(RC(182, 52, 72, 14, BLUE, INK, 1.6))
    b.append(T(220, 88, '40 sq cm', 10.5, 'middle', INK))
    b.append(L(218, 52, 218, 30, INK, 1.8))
    b.append(T(188, 44, 'load', 11.5, 'middle', INK))
    # the 20 cm travel of the small piston
    b.append(L(112, 66, 112, 118, GREY, 1.2, ' stroke-dasharray="4 4"'))
    b.append(L(104, 66, 120, 66, GREY, 1.2))
    b.append(L(104, 118, 120, 118, GREY, 1.2))
    b.append(T(126, 96, '20 cm', 11, 'start', GREY))
    return svg(288, 168,
               'A hydraulic jack: a piston of area 2.0 square centimetres pushed down '
               'with a force of 100 newtons through 20 centimetres, and a load piston of '
               'area 40 square centimetres.',
               ar + '\n' + '\n'.join(b))


FIGS = {
    's05-02': f02,
    's05-03': f03,
    's05-05': f05,
    's05-06': f06,
    's05-07': f07,
    's05-08': f08,
    's05-09': f09,
    's05-10': f10,
    's05-15': f15,
    's05-16': f16,
    's05-20': f20,
    's05-22': f22,
    's05-25': f25,
}
