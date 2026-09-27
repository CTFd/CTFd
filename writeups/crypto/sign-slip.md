<!-- nctf-meta category="crypto" difficulty="hard" points="450" author="ctf-2026" stub="0" -->

# sign-slip

**Category** crypto · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Keyless checksum posing as a signature → forgeable token.** The token's `sig` is a plain CRC32 of the role — no secret — so any role's signature is trivially computable. Forge an admin token.

## Intended path

1. `GET /login` shows the token format `role=user;sig=<crc32>`.
2. Compute `crc32("admin")`, present `X-Token: role=admin;sig=<that>` to `GET /admin/flag` → the per-team flag.

`/flag.txt` is served by no route; it only appears through the exploit above.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the exploit
reads _this_ instance's secret at solve time, so a flag from another team is
useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the exploit path runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
