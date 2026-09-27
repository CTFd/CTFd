<!-- nctf-meta category="supplychain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# lockfile-integrity-drift

One tarball was tampered after the lockfile was generated, so its real sha512 no
longer matches the pinned `integrity`. The tamper is a block of bytes appended
**after** the gzip member, and those bytes carry the flag.

## Vulnerability

`package-lock.json` pins an SRI `integrity` (`sha512-<base64>`) per dependency.
Every shipped `.tgz` hashes to its pin except `minimist-1.2.8.tgz`. Its gzip
member is a byte-for-byte benign package (installing it, or running `tar`/`zgrep`
on it, reveals nothing), but extra bytes were appended after the gzip stream.
Those trailing bytes are the only reason the file's sha512 drifts from the pin —
the mismatch delta and the payload are the same bytes.

The payload is not stored in clear text or base64: it is the flag XORed with a
keystream derived from that dependency's **pinned** integrity. So you must (1)
find which dep's sha512 drifted, (2) read the bytes trailing its gzip member, and
(3) key off that dep's pinned integrity — no single step can be skipped or
grepped.

## Solve

1. For each entry, recompute `sha512-` + base64(sha512(tarball bytes)) and
   compare to the pinned `integrity`. Only `minimist` mismatches.
2. Split off the bytes after the gzip member of the mismatched tarball
   (e.g. `zlib.decompressobj(16 + zlib.MAX_WBITS)` then read `.unused_data`).
3. Rebuild the keystream `SHA512(pinned_integrity_string || counter_be32)` and
   XOR it against those trailing bytes to recover the flag.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
