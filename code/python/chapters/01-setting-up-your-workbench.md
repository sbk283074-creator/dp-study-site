---
chapter: 1
part: 1
title: Setting Up Your Python Workbench
summary: Install Python, run your first script, and build a workspace you will still be using at Chapter 39.
minutes: 30
tags: [installation, repl, vscode, pip]
---

Before you can write anything useful you need three things working: a Python interpreter, a
place to type code, and the ability to run a file. That's it. Everything else — frameworks,
databases, game engines — is built on top of those three. This chapter gets them working and
shows you the small set of commands you will type thousands of times.

## Installing Python

You need **Python 3.12 or newer**. Anything older is missing syntax used later in this book.

:::note Which installer
- **macOS** — install from [python.org](https://www.python.org/downloads/). Do *not* rely on the
  system Python that ships with macOS; it is old and Apple reserves it for the OS.
- **Windows** — install from [python.org](https://www.python.org/downloads/). In the installer,
  tick **"Add python.exe to PATH"**. This one checkbox prevents an hour of pain later.
- **Linux** — Python 3 is almost certainly installed. Check with `python3 --version`. If it is
  older than 3.12, use your distribution's packages or build from source.
:::

Verify the install by opening a terminal (Terminal on macOS/Linux, PowerShell on Windows):

```bash
python3 --version
```

```text
Python 3.13.2
```

:::pitfall `python` vs `python3`
On macOS and Linux, `python` often does not exist or points at Python 2, which is dead. Always
type `python3`. On Windows the launcher is usually `python`. Whichever you use, be consistent —
every command in this book uses `python3`, so if you are on Windows, read `python3` as `python`.
:::

## Your first thirty seconds: the REPL

The fastest way to check an idea is the **REPL** (Read–Eval–Print Loop): an interactive prompt
where Python evaluates what you type immediately.

```bash
python3
```

```text
Python 3.13.2 (main, Feb  4 2025, 00:00:00) [Clang 17.0.0] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

The `>>>` is the prompt. Type an expression, press Enter, and Python prints the result:

```python
>>> 2 + 3
5
>>> "hello".upper()
'HELLO'
>>> len("python")
6
```

Three things just happened that will matter forever:

1. `2 + 3` produced `5` — Python is a calculator when you need it to be.
2. `"hello".upper()` — values have **methods** you call with a dot. Text values know how to
   shout.
3. `len("python")` — **functions** take a value in parentheses and return a value back.

Type `exit()` to leave, or press `Ctrl-D` (macOS/Linux) / `Ctrl-Z` then Enter (Windows).

:::tip Use the REPL as a scratchpad, not a notebook
The REPL is for two-second experiments: "does this string method exist?", "what does this
return?". Anything you want to keep goes into a file. The REPL forgets everything the moment
you close it.
:::

## Your first real program

Create a folder for this chapter and a file called `hello.py`:

```bash
mkdir -p ~/python-mastery/01
cd ~/python-mastery/01
```

Open a text editor and type this in:

```python
# hello.py — my first program

name = input("What is your name? ")
print(f"Hello, {name}! Welcome to Python.")
print(f"Your name has {len(name)} characters.")
```

Save it, then run it from the terminal:

```bash
python3 hello.py
```

```text
What is your name? Ada
Hello, Ada! Welcome to Python.
Your name has 3 characters.
```

Take apart what happened:

- `name = input(...)` — `input()` pauses the program, waits for you to type, and returns your
  text as a string. The `=` **assigns** it to the name `name`.
- `f"Hello, {name}!"` — an **f-string**. The `f` before the quote tells Python to evaluate
  anything inside `{}` and drop the result into the string. You will use these constantly.
- `# hello.py — my first program` — a **comment**. Python ignores everything after `#`.

:::pitfall Naming the file `python.py`
Never name a file after a module you intend to import (`python.py`, `string.py`, `random.py`,
`json.py`). Python looks in the current folder first, so your file shadows the real one and you
get bizarre errors like `AttributeError: module 'random' has no attribute 'randint'`.
:::

## Choosing an editor

You can write Python in Notepad. You should not. A good editor catches your typos before you
run anything.

**VS Code** is the safe default and is what this book assumes:

1. Install [VS Code](https://code.visualstudio.com/).
2. Install the **Python** extension by Microsoft (the one with the blue snake).
3. Open your project folder: `code ~/python-mastery/01` (or File → Open Folder).
4. When prompted, select your Python 3.13 interpreter — VS Code shows it in the bottom-right.

Two features will save you immediately:

- **Run** — click the ▶ button in the top-right of the editor, or right-click and choose
  "Run Python File in Terminal".
- **Problems panel** — red squiggles under code that will not run. Hover them.

:::note Alternatives
PyCharm Community Edition is a heavier, fully-featured Python IDE and is excellent if you like
things done for you. Vim/Neovim, Sublime Text, and Zed are all fine. The editor matters far
less than whether you have installed its Python integration.
:::

## Installing packages with pip

Python ships with a large **standard library** — modules like `math`, `random`, `json`, and
`pathlib` that need no installation. Everything else comes from PyPI, the Python Package Index,
via `pip`:

```bash
python3 -m pip install requests
```

```text
Collecting requests
  Downloading requests-2.32.3-py3-none-any.whl (64 kB)
Successfully installed requests-2.32.3
```

Always write `python3 -m pip` rather than bare `pip`. It guarantees the package lands on the
same interpreter that `python3` runs.

```python
>>> import requests
>>> response = requests.get("https://api.github.com")
>>> response.status_code
200
```

You just made an HTTP request to GitHub's API. One `pip install` turned a two-line program into
something that talks to the internet — that leverage is why the Python ecosystem is so large.

:::warning Install into a virtual environment
Installing packages globally works, but it becomes a disaster the first time two projects need
different versions of the same library. Chapter 10 fixes this properly with virtual
environments. Until then, installing a few packages globally is fine while you learn.
:::

## Reading a traceback

Run this deliberately broken program:

```python
# broken.py
def greet(name):
    return f"Hello, {name.capitalizee()}"

print(greet("ada"))
```

```bash
python3 broken.py
```

```text
Traceback (most recent call last):
  File "/Users/you/python-mastery/01/broken.py", line 5, in <module>
    print(greet("ada"))
  File "/Users/you/python-mastery/01/broken.py", line 2, in greet
    return f"Hello, {name.capitalizee()}"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'capitalizee'
```

Read tracebacks **bottom-up**:

1. Last line: `AttributeError: 'str' object has no attribute 'capitalizee'` — the *what*. A
   string does not have `capitalizee`.
2. Above it: the exact line, with `^^^` pointing at the offending expression.
3. Above that: the chain of calls that got there — `print(...)` at line 5 called `greet(...)` at
   line 2.

The fix: the method is `capitalize()`, not `capitalizee()`. Ninety percent of debugging is
reading that last line carefully.

:::scenario You run your script and get "command not found: python3"
You installed Python, you saved `hello.py`, you type `python3 hello.py`, and the terminal
answers `command not found`. This is the single most common first-day failure, and it is never
actually about Python.
:::

:::solution It is almost always one of three things
1. **Python is not on your PATH.** You installed it but the terminal cannot find it. On Windows,
   re-run the installer, choose "Modify", and tick *Add python.exe to PATH*. On macOS, the
   python.org installer adds a `Python 3.x` folder to `/Applications` — run the
   `Install Certificates.command` inside it and restart your terminal.
2. **You are in the wrong folder.** `python3 hello.py` only works if the terminal's current
   directory contains `hello.py`. Run `pwd` (macOS/Linux) or `cd` (Windows) to see where you
   are, then `cd ~/python-mastery/01` to get to the right place. If Python *runs* but says
   `can't open file 'hello.py': No such file or directory`, this is your problem.
3. **You are in the REPL.** If your prompt starts with `>>>`, you are inside Python, not the
   shell. Type `exit()` first, then run the command.

The general skill here is *narrowing*: does the error come from the shell (cannot find the
program), from Python (cannot find the file), or from your code (traceback)? Each one has a
different fix, and the error message tells you which world you are in.
:::

## Key takeaways

- `python3 --version` confirms your interpreter; you need 3.12+.
- The REPL (`python3` with no arguments) is a scratchpad for instant experiments.
- Real programs live in `.py` files and run with `python3 filename.py` from the folder that
  contains them.
- `python3 -m pip install <package>` adds third-party libraries from PyPI.
- F-strings (`f"...{value}..."`) insert values into text; `#` starts a comment.
- Read tracebacks from the bottom up: the last line is the error, the line above is where it
  happened.

## Practice

- [ ] Install Python and confirm `python3 --version` reports 3.12 or newer.
- [ ] Run `python3` and use the REPL to compute `7 * 6`, `"python".replace("p", "P")`, and
      `len([1, 2, 3])`. Write down what each returns.
- [ ] Write `madlibs.py`: ask the user for a noun, a verb, and an adjective, then print a
      one-sentence story using an f-string.
- [ ] Write `broken.py` with a deliberate typo, run it, and identify the error type from the
      last line of the traceback. Fix it.
- [ ] Install a package with `python3 -m pip install rich`, then print a styled table with it.

## Solutions

:::solution Exercise 2
```python
>>> 7 * 6
42
>>> "python".replace("p", "P")
'Python'
>>> len([1, 2, 3])
3
```
`replace()` returns a *new* string — it does not change the original, because strings in Python
are immutable. `len()` works on anything with a length, including lists.
:::

:::solution Exercise 3
```python
# madlibs.py
noun = input("Give me a noun: ")
verb = input("Give me a verb: ")
adjective = input("Give me an adjective: ")

print(f"The {adjective} {noun} decided to {verb} right through the wall.")
```
Everything `input()` returns is a string, so no conversion is needed here. That changes the
moment you ask for a number — see Chapter 2.
:::

:::solution Exercise 4
Any typo works. A typical one:

```python
print("Hello".toupper())
```
```text
AttributeError: 'str' object has no attribute 'toupper'
```
The error type is `AttributeError` — you asked an object for something it does not have. The
correct method is `"Hello".upper()`.
:::

:::solution Exercise 5
```bash
python3 -m pip install rich
```
```python
# table.py
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Languages I am learning")
table.add_column("Language")
table.add_column("Difficulty", justify="right")
table.add_row("Python", "friendly")
table.add_row("SQL", "medium")
table.add_row("JavaScript", "chaotic")
console.print(table)
```
`from X import Y` pulls a specific name out of a module so you can use it without the prefix.
Chapter 10 covers the import system properly.
:::
