<!-- nctf-meta category="crypto" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# ecb-echo

## TL;DR

The tapped service encrypts `AES-ECB(your_input || SECRET)`. ECB is
deterministic per block, so the secret leaks one byte at a time. The shipped
`oracle_log.json` is a raw, unlabelled transcript — nothing points at the
answer — so you must actually run the byte-at-a-time recovery against it.

## Technique

In ECB mode each 16-byte block is encrypted independently, so equal plaintext
blocks give equal ciphertext blocks. Because the secret is appended to attacker
input, you can push the next unknown secret byte to the end of a block by
sending `16 - 1 - (i mod 16)` filler bytes. That block then encrypts
`filler || known_secret_prefix || <one unknown byte>`. Comparing it against the
same block built from `filler || known_secret_prefix || guess` for each possible
`guess` reveals the byte when the ciphertext blocks match.

## Log format

- `probe`: ciphertext hex for input `"A"*k`, `k = 0..32`. The block size is the
  amount the ciphertext length jumps by as filler grows.
- `queries`: `SHA256(attacker_input) -> ciphertext_hex`. The transcript is keyed
  by a fingerprint of the input, not the input itself, so no secret plaintext is
  present and the map cannot be grepped or reversed. To use an entry you must
  reconstruct the exact attacker input and hash it.

## Attack

1. From `probe`, confirm the block size is 16 by finding where the ciphertext
   length jumps.
2. For secret byte `i`: build `filler = "A"*(15 - (i mod 16))`, look up its
   ciphertext by `SHA256(filler)`, and take block `i//16` as the target.
3. For each printable `guess`, look up `SHA256(filler || recovered || guess)`,
   take the same block, and compare to the target. The match is the byte.
4. Append it to `recovered` and repeat. Each query key depends on the bytes
   already recovered, so the recovery must be done in order. Stop when the
   aligned filler query is absent (the whole secret is recovered).

## Run

```
python3 solve.py            # defaults to ../oracle_log.json
python3 solve.py /path/to/oracle_log.json
```

Output:

```
[+] block size = 16
[+] recovered 51 bytes
[+] FLAG = NCTF{…}
```

## Files

- `../src/gen.py` — deterministic builder for the oracle log (not shipped).
- `../oracle_log.json` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
