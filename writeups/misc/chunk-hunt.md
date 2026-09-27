<!-- nctf-meta category="misc" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# chunk-hunt

Reassemble a flag split across a PNG's ancillary `tEXt` chunks.

## Technique

A PNG file is the 8-byte signature followed by a sequence of chunks, each
`length (4B) | type (4B) | data | crc (4B)`. `badge.png` is a real, viewable
image, but extra `tEXt` chunks were spliced in before `IEND`. Their keywords
are `frg00`, `frg01`, ... and each holds a 5-character slice of a base85 string.
The chunks are stored out of order, and a decoy `Comment` chunk is thrown in.

## Steps

1. Walk the chunk stream from offset 8, reading each chunk's length and type.
2. Collect every `tEXt` chunk whose keyword starts with `frg`.
3. Sort the fragments by the numeric suffix and concatenate them.
4. base85-decode the result.

Run `python3 solution/solve.py` (pure standard library).

## Flag

`NCTF{…}`
