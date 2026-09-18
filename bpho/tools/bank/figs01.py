# -*- coding: utf-8 -*-
"""Figures for BANK SECTION 01 (S01-01 .. S01-25).

Keys are 's01-<QQ>': section 01, question QQ, zero-padded.  Every marker id is prefixed
with the figure key so it cannot collide with any other figure in the bank.

Run `python figs.py` from tools/bank to (re)build fig/.
"""
import math
import os

from svgkit import *



# ═════════════════════════════════════════════════════════════════════════════
# s01-02  potential divider loaded by a real voltmeter
# ═════════════════════════════════════════════════════════════════════════════
def f_02():
    b = [mk('q02-ar')]
    # outer loop
    b.append(L(60, 50, 270, 50, INK, 2))                    # top rail
    b.append(L(270, 50, 270, 110, INK, 2))                  # down to the node
    b.append(L(270, 110, 270, 170, INK, 2))                 # R2
    b.append(L(270, 170, 60, 170, INK, 2))                  # bottom rail
    b.append(L(60, 170, 60, 50, INK, 2))                    # up the left side
    # the cell, drawn as two plates on the left rail
    b.append(L(48, 104, 72, 104, INK, 2.2))
    b.append(L(54, 118, 66, 118, INK, 5))
    b.append(T(42, 116, '12 V', 11.5, 'end', INK))
    # R1 and R2 as boxes.  Their labels go to the LEFT of the boxes, anchored on
    # their right edge, so the voltmeter branch on the right has a clear lane.
    b.append(RC(262, 62, 16, 40, WALL, INK, 1.6))
    b.append(T(252, 86, 'R\u2081 = 6.0 k\u03a9', 11.5, 'end', INK))
    b.append(RC(262, 120, 16, 40, WALL, INK, 1.6))
    b.append(T(252, 144, 'R\u2082 = 3.0 k\u03a9', 11.5, 'end', INK))
    # voltmeter branch: off the node, right, down through the meter, and back to
    # the bottom rail.  Every segment has non-zero length.
    b.append(L(270, 110, 350, 110, INK, 1.7))
    b.append(L(350, 110, 350, 126, INK, 1.7))
    b.append(CI(350, 140, 14, BLUE, 1.8))
    b.append(T(350, 144, 'V', 12, 'middle', BLUE))
    b.append(L(350, 154, 350, 170, INK, 1.7))
    b.append(L(350, 170, 270, 170, INK, 1.7))
    b.append(T(350, 196, 'voltmeter', 11, 'middle', BLUE))
    b.append(T(350, 210, '6.0 k\u03a9', 11, 'middle', BLUE))
    return svg(420, 226, 'A potential divider across a 12 V supply: a 6.0 kilohm '
               'resistor and a 3.0 kilohm resistor in series, with a voltmeter of '
               'resistance 6.0 kilohm connected across the 3.0 kilohm resistor.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-04  bullet embedding in a spring-mounted block
# ═════════════════════════════════════════════════════════════════════════════
def f_04():
    b = [mk('q04-ar')]
    b.append(L(20, 120, 380, 120, INK, 2))                  # ground
    for x in range(28, 380, 16):                            # hatching below the ground
        b.append(L(x, 120, x - 8, 128, GREY, 1.1))
    # bullet
    b.append(CI(52, 100, 7, RED, 1.8, RED))
    b.append(L(59, 100, 92, 100, RED, 2, ' marker-end="url(#q04-ar)"'))
    b.append(T(44, 84, 'm', 12, 'middle', RED))
    b.append(T(52, 78, 'u', 12, 'middle', RED))
    # block
    b.append(RC(120, 70, 64, 50, WALL, INK, 1.8))
    b.append(T(152, 60, '3m', 12, 'middle', INK))
    # spring from the block to the wall
    zz = [(184, 95)]
    for i in range(6):
        zz.append((192 + i * 14, 82 if i % 2 == 0 else 108))
    zz.append((276, 95))
    b.append(PL(zz, GREEN, 2))
    b.append(T(230, 66, 'stiffness k', 11.5, 'middle', GREEN))
    # wall
    b.append(L(300, 40, 300, 120, INK, 3))
    for y in range(44, 120, 16):
        b.append(L(300, y, 312, y + 10, GREY, 1.1))
    b.append(T(316, 88, 'fixed', 11, 'start', INK))
    return svg(400, 160, 'A bullet of mass m travelling at speed u approaches a block '
               'of mass 3m resting on frictionless ground. The block is attached to a '
               'spring of stiffness k, fixed at its far end to a rigid wall.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-07  a ball passing the same height twice
# ═════════════════════════════════════════════════════════════════════════════
def f_07():
    b = [mk('q07-ar')]
    b.append(L(40, 195, 380, 195, INK, 2))                  # ground
    # the trajectory: a parabola from the left foot, apex at x=200, down again
    pts = []
    for i in range(0, 61):
        x = 100 + i * (200 / 60.0)
        y = 195 - 140 * (1 - ((x - 200) / 100.0) ** 2)
        pts.append((x, y))
    b.append(PL(pts, BLUE, 2.2))
    # launch speed indicator at the left foot
    b.append(PA('M88,183 Q100,169 112,183', BLUE, 1.6))
    b.append(T(100, 164, 'u', 12.5, 'middle', BLUE))
    # The height h is a HORIZONTAL line, because that is what "a height" means:
    # the question is about one height crossed at two different times.  Drawing it
    # vertically (as a first draft did) makes the figure argue for the wrong thing.
    b.append(L(110, 115, 290, 115, GREY, 1.4, ' stroke-dasharray="6 4"'))
    b.append(T(104, 119, 'h', 12.5, 'end', GREY))
    b.append(CI(134.5, 115, 3.6, RED, 1.6, RED))            # crossed going up
    b.append(CI(265.5, 115, 3.6, RED, 1.6, RED))            # crossed going down
    # labels sit outside the parabola, joined to the crossing points by leaders
    b.append(L(114, 100, 132, 113, GREY, 1.1))
    b.append(T(56, 96, 'going up', 11, 'start', GREY))
    b.append(L(300, 80, 268, 112, GREY, 1.1))
    b.append(T(304, 76, 'going down', 11, 'start', GREY))
    b.append(T(200, 216, 'ground', 11, 'middle', GREY))
    return svg(420, 232, 'The trajectory of a ball thrown vertically upward from ground '
               'level with speed u. A dashed horizontal line marks a height h, which the '
               'trajectory crosses twice: once on the way up and once on the way down.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-08  a beam held by an angled stay
# ═════════════════════════════════════════════════════════════════════════════
def f_08():
    b = [mk('q08-ar')]
    # wall.  The hatching goes on the SIDE THE WALL IS ON (left), otherwise it
    # reads as a free edge rather than a rigid support.
    b.append(L(50, 20, 50, 200, INK, 3))
    for y in range(24, 200, 18):
        b.append(L(50, y, 38, y + 10, GREY, 1.1))
    # beam
    b.append(L(50, 160, 290, 160, INK, 3))
    # stay wire from the far end back to the wall at 30 degrees to the beam
    b.append(L(290, 160, 50, 160 - 240 * 0.5774, AMBER, 2.2))
    b.append(CI(50, 160, 5, RED, 2, RED))
    b.append(T(44, 186, 'O', 12.5, 'end', RED))
    # the 30 degree marker: an arc centred on the vertex, where the angle is
    b.append(ARC(290, 160, 40, 180, 210, GREY, 1.3))
    b.append(T(240, 150, '30\u00b0', 11.5, 'end', GREY))
    b.append(T(200, 92, 'T', 12.5, 'middle', AMBER))
    b.append(T(170, 186, 'W = mg', 11.5, 'middle', INK))
    b.append(L(170, 176, 170, 162, GREY, 1.3, ' marker-end="url(#q08-ar)"'))
    b.append(T(170, 214, 'uniform beam, length 4.0 m', 11, 'middle', GREY))
    b.append(T(170, 144, 'centre of gravity', 10.5, 'middle', GREY))
    b.append(CI(170, 160, 3, GREY, 1.2, GREY))
    return svg(340, 230, 'A uniform horizontal beam hinged at O to a vertical wall. A '
               'stay wire runs from the far end of the beam back to the wall, making an '
               'angle of 30 degrees with the beam. The weight of the beam acts at its '
               'midpoint.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-10  the resonances of a pipe closed at one end
# ═════════════════════════════════════════════════════════════════════════════
def f_10():
    b = [mk('q10-ar')]
    b.append(L(50, 70, 330, 70, INK, 2))
    b.append(L(50, 130, 330, 130, INK, 2))
    b.append(L(50, 60, 50, 140, INK, 4))                    # the closed end
    b.append(T(50, 50, 'closed end', 11.5, 'middle', INK))
    b.append(T(330, 50, 'open end', 11.5, 'middle', INK))
    # the fundamental: displacement zero at the closed end, largest at the open end
    b.append(PA('M50,100 Q200,100 330,72', BLUE, 2.2))
    b.append(T(52, 156, 'node', 11.5, 'middle', BLUE))
    b.append(T(330, 156, 'antinode', 11.5, 'middle', BLUE))
    b.append(L(50, 140, 50, 148, GREY, 1.2))
    b.append(L(330, 140, 330, 148, GREY, 1.2))
    b.append(T(190, 186, 'the fundamental: a quarter of a wavelength fits', 11, 'middle', GREY))
    return svg(380, 200, 'A pipe closed at its left end and open at its right. The curve '
               'shows the fundamental standing wave: the air cannot move at the closed '
               'end, so there is a node there, and it moves most at the open end, so '
               'there is an antinode there.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-11  total internal reflection in a 45-45-90 prism
# ═════════════════════════════════════════════════════════════════════════════
def f_11():
    b = [mk('q11-ar')]
    b.append(PG([(80, 40), (240, 40), (80, 200)], INK, 2, WALL))
    # incident ray: vertical, along the normal of the top face
    b.append(L(160, 12, 160, 120, RED, 2.2, ' marker-end="url(#q11-ar)"'))
    # the normal at the point of incidence, as a dashed construction line through it
    b.append(L(140, 100, 180, 140, GREY, 1.4, ' stroke-dasharray="5 4"'))
    # reflected ray: horizontally out through the left face
    b.append(L(160, 120, 80, 120, BLUE, 2.2))
    b.append(L(80, 120, 34, 120, BLUE, 2.2, ' marker-end="url(#q11-ar)"'))
    # the angle of incidence, drawn in the wedge between the ray and the normal
    b.append(ARC(160, 120, 20, 270, 225, RED, 1.3))
    b.append(T(145, 92, '45\u00b0', 11.5, 'middle', RED))
    b.append(T(150, 62, 'incident', 11, 'end', RED))
    b.append(T(86, 108, 'reflected', 11, 'start', BLUE))
    b.append(T(100, 82, 'glass', 11, 'start', GREY))
    b.append(T(200, 24, 'air', 11, 'start', GREY))
    b.append(T(160, 220, 'the long face is the hypotenuse', 11, 'middle', GREY))
    return svg(320, 230, 'A right-angled isosceles glass prism. A ray enters normally '
               'through the upper face, so it is not bent, and meets the hypotenuse at '
               '45 degrees to the normal. It is drawn totally internally reflected and '
               'leaves through the left face.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-12  the current-voltage characteristic of a filament lamp
# ═════════════════════════════════════════════════════════════════════════════
def f_12():
    b = [mk('q12-ar')]
    X0, Y0 = 60, 210           # origin
    X1, Y1 = 320, 40           # top right of the plotting area
    b.append(L(X0, Y0, X1 + 12, Y0, INK, 1.7, ' marker-end="url(#q12-ar)"'))
    b.append(L(X0, Y0, X0, Y1 - 12, INK, 1.7, ' marker-end="url(#q12-ar)"'))
    b.append(T(X1 + 14, Y0 + 18, 'V / V', 11.5, 'end', INK))
    b.append(T(46, Y1 - 6, 'I / A', 11.5, 'end', INK))
    # the characteristic: straight enough near the origin, then flattening
    pts = [(60, 210), (100, 176), (140, 146), (180, 122), (220, 104), (260, 92), (320, 82)]
    b.append(PL(pts, BLUE, 2.4))
    # the marked point at 6.0 V, 0.40 A
    px, py = 255, 93
    b.append(L(X0, py, px, py, GREY, 1.3, ' stroke-dasharray="5 4"'))
    b.append(L(px, py, px, Y0, GREY, 1.3, ' stroke-dasharray="5 4"'))
    b.append(CI(px, py, 4, RED, 2, RED))
    b.append(T(px + 10, py - 8, 'P', 12, 'start', RED))
    # axis numbers, kept off the curves
    for v, x in ((2, 125), (4, 190), (6, 255)):
        b.append(T(x, Y0 + 17, str(v), 11, 'middle', GREY))
    for i, y in ((0.2, 153), (0.4, 96)):
        b.append(T(X0 - 8, y + 4, str(i), 11, 'end', GREY))
    b.append(T(180, 240, 'a filament lamp: the resistance rises as the current rises',
               11, 'middle', GREY))
    return svg(360, 250, 'The current-voltage characteristic of a filament lamp. The '
               'curve passes through the origin and bends over as the current rises, '
               'because the filament gets hotter and its resistance increases. A point '
               'P is marked at 6.0 volts and 0.40 amperes.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-14  alpha decay: the recoil
# ═════════════════════════════════════════════════════════════════════════════
def f_14():
    b = [mk('q14-ar')]
    b.append(CI(80, 80, 18, PURPLE, 2.2, '#ece7f8'))
    b.append(T(80, 85, 'A', 13, 'middle', PURPLE))
    b.append(T(80, 46, 'at rest', 11, 'middle', GREY))
    b.append(PA('M108,80 L196,80', GREY, 1.6, 'none', ' marker-end="url(#q14-ar)"'))
    b.append(T(152, 70, 'decays', 11, 'middle', GREY))
    # the two products
    b.append(CI(240, 56, 11, RED, 2, '#fbeceb'))
    b.append(T(240, 60, '\u03b1', 12.5, 'middle', RED))
    b.append(T(240, 30, 'mass 4', 11, 'middle', RED))
    b.append(L(258, 56, 316, 56, RED, 2.2, ' marker-end="url(#q14-ar)"'))
    b.append(CI(240, 118, 17, GREEN, 2, '#e9f5f0'))
    b.append(T(240, 123, 'A\u22124', 11.5, 'middle', GREEN))
    b.append(T(240, 152, 'mass A \u2212 4', 11, 'middle', GREEN))
    b.append(L(216, 118, 158, 118, GREEN, 2.2, ' marker-end="url(#q14-ar)"'))
    b.append(T(180, 176, 'the two products separate with equal and opposite momenta',
               11, 'middle', GREY))
    return svg(360, 190, 'A nucleus of mass number A at rest decays by emitting an alpha '
               'particle of mass number 4. The alpha particle and the recoiling nucleus '
               'of mass number A minus 4 separate with equal and opposite momenta.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-15  a wire stretched at constant volume
# ═════════════════════════════════════════════════════════════════════════════
def f_15():
    b = [mk('q15-ar')]
    # before: short and fat
    b.append(RC(60, 44, 90, 26, '#dfe8f6', INK, 1.8))
    b.append(T(105, 32, 'before: R, length L, area A', 11, 'middle', INK))
    b.append(L(152, 57, 196, 57, AMBER, 2.4, ' marker-end="url(#q15-ar)"'))
    b.append(T(174, 44, 'stretch', 11, 'middle', AMBER))
    # after: long and thin
    b.append(RC(60, 104, 150, 15, '#dfe8f6', INK, 1.8))
    b.append(T(135, 140, 'after: length L(1 + x), area A / (1 + x)', 11, 'middle', INK))
    b.append(T(300, 70, 'volume', 11, 'middle', GREY))
    b.append(T(300, 86, 'unchanged', 11, 'middle', GREY))
    b.append(PA('M262,104 L262,70', GREY, 1.4))
    b.append(PA('M262,70 L262,60', GREY, 1.4))
    b.append(T(200, 172, 'the wire gets longer AND thinner, and both raise the resistance',
               11, 'middle', GREY))
    return svg(400, 190, 'A uniform wire of resistance R, length L and cross-sectional '
               'area A is stretched so that its length becomes L times one plus x. Its '
               'volume is unchanged, so its cross-sectional area falls in the same '
               'proportion.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-16  five candidate velocity-time graphs for a bouncing ball
# ═════════════════════════════════════════════════════════════════════════════
def _panel(x0, y0, w, h, letter, pts, colour, extra=None):
    """One candidate v-t panel.

    The time axis runs through the MIDDLE of the panel, not along its bottom edge.
    That is forced by the physics: the question takes downward as negative, so the
    ball's velocity is negative for most of the flight and a panel whose axis sits
    on the bottom edge can only ever show the upward half.  The first draft had it
    along the bottom, which made every panel contradict the stated convention.
    """
    out = [mk('q16%s-ar' % letter)]
    ymid = y0 + h / 2.0
    out.append(RC(x0 - 6, y0 - 6, w + 16, h + 26, PANEL))
    out.append(L(x0, ymid, x0 + w, ymid, INK, 1.5, ' marker-end="url(#q16%s-ar)"' % letter))
    out.append(L(x0, y0 + h, x0, y0, INK, 1.5, ' marker-end="url(#q16%s-ar)"' % letter))
    out.append(T(x0 + w + 8, ymid + 12, 't', 11, 'middle', INK))
    out.append(T(x0 - 12, y0 - 4, 'v', 11, 'middle', INK))
    if pts:
        out.append(PL(pts, colour, 2.2))
    if extra:
        out.append(extra)
    out.append(T(x0 + w / 2.0, y0 + h + 17, letter, 12, 'middle', INK, '600'))
    return out


def f_16():
    W, H = 580, 340
    b = []

    # ---- A: velocity that is never negative.  A decaying zigzag that stays
    # entirely above the axis -- i.e. a SPEED-time graph.  The error is the
    # convention: while the ball falls its velocity is negative.
    pa = [(30, 81), (72, 47), (72, 64), (93, 81), (114, 64), (114, 72.5), (124.5, 81)]

    # ---- B: a curve whose slope steepens without limit
    b_curve = PA('M225,81 C285,87 335,107 365,133', RED, 2.2)

    # ---- C: rises to a positive peak, falls to zero once, then stays there
    pc = [(400, 81), (460, 47), (520, 81), (540, 81)]

    # ---- D: straight sections of the SAME slope, but every bounce reaches the
    # same peak, so the ball would return to its original height.  Same slope is
    # the point: the error is the equal peaks, not curvature.
    pd = [(130, 225), (165, 259), (165, 191), (235, 259), (235, 191), (270, 225)]

    # ---- E: straight sections of the same slope, each bounce smaller.  The
    # troughs and peaks halve in turn, and the durations shrink with them.
    pe = [(320, 225), (376, 259), (376, 208), (432, 242), (432, 216.5), (460, 233.5)]

    P = [
        (20, 26, 160, 110, 'A', pa, BLUE, None),
        (205, 26, 160, 110, 'B', None, RED, b_curve),
        (390, 26, 160, 110, 'C', pc, AMBER, None),
        (120, 170, 160, 110, 'D', pd, GREEN, None),
        (310, 170, 160, 110, 'E', pe, PURPLE, None),
    ]
    for (x0, y0, w, h, letter, pts, colour, extra) in P:
        b += _panel(x0, y0, w, h, letter, pts, colour, extra)
    b.append(T(W / 2.0, 330, 'downward is negative', 11.5, 'middle', GREY))
    return svg(W, H, 'Five candidate graphs of velocity against time for a ball released '
               'from rest, bouncing on the floor and rising lower each time. In every '
               'panel the time axis runs through the middle, so the part of the motion '
               'below the axis is the ball falling. A shows a decaying zigzag that never '
               'goes below the axis. B shows the velocity growing ever more steeply. C '
               'shows the velocity rising to a positive peak and then falling to zero '
               'once. D shows straight sections with every bounce reaching the same '
               'peak. E shows straight sections with each bounce smaller than the one '
               'before.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-17  a block on a rough slope, pulled by a hanging mass
# ═════════════════════════════════════════════════════════════════════════════
def f_17():
    b = [mk('q17-ar')]
    # The slope is a true 3-4-5 triangle: base 200, height 150, so the drawn angle
    # really is the one the labels state (sin = 0.60, cos = 0.80, tan = 0.75).
    # The first draft drew a 26.6-degree slope under a label claiming 36.9 degrees.
    b.append(PG([(40, 190), (240, 190), (240, 40)], INK, 2, '#eef2f8'))
    for i in range(9):
        x = 40 + i * 25
        b.append(L(x, 190, x + 10, 198, GREY, 1.1))
    # the block, rotated so it lies flat on the incline instead of cutting into it
    b.append(PG([(111.6, 136.3), (148.4, 108.7), (130.4, 84.7), (93.6, 112.3)],
                INK, 1.8, WALL))
    b.append(T(96, 78, '5.0 kg', 11.5, 'middle', INK))
    # the pulley at the top
    b.append(CI(252, 36, 9, INK, 2))
    b.append(T(252, 16, 'smooth pulley', 11, 'middle', GREY))
    # string: parallel to the slope, then vertically down to the hanging mass
    b.append(L(148.4, 108.7, 247, 40, AMBER, 1.8))
    b.append(L(261, 42, 261, 148, AMBER, 1.8))
    b.append(RC(245, 148, 32, 34, WALL, INK, 1.8))
    b.append(T(261, 170, 'm', 12.5, 'middle', INK))
    b.append(T(286, 150, 'hangs', 11, 'start', GREY))
    b.append(T(286, 164, 'freely', 11, 'start', GREY))
    # friction, acting down the slope.  Drawn just down-slope of the block rather than
    # from its contact point: collinear with the block's own base edge it read as part
    # of the block instead of as a force.
    b.append(L(111.6, 136.3, 83.6, 157.3, RED, 2.2, ' marker-end="url(#q17-ar)"'))
    b.append(T(120, 166, 'friction', 11, 'middle', RED))
    # the slope angle as its sine and cosine -- the question never names the angle
    b.append(T(196, 172, 'sin \u03b8 = 0.60', 11, 'middle', GREY))
    b.append(T(196, 186, 'cos \u03b8 = 0.80', 11, 'middle', GREY))
    # the coefficient, under the slope surface where it belongs
    b.append(T(190, 116, '\u03bc = 0.50', 11.5, 'middle', GREY))
    return svg(400, 230, 'A block of mass 5.0 kilograms on a rough plane inclined at an '
               'angle with sine 0.60 and cosine 0.80, so the plane rises 3 units for '
               'every 4 along its base. A string runs up the slope over a smooth pulley '
               'at the top and hangs vertically with a mass m on its end. An arrow shows '
               'friction acting down the slope, opposing the impending motion up the '
               'slope.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-19  a stress-strain curve
# ═════════════════════════════════════════════════════════════════════════════
def f_19():
    b = [mk('q19-ar')]
    X0, Y0 = 70, 210
    X1, Y1 = 310, 40
    b.append(L(X0, Y0, X1 + 12, Y0, INK, 1.7, ' marker-end="url(#q19-ar)"'))
    b.append(L(X0, Y0, X0, Y1 - 12, INK, 1.7, ' marker-end="url(#q19-ar)"'))
    b.append(T(X1 + 14, Y0 + 18, 'strain', 11.5, 'end', INK))
    b.append(T(58, Y1 - 4, 'stress', 11.5, 'end', INK))
    # the linear region, then a curve that bends over
    b.append(L(X0, Y0, 210, 92, BLUE, 2.4))
    b.append(PA('M210,92 Q250,74 320,66', BLUE, 2.4))
    b.append(CI(210, 92, 4, RED, 2, RED))
    b.append(T(206, 84, 'end of the straight region', 11, 'end', RED))
    # the shaded triangle whose area is the energy per unit volume.  The caption
    # goes OUTSIDE the triangle with a leader, because the hypotenuse is a diagonal
    # and any text laid over the interior is crossed by it at some length.
    b.append(PG([(X0, Y0), (210, 92), (210, Y0)], BLUE, 1.2, '#dfe8f6'))
    b.append(L(212, 194, 224, 180, BLUE, 1.1))
    b.append(T(228, 168, 'this shaded area is the', 11, 'start', BLUE))
    b.append(T(228, 182, 'energy per unit volume', 11, 'start', BLUE))
    b.append(T(150, 234, 'the gradient is Young\u2019s modulus', 11, 'middle', GREY))
    return svg(400, 250, 'A stress-strain curve for a metal. The straight-line region '
               'runs from the origin to a point marked at a stress of 3.0 times 10 to '
               'the 8 pascals and a strain of 1.5 times 10 to the minus 3. The area of '
               'the triangle beneath that line is the strain energy per unit volume.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-20  a diffraction grating and its orders
# ═════════════════════════════════════════════════════════════════════════════
def f_20():
    b = [mk('q20-ar')]
    # the grating, drawn as a row of slits
    b.append(L(50, 150, 380, 150, INK, 2.4))
    for x in range(60, 380, 24):
        b.append(L(x, 144, x, 156, '#ffffff', 3))
    # the grating label goes to the LEFT of the beam, anchored on its right edge,
    # so the incoming ray does not run through it
    b.append(T(205, 138, 'grating: 500 lines/mm', 11, 'end', GREY))
    # the incoming beam
    b.append(L(215, 20, 215, 142, RED, 2.4, ' marker-end="url(#q20-ar)"'))
    b.append(T(215, 12, '600 nm, normal incidence', 11, 'middle', RED))
    # the undeviated beam and the three diffracted orders
    b.append(L(215, 158, 215, 220, GREY, 1.6))
    b.append(T(215, 234, 'n = 0', 11, 'middle', GREY))
    for n, (dx, dy) in ((1, (78, 58)), (2, (112, 42)), (3, (146, 28))):
        b.append(L(215, 158, 215 + dx, 158 + dy, BLUE, 1.8,
                   ' marker-end="url(#q20-ar)"'))
        b.append(T(215 + dx + 6, 158 + dy + 12, 'n = %d' % n, 11, 'start', BLUE))
    # the reason there is no fourth order, set clear of the grey zero-order line
    b.append(T(50, 250, 'no order beyond n = 3:', 11, 'start', GREY))
    b.append(T(50, 264, 'it would need sin \u03b8 above 1', 11, 'start', GREY))
    return svg(420, 276, 'A diffraction grating ruled with 500 lines per millimetre, '
               'illuminated at normal incidence by light of wavelength 600 nanometres. '
               'The undeviated zero order is shown, together with the first, second and '
               'third orders on one side. There is no fourth order, because it would '
               'require the sine of the diffraction angle to exceed one.', '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-21  an optical fibre: both boundaries
# ═════════════════════════════════════════════════════════════════════════════
def f_21():
    b = [mk('q21-ar')]
    # core between two cladding bands
    b.append(RC(60, 58, 300, 60, '#eaf1fc', INK, 1.6))
    b.append(RC(60, 34, 300, 24, '#e2e7f0'))
    b.append(RC(60, 118, 300, 22, '#e2e7f0'))
    b.append(L(60, 58, 360, 58, INK, 1.6))
    b.append(L(60, 118, 360, 118, INK, 1.6))
    b.append(T(210, 26, 'cladding  n\u2082 = 1.2', 11, 'middle', GREY))
    b.append(T(210, 156, 'cladding  n\u2082 = 1.2', 11, 'middle', GREY))
    # The core label sits low and left, under the launched ray rather than across
    # it.  The first draft put it where the reflection caption also wanted to be.
    b.append(T(66, 110, 'core  n\u2081 = 1.5', 11, 'start', GREY))
    # The ray obeys Snell's law at the end face and the critical angle at the walls.
    # Entry at theta-a with sin(theta-a) = 0.90 needs sin(theta-r) = 0.90 / 1.5 = 0.60,
    # so the ray inside makes 36.9 degrees with the axis -- slope 0.75.  It then meets
    # each wall at 53.1 degrees to the normal, which is exactly the critical angle for
    # 1.5 against 1.2.  A shallower ray (the first draft) does not satisfy Snell.
    b.append(L(30, 30, 60, 96, RED, 2.2, ' marker-end="url(#q21-ar)"'))
    b.append(L(60, 96, 109.7, 58, BLUE, 2.2))
    b.append(L(109.7, 58, 188.1, 118, BLUE, 2.2))
    b.append(L(188.1, 118, 266.5, 58, BLUE, 2.2))
    b.append(L(266.5, 58, 344.9, 118, BLUE, 2.2))
    # the acceptance angle, drawn at a radius that clears the ray's own arrowhead --
    # at r = 10 the arc sat entirely inside the arrowhead and was invisible
    b.append(ARC(60, 96, 20, 180, 245.6, RED, 1.3))
    b.append(T(36, 74, '\u03b8\u2090', 12, 'end', RED))
    b.append(L(44, 96, 60, 96, GREY, 1.3, ' stroke-dasharray="4 4"'))
    b.append(T(34, 92, 'axis', 10.5, 'end', GREY))
    # the bounce points
    b.append(CI(109.7, 58, 3.2, RED, 1.5, RED))
    b.append(CI(188.1, 118, 3.2, RED, 1.5, RED))
    b.append(T(210, 178, 'the ray is totally internally reflected at both walls',
               11, 'middle', BLUE))
    return svg(420, 196, 'A step-index optical fibre. A ray enters the flat end face from '
               'air at an angle theta-a to the fibre axis, is refracted into the core of '
               'refractive index 1.5, and then strikes the boundary with the cladding of '
               'refractive index 1.2 at more than the critical angle, so it is totally '
               'internally reflected at each wall and guided along the fibre.',
               '\n'.join(b))


# ═════════════════════════════════════════════════════════════════════════════
# s01-24  a bubble rising through a lake
# ═════════════════════════════════════════════════════════════════════════════
def f_24():
    b = [mk('q24-ar')]
    # the lake, seen from the side
    b.append(RC(40, 60, 240, 150, '#e8f1fb'))
    b.append(L(40, 60, 280, 60, BLUE, 2))
    b.append(L(40, 60, 40, 210, INK, 2))
    b.append(L(280, 60, 280, 210, INK, 2))
    b.append(L(40, 210, 280, 210, INK, 2.4))
    for i in range(14):
        x = 44 + i * 17
        b.append(L(x, 210, x + 10, 218, GREY, 1.1))
    b.append(T(160, 48, 'surface', 11.5, 'middle', BLUE))
    # the two bubbles
    b.append(CI(150, 192, 5, RED, 1.8, '#fbeceb'))
    b.append(CI(150, 84, 8.5, RED, 1.8, '#fbeceb'))
    b.append(T(166, 196, '1.0 cm\u00b3', 11, 'start', RED))
    b.append(T(166, 88, '3.0 cm\u00b3', 11, 'start', RED))
    # the depth marker
    b.append(L(96, 192, 96, 60, GREY, 1.4, ' stroke-dasharray="5 4"'))
    b.append(L(90, 192, 102, 192, GREY, 1.3))
    b.append(L(90, 60, 102, 60, GREY, 1.3))
    b.append(T(84, 130, '20 m', 11.5, 'end', GREY))
    b.append(T(160, 236, 'pressure at the bottom = atmosphere + \u03c1gh',
               11, 'middle', GREY))
    return svg(320, 250, 'A lake 20 metres deep. A bubble of volume 1.0 cubic centimetre '
               'is released at the bottom and rises to the surface, where its volume is '
               '3.0 cubic centimetres. The pressure at the bottom is the atmospheric '
               'pressure plus the pressure of the water above.', '\n'.join(b))


# Figure key convention: 's<NN>-<QQ>' -- section, then the zero-padded question number.
# Four of these used to be written 's01-q02' / 's01-q16' while the other eleven were
# 's01-08' / 's01-15'.  Both sides agreed, so nothing was broken, but two naming schemes
# in one interface is how a missing figure happens at section 20.  One scheme now.


FIGS = {
    's01-02': f_02, 's01-04': f_04, 's01-07': f_07, 's01-08': f_08,
    's01-10': f_10, 's01-11': f_11, 's01-12': f_12, 's01-14': f_14,
    's01-15': f_15, 's01-16': f_16, 's01-17': f_17, 's01-19': f_19,
    's01-20': f_20, 's01-21': f_21, 's01-24': f_24,
}
