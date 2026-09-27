<!-- nctf-meta category="sysadmin" difficulty="medium" points="200" author="dagbanjaphet" stub="0" -->

# rotate-root

## TL;DR

logrotate's `postrotate` runs `rotate-hook.sh` as root (and sudoers lets
`deploy` trigger it too). The hook does not store a token — it **derives** one
from `rotate.conf` and writes it to `$SECRET_DIR/app-$CYCLE-$HOSTID.token`. That
token file is not shipped, so you reconstruct the token from the config and wrap
it as `NCTF{…}`. No file contains the flag
literally.

## The privilege path

- `etc/logrotate.d/app` has a `postrotate` block. logrotate runs from
  `/etc/cron.daily` **as root**, so anything in `postrotate` runs as root.
- `etc/sudoers.d/deploy` additionally grants `deploy` NOPASSWD to run the same
  `rotate-hook.sh` as root on demand.
- So `rotate-hook.sh` is the root-privileged write. It drops its output into
  `/var/lib/app/secrets/` (mode `0700`, root-owned) — a directory that is not
  part of the bundle.

## Deriving the token

`rotate-hook.sh` sources `etc/app/rotate.conf` and computes the token
deterministically:

```sh
NAME="app-${CYCLE}-${HOSTID}.token"
OUT="${SECRET_DIR}/${NAME}"
TOKEN=$(printf '%s:%s:%s' "$CYCLE" "$HOSTID" "$ROTATE_SECRET" | sha256sum | cut -c1-10)
```

With `CYCLE=2024w18`, `HOSTID=kbz07`, `ROTATE_SECRET=dev-rotate-secret-0000`:

```
sha256("2024w18:kbz07:dev-rotate-secret-0000") = 1c921ff376...
TOKEN = 1c921ff376
```

Because the token is a pure function of committed config, there is nothing to
`cat` — you recompute it. The flag is that token wrapped in the documented
format.

## Attack

1. Read `CYCLE`, `HOSTID`, `ROTATE_SECRET` from `rotate.conf`.
2. Apply the hook's rule: `sha256("<CYCLE>:<HOSTID>:<ROTATE_SECRET>")[:10 hex]`.
3. Wrap: `NCTF{…}`.

## Run

```
python3 solve.py
```

Output:

```
[+] root-written (unshipped) token path: /var/lib/app/secrets/app-2024w18-kbz07.token
[+] derived rotation token: 1c921ff376
[+] FLAG = NCTF{…}
```

## Files

- `../fs/...` — the ops bundle (mirror of the host paths); the token file is
  intentionally absent.
- `../src/gen.py` — deterministic builder.
- `solve.py` — reference solver (stdlib only).
