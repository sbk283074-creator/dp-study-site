#!/usr/bin/env python3
"""Chapter 47 demo -- the two ways to store a graph, and what each one costs.

A graph is just a set of edges. How you store it decides which question is
cheap: "are u and v joined?" or "who is u joined to?". Those two questions
have different answers, and the gap between them is a factor of n.

Both costs below are exact counts -- slots allocated and slots probed -- so
nothing here depends on the machine.
"""
import random

N = 300
TARGET_EDGES = 900


def build_edges(n, target, seed=0):
    """A connected graph: a ring, plus random chords until it has enough
    edges. The ring guarantees connectivity, so no query is trivially
    uninteresting."""
    rng = random.Random(seed)
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    while len(edges) < target:
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    return sorted(edges)


def as_matrix(n, edges):
    """n^2 slots, whether or not the edges exist. One read answers any
    pair question -- including for a pair that is not joined."""
    matrix = [[False] * n for _ in range(n)]
    for u, v in edges:
        matrix[u][v] = True
        matrix[v][u] = True
    return matrix


def as_lists(n, edges):
    """One slot per *edge end*. Answering "are u and v joined?" means
    walking u's list until it is found or exhausted."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def list_probes(adj, u, v):
    probes = 0
    for w in adj[u]:
        probes += 1
        if w == v:
            break
    return probes


def who_is_u_joined_to(adj, matrix, u):
    """The other question, counted both ways."""
    return len(adj[u]), len(matrix[u])


EDGES = build_edges(N, TARGET_EDGES)
MATRIX = as_matrix(N, EDGES)
ADJ = as_lists(N, EDGES)
M = len(EDGES)

print(f"a connected graph: {N:,} nodes, {M:,} edges, mean degree "
      f"{2 * M / N:.1f}")
print()
print("storage")
print()
print(f"{'representation':<20}{'slots':>14}{'slots per edge':>17}")
print("-" * 51)
print(f"{'adjacency matrix':<20}{N * N:>14,}{N * N / M:>17.1f}")
print(f"{'adjacency lists':<20}{2 * M:>14,}{2 * M / M:>17.1f}")
print()
print(f"  the matrix needs {N * N / (2 * M):.0f}x the slots for the same graph")
print()
print("The matrix is the same size whether the graph has 900 edges or")
print("90,000, because it allocates a slot for every pair that *could*")
print("exist. The list allocates a slot for every edge that *does*. On a")
print("sparse graph -- and almost every graph that models something real is")
print("sparse -- that is the whole argument.")
print()
print()
print("cost of asking 'are u and v joined?', over every ordered pair")
print()


def count_pair_probes(matrix, adj, n):
    """Exact totals over all n^2 ordered pairs, both representations."""
    matrix_total = 0
    list_total = 0
    list_found = 0
    for u in range(n):
        for v in range(n):
            matrix_total += 1
            probes = list_probes(adj, u, v)
            list_total += probes
            if probes and adj[u][probes - 1] == v:
                list_found += 1
    return matrix_total, list_total, list_found


matrix_total, list_total, list_found = count_pair_probes(MATRIX, ADJ, N)
print(f"{'representation':<20}{'total probes':>14}{'per query':>12}"
      f"{'worst case':>13}")
print("-" * 59)
print(f"{'adjacency matrix':<20}{matrix_total:>14,}{matrix_total / N ** 2:>12.2f}"
      f"{1:>13,}")
print(f"{'adjacency lists':<20}{list_total:>14,}{list_total / N ** 2:>12.2f}"
      f"{max(len(a) for a in ADJ):>13,}")
print()
print("One read either way, for a pair that is joined -- the matrix wins")
print("nothing there. The gap is in the *other* case. When the edge is")
print("absent, the matrix still answers in one read, and the list has to")
print("walk the whole neighbour list before it can say no. That is why the")
print("list column averages well above 1 and the matrix column is exactly")
print("1.00.")
print()
print()
print("cost of asking 'who is u joined to?', over every node")
print()
matrix_scan = sum(who_is_u_joined_to(ADJ, MATRIX, u)[1] for u in range(N))
list_scan = sum(who_is_u_joined_to(ADJ, MATRIX, u)[0] for u in range(N))
print(f"{'representation':<20}{'total probes':>14}{'per node':>12}")
print("-" * 46)
print(f"{'adjacency matrix':<20}{matrix_scan:>14,}{matrix_scan / N:>12.1f}")
print(f"{'adjacency lists':<20}{list_scan:>14,}{list_scan / N:>12.1f}")
print()
print("And now it reverses completely. Listing a node's neighbours means")
print("scanning all n slots of its matrix row and discarding the empty ones;")
print("the list *is* the answer, and iterating it touches nothing else. Any")
print("algorithm whose inner loop is 'for each neighbour of u' -- which is")
print("every traversal in this chapter -- is paying the matrix's cost on")
print("every single step.")
print()
print("So the rule is not 'lists are better'. It is that the matrix buys")
print("constant-time *pair* queries by paying n^2 memory and n per neighbour")
print("scan, and a dense graph is the only thing that makes that trade good.")
print()
print(f"  pairs that are joined      : {list_found:,}")
print(f"  density                    : {2 * M / (N * (N - 1)):.4f}")
print(f"  matrix slots per real edge : {N * N / M:.0f}")
