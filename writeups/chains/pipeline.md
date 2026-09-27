<!-- nctf-meta category="chains" difficulty="hard" points="550" author="ctf-2026" stub="0" -->

# pipeline

**Category** chains · **Served** yes (per-team flag) · multi-stage

## Vulnerability chain

**Dependency confusion → build hook → runner RCE.** `/build` resolves the highest version across the private lockfile and a public registry; a higher public `internal-lib` wins and its build hook installs a runner action that `/run` executes.

## Intended path

1. `POST /publish-public {name:internal-lib, version:99.0.0, buildhook:install-runner:emit-flag}`.
2. `POST /build {name:internal-lib}` → runner installed.
3. `POST /run` → the per-team flag.

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
