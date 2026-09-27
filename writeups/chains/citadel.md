<!-- nctf-meta category="chains" difficulty="hard" points="600" author="ctf-2026" stub="0" -->

# citadel

**Category** chains · **Served** yes (per-team flag) · multi-stage

## Vulnerability chain

**Web foothold → user pivot (reused credential) → root (sudo rule).** The shipped default deploy creds give a foothold; `/home/deploy/.env` leaks a reused svc password; svc has a sudo rule to run flagtool as root.

## Intended path

1. `POST /login {user:deploy, pass:deploy}` → deploy token.
2. `GET /read?path=/home/deploy/.env` (X-Token) → `svc_password`.
3. `POST /su {user:svc, password:...}` → svc token.
4. `GET /sudo?cmd=flagtool` (X-Token) → the per-team flag.

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
