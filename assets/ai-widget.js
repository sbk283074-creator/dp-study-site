/* ============================================================================
 * DP Study Site — global AI Study Assistant + Site Navigator
 * Loaded on every page of the static site (GitHub Pages) from an absolute URL,
 * so updating this one file updates every page at once.
 * Talks to the Cloudflare Worker /api/ask backend (CORS: *).
 * Self-contained: injects its own styles, no external dependencies.
 *
 * THREE THINGS THIS WIDGET DOES
 *
 * 1. AI STUDY ASSISTANT (chat panel)
 *    - Every reply is SPLIT: the model's chain of thought (when the model
 *      returns one) goes into a collapsible "Thinking" block, and only the
 *      finished answer is shown in the body. Reasoning never pollutes the
 *      answer text, and the answer can be COPIED with one click (each reply
 *      carries a Copy row, plus "Copy thinking" when there is any).
 *    - Full-page mode: the ⤢ button in the header expands the panel to fill
 *      the whole viewport (and Esc drops back; Esc again closes).
 *    - The control bar sits directly above the input bar and can be HIDDEN
 *      with the ⚙ toggle when you just want to type — it collapses to a
 *      one-line summary and remembers your choice.
 *      Reply length    short | medium | long     -> token budget + length instruction
 *      Thinking depth  quick | standard | deep   -> temperature + reasoning instruction
 *      Task difficulty easy  | medium   | hard   -> model quality tier
 *      Model           Auto (best fit) | any free model  (explicit Auto option)
 *
 *    "Auto" weighs three indexes — how LONG the answer must be, how COMPLEX the
 *    task is, and how SCARCE or ABUNDANT each model's quota is — to spend the
 *    org's free Groq quota where it helps most:
 *      - token-rich / request-poor models (Compound: 250 req/day, unlimited tokens)
 *          -> long answers and the most complex tasks
 *      - request-rich / token-poor models (Allam: 7,000 req/day, 6K tok/min)
 *          -> many short, simple questions
 *      - balanced models (GPT-OSS 120B / Qwen3.8-27B: 1,000 req/day, 200K tok/day)
 *          -> the everyday middle
 *
 * 2. SITE NAVIGATOR (🧭 Sites button)
 *    A floating button that opens the complete map of the site — every study
 *    space, every subject hub and the guides — so every sub-site links to every
 *    other sub-site from anywhere. The current page is marked "you are here".
 * ==========================================================================*/
(function () {
  "use strict";

  var API = "https://ib-dp-platform-api.pages.dev/api/ask";
  var STATUS = "https://ib-dp-platform-api.pages.dev/api/ask/status";
  var HUB = "https://sbk283074-creator.github.io/dp-study-site/";
  var LS_CHAT = "dp_ai_chat_v1";
  var LS_SET = "dp_ai_settings_v1";

  // Known free-tier pool (labels used for the model picker + live hint).
  // The live status endpoint is consulted first; this is the fallback.
  var MODEL_LABELS = {
    "openai/gpt-oss-120b": "GPT-OSS 120B",
    "openai/gpt-oss-20b": "GPT-OSS 20B",
    "qwen/qwen3.6-27b": "Qwen3 27B",
    "qwen/qwen3.8-27b": "Qwen3.8 27B",
    "groq/compound-mini": "Compound Mini",
    "groq/compound": "Compound",
    "allam-2-7b": "Allam 2 7B"
  };

  // Capability notes used only as a FALLBACK, when the live status endpoint
  // cannot be reached — so the usage panel still tells the student what each
  // model is for even with no quota numbers to show.
  var MODEL_INFO = {
    "openai/gpt-oss-120b": { who: "OpenAI open-weight · 117B MoE", best: "Hardest problems, proofs, multi-step reasoning" },
    "openai/gpt-oss-20b": { who: "OpenAI open-weight · 21B MoE", best: "Quick checks and short explanations" },
    "qwen/qwen3.6-27b": { who: "Alibaba · 27B dense", best: "Chinese answers, general IB questions" },
    "qwen/qwen3.8-27b": { who: "Alibaba · 27B dense", best: "Standard IB questions, especially in Chinese" },
    "groq/compound-mini": { who: "Groq system · 120B + 70B + tools", best: "Long, detailed explanations (unlimited daily tokens)" },
    "groq/compound": { who: "Groq system · 120B + 70B + tools", best: "Long answers that need web search or code tools" },
    "allam-2-7b": { who: "SDAIA · 7B", best: "Many short, simple questions (largest request quota)" }
  };

  // --- the complete site map: every sub-site reachable from every page ------
  var SITE = [
    {
      group: "Study spaces",
      items: [
        { t: "DP Learning \u2014 hub", d: "Six subjects, the DP core, the study plan.", u: "index.html" },
        { t: "Question Bank", d: "9,969 real questions \u2014 practise and review.", u: "qbank/" },
        { t: "Python Mastery", d: "A focused, self-contained Python course.", u: "PYTHON/" },
        { t: "The World's Wife Lab", d: "Duffy's collection, poem by poem.", u: "Eng%20learning/" },
        { t: "Challenge Bank", d: "Original hard problems with full markschemes.", u: "challenge-bank/site/" }
      ]
    },
    {
      group: "Subjects",
      items: [
        { t: "Mathematics AA HL", d: "Five topics, four components, P3 technique.", u: "math/index.html" },
        { t: "Physics HL", d: "Themes A\u2013E plus the IA and uncertainty.", u: "physics/index.html" },
        { t: "Computer Science HL", d: "The 2027 guide \u2014 themes A and B.", u: "cs/index.html" },
        { t: "English A: Lang & Lit SL", d: "Paper 1, Paper 2, individual oral, works.", u: "english/index.html" },
        { t: "Chinese A SL", d: "Paper 1, Paper 2, individual oral, works.", u: "chinese/index.html" },
        { t: "Business Management SL", d: "Five units, two papers, research project.", u: "business/index.html" },
        { t: "DP Core \u2014 TOK \u00b7 EE \u00b7 CAS", d: "The compulsory core outside your six subjects.", u: "core/index.html" }
      ]
    },
    {
      group: "Guides & tools",
      items: [
        { t: "Study plan", d: "How to sequence the whole two-year course.", u: "study-plan.html" },
        { t: "Command terms & exam technique", d: "What each command word actually demands.", u: "exam-toolkit.html" }
      ]
    }
  ];

  function defaultSettings() {
    return {
      depth: "standard",
      difficulty: "medium",
      length: "medium",
      model: "",
      hideControls: false,
      showUsage: false // the usage strip stays collapsed until asked for
    };
  }
  function loadSettings() {
    try {
      var s = JSON.parse(localStorage.getItem(LS_SET) || "{}");
      var d = defaultSettings();
      return {
        depth: s.depth || d.depth,
        difficulty: s.difficulty || d.difficulty,
        length: s.length || d.length,
        model: s.model || d.model,
        hideControls: !!s.hideControls,
        showUsage: !!s.showUsage
      };
    } catch (e) { return defaultSettings(); }
  }
  function saveSettings(s) {
    try { localStorage.setItem(LS_SET, JSON.stringify(s)); } catch (e) {}
  }

  // --- Client-side mirror of the backend's AUTO resolver ---------------------
  // Kept in exact lock-step with resolveAsk() in backend/src/ai.js, so the live
  // "which model will answer" hint never disagrees with what the server does.
  var LEN_NEED = { short: 1, medium: 2, long: 3 };
  var DIFF_NEED = { easy: 1, medium: 2, hard: 3 };
  var DEPTH_NEED = { quick: 1, standard: 2, deep: 3 };
  var REASONS = {
    "groq/compound": "Long + complex \u2192 Compound: unlimited daily tokens plus tools (only 250 req/day, so reserved for the heaviest asks).",
    "groq/compound-mini": "Long reply \u2192 Compound Mini: unlimited daily tokens at 70K tok/min (250 req/day).",
    "openai/gpt-oss-120b": "Hard / deep task \u2192 GPT-OSS 120B: the strongest reasoning model, 200K tokens/day.",
    "allam-2-7b": "Short + simple \u2192 Allam 2 7B: the largest request quota (7,000/day), for many quick questions.",
    "qwen/qwen3.8-27b": "Standard task \u2192 Qwen3.8-27B: the strongest general model, best for Chinese (200K tokens/day)."
  };

  function predictModel(s) {
    var lenNeed = LEN_NEED[s.length] || 2;
    var cplx = Math.max(DIFF_NEED[s.difficulty] || 2, DEPTH_NEED[s.depth] || 2);
    if (lenNeed === 3) return cplx >= 3 ? "groq/compound" : "groq/compound-mini";
    if (cplx >= 3) return "openai/gpt-oss-120b";
    if (cplx <= 1 && lenNeed <= 1) return "allam-2-7b";
    return "qwen/qwen3.8-27b";
  }
  function labelFor(id) { return MODEL_LABELS[id] || id || "AI"; }
  // compact names for the one-line summary shown when the controls are hidden
  var SHORT_AXIS = {
    short: "Short", medium: "Med", long: "Long",
    quick: "Quick", standard: "Std", deep: "Deep",
    easy: "Easy", hard: "Hard"
  };

  // --- infer the subject/space from the current URL path ---
  function inferSubject() {
    var p = location.pathname.toLowerCase();
    if (p.indexOf("/math/") > -1) return "Mathematics AA HL";
    if (p.indexOf("/physics/") > -1) return "Physics HL";
    if (p.indexOf("/cs/") > -1) return "Computer Science HL";
    if (p.indexOf("/english/") > -1) return "English A Lang & Lit SL";
    if (p.indexOf("/chinese/") > -1) return "Chinese A SL";
    if (p.indexOf("/business/") > -1) return "Business Management SL";
    if (p.indexOf("/core/") > -1) return "DP Core (TOK / EE / CAS)";
    if (p.indexOf("/qbank/") > -1) return "Question Bank";
    if (p.indexOf("/challenge-bank/") > -1) return "Challenge Bank";
    if (p.indexOf("/python") > -1) return "Python Mastery";
    if (p.indexOf("/eng%20learning") > -1 || p.indexOf("/eng learning") > -1) return "The World's Wife Lab";
    return "";
  }

  // --- which site-map entry are we on? (exact page, else nearest section) ---
  function normPath(u) {
    var p;
    try { p = new URL(u, HUB).pathname; } catch (e) { p = String(u); }
    p = p.replace(/index\.html$/, "");
    if (p.length > 1) p = p.replace(/\/+$/, "");
    return p;
  }
  function currentEntryUrl() {
    var here = normPath(location.href);
    var best = null, bestLen = -1;
    for (var i = 0; i < SITE.length; i++) {
      for (var j = 0; j < SITE[i].items.length; j++) {
        var it = SITE[i].items[j];
        var t = normPath(HUB + it.u);
        if (t === here) return it.u;                    // the exact page
        if (it.u === "index.html") continue;            // never prefix-match the hub root
        if (here.indexOf(t + "/") === 0 && t.length > bestLen) {  // a page inside that section
          bestLen = t.length;
          best = it.u;
        }
      }
    }
    return best;
  }

  // --- tiny safe formatter: escape, then a few markdown-ish touches ---
  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function format(text) {
    var safe = escapeHtml(text);
    safe = safe.replace(/`([^`]+)`/g, "<code>$1</code>");
    safe = safe.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    safe = safe.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
    safe = safe.replace(/(^|[^_])_([^_\n]+)_/g, "$1<em>$2</em>");
    safe = safe.replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>");
    return "<p>" + safe + "</p>";
  }

  function loadHistory() {
    try { return JSON.parse(localStorage.getItem(LS_CHAT) || "[]"); }
    catch (e) { return []; }
  }
  function saveHistory(arr) {
    try { localStorage.setItem(LS_CHAT, JSON.stringify(arr.slice(-40))); } catch (e) {}
  }

  // one labelled segmented row:  <label> <btn><btn><btn>
  function segRow(axis, label, opts) {
    var btns = opts.map(function (o) {
      return '<button type="button" data-v="' + o.v + '">' + escapeHtml(o.t) + '</button>';
    }).join("");
    return '<div class="dp-ai-ctrl-row">' +
      '<span class="dp-ai-ctrl-lab">' + escapeHtml(label) + '</span>' +
      '<div class="dp-ai-seg" data-axis="' + axis + '">' + btns + '</div>' +
      '</div>';
  }

  // the whole-site navigator markup
  function navMarkup() {
    var currentUrl = currentEntryUrl();
    var out = '<div class="dp-ai-nav-head">' +
      '<div><h3>Site map</h3><span class="dp-ai-nav-sub">Every space, subject and guide \u2014 from any page</span></div>' +
      '<button id="dpAiNavClose" aria-label="Close site map">\u00d7</button>' +
      '</div><div class="dp-ai-nav-body">';
    SITE.forEach(function (sec) {
      out += '<div class="dp-ai-nav-group"><span class="dp-ai-nav-group-lab">' + escapeHtml(sec.group) + '</span>';
      sec.items.forEach(function (it) {
        var cur = (it.u === currentUrl);
        out += '<a class="dp-ai-nav-item' + (cur ? ' is-here' : '') + '" href="' + HUB + it.u + '"' +
          (cur ? ' aria-current="page"' : '') + '>' +
          '<span class="dp-ai-nav-t">' + escapeHtml(it.t) +
          (cur ? '<em class="dp-ai-nav-here">you are here</em>' : '') + '</span>' +
          '<span class="dp-ai-nav-d">' + escapeHtml(it.d) + '</span>' +
          '</a>';
      });
      out += '</div>';
    });
    out += '<div class="dp-ai-nav-group"><span class="dp-ai-nav-group-lab">Suggested flow</span>' +
      '<p class="dp-ai-nav-flow">Understand a topic in <a href="' + HUB + 'index.html">DP Learning</a> ' +
      '\u2192 test it in the <a href="' + HUB + 'qbank/">Question Bank</a> ' +
      '\u2192 build fluency in <a href="' + HUB + 'PYTHON/">Python Mastery</a> ' +
      '\u2192 go line by line through <a href="' + HUB + 'Eng%20learning/">The World\u2019s Wife</a> ' +
      '\u2192 stretch on the <a href="' + HUB + 'challenge-bank/site/">Challenge Bank</a>.</p></div>';
    out += '</div>';
    return out;
  }

  function build() {
    if (document.getElementById("dp-ai-root")) return;

    var subject = inferSubject();
    var settings = loadSettings();

    var styles = [
      ".dp-ai-launch{position:fixed;right:18px;bottom:18px;z-index:2147483000;display:flex;align-items:center;gap:10px}",
      ".dp-ai-btn{display:flex;align-items:center;gap:8px;padding:12px 16px;border:none;border-radius:999px;",
      "background:#3653d6;background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff;font:600 14px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;",
      "cursor:pointer;box-shadow:0 6px 20px rgba(54,83,214,.35);transition:transform .15s ease,box-shadow .15s ease}",
      ".dp-ai-btn:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(54,83,214,.45)}",
      ".dp-ai-btn__dot{width:8px;height:8px;border-radius:50%;background:#9affc4;box-shadow:0 0 0 3px rgba(154,255,196,.25)}",
      ".dp-ai-ghost{display:flex;align-items:center;gap:7px;padding:11px 14px;border:1px solid #d8dfeb;border-radius:999px;",
      "background:#fff;color:#334155;font:600 13px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;",
      "box-shadow:0 4px 14px rgba(16,24,40,.12);transition:transform .15s ease,border-color .15s ease,color .15s ease}",
      ".dp-ai-ghost:hover{transform:translateY(-2px);border-color:#3653d6;color:#3653d6}",
      ".dp-ai-ghost .ic{font-size:14px;line-height:1}",
      // ---- chat panel ----
      ".dp-ai-panel{position:fixed;right:18px;bottom:78px;z-index:2147483002;width:min(400px,calc(100vw - 36px));",
      "height:min(640px,calc(100vh - 96px));display:none;flex-direction:column;background:#fff;border:1px solid #e3e8f0;",
      "border-radius:16px;overflow:hidden;box-shadow:0 18px 50px rgba(16,24,40,.18);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#151923}",
      ".dp-ai-panel.open{display:flex}",
      ".dp-ai-panel--full{top:0;right:0;bottom:0;left:0;width:auto;height:auto;max-width:none;border-radius:0;border:none}",
      ".dp-ai-panel--full .dp-ai-msgs{padding-left:max(16px,calc((100% - 860px)/2));padding-right:max(16px,calc((100% - 860px)/2))}",
      ".dp-ai-panel--full .dp-ai-ctrl,.dp-ai-panel--full .dp-ai-input,.dp-ai-panel--full .dp-ai-foot,",
      ".dp-ai-panel--full .dp-ai-head{padding-left:max(16px,calc((100% - 860px)/2));padding-right:max(16px,calc((100% - 860px)/2))}",
      ".dp-ai-head{display:flex;align-items:center;gap:8px;padding:14px 14px;background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff}",
      ".dp-ai-head h3{margin:0;font-size:15px;font-weight:700;flex:1}",
      ".dp-ai-head .chip{font-size:11px;font-weight:600;background:rgba(255,255,255,.18);padding:3px 8px;border-radius:999px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px}",
      ".dp-ai-head button{background:rgba(255,255,255,.15);border:none;color:#fff;width:28px;height:28px;border-radius:8px;cursor:pointer;font-size:15px;line-height:1}",
      ".dp-ai-head button:hover{background:rgba(255,255,255,.28)}",
      // min-height:0 lets the message list actually shrink in a flex column, so
      // opening the usage strip can never push the input out of the panel
      ".dp-ai-msgs{flex:1;min-height:0;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:#fafbfd}",
      ".dp-ai-msg{max-width:88%;padding:10px 13px;border-radius:12px;font-size:14px;line-height:1.55;word-wrap:break-word}",
      ".dp-ai-msg p{margin:0 0 8px}.dp-ai-msg p:last-child{margin:0}",
      ".dp-ai-msg code{background:#eef1ff;padding:1px 5px;border-radius:5px;font-size:12.5px}",
      ".dp-ai-msg.user{align-self:flex-end;background:#3653d6;color:#fff;border-bottom-right-radius:4px}",
      ".dp-ai-msg.bot{align-self:flex-start;background:#fff;border:1px solid #e3e8f0;border-bottom-left-radius:4px}",
      ".dp-ai-msg.bot strong{color:#2a44b8}",
      // ---- reason / answer split + copy controls ----
      ".dp-ai-think{margin:0 0 9px;border:1px solid #e3e8f0;background:#f7f9fd;border-radius:9px;overflow:hidden}",
      ".dp-ai-think-toggle{display:block;width:100%;text-align:left;border:none;background:transparent;padding:6px 9px;",
      "cursor:pointer;font:600 11.5px -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#5a6577}",
      ".dp-ai-think-toggle:hover{color:#3653d6}",
      ".dp-ai-think-n{font-weight:500;color:#94a0b2}",
      ".dp-ai-think-body{display:none;padding:4px 10px 9px;border-top:1px solid #e6eaf3;font-size:12.5px;line-height:1.5;",
      "color:#5a6577;max-height:260px;overflow:auto}",
      ".dp-ai-think-body.open{display:block}",
      ".dp-ai-think-body strong{color:#3c4657}",
      ".dp-ai-think-body code{background:#eef1ff}",
      ".dp-ai-acts{display:flex;gap:6px;margin-top:9px;padding-top:8px;border-top:1px solid #eef1f6}",
      ".dp-ai-act{border:1px solid #d8dfeb;background:#fff;color:#5a6577;",
      "font:600 11px -apple-system,Segoe UI,Roboto,Arial,sans-serif;padding:4px 10px;border-radius:999px;cursor:pointer}",
      ".dp-ai-act:hover{border-color:#3653d6;color:#3653d6}",
      ".dp-ai-act.ok{border-color:#1f9d5a;color:#1f9d5a}",
      ".dp-ai-msg.err{align-self:flex-start;background:#fdeceb;color:#b02a1f;border:1px solid #f5c4bf;border-bottom-left-radius:4px}",
      // ---- collapsible control bar, attached to the input ----
      ".dp-ai-ctrl{border-top:1px solid #eef1f6;background:#fff}",
      ".dp-ai-ctrl-toggle{display:flex;align-items:center;gap:8px;width:100%;border:none;background:transparent;",
      "padding:9px 12px;cursor:pointer;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;text-align:left}",
      ".dp-ai-ctrl-toggle:hover{background:#f7f9fd}",
      ".dp-ai-ctrl-toggle .gear{font-size:12px;line-height:1;color:#7a8398}",
      ".dp-ai-ctrl-toggle .tlab{font-size:11px;font-weight:700;color:#7a8398;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}",
      ".dp-ai-ctrl-sum{flex:1;font-size:11.5px;font-weight:600;color:#3653d6;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right}",
      ".dp-ai-chev{color:#94a0b2;font-size:12px;line-height:1;transition:transform .15s ease}",
      ".dp-ai-ctrl.collapsed .dp-ai-chev{transform:rotate(-90deg)}",
      ".dp-ai-ctrl-body{padding:0 12px 8px}",
      ".dp-ai-ctrl.collapsed .dp-ai-ctrl-body{display:none}",
      ".dp-ai-ctrl-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}",
      ".dp-ai-ctrl-lab{flex:0 0 46px;font-size:10px;font-weight:700;color:#7a8398;text-transform:uppercase;letter-spacing:.04em}",
      ".dp-ai-seg{flex:1;display:flex;gap:3px;background:#eef1f6;border-radius:9px;padding:3px}",
      ".dp-ai-seg button{flex:1;border:none;background:transparent;padding:6px 2px;border-radius:7px;font:600 11.5px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#5a6577;cursor:pointer;transition:all .12s}",
      ".dp-ai-seg button:hover{color:#3653d6}",
      ".dp-ai-seg button.on{background:#fff;color:#3653d6;box-shadow:0 1px 3px rgba(16,24,40,.14)}",
      "select.dp-ai-sel{flex:1;padding:7px 9px;border:1px solid #ccd5e4;border-radius:9px;font:600 12px -apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#fff;color:#151923;cursor:pointer}",
      ".dp-ai-hint{font-size:11px;color:#5a6577;background:#f4f6fb;border:1px solid #e6eaf3;border-radius:8px;padding:6px 9px;line-height:1.45;margin-top:2px}",
      ".dp-ai-hint b{color:#2a44b8}",
      // ---- collapsible usage strip: one line when closed ----
      ".dp-ai-usage{position:relative;border-top:1px solid #eef1f6;background:#fff}",
      ".dp-ai-usage-toggle{display:flex;align-items:center;gap:8px;width:100%;border:none;background:transparent;",
      "padding:7px 12px;cursor:pointer;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;text-align:left}",
      ".dp-ai-usage-toggle:hover{background:#f7f9fd}",
      ".dp-ai-usage-toggle .dot{width:7px;height:7px;border-radius:50%;background:#1f9d5a;box-shadow:0 0 0 3px rgba(31,157,90,.18);flex:0 0 auto}",
      ".dp-ai-usage-toggle .dot.warn{background:#d97706;box-shadow:0 0 0 3px rgba(217,119,6,.16)}",
      ".dp-ai-usage-toggle .dot.off{background:#b9c0cf;box-shadow:none}",
      ".dp-ai-usage-toggle .tlab{font-size:10px;font-weight:800;color:#7a8398;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}",
      ".dp-ai-usage-sum{flex:1;font-size:11px;font-weight:600;color:#3653d6;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right}",
      ".dp-ai-usage .dp-ai-chev{transform:rotate(-90deg)}",
      ".dp-ai-usage.open .dp-ai-chev{transform:none}",
      // the open body floats over the conversation instead of pushing the input
      // box around, so it costs exactly zero layout space on any screen
      ".dp-ai-usage-body{display:none;position:absolute;left:0;right:0;bottom:100%;z-index:2;",
      "box-sizing:border-box;padding:9px 12px;max-height:190px;overflow-y:auto;background:#fff;",
      "border-top:1px solid #eef1f6;box-shadow:0 -10px 24px rgba(16,24,40,.10)}",
      ".dp-ai-usage.open .dp-ai-usage-body{display:block}",
      ".dp-ai-urow{border:1px solid #e6eaf3;border-radius:8px;padding:6px 8px;margin-bottom:5px;background:#fbfcfe}",
      ".dp-ai-urow.on{background:#f2f5ff;border-color:#dbe2ff}",
      ".dp-ai-urow .top{display:flex;justify-content:space-between;align-items:baseline;gap:8px}",
      ".dp-ai-urow .nm{font-size:11.5px;font-weight:700;color:#1d2436;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}",
      ".dp-ai-urow .q{font-size:10.5px;color:#5a6577;white-space:nowrap}",
      ".dp-ai-urow .sub{display:block;font-size:10.5px;color:#6c7788;margin-top:2px;line-height:1.4}",
      ".dp-ai-unote{margin:2px 0 0;font-size:10px;color:#8b93a7;line-height:1.45}",
      ".dp-ai-foot{padding:7px 12px;font-size:11px;color:#6c7788;display:flex;justify-content:space-between;align-items:center;gap:8px;border-top:1px solid #eef1f6;background:#fff}",
      ".dp-ai-foot .meta{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}",
      ".dp-ai-foot a{color:#3653d6;text-decoration:none;font-weight:600;white-space:nowrap}",
      ".dp-ai-input{display:flex;gap:8px;padding:10px 12px 12px;background:#fff}",
      ".dp-ai-input textarea{flex:1;resize:none;border:1px solid #ccd5e4;border-radius:10px;padding:9px 11px;font:14px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif;outline:none;max-height:120px}",
      ".dp-ai-input textarea:focus{border-color:#3653d6;box-shadow:0 0 0 3px #eef1ff}",
      ".dp-ai-input button{background:#3653d6;color:#fff;border:none;border-radius:10px;padding:0 16px;font-weight:700;cursor:pointer}",
      ".dp-ai-input button:disabled{opacity:.5;cursor:default}",
      ".dp-ai-typing{display:inline-flex;gap:4px;padding:4px 2px}",
      ".dp-ai-typing span{width:6px;height:6px;border-radius:50%;background:#94a0b2;animation:dpai-b 1s infinite ease-in-out}",
      ".dp-ai-typing span:nth-child(2){animation-delay:.15s}.dp-ai-typing span:nth-child(3){animation-delay:.3s}",
      "@keyframes dpai-b{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}",
      // ---- site navigator panel ----
      ".dp-ai-nav{position:fixed;right:18px;bottom:78px;z-index:2147483002;width:min(430px,calc(100vw - 36px));",
      "height:min(620px,calc(100vh - 96px));display:none;flex-direction:column;background:#fff;border:1px solid #e3e8f0;",
      "border-radius:16px;overflow:hidden;box-shadow:0 18px 50px rgba(16,24,40,.18);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#151923}",
      ".dp-ai-nav.open{display:flex}",
      ".dp-ai-nav-head{display:flex;align-items:flex-start;gap:8px;padding:14px;background:linear-gradient(135deg,#1f2a44,#31456e);color:#fff}",
      ".dp-ai-nav-head h3{margin:0;font-size:15px;font-weight:700}",
      ".dp-ai-nav-head .dp-ai-nav-sub{display:block;font-size:11px;color:rgba(255,255,255,.72);margin-top:2px}",
      ".dp-ai-nav-head>div{flex:1}",
      ".dp-ai-nav-head button{background:rgba(255,255,255,.15);border:none;color:#fff;width:28px;height:28px;border-radius:8px;cursor:pointer;font-size:15px;line-height:1}",
      ".dp-ai-nav-head button:hover{background:rgba(255,255,255,.28)}",
      ".dp-ai-nav-body{flex:1;overflow-y:auto;padding:12px 12px 16px;background:#fafbfd}",
      ".dp-ai-nav-group{margin-bottom:14px}",
      ".dp-ai-nav-group-lab{display:block;font-size:10px;font-weight:800;color:#8b93a7;text-transform:uppercase;letter-spacing:.06em;margin:0 2px 6px}",
      ".dp-ai-nav-item{display:block;padding:9px 11px;border:1px solid #e6eaf3;border-radius:10px;background:#fff;margin-bottom:6px;text-decoration:none;transition:border-color .12s,transform .12s}",
      ".dp-ai-nav-item:hover{border-color:#3653d6;transform:translateX(2px)}",
      ".dp-ai-nav-t{display:flex;align-items:center;gap:7px;font-size:13.5px;font-weight:700;color:#1d2436}",
      ".dp-ai-nav-item:hover .dp-ai-nav-t{color:#2a44b8}",
      ".dp-ai-nav-d{display:block;font-size:11.5px;color:#6c7788;margin-top:2px;line-height:1.4}",
      ".dp-ai-nav-item.is-here{border-color:#3653d6;background:#f2f5ff;cursor:default}",
      ".dp-ai-nav-item.is-here:hover{transform:none}",
      ".dp-ai-nav-here{font-style:normal;font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:#fff;background:#3653d6;padding:2px 6px;border-radius:999px}",
      ".dp-ai-nav-flow{margin:0 2px;font-size:11.5px;line-height:1.6;color:#5a6577}",
      ".dp-ai-nav-flow a{color:#3653d6;text-decoration:none;font-weight:600}"
    ].join("");

    var styleEl = document.createElement("style");
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);

    var root = document.createElement("div");
    root.id = "dp-ai-root";
    root.innerHTML =
      '<div class="dp-ai-launch">' +
        '<button class="dp-ai-ghost" id="dpAiNavBtn" aria-label="Open the site map" aria-expanded="false">' +
          '<span class="ic">\uD83E\uDDED</span><span>Sites</span>' +
        '</button>' +
        '<button class="dp-ai-btn" id="dpAiBtn" aria-label="Open AI study assistant" aria-expanded="false">' +
          '<span class="dp-ai-btn__dot"></span><span>Ask AI</span>' +
        '</button>' +
      '</div>' +
      '<div class="dp-ai-nav" id="dpAiNav" role="dialog" aria-label="Site map">' + navMarkup() + '</div>' +
      '<div class="dp-ai-panel" id="dpAiPanel" role="dialog" aria-label="AI study assistant">' +
        '<div class="dp-ai-head">' +
          '<h3>AI Study Assistant</h3>' +
          (subject ? '<span class="chip" id="dpAiSubj">' + escapeHtml(subject) + '</span>' : '') +
          '<button id="dpAiExpand" aria-label="Toggle full page" title="Full-page mode">\u2922</button>' +
          '<button id="dpAiClose" aria-label="Close">\u00d7</button>' +
        '</div>' +
        '<div class="dp-ai-msgs" id="dpAiMsgs"></div>' +
        '<div class="dp-ai-usage" id="dpAiUsage">' +
          '<button class="dp-ai-usage-toggle" id="dpAiUsageToggle" aria-expanded="false" aria-controls="dpAiUsageBody" ' +
            'title="How much free AI is left today, and what each model is for">' +
            '<span class="dot off" id="dpAiUsageDot"></span>' +
            '<span class="tlab">Usage</span>' +
            '<span class="dp-ai-usage-sum" id="dpAiUsageSum">checking\u2026</span>' +
            '<span class="dp-ai-chev">\u25be</span>' +
          '</button>' +
          '<div class="dp-ai-usage-body" id="dpAiUsageBody"></div>' +
        '</div>' +
        '<div class="dp-ai-ctrl" id="dpAiCtrl">' +
          '<button class="dp-ai-ctrl-toggle" id="dpAiCtrlToggle" aria-expanded="true">' +
            '<span class="gear">\u2699</span>' +
            '<span class="tlab">Model &amp; controls</span>' +
            '<span class="dp-ai-ctrl-sum" id="dpAiCtrlSum"></span>' +
            '<span class="dp-ai-chev">\u25be</span>' +
          '</button>' +
          '<div class="dp-ai-ctrl-body" id="dpAiCtrlBody">' +
            segRow("length", "Length", [{ v: "short", t: "Short" }, { v: "medium", t: "Medium" }, { v: "long", t: "Long" }]) +
            segRow("depth", "Think", [{ v: "quick", t: "Quick" }, { v: "standard", t: "Standard" }, { v: "deep", t: "Deep" }]) +
            segRow("difficulty", "Task", [{ v: "easy", t: "Easy" }, { v: "medium", t: "Medium" }, { v: "hard", t: "Hard" }]) +
            '<div class="dp-ai-ctrl-row">' +
              '<span class="dp-ai-ctrl-lab">Model</span>' +
              '<select class="dp-ai-sel" id="dpAiModel"><option value="">Auto \u2014 best fit for my choices</option></select>' +
            '</div>' +
            '<div class="dp-ai-hint" id="dpAiHint"></div>' +
          '</div>' +
        '</div>' +
        '<div class="dp-ai-input">' +
          '<textarea id="dpAiText" rows="1" placeholder="Ask anything about ' + (subject || "your IB subjects") + '\u2026"></textarea>' +
          '<button id="dpAiSend">Send</button>' +
        '</div>' +
        '<div class="dp-ai-foot"><span class="meta" id="dpAiMeta"></span><a href="' + HUB + '" target="_blank" rel="noopener">\u2302 Hub</a></div>' +
      '</div>';
    document.body.appendChild(root);

    var btn = document.getElementById("dpAiBtn");
    var panel = document.getElementById("dpAiPanel");
    var msgs = document.getElementById("dpAiMsgs");
    var text = document.getElementById("dpAiText");
    var send = document.getElementById("dpAiSend");
    var meta = document.getElementById("dpAiMeta");
    var closeBtn = document.getElementById("dpAiClose");
    var expandBtn = document.getElementById("dpAiExpand");
    var ctrl = document.getElementById("dpAiCtrl");
    var ctrlBody = document.getElementById("dpAiCtrlBody");
    var ctrlToggle = document.getElementById("dpAiCtrlToggle");
    var ctrlSum = document.getElementById("dpAiCtrlSum");
    var modelSel = document.getElementById("dpAiModel");
    var hintEl = document.getElementById("dpAiHint");
    var usageBox = document.getElementById("dpAiUsage");
    var usageToggle = document.getElementById("dpAiUsageToggle");
    var usageSum = document.getElementById("dpAiUsageSum");
    var usageBody = document.getElementById("dpAiUsageBody");
    var usageDot = document.getElementById("dpAiUsageDot");
    var navBtn = document.getElementById("dpAiNavBtn");
    var nav = document.getElementById("dpAiNav");
    var navClose = document.getElementById("dpAiNavClose");

    // last good /api/ask/status payload — feeds the usage strip
    var poolState = null;

    function scrollDown() { msgs.scrollTop = msgs.scrollHeight; }

    // ---- copy to clipboard (with a fallback for non-secure contexts) ----
    function copyText(str, btn) {
      var label = btn.textContent;
      function done() {
        btn.textContent = "Copied \u2713";
        btn.classList.add("ok");
        setTimeout(function () { btn.textContent = label; btn.classList.remove("ok"); }, 1400);
      }
      function fallback(s) {
        try {
          var ta = document.createElement("textarea");
          ta.value = s;
          ta.setAttribute("readonly", "");
          ta.style.position = "fixed";
          ta.style.left = "-9999px";
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
          done();
        } catch (e) { btn.textContent = "Copy failed"; }
      }
      var s = String(str == null ? "" : str);
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(s).then(done, function () { fallback(s); });
        } else { fallback(s); }
      } catch (e) { fallback(s); }
    }

    // plain text of a rendered answer, for when no raw text was stored.
    // Line breaks are re-inserted (a <br> or a block boundary becomes a newline)
    // because the splitter below works line by line — without this, a heading
    // that was alone on its line in the reply would run into the text before it.
    function toPlain(html) {
      var d = document.createElement("div");
      d.innerHTML = String(html == null ? "" : html)
        .replace(/<br\s*\/?>/gi, "\n")
        .replace(/<\/(?:p|div|li|h[1-6]|tr|section|article|blockquote|pre)>/gi, "\n");
      return (d.textContent || "").replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
    }

    // The server already separates thinking from the answer (splitThinking() in
    // backend/src/ai.js). This is the client-side twin, kept for two reasons:
    //   - a cached API build that predates the split still returns them merged;
    //   - conversations saved BEFORE the split existed are still in localStorage.
    // It handles the same three shapes: <think> blocks, raw reasoning channels,
    // and a plain-text "Thinking:" section.
    var PLAIN_THINK_HEADING =
      /^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*|__)?[ \t]*(?:thinking|chain[ -]of[ -]thought|internal reasoning|reasoning process|thought process|scratchpad)[ \t]*(?:\*\*|__)?[ \t]*:[ \t]*(?:\*\*|__)?[ \t]*$/im;

    function splitInlineThinking(text) {
      var t = text == null ? "" : String(text);
      var parts = [];
      function grab(inner) {
        inner = String(inner).trim();
        if (inner) parts.push(inner);
        return "\n";
      }
      t = t.replace(/<think(?:ing)?\b[^>]*>([\s\S]*?)<\/think(?:ing)?>/gi, function (_m, inner) { return grab(inner); });
      t = t.replace(/<analysis\b[^>]*>([\s\S]*?)<\/analysis>/gi, function (_m, inner) { return grab(inner); });
      t = t.replace(/<\|(?:start|end|channel|message|constrain|return|call|tool)\|>/gi, "");
      var h = PLAIN_THINK_HEADING.exec(t);
      if (h) {
        var before = t.slice(0, h.index).trim();
        var after = t.slice(h.index + h[0].length).trim();
        // only when a real answer already precedes the heading
        if (before.length >= 20 && after.length >= 40) {
          parts.push(after);
          t = before;
        }
      }
      return {
        answer: t.replace(/\n{3,}/g, "\n\n").trim(),
        thinking: parts.join("\n\n").trim()
      };
    }

    // A bot reply carries two extra things: the model's chain of thought, in a
    // block that stays COLLAPSED (so thinking is separated from the answer, the
    // way a normal assistant does it), and a row of copy controls.
    function decorateBot(el, text, thinking) {
      var inner = el.innerHTML;
      var plain = text || toPlain(inner);
      el.innerHTML = "";
      if (thinking) {
        var wrap = document.createElement("div");
        wrap.className = "dp-ai-think";
        var tg = document.createElement("button");
        tg.type = "button";
        tg.className = "dp-ai-think-toggle";
        var body = document.createElement("div");
        body.className = "dp-ai-think-body";
        body.innerHTML = format(thinking);
        function paint(open) {
          tg.setAttribute("aria-expanded", open ? "true" : "false");
          tg.innerHTML = (open ? "\u25be " : "\u25b8 ") + "Thinking <span class=\"dp-ai-think-n\">" +
            thinking.length.toLocaleString() + " chars</span>";
        }
        tg.addEventListener("click", function () {
          paint(body.classList.toggle("open"));
        });
        paint(false);
        wrap.appendChild(tg);
        wrap.appendChild(body);
        el.appendChild(wrap);
      }
      // the finished answer, in its own container so it is never confused with
      // the reasoning that sits above it
      var ans = document.createElement("div");
      ans.className = "dp-ai-answer";
      ans.innerHTML = inner;
      el.appendChild(ans);

      var acts = document.createElement("div");
      acts.className = "dp-ai-acts";
      var cp = document.createElement("button");
      cp.type = "button";
      cp.className = "dp-ai-act";
      cp.textContent = "Copy";
      cp.title = "Copy this answer";
      cp.addEventListener("click", function () { copyText(plain, cp); });
      acts.appendChild(cp);
      if (thinking) {
        var cpt = document.createElement("button");
        cpt.type = "button";
        cpt.className = "dp-ai-act";
        cpt.textContent = "Copy thinking";
        cpt.addEventListener("click", function () { copyText(thinking, cpt); });
        acts.appendChild(cpt);
      }
      el.appendChild(acts);
    }

    function addMsg(role, html, meta) {
      var el = document.createElement("div");
      el.className = "dp-ai-msg " + role;
      el.innerHTML = html;
      if (role === "bot" && meta) decorateBot(el, meta.text, meta.thinking || "");
      msgs.appendChild(el);
      scrollDown();
      return el;
    }

    // restore history — anything saved before the thinking/answer split is
    // migrated on the way in, so old replies no longer show reasoning inline
    var history = loadHistory();
    history.forEach(function (m) {
      if (m.role === "bot") {
        var raw = m.text || toPlain(m.html);
        var sp = splitInlineThinking(raw);
        var ans = sp.answer || raw;
        var think = m.thinking || sp.thinking || "";
        addMsg("bot", format(ans), { text: ans, thinking: think });
      } else {
        addMsg(m.role, m.html);
      }
    });

    function pushHistory(role, html, meta) {
      var item = { role: role, html: html };
      if (role === "bot" && meta) { item.text = meta.text; item.thinking = meta.thinking || ""; }
      history.push(item);
      saveHistory(history);
    }

    function openPanel() {
      nav.classList.remove("open");
      panel.classList.add("open");
      btn.setAttribute("aria-expanded", "true");
      text.focus();
    }
    function closePanel() {
      panel.classList.remove("open");
      panel.classList.remove("dp-ai-panel--full");
      expandBtn.textContent = "\u2922";
      expandBtn.title = "Full-page mode";
      btn.setAttribute("aria-expanded", "false");
    }
    function toggleFull() {
      var on = panel.classList.toggle("dp-ai-panel--full");
      expandBtn.textContent = on ? "\u2921" : "\u2922";
      expandBtn.title = on ? "Exit full page" : "Full-page mode";
      text.focus();
    }
    function openNav() {
      closePanel();
      nav.classList.add("open");
      navBtn.setAttribute("aria-expanded", "true");
    }
    function closeNav() {
      nav.classList.remove("open");
      navBtn.setAttribute("aria-expanded", "false");
    }

    btn.addEventListener("click", function () {
      if (panel.classList.contains("open")) closePanel(); else openPanel();
    });
    closeBtn.addEventListener("click", closePanel);
    expandBtn.addEventListener("click", toggleFull);
    navBtn.addEventListener("click", function () {
      if (nav.classList.contains("open")) closeNav(); else openNav();
    });
    if (navClose) navClose.addEventListener("click", closeNav);
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (panel.classList.contains("dp-ai-panel--full")) { toggleFull(); return; }
      if (panel.classList.contains("open")) { closePanel(); return; }
      if (nav.classList.contains("open")) closeNav();
    });

    // --- control bar wiring + collapse logic ---
    function syncSegs() {
      ctrl.querySelectorAll(".dp-ai-seg").forEach(function (seg) {
        var axis = seg.getAttribute("data-axis");
        seg.querySelectorAll("button").forEach(function (b) {
          b.classList.toggle("on", b.getAttribute("data-v") === settings[axis]);
        });
      });
      modelSel.value = settings.model || "";
    }
    function refreshHint() {
      if (settings.model) {
        hintEl.innerHTML = "<b>Fixed model:</b> " + escapeHtml(labelFor(settings.model)) +
          " \u2014 the Auto routing is overridden.";
      } else {
        var picked = predictModel(settings);
        hintEl.innerHTML = "<b>Auto \u2192 " + escapeHtml(labelFor(picked)) + "</b> \u00b7 " + escapeHtml(REASONS[picked] || "");
      }
      ctrlSum.textContent =
        (settings.model ? labelFor(settings.model) : "Auto \u2192 " + labelFor(predictModel(settings))) +
        " \u00b7 " + (SHORT_AXIS[settings.length] || settings.length) +
        " \u00b7 " + (SHORT_AXIS[settings.depth] || settings.depth) +
        " \u00b7 " + (SHORT_AXIS[settings.difficulty] || settings.difficulty);
      // the usage strip marks the model that will actually answer, so it has to
      // follow the same settings the hint does
      renderUsage();
    }
    function applyCollapse() {
      ctrl.classList.toggle("collapsed", !!settings.hideControls);
      ctrlToggle.setAttribute("aria-expanded", settings.hideControls ? "false" : "true");
    }

    // --- usage strip: the same "what is left today" view the per-question Ask
    //     AI panel has, but collapsed to a single line so it costs no room ---
    function fmtInt(n) { return Number(n || 0).toLocaleString(); }
    function shortDur(sec) {
      if (!isFinite(sec) || sec < 0) return "";
      var h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60);
      return h ? h + "h " + m + "m" : Math.max(1, m) + "m";
    }
    function usageRow(name, quota, sub, isPick) {
      return '<div class="dp-ai-urow' + (isPick ? " on" : "") + '">' +
        '<div class="top"><span class="nm">' + escapeHtml(name) + '</span>' +
        '<span class="q">' + escapeHtml(quota) + '</span></div>' +
        (sub ? '<span class="sub">' + escapeHtml(sub) + '</span>' : '') +
        '</div>';
    }
    function renderUsage() {
      if (!usageBox) return;
      var auto = settings.model || predictModel(settings);
      var rows = "", sum = "", dot = "dot off";
      if (poolState && poolState.pool && poolState.pool.length) {
        var ag = poolState.aggregate || {};
        var total = poolState.pool.length;
        var avail = ag.availableNow == null
          ? poolState.pool.filter(function (m) { return m.available; }).length
          : ag.availableNow;
        sum = avail + "/" + total + " free · " + fmtInt(ag.rpdRemaining) + " req left today";
        var rs = poolState.resetInSeconds;
        if (isFinite(rs)) sum += " · resets in " + shortDur(rs);
        dot = avail === 0 ? "dot off" : (avail < Math.ceil(total / 2) ? "dot warn" : "dot");
        rows = poolState.pool.map(function (m) {
          var isPick = m.id === auto;
          var caps = m.caps || MODEL_INFO[m.id] || {};
          var sub = (caps.vendor ? caps.vendor + " · " + caps.size : caps.who || "") +
            (caps.bestFor || caps.best ? " — Best for: " + (caps.bestFor || caps.best) : "");
          return usageRow(
            labelFor(m.id) + (isPick ? " ★" : "") + (m.available ? "" : " · capped"),
            (m.remaining === null ? "∞" : fmtInt(m.remaining)) + " req · " +
              (m.tpdRemaining === null ? "∞" : fmtInt(m.tpdRemaining)) + " tok",
            sub,
            isPick
          );
        }).join("");
      } else {
        // No live numbers: fall back to what each model is good at.
        sum = "capabilities only";
        rows = Object.keys(MODEL_LABELS).map(function (id) {
          var info = MODEL_INFO[id] || {};
          return usageRow(labelFor(id), "quota offline", info.best ? info.who + " — Best for: " + info.best : "", id === auto);
        }).join("");
      }
      usageBody.innerHTML = rows +
        '<p class="dp-ai-unote">Requests = how many questions per day; tokens = how long the ' +
        'answers can be. \u201c\u221e\u201d means no cap on that dimension. Quotas reset at 00:00 UTC.</p>';
      usageSum.textContent = sum;
      usageDot.className = dot;
    }
    function applyUsage() {
      if (!usageBox) return;
      usageBox.classList.toggle("open", !!settings.showUsage);
      usageToggle.setAttribute("aria-expanded", settings.showUsage ? "true" : "false");
      sizeUsageBody();
    }
    // The body floats above the strip, so its only limit is the room between the
    // header and the strip — measure that and cap it, or it would cover the title.
    function sizeUsageBody() {
      if (!usageBox || !usageBox.classList.contains("open")) return;
      var pr = panel.getBoundingClientRect();
      var sr = usageBox.getBoundingClientRect();
      var head = panel.querySelector(".dp-ai-head");
      var headH = head ? head.getBoundingClientRect().height : 0;
      var room = Math.floor(sr.top - pr.top - headH - 8);
      usageBody.style.maxHeight = Math.max(64, Math.min(190, room)) + "px";
    }
    usageToggle.addEventListener("click", function () {
      settings.showUsage = !settings.showUsage;
      saveSettings(settings);
      applyUsage();
    });
    window.addEventListener("resize", sizeUsageBody);
    renderUsage();

    ctrlToggle.addEventListener("click", function () {
      settings.hideControls = !settings.hideControls;
      saveSettings(settings);
      applyCollapse();
      sizeUsageBody(); // the control bar just changed height
    });
    ctrl.querySelectorAll(".dp-ai-seg button").forEach(function (b) {
      b.addEventListener("click", function () {
        var axis = b.parentNode.getAttribute("data-axis");
        settings[axis] = b.getAttribute("data-v");
        saveSettings(settings);
        syncSegs();
        refreshHint();
      });
    });
    modelSel.addEventListener("change", function () {
      settings.model = modelSel.value || "";
      saveSettings(settings);
      refreshHint();
    });

    // Model picker + usage strip, both fed by the live status endpoint.
    // The picker is rebuilt each time (never appended twice) so a refresh after
    // every reply cannot duplicate options.
    function applyModelList(list) {
      while (modelSel.options.length > 1) modelSel.removeChild(modelSel.lastChild);
      (list || []).forEach(function (id) {
        if (!id) return;
        var o = document.createElement("option");
        o.value = id;
        o.textContent = labelFor(id);
        modelSel.appendChild(o);
      });
      syncSegs();
      refreshHint();
    }
    function applyStatus(d) {
      if (d && d.configured === false) poolState = null;
      else if (d && Array.isArray(d.pool) && d.pool.length) poolState = d;
      if (poolState) applyModelList(poolState.pool.map(function (m) { return m.id; }));
      else applyModelList(Object.keys(MODEL_LABELS));
      renderUsage();
    }
    function fetchStatus() {
      try {
        fetch(STATUS, { method: "GET", headers: { "content-type": "application/json" } })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (d) { applyStatus(d); })
          .catch(function () { applyStatus(null); });
      } catch (e) { applyStatus(null); }
    }
    fetchStatus();
    syncSegs();
    refreshHint();
    applyCollapse();
    applyUsage();

    function setLoading(on) {
      send.disabled = on;
      text.disabled = on;
      if (on) meta.textContent = "Thinking\u2026";
      else if (!meta.dataset.keep) meta.textContent = "";
    }

    function showTyping() {
      var el = document.createElement("div");
      el.className = "dp-ai-msg bot";
      el.id = "dpAiTyping";
      el.innerHTML = '<span class="dp-ai-typing"><span></span><span></span><span></span></span>';
      msgs.appendChild(el);
      scrollDown();
    }
    function removeTyping() {
      var t = document.getElementById("dpAiTyping");
      if (t) t.parentNode.removeChild(t);
    }

    function autosize() {
      text.style.height = "auto";
      text.style.height = Math.min(text.scrollHeight, 120) + "px";
    }
    text.addEventListener("input", autosize);

    function sendMessage() {
      var val = text.value.trim();
      if (!val) return;
      var userHtml = format(val);
      addMsg("user", userHtml);
      pushHistory("user", userHtml);
      text.value = "";
      autosize();
      setLoading(true);
      showTyping();

      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, 30000);

      var payload = {
        message: val,
        subject: subject || undefined,
        depth: settings.depth,
        difficulty: settings.difficulty,
        length: settings.length
      };
      if (settings.model) payload.model = settings.model;

      fetch(API, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal
      })
        .then(function (r) {
          return r.json().then(function (data) { return { status: r.status, data: data }; });
        })
        .then(function (res) {
          removeTyping();
          var d = res.data || {};
          if (res.status === 200 && d.ok) {
            // Belt and braces: the server splits thinking from the answer, and
            // we split again here, so nothing that is reasoning can ever render
            // as part of the answer.
            var sp = splitInlineThinking(d.answer || "");
            var cleanAnswer = sp.answer || d.answer || "(no answer)";
            var botMeta = { text: cleanAnswer, thinking: d.thinking || sp.thinking || "" };
            var botHtml = format(cleanAnswer);
            addMsg("bot", botHtml, botMeta);
            pushHistory("bot", botHtml, botMeta);
            if (d.intent) {
              meta.textContent = "via " + labelFor(d.model) + " \u00b7 " + d.intent.depth + " \u00b7 " + d.intent.difficulty + " \u00b7 " + d.intent.length;
              meta.title = d.intent.reason || "";
            } else if (d.model) {
              meta.textContent = "via " + labelFor(d.model);
              meta.title = "";
            } else {
              meta.textContent = "";
              meta.title = "";
            }
          } else if (d.error === "rate_limited" || d.error === "quota_exceeded") {
            addMsg("err", format(d.message || "Rate limit reached. Please try again shortly."));
            meta.textContent = "";
            meta.title = "";
          } else {
            addMsg("err", format((d && d.message) || ("Something went wrong (HTTP " + res.status + ").")));
            meta.textContent = "";
            meta.title = "";
          }
        })
        .catch(function (err) {
          removeTyping();
          addMsg("err", format("Could not reach the AI service. Check your connection and try again." + (err && err.name === "AbortError" ? " (timed out)" : "")));
          meta.textContent = "";
          meta.title = "";
        })
        .then(function () {
          clearTimeout(timer);
          setLoading(false);
          text.focus();
          // Every reply spends quota, so re-read the live numbers.
          fetchStatus();
        });
    }

    send.addEventListener("click", sendMessage);
    text.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // first-run hint
    if (history.length === 0) {
      var hint = "Hi \u2014 I'm your AI study assistant. Use the controls just above the box to set how long the reply should be, how hard I should think, and how hard the task is" +
        (subject ? " for " + subject : "") +
        ". Leave Model on Auto and I'll pick the best free model for those choices. Use \u2922 to go full page, or \u2699 to hide the controls. Ask me to explain a concept, work through a problem, or quiz you. Your conversation is saved on this device.";
      addMsg("bot", format(hint));
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
