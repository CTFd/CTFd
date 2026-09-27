<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# base64-decode

## TL;DR

`secret.txt` is Base64. Decode it.

## Steps

1. Notice the alphabet: `A-Z a-z 0-9 + /` with `=` padding -- that is Base64.
2. Decode it:

```
base64 -d secret.txt      # -> NCTF{…}
```

Or run `python3 solve.py`.

## Flag

`NCTF{…}`
