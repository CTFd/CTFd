<!-- nctf-meta category="crypto" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# affine-relay

## TL;DR

The memo is enciphered with an affine cipher over A–Z. Its key space is tiny
(312 keys), so brute-force every key and keep the decryption containing the
flag.

## Technique

An affine cipher maps each letter `x` (0–25) to `E(x) = (a*x + b) mod 26`, where
`a` must be coprime with 26. Non-letters are passed through unchanged, which is
why the spacing, punctuation, and the `NCTF{…}` braces survive the relay.

There are `phi(26) = 12` legal values of `a` and `26` values of `b`, so only
`12 * 26 = 312` possible keys — trivially exhaustible.

## Attack

1. Read `cipher.txt`.
2. For every valid `a` (with `gcd(a, 26) == 1`) and every `b`, decrypt using the
   inverse map `D(y) = a^{-1} * (y - b) mod 26`.
3. The correct key is the one whose decryption contains the marker `NCTF{…}

```

## Files

- `../src/gen.py` — deterministic builder for `cipher.txt` (not shipped).
- `../cipher.txt` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
```
