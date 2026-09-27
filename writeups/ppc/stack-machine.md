<!-- nctf-meta category="ppc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# stack-machine

`program.txt` is a program for a tiny stack machine; interpreting it faithfully
prints the flag.

## Technique

The machine has an operand stack and a flat integer memory. The instruction set
is:

- `PUSH n` / `POP` / `DUP`
- `LOAD` (pop address, push `mem[address]`)
- `STORE` (pop address, then pop value, set `mem[address] = value`)
- `ADD` / `SUB` / `MUL` / `MOD` (pop `B` then `A`, push `A op B`)
- `EMIT` (pop, output `chr(value & 0xFF)`)
- `JMP L` / `JZ L` (labels end with `:`)
- `HALT`
- `.data BASE v0 v1 ...` preloads `mem[BASE + i] = vi`

The program loops over the data cells and emits `(data[i] * 37 + 91) mod 256`
for each, so the stored data bytes are deliberately not the flag; only running
the arithmetic reveals it.

## Steps

1. Parse the lines: record label positions, load the `.data` cells into memory,
   keep the rest as the code stream.
2. Execute from the top, honoring the operand-order rules above.
3. Collect `EMIT` output; that string is the flag.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

Linear in the number of executed instructions (a few hundred) — instant.

## Flag

`NCTF{…}`
