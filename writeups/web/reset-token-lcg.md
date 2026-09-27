<!-- nctf-meta category="web" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# reset-token-lcg

**Summary:** Reset tokens come from an LCG seeded with the request's
whole-second timestamp. The log leaks exact timestamps, so the admin token is
fully predictable, which unseals the flag.

## Vulnerability

`make_token(seed)` runs a fixed linear congruential generator (`a=1664525`,
`c=1013904223`, mod `2**32`) seeded from `int(now)`. Second-granularity time is
guessable, and here it is written straight into `reset_log.txt`. The admin
token was not logged, but its issue second was -- enough to regenerate it.

`/reset/confirm` unseals the flag by XORing `SEALED_FLAG_HEX` with a keystream
of `sha256("resetseal|" + token)`, so the correct admin token is all you need.

## Steps

1. Parse `reset_log.txt`; confirm the LCG reproduces the logged guest tokens
   from their timestamps.
2. Seed the LCG with the admin line's timestamp to regenerate the admin token.
3. Reproduce `/reset/confirm`: derive the key and XOR `SEALED_FLAG_HEX`.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
