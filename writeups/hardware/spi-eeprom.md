<!-- nctf-meta category="hardware" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# spi-eeprom

**Flag:** `NCTF{…}`

## TL;DR

`spi_capture.csv` is a 4-channel SPI capture (`CS`, `CLK`, `MOSI`, `MISO`) of an
EEPROM read. Decode SPI mode 0 and read the bytes the EEPROM returns on `MISO`.

## Format

- Bus: standard 4-wire SPI, **mode 0** (CPOL=0, CPHA=0) → data valid on the
  **rising** edge of `CLK`.
- Framing: a transfer is active only while `CS` is **low**. Bytes are
  **MSB-first**, 8 bits each.
- Transaction: `MOSI` carries `0x03` (READ opcode) then a 16-bit address
  (`0x0100`); the EEPROM streams the stored bytes back on `MISO` while the
  master clocks dummy `0x00` bytes.

## Solve steps

1. Parse the CSV into the four channel arrays.
2. Walk the samples; on each `CLK` rising edge (0→1) while `CS==0`, latch one
   bit from `MOSI` and one from `MISO`.
3. Pack the latched bits MSB-first into bytes.
4. `MOSI` bytes = `03 01 00 …` (opcode + address). The `MISO` bytes after those
   3 command bytes are the returned payload = the flag.

Run the solver:

```
python3 solution/solve.py            # uses ../spi_capture.csv
python3 solution/solve.py spi_capture.csv
```

It prints `NCTF{…}`.
