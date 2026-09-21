#!/usr/bin/env python3
"""Chapter 47 demo -- union-find, and the two one-line tricks that turn it
from quadratic into almost linear.

Union-find answers one question -- "are these two in the same group?" -- and
takes one instruction: "merge these two groups". It beats a traversal because
it never rebuilds the groups, and it is fast for a reason worth counting:
two independent tricks, each of which is a single line, and each of which
fixes a different failure.
"""


class UnionFind:
    def __init__(self, n, compress=True, by_rank=True):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.compress = compress
        self.by_rank = by_rank
        self.hops = 0

    def find(self, x):
        """Walk to the root, counting the steps. That count *is* the cost."""
        root = x
        while self.parent[root] != root:
            self.hops += 1
            root = self.parent[root]
        if self.compress:
            while self.parent[x] != root:
                self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.by_rank and self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.by_rank and self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


N = 2_000


def chain_then_query(compress, by_rank):
    """The sequence that separates the four variants.

    `union(i + 1, i)` is deliberate. `union(a, b)` hangs the root of `b` under
    the root of `a`, so merging *forwards* builds a chain one link at a time --
    and merging backwards would attach every new node to the same root and
    build a star of depth 1, which is the opposite of the worst case.
    """
    uf = UnionFind(N, compress=compress, by_rank=by_rank)
    for i in range(N - 1):
        uf.union(i + 1, i)
    uf.hops = 0
    for i in range(N):
        uf.find(0)
    return uf.hops


print(f"{N:,} elements, merged into one chain, then {N:,} finds of the far end")
print()
print(f"{'variant':<34}{'parent hops':>13}{'per find':>11}")
print("-" * 58)
variants = [
    ("no compression, no union by rank", False, False),
    ("union by rank only", False, True),
    ("path compression only", True, False),
    ("both", True, True),
]
counts = {}
for name, compress, by_rank in variants:
    hops = chain_then_query(compress, by_rank)
    counts[name] = hops
    print(f"{name:<34}{hops:>13,}{hops / N:>11.1f}")
print()
worst = counts["no compression, no union by rank"]
best = counts["both"]
print(f"  the naive version costs {worst / best:,.0f}x the full version")
print()
print("The naive version is quadratic, and the arithmetic is easy to see: the")
print("chain has length n, and asking for the root of the far end walks the")
print("whole chain. Do that n times and you have n(n-1) hops -- which is what")
print("the first row shows, to the digit. That is why the first implementation")
print("anybody writes is unusable on real data.")
print()
print("The two fixes address two different things, which is why they stack.")
print()
print("Union by rank decides *which* root becomes the child. Always hanging")
print("the second tree under the first is what builds a chain; hanging the")
print("smaller under the larger keeps the depth logarithmic. It costs one")
print("comparison and one extra array, and it is the trick that makes the")
print("worst case provably shallow.")
print()
print("Path compression changes the tree while you are walking it. Every node")
print("on the way to the root is re-pointed directly at the root, so the")
print("second find on the same path is one step. It costs a few assignments")
print("and it is the trick that makes repeated queries almost free.")
print()
print("Together they give the result that makes union-find worth knowing: the")
print("amortised cost per operation is effectively constant -- the inverse of")
print("the Ackermann function, which is below 5 for any input that fits in the")
print("universe. Not 'log n'. Effectively 1.")
print()
print("The order to reach for them is worth noting. Path compression alone is")
print("usually enough, and it is the one you get for free in any implementation")
print("that re-points while walking. Union by rank is the one that bounds the")
print("*first* query, which matters when you build the structure once and query")
print("it a handful of times.")
print()
print()
print("Part 2 -- the question it answers that a traversal cannot")
print()
rng_state = 12345


def next_random(state, limit):
    """A tiny linear congruential generator, so the demo is the same on every
    machine and every Python."""
    state = (1103515245 * state + 12345) % (2 ** 31)
    return state, state % limit


state = rng_state
pairs = []
for _ in range(6):
    state, a = next_random(state, N)
    state, b = next_random(state, N)
    pairs.append((a, b))
uf = UnionFind(N, compress=True, by_rank=True)
for i in range(0, 200, 2):
    uf.union(i, i + 1)
print(f"  merged {100} pairs, from a universe of {N:,}")
print()
print(f"  {'pair':>18}{'same group?':>14}")
print("  " + "-" * 32)
for a, b in pairs:
    print(f"  {f'{a:>7} {b:>7}':>18}{str(uf.find(a) == uf.find(b)):>14}")
print()
print("A traversal can answer this too -- flood fill, then check the labels --")
print("but it has to be redone from scratch every time an edge is added. Union")
print("find absorbs the additions and answers queries incrementally, which is")
print("the difference between a structure and a computation.")
print()
print("That is what makes it the right tool for Kruskal's minimum spanning")
print("tree: sort the edges, then walk them cheapest first, merging groups as")
print("you go and skipping any edge whose two ends are already joined. The")
print("cycle test -- 'would this edge close a loop?' -- is exactly 'are these")
print("two already in the same group?', which is one find each.")
print()
print(f"  the two ends of a merged pair, always same group: "
      f"{all(uf.find(i) == uf.find(i + 1) for i in range(0, 200, 2))}")
