<!-- nctf-meta category="web" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# jwt-forge

**Summary:** The HS256 signing secret is leaked in a committed `config.env`, so
you can forge an `admin` token and unseal the flag offline.

## Vulnerability

`app.py` verifies bearer tokens with a hardcoded symmetric key
(`JWT_SECRET`). That same key was committed in plaintext to `config.env`. With
the key in hand there is no forgery barrier: you can mint a token with any
claims, including `role: admin`.

The flag is not stored in cleartext. `/api/flag`, once it accepts an admin
token, XOR-decrypts `SEALED_FLAG_HEX` with a keystream derived from
`sha256(secret + "|ops-seal")`. Holding the secret is enough to run that step
yourself.

## Steps

1. Read `JWT_SECRET` out of `config.env`.
2. Forge `{"sub":"x","role":"admin"}` signed with HS256 using that secret (this
   is exactly what the server would accept at `/api/flag`).
3. Reproduce the unseal: derive `key = sha256(secret + "|ops-seal")`, build the
   `sha256(key || counter)` keystream, and XOR it against `SEALED_FLAG_HEX`.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
