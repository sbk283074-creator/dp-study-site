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
    plan: window.BPHO_PLAN || [],
    guidance: window.BPHO_GUIDANCE || {},
    priority: window.BPHO_PRIORITY || null,
    concepts: window.BPHO_CONCEPTS || [],
    /* The downloadable PDFs, read from the generated manifest.  Empty if the PDFs were
       never built, and the Papers area then says so instead of offering dead links. */
    papers: window.BPHO_PAPERS || [],
    papersBuilt: window.BPHO_PAPERS_BUILT || ""
  };

  /* ---------------- what the 2025 paper actually tested ----------------
     One real Round 0 paper exists, so it is the only hard evidence about where the 25 marks go.
     `PRI` is derived from the bank itself (data/priority.js) and drives the ordering of the nav,
     the overview, and the practice filters. Everything degrades gracefully if it is missing. */
  var PRI = DATA.priority;
  function pmod(code) { return PRI ? PRI.forCode(code) : null; }              /* {code,n,rel,rank,...} */
  function pcount(code) { var m = pmod(code); return m ? m.n : 0; }           /* marks on the paper */
  function prank(code) { var m = pmod(code); return m ? m.rank : 99; }
  /* most-tested first, falling back to the hand-set module priority when counts tie.
     Takes module OBJECTS (DATA.curriculum entries) — hence the .code lookups. */
  function yieldSort(a, b) {
    return (pcount(b.code) - pcount(a.code)) || (prank(a.code) - prank(b.code)) ||
      ((a.priority || 9) - (b.priority || 9)) || a.code.localeCompare(b.code);
  }

  /* ---------------- question labels and paper names ----------------
     Two banks share this app: the 2025 paper ("R0-01".."R0-25") and the 2025 sample
     sheet ("R0S-01".."R0S-12"). A single replace("R0-", "Q") is not enough -- the
     sample ids contain no "R0-" at all, so they leaked through as "R0S-01" into links
     that read "Q..." everywhere else. Read the prefix explicitly instead. */
  /* Three banks share this app now: the 2025 paper ("R0-01".."R0-25"), the 2025 sample
     sheet ("R0S-01".."R0S-12") and the original drill bank ("S01-01".."S40-25"). A drill
     id already reads as "section 01, question 01", so it is shown as it stands -- but it
     needs an explicit branch of its own, because the catch-all `replace("R0-", "Q")`
     below is a no-op on it and would have passed it through looking like a match. */
  var BANK_ID = /^S(\d\d)-(\d\d)$/;
  function qLabel(id) {
    var t = String(id);
    if (t.indexOf("R0S-") === 0) return "S" + t.slice(4);
    if (BANK_ID.test(t)) return t;
    return t.replace("R0-", "Q");
  }
  function qLabelLong(id) {
    var t = String(id);
    if (t.indexOf("R0S-") === 0) return "Sample question S" + t.slice(4);
    var m = BANK_ID.exec(t);
    if (m) return "Drill bank section " + (+m[1]) + ", question " + (+m[2]);
    return t.replace("R0-", "Question ");
  }
  /* The card flag. "R0-SAMPLE" is a tag, not English. */
  function paperLabel(p) {
    if (p === "R0-SAMPLE") return "2025 sample";
    var m = /^BANK-S(\d\d)$/.exec(String(p));
    if (m) return "Drill bank section " + (+m[1]);
    return String(p).replace("R0-", "R0 ");
  }
  /* Every drill-bank paper tag actually present in the data, in order.  Read from the
     bank rather than hardcoded, so publishing section 2 needs no change here. */
  function bankTags() {
    var seen = [], out = [];
    DATA.questions.forEach(function (q) {
      if (q.paper && q.paper.indexOf("BANK-") === 0 && seen.indexOf(q.paper) < 0) {
        seen.push(q.paper); out.push(q.paper);
      }
    });
    return out.sort();
  }

  /* Round 0 gives 60 minutes for 25 questions -- 2.4 minutes each. The fixed-paper
     mock used to hardcode 60 * 60 seconds, which would have handed the 12-question
     sample sheet a full hour, nearly three times the pace the paper actually runs at. */
  var SECONDS_PER_QUESTION = 144;
  function paperSeconds(n) { return n * SECONDS_PER_QUESTION; }
  function fmtMinutes(sec) { return Math.round(sec / 60) + " minutes"; }
  /* Download sizes are shown so a 1.2 MB markscheme is not a surprise on a phone. */
  function fmtBytes(b) {
    if (!b) return "";
    return b >= 1048576 ? (b / 1048576).toFixed(1) + " MB" : Math.round(b / 1024) + " KB";
  }

  /* ---------------- state ---------------- */

  var state = load();

  function blank() {
    return { checks: {}, answers: {}, days: {}, done: {}, read: {}, mock: null, selftest: {},
             examDate: EXAM_DATE, v: 1 };
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
      (q.paper ? '<span class="flag flag--paper">' + esc(paperLabel(q.paper)) + "</span>" : "") +
      "</div>";
    /* the topics this question actually draws on — clicking one opens that module */
    if (q.rel && q.rel.length) {
      html += '<div class="mcq__rel"><span class="small">Draws on:</span> ' +
        q.rel.map(function (r) {
          return '<a class="relchip" href="#/m/' + esc(r[0]) + '"><b>' + esc(r[0]) + "</b>" + esc(r[1]) + "</a>";
        }).join("") + "</div>";
    }
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
    html += revealBlock("Show full solution",
      q.sol + (q.trap ? '<p><b>Trap:</b> ' + q.trap + "</p>" : "") +
      ((q.key || []).length
        ? '<div class="mcq__rel"><span class="small">The key points this question turns on:</span> ' +
          keyChips(q.key) + "</div>"
        : ""));
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

    h += '<h2>Where to start</h2>';
    h += '<p class="sub">Modules in the order their prerequisites allow. Each one opens with what it ' +
      "assumes you can already do, and a three-question check you can take before committing to it.</p>";
    h += '<ol class="steps">';
    gdOrder().forEach(function (c) {
      var mm = mod(c);
      var g = gd(c);
      var st = state.selftest[c];
      var badge = "";
      if (st && st.done) {
        var n = (g.starter || []).filter(function (s, i) { return (st.picks || {})[i] === s.ans; }).length;
        badge = ' <span class="flag ' + (n === 3 ? "flag--tierA" : "flag--new") + '">check ' + n + "/3</span>";
      }
      h += '<li><a href="#/m/' + c + '"><b>' + esc(c) + "</b> · " + esc(mm ? mm.short : c) + "</a>" +
        badge + (g && g.before && g.before.length
          ? '<span class="small"> — after ' + g.before.join(", ") + "</span>" : "") +
        "</li>";
    });
    h += "</ol>";

    h += '<h2>The plan</h2>';
    h += '<div class="card">' +
      "<p>" + planDone + " of " + DATA.plan.length + " days marked complete.</p>" +
      '<div class="bar bar--purple"><i style="width:' + pct(planDone, DATA.plan.length) + '%"></i></div>' +
      '<p style="margin-top:14px"><a class="btn btn--primary" href="#/plan">Open the plan</a></p>' +
      "</div>";

    /* ---- the papers, as printable PDFs ---- */
    if (DATA.papers.length) {
      var pq = DATA.papers.reduce(function (a, p) { return a + (p.n || 0); }, 0);
      h += "<h2>Papers to print</h2>";
      h += '<div class="card">' +
        "<p>" + DATA.papers.length + " papers as real PDFs \u2014 the two sheets BPhO has published and " +
        "every section of the drill bank, " + pq + " questions in all. Each comes with a matching " +
        "markscheme PDF, so you can sit a paper on paper under the real clock and mark it properly " +
        "afterwards.</p>" +
        '<p style="margin-top:14px"><a class="btn btn--primary" href="#/papers">Papers &amp; downloads</a></p>' +
        "</div>";
    }

    /* ---- the teaching layer ---- */
    if (CON.length) {
      h += "<h2>Learn the key points</h2>";
      h += '<div class="card">' +
        "<p>Every question in the 2025 paper names the key points it turns on, and each of those is a " +
        "short lesson written as if you have met none of it before \u2014 what the quantity is, where the " +
        "formula comes from, what each symbol and unit means, and the trap the paper is setting. " +
        CON.length + " points in all, ordered so nothing depends on something you have not read.</p>" +
        '<div class="bar"><i style="width:' + pct(conDone(), CON.length) + '%"></i></div>' +
        '<p class="small" style="margin-top:8px">' + conDone() + " of " + CON.length + " read.</p>" +
        '<p style="margin-top:14px"><a class="btn btn--primary" href="#/learn">Start at the beginning</a></p>' +
        "</div>";
      var hot = CON.slice().sort(function (a, b) {
        return (b.q || []).length - (a.q || []).length;
      }).filter(function (x) { return (x.q || []).length > 1; }).slice(0, 8);
      if (hot.length) {
        h += '<p class="sub">The points the paper leans on hardest — these are each used by more ' +
          "than one question:</p>";
        h += '<div class="mcq__rel">' + keyChips(hot.map(function (x) { return x.id; })) + "</div>";
      }
    }

    /* ---- what the paper actually asked: the only hard evidence there is ---- */
    if (PRI && PRI.total) {
      h += '<h2>What the 2025 paper actually tested</h2>';
      h += '<p class="sub">There is exactly one Round 0 past paper in existence. These are the ' +
        PRI.total + " marks it spent, module by module — so this table, not anyone's opinion, is " +
        "what sets the priorities below. <b>Marks</b> counts questions whose main topic is that " +
        "module; <b>used in</b> also counts questions that lean on it.</p>";
      h += '<div class="card" style="padding:6px 4px 2px"><table class="yield"><thead><tr>' +
        "<th></th><th>Module</th><th>Marks</th><th>Used in</th><th>Share</th><th></th></tr></thead><tbody>";
      PRI.modules.forEach(function (m) {
        if (!m.n && !m.rel) return;                       /* hide modules the paper never touched */
        var w = Math.round((m.n / PRI.total) * 100);
        h += '<tr class="' + (m.n >= 3 ? "yield--hot" : m.n ? "yield--mid" : "yield--cold") + '">' +
          "<td><b>" + m.rank + "</b></td>" +
          '<td><a href="#/m/' + esc(m.code) + '"><b>' + esc(m.code) + "</b> · " + esc(m.short) + "</a></td>" +
          "<td><b>" + m.n + "</b></td>" +
          "<td>" + (m.rel || "—") + "</td>" +
          '<td style="min-width:120px"><div class="bar" style="margin:0"><i style="width:' + w + '%"></i></div>' +
          '<span class="small">' + m.share + "%</span></td>" +
          "<td>" + (m.n ? '<a class="btn btn--xs" href="#/practice/' + esc(m.code) + '">Drill</a>' : "") + "</td>" +
          "</tr>";
      });
      h += "</tbody></table></div>";
      h += '<div class="callout callout--key"><p><b>Read the top two rows again.</b> Mechanics ' +
        "(forces, energy, statics) and circuits took " +
        ((pcount("C") + pcount("H")) ) + " of the " + PRI.total + " marks between them — " +
        Math.round(((pcount("C") + pcount("H")) / PRI.total) * 100) + "%. The toolkit (module A) is " +
        "not a topic you revise separately; it is what the other " + (PRI.total - pcount("A")) +
        " questions are made of.</p></div>";
    }

    h += '<h2>Modules</h2>';
    h += '<p class="sub">Most-tested first, using the table above. Tick items off as you go.</p>';
    DATA.curriculum.slice().sort(yieldSort).forEach(function (m) {
      var d = modDone(m.code), t = modChecks(m.code).length, n = pcount(m.code);
      h += '<div class="card" style="padding:14px 18px">' +
        '<div style="display:flex;gap:12px;align-items:baseline;flex-wrap:wrap">' +
        '<span class="navlink__code" style="flex:0 0 auto">' + esc(m.code) + "</span>" +
        '<a href="#/m/' + m.code + '" style="font-weight:600;font-size:15.5px">' + esc(m.title) + "</a>" +
        (PRI ? '<span class="flag ' + (n >= 3 ? "flag--r1" : n ? "flag--new" : "flag--tierA") + '">' +
          n + " / " + PRI.total + " marks</span>" : "") +
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

  /* ---------------- study guidance (prereq · order · self-test) ---------------- */

  function gd(code) { return DATA.guidance[code] || null; }

  /** Modules that declare `code` as a prerequisite — derived, never stored. */
  function gdAfter(code) {
    return DATA.curriculum
      .filter(function (m) {
        var g = gd(m.code);
        return g && (g.before || []).indexOf(code) >= 0;
      })
      .map(function (m) { return m.code; });
  }

  /** A recommended reading order: respect the declared prerequisites first,
      then the curriculum's own priority. Simple stable topo sort. */
  function gdOrder() {
    var codes = DATA.curriculum.map(function (m) { return m.code; });
    var placed = [], seen = {};
    var guard = 0;
    while (placed.length < codes.length && guard++ < 200) {
      var progressed = false;
      for (var i = 0; i < codes.length; i++) {
        var c = codes[i];
        if (seen[c]) continue;
        var g = gd(c);
        var pre = (g && g.before) || [];
        var ready = pre.every(function (p) { return seen[p] || codes.indexOf(p) < 0; });
        if (!ready) continue;
        placed.push(c); seen[c] = true; progressed = true;
      }
      if (!progressed) {
        // cycle or unknown prerequisite: fall back to curriculum priority
        for (var k = 0; k < codes.length; k++) if (!seen[codes[k]]) { placed.push(codes[k]); seen[codes[k]] = true; }
      }
    }
    return placed;
  }

  function prereqChips(codes, emptyText) {
    if (!codes.length) return '<span class="small">' + (emptyText || "none") + "</span>";
    return codes.map(function (c) {
      var m = mod(c);
      return '<a class="gchip" href="#/m/' + c + '">' + esc(c) + " · " + esc(m ? m.short : c) + "</a>";
    }).join("");
  }

  function selfTestBlock(code) {
    var g = gd(code);
    if (!g || !g.starter || !g.starter.length) return "";
    var st = state.selftest[code] || {};
    var picks = st.picks || {};
    var shown = !!st.done;

    var h = '<section class="guide" id="selftest"><h2>Are you ready? — 3-question check</h2>';
    h += '<p class="sub">Answer all three, then check. These are gates, not a score: if you miss one, ' +
      "read the module rather than guessing again.</p>";

    g.starter.forEach(function (s, i) {
      var pick = picks[i];
      h += '<div class="stq"><p class="stq__q"><b>' + (i + 1) + ".</b> " + s.q + "</p>";
      h += '<div class="stq__opts">';
      s.opts.forEach(function (o, k) {
        var cls = "stopt";
        if (shown) {
          if (k === s.ans) cls += " is-right";
          else if (k === pick) cls += " is-wrong";
        } else if (k === pick) cls += " is-picked";
        h += '<button type="button" class="' + cls + '" data-st="' + esc(code) + '" data-i="' + i +
          '" data-k="' + k + '"><span class="stopt__k">' + "ABC"[k] + '</span><span>' + o + "</span></button>";
      });
      h += "</div>";
      if (shown) {
        var ok = pick === s.ans;
        h += '<p class="stq__why ' + (ok ? "ok" : "no") + '">' +
          (ok ? "<b>Correct.</b> " : (pick === undefined || pick === null ? "<b>Not answered.</b> " : "<b>Not quite.</b> ")) +
          esc(s.why) + "</p>";
      }
      h += "</div>";
    });

    if (shown) {
      var score = g.starter.filter(function (s, i) { return picks[i] === s.ans; }).length;
      h += '<div class="callout ' + (score === g.starter.length ? "callout--good" : "callout--warn") + '"><p>' +
        (score === g.starter.length
          ? "<b>" + score + " / 3 — go on.</b> You have what this module assumes. Work through the sections, then the examples."
          : "<b>" + score + " / 3.</b> Read the prerequisite material first — the links above take you straight to it — then come back and try again.") +
        "</p></div>";
      h += '<p><button class="btn btn--sm" data-act="strestart" data-code="' + esc(code) + '">Reset this check</button></p>';
    } else {
      var all = g.starter.every(function (s, i) { return picks[i] !== undefined && picks[i] !== null; });
      h += '<p><button class="btn btn--primary" data-act="stcheck" data-code="' + esc(code) + '"' +
        (all ? "" : " disabled") + ">Check my answers</button>" +
        '<span class="small" style="margin-left:10px">' +
        (all ? "ready to check" : "answer all three first") + "</span></p>";
    }
    h += "</section>";
    return h;
  }

  function guidanceBlock(code) {
    var g = gd(code);
    if (!g) return "";
    var after = gdAfter(code);

    var h = '<section class="guide">';
    h += "<h2>Before you start</h2>";
    h += '<div class="guide__prereq">' + g.prereq + "</div>";

    h += '<div class="guide__row"><div class="guide__col">' +
      '<h4>Learn this first</h4><div class="guide__chips">' +
        prereqChips(g.before || [], "nothing — start here") + "</div></div>";
    h += '<div class="guide__col"><h4>This unlocks</h4><div class="guide__chips">' +
      prereqChips(after, "no other module depends on this") + "</div></div></div>";
    h += "</section>";

    h += selfTestBlock(code);
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

    /* ---- how much of the one real paper this module is worth ---- */
    var pm = pmod(code);
    if (PRI && pm) {
      var ids = (PRI.drawsOn[code] || []);
      if (pm.n) {
        h += '<div class="callout callout--key"><p><b>' + pm.n + " of the " + PRI.total +
          " marks on the 2025 paper (" + pm.share + "%)</b> sat on this module — ranked " +
          pm.rank + " of " + PRI.modules.length + ". " +
          '<a href="#/practice/' + esc(code) + '">Drill it here.</a></p></div>';
      } else {
        h += '<div class="callout callout--warn"><p><b>No mark on the 2025 paper sat here directly.</b> ' +
          (ids.length
            ? "It was still used inside " + ids.length + " question" + (ids.length === 1 ? "" : "s") +
              ", so it is worth knowing but it is not where the marks are."
            : "Treat it as insurance: revise it only once the modules above the line are solid.") +
          "</p></div>";
      }
      if (ids.length) {
        h += '<p class="sub">Used in: ' + ids.map(function (id) {
          return '<a href="#/practice/' + esc(code) + '">' + esc(qLabel(id)) + "</a>";
        }).join(" · ") + "</p>";
      }
    }

    h += guidanceBlock(code);

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

    /* ---- the actual 2025 questions that sat on this module, with the topics they drew on ---- */
    var pq = (PRI && PRI.byModule[code]) || [];
    if (pq.length) {
      h += "<h2>What the 2025 paper asked from this module</h2>";
      h += '<p class="sub">' + pq.length + " of the " + PRI.total + " questions — answer " +
        (pq.length === 1 ? "it" : "these") + " and you have banked every mark this module is worth.</p>";
      h += '<ul class="tight">';
      pq.forEach(function (id) {
        var q = byQid(id);
        if (!q) return;
        var rels = (q.rel || []).filter(function (r) { return r[0] === code; })
          .map(function (r) { return esc(r[1]); });
        h += "<li><b>" + esc(qLabel(id)) + "</b> — " + esc(q.topic) +
          (rels.length ? ' <span class="small">· ' + rels.join(", ") + "</span>" : "") + "</li>";
      });
      h += "</ul>";
    }

    var qs = DATA.questions.filter(function (q) { return q.module === code; });
    if (qs.length) {
      /* the lessons behind this module's questions, so a weak module is one click from the theory */
      var cpts = CON.filter(function (x) {
        return x.m === code || (x.q || []).some(function (qid) {
          return qs.some(function (q) { return q.id === qid; });
        });
      });
      if (cpts.length) {
        h += "<h2>Key points in this module</h2>";
        h += '<p class="sub">' + cpts.length + " lessons, each written from first principles. " +
          "The ones the 2025 paper actually leaned on are listed with their questions.</p>";
        h += '<div class="mcq__rel">' + keyChips(cpts.map(function (x) { return x.id; })) + "</div>";
      }

      h += "<h2>Practice — " + qs.length + " questions</h2>";
      h += '<p class="sub">Round 0 format: five options, no calculator, one mark each.</p>';
      h += '<p><a class="btn" href="#/practice/' + code + '">Practise this module only</a></p>';
    }

    return h;
  }

  var practiceFilter = "all";
  var practiceDiff = "all";
  var practicePaper = "all";

  function viewPractice(code) {
    var list = DATA.questions.slice();
    if (code) list = list.filter(function (q) { return q.module === code; });
    if (practicePaper === "paper") list = list.filter(function (q) { return q.paper === "R0-2025"; });
    if (practicePaper === "sample") list = list.filter(function (q) { return q.paper === "R0-SAMPLE"; });
    if (practicePaper.indexOf("BANK-") === 0) list = list.filter(function (q) { return q.paper === practicePaper; });
    if (practiceDiff !== "all") list = list.filter(function (q) { return String(q.diff) === practiceDiff; });
    /* no module filter and no paper filter → surface the most-tested modules first */
    if (!code && practicePaper === "all") {
      list.sort(function (a, b) { return (pcount(b.module) - pcount(a.module)) || (prank(a.module) - prank(b.module)); });
    }

    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>Practice</h1>";
    h += '<p class="lede">Competition-style multiple choice. Attempt each one properly — work it out on paper, then reveal the solution.</p>';

    h += '<div class="toolbar">' +
      '<button class="btn btn--primary" data-act="mock">Timed mock — 25 in 60 min</button>' +
      '<button class="btn" data-act="mockuntimed">Untimed mock</button>' +
      '<span class="small">60 minutes, no calculator — same conditions as the paper.</span></div>';

    /* Past-paper mock: the 25-question 2025 Round 0 paper, in paper order. Use this as the final
       practice attempt — same format, same clock, same scoring. */
    h += '<div class="toolbar">' +
      '<button class="btn btn--paper" data-act="mockpaper">📝 2025 past paper — timed</button>' +
      '<button class="btn" data-act="mockpaperu">2025 past paper — untimed</button>' +
      '<span class="small">The actual 2025 paper. Final practice mock.</span></div>';

    /* The sample sheet, as its own short mock. 12 questions at the paper's own pace is
       about 29 minutes, so the clock is scaled from the question count -- see
       paperSeconds(). */
    h += '<div class="toolbar">' +
      '<button class="btn btn--paper" data-act="mocksample">🔎 2025 sample sheet — timed</button>' +
      '<button class="btn" data-act="mocksampleu">2025 sample sheet — untimed</button>' +
      '<span class="small">The 12 published sample questions, in order. Shorter clock.</span></div>';

    /* The original drill bank: 40 sections of 25, each one built to the real paper's own
       module mix, so any section works as a full-length mock.  Read from the data, so
       publishing another section adds its own launcher with no change here. */
    bankTags().forEach(function (tag) {
      var n = DATA.questions.filter(function (q) { return q.paper === tag; }).length;
      h += '<div class="toolbar">' +
        '<button class="btn btn--paper" data-act="mockbank" data-code="' + esc(tag) + '">🏋 ' +
          esc(paperLabel(tag)) + ' — timed</button>' +
        '<button class="btn" data-act="mockbanku" data-code="' + esc(tag) + '">' +
          esc(paperLabel(tag)) + ' — untimed</button>' +
        '<span class="small">' + n + ' original questions, same module mix as the 2025 ' +
          'paper. Written to be at least as hard, and every answer hand-checked.</span></div>';
    });

    /* The same papers, as files.  Some of the practice above is better done on paper --
       printing a sheet removes the reveal button and the temptation to peek. */
    if (DATA.papers.length) {
      h += '<div class="toolbar">' +
        '<a class="btn" href="#/papers">⤓ Download any paper as a PDF</a>' +
        '<span class="small">Every paper here, plus its markscheme, printable and offline.</span></div>';
    }

    /* Modules that carry the most marks on the one real paper come first, with the count shown,
       so it is obvious where to spend the time. */
    h += '<div class="chiprow">' +
      chip("all", "All modules", practiceFilter === "all", "pf") +
      DATA.curriculum.filter(function (m) {
        return DATA.questions.some(function (q) { return q.module === m.code; });
      }).sort(yieldSort).map(function (m) {
        var n = pcount(m.code);
        return chip(m.code, m.code + " · " + m.short +
          (PRI ? " (" + n + (n === 1 ? " mark)" : " marks)") : ""), practiceFilter === m.code, "pf");
      }).join("") + "</div>";

    /* One chip per named paper, with the count read from the bank rather than from
       PRI: the sample sheet carries no marks on the real paper, so PRI knows nothing
       about it and a PRI.total chip labelled only the past paper. */
    var paperCount = DATA.questions.filter(function (q) { return q.paper === "R0-2025"; }).length;
    var sampleCount = DATA.questions.filter(function (q) { return q.paper === "R0-SAMPLE"; }).length;
    var banks = bankTags();
    if (paperCount || sampleCount || banks.length) {
      h += '<div class="chiprow">' +
        chip("all", "Whole bank", practicePaper === "all", "pp") +
        (paperCount ? chip("paper", "2025 paper only — " + paperCount + " questions",
          practicePaper === "paper", "pp") : "") +
        (sampleCount ? chip("sample", "2025 sample sheet — " + sampleCount + " questions",
          practicePaper === "sample", "pp") : "") +
        banks.map(function (tag) {
          var n = DATA.questions.filter(function (q) { return q.paper === tag; }).length;
          return chip(tag, paperLabel(tag) + " — " + n + " questions",
            practicePaper === tag, "pp");
        }).join("") +
        "</div>";
    }

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

  /* ---------------- the papers area ----------------
     A place for the *papers* rather than for the questions: the two sheets BPhO has
     published, and each section of the original drill bank, every one of them as a real
     PDF of questions plus a matching markscheme PDF.  This is a different job from
     Practice -- there you answer one question at a time and the app marks you; here you
     take away a sheet you can print, sit against a clock, and mark on paper.

     Every link is read from data/papers.js, which the PDF builder writes from the files
     it actually produced.  Nothing here is hardcoded, so a section that has no PDF yet
     simply does not appear -- a hand-written link would be a dead download the first time
     someone added a section and forgot to rebuild. */
  function viewPapers() {
    var P = DATA.papers;

    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>Papers &amp; downloads</h1>";
    h += '<p class="lede">Every paper on this site as a real PDF. Each one comes with a ' +
      "matching markscheme: a quick answer key, a full worked solution for every question, " +
      "and the trap the question was built around.</p>";

    if (!P.length) {
      h += '<div class="callout callout--warn"><p><b>The PDFs have not been built yet.</b> ' +
        "From the <code>bpho/</code> folder run <code>node tools/papers/build_pdfs.js</code> " +
        "and reload this page. The questions themselves are unaffected and are still " +
        'available under <a href="#/practice">Practice</a>.</p></div>';
      return h;
    }

    var nQ = 0, nPages = 0, nBytes = 0, nFig = 0;
    P.forEach(function (p) {
      nQ += p.n || 0;
      nPages += (p.qPages || 0) + (p.mPages || 0);
      nBytes += (p.qBytes || 0) + (p.mBytes || 0);
      nFig += p.figures || 0;
    });

    h += '<div class="grid2">' +
      '<div class="stat"><b>' + P.length + "</b><span>papers, each with its own markscheme</span></div>" +
      '<div class="stat"><b>' + nQ + "</b><span>questions in total</span></div>" +
      '<div class="stat"><b>' + nFig + "</b><span>figures drawn for them</span></div>" +
      '<div class="stat"><b>' + nPages + "</b><span>pages of PDF, " + fmtBytes(nBytes) + " to download</span></div>" +
      "</div>";

    h += '<div class="callout callout--key"><p><b>How to use these.</b> Print the question ' +
      "paper (or open it on a second screen), sit it in one go against the clock with no " +
      "calculator, and only then open the markscheme and mark yourself. Two marks per " +
      "question is roughly the standard to hold yourself to; the 2025 UK qualifying line was " +
      "11 out of 25.</p></div>";

    /* The badge is the honest part of the card.  An original question mistaken for a real
       one mis-calibrates revision, so the two kinds are never mixed in one list. */
    var official = P.filter(function (p) { return p.kind === "official"; });
    var own = P.filter(function (p) { return p.kind !== "official"; });

    function group(title, blurb, list) {
      if (!list.length) return "";
      var g = '<h2>' + esc(title) + '</h2><p class="sub">' + blurb + "</p>";
      list.forEach(function (p) { g += paperCard(p); });
      return g;
    }

    h += group("Official BPhO material",
      "Reproduced from what BPhO has published, for personal study. These are the only " +
      "questions on this site that come from BPhO itself.", official);
    h += group("Original drill bank",
      "Written for this course in the Round 0 format and held to its rules — 25 questions, " +
      "60 minutes, no calculator, one answer in five. Not BPhO material.", own);

    h += '<div class="callout"><p class="small">Built ' + esc(DATA.papersBuilt) +
      ". The 250 curriculum questions live under <a href=\"#/practice\">Practice</a> instead: " +
      "they are organised by topic rather than laid out as a paper, so they are not offered " +
      "as a download.</p></div>";

    h += '<footer class="foot">A paper is rebuilt from the same data the site loads, in the ' +
      "same order, so a PDF can never disagree with the page it was downloaded from.</footer>";
    return h;
  }

  /* One paper, as a card: what it is, what is in it, and the two downloads. */
  function paperCard(p) {
    var mins = Math.round((p.seconds || 0) / 60);
    var isOfficial = p.kind === "official";
    var h = '<div class="card paper">';

    h += '<div class="paper__top"><h3 class="paper__t">' + esc(p.label) + "</h3>" +
      '<span class="flag ' + (isOfficial ? "flag--tierA" : "flag--new") + '">' +
      (isOfficial ? "Official BPhO material" : "Original · written for this course") +
      "</span></div>";

    h += '<p class="paper__note">' + esc(p.note) + "</p>";

    h += '<ul class="paper__meta">' +
      "<li><b>" + p.n + "</b> questions</li>" +
      "<li><b>" + mins + "</b> minutes</li>" +
      (p.figures ? "<li><b>" + p.figures + "</b> figure" + (p.figures === 1 ? "" : "s") + "</li>" : "") +
      "<li><b>" + ((p.qPages || 0) + (p.mPages || 0)) + "</b> PDF pages</li>" +
      "<li>" + (p.modules || "").split(" ").length + " modules — <code>" + esc(p.modules) + "</code></li>" +
      "</ul>";

    h += '<div class="toolbar">' +
      '<a class="btn btn--primary" href="' + esc(p.questions) + '" download>' +
        "⤓ Question paper <span class=\"paper__sz\">PDF · " + fmtBytes(p.qBytes) + "</span></a>" +
      '<a class="btn btn--paper" href="' + esc(p.markscheme) + '" download>' +
        "⤓ Markscheme <span class=\"paper__sz\">PDF · " + fmtBytes(p.mBytes) + "</span></a>" +
      '<a class="btn btn--ghost btn--sm" href="' + esc(p.questions) + '" target="_blank" rel="noopener">' +
        "Open the questions</a>" +
      "</div>";

    h += "</div>";
    return h;
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

    var timed = !!m.seconds;
    var left = mockSecondsLeft();
    var answered = m.ids.filter(function (id) { return m.picks[id]; }).length;

    var h = '<a class="toplink" href="#/practice">← Practice</a>';
    h += "<h1>Mock paper" + (timed ? " — timed" : " — untimed") + "</h1>";

    if (timed) {
      h += '<div class="mockclock' + (left <= 300 ? " is-low" : "") + '">' +
        '<div class="mockclock__row"><span class="mockclock__t" id="mocktimer">' + fmtClock(left) +
        "</span><span class=\"small\">remaining · " + fmtMinutes(m.seconds) + " for " + m.ids.length + " questions</span></div>" +
        '<div class="bar"><i id="mocktimebar" style="width:' + (100 * left / m.seconds) + '%"></i></div>' +
        '<p class="sub" style="margin:8px 0 0">The paper marks itself when the clock reaches zero. ' +
        "There is no negative marking, so fill in every question before then.</p></div>";
    } else {
      h += '<div class="callout callout--key"><p><b>' + m.ids.length +
        " questions, no clock.</b> Use this to learn the material; switch to a timed mock once " +
        "accuracy is holding up.</p></div>";
    }

    h += '<div class="toolbar"><button class="btn btn--primary" data-act="marksubmit">Mark my paper</button>' +
      '<span class="small">' + answered + " of " + m.ids.length + " answered</span>" +
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

  /* Reduce a finished mock into per-topic and per-module accuracy, and the
     ordered list of things to fix. Pure function so it is easy to reason about. */
  function analyseMock(m) {
    var items = [], score = 0, blank = 0, perTopic = {}, perModule = {};
    m.ids.forEach(function (id, i) {
      var q = byQid(id);
      if (!q) return;
      var pick = m.picks[id] || null;
      var ok = pick === "ABCDE"[q.ans];
      if (ok) score++; else if (!pick) blank++;
      var it = { n: i + 1, q: q, pick: pick, ok: ok };
      items.push(it);

      var t = perTopic[q.topic] || (perTopic[q.topic] = { topic: q.topic, module: q.module, n: 0, ok: 0, missed: [] });
      t.n++; if (ok) t.ok++; else t.missed.push(q.id);

      var mm = perModule[q.module] || (perModule[q.module] = { code: q.module, n: 0, ok: 0, missed: [] });
      mm.n++; if (ok) mm.ok++; else mm.missed.push(q.id);
    });

    function arr(o) {
      return Object.keys(o).map(function (k) { return o[k]; })
        .sort(function (a, b) {
          // worst accuracy first, then the topic with the most questions
          var pa = a.ok / a.n, pb = b.ok / b.n;
          if (pa !== pb) return pa - pb;
          return b.n - a.n;
        });
    }
    return {
      items: items, score: score, blank: blank, total: m.ids.length,
      topics: arr(perTopic), modules: arr(perModule),
      wrong: items.filter(function (x) { return !x.ok; })
    };
  }

  function viewMockResult() {
    var m = state.mock;
    if (!m || !m.marked) return "<h1>No result</h1><p><a href=\"#/practice\">Back to practice</a></p>";
    var a = analyseMock(m);
    var LINE = 11;                      /* 11/25, the UK-region qualifying line */
    /* The 11/25 line is a claim about a 25-question paper, and only about one. BPhO sets
       no pass mark on the 12-question sample sheet, so judging that against "11 out of
       25" is a false comparison: 11 is unreachable there and 0 is not a fail. Decide by
       the LENGTH of what was actually sat, not by the paper's tag -- a drill-bank section
       is 25 questions and IS judged against 11/25, while a shorter sheet is judged
       against the 44% that line implies. The tag-based test this replaced scored a
       full-length bank section as if it were the 12-question sample. */
    var PASS_FRAC = LINE / 25;
    var isFullPaper = a.total === 25;
    var passed = isFullPaper ? (a.score >= LINE)
                             : (a.total > 0 && a.score / a.total >= PASS_FRAC);

    var h = '<a class="toplink" href="#/practice">← Practice</a>';
    h += "<h1>Mock result</h1>";

    h += '<div class="grid2">' +
      '<div class="stat"><b>' + a.score + " / " + a.total + "</b><span>correct</span></div>" +
      '<div class="stat"><b>' + (isFullPaper ? (passed ? "Above" : "Below") : Math.round(100 * a.score / a.total) + "%") +
        "</b><span>" + (isFullPaper ? "the " + LINE + "/25 qualifying line" : "the 44% that 11/25 implies") + "</span></div>" +
      '<div class="stat"><b>' + a.blank + "</b><span>left blank — never do this</span></div>" +
      '<div class="stat"><b>' + (m.mode === "timed" ? fmtClock(m.elapsed || 0) : "—") + "</b><span>" +
      (m.mode === "timed" ? (m.autoSubmitted ? "ran out of time" : "time taken of " + fmtClock(m.seconds)) : "untimed") + "</span></div>" +
      "</div>";

    h += '<div class="callout ' + (passed ? "callout--good" : "callout--warn") + '"><p>' +
      (passed
        ? (isFullPaper
          ? "<b>You are on track.</b> Keep the accuracy and work on speed — the next step is a timed mock under real conditions."
          : "<b>You are on track.</b> That is the accuracy the 11/25 line implies. " + a.total + " questions is a style check, not a mock — the real paper is 25 in 60 minutes.")
        : (isFullPaper
          ? "<b>Below the line.</b> The repair plan below is ordered by where the marks actually are, not by module number."
          : "<b>Below the accuracy the 11/25 line implies.</b> The repair plan below is ordered by where the marks actually are, not by module number.")) +
      "</p></div>";

    /* ---- review by topic ------------------------------------------------ */
    h += '<h2>Review by topic</h2>';
    h += '<p class="sub">Every topic you met, worst first. Anything below 100% is where the next hour goes.</p>';
    h += "<table><thead><tr><th>Topic</th><th>Module</th><th>Score</th><th>Accuracy</th><th></th></tr></thead><tbody>";
    a.topics.forEach(function (t) {
      var p = pct(t.ok, t.n);
      h += "<tr" + (p < 100 ? ' class="row-weak"' : "") + "><td>" + esc(t.topic) + "</td>" +
        '<td><a href="#/m/' + esc(t.module) + '">' + esc(t.module) + "</a></td>" +
        "<td>" + t.ok + " / " + t.n + "</td>" +
        '<td><span class="minibar"><i style="width:' + p + '%"></i></span> ' + p + "%</td>" +
        '<td>' + (p < 100 ? '<a class="btn btn--sm" href="#/practice/' + esc(t.module) + '">Practise</a>' : "") + "</td></tr>";
    });
    h += "</tbody></table>";

    /* ---- weak-topic recommendations ------------------------------------- */
    var weakModules = a.modules.filter(function (x) { return x.ok < x.n; });
    if (weakModules.length) {
      h += '<h2>Weak topics — what to do about them</h2>';
      h += '<div class="card">';
      h += '<p class="sub" style="margin-top:0">Ranked by how many marks are available, not by how ' +
        "bad the score looks. Two marks lost in one module beats one mark lost in two.</p><ul class=\"tight\">";
      weakModules.forEach(function (x) {
        var mm = mod(x.code);
        var g = gd(x.code);
        var st = state.selftest[x.code];
        var avail = DATA.questions.filter(function (q) { return q.module === x.code; }).length;
        h += '<li><b>' + esc(x.code) + " · " + esc(mm ? mm.short : x.code) + "</b> — " +
          x.ok + "/" + x.n + " on this paper, " + avail + " questions in the bank.";
        var bits = [];
        bits.push('<a href="#/m/' + esc(x.code) + '">Re-read the module</a>');
        if (g && g.starter) {
          bits.push(st && st.done ? '<span class="small">readiness check already taken</span>'
            : '<a href="#/m/' + esc(x.code) + '">Take the readiness check</a>');
        }
        bits.push('<a href="#/practice/' + esc(x.code) + '">Practise this module</a>');
        h += '<div class="small">' + bits.join(" · ") + "</div></li>";
      });
      h += "</ul></div>";
    } else {
      h += '<h2>Weak topics</h2><div class="callout callout--good"><p><b>None on this paper.</b> ' +
        "Every topic you met was clean. Take another mock — a different 25 questions will find the gaps.</p></div>";
    }

    /* ---- post-mock repair plan ------------------------------------------ */
    h += "<h2>Repair plan</h2>";
    h += '<ol class="steps">';
    if (a.blank > 0) {
      h += "<li><b>Stop leaving blanks.</b> There is no negative marking, so an unanswered question is " +
        "a mark thrown away. On this paper that was " + a.blank + " question" + (a.blank === 1 ? "" : "s") +
        " — guessing would have been worth about " + Math.round(a.blank / 5) + " mark" + (Math.round(a.blank / 5) === 1 ? "" : "s") +
        " on average. Fill in every answer before the clock stops.</li>";
    }
    var plan = weakModules.slice(0, 3);
    plan.forEach(function (x, idx) {
      var mm = mod(x.code);
      var missedTopics = {};
      x.missed.forEach(function (id) { var q = byQid(id); if (q) missedTopics[q.topic] = 1; });
      var names = Object.keys(missedTopics).join(", ");
      h += "<li><b>Session " + (idx + 1) + " — module " + esc(x.code) + " (" + esc(mm ? mm.short : x.code) + ").</b> " +
        "Read the module, take its three-question readiness check, then work the " + x.missed.length +
        " question" + (x.missed.length === 1 ? "" : "s") + " you missed" +
        (names ? " on " + esc(names) : "") + ". Finish on the module's own question set before moving on." +
        ' <a href="#/m/' + esc(x.code) + '">Open module ' + esc(x.code) + "</a></li>";
    });
    if (a.score >= LINE && m.mode !== "timed") {
      h += "<li><b>Now do it timed.</b> Your accuracy qualifies; pace is the open question. " +
        "Run a 60-minute mock and see whether the score survives the clock.</li>";
    }
    if (a.score >= LINE && m.mode === "timed" && !m.autoSubmitted) {
      h += "<li><b>Bank the time.</b> You finished with time to spare. Spend it checking the questions " +
        "you guessed — one re-check per paper is usually a mark.</li>";
    }
    if (m.autoSubmitted) {
      h += "<li><b>You ran out of time.</b> Practise at pace: take 25 questions and give yourself " +
        "50 minutes, then 45. Speed on this paper comes from recognising the method, not from working faster.</li>";
    }
    h += '<li><b>Then take another mock.</b> A fresh 25 questions will tell you whether the repair held.</li>';
    h += "</ol>";

    h += '<div class="toolbar">' +
      '<button class="btn btn--primary" data-act="mock">New timed mock</button>' +
      '<button class="btn" data-act="mockuntimed">New untimed mock</button>' +
      '<button class="btn" data-act="mockclear">Clear and practise freely</button></div>';

    h += "<h2>Question by question</h2>";
    h += "<table><thead><tr><th>#</th><th>Topic</th><th>You</th><th>Answer</th><th></th></tr></thead><tbody>" +
      a.items.map(function (x) {
        return "<tr" + (x.ok ? "" : ' class="row-weak"') + "><td>Q" + x.n + "</td><td>" + esc(x.q.topic) +
          "</td><td>" + (x.pick || "—") + "</td><td>" + "ABCDE"[x.q.ans] + "</td><td>" +
          (x.ok ? "✓" : "✗") + "</td></tr>";
      }).join("") + "</tbody></table>";

    h += "<h2>Review the ones you missed</h2>";
    if (!a.wrong.length) {
      h += '<p class="sub">Nothing missed. Take another mock.</p>';
    } else {
      a.wrong.forEach(function (x) { h += questionCard(x.q); });
    }
    return h;
  }

  /* ---------------- key points: the teaching layer ----------------
     Every past-paper question names the key points it uses (`key`), and every key point is a
     short lesson written from zero. The lessons are chained by `pre` (prerequisites), so the
     course can be read top to bottom without ever meeting a term before it is defined.
     `stage` groups them: 0 toolkit · 1 mechanics · 2 materials & thermal · 3 waves & optics ·
     4 electricity · 5 quantum & nuclear. */

  var CON = DATA.concepts;
  var CONBY = {};
  CON.forEach(function (x) { CONBY[x.id] = x; });
  var STAGES = [
    ["The toolkit", "Not physics topics — the techniques that decide whether you can even start a question. Read these first."],
    ["Mechanics", "Force, motion, momentum, energy, rotation."],
    ["Materials and thermal", "How real stuff stretches, and how heat is counted."],
    ["Waves and optics", "Superposition, standing waves, and what happens at a boundary."],
    ["Electricity", "Charge, resistance, and the circuits the paper keeps testing."],
    ["Quantum and nuclear", "Photons, energy levels, and what nuclei do."]
  ];
  /* reading order: stage first, then prerequisites before dependants within the stage */
  var CONORDER = (function () {
    var out = [];
    function visit(x, seen) {
      if (seen[x.id]) return;
      seen[x.id] = 1;
      x.pre.forEach(function (p) { if (CONBY[p]) visit(CONBY[p], seen); });
      out.push(x);
    }
    var bys = {};
    CON.forEach(function (x) { (bys[x.stage] = bys[x.stage] || []).push(x); });
    var seen = {};
    Object.keys(bys).sort().forEach(function (s) {
      bys[s].forEach(function (x) { visit(x, seen); });
    });
    return out;
  })();
  var CONPOS = {};
  CONORDER.forEach(function (x, i) { CONPOS[x.id] = i; });

  function conDone() { return Object.keys(state.read || {}).filter(function (k) { return state.read[k]; }).length; }

  function keyChips(ids, cls) {
    return (ids || []).filter(function (k) { return CONBY[k]; }).map(function (k) {
      var c = CONBY[k];
      return '<a class="' + (cls || "kchip") + '" href="#/c/' + esc(k) + '" title="' + esc(c.one) + '">' +
        '<b>' + esc(c.m) + "</b>" + esc(c.t) + "</a>";
    }).join("");
  }

  function viewLearn() {
    var h = '<a class="toplink" href="#/">← Overview</a>';
    h += "<h1>Key points, in order</h1>";
    h += '<p class="sub">Everything the 2025 paper used, taught from nothing. ' +
      CON.length + " points, " + conDone() + " read. Each one is self-contained: what the idea is, " +
      "where the formula comes from, what every symbol and unit means, and the trap the paper sets. " +
      "Work down the list — nothing here depends on something you have not read yet.</p>";
    h += '<div class="bar" style="margin-bottom:22px"><i style="width:' + pct(conDone(), CON.length) + '%"></i></div>';

    var stage = -1;
    CONORDER.forEach(function (c, i) {
      if (c.stage !== stage) {
        stage = c.stage;
        if (STAGES[stage]) {
          h += '<h2 style="margin-top:26px">' + (stage + 0 === stage ? "Stage " + stage : "") +
            (STAGES[stage] ? " · " + esc(STAGES[stage][0]) : "") + "</h2>";
          h += '<p class="sub">' + esc(STAGES[stage][1]) + "</p>";
        }
      }
      var read = state.read && state.read[c.id];
      h += '<div class="card lesson' + (read ? " lesson--read" : "") + '" id="c-' + esc(c.id) + '">';
      h += '<div class="lesson__head">' +
        '<span class="lesson__n">' + (i + 1) + "</span>" +
        '<a class="lesson__t" href="#/c/' + esc(c.id) + '">' + esc(c.t) + "</a>" +
        '<span class="flag flag--paper">' + esc(c.m) + "</span>" +
        '<button class="btn btn--xs" type="button" data-read="' + esc(c.id) + '">' +
        (read ? "✓ Read" : "Mark read") + "</button>" +
        "</div>";
      h += '<p class="lesson__one">' + esc(c.one) + "</p>";
      h += '<div class="lesson__foot">' +
        '<span class="small">Used in ' + (c.q || []).map(function (qid) {
          return '<a href="#/q/' + esc(qid) + '">' + esc(qLabel(qid)) + "</a>";
        }).join(" · ") + "</span>" +
        (c.pre.length ? '<span class="small"> · needs ' + c.pre.map(function (p) {
          return '<a href="#/c/' + esc(p) + '">' + esc(CONBY[p] ? CONBY[p].t : p) + "</a>";
        }).join(", ") + "</span>" : "") +
        "</div>";
      h += "</div>";
    });
    return h;
  }

  function viewConcept(id) {
    var c = CONBY[id];
    if (!c) return '<h1>No such key point</h1><p><a href="#/learn">Back to the course</a></p>';
    var i = CONPOS[id];
    var next = CONORDER[i + 1];
    var after = CON.filter(function (x) { return x.pre.indexOf(id) >= 0; });

    var h = '<a class="toplink" href="#/learn">← All key points</a>';
    h += '<div class="card lesson lesson--full">';
    h += '<div class="lesson__head">' +
      '<span class="lesson__n">' + (i + 1) + " / " + CON.length + "</span>" +
      '<a class="flag flag--paper" href="#/m/' + esc(c.m) + '">' + esc(c.m) + "</a>" +
      '<button class="btn btn--xs" type="button" data-read="' + esc(id) + '">' +
      ((state.read && state.read[id]) ? "✓ Read" : "Mark read") + "</button>" +
      "</div>";
    h += "<h1>" + esc(c.t) + "</h1>";
    h += '<p class="lead">' + esc(c.one) + "</p>";
    if (c.pre.length) {
      h += '<div class="mcq__rel"><span class="small">Read first:</span> ' + keyChips(c.pre) + "</div>";
    }
    h += '<div class="lesson__body">' + c.body + "</div>";
    if (c.used) {
      h += '<div class="callout callout--key"><b>Where the paper uses it.</b> ' + c.used + "</div>";
    }
    if ((c.q || []).length) {
      h += "<h2>Questions that use this</h2>";
      h += '<p class="sub">' + c.q.map(function (qid) {
        var q = DATA.questions.filter(function (x) { return x.id === qid; })[0];
        return '<a class="btn btn--xs" href="#/q/' + esc(qid) + '">' +
          esc(qLabel(qid)) + (q ? " · " + esc(q.topic) : "") + "</a>";
      }).join(" ") + "</p>";
    }
    if (after.length) {
      h += '<div class="mcq__rel"><span class="small">This unlocks:</span> ' +
        keyChips(after.map(function (x) { return x.id; })) + "</div>";
    }
    h += '<div class="lesson__nav">' +
      (next ? '<a class="btn btn--primary" href="#/c/' + esc(next.id) + '">Next: ' + esc(next.t) + " →</a>" :
        '<a class="btn btn--primary" href="#/practice">That is the whole course — go practise</a>') +
      "</div>";
    h += "</div>";
    return h;
  }

  function viewQuestion(id) {
    var q = DATA.questions.filter(function (x) { return x.id === id; })[0];
    if (!q) return '<h1>No such question</h1><p><a href="#/practice">Back to practice</a></p>';
    var h = '<a class="toplink" href="#/practice">← Practice</a>';
    h += "<h1>" + esc(q.topic) + "</h1>";
    h += '<p class="sub">' + esc(qLabelLong(q.id)) +
      " · " + esc(mod(q.module) ? mod(q.module).title : q.module) + "</p>";
    h += questionCard(q);
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
    else if (view === "papers") html = viewPapers();
    else if (view === "learn") html = viewLearn();
    else if (view === "c") html = viewConcept(parts[1]);
    else if (view === "q") html = viewQuestion(parts[1]);
    else if (view === "glossary") html = viewGlossary();
    else if (view === "reference") html = viewReference();
    else if (view === "mock") html = (state.mock && state.mock.marked) ? viewMockResult() : viewMock();
    else html = "<h1>Not found</h1><p><a href=\"#/\">Back to overview</a></p>";

    main.innerHTML = html;
    window.scrollTo(0, 0);
    bindAll(main);
    paintNav(view, parts[1]);

    // Only a live, timed mock gets a clock. Leaving the view must kill it.
    stopMockTimer();
    if (view === "mock" && state.mock && !state.mock.marked && state.mock.seconds) startMockTimer();
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

    root.querySelectorAll("[data-st]").forEach(function (b) {
      b.addEventListener("click", function () {
        var code = b.getAttribute("data-st");
        var i = b.getAttribute("data-i"), k = parseInt(b.getAttribute("data-k"), 10);
        var st = state.selftest[code] || { picks: {}, done: false };
        if (st.done) return;               // locked once checked — press Reset
        st.picks[i] = k;
        state.selftest[code] = st;
        save();
        render();
      });
    });

    root.querySelectorAll("[data-chip]").forEach(function (b) {
      b.addEventListener("click", function () {
        var g = b.getAttribute("data-chip"), v = b.getAttribute("data-val");
        if (g === "pf") { practiceFilter = v; location.hash = v === "all" ? "#/practice" : "#/practice/" + v; }
        if (g === "pd") { practiceDiff = v; render(); }
        if (g === "pp") { practicePaper = v; render(); }
      });
    });

    root.querySelectorAll("[data-read]").forEach(function (b) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-read");
        state.read = state.read || {};
        state.read[id] = !state.read[id];
        save();
        render();
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
      b.addEventListener("click", function () { act(b.getAttribute("data-act"), b); });
    });

    var imp = root.querySelector('[data-act="import"]');
    if (imp) imp.addEventListener("change", function () { if (imp.files[0]) importProgress(imp.files[0]); });
  }

  function act(a, el) {
    var code = el && el.getAttribute ? el.getAttribute("data-code") : null;
    if (a === "export") exportProgress();
    else if (a === "reset") reset();
    else if (a === "stcheck") {
      if (!code) return;
      var st = state.selftest[code] || { picks: {}, done: false };
      st.done = true;
      state.selftest[code] = st;
      save();
      render();
      var box = document.getElementById("selftest");
      if (box) box.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    else if (a === "strestart") { if (code) { delete state.selftest[code]; save(); render(); } }
    else if (a === "mock") startMock("timed");
    else if (a === "mockuntimed") startMock("untimed");
    else if (a === "mockpaper") startMockPaper("R0-2025", "timed");
    else if (a === "mockpaperu") startMockPaper("R0-2025", "untimed");
    else if (a === "mocksample") startMockPaper("R0-SAMPLE", "timed");
    else if (a === "mocksampleu") startMockPaper("R0-SAMPLE", "untimed");
    /* The drill bank launchers carry their own paper tag, so one handler serves every
       section and no new branch is needed when section 2 is published. */
    else if (a === "mockbank") startMockPaper(code, "timed");
    else if (a === "mockbanku") startMockPaper(code, "untimed");
    else if (a === "marksubmit") finishMock();
    else if (a === "mockquit") { if (confirm("Abandon this mock?")) { state.mock = null; save(); location.hash = "#/practice"; } }
    else if (a === "mockclear") { state.mock = null; save(); location.hash = "#/practice"; }
    else if (a === "setdate") {
      var v = document.getElementById("examdate");
      if (v && v.value) { state.examDate = v.value + "T09:00:00+07:00"; save(); alert("Saved."); render(); }
    }
  }

  function startMock(mode) {
    var pool = DATA.questions.slice();
    for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
    var ids = pool.slice(0, Math.min(25, pool.length)).map(function (q) { return q.id; });
    state.mock = {
      ids: ids, picks: {}, started: Date.now(),
      // Real Round 0: 25 questions in 60 minutes. Untimed keeps the paper but
      // drops the clock, for learning the material rather than the pace.
      mode: mode === "untimed" ? "untimed" : "timed",
      seconds: mode === "untimed" ? 0 : 60 * 60,
      marked: false, elapsed: 0, autoSubmitted: false
    };
    save();
    location.hash = "#/mock";
    render();
  }

  /* Fixed-paper mock: assemble the 25 questions in a single named paper (e.g. the 2025 Round 0
     paper) in their stored order, and launch them as a Round 0 mock. Used as the final practice
     attempt once the rest of the curriculum is in place. */
  function startMockPaper(tag, mode) {
    var ids = DATA.questions.filter(function (q) { return q.paper === tag; })
                            .map(function (q) { return q.id; });
    if (!ids.length) { alert("No questions tagged " + tag); return; }
    state.mock = {
      ids: ids, picks: {}, started: Date.now(),
      // The tag is stored so the result page can tell the real paper from the sample
      // sheet: 11/25 is a claim about the paper only, and is false for 12 questions.
      paper: tag,
      mode: mode === "untimed" ? "untimed" : "timed",
      seconds: mode === "untimed" ? 0 : paperSeconds(ids.length),
      marked: false, elapsed: 0, autoSubmitted: false
    };
    save();
    location.hash = "#/mock";
    render();
  }

  function finishMock(auto) {
    var m = state.mock;
    if (!m || m.marked) return;
    m.marked = true;
    m.autoSubmitted = !!auto;
    m.elapsed = Math.floor((Date.now() - m.started) / 1000);
    save();
    if (auto) alert("Time is up. Your paper has been marked automatically.");
    location.hash = "#/mock";
    render();
  }

  /* ---- live clock for a timed mock ------------------------------------- */
  var MOCK_TIMER = null;

  function stopMockTimer() {
    if (MOCK_TIMER) { clearInterval(MOCK_TIMER); MOCK_TIMER = null; }
  }

  function mockSecondsLeft() {
    var m = state.mock;
    if (!m || !m.seconds) return null;
    return Math.max(0, m.seconds - Math.floor((Date.now() - m.started) / 1000));
  }

  function fmtClock(s) {
    s = Math.max(0, Math.floor(s));
    return Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2);
  }

  function startMockTimer() {
    stopMockTimer();
    var m = state.mock;
    if (!m || m.marked || !m.seconds) return;
    MOCK_TIMER = setInterval(function () {
      var m2 = state.mock;
      if (!m2 || m2.marked) { stopMockTimer(); return; }
      var left = mockSecondsLeft();
      var el = document.getElementById("mocktimer");
      if (el) {
        el.textContent = fmtClock(left);
        el.classList.toggle("is-low", left <= 300);
        el.classList.toggle("is-out", left <= 60);
      }
      var bar = document.getElementById("mocktimebar");
      if (bar) bar.style.width = (100 * left / m2.seconds) + "%";
      if (left <= 0) { stopMockTimer(); finishMock(true); }
    }, 1000);
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
      '<a class="navlink" data-view="papers" href="#/papers"><span class="navlink__code">⤓</span><span class="navlink__t">Papers &amp; PDFs</span>' +
      (DATA.papers.length ? '<span class="navlink__n">' + DATA.papers.length + "</span>" : "") + "</a>" +
      '<a class="navlink" data-view="learn" href="#/learn"><span class="navlink__code">✦</span><span class="navlink__t">Key points</span>' +
      (CON.length ? '<span class="navlink__n">' + conDone() + "/" + CON.length + "</span>" : "") + "</a>" +
      "</div>";

    var groups = { 1: "Priority 1", 2: "Priority 2", 3: "Priority 3", 4: "Insurance" };
    [1, 2, 3, 4].forEach(function (p) {
      var ms = DATA.curriculum.filter(function (m) { return m.priority === p; });
      if (!ms.length) return;
      h += '<div class="side__group"><h4>' + groups[p] + "</h4>";
      /* within each priority band, put the modules the 2025 paper tested hardest first, and
         show how many of the 25 marks each one carried */
      ms.slice().sort(yieldSort).forEach(function (m) {
        var n = pcount(m.code);
        h += '<a class="navlink" data-view="m" data-code="' + m.code + '" href="#/m/' + m.code + '">' +
          '<span class="navlink__code">' + esc(m.code) + '</span>' +
          '<span class="navlink__t">' + esc(m.short || m.title) + '</span>' +
          (PRI ? '<span class="navlink__n' + (n ? " hot" : "") + '" title="' + n +
            ' of the 25 marks on the 2025 paper">' + n + "</span>" : "") +
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
