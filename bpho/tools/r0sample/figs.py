# -*- coding: utf-8 -*-
"""Figures for the 2025 Round 0 SAMPLE questions (S1..S12).

Every coordinate below was MEASURED off the printed PDF with pypdfium2 -- vector
path extraction for the strokes, per-character boxes for the text -- so nothing
is traced by eye. The five theta_c sketches are the printed polylines scaled 1:1;
the circuit, the sheet-on-rods, the springs and the chain are rebuilt from the
measured coordinates of each wire, plate, rod, coil and block.

Two traps this file already fell into, both worth remembering:

1. The bodies are written in RAW PDF coordinates, so the viewBox has to be built
   by wrapping the body in a translate() group. Declaring a hand-guessed viewBox
   (0 0 206 100) while the strokes sit at x = 231..381 renders a completely EMPTY
   picture -- and an empty picture looks exactly like a correct one until you
   rasterise it.
2. An SVG that is going to be an <img>, or validated as XML, needs an explicit
   xmlns. Without it the browser renders it inline but every XML parser rejects it.

Because this model cannot read images, each figure is verified by rasterising the
printed page (tools/r0sample/verify_figs.py) or the emitted SVG to coarse ASCII.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig')

INK = '#14181f'
GREY = '#7b8494'
BLUE = '#2f5fd0'
RED = '#b3352f'
FILL = '#e8eefc'
FILL2 = '#fdf1e7'


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------


def svg(x0, y0, x1, y1, label, body, extra=''):
    """Wrap `body` (raw PDF coordinates) in a viewBox that actually contains it."""
    w, h = x1 - x0, y1 - y0
    return ('<figure class="fig">\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" role="img" '
            'aria-label="%s">\n'
            '<g transform="translate(%g,%g)">\n%s\n%s\n</g>\n</svg>\n</figure>'
            % (w, h, label, -x0, -y0, extra, body))


def arrow_defs(prefix, color=INK):
    return ('<defs>\n'
            '<marker id="%s-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" '
            'orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="%s"/></marker>\n'
            '</defs>' % (prefix, color))


def txt(x, y, s, size=12, anchor='start', color=INK, weight='', style=''):
    a = ' text-anchor="%s"' % anchor if anchor != 'start' else ''
    w = ' font-weight="%s"' % weight if weight else ''
    st = ' %s' % style if style else ''
    return ('<text x="%g" y="%g" font-size="%g"%s fill="%s"%s%s>%s</text>'
            % (x, y, size, a, color, w, st, s))


def sub_label(x, y, main, sub, size=12, anchor='middle', color=INK):
    """T with a real subscript, built from two tspans (no font dependency)."""
    return ('<text x="%g" y="%g" font-size="%g" text-anchor="%s" fill="%s">%s'
            '<tspan font-size="%g" dy="%g">%s</tspan></text>'
            % (x, y, size, anchor, color, main, size * 0.72, size * 0.26, sub))


def frac(cx, cy, num, den, size=11, color=INK, bar=13):
    """A stacked fraction: numerator, rule, denominator, centred on (cx, cy)."""
    return ('<text x="%g" y="%g" font-size="%g" text-anchor="middle" fill="%s">%s</text>\n'
            '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1"/>\n'
            '<text x="%g" y="%g" font-size="%g" text-anchor="middle" fill="%s">%s</text>'
            % (cx, cy - 2.5, size, color, num,
               cx - bar / 2, cy, cx + bar / 2, cy, color,
               cx, cy + size - 1.5, size, color, den))


# ============================================================================
# S3 — two cells and two resistors sharing a link
# ============================================================================
def fig_s3():
    """Measured off page 1. Top wire y=345.1, return wire y=420.1, outer branches
    at x=231 and x=381 each holding a 6.0 ohm box, a plain link at x=306, and the
    two cells sitting in the top wire.

    Polarity is the whole question, so it was read off the stroke lengths rather
    than assumed: at x=266.3 the plate is 15.0 long and at x=270.7 it is 7.5, and
    the same at 341.3 / 345.7. The LONG plate is the positive terminal, so BOTH
    cells have + on their left-hand side."""
    B = []
    B.append('<g stroke="%s" stroke-width="2" fill="none">' % INK)
    for seg in [(231, 345.1, 266.3, 345.1), (270.7, 345.1, 306, 345.1),
                (306, 345.1, 341.3, 345.1), (345.7, 345.1, 381, 345.1),   # top wire, split by the cells
                (231, 420.1, 381, 420.1),                                # return wire
                (306, 345.1, 306, 420.1)]:                               # the link
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g"/>' % seg)
    B.append('</g>')
    # cell plates: long = positive, short = negative
    B.append('<g stroke="%s" stroke-width="2.4">' % INK)
    B.append('<line x1="266.3" y1="337.6" x2="266.3" y2="352.6"/>')   # + (long)
    B.append('<line x1="270.7" y1="341.3" x2="270.7" y2="348.8"/>')   # - (short)
    B.append('<line x1="341.3" y1="337.6" x2="341.3" y2="352.6"/>')
    B.append('<line x1="345.7" y1="341.3" x2="345.7" y2="348.8"/>')
    B.append('</g>')
    # outer branches and their resistor boxes
    B.append('<g stroke="%s" stroke-width="2" fill="none">' % INK)
    for seg in [(231, 345.1, 231, 367.6), (231, 397.6, 231, 420.1),
                (381, 345.1, 381, 367.6), (381, 397.6, 381, 420.1)]:
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g"/>' % seg)
    B.append('</g>')
    B.append('<rect x="225" y="367.6" width="12" height="30" fill="%s" stroke="%s" stroke-width="2"/>' % (FILL, INK))
    B.append('<rect x="375" y="367.6" width="12" height="30" fill="%s" stroke="%s" stroke-width="2"/>' % (FILL, INK))
    # junction dots where the link meets the two wires
    for (x, y) in [(306, 345.1), (306, 420.1)]:
        B.append('<circle cx="%g" cy="%g" r="2.6" fill="%s"/>' % (x, y, INK))
    # current arrow in the link; the printed arrowhead points DOWN
    B.append('<line x1="306" y1="392" x2="306" y2="409" stroke="%s" stroke-width="2" marker-end="url(#s3-ar)"/>' % RED)
    # labels, all placed from the measured character boxes
    B.append(txt(269.1, 330.8, '3.0 V', 11, 'middle'))
    B.append(txt(344.8, 330.8, '6.0 V', 11, 'middle'))
    B.append(txt(216.7, 385.6, '6.0 &#937;', 11, 'end'))
    B.append(txt(393.6, 385.6, '6.0 &#937;', 11, 'start'))
    B.append(txt(307.9, 390.3, 'I', 12, 'start', RED, 'bold'))
    body = '\n'.join(B)
    return svg(182, 316, 428, 432,
               'A circuit: a 3.0 volt cell in series with a 6.0 volt cell along the top wire, '
               'both with their long positive plate on the left, two 6.0 ohm resistors in the '
               'outer branches, and a plain wire linking the junction between the two cells to '
               'the return wire. The current I flows down that link.',
               body, arrow_defs('s3', RED))


# ============================================================================
# S7 — equilateral sheet carried on three rods
# ============================================================================
def fig_s7():
    """Measured off page 2. The sheet's outline is one closed path that starts at
    (306,246) -- which is the midpoint of the edge joining (235,274) and (377,217),
    i.e. exactly where the extra load sits. The three rods are 28.3 units long and
    hang from the corners; the printed arrows point up the page (the reactions).
    The two rods at the ends of the loaded edge are labelled R and the third N."""
    V1, V2, V3 = (235, 274), (377, 217), (349, 303)
    M = ((V1[0] + V2[0]) / 2.0, (V1[1] + V2[1]) / 2.0)      # (306, 245.5) -- printed marker is (306,246)
    B = []
    B.append('<polygon points="%g,%g %g,%g %g,%g" fill="%s" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round"/>'
             % (V1[0], V1[1], V2[0], V2[1], V3[0], V3[1], FILL, INK))
    # rods, hanging from each corner
    B.append('<g stroke="%s" stroke-width="2">' % INK)
    for (x, y0) in [V1, V2, V3]:
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g"/>' % (x, y0, x, y0 + 28.3))
    B.append('</g>')
    # reaction arrows, pointing back up the rods
    for (x, y0) in [V1, V2, V3]:
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="2" '
                 'marker-end="url(#s7-ar)"/>' % (x, y0 + 28.3, x, y0 + 14, BLUE))
    # the added weight: the printed figure marks it with a ring and no label
    B.append('<circle cx="%g" cy="%g" r="4.6" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (M[0], M[1], FILL2, RED))
    B.append(txt(381.4, 235.9, 'R', 12, 'start', BLUE, 'bold'))
    B.append(txt(239.7, 289.8, 'R', 12, 'start', BLUE, 'bold'))
    B.append(txt(352.3, 318.1, 'N', 12, 'start', BLUE, 'bold'))
    body = '\n'.join(B)
    return svg(228, 208, 398, 340,
               'A triangular metal sheet seen at an angle, supported at each corner by a rod of equal '
               'length, with the reaction arrows drawn pointing up the rods. The two corners on the '
               'left and the upper right are labelled R and the lower right corner is labelled N. An '
               'unlabelled ring marks the extra load, sitting at the midpoint of the edge that joins '
               'the two R corners.',
               body, arrow_defs('s7', BLUE))


# ============================================================================
# S8 — the five critical-angle sketches
# ============================================================================
# Printed polylines, 1:1 from the page. The steep opening stroke of A, C and E is a
# separate vertical path object, listed in S8_STEM -- it is the n = 1 asymptote.
S8_STEM = {
    "A": (125.6, 552.1, 492.9),
    "C": (462.6, 552.1, 492.9),
    "E": (378.4, 694.8, 635.5),
}
S8_CURVES = {
    "A": [(125.6, 492.9), (128.1, 495.3), (130.8, 498.0), (134.1, 501.3), (137.1, 504.3),
          (139.6, 506.8), (142.3, 509.5), (144.8, 512.0), (147.3, 514.5), (149.8, 517.0),
          (152.3, 519.5), (155.0, 522.2), (157.5, 524.7), (160.9, 528.1), (163.9, 531.1),
          (166.5, 533.7), (169.5, 536.7), (172.0, 539.2), (174.5, 541.7), (177.3, 544.5),
          (180.3, 547.5), (183.3, 550.5), (184.9, 552.1)],
    "B": [(246.7, 552.1), (249.3, 551.2), (251.8, 550.2), (254.4, 549.3), (257.0, 548.3),
          (259.8, 547.3), (262.3, 546.3), (264.9, 545.4), (267.7, 544.3), (270.2, 543.4),
          (272.8, 542.4), (276.9, 540.8), (279.4, 539.8), (282.0, 538.8), (284.6, 537.8),
          (287.1, 536.8), (289.9, 535.7), (292.7, 534.5), (295.3, 533.5), (297.8, 532.4),
          (300.4, 531.3), (303.0, 530.2), (305.7, 529.0), (308.5, 527.7), (311.7, 526.2),
          (314.3, 525.0), (316.9, 523.8), (319.4, 522.5), (322.0, 521.2), (325.2, 519.5),
          (327.8, 518.0), (330.3, 516.6), (332.9, 515.0), (335.7, 513.2), (338.2, 511.4),
          (340.8, 509.5), (343.4, 507.3), (345.9, 504.9), (348.5, 502.1), (351.1, 498.4),
          (353.4, 490.1)],
    "C": [(462.6, 492.9), (465.1, 492.9), (467.6, 493.1), (470.1, 493.3), (472.6, 493.7),
          (475.1, 494.2), (477.6, 494.8), (480.1, 495.5), (482.6, 496.3), (485.1, 497.3),
          (487.6, 498.4), (490.1, 499.6), (492.6, 501.0), (495.1, 502.5), (497.7, 504.3),
          (500.3, 506.4), (502.8, 508.5), (505.3, 511.0), (507.8, 513.7), (510.3, 516.9),
          (512.9, 520.7), (515.4, 525.1), (517.9, 530.6), (520.4, 538.7), (521.9, 552.1)],
    "D": [(162.5, 694.8), (165.0, 692.7), (167.6, 690.5), (170.4, 688.2), (172.9, 686.0),
          (175.5, 683.9), (178.1, 681.8), (180.9, 679.6), (184.1, 677.0), (186.6, 675.0),
          (189.6, 672.6), (193.3, 669.9), (196.0, 667.8), (198.6, 666.0), (201.4, 664.0),
          (204.0, 662.2), (206.5, 660.5), (209.1, 658.8), (211.7, 657.2), (214.2, 655.7),
          (216.8, 654.2), (219.4, 652.7), (222.6, 651.1), (225.1, 649.8), (227.7, 648.5),
          (230.3, 647.4), (233.3, 646.2), (235.8, 645.2), (238.4, 644.3), (241.0, 643.4),
          (243.5, 642.7), (246.1, 642.0), (248.9, 641.3), (251.4, 640.8), (254.6, 640.3),
          (257.4, 639.9), (260.2, 639.7), (262.8, 639.5), (265.3, 639.5), (267.9, 639.5),
          (269.2, 639.5)],
    "E": [(378.4, 632.7), (380.9, 646.4), (383.4, 651.6), (385.9, 655.3), (388.4, 658.3),
          (390.9, 660.7), (393.4, 662.7), (395.9, 664.5), (398.5, 666.2), (401.0, 667.5),
          (403.5, 668.8), (406.0, 669.9), (408.6, 671.0), (411.1, 671.9), (413.6, 672.8),
          (416.1, 673.6), (418.7, 674.3), (421.2, 675.0), (423.7, 675.6), (426.3, 676.3),
          (428.8, 676.8), (431.3, 677.3), (433.8, 677.8), (436.4, 678.3), (437.7, 678.5)],
}
# (x-axis x0, x1, baseline, y-axis top, letter x, letter baseline, theta x, n x)
S8_AXES = {
    "A": (78.2, 193.9, 552.1, 460.2, 141.5, 461.5, 81.8, 197.6),
    "B": (246.7, 362.4, 552.1, 460.2, 310.2, 461.5, 250.3, 366.1),
    "C": (415.2, 530.8, 552.1, 460.2, 478.5, 461.3, 418.8, 534.6),
    "D": (162.5, 278.1, 694.8, 602.9, 225.9, 604.1, 166.0, 281.8),
    "E": (331.0, 446.6, 694.8, 602.9, 394.5, 604.2, 334.5, 450.3),
}


def fig_s8():
    B = []
    for name in 'ABCDE':
        x0, x1, yb, yt, lx, ly, tx, nx = S8_AXES[name]
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#s8-ar)"/>' % (x0, yb, x1, yb, INK))
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#s8-ar)"/>' % (x0, yb, x0, yt, INK))
        pts = list(S8_CURVES[name])
        if name in S8_STEM:
            sx, sy1, sy2 = S8_STEM[name]
            B.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="2.2"/>'
                     % (sx, sy1, sx, sy2, BLUE))
        B.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>'
                 % (' '.join('%g,%g' % p for p in pts), BLUE))
        B.append(sub_label(lx, ly, name, '', 12, 'middle', INK))
        B.append('<text x="%g" y="%g" font-size="12" fill="%s">&#952;<tspan font-size="8.6" '
                 'dy="2.6">c</tspan></text>' % (tx, yt - 3.4, INK))
        B.append(txt(nx, yb - 2.2, 'n', 12))
    body = '\n'.join(B)
    return svg(70, 442, 546, 702,
               'Five candidate graphs of the critical angle theta sub c against refractive index n. '
               'A falls in a straight line to the axis; B rises and steepens; C runs almost flat and '
               'then plunges to the axis; D rises and levels off; E falls steeply at first and then '
               'flattens, never reaching the axis. A, C and E each begin with a vertical stroke, '
               'which marks n = 1.',
               body, arrow_defs('s8'))


# ============================================================================
# S9 — three springs, point P pushed out of the plane
# ============================================================================
def fig_s9():
    """Measured off page 3: P is at (306,192.3), A at (306,126.8), B at (249.3,225)
    and C at (362.7,225). Each of PA, PB, PC is 65.4 long and the three are 120
    degrees apart, which is what 'equidistant' in the stem means."""
    P, A, Bp, Cp = (306.0, 192.3), (306.0, 126.8), (249.3, 225.0), (362.7, 225.0)
    S = []

    def coil(p, q, n=9, amp=4.4):
        """a spring, drawn as a zig-zag between p and q"""
        (x0, y0), (x1, y1) = p, q
        dx, dy = x1 - x0, y1 - y0
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        pts = [(x0, y0)]
        for i in range(1, n):
            t = i / float(n)
            s = amp if i % 2 else -amp
            pts.append((x0 + dx * t + nx * s, y0 + dy * t + ny * s))
        pts.append((x1, y1))
        return 'M' + ' L'.join('%g,%g' % p for p in pts)

    for q in (A, Bp, Cp):
        S.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round"/>'
                 % (coil(P, q), INK))
    for q in (A, Bp, Cp, P):
        S.append('<circle cx="%g" cy="%g" r="2.8" fill="%s"/>' % (q[0], q[1], INK))
    S.append(txt(305.75, 122.2, 'A', 12, 'middle', INK, 'bold'))
    S.append(txt(240.65, 229.2, 'B', 12, 'middle', INK, 'bold'))
    S.append(txt(371.05, 229.3, 'C', 12, 'middle', INK, 'bold'))
    S.append(txt(298.75, 188.9, 'P', 12, 'middle', INK, 'bold'))
    body = '\n'.join(S)
    return svg(230, 108, 382, 238,
               'Point P joined to three fixed points A, B and C by three identical springs. A is '
               'directly above P, B is down and to the left and C is down and to the right, each the '
               'same distance from P and 120 degrees from its neighbours.',
               body)


# ============================================================================
# S12 — a chain of blocks with halving masses
# ============================================================================
def fig_s12():
    """Measured off page 3. Blocks at x = 207.2..234.7, 263.9..291.4 and 320.6..348.1,
    each 27.5 tall and sitting on a line at y = 671.8; the strings run at the blocks'
    mid-height, y = 657.7, and the pull D leaves the front block to the right.

    The printed figure gives the FRONT block (the one being pulled, on the right) the
    plain label m and backs the others with stacked fractions m/2 and m/4 -- so the
    mass halves as you move away from the pull, which is what the stem says."""
    B = []
    B.append('<line x1="178.4" y1="671.8" x2="405.2" y2="671.8" stroke="%s" stroke-width="1.6"/>' % INK)
    # strings, running at the blocks' mid-height
    B.append('<g stroke="%s" stroke-width="2">' % INK)
    for seg in [(178.4, 657.7, 206.8, 657.7), (235.1, 657.7, 263.5, 657.7),
                (291.8, 657.7, 320.2, 657.7)]:
        B.append('<line x1="%g" y1="%g" x2="%g" y2="%g"/>' % seg)
    B.append('</g>')
    # blocks
    for x, w in [(207.2, 27.5), (263.9, 27.5), (320.6, 27.5)]:
        B.append('<rect x="%g" y="643.9" width="%g" height="27.5" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (x, w, FILL, INK))
    # the pull
    B.append('<line x1="348.5" y1="657.7" x2="387.8" y2="657.7" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#s12-ar)"/>' % RED)
    B.append(txt(395.1, 661.8, 'D', 12, 'start', RED, 'bold'))
    # masses: front block is plain m, the ones behind it are m/2 and m/4
    B.append(frac(221.0, 657.2, 'm', '4'))
    B.append(frac(277.7, 657.2, 'm', '2'))
    B.append(txt(334.4, 660.4, 'm', 11, 'middle'))
    # tensions, labelled from the front
    B.append(sub_label(248.5, 646.7, 'T', '2', 11.5))
    B.append(sub_label(305.0, 646.7, 'T', '1', 11.5))
    body = '\n'.join(B)
    return svg(172, 634, 408, 678,
               'A chain of blocks on horizontal ground, pulled to the right by a force D. The front '
               'block has mass m, the block behind it has mass m over 2 and the one behind that has '
               'mass m over 4, with the chain continuing off to the left. T1 labels the string between '
               'the front block and the next one, and T2 the string behind that.',
               body, arrow_defs('s12', RED))


FIGS = {'r0s-03': fig_s3, 'r0s-07': fig_s7, 'r0s-08': fig_s8,
        'r0s-09': fig_s9, 'r0s-12': fig_s12}

if __name__ == '__main__':
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for key, fn in sorted(FIGS.items()):
        s = fn()
        open(os.path.join(OUT, key + '.svg'), 'w', encoding='utf-8').write(s)
        print('%-9s %6d bytes' % (key, len(s)))
    print('wrote', len(FIGS), 'figures to', OUT)
