<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# rot13-decode

## TL;DR

ROT13. Applying ROT13 again reverses it.

## Steps

```
tr 'A-Za-z' 'N-ZA-Mn-za-m' < secret.txt   # -> NCTF{…}
```

Or run `python3 solve.py`.

## Flag

`NCTF{…}`
