<!-- nctf-meta category="ai" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# oracle-canary-decoy

**Summary:** The easy answer is a decoy canary. The real flag is on the admin
channel, unlocked by an `X-Auth` header whose token is XOR-obfuscated in the
source.

## Vulnerability

`respond` checks headers first: if an `X-Auth` header equals the maintenance
token it returns the real flag on the admin channel. Otherwise, any request that
mentions the secret gets the decoy flag from the user channel. The maintenance
token is stored as `_TOK`, each byte XORed with `0x5b`, so it is not readable
directly in the file. Recovering it requires undoing the XOR.

## Steps

1. Notice the first answer scores as wrong -- it is the canary.
2. Read the source: `_admin_token()` builds the token as `chr(b ^ 0x5b)` over
   `_TOK`.
3. Reproduce that to get the token and send `X-Auth: <token>` before the
   request.

Run:

```
python3 solution/solve.py
```

## Flag

`NCTF{…}`
