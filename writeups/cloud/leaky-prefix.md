<!-- nctf-meta category="cloud" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# leaky-prefix

## TL;DR

The bucket policy's public `s3:GetObject` statement uses the resource prefix
`assets/public*` (the wildcard sits before the slash), so it also matches the
internal `assets/public-backup/` prefix. That backup object is world-readable
and holds the flag.

## Technique

Classic S3 bucket-policy prefix bug. The author wanted to expose only
`assets/public/*`:

```json
"Resource": "arn:aws:s3:::kekeli-media-prod/assets/public/*"
```

but shipped:

```json
"Resource": "arn:aws:s3:::kekeli-media-prod/assets/public*"
```

`assets/public*` is a prefix glob, so it matches `assets/public/logo.txt` and
also `assets/public-backup/db-snapshot-note.txt`.

## Attack

1. Parse `bucket-policy.json`. Collect every Allow statement with an anonymous
   `Principal: *` that grants `s3:GetObject`, and pull its `Resource` ARN
   pattern (relative to the bucket: `assets/public*`).
2. Match that glob against the keys in `object-index.json`. The unintended hit
   is `assets/public-backup/db-snapshot-note.txt`.
3. Read that object under `objects/`; the flag is in the body.

`objects/internal/old-ctf-note.txt` contains a decoy `NCTF{…}` string, but it
lives under a prefix no anonymous statement grants — not reachable.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../bucket-policy.json` — the live bucket policy (the bug).
- `../object-index.json` — object inventory.
- `../objects/` — object bodies.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
