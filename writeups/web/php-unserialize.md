<!-- nctf-meta category="web" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# php-unserialize

**Summary:** The portal calls `unserialize()` on the attacker-controlled cookie
with no class allowlist, so you can inject a `FlagReveal` object whose
`__wakeup()` decrypts and prints the flag.

## Vulnerability

`index.php` deserializes `base64_decode($_COOKIE["sess"])` directly. PHP will
instantiate any in-scope class named in the payload and run its magic methods.
`FlagReveal::__wakeup()` runs the moment such an object is deserialized and
echoes the flag, which it decrypts from a sealed hex blob using a keystream of
`md5($seed . ":" . block)` over 16-byte blocks.

The needed `$seed` is the maintenance seed hardcoded at the top of the file.

## Steps

1. Confirm the captured cookie is a plain guest `Session`.
2. Object injection: craft `O:10:"FlagReveal":1:{s:4:"seed";s:N:"<seed>";}`,
   base64 it -- that is the cookie you would send.
3. Reproduce `__wakeup()`: XOR the sealed bytes against the md5 block keystream
   keyed on the leaked seed.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
