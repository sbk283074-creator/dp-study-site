/* ==========================================================================
   DP Learning Platform — app shell
   Renders sidebar nav, breadcrumbs, prev/next links, progress tracking
   (localStorage), keyboard search, heading anchors and theme toggle.
   ========================================================================== */

/* ---------- Navigation model ---------------------------------------------- */
const NAV = [
  {
    id: 'start', group: 'Start here', dot: 'var(--accent)', open: true,
    items: [
      { p: 'index.html', t: 'Dashboard', n: '00' },
      { p: 'study-plan.html', t: 'Study plan & exam technique', n: '01' },
      { p: 'exam-toolkit.html', t: 'Command terms & calculator skills', n: '02' }
    ]
  },
  {
    id: 'math', group: 'Mathematics AA HL', dot: '#3653d6', open: true,
    meta: 'P1 30% · P2 30% · P3 20% · Exploration 20%',
    items: [
      { p: 'math/index.html', t: 'Overview, assessment & connections', n: '00' },
      { p: 'math/01-number-algebra.html', t: 'Number & algebra', n: '01' },
      { p: 'math/02-functions.html', t: 'Functions', n: '02' },
      { p: 'math/03-geometry-trigonometry.html', t: 'Geometry & trigonometry', n: '03' },
      { p: 'math/04-statistics-probability.html', t: 'Statistics & probability', n: '04' },
      { p: 'math/05-calculus.html', t: 'Calculus', n: '05' },
      { p: 'math/06-ia-exploration.html', t: 'The exploration (IA)', n: 'IA' }
    ]
  },
  {
    id: 'physics', group: 'Physics HL', dot: '#0a6f80', open: true,
    meta: 'P1 36% · P2 44% · Investigation 20%',
    items: [
      { p: 'physics/index.html', t: 'Overview, assessment & toolkit', n: '00' },
      { p: 'physics/A-space-time-motion.html', t: 'A · Space, time & motion', n: 'A' },
      { p: 'physics/B-particulate-matter.html', t: 'B · The particulate nature of matter', n: 'B' },
      { p: 'physics/C-wave-behaviour.html', t: 'C · Wave behaviour', n: 'C' },
      { p: 'physics/D-fields.html', t: 'D · Fields', n: 'D' },
      { p: 'physics/E-nuclear-quantum.html', t: 'E · Nuclear & quantum physics', n: 'E' },
      { p: 'physics/F-skills-ia.html', t: 'F · Practical scheme, skills & IA', n: 'F' }
    ]
  },
  {
    id: 'cs', group: 'Computer Science HL', dot: '#7a5a13', open: true,
    meta: 'P1 40% · P2 40% · IA 20% · new 2027 guide',
    items: [
      { p: 'cs/index.html', t: 'Overview & assessment', n: '00' },
      { p: 'cs/A1-computer-fundamentals.html', t: 'A1 · Computer fundamentals', n: 'A1' },
      { p: 'cs/A2-networks.html', t: 'A2 · Networks', n: 'A2' },
      { p: 'cs/A3-databases.html', t: 'A3 · Databases', n: 'A3' },
      { p: 'cs/A4-machine-learning.html', t: 'A4 · Machine learning', n: 'A4' },
      { p: 'cs/B1-computational-thinking.html', t: 'B1 · Computational thinking', n: 'B1' },
      { p: 'cs/B2-programming.html', t: 'B2 · Programming', n: 'B2' },
      { p: 'cs/B3-oop.html', t: 'B3 · Object-oriented programming', n: 'B3' },
      { p: 'cs/B4-abstract-data-types.html', t: 'B4 · Abstract data types (HL)', n: 'B4' },
      { p: 'cs/case-study.html', t: 'Paper 1 · The pre-seen case study', n: 'CS' },
      { p: 'cs/ia-solution.html', t: 'IA · The computational solution', n: 'IA' },
      { p: 'cs/collaborative-project.html', t: 'Collaborative sciences project', n: 'CP' }
    ]
  },
  {
    id: 'english', group: 'English A: Lang & Lit SL', dot: '#b03060', open: false,
    meta: 'P1 35% · P2 35% · IO 30%',
    items: [
      { p: 'english/index.html', t: 'Overview & assessment', n: '00' },
      { p: 'english/paper1.html', t: 'Paper 1 — textual analysis', n: 'P1' },
      { p: 'english/paper2.html', t: 'Paper 2 — comparative essay', n: 'P2' },
      { p: 'english/individual-oral.html', t: 'The individual oral (IO)', n: 'IO' },
      { p: 'english/work-chronicle.html', t: 'Chronicle of a Death Foretold', n: 'W1' },
      { p: 'english/work-othello.html', t: 'Othello', n: 'W2' },
      { p: 'english/work-sense-of-ending.html', t: 'The Sense of an Ending', n: 'W3' },
      { p: 'english/work-worlds-wife.html', t: 'The World\'s Wife', n: 'W4' }
    ]
  },
  {
    id: 'chinese', group: 'Chinese A: Lang & Lit SL', dot: '#c0392b', open: false,
    meta: 'Paper 1 35% · Paper 2 35% · IO 30%',
    items: [
      { p: 'chinese/index.html', t: 'Overview & assessment', n: '00' },
      { p: 'chinese/paper1.html', t: 'Paper 1 — textual analysis', n: 'P1' },
      { p: 'chinese/paper2.html', t: 'Paper 2 — comparative essay', n: 'P2' },
      { p: 'chinese/individual-oral.html', t: 'Individual oral (IO)', n: 'IO' },
      { p: 'chinese/work-shengsi-pilao.html', t: 'Life and Death Are Wearing Me Out (Mo Yan)', n: 'W1' },
      { p: 'chinese/work-kelara.html', t: 'Klara and the Sun (Ishiguro)', n: 'W2' },
      { p: 'chinese/work-mudanting.html', t: 'The Peony Pavilion (Tang Xianzu)', n: 'W3' },
      { p: 'chinese/work-wanwu-jingmo.html', t: 'A Silence Like No Other (Yi Sha)', n: 'W4' }
    ]
  },
  {
    id: 'business', group: 'Business management SL', dot: '#1d7a4c', open: false,
    meta: 'P1 35% · P2 35% · research project 30%',
    items: [
      { p: 'business/index.html', t: 'How the course works', n: '00' },
      { p: 'business/01-introduction-to-business-management.html', t: 'Unit 1 · Introduction to business management', n: 'U1' },
      { p: 'business/02-human-resource-management.html', t: 'Unit 2 · Human resource management', n: 'U2' },
      { p: 'business/03-finance-and-accounts.html', t: 'Unit 3 · Finance and accounts', n: 'U3' },
      { p: 'business/04-marketing.html', t: 'Unit 4 · Marketing', n: 'U4' },
      { p: 'business/05-operations-management.html', t: 'Unit 5 · Operations management', n: 'U5' },
      { p: 'business/06-toolkit.html', t: 'The toolkit (8 SL tools)', n: 'TK' },
      { p: 'business/07-research-project.html', t: 'The research project (IA, 30%)', n: 'IA' }
    ]
  },
  {
    id: 'core', group: 'DP core · TOK, EE & CAS', dot: '#6d4c7d', open: false,
    meta: 'TOK essay + exhibition · EE 30 marks · CAS pass/fail',
    items: [
      { p: 'core/index.html', t: 'The DP core: how it all fits', n: '00' },
      { p: 'core/tok-course.html', t: 'TOK — the course', n: 'T1' },
      { p: 'core/tok-essay.html', t: 'TOK — the essay (1,600 words)', n: 'T2' },
      { p: 'core/tok-exhibition.html', t: 'TOK — the exhibition', n: 'T3' },
      { p: 'core/ee-choosing.html', t: 'EE — pathway & research question', n: 'E1' },
      { p: 'core/ee-writing.html', t: 'EE — research, writing & criteria', n: 'E2' },
      { p: 'core/ee-subjects.html', t: 'EE — in your subjects', n: 'E3' },
      { p: 'core/cas-basics.html', t: 'CAS — the requirement', n: 'C1' },
      { p: 'core/cas-project.html', t: 'CAS — the project', n: 'C2' },
      { p: 'core/cas-portfolio.html', t: 'CAS — reflection & portfolio', n: 'C3' }
    ]
  }
];

/* Flat lookup -------------------------------------------------------------- */
const PAGES = [];
NAV.forEach(g => g.items.forEach(i => PAGES.push({ ...i, group: g.group, gid: g.id, dot: g.dot })));

/* ---------- Helpers -------------------------------------------------------- */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const norm = p => p.replace(/^\.\//, '').replace(/index\.html$/, '').replace(/\/$/, '') || 'index.html';
const pageKey = p => p.replace(/\.html$/, '').replace(/\//g, '__');
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};

function depthPrefix() {
  // how many folders deep is this page? used to build asset paths
  const rel = location.pathname.split('/').filter(Boolean);
  return ''; // document-relative resolution handled by relative paths per file
}

/* ---------- Sidebar -------------------------------------------------------- */
function currentPath() {
  const full = location.pathname.split('/');
  const file = full[full.length - 1] || 'index.html';
  const parent = full[full.length - 2] || '';
  const known = ['math', 'physics', 'cs', 'english', 'chinese'];
  return known.includes(parent) ? parent + '/' + file : file;
}

function renderSidebar() {
  const root = $('#sidebar'); if (!root) return;
  const cur = currentPath();
  const done = store.get('dp.done', {});
  const html = NAV.map(g => {
    const items = g.items.map(i => {
      const k = pageKey(norm(i.p));
      const isDone = !!done[k];
      const active = norm(i.p) === cur ? ' aria-current="page"' : '';
      return `<a class="navitem" href="${hrefTo(i.p)}"${active} data-key="${k}">
        <span class="navitem__num">${i.n}</span>
        <span>${i.t}</span>
        ${isDone ? '<span class="navitem__check">✓</span>' : ''}
      </a>`;
    }).join('');
    return `<div class="navgroup" data-open="${g.open}" data-gid="${g.id}">
      <button class="navgroup__head" type="button">
        <span class="navgroup__dot" style="background:${g.dot}"></span>
        <span>${g.group}</span>
        <span class="navgroup__chev">▼</span>
      </button>
      ${g.meta ? `<div class="navgroup__meta">${g.meta}</div>` : ''}
      <div class="navgroup__items">${items}</div>
    </div>`;
  }).join('');
  root.innerHTML = html;
  root.querySelectorAll('.navgroup__head').forEach(b => {
    b.addEventListener('click', () => {
      const grp = b.parentElement;
      const open = grp.getAttribute('data-open') === 'true';
      grp.setAttribute('data-open', String(!open));
      const g = NAV.find(x => x.id === grp.dataset.gid); if (g) g.open = !open;
      store.set('dp.nav', NAV.map(x => [x.id, x.open]));
    });
  });
  const saved = store.get('dp.nav', null);
  if (saved) {
    const m = new Map(saved);
    root.querySelectorAll('.navgroup').forEach(el => {
      if (m.has(el.dataset.gid)) el.setAttribute('data-open', String(m.get(el.dataset.gid)));
    });
  }
  const active = root.querySelector('[aria-current="page"]');
  if (active) { const g = active.closest('.navgroup'); if (g) g.setAttribute('data-open', 'true'); }
}

/* Relative href from current page to target site-root-relative path */
function hrefTo(target) {
  const full = location.pathname;
  const here = full.substring(0, full.lastIndexOf('/'));
  const segs = here.split('/').filter(Boolean);
  const rootIdx = segs.length ? -1 : 0;
  // count how many segments of `here` come after the site root:
  // site root is the folder containing assets/ -> find by known subject dirs
  const known = ['math', 'physics', 'cs', 'english', 'chinese'];
  let up = 0;
  for (let i = segs.length - 1; i >= 0; i--) { if (known.includes(segs[i])) up++; }
  return '../'.repeat(up) + target;
}

/* ---------- Breadcrumbs ---------------------------------------------------- */
function renderCrumbs() {
  const el = $('#crumbs'); if (!el) return;
  const cur = currentPath();
  const p = PAGES.find(x => norm(x.p) === cur);
  const parts = [`<a href="${hrefTo('index.html')}">DP Learning</a>`];
  if (p) parts.push(`<span class="sep">/</span><a href="${hrefTo(PAGES.find(x => x.gid === p.gid).p)}">${p.group}</a>`);
  parts.push(`<span class="sep">/</span><span class="current">${p ? p.t : (document.title || 'Page')}</span>`);
  el.innerHTML = parts.join(' ');
}

/* ---------- Prev / next ---------------------------------------------------- */
function ensureEl(id, cls) {
  let el = document.getElementById(id);
  if (!el) {
    el = document.createElement('div');
    el.id = id; el.className = cls;
    const host = $('#content') || document.body;
    host.appendChild(el);
  }
  return el;
}

function renderPagenav() {
  const el = ensureEl('pagenav', 'pagenav');
  const cur = currentPath();
  const i = PAGES.findIndex(x => norm(x.p) === cur);
  if (i < 0) return;
  const prev = PAGES[i - 1], next = PAGES[i + 1];
  el.innerHTML = `
    <a class="prev" href="${prev ? hrefTo(prev.p) : '#'}">
      <div class="pagenav__dir">← Previous</div>
      <div class="pagenav__title">${prev ? prev.t : '—'}</div>
    </a>
    <a class="next" href="${next ? hrefTo(next.p) : '#'}">
      <div class="pagenav__dir">Next →</div>
      <div class="pagenav__title">${next ? next.t : '—'}</div>
    </a>`;
}

/* ---------- Heading anchors ------------------------------------------------ */
function addAnchors() {
  const seen = new Map();
  $$('.content h2, .content h3').forEach(h => {
    if (h.querySelector('.anchor')) return;
    let id = (h.textContent || '').trim().toLowerCase()
      .replace(/[^\p{L}\p{N}\s-]/gu, '').replace(/\s+/g, '-').slice(0, 60);
    if (!id) id = 'h' + Math.random().toString(36).slice(2, 7);
    if (seen.has(id)) { seen.set(id, seen.get(id) + 1); id = id + '-' + seen.get(id); } else seen.set(id, 1);
    h.id = id;
    const a = document.createElement('a');
    a.className = 'anchor'; a.href = '#' + id; a.textContent = '#';
    h.appendChild(a);
  });
}

/* ---------- Progress ------------------------------------------------------- */
function progressAll() {
  const done = store.get('dp.done', {});
  return { n: PAGES.filter(p => done[pageKey(norm(p.p))]).length, total: PAGES.length };
}
function progressGroup(gid) {
  const done = store.get('dp.done', {});
  const items = PAGES.filter(p => p.gid === gid);
  return { n: items.filter(p => done[pageKey(norm(p.p))]).length, total: items.length };
}
function renderProgressChip() {
  const el = $('#progress-chip'); if (!el) return;
  const { n, total } = progressAll();
  const pct = Math.round(100 * n / total);
  el.innerHTML = `<div class="progress-chip__bar"><div class="progress-chip__fill" style="width:${pct}%"></div></div><span>${n}/${total} pages</span>`;
  el.title = `${pct}% of pages marked complete`;
}
function setDone(key, val) {
  const done = store.get('dp.done', {});
  if (val) done[key] = Date.now(); else delete done[key];
  store.set('dp.done', done);
  renderProgressChip(); renderSidebar(); refreshCompleteBtn();
}

/* ---------- Page completion button ---------------------------------------- */
function keyOfCurrent() { return pageKey(norm(currentPath())); }
function refreshCompleteBtn() {
  const btn = $('#complete-btn'); if (!btn) return;
  const done = !!store.get('dp.done', {})[keyOfCurrent()];
  btn.dataset.done = String(done);
  btn.textContent = done ? '✓ Completed — click to reset' : 'Mark this page complete';
  btn.classList.toggle('btn--primary', !done);
}
function renderPageClose() {
  const el = ensureEl('pageclose', 'pageclose');
  const cur = currentPath();
  const p = PAGES.find(x => norm(x.p) === cur);
  el.innerHTML = `<p class="pageclose__text"><strong>Self-check:</strong> can you do the practice questions on this page closed-book? If not, re-read the derivations and retry in 48 hours (spaced repetition beats re-reading).</p>
    <button id="complete-btn" class="btn btn--primary" type="button">Mark this page complete</button>
    <button id="print-btn" class="btn" type="button">Print / save as PDF</button>`;
  $('#complete-btn').addEventListener('click', () => setDone(keyOfCurrent(), !store.get('dp.done', {})[keyOfCurrent()]));
  $('#print-btn').addEventListener('click', () => window.print());
  refreshCompleteBtn();
}

/* ---------- Checklists (persisted) ---------------------------------------- */
function wireChecklists() {
  $$('.checklist').forEach(list => {
    const base = 'dp.cl.' + keyOfCurrent() + '.';
    const boxes = $$('input[type=checkbox]', list);
    const saved = store.get(base + 'v', []);
    boxes.forEach((b, i) => { if (saved[i]) b.checked = true; });
    boxes.forEach((b, i) => b.addEventListener('change', () => {
      const arr = $$('input[type=checkbox]', list).map(x => x.checked);
      store.set(base + 'v', arr);
    }));
  });
}

/* ---------- Search --------------------------------------------------------- */
let INDEX = [];
function loadIndex() {
  if (window.DP_SEARCH_INDEX) { INDEX = window.DP_SEARCH_INDEX; return; }
  const s = document.createElement('script');
  s.src = hrefTo('assets/js/search-index.js');
  document.head.appendChild(s);
}
function search(q) {
  const terms = q.toLowerCase().split(/\s+/).filter(t => t.length > 1);
  if (!terms.length) return [];
  const scored = [];
  INDEX.forEach(doc => {
    let score = 0, snip = '';
    const title = doc.title.toLowerCase();
    const heads = (doc.heads || []).join(' | ').toLowerCase();
    const text = (doc.text || '').toLowerCase();
    terms.forEach(t => {
      if (title.includes(t)) score += 12;
      if (heads.includes(t)) score += 7;
      const idx = text.indexOf(t);
      if (idx >= 0) { score += 2; if (!snip) snip = (doc.text || '').slice(Math.max(0, idx - 70), idx + 150); }
    });
    if (score > 0) scored.push({ doc, score, snip: snip || (doc.text || '').slice(0, 160) });
  });
  return scored.sort((a, b) => b.score - a.score).slice(0, 12);
}
function renderResults(q) {
  const box = $('#results'); if (!box) return;
  if (!q.trim()) { box.hidden = true; box.innerHTML = ''; return; }
  const res = search(q);
  box.hidden = false;
  if (!res.length) { box.innerHTML = `<div class="results__empty">No results. The index loads after the first search — try again in a second.</div>`; return; }
  box.innerHTML = res.map(r => {
    const d = r.doc;
    const url = hrefTo(d.path) ;
    return `<a class="results__item" href="${url}">
      <div class="results__path">${(d.subject || '')}</div>
      <div class="results__title">${escapeHtml(d.title)}</div>
      <div class="results__snip">${escapeHtml(r.snip.replace(/\s+/g, ' '))}</div>
    </a>`;
  }).join('');
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function wireSearch() {
  const input = $('#search-input'); if (!input) return;
  input.addEventListener('input', () => { if (!INDEX.length && window.DP_SEARCH_INDEX) INDEX = window.DP_SEARCH_INDEX; renderResults(input.value); });
  input.addEventListener('focus', () => { if (!INDEX.length) loadIndex(); if (input.value) renderResults(input.value); });
  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') { input.value = ''; renderResults(''); input.blur(); }
    if (e.key === 'Enter') { const first = $('#results .results__item'); if (first) location.href = first.getAttribute('href'); }
  });
  document.addEventListener('click', e => { if (!e.target.closest('.searchbox')) { const b = $('#results'); if (b) b.hidden = true; } });
  document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); input.focus(); }
    if (e.key === '/' && document.activeElement !== input && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
  });
}

/* ---------- Theme ---------------------------------------------------------- */
function wireTheme() {
  const btn = $('#theme-btn'); if (!btn) return;
  const cur = store.get('dp.theme', 'light');
  document.documentElement.setAttribute('data-theme', cur);
  btn.textContent = cur === 'dark' ? '☀' : '☾';
  btn.title = 'Toggle light / dark';
  btn.addEventListener('click', () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    store.set('dp.theme', next);
    btn.textContent = next === 'dark' ? '☀' : '☾';
  });
}

/* ---------- Dashboard ------------------------------------------------------ */
const SUBJ_COLORS = { start: '#42506b', math: '#3653d6', physics: '#0a6f80', cs: '#7a5a13', english: '#b03060', chinese: '#c0392b', business: '#1d7a4c', core: '#6d4c7d' };
function renderDashboard() {
  const el = document.getElementById('dashboard');
  if (!el) return;
  const done = store.get('dp.done', {});
  const groups = NAV.filter(g => g.id !== 'start' && g.id !== 'qbank');
  el.innerHTML = groups.map(g => {
    const items = PAGES.filter(p => p.gid === g.id);
    const n = items.filter(p => done[pageKey(norm(p.p))]).length;
    const pct = Math.round(100 * n / items.length);
    const colour = SUBJ_COLORS[g.id] || g.dot;
    return `<a class="subject-card" style="--c:${colour}" href="${hrefTo(g.items[0].p)}">
      <div class="subject-card__meta">${g.meta || ''}</div>
      <h3>${g.group}</h3>
      <p>${items.length} pages · ${g.id === 'core' ? 'exemplars, step-by-step method, practice tasks' : 'derivations, worked examples, practice questions'}</p>
      <div class="subject-card__bar"><div class="subject-card__fill" style="width:${pct}%"></div></div>
      <div class="subject-card__pct">${n} / ${items.length} pages complete (${pct}%)</div>
    </a>`;
  }).join('');
}

/* ---------- Dashboard stats ------------------------------------------------ */
function renderStats() {
  const el = document.getElementById('stat-row'); if (!el) return;
  const done = store.get('dp.done', {});
  const n = PAGES.filter(p => p.gid !== 'qbank' && done[pageKey(norm(p.p))]).length;
  const total = PAGES.filter(p => p.gid !== 'qbank').length;
  const weeks = Math.max(0, Math.round((new Date('2028-04-25') - new Date()) / 6048e5));
  el.innerHTML = `
    <div class="stat"><div class="stat__n">${n}<span style="font-size:.9rem;color:var(--muted)">/${total}</span></div><div class="stat__l">Pages complete</div></div>
    <div class="stat"><div class="stat__n">6</div><div class="stat__l">Subjects + core</div></div>
    <div class="stat"><div class="stat__n">${weeks}</div><div class="stat__l">Weeks to exams</div></div>
    <div class="stat"><div class="stat__n">${Math.round(100 * n / total)}%</div><div class="stat__l">Syllabus covered</div></div>`;
}

/* ---------- Boot ----------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  // Build the app chrome. Pages may wrap their content in #app-shell, or not —
  // either way everything visible ends up inside .content.
  let inner = '';
  const shell = document.getElementById('app-shell');
  if (shell) {
    inner = shell.innerHTML;
    shell.remove();
  } else {
    const kids = Array.from(document.body.children).filter(el => el.tagName !== 'SCRIPT');
    inner = kids.map(el => el.outerHTML).join('');
    kids.forEach(el => el.remove());
  }
  const wrap = document.createElement('div');
  wrap.innerHTML = `
      <header class="topbar">
        <button class="iconbtn" id="menu-btn" type="button" aria-label="Menu">☰</button>
        <a class="topbar__brand" href="${hrefTo('index.html')}"><span class="topbar__logo">DP</span><span>IB Learning System</span></a>
        <nav class="crumbs" id="crumbs"></nav>
        <div class="topbar__spacer"></div>
        <div class="searchbox">
          <input id="search-input" type="search" placeholder="Search all subjects…" autocomplete="off" />
          <kbd>⌘K</kbd>
          <div class="results" id="results" hidden></div>
        </div>
        <div class="progress-chip" id="progress-chip"></div>
        <button class="iconbtn" id="theme-btn" type="button" aria-label="Toggle theme">☾</button>
      </header>
      <aside class="sidebar" id="sidebar"></aside>
      <div class="main"><div class="content" id="content">${inner}</div></div>`;
  while (wrap.firstChild) document.body.appendChild(wrap.firstChild);
  renderSidebar(); renderCrumbs(); renderPagenav(); addAnchors();
  renderProgressChip(); renderPageClose(); wireChecklists(); wireSearch(); wireTheme();
  renderDashboard(); renderStats();
  const mb = $('#menu-btn');
  if (mb) mb.addEventListener('click', () => {
    const open = document.body.getAttribute('data-nav') === 'open';
    document.body.setAttribute('data-nav', open ? '' : 'open');
  });
});
