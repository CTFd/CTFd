<!-- nctf-meta category="web" difficulty="hard" points="450" author="ctf-2026" stub="0" -->

# webhook-relay

**Category** web · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability chain

**Webhook URL validation bypass → SSRF → internal metadata.** The callback validator only checks that the URL _contains_ the partner host, so a fragment/userinfo trick keeps the string while pointing at the internal metadata host.

## Intended path

1. `GET /webhook/deliver?url=http://169.254.169.254/latest/meta-data/flag%23hooks.partner.example`.
2. The `response` is the per-team flag.

The running service is the oracle; nothing here is downloadable. `/flag.txt` is
emitted only through the exploit above.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the flag is
emitted only after the server verifies the effect on _this_ instance, so a flag
from another team is useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the exploit path runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
