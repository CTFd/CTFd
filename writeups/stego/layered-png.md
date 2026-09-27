<!-- nctf-meta category="stego" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# layered-png

A multi-stage stego chain: LSB plane -> ZIP -> base64 -> flag.

## Technique

The LSBs of the R/G/B bytes carry a byte stream shaped as a 4-byte big-endian
length prefix followed by that many bytes of a ZIP archive. The ZIP contains
`stage2.txt`, whose content is the base64 of the flag.

## Solve

1. Load the PNG as RGB, collect `byte & 1` for every colour byte in order, and
   pack them 8 at a time (MSB first) into bytes.
2. Read the first 4 bytes as a big-endian length `N`; take the next `N` bytes.
3. Those bytes are a ZIP. Open it and read `stage2.txt`.
4. Base64-decode that content to reveal the flag.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
