<!-- nctf-meta category="chains" difficulty="hard" points="500" author="ctf-2026" stub="0" -->

# relay

**Category** chains · **Served** yes (per-team flag) · multi-stage

## Vulnerability chain

**Reverse a homemade TLV protocol → echo over-read (OOB) leaks the secret.** The echo op copies `length` bytes from a buffer holding the value then the secret; a declared length larger than the value over-reads into the secret.

## Intended path

1. Reverse the TLV framing from `/` (type, length, value).
2. `POST /cmd {packet:'02ff41'}` (echo, length 0xff, 1-byte value) → the response leaks the per-team flag.

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
