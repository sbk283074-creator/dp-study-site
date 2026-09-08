#!/usr/bin/env python3
"""Validate the DP Learning site.

Two checks, run over every .html file outside tools/ and .workbuddy-ai/:

  1. LINKS    - every local href/src resolves to a file that exists.
  2. STRUCTURE- tags are properly nested (stack matcher over block/flow tags),
                plus a report of component usage and word counts so pages that
                fell short of the brief are obvious.

Exit code 0 = clean. Any problem is printed with file:line.
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.workbuddy-ai', 'tools', '.git', 'node_modules'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
# Tags whose end tag is optional / which we do not want to enforce.
LOOSE = {'p', 'li', 'td', 'th', 'tr', 'thead', 'tbody', 'option', 'dt', 'dd',
         'head', 'html', 'body', 'colgroup', 'figure', 'figcaption'}

ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))')
LINK_ATTRS = {'href', 'src'}


class Checker(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.errors = []
        self.links = []
        self.text_len = 0
        self.counts = {}

    def handle_starttag(self, tag, attrs):
        d = {}
        for a in attrs:
            if isinstance(a, tuple):
                d[a[0]] = (a[1] or '') if len(a) > 1 else ''
            else:  # already a dict (shouldn't happen, but be safe)
                d.update(a)
        cls = d.get('class', '')
        for c in cls.split():
            self.counts[c] = self.counts.get(c, 0) + 1
        for a, v in d.items():
            if a in LINK_ATTRS and v and not v.startswith(('http', '//', '#', 'mailto:', 'data:', 'javascript:')):
                self.links.append(v)
        if tag not in VOID and tag not in LOOSE:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        # `<rect />` style: handle_starttag pushed it, so pop it straight back off.
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in LOOSE:
            # pop down to a matching loose tag if present, else ignore
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    return
            return
        if not self.stack:
            self.errors.append(f'{self.getpos()[0]}: stray </{tag}>')
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errors.append(
                f'{self.getpos()[0]}: </{tag}> closes <{self.stack[-1][0]}> opened at line {self.stack[-1][1]}')
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    return

    def handle_data(self, data):
        self.text_len += len(data.split())


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, ROOT)
        for f in sorted(filenames):
            if f.endswith('.html'):
                yield os.path.join(rel, f) if rel != '.' else f


def main():
    files = list(walk())
    broken, struct, thin = [], [], []
    total_links = 0
    for rel in files:
        p = os.path.join(ROOT, rel)
        with open(p, encoding='utf-8') as fh:
            src = fh.read()
        c = Checker(rel)
        c.feed(src)
        for t, ln in c.stack:
            struct.append(f'{rel}:{ln}: <{t}> never closed')
        for e in c.errors:
            struct.append(f'{rel}:{e}')
        for link in c.links:
            total_links += 1
            target = link.split('#')[0]
            if not target:
                continue
            tp = os.path.normpath(os.path.join(os.path.dirname(p), target))
            if not os.path.exists(tp):
                broken.append(f'{rel}: {link} -> missing {os.path.relpath(tp, ROOT)}')
        if c.text_len < 400 and 'index.html' not in rel:
            thin.append(f'{rel}: only {c.text_len} words')
    print(f'Scanned {len(files)} pages, {total_links} local links.')
    print()
    if broken:
        print(f'BROKEN LINKS ({len(broken)})')
        for b in broken:
            print('  ' + b)
    else:
        print('BROKEN LINKS: none')
    print()
    if struct:
        print(f'STRUCTURE PROBLEMS ({len(struct)})')
        for s in struct[:60]:
            print('  ' + s)
    else:
        print('STRUCTURE: clean')
    print()
    if thin:
        print(f'THIN PAGES ({len(thin)})')
        for t in thin:
            print('  ' + t)
    else:
        print('THIN PAGES: none')
    return 1 if (broken or struct) else 0


if __name__ == '__main__':
    sys.exit(main())
