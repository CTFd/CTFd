<!-- nctf-meta category="web" difficulty="medium" points="400" author="ctf-2026" stub="0" -->

# cms-jwtconf

**Category** web · **Value** 400 · **Served** yes (per-team flag)

## Vulnerability

RS256/HS256 **algorithm confusion** in a homegrown JWT verifier.

The service signs its session tokens with RS256 and publishes the RSA **public**
key at `/pubkey`. Its verifier reads the `alg` header and branches:

- `alg=RS256` → verify the signature against the RSA public key;
- `alg=HS256` → verify as HMAC-SHA256 **using that same public-key PEM as the
  secret**.

Because the public key is public, an attacker can compute a valid HS256 MAC over
any header/payload of their choosing. The role check on `/flag` (`role=="admin"`)
is therefore forgeable.

## Intended path

1. `GET /pubkey` — grab the exact PEM bytes the server serves.
2. Build a token `{"alg":"HS256","typ":"JWT"}` / `{"role":"admin","iss":"cms-jwtconf"}`
   and sign it with `HMAC_SHA256(pem_bytes, signing_input)`.
3. `GET /flag` with `Authorization: Bearer <forged token>` → the per-team flag.

Guest tokens (`role=guest`, RS256) get 403 on `/flag`; no token gets 401. The
flag file `/flag.txt` is returned by no route other than this admin-gated check.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

The solver fetches `/pubkey`, forges the HS256 admin token, and reads `/flag`.

## Why it resists AI one-shotting

The flag is per-team (HMAC-derived) and lives only on the running instance —
there is no downloadable artifact to hand an agent, and a flag pasted from one
team is useless to another. Solving still requires recognising the confusion and
re-deriving the MAC against _this_ instance's published key.

> Variante de la classe `jwt-relay` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): solver recovers the exact per-team flag; `/flag` returns 401 without a
token and 403 for a guest token. **Docker/Lot-5 rehearsal (image build +
entrypoint flag injection under su-exec) is the remaining gate before
`state: visible`.**
