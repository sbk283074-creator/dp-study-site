---
chapter: 10
part: 2
title: Modules, Packages & Virtual Environments
summary: Split code across files and folders, control exactly what import does, and give every project its own isolated set of dependencies.
minutes: 40
tags: [import, modules, packages, venv, pip, project layout]
---

Everything you have written so far has lived in one file. That works up to about two hundred
lines, and then it stops working: you scroll past four functions to find the one you want, you
copy a helper into a second script because importing it seems complicated, and the copy drifts
from the original. Separately, every package you install with `pip` currently lands in one shared
pile, which is fine for learning and a genuine problem the first time two projects want different
versions of the same library. This chapter fixes both: how to split code into modules and
packages, and how to give each project its own private pile of packages.

## What `import` actually does

`import` is not a copy-paste of source code. It is three steps:

1. **Find** the file that matches the name, by searching a list of directories.
2. **Execute** that file top to bottom, once.
3. **Bind** a name in your namespace to the resulting module object.

Step 2 is the one people forget. A module is a *program that gets run*. Prove it:

```python
# noisy.py
print("noisy.py is executing")

def hello():
    return "hi"
```

```python
>>> import noisy
noisy.py is executing
>>> import noisy
>>> noisy.hello()
'hi'
```

The second `import noisy` printed nothing. Python caches executed modules in `sys.modules`, so
importing the same module fifty times runs its code exactly once and hands back the same object.
That is why module-level code is a bad place to open a database connection you want to reset in
tests — it happens once per process, whether you like it or not.

### The four import forms

```python
import math                    # bind "math"; use math.sqrt(2)
from math import sqrt          # bind "sqrt"; use sqrt(2)
import math as m               # bind "m";    use m.sqrt(2)
from math import *             # bind every public name — don't
```

The first two are the ones you will use daily. `import math` keeps the module prefix, so a reader
always sees where `sqrt` came from. `from math import sqrt` is nicer when a name is used a dozen
times in one file. Aliases (`import pandas as pd`) exist for two reasons: the module name is long,
or the short name is a convention the whole ecosystem follows (`np`, `pd`, `plt`).

:::pitfall `from x import *` steals names you did not expect
```python
from os import *
open("notes.txt")          # TypeError: open() missing required argument 'flags'
```
`os` defines its own low-level `open`, and `import *` silently rebound the builtin `open` to it.
Nothing warns you. Worse, when a reader sees `total(...)` in a file that star-imported three
modules, there is no way to tell which module supplied it. The only place star imports are
tolerated is a REPL session where you are experimenting. If you need many names, import the
module and use the prefix.
:::

## The module search path

When Python resolves `import json`, it walks `sys.path` in order and takes the first match.

```python
>>> import sys
>>> for entry in sys.path:
...     print(entry)
...
/Users/you/projects/shop
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages
```

Roughly, in order:

1. The directory of the script you ran (or the current directory for `python3 -m` and the REPL).
2. Anything in the `PYTHONPATH` environment variable.
3. The standard library.
4. `site-packages` — where `pip` installs third-party code.

That first entry is the source of an error that costs beginners hours.

:::pitfall Naming your file after a module you import
You are learning JSON, so you call your file `json.py`. You then write `import json` and get:

```text
AttributeError: module 'json' has no attribute 'dumps'
```

Your own file is first on `sys.path`, so `import json` imported *your* file, which has no
`dumps`. The same trap applies to `random.py`, `string.py`, `email.py`, `types.py`, and — once you
install libraries — `requests.py`, `pytest.py`, `fastapi.py`. Check with `print(json.__file__)`
if you suspect it. Rename your file; there is no workaround worth learning.
:::

## A module is just a file

Create two files in the same folder:

```python
# textkit.py
def shout(text):
    return text.upper() + "!"

def whisper(text):
    return text.lower() + "..."

DEFAULTS = {"tone": "loud"}
```

```python
# app.py
import textkit

print(textkit.shout("deploying"))
print(textkit.DEFAULTS)
```

```bash
python3 app.py
```

```text
DEPLOYING!
{'tone': 'loud'}
```

No configuration, no registration, no build step. A file in the same directory is an importable
module whose name is the filename without `.py`. Functions, classes, and constants defined at the
top level become attributes of the module object.

## `if __name__ == "__main__":`

Every module has a `__name__` variable. When you run a file directly, Python sets it to
`"__main__"`. When you import that same file, `__name__` is the module's name. Check it, and you
get a file that is both an importable library and a runnable script.

```python
# textkit.py
def shout(text):
    return text.upper() + "!"

def whisper(text):
    return text.lower() + "..."

if __name__ == "__main__":
    print(shout("running as a script"))
```

```python
# app.py
import textkit

print(textkit.shout("imported as a library"))
```

```bash
python3 textkit.py
python3 app.py
```

```text
RUNNING AS A SCRIPT!
IMPORTED AS A LIBRARY!
```

Without the guard, importing `textkit` from `app.py` would print the demo line as a side effect.
Put argument parsing, `print()` calls, and anything that *does* something below the guard. Keep
pure definitions above it. That single habit is what makes a file reusable.

When a script grows, move the body into a function and call it from the guard:

```python
def main():
    print(shout("running as a script"))

if __name__ == "__main__":
    main()
```

`main()` is importable, so it becomes testable — which matters from Chapter 11 onward.

## Packages

A package is a folder of modules. The folder needs an `__init__.py` file; in modern Python it can
be empty, but its presence is what tells Python the directory is importable.

```text
shop/
    __init__.py
    pricing.py
    catalog.py
    shipping/
        __init__.py
        rates.py
```

```python
# shop/pricing.py
TAX_RATE = 0.20

def with_tax(amount):
    return round(amount * (1 + TAX_RATE), 2)
```

```python
# shop/shipping/rates.py
def standard(weight_kg):
    return 4.99 if weight_kg < 1 else 4.99 + (weight_kg - 1) * 1.50
```

```python
# main.py
from shop import pricing
from shop.shipping import rates

print(pricing.with_tax(100))
print(rates.standard(2.5))
```

`__init__.py` can also re-export, so callers get a clean top-level API:

```python
# shop/__init__.py
from .pricing import with_tax
from .shipping.rates import standard

__all__ = ["with_tax", "standard"]
```

```python
from shop import with_tax, standard
```

`__all__` is the list of names `from shop import *` should export. Defining it is good manners
even if you never use star imports, because it documents the public surface.

### Absolute vs relative imports

Inside `shop/catalog.py`, these both reach `pricing`:

```python
from shop import pricing        # absolute — full path from the project root
from . import pricing           # relative — "the package I am in"
```

```python
from .pricing import with_tax           # sibling module
from .shipping.rates import standard    # nested subpackage
from .. import config                   # parent package
```

Use absolute imports by default: they keep working when you move a file, and the reader sees the
whole path. Relative imports save typing inside a package and have one real advantage — if you
rename the package, the internal imports still work. They only function inside a package; a
top-level script cannot do `from . import x` and will fail with
`ImportError: attempted relative import with no known parent package`.

## Circular imports

`a.py` imports from `b.py`, and `b.py` imports from `a.py`. Neither can finish executing, because
each is waiting on the other.

```python
# models.py
from notify import send_welcome      # runs while models is only half-built

class User:
    def create(self):
        send_welcome(self.email)
```

```python
# notify.py
from models import User              # models is not finished yet

def send_welcome(email):
    print(f"welcome {email}")
```

```text
ImportError: cannot import name 'User' from partially initialized module 'models'
(most likely due to a circular import)
```

Three ways out, in order of preference:

1. **Extract the shared thing into a third module.** Whatever both files need — a constant, a
   base class, a small type — moves to `common.py`, and both import from it. This is the real
   fix; a cycle almost always means your dependency graph has a missing node.
2. **Import the module, not the name.** `import models` inside `notify.py` binds the module
   object immediately and defers attribute lookup to call time, so it survives the half-built
   state. `from models import User` needs `User` to exist *right now*.
3. **Defer the import into the function.** Move `from notify import send_welcome` inside
   `User.create`. Works, but it hides a design problem — reach for it only when you cannot
   restructure.

## Virtual environments

The problem: one Python installation has one `site-packages`. Project A needs `requests` 2.28,
project B needs 2.32, and installing for B breaks A. Upgrading anything becomes a gamble, and
your `requirements.txt` lists fifty packages you never imported because they accumulated over two
years.

A virtual environment is a folder containing its own interpreter link and its own
`site-packages`. Create one per project:

```bash
python3 -m venv .venv
```

Activate it — this just prepends the environment's `bin` (or `Scripts`) directory to your `PATH`:

```bash
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows PowerShell
.venv\Scripts\activate.bat         # Windows cmd
```

```bash
(shop) $ which python3
/Users/you/projects/shop/.venv/bin/python3
(shop) $ python3 -m pip install requests
```

The `(shop)` prefix is the shell telling you the environment is active. To leave it:

```bash
deactivate
```

Naming it `.venv` is a convention editors and tools recognise; VS Code auto-detects it, and
Chapter 22 will have you add `.venv/` to `.gitignore` so you never commit a few thousand
dependency files.

:::pitfall You installed the package but your program still says ModuleNotFoundError
You ran `python3 -m pip install requests`, then ran your script, and got
`ModuleNotFoundError: No module named 'requests'`. Two usual causes:

1. **You forgot to activate the venv.** The install went into `.venv/`, but you launched the
   script with the system interpreter. Activate first, then install, then run.
2. **Your editor is using a different interpreter.** VS Code shows the selected interpreter in
   the bottom-right corner. If it says `Python 3.13.2 ('system')`, click it and pick the one
   inside `.venv`.

Confirm what you are running with `python3 -c "import sys; print(sys.prefix)"`. If that path is
not inside your project, you are not in the environment.
:::

## Installing and recording dependencies

Always install through the interpreter you intend to run:

```bash
python3 -m pip install requests rich
python3 -m pip freeze > requirements.txt
```

```text
# requirements.txt
certifi==2025.1.31
charset-normalizer==3.4.1
idna==3.10
markdown-it-py==3.0.0
pygments==2.19.1
requests==2.32.3
rich==13.9.4
urllib3==2.3.0
```

A teammate — or a deployment server in Chapter 29 — reproduces your environment with one line:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

`pip freeze` prints *everything* installed with exact versions, including the transitive
dependencies you did not ask for. For applications that is what you want: a fully pinned,
reproducible environment. Libraries you publish should list only their direct dependencies
loosely; Chapter 22 covers that difference.

## `pipx` for tools

Some packages are not libraries you import — they are commands you run. `black`, `ruff`,
`mypy`, `httpie`, `poetry`. Installing those into a project venv pollutes its
`requirements.txt` and risks version conflicts with your actual code. `pipx` gives each tool its
own environment and puts just the executable on your `PATH`.

```bash
python3 -m pip install pipx
python3 -m pipx ensurepath
pipx install black
black .
```

Rule of thumb: if the thing appears in an `import` statement, it belongs in the project venv. If
you only ever type its name in a terminal, install it with `pipx`.

## A sane project layout

**Flat layout** — modules at the root, next to the tests:

```text
invoice_tool/
    .venv/
    pricing.py
    billing.py
    main.py
    tests/
        test_pricing.py
    requirements.txt
    README.md
```

This works because `sys.path[0]` is the directory of the script you run, so `main.py` can do
`import pricing` with no ceremony. It is right for scripts, exercises, and small tools.

**`src/` layout** — the importable package lives one directory down:

```text
invoice_tool/
    .venv/
    src/
        invoice_tool/
            __init__.py
            pricing.py
            billing.py
            cli.py
    tests/
        test_pricing.py
    pyproject.toml
    README.md
```

Two benefits. The package is a real package with a real name, so it can be built and installed
(Chapter 22) without renaming anything. And tests cannot accidentally import the source folder
instead of the installed package — a subtle failure where your tests pass locally but the shipped
package is broken. The cost is that you must install your own code before importing it:

```bash
python3 -m pip install -e .
```

`-e` means "editable": Python imports your working directory, so edits take effect immediately.

For the rest of this book you will use a package directory, because Chapter 23's TaskForge CLI
and the FastAPI app in Chapters 26–27 are both real packages people install.

## Worked example: a small multi-file package

```text
textstats/
    __init__.py
    counts.py
    reading.py
    cli.py
sample.txt
```

```python
# textstats/counts.py
def words(text):
    return [word for word in text.split() if word]

def word_count(text):
    return len(words(text))

def char_count(text, ignore_spaces=True):
    return len(text.replace(" ", "")) if ignore_spaces else len(text)
```

```python
# textstats/reading.py
from .counts import word_count

WORDS_PER_MINUTE = 220

def reading_minutes(text):
    count = word_count(text)
    if count == 0:
        return 0
    return max(1, round(count / WORDS_PER_MINUTE))
```

```python
# textstats/__init__.py
from .counts import char_count, word_count
from .reading import reading_minutes

__all__ = ["word_count", "char_count", "reading_minutes"]
```

```python
# textstats/cli.py
import sys
from pathlib import Path

from . import char_count, reading_minutes, word_count


def main(argv):
    if len(argv) != 1:
        print("usage: python3 -m textstats.cli <file>")
        return 2

    path = Path(argv[0])
    if not path.exists():
        print(f"no such file: {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    print(f"words:    {word_count(text)}")
    print(f"chars:    {char_count(text)}")
    print(f"reading:  {reading_minutes(text)} min")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Run it as a module from the project root — `-m` sets `sys.path[0]` to the current directory, so
the package resolves:

```bash
python3 -m textstats.cli sample.txt
```

```text
words:    412
chars:    1903
reading:  2 min
```

Note the shape: each module has one job, `__init__.py` defines the public API, `cli.py` is the
only file that touches `sys.argv` and `print()`. When we add tests in Chapter 11, they will
import `textstats` and call `word_count` directly, never the CLI.

:::scenario "Works on my machine" — ModuleNotFoundError on your teammate's laptop
You push a project. Ten minutes later: *"I cloned it, installed requirements, and it crashes with
`ModuleNotFoundError: No module named 'textstats'`."* It runs perfectly for you.
:::

:::solution Fix the import root, not the imports
The cause is nearly always that `sys.path[0]` differs. You ran from the project root, so
`textstats/` was importable. Your teammate ran `python3 textstats/cli.py` from somewhere else, so
`sys.path[0]` became `textstats/`, and relative imports broke.

Pick one of these and write it in the README:

1. **Run as a module from the root:** `python3 -m textstats.cli sample.txt`. Zero installation,
   works for everyone.
2. **Install the package in editable mode:** add a `pyproject.toml` (Chapter 22), then
   `python3 -m pip install -e .` once per machine. Now `import textstats` works from any
   directory, and `python3 -m textstats.cli` works too.
3. **Provide an entry point** so the command is just `textstats sample.txt`.

What you must never do is "fix" it by appending to `sys.path` at the top of a file:

```python
import sys
sys.path.append("/Users/you/projects/textstats")   # no
```

That hardcodes one developer's machine into the source. If an import does not resolve, the
problem is how the program is being launched or installed — not the import statement.
:::

## Key takeaways

- `import` finds a file, executes it once, and binds a name to the resulting module object.
- A module is any `.py` file; a package is a folder with `__init__.py`; subpackages nest.
- `if __name__ == "__main__":` guards code that should only run when the file is executed
  directly, not when it is imported.
- Never name your own file after a module you import — `json.py` will shadow the real `json`.
- Absolute imports (`from shop import pricing`) are the default; relative imports (`.pricing`)
  are for siblings inside a package.
- Circular imports mean a missing module in your design; extract the shared code rather than
  deferring the import.
- One virtual environment per project, created with `python3 -m venv .venv` and activated before
  you install or run anything.
- `python3 -m pip freeze > requirements.txt` and `pip install -r requirements.txt` make an
  environment reproducible; `pipx` installs command-line tools outside your project.

## Practice

- [ ] Create `mathkit.py` with `add(a, b)`, `mul(a, b)`, and `mean(values)`. Import it from a
      second file and print the results. Add an `if __name__ == "__main__":` demo and run the
      file both directly and by import to see the difference.
- [ ] Create a venv in a scratch folder, activate it, install `rich`, run
      `python3 -c "import sys; print(sys.prefix)"`, then `deactivate` and run it again. Explain
      the two different paths.
- [ ] Build the `textstats` package exactly as shown and run it on a text file of your own. Add a
      `sentence_count()` function to `counts.py` and export it through `__init__.py`.
- [ ] Write two modules that import each other and trigger a real `ImportError`, then fix the
      cycle by extracting the shared constant into a third module.
- [ ] Turn `textstats` into a `src/` layout project with a `pyproject.toml`, install it with
      `python3 -m pip install -e .`, and confirm `import textstats` works from `/tmp`.

## Solutions

:::solution Exercise 1
```python
# mathkit.py
def add(a, b):
    return a + b

def mul(a, b):
    return a * b

def mean(values):
    return sum(values) / len(values)

if __name__ == "__main__":
    print(add(2, 3), mul(4, 5), mean([1, 2, 3]))
```
```python
# use_mathkit.py
import mathkit

print(mathkit.mean([10, 20, 31]))
```
```bash
python3 mathkit.py        # 5 20 2.0
python3 use_mathkit.py    # 20.333333333333332
```
Running `mathkit.py` directly sets `__name__` to `"__main__"`, so the demo runs. Importing it
sets `__name__` to `"mathkit"`, so it stays quiet.
:::

:::solution Exercise 2
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install rich
python3 -c "import sys; print(sys.prefix)"
# /Users/you/scratch/.venv
deactivate
python3 -c "import sys; print(sys.prefix)"
# /Library/Frameworks/Python.framework/Versions/3.13
```
`sys.prefix` is the root of the running interpreter. Inside the venv it points at `.venv`, so
`pip install` writes into `.venv/lib/python3.13/site-packages`. Outside it points at the system
Python, and installs land in the shared pile you are trying to avoid.
:::

:::solution Exercise 3
```python
# textstats/counts.py
def sentence_count(text):
    return sum(1 for ch in text if ch in ".!?")
```
```python
# textstats/__init__.py
from .counts import char_count, sentence_count, word_count
from .reading import reading_minutes

__all__ = ["word_count", "char_count", "sentence_count", "reading_minutes"]
```
Re-exporting in `__init__.py` means callers write `from textstats import sentence_count` instead
of knowing that the function lives in `counts.py`. You can move it between internal modules later
without breaking anyone.
:::

:::solution Exercise 4
```python
# a.py
from b import B_NAME
A_NAME = "a"
```
```python
# b.py
from a import A_NAME
B_NAME = "b"
```
```text
ImportError: cannot import name 'A_NAME' from partially initialized module 'a'
```
Fixed by extracting the shared value:
```python
# names.py
A_NAME = "a"
B_NAME = "b"
```
```python
# a.py
from names import B_NAME
```
```python
# b.py
from names import A_NAME
```
The cycle existed because both modules wanted the same data. Once that data has its own module,
the dependency graph becomes a simple fan-in shape with no loop.
:::

:::solution Exercise 5
```text
textstats/
    src/textstats/__init__.py
    src/textstats/counts.py
    src/textstats/reading.py
    src/textstats/cli.py
    tests/test_counts.py
    pyproject.toml
```
```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "textstats"
version = "0.1.0"
requires-python = ">=3.12"

[tool.setuptools.packages.find]
where = ["src"]
```
```bash
python3 -m pip install -e .
cd /tmp && python3 -c "import textstats; print(textstats.__file__)"
```
Editable install adds a link back to `src/textstats`, so `import textstats` resolves from any
directory while still using the code you are editing. Chapter 22 extends this file into a fully
publishable package.
:::
