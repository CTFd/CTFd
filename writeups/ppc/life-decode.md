<!-- nctf-meta category="ppc" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# life-decode

Run Conway's Game of Life for the stated number of generations; the final board
is the key that decrypts the flag.

## Technique

`grid.txt` header is `W H GENERATIONS`, followed by `CIPHER <hex>` and `H` rows
of `W` bits (the initial board). The automaton is Conway's Game of Life on a
finite board with dead boundaries (out-of-board neighbours count as 0). The flag
was XOR-encrypted with a SHA-256 keystream seeded by the flattened final board,
so the exact rule, boundary condition, and step count are all required.

## Steps

1. Parse the dimensions, step count, ciphertext, and initial grid.
2. Step `GENERATIONS` times. Each generation, every cell is recomputed from the
   previous generation: a live cell survives with 2 or 3 live neighbours; a dead
   cell becomes live with exactly 3. Neighbours off the board are dead.
3. Flatten the final board row-major into a `'0'/'1'` string.
4. Build the keystream: `SHA-256(bits + counter.to_bytes(4))` for
   `counter = 0, 1, ...`, concatenated, then XOR against the ciphertext.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

`O(GENERATIONS * W * H)` = 120 x 64 x 48 ~ 3.7e5 cell updates — instant.

## Flag

`NCTF{…}`
