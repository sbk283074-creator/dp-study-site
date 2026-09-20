# CODE-PLAN.md — review against the repository

Checked 2026-09-20. Every claim below was tested against the working tree, git, or the live
site; nothing is inferred from the plan's own text.

> **Actioned the same day.** §8's list has been worked through — §10 is the resolution log, and it
> separates what is *fixed* from what was *written here but must be run locally* from the one item
> that is *still open* (the push). Read §10 before acting on §8.

**Verdict.** The plan is unusually good. The survey numbers are real, the architecture
decisions are sound, and P0/P1 are genuinely built — not just described. But **the progress
table marks work ✅ that has never been deployed**, and there are six places where the
document and the repository disagree. Two of them will break the next session's first
command.

---

## 1. What is real (verified, not assumed)

| Claim | Status | Evidence |
|---|---|---|
| `code/` skeleton exists | ✅ | `_build/{build.py 22 KB, languages.json, template.html, hub-template.html, assets/}` |
| Platform homepage | ✅ | `code/index.html`, 10,242 bytes, **14 language cards** |
| Python migrated | ✅ | `code/python/` — 40 chapters (1.30 MB), `parts.json`, `STYLE.md` |
| `verify/` migrated | ✅ | `code/verify/python/{taskforge, studyhub, shots, BUGS-taskforge.md}` |
| Registry | ✅ | `languages.json` — 7 `full` + 7 `mini`, `python` = `live`, rest `planned`; matches §4.1/§4.2 exactly |
| Progress preserved | ✅ | `python` keeps `store: "python-mastery-v1"` |
| Hub rewired | ✅ | all 4 places in §1.6 now `href="code/"`; **zero** `PYTHON/` references remain |
| `PYTHON/` redirect | ✅ | 1,544-byte page, `meta refresh` + `rel=canonical` → `../code/python/index.html` |
| **Problem A fixed** | ✅ | see §2 — and fixed better than the plan describes |
| Built book size | ✅ | 2,213,036 bytes = the plan's "2.21 MB"; chapters 1,298,182 = "1.3 MB" |
| Search index rebuilt | ✅ | `tools/build_search_index.py` already handles `code/python/index.html` |
| `STRUCTURE.md` updated | ✅ | documents the rebuild command, the redirect, and the Problem A lesson |

The hub's per-language progress bars read each track's own `localStorage` key, so the
aggregate view works without a backend. That is the right call and it is implemented.

---

## 2. Problem A is fixed, and better than the plan says

The plan worried that rebuilding would drop the two hand-edited `.tb-site` links. It would
have. The fix is in the template now:

- `_build/template.html` — 3 occurrences
- `_build/assets/style.css` — 2 occurrences

and the built book carries **three** links, not two:

```
class="tb-site" href="../../index.html"   ← DP Learning hub
class="tb-site" href="../../qbank/"       ← Question Bank
class="tb-site" href="../index.html"      ← CODE platform home
```

The third is new — the book now knows about the platform it sits in. `STRUCTURE.md` even
records the lesson ("Do not hand-edit any built `index.html`"). This is the plan's #1 risk
and it is genuinely closed.

---

## 3. The finding that matters: **P0 and P1 are not deployed**

```
local  HEAD : d524957  Restructure Python Mastery into CODE, a multi-language platform
remote HEAD : 0008c02  bpho: notation audit — the radical, and three faults it exposed
```

| URL | live status |
|---|---|
| `/code/` | **404** |
| `/code/python/` | **404** |
| `/PYTHON/` | 200 — still the **old 2.2 MB book** (title "Python Mastery", 2,212,526 bytes) |
| live hub link | still `href="PYTHON/"` |

So §0's ✅ for P0/P1 is accurate for the working tree and **false for the site**. Nothing
about the migration is visible to a reader yet, and the plan's stated premise — *"Python
成为子栏目，URL 稳定"* — is exactly the thing that has not been tested. Until `d524957` is
pushed, the live site is byte-identical to the pre-migration state.

This is the same failure the project already has a rule for: **"the profile is a claim; the
measurement is the fact."** A progress table is a claim. `curl` is the measurement.

---

## 4. Six places the document disagrees with the repository

### 4.1 The documented CLI does not exist — and this will break the next command

- `CODE-PLAN.md` §2: *"`build.py` ← 支持 `--lang`；或 `build.py --all`"*
- `STRUCTURE.md` line 280: *"`python3 build.py [--lang python]`"*

The argument is **positional**. Verified:

```
$ python3 build.py --lang python
no language '--lang' in languages.json
$ python3 build.py --all
no language '--all' in languages.json
```

Both exit immediately with an error. The real invocations are `build.py` (all tracks) and
`build.py python` (one). Fix both documents — a wrong first command is the most expensive
kind of documentation bug.

### 4.2 `languages.yaml` vs `languages.json`

§2's architecture diagram says `languages.yaml`. The file is `languages.json`, as §0 says.
Pick one; the diagram is wrong.

### 4.3 §0 and §6 are two different roadmaps

| | §0 progress table | §6 roadmap |
|---|---|---|
| phases | P0–P5 (six) | P0–P4 (five) |
| P2 | "C/C++ 赛道骨架 + 前几章" | "模板验证 — 用 1 个新语言跑完整条赛道" |
| P3 | "Java (+Kotlin) 赛道" | "扩语种 — 批量产出其余语言" |
| P4 | "TypeScript / C# / Go / Rust + 迷你赛道" | "终极项目 capstone" |

They disagree on both the count and the content. A reader cannot tell which is current.

### 4.4 §7 presents five decisions as open; all five are made

§7 is titled *"需要你拍板的决策"* and lists options 1A–5B. The document header says
*"决策已拍板（1A / 2B / 3A / 4A / 5A）"*. So §7 is stale — it should be retitled as the
decision **record**, with the chosen option marked, and ideally with the reason. As written
it invites the reader to re-litigate settled ground.

### 4.5 §1 is a pre-migration snapshot, labelled as current

§1.1 describes `PYTHON/python-mastery/` and `PYTHON/verify/`, and its *"是否入库"* column
explains which of those paths git tracks. **Neither path exists any more** — §0 says P1
moved them. The survey is good and worth keeping, but it needs a label: *"survey, 2026-09-19,
before the migration"*, or its paths need updating.

### 4.6 The promised drift check does not exist, and its target is gone

§8's mitigation for the top risk is *"加一条 'dist 与部署文件必须逐字节一致' 的检查"*. Two
problems: there is no `dist/` in the new layout — the build writes `code/<lang>/index.html`
and `code/index.html` **directly** — and no such check exists in `tools/`.

The property that actually matters now is **idempotence**: re-running the build must not
change the output. That is a one-liner and it is worth having, because the build is slow
(~2 min) and nobody will notice a silent drift by eye:

```sh
cd code/_build && python3 build.py && git diff --exit-code -- ../../
```

---

## 5. Arithmetic slips

- §1.7 Problem B says *"6 种语言 … 约 13 MB+"*, but §4.1 lists **7** full tracks. Seven ×
  2.21 MB ≈ **15.5 MB**. The conclusion (one file per language) is unaffected — it is
  *strengthened* — but the number is wrong.
- §8 says *"40 章 × 6 语言"*. With 7 full tracks that is **280 chapters** for the full
  tracks alone, before the 7 mini tracks. The risk estimate is understated by ~17%.
- §4.6 recommends starting with *"Java 或 C/C++"* and orders *"Java → C/C++ → …"*, but
  decision **2B** chose **C++** as the second track. The prose should follow the decision.

---

## 6. Naming debt

The hub's button and card still carry Python-specific class names for what is now the
platform entry:

```html
<a class="btn btn--platform-python" href="code/">Code Mastery</a>
<a class="platform-card platform-card--python" href="code/">
```

Harmless, but it will confuse the next person to touch the Hub CSS, and the same pattern
will be copied when a card is added for a second platform.

---

## 7. What could not be verified

**Byte-for-byte build reproducibility.** Running `code/_build/build.py` fails in this
environment after ~2 minutes:

```
PermissionError: Sensitive content approval timed out.
The operation was not authorized and was blocked.
  at build.py:342  raw = path.read_text(encoding="utf-8")   # inside load_chapters()
```

This is the file-access broker gating Python's `open()`, **not a defect in the repository** —
the same 40 files read fine through the shell (`wc -c chapters/*.md` → 1,298,182 bytes), and
`languages.json` is read successfully earlier in the same run. It happened both sandboxed
and escalated. **Run the byte comparison locally.**

What was verified instead, which is most of the substance: all **40** chapter front-matter
titles are present in the built book, and **0** of the 7 template placeholders
(`__DATA__`, `__NAV__`, `__CONTENT__`, `__STYLE__`, `__SCRIPT__`, `__PART_NAMES__`,
`__CARDS__`) survived unresolved.

---

## 8. Recommended order

1. **Push `d524957`.** Nothing is live. Then re-check `/code/` and `/code/python/` (expect
   200) and confirm `/PYTHON/` is now the 1.5 KB redirect rather than the 2.2 MB book.
2. **Fix the CLI in both documents** (§4.1) — `build.py python`, not `--lang python`.
3. **Add the idempotence check** (§4.6) — it is the plan's own top mitigation, restated for
   the layout that actually shipped.
4. **Reconcile §0 with §6**, and turn §7 into the decision record.
5. **Label §1 as a pre-migration survey.**
6. Fix the 6→7 arithmetic in §1.7 and §8; align §4.6 with decision 2B.
7. Rename the Hub's `--python` classes.

Items 1–3 are the ones that block the next session. Items 4–7 are documentation hygiene and
cost little.

---

## 9. One note on scope

The plan's §4.6 advice — *"先用 1 个 section 跑通整条赛道，再批量复制"* — is the single most
valuable line in the document, and it is worth defending. Seven full tracks at 40 chapters
each is ~280 chapters plus 21 project builds; the risk is not effort but **template defects
multiplied sevenfold**, which is exactly the failure the plan already suffered once with
Problem A. Run one track end to end, including its `verify/` implementation and its two
project builds, before a second track is started.

---

## 10. Resolution log (2026-09-20)

| §8 item | Status | What changed |
|---|---|---|
| 1. Push `d524957` | ⬜ **open** | Not done — it publishes to the live site, so it is waiting on Lucas's go-ahead. Nothing else in this log depends on it. |
| 2. Fix the CLI in both documents | ✅ **done** | `CODE-PLAN.md` §0 + §2 diagram + §2 design table, and `STRUCTURE.md` line 280. Both now say `build.py <lang-id>` (positional) and `languages.json`. |
| 3. Add the idempotence check | ✅ **written** | New `code/_build/check-idempotent.sh`, documented in `CODE-PLAN.md` §0 and §8 and in `STRUCTURE.md` §03. **Must be run locally** — see below. |
| 4. Reconcile §0 with §6; §7 → decision record | ✅ **done** | §6 rewritten to the same P0–P5 numbering as §0, with a 产出/前置 column and a "P2 is the gate" warning. §7 retitled 决策记录（已拍板）, each row marking the chosen option with its reason. |
| 5. Label §1 as a pre-migration survey | ✅ **done** | Warning banner under the §1 heading naming the dead paths and pointing to §2. |
| 6. Fix the 6→7 arithmetic; align §4.6 with 2B | ✅ **done** | §1.7 "6 种语言 ≈ 13 MB" → "7 个完整赛道 ≈ 15.5 MB+"; the drift multiplier 6× → 7 copies; §8 "40 章 × 6 语言" → "7 个完整赛道 ≈ 280 章 + 21 项目构建"; §4.6 order now **C/C++ → Java(+Kotlin) → TS → C# → Go → Rust**, citing decision 2B. |
| 7. Rename the Hub's `--python` classes | ✅ **done** | `btn--platform-python` → `btn--platform-code` and `platform-card--python` → `platform-card--code`, in `index.html` (2 sites) and `assets/css/main.css` (5 sites). The colour identity is unchanged; only the name moved. |

### The idempotence script

`code/_build/check-idempotent.sh` snapshots the SHA-256 of every built page, runs the build, then
compares. It covers `code/index.html` plus each `code/<lang>/index.html`, excluding `_build/` and
`verify/`. Both branches were exercised while writing it:

- a no-op build → `OK — idempotent … across 2 page(s)`, exit 0
- a build that appended a single byte → `FAIL`, exit 1, with the hash diff printed

**It cannot be fully run in this environment** — the `python3 build.py` step hits the same
file-broker `PermissionError` recorded in §7. Run it locally; exit 0 is the pass, and a failure
names the page that moved:

```sh
sh code/_build/check-idempotent.sh
```

### One correction to this review's own §6

§6 called the Hub's classes *"harmless"*. They were harmless to the **rendering** — but the rename
turned out to be load-bearing for the next author, because every other card is named for its
platform (`--core`, `--qbank`, `--litlab`, `--challenge`, `--bpho`, `--vocab`). A card called
`--python` for a platform called "Code Mastery" is exactly the inconsistency that gets copied.
Low priority, but now closed.

### A process note worth keeping

Editing a document with several parallel edits **silently drops all but one of them** — the §0, §1
and §8 edits landed while the co-batched §1.7, §2, §4.6, §6 and §7 edits vanished, with every call
reporting success. Apply same-file edits **one per message** and re-grep afterwards. This is the
same class of failure as the plan's own Problem A: a write that reports success is not a write that
persisted.
