<!-- nctf-meta category="crypto" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# keystream-reuse

## TL;DR

All 25 ciphertexts reuse one keystream (a many-time pad). Recover the keystream
column by column with the classic "space XOR letter is a letter" heuristic, then
XOR it back to read the flag.

## Technique

Because the same keystream `k` is reused:

```
c_i XOR c_j = (m_i XOR k) XOR (m_j XOR k) = m_i XOR m_j
```

The key cancels. In English text a space (0x20) XORed with a letter yields that
letter with its case flipped — still an ASCII letter. So for a given column, the
ciphertext byte that produces the most ASCII letters when XORed against every
other ciphertext in that column is very likely encrypting a space. That byte
gives the keystream: `k = c XOR 0x20`.

## Attack

1. Read all ciphertexts (hex lines).
2. For each column, score every present ciphertext byte by how many other
   ciphertexts in that column give an ASCII letter (or zero) when XORed with it.
   The highest scorer is the space; set `key[col] = byte XOR 0x20`.
3. XOR the recovered keystream into every ciphertext and search the plaintexts
   for `NCTF{…}`.

The flag message is placed in the middle columns, which — with 25 messages —
carry enough space signal to be recovered exactly.

## Run

```
python3 solve.py            # defaults to ../messages.txt
python3 solve.py /path/to/messages.txt
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../src/gen.py` — deterministic builder (not shipped).
- `../messages.txt` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
