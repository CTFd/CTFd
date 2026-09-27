<!-- nctf-meta category="forensics" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# mem-struct

**Category:** forensics · **Difficulty:** medium
**Flag:** `NCTF{…}` (static)

## One-line summary

Locate a 16-byte record by its magic, read the offset/length/XOR-key it holds,
then de-obfuscate the flag bytes it points to.

## Technique

Memory-forensics struct chasing. The dump is 64 KiB of random bytes with:

- a **decoy** plaintext `NCTF{…}` at `0x1200` (what a lazy `strings` finds),
- the real flag at `0xB840`, stored XOR-obfuscated so `strings` cannot see it,
- a `secret_record` struct at `0x74C0` describing where and how the flag is
  stored.

The struct (little-endian) is:

```
uint32 magic     0x0FF5E7ED
uint32 xor_key
uint32 flag_off    absolute offset of the flag in the dump
uint32 flag_len
```

## Step by step

1. `strings memdump.bin | grep NCTF` finds only the decoy — set it aside.
2. Search for the magic bytes `ED E7 F5 0F` (little-endian `0x0FF5E7ED`).
3. Parse the 16 bytes there into `magic, xor_key, flag_off, flag_len`.
4. Read `flag_len` bytes at `flag_off`.
5. XOR each byte with the repeating 4-byte little-endian `xor_key`
   (`byte[i] ^ key[i % 4]`). The result is the flag.

## Run the reference solver

```
python3 solve.py ../memdump.bin
```

## Flag

`NCTF{…}`
