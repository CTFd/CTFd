<!-- nctf-meta category="misc" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# pbkdf2-crack

Recover a passphrase from a PBKDF2-HMAC-SHA256 record using the shipped
wordlist.

## Technique

`hash.txt` is a Django-style password record:

```
pbkdf2_sha256$1200$n0tr4nd0m$<base64 derived key>
```

The four `$`-separated fields are the algorithm, the iteration count, the salt,
and the base64-encoded 32-byte derived key. PBKDF2 is not reversible, but the
work factor here is low, so a dictionary attack over the shipped `wordlist.txt`
(2001 candidates) finishes instantly.

## Steps

1. Split `hash.txt` on `$` to get iterations, salt, and the base64 key.
2. For each candidate word, compute
   `hashlib.pbkdf2_hmac("sha256", word, salt, iterations)`.
3. The word whose derived key matches is the passphrase: `sunshine_dragon_42`.
4. The flag is `NCTF{…}`.

Run `python3 solution/solve.py`.

## Flag

`NCTF{…}`
