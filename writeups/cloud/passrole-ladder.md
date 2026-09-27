<!-- nctf-meta category="cloud" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# passrole-ladder

## TL;DR

`mallory` can create/invoke Lambda functions and `iam:PassRole` two roles to
Lambda. Only `lambda-exec-role` is both passable by her, trusted by Lambda, and
able to read the production secret — so she creates a function with that role,
invokes it, and reads the secret. It is XOR-sealed with `SHA256(role ARN)`;
decrypt for the flag.

## Technique

The classic `iam:PassRole` + `lambda:CreateFunction` escalation. A user who can

- create and invoke Lambda functions, and
- pass a role to the Lambda service

gains all permissions of any role satisfying **all three** of:

1. it is in the user's `iam:PassRole` resource set,
2. its trust policy allows `lambda.amazonaws.com` to assume it, and
3. it holds the permission you want (here `secretsmanager:GetSecretValue` on the
   prod secret).

The dump ships two decoy roles: `break-glass-admin` can read the secret but is
not passable by mallory and does not trust Lambda; `lambda-logs-role` is
passable and trusts Lambda but can only write logs. Only `lambda-exec-role`
closes the loop.

## Attack

1. Resolve mallory's managed policies. Confirm `lambda:CreateFunction` and
   `lambda:InvokeFunction`, and collect her `iam:PassRole` resources.
2. For each role, test: passable ∧ trusts `lambda.amazonaws.com` ∧ its policy
   grants `GetSecretValue` on the secret ARN. Winner: `lambda-exec-role`.
3. `prod-secret.json` is XOR-sealed with a keystream from `SHA256(role ARN)`.
   Recompute and decrypt.

## Run

```
python3 solve.py
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../iam-users.json`, `../iam-roles.json`, `../iam-policies.json` — the IAM graph.
- `../prod-secret.json` — the sealed target secret.
- `../src/gen.py` — deterministic builder (not shipped).
- `solve.py` — reference solver (stdlib only).
