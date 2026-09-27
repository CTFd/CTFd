<!-- nctf-meta category="crypto" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# notarysvc-signext

**Category** crypto · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability

**Hash length-extension.** The MAC is `SHA256(secret || msg)` (a raw prefix-MAC,
not HMAC). From one valid `(msg, sig)` an attacker can compute the MAC of
`msg || glue-padding || suffix` without knowing the secret, because SHA-256's
final state after `secret || msg || padding` _is_ `sig`. The `/sign` endpoint
refuses privileged commands, so the grant must be forged this way.

## Intended path

1. `GET /sign?cmd=ls` → a benign `(msg, sig)`.
2. For each candidate secret length `k` (unknown, brute-forced):
   - compute the SHA-256 glue padding for `len(secret)+len(msg)`;
   - resume SHA-256 from `sig` and hash the suffix `&op=grantflag` to get the
     forged MAC.
3. `GET /api?msg=<msg+glue+suffix>&sig=<forged>` — the right `k` validates and
   the message ends with the privileged suffix → the per-team flag.

## Reference solver

The solver includes a compact SHA-256 that resumes from a digest state (the
length-extension core), and brute-forces the secret length 1..64.

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the secret is
freshly random per instance and its length varies, so the forge must be computed
against _this_ instance's `(msg, sig)`. Recognising a prefix-MAC and implementing
the extension is the whole challenge.

> Variante de la classe `sealbox-signext` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the forged MAC validates and yields the exact per-team flag; `/sign`
refuses `op`/`grantflag` (403) and `/api` rejects bad signatures (401).
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
