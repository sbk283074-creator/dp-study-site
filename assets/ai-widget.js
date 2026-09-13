/* ============================================================================
 * DP Study Site — global AI Study Assistant widget
 * Loaded on every page of the static site (GitHub Pages).
 * Talks to the Cloudflare Worker /api/ask backend (CORS: *).
 * Self-contained: injects its own styles, no external dependencies.
 *
 * The control bar sits directly on top of the input bar and is ALWAYS visible,
 * so the student can find and change it on every single question:
 *
 *   Reply length    short | medium | long     -> token budget + length instruction
 *   Thinking depth  quick | standard | deep   -> temperature + reasoning instruction
 *   Task difficulty easy  | medium   | hard   -> model quality tier
 *   Model           Auto (best fit) | any free model  (explicit Auto option)
 *
 * "Auto" weighs three indexes — how LONG the answer must be, how COMPLEX the
 * task is, and how SCARCE or ABUNDANT each model's quota is — to spend the
 * org's free Groq quota where it helps most:
 *   - token-rich / request-poor models (Compound: 250 req/day, unlimited tokens)
 *       -> long answers and the most complex tasks
 *   - request-rich / token-poor models (Allam: 7,000 req/day, 6K tok/min)
 *       -> many short, simple questions
 *   - balanced models (GPT-OSS 120B / Qwen3.8-27B: 1,000 req/day, 200K tok/day)
 *       -> the everyday middle
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

  function defaultSettings() {
    return { depth: "standard", difficulty: "medium", length: "medium", model: "" };
  }
  function loadSettings() {
    try {
      var s = JSON.parse(localStorage.getItem(LS_SET) || "{}");
      var d = defaultSettings();
      return {
        depth: s.depth || d.depth,
        difficulty: s.difficulty || d.difficulty,
        length: s.length || d.length,
        model: s.model || d.model
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

  function build() {
    if (document.getElementById("dp-ai-root")) return;

    var subject = inferSubject();
    var settings = loadSettings();

    var styles = [
      ".dp-ai-btn{position:fixed;right:18px;bottom:18px;z-index:2147483000;",
      "display:flex;align-items:center;gap:8px;padding:12px 16px;border:none;border-radius:999px;",
      "background:#3653d6;background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff;font:600 14px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;",
      "cursor:pointer;box-shadow:0 6px 20px rgba(54,83,214,.35);transition:transform .15s ease,box-shadow .15s ease}",
      ".dp-ai-btn:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(54,83,214,.45)}",
      ".dp-ai-btn__dot{width:8px;height:8px;border-radius:50%;background:#9affc4;box-shadow:0 0 0 3px rgba(154,255,196,.25)}",
      ".dp-ai-panel{position:fixed;right:18px;bottom:78px;z-index:2147483000;width:min(400px,calc(100vw - 36px));",
      "height:min(640px,calc(100vh - 96px));display:none;flex-direction:column;background:#fff;border:1px solid #e3e8f0;",
      "border-radius:16px;overflow:hidden;box-shadow:0 18px 50px rgba(16,24,40,.18);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#151923}",
      ".dp-ai-panel.open{display:flex}",
      ".dp-ai-head{display:flex;align-items:center;gap:8px;padding:14px 14px;background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff}",
      ".dp-ai-head h3{margin:0;font-size:15px;font-weight:700;flex:1}",
      ".dp-ai-head .chip{font-size:11px;font-weight:600;background:rgba(255,255,255,.18);padding:3px 8px;border-radius:999px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px}",
      ".dp-ai-head button{background:rgba(255,255,255,.15);border:none;color:#fff;width:28px;height:28px;border-radius:8px;cursor:pointer;font-size:15px;line-height:1}",
      ".dp-ai-head button:hover{background:rgba(255,255,255,.28)}",
      ".dp-ai-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:#fafbfd}",
      ".dp-ai-msg{max-width:88%;padding:10px 13px;border-radius:12px;font-size:14px;line-height:1.55;word-wrap:break-word}",
      ".dp-ai-msg p{margin:0 0 8px}.dp-ai-msg p:last-child{margin:0}",
      ".dp-ai-msg code{background:#eef1ff;padding:1px 5px;border-radius:5px;font-size:12.5px}",
      ".dp-ai-msg.user{align-self:flex-end;background:#3653d6;color:#fff;border-bottom-right-radius:4px}",
      ".dp-ai-msg.bot{align-self:flex-start;background:#fff;border:1px solid #e3e8f0;border-bottom-left-radius:4px}",
      ".dp-ai-msg.bot strong{color:#2a44b8}",
      ".dp-ai-msg.err{align-self:flex-start;background:#fdeceb;color:#b02a1f;border:1px solid #f5c4bf;border-bottom-left-radius:4px}",
      // ---- always-visible control bar, attached to the input ----
      ".dp-ai-ctrl{padding:10px 12px 8px;border-top:1px solid #eef1f6;background:#fff}",
      ".dp-ai-ctrl-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}",
      ".dp-ai-ctrl-lab{flex:0 0 46px;font-size:10px;font-weight:700;color:#7a8398;text-transform:uppercase;letter-spacing:.04em}",
      ".dp-ai-seg{flex:1;display:flex;gap:3px;background:#eef1f6;border-radius:9px;padding:3px}",
      ".dp-ai-seg button{flex:1;border:none;background:transparent;padding:6px 2px;border-radius:7px;font:600 11.5px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#5a6577;cursor:pointer;transition:all .12s}",
      ".dp-ai-seg button:hover{color:#3653d6}",
      ".dp-ai-seg button.on{background:#fff;color:#3653d6;box-shadow:0 1px 3px rgba(16,24,40,.14)}",
      "select.dp-ai-sel{flex:1;padding:7px 9px;border:1px solid #ccd5e4;border-radius:9px;font:600 12px -apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#fff;color:#151923;cursor:pointer}",
      ".dp-ai-hint{font-size:11px;color:#5a6577;background:#f4f6fb;border:1px solid #e6eaf3;border-radius:8px;padding:6px 9px;line-height:1.45;margin-top:2px}",
      ".dp-ai-hint b{color:#2a44b8}",
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
      "@keyframes dpai-b{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}"
    ].join("");

    var styleEl = document.createElement("style");
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);

    var root = document.createElement("div");
    root.id = "dp-ai-root";
    root.innerHTML =
      '<button class="dp-ai-btn" id="dpAiBtn" aria-label="Open AI study assistant">' +
        '<span class="dp-ai-btn__dot"></span><span>Ask AI</span>' +
      '</button>' +
      '<div class="dp-ai-panel" id="dpAiPanel" role="dialog" aria-label="AI study assistant">' +
        '<div class="dp-ai-head">' +
          '<h3>AI Study Assistant</h3>' +
          (subject ? '<span class="chip" id="dpAiSubj">' + escapeHtml(subject) + '</span>' : '') +
          '<button id="dpAiClose" aria-label="Close">\u00d7</button>' +
        '</div>' +
        '<div class="dp-ai-msgs" id="dpAiMsgs"></div>' +
        '<div class="dp-ai-ctrl">' +
          segRow("length", "Length", [{ v: "short", t: "Short" }, { v: "medium", t: "Medium" }, { v: "long", t: "Long" }]) +
          segRow("depth", "Think", [{ v: "quick", t: "Quick" }, { v: "standard", t: "Standard" }, { v: "deep", t: "Deep" }]) +
          segRow("difficulty", "Task", [{ v: "easy", t: "Easy" }, { v: "medium", t: "Medium" }, { v: "hard", t: "Hard" }]) +
          '<div class="dp-ai-ctrl-row">' +
            '<span class="dp-ai-ctrl-lab">Model</span>' +
            '<select class="dp-ai-sel" id="dpAiModel"><option value="">Auto \u2014 best fit for my choices</option></select>' +
          '</div>' +
          '<div class="dp-ai-hint" id="dpAiHint"></div>' +
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
    var ctrl = root.querySelector(".dp-ai-ctrl");
    var modelSel = document.getElementById("dpAiModel");
    var hintEl = document.getElementById("dpAiHint");

    function scrollDown() { msgs.scrollTop = msgs.scrollHeight; }

    function addMsg(role, html) {
      var el = document.createElement("div");
      el.className = "dp-ai-msg " + role;
      el.innerHTML = html;
      msgs.appendChild(el);
      scrollDown();
      return el;
    }

    // restore history
    var history = loadHistory();
    history.forEach(function (m) { addMsg(m.role, m.html); });

    function pushHistory(role, html) {
      history.push({ role: role, html: html });
      saveHistory(history);
    }

    function openPanel() {
      panel.classList.add("open");
      btn.setAttribute("aria-expanded", "true");
      text.focus();
    }
    function closePanel() {
      panel.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
    }

    btn.addEventListener("click", function () {
      if (panel.classList.contains("open")) closePanel(); else openPanel();
    });
    closeBtn.addEventListener("click", closePanel);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.classList.contains("open")) closePanel();
    });

    // --- control bar wiring ---
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
        return;
      }
      var picked = predictModel(settings);
      hintEl.innerHTML = "<b>Auto \u2192 " + escapeHtml(labelFor(picked)) + "</b> \u00b7 " + escapeHtml(REASONS[picked] || "");
    }
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

    // populate model picker from the live status endpoint (fallback to known pool)
    function fillModels() {
      var ids = Object.keys(MODEL_LABELS);
      function apply(list) {
        list.forEach(function (id) {
          if (!id) return;
          var o = document.createElement("option");
          o.value = id;
          o.textContent = labelFor(id);
          modelSel.appendChild(o);
        });
        syncSegs();
        refreshHint();
      }
      try {
        fetch(STATUS, { method: "GET", headers: { "content-type": "application/json" } })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (d) {
            var list = (d && Array.isArray(d.pool) && d.pool.length)
              ? d.pool.map(function (m) { return m.id; })
              : ids;
            apply(list);
          })
          .catch(function () { apply(ids); });
      } catch (e) { apply(ids); }
    }
    fillModels();
    syncSegs();
    refreshHint();

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
            var botHtml = format(d.answer || "(no answer)");
            addMsg("bot", botHtml);
            pushHistory("bot", botHtml);
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
        .then(function () { clearTimeout(timer); setLoading(false); text.focus(); });
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
        ". Leave Model on Auto and I'll pick the best free model for those choices. Ask me to explain a concept, work through a problem, or quiz you. Your conversation is saved on this device.";
      addMsg("bot", format(hint));
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
