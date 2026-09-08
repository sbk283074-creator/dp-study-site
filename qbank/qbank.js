/* ==========================================================================
   DP Learning Platform — Question Bank shared module
   Loaded (after the data scripts) by every page in /qbank/.
   Exposes window.QB with data access, rendering helpers, a figure lightbox,
   and localStorage-backed wrong book / progress / collections.
   ========================================================================== */
(function () {
  "use strict";
  const QB = {};
  window.QB = QB;

  // Base URL for question-bank figures. Empty = serve relatively from
  // /qbank/figures/ (works over file:// and when figures are committed to the
  // repo). Set to a CDN base (e.g. "https://pub-xxxx.r2.dev/figures/") to serve
  // figures from an external host (Cloudflare R2 / Internet Archive / etc.).
  QB.FIGURE_BASE = "";

  /* ---------- data ------------------------------------------------------- */
  let _cache = null;
  QB.data = function () {
    if (_cache) return _cache;
    const src = window.QB_DATA || {};
    const out = [];
    Object.keys(src).forEach(function (k) {
      const arr = src[k];
      if (Array.isArray(arr)) arr.forEach(function (r) { out.push(r); });
    });
    _cache = out;
    return out;
  };

  QB.groups = function () {
    const labels = { physics: "Physics HL", mathematics: "Mathematics AA HL", "computer-science": "Computer Science HL", other: "Other" };
    const seen = {};
    QB.data().forEach(function (r) { seen[r.group] = (seen[r.group] || 0) + 1; });
    return Object.keys(labels).filter(function (g) { return seen[g]; })
      .map(function (g) { return { v: g, label: labels[g], n: seen[g] }; });
  };

  /* ---------- escaping / rich text -------------------------------------- */
  QB.esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  // plain text stored with \n line breaks + unicode maths symbols -> render
  // with preserved newlines. We deliberately do NOT run MathJax: the bulk of
  // the bank is past-paper text with unicode (ρ, ∆, ±, −) not LaTeX delimiters.
  QB.rich = function (s) { return QB.esc(s).replace(/\n/g, "<br>"); };

  /* ---------- facets (for filter dropdowns) ----------------------------- */
  QB.facet = function (field) {
    const m = {};
    QB.data().forEach(function (r) {
      const v = r[field];
      if (v == null || v === "") return;
      m[v] = (m[v] || 0) + 1;
    });
    return Object.keys(m).sort(function (a, b) { return m[b] - m[a]; })
      .map(function (v) { return { v: v, n: m[v] }; });
  };

  /* ---------- figures ---------------------------------------------------- */
  QB.figures = function (rec) {
    const out = [];
    const push = function (arr, kind) {
      (arr || []).forEach(function (p) { if (p) out.push({ src: (QB.FIGURE_BASE || "figures/") + p, kind: kind }); });
    };
    push(rec.imgQ, "question");
    push(rec.fig, "figure");
    push(rec.imgF, "figure");
    push(rec.figA, "answer");
    push(rec.imgA, "answer");
    return out;
  };

  /* ---------- badges ----------------------------------------------------- */
  QB.statusClass = function (s) { return s === "current" ? "current" : s === "legacy" ? "legacy" : "unknown"; };
  QB.diffBadge = function (d) {
    if (!d) return "";
    const m = { easy: "easy", medium: "medium", hard: "hard" };
    const cls = m[String(d).toLowerCase()] || "sl";
    return '<span class="badge badge--' + cls + '">' + QB.esc(d) + "</span>";
  };

  /* ---------- question card --------------------------------------------- */
  QB.cardHTML = function (rec, opts) {
    opts = opts || {};
    const figs = QB.figures(rec);
    const figHTML = figs.length
      ? '<div class="qcard__figs">' + figs.map(function (f) {
          return '<img class="qb-fig" src="' + QB.esc(f.src) + '" alt="figure" loading="lazy" data-kind="' + f.kind + '" onerror="this.style.display=\'none\'">';
        }).join("") + "</div>"
      : "";
    const meta = [];
    if (rec.marks) meta.push("<span><b>" + rec.marks + "</b> marks</span>");
    if (rec.paper) meta.push("<span>" + QB.esc(rec.paper) + "</span>");
    if (rec.year) meta.push("<span>" + rec.year + (rec.session ? " " + rec.session : "") + "</span>");
    if (rec.command) meta.push("<span>" + QB.esc(rec.command) + "</span>");
    if (rec.topic && rec.topic !== "Physics HL" && rec.topic !== "AA HL" && rec.topic !== "CS HL")
      meta.push("<span>" + QB.esc(rec.topic) + "</span>");
    const diff = QB.diffBadge(rec.difficulty);
    const hasAns = rec.answer || rec.explanation;
    const answerHTML = hasAns
      ? '<div class="qcard__answer" hidden>' +
          '<div class="qcard__answerlabel">Mark scheme / model answer</div>' + QB.rich(rec.answer) +
          (rec.explanation ? '<div class="qcard__explainlabel">Examiner note</div>' + QB.rich(rec.explanation) : "") +
        "</div>"
      : "";
    const actions = opts.actions != null
      ? opts.actions
      : (hasAns ? '<button class="btn qb-reveal" type="button">Show answer</button>' : "");
    let extra = "";
    if (opts.onMarkWrong)
      extra += '<button class="btn qb-markwrong" type="button" data-id="' + QB.esc(rec.id) + '">Wrong</button>';
    if (opts.onSaveColl)
      extra += '<button class="btn qb-savecoll" type="button" data-id="' + QB.esc(rec.id) + '">Save set</button>';
    return '<article class="qcard" data-id="' + QB.esc(rec.id) + '">' +
      '<div class="qcard__head">' +
        '<span class="badge badge--hl">' + QB.esc(rec.level || rec.subject || "") + "</span>" +
        '<span class="qcard__status qcard__status--' + QB.statusClass(rec.status) + '">' + QB.esc(rec.status) + "</span>" +
        diff +
        '<span class="qcard__headspacer"></span>' +
        '<span class="qcard__id">' + QB.esc(rec.id) + "</span>" +
      "</div>" +
      '<div class="qcard__meta">' + meta.join('<span class="qcard__sep">·</span>') + "</div>" +
      '<div class="qcard__body">' + QB.rich(rec.question) + "</div>" +
      figHTML +
      '<div class="qcard__actions">' + actions + extra + "</div>" +
      answerHTML +
    "</article>";
  };

  /* ---------- store ------------------------------------------------------ */
  const NS = "dp.qb.";
  QB.storeGet = function (k, d) { try { return JSON.parse(localStorage.getItem(NS + k)) ?? d; } catch (e) { return d; } };
  QB.storeSet = function (k, v) { try { localStorage.setItem(NS + k, JSON.stringify(v)); } catch (e) {} };

  QB.getWrong = function () { return QB.storeGet("wrong", []); };
  QB.addWrong = function (id) { const w = QB.getWrong(); if (!w.includes(id)) { w.unshift(id); QB.storeSet("wrong", w); } };
  QB.removeWrong = function (id) { QB.storeSet("wrong", QB.getWrong().filter(function (x) { return x !== id; })); };
  QB.inWrong = function (id) { return QB.getWrong().includes(id); };

  QB.getProgress = function () {
    return QB.storeGet("progress", { attempts: 0, correct: 0, wrong: 0, bySubject: {}, sessions: [], streak: 0, lastDay: null });
  };
  QB.recordResult = function (rec, ok) {
    const p = QB.getProgress();
    p.attempts++; if (ok) p.correct++; else p.wrong++;
    const s = rec.group || "other";
    p.bySubject[s] = p.bySubject[s] || { attempts: 0, correct: 0, wrong: 0 };
    p.bySubject[s].attempts++; if (ok) p.bySubject[s].correct++; else p.bySubject[s].wrong++;
    const day = new Date().toISOString().slice(0, 10);
    if (p.lastDay !== day) {
      const y = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
      p.streak = p.lastDay === y ? p.streak + 1 : 1;
      p.lastDay = day;
    }
    p.sessions.push({ t: Date.now(), ok: ok, subj: s });
    if (p.sessions.length > 300) p.sessions = p.sessions.slice(-300);
    QB.storeSet("progress", p);
    if (!ok) QB.addWrong(rec.id);
  };

  QB.getColl = function () { return QB.storeGet("coll", []); };
  QB.saveColl = function (name, filters) { const c = QB.getColl(); c.push({ name: name, filters: filters, t: Date.now() }); QB.storeSet("coll", c); };
  QB.delColl = function (i) { const c = QB.getColl(); c.splice(i, 1); QB.storeSet("coll", c); };

  /* ---------- filtering + search --------------------------------------- */
  QB.applyFilters = function (recs, f) {
    return recs.filter(function (r) {
      if (f.subject && r.group !== f.subject) return false;
      if (f.status && r.status !== f.status) return false;
      if (f.topic && r.topic !== f.topic) return false;
      if (f.paper && r.paper !== f.paper) return false;
      if (f.command && r.command !== f.command) return false;
      if (f.level && r.level !== f.level) return false;
      if (f.year && String(r.year) !== String(f.year)) return false;
      if (f.difficulty && r.difficulty !== f.difficulty) return false;
      if (f.hasFig && !QB.figures(r).length) return false;
      if (f.kp && (r.kps || []).indexOf(f.kp) < 0) return false;
      return true;
    });
  };
  QB.search = function (recs, q) {
    q = (q || "").trim().toLowerCase();
    if (!q) return recs;
    const terms = q.split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return recs;
    return recs.filter(function (r) {
      const hay = ((r.question || "") + " " + (r.answer || "") + " " + (r.topic || "") + " " +
        (r.command || "") + " " + (r.source || "") + " " + (r.tags || []).join(" ")).toLowerCase();
      return terms.every(function (t) { return hay.indexOf(t) >= 0; });
    });
  };

  /* ---------- knowledge points / exams from meta (if present) ---------- */
  QB.knowledgePoints = function () { return (window.QB_META && window.QB_META.knowledgePoints) || []; };
  QB.examPapers = function () { return (window.QB_META && window.QB_META.examPapers) || []; };

  /* ---------- figure lightbox (event-delegated) ------------------------ */
  document.addEventListener("click", function (e) {
    const t = e.target;
    if (t && t.closest) {
      const img = t.closest(".qb-fig");
      if (img) { QB.openLightbox(img.getAttribute("src"), img.getAttribute("alt")); return; }
      const rb = t.closest(".qb-reveal");
      if (rb) {
        const card = rb.closest(".qcard");
        const ans = card && card.querySelector(".qcard__answer");
        if (ans) { ans.hidden = !ans.hidden; rb.textContent = ans.hidden ? "Show answer" : "Hide answer"; }
        return;
      }
    }
  });
  QB.openLightbox = function (src, alt) {
    let lb = document.getElementById("qb-lightbox");
    if (!lb) {
      lb = document.createElement("div");
      lb.id = "qb-lightbox"; lb.className = "qb-lightbox"; lb.hidden = true;
      lb.innerHTML = '<div class="qb-lightbox__inner"><img alt=""><button class="qb-lightbox__close" aria-label="Close" type="button">×</button></div>';
      document.body.appendChild(lb);
      lb.addEventListener("click", function (ev) {
        if (ev.target === lb || (ev.target.closest && ev.target.closest(".qb-lightbox__close"))) lb.hidden = true;
      });
    }
    lb.querySelector("img").src = src; lb.querySelector("img").alt = alt || "";
    lb.hidden = false;
  };

  /* ---------- paged renderer ------------------------------------------- */
  // render(list, container, opts) shows PAGE_SIZE at a time with a Load more.
  const PAGE_SIZE = 40;
  QB.renderPaged = function (list, container, opts) {
    opts = opts || {};
    container.innerHTML = "";
    if (!list.length) {
      container.innerHTML = '<div class="qb-empty">No questions match these filters. Try widening them or switching the currency filter to “all”.</div>';
      return;
    }
    let shown = 0;
    const grid = document.createElement("div");
    grid.className = "qb-grid";
    container.appendChild(grid);
    function append() {
      const next = list.slice(shown, shown + PAGE_SIZE);
      grid.insertAdjacentHTML("beforeend", next.map(function (r) {
        return QB.cardHTML(r, { actions: opts.actions, onMarkWrong: opts.onMarkWrong, onSaveColl: opts.onSaveColl });
      }).join(""));
      shown += next.length;
      if (opts.onAfterRender) opts.onAfterRender(grid);
      if (shown < list.length) {
        let btn = container.querySelector(".qb-loadmore");
        if (!btn) { btn = document.createElement("button"); btn.className = "btn qb-loadmore"; btn.type = "button"; btn.addEventListener("click", append); container.appendChild(btn); }
        btn.textContent = "Load more (" + (list.length - shown) + " remaining)";
      } else { const b = container.querySelector(".qb-loadmore"); if (b) b.remove(); }
    }
    append();
  };

  /* small util: read URL query into a filters object */
  QB.params = function () {
    const p = new URLSearchParams(location.search);
    const f = {};
    ["subject", "status", "topic", "paper", "command", "level", "year", "q"].forEach(function (k) {
      if (p.has(k)) f[k] = p.get(k);
    });
    return f;
  };
})();
