/* End-to-end check that the drill bank is actually wired into the study site.
   "The file was written" is not the same as "the page works" -- this drives a real
   browser over the local server and asserts what a student would see.

   Run from bpho/:  node tools/bank/verify_site.js [base-url]
   Default base is the local static server on 127.0.0.1:8901, which is rooted at the whole
   DP site -- so the study space is /bpho/index.html, not /index.html. Pass the Pages URL
   to check the deployed copy instead:
     node tools/bank/verify_site.js https://sbk283074-creator.github.io/dp-study-site/bpho/index.html
*/
const { chromium } = require('/Users/lucas.ma/.workbuddy-ai/binaries/node/workspace/node_modules/playwright-core');

const BASE = process.argv[2] || 'http://127.0.0.1:8901/bpho/index.html';
const TAG = 'BANK-S01';

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

  // ── 1. the data file loaded and joined the shared bank ────────────────────
  await page.goto(BASE, { waitUntil: 'load' });
  await page.waitForTimeout(500);
  const info = await page.evaluate(tag => {
    const qs = window.BPHO_QUESTIONS || [];
    const bank = qs.filter(q => q.paper === tag);
    return {
      total: qs.length,
      bank: bank.length,
      figs: bank.filter(q => /<svg/.test(q.q)).length,
      traps: bank.filter(q => q.trap).length,
      ids: bank.map(q => q.id)
    };
  }, TAG);
  ok(info.bank === 25, 'the bank file contributed 25 questions', JSON.stringify({ total: info.total, bank: info.bank }));
  ok(info.figs === 15, '15 of them carry an inline figure', 'got ' + info.figs);
  ok(info.traps === 25, 'every one carries a trap note', 'got ' + info.traps);
  ok(new Set(info.ids).size === 25, 'their ids are unique');

  // ── 2. the practice page offers the section ───────────────────────────────
  await go(page, '#/practice');
  const prac = await page.evaluate(tag => {
    const m = document.getElementById('main');
    return {
      chip: !!m.querySelector('[data-chip][data-val="' + tag + '"]'),
      chipText: (m.querySelector('[data-chip][data-val="' + tag + '"]') || {}).innerText || '',
      launch: !!m.querySelector('[data-act="mockbank"][data-code="' + tag + '"]'),
      untimed: !!m.querySelector('[data-act="mockbanku"][data-code="' + tag + '"]'),
      named: m.innerText.indexOf('Drill bank section 1') >= 0
    };
  }, TAG);
  ok(prac.chip, 'a filter chip for the section exists');
  ok(/Drill bank section 1/.test(prac.chipText), 'the chip is labelled in English, not a raw tag', JSON.stringify(prac.chipText));
  ok(prac.launch && prac.untimed, 'both mock launchers exist');
  ok(prac.named, 'the tag is never shown to the reader');

  // ── 3. the chip filters the list to just that section ─────────────────────
  await page.click('[data-chip][data-val="' + TAG + '"]');
  await page.waitForTimeout(320);
  const filtered = await page.evaluate(() => {
    const t = document.getElementById('main').innerText;
    const m = t.match(/(\d+)\s+questions shown/);
    return m ? Number(m[1]) : -1;
  });
  ok(filtered === 25, 'the chip narrows the list to 25', 'got ' + filtered);

  // ── 4. the launcher builds a real 25-question timed mock ──────────────────
  await page.click('[data-act="mockbank"][data-code="' + TAG + '"]');
  await page.waitForTimeout(450);
  const mock = await page.evaluate(() => {
    const s = JSON.parse(localStorage.getItem('bpho-r0-v1') || '{}');
    return { hash: location.hash, n: s.mock ? s.mock.ids.length : 0, paper: s.mock ? s.mock.paper : null, sec: s.mock ? s.mock.seconds : 0 };
  });
  ok(mock.n === 25, 'the mock holds 25 questions', 'got ' + mock.n);
  ok(mock.paper === TAG, 'the mock is tagged with the section', String(mock.paper));
  ok(mock.sec === 3600, 'the clock is 60 minutes, the paper\'s own pace', mock.sec + 's');

  // ── 5. a figure-bearing question renders a real, non-zero figure ──────────
  await go(page, '#/q/S01-02');
  const fig = await page.evaluate(() => {
    const m = document.getElementById('main');
    const svg = m.querySelector('.fig svg');
    const r = svg ? svg.getBoundingClientRect() : null;
    return { sub: (m.querySelector('.sub') || {}).innerText || '', has: !!svg,
             w: r ? Math.round(r.width) : 0, h: r ? Math.round(r.height) : 0,
             vb: svg ? svg.getAttribute('viewBox') : null,
             opts: m.querySelectorAll('.mcq__opt, [data-mock]').length };
  });
  ok(fig.has && fig.w > 120 && fig.h > 60, 'the figure renders at a real size', fig.w + 'x' + fig.h + ' ' + fig.vb);
  ok(/Drill bank section 1, question 2/.test(fig.sub), 'the long label reads properly', JSON.stringify(fig.sub));

  // ── 6. the result page judges a bank section as a full 25-question paper ──
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
  ok(/qualifying line/.test(res), 'the result is judged against the 11/25 line, not the sample rule');
  ok(!/style check/.test(res), 'and it is NOT described as a short style check');
  const score = (res.match(/(\d+)\s*\/\s*25\s*correct/) || [])[1];
  ok(score !== undefined, 'a score out of 25 is reported', 'score=' + score);

  // ── 7. nothing threw along the way ────────────────────────────────────────
  ok(errors.length === 0, 'no console or page errors', errors.slice(0, 4).join(' | '));

  await browser.close();
  console.log('\n' + (fails ? 'FAILED: ' + fails + ' check(s)' : 'all checks passed'));
  process.exit(fails ? 1 : 0);
})();
