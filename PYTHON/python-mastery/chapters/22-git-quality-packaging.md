---
chapter: 22
part: 3
title: Git, Code Quality & Packaging
summary: Put your work under version control, automate the quality checks a senior engineer runs, and turn a folder of scripts into a package other people can install.
minutes: 45
tags: [git, branching, ruff, mypy, pre-commit, pyproject.toml, semver, packaging]
---

Every program you have written so far lives in a folder and exists in exactly one state: the one
on disk right now. Change a file, and the previous version is gone. That is fine for a ninety-
line exercise and unacceptable for anything real, because the three questions you will actually
ask about code are "what did this look like last Thursday?", "which of us wrote this line?", and
"can I try a risky idea without destroying what works?". Version control answers all three. Then
once your code is safe, two more problems appear: keeping it *consistent* when more than one
person (or more than one mood) touches it, and getting it off your laptop. Git, automated
quality tooling, and packaging are the standard answers, in that order.

## What version control actually solves

You could version code by copying the folder: `app/`, `app-v2/`, `app-v2-final/`,
`app-v2-final-REALLY/`. Everyone does this once. It fails immediately: you cannot tell what
differs between two copies, you cannot merge two people's copies, and disk fills up with
guesswork.

Git stores a directed graph of **snapshots**. Each snapshot (a commit) records the full state of
the tree, a pointer to its parent, an author, a timestamp, and a message. Because snapshots are
content-addressed — identified by a hash of their contents — identical content is stored once,
so a hundred commits of a thousand-file project cost roughly the size of the files plus the
changes. That design gives you three things for free:

1. **History** — every state you ever committed is retrievable, forever.
2. **Attribution** — every line carries the commit that introduced it.
3. **Branches** — parallel lines of history that can be merged back together.

## Your first repository

```bash
mkdir -p ~/python-mastery/weather && cd ~/python-mastery/weather
git init
```

```text
Initialized empty Git repository in /Users/you/python-mastery/weather/.git/
```

That created a `.git/` directory holding the entire history database. You never edit it by hand.
Write a file:

```python
# weather.py
CITIES = {"Berlin": 12.5, "Lisbon": 21.0, "Oslo": 4.0}


def report(city: str) -> str:
    return f"{city}: {CITIES[city]}C"
```

Now ask git what it sees:

```bash
git status
```

```text
On branch main
No commits yet
Untracked files:
  (use "git add <file> ..." to include in what will be committed)
	weather.py

nothing added to commit but untracked files present
```

Git works in three areas. The **working tree** is your files. The **index** (also called the
staging area) is what the *next* commit will contain. The **repository** is the committed
history. You move files from working tree to index with `add`, and from index to repository with
`commit`:

```bash
git add weather.py
git commit -m "Add city temperature report"
```

```text
[main (root-commit) 8f3a1c2] Add city temperature report
 1 file changed, 4 insertions(+)
```

That `8f3a1c2` is the short hash of the commit — its permanent name.

Three more commands cover ninety percent of daily git use:

```bash
git log --oneline --graph --decorate   # history, compact
git diff                                # unstaged changes vs index
git diff --staged                       # index vs last commit
git show 8f3a1c2                        # one commit in full
```

`git diff` output reads as: lines starting with `-` were removed, lines with `+` were added,
`@@` headers tell you where. Learn to read it; it is how you review your own work before
inflicting it on anyone.

:::tip Commit small, commit often
A commit should be one coherent change that you could describe in a sentence and revert without
collateral damage. "Add temperature report plus rewrite the CLI plus fix a typo in the README"
is three commits pretending to be one. Small commits make `git bisect` — the binary search over
history that finds the commit that introduced a bug — genuinely useful instead of theoretical.
:::

## Commit messages that future-you can use

A commit message has a subject line, a blank line, and an optional body:

```text
Cap temperature lookups at 60 entries

The in-memory dict grew without bound on the shared deployment and the
process was OOM-killed twice last week. Cache eviction comes later; this
stops the bleeding.

Refs: OPS-441
```

Rules that matter:

- Subject in the imperative mood: "Add", "Fix", "Remove" — as if giving an order. Not "Added",
  not "Adds".
- Subject under ~72 characters, no trailing period.
- Blank line before the body. Tools parse this.
- The body explains **why**, not what. The diff already says what.

The test: six months from now, will this message tell you whether it is safe to revert? If it
says "fix" or "wip" or "changes", it will not, and you will have to read the whole diff to find
out.

## .gitignore

Git will happily track compiled bytecode, virtual environments, database files, and your API
keys if you let it. `.gitignore` lists path patterns git should never offer to commit:

```bash
cat > .gitignore <<'EOF'
# Python bytecode
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/

# Environments
.venv/
venv/
.env

# Local databases and caches
*.db
*.sqlite3
.coverage
.pytest_cache/
.ruff_cache/
.mypy_cache/

# Editors and OS
.vscode/
.idea/
.DS_Store
EOF
```

Patterns are matched against paths relative to the `.gitignore` file: `*.db` matches anywhere,
`/config.db` matches only at the root, `logs/` matches a directory at any depth, and a leading
`!` re-includes something previously excluded. When git ignores a file you wanted to add, ask
it why:

```bash
git check-ignore -v .venv/bin/python
```

```text
.gitignore:9:.venv/	.venv/bin/python
```

That tells you the rule and the line. `.gitignore` only affects *untracked* files — if a file is
already committed, ignoring it does nothing. Remove it from the index first with
`git rm --cached <file>`.

## Branching and merging

A branch is a movable pointer to a commit. `main` is just a branch that happens to be the
default name. You work on a branch so that half-finished work never touches the version everyone
else depends on.

```bash
git switch -c add-units          # create and switch (git checkout -b on older git)
git switch main                  # go back
git branch                       # list branches, * marks the current one
```

Do the work, commit it, then bring it back into `main`:

```bash
git switch main
git merge add-units
```

If `main` has not moved since you branched, git performs a **fast-forward**: it just slides the
`main` pointer forward. No new commit, no conflict possible. If `main` *has* moved, git creates a
**merge commit** with two parents.

### Resolving a merge conflict

A conflict happens when both sides changed the same region of the same file. Git stops and asks
you to decide:

```bash
git merge add-units
```

```text
Auto-merging weather.py
CONFLICT (content): Merge conflict in weather.py
Automatic merge failed; fix conflicts then commit the result.
```

Open the file. Git has written both versions into it, separated by markers:

```python
<<<<<<< HEAD
def report(city: str) -> str:
    return f"{city}: {CITIES[city]}C"
=======
def report(city: str, unit: str = "C") -> str:
    temp = CITIES[city]
    if unit == "F":
        temp = temp * 9 / 5 + 32
    return f"{city}: {temp}{unit}"
>>>>>>> add-units
```

Everything between `<<<<<<< HEAD` and `=======` is your current branch. Everything between
`=======` and `>>>>>>> add-units` is the incoming branch. Your job is to delete the markers and
leave the code that should exist. Here, take the incoming version and keep it:

```python
def report(city: str, unit: str = "C") -> str:
    temp = CITIES[city]
    if unit == "F":
        temp = temp * 9 / 5 + 32
    return f"{city}: {temp}{unit}"
```

Then:

```bash
git add weather.py
git commit          # pre-filled with a merge message; keep or edit
```

A conflict is not an error state — it is git refusing to guess. The resolution is always a human
decision about which behaviour is correct, which is why no tool can do it for you. Run your
tests after resolving; "it merges" and "it works" are different claims. To abandon a bad merge
entirely, `git merge --abort`.

## Stashing work in progress

You are mid-change and someone needs a fix on `main` now. You do not want a commit called "wip".

```bash
git stash push -m "half-done unit conversion"
git switch main
# ... fix, commit ...
git switch add-units
git stash pop
```

`git stash` shelves both staged and unstaged changes and restores a clean tree. `git stash list`
shows what is shelved; `git stash pop` reapplies the most recent one (and drops it),
`git stash apply` reapplies without dropping. Stashes are local and easy to forget — treat them
as a ten-minute parking space, not storage.

## Remotes: clone, push, pull

A **remote** is a named URL to another copy of the repository. By convention the primary one is
called `origin`.

```bash
git remote add origin git@github.com:you/weather.git
git push -u origin main       # -u sets upstream so later pushes are just `git push`
```

To get someone else's project:

```bash
git clone git@github.com:you/weather.git
cd weather                    # you now have full history locally
```

To incorporate their work:

```bash
git pull                      # fetch + merge
git pull --rebase             # fetch + replay your commits on top (cleaner history)
```

`git fetch` downloads objects without touching your working tree — safe to run any time. `pull`
changes files. If you have unpushed local commits and the remote has moved, a plain `pull`
creates a merge commit; `--rebase` avoids that by rewriting your commits to sit on top of the
new remote state. Rebase rewrites history, so never rebase commits you have already pushed and
told people about.

## The pull-request workflow

Almost nobody pushes straight to a shared `main`. The standard loop:

1. `git switch -c feat/unit-conversion`
2. Commit your work in small pieces.
3. `git push -u origin feat/unit-conversion`
4. Open a **pull request** (GitHub) / **merge request** (GitLab): a discussion page showing the
   diff, the commits, and the CI results.
5. Reviewers comment. You push more commits; the PR updates automatically.
6. CI (GitHub Actions) runs your tests, linter, and type checker on every push.
7. Merge: **merge commit** (keeps everything), **squash** (one commit on `main`, best for tidy
   history), or **rebase** (linear, no merge commit).

The PR is where code review happens, and the diff is the unit of review. Keep PRs small enough
that a human can actually read them; a 2,000-line PR gets an "lgtm" and no actual scrutiny.

## Code quality tooling

Style arguments are worthless; automated tools are not. Three tools cover the ground.

### ruff

Ruff is one Rust binary that lints *and* formats, replacing flake8, isort, pyupgrade, and
usually black.

```bash
python3 -m pip install ruff
ruff check .            # lint
ruff check . --fix      # lint and auto-fix what is safe
ruff format .           # format (black-compatible output)
```

```text
weather.py:5:1: F401 [*] `os` imported but unused
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

Configure it in `pyproject.toml`, not a separate `setup.cfg` / `.flake8` / `.isort.cfg` pile:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["B008"]
```

Those prefixes are rule families: `E`/`F` are pycodestyle and pyflakes errors, `I` sorts imports,
`UP` modernises syntax for your target Python, `B` is bugbear (likely bugs), `SIM` suggests
simplifications. Start with this set and widen it later.

### mypy

Chapter 16 introduced type hints. mypy checks them without running your code:

```bash
python3 -m pip install mypy
mypy src tests
```

```text
src/weather.py:9: error: Argument 1 has incompatible type "int"; expected "str"  [arg-type]
Found 1 error in 1 file (checked 3 source files)
```

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_unreachable = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
```

`strict = true` is the correct setting for new code. For an existing project, turn the flags on
one at a time or you will drown.

### pre-commit

A tool you install once and then forget, because it runs the other tools for you every time you
commit.

```bash
python3 -m pip install pre-commit
pre-commit install          # writes .git/hooks/pre-commit
pre-commit run --all-files  # run against everything, once
```

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies: [sqlalchemy>=2.0]
        files: ^src/
```

Pin every `rev` to a tag; an unpinned hook is a supply-chain surprise waiting for a bad morning.
`detect-private-key` is there precisely because of the pitfall at the end of this chapter.

## Docstrings and comments that earn their place

A comment should explain *why* the code is like this, when the code cannot say it:

```python
# Round half-up: the finance team's export must match their spreadsheet,
# which rounds 2.5 to 3, not to 2 like Python's built-in round().
total = int(Decimal(amount).quantize(0, ROUND_HALF_UP))
```

Comments that restate the code are noise and rot — the day someone changes the code and not the
comment, the comment becomes a lie. Delete them.

Docstrings describe the contract: what the function guarantees, what it requires, what it
raises. Use them on anything public.

```python
def complete_task(task_id: int, *, at: datetime | None = None) -> Task:
    """Mark a task done and stamp ``completed_at``.

    Raises:
        NotFoundError: no task with that id.
        ProjectArchivedError: the task's project is archived and frozen.
    """
```

## Semantic versioning

Version numbers are a contract, and SemVer (`MAJOR.MINOR.PATCH`) is the vocabulary:

| Change | Bump | Example |
| --- | --- | --- |
| Bug fix, no API change | PATCH | `0.1.0` → `0.1.1` |
| New feature, backwards compatible | MINOR | `0.1.1` → `0.2.0` |
| Breaking change | MAJOR | `0.2.0` → `1.0.0` |
| Anything, before public release | whatever | `0.x.y` — unstable, expect breaks |

Below `1.0.0` the rules are relaxed: anything may break at any time. Above `1.0.0` you are
promising that `pip install mylib>=1,<2` will never break a working program.

## pyproject.toml: one file for everything

Historically Python projects scattered config across `setup.py`, `setup.cfg`, `requirements.txt`,
`MANIFEST.in`, `.flake8`, `mypy.ini`, and `pytest.ini`. `pyproject.toml` replaces all of it. This
is the file you will write for the TaskForge project in Chapter 23:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "taskforge"
version = "0.1.0"
description = "A personal task manager for the command line"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = [
    "typer>=0.15",
    "sqlalchemy>=2.0",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
    "mypy>=1.14",
    "pre-commit>=4.0",
    "build>=1.2",
    "twine>=6.0",
]

[project.scripts]
taskforge = "taskforge.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/taskforge"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Key points:

- `[build-system]` tells pip *how* to build. `hatchling` is a simple modern backend; `setuptools`
  and `flit` are fine alternatives.
- `[project]` is metadata. `requires-python = ">=3.12"` is not decoration — pip will refuse to
  install on older interpreters instead of failing at import time.
- `[project.scripts]` creates a console command. Installing the package puts an executable
  `taskforge` on your PATH that calls `taskforge.cli:app`.
- Every tool you use adds a `[tool.X]` table to this same file.

Use `src/` layout (the package lives in `src/taskforge/`, not `taskforge/` at the root). It
forces you to test the *installed* package rather than accidentally importing the source folder
from your working directory — a bug class that has wasted a lot of afternoons.

## Building and publishing

```bash
python3 -m pip install build twine
python3 -m build
```

```text
Successfully built taskforge-0.1.0.tar.gz and taskforge-0.1.0-py3-none-any.whl
```

Two artefacts: an **sdist** (source tarball) and a **wheel** (pre-built zip that pip installs
without running your code). `py3-none-any` means any Python 3, no ABI, any platform — a pure
Python wheel.

Always rehearse on TestPyPI, a separate index that exists for exactly this:

```bash
python3 -m twine upload --repository testpypi dist/*
```

```text
Uploading distributions to https://test.pypi.org/legacy/
Enter your API token:
View at: https://test.pypi.org/project/taskforge/0.1.0/
```

Verify it installs from the test index in a clean environment:

```bash
python3 -m venv /tmp/verify && source /tmp/verify/bin/activate
python3 -m pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ taskforge
taskforge --help
```

The `--extra-index-url https://pypi.org/simple/` matters: TestPyPI does not host your
dependencies, so pip needs the real index to find `typer` and `sqlalchemy`.

Then the real thing:

```bash
python3 -m twine check dist/*
python3 -m twine upload dist/*
```

:::warning You cannot overwrite a version
PyPI rejects a re-upload of an existing version, deliberately: someone may already have that
exact artefact pinned. Bump the version (or use `1.0.0rc1`, `1.0.0.dev1` — PEP 440 pre-release
and dev suffixes) and upload again. This is also why you rehearse on TestPyPI.
:::

## Tagging releases

A tag is a permanent, human-readable name for one commit:

```bash
git tag -a v0.1.0 -m "First public release"
git push origin v0.1.0        # tags are NOT pushed by `git push` by default
git tag                       # list
```

Annotated tags (`-a`) carry an author, date, and message; lightweight tags are just a pointer.
Use annotated. Tag the commit *after* you bump the version in `pyproject.toml`, so the tag and
the version agree, and let CI build and upload when a tag is pushed rather than uploading by
hand every time.

:::scenario Your branch conflicts with a teammate's, on a file you did not write
You branch off `main` on Monday to add unit conversion. On Tuesday Priya refactors `weather.py`
onto `main` — same file, same functions. Wednesday you run `git merge main` and git reports a
conflict in a function you have never read. The markers are forty lines long and you cannot tell
which side is which.
:::

:::solution Narrow it, do not guess
1. **See the whole picture first.** `git log --oneline --graph --all` shows you where the
   branches diverged. `git diff main...HEAD` shows everything you changed since the split;
   `git diff HEAD...main` shows everything *they* changed. Read theirs before touching the file.
2. **Ask git to explain the conflict.** `git checkout --conflict=diff3 weather.py` rewrites the
   markers with a third section, `|||||||`, showing the common ancestor. Now you can see what
   each side started from, and the resolution is usually obvious.
3. **Take a whole side when you can.** `git checkout --ours weather.py` or
   `git checkout --theirs weather.py` discards one version entirely. Use it when you know one
   side is strictly better; hand-edit when both contain real work.
4. **Prove it.** Run the test suite. A conflict resolved by guessing compiles and still breaks
   behaviour, and no reviewer will spot it in a 600-line diff.
5. **Prevent the category.** Keep branches short-lived, pull from `main` daily, and keep
   functions small so two people rarely edit the same twenty lines. Process beats heroics.

If the merge is going badly, `git merge --abort` returns you to a clean tree. Nothing is lost —
that is the entire point of the tool.
:::

:::pitfall Committing secrets or `.venv/`
Two mistakes that look small and are not.

**`.venv/`** — a virtual environment is 30–200 MB of third-party code pinned to *your* operating
system and CPU. Committing it means every clone is enormous, every `git status` is polluted, and
the day someone else opens the repo on another platform it silently does not work. Put `.venv/`
in `.gitignore` **before your first commit**, and record dependencies in `pyproject.toml` so
anyone can rebuild the environment with one command.

**Secrets** — a `.env` file, an API key pasted into a config file, a database URL with a
password. The moment you `git push`, assume it is public: automated scrapers watch public
repositories and find credentials in minutes, not days.

Here is the part people get wrong. Deleting the file in a new commit does **not** fix it. The
secret is still in the previous commit, and the commit is still in history; `git log -p`, forks,
clones, CI caches and GitHub's own commit view will all show it. Rewriting history with
`git filter-repo` (or BFG Repo-Cleaner) can scrub it from *your* repository, and you must force-
push the rewrite — but by then the secret may already be in someone's clone, in a CI log, or in
a fork you do not control. Rewriting is cleanup, not remediation.

**Rotate the credential.** Revoke the key, generate a new one, deploy it through your normal
secret mechanism, then check the provider's access logs for use you do not recognise. Do this
first, before any git archaeology. Then, as prevention: `.env` in `.gitignore`, a committed
`.env.example` documenting the variable names with dummy values, the `detect-private-key`
pre-commit hook, and secret scanning (GitHub push protection) enabled on the repository.
:::

## Key takeaways

- `git init`, `git add`, `git commit` move work from the working tree through the index into
  permanent history; `git status`, `git log` and `git diff` are how you inspect all three.
- A commit should be one revertible change, with an imperative subject line and a body that
  explains why.
- `.gitignore` prevents untracked junk from being committed, but never hides a file git already
  tracks — use `git rm --cached` for that.
- Branches are cheap pointers; merges either fast-forward or create a merge commit, and a
  conflict is git refusing to guess, resolved by editing out the markers and running the tests.
- `ruff` (lint + format), `mypy` (types) and `pre-commit` (run them automatically) replace
  arguments about style with commands.
- `pyproject.toml` holds project metadata, dependencies, and every tool's configuration.
- `python3 -m build` produces an sdist and a wheel; rehearse on TestPyPI, then publish to PyPI,
  and remember that versions can never be re-uploaded.
- A leaked secret is fixed by rotating it, not by rewriting history.

## Practice

- [ ] Create a repository from a project you built in Chapter 20. Make three separate commits
      (one per logical change) and inspect the result with `git log --oneline --graph`.
- [ ] Add the `.gitignore` from this chapter and verify with `git check-ignore -v` that
      `.venv/bin/python` and `app.db` are both ignored.
- [ ] Create a branch, change a line that also exists on `main`, merge, and resolve the
      conflict by hand. Then run `git checkout --conflict=diff3 <file>` on a second conflict and
      note how the ancestor section helps.
- [ ] Install `ruff` and `mypy` on that project, add both `[tool.*]` tables to
      `pyproject.toml`, and fix every finding (or justify each `noqa` in a comment).
- [ ] Set up `pre-commit` with the three repos from this chapter and confirm that a commit with
      trailing whitespace is rejected and then auto-fixed on retry.
- [ ] Package a small utility as `greettool` with `[project.scripts]`, build it, upload it to
      TestPyPI, and install it into a throwaway virtual environment to prove the console command
      works.

## Solutions

:::solution Exercise 1
```bash
cd ~/python-mastery/renamer
git init
git add renamer.py && git commit -m "Add bulk renamer with dry-run support"
# edit README
git add README.md && git commit -m "Document the dry-run flag"
# edit renamer.py
git add renamer.py && git commit -m "Skip hidden files during rename"
git log --oneline --graph
```
```text
* 5c1d8aa (HEAD -> main) Skip hidden files during rename
* 2b7f104 Document the dry-run flag
* 9e3a771 Add bulk renamer with dry-run support
```
Three commits instead of one means you can revert "Skip hidden files" without losing the
README, and `git show 2b7f104` shows exactly one change. Staging per file is what makes this
possible; `git add -A` before every commit collapses everything into one blob.
:::

:::solution Exercise 2
```bash
git check-ignore -v .venv/bin/python
git check-ignore -v app.db
```
```text
.gitignore:9:.venv/	.venv/bin/python
.gitignore:14:*.db	app.db
```
The output is `source-file:line:pattern<TAB>path`, so you learn not just *that* a file is
ignored but *which line* did it — which is how you debug a pattern that is too greedy. If a
`.db` file still shows up in `git status`, it was committed earlier; untrack it with
`git rm --cached app.db` and commit that removal.
:::

:::solution Exercise 3
```bash
git switch -c change-greeting
# edit line 3 of app.py to: GREETING = "Hi"
git add app.py && git commit -m "Use a friendlier greeting"
git switch main
# edit the same line to: GREETING = "Hello there"
git add app.py && git commit -m "Make greeting configurable"
git merge change-greeting
```
```text
Auto-merging app.py
CONFLICT (content): Merge conflict in app.py
```
```python
<<<<<<< HEAD
GREETING = "Hello there"
=======
GREETING = "Hi"
>>>>>>> change-greeting
```
Resolve to `GREETING = "Hello there"` (keep `main`'s wording), delete the markers, then
`git add app.py && git commit`. The `--conflict=diff3` variant adds the original
`GREETING = "Hello"`, making it obvious that *both* sides edited the same line rather than one
side adding a new one — a different situation with a different correct answer.
:::

:::solution Exercise 4
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
```
```bash
python3 -m pip install ruff mypy
ruff check . --fix && ruff format .
mypy src
```
Fix findings in this order: `F` (real bugs — unused imports, undefined names), then `E`/`I`
(cosmetic, auto-fixable), then `B`/`SIM` (judgement calls). For a false positive, write
`value = transform(x)  # noqa: SIM108 -- the if/else documents the two cases` — always with a
reason, because a bare `noqa` is a suppressed bug with extra steps. `mypy` findings are the ones
worth arguing with: if the annotation is wrong, fix the annotation; if the logic is wrong, the
type checker just found a real bug.
:::

:::solution Exercise 5
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: detect-private-key
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        files: ^src/
```
```bash
pre-commit install
git add .pre-commit-config.yaml && git commit -m "Add pre-commit hooks"
# add trailing whitespace to a file
git add app.py && git commit -m "demo"
```
```text
trim trailing whitespace.................................................Failed
- hook id: trailing-whitespace
- files were modified by this hook
```
The first failure rewrites the file in place and aborts the commit; `git add app.py &&
git commit` now succeeds. That two-step is normal and intentional — hooks that modify files
must fail so you can review what they changed before it is committed.
:::

:::solution Exercise 6
```toml
[project]
name = "greettool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
greet = "greettool:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/greettool"]
```
```python
# src/greettool/__init__.py
"""greettool — say hello from the command line."""


def main() -> None:
    print("Hello from greettool!")
```
```bash
python3 -m build
python3 -m twine upload --repository testpypi dist/*
python3 -m venv /tmp/verify && source /tmp/verify/bin/activate
python3 -m pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ greettool
greet
```
```text
Hello from greettool!
```
The point of the clean-venv check is that it catches packaging mistakes a local import hides: a
missing `[tool.hatch.build.targets.wheel] packages` entry builds a wheel with no code in it, and
`import greettool` from the project root would have worked anyway. Always verify the artefact,
never your source tree.
:::
