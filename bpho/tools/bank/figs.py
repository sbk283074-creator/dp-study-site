# -*- coding: utf-8 -*-
"""Build fig/ from every figsNN.py in this directory.

Run:  python figs.py            (all sections)
      python figs.py 1 2        (just these)

Each figsNN.py exports a FIGS dict mapping a figure key to a zero-argument function that
returns the SVG text.  Keys are 's<NN>-<QQ>'.  Sections are discovered, not listed, so
adding a section's figures needs no change here.
"""
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, 'fig')

MOD_RE = re.compile(r'^figs(\d\d)\.py$')


def section_modules():
    """Every figsNN.py in this directory, as (section number, module name), sorted."""
    found = []
    for f in sorted(os.listdir(HERE)):
        m = MOD_RE.match(f)
        if m:
            found.append((int(m.group(1)), 'figs' + m.group(1)))
    return found


def collect(want=None):
    """Merge the FIGS dicts of the requested sections."""
    figs = {}
    for n, name in section_modules():
        if want and n not in want:
            continue
        mod = importlib.import_module(name)
        for key, fn in mod.FIGS.items():
            if key in figs:
                raise SystemExit('duplicate figure key %r (section %02d)' % (key, n))
            figs[key] = fn
    return figs


def main(argv):
    want = {int(a) for a in argv if a.isdigit()} or None
    figs = collect(want)
    if not figs:
        print('no figures found -- is there a figsNN.py?')
        return 1
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for key, fn in sorted(figs.items()):
        path = os.path.join(OUT, key + '.svg')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(fn() + '\n')
        print('wrote %-10s %6d bytes' % (key, os.path.getsize(path)))
    print('%d figures' % len(figs))

    # Report -- never delete -- files left over from a renamed key.  A stale svg does
    # nothing at render time (the build only reads keys that are referenced) but it makes
    # the directory lie about what is current, and the next person to grep for a key
    # finds two files and no way to tell which one is live.
    #
    # Only for the sections actually built.  Building one section with `figs.py 2` makes
    # every other section's figures look stale, which is a false alarm loud enough to
    # train the reader to ignore the warning entirely.
    KEY_RE = re.compile(r'^s(\d\d)-')
    built = {int(KEY_RE.match(k).group(1)) for k in figs if KEY_RE.match(k)}
    stale = []
    for f in sorted(os.listdir(OUT)):
        if not f.endswith('.svg'):
            continue
        key = f[:-4]
        m = KEY_RE.match(key)
        if m and int(m.group(1)) not in built:
            continue                      # a section we did not build this run
        if key not in figs:
            stale.append(key)
    if stale:
        print('\nSTALE: %d file(s) no longer produced by any figure: %s'
              % (len(stale), ', '.join(stale)))
        print('       delete them once you have confirmed nothing references them:')
        for k in stale:
            print('       rm %s' % os.path.join(OUT, k + '.svg'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
