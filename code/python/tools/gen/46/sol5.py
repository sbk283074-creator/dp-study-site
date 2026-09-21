#!/usr/bin/env python3
"""Chapter 46 solution 5 -- sorting version strings, where a key gets hard."""
import functools

VERSIONS = ["1.9", "1.10", "1.2.3", "1.2", "2.0", "1.10.1", "1.2.10", "1.2.2"]


def numeric_key(text):
    """Split on dots and convert each part to an int. Works for plain
    numeric versions and nothing else."""
    return tuple(int(part) for part in text.split("."))


def compare_numeric(left, right):
    left_parts = numeric_key(left)
    right_parts = numeric_key(right)
    if left_parts < right_parts:
        return -1
    if left_parts > right_parts:
        return 1
    return 0


print(f"versions: {VERSIONS}")
print()
print("sorted() with no key sorts them as text:")
print(f"  {sorted(VERSIONS)}")
print()
print("'1.10' comes before '1.9', because '1' < '9' at the third character.")
print("Every version-comparison bug in every build system starts here.")
print()
print("sorted() with a numeric key:")
print(f"  {sorted(VERSIONS, key=numeric_key)}")
print()
print("Now 1.9 precedes 1.10, which is what the version number means. The")
print("key turns each version into a tuple of ints, and tuple comparison")
print("does the rest -- element by element, and a shorter tuple that is a")
print("prefix of a longer one sorts first.")
print()
print("That last rule is worth seeing, because it is a decision rather than")
print("an accident:")
print()
print(f"  {'1.2':<8} -> {numeric_key('1.2')}")
print(f"  {'1.2.0':<8} -> {numeric_key('1.2.0')}")
print(f"  1.2 sorts before 1.2.0 : {numeric_key('1.2') < numeric_key('1.2.0')}")
print()
print("Whether those two are the same release is a policy question, and the")
print("tuple key has answered it silently in favour of 'different'. If your")
print("policy says they are equal, pad the tuples to the same length first.")
print()
print("cmp_to_key gives the same answer as the key, and costs more:")
print()
print(f"  {sorted(VERSIONS, key=functools.cmp_to_key(compare_numeric))}")
print(f"  agrees with the key version: "
      f"{sorted(VERSIONS, key=functools.cmp_to_key(compare_numeric)) == sorted(VERSIONS, key=numeric_key)}")
print()
print("So far the key has won on every count. Here is where it stops being")
print("easy -- pre-release suffixes:")
print()
RELEASES = ["1.2.3", "1.2.3-rc1", "1.2.3-rc2", "1.2.3-beta", "1.2.4"]
print(f"  {RELEASES}")
try:
    sorted(RELEASES, key=numeric_key)
except ValueError as error:
    print(f"  numeric_key raises: ValueError: {error}")
print()
print("`int('3-rc1')` is not a number. The key can still be written -- it")
print("just has to encode the ordering rule, which for semantic versioning")
print("is 'no suffix outranks any suffix, then compare the suffix text':")
print()


def release_key(text):
    if "-" not in text:
        return (numeric_key(text), 1, "")
    base, suffix = text.split("-", 1)
    return (numeric_key(base), 0, suffix)


print(f"  {sorted(RELEASES, key=release_key)}")
print()
print("That works and it is still a key, so the sort stays single-pass and")
print("the rule stays in one function. cmp_to_key is the escape hatch for the")
print("cases where no such encoding exists -- when the comparison depends on")
print("the pair rather than on each item alone, as in the largest-number")
print("problem earlier in this chapter.")
print()
print("The order to try them in is: a key, then a richer key, then")
print("cmp_to_key. Reaching for cmp_to_key first costs a factor of log n in")
print("calls and gives up the ability to look at one item and say where it")
print("belongs.")
