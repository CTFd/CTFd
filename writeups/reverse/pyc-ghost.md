<!-- nctf-meta category="reverse" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# pyc-ghost

**Category:** reverse · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

The artifact is a marshalled CPython `.pyc`. The flag is never stored — it is
rebuilt from a data array XORed with an LCG keystream. Unmarshal the bytecode,
recover the routine, and run it.

## The technique

`grep NCTF{…}

```

Confirm against the module:

```

$ echo 'NCTF{…}' | python3 vault.pyc
flag? [+] correct

```

## Rebuilding

```

make # compile src/vault.py -> ./vault.pyc
make verify # confirm no plaintext flag, then run the solver

```

The `.pyc` is CPython-3.11 bytecode. `src/vault.py` and `src/gen.py` are
developer-only and are not shipped.
```
