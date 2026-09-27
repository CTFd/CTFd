<!-- nctf-meta category="ppc" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# z-locator

Every occurrence of the pattern in the text is followed by one flag character;
concatenating them in order gives the flag.

## Technique

`data.txt` line 1 is a distinctive pattern (`Qx7#zZ`), line 2 is a large text
built from random lowercase filler with the pattern inserted `len(flag)` times,
each followed by one flag byte. The intended matcher is the Z-function, though
KMP or any linear/near-linear exact matcher works.

## Steps

1. Read the pattern `P` and text `T`.
2. Build `S = P + "\x01" + T` and compute its Z-array.
3. For each index `i` into the `T` portion where `Z[i] == len(P)`, the pattern
   matches at that spot; take the character of `T` at `match_end` (the index
   just past the match).
4. Concatenate those characters in increasing position order.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

`O(|P| + |T|)` for the Z-function over the ~26 KB input.

## Flag

`NCTF{…}`
