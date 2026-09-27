<!-- nctf-meta category="crypto" difficulty="medium" points="350" author="dagbanjaphet" stub="0" -->

# tlv-vault

**Category:** crypto - **Difficulty:** medium - **Flag:** `NCTF{…}`

## TL;DR

Parse the invented `VLT1` container correctly, honouring four traps that punish
naive parsing, extract a repeating-XOR key, and decrypt each vault. One of the
eight decrypts to the flag.

## The format

`VLT1` looks like an ordinary TLV container, which is exactly the point. Four
details break any parser that treats it like DER/protobuf or generic TLV:

1. **Length prefixes count records/entries, not bytes.** The header's
   `rec_count` is a number of records; each record's `count` is a number of
   _entries_, and you must multiply by the per-type entry size to advance.
2. **The header checksum covers the header only** (`sum(bytes[0:7]) & 0xFF`).
   Checksumming the whole file never validates - a hint you're using it wrong.
3. **The ciphertext offset is relative to EOF.** `ciphertext_start =
filesize - ct_off`. Reading from start-of-file lands in the wrong place.
4. **The `version` byte is a key mask.** Each stored key byte must be XORed
   with `version` to get the real key byte. Raw XOR (skipping the mask) yields
   near-garbage - the tell that something is still off.

One decoy: record type `0x53` (**SALT**). The spec marks it reserved; its bytes
look key-ish but are pure noise. Feeding them into the key gives garbage, and
the spec refutes it in one line. It never costs an attempt.

### Worked example - `vault_05.vlt` (the flag vault)

```
0000  56 4c 54 31 7c 02 00 a5   VLT1 | ver=0x7c | rec_count=2 | cksum=0xa5
0008  4b 08 02 9d 06 83 00 f6   KEY record: type=0x4b count=8 entries...
0010  03 8e 01 16 07 31 04 ef
0018  05 d8
001a  4d 02 20 00 24 00         META: type=0x4d count=2 -> ct_len=0x20, ct_off=0x24
0020  c9 3e ... 8b 30           ciphertext (32 bytes)
003e  00 45 4e 44               footer 0x00 'E' 'N' 'D'
```

- Header checksum: `sum(56 4c 54 31 7c 02 00) & 0xff = 0xa5`. Matches.
- `version = 0x7c`.
- KEY: `count=8`, so 8 entries x 2 bytes = 16 bytes. Entries are
  `(pos, stored)` and appear **out of order**: `(2,0x9d)(6,0x83)(0,0xf6)
(3,0x8e)(1,0x16)(7,0x31)(4,0xef)(5,0xd8)`. Real key byte =
  `stored ^ version`, e.g. `key[0] = 0xf6 ^ 0x7c = 0x8a`.
- META: `ct_len=32`, `ct_off=36`. `filesize = 68`, so
  `ciphertext_start = 68 - 36 = 32 (0x20)`. The last 4 bytes (`00 45 4e 44`)
  are the footer, not ciphertext - which is exactly why the offset is
  EOF-relative.
- XOR-decrypt the 32 ciphertext bytes with the 8-byte key -> `NCTF{…}`.

## Solve

`solution/solve.py` implements the parser and runs it over all eight vaults:

```
$ python3 solution/solve.py
vault_01.vlt: vault services log rotation completed ...
...
vault_05.vlt: NCTF{…}
...
FLAG: NCTF{…}
```

The samples deliberately vary version byte, key length (5-9), record order, and
whether the SALT decoy is present, so a hard-coded/positional parser fails on
some files. You need a general reader.

## Is this LLM-one-shot solvable? (honest assessment)

- **What an LLM does well:** it will spot the ASCII magic, recognise TLV-ish
  framing, and write a plausible parser quickly. Given the partial spec it can
  usually get to a working solver.
- **Where it slips:** every one of the four traps is a place where the "obvious"
  standard-TLV assumption is wrong. Common failure modes seen in testing:
  reading `count` as a byte length (walks off the first record), checksumming
  the whole file and declaring the files corrupt, reading the ciphertext from
  start-of-file, and forgetting the `version` mask (producing text that is
  _almost_ readable, which is a nasty tarpit because it looks close). A model
  that reads the spec carefully and iterates against "does this decode to ASCII"
  will get there; a one-prompt "decode this file" attempt generally does not,
  because no single assumption is standard and the traps compound.
- The decoy SALT record and the near-miss of raw-XOR-without-mask add two
  refutable-but-tempting dead ends.

## Reproducing the artifacts

`solution/generate.py` regenerates the exact eight public vaults
deterministically (fixed seeds). It is included for authorship/audit only and
is **not** shipped to players.
