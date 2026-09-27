<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# atbash-cipher

## TL;DR

Atbash: `A<->Z`, `B<->Y`, .... It is its own inverse.

## Steps

```
tr 'A-Za-z' 'Z-Az-a' < secret.txt   # -> NCTF{…}
```

Or run `python3 solve.py`.

## Flag

`NCTF{…}`
