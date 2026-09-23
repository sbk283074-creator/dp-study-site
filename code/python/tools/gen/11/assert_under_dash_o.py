"""Chapter 11 -- assert is not a check, and -O is the proof.

One program with five assertions, two of which are false, run twice: once
normally and once with the optimiser flag. The count is of assertions that
fired, and under the flag the count is zero -- every check reports success,
including the two that are wrong.
"""

import os
import subprocess
import sys
import tempfile

PROGRAM = '''\
CHECKS = [
    ("a value is positive", 5 > 0),
    ("a list is sorted", [1, 2, 3] == sorted([1, 2, 3])),
    ("a value is negative", -5 > 0),
    ("a key is present", "x" in {"x": 1}),
    ("a value is even", 7 % 2 == 0),
]

passed = 0
failed = 0
for label, condition in CHECKS:
    try:
        assert condition, label
        passed += 1
    except AssertionError:
        failed += 1

print(f"{passed} {failed} {__debug__}")
'''

directory = tempfile.mkdtemp()
path = os.path.join(directory, "checks.py")
with open(path, "w", encoding="utf-8") as handle:
    handle.write(PROGRAM)


def run(optimised):
    arguments = [sys.executable] + (["-O"] if optimised else []) + [path]
    finished = subprocess.run(arguments, capture_output=True, text=True)
    passed, failed, debug = finished.stdout.split()
    return int(passed), int(failed), debug


print(f"five assertions, two of them false, run with and without -O")
print()
print(f"{'mode':<14}{'passed':>8}{'failed':>8}{'__debug__':>11}")
print("-" * 41)
for label, optimised in (("no flag", False), ("-O", True)):
    passed, failed, debug = run(optimised)
    print(f"{label:<14}{passed:>8}{failed:>8}{debug:>11}")

print()
print("Without the flag, three assertions pass and two fail -- which is the")
print("correct answer, because two of the five claims are false. With the flag,")
print("all five pass, and the two that are wrong are still wrong, because")
print("nothing changed except whether the check ran.")
print()
print("The third column is the reason. `__debug__` is true by default and false")
print("under `-O`, and `assert` is defined as a statement that does nothing")
print("when `__debug__` is false. So an assertion is a claim that is only")
print("checked in a development run, and a production run with the flag set")
print("executes none of them.")
print()
print("That makes `assert` the right tool for the assumptions a program makes")
print("about itself -- the ones that would be a bug in the program rather than")
print("a problem with the input -- and the wrong tool for validating anything a")
print("caller can control. A validation that disappears when somebody sets a")
print("flag is not a validation; it is a comment that costs a comparison in")
print("development and nothing in production.")
