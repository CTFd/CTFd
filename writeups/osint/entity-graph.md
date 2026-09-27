<!-- nctf-meta category="osint" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# entity-graph

**Category:** osint · **Difficulty:** easy
**Flag:** `NCTF{…}`

## Summary

A Maltego-style investigation graph is shipped as two CSVs. Pivoting from the
seed persona along verified links only reaches exactly one real identity. The
flag is **not** written in the graph — it is derived from the verified pivot
path, so you have to actually traverse the graph to produce it.

## Technique

Link analysis / graph pivoting with edge-trust filtering, then a keyed HMAC over
the recovered path. The trap is that the graph mixes analyst-confirmed edges
with speculative ones. Following speculative edges (`mentions`, `follows`,
`similar_name`) reaches decoy `person` nodes, including a decoy flag
`NCTF{…}` stored verbatim in `nodes.csv` — grepping
for `NCTF{…}`. Any speculative detour changes
the reachable set / path and yields the wrong digest.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
