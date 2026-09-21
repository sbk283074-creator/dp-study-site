# Fixture — every block here must FAIL, and the harness must catch all nine

One: a `run` block whose output does not match its fence.

```python run
print("hello")
```

```text
goodbye
```

Two: a `run` block that exits non-zero.

```python run
raise SystemExit(3)
```

Three: a `bad` block that is not actually bad.

```python bad
print("I am fine")
```

Four: a `bad` block that does fail, but not in the way the fence claims.

```python bad
raise ValueError("boom")
```

```text
TypeError: a different error entirely
```

Five: a `repl` transcript whose output is wrong.

```python repl
>>> 2 + 3
6
```

Six: a `sh run` block whose output does not match its fence.

```sh run
echo one
```

```text
two
```

Seven: an unknown directive, which must be rejected rather than ignored. This one
is a typo, and a typo must not silently downgrade the block to a fragment.

```python runn
print("typo in the directive")
```

Eight: a `repl` transcript whose continuation line is genuinely not indented.
Preserving indentation after `...` must not go so far as to accept code that
never had any — otherwise the fix for the `lstrip()` bug would make every
compound statement uncheckable.

```python repl
>>> for ch in "python":
... print(ch.upper(), end="")
PYTHON
```

Nine: an elided traceback whose *final* line is wrong. The elision may swallow
the frames, but it must not swallow the exception the fence claims.

```python repl
>>> next(iter([]))
Traceback (most recent call last):
  ...
ValueError: this is not the error that was raised
```
