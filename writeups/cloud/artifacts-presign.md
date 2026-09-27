<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="ctf-2026" stub="0" -->

# artifacts-presign

**Category** cloud · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Presigned-URL abuse → privileged object write → deploy-time reveal.** The
`/presign` issuer is documented to sign PUT URLs only for the `uploads/` prefix,
but it never enforces that prefix — it signs any key it is handed. Signing a PUT
for the privileged `hooks/postdeploy` object lets the attacker plant a hook the
deploy worker trusts; running `/deploy` then publishes the flag into a readable
artifact.

## Intended path

1. `GET /presign?key=hooks/postdeploy` → a signed `/put?...` URL for a key the
   issuer should have refused.
2. `PUT <that url>` with body `emit-flag` → writes the trusted hook.
3. `GET /deploy` → the post-deploy step runs the hook and writes the flag into
   `artifacts/deploy.log`.
4. `GET /get?key=artifacts/deploy.log` → the per-team flag.

`/flag.txt` is served by no route; it only reaches the attacker through the
deploy step they triggered. `/put` refuses any key without a valid, unexpired
signature, so the write must go through the over-broad presign.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the signing
secret is fresh random per instance so a presigned URL from one team is useless
against another. The chain must be run against _this_ instance.

> Variante de la classe `backup-presign` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the over-broad presign signs `hooks/postdeploy`, the sentinel write plus
`/deploy` publish the exact per-team flag, and `/put` rejects an unsigned or
expired write. **Docker/Lot-5 rehearsal is the remaining gate before
`state: visible`.**
