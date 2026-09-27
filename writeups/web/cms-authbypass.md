<!-- nctf-meta category="web" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# cms-authbypass

**Category** web · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability chain

**Broken access control → IDOR → mass-assignment.** The admin API is "protected"
by a **client-supplied header** (`X-Account-Role: admin`) — the server trusts a
value the client controls. `/api/users/<id>` (GET) is an IDOR, and the update
endpoint mass-assigns every field in the body (including `role`) once past that
header gate. `/flag` checks the real server-side session role, so you must
actually promote your own account.

## Intended path

1. `GET /register?user=solver&pass=x` → `token`, `uid`.
2. `POST /api/users/<uid>` with header `X-Account-Role: admin` and body
   `{"role":"admin"}` → the forged header bypasses authz, mass-assignment sets
   your role.
3. `GET /flag?token=<token>` → the per-team flag.

Without the forged header the update returns 403; without an admin session
`/flag` returns 403.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact. The promotion
must be performed against _this_ instance's session; a flag from another team is
useless. The chain rewards recognising that authorization is decided from a
forgeable header.

> Variante de la classe `forum-authbypass` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the forged header + mass-assignment promotes the account and `/flag`
returns the exact per-team flag; the update 403s without the header. **Docker/
Lot-5 rehearsal is the remaining gate before `state: visible`.**
