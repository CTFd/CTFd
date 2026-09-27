<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# html-entities

## TL;DR

Numeric HTML character references `&#NNN;`. Unescape them.

## Steps

`&#78;` = `N` (decimal code point 78), and so on. Python's
`html.unescape` does the whole string at once.

Run `python3 solve.py`.

## Flag

`NCTF{…}`
