/* Python Mastery — site behaviour: routing, progress, search, highlighting. */
(function () {
  "use strict";

  var STORE = "python-mastery-v1";
  var state = { done: {}, tasks: {}, theme: "light", last: null, collapsed: {} };

  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
    Object.keys(state).forEach(function (k) { if (saved[k]) state[k] = saved[k]; });
  } catch (e) { /* first visit */ }

  function save() { try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) {} }

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------------- theme ---------------- */
  function applyTheme() {
    document.documentElement.setAttribute("data-theme", state.theme);
    var b = $("#theme-btn");
    if (b) b.textContent = state.theme === "dark" ? "Light" : "Dark";
  }

  /* ---------------- routing ---------------- */
  function slugFromHash() {
    var h = (location.hash || "").replace(/^#\/?/, "");
    if (h && document.getElementById(h)) return h;
    return (window.CHAPTERS[0] || {}).slug;
  }

  function show(slug, opts) {
    opts = opts || {};
    $$(".chapter").forEach(function (s) { s.hidden = s.dataset.slug !== slug; });
    var section = document.getElementById(slug);
    if (!section) return;

    $$(".nav-link").forEach(function (a) { a.classList.toggle("active", a.dataset.slug === slug); });
    var crumb = $("#crumb");
    var meta = CHAPTERS.filter(function (c) { return c.slug === slug; })[0];
    if (crumb && meta) {
      crumb.textContent = (PART_NAMES[meta.part] || "") + (meta.number ? " · Ch " + meta.number : "");
    }

    // build the right-hand TOC
    var toc = $("#toc-list");
    if (toc) {
      toc.innerHTML = (meta && meta.toc.length)
        ? meta.toc.map(function (t) {
            return '<a class="toc-link toc-' + t.level + '" href="#' + t.id + '">' + escapeHtml(t.text) + "</a>";
          }).join("")
        : "";
    }
    $$(".toc-link").forEach(function (a) {
      a.addEventListener("click", function (ev) {
        ev.preventDefault();
        var el = document.getElementById(a.getAttribute("href").slice(1));
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    // Highlight this chapter's code blocks on first view. Doing it lazily keeps the
    // initial paint fast even though the book carries 1400+ code blocks.
    var blocks = section.querySelectorAll(".code code");
    for (var b = 0; b < blocks.length; b++) highlight(blocks[b]);

    state.last = slug;
    save();
    document.body.classList.remove("nav-open");
    if (!opts.keepScroll) window.scrollTo(0, 0);
    document.title = (meta ? meta.title + " — " : "") + "Python Mastery";
    syncDone(slug);
    highlightToc();
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ---------------- progress ---------------- */
  function syncDone(slug) {
    var btn = $('.done-btn[data-slug="' + slug + '"]');
    if (btn) {
      var isDone = !!state.done[slug];
      btn.classList.toggle("done", isDone);
      btn.textContent = isDone ? "✓ Completed — click to reset" : "Mark chapter complete";
    }
    var link = $('.nav-link[data-slug="' + slug + '"]');
    if (link) link.classList.toggle("done", !!state.done[slug]);
    updateProgress();
  }

  function updateProgress() {
    var total = CHAPTERS.length || 1;
    var n = Object.keys(state.done).filter(function (k) { return state.done[k]; }).length;
    var pct = Math.round((n / total) * 100);
    var fill = $("#progress-fill");
    if (fill) fill.style.width = pct + "%";
    var label = $("#progress-label");
    if (label) label.textContent = n + " / " + total + " chapters";
    var pctLabel = $("#progress-pct");
    if (pctLabel) pctLabel.textContent = pct + "%";
  }

  /* ---------------- TOC scrollspy ---------------- */
  function highlightToc() {
    var links = $$(".toc-link");
    if (!links.length) return;
    var best = null;
    links.forEach(function (a) {
      var el = document.getElementById(a.getAttribute("href").slice(1));
      if (el && el.getBoundingClientRect().top <= 120) best = a;
    });
    links.forEach(function (a) { a.classList.toggle("active", a === best); });
  }

  /* ---------------- python-ish highlighter ---------------- */
  var KEYWORDS = {
    python: "def class return if elif else for while in is not and or None True False lambda try except finally raise with as import from pass break continue yield global nonlocal assert del async await match case",
    javascript: "const let var function return if else for while class new await async import from export try catch finally typeof instanceof",
    sql: "SELECT FROM WHERE JOIN LEFT INNER GROUP BY ORDER LIMIT INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE PRIMARY KEY",
    bash: "cd ls echo mkdir rm cp mv cat pip python python3 git export source curl",
    html: "",
  };

  function highlight(node) {
    if (node.dataset.hl === "1") return;
    node.dataset.hl = "1";
    var lang = (node.className.match(/language-([\w-]+)/) || [])[1] || "text";
    var words = (KEYWORDS[lang] || "").split(" ");
    if (!words.length) return;
    var kw = new RegExp("\\b(" + words.join("|") + ")\\b", "g");
    var src = node.textContent;

    // Split into tokens in one pass: comments, strings, numbers, decorators, words.
    var pattern = /(#[^\n]*|\/\/[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(@[\w.]+)|\b(\d+\.?\d*)\b|([A-Za-z_]\w*)/g;
    var out = "", last = 0, m;
    function put(text, cls) {
      out += cls ? '<span class="tok-' + cls + '">' + escapeHtml(text) + "</span>" : escapeHtml(text);
    }
    while ((m = pattern.exec(src)) !== null) {
      put(src.slice(last, m.index));
      last = m.index + m[0].length;
      if (m[1]) put(m[0], "com");
      else if (m[2]) put(m[0], "str");
      else if (m[3]) put(m[0], "dec");
      else if (m[4]) put(m[0], "num");
      else if (m[5]) {
        var followed = src[pattern.lastIndex] === "(";
        var isKw = words.indexOf(m[0]) !== -1;
        put(m[0], isKw ? "kw" : (followed ? "fn" : null));
      }
    }
    put(src.slice(last));
    node.innerHTML = out;
  }

  /* ---------------- search ---------------- */
  function runSearch(q) {
    var box = $("#results");
    var nav = $("#nav");
    q = (q || "").trim().toLowerCase();
    if (q.length < 2) { box.innerHTML = ""; nav.style.display = ""; return; }
    nav.style.display = "none";
    var hits = [];
    CHAPTERS.forEach(function (c) {
      var hay = (c.title + " " + c.summary + " " + (c.tags || []).join(" ")).toLowerCase();
      var idx = hay.indexOf(q);
      if (idx === -1) return;
      hits.push({ c: c, snippet: c.summary });
    });
    box.innerHTML = hits.length
      ? hits.map(function (h) {
          return '<a class="result" href="#/' + h.c.slug + '" data-slug="' + h.c.slug + '">' +
            escapeHtml(h.c.title) + "<small>" + escapeHtml(h.c.summary.slice(0, 90)) + "</small></a>";
        }).join("")
      : '<div class="result">No matches.</div>';
  }

  /* ---------------- init ---------------- */
  function init() {
    applyTheme();

    $("#theme-btn").addEventListener("click", function () {
      state.theme = state.theme === "dark" ? "light" : "dark";
      applyTheme(); save();
    });

    $("#menu-btn").addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });

    // collapsible parts
    $$(".nav-part-btn").forEach(function (btn) {
      var part = btn.parentNode;
      var key = btn.textContent.trim();
      if (state.collapsed[key]) part.classList.add("collapsed");
      btn.addEventListener("click", function () {
        part.classList.toggle("collapsed");
        state.collapsed[key] = part.classList.contains("collapsed");
        save();
      });
    });

    $("#search").addEventListener("input", function (e) { runSearch(e.target.value); });

    // navigation (delegated)
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest ? ev.target.closest("[data-slug]") : null;
      if (a && (a.classList.contains("nav-link") || a.classList.contains("result") ||
                a.classList.contains("pager-btn"))) {
        location.hash = "#/" + a.dataset.slug;
        return;
      }
      var copy = ev.target.closest ? ev.target.closest(".copy-btn") : null;
      if (copy) {
        var code = copy.closest(".code").querySelector("code");
        var text = code ? code.textContent : "";
        var done = function () {
          copy.textContent = "Copied";
          copy.classList.add("copied");
          setTimeout(function () { copy.textContent = "Copy"; copy.classList.remove("copied"); }, 1200);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, done);
        } else {
          var ta = document.createElement("textarea");
          ta.value = text; document.body.appendChild(ta); ta.select();
          try { document.execCommand("copy"); } catch (e) {}
          document.body.removeChild(ta); done();
        }
      }
    });

    // mark complete
    document.addEventListener("click", function (ev) {
      var b = ev.target.closest ? ev.target.closest(".done-btn") : null;
      if (!b) return;
      var slug = b.dataset.slug;
      state.done[slug] = !state.done[slug];
      save(); syncDone(slug);
    });

    // exercise checkboxes
    $$(".task-box").forEach(function (box, i) {
      var key = box.closest(".chapter").dataset.slug + ":" + i;
      box.checked = !!state.tasks[key];
      box.addEventListener("change", function () { state.tasks[key] = box.checked; save(); });
    });

    window.addEventListener("hashchange", function () { show(slugFromHash()); });
    window.addEventListener("scroll", highlightToc, { passive: true });
    document.addEventListener("keydown", function (e) {
      if (/input|textarea/i.test((e.target.tagName || ""))) return;
      var i = CHAPTERS.findIndex(function (c) { return c.slug === slugFromHash(); });
      if (e.key === "ArrowRight" && i < CHAPTERS.length - 1) location.hash = "#/" + CHAPTERS[i + 1].slug;
      if (e.key === "ArrowLeft" && i > 0) location.hash = "#/" + CHAPTERS[i - 1].slug;
      if (e.key === "/") { e.preventDefault(); $("#search").focus(); }
    });

    var start = (location.hash || "").replace(/^#\/?/, "");
    show(document.getElementById(start) ? start : (state.last && document.getElementById(state.last)
      ? state.last : CHAPTERS[0].slug), { keepScroll: false });
    updateProgress();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
