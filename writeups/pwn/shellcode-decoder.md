<!-- nctf-meta category="pwn" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# shellcode-decoder

**One-line:** the program runs your shellcode in an RWX buffer; write shellcode
that decodes the in-memory flag section.

## Vulnerability (by design)

The program `mmap`s a `PROT_READ|PROT_WRITE|PROT_EXEC` buffer, reads your bytes
into it, and calls it. Arbitrary code execution is the intended primitive.

The flag section is protected against a lazy static solve: at startup the
program masks it with a random byte `r`, storing `enc = flag ^ K ^ r`, and keeps
`dkey = K ^ r` in a global. So `flag = enc ^ dkey`, but `dkey` only takes its
real value at runtime — XORing the file's bytes with `K` will not reveal the
flag. Only code running inside the process can read the live `dkey`.

## Solve

Both `enc` and `dkey` are globals at fixed addresses (no PIE); the program also
prints them for convenience. Write shellcode that:

1. Loads `dkey` and `enc`'s address.
2. XORs each of `enc_len` bytes of `enc` with `dkey` in place (recovering flag).
3. `write(1, enc, enc_len)` then `exit(0)`.

The solver reads the addresses and `enc_len` straight from the ELF symbols,
assembles this shellcode with pwntools, and sends it.

Run: `python3 solution/solve.py`

## Flag

`NCTF{…}`
