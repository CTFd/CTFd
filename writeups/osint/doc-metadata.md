<!-- nctf-meta category="osint" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# doc-metadata

**Category:** osint · **Difficulty:** easy
**Flag:** `NCTF{…}`

## Summary

Six `.docx` files are signed by a generic comms team, but their OOXML core
metadata betrays a single insider editor whose keyword fields, in creation
order, spell the flag.

## Technique

OOXML metadata analysis. A `.docx` is a ZIP; `docProps/core.xml` holds
`dc:creator`, `cp:lastModifiedBy`, `cp:keywords`, and `dcterms:created`. The
visible author (`dc:creator`) is a decoy; the real editor is in
`cp:lastModifiedBy`.

## Step by step

1. Unzip each `.docx` and read `docProps/core.xml`.
2. Note `dc:creator` is always "Cellule Comms CERT.tg" — useless. The
   `cp:lastModifiedBy` field differs: `stagiaire.doc`, `presse.externe`, and the
   insider `afanou.k`.
3. Keep only the documents where `cp:lastModifiedBy == afanou.k` (four of them).
   Non-insider docs carry decoy keywords like `tarifs;energie`.
4. Sort those documents by `dcterms:created` and concatenate their `cp:keywords`:
   `NCTF{…}`.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
