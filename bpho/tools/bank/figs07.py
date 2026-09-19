# -*- coding: utf-8 -*-
"""BPhO Round 0 -- BANK SECTION 07 figures (s07-01 .. s07-25).

Hand-authored inline SVG, emitted to fig/ by figs.py.  Every figure encodes the
discriminator its question turns on, never decoration:

  s07-02  the slab and its three dimensions, because the whole question is which
          of them to multiply and which to leave in grams
  s07-04  H and R on one trajectory, so that the ratio the question asks for is a
          ratio of two labelled lengths on the same picture
  s07-05  the velocity triangle at the point of impact: the two components come
          from different places, and the figure says so
  s07-07  the disc, the hole and the two centres -- the offset a is the only
          length that matters, and the answer's direction is visible in it
  s07-09  which face is 60 degrees and which is 30 degrees, with both normals
          drawn, because the two answers differ by a factor of root three
  s07-10  the top point marked on the rim, with the road and the centre below it
  s07-14  the eye, the mirror plane and the two extreme rays: the ray that reaches
          the top of the head and the ray that reaches the feet
  s07-17  the topology -- two branches that leave one node and rejoin at another
  s07-18  the potentiometer wire with the two balance points marked on one ruler
  s07-19  the loop: supply, resistor and capacitor in series, so the charge that
          passes through each of them is the same charge
  s07-22  the recorded decay curve itself, whose flattened tail is the whole
          question -- a constant background has been added to something decaying
  s07-24  the stopping-potential line, whose crossing of the axis is the only
          number the question takes from it
  s07-25  the lamp, the sphere of radius 3.0 m and the detector on it: the geometry
          enters as a ratio of two areas and never as a distance compared with a size

Rules that fail silently if broken: marker ids carry the figure key (HTML has no id
namespace), colours are literal hex (a CSS variable resolves against the svg and comes
out black), and no <sup>/<sub> inside the markup (they are HTML breakout tags and the
parser closes the svg at them -- exponents are <tspan>).
"""
import math

from svgkit import (ARC, CI, INK, GREY, BLUE, RED, GREEN, AMBER, PURPLE, PANEL,
                    WALL, L, PA, PG, PL, RC, T, mk, svg)

P = 's07'


def _dim(x1, y1, x2, y2, label, off=0.0, c=GREY, size=11.0, anchor=None):
    """A dimension line with end ticks and a label.

    Kept local, exactly as figs01..06 keep it, rather than promoted to svgkit: the
    shared module is imported by seven figure files and a change there would have to
    be re-verified against every one of them.
    """
    out = [L(x1, y1, x2, y2, c, 1.2)]
    if abs(x2 - x1) > abs(y2 - y1):
        for x in (x1, x2):
            out.append(L(x, y1 - 5, x, y1 + 5, c, 1.2))
        out.append(T((x1 + x2) / 2.0, y1 + 15 + off, label, size, anchor or 'middle', c))
    else:
        for y in (y1, y2):
            out.append(L(x1 - 5, y, x1 + 5, y, c, 1.2))
        out.append(T(x1 - 9, (y1 + y2) / 2.0 + 4 + off, label, size, anchor or 'end', c))
    return out


def _ar(key, colour=INK):
    """A marker id that cannot collide with any other figure's.

    HTML has no id namespace, so two figures that both define `id="ar"` silently give
    one of them the wrong arrowhead.  House convention (figs01..06) is '<key>-ar'.
    """
    return mk('%s-%s-ar' % (P, key), colour)


def _dash(x1, y1, x2, y2, c=GREY, sw=1.0):
    return L(x1, y1, x2, y2, c, sw, ' stroke-dasharray="5 4"')


def _ticks(pts, dx, dy, c=GREY, sw=0.9):
    """Short hatch ticks, used to mark a surface as solid or a region as removed."""
    return [L(x, y, x + dx, y + dy, c, sw) for (x, y) in pts]


def _grid(xs, ys, x0, x1, y0, y1, c=WALL, sw=1.0):
    out = []
    for x in xs:
        out.append(L(x, y0, x, y1, c, sw))
    for y in ys:
        out.append(L(x0, y, x1, y, c, sw))
    return out


def _axes(x0, y0, x1, y1, c=INK, sw=1.8):
    """Two axes with small arrowheads, drawn as plain lines plus triangles."""
    out = [L(x0, y0, x1, y0, c, sw), L(x0, y0, x0, y1, c, sw)]
    out.append(PG([(x1, y0), (x1 - 8, y0 - 4), (x1 - 8, y0 + 4)], c, 0.6, c))
    out.append(PG([(x0, y1), (x0 - 4, y1 + 8), (x0 + 4, y1 + 8)], c, 0.6, c))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# 02 -- the cloud as a slab, with all three dimensions on it
# ═════════════════════════════════════════════════════════════════════════════
def f02():
    b = []
    f0, f1, f2, f3 = (80, 195), (330, 195), (330, 125), (80, 125)     # front face
    b1, b2, b3 = (385, 150), (385, 80), (135, 80)                      # back face
    b.append(PG([f3, f2, b2, b3], GREY, 1.4, PANEL))                   # top
    b.append(PG([f2, b2, b1, f1], GREY, 1.4, WALL))                    # right
    b.append(PG([f3, f2, f1, f0], GREY, 1.4, PANEL))                   # front
    b.append(T(205, 166, 'cloud', 13, 'middle', GREY))
    # the width, along the bottom
    b += _dim(80, 215, 330, 215, '1.0 km')
    # the depth, along the top face's receding edge
    b.append(_dash(330, 125, 342, 116))
    b.append(_dash(385, 80, 397, 71))
    b += _dim(342, 116, 397, 71, '1.0 km', anchor='start')
    # the height, on the left
    b += _dim(62, 125, 62, 195, '500 m')
    return svg(470, 250,
               'A cloud drawn as a rectangular slab one kilometre long, one kilometre '
               'wide and five hundred metres deep.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 04 -- the trajectory with H and R both labelled on it
# ═════════════════════════════════════════════════════════════════════════════
def f04():
    ar = _ar('04', INK)
    b = []
    yg = 200.0
    ax, bx = 60.0, 400.0
    apex_x, apex_y = 230.0, 128.0
    k = (yg - apex_y) / (bx - apex_x) ** 2
    b.append(L(45, yg, 440, yg, INK, 2.0))
    b += _ticks([(x, yg) for x in range(50, 436, 15)], -9, 9)
    pts = [(x, apex_y + k * (x - apex_x) ** 2) for x in range(60, 401, 4)]
    b.append(PL(pts, BLUE, 2.6))
    # the angle at the launch
    slope = 2 * k * (ax - apex_x)
    ang = math.degrees(math.atan(-slope))          # above the horizontal
    b.append(ARC(ax, yg, 52, -ang, 0, GREY, 1.3))
    b.append(T(ax + 66 * math.cos(math.radians(-ang / 2)),
               yg + 66 * math.sin(math.radians(-ang / 2)) + 4, '&#952;', 13, 'start'))
    # the launch direction -- the tangent to the curve at the launch point.
    # `slope` is dy/dx in SVG coordinates (y downward), and it is already negative
    # here because the curve rises to the right, so the direction vector is
    # (1, slope) and NOT (1, -slope): negating it points the arrow back down the
    # slope, which no lint can see and a screenshot shows at once.
    ux, uy = 1.0, slope
    n = math.hypot(ux, uy)
    b.append(L(ax, yg, ax + 70 * ux / n, yg + 70 * uy / n, RED, 2.0,
               ' marker-end="url(#%s-04-ar)"' % P))
    b.append(T(ax + 30 * ux / n, yg + 30 * uy / n - 8, 'u', 12.5, 'middle', RED))
    # the apex and the height
    b.append(CI(apex_x, apex_y, 3.2, BLUE, 1.2, BLUE))
    b.append(_dash(apex_x, apex_y, apex_x, yg))
    b.append(T(apex_x + 8, (apex_y + yg) / 2.0 + 4, 'H', 12.5, 'start'))
    b += _dim(ax, 222, bx, 222, 'R')
    return svg(470, 250,
               'The parabolic path of a ball projected from level ground at an angle '
               'theta. Its maximum height is labelled H and its horizontal range R, '
               'both measured from the launch point.', ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 05 -- a horizontal launch off a cliff, with the velocity triangle at impact
# ═════════════════════════════════════════════════════════════════════════════
def f05():
    ar = _ar('05', BLUE)
    b = []
    yg = 175.0
    lx, ly = 100.0, 45.0
    ix = 380.0
    b.append(RC(48, 30, 52, yg - 30, WALL))
    b.append(L(100, 30, 100, yg, INK, 2.2))
    b += _ticks([(48, 40 + 14 * i) for i in range(10)], -9, 9)
    b.append(L(100, yg, 455, yg, INK, 2.0))
    b += _ticks([(x, yg) for x in range(106, 450, 15)], -9, 9)
    # the fall
    pts = [(lx + (ix - lx) * t, ly + (yg - ly) * t * t)
           for t in [i / 40.0 for i in range(41)]]
    b.append(PL(pts, BLUE, 2.6))
    b.append(_dash(lx, ly, ix, ly))
    b.append(_dash(ix, ly, ix, yg))
    # the launch velocity
    b.append(L(lx, ly, lx + 58, ly, RED, 2.0,
               ' marker-end="url(#%s-05-ar)"' % P))
    b.append(T(lx + 26, ly - 9, 'u', 12.5, 'middle', RED))
    # the triangle of velocities, drawn clear of the ground
    hx, hy = ix + 72, yg
    vy = 96.0
    b.append(L(ix, yg, hx, hy, GREEN, 2.0, ' marker-end="url(#%s-05-ar)"' % P))
    b.append(T((ix + hx) / 2.0, yg - 9, 'u', 12.5, 'middle', GREEN))
    b.append(L(hx, hy, hx, hy + vy, RED, 2.0, ' marker-end="url(#%s-05-ar)"' % P))
    b.append(T(hx + 8, hy + vy / 2.0, 'v', 12.5, 'start', RED))
    b.append(_dash(ix, yg, hx, hy + vy, BLUE, 1.6))
    ang = math.degrees(math.atan2(vy, hx - ix))
    b.append(ARC(ix, yg, 46, 0, ang, GREY, 1.3))
    b.append(T(ix + 60 * math.cos(math.radians(ang / 2)),
               yg + 60 * math.sin(math.radians(ang / 2)) + 4, '&#952;', 13, 'start'))
    b += _dim(40, ly, 40, yg, 'h')
    return svg(470, 290,
               'A ball thrown horizontally with speed u from the top of a cliff of '
               'height h, curving down to the ground. Beside the point of impact its '
               'velocity is shown as a horizontal component u and a downward vertical '
               'component v, with the resultant at an angle theta below the horizontal.',
               ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 07 -- a disc with an off-centre hole: the geometry, not the answer
# ═════════════════════════════════════════════════════════════════════════════
def f07():
    b = []
    ox, oy, R = 190.0, 130.0, 96.0
    a = R / 2.0
    cx = ox + a
    b.append(CI(ox, oy, R, INK, 2.0, PANEL))
    b.append(PA('M %g %g A %g %g 0 0 1 %g %g A %g %g 0 0 1 %g %g'
                % (cx, oy - a, a, a, cx, oy + a, a, a, cx, oy - a),
                GREY, 1.6, 'none', ' stroke-dasharray="6 5"'))
    b += _ticks([(cx - a + 11 + 13 * i, oy + a - 13 - 5 * i) for i in range(8)],
                8, -6, GREY, 0.9)
    # the two centres, and the offset between them
    b.append(CI(ox, oy, 3.0, INK, 1.2, INK))
    b.append(CI(cx, oy, 3.0, BLUE, 1.2, BLUE))
    b.append(T(ox - 8, oy - 8, 'O', 12.5, 'end'))
    b.append(T(cx + 10, oy - 10, 'C', 12.5, 'start', BLUE))
    # a radius of the disc
    rr = math.radians(215)
    b.append(L(ox, oy, ox + R * math.cos(rr), oy + R * math.sin(rr), INK, 1.6))
    b.append(T(ox + 0.62 * R * math.cos(rr) - 6, oy + 0.62 * R * math.sin(rr) + 12,
               '2a', 12.0, 'middle'))
    # the offset a, dimensioned below the shape
    b.append(_dash(ox, oy, ox, 232))
    b.append(_dash(cx, oy + a, cx, 232))
    b += _dim(ox, 232, cx, 232, 'a')
    # the hole's radius, dimensioned to the right of it
    b.append(_dash(cx, oy, cx + a, oy))
    b += _dim(cx, 268, cx + a, 268, 'a')
    b.append(_dash(cx, oy, cx, 268))
    b.append(_dash(cx + a, oy, cx + a, 268))
    return svg(470, 300,
               'A circular disc of radius 2a with a circular hole of radius a cut out '
               'of it. The centre C of the hole is a distance a from the centre O of '
               'the disc. The hole is shown dashed, to mark it as material removed.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 09 -- a cylinder in a V-groove, both faces and both normals
# ═════════════════════════════════════════════════════════════════════════════
def f09():
    b = []
    apx, apy = 235.0, 200.0
    R = 45.0
    c60, s60 = math.cos(math.radians(60)), math.sin(math.radians(60))
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    # The left face rises at 60 degrees, so its inward normal is at 30 degrees to the
    # horizontal; the right face rises at 30 degrees, so its inward normal is at 60.
    # With (X, Y) the centre measured from the apex, Y counted upwards, the
    # perpendicular distance from the centre to each face is R:
    #     c30*X + s30*Y = R        (left face)
    #    -s30*X + c30*Y = R        (right face)
    # Solved rather than eyeballed, because a centre merely near the faces draws a
    # cylinder that visibly floats or sinks.  The first version of this figure had the
    # two normals swapped, which put the cylinder through the right-hand face -- a
    # defect that was invisible in the source and obvious in a screenshot.
    nlx, nly = c30, s30
    nrx, nry = -s30, c30
    det = nlx * nry - nrx * nly
    X = (R * nry - R * nly) / det
    Y = (R * nlx - R * nrx) / det
    px, py = apx + X, apy - Y
    # the two faces, hatched on the outside
    b.append(L(apx, apy, apx - 150 * c60, apy - 150 * s60, INK, 2.6))
    b.append(L(apx, apy, apx + 150 * c30, apy - 150 * s30, INK, 2.6))
    b += _ticks([(apx - t * c60, apy - t * s60) for t in range(20, 150, 16)],
                -13 * c30, 13 * s30)
    b += _ticks([(apx + t * c30, apy - t * s30) for t in range(20, 150, 16)],
                13 * s30, 13 * c30)
    b.append(CI(px, py, R, INK, 2.0, PANEL))
    # the angles at the apex, against a horizontal guide
    b.append(_dash(120, apy, 370, apy, WALL, 1.2))
    b.append(ARC(apx, apy, 62, 180, 240, GREY, 1.3))
    b.append(T(apx - 78, apy - 30, '60&#176;', 11.5, 'end', GREY))
    b.append(ARC(apx, apy, 62, -30, 0, GREY, 1.3))
    b.append(T(apx + 82, apy - 12, '30&#176;', 11.5, 'start', GREY))
    # the three forces: W through the centre, and one normal at each contact
    b.append(L(px, py, px, py + 82, RED, 2.0, ' marker-end="url(#%s-09-ar)"' % P))
    b.append(T(px + 9, py + 78, 'W', 12.5, 'start', RED))
    cl = (px - R * c30, py + R * s30)
    cr = (px + R * s30, py + R * c30)
    b.append(CI(cl[0], cl[1], 3.0, GREEN, 1.2, GREEN))
    b.append(CI(cr[0], cr[1], 3.0, GREEN, 1.2, GREEN))
    b.append(L(cl[0], cl[1], cl[0] + 62 * c30, cl[1] - 62 * s30, GREEN, 2.0,
               ' marker-end="url(#%s-09n-ar)"' % P))
    b.append(T(cl[0] + 70 * c30, cl[1] - 70 * s30 + 5, 'N', 12.5, 'start', GREEN))
    b.append(L(cr[0], cr[1], cr[0] - 62 * s30, cr[1] - 62 * c30, GREEN, 2.0,
               ' marker-end="url(#%s-09n-ar)"' % P))
    b.append(T(cr[0] - 70 * s30 - 4, cr[1] - 70 * c30 + 5, 'N', 12.5, 'end', GREEN))
    return svg(470, 260,
               'A cylinder of weight W resting in a V-shaped groove. The left face is '
               'inclined at 60 degrees to the horizontal and the right face at 30 '
               'degrees. The two normal reactions N act at the points of contact, each '
               'perpendicular to its own face, and W acts downwards through the centre.',
               _ar('09', RED) + _ar('09n', GREEN) + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 10 -- a wheel rolling, with the top of the rim marked
# ═════════════════════════════════════════════════════════════════════════════
def f10():
    ar = _ar('10', INK)
    b = []
    yg = 175.0
    ox, oy, R = 230.0, 115.0, 60.0
    b.append(L(60, yg, 420, yg, INK, 2.0))
    b += _ticks([(x, yg) for x in range(66, 416, 15)], -9, 9)
    b.append(CI(ox, oy, R, INK, 2.2, PANEL))
    b.append(CI(ox, oy, 3.2, INK, 1.2, INK))
    b.append(_dash(ox, oy - R - 18, ox, yg))
    b.append(CI(ox, oy - R, 4.2, RED, 1.2, RED))
    b.append(CI(ox, yg, 3.2, BLUE, 1.2, BLUE))
    b.append(T(ox + 10, oy - R - 6, 'P', 13, 'start', RED, 'bold'))
    b.append(T(ox + 12, yg + 32, 'contact', 10.5, 'start', BLUE))
    b.append(_dash(ox, oy, ox - R * math.cos(math.radians(30)),
                   oy + R * math.sin(math.radians(30))))
    b.append(T(ox - 30, oy + 22, 'r', 12.5, 'middle'))
    b.append(L(ox, oy, ox + 96, oy, INK, 2.0, ' marker-end="url(#%s-10-ar)"' % P))
    b.append(T(ox + 48, oy - 9, 'v', 13, 'middle'))
    b.append(ARC(ox, oy, R - 12, 250, 200, GREY, 1.4))
    return svg(470, 230,
               'A wheel of radius r rolling to the right along a level road at constant '
               'speed v. Its centre moves at v, the point of contact with the road is '
               'instantaneously at rest, and the point P at the top of the rim is '
               'marked.', ar + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 14 -- a person in front of a plane mirror, and the two extreme rays
# ═════════════════════════════════════════════════════════════════════════════
def f14():
    b = []
    mx = 300.0
    top, bot = 56.0, 240.0
    eyex, eyey = 99.0, 72.0
    b.append(L(mx, 40, mx, 272, INK, 3.2))
    b += _ticks([(mx, 46 + 14 * i) for i in range(17)], 13, -11)
    b.append(T(mx + 20, 34, 'mirror', 11.5, 'start', GREY))
    # the person
    b.append(CI(90, 68, 12, INK, 1.8, PANEL))
    b.append(L(90, 80, 90, 180, INK, 2.2))
    b.append(L(90, 100, 72, 138, INK, 1.8))
    b.append(L(90, 100, 108, 138, INK, 1.8))
    b.append(L(90, 180, 76, bot, INK, 1.8))
    b.append(L(90, 180, 104, bot, INK, 1.8))
    b.append(CI(eyex, eyey, 3.4, AMBER, 1.2, AMBER))
    b.append(L(eyex, eyey, 122, 58, GREY, 0.9))
    b.append(T(126, 58, 'eye', 11, 'start', AMBER))
    # the two rays: head-top to the eye, and feet to the eye
    for (sy, name) in ((top, 'head'), (bot, 'feet')):
        ry = (sy + eyey) / 2.0
        b.append(L(90, sy, mx, ry, BLUE, 1.8))
        b.append(L(mx, ry, eyex, eyey, BLUE, 1.8))
        b.append(CI(mx, ry, 3.2, BLUE, 1.2, BLUE))
    b += _dim(54, top, 54, bot, '1.70 m')
    return svg(470, 300,
               'A person of height 1.70 m standing in front of a vertical plane mirror. '
               'Two rays are drawn: one from the top of the head to the eye and one from '
               'the feet to the eye, each reflected at the mirror. The mirror is drawn '
               'much taller than the rays need, and its height is not labelled.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 17 -- two identical cells in parallel across one resistor
# ═════════════════════════════════════════════════════════════════════════════
def _cell(x, ytop, ybot, label, side):
    """A cell between ytop and ybot at x, with its label on the given side."""
    out = []
    mid = (ytop + ybot) / 2.0
    out.append(L(x, ytop, x, mid - 8, INK, 1.8))
    out.append(L(x - 14, mid - 8, x + 14, mid - 8, INK, 1.6))
    out.append(L(x - 7, mid + 4, x + 7, mid + 4, INK, 3.2))
    out.append(L(x, mid + 4, x, ybot, INK, 1.8))
    if side == 'left':
        out.append(T(x - 20, mid + 2, label, 11, 'end'))
    else:
        out.append(T(x + 20, mid + 2, label, 11, 'start'))
    return out


def f17():
    b = []
    yt, yb = 80.0, 210.0
    for x in (130.0, 230.0):
        b.append(L(x, yt, x, yt + 26, INK, 1.8))
        b += _cell(x, yt + 26, yt + 78, '1.5 V', 'left' if x == 130 else 'right')
        b.append(RC(x - 11, yt + 92, 22, 16, PANEL, INK, 1.5))
        b.append(L(x, yt + 78, x, yt + 92, INK, 1.8))
        b.append(L(x, yt + 108, x, yb, INK, 1.8))
        if x == 130:
            b.append(T(x - 18, yt + 105, '1.0 &#937;', 11, 'end'))
        else:
            b.append(T(x + 18, yt + 105, '1.0 &#937;', 11, 'start'))
    b.append(L(130, yt, 330, yt, INK, 2.0))
    b.append(L(130, yb, 330, yb, INK, 2.0))
    b.append(L(330, yt, 330, yt + 40, INK, 1.8))
    b.append(RC(319, yt + 40, 22, 16, PANEL, INK, 1.5))
    b.append(L(330, yt + 56, 330, yb, INK, 1.8))
    b.append(T(348, yt + 54, '2.0 &#937;', 11.5, 'start'))
    for (x, y) in ((130, yt), (230, yt), (130, yb), (230, yb), (330, yt), (330, yb)):
        b.append(CI(x, y, 3.0, INK, 1.0, INK))
    return svg(470, 250,
               'Two identical cells, each of electromotive force 1.5 volts and internal '
               'resistance 1.0 ohm, connected in parallel. The pair is joined across a '
               'resistor of 2.0 ohms.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 18 -- a potentiometer, with both balance points marked on one ruler
# ═════════════════════════════════════════════════════════════════════════════
def f18():
    b = []
    yw, yb = 80.0, 220.0
    x0, x1 = 80.0, 400.0
    b.append(L(x0, yw, x1, yw, INK, 2.6))
    b.append(L(x0, yb, x1, yb, INK, 2.0))
    # the driver cell
    b.append(L(x0, yw, x0, 142, INK, 1.8))
    b.append(L(x0 - 14, 142, x0 + 14, 142, INK, 1.6))
    b.append(L(x0 - 7, 154, x0 + 7, 154, INK, 3.2))
    b.append(L(x0, 154, x0, yb, INK, 1.8))
    b.append(T(x0 - 20, 152, 'driver', 10.5, 'end'))
    # the ruler under the wire
    b.append(L(x0, 96, x1, 96, GREY, 1.0))
    for i in range(11):
        x = x0 + 32 * i
        b.append(L(x, 96, x, 96 + (7 if i % 5 == 0 else 4), GREY, 1.0))
    b.append(T(x0, 116, '0', 10, 'middle', GREY))
    b.append(T(x0 + 160, 116, '0.50 m', 10, 'middle', GREY))
    b.append(T(x1, 116, '1.00 m', 10, 'middle', GREY))
    # the two balance points
    b.append(_dash(x0 + 144, yw, x0 + 144, 152))
    b.append(T(x0 + 144, 168, '45.0 cm', 10.5, 'end', BLUE))
    xb = x0 + 192
    b.append(L(xb, yw, xb, 130, INK, 1.8))
    b.append(CI(xb, yw, 3.4, INK, 1.0, INK))
    b.append(T(xb, 72, '60.0 cm', 10.5, 'middle', BLUE))
    b.append(_dash(xb, yw, xb, 72))
    b.append(CI(xb, 148, 17, INK, 1.6, PANEL))
    b.append(T(xb, 153, 'G', 12, 'middle'))
    b.append(L(xb, 130, xb, 131, INK, 1.8))
    b.append(L(xb, 165, xb, 182, INK, 1.8))
    b.append(L(xb - 14, 182, xb + 14, 182, INK, 1.6))
    b.append(L(xb - 7, 194, xb + 7, 194, INK, 3.2))
    b.append(L(xb, 194, xb, yb, INK, 1.8))
    b.append(T(xb + 22, 190, 'unknown cell', 10.5, 'start'))
    return svg(470, 250,
               'A potentiometer: a uniform resistance wire one metre long with a driver '
               'cell across it, and a galvanometer in series with an unknown cell '
               'connected to a sliding contact. The contact is shown at 60.0 centimetres, '
               'and the earlier balance point at 45.0 centimetres is marked on the same '
               'ruler.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 19 -- the charging loop: supply, resistor, capacitor
# ═════════════════════════════════════════════════════════════════════════════
def f19():
    b = []
    yt, yb = 60.0, 170.0
    b.append(L(100, yt, 340, yt, INK, 2.0))
    b.append(L(100, yb, 340, yb, INK, 2.0))
    b.append(L(100, yt, 100, 105, INK, 1.8))
    b.append(L(86, 105, 114, 105, INK, 1.6))
    b.append(L(93, 117, 107, 117, INK, 3.2))
    b.append(L(100, 117, 100, yb, INK, 1.8))
    b.append(T(78, 116, 'V', 12.5, 'end'))
    b.append(RC(190, yt - 10, 56, 20, PANEL, INK, 1.6))
    b.append(T(218, yt - 18, 'R', 12.5, 'middle'))
    b.append(L(340, yt, 340, 96, INK, 1.8))
    b.append(L(322, 96, 358, 96, INK, 2.6))
    b.append(L(322, 110, 358, 110, INK, 2.6))
    b.append(L(340, 110, 340, yb, INK, 1.8))
    b.append(T(366, 108, 'C', 12.5, 'start'))
    b.append(L(250, yt, 300, yt, BLUE, 2.0, ' marker-end="url(#s07-19-ar)"'))
    return svg(470, 220,
               'A capacitor of capacitance C charged from a battery of electromotive '
               'force V through a resistor of resistance R. The three are in a single '
               'series loop, so the same charge passes through each of them.',
               _ar('19', BLUE) + '\n' + '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 22 -- the recorded decay curve, with the flattened tail that gives it away
# ═════════════════════════════════════════════════════════════════════════════
def f22():
    b = []
    x0, y0 = 70.0, 250.0
    xs, ys = 4.5, 210.0 / 900.0        # px per second, px per count per minute
    b += _grid([x0 + 90 * i for i in range(1, 5)],
               [y0 - 200 * ys * i for i in range(1, 5)], x0, x0 + 360, 40, y0)
    b += _axes(x0, y0, x0 + 360, 40)
    for i in range(1, 5):
        b.append(T(x0 + 90 * i, y0 + 18, '%d' % (20 * i), 10.5, 'middle', GREY))
    for i in range(1, 5):
        b.append(T(x0 - 8, y0 - 200 * ys * i + 4, '%d' % (200 * i), 10.5, 'end', GREY))
    b.append(T(x0 + 180, y0 + 40, 'time / s', 11, 'middle', GREY))
    b.append(T(x0 - 4, 30, 'count rate / counts per minute', 11, 'start', GREY))
    # the recorded curve: 200 + 640 * 2^(-t/20)
    pts = []
    for i in range(81):
        t = float(i)
        r = 200.0 + 640.0 * 2 ** (-t / 20.0)
        pts.append((x0 + t * xs, y0 - r * ys))
    b.append(PL(pts, BLUE, 2.8))
    for t in (0, 20, 40, 60, 80):
        r = 200.0 + 640.0 * 2 ** (-t / 20.0)
        b.append(CI(x0 + t * xs, y0 - r * ys, 3.6, BLUE, 1.2, BLUE))
    return svg(470, 300,
               'A graph of the count rate recorded by a detector against time, over '
               'eighty seconds. The curve starts at 840 counts per minute, falls steeply '
               'at first and then flattens, ending at 240 counts per minute. It does not '
               'halve at equal intervals, because a steady background has been added to '
               'a decaying source.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 24 -- the stopping-potential line: only its crossing of the axis is wanted
# ═════════════════════════════════════════════════════════════════════════════
def f24():
    b = []
    x0, y0 = 70.0, 240.0
    xs = 360.0 / 10.0                 # px per 1e14 Hz
    ysv = 78.0                        # px per volt
    b += _grid([x0 + 2 * xs * i for i in range(1, 5)],
               [y0 - 0.5 * ysv * i for i in range(1, 5)], x0, x0 + 10 * xs, 45, y0)
    b += _axes(x0, y0, x0 + 360, 45)
    for i in range(1, 6):
        b.append(T(x0 + 2 * xs * i, y0 + 18, '%.1f' % (2.0 * i), 10.5, 'middle', GREY))
    for i in range(1, 5):
        b.append(T(x0 - 8, y0 - 0.5 * ysv * i + 4, '%.1f' % (0.5 * i), 10.5, 'end', GREY))
    b.append(T(x0 + 180, y0 + 40, 'frequency / 10<tspan font-size="8.5" dy="-4">14'
               '</tspan> Hz', 11, 'middle', GREY))
    b.append(T(x0 - 4, 34, 'stopping potential / V', 11, 'start', GREY))
    # the line: V = (h/e)(f - f0), f0 = 5.0e14 Hz
    f0, grad = 5.0, 2.0625 / 5.0      # in units of 1e14 Hz and volts
    b.append(L(x0 + f0 * xs, y0, x0 + 10 * xs, y0 - grad * (10 - f0) * ysv, BLUE, 2.8))
    b.append(CI(x0 + f0 * xs, y0, 3.6, RED, 1.2, RED))
    return svg(470, 300,
               'A graph of stopping potential against frequency for a metal surface. The '
               'line is straight and crosses the frequency axis between the 4.0 and 6.0 '
               'marks, at 5.0 times ten to the fourteenth hertz, rising to just over two '
               'volts at ten times ten to the fourteenth hertz.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# 25 -- the lamp, the sphere at 3.0 m, and the detector on it
# ═════════════════════════════════════════════════════════════════════════════
def f25():
    ar = _ar('25', AMBER)
    b = []
    cx, cy, R = 230.0, 155.0, 110.0
    b.append(CI(cx, cy, R, GREY, 1.6, 'none'))
    b.append(PA('M %g %g A %g %g 0 0 1 %g %g A %g %g 0 0 1 %g %g'
                % (cx, cy - R, R, R, cx, cy + R, R, R, cx, cy - R),
                GREY, 1.6, 'none', ' stroke-dasharray="7 6"'))
    b.append(T(cx, 30, 'sphere of radius 3.0 m', 11.5, 'middle', GREY))
    b.append(CI(cx, cy, 8, AMBER, 1.6, AMBER))
    b.append(T(cx - 16, cy - 16, 'lamp, 100 W', 11.5, 'end', AMBER))
    for a in (20, 55, 90, 125, 160, 200, 235, 270, 305, 340):
        r = math.radians(a)
        b.append(L(cx + 16 * math.cos(r), cy + 16 * math.sin(r),
                   cx + 34 * math.cos(r), cy + 34 * math.sin(r), AMBER, 1.4,
                   ' marker-end="url(#%s-25-ar)"' % P))
    # the detector, on the sphere
    dx, dy = cx + R, cy
    b.append(L(dx, dy - 16, dx, dy + 16, BLUE, 4.0))
    b.append(L(dx - 6, dy - 16, dx + 6, dy - 16, INK, 1.2))
    b.append(L(dx - 6, dy + 16, dx + 6, dy + 16, INK, 1.2))
    b.append(_dash(cx, cy, dx, dy, INK, 1.2))
    b.append(T((cx + dx) / 2.0, cy - 8, '3.0 m', 11.5, 'middle'))
    b.append(T(dx + 14, dy - 10,
               'detector, 2.0 cm<tspan font-size="8" dy="-4">2</tspan>', 11, 'start', BLUE))
    return svg(470, 300,
               'A lamp radiating equally in all directions, surrounded by a dashed '
               'sphere of radius 3.0 metres. A small detector lies on the sphere, its '
               'face towards the lamp, and only a tiny fraction of the sphere is covered '
               'by it.', ar + '\n' + '\n'.join(b))


FIGS = {
    's07-02': f02,
    's07-04': f04,
    's07-05': f05,
    's07-07': f07,
    's07-09': f09,
    's07-10': f10,
    's07-14': f14,
    's07-17': f17,
    's07-18': f18,
    's07-19': f19,
    's07-22': f22,
    's07-24': f24,
    's07-25': f25,
}
