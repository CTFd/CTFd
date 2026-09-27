<!-- nctf-meta category="supplychain" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# sbom-component-swap

Cross-referencing a CycloneDX SBOM against a known-bad hash feed pinpoints the
compromised component.

## Vulnerability

The SBOM lists four components, each with a SHA-256 and a shipped blob. The
SOC advisory `known-bad-hashes.txt` contains the hash of the `acme-updater`
blob, flagging it as a backdoored artifact.

## Solve

1. Parse `bom.json` and the advisory feed.
2. Find the component whose SHA-256 appears in the feed: `acme-updater`.
3. Follow its `blob` property to `component-acme-updater.bin`.
4. Its `cfg` value is base64(flag). Decode it.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
