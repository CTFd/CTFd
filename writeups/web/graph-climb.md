<!-- nctf-meta category="web" difficulty="hard" points="450" author="ctf-2026" stub="0" -->

# graph-climb

**Category** web · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability chain

A homegrown GraphQL-style API with three chained flaws:

1. **Introspection enabled** — `{ __schema { ... } }` reveals the `updateUser`
   mutation and the role-gated `viewer.flag` field.
2. **IDOR** — `user(id)` returns any account with no authorization check (you can
   read the `admin` account, id 1, and learn the `role` field exists).
3. **Mass-assignment** — `updateUser(id, patch)` writes _every_ field in `patch`,
   including `role`, with no allow-list. Promote your own viewer (id 1000).

The `viewer.flag` field returns the per-team flag only when your role is `admin`.

## Intended path

```
POST /graphql   (header: X-Session: anything)
{ __schema { queryType } }                                      # introspect
mutation { updateUser(id: 1000, patch: {"role": "admin"}) { role } }   # mass-assign
{ viewer { role flag } }                                        # -> NCTF{…}
```

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact. The chain must
be executed against _this_ instance (introspect → promote → read); a flag from
another team's instance is worthless. Each step is a distinct authorization flaw,
so it rewards understanding the API rather than pattern-matching one payload.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): fresh guest sees `role=user` and `flag=<admin only>`; IDOR reads the admin
account; after the mass-assignment promotion `viewer { flag }` returns the exact
per-team flag. **Docker/Lot-5 rehearsal is the remaining gate before
`state: visible`.**
