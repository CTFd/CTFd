<!-- nctf-meta category="crypto" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# vigenere-drift

## TL;DR

A Vigenere cipher whose shift drifts up by one every full period. The drift is
public, so it can be removed and each key column recovered independently by
chi-squared frequency analysis.

## Technique

For the `n`-th enciphered letter (counting letters only) and base key `K` of
length `L`, the effective shift is:

```
shift(n) = ( K[n mod L] + floor(n / L) ) mod 26
```

The extra `floor(n / L)` term is what defeats naive frequency grouping — within
a single key column the shift is no longer constant. But that term depends only
on `n` and `L`, both public once `L` is guessed. Subtract it and every column is
again a single constant Caesar offset.

## Attack

1. Extract the letter positions from `cipher.txt` (non-letters pass through and
   do not advance the counter).
2. For each candidate key length `L = 1..12` and each column `col`, try all 26
   base offsets. For each offset, decrypt that column's letters (subtracting the
   drift `floor(n / L)`) and score the result with chi-squared against English
   letter frequencies; keep the best offset.
3. Decrypt with the recovered key and check for `NCTF{…}

```

## Files

- `../src/gen.py` — deterministic builder for `cipher.txt` (not shipped).
- `../cipher.txt` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
```
