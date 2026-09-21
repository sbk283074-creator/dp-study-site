#!/usr/bin/env python3
"""Chapter 45 demo -- a trie, and the one job it does that a dict cannot.

A dict answers 'is this exact key present'. A trie answers 'which keys start
with this prefix', because the shared prefix is shared *storage* rather than
something you have to search for.
"""
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def vocabulary():
    """2,028 distinct three-letter words: the first two letters run over the
    whole alphabet, the third over just a, b and c."""
    words = []
    for first in LETTERS:
        for second in LETTERS:
            for third in LETTERS[:3]:
                words.append(first + second + third)
    return words


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
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
    return root


def count_nodes(root):
    total = 0
    stack = [root]
    while stack:
        total += 1
        stack.extend(stack.pop().children.values())
    return total


def trie_prefix(root, prefix):
    """Walk the prefix, then collect the subtree. Returns (words, visits)."""
    visits = 0
    node = root
    for char in prefix:
        visits += 1
        node = node.children.get(char)
        if node is None:
            return [], visits
    found = []
    stack = [(prefix, node)]
    while stack:
        text, current = stack.pop()
        visits += 1
        if current.is_word:
            found.append(text)
        for char, child in current.children.items():
            stack.append((text + char, child))
    found.sort()
    return found, visits


def scan_prefix(words, prefix):
    """The obvious version: check every word. Counts character comparisons,
    because that is the work, and startswith hides it in C."""
    comparisons = 0
    found = []
    for word in words:
        matched = True
        for index, char in enumerate(prefix):
            comparisons += 1
            if index >= len(word) or word[index] != char:
                matched = False
                break
        if matched:
            found.append(word)
    return found, comparisons


WORDS = vocabulary()
ROOT = build(WORDS)

print(f"a trie over {len(WORDS):,} words")
print()
print(f"{'nodes in the trie':<32}{count_nodes(ROOT):>10,}")
print(f"{'words stored':<32}{len(WORDS):>10,}")
print(f"{'nodes per word':<32}{count_nodes(ROOT) / len(WORDS):>10.2f}")
print()
print("The prefix is stored once. Every word beginning with 'ab' shares the")
print("same two nodes, which is why the node count is 2,731 rather than")
print("three nodes per word.")
print()
print("the same query, asked two ways")
print()
print(f"{'prefix':>8}{'matches':>10}{'trie visits':>14}{'scan comparisons':>18}")
print("-" * 52)
for prefix in ("ab", "xyz", "q", "abc", "zz"):
    trie_words, visits = trie_prefix(ROOT, prefix)
    scan_words, comparisons = scan_prefix(WORDS, prefix)
    assert trie_words == scan_words, prefix
    print(f"{prefix:>8}{len(trie_words):>10}{visits:>14,}{comparisons:>18,}")
print()
print("Both columns find the same words. The scan pays for every word in the")
print("vocabulary; the trie pays for the prefix plus the answers. Watch what")
print("happens to each column as the prefix gets longer and the answer set")
print("gets smaller -- the trie's cost falls with the answer, and the scan's")
print("does not.")
print()
print("That is the property a dict cannot offer. `{'ab': [...]}` would answer")
print("this query in one hash, and would then be wrong the moment the")
print("vocabulary grows, because every prefix has to be enumerated in")
print("advance. A trie derives the answer from the words themselves.")
print()
print("The cost is memory and nothing else. A dict of 2,028 words holds")
print("2,028 keys; this trie holds 2,731 node objects, each with a dict of")
print("its own. For an autocomplete over a million words that is hundreds of")
print("megabytes, and the production answer is a compressed trie or a")
print("sorted array with two bisects -- which is exactly the trade this")
print("chapter keeps making: the fastest structure for the query you have,")
print("at the memory cost you are willing to pay.")
