<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# vigenere-known-key

## TL;DR

Standard Vigenere with the key handed to you: `WARMUP`.

## Steps

1. For each letter, subtract the key letter's shift (repeating the key,
   skipping non-letters), mod 26.
2. Decrypting with `WARMUP` yields the flag directly.

Run `python3 solve.py`.

## Flag

`NCTF{…}`
