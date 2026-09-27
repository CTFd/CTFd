<!-- nctf-meta category="pwn" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# off-by-one-auth

**One-line:** a `<=` in a read loop writes one byte past the buffer, onto an
`authorized` flag.

## Vulnerability

Input goes into a stack struct:

```c
struct frame {
    char buf[32];
    volatile unsigned long authorized;
};
```

The read loop is off by one:

```c
for (int i = 0; i <= n; i++)   /* should be i < n */
    s.buf[i] = getchar();
```

The length is validated as `0 <= n <= 32`. At the maximum, `n == 32`, the loop
writes indices `0..32` — index `32` is one past the 32-byte `buf` and lands on
the low byte of `authorized`. `authorized` starts at 0; any non-zero byte there
unlocks `reveal()`, which XOR-decodes the embedded flag (never stored in
cleartext).

## Solve

1. Answer the length prompt with `32` (the maximum the check allows).
2. Send 33 bytes. The 33rd byte is written to `authorized`'s low byte.
3. Any non-zero value works; the program prints `authorized.` then the flag.

Run: `python3 solution/solve.py`

## Flag

`NCTF{…}`
