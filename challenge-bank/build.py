#!/usr/bin/env python3
"""Render the Challenge Bank static site from the JSON question files.

    python3 build.py            # rebuild site/ from data/
    python3 build.py --check    # validate data only, write nothing

The site is plain HTML + CSS + vanilla JS. It works from file:// (data is
injected as a JS global rather than fetched), and no build framework, template
engine or third-party package is involved.
"""

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SITE = ROOT / "site"
EXPORT = ROOT / "export"

SUBJECTS = {
    "math-aa-hl": {
        "name": "Mathematics: analysis and approaches HL",
        "short": "Maths AA HL",
        "guide": "2021 guide (first assessment 2021) — in force through November 2028",
        "blurb": "Non-routine Paper 1 and Paper 3 problems: reverse constructions, long chains, and "
                 "questions where the hard part is setting up the mathematics, not executing it.",
        "mathjax": True,
    },
    "physics-hl": {
        "name": "Physics HL",
        "short": "Physics HL",
        "guide": "2025 guide (first assessment 2025)",
        "blurb": "Multi-step Paper 2 problems that cross theme boundaries, with quantitative work, "
                 "units and significant figures enforced throughout.",
        "mathjax": True,
    },
    "computer-science-hl": {
        "name": "Computer science HL",
        "short": "CS HL",
        "guide": "2027 guide (first assessment 2027) — Theme A / Theme B",
        "blurb": "Algorithmic thinking and ADT reasoning against the new syllabus, including the "
                 "Paper 2 question type that requires no code.",
        "mathjax": True,
    },
    "business-management-sl": {
        "name": "Business management SL",
        "short": "BM SL",
        "guide": "2024 guide (first assessment 2024)",
        "blurb": "Original case studies and quantitative stimuli where the numbers point one way "
                 "and the judgement points another. SL content boundaries strictly observed.",
        "mathjax": True,
    },
}

CSS = """
:root{
  --ink:#111827; --muted:#6b7280; --line:#e5e7eb; --bg:#ffffff; --soft:#f8fafc;
  --accent:#1d4ed8; --accent-soft:#eff6ff; --hard:#b91c1c; --hard-soft:#fef2f2;
  --ok:#047857; --radius:10px;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:920px;margin:0 auto;padding:0 24px}
a{color:var(--accent)}
header.site{border-bottom:1px solid var(--line);background:var(--soft)}
header.site .wrap{display:flex;align-items:baseline;gap:16px;padding-top:18px;padding-bottom:18px;flex-wrap:wrap}
header.site a.brand{font-weight:700;text-decoration:none;color:var(--ink);font-size:17px}
header.site nav{margin-left:auto;display:flex;gap:16px;flex-wrap:wrap;font-size:14px}
header.site nav a{color:var(--muted);text-decoration:none}
header.site nav a:hover{color:var(--accent)}
header.site nav a.ext{color:var(--accent);border:1px solid var(--line);border-radius:999px;padding:3px 10px}
header.site nav a.ext:hover{border-color:var(--accent)}
h1{font-size:30px;line-height:1.25;margin:0 0 8px;letter-spacing:-.01em}
h2{font-size:21px;margin:34px 0 12px}
h3{font-size:17px;margin:24px 0 8px}
p{margin:0 0 14px}
.lede{font-size:18px;color:#374151}
small,.small{font-size:13px;color:var(--muted)}
main{padding:34px 0 60px;min-height:60vh}
footer.site{border-top:1px solid var(--line);padding:22px 0 40px;color:var(--muted);font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:22px}
.card{border:1px solid var(--line);border-radius:var(--radius);padding:18px;background:#fff}
.card h3{margin:0 0 6px;font-size:17px}
.card h3 a{text-decoration:none;color:var(--ink)}
.card h3 a:hover{color:var(--accent)}
.card p{font-size:14px;color:#374151;margin:8px 0 12px}
.card .count{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.chip{display:inline-block;font-size:12px;padding:2px 9px;border-radius:999px;border:1px solid var(--line);
  background:var(--soft);color:#374151;margin:0 6px 6px 0;white-space:normal;overflow-wrap:anywhere;max-width:100%;line-height:1.45}
.chip-hard{border-color:#fecaca;background:var(--hard-soft);color:var(--hard);font-weight:600}
.chip-key{background:var(--accent-soft);border-color:#bfdbfe;color:#1e40af}
.chip-topic{background:#f5f3ff;border-color:#ddd6fe;color:#5b21b6;font-weight:600}
.q{border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin-bottom:14px;background:#fff}
.q h3{margin:0 0 8px;font-size:18px}
.q h3 a{text-decoration:none;color:var(--ink)}
.q h3 a:hover{color:var(--accent)}
.q .meta{margin-top:10px}
.q .stem{color:#374151;font-size:14px;margin:8px 0 10px}
.box{border:1px solid var(--line);border-left:3px solid var(--accent);background:var(--soft);
  border-radius:0 var(--radius) var(--radius) 0;padding:16px 18px;margin:18px 0}
.box h4{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}
.box p:last-child,.box ul:last-child{margin-bottom:0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
th{background:var(--soft);font-weight:600}
figure{margin:18px 0}
figure svg{max-width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:8px}
figcaption{font-size:13px;color:var(--muted);margin-top:6px}
ol.parts{padding-left:22px}
ol.parts li{margin-bottom:12px}
.marks{float:right;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
details{border:1px solid var(--line);border-radius:var(--radius);margin:12px 0;background:#fff}
details[open]{background:#fff}
summary{cursor:pointer;padding:12px 16px;font-weight:600;font-size:15px;list-style:none}
summary::-webkit-details-marker{display:none}
summary:before{content:"▸ ";color:var(--accent)}
details[open] summary:before{content:"▾ "}
details .body{padding:0 18px 16px;border-top:1px solid var(--line)}
details .body > :first-child{margin-top:14px}
.reveal-note{font-size:13px;color:var(--muted);margin:6px 0 0}
pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:var(--radius);overflow-x:auto;
  font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
code{font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
p code,li code,td code{background:var(--soft);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 6px}input[type=search],select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff}
input[type=search]{flex:1;min-width:200px}
.pager{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}
.pager a,.btn{display:inline-block;border:1px solid var(--line);border-radius:8px;padding:7px 13px;
  text-decoration:none;font-size:14px;color:#374151;background:#fff}
.pager a:hover,.btn:hover{border-color:var(--accent);color:var(--accent)}
.stat-row{display:flex;gap:22px;flex-wrap:wrap;margin:16px 0}
.stat{font-size:13px;color:var(--muted)}
.stat b{display:block;font-size:22px;color:var(--ink)}
#results .q{margin-bottom:10px}
.empty{color:var(--muted);font-size:14px}
/* "Mark as done" — challenge-bank progress tracking (localStorage, no backend) */
.q{position:relative}
.q-head{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}
.q-head h3{margin:0;flex:1;min-width:0}
.q-done{margin-top:2px;border:1px solid var(--line);background:#fff;color:#475569;border-radius:999px;
  padding:6px 13px;font:600 12.5px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;
  white-space:nowrap;flex:none}
.q-done:hover{border-color:var(--accent);color:var(--accent)}
.q-done.on{background:#e7f6ec;border-color:#34a853;color:#1e7e34}
.q-done-page{display:inline-block;margin:14px 0 4px;border:1px solid var(--line);background:#fff;color:#334155;
  border-radius:10px;padding:9px 16px;font:600 14px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer}
.q-done-page:hover{border-color:var(--accent);color:var(--accent)}
.q-done-page.on{background:#e7f6ec;border-color:#34a853;color:#1e7e34}
/* "Ask AI" -- a per-question launcher, not a second chat.
   The panel it opens lives in assets/ai-widget.js and is loaded by every page
   on the site, so the tutor a student gets here is the same one the floating
   "Ask AI" button gives them: same controls, same model pool, same rendering.
   This block only decides WHICH question to focus on and how to ask it. The
   item's text rides along in a hidden node, because the tutor has no access to
   this bank and a request that sent only "help me" would be answered blind. */
.qai{margin:14px 0 0;border:1px solid #c7d2fe;border-radius:var(--radius);background:#f7f8ff;padding:12px 14px}
.qai-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.qai-title{font-weight:600;font-size:14px;color:#3730a3;white-space:nowrap}
.qai-sub{font-size:12px;color:var(--muted);flex:1;min-width:170px}
.qai-modes{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px}
.qai-btn{border:1px solid #a5b4fc;background:#fff;color:#3730a3;border-radius:8px;padding:7px 13px;
  font:600 13px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;white-space:nowrap}
.qai-btn:hover{border-color:#4f46e5;background:#eef2ff}
@media print{.qai{display:none}}
.kv{margin:0;font-size:13px}
.kv div{display:flex;gap:10px;padding:5px 0;border-bottom:1px solid var(--line)}
.kv div:last-child{border-bottom:0}
.kv dt{flex:0 0 150px;color:var(--muted)}
.kv dd{margin:0;flex:1;min-width:0;overflow-wrap:anywhere}
.paper-q{margin:0 0 34px;padding-top:14px;border-top:2px solid var(--line);page-break-inside:avoid}
.paper-q h3{margin-top:0}
.paper-marks{float:right;color:var(--muted);font-weight:400;font-size:14px}
.paper-ref{color:var(--muted);font-size:12.5px;margin:-6px 0 12px}
.paper-switch{font-size:14px}
/* A long equation is wider than a phone: let it scroll inside its own box
   instead of dragging the whole page sideways. Three things are required:
   display must be stated (and outrank MathJax's runtime stylesheet), and
   MathJax also writes an inline min-width on the container - min-width beats
   max-width, so it has to be reset with !important too. */
mjx-container{display:inline-block !important;max-width:100% !important;min-width:0 !important;overflow-x:auto;overflow-y:hidden}
mjx-container[display="true"]{display:block !important;padding:.15em 0 .5em}
@media (max-width:760px){
  table{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch}
  /* tighter cells: at this width the default padding leaves narrow columns a
     few px short of their longest unbreakable run */
  th,td{white-space:normal;padding:6px 8px}
  .wrap{overflow-wrap:anywhere}
}
/* ---- Build-your-own-paper: selection checkbox + floating bar ---- */
.q-pick-wrap{display:flex;align-items:center;gap:5px;flex:none;margin-right:6px;font-size:12px;color:var(--muted);cursor:pointer;user-select:none}
.q-pick-wrap input{width:15px;height:15px;cursor:pointer;accent-color:var(--accent)}
.q-pick-page{margin:14px 8px 4px 0;border:1px solid var(--line);background:#fff;color:#334155;border-radius:10px;padding:9px 16px;font:600 14px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer}
.q-pick-page:hover{border-color:var(--accent);color:var(--accent)}
.q-pick-page.on{background:#e7f6ec;border-color:#34a853;color:#1e7e34}
.q-pdf{margin:14px 0 4px;border:1px solid var(--line);background:#fff;color:#334155;border-radius:10px;padding:9px 16px;font:600 14px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer}
.q-pdf:hover{border-color:var(--accent);color:var(--accent)}
.cb-pickbar{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:40;display:flex;gap:12px;align-items:center;background:#0f172a;color:#fff;padding:10px 16px;border-radius:999px;box-shadow:0 6px 22px rgba(0,0,0,.25);font-size:14px}
.cb-pickbar[hidden]{display:none}
.cb-pickbar b{font-size:15px}
.cb-pickbar .btn{background:#fff;color:#0f172a;border:0;padding:6px 12px;border-radius:999px;font:600 13px -apple-system,Segoe UI,Roboto,Arial,sans-serif;text-decoration:none;cursor:pointer}
.cb-pickbar .cb-pickbar-clear{background:transparent;color:#cbd5e1;border:0;cursor:pointer;font-size:13px;text-decoration:underline}
/* ---- Builder page ---- */
.builder-controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:18px 0 14px;padding:12px 14px;border:1px solid var(--line);border-radius:var(--radius);background:var(--soft)}
.b-answers{font-size:14px;display:flex;align-items:center;gap:6px;cursor:pointer}
.paper-q-bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.paper-q-actions{margin-left:auto;display:flex;gap:6px}
.paper-q-actions button{border:1px solid var(--line);background:#fff;border-radius:7px;padding:3px 9px;font-size:13px;cursor:pointer}
.paper-q-actions button:hover{border-color:var(--accent);color:var(--accent)}
.paper-q-bar .paper-ref{font-size:12.5px;color:var(--muted)}
/* ---- Exam-paper layout: cover, question head, writing space, markscheme ---- */
.exam-cover{border:2px solid #111827;padding:20px 22px;margin:0 0 26px}
.ec-prog{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:0}
.ec-subject{font-family:Georgia,"Times New Roman",serif;font-size:25px;letter-spacing:.03em;text-transform:uppercase;margin:8px 0 2px}
.ec-level{margin:0;font-size:15px;color:#374151}
.ec-paper{font-family:Georgia,"Times New Roman",serif;font-size:18px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin:12px 0 0}
.ec-facts{width:100%;border-collapse:collapse;margin-top:16px;font-size:13.5px}
.ec-facts .ec-k{color:var(--muted);padding:7px 14px 7px 0;white-space:nowrap;width:1%}
.ec-facts .ec-v{padding:7px 26px 7px 0}
.ec-facts .ec-rule{border-bottom:1px solid #9ca3af;padding:7px 26px 7px 0;width:26%}
.ec-instr{margin-top:18px;border-top:1px solid #9ca3af;padding-top:12px;font-size:13.5px}
.ec-instr h2{font-size:12px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 8px;color:var(--muted)}
.ec-instr ul{margin:0;padding-left:20px}
.ec-instr li{margin:3px 0}
.ec-note{margin:12px 0 0;font-size:13px;color:#374151}
.exam-run-head{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid #111827;padding-bottom:6px;margin:0 0 16px}
.paper-q{border-top:0;border-bottom:1px solid var(--line);margin:0;padding:16px 0 6px;break-inside:avoid;page-break-inside:avoid}
.pq-head{display:flex;align-items:baseline;gap:14px}
.pq-head h3{margin:0;flex:1 1 auto;min-width:0;font-size:17px;font-weight:600}
.pq-n{font-weight:700;margin-right:4px}
.pq-right{flex:0 0 auto;text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:4px}
.pq-right .paper-q-actions{margin:0}
.builder-cta{border-color:var(--accent);background:var(--accent-soft)}
.builder-cta h3{margin-top:0}
.builder-cta ol{margin:10px 0 0;padding-left:20px}
.builder-cta li{margin:5px 0}
.pq-marks{display:block;font-size:13px;color:var(--muted);white-space:nowrap}
.pq-ref{display:block;font-size:11px;color:#9ca3af;letter-spacing:.02em}
.pq-lines{margin:12px 0 6px}
.pq-line{display:block;border-bottom:1px dotted #c9c9c9;height:21px}
.exam-end{text-align:center;font-size:13px;color:var(--muted);letter-spacing:.06em;margin:24px 0 0}
.exam-ms{break-before:page;page-break-before:always;margin-top:34px}
.exam-ms h2{text-align:center;font-family:Georgia,"Times New Roman",serif;font-size:17px;letter-spacing:.16em;text-transform:uppercase;border-top:2px solid #111827;border-bottom:2px solid #111827;padding:8px 0;margin:0 0 18px}
.ms-q .pq-head h3{font-size:16px;font-weight:600}
@media print{
  header.site nav,footer.site,.controls,input[type=search],select,.paper-switch,.pager,.q-done,.q-done-page{display:none}
  details{border:0} details .body{border-top:0}
  details[open] .body{border-top:0}
  body{font-size:11.5pt}
  .paper-q{border-top:1px solid #999}
  /* single-question export: show ONLY the question block, never the answer */
  body.cb-print-q .q-done-page,body.cb-print-q .q-pick-page,body.cb-print-q .q-pdf,
  body.cb-print-q .qai,body.cb-print-q details,body.cb-print-q .kv,
  body.cb-print-q header.site,body.cb-print-q footer.site,
  body.cb-print-q .pager,body.cb-print-q .reveal-note,body.cb-print-q #cb-pickbar,
  body.cb-print-q #dp-ai-root,body.cb-print-q #dp-tools-root{display:none !important}
  /* builder export: hide the on-screen controls, keep the assembled paper */
  body.cb-print-paper .builder-controls,body.cb-print-paper #cb-pickbar,
  body.cb-print-paper #dp-ai-root,body.cb-print-paper #dp-tools-root{display:none !important}
  /* exam-paper pages (per-subject papers + built papers): drop the whole site
     chrome so the browser prints the paper, not the website around it */
  body.cb-paper header.site,body.cb-paper footer.site,body.cb-paper .paper-switch,
  body.cb-paper .builder-controls,body.cb-paper #cb-pickbar,body.cb-paper .no-print,
  body.cb-paper #dp-ai-root,body.cb-paper #dp-tools-root{display:none !important}
  body.cb-paper main,body.cb-paper main>.wrap{max-width:none;width:auto;margin:0;padding:0}
  .pq-line{height:22px}
  .exam-cover{break-after:auto}
}
"""

JS = """
(function(){
  // ---------- Mark as done (works on listing + individual question pages) ----------
  var DONE_KEY = 'cb_done_v1';
  function loadDone(){ try { return JSON.parse(localStorage.getItem(DONE_KEY) || '{}'); } catch(e){ return {}; } }
  function saveDone(o){ try { localStorage.setItem(DONE_KEY, JSON.stringify(o)); } catch(e){} }
  function isDone(id){ return !!(id && loadDone()[id]); }
  function setDone(id, val){
    if(!id) return;
    var o = loadDone();
    if(val) o[id] = 1; else delete o[id];
    saveDone(o);
  }
  function wireToggle(btn){
    var id = btn.getAttribute('data-qid');
    if(!id) return;
    function paint(){
      var d = isDone(id);
      btn.setAttribute('aria-pressed', d ? 'true' : 'false');
      btn.textContent = d ? '\\u2713 Done' : 'Mark done';
      btn.classList.toggle('on', d);
      var card = btn.closest('.q');
      if(card) card.classList.toggle('is-done', d);
    }
    paint();
    btn.addEventListener('click', function(){
      setDone(id, !isDone(id));
      paint();
      if(typeof window.__cbRunFilter === 'function') window.__cbRunFilter();
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.q-done, .q-done-page'), wireToggle);

  // ---------- Listing filter: search / topic / paper / difficulty / done ----------
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  if(q && box){
    function hay(card){ return (card.dataset.search || '').toLowerCase(); }
    window.__cbRunFilter = function(){
      var term = q.value.trim().toLowerCase();
      var diff = (document.getElementById('f-diff')||{}).value || '';
      var paper = (document.getElementById('f-paper')||{}).value || '';
      var topic = (document.getElementById('f-topic')||{}).value || '';
      var fd = (document.getElementById('f-done')||{}).value || '';
      var shown = 0;
      Array.prototype.forEach.call(document.querySelectorAll('[data-search]'), function(card){
        var id = card.getAttribute('data-qid') || '';
        var done = isDone(id);
        var ok = (!term || hay(card).indexOf(term) !== -1)
              && (!diff || card.dataset.diff === diff)
              && (!paper || card.dataset.paper === paper)
              && (!topic || card.dataset.topic === topic)
              && (!fd || (fd === 'done' ? done : !done));
        card.style.display = ok ? '' : 'none';
        if(ok) shown++;
      });
      var note = document.getElementById('count');
      if(note) note.textContent = shown + ' question' + (shown === 1 ? '' : 's') + ' shown';
    };
    q.addEventListener('input', window.__cbRunFilter);
    ['f-diff','f-paper','f-topic','f-done'].forEach(function(id){
      var el = document.getElementById(id);
      if(el) el.addEventListener('change', window.__cbRunFilter);
    });
    window.__cbRunFilter();
  }

  // global search on the home page -- carrying the same filters the subject
  // pages already have, so "which Marketing questions have I not done" is
  // answerable from one place instead of by opening four subject pages in turn.
  var g = document.getElementById('g');
  var gr = document.getElementById('gresults');
  if(g && gr && window.CB_INDEX){
    var gSubject = document.getElementById('g-subject');
    var gTopic = document.getElementById('g-topic');
    var gDiff = document.getElementById('g-diff');
    var gDone = document.getElementById('g-done');

    // The topic vocabulary is per subject, so the topic list is rebuilt from
    // whatever the subject filter currently admits. A topic select that still
    // offered "Theme D: Fields" after switching to Business Management would be
    // a filter that can only ever return nothing.
    function topicOptions(){
      if(!gTopic) return;
      var want = gSubject ? gSubject.value : '';
      var seen = {}, out = [];
      window.CB_INDEX.forEach(function(x){
        if(!x.topic) return;
        if(want && x.sub !== want) return;
        if(seen[x.topic]) return;
        seen[x.topic] = 1; out.push(x.topic);
      });
      out.sort();
      var keep = gTopic.value;
      gTopic.innerHTML = '<option value="">All topics</option>' + out.map(function(t){
        return '<option value="' + t.replace(/"/g, '&quot;') + '">' + t + '</option>';
      }).join('');
      // Reset explicitly rather than relying on the browser to drop the old
      // selection when the option it named stops existing: if the subject
      // changed, the old topic is now a filter that can only ever return
      // nothing, and it must not stay quietly applied.
      gTopic.value = (keep && seen[keep]) ? keep : '';
    }

    function runGlobal(){
      var term = (g.value || '').trim().toLowerCase();
      var sub = gSubject ? gSubject.value : '';
      var topic = gTopic ? gTopic.value : '';
      var diff = gDiff ? gDiff.value : '';
      var fd = gDone ? gDone.value : '';
      var filtered = !!(sub || topic || diff || fd);
      // Two characters was the old floor purely to avoid dumping the whole bank
      // on one keystroke. With a filter applied, browsing without typing is the
      // point, so the floor only applies to a bare search.
      if(term.length < 2 && !filtered){ gr.innerHTML = ''; return; }
      var hits = window.CB_INDEX.filter(function(x){
        if(term.length >= 2 && x.s.indexOf(term) === -1) return false;
        if(sub && x.sub !== sub) return false;
        if(topic && x.topic !== topic) return false;
        if(diff && String(x.d) !== diff) return false;
        if(fd){
          var d = isDone(x.id);
          if(fd === 'done' ? !d : d) return false;
        }
        return true;
      });
      var capped = hits.slice(0, 60);
      gr.innerHTML = hits.length ? capped.map(function(x){
        // Same affordances as a subject listing, so a paper can be assembled
        // straight from a search instead of by walking four subject pages.
        return '<div class="q" data-qid="' + x.id + '">' +
               '<div class="q-head">' +
               '<label class="q-pick-wrap" title="Add this question to your custom paper">' +
               '<input type="checkbox" class="q-pick" data-qid="' + x.id + '"> <span>Paper</span></label>' +
               '<h3><a href="' + x.u + '">' + x.t + '</a></h3>' +
               '<button type="button" class="q-done" data-qid="' + x.id + '" aria-pressed="false">Mark done</button>' +
               '</div>' +
               '<div class="meta"><span class="chip">' + x.sub + '</span>' +
               (x.topic ? '<span class="chip chip-topic">' + x.topic + '</span>' : '') +
               '<span class="chip">' + x.paper + '</span>' +
               '<span class="chip">' + x.marks + ' marks</span>' +
               '<span class="chip chip-hard">difficulty ' + x.d + '</span></div>' +
               '</div>';
      }).join('') + (hits.length > capped.length
          ? '<p class="small">' + (hits.length - capped.length) + ' more match -- narrow the search or add a filter.</p>'
          : '')
        : '<p class="empty">No questions match that search.</p>';
      Array.prototype.forEach.call(gr.querySelectorAll('.q-done'), wireToggle);
      if(window.cbPaintPick) window.cbPaintPick();  // reflect the current selection
    }

    if(gSubject) gSubject.addEventListener('change', function(){ topicOptions(); runGlobal(); });
    if(gTopic) gTopic.addEventListener('change', runGlobal);
    if(gDiff) gDiff.addEventListener('change', runGlobal);
    if(gDone) gDone.addEventListener('change', runGlobal);
    g.addEventListener('input', runGlobal);
    // Ticking "Mark done" in a search result has to re-run this filter, not the
    // listing one -- and only one of the two exists on any given page.
    window.__cbRunFilter = runGlobal;
    topicOptions();
  }

  // ---------- "Ask AI": hand each question to the shared assistant ----------
  // There is no second chat implementation here. assets/ai-widget.js already
  // ships the panel -- controls, model pool, usage strip, rendering -- on every
  // page of the site, so this block only says WHICH question to focus on and
  // how to ask it. The item's own text (stem, every part, marks, difficulty)
  // rides along, because the tutor has no access to this bank and a request
  // that sent only "help me" would be answered blind.
  //
  // How each mode is put to the tutor. "Hint" deliberately withholds the answer:
  // a hint that works the question through is not a hint, it is the answer with
  // a preamble, and it removes the practice the question exists to give.
  var AI_MODES = {
    solution: { display:'Full worked solution', depth:'deep', difficulty:'hard', length:'long',
      ask:'Give a full worked solution in IB markscheme style. For each part give the method, the working and the result, and name which marks are earned (M method, A accuracy, R reasoning). Finish with the two errors candidates most often make here.' },
    hint: { display:'Hint only', depth:'quick', difficulty:'medium', length:'short',
      ask:'Give a HINT ONLY. Name the first move and the one thing to watch for. Do not give the answer, do not work any part through to a final value, and do not list the steps.' },
    steps: { display:'Guided steps', depth:'standard', difficulty:'hard', length:'medium',
      ask:'Work through the parts one at a time. For each part give the method and the markscheme logic, but stop short of the final value of the last part so I still have to finish it myself.' },
    mark: { display:'Mark my attempt', depth:'deep', difficulty:'hard', length:'medium',
      ask:'Mark my attempt against IB criteria. Say which marks I earned and which I lost, and exactly why for each. Do not rewrite the whole solution unless I lost a mark on that part.' }
  };

  // The whole item, exactly as the student sees it, behind a one-line header so
  // the tutor knows the subject, the difficulty and what the question is worth.
  function aiContext(panel){
    var src = panel.querySelector('.qai-src');
    var text = src ? src.textContent.trim() : '';
    var subj = panel.getAttribute('data-ai-subject') || 'IB';
    var diff = panel.getAttribute('data-ai-diff') || '';
    var marks = panel.getAttribute('data-ai-marks') || '';
    var ref = panel.getAttribute('data-ai-ref') || '';
    var head = 'IB ' + subj + ' question' + (ref ? ' (' + ref + ')' : '') +
               (diff ? ', difficulty ' + diff + ' of 5' : '') +
               (marks ? ', worth ' + marks + ' marks' : '') + '.';
    return head + '\\n\\n' + text;
  }

  function aiAsk(panel, mode){
    var conf = AI_MODES[mode] || AI_MODES.solution;
    if(!window.dpAI || typeof window.dpAI.open !== 'function'){
      window.alert('The study assistant has not finished loading. Reload the page and try again.');
      return;
    }
    var marks = parseInt(panel.getAttribute('data-ai-marks'), 10);
    window.dpAI.open({
      ref: panel.getAttribute('data-ai-ref') || 'this question',
      subject: panel.getAttribute('data-ai-subject') || undefined,
      marks: isNaN(marks) ? undefined : marks,
      context: aiContext(panel),
      prompt: conf.ask,
      display: conf.display,
      depth: conf.depth, difficulty: conf.difficulty, length: conf.length,
      // "Mark my attempt" has to wait for the student's working, so it opens the
      // box prefilled instead of firing a request at a blank attempt.
      autoSend: mode !== 'mark'
    });
    if(mode === 'mark'){
      var ta = document.getElementById('dpAiText');
      if(ta){ ta.value += '\\n\\nMY ATTEMPT:\\n'; ta.focus(); }
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-ai]'), function(panel){
    Array.prototype.forEach.call(panel.querySelectorAll('.qai-btn[data-ai-mode]'), function(btn){
      btn.addEventListener('click', function(){
        aiAsk(panel, btn.getAttribute('data-ai-mode'));
      });
    });
  });
})();

(function(){
  // ---------- Build-your-own-paper selection (localStorage, no backend) ----------
  var PICK_KEY = 'cb_pick_v1';
  function loadPick(){ try { return JSON.parse(localStorage.getItem(PICK_KEY) || '[]'); } catch(e){ return []; } }
  function savePick(a){ try { localStorage.setItem(PICK_KEY, JSON.stringify(a)); } catch(e){} }
  function isPicked(id){ return loadPick().indexOf(id) !== -1; }
  function setPick(id, val){
    if(!id) return;
    var a = loadPick(), i = a.indexOf(id);
    if(val && i === -1) a.push(id);
    if(!val && i !== -1) a.splice(i, 1);
    savePick(a); paintPick();
  }
  function clearPick(){ savePick([]); paintPick(); }
  // The builder lives at <site>/papers/builder.html. On GitHub Pages the path
  // contains "/site/", but a local server may serve site/ as the root, so anchor
  // on that marker when present and otherwise fall back to a depth calculation.
  function builderHref(){
    var p = location.pathname, i = p.indexOf('/site/');
    if(i >= 0) return p.slice(0, i + 6) + 'papers/builder.html';
    var segs = p.split('/').filter(Boolean);
    if(segs.length && segs[segs.length - 1].indexOf('.') !== -1) segs.pop();
    if(segs[segs.length - 1] === 'papers') return 'builder.html';
    return (segs.length === 0 ? '' : '../') + 'papers/builder.html';
  }
  function paintPick(){
    Array.prototype.forEach.call(document.querySelectorAll('.q-pick'), function(cb){
      var id = cb.getAttribute('data-qid');
      if(id) cb.checked = isPicked(id);
    });
    var pageBtn = document.querySelector('.q-pick-page');
    if(pageBtn){
      var on = isPicked(pageBtn.getAttribute('data-qid'));
      pageBtn.classList.toggle('on', on);
      pageBtn.textContent = on ? '\u2713 In paper' : 'Add to paper';
    }
    var bar = document.getElementById('cb-pickbar');
    if(bar){
      var n = loadPick().length;
      var cnt = bar.querySelector('[data-n]'); if(cnt) cnt.textContent = n;
      var pl = bar.querySelector('[data-plural]'); if(pl) pl.textContent = n === 1 ? '' : 's';
      var buildLink = bar.querySelector('.cb-pickbar-build');
      if(buildLink) buildLink.setAttribute('href', builderHref());
      bar.hidden = n === 0;
    }
  }
  // Delegated, because checkboxes are also rendered later -- into the home
  // page's search results and the builder's own list -- long after this file
  // has run. A per-element listener bound at load time misses every one of them.
  document.addEventListener('change', function(e){
    var cb = e.target;
    if(cb && cb.classList && cb.classList.contains('q-pick')){
      var id = cb.getAttribute('data-qid');
      if(id) setPick(id, cb.checked);
    }
  });
  var pageBtn = document.querySelector('.q-pick-page');
  if(pageBtn) pageBtn.addEventListener('click', function(){
    var id = pageBtn.getAttribute('data-qid');
    setPick(id, !isPicked(id));
  });
  var clearBtn = document.getElementById('cb-clear');
  if(clearBtn) clearBtn.addEventListener('click', function(){
    if(window.confirm('Clear all selected questions?')) clearPick();
  });

  // ---------- Single-question "Save as PDF" (isolated print) ----------
  function printQuestion(){
    document.body.classList.add('cb-print-q');
    var done = function(){ document.body.classList.remove('cb-print-q'); window.removeEventListener('afterprint', done); };
    window.addEventListener('afterprint', done);
    window.print();
    setTimeout(function(){ document.body.classList.remove('cb-print-q'); }, 1200);
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-print-q]'), function(b){
    b.addEventListener('click', printQuestion);
  });

  window.cbPaintPick = paintPick;
  paintPick();
})();
"""

MATHJAX = """<script>
window.MathJax={tex:{inlineMath:[],displayMath:[['\\\\(','\\\\)'],['$','$'],['$$','$$'],['\\\\[','\\\\]']],
processEscapes:true},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']},
startup:{pageReady:()=>MathJax.startup.defaultPageReady().then(fixInlineMath)}};
function fixInlineMath(){
  document.querySelectorAll('mjx-container[display="true"]').forEach(function(c){
    var parent=c.parentElement, hasText=false, i, n, ch=parent.childNodes;
    for(i=0;i<ch.length;i++){ n=ch[i]; if(n.nodeType===3 && n.textContent.trim().length>0){hasText=true;break;} }
    if(hasText){ c.style.setProperty('display','inline-block','important'); c.style.verticalAlign='middle'; c.style.margin='0 0.12em'; }
    else{ c.style.display='block'; c.style.margin='0.6em auto'; c.style.textAlign='center'; }
  });
}
function mjFallback(){var s=document.createElement('script');
s.src='https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js';s.async=true;document.head.appendChild(s);}
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" onerror="mjFallback()"></script>"""


# --------------------------------------------------------------------------
# tiny markdown-lite -> HTML
# --------------------------------------------------------------------------
def inline(s):
    s = html.escape(str(s), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s, flags=re.S)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    return s


def md(text):
    if not text:
        return ""
    blocks = re.split(r"\n\s*\n", str(text).strip())
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith("```"):
            body = b.strip("`")
            body = body.split("\n", 1)[1] if "\n" in body else body
            out.append("<pre><code>" + html.escape(body) + "</code></pre>")
            continue
        lines = [l for l in b.split("\n") if l.strip()]
        if lines and all(l.strip().startswith("- ") for l in lines):
            out.append("<ul>" + "".join("<li>" + inline(l.strip()[2:]) + "</li>" for l in lines) + "</ul>")
            continue
        out.append("<p>" + inline(b).replace("\n", "<br>") + "</p>")
    return "\n".join(out)


def table_html(tbl):
    cols = tbl.get("columns") or []
    rows = tbl.get("rows") or []
    parts = ["<table>"]
    if cols:
        parts.append("<thead><tr>" + "".join("<th>" + inline(c) + "</th>" for c in cols) + "</tr></thead>")
    parts.append("<tbody>")
    for r in rows:
        parts.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in r) + "</tr>")
    parts.append("</tbody></table>")
    cap = tbl.get("caption")
    return "<figure>" + "".join(parts) + (("<figcaption>" + inline(cap) + "</figcaption>") if cap else "") + "</figure>"


def stimulus_html(stim):
    if not stim:
        return ""
    if isinstance(stim, str):
        return '<div class="box"><h4>Stimulus</h4>' + md(stim) + "</div>"
    out = ['<div class="box"><h4>']
    out.append(inline(stim.get("title", "Stimulus")))
    out.append("</h4>")
    out.append(md(stim.get("body", "")))
    if stim.get("table"):
        out.append(table_html(stim["table"]))
    out.append("</div>")
    return "".join(out)


def figure_html(fig):
    if not fig:
        return ""
    if fig.get("type") == "svg":
        return ('<figure>' + fig["content"] +
                ('<figcaption>' + inline(fig["caption"]) + '</figcaption>' if fig.get("caption") else '') +
                '</figure>')
    if fig.get("type") == "table":
        return table_html(fig)
    if fig.get("type") == "code":
        return "<pre><code>" + html.escape(fig["content"]) + "</code></pre>"
    return ""


# --------------------------------------------------------------------------
# reusable question / answer bodies (pages, papers, PDF builder)
# --------------------------------------------------------------------------
def question_body_html(q):
    """The question itself (stem + stimulus + figure + parts), no answer.

    Reused by the question page, the per-subject paper and the custom builder so
    every surface renders the item identically."""
    parts = "".join(
        '<li><span class="marks">[%s mark%s]</span><strong>(%s)</strong> %s%s</li>'
        % (p["marks"], "" if p["marks"] == 1 else "s",
           html.escape(p["label"]), md(p["text"]),
           " <em>(%s)</em>" % html.escape(p["command_term"]) if p.get("command_term") else "")
        for p in q.get("parts") or []
    )
    return (stimulus_html(q.get("stimulus")) + figure_html(q.get("figure")) +
            md(q.get("question")) + '<ol class="parts">%s</ol>' % parts)


def answer_body_html(q):
    return (md(q.get("answer")) +
            "<h4>Markscheme notes</h4>" + md(q.get("markscheme_notes")))


def subject_level(slug):
    """The level lives in the subject slug and nowhere else."""
    if slug.endswith("-hl"):
        return "Higher Level"
    if slug.endswith("-sl"):
        return "Standard Level"
    return ""


def minutes_for(total_marks):
    """A paper's time budget. IB allows roughly 1.4 minutes a mark and always
    quotes the result in whole five-minute units."""
    return max(30, int(round(total_marks * 1.4 / 5.0) * 5))


def fmt_minutes(total_marks):
    """Spelled-out duration, the way a real paper quotes it: 1 hour 30 minutes."""
    h, m = divmod(minutes_for(total_marks), 60)
    if not h:
        return "%d minutes" % m
    return "%d hour%s%s" % (h, "s" if h > 1 else "", " %d minutes" % m if m else "")


def fmt_minutes_short(total_marks):
    """Compact duration for one-line summaries: 36 h 15 min."""
    h, m = divmod(minutes_for(total_marks), 60)
    if not h:
        return "%d min" % m
    return "%d h %d min" % (h, m) if m else "%d h" % h


def time_fact(total_marks):
    """The cover's time row, as (label, value).

    A real IB paper tops out near 90 marks (2 h 15) and even a whole Paper 3 stays
    under 180. A complete subject set does not fit one sitting at all, so its
    36-hour total must not be dressed up as one exam's working time: past 180
    marks the row is a total and says outright that it runs over sessions."""
    if total_marks <= 180:
        return "Working time", fmt_minutes(total_marks)
    return "Total working time", "%s across sessions" % fmt_minutes_short(total_marks)


def ruled_lines(marks, cap=12):
    """Writing space proportional to the marks on offer — about a line a mark,
    never a two-line stub and never most of a page."""
    n = max(2, min(cap, -(-int(marks or 1) * 6 // 5)))  # ceil(marks * 1.2)
    return '<div class="pq-lines">%s</div>' % ('<span class="pq-line"></span>' * n)


def exam_cover(meta, slug, *, answers, count, marks):
    """The cover block. A real paper opens with programme / subject / level /
    paper, the candidate's own details, the time and mark budget, and what the
    candidate is and is not allowed to do."""
    if answers:
        paper_line = "Markscheme"
        instr = [
            "This booklet gives the answers and markschemes for the matching question paper.",
            "Award marks against the working shown, not only against the final value.",
            "Each answer states the markscheme logic, so partial credit can be judged fairly.",
            "Questions are numbered exactly as they are in the question paper.",
        ]
        note = ("Do not open this until you have written your own answers. Reading a markscheme "
                "first replaces the thinking the question exists to make you do.")
    else:
        paper_line = "Challenge question paper"
        instr = [
            "Do not open this paper until instructed to do so.",
            "Answer <b>all</b> questions. Show all working.",
            "The number of marks available is shown in brackets [ ] after each question or part.",
            "Write your answers in the spaces provided.",
            "A calculator is permitted.",
            "No answers are printed in this paper. Attempt every question before opening the markscheme.",
        ]
        note = ""
        if marks > 180:
            instr.append("This paper is a complete subject set (%d questions, %d marks). It is not a "
                         "single sitting \u2014 split it across sessions and mark each part before "
                         "moving on." % (count, marks))
    facts = (
        '<table class="ec-facts">'
        '<tr><td class="ec-k">Candidate name</td><td class="ec-rule"></td>'
        '<td class="ec-k">Date</td><td class="ec-rule"></td></tr>'
        '<tr><td class="ec-k">Questions</td><td class="ec-v">%d</td>'
        '<td class="ec-k">Total marks</td><td class="ec-v">%d</td></tr>'
        '<tr><td class="ec-k">%s</td><td class="ec-v">%s</td>'
        '<td class="ec-k">Calculator</td><td class="ec-v">permitted</td></tr>'
        '</table>' % (count, marks, *time_fact(marks))
    )
    note_html = '<p class="ec-note">%s</p>' % note if note else ""
    return """<section class="exam-cover">
<p class="ec-prog">IB Diploma Programme</p>
<h1 class="ec-subject">{subject}</h1>
<p class="ec-level">{level}</p>
<p class="ec-paper">{line}</p>
{facts}
<div class="ec-instr"><h2>Instructions to candidates</h2><ul>{instr}</ul></div>
{note}
</section>""".format(subject=html.escape(meta["name"]), level=html.escape(subject_level(slug)),
                     line=html.escape(paper_line), facts=facts,
                     instr="".join("<li>%s</li>" % s for s in instr), note=note_html)


def build_bank(all_qs):
    """Flat, browser-loadable copy of every question's printable content.

    The builder page is a static file with no backend, so it reads this JSON
    (fetched at runtime) to render whatever the user has selected. HTML bodies
    are pre-rendered here with the same helpers the pages use, so a selected
    question looks exactly like its page."""
    out = []
    for slug in SUBJECTS:
        for q in all_qs.get(slug, []):
            out.append({
                "id": q["id"],
                "subject": SUBJECTS[slug]["short"],
                "subject_name": SUBJECTS[slug]["name"],
                "subject_level": subject_level(slug),
                "level": q.get("level"),
                "topic": q.get("topic") or "",
                "subtopic": q.get("subtopic") or "",
                "syllabus_ref": q.get("syllabus_ref") or "",
                "paper": q.get("paper") or "",
                "section": q.get("section") or "",
                "marks": q["marks"],
                "difficulty": q["difficulty"],
                "title": q.get("title") or q.get("subtopic") or "",
                "q_html": question_body_html(q),
                "a_html": answer_body_html(q),
            })
    return out


# --------------------------------------------------------------------------
# page scaffolding
# --------------------------------------------------------------------------
def page(title, body, subject=None, mathjax=False, extra_head="", body_class=""):
    nav = "".join(
        '<a href="../%s/index.html">%s</a>' % (slug, SUBJECTS[slug]["short"])
        for slug in SUBJECTS
    )
    # Depth 0 at site/index.html, depth 1 at site/<subject>/ and site/q/.
    # The main study system sits two levels above the site root.
    up = "../../" if not subject else "../../../"
    body_attr = ' class="%s"' % body_class if body_class else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — IB Challenge Bank</title>
<link rel="stylesheet" href="{'../' if subject else ''}assets/site.css">
{MATHJAX if mathjax else ''}{extra_head}
</head>
<body{body_attr}>
<header class="site"><div class="wrap">
  <a class="brand" href="{'../index.html' if subject else 'index.html'}">IB Challenge Bank</a>
  <nav>{nav}<a href="{'../' if subject else ''}papers/builder.html">Paper builder</a><a href="{'../index.html' if subject else 'index.html'}">About</a><a class="ext" href="{up}index.html">Study system &#8599;</a></nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
  Original questions written for the class of 2028 (May 2028 session). Nothing here is copied from an IB
  past paper, textbook or question bank; figures are authored, not scanned. Part of the
  <a href="{up}index.html">DP study system</a>.
</div></footer>
<div id="cb-pickbar" class="cb-pickbar" hidden>
  <span><b data-n>0</b> question<span data-plural>s</span> selected</span>
  <a class="btn cb-pickbar-build" href="#">Build paper</a>
  <button type="button" class="cb-pickbar-clear" id="cb-clear">Clear</button>
</div>
<script src="{'../' if subject else ''}assets/site.js"></script>
<script src="https://sbk283074-creator.github.io/dp-study-site/assets/ai-widget.js?v=3" defer></script>
</body>
</html>
"""


def chips(q):
    out = ['<div class="meta">']
    # The topic is the label a learner actually navigates by ("which part of the
    # course is this?"), so it leads the row rather than being buried in metadata.
    if q.get("topic"):
        out.append('<span class="chip chip-topic">%s</span>' % html.escape(q["topic"]))
    out.append('<span class="chip chip-key">%s</span>' % html.escape(q["syllabus_ref"]))
    out.append('<span class="chip">%s%s</span>' % (html.escape(q.get("paper") or ""),
                                                   " · Section " + q["section"] if q.get("section") else ""))
    out.append('<span class="chip">%s marks</span>' % q["marks"])
    out.append('<span class="chip chip-hard">difficulty %s</span>' % q["difficulty"])
    if q.get("technology"):
        out.append('<span class="chip">technology: %s</span>' % html.escape(q["technology"]))
    if q.get("language"):
        out.append('<span class="chip">%s</span>' % html.escape(q["language"]))
    for t in (q.get("command_terms") or [])[:4]:
        out.append('<span class="chip">%s</span>' % html.escape(t))
    out.append("</div>")
    return "".join(out)


def ai_panel(q):
    """A per-question "Ask AI" launcher.

    It does not build its own chat. It hands the item to the shared assistant
    (assets/ai-widget.js, loaded by every page on the site) and opens that panel
    focused on this question, so the tutor here is the same one the floating
    "Ask AI" button gives -- same controls, same model pool, same conversation --
    just scoped to a single item.

    The whole item (stem and every part) rides along in a hidden node, because
    the tutor has no access to this bank and a request that sent only "help me"
    would be answered blind. Inert until clicked, so a listing of ninety
    questions costs ninety small rows and nothing else.
    """
    src = [str(q.get("question") or "").strip()]
    parts = q.get("parts") or []
    if parts:
        src.append("")
        for p in parts:
            src.append("(%s) %s [%s mark%s]%s" % (
                p.get("label") or "?", p.get("text") or "", p.get("marks"),
                "" if p.get("marks") == 1 else "s",
                " (%s)" % p["command_term"] if p.get("command_term") else ""))
    return f"""<div class="qai" data-ai data-ai-subject="{html.escape(q['subject'])}" data-ai-diff="{q['difficulty']}" data-ai-marks="{q['marks']}" data-ai-ref="{html.escape(q['id'])}">
<div class="qai-head">
  <span class="qai-title">Ask AI</span>
  <span class="qai-sub">Opens the study assistant focused on this question &mdash; the whole item is sent, not just its topic.</span>
</div>
<div class="qai-modes">
  <button type="button" class="qai-btn" data-ai-mode="solution">Full worked solution</button>
  <button type="button" class="qai-btn" data-ai-mode="hint">Hint only</button>
  <button type="button" class="qai-btn" data-ai-mode="steps">Guided steps</button>
  <button type="button" class="qai-btn" data-ai-mode="mark">Mark my attempt</button>
</div>
<div class="qai-src" hidden>{html.escape(chr(10).join(src))}</div>
</div>"""


def question_card(q, slug):
    title = q.get("title") or q["subtopic"]
    qid = q["id"]
    search = " ".join([q["id"], q["topic"], q["subtopic"], q["syllabus_ref"],
                       q.get("challenge_mechanism", ""), " ".join(q.get("tags") or [])])
    return f"""<div class="q" data-search="{html.escape(search, quote=True)}" data-diff="{q['difficulty']}" data-paper="{html.escape(q.get('paper') or '')}" data-topic="{html.escape(q.get('topic') or '', quote=True)}" data-qid="{html.escape(qid)}">
<div class="q-head"><label class="q-pick-wrap" title="Add this question to your custom paper"><input type="checkbox" class="q-pick" data-qid="{html.escape(qid)}"> <span>Paper</span></label><h3><a href="../q/{html.escape(qid)}.html">{html.escape(title)}</a></h3>
<button type="button" class="q-done" data-qid="{html.escape(qid)}" aria-pressed="false">Mark done</button></div>
<p class="stem">{inline(q.get('challenge_mechanism', ''))}</p>
{chips(q)}
{ai_panel(q)}
</div>"""


def build_question_page(q, slug):
    parts = "".join(
        '<li><span class="marks">[%s mark%s]</span><strong>(%s)</strong> %s%s</li>'
        % (p["marks"], "" if p["marks"] == 1 else "s",
           html.escape(p["label"]), md(p["text"]),
           " <em>(%s)</em>" % html.escape(p["command_term"]) if p.get("command_term") else "")
        for p in q.get("parts") or []
    )
    prov = q.get("provenance") or {}
    orig = q.get("originality") or {}
    ver = q.get("verification") or {}
    if orig.get("max_similarity") is None:
        nearest = "not yet scanned"
    elif orig.get("nearest_bank_id"):
        nearest = "%s (similarity %s)" % (html.escape(str(orig["nearest_bank_id"])),
                                          orig["max_similarity"])
    else:
        nearest = "no shared 5-grams with the 12,796-question corpus (similarity %s)" % orig["max_similarity"]
    if orig.get("max_internal_similarity") is None:
        nearest_internal = "not yet scanned"
    elif orig.get("nearest_internal_id"):
        nearest_internal = "%s (similarity %s)" % (html.escape(str(orig["nearest_internal_id"])),
                                                   orig["max_internal_similarity"])
    else:
        nearest_internal = "no shared 5-grams with any other question here (similarity %s)" % orig["max_internal_similarity"]
    body = f"""
<h1>{html.escape(q.get('title') or q['subtopic'])}</h1>
<p class="lede"><a href="../{slug}/index.html">{html.escape(SUBJECTS[slug]['name'])}</a> · {html.escape(q['id'])}</p>
<button type="button" class="q-done-page" data-qid="{html.escape(q['id'])}" aria-pressed="false">Mark done</button>
<button type="button" class="q-pick-page" data-qid="{html.escape(q['id'])}">Add to paper</button>
<button type="button" class="q-pdf" data-print-q>Save as PDF</button>
{chips(q)}
{stimulus_html(q.get('stimulus'))}
{figure_html(q.get('figure'))}
<section id="q-print">
<h2>Question</h2>
{md(q.get('question'))}
<ol class="parts">{parts}</ol>
<p class="reveal-note">Total: {q['marks']} marks. Try the question before revealing anything below.</p>
</section>
{ai_panel(q)}
<details><summary>Reveal the answer</summary><div class="body">{md(q.get('answer'))}</div></details>
<details><summary>Markscheme notes</summary><div class="body">{md(q.get('markscheme_notes'))}</div></details>
<details><summary>Why this question is hard</summary><div class="body">{md(q.get('explanation'))}</div></details>
<h2>Metadata</h2>
<dl class="kv">
  <div><dt>Topic</dt><dd>{html.escape(q.get('topic') or '')} — {html.escape(q.get('subtopic') or '')}</dd></div>
  <div><dt>Challenge lever</dt><dd>{html.escape(q.get('challenge_mechanism') or '')}</dd></div>
  <div><dt>Syllabus reference</dt><dd>{html.escape(q.get('syllabus_ref') or '')}</dd></div>
  <div><dt>Inspiration</dt><dd>{html.escape(prov.get('inspired_by') or 'original')}</dd></div>
  <div><dt>Adaptation</dt><dd>{html.escape(prov.get('adaptation') or '')}</dd></div>
  <div><dt>Verification</dt><dd>{html.escape(ver.get('method') or '')}</dd></div>
  <div><dt>Nearest bank match</dt><dd>{nearest}</dd></div>
  <div><dt>Nearest item here</dt><dd>{nearest_internal}</dd></div>
  <div><dt>Status</dt><dd>{html.escape(q.get('status') or '')} · authored by {html.escape(q.get('authored_by') or '')} · {html.escape(q.get('updated_at') or '')}</dd></div>
</dl>
<div class="pager"><a href="../{slug}/index.html">← All {html.escape(SUBJECTS[slug]['short'])} questions</a></div>
"""
    return page("%s — %s" % (q["id"], SUBJECTS[slug]["short"]), body, subject=slug,
                mathjax=SUBJECTS[slug]["mathjax"])


def build_paper(slug, qs, answers=False):
    """A printable exam-style paper, or its matching markscheme, for one subject.

    Deliberately NOT a restyled copy of the on-screen listing. It is laid out the
    way a real paper is: a cover carrying the candidate's own details and the
    instructions, questions numbered with their mark allocation in the right-hand
    margin and writing space sized from the marks on offer, and — for the
    markscheme — a section that starts on its own page.
    """
    meta = SUBJECTS[slug]
    total = sum(q["marks"] for q in qs)
    kind = "Markscheme" if answers else "Question paper"
    blocks = []
    for i, q in enumerate(qs, 1):
        title = html.escape(q.get("title") or q["subtopic"])
        head = (
            '<div class="pq-head"><h3><span class="pq-n">%d.</span> %s</h3>'
            '<span class="pq-right"><span class="pq-marks">[%d mark%s]</span>'
            '<span class="pq-ref">%s</span></span></div>'
            % (i, title, q["marks"], "" if q["marks"] == 1 else "s", html.escape(q["id"]))
        )
        if answers:
            meta_line = " \u00b7 ".join(x for x in [
                html.escape(q.get("topic") or ""),
                html.escape(q.get("syllabus_ref") or ""),
                "difficulty %s" % q["difficulty"],
            ] if x)
            blocks.append('<section class="paper-q ms-q">\n%s\n<p class="pq-ref">%s</p>\n%s</section>'
                          % (head, meta_line, answer_body_html(q)))
        else:
            blocks.append('<section class="paper-q">\n%s\n%s\n%s</section>'
                          % (head, question_body_html(q), ruled_lines(q["marks"])))
    switch = ('<p class="paper-switch"><a href="%s-paper.html">&#8592; Question paper</a></p>' % slug
              if answers
              else '<p class="paper-switch"><a href="%s-answers.html">Markscheme &#8594;</a></p>' % slug)
    run_head = ('<div class="exam-run-head"><span>%s \u00b7 %s</span>'
                '<span>%d questions \u00b7 %d marks \u00b7 %s</span></div>'
                % (html.escape(meta["short"]), html.escape(kind), len(qs), total,
                   "%s working time across sessions" % fmt_minutes_short(total)
                   if total > 180 else fmt_minutes(total)))
    cover = exam_cover(meta, slug, answers=answers, count=len(qs), marks=total)
    if answers:
        body = cover + '<section class="exam-ms"><h2>Markscheme</h2>%s%s</section>' % (run_head, "".join(blocks))
    else:
        body = (cover + switch + run_head + "".join(blocks)
                + '<p class="exam-end">End of questions \u00b7 %d marks in total</p>' % total)
    return page("%s \u2014 %s" % (meta["short"], kind), body, subject=slug,
                mathjax=meta["mathjax"], body_class="cb-paper")


def build_subject_page(slug, qs):
    meta = SUBJECTS[slug]
    diffs = sorted({q["difficulty"] for q in qs})
    papers = sorted({q.get("paper") or "" for q in qs if q.get("paper")})
    topics = sorted({q.get("topic") or "" for q in qs if q.get("topic")})
    total = sum(q["marks"] for q in qs)
    body = f"""
<h1>{html.escape(meta['name'])}</h1>
<p class="lede">{html.escape(meta['blurb'])}</p>
<p><small>{html.escape(meta['guide'])}</small></p>
<div class="stat-row">
  <div class="stat"><b>{len(qs)}</b>questions</div>
  <div class="stat"><b>{total}</b>marks in total</div>
  <div class="stat"><b>{min(diffs) if diffs else '–'}–{max(diffs) if diffs else '–'}</b>difficulty range</div>
</div>
<p class="paper-switch">Printable: <a href="../papers/{slug}-paper.html">question paper</a> · <a href="../papers/{slug}-answers.html">answer booklet</a></p>
<div class="controls">
  <input type="search" id="q" placeholder="Search topic, syllabus reference, tag…" aria-label="Search questions">
  <select id="f-topic" aria-label="Filter by topic"><option value="">All topics</option>
    {''.join('<option value="%s">%s</option>' % (html.escape(t, quote=True), html.escape(t)) for t in topics)}
  </select>
  <select id="f-paper" aria-label="Filter by paper"><option value="">All papers</option>
    {''.join('<option value="%s">%s</option>' % (html.escape(p, quote=True), html.escape(p)) for p in papers)}
  </select>
  <select id="f-diff" aria-label="Filter by difficulty"><option value="">All difficulties</option>
    {''.join('<option value="%s">Difficulty %s</option>' % (d, d) for d in diffs)}
  </select>
  <select id="f-done" aria-label="Filter by progress"><option value="">All questions</option><option value="todo">To do</option><option value="done">Done</option></select>
</div>
<p class="small" id="count">{len(qs)} questions</p>
<div id="results"></div>
{''.join(question_card(q, slug) for q in qs)}
"""
    return page(meta["name"], body, subject=slug, mathjax=meta["mathjax"])


def build_index(all_qs):
    cards = []
    for slug, meta in SUBJECTS.items():
        qs = all_qs.get(slug, [])
        cards.append(f"""<div class="card">
  <h3><a href="{slug}/index.html">{html.escape(meta['name'])}</a></h3>
  <p class="count">{len(qs)} question{'s' if len(qs) != 1 else ''}</p>
  <p>{html.escape(meta['blurb'])}</p>
  <p><small>{html.escape(meta['guide'])}</small></p>
</div>""")
    index_js = [{"t": (q.get("title") or q["subtopic"]), "sub": SUBJECTS[slug]["short"],
                 "u": "q/%s.html" % q["id"], "id": q["id"], "marks": q["marks"],
                 "d": q["difficulty"],
                 "paper": q.get("paper") or "", "topic": q.get("topic") or "",
                 "s": " ".join([q["id"], q["topic"], q["subtopic"], q["syllabus_ref"],
                                " ".join(q.get("tags") or [])]).lower()}
                for slug in SUBJECTS for q in all_qs.get(slug, [])]
    sub_opts = "".join(
        '<option value="%s">%s</option>' % (html.escape(SUBJECTS[s]["short"], quote=True),
                                            html.escape(SUBJECTS[s]["short"]))
        for s in SUBJECTS if all_qs.get(s))
    diff_opts = "".join(
        '<option value="%s">Difficulty %s</option>' % (d, d)
        for d in sorted({q["difficulty"] for qs in all_qs.values() for q in qs}))
    body = f"""
<h1>IB Challenge Bank</h1>
<p class="lede">A small, deliberately hard set of <strong>original</strong> exam-style questions for the
class of 2028 session: Maths AA HL, Physics HL, Computer Science HL and Business Management SL.</p>
<p>Every question is written from scratch against a specific syllabus bullet. Nothing is a past-paper
question with the numbers changed, and nothing is a one-step recall item. Each question carries a stated
<em>challenge lever</em> — the thing that makes it hard — and shows its markscheme, its provenance and
how it was verified.</p>
<h2>Browse by subject</h2>
<div class="cards">{''.join(cards)}</div>
<h2>Papers</h2>
<div class="card builder-cta">
  <h3><a href="papers/builder.html">Build your own paper &#8594;</a></h3>
  <p>Pick any questions, from any subject, and assemble them into a printable paper laid out like a real
  exam — cover page, instructions, questions numbered with their marks in the margin, writing space for
  each answer, and a markscheme on its own pages.</p>
  <ol>
    <li>Tick <strong>Paper</strong> next to a question — here in the search results, or on a subject page.</li>
    <li>A bar appears at the bottom of the screen showing how many you have picked. It follows you from
    page to page, so you can build a paper across subjects.</li>
    <li>Press <strong>Build paper</strong>, tick <em>Include the markscheme</em> if you want the answers,
    then <strong>Print / Save as PDF</strong>.</li>
  </ol>
</div>
<h3>Ready-made papers</h3>
<p>Each subject is also assembled into a printable question paper and a matching markscheme, so a whole
set can be attempted under exam conditions away from the screen. Every paper uses the same exam layout as
the builder, and the markscheme starts on its own page.</p>
<ul>{''.join(
    '<li><strong>%s</strong> — %d questions, %d marks · '
    '<a href="papers/%s-paper.html">question paper</a> · '
    '<a href="papers/%s-answers.html">markscheme</a></li>'
    % (html.escape(SUBJECTS[s]['short']), len(all_qs.get(s, [])),
       sum(q['marks'] for q in all_qs.get(s, [])), s, s)
    for s in SUBJECTS if all_qs.get(s)
)}</ul>
<h2>Search all questions</h2>
<p>Filter by subject, topic, difficulty or progress, or type to search every subject at once.
The topic list follows the subject you pick.</p>
<div class="controls">
  <input type="search" id="g" placeholder="Search all subjects…" aria-label="Search all questions">
  <select id="g-subject" aria-label="Filter by subject"><option value="">All subjects</option>{sub_opts}</select>
  <select id="g-topic" aria-label="Filter by topic"><option value="">All topics</option></select>
  <select id="g-diff" aria-label="Filter by difficulty"><option value="">All difficulties</option>{diff_opts}</select>
  <select id="g-done" aria-label="Filter by progress"><option value="">All questions</option><option value="todo">To do</option><option value="done">Done</option></select>
</div>
<div id="gresults"></div>
<h2>How to use this bank</h2>
<ul>
  <li>Attempt the question in writing first — timed, closed book, under exam conditions for that paper.</li>
  <li>Only then open <em>Reveal the answer</em>. Compare method, not just the final value.</li>
  <li>Read <em>Markscheme notes</em> for what earns partial credit and what the common errors are.</li>
  <li>To work away from the screen, tick <em>Paper</em> on the questions you want and print them from the
  <a href="papers/builder.html">paper builder</a>; or print a whole subject at once.</li>
  <li>Read <em>Why this question is hard</em> last; it names the trap the question is built around.</li>
</ul>
"""
    extra = "<script>window.CB_INDEX = %s;</script>" % json.dumps(index_js, ensure_ascii=False)
    return page("IB Challenge Bank", body, extra_head=extra)


# --------------------------------------------------------------------------
# custom "build your own exam paper" page
# --------------------------------------------------------------------------
# A static page (no backend). It reads the user's selection from localStorage and
# the printable question bodies from data/bank.json, then assembles an exam-style
# paper the browser can print to PDF. MathJax is included so selected questions
# with LaTeX typeset exactly as they do on their own pages.
BUILDER_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Build your own exam paper &mdash; IB Challenge Bank</title>
<link rel="stylesheet" href="../assets/site.css">
__MATHJAX__
</head>
<body class="cb-paper">
<header class="site"><div class="wrap">
  <a class="brand" href="../index.html">IB Challenge Bank</a>
  <nav><a href="../math-aa-hl/index.html">Maths AA HL</a><a href="../physics-hl/index.html">Physics HL</a><a href="../computer-science-hl/index.html">CS HL</a><a href="../business-management-sl/index.html">BM SL</a><a href="../papers/builder.html">Paper builder</a><a href="../index.html">About</a><a class="ext" href="../../index.html">Study system &#8599;</a></nav>
</div></header>
<main><div class="wrap">
<div class="builder-controls">
  <label class="b-answers"><input type="checkbox" id="b-answers"> Include the markscheme (starts on a new page)</label>
  <button type="button" class="btn" id="b-print">Print / Save as PDF</button>
  <button type="button" class="btn" id="b-clear">Clear selection</button>
  <span class="b-total" id="b-total"></span>
  <a class="btn" href="../index.html">&#8592; Back to the bank</a>
</div>
<div id="b-paper"></div>
<div id="b-empty" class="empty" hidden>
  <p><strong>No questions selected yet.</strong></p>
  <p>Tick <strong>Paper</strong> next to any question &mdash; in the search results on the home page or on a
  subject page &mdash; or press <strong>Add to paper</strong> on a question&#39;s own page. The bar at the
  bottom of the screen keeps the count, and your selection is remembered in this browser, so you can gather
  questions from several subjects before you build.</p>
  <p><a class="btn" href="../index.html">Browse the bank &#8594;</a></p>
</div>
</div></main>
<footer class="site"><div class="wrap">
  Part of the <a href="../../index.html">DP study system</a>.
</div></footer>
<script src="../assets/site.js"></script>
<script src="https://sbk283074-creator.github.io/dp-study-site/assets/ai-widget.js?v=3" defer></script>
<script>
// The paper is assembled in the browser from data/bank.json (no backend): this
// page reads the selection that the site-wide picker keeps in localStorage and
// lays the questions out as an exam paper -- cover, numbered questions with the
// mark allocation in the right-hand margin, ruled writing space sized from the
// marks, and an optional markscheme that starts on its own page.
(function(){
  var PAPER=document.getElementById('b-paper');
  var EMPTY=document.getElementById('b-empty');
  var TOTAL=document.getElementById('b-total');
  var ANS=document.getElementById('b-answers');
  var KEY='cb_pick_v1';

  function esc(s){
    return String(s==null?'':s).replace(/[&<>"]/g,function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];
    });
  }
  function pick(){ try{ return JSON.parse(localStorage.getItem(KEY)||'[]'); }catch(e){ return []; } }
  function savePick(a){ try{ localStorage.setItem(KEY,JSON.stringify(a)); }catch(e){} }
  function typeset(){
    if(window.MathJax && MathJax.typesetPromise){
      MathJax.typesetPromise([PAPER]).then(function(){ if(typeof fixInlineMath==='function') fixInlineMath(); });
    } else if(typeof fixInlineMath==='function'){ fixInlineMath(); }
  }
  // A paper's time budget: about 1.4 minutes a mark, quoted in whole 5s.
  function fmtMinutes(t){
    var m=Math.max(30,Math.round(t*1.4/5)*5), h=Math.floor(m/60), r=m%60;
    if(!h) return r+' minutes';
    return h+' hour'+(h>1?'s':'')+(r?' '+r+' minutes':'');
  }
  // Writing space proportional to the marks on offer.
  function ruled(marks){
    var n=Math.max(2,Math.min(12,Math.ceil((marks||1)*1.2))), s='', i;
    for(i=0;i<n;i++) s+='<span class="pq-line"></span>';
    return '<div class="pq-lines">'+s+'</div>';
  }
  function marksLabel(m){ return '['+(m==null?'\u2014':m)+' mark'+(m===1?'':'s')+']'; }
  // A real paper tops out near 90 marks; a complete subject set does not fit one
  // sitting, so its total must not read as a single exam's working time.
  function timeLabel(t){ return t<=180 ? 'Working time' : 'Total working time'; }
  function timeValue(t){
    if(t<=180) return fmtMinutes(t);
    var m=Math.max(30,Math.round(t*1.4/5)*5), h=Math.floor(m/60), r=m%60;
    return (h ? h+' h'+(r?' '+r+' min':'') : r+' min')+' across sessions';
  }
  function cover(items,total){
    var names={}, lean=items[0]||{};
    items.forEach(function(q){ if(q.subject_name) names[q.subject_name]=1; });
    var keys=Object.keys(names);
    var subject = keys.length===1 ? keys[0] : 'Mixed subjects';
    var level   = keys.length===1 ? (lean.subject_level||'') : 'Questions from more than one subject';
    return '<section class="exam-cover">'
      + '<p class="ec-prog">IB Diploma Programme</p>'
      + '<h1 class="ec-subject">'+esc(subject)+'</h1>'
      + '<p class="ec-level">'+esc(level)+'</p>'
      + '<p class="ec-paper">Practice paper</p>'
      + '<table class="ec-facts">'
      + '<tr><td class="ec-k">Candidate name</td><td class="ec-rule"></td>'
      + '<td class="ec-k">Date</td><td class="ec-rule"></td></tr>'
      + '<tr><td class="ec-k">Questions</td><td class="ec-v">'+items.length+'</td>'
      + '<td class="ec-k">Total marks</td><td class="ec-v">'+total+'</td></tr>'
      + '<tr><td class="ec-k">'+timeLabel(total)+'</td><td class="ec-v">'+timeValue(total)+'</td>'
      + '<td class="ec-k">Calculator</td><td class="ec-v">permitted</td></tr>'
      + '</table>'
      + '<div class="ec-instr"><h2>Instructions to candidates</h2><ul>'
      + '<li>Do not open this paper until instructed to do so.</li>'
      + '<li>Answer <b>all</b> questions. Show all working.</li>'
      + '<li>The number of marks available is shown in brackets [ ] after each question or part.</li>'
      + '<li>Write your answers in the spaces provided.</li>'
      + '<li>A calculator is permitted.</li>'
      + (total>180 ? '<li>This paper is long ('+items.length+' questions, '+total+' marks), so it is not a '
          + 'single sitting \u2014 split it into parts and mark each part before moving on.</li>' : '')
      + (ANS.checked
          ? '<li>The markscheme follows the questions, starting on a new page. Attempt the paper first.</li>'
          : '<li>No markscheme is included in this printing.</li>')
      + '</ul></div></section>';
  }
  function move(id,delta){
    var a=pick(), i=a.indexOf(id), j=i+delta;
    if(i<0||j<0||j>=a.length) return;
    a.splice(i,1); a.splice(j,0,id); savePick(a); render();
  }
  function paperHead(q,i,n){
    return '<div class="pq-head"><h3><span class="pq-n">'+i+'.</span> '+esc(q.title)+'</h3>'
      + '<span class="pq-right">'
      + '<span class="pq-marks">'+marksLabel(q.marks)+'</span>'
      + '<span class="pq-ref">'+esc(q.id)+'</span>'
      + '<span class="paper-q-actions no-print">'
      + (i>1?'<button type="button" class="b-up" data-id="'+esc(q.id)+'" title="Move up">&#8593;</button>':'')
      + (i<n?'<button type="button" class="b-down" data-id="'+esc(q.id)+'" title="Move down">&#8595;</button>':'')
      + '<button type="button" class="b-remove" data-id="'+esc(q.id)+'">Remove</button>'
      + '</span></span></div>';
  }
  function render(){
    var ids=pick(), items=[], total=0;
    ids.forEach(function(id){ var q=byId[id]; if(q){ items.push(q); total += parseInt(q.marks,10)||0; } });
    if(!items.length){
      PAPER.innerHTML=''; EMPTY.hidden=false; TOTAL.textContent=''; return;
    }
    EMPTY.hidden=true;
    var n=items.length;
    var qHtml = items.map(function(q,i){
      return '<section class="paper-q">'+paperHead(q,i+1,n)+q.q_html+ruled(q.marks)+'</section>';
    }).join('');
    var msHtml = items.map(function(q,i){
      var ref=[q.topic,q.syllabus_ref,'difficulty '+q.difficulty].filter(Boolean).join(' \u00b7 ');
      return '<section class="paper-q ms-q">'
        + '<div class="pq-head"><h3><span class="pq-n">'+(i+1)+'.</span> '+esc(q.title)+'</h3>'
        + '<span class="pq-right"><span class="pq-marks">'+marksLabel(q.marks)+'</span>'
        + '<span class="pq-ref">'+esc(ref)+'</span></span></div>'
        + q.a_html + '</section>';
    }).join('');
    PAPER.innerHTML = cover(items,total)
      + '<div class="exam-run-head"><span>Practice paper</span><span>'
      + n+' questions \u00b7 '+total+' marks \u00b7 '+fmtMinutes(total)+'</span></div>'
      + qHtml
      + '<p class="exam-end">End of questions \u00b7 '+total+' marks in total</p>'
      + (ANS.checked ? '<section class="exam-ms"><h2>Markscheme</h2>'+msHtml+'</section>' : '');
    TOTAL.textContent = n+' question'+(n===1?'':'s')+' \u00b7 '+total+' marks';
    Array.prototype.forEach.call(PAPER.querySelectorAll('.b-remove'),function(b){
      b.addEventListener('click',function(){
        var a=pick(), i=a.indexOf(b.getAttribute('data-id'));
        if(i>-1){ a.splice(i,1); savePick(a); render(); if(window.cbPaintPick) window.cbPaintPick(); }
      });
    });
    Array.prototype.forEach.call(PAPER.querySelectorAll('.b-up'),function(b){
      b.addEventListener('click',function(){ move(b.getAttribute('data-id'),-1); });
    });
    Array.prototype.forEach.call(PAPER.querySelectorAll('.b-down'),function(b){
      b.addEventListener('click',function(){ move(b.getAttribute('data-id'),1); });
    });
    typeset();
  }
  var byId={};
  fetch('../data/bank.json').then(function(r){ return r.json(); }).then(function(bank){
    bank.forEach(function(q){ byId[q.id]=q; });
    ANS.addEventListener('change',render);
    document.getElementById('b-print').addEventListener('click',function(){
      document.body.classList.add('cb-print-paper');
      var done=function(){ document.body.classList.remove('cb-print-paper'); window.removeEventListener('afterprint',done); };
      window.addEventListener('afterprint',done);
      window.print();
      setTimeout(function(){ document.body.classList.remove('cb-print-paper'); },1200);
    });
    document.getElementById('b-clear').addEventListener('click',function(){
      if(confirm('Clear all selected questions?')){ savePick([]); render(); if(window.cbPaintPick) window.cbPaintPick(); }
    });
    render();
  }).catch(function(){
    EMPTY.hidden=false;
    EMPTY.innerHTML='<p><strong>Could not load the question bank data.</strong></p>'
      + '<p>This page reads <code>data/bank.json</code> next to it with <code>fetch</code>, which browsers '
      + 'block for <code>file://</code> pages. Serve the site over http(s) &mdash; on the live site this is '
      + 'handled for you.</p>';
  });
})();
</script>
</body>
</html>
"""


def build_builder():
    return BUILDER_PAGE.replace("__MATHJAX__", MATHJAX)


# --------------------------------------------------------------------------
def load():
    all_qs, errors = {}, []
    for slug in SUBJECTS:
        all_qs[slug] = []
        d = DATA / slug
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            if f.name.startswith("_"):      # templates and scratch files
                continue
            try:
                payload = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append("%s: invalid JSON (%s)" % (f, e))
                continue
            for q in payload.get("questions", []):
                missing = [k for k in ("id", "subject", "level", "syllabus_ref", "topic",
                                       "subtopic", "marks", "difficulty", "question",
                                       "answer", "explanation", "challenge_mechanism")
                           if not q.get(k)]
                if missing:
                    errors.append("%s: %s missing %s" % (f.name, q.get("id", "?"), ", ".join(missing)))
                all_qs[slug].append(q)
    # order: hardest first, then most marks
    for slug in all_qs:
        all_qs[slug].sort(key=lambda q: (-q.get("difficulty", 0), -q.get("marks", 0)))
    return all_qs, errors


def write_export(all_qs):
    EXPORT.mkdir(parents=True, exist_ok=True)
    for slug, qs in all_qs.items():
        rows = []
        for q in qs:
            stem = md(q.get("question"))
            parts = "".join("<p>(%s) %s [%s]</p>" % (p["label"], md(p["text"]), p["marks"])
                            for p in q.get("parts") or [])
            rows.append({
                "id": q["id"], "subject": q["subject"], "level": q["level"],
                "topic": q["topic"], "subtopic": q["subtopic"],
                "paper_type": q.get("paper"), "command_term": ", ".join(q.get("command_terms") or []),
                "marks": q["marks"], "difficulty": q["difficulty"],
                "question": stem + parts, "answer": md(q.get("answer")),
                "explanation": md(q.get("explanation")),
                "source": "Challenge Bank (original, AI-authored)",
                "tags": q.get("tags") or [], "authored_by": "ai",
            })
        (EXPORT / ("%s.json" % slug)).write_text(
            json.dumps({"questions": rows}, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate data, write nothing")
    args = ap.parse_args()

    if not DATA.is_dir():
        print("No data/ directory.", file=sys.stderr)
        return 1
    all_qs, errors = load()
    total = sum(len(v) for v in all_qs.values())
    for e in errors:
        print("ERROR " + e, file=sys.stderr)
    print("Loaded %d questions across %d subjects." % (total, len(all_qs)))
    if args.check:
        return 1 if errors else 0
    if errors:
        print("Fix the errors above before building.", file=sys.stderr)
        return 1

    # Write every page in place (overwriting), then prune only stale files.
    # Deliberately NOT a rm-rf of site/: a bulk delete is slow and can trip
    # external safety guards, and overwriting is enough to keep output fresh.
    expected = set()

    def put(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        expected.add(path.resolve())

    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "q").mkdir(parents=True, exist_ok=True)
    (SITE / "papers").mkdir(parents=True, exist_ok=True)
    put(SITE / "assets" / "site.css", CSS)
    put(SITE / "assets" / "site.js", JS)

    put(SITE / "index.html", build_index(all_qs))
    for slug, qs in all_qs.items():
        put(SITE / slug / "index.html", build_subject_page(slug, qs))
        for q in qs:
            put(SITE / "q" / ("%s.html" % q["id"]), build_question_page(q, slug))
        put(SITE / "papers" / ("%s-paper.html" % slug), build_paper(slug, qs))
        put(SITE / "papers" / ("%s-answers.html" % slug), build_paper(slug, qs, answers=True))

    # Browser-loadable copy of every question's printable body, used by the custom
    # paper builder (a static page with no backend of its own).
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    put(SITE / "data" / "bank.json", json.dumps(build_bank(all_qs), ensure_ascii=False))
    put(SITE / "papers" / "builder.html", build_builder())

    pruned = 0
    if SITE.exists():
        for f in sorted(SITE.rglob("*")):
            if f.is_file() and f.resolve() not in expected:
                f.unlink()
                pruned += 1
    if pruned:
        print("Pruned %d stale file(s) from site/." % pruned)

    write_export(all_qs)
    print("Wrote %d HTML files to site/ and %d export files to export/." %
          (len(list(SITE.rglob('*.html'))), len(list(EXPORT.glob('*.json')))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
