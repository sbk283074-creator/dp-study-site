"""Chapter 38 -- two ways to key an anagram, and the size of the key they make.

Ten base words and their rotations, keyed two ways. The count is of groups found,
of characters each key is made of, and of the base words that turn out to be
anagrams of each other.
"""

LETTERS = "abcdefghijklmnopqrstuvwxyz"

# Ten base words. Two of them -- danger and garden -- are anagrams of each other,
# which the count below finds rather than the author.
BASES = [
    "listen", "master", "rescue", "danger", "elbow",
    "cinema", "forest", "garden", "hunter", "island",
]


def rotations(word):
    """One rotation per letter, which are all anagrams of each other."""
    return [word[index:] + word[:index] for index in range(len(word))]


WORDS = []
for base in BASES:
    WORDS.extend(rotations(base))


def sorted_key(word):
    return "".join(sorted(word))


def counted_key(word):
    """A slot per letter, as a string of digits."""
    return "".join(str(word.count(letter)) for letter in LETTERS)


def group(words, key):
    groups = {}
    for word in words:
        groups.setdefault(key(word), []).append(word)
    return groups


def partition(groups):
    """The grouping itself, independent of how the key was spelled."""
    return sorted(sorted(members) for members in groups.values())


by_sorted = group(WORDS, sorted_key)
by_counted = group(WORDS, counted_key)

sorted_chars = sum(len(sorted_key(word)) for word in WORDS)
counted_chars = sum(len(counted_key(word)) for word in WORDS)
colliding = [base for base in BASES
             if sum(1 for other in BASES if sorted_key(other) == sorted_key(base)) > 1]

print(f"{len(WORDS)} words from {len(BASES)} base words")
print()
print(f"{'key':<18}{'groups found':>14}{'characters of key':>19}")
print("-" * 51)
print(f"{'sorted letters':<18}{len(by_sorted):>14}{sorted_chars:>19}")
print(f"{'letter counts':<18}{len(by_counted):>14}{counted_chars:>19}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'words':<46}{len(WORDS):>8}")
print(f"{'base words':<46}{len(BASES):>8}")
print(f"{'base words that are anagrams of each other':<46}"
      f"{len(colliding):>8}")
print(f"{'groups the sorted key finds':<46}{len(by_sorted):>8}")
print(f"{'groups the counted key finds':<46}{len(by_counted):>8}")
print(f"{'the two keys group the words identically':<46}"
      f"{int(partition(by_sorted) == partition(by_counted)):>8}")
print(f"{'characters of key, sorted':<46}{sorted_chars:>8}")
print(f"{'characters of key, counted':<46}{counted_chars:>8}")
print(f"{'times larger the counted key is':<46}"
      f"{counted_chars // sorted_chars:>8}")

print()
print(f"The first thing the table does is catch a mistake in the list above it.")
print(f"There are {len(BASES)} base words and both keys find {len(by_sorted)} groups, because")
print(f"{' and '.join(colliding)} are anagrams of each other -- which is obvious once it is")
print("counted and invisible when the list is read as ten separate ideas. Two")
print("groups of rotations are one group of words.")
print()
print(f"The second thing is that both keys agree. That check has to compare the")
print("groupings rather than the key strings: a sorted word and a tally of letters")
print("are never equal to each other, so comparing the keys directly would report")
print("a disagreement between two methods that group identically.")
print()
print(f"Then the trade. The sorted key is one character per letter, so {sorted_chars}")
print(f"characters for the whole list; the counted key is {len(LETTERS)} slots whatever the")
print(f"word is, so {counted_chars} characters -- {counted_chars // sorted_chars} times as much, for the same")
print("answer. Sorting is the more expensive operation and the smaller key;")
print("counting is linear and the bigger one.")
print()
print("Which wins depends on what you are keying. For words of six or seven")
print("letters the sort is nothing, and the smaller key is also the one a human")
print("can read in a debugger -- worth more than the asymptotics at this size. The")
print("counted key is the right answer for long strings, or when the same key is")
print("built and compared millions of times. The habit is to measure the thing you")
print("are actually trading: here, the same groups and a key four times bigger.")
