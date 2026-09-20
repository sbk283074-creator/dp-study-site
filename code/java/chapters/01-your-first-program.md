---
chapter: 1
part: 1
title: Your First Program, and Why It Looks Like That
summary: Write, compile and run a Java program; know what every word of `public static void main(String[] args)` is for, and how to print and read arguments.
minutes: 40
tags: [main, printing, arguments, packages, classpath]
---

Every Java program you will ever run starts the same way, and the ceremony around that start is a
dozen words you did not choose. This chapter explains each of them, because knowing why they are
there turns "Java is verbose" into "Java is explicit" — and it means that when a program refuses to
start, you will know which of the twelve words to look at first.

## The smallest program Java will run

```java run
public class Greet {
    public static void main(String[] args) {
        System.out.println("Java says hello");
    }
}
```

```text
Java says hello
```

Three things happen here, and each is a rule rather than a style choice.

**The file must be named `Greet.java`.** A public class and its file share a name, exactly.
**Everything is inside a class.** Java has no top-level functions, so there is no way to write a
program that is not a class. Try it and the compiler says what it wanted:

```java bad
System.out.println("no class here");
```

```text
error: class, interface, enum, or record expected
```

**`main` is the one name the JVM looks for.** A class without it compiles happily and is useless as
a starting point.

## Every word of `public static void main(String[] args)`

| Word | What it does | What happens without it |
|---|---|---|
| `public` | The JVM starts your program from outside the class, so the method must be reachable from anywhere. | `Main method not found` |
| `static` | The JVM calls it before any object exists. A non-static `main` would need an instance, and there is nobody to make one. | `Main method is not static` |
| `void` | The JVM ignores what you return, so it insists you return nothing. | `Main method must return a value of type void` |
| `main` | The name the launcher looks up. Case matters. | `Main method not found` |
| `String[] args` | The command-line arguments, as an array. The parameter is always exactly this. | `Main method not found` |

The table is not theoretical — those are the three errors the JVM actually prints, and each one
names the word you got wrong. Here is the first of them, from a program that compiles cleanly and
still will not start:

```java throw
public class NoMain {
    public static void main(String args) {
        System.out.println("this line never prints");
    }
}
```

```text
Error: Main method not found in class NoMain
```

`String args` is a perfectly legal parameter — one string — so `javac` has nothing to complain
about. The program compiles, the class file exists, and the JVM rejects it at launch. This is the
one failure mode in Java that no compiler flag catches, which is why it earns a place in Chapter 1
instead of a footnote.

## Printing: `println`, `print`, `printf`

`System.out` is an object with methods on it, and the three you use constantly differ only in what
they do at the end:

```java run
public class Output {
    public static void main(String[] args) {
        System.out.println("println ends the line");
        System.out.print("print does not, so this continues ");
        System.out.println("and this finishes it");
        System.out.printf("printf formats: %d, %.2f, %s%n", 7, 3.14159, "text");
        System.out.printf("width: |%5d|%-5d|%05d|%n", 42, 42, 42);
        System.out.printf("a literal percent needs doubling: 100%%%n");
    }
}
```

```text
println ends the line
print does not, so this continues and this finishes it
printf formats: 7, 3.14, text
width: |   42|42   |00042|
a literal percent needs doubling: 100%
```

`%d` is an integer, `%.2f` a floating-point number to two decimal places, `%s` anything at all, and
`%n` a newline. That last one is worth memorising over `\n`: `%n` is the line separator of the
machine you are on, so it is `\r\n` on Windows and `\n` everywhere else, and your output looks right
on both.

:::pitfall The capital that costs ten minutes

Java is case-sensitive and `System`, `Out` and `Println` are three separate words to it. The
compiler's answer is `cannot find symbol`, which is accurate but does not tell you that you typed
`System.Out.println` instead of `System.out.println`. When you see `cannot find symbol` on
something you are certain exists, check the capitalisation before you check anything else.

```java bad
public class Case {
    public static void main(String[] args) {
        System.Out.println("capital O");
    }
}
```

```text
cannot find symbol
```
:::

## Arguments arrive as an array

Whatever you type after the class name lands in `args`, and `args.length` tells you how many there
were:

```sh run
cat > Args.java <<'EOF'
public class Args {
    public static void main(String[] args) {
        System.out.println("count = " + args.length);
        System.out.println("first = " + args[0]);
        System.out.println("last  = " + args[args.length - 1]);
    }
}
EOF
javac -d out Args.java
java -cp out Args alpha beta gamma
```

```text
count = 3
first = alpha
last  = gamma
```

`args` is always present and never null; with no arguments it is an array of length 0. That is
worth knowing before Chapter 5, where arrays get their own chapter and where `args[0]` on an empty
array becomes your first exception.

## A second class means a second file

One public class per file is the rule, so a program that needs a helper is two files. This is also
how you call a method that lives somewhere else:

```java run-files
// ===== Format.java =====
public class Format {
    public static String banner(String text) {
        return "*** " + text + " ***";
    }
}

// ===== Main.java =====
public class Main {
    public static void main(String[] args) {
        System.out.println(Format.banner("quill"));
    }
}
```

```text
*** quill ***
```

`Format.banner(...)` is a **static** call: no object is involved, you name the class and the method.
The banners (`// ===== Format.java =====`) are this book's way of showing several files in one
listing — they are comments, so the listing is still exactly what you would type, but you would put
each part in its own file.

:::scenario The class file is there and Java says it is not

You compiled successfully, `Main.class` is sitting in `out/`, and `java -cp out Main` answers
`Error: Could not find or load main class Main`. You check the spelling. You check the case. It is
right.

:::solution
Look for a `package` line at the top of the source. A class in a package has a **fully qualified
name** — package, dot, class — and that is the only name the JVM will accept. The class file is
written into a directory matching the package, under the classpath root:

```sh run
mkdir -p src/app
cat > src/app/Main.java <<'EOF'
package app;
public class Main {
    public static void main(String[] args) {
        System.out.println("found through the package");
    }
}
EOF
javac -d out src/app/Main.java
ls out/app
java -cp out Main 2>&1 | head -1
java -cp out app.Main
```

```text
Main.class
Error: Could not find or load main class Main
found through the package
```

The classpath is a list of *roots*, and the JVM turns a class name into a path underneath one of
them: `app.Main` becomes `out/app/Main.class`. `Main` on its own would be `out/Main.class`, which
does not exist — hence the error, which is telling the truth and is easy to misread as a spelling
problem. Get used to naming classes in full; every real project puts code in packages.
:::

## Key takeaways

- A runnable Java program is a public class with `public static void main(String[] args)`, in a file
  named after the class.
- `javac` produces a `.class` file of bytecode; `java` runs the **class**, named in full if it has a
  package. `java Main.class` is always wrong.
- A wrong `main` signature compiles and fails at launch with `Main method not found`, `not static`,
  or `must return a value of type void` — the JVM names the word you got wrong.
- `println` ends the line, `print` does not, `printf` formats; use `%n`, not `\n`, and `%%` for a
  literal percent.
- Command-line arguments arrive in `args`, an array that is empty rather than absent when you pass
  none.
- `-d out` keeps class files out of your source tree; `-cp out` tells the JVM where to look.

## Practice

- [ ] Write a program that prints a three-line title using `printf`, with the title supplied as a
      command-line argument and a fallback of `"untitled"` when none is given.
- [ ] Write a program with two classes: one holds `public static int square(int n)`, the other
      prints the squares of 1 to 5.
- [ ] Compile the previous program with `-d build` and run it from a different directory using an
      absolute `-cp`.
- [ ] Write a program whose class is in the package `tools.text` and run it. Then try running it
      without the package prefix and write down the exact error.
- [ ] Make `main` non-static on purpose, compile, and read the launcher's message. Put the one-line
      fix in a comment.

## Solutions

:::solution Exercise 1
`args.length == 0` is how you detect "no arguments", and remember that `args[0]` would throw if you
read it without checking.

```java run
public class Title {
    public static void main(String[] args) {
        String title = args.length == 0 ? "untitled" : args[0];
        System.out.printf("+%s+%n", "-".repeat(title.length() + 2));
        System.out.printf("| %s |%n", title);
        System.out.printf("+%s+%n", "-".repeat(title.length() + 2));
    }
}
```

```text
+----------+
| untitled |
+----------+
```
:::

:::solution Exercise 2
Two files, because one public class per file. A `static` method is called on the class, so no object
is needed.

```java run-files
// ===== Maths.java =====
public class Maths {
    public static int square(int n) {
        return n * n;
    }
}

// ===== Main.java =====
public class Main {
    public static void main(String[] args) {
        for (int n = 1; n <= 5; n++) {
            System.out.println(n + " squared = " + Maths.square(n));
        }
    }
}
```

```text
1 squared = 1
2 squared = 4
3 squared = 9
4 squared = 16
5 squared = 25
```
:::

:::solution Exercise 3
The classpath can be absolute, which is what a script or a build tool would use. Nothing about the
class file says where it will be run from.

```sh run
mkdir -p demo
cat > demo/Maths.java <<'EOF'
public class Maths {
    public static int square(int n) { return n * n; }
}
EOF
cat > demo/Main.java <<'EOF'
public class Main {
    public static void main(String[] args) {
        System.out.println("square of 6 = " + Maths.square(6));
    }
}
EOF
javac -d build demo/Maths.java demo/Main.java
cd /tmp && java -cp "$OLDPWD/build" Main
```

```text
square of 6 = 36
```
:::

:::solution Exercise 4
The package is part of the name; leaving it off gives you the same `Could not find or load main
class` as the scenario, and it is the single most common Java beginner error after a wrong `main`
signature.

```sh run
mkdir -p src/tools/text
cat > src/tools/text/Words.java <<'EOF'
package tools.text;
public class Words {
    public static void main(String[] args) {
        System.out.println("words, from a package");
    }
}
EOF
javac -d out src/tools/text/Words.java
java -cp out tools.text.Words
java -cp out Words 2>&1 | head -1
```

```text
words, from a package
Error: Could not find or load main class Words
```
:::

:::solution Exercise 5
A non-static `main` is an ordinary method that happens to be called `main`. The JVM needs to call it
before any object exists, so it insists on `static`.

```java throw
public class NotStatic {
    public void main(String[] args) {
        System.out.println("never runs");
    }
}
```

```text
Error: Main method is not static in class NotStatic
```

The fix is one word: `public static void main(String[] args)`.
:::
