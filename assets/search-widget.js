/* Global search for the whole DP study site — one file, injected by ai-widget.js.
 *
 * Why it lives here and not in a per-page snippet: 429 pages load ai-widget.js by
 * absolute URL, so this one file reaches every space at once. Editing 429 HTML
 * files by hand is exactly what we must not do.
 *
 *   - the six study spaces, the seven subject pages and both vocab spaces;
 *   - all 320-odd Challenge Bank questions, with difficulty and marks;
 *   - every BPhO module, glossary term, worked example and practice question;
 *   - all 30 World's Wife poems (deep-linked with #poem=<id>);
 *   - every Python Mastery chapter (deep-linked with #/<slug>);
 * and one row that hands a query over to the Question Bank (see bankRow below for
 * why the palette does not query its API itself).
 *
 * The index (assets/js/search-index.js, ~765 KB raw / ~175 KB gzipped) is only
 * fetched the first time the palette is opened.
 */
(function () {
  "use strict";
  if (window.__dpSearchLoaded) return;
  window.__dpSearchLoaded = true;

  var HUB = "https://sbk283074-creator.github.io/dp-study-site/";
  var INDEX_URL = HUB + "assets/js/search-index.js?v=7";

  var IDX = null;
  var LOADING = false;
  var PENDING = [];
  var RESULTS = [];
  var CUR = -1;

  /* ------------------------------------------------------------------ styles */
  var CSS = [
    "#dp-search-root{position:fixed;left:18px;bottom:18px;z-index:2147483001;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}",
    "#dp-search-btn{display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:999px;",
    "border:1px solid rgba(15,23,42,.12);background:#fff;color:#0f172a;font-size:13px;font-weight:600;",
    "cursor:pointer;box-shadow:0 6px 22px rgba(15,23,42,.14);line-height:1}",
    "#dp-search-btn:hover{border-color:#2563eb;color:#2563eb}",
    "#dp-search-btn .k{font-size:11px;font-weight:700;color:#64748b;border:1px solid rgba(100,116,139,.35);",
    "border-radius:5px;padding:1px 5px}",
    "#dp-search-mask{position:fixed;inset:0;z-index:2147483010;background:rgba(15,23,42,.42);",
    "backdrop-filter:blur(2px);display:flex;align-items:flex-start;justify-content:center;padding:9vh 16px 16px}",
    "#dp-search-panel{width:min(680px,100%);max-height:74vh;display:flex;flex-direction:column;overflow:hidden;",
    "background:#fff;border-radius:14px;box-shadow:0 24px 70px rgba(15,23,42,.34);border:1px solid rgba(15,23,42,.08)}",
    "#dp-search-field{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid rgba(15,23,42,.09)}",
    "#dp-search-input{flex:1;border:0;outline:0;font-size:16px;color:#0f172a;background:transparent;font-family:inherit}",
    "#dp-search-input::placeholder{color:#94a3b8}",
    "#dp-search-count{font-size:11px;color:#64748b;white-space:nowrap}",
    "#dp-search-list{overflow-y:auto;padding:6px 0 10px;margin:0}",
    ".dp-search-group{padding:10px 16px 4px;font-size:10.5px;font-weight:800;letter-spacing:.09em;",
    "text-transform:uppercase;color:#94a3b8}",
    ".dp-search-item{display:block;padding:9px 16px;text-decoration:none;color:inherit;border-left:3px solid transparent}",
    ".dp-search-item.sel{background:#eff6ff;border-left-color:#2563eb}",
    ".dp-search-t{font-size:13.5px;font-weight:600;color:#0f172a;line-height:1.35}",
    ".dp-search-s{font-size:11.5px;color:#64748b;margin-top:2px;line-height:1.4;",
    "display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}",
    ".dp-search-b{display:inline-block;margin-left:6px;font-size:10px;font-weight:700;color:#475569;",
    "background:#f1f5f9;border-radius:4px;padding:1px 6px;vertical-align:1px}",
    // Dark text on the amber highlight in BOTH themes: `color:inherit` turned the
    // match into an unreadable yellow block in dark mode.
    ".dp-search-item mark{background:#fde68a;color:#0f172a;border-radius:2px;padding:0 1px}",
    "#dp-search-empty{padding:26px 18px;text-align:center;color:#64748b;font-size:13px;line-height:1.6}",
    "#dp-search-foot{padding:9px 16px;border-top:1px solid rgba(15,23,42,.09);font-size:11px;color:#94a3b8;",
    "display:flex;gap:14px;flex-wrap:wrap;align-items:center}",
    "#dp-search-foot span{white-space:nowrap}",
    "#dp-search-foot b{font-weight:700;color:#475569;background:#f1f5f9;border-radius:4px;padding:1px 5px}",
    "@media (max-width:640px){#dp-search-btn span.lbl{display:none}#dp-search-mask{padding:0;align-items:stretch}",
    "#dp-search-panel{width:100%;max-height:100%;border-radius:0;border:0}}",
    "@media print{#dp-search-root{display:none!important}}",
    "html[data-theme=dark] #dp-search-btn{background:#0f172a;color:#e2e8f0;border-color:rgba(226,232,240,.18)}",
    "html[data-theme=dark] #dp-search-panel{background:#0f172a;border-color:rgba(226,232,240,.14)}",
    "html[data-theme=dark] #dp-search-input{color:#e2e8f0}",
    "html[data-theme=dark] .dp-search-t{color:#e2e8f0}",
    "html[data-theme=dark] .dp-search-item.sel{background:#1e293b}",
    "html[data-theme=dark] #dp-search-field,html[data-theme=dark] #dp-search-foot{border-color:rgba(226,232,240,.12)}"
  ].join("");

  /* ------------------------------------------------- spaces shown before typing */
  var SPACES = [
    { t: "DP Learning — hub", d: "Six subjects, the DP core, the study plan.", u: "index.html" },
    { t: "Question Bank", d: "9,969 real IB questions — practise and review.", u: "qbank/" },
    { t: "Python Mastery", d: "A focused, self-contained Python course.", u: "PYTHON/" },
    { t: "The World's Wife Lab", d: "Duffy's collection, poem by poem.", u: "Eng%20learning/" },
    { t: "Challenge Bank", d: "Original hard problems with full markschemes.", u: "challenge-bank/site/" },
    { t: "IB English Vocab", d: "Daily IB English Lang & Lit vocabulary.", u: "ib-english-vocab/" },
    { t: "BPhO Round 0", d: "Physics Olympiad — topics, drills, timed mocks.", u: "bpho/" },
    { t: "Vocabulary Review", d: "1,452 curated words with Leitner repetition.", u: "vocab-review/" }
  ];

  /* -------------------------------------------------------------------- utils */
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function rxEsc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  function mark(text, terms) {
    var out = esc(text);
    for (var i = 0; i < terms.length; i++) {
      if (!terms[i]) continue;
      out = out.replace(new RegExp("(" + rxEsc(esc(terms[i])) + ")", "gi"), "<mark>$1</mark>");
    }
    return out;
  }

  function snippet(text, terms) {
    var lower = (text || "").toLowerCase();
    var at = -1;
    for (var i = 0; i < terms.length; i++) {
      var p = terms[i] ? lower.indexOf(terms[i]) : -1;
      if (p >= 0 && (at < 0 || p < at)) at = p;
    }
    if (at < 0) return (text || "").slice(0, 150);
    var from = Math.max(0, at - 60);
    return (from > 0 ? "…" : "") + text.slice(from, from + 190);
  }

  function loadIndex(cb) {
    if (IDX) { cb(); return; }
    if (window.DP_SEARCH_INDEX) { IDX = window.DP_SEARCH_INDEX; cb(); return; }
    PENDING.push(cb);
    if (LOADING) return;
    LOADING = true;
    var s = document.createElement("script");
    s.src = INDEX_URL;
    s.onload = function () {
      LOADING = false;
      IDX = window.DP_SEARCH_INDEX || [];
      var q = PENDING; PENDING = [];
      for (var i = 0; i < q.length; i++) q[i]();
    };
    s.onerror = function () {
      LOADING = false; IDX = [];
      var q = PENDING; PENDING = [];
      for (var i = 0; i < q.length; i++) q[i]();
    };
    document.head.appendChild(s);
  }

  /* ------------------------------------------------------------------- search */
  function scoreDoc(d, terms, phrase) {
    var title = (d.title || "").toLowerCase();
    var heads = (d.heads || []).join(" ").toLowerCase();
    var badge = (d.badge || "").toLowerCase();
    var text = (d.text || "").toLowerCase();
    var s = 0;
    if (phrase && title.indexOf(phrase) >= 0) s += 45;
    if (phrase && text.indexOf(phrase) >= 0) s += 8;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      if (!t) continue;
      var hit = false;
      var p = title.indexOf(t);
      if (p === 0) { s += 22; hit = true; }
      else if (p > 0) { s += 14; hit = true; }
      if (badge.indexOf(t) >= 0) { s += 7; hit = true; }
      if (heads.indexOf(t) >= 0) { s += 6; hit = true; }
      if (text.indexOf(t) >= 0) { s += 3; hit = true; }
      if (!hit) return 0;              // every term must appear somewhere
    }
    return s;
  }

  function runSearch(q) {
    var phrase = q.toLowerCase().trim();
    var terms = phrase.split(/\s+/).filter(function (t) { return t.length > 1; });
    // Every other exit returns the {rows, total, terms} shape. Returning a bare
    // array here made the first keystroke of every query throw
    // ("undefined is not an object (evaluating 'res.rows.map')") for any
    // single-character token, so keep the shape.
    if (!terms.length) return { rows: [], total: 0, terms: terms };
    var scored = [];
    for (var i = 0; i < IDX.length; i++) {
      var s = scoreDoc(IDX[i], terms, phrase);
      if (s > 0) scored.push({ d: IDX[i], s: s });
    }
    scored.sort(function (a, b) { return b.s - a.s; });

    // Group by space, best group first, best item first inside a group.
    var order = [], bySpace = {};
    for (var j = 0; j < scored.length; j++) {
      var sp = scored[j].d.space || "Other";
      if (!bySpace[sp]) { bySpace[sp] = []; order.push(sp); }
      if (bySpace[sp].length < 5) bySpace[sp].push(scored[j]);
    }
    var out = [];
    for (var k = 0; k < order.length && out.length < 26; k++) {
      out.push({ group: order[k] });
      var items = bySpace[order[k]];
      for (var m = 0; m < items.length && out.length < 26; m++) out.push(items[m].d);
    }
    return { rows: out, total: scored.length, terms: terms };
  }

  /* ------------------------------------------------------- the question bank door
   * `/api/questions` accepts `search` and SILENTLY IGNORES IT: medusa, entropy and
   * quantum all return the same first rows with total always 17,366. Rendering that
   * as "live results" would be inventing matches, so the palette does not query it.
   * Instead it offers one honest row that opens the bank, which owns real search.
   */
  function bankRow(q) {
    return {
      title: q ? 'Search "' + q + '" in the Question Bank' : 'Search the Question Bank',
      sub: '9,969 real IB questions with markschemes — opens the bank',
      url: HUB + 'qbank/'
    };
  }

  /* ---------------------------------------------------------------------- DOM */
  var root = document.createElement("div");
  root.id = "dp-search-root";
  root.innerHTML =
    '<button id="dp-search-btn" type="button" aria-label="Search the whole site">' +
    '<span aria-hidden="true">\uD83D\uDD0D</span><span class="lbl">Search</span><span class="k">\u2318K</span>' +
    "</button>";
  document.body.appendChild(root);

  var st = document.createElement("style");
  st.textContent = CSS;
  document.head.appendChild(st);

  var mask = null, input = null, list = null, countEl = null;

  function buildPanel() {
    mask = document.createElement("div");
    mask.id = "dp-search-mask";
    mask.innerHTML =
      '<div id="dp-search-panel" role="dialog" aria-modal="true" aria-label="Search">' +
      '<div id="dp-search-field">' +
      '<span aria-hidden="true">\uD83D\uDD0D</span>' +
      '<input id="dp-search-input" type="search" placeholder="Search every space — questions, poems, topics, chapters…" autocomplete="off" spellcheck="false" />' +
      '<span id="dp-search-count"></span>' +
      "</div>" +
      '<div id="dp-search-list"></div>' +
      '<div id="dp-search-foot">' +
      "<span><b>\u2191\u2193</b> move</span><span><b>\u21B5</b> open</span>" +
      "<span><b>esc</b> close</span><span id=\"dp-search-note\">opens the Question Bank</span>" +
      "</div></div>";
    document.body.appendChild(mask);
    input = mask.querySelector("#dp-search-input");
    list = mask.querySelector("#dp-search-list");
    countEl = mask.querySelector("#dp-search-count");

    mask.addEventListener("mousedown", function (e) { if (e.target === mask) close(); });
    input.addEventListener("input", function () { CUR = -1; paint(); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") { e.preventDefault(); openCurrent(); }
      else if (e.key === "Escape") { e.preventDefault(); close(); }
    });
    list.addEventListener("mousemove", function (e) {
      var it = e.target.closest ? e.target.closest(".dp-search-item") : null;
      if (!it) return;
      var i = parseInt(it.getAttribute("data-i"), 10);
      if (i !== CUR) { CUR = i; highlight(); }
    });
  }

  function defaultRows() {
    return [{ group: "Study spaces" }].concat(SPACES.map(function (s) {
      return { title: s.t, sub: s.d, badge: "", url: HUB + s.u };
    }));
  }

  function paint() {
    if (!input) return;
    var q = input.value.trim();
    if (!q) {
      RESULTS = []; CUR = -1;
      renderRows(defaultRows(), "", 0);
      countEl.textContent = "";
      return;
    }
    loadIndex(function () {
      if (input.value.trim() !== q) return;      // user kept typing
      var res = runSearch(q);
      var rows = res.rows.map(function (r) {
        if (r.group) return r;
        return {
          title: r.title, badge: r.badge, url: r.url,
          sub: snippet(r.text, res.terms)
        };
      });
      rows = rows.concat([{ group: "Question Bank" }, bankRow(q)]);
      RESULTS = [];
      renderRows(rows, q, res.total, res.terms);
      var shown = rows.filter(function (r) { return !r.group; }).length - 1;
      countEl.textContent = res.total ? (shown + " of " + res.total) : "";
    });
  }

  function renderRows(rows, q, total, terms) {
    var t = terms || (q ? q.toLowerCase().split(/\s+/).filter(function (x) { return x.length > 1; }) : []);
    var html = "";
    if (q && total === 0) {
      html += '<div id="dp-search-empty">Nothing on the site matched <b>' + esc(q) +
        "</b>.<br>Try a topic (“entropy”), a command term (“evaluate”), a poem title, " +
        "or search the Question Bank below.</div>";
    }
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      if (r.group) { html += '<div class="dp-search-group">' + esc(r.group) + "</div>"; continue; }
      var idx = RESULTS.length;
      RESULTS.push(r);
      html += '<a class="dp-search-item" data-i="' + idx + '" href="' + esc(r.url || HUB) + '">' +
        '<div class="dp-search-t">' + (t.length ? mark(r.title, t) : esc(r.title)) +
        (r.badge ? '<span class="dp-search-b">' + esc(r.badge) + "</span>" : "") + "</div>" +
        (r.sub ? '<div class="dp-search-s">' + (t.length ? mark(r.sub, t) : esc(r.sub)) + "</div>" : "") +
        "</a>";
    }
    list.innerHTML = html;
    CUR = -1;
    highlight();
  }

  function items() {
    return list ? Array.prototype.slice.call(list.querySelectorAll(".dp-search-item")) : [];
  }
  function highlight() {
    var all = items();
    for (var i = 0; i < all.length; i++) all[i].classList.toggle("sel", i === CUR);
    if (CUR >= 0 && all[CUR] && all[CUR].scrollIntoView) {
      all[CUR].scrollIntoView({ block: "nearest" });
    }
  }
  function move(d) {
    var n = items().length;
    if (!n) return;
    CUR = (CUR + d + n) % n;
    highlight();
  }
  function openCurrent() {
    var all = items();
    if (CUR >= 0 && all[CUR]) { location.href = all[CUR].getAttribute("href"); close(); return; }
    if (all[0]) { location.href = all[0].getAttribute("href"); close(); }
  }

  function open() {
    loadIndex(function () {});
    if (!mask) buildPanel();
    mask.style.display = "flex";
    document.body.style.overflow = "hidden";
    input.value = "";
    CUR = -1;
    paint();
    setTimeout(function () { input.focus(); }, 10);
  }
  function close() {
    if (!mask) return;
    mask.style.display = "none";
    document.body.style.overflow = "";
  }
  function isOpen() { return mask && mask.style.display === "flex"; }

  root.querySelector("#dp-search-btn").addEventListener("click", open);

  /* Keyboard: capture phase so the hub's own inline search box (app.js) does not
     steal Cmd+K / "/" out from under the palette. */
  document.addEventListener("keydown", function (e) {
    var k = (e.key || "").toLowerCase();
    if ((e.metaKey || e.ctrlKey) && k === "k") {
      e.preventDefault(); e.stopPropagation(); isOpen() ? close() : open(); return;
    }
    if (k === "/" && !e.metaKey && !e.ctrlKey && !e.altKey) {
      var t = e.target, tag = t && t.tagName ? t.tagName.toLowerCase() : "";
      if (tag === "input" || tag === "textarea" || tag === "select" || (t && t.isContentEditable)) return;
      e.preventDefault(); e.stopPropagation(); isOpen() ? close() : open();
    }
  }, true);

  window.dpSearch = { open: open, close: close };
})();
