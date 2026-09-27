<!-- nctf-meta category="reverse" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# java-cafe

**Category:** reverse · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

A compiled Java class builds the flag at runtime from a base64 string XORed with
a key, then compares it against your argument. Both constants live in the class
file's constant pool; decoding them recovers the flag.

## The technique

`javap -c -p Vault.class` (or a decompiler) shows:

```java
static final String B = "JCIiJxgLEAg1Aw8VUAIJAQ8+HxI8EwMEDgAUDQYc";
static final String K = "javacafe";

static byte[] unlock() {
    byte[] enc = Base64.getDecoder().decode(B);
    byte[] key = K.getBytes();
    for (int i = 0; i < enc.length; i++)
        out[i] = (byte)(enc[i] ^ key[i % key.length]);
    return out;
}
```

`main` only compares `unlock()` to `args[0]`, so the flag is never stored
directly (`grep byt3code_is_readable Vault.class` → 0 hits).

## Solve

```
flag = xor( base64_decode(B), K repeated )
```

The solver pulls the constant-pool strings straight out of the `.class`
(watching for the UTF-8 length byte that prefixes a string, e.g. `(` = 40),
tries each base64 run against each short key, and keeps the one that yields
`NCTF{…}`:

```
$ python3 solve.py ../Vault.class
key : javacafe
flag: NCTF{…}
```

Confirm against the class:

```
$ java -cp . Vault 'NCTF{…}'
=== java-cafe vault ===
[+] correct
```

## Rebuilding

```
make          # compile src/Vault.java -> ./Vault.class
make verify   # confirm no plaintext flag, then run the solver
```
