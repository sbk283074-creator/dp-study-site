---
chapter: 6
part: 1
title: Methods, Overloading and the Call Stack
summary: Understand what a method call actually does -- copies the arguments onto a stack, runs the body, returns one value -- and why a swap method can never work.
minutes: 55
tags: [methods, parameters, overloading, varargs, recursion, call stack, StackOverflowError]
---

A method is a name for a computation, and Java's version of it has three properties that decide most
of the bugs in this chapter. Arguments are **copied**, always, so a method can never reassign a
caller's variable. A method returns **one** value, so anything more has to travel in an object. And a
call **pushes a frame** onto a stack, which is why recursion works, why it is bounded, and why a
method that calls itself without a base case dies with a `StackOverflowError` rather than hanging.

Chapter 5 chose *which* code runs. This chapter is about how the code is packaged and how the JVM
keeps track of it while it runs — the first place in this book where the language stops being syntax
and starts being a machine.

## Parameters are copies, always

Java is pass-by-value for every type, without exception. For a primitive, the value is copied. For an
object, the *reference* is copied — which is not the same thing as passing the object by reference,
and the difference is the source of a great deal of confusion:

```java run
public class PassByValue {
    static void tryToReassign(int number, int[] numbers) {
        number = 999;
        numbers = new int[]{999};
    }

    static void mutate(int[] numbers) {
        numbers[0] = 42;
    }

    public static void main(String[] args) {
        int value = 1;
        tryToReassign(value, new int[]{1});
        System.out.println("after tryToReassign, the caller's int is still " + value);

        int[] shared = {1, 2, 3};
        mutate(shared);
        System.out.println("after mutate, the caller's array starts with " + shared[0]);

        int[] original = {1, 2, 3};
        int[] alias = original;
        alias[0] = 99;
        System.out.println("the alias and the original are the same array: " + (original[0] == 99));

        int[] copy = original.clone();
        copy[0] = 7;
        System.out.println("a clone is a different array: " + (original[0] != copy[0]));
        System.out.println("original[0] = " + original[0] + ", copy[0] = " + copy[0]);
    }
}
```

```text
after tryToReassign, the caller's int is still 1
after mutate, the caller's array starts with 42
the alias and the original are the same array: true
a clone is a different array: true
original[0] = 99, copy[0] = 7
```

Read the first line as the rule: after `tryToReassign`, the caller's `int` is still `1`. The method
assigned `999` to its own copy and then threw the copy away. The same is true of the array parameter
in that method — `numbers = new int[]{999}` rebinds the *local copy of the reference* and the
caller's array is untouched.

The third line is where people conclude that Java passes objects by reference, and it is not that.
`mutate` received a copy of the reference, and through that copy it reached the caller's array and
changed a slot. The array object is shared; the variable is not. That is why `alias[0] = 99` changes
`original[0]` — `alias` and `original` hold the same reference — while `copy[0] = 7` does not, because
`clone()` produced a second array.

The practical rule: **a method can change the state of the object you hand it, and cannot change
which object your variable points at.** If you need a method to hand you back a new array, it has to
return it.

## One return value, and what to do when you need three

`return` hands back exactly one value. When a computation naturally produces several, the options in
order of preference are a small class that names them, an array when the elements are genuinely the
same kind of thing, and a mutation of an object you already passed in. The first is almost always
right, because a class gives the fields names and the array does not — `result[0]` and `result[1]`
say nothing about which is the minimum.

A holder class costs about ten lines and is worth writing rather than contorting the design:

```java
static final class MinMax {
    final int min;
    final int max;
    MinMax(int min, int max) { this.min = min; this.max = max; }
}
```

The `final` fields matter: a value that travels out of a method should not be modifiable by whoever
receives it, or the method's guarantee lasts exactly until the first caller decides otherwise. Java
16 added records, which write that class for you — `record MinMax(int min, int max) {}` — and Chapter
16 covers them. Until then the hand-written version is what a record compiles to anyway.

## Overloading: the compiler chooses, and it chooses at compile time

Two methods may share a name if their parameter lists differ. The compiler picks one when it compiles
the *call*, using the static types of the arguments, and this is worth knowing precisely because it
is not the same rule that governs overriding (Chapter 9):

```java run
public class Overload {
    static String pick(int value) {
        return "int";
    }

    static String pick(long value) {
        return "long";
    }

    static String pick(double value) {
        return "double";
    }

    static String pick(Integer value) {
        return "Integer";
    }

    static String pick(Object value) {
        return "Object";
    }

    static String pick(int a, int b) {
        return "two ints";
    }

    public static void main(String[] args) {
        byte small = 1;
        short medium = 2;
        char letter = 'x';
        Integer boxed = 5;

        System.out.println("pick(1)      -> " + pick(1));
        System.out.println("pick(1L)     -> " + pick(1L));
        System.out.println("pick(1.0)    -> " + pick(1.0));
        System.out.println("pick(1.0f)   -> " + pick(1.0f));
        System.out.println("pick(boxed)  -> " + pick(boxed));
        System.out.println("pick(\"text\") -> " + pick("text"));
        System.out.println("pick(byte)   -> " + pick(small));
        System.out.println("pick(short)  -> " + pick(medium));
        System.out.println("pick(char)   -> " + pick(letter));
        System.out.println("pick(1, 2)   -> " + pick(1, 2));
    }
}
```

```text
pick(1)      -> int
pick(1L)     -> long
pick(1.0)    -> double
pick(1.0f)   -> double
pick(boxed)  -> Integer
pick("text") -> Object
pick(byte)   -> int
pick(short)  -> int
pick(char)   -> int
pick(1, 2)   -> two ints
```

Three lines there repay study.

**`pick(1.0f)` returns `double`.** There is no `pick(float)`, so the compiler looks for a method it
can reach by *widening* the argument, and `float` widens to `double`. It does not box to `Float`,
because widening is tried in an earlier phase than boxing — a rule that exists to keep old code
compiling, and one you should not rely on reading about; print it once, as above, and remember the
shape.

**`pick(byte)`, `pick(short)` and `pick(char)` all return `int`.** The promotion ladder from Chapter 4
applies to arguments too: all three widen to `int`, and `pick(int)` is the most specific method
reachable. There is no `pick(byte)` and there does not need to be.

**`pick("text")` returns `Object`.** A `String` is an `Object` by widening reference conversion, and
with no `pick(String)` in sight that is the method chosen. This is the quiet one: an overload set
that accepts `Object` will absorb every argument nobody wrote a case for, and the compiler will not
mention it. If you did not intend to accept everything, do not offer `Object`.

When two candidates are equally specific, the call does not compile:

```java bad
public class OverloadAmbiguous {
    static String pick(int a, long b) {
        return "int, long";
    }

    static String pick(long a, int b) {
        return "long, int";
    }

    public static void main(String[] args) {
        System.out.println(pick(1, 2));
    }
}
```

```text
error: reference to pick is ambiguous
```

That is the compiler refusing to guess. Note what it is *not*: it is not an ambiguity that could be
resolved at run time by looking at the actual values, because there is nothing to look at — the
choice is made from the argument's *declared* type, before any value exists.

## Varargs: one parameter, any number of arguments

A parameter written `int...` accepts zero or more arguments, and inside the method it is an ordinary
array:

```java run
public class Varargs {
    static int total(int... values) {
        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        return sum;
    }

    static String kinds(Object... items) {
        StringBuilder builder = new StringBuilder();
        for (Object item : items) {
            if (builder.length() > 0) {
                builder.append(", ");
            }
            builder.append(item.getClass().getSimpleName());
        }
        return builder.toString();
    }

    public static void main(String[] args) {
        System.out.println("total()        = " + total());
        System.out.println("total(1)       = " + total(1));
        System.out.println("total(1, 2, 3) = " + total(1, 2, 3));

        int[] array = {4, 5, 6};
        System.out.println("total(array)   = " + total(array));

        System.out.println("kinds(1, \"a\")  = " + kinds(1, "a"));
        System.out.println("kinds()        = [" + kinds() + "]");
        System.out.println("inside the method the vararg is an array of length " + array.length);
    }
}
```

```text
total()        = 0
total(1)       = 1
total(1, 2, 3) = 6
total(array)   = 15
kinds(1, "a")  = Integer, String
kinds()        = []
inside the method the vararg is an array of length 3
```

`total()` with no arguments is legal and the array has length zero — which is why `int...` should
never be trusted to be non-empty. `total(array)` passing a real array is legal too, and it is the
same code path: the compiler wraps the arguments into an array only when they are not already one.

Two things to watch. A vararg parameter **must be last**, since anything after it would be
ambiguous. And an overload set that has both `m(int[])` and `m(int...)` will prefer the array version
when you pass an array and the vararg version when you pass separate values, which is exactly the
kind of subtlety `-Xlint:overloads` exists to flag.

## The call stack, and why recursion is bounded

Every call pushes a **frame** onto the thread's call stack: the parameters, the local variables, and
where to return to. A frame lives until its method returns, so a method that calls itself holds one
frame per level. Printing on the way in and on the way out makes that visible:

```java run
public class CallStack {
    static void enter(int n) {
        int local = n * 10;
        System.out.println("enter " + n + "   local = " + local);
        if (n > 0) {
            enter(n - 1);
        }
        System.out.println("leave " + n + "   local still " + local);
    }

    public static void main(String[] args) {
        enter(3);
        System.out.println("leave order is the reverse of enter order: each frame waits for the one below");
    }
}
```

```text
enter 3   local = 30
enter 2   local = 20
enter 1   local = 10
enter 0   local = 0
leave 0   local still 0
leave 1   local still 10
leave 2   local still 20
leave 3   local still 30
leave order is the reverse of enter order: each frame waits for the one below
```

The output is the stack drawn out over time. The `enter` lines run in one order and the `leave` lines
in the reverse, because each frame has to wait for the one it called — the `leave 3` line cannot run
until `enter 3`'s call to `enter 2` has returned, which cannot happen until everything below it has.
And every frame has its own `local`: `leave 1` still sees `10` after four other frames have come and
gone, because `local` is not shared state, it is a slot in a frame that is still alive.

That structure is what makes recursion elegant and what makes it bounded. The stack has a fixed size
— typically a megabyte or two per thread — so a recursion that is a million frames deep runs out:

```java throw
public class StackOverflow {
    static int descend(int depth) {
        return descend(depth + 1) + 1;
    }

    public static void main(String[] args) {
        System.out.println(descend(0));
    }
}
```

```text
Exception in thread "main" java.lang.StackOverflowError
```

`StackOverflowError` is an `Error` rather than an `Exception`, which is deliberate: a program cannot
usefully recover from running out of stack, and catching it is a bad idea because the handler itself
needs stack to run. The fix is always structural — add a base case that is actually reached, or
convert the recursion to a loop, which uses one frame regardless of depth. Every recursive method
needs an argument that provably moves toward the base case on every call; `descend` above is the
method with no base case at all, and the compiler is happy to compile it.

:::pitfall The helper that swaps two values and does nothing

```java
static void swap(int a, int b) {
    int temp = a;
    a = b;
    b = temp;
}
```

This is the single most common first attempt at a utility method in Java, and it cannot work. `a` and
`b` are copies, so the method swaps its own two locals and returns, and the caller's variables are
exactly as they were. The compiler will not warn — the method is perfectly well-formed and simply has
no effect the caller can observe.

There are three honest fixes, and choosing between them is a design decision rather than a
workaround: swap the caller's array or list element if the values live in a container, swap the
fields of an object you were handed, or return a small holder type and let the caller assign it.
What you cannot do is make the language pass an `int` by reference.
:::

:::scenario The utility method that "worked in the test"

A developer writes `swap(int, int)` as part of a sorting routine, tests it by printing the two
parameters *inside* the method — where they are correctly swapped — and ships it. The sort produces
output that is mostly right, because most comparisons do not need a swap.

:::solution
The method swaps its own copies. Inside the method the values really are exchanged, which is why the
test passed; the caller's variables never change, which is why the sort is wrong.

```java run
public class Scenario {
    static void swapWrong(int a, int b) {
        int temp = a;
        a = b;
        b = temp;
    }

    static void swapArray(int[] pair) {
        int temp = pair[0];
        pair[0] = pair[1];
        pair[1] = temp;
    }

    static final class Pair {
        int left;
        int right;

        Pair(int left, int right) {
            this.left = left;
            this.right = right;
        }

        @Override
        public String toString() {
            return "(" + left + ", " + right + ")";
        }
    }

    static void swapPair(Pair pair) {
        int temp = pair.left;
        pair.left = pair.right;
        pair.right = temp;
    }

    public static void main(String[] args) {
        int a = 1;
        int b = 2;
        swapWrong(a, b);
        System.out.println("after swapWrong(a, b): a = " + a + ", b = " + b);

        int[] pair = {1, 2};
        swapArray(pair);
        System.out.println("after swapArray:      " + pair[0] + ", " + pair[1]);

        Pair holder = new Pair(1, 2);
        swapPair(holder);
        System.out.println("after swapPair:       " + holder);

        System.out.println("only the two that received a reference changed the caller's state");
    }
}
```

```text
after swapWrong(a, b): a = 1, b = 2
after swapArray:      2, 1
after swapPair:       (2, 1)
only the two that received a reference changed the caller's state
```

The output is the diagnosis in three lines. `swapWrong` left the caller's `a` and `b` at `1` and `2`.
`swapArray` worked, because the *elements* of the array are reachable through the copied reference.
`swapPair` worked, for the same reason one level up: the fields of the object are reachable, so
mutating them is visible.

The generalisation is worth stating plainly, because it covers every version of this bug: **a method
cannot change the caller's variable, and can change anything the caller's variable points at.** When
a helper seems to have no effect, ask which of the two it was trying to do.
:::

## Key takeaways

- Java passes everything by value. A primitive is copied; an object's *reference* is copied, which is
  why a method can mutate the object and cannot reassign the caller's variable.
- `clone()` on an array produces a second array; `int[] b = a;` produces a second name for the same
  one. Changing a slot through either name is visible through both.
- A method returns exactly one value. Return a small holder class with `final` fields when a
  computation has several results, and let Chapter 16's records write that class for you.
- Overload resolution happens at compile time, using the arguments' declared types. Widening is tried
  before boxing, which is why `pick(1.0f)` reaches `pick(double)` and `pick(byte)` reaches `pick(int)`.
- An overload taking `Object` silently accepts every argument no other overload matches. If that is
  not the intent, do not offer it.
- Two equally specific overloads make the call ambiguous, and that is a compile error — the choice
  cannot be deferred to run time.
- A `int...` parameter accepts zero arguments and is an ordinary array inside the method, so it must
  be treated as possibly empty and must be the last parameter.
- Every call pushes a frame holding its own parameters and locals. Frames are released in reverse
  order, which is why a recursive method's work unwinds from the deepest call outward.
- The stack is bounded, so recursion without a reachable base case throws `StackOverflowError` — an
  `Error`, not an `Exception`, and not something to catch.

## Practice

- [ ] Write a method that returns the minimum, the maximum and the index of the maximum of an `int[]`
      in one object, and print all three.
- [ ] Write factorial twice — once recursively and once with a loop — and check that they agree for
      `0`, `1`, `5`, `10` and `20`, then show what `21!` does.
- [ ] Write a recursive binary search over a sorted array and check it on the first element, the
      last, a middle one and a value that is absent. Then compute the midpoint both ways for two
      large indices and explain the difference.
- [ ] Write Euclid's algorithm twice, recursively and with a loop, and check the two agree on pairs
      that include a zero.

## Solutions

:::solution Exercise 1
One pass, three answers, one object to carry them. The holder's fields are `final` so the caller
cannot edit the result after the fact:

```java run
public class Sol1 {
    static final class MinMax {
        final int min;
        final int max;
        final int indexOfMax;

        MinMax(int min, int max, int indexOfMax) {
            this.min = min;
            this.max = max;
            this.indexOfMax = indexOfMax;
        }
    }

    static MinMax minMax(int[] values) {
        int min = values[0];
        int max = values[0];
        int indexOfMax = 0;
        for (int i = 1; i < values.length; i++) {
            if (values[i] < min) {
                min = values[i];
            }
            if (values[i] > max) {
                max = values[i];
                indexOfMax = i;
            }
        }
        return new MinMax(min, max, indexOfMax);
    }

    public static void main(String[] args) {
        MinMax result = minMax(new int[]{7, 3, 9, 1, 9, 4});
        System.out.println("min          = " + result.min);
        System.out.println("max          = " + result.max);
        System.out.println("index of max = " + result.indexOfMax);
        System.out.println("a method returns one value, so the three answers travel in one object: "
                + (result.min < result.max));
    }
}
```

```text
min          = 1
max          = 9
index of max = 2
a method returns one value, so the three answers travel in one object: true
```

`indexOfMax` is `2` for `{7, 3, 9, 1, 9, 4}` — the *first* index holding the maximum, because the
comparison is `>` and a later equal value does not displace it. That is worth deciding explicitly in
any method that returns an index; `<` instead of `<=` is the whole difference between first and last.
:::

:::solution Exercise 2
The two versions are the same computation written two ways, and they agree on every input that does
not overflow:

```java run
public class Sol2 {
    static long factorialRecursive(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorialRecursive(n - 1);
    }

    static long factorialLoop(int n) {
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    public static void main(String[] args) {
        for (int n : new int[]{0, 1, 5, 10, 20}) {
            long recursive = factorialRecursive(n);
            long loop = factorialLoop(n);
            System.out.println(n + "! = " + recursive + "  (loop agrees: " + (recursive == loop) + ")");
        }
        System.out.println("20! still fits in a long : " + factorialLoop(20));
        System.out.println("21! overflows            : " + factorialLoop(21));
        System.out.println("and comes out negative   : " + (factorialLoop(21) < 0));
    }
}
```

```text
0! = 1  (loop agrees: true)
1! = 1  (loop agrees: true)
5! = 120  (loop agrees: true)
10! = 3628800  (loop agrees: true)
20! = 2432902008176640000  (loop agrees: true)
20! still fits in a long : 2432902008176640000
21! overflows            : -4249290049419214848
and comes out negative   : true
```

`20!` is `2432902008176640000`, the largest factorial a `long` can hold, and `21!` wraps to
`-4249290049419214848` — the Chapter 4 overflow, arriving inside a chapter about methods. The
recursive version has a second limit the loop does not: it needs one frame per level, so a factorial
large enough to overflow would first have to be small enough to fit on the stack.
:::

:::solution Exercise 3
Binary search is the recursion where the base case is not a value but a *failure*: `low > high` means
the range is empty and the target is not there:

```java run
public class Sol3 {
    static int search(int[] sorted, int target) {
        return search(sorted, target, 0, sorted.length - 1);
    }

    private static int search(int[] sorted, int target, int low, int high) {
        if (low > high) {
            return -1;
        }
        int mid = low + (high - low) / 2;
        if (sorted[mid] == target) {
            return mid;
        }
        if (sorted[mid] < target) {
            return search(sorted, target, mid + 1, high);
        }
        return search(sorted, target, low, mid - 1);
    }

    public static void main(String[] args) {
        int[] sorted = {1, 3, 5, 7, 9, 11, 13};
        for (int target : new int[]{1, 7, 13, 4}) {
            System.out.println("search(" + target + ") = " + search(sorted, target));
        }

        int low = 1_500_000_000;
        int high = 1_800_000_000;
        System.out.println("(low + high) / 2      = " + ((low + high) / 2));
        System.out.println("low + (high - low) / 2 = " + (low + (high - low) / 2));
    }
}
```

```text
search(1) = 0
search(7) = 3
search(13) = 6
search(4) = -1
(low + high) / 2      = -497483648
low + (high - low) / 2 = 1650000000
```

The last two lines are a genuine bug in the version everybody writes first. `(low + high) / 2`
overflows for large indices and returns `-497483648` — a negative midpoint, which then indexes an
array out of bounds or recurses forever. `low + (high - low) / 2` computes the same value without the
intermediate overflow. The array here is far too small to trigger it, which is exactly why the bug
survived for years in the JDK's own `binarySearch`.
:::

:::solution Exercise 4
Euclid's algorithm is the recursion with the shortest base case in computing: when the remainder is
zero, the other number is the answer.

```java run
public class Sol4 {
    static int gcdRecursive(int a, int b) {
        return b == 0 ? a : gcdRecursive(b, a % b);
    }

    static int gcdLoop(int a, int b) {
        while (b != 0) {
            int remainder = a % b;
            a = b;
            b = remainder;
        }
        return a;
    }

    public static void main(String[] args) {
        int[][] pairs = {{48, 18}, {17, 5}, {100, 0}, {0, 7}, {270, 192}};
        for (int[] pair : pairs) {
            int recursive = gcdRecursive(pair[0], pair[1]);
            int loop = gcdLoop(pair[0], pair[1]);
            System.out.println("gcd(" + pair[0] + ", " + pair[1] + ") = " + recursive
                    + "  (loop agrees: " + (recursive == loop) + ")");
        }
        System.out.println("a base case of b == 0 is what makes both versions stop: "
                + (gcdRecursive(100, 0) == 100));
    }
}
```

```text
gcd(48, 18) = 6  (loop agrees: true)
gcd(17, 5) = 1  (loop agrees: true)
gcd(100, 0) = 100  (loop agrees: true)
gcd(0, 7) = 7  (loop agrees: true)
gcd(270, 192) = 6  (loop agrees: true)
a base case of b == 0 is what makes both versions stop: true
```

`gcd(100, 0)` returning `100` and `gcd(0, 7)` returning `7` are the two cases that a base case of
`a == b` would get wrong, and they are worth having in the test list for that reason. The recursive
form terminates because the remainder is strictly smaller than the divisor, so the arguments shrink
on every call — which is the property every recursion needs and the property `descend` in the
`StackOverflow` example does not have.
:::
