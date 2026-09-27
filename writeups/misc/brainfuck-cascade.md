<!-- nctf-meta category="misc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# brainfuck-cascade

A base85 blob decodes to a Brainfuck program whose output is the flag.

## Technique

`cipher.txt` is a single base85 (`b85`) string. Decoding it yields a program
made only of the eight Brainfuck instructions `+ - < > . , [ ]`. The program is
a straight-line, delta-encoded printer: it adjusts one cell to each flag byte
and emits it with `.`. Running it prints the flag.

## Steps

1. `base64.b85decode` the contents of `cipher.txt`.
2. Interpret the result as Brainfuck (8-bit wrapping cells, no input needed).
3. The program's standard output is the flag.

Run `python3 solution/solve.py` (pure standard library; it includes a tiny
Brainfuck interpreter).

## Flag

`NCTF{…}`
