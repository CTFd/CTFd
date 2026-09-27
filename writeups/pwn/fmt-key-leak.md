<!-- nctf-meta category="pwn" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# fmt-key-leak

**One-line:** format-string leak of a per-run stack cookie, then echo it back.

## Vulnerability

The first line of input is used directly as a format string:

```c
printf(line); /* no "%s" */
```

A random 64-bit `cookie` is generated per run and stored on the stack. Because
`printf` walks its (missing) arguments off the stack, `%p` / `%lx` specifiers
disclose stack contents, including the cookie. The program then asks you to type
the cookie back; only on a match does `reveal()` XOR-decode the flag. Since the
cookie is randomised each run, a canned value is useless — the leak must be done
live in the same connection.

## Solve

1. Scan the stack with `%N$lx` to find where the cookie lands. For this binary
   (built `-O0 -no-pie`) it is at argument offset **25**.
2. Send `%25$lx` and parse the hex value.
3. Send that value as a decimal at the verification prompt.
4. `reveal()` prints the decoded flag.

Run: `python3 solution/solve.py`

## Flag

`NCTF{…}`
