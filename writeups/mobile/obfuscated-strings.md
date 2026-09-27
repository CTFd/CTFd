<!-- nctf-meta category="mobile" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# obfuscated-strings

**Category:** mobile · **Difficulty:** easy
**Flag:** `NCTF{…}`

## Summary

A "StringFog"-style build plugin stores the license string as an obfuscated
`int[]` and rebuilds it at runtime. Reimplementing the decode loop over the
shipped array recovers the flag.

## The technique

`sources/com/stashbox/app/StringFog.java` contains `DATA` and `unfog()`. The
encode used at build time was, per index `i`:

```
x = (flag[i] + (i*7 + 3)) & 0xFF
x = ROL8(x, (i % 5) + 1)
x ^= 0xA5
```

`unfog()` inverts it: XOR `0xA5`, rotate right by `(i % 5) + 1`, subtract
`(i*7 + 3)` mod 256. The plaintext flag never appears in the file.

## Solve

Parse `DATA` out of the class and run the inverse:

```
$ python3 solve.py app.apk
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes app.apk with the flag embedded as obfuscated DATA
```
