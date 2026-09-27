<!-- nctf-meta category="forensics" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# png-magic-fix

**Category:** forensics · **Difficulty:** beginner
**Flag:** `NCTF{…}` (static)

## One-line summary

The PNG signature has been zeroed out; restore it, then inflate the
zlib-compressed `zTXt` metadata chunk to read the flag.

## Technique

Every PNG begins with the fixed 8-byte signature
`89 50 4E 47 0D 0A 1A 0A`. In `evidence.png` those 8 bytes are `00`, so viewers
reject the file even though every chunk after it is valid. This is a classic
"fix the header magic" carve.

The recovery note is not stored in cleartext. It lives in a **`zTXt`** chunk,
whose text payload is zlib-_compressed_ (`keyword \x00` + a 1-byte compression
method + a zlib datastream). Because the bytes are compressed, `strings
evidence.png` shows nothing useful — you must actually parse the chunk and
inflate it.

## Step by step

1. Inspect the first bytes: `xxd evidence.png | head`. They are all zeros where a
   PNG signature should be.
2. Overwrite bytes 0–7 with the canonical PNG signature.
3. The file now opens. The image is a flat teal square — a decoy; the answer is
   in the metadata.
4. `strings evidence.png | grep NCTF` finds nothing: the metadata is compressed.
5. Read the `zTXt` chunk (`exiftool fixed.png` inflates it for you, or parse
   manually). The `Comment` keyword holds the zlib-compressed flag; inflate it.

## Run the reference solver

```
python3 solve.py ../evidence.png
```

It repairs the signature in memory, locates the `zTXt` chunk, inflates its
datastream, and prints the `Comment` value.

## Flag

`NCTF{…}`
