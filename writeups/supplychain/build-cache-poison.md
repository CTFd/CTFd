<!-- nctf-meta category="supplychain" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# build-cache-poison

One vendored dependency is fetched into the build cache with no checksum
verification, and that entry has been poisoned.

## Vulnerability

The Makefile fetches four artifacts. Three run `sha256sum -c checksums.sha256`
after downloading; `libnet-0.9.tar.gz` is pulled from a different mirror with
no verification step. That cache entry carries the flag as
`base64(XOR(flag, XOR_KEY))`, where `XOR_KEY` is declared at the top of the
Makefile.

## Solve

1. Parse the Makefile recipes. Find the `vendor-cache/…` target whose recipe
   has no `sha256sum`: `libnet-0.9.tar.gz`.
2. Read `XOR_KEY` from the Makefile.
3. Extract the payload (`build.env`) from that tarball; `BUILD_TOKEN=` is
   base64. base64-decode, then XOR each byte with `XOR_KEY`.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
