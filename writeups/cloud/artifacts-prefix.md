<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="ctf-2026" stub="0" -->

# artifacts-prefix

**Category** cloud · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability chain

**Public prefix → leaked credential → assume-role → private object.** The
`public/` prefix is world-listable and one public object
(`public/backup-notes.txt`) leaks a deploy credential committed by mistake. That
credential assumes the `backup-restore` role, which reads the private flag object.

## Intended path

1. `GET /list?prefix=public/` → object keys.
2. `GET /get?key=public/backup-notes.txt` → contains `deploy_secret=AKIA...`.
3. `GET /assume?secret=<deploy_secret>` → a role `token`.
4. `GET /get?key=private/flag` with `X-Role-Token: <token>` → the per-team flag.

`private/*` is not listable and the flag object 403s without the role token.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the leaked
credential and role token are freshly random per instance. The chain must be run
against _this_ instance — a credential or flag from another team is useless.

> Variante de la classe `backup-prefix` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): listing the public prefix leaks the credential, which assumes the role and
reads the exact per-team flag; `private/flag` returns 403 without the role token.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
