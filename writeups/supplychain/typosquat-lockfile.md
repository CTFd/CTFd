<!-- nctf-meta category="supplychain" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# typosquat-lockfile

A typosquatted dependency (`expres`, one letter off `express`) sneaks into the
lockfile, resolved from an attacker-controlled mirror.

## Vulnerability

Every legitimate dependency resolves from `registry.npmjs.org`. One entry,
`expres@4.18.9`, resolves from `npm-registry-mirror.dev` instead. Its name is
edit-distance 1 from the popular `express`, and its tarball hides a payload.

## Solve

1. Read `package-lock.json`; group `packages` by the host of each `resolved`
   URL. The odd host out is the attacker mirror serving `expres`.
2. Extract `package/index.js` from `expres-4.18.9.tgz`.
3. The payload variable `_p` is `ROT13(base64(flag))`. ROT13-decode, then
   base64-decode to reveal the flag.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
