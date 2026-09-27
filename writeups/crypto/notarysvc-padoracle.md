<!-- nctf-meta category="crypto" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# notarysvc-padoracle

**Category** crypto · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability

AES-CBC **padding oracle**. `/whoami` decrypts the session cookie and returns a
distinct error (HTTP 400) on a PKCS#7 padding failure versus a valid decrypt
(200). That single bit of leakage is enough to decrypt — or, here, to _forge_ —
ciphertext without the key.

## Intended path (CBC-R forge)

The goal is a cookie that decrypts to exactly `role=admin`.

1. Pick an arbitrary ciphertext block `C`.
2. Use the oracle to recover `C`'s intermediate state `I = AES_dec(key, C)`,
   byte by byte (the classic padding-oracle block decryption).
3. Set `IV = I XOR pad("role=admin")`. Then `IV || C` decrypts to
   `AES_dec(C) XOR IV = I XOR IV = pad("role=admin")`.
4. `GET /flag?cookie=IV||C` → the per-team flag.

No key is ever recovered; the oracle alone lets us choose the plaintext.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact, key freshly
random per instance. The forge must be carried out against _this_ instance's
oracle (256×16 queries for one block); a cookie forged for one team is invalid
for another.

> Variante de la classe `oracle-cascade` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the solver forges an admin cookie purely from the padding oracle and reads
the exact per-team flag; a normal user cookie gets 403 at `/flag`. **Docker/Lot-5
rehearsal is the remaining gate before `state: visible`.**
