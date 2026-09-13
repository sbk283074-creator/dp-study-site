/* ============================================================================
 * DP Study Site — global AI Study Assistant widget
 * Loaded on every page of the static site (GitHub Pages).
 * Talks to the Cloudflare Worker /api/ask backend (CORS: *).
 * Self-contained: injects its own styles, no external dependencies.
 *
 * Controls exposed to the student (the "AI control panel"):
 *   Reply length   short | medium | long   -> token budget + length instruction
 *   Thinking depth quick | standard | deep  -> temperature + reasoning instruction
 *   Task difficulty easy | medium | hard    -> which free model is chosen
 *   Model          Auto (best for choices) | any free model
 * The backend maps these onto the best-fit free Groq model so the org's quota
 * is spent where it helps most (reasoning models for hard/deep, unlimited-token
 * models for long answers, high-quota models for many short easy questions).
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

  // Client-side mirror of the backend's model resolver — gives instant "which
  // model will answer" feedback as the student toggles the controls.
  function predictModel(s) {
    var d = s.depth, f = s.difficulty, l = s.length;
    var tier = (f === "hard" || d === "deep") ? 2 : ((f === "easy" && d === "quick") ? 0 : 1);
    if (tier === 2) return "openai/gpt-oss-120b";
    if (tier === 0) return (l === "long") ? "openai/gpt-oss-20b" : "allam-2-7b";
    return (l === "long") ? "groq/compound-mini" : "qwen/qwen3.8-27b";
  }
  function predictReason(s) {
    var d = s.depth, f = s.difficulty, l = s.length;
    var tier = (f === "hard" || d === "deep") ? 2 : ((f === "easy" && d === "quick") ? 0 : 1);
    if (tier === 2) return "Hard task / deep thinking → GPT-OSS 120B, the strongest reasoning model (65K output, 200K tokens/day).";
    if (tier === 0) return (l === "long")
      ? "Easy + quick but a longer answer → GPT-OSS 20B handles the length without spending the reasoning models."
      : "Easy + quick, short answer → Allam 2 7B has the largest request quota (7,000/day) — ideal for many short questions.";
    return (l === "long")
      ? "Standard task, long answer → Compound Mini has unlimited daily tokens, built for detailed explanations."
      : "Standard task → Qwen3.8-27B, the strongest general model on Groq and best for Chinese (200K tokens/day).";
  }

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
      ".dp-ai-panel{position:fixed;right:18px;bottom:78px;z-index:2147483000;width:min(390px,calc(100vw - 36px));",
      "height:min(580px,calc(100vh - 110px));display:none;flex-direction:column;background:#fff;border:1px solid #e3e8f0;",
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
      ".dp-ai-foot{padding:8px 12px;font-size:11px;color:#6c7788;display:flex;justify-content:space-between;align-items:center;border-top:1px solid #eef1f6;background:#fff}",
      ".dp-ai-foot a{color:#3653d6;text-decoration:none;font-weight:600}",
      ".dp-ai-input{display:flex;gap:8px;padding:12px;border-top:1px solid #eef1f6;background:#fff}",
      ".dp-ai-input textarea{flex:1;resize:none;border:1px solid #ccd5e4;border-radius:10px;padding:9px 11px;font:14px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif;outline:none;max-height:120px}",
      ".dp-ai-input textarea:focus{border-color:#3653d6;box-shadow:0 0 0 3px #eef1ff}",
      ".dp-ai-input button{background:#3653d6;color:#fff;border:none;border-radius:10px;padding:0 16px;font-weight:700;cursor:pointer}",
      ".dp-ai-input button:disabled{opacity:.5;cursor:default}",
      ".dp-ai-typing{display:inline-flex;gap:4px;padding:4px 2px}",
      ".dp-ai-typing span{width:6px;height:6px;border-radius:50%;background:#94a0b2;animation:dpai-b 1s infinite ease-in-out}",
      ".dp-ai-typing span:nth-child(2){animation-delay:.15s}.dp-ai-typing span:nth-child(3){animation-delay:.3s}",
      "@keyframes dpai-b{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}",
      // ---- settings sheet ----
      ".dp-ai-set{position:absolute;left:0;right:0;top:53px;bottom:0;background:#fff;display:none;flex-direction:column;padding:14px 16px;overflow-y:auto;z-index:3}",
      ".dp-ai-set.open{display:flex}",
      ".dp-ai-set-h{display:flex;align-items:center;font-weight:700;font-size:14px;margin-bottom:4px}",
      ".dp-ai-set-h button{margin-left:auto;background:#eef1f6;border:none;color:#46506a;width:26px;height:26px;border-radius:8px;cursor:pointer;font-size:15px;line-height:1}",
      ".dp-ai-set-h button:hover{background:#e1e6f2}",
      ".dp-ai-set-sub{font-size:11.5px;color:#8a93a6;margin:0 0 14px;line-height:1.5}",
      ".dp-ai-set-row{margin-bottom:14px}",
      ".dp-ai-set-row>label{display:block;font-size:12px;font-weight:700;color:#46506a;margin-bottom:6px}",
      ".dp-ai-seg{display:flex;gap:4px;background:#eef1f6;border-radius:10px;padding:3px}",
      ".dp-ai-seg button{flex:1;border:none;background:transparent;padding:7px 4px;border-radius:8px;font:600 12px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#5a6577;cursor:pointer;transition:all .12s}",
      ".dp-ai-seg button:hover{color:#3653d6}",
      ".dp-ai-seg button.on{background:#fff;color:#3653d6;box-shadow:0 1px 3px rgba(16,24,40,.14)}",
      "select.dp-ai-sel{width:100%;padding:9px 10px;border:1px solid #ccd5e4;border-radius:10px;font:13px -apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#fff;color:#151923;cursor:pointer}",
      ".dp-ai-set-note{font-size:11.5px;color:#5a6577;background:#f4f6fb;border:1px solid #e6eaf3;border-radius:10px;padding:10px 12px;line-height:1.55}",
      ".dp-ai-set-note b{color:#2a44b8}"
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
          '<button id="dpAiGear" aria-label="AI settings" title="AI settings">⚙</button>' +
          '<button id="dpAiClose" aria-label="Close">×</button>' +
        '</div>' +
        '<div class="dp-ai-msgs" id="dpAiMsgs"></div>' +
        '<div class="dp-ai-set" id="dpAiSet">' +
          '<div class="dp-ai-set-h">AI settings<button id="dpAiSetClose" aria-label="Close settings">×</button></div>' +
          '<p class="dp-ai-set-sub">Tune how the AI answers. These pick the best free model so the answer fits your need and the quota is used well.</p>' +
          '<div class="dp-ai-set-row"><label>Reply length</label>' +
            '<div class="dp-ai-seg" data-axis="length">' +
              '<button data-v="short">Short</button><button data-v="medium">Medium</button><button data-v="long">Long</button>' +
            '</div></div>' +
          '<div class="dp-ai-set-row"><label>Thinking depth</label>' +
            '<div class="dp-ai-seg" data-axis="depth">' +
              '<button data-v="quick">Quick</button><button data-v="standard">Standard</button><button data-v="deep">Deep</button>' +
            '</div></div>' +
          '<div class="dp-ai-set-row"><label>Task difficulty</label>' +
            '<div class="dp-ai-seg" data-axis="difficulty">' +
              '<button data-v="easy">Easy</button><button data-v="medium">Medium</button><button data-v="hard">Hard</button>' +
            '</div></div>' +
          '<div class="dp-ai-set-row"><label>Model</label>' +
            '<select class="dp-ai-sel" id="dpAiModel"><option value="">Auto (best for your choices)</option></select>' +
          '</div>' +
          '<div class="dp-ai-set-note" id="dpAiReason"></div>' +
        '</div>' +
        '<div class="dp-ai-input">' +
          '<textarea id="dpAiText" rows="1" placeholder="Ask anything about ' + (subject || "your IB subjects") + '…"></textarea>' +
          '<button id="dpAiSend">Send</button>' +
        '</div>' +
        '<div class="dp-ai-foot"><span id="dpAiMeta"></span><a href="' + HUB + '" target="_blank" rel="noopener">⌂ Hub</a></div>' +
      '</div>';
    document.body.appendChild(root);

    var btn = document.getElementById("dpAiBtn");
    var panel = document.getElementById("dpAiPanel");
    var msgs = document.getElementById("dpAiMsgs");
    var text = document.getElementById("dpAiText");
    var send = document.getElementById("dpAiSend");
    var meta = document.getElementById("dpAiMeta");
    var closeBtn = document.getElementById("dpAiClose");
    var gearBtn = document.getElementById("dpAiGear");
    var setEl = document.getElementById("dpAiSet");
    var setClose = document.getElementById("dpAiSetClose");
    var modelSel = document.getElementById("dpAiModel");
    var reasonEl = document.getElementById("dpAiReason");

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
      setEl.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
    }
    function openSettings() { setEl.classList.add("open"); refreshReason(); }
    function closeSettings() { setEl.classList.remove("open"); }

    btn.addEventListener("click", function () {
      if (panel.classList.contains("open")) closePanel(); else openPanel();
    });
    closeBtn.addEventListener("click", closePanel);
    gearBtn.addEventListener("click", function (e) { e.stopPropagation(); openSettings(); });
    setClose.addEventListener("click", closeSettings);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.classList.contains("open")) { if (setEl.classList.contains("open")) closeSettings(); else closePanel(); }
    });

    // --- settings controls ---
    function syncSegs() {
      var segs = setEl.querySelectorAll(".dp-ai-seg");
      segs.forEach(function (seg) {
        var axis = seg.getAttribute("data-axis");
        seg.querySelectorAll("button").forEach(function (b) {
          b.classList.toggle("on", b.getAttribute("data-v") === settings[axis]);
        });
      });
      modelSel.value = settings.model || "";
    }
    function refreshReason() {
      var m = settings.model;
      if (m) {
        reasonEl.innerHTML = "<b>Fixed model:</b> " + escapeHtml(MODEL_LABELS[m] || m) +
          ". The Auto routing below is overridden.";
        return;
      }
      var picked = predictModel(settings);
      reasonEl.innerHTML = "<b>Will use:</b> " + escapeHtml(MODEL_LABELS[picked] || picked) +
        ".<br>" + escapeHtml(predictReason(settings));
    }
    setEl.querySelectorAll(".dp-ai-seg button").forEach(function (b) {
      b.addEventListener("click", function () {
        var axis = b.parentNode.getAttribute("data-axis");
        settings[axis] = b.getAttribute("data-v");
        saveSettings(settings);
        syncSegs();
        refreshReason();
      });
    });
    modelSel.addEventListener("change", function () {
      settings.model = modelSel.value || "";
      saveSettings(settings);
      refreshReason();
    });

    // populate model picker from the live status endpoint (fallback to known pool)
    function fillModels() {
      var ids = Object.keys(MODEL_LABELS);
      try {
        fetch(STATUS, { method: "GET", headers: { "content-type": "application/json" } })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (d) {
            if (d && Array.isArray(d.pool) && d.pool.length) {
              ids = d.pool.map(function (m) { return m.id; });
            }
            ids.forEach(function (id) {
              var o = document.createElement("option");
              o.value = id;
              o.textContent = MODEL_LABELS[id] || id;
              modelSel.appendChild(o);
            });
            syncSegs();
          })
          .catch(function () { syncSegs(); });
      } catch (e) { syncSegs(); }
    }
    fillModels();
    syncSegs();
    refreshReason();

    function setLoading(on) {
      send.disabled = on;
      text.disabled = on;
      if (on) meta.textContent = "Thinking…";
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
        body: JSON.stringify(payload)
      }, { signal: controller.signal })
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
              var lbl = MODEL_LABELS[d.model] || d.model || "AI";
              meta.textContent = "via " + lbl + " · " + d.intent.depth + " · " + d.intent.difficulty + " · " + d.intent.length;
              meta.title = d.intent.reason || "";
            } else if (d.model) {
              meta.textContent = "via " + (MODEL_LABELS[d.model] || d.model);
              meta.title = "";
            } else {
              meta.textContent = "";
              meta.title = "";
            }
          } else if (d.error === "rate_limited" || d.error === "quota_exceeded") {
            var eh = format(d.message || "Rate limit reached. Please try again shortly.");
            addMsg("err", eh);
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
      var hint = "Hi — I'm your AI study assistant. Tap ⚙ to set reply length, thinking depth and task difficulty" +
        (subject ? " for " + subject : "") +
        ", then ask me to explain a concept, work through a problem, or quiz you. Your conversation is saved on this device.";
      addMsg("bot", format(hint));
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
