---
chapter: 20
part: 3
title: Automation & CLI Tools
summary: Turn a script only you can run into a tool anyone can: argument parsing, exit codes, real logging, safe file operations, scheduled runs. Build a folder-tidying CLI that reports what it did and is safe to run twice.
minutes: 45
tags: [argparse, logging, cron, automation]
---

A script is something you run. A tool is something someone else can run, on a different machine, at
three in the morning, without you. The gap between them is not cleverness — it is five boring
things: arguments instead of hard-coded paths, exit codes the caller can check, logging instead of
`print`, operations that are safe to repeat, and error messages that say what to do next. Get those
right and a 60-line script becomes infrastructure. Skip them and your automation is one laptop
sleep away from failing silently.

## What separates a script from a tool

Before writing a line, decide which of these you have:

- **Arguments.** Paths, thresholds, and modes come from the command line, not from edits to the
  file. Nobody should have to open the source to change a folder.
- **Exit codes.** The process tells the caller whether it worked. This is the entire contract with
  cron, CI, and shell `&&`.
- **Logging.** Timestamped, levelled, routable to a file. `print` is for the user; logging is for
  whoever has to explain what happened at 03:00.
- **Idempotency.** Running it twice does the same thing as running it once. If a half-finished run
  leaves the world in a worse state than when it started, it is not a tool.
- **Clear errors.** `FileNotFoundError: [Errno 2] ... 'invoices.csv'` tells you nothing actionable.
  `No such file: /data/invoices.csv — pass --input or set TIDY_INPUT` tells you exactly what to do.

Everything below builds one tool, `tidy.py`, that organises a messy downloads folder and reports
what it did.

## argparse: the standard-library answer

`argparse` does three jobs: it parses `sys.argv`, it converts strings into the types you want, and
it generates `--help`. Start with the smallest version that is useful.

```python
#!/usr/bin/env python3
"""tidy.py - organise a folder into subfolders by file type."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tidy",
        description="Organise a messy folder into subfolders by file type.",
    )
    parser.add_argument("source", type=Path, help="folder to organise")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, move nothing")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    print(f"would organise {args.source} (dry run: {args.dry_run})")
```

Two details already. `type=Path` means `args.source` is a `Path`, not a `str` — any callable that
takes a string and returns a value (or raises) works as `type`, so `type=int`, `type=float`, and
`type=Path` all just work. And `action="store_true"` makes `--dry-run` a boolean flag defaulting to
`False`; there is no value to pass.

### Optional arguments, choices, defaults

```python
parser.add_argument("--dest", type=Path, default=None,
                    help="where to create the type folders (default: inside SOURCE)")
parser.add_argument("--min-size", type=int, default=0, metavar="BYTES",
                    help="skip files smaller than this")
parser.add_argument("--format", choices=("text", "markdown", "html"), default="text",
                    help="report format (default: text)")
parser.add_argument("-n", "--limit", type=int, default=None, help="stop after N files")
```

`choices` gives you validation and a free error message for nothing. `metavar` changes what appears
in `--help` without changing the attribute name — worth using whenever the value has a unit. Short
and long option names (`-n`/`--limit`) are cheap; add them for the options people actually type.

The generated help is the interface most people will see, so read it once:

```text
$ python3 tidy.py --help
usage: tidy [-h] [--dest DEST] [--min-size BYTES] [--format {text,markdown,html}]
            [-n LIMIT] [--dry-run]
            SOURCE

Organise a messy folder into subfolders by file type.

positional arguments:
  SOURCE                folder to organise

options:
  -h, --help            show this help message and exit
  --dest DEST           where to create the type folders (default: inside SOURCE)
  --min-size BYTES      skip files smaller than this
  --format {text,markdown,html}
                        report format (default: text)
  -n LIMIT              stop after N files
  --dry-run             print the plan, move nothing
```

### nargs: a variable number of values

Use `nargs` when an option takes a list. `"*"` means zero or more, `"+"` means at least one, and
`argparse.REMAINDER` grabs whatever is left.

```python
parser.add_argument("--exclude", nargs="*", default=[], metavar="NAME",
                    help="filenames to leave alone")
parser.add_argument("paths", nargs="+", type=Path, help="one or more folders")
```

```bash
python3 tidy.py ~/Downloads ~/Desktop --exclude README.md notes.txt --dry-run
```

### Subcommands with add_subparsers

Once a tool does more than one thing, subcommands beat a pile of unrelated flags. Every real CLI
you use works this way: `git commit`, `pip install`, `alembic upgrade`.

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tidy",
        description="Organise a folder, report on data, and notify someone.",
        epilog="examples:\n"
               "  tidy organise ~/Downloads --dry-run\n"
               "  tidy report sales.csv -o report.md\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="tidy 1.0")

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    organise = sub.add_parser("organise", help="move files into folders by type")
    organise.add_argument("source", type=Path, help="folder to organise")
    organise.add_argument("--dest", type=Path, default=None)
    organise.add_argument("--dry-run", action="store_true", help="print the plan, move nothing")
    organise.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    organise.add_argument("-q", "--quiet", action="store_true", help="warnings and errors only")
    organise.add_argument("--log-file", type=Path, default=None, help="also log here")

    report = sub.add_parser("report", help="summarise a CSV as Markdown or HTML")
    report.add_argument("csv_path", type=Path, help="CSV to read")
    report.add_argument("-o", "--output", type=Path, default=Path("report.md"))
    report.add_argument("--format", choices=("markdown", "html"), default="markdown")
    report.add_argument("--webhook", default=None, help="URL to POST the summary to")

    return parser
```

`dest="command"` stores which subcommand was chosen in `args.command`; `required=True` turns a bare
`tidy` into a usage error instead of a `NoneType` crash. `RawDescriptionHelpFormatter` keeps the
line breaks in your `epilog`, which is the difference between an example block people read and a
paragraph they skip.

Dispatch on it:

```python
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "organise":
        return cmd_organise(args)
    return cmd_report(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

Taking `argv` as a parameter costs nothing and makes the CLI testable — pass `["organise", "tmp"]`
from a test instead of monkeypatching `sys.argv`, exactly as you saw in Chapter 17.

## The same tool with click or typer

`argparse` is verbose because it is explicit. `click` and `typer` get the same result from
decorators, and the help text comes from the docstring.

```python
import pathlib

import click


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
@click.option("--dest", type=click.Path(path_type=pathlib.Path), default=None)
@click.option("--dry-run", is_flag=True, help="print the plan, move nothing")
def organise(source: pathlib.Path, dest: pathlib.Path | None, dry_run: bool) -> None:
    """Organise SOURCE into folders by file type."""
    root = dest or source
    for path in sorted(source.iterdir()):
        if path.is_file():
            click.echo(f"{path.name} -> {root / (path.suffix.lstrip('.') or 'other')}")


if __name__ == "__main__":
    organise()
```

`typer` is the same idea with type hints doing the work — and if you have read Chapter 16, the
signatures will look familiar:

```python
import pathlib
from typing import Optional

import typer

app = typer.Typer()


@app.command()
def organise(
    source: pathlib.Path = typer.Argument(..., exists=True, file_okay=False),
    dest: Optional[pathlib.Path] = typer.Option(None, "--dest"),
    dry_run: bool = typer.Option(False, "--dry-run", help="print the plan, move nothing"),
) -> None:
    """Organise SOURCE into folders by file type."""
    root = dest or source
    for path in sorted(source.iterdir()):
        if path.is_file():
            print(f"{path.name} -> {root / (path.suffix.lstrip('.') or 'other')}")


if __name__ == "__main__":
    app()
```

Reach for them when the tool grows past a couple of subcommands, or when you want shell completion,
prompts, password input, or colour output for free. Stay with `argparse` on machines where you
cannot install anything — a cron box, a CI image, a colleague's locked-down laptop.

## Exit codes: the contract with everything upstream

Zero means success. Anything else means failure. That is the whole protocol, and it is how `&&`,
`make`, cron, and CI decide what to do next.

| Code | Meaning |
| --- | --- |
| `0` | success |
| `1` | the program ran but failed (file missing, network down) |
| `2` | usage error — bad arguments; `argparse` exits with this itself |

Return the code from `main()` and let `SystemExit` carry it:

```python
import sys


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return cmd_organise(args)
    except TidyError as exc:
        print(f"tidy: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

Errors go to **stderr**, results go to **stdout**. Keep them separate and `tidy report data.csv >
report.md` still gives you a readable report while the error surfaces on the terminal instead of
being piped into the file.

## Logging: why print is not enough

`print` has no level, no timestamp, no destination control, and no way to turn it off. Once the tool
runs unattended you need all four.

```python
import logging
import sys
from pathlib import Path

logger = logging.getLogger("tidy")     # module-level, never the root logger


def configure_logging(verbose: bool, quiet: bool, log_file: Path | None = None) -> None:
    level = logging.DEBUG if verbose else logging.WARNING if quiet else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
```

Log to **stderr** so `--output -` and shell redirection keep working, configure **once** in `main`,
and use `%(name)s` so you know which module spoke. Then use the logger the way it was designed:

```python
logger.debug("scanning %s", source)          # development detail
logger.info("moved %s -> %s", src.name, dst) # normal work
logger.warning("skipped %s: unreadable", p)  # survived, but look at it
logger.error("cannot write to %s", dest)     # this run is compromised

try:
    shutil.move(src, dst)
except OSError:
    logger.exception("failed to move %s", src)   # ERROR + traceback, inside except only
    raise                                        # main() turns this into exit code 1
```

`logger.exception` is `logger.error` plus the traceback, and it only makes sense inside an `except`
block. Use lazy `%s` formatting — `logger.info("moved %s", name)` — because the string is only built
if the record is actually emitted; an f-string is built on every call even when the level is off.

:::pitfall logging.basicConfig() silently does nothing
Call `basicConfig()` twice and the second call is ignored, because the root logger already has
handlers. In a test that configures logging in a fixture, or a script run twice in one process,
your `--verbose` flag appears to have no effect. Pass `force=True` (Python 3.8+) to replace the
existing handlers, or attach handlers to your own logger instead of the root.
:::

## The actual work: pathlib plus shutil

Now the tool does something. Categories, then a collision-safe target, then the move.

```python
from __future__ import annotations

import itertools
import shutil
from pathlib import Path

CATEGORIES: dict[str, tuple[str, ...]] = {
    "images": (".png", ".jpg", ".jpeg", ".gif", ".heic", ".webp", ".svg"),
    "documents": (".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"),
    "spreadsheets": (".xls", ".xlsx", ".csv", ".numbers"),
    "archives": (".zip", ".tar", ".gz", ".7z", ".dmg", ".pkg"),
    "code": (".py", ".js", ".ts", ".json", ".toml", ".yaml", ".yml", ".sh"),
    "media": (".mp4", ".mov", ".mp3", ".m4a", ".wav"),
}
LOOKUP = {ext: name for name, exts in CATEGORIES.items() for ext in exts}


def category_for(path: Path) -> str:
    if path.name.startswith("."):
        return "hidden"
    return LOOKUP.get(path.suffix.lower(), "other")


def unique_target(target: Path) -> Path:
    """Return a path that does not exist yet: report.pdf -> report (1).pdf."""
    if not target.exists():
        return target
    for counter in itertools.count(1):
        candidate = target.with_name(f"{target.stem} ({counter}){target.suffix}")
        if not candidate.exists():
            return candidate


def plan_moves(source: Path, dest_root: Path) -> list[tuple[Path, Path]]:
    """Decide every move first, touch nothing. Directories are left alone."""
    return [
        (path, unique_target(dest_root / category_for(path) / path.name))
        for path in sorted(source.iterdir())
        if path.is_file()
    ]


def apply_moves(moves: list[tuple[Path, Path]], *, dry_run: bool) -> int:
    moved = 0
    for src, dst in moves:
        if dry_run:
            print(f"would move  {src.name}  ->  {dst}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dst)
        logger.info("moved %s -> %s", src.name, dst)
        moved += 1
    return moved
```

Three properties are deliberate. `plan_moves` is pure — it returns a list and touches nothing — so
`--dry-run` is just "print the plan instead of applying it". `unique_target` makes collisions
impossible instead of letting `shutil.move` overwrite a file that already had that name. And because
only top-level files are considered, a second run skips the folders it created and finds nothing to
move — idempotent by construction rather than by luck.

## Configuration: env vars, .env, and precedence

Secrets and machine-specific paths never go in the source. Read them from the environment and give
them one home — a frozen dataclass, as in Chapter 16.

```text
# .env  (commit .env.example, never .env itself)
TIDY_SOURCE=/Users/you/Downloads
TIDY_WEBHOOK_URL=https://hooks.example.com/services/T000/B000/XXXX
TIDY_SMTP_USER=reports@example.com
TIDY_SMTP_PASSWORD=abcdefghijklmnop      # an APP PASSWORD, not your account password
TIDY_NOTIFY_TO=you@example.com,team@example.com
```

```python
import os
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class Config:
    source: Path = Path("~/Downloads")
    webhook_url: str | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    notify_to: tuple[str, ...] = ()

    @classmethod
    def from_env(cls, prefix: str = "TIDY_") -> "Config":
        return cls(
            source=Path(os.environ.get(f"{prefix}SOURCE", "~/Downloads")).expanduser(),
            webhook_url=os.environ.get(f"{prefix}WEBHOOK_URL"),
            smtp_user=os.environ.get(f"{prefix}SMTP_USER"),
            smtp_password=os.environ.get(f"{prefix}SMTP_PASSWORD"),
            notify_to=tuple(
                addr.strip()
                for addr in os.environ.get(f"{prefix}NOTIFY_TO", "").split(",")
                if addr.strip()
            ),
        )


def merge(base: Config, **cli: object) -> Config:
    """CLI values win, but only the ones the user actually supplied."""
    return replace(base, **{k: v for k, v in cli.items() if v is not None})
```

```bash
python3 -m pip install python-dotenv
```

```python
from dotenv import load_dotenv

load_dotenv()          # reads .env into os.environ; does NOT override real env vars
config = Config.from_env()
```

The precedence rule, highest to lowest: **command-line flags → real environment variables → `.env`
file → dataclass defaults**. A flag is a deliberate one-off decision, the environment is how the
machine (or CI secret store) is configured, `.env` is a local convenience. Document it in the
README, because "why is it using the wrong folder" is always a precedence question.

:::pitfall A boolean flag cannot mean "not given"
`--dry-run` with `action="store_true"` is `False` whether the user passed `--no-dry-run`, nothing at
all, or their config says dry-run. When a setting has three states (on, off, unset) use
`default=None` with `action="store_true"`, or `--dry-run/--no-dry-run` via
`parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction)`, and fall back to config
only when the value is `None`.
:::

## Notifications: email and webhooks

When the job runs unattended, silence is the failure mode. Send the result somewhere someone reads.

```python
import smtplib
import ssl
from email.message import EmailMessage


def send_report(
    *, subject: str, body: str, sender: str, recipients: tuple[str, ...],
    host: str, port: int, user: str, password: str, attachment: Path | None = None,
) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)
    if attachment:
        message.add_attachment(
            attachment.read_bytes(), maintype="text", subtype="markdown",
            filename=attachment.name,
        )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as smtp:
        smtp.login(user, password)
        smtp.send_message(message)
```

:::danger Never put your real password in a script
Use an app password (Gmail, iCloud, Fastmail all offer them) or a scoped SMTP token, and keep it in
an environment variable or `.env` that is in `.gitignore`. A real account password in a committed
file is a full account compromise, not just an email leak — and it will be found by scanners within
minutes if the repo is ever public.
:::

Plain SMTP is increasingly blocked and always fiddly. For anything internal, a webhook is less code
and more useful — it lands in Slack or Teams where the team already is:

```python
import json
import urllib.request


def post_webhook(url: str, text: str, timeout: float = 10.0) -> None:
    payload = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        logger.debug("webhook responded %s", response.status)
```

Same idea as the HTTP calls in Chapter 18, stdlib only — no dependency for a fifteen-line function.

Notification failures should be visible but not fatal: the files moved, so the job succeeded. Catch,
log at `ERROR`, return the code the *work* earned.

```python
try:
    post_webhook(config.webhook_url, summary)
except OSError:
    logger.exception("webhook failed; the files were still moved")
```

## Generating the report

CSV in (Chapter 19), Markdown or HTML out. Escape anything that goes into HTML — a region name with
an ampersand is not an attack, but it is broken output.

```python
import csv
import html


def summarise(csv_path: Path) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            region = (row.get("region") or "unknown").strip()
            try:
                totals[region] = totals.get(region, 0.0) + float(row.get("total") or 0)
            except ValueError:
                logger.warning("bad total in row %s", row)
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)


def as_markdown(totals: list[tuple[str, float]]) -> str:
    lines = ["# Sales by region", "", "| Region | Total |", "| --- | ---: |"]
    lines += [f"| {name} | {total:,.2f} |" for name, total in totals]
    lines.append(f"| **Total** | **{sum(t for _, t in totals):,.2f}** |")
    return "\n".join(lines) + "\n"


def as_html(totals: list[tuple[str, float]]) -> str:
    rows = "\n".join(
        f"    <tr><td>{html.escape(name)}</td><td>{total:,.2f}</td></tr>"
        for name, total in totals
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Sales by region</title>
<body><h1>Sales by region</h1>
<table>
  <tr><th>Region</th><th>Total</th></tr>
{rows}
</table></body></html>
"""
```

Write it atomically-adjacent — build the string fully, then write once. A half-written file is worse
than no file, because the next run will trust it.

```python
def cmd_report(args: argparse.Namespace) -> int:
    if not args.csv_path.is_file():
        raise TidyError(f"no such file: {args.csv_path} — pass a path or set TIDY_SOURCE")

    totals = summarise(args.csv_path)
    text = as_html(totals) if args.format == "html" else as_markdown(totals)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    logger.info("wrote %s (%d regions)", args.output, len(totals))
    print(text)
    return 0
```

## Scheduling it: cron and Task Scheduler

A tool that has to be run by hand is not automation. On macOS and Linux, `cron` is already there.

```bash
crontab -l                 # list your jobs
crontab -e                 # edit them
```

```bash
# m   h  dom  mon  dow   command
MAILTO=you@example.com
0 7 * * 1-5 /usr/bin/env python3 /Users/you/tools/tidy.py organise /Users/you/Downloads --log-file /Users/you/logs/tidy.log >> /Users/you/logs/cron.out 2>&1
```

That is 07:00, Monday to Friday. The five fields are minute, hour, day of month, month, day of week;
`*` means every. On Windows, the equivalent is Task Scheduler, scriptable as:

```bash
schtasks /create /sc daily /st 07:00 /tn "TidyDownloads" ^
  /tr "C:\Python312\python.exe C:\Users\you\tools\tidy.py organise C:\Users\you\Downloads"
```

:::pitfall Cron runs your script in a different world
Cron gives you almost no environment: `PATH` is typically just `/usr/bin:/bin`, your shell profile
is not sourced, and the working directory is your home directory — not the project folder. So
`python3` may not resolve, `Path("data.csv")` points somewhere you did not expect, and every virtual
environment you set up is invisible. The fixes are mechanical: absolute paths for the interpreter,
the script, and every argument; `/Users/you/venv/bin/python` if you need packages; `cd` inside the
command or `Path(__file__).parent` in the code; and always redirect output to a log file, because
cron output otherwise goes to mail you will never read.
:::

## --dry-run and idempotency: the two features that make it safe

`--dry-run` answers "what will this do to me?". Idempotency answers "what happens if it runs twice,
or half-runs?". Together they are why you can point a tool at real data on a Friday.

The rules are simple and worth memorising:

- **Plan, then act.** Compute the full list of changes first. Dry-run prints the plan; the real run
  applies it. One code path, no duplicated logic that can drift.
- **Check before you write.** `if not target.exists()`, `INSERT OR IGNORE`, `mkdir(exist_ok=True)`.
  Every operation should be a no-op the second time.
- **Never overwrite.** Write to a temp file and `os.replace()`, or pick a new name. A tool that
  destroys data on a name collision is worse than no tool.
- **Fail loudly and early.** Validate inputs before the first mutation, so a bad argument cannot
  leave the folder half-organised.

Note the interaction with exit codes: a dry-run that finds nothing to do still exits `0`. It
succeeded at telling you there was nothing to do.

## Handing it to a non-technical colleague

The last mile is not code, it is friction. Four things get a tool adopted:

- **One command.** `python3 tidy.py organise ~/Downloads` and it works. Everything else is optional.
- **Sensible defaults.** Source defaults to their downloads folder; format defaults to whatever they
  will most likely want. A tool that demands six flags before it runs is a tool they will not run.
- **Errors that say what to do.** `no such file: /data/invoices.csv — pass --input or set
  TIDY_INPUT`, not a traceback. Catch the expected exceptions at the top of `main` and translate them.
- **A twelve-line README.** What it does, the one command, how to install (`pip install -r
  requirements.txt`), how to get an app password, and who to ask.

```text
# tidy

Sorts a folder into subfolders by file type and emails or posts a summary.

    python3 tidy.py organise ~/Downloads --dry-run    # see what it would do
    python3 tidy.py organise ~/Downloads              # do it

Setup:
    python3 -m pip install python-dotenv
    cp .env.example .env      # then fill in TIDY_SMTP_PASSWORD (an APP password)

Runs at 07:00 on weekdays via cron (see README for the crontab line).
```

:::scenario The 08:00 report only runs when you are at your laptop
Finance needs a daily sales summary by 08:00. It is a 40-line script on your machine that you run
by hand after your first coffee. You take a day off and nobody notices until 11:00, by which time
the number is stale and you look unreliable. Worse, the script prints to the terminal, so when it
fails there is no record of why.
:::

:::solution Make it a CLI, schedule it, and make its failures findable
Three changes turn it into infrastructure. First, a real interface: `argparse` with a `report`
subcommand, `--output`, and `--webhook`, so the paths and recipients are configuration rather than
edits to the file. Second, logging to a file plus a non-zero exit code, so a failure leaves evidence
and can be alerted on. Third, cron with absolute paths, so it runs whether or not you are awake.

```python
def cmd_report(args: argparse.Namespace) -> int:
    configure_logging(args.verbose, args.quiet, args.log_file)
    config = merge(Config.from_env(), output=args.output)
    try:
        totals = summarise(args.csv_path)
        path = config.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(as_markdown(totals), encoding="utf-8")
    except (OSError, ValueError) as exc:
        logger.exception("report failed")
        return 1

    logger.info("wrote %s with %d regions", path, len(totals))
    if config.webhook_url:
        try:
            post_webhook(config.webhook_url, f"Daily report ready: {path} ({len(totals)} regions)")
        except OSError:
            logger.exception("webhook failed; the report was still written")
    return 0
```

```bash
0 7 * * 1-5 /usr/bin/env python3 /Users/you/tools/tidy.py report /Users/you/data/sales.csv -o /Users/you/reports/sales.md --log-file /Users/you/logs/tidy.log >> /Users/you/logs/cron.out 2>&1
```

The point is not any single line — it is that every failure now has somewhere to go. A missing CSV
logs a traceback to `tidy.log` and exits `1`. A dead webhook logs an error and still exits `0`,
because the report was written; you will see the failure in the log and fix it later. Absolute paths
mean cron's tiny environment does not matter. And because the report is regenerated from scratch
each run, re-running at 11:00 produces the same file — no partial state to clean up.
:::

## Key takeaways

- A tool takes arguments, returns a meaningful exit code, logs with levels, is safe to re-run, and
  explains its own errors; a script does none of these.
- `argparse` gives you `type=`, `choices`, `default`, `action="store_true"`, `nargs`, and
  `add_subparsers` for subcommands — plus `--help` you did not have to write.
- `click` and `typer` express the same CLI with decorators and type hints; choose them for
  completion, prompts, and colour, and stay with `argparse` when you cannot install anything.
- Exit `0` on success, `1` on failure, `2` on bad usage; send errors to stderr and results to stdout
  so redirection keeps working.
- Configure logging once in `main` with a format string, a level from `--verbose`/`--quiet`, and a
  `FileHandler`; use `logger.exception` inside `except`, never `print` for diagnostics.
- Plan changes first (pure function), then apply them — that is what makes `--dry-run` and
  idempotent re-runs nearly free.
- Cron has a minimal environment and a different working directory: use absolute paths everywhere
  and log to a file.
- Configuration resolves in one order: CLI flags, then environment variables, then `.env`, then
  defaults — and never store a real account password in any of them.

## Practice

- [ ] Write `bigfiles.py`: one positional `path` (`type=Path`), `-n/--top` as an `int` defaulting to
      5, and a `--human` flag that prints sizes in KB. Print the N largest files in the folder.
- [ ] Add a `type=` validator `existing_dir(value)` that raises `argparse.ArgumentTypeError` when the
      path is not a directory, wire it into the positional argument, and confirm the error message
      when you pass a file.
- [ ] Write `configure_logging(verbose, quiet, log_file)` exactly as above, then a script that logs
      one DEBUG, one INFO, one WARNING line and one `logger.exception` from inside a `try`. Run it
      with `--verbose` and confirm all four appear in the log file.
- [ ] Implement `unique_target(path)` and prove it: create `notes.txt` in a temp directory, call it
      three times, and show the returned names.
- [ ] Add a `report` subcommand to `tidy.py` that reads a CSV with `csv.DictReader` (Chapter 19) and
      writes a Markdown table to `--output`, exiting `1` with a "what to do" message when the CSV is
      missing.
- [ ] Make `tidy organise` provably idempotent: build a folder with ten files in `tempfile`, run the
      organiser twice, and assert the second run moves zero files.

## Solutions

:::solution Exercise 1
```python
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the biggest files in a folder.")
    parser.add_argument("path", type=Path, help="folder to inspect")
    parser.add_argument("-n", "--top", type=int, default=5, help="how many to show (default: 5)")
    parser.add_argument("--human", action="store_true", help="print sizes in KB")
    args = parser.parse_args()

    files = [p for p in args.path.iterdir() if p.is_file()]
    biggest = sorted(files, key=lambda p: p.stat().st_size, reverse=True)[: args.top]
    for path in biggest:
        size = path.stat().st_size
        shown = f"{size / 1024:,.1f} KB" if args.human else f"{size:,} bytes"
        print(f"{shown:>12}  {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
`type=Path` means no manual conversion, and `default=5` on an `int` option is validated by argparse
before your code runs — pass `--top abc` and you get a usage error, not a `ValueError` later. Note
that `-n` and `--top` both write to `args.top`.
:::

:::solution Exercise 2
```python
import argparse
from pathlib import Path


def existing_dir(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{value!r} is not a folder")
    return path


parser = argparse.ArgumentParser()
parser.add_argument("path", type=existing_dir, help="an existing folder")
args = parser.parse_args()
print("got", args.path)
```
`type` accepts any one-argument callable, so validation happens inside argparse, which turns your
exception into a clean `usage:` message and exit code `2` instead of a traceback. `.expanduser()`
is what makes `~/Downloads` work — the shell does not expand it inside quotes on every platform.
:::

:::solution Exercise 3
```python
import logging
import sys
from pathlib import Path


def configure_logging(verbose: bool, quiet: bool, log_file: Path | None = None) -> None:
    level = logging.DEBUG if verbose else logging.WARNING if quiet else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


logger = logging.getLogger("demo")
configure_logging(verbose=True, quiet=False, log_file=Path("logs/demo.log"))
logger.debug("scan started")
logger.info("processed 42 records")
logger.warning("3 rows had no region")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("failed to compute the average")
```
`force=True` matters here: without it, a second `basicConfig` in the same process is a no-op and you
get no file handler. And `logger.exception` must be inside the `except` block — that is where it
finds the traceback to attach.
:::

:::solution Exercise 4
```python
import itertools
import tempfile
from pathlib import Path


def unique_target(target: Path) -> Path:
    if not target.exists():
        return target
    for counter in itertools.count(1):
        candidate = target.with_name(f"{target.stem} ({counter}){target.suffix}")
        if not candidate.exists():
            return candidate


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    first = unique_target(root / "notes.txt")
    first.write_text("one")
    second = unique_target(root / "notes.txt")
    second.write_text("two")
    third = unique_target(root / "notes.txt")
    print(first.name, second.name, third.name, sep="\n")
```
```text
notes.txt
notes (1).txt
notes (2).txt
```
`itertools.count(1)` gives an unbounded counter without an index variable, and `with_name` keeps
the parent directory and rebuilds only the final component — safer than string surgery on the full
path. Because the check-then-create is not atomic, treat this as collision *avoidance* for
single-process tools, not as locking.
:::

:::solution Exercise 5
```python
import argparse
import csv
import sys
from pathlib import Path


class TidyError(Exception):
    pass


def summarise(csv_path: Path) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            region = (row.get("region") or "unknown").strip()
            try:
                totals[region] = totals.get(region, 0.0) + float(row.get("total") or 0)
            except ValueError:
                print(f"warning: bad total for {region!r}", file=sys.stderr)
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)


def cmd_report(csv_path: Path, output: Path) -> int:
    if not csv_path.is_file():
        raise TidyError(f"no such file: {csv_path} — pass a CSV path or set TIDY_SOURCE")
    totals = summarise(csv_path)
    lines = ["# Sales by region", "", "| Region | Total |", "| --- | ---: |"]
    lines += [f"| {name} | {total:,.2f} |" for name, total in totals]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("report.md"))
    args = parser.parse_args()
    try:
        raise SystemExit(cmd_report(args.csv_path, args.output))
    except TidyError as exc:
        print(f"tidy: {exc}", file=sys.stderr)
        raise SystemExit(1)
```
Building the string before writing means the file either has a complete report or does not exist —
never a half-file that a later run would happily overwrite. The custom `TidyError` is what lets
`main` turn an expected failure into exit code `1` with a message that tells the user what to do.
:::

:::solution Exercise 6
```python
import tempfile
from pathlib import Path

from tidy import plan_moves, apply_moves


def organise(source: Path, *, dry_run: bool) -> int:
    return apply_moves(plan_moves(source, source), dry_run=dry_run)


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for name in ["a.pdf", "b.png", "c.zip", "d.py", "e.mp4"]:
        (root / name).write_text("x")

    first = organise(root, dry_run=False)
    second = organise(root, dry_run=False)
    print("first run moved:", first)
    print("second run moved:", second)
    assert second == 0, "not idempotent!"
    print(sorted(p.name for p in root.iterdir() if p.is_dir()))
```
```text
first run moved: 5
second run moved: 0
['documents', 'images', 'archives', 'code', 'media']
```
Idempotency here comes from the plan, not from a flag: `plan_moves` only looks at top-level files,
so once `a.pdf` is inside `documents/` it is no longer a candidate. That is the pattern to aim for —
the second run is a genuine no-op because there is genuinely nothing left to do, not because the
code remembers having run before.
:::
