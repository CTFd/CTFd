<!-- nctf-meta category="crypto" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# modulus-siblings

## TL;DR

The same message is encrypted under one modulus with two coprime exponents. The
RSA common-modulus attack recovers it without factoring `n`.

## Technique

Given `c1 = m^e1 mod n` and `c2 = m^e2 mod n` with `gcd(e1, e2) = 1`, the
extended Euclidean algorithm yields integers `a, b` such that:

```
a*e1 + b*e2 = 1
```

Therefore:

```
c1^a * c2^b = m^(a*e1 + b*e2) = m^1 = m   (mod n)
```

One of `a, b` is negative; replace the corresponding ciphertext with its modular
inverse mod `n` and negate the exponent.

## Attack

1. Read `n`, `e1`, `e2`, `c1`, `c2` from `transcript.json`.
2. Run extended Euclid on `e1, e2` to get `a, b`.
3. Compute `m = c1^a * c2^b mod n` (inverting for negative exponents).
4. Convert `m` to bytes to read the flag.

## Run

```
python3 solve.py            # defaults to ../transcript.json
python3 solve.py /path/to/transcript.json
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../src/gen.py` — deterministic builder (not shipped).
- `../transcript.json` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
