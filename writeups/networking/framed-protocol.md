<!-- nctf-meta category="networking" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# framed-protocol

**Summary:** Reverse a length-prefixed binary framing, CRC-validate frames, keep
the DATA frames, order by seq, and concatenate their payloads.

## Technique

The stream is a sequence of frames:

```
0xAA | opcode(1) | seq(1) | length(2 BE) | payload(length) | crc(1)
```

- `crc` = XOR of every byte from `opcode` through the last payload byte.
- Opcodes: `0x10` DATA, `0x20` NOISE, `0x30` END.

Key gotchas:

- You must advance by the **length field**, not by scanning for `0xAA` — payloads
  can (and do) contain `0xAA`.
- Some frames carry a deliberately wrong CRC; those are decoys and must be
  discarded.
- DATA frames arrive out of order; reorder by `seq`.

## Steps

1. Hex-decode `stream.hex` into bytes.
2. Walk frames using the length field; stop at the END opcode.
3. For each frame, recompute the CRC and drop mismatches.
4. Keep DATA frames, sort by `seq`, concatenate payloads, decode as ASCII.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
