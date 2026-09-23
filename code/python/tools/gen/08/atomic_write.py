"""Chapter 8 -- the file a reader can see while it is being written.

Two designs for writing the same three chunks to the same path: truncate the
target and write into it, or write a temporary file and rename it over the
target. The count is of observations a reader can make that are neither the
old contents nor the new ones -- a file that is not any version of the data.
"""

import os
import tempfile

OLD = "old\n"
CHUNKS = ["alpha\n", "beta\n", "gamma\n"]
NEW = "".join(CHUNKS)


def observe(target):
    """Classify what a reader sees at this moment."""
    try:
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
    except FileNotFoundError:
        return "missing"
    if content == OLD:
        return "old"
    if content == NEW:
        return "new"
    return "torn"


def truncate_then_write(target):
    """Open the target for writing, which empties it, then write the chunks."""
    seen = []
    with open(target, "w", encoding="utf-8") as handle:
        for chunk in CHUNKS:
            handle.write(chunk)
            handle.flush()
            seen.append(observe(target))
    seen.append(observe(target))
    return seen


def write_then_rename(target):
    """Write a temporary file, then put it in place in one step."""
    seen = []
    temporary = target + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        for chunk in CHUNKS:
            handle.write(chunk)
            handle.flush()
            seen.append(observe(target))
    os.replace(temporary, target)
    seen.append(observe(target))
    return seen


DESIGNS = [
    ("truncate and write", truncate_then_write),
    ("write, then rename", write_then_rename),
]

print(f"{len(CHUNKS)} chunks, {len(CHUNKS) + 1} observations per design: one after each")
print(f"chunk is written and one when the write is finished")
print()
print(f"{'design':<22}{'old':>6}{'new':>6}{'torn':>7}{'missing':>9}")
print("-" * 50)
for name, design in DESIGNS:
    directory = tempfile.mkdtemp()
    target = os.path.join(directory, "data.txt")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(OLD)
    seen = design(target)
    counts = {state: seen.count(state) for state in ("old", "new", "torn", "missing")}
    print(f"{name:<22}{counts['old']:>6}{counts['new']:>6}{counts['torn']:>7}"
          f"{counts['missing']:>9}")

print()
print("The first design leaves a file that is not any version of the data, and")
print("it does so on every chunk but the last. A reader that arrives in the")
print("middle gets a prefix -- a document with half a record in it, a settings")
print("file that parses up to the point it stops.")
print()
print("The second design shows the old file until the rename and the new file")
print("after it, and the rename is one operation the filesystem makes atomic.")
print("There is no moment in between, which is why the torn count is zero.")
print()
print("The cost is a second file and a rename, and the benefit is that every")
print("observation is a complete version of something. That is what atomic")
print("means here: not that the write cannot fail, but that a failure leaves a")
print("whole file behind rather than half of one.")
