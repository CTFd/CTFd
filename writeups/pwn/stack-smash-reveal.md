<!-- nctf-meta category="pwn" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# stack-smash-reveal

**One-line:** classic `ret2win` — overflow a stack buffer to return into `win()`.

## Vulnerability

`vuln()` reads 256 bytes into a 64-byte stack buffer:

```c
char buf[64];
read(0, buf, 256);
```

The binary is built with **no stack canary** and **no PIE** (`-fno-stack-protector
-no-pie`), so the saved return address is at a fixed, unprotected offset and
`win()` lives at a fixed address. `win()` is never called on the normal path; it
XOR-decodes the embedded flag (with a compile-time `KEY`) and writes it out, so
the flag is not present in cleartext in the binary.

## Solve

1. `buf` is at `rbp-0x40`, so the return address is `0x40 + 8 = 72` bytes in.
2. Build `b"A"*72 + p64(ret_gadget) + p64(win)`. The extra `ret` keeps the stack
   16-byte aligned before `win()` executes.
3. Send it; `win()` prints the decoded flag.

Run: `python3 solution/solve.py`

## Flag

`NCTF{…}`
