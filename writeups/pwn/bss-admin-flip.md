<!-- nctf-meta category="pwn" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# bss-admin-flip

**One-line:** overflow a global buffer into an adjacent `is_admin` flag.

## Vulnerability

The program keeps its state in one global struct that lives in `.bss`:

```c
struct account {
    char name[64];
    volatile long is_admin;
};
```

`is_admin` sits immediately after the 64-byte `name`. Input is read with:

```c
read(0, user.name, 128); /* name is only 64 bytes */
```

So 64 filler bytes fill `name` and the next bytes land directly in `is_admin`.
When `is_admin` is non-zero the program calls `reveal()`, which XOR-decodes the
embedded flag (compile-time `KEY`) — the flag is never stored in cleartext.

## Solve

1. Send `b"A"*64` to fill `name`.
2. Append any non-zero 8-byte value to set `is_admin`.
3. The program prints `welcome, admin.` and then the decoded flag.

Run: `python3 solution/solve.py`

## Flag

`NCTF{…}`
