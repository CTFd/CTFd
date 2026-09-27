<!-- nctf-meta category="blockchain" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# replay-signer

**Summary.** Two ECDSA signatures share the same `r`, so the signer reused the
nonce `k`. That leaks the private key with schoolbook algebra; the vault note
is sealed with that key.

**Vuln / technique.** ECDSA nonce reuse on secp256k1. With
`s1 = k^-1 (z1 + r d)` and `s2 = k^-1 (z2 + r d)` sharing `k` and `r`:

```
k = (z1 - z2) / (s1 - s2)   (mod n)
d = (s1 k - z1) / r         (mod n)
```

where `z_i = keccak256(message_i) mod n`. No point arithmetic needed to
recover `d` -- only modular inverses mod the curve order `n`.

**Steps.**

1. Parse `r, s1, s2, message1, message2` from `signatures.json`.
2. Recover `k`, then `d` with the formulas above.
3. Seal key = `keystream(keccak256)` seeded by `d` (32-byte big-endian);
   XOR into `cipher_hex`.

**Flag.** `NCTF{…}`
