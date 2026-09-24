---
chapter: 7
part: 1
title: Arrays and the Enhanced for
summary: Build and fill arrays, visit them with the enhanced for, avoid the bounds and identity traps, and use Arrays.sort and Arrays.binarySearch correctly.
minutes: 55
tags: [arrays, enhanced for, bounds, Arrays, sorting, binary search, multidimensional]
---

An array is the only collection built into the language rather than the library, and it is the one
place Java exposes a raw block of memory with a length and a bounds check. Everything in
`java.util` — `ArrayList`, `HashMap`, `StringBuilder` — is ultimately built on one, so the rules in
this chapter are the rules the collections inherit.

Three of those rules cause almost every array bug: the length is **fixed** when the array is created,
the contents are **defaults** until you write to them, and an array variable holds a **reference**, so
`==` asks whether two names point at the same block rather than whether two blocks hold the same
values.

## Creating an array, and what is in it before you fill it

```java run
import java.util.Arrays;

public class Basics {
    public static void main(String[] args) {
        int[] zeros = new int[5];
        System.out.println("new int[5]     = " + Arrays.toString(zeros));

        String[] names = new String[3];
        System.out.println("new String[3]  = " + Arrays.toString(names));

        boolean[] flags = new boolean[2];
        System.out.println("new boolean[2] = " + Arrays.toString(flags));

        int[] literals = {10, 20, 30};
        System.out.println("literal        = " + Arrays.toString(literals));
        System.out.println("length         = " + literals.length);
        System.out.println("the last index is length - 1 = " + (literals.length - 1));

        System.out.println("without Arrays.toString it prints an identity, not the contents: "
                + literals.toString().startsWith("[I@"));
    }
}
```

```text
new int[5]     = [0, 0, 0, 0, 0]
new String[3]  = [null, null, null]
new boolean[2] = [false, false]
literal        = [10, 20, 30]
length         = 3
the last index is length - 1 = 2
without Arrays.toString it prints an identity, not the contents: true
```

`new int[5]` creates five slots and fills them with the type's default — `0` for numbers, `false` for
`boolean`, and `null` for anything that is a reference. There is no "uninitialised" state to detect:
an array of `String` is full of `null` references from the moment it exists, and using one before
assigning it throws `NullPointerException` at the point of use, far from the line that created the
array. The habit that prevents this is to create an array and fill it in the same method, or to
prefer a `List` (Chapter 12) when the contents arrive over time.

`length` is a **field**, not a method — `values.length`, with no parentheses. It cannot change after
creation, which is the definition of an array and the reason `ArrayList` exists. The last valid index
is `length - 1`, and the off-by-one that uses `length` is the single most common array bug there is.

The last line is worth a moment. Printing an array without a helper prints something like `[I@1b6d3586`,
which is the type descriptor, an `@`, and an identity hash — a number that differs between runs. It
is not the contents, and it is not even stable, so a program that prints an array by concatenation is
printing something you cannot compare or test. `Arrays.toString` is the fix, and the `startsWith("[I@")`
test above is how you check for the mistake without printing the unstable part.

## Bounds are checked, and the message is exact

Reading past the end of an array is not undefined behaviour, as it is in C. Java checks every access
and throws, which turns a memory-corruption bug into an exception with a line number:

```java throw
public class Bounds {
    public static void main(String[] args) {
        int[] values = {10, 20, 30};
        System.out.println("length           = " + values.length);
        System.out.println("last valid index = " + (values.length - 1));
        System.out.println("reading index 3:");
        System.out.println(values[3]);
    }
}
```

```text
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 3 out of bounds for length 3
```

The message is worth reading closely, because it is more informative than it looks: *Index 3 out of
bounds for length 3* names the index you asked for and the length that made it invalid. A loop
written as `i <= values.length` fails on the very first pass through the end, and the message tells
you immediately which of the two numbers is wrong.

The cost of that check is a comparison per access, which is one of the reasons a tight loop over a
`List<Integer>` is slower than the same loop over an `int[]` — an array access is a bounds check and
an add, while a list access is a method call, a bounds check, and a boxing conversion. Chapter 11
returns to what the compiler does with both.

## The enhanced for, and the two things it cannot do

The enhanced `for` visits every element once, in order, without an index:

```java run
import java.util.Arrays;

public class EnhancedFor {
    public static void main(String[] args) {
        int[] values = {4, 8, 15, 16, 23, 42};

        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        System.out.println("sum            = " + sum);

        System.out.print("values over 10 :");
        for (int value : values) {
            if (value > 10) {
                System.out.print(" " + value);
            }
        }
        System.out.println();

        for (int value : values) {
            value = value * 2;
        }
        System.out.println("after doubling the loop variable: " + Arrays.toString(values));

        for (int i = 0; i < values.length; i++) {
            values[i] = values[i] * 2;
        }
        System.out.println("after doubling by index         : " + Arrays.toString(values));

        for (int value : values) {
            if (value == 30) {
                System.out.println("found 30, but an enhanced for cannot say where");
            }
        }
    }
}
```

```text
sum            = 108
values over 10 : 15 16 23 42
after doubling the loop variable: [4, 8, 15, 16, 23, 42]
after doubling by index         : [8, 16, 30, 32, 46, 84]
found 30, but an enhanced for cannot say where
```

It is the right default and it should be your first choice whenever you are reading every element.
Two limitations are worth knowing before you reach for it and find out.

**The loop variable is a copy.** `value = value * 2` assigns to a local that is overwritten on the
next iteration, so the array is unchanged — which is what the two `after doubling` lines show side by
side. To modify the elements you need the index, and an ordinary `for` with `values[i] = ...`. This
is Chapter 6's pass-by-value rule arriving again: the loop hands you a copy of each element.

**It does not know the index.** If the position matters — to report where something was found, to
compare neighbours, or to skip elements — you need the indexed loop. Note that this is a real
limitation and not a style preference: there is no `for (int i : ...)` syntax, and the workarounds
that count a separate variable are worse than just writing the indexed loop.

There is a third limitation that does not apply to arrays but will apply to every `Collection` you
meet from Chapter 12 on: modifying the collection *inside* an enhanced `for` throws
`ConcurrentModificationException`. It is safe on an array, because an array has no iterator to
invalidate.

## Arrays are objects: identity, contents and copies

An array variable is a reference, exactly like the ones in Chapter 2, and the consequences are worth
seeing once:

```java run
import java.util.Arrays;

public class Aliasing {
    public static void main(String[] args) {
        int[] original = {1, 2, 3};
        int[] alias = original;
        int[] copy = Arrays.copyOf(original, original.length);
        int[] longer = Arrays.copyOf(original, 5);

        alias[0] = 99;

        System.out.println("original = " + Arrays.toString(original));
        System.out.println("alias    = " + Arrays.toString(alias));
        System.out.println("copy     = " + Arrays.toString(copy));
        System.out.println("longer   = " + Arrays.toString(longer));

        System.out.println("original == alias : " + (original == alias));
        System.out.println("original == copy  : " + (original == copy));

        int[] sameContents = {99, 2, 3};
        System.out.println("a different array holding the same numbers:");
        System.out.println("  ==            : " + (original == sameContents));
        System.out.println("  Arrays.equals : " + Arrays.equals(original, sameContents));
        System.out.println("  == is identity; Arrays.equals is contents");
    }
}
```

```text
original = [99, 2, 3]
alias    = [99, 2, 3]
copy     = [1, 2, 3]
longer   = [1, 2, 3, 0, 0]
original == alias : true
original == copy  : false
a different array holding the same numbers:
  ==            : false
  Arrays.equals : true
  == is identity; Arrays.equals is contents
```

`int[] alias = original;` copies the reference, not the array, so writing through either name is
visible through both — the first two lines are identical for that reason. `Arrays.copyOf` produces a
genuinely separate array, and it is the one to reach for whenever you intend to modify one without
the other. Note that `copyOf` also takes a length, so it doubles as the way to grow or shrink an
array: `Arrays.copyOf(original, 5)` returned the three values and then padded with two `0`s.

The bottom four lines are the rule stated as a measurement. `original == alias` is `true` because
they are the same object; `original == copy` is `false` because they are not. And `==` against a
*different* array holding the same three numbers is also `false`, while `Arrays.equals` on the same
pair is `true`. **`==` asks about identity and `Arrays.equals` asks about contents**, and a program
that tests arrays with `==` is testing whether two variables were assigned from each other.

For nested arrays there is a second level to this. `Arrays.equals` on an `int[][]` compares the *row
references*, so it is `false` for two separately-built matrices with equal numbers;
`Arrays.deepEquals` recurses and compares the contents. The same split exists for `hashCode` and
`toString`, and Chapter 10 is about why.

## Arrays of arrays

An `int[][]` is not a rectangular block of memory — it is an array whose elements are themselves
arrays. That is why the second dimension can be a different length on every row:

```java run
import java.util.Arrays;

public class Grid {
    public static void main(String[] args) {
        int[][] grid = new int[3][4];
        System.out.println("rows          = " + grid.length);
        System.out.println("columns       = " + grid[0].length);
        System.out.println("grid[0] is an int[] : " + (grid[0] instanceof int[]));

        for (int row = 0; row < grid.length; row++) {
            for (int col = 0; col < grid[row].length; col++) {
                grid[row][col] = (row + 1) * (col + 1);
            }
        }
        for (int[] row : grid) {
            System.out.println("  " + Arrays.toString(row));
        }

        int[][] jagged = {{1}, {2, 3}, {4, 5, 6}};
        System.out.println("a jagged array has rows of different lengths:");
        for (int[] row : jagged) {
            System.out.println("  length " + row.length + " -> " + Arrays.toString(row));
        }
        System.out.println("int[][] is an array of int[], which is why it need not be a rectangle");
    }
}
```

```text
rows          = 3
columns       = 4
grid[0] is an int[] : true
  [1, 2, 3, 4]
  [2, 4, 6, 8]
  [3, 6, 9, 12]
a jagged array has rows of different lengths:
  length 1 -> [1]
  length 2 -> [2, 3]
  length 3 -> [4, 5, 6]
int[][] is an array of int[], which is why it need not be a rectangle
```

`grid[0].length` works because `grid[0]` is an `int[]`. The jagged example is not a curiosity: an
array of arrays with different row lengths is the natural representation of a table whose rows have
different arities, and it is how a great deal of parsed data arrives. It also means the *inner* arrays
are independently replaceable — `grid[1] = new int[]{1, 2}` is legal and changes only that row.

The practical consequence for loops is that the inner bound must be read from the row, not from the
first row: `for (int col = 0; col < grid[row].length; col++)`. Using `grid[0].length` for every row is
correct for a rectangular array and throws for a jagged one.

## Sorting and searching

`java.util.Arrays` is the static toolbox for arrays, and two of its methods are used far more than the
rest:

```java run
import java.util.Arrays;

public class Sorting {
    public static void main(String[] args) {
        int[] values = {42, 8, 15, 4, 23, 16};
        System.out.println("unsorted         = " + Arrays.toString(values));
        Arrays.sort(values);
        System.out.println("sorted           = " + Arrays.toString(values));

        System.out.println("binarySearch(23) = " + Arrays.binarySearch(values, 23));
        System.out.println("binarySearch(7)  = " + Arrays.binarySearch(values, 7));

        int[] filled = new int[5];
        Arrays.fill(filled, 7);
        System.out.println("filled           = " + Arrays.toString(filled));
        Arrays.fill(filled, 1, 3, 0);
        System.out.println("filled 1 to 2    = " + Arrays.toString(filled));

        String[] words = {"pear", "apple", "fig"};
        Arrays.sort(words);
        System.out.println("strings sort     = " + Arrays.toString(words));

        int[] unsorted = {3, 1, 2};
        System.out.println("searching an unsorted array: " + Arrays.binarySearch(unsorted, 3));
        System.out.println("3 is at index 0, and binary search reported " + Arrays.binarySearch(unsorted, 3));
    }
}
```

```text
unsorted         = [42, 8, 15, 4, 23, 16]
sorted           = [4, 8, 15, 16, 23, 42]
binarySearch(23) = 4
binarySearch(7)  = -2
filled           = [7, 7, 7, 7, 7]
filled 1 to 2    = [7, 0, 0, 7, 7]
strings sort     = [apple, fig, pear]
searching an unsorted array: -4
3 is at index 0, and binary search reported -4
```

`Arrays.sort` sorts in place — it returns `void`, and the array you passed is the sorted one. That
surprises people who expect a returned array and then wonder why their "unsorted" copy is sorted too;
the answer is that there is no copy, and `Arrays.copyOf` before the sort is how you keep the original.

`Arrays.binarySearch` is the method that has a precondition and does not enforce it. It requires a
**sorted** array, and given an unsorted one it returns a plausible-looking number rather than an
error. The last two lines are that failure measured: `3` is at index `0` of `{3, 1, 2}`, and binary
search reported `-4`. There is no exception and no warning, and the value it returns is a perfectly
well-formed "not found" result.

Two more details from the block. A **negative** result means not found, and it encodes where the value
*would* go: `-(insertion point) - 1`. So `binarySearch(values, 7)` on `{4, 8, 15, 16, 23, 42}` returned
`-2`, which decodes to "insert at index 1". And `Arrays.fill(filled, 1, 3, 0)` fills a **half-open
range** — indices 1 and 2, not 1, 2 and 3 — which is the same `fromIndex, toIndex` convention as
`String.substring` and every other range in the library.

:::pitfall Comparing arrays with `==`

```java
if (actual == expected) { ... }        // true only if they are the same object
if (Arrays.equals(actual, expected)) { ... }   // compares the contents
```

`==` on two arrays compares references, so it is `false` for two arrays built separately and `true`
for one array compared with itself. That second case is the dangerous one: a test that asserts
`assertEquals(actual, actual)` — which is what happens when a helper returns the input unchanged —
passes for every possible input, including the ones the code gets wrong. Use `Arrays.equals` for
one-dimensional arrays, `Arrays.deepEquals` for nested ones, and check that the two sides of a test
are genuinely different objects before trusting the result.
:::

:::scenario The test that passes on every input

A validation method returns a copy of the expected array, and the test asserts that the returned
array equals the expected one. It has never failed, in two years.

:::solution
The assertion is comparing the array with itself. The method under test returns the array it was
given — not a copy — so `actual == expected` is true by construction, and the test can only fail if
the method starts returning a *different* array. It is testing identity while claiming to test
contents.

```java run
import java.util.Arrays;

public class Scenario {
    static boolean sameItems(int[] a, int[] b) {
        return a == b;
    }

    static boolean sameItemsCorrect(int[] a, int[] b) {
        return Arrays.equals(a, b);
    }

    public static void main(String[] args) {
        int[] expected = {1, 2, 3};
        int[] actual = {1, 2, 3};

        System.out.println("both arrays print as " + Arrays.toString(expected)
                + " and " + Arrays.toString(actual));
        System.out.println("sameItems (==)           : " + sameItems(expected, actual));
        System.out.println("sameItemsCorrect (equals): " + sameItemsCorrect(expected, actual));

        int[] sameObject = expected;
        System.out.println("== is true only when both names hold one array: "
                + sameItems(expected, sameObject));
        System.out.println("so a test that compares a value with itself always passes: "
                + sameItems(expected, expected));
    }
}
```

```text
both arrays print as [1, 2, 3] and [1, 2, 3]
sameItems (==)           : false
sameItemsCorrect (equals): true
== is true only when both names hold one array: true
so a test that compares a value with itself always passes: true
```

The three `sameItems` lines are the whole story. Two arrays holding `1, 2, 3` are **not** equal by
`==` and are equal by `Arrays.equals`. The same array under two names **is** equal by `==`, which is
why the test passed. And comparing a value with itself is `true` for every input, so the assertion
carried no information at all.

The fix is one method call — `Arrays.equals` — but the habit that prevents the whole class of bug is
to ask, of any assertion: *could this fail?* An assertion that compares two things that are the same
object, or that asserts a value is equal to itself, is not a test. The same trap appears with
`List.equals` versus `==` in Chapter 12, and with `equals` versus `==` on any object in Chapter 10.
:::

## Key takeaways

- `new int[5]` fills the array with the type's defaults: `0`, `false`, or `null`. There is no
  uninitialised state, and a `null` element throws at the point of use rather than at creation.
- `length` is a field, not a method, and it cannot change. The last valid index is `length - 1`.
- Printing an array without `Arrays.toString` prints a type descriptor and an unstable identity hash,
  not the contents.
- Every array access is bounds-checked and throws `ArrayIndexOutOfBoundsException` naming both the
  index and the length.
- The enhanced `for` gives you a **copy** of each element, so assigning to the loop variable does not
  change the array, and it cannot tell you the index.
- An array variable is a reference. `int[] b = a;` is a second name for one array; `Arrays.copyOf`
  makes a second array. `==` compares identity, `Arrays.equals` compares contents, and
  `Arrays.deepEquals` compares nested contents.
- An `int[][]` is an array of `int[]`, so rows may have different lengths; read each row's bound from
  that row.
- `Arrays.sort` sorts **in place** and returns `void`. `Arrays.binarySearch` requires a sorted array
  and silently returns a wrong answer on an unsorted one; a negative result encodes the insertion
  point as `-(index) - 1`.
- Range parameters in `java.util.Arrays` and `String` are half-open: `fill(a, 1, 3, 0)` writes
  indices 1 and 2.

## Practice

- [ ] Reverse an array in place using two indices that move toward each other, and check it on
      lengths 1 through 5 including an odd one.
- [ ] Count how many times each value in `{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 0}` appears, using an
      `int[]` of counters, and check that the counts add up to the number of values.
- [ ] Transpose a 2-by-3 matrix into a 3-by-2 one and verify that transposing twice returns the
      original.
- [ ] Find the second largest **distinct** value in an array, and decide what to return when there is
      no such value.

## Solutions

:::solution Exercise 1
Two indices moving toward each other, swapping as they go. The loop stops when they meet or cross,
which is what makes both the even and the odd length work without a special case:

```java run
import java.util.Arrays;

public class Sol1 {
    static void reverse(int[] values) {
        int left = 0;
        int right = values.length - 1;
        while (left < right) {
            int temp = values[left];
            values[left] = values[right];
            values[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        int[][] cases = {{1}, {1, 2}, {1, 2, 3}, {1, 2, 3, 4}, {1, 2, 3, 4, 5}};
        for (int[] values : cases) {
            int[] before = Arrays.copyOf(values, values.length);
            reverse(values);
            System.out.println(Arrays.toString(before) + " -> " + Arrays.toString(values));
        }

        int[] odd = {1, 2, 3, 4, 5};
        reverse(odd);
        System.out.println("for an odd length the middle element never moves: " + odd[2]);
        System.out.println("the swap uses the array, so it works where a swap method could not");
    }
}
```

```text
[1] -> [1]
[1, 2] -> [2, 1]
[1, 2, 3] -> [3, 2, 1]
[1, 2, 3, 4] -> [4, 3, 2, 1]
[1, 2, 3, 4, 5] -> [5, 4, 3, 2, 1]
for an odd length the middle element never moves: 3
the swap uses the array, so it works where a swap method could not
```

For `{1, 2, 3, 4, 5}` the middle element is never touched, because `left` and `right` both reach `2`
and the condition `left < right` is false — the same reason an odd-length string reverses correctly.
The swap here works where Chapter 6's `swap(int, int)` could not: the values live in an array, and the
method holds a reference to it, so writing through the reference is visible to the caller.
:::

:::solution Exercise 2
One counter per value, indexed by the value itself. This is the pattern that makes an array worth
having — the index *is* the key, so no searching is needed:

```java run
import java.util.Arrays;

public class Sol2 {
    static int[] histogram(int[] values, int buckets) {
        int[] counts = new int[buckets];
        for (int value : values) {
            if (value >= 0 && value < buckets) {
                counts[value]++;
            }
        }
        return counts;
    }

    public static void main(String[] args) {
        int[] values = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 0};
        int[] counts = histogram(values, 10);

        System.out.println("values = " + Arrays.toString(values));
        for (int value = 0; value < counts.length; value++) {
            if (counts[value] > 0) {
                System.out.println("  " + value + " appears " + counts[value] + " time(s)");
            }
        }

        int total = 0;
        for (int count : counts) {
            total += count;
        }
        System.out.println("the counts add up to " + total + " of " + values.length + " values");
    }
}
```

```text
values = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 0]
  0 appears 1 time(s)
  1 appears 2 time(s)
  2 appears 1 time(s)
  3 appears 2 time(s)
  4 appears 1 time(s)
  5 appears 3 time(s)
  6 appears 1 time(s)
  9 appears 1 time(s)
the counts add up to 12 of 12 values
```

`5` appears three times and `1` and `3` twice, and the counts add to `12`, which is the assertion that
nothing was dropped. The bounds test in the loop is not decoration: without it a value of `10` or a
negative would throw, and a histogram that throws on unexpected input is a histogram that fails in
production. Printing only the non-zero buckets is a small choice with a visible effect — the output is
eight lines instead of ten, and the two absent values are still accounted for by the total.
:::

:::solution Exercise 3
The result is allocated with the dimensions swapped, and the loop copies each element to its mirrored
position:

```java run
import java.util.Arrays;

public class Sol3 {
    static int[][] transpose(int[][] matrix) {
        int[][] result = new int[matrix[0].length][matrix.length];
        for (int row = 0; row < matrix.length; row++) {
            for (int col = 0; col < matrix[row].length; col++) {
                result[col][row] = matrix[row][col];
            }
        }
        return result;
    }

    static void print(int[][] matrix) {
        for (int[] row : matrix) {
            System.out.println("  " + Arrays.toString(row));
        }
    }

    public static void main(String[] args) {
        int[][] matrix = {{1, 2, 3}, {4, 5, 6}};
        System.out.println("the original has " + matrix.length + " rows:");
        print(matrix);

        int[][] flipped = transpose(matrix);
        System.out.println("the transpose has " + flipped.length + " rows:");
        print(flipped);

        System.out.println("transposing twice returns the original: "
                + Arrays.deepEquals(matrix, transpose(flipped)));
        System.out.println("note deepEquals for nested arrays; equals would compare the row references");
    }
}
```

```text
the original has 2 rows:
  [1, 2, 3]
  [4, 5, 6]
the transpose has 3 rows:
  [1, 4]
  [2, 5]
  [3, 6]
transposing twice returns the original: true
note deepEquals for nested arrays; equals would compare the row references
```

`transpose(transpose(m))` returning the original is the property that makes this correct rather than
merely plausible, and `Arrays.deepEquals` is what checks it — `equals` would compare the row
references and report `false` for two separately built matrices. Note that the method *returns* a new
matrix rather than mutating the input, because a 2-by-3 and a 3-by-2 cannot share storage.
:::

:::solution Exercise 4
One pass, two variables, and the `else if` that rejects duplicates of the largest. Returning
`Integer.MIN_VALUE` for "no second value" is a choice with a cost, stated on the last line:

```java run
import java.util.Arrays;

public class Sol4 {
    static int secondLargest(int[] values) {
        int largest = Integer.MIN_VALUE;
        int second = Integer.MIN_VALUE;
        for (int value : values) {
            if (value > largest) {
                second = largest;
                largest = value;
            } else if (value < largest && value > second) {
                second = value;
            }
        }
        return second;
    }

    public static void main(String[] args) {
        int[][] cases = {{3, 7, 7, 2, 9, 9, 5}, {1, 2}, {5, 5, 5}, {-3, -7, -1}};
        for (int[] values : cases) {
            System.out.println(Arrays.toString(values) + " -> " + secondLargest(values));
        }

        System.out.println("a duplicate of the largest is not a second value: "
                + secondLargest(new int[]{4, 4, 1}));
        System.out.println("no second value at all reports Integer.MIN_VALUE: "
                + (secondLargest(new int[]{5, 5, 5}) == Integer.MIN_VALUE));
    }
}
```

```text
[3, 7, 7, 2, 9, 9, 5] -> 7
[1, 2] -> 1
[5, 5, 5] -> -2147483648
[-3, -7, -1] -> -3
a duplicate of the largest is not a second value: 1
no second value at all reports Integer.MIN_VALUE: true
```

`{5, 5, 5}` has no second distinct value and reports `-2147483648`, which is indistinguishable from a
genuine second value of `Integer.MIN_VALUE`. That is the standard weakness of using a sentinel, and
the honest alternatives are to return an `OptionalInt` (Chapter 15) or to throw. What the exercise is
really about is the `value < largest` guard: without it, `{4, 4, 1}` reports `4`, which is not the
second largest value by any reading.
:::
