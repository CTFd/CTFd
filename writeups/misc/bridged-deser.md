<!-- nctf-meta category="misc" difficulty="medium" points="500" author="ctf-2026" stub="0" -->

# bridged-deser

**Category** misc · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**SSRF → internal RPC → unsafe deserialization → gadget.** The server-side `/fetch` has no target allow-list, so it reaches the internal-only RPC, which deserializes its body into a registry class with no allow-list — including the debug `FlagDumper` gadget.

## Intended path

1. `GET /fetch?url=/internal/rpc&body=<json {"__class__":"__x__"}>` leaks the registry.
2. `GET /fetch?url=/internal/rpc&body=<json {"__class__":"FlagDumper"}>` → `result` is the per-team flag.

`/flag.txt` is served by no route; it only appears through the exploit above.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the exploit
reads _this_ instance's secret at solve time, so a flag from another team is
useless.

> Variante de la classe `ingestd-deser` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the exploit path runs and the service returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
