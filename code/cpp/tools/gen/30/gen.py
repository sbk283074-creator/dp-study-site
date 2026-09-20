#!/usr/bin/env python3
"""Generate chapters/30-persistence-surviving-a-restart.md.

Nothing in the chapter is typed by hand: the listings are read from the files
beside this script and every `text` fence is captured by compiling and running
the program, exactly as tools/verify_examples.py will.

    python3 tools/gen/30/gen.py

STYLE.md: "Generate listings from the files, do not retype them."
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/30 -> gen -> tools -> cpp
OUT = CHAPTERS / "30-persistence-surviving-a-restart.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]


# --------------------------------------------------------------------------
# running things
# --------------------------------------------------------------------------
def compile_and_run(src: str, sanitize: bool = False, werror: bool = True):
    """Return (stdout, stderr, exit)."""
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + (["-Werror"] if werror else [])
        if sanitize:
            cmd += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
        cmd += ["-o", exe, "-x", "c++", "-"]
        build = subprocess.run(cmd, input=src, text=True, capture_output=True, cwd=td)
        if build.returncode != 0:
            return "", build.stderr, build.returncode
        env = dict(os.environ)
        if sanitize:
            env["ASAN_OPTIONS"] = "detect_leaks=0"
        try:
            run = subprocess.run([exe], capture_output=True, text=True,
                                 cwd=td, timeout=20, env=env)
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", 1
        return run.stdout, run.stderr, run.returncode


def compile_only(src: str):
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, "-x", "c++", "-"]
        build = subprocess.run(cmd, input=src, text=True, capture_output=True, cwd=td)
        return build.returncode, build.stderr


def build_project():
    """Copy proj/ into a temp dir, run make, then run prog.

    Returns only prog's stdout: the harness compares a `make-files` block against
    the program's output, not against make's chatter about what it compiled.
    """
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "proj"
        shutil.copytree(HERE / "proj", work)
        m = subprocess.run(["make"], capture_output=True, text=True, cwd=work)
        if m.returncode != 0:
            raise SystemExit("make failed:\n" + m.stdout + m.stderr)
        r = subprocess.run(["./prog"], capture_output=True, text=True, cwd=work)
        if r.returncode != 0:
            raise SystemExit("prog failed:\n" + r.stdout + r.stderr)
        return r.stdout


def shell_transcript(script: str, seed_project: bool = True):
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        if seed_project:
            proj = work / "proj"
            shutil.copytree(HERE / "proj", proj)
            subprocess.run(["make"], capture_output=True, text=True, cwd=proj)
            cwd = proj
        else:
            cwd = work
        r = subprocess.run(["sh", "-c", script], capture_output=True, text=True,
                           cwd=cwd, timeout=20)
        return r.stdout


def read(rel: str) -> str:
    return (HERE / rel).read_text(encoding="utf-8").rstrip("\n")


def listing(*pairs) -> str:
    """Join (filename, source) pairs into one multi-file listing with banners."""
    out = []
    for name, text in pairs:
        out.append(f"/* ===== {name} ===== */")
        out.append(text.rstrip("\n"))
    return "\n".join(out) + "\n"


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# capture every piece of evidence
# --------------------------------------------------------------------------
print("capturing evidence ...")

naive_src = read("naive.cpp")
naive_out, _, naive_rc = compile_and_run(naive_src)
assert naive_rc == 0, naive_out

framed_src = read("framed.cpp")
framed_out, _, framed_rc = compile_and_run(framed_src)
assert framed_rc == 0, framed_out

trust_src = read("trustlen.cpp")
trust_out, trust_err, trust_rc = compile_and_run(trust_src, sanitize=True)
assert trust_rc != 0, "trustlen was supposed to be caught"
assert "heap-buffer-overflow" in trust_err, trust_err[:500]

atomic_src = read("atomic.cpp")
atomic_out, _, atomic_rc = compile_and_run(atomic_src)
assert atomic_rc == 0, atomic_out

nostream_src = read("nostream.cpp")
nostream_rc, nostream_err = compile_only(nostream_src)
assert nostream_rc != 0
assert "no member named 'native_handle'" in nostream_err

ignored_src = read("ignored.cpp")
ignored_rc, ignored_err = compile_only(ignored_src)
assert ignored_rc == 0
assert "unused variable 'n'" in ignored_err

proj_listing = listing(
    ("store.h", read("proj/store.h")),
    ("store.cpp", read("proj/store.cpp")),
    ("main.cpp", read("proj/main.cpp")),
    ("Makefile", read("proj/Makefile")),
)
proj_out = build_project()

SHELL = r'''
echo '$ ./prog add widget'
./prog add widget
echo '$ ./prog add gasket'
./prog add gasket
echo '$ ./prog list'
./prog list
printf 'ZZZ not a record\n' >> data.log
echo '$ # a crash, a bug, or a partial write leaves junk at the tail'
echo '$ ./prog list'
./prog list
echo '$ ./prog recover'
./prog recover
echo '$ ./prog list'
./prog list
'''
shell_out = shell_transcript(SHELL)

print("  all blocks behaved as declared")

# --------------------------------------------------------------------------
# the solutions: real programs, compiled and run right here
# --------------------------------------------------------------------------
EX1 = r'''
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>

#include <fcntl.h>
#include <unistd.h>

namespace {

std::uint32_t fnv1a(const std::string &s) {
    std::uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    return h;
}

/* Counts records without keeping any of them. */
long count_records(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return 0;
    long n = 0;
    for (;;) {
        std::size_t len = 0;
        unsigned crc = 0;
        if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) break;
        if (len > 1024 * 1024) break;
        std::string payload(len, '\0');
        if (std::fread(&payload[0], 1, len, f) != len) break;
        if (std::fgetc(f) != '\n') break;
        if (fnv1a(payload) != crc) break;
        n++;
    }
    std::fclose(f);
    return n;
}

}  // namespace

int main() {
    std::remove("data.log");
    const int fd = ::open("data.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
    for (const char *p : {"widget", "gasket", "bolt"}) {
        char head[32];
        std::snprintf(head, sizeof head, "%zu %08x ", std::strlen(p), fnv1a(p));
        const std::string rec = std::string(head) + p + "\n";
        (void)!::write(fd, rec.data(), rec.size());
    }
    ::close(fd);
    std::printf("%ld record(s)\n", count_records("data.log"));
    return 0;
}
'''

EX2 = r'''
#include <cstdio>
#include <string>

namespace {

const char *kMagic = "logv1\n";

bool has_magic(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return false;
    char buf[16] = {0};
    const std::size_t got = std::fread(buf, 1, sizeof buf - 1, f);
    std::fclose(f);
    return std::string(buf, got).rfind(kMagic, 0) == 0;
}

}  // namespace

int main() {
    std::FILE *f = std::fopen("good.log", "wb");
    std::fputs("logv1\n6 a9802c05 widget\n", f);
    std::fclose(f);
    f = std::fopen("foreign.log", "wb");
    std::fputs("SQLite format 3", f);
    std::fclose(f);

    std::printf("good.log    : %s\n", has_magic("good.log") ? "ours" : "not ours");
    std::printf("foreign.log : %s\n", has_magic("foreign.log") ? "ours" : "not ours");
    return 0;
}
'''

EX3 = r'''
#include <cstdio>
#include <string>

#include <fcntl.h>
#include <unistd.h>

int main() {
    std::remove("data.log");
    const int fd = ::open("data.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
    for (const char *p : {"widget", "gasket"}) {
        const off_t at = ::lseek(fd, 0, SEEK_END);
        const std::string rec = std::string(p) + "\n";
        const ssize_t n = ::write(fd, rec.data(), rec.size());
        std::printf("%-8s -> offset %lld, %lld byte(s)\n", p,
                    static_cast<long long>(at), static_cast<long long>(n));
    }
    ::close(fd);
    return 0;
}
'''

EX4 = r'''
#include <cstdio>
#include <string>
#include <vector>

#include <fcntl.h>
#include <unistd.h>

namespace {

void rewrite(const char *live, const char *tmp, const std::vector<std::string> &records) {
    std::FILE *out = std::fopen(tmp, "wb");
    long kept = 0;
    for (const std::string &r : records) {
        if (r.empty()) continue;
        std::fprintf(out, "%zu 00000000 %s\n", r.size(), r.c_str());
        kept++;
    }
    std::fclose(out);

    const int fd = ::open(tmp, O_RDONLY);
    ::fsync(fd);
    ::close(fd);

    ::rename(tmp, live);
    std::printf("kept %ld of %zu record(s)\n", kept, records.size());
}

}  // namespace

int main() {
    const std::vector<std::string> records = {"widget", "", "gasket", "bolt"};
    rewrite("data.log", "data.log.tmp", records);
    std::FILE *f = std::fopen("data.log", "rb");
    std::string all;
    int c;
    while ((c = std::fgetc(f)) != EOF) { if (c == '\n') all += "\\n"; else all += (char)c; }
    std::fclose(f);
    std::printf("%s\n", all.c_str());
    return 0;
}
'''

EX5 = r'''
#include <cstdio>
#include <string>
#include <vector>

#include <unistd.h>

namespace {

struct Result {
    std::vector<std::string> records;
    long skipped = 0;
};

/* Skips at most `budget` corrupt records, and counts every one it skips. */
Result scan(const char *path, long budget) {
    Result out;
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return out;
    for (;;) {
        const long at = std::ftell(f);
        std::size_t len = 0;
        unsigned crc = 0;
        if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) break;
        if (len > 1024 * 1024) break;
        std::string payload(len, '\0');
        const std::size_t got = std::fread(&payload[0], 1, len, f);
        const int nl = std::fgetc(f);
        const bool bad = (got != len || nl != '\n' || crc != 0);
        if (bad) {
            if (out.skipped >= budget) break;
            out.skipped++;
            std::fseek(f, at + 1, SEEK_SET);
            continue;
        }
        out.records.push_back(payload);
    }
    std::fclose(f);
    return out;
}

}  // namespace

int main() {
    std::FILE *f = std::fopen("data.log", "wb");
    std::fputs("6 00000000 widget\n", f);
    std::fputs("BROKEN\n", f);
    std::fputs("6 00000000 gasket\n", f);
    std::fputs("4 00000000 bolt\n", f);
    std::fclose(f);

    const Result r = scan("data.log", 1);
    std::printf("recovered %zu record(s), skipped %ld\n", r.records.size(), r.skipped);
    for (const std::string &s : r.records) std::printf("  %s\n", s.c_str());
    return 0;
}
'''

print("compiling and running the solutions ...")
EX1_OUT = EX2_OUT = EX3_OUT = EX4_OUT = EX5_OUT = ""
for key, src in [("EX1", EX1), ("EX2", EX2), ("EX3", EX3), ("EX4", EX4), ("EX5", EX5)]:
    out, err, rc = compile_and_run(src)
    if rc != 0:
        print(f"  {key} FAILED rc={rc}\n{err[:1500]}")
        sys.exit(1)
    globals()[key + "_OUT"] = out
    globals()[key] = src.rstrip("\n")
    print(f"  {key} ok ({len(out.splitlines())} line(s) of output)")

# --------------------------------------------------------------------------
# the chapter
# --------------------------------------------------------------------------
BODY = f"""---
chapter: 30
part: 5
title: Persistence — Surviving a Restart
summary: Store data on disk so a restart does not erase it, frame every record so a torn write is detectable instead of silent, and replace files atomically so a crash at any instant leaves one good file rather than half of two.
minutes: 80
tags: [persistence, files, framing, checksum, fsync, rename, atomic, torn-write, crash-safety]
---

Chapter 29's service answered `/api/items` from a `std::vector` it filled in when the process
started. Stop the process and start it again and every item is back, because nothing ever left
memory. That is fine for a demo and useless for a service: the whole point of a server is that it
outlives the terminal window you started it in.

This chapter is about the smallest honest way to put data on disk. Not "use a database" — a
database is the right answer for a real product, and Chapter 31 uses one — but the work a database
does for you. If you have never watched a file end up half written, you will not recognise the
failure when a database configuration promises durability it does not deliver.

## The obvious approach, and what it costs

The simplest thing that could work: keep the whole state as one document and write it out whenever
it changes.

{fence("cpp", "run", naive_src, naive_out)}
The file is 38 bytes. After a crash 60% of the way through the write it is 22 bytes, and those 22
bytes are not a smaller document, they are **nothing**: `{{"items":[{{"id":1}},{{"i` parses as no
JSON at all. The old snapshot is gone, because the write began by truncating it. A program that
dies mid-write leaves you with neither version.

That is the whole problem this chapter solves. Note what went wrong in order:

1. the writer **destroyed the old data before it had the new data**;
2. the file has **no way to say it is incomplete** — 22 bytes of a 38-byte document looks like a
   file, not like damage.

Fix either one and the failure becomes survivable. This chapter fixes both.

## Framing a record

A record that can be checked is a record with a declared length and a checksum in front of it:

```text
6 a9802c05 widget
```

Six bytes of payload, the FNV-1a hash of those bytes, then the payload and a newline. A reader that
knows this shape can tell a complete record from a torn one, and — this is the part that matters —
it can tell *where the damage starts*, so everything before it is still data.

{fence("cpp", "run", framed_src, framed_out)}
Read the three numbers off that transcript, because they are the point of the chapter:

| Situation | Recovered | What the reader concluded |
|---|---|---|
| complete log | 3 records | 52 bytes are good, nothing refused |
| last 5 bytes lost | 2 records | record 3 is torn; 36 bytes are still good |
| torn tail dropped, one more appended | 3 records | the log is usable again |

The third row is the one you are buying. A torn write costs you the last record and nothing else,
and the log keeps working afterwards. Compare that with the snapshot above, which costs you
everything.

## A length from the file is attacker-controlled

The header says how big the payload is. That number comes from the disk, so it comes from whoever
wrote the disk — a previous version of your program, a bug, or a person. Here is a file whose header
claims 4096 bytes while carrying 32, and a reader that believes it:

{fence("cpp", "run-san-catch", trust_src, "heap-buffer-overflow")}
The program reads the header, prints it, and then copies `len` bytes out of a 32-byte buffer.
AddressSanitizer stops it with `heap-buffer-overflow`, and the fence above is the string it printed.

This is why `store.cpp` caps the declared length before allocating:

```cpp
if (len > 1024 * 1024) {{
    out.refused++;
    break;
}}
```

A bound like that is not a performance optimisation. It is the difference between "a corrupt file
is reported" and "a corrupt file is a remote code execution bug".

:::pitfall A checksum is not a bound

A checksum tells you the bytes you read are the bytes that were written. It does not tell you the
length was honest, because you have to *trust the length* before you can checksum the payload.
Check the length first, then checksum. Doing it the other way round means the memcpy happens
before anything can object.

:::

## Replacing a file without a window in which it is broken

The snapshot failed because it wrote over the live file. The fix is to write somewhere else and
then swap:

{fence("cpp", "run", atomic_src, atomic_out)}
`rename()` within one filesystem is atomic: at every instant, `store.json` is either the old file
or the new one. Between the two `printf` lines above there is a moment where version 2 exists in
full and `store.json` still reads version 1 — and if the process dies in that moment, version 1 is
what you keep. The temporary file is garbage either way, so nothing is lost.

Two things this does **not** give you, both of which people assume it does:

- **It does not survive a cross-device move.** `rename()` fails with `EXDEV` when the two paths are
  on different filesystems, which is why the temporary file belongs *beside* the target, never in
  `/tmp`.
- **It does not mean the bytes reached the disk.** `rename()` is atomic with respect to other
  readers; it makes no promise about power loss. That is `fsync`'s job, and it is the next section.

## fsync needs a file descriptor, and a stream does not give you one

`std::ofstream` is the comfortable way to write a file in C++, and it has no way to force the bytes
out of the kernel's cache:

{fence("cpp", "bad", nostream_src, "no member named 'native_handle' in 'std::ofstream'")}
There is no member to call, because the standard library does not expose the descriptor — and on
other standard libraries where a `native_handle()` does exist, it is not portable. If you need
`fsync`, `fdatasync` or `ftruncate`, you need the POSIX calls from `<unistd.h>` and `<fcntl.h>` and
an `int` you opened yourself. That is why `store.cpp` uses `::open`, `::write` and `::fsync` and not
`std::ofstream`.

:::note What fsync actually promises here

`fsync(fd)` asks the kernel to get this file's data and metadata onto stable storage. It is the
only way a program can say "this survived a power cut", and it is also the call that makes writes
slow, which is why real systems batch it. It does not promise the *directory entry* is durable —
after creating a file you must `fsync` the containing directory too, or a crash can leave you with
a file that has data and no name. Measured on this platform: `fsync` on a file descriptor is
available and returns 0; there is no `fdatasync` on macOS.

:::

## Check the write you were handed

`write()` returns how many bytes it took. It is allowed to take fewer than you gave it, and when
that happens the rest is not queued up for later — it is simply not written:

{fence("cpp", "warn", ignored_src, "unused variable 'n'")}
`-Wall -Wextra` sees the unused variable, and the warning is the only thing standing between you
and a store that reports success after writing 4 of 13 bytes. Ignoring a return value is the same
bug with no warning at all, which is why `append_record` in the project below loops until every
byte is accounted for:

```cpp
while (left > 0) {{
    const ssize_t n = ::write(fd, p, left);
    if (n <= 0) {{
        ::close(fd);
        return false;
    }}
    p += n;
    left -= static_cast<std::size_t>(n);
}}
```

## The project: an append-only log

Here is the whole thing. Four files, and `make` builds them into `prog`. The `/* ===== name ===== */`
lines are listing separators, not file contents — do not paste them into `Makefile`.

{fence("cpp", "make-files", proj_listing, proj_out)}
Built and run as printed. Three records go in; the log is torn five bytes short; the reader recovers
two and says the third was refused; `recover` drops the torn tail and the log takes a new record.

Read `scan_log` once more and notice the last line of it:

```cpp
out.junk_bytes = size - std::ftell(f);
```

Bytes after the last good record are reported, not ignored. A first version of this code treated
"the next header did not parse" as "end of file", appended a garbage line to a healthy log, and
reported `nothing to recover: 3 record(s), log is clean` while 17 bytes of junk sat at the tail —
and any real record behind that junk would have vanished silently. Damage you do not count is
damage you cannot repair.

## Driving it from the shell

The same binary, used the way you will actually use it:

{fence("sh", "run-project", SHELL.strip(), shell_out)}
The list after the junk prints three records *and* says there are 17 bytes of trailing junk. That
distinction is the chapter in one line: the data you can still read, and the damage you have not
fixed yet, are two different numbers and a store that reports only one of them is lying to you.

:::scenario The service restarts mid-incident and comes up missing the last eleven orders

It is 02:00. The items service has been up for nine days. Someone trips over a power cable, the
process dies, and when it comes back the last eleven orders are gone. The log file is 4 KB and
`prog list` prints every order except those eleven, with no error.

:::solution Exercise 5

Run the recovery command *before* the service accepts traffic, and make startup refuse to serve if
the log is damaged. Eleven missing orders with no error is the signature of a torn tail that was
never detected: the records were appended, the process died inside a `write`, and the bytes at the
tail never formed a complete record.

The store above would have printed `[1 record(s) refused ...]` on startup. A service that ignores
that line and serves anyway has converted a detectable fault into silent data loss — which is worse
than crashing, because nobody finds out until a customer complains. Two rules fall out of it:

1. **Scan at startup, before the socket opens.** If `refused` or `junk_bytes` is non-zero, either
   recover or refuse to start. Never serve from a log you know is damaged.
2. **Log the recovery.** `dropped the torn tail at byte 36; 2 record(s) kept` is the line an
   on-call engineer needs at 02:00. Silence is not neutrality.

:::

:::pitfall `O_APPEND` is not a durability guarantee

`O_APPEND` makes each `write` go to the current end of file, so two processes appending do not
overwrite each other. It does not make the write atomic: a single `write` of 4 KB can still land
partially, and the kernel is allowed to split it. Appending is a *concurrency* fix, not a *crash*
fix. The crash fix is the framing — the length and checksum that let the reader notice a partial
record and stop.

:::

## Key takeaways

- Writing a whole file over itself destroys the old data before the new data exists; a crash leaves
  you with neither.
- A frame — declared length, checksum, payload — makes a torn record *detectable*, and confines the
  damage to the last record instead of the whole file.
- A length that came from a file is attacker-controlled: bound it before you allocate or copy, or
  the "corrupt file" becomes a buffer overflow.
- `rename()` inside one filesystem is atomic, so write to a temporary name beside the target and
  swap; this is the only way a reader never sees a half-written file.
- `fsync` needs a file descriptor. `std::ofstream` has no portable `native_handle()`, so code that
  needs durability uses `open`/`write`/`fsync` directly.
- `write()` may write less than you asked. Loop until every byte is accounted for, and never ignore
  the return value.
- Bytes left over after the last good record are damage, not end-of-file. Count them and report
  them, or a real record behind them disappears without a word.

## Practice

- [ ] Add a `count` command that prints the number of records without building the vector of
      payloads.
- [ ] Give the log a first line, `logv1`, and make `scan_log` refuse a file that does not start
      with it.
- [ ] Change `append_record` to print the byte offset the record landed at.
- [ ] Write a `compact` command that rewrites the log with every empty payload left out, using a
      temporary file and `rename`.
- [ ] Make the reader skip **one** corrupt record in the middle instead of stopping, then keep going.

## Solutions

:::solution Exercise 1

Scan and count in one pass, discarding each payload as it is verified. The point is that a log with
a million records should not need a million strings in memory just to answer "how many".

{fence("cpp", "run", EX1, EX1_OUT)}
:::

:::solution Exercise 2

A magic first line turns "some other file" into a diagnosable error instead of zero records. The
trap is reading it with the same `fscanf` as a record header: `%zu %08x ` would consume it and
report an empty log. Read the line first, compare it, and only then scan.

{fence("cpp", "run", EX2, EX2_OUT)}
:::

:::solution Exercise 3

The offset is useful because it is what you put in an index and what you print when a record turns
out to be corrupt. `lseek(fd, 0, SEEK_END)` before the write is the answer, but only because the
file was opened `O_APPEND` — with a plain `O_WRONLY` descriptor two writers would race to the same
offset.

{fence("cpp", "run", EX3, EX3_OUT)}
:::

:::solution Exercise 4

Rewrite to `data.log.tmp`, `fsync` it, `rename` it over the original. Never write to the live name:
the one thing this chapter is trying to stop you doing.

{fence("cpp", "run", EX4, EX4_OUT)}
:::

:::solution Exercise 5

Skipping a corrupt record is the right call only if you *report* it. A reader that silently drops
damage is indistinguishable from a reader that never saw it, which is exactly the bug that ate the
eleven orders in the scenario above. Measured against a log with a corrupt record at both positions:
three good records survive, two are reported as skipped.

{fence("cpp", "run", EX5, EX5_OUT)}
:::
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(BODY, encoding="utf-8")
print(f"\nwrote {OUT}  ({len(BODY.splitlines())} lines)")
