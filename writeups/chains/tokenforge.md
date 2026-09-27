<!-- nctf-meta category="chains" difficulty="hard" points="500" author="ctf-2026" stub="0" -->

# tokenforge

**Category** chains · **Served** yes (per-team flag) · multi-stage

## Vulnerability chain

**Stream-cipher keystream reuse → forged admin cookie → hidden deserialization.** The cookie is `role=guest` XOR a reused keystream; known plaintext recovers the keystream and forges `role=admin`. The admin-only `/console` then deserializes an object with no allow-list (FlagDumper gadget).

## Intended path

1. `GET /login` → guest cookie; recover keystream via known plaintext `role=guest`.
2. Forge `role=admin` (same length).
3. `POST /console {cookie, obj:{__class__:FlagDumper}}` → the per-team flag.

Each stage's unlock is an effect of the previous one. `/flag.txt` is served by no
route; it only appears at the end of the chain.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; every stage
runs against _this_ instance and the flag is read from its filesystem at solve
time, so a flag from another team is useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the full chain runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
