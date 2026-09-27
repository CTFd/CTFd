<!-- nctf-meta category="sysadmin" difficulty="hard" points="450" author="ctf-2026" stub="0" -->

# secret-slip

**Category** sysadmin · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**State leak → nonce reuse → rotation hijack.** `/status` leaks the secret `pending_nonce` that authorises the next admin-key rotation. Rotating with it mints and returns a fresh admin token, which reads the flag.

## Intended path

1. `GET /status` → `pending_nonce`.
2. `POST /rotate {nonce}` → `admin_token`.
3. `GET /admin/flag` with `X-Admin-Token` → the per-team flag.

`/flag.txt` is root-owned and served by no route; only the privilege escalation
above reaches it.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the read
targets _this_ instance's root-only file, so a flag from another team is useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the escalation runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
