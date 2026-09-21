---
chapter: 39
part: 7
title: From Source to Bytecode
summary: Follow a line of Python from the text you type to the instructions the interpreter actually runs — and use that to explain behaviour that otherwise looks like magic.
minutes: 55
tags: [bytecode, dis, AST, compile, CPython, performance]
---

You have written working Python for thirty-eight chapters, and there is still a black box in the
middle of it. You press Enter and something happens. Sometimes it happens quickly and sometimes it
does not, and the only advice you have for the slow case is "use a set instead of a list", which
you have repeated often enough to believe without being able to defend.

This chapter opens the box. It is not trivia. Between the text you type and the result you see
there are exactly three stages, and knowing them explains a whole family of things that otherwise
look arbitrary: why a local variable is faster than a global, why `x = 1 + 2 * 3` does no arithmetic
at run time, why `assert` disappears under `-O` and takes your validation with it, why
`__pycache__` exists, and why two functions that look equally simple can differ by a factor of two.
That knowledge is also the foundation for Part VIII: you cannot reason about the cost of an
algorithm if you do not know what a single operation costs.

## What actually happens when you press Enter

Python runs your file in three stages, and they are separate programs:

1. **Parse.** A tokenizer splits the text into tokens, and a parser turns those into a tree — the
   **abstract syntax tree**, or AST. This is the only stage that ever sees your text as text.
2. **Compile.** The tree is walked and turned into **bytecode**: a flat list of simple instructions
   for a virtual machine. Constant folding and other small optimisations happen here.
3. **Execute.** The bytecode runs on the **evaluation loop** — a loop inside the interpreter that
   reads one instruction at a time and does what it says.

Only stage 1 can fail with a `SyntaxError`, and that is why a syntax error appears before any of
your code runs, even the `print` on line one. Stages 2 and 3 operate on structures, not text.

## Stage one: the parser builds a tree

The `ast` module hands you stage one's output directly.

```python run
import ast

SOURCE = "total = price * 1.2 + 5"

print("1. the text you typed")
print("  ", SOURCE)

print("\n2. the AST the parser produced")
tree = ast.parse(SOURCE)
print(ast.dump(tree, indent=2))

print("\n3. the code object the compiler produced")
code = compile(SOURCE, "<demo>", "exec")
print("   co_consts :", code.co_consts)
print("   co_names  :", code.co_names)
print("   co_stacksize:", code.co_stacksize)
```

```text
1. the text you typed
   total = price * 1.2 + 5

2. the AST the parser produced
Module(
  body=[
    Assign(
      targets=[
        Name(id='total', ctx=Store())],
      value=BinOp(
        left=BinOp(
          left=Name(id='price', ctx=Load()),
          op=Mult(),
          right=Constant(value=1.2)),
        op=Add(),
        right=Constant(value=5)))])

3. the code object the compiler produced
   co_consts : (1.2, 5, None)
   co_names  : ('price', 'total')
   co_stacksize: 2
```

Read the tree and you can see the two facts that decide everything downstream.

**The tree has structure the text did not.** `total = price * 1.2 + 5` is a string of characters;
the tree knows that `*` binds tighter than `+`, and it says so by nesting — the `Mult` node is
*inside* the `Add` node. Precedence is a property of the tree, not of the text. That is why
`ast.parse` is the right tool for anything that needs to understand Python rather than run it.

**The compiler reads the tree, not the text.** `co_consts` is `(1.2, 5, None)` — and it does not
contain `7`, because `price` is a variable and `price * 1.2 + 5` cannot be folded. Write the
foldable version instead and the arithmetic vanishes:

```python repl
>>> compile("x = 1 + 2 * 3", "<s>", "exec").co_consts
(7, None)
>>> import dis
>>> dis.dis(compile("x = 1 + 2 * 3", "<s>", "exec"))
  0           RESUME                   0

  1           LOAD_CONST               0 (7)
              STORE_NAME               0 (x)
              RETURN_CONST             1 (None)
```

There is no addition in that bytecode. The expression was computed by the compiler, once, and the
result baked in as a constant. `co_consts`, `co_names` and `co_varnames` are the three tables a
code object carries, and they are the compiler's answer to "what does this function need to look
up, and where does each name live?"

## Bytecode is a stack machine

The instructions operate on a **stack**. `LOAD_FAST a` pushes `a`; `BINARY_OP` pops two values,
applies the operator, and pushes the result. Nothing is stored in a register and nothing is
addressable at random — the stack is the only workspace.

That makes `co_stacksize` meaningful: it is the maximum depth the stack ever reaches, and the
compiler works it out statically.

```python run
import dis

def add(a, b):
    return a + b

def add_both(a, b):
    return a + b, a - b

print("co_stacksize of add      :", add.__code__.co_stacksize)
print("co_stacksize of add_both :", add_both.__code__.co_stacksize)

print("\nadd:")
dis.dis(add)
print("\nadd_both:")
dis.dis(add_both)
```

```text
co_stacksize of add      : 2
co_stacksize of add_both : 3

add:
  3           RESUME                   0

  4           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP                0 (+)
              RETURN_VALUE

add_both:
  6           RESUME                   0

  7           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP                0 (+)
              LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP               10 (-)
              BUILD_TUPLE              2
              RETURN_VALUE
```

`add` peaks at two values on the stack; `add_both` peaks at three, because it needs both results
alive at once to build the tuple. `BUILD_TUPLE 2` pops two and pushes one.

:::warning Your bytecode will not match this chapter's bytecode
Opcode names, their numbering, and which instructions exist at all change between Python versions.
`LOAD_FAST_LOAD_FAST` and `RETURN_CONST` in the output above are 3.12/3.13 additions — they exist
because newer CPythons merge common instruction pairs into one. On 3.10 the same function is a
different list of instructions with the same meaning.

So read the *shape*: which names are looked up, how many jumps there are, whether something is a
constant. Never memorise an opcode number, and never write a test that asserts on `dis` output
without pinning the interpreter version.
:::

## A loop is a jump

There is no loop instruction. A loop is an instruction that moves the instruction pointer
backwards, guarded by a test.

```python run
import dis

def total(xs):
    s = 0
    for x in xs:
        s += x
    return s

dis.dis(total)
```

```text
  3           RESUME                   0

  4           LOAD_CONST               1 (0)
              STORE_FAST               1 (s)

  5           LOAD_FAST                0 (xs)
              GET_ITER
      L1:     FOR_ITER                 7 (to L2)
              STORE_FAST               2 (x)

  6           LOAD_FAST_LOAD_FAST     18 (s, x)
              BINARY_OP               13 (+=)
              STORE_FAST               1 (s)
              JUMP_BACKWARD            9 (to L1)

  5   L2:     END_FOR
              POP_TOP

  7           LOAD_FAST                1 (s)
              RETURN_VALUE
```

Three things are worth reading off that listing.

`GET_ITER` calls `__iter__` **once**, before the loop starts — not once per iteration. That is why
Chapter 14 insisted that an iterable is not an iterator: the loop asks for the iterator a single
time and then only ever calls `next` on it, via `FOR_ITER`. `FOR_ITER` is `next()` plus a jump: it
pushes the next value, or jumps to the exit when the iterator raises `StopIteration`. The exception
is not propagated to you; the loop consumes it.

`JUMP_BACKWARD 9 (to L1)` is the loop. The compiler emitted a backward jump, and it is the target
of `FOR_ITER`'s exit that leaves. The `L1`/`L2` labels are the compiler's names for jump targets;
they are shown for your benefit and do not exist at run time.

The `s += x` line is one `BINARY_OP 13 (+=)` — an in-place add. That matters: for an immutable
type like `int` it is the same as `s = s + x`, but for a list `+=` calls `__iadd__` and mutates in
place, which is exactly the aliasing behaviour Chapter 6 warned about. The bytecode shows you that
the interpreter treats them as different operations.

## Where a name lives decides what it costs

This is the part with immediate practical value. Every name you use is resolved by one of a small
number of instructions, and they are not equally expensive.

```python run
import dis

LIMIT = 100
WATCHED = {"LOAD_GLOBAL", "LOAD_FAST", "LOAD_FAST_LOAD_FAST", "LOAD_ATTR", "COMPARE_OP"}

def uses_global(xs):
    out = []
    for x in xs:
        if x < LIMIT:
            out.append(x)
    return out

def uses_local(xs):
    limit = LIMIT
    out = []
    for x in xs:
        if x < limit:
            out.append(x)
    return out

def show(fn):
    print(f"{fn.__name__}:")
    for ins in dis.get_instructions(fn):
        if ins.opname in WATCHED:
            print(f"    {ins.opname:<20} {ins.argrepr}")
    print()

show(uses_global)
show(uses_local)
```

```text
uses_global:
    LOAD_FAST            xs
    LOAD_FAST            x
    LOAD_GLOBAL          LIMIT
    COMPARE_OP           bool(<)
    LOAD_FAST            out
    LOAD_ATTR            append + NULL|self
    LOAD_FAST            x
    LOAD_FAST            out

uses_local:
    LOAD_GLOBAL          LIMIT
    LOAD_FAST            xs
    LOAD_FAST_LOAD_FAST  x, limit
    COMPARE_OP           bool(<)
    LOAD_FAST            out
    LOAD_ATTR            append + NULL|self
    LOAD_FAST            x
    LOAD_FAST            out
```

The loop body is the contrast. `uses_global` does `LOAD_FAST x`, `LOAD_GLOBAL LIMIT`,
`COMPARE_OP`. `uses_local` does `LOAD_FAST_LOAD_FAST x, limit`, `COMPARE_OP` — the local is fetched
by the same instruction that fetches `x`.

Both versions take two instructions to perform the comparison, so this is not a story about
instruction count. It is a story about **what one instruction costs**:

- `LOAD_FAST` indexes a fixed-size array of the function's locals, by slot number. `co_varnames`
  gives the mapping, and it is decided at compile time. There is no dictionary involved.
- `LOAD_GLOBAL` looks the name up in the module's globals **dictionary**, then falls back to the
  builtins dictionary if it is not there. A miss on the first is a common case, not an error.
- `LOAD_ATTR` looks the attribute up on the object — which may run a `@property` getter, a
  descriptor, or `__getattr__`, all of which are arbitrary Python code. Chapter 42 is entirely
  about what happens here.

So the ordering `local < global < attribute` is a property of the mechanism, not folklore. Hoisting
a global or an attribute into a local before a hot loop removes a dictionary lookup per iteration.

**Measure before you act on that.** On the machine this chapter was written on, hoisting the global
gave roughly a 20% improvement in a tight loop and hoisting an attribute roughly 18% — real, and
also well under the factor of two that people repeat. Since 3.11 the interpreter *specialises*
`LOAD_GLOBAL` at run time, caching the result for a known module, so the gap is narrower than it
was in older versions. The honest summary: the mechanism guarantees the direction, only a
measurement tells you the size, and Chapter 58 is where you learn to take that measurement.

:::pitfall Reading bytecode is not profiling
The most common way this chapter makes you slower is the temptation to hand-optimise from `dis`
output. You spot a `LOAD_GLOBAL` in a loop, hoist it, and feel productive — while the actual cost
of that function is dominated by the network call three lines down, or by the fact that you are
searching a list where a set would do.

Bytecode tells you the *shape* of a computation: which names are looked up, how many jumps there
are, what is a constant. It cannot tell you which line matters. Profile first — Chapter 58 — and
reach for `dis` only to explain a result you already have.
:::

## The `.pyc` cache

Compiling is work, and the result does not depend on the data, so Python caches it. Import a module
and CPython writes the compiled code object to a file next to the source.

```python run
import importlib.util, sys

print("the cache file a module would get:")
print("  ", importlib.util.cache_from_source("shop/pricing.py"))

print("\nsource suffix and magic:")
print("   sys.implementation.cache_tag:", sys.implementation.cache_tag)
print("   importlib.util.MAGIC_NUMBER :", importlib.util.MAGIC_NUMBER.hex())
```

```text
the cache file a module would get:
   shop/__pycache__/pricing.cpython-313.pyc

source suffix and magic:
   sys.implementation.cache_tag: cpython-313
   importlib.util.MAGIC_NUMBER : f30d0d0a
```

Three details in that filename are doing real work, and each one is a bug avoided.

The **magic number** is written at the top of every `.pyc`. If it does not match the interpreter's,
the file is ignored and the source is recompiled — which is why installing a new Python does not
silently run old bytecode.

The **cache tag**, `cpython-313`, names the implementation *and* version. So CPython 3.13 and PyPy
never read each other's caches, and neither do 3.13 and 3.12. A `.pyc` is not portable bytecode.

The **source timestamp and size** are stored after the magic number, and the cache is discarded
when either changes. That is why editing a file takes effect immediately and why a stale `.pyc` is
almost never the cause of the bug you are chasing.

Two consequences you will actually meet. `__pycache__` should be in `.gitignore` — it is derived
data, and committing it means every developer commits a different binary for the same source. And a
program you *run* directly, `python3 script.py`, is not cached at all; only imported modules are.
That is why the first run of a large application is slower than the second.

## `-O` and `-OO` change what gets compiled

The compiler reads flags, and two of them delete code.

```python run
import os, subprocess, sys, tempfile, textwrap

SOURCE = textwrap.dedent('''
    """Module docstring."""
    def f(x):
        """Function docstring."""
        assert x > 0, "x must be positive"
        return x * 2

    print("__debug__    =", __debug__)
    print("module doc   =", repr(__doc__))
    print("f.__doc__    =", repr(f.__doc__))
    print("f(-1)        =", f(-1))
''')

with tempfile.TemporaryDirectory() as td:
    path = os.path.join(td, "demo.py")
    with open(path, "w") as fh:
        fh.write(SOURCE)
    for flags in ([], ["-O"], ["-OO"]):
        label = "python3 " + " ".join(flags) if flags else "python3"
        print(f"--- {label}")
        proc = subprocess.run([sys.executable, *flags, path],
                              capture_output=True, text=True)
        print(proc.stdout.rstrip())
        if proc.stderr.strip():
            print("stderr:", proc.stderr.strip().splitlines()[-1])
        print()
```

```text
--- python3
__debug__    = True
module doc   = 'Module docstring.'
f.__doc__    = 'Function docstring.'
stderr: AssertionError: x must be positive

--- python3 -O
__debug__    = False
module doc   = 'Module docstring.'
f.__doc__    = 'Function docstring.'
f(-1)        = -2

--- python3 -OO
__debug__    = False
module doc   = None
f.__doc__    = None
f(-1)        = -2
```

This is Chapter 9's "`assert` is for developers, not users" made mechanical. Under `-O` the assert
is not *skipped*; it is **not compiled**. There is no bytecode for it, no check, and no message.
`f(-1)` returns `-2` and the `"x must be positive"` text is gone from the program.

That is the whole argument in one output block. If you used `assert` to validate a value that came
from a user, a file, or a network, then whoever runs your code with `-O` — some distributions do —
has removed your validation. Raise an exception instead; `raise` is compiled in every mode.

`-OO` goes further and strips docstrings, which is why `__doc__` is `None`. Do not run `-OO` on a
codebase that relies on docstrings at run time: FastAPI, Pydantic and Click all read them.

:::scenario A batch job is too slow and the profiler points at a loop
A nightly job processes 400,000 rows and takes eleven minutes. The profiler says 70% of the time is
inside `apply_rules`, which is forty lines long and does nothing but compare each row's fields
against a set of thresholds held in module-level configuration. Nobody can see anything expensive in
it.

The `dis` output shows why. The thresholds are module globals, so every comparison in the inner
loop is a `LOAD_GLOBAL` — a dictionary lookup in the module namespace — and each row's fields are
read with `LOAD_ATTR`, which is a full attribute lookup on an object. The inner loop runs about
four million times, so that is four million dictionary lookups that the function does not need.
:::

:::solution Hoist the lookups, then measure
Bind the globals and the attributes to locals once, before the loop:

```python
def apply_rules(rows, thresholds):
    low, high, cap = thresholds["low"], thresholds["high"], thresholds["cap"]
    out = []
    for row in rows:
        amount = row.amount
        if low <= amount <= high:
            out.append(min(amount, cap))
    return out
```

Every name in the loop body is now a local, so the loop is `LOAD_FAST` and `BINARY_OP` with no
dictionary lookups at all.

Then do the part people skip: measure. Hoisting is a mechanism, not a guarantee — on the machine
this chapter was written on it was worth about 20%, and if the same function spends 60% of its time
parsing dates then you have improved 20% of 40%. `cProfile` before and after, and if the numbers do
not move, keep the version that reads better. Chapter 58 covers that workflow properly.
:::

## What this chapter is not

Everything above describes **CPython**, the implementation you almost certainly installed. Python is
a language with a specification; CPython is one program that implements it, and its bytecode is an
internal detail with no compatibility promise.

The differences are not academic. **PyPy** has a just-in-time compiler and no `dis` output worth
reading — the same program can be several times faster or slower. **GraalPy** runs on the JVM. The
**free-threaded** builds of 3.13 remove the GIL, so the concurrency chapter's advice changes shape.
And CPython itself changes: 3.11 added an *adaptive* interpreter that rewrites hot instructions into
specialised forms as the program runs, which is why the bytecode you disassemble once may not be
what executes on the millionth iteration.

The durable content of this chapter is the three-stage pipeline, the stack machine, and the fact
that a name's home — local slot, module dict, or object attribute — is what decides the cost of
reading it. Those hold in every implementation. The opcode names do not.

That distinction is the whole point of Part VII. In the next four chapters we stay at this level and
answer the questions the API cannot: what is an object, really, and what does creating one do?
Where does memory come from and when does it go back? And what single mechanism produces
`@property`, `@classmethod`, `@staticmethod` and every method you have ever called?

## Key takeaways

- Python runs your file in three stages — parse to an AST, compile to bytecode, execute on the
  evaluation loop — and only the first one sees your code as text.
- Precedence and structure live in the AST, not the text, so `ast.parse` is the right tool for
  analysing Python rather than running it.
- Bytecode is a stack machine: instructions push and pop, and `co_stacksize` is the maximum depth
  the compiler computed for the function.
- The compiler folds constants, so `x = 1 + 2 * 3` contains no addition at run time.
- A loop is a backward jump guarded by `FOR_ITER`, which calls `next()` and consumes
  `StopIteration` rather than raising it.
- A name's home decides the cost of reading it: `LOAD_FAST` indexes a compile-time slot,
  `LOAD_GLOBAL` does a dictionary lookup, and `LOAD_ATTR` may run arbitrary Python.
- Hoisting a global or attribute into a local removes a lookup per iteration — real, measurable, and
  usually well under the factor of two that people claim.
- `assert` is not compiled under `-O` and docstrings are stripped under `-OO`, which is why
  validation must use `raise`.
- Imported modules are cached in `__pycache__` as `.pyc` files keyed by magic number, cache tag and
  source timestamp; a directly-run script is not cached.
- Opcodes are a CPython implementation detail and change between versions. Read the shape, never
  memorise the numbers.

## Practice

- [ ] Compile a small expression with `compile(...)` and print `co_consts`, `co_names`,
      `co_varnames` and `co_stacksize`. Predict each one before you run it.
- [ ] Write a function with an `if`/`else` and disassemble it. Identify the conditional jump and the
      unconditional jump, and say which branch is the fall-through.
- [ ] Take a loop you have written in an earlier chapter and rewrite it so that every name read
      inside the loop is a local. Disassemble both and count the `LOAD_GLOBAL` and `LOAD_ATTR`
      instructions that remain.
- [ ] Use `ast.parse` to list every function definition in a file, with its argument names. Do it
      without importing the file.
- [ ] Run a script containing an `assert` under both `python3` and `python3 -O`, and show that the
      assert is absent from the bytecode rather than skipped.
- [ ] Predict, then verify, the `co_stacksize` of a function containing `a + b + c + d`. Explain the
      number you get.

## Solutions

:::solution Exercise 1
```python run
code = compile("result = a * 2 + 1", "<exercise>", "exec")
print("co_consts  :", code.co_consts)
print("co_names   :", code.co_names)
print("co_varnames:", code.co_varnames)
print("co_stacksize:", code.co_stacksize)
```

```text
co_consts  : (2, 1, None)
co_names   : ('a', 'result')
co_varnames: ()
co_stacksize: 2
```

`co_consts` holds the literals the compiler kept, plus the implicit `None` a module returns.
`co_names` holds the names that must be looked up at run time — `a` because it is read from the
module namespace, and `result` because it is *stored* there. `co_varnames` is empty because at
module level nothing lives in a function's local slots: module code uses `STORE_NAME` and
`LOAD_NAME`, which go through the namespace dictionary, rather than the `LOAD_FAST`/`STORE_FAST`
slot instructions a function uses.

`co_stacksize` is 2, and the arithmetic explains it. `a * 2` needs two slots; `BINARY_OP` collapses
them to one. `+ 1` then needs two again, and `BINARY_OP` collapses those. The peak is 2 no matter
how long the expression gets, because the compiler is building a left-associative chain and only
ever holds one pending result.
:::

:::solution Exercise 2
```python run
import dis

def describe(n):
    if n > 0:
        return "positive"
    else:
        return "not positive"

dis.dis(describe)
```

```text
  3           RESUME                   0

  4           LOAD_FAST                0 (n)
              LOAD_CONST               1 (0)
              COMPARE_OP             148 (bool(>))
              POP_JUMP_IF_FALSE        1 (to L1)

  5           RETURN_CONST             2 ('positive')

  7   L1:     RETURN_CONST             3 ('not positive')
```

`POP_JUMP_IF_FALSE 1 (to L1)` is the conditional jump. The `if` body is the **fall-through** — it
runs when the condition is true and no jump is taken — while the `else` body is the jump target.
That is the compiler's convention: it lays out the first branch inline and makes the second the
target. The absence of an unconditional jump at the end is worth noticing too: each branch returns,
so neither needs to skip over the other.

Notice also that the `COMPARE_OP` argument is 148 here and 18 in the earlier listing. The argument
is not an opcode you should read; it is an index into a table of comparison operations, and the
numbering shifts between versions. The parenthesised `(bool(>))` is the part meant for you.
:::

:::solution Exercise 3
```python run
import dis

THRESHOLD = 10

class Row:
    def __init__(self, value):
        self.value = value

def before(rows):
    out = []
    for row in rows:
        if row.value > THRESHOLD:
            out.append(row.value)
    return out

def after(rows):
    threshold = THRESHOLD
    out = []
    for row in rows:
        value = row.value
        if value > threshold:
            out.append(value)
    return out

def loop_body(fn):
    ops = list(dis.get_instructions(fn))
    start = next(i for i, o in enumerate(ops) if o.opname == "FOR_ITER")
    end = max(i for i, o in enumerate(ops) if o.opname == "JUMP_BACKWARD")
    return ops[start:end + 1]

for fn in (before, after):
    counts = {}
    for ins in loop_body(fn):
        counts[ins.opname] = counts.get(ins.opname, 0) + 1
    print(f"{fn.__name__:7s} {counts}")
```

```text
before  {'FOR_ITER': 1, 'STORE_FAST': 1, 'LOAD_FAST': 3, 'LOAD_ATTR': 3, 'LOAD_GLOBAL': 1, 'COMPARE_OP': 1, 'POP_JUMP_IF_TRUE': 1, 'JUMP_BACKWARD': 2, 'CALL': 1, 'POP_TOP': 1}
after   {'FOR_ITER': 1, 'STORE_FAST': 2, 'LOAD_FAST': 3, 'LOAD_ATTR': 2, 'LOAD_FAST_LOAD_FAST': 1, 'COMPARE_OP': 1, 'POP_JUMP_IF_TRUE': 1, 'JUMP_BACKWARD': 2, 'CALL': 1, 'POP_TOP': 1}
```

The `loop_body` helper is the important part of this exercise, and it is why the numbers mean
something. Counting instructions across the whole function would have been misleading: `before`
reads `THRESHOLD` once and `after` reads it once, so a whole-function count shows the same
`LOAD_GLOBAL` in both. The difference is *where* the read happens, so the window has to be the loop
body — from `FOR_ITER` to the last `JUMP_BACKWARD`.

Inside that window the contrast is exactly what the chapter predicted:

- `LOAD_GLOBAL` disappears from `after` entirely, replaced by `LOAD_FAST_LOAD_FAST`.
- `LOAD_ATTR` drops from 3 to 2, because `before` reads `row.value` twice per iteration — once to
  compare and once to append — while `after` reads it once into `value` and reuses it.
- `STORE_FAST` rises from 1 to 2, which is the cost side of the trade: `after` writes `value` into a
  local slot each iteration to avoid the second attribute read.

That last line is the honest part. Hoisting is not free; it trades a dictionary or attribute lookup
for a slot write. Which one wins depends on the relative cost of the two, which is why Chapter 58
insists on measuring rather than counting instructions.
:::

:::solution Exercise 4
```python run
import ast

SOURCE = """
def first(a, b=2, *rest, **opts):
    return a

def second(x: int) -> str:
    return str(x)

class Thing:
    def method(self, y):
        return y
"""

tree = ast.parse(SOURCE)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        args = [a.arg for a in node.args.args]
        args += [a.arg for a in node.args.kwonlyargs]
        vararg = node.args.vararg.arg if node.args.vararg else None
        kwarg = node.args.kwarg.arg if node.args.kwarg else None
        print(f"{node.name:8s} args={args} vararg={vararg} kwarg={kwarg}")
```

```text
first    args=['a', 'b'] vararg=rest kwarg=opts
second   args=['x'] vararg=None kwarg=None
method   args=['self', 'y'] vararg=None kwarg=None
```

The `vararg` and `kwarg` lines carry a small lesson of their own. `node.args.vararg` is not a name;
it is either `None` or an `ast.arg` node, and printing the node gives you
`<ast.arg object at 0x7f...>` — an address, which is useless and different every run. The name is one
level further in, at `.arg`. This indirection is the AST's whole design: a *node* carries its
position and its children, and the leaf payload is a field on it. Every time an `ast` walk prints
something address-like, you have stopped one level too early.

`ast.walk` visits every node in the tree, so `method` is found without descending into `Thing`
explicitly. Nothing was imported or executed, which is the point: this is static analysis, and it
works on code that cannot be run — code for another platform, code that needs credentials, code
that is syntactically valid but semantically dangerous.

Note that `self` appears as an ordinary argument. That is the truth of it: `self` is not a keyword
or a special form, it is the first parameter of a function that happens to live on a class, and the
interpreter passes the instance in when you call it through the instance. Chapter 42 shows exactly
where that argument comes from.
:::

:::solution Exercise 5
```python run
import os, subprocess, sys, tempfile, textwrap

SOURCE = textwrap.dedent('''
    def withdraw(balance, amount):
        assert amount > 0, "amount must be positive"
        return balance - amount

    print(withdraw(100, -5))
''')

PROBE = textwrap.dedent('''
    import dis, sys

    def opnames(code):
        found = [i.opname for i in dis.get_instructions(code)]
        for const in code.co_consts:
            if hasattr(const, "co_code"):
                found += opnames(const)
        return found

    code = compile(open(sys.argv[1]).read(), sys.argv[1], "exec")
    print([n for n in opnames(code) if "ASSERT" in n or n.startswith("RAISE")])
''')

with tempfile.TemporaryDirectory() as td:
    demo = os.path.join(td, "demo.py")
    probe = os.path.join(td, "probe.py")
    with open(demo, "w") as fh:
        fh.write(SOURCE)
    with open(probe, "w") as fh:
        fh.write(PROBE)

    for flags in ([], ["-O"]):
        proc = subprocess.run([sys.executable, *flags, probe, demo],
                              capture_output=True, text=True)
        label = "python3 -O" if flags else "python3"
        print(f"{label:11s} -> {proc.stdout.strip()}")
```

```text
python3     -> ['LOAD_ASSERTION_ERROR', 'RAISE_VARARGS']
python3 -O  -> []
```

Two details in this program are the actual lesson, and both are easy to get wrong.

The first is `opnames`. `dis.get_instructions` does **not** descend into nested code objects. Called
on the module's code object it lists the module's own instructions — `LOAD_CONST` of the function,
`STORE_NAME`, `LOAD_NAME` of `print`, `CALL` — and never looks inside `withdraw`. The `assert` is in
`withdraw`, so a non-recursive probe reports `[]` for *both* runs and the exercise proves nothing.
The fix is to walk `co_consts` and recurse into anything that has a `co_code`: nested functions,
lambdas, comprehensions and class bodies are all stored as constants of their enclosing code object.
This is the same "one level too deep" mistake as the `ast.arg` one in Exercise 4, on a different data
structure — and it is worth noticing that both times the symptom was a *plausible* empty answer
rather than an error.

The second is why the probe runs in a child process. `-O` is decided before the interpreter starts,
so you cannot turn it on from inside a running program. The child gets `-O` on its command line and
the parent reads its stdout.

With both fixed, the result is the evidence. Under `-O` the list is empty — not "the assert was
skipped", but "there is no assert left to skip". The statement was removed during compilation, so
there is no instruction for it in the code object at all.

The surviving version emits two instructions, and they are the two halves of what `assert` means.
`assert amount > 0, "msg"` is defined as "if not `amount > 0`, raise `AssertionError` with `msg`".
`LOAD_ASSERTION_ERROR` pushes the `AssertionError` class, the message is pushed and called, and
`RAISE_VARARGS` raises it. Nothing about that is special-cased at run time; `assert` is syntax sugar
that the parser lowers into ordinary bytecode.
:::

:::solution Exercise 6
```python run
import dis

def left(a, b, c, d):
    return a + b + c + d

def nested(a, b, c, d):
    return (a + b) + (c + d)

for fn in (left, nested):
    print(f"--- {fn.__name__:6s} co_stacksize={fn.__code__.co_stacksize}")
    dis.dis(fn)
```

```text
--- left   co_stacksize=2
  3           RESUME                   0

  4           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP                0 (+)
              LOAD_FAST                2 (c)
              BINARY_OP                0 (+)
              LOAD_FAST                3 (d)
              BINARY_OP                0 (+)
              RETURN_VALUE
--- nested co_stacksize=3
  6           RESUME                   0

  7           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP                0 (+)
              LOAD_FAST_LOAD_FAST     35 (c, d)
              BINARY_OP                0 (+)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

The answer is **2** — not 4, and not 5. Four names are read and three additions happen, so a guess of
4 is natural, and it is wrong.

The reason is associativity. `+` is left-associative, so `a + b + c + d` means `((a + b) + c) + d`.
The compiler walks that left spine, and at every point it needs only two things alive: the running
total and the next operand. `a` and `b` go on (peak 2), `BINARY_OP` collapses them to the total
(stack 1), `c` goes on (stack 2), `BINARY_OP` collapses again, `d` goes on (stack 2), and the last
`BINARY_OP` leaves one value for `RETURN_VALUE`. The peak never exceeds 2. Notice that the compiler
does not even bother pairing `c` and `d` — it has no reason to.

`nested` is the contrast, and it is the point of the exercise. `(a + b) + (c + d)` computes the
*same value*, from the *same four names*, with the *same three additions*. But now the left half has
to stay on the stack while the right half is computed, so at the moment of `LOAD_FAST_LOAD_FAST 35`
the stack holds three things: the left sum, plus `c` and `d`. The peak is 3.

So `co_stacksize` is not a measure of how big the expression is. It is a measure of how many
intermediate values must be *alive at the same time* — and you can change it by adding brackets that
change nothing about the answer. This is the same idea you will meet again in Chapter 58, where the
thing being counted is not instructions but live data.

One last detail, because the `35` looks arbitrary. The argument of `LOAD_FAST_LOAD_FAST` is two
4-bit local-slot numbers packed into one byte: `(first_slot << 4) | second_slot`. For `(a, b)` the
slots are 0 and 1, so the argument is 1. For `(c, d)` the slots are 2 and 3, so it is `0x23` — 35.
That is why the number looks meaningless: it is not a count of anything, it is an encoding. It is
also exactly why the chapter keeps saying not to read the argument and to read the `argrepr` in
parentheses instead.
:::
