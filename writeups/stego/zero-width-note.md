<!-- nctf-meta category="stego" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# zero-width-note

The flag is encoded in invisible zero-width characters spliced into a plain
text memo.

## Technique

Each flag byte is written MSB-first as 8 zero-width characters: U+200B
(zero-width space) for bit 0 and U+200C (zero-width non-joiner) for bit 1. When
rendered the note looks completely normal.

## Solve

1. The file is longer than its visible text. A hex dump shows `e2 80 8b` /
   `e2 80 8c` (UTF-8 for U+200B / U+200C) between the words.
2. Keep only those two code points in order, map them to bits 0 and 1.
3. Pack 8 bits per byte (MSB first) and decode as ASCII.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
