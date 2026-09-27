<!-- nctf-meta category="crypto" difficulty="medium" points="250" author="ctf-2026" stub="0" -->

# notarysvc-kdf

**Category** crypto · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability

**Weak key derivation.** Session tokens are `HMAC_SHA256(K, username)` where the
server key `K = SHA256("nctf-kdf-" + seed)` and `seed` is a 4-digit PIN — a
10 000-key space that is trivially brute-forceable given one known token.

## Intended path

1. `GET /login` → a valid **guest** token (a known `(plaintext, MAC)` pair).
2. For each `seed` in `0000..9999`, derive `K` and check
   `HMAC(K, "guest")` against the observed token → recover `K`.
3. Forge `HMAC(K, "admin")` and `GET /panel?user=admin&token=...` → the per-team
   flag.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact, and the seed
is freshly random per instance. The brute-force must run against _this_
instance's guest token; a recovered key or flag from another team is worthless.

> Variante de la classe `kdf-slip` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the solver recovers the seed from the guest token, forges the admin token,
and reads the exact per-team flag; a non-admin token is refused. **Docker/Lot-5
rehearsal is the remaining gate before `state: visible`.**
