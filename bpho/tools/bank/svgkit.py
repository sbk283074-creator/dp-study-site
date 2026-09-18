# -*- coding: utf-8 -*-
"""Shared SVG primitives and the house palette for the BPhO drill bank figures.

Every figure in this bank is hand-authored inline SVG emitted into fig/.  There are no
image files and nothing is fetched, because the study site has to work over file://.

Three rules, each of which fails silently if broken:

  1. A figure-bearing `q` in secNN.py must be a BACKTICK template string, because the
     SVG attributes use double quotes.  The build step handles that.
  2. Marker ids must be unique across the WHOLE bank, because HTML has no id namespace:
     two figures both defining id="ar" collide and one silently gets the other's
     arrowhead.  Prefix every marker with the figure key.
  3. Literal hex inside the SVG, never var(--...).  A CSS variable in a <text fill>
     resolves against the SVG's own context, not the page, and comes out black.

The house rule for the drawings themselves: a figure must encode the discriminator the
question turns on, not decorate the apparatus.

Per-section figures live in figsNN.py and import from here:

    from svgkit import *

`figs.py` is the driver that writes fig/ from all of them.
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig')

INK = '#14181f'
GREY = '#7b8494'
BLUE = '#2f5fd0'
RED = '#b3352f'
GREEN = '#1f7a53'
AMBER = '#a8641a'
PURPLE = '#5b3fa8'
PANEL = '#f2f5fa'
WALL = '#e6eaf2'


def _col(x, fn, slot):
    """Guard the colour/fill slots.

    Every helper that takes both a stroke colour and a fill puts them in the SAME order
    -- (..., colour, width, fill) -- except RC, which takes the fill first because a
    plain rectangle usually has no stroke.  That one inconsistency has produced the same
    silent-swap bug three times: PG(pts, '#dfe8f6', BLUE, 1.2) puts the fill into the
    colour slot, and the failure surfaces as `TypeError: must be real number, not str`
    from deep inside a %-format, which says nothing about the actual mistake.

    So check the slot and say what went wrong.
    """
    if not isinstance(x, str) or (x != 'none' and not x.startswith('#')):
        raise TypeError(
            "%s: %s slot got %r -- expected a colour like '#14181f' or 'none'. "
            "Signature is %s.  The usual cause is passing the fill before the colour; "
            "only RC takes the fill first."
            % (fn, slot, x, _SIG[fn]))
    return x


_SIG = {
    'L':  'L(x1, y1, x2, y2, c, sw, extra)',
    'PL': 'PL(pts, c, sw, fill, extra)',
    'PG': 'PG(pts, c, sw, fill)',
    'CI': 'CI(cx, cy, r, c, sw, fill)',
    'PA': 'PA(d, c, sw, fill, extra)',
    'RC': 'RC(x, y, w, h, fill, stroke, sw)  <-- fill FIRST, unlike the others',
}


# HTML foreign-content BREAKOUT tag names.  When the HTML parser meets one of these
# inside an inline <svg>, it closes the svg and parses the remainder as HTML.  A figure
# built with <sup> therefore loses its exponent AND every element written after it, and
# it fails silently: the svg keeps its box, so a size check, a tag-balance lint and a
# screenshot of the svg alone all still look fine.  `sub` and `sup` are the two that a
# physics figure naturally reaches for, so they are rejected at build time.
BREAKOUT_IN_SVG = ("sup", "sub", "span", "code", "em", "strong", "b", "i", "small",
                   "p", "div", "br", "hr", "table", "ul", "ol", "li", "font")


def svg(w, h, label, body):
    bad = [t for t in BREAKOUT_IN_SVG if ("<%s>" % t) in body or ("<%s " % t) in body]
    if bad:
        raise SystemExit(
            "figure uses %s inside inline SVG -- the HTML parser will close the svg there "
            "and drop the rest of the figure into the page. Use <tspan> instead."
            % ", ".join("<%s>" % t for t in bad))
    return ('<figure class="fig">\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" role="img" '
            'aria-label="%s">\n%s\n</svg>\n</figure>' % (w, h, label, body))


def mk(pid, color=INK):
    return ('<defs><marker id="%s" markerWidth="9" markerHeight="9" refX="7" refY="3.2" '
            'orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="%s"/></marker></defs>'
            % (pid, color))


def L(x1, y1, x2, y2, c=INK, sw=1.7, extra=''):
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g"%s/>'
            % (x1, y1, x2, y2, c, sw, extra))


def T(x, y, s, size=11.5, anchor='start', c=INK, weight=''):
    a = ' text-anchor="%s"' % anchor if anchor != 'start' else ''
    w = ' font-weight="%s"' % weight if weight else ''
    return ('<text x="%g" y="%g" font-size="%g"%s%s fill="%s">%s</text>'
            % (x, y, size, a, w, c, s))


def PL(pts, c=INK, sw=1.7, fill='none', extra=''):
    c, fill = _col(c, 'PL', 'colour'), _col(fill, 'PL', 'fill')
    d = ' '.join('%g,%g' % p for p in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%g" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, fill, c, sw, extra))


def PG(pts, c=INK, sw=1.6, fill='none'):
    c, fill = _col(c, 'PG', 'colour'), _col(fill, 'PG', 'fill')
    d = ' '.join('%g,%g' % p for p in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%g" '
            'stroke-linejoin="round"/>' % (d, fill, c, sw))


def CI(cx, cy, r, c=INK, sw=1.7, fill='none'):
    c, fill = _col(c, 'CI', 'colour'), _col(fill, 'CI', 'fill')
    return '<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="%g"/>' % (
        cx, cy, r, fill, c, sw)


def PA(d, c=INK, sw=1.7, fill='none', extra=''):
    c, fill = _col(c, 'PA', 'colour'), _col(fill, 'PA', 'fill')
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round" '
            'stroke-linecap="round"%s/>' % (d, fill, c, sw, extra))


def RC(x, y, w, h, fill=PANEL, stroke='none', sw=0):
    fill, stroke = _col(fill, 'RC', 'fill'), _col(stroke, 'RC', 'stroke')
    s = ' stroke="%s" stroke-width="%g"' % (stroke, sw) if stroke != 'none' else ''
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"%s/>' % (x, y, w, h, fill, s)


def ARC(cx, cy, r, a0, a1, c=GREY, sw=1.2, n=16):
    """Small angle arc, as a sampled polyline.  Angles in degrees, SVG convention
    (y grows downward), measured from the +x axis.

    Deliberately NOT an SVG elliptical arc.  The `A` command takes two flags that
    are easy to get wrong, and when large-arc and sweep are both set the radius is
    silently enlarged and the arc bulges outside the circle it is supposed to lie
    on -- a bug that is invisible in the source and obvious on screen.  Sampling
    the arc removes the whole class of mistake.
    """
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / float(n))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return PL(pts, c, sw)
