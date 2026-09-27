<!-- nctf-meta category="stego" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# trailing-zip

A BMP/ZIP polyglot: a valid bitmap with a ZIP archive appended after the pixel
data.

## Technique

The BMP header fixes the amount of pixel data, so viewers ignore everything
past it. A ZIP reader finds an archive by scanning backward from the end of the
file for the end-of-central-directory record, so appending a ZIP to a valid BMP
yields a file that is simultaneously a picture and an archive.

## Solve

1. Notice the file is much larger than a small bitmap should be.
2. Search the raw bytes for the `PK\x03\x04` / `PK\x05\x06` ZIP signatures.
3. Open the file directly with `unzip` or Python's `zipfile` (it handles the
   BMP prefix automatically) and read `secret/flag.txt`.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
