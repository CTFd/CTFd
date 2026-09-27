<!-- nctf-meta category="hardware" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# manchester-ook

**Flag:** `NCTF{…}`

## TL;DR

`samples.txt` is an oversampled OOK envelope of a Manchester-coded packet.
Recover the half-bit period, pair half-bits into bits, and decode MSB-first
bytes after the sync.

## Line coding

- On-off keying: `1` = carrier on, `0` = carrier off, one value per sample.
- **Manchester (Thomas convention):** each bit is two half-bits of opposite
  level. `1` = low→high, `0` = high→low. There is always a transition in the
  middle of a bit, which is what makes the coding self-clocking.
- Oversampling: 5 samples per half-bit → 10 per bit.
- Packet: alternating preamble, sync byte `0x7E`, then the flag as MSB-first
  bytes.

## Solve steps

1. Read the samples.
2. The shortest run of a constant level is one half-bit (5 samples). That gives
   the half-bit period.
3. Reduce to one level per half-bit by sampling each half-bit's centre.
4. Pair adjacent half-bits into bits (`low,high`→one value, `high,low`→the
   other). Because the polarity convention and the pairing/byte alignment are
   not known a priori, try both conventions, both pair offsets, and all 8 bit
   offsets; group MSB-first into bytes and keep the interpretation whose text
   contains `NCTF{…}` (the sync byte `0x7E` marks the payload start).

Run the solver:

```
python3 solution/solve.py            # uses ../samples.txt
python3 solution/solve.py samples.txt
```

It prints `NCTF{…}`.
