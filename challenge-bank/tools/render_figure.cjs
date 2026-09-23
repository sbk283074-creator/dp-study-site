// Render-and-read pass on the new figure: the step that Batch 30/31 earned and that
// no text audit can replace. Presence in the DOM is not the same as being drawn right.
const path = require('/Users/lucas.ma/.workbuddy/binaries/node/versions/20.18.0/lib/node_modules/@playwright/cli/node_modules/playwright-core');

(async () => {
  const file = process.argv[2] || 'site/q/MATH-P3-019.html';
  const shot = process.argv[3] || '/tmp/p3019-figure.png';
  // the bundled playwright-core wants build 1237 and this machine has 1234
  const bin = process.env.PW_CHROME ||
    '/Users/lucas.ma/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell';
  const browser = await path.chromium.launch({ executablePath: bin });
  const page = await browser.newPage({ viewport: { width: 980, height: 1400 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + process.cwd() + '/' + file, { waitUntil: 'load' });
  const hide = () => page.addStyleTag({ content: '#dp-ai-root,#dp-tools-root,#dp-search-root{display:none !important}' });
  await hide();
  await page.waitForTimeout(2500);   // let MathJax settle

  const info = await page.evaluate(() => {
    const fig = document.querySelector('#q-print figure svg') ? document.querySelector('#q-print figure') : document.querySelector('figure:has(svg)');
    const svg = fig && fig.querySelector('svg');
    const r = svg && svg.getBoundingClientRect();
    const fr = fig && fig.getBoundingClientRect();
    const texts = svg ? Array.from(svg.querySelectorAll('text')).map(t => t.textContent) : [];
    const body = document.body.innerText;
    return {
      svgBox: r ? { w: Math.round(r.width), h: Math.round(r.height) } : null,
      figBox: fr ? { w: Math.round(fr.width), h: Math.round(fr.height) } : null,
      viewBox: svg && svg.getAttribute('viewBox'),
      hasWidthAttr: !!(svg && svg.getAttribute('width')),
      texts,
      polys: svg ? svg.querySelectorAll('polyline').length : 0,
      // raw markup leaking into prose is a renderer defect, not a figure defect
      leaks: ['viewBox', 'stroke-width', '</svg>', 'polyline'].filter(t => body.includes(t)),
      // MathJax actually typeset the question?
      mjx: document.querySelectorAll('mjx-container').length,
      rawLatex: /\\frac|\\infty|\\pi\$/.test(body),
      marksVisible: /\[4 marks\]|\[3 marks\]/.test(body),
      optionLists: document.querySelectorAll('ol.opts').length,
    };
  });

  const fig = await page.$('#q-print figure:has(svg)') || await page.$('figure:has(svg)');
  if (fig) await fig.screenshot({ path: shot });
  await page.screenshot({ path: shot.replace(/\.png$/, '-page.png'), fullPage: false });

  console.log(JSON.stringify({ ...info, shot, errors }, null, 1));
  await browser.close();
})();
