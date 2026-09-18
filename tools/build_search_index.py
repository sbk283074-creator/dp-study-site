#!/usr/bin/env python3
"""Build assets/js/search-index.js — the index behind the global search palette.

Run from the site root:   python3 tools/build_search_index.py

Design notes that matter:

1. ONLY GIT-TRACKED FILES ARE INDEXED.
   The previous version walked the whole working tree, so 84 of its 161 entries
   pointed at pages that do not exist on the live site — 76 of them were pygame's
   docs inside the gitignored PYTHON/verify-venv/, and 8 were inside the
   gitignored 13 GB `dp learning/` copy. Half the payload was dead weight and
   every one of those results 404'd. `git ls-files` is the source of truth for
   "what actually ships".

2. THE INDEX IS A PLAIN JS ASSIGNMENT, NOT JSON.
   Pages load it with a <script> tag, which works from file:// where fetch()
   would be blocked by CORS.

3. SINGLE-PAGE APPS NEED HELP.
   A crawler reading bpho/index.html or PYTHON/index.html sees either an empty
   shell or one enormous document. BPhO's content lives in `window.BPHO_*`
   globals (dumped by tools/bpho_dump.mjs), and Python Mastery is split into
   <section class="chapter" id="slug"> blocks, so both become many small,
   precisely deep-linked entries instead of one useless one.
"""
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'js', 'search-index.js')
HUB = 'https://sbk283074-creator.github.io/dp-study-site/'

SKIP_FILES = {'tools/example-page.html'}
TEXT_CAP = 460       # chars of body text for an ordinary page
CHAPTER_CAP = 620    # chars for one chapter of a single-page app
POEM_CAP = 1100      # a poem plus its context is worth more than a page snippet

# --------------------------------------------------------------------------
# Spaces — the group headings the palette shows results under.
# --------------------------------------------------------------------------
SPACES = [
    (r'^challenge-bank/', 'Challenge Bank', 'page'),
    (r'^bpho/', 'BPhO Round 0', 'page'),
    (r'^ib-english-vocab/', 'IB English Vocab', 'page'),
    (r'^vocab-review/', 'Vocabulary Review', 'page'),
    (r'^Eng learning/', "The World's Wife Lab", 'page'),
    (r'^PYTHON/', 'Python Mastery', 'page'),
    (r'^qbank/', 'Question Bank', 'page'),
    (r'^math/', 'Maths AA HL', 'page'),
    (r'^physics/', 'Physics HL', 'page'),
    (r'^cs/', 'Computer Science HL', 'page'),
    (r'^english/', 'English A: Lang & Lit', 'page'),
    (r'^chinese/', 'Chinese A SL', 'page'),
    (r'^business/', 'Business Management SL', 'page'),
    (r'^core/', 'DP Core (TOK · EE · CAS)', 'page'),
]

CH_SUBJECT = {
    'math-aa-hl': 'Maths AA HL',
    'physics-hl': 'Physics HL',
    'computer-science-hl': 'Computer Science HL',
    'business-management-sl': 'Business Management SL',
}


def strip_tags(s: str) -> str:
    s = re.sub(r'(?is)<(script|style|svg|noscript)\b.*?</\1>', ' ', s)
    s = re.sub(r'(?s)<!--.*?-->', ' ', s)
    s = re.sub(r'(?is)<(header|nav|footer)\b.*?</\1>', ' ', s)
    s = re.sub(r'(?i)</(p|div|li|h[1-6]|tr|section|details|br)>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def clean(s: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()


def space_of(rel: str):
    for pat, name, kind in SPACES:
        if re.match(pat, rel):
            return name, kind
    return 'Hub & guides', 'page'


# Trailing " — <site name>" segments stripped from <title>.
SITE_SUFFIXES = {
    'ib challenge bank', 'dp learning', 'ib english vocabulary mastery',
    'english lit lab', 'vocabulary review',
}


def title_of(raw: str, rel: str) -> str:
    m = re.search(r'(?is)<title>(.*?)</title>', raw)
    t = clean(m.group(1)) if m else os.path.basename(rel)
    # Drop only a trailing site-name segment, so "BM SL — Question paper" survives
    # while "BM SL — IB Challenge Bank" becomes "BM SL".
    parts = [p.strip() for p in re.split(r'\s+[—–|]\s+', t) if p.strip()]
    while len(parts) > 1 and parts[-1].lower() in SITE_SUFFIXES:
        parts.pop()
    t = ' — '.join(parts)
    return t or os.path.basename(rel)


def main_text(raw: str) -> str:
    """Body text with the shared chrome removed.

    Some single-page apps (the Lit Lab, Vocabulary Review) put their controls in
    <main> and their content elsewhere, so a short result falls back to the whole
    document rather than indexing the toolbar.
    """
    m = re.search(r'(?is)<main\b.*?</main>', raw)
    body = m.group(0) if m else raw
    m2 = re.search(r'(?is)<div id="app-shell">(.*)</div>\s*<script', body)
    if m2:
        body = m2.group(1)
    text = strip_tags(body)
    if len(text) < 150:
        text = strip_tags(raw)
    return text


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    return [p for p in out.stdout.split('\n')
            if p.strip() and p not in SKIP_FILES]


def is_redirect_stub(raw: str) -> bool:
    return bool(re.search(r'(?i)http-equiv=["\']refresh', raw)) or len(raw) < 900


# --------------------------------------------------------------------------
# Per-space extractors
# --------------------------------------------------------------------------
def challenge_bank_docs(rel, raw):
    """One question page -> one richly labelled entry."""
    h1 = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', raw)
    title = clean(h1.group(1)) if h1 else title_of(raw, rel)
    # The id is only in <title> and in the lede as a bare text node
    # ("… · MATH-AHL1.11-201"), never wrapped in its own tag.
    qid = ''
    m = re.search(r'([A-Z]{2,}(?:-[A-Za-z0-9.]+)+-\d{3})', title_of(raw, rel))
    if m:
        qid = m.group(1)
    subj = ''
    m = re.search(r'(?is)class="lede"[^>]*>.*?<a[^>]*>(.*?)</a>', raw)
    if m:
        subj = clean(m.group(1))
    if not subj:
        parts = rel.split('/')
        if len(parts) > 2:
            subj = CH_SUBJECT.get(parts[2], '')
    chips = [clean(c) for c in re.findall(r'(?is)<span class="chip[^"]*">(.*?)</span>', raw)]
    marks = next((c for c in chips if 'mark' in c.lower()), '')
    diff = next((c for c in chips if c.lower().startswith('difficulty')), '')
    topic = next((c for c in chips if c.lower().startswith('topic')), '')
    paper = next((c for c in chips if re.match(r'^P\d', c)), '')
    badge = ' · '.join(x for x in [diff.replace('difficulty ', 'd'), marks, paper] if x)
    return [{
        'path': rel, 'hash': '', 'title': (qid + ' · ' if qid else '') + title[:150],
        'space': 'Challenge Bank', 'subject': subj, 'kind': 'question',
        'badge': badge, 'heads': [topic] if topic else [],
        'text': main_text(raw)[:CHAPTER_CAP], 'url': HUB + rel,
    }]


def chapter_docs(rel, raw, space):
    """Split a hash-routed single-page app into one entry per <section class="chapter">."""
    docs = []
    blocks = re.findall(
        r'(?is)<section class="chapter"[^>]*id="([^"]+)"[^>]*>(.*?)</section>', raw)
    for slug, inner in blocks:
        h = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', inner)
        title = clean(h.group(1)) if h else slug.replace('-', ' ')
        heads = [clean(x) for x in re.findall(r'(?is)<h2[^>]*>(.*?)</h2>', inner)][:12]
        text = strip_tags(inner)
        if len(text) < 60:
            continue                      # a chapter stub is not a search result
        docs.append({
            'path': rel, 'hash': '#/' + slug, 'title': title[:150],
            'space': space, 'subject': space, 'kind': 'chapter',
            'badge': 'chapter', 'heads': heads,
            'text': text[:CHAPTER_CAP],
            'url': HUB + rel + '#/' + slug,
        })
    return docs


def basic_doc(rel, raw):
    space, kind = space_of(rel)
    heads = [clean(x) for x in re.findall(r'(?is)<h[23][^>]*>(.*?)</h[23]>', raw)][:15]
    return {
        'path': rel, 'hash': '', 'title': title_of(raw, rel)[:150],
        'space': space, 'subject': space if space != 'Hub & guides' else '',
        'kind': kind, 'badge': '', 'heads': heads,
        'text': main_text(raw)[:TEXT_CAP], 'url': HUB + rel,
    }


LITLAB_PATH = 'Eng learning/index.html'


def page_docs(rel, raw):
    if re.match(r'^challenge-bank/site/q/', rel):
        return challenge_bank_docs(rel, raw)
    if rel == LITLAB_PATH:
        # The prose lives in an inline JS literal, so the scraped text is only
        # the toolbar. The 30 poems come from englab_docs(); this is the door.
        return [{
            'path': rel, 'hash': '', 'title': "The World's Wife Lab",
            'space': "The World's Wife Lab", 'subject': 'Carol Ann Duffy',
            'kind': 'page', 'badge': '30 poems', 'heads': [],
            'text': ("Carol Ann Duffy's The World's Wife, poem by poem: full text, key "
                     'passages, vocabulary, close reading and examiner-style questions '
                     'for Paper 2 and the Individual Oral.'),
            'url': HUB + rel.replace(' ', '%20'),
        }]
    if rel == 'PYTHON/index.html':
        got = chapter_docs(rel, raw, 'Python Mastery')
        return got if got else [basic_doc(rel, raw)]
    return [basic_doc(rel, raw)]


# --------------------------------------------------------------------------
# The World's Wife Lab — 30 poems that live in one inline JS literal
# --------------------------------------------------------------------------
def englab_docs():
    rel = 'Eng learning/index.html'
    try:
        r = subprocess.run(['node', os.path.join('tools', 'englab_dump.mjs')],
                           cwd=ROOT, capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.SubprocessError) as e:
        print(f'  ! lit lab: could not run node ({e}) — poems skipped', file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f'  ! lit lab: dump failed: {r.stderr.strip()[:200]}', file=sys.stderr)
        return []
    try:
        poems = json.loads(r.stdout).get('poems', [])
    except ValueError as e:
        print(f'  ! lit lab: bad JSON ({e})', file=sys.stderr)
        return []

    docs = []
    for p in poems:
        if not p.get('title'):
            continue
        body = ' '.join([p.get('context', ''), p.get('text', ''),
                         ' '.join(p.get('passages', [])), p.get('analysis', '')])
        docs.append({
            'path': rel, 'hash': '#poem=' + str(p.get('id', '')),
            'title': p['title'], 'space': "The World's Wife Lab",
            'subject': (p.get('author') or 'Carol Ann Duffy'),
            'kind': 'poem', 'badge': 'poem',
            'heads': [], 'text': body[:POEM_CAP],
            'url': HUB + rel.replace(' ', '%20') + '#poem=' + str(p.get('id', '')),
        })
    return docs


# --------------------------------------------------------------------------
# BPhO — content that only exists as JS globals
# --------------------------------------------------------------------------
def bpho_docs():
    try:
        r = subprocess.run(['node', os.path.join('tools', 'bpho_dump.mjs')],
                           cwd=ROOT, capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.SubprocessError) as e:
        print(f'  ! bpho: could not run node ({e}) — BPhO content skipped', file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f'  ! bpho: dump failed: {r.stderr.strip()[:200]}', file=sys.stderr)
        return []
    try:
        data = json.loads(r.stdout)
    except ValueError as e:
        print(f'  ! bpho: bad JSON ({e})', file=sys.stderr)
        return []

    base = 'bpho/index.html'
    docs = []

    for d in data.get('plan', []):
        docs.append({
            'path': base, 'hash': '#/plan', 'title': "Day %s — %s" % (d['day'], d['title']),
            'space': 'BPhO Round 0', 'subject': 'BPhO', 'kind': 'plan',
            'badge': "Day %s · %s · %s min" % (d['day'], d['date'], d['mins']),
            'heads': [], 'text': (d['focus'] + ' ' + ' '.join(d['tasks']))[:TEXT_CAP],
            'url': HUB + base + '#/plan',
        })

    for m in data.get('modules', []):
        heads = [s['h'] for s in m.get('sections', [])]
        body = ' '.join([m.get('why', ''), m.get('warn', '')] +
                        [s['body'] for s in m.get('sections', [])])
        docs.append({
            'path': base, 'hash': '#/m/' + str(m['code']),
            'title': "Module %s — %s" % (m['code'], m['title']),
            'space': 'BPhO Round 0', 'subject': 'BPhO', 'kind': 'module',
            'badge': m.get('short') or ("Module %s" % m['code']),
            'heads': heads[:12], 'text': body[:CHAPTER_CAP],
            'url': HUB + base + '#/m/' + str(m['code']),
        })
        for ex in m.get('examples', []):
            if not ex.get('title'):
                continue
            docs.append({
                'path': base, 'hash': '#/m/' + str(m['code']),
                'title': ex['title'][:150],
                'space': 'BPhO Round 0', 'subject': 'BPhO', 'kind': 'example',
                'badge': 'worked example · M%s' % m['code'],
                'heads': [], 'text': ex.get('body', '')[:TEXT_CAP],
                'url': HUB + base + '#/m/' + str(m['code']),
            })

    for g in data.get('glossary', []):
        docs.append({
            'path': base, 'hash': '#/glossary',
            'title': g['en'], 'space': 'BPhO Round 0', 'subject': 'BPhO',
            'kind': 'glossary', 'badge': 'glossary',
            'heads': [], 'text': (g['def'] + ' ' + g['zh'])[:TEXT_CAP],
            'url': HUB + base + '#/glossary',
        })

    for q in data.get('questions', []):
        # '#/q/<id>', NOT '#/practice/<id>'. The practice route takes a MODULE code
        # (`viewPractice(code)` filters `q.module === code`), so a question id there
        # matches nothing and every question hit in the palette landed on the generic
        # practice index with "No questions match that filter." That silently broke
        # the deep link for all 200 questions -- the authored bank, the 25 past-paper
        # questions and the 12 sample questions alike. '#/q/<id>' is the route that
        # actually resolves a question, so it is what the index must emit.
        qid = str(q.get('id', ''))
        docs.append({
            'path': base, 'hash': '#/q/' + qid,
            'title': (q.get('q') or '')[:150] or ("Question %s" % qid),
            'space': 'BPhO Round 0', 'subject': 'BPhO', 'kind': 'bpho-question',
            'badge': ("%s · d%s" % (q.get('topic', ''), q.get('diff', ''))).strip(' ·'),
            'heads': [],
            'text': ' '.join([q.get('q', '')] + list(q.get('opts', [])))[:TEXT_CAP],
            'url': HUB + base + '#/q/' + qid,
        })
    return docs


# --------------------------------------------------------------------------
def main() -> int:
    docs = []
    for rel in tracked_html():
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full):
            continue
        raw = open(full, encoding='utf-8', errors='replace').read()
        if is_redirect_stub(raw):
            continue
        docs.extend(page_docs(rel, raw))

    bpho = bpho_docs()
    docs.extend(bpho)
    docs.extend(englab_docs())

    seen, uniq = set(), []
    for d in docs:
        k = (d['path'], d['hash'], d['title'])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(d)
    docs = uniq
    docs.sort(key=lambda d: (d['space'], d['kind'], d['title'].lower()))

    payload = json.dumps(docs, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('/* Generated by tools/build_search_index.py — do not edit by hand. */\n')
        f.write('window.DP_SEARCH_INDEX=' + payload + ';\n')
        meta = {'count': len(docs), 'bpho': len(bpho),
                'spaces': sorted({d['space'] for d in docs})}
        f.write('window.DP_SEARCH_META=' +
                json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ';\n')

    kb = os.path.getsize(OUT) / 1024
    print(f'Indexed {len(docs)} entries -> assets/js/search-index.js ({kb:.0f} KB)')
    by_space = {}
    for d in docs:
        by_space[d['space']] = by_space.get(d['space'], 0) + 1
    for k in sorted(by_space, key=lambda x: -by_space[x]):
        print(f"  {k:<28} {by_space[k]:>5}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
