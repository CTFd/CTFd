<!-- nctf-meta category="reverse" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# byte-drift

**Category:** reverse · **Difficulty:** beginner
**Flag:** `NCTF{…}`

## Summary

A stripped x86-64 lock binary validates a passphrase byte-by-byte against an
embedded array using an invertible transform. Inverting the array recovers the
passphrase, which is the flag.

## The technique

Disassembling `main` → `check()` shows each input byte is transformed and
compared to `target[]`:

```c
t = ROL8((p[i] + (i*3 + 7)) & 0xFF, (i % 7) + 1) ^ 0x5C;
if (t != target[i]) return 0;
```

There is no stored flag string (`grep -a 'inv3rt_th3_drift' chall` → 0 hits).
Because the transform is a rotate + position-dependent add + xor, it is fully
invertible:

```
x    = target[i] ^ 0x5C
x    = ROR8(x, (i % 7) + 1)
p[i] = (x - (i*3 + 7)) & 0xFF
```

## Solve

Lift `target[]` from `.rodata` (or brute-force the window position) and invert
it. The solver scans every window, inverts, and keeps the one that decodes to
`NCTF{…}` — no hardcoded answer:

```
$ python3 solve.py ../chall
flag: NCTF{…}
```

Sanity check against the binary itself:

```
$ ./chall 'NCTF{…}'
=== byte-drift lock ===
[+] unlocked. the passphrase IS the flag.
```

## Rebuilding

```
make          # regenerate src/chall.c and compile ./chall
make verify   # confirm no plaintext flag, then run the solver
```
