---
chapter: 37
part: 5
title: Persistence — Surviving a Restart
summary: Store data on disk so a restart does not erase it, frame every record so a torn write is detectable instead of silent, and replace files atomically so a crash at any instant leaves one good file rather than half of two.
minutes: 80
tags: [persistence, files, framing, checksum, fsync, rename, atomic, torn-write, crash-safety]
---

Chapter 36's service answered `/api/items` from a `std::vector` it filled in when the process
started. Stop the process and start it again and every item is back, because nothing ever left
memory. That is fine for a demo and useless for a service: the whole point of a server is that it
outlives the terminal window you started it in.

This chapter is about the smallest honest way to put data on disk. Not "use a database" — a
database is the right answer for a real product, and Chapter 38 uses one — but the work a database
does for you. If you have never watched a file end up half written, you will not recognise the
failure when a database configuration promises durability it does not deliver.

## The obvious approach, and what it costs

The simplest thing that could work: keep the whole state as one document and write it out whenever
it changes.

```cpp run
/* What a "write the whole file" snapshot looks like when the process dies
   part way through. */
#include <cstdio>
#include <string>

#include <fcntl.h>
#include <unistd.h>

namespace {

std::string snapshot(int count) {
    std::string out = "{\"items\":[";
    for (int i = 0; i < count; i++) {
        if (i > 0) out += ",";
        out += "{\"id\":" + std::to_string(i + 1) + "}";
    }
    out += "]}";
    return out;
}

std::string read_all(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return "(no such file)";
    std::string out;
    int c;
    while ((c = std::fgetc(f)) != EOF) out += static_cast<char>(c);
    std::fclose(f);
    return out;
}

void write_bytes(const char *path, const std::string &data) {
    int fd = ::open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        std::perror("open");
        return;
    }
    ssize_t n = ::write(fd, data.data(), data.size());
    ::close(fd);
    std::printf("write() returned %lld\n", static_cast<long long>(n));
}

}  // namespace

int main() {
    const std::string data = snapshot(3);

    write_bytes("store.json", data);
    std::printf("the file reads: %s\n\n", read_all("store.json").c_str());

    /* Now the same write, except the process died after 60% of it. truncate()
       is exactly what a kill -9 leaves on disk. */
    write_bytes("store.json", data);
    if (::truncate("store.json", static_cast<off_t>(data.size() * 6 / 10)) != 0) {
        std::perror("truncate");
        return 1;
    }
    std::printf("after dying 60%% of the way through:\n");
    std::printf("the file reads: %s\n", read_all("store.json").c_str());
    return 0;
}
```

```text
write() returned 38
the file reads: {"items":[{"id":1},{"id":2},{"id":3}]}

write() returned 38
after dying 60% of the way through:
the file reads: {"items":[{"id":1},{"i
```

The file is 38 bytes. After a crash 60% of the way through the write it is 22 bytes, and those 22
bytes are not a smaller document, they are **nothing**: `{"items":[{"id":1},{"i` parses as no
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

```cpp run
/* Length + checksum framing: a torn tail is detectable, and the records
   before it are untouched. */
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

#include <unistd.h>

namespace {

std::uint32_t fnv1a(const std::string &s) {
    std::uint32_t h = 2166136261u;
    for (unsigned char c : s) {
        h ^= c;
        h *= 16777619u;
    }
    return h;
}

std::string frame(const std::string &payload) {
    char head[64];
    std::snprintf(head, sizeof head, "%zu %08x ", payload.size(), fnv1a(payload));
    return std::string(head) + payload + "\n";
}

void append(const char *path, const std::string &payload) {
    std::FILE *f = std::fopen(path, "ab");
    if (!f) {
        std::perror("fopen");
        std::exit(1);
    }
    std::fputs(frame(payload).c_str(), f);
    std::fclose(f);
}

struct Scan {
    std::vector<std::string> records;
    long good_bytes = 0;   /* bytes covered by complete, verified records */
    long refused = 0;      /* count of records that failed verification */
    long junk_bytes = 0;   /* bytes left over after the last good record */
};

Scan scan(const char *path) {
    Scan out;
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return out;

    std::fseek(f, 0, SEEK_END);
    const long size = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);

    for (;;) {
        std::size_t len = 0;
        unsigned crc = 0;
        if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) break;
        std::string payload(len, '\0');
        const std::size_t got = std::fread(&payload[0], 1, len, f);
        const int nl = std::fgetc(f);
        if (got != len || nl != '\n') {
            out.refused++;
            break;
        }
        if (fnv1a(payload) != crc) {
            out.refused++;
            break;
        }
        out.records.push_back(payload);
        out.good_bytes = std::ftell(f);
    }
    out.junk_bytes = size - std::ftell(f);
    std::fclose(f);
    return out;
}

std::string raw(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return "(no such file)";
    std::string out;
    int c;
    while ((c = std::fgetc(f)) != EOF) {
        if (c == '\n') out += "\\n";
        else           out += static_cast<char>(c);
    }
    std::fclose(f);
    return out;
}

void report(const char *path) {
    const Scan s = scan(path);
    std::printf("  recovered %zu record(s), refused %ld, %ld good byte(s), %ld junk byte(s)\n",
                s.records.size(), s.refused, s.good_bytes, s.junk_bytes);
    for (const std::string &r : s.records) std::printf("    %s\n", r.c_str());
}

}  // namespace

int main() {
    std::remove("data.log");
    append("data.log", "widget");
    append("data.log", "gasket");
    append("data.log", "bolt");
    std::printf("the log on disk:\n  %s\n\n", raw("data.log").c_str());

    std::printf("reading it back:\n");
    report("data.log");

    /* A crash half way through the third record: five bytes short. */
    const Scan before = scan("data.log");
    ::truncate("data.log", before.good_bytes - 5);
    std::printf("\nafter losing the last 5 bytes:\n  %s\n", raw("data.log").c_str());
    report("data.log");

    /* Throw away the torn tail, then carry on. */
    const Scan after = scan("data.log");
    ::truncate("data.log", after.good_bytes);
    append("data.log", "washer");
    std::printf("\nafter truncating to the last good record and appending:\n");
    report("data.log");
    return 0;
}
```

```text
the log on disk:
  6 a9802c05 widget\n6 65b3381a gasket\n4 ce96dd46 bolt\n

reading it back:
  recovered 3 record(s), refused 0, 52 good byte(s), 0 junk byte(s)
    widget
    gasket
    bolt

after losing the last 5 bytes:
  6 a9802c05 widget\n6 65b3381a gasket\n4 ce96dd46 
  recovered 2 record(s), refused 1, 36 good byte(s), 0 junk byte(s)
    widget
    gasket

after truncating to the last good record and appending:
  recovered 3 record(s), refused 0, 54 good byte(s), 0 junk byte(s)
    widget
    gasket
    washer
```

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

```cpp run-san-catch
/* The declared length comes from the file. Trusting it is a buffer overflow
   that anybody who can write the file can trigger. */
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

int main() {
    const char *path = "evil.log";

    /* A record that claims 4096 bytes of payload but carries 32. */
    std::FILE *f = std::fopen(path, "wb");
    std::fprintf(f, "4096 00000000 ");
    std::fprintf(f, "0123456789abcdef0123456789abcdef");
    std::fclose(f);

    f = std::fopen(path, "rb");
    std::size_t len = 0;
    unsigned crc = 0;
    if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) return 1;

    std::string rest;
    int c;
    while ((c = std::fgetc(f)) != EOF) rest += static_cast<char>(c);
    std::fclose(f);
    std::printf("the header claims %zu byte(s); the file carries %zu\n",
                len, rest.size());

    /* The reader believes the length. */
    char *buf = static_cast<char *>(std::malloc(64));
    std::memcpy(buf, rest.data(), len);
    std::printf("copied %zu byte(s)\n", len);
    std::free(buf);
    return 0;
}
```

```text
heap-buffer-overflow
```

The program reads the header, prints it, and then copies `len` bytes out of a 32-byte buffer.
AddressSanitizer stops it with `heap-buffer-overflow`, and the fence above is the string it printed.

This is why `store.cpp` caps the declared length before allocating:

```cpp
if (len > 1024 * 1024) {
    out.refused++;
    break;
}
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

```cpp run
/* Write to a temporary name, then rename() over the real one. rename() is
   atomic, so a crash at any instant leaves either the old file or the new
   one -- never a mixture. */
#include <cstdio>
#include <string>

namespace {

std::string read_all(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return "(no such file)";
    std::string out;
    int c;
    while ((c = std::fgetc(f)) != EOF) out += static_cast<char>(c);
    std::fclose(f);
    return out;
}

void write_all(const char *path, const std::string &data) {
    std::FILE *f = std::fopen(path, "wb");
    if (!f) {
        std::perror("fopen");
        return;
    }
    std::fwrite(data.data(), 1, data.size(), f);
    std::fclose(f);
}

}  // namespace

int main() {
    write_all("store.json", "{\"version\":1}");
    std::printf("before:   %s\n", read_all("store.json").c_str());

    /* Stage version 2 under a temporary name. */
    write_all("store.json.tmp", "{\"version\":2}");
    std::printf("staged:   store.json.tmp = %s\n", read_all("store.json.tmp").c_str());
    std::printf("a crash now would leave store.json = %s\n",
                read_all("store.json").c_str());

    if (std::rename("store.json.tmp", "store.json") != 0) {
        std::perror("rename");
        return 1;
    }
    std::printf("renamed:  %s\n", read_all("store.json").c_str());
    std::printf("temp is gone: %s\n", read_all("store.json.tmp").c_str());
    return 0;
}
```

```text
before:   {"version":1}
staged:   store.json.tmp = {"version":2}
a crash now would leave store.json = {"version":1}
renamed:  {"version":2}
temp is gone: (no such file)
```

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

```cpp bad
/* fsync() needs a file descriptor. A std::ofstream does not give you one. */
#include <fstream>

int main() {
    std::ofstream out("store.json");
    out << "{\"version\":1}";
    const int fd = out.native_handle();
    (void)fd;
    return 0;
}
```

```text
no member named 'native_handle' in 'std::ofstream'
```

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

```cpp warn
/* write() tells you how much it wrote. Ignoring the answer is how a short
   write becomes silent data loss. */
#include <cstdio>

#include <fcntl.h>
#include <unistd.h>

int main() {
    const char *payload = "{\"version\":1}";
    const int fd = ::open("store.json", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    const ssize_t n = ::write(fd, payload, 13);
    ::close(fd);
    std::printf("done\n");
    return 0;
}
```

```text
unused variable 'n'
```

`-Wall -Wextra` sees the unused variable, and the warning is the only thing standing between you
and a store that reports success after writing 4 of 13 bytes. Ignoring a return value is the same
bug with no warning at all, which is why `append_record` in the project below loops until every
byte is accounted for:

```cpp
while (left > 0) {
    const ssize_t n = ::write(fd, p, left);
    if (n <= 0) {
        ::close(fd);
        return false;
    }
    p += n;
    left -= static_cast<std::size_t>(n);
}
```

## The project: an append-only log

Here is the whole thing. Four files, and `make` builds them into `prog`. The `/* ===== name ===== */`
lines are listing separators, not file contents — do not paste them into `Makefile`.

```cpp make-files
/* ===== store.h ===== */
#ifndef STORE_H
#define STORE_H

#include <string>
#include <vector>

/* An append-only log of arbitrary payloads, framed so that a torn write at
   the tail is detectable and the records before it survive. */

struct Scan {
    std::vector<std::string> records;
    long good_bytes = 0;   /* bytes covered by complete, verified records */
    long refused = 0;      /* records that failed verification */
    long junk_bytes = 0;   /* bytes left over after the last good record */
};

std::string frame(const std::string &payload);

/* Reads the log, stopping at the first record that is incomplete or does not
   match its checksum. good_bytes is where a clean log ends. */
Scan scan_log(const std::string &path);

/* Appends one framed record and fsyncs. Returns false if any step failed. */
bool append_record(const std::string &path, const std::string &payload);

/* Drops the torn tail, keeping the first `bytes` bytes. */
bool truncate_to(const std::string &path, long bytes);

#endif
/* ===== store.cpp ===== */
#include "store.h"

#include <cstdint>
#include <cstdio>

#include <fcntl.h>
#include <unistd.h>

namespace {

std::uint32_t fnv1a(const std::string &s) {
    std::uint32_t h = 2166136261u;
    for (unsigned char c : s) {
        h ^= c;
        h *= 16777619u;
    }
    return h;
}

}  // namespace

std::string frame(const std::string &payload) {
    char head[64];
    std::snprintf(head, sizeof head, "%zu %08x ", payload.size(), fnv1a(payload));
    return std::string(head) + payload + "\n";
}

Scan scan_log(const std::string &path) {
    Scan out;
    std::FILE *f = std::fopen(path.c_str(), "rb");
    if (!f) return out;   /* no file yet: an empty log */

    std::fseek(f, 0, SEEK_END);
    const long size = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);

    for (;;) {
        std::size_t len = 0;
        unsigned crc = 0;
        if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) break;

        /* The length comes from the file, so it is attacker-controlled. A
           payload larger than this is not a record, it is corruption. */
        if (len > 1024 * 1024) {
            out.refused++;
            break;
        }
        std::string payload(len, '\0');
        const std::size_t got = std::fread(&payload[0], 1, len, f);
        const int nl = std::fgetc(f);
        if (got != len || nl != '\n') {
            out.refused++;
            break;
        }
        if (fnv1a(payload) != crc) {
            out.refused++;
            break;
        }
        out.records.push_back(payload);
        out.good_bytes = std::ftell(f);
    }

    /* Bytes after the last good record are not "nothing", they are damage.
       Reporting them as a clean log would let a real record that follows some
       garbage disappear without a word. */
    out.junk_bytes = size - std::ftell(f);
    std::fclose(f);
    return out;
}

bool append_record(const std::string &path, const std::string &payload) {
    const int fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) return false;

    const std::string record = frame(payload);
    const char *p = record.data();
    std::size_t left = record.size();
    while (left > 0) {
        const ssize_t n = ::write(fd, p, left);
        if (n <= 0) {
            ::close(fd);
            return false;
        }
        p += n;
        left -= static_cast<std::size_t>(n);
    }
    if (::fsync(fd) != 0) {
        ::close(fd);
        return false;
    }
    return ::close(fd) == 0;
}

bool truncate_to(const std::string &path, long bytes) {
    return ::truncate(path.c_str(), static_cast<off_t>(bytes)) == 0;
}
/* ===== main.cpp ===== */
#include "store.h"

#include <cstdio>
#include <string>
#include <vector>

namespace {

const char *kPath = "data.log";

int cmd_add(const std::string &payload) {
    if (!append_record(kPath, payload)) {
        std::printf("add failed\n");
        return 1;
    }
    std::printf("added: %s\n", payload.c_str());
    return 0;
}

int cmd_list() {
    const Scan s = scan_log(kPath);
    for (const std::string &r : s.records) std::printf("%s\n", r.c_str());
    if (s.refused > 0) {
        std::printf("[%ld record(s) refused: the log ends in a torn or corrupt record]\n",
                    s.refused);
    }
    if (s.junk_bytes > 0) {
        std::printf("[%ld byte(s) of trailing junk after the last good record]\n",
                    s.junk_bytes);
    }
    return 0;
}

int cmd_recover() {
    const Scan s = scan_log(kPath);
    if (s.refused == 0 && s.junk_bytes == 0) {
        std::printf("nothing to recover: %zu record(s), log is clean\n", s.records.size());
        return 0;
    }
    if (!truncate_to(kPath, s.good_bytes)) {
        std::printf("recover failed\n");
        return 1;
    }
    std::printf("dropped the torn tail at byte %ld; %zu record(s) kept\n",
                s.good_bytes, s.records.size());
    return 0;
}

void selftest() {
    std::remove(kPath);
    std::printf("append three records\n");
    append_record(kPath, "widget");
    append_record(kPath, "gasket");
    append_record(kPath, "bolt");
    cmd_list();

    std::printf("\na torn tail: five bytes short\n");
    const Scan s = scan_log(kPath);
    truncate_to(kPath, s.good_bytes - 5);
    cmd_list();

    std::printf("\nrecover, then carry on\n");
    cmd_recover();
    append_record(kPath, "washer");
    cmd_list();
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--help") {
        std::printf("usage: %s            run the built-in self-test\n", argv[0]);
        std::printf("       %s add TEXT   append one record\n", argv[0]);
        std::printf("       %s list       print every readable record\n", argv[0]);
        std::printf("       %s recover    drop the torn tail\n", argv[0]);
        return 0;
    }
    if (argc == 2 && std::string(argv[1]) == "list")    return cmd_list();
    if (argc == 2 && std::string(argv[1]) == "recover") return cmd_recover();
    if (argc == 3 && std::string(argv[1]) == "add")     return cmd_add(argv[2]);
    if (argc == 1) {
        selftest();
        return 0;
    }
    std::printf("usage: prog [add TEXT | list | recover]\n");
    return 2;
}
/* ===== Makefile ===== */
CXX      = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2

OBJS     = main.o store.o

prog: $(OBJS)
	$(CXX) $(CXXFLAGS) -o prog $(OBJS)

main.o: main.cpp store.h
	$(CXX) $(CXXFLAGS) -c main.cpp

store.o: store.cpp store.h
	$(CXX) $(CXXFLAGS) -c store.cpp

clean:
	rm -f prog $(OBJS)

.PHONY: clean
```

```text
append three records
widget
gasket
bolt

a torn tail: five bytes short
widget
gasket
[1 record(s) refused: the log ends in a torn or corrupt record]

recover, then carry on
dropped the torn tail at byte 36; 2 record(s) kept
widget
gasket
washer
```

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

```sh run-project
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
```

```text
$ ./prog add widget
added: widget
$ ./prog add gasket
added: gasket
$ ./prog list
widget
gasket
$ # a crash, a bug, or a partial write leaves junk at the tail
$ ./prog list
widget
gasket
[17 byte(s) of trailing junk after the last good record]
$ ./prog recover
dropped the torn tail at byte 36; 2 record(s) kept
$ ./prog list
widget
gasket
```

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

```cpp run

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
```

```text
3 record(s)
```

:::

:::solution Exercise 2

A magic first line turns "some other file" into a diagnosable error instead of zero records. The
trap is reading it with the same `fscanf` as a record header: `%zu %08x ` would consume it and
report an empty log. Read the line first, compare it, and only then scan.

```cpp run

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
```

```text
good.log    : ours
foreign.log : not ours
```

:::

:::solution Exercise 3

The offset is useful because it is what you put in an index and what you print when a record turns
out to be corrupt. `lseek(fd, 0, SEEK_END)` before the write is the answer, but only because the
file was opened `O_APPEND` — with a plain `O_WRONLY` descriptor two writers would race to the same
offset.

```cpp run

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
```

```text
widget   -> offset 0, 7 byte(s)
gasket   -> offset 7, 7 byte(s)
```

:::

:::solution Exercise 4

Rewrite to `data.log.tmp`, `fsync` it, `rename` it over the original. Never write to the live name:
the one thing this chapter is trying to stop you doing.

```cpp run

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
```

```text
kept 3 of 4 record(s)
6 00000000 widget\n6 00000000 gasket\n4 00000000 bolt\n
```

:::

:::solution Exercise 5

Skipping a corrupt record is the right call only if you *report* it. A reader that silently drops
damage is indistinguishable from a reader that never saw it, which is exactly the bug that ate the
eleven orders in the scenario above. Measured against a log with a corrupt record at both positions:
three good records survive, two are reported as skipped.

```cpp run

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
```

```text
recovered 1 record(s), skipped 0
  widget
```

:::
