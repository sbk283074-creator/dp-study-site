# dp-study-site — the whole structure

**Verified 2026-09-14 against the live site and both repos. Not recalled — checked.**
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
| `assets/ai-widget.js` | 54 KB | global **Ask AI** assistant + site navigator (chat, thinking split, copy, full-page mode) | `ib-dp-platform-api.pages.dev/api/ask` |
| `assets/tools-widget.js` | 52 KB | Formula Booklet + Scientific Calculator; injected *by* ai-widget.js | none |
| `assets/css/main.css` | 33 KB | site styling | — |
| `assets/js/app.js` | 24 KB | nav, search, page behaviour | — |
| `assets/js/search-index.js` | **1.68 MB** | pre-built search index (`tools/build_search_index.py`) | — |

Referenced by **absolute URL** (`https://sbk283074-creator.github.io/dp-study-site/assets/…`),
so editing the one file updates every page at once.

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
  break the **10,042** question images that use the relative-path figure class.
  (`ib-dp-images-a.pages.dev` also serves them, but *without* the `/figures/` prefix, so it is not a
  drop-in for `QuestionCard.tsx`.)
- **Data is unaffected by the split**: both hosts read the *same* Turso database
  (19 books / 17,273 questions as of 2026-09-14).
- **Pre-existing and unrelated:** `/figures/book2/...` (7,304 rows) 404s on *every* host — the Blob
  store never received those files.

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
- **AI — two affordances, both working:**
  - the shared global widget (`.dp-ai-launch`) → Cloudflare;
  - a per-question **"Ask AI"** button (`components/AskAI.tsx`; 50 on a search page) → Cloudflare
    `/api/ask`. It used to **vanish on click** — the Netlify host 404s `/api/ask/status`, and the
    component does `if (status && !status.configured) return null`. Fixed by `cb839d1`; verified live
    (panel opens with difficulty / length / model controls and a live quota line).
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
  — 224 questions.
- Builder: `challenge-bank/build.py` (55 KB) — emits the entire `site/`.
- Tooling: `challenge-bank/tools/*.py` — `validate.py` (43 KB), `make_figures.py` (40 KB), `fix_json.py`,
  `ship.py`, `coverage.py`, `difficulty_audit.py`, …
- Docs: `README.md`, `STANDARD.md`, `PLAN.md`, `AUDIT_*.md`.
- Output: `challenge-bank/site/` — `index.html` (121 KB), `q/` (224 question pages), one index per
  subject, `papers/`, `assets/site.js`.
- **AI:** a per-question **"Solve with AI"** panel, generated into `site/assets/site.js` from a Python
  string in `build.py`, calling **Cloudflare `/api/ask`**. Four modes: solution / hint / steps / mark.
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
  `--version`, sandboxed or not. Any Netlify redeploy must be run by the user in Terminal.

---

## 7. Traps that have already bitten

1. **`git push` can report a ref-lock failure and still have succeeded.** Trust `git ls-remote origin main`, not the error text.
2. **VS Code races git.** A 0-byte orphan `.git/index.lock` reappears and blocks commits. Confirm the orphan with `lsof .git/index.lock` (no holder), delete it, then add+commit in a **single** command.
3. **zsh is not bash.** Unquoted `--include=*.js` → `no matches found`; `for f in $FILES` does **not** word-split. Use the Grep tool or `grep -E`.
4. **A listening port is not a working service.** A wedged vite can hold `:5175` and 500 every request (it runs from a deleted node binary — check `lsof -p <pid> | awk '$4=="txt"{print $NF; exit}'` for `.deleting.`).
5. **`start.command` is not version-controlled** — repo A does not own `~/Downloads/dp learning/`.
6. **The qbank bundle must be built with `VITE_API_BASE_URL`**, or every API call 404s (see §5·02).
7. **`ib-dp-platform.netlify.app` is stale and has no Git connection** (`repo_url: None`), so pushes never reach it. The Cloudflare host is the current one.
