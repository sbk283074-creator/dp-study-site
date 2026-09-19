/* The one notation check that reads the DOM instead of the source.

   Every gate in gates.py reads a string.  `visible()` strips tags, `rendered()` models
   how a browser lays them out, `escaped_texts()` looks at the fields app.js escapes --
   all of them are models of the renderer, and a model is exactly the thing that gets the
   renderer wrong.  This script asks the real renderer.

   Why it earns its place: a question's fields are not all injected the same way.
   `stem`, `opts`, `sol` and `trap` go in as HTML, so `&#8730;` becomes a radical.
   `topic` and every `rel[i][1]` are passed through `esc()`, because priority.js reuses a
   rel label as a topic NAME -- so an entity there reaches the student verbatim.  That
   mismatch shipped once: four sections displayed `u<sup>2</sup> sin<sup>2</sup>&#952; / 2g`
   to the candidate.  G12 now catches the source, and this catches the page.

   So: walk every question in the bank through its real route, take `innerText`, and look
   for anything still shaped like an entity.  It also reports the distinct symbol glyphs
   that rendered, which is how a radical that silently degraded to a blank or a box would
   show up -- a source check cannot see that, because the source is fine.

   Run from bpho/ with the local server up (rooted at the repo root):
     NODE_PATH=<playwright-core> node tools/bank/check_render.js
   Pass a URL to check the deployed copy instead.
*/
const { chromium } = require('/Users/lucas.ma/.workbuddy-ai/binaries/node/workspace/node_modules/playwright-core');

const BASE = process.argv[2] || 'http://127.0.0.1:8901/bpho/index.html';

/* Named (&theta;), decimal (&#952;) and hex (&#x3b8;) references.  All three are legal
   HTML and all three would be a defect if one reached the rendered text. */
const ENTITY_RE = /&(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);/g;

/* The symbols this corpus actually uses.  If one of these stops appearing in the
   rendered text, it did not render -- and the count is the evidence. */
const GLYPH_RE = /[\u221a\u00b2\u00b3\u00bd\u00bc\u00be\u03b8\u03c9\u03c1\u03bb\u03b3\u0394\u2248\u00d7\u00f7\u2212\u00b0\u221d\u2264\u2265\u03bc\u03c3\u03b5\u03b1\u03b2\u03c0\u03c6\u2192]/g;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 1400 } });
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push(String(e)));

  await page.goto(BASE, { waitUntil: 'load' });

  // discovered, not listed: publishing section 8 must not need an edit here
  const ids = await page.evaluate(() => (window.BPHO_QUESTIONS || []).map(q => q.id));
  if (!ids.length) {
    console.log('FAIL: the page exposes no questions -- is the server rooted at the repo?');
    process.exit(1);
  }

  const bad = [];
  const glyphs = new Map();
  for (const id of ids) {
    await page.evaluate(h => { location.hash = h; }, '#/q/' + id);
    await page.waitForTimeout(60);
    const txt = await page.evaluate(() => {
      const m = document.getElementById('main');
      return m ? m.innerText : '';
    });
    for (const m of txt.matchAll(ENTITY_RE)) {
      bad.push({ id, hit: m[0], ctx: txt.slice(Math.max(0, m.index - 45), m.index + 25) });
    }
    for (const m of txt.matchAll(GLYPH_RE)) {
      glyphs.set(m[0], (glyphs.get(m[0]) || 0) + 1);
    }
  }

  console.log('questions walked: %d', ids.length);
  console.log('unrendered entities: %d', bad.length);
  for (const b of bad.slice(0, 25)) {
    console.log('   %s  %s   ...%s...', b.id, b.hit, b.ctx.replace(/\n/g, ' '));
  }
  console.log('symbol glyphs that rendered:');
  console.log('   %s', [...glyphs.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([c, n]) => c + '(U+' + c.codePointAt(0).toString(16).toUpperCase() + ')\u00d7' + n)
    .join('  '));
  console.log('console/page errors: %d', errs.length);
  errs.slice(0, 5).forEach(e => console.log('   ' + e));

  await browser.close();

  if (bad.length || errs.length) {
    console.log('\nFAILED: the page shows something the student should not see');
    process.exit(1);
  }
  console.log('\nall checks passed');
})();
