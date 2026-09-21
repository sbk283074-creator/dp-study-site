#!/usr/bin/env python3
"""Chapter 47 solution 5 -- two colours, one traversal, and a surprising
number of real problems.

"Can these be split into two groups so that no two conflicting things end up
together?" is exactly "is this graph bipartite?", and a BFS that colours as it
goes answers it in a single pass. The traversal is the same one from earlier
in the chapter. The only addition is an array of colours -- and the realisation
that a conflict is not a property of the nodes at all.
"""
from collections import deque

CYCLE_4 = {
    "a": ["b", "d"],
    "b": ["a", "c"],
    "c": ["b", "d"],
    "d": ["a", "c"],
}

CYCLE_5 = {
    "a": ["b", "e"],
    "b": ["a", "c"],
    "c": ["b", "d"],
    "d": ["c", "e"],
    "e": ["d", "a"],
}

COURSES = {
    "maths": ["physics", "stats"],
    "physics": ["maths", "chem"],
    "chem": ["physics", "bio"],
    "bio": ["chem"],
    "stats": ["maths", "cs"],
    "cs": ["stats"],
}


def two_colour(adj):
    """BFS from every unvisited node, colouring each neighbour the opposite of
    its parent. Returns the colouring, or the edge that makes it impossible."""
    colour = {}
    for start in adj:
        if start in colour:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in colour:
                    colour[v] = 1 - colour[u]
                    queue.append(v)
                elif colour[v] == colour[u]:
                    return None, (u, v)
    return colour, None


def show(adj, label):
    colour, clash = two_colour(adj)
    print(f"  {label}")
    if colour is None:
        print(f"    not bipartite -- the edge {clash[0]}-{clash[1]} "
              f"joins two nodes of the same colour")
        return
    groups = {0: [], 1: []}
    for node, c in colour.items():
        groups[c].append(node)
    print(f"    bipartite, in one pass")
    print(f"    group A: {', '.join(sorted(groups[0]))}")
    print(f"    group B: {', '.join(sorted(groups[1]))}")


print("Part 1 -- what the traversal is looking for")
print()
show(CYCLE_4, "a four-cycle")
print()
show(CYCLE_5, "a five-cycle")
print()
print("An even cycle alternates colours all the way round and closes cleanly.")
print("An odd cycle does not: walking round it flips the colour five times,")
print("so the last node is forced to be the same colour as the first -- and")
print("the edge that closes the loop then joins two nodes that must differ.")
print()
print("That is the whole theory, and it is worth stating as one line: a graph")
print("is bipartite if and only if it contains no odd cycle. The traversal")
print("finds this by *doing* it -- it tries to colour the graph, and the")
print("attempt fails at exactly the edge that cannot be satisfied.")
print()
print("The failure report is the useful part. 'Not bipartite' tells you")
print("nothing; the edge tells you which pair of things you have to separate")
print("by some other means.")
print()
print()
print("Part 2 -- the same question with consequences")
print()
print("  six courses, where two courses are joined if a student takes both")
print()
for course, clashes in COURSES.items():
    print(f"    {course:<8} shares a student with: {', '.join(clashes)}")
print()
show(COURSES, "can these be examined in two slots?")
print()
print("Two exam slots, no student in two places at once -- that is a two")
print("colouring, and it works. Group A sits in the morning and group B in")
print("the afternoon, and no student has two exams in the same slot.")
print()
print("Notice what the graph is. The nodes are courses and the edges are")
print("*conflicts*, which is the opposite of the graphs earlier in this")
print("chapter: there, an edge meant 'connected' and we looked for paths")
print("through it. Here an edge means 'must not be together' and we look for")
print("a way to avoid it. The traversal is identical; only the reading of an")
print("edge changed.")
print()
print("That reframing is what makes the technique portable. 'Can I do this in")
print("two rounds?' is bipartiteness whenever the constraint is pairwise and")
print("binary -- two teams, two machines, two shifts, two colours, black and")
print("white. And when the answer is no, the odd cycle is the *proof*: it is a")
print("concrete set of things that cannot be split, and you can hand it to")
print("somebody instead of an assertion.")
print()
print()
print("Part 3 -- and when two is not enough")
print()
TRIANGLE = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}
show(TRIANGLE, "three mutually conflicting courses")
print()
print("Three courses, every pair in conflict: two slots cannot work, and no")
print("colouring will make them. That is not a failure of the traversal -- it")
print("is the answer, and the edge it reports is the proof. The general")
print("question ('how many slots?') is graph colouring, which is hard, and")
print("the two-colour case is the one special case that is easy.")
print()
print("Knowing where the easy case stops is most of the value. Bipartiteness")
print("is one BFS. Three colours is NP-hard. The gap between them is not a")
print("gap in effort; it is a gap in what is known to be possible.")
print()
print(f"  the four-cycle is bipartite : {two_colour(CYCLE_4)[0] is not None}")
print(f"  the five-cycle is bipartite : {two_colour(CYCLE_5)[0] is not None}")
print(f"  the courses are bipartite   : {two_colour(COURSES)[0] is not None}")
print(f"  the triangle is bipartite   : {two_colour(TRIANGLE)[0] is not None}")
