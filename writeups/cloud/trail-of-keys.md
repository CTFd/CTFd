<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# trail-of-keys

## TL;DR

Correlate the CloudTrail records: one assumed-role session (temporary key
`ASIA5EXFIL0SESSION07`) called `GetSecretValue` on the sensitive
`prod/customer-export` secret and then `PutObject`'d the notes file. The
exfiltrated object is XOR-sealed with `SHA256(that ASIA key)`; decrypt for the
flag.

## Technique

CloudTrail never logs secret values, so you reconstruct the exfiltration by
following identifiers across events:

- `AssumeRole` responses mint a temporary `ASIA...` access key
  (`responseElements.credentials.accessKeyId`).
- Subsequent API calls carry that key in `userIdentity.accessKeyId`.

Several sessions exist as noise (a backup writer, a metrics reader, and a decoy
that reads a harmless dev secret). Only one reads the sensitive secret **and**
writes the exfil object. That session's temporary key is the pivot.

## Attack

1. Scan for `GetSecretValue` where `secretId` contains `prod/customer-export`.
   The caller is `ASIA5EXFIL0SESSION07`.
2. Confirm the same key later `PutObject`'d `kekeli-scratch/tmp/notes.bin`.
3. `exfil-notes.json` holds that object, XOR-sealed with a keystream derived
   from `SHA256(ASIA5EXFIL0SESSION07)`. Recompute and decrypt.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../cloudtrail.json` — the event export.
- `../exfil-notes.json` — the sealed exfiltrated object.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
