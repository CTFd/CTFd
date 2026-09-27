<!-- nctf-meta category="cloud" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# imds-ssrf

## TL;DR

The SSRF capture shows an IMDSv2 walk to
`/latest/meta-data/iam/security-credentials/media-transcoder-role`, whose
response contains the role's temporary `SecretAccessKey`. The operator note is
XOR-sealed with `SHA256(SecretAccessKey)`; decrypt for the flag.

## Technique

A server-side request forgery in the preview service let the attacker fetch
`http://169.254.169.254/...`. IMDSv2 requires a session token, so the capture
first `PUT`s `/latest/api/token`, then reuses it as
`X-aws-ec2-metadata-token` to enumerate the role and read its credential
document (`AccessKeyId` / `SecretAccessKey` / `Token`).

The recovered note was encrypted with a keystream derived from that
`SecretAccessKey`, so parsing the capture is what unlocks it.

## Attack

1. In `ssrf-capture.log`, read the final credential JSON and extract
   `SecretAccessKey`.
2. `notes.enc` is base64 of the note ciphertext, XORed with a keystream from
   `SHA256(SecretAccessKey)`. Recompute and decrypt.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../ssrf-capture.log` — the SSRF/IMDS proxy capture (fake dev creds).
- `../notes.enc` — the sealed operator note.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
