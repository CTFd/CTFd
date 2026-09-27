<!-- nctf-meta category="reverse" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# crc-forge

**Category:** reverse · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

The validator stores a CRC32 per character position instead of the flag itself.
Because each CRC covers only a position byte plus one flag byte, every flag byte
is trivially brute-forced.

## The technique

`check()` recomputes a checksum for each input byte and compares it to a fixed
table:

```c
if (crc32_2((uint8_t)(i & 0xFF), p[i]) != table[i]) return 0;
```

`crc32_2` is a standard CRC32 (reflected, poly `0xEDB88320`, init/final
`0xFFFFFFFF`) over the two-byte message `{i & 0xFF, flag[i]}`. No flag character
is stored (`grep -a 'crc32_le4ks' chall` → 0 hits).

CRC32 is collision-prone in general but injective over a single byte with a
fixed prefix. So for each position `i`:

```
for b in 0..255:
    if crc32([i & 0xFF, b]) == table[i]: flag[i] = b
```

## Solve

The table is a raw little-endian `uint32` array. The solver slides a
4-byte-aligned window over the file, decodes consecutive entries using the local
index as the position salt, and keeps the run that spells `NCTF{…}` — no
hardcoded offset or answer:

```
$ python3 solve.py ../chall
flag: NCTF{…}
```

Verify against the binary:

```
$ ./chall 'NCTF{…}'
[+] checksums match. that is the flag.
```

## Rebuilding

```
make          # regenerate src/chall.c and compile ./chall
make verify   # confirm no plaintext flag, then run the solver
```
