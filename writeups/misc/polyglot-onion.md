<!-- nctf-meta category="misc" difficulty="medium" points="250" author="ctf-authoring" stub="0" -->

# polyglot-onion

**Category:** misc (polyglot / file-format forensics) · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Scenario

Players download one file, `keepsake.png`. It is a genuinely valid PNG (renders
in any viewer, `file` calls it `PNG image data, 96 x 96, 8-bit/color RGB`). It
is also a nested polyglot: peel one layer and you get another ordinary,
self-identifying file, and so on. Nothing labels the encodings — each layer must
be recognised from its **magic bytes / structure**.

## The onion (outside → in)

| Layer | What it is                                    | How you know                                                          | How to peel                       |
| ----: | --------------------------------------------- | --------------------------------------------------------------------- | --------------------------------- |
|    L0 | valid **PNG** with data appended after `IEND` | the file is bigger than the PNG; bytes continue past the `IEND` chunk | carve everything after `IEND`+CRC |
|    L1 | a **ZIP** archive (its one entry)             | `PK\x03\x04` local-file-header signature                              | unzip; read the single member     |
|    L2 | **Ascii85** text                              | printable, framed `<~ … ~>`                                           | `base64.a85decode(…, adobe=True)` |
|    L3 | a **gzip** stream                             | magic `1f 8b`                                                         | `gzip.decompress`                 |
|    L4 | a **bzip2** stream                            | magic `BZh`                                                           | `bz2.decompress`                  |
|    L5 | a **POSIX tar** with `flag.txt`               | `ustar` at offset 257                                                 | extract the member → the flag     |

Each transform is the _only_ thing that makes sense given the bytes in hand;
there are no format labels anywhere. Recognising `PK`, `1f 8b`, `BZh`, `<~ ~>`,
and the tar `ustar` magic is the whole challenge.

## Intended solve

Manual, with common tools:

```bash
# L0: PNG carries a trailing zip — the zip's own directory is at EOF
unzip keepsake.png            # tolerant tools read the appended archive
# -> inflates "scrap.txt"     (it's Ascii85: starts "<~", ends "~>")

python3 -c 'import base64,sys; sys.stdout.buffer.write(base64.a85decode(open("scrap.txt","rb").read().strip(), adobe=True))' > l2.bin
file l2.bin                   # gzip compressed data
gunzip -c l2.bin > l3.bin
file l3.bin                   # bzip2 compressed data
bunzip2 -c l3.bin > l4.tar
file l4.tar                   # POSIX tar archive
tar xf l4.tar && cat flag.txt
# NCTF{…}
```

A self-contained programmatic solver is in [`solve.py`](solve.py). It does **not**
hard-code the layout: at every step it sniffs the bytes it holds, dispatches to
the matching peeler, and stops when it sees an `NCTF{…}` token.

```bash
python3 solve.py ../keepsake.png
# [layer 0] detected png-trailer  -> 323 bytes
# [layer 1] detected zip          -> 207 bytes
# [layer 2] detected ascii85      -> 164 bytes
# [layer 3] detected gzip         -> 141 bytes
# [layer 4] detected bzip2        -> 10240 bytes
# [layer 5] flag found
# NCTF{…}
```

## Why the description doesn't give it away

Per the anti-LLM authoring rules the description only sets the scene ("an
ordinary picture that weighs too much; peel it") and never names PNG, zip,
Ascii85, gzip, bzip2 or tar. The player has to _deduce_ each layer from magic
bytes. There are no self-labelled decoys and the flag never appears verbatim in
the handout — it exists only inside the innermost tar member (`gen.py` asserts
this at build time).

## Rebuilding

`gen.py` (in the challenge root, **not** shipped, **not** listed in `files:`)
rebuilds `keepsake.png` deterministically — no wall-clock input: gzip `mtime=0`,
tar `mtime=0`, `ZIP_STORED` with a fixed date, and a formula-generated image.
Re-running produces a byte-identical handout (verified via `md5sum`).

## Honesty note — how an LLM does here

A capable agent that can run code will likely solve this: the individual moves
(carve trailing zip, spot `1f 8b`, `bunzip2`, untar) are textbook. The friction
that keeps it honest at **medium** is that _nothing states the chain_ — the
solver must inspect-and-dispatch at each of six layers, recover from the
appended-zip offset quirk, and recognise Adobe-framed Ascii85 rather than plain
base64. It rewards reading bytes, not reading the prompt.
