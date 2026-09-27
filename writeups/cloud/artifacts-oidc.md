<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="ctf-2026" stub="0" -->

# artifacts-oidc

**Category** cloud · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability

**`alg=none` acceptance** in an OIDC resource server. The ID-token validator
honours the token header's `alg`; when it is `none` it treats the token as
unsigned and accepts it with no signature check. Any claims can then be forged.

## Intended path

1. Forge an unsigned ID token: header `{"alg":"none"}`, claims
   `{"sub":"attacker","groups":["platform-admin"]}` (a JWT with an empty third
   segment).
2. `GET /admin/flag` with `Authorization: Bearer <token>` → the per-team flag.

The HS256 signing secret is never needed — the server skips verification when
`alg=none`.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact. The token is
crafted and presented to _this_ instance; a flag from another team's instance is
useless. Recognising the alg:none misconfig is the whole point.

> Variante de la classe `oidc-forge` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the forged alg=none admin token yields the exact per-team flag; a normal
HS256 guest token has no admin group and is refused (403). **Docker/Lot-5
rehearsal is the remaining gate before `state: visible`.**
