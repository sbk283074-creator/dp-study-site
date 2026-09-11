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
        "mathjax": False,
    },
    "business-management-sl": {
        "name": "Business management SL",
        "short": "BM SL",
        "guide": "2024 guide (first assessment 2024)",
        "blurb": "Original case studies and quantitative stimuli where the numbers point one way "
                 "and the judgement points another. SL content boundaries strictly observed.",
        "mathjax": False,
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
  background:var(--soft);color:#374151;margin:0 6px 6px 0;white-space:nowrap}
.chip-hard{border-color:#fecaca;background:var(--hard-soft);color:var(--hard);font-weight:600}
.chip-key{background:var(--accent-soft);border-color:#bfdbfe;color:#1e40af}
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
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
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
p code,li code,td code{background:var(--soft);padding:1px 5px;border-radius:4px}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 6px}
input[type=search],select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff}
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
.kv{margin:0;font-size:13px}
.kv div{display:flex;gap:10px;padding:5px 0;border-bottom:1px solid var(--line)}
.kv div:last-child{border-bottom:0}
.kv dt{flex:0 0 150px;color:var(--muted)}
.kv dd{margin:0;flex:1}
.paper-q{margin:0 0 34px;padding-top:14px;border-top:2px solid var(--line);page-break-inside:avoid}
.paper-q h3{margin-top:0}
.paper-marks{float:right;color:var(--muted);font-weight:400;font-size:14px}
.paper-ref{color:var(--muted);font-size:12.5px;margin:-6px 0 12px}
.paper-switch{font-size:14px}
@media print{
  header.site nav,footer.site,.controls,input[type=search],select,.paper-switch,.pager{display:none}
  details{border:0} details .body{border-top:0}
  details[open] .body{border-top:0}
  body{font-size:11.5pt}
  .paper-q{border-top:1px solid #999}
}
"""

JS = """
(function(){
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  if(!q || !box) return;
  function hay(card){ return (card.dataset.search || '').toLowerCase(); }
  function run(){
    var term = q.value.trim().toLowerCase();
    var diff = (document.getElementById('f-diff')||{}).value || '';
    var paper = (document.getElementById('f-paper')||{}).value || '';
    var shown = 0;
    Array.prototype.forEach.call(document.querySelectorAll('[data-search]'), function(card){
      var ok = (!term || hay(card).indexOf(term) !== -1)
            && (!diff || card.dataset.diff === diff)
            && (!paper || card.dataset.paper === paper);
      card.style.display = ok ? '' : 'none';
      if(ok) shown++;
    });
    var note = document.getElementById('count');
    if(note) note.textContent = shown + ' question' + (shown === 1 ? '' : 's') + ' shown';
    box.style.display = 'none';
  }
  q.addEventListener('input', run);
  ['f-diff','f-paper'].forEach(function(id){
    var el = document.getElementById(id);
    if(el) el.addEventListener('change', run);
  });

  // global search on the home page
  var g = document.getElementById('g');
  var gr = document.getElementById('gresults');
  if(g && gr && window.CB_INDEX){
    g.addEventListener('input', function(){
      var t = g.value.trim().toLowerCase();
      if(t.length < 2){ gr.innerHTML = ''; return; }
      var hits = window.CB_INDEX.filter(function(x){
        return x.s.indexOf(t) !== -1;
      }).slice(0, 20);
      gr.innerHTML = hits.length ? hits.map(function(x){
        return '<div class="q"><h3><a href="' + x.u + '">' + x.t + '</a></h3>' +
               '<div class="meta"><span class="chip">' + x.sub + '</span>' +
               '<span class="chip">' + x.paper + '</span>' +
               '<span class="chip">' + x.marks + ' marks</span>' +
               '<span class="chip chip-hard">difficulty ' + x.d + '</span></div></div>';
      }).join('') : '<p class="empty">No questions match that search.</p>';
    });
  }
})();
"""

MATHJAX = """<script>
window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']],
processEscapes:true},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};
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
# page scaffolding
# --------------------------------------------------------------------------
def page(title, body, subject=None, mathjax=False, extra_head=""):
    nav = "".join(
        '<a href="../%s/index.html">%s</a>' % (slug, SUBJECTS[slug]["short"])
        for slug in SUBJECTS
    )
    # Depth 0 at site/index.html, depth 1 at site/<subject>/ and site/q/.
    # The main study system sits two levels above the site root.
    up = "../../" if not subject else "../../../"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — IB Challenge Bank</title>
<link rel="stylesheet" href="{'../' if subject else ''}assets/site.css">
{MATHJAX if mathjax else ''}{extra_head}
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{'../index.html' if subject else 'index.html'}">IB Challenge Bank</a>
  <nav>{nav}<a href="{'../index.html' if subject else 'index.html'}">About</a><a class="ext" href="{up}index.html">Study system &#8599;</a></nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
  Original questions written for the class of 2028 (May 2028 session). Nothing here is copied from an IB
  past paper, textbook or question bank; figures are authored, not scanned. Part of the
  <a href="{up}index.html">DP study system</a>.
</div></footer>
<script src="{'../' if subject else ''}assets/site.js"></script>
</body>
</html>
"""


def chips(q):
    out = ['<div class="meta">']
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


def question_card(q, slug):
    title = q.get("title") or q["subtopic"]
    search = " ".join([q["id"], q["topic"], q["subtopic"], q["syllabus_ref"],
                       q.get("challenge_mechanism", ""), " ".join(q.get("tags") or [])])
    return f"""<div class="q" data-search="{html.escape(search, quote=True)}" data-diff="{q['difficulty']}" data-paper="{html.escape(q.get('paper') or '')}">
<h3><a href="../q/{html.escape(q['id'])}.html">{html.escape(title)}</a></h3>
<p class="stem">{inline(q.get('challenge_mechanism', ''))}</p>
{chips(q)}
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
{chips(q)}
{stimulus_html(q.get('stimulus'))}
{figure_html(q.get('figure'))}
<h2>Question</h2>
{md(q.get('question'))}
<ol class="parts">{parts}</ol>
<p class="reveal-note">Total: {q['marks']} marks. Try the question before revealing anything below.</p>
<details><summary>Reveal the answer</summary><div class="body">{md(q.get('answer'))}</div></details>
<details><summary>Markscheme notes</summary><div class="body">{md(q.get('markscheme_notes'))}</div></details>
<details><summary>Why this question is hard</summary><div class="body">{md(q.get('explanation'))}</div></details>
<h2>Metadata</h2>
<dl class="kv">
  <div><dt>Challenge lever</dt><dd>{html.escape(q.get('challenge_mechanism',''))}</dd></div>
  <div><dt>Syllabus reference</dt><dd>{html.escape(q.get('syllabus_ref',''))}</dd></div>
  <div><dt>Inspiration</dt><dd>{html.escape(prov.get('inspired_by','original'))}</dd></div>
  <div><dt>Adaptation</dt><dd>{html.escape(prov.get('adaptation',''))}</dd></div>
  <div><dt>Verification</dt><dd>{html.escape(ver.get('method',''))}</dd></div>
  <div><dt>Nearest bank match</dt><dd>{nearest}</dd></div>
  <div><dt>Nearest item here</dt><dd>{nearest_internal}</dd></div>
  <div><dt>Status</dt><dd>{html.escape(q.get('status',''))} · authored by {html.escape(q.get('authored_by',''))} · {html.escape(q.get('updated_at',''))}</dd></div>
</dl>
<div class="pager"><a href="../{slug}/index.html">← All {html.escape(SUBJECTS[slug]['short'])} questions</a></div>
"""
    return page("%s — %s" % (q["id"], SUBJECTS[slug]["short"]), body, subject=slug,
                mathjax=SUBJECTS[slug]["mathjax"])


def build_paper(slug, qs, answers=False):
    """A printable paper, or its matching answer booklet, for one subject."""
    meta = SUBJECTS[slug]
    total = sum(q["marks"] for q in qs)
    blocks = []
    for i, q in enumerate(qs, 1):
        if answers:
            blocks.append(f"""<section class="paper-q">
<h3>{i}. {html.escape(q['id'])} <span class="paper-marks">{q['marks']} marks</span></h3>
{md(q.get('answer'))}
<h4>Markscheme notes</h4>
{md(q.get('markscheme_notes'))}
</section>""")
        else:
            parts = "".join(
                '<li><span class="marks">[%s mark%s]</span><strong>(%s)</strong> %s%s</li>'
                % (p["marks"], "" if p["marks"] == 1 else "s",
                   html.escape(p["label"]), md(p["text"]),
                   " <em>(%s)</em>" % html.escape(p["command_term"]) if p.get("command_term") else "")
                for p in q.get("parts") or []
            )
            blocks.append(f"""<section class="paper-q">
<h3>{i}. {html.escape(q.get('title') or q['subtopic'])} <span class="paper-marks">{q['marks']} marks</span></h3>
<p class="paper-ref">{html.escape(q['id'])} · {html.escape(q.get('syllabus_ref', ''))} · difficulty {q['difficulty']}</p>
{stimulus_html(q.get('stimulus'))}
{figure_html(q.get('figure'))}
{md(q.get('question'))}
<ol class="parts">{parts}</ol>
</section>""")
    kind = "Answer booklet" if answers else "Question paper"
    lede = ("Answers, markschemes and examiner notes. Do not open this until you have written your own "
            "answers." if answers else
            "No answers are printed in this paper. Attempt every question in writing before opening the "
            "matching answer booklet.")
    switch = ('<a href="%s-paper.html">&#8592; Question paper</a>' % slug if answers
              else '<a href="%s-answers.html">Answer booklet &#8594;</a>' % slug)
    body = f"""
<h1>{html.escape(meta['name'])} — Challenge {kind}</h1>
<p class="lede">{len(qs)} questions · {total} marks · difficulty 4–5 · May 2028 cohort</p>
<p class="reveal-note">{lede}</p>
<p class="paper-switch">{switch}</p>
{''.join(blocks)}
"""
    return page("%s — Challenge %s" % (meta["short"], kind), body, subject=slug,
                mathjax=meta["mathjax"])


def build_subject_page(slug, qs):
    meta = SUBJECTS[slug]
    diffs = sorted({q["difficulty"] for q in qs})
    papers = sorted({q.get("paper") or "" for q in qs if q.get("paper")})
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
  <select id="f-paper" aria-label="Filter by paper"><option value="">All papers</option>
    {''.join('<option value="%s">%s</option>' % (html.escape(p, quote=True), html.escape(p)) for p in papers)}
  </select>
  <select id="f-diff" aria-label="Filter by difficulty"><option value="">All difficulties</option>
    {''.join('<option value="%s">Difficulty %s</option>' % (d, d) for d in diffs)}
  </select>
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
                 "u": "q/%s.html" % q["id"], "marks": q["marks"], "d": q["difficulty"],
                 "paper": q.get("paper") or "",
                 "s": " ".join([q["id"], q["topic"], q["subtopic"], q["syllabus_ref"],
                                " ".join(q.get("tags") or [])]).lower()}
                for slug in SUBJECTS for q in all_qs.get(slug, [])]
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
<h2>Printable papers</h2>
<p>Each subject is also assembled into a printable question paper and a matching answer booklet, so a
whole set can be attempted under exam conditions away from the screen. Open the paper, print it, then
mark against the booklet.</p>
<ul>{''.join(
    '<li><strong>%s</strong> — %d questions, %d marks · '
    '<a href="papers/%s-paper.html">question paper</a> · '
    '<a href="papers/%s-answers.html">answer booklet</a></li>'
    % (html.escape(SUBJECTS[s]['short']), len(all_qs.get(s, [])),
       sum(q['marks'] for q in all_qs.get(s, [])), s, s)
    for s in SUBJECTS if all_qs.get(s)
)}</ul>
<h2>Search all questions</h2>
<div class="controls"><input type="search" id="g" placeholder="Type at least two characters…" aria-label="Search all questions"></div>
<div id="gresults"></div>
<h2>How to use this bank</h2>
<ul>
  <li>Attempt the question in writing first — timed, closed book, under exam conditions for that paper.</li>
  <li>Only then open <em>Reveal the answer</em>. Compare method, not just the final value.</li>
  <li>Read <em>Markscheme notes</em> for what earns partial credit and what the common errors are.</li>
  <li>Read <em>Why this question is hard</em> last; it names the trap the question is built around.</li>
</ul>
"""
    extra = "<script>window.CB_INDEX = %s;</script>" % json.dumps(index_js, ensure_ascii=False)
    return page("IB Challenge Bank", body, extra_head=extra)


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
