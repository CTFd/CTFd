<!-- nctf-meta category="reverse" difficulty="hard" points="500" author="challenge-team" stub="0" -->

# maze-vm

**Flag:** `NCTF{…}`

The only shipped artifact is `chall`, a native x86-64 Linux ELF. It embeds a
program for a bespoke stack+register VM. That program validates a 16-byte
passphrase; the accepted passphrase _is_ the inner flag text, printed back as
`NCTF{…}` on success.

## What the binary actually does

1. **Blob.** All challenge data lives in one `.rodata` blob prefixed with the
   magic `MZVMv1`. Layout:

   ```
   "MZVMv1\0\0"   xor_seed(u8) xor_mul(u8) plen(u8) prog_len(u16 LE)
   prog_obf[prog_len]   target[plen]
   ```

2. **Anti-analysis (light).** `prog_obf` is the bytecode under a rolling-XOR
   keystream. The binary decodes it in memory at startup:

   ```
   key = xor_seed
   for each stored byte o:  plain = o ^ key ;  key = (key*xor_mul + o) mod 256
   ```

   So the bytes at rest are not the bytes that execute. There are no debugger
   or timing tricks — everything is recoverable statically.

3. **The VM.** A byte-oriented stack machine with a 16-byte work array `st[]`
   and an input buffer, dispatched through a **threaded (computed-goto)** loop
   (`goto *table[prog[pc++]]`), not a switch. Opcodes used by the checker:

   | op   | mnemonic  | effect                                            |
   | ---- | --------- | ------------------------------------------------- |
   | 0x12 | `PUSHI k` | push immediate                                    |
   | 0x13 | `LDIN i`  | push `input[i]`                                   |
   | 0x14 | `LDST i`  | push `st[i]`                                      |
   | 0x15 | `STST i`  | `st[i] = pop`                                     |
   | 0x19 | `ADD`     | `(a+b) mod 256`                                   |
   | 0x1E | `MULMOD`  | `(a*b) mod 256` (modular multiply)                |
   | 0x1B | `XOR`     | `a ^ b`                                           |
   | 0x1F | `ROL n`   | rotate top-of-stack left by `n` bits              |
   | 0x21 | `PERM …`  | `st[i] = st[perm[i]]`, `perm` = next `plen` bytes |
   | 0x22 | `CMP`     | pop two; set fail flag if unequal                 |
   | 0x11 | `HALT`    | print flag if no failure, else `Denied.`          |

4. **The transform** (unrolled) is, per byte: add a constant, modular-multiply
   by an odd constant, XOR a constant, bit-rotate — then one whole-array
   **byte permutation** (the _only_ cross-byte mixing) — then another
   multiply/XOR/rotate round, then compare each byte to `target[i]`.

## Recovering the input

Because every arithmetic step is per-byte and the only cross-byte step is a
pure permutation, **each output byte depends on exactly one input byte**. So
the input is recovered without algebra: reimplement the VM, then for each of
the 16 input positions scan all 256 values and keep the one that makes its
output byte match `target` (16 × 256 evaluations).

`solve.py` does exactly this against the _lifted_ bytecode (no transform
constants hardcoded): it finds the blob, reproduces the keystream, interprets
the recovered program as a white-box oracle, recovers the input, and confirms
the real binary prints the flag.

## Run it

```
make            # regenerates program.h and builds ./chall
cd solution && python3 solve.py ../chall
# or, from the challenge root:
make verify     # checks no plaintext flag/passphrase, then runs the solver
```

Expected solver output:

```
[*] blob: plen=16 prog_len=530 seed=0x5a mul=0x1b  (306 instrs)
[*] recovered input : b'm4ze_vm_thr34d3d'
[*] binary output   : NCTF{…}
[+] FLAG: NCTF{…}
```
