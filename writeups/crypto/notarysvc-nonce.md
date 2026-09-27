<!-- nctf-meta category="crypto" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# notarysvc-nonce

**Category** crypto · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability

ECDSA **nonce reuse** (secp256k1). The signing oracle uses the same nonce `k`
for every signature, so any two signatures share the same `r` and leak the
private key.

The oracle refuses to sign any message containing `admin`, so the privileged
command cannot be signed directly — you must recover the key and forge it.

## Intended path

1. `GET /sign?msg=alpha` and `GET /sign?msg=bravo` → two signatures `(r, s1)`,
   `(r, s2)` with the **same `r`** (shared nonce).
2. Recover the nonce: `k = (z1 - z2) / (s1 - s2) mod n`, with
   `z = SHA256(msg) mod n`.
3. Recover the private key: `d = (s1·k - z1) / r mod n`.
4. Sign the admin command (`role=admin;grant=flag`, published at `/`) with `d`
   and any fresh nonce, then `GET /flag?msg=...&r=...&s=...` → the per-team flag.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact, and the key is
freshly random per instance — a flag or key from one team is useless to another.
The solver must actually recover _this_ instance's `d` from _its_ signatures.

> Variante de la classe `nonce-climb` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the solver recovers the private key from two reused-nonce signatures,
forges the admin signature, and reads the exact per-team flag; `/sign` refuses
admin messages (403) and `/flag` rejects bad signatures (401). **Docker/Lot-5
rehearsal is the remaining gate before `state: visible`.**
