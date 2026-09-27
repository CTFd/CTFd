<!-- nctf-meta category="hardware" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# firmware-blob

**Flag:** `NCTF{…}`

## TL;DR

`firmware.bin` is a small custom container (`FWB1`) with a section table. The
`.flag` section is XOR-encoded with the key stored in the `.key` section.

## Container format

All integers are little-endian.

```
magic       4s   "FWB1"
version     u16
n_sections  u16
section table (n_sections x 20 bytes):
  name    8s   NUL-padded
  offset  u32  from start of file
  length  u32
  flags   u32  bit0 = XOR-encoded
raw section payloads at their offsets
```

Sections: `.boot` (banner), `.key` (4-byte XOR key), `.flag` (encoded flag).

## Solve steps

1. Read the header; confirm the magic `FWB1` and the section count.
2. Walk the section table, slicing each payload out with its `offset`/`length`.
3. The `.flag` entry has `flags & 1` set → XOR-encoded. Take the `.key` bytes
   and XOR-decode `.flag`, cycling the key.
4. Result is the ASCII flag.

Run the solver:

```
python3 solution/solve.py            # uses ../firmware.bin
python3 solution/solve.py firmware.bin
```

It prints `NCTF{…}`.
