<!-- nctf-meta category="mobile" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# keystore-alias

**Category:** mobile · **Difficulty:** hard
**Flag:** `NCTF{…}`

## Summary

An app ships a custom keystore blob with several alias entries. Each entry's
plaintext is protected by a key derived from the alias, a per-entry salt, and a
hardcoded passphrase. Deriving the key for the correct alias recovers the flag.

## The technique

`KeyDeriver.java` documents both the format and the derivation.

Format of `assets/vault.keystore`:

```
"AKS1" | count | { aliasLen | alias | salt(16) | encLen(2 BE) | enc } * count
```

Per entry:

```
master = sha256(alias || salt || PASSPHRASE)
ks[i]  = sha256(master || byte(i/32))[i % 32]
plain  = enc XOR ks
```

The app unlocks the `grant` alias (the `legacy` alias holds a decoy). Only
ciphertext is stored, never the plaintext flag.

## Solve

```
$ python3 solve.py entvault.apk
[decoy] legacy: NCTF{…}
[TARGET] grant: NCTF{…}
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes entvault.apk (vault.keystore + KeyDeriver.java)
```
