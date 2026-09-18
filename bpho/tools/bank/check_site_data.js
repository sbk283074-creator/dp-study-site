/* Load a generated bpho data file the way the browser does -- by running it against a
   fake `window` -- and assert the shape the app depends on.  A template-literal
   escaping mistake is a hard syntax error, so this is the difference between "the file
   was written" and "the file works".

   Run from bpho/:  node tools/bank/check_site_data.js data/bank-01.js */
const fs = require('fs');

const path = process.argv[2];
const src = fs.readFileSync(path, 'utf8');
const win = {};
try {
  new Function('window', src)(win);
} catch (e) {
  console.log('SYNTAX ERROR loading ' + path + ': ' + e.message);
  process.exit(1);
}

const qs = win.BPHO_QUESTIONS || [];
const LET = 'ABCDE';
let bad = 0;
const fail = (m) => { console.log('  FAIL ' + m); bad++; };

console.log('loaded ' + path);
console.log('  questions: ' + qs.length);

const ids = new Set();
let figs = 0, traps = 0, keyed = 0, answerOk = 0;
for (const q of qs) {
  if (!q.id) { fail('a question has no id'); continue; }
  if (ids.has(q.id)) fail('duplicate id ' + q.id);
  ids.add(q.id);
  for (const f of ['module', 'topic', 'q', 'sol', 'paper']) {
    if (typeof q[f] !== 'string' || !q[f]) fail(q.id + ': field ' + f + ' missing/empty');
  }
  if (!Number.isInteger(q.diff) || q.diff < 1 || q.diff > 3) fail(q.id + ': diff ' + q.diff);
  if (!Array.isArray(q.opts) || q.opts.length !== 5) fail(q.id + ': opts not five');
  if (!Number.isInteger(q.ans) || q.ans < 0 || q.ans > 4) fail(q.id + ': ans ' + q.ans);
  if (!Array.isArray(q.rel) || q.rel.some(r => !Array.isArray(r) || r.length !== 2))
    fail(q.id + ': rel is not a list of [module, topic] pairs');
  if (!Array.isArray(q.key)) fail(q.id + ': key missing');
  if (typeof q.trap !== 'string') fail(q.id + ': trap missing');
  else traps++;
  if (/\{\{FIG/.test(q.q + q.sol + (q.trap || ''))) fail(q.id + ': unresolved figure placeholder');
  if (/<svg/.test(q.q)) figs++;
  // the letter the solution states must be the letter the key points at
  const m = q.sol.match(/Answer:\s*([A-E])/g);
  if (!m) fail(q.id + ': solution never states Answer: <letter>');
  else {
    keyed++;
    const last = m[m.length - 1].replace(/Answer:\s*/, '');
    if (last === LET[q.ans]) answerOk++;
    else fail(q.id + ': solution says ' + last + ', key says ' + LET[q.ans]);
  }
}

console.log('  with a figure:      ' + figs);
console.log('  with a trap:        ' + traps);
console.log('  key == solution:    ' + answerOk + '/' + keyed);
console.log('  paper tag:          ' + (qs[0] ? qs[0].paper : '(none)'));
console.log(bad ? '\nFAILED: ' + bad + ' problem(s)' : '\nOK: data loads and the shape is right');
process.exit(bad ? 1 : 0);
