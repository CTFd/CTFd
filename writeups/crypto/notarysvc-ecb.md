<!-- nctf-meta category="crypto" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# notarysvc-ecb

**Category** crypto · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability

AES-**ECB cut-and-paste**. Session tokens are `ECB(key, "name=<name>&role=user")`.
ECB encrypts each 16-byte block independently, so blocks can be rearranged and a
block whose plaintext you control can be reused elsewhere.

## Intended path

Block size 16; layout `name=<name>&role=user`.

1. Request a token with `name = "A"*11 + "admin" + \x0b*11`. The prefix `name=`
   (5) + 11 `A`s fills block 0, so **block 1 = `admin` + PKCS#7 padding** — grab
   its ciphertext `C_admin`.
2. Request a token with `name = "AAAAA"`: block 0 = `name=AAAAA&role=`, block 1 =
   `user` + padding.
3. Splice: `block0(from step 2) || C_admin` decrypts to `name=AAAAA&role=admin`.
4. `GET /flag?token=...` → the per-team flag.

No key is recovered — only ECB's block independence is abused.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact, key freshly
random per instance. The two crafted tokens must be requested from _this_
instance and spliced against _its_ ciphertext; nothing transfers between teams.

> Variante de la classe `sealbox-ecb` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the spliced token decrypts to `role=admin` and yields the exact per-team
flag; a normal user token gets 403. **Docker/Lot-5 rehearsal is the remaining
gate before `state: visible`.**
