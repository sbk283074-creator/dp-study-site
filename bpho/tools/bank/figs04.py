# -*- coding: utf-8 -*-
"""Figures for BANK SECTION 04 (S04-01 .. S04-25).

Keys are 's04-<QQ>'.  Every marker id is prefixed with the figure key so it cannot
collide with any other figure in the bank -- HTML has no id namespace, so two figures
defining `id="a"` silently give one of them the wrong arrowhead.

Run `python figs.py 4` from tools/bank to (re)build fig/.  Editing this file without
running that writes nothing the gate or the build will ever see.

Design rule, carried over from sections 1-3: a figure must encode the discriminator the
question turns on, not decorate the apparatus.  So the impulse figure shows that the ball
rebounds DOWNWARD (the component along the wall is unchanged, so the change in momentum
is perpendicular to the wall), the loop figure states that at the top both forces act
downward, and the fibre figure marks the angle at the side wall as 90 - r, because that
is the step the question turns on.
"""
import math

from svgkit import *


def ell(cx, cy, rx, ry, a0=0, a1=360, c=GREY, sw=1.2, n=48, extra=''):
    """A full or partial ellipse as a sampled polyline.

    Sampled rather than written as an SVG arc: the `A` command's large-arc and sweep
    flags are easy to get wrong and fail silently by enlarging the radius.
    """
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / float(n))
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return PL(pts, c, sw, 'none', extra)


def _dash(x1, y1, x2, y2, c=GREY, sw=1.2):
    return L(x1, y1, x2, y2, c, sw, ' stroke-dasharray="5 4"')


def _hatch_right(x, y0, y1, step=13, dx=11, dy=9, c=INK, sw=1.2):
    """Ticks going right-and-down, for a vertical wall at x."""
    out = []
    y = y0
    while y < y1:
        out.append(L(x, y, x + dx, y + dy, c, sw))
        y += step
    return out


def _hatch_down(y, x0, x1, step=13, dx=-9, dy=9, c=INK, sw=1.2):
    """Ticks going down-and-left, for a horizontal surface at y."""
    out = []
    x = x0
    while x < x1:
        out.append(L(x, y, x + dx, y + dy, c, sw))
        x += step
    return out


def _hatch_up(y, x0, x1, step=13, dx=9, dy=-9, c=INK, sw=1.2):
    """Ticks going up-and-right, for a ceiling at y."""
    out = []
    x = x0
    while x < x1:
        out.append(L(x, y, x + dx, y + dy, c, sw))
        x += step
    return out


def _dim(x1, y1, x2, y2, label, off=0.0, c=GREY, size=11.0):
    """A dimension line with end ticks and a centred label."""
    out = [L(x1, y1, x2, y2, c, 1.2)]
    if abs(x2 - x1) > abs(y2 - y1):                 # horizontal
        for x in (x1, x2):
            out.append(L(x, y1 - 5, x, y1 + 5, c, 1.2))
        out.append(T((x1 + x2) / 2.0, y1 + 15 + off, label, size, 'middle', c))
    else:                                           # vertical
        for y in (y1, y2):
            out.append(L(x1 - 5, y, x1 + 5, y, c, 1.2))
        out.append(T(x1 - 9, (y1 + y2) / 2.0 + 4 + off, label, size, 'end', c))
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# 01 -- a cell with internal resistance, voltmeter across the terminals
# ═══════════════════════════════════════════════════════════════════════════════
def f_01():
    """The discriminator is WHERE the voltmeter is connected.

    It is across the external resistor, so it reads the terminal p.d. -- the emf minus
    the volts lost across r.  A figure that drew the cell as a single box would hide the
    very resistance the question is about, so r is drawn as a separate component and the
    dashed box marks what is physically inside the cell.
    """
    W, H = 560, 262
    b = [mk('s04-01-ar', BLUE)]
    yt, yb2, xl, xr = 100.0, 220.0, 110.0, 470.0

    # the loop
    b.append(L(xl, yt, xr, yt, INK, 1.8))
    b.append(L(xr, yt, xr, yb2, INK, 1.8))
    b.append(L(xl, yb2, xr, yb2, INK, 1.8))

    # the left branch: internal resistor r, then the cell itself
    b.append(L(xl, yb2, xl, 200.0, INK, 1.8))
    b.append(L(102, 200, 118, 200, INK, 2.6))            # short plate (negative)
    b.append(L(92, 186, 128, 186, INK, 2.6))             # long plate (positive)
    b.append(L(xl, 186, xl, 150, INK, 1.8))
    b.append(RC(xl - 16, 126, 32, 24, WALL, INK, 1.8))
    b.append(L(xl, 126, xl, yt, INK, 1.8))
    b.append(T(84, 196, '6.0 V', 11.5, 'end', INK))

    # what is inside the cell: labelled in words, NOT boxed.  A dashed box around this
    # branch ran straight through the "6.0 V" label -- the box was pure decoration and
    # the words carry the fact the question turns on.
    b.append(T(xl + 26, 141, 'r', 12, 'start', AMBER, 'bold'))
    b.append(T(xl + 26, 155, '(inside the cell)', 10, 'start', GREY))

    # the external resistor
    b.append(RC(250, yt - 12, 80, 24, WALL, INK, 1.8))
    b.append(T(290, 78, 'R = 12 &#937;', 12, 'middle', INK))

    # the voltmeter, across the terminals -- the whole point of the figure
    b.append(L(250, yt, 250, 40, INK, 1.4))
    b.append(L(250, 40, 272, 40, INK, 1.4))
    b.append(CI(290, 40, 18, INK, 1.8, '#ffffff'))
    b.append(T(290, 45, 'V', 12.5, 'middle', INK, 'bold'))
    b.append(L(308, 40, 330, 40, INK, 1.4))
    b.append(L(330, 40, 330, yt, INK, 1.4))
    for x in (250, 330):
        b.append(CI(x, yt, 3.2, INK, 1.4, INK))

    b.append(T(290, 14, 'voltmeter', 10.5, 'middle', GREY))
    b.append(T(350, 45, 'reads 4.8 V', 11.5, 'start', BLUE))

    return svg(W, H, 'A cell of emf 6.0 V with internal resistance r in series with a '
                     '12 ohm resistor R; a voltmeter connected across R alone, reading the '
                     'terminal potential difference of 4.8 V', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 03 -- a ladder against a smooth wall
# ═══════════════════════════════════════════════════════════════════════════════
def f_03():
    """The discriminator is that a SMOOTH wall can only push horizontally, and that the
    weight of a uniform ladder acts at its midpoint -- so the moment arm of the weight
    about the foot is the HORIZONTAL distance to the midpoint.  That horizontal distance
    is drawn as a dashed right angle, because it is the step the algebra turns on.
    """
    W, H = 560, 306
    b = [mk('s04-03-ar', RED)]
    xf, yf = 150.0, 250.0
    ang = math.radians(30.0)
    Lp = 290.0 / math.cos(ang)                 # so the top lands at x = 440
    xt, yt = xf + Lp * math.cos(ang), yf - Lp * math.sin(ang)
    xm, ym = (xf + xt) / 2.0, (yf + yt) / 2.0

    # ground and wall
    b.append(L(60, yf, 500, yf, INK, 2.0))
    b += _hatch_down(yf, 66, 494)
    b.append(L(440, 40, 440, yf, INK, 2.0))
    b += _hatch_right(440, 46, 244)
    b.append(T(452, 58, 'smooth wall', 10.5, 'start', GREY))

    # the ladder
    b.append(L(xf, yf, xt, yt, '#8a93a3', 5.0))
    b.append(L(xf, yf, xt, yt, INK, 1.6))

    # the angle to the ground
    b.append(ARC(xf, yf, 92, 0, -30, GREY, 1.3))
    b.append(T(250, 224, '30&#176;', 12, 'middle', GREY, 'bold'))

    # the weight, at the midpoint
    b.append(L(xm, ym, xm, ym + 52, RED, 2.2, ' marker-end="url(#s04-03-ar)"'))
    b.append(T(xm + 10, ym + 34, 'W', 12, 'start', RED, 'bold'))
    b.append(CI(xm, ym, 3.4, RED, 1.4, RED))

    # the moment arm of W about the foot: a VERTICAL force's arm is the horizontal
    # distance.  Drawn BELOW the ground line -- laid on the ground it was completely
    # invisible, hidden under the very surface it was supposed to be measured along.
    b.append(_dash(xm, ym, xm, 276))
    b.append(_dash(xf, yf, xf, 276))
    b.append(_dash(xf, 276, xm, 276))
    for x in (xf, xm):
        b.append(L(x, 271, x, 281, GREY, 1.2))
    b.append(T((xf + xm) / 2.0, 292, 'd', 12, 'middle', GREY, 'bold'))

    # the three reaction forces
    b.append(L(xf, yf, xf, yf - 46, AMBER, 2.2, ' marker-end="url(#s04-03-ar)"'))
    b.append(T(xf - 8, yf - 30, 'N', 12, 'end', AMBER, 'bold'))
    b.append(L(xf, yf, xf + 46, yf, GREEN, 2.2, ' marker-end="url(#s04-03-ar)"'))
    b.append(T(xf + 50, yf - 8, 'F', 12, 'start', GREEN, 'bold'))
    b.append(L(xt, yt, xt - 46, yt, BLUE, 2.2, ' marker-end="url(#s04-03-ar)"'))
    b.append(T(xt - 50, yt - 8, 'R', 12, 'end', BLUE, 'bold'))

    return svg(W, H, 'A uniform ladder of weight W leaning against a smooth vertical wall '
                     'at 30 degrees to the ground; the wall pushes horizontally with R, the '
                     'ground pushes up with N and horizontally with friction F, and the '
                     'horizontal distance d from the foot to the midpoint is marked', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 06 -- two projectiles at complementary angles
# ═══════════════════════════════════════════════════════════════════════════════
def f_06():
    """The discriminator is that both arcs end at the SAME point on the ground.

    That is the fact the question rests on: complementary angles give equal range but
    different flight times, so the 60-degree arc is three times as tall while the
    30-degree one stays in the air for less time.
    """
    W, H = 560, 292
    b = [mk('s04-06-ar', INK)]
    yg, x0, R = 228.0, 90.0, 380.0

    b.append(L(50, yg, 520, yg, INK, 2.0))
    b += _hatch_down(yg, 56, 514)

    def arc(deg, colour):
        pts = []
        n = 60
        tan = math.tan(math.radians(deg))
        for i in range(n + 1):
            s = i / float(n)
            pts.append((x0 + R * s, yg - R * tan * s * (1 - s)))
        return PL(pts, colour, 2.4)

    b.append(arc(60, BLUE))
    b.append(arc(30, AMBER))

    # the common apex abscissa, so the height difference is unmistakable
    b.append(_dash(x0 + R / 2, yg, x0 + R / 2, 52))
    # the shared range
    b.append(_dash(x0 + R, yg, x0 + R, 52))
    b += _dim(x0, yg + 26, x0 + R, yg + 26, 'same range')

    # The angle labels sit to the RIGHT of each apex, not on the curve.  Placed at the
    # apex they were drawn straight through the arc they label -- obvious on screen,
    # invisible in the source.
    b.append(T(x0 + R / 2 + 12, 52, '60&#176;', 12, 'start', BLUE, 'bold'))
    b.append(T(x0 + R / 2 + 12, 196, '30&#176;', 12, 'start', AMBER, 'bold'))
    b.append(CI(x0, yg, 4.0, INK, 1.4, INK))
    b.append(T(x0 - 6, yg + 20, 'launch point', 10.5, 'end', GREY))
    b.append(T(300, 30, 'both launched with the same speed', 10.5, 'middle', GREY))

    return svg(W, H, 'Two projectiles launched from the same point with the same speed, one '
                     'at 60 degrees and one at 30 degrees to the horizontal; the 60 degree '
                     'arc is three times as high and both land at the same distance', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 07 -- a ball bouncing off a wall: the change in momentum
# ═══════════════════════════════════════════════════════════════════════════════
def f_07():
    """The discriminator is that the ball leaves moving DOWNWARD, not back up.

    A smooth wall reverses only the component perpendicular to it, so the component
    parallel to the wall is untouched and the change in momentum is perpendicular to the
    wall with magnitude 2mv cos(theta).  The vector triangle at the foot of the figure is
    the evidence, and it is the part a decoration-only figure would leave out.
    """
    W, H = 560, 296
    b = [mk('s04-07-ar', RED), mk('s04-07-ab', BLUE)]
    xw = 430.0
    th = math.radians(25.0)
    yc = 154.0
    dx = 180.0
    dy = dx * math.tan(th)

    b.append(L(xw, 26, xw, 268, INK, 2.0))
    b += _hatch_right(xw, 32, 262)
    b.append(T(xw + 14, 46, 'wall', 10.5, 'start', GREY))

    # in and out: same angle, both travelling DOWNWARD to the right and left
    b.append(CI(250, yc - dy, 7, BLUE, 1.6, '#e8eefc'))
    b.append(L(250, yc - dy, 426, yc - dy + 176 * math.tan(th), BLUE, 2.0,
               ' marker-end="url(#s04-07-ab)"'))
    b.append(CI(xw, yc, 7, BLUE, 1.6, '#e8eefc'))
    b.append(L(xw, yc, 264, yc + 166 * math.tan(th), BLUE, 2.0,
               ' marker-end="url(#s04-07-ab)"'))
    b.append(T(300, 80, 'v', 12.5, 'middle', BLUE, 'bold'))
    b.append(T(300, 204, 'v', 12.5, 'middle', BLUE, 'bold'))

    # the normal, and the two angles
    b.append(_dash(xw, yc, 322, yc))
    b.append(T(318, yc - 8, 'normal', 10.5, 'end', GREY))
    b.append(ARC(xw, yc, 56, 180, 180 + math.degrees(th), GREY, 1.3))
    b.append(ARC(xw, yc, 56, 180 - math.degrees(th), 180, GREY, 1.3))
    b.append(T(360, 138, '&#952;', 12, 'middle', GREY, 'bold'))
    b.append(T(360, 172, '&#952;', 12, 'middle', GREY, 'bold'))

    # the vector triangle: the whole answer
    ox, oy, k = 150.0, 236.0, 0.40
    b.append(L(ox, oy, ox + dx * k, oy + dy * k, BLUE, 2.0, ' marker-end="url(#s04-07-ab)"'))
    b.append(L(ox, oy, ox - dx * k, oy + dy * k, BLUE, 2.0, ' marker-end="url(#s04-07-ab)"'))
    b.append(L(ox + dx * k, oy + dy * k, ox - dx * k, oy + dy * k, RED, 2.4,
               ' marker-end="url(#s04-07-ar)"'))
    b.append(T(ox + 16, oy + 6, 'v', 11.5, 'start', BLUE, 'bold'))
    b.append(T(ox - 16, oy + 6, 'v', 11.5, 'end', BLUE, 'bold'))
    b.append(T(ox, oy + dy * k + 18, '&#916;v', 12, 'middle', RED, 'bold'))
    b.append(T(ox, oy - 12, 'velocity triangle', 10.5, 'middle', GREY))

    return svg(W, H, 'A ball striking a vertical wall at 25 degrees below the horizontal and '
                     'rebounding at the same angle below the horizontal; a velocity triangle '
                     'below shows the change in velocity is horizontal, perpendicular to the '
                     'wall', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 08 -- the top of a vertical circular loop
# ═══════════════════════════════════════════════════════════════════════════════
def f_08():
    """The discriminator is that at the TOP of the loop both the weight and the normal
    reaction act DOWNWARD, so they add.  A figure that drew the normal reaction pointing
    outward, as it does at the bottom, would make the question unanswerable -- so the
    figure states the direction in words as well as drawing it.
    """
    W, H = 560, 312
    b = [mk('s04-08-ar', RED), mk('s04-08-ab', BLUE), mk('s04-08-ag', GREEN)]
    cx, cy, r = 280.0, 172.0, 100.0

    b.append(CI(cx, cy, r, INK, 3.0, '#f2f5fa'))
    b.append(CI(cx, cy, r - 12, '#c9d2e0', 1.2))
    b.append(CI(cx, cy, 3.0, GREY, 1.2, GREY))
    b.append(_dash(cx, cy, cx, cy - r))
    b.append(T(cx + 8, 150, 'r', 12, 'start', GREY, 'bold'))

    # the car at the top
    b.append(RC(cx - 20, cy - r + 2, 40, 15, WALL, INK, 1.6))
    # both forces act downward
    b.append(L(cx - 11, cy - r + 20, cx - 11, cy - r + 64, RED, 2.2,
               ' marker-end="url(#s04-08-ar)"'))
    b.append(T(cx - 20, cy - r + 52, 'mg', 12, 'end', RED, 'bold'))
    b.append(L(cx + 11, cy - r + 20, cx + 11, cy - r + 48, BLUE, 2.2,
               ' marker-end="url(#s04-08-ab)"'))
    b.append(T(cx + 21, cy - r + 40, 'N', 12, 'start', BLUE, 'bold'))
    # the speed, tangential and clear of both the car and the heading
    b.append(L(cx + 22, cy - r - 16, cx + 90, cy - r - 16, GREEN, 2.2,
               ' marker-end="url(#s04-08-ag)"'))
    b.append(T(cx + 96, cy - r - 12, 'v', 12.5, 'start', GREEN, 'bold'))

    b.append(T(cx, 34, 'at the top, mg and N both act downward', 11.5, 'middle', INK))
    b.append(T(cx, 296, 'so mg + N = mv&#178;/r, and the smallest possible N is zero',
               11.5, 'middle', GREY))

    return svg(W, H, 'A car at the top of a vertical circular loop of radius r, drawn with '
                     'its weight and the normal reaction from the track both pointing '
                     'downward and its velocity tangential', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 10 -- the acceptance angle of an optical fibre
# ═══════════════════════════════════════════════════════════════════════════════
def f_10():
    """The discriminator is the angle at the SIDE wall.

    The ray is refracted to r at the end face and then meets the side wall, where the
    normal is horizontal -- so the angle of incidence there is 90 - r, not r.  That single
    piece of geometry is the whole question, so the figure marks it explicitly.
    """
    W, H = 560, 186
    b = [mk('s04-10-ar', BLUE)]
    x0, x1 = 120.0, 440.0
    ya, yb2 = 60.0, 140.0
    yc = (ya + yb2) / 2.0
    r = math.radians(25.0)

    # the core
    b.append(RC(x0, ya, x1 - x0, yb2 - ya, '#eef2f8'))
    b.append(L(x0, ya, x1, ya, INK, 1.8))
    b.append(L(x0, yb2, x1, yb2, INK, 1.8))
    b.append(L(x0, ya, x0, yb2, INK, 2.4))
    # the core label moves right, to leave room below the bounce point
    b.append(T(300, yb2 + 20, 'core, refractive index n', 10.5, 'start', GREY))

    # the axis, and the ray in air
    b.append(_dash(56, yc, x1 + 20, yc))
    b.append(L(40, 40, x0, yc, BLUE, 2.2, ' marker-end="url(#s04-10-ar)"'))
    b.append(ARC(x0, yc, 74, 180, 180 + math.degrees(math.atan2(yc - 40, x0 - 40)), GREY, 1.3))
    b.append(T(44, 72, 'i', 12.5, 'end', GREY, 'bold'))

    # the refracted ray, then the angle at the side wall
    hitx = x0 + (yb2 - yc) / math.tan(r)
    b.append(L(x0, yc, hitx, yb2, BLUE, 2.2))
    b.append(ARC(x0, yc, 52, 0, math.degrees(r), GREY, 1.3))
    b.append(T(174, 112, 'r', 12.5, 'start', GREY, 'bold'))
    # radius 30, not 44.  At 44 the arc swept left as far as x = 166 and passed straight
    # through the 'r' label's box, which the collision scan caught and the eye would not
    # have -- the arc and the label are both grey and both small.
    b.append(ARC(hitx, yb2, 30, 205, 270, GREY, 1.3))
    # The label belongs UNDER the bounce point, not floating above the axis.  The 65-degree
    # wedge between the incoming ray and the wall's normal is only about 23 px wide at the
    # arc's radius, and this label is 42 px wide, so it cannot sit inside the angle at all.
    # Below the wall, directly under the marked bounce point, it is unambiguous.
    b.append(T(196, yb2 + 22, '90&#176; &#8722; r', 11, 'middle', AMBER, 'bold'))
    b.append(CI(hitx, yb2, 3.4, INK, 1.4, INK))

    # the reflection, and a second bounce so the guiding is visible
    upx = hitx + (yb2 - ya) / math.tan(r)
    b.append(L(hitx, yb2, upx, ya, BLUE, 2.2))
    # the second bounce stays INSIDE the core -- with the fibre ending at x = 400 the
    # segment finished exactly on the end face, which read as the ray escaping sideways
    b.append(L(upx, ya, min(upx + 62, x1), ya + min(62, x1 - upx) * math.tan(r), BLUE, 2.2))

    return svg(W, H, 'A ray of light entering the flat end face of an optical fibre at angle '
                     'i to the axis, refracted to angle r inside the core, then meeting the '
                     'side wall where the angle to the normal is 90 minus r', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 11 -- a thermistor in a potential divider
# ═══════════════════════════════════════════════════════════════════════════════
def f_11():
    """The discriminator is WHICH component the output is taken across.

    The thermistor is the top arm and the output is across the fixed resistor, so heating
    the thermistor lowers its resistance, raises the current, and therefore RAISES the
    output.  A figure that swapped the two arms would invert the answer.
    """
    W, H = 560, 232
    b = [mk('s04-11-ar', INK)]
    xl, xr, yt, yb2 = 110.0, 450.0, 60.0, 170.0

    b.append(L(xl, yt, xr, yt, INK, 1.8))
    b.append(L(xl, yb2, xr, yb2, INK, 1.8))
    b.append(L(xr, yt, xr, yb2, INK, 1.8))
    b.append(L(xl, yb2, xl, 122, INK, 1.8))
    b.append(L(96, 122, 124, 122, INK, 2.6))
    b.append(L(102, 110, 118, 110, INK, 2.6))
    b.append(L(xl, 110, xl, yt, INK, 1.8))
    b.append(T(88, 120, '6.0 V', 11.5, 'end', INK))

    # the thermistor, in the TOP arm
    b.append(RC(250, yt - 12, 80, 24, WALL, INK, 1.8))
    b.append(L(238, 84, 342, 36, INK, 1.8))
    b.append(L(228, 84, 238, 84, INK, 2.2))
    b.append(T(290, 28, 'thermistor', 11.5, 'middle', INK))

    # the fixed resistor, in the BOTTOM arm, with the output across it
    b.append(RC(250, yb2 - 12, 80, 24, WALL, INK, 1.8))
    b.append(T(244, 158, 'R', 12.5, 'end', INK, 'bold'))
    b.append(L(250, yb2, 250, 204, INK, 1.4))
    b.append(L(330, yb2, 330, 204, INK, 1.4))
    b.append(CI(250, 204, 3.2, INK, 1.4, INK))
    b.append(CI(330, 204, 3.2, INK, 1.4, INK))
    b.append(T(290, 222, 'V out', 11.5, 'middle', BLUE, 'bold'))

    return svg(W, H, 'A potential divider with a thermistor in the upper arm and a fixed '
                     'resistor R in the lower arm, the output being taken across R', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 13 -- stopping potential against frequency
# ═══════════════════════════════════════════════════════════════════════════════
def f_13():
    """The discriminator is the GRADIENT, not the intercept.

    The line is straight with gradient h/e and intercept -W0/e on the potential axis, so a
    gradient read off the graph gives Planck's constant directly.  The triangle is drawn
    on the line because that is what the question asks the reader to do.
    """
    W, H = 560, 268
    b = [mk('s04-13-ar', INK)]
    xax, y0 = 170.0, 150.0
    b.append(L(110, y0, 520, y0, INK, 1.8, ' marker-end="url(#s04-13-ar)"'))
    b.append(L(xax, 210, xax, 40, INK, 1.8, ' marker-end="url(#s04-13-ar)"'))
    b.append(T(524, y0 + 18, 'frequency', 11.5, 'end', GREY))
    b.append(T(xax - 6, 34, 'stopping potential', 11.5, 'end', GREY))

    # the line: V = 0 at f0, rising to the right
    x_end, y_end = 500.0, 54.0
    slope = (y_end - y0) / (x_end - xax)

    def on_line(x):
        return y0 + slope * (x - xax)

    b.append(L(xax, y0, x_end, y_end, BLUE, 2.6))
    b.append(_dash(xax, y0, xax, 210))
    b.append(CI(xax, y0, 4.0, BLUE, 1.4, BLUE))
    # 'f' sits just clear of the vertical axis.  Anchored 'middle' on the axis it was
    # struck through by the axis line itself.
    b.append(T(xax - 4, y0 + 22, 'f', 12.5, 'end', INK, 'bold'))
    b.append(T(xax + 12, y0 + 24, 'threshold', 10.5, 'start', GREY))

    # Both corners of the triangle must sit ON the line.  Placed at guessed y-values it
    # floated 13 px clear at one end and 2 px at the other -- and a gradient triangle that
    # does not lie on its own line teaches the reader to measure the wrong thing.
    ax, bx = 250.0, 430.0
    ay, by = on_line(ax), on_line(bx)
    b.append(L(ax, ay, bx, ay, GREEN, 1.8))
    b.append(L(bx, ay, bx, by, GREEN, 1.8))
    b.append(T((ax + bx) / 2.0, ay + 16, '&#916;f', 12, 'middle', GREEN, 'bold'))
    b.append(T(bx + 10, (ay + by) / 2.0 + 4, '&#916;V', 12, 'start', GREEN, 'bold'))
    # clear of both the "threshold" label and the triangle, which used to overlap it
    b.append(T(300, 198, 'gradient = h / e', 12, 'middle', INK, 'bold'))

    return svg(W, H, 'A graph of stopping potential against frequency: a straight line '
                     'crossing the frequency axis at the threshold frequency, with a '
                     'triangle on the line marking the gradient', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 15 -- crossing a river
# ═══════════════════════════════════════════════════════════════════════════════
def f_15():
    """The discriminator is that the crossing TIME depends only on the component of the
    boat's velocity perpendicular to the banks -- so the current changes where the boat
    lands, not how long it takes.  The figure separates the three vectors so that the
    right-angled structure is visible.
    """
    W, H = 560, 264
    b = [mk('s04-15-ar', RED), mk('s04-15-ab', BLUE)]
    xa, y0, y1 = 150.0, 70.0, 210.0
    drift = 140.0

    b.append(L(60, y0, 500, y0, INK, 2.0))
    b.append(L(60, y1, 500, y1, INK, 2.0))
    b += _hatch_up(y0, 66, 494)
    b += _hatch_down(y1, 66, 494)
    b.append(T(70, y0 - 12, 'far bank', 10.5, 'start', GREY))
    b.append(T(70, y1 + 22, 'near bank', 10.5, 'start', GREY))

    b.append(L(xa, y1, xa, y0, BLUE, 2.4, ' marker-end="url(#s04-15-ab)"'))
    b.append(T(xa + 10, (y0 + y1) / 2.0, 'boat', 11.5, 'start', BLUE, 'bold'))
    b.append(L(xa, y1, xa + drift, y1, GREEN, 2.4, ' marker-end="url(#s04-15-ar)"'))
    b.append(T(xa + drift / 2.0, y1 - 8, 'current', 11.5, 'middle', GREEN, 'bold'))
    b.append(L(xa, y1, xa + drift, y0, RED, 2.4, ' marker-end="url(#s04-15-ar)"'))
    b.append(T(xa + drift + 12, y0 + 10, 'resultant', 11.5, 'start', RED, 'bold'))

    b.append(CI(xa, y1, 3.6, INK, 1.4, INK))
    b += _dim(xa, y0 - 30, xa + drift, y0 - 30, 'the current carries it downstream')
    b += _dim(106, y0, 106, y1, 'width')

    return svg(W, H, 'A boat leaving the near bank pointing straight across a river; its '
                     'velocity relative to the water is drawn across the river, the '
                     'current is drawn along the bank, and the resultant shows it landing '
                     'downstream', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 16 -- a sign hanging from two wires at unequal angles
# ═══════════════════════════════════════════════════════════════════════════════
def f_16():
    """The discriminator is that the STEEPER wire carries LESS.

    Both wires' horizontal components must cancel, so T sin(angle from vertical) is the
    same for both -- which means the wire closer to the vertical takes more of the load.
    The two dashed verticals exist so the angles can be read from the vertical, which is
    where the mistake happens.
    """
    W, H = 560, 268
    b = [mk('s04-16-ar', RED), mk('s04-16-aw', INK)]
    yc = 80.0
    xs0, xs1, ys = 215.0, 345.0, 170.0
    dy = ys - yc
    ax1 = xs0 - dy * math.tan(math.radians(60))
    ax2 = xs1 + dy * math.tan(math.radians(30))

    b.append(L(30, yc, 500, yc, INK, 2.0))
    b += _hatch_up(yc, 36, 494)

    # the two wires
    b.append(L(ax1, yc, xs0, ys, INK, 2.0))
    b.append(L(ax2, yc, xs1, ys, INK, 2.0))
    # Tension labels sit OUTSIDE each wire.  Placed on the wire they were struck through
    # by it, and the "2" of T2 landed on top of the 30-degree label.
    b.append(T(84, 105, 'T<tspan font-size="8.5" dy="3">1</tspan>', 12, 'start', INK, 'bold'))
    b.append(T(388, 105, 'T<tspan font-size="8.5" dy="3">2</tspan>', 12, 'start', INK, 'bold'))

    # the verticals the angles are measured from
    b.append(_dash(xs0, ys, xs0, ys - 62))
    b.append(_dash(xs1, ys, xs1, ys - 62))
    b.append(ARC(xs0, ys, 50, 210, 270, GREY, 1.3))
    b.append(T(178, 122, '60&#176;', 11.5, 'middle', GREY, 'bold'))
    b.append(ARC(xs1, ys, 50, 270, 300, GREY, 1.3))
    # inside the 30-degree wedge, above the arc.  Lower down the wire crosses the text --
    # the wedge narrows towards the vertex, so the only clear space is near the top.
    b.append(T(359, 120, '30&#176;', 11.5, 'middle', GREY, 'bold'))

    # the sign
    b.append(RC(xs0, ys, xs1 - xs0, 44, '#dde3ec', INK, 1.8))
    b.append(T((xs0 + xs1) / 2.0, ys + 27, 'sign', 11.5, 'middle', INK))
    b.append(L((xs0 + xs1) / 2.0, ys + 44, (xs0 + xs1) / 2.0, ys + 78, RED, 2.2,
               ' marker-end="url(#s04-16-ar)"'))
    b.append(T((xs0 + xs1) / 2.0 + 10, ys + 68, 'W', 12, 'start', RED, 'bold'))

    return svg(W, H, 'A sign hanging from two wires attached to a ceiling, the left wire at '
                     '60 degrees to the vertical and the right at 30 degrees to the '
                     'vertical, with the weight of the sign acting at its centre', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 19 -- the resonances of a pipe closed at one end
# ═══════════════════════════════════════════════════════════════════════════════
def f_19():
    """The discriminator is the RATIO between successive resonances.

    A pipe closed at one end fits a quarter wavelength, then three quarters, then five --
    so the resonances are in the ratio 1 : 3 : 5, not 1 : 2 : 3.  Drawing the three
    patterns on one axis makes that ratio read straight off the picture.
    """
    W, H = 560, 292
    b = []
    x0, x1 = 120.0, 440.0
    rows = ((70.0, 1, 'L = &#955;/4', 'x1'), (155.0, 3, 'L = 3&#955;/4', 'x3'),
            (240.0, 5, 'L = 5&#955;/4', 'x5'))

    for yc, n, lab, mult in rows:
        b.append(L(x0, yc - 18, x1, yc - 18, INK, 1.4))
        b.append(L(x0, yc + 18, x1, yc + 18, INK, 1.4))
        b.append(L(x0, yc - 22, x0, yc + 22, INK, 3.0))     # closed end
        pts = []
        steps = 160
        for i in range(steps + 1):
            s = i / float(steps)
            pts.append((x0 + (x1 - x0) * s, yc - 15.0 * math.sin(n * math.pi * s / 2.0)))
        b.append(PL(pts, BLUE, 2.2))
        b.append(T(x0, yc + 42, lab, 11.5, 'start', GREY))
        b.append(T(x1 + 16, yc + 4, mult, 12, 'start', BLUE, 'bold'))

    b.append(T(x0, 30, 'closed at the left, open at the right', 11, 'start', GREY))

    return svg(W, H, 'Three standing-wave patterns in a pipe closed at the left and open at '
                     'the right: one quarter wavelength, three quarters and five quarters, '
                     'with the resonances in the ratio 1 to 3 to 5', '\n'.join(b))


# ═══════════════════════════════════════════════════════════════════════════════
# 22 -- charge sharing between two capacitors
# ═══════════════════════════════════════════════════════════════════════════════
def f_22():
    """The discriminator is that CHARGE is what is conserved, not energy.

    A charged capacitor joined across an uncharged one keeps its total charge but the
    common voltage falls, and the energy that disappears goes into heat and radiation in
    the connecting wire.  The figure labels the charge on the charged capacitor, because
    that is the quantity that carries over.
    """
    W, H = 560, 258
    b = [mk('s04-22-ar', INK)]
    yt, yb2, xl, xr = 90.0, 175.0, 110.0, 470.0

    # A full loop, not a single folded line: the two capacitors are in PARALLEL, and a
    # one-line drawing left the reader to guess which plates were joined to which.
    b.append(L(xl, yt, xr, yt, INK, 1.8))
    b.append(L(xl, yb2, xr, yb2, INK, 1.8))
    b.append(L(xl, yt, xl, yb2, INK, 1.8))
    b.append(L(xr, yt, xr, yb2, INK, 1.8))

    # C1, in the top wire, drawn solid because it is the charged one
    b.append(L(xl, yt, 190, yt, INK, 1.8))
    b.append(L(190, yt - 20, 190, yt + 20, INK, 3.2))
    b.append(L(206, yt - 20, 206, yt + 20, INK, 3.2))
    b.append(L(206, yt, 275, yt, INK, 1.8))
    b.append(T(184, yt - 28, '+', 13, 'middle', RED, 'bold'))
    b.append(T(212, yt - 28, '&#8722;', 13, 'middle', BLUE, 'bold'))

    # the switch, closed
    b.append(CI(275, yt, 3.4, INK, 1.4, INK))
    b.append(CI(305, yt, 3.4, INK, 1.4, INK))
    b.append(L(278, yt, 302, yt, INK, 2.0))
    b.append(T(290, yt - 14, 'S closed', 10.5, 'middle', GREY))

    # C2, in grey because it is uncharged
    b.append(L(305, yt, 380, yt, INK, 1.8))
    b.append(L(380, yt - 20, 380, yt + 20, GREY, 3.2))
    b.append(L(396, yt - 20, 396, yt + 20, GREY, 3.2))
    b.append(L(396, yt, xr, yt, INK, 1.8))

    # Subscripts are <tspan>, never <sub> -- `sub` is an HTML foreign-content breakout
    # tag, so inside an inline svg it would close the svg and dump the rest of the figure
    # into the page.  svgkit.svg() raises on it.
    b.append(T(198, 210, 'C<tspan font-size="8.5" dy="3">1</tspan>', 12.5, 'middle', INK, 'bold'))
    b.append(T(198, 228, '4.0 &#956;F', 11.5, 'middle', GREY))
    b.append(T(198, 246, 'carries 48 &#956;C', 11, 'middle', RED))
    b.append(T(388, 210, 'C<tspan font-size="8.5" dy="3">2</tspan>', 12.5, 'middle', INK, 'bold'))
    b.append(T(388, 228, '8.0 &#956;F', 11.5, 'middle', GREY))
    b.append(T(388, 246, 'uncharged', 11, 'middle', GREY))

    return svg(W, H, 'A 4.0 microfarad capacitor carrying 48 microcoulombs connected through a '
                     'closed switch to an uncharged 8.0 microfarad capacitor', '\n'.join(b))


FIGS = {
    's04-01': f_01,
    's04-03': f_03,
    's04-06': f_06,
    's04-07': f_07,
    's04-08': f_08,
    's04-10': f_10,
    's04-11': f_11,
    's04-13': f_13,
    's04-15': f_15,
    's04-16': f_16,
    's04-19': f_19,
    's04-22': f_22,
}
