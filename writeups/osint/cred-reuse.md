<!-- nctf-meta category="osint" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# cred-reuse

**Category:** osint · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

Crack a leaked forum hash dump with the supplied wordlist, find the account that
reused its password on the admin-portal, and use that password to decrypt the
admin note.

## Technique

Offline hash cracking (SHA-1 vs wordlist) + credential-reuse pivot across a
service registry + a standard OpenSSL AES-256-CBC (PBKDF2) decrypt.

## Step by step

1. Hash every word in `wordlist.txt` with SHA-1 and match against `dump.txt`.
   Most accounts crack.
2. Read `services.csv`. Find the cracked email registered on both `forum` and
   `admin-portal`: `afi.doe@webmail.tg`, password `Lome228!`. (`root.admin@cert.tg`
   is on the admin-portal but not in the forum breach, so it cannot be cracked —
   a dead end.)
3. `admin_portal.enc` is a standard OpenSSL container (it begins with the
   `Salted__` magic, `openssl enc -aes-256-cbc -pbkdf2`). Decrypt it with the
   reused password:
   `openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:'Lome228!' -in admin_portal.enc`.
4. Read the `jeton de secours` line — the flag.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
