/* Dump the two real BPhO papers as JSON so the Python gate system can calibrate the
   difficulty scorer against them.

   The scorer itself lives in gates.py and is written in Python -- one implementation,
   so a new question and a 2025 question are measured by exactly the same instrument.
   This script only extracts the raw fields; it does not score anything.

   Run:  node extract_papers.js > papers.json
   Re-run whenever questions-4.js or questions-5.js changes. */

const fs = require('fs');
const path = require('path');

global.window = global;

const DATA = path.join(__dirname, '..', '..', 'data');
const FILES = [
  'plan', 'glossary',
  'modules-1', 'modules-2', 'modules-3', 'modules-4', 'modules-5', 'modules-6', 'modules-7',
  'curriculum',
  'questions-1', 'questions-2', 'questions-3', 'questions-4', 'questions-5', 'questions',
];

for (const f of FILES) {
  const p = path.join(DATA, f + '.js');
  if (!fs.existsSync(p)) { console.error('missing ' + p); process.exit(1); }
  // eslint-disable-next-line no-eval
  eval(fs.readFileSync(p, 'utf8'));
}

const WANT = ['R0-2025', 'R0-SAMPLE'];
const out = (window.BPHO_QUESTIONS || [])
  .filter(q => WANT.indexOf(q.paper) >= 0)
  .map(q => ({
    id: q.id,
    paper: q.paper,
    module: q.module,
    topic: q.topic,
    diff: q.diff,
    rel: q.rel || [],
    key: q.key || [],
    q: q.q,
    opts: q.opts,
    ans: q.ans,
    sol: q.sol,
    trap: q.trap || '',
  }));

process.stdout.write(JSON.stringify({ generated: new Date().toISOString(), questions: out }, null, 1) + '\n');
console.error('extracted ' + out.length + ' questions from ' + WANT.join(', '));
