<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# tap-code

## TL;DR

Tap code / Polybius square: each two-digit number is `(row, col)` in a
5x5 letter grid (K shares C's cell).

## Steps

1. Split on double spaces to get words, single spaces for letters.
2. `44 11 35` -> `T A P`, etc. Message: `TAP CODE POLYBIUS`.
3. Lowercase and join words with underscores inside `NCTF{…}`.

Run `python3 solve.py`.

## Flag

`NCTF{…}`
