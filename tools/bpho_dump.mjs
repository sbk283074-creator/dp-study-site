/* Dump the BPhO Round 0 data files as JSON on stdout.
 *
 * BPhO is a hash-routed SPA: bpho/index.html ships an empty shell and all real
 * content arrives as `window.BPHO_*` globals from bpho/data/*.js. A crawler that
 * only reads HTML therefore sees none of it, so the search index needs this.
 *
 * The data files are plain JS assignments, not JSON (they must work over
 * file://), so the only reliable way to read them is to evaluate them.
 *
 * Usage:  node tools/bpho_dump.mjs        (run from the site root)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIR = path.join(ROOT, 'bpho', 'data');

// Discover the sharded content files rather than listing them by hand: a new
// `questions-N.js` / `modules-N.js` shard used to be silently dropped from the
// search index unless someone remembered to edit this file (it happened, and
// 82 questions went missing). Sorted numerically so the `concat onto a shared
// global` files are applied in the order the browser applies them.
const shards = (prefix) =>
  fs.readdirSync(DIR)
    .filter((f) => new RegExp(`^${prefix}-\\d+\\.js$`).test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)[0], 10) - parseInt(b.match(/\d+/)[0], 10));

const FILES = [
  'plan.js',
  'glossary.js',
  ...shards('modules'),
  ...shards('questions'),
];

const win = {};
for (const f of FILES) {
  const p = path.join(DIR, f);
  if (!fs.existsSync(p)) {
    console.error(`bpho_dump: missing ${f}`);
    continue;
  }
  const src = fs.readFileSync(p, 'utf8');
  // Each file assigns onto `window`, so hand it one and let it run.
  new Function('window', src)(win);
}

const strip = (s) =>
  String(s == null ? '' : s)
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z]+;|&#\d+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const out = {
  plan: (win.BPHO_PLAN || []).map((d) => ({
    day: d.day, date: d.date, mins: d.mins,
    title: strip(d.title), focus: strip(d.focus),
    tasks: (d.tasks || []).map(strip),
  })),
  modules: (win.BPHO_MODULES || []).map((m) => ({
    code: m.code, title: strip(m.title), short: strip(m.short),
    priority: m.priority, tier: strip(m.tier), why: strip(m.why), warn: strip(m.warn),
    // `sections` is the real checklist container: [{h, body}].
    sections: (m.sections || []).map((s) => ({ h: strip(s.h), body: strip(s.body) })),
    examples: (m.examples || []).map((e) => ({
      title: strip(e.title || e.q || ''), body: strip(e.body || e.sol || e.a || ''),
    })),
  })),
  glossary: (win.BPHO_GLOSSARY || []).map((g) => ({
    en: strip(g.en), zh: strip(g.zh), def: strip(g.def),
  })),
  questions: (win.BPHO_QUESTIONS || []).map((q) => ({
    id: q.id, module: q.module, topic: strip(q.topic), diff: q.diff,
    q: strip(q.q),
    opts: (q.opts || []).map(strip),
    sol: strip(q.sol).slice(0, 400),
  })),
};

process.stdout.write(JSON.stringify(out));
