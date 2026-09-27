<!-- nctf-meta category="supplychain" difficulty="medium" points="550" author="ctf-2026" stub="0" -->

# buildfarm-depconf

**Category** supplychain · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Dependency confusion → build-hook execution.** `internal-lib` is pinned to the private registry at 1.0.0, but the resolver also queries a public registry and picks whichever version is higher. Publishing `internal-lib` publicly at a higher version wins, and its build hook runs.

## Intended path

1. `POST /publish-public {"name":"internal-lib","version":"99.0.0","buildhook":"emit-flag"}`.
2. `GET /resolve?name=internal-lib` → source `public`, `build` is the per-team flag.

`/flag.txt` is served by no route; it only appears as the output of the hook the
attacker triggered.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the hook reads the flag from _this_ instance's filesystem at solve time, so a flag from another team is useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the exploit path runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
