<!-- nctf-meta category="ppc" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# congruence-vault

Solve every linear congruence for its unique `x`; the whole batch of solutions
is the key that decrypts the flag.

## Technique

`system.txt` begins with `CIPHER <hex>`, then 160 lines `a b m` meaning
`a * x ≡ b (mod m)`. Each `m` is prime and `1 <= a < m`, so `gcd(a, m) = 1` and
`x = b * a^(-1) mod m` is the unique solution in `[0, m)`. The flag was
XOR-encrypted with a SHA-256 keystream seeded by all the solutions, so every
single congruence must be solved correctly.

## Steps

1. Parse the ciphertext and the 160 triples.
2. For each, compute the modular inverse of `a` mod `m` (extended Euclid, or
   `pow(a, -1, m)` in Python 3.8+) and set `x = (b * inv) % m`.
3. Join the solutions as comma-separated decimal, `SHA-256` it, extend by
   re-hashing until you have enough bytes.
4. XOR the keystream against the ciphertext.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

`O(count * log m)` for the inverses — instant.

## Flag

`NCTF{…}`
