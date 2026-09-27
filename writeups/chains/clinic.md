<!-- nctf-meta category="chains" difficulty="hard" points="450" author="ctf-2026" stub="0" -->

# clinic

**Category** chains · **Served** yes (per-team flag) · multi-stage

## Vulnerability chain

**Predictable session id → IDOR export → admin action.** Session ids are sequential and the admin is id 1; `/export` has no ownership check (IDOR) and leaks the admin API key that drives the admin rotation.

## Intended path

1. `POST /login {user:guest}` → note the sid is sequential.
2. `GET /export?sid=1` → admin `api_key`.
3. `POST /admin/rotate {key}` → the per-team flag.

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
