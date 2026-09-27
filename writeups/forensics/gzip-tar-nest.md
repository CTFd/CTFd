<!-- nctf-meta category="forensics" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# gzip-tar-nest

**Category:** forensics · **Difficulty:** easy
**Flag:** `NCTF{…}` (static)

## One-line summary

A five-layer nested archive; unpack gzip -> tar -> zip -> gzip -> tar to reach
`flag.txt`.

## Technique

Recursive archive extraction. Each layer is a genuine, standard archive but a
different format from the one around it, so a single `gunzip` or `tar xf` only
reveals the next container:

```
parcel.tar.gz   gzip of a tar
  README.txt    breadcrumb: "open level2.zip"
  level2.zip    zip
    level3.tar.gz   gzip of a tar
      notes.txt     breadcrumb
      flag.txt      the flag
```

## Step by step

```
tar xzf parcel.tar.gz          # -> README.txt, level2.zip
unzip level2.zip               # -> level3.tar.gz
tar xzf level3.tar.gz          # -> notes.txt, flag.txt
cat flag.txt
```

Or in one shot: `binwalk -eM parcel.tar.gz` extracts every layer recursively.

## Run the reference solver

```
python3 solve.py ../parcel.tar.gz
```

## Flag

`NCTF{…}`
