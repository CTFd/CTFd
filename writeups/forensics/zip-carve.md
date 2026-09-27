<!-- nctf-meta category="forensics" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# zip-carve

**Category:** forensics · **Difficulty:** easy
**Flag:** `NCTF{…}` (static)

## One-line summary

A ZIP member exists in the byte stream but was deleted from the central
directory; carve the orphaned `PK\x03\x04` local file header and inflate its
DEFLATE-compressed data to recover it.

## Technique

A ZIP file has two copies of its file metadata: a **local file header** in front
of each member's data, and a **central directory** at the end of the archive
that every tool actually reads. `archive.zip` has been edited so the central
directory lists only the decoy `notes.txt`, while the local header and
compressed bytes of `secret.txt` remain untouched in the stream. `unzip -l`,
`zipinfo`, and Python's `zipfile` therefore never reveal `secret.txt`.

The orphaned member is stored with **compression method 8 (DEFLATE)**, so its
payload is a raw deflate stream — `strings archive.zip` shows nothing readable.
You have to parse the local file header for the compressed size and method, then
inflate the bytes yourself.

## Step by step

1. `zipinfo archive.zip` (or Python `zipfile.namelist()`) shows only
   `notes.txt`, yet the file is bigger than that member.
2. Search the raw bytes for every local file header signature `PK\x03\x04`.
   There are two.
3. Parse the second header: name length, compressed size, and method = 8
   (DEFLATE). Read out its compressed payload — this is `secret.txt`.
4. Inflate that payload as a raw deflate stream (e.g. Python
   `zlib.decompress(payload, -15)`). It contains
   `internal recovery token -> NCTF{…}`.

Tools like `binwalk archive.zip` or `foremost` also surface the second member.

## Run the reference solver

```
python3 solve.py ../archive.zip
```

## Flag

`NCTF{…}`
