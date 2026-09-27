<!-- nctf-meta category="reverse" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# shell-lock

**Category:** reverse · **Difficulty:** easy
**Flag:** `NCTF{…}`
**Password:** `sh3ll_w1zard`

## Summary

An obfuscated POSIX shell script gates on a password it reconstructs at runtime,
then XOR-decrypts the flag. Both the password and the flag are stored encoded;
peeling the two encodings recovers everything.

## The technique

The script has two data lines:

```sh
_k=5942194646755d1b504b584e
_b=PStnKhcsHwIWDS0XFgRVMwhsFEMDEQY7Aw0AAAk7Cg==
```

The first `perl` pipeline turns `_k` into the password:

```
password[j] = hexbyte(_k, j) ^ 0x2A
```

which gives `sh3ll_w1zard`. After the `[ "$1" = "$_p" ]` gate, `_b` is
base64-decoded and XORed with the password (repeated) to print the flag. No
plaintext flag or password is in the file.

## Solve

Reproduce both steps:

1. de-XOR the hex string `_k` with `0x2A` → password
2. base64-decode `_b`, XOR with the password → flag

```
$ python3 solve.py ../lock.sh
password: sh3ll_w1zard
flag    : NCTF{…}
```

Or run the script with the recovered password:

```
$ sh lock.sh sh3ll_w1zard
NCTF{…}
```

## Rebuilding

```
make          # regenerate ./lock.sh
make verify   # confirm no plaintext secrets, then run the solver
```
