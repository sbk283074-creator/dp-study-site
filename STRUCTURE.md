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
  github.io — that mistake shipped once (commit `24cccf3`). Verify after building: the bundle should
  contain the Cloudflare host **twice** and the Netlify host **once**.

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
  — 238 questions (Math AA HL 102, Physics HL 71, CS HL 37, BM SL 28).
- Builder: `challenge-bank/build.py` (55 KB) — emits the entire `site/`.
- Tooling: `challenge-bank/tools/*.py` — `validate.py` (43 KB), `make_figures.py` (40 KB), `fix_json.py`,
  `ship.py`, `coverage.py`, `difficulty_audit.py`, …
- Docs: `README.md`, `STANDARD.md`, `PLAN.md`, `AUDIT_*.md`.
- Output: `challenge-bank/site/` — `index.html`, `q/` (238 question pages), one index per
  subject, `papers/`, `assets/site.js`.
- **AI:** four launcher buttons per question (full worked solution / hint only / guided steps /
  mark my attempt), generated into `site/assets/site.js` from a Python string in `build.py`. They call
  `window.dpAI.open({ref, subject, marks, context, prompt, display, …})` — i.e. the **same** global
  widget in focused mode (§3·1), *not* a self-contained panel. "Mark my attempt" passes
  `autoSend:false` so the composer is prefilled with `MY ATTEMPT:` instead of sending. The question
  text rides along in `context`, so the widget is not limited to `questionId` grounding here.
- **Figures:** hand-authored inline SVG stored in the question JSON as
  `figure = {type:"svg", content, caption}`; `build.py::figure_html` requires `type:"svg"`.
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
2. **VS Code races git.** A 0-byte orphan `.git/index.lock` reappears and blocks commits. Confirm the orphan with `lsof .git/index.lock` (no holder), delete it, then add+commit in a **single** command.
3. **zsh is not bash.** Unquoted `--include=*.js` → `no matches found`; `for f in $FILES` does **not** word-split. Use the Grep tool or `grep -E`.
4. **A listening port is not a working service.** A wedged vite can hold `:5175` and 500 every request (it runs from a deleted node binary — check `lsof -p <pid> | awk '$4=="txt"{print $NF; exit}'` for `.deleting.`).
5. **`start.command` is not version-controlled** — repo A does not own `~/Downloads/dp learning/`.
6. **The qbank bundle must be built with `VITE_API_BASE_URL`**, or every API call 404s (see §5·02).
7. **`ib-dp-platform.netlify.app` is stale and has no Git connection** (`repo_url: None`), so pushes never reach it. The Cloudflare host is the current one. It **cannot be retired**, though — it is the only host with a `/figures` route (§4).
8. **Repointing `qbank/index.html` — change ONLY the hashed `<script type="module">` line.** The `ai-widget.js?v=2` line just below it is a separate concern; drop it and the shared widget goes missing.
9. **React `setState` is not synchronous.** `setCategory('past'); runSearch()` reads the *previous* render's value, so a filter silently needs two clicks. Pass the value you are about to set (`load(0, {category: c})`).
10. **The Bash tool's `grep` can silently return nothing** for patterns that demonstrably exist. Use the Grep tool.
11. **`agent-browser screenshot` takes `[selector] [path]`** — there is no `--path` flag; passing one fails with "Element not found" at exit 0.
12. **`/api/*` 403s a bare `urllib` request.** Send `User-Agent: Mozilla/5.0`.
13. **A second agent session may push to repo A mid-task.** Re-run `git ls-remote origin main` before pushing, and audit which paths the intervening commits touched before assuming your build is intact.
