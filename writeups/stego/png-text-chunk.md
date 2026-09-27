<!-- nctf-meta category="stego" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# png-text-chunk

The flag is hidden in a PNG `tEXt` metadata chunk, base64-encoded.

## Technique

PNG files may contain any number of `tEXt` keyword/value records. This image
ships two: a plaintext decoy (`Description`) and the real payload (`Signature`),
whose value is the base64 of the flag.

## Solve

1. Read the PNG's text metadata (`exiftool sunset.png`, `strings`, or parse the
   chunk stream directly — each chunk is length, type, data, CRC).
2. Collect every `tEXt` value.
3. Base64-decode each; the one that decodes to `NCTF{…}` is the flag.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
