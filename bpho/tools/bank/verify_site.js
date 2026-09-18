/* End-to-end check that the drill bank is actually wired into the study site.
   "The file was written" is not the same as "the page works" -- this drives a real
   browser over the local server and asserts what a student would see.

   Run from bpho/:  node tools/bank/verify_site.js [base-url]
   Default base is the local static server on 127.0.0.1:8901, which is rooted at the whole
   DP site -- so the study space is /bpho/index.html, not /index.html. Pass the Pages URL
   to check the deployed copy instead:
     node tools/bank/verify_site.js https://sbk283074-creator.github.io/dp-study-site/bpho/index.html

   The sections to check are DISCOVERED from the page, not listed here.  The first version
   hardcoded `TAG = 'BANK-S01'`, which meant that publishing section 2 would have been
   verified by a script that never looked at it.  Discovering the tags from
   window.BPHO_QUESTIONS means every section that ships is checked by construction, and
   the script needs no edit for sections 3 through 40.

   It also checks the papers area: that every card matches the generated manifest, and
   that every download link fetches a file whose first bytes really are %PDF-.
*/
const { chromium } = require('/Users/lucas.ma/.workbuddy-ai/binaries/node/workspace/node_modules/playwright-core');

const BASE = process.argv[2] || 'http://127.0.0.1:8901/bpho/index.html';
const FIG_MIN = 8;            // spec.FIG_MIN -- the same floor the gate enforces

/* The directory BASE sits in, so a download link can be fetched.  The PDF paths in
   data/papers.js are relative to index.html ("papers/x.pdf"), which is what makes them
   work over file:// as well as over Pages, so the check has to resolve them the same way
   the browser does rather than gluing them onto BASE. */
const DIR = /\/[^/]*\.[^/]*$/.test(BASE) ? BASE.replace(/[^/]*$/, '') : BASE.replace(/\/?$/, '/');

let fails = 0;
function ok(cond, label, extra) {
  console.log((cond ? '  ok   ' : '  FAIL ') + label + (extra ? '   ' + extra : ''));
  if (!cond) fails++;
}

async function go(page, hash) {
  await page.evaluate(h => { location.hash = h; }, hash);
  await page.waitForTimeout(320);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));

  console.log('drill bank end-to-end\n');

  await page.goto(BASE, { waitUntil: 'load' });
  await page.waitForTimeout(500);

  const tags = await page.evaluate(() => {
    const qs = window.BPHO_QUESTIONS || [];
    return [...new Set(qs.filter(q => /^BANK-S\d+$/.test(q.paper || '')).map(q => q.paper))]
      .sort();
  });
  ok(tags.length > 0, 'at least one bank section is loaded', tags.join(', '));
  if (!tags.length) { await browser.close(); process.exit(1); }

  for (const TAG of tags) {
    const sec = Number(TAG.replace('BANK-S', ''));
    console.log('\n--- ' + TAG + ' ---');

    // ── 1. the data file loaded and joined the shared bank ──────────────────
    const info = await page.evaluate(tag => {
      const qs = window.BPHO_QUESTIONS || [];
      const bank = qs.filter(q => q.paper === tag);
      return {
        total: qs.length,
        bank: bank.length,
        figs: bank.filter(q => /<svg/.test(q.q)).length,
        traps: bank.filter(q => q.trap).length,
        ids: bank.map(q => q.id),
        firstFig: (bank.find(q => /<svg/.test(q.q)) || {}).id || null
      };
    }, TAG);
    ok(info.bank === 25, 'the bank file contributed 25 questions',
       JSON.stringify({ total: info.total, bank: info.bank }));
    ok(info.figs >= FIG_MIN, 'at least ' + FIG_MIN + ' carry an inline figure', 'got ' + info.figs);
    ok(info.traps === 25, 'every one carries a trap note', 'got ' + info.traps);
    ok(new Set(info.ids).size === info.bank, 'their ids are unique');

    // ── 2. the practice page offers the section ─────────────────────────────
    await go(page, '#/practice');
    const prac = await page.evaluate(tag => {
      const m = document.getElementById('main');
      const chip = m.querySelector('[data-chip][data-val="' + tag + '"]');
      return {
        chip: !!chip,
        chipText: chip ? chip.innerText : '',
        launch: !!m.querySelector('[data-act="mockbank"][data-code="' + tag + '"]'),
        untimed: !!m.querySelector('[data-act="mockbanku"][data-code="' + tag + '"]'),
        rawTagShown: m.innerText.indexOf(tag) >= 0
      };
    }, TAG);
    ok(prac.chip, 'a filter chip for the section exists');
    ok(new RegExp('Drill bank section ' + sec + '\\b').test(prac.chipText),
       'the chip is labelled in English, not a raw tag', JSON.stringify(prac.chipText));
    ok(prac.launch && prac.untimed, 'both mock launchers exist');
    ok(!prac.rawTagShown, 'the raw tag is never shown to the reader');

    // ── 3. the chip filters the list to just that section ───────────────────
    await page.click('[data-chip][data-val="' + TAG + '"]');
    await page.waitForTimeout(320);
    const filtered = await page.evaluate(() => {
      const m = document.getElementById('main').innerText.match(/(\d+)\s+questions shown/);
      return m ? Number(m[1]) : -1;
    });
    ok(filtered === 25, 'the chip narrows the list to 25', 'got ' + filtered);

    // ── 4. the launcher builds a real 25-question timed mock ────────────────
    await page.click('[data-act="mockbank"][data-code="' + TAG + '"]');
    await page.waitForTimeout(450);
    const mock = await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('bpho-r0-v1') || '{}');
      return { n: s.mock ? s.mock.ids.length : 0, paper: s.mock ? s.mock.paper : null,
               sec: s.mock ? s.mock.seconds : 0 };
    });
    ok(mock.n === 25, 'the mock holds 25 questions', 'got ' + mock.n);
    ok(mock.paper === TAG, 'the mock is tagged with the section', String(mock.paper));
    ok(mock.sec === 3600, "the clock is 60 minutes, the paper's own pace", mock.sec + 's');

    // ── 5. a figure-bearing question renders a real, non-zero figure ────────
    if (info.firstFig) {
      await go(page, '#/q/' + info.firstFig);
      const fig = await page.evaluate(() => {
        const m = document.getElementById('main');
        const svg = m.querySelector('.fig svg');
        const r = svg ? svg.getBoundingClientRect() : null;
        return { sub: (m.querySelector('.sub') || {}).innerText || '', has: !!svg,
                 w: r ? Math.round(r.width) : 0, h: r ? Math.round(r.height) : 0,
                 vb: svg ? svg.getAttribute('viewBox') : null };
      });
      ok(fig.has && fig.w > 120 && fig.h > 60, 'the figure renders at a real size',
         fig.w + 'x' + fig.h + ' ' + fig.vb);
      const qn = Number(info.firstFig.split('-')[1]);
      ok(new RegExp('Drill bank section ' + sec + ', question ' + qn + '\\b').test(fig.sub),
         'the long label reads properly', JSON.stringify(fig.sub));
    }

    // ── 6. the result page judges a bank section as a full 25-question paper ─
    await go(page, '#/practice');
    await page.click('[data-act="mockbanku"][data-code="' + TAG + '"]');
    await page.waitForTimeout(400);
    const nOpts = await page.evaluate(() => document.querySelectorAll('[data-mock]').length);
    for (let i = 0; i < nOpts; i += 5) {
      await page.evaluate(idx => {
        const b = document.querySelectorAll('[data-mock]')[idx];
        if (b) b.click();
      }, i);
      await page.waitForTimeout(45);
    }
    await page.click('[data-act="marksubmit"]');
    await page.waitForTimeout(450);
    const res = await page.evaluate(() => document.getElementById('main').innerText);
    ok(/qualifying line/.test(res), 'the result is judged against the 11/25 line');
    ok(!/style check/.test(res), 'and it is NOT described as a short style check');
    ok(/(\d+)\s*\/\s*25\s*correct/.test(res), 'a score out of 25 is reported');
  }

  // ── 7. the papers area, and that every download link is a real file ────────
  /* "The PDFs exist" and "the download works" are different claims.  This fetches every
     link the page offers and checks the first five bytes, because a rendered download
     page pointing at a 404 looks perfectly fine and is worse than no page at all.  It
     also cross-checks each paper's question count against the live bank -- the PDFs are
     built from that same data, so a mismatch means the papers are stale. */
  console.log('\n--- papers & downloads ---');
  await go(page, '#/papers');
  const pap = await page.evaluate(() => {
    const m = document.getElementById('main');
    const nav = document.querySelector('.navlink[data-view="papers"]');
    return {
      nav: nav ? nav.classList.contains('on') : null,
      h1: (m.querySelector('h1') || {}).textContent || '',
      man: window.BPHO_PAPERS || [],
      cards: [...m.querySelectorAll('.paper')].map(c => ({
        title: c.querySelector('.paper__t').textContent.trim(),
        flag: c.querySelector('.flag').textContent.trim(),
        dl: [...c.querySelectorAll('a[download]')].map(a => a.getAttribute('href')),
      })),
    };
  });
  ok(pap.man.length > 0, 'the PDF manifest loaded', pap.man.length + ' paper(s)');
  ok(pap.nav === true, 'the nav entry highlights on this route');
  ok(pap.cards.length === pap.man.length, 'one card per manifest entry',
     pap.cards.length + ' cards / ' + pap.man.length + ' entries');

  /* The reverse direction, which is the one that actually breaks in practice: every
     drill-bank section in the bank must have a built PDF.  A manifest that is merely
     MISSING a section produces a page that still looks complete and correct, so nothing
     else would ever catch "added section 4, forgot to rebuild the PDFs".  This is the
     check that makes forgetting loud. */
  const missing = tags.filter(t => !pap.man.some(p => p.tag === t));
  ok(missing.length === 0,
     'every bank section has a built PDF (node tools/papers/build_pdfs.js)',
     missing.length ? 'MISSING: ' + missing.join(', ') : tags.length + ' sections, all present');

  for (const p of pap.man) {
    const card = pap.cards.find(c => c.title === p.label);
    ok(!!card, p.tag + ': has a card');
    if (!card) continue;

    ok(card.dl.length === 2, p.tag + ': offers exactly two downloads', card.dl.join(', '));
    const official = p.kind === 'official';
    ok(official ? /Official BPhO/.test(card.flag) : /Original/.test(card.flag),
       p.tag + ': the provenance badge is right', JSON.stringify(card.flag));

    for (const href of card.dl) {
      const r = await page.request.get(DIR + href);
      const body = await r.body();
      const magic = body.slice(0, 5).toString('latin1');
      ok(r.status() === 200 && magic === '%PDF-',
         p.tag + ': ' + href + ' is a real PDF',
         r.status() + ' ' + Math.round(body.length / 1024) + 'KB ' + magic);
    }

    const live = await page.evaluate(tag =>
      (window.BPHO_QUESTIONS || []).filter(q => q.paper === tag).length, p.tag);
    ok(live === p.n, p.tag + ': the PDF count matches the live bank', p.n + ' vs ' + live);
  }

  // ── 8. nothing threw along the way ────────────────────────────────────────
  console.log('');
  ok(errors.length === 0, 'no console or page errors', errors.slice(0, 4).join(' | '));

  await browser.close();
  console.log('\n' + (fails ? 'FAILED: ' + fails + ' check(s)' : 'all checks passed'));
  process.exit(fails ? 1 : 0);
})();
