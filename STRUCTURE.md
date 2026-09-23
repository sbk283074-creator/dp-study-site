# dp-study-site — the whole structure

**Verified 2026-09-16 against the live site and both repos. Not recalled — checked.**
Read this before changing anything in `~/Downloads/dp learning final`.

---

## 0. The one-paragraph version

`https://sbk283074-creator.github.io/dp-study-site/` is **one GitHub Pages site** built from **repo A**
(`~/Downloads/dp learning final`). Inside it sit **six "study spaces"** plus seven subject pages.
Only **one** of the six owns a backend (the Question Bank). Three separate backends exist in total,
and they are **not interchangeable** — two of them serve the *same API*, but one of those is 17 days stale.

---

## 1. Two repos (and one nested copy)

| Repo | Path | Remote | Deploys to |
|---|---|---|---|
| **A — dp-study-site** | `~/Downloads/dp learning final` | `sbk283074-creator/dp-study-site` | GitHub Pages → `.../dp-study-site/` |
| **B — ib-dp-platform** | `~/Downloads/dp learning/ib-dp-platform` | `sbk283074-creator/ib-dp-platform` | GitHub Pages **and** Netlify **and** Cloudflare |
| (nested, ignored) | `~/Downloads/dp learning final/dp learning/ib-dp-platform` | — | a gitignored ~13 GB copy. **Do not edit.** |

Repo A's `.gitignore` line 3 is `dp learning/` — that is why the nested copy is invisible to git.
Also ignored: `PYTHON/verify-venv/`, `qbank/figures/`, `_figures_export/`, `_litfill/`, `tools/_*`.
Note the CODE tracks keep their chapter sources **in** the repo (they are the only copy of the
content); only heavy local tooling (the 234 MB venv) stays out.

---

## 2. The six study spaces — this is the "six websites"

The hub's nav-card row ("Choose where you want to study") numbers them **01–06**:

| # | Name | Path in repo A | Live URL | Kind | Backend |
|---|---|---|---|---|---|
| 01 | DP Learning hub | `index.html` | `/dp-study-site/` | static HTML + shared widgets | none |
| 02 | Question Bank | `qbank/` | `/dp-study-site/qbank/` | **React SPA** (pre-built) | **Cloudflare API** + Netlify figures |
| 03 | Code Mastery | `code/` (hub) + `code/python/index.html` (book) | `/dp-study-site/code/` | platform hub + one self-contained book per track | none |
| 04 | The World's Wife Lab | `Eng learning/index.html` | `/dp-study-site/Eng%20learning/` | single-file app, 504 KB | none |
| 05 | Challenge Bank | `challenge-bank/site/` | `/dp-study-site/challenge-bank/site/` | **generated static** | Cloudflare (**AI only**) |
| 06 | BPhO Round 0 | `bpho/` | `/dp-study-site/bpho/` | static SPA, hash-routed | Cloudflare (**AI only**) |

In the repo but **not** one of the six (the hub has no nav card for these): the subject pages
`math/ physics/ cs/ english/ chinese/ business/ core/` (static study pages),
`study-plan.html` + `exam-toolkit.html`, and the two vocabulary spaces
`ib-english-vocab/` and `vocab-review/` (§5·07).

---

## 3. Shared assets — loaded by every static page

| File | Size | What it does | Backend |
|---|---|---|---|
| `assets/ai-widget.js` | 68 KB | the **one** chat implementation — global **Ask AI** + site navigator, *and* the focused per-item mode (§3·1). Also the **loader for the other two widgets** | `ib-dp-platform-api.pages.dev/api/ask` |
| `assets/tools-widget.js` | 52 KB | Formula Booklet + Scientific Calculator; injected *by* ai-widget.js | none |
| `assets/search-widget.js` | 20 KB | the global search palette (§3·2); injected *by* ai-widget.js | none |
| `assets/css/main.css` | 33 KB | site styling | — |
| `assets/js/app.js` | 24 KB | nav, the hub's inline search box, page behaviour | — |
| `assets/js/search-index.js` | **853 KB** | pre-built search index (`tools/build_search_index.py`), read by *both* search UIs | — |

Referenced by **absolute URL** (`https://sbk283074-creator.github.io/dp-study-site/assets/…`),
so editing the one file updates every page at once. **429 pages load `ai-widget.js`**, which
is what makes it the mount point for every other widget: add a `load<Thing>()` IIFE beside
`loadTools()` and the whole site gets it, with no HTML edits. A widget change still needs
`ai-widget.js?v=` bumped (§7 trap 8) or browsers keep the cached copy.

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

Focus mode is not question-specific, so three more optional keys let a **non-question** page reuse it
without pretending it has a question (all default to the original question-bank wording, so the two
banks are byte-identical to before):

| Key | Effect |
|---|---|
| `noun` | `"poem"` / `"word"` / `"term"` → header becomes "Ask about this **poem**", and the opening bot line is reworded for it |
| `contextLabel` | renames the `Question:` prefix prepended to `context` (e.g. `Poem:` / `Word:` / `Term:`) |
| `intro` | replaces the opening bot line outright |

Live callers of `open()` today:

| Caller | Scope | Notes |
|---|---|---|
| `qbank/` (React) | one question | `questionId` grounding |
| `challenge-bank/site/assets/site.js` | one question | 4 launchers, generated from `build.py` |
| `Eng learning/index.html` | one **poem**, one **glossary term**, the whole glossary | `noun:"poem"` / `"term"`, `contextLabel` set accordingly (§5·04) |
| `vocab-review/index.html` | one **word** | `noun:"word"`, prompt asks for a Chinese explanation (§5·07) |
| `ib-english-vocab/assets/vocab-ask-ai.js` | one **word** | injected into every `days/dayN.html` (§5·07) |

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

### 3·2 There is also ONE search, and it is on every page (added 2026-09-16)

`assets/search-widget.js` — one self-contained palette: **⌘K / Ctrl+K**, or the `/` key, or the
launcher button bottom-left (deliberately bottom-**left**: the AI and tools clusters own
bottom-right). Results are grouped by space, matched terms are highlighted, ↑↓/↵/esc work, and
on a phone it goes full-screen.

It answers from `assets/js/search-index.js` (**980 entries**), fetched **only when the palette is
first opened**. The index is a plain `window.DP_SEARCH_INDEX=[…]` assignment, not JSON, so it
loads by `<script>` and therefore works over `file://`.

Two UIs read that one index — this palette and the hub's inline box in `app.js`. They agree
because both key off `path` / `title` / `heads` / `text`; the palette adds `space`, `kind`,
`badge`, `hash` and an absolute `url`. **If you change the index shape, keep those four keys.**

What the index covers, and the two things it cannot scrape:

| Source | How |
|---|---|
| Tracked HTML (hub, 7 subjects, core, guides, both vocab spaces, qbank, Lit Lab, 5 Challenge Bank indexes, 9 paper pages) | scraped, text capped at 460 chars |
| 331 Challenge Bank questions | `challenge-bank/site/q/*.html`, labelled with id / topic / difficulty / marks / paper |
| `code/python/index.html` (2.2 MB, hash-routed) | split into its **40 `<section class="chapter" id="slug">`** blocks → `#/<slug>` deep links |
| **BPhO** (shell page; content is `window.BPHO_*`) | `tools/bpho_dump.mjs` evaluates the `data/*.js` globals → 435 entries (plan, modules, glossary, worked examples, 163 questions). It **auto-discovers** `modules-N.js` / `questions-N.js` by glob — a hand-maintained file list silently dropped `questions-3.js` from the index once, so new shards are now picked up automatically |
| **World's Wife Lab** (content is one inline `const SEED` literal) | `tools/englab_dump.mjs` brace-matches and evaluates `SEED` → 30 poems with text, key passages and analysis |

- **The Lab gained `#poem=<id>` deep links** for this (§5·04), because a poem result has to open
  *that* poem. The BPhO and Python results deep-link through the routes those apps already had.
- **The palette does NOT query the Question Bank API.** `/api/questions` accepts `search` and
  silently **ignores** it: `medusa`, `entropy` and `quantum` all return the same first rows with
  `total` always 17,366. Rendering that as live results would invent matches, so it offers one row
  that hands the query to the bank instead. `total` is also unusable as a headline figure — it
  counts the 7,304 book rows the bank's own UI hides.
- **Only git-tracked HTML is indexed.** The previous builder walked the working tree, so 84 of its
  161 entries (76 pygame docs in the gitignored `PYTHON/verify-venv/`, 8 in the gitignored 13 GB
  `dp learning/`) pointed at pages that do not deploy. `git ls-files` is the scope now.

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
page builder — harmless, and a rebuild may re-add them. Loads `main.css`, `app.js`, and `ai-widget.js`
(which is what pulls in the tools and the search palette). **No build step** — edit the HTML directly.
`index.html` no longer loads `search-index.js` itself; both search UIs fetch it on demand.

The hub is the **only** place with an inline search box (`#search-input` / `#results`, wired in
`app.js`). ⌘K was claimed by both that box and the palette; the palette now listens in the **capture
phase** and calls `stopPropagation()`, so ⌘K opens the palette and the inline box keeps its value.
Both read the same index, so both answer correctly.

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

### 03 · CODE Mastery — `code/`
**A platform of per-language books**, not one Python page. Each language is one self-contained
`index.html` carrying its whole course; `code/index.html` is the hub that lists them all.

```
code/
├── index.html              ← hub: one card per language, with per-book progress bars
├── _build/                 ← shared build system (one converter for every language)
│   ├── build.py            ←   python3 build.py [<lang-id>]  →  builds books + hub
│   │                           (positional, not --lang; no arg = every live track)
│   ├── languages.json      ←   the registry: every track, its status and its store key
│   ├── template.html       ←   book shell (incl. the two top-bar links back to the DP site)
│   ├── hub-template.html   ←   hub shell
│   └── assets/             ←   style.css + app.js, shared by every book
├── python/                 ← track 1 (live): chapters/ (40 md) + parts.json + STYLE.md
│   └── index.html          ←   2.2 MB built book
└── verify/python/          ← runnable reference implementations (TaskForge, StudyHub) + bug log
```

**Rebuild:** `cd code/_build && python3 build.py` → rewrites every live track's book and the hub.
Adding a language = add a directory with `chapters/` + `parts.json`, then register it in
`languages.json`; the builder needs no edits. **No backend.**

**Check it stayed reproducible:** `sh code/_build/check-idempotent.sh` — it hashes every built page,
runs the build again, and fails if a single byte moved. There is no `dist/` staging area, so
"the dist matches the deployed file" is not a property this layout can have; **idempotence is the
property that matters**. It needs checking mechanically because each book is a ~2 MB single file,
where a dropped link or a stale chapter is invisible by eye — that is exactly how the `.tb-site`
links went missing once.

Caveats worth remembering:
- Each book has its own `localStorage` key. **Python's is deliberately still `python-mastery-v1`**
  so existing readers keep their progress after the move. New tracks get `code-mastery-<id>-v1`.
- Two "back to DP Learning / Question Bank" links were hand-edited into the deployed file once and
  were missing from the template — rebuilding silently deleted them. They now live in
  `template.html`, so the build reproduces them. Do not hand-edit any built `index.html`.
- **`assets/ai-widget.js` keeps its own hardcoded site map.** Moving a space means editing it in
  three places: the `SITE` array, the path→label function, and the "suggested flow" line. It builds
  its nav in JavaScript, so **grepping the static HTML will not find these** — when `PYTHON/` moved
  to `code/`, all three were missed while the HTML looked clean. Check it whenever a space moves.
  Every page also loads it from the **absolute production URL** with a cache-busting query
  (`…/dp-study-site/assets/ai-widget.js?v=13`), so a local edit cannot be tested locally — the
  browser fetches the *deployed* copy. **Deploying a widget change therefore needs the `?v=` number
  bumped in every page that loads it**, or browsers keep serving the cached build.
- `PYTHON/index.html` is now a 1.5 KB **redirect** to `../code/python/index.html`; the old 2.2 MB
  file and its sources were moved with `git mv` (history preserved).

### 04 · The World's Wife Lab — `Eng learning/`
Ships a **single 504 KB `index.html`**; `data-page-node-id` injected (52). Sources are the poem files
`Eng learning/Poems/*.docx` plus root `.docx`/`.pdf`. Loads the shared `ai-widget.js` by absolute URL.
**No backend, no in-repo build step.**

- **All 30 poems and their analysis live in one inline `const SEED` literal**, not in the DOM —
  nothing is rendered until you pick a poem. So a crawler sees only the toolbar, which is why the
  old search index had one entry for the whole lab reading "Read & Annotate  Analysis  Key lines".
  `tools/englab_dump.mjs` extracts the literal by brace matching and evaluates it (§3·2).
- **`#poem=<id>` deep links** (added 2026-09-16, for the search palette): a small script *after* the
  app's own `<script>` reads the hash and reuses the app's `currentPoem` / `switchView()` /
  `render()`. It is a no-op without a hash, and it works because `let currentPoem` at the top level
  of a classic script is visible to a later one. The lab itself has **no** hash routing of its own —
  `selectPoem`/`currentPoem` are plain state, and there is no `URLSearchParams` anywhere.

### 05 · Challenge Bank — `challenge-bank/`
**Fully generated. The JSON is the source of truth, not the HTML.**
- Data: `challenge-bank/data/{math-aa-hl,physics-hl,computer-science-hl,business-management-sl}/*.json`
  — **337 questions** (Math AA HL 136, Physics HL 95, CS HL 67, BM SL 39). Re-measured 2026-09-23;
  the count comes from `tools/validate.py`'s `load()`, never from a glob.
  **Do not count these with a glob.** The filenames are not uniform — `batch21.json`, `batch22.json`,
  `batch22c.json` and `batch23.json` sit beside `p3-batch2.json`, `p1b-data.json`,
  `abstract-data-types.json`, `p2-case-study.json`, `p2-theme-b.json`, `gravitational-fields.json`. A
  `data/*/batch*.json` glob matches **68 files holding 233 of the 331 items** (re-measured 2026-09-17), so
  it silently misses 98; the number drifts as the bank grows, so re-measure rather than quoting it. Batch
  26 is the proof: it added two files and the glob figure **did not move at all**, because both are named
  `…-batch26.json` — and Batch 27 repeated it, its one file being `figures-batch27.json`, which the glob
  does not match either. Batch 28's one file is `p1a-theme-a-batch28.json`, Batch 29's is
  `p1a-mcq-batch5.json` and Batch 30's is `section-a-batch30.json`, and none of the three matches —
  `batch*.json` needs the filename to *begin* with `batch`
  — so the glob figure has now been frozen at 233 for five consecutive waves (26, 27, 28, 29, 30) and would
  read the same if the bank had not grown at all: 315 → 331 items moved it by exactly zero.
  `data/*/*batch*.json` (85 files holding 298 of the 331) is the pattern that works; neither is a
  substitute for `load()`. Use
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
- Output: `challenge-bank/site/` — `index.html`, `q/` (337 question pages), one index per
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
  (`<pre><code>`, content HTML-escaped) — and returns `""` for anything else. At 337 items: **110
  figure-bearing (104 svg / 4 code / 2 table) = 33%**, with every subject above the 15% per-subject
  target (Maths 22%, Physics 39%, CS 52%, BM 21%). No charting library is involved anywhere: every
  figure is a plain-Python SVG string builder — the named set in `tools/make_figures.py`, the rest
  inline in the batch generator that authored the item (which is `/tmp`-only, so the JSON copy is the
  only durable one — see the trap note below), and `validate.py` fails on the
  fingerprints of matplotlib / Chart.js / plotly / vega / bokeh / `<canvas` / `data:image/`, so the
  "without other tools" rule is gate-enforced. `FIGURE_COVERAGE_FLOOR` in `difficulty_audit.py` is a
  **ratchet** (now 0.32): it may rise and may never fall, and it is now the binding constraint — six
  non-figure items of headroom remain, so a new batch must carry figures. A stimulus table is separate
  from a figure: it
  lives in `stimulus.table` and is emitted by `stimulus_html`, so an item can carry a table with no
  `figure`.
- **MCQ options are printed now, and the key is measured.** Until 2026-09-23 `build.py` rendered
  `parts[].options` **nowhere** — not on the question page, not in the printable paper — so a Physics
  P1A candidate met "Which statement is correct?" with no statements on 95 questions, and the fact that
  every authored cluster keys its answer at the *first* option went unnoticed for six waves.
  `options_html` / `options_scheme_html` now print the choices on every surface, with the keyed option
  badged and each `rationale` shown in the markscheme (for an MCQ the per-option rationale *is* the
  markscheme). Two gates came with the fix: `validate.py` fails any part whose answer states a letter
  different from the option flagged `correct` (and warns where no letter is stated at all), and
  `difficulty_audit.py` section 6 reports the key distribution against `KEY_SPREAD_CEILING` (0.80, a
  ratchet that may only fall) plus `KEY_MONO_CLUSTERS_MAX` (14). Measured 2026-09-23: **A 76, B 6, C 7,
  D 6** over 95 questions, with **14 clusters keying all five parts at A**. Redistributing them is the
  published backlog and it is *not* a regex job — 14 of those clusters name other options by letter in
  their markscheme prose ("Option B inverts it, option C assumes…"), so a blind reorder would turn a
  markscheme sentence into a false statement. That is exactly why the letter-versus-key assertion ships
  first, as STANDARD §4.3 already said it must.
- **Difficulty is evidenced, and the top-tier debt is cleared.** Every item must carry
  `difficulty_evidence` (`lever_type` from a closed 13-term taxonomy + `naive_path` + `failure_point` +
  `wrong_answer`); the rubric scores it out of 9 and the label must be earned (d5 needs 8). As of
  2026-09-23: **252 of 337 items evidenced, `difficulty 5 with no evidence: 0`**, and the 85 outstanding
  items are all difficulty-4 claims. Reading the 79-item difficulty-5 backlog produced
  **five label corrections, all downwards** — `MATH-P3-010` 5→4, `MATH-AHL5.9-001` 5→4,
  `MATH-AHL5.10-001` 5→3, `MATH-AHL5.11-001` 5→4, `PHYS-E.2-101` 5→4 — while
  `labels the evidence does not permit` stayed at 0.
- **Node coverage is not paper coverage — and a table can encode the same mistake as the data.**
  `PAPER_TYPES` in `validate.py` read `("Computer Science HL", "P2"): {"case_study"}` while `STANDARD.md`
  §2.4 said the opposite, so 17 CS items sat on the wrong paper and **no item carried P2's only legal
  type** — the 80-mark component was unmodelled while the audit reported 100% node coverage. Correcting
  the table to P1 → `{structured, extended_response, case_study}`, P2 → `{extended_response}` produced
  **17 failures with no data change**, and the 17 items were then re-filed by their own `topic` field
  (9 Theme A → P1, 8 Theme B → P2 as `extended_response`). Per-paper distribution is now Maths P1 67 /
  P2 40 / P3 29, Physics P1A **19 clusters (95 questions)** / P1B 17 / P2 59, **CS P1 49** / P2 18,
  BM P1 10 / P2 29.
- **`section` is checked too, and the same lesson applied twice.** `section` renders as a student-visible
  chip (`P1 · Section A`) and feeds the paper builder, and was validated nowhere. `SECTION_RULES` in
  `validate.py` now holds the legal set per `(subject, paper)` — **empty set included**, which is what
  makes "this paper has no sections" enforceable — and `SECTION_THEME_RULES` holds CS P1 Section A ⇒
  theme A. Adding the rule exposed **60 items** (of the then-305) with a label their paper does not have: **47
  Physics P2** and **10 Maths P3** were split into sections those papers do not contain (read off the
  guide PDFs: Physics P2 is "short-answer and extended-response questions" with no split named, Maths P3
  is "two compulsory extended response problem-solving questions"), and **3 CS P1** items were theme B in
  Section A. All 60 were cleared rather than reassigned — **60 deletions, 0 insertions across 23 files**.
  Legitimately sectioned: Physics P1 (the 1A/1B booklet split, 19 `mcq` on A / 17 `data_based` on B),
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

### 06 · BPhO Round 0 — `bpho/`
Preparation space for the **British Physics Olympiad Round 0** paper (25 single-answer MCQs,
60 min, **non-calculator**, 1 mark each, no negative marking, no awards — a selection round only).
Built 2026-09-16. **Hand-authored static SPA — no build step, no bundler, no `fetch()`.**

- Shell: `bpho/index.html` — plain `<script>` tags in dependency order, then `assets/app.js`.
- Data lives in `bpho/data/` and ships as **`window.BPHO_*` global assignments**, *not* JSON files.
  This is deliberate: the pages must work over `file://`, where `fetch()` is blocked by CORS.
- Content is split across files that each **`concat` onto a shared global**, because one 300 KB+
  data file is unreviewable:
  `plan.js` (16 days) · `glossary.js` (141 terms) · `modules-1.js` … `modules-7.js` (14 modules,
  162 checklist items, **100 worked examples**) · `questions-1.js` … `questions-3.js` (**163 authored questions**) ·
  `questions-4.js` (**25**, the 2025 past paper) · `questions-5.js` (**12**, the published sample
  sheet) · `guidance.js` (`window.BPHO_GUIDANCE` — one entry per module, see below).
  `guidance.js` is **not** an aggregator: it must load before `assets/app.js`, and `app.js` falls back
  to `{}` if it is missing, so the space degrades to no-guidance rather than breaking.
- Two aggregators present the exact shape `app.js` expects and must load **last**:
  `curriculum.js` → `window.BPHO_CURRICULUM = {modules: (window.BPHO_MODULES || [])}` and
  `questions.js` → `window.BPHO_QUESTIONS = (window.BPHO_QUESTIONS || [])`.
  **Adding a module means adding a file *and* a `<script>` tag before the aggregator.**
- Routes (hash-routed): `#/` overview, `#/plan`, `#/m/<CODE>`, `#/practice[/<CODE>]`,
  `#/glossary`, `#/reference`, `#/mock`. Progress is `localStorage` with export/import JSON.
- **Study guidance** (`guidance.js`, one entry per module code): `prereq` (what you must already be
  able to do), `before[]` (module codes to read first), `starter[3]` (a three-question readiness
  check, `{q, opts[3], ans, why}`) and `review`. The `before[]` edges are the single source of truth
  for two derived views: the overview's **"Where to start"** `<ol class="steps">` is a stable
  topological sort of them (`gdOrder()`), and each module's **"This unlocks"** column is computed by
  inverting them (`gdAfter()`) — never stored, so the two can never disagree. Module A is the sole
  entry point; its "Learn this first" column reads *"nothing — start here"*.
  The readiness check is a **gate, not a score**: the Check button stays `disabled` until all three
  are answered, and a miss recommends re-reading rather than retrying.
- **Mock system**: two modes on `#/practice`. *Timed* is the real format — 25 random questions in
  60 min, live `#mocktimer` clock with `is-low` (≤300 s) and `is-out` (≤60 s) states, auto-marking at
  zero. *Untimed* drops the clock (`seconds: 0`) so the same paper can be used to learn the material.
  The single interval is stopped on **every** render and restarted only for a live unmarked timed mock
  (`stopMockTimer()` then conditional `startMockTimer()`), so it cannot leak across routes.
  The result view gives a **by-topic table** (worst first), **weak-topic recommendations** ranked by
  marks available (`a.modules`), and a **repair plan** — an `ol.steps` that leads with *stop leaving
  blanks* (no negative marking ⇒ a blank is a thrown-away mark), then up to three per-module sessions
  naming the topics missed, then mode-specific advice, then "take another mock".
- **AI:** every question card carries an "Ask AI about this" button wired to
  `window.dpAI.open({ref, subject, topic, context, prompt, display, autoSend:true})` — the **same**
  global widget in focused mode (§3·1), not a second chat UI. The question, its five options, the
  correct letter and the official solution all ride along in `context`.
- **Registering a new space is a TWO-place job, and the second place is easy to forget:**
  (1) a `.platform-card` in the hub's `index.html` card row, and (2) an entry in the shared widget's
  `SITE` array in `assets/ai-widget.js` — that array *is* the **🧭 Sites** button list, and it also
  drives the "you are here" marker and the "Suggested flow" line. A space that is in (1) but not (2)
  is reachable but invisible to the site map. The path also needs a branch in `inferSubject()`
  (same file) or the widget cannot name the space it is on.
- Module codes are the letters **A, I, L, M, H, B, C, D, E, F, G, K, J, N** — not A–N in order.
  Each checklist item carries a flag from `CORE` / `NEW` / `R1-ONLY` / `SKIP` and the module carries
  a priority 1–4. `R1-ONLY` marks material that appears in Round 1 but is **out of scope** for
  Round 0; module N is explicitly an insurance module of Round 1 material.
- Scope rule that governs the whole space: **Round 1 evidence is not evidence about Round 0.**
  BPhO publishes no Round 1 syllabus, so the R0/R1 differential was reconstructed from the Round 0
  sample paper plus the AQA AS Physics 7407 spec (§3.1–3.5), not from Round 1 papers.
- Verification (2026-09-16, headless Chromium over `http://127.0.0.1:8899/`): all 8 routes render,
  81 question cards, answering Q1 gives "Correct", solution reveal opens, a checklist tick
  **persists across reload**, mock starts with 125 option buttons (25 × 5) and marking produces the
  result view with 3 stat cards, and the hub card navigates to the space. Zero console/page errors.
  Also confirmed the **🧭 Sites** list shows "BPhO Round 0" and the "Suggested flow" links to it.
  *Testing note:* the widget is loaded by **absolute URL**, so a localhost run fetches the *deployed*
  copy — test an edited widget with a Playwright `route` interception serving the local file, or the
  old version passes and the new one is never exercised. "you are here" reads 0 on localhost for
  **every** space, because the widget compares against `HUB + item` (a live absolute path) while the
  local path is shorter; that is a harness artefact, not a defect.
- **Audit + expansion (2026-09-17).** A full audit of the 100 worked examples and the question bank
  found one systemic defect: **every one of the 81 answers was option A**, and the solutions all read
  "Answer: A". Fixed by redistributing the correct option across A–E and remapping every option
  letter quoted inside the solution text, then re-checking each swap against the option values.
  Four worked examples had genuine errors (`F` third-harmonic option mislabelled as the *second*
  harmonic's wavelength; `J` calorimetry option 420 that no computation produced; `J` ice-melt option
  1.0 × 10⁵ where the sum is 8.4 × 10⁴; `J` aluminium expansivity unit). The bank then grew
  **81 → 163** with 82 new questions (new `questions-3.js`) written to be non-calculator and
  ratio/multi-step where possible.
  Current invariants, all machine-checked: 163 questions / 14 modules / 14 guidance entries · answer
  spread **A 34, B 33, C 32, D 32, E 32** · **0** duplicate options · **0** malformed 5-option
  arrays · **0** solutions whose stated letter disagrees with the `ans` index · **0** duplicate IDs ·
  **0** topology violations in the reading order. `applications`-style dead data (`trap`) is left
  alone — it is never rendered.
  Browser pass re-run 2026-09-17 (headless Chromium, `http://127.0.0.1:8123/bpho/index.html`):
  overview shows 163; module E renders its guidance block, readiness check gated then marking
  *2 / 3*; timed mock shows 25 questions with the clock ticking 59:59 → 59:57 and the answered
  counter moving 0 → 9 of 25; result view shows the stat grid, 25 topic rows, weak topics and a
  5-step repair plan; leaving the mock removes `#mocktimer`; the untimed mock renders with no clock.
  **Zero 4xx responses and zero page errors.**
- **Hand-drawn figures (2026-09-17).** Every diagram in the space is **inline SVG authored by hand
  into the data strings** — no image files, no image-generation tool, no fetched asset. That is forced
  by the `file://` constraint for the same reason the data is: an external `.svg` would be a second
  network request, and the pages must work from disk.
  **38 figures** ship: **16 in the explanations** (`modules-3.js` 6 for H·circuits, `modules-4.js` 6
  for C·forces, `modules-6.js` 4 for G·optics) and **22 in the question stems** (`questions-1.js` 8,
  `questions-2.js` 6, `questions-3.js` 5 … plus the H/I shards). Markup is
  `<figure class="fig"><svg viewBox="0 0 W H" role="img" aria-label="…">…</svg>` with an optional
  `<figcaption>`; `assets/style.css` scales the SVG with `width:100%;height:auto;max-width:560px`, so
  figures are responsive with **no fixed `width`/`height`** on the `<svg>`.
  Three rules make them safe in this codebase:
  1. **A question stem that carries a figure must be a backtick template string.** `q` was a
     double-quoted string; SVG attributes also use `"`, so the field had to be converted to
     `` q: `<p>…</p><figure…>…</figure>` ``. Backticks are safe here because the SVG contains no
     `${`. `sol` and section `body` were already backticked.
  2. **Marker ids must be globally unique across every figure.** HTML documents have **no id
     namespace**, so two figures each defining `id="a"` collide and one of them silently renders with
     the wrong arrowhead. Every marker is therefore prefixed per figure (`cq2-*`, `ds-*`, `gr-*`,
     `oe-*`, `vr-*`, `bm-*`, `cb-*`, …). Current total: 40 ids, all distinct.
  3. **Colours are literal hex, not CSS variables.** `app.js` injects `q.q` / `s.body` / `x.sol` into
     `innerHTML` **raw** (only labels and ids pass through `esc()`), so SVG survives intact — but a
     `var(--ink)` inside a `<text fill>` resolves against the SVG's own context, not the page. Figures
     hand-colour with `#14181f` ink · `#4a5262` ink-2 · `#7b8494` ink-3 · `#e2e6ed`/`#cbd2dd` lines ·
     `#2f5fd0` accent · `#b3352f` bad · `#1f7a53` good · `#a8641a` warn · `#5b3fa8` purple.
  **A figure must encode the discriminator the question tests, not decorate it** — the half-wave
  rectified waveform shows the *same peak, half the area*; the friction graph shows the *drop* at
  limiting equilibrium; the lamp I–V curve *flattens* while the diode is *flat then vertical*; the
  double-slit figure carries the `s sin θ` construction. Figures that merely illustrate the apparatus
  are worth less than ones that carry the argument.
  *Verification.* `/tmp/lint-svg.js` walks every `<figure class="fig">` and asserts: no dangling
  `url(#id)`, no `x2`/`y2` on a `<text>`, balanced tags, `viewBox="0 0 W H"`, `role="img"` +
  `aria-label`, and **no duplicate id across the whole space**. It found one real geometry bug — an
  SVG arc written `A78 78 0 1 1` (large-arc **and** sweep both set) renders with an *enlarged* radius
  and bulged outside the circle; the long arc needs `large-arc=1, sweep=0`. Screenshot every figure
  with Playwright before believing it: presence in the DOM is not the same as being drawn correctly.
  The browser pass asserts **100 `.ex`, 16 explanation figures, 22 question figures, zero
  zero-size SVGs, zero console errors**, and that no raw `viewBox`/`stroke-width` text leaks into a
  paragraph.
- **The two named papers, their generators, and the /tmp trap (2026-09-18).** The space ships two
  real question sets, each a named paper a mock can be assembled from:
  - `questions-4.js` — **25 questions**, the 2025 past paper, `paper:"R0-2025"`. Its key is the
    **printed** one (A 8, B 5, C 5, D 3, E 4).
  - `questions-5.js` — **12 questions**, the published 2025 **sample sheet**, `paper:"R0-SAMPLE"`.
    BPhO prints no key for it, so the key was derived from first principles and checked against the
    sheet's own geometry. It has **no answer C** (B 6, D 3, E 2, A 1). That is the real sheet, not a
    defect, so `tools/r0sample/build.py` **pins the sequence** instead of requiring all five letters —
    "correcting" the distribution toward uniformity would falsify the record.
  Four of the twelve are decidable only from the drawing, which is why their figures are **generated
  from measured geometry** rather than described: the plate polarity in **S3** (both long plates are on
  the left, so the link carries 0.50 A, not 1.5 A), the exponent on option E of **S6**
  (`A² s³ J⁻¹` is a farad·second, so only `s Ω⁻¹` is a capacitance), the load position in **S7** (the
  outline path begins at the midpoint of the R–R edge — that is what makes moments about that edge
  clean), and the curvature in **S8** (only E decreases *and* flattens without reaching the axis, the
  `arcsin(1/n)` shape).
  - **Generators.** `data/questions-4.js` comes from `tools/paper2025/{q1..q5,figs,keys,build}.py`;
    `data/questions-5.js` from `tools/r0sample/{qs,figs,keys,build}.py`. Both emit into `bpho/data/`,
    and both figure scripts write `fig/` **beside themselves**. They used to import from and read
    figures out of `/tmp/bpho25`, which made the committed `questions-4.js` **unreproducible the moment
    `/tmp` was cleared** — and nothing in the repo said so. Everything now resolves relative to the
    script's own file, and that fix is verified the only way it can be: regenerate `questions-4.js` and
    diff against the committed copy — **byte-identical**.
    The teaching layer works the same way: `tools/paper2025/build_concepts.py` reads
    `concepts_a/b/c/d.py` **and both `keys.py` maps**, loaded by explicit path (both banks ship a file
    of that name, so a plain `import keys` would silently shadow one with the other). It emits
    `data/concepts.js` — **71 key points, 129 links across the two banks**. The sample sheet needed four
    points the past paper never tested: `criticalangle`, `secondorder`, `apparentweight`, `tailmass`
    (all authored in `concepts_d.py`). Rebuilding was diffed and shown to be **purely additive**: 144
    lines added, 28 replaced (3 header lines, 24 `q:` arrays that gained a sample id, 1 trailing comma).
  - **Gates — and the ones that were watched to fail.** `build.py` checks each answer against the
    derived key, that `sol` states the same letter, five distinct options, no unresolved `{{FIG}}`, no
    caret or ASCII exponent, every decimal hand-computable, and that every question is keyed. The
    non-calculator lint deliberately **does not strip the SVG**: a figure label is exactly as visible as
    a sentence, and on the past paper an evaluated 20.7° sat in an axis label no candidate could
    produce. Three defects were planted and each was *required* to fail — a flipped answer (caught by
    two gates), a calculator-only decimal **inside a figure label** (caught: the past paper's bug shape),
    and a **caret inside a figure label**, a real hole because `supify()` runs on the stem *before* the
    SVG is inlined. `tools/r0sample/verify_figs.py` separately asserts every drawn coordinate falls
    inside its `viewBox` — the defect that made the first five figures render **completely empty**,
    which looks identical to correct until it is rasterised.
  - **UI.** `#/practice` gained a second paper chip and a second mock toolbar. The mock clock now
    derives from the question count (`SECONDS_PER_QUESTION = 144`, the paper's own 2.4 min per question)
    instead of a hardcoded `60 * 60`, so the 12-question sheet gets **29 minutes** while the 25-question
    paper still gets 60. The result page no longer judges the sample against **11/25** — BPhO sets no
    pass mark on it, so it is scored against the **44% that line implies**, and says so. Ids are
    labelled through `qLabel()` / `qLabelLong()` / `paperLabel()`: a bare `replace("R0-", "Q")` left the
    sample ids leaking through as `R0S-01` into links that read `Q…` everywhere else.
  - **Rebuild:** `python tools/paper2025/figs.py && python tools/paper2025/build.py` for the past paper
    (same two under `tools/r0sample/` for the sample sheet), then
    `python tools/paper2025/build_concepts.py` for the teaching layer. `build.py` reads `fig/`, so
    regenerate the figures after any change to them. Everything else in the space is still hand-edited
    directly.

### 07 · The two vocabulary spaces — `ib-english-vocab/` and `vocab-review/`

Neither is in the hub's 01–06 row; both are reached from the widget's **🧭 Sites** map.

**`vocab-review/`** — "词汇复习站 · Vocabulary Review", a **Chinese-UI** Leitner spaced-repetition
drill over ~1,450 curated words (`data.js` + `data_extra*.js`). Single `index.html`, no build.
`openDetail(w)` renders one word into `#detailCard` and stashes it in the module-level `detailWord`,
which is what the **🤖 问 AI：就讲这个词** button reads; that button got its own `.askai` accent class
in `.d-actions`. Its prompt is deliberately Chinese, matching the site's own UI language.

**`ib-english-vocab/`** — the IB English vocabulary plan, an **English-UI** site: a `manifest.json`
hub plus one page per day in `days/`.
- Hub: `index.html` + `assets/site.js` + `assets/site.css`; `site.js` fetches `manifest.json`.
- Day pages: **fully self-contained** — inline CSS, and until now no shared JS at all.
- `build.mjs` regenerates `manifest.json` (curated entries are preserved) and the `/day/N/` redirect
  stubs. It does **not** generate the day pages themselves.

**The per-word Ask AI hook.** Because day pages share no stylesheet or script, the button cannot live
in shared CSS — it lives in `assets/vocab-ask-ai.js` (6 KB), which every day page loads via
`<script src="../assets/vocab-ask-ai.js" defer></script>` placed **right after** the widget tag.
It reads each `.word-card` (`.word` `.ipa` `.pos` `.definition` `.usage-box` `.example` `.ib-tip`
`.collocations`), appends a pill button into `.word-header`, and calls
`window.dpAI.open({ … noun:"word", contextLabel:"Word", autoSend:false })`. It is idempotent, so
running twice cannot double the buttons.

Two consequences worth remembering:

- **Load order matters.** `ai-widget.js` defines `window.dpAI` only while its `build()` runs, and both
  scripts are `defer`, so the widget tag must come first. Reversing them silently disables the button.
- **A regenerated day page must keep both `<script>` tags**, or it loses the feature without any error.

---

## 6. Build & deploy map

| Artifact | Build | Deploy |
|---|---|---|
| Hub, subject pages, Lit Lab, Python Mastery | hand-edited / their own `build.py` | push repo A → Pages |
| `assets/js/search-index.js` | `cd repo root && python3 tools/build_search_index.py` (needs `node` for the BPhO and Lit Lab dumpers; skips them with a warning if absent) | commit the output → push repo A |
| `bpho/` | **none** — hand-authored data files, no bundler | push repo A → Pages |
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
8. **Repointing `qbank/index.html` — change ONLY the hashed `<script type="module">` line.** The widget cache-buster just below it (`ai-widget.js?v=…`, **`?v=13`** as of 2026-09-16) is a separate concern; drop it and the shared widget — and with it the search palette and the tools — goes missing. **Read the current value out of the file rather than assuming it**; nobody keeps a changelog of these bumps. There are also **two hardcoded copies inside `challenge-bank/build.py`**, which generates that whole site: bump the HTML alone and the next build silently reverts it. Those two copies had drifted to `?v=5` while the site was on `v12`, so a Challenge Bank rebuild would have quietly dropped the site back seven versions. Bump **all four places at once** — `challenge-bank/build.py` (2), and every HTML file (there is no build step for the hub/subjects/Lit Lab/BPhO, so they are edited in place).
9. **React `setState` is not synchronous.** `setCategory('past'); runSearch()` reads the *previous* render's value, so a filter silently needs two clicks. Pass the value you are about to set (`load(0, {category: c})`).
10. **The Bash tool's `grep` can silently return nothing** for patterns that demonstrably exist. Use the Grep tool.
11. **`agent-browser screenshot` takes `[selector] [path]`** — there is no `--path` flag; passing one fails with "Element not found" at exit 0.
12. **`/api/*` 403s a bare `urllib` request.** Send `User-Agent: Mozilla/5.0`.
13. **A second agent session may push to repo A mid-task.** Re-run `git ls-remote origin main` before pushing, and audit which paths the intervening commits touched before assuming your build is intact.
14. **The live API cannot be deployed from this repo.** `ib-dp-platform-api.pages.dev` does **not** auto-deploy. A backend change was pushed (`daa0fc0`, adding `exclude_category`) and the live API ignored it across 12 checks over ~5 minutes — `exclude_category=book` kept returning 17,273 instead of 9,969. There is no `wrangler` config in the repo, and `netlify deploy` cannot run in the agent environment. **Treat any `backend/` change as local-only** until the user deploys it, and never make the frontend depend on a new API param.
15. **The qbank has no SPA fallback.** A hard load of `/dp-study-site/qbank/books` returns a **404** page — GitHub Pages has no rewrite for `qbank/` sub-paths — even though in-app navigation to Books works. Test routes by clicking the nav, not by typing the URL.
16. **TWO checkouts of repo A exist on disk, and only one is authoritative.** `~/Downloads/dp learning final` is the real one (tracked: has `STRUCTURE.md`, `backend/`, `challenge-bank/`, HEAD in step with `origin/main`). `~/Downloads/FOOTBALL STADIUM/dp learning final` is a **stale clone frozen at `56b7bd4`** — Sept-9 state, `qbank/assets/index-B0bvnfED.js`, no `STRUCTURE.md`, no `challenge-bank/` — carrying its own unrelated uncommitted edits to `core/ cs/ english/ math/ physics/`. The agent *workspace* (`.workbuddy-ai/memory/`) sits under the stale one, so `cd`-ing by habit lands in the wrong tree and it will happily accept a commit. Before editing: `git rev-parse HEAD` **and** confirm `STRUCTURE.md` exists. Do not delete the stale clone; it is not yours.
