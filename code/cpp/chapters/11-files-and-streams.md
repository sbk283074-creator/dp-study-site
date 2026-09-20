---
chapter: 11
part: 2
title: Files and Streams
summary: Read and write files with the FILE handle, loop over lines without double-counting the last one, parse fields, store records in binary, and find out why gets was deleted from the language.
minutes: 55
tags: [file, fopen, fclose, fgets, fprintf, fscanf, fread, fwrite, feof, errno]
---

Every program in this book so far has lost its data when it exits. A file is how that stops being true,
and C's approach is a `FILE *` — an opaque handle to a *stream*, which is a buffered sequence of bytes
that may be a file on disk, the terminal, a pipe, or nothing at all. Once you can name a stream you can
write to it and read from it with the same functions, which is why `fprintf(stdout, ...)` and
`fprintf(f, ...)` are the same operation. The chapter's real subject, though, is the loop that reads
lines, because the obvious way to write it is wrong and the wrong version passes every test you would
think to run.

## Opening and closing

`fopen` takes a path and a mode, and returns a `FILE *` or `NULL`. There is no exception and no default:
if you do not check for `NULL`, the first use crashes.

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *out = fopen("notes.txt", "w");

    if (out == NULL) {
        printf("could not open for writing\n");
        return 1;
    }
    fprintf(out, "alpha\n");
    fprintf(out, "beta\n");

    if (fclose(out) != 0) {
        printf("could not flush notes.txt\n");
        return 1;
    }
    printf("wrote notes.txt\n");

    FILE *in = fopen("notes.txt", "r");

    if (in == NULL) {
        printf("could not open for reading\n");
        return 1;
    }

    char line[64];
    int count = 0;

    while (fgets(line, sizeof(line), in) != NULL) {
        count++;
        printf("line %d is %zu characters\n", count, strlen(line));
    }
    fclose(in);
    printf("total %d lines\n", count);

    remove("notes.txt");
    return 0;
}
```

```text
wrote notes.txt
line 1 is 6 characters
line 2 is 5 characters
total 2 lines
```

Two things in that output are worth reading twice. `alpha` is five letters and the line reports six,
because **`fgets` keeps the newline**. That is a feature, not a bug: it is how you tell a complete line
from one that was cut off by the buffer, which is the pitfall at the end of this chapter. And `fclose`
has a return value that is being checked. For a stream you have been writing to, `fclose` is the call
that actually flushes the buffer to disk, and it can fail — a full disk is reported *here*, not at
`fprintf`. Ignoring it means a program that reports success and produced a truncated file.

The mode strings are worth memorising:

| Mode | Meaning |
|---|---|
| `"r"` | Read. Fails if the file does not exist. |
| `"w"` | Write. Creates the file, or **truncates** it to zero length if it exists. |
| `"a"` | Append. Creates the file, or writes at the end if it exists. |
| `"r+"` | Read and write an existing file, without truncating. |
| `"w+"` | Read and write, truncating first. |
| `"a+"` | Read anywhere, write only at the end. |
| `"rb"`, `"wb"`, `"ab"` | The same, in binary. On Unix the `b` changes nothing; on Windows it stops newline translation. |

`"w"` destroying an existing file is the single most expensive typo in C. And the mode is checked at
runtime, not at compile time, so a bad one is a `NULL` rather than a build error:

```c run
#include <stdio.h>

int main(void) {
    FILE *f = fopen("notes.txt", "q");

    if (f == NULL) {
        printf("bad mode rejected\n");
        return 0;
    }
    fclose(f);
    printf("opened\n");
    return 0;
}
```

```text
bad mode rejected
```

## Why the error is not in the message

`fopen` returning `NULL` tells you it failed. It does not tell you why, because the reason lives in
`errno`, a global set by the last failing library call. `strerror` turns it into words:

```c run
#include <errno.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *f = fopen("does-not-exist.txt", "r");

    if (f == NULL) {
        printf("open failed: %s\n", strerror(errno));
        return 0;
    }
    fclose(f);
    printf("opened\n");
    return 0;
}
```

```text
open failed: No such file or directory
```

`perror("fopen")` is the shorthand: it prints your label, a colon, the same message and a newline, to
`stderr`. Use `perror` for a human reading a terminal, and `strerror(errno)` when the message needs to
go into a log line or a buffer you are building. What you should not do is print "could not open file"
and nothing else — the difference between a missing file, a permissions problem and a full disk is in
`errno`, and it is the one piece of information you actually need.

## Reading lines

The loop to memorise is `while (fgets(line, sizeof(line), f) != NULL)`. `fgets` reads at most one fewer
than the size you give it, always terminates what it wrote, and returns `NULL` at end of file or on
error.

Because the newline is part of what it read, the first thing most programs do with a line is remove it.
`strcspn(line, "\n")` returns the index of the first newline, or the length of the string if there is
none — which makes it a safe one-liner for both cases:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *f = fopen("words.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("first\n", f);
    fputs("second\n", f);
    fclose(f);

    f = fopen("words.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[64];

    while (fgets(line, sizeof(line), f) != NULL) {
        line[strcspn(line, "\n")] = '\0';
        printf("[%s]\n", line);
    }
    fclose(f);

    remove("words.txt");
    return 0;
}
```

```text
[first]
[second]
```

`line[strcspn(line, "\n")] = '\0';` writes a terminator over the newline if there is one, and over the
existing terminator if there is not. Both cases are correct, which is why this idiom is preferred to
`strlen` plus a bounds check plus a special case.

`fgets` replaced `gets`, which read a line into a buffer with **no length argument at all** — it could
not know the buffer's size, so a long line was an unavoidable overflow. It was removed from the C
standard in C11. Apple's headers keep it for compatibility, which turns it into a warning rather than
an error:

```c warn
#include <stdio.h>

int main(void) {
    char buffer[64];

    gets(buffer);
    printf("%s\n", buffer);
    return 0;
}
```

```text
'gets' is deprecated
```

Read the full warning when you meet it: it does not say the function is old-fashioned, it says it cannot
be used safely. There is no input you can feed `gets` that makes it correct, which is why the fix is
always `fgets(buffer, sizeof(buffer), stdin)` and never a larger buffer.

## Writing

`fprintf` takes a stream as its first argument and is otherwise `printf`. `fputs` writes a string with
no formatting, and `fputc` writes one character. Because the format string is checked against the
arguments, the compiler catches the commonest mistake of passing the wrong thing:

```c warn
#include <stdio.h>

int main(void) {
    FILE *f = fopen("words.txt", "r");

    if (f == NULL) {
        return 1;
    }
    printf("%s\n", f);
    fclose(f);
    return 0;
}
```

```text
format specifies type 'char *' but the argument has type 'FILE *'
```

The `-Wformat` check runs on `fprintf` exactly as it does on `printf`, and it is one of the most valuable
warnings in C — it catches type mismatches, missing arguments, `%d` where a `double` was passed, and
this one, where the stream itself was handed over as if it were its contents.

`stdout` and `stderr` are `FILE *` values that already exist, so `fprintf(stdout, ...)` and `printf(...)`
are the same call. `stderr` is unbuffered and reserved for errors, which means an error message survives
a crash that loses the buffered `stdout`. Redirect the two separately and you can read the errors without
the output.

## Temporary files, size, and appending

`tmpfile()` returns a stream to a file with no name that is removed when it is closed — the right tool
for scratch data, and one that cannot collide with a real path:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *f = tmpfile();

    if (f == NULL) {
        printf("no temporary file\n");
        return 1;
    }
    for (int i = 1; i <= 3; i++) {
        fprintf(f, "row %d\n", i);
    }
    rewind(f);

    char line[64];

    while (fgets(line, sizeof(line), f) != NULL) {
        line[strcspn(line, "\n")] = '\0';
        printf("[%s]", line);
    }
    fclose(f);
    printf("\n");
    return 0;
}
```

```text
[row 1][row 2][row 3]
```

`rewind(f)` is `fseek(f, 0, SEEK_SET)` — it puts the read position back at the start, which is necessary
because the writes left it at the end. To measure a file, seek to the end and ask where you are:

```c run
#include <stdio.h>

int main(void) {
    FILE *f = fopen("size.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("alpha\n", f);
    fputs("beta\n", f);
    fclose(f);

    f = fopen("size.txt", "r");

    if (f == NULL) {
        return 1;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 1;
    }

    long size = ftell(f);

    rewind(f);

    int first = fgetc(f);

    fclose(f);
    printf("size = %ld bytes\n", size);
    printf("first character = %c\n", first);

    remove("size.txt");
    return 0;
}
```

```text
size = 11 bytes
first character = a
```

Eleven bytes is `alpha` plus a newline plus `beta` plus a newline — six plus five. `ftell` returns a
`long`, which is why the format is `%ld` and not `%d`. `fgetc` returns an `int` rather than a `char`,
deliberately: it has to be able to return `EOF`, which is `-1`, and a `char` cannot always represent
that. Comparing the result against `EOF` is the only correct end test for `fgetc`, and storing it in a
`char` is a classic bug.

`"a"` mode appends rather than truncating, which is what a log file needs:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *f = fopen("log.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("first\n", f);
    fclose(f);

    f = fopen("log.txt", "a");

    if (f == NULL) {
        return 1;
    }
    fputs("second\n", f);
    fclose(f);

    f = fopen("log.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[64];

    while (fgets(line, sizeof(line), f) != NULL) {
        line[strcspn(line, "\n")] = '\0';
        printf("[%s]", line);
    }
    fclose(f);
    printf("\n");

    remove("log.txt");
    return 0;
}
```

```text
[first][second]
```

## Parsing fields with fscanf

`fscanf` reads according to a format, and — this is the part people miss — it returns **how many items it
successfully converted**, not a boolean. Testing that return value against the number of fields you
asked for is what makes the loop terminate correctly:

```c run
#include <stdio.h>

int main(void) {
    FILE *f = fopen("pairs.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("1 10\n2 20\n3 30\n", f);
    fclose(f);

    f = fopen("pairs.txt", "r");

    if (f == NULL) {
        return 1;
    }

    int left = 0;
    int right = 0;
    int pairs = 0;
    int total = 0;

    while (fscanf(f, "%d %d", &left, &right) == 2) {
        pairs++;
        total += left + right;
    }
    fclose(f);

    printf("pairs = %d\n", pairs);
    printf("total = %d\n", total);

    remove("pairs.txt");
    return 0;
}
```

```text
pairs = 3
total = 66
```

`== 2` is the whole loop condition. If a line contains something that is not a number, `fscanf` converts
what it can, returns a smaller count, and the loop stops — which is usually what you want for well-formed
input, and usually not what you want for input a human typed. When the format is not guaranteed, read the
line with `fgets` and parse it with `sscanf`, so a malformed line is one iteration rather than the end of
the file.

## Binary records

Text files are for humans. When a program is the only reader, `fwrite` and `fread` move whole structs in
one call:

```c run
#include <stdio.h>

typedef struct {
    int id;
    int score;
} Record;

int main(void) {
    Record written[3] = {{1, 90}, {2, 75}, {3, 88}};
    FILE *f = fopen("records.bin", "wb");

    if (f == NULL) {
        return 1;
    }

    size_t count = fwrite(written, sizeof(Record), 3, f);

    fclose(f);
    printf("wrote %zu records of %zu bytes\n", count, sizeof(Record));

    f = fopen("records.bin", "rb");

    if (f == NULL) {
        return 1;
    }

    Record read_back[3];
    size_t got = fread(read_back, sizeof(Record), 3, f);

    fclose(f);

    for (size_t i = 0; i < got; i++) {
        printf("id %d score %d\n", read_back[i].id, read_back[i].score);
    }

    remove("records.bin");
    return 0;
}
```

```text
wrote 3 records of 8 bytes
id 1 score 90
id 2 score 75
id 3 score 88
```

`fwrite` takes an element size and a count, and returns the number of *elements* written, which should
equal the count. `fread` returns the number of elements actually read, so the loop bound is `got` rather
than `3` — that is how a short file is handled without a separate check.

A binary file like this is not portable, and the reason is chapter 9: `sizeof(Record)` is 8 here, and
would be 12 with a `char` member added because of padding. Different compilers, different platforms and
different optimisation settings produce different layouts, so a binary file is a contract with *your*
program on *your* machine. If two programs must exchange records, either agree on a byte layout and
write each field with `fwrite(&r.id, sizeof(int), 1, f)`, or use a text format.

:::scenario The report that counted its last row twice
A developer writes an analyser that reads a log file and counts the records. It works on every file they
try, except that the totals are always one too high:

```c run
#include <stdio.h>

int main(void) {
    FILE *f = fopen("records.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("alpha\n", f);
    fputs("beta\n", f);
    fclose(f);

    f = fopen("records.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[64];
    int count = 0;

    while (!feof(f)) {
        fgets(line, sizeof(line), f);
        count++;
        printf("%d: %s", count, line);
    }
    fclose(f);
    printf("counted %d records\n", count);

    remove("records.txt");
    return 0;
}
```

```text
1: alpha
2: beta
3: beta
counted 3 records
```

Two lines in the file, three counted, and the third prints `beta` again. The bug is the order of the
test and the read. `feof` does not predict the future — it reports whether a *previous* read already hit
the end, and it only becomes true *after* the failing read. So the loop runs one extra time: `fgets`
returns `NULL` and leaves `line` untouched, the buffer still holds `beta` from the previous iteration,
and the stale contents are counted as a fresh record.

This is the classic end-of-file bug, and it is worth noticing how well it hides. The program does not
crash. The output looks plausible. On a file whose last line is empty, or whose records are deduplicated
later, the error is invisible entirely. The only thing that gives it away is the arithmetic: the count
does not match the number of lines you can see.

:::solution Test the function's return value, not the stream's state
`fgets` already tells you whether it read anything. Its return value is the only signal you need, and it
is available *before* you use the buffer:

```c run
#include <stdio.h>

int main(void) {
    FILE *f = fopen("records.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("alpha\n", f);
    fputs("beta\n", f);
    fclose(f);

    f = fopen("records.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[64];
    int count = 0;

    while (fgets(line, sizeof(line), f) != NULL) {
        count++;
        printf("%d: %s", count, line);
    }
    fclose(f);
    printf("counted %d records\n", count);

    remove("records.txt");
    return 0;
}
```

```text
1: alpha
2: beta
counted 2 records
```

The rule generalises to every read function in the standard library: **the return value is the test, and
`feof` and `ferror` are for afterwards.** When the loop ends you can call `feof(f)` to confirm it ended
because of the end of the file, and `ferror(f)` to find out whether it ended because something went
wrong. A loop that terminates on `feof` *before* reading has neither piece of information, because it
has not attempted the read that would set the flag.
:::

:::pitfall fgets splits a long line instead of failing
`fgets` reads at most `size - 1` characters. When a line is longer than the buffer, it does not tell you
— it returns the first part as a complete-looking line, and the rest arrives on the next iteration as
though it were another line:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *long_line = "this line is far longer than the buffer will hold\n";
    FILE *f = fopen("long.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs(long_line, f);
    fclose(f);

    f = fopen("long.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[16];
    int parts = 0;

    while (fgets(line, sizeof(line), f) != NULL) {
        parts++;

        size_t length = strlen(line);

        printf("part %d: %zu chars, ends with newline: %d\n",
               parts, length, line[length - 1] == '\n');
    }
    fclose(f);

    remove("long.txt");
    return 0;
}
```

```text
part 1: 15 chars, ends with newline: 0
part 2: 15 chars, ends with newline: 0
part 3: 15 chars, ends with newline: 0
part 4: 5 chars, ends with newline: 1
```

One line in the file, four iterations out. Nothing about the loop is wrong; the buffer is simply too
small, and `fgets` did exactly what it promises. This is why the newline is worth keeping rather than
stripping immediately: `line[length - 1] == '\n'` is the test that distinguishes a whole line from a
fragment, and it costs one comparison.

Two ways to fix it. Make the buffer bigger than any line you will meet, which is fine for a config file
and a guess for anything else — the program above has no upper bound on line length. Or handle the
fragment deliberately: when the line does not end in a newline and the buffer is full, keep reading and
appending until it does, growing the buffer with `realloc` if necessary. That is what a general-purpose
line reader has to do, and it is why `getline` exists in POSIX and why `std::getline` with `std::string`
in C++ makes the whole problem disappear — the string grows to fit, and there is no buffer size to get
wrong.
:::

## Key takeaways

- `fopen(path, mode)` returns a `FILE *` or `NULL`, and it must be checked. The mode is validated at
  runtime, so a typo is a `NULL` rather than a build error.
- `"w"` truncates an existing file. `"a"` appends. `"r"` fails if the file is absent.
- `fclose` returns an error status and is where a write actually reaches the disk. Check it for any
  stream you have written to.
- The reason for a failure is in `errno`; `perror("label")` prints it to `stderr` and
  `strerror(errno)` gives you the text to put anywhere else.
- `fgets(line, sizeof(line), f)` keeps the newline. Strip it with
  `line[strcspn(line, "\n")] = '\0';`, which is correct whether or not a newline is present.
- The line loop is `while (fgets(...) != NULL)`. Never `while (!feof(f))` — `feof` reports the *previous*
  read's outcome, so a loop that tests it before reading processes the last line twice.
- `gets` has no length parameter and cannot be used safely; it was removed from C11. Use `fgets`.
- `fscanf` returns the number of fields converted. Test it against the number you asked for. For
  unreliable input, read a line with `fgets` and parse it with `sscanf`.
- `fwrite` and `fread` take an element size and a count and return a count. Use the returned count as
  your loop bound so a short file is handled.
- A binary file written with `fwrite` on a struct is not portable, because `sizeof` includes padding and
  the layout is implementation-defined.
- `fgetc` returns an `int` so it can also return `EOF`. Store it in an `int`, not a `char`.
- `fgets` silently splits a line longer than the buffer. Keep the newline and test for it, or grow the
  buffer until the line is complete.

## Practice

- [ ] Write a program that creates a file with three lines, closes it, reopens it, and prints the file's
      size in bytes and the number of lines.
- [ ] Write `static size_t count_lines(const char *path)` that returns the number of lines in a file, or
      `0` if it cannot be opened. Test it on a file that exists and on one that does not.
- [ ] Write a program that writes five records of two `int`s each to a binary file and reads them back,
      printing the sum of the second field.
- [ ] Write `static int copy_file(const char *source, const char *destination)` that copies a text file
      line by line and returns `0` on success or `-1` on any failure, closing every stream it opened.
- [ ] Write a program that reads a file of one number per line and prints their sum, skipping lines that
      are not numbers and reporting how many it skipped.
- [ ] Take the `while (!feof(f))` program from the scenario and change the loop condition to
      `while (fgets(line, sizeof(line), f))`. Predict the count before running it, then explain the
      difference in one sentence.

## Solutions

:::solution Exercise 1
Write, close, then reopen to measure — the size is only final once the stream has been flushed.

```c run
#include <stdio.h>

int main(void) {
    FILE *f = fopen("report.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("alpha\n", f);
    fputs("beta\n", f);
    fputs("gamma\n", f);

    if (fclose(f) != 0) {
        return 1;
    }

    f = fopen("report.txt", "r");

    if (f == NULL) {
        return 1;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 1;
    }

    long size = ftell(f);

    rewind(f);

    char line[64];
    size_t lines = 0;

    while (fgets(line, sizeof(line), f) != NULL) {
        lines++;
    }
    fclose(f);

    printf("size = %ld bytes\n", size);
    printf("lines = %zu\n", lines);

    remove("report.txt");
    return 0;
}
```

```text
size = 17 bytes
lines = 3
```

Seventeen bytes is `alpha` plus a newline, `beta` plus a newline, and `gamma` plus a newline: six, five,
six. Measuring before the `fclose` would have been a mistake even though the program would often print
the same number, because the buffer is flushed at close time and a failure there means the file on disk
is shorter than the arithmetic says. Note that `fseek` is checked and `fclose` is called before
returning on the failure path — the two habits that make the function safe to call on a file that has
been deleted from under it.
:::

:::solution Exercise 2
Open, loop on `fgets`, close every path.

```c run
#include <stdio.h>

static size_t count_lines(const char *path) {
    FILE *f = fopen(path, "r");

    if (f == NULL) {
        return 0;
    }

    char line[128];
    size_t lines = 0;

    while (fgets(line, sizeof(line), f) != NULL) {
        lines++;
    }
    fclose(f);
    return lines;
}

int main(void) {
    FILE *f = fopen("three.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("one\n", f);
    fputs("two\n", f);
    fputs("three\n", f);
    fclose(f);

    printf("three.txt: %zu lines\n", count_lines("three.txt"));
    printf("missing.txt: %zu lines\n", count_lines("missing.txt"));

    remove("three.txt");
    return 0;
}
```

```text
three.txt: 3 lines
missing.txt: 0 lines
```

The function returns `0` both for an empty file and for one it could not open, which is a real limitation
— the caller cannot tell the two apart. A production version would return `int` with a negative error
code, or take a `size_t *out` and return a status, the way `str_init` did in the previous chapter. The
exercise keeps the simpler signature because the loop is the point: `while (fgets(...) != NULL)` counts
each line exactly once, including a final line with no newline at the end, which `feof`-based loops get
wrong in both directions. The `fclose` sits after the loop rather than inside it, so the file is closed
once regardless of how many lines were read.
:::

:::solution Exercise 3
Write with `fwrite`, read with `fread`, and use the returned count as the loop bound.

```c run
#include <stdio.h>

typedef struct {
    int id;
    int score;
} Record;

int main(void) {
    Record written[5] = {{1, 10}, {2, 20}, {3, 30}, {4, 40}, {5, 50}};
    FILE *f = fopen("scores.bin", "wb");

    if (f == NULL) {
        return 1;
    }

    size_t wrote = fwrite(written, sizeof(Record), 5, f);

    fclose(f);
    printf("wrote %zu of 5 records\n", wrote);

    f = fopen("scores.bin", "rb");

    if (f == NULL) {
        return 1;
    }

    Record back[5];
    size_t got = fread(back, sizeof(Record), 5, f);

    fclose(f);

    int total = 0;

    for (size_t i = 0; i < got; i++) {
        total += back[i].score;
    }
    printf("read %zu records, total score %d\n", got, total);

    remove("scores.bin");
    return 0;
}
```

```text
wrote 5 of 5 records
read 5 records, total score 150
```

Both calls return a count of elements, and both are printed rather than assumed. `wrote` should equal `5`
— if it does not, the disk is full or the stream failed, and `ferror(f)` would say which. `got` is the
loop bound because a short file is a legitimate outcome that should produce a smaller total rather than
reading uninitialised entries of `back`. The array is declared with five elements and the read asks for
five, so the only way to get fewer is a truncated file; using `got` means that case degrades instead of
misbehaving. Note that `Record` is 8 bytes here because it holds two `int`s with no padding between them,
which the previous chapter's `sizeof` idiom would confirm.
:::

:::solution Exercise 4
Two streams, two `fclose` calls, and a single exit path.

```c run
#include <stdio.h>

static int copy_file(const char *source, const char *destination) {
    FILE *in = fopen(source, "r");

    if (in == NULL) {
        return -1;
    }

    FILE *out = fopen(destination, "w");

    if (out == NULL) {
        fclose(in);
        return -1;
    }

    char line[128];
    int status = 0;

    while (fgets(line, sizeof(line), in) != NULL) {
        if (fputs(line, out) == EOF) {
            status = -1;
            break;
        }
    }
    if (ferror(in)) {
        status = -1;
    }
    if (fclose(out) != 0) {
        status = -1;
    }
    fclose(in);
    return status;
}

int main(void) {
    FILE *f = fopen("source.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("line one\n", f);
    fputs("line two\n", f);
    fclose(f);

    printf("copy: %d\n", copy_file("source.txt", "copy.txt"));
    printf("missing: %d\n", copy_file("nope.txt", "copy2.txt"));

    f = fopen("copy.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[128];

    while (fgets(line, sizeof(line), f) != NULL) {
        printf("copied: %s", line);
    }
    fclose(f);

    remove("source.txt");
    remove("copy.txt");
    return 0;
}
```

```text
copy: 0
missing: -1
copied: line one
copied: line two
```

Every failure path closes what it opened, which is why the `out == NULL` branch calls `fclose(in)` before
returning. The single `status` variable is the alternative to returning early from inside the loop, and
it exists because the two streams have to be closed in a defined order before the function exits — a
`return` inside the `while` would leak both. `ferror(in)` after the loop distinguishes a read that ended
because of the end of the file from one that ended because of a hardware error, which is the check the
scenario's solution promised. And `fclose(out) != 0` is checked before `fclose(in)`, because the write
stream is the one whose flush can lose data; if it fails, the copy is incomplete and the caller has to
know.
:::

:::solution Exercise 5
Read the line, then parse it, so a bad line costs one iteration rather than the rest of the file.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    FILE *f = fopen("numbers.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("10\n20\nnot a number\n30\n", f);
    fclose(f);

    f = fopen("numbers.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[64];
    int total = 0;
    int skipped = 0;

    while (fgets(line, sizeof(line), f) != NULL) {
        char *end = NULL;
        long value = strtol(line, &end, 10);

        if (end == line) {
            skipped++;
            continue;
        }
        total += (int)value;
    }
    fclose(f);

    printf("total = %d\n", total);
    printf("skipped = %d\n", skipped);

    remove("numbers.txt");
    return 0;
}
```

```text
total = 60
skipped = 1
```

`strtol` takes a pointer to a `char *` and stores there the address of the first character it could not
convert. If that address is still the start of the string, nothing was converted and the line is not a
number — which is the test `end == line`. This is the right shape for input you do not control: a
malformed line is counted and skipped, and the loop continues, where `fscanf(f, "%d", &value)` would have
returned `0` and left the offending text in the stream to trip up the next read. The `continue` is what
makes the `total +=` unreachable for a bad line, which is clearer than nesting the addition inside an
`else`. One caveat worth knowing: `strtol` also converts a line like `10 bananas` to `10` without
complaining, because it stops at the space and reports success. Use `end` to check that the remaining
characters are only whitespace if you need to reject that.
:::

:::solution Exercise 6
The count becomes `3` instead of `4`, and the change is one loop condition.

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *f = fopen("noeol.txt", "w");

    if (f == NULL) {
        return 1;
    }
    fputs("alpha\nbeta\ngamma", f);
    fclose(f);

    f = fopen("noeol.txt", "r");

    if (f == NULL) {
        return 1;
    }

    char line[64];
    int count = 0;

    while (fgets(line, sizeof(line), f) != NULL) {
        count++;
        line[strcspn(line, "\n")] = '\0';
        printf("%d: [%s]\n", count, line);
    }
    fclose(f);
    printf("counted %d lines\n", count);

    remove("noeol.txt");
    return 0;
}
```

```text
1: [alpha]
2: [beta]
3: [gamma]
counted 3 lines
```

The file has no newline after `gamma`, which is the case that breaks a `feof`-based loop in the other
direction: `feof` only becomes true *after* a read hits the end, so a loop that reads first and tests
afterwards will process `gamma` and then loop once more on a `NULL` return. Testing `fgets`'s return
value handles both a trailing newline and its absence with the same code, because the question it answers
is "did you give me a line", not "is the stream at the end". The one-sentence answer to the exercise: the
`feof` version asks about the stream's state *before* the read that would change it, so it always runs
one iteration too many.
:::
