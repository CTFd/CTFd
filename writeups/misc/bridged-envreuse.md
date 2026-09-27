<!-- nctf-meta category="misc" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# bridged-envreuse

**Category** misc · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Env leak → secret reuse → signed-command execution.** `/debug/env` dumps `WORKER_HMAC_SECRET`, the key the task runner uses to authorise commands. With it an attacker signs any command; `emit-flag` reads the secret.

## Intended path

1. `GET /debug/env` → `WORKER_HMAC_SECRET`.
2. Compute `sig = HMAC(secret, "emit-flag")`, `POST /task {cmd:emit-flag, sig}` → the per-team flag.

`/flag.txt` is served by no route; it only appears through the exploit above.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the exploit
reads _this_ instance's secret at solve time, so a flag from another team is
useless.

> Variante de la classe `ingestd-envreuse` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the exploit path runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
