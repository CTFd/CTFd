<!-- nctf-meta category="ppc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# dijkstra-relay

The unique shortest path from source to target passes through nodes whose label
characters spell the flag.

## Technique

`graph.txt` gives, in order: `N M` (nodes, edges), then `src dst`, then `N`
lines `L <node> <char>`, then `M` lines `E <u> <v> <w>`. The graph has a
"spine" of weight-1 edges from the source to the target; every other edge has
weight >= 500, so the spine is the strictly unique shortest path. Its node
labels, in path order, are the flag.

## Steps

1. Parse labels into an array and edges into an adjacency list.
2. Run Dijkstra from `src` with a binary heap, storing a predecessor per node.
3. Once `dst` is settled, walk predecessors back to `src` and reverse.
4. Concatenate the label of each node on the path.

Run `python3 solution/solve.py` (pure standard library, uses `heapq`).

## Complexity

`O((N + M) log N)` — trivial for ~150 nodes and ~1200 edges.

## Flag

`NCTF{…}`
