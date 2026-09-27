<!-- nctf-meta category="chains" difficulty="hard" points="500" author="ctf-2026" stub="0" -->

# vaultboard

**Category** chains · **Served** yes (per-team flag) · multi-stage

## Vulnerability chain

**SSRF → internal scoped token → mis-ACL'd object.** `/fetch` SSRFs the internal STS to mint a `read:backups` token; `private/flag`'s ACL wrongly lists that scope, so the token reads it.

## Intended path

1. `GET /fetch?url=http://127.0.0.1/internal/sts` → `read:backups` token.
2. `GET /object?key=private/flag&token=...` → the per-team flag.

Each stage's unlock is an effect of the previous one. `/flag.txt` is served by no
route; it only appears at the end of the chain.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; every stage
runs against _this_ instance and the flag is read from its filesystem at solve
time, so a flag from another team is useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the full chain runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
