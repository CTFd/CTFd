<!-- nctf-meta category="sysadmin" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# auditd-cron

**Category** sysadmin · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Writable-PATH cron misconfig → root command execution.** Root's cron resolves `backup` through a PATH whose first directory (`/opt/tools`) is world-writable. A dropped `backup` there runs as root.

## Intended path

1. `GET /drop?name=backup&action=emit-flag` (writes into /opt/tools).
2. `GET /run-cron` → resolves /opt/tools/backup, output is the per-team flag.

`/flag.txt` is root-owned and served by no route; only the privilege escalation
above reaches it.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the read
targets _this_ instance's root-only file, so a flag from another team is useless.

> Variante de la classe `schedd-cron` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the escalation runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
