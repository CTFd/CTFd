<!-- nctf-meta category="hardware" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# boot-rom

**Flag:** `NCTF{…}`

## TL;DR

`rom.bin` is a program for the NANO-8, a 3-byte-per-instruction 8-bit VM
specified in `ISA.md`. Implement the VM, run the ROM, and the `OUT` bytes are
the flag.

## The machine

- 8 registers `R0..R7` (8-bit, wrap mod 256), one flat byte-addressable memory,
  PC in bytes, instructions `opcode, arg1, arg2`.
- Opcodes used: `LDI` (0x01), `XOR` (0x05), `OUT` (0x08), `JNZ` (0x09),
  `ADDI` (0x0A), `HLT` (0x0B), `LDX` (0x0C, indexed load `Rr = mem[Rp]`).

## What the ROM does

Disassembled:

```
LDI  R0, 34        ; count = flag length
LDI  R1, 0x5A      ; xor key
LDI  R2, 30        ; pointer to the data block (right after the code)
loop:
LDX  R4, R2        ; R4 = mem[R2]
XOR  R4, R1        ; decode with key
OUT  R4            ; emit byte
ADDI R2, 1         ; advance pointer
ADDI R0, 0xFF      ; count -= 1  (adding 255 == -1 mod 256)
JNZ  R0, loop      ; repeat until count == 0
HLT
```

The bytes at offset 30..63 are the flag XORed with `0x5A`; the loop decodes and
prints them.

## Solve steps

1. Implement the VM from `ISA.md`: load `rom.bin` at address 0, fetch 3 bytes
   per step, dispatch on the opcode, advance PC by 3 (or jump on `JNZ`).
2. Run until `HLT`, appending each `OUT` operand to an output buffer.
3. Decode the buffer as ASCII → the flag.

Run the solver:

```
python3 solution/solve.py            # uses ../rom.bin
python3 solution/solve.py rom.bin
```

It prints `NCTF{…}`.
