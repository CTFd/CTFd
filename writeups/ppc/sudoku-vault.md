<!-- nctf-meta category="ppc" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# sudoku-vault

Solve the uniquely-completable Sudoku; the completed grid is the key that
decrypts the flag.

## Technique

`puzzle.txt` has `CIPHER <hex>` and nine rows of nine digits (`0` = empty). The
puzzle was dug from a full valid grid while a solution-counter confirmed it
stayed uniquely solvable, so any correct solver reaches the same completion. The
flag was XOR-encrypted with a SHA-256 keystream seeded by the 81 solution digits
in row-major order.

## Steps

1. Parse the ciphertext and the 9x9 grid.
2. Solve by backtracking; choosing the empty cell with the fewest candidates
   (minimum-remaining-values heuristic) makes it terminate instantly.
3. Flatten the solved grid row-major into an 81-character digit string.
4. Build the keystream from `SHA-256` of that string (re-hash to extend) and XOR
   against the ciphertext.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

Backtracking with MRV solves a unique 9x9 puzzle in microseconds here.

## Flag

`NCTF{…}`
