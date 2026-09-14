/* ============================================================================
 * DP Study Site — global Formula Booklet + Scientific Calculator
 * Loaded on every page of the static site (GitHub Pages) from an absolute URL,
 * injected by assets/ai-widget.js. Self-contained: own styles, own launch
 * buttons and panels, no external dependencies, no MathJax needed.
 *
 * TWO FLOATING BARS
 *   1. FORMULA BOOKLET  — a compact, searchable reference of the IB DP
 *      Mathematics AA and Physics data-booklet essentials. Rendered with plain
 *      HTML (fractions / roots / sub-sup) so it looks identical on every page,
 *      even where MathJax is not loaded.
 *   2. SCIENTIFIC CALCULATOR — a real evaluator (shunting-yard → RPN) with
 *      sin/cos/tan (deg & rad), ln/log, √, powers, π, parentheses, Ans memory.
 * ==========================================================================*/
(function () {
  "use strict";

  if (window.__dpToolsLoaded) return;
  window.__dpToolsLoaded = true;

  // --- small HTML helpers for nicely-set formulas (no MathJax needed) --------
  function frac(n, d) {
    return '<span class="fb-frac"><span class="fb-n">' + n + '</span><span class="fb-d">' + d + '</span></span>';
  }
  function root(x) { return '<span class="fb-rad">' + x + '</span>'; }
  function sup(x) { return '<sup>' + x + '</sup>'; }
  function sub(x) { return '<sub>' + x + '</sub>'; }

  // ---- formula booklet content ----------------------------------------------
  // Each item: { t: title, f: formula HTML, k: extra keywords for search }
  var FORMULAS = {
    "Mathematics AA HL": [
      { t: "Quadratic formula", f: "x = " + frac("−b ± " + root("b" + sup("2") + " − 4ac"), "2a"), k: "quadratic equation roots solve" },
      { t: "Discriminant", f: "Δ = b" + sup("2") + " − 4ac", k: "discriminant nature of roots" },
      { t: "Sine rule", f: frac("a", "sin A") + " = " + frac("b", "sin B") + " = " + frac("c", "sin C"), k: "sine rule triangle" },
      { t: "Cosine rule", f: "c" + sup("2") + " = a" + sup("2") + " + b" + sup("2") + " − 2ab cos C", k: "cosine rule triangle side angle" },
      { t: "Area of a triangle", f: frac("1", "2") + "ab sin C", k: "area triangle" },
      { t: "Logarithm — change of base", f: "log" + sub("a") + "b = " + frac("log b", "log a"), k: "log logarithm base" },
      { t: "Derivative of a power", f: frac("d", "dx") + "(x" + sup("n") + ") = n x" + sup("n−1"), k: "differentiate derivative power calculus" },
      { t: "Integral of a power", f: "∫ x" + sup("n") + " dx = " + frac("x" + sup("n+1"), "n+1") + " + C", k: "integrate integral calculus power" },
      { t: "Trigonometric identity", f: "sin" + sup("2") + "θ + cos" + sup("2") + "θ = 1", k: "trig identity pythagorean" },
      { t: "Arc length & sector area", f: "s = rθ &nbsp;·&nbsp; A = " + frac("1", "2") + "r" + sup("2") + "θ", k: "arc length sector angle radians" },
      { t: "Binomial expansion", f: "(a+b)" + sup("n") + " = Σ " + frac("n!", "r!(n−r)!") + " a" + sup("n−r") + "b" + sup("r"), k: "binomial expansion combination" },
      { t: "Probability — union", f: "P(A∪B) = P(A) + P(B) − P(A∩B)", k: "probability union intersection" },
      { t: "Conditional probability", f: "P(A|B) = " + frac("P(A∩B)", "P(B)"), k: "conditional probability bayes" }
    ],
    "Physics HL": [
      { t: "Constant acceleration (SUVAT)", f: "v = u + at &nbsp;·&nbsp; s = ut + " + frac("1", "2") + "at" + sup("2"), k: "suvat kinematics acceleration velocity" },
      { t: "Velocity–displacement", f: "v" + sup("2") + " = u" + sup("2") + " + 2as", k: "suvat velocity displacement" },
      { t: "Newton's second law", f: "F = ma", k: "newton force mass acceleration" },
      { t: "Weight", f: "W = mg", k: "weight gravity mass" },
      { t: "Momentum & impulse", f: "p = mv &nbsp;·&nbsp; F = " + frac("Δp", "Δt"), k: "momentum impulse collision" },
      { t: "Kinetic & gravitational PE", f: "E" + sub("k") + " = " + frac("1", "2") + "mv" + sup("2") + " &nbsp;·&nbsp; E" + sub("p") + " = mgh", k: "kinetic potential energy work" },
      { t: "Power", f: "P = " + frac("W", "t") + " = Fv", k: "power work rate" },
      { t: "Circular motion", f: "a = " + frac("v" + sup("2"), "r") + " = ω" + sup("2") + "r &nbsp;·&nbsp; F = " + frac("mv" + sup("2"), "r"), k: "circular motion centripetal force angular" },
      { t: "Newton's law of gravitation", f: "F = " + frac("G m" + sub("1") + "m" + sub("2"), "r" + sup("2")), k: "gravitation newton field" },
      { t: "Electric field & potential", f: "E = " + frac("F", "q") + " &nbsp;·&nbsp; V = " + frac("W", "q") + " &nbsp;·&nbsp; E = " + frac("V", "d"), k: "electric field potential voltage" },
      { t: "Electrical power", f: "P = VI = I" + sup("2") + "R = " + frac("V" + sup("2"), "R"), k: "power electric resistance ohm" },
      { t: "Resistivity", f: "R = " + frac("ρL", "A"), k: "resistivity resistance wire" },
      { t: "Snell's law (refraction)", f: "n" + sub("1") + " sin θ" + sub("1") + " = n" + sub("2") + " sin θ" + sub("2"), k: "snell refraction index light" },
      { t: "Wave speed", f: "v = fλ", k: "wave speed frequency wavelength" },
      { t: "Ideal gas", f: "pV = nRT", k: "ideal gas pressure volume temperature" },
      { t: "Thermal energy", f: "Q = mcΔT &nbsp;·&nbsp; ΔE = Q − W", k: "thermal heat specific capacity internal energy" },
      { t: "Mass–energy & photon", f: "E = mc" + sup("2") + " &nbsp;·&nbsp; E = hf = " + frac("hc", "λ") + " &nbsp;·&nbsp; hf = Φ + E" + sub("k"), k: "mass energy photon photoelectric planck" }
    ]
  };

  // ---- scientific calculator: tokenizer + shunting-yard + RPN evaluator ------
  function norm(s) {
    return String(s)
      .replace(/×/g, "*").replace(/÷/g, "/")
      .replace(/π/g, "pi").replace(/−/g, "-")
      .replace(/√/g, "sqrt").replace(/Ans/g, String(ANS === null ? 0 : ANS));
  }
  var ANS = null;
  function calcEval(expr, deg) {
    var s = norm(expr).replace(/\s+/g, "");
    if (!s) throw new Error("empty");
    var tokens = [], i = 0;
    while (i < s.length) {
      var c = s[i];
      if ((c >= "0" && c <= "9") || c === ".") {
        var j = i + 1;
        while (j < s.length && ((s[j] >= "0" && s[j] <= "9") || s[j] === ".")) j++;
        tokens.push({ t: "num", v: parseFloat(s.slice(i, j)) }); i = j;
      } else if (/[a-zA-Z]/.test(c)) {
        var k = i + 1;
        while (k < s.length && /[a-zA-Z]/.test(s[k])) k++;
        var name = s.slice(i, k).toLowerCase();
        if (name === "pi") tokens.push({ t: "num", v: Math.PI });
        else tokens.push({ t: "name", v: name });
        i = k;
      } else if ("+-*/^%()".indexOf(c) >= 0) {
        tokens.push({ t: "op", v: c }); i++;
      } else throw new Error("bad char " + c);
    }
    // Unary minus/plus gets its own tier: tighter than * (2 * -3 = 2·(-3)) but
    // looser than ^ (-2^2 = -(2^2)), matching the standard math convention.
    var prec = { "+": 2, "-": 2, "*": 3, "/": 3, "%": 3, "^": 5, "-u": 4, "+u": 4 };
    var right = { "^": true };
    var out = [], ops = [], prev = null;
    function isUnary(tk) {
      if (prev === null) return true;
      if (prev.t === "num") return false;
      if (prev.t === "op" && prev.v === ")") return false;
      return true; // after "(" or any other operator / function name
    }
    for (var n = 0; n < tokens.length; n++) {
      var tk = tokens[n];
      if (tk.t === "num") out.push(tk);
      else if (tk.t === "name") ops.push(tk);
      else if (tk.v === "(") ops.push(tk);
      else if (tk.v === ")") {
        while (ops.length && ops[ops.length - 1].v !== "(") out.push(ops.pop());
        if (!ops.length) throw new Error("mismatch");
        ops.pop();
        if (ops.length && ops[ops.length - 1].t === "name") out.push(ops.pop());
      } else {
        var unary = isUnary(tk);
        if (unary) {
          // A prefix unary operator starts a new primary expression; it must NOT
          // run the precedence-pop loop, or it would pop an operator before that
          // operator has received its right operand (e.g. 2^-3). Just push it.
          ops.push({ t: "op", v: tk.v + "u" });
        } else {
          while (ops.length) {
            var top = ops[ops.length - 1];
            if (top.t === "op" && top.v !== "(") {
              var p1 = prec[tk.v], p2 = prec[top.v];
              if (p2 > p1 || (p2 === p1 && !right[tk.v])) { out.push(ops.pop()); continue; }
            }
            break;
          }
          ops.push(tk);
        }
      }
      prev = tk;
    }
    while (ops.length) {
      var o = ops.pop();
      if (o.v === "(" || o.v === ")") throw new Error("mismatch");
      out.push(o);
    }
    var st = [];
    for (var m = 0; m < out.length; m++) {
      var t = out[m];
      if (t.t === "num") st.push(t.v);
      else if (t.v === "+") { var b = st.pop(), a = st.pop(); st.push(a + b); }
      else if (t.v === "-") { var b2 = st.pop(), a2 = st.pop(); st.push(a2 - b2); }
      else if (t.v === "*") { var b3 = st.pop(), a3 = st.pop(); st.push(a3 * b3); }
      else if (t.v === "/") { var b4 = st.pop(), a4 = st.pop(); st.push(a4 / b4); }
      else if (t.v === "%") { var b5 = st.pop(), a5 = st.pop(); st.push(a5 % b5); }
      else if (t.v === "^") { var b6 = st.pop(), a6 = st.pop(); st.push(Math.pow(a6, b6)); }
      else if (t.v === "-u") st.push(-st.pop());
      else if (t.v === "+u") { /* no-op */ }
      else if (t.t === "name") {
        var fn = t.v, x = st.pop(), r;
        var ang = deg ? x * Math.PI / 180 : x;
        switch (fn) {
          case "sin": r = Math.sin(ang); break;
          case "cos": r = Math.cos(ang); break;
          case "tan": r = Math.tan(ang); break;
          case "asin": r = deg ? Math.asin(x) * 180 / Math.PI : Math.asin(x); break;
          case "acos": r = deg ? Math.acos(x) * 180 / Math.PI : Math.acos(x); break;
          case "atan": r = deg ? Math.atan(x) * 180 / Math.PI : Math.atan(x); break;
          case "ln": r = Math.log(x); break;
          case "log": r = Math.log10(x); break;
          case "sqrt": r = Math.sqrt(x); break;
          case "cbrt": r = Math.cbrt(x); break;
          case "exp": r = Math.exp(x); break;
          case "abs": r = Math.abs(x); break;
          case "sinh": r = Math.sinh(x); break;
          case "cosh": r = Math.cosh(x); break;
          case "tanh": r = Math.tanh(x); break;
          default: throw new Error("unknown " + fn);
        }
        st.push(r);
      }
    }
    if (st.length !== 1) throw new Error("syntax");
    return st[0];
  }
  function fmtNum(r) {
    if (typeof r !== "number") return "Error";
    if (!isFinite(r)) return r > 0 ? "∞" : (r < 0 ? "−∞" : "Error");
    if (Number.isInteger(r)) return String(r);
    var s = r.toPrecision(12).replace(/\.?0+$/, "");
    return s;
  }

  // ---- build the DOM --------------------------------------------------------
  if (document.getElementById("dp-tools-root")) return;
  var styles = [
    // launch cluster sits just above the AI cluster (bottom:18) so the two rows
    // never overlap; it is hidden behind the AI panel when that is open.
    ".dp-tools-launch{position:fixed;right:18px;bottom:80px;z-index:2147483000;display:flex;align-items:center;gap:10px}",
    ".dp-tools-btn{display:flex;align-items:center;gap:7px;padding:11px 14px;border:1px solid #d8dfeb;border-radius:999px;",
    "background:#fff;color:#334155;font:600 13px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;",
    "box-shadow:0 4px 14px rgba(16,24,40,.12);transition:transform .15s ease,border-color .15s ease,color .15s ease}",
    ".dp-tools-btn:hover{transform:translateY(-2px);border-color:#3653d6;color:#3653d6}",
    ".dp-tools-btn .ic{font-size:14px;line-height:1}",
    // shared panel chrome
    ".dp-tools-panel{position:fixed;right:18px;bottom:78px;z-index:2147483002;width:min(420px,calc(100vw - 36px));",
    "height:min(620px,calc(100vh - 96px));display:none;flex-direction:column;background:#fff;border:1px solid #e3e8f0;",
    "border-radius:16px;overflow:hidden;box-shadow:0 18px 50px rgba(16,24,40,.18);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#151923}",
    ".dp-tools-panel.open{display:flex}",
    ".dp-tools-head{display:flex;align-items:center;gap:8px;padding:13px 14px;background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff}",
    ".dp-tools-head h3{margin:0;font-size:15px;font-weight:700;flex:1}",
    ".dp-tools-head .tg{margin-left:auto;display:flex;gap:6px;align-items:center}",
    ".dp-tools-head button{background:rgba(255,255,255,.15);border:none;color:#fff;min-width:28px;height:28px;border-radius:8px;cursor:pointer;font-size:13px;line-height:1;padding:0 8px}",
    ".dp-tools-head button:hover{background:rgba(255,255,255,.28)}",
    ".dp-tools-head .seg{display:flex;gap:0;background:rgba(255,255,255,.15);border-radius:8px;overflow:hidden}",
    ".dp-tools-head .seg button{border-radius:0;background:transparent;min-width:auto;padding:0 10px;height:28px;font-weight:600}",
    ".dp-tools-head .seg button.on{background:rgba(255,255,255,.32)}",
    // ---- formula booklet ----
    ".dp-fb-search{display:block;width:100%;box-sizing:border-box;padding:9px 12px;border:none;border-bottom:1px solid #eef1f6;font:14px -apple-system,Segoe UI,Roboto,Arial,sans-serif;outline:none}",
    ".dp-fb-search:focus{border-bottom-color:#3653d6}",
    ".dp-fb-body{flex:1;min-height:0;overflow-y:auto;padding:10px 12px 16px;background:#fafbfd}",
    ".dp-fb-group-lab{display:block;font-size:10px;font-weight:800;color:#8b93a7;text-transform:uppercase;letter-spacing:.06em;margin:12px 2px 6px}",
    ".dp-fb-item{border:1px solid #e6eaf3;border-radius:10px;background:#fff;margin-bottom:7px;overflow:hidden}",
    ".dp-fb-item .t{font-size:11.5px;font-weight:700;color:#3653d6;padding:6px 11px 0}",
    ".dp-fb-item .f{padding:4px 11px 10px;font-size:15px;line-height:1.7;color:#1d2436;text-align:center}",
    ".dp-fb-empty{color:#8b93a7;font-size:13px;text-align:center;padding:30px 10px}",
    // formula typesetting helpers
    ".fb-frac{display:inline-flex;flex-direction:column;text-align:center;vertical-align:middle;margin:0 .12em;line-height:1.05}",
    ".fb-frac .fb-n{display:block;padding:0 .4em}",
    ".fb-frac .fb-d{display:block;padding:0 .4em;border-top:1.5px solid currentColor}",
    ".fb-rad{display:inline-block;border-top:1.5px solid currentColor;padding:0 .28em;margin-left:.08em;vertical-align:middle}",
    // ---- calculator ----
    ".dp-cal-body{flex:1;min-height:0;display:flex;flex-direction:column;padding:12px;background:#fafbfd}",
    ".dp-cal-res{text-align:right;font-size:13px;color:#6c7788;min-height:18px;padding:0 4px;word-break:break-all}",
    ".dp-cal-expr{width:100%;box-sizing:border-box;text-align:right;font:600 22px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;",
    "border:1px solid #ccd5e4;border-radius:10px;padding:8px 12px;margin:6px 0 10px;outline:none;color:#151923;background:#fff}",
    ".dp-cal-expr:focus{border-color:#3653d6;box-shadow:0 0 0 3px #eef1ff}",
    ".dp-cal-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;flex:1}",
    ".dp-cal-grid button{border:1px solid #d8dfeb;background:#fff;color:#151923;border-radius:10px;font:600 15px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;padding:10px 0;transition:background .1s,border-color .1s}",
    ".dp-cal-grid button:hover{background:#f1f4fb;border-color:#3653d6}",
    ".dp-cal-grid button:active{background:#e6ecfb}",
    ".dp-cal-grid button.op{background:#eef1ff;color:#2a44b8;border-color:#dbe2ff}",
    ".dp-cal-grid button.fn{background:#f3f6fb;color:#334155}",
    ".dp-cal-grid button.eq{background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff;border-color:transparent}",
    ".dp-cal-grid button.util{background:#fff;color:#b02a1f}",
    ".dp-cal-note{font-size:10.5px;color:#8b93a7;text-align:center;margin-top:8px;line-height:1.4}"
  ].join("");

  var styleEl = document.createElement("style");
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);

  var root = document.createElement("div");
  root.id = "dp-tools-root";
  root.innerHTML =
    '<div class="dp-tools-launch">' +
      '<button class="dp-tools-btn" id="dpFbBtn" aria-label="Open formula booklet" aria-expanded="false">' +
        '<span class="ic">\u{1F4D8}</span><span>Formula</span>' +
      '</button>' +
      '<button class="dp-tools-btn" id="dpCalBtn" aria-label="Open calculator" aria-expanded="false">' +
        '<span class="ic">\u{1F9EE}</span><span>Calc</span>' +
      '</button>' +
    '</div>' +

    // --- formula booklet panel ---
    '<div class="dp-tools-panel" id="dpFbPanel" role="dialog" aria-label="Formula booklet">' +
      '<div class="dp-tools-head">' +
        '<h3>Formula Booklet</h3>' +
        '<div class="tg"><div class="seg" id="dpFbSeg">' +
          '<button type="button" data-cat="Mathematics AA HL" class="on">Math</button>' +
          '<button type="button" data-cat="Physics HL">Physics</button>' +
        '</div><button id="dpFbClose" aria-label="Close">\u00d7</button></div>' +
      '</div>' +
      '<input class="dp-fb-search" id="dpFbSearch" type="text" placeholder="Search formulas\u2026" aria-label="Search formulas">' +
      '<div class="dp-fb-body" id="dpFbBody"></div>' +
    '</div>' +

    // --- calculator panel ---
    '<div class="dp-tools-panel" id="dpCalPanel" role="dialog" aria-label="Scientific calculator">' +
      '<div class="dp-tools-head">' +
        '<h3>Calculator</h3>' +
        '<div class="tg"><div class="seg" id="dpCalMode">' +
          '<button type="button" data-deg="1" class="on">DEG</button>' +
          '<button type="button" data-deg="0">RAD</button>' +
        '</div><button id="dpCalClose" aria-label="Close">\u00d7</button></div>' +
      '</div>' +
      '<div class="dp-cal-body">' +
        '<div class="dp-cal-res" id="dpCalRes"></div>' +
        '<input class="dp-cal-expr" id="dpCalExpr" type="text" inputmode="text" placeholder="0" aria-label="Calculator expression" autocomplete="off">' +
        '<div class="dp-cal-grid" id="dpCalGrid"></div>' +
        '<div class="dp-cal-note">Type or tap. Functions need ( ). Ans recalls the last result. = evaluates.</div>' +
      '</div>' +
    '</div>';
  document.body.appendChild(root);

  // ---- formula booklet logic ----
  var fbBtn = document.getElementById("dpFbBtn");
  var fbPanel = document.getElementById("dpFbPanel");
  var fbBody = document.getElementById("dpFbBody");
  var fbSearch = document.getElementById("dpFbSearch");
  var fbSeg = document.getElementById("dpFbSeg");
  var fbClose = document.getElementById("dpFbClose");
  var fbCat = "Mathematics AA HL";

  function renderFormulas() {
    var q = fbSearch.value.trim().toLowerCase();
    var items = FORMULAS[fbCat];
    var html = '<div class="dp-fb-group-lab">' + fbCat + '</div>';
    var shown = 0;
    items.forEach(function (it) {
      if (q && (it.t + " " + it.k).toLowerCase().indexOf(q) === -1) return;
      shown++;
      html += '<div class="dp-fb-item"><div class="t">' + it.t + '</div><div class="f">' + it.f + '</div></div>';
    });
    if (!shown) html = '<div class="dp-fb-empty">No formulas match \u201c' + q + '\u201d.</div>';
    fbBody.innerHTML = html;
  }
  fbSeg.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-cat]");
    if (!b) return;
    fbCat = b.getAttribute("data-cat");
    fbSeg.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
    renderFormulas();
  });
  fbSearch.addEventListener("input", renderFormulas);

  // ---- calculator logic ----
  var calBtn = document.getElementById("dpCalBtn");
  var calPanel = document.getElementById("dpCalPanel");
  var calExpr = document.getElementById("dpCalExpr");
  var calRes = document.getElementById("dpCalRes");
  var calGrid = document.getElementById("dpCalGrid");
  var calMode = document.getElementById("dpCalMode");
  var calClose = document.getElementById("dpCalClose");
  var deg = true;

  // button layout: [label, kind, insertText?]
  var CAL_KEYS = [
    ["sin", "fn", "sin("], ["cos", "fn", "cos("], ["tan", "fn", "tan("], ["\u232B", "util", "back"],
    ["(", "op", "("], [")", "op", ")"], ["%", "op", "%"], ["\u00f7", "op", "\u00f7"],
    ["ln", "fn", "ln("], ["log", "fn", "log("], ["\u221a", "fn", "sqrt("], ["\u00d7", "op", "\u00d7"],
    ["7", "", "7"], ["8", "", "8"], ["9", "", "9"], ["\u2212", "op", "\u2212"],
    ["4", "", "4"], ["5", "", "5"], ["6", "", "6"], ["+", "op", "+"],
    ["1", "", "1"], ["2", "", "2"], ["3", "", "3"], ["x\u00b2", "fn", "^(2)"],
    ["0", "", "0"], [".", "", "."], ["\u03c0", "fn", "\u03c0"], ["^", "op", "^"],
    ["Ans", "fn", "Ans"], ["C", "util", "clear"], ["=", "eq", "eq"]
  ];
  CAL_KEYS.forEach(function (k) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = k[1] || "";
    btn.textContent = k[0];
    btn.addEventListener("click", function () { calKey(k[2]); });
    calGrid.appendChild(btn);
  });

  function insertAtCursor(t) {
    if (t === "back") {
      var s = calExpr.selectionStart, e = calExpr.selectionEnd, v = calExpr.value;
      if (s === e && s > 0) { calExpr.value = v.slice(0, s - 1) + v.slice(s); calExpr.selectionStart = calExpr.selectionEnd = s - 1; }
      else { calExpr.value = v.slice(0, s) + v.slice(e); calExpr.selectionStart = calExpr.selectionEnd = s; }
      return;
    }
    if (t === "clear") { calExpr.value = ""; calRes.textContent = ""; return; }
    if (t === "eq") { evaluate(); return; }
    var s2 = calExpr.selectionStart, e2 = calExpr.selectionEnd, v2 = calExpr.value;
    calExpr.value = v2.slice(0, s2) + t + v2.slice(e2);
    calExpr.selectionStart = calExpr.selectionEnd = s2 + t.length;
    calExpr.focus();
  }
  function calKey(t) { insertAtCursor(t); }

  function evaluate() {
    var raw = calExpr.value;
    if (!raw.trim()) return;
    try {
      var r = calcEval(raw, deg);
      if (typeof r !== "number" || isNaN(r)) { calRes.textContent = "Error"; return; }
      ANS = r;
      calRes.textContent = fmtNum(r);
    } catch (err) {
      calRes.textContent = "Error";
    }
  }

  calExpr.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); evaluate(); }
    else if (e.key === "=") { e.preventDefault(); evaluate(); }
  });
  calMode.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-deg]");
    if (!b) return;
    deg = b.getAttribute("data-deg") === "1";
    calMode.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
  });

  // ---- open / close wiring ----
  function openFb() { calPanel.classList.remove("open"); calBtn.setAttribute("aria-expanded", "false"); fbPanel.classList.add("open"); fbBtn.setAttribute("aria-expanded", "true"); fbSearch.focus(); }
  function closeFb() { fbPanel.classList.remove("open"); fbBtn.setAttribute("aria-expanded", "false"); }
  function openCal() { fbPanel.classList.remove("open"); fbBtn.setAttribute("aria-expanded", "false"); calPanel.classList.add("open"); calBtn.setAttribute("aria-expanded", "true"); calExpr.focus(); }
  function closeCal() { calPanel.classList.remove("open"); calBtn.setAttribute("aria-expanded", "false"); }

  fbBtn.addEventListener("click", function () { fbPanel.classList.contains("open") ? closeFb() : openFb(); });
  calBtn.addEventListener("click", function () { calPanel.classList.contains("open") ? closeCal() : openCal(); });
  fbClose.addEventListener("click", closeFb);
  calClose.addEventListener("click", closeCal);

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (fbPanel.classList.contains("open")) closeFb();
    else if (calPanel.classList.contains("open")) closeCal();
  });

  // first paint
  renderFormulas();
})();
