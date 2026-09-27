<!-- nctf-meta category="cloud" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# sub-wildcard

## TL;DR

The `ci-deployer` trust policy gates the GitHub OIDC `sub` claim with
`StringLike "repo:kekeli-cloud/*"`, which admits any repo in the org — including
an attacker's fork. Several tokens were captured, but only the fork's token
satisfies that pattern; the rest are decoys. Pick the admitted token, assume the
role (which can read the release secret), and unseal the secret — it is sealed
with `SHA256(admitted sub)` — for the flag.

## Technique

GitHub Actions OIDC subjects look like
`repo:<owner>/<repo>:ref:refs/heads/<branch>`. A correct trust policy pins the
full subject (repo **and** ref). This one uses a `StringLike` wildcard:

```json
"token.actions.githubusercontent.com:sub": "repo:kekeli-cloud/*"
```

Any repository under `kekeli-cloud/` matches — so `kekeli-cloud/media-svc-fork`
(an attacker fork) can call `sts:AssumeRoleWithWebIdentity` and become
`ci-deployer`, which grants `secretsmanager:GetSecretValue` on the release
secret. `oidc-token.json` ships several captured tokens; the decoys use a
different org (`acme-corp/`), a hyphen-extended look-alike (`kekeli-cloud-staging/`),
a collapsed name (`kekelicloud/`), or a different path split (`kekeli/cloud-...`),
none of which match `repo:kekeli-cloud/*`.

## Attack

1. Read the `StringEquals` (`aud`) and `StringLike` (`sub`) conditions in
   `trust-policy.json`.
2. Evaluate each captured token in `oidc-token.json` against them. Exactly one
   (`repo:kekeli-cloud/media-svc-fork:...`) is admitted; the decoys fail.
3. Confirm `role-permissions.json` grants `secretsmanager:GetSecretValue` on the
   release secret — reachable once assumed.
4. The sealed `SecretStringCiphertextB64` is XORed with a keystream derived from
   `SHA256(admitted sub)`. Recompute and decrypt.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../trust-policy.json` — the OIDC trust policy (the wildcard bug).
- `../oidc-token.json` — several captured tokens; only one is admitted.
- `../role-permissions.json` — proves the secret is reachable once assumed.
- `../release-secret.json` — the sealed secret value.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
