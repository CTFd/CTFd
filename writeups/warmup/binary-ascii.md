<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# binary-ascii

## TL;DR

Groups of 8 bits -> ASCII bytes.

## Steps

For each space-separated 8-bit group, `int(group, 2)` gives a byte;
`chr` turns it into a character. Join them all.

Run `python3 solve.py`.

## Flag

`NCTF{…}`
