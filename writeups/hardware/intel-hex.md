<!-- nctf-meta category="hardware" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# intel-hex

**Flag:** `NCTF{…}`

## TL;DR

`image.hex` is an Intel HEX memory dump. Reassemble it into a flat image; the
flag is at offset `0x40` with each byte's nibbles swapped.

## Intel HEX format

Each record is `:LL AAAA TT [DD..] CC`:

- `LL` — data byte count
- `AAAA` — 16-bit load address
- `TT` — record type (`00` data, `01` EOF)
- `DD..` — data
- `CC` — checksum, the two's complement of the sum of all preceding bytes
  (so the whole record's bytes sum to 0 mod 256)

## Solve steps

1. For each `:` line, hex-decode the body, verify the checksum, and for data
   records copy the bytes into memory at their address.
2. Read the 34 bytes starting at offset `0x40`.
3. Undo the transform: swap the high and low nibble of every byte
   (`((b << 4) | (b >> 4)) & 0xFF`).
4. Decode as ASCII → the flag.

Run the solver:

```
python3 solution/solve.py            # uses ../image.hex
python3 solution/solve.py image.hex
```

It prints `NCTF{…}`.
