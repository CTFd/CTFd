<!-- nctf-meta category="mobile" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# native-xor

**Category:** mobile · **Difficulty:** hard
**Flag:** `NCTF{…}`

## Summary

An Android app validates its flag in a native `.so`. The decompiled JNI routine
ships the full substitution box and XOR key, and compares a per-byte transform
of the input against `assets/enc.bin`. Inverting the transform recovers the
flag.

## The technique

`lib/arm64-v8a/decompiled_native.c` shows:

```c
t = (flag[i] + i) & 0xff;
t ^= KEY[i % 6];
enc[i] = SBOX[t];         // compared against assets/enc.bin
```

Every step is invertible. Build `SBOX_INV` from the shipped 256-byte `SBOX`,
then per index `i` of `enc.bin`:

```
t = SBOX_INV[enc[i]]
t ^= KEY[i % 6]
flag[i] = (t - i) & 0xFF
```

The plaintext flag is never stored; only the transformed bytes are.

## Solve

```
$ python3 solve.py nativegame.apk
key: 13 37 42 9a 5c e1
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes nativegame.apk (decompiled_native.c + enc.bin)
```
