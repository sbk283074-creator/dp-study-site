#!/usr/bin/env python3
"""BPhO Round 0 — 2025 past paper: inline SVG figures with computed geometry.

Every coordinate that depends on trigonometry is computed here rather than eyeballed,
so the drawn angle really is the angle the solution claims.
"""

import math

INK = "#14181f"
INK2 = "#4a5262"
INK3 = "#7b8494"
ACC = "#2f5fd0"
BAD = "#b3352f"
GOOD = "#1f7a53"
PUR = "#5b3fa8"
SOFT = "#e8eefc"
LINE = "#e2e6ed"
LINE2 = "#cbd2dd"
WHITE = "#ffffff"


def defs(prefix):
    return f"""<defs>
<marker id="{prefix}-ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="{INK}"/></marker>
<marker id="{prefix}-arA" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="{ACC}"/></marker>
<marker id="{prefix}-arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="{BAD}"/></marker>
<marker id="{prefix}-dim" markerWidth="8" markerHeight="8" refX="6.4" refY="2.8" orient="auto"><path d="M0,0 L6.4,2.8 L0,5.6 z" fill="{INK3}"/></marker>
<marker id="{prefix}-dimS" markerWidth="8" markerHeight="8" refX="0.6" refY="2.8" orient="auto"><path d="M6.4,0 L0,2.8 L6.4,5.6 z" fill="{INK3}"/></marker>
</defs>"""


def fig(svg_inner, viewbox, cap, aria):
    return (
        '<figure class="fig">\n'
        f'<svg viewBox="{viewbox}" role="img" aria-label="{aria}">\n'
        + svg_inner.strip()
        + "\n</svg>\n"
        + f"<figcaption>{cap}</figcaption>\n</figure>"
    )


def axes(prefix, y, x0, y0, x1, tip="t", tipy="j"):
    """Simple L-shaped axes with arrowheads; origin (x0, y0)."""
    return (
        f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{INK}" stroke-width="1.8" marker-end="url(#{prefix}-ar)"/>\n'
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y}" stroke="{INK}" stroke-width="1.8" marker-end="url(#{prefix}-ar)"/>\n'
        f'<text x="{x1-4}" y="{y0+18}" text-anchor="end" font-size="12" font-style="italic" fill="{INK2}">{tip}</text>\n'
        f'<text x="{x0-8}" y="{y+2}" text-anchor="end" font-size="12" font-style="italic" fill="{INK2}">{tipy}</text>'
    )


def rect_res(cx, cy, w, h):
    return f'<rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w}" height="{h}" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'


def dot(x, y, r=3.6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>'


# ----------------------------------------------------------------- Q1
def r0_01():
    """Force–extension triangle: the work done is the area."""
    p = "f1"
    x0, y0, xF, yF = 70, 196, 392, 62
    s = defs(p)
    s += f'\n<line x1="{x0}" y1="{y0}" x2="{xF}" y2="{y0}" stroke="{INK}" stroke-width="1.8" marker-end="url(#{p}-ar)"/>\n'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="34" stroke="{INK}" stroke-width="1.8" marker-end="url(#{p}-ar)"/>\n'
    s += f'<polygon points="{x0},{y0} {xF},{yF} {xF},{y0}" fill="{SOFT}" stroke="{ACC}" stroke-width="2.2"/>\n'
    s += f'<line x1="{x0}" y1="{yF}" x2="{xF}" y2="{yF}" stroke="{INK3}" stroke-width="1.4" stroke-dasharray="5 4"/>\n'
    s += f'<text x="{x0-8}" y="{yF+4}" text-anchor="end" font-size="12.5" font-weight="600" fill="{BAD}">σA</text>\n'
    s += f'<text x="{x0-8}" y="{y0+4}" text-anchor="end" font-size="12.5" fill="{INK3}">0</text>\n'
    s += f'<text x="{xF}" y="{y0+18}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{BAD}">εL</text>\n'
    s += f'<text x="{x0-8}" y="28" text-anchor="end" font-size="12" font-style="italic" fill="{INK2}">force</text>\n'
    s += f'<text x="{xF+8}" y="{y0+34}" text-anchor="end" font-size="12" font-style="italic" fill="{INK2}">extension</text>\n'
    s += f'<text x="{(x0+xF)/2:.0f}" y="{(y0+yF)/2+10:.0f}" text-anchor="middle" font-size="13" font-weight="600" fill="{ACC}">area = ½ · σA · εL</text>'
    return fig(s, "0 0 480 246",
               "<b>The force rises in step with the extension.</b> Because the wire behaves elastically, "
               "the force grows linearly from zero to <code>σA</code> as the extension grows from zero to "
               "<code>εL</code>, so the work done is the shaded triangle — not the rectangle you would get if "
               "the full force were applied throughout.",
               "A force against extension graph: a straight line from the origin up to the point where the force is sigma A and the extension is epsilon L, with the triangular area beneath it shaded.")


# ----------------------------------------------------------------- Q2
def r0_02():
    """Refraction, with both angles measured from the surface (as the paper draws them).

    Drawn for light passing from n1 = 1.5 (above) into n2 = 1.0 (below): entering the
    less dense medium the ray bends away from the normal, so the refracted ray is the
    steeper of the two - the same shape the paper's own diagram has. The relation
    n1 cos(theta1) = n2 cos(theta2) holds exactly for the angles actually drawn.
    """
    p = "f2"
    cx, cy = 240.0, 170.0
    n1, n2 = 1.5, 1.0
    th1 = math.radians(60.0)
    th2 = math.acos((n1 / n2) * math.cos(th1))
    L1, L2 = 124.0, 150.0
    ix, iy = cx - L1 * math.cos(th1), cy - L1 * math.sin(th1)
    rx, ry = cx + L2 * math.cos(th2), cy + L2 * math.sin(th2)
    R = 66.0
    s = defs(p)
    s += f'\n<line x1="40" y1="{cy}" x2="452" y2="{cy}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{cx}" y2="{cy}" stroke="{ACC}" stroke-width="2.6" marker-end="url(#{p}-arA)"/>\n'
    s += f'<line x1="{cx}" y1="{cy}" x2="{rx:.1f}" y2="{ry:.1f}" stroke="{ACC}" stroke-width="2.6" marker-end="url(#{p}-arA)"/>\n'
    s += f'<path d="M{cx-R:.1f},{cy} A{R},{R} 0 0 1 {cx-R*math.cos(th1):.1f},{cy-R*math.sin(th1):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    s += f'<path d="M{cx+R:.1f},{cy} A{R},{R} 0 0 0 {cx+R*math.cos(th2):.1f},{cy+R*math.sin(th2):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    lx = cx - 88 * math.cos(math.radians(32))
    ly = cy - 88 * math.sin(math.radians(32))
    s += f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="14" font-style="italic" font-weight="600" fill="{BAD}">\u03b8\u2081</text>\n'
    s += f'<text x="{cx+84:.0f}" y="{cy+52:.0f}" text-anchor="middle" font-size="14" font-style="italic" font-weight="600" fill="{BAD}">\u03b8\u2082</text>\n'
    s += f'<text x="118" y="{cy-16:.0f}" text-anchor="middle" font-size="13.5" font-style="italic" fill="{INK}">n\u2081</text>\n'
    s += f'<text x="118" y="{cy+28:.0f}" text-anchor="middle" font-size="13.5" font-style="italic" fill="{INK}">n\u2082</text>\n'
    s += f'<text x="300" y="{cy-14:.0f}" text-anchor="middle" font-size="11.5" fill="{INK3}">surface</text>'
    cap = ("<b>\u03b8\u2081 and \u03b8\u2082 are measured from the <i>surface</i>, not from the normal.</b> Drawn to scale "
           "for <code>n\u2081 = 1.5</code>, <code>n\u2082 = 1</code> and <code>\u03b8\u2081 = 60\u00b0</code>: the refracted ray sits at "
           f"<code>\u03b8\u2082 = {math.degrees(th2):.1f}\u00b0</code> to the surface, which is "
           f"<code>{90-math.degrees(th2):.1f}\u00b0</code> to the normal. Check it against Snell in the normal form: "
           f"<code>1.5 sin 30\u00b0 = 1 sin {90-math.degrees(th2):.1f}\u00b0 = 0.75</code> \u2014 which is exactly what "
           "<code>n\u2081 cos \u03b8\u2081 = n\u2082 cos \u03b8\u2082</code> asserts.")
    return fig(s, "0 0 480 300", cap,
               "A ray crossing a horizontal boundary between medium n1 above and n2 below, drawn with both angles marked between the ray and the boundary surface rather than between the ray and the normal.")


# ----------------------------------------------------------------- Q7
def r0_07():
    p = "f7"
    y = 62.0
    ax, bx = 90.0, 330.0
    s = defs(p)
    s += "\n"
    s += f'<line x1="{ax}" y1="{y}" x2="{ax+128}" y2="{y}" stroke="{INK}" stroke-width="2.4" marker-end="url(#{p}-ar)"/>\n'
    s += f'<line x1="{bx}" y1="{y}" x2="{bx+64}" y2="{y}" stroke="{INK}" stroke-width="2.4" marker-end="url(#{p}-ar)"/>\n'
    s += dot(ax, y) + "\n" + dot(bx, y)
    s += f'<text x="{ax+64}" y="{y-12}" text-anchor="middle" font-size="13" font-weight="600" fill="{INK}">A · 6 m s⁻¹</text>\n'
    s += f'<text x="{bx+40}" y="{y-12}" text-anchor="middle" font-size="13" font-weight="600" fill="{INK}">B · 3 m s⁻¹</text>\n'
    for xx in (ax, bx):
        s += f'<line x1="{xx}" y1="{y+6}" x2="{xx}" y2="{y+58}" stroke="{LINE2}" stroke-width="1.2" stroke-dasharray="4 4"/>\n'
    s += f'<line x1="{ax}" y1="{y+58}" x2="{bx}" y2="{y+58}" stroke="{INK3}" stroke-width="1.5" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<text x="{(ax+bx)/2}" y="{y+78}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{ACC}">initial separation 18 m</text>'
    return fig(s, "0 0 480 160",
               "<b>Read the arrows before you compute.</b> Both particles travel the same way, so the gap "
               "closes at <code>6 − 3 = 3 m s⁻¹</code>. If they were approaching each other the closing speed "
               "would be <code>9 m s⁻¹</code>, A would travel 12 m — and 12 m is not on the list.",
               "Two dots on a horizontal line, A moving right at six metres per second and B also moving right at three metres per second, with the eighteen metre gap between them marked by a dimension line.")


# ----------------------------------------------------------------- Q8
def r0_08():
    p = "f8"
    L, Rr, T, B, M = 70.0, 400.0, 60.0, 240.0, 140.0
    JM, JB = 250.0, 240.0
    s = defs(p)
    # outer wires
    s += f'\n<line x1="{L}" y1="{T}" x2="{L}" y2="{B}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="{Rr}" y1="{T}" x2="{Rr}" y2="{B}" stroke="{INK}" stroke-width="2"/>\n'
    # top branch: cell then resistor
    s += f'<line x1="{L}" y1="{T}" x2="150" y2="{T}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="152" y1="{T-16}" x2="152" y2="{T+16}" stroke="{INK}" stroke-width="2.6"/>\n'
    s += f'<line x1="164" y1="{T-8}" x2="164" y2="{T+8}" stroke="{INK}" stroke-width="2.6"/>\n'
    s += f'<line x1="166" y1="{T}" x2="250" y2="{T}" stroke="{INK}" stroke-width="2"/>\n'
    s += rect_res(285, T, 70, 24)
    s += f'<line x1="320" y1="{T}" x2="{Rr}" y2="{T}" stroke="{INK}" stroke-width="2"/>\n'
    # middle branch
    s += f'<line x1="{L}" y1="{M}" x2="112" y2="{M}" stroke="{INK}" stroke-width="2"/>\n'
    s += rect_res(147, M, 70, 24)
    s += f'<line x1="182" y1="{M}" x2="{JM}" y2="{M}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<circle cx="302" cy="{M}" r="18" fill="{WHITE}" stroke="{INK}" stroke-width="2.2"/>\n'
    s += f'<text x="302" y="{M+5}" text-anchor="middle" font-size="13" font-weight="600" fill="{INK}">A</text>\n'
    s += f'<line x1="320" y1="{M}" x2="{Rr}" y2="{M}" stroke="{INK}" stroke-width="2"/>\n'
    # vertical link M
    s += f'<line x1="{JM}" y1="{M}" x2="{JM}" y2="{JB}" stroke="{INK}" stroke-width="2"/>\n'
    # bottom branch
    s += f'<line x1="{L}" y1="{B}" x2="152" y2="{B}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<circle cx="170" cy="{B}" r="18" fill="{WHITE}" stroke="{INK}" stroke-width="2.2"/>\n'
    s += f'<text x="170" y="{B+5}" text-anchor="middle" font-size="13" font-weight="600" fill="{INK}">V</text>\n'
    s += f'<line x1="188" y1="{B}" x2="{JM}" y2="{B}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="{JM}" y1="{B}" x2="300" y2="{B}" stroke="{INK}" stroke-width="2"/>\n'
    s += rect_res(335, B, 70, 24)
    s += f'<line x1="370" y1="{B}" x2="{Rr}" y2="{B}" stroke="{INK}" stroke-width="2"/>\n'
    # junction dots
    for (x, y) in [(L, M), (L, B), (JM, M), (JM, B), (Rr, T), (Rr, M), (Rr, B)]:
        s += dot(x, y) + "\n"
    s += f'<text x="158" y="{T-26}" font-size="14" font-style="italic" font-weight="600" fill="{INK}">ε</text>\n'
    s += f'<text x="285" y="{T-18}" text-anchor="middle" font-size="13.5" font-style="italic" fill="{INK}">R</text>\n'
    s += f'<text x="147" y="{M-18}" text-anchor="middle" font-size="13.5" font-style="italic" fill="{INK}">R</text>\n'
    s += f'<text x="335" y="{B-18}" text-anchor="middle" font-size="13.5" font-style="italic" fill="{INK}">R</text>'
    return fig(s, "0 0 470 288",
               "<b>Two of these five components are decoys.</b> The ammeter is ideal, so its branch has zero "
               "resistance and short-circuits the resistor beside it; the voltmeter is ideal, so its branch "
               "carries no current at all. What is left is the cell in series with two resistors.",
               "A circuit: a cell in series with a resistor in the top branch, a resistor from the left node to a middle node, an ammeter from that middle node to the right node, and a voltmeter from the left node to the middle node with a resistor from the middle node to the right node.")


# ----------------------------------------------------------------- Q20 (five option graphs)
def _mini(prefix, shape, dashed_at=None, label=""):
    x0, y0, xt, yt = 22, 96, 162, 14
    s = defs(prefix)
    s += f'\n<line x1="{x0}" y1="{y0}" x2="{xt}" y2="{y0}" stroke="{INK}" stroke-width="1.7" marker-end="url(#{prefix}-ar)"/>\n'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{yt}" stroke="{INK}" stroke-width="1.7" marker-end="url(#{prefix}-ar)"/>\n'
    if dashed_at is not None:
        s += f'<line x1="{dashed_at}" y1="{y0}" x2="{dashed_at}" y2="{shape[0][1]}" stroke="{INK3}" stroke-width="1.4" stroke-dasharray="5 4"/>\n'
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in shape)
    s += f'<polyline points="{pts}" fill="none" stroke="{ACC}" stroke-width="2.6" stroke-linejoin="round"/>\n'
    s += f'<ellipse cx="{dashed_at}" cy="{y0}" rx="2.6" ry="2.6" fill="{INK3}"/>\n' if dashed_at is not None and False else ""
    s += f'<text x="{xt-6}" y="{y0+17}" text-anchor="end" font-size="11.5" font-style="italic" fill="{INK2}">t</text>\n'
    s += f'<text x="{x0-7}" y="{yt+4}" text-anchor="end" font-size="11.5" font-style="italic" fill="{INK2}">j</text>'
    return ('<svg class="gopt" viewBox="0 0 182 126" role="img" aria-label="' + label + '">\n' + s + '\n</svg>')


def r0_20_opts():
    """Returns the five option glyphs, in paper order."""
    out = []
    # A — straight line falling from a jump to zero
    out.append(_mini("gA", [(55, 30), (142, 94)], dashed_at=55, label="A jerk graph that jumps at the dashed line and then falls in a straight line to zero."))
    # B — smooth hump starting and ending on the axis
    out.append(_mini("gB", [(55, 94), (66, 62), (78, 34), (92, 24), (106, 30), (122, 56), (142, 94)], label="A smooth hump that starts on the axis and returns to the axis."))
    # C — piecewise-linear triangle
    out.append(_mini("gC", [(55, 94), (95, 24), (142, 94)], label="A triangle: jerk rising in a straight line from zero to a peak and falling back to zero."))
    # D — jump, rounded peak, back to zero
    out.append(_mini("gD", [(50, 62), (58, 40), (70, 26), (88, 22), (104, 30), (122, 58), (146, 94)], dashed_at=50, label="Jerk jumping at the dashed line, rising to a rounded peak and then falling to zero."))
    # E — jump then monotone convex decay
    out.append(_mini("gE", [(52, 28), (78, 34), (104, 48), (128, 68), (150, 90)], dashed_at=52, label="Jerk jumping at the dashed line and then decaying steadily towards zero."))
    return out


# ----------------------------------------------------------------- Q20 (solution)
def r0_20_sol():
    """The correct graph, with the four features the options have to satisfy labelled."""
    p = "fs20"
    x0, y0, xt, yt = 62.0, 202.0, 442.0, 40.0
    xj = 152.0
    s = defs(p)
    s += f'\n<line x1="{x0}" y1="{y0}" x2="{xt}" y2="{y0}" stroke="{INK}" stroke-width="1.8" marker-end="url(#{p}-ar)"/>\n'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{yt}" stroke="{INK}" stroke-width="1.8" marker-end="url(#{p}-ar)"/>\n'
    # phase 1: j = 0, drawn as a distinct grey line lying on the axis
    s += f'<line x1="{x0}" y1="{y0}" x2="{xj}" y2="{y0}" stroke="{INK3}" stroke-width="4"/>' + "\n"
    s += f'<line x1="{xj}" y1="{y0}" x2="{xj}" y2="62" stroke="{INK3}" stroke-width="1.5" stroke-dasharray="6 5"/>\n'
    s += (f'<path d="M{xj},{132} C190,80 220,64 258,66 C306,68 372,128 414,200" '
          f'fill="none" stroke="{ACC}" stroke-width="2.8" stroke-linejoin="round"/>\n')
    s += f'<circle cx="{xj}" cy="132" r="3.6" fill="{ACC}"/>\n'
    s += f'<text x="{x0+8}" y="{y0-12}" font-size="11.5" fill="{INK3}">free fall: a = g, so j = 0</text>\n'
    s += f'<text x="{xj+8}" y="56" font-size="11.5" font-weight="600" fill="{BAD}">rope goes taut: j jumps</text>\n'
    s += f'<text x="266" y="58" font-size="11.5" font-weight="600" fill="{ACC}">a = 0: speed greatest, so |j| greatest</text>\n'
    s += f'<text x="{xt-6}" y="{y0+18}" text-anchor="end" font-size="12" font-style="italic" fill="{INK2}">t</text>\n'
    s += f'<text x="{x0-8}" y="{yt+6}" text-anchor="end" font-size="12" font-style="italic" fill="{INK2}">j</text>\n'
    s += f'<text x="418" y="{y0-12}" text-anchor="end" font-size="11.5" font-weight="600" fill="{GOOD}">v = 0: at rest, j = 0</text>'
    return fig(s, "0 0 480 244",
               "<b>The graph the correct option has to have.</b> Flat at zero while the rope is slack; a "
               "discontinuous jump at the instant it goes taut; a rise to a maximum as the jumper is still "
               "speeding up; and a return to exactly zero at the moment of instantaneous rest.",
               "Jerk against time: zero during free fall, a jump at the moment the rope becomes taut, a rounded maximum, and a return to zero at the instant the jumper comes to rest.")


# ----------------------------------------------------------------- Q21
def r0_21():
    p = "f21"
    ox, oy = 88.0, 232.0
    Lr = 292.0
    a = math.radians(30.0)
    ex, ey = ox + Lr * math.cos(a), oy - Lr * math.sin(a)
    s = defs(p)
    s += f'\n<line x1="40" y1="42" x2="446" y2="42" stroke="{INK}" stroke-width="2.2"/>\n'
    for i in range(0, 13):
        x = 60 + i * 32
        s += f'<line x1="{x}" y1="42" x2="{x-12}" y2="30" stroke="{LINE2}" stroke-width="1.6"/>\n'
    s += f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex:.1f}" y2="42" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{INK}" stroke-width="2.8"/>\n'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox+200}" y2="{oy}" stroke="{INK3}" stroke-width="1.4" stroke-dasharray="6 5"/>\n'
    R = 66.0
    s += f'<path d="M{ox+R},{oy} A{R},{R} 0 0 1 {ox+R*math.cos(a):.1f},{oy-R*math.sin(a):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    s += f'<text x="{ox+86}" y="{oy-16}" font-size="12.5" font-weight="600" fill="{BAD}">30°</text>\n'
    s += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="7.5" fill="{WHITE}" stroke="{INK}" stroke-width="2.4"/>\n'
    s += f'<text x="{ex+14:.1f}" y="{ey-6:.1f}" font-size="13.5" font-style="italic" font-weight="600" fill="{INK}">m</text>\n'
    s += f'<text x="{(ox+ex)/2-14:.0f}" y="{(oy+ey)/2-6:.0f}" font-size="13.5" font-style="italic" fill="{INK}">ℓ</text>\n'
    s += f'<circle cx="{ox}" cy="{oy}" r="4.6" fill="{INK}"/>\n'
    s += f'<text x="{ox-16}" y="{oy+6}" font-size="13.5" font-weight="600" fill="{INK}">O</text>\n'
    s += f'<text x="{ex:.1f}" y="30" text-anchor="middle" font-size="11.5" fill="{INK3}">ceiling</text>\n'
    s += f'<text x="{ex+10:.1f}" y="{(ey+42)/2:.0f}" font-size="12" fill="{INK2}">string</text>'
    return fig(s, "0 0 480 262",
               "<b>The ring is released at the top end — the end the string is tied to — and slides down "
               "towards the hinge.</b> So its distance from O is <code>ℓ − s</code>, and <code>s</code> grows "
               "like <code>t²</code>: that is where the <code>t²</code> in the given tension comes from.",
               "A rod hinged at its lower-left end at O making thirty degrees with the horizontal, with a vertical string from the ceiling down to its upper end where a small ring of mass m is released.")


# ----------------------------------------------------------------- Q23
def r0_23():
    p = "f23"
    x0, y0 = 122.0, 216.0
    y5, y2 = 62.0, 188.0
    xs = 396.0
    s = defs(p)
    s += "\n" + axes(p, 40, x0, y0, 452.0, tip="log(I / W m⁻²)", tipy="log(R / Ω)")
    s += f'<line x1="{x0}" y1="{y5}" x2="{xs}" y2="{y2}" stroke="{ACC}" stroke-width="2.6"/>\n'
    for yy, lb in ((y5, "5.2"), (y2, "1.8")):
        s += f'<line x1="{x0-6}" y1="{yy}" x2="{x0+6}" y2="{yy}" stroke="{INK}" stroke-width="1.8"/>\n'
        s += f'<text x="{x0-12}" y="{yy+5}" text-anchor="end" font-size="13" font-weight="600" fill="{BAD}">{lb}</text>\n'
    for xx, lb in ((x0, "0"), (xs, "4")):
        s += f'<line x1="{xx}" y1="{y0-6}" x2="{xx}" y2="{y0+6}" stroke="{INK}" stroke-width="1.8"/>\n'
        s += f'<text x="{xx}" y="{y0+24}" text-anchor="middle" font-size="13" font-weight="600" fill="{BAD}">{lb}</text>\n'
    s += f'<text x="{x0+8}" y="{y5-8}" font-size="11.5" fill="{INK3}">(0, 5.2)</text>\n'
    s += f'<text x="{xs-8}" y="{y2+26}" text-anchor="end" font-size="11.5" fill="{INK3}">(4, 1.8)</text>'
    return fig(s, "0 0 480 268",
               "<b>A straight line on log–log axes.</b> Its gradient is "
               "<code>(1.8 − 5.2)/(4 − 0) = −0.85</code>, so <code>R ∝ I<sup>−0.85</sup></code>. Halving the "
               "distance multiplies the intensity by four, and <code>4<sup>−0.85</sup> ≈ 0.31</code>.",
               "A straight line on a graph of log R against log I, falling from 5.2 on the vertical axis at zero on the horizontal axis to 1.8 at four on the horizontal axis.")


# ----------------------------------------------------------------- Q25
def r0_25():
    p = "f25"
    col = [128.0, 240.0, 352.0]
    row = [72.0, 164.0, 256.0]
    s = defs(p)
    for y in row:                                     # horizontal wires + resistors
        s += f'\n<line x1="{col[0]}" y1="{y}" x2="{col[2]}" y2="{y}" stroke="{INK}" stroke-width="2"/>\n'
    for x in col:                                     # vertical wires
        s += f'<line x1="{x}" y1="{row[0]}" x2="{x}" y2="{row[2]}" stroke="{INK}" stroke-width="2"/>\n'
    for y in row:
        for i in range(2):
            s += rect_res((col[i] + col[i + 1]) / 2, y, 52, 20) + "\n"
    for x in col:
        for j in range(2):
            s += rect_res(x, (row[j] + row[j + 1]) / 2, 20, 46) + "\n"
    for x in col:
        for y in row:
            s += dot(x, y) + "\n"
    # labels placed clear of every wire and resistor box (verified against the printed figure:
    # P,Q,R on the top row, S at the centre, T bottom-middle, U bottom-right)
    lab = [("P", 128, 56), ("Q", 240, 56), ("R", 352, 56),
           ("S", 262, 150), ("T", 240, 284), ("U", 352, 284)]
    for (t, x, y) in lab:
        s += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="14" font-weight="600" fill="{PUR}">{t}</text>\n'
    return fig(s, "0 0 480 300",
               "<b>A 3 × 3 grid of nodes with all twelve resistors identical.</b> The labels sit on the nodes: "
               "P, Q, R along the top; S at the centre; T and U along the bottom. Every line you can see is "
               "one resistor.",
               "A square grid of nine nodes joined by twelve identical resistors, labelled P, Q and R along the top row, S at the centre, and T and U along the bottom row.")


# ----------------------------------------------------------------- Q6 (solution)
def r0_06():
    p = "f6"
    ytop, ybot, ymid = 58.0, 146.0, 102.0
    s = defs(p)
    s += f'\n<line x1="70" y1="{ytop}" x2="214" y2="{ytop}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="70" y1="{ybot}" x2="214" y2="{ybot}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="70" y1="{ytop}" x2="70" y2="{ybot}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<line x1="252" y1="{ytop}" x2="252" y2="{ybot}" stroke="{INK}" stroke-width="2"/>\n'
    for x in (100.0, 142.0, 184.0):
        s += rect_res(x, ymid, 18, 46) + "\n"
        s += f'<line x1="{x}" y1="{ytop}" x2="{x}" y2="{(ymid-23):.0f}" stroke="{INK}" stroke-width="2"/>\n'
        s += f'<line x1="{x}" y1="{ymid+23:.0f}" x2="{x}" y2="{ybot}" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<text x="100" y="{ytop-10}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{INK2}">3 Ω</text>\n'
    s += f'<text x="142" y="{ytop-10}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{INK2}">3 Ω</text>\n'
    s += f'<text x="184" y="{ytop-10}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{INK2}">3 Ω</text>\n'
    s += f'<line x1="40" y1="{ymid}" x2="70" y2="{ymid}" stroke="{INK}" stroke-width="2"/>\n'
    s += dot(40, ymid) + "\n"
    s += f'<line x1="252" y1="{ymid}" x2="300" y2="{ymid}" stroke="{INK}" stroke-width="2"/>\n'
    s += rect_res(332, ymid, 64, 22) + "\n"
    s += f'<line x1="364" y1="{ymid}" x2="424" y2="{ymid}" stroke="{INK}" stroke-width="2"/>\n'
    s += dot(424, ymid) + "\n"
    s += f'<text x="332" y="{ymid-16}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{INK2}">3 Ω</text>\n'
    s += f'<text x="142" y="{ybot+34}" text-anchor="middle" font-size="13" font-weight="600" fill="{GOOD}">three in parallel: 3/3 = 1 Ω, cost £3</text>\n'
    s += f'<text x="332" y="{ymid+34}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{GOOD}">one in series: +3 Ω</text>\n'
    s += f'<text x="240" y="238" text-anchor="middle" font-size="14" font-weight="600" fill="{GOOD}">R = 1 Ω + 3 Ω = 4 Ω for £4</text>'
    return fig(s, "0 0 480 252",
               "<b>The winning combination.</b> Three 3 Ω resistors side by side give "
               "<code>3/3 = 1 Ω</code>; one more 3 Ω in series brings it to exactly "
               "<code>4 Ω</code>. Three of them cost £1 each, the fourth another £1.",
               "A schematic: three three-ohm resistors in parallel between two rails, giving one ohm, followed in series by a single three-ohm resistor.")


# ----------------------------------------------------------------- Q14 (solution)
def r0_14():
    p = "f14"
    b = 66.0
    R = 1.5 * b
    ox, oy = 196.0, 158.0
    d = R
    cxx = ox + d
    a = (d * d + R * R - b * b) / (2 * d)
    h = math.sqrt(R * R - a * a)
    px, py1, py2 = ox + a, oy - h, oy + h
    s = defs(p)
    s += f'\n<circle cx="{ox}" cy="{oy}" r="{R:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>\n'
    s += f'<circle cx="{cxx:.1f}" cy="{oy}" r="{b:.1f}" fill="{SOFT}" fill-opacity="0.55" stroke="{ACC}" stroke-width="2.2"/>\n'
    s += f'<line x1="{px:.1f}" y1="{py1:.1f}" x2="{px:.1f}" y2="{py2:.1f}" stroke="{PUR}" stroke-width="2.2" stroke-dasharray="6 4"/>\n'
    s += f'<circle cx="{px:.1f}" cy="{py1:.1f}" r="3.4" fill="{PUR}"/>\n'
    s += f'<circle cx="{px:.1f}" cy="{py2:.1f}" r="3.4" fill="{PUR}"/>\n'
    s += dot(ox, oy, 4.2) + "\n" + dot(cxx, oy, 4.2) + "\n"
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox-R:.1f}" y2="{oy}" stroke="{INK3}" stroke-width="1.4" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<line x1="{cxx:.1f}" y1="{oy}" x2="{cxx+b:.1f}" y2="{oy}" stroke="{INK3}" stroke-width="1.4" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<line x1="{ox}" y1="{oy+52}" x2="{cxx:.1f}" y2="{oy+52}" stroke="{ACC}" stroke-width="1.5" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy+52}" stroke="{LINE2}" stroke-width="1.2" stroke-dasharray="4 4"/>\n'
    s += f'<line x1="{cxx:.1f}" y1="{oy}" x2="{cxx:.1f}" y2="{oy+52}" stroke="{LINE2}" stroke-width="1.2" stroke-dasharray="4 4"/>\n'
    s += f'<text x="{ox-58:.0f}" y="{oy-10:.0f}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK2}">R = 3b/2</text>\n'
    s += f'<text x="{cxx+34:.0f}" y="{oy-10:.0f}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK2}">b</text>\n'
    s += f'<text x="{(ox+cxx)/2:.0f}" y="{oy+70:.0f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{ACC}">d = R at the start</text>\n'
    s += f'<text x="{ox-18:.0f}" y="{oy+6:.0f}" text-anchor="end" font-size="13.5" font-weight="600" fill="{INK}">O</text>\n'
    s += f'<text x="{cxx+2:.0f}" y="{oy-10:.0f}" text-anchor="start" font-size="13.5" font-weight="600" fill="{ACC}">C</text>\n'
    s += f'<text x="{px+10:.1f}" y="{py1+4:.1f}" font-size="13" font-weight="600" fill="{PUR}">P</text>\n'
    s += f'<text x="{px+10:.1f}" y="{py2+4:.1f}" font-size="13" font-weight="600" fill="{PUR}">Q</text>\n'
    s += f'<text x="{ox-R-30:.0f}" y="{oy+18:.0f}" text-anchor="start" font-size="11.5" fill="{INK3}">cup rim</text>\n'
    s += f'<text x="{cxx-40:.0f}" y="{oy+b+26:.0f}" text-anchor="middle" font-size="11.5" fill="{ACC}">biscuit</text>'
    return fig(s, "0 0 480 268",
               "<b>The geometry of the balance.</b> The rim (radius <code>R</code>) crosses the biscuit's edge "
               "(radius <code>b</code>) at P and Q. The biscuit stays up while its centre of mass C lies inside "
               "the segment cut off by the chord PQ — so it falls the moment C reaches that chord.",
               "A large circle for the cup rim and a smaller circle for the biscuit overlapping it, with the two crossing points joined by a dashed chord, the two centres marked O and C, and the radii R and b dimensioned.")


# ----------------------------------------------------------------- Q16 (solution)
def r0_16():
    p = "f16"
    n = math.sqrt(2.0)
    th1 = math.radians(30.0)
    th2 = math.asin(math.sin(th1) / n)
    ax0, ay0, side = 150.0, 84.0, 176.0
    ax1, ay1 = ax0 + side, ay0 + side
    ex_, ey_ = ax0 + side / 2, ay0
    # incident ray, drawn backwards from the entry point along -normal
    Li = 76.0
    ix, iy = ex_ - Li * math.sin(th1), ey_ - Li * math.cos(th1)
    # refracted ray to the opposite (bottom) face
    Lr = side / math.cos(th2)
    rx, ry = ex_ + Lr * math.sin(th2), ey_ + Lr * math.cos(th2)
    s = defs(p)
    s += f'\n<rect x="{ax0}" y="{ay0}" width="{side}" height="{side}" fill="{SOFT}" fill-opacity="0.5" stroke="{INK}" stroke-width="2.2"/>\n'
    s += f'<line x1="{ex_}" y1="{ay0-44}" x2="{ex_}" y2="{ay0+52}" stroke="{LINE2}" stroke-width="1.5" stroke-dasharray="6 5"/>\n'
    s += f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{ex_}" y2="{ey_}" stroke="{ACC}" stroke-width="2.6" marker-end="url(#{p}-arA)"/>\n'
    s += f'<line x1="{ex_}" y1="{ey_}" x2="{rx:.1f}" y2="{ry:.1f}" stroke="{ACC}" stroke-width="2.6" marker-end="url(#{p}-arA)"/>\n'
    R1, R2 = 46.0, 46.0
    s += f'<path d="M{ex_},{ay0-R1} A{R1},{R1} 0 0 0 {ex_-R1*math.sin(th1):.1f},{ay0-R1*math.cos(th1):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    s += f'<path d="M{ex_},{ay0+R2} A{R2},{R2} 0 0 0 {ex_+R2*math.sin(th2):.1f},{ay0+R2*math.cos(th2):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    s += f'<text x="{ex_-36:.0f}" y="{ay0-28:.0f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{BAD}">30°</text>\n'
    s += f'<text x="{ex_+34:.0f}" y="{ay0+52:.0f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{BAD}">20.7°</text>\n'
    s += f'<text x="{ax0+52:.0f}" y="{ay0+148:.0f}" font-size="13.5" font-style="italic" fill="{INK}">n = √2</text>\n'
    s += f'<line x1="{ax0-20}" y1="{ay0}" x2="{ax0-20}" y2="{ay1}" stroke="{INK3}" stroke-width="1.4" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<text x="{ax0-30}" y="{ay0+side/2+5:.0f}" text-anchor="end" font-size="13" font-weight="600" fill="{INK2}">a</text>\n'
    s += f'<text x="{rx-34:.1f}" y="{(ey_+ry)/2+16:.0f}" text-anchor="end" font-size="11.5" fill="{INK2}">path = a / cos θ₂</text>\n'
    s += f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="4" fill="{BAD}"/>'
    return fig(s, "0 0 480 290",
               "<b>Why the path is <code>a / cos θ₂</code>.</b> The ray enters the top face and leaves through "
               "the opposite face a distance <code>a</code> below it, so it covers "
               "<code>a / cos θ₂ = a / cos 20.7°</code> of glass at speed <code>c/√2</code>.",
               "A square glass block with a ray meeting the top face at thirty degrees to the normal, refracting to a steeper path inside the block and leaving through the bottom face, with the side labelled a.")


# ----------------------------------------------------------------- Q22 (solution)
def r0_22():
    p = "f22"
    ox, oy = 200.0, 48.0
    Lp = 156.0
    thA, thB = math.radians(30.0), math.radians(60.0)
    ax_, ay_ = ox + Lp * math.sin(thA), oy + Lp * math.cos(thA)
    bx_, by_ = ox + Lp * math.sin(thB), oy + Lp * math.cos(thB)
    rA, rB = Lp * math.sin(thA), Lp * math.sin(thB)
    s = defs(p)
    s += f'\n<line x1="60" y1="30" x2="440" y2="30" stroke="{INK}" stroke-width="2.2"/>\n'
    for i in range(0, 12):
        x = 76 + i * 32
        s += f'<line x1="{x}" y1="30" x2="{x-12}" y2="18" stroke="{LINE2}" stroke-width="1.6"/>\n'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{by_:.1f}" stroke="{LINE2}" stroke-width="1.5" stroke-dasharray="6 5"/>\n'
    s += f'<ellipse cx="{ox}" cy="{ay_}" rx="{rA:.1f}" ry="15" fill="none" stroke="{INK3}" stroke-width="1.4" stroke-dasharray="5 5"/>\n'
    s += f'<ellipse cx="{ox}" cy="{by_}" rx="{rB:.1f}" ry="18" fill="none" stroke="{LINE2}" stroke-width="1.4" stroke-dasharray="5 5"/>\n'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ax_:.1f}" y2="{ay_:.1f}" stroke="{INK}" stroke-width="2.4"/>\n'
    s += f'<line x1="{ox}" y1="{oy}" x2="{bx_:.1f}" y2="{by_:.1f}" stroke="{INK3}" stroke-width="1.8" stroke-dasharray="7 5"/>\n'
    s += f'<line x1="{ox}" y1="{ay_:.1f}" x2="{ax_:.1f}" y2="{ay_:.1f}" stroke="{ACC}" stroke-width="1.6" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    R = 62.0
    s += f'<path d="M{ox},{oy+R} A{R},{R} 0 0 1 {ox+R*math.sin(thA):.1f},{oy+R*math.cos(thA):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    s += f'<path d="M{ox},{oy+R} A{R},{R} 0 0 0 {ox+R*math.sin(thB):.1f},{oy+R*math.cos(thB):.1f}" fill="none" stroke="{INK3}" stroke-width="1.4" stroke-dasharray="5 4"/>\n'
    s += f'<text x="{ox+40}" y="{oy+82}" font-size="12.5" font-weight="600" fill="{BAD}">30°</text>\n'
    s += f'<text x="{ox+52}" y="{oy+56}" font-size="12.5" font-weight="600" fill="{INK3}">60°</text>\n'
    s += f'<circle cx="{ax_:.1f}" cy="{ay_:.1f}" r="7.5" fill="{WHITE}" stroke="{INK}" stroke-width="2.4"/>\n'
    s += f'<circle cx="{bx_:.1f}" cy="{by_:.1f}" r="6" fill="{WHITE}" stroke="{INK3}" stroke-width="1.8"/>\n'
    s += f'<text x="{ax_:.1f}" y="{ay_+26:.1f}" text-anchor="middle" font-size="12" font-weight="600" fill="{ACC}">r = ℓ sin 30°</text>\n'
    s += f'<text x="{bx_:.1f}" y="{by_+26:.1f}" text-anchor="middle" font-size="11.5" fill="{INK3}">r = ℓ sin 60°</text>\n'
    s += f'<text x="{(ox+ax_)/2-16:.0f}" y="{(oy+ay_)/2:.0f}" font-size="13" font-style="italic" fill="{INK}">ℓ</text>\n'
    s += dot(ox, oy, 4)
    return fig(s, "0 0 480 250",
               "<b>Doubling the angle from 30° to 60° nearly doubles the radius</b> — "
               "<code>ℓ sin 30° = 0.50ℓ</code> becomes <code>ℓ sin 60° = 0.87ℓ</code> — while the height of the "
               "bob above the pivot falls from <code>0.87ℓ</code> to <code>0.50ℓ</code>. Every one of those "
               "changes is packed into <code>ω² = g/(ℓ cos θ)</code>.",
               "A conical pendulum: a string from a fixed point making thirty degrees with the vertical, with the bob on a dashed horizontal circle, and a second fainter string at sixty degrees with a larger circle.")


# ----------------------------------------------------------------- Q24 (solution)
def r0_24():
    p = "f24"
    wallx, groundy = 396.0, 248.0
    bx, tx, ty = 176.0, 396.0, 28.0
    # 45 degrees to the vertical means 45 degrees to the ground too
    top_y = groundy - (tx - bx)
    gx, gy = (bx + tx) / 2, (groundy + top_y) / 2
    s = defs(p)
    s += f'\n<line x1="{wallx}" y1="20" x2="{wallx}" y2="{groundy}" stroke="{INK}" stroke-width="2.4"/>\n'
    s += f'<line x1="56" y1="{groundy}" x2="440" y2="{groundy}" stroke="{INK}" stroke-width="2.4"/>\n'
    s += f'<line x1="{bx}" y1="{groundy}" x2="{tx}" y2="{top_y:.1f}" stroke="{INK}" stroke-width="3"/>\n'
    s += dot(gx, gy, 4.6) + "\n"
    s += f'<text x="{gx-10:.0f}" y="{gy-12:.0f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{PUR}">G</text>\n'
    s += f'<line x1="{gx:.1f}" y1="{gy:.1f}" x2="{wallx}" y2="{gy:.1f}" stroke="{LINE2}" stroke-width="1.3" stroke-dasharray="5 4"/>\n'
    s += f'<line x1="{bx}" y1="{groundy+34}" x2="{wallx}" y2="{groundy+34}" stroke="{ACC}" stroke-width="1.5" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<line x1="{bx}" y1="{groundy}" x2="{bx}" y2="{groundy+40}" stroke="{LINE2}" stroke-width="1.2" stroke-dasharray="4 4"/>\n'
    s += f'<line x1="{wallx}" y1="{groundy}" x2="{wallx}" y2="{groundy+40}" stroke="{LINE2}" stroke-width="1.2" stroke-dasharray="4 4"/>\n'
    s += f'<text x="{(bx+wallx)/2:.0f}" y="{groundy+54}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{ACC}">x = L sin θ</text>\n'
    s += f'<line x1="112" y1="{gy:.1f}" x2="{gx:.1f}" y2="{gy:.1f}" stroke="{INK3}" stroke-width="1.4" marker-start="url(#{p}-dimS)" marker-end="url(#{p}-dim)"/>\n'
    s += f'<text x="{(112+gx)/2:.0f}" y="{gy-8:.0f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{INK2}">h = (L/2) cos θ</text>\n'
    R = 74.0
    s += f'<path d="M{tx},{top_y+R:.1f} A{R},{R} 0 0 0 {tx-R*math.sin(math.radians(45)):.1f},{top_y+R*math.cos(math.radians(45)):.1f}" fill="none" stroke="{BAD}" stroke-width="1.8"/>\n'
    s += f'<text x="{tx-58:.0f}" y="{top_y+R+20:.0f}" font-size="12.5" font-weight="600" fill="{BAD}">45°</text>\n'
    s += f'<line x1="{bx}" y1="{groundy-14}" x2="{bx+52}" y2="{groundy-14}" stroke="{GOOD}" stroke-width="2.4" marker-end="url(#{p}-ar)"/>\n'
    s += f'<text x="{bx+60}" y="{groundy-8}" font-size="12.5" font-weight="600" fill="{GOOD}">push a</text>'
    return fig(s, "0 0 480 300",
               "<b>The centre of mass is half way up the ladder</b>, so its height is "
               "<code>h = (L/2) cos θ</code>. At 45° a small push <code>a</code> towards the wall raises it by "
               "<code>(a/2) tan 45° = a/2</code> — the top of the ladder rises by the full <code>a</code>, the "
               "centre by half of that.",
               "A ladder resting against a wall at forty-five degrees, its centre of mass marked, with the height of the centre of mass, the base distance and the push towards the wall all dimensioned.")


FIGURES = {
    "r0-01": r0_01, "r0-02": r0_02, "r0-06": r0_06, "r0-07": r0_07, "r0-08": r0_08,
    "r0-14": r0_14, "r0-16": r0_16, "r0-21": r0_21, "r0-22": r0_22, "r0-23": r0_23,
    "r0-20-sol": r0_20_sol, "r0-24": r0_24, "r0-25": r0_25,
}


if __name__ == "__main__":
    import os
    os.makedirs("/tmp/bpho25/fig", exist_ok=True)
    for k, fn in FIGURES.items():
        open(f"/tmp/bpho25/fig/{k}.svg", "w").write(fn())
        print(k, len(fn()))
    for i, g in enumerate(r0_20_opts()):
        open(f"/tmp/bpho25/fig/r0-20-{'ABCDE'[i]}.svg", "w").write(g)
    print("r0-20 done")
