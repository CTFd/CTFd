<!-- nctf-meta category="cloud" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# sas-forge

## TL;DR

An Azure Storage account key is the master signing key for Service SAS tokens. A
SAS `sig` is `base64(HMAC-SHA256(accountKey, StringToSign))` computed entirely
offline. Forge the signature for the private `RELEASE_NOTES.enc` blob; the blob
is XOR-sealed with `SHA256(that sig)`, so the forged signature decrypts it.

## Technique

The Azure Service SAS (signed version `2020-12-06`) signs a newline-joined
StringToSign:

```
sp \n st \n se \n canonicalizedResource \n si \n sip \n spr \n sv \n sr \n
sst \n ses \n rscc \n rscd \n rsce \n rscl \n rsct
```

where `canonicalizedResource = /blob/<account>/<container>/<blob>`. The key is
the account key, base64-decoded to raw bytes. Because the account key leaked,
anyone can mint a valid read SAS for **any** blob — no Azure round-trip, no
authorization check.

## Attack

1. Read the account key from `leaked-account-key.txt` and the SAS fields from
   `sas-params.json` (`sas-example.txt` shows the query-parameter scheme).
2. Build the StringToSign in the exact field order above, with
   `canonicalizedResource = /blob/kekelistorage/private-releases/media-svc/RELEASE_NOTES.enc`.
3. `sig = base64(HMAC_SHA256(base64decode(account_key), StringToSign))`.
4. `flag-blob.enc` is XOR-sealed with a keystream from `SHA256(sig)`. Recompute
   and decrypt.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../leaked-account-key.txt` — the leaked account key (obviously fake dev key).
- `../sas-example.txt` — a sample SAS URL (reveals the parameter names).
- `../blob-index.json` — container/blob inventory.
- `../sas-params.json` — the SAS fields to sign for the target blob.
- `../flag-blob.enc` — the sealed private blob.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
