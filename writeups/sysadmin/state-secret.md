<!-- nctf-meta category="sysadmin" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# state-secret

## TL;DR

`terraform.tfstate` stores the `random_password.vault.result` passphrase in
plaintext (Terraform state is never encrypted at rest by default). That
passphrase decrypts the shipped `vault.enc` blob to the flag.

## The misconfiguration

Terraform writes the full attribute set of every resource into state as
plaintext JSON. Attributes marked `sensitive` in HCL are only redacted in CLI
output — in the state file they are cleartext. Committing `terraform.tfstate`
(or storing it in an unencrypted backend) therefore leaks every generated
secret. Here the vault passphrase lives at
`resources[].instances[].attributes.result`. `main.tf` also carries a decoy
`aws` `secret_key` that is not the passphrase.

## The blob format

The encryptor itself, `encrypt.py`, is committed with the bundle (it is the
`data.external` program `main.tf` calls), and its header documents the format
exactly:

```
b"ENC1" + salt(16) + iters(4, big-endian) + ciphertext
key    = PBKDF2-HMAC-SHA256(passphrase, salt, iters)
stream = SHA256(key || counter)  for counter = 0, 1, 2, ...
plaintext = ciphertext XOR stream
```

So the format is not a guess — read `encrypt.py` and invert it (it even ships a
`decrypt()` helper).

## Attack

1. Parse `terraform.tfstate`; collect candidate string attributes.
2. For each candidate, derive the key from the blob's salt/iters and decrypt.
3. Keep the plaintext that starts with `NCTF{…}

```

## Files

- `../main.tf`, `../terraform.tfstate`, `../vault.enc` — the leaked bundle.
- `../encrypt.py` — the committed encryptor; documents/implements the blob format.
- `../src/gen.py` — deterministic builder.
- `solve.py` — reference solver (stdlib only).
```
