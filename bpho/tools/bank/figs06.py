# -*- coding: utf-8 -*-
"""Hand-authored SVG figures for drill-bank section 6.

House rule: a figure must encode the DISCRIMINATOR the question turns on, not decorate
the apparatus.  Each function says below which discriminator it encodes.

Marker ids are prefixed with the figure key because HTML has no id namespace -- two
figures both defining id="ar" collide and one silently gets the other's arrowhead.
"""
from svgkit import *


def _dim(x1, y1, x2, y2, c=GREY, sw=1.1, tick=5):
    """A dimension line with a tick across each end."""
    return (L(x1, y1, x2, y2, c, sw)
            + L(x1 - tick, y1, x1 + tick, y1, c, sw)
            + L(x2 - tick, y2, x2 + tick, y2, c, sw))


# ── 01 ───────────────────────────────────────────────────────────────────────
def f_01():
    """A real voltmeter has a finite resistance, so connecting it CHANGES the divider.

    The discriminator is the loading: the reading is 7.2 V, not the unloaded 8.0 V.
    The voltmeter is therefore drawn as a component in parallel with the 8 ohm, not as
    an ideal probe floating beside it.
    """
    b = []
    b.append(L(90, 70, 500, 70, INK, 2.0))
    b.append(L(90, 240, 500, 240, INK, 2.0))
    # The right-hand rail is deliberately well clear of the voltmeter's tap.  At 30 px
    # apart the tap read as if it met the corner of the loop, which would put the
    # voltmeter across the whole supply instead of across the 8 ohm.
    b.append(L(500, 70, 500, 240, INK, 2.0))
    b.append(L(90, 70, 90, 146, INK, 2.0))
    b.append(L(90, 160, 90, 240, INK, 2.0))
    b.append(L(76, 146, 104, 146, INK, 2.4))
    b.append(L(84, 160, 96, 160, INK, 4.5))
    b.append(T(112, 158, '12 V', 11.5, 'start', INK, 'bold'))
    b.append(RC(170, 58, 70, 24, '#ffffff', INK, 1.6))
    b.append(T(205, 50, '4.0 &#937;', 11.5, 'middle', INK, 'bold'))
    b.append(RC(340, 58, 70, 24, '#ffffff', INK, 1.6))
    b.append(T(375, 50, '8.0 &#937;', 11.5, 'middle', INK, 'bold'))
    # the voltmeter, tapped across the 8 ohm
    b.append(L(310, 70, 310, 150, INK, 2.0))
    b.append(L(310, 150, 358, 150, INK, 2.0))
    b.append(L(402, 150, 440, 150, INK, 2.0))
    b.append(L(440, 150, 440, 70, INK, 2.0))
    b.append(CI(380, 150, 22, INK, 1.8, '#ffffff'))
    b.append(T(380, 156, 'V', 12.5, 'middle', INK, 'bold'))
    b.append(CI(310, 70, 3.6, INK, 0, INK))
    b.append(CI(440, 70, 3.6, INK, 0, INK))
    return svg(560, 290, 'A 12 volt cell in series with a 4.0 ohm and an 8.0 ohm resistor, '
               'with a voltmeter connected in parallel across the 8.0 ohm resistor',
               ''.join(b))


# ── 03 ───────────────────────────────────────────────────────────────────────
def f_03():
    """A block pulled UP a rough slope: friction therefore acts DOWN the slope.

    The discriminator is the DIRECTION of the friction arrow.  A student who draws it up
    the slope (as if the block were sliding down) subtracts instead of adding and gets a
    different answer, so the figure must settle the direction without ambiguity.
    """
    b = [mk('s0603rd', RED), mk('s0603bl', BLUE),
         mk('s0603gr', GREEN), mk('s0603am', AMBER)]
    b.append(PG([(110, 250), (420, 71), (420, 250)], 'none', 0, '#eef2f8'))
    b.append(L(70, 250, 500, 250, INK, 2.0))
    b.append(L(110, 250, 420, 71, INK, 2.0))
    b.append(L(420, 71, 420, 250, INK, 1.4))
    # the block, sitting ON the slope.  The centre must be offset by half the block's
    # height along the outward normal; centring it on the surface line makes the block
    # straddle the slope, with half of it buried in the plane.
    b.append(PG([(274.5, 124.9), (287.5, 147.5), (242.5, 173.5), (229.5, 150.9)],
                INK, 1.6, '#dfe8f6'))
    # the forces, from the block's centre
    b.append(L(258.5, 149.2, 258.5, 221, RED, 2.0, ' marker-end="url(#s0603rd)"'))
    b.append(L(258.5, 149.2, 223.5, 88.6, BLUE, 2.0, ' marker-end="url(#s0603bl)"'))
    b.append(L(258.5, 149.2, 206.5, 179.2, GREEN, 2.0, ' marker-end="url(#s0603gr)"'))
    b.append(L(258.5, 149.2, 314.8, 116.7, AMBER, 2.0, ' marker-end="url(#s0603am)"'))
    # the angle at the foot
    b.append(ARC(110, 250, 80, 0, -30, GREY, 1.2))
    b.append(T(168, 242, '30&#176;', 11.5, 'end', GREY, 'bold'))
    b.append(T(266, 195, 'W', 12, 'start', RED, 'bold'))
    b.append(T(215, 84, 'N', 12, 'end', BLUE, 'bold'))
    b.append(T(196, 168, 'f', 12, 'end', GREEN, 'bold'))
    b.append(T(296, 100, 'F', 12, 'middle', AMBER, 'bold'))
    return svg(560, 290, 'A block on a plane inclined at 30 degrees to the horizontal. The '
               'weight acts down, the normal reaction perpendicular to the plane, the '
               'friction down the slope, and the applied force F up the slope',
               ''.join(b))


# ── 06 ───────────────────────────────────────────────────────────────────────
def f_06():
    """Average velocity is total displacement over total time, NOT the peak speed.

    The three shaded regions make the discriminator visible: the two triangles each
    contribute half of the rectangle that would enclose them, so the area is 72 m, not
    96 m.  A student who reads the graph as three rectangles gets 8.0 m/s.
    """
    b = [mk('s0606ar', INK)]
    b.append(PG([(80, 250), (213.3, 70), (213.3, 250)], BLUE, 1.0, '#e6eefc'))
    b.append(PG([(213.3, 70), (413.3, 70), (413.3, 250), (213.3, 250)],
                AMBER, 1.0, '#fdf3e0'))
    b.append(PG([(413.3, 70), (480, 250), (413.3, 250)], BLUE, 1.0, '#e6eefc'))
    b.append(L(80, 250, 510, 250, INK, 2.0, ' marker-end="url(#s0606ar)"'))
    b.append(L(80, 250, 80, 40, INK, 2.0, ' marker-end="url(#s0606ar)"'))
    b.append(PL([(80, 250), (213.3, 70), (413.3, 70), (480, 250)], INK, 2.4))
    b.append(T(80, 268, '0', 11, 'middle', INK))
    b.append(T(213.3, 268, '4.0', 11, 'middle', INK))
    b.append(T(413.3, 268, '10', 11, 'middle', INK))
    b.append(T(480, 268, '12', 11, 'middle', INK))
    b.append(T(72, 74, '8.0', 11, 'end', INK))
    b.append(T(72, 254, '0', 11, 'end', INK))
    b.append(T(86, 34, 'velocity / m s<tspan font-size="9" dy="-4">-1</tspan>',
               11, 'start', INK))
    # The axis title goes on its own line.  Level with the tick labels it collided with
    # the final '12', printing as "12time / s".
    b.append(T(540, 288, 'time / s', 11, 'end', INK))
    b.append(T(313, 238, 'area = displacement', 11, 'middle', GREY))
    return svg(560, 300, 'A velocity-time graph rising linearly from zero to 8.0 metres per '
               'second in 4.0 seconds, constant at 8.0 for the next 6.0 seconds, then '
               'falling linearly to zero over the last 2.0 seconds', ''.join(b))


# ── 07 ───────────────────────────────────────────────────────────────────────
def f_07():
    """Equal masses, elastic, one at rest: the two final paths are PERPENDICULAR.

    The discriminator is that the two outgoing directions are not drawn at a measured
    angle -- they are dashed, and both are labelled theta, because theta is what the
    question asks the reader to find.  Drawing them at 45 degrees each would hand over
    the answer.
    """
    b = [mk('s0607ar', INK), mk('s0607gr', GREY)]
    b.append(L(60, 150, 180, 150, INK, 2.2, ' marker-end="url(#s0607ar)"'))
    b.append(T(120, 140, 'u', 12, 'middle', INK, 'bold'))
    b.append(CI(186, 150, 7, INK, 1.8, '#ffffff'))
    b.append(T(186, 180, 'at rest', 11, 'middle', GREY))
    b.append(L(193, 150, 340, 150, GREY, 1.0, ' stroke-dasharray="3 4"'))
    b.append(L(193, 150, 304.5, 49.6, GREY, 1.8,
               ' stroke-dasharray="6 4" marker-end="url(#s0607gr)"'))
    b.append(L(193, 150, 304.5, 250.4, GREY, 1.8,
               ' stroke-dasharray="6 4" marker-end="url(#s0607gr)"'))
    b.append(T(255, 124, '&#952;', 12, 'middle', GREY, 'bold'))
    b.append(T(255, 180, '&#952;', 12, 'middle', GREY, 'bold'))
    b.append(T(314, 44, 'v', 12, 'start', GREY, 'bold'))
    b.append(T(314, 256, 'v', 12, 'start', GREY, 'bold'))
    return svg(560, 290, 'A particle of mass m moving with speed u towards an identical '
               'particle at rest. Two dashed outgoing paths are drawn at equal angles '
               'theta to the original direction, one above and one below', ''.join(b))


# ── 09 ───────────────────────────────────────────────────────────────────────
def f_09():
    """Superposition is an algebraic sum of displacements, signs included.

    The discriminator is the SIGN: the pulses have opposite polarity, so at full overlap
    the displacement is 3.0 - 1.0 = 2.0 cm, not 4.0 cm and not zero.  The dashed line
    marks the fixed meeting point, which is what makes the overlap instant findable.
    """
    b = [mk('s0609bl', BLUE), mk('s0609am', AMBER)]
    b.append(L(50, 150, 510, 150, INK, 1.8))
    b.append(L(250, 70, 250, 200, GREY, 1.2, ' stroke-dasharray="4 4"'))
    b.append(T(250, 216, 'midpoint', 11, 'middle', GREY))
    b.append(PL([(90, 150), (90, 90), (170, 90), (170, 150)], BLUE, 2.2, '#e6eefc'))
    b.append(PL([(330, 150), (330, 170), (410, 170), (410, 150)], AMBER, 2.2, '#fdf3e0'))
    b.append(T(82, 96, 'P', 12, 'end', BLUE, 'bold'))
    b.append(T(130, 124, '+3.0 cm', 11, 'middle', BLUE))
    b.append(T(418, 170, 'Q', 12, 'start', AMBER, 'bold'))
    b.append(T(370, 192, '&#8722;1.0 cm', 11, 'middle', AMBER))
    b.append(L(95, 62, 150, 62, BLUE, 1.6, ' marker-end="url(#s0609bl)"'))
    b.append(L(405, 62, 350, 62, AMBER, 1.6, ' marker-end="url(#s0609am)"'))
    b.append(T(250, 50, 'each 2.0 m/s', 11, 'middle', GREY))
    return svg(560, 240, 'Two rectangular pulses on a string approaching each other. The '
               'left-hand pulse is 3.0 centimetres high and positive, the right-hand one '
               'is 1.0 centimetre deep and negative, and the midpoint between them is '
               'marked with a dashed line', ''.join(b))


# ── 10 ───────────────────────────────────────────────────────────────────────
def f_10():
    """Snell's law relates SINES, not angles.

    The discriminator is that the 60 degree angle and the 30 degree angle are both drawn
    from the NORMAL, not from the surface.  A student who measures from the surface reads
    30 degrees and 60 degrees and reaches a different answer.
    """
    b = [mk('s0610bl', BLUE), mk('s0610rd', RED)]
    b.append(RC(60, 160, 440, 110, '#eef3fa', 'none', 0))
    b.append(L(60, 160, 500, 160, INK, 2.2))
    b.append(L(260, 50, 260, 275, GREY, 1.2, ' stroke-dasharray="5 4"'))
    b.append(L(130.1, 85, 260, 160, BLUE, 2.2, ' marker-end="url(#s0610bl)"'))
    b.append(L(260, 160, 315, 255.3, RED, 2.2, ' marker-end="url(#s0610rd)"'))
    b.append(ARC(260, 160, 70, 270, 210, GREY, 1.2))
    b.append(ARC(260, 160, 70, 90, 60, GREY, 1.2))
    b.append(T(212, 86, '60&#176;', 11.5, 'end', GREY, 'bold'))
    b.append(T(280, 250, '30&#176;', 11.5, 'start', GREY, 'bold'))
    b.append(T(90, 145, 'air', 11, 'start', GREY))
    b.append(T(90, 190, 'glass', 11, 'start', GREY))
    b.append(T(266, 62, 'normal', 11, 'start', GREY))
    b.append(T(490, 205, 'refractive index &#8730;3', 11, 'end', GREY))
    return svg(560, 300, 'A ray of light in air meeting the flat surface of a glass block at '
               '60 degrees to the normal and continuing into the glass at 30 degrees to '
               'the normal. The glass has refractive index root three', ''.join(b))


# ── 14 ───────────────────────────────────────────────────────────────────────
def f_14():
    """Relative velocity is a VECTOR difference, so the magnitudes do not simply add.

    The discriminator is the closed triangle: the dashed side shows that 15 east and 20
    north are perpendicular legs, so the relative velocity is the hypotenuse, 25 m/s.
    The right-angle marker at the origin is what stops the reader adding 15 and 20.
    """
    b = [mk('s0614bl', BLUE), mk('s0614gr', GREEN), mk('s0614rd', RED)]
    b.append(PG([(180, 150), (192, 150), (192, 138), (180, 138)], GREY, 1.2, 'none'))
    b.append(L(180, 150, 255, 150, BLUE, 2.2, ' marker-end="url(#s0614bl)"'))
    b.append(L(180, 150, 180, 50, GREEN, 2.2, ' marker-end="url(#s0614gr)"'))
    b.append(L(255, 150, 255, 250, GREY, 1.0, ' stroke-dasharray="4 4"'))
    b.append(L(180, 150, 255, 250, RED, 2.2, ' marker-end="url(#s0614rd)"'))
    b.append(T(262, 146, 'A: 15 m/s east', 11.5, 'start', BLUE, 'bold'))
    b.append(T(186, 42, 'B: 20 m/s north', 11.5, 'start', GREEN, 'bold'))
    b.append(T(262, 258, 'A relative to B', 11.5, 'start', RED, 'bold'))
    return svg(560, 300, 'A velocity triangle. One arrow points east with magnitude 15 '
               'metres per second, one points north with magnitude 20 metres per second, '
               'and the third, drawn from the same origin, is their vector difference',
               ''.join(b))


# ── 16 ───────────────────────────────────────────────────────────────────────
def f_16():
    """On a flat circular track the centripetal force is supplied entirely by friction.

    The discriminator is that the friction arrow is RADIAL, pointing at the centre -- not
    tangential.  A student who draws it along the direction of travel has no centripetal
    force at all and cannot set up the equation.
    """
    b = [mk('s0616gr', GREEN)]
    b.append(CI(280, 150, 100, GREY, 1.6, 'none'))
    b.append(CI(280, 150, 4, INK, 0, INK))
    b.append(RC(266, 42, 28, 14, '#ffffff', INK, 1.6))
    b.append(T(280, 34, 'car', 11, 'middle', INK))
    b.append(L(280, 110, 280, 150, GREY, 1.2, ' stroke-dasharray="4 4"'))
    b.append(T(272, 134, 'R', 12, 'end', GREY, 'bold'))
    b.append(L(280, 58, 280, 100, GREEN, 2.2, ' marker-end="url(#s0616gr)"'))
    b.append(T(288, 84, 'f', 12, 'start', GREEN, 'bold'))
    b.append(T(280, 272, 'track, radius R', 11, 'middle', GREY))
    return svg(560, 300, 'A plan view of a car on a circular track of radius R. The friction '
               'force on the car is drawn along the radius, pointing towards the centre '
               'of the circle', ''.join(b))


# ── 19 ───────────────────────────────────────────────────────────────────────
def f_19():
    """Apparent depth is the REAL depth divided by the refractive index, not multiplied.

    The discriminator is that the apparent image sits ABOVE the object, between the
    object and the surface.  A student who expects a magnified pool puts it below and
    reaches 2.7 m instead of 1.5 m.
    """
    b = [mk('s0619am', AMBER), mk('s0619rd', RED)]
    b.append(RC(60, 120, 440, 160, '#e8f1fa', 'none', 0))
    b.append(L(60, 120, 500, 120, INK, 2.2))
    b.append(L(290, 40, 290, 180, GREY, 1.1, ' stroke-dasharray="4 4"'))
    b.append(L(250, 260, 250, 50, GREY, 1.1, ' stroke-dasharray="3 5"'))
    b.append(L(250, 260, 290, 120, AMBER, 2.2, ' marker-end="url(#s0619am)"'))
    b.append(L(290, 120, 321.5, 40, RED, 2.2, ' marker-end="url(#s0619rd)"'))
    b.append(L(290, 120, 250, 221.5, GREY, 1.4, ' stroke-dasharray="6 4"'))
    b.append(CI(250, 260, 5.5, INK, 1.8, '#ffffff'))
    b.append(CI(250, 221.5, 5.5, RED, 1.8, 'none'))
    b.append(T(258, 266, 'object', 11, 'start', INK))
    b.append(T(258, 226, 'apparent image', 11, 'start', RED))
    b.append(T(95, 100, 'air', 11, 'start', GREY))
    b.append(T(95, 150, 'water', 11, 'start', GREY))
    return svg(560, 300, 'An object at the bottom of a pool, a ray travelling up to the '
               'surface and refracting away from the normal, and the backward extension '
               'of that ray meeting the vertical sight line at the apparent image, which '
               'is above the real object', ''.join(b))


# ── 20 ───────────────────────────────────────────────────────────────────────
def f_20():
    """Two resistors in parallel are NOT added, and the supply does not divide evenly.

    The discriminator is the topology: the 6 ohm and the 2 ohm are on separate branches
    between the same two nodes, while the 3 ohm is in series with the whole pair.  The
    junction dots mark the nodes, so "which two are in parallel" is unambiguous.
    """
    b = []
    b.append(L(80, 80, 420, 80, INK, 2.0))
    b.append(L(80, 220, 420, 220, INK, 2.0))
    b.append(L(80, 80, 80, 143, INK, 2.0))
    b.append(L(80, 157, 80, 220, INK, 2.0))
    b.append(L(66, 143, 94, 143, INK, 2.4))
    b.append(L(74, 157, 86, 157, INK, 4.5))
    b.append(T(100, 154, '6.0 V', 11.5, 'start', INK, 'bold'))
    b.append(RC(150, 68, 80, 24, '#ffffff', INK, 1.6))
    b.append(T(190, 60, '3.0 &#937;', 11.5, 'middle', INK, 'bold'))
    b.append(L(320, 80, 320, 128, INK, 2.0))
    b.append(RC(308, 128, 24, 64, '#ffffff', INK, 1.6))
    b.append(L(320, 192, 320, 220, INK, 2.0))
    b.append(T(300, 164, '6.0 &#937;', 11.5, 'end', INK, 'bold'))
    b.append(L(420, 80, 420, 128, INK, 2.0))
    b.append(RC(408, 128, 24, 64, '#ffffff', INK, 1.6))
    b.append(L(420, 192, 420, 220, INK, 2.0))
    b.append(T(400, 164, '2.0 &#937;', 11.5, 'end', INK, 'bold'))
    b.append(CI(320, 80, 4, INK, 0, INK))
    b.append(CI(320, 220, 4, INK, 0, INK))
    return svg(560, 290, 'A 6.0 volt cell connected to a 3.0 ohm resistor in series with a '
               'parallel pair made of a 6.0 ohm and a 2.0 ohm resistor', ''.join(b))


# ── 22 ───────────────────────────────────────────────────────────────────────
def f_22():
    """A plateau on a heating curve means energy is going into latent heat, not into
    raising the temperature.

    The discriminator is the RATIO of the two times: the melting plateau is longer than
    the warming stage, so the latent heat is larger than mc times the temperature rise.
    The shaded band and the marked 6.0 min make that comparison readable off the figure.
    """
    b = [mk('s0622ar', INK)]
    b.append(PG([(206.7, 90), (396.7, 90), (396.7, 112), (206.7, 112)],
                'none', 0, '#fdf3e0'))
    b.append(L(80, 250, 510, 250, INK, 2.0, ' marker-end="url(#s0622ar)"'))
    b.append(L(80, 250, 80, 50, INK, 2.0, ' marker-end="url(#s0622ar)"'))
    b.append(PL([(80, 210), (206.7, 90), (396.7, 90), (460, 70)], INK, 2.4))
    b.append(T(80, 268, '0', 11, 'middle', INK))
    b.append(T(206.7, 268, '4.0', 11, 'middle', INK))
    b.append(T(396.7, 268, '10', 11, 'middle', INK))
    b.append(T(460, 268, '12', 11, 'middle', INK))
    b.append(T(72, 214, '20', 11, 'end', INK))
    b.append(T(72, 94, '80', 11, 'end', INK))
    b.append(T(86, 44, 'temperature / &#176;C', 11, 'start', INK))
    # own line, for the same reason as s06-06
    b.append(T(540, 288, 'time / min', 11, 'end', INK))
    b.append(T(130, 236, 'solid', 11, 'middle', GREY))
    b.append(T(301, 80, 'melting', 11, 'middle', AMBER, 'bold'))
    b.append(T(434, 152, 'liquid', 11, 'middle', GREY))
    b.append(L(206.7, 290, 396.7, 290, AMBER, 1.4))
    b.append(L(206.7, 285, 206.7, 295, AMBER, 1.4))
    b.append(L(396.7, 285, 396.7, 295, AMBER, 1.4))
    b.append(T(301, 310, '6.0 min', 11, 'middle', AMBER, 'bold'))
    return svg(560, 322, 'A heating curve. The temperature of a solid rises from 20 to 80 '
               'degrees Celsius in 4.0 minutes, stays at 80 for 6.0 minutes while the '
               'solid melts, and then rises again', ''.join(b))


# ── 25 ───────────────────────────────────────────────────────────────────────
def f_25():
    """A floating body displaces its own weight, so the SUBMERGED fraction equals the
    ratio of the densities.

    The discriminator is which fraction is submerged: the figure marks the 0.60 V below
    the surface and the 0.40 V above it, so a student who reads the wrong one gets
    400 kg/m3 instead of 600.
    """
    b = []
    b.append(RC(60, 140, 440, 120, '#e8f1fa', 'none', 0))
    b.append(L(60, 140, 500, 140, INK, 2.2))
    b.append(RC(200, 100, 160, 40, '#ffffff', 'none', 0))
    b.append(RC(200, 140, 160, 60, '#dfe8f6', 'none', 0))
    b.append(RC(200, 100, 160, 100, 'none', INK, 2.0))
    b.append(_dim(380, 100, 380, 140))
    b.append(T(392, 124, '0.40 V', 11, 'start', GREY))
    b.append(_dim(380, 140, 380, 200, BLUE, 1.2))
    b.append(T(392, 174, '0.60 V', 11, 'start', BLUE))
    b.append(T(280, 126, 'wood', 11, 'middle', GREY))
    b.append(T(100, 180, 'water', 11, 'start', GREY))
    return svg(560, 280, 'A rectangular block of wood floating in water. The part below the '
               'surface is shaded and marked 0.60 V, and the part above is marked 0.40 V',
               ''.join(b))


FIGS = {
    's06-01': f_01,
    's06-03': f_03,
    's06-06': f_06,
    's06-07': f_07,
    's06-09': f_09,
    's06-10': f_10,
    's06-14': f_14,
    's06-16': f_16,
    's06-19': f_19,
    's06-20': f_20,
    's06-22': f_22,
    's06-25': f_25,
}
