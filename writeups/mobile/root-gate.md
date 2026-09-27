<!-- nctf-meta category="mobile" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# root-gate

**Category:** mobile · **Difficulty:** easy
**Flag:** `NCTF{…}`

## Summary

An app hides its unlock code behind a root/tamper check. Statically, the check
is irrelevant: the trusted branch derives its decryption key from a hardcoded
`BuildConfig.RELEASE_CHANNEL`, so reading the constant recovers the flag.

## The technique

`MainActivity.onCreate` has two paths:

- `isTampered()` true → shows the decoy `NCTF{…}` (red herring)
- otherwise → decrypts `strings.xml`'s `secure_payload`

The decryption is a SHA-256 keystream XOR keyed by `RELEASE_CHANNEL`:

```
ks[i]  = sha256(RELEASE_CHANNEL || byte(i / 32))[i % 32]
flag[i] = ct[i] XOR ks[i]
```

The real flag is never stored in cleartext; only the decoy is.

## Solve

```
$ python3 solve.py securebank.apk
RELEASE_CHANNEL: prod-ch_88f2a
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes securebank.apk with the flag embedded
```
