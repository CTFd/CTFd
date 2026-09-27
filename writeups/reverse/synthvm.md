<!-- nctf-meta category="reverse" difficulty="hard" points="500" author="challenge-team" stub="0" -->

# synthvm

**Flag:** `NCTF{…}`

## TL;DR

`synthvm` embeds a bespoke ~80-opcode register+stack bytecode machine and a
fully-unrolled ~6164-instruction program. The program reads your input, runs it
through 17 mixing rounds (add-carry, an invented S-box, a byte rotate, a
per-position XOR), and compares the result to an embedded target `T[]`. The
accepted input _is_ the flag. To solve you must (a) recover the runtime opcode
remap, (b) work out the custom varint, (c) disassemble the program, (d)
understand the round function, and (e) invert it. `solve.py` does all of this
from the ELF and verifies against the binary.

## 1. Recon

```
$ file synthvm
synthvm: ELF 64-bit LSB pie executable, x86-64, ... stripped
$ strings synthvm | grep -i CTF
(nothing)
$ ./synthvm <<<'AAAA'
Denied
```

No flag string. The only human-readable output is `Access granted` / `Denied`.
So this is a keygen: find the input that yields `Access granted`.

## 2. Find and understand the interpreter

In a disassembler the core is a classic fetch/decode/dispatch loop: read a byte
from a large `.rodata` array via a program counter, index a 256-entry table with
it, and jump into a huge `switch`. That shape is a bytecode VM.

Two twists you must nail before anything else:

### 2a. The dispatch is remapped at runtime

`init` calls a routine that fills a 256-byte table (`opmap`) using a keyed
Fisher-Yates shuffle driven by a xorshift32 PRNG seeded with a constant
(`OP_SEED = 0x1F3D5B79`). Every fetched program byte is routed through this
table: `internal_op = opmap[raw_byte]`. So the `case` labels in the `switch` are
the _internal_ opcode numbers, but the bytes in the program are the _permuted_
values. Reading the switch statically without applying the permutation gives you
nonsense.

Recover it two ways:

- **Reimplement:** read the seed and the shuffle out of the init routine and
  rebuild the permutation (what `solve.py` does), or
- **Trace:** set a breakpoint after `init` and dump the 256-byte table.

xorshift32 used here:

```c
x ^= x<<13; x ^= x>>17; x ^= x<<5;
```

Fisher-Yates: `for i in 255..1: st=xs32(st); j=st%(i+1); swap(arr[i],arr[j])`
starting from the identity.

### 2b. The immediate encoding is a custom varint

Immediates are a little-endian base-128 varint, **but the continuation flag is
the LOW bit**, and the 7 payload bits are the HIGH bits of each byte:

```
value |= (byte >> 1) << shift; shift += 7; stop when (byte & 1) == 0
```

This is deliberately not LEB128 (whose continuation flag is the MSB). If you
assume LEB128 your operands are wrong.

### 2c. The ISA

80 opcodes; the ones the program actually uses:

| op        | format         | effect                                       |
| --------- | -------------- | -------------------------------------------- |
| MOVI      | reg, imm       | reg = imm                                    |
| IN        | reg            | reg = next input byte, or 0x100 at EOF       |
| CMPI      | reg, imm       | set compare operands (reg, imm)              |
| JZ/JNZ    | addr           | branch to ABSOLUTE program offset on ==/!=   |
| ANDI/XORI | reg, imm       | reg &= / ^= imm                              |
| ADD/MOV   | reg, reg       | reg op= reg                                  |
| LDB/STB   | reg,[base+off] | byte load/store into data RAM                |
| SBOX      | reg, reg       | reg = sbox[reg & 0xff] (built-in bijection)  |
| ROL8      | reg, imm       | rotate the low byte of reg left by (imm & 7) |
| OUT       | reg            | putchar                                      |
| HALT      | -              | stop                                         |

Operand packing: register operands are nibbles (`dst = b>>4`, `src = b&0xf`);
memory ops pack `dst`/`base` in the two nibbles then a varint offset; branch
targets are a fixed 3-byte varint holding an absolute program offset.

The built-in `SBOX` is a second full 8-bit permutation, built by the same
Fisher-Yates with `SBOX_SEED = 0xC0FFEE42`. Recover it the same way (rebuild or
dump the 256-byte table).

## 3. Lift the program

Disassemble linearly from the program start. The structure is:

```
MOVI r14, 0x100              ; r14 = input buffer base in data RAM
; read L bytes:
  IN r2 ; CMPI r2,0x100 ; JZ reject ; ANDI r2,0xff ; STB r2,[r14+i]   (x L)
; 17 rounds, each:
  MOVI r6, IV_r                                   ; carry seed
  for i in 0..L-1:
    LDB r1,[r14+i]
    ADD r1, r6
    ANDI r1, 0xff
    SBOX r1, r1
    ROL8 r1, rot_r
    XORI r1, c_{r,i}
    STB r1,[r14+i]
    MOV r6, r1                                     ; carry chains on OUTPUT
; compare:
  for i in 0..L-1: LDB r1,[r14+i] ; CMPI r1, T[i] ; JNZ reject
; success: print "Access granted"
```

So `L = 41` (count the `IN`s) and `R = 17` (count the `MOVI r6`s). The
parameters are all sitting in the disassembly:

- `IV_r` = the `MOVI r6, imm` immediate at the top of each round,
- `rot_r` = the `ROL8 r1, imm` immediate (constant within a round),
- `c_{r,i}`= the `XORI r1, imm` immediates in order,
- `T[i]` = the `CMPI r1, imm` immediates in the compare loop.

## 4. The round function and its inverse

Forward, per round `r`, with `carry = IV_r` at `i = 0`:

```
out = ROL8( SBOX[ (in + carry) & 0xff ], rot_r ) ^ c_{r,i}
carry = out            # feedback uses the OUTPUT byte
```

This is invertible left-to-right because the carry at position `i` is the
_previous output_, which we know (it is this round's output array, i.e. the next
round's input):

```
t = out ^ c_{r,i}
t = ROR8(t, rot_r)
t = ISBOX[t]
carry = IV_r if i==0 else out[i-1]
in = (t - carry) & 0xff
```

Invert round 16 down to round 0 starting from `T[]` and you get the original
input.

## 5. Solve

`solve.py` does exactly the above straight off the ELF: rebuild `opmap` and the
S-box from the seeds, find `PROG` by its first instruction, disassemble with the
custom varint, read `IV/rot/c/T` out of the instruction stream, invert, and
verify against the binary.

```
$ python3 solve.py ../synthvm
[*] PROG @ file offset 0x2260
[*] L=41 rounds=17
[*] recovered flag: NCTF{…}
[*] binary says: Access granted => OK
```

## 6. The decoy

After the real check and its `HALT`s there is an unreferenced block that XORs the
buffer with `0x5A` and compares to a different table which inverts to
`NCTF{…}`. Nothing branches to it - it is dead
code. Build the control-flow graph (or just notice the two `HALT`s and that no
`J*`/`CALL` targets its address) and it is refuted in a minute. It costs no
attempt if you check reachability before submitting.

## 7. Honest note on what an LLM does here

An LLM is genuinely useful for the _mechanical_ sub-tasks: recognising the
fetch/dispatch loop, reimplementing xorshift32 + Fisher-Yates once the seed is
pointed out, spotting that the varint continuation bit is the LSB, and writing
the inversion once the round function is stated. Where it struggles, and why this
resists one-shot prompting:

- The static disassembly is a **trap** until the dispatch permutation is applied.
  A model that reads the `switch` and maps program bytes to those cases directly
  produces a wrong lift and confidently reasons from it. You must realise the
  bytes are remapped and reconstruct the table first - there is no shortcut that
  falls out of pattern-matching the binary.
- The program is ~6000 unrolled instructions with per-position constants; there
  is no small loop to summarise. You must actually lift it and extract 17x41 XOR
  constants, 17 rotates, 17 carry seeds and 41 target bytes programmatically. A
  model that "eyeballs" it will get constants wrong.
- Getting the carry-feedback direction wrong (chaining on input vs output) yields
  a clean-looking but incorrect inversion, so the math has to be reasoned, not
  guessed.

Feeding the whole binary to a model and asking for the flag does not work; you
need the disassembler + the correct remap + the correct varint + the correct
inversion, i.e. the intended tool-building path. Playtest target 2-4h.
