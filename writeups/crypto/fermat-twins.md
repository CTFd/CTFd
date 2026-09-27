<!-- nctf-meta category="crypto" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# fermat-twins

## TL;DR

The RSA primes `p` and `q` are chosen only a few billion apart, so the modulus
falls instantly to Fermat factorization.

## Technique

When `p` and `q` are close, `n = pq` sits just below a perfect square. Fermat's
method writes:

```
n = a^2 - b^2 = (a - b)(a + b)
```

Starting from `a = ceil(sqrt(n))` and incrementing, `a^2 - n` becomes a perfect
square `b^2` after only a handful of steps when `|p - q|` is small. Then
`p = a - b` and `q = a + b`.

## Attack

1. Parse `n` and `e` from `pubkey.pem` and read the hex ciphertext.
2. Fermat-factor `n` into `p` and `q`.
3. Compute `phi = (p-1)(q-1)`, `d = e^{-1} mod phi`, and `m = c^d mod n`.
4. Convert `m` to bytes to read the flag.

## Run

```
python3 solve.py            # defaults to ../pubkey.pem and ../ciphertext.txt
python3 solve.py /path/to/pubkey.pem /path/to/ciphertext.txt
```

Output:

```
[+] |p-q| = 729025913522
[+] FLAG = NCTF{…}
```

## Files

- `../src/gen.py` — deterministic builder (not shipped).
- `../pubkey.pem`, `../ciphertext.txt` — the player handout.
- `solve.py` — this reference solver (Python + pycryptodome).
