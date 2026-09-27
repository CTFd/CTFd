<!-- nctf-meta category="mobile" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# deeplink-guard

**Category:** mobile · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

An iOS app unlocks a "grant" screen only for one exact custom-scheme deeplink,
and it uses the canonical form of that deeplink as the key to decrypt the grant
code. Reconstructing the winning URI from the shipped constants recovers the
flag.

## The technique

An `.ipa` is a ZIP. Inside `Payload/VaultApp.app/`:

- `Info.plist` → `CFBundleURLSchemes` = `vaultapp`
- `DeepLinkRouter.swift` → validates `scheme == vaultapp`, `host == unlock`,
  `path == /grant`, `?code == s3cr3t-grant-0x5f`
- `Secrets.plist` → base64 `grant_ciphertext`

The winning deeplink is therefore:

```
vaultapp://unlock/grant?code=s3cr3t-grant-0x5f
```

and its exact string is the key:

```
ks[i] = sha256(canonical || byte(i/32))[i % 32]
flag  = grant_ciphertext XOR ks
```

## Solve

```
$ python3 solve.py VaultApp.ipa
winning deeplink: vaultapp://unlock/grant?code=s3cr3t-grant-0x5f
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes VaultApp.ipa with the flag embedded
```
