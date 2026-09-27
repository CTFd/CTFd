<!-- nctf-meta category="web" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# flask-unsign

**Summary:** The Flask `secret_key` is hardcoded in the source, so the captured
session cookie can be decoded, edited to `role: admin`, re-signed, and the flag
unsealed offline.

## Vulnerability

Flask signs session cookies with `app.secret_key` using itsdangerous. That key
is committed in `app.py`. Anyone with the key can mint a cookie the server
treats as authentic, so the `role` field -- which gates `/admin/flag` -- is
attacker-controlled.

The flag is sealed (`SEALED_FLAG_HEX`) with a keystream derived from
`sha256(secret_key + "|panel-seal")`, so once you hold the key you can also
perform the unseal that `/admin/flag` would do.

## Steps

1. Pull `secret_key` out of `app.py`.
2. Load `session_cookie.txt` with the matching itsdangerous serializer to
   confirm `role: guest`.
3. Set `role: admin`, re-sign (this is what the admin route accepts).
4. Reproduce the unseal and XOR `SEALED_FLAG_HEX` back to the flag.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
