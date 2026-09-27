<!-- nctf-meta category="blockchain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# overflow-mint

**Summary.** Solidity 0.7.x does no overflow checks. `n * price` wraps modulo
2\*\*256, so a gigantic token count can be bought for a few wei.

**Vuln / technique.** Unchecked integer overflow in `buy(n)`. With
`price = 2**252 + 1`, choosing `n = 16` gives
`n * price = 2**256 + 16`, which wraps to just `16` wei -- affordable within
the tiny `budget`, while crediting 16 tokens... but the win threshold logic
keys the vault on that exact `n`.

**Steps.**

1. Read `price` and `budget_wei` from `sale.json`.
2. Find the smallest `n > 0` with `(n * price) mod 2**256 <= budget` and
   `n * price >= 2**256` (i.e. it truly overflowed). That is `n = 16`.
3. The vault ciphertext is XORed with `keystream(keccak256)` seeded by `n`
   (32-byte big-endian). Rebuild the keystream and XOR `cipher_hex`.

**Flag.** `NCTF{…}`
