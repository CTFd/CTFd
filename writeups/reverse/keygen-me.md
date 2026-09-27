<!-- nctf-meta category="reverse" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# keygen-me

**Category:** reverse · **Difficulty:** hard
**Flag:** `NCTF{…}`
**Accepted key:** `JZBVIRT3-NNSXSZZT-NZPXG33M-OYZWIX3U-NAZV643F-OJUWC3D5`

## Summary

The validator enforces a chained constraint system on the base32 symbols of a
license key. The system has a unique solution; that solution is the base32
encoding of the flag, so decoding the accepted key reveals it.

## The technique

The key is 48 symbols from the RFC4648 base32 alphabet (`A-Z2-7`), grouped in
eights. Each symbol is read as its 5-bit index `v[i]`. `check()` verifies:

```c
if (v[0] != t[0]) return 0;
for i in 1..47:
    if ((v[i] + 3*v[i-1] + 7*i + 0x1B) % 32 != t[i]) return 0;
```

against an embedded target array `t[]` of 48 values (each `< 32`). The flag is
not stored anywhere — even a valid key only prints "license accepted".

## Solve

The constraints are triangular, so forward substitution gives the unique key:

```
v[0] = t[0]
v[i] = (t[i] - 3*v[i-1] - 7*i - 0x1B) % 32
```

The solved `v[]` is the base32 encoding of the flag, so repack the 48 five-bit
values into bytes (i.e. base32-decode) to read it. The solver lifts `t[]` from
the binary (a 48-byte run, all `< 32`), solves, and repacks — no hardcoded
answer:

```
$ python3 solve.py ../chall
serial: JZBVIRT3-NNSXSZZT-NZPXG33M-OYZWIX3U-NAZV643F-OJUWC3D5
flag  : NCTF{…}
```

Confirm the key against the validator:

```
$ ./chall 'JZBVIRT3-NNSXSZZT-NZPXG33M-OYZWIX3U-NAZV643F-OJUWC3D5'
[+] license accepted. (decode the key to read the flag)
```

## Rebuilding

```
make          # regenerate src/chall.c and compile ./chall
make verify   # confirm no plaintext flag, then run the solver
```
