<!-- nctf-meta category="web" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# mass-assignment

**Summary:** `PATCH /api/me` merges the whole request body into the user record
with no field allowlist, so sending `{"is_admin": true, "role": "admin"}`
promotes the member. The flag endpoint keys its unseal on exactly that
privileged assignment, so crafting the right mass-assignment request is what
produces the key.

## Vulnerability

`update_me()` does `user.update(body)` on the parsed JSON. Any field in the
body -- including the privileged `is_admin` and `role` fields that gate
`/api/me/flag` -- is written straight onto the record. The captured request
(`capture.http`) shows the endpoint accepting an arbitrary body and echoing the
merged record (a plain `member`, `is_admin: false`), confirming the behaviour.

`/api/me/flag` requires `is_admin == true` **and** `role == "admin"`, then
derives the seal key from the canonical JSON of that assignment
(`{"is_admin":true,"role":"admin"}`) and XOR-unseals `SEALED_FLAG_HEX`. There is
no standalone constant key: setting only one of the two fields fails the gate or
derives the wrong key.

## Steps

1. Load the shipped member from `users.json` (`role: member`, `is_admin:
false`).
2. Apply the mass-assignment merge with `{"is_admin": true, "role": "admin"}`.
3. Re-run the admin check, rebuild the canonical assignment, and reproduce the
   unseal.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
