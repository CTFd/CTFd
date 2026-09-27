<!-- nctf-meta category="ai" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# oracle-tool-args

**Summary:** Steer the `read_file` tool arg past a case-sensitive path
blocklist by re-casing the path; the store resolves it case-insensitively.

## Vulnerability

`_guard_ok` rejects a path only if it contains a blocked substring
(`flag`, `secret`, `vault`, `flag.enc`) matched case-sensitively. `_read`
normalises the path with `.lower()` before comparing against the file store. A
path like `Vault/Flag.enc` contains none of the lowercase blocked substrings, so
the guard passes it, but after normalisation it resolves to the protected file
`vault/flag.enc`.

## Steps

1. Read the source to learn the protected file name (`vault/flag.enc`).
2. Call `oracle.respond("read_file:Vault/Flag.enc")`.
3. The tool returns the file contents, which are the flag.

Run:

```
python3 solution/solve.py
```

## Flag

`NCTF{…}`
