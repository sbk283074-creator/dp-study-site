"""Chapter 62 -- most of a real file is not the transformation.

A function of the kind you meet in a codebase, classified line by line. The count
is of lines in each category, and of how many of them do the actual work.
"""

MODULE = [
    '"""Fetch a page and return the rows in its table."""',
    "",
    "import logging",
    "import time",
    "from urllib.parse import urlparse",
    "",
    "log = logging.getLogger(__name__)",
    "",
    "RETRIES = 3",
    "BACKOFF = 0.5",
    "",
    "",
    "def fetch_rows(url, *, timeout=5.0, retries=RETRIES):",
    '    """Return the rows, retrying a flaky server."""',
    "    if not url:",
    "        raise ValueError('url is required')",
    "    if urlparse(url).scheme not in ('http', 'https'):",
    "        raise ValueError(f'unsupported scheme: {url}')",
    "",
    "    last_error = None",
    "    for attempt in range(1, retries + 1):",
    "        try:",
    "            log.debug('fetching %s, attempt %d', url, attempt)",
    "            page = _get(url, timeout=timeout)",
    "            if page is None:",
    "                raise LookupError('empty response')",
    "            return _rows(page)",
    "        except (LookupError, TimeoutError) as error:",
    "            last_error = error",
    "            log.warning('attempt %d failed: %s', attempt, error)",
    "            if attempt < retries:",
    "                time.sleep(BACKOFF * attempt)",
    "        except ValueError:",
    "            log.error('bad response from %s, not retrying', url)",
    "            raise",
    "",
    "    log.error('gave up on %s after %d attempts', url, retries)",
    "    raise TimeoutError(f'{url} failed after {retries} attempts') from last_error",
    "",
    "",
    "def _rows(page):",
    "    table = page.split('<table', 1)[-1]",
    "    body = table.split('>', 1)[-1].split('</table>', 1)[0]",
    "    return [row.split('</tr>')[0] for row in body.split('<tr')[1:]]",
]

# Everything after this line is the transformation; everything before it is the
# machinery that decides whether the transformation gets to run.
WORK_START = next(index for index, line in enumerate(MODULE)
                  if line.startswith("def _rows"))


def category(index, line):
    stripped = line.strip()
    if not stripped:
        return "blank"
    if index > WORK_START:
        return "transformation"
    if stripped.startswith("#"):
        return "comment"
    if stripped.startswith('"""'):
        return "docstring"
    if stripped.startswith(("import ", "from ")):
        return "import"
    if stripped.startswith("def "):
        return "signature"
    if stripped.startswith(("raise ", "if not ", "if urlparse")):
        return "validation"
    if stripped.startswith("log."):
        return "logging"
    return "plumbing"


counts = {}
for index, line in enumerate(MODULE):
    counts[category(index, line)] = counts.get(category(index, line), 0) + 1

order = ["transformation", "plumbing", "validation", "logging", "signature",
         "docstring", "import", "comment", "blank"]
total = len(MODULE)
work = counts.get("transformation", 0)

print(f"a {total}-line function, classified line by line")
print()
print(f"{'category':<16}{'lines':>7}{'share':>9}   bar")
print("-" * 66)
for name in order:
    count = counts.get(name, 0)
    print(f"{name:<16}{count:>7}{100.0 * count / total:>8.1f}%   {'#' * count}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'lines in the file':<46}{total:>8}")
print(f"{'lines that do the transformation':<46}{work:>8}")
print(f"{'lines around them':<46}{total - work:>8}")
print(f"{'lines spent on guards':<46}{counts.get('validation', 0):>8}")
print(f"{'lines spent on logging':<46}{counts.get('logging', 0):>8}")
print(f"{'lines that are blank':<46}{counts.get('blank', 0):>8}")
print(f"{'lines that are imports':<46}{counts.get('import', 0):>8}")
print(f"{'share of the file that is the work':<46}"
      f"{round(100 * work / total):>7}%")

print()
print("The bar chart answers 'where do I start reading this'. Three lines out of")
print(f"{total} are the transformation -- split on a tag, take the middle, collect the")
print("rows -- and the other 41 decide whether those three lines get to run: two")
print("guards, a retry loop, a backoff, four log calls, and the imports and")
print("constants that make them work.")
print()
print("That ratio is not an accident of this example; it is what production code")
print("looks like. The transformation is the part that differs in every file, and")
print("the guards, the retries, the logging and the error paths are the part that")
print("is the same in all of them. A reader who tries to understand every line in")
print("order therefore spends most of their time on code they have seen before,")
print("and arrives at the interesting part tired.")
print()
print("So read for the shape first. Find the function, read its signature and what")
print("it returns, then find the lines that produce that return -- here they are")
print("the last three, in a helper called from the middle of a retry loop.")
print("Everything between is usually one of five things: a guard, a retry, a log,")
print("a conversion, or a call to something else. Knowing which five is the whole")
print("skill, and the count above is the reason it is worth having.")
