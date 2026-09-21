#!/usr/bin/env python3
"""Chapter 48 demo -- the recursion tree, counted.

The naive Fibonacci function is the standard example of exponential blow-up,
and it is standard because the blow-up is visible without any instrumentation:
count the calls and the numbers double every time n grows by one.

Counting rather than timing is what makes the claim checkable. The call count
is a property of the recurrence and the input, so it is the same on every
machine -- and it says exactly how much work is being thrown away.
"""


def fib_naive(n, tally):
    """Two recursive calls per node of the tree, and no memory of anything."""
    tally[0] += 1
    if n < 2:
        return n
    return fib_naive(n - 1, tally) + fib_naive(n - 2, tally)


def distinct_subproblems(n):
    """The naive tree solves fib(0)..fib(n) over and over. The number of
    *different* things it is asked to compute is n + 1."""
    return n + 1


def fib_value(n):
    """The same sequence, computed in the obvious cheap way, for a check."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print("naive fibonacci, calls counted")
print()
print(f"{'n':>4}{'calls':>14}{'distinct':>10}{'reuse':>9}{'calls/2^n':>11}")
print("-" * 48)
rows = []
for n in (5, 10, 15, 20, 25, 30):
    tally = [0]
    value = fib_naive(n, tally)
    calls = tally[0]
    distinct = distinct_subproblems(n)
    rows.append((n, calls, distinct, value))
    print(f"{n:>4}{calls:>14,}{distinct:>10,}{calls / distinct:>9.0f}"
          f"{calls / 2 ** n:>11.3f}")
print()
first, last = rows[0], rows[-1]
print(f"  fib(30) = {last[3]:,}")
print(f"  calls grew from {first[1]:,} at n = 5 to {last[1]:,} at n = 30")
print(f"  a factor of {last[1] / first[1]:,.0f} over "
      f"{last[0] - first[0]} more units of n")
print()
print("Read the last column carefully, because the obvious reading of it is")
print("wrong. It does not settle at a constant -- it shrinks by a constant")
print("*factor* every time n goes up by one. The call count grows like the")
print("golden ratio to the n; 2^n grows like 2 to the n; so their ratio")
print("behaves like (phi/2)^n, which is still exponential, just downhill.")
print()
print("That is what 'the same growth rate' means precisely. Not that the two")
print("counts are proportional, but that they differ by a constant factor")
print("*inside the exponent*. It is the reason O(2^n) and O(phi^n) name the")
print("same class, and the reason the shape of the curve matters here rather")
print("than the constant in front of it.")
print()
print("The reuse column is the other half of the story, and it is the one that")
print("makes the fix obvious. At n = 30 the function is called")
print(f"{last[1]:,} times to compute {last[2]} distinct values -- each value computed")
print(f"about {last[1] / last[2]:,.0f} times. The tree is not doing {last[1]:,} different")
print(f"things; it is doing {last[2]} different things over and over.")
print()
print("That is what 'overlapping subproblems' means, and it is worth stating")
print("precisely because the phrase is used loosely. It does not mean the")
print("problem has a recursive definition -- everything recursive does. It")
print("means the recursion tree contains the *same node* many times.")
print()
print()
print("The tree, drawn small")
print()


def draw(n, depth, lines):
    lines.append("  " + "  " * depth + f"fib({n})")
    if n >= 2:
        draw(n - 1, depth + 1, lines)
        draw(n - 2, depth + 1, lines)


lines = []
draw(5, 0, lines)
for line in lines:
    print(line)
print(f"  -- {len(lines)} nodes, for fib(5), which has "
      f"{distinct_subproblems(5)} distinct values")
print()
print("Look for the repeats: fib(2) appears three times and fib(1) five")
print("times. Every one of those subtrees is identical work, and every one")
print("of them is thrown away the moment it finishes, because the function")
print("keeps no memory between calls.")
print()
print("A cache turns that tree into a line. The first time fib(2) is asked")
print("for, the answer is computed and stored; every later ask is a lookup.")
print("The tree does not get smaller -- it stops being built.")
print()
print(f"  nodes in the tree for fib(5)  : {len(lines)}")
print(f"  distinct values for fib(5)    : {distinct_subproblems(5)}")
print(f"  nodes in the tree for fib(30) : {last[1]:,}")
print(f"  distinct values for fib(30)   : {last[2]:,}")
print(f"  the ratio grows as fast as the tree does: "
      f"{last[1] / last[2]:,.0f}x at n = 30")
print()
print()
print("The node count has a closed form")
print()
print("It is worth stating, because it is a check on the whole exercise")
print("rather than a new fact: the number of calls needed to compute fib(n)")
print("naively is 2*F(n+1) - 1, where F is the same sequence being computed.")
print("The function's own value tells you how many times it was called.")
print()
print(f"{'n':>4}{'calls counted':>16}{'2*F(n+1) - 1':>16}{'agree':>8}")
print("-" * 44)
for n, calls, _, _ in rows:
    formula = 2 * fib_value(n + 1) - 1
    print(f"{n:>4}{calls:>16,}{formula:>16,}{str(calls == formula):>8}")
print()
print("Every row agrees, and the reason is that the count satisfies the same")
print("recurrence as the value -- one step ahead of it. Calls(n) = 1 +")
print("Calls(n-1) + Calls(n-2) is exactly fib's own recurrence with a 1")
print("added, which is why the solution comes out as a Fibonacci number and")
print("not as something with 2^n in it.")
print()
print("That also pins down the decay rate in the first table, which can then")
print("be checked rather than asserted. If calls(n) grows like phi^n, then")
print("calls(n)/2^n grows like (phi/2)^n -- so five units of n should shrink")
print("it by a factor of (phi/2)^5, every time, forever.")
print()
PHI = (1 + 5 ** 0.5) / 2
STEP = (PHI / 2) ** 5
print(f"   n   calls/2^n   vs 5 rows back   (phi/2)^5     error")
print("-" * 56)
previous = None
errors = []
for n, calls, _, _ in rows:
    ratio = calls / 2 ** n
    if previous is None:
        print(f"{n:>4}{ratio:>12.6f}{'-':>17}{'-':>12}{'-':>10}")
    else:
        back = ratio / previous
        error = back - STEP
        errors.append(error)
        print(f"{n:>4}{ratio:>12.6f}{back:>17.6f}{STEP:>12.6f}{error:>10.1e}")
    previous = ratio
print()
span = (len(errors) - 1) * 5
total = errors[0] / errors[-1]
per_step = total ** (1 / (len(errors) - 1))
print("The third column converges on the fourth and stays there, and the")
print("last column shows how fast: the error falls by a factor of")
print(f"{total:,.0f} over the {span} units of n between the first and last row --")
print(f"about {per_step:.0f}x for every five units. That factor is (1/phi)^5, the")
print("other half of the same asymptotic: the neglected term in Binet's")
print("formula shrinks like psi^n, where psi is -1/phi.")
print()
print("The first row is the one that has not converged yet, and that is")
print("expected -- at n = 10 the correction terms are still comparable to the")
print("leading one, so the asymptotic has not taken over. It is worth")
print("noticing that the *first* row is the one that lies, which is a")
print("pattern that recurs everywhere counts are used to justify a claim")
print("about growth.")
print()
print("This is the useful habit in miniature. A claim like 'the growth rate")
print("is phi' is not verifiable on its own, because phi is irrational and no")
print("run will ever print it. But the *ratio of ratios* is a clean number,")
print("and it is the same on every machine.")
