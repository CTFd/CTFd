<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# gcp-token-scope

## TL;DR

The CI helper service account is granted `roles/storage.objectViewer` at the
**project** level, so a token minted from its leaked key can read every bucket —
including the private `kekeli-prod-artifacts` bucket. Its `RELEASE_TOKEN.enc`
object is XOR-sealed with `SHA256(private_key_id)`; decrypt for the flag.

## Technique

The intended grant was a bucket-scoped IAM binding on the CI cache bucket. The
policy instead binds `roles/storage.objectViewer` to
`serviceAccount:ci-helper@...` in the project IAM policy, which applies to all
buckets in the project. Any OAuth token minted from `sa-key.json` inherits that
scope, so the private artifacts bucket is readable.

## Attack

1. In `iam-policy.json`, find the binding whose `members` include the SA's
   `client_email` from `sa-key.json`. It is project-wide `objectViewer`.
2. In `bucket-listing.json`, the private `kekeli-prod-artifacts` bucket holds
   `releases/RELEASE_TOKEN.enc` — now reachable.
3. `release-token.json` ships that object, XOR-sealed with a keystream from
   `SHA256(sa-key.private_key_id)`. Recompute and decrypt.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../sa-key.json` — leaked SA key (obviously fake dev PEM).
- `../iam-policy.json` — the over-broad binding.
- `../bucket-listing.json` — bucket inventory.
- `../release-token.json` — the sealed private object.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
