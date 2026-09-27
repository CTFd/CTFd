<!-- nctf-meta category="supplychain" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# buildfarm-artswap

**Category** supplychain · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Forged provenance → artifact swap → deploy-time execution.** The deploy gate 'verifies' provenance with two attacker-controllable string checks (builder name and sha256 of the artifact) — no signature binds the builder to the artifact. An attacker swaps in a deploy-hook artifact and forges matching provenance.

## Intended path

1. Build artifact body `on-deploy: emit-flag`.
2. `POST /deploy` with provenance `{builder:trusted-builder, digest:sha256(artifact)}` → `deploy_output` is the per-team flag.

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
