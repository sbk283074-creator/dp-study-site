/* Dump the World's Wife Lab's poems as JSON on stdout.
 *
 * Eng learning/index.html is a single self-contained 505 KB app: the 30 poems and
 * all of their analysis live in one `const SEED = { poems: [...] }` literal inside
 * an inline <script>, and nothing is rendered into the DOM until a poem is picked.
 * A crawler therefore sees only the toolbar, which is why the old index had one
 * entry for the whole lab whose text was "Read & Annotate  Analysis  Key lines".
 *
 * The literal is extracted by brace matching and evaluated in Node, which is far
 * more reliable than regexing JS object literals that contain backtick templates.
 *
 * Usage:  node tools/englab_dump.mjs        (run from the site root)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const FILE = path.join(ROOT, 'Eng learning', 'index.html');

const raw = fs.readFileSync(FILE, 'utf8');
const key = 'const SEED';
const at = raw.indexOf(key);
if (at < 0) {
  console.error('englab_dump: no `const SEED` found');
  process.stdout.write('{"poems":[]}');
  process.exit(0);
}

// Brace-match the object literal, skipping braces inside strings and templates.
const start = raw.indexOf('{', at);
let depth = 0, end = -1, quote = null, tpl = 0;
for (let i = start; i < raw.length; i++) {
  const c = raw[i], prev = raw[i - 1];
  if (quote) {
    if (c === quote && prev !== '\\') quote = null;
    continue;
  }
  if (c === '`') { tpl = tpl ? 0 : 1; continue; }
  if (tpl) continue;
  if (c === '"' || c === "'" || c === '/') { if (c !== '/' ) quote = c; continue; }
  if (c === '{') depth++;
  else if (c === '}') {
    depth--;
    if (depth === 0) { end = i + 1; break; }
  }
}
if (end < 0) {
  console.error('englab_dump: could not brace-match SEED');
  process.stdout.write('{"poems":[]}');
  process.exit(0);
}

let seed;
try {
  seed = new Function('return ' + raw.slice(start, end))();
} catch (e) {
  console.error('englab_dump: SEED did not evaluate: ' + e.message);
  process.stdout.write('{"poems":[]}');
  process.exit(0);
}

const strip = (s) =>
  String(s == null ? '' : s)
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z]+;|&#\d+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const poems = (seed.poems || []).map((p) => ({
  id: p.id,
  title: strip(p.title),
  author: strip(p.author),
  context: strip(p.context),
  text: strip(p.text),
  analysis: strip(p.analysis),
  passages: (p.keyPassages || []).map((k) => strip(k.text) + ' — ' + strip(k.note)),
  vocab: (p.vocab || []).map((v) => strip(v.term || v.w) + ' ' + strip(v.def || v.meaning)),
}));

process.stdout.write(JSON.stringify({ poems }));
