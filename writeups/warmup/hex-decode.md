<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# hex-decode

## TL;DR

`secret.txt` is hex-encoded ASCII. Decode two chars per byte.

## Steps

```
xxd -r -p secret.txt      # -> NCTF{…}
```

Or run `python3 solve.py`.

## Flag

`NCTF{…}`
