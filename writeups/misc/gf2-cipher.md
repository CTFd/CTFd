<!-- nctf-meta category="misc" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# gf2-cipher

Solve a linear system over GF(2); the unique solution is the flag's bits.

## Technique

`system.json` holds an n x n matrix `A` (n = 264) and a length-n bit vector `b`
with `A x = b` over GF(2) — additions are XOR, multiplications are AND. `A` is
built as the product of a unit lower-triangular and a unit upper-triangular
matrix, so it is invertible and the solution `x` is unique. The flag is never
stored directly; only `A` and `b` ship.

Each row of `A` is a hex integer whose bit `j` is column `j`. The solution
vector `x` is the flag's bits, MSB-first within each byte:
`x[8*j + k] = bit (7-k) of byte j`.

## Steps

1. Load the rows as integers and append each `b` bit as an augmented column `n`.
2. Gaussian elimination over GF(2): for each column find a pivot row, then XOR
   it into every other row that has a 1 in that column.
3. Read each column's solution bit from its pivot row's augmented bit.
4. Pack 8 bits per byte (MSB first) and decode as ASCII.

Run `python3 solution/solve.py` (pure standard library).

## Flag

`NCTF{…}`
