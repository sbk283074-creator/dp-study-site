#!/usr/bin/env python3
"""Chapter 45 demo -- a stack, and the check that a counter cannot do.

The stack here is a plain list used with a discipline: only append and pop,
never index. That is the whole implementation. The interest is in what the
discipline lets you compute.
"""
PAIRS = {")": "(", "]": "[", "}": "{"}


def check_with_stack(text):
    """A stack remembers not just how many brackets are open but which ones,
    in the order they opened. Returns (ok, max_depth)."""
    stack = []
    max_depth = 0
    for char in text:
        if char in "([{":
            stack.append(char)
            max_depth = max(max_depth, len(stack))
        elif char in PAIRS:
            if not stack or stack.pop() != PAIRS[char]:
                return False, max_depth
    return not stack, max_depth


def check_with_counter(text):
    """The version that looks right and is not. Two integers cannot tell you
    the order the brackets opened, so `([)]` passes."""
    depth = 0
    for char in text:
        if char in "([{":
            depth += 1
        elif char in PAIRS:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


CASES = [
    "()",
    "([)]",
    "{[()]}",
    "((()))",
    "(",
    ")(",
    "",
]

print("is this text's brackets balanced?")
print()
print(f"{'input':>10}{'stack':>10}{'counter':>10}{'max depth':>12}")
print("-" * 42)
for text in CASES:
    ok, depth = check_with_stack(text)
    shown = repr(text) if text else "'' (empty)"
    print(f"{shown:>10}{str(ok):>10}{str(check_with_counter(text)):>10}{depth:>12}")
print()
print("Row 2 is the whole point. `([)]` has two opens and two closes, so a")
print("counter says balanced. It is not balanced, and a parser that believes")
print("the counter will build a tree with the wrong shape -- or, more")
print("usually, will not notice until a later stage does something strange.")
print()
print("The stack gets it right because it stores the *order*. Popping")
print("returns the bracket you are inside, so the comparison")
print("`stack.pop() != PAIRS[char]` is a check a pair of integers cannot")
print("express. The extra memory is O(depth), which for real code is tiny.")
print()
print("max_depth is not decoration either. It is the number you need")
print("before you feed this a file you did not write: a nested input that")
print("is 50,000 deep will not overflow this stack, but it will overflow")
print("the recursive parser in Chapter 48, and depth is how you find out")
print("which one you have before it happens in production.")
