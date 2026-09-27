<!-- nctf-meta category="reverse" difficulty="medium" points="350" author="challenge-team" stub="0" -->

# packed-vm-lite

**Flag:** `NCTF{…}`

## TL;DR

The binary contains a hand-rolled bytecode interpreter (a small register+stack
VM, ~30 opcodes) plus a 77-byte program and two 24-byte tables (`VMKEY`,
`VMTARGET`). The program loops over the 24-char serial, transforms each byte,
and compares to `VMTARGET`. Read the opcode `switch`, recover the per-byte
transform, and invert it. The flag is printed as `NCTF{…}` on success and
is **not** stored anywhere in the file.

## 1. Recon

```
$ file vmcheck
vmcheck: ELF 64-bit LSB pie executable, x86-64, stripped
$ strings vmcheck | grep -i CTF
NCTF{…}                      # just the output format, not the flag
$ strings vmcheck | grep -i DEAD
vault_master_key=0xDEADBEEFCAFEBABE
```

That `vault_master_key=...` string is the **decoy**. Cross-reference it: nothing
in the code reads it. It is refuted in a minute and never used - ignore it. The
`NCTF{…}` shows the flag is built from a runtime string, so we need the serial.

## 2. Find the interpreter

In a disassembler the core is one big `switch` on a byte fetched from a static
array (`PROG`), driven by a program counter, with a 256-byte stack and a 16-entry
register file. That shape - fetch opcode, dispatch, mutate stack/regs, advance
pc - is a bytecode VM. Recover the semantics opcode by opcode. The full ISA is:

| op   | name     | effect                                |
| ---- | -------- | ------------------------------------- | --- |
| 0x01 | PUSH i   | push imm                              |
| 0x03 | DUP      | duplicate top                         |
| 0x05 | LDR i    | push regs[i]                          |
| 0x06 | STR i    | pop -> regs[i]                        |
| 0x07 | INC i    | regs[i]++                             |
| 0x09 | LOADR    | pop idx -> push input[idx]            |
| 0x0A | LOADK    | pop idx -> push KEY[idx]              |
| 0x0B | LOADT    | pop idx -> push TARGET[idx]           |
| 0x0C | ADD      | (a+b)&0xff                            |
| 0x0E | XOR      | a^b                                   |
| 0x10 | OR       | a                                     | b   |
| 0x12 | ADDI i   | top += i                              |
| 0x14 | MULI i   | top \*= i                             |
| 0x15 | ANDI i   | top &= i                              |
| 0x16 | ROLV     | pop amt, pop val -> rotl8(val, amt&7) |
| 0x19 | CMPEQ    | pop a,b -> (a==b)?1:0                 |
| 0x1B | CHKLEN i | if len!=i set regs[3]=1               |
| 0x1C | JMP i    | pc = i (ABSOLUTE offset)              |
| 0x1E | JNZ i    | pop; if !=0 pc = i                    |
| 0x1F | HALT     | stop                                  |

Gotchas that punish skimming:

- **Jump operands are absolute program offsets**, not relative displacements.
- **`ROLV` rotates by a value taken off the stack** (the amount is computed as
  `(i*3+1)&7`), not by an immediate.
- `0x17 RORV` and `0x18 NOT` exist in the dispatch table but the program never
  emits them - dead opcodes, a wrong turn if you assume every handler is used.

## 3. Recover the transform

Following the loop body, for byte index `i` (0-based), with `prev` seeded to
`0x5A`:

```
amt = (i*3 + 1) & 7
t   = rotl8(serial[i], amt)
t  ^= KEY[i]
t   = (t + prev) & 0xFF
require t == TARGET[i]
prev = serial[i]          # feedback uses the RAW serial byte, not t
```

The feedback on the raw plaintext byte is the subtle bit: it makes recovery
strictly left-to-right (each byte depends on the previous recovered byte), but
it is fully deterministic - no search needed.

## 4. Invert

```
t = (TARGET[i] - prev) & 0xFF
t ^= KEY[i]
serial[i] = rotr8(t, amt)
prev = serial[i]
```

`KEY[]` and `TARGET[]` are lifted straight from `.rodata`. Run
[`solve.py`](solve.py):

```
$ python3 solve.py ../vmcheck
serial: vm_bytec0de_1s_n0t_h4rd!
flag:  NCTF{…}
--- binary says ---
Correct!
NCTF{…}
[+] verified against binary
```

## Honest note on LLM difficulty

An LLM is **good** at the last mile here: once the ~30 opcode handlers are
described, deriving and inverting the per-byte transform is straightforward and
a capable model writes the correct inverse in one shot. The real work - and
where a one-prompt attempt fails - is faithfully reading the dispatch table from
the stripped binary: absolute (not relative) jumps, the stack-supplied rotate
amount, the feedback chaining on the _raw_ byte rather than the transformed one,
and not being lured into "explaining" the two dead opcodes or the decoy string.
Get any of those wrong and the inverse produces garbage that the binary rejects,
which is exactly the built-in check (`solve.py` runs the binary to confirm). So
it is a fair medium: mechanical once fully understood, unforgiving if rushed.

## Rebuild

```
make           # regenerates program.h via src/gen.py, builds ./vmcheck
make verify    # confirms no plaintext flag, runs the solver
```
