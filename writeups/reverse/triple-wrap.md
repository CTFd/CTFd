<!-- nctf-meta category="reverse" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# triple-wrap

**Category:** reverse · **Difficulty:** easy
**Flag:** `NCTF{…}`
**Decoy:** `NCTF{…}`

## Summary

The flag is embedded as a base64 blob that is three transform layers deep. The
binary unwraps it at runtime to compare against your input; peeling the layers
by hand recovers the flag.

## The technique

`strings chall | grep NCTF{…}`:

```
$ python3 solve.py ../chall
key : wrapkey
flag: NCTF{…}
```

Check against the binary:

```
$ ./chall 'NCTF{…}'
[+] correct!
```

## Rebuilding

```
make          # regenerate src/chall.c and compile ./chall
make verify   # confirm strings shows only the decoy, then run the solver
```
