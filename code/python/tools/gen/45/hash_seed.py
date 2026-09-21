#!/usr/bin/env python3
"""Chapter 45 demo -- string hashing is salted per process, and why.

Nothing here prints a hash value. Hash values depend on the Python build and
on the seed, so printing them would be a fact about this laptop rather than
a fact about Python. What is printed is the comparison, which is stable.
"""
import os
import subprocess
import sys

PROGRAM = (
    "keys = [f'user{i:04d}' for i in range(50)]\n"
    "layout = [0] * 8\n"
    "for key in keys:\n"
    "    layout[hash(key) % 8] += 1\n"
    "print(','.join(str(n) for n in layout))\n"
)


def layout_under(seed):
    """Run the same program in a fresh interpreter with a chosen seed."""
    env = dict(os.environ, PYTHONHASHSEED=seed)
    result = subprocess.run(
        [sys.executable, "-c", PROGRAM],
        capture_output=True, text=True, env=env, check=True,
    )
    return result.stdout.strip()


print("the same 50 keys, hashed into 8 buckets, in fresh processes")
print()
print(f"{'comparison':<46}{'identical?':>12}")
print("-" * 58)
runs = {seed: [layout_under(seed) for _ in range(2)] for seed in ("0", "1")}
print(f"{'two runs with seed 0':<46}{str(runs['0'][0] == runs['0'][1]):>12}")
print(f"{'two runs with seed 1':<46}{str(runs['1'][0] == runs['1'][1]):>12}")
print(f"{'one run with seed 0, one with seed 1':<46}{str(runs['0'][0] == runs['1'][0]):>12}")
print()
print("The bucket occupancies themselves are deliberately not printed. They")
print("depend on the Python build as well as the seed, so they would be a")
print("fact about this laptop rather than a fact about Python.")
print()
print("Two runs of the identical program, and the keys land in different")
print("buckets. That is hash randomisation: CPython picks a random salt at")
print("startup and mixes it into the hash of every str and bytes object, so")
print("hash values are not reproducible across processes.")
print()
print("Two consequences you will meet.")
print()
print("The harmless one: iterating a set of strings gives a different order")
print("in a different process. `set` iteration order was never a promise, and")
print("this is why the same script can print a different order tomorrow.")
print("dicts are unaffected, because dicts have kept insertion order since")
print("3.7 -- that is a language guarantee, not a hash property.")
print()
print("The one that matters: without the salt, an attacker who knows the")
print("hash function can choose keys that all collide, and a dict lookup")
print("becomes a linear scan. That is hash flooding, and it turns a JSON")
print("request body into a denial of service. The salt is the fix, and it is")
print("on by default. Chapter 52 comes back to this when it covers untrusted")
print("input -- for now the point is just that `hash()` is not a pure")
print("function of its argument.")
