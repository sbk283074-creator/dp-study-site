#!/usr/bin/env python3
"""Chapter 47 solution 1 -- a word ladder, which is BFS on a graph nobody
built.

The graph is implicit. The nodes are words, two words are joined when they
differ in exactly one letter, and no edge is ever stored. That is the normal
situation rather than the exception: the graph is described by a *rule*, and
materialising it would cost far more than searching it. So the traversal has
to be able to ask a node for its neighbours, and the neighbour function is
where all the cost lives.
"""
from collections import deque

WORDS = {
    "cold", "cord", "card", "ward", "warm", "word", "wood", "wool", "cool",
    "pool", "poll", "pole", "pale", "sale", "sage", "gale", "gall", "wall",
    "well", "weld", "wild", "wind", "wine", "fine", "find", "fond", "fund",
    "bold", "bald", "balm", "calm", "palm", "pall", "fall", "fell", "feel",
    "heel", "heal", "teal", "tell", "tall", "tale", "male", "malt", "halt",
    "half", "hall", "hale", "hole", "home", "hope", "rope", "rose", "rise",
    "wise", "wish", "wash", "cash", "case", "cave", "save", "same", "some",
    "come", "cone", "bone", "born", "burn", "barn", "yarn", "yard", "hard",
    "hare", "care", "cart", "cast", "cost", "coat", "boat", "bolt", "belt",
    "best", "nest", "next", "text", "test", "tent", "rent", "rest", "rust",
    "dust", "dusk", "disk", "dish", "fish", "fist", "fast", "last", "list",
    "lost", "lose", "lone", "lane", "land", "sand", "send", "seed", "seek",
    "week", "weed", "deed", "dead", "dear", "fear", "near", "neat", "seat",
    "seal", "meal", "mean", "mane", "made", "make", "wake", "cake", "came",
    "game", "gate", "late", "lake", "bake", "bark", "dark", "dare", "bare",
    "base", "ease", "easy", "east", "vast", "vest", "west", "pest", "past",
}
LETTERS = "abcdefghijklmnopqrstuvwxyz"
LENGTH = 4
CANDIDATES_PER_WORD = LENGTH * (len(LETTERS) - 1)


def neighbours(word, tally=None):
    """Every word in the dictionary one letter away.

    Note what this costs. For each of the 4 positions it tries all 25 other
    letters, so 100 candidate strings are built and hashed *per word*,
    whether or not any of them is a word. That 100 is the real price of an
    implicit graph, and it is why the tally below counts candidates rather
    than edges.
    """
    for i in range(LENGTH):
        for ch in LETTERS:
            if ch != word[i]:
                if tally is not None:
                    tally[0] += 1
                candidate = word[:i] + ch + word[i + 1:]
                if candidate in WORDS:
                    if tally is not None:
                        tally[1] += 1
                    yield candidate


def ladder(start, goal):
    """BFS over an implicit graph, with both costs counted: candidates built
    (the neighbour function's work) and edges found (the graph's size)."""
    parent = {start: None}
    queue = deque([start])
    tally = [0, 0]
    while queue:
        u = queue.popleft()
        if u == goal:
            break
        for v in neighbours(u, tally):
            if v not in parent:
                parent[v] = u
                queue.append(v)
    if goal not in parent:
        return None, tally, len(parent)
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path, tally, len(parent)


print(f"a dictionary of {len(WORDS)} four-letter words")
print(f"every word has {CANDIDATES_PER_WORD} candidate neighbours to test")
print()
route, tally, visited = ladder("cold", "warm")
print(f"  cold -> warm     : {' -> '.join(route)}")
print(f"  steps            : {len(route) - 1}")
print(f"  words visited    : {visited}")
print(f"  candidates built : {tally[0]:,}")
print(f"  real edges found : {tally[1]:,}")
print(f"  candidates per edge: {tally[0] / tally[1]:.0f}")
print()
print("Every step changes exactly one letter, which is the only constraint the")
print("problem stated. The route is not the one a person would guess -- 'cold,")
print("cord, card, ward, warm' goes through two words that have nothing to do")
print("with temperature -- and it is the shortest one, because BFS has no")
print("opinions about which words are related.")
print()
print("Now the cost, which is the interesting half. The graph was never built,")
print("and the traversal touched only the part of it that mattered. But look")
print("at the ratio: every *edge* the search found cost")
print(f"{tally[0] / tally[1]:.0f} candidate strings built and hashed. The search is cheap")
print("and the neighbour function is not, and on a real dictionary that ratio")
print("is what decides whether this runs in a second or a minute.")
print()
print("The standard fix is to stop generating neighbours and start looking")
print("them up: index the dictionary by wildcard pattern, so that 'c_ld' maps")
print("to every word matching it. Then a word's neighbours are four dictionary")
print("lookups instead of a hundred hash tests, and the implicit graph has")
print("been made explicit exactly where the search touches it. That is the")
print("usual trade -- pay memory to remove a constant factor -- and it is")
print("worth making only because the search visits these words many times.")
print()
print()
print("The same code on a pair with no route")
print()
route, tally, visited = ladder("cold", "zzzz")
print(f"  cold -> zzzz     : {route}")
print(f"  words visited    : {visited} of {len(WORDS)}")
print(f"  candidates built : {tally[0]:,}")
print()
print("The search exhausts the entire connected component of 'cold' and")
print("reports that there is no route -- which is the correct answer, and one")
print("that can only be known by looking. Note that 'no route' and 'the goal")
print("is isolated' are different facts, and this code cannot tell them apart:")
print("both produce the same empty result.")
print()
print(f"  is zzzz reachable from cold? {route is not None}")
print(f"  words one letter from cold : {sorted(neighbours('cold'))}")
print(f"  words one letter from warm : {sorted(neighbours('warm'))}")
