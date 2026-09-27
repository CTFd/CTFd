<!-- nctf-meta category="forensics" difficulty="medium" points="350" author="ctf-team" stub="0" -->

# SRAM Retention

**Category:** forensics · **Difficulty:** medium · **Flag:** `NCTF{…}`

## TL;DR

`retention.dump` is an image of an invented banked SRAM (the "AE-32"). Parse the
8-byte header, read the bank base table (EOF-relative u16 offsets), locate each
bank by its `BNK`+id tag, then de-interleave the key that was written round-robin
across the banks. The datasheet gives the structure; two fields are designed to
trip up a fast reader.

## The artifact

- `retention.dump` — 1024-byte raw SRAM image containing the key.
- `AE32_SRAM_datasheet.md` — partial spec of the invented format.
- `samples/*.dump` + `samples/KNOWN.txt` — six worked images with known plaintext
  so you can validate your parser first.

## Format recap (from the datasheet)

Header at `0x00` (little-endian throughout):

| Off  | Sz  | Field                                     |
| ---- | --- | ----------------------------------------- |
| 0x00 | 4   | `MAGIC` = `AE32`                          |
| 0x04 | 1   | `NBANKS`                                  |
| 0x05 | 1   | `VAULT_LEN`                               |
| 0x06 | 1   | `STRIDE`                                  |
| 0x07 | 1   | `HCK` (checksum of bytes 0x00..0x06 only) |

Then at `0x08`, `NBANKS` × u16 LE bank base table. Each bank starts with tag
`b"BNK" + bytes([logical_id])`; vault registers begin 4 bytes after the tag.

## The three things you have to get right

1. **Bank offsets are end-of-file relative.** The table stores a _distance from
   EOF_, not an absolute offset:
   `phys(bank i) = filesize - table_entry[i]`.
   The `BNK`+id tag at the computed offset confirms you did it right. (If you read
   the entries as absolute offsets they point into noise and no tag appears.)

2. **The header checksum covers the header only** (7 bytes), not the whole image
   and not the base table. Handy to confirm you parsed the header correctly;
   misleading if you assume it's a whole-file integrity check.

3. **The key is interleaved round-robin across logical banks.** Byte `k` of the
   key is in logical bank `k % NBANKS`, slot `j = k // NBANKS`, at intra-bank
   offset `4 + j*STRIDE`. Consecutive key bytes live in _different_ banks, so any
   single bank read in isolation gives you gibberish. De-interleave in that order.

## Solve

```bash
python3 solve.py ../retention.dump
# NCTF{…}
```

Validate the parser on the samples first:

```bash
for f in ../samples/sample_0*.dump; do python3 solve.py "$f"; done
# matches samples/KNOWN.txt exactly
```

Core of `solve.py`:

```python
nbanks, vault_len, stride = data[4], data[5], data[6]
assert (sum(data[0:7]) & 0xFF) == data[7]          # header-only checksum
phys = [len(data) - u16le(data, 0x08 + 2*i) for i in range(nbanks)]  # EOF-relative
for i, base in enumerate(phys):
    assert data[base:base+3] == b"BNK" and data[base+3] == i
key = bytes(
    data[phys[k % nbanks] + 4 + (k // nbanks) * stride]
    for k in range(vault_len)
)
```

## The decoy

`strings retention.dump` returns `NCTF{…}`. It is a
plain contiguous string sitting in the retention noise at `0x40`, **not** inside
any tagged bank and never touched by the interleave rule — the datasheet says the
vault only ever lives in tagged banks and is assembled by interleaving. It's
refutable in seconds: it has no `BNK` tag around it and no bank base table entry
points near it. One decoy, costs nothing, punishes only the reflexive `strings`
grab.

## Honest note for pre-testing

This is a _careful reading + de-interleave_ problem, not an obscure-tooling one.
A capable solver (LLM included) that actually reads the datasheet can write the
parser directly; the samples exist precisely so you can confirm the interleave
order without guesswork. What makes it non-trivial and non-one-prompt:

- The two counter-intuitive fields (EOF-relative offsets, header-only checksum)
  are stated tersely and are easy to skim past — getting either wrong yields
  garbage, and the `BNK` tag is the only signal that you're off.
- The round-robin interleave means naive "read the bytes after each tag" or
  "concatenate banks in file order" both fail; the exact `k % NBANKS` /
  `k // NBANKS` mapping has to be reproduced.
- The `strings` decoy plus retention noise mean the flag is not sitting in the
  clear anywhere, so a solve without parsing the structure isn't possible.

Regenerate all artifacts deterministically with `python3 ../gen.py`.
