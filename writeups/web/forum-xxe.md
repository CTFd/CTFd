<!-- nctf-meta category="web" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# forum-xxe

**Category** web · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**XXE → SSRF / internal file read.** The importer resolves external SYSTEM entities (file:// and the internal metadata host), so a file:// entity reads the root flag.

## Intended path

1. `POST /import` an XML doc declaring `<!ENTITY x SYSTEM "file:///flag.txt">` and referencing `&x;`.
2. The `parsed` field contains the per-team flag.

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
