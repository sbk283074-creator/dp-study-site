/* BPhO Round 0 — study space app
   Hash-routed SPA. No dependencies. Progress in localStorage with export/import. */

(function () {
  "use strict";

  var STORE_KEY = "bpho-r0-v1";
  var EXAM_DATE = "2026-10-02T09:00:00+07:00"; // non-UK sitting; adjust in Reference if needed

  var DATA = {
    curriculum: (window.BPHO_CURRICULUM || { modules: [] }).modules,
    questions: window.BPHO_QUESTIONS || [],
    glossary: window.BPHO_GLOSSARY || [],
    plan: window.BPHO_PLAN || []
  };

  /* ---------------- state ---------------- */

  var state = load();

  function blank() {
    return { checks: {}, answers: {}, days: {}, done: {}, mock: null, examDate: EXAM_DATE, v: 1 };
  }

  function load() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      if (!raw) return blank();
      var o = JSON.parse(raw);
      var b = blank();
      for (var k in b) if (!(k in o)) o[k] = b[k];
      return o;
    } catch (e) {
      return blank();
    }
  }

  function save() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) {}
    paintProgress();
  }

  function reset() {
    if (!confirm("Reset all BPhO progress? This cannot be undone.")) return;
    state = blank();
    save();
    render();
  }

  function exportProgress() {
    var blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "bpho-round0-progress-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  }

  function importProgress(file) {
    var fr = new FileReader();
    fr.onload = function () {
      try {
        var o = JSON.parse(fr.result);
        if (!o || typeof o !== "object") throw new Error("bad file");
        var b = blank();
        for (var k in b) if (!(k in o)) o[k] = b[k];
        state = o;
        save();
        render();
        alert("Progress imported.");
      } catch (e) {
        alert("That file could not be read as a progress export.");
      }
    };
    fr.readAsText(file);
  }

  /* ---------------- helpers ---------------- */

  function el(html) {
    var d = document.createElement("div");
    d.innerHTML = html.trim();
    return d.firstElementChild;
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function mod(code) {
    for (var i = 0; i < DATA.curriculum.length; i++) if (DATA.curriculum[i].code === code) return DATA.curriculum[i];
    return null;
  }

  function daysLeft() {
    var t = new Date(state.examDate).getTime() - Date.now();
    return Math.max(0, Math.ceil(t / 86400000));
  }

  function pct(n, d) { return d ? Math.round((n / d) * 100) : 0; }

  function allChecks() {
    var out = [];
    DATA.curriculum.forEach(function (m) { (m.checklist || []).forEach(function (c) { out.push({ m: m, c: c }); }); });
    return out;
  }

  function modChecks(code) {
    var m = mod(code);
    return (m && m.checklist) || [];
  }

  function modDone(code) {
    return modChecks(code).filter(function (c) { return state.checks[code + ":" + c.id]; }).length;
  }

  function flagClass(f) {
    var s = String(f || "").toUpperCase();
    if (s === "CORE") return "flag--core";
    if (s === "NEW") return "flag--new";
    if (s === "R1-ONLY") return "flag--r1";
    if (s === "SKIP") return "flag--skip";
    return "flag--tierA";
  }

  /* ---------------- reveal ---------------- */

  function revealBlock(label, html) {
    var id = "rv" + Math.random().toString(36).slice(2, 9);
    return '<div class="reveal" id="' + id + '">' +
      '<button class="reveal__btn" type="button" data-reveal="' + id + '">' + esc(label) + '</button>' +
      '<div class="reveal__body">' + html + "</div></div>";
  }

  function bindReveals(root) {
    root.querySelectorAll("[data-reveal]").forEach(function (b) {
      b.addEventListener("click", function () {
        var box = document.getElementById(b.getAttribute("data-reveal"));
        if (!box) return;
        box.classList.toggle("open");
        var open = box.classList.contains("open");
        var t = b.textContent;
        if (open) { b.setAttribute("data-orig", t); b.textContent = "Hide solution"; }
        else { b.textContent = b.getAttribute("data-orig") || t; }
      });
    });
  }

  /* ---------------- question rendering ---------------- */

  function questionCard(q, opts) {
    opts = opts || {};
    var answered = state.answers[q.id];
    var html = '<div class="mcq" id="q-' + q.id + '">';
    html += '<div class="mcq__meta">' +
      '<span class="mcq__id">' + esc(q.id) + "</span>" +
      "<span>" + esc(mod(q.module) ? mod(q.module).title : q.module) + "</span>" +
      "<span>· " + esc(q.topic) + "</span>" +
      '<span>· <span class="flag ' + (q.diff === 3 ? "flag--r1" : q.diff === 2 ? "flag--new" : "flag--tierA") + '">' +
      (q.diff === 3 ? "challenge" : q.diff === 2 ? "extension" : "core") + "</span></span>" +
      "</div>";
    html += '<p class="mcq__q">' + q.q + "</p>";
    html += '<div class="mcq__opts">';
    q.opts.forEach(function (o, i) {
      var cls = "opt";
      if (answered) {
        if (i === q.ans) cls += " right";
        else if (answered === "ABCDE"[i]) cls += " wrong";
      }
      html += '<button class="' + cls + '" type="button" data-q="' + q.id + '" data-k="' + "ABCDE"[i] + '">' +
        '<span class="opt__k">' + "ABCDE"[i] + '</span><span class="opt__v">' + o + "</span></button>";
    });
    html += "</div>";
    html += '<div class="mcq__foot">';
    if (answered) {
      var ok = answered === "ABCDE"[q.ans];
      html += '<span class="mcq__verdict ' + (ok ? "ok" : "no") + '">' +
        (ok ? "Correct" : "You chose " + esc(answered) + " — answer is " + "ABCDE"[q.ans]) + "</span>";
    } else {
      html += '<span class="small">Pick an option.</span>';
    }
    html += '<button class="btn btn--sm" type="button" data-ai="' + q.id + '">Ask AI about this</button>';
    html += "</div>";
    html += revealBlock("Show full solution", q.sol + (q.trap ? '<p><b>Trap:</b> ' + q.trap + "</p>" : ""));
    html += "</div>";
    return html;
  }

  function bindQuestions(root) {
    root.querySelectorAll(".opt[data-q]").forEach(function (b) {
      b.addEventListener("click", function () {
        var qid = b.getAttribute("data-q");
        if (state.answers[qid]) return;
        state.answers[qid] = b.getAttribute("data-k");
        save();
        var card = document.getElementById("q-" + qid);
        var q = byQid(qid);
        if (card && q) {
          card.outerHTML = questionCard(q);
          var fresh = document.getElementById("q-" + qid);
          if (fresh) { bindQuestions(fresh.parentNode || fresh); bindReveals(fresh.parentNode || fresh); }
        }
      });
    });
    root.querySelectorAll("[data-ai]").forEach(function (b) {
      b.addEventListener("click", function () {
        var q = byQid(b.getAttribute("data-ai"));
        if (!q) return;
        var ctx = "BPhO Round 0 practice question " + q.id + " (" + q.topic + ")\n\n" + q.q +
          "\n\nOptions:\n" + q.opts.map(function (o, i) { return "ABCDE"[i] + ") " + o; }).join("\n") +
          "\n\nCorrect answer: " + "ABCDE"[q.ans] + "\n\nOfficial solution:\n" + q.sol;
        if (window.dpAI && window.dpAI.open) {
          window.dpAI.open({
            ref: q.id,
            subject: "BPhO Round 0",
            topic: q.topic,
            context: ctx,
            prompt: "Explain this question from first principles as if I have forgotten the topic. Show every algebraic step, say why each step is allowed, and point out where the wrong options come from.",
            display: "Explain " + q.id,
            autoSend: true
          });
        } else {
          alert("The Ask AI assistant is not loaded. Open this page from the DP study site to use it.");
        }
      });
    });
  }

  function byQid(id) {
    for (var i = 0; i < DATA.questions.length; i++) if (DATA.questions[i].id === id) return DATA.questions[i];
    return null;
  }

  /* ---------------- views ---------------- */

  function viewHome() {
    var checks = allChecks();
    var doneChecks = checks.filter(function (x) { return state.checks[x.m.code + ":" + x.c.id]; }).length;
    var answered = Object.keys(state.answers).length;
    var correct = DATA.questions.filter(function (q) { return state.answers[q.id] === "ABCDE"[q.ans]; }).length;
    var days = daysLeft();
    var planDone = DATA.plan.filter(function (d) { return state.days[d.day]; }).length;

    var h = '<a class="toplink" href="../index.html">← Back to DP Learning</a>';
    h += "<h1>BPhO Round 0 — the sprint</h1>";
    h += '<p class="lede">Everything you need for the paper, written on the assumption that you have forgotten the topic. Derivations first, worked examples, then competition-style questions with full solutions.</p>';

    h += '<div class="grid2">' +
      '<div class="stat"><b>' + days + "</b><span>days until the paper</span></div>" +
      '<div class="stat"><b>' + doneChecks + " / " + checks.length + "</b><span>topic checklist items ticked</span></div>" +
      '<div class="stat"><b>' + answered + " / " + DATA.questions.length + "</b><span>practice questions attempted</span></div>" +
      '<div class="stat"><b>' + pct(correct, answered || 1) + '%</b><span>accuracy on attempted</span></div>' +
      "</div>";

    h += '<h2>Start here</h2>';
    h += '<div class="card">' +
      "<p><b>Read this before the plan.</b> The paper is 25 multiple-choice questions in 60 minutes with " +
      "<b>no calculator</b>. That means the binding constraint is speed and estimation, not depth. " +
      "You need about 9–10 genuinely earned marks out of 25 to reach the qualifying line of 11 " +
      "(guessing supplies the rest, since there is no negative marking).</p>" +
      '<p class="sub">Target: 11/25 — the UK-region qualifying line, which is the route open to you as an overseas candidate.</p>' +
      "</div>";

    h += '<h2>The plan</h2>';
    h += '<div class="card">' +
      "<p>" + planDone + " of " + DATA.plan.length + " days marked complete.</p>" +
      '<div class="bar bar--purple"><i style="width:' + pct(planDone, DATA.plan.length) + '%"></i></div>' +
      '<p style="margin-top:14px"><a class="btn btn--primary" href="#/plan">Open the plan</a></p>' +
      "</div>";

    h += '<h2>Modules</h2>';
    h += '<p class="sub">In the order the plan covers them. Tick items off as you go.</p>';
    DATA.curriculum.forEach(function (m) {
      var d = modDone(m.code), t = modChecks(m.code).length;
      h += '<div class="card" style="padding:14px 18px">' +
        '<div style="display:flex;gap:12px;align-items:baseline;flex-wrap:wrap">' +
        '<span class="navlink__code" style="flex:0 0 auto">' + esc(m.code) + "</span>" +
        '<a href="#/m/' + m.code + '" style="font-weight:600;font-size:15.5px">' + esc(m.title) + "</a>" +
        '<span class="small" style="margin-left:auto">' + d + "/" + t + "</span></div>" +
        '<div class="bar" style="margin-top:8px"><i style="width:' + pct(d, t) + '%"></i></div>' +
        "</div>";
    });

    h += '<h2>Your progress</h2>';
    h += '<div class="card"><p class="small">Saved in this browser. Export it if you want a backup or to move devices.</p>' +
      '<div class="toolbar"><button class="btn" data-act="export">Export progress</button>' +
      '<label class="btn" style="display:inline-block">Import progress<input type="file" accept="application/json" data-act="import" style="display:none"></label>' +
      '<button class="btn" data-act="reset">Reset</button></div></div>';

    h += '<footer class="foot">Sources: the official BPhO Round 0 sample paper, the official Round 0 scope statement, ' +
      "the AQA AS Physics 7407 specification, and archived BPhO Round 1 papers. Evidence tiers are marked on every module.</footer>";

    return h;
  }

  function viewPlan() {
    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>The plan</h1>";
    h += '<p class="lede">Days 1–14 run from 16 to 29 September, then two buffer days follow. Each day is sized to be finishable — roughly two to three hours.</p>';
    h += '<div class="callout callout--key"><p><b>If you fall behind, cut from the bottom, not the middle.</b> ' +
      "Circuits, the toolkit and kinematics carry the most marks. Thermal, the <code>R1-ONLY</code> material and the buffer days are the first things to drop.</p></div>";

    DATA.plan.forEach(function (d) {
      var done = !!state.days[d.day];
      h += '<div class="day' + (done ? " day--done" : "") + '">' +
        '<div class="day__head"><span class="day__n">Day ' + d.day + '</span>' +
        '<span class="day__date">' + esc(d.date) + "</span>" +
        '<span class="small" style="margin-left:auto">' + esc(d.mins) + " min</span></div>" +
        '<p class="day__title">' + esc(d.title) + "</p>" +
        '<p class="small">' + esc(d.focus) + "</p>" +
        '<div class="day__mods">' + d.mods.map(function (c) {
          var m = mod(c);
          return m ? '<a href="#/m/' + c + '">' + esc(c) + " · " + esc(m.title) + "</a>" : "";
        }).join("") + "</div>" +
        '<ul class="tight">' + d.tasks.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>" +
        '<label class="small" style="display:flex;gap:8px;align-items:center;cursor:pointer">' +
        '<input type="checkbox" data-day="' + d.day + '"' + (done ? " checked" : "") + ' style="width:15px;height:15px;accent-color:var(--accent)">' +
        "Mark this day complete</label>" +
        "</div>";
    });
    return h;
  }

  function viewModule(code) {
    var m = mod(code);
    if (!m) return "<h1>Module not found</h1><p><a href=\"#/\">Back to overview</a></p>";

    var d = modDone(code), t = modChecks(code).length;

    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>" + esc(m.code) + " · " + esc(m.title) + "</h1>";
    h += '<p class="lede">' + m.why + "</p>";
    h += '<div class="toolbar">' +
      '<span class="flag flag--tierA">' + esc(m.tier) + "</span>" +
      '<span class="small">' + d + " of " + t + " items ticked</span></div>";
    h += '<div class="bar" style="margin-bottom:20px"><i style="width:' + pct(d, t) + '%"></i></div>';

    if (m.warn) h += '<div class="callout callout--warn">' + m.warn + "</div>";

    (m.sections || []).forEach(function (s) {
      h += "<h2>" + esc(s.h) + "</h2>";
      h += s.body;
    });

    if (m.examples && m.examples.length) {
      h += "<h2>Worked examples</h2>";
      h += '<p class="sub">Try each one on paper before revealing the solution.</p>';
      m.examples.forEach(function (x, i) {
        h += '<div class="ex"><div class="ex__head"><span class="ex__tag">Example ' + (i + 1) + "</span>" +
          '<span class="small">' + esc(x.tag || "") + "</span></div>" +
          '<p class="ex__q">' + x.q + "</p>" +
          revealBlock("Show full solution", x.sol) +
          "</div>";
      });
    }

    if (m.traps && m.traps.length) {
      h += "<h2>Common traps</h2>";
      h += '<div class="callout callout--bad"><ul class="tight" style="margin:0">' +
        m.traps.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ul></div>";
    }

    if (m.checklist && m.checklist.length) {
      h += "<h2>Checklist</h2>";
      h += '<ul class="check">' + m.checklist.map(function (c) {
        var id = code + ":" + c.id;
        var on = !!state.checks[id];
        return '<li><input type="checkbox" id="ck-' + esc(id) + '" data-check="' + esc(id) + '"' + (on ? " checked" : "") + ">" +
          '<label for="ck-' + esc(id) + '"><span class="check__id">' + esc(c.id) + "</span>" +
          '<span class="flag ' + flagClass(c.flag) + '">' + esc(c.flag) + "</span> " + c.text + "</label></li>";
      }).join("") + "</ul>";
    }

    var qs = DATA.questions.filter(function (q) { return q.module === code; });
    if (qs.length) {
      h += "<h2>Practice — " + qs.length + " questions</h2>";
      h += '<p class="sub">Round 0 format: five options, no calculator, one mark each.</p>';
      h += '<p><a class="btn" href="#/practice/' + code + '">Practise this module only</a></p>';
    }

    return h;
  }

  var practiceFilter = "all";
  var practiceDiff = "all";

  function viewPractice(code) {
    var list = DATA.questions.slice();
    if (code) list = list.filter(function (q) { return q.module === code; });
    if (practiceDiff !== "all") list = list.filter(function (q) { return String(q.diff) === practiceDiff; });

    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>Practice</h1>";
    h += '<p class="lede">Competition-style multiple choice. Attempt each one properly — work it out on paper, then reveal the solution.</p>';

    h += '<div class="toolbar">' +
      '<button class="btn btn--primary" data-act="mock">Start a 25-question mock</button>' +
      '<span class="small">60 minutes, no calculator — same conditions as the paper.</span></div>';

    h += '<div class="chiprow">' +
      chip("all", "All modules", practiceFilter === "all", "pf") +
      DATA.curriculum.filter(function (m) {
        return DATA.questions.some(function (q) { return q.module === m.code; });
      }).map(function (m) {
        return chip(m.code, m.code + " · " + m.title, practiceFilter === m.code, "pf");
      }).join("") + "</div>";

    h += '<div class="chiprow">' +
      chip("all", "Any difficulty", practiceDiff === "all", "pd") +
      chip("1", "Core", practiceDiff === "1", "pd") +
      chip("2", "Extension", practiceDiff === "2", "pd") +
      chip("3", "Challenge", practiceDiff === "3", "pd") + "</div>";

    if (!list.length) {
      h += '<div class="callout callout--warn"><p>No questions match that filter.</p></div>';
    } else {
      h += '<p class="small">' + list.length + " questions shown.</p>";
      list.forEach(function (q) { h += questionCard(q); });
    }
    return h;
  }

  function chip(val, label, on, group) {
    return '<button class="chip' + (on ? " on" : "") + '" type="button" data-chip="' + group + '" data-val="' + esc(val) + '">' + esc(label) + "</button>";
  }

  function viewGlossary() {
    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>Glossary</h1>";
    h += '<p class="lede">Every term the paper might use, with the 中文 for it. The exam is in English, so knowing the English term is what matters — the Chinese is there to make it stick.</p>';
    h += '<div class="toolbar"><input type="text" id="glossq" placeholder="Filter terms…" style="font:inherit;font-size:14px;padding:8px 12px;border:1px solid var(--line-2);border-radius:8px;min-width:240px"></div>';
    h += '<div class="gloss" id="glosslist">' + DATA.glossary.map(function (g) {
      return '<div class="gloss__item" data-term="' + esc((g.en + " " + g.zh + " " + g.def).toLowerCase()) + '">' +
        '<span class="gloss__en">' + esc(g.en) + '</span><span class="gloss__zh">' + esc(g.zh) + "</span>" +
        '<p class="gloss__def">' + esc(g.def) + "</p></div>";
    }).join("") + "</div>";
    return h;
  }

  function viewReference() {
    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>Reference</h1>";

    h += "<h2>The paper</h2>";
    h += "<table><tbody>" +
      "<tr><th>Format</th><td>25 single-answer multiple choice, options A–E</td></tr>" +
      "<tr><th>Time</th><td>60 minutes — about 2.4 minutes per question</td></tr>" +
      "<tr><th>Calculator</th><td><b>Not permitted.</b> A standard formula booklet may be used</td></tr>" +
      "<tr><th>Marking</th><td>1 mark each, <b>no negative marking</b>, maximum 25</td></tr>" +
      "<tr><th>Awards</th><td>None — it is a selection round</td></tr>" +
      "<tr><th>Target</th><td>11/25 for the UK-region qualifying line</td></tr>" +
      "</tbody></table>";

    h += "<h2>Constants worth memorising</h2>";
    h += '<p class="sub">The data booklet is available, but at 2.4 minutes a question there is no time to look things up.</p>';
    h += "<table><thead><tr><th>Quantity</th><th>Value</th></tr></thead><tbody>" +
      "<tr><td>Gravitational field strength <code>g</code></td><td>9.81 N kg⁻¹</td></tr>" +
      "<tr><td>Speed of light <code>c</code></td><td>3.00 × 10⁸ m s⁻¹</td></tr>" +
      "<tr><td>Elementary charge <code>e</code></td><td>1.60 × 10⁻¹⁹ C</td></tr>" +
      "<tr><td>Planck constant <code>h</code></td><td>6.63 × 10⁻³⁴ J s</td></tr>" +
      "<tr><td>Electron volt</td><td>1 eV = 1.60 × 10⁻¹⁹ J</td></tr>" +
      "<tr><td>Radius of the Earth</td><td>≈ 6.4 × 10⁶ m</td></tr>" +
      "<tr><td>Earth–Sun distance</td><td>≈ 1.5 × 10¹¹ m</td></tr>" +
      "<tr><td>Length of a day</td><td>86 400 s</td></tr>" +
      "</tbody></table>";

    h += "<h2>Approximations BPhO supplies</h2>";
    h += '<p class="sub">These appear on BPhO\'s own constant sheet, which means they are expected tools rather than optional tricks.</p>';
    h += '<div class="formula">(1 + x)ⁿ ≈ 1 + nx&nbsp;&nbsp;&nbsp;(x ≪ 1)\n1/(1 + x)ⁿ ≈ 1 − nx&nbsp;&nbsp;&nbsp;(x ≪ 1)\neˣ ≈ 1 + x\n\n' +
      "tan θ ≈ sin θ ≈ θ&nbsp;&nbsp;&nbsp;(θ ≪ 1)\ncos θ ≈ 1 − θ²/2&nbsp;&nbsp;&nbsp;(θ ≪ 1)</div>";
    h += '<div class="callout callout--key"><p><b>The one to internalise:</b> <code>√(a² + d²) − a ≈ d²/2a</code> when <code>d ≪ a</code>. ' +
      "It is the binomial approximation in disguise and it turns up whenever a point is displaced slightly from a symmetrical position.</p></div>";

    h += "<h2>Technique checklist</h2>";
    h += "<table><thead><tr><th>Move</th><th>When to reach for it</th></tr></thead><tbody>" +
      "<tr><td>Dimensional analysis</td><td>You are asked for the form of a relationship and no numbers are given</td></tr>" +
      "<tr><td>Ratio reasoning</td><td>The question asks for a ratio — shared constants cancel, so never compute them</td></tr>" +
      "<tr><td>Limiting cases</td><td>Substitute <code>n → 1</code>, <code>θ → 0</code>, <code>m → 0</code> and see which options die</td></tr>" +
      "<tr><td>Graph shape</td><td>Which curve describes the relationship — reason about asymptotes, not plotted values</td></tr>" +
      "<tr><td>Order of magnitude</td><td>Options differ by powers of ten; estimate to within a factor of 3 and pick</td></tr>" +
      "<tr><td>Guess</td><td>No negative marking. Never leave a blank</td></tr>" +
      "</tbody></table>";

    h += "<h2>Your settings</h2>";
    h += '<div class="card"><p class="small">Exam date drives the countdown. Change it if your sitting differs from the default.</p>' +
      '<div class="toolbar"><input type="date" id="examdate" value="' + esc(String(state.examDate).slice(0, 10)) + '" style="font:inherit;font-size:14px;padding:7px 11px;border:1px solid var(--line-2);border-radius:8px">' +
      '<button class="btn" data-act="setdate">Save date</button></div></div>';

    h += "<h2>What is not on the paper</h2>";
    h += '<div class="callout callout--bad"><p>Officially excluded: electric fields, magnetic fields, gravitational fields, particle physics, and RC charging or discharging (time constants). ' +
      "Everything in the modules flagged <code>R1-ONLY</code> is Round 1 material and is insurance only.</p></div>";

    h += '<footer class="foot">Evidence: official BPhO Round 0 page and sample paper (Tier A); archived BPhO Round 1 Section 1 and Section 2 papers, 2020–2024 (Tier B); AQA AS Physics 7407 specification (Tier A, for the definition of "Year 12 topics").</footer>';
    return h;
  }

  function viewMock() {
    var m = state.mock;
    if (!m) return "<h1>No mock in progress</h1><p><a href=\"#/practice\">Back to practice</a></p>";

    var spent = Math.floor((Date.now() - m.started) / 1000);
    var left = Math.max(0, m.seconds - spent);

    var h = '<a class="toplink" href="#/practice">← Practice</a>';
    h += "<h1>Mock paper</h1>";
    h += '<div class="callout callout--key"><p><b>' + m.ids.length + " questions · " + Math.floor(left / 60) + ":" +
      ("0" + (left % 60)).slice(-2) + " remaining.</b> No calculator. One mark each, no negative marking.</p></div>";

    h += '<div class="toolbar"><button class="btn btn--primary" data-act="marksubmit">Mark my paper</button>' +
      '<button class="btn" data-act="mockquit">Abandon</button></div>';

    m.ids.forEach(function (id, i) {
      var q = byQid(id);
      if (!q) return;
      h += '<div class="mcq"><div class="mcq__meta"><span class="mcq__id">Q' + (i + 1) + "</span>" +
        "<span>" + esc(q.topic) + "</span></div>" +
        '<p class="mcq__q">' + q.q + "</p><div class=\"mcq__opts\">" +
        q.opts.map(function (o, k) {
          var sel = m.picks[id] === "ABCDE"[k];
          return '<button class="opt' + (sel ? " right" : "") + '" type="button" data-mock="' + id + '" data-k="' + "ABCDE"[k] + '">' +
            '<span class="opt__k">' + "ABCDE"[k] + '</span><span class="opt__v">' + o + "</span></button>";
        }).join("") + "</div></div>";
    });
    return h;
  }

  function viewMockResult() {
    var m = state.mock;
    if (!m || !m.marked) return "<h1>No result</h1><p><a href=\"#/practice\">Back to practice</a></p>";
    var score = 0, blank = 0;
    var rows = m.ids.map(function (id, i) {
      var q = byQid(id);
      var pick = m.picks[id] || null;
      var ok = pick === "ABCDE"[q.ans];
      if (ok) score++; else if (!pick) blank++;
      return "<tr><td>Q" + (i + 1) + "</td><td>" + esc(q.topic) + "</td><td>" + (pick || "—") +
        "</td><td>" + "ABCDE"[q.ans] + "</td><td>" + (ok ? "✓" : "✗") + "</td></tr>";
    }).join("");

    var h = '<a class="toplink" href="#/practice">← Practice</a>';
    h += "<h1>Mock result</h1>";
    h += '<div class="grid2">' +
      '<div class="stat"><b>' + score + " / " + m.ids.length + "</b><span>correct</span></div>" +
      '<div class="stat"><b>' + (score >= 11 ? "Above" : "Below") + "</b><span>the 11/25 qualifying line</span></div>" +
      '<div class="stat"><b>' + blank + "</b><span>left blank — never do this</span></div>" +
      "</div>";

    h += '<div class="callout ' + (score >= 11 ? "callout--good" : "callout--warn") + '"><p>' +
      (score >= 11
        ? "<b>You are on track.</b> Keep the accuracy and work on speed."
        : "<b>Below the line.</b> Look at which topics the misses cluster in — that is where the next session goes.") +
      "</p></div>";

    h += "<h2>Question by question</h2>";
    h += "<table><thead><tr><th>#</th><th>Topic</th><th>You</th><th>Answer</th><th></th></tr></thead><tbody>" + rows + "</tbody></table>";

    h += '<div class="toolbar"><button class="btn" data-act="mockclear">Clear and practise freely</button></div>';

    h += "<h2>Review the ones you missed</h2>";
    m.ids.forEach(function (id) {
      var q = byQid(id);
      if (!q) return;
      if (m.picks[id] === "ABCDE"[q.ans]) return;
      h += questionCard(q);
    });
    return h;
  }

  /* ---------------- router ---------------- */

  function render() {
    var hash = location.hash.replace(/^#\/?/, "");
    var parts = hash.split("/").filter(Boolean);
    var view = parts[0] || "home";
    var main = document.getElementById("main");
    var html;

    if (view === "home") html = viewHome();
    else if (view === "plan") html = viewPlan();
    else if (view === "m") html = viewModule(parts[1]);
    else if (view === "practice") { if (parts[1]) practiceFilter = parts[1]; html = viewPractice(practiceFilter === "all" ? null : practiceFilter); }
    else if (view === "glossary") html = viewGlossary();
    else if (view === "reference") html = viewReference();
    else if (view === "mock") html = (state.mock && state.mock.marked) ? viewMockResult() : viewMock();
    else html = "<h1>Not found</h1><p><a href=\"#/\">Back to overview</a></p>";

    main.innerHTML = html;
    window.scrollTo(0, 0);
    bindAll(main);
    paintNav(view, parts[1]);
  }

  function bindAll(root) {
    bindReveals(root);
    bindQuestions(root);

    root.querySelectorAll("[data-check]").forEach(function (b) {
      b.addEventListener("change", function () {
        var id = b.getAttribute("data-check");
        if (b.checked) state.checks[id] = true; else delete state.checks[id];
        save();
      });
    });

    root.querySelectorAll("[data-day]").forEach(function (b) {
      b.addEventListener("change", function () {
        var d = b.getAttribute("data-day");
        if (b.checked) state.days[d] = true; else delete state.days[d];
        save();
        var box = b.closest(".day");
        if (box) box.classList.toggle("day--done", b.checked);
      });
    });

    root.querySelectorAll("[data-chip]").forEach(function (b) {
      b.addEventListener("click", function () {
        var g = b.getAttribute("data-chip"), v = b.getAttribute("data-val");
        if (g === "pf") { practiceFilter = v; location.hash = v === "all" ? "#/practice" : "#/practice/" + v; }
        if (g === "pd") { practiceDiff = v; render(); }
      });
    });

    root.querySelectorAll("[data-mock]").forEach(function (b) {
      b.addEventListener("click", function () {
        state.mock.picks[b.getAttribute("data-mock")] = b.getAttribute("data-k");
        save();
        render();
      });
    });

    var gq = document.getElementById("glossq");
    if (gq) {
      gq.addEventListener("input", function () {
        var v = gq.value.toLowerCase().trim();
        document.querySelectorAll("#glosslist .gloss__item").forEach(function (n) {
          n.classList.toggle("hidden", v && n.getAttribute("data-term").indexOf(v) === -1);
        });
      });
    }

    root.querySelectorAll("[data-act]").forEach(function (b) {
      b.addEventListener("click", function () { act(b.getAttribute("data-act")); });
    });

    var imp = root.querySelector('[data-act="import"]');
    if (imp) imp.addEventListener("change", function () { if (imp.files[0]) importProgress(imp.files[0]); });
  }

  function act(a) {
    if (a === "export") exportProgress();
    else if (a === "reset") reset();
    else if (a === "mock") startMock();
    else if (a === "marksubmit") { state.mock.marked = true; save(); location.hash = "#/mock"; render(); }
    else if (a === "mockquit") { if (confirm("Abandon this mock?")) { state.mock = null; save(); location.hash = "#/practice"; } }
    else if (a === "mockclear") { state.mock = null; save(); location.hash = "#/practice"; }
    else if (a === "setdate") {
      var v = document.getElementById("examdate");
      if (v && v.value) { state.examDate = v.value + "T09:00:00+07:00"; save(); alert("Saved."); render(); }
    }
  }

  function startMock() {
    var pool = DATA.questions.slice();
    for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
    var ids = pool.slice(0, Math.min(25, pool.length)).map(function (q) { return q.id; });
    state.mock = { ids: ids, picks: {}, started: Date.now(), seconds: 60 * 60, marked: false };
    save();
    location.hash = "#/mock";
  }

  function paintNav(view, code) {
    document.querySelectorAll(".navlink").forEach(function (a) {
      var t = a.getAttribute("data-view");
      var c = a.getAttribute("data-code");
      var on = (t === view && (t !== "m" || c === code));
      a.classList.toggle("on", !!on);
    });
  }

  function paintProgress() {
    var checks = allChecks();
    var done = checks.filter(function (x) { return state.checks[x.m.code + ":" + x.c.id]; }).length;
    var bar = document.getElementById("overallbar");
    if (bar) bar.style.width = pct(done, checks.length) + "%";
    var lbl = document.getElementById("overallpct");
    if (lbl) lbl.textContent = pct(done, checks.length) + "%";

    document.querySelectorAll("[data-tick]").forEach(function (n) {
      var c = n.getAttribute("data-tick");
      var d = modDone(c), t = modChecks(c).length;
      n.textContent = d === t && t ? "✓" : (d ? d + "/" + t : "");
    });
  }

  /* ---------------- boot ---------------- */

  function buildNav() {
    var nav = document.getElementById("nav");
    var h = "";
    h += '<div class="side__count"><b id="overallpct">0%</b><span>of the checklist complete</span>' +
      '<div class="bar bar--purple" style="margin-top:8px"><i id="overallbar" style="width:0%"></i></div></div>';

    h += '<div class="side__group"><h4>Study</h4>' +
      '<a class="navlink" data-view="home" href="#/"><span class="navlink__code">◎</span><span class="navlink__t">Overview</span></a>' +
      '<a class="navlink" data-view="plan" href="#/plan"><span class="navlink__code">▤</span><span class="navlink__t">The plan</span></a>' +
      '<a class="navlink" data-view="practice" href="#/practice"><span class="navlink__code">✎</span><span class="navlink__t">Practice</span></a>' +
      "</div>";

    var groups = { 1: "Priority 1", 2: "Priority 2", 3: "Priority 3", 4: "Insurance" };
    [1, 2, 3, 4].forEach(function (p) {
      var ms = DATA.curriculum.filter(function (m) { return m.priority === p; });
      if (!ms.length) return;
      h += '<div class="side__group"><h4>' + groups[p] + "</h4>";
      ms.forEach(function (m) {
        h += '<a class="navlink" data-view="m" data-code="' + m.code + '" href="#/m/' + m.code + '">' +
          '<span class="navlink__code">' + esc(m.code) + '</span>' +
          '<span class="navlink__t">' + esc(m.short || m.title) + '</span>' +
          '<span class="navlink__tick" data-tick="' + m.code + '"></span></a>';
      });
      h += "</div>";
    });

    h += '<div class="side__group"><h4>Tools</h4>' +
      '<a class="navlink" data-view="glossary" href="#/glossary"><span class="navlink__code">文</span><span class="navlink__t">Glossary · 词汇</span></a>' +
      '<a class="navlink" data-view="reference" href="#/reference"><span class="navlink__code">≡</span><span class="navlink__t">Reference</span></a>' +
      '<a class="navlink" href="../index.html"><span class="navlink__code">←</span><span class="navlink__t">DP Learning</span></a>' +
      "</div>";

    nav.innerHTML = h;
    paintProgress();
  }

  window.addEventListener("hashchange", render);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  function boot() {
    buildNav();
    render();
    setInterval(function () {
      if (location.hash.indexOf("#/mock") === 0 && state.mock && !state.mock.marked) render();
    }, 30000);
  }
})();
