<!-- nctf-meta category="reverse" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# stack-vm

**Category:** reverse · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

The key check runs inside a tiny embedded bytecode VM. Disassembling the program
gives an invertible per-byte transform; inverting the target array yields the
key, and the flag is a second array XORed with that key.

## The VM

The binary carries a bytecode program `prog` and interprets it once per input
byte (accumulator = the byte, plus a position register). Opcodes:

```
0x01 XOR imm   0x02 ADD imm   0x03 SUB imm
0x04 ROL imm   0x05 ROR imm   0x06 XORI (acc ^= i)   0xFF HALT
```

The embedded program disassembles to:

```
XOR 0x3D ; ADD 0x11 ; ROL 3 ; XORI ; SUB 0x07 ; ROR 2 ; HALT
```

so at position `i`:

```
y = ROR8( ((ROL8(((x ^ 0x3D) + 0x11) & 0xFF, 3) ^ i) - 0x07) & 0xFF, 2 )
```

`check()` compares `y` to `target[i]`.

## Solve

Every op is invertible, so run the program backwards to turn each `target[i]`
into `key[i]`:

```
acc = target[i]
acc = ROL8(acc, 2)          # inverse ROR 2
acc = (acc + 0x07) & 0xFF   # inverse SUB
acc ^= i                    # inverse XORI
acc = ROR8(acc, 3)          # inverse ROL 3
acc = (acc - 0x11) & 0xFF   # inverse ADD
acc ^= 0x3D                 # inverse XOR
key[i] = acc
```

The recovered key is `tr4ce_th3_vm_ops!`. The flag is `flag_enc[i] ^ key[i %
keylen]`. The solver slides over the file, inverts each window to a candidate
key, and keeps the one that decrypts another window to `NCTF{…}` — no
hardcoded offsets or answer:

```
$ python3 solve.py ../chall
key : tr4ce_th3_vm_ops!
flag: NCTF{…}
```

Or feed the key back to the binary:

```
$ ./chall 'tr4ce_th3_vm_ops!'
[+] key accepted. flag: NCTF{…}
```

## Rebuilding

```
make          # regenerate src/chall.c and compile ./chall
make verify   # confirm no plaintext flag, then run the solver
```
