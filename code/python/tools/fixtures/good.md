# Fixture — every block here must PASS

A complete program whose output is checked against the fence beneath it.

```python run
print("hello")
print(2 + 3)
```

```text
hello
5
```

A transcript that must replay exactly, entry by entry.

```python repl
>>> 2 + 3
5
>>> name = "ada"
>>> name.upper()
'ADA'
>>> [n * n for n in range(4)]
[0, 1, 4, 9]
```

An exception entry may show only the final line, the way every Python book does.
The traceback frames above it name a temp file and are not part of the claim.

```python repl
>>> "3" * 15.0
TypeError: can't multiply sequence by non-int of type 'float'
>>> 1 / 0
ZeroDivisionError: division by zero
```

A program that must fail, with the message quoted from the real traceback.

```python bad
raise ValueError("boom")
```

```text
ValueError: boom
```

A block that must parse but must not be run.

```python compile
import sys

if len(sys.argv) > 1:
    print(sys.argv[1])
```

A shell block whose output is checked.

```sh run
echo one
echo two
```

```text
one
two
```

A bare fragment is not run and not counted as an actionable block.

```python
x = 1
```

A program that prints nothing still counts as a pass.

```python run
total = sum(range(10))
assert total == 45
```

A transcript containing multi-line statements. The indentation after `...` is
part of the code and must survive the prompt strip — an `lstrip()` there turns
every `for`, `if` and `def` in a transcript into an `IndentationError`.

```python repl
>>> for ch in "python":
...     print(ch.upper(), end="")
PYTHON
>>> def double(x):
...     return x * 2
...
>>> double(21)
42
>>> total = 0
>>> for n in [1, 2, 3]:
...     total += n
...     print(total)
1
3
6
```

When a book does print the traceback, it elides the frames that name a temp
file with a bare `...` line. That elision must be honoured, but only where it
is actually written.

```python repl
>>> next(iter([]))
Traceback (most recent call last):
  ...
StopIteration
```
