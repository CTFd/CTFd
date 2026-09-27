<!-- nctf-meta category="supplychain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# pip-postinstall-hook

A malicious Python sdist runs code at install time through a custom
`cmdclass` install command, with the payload lightly obfuscated.

## Vulnerability

`setup.py` defines a `PostInstall(install)` command whose `run()` executes a
payload reconstructed from `_B` (a hex string) XOR'd byte-by-byte with `_K`.
Both values are embedded in `setup.py`, so the payload is recoverable
statically without ever running the installer.

## Solve

1. Extract `setup.py` from `acme-license-check-1.0.0.tar.gz`.
2. Read the constants `_K` (key) and `_B` (hex blob).
3. `bytes.fromhex(_B)`, then XOR each byte with `_K`, and decode to text.
4. The reconstructed source writes the flag to `~/.acme_licence`.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
