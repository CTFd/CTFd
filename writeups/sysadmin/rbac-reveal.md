<!-- nctf-meta category="sysadmin" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# rbac-reveal

## TL;DR

A Kubernetes `Secret` is base64, not encryption, and the RBAC `Role` grants the
app ServiceAccount read on every secret in the namespace. The `token` value was
base64-encoded twice (once by the deploy script, once by `kubectl`), so decoding
it twice yields the flag.

## The misconfiguration

Two things combine:

1. **Over-permissive RBAC.** `rbac.yaml` grants `get`/`list`/`watch` on
   `secrets` namespace-wide. Anyone bound to `app-reader` can read all secrets;
   it should at most be scoped with `resourceNames: ["app-api"]`.
2. **"Secret" is only encoding.** `Secret.data` values are base64. Treating that
   as protection is the mistake. Here the value was pre-base64'd before being
   stored, so it is base64-of-base64.

## Attack

1. Read `data.token` from `secret.yaml`.
2. Base64-decode it once → another base64 string.
3. Base64-decode that → the flag.

## Run

```
python3 solve.py
```

Output:

```
[+] Secret data.token = VGtOVVJudHJPSE5m...
[+] after first base64 decode: TkNURntrOHNfc2VjcmV0...
[+] FLAG = NCTF{…}
```

## Files

- `../rbac.yaml`, `../secret.yaml`, `../deployment.yaml` — the manifest bundle.
- `../src/gen.py` — deterministic builder.
- `solve.py` — reference solver (stdlib only).
