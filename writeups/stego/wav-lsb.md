<!-- nctf-meta category="stego" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# wav-lsb

Least-significant-bit steganography in the PCM samples of a WAV file.

## Technique

The flag bytes are written MSB-first into the low bit of each 16-bit mono
sample, terminated by a NUL byte. The audible carrier (a 440 Hz + 660 Hz hum)
masks the change entirely.

## Solve

1. Open the WAV with `wave` (16-bit, mono) and read all frames.
2. Unpack the samples as signed little-endian 16-bit integers.
3. Collect `sample & 1` for each, pack 8 bits per byte MSB-first.
4. Stop at the `0x00` terminator and decode as ASCII.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
