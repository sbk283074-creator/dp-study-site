---
chapter: 5
part: 1
title: Control Flow
summary: Make a program decide and repeat — branches, the three loops, break and continue, switch dispatch and its fall-through trap, and the one place goto is the right answer.
minutes: 50
tags: [if, loops, switch, break, continue, goto, control flow]
---

A program with no branches runs once and stops. Every interesting thing a program does involves
choosing between alternatives and repeating work until a condition changes, and C gives you a small,
sharp set of tools for both: `if`, three kinds of loop, and `switch`. The tools are easy to learn and
easy to misuse, because most of the misuse still compiles. A `switch` that falls through the wrong
case, a loop whose condition can never become false, a `break` that escapes the wrong level — none of
these are syntax errors. This chapter is about the shapes that are hard to get wrong.

## Branching with if

`if` takes a value and treats zero as false and everything else as true. There is no boolean type
required — `if (count)` means "if count is not zero", and that idiom is everywhere in C.

```c run
#include <stdio.h>

int main(void) {
    int temperature = 120;

    if (temperature > 100) {
        printf("boiling\n");
    } else if (temperature > 0) {
        printf("liquid\n");
    } else {
        printf("frozen\n");
    }
    return 0;
}
```

```text
boiling
```

Only one branch runs, and the conditions are tested in order — so the `else if` is only reached when
the first test failed. That ordering is a contract: `temperature > 0` would be true for 120 as well,
and it is never asked.

The braces are not optional in the sense that they are always required — a single statement is legal
without them. They are optional in the sense that *omitting them is how the dangling-else bug
happens*:

```c warn
#include <stdio.h>

int main(void) {
    int outer = 1;
    int inner = 0;

    if (outer)
        if (inner)
            printf("both\n");
    else
        printf("outer is false\n");

    printf("done\n");
    return 0;
}
```

```text
add explicit braces to avoid dangling else [-Wdangling-else]
```

Read the indentation and you would say the `else` belongs to `if (outer)`. The compiler disagrees:
an `else` always binds to the nearest unmatched `if`, which is `if (inner)`. So the program prints
`outer is false` — even though `outer` is `1`, which is true. The indentation is a lie the compiler
is not reading. Braces make the structure explicit and the ambiguity impossible:

```c run
#include <stdio.h>

int main(void) {
    int outer = 1;
    int inner = 0;

    if (outer) {
        if (inner) {
            printf("both\n");
        }
    } else {
        printf("outer is false\n");
    }

    printf("done\n");
    return 0;
}
```

```text
done
```

Same values, same tests, and now the `else` belongs to the outer `if` because the braces say so.
`outer` is true, the inner test fails quietly, and the `else` branch is never reached — which is what
the original indentation claimed was happening and was not.

That is why this book puts braces on every branch, including one-liners. It costs a line and removes
a class of bug permanently. The warning above only fires because the indentation is misleading;
braces always work.

## while and do-while

`while` tests before each iteration, so it can run zero times. `do-while` tests after, so it always
runs at least once — which is exactly what you want when the body has to execute before there is
anything to test.

```c run
#include <stdio.h>

int main(void) {
    int n = 0;

    do {
        printf("ran once with n=%d\n", n);
        n++;
    } while (n < 0);

    return 0;
}
```

```text
ran once with n=0
```

`n < 0` is false before the loop even starts, and the body ran anyway. That is not a bug — it is the
definition. The pattern is right for "prompt, then validate": you cannot test the user's answer before
you have asked for it. The trailing semicolon after `while (...)` is required and easy to forget.

The most common `while` shape combines a bound with a sentinel, so the loop stops at whichever comes
first. Short-circuit `&&` from Chapter 4 is what makes it safe:

```c run
#include <stdio.h>

int main(void) {
    int readings[5] = {12, -3, 7, 0, 99};
    int total = 0;
    int i = 0;

    while (i < 5 && readings[i] != 0) {
        total += readings[i];
        i++;
    }

    printf("summed %d reading(s), total %d\n", i, total);
    return 0;
}
```

```text
summed 3 reading(s), total 16
```

Two facts are doing work. `i < 5` is checked first, so `readings[i]` is never evaluated at `i == 5` —
that is the array bound, and without it the program would read past the end. And the sentinel `0`
stops the loop early, at index 3, leaving `99` unread. The order of the two conditions is not a
style choice; reversing them makes the program read out of bounds on a full array.

## for, and when to use it

`for (init; condition; step)` groups the three facts about a counted loop in one place, which is why
it is the right tool whenever the loop's length is known up front. Any of the three clauses may be
empty — `for (;;)` is an infinite loop — and the init clause may declare the variable, scoped to the
loop.

```c
for (int i = 0; i < count; i++) { ... }
```

Prefer that to declaring `i` outside. A loop variable that cannot be seen after the loop cannot be
reused by accident, and the compiler can tell you when a loop never runs because the bound is
impossible.

Which loop to reach for:

| Shape | Use when |
|---|---|
| `for` | the number of iterations is known or computable up front |
| `while` | the loop runs while a condition holds, possibly zero times |
| `do-while` | the body must run at least once before anything can be tested |

## break and continue

`break` leaves the innermost loop or `switch` immediately. `continue` skips the rest of the current
iteration and goes back to the test. Both are jumps, and `continue` jumps *past* everything below it,
which is the part that surprises people:

```c run
#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 10; i++) {
        if (i % 2 == 0) {
            continue;
        }
        if (i > 7) {
            break;
        }
        printf("%d ", i);
    }
    printf("\n");
    return 0;
}
```

```text
1 3 5 7
```

The odd numbers up to 7, then nothing. `i` reaches 8, `8 % 2 == 0` sends it back to the top with
`continue`, and the `i > 7` check below is never reached for that iteration. The loop only stops when
`i` reaches 9 — an odd number — and the break finally runs. Had the two `if`s been in the other order,
the loop would have stopped at 8 instead. **The order of a `break` relative to a `continue` in the
same body changes which iterations the break can see.**

`break` also breaks out of a `switch`, which is where it does the most damage when omitted, and it
only ever escapes one level. To leave two nested loops you need a flag, a `return`, or the `goto`
discussed below.

## switch: dispatch on a value

`switch` compares one integer value against a list of constant labels. It is not a chain of `if`s —
the compiler may build a jump table, and it is the natural way to dispatch on an `enum`.

```c run
#include <stdio.h>

enum Outcome { OUTCOME_OK, OUTCOME_RETRY, OUTCOME_FATAL };

static const char *describe(enum Outcome outcome) {
    switch (outcome) {
    case OUTCOME_OK:
        return "success";
    case OUTCOME_RETRY:
        return "retry";
    case OUTCOME_FATAL:
        return "give up";
    }
    return "unknown";
}

int main(void) {
    for (int i = 0; i < 3; i++) {
        printf("%d: %s\n", i, describe((enum Outcome)i));
    }
    return 0;
}
```

```text
0: success
1: retry
2: give up
```

Every case ends in `return`, so falling through is impossible by construction — which is a better
guarantee than remembering to write `break`. The `return "unknown";` after the switch is there
because the compiler cannot prove the value is one of the three; without it, `-Wreturn-type` would
complain that control may reach the end of a non-void function.

Two rules about case labels are worth knowing before they bite you. A label must be an integer
constant expression — a `double` will not do:

```c bad
#include <stdio.h>

int main(void) {
    double value = 1.0;

    switch (value) {
    case 1:
        printf("one\n");
        break;
    default:
        break;
    }
    return 0;
}
```

```text
error: statement requires expression of integer type ('double' invalid)
```

And two labels may not share a value, because there would be no way to choose:

```c bad
#include <stdio.h>

int main(void) {
    int x = 1;

    switch (x) {
    case 1:
        printf("one\n");
        break;
    case 1:
        printf("uno\n");
        break;
    default:
        break;
    }
    return 0;
}
```

```text
error: duplicate case value '1'
```

A case body is a sequence of statements, not a block, so a declaration directly after a label is
allowed only as a C23 extension. Wrap the body in braces when it needs a local variable:

```c warn
#include <stdio.h>

int main(void) {
    int x = 1;

    switch (x) {
    case 1:
        int y = 5;
        printf("y=%d\n", y);
        break;
    default:
        break;
    }
    return 0;
}
```

```text
label followed by a declaration is a C23 extension [-Wc23-extensions]
```

This builds and runs under clang, and it will not build under a strict C17 compiler. Write
`case 1: {` … `}` and the question disappears:

```c run
#include <stdio.h>

int main(void) {
    int x = 2;

    switch (x) {
    case 1: {
        int y = 5;
        printf("y=%d\n", y);
        break;
    }
    default:
        printf("other\n");
        break;
    }
    return 0;
}
```

```text
other
```

:::pitfall Forgetting break, and getting two cases for the price of one
`switch` does not stop at the next label. After a case's statements run, control continues into the
following case unless something stops it.

```c run
#include <stdio.h>

int main(void) {
    int x = 1;

    switch (x) {
    case 1:
        printf("one\n");
    case 2:
        printf("two\n");
        break;
    default:
        break;
    }
    return 0;
}
```

```text
one
two
```

`x` is `1`, so `case 1` runs and prints `one`. There is no `break`, so execution falls into
`case 2` and prints `two` as well — even though `x` was never `2`. The bug is invisible in the
output when both messages happen to be plausible.

This is not always a mistake. Stacking labels with no statements between them is the idiomatic way to
say "these cases share a body", and it is what the grade example in this chapter's solutions does.
The rule is that a fall-through should be either impossible (every case ends in `break` or `return`)
or deliberate and commented. Clang can warn about the accidental kind with
`-Wimplicit-fallthrough`, but note that `-Wall -Wextra` does **not** enable it — you have to ask for
that flag explicitly, which is why it is not the safety net people assume it is.
:::

## goto, and the one place it earns its place

`goto` jumps to a label anywhere in the same function. It cannot jump into a different function, and
jumping backwards is how you write a loop by hand. Teaching languages tell you never to use it. In C
there is exactly one pattern where it is not just acceptable but the clearest thing you can write:
unwinding a function that has acquired several resources, when any acquisition can fail.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int status = 0;
    int *first = NULL;
    int *second = NULL;

    first = malloc(sizeof(int) * 4);
    if (first == NULL) {
        status = 1;
        goto cleanup;
    }

    second = malloc(sizeof(int) * 4);
    if (second == NULL) {
        status = 1;
        goto cleanup;
    }

    first[0] = 20;
    second[0] = 22;
    printf("total %d\n", first[0] + second[0]);

cleanup:
    free(second);
    free(first);
    return status;
}
```

```text
total 42
```

The alternative without `goto` is a chain of nested `if`s or a repeated block of cleanup code, and
both get worse with every resource you add. With `goto`, there is exactly one cleanup path, it is
reached from every failure point, and `free(NULL)` is defined to do nothing — so the labels are safe
even when nothing was allocated. Chapter 7 will make this pattern much less necessary, and Chapter 28
removes it entirely with `std::unique_ptr`. Until then it is the honest answer.

Two rules keep it safe: jump **forwards** to a label at the end of the function, and never jump over a
declaration that initialises a variable you later use.

:::scenario The retry that never retried
A network client wraps a request in a state machine. Here is the shape of the original code, made
runnable so you can see it fail:

```c run
#include <stdio.h>

enum Result { RESULT_OK, RESULT_RETRY, RESULT_FATAL };

static const char *handle(enum Result result, int *attempts) {
    switch (result) {
    case RESULT_OK:
        return "payload";
    case RESULT_RETRY:
        (*attempts)++;
        /* intended: try again, but there is no break */
    case RESULT_FATAL:
        return NULL;
    }
    return NULL;
}

int main(void) {
    int attempts = 0;
    const char *outcome = handle(RESULT_RETRY, &attempts);

    printf("attempts=%d, outcome=%s\n", attempts, outcome ? outcome : "(null)");
    return 0;
}
```

```text
attempts=1, outcome=(null)
```

The `case RESULT_RETRY` branch has no `break`, so after incrementing `attempts` it falls into the
fatal case and returns `NULL`. The retry counter is incremented and then thrown away; the client
gives up on the first failure. Nothing crashes, and the counter in the logs looks busy, so the bug
survives review.

:::solution Make each case self-contained, and let the enum do the checking
The fix is structural rather than a missing `break`:

```c run
#include <stdio.h>

enum Outcome { OUTCOME_OK, OUTCOME_RETRY, OUTCOME_FATAL };

static const char *describe(enum Outcome outcome) {
    switch (outcome) {
    case OUTCOME_OK:
        return "success";
    case OUTCOME_RETRY:
        return "retry";
    case OUTCOME_FATAL:
        return "give up";
    }
    return "unknown";
}

int main(void) {
    for (int i = 0; i < 3; i++) {
        printf("%d: %s\n", i, describe((enum Outcome)i));
    }
    return 0;
}
```

```text
0: success
1: retry
2: give up
```

Three things changed and all three matter. Every case ends in a `return`, so there is no way to fall
through — the structure makes the bug unrepresentable rather than merely absent. The `switch` is over
an `enum`, so `-Wswitch` will tell you the day somebody adds a fourth outcome and forgets a case;
a `switch` over a plain `int` gets no such protection. And the dispatch is isolated in a small
function that returns a value instead of performing the action inline, so the state machine can be
tested by calling it, without a network.

The flag that would have caught the original is `-Wimplicit-fallthrough`, and the lesson there is
that it is *not* part of `-Wall -Wextra` on this compiler. If a project cares about accidental
fall-through, it has to say so explicitly — assuming a warning is on because it sounds like it should
be is how a bug survives a "we compile with warnings enabled" policy.
:::

## Key takeaways

- `if` treats zero as false and everything else as true; there is no boolean type required.
- An `else` binds to the nearest unmatched `if`, not to the one the indentation suggests. Braces on
  every branch remove the ambiguity permanently.
- `while` tests first and may run zero times; `do-while` tests last and always runs at least once.
- A bound-and-sentinel `while` depends on the order of its `&&` operands: the bounds check must come
  first so the array access is never evaluated out of range.
- `for` is for counted loops, and declaring the variable in the init clause keeps it out of scope
  afterwards.
- `break` exits the innermost loop or `switch`; `continue` skips to the next iteration, past
  everything below it — including a `break` that comes later in the body.
- `switch` dispatches on an integer constant expression. Case labels must be integer constants and
  must be unique, and a declaration directly after a label needs braces.
- Without a `break` or `return`, execution falls into the next case. Stacked labels are the
  deliberate form; everything else is a bug.
- `-Wimplicit-fallthrough` is not enabled by `-Wall -Wextra` on Apple clang. Ask for it explicitly.
- `goto` forward to a single cleanup label is the standard C idiom for unwinding multiple resources,
  and `free(NULL)` makes the cleanup path safe when nothing was acquired.

## Practice

- [ ] Print the numbers 1 to 20, but print `three` instead of every multiple of 3.
- [ ] Rewrite the bound-and-sentinel `while` loop from this chapter as a `for` loop. Which one states
      the loop's contract more clearly, and why?
- [ ] Write a `do-while` loop that keeps asking for a positive number until it gets one, printing the
      prompt each time. It needs input, so it will not be run automatically — build it and drive it
      with a pipe.
- [ ] Write a `switch` over a `char` grade (`'A'`…`'F'`) that prints a comment for each. Make every
      case end in `break` or `return`, then compile with `-Wall -Wextra -Werror`.
- [ ] Now add a deliberate fall-through to that `switch` by stacking two labels on one body. Explain
      in one sentence why you would want that.
- [ ] Rewrite a function that allocates two buffers as a `goto cleanup` function, and confirm that
      both buffers are freed on every failure path.

## Solutions

:::solution Exercise 1
A loop and a branch.

```c run
#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 20; i++) {
        if (i % 3 == 0) {
            printf("three ");
        } else {
            printf("%d ", i);
        }
    }
    printf("\n");
    return 0;
}
```

```text
1 2 three 4 5 three 7 8 three 10 11 three 13 14 three 16 17 three 19 20
```

`i % 3 == 0` is the test for divisibility, using the remainder operator from Chapter 4. The loop is a
`for` because the count is known: twenty iterations, starting at 1. Note the braces on both branches
even though each holds one statement — that is the habit from earlier in this chapter, and it costs
nothing.
:::

:::solution Exercise 3
Ask first, validate after — which is what `do-while` is for.

```c compile
#include <stdio.h>

int main(void) {
    int value = 0;

    do {
        printf("Enter a positive number: ");
        if (scanf("%d", &value) != 1) {
            fprintf(stderr, "that is not a number\n");
            return 1;
        }
    } while (value <= 0);

    printf("accepted %d\n", value);
    return 0;
}
```

Build it and drive it with a pipe so the prompts are visible in one go:

```bash
printf -- '-3\n0\n7\n' | ./prompt
```

```text
Enter a positive number: Enter a positive number: Enter a positive number: accepted 7
```

The prompt appears three times because the body ran three times: once for `-3`, once for `0`, once for
`7`. This is the `do-while` shape doing its job — a `while (value <= 0)` loop would have to be primed
with a fake initial value to reach the same behaviour, which is exactly the awkwardness the `do-while`
exists to remove. The `!= 1` check on `scanf` is the Chapter 2 rule: it tells you whether the input was
actually a number, which matters because a failed `scanf` leaves `value` unchanged and would otherwise
loop forever on the same bad input.
:::

:::solution Exercise 4 and 5
Every case ends in `return`, and two pairs of labels share a body deliberately.

```c run
#include <stdio.h>

static const char *comment_for(char grade) {
    switch (grade) {
    case 'A':
    case 'B':
        return "good";
    case 'C':
        return "acceptable";
    case 'D':
    case 'F':
        return "needs work";
    default:
        return "unknown grade";
    }
}

int main(void) {
    const char grades[] = {'A', 'C', 'D', 'X'};

    for (int i = 0; i < 4; i++) {
        printf("%c: %s\n", grades[i], comment_for(grades[i]));
    }
    return 0;
}
```

```text
A: good
C: acceptable
D: needs work
X: unknown grade
```

`case 'A':` has no statements and no `break`, so control falls straight into `case 'B':` — and that is
the point. Stacking labels is how you say "these values share a body" without repeating the body, and
it is the one form of fall-through that is unambiguously intentional. The `default` case catches
everything else, which matters here because `'X'` is not a grade: without it the function would fall
off the end without returning a value, which is undefined behaviour.
:::

:::solution Exercise 6
One cleanup path, reached from every failure.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int status = 0;
    int *first = NULL;
    int *second = NULL;

    first = malloc(sizeof(int) * 4);
    if (first == NULL) {
        status = 1;
        goto cleanup;
    }

    second = malloc(sizeof(int) * 4);
    if (second == NULL) {
        status = 1;
        goto cleanup;
    }

    first[0] = 20;
    second[0] = 22;
    printf("total %d\n", first[0] + second[0]);

cleanup:
    free(second);
    free(first);
    return status;
}
```

```text
total 42
```

Both pointers start as `NULL`, and `free(NULL)` is defined to do nothing, so the cleanup block is
correct whether the failure happened before the first allocation, between the two, or not at all. That
initialisation is not decoration — without it, a failure on the first `malloc` would send you to
`cleanup` with `first` and `second` holding whatever garbage was on the stack, and `free` on an
uninitialised pointer is undefined behaviour. Note also that the label is at the end and every `goto`
jumps forward to it; a `goto` that jumps backwards is a loop wearing a disguise.
:::
