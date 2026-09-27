<!-- nctf-meta category="hardware" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# i2c-sniff

**Flag:** `NCTF{…}`

## TL;DR

`i2c_capture.csv` is a two-channel I2C capture (`SCL`, `SDA`). Decode the START,
address byte, data bytes, and STOP; the data bytes spell the flag.

## Format / protocol

- `SDA` may only change while `SCL` is low; it is valid while `SCL` is high.
- **START** = `SDA` falls (1→0) while `SCL` is high.
- **STOP** = `SDA` rises (0→1) while `SCL` is high.
- A byte is 8 bits MSB-first, followed by a 9th **ACK** bit (receiver pulls
  `SDA` low = ACK).
- First byte after START = `(7-bit address << 1) | R/W`. Here address `0x42`,
  write. The following bytes are the ASCII payload.

## Solve steps

1. Parse the CSV into `SCL`/`SDA` sample arrays.
2. Scan for edges: detect START and STOP by an `SDA` transition while `SCL` is
   held high.
3. Between a START and the next STOP, latch `SDA` on each `SCL` rising edge.
   Every 9 latched bits = one byte (first 8 = data MSB-first, 9th = ACK).
4. Discard the address byte, decode the rest as ASCII → the flag.

Run the solver:

```
python3 solution/solve.py            # uses ../i2c_capture.csv
python3 solution/solve.py i2c_capture.csv
```

It prints `NCTF{…}`.
