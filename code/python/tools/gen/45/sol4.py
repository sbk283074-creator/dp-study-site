#!/usr/bin/env python3
"""Chapter 45 solution 4 -- longest common prefix, which is what a trie is for."""


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children = {}
        self.is_word = False


def build(words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_word = True
    return root


def longest_common_prefix(words):
    """Walk down the trie while there is exactly one way to go and no word
    has ended. Both conditions matter: a word ending here means it is itself
    the common prefix, and two children means the paths have diverged."""
    if not words:
        return ""
    root = build(words)
    prefix = []
    node = root
    while len(node.children) == 1 and not node.is_word:
        char, node = next(iter(node.children.items()))
        prefix.append(char)
    return "".join(prefix)


def longest_common_prefix_by_scan(words):
    """The version everyone writes first. Compare the first word against
    every other word, character by character, and keep the shortest match."""
    if not words:
        return ""
    first = words[0]
    for position, char in enumerate(first):
        for word in words[1:]:
            if position >= len(word) or word[position] != char:
                return first[:position]
    return first


CASES = [
    ["flower", "flow", "flight"],
    ["interview", "internet", "internal"],
    ["dog", "cat", "bird"],
    ["prefix"],
    ["apple", "apple", "apple"],
    ["", "b"],
    ["ab", "abc", "abcd", "abcde"],
]

print("longest common prefix of each set")
print()
print(f"{'words':<44}{'trie':>10}{'scan':>10}  {'agree':>6}")
print("-" * 72)
for words in CASES:
    trie_answer = longest_common_prefix(words)
    scan_answer = longest_common_prefix_by_scan(words)
    shown = str(words)
    if len(shown) > 42:
        shown = shown[:39] + "..."
    print(f"{shown:<44}{trie_answer!r:>10}{scan_answer!r:>10}"
          f"  {str(trie_answer == scan_answer):>6}")
print()
print("The two agree on every case, including the awkward ones: a single")
print("word (the whole word), a set with no shared first character (the empty")
print("string), and repeated words (again the whole word).")
print()
print("The trie wins on cost, not on correctness. The scan compares the first")
print("word against all the others, so it costs up to n * L character")
print("comparisons for n words of length L. The trie costs the length of the")
print("answer, because the answer *is* the path -- it never looks at the")
print("words at all, only at the shape of the tree they built.")
print()
print("There is a second reason to prefer it that has nothing to do with")
print("speed. The scan needs the first word to be the one that defines the")
print("answer; give it a set where the first word is the odd one out and it")
print("returns immediately with an empty string, which happens to be right,")
print("but for the wrong reason. The trie has no such dependence on the input")
print("order, and code that does not depend on input order is code that does")
print("not break when someone sorts the list.")
