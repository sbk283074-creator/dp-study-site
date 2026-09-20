---
chapter: 0
part: 0
title: How to Use This Book
summary: Know what you are building, how a Java program actually reaches the screen, and the two rules Java enforces that will cost you an afternoon if you meet them by accident.
minutes: 14
tags: [orientation, how to read, jvm, javac, tooling]
---

Java runs a large share of the world's serious software: bank back ends, Android apps, Kafka,
Hadoop, Minecraft. It is also the language most degrees and most coding interviews assume, and if
you are taking IB Computer Science it is one of the two languages the course is written for. This
book takes you from "I have never compiled anything" to shipping three real programs — a
command-line product, a web service and a game — and it does it by making you write code from the
first page, not by explaining syntax at you.

## What you are actually building

Three projects, each larger than the last:

| Project | What it is | Chapters | What it forces you to learn |
|---|---|---|---|
| **Quill** | A command-line vault for notes: add, search by text and tag, list, export | 18–23 | Interfaces as commands, exceptions that mean something, files, packaging a runnable JAR |
| **Bulletin** | A web service with real HTTP, HTML pages, forms, accounts and sessions | 24–30 | Sockets, the request/response cycle, templating and escaping, cookies |
| **Ironhold** | A game with a loop, input, sprites, collision and waves of enemies | 31–36 | A deterministic game loop, rendering, state, and why `double` beats `int` for timing |

They are not toys. Each one is built with the JDK alone, each one is compiled and run on this
machine before a line of it reaches a page, and each one is something you could keep using after
you finish the chapter.

## One rule for the whole book: no third-party libraries

There is no Maven, no Gradle, no Spring, no JUnit, and no JSON library anywhere in this book.
Every program compiles with `javac` and runs with `java`. That is not stubbornness; it is the
reason the book can make a promise most books cannot.

A Java tutorial that starts with Spring Boot starts with a `pom.xml` that downloads two hundred
jars, and from that moment the reader cannot tell whether a failure is their mistake or a
dependency they cannot see. Here, if a program does not work, there are exactly two files
involved: the one you typed and the JDK. And because there is nothing to download, every example
in this book was compiled and run on the machine that wrote it — the output you are about to read
is measured, not imagined.

Where a real project would reach for a library, the chapter says so and says what the library
saves you. By then you will know what it is doing underneath.

## How a Java program reaches the screen

This is the one thing to understand before Chapter 1, because it explains rules that otherwise
look arbitrary. C compiles your source into machine code for *this* processor. Python runs your
source directly. Java does neither: `javac` compiles your source into **bytecode**, a
machine-independent instruction set stored in a `.class` file, and `java` starts a JVM that runs
that bytecode — interpreting it at first, then compiling the hot parts to native code while the
program runs.

```sh run
cat > Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("Java says hello");
    }
}
EOF
javac Main.java
ls Main.*
java Main
```

```text
Main.class
Main.java
Java says hello
```

Two files in, two files out. `Main.java` is what you wrote; `Main.class` is bytecode. The second
command ran the class, and it did not mention the file at all — `java Main` names a *class*, not a
path. That distinction bites everyone once, so here it is deliberately:

```sh run
cat > Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("ok");
    }
}
EOF
javac Main.java
java Main.class 2>&1 | head -1
```

```text
Error: Could not find or load main class Main.class
```

`java` took the argument `Main.class`, looked for a class actually *named* `Main.class` — a dot is
legal in an identifier — and found nothing. `java Main` is right. `java Main.class` is wrong.

The bytecode itself carries the Java version it was built for, and you can read it:

```sh run
cat > Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("ok");
    }
}
EOF
javac Main.java
javap -p Main
echo "--- and the version it targets ---"
javap -verbose Main | grep -E "^  (major|minor) version"
```

```text
Compiled from "Main.java"
public class Main {
  public Main();
  public static void main(java.lang.String[]);
}
--- and the version it targets ---
  minor version: 0
  major version: 65
```

Major version 65 means Java 21: the class-file major version is the language level plus 44, so
Java 8 is 52, Java 17 is 61, Java 21 is 65. A JVM refuses to load bytecode newer than itself,
which is the whole reason "class file has wrong version" errors exist — and why you compile with
`--release 21` when you want your program to run on a Java 21 runtime even if your own JDK is
newer.

Every example in this book is compiled with `javac -Xlint:all -Werror --release 21`. Say the
version when you ask for help with something here; it matters.

## Two rules Java enforces that Python does not

**A public class must live in a file with the same name.** Python does not care what you call the
file. Java does, and the error names the fix:

```sh run
cat > Wrong.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("hi");
    }
}
EOF
javac Wrong.java 2>&1 | head -1
```

```text
Wrong.java:1: error: class Main is public, should be declared in a file named Main.java
```

**Everything lives inside a class.** There is no top-level function and no top-level `main`. Even
the entry point is a method with an exact signature — `public static void main(String[] args)` —
and a typo in it produces a program that compiles and then refuses to run. You will meet that
error in Chapter 1, on purpose.

Both rules feel like ceremony at first. They are what lets a compiler find any class in a project
of ten thousand files by name alone.

## This book checks itself

Every code block in this book carries a directive that says what must happen to it: `run` means it
compiles and prints exactly the output shown beneath it, `bad` means the compiler *rejects* it and
the quoted error is the real one, `warn` means it compiles but the compiler complains, `throw`
means it dies with the stated exception. A script reads those directives and executes every block:

```sh run
echo "python3 tools/verify_examples.py          # every chapter"
echo "python3 tools/verify_examples.py 00-how-to-use-this-book"
```

```text
python3 tools/verify_examples.py          # every chapter
python3 tools/verify_examples.py 00-how-to-use-this-book
```

That is why the transcripts above are trustworthy: this chapter's own blocks are re-compiled and
re-run by that script, and a hand-copied transcript that drifts from reality fails it. The script
has a `--self-test` of its own — a fixture that must pass and a fixture that must fail — because a
gate that has gone quietly blind is worse than no gate.

:::scenario You are handed a Java project and it does not start

Someone leaves you a folder of `.java` files and a note that says "run it". There is no
`README`, no `pom.xml`, and no obvious starting point.

:::solution
Find the entry point before you try to build anything. Every runnable Java program has a
`public static void main(String[] args)` somewhere, and there is usually one:

```sh run
cat > Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("bulletin starts");
    }
}
EOF
grep -rl "static void main" --include="*.java" .
echo "--- build it, then name the class, not the file ---"
javac -d out Main.java
java -cp out Main
```

```text
./Main.java
--- build it, then name the class, not the file ---
bulletin starts
```

Then `javac -d out Main.java` followed by `java -cp out Main`. Two habits make the rest easy:
always compile with `-d out` so class files do not litter the source tree, and always pass `-cp`
when running, so the JVM looks where you actually put the classes. If it still says
`Could not find or load main class`, you are naming a file, or your class has a `package`
declaration and you must name it with the package in front: `java -cp out com.acme.Main`.
:::

:::pitfall Copying a Java program into a differently named file

It happens constantly: you paste an example into `Test.java` or `Example.java`, and the compiler
answers `class Main is public, should be declared in a file named Main.java`. Beginners read that
as "Java is broken" and start renaming things at random. The rule is one line: a public type's
name and its file's name must match, exactly, including case. Rename the file, or make the class
non-public — not both, and not neither.
:::

## Key takeaways

- `javac` turns source into bytecode in a `.class` file; `java` runs that bytecode in a JVM. The
  two steps are separate and always will be.
- `java Main` names a **class**. `java Main.class` is an error that says `ClassNotFoundException`,
  because a dot is legal inside a class name.
- A public class must be declared in a file of the same name; the compiler error tells you the
  name it wanted.
- Class-file major version 65 means Java 21. The number is the language level plus 44, and a JVM
  will not load bytecode newer than itself.
- Every example here is compiled with `-Xlint:all -Werror --release 21` and run before it is
  printed. The harness that does it is `tools/verify_examples.py`, and it has its own self-test.
- This book uses no third-party libraries, so nothing you read depends on a download.

## Practice

- [ ] Write a program that prints the Java version it is running under, using
      `System.getProperty("java.version")`, and compile it with `--release 21`.
- [ ] Put a `public class Ledger` in a file called `Account.java`, read the compiler error, then
      fix it two different ways and say which way you would keep in a real project.
- [ ] Run `javap -verbose` on a class compiled with `--release 17` and one compiled with
      `--release 21`. Report both major versions and work out which JVMs can run each.
- [ ] Compile a program with `-d out` and then run it three ways: `java -cp out Main`,
      `java Main` from inside `out`, and `java -cp . Main`. Explain which two work and why.

## Solutions

:::solution Exercise 1
`System.getProperty` reads a JVM property; `java.version` is the runtime's version, which is not
necessarily the version you compiled for.

```java run
public class Version {
    public static void main(String[] args) {
        System.out.println("java.version  = " + System.getProperty("java.version"));
        System.out.println("class format  = " + (Runtime.version().feature() + 44));
    }
}
```

```text
java.version  = 21.0.12.1
class format  = 65
```

Measured on Temurin 21.0.12.1. Your first line will differ if your JDK differs; the second will be
65 on any Java 21 runtime.
:::

:::solution Exercise 2
Option one: rename the file to `Ledger.java`. Option two: drop `public`, which makes the class
package-private and lets the file be called anything. Keep the rename. A class you intend to use
from other packages should be public, and a file whose name does not match its content costs every
reader a moment of doubt forever.

```sh run
cat > Ledger.java <<'EOF'
public class Ledger {
    public static void main(String[] args) {
        System.out.println("ledger opens");
    }
}
EOF
javac -d out Ledger.java
java -cp out Ledger
```

```text
ledger opens
```
:::

:::solution Exercise 3
`--release 17` produces major version 61, `--release 21` produces 65. A Java 21 JVM runs both; a
Java 17 JVM runs the first and refuses the second with `UnsupportedClassVersionError`. That is
why `--release` exists: it lets a newer JDK emit bytecode an older runtime accepts, and it also
stops you from accidentally using an API that the older runtime does not have.

```sh run
cat > Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("same source, two targets");
    }
}
EOF
javac --release 17 -d out17 Main.java
javac --release 21 -d out21 Main.java
echo "release 17 -> $(javap -verbose -cp out17 Main | grep 'major' | tr -s ' ')"
echo "release 21 -> $(javap -verbose -cp out21 Main | grep 'major' | tr -s ' ')"
java -cp out17 Main
```

```text
release 17 ->  major version: 61
release 21 ->  major version: 65
same source, two targets
```
:::

:::solution Exercise 4
`java -cp out Main` works, because you told the JVM where the class lives. `java Main` from inside
`out` works, because the default classpath is the current directory. `java -cp . Main` from the
project root fails, because `Main.class` is in `out`, not in `.`; you get
`Could not find or load main class Main`. The classpath is a list of *roots*, not a list of files:
the JVM looks for `Main.class` underneath each root, following the package as directories.

```sh run
cat > Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("found me");
    }
}
EOF
javac -d out Main.java
java -cp out Main
cd out && java Main && cd ..
java -cp . Main 2>&1 | head -1
```

```text
found me
found me
Error: Could not find or load main class Main
```
:::
