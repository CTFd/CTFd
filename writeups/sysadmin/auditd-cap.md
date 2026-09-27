<!-- nctf-meta category="sysadmin" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# auditd-cap

**Category** sysadmin · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Over-broad capability → arbitrary file read.** A helper (`logtool`) ships with `cap_dac_read_search`, which bypasses file permissions. Its `--read` reads the root-only flag.

## Intended path

1. `GET /bins` → `logtool` has `cap_dac_read_search`.
2. `GET /exec?bin=logtool&args=--read=/flag.txt` → the per-team flag.

`/flag.txt` is root-owned and served by no route; only the privilege escalation
above reaches it.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the read
targets _this_ instance's root-only file, so a flag from another team is useless.

> Variante de la classe `schedd-cap` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the escalation runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
