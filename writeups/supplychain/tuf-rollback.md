<!-- nctf-meta category="supplychain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# tuf-rollback

A TUF rollback attack: the served snapshot is older than the timestamp role
knows about, pinning a backdoored release.

## Vulnerability

The `timestamp` role (the freshest, most-trusted role) records that the current
`snapshot` is version 8. The served `snapshot.json` is version 5 — an attacker
replayed old metadata. That stale snapshot pins targets version 5, which points
at `updater-agent-2.0.1.tgz`, a backdoored build. The clean current release
(`2.1.0`) is only referenced by the newer targets v8.

## Solve

1. Read `timestamp.json`: expected snapshot version is 8.
2. Read `snapshot.json`: version 5 < 8 -> rollback detected.
3. The stale snapshot pins targets version 5. Load `targets-v5.json`, follow
   its target to `targets/updater-agent-2.0.1.tgz`, verify its sha256.
4. Extract `agent.py`; `_c` is base64(flag). Decode it.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
