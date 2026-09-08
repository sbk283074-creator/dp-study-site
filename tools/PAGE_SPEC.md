# PAGE SPEC — DP Learning System

Every content page in this site is a standalone static HTML file that follows this spec exactly.
Consistency is what makes 40 pages feel like one product. Follow it literally.

---

## 1. Exact file skeleton

For a page at `math/01-number-algebra.html`:

```html
<!DOCTYPE html>
<html lang="en" data-subject="math">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Number &amp; algebra — Mathematics AA HL</title>
<link rel="stylesheet" href="../assets/css/main.css">
<script>
window.MathJax={tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']],processEscapes:true},
options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};
function mjFallback(){var s=document.createElement('script');s.src='https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js';s.async=true;document.head.appendChild(s);}
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" onerror="mjFallback()"></script>
</head>
<body>
<div id="app-shell">

  <!-- ALL page content goes here, see section 3 -->

</div>
<script src="../assets/js/app.js"></script>
</body>
</html>
```

Rules:
- Asset paths: pages inside a subject folder use `../assets/...`; pages at the site root use `assets/...`.
- `<html data-subject="...">` must be one of: `start`, `math`, `physics`, `cs`, `english`, `chinese`.
  This drives the accent colour. Do NOT use inline `style="color:..."` anywhere.
- Chinese-language pages use `<html lang="zh-CN" data-subject="chinese">`.
- Math pages (math, physics) include the MathJax block above. CS pages include it only if they use maths
  (e.g. binary/hex, Big-O is fine without). English/Chinese pages omit it entirely.
- NEVER add `<style>` blocks, inline styles, extra CSS files, or extra JS files. The stylesheet
  at `assets/css/main.css` already contains every component listed below.
- Write real, valid HTML. Escape `<`, `>`, `&` in text. Use `&amp;` etc.
- Do not use Markdown syntax. Only HTML.
- In `pre` blocks, escape `<` and `>` as `&lt;` `&gt;`.

---

## 2. Page header block (every page starts with this)

```html
<span class="eyebrow">Mathematics AA HL · Topic 1</span>
<h1 class="page-title">Number &amp; algebra</h1>
<p class="lede">Two or three sentences that answer: what is this topic really about, why does the IB
examine it, and how does it connect to the rest of the course. Written to a student, not a textbook.</p>
<div class="page-meta">
  <span class="tag">~1100 words per subtopic</span>
  <span class="tag">HL only: ●</span>
  <span class="tag tag--hl">Paper 1 · Paper 2 · Paper 3</span>
</div>
```

---

## 3. Component library (use these — do not invent new markup)

### 3.1 Sections
`<h2>` = major section, `<h3>` = subtopic, `<h4>` = sub-part. Anchors are auto-added by JS.

### 3.2 Callouts — the voice of the site
```html
<div class="callout callout--why">
  <span class="callout__label">Why this exists</span>
  <p>…</p>
</div>
```
Variants: `callout--why` (intuition / motivation), `callout--how` (method, procedure, "how to use it"),
`callout--link` (connection to another topic/subject), `callout--exam` (exam technique, markscheme habits,
timing), `callout--trap` (common error / misconception), `callout--note`, `callout--vocab` (term + English gloss;
bilingual entries belong in the chinese section only).

Use at least 4–6 callouts per page, mixed types. Never write a page that is only prose.

### 3.3 Derivation / proof (the "why and how of a formula")
```html
<details class="derivation">
  <summary><span class="badge">Proof</span> Where the quadratic formula comes from (completing the square)</summary>
  <div class="dbody">
    <ol class="steps">
      <li>…</li>
      <li>…</li>
    </ol>
  </div>
</details>
```
Every important formula gets one of these. Show the algebra line by line with `\( \)` / `\[ \]`, and end with
one sentence on *what the result means* and *when it is the wrong tool*.

### 3.4 Worked example — 2+ per key point
```html
<details class="worked">
  <summary><span class="badge badge--medium">Worked example 3</span> IB-style · 7 marks · Calculator allowed</summary>
  <div class="dbody">
    <p><strong>Question.</strong> …</p>
    <ol class="steps">
      <li>…</li>
    </ol>
    <div class="answerline"><b>Answer:</b> …</div>
  </div>
</details>
```
Badges: `badge--easy`, `badge--medium`, `badge--hard`, `badge--hl` (HL only), `badge--sl`.
Solutions must be *fully* worked: every algebraic line, every unit, and a final sentence justifying the
result (e.g. "the answer is negative, which makes sense because the force opposes the motion").

### 3.5 Practice set (end of each major section or page)
```html
<ol class="practice">
  <li>
    <p>Question text.</p>
    <details class="answer">
      <summary>Show answer</summary>
      <div class="dbody">…full solution…</div>
    </details>
  </li>
</ol>
```
5–8 questions per page, graded easy → hard. Every question MUST have an answer.

### 3.6 Connections
```html
<div class="conn">
  <span class="conn__title">Connections</span>
  <ul>
    <li><strong>→ Topic 5 (Calculus):</strong> …</li>
  </ul>
</div>
```
Also available: `<div class="map"><span class="map__node">A</span><span class="map__arrow">→</span>…</div>`

### 3.7 Figures (inline SVG, no external images)
```html
<figure class="viz">
  <svg viewBox="0 0 640 320" role="img" aria-label="…">
    <rect x="0" y="0" width="640" height="320" fill="#ffffff"/>
    … shapes with EXPLICIT fill/stroke colours …
    <text x="20" y="30" font-size="14" fill="#151923">Label</text>
  </svg>
  <figcaption><span class="viz__title">Figure 1.</span> Caption explaining what to notice.</figcaption>
</figure>
```
SVG rules: `viewBox="0 0 640 320"` (or 640×400 when taller), no `width`/`height` attributes, text uses
`font-family="system-ui, sans-serif"`, colours: axis/lines `#334155`, accent stroke `#3653d6`
(physics `#0a6f80`, cs `#7a5a13`, english `#b03060`, chinese `#c0392b`), light fills `#eef2ff`,
grid `#e2e8f0`, labels `#151923`, secondary `#6c7788`. **Every shape must have an explicit fill/stroke** —
no bare shapes, they render black otherwise. Aim for 2–6 figures per topic page where a diagram genuinely
explains something (do not add decorative diagrams).

### 3.8 Tables, grid cards, glossary
```html
<div class="table-wrap"><table><thead><tr><th>…</th></tr></thead><tbody>…</tbody></table></div>
<div class="grid grid--2"><div class="card"><h4>…</h4><p>…</p></div>…</div>
<dl class="glossary"><dt>Term</dt><dd>Definition.</dd></dl>
```

### 3.9 Checklist (persisted in localStorage)
```html
<ul class="checklist">
  <li><label><input type="checkbox"><span>I can derive the quadratic formula from memory.</span></label></li>
</ul>
```

### 3.10 Language-arts extras
```html
<blockquote class="quote-block">“Quotation.”<cite>Work, chapter / line</cite></blockquote>
<table class="quote-table"> … </table>
<div class="io-plan"><div class="io-plan__row"><div class="io-plan__t">0–1 min</div><div class="io-plan__c">…</div></div></div>
<div class="wordlist"><div><b>word</b> — <span>English gloss</span></div></div>
```

---

## 4. Content standard (non-negotiable)

For **every** syllabus sub-point the page covers:

1. **Intuition first** — plain-language "what is going on here", no jargon, one concrete image or analogy.
2. **Formal statement** — the definition / formula / theorem, with every symbol defined.
3. **Why it is true** — a derivation, proof, or first-principles argument inside `details.derivation`.
   For descriptive subjects (CS, languages) replace with "why this design/technique works" reasoning.
4. **How to use it** — a repeatable procedure in `callout--how`, including the calculator / data-booklet
   / command-term specifics the IB expects.
5. **At least two worked examples** with full solutions and a sanity check.
6. **Traps** in `callout--trap` (the three most common ways to lose marks on this point).
7. **Connections** to other points, other topics, and other subjects.
8. **Practice** — closed-book questions with answers.

For every **worked example** and **practice question**, write the solution the way a markscheme would:
state the method, show the substitution, give the final answer with units, and add a one-line comment
on where the marks come from.

Use IB command terms precisely (state, determine, calculate, show that, hence, deduce, justify, evaluate,
explain, describe, analyse, compare, contrast, discuss, to what extent). For HL maths note whether a
question is "show that" (no calculator reasoning needed) or "hence".

Explicitly label HL-only content with `<span class="badge badge--hl">HL only</span>`, and SL/HL-common
content with `<span class="badge badge--sl">SL / HL</span>`.

---

## 5. Length & tone

- Topic pages: **2,500–6,000 words** of real content. Do not pad; do not summarise into bullet skeletons.
- Overview pages: 1,500–2,500 words plus a syllabus map and assessment table.
- Tone: a sharp, encouraging tutor who is honest about what is hard. Second person ("you").
- No filler openings ("In this section we will explore…"). Start with the idea.
- The user is a student whose first language is not English — in maths/physics/CS pages, add a
  `callout--vocab` glossary at the end of each major section with `term — English gloss` pairs for key
  vocabulary (Chinese glosses are not used in this section; they live in the chinese section instead).

---

## 6. Do not

- Do not create any file other than the pages assigned to you.
- Do not modify `assets/css/main.css`, `assets/js/app.js`, or any other agent's pages.
- Do not run a dev server, do not commit, do not call present_files.
- Do not leave TODOs or placeholders. Finish every page you start.
- Do not write "see above" instead of re-explaining; each page must stand alone.
