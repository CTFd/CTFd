<!-- nctf-meta category="hardware" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# uart-capture

**Flag:** `NCTF{…}`

## TL;DR

`capture.csv` is a uniformly-sampled logic-analyzer recording. The `d0_uart`
column is an idle-high UART line carrying one ASCII message at 8N1; `d1_refclk`
is an unrelated decoy probe. Decode the UART frames to read the flag.

## Format

| field       | meaning                                        |
| ----------- | ---------------------------------------------- |
| `time_ns`   | sample timestamp in nanoseconds (dt = 1000 ns) |
| `d0_uart`   | UART data line level (0/1)                     |
| `d1_refclk` | decoy clock probe, no framing — ignore it      |

- Sample rate: 1 MHz (from the 1000 ns step in `time_ns`).
- Line coding: UART **8N1**, idle high, **LSB-first**, no parity.
- Baud: 125000 → exactly 8 samples per bit.

## Solve steps

1. **Read the CSV** and pull `d0_uart` plus the sample period from `time_ns`
   (dt = 1000 ns → 1 MHz).
2. **Recover the bit period.** The shortest run of a constant level on the line
   is one bit time. Here it is 8 samples → 125000 baud.
3. **Frame the bytes.** UART is asynchronous: idle is high, and each byte starts
   with a falling edge (start bit = 0). After the start bit, sample the centre
   of each of the 8 data-bit cells, LSB-first, then confirm the stop bit is
   high.
4. **Assemble** the bytes into ASCII → the flag.

Run the solver:

```
python3 solution/solve.py            # uses ../capture.csv
python3 solution/solve.py capture.csv
```

It prints `NCTF{…}`.
