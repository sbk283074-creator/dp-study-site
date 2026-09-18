/* Build the downloadable PDFs for every question paper on the BPhO study space.

   Run from bpho/:   node tools/papers/build_pdfs.js

   Why a headless browser rather than a PDF library: every question may carry a
   hand-authored inline SVG figure.  Chromium already renders those correctly, honours
   `break-inside: avoid` so a question is not split across a page boundary, and gives us
   page numbers in the margin for free.  A text-only PDF writer would have to re-implement
   SVG rendering, and the figures are the part most worth getting right.

   The questions are read from the SAME data files the site loads, in the same order, so a
   PDF cannot disagree with the page it is downloaded from.  The script also writes
   data/papers.js, which is how the site knows which PDFs exist -- a link to a file that
   was never generated is a dead download, and the site should not offer one.
*/
const { chromium } = require('/Users/lucas.ma/.workbuddy-ai/binaries/node/workspace/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

const HERE = __dirname;                            // bpho/tools/papers
const SITE = path.resolve(HERE, '..', '..');       // bpho/
const DATA = path.join(SITE, 'data');
const OUT = path.join(SITE, 'papers');

const SECONDS_PER_QUESTION = 144;                  // 2.4 min, the real paper's pace

/* Which papers to build, and what to call them.  `kind` decides the provenance line:
   the two official papers are reproduced BPhO material and must say so, because a reader
   who mistakes an original question for a real one will mis-calibrate their revision. */
const PAPERS = [
  { tag: 'R0-2025', kind: 'official', slug: 'r0-2025',
    label: 'BPhO Round 0 — 2025 paper',
    note: 'The one real Round 0 paper in existence. Reproduced from the published BPhO material for personal study.' },
  { tag: 'R0-SAMPLE', kind: 'official', slug: 'r0-sample',
    label: 'BPhO Round 0 — 2025 sample sheet',
    note: 'The 12 questions BPhO published as a sample. Reproduced from the official material for personal study.' },
];

/* Drill-bank sections are discovered from the data, so publishing section 4 adds its own
   PDFs with no change here. */
function bankPapers(questions) {
  const seen = [];
  questions.forEach(q => {
    if (q.paper && /^BANK-S\d\d$/.test(q.paper) && !seen.includes(q.paper)) seen.push(q.paper);
  });
  return seen.sort().map(tag => ({
    tag,
    kind: 'generated',
    slug: tag.toLowerCase(),
    label: 'Drill bank section ' + Number(tag.slice(-2)),
    note: 'Original questions written for this course, in the Round 0 format. Not BPhO material.',
  }));
}

/* ---------------- HTML ---------------- */

const CSS = `
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0; color: #14181f;
  font: 10.6pt/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "Helvetica Neue", Arial, sans-serif;
}
h1 { font-size: 19pt; line-height: 1.15; margin: 0 0 3mm; letter-spacing: -0.2pt; }
h2 { font-size: 12pt; margin: 8mm 0 3mm; padding-bottom: 1.5mm;
     border-bottom: 0.6pt solid #cbd2dd; }
p { margin: 0 0 2.4mm; }
b, strong { font-weight: 650; }
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em; background: #f1f3f7; padding: 0.3mm 1mm; border-radius: 1mm;
}
.formula {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.93em; background: #f1f3f7; border-left: 0.8mm solid #2f5fd0;
  padding: 1.6mm 3mm; border-radius: 0 1.5mm 1.5mm 0; margin: 2mm 0 3mm;
  white-space: pre-wrap; line-height: 1.5; break-inside: avoid;
}
.formula sup, .formula sub { font-size: 0.72em; line-height: 0; }

/* ---- cover / masthead ---- */
.masthead { border-bottom: 1.6pt solid #14181f; padding-bottom: 4mm; margin-bottom: 5mm; }
.masthead .kicker { font-size: 8.6pt; letter-spacing: 1.1pt; text-transform: uppercase;
                    color: #2f5fd0; font-weight: 700; margin: 0 0 2mm; }
.masthead .meta { color: #4a5262; font-size: 9.6pt; margin: 0; }
.masthead .prov { color: #7b8494; font-size: 8.8pt; margin: 2.5mm 0 0; font-style: italic; }
.rules { background: #f1f3f7; border-radius: 2mm; padding: 3.5mm 4mm; margin: 0 0 7mm; }
.rules h2 { margin: 0 0 2mm; font-size: 10.4pt; border: 0; padding: 0; }
.rules ul { margin: 0; padding-left: 5mm; }
.rules li { margin: 0 0 1mm; }

/* ---- questions ---- */
.q { break-inside: avoid; margin: 0 0 6.5mm; padding-bottom: 4.5mm;
     border-bottom: 0.4pt solid #e2e6ed; }
.q:last-child { border-bottom: 0; }
.q__head { font-size: 9.2pt; color: #4a5262; margin: 0 0 1.6mm; }
.q__n { font-weight: 700; color: #14181f; }
.q__mod { font-family: ui-monospace, Menlo, monospace; font-size: 8.6pt;
          border: 0.4pt solid #cbd2dd; border-radius: 1mm; padding: 0 1.2mm; margin-left: 1.5mm; }
.q__stem { margin: 0 0 2.4mm; }
.opts { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4mm 5mm; }
.opt { display: flex; gap: 2mm; break-inside: avoid; }
.opt__k { font-weight: 700; color: #2f5fd0; min-width: 3.4mm; }
.opt__v { flex: 1; }

/* figures: the svg carries only a viewBox, so width must come from here */
.fig { margin: 3mm 0; break-inside: avoid; }
.fig svg { display: block; width: 100%; height: auto; max-width: 108mm; margin: 0 auto; }

/* ---- markscheme ---- */
.keytable { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.6mm; margin: 0 0 7mm; }
.keytable div { border: 0.4pt solid #cbd2dd; border-radius: 1.4mm; padding: 1.6mm 2mm;
                font-size: 9.4pt; }
.keytable b { display: inline-block; min-width: 7mm; color: #4a5262; font-weight: 600; }
.keytable i { font-style: normal; font-weight: 700; color: #1f7a53; }
/* A solution is long, so the block must be ALLOWED to break -- holding it whole pushed
   the first one to the next page and left "Worked solutions" sitting over half a blank
   sheet.  Keep the heading with what follows, keep the formulas and trap notes whole, and
   let the prose flow with normal orphan/widow control. */
.ms { margin: 0 0 6.5mm; padding-bottom: 4.5mm; border-bottom: 0.4pt solid #e2e6ed; }
.ms:last-child { border-bottom: 0; }
.ms__head { break-after: avoid; }
.ms__ans { display: inline-block; background: #e6f4ee; color: #1f7a53; font-weight: 700;
           border-radius: 1.2mm; padding: 0.6mm 2.4mm; font-size: 10pt; }
.ms__body { margin-top: 2.4mm; }
.ms__body p, .ms__body li { orphans: 2; widows: 2; }
.trap { background: #fdf3e4; border-left: 0.8mm solid #a8641a; border-radius: 0 1.5mm 1.5mm 0;
        padding: 2mm 3mm; margin: 3mm 0 0; font-size: 9.6pt; break-inside: avoid; }
.trap b { color: #a8641a; }
`;

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)/g, '&amp;')
    .replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const LETTERS = 'ABCDE';

function masthead(paper, n, subtitle) {
  const mins = Math.round(n * SECONDS_PER_QUESTION / 60);
  return '<div class="masthead">'
    + '<p class="kicker">BPhO Round 0 · ' + esc(subtitle) + '</p>'
    + '<h1>' + esc(paper.label) + '</h1>'
    + '<p class="meta">' + n + ' questions · ' + mins + ' minutes · '
    + 'single answer, 5 options · <b>no calculator</b> · no negative marking</p>'
    + '<p class="prov">' + esc(paper.note) + '</p>'
    + '</div>';
}

const RULES = '<div class="rules"><h2>Before you start</h2><ul>'
  + '<li>Answer every question. There is no negative marking, so a blank is a wasted mark.</li>'
  + '<li>No calculator. Every answer here is reachable by hand, and the numbers are chosen to divide cleanly.</li>'
  + '<li>Work on paper, then mark yourself against the markscheme PDF.</li>'
  + '<li>The 2025 UK qualifying line was 11 out of 25, so about 44% is the target to beat.</li>'
  + '</ul></div>';

function questionsDoc(paper, qs) {
  let h = masthead(paper, qs.length, 'question paper') + RULES;
  qs.forEach((q, i) => {
    h += '<div class="q"><p class="q__head"><span class="q__n">Q' + (i + 1) + '</span>'
      + ' · ' + esc(q.topic || '') + '<span class="q__mod">' + esc(q.module || '') + '</span></p>'
      + '<div class="q__stem">' + q.q + '</div>'
      + '<div class="opts">'
      + q.opts.map((o, k) => '<div class="opt"><span class="opt__k">' + LETTERS[k]
        + '</span><span class="opt__v">' + o + '</span></div>').join('')
      + '</div></div>';
  });
  return h;
}

function markschemeDoc(paper, qs) {
  let h = masthead(paper, qs.length, 'markscheme');
  h += '<h2>Quick key</h2><div class="keytable">'
    + qs.map((q, i) => '<div><b>Q' + (i + 1) + '</b> <i>' + LETTERS[q.ans] + '</i></div>').join('')
    + '</div><h2>Worked solutions</h2>';
  qs.forEach((q, i) => {
    h += '<div class="ms"><p class="q__head"><span class="q__n">Q' + (i + 1) + '</span>'
      + ' · ' + esc(q.topic || '') + ' — <span class="ms__ans">Answer ' + LETTERS[q.ans]
      + '</span></p><div class="ms__body">' + q.sol + '</div>'
      + (q.trap ? '<div class="trap"><b>The trap.</b> ' + q.trap + '</div>' : '')
      + '</div>';
  });
  return h;
}

function wrap(title, body) {
  return '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    + '<title>' + esc(title) + '</title><style>' + CSS + '</style></head>'
    + '<body>' + body + '</body></html>';
}

/* How many pages did Chromium actually emit?

   The site shows this on each download card, and it is also the only cheap proof that a
   PDF is not empty -- page.pdf() resolves happily even if it wrote a blank document, so
   without a count the build would report success on a broken file.

   Chromium writes the page tree as plain (uncompressed) objects, so counting
   `/Type /Page` in the raw bytes is reliable here.  The lookahead matters: `/Type /Pages`
   is the *tree node* and must not be counted, and a greedy `[^s]` would eat the first
   character of the next token, so two adjacent page objects could be miscounted as one.
   Verified against PyMuPDF on every file: 12/34/6 and so on, exact. */
function pdfPages(file) {
  const raw = fs.readFileSync(file).toString('latin1');
  return (raw.match(/\/Type\s*\/Page(?![s])/g) || []).length;
}

/* ---------------- run ---------------- */

function dataScripts() {
  /* Read the load order out of index.html rather than hardcoding it: a new section adds
     one <script> tag there, and the PDF builder must pick it up or the two drift. */
  const html = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');
  const out = [];
  const re = /<script src="(data\/[^"]+\.js)"><\/script>/g;
  let m;
  while ((m = re.exec(html))) out.push(path.join(SITE, m[1]));
  if (!out.length) throw new Error('no data scripts found in index.html');
  return out;
}

(async () => {
  const scripts = dataScripts();
  const browser = await chromium.launch();

  // ---- 1. read the questions exactly as the site does ----
  const loader = await browser.newPage();
  await loader.setContent('<!doctype html><meta charset="utf-8"><body></body>');
  for (const p of scripts) await loader.addScriptTag({ path: p });
  const questions = await loader.evaluate(() => window.BPHO_QUESTIONS || []);
  await loader.close();
  if (!questions.length) throw new Error('BPHO_QUESTIONS is empty after loading ' + scripts.length + ' files');

  const papers = PAPERS.concat(bankPapers(questions));

  // ---- 2. render each paper ----
  fs.mkdirSync(OUT, { recursive: true });
  const page = await browser.newPage();
  const manifest = [];
  let built = 0;

  for (const paper of papers) {
    const qs = questions.filter(q => q.paper === paper.tag);
    if (!qs.length) { console.log('  skip  ' + paper.tag + ' — no questions'); continue; }

    for (const [which, doc] of [['questions', questionsDoc], ['markscheme', markschemeDoc]]) {
      const file = paper.slug + '-' + which + '.pdf';
      await page.setContent(wrap(paper.label + ' — ' + which, doc(paper, qs)),
                            { waitUntil: 'load' });
      await page.emulateMedia({ media: 'print' });
      await page.pdf({
        path: path.join(OUT, file),
        format: 'A4',
        printBackground: true,
        margin: { top: '17mm', bottom: '15mm', left: '15mm', right: '15mm' },
        displayHeaderFooter: true,
        headerTemplate: '<div style="font:8pt -apple-system,Segoe UI,Roboto,Arial,sans-serif;'
          + 'color:#7b8494;width:100%;padding:0 15mm;display:flex;justify-content:space-between">'
          + '<span>' + esc(paper.label) + '</span>'
          + '<span>' + (which === 'markscheme' ? 'Markscheme' : 'Question paper') + '</span></div>',
        footerTemplate: '<div style="font:8pt -apple-system,Segoe UI,Roboto,Arial,sans-serif;'
          + 'color:#7b8494;width:100%;text-align:center">'
          + '<span class="pageNumber"></span> / <span class="totalPages"></span></div>',
      });
      const bytes = fs.statSync(path.join(OUT, file)).size;
      const pages = pdfPages(path.join(OUT, file));
      if (!pages) throw new Error('wrote an empty PDF: papers/' + file);
      console.log('  wrote papers/' + file + '  ' + Math.round(bytes / 1024) + ' KB, ' + pages + ' pages');
      if (which === 'questions') paper._q = { file, bytes, pages };
      else paper._m = { file, bytes, pages };
      built++;
    }

    manifest.push({
      tag: paper.tag,
      kind: paper.kind,
      label: paper.label,
      note: paper.note,
      n: qs.length,
      seconds: qs.length * SECONDS_PER_QUESTION,
      figures: qs.filter(q => /<svg/.test(q.q)).length,
      modules: [...new Set(qs.map(q => q.module))].sort().join(' '),
      questions: 'papers/' + paper._q.file,
      markscheme: 'papers/' + paper._m.file,
      qBytes: paper._q.bytes,
      mBytes: paper._m.bytes,
      qPages: paper._q.pages,
      mPages: paper._m.pages,
    });
  }

  await browser.close();

  // ---- 3. tell the site what exists ----
  const stamp = new Date().toISOString().slice(0, 10);
  const js = '/* BPhO Round 0 — the downloadable papers that actually exist on disk.\n'
    + '   GENERATED by tools/papers/build_pdfs.js — do not edit by hand.\n\n'
    + '   The site renders its download links from this list, so a paper that was never\n'
    + '   built is never offered.  A hardcoded link would be a dead download the moment\n'
    + '   someone added a section and forgot to rebuild the PDFs. */\n\n'
    + 'window.BPHO_PAPERS = ' + JSON.stringify(manifest, null, 1) + ';\n'
    + 'window.BPHO_PAPERS_BUILT = "' + stamp + '";\n';
  fs.writeFileSync(path.join(DATA, 'papers.js'), js, 'utf8');
  console.log('\nwrote data/papers.js — ' + manifest.length + ' paper(s), ' + built + ' PDF(s)');

  const total = manifest.reduce((a, p) => a + p.qBytes + p.mBytes, 0);
  const pages = manifest.reduce((a, p) => a + p.qPages + p.mPages, 0);
  console.log('total ' + (total / 1048576).toFixed(1) + ' MB, ' + pages + ' pages in papers/');
})().catch(e => { console.error('FATAL', e); process.exit(1); });
