# -*- coding: utf-8 -*-
"""Figures for BANK SECTION 02 (S02-01 .. S02-25).

Keys are 's02-<QQ>': section 02, question QQ, zero-padded.  Every marker id is prefixed
with the figure key so it cannot collide with any other figure in the bank.

Run `python figs.py` from tools/bank to (re)build fig/.
"""
import math
import os

from svgkit import *


def ell(cx, cy, rx, ry, a0=0, a1=360, c=GREY, sw=1.2, n=40, extra=''):
    """A full or partial ellipse as a sampled polyline, for the perspective circle a
    rotating bob sweeps out.

    Sampled rather than written as an SVG arc, for the same reason svgkit.ARC is: the
    `A` command's large-arc and sweep flags are easy to get wrong and fail silently by
    enlarging the radius.  Sampling removes the whole class of mistake."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / float(n))
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return PL(pts, c, sw, 'none', extra)


def f_02():
    """The endless resistor ladder.

    The discriminator is the SELF-SIMILARITY: one section in front of the rest is the
    same network again.  So the drawing has to make the repetition unmistakable -- three
    identical sections and then a dashed continuation -- and it has to show which way
    round the series and shunt resistors sit, because that is what the fixed-point
    relation encodes."""
    W, H = 580, 250
    b = [mk('s02-02-ar')]

    # rails first, so the opaque resistor boxes sit on top of them
    b.append(L(70, 60, 380, 60, INK, 1.8))
    b.append(L(70, 180, 380, 180, INK, 1.8))

    for k in range(3):
        x = 100 * k
        # series resistor on the top rail
        b.append(RC(110 + x, 52, 40, 16, '#ffffff', INK, 1.6))
        # shunt resistor between the rails
        b.append(RC(172 + x, 100, 16, 40, '#ffffff', INK, 1.6))
        b.append(L(180 + x, 60, 180 + x, 100, INK, 1.8))
        b.append(L(180 + x, 140, 180 + x, 180, INK, 1.8))

    # the ladder does not stop here
    b.append(L(380, 60, 520, 60, GREY, 1.6, ' stroke-dasharray="7 5"'))
    b.append(L(380, 180, 520, 180, GREY, 1.6, ' stroke-dasharray="7 5"'))
    b.append(T(455, 128, 'and so on', 11.5, 'middle', GREY))

    # input terminals.  The stem already asks the question, so the drawing only has to
    # name the two terminals -- three lines of repeated question text just crowded it.
    b.append(CI(70, 60, 5, INK, 1.8, '#ffffff'))
    b.append(CI(70, 180, 5, INK, 1.8, '#ffffff'))
    b.append(T(48, 64, 'A', 12, 'end', BLUE, 'bold'))
    b.append(T(48, 184, 'B', 12, 'end', BLUE, 'bold'))

    b.append(T(130, 44, 'R', 12, 'middle', INK))
    b.append(T(196, 124, 'R', 12, 'start', INK))
    b.append(T(70, 226, 'Every resistor in the network has the same resistance R.', 11.5, 'start', GREY))

    return svg(550, H, 'An endless resistor ladder: a series resistor R followed by a '
                       'shunt resistor R, repeated without end', '\n'.join(b))


def f_05():
    """The conical pendulum.

    The discriminator is that the RADIUS of the circle is L sin(theta), not L -- almost
    every wrong option in the question comes from confusing the string length with the
    radius.  So the drawing marks both, separately, and shows the bob's circular path in
    perspective so that "horizontal circle" is visible rather than asserted."""
    W, H = 420, 250
    px, py = 150.0, 46.0                      # pivot
    # NOT named L: svgkit exports L() as the line helper, and a local L would shadow it
    # and fail with "'float' object is not callable" on the first line drawn.
    slen = 150.0
    th = math.radians(30.0)
    bx = px + slen * math.sin(th)             # bob, 225.0
    by = py + slen * math.cos(th)             # 175.9
    axis_y = 196.0

    b = [mk('s02-05-ar'), mk('s02-05-ag'), mk('s02-05-aa')]

    # the circle the bob sweeps out, in perspective.  Centred on the AXIS, not on the
    # midpoint: the bob is at the near point of the circle, so the far point is
    # diametrically opposite it, at px - (bx - px).  An ellipse centred on the midpoint
    # comes out half size and reads as an arc floating beside the bob.
    b.append(ell(px, by, bx - px, 11.0, 0, 360, GREY, 1.2, 44,
                 ' stroke-dasharray="5 4"'))

    # the axis it turns about
    b.append(L(px, py, px, axis_y, GREY, 1.4, ' stroke-dasharray="6 4"'))

    # the string, and the bob on the end of it
    b.append(L(px, py, bx, by, INK, 1.8))
    b.append(CI(bx, by, 9, INK, 1.8, '#ffffff'))

    # the angle between the string and the vertical.  theta goes INSIDE the wedge, which
    # at this height means between x = px and x = px + (y - py) tan(theta).
    b.append(ARC(px, py, 55, 60, 90, RED, 1.4))
    b.append(T(163, 92, '&#952;', 12, 'middle', RED))

    # the radius, which is NOT the string length.  Labelled clear of both the dashed
    # radius line and the lower arc of the path ellipse.
    b.append(L(px, by, bx - 9, by, BLUE, 1.5, ' stroke-dasharray="5 4"'))
    b.append(T(170, by + 32, 'r = L sin&#952;', 11, 'middle', BLUE))

    # the length of the string
    b.append(T(194, 106, 'L', 12, 'start', INK))

    # the weight
    b.append(L(bx, by + 9, bx, by + 44, RED, 2.2, ' marker-end="url(#s02-05-ar)"'))
    b.append(T(bx + 6, by + 34, 'mg', 11.5, 'start', RED))

    b.append(T(24, 228, 'The bob moves in a horizontal circle of radius r.', 11.5,
               'start', GREY))
    b.append(T(24, 244, 'The tension has to hold the weight up as well as turn the bob.',
               11.5, 'start', GREY))

    return svg(W, H, 'A conical pendulum: a bob on a string of length L sweeping a '
                      'horizontal circle, with the string at angle theta to the vertical',
               '\n'.join(b))


def f_11():
    """Activity against time, with the activity axis LOGARITHMIC.

    The discriminator is that equal RATIOS occupy equal DISTANCES vertically, so the
    straight line IS the exponential and the drop 800 -> 100 can be counted as three
    halvings rather than read off point by point.  Two consequences for the drawing:

      * the ticks 100, 200, 400, 800 must be evenly spaced even though their values are
        not, or the whole point of the log axis is invisible;
      * the time gridlines must sit at multiples of 3, so that the crossing at t = 4
        (which is the answer) is NOT marked.  Marking it would turn a ratio argument
        into a reading-off exercise.
    """
    W, H = 500, 272
    x0, y0 = 74.0, 212.0
    pm = 24.0                                   # px per minute
    b = [mk('s02-11-ar')]

    # gridlines first, so the axes and the plotted line sit on top
    for k in range(4):
        y = 190 - 40 * k                        # 100 -> 190, 200 -> 150, 400 -> 110, 800 -> 70
        b.append(L(x0, y, x0 + 15 * pm, y, WALL, 1.0))
    for t in range(0, 16, 3):
        b.append(L(x0 + t * pm, y0, x0 + t * pm, 60, WALL, 1.0))

    # axes
    b.append(L(x0, 60, x0, y0, INK, 1.8))
    b.append(L(x0, y0, x0 + 15 * pm, y0, INK, 1.8))

    # y ticks -- evenly spaced, which is the whole content of the figure
    for k, val in enumerate((100, 200, 400, 800)):
        y = 190 - 40 * k
        b.append(L(x0 - 6, y, x0, y, INK, 1.5))
        b.append(T(x0 - 10, y + 4, str(val), 11, 'end', INK))

    # x ticks
    for t in range(0, 16, 3):
        b.append(L(x0 + t * pm, y0, x0 + t * pm, y0 + 6, INK, 1.5))
        b.append(T(x0 + t * pm, y0 + 20, str(t), 11, 'middle', INK))

    # the decay: straight on a log axis, from (0, 800) to (12, 100)
    b.append(L(x0, 70, x0 + 12 * pm, 190, BLUE, 2.0))
    b.append(CI(x0, 70, 4.5, BLUE, 1.8, '#ffffff'))
    b.append(CI(x0 + 12 * pm, 190, 4.5, BLUE, 1.8, '#ffffff'))

    # only the two stated points are labelled, and only with their VALUES: the x-axis
    # already names 0 and 12, so the positions identify the points and the long
    # "at t = ... min" wording is redundant.  It was also 180 px of text hanging off the
    # right edge, which the overflow lint now catches.
    b.append(T(x0 + 12, 64, '800 kBq', 11, 'start', BLUE))
    b.append(T(x0 + 12 * pm + 10, 186, '100 kBq', 11, 'start', BLUE))

    b.append(T(x0, 34, 'activity / kBq, on a logarithmic scale', 11.5, 'start', GREY))
    # centred under the axis: right-aligned at the far end it ran into the "15" tick
    b.append(T(x0 + 7.5 * pm, y0 + 40, 'time / min', 11.5, 'middle', GREY))

    return svg(W, H, 'A straight line on a graph of activity against time, where the '
                      'activity axis is logarithmic: the activity falls from 800 kBq at '
                      't = 0 to 100 kBq at t = 12 min', '\n'.join(b))


def f_12():
    """The cell with internal resistance driving a series-parallel network.

    The discriminator is that the internal resistance is PART OF THE LOOP, so the current
    is not 12/6.  The drawing therefore puts the internal resistor inside a dashed box
    with the cell -- it belongs to the source, not to the external circuit -- and labels
    it in the same style as the external resistors so that it cannot be overlooked as
    decoration.
    """
    W, H = 520, 250
    top, bot = 64.0, 186.0
    xl, xr = 74.0, 468.0
    b = [mk('s02-12-ar')]

    # the rails
    b.append(L(xl, top, xr, top, INK, 1.8))
    b.append(L(xl, bot, xr, bot, INK, 1.8))
    b.append(L(xl, top, xl, bot, INK, 1.8))
    b.append(L(xr, top, xr, bot, INK, 1.8))

    # the cell on the left limb: a long plate and a short one
    b.append(L(54, 112, 94, 112, INK, 2.4))
    b.append(L(64, 134, 84, 134, INK, 2.4))
    b.append(T(104, 118, '12 V', 12, 'start', INK, 'bold'))

    # the source's own resistance.  It sits on the top rail in series with the cell, and
    # BOTH are inside the dashed box -- a box drawn round the cell alone would say the
    # internal resistance is part of the external circuit, which is the error the question
    # is about.
    b.append(RC(112, top - 8, 46, 16, '#ffffff', INK, 1.6))
    b.append(T(135, 92, 'r = 2 &#937;', 11, 'middle', RED))
    b.append(RC(44, 46, 132, 108, 'none', GREY, 1.2))
    b.append(T(46, 172, 'the source', 10.5, 'start', GREY))

    # the parallel pair
    for x in (240.0, 320.0):
        b.append(L(x, top, x, 97, INK, 1.8))
        b.append(L(x, 153, x, bot, INK, 1.8))
        b.append(RC(x - 8, 97, 16, 56, '#ffffff', INK, 1.6))
        b.append(T(x + 14, 128, '6 &#937;', 11, 'start', INK))

    # the series resistor
    b.append(RC(396, top - 8, 46, 16, '#ffffff', INK, 1.6))
    b.append(T(419, top - 14, '3 &#937;', 11, 'middle', INK))

    b.append(T(xl + 4, 216, 'The source has an internal resistance of 2 &#937;.',
               11.5, 'start', GREY))
    b.append(T(xl + 4, 232, 'The two 6 &#937; resistors are in parallel with each other.',
               11.5, 'start', GREY))

    return svg(W, H, 'A circuit: a 12 V source with 2 ohm internal resistance driving two '
                      '6 ohm resistors in parallel, in series with a 3 ohm resistor',
               '\n'.join(b))


def f_14():
    """Charge sharing between two capacitors, before and after.

    The discriminator is that the PLATES ARE ISOLATED when the switch closes, so the
    charge is what is conserved and the potential difference is not.  So the figure has
    to show two separate panels: the charging (with the supply) and the joining (without
    it).  A single panel would leave the reader free to assume the battery is still
    connected, which is the error that produces V/2 instead of V/3.
    """
    W, H = 560, 236
    b = [mk('s02-14-ar')]

    # ── panel (a): charging, supply attached ────────────────────────────────
    b.append(RC(26, 44, 244, 152, PANEL))
    b.append(T(38, 64, '(a) charged to V, supply removed', 11, 'start', GREY, 'bold'))
    # battery
    b.append(L(62, 106, 92, 106, INK, 2.4))
    b.append(L(70, 126, 84, 126, INK, 2.4))
    b.append(T(50, 100, 'V', 11.5, 'end', INK, 'bold'))
    # wires up to the capacitor
    b.append(L(77, 106, 77, 88, INK, 1.7))
    b.append(L(77, 88, 200, 88, INK, 1.7))
    b.append(L(200, 88, 200, 108, INK, 1.7))
    b.append(L(200, 126, 200, 166, INK, 1.7))
    b.append(L(200, 166, 77, 166, INK, 1.7))
    b.append(L(77, 166, 77, 126, INK, 1.7))
    # the capacitor plates
    b.append(L(176, 108, 224, 108, INK, 2.6))
    b.append(L(176, 126, 224, 126, INK, 2.6))
    b.append(T(232, 122, 'C', 12.5, 'start', BLUE, 'bold'))

    # ── panel (b): the two capacitors joined, no supply ─────────────────────
    b.append(RC(290, 44, 244, 152, PANEL))
    b.append(T(302, 64, '(b) now joined by the switch', 11, 'start', GREY, 'bold'))
    # top wire with a switch
    b.append(L(344, 108, 344, 90, INK, 1.7))
    b.append(L(344, 90, 396, 90, INK, 1.7))
    b.append(CI(396, 90, 3.5, INK, 1.7, '#ffffff'))
    b.append(L(396, 90, 424, 74, INK, 1.9))          # the blade, open
    b.append(CI(424, 90, 3.5, INK, 1.7, '#ffffff'))
    b.append(L(424, 90, 476, 90, INK, 1.7))
    b.append(L(476, 90, 476, 108, INK, 1.7))
    # bottom wire
    b.append(L(344, 126, 344, 160, INK, 1.7))
    b.append(L(344, 160, 476, 160, INK, 1.7))
    b.append(L(476, 160, 476, 126, INK, 1.7))
    # capacitor C
    b.append(L(320, 108, 368, 108, INK, 2.6))
    b.append(L(320, 126, 368, 126, INK, 2.6))
    b.append(T(344, 186, 'C', 12.5, 'middle', BLUE, 'bold'))
    # capacitor 2C, drawn wider to show the larger capacitance.  Its plates stop short of
    # the panel edge -- at 528 they touched it and the label ran off the canvas.
    b.append(L(436, 108, 516, 108, INK, 2.6))
    b.append(L(436, 126, 516, 126, INK, 2.6))
    b.append(T(476, 186, '2C', 12.5, 'middle', BLUE, 'bold'))
    # The two plates of each capacitor are joined to the corresponding plate of the other.
    # Kept short and set at the left margin: the previous wording ran 180 px past the
    # right edge of the viewBox and was silently clipped.
    b.append(T(26, 218, 'Each upper plate is joined to the other upper plate, and the '
                        'lower plates likewise.', 11, 'start', GREY))

    return svg(W, H, 'Two panels: a capacitor C charged to a potential difference V with '
                      'the supply attached, and then the same capacitor joined by a switch '
                      'to an uncharged capacitor of capacitance 2C', '\n'.join(b))


def f_16():
    """Two coherent sources and a point off the axis.

    The discriminator is the PATH DIFFERENCE, and nothing else: not the two distances
    separately, and certainly not the distance from the midpoint.  So the drawing gives
    the two path lengths and marks no midpoint, no perpendicular bisector and no
    separation between the sources -- every one of those would invite the reader to
    compute something that does not enter the answer.
    """
    W, H = 480, 284
    s1x, s1y = 140.0, 214.0
    s2x, s2y = 330.0, 214.0
    px, py = 255.0, 72.0
    b = []

    # the two paths, dashed so the eye reads them as measurements rather than apparatus
    b.append(L(s1x, s1y, px, py, GREY, 1.6, ' stroke-dasharray="7 5"'))
    b.append(L(s2x, s2y, px, py, GREY, 1.6, ' stroke-dasharray="7 5"'))

    # the sources and the point
    b.append(CI(s1x, s1y, 6.5, INK, 1.8, '#ffffff'))
    b.append(CI(s2x, s2y, 6.5, INK, 1.8, '#ffffff'))
    b.append(CI(px, py, 6.5, BLUE, 1.8, '#ffffff'))
    b.append(T(s1x, 238, 'S1', 12.5, 'middle', INK, 'bold'))
    b.append(T(s2x, 238, 'S2', 12.5, 'middle', INK, 'bold'))
    b.append(T(px, 58, 'P', 12.5, 'middle', BLUE, 'bold'))

    # path lengths, placed clear of the lines they label.  Round values on purpose: the
    # answer turns on the DIFFERENCE being exactly half a wavelength, and 2.5 with 3.5
    # makes that difference 1.0 at a glance.
    b.append(T(133, 160, '2.5 m', 11.5, 'start', INK))
    b.append(T(300, 130, '3.5 m', 11.5, 'start', INK))

    # the one fact the figure cannot show and the reader must be told
    b.append(T(28, 268, 'S1 and S2 are driven by the same oscillator, so they emit in '
                        'phase.', 11, 'start', GREY))

    return svg(W, H, 'Two loudspeakers S1 and S2 and a point P, with the path from S1 to '
                      'P marked 2.5 m and the path from S2 to P marked 3.5 m',
               '\n'.join(b))


def f_17():
    """Force against extension for a wire, straight up to the limit of proportionality.

    The discriminator is the GRADIENT, so the two numbers the reader needs -- 2.0 mm and
    40 N -- are given by the graph and NOT repeated in the stem.  Repeating them would
    make the figure decorative and turn a gradient-reading question into an arithmetic
    one.  Dashed guides are drawn to both axes so the point can be read unambiguously.
    """
    W, H = 470, 274
    x0, y0 = 74.0, 212.0
    pm = 128.0                       # px per mm of extension
    pn = 3.2                         # px per newton
    ex, fy = 2.0, 40.0
    gx, gy = x0 + ex * pm, y0 - fy * pn
    b = []

    # gridlines
    for k in range(1, 6):
        b.append(L(x0 + k * 0.5 * pm, y0, x0 + k * 0.5 * pm, 52, WALL, 1.0))
    for k in range(1, 6):
        b.append(L(x0, y0 - k * 10 * pn, x0 + 2.5 * pm, y0 - k * 10 * pn, WALL, 1.0))

    b.append(L(x0, 52, x0, y0, INK, 1.8))
    b.append(L(x0, y0, x0 + 2.5 * pm, y0, INK, 1.8))

    for k in range(0, 6):
        x = x0 + k * 0.5 * pm
        b.append(L(x, y0, x, y0 + 6, INK, 1.4))
        b.append(T(x, y0 + 21, ('%g' % (k * 0.5)), 11, 'middle', INK))
    for k in range(0, 6):
        y = y0 - k * 10 * pn
        b.append(L(x0 - 6, y, x0, y, INK, 1.4))
        b.append(T(x0 - 10, y + 4, str(k * 10), 11, 'end', INK))

    # the guides, then the line, then the point on top of both
    b.append(L(gx, gy, gx, y0, GREY, 1.2, ' stroke-dasharray="5 4"'))
    b.append(L(x0, gy, gx, gy, GREY, 1.2, ' stroke-dasharray="5 4"'))
    b.append(L(x0, y0, gx, gy, BLUE, 2.2))
    b.append(CI(gx, gy, 4.5, BLUE, 1.8, '#ffffff'))

    b.append(T(x0 + 2, 44, 'force / N', 11.5, 'start', GREY))
    b.append(T(x0 + 2.5 * pm, y0 + 40, 'extension / mm', 11.5, 'end', GREY))
    # No "limit of proportionality" annotation.  It was redundant -- the stem already
    # says so -- and every position tried either sat on the data point or was crossed by
    # the gridline at 30 N.  The figure's job is the gradient; the stem's job is words.

    return svg(W, H, 'A straight-line graph of force against extension for a wire, '
                      'passing through the origin and through the point 2.0 mm, 40 N',
               '\n'.join(b))


def f_21():
    """Four nuclear energy levels, with ONE transition drawn.

    The discriminator is that the nucleus may drop straight to any lower level, so the
    observable photon energies are the differences between EVERY pair of levels.  The
    drawing must therefore show the four levels clearly and mark exactly one transition
    as an example -- drawing all six would print the answer, and drawing none would leave
    the reader unsure what a transition is.

    The four spacings are chosen so that all six differences are distinct (1, 2, 3, 4, 6
    and 7 MeV), which is what makes the count come out as six rather than five.
    """
    W, H = 420, 268
    x0, x1 = 96.0, 264.0
    b = [mk('s02-21-ar')]
    levels = [(0.0, '0'), (1.0, '1.0'), (3.0, '3.0'), (7.0, '7.0')]

    def yy(e):
        return 224.0 - e * 22.0

    # the levels, each labelled with its energy above the ground state
    for e, lab in levels:
        y = yy(e)
        b.append(L(x0, y, x1, y, INK, 2.0))
        b.append(T(x1 + 10, y + 4, lab, 11.5, 'start', INK))

    # one transition, as the example the stem refers to
    ytop, ybot = yy(7.0), yy(0.0)
    ax = 150.0
    b.append(L(ax, ytop + 2, ax, ybot - 2, BLUE, 1.8, ' marker-end="url(#s02-21-ar)"'))
    # The label goes in the gap between the 3.0 and 1.0 levels, clear of the arrow.  At
    # y = 150 it sat on the 3.0 MeV level line, which the stroke-collision check catches.
    b.append(T(ax + 10, 180, 'one possible', 10.5, 'start', BLUE))
    b.append(T(ax + 10, 194, 'transition', 10.5, 'start', BLUE))

    # the energy scale
    b.append(T(x0 - 8, 30, 'energy above the ground state', 11, 'start', GREY))
    b.append(T(x1 + 10, 246, 'MeV', 11, 'start', GREY))

    return svg(W, H, 'Four nuclear energy levels at 0, 1.0, 3.0 and 7.0 MeV above the '
                      'ground state, with one downward transition arrow drawn as an '
                      'example', '\n'.join(b))


FIGS = {
    's02-02': f_02,
    's02-05': f_05,
    's02-11': f_11,
    's02-12': f_12,
    's02-14': f_14,
    's02-16': f_16,
    's02-17': f_17,
    's02-21': f_21,
}
