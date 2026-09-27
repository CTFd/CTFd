<!-- nctf-meta category="web" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# forum-protopoll

**Category** web · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Prototype-pollution-style merge → render-hook gadget.** `/settings` deep-merges user JSON into a shared config with no key allow-list, so a merge sets the `render_hook` gadget the renderer runs.

## Intended path

1. `POST /settings {"render_hook":"emit-flag"}`.
2. `GET /render` → `hook_output` is the per-team flag.

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
