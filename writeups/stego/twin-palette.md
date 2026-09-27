<!-- nctf-meta category="stego" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# twin-palette

Steganography in the palette indices of an indexed PNG.

## Technique

The palette is built in pairs: index `2k` and index `2k+1` hold the exact same
RGB colour. The picture is drawn with even indices, so flipping a pixel's index
low bit changes nothing visible. That low bit carries the flag (MSB first per
byte), terminated by a NUL byte. Inspecting the rendered RGB reveals nothing —
you must look at the raw index values.

## Solve

1. Open the image in palette mode (`mode == "P"`).
2. Read the raw index of every pixel (`img.tobytes()`), take `index & 1`.
3. Pack 8 bits per byte MSB-first, stop at the NUL terminator, decode ASCII.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
