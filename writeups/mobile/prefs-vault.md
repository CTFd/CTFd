<!-- nctf-meta category="mobile" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# prefs-vault

**Category:** mobile · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

An app stores an encrypted session token in SharedPreferences and decrypts it
locally with a key derived from a hardcoded pepper plus the per-install salt.
Both ship in the backup, so the token is recoverable offline.

## The technique

- `shared_prefs/vault_prefs.xml` → `device_salt` and base64 `enc_token`
- `TokenStore.java` → `PEPPER` constant, key derivation, RC4

```
key       = SHA-256(PEPPER || device_salt)
flag      = RC4(key, base64_decode(enc_token))
```

RC4 is symmetric, so the same routine decrypts. The plaintext flag never
appears in the bundle.

## Solve

```
$ python3 solve.py quicknotes.apk
pepper: app_pepper_v2_9c1f | salt: a1b2c3d4e5f60718
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes quicknotes.apk (prefs + decompiled TokenStore)
```
