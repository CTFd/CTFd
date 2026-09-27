<!-- nctf-meta category="supplychain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# provenance-forgery

A weak, homemade provenance signature scheme with a leaked key lets you verify
every attestation offline and spot the forged release.

## Vulnerability

Provenance is signed as `sig = sha256(KEY || 0x0a || subject.sha256)`. The key
is leaked in `ci-signing.key`, so signatures are trivially verifiable (and
forgeable). The `1.2.0` release was not built by the real pipeline: its
provenance signature is invalid and its recorded digest does not match the
shipped artifact. That artifact carries the flag.

## Solve

1. Read `SIGNING_KEY` from `ci-signing.key`.
2. For each provenance statement, recompute the shipped artifact's sha256 and
   the expected signature. `1.2.0` fails both checks.
3. Extract `dist/app.js` from `acme-app-1.2.0.tgz`; its `_t` value is
   base64(flag). Decode it.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
