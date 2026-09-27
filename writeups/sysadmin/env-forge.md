<!-- nctf-meta category="sysadmin" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# env-forge

## TL;DR

A committed `.env` leaks the HS256 signing secret. The admin flag is derived
from that same secret, so it can be recomputed offline with no running service.

## The misconfiguration

`docker-compose.yml` loads `.env`, which contains `APP_JWT_SECRET`. Committing a
secret-bearing `.env` is the classic "secret in the repo" mistake. The shipped
`app/session.py` shows the secret does double duty:

- it signs and verifies session JWTs (HS256), and
- it derives the admin flag:

```python
body = HMAC_SHA256(APP_JWT_SECRET, b"nctf:admin-flag:v1").hexdigest()[:12]
flag = "NCTF{…}"
```

Once the key is public, both forging an admin token and recomputing the flag are
trivial.

## Attack

1. Read `APP_JWT_SECRET` from `.env` (`dev-jwt-secret-change-me-before-prod`).
2. (Optional, to prove the auth bypass) forge an HS256 JWT with
   `iss=kekeli-internal` and `role=admin` signed with the secret — `verify()`
   accepts it.
3. Recompute the flag body as `HMAC_SHA256(secret, b"nctf:admin-flag:v1")` hex,
   first 12 chars.

## Run

```
python3 solve.py
```

Output:

```
[+] forged admin JWT: eyJhbGciOi...
[+] FLAG = NCTF{…}
```

## Files

- `../.env`, `../docker-compose.yml`, `../app/session.py` — the leaked bundle.
- `../src/gen.py` — deterministic builder (not shipped to players).
- `solve.py` — reference solver (Python stdlib only).
