# dp-study-site — the whole structure

**Verified 2026-09-15 against the live site and both repos. Not recalled — checked.**
Read this before changing anything in `~/Downloads/dp learning final`.

---

## 0. The one-paragraph version

`https://sbk283074-creator.github.io/dp-study-site/` is **one GitHub Pages site** built from **repo A**
(`~/Downloads/dp learning final`). Inside it sit **five "study spaces"** plus seven subject pages.
Only **one** of the five owns a backend (the Question Bank). Three separate backends exist in total,
and they are **not interchangeable** — two of them serve the *same API*, but one of those is 17 days stale.

---

## 1. Two repos (and one nested copy)

| Repo | Path | Remote | Deploys to |
|---|---|---|---|
| **A — dp-study-site** | `~/Downloads/dp learning final` | `sbk283074-creator/dp-study-site` | GitHub Pages → `.../dp-study-site/` |
| **B — ib-dp-platform** | `~/Downloads/dp learning/ib-dp-platform` | `sbk283074-creator/ib-dp-platform` | GitHub Pages **and** Netlify **and** Cloudflare |
| (nested, ignored) | `~/Downloads/dp learning final/dp learning/ib-dp-platform` | — | a gitignored ~13 GB copy. **Do not edit.** |

Repo A's `.gitignore` line 3 is `dp learning/` — that is why the nested copy is invisible to git.
Also ignored: `PYTHON/python-mastery/`, `PYTHON/verify/`, `PYTHON/verify-venv/`, `qbank/figures/`,
`_figures_export/`, `_litfill/`, `tools/_*`. Sources stay local; only built output ships.

---

## 2. The five study spaces — this is the "five websites"

The hub's nav-card row ("Choose where you want to study") numbers them **01–05**:

| # | Name | Path in repo A | Live URL | Kind | Backend |
|---|---|---|---|---|---|
| 01 | DP Learning hub | `index.html` | `/dp-study-site/` | static HTML + shared widgets | none |
| 02 | Question Bank | `qbank/` | `/dp-study-site/qbank/` | **React SPA** (pre-built) | **Cloudflare API** + Netlify figures |
| 03 | Python Mastery | `PYTHON/index.html` | `/dp-study-site/PYTHON/` | single-file app, 2.2 MB | none |
| 04 | The World's Wife Lab | `Eng learning/index.html` | `/dp-study-site/Eng%20learning/` | single-file app, 504 KB | none |
| 05 | Challenge Bank | `challenge-bank/site/` | `/dp-study-site/challenge-bank/site/` | **generated static** | Cloudflare (**AI only**) |

In the repo but **not** one of the five: the subject pages
`math/ physics/ cs/ english/ chinese/ business/ core/` (static study pages), and
`study-plan.html` + `exam-toolkit.html`.

---

## 3. Shared assets — loaded by every static page

| File | Size | What it does | Backend |
|---|---|---|---|
| `assets/ai-widget.js` | 64 KB | the **one** chat implementation — global **Ask AI** + site navigator, *and* the focused per-question mode (§3·1) | `ib-dp-platform-api.pages.dev/api/ask` |
| `assets/tools-widget.js` | 52 KB | Formula Booklet + Scientific Calculator; injected *by* ai-widget.js | none |
| `assets/css/main.css` | 33 KB | site styling | — |
| `assets/js/app.js` | 24 KB | nav, search, page behaviour | — |
| `assets/js/search-index.js` | **1.68 MB** | pre-built search index (`tools/build_search_index.py`) | — |

Referenced by **absolute URL** (`https://sbk283074-creator.github.io/dp-study-site/assets/…`),
so editing the one file updates every page at once.

### 3·1 There is ONE chat implementation, and it has a public hook

Both banks open **the same panel** as the floating button — there is no second chat UI. `ai-widget.js`
ends `build()` by publishing:

```js
window.dpAI = {
  open(opts),   // enter focused mode on one question, then optionally auto-send
  close(),      // closes the panel (also exits focused mode)
  focused()     // -> true while scoped to a question
};
```

`opts`: `ref` (chip label), `questionId` (grounding — the server looks the row up itself),
`subject`, `topic`, `marks`, `context` (question text, prepended to the seed),
`prompt`, `display` (what the user bubble says), `depth`/`difficulty`/`length`,
and `autoSend:false` (prefill the composer instead of sending — used by "Mark my attempt").

Gotchas worth knowing before touching it:

- Focused transcripts live in a **memory-only** array (`scopeMsgs`); they never touch
  `localStorage['dp_ai_chat_v1']`, so the site-wide history is never overwritten. Closing the panel
  runs `exitScope()`, so the floating launcher can never reopen someone else's question.
- `/api/ask` reads **`complexity`** (`simple|standard|deep`), *not* `depth`/`difficulty`. The panel's
  two rows are collapsed by `complexityFor()` before sending; the raw fields are inert server-side.
  `length` (`short|medium|long`) *is* honoured.
- **Grounding comes only from `questionId`.** There is no field for client-supplied question text.
  Book rows are still placeholders (`question` = `"[See question image. Source: …]"`,
  `answer`/`explanation` = `__AI_FILL__`), so the AI cannot actually answer a Books question.

---

## 4. The three backends — and which one is current

| Host | Platform | Serves | Status |
|---|---|---|---|
| `ib-dp-platform-api.pages.dev` | Cloudflare | **the full current API** — health, books, questions, facets, collections, exams, **ask** | ✅ **current** (CORS `*`) |
| `ib-dp-platform.netlify.app` | Netlify | the same API **but 17 days old** — **no `/api/ask`** | ❌ **stale** (last deploy 2026-08-28) |
| `e9ce3af0-…netlify.app/figures/` | Netlify Blobs | question figures | ✅ |

**This split is the most confusing thing in the project.** Pin it down:

- The **Question Bank SPA** (`qbank/`) now uses a **split base** (commit `cb839d1`):
  API → Cloudflare, figures → Netlify. The two are read separately in code, so this needs no code change.
- The **Challenge Bank** and the **global widget** call `https://ib-dp-platform-api.pages.dev`
  → they talk to the **current** backend.
- `/api/ask` was added in commit `dd4316c` on **2026-09-12** — i.e. **after** Netlify's last deploy
  (2026-08-28). So Netlify **404s** it and Cloudflare serves it.
- **The two hosts are not equivalent for images.** Cloudflare has **no `/figures` route at all**
  (route-level JSON 404); Netlify serves figures from a Blob store (200 for a real path, 101 KB).
  That is *why* the base is split rather than simply repointed — pointing both at Cloudflare would
  break the **9,969** question images that use the relative-path figure class.
  (`ib-dp-images-a.pages.dev` also serves them, but *without* the `/figures/` prefix, so it is not a
  drop-in for `QuestionCard.tsx`.)
- **Data is unaffected by the split**: both hosts read the *same* Turso database
  (19 books / 17,273 questions as of 2026-09-14).
- **The files were also missing from the store** — not merely mis-URLed. `/figures/book2/...` 404'd on
  *every* host because the Blob store never received them. **Backfilled 2026-09-15**: 13,342 files /
  **967.5 MB** were absent (`book2` 12,938, `specimen` 153, `physics_hl_p3` 113, `physics_hl_p2` 82,
  `physics_hl_p1` 56) out of a 102,346-file / 10.2 GB local tree. The DB references **35,993 distinct
  image paths** (28,689 relative + 7,304 root-relative) and **0** were missing locally, so the store
  now covers every one of them.

---

## 5. Per-site detail

### 01 · Hub — `index.html` (22 KB)
Hand-written static HTML. Carries `data-page-node-id` attributes (92 of them) injected by an external
page builder — harmless, and a rebuild may re-add them. Loads `main.css`, `app.js`, `search-index.js`,
`ai-widget.js`. **No build step** — edit the HTML directly.

### 02 · Question Bank — `qbank/`
**Not written here.** It is the *built* frontend of repo B.
- Source: `~/Downloads/dp learning/ib-dp-platform/frontend/` (React + TS + Vite).
- Committed output: `qbank/index.html`, `qbank/assets/index-<hash>.js`, `qbank/assets/index-<hash>.css`.
- Reads books / questions / facets / collections / exams from the **Cloudflare** API (since `cb839d1`);
  figures still come from Netlify (see §4).
- **AI — one implementation, two entry points:**
  - the shared global widget (`.dp-ai-launch`) → Cloudflare;
  - a per-question **"Ask AI"** button (`components/AskAI.tsx`, one per card) that does **not** own a
    chat panel. It calls `window.dpAI.open({ref, questionId, subject, topic, marks, …})` and the
    *global* widget opens in **focused mode** (§3·1). It polls for the hook (the widget is `defer`)
    and stays **disabled** until it appears — it no longer unmounts itself, which is what made the old
    select-form version **vanish on click** (the Netlify host 404s `/api/ask/status` and the component
    did `if (status && !status.configured) return null`).
- **Books are hidden from the UI (2026-09-15).** Questions imported from textbooks were not usable —
  `question` holds `"[See question image. Source: …]"` and `answer`/`explanation` are `__AI_FILL__` —
  so they no longer appear anywhere in the frontend. **The rows were not deleted**: they are still in
  Turso, and `/api/questions?category=book` still returns all 7,304 of them. The switch is
  frontend-only and reversible.
  - Search / Practice / Export lost their **All** and **Books** category options and now default to
    **Past papers**. This is the load-bearing detail: an *absent* `category` means "no filter", which
    is exactly what surfaced the books, so every remaining option is a real non-book category and the
    exclusion holds **by construction**. A client-side filter was rejected — books are 42% of all rows
    (7,304 of 17,366), so browser-side filtering cannot produce correct page sizes or totals.
  - `BooksPage` / `BookDetailPage` / `BookReaderPage` now render a shared
    `components/NotAvailable.tsx` notice ("This feature is not available yet"). The previous
    implementations are in git history.
  - `backend/src/api.js` gained an **`exclude_category`** param (comma-separated) for exactly this
    job, but **it is not live** — see trap 14. Nothing in the frontend depends on it.
- **Mock papers now has data (2026-09-15).** The category button had been a dead end: production held
  **zero** `category='mock'` rows, so clicking it returned 0 and rendered the generic
  *"Nothing matches the current filters"* — blaming the user's filters for a dataset that was never
  loaded. The rows are the **official IB specimen papers**, produced by
  `ib-dp-platform/backend/ocr/specimen_json/specimen.json` (93 questions) and imported via
  `POST /api/questions/bulk`. **`mock` is now 93**, and the unfiltered total is **17,366**
  (`7,304 book + 6,977 past + 2,205 topic + 787 questionbank + 93 mock`). All six specimen papers are
  present (CS HL P1 15 / P2 16 / P3 8; Physics HL P1A 40 / P1B 4 / P2 10) and all 93 carry a
  `question_image`.
  - **The import needs no DB credentials.** `createApp()` is only `cors()` + `express.json()` — there is
    **no auth, API key or bearer check anywhere** in `backend/src` or `backend/netlify` — and
    `POST /api/questions/bulk` is **idempotent by id** (`INSERT OR REPLACE` whenever an id is present).
    Send ~20 rows per call: the handler wraps each batch in one `db.transaction`, and the Worker's
    50-subrequest cap is what kills bigger payloads.
- **Still missing: 73 Physics HL past-paper rows (2015 Nov).** They exist in the local dev DB
  (`backend/data/app.db`) but production has **none** of them (40× Paper 1, 9× Paper 2, 24× Paper 3).
  Their 157 image refs all resolve, so only the rows are absent. **They cannot be pushed through the
  API:** `validateQuestion` requires a non-empty `explanation`, and all 73 have `explanation=''` — as do
  **10,042 existing rows** (every `past`/`topic`/`questionbank` row; only `book` and `mock` have
  explanations). The OCR importers (`ocr/import_physics_topic.mjs` and friends) `INSERT` directly and
  bypass the validator, which is why the gap exists and why neither validating path can close it.
  Resolution: run `ib-dp-platform/backend/scripts/copy_missing_rows.mjs --category=past --day=2026-09-12`
  with `TURSO_URL`/`TURSO_AUTH_TOKEN` set — it reads the local rows read-only and writes them through
  `insertQuestion` (no validation) as upserts, so re-running is safe.
- **Rebuild recipe** (the only sanctioned way — never hand-edit the bundle):
  ```bash
  cd ~/Downloads/dp learning/ib-dp-platform/frontend
  VITE_API_BASE_URL=https://ib-dp-platform-api.pages.dev \
  VITE_FIGURES_BASE_URL=https://ib-dp-platform.netlify.app \
  npm run build
  # then copy dist/assets/index-*.js|css into repo A's qbank/assets/ and repoint qbank/index.html
  ```
  Both vars are **mandatory and must differ** (see §4). Without `VITE_API_BASE_URL`, `api.ts` resolves
  the host as `import.meta.env.VITE_API_BASE_URL || ""`, so every call goes *relative* and 404s on
  github.io — that mistake shipped once (commit `24cccf3`). Verify after building: the bundle must
  contain **the Netlify host** (figures) and **the Cloudflare host** (API).
  **The Cloudflare count is 1, not 2, as of 2026-09-15** — `VITE_API_BASE_URL` appears twice in the
  source (`getJSON` and `getBookFileUrl`), but `getBookFileUrl` lost its only caller when the book
  reader was switched off, so Rollup tree-shakes it. Use the Netlify count as the stable invariant.

### 03 · Python Mastery — `PYTHON/`
Ships a **single 2.2 MB `index.html`** — a hash-routed app (`#/01-setting-up-…`).
Sources are gitignored: `PYTHON/python-mastery/` (`build.py`, `chapters/`, `template.html`, `STYLE.md`,
`dist/`), plus `PYTHON/verify/` and `PYTHON/verify-venv/` (a real Python 3.13 venv with
FastAPI/pydantic — 2,798 `.py`, 2,778 `.pyc`, 286 `.so`).
Rebuild: run `PYTHON/python-mastery/build.py` → emits `PYTHON/index.html`. **No backend.**

### 04 · The World's Wife Lab — `Eng learning/`
Ships a **single 504 KB `index.html`**; `data-page-node-id` injected (52). Sources are the poem files
`Eng learning/Poems/*.docx` plus root `.docx`/`.pdf`. Loads the shared `ai-widget.js` by absolute URL.
**No backend, no in-repo build step.**

### 05 · Challenge Bank — `challenge-bank/`
**Fully generated. The JSON is the source of truth, not the HTML.**
- Data: `challenge-bank/data/{math-aa-hl,physics-hl,computer-science-hl,business-management-sl}/*.json`
  — **310 questions** (Math AA HL 125, Physics HL 90, CS HL 56, BM SL 39), as of commit `b69ec98`.
  **Do not count these with a glob.** The filenames are not uniform — `batch21.json`, `batch22.json`,
  `batch22c.json` and `batch23.json` sit beside `p3-batch2.json`, `p1b-data.json`,
  `abstract-data-types.json`, `p2-case-study.json`, `p2-theme-b.json`, `gravitational-fields.json`. A
  `data/*/batch*.json` glob matches **68 files holding 233 of the 310 items** (re-measured 2026-09-16), so
  it silently misses 77; the number drifts as the bank grows, so re-measure rather than quoting it. Batch
  26 is the proof: it added two files and the glob figure **did not move at all**, because both are named
  `…-batch26.json`. Use
  `tools/validate.py`'s `load()`, which also returns **`(file, question)` tuples**, not bare questions.
  **`fig-*.json` are *not* figure assets** — `physics-hl/fig-circuit-structured.json` and
  `fig-standing-wave.json` hold real items (`PHYS-B.5-102`, `PHYS-C.4-102`) and `load()` reads them. The
  figure assets live in `data/_figures.json`, a dict of named SVG builders with no `questions` key, which
  is what the `_` prefix makes `load()` skip.
  (Two Physics writers targeted `physics-hl/batch22.json` at once on 2026-09-16 and one clobbered the
  other; the surviving pair was refiled as `batch22c.json`. **One wave, one filename.**)
- Builder: `challenge-bank/build.py` (55 KB) — emits the entire `site/`.
- Tooling: `challenge-bank/tools/*.py` — `validate.py` (43 KB), `make_figures.py` (40 KB), `fix_json.py`,
  `ship.py`, `coverage.py`, `difficulty_audit.py`, …
- Docs: `README.md`, `STANDARD.md`, `PLAN.md`, `AUDIT_*.md`.
- Output: `challenge-bank/site/` — `index.html`, `q/` (310 question pages), one index per
  subject, `papers/`, `assets/site.js`.
- **AI:** four launcher buttons per question (full worked solution / hint only / guided steps /
  mark my attempt), generated into `site/assets/site.js` from a Python string in `build.py`. They call
  `window.dpAI.open({ref, subject, marks, context, prompt, display, …})` — i.e. the **same** global
  widget in focused mode (§3·1), *not* a self-contained panel. "Mark my attempt" passes
  `autoSend:false` so the composer is prefilled with `MY ATTEMPT:` instead of sending. The question
  text rides along in `context`, so the widget is not limited to `questionId` grounding here.
- **Figures:** hand-authored inline SVG stored in the question JSON as
  `figure = {type:"svg", content, caption}`. `build.py::figure_html` handles **three** types, not one —
  `svg` (`<figure>` + optional `<figcaption>`), `table` (delegates to `table_html`) and `code`
  (`<pre><code>`, content HTML-escaped) — and returns `""` for anything else. At 310 items: **84
  figure-bearing (78 svg / 4 code / 2 table) = 27%**, with every subject above the 15% per-subject
  target (Maths 15%, Physics 37%, CS 43%, BM 21%). No charting library is involved anywhere: every
  figure is a plain-Python SVG string builder in `tools/make_figures.py`, and `validate.py` fails on the
  fingerprints of matplotlib / Chart.js / plotly / vega / bokeh / `<canvas` / `data:image/`, so the
  "without other tools" rule is gate-enforced. `FIGURE_COVERAGE_FLOOR` in `difficulty_audit.py` is a
  **ratchet** (now 0.27): it may rise and may never fall, and it is now the binding constraint — one
  non-figure item of headroom remains, so a new batch must carry figures. A stimulus table is separate
  from a figure: it
  lives in `stimulus.table` and is emitted by `stimulus_html`, so an item can carry a table with no
  `figure`.
- **Difficulty is evidenced, and the top-tier debt is cleared.** Every item must carry
  `difficulty_evidence` (`lever_type` from a closed 13-term taxonomy + `naive_path` + `failure_point` +
  `wrong_answer`); the rubric scores it out of 9 and the label must be earned (d5 needs 8). As of
  2026-09-16: **225 of 310 items evidenced, `difficulty 5 with no evidence: 0`**, and the 85 outstanding
  items are all difficulty-3 or difficulty-4 claims. Reading the 79-item difficulty-5 backlog produced
  **five label corrections, all downwards** — `MATH-P3-010` 5→4, `MATH-AHL5.9-001` 5→4,
  `MATH-AHL5.10-001` 5→3, `MATH-AHL5.11-001` 5→4, `PHYS-E.2-101` 5→4 — while
  `labels the evidence does not permit` stayed at 0.
- **Node coverage is not paper coverage — and a table can encode the same mistake as the data.**
  `PAPER_TYPES` in `validate.py` read `("Computer Science HL", "P2"): {"case_study"}` while `STANDARD.md`
  §2.4 said the opposite, so 17 CS items sat on the wrong paper and **no item carried P2's only legal
  type** — the 80-mark component was unmodelled while the audit reported 100% node coverage. Correcting
  the table to P1 → `{structured, extended_response, case_study}`, P2 → `{extended_response}` produced
  **17 failures with no data change**, and the 17 items were then re-filed by their own `topic` field
  (9 Theme A → P1, 8 Theme B → P2 as `extended_response`). Per-paper distribution is now Maths P1 61 /
  P2 35 / P3 29, Physics P1A 14 clusters (70 questions) / P1B 17 / P2 59, CS P1 44 / P2 12, BM P1 10 / P2 29.
- **`section` is checked too, and the same lesson applied twice.** `section` renders as a student-visible
  chip (`P1 · Section A`) and feeds the paper builder, and was validated nowhere. `SECTION_RULES` in
  `validate.py` now holds the legal set per `(subject, paper)` — **empty set included**, which is what
  makes "this paper has no sections" enforceable — and `SECTION_THEME_RULES` holds CS P1 Section A ⇒
  theme A. Adding the rule exposed **60 items** (of the then-305) with a label their paper does not have: **47
  Physics P2** and **10 Maths P3** were split into sections those papers do not contain (read off the
  guide PDFs: Physics P2 is "short-answer and extended-response questions" with no split named, Maths P3
  is "two compulsory extended response problem-solving questions"), and **3 CS P1** items were theme B in
  Section A. All 60 were cleared rather than reassigned — **60 deletions, 0 insertions across 23 files**.
  Legitimately sectioned: Physics P1 (the 1A/1B booklet split, 14 `mcq` on A / 17 `data_based` on B),
  Maths P1/P2, CS P1, BM P1/P2. What it leaves: **6 CS P1 theme-B items with no case-study anchor** fit
  neither section and need content, not metadata.
- **The same sweep found `technology` wrong in 11 places, and the fix was 128 items.** Auditing *every*
  field `build.py` reads (the defect class is "the renderer prints it and nothing validates it") turned up
  four unchecked rendered fields. `technology` was the bad one: it renders as a chip and had drifted into
  **six strings for three ideas**, and the Maths 2021 guide says Paper 2 and Paper 3 are "Technology
  required" while **3 P2 and 8 P3 items said `not allowed`** — a false instruction on the papers that
  mandate a GDC. `TECHNOLOGY_VALUES` closes the vocabulary to
  `not allowed / permitted / required / not applicable` and `TECHNOLOGY_RULES` records the per-paper
  values policy rules out (Physics is "calculators permitted", so `not allowed` is false there too). The
  migration was **128 insertions / 128 deletions across 46 files** — one line per item. CS and BM guides
  say nothing about calculators, so those stay author judgement, with one open question recorded: **CS P1
  is split 17 `not allowed` / 15 `permitted` within a single paper** and the split correlates with
  nothing. `level` (stated twice — derived from the slug and per item, both printed) and `language`
  (`python / java / pseudocode / sql`) were closed while still free; both were already correct.
- Rebuild: `cd challenge-bank && python3 build.py`.

---

## 6. Build & deploy map

| Artifact | Build | Deploy |
|---|---|---|
| Hub, subject pages, Lit Lab, Python Mastery | hand-edited / their own `build.py` | push repo A → Pages |
| `qbank/` | repo B frontend, `VITE_API_BASE_URL` **set** | copy into repo A → push |
| `challenge-bank/site/` | `python3 build.py` | commit the output → push repo A |
| platform frontend | `npm run build` | Actions `.github/workflows/deploy.yml` → Pages |
| platform backend — **Netlify** | — | **manual `netlify deploy --prod` only; NOT git-connected** |
| platform backend — **Cloudflare** | config not in repo | dashboard / Git-connected; currently the live one |

- Repo A pushes auto-deploy Pages (`.nojekyll` present).
- Pages' CDN caches hard: after a push, poll with `?cb=$(date +%s)`, or read
  `raw.githubusercontent.com/sbk283074-creator/dp-study-site/main/…` to bypass it.
- **The `netlify` CLI cannot run in the agent environment** — invoking it kills the shell even for
  `--version`, sandboxed or not. Any Netlify **redeploy** must be run by the user in Terminal.
- **But the `@netlify/blobs` SDK works fine from the agent.** `getStore({name:'figures', siteID, token})`
  with `siteID` from `.netlify/state.json` and `token` from
  `~/Library/Preferences/netlify/config.json` → `users.*.auth.token` does `list`/`set`/`get` over plain
  HTTPS. That is how the figure blobs are backfilled (`upload-figures-fast.mjs`, concurrency 40,
  idempotent — it snapshots existing keys with `list()` then `set()`s only the missing ones).

---

## 7. Traps that have already bitten

1. **`git push` can report a ref-lock failure and still have succeeded.** Trust `git ls-remote origin main`, not the error text.
2. **A 0-byte `.git/index.lock` blocks commits — check who owns it first.** VS Code leaves orphans, so the fix is to delete the lock and then `add`+`commit` in a **single** command. But `lsof` can report *no holder* while the **concurrent session is mid-`git add -A`**; deleting a live lock corrupts their index. Check `pgrep -fl "git-core|git push|git commit|git add"` too, and wait if one is running.
3. **zsh is not bash.** Unquoted `--include=*.js` → `no matches found`; `for f in $FILES` does **not** word-split. Use the Grep tool or `grep -E`.
4. **A listening port is not a working service.** A wedged vite can hold `:5175` and 500 every request (it runs from a deleted node binary — check `lsof -p <pid> | awk '$4=="txt"{print $NF; exit}'` for `.deleting.`).
5. **`start.command` is not version-controlled** — repo A does not own `~/Downloads/dp learning/`.
6. **The qbank bundle must be built with `VITE_API_BASE_URL`**, or every API call 404s (see §5·02).
7. **`ib-dp-platform.netlify.app` is stale and has no Git connection** (`repo_url: None`), so pushes never reach it. The Cloudflare host is the current one. It **cannot be retired**, though — it is the only host with a `/figures` route (§4).
8. **Repointing `qbank/index.html` — change ONLY the hashed `<script type="module">` line.** The widget cache-buster just below it (`ai-widget.js?v=…`, **`?v=5`** as of 2026-09-15) is a separate concern; drop it and the shared widget goes missing. **Read the current value out of the file rather than assuming it** — it was bumped four times in one day (`v2` → `v3` print rule → `v4`/`v5` the route-change fix). There are also **two hardcoded copies inside `challenge-bank/build.py`**, which generates that whole site; bump the HTML alone and the next build silently reverts it.
9. **React `setState` is not synchronous.** `setCategory('past'); runSearch()` reads the *previous* render's value, so a filter silently needs two clicks. Pass the value you are about to set (`load(0, {category: c})`).
10. **The Bash tool's `grep` can silently return nothing** for patterns that demonstrably exist. Use the Grep tool.
11. **`agent-browser screenshot` takes `[selector] [path]`** — there is no `--path` flag; passing one fails with "Element not found" at exit 0.
12. **`/api/*` 403s a bare `urllib` request.** Send `User-Agent: Mozilla/5.0`.
13. **A second agent session may push to repo A mid-task.** Re-run `git ls-remote origin main` before pushing, and audit which paths the intervening commits touched before assuming your build is intact.
14. **The live API cannot be deployed from this repo.** `ib-dp-platform-api.pages.dev` does **not** auto-deploy. A backend change was pushed (`daa0fc0`, adding `exclude_category`) and the live API ignored it across 12 checks over ~5 minutes — `exclude_category=book` kept returning 17,273 instead of 9,969. There is no `wrangler` config in the repo, and `netlify deploy` cannot run in the agent environment. **Treat any `backend/` change as local-only** until the user deploys it, and never make the frontend depend on a new API param.
15. **The qbank has no SPA fallback.** A hard load of `/dp-study-site/qbank/books` returns a **404** page — GitHub Pages has no rewrite for `qbank/` sub-paths — even though in-app navigation to Books works. Test routes by clicking the nav, not by typing the URL.
16. **TWO checkouts of repo A exist on disk, and only one is authoritative.** `~/Downloads/dp learning final` is the real one (tracked: has `STRUCTURE.md`, `backend/`, `challenge-bank/`, HEAD in step with `origin/main`). `~/Downloads/FOOTBALL STADIUM/dp learning final` is a **stale clone frozen at `56b7bd4`** — Sept-9 state, `qbank/assets/index-B0bvnfED.js`, no `STRUCTURE.md`, no `challenge-bank/` — carrying its own unrelated uncommitted edits to `core/ cs/ english/ math/ physics/`. The agent *workspace* (`.workbuddy-ai/memory/`) sits under the stale one, so `cd`-ing by habit lands in the wrong tree and it will happily accept a commit. Before editing: `git rev-parse HEAD` **and** confirm `STRUCTURE.md` exists. Do not delete the stale clone; it is not yours.
