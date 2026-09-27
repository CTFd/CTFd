<!-- nctf-meta category="supplychain" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# buildfarm-postinstall

**Category** supplychain · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Unauthenticated publish → post-install hook execution.** The registry accepts unsigned, unreviewed package publishes, and the installer runs each package's post-install hook. An attacker publishes a package whose hook is the debug `emit-flag` and installs it.

## Intended path

1. `POST /publish {"name":"pwn-pkg","postinstall":"emit-flag"}`.
2. `GET /install?pkg=pwn-pkg` → `postinstall_output` is the per-team flag.

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
