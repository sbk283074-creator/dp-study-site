---
chapter: 47
part: 8
title: Graphs
summary: A graph is a set of edges and a decision about how to store them. Traverse it in rings or in paths, order it, weigh it, and search it -- BFS, DFS, topological sort, Dijkstra, A*, union-find -- with every cost counted rather than timed.
minutes: 110
tags: [graphs, BFS, DFS, topological sort, Dijkstra, A*, union-find, complexity, pathfinding]
---

Chapter 45 gave you the containers and Chapter 46 the sorting. This chapter is where they stop being
exercises and start being the shape of the problem.

A graph is the most general data structure there is. A tree is a graph. A list is a graph. A
dependency file, a road network, a social network, a game map, a state space, and the call graph of
your own program are all graphs, and they are all the same object: a set of things, and a set of
pairs of things that are related.

That generality is the difficulty. There is no single graph algorithm, because there is no single
graph question -- and the questions in this chapter look so similar that choosing the wrong one
produces a confident, plausible, wrong answer with no exception raised. That is the theme, and it
runs through every section: **a wrong shortest path looks exactly like a right one**.

Two things keep it honest. The first is that Chapter 35 already built A\*, so by the end of this
chapter you will be able to see that the enemy pathfinding there was graph search with a heuristic,
rather than a technique that arrived from nowhere. The second is the counting discipline from
Chapters 44 to 46: every cost below is an exact count of probes, expansions, relaxations or hops,
and not one of them is a stopwatch reading.

## The two ways to store a graph

Everything in this chapter is a decision about representation, so start with the representation
itself. There are two, they are both obvious, and the trade between them is a factor of the number
of nodes.

<<BLOCK:adjacency>>

The matrix allocates a slot for every pair that *could* be joined; the list allocates one per edge
that *is*. On this graph that is 90,000 slots against 1,800 -- a factor of fifty -- and the ratio
gets worse as the graph gets sparser, which is the direction every graph that models something real
goes.

But the matrix is not a mistake, and the second table is why. Asking "are these two joined?" costs
exactly one read in a matrix, whether or not the edge exists. In a list it costs an average of 5.94
reads, because an absent edge means walking the whole neighbour list before you can say no.

The third table is the one that decides it for this chapter. Every traversal here has "for each
neighbour of u" in its inner loop, and that costs 300 probes per node in a matrix against 6 in a
list. Since the inner loop runs once per node, the matrix is paying its n² price on every step of
every algorithm. Use a matrix when the graph is dense, or when the question is a pair query; use
lists for everything else.

## Breadth-first search

BFS explores in rings, and that single fact gives it three things at once.

<<BLOCK:graph_bfs>>

Read the small graph carefully, because three separate outputs come out of one traversal and it is
worth keeping them apart. The visit *order* is what BFS is doing. The *level* of each node is the
answer to "how far away is this?", and it is the shortest distance in edges, because BFS cannot
reach a node at level 3 before it has finished level 2. And the *parent* map is what turns a distance
into an actual route -- recorded at the moment each node was first discovered, which is by definition
the moment it was discovered by a shortest route.

Nothing extra was computed for the parent map. That is the point of it: the information was already
there in the traversal, and writing it down is what makes BFS a pathfinder rather than a visitor.

The grid is the same code answering a question with a right answer. The route is 400 steps against a
straight-line distance of 398, so the walls forced a detour of exactly 2 -- and BFS found the
shortest possible detour without ever considering the straight line, the goal's position, or
anything at all about where it was going. It expanded 28,405 of the 28,790 open cells to do it.

That is BFS's strength and its weakness in one number. Expanding equally in every direction is what
makes it provably correct on an unweighted graph, and it is also why reaching a corner cost it
almost the entire grid. The second half of this chapter is about paying less, and about what that
costs.

## Depth-first search

DFS is the traversal you get for free from a recursive function: visit a node, then visit each of its
neighbours in turn. It is shorter than BFS, it answers different questions, and it has two traps.

<<BLOCK:graph_dfs>>

The first trap is in the first table. Both stack versions visit every node exactly once, so both are
legitimate depth-first traversals -- and only one of them is *the same* traversal as the recursive
version. A stack returns the last thing you put in; recursive DFS recurses into the *first*
neighbour. So the naive rewrite pops the last neighbour instead, and reversing the push order
cancels that out exactly.

This matters more than it looks, because algorithms get built on the order. A topological sort reads
the *finish* order. A finish order that depends on which way the stack was filled is a different
answer -- sometimes still valid, and not the one you proved correct.

The second trap is that DFS follows a path to its end before backing up. On a chain of 5,000 nodes
the recursive version does not run out of memory, it runs out of *call frames*, and the default
limit stops it at a depth of 998. The fix is not to raise the limit: a raised limit is a bigger
number with the same failure mode, and CPython's stack can overflow for real -- a segfault rather
than an exception -- before the counter stops you. Rewrite the traversal with an explicit stack.

The third table is the part that does not match the folklore, and it is worth reading twice. The
textbook claim is "BFS holds the frontier, DFS holds the path, so DFS uses less memory". The middle
row is the version almost everybody writes, and it holds **more** than BFS does -- 4,297 entries
against a frontier of 142.

The reason is the marking, not the traversal. That version marks a node as visited when it is
*popped*, so a node with three unvisited neighbours is queued three times before any of them is
examined. Those duplicates are never traversed -- the `if u in seen: continue` at the top throws them
away -- but they are in the list, and the list is the memory. Marking on push removes them, and the
stack really does hold the current path plus the siblings still to try.

The transferable rule is about the marking: decide when a node counts as visited, and decide it as
early as you can. Every duplicate in that stack was work you paid for and threw away.

## The same graph, two questions

"Find a route from A to B" has two meanings, and the two traversals answer different ones.

<<BLOCK:bfs_vs_dfs>>

Both reach the goal. BFS arrives in 78 steps, which is exactly the straight-line distance. DFS
arrives in 380 steps -- 302 more than the shortest route -- and it is not a bug. It is precisely what
"follow the first unexplored neighbour and do not reconsider" means, and on this grid DFS looked at
*fewer* cells, because it committed early and got lucky.

That is why the choice of traversal is a choice about the question and not about speed. If the edge
count matters, it is BFS and only BFS. DFS is for questions where the *order* is the answer -- is
this connected, does it contain a cycle, in what order must these run -- and it says nothing useful
about distance.

## Ordering a graph

A topological order is an ordering in which every edge points forwards. It exists if and only if the
graph has no cycle, which makes topological sorting the standard way to *detect* a cycle in a
dependency graph -- and the reason a build system can tell you that two modules depend on each other
instead of looping until it runs out of memory.

<<BLOCK:topo_sort>>

The two algorithms disagree about the order, and both are right. A topological order is not unique:
"algebra before physics" is a constraint, and whether statistics comes before or after physics is
specified by nothing. Only the *relative* order of an edge's two endpoints is pinned, which is what
the validity check tests and the only thing a topological sort promises.

Both are O(V + E) -- every node is enqueued once and every edge examined once, which is why the probe
counts match the edge count exactly. Kahn's algorithm spends O(V) memory on an in-degree table; DFS
spends it on the recursion stack, which is where the previous section's recursion limit comes back.

Then the cycle, and this is the case that makes the whole technique worth knowing. Kahn's algorithm
does not hang and does not raise. It runs out of nodes with no prerequisites and stops -- and a
directed graph is acyclic if and only if a topological sort consumes all of it. Everything left over
is on a cycle or downstream of one.

## Weighted graphs: Dijkstra

Dijkstra is BFS with a priority queue instead of a queue. That one change is what lets it handle
weights, and it is also where all the cost goes.

<<BLOCK:dijkstra>>

Every distance in that first table is final the moment it is popped, and that is Dijkstra's actual
claim: the next node out of the heap is the nearest node not yet settled. The heap is not an
optimisation of the search, it *is* the search.

The stale pops are the price of the interface. A binary heap has no "decrease this key" operation,
so when a shorter route to a node is found, a second entry is pushed and the first is recognised as
obsolete by comparing its distance with the best known. That is why there are more pushes than there
are nodes -- 2,004 pushes for 1,600 nodes -- and why 405 entries were thrown away after being
popped.

The second table is the argument for the heap, and it has an edge case worth knowing. The heap's work
is proportional to the *edges*; the array's nearest-node scan is proportional to the *nodes squared*,
because finding the nearest unfinished node means looking at all of them every time, whether or not
any of them has changed. That is 2,560,000 scans against 2,005 pops.

But on a *dense* graph the edge count approaches n², so both are n² and the heap's log factor makes
it worse. The heap wins on sparse graphs -- which is what a road network, a dependency tree and a
social graph all are.

## The fewest steps and the cheapest route

BFS minimises the number of edges. Dijkstra minimises the sum of the weights. On an unweighted graph
those are the same question -- which is exactly why BFS is a special case of Dijkstra -- and on a
weighted graph they are not.

<<BLOCK:dijkstra_vs_bfs>>

BFS is not confused. It was asked for the route with the fewest edges and it returned the route with
the fewest edges. The mistake is in the question: on a road network nobody wants fewer roads, they
want fewer miles. The two-edge route costs 6 and the three-edge route costs 3, so the answer that
looks worse is twice as good.

The second table is what that costs at scale. 98.6% of the nodes are reached by a route that is
longer than it needs to be, the total excess across the grid is 120,594, and the worst single node is
reached by a route costing 194 more than the cheapest one.

And notice what BFS did *not* do. It never raised, never warned, and produced a route that is
genuinely the fewest-edges route. A wrong shortest path is a list of nodes that starts at the source,
ends at the target, and has every consecutive pair genuinely joined by an edge. The only way to
catch it is to know which question you asked.

## The assumption Dijkstra is standing on

Dijkstra settles a node when it comes out of the heap, and the correctness proof says that is safe
*because every edge weight is non-negative*. Remove that and the algorithm still runs, still
terminates, and returns a wrong answer.

<<BLOCK:negative_edges>>

The true cheapest route to T costs 1, and Dijkstra returns 2. A came out of the heap at distance 1
and was declared final; by the time B had been settled it was too late to revise A. The negative edge
was discovered *after* the node it improves had been frozen.

That is the whole content of the assumption. Dijkstra's greedy step says "the nearest unsettled node
is final", and the proof is: any other route to it would have to leave through a node that is already
settled, and every edge adds a non-negative amount, so no detour can be cheaper. A negative edge
makes a detour cheaper, and the argument collapses.

Bellman-Ford makes no such assumption, pays for it with V-1 rounds over every edge, and gets the
negative-cycle test for free. A negative cycle means there is no shortest path at all -- you can go
round the loop again and pay less, forever -- and "the shortest distance is not a number" is a
question you want answered before you trust a route, a price, or a schedule.

## A\*: Dijkstra with an opinion

Dijkstra expands in rings because it has no idea where the target is. A\* adds a heuristic -- an
estimate of the remaining distance -- to the priority, and the search leans towards the goal.

<<BLOCK:astar>>

Read the second row first, because it is the one that does not match the textbook. An admissible
heuristic, correct code, an optimal route -- and 1.3 times fewer cells expanded than Dijkstra. All
that work for almost nothing.

The reason is ties. `f = g + h` is the estimated total cost of a route through a cell, and near the
optimum *every* cell on every good route has the same `f` -- that is what "good route" means. So the
heap is full of cells with identical priority, and something has to decide between them. Pushing
`(f, g, cell)` decides in favour of the smallest `g`, and the smallest `g` is the cell nearest the
start, so the search expands outwards in rings -- which is precisely what Dijkstra did. The
heuristic is in the arithmetic and absent from the behaviour.

Change one thing -- on an equal `f`, let the *largest* `g` come out first -- and the search dives
towards the goal. The expansions collapse from 2,389 to 294, an 8.1-fold saving, with the same
heuristic, the same proof, and the same optimal route.

:::tip Tie-breaking is not a detail in A\*
Every description of A\* is about the arithmetic, and this is about the queue -- which is why it is
invisible in the literature and decisive in practice. The cheap version is to prefer the deeper node;
the usual refinement is to break ties by the cross-product of the direction to the goal and the
direction to the neighbour, which prefers a straight line over a staircase. Either way, if your A\*
"works but is slow", the heuristic is probably fine and the tie-break is not.
:::

Then the other half of the contract, which is about correctness rather than speed. Multiplying the
estimate by three makes the search even more focused -- 144 cells, the fewest of the four -- and the
route it returns is 16 steps longer than the best one. Manhattan distance is exactly the true
remaining cost on an open four-directional grid, so tripling it overstates every route, and A\*
abandons a route it knows is good in favour of one that merely looks good.

That is the admissibility condition: `h(n)` must never exceed the true remaining cost. It is the price
of the speedup, and it is a property of a function *you* wrote, not of the algorithm. Dijkstra needs
no such promise because it has no heuristic to be wrong about.

## Connected components

Before the harder questions, the simplest one a traversal can answer: how many separate pieces is
this made of? It is the first thing worth asking about any graph you did not build yourself.

<<BLOCK:components>>

The two traversals produce exactly the same partition, and that is not a coincidence -- it is the
definition of a connected component. Two cells are in the same component if some path joins them, and
that is a property of the map; the order in which a traversal discovers them cannot change it. So
this is the one question in the chapter whose answer does not depend on *how* you traversed, and the
code can be the simplest version of the traversal with no loss at all.

The second half is the same idea on a graph with no geometry, and the answer is a fact about random
graphs rather than about the code: with a mean degree of 3, one component swallows 93% of the graph,
and 24 of the nodes are isolated -- reachable from nothing and leading nowhere. The practical version
of the question is asked constantly -- is this network still one network, which accounts are
unreachable, does this migration leave anything stranded -- and a component of size 1 is a node that
can never talk to anything.

## Union-find

A traversal answers "are these two in the same group?" by flood-filling, which means redoing the work
from scratch every time an edge is added. Union-find absorbs the additions and answers incrementally,
and it is fast for a reason worth counting: two independent tricks, each of which is a single line.

<<BLOCK:union_find>>

The naive version is quadratic and the arithmetic is easy to see. The chain has length n, asking for
the root of the far end walks the whole chain, and doing that n times is n(n-1) hops -- which is what
the first row shows, to the digit.

The two fixes address two different things, which is why they stack. **Union by rank** decides which
root becomes the child: always hanging the second tree under the first is what builds the chain, and
hanging the smaller under the larger keeps the depth logarithmic. **Path compression** changes the
tree while you are walking it, re-pointing every node on the path directly at the root, so the second
query on that path is one step.

Together they give the result that makes union-find worth knowing: the amortised cost per operation
is effectively constant -- the inverse of the Ackermann function, which is below 5 for any input that
fits in the universe. Not "log n". Effectively 1.

:::pitfall `union(a, b)` hangs `b` under `a`, and that is what makes the worst case
The order of the two arguments is not cosmetic. Merging *forwards* along a chain builds a chain one
link at a time; merging backwards attaches every new node to the same root and builds a star of depth
1, which is the best case rather than the worst. A benchmark that measures the wrong direction will
report that union-find is fine without either optimisation, and it will be measuring the wrong thing.
:::

## Choosing, on evidence

One requirement, several implementations, and a failure that is reported two ways.

:::scenario The deploy that could not be ordered
A deployment pipeline has services that must start after the things they depend on. That is a
topological sort, and it fails in exactly one situation. Here is the version that ships:

```python
started = []
while True:
    for name, needs in services.items():
        if name not in started and all(n in started for n in needs):
            started.append(name)
```

It re-scans every service on every round, so it is O(V²) where the topological sort is O(V + E) --
and worse, it has no way to say *why* it stopped. It knows only that nothing happened.

Here is the same failure, reported both ways:

<<BLOCK:scenario>>
:::

:::solution The rule
A traversal that reports *whether* something failed is a different tool from one that reports
*where* -- and the second one usually costs the same, because the information was already there.
Kahn's algorithm was holding the answer in the stuck set; the DFS was holding it in the grey path. A
node is grey while it is on the current path and black once it is finished, and meeting a grey node
means an edge has closed a loop.

Neither required any extra bookkeeping. Only the decision to look.
:::

## Key takeaways

- A graph is a set of edges and a decision about how to store them. An adjacency matrix costs n²
  slots and answers pair queries in one read; adjacency lists cost 2m slots and make "for each
  neighbour" free. Every traversal in this chapter has that inner loop, so the list is usually right.
- BFS explores in rings, and one traversal gives you the visit order, the shortest distance in edges,
  and a parent map that reconstructs the route. Nothing extra is computed for the parent map.
- DFS is the traversal a recursive function gives you for free, and the obvious iterative rewrite is
  *not* the same traversal. Push the neighbours in reverse and the order matches.
- DFS exhausts the call stack on a deep graph. Rewrite it with an explicit stack rather than raising
  the recursion limit -- a raised limit has the same failure mode, and the real failure is a segfault.
- "BFS holds the frontier, DFS holds the path" is about the shape of the memory, not its size. Mark a
  node visited when you *push* it, or the stack fills with duplicates -- 4,297 entries against a
  frontier of 142.
- A topological sort exists if and only if the graph is acyclic, so a failed sort is a cycle test. The
  nodes it could not place are on a cycle or downstream of one; a DFS with colours names the cycle.
- Dijkstra is BFS with a heap. It is correct only on non-negative weights, and it fails silently: a
  wrong shortest path is a valid list of nodes.
- BFS minimises edges and Dijkstra minimises weight. On a weighted graph BFS is wrong for 98.6% of
  the nodes, and nothing about the output says so.
- A heuristic must never overstate the true remaining cost, or A\* returns a suboptimal route. That is
  a property of a function you wrote, not of the algorithm.
- In A\*, breaking ties towards the goal is worth more than the heuristic: 2,389 expansions become 294
  with the same admissible estimate and the same optimal route.
- Connected components are the one question whose answer does not depend on the traversal, so the
  simplest traversal is the right one.
- Union-find answers "same group?" incrementally. Union by rank bounds the depth and path compression
  flattens the tree; together they make the amortised cost effectively constant.

## Practice

- [ ] Write a word ladder: BFS over an implicit graph where two four-letter words are joined when
  they differ in one letter. Count the candidate strings built, and explain why the neighbour
  function is where the cost is.
- [ ] Implement bidirectional BFS and compare the nodes expanded against plain BFS on a graph that
  branches. Explain why the saving is a square root rather than a factor, and why the same demo on a
  square grid shows almost nothing.
- [ ] Build a minimum spanning tree two ways -- Kruskal with union-find, Prim with a heap -- and check
  that both give the same total weight. Report the longest edge in the tree and say what that number
  means.
- [ ] Cross a grid where you may break at most k walls. Model the state as `(cell, walls_broken)` and
  solve it with plain BFS, then measure the blow-up in the state space as k grows.
- [ ] Decide whether a set of courses can be examined in two slots, using a two-colouring. When the
  answer is no, report the edge or the odd cycle that proves it rather than the word "no".

## Solutions

:::solution Exercise 1
The graph is never built. The traversal asks a node for its neighbours and the neighbour function
does 100 candidate tests per word, so the search is cheap and the neighbour function is not -- which
is the standard reason to make an implicit graph explicit where the search touches it often.

<<BLOCK:sol1>>
:::

:::solution Exercise 2
One search grows a ball of radius d; two grow balls of radius d/2, and a ball of radius r on a graph
that branches b ways holds about b^r nodes. Halving r square-roots the work. The stopping rule has to
be proved -- and it needs the graph to be unweighted for the proof to hold.

<<BLOCK:sol2>>
:::

:::solution Exercise 3
Sort the edges, walk them cheapest first, and keep an edge unless its two ends are already connected.
"Already connected" is one union-find query, which is the whole reason the structure exists.

<<BLOCK:sol3>>
:::

:::solution Exercise 4
Put the extra information into the node and the problem stops being special. The search does not
change -- only the graph it runs on -- and the price is `cells * (budget + 1)`.

<<BLOCK:sol4>>
:::

:::solution Exercise 5
Colour each neighbour the opposite of its parent. An odd cycle forces the last node to match the
first, and the edge that closes the loop is the proof you hand to somebody instead of an assertion.

<<BLOCK:sol5>>
:::
