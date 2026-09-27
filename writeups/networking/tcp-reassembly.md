<!-- nctf-meta category="networking" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# tcp-reassembly

**Summary:** Place each segment's bytes at `offset = (seq - ISN - 1) mod 2**32`
and read the contiguous buffer.

## Technique

The segments are one direction of a TCP flow with **absolute** 32-bit sequence
numbers. Reassembly is by byte offset, not arrival order:

- The **SYN** segment carries the ISN; the first data byte is at `ISN + 1`.
- A segment's offset into the stream is `(seq - (ISN + 1)) mod 2**32`.
- The ISN is deliberately near `2**32`, so sequence numbers **wrap** — the
  modulus is required or offsets go negative/huge.
- Exact retransmissions and overlapping retransmissions repeat bytes already
  present; they carry identical bytes, so placing by offset naturally dedups.

## Steps

1. Parse `segments.json`; find the SYN to get the ISN.
2. For each data segment, compute `offset = (seq - ISN - 1) mod 2**32` and write
   its bytes at `offset..offset+len`.
3. Confirm the buffer is contiguous (no gaps) and decode as ASCII.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
