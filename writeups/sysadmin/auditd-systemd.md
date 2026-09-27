<!-- nctf-meta category="sysadmin" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# auditd-systemd

**Category** sysadmin · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Env injection into a root unit → sudo/dev flag → secret dump.** `backup.service` (User=root) runs `backup-helper $BACKUP_ARGS` and reads an env drop-in with no allow-list. Injecting `BACKUP_ARGS=--dump-secrets` makes the root helper dump the secret.

## Intended path

1. `GET /unit` → helper usage lists `--dump-secrets`.
2. `POST /set-env {key:BACKUP_ARGS, value:--dump-secrets}` then `GET /start` → the per-team flag.

`/flag.txt` is root-owned and served by no route; only the privilege escalation
above reaches it.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the read
targets _this_ instance's root-only file, so a flag from another team is useless.

> Variante de la classe `schedd-systemd` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the escalation runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
