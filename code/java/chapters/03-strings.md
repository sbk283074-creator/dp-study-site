---
chapter: 3
part: 1
title: Strings, and Why They Never Change
summary: Work with immutable strings, know what the string pool does to `==`, build text with StringBuilder, and handle characters that need two `char`s.
minutes: 50
tags: [strings, immutability, interning, StringBuilder, unicode]
---

A `String` in Java cannot be modified. Every method that looks like it changes one — `toUpperCase`,
`replace`, `concat`, `trim` — returns a **new** string and leaves the original alone. That single
design decision is why strings are safe to share between threads, why they can be cached, and why
building a sentence in a loop is the classic Java performance mistake. It is also why `==` on strings
appears to work in your first program and fails in your first real one.

## Nothing you do to a string changes it

```java run
public class Immutable {
    public static void main(String[] args) {
        String s = "hello";
        String upper = s.toUpperCase();
        System.out.println("upper    = " + upper);
        System.out.println("original = " + s);
        System.out.println("concat returned the same object: " + (s.concat("!") == s));
        System.out.println("equalsIgnorecase works: " + "Hello".equalsIgnoreCase("HELLO"));
    }
}
```

```text
upper    = HELLO
original = hello
concat returned the same object: false
equalsIgnorecase works: true
```

If you come from a language where strings are mutable, the habit to unlearn is calling a method and
expecting the variable to change. In Java you always assign the result: `s = s.toUpperCase();`

## The string pool, and why `==` sometimes works anyway

The compiler keeps one copy of every string literal it can see, and hands out references to it. Two
literals with the same text are therefore the *same object*, which is the only reason `==` ever
returns true for strings:

```java run
public class Pool {
    public static void main(String[] args) {
        String a = "ab";
        String b = "a" + "b";            // folded by the compiler into "ab"
        String c = new String("ab");     // explicitly a fresh object
        String d = "a".concat("b");      // computed at run time
        System.out.println("a == b (folded literal) : " + (a == b));
        System.out.println("a == c (new object)     : " + (a == c));
        System.out.println("a == d (computed)       : " + (a == d));
        System.out.println("a.equals(c)             : " + a.equals(c));
        System.out.println("a == c.intern()         : " + (a == c.intern()));
    }
}
```

```text
a == b (folded literal) : true
a == c (new object)     : false
a == d (computed)       : false
a.equals(c)             : true
a == c.intern()         : true
```

`intern()` puts a string into the pool and returns the pooled copy, which is the only legitimate way
to make `==` work — and it exists for memory, not for comparisons.

:::pitfall Comparing strings with `==`

```java
if (input == "yes") { ... }     // wrong, and it works sometimes
```

Two string literals are the same object, so `input == "yes"` is true when `input` was assigned the
literal `"yes"` and false when it came from a file, a socket, a database or `substring`. That is the
worst possible failure: correct while you test, wrong in production. Use `.equals()`, always, with no
exceptions and no shortcuts.
:::

Single quotes and double quotes are different types, and the compiler is firm about it:

```java bad
public class Quotes {
    public static void main(String[] args) {
        String s = 'c';
        System.out.println(s);
    }
}
```

```text
incompatible types: char cannot be converted to String
```

`'c'` is a `char`, a 16-bit number. `"c"` is a `String`. The distinction is not cosmetic — see the
last section of this chapter.

## The operations you use every day

```java run
import java.util.Arrays;

public class Operations {
    public static void main(String[] args) {
        System.out.println("length      : " + "quill".length());
        System.out.println("substring   : " + "abcdef".substring(2, 4));
        System.out.println("contains    : " + "quill".contains("uill"));
        System.out.println("replace     : " + "a-b-c".replace('-', '/'));
        System.out.println("join        : " + String.join("-", "x", "y", "z"));
        System.out.println("repeat      : " + "ab".repeat(3));
        System.out.println("split       : " + Arrays.toString("a,b,,c".split(",")));
        System.out.println("split(-1)   : " + Arrays.toString("a,b,,c".split(",", -1)));
        System.out.println("isBlank     : " + "   ".isBlank() + ", isEmpty: " + "   ".isEmpty());
        System.out.println("strip       : [" + "  padded  ".strip() + "]");
        System.out.println("format      : " + String.format("%s has %d notes", "quill", 3));
    }
}
```

```text
length      : 5
substring   : cd
contains    : true
replace     : a/b/c
join        : x-y-z
repeat      : ababab
split       : [a, b, , c]
split(-1)   : [a, b, , c]
isBlank     : true, isEmpty: false
strip       : [padded]
format      : quill has 3 notes
```

Three of those are worth committing to memory. `substring(start, end)` takes the end index as
**exclusive**, so `substring(2, 4)` is two characters. `split` takes a **regular expression**, not a
literal — splitting on `.` needs `"\\."`, because `.` means "any character". And `isBlank` asks
about whitespace while `isEmpty` asks about length zero, which are different questions for `"   "`.

## Text blocks for anything multi-line

Since Java 15, three double quotes open a **text block** — a string that may span lines and keeps its
formatting. Embedded HTML, SQL and JSON stop being a wall of concatenation:

```java run
public class Blocks {
    public static void main(String[] args) {
        String page = """
                <article class="note">
                  <h1>%s</h1>
                  <p>%d words</p>
                </article>
                """;
        System.out.println(page.formatted("First note", 240));
        System.out.println("--- indentation is stripped to the least-indented line ---");
        String indented = """
                line one
                  line two
                """;
        System.out.print(indented);
        System.out.println("--- a trailing backslash joins lines ---");
        System.out.println("""
                a very long sentence that \
                continues without a newline
                """);
    }
}
```

```text
<article class="note">
  <h1>First note</h1>
  <p>240 words</p>
</article>

--- indentation is stripped to the least-indented line ---
line one
  line two
--- a trailing backslash joins lines ---
a very long sentence that continues without a newline
```

`formatted(...)` is `String.format` as an instance method, which reads better than
`String.format(page, ...)` when the template is a variable.

## Building text in a loop

Because every `+` makes a new string, adding to one in a loop copies the whole thing each time. The
cost is quadratic, and it is measurable:

```java run
public class Building {
    static long millis(Runnable job) {
        long start = System.nanoTime();
        job.run();
        return (System.nanoTime() - start) / 1_000_000;
    }

    public static void main(String[] args) {
        final int n = 50_000;
        long concat = millis(() -> {
            String s = "";
            for (int i = 0; i < n; i++) s += "x";
        });
        long builder = millis(() -> {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) sb.append("x");
        });
        System.out.println("concat  : many copies of a growing string");
        System.out.println("builder : one mutable buffer");
        System.out.println("builder faster: " + (builder < concat));
    }
}
```

```text
concat  : many copies of a growing string
builder : one mutable buffer
builder faster: true
```

The exact milliseconds depend on the machine, so this chapter does not print them; the ordering does
not, and at fifty thousand appends it is not close. `StringBuilder` is the tool whenever the number
of appends is not known at compile time. Compilers do quietly use a `StringBuilder` for a single
expression like `a + b + c`, so this is about loops specifically — do not contort one-line
concatenations to avoid a builder that was never needed.

## A `char` is not always a character

Java strings are sequences of UTF-16 **code units**, and one `char` holds one of them. Characters
outside the Basic Multilingual Plane — emoji, most newer pictographs, some scripts — need **two**:

```java run
public class Unicode {
    public static void main(String[] args) {
        String emoji = "😀";
        System.out.println("length()        = " + emoji.length());
        System.out.println("codePointCount  = " + emoji.codePointCount(0, emoji.length()));
        System.out.println("charAt(0)       = " + Integer.toHexString(emoji.charAt(0)));
        System.out.println("codePointAt(0)  = " + Integer.toHexString(emoji.codePointAt(0)));
        String name = "Ada 😀";
        System.out.println("name length     = " + name.length());
        System.out.println("name code points= " + name.codePointCount(0, name.length()));
        String cut = name.substring(0, 5);
        System.out.println("cut             = " + cut);
        System.out.println("cut ends on a lone half: " + Character.isHighSurrogate(cut.charAt(4)));
    }
}
```

```text
length()        = 2
codePointCount  = 1
charAt(0)       = d83d
codePointAt(0)  = 1f600
name length     = 6
name code points= 5
cut             = Ada ?
cut ends on a lone half: true
```

`length()` counts code units, not characters. Slicing by code units can cut a surrogate pair in
half, and the broken half prints as `?` — which is what those stray question marks in production logs
usually are. When the text can contain emoji, iterate by code point
(`codePoints()`), count with `codePointCount`, and slice with `offsetByCodePoints`.

:::scenario A "20 character" preview renders a question mark

A list view shows the first twenty characters of each note. Notes with emoji in them end in `?`,
and the bug report says the database is corrupting text.

:::solution
The database is fine; `substring(0, 20)` counts code units and can stop between the two halves of one
character. Cut on a code-point boundary instead, and say in the code why:

```java run-files
// ===== Preview.java =====
public class Preview {
    /** First `max` characters, never splitting a surrogate pair. */
    public static String of(String text, int max) {
        if (text.codePointCount(0, text.length()) <= max) return text;
        int end = text.offsetByCodePoints(0, max);
        return text.substring(0, end) + "…";
    }
}

// ===== Main.java =====
public class Main {
    public static void main(String[] args) {
        String note = "Meeting notes 😀😀😀 and more text after";
        String naive = note.substring(0, 15);
        String safe = Preview.of(note, 15);
        System.out.println("naive: [" + naive + "]");
        System.out.println("safe : [" + safe + "]");
        System.out.println("naive ends on a half : " + Character.isHighSurrogate(naive.charAt(14)));
        System.out.println("safe ends on a half  : " + Character.isHighSurrogate(safe.charAt(safe.length() - 2)));
        System.out.println("safe code points     = " + safe.codePointCount(0, safe.length()));
    }
}
```

```text
naive: [Meeting notes ?]
safe : [Meeting notes 😀…]
naive ends on a half : true
safe ends on a half  : false
safe code points     = 16
```

`offsetByCodePoints(0, max)` converts "fifteen characters" into "this many code units", so the slice
lands between characters. The ellipsis is a single code point, which is why the safe version counts
sixteen rather than fifteen.
:::

## Key takeaways

- A `String` is immutable: every transforming method returns a new one, so assign the result.
- Compare strings with `.equals()` (or `equalsIgnoreCase`), never `==`. Literals are pooled, so `==`
  works until the string comes from somewhere else.
- `substring(start, end)` ends exclusively; `split` takes a regular expression; `isBlank` and
  `isEmpty` ask different questions.
- Text blocks (`"""`) hold multi-line text and strip the common indentation; `formatted(...)` fills
  them in.
- Use `StringBuilder` when appending in a loop. A single `a + b + c` expression is already fine.
- `length()` counts UTF-16 code units, not characters. Emoji need two, so use `codePointCount`
  and `offsetByCodePoints` when text can contain them.

## Practice

- [ ] Write a program that reads two strings and reports whether they are equal ignoring case and
      surrounding whitespace, without creating a third string unnecessarily.
- [ ] Turn `"one two three"` into `"ONE-TWO-THREE"` using `split`, a loop and `String.join`.
- [ ] Build a multiplication table with `StringBuilder` and print it as one string.
- [ ] Write `Preview.of` from the scenario so that a `max` larger than the text returns the text
      unchanged and `max` of zero returns just the ellipsis.
- [ ] Print every code point of `"A😀B"` as hexadecimal, and show what `charAt` alone would give.

## Solutions

:::solution Exercise 1
`strip()` removes Unicode whitespace and returns a new string; `equalsIgnoreCase` then does the
comparison. Comparing stripped copies avoids the trap of comparing a trimmed string to an untrimmed
one.

```java run
public class Compare {
    public static void main(String[] args) {
        String a = "  Hello  ";
        String b = "HELLO";
        System.out.println("raw equal      : " + a.equals(b));
        System.out.println("raw ignore case: " + a.equalsIgnoreCase(b));
        System.out.println("stripped       : " + a.strip().equalsIgnoreCase(b.strip()));
    }
}
```

```text
raw equal      : false
raw ignore case: false
stripped       : true
```
:::

:::solution Exercise 2
`split(" ")` splits on a single space; `" +"` would be the regular expression for "one or more
spaces", which is usually what you want with real input.

```java run
import java.util.Arrays;

public class Words {
    public static void main(String[] args) {
        String[] parts = "one two three".split(" +");
        for (int i = 0; i < parts.length; i++) parts[i] = parts[i].toUpperCase();
        System.out.println(Arrays.toString(parts));
        System.out.println(String.join("-", parts));
    }
}
```

```text
[ONE, TWO, THREE]
ONE-TWO-THREE
```
:::

:::solution Exercise 3
One builder, one string at the end. Building this with `+=` inside the double loop would allocate a
new string twice per cell.

```java run
public class Table {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        for (int row = 1; row <= 3; row++) {
            for (int col = 1; col <= 3; col++) {
                sb.append(String.format("%3d", row * col));
            }
            sb.append('\n');
        }
        System.out.print(sb);
    }
}
```

```text
  1  2  3
  2  4  6
  3  6  9
```
:::

:::solution Exercise 4
The two edge cases are the ones a tester will find: `max` beyond the end, and `max` of zero. Both are
one line once `codePointCount` is the thing being compared.

```java run
public class Preview {
    static String of(String text, int max) {
        if (max <= 0) return "…";
        if (text.codePointCount(0, text.length()) <= max) return text;
        return text.substring(0, text.offsetByCodePoints(0, max)) + "…";
    }
    public static void main(String[] args) {
        String note = "Short note";
        System.out.println("[" + of(note, 100) + "]");
        System.out.println("[" + of(note, 0) + "]");
        System.out.println("[" + of("Exactly ten", 10) + "]");
        System.out.println("[" + of("Exactly ten", 9) + "]");
    }
}
```

```text
[Short note]
[…]
[Exactly te…]
[Exactly t…]
```
:::

:::solution Exercise 5
`codePoints()` returns a stream of `int` code points, which sidesteps the whole surrogate question.
Iterating `charAt` instead would report four "characters" for a three-character string.

```java run
public class CodePoints {
    public static void main(String[] args) {
        String s = "A😀B";
        System.out.println("length        = " + s.length());
        System.out.println("code points   = " + s.codePointCount(0, s.length()));
        s.codePoints().forEach(cp -> System.out.println("  U+" + Integer.toHexString(cp).toUpperCase()));
    }
}
```

```text
length        = 4
code points   = 3
  U+41
  U+1F600
  U+42
```
:::
