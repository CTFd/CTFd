<!-- nctf-meta category="web" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# cms-smuggle

**Category** web · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Request smuggling (CL/TE desync) → cache poisoning → auth bypass.** The ingest parser treats a trailing `SMUGGLED GET <path>` line as a second, pipelined request processed with internal trust, and caches its response — so a smuggled `GET /admin/flag` poisons the cache with the admin response.

## Intended path

1. `POST /ingest` with a body line `SMUGGLED GET /admin/flag`.
2. `GET /page?p=/admin/flag` → `cached` is the per-team flag.

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
