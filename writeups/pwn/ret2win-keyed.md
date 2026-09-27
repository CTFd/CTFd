<!-- nctf-meta category="pwn" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# ret2win-keyed

**One-line:** ret2win that only pays out if you pass the right argument in RDI.

## Vulnerability

`vuln()` overflows a 64-byte stack buffer (`read(0, buf, 256)`), and there is no
canary and no PIE. But the reveal function takes an argument:

```c
void reveal(unsigned long k) {
    if (k != token) { puts("wrong key"); return; }
    /* XOR-decode + print flag */
}
```

`token` is random per run and printed once at startup. Jumping straight to
`reveal()` leaves RDI uncontrolled, so the check fails. Under the System-V
AMD64 ABI the first integer argument is in RDI, so the exploit must load the
token into RDI before entering `reveal()`. The binary ships a `pop rdi; ret`
gadget (symbol `gadget_pop_rdi`) for exactly this.

## Solve

1. Read the printed `token: 0x...`.
2. `buf` is at `rbp-0x40`; the return address is `0x40 + 8 = 72` bytes in.
3. Chain: `b"A"*72 + p64(pop_rdi) + p64(token) + p64(reveal)`.
4. `reveal()` sees `k == token`, decodes and prints the flag.

Run: `python3 solution/solve.py`

## Flag

`NCTF{…}`
