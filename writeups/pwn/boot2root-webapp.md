<!-- nctf-meta category="pwn" difficulty="hard" points="500" author="dagbanjaphet" stub="0" -->

# boot2root-webapp

**Challenge id:** `pwn-boot2root-webapp` · **Category:** pwn · **Difficulty:** hard
**Served:** yes (per-team container, `type: team_instance`)

## Flag derivation

Per-team, dynamic. The instancier injects `FLAG` and `CHALLENGE_SECRET`
(never the team master secret). `flag.py` resolves, in order:

1. `FLAG` env -> verbatim;
2. else `CHALLENGE_SECRET` -> `"NCTF{…}"`;
3. else LOCAL DEV fallback `HMAC_SHA256(TEAM_SECRET or "local-dev-secret",
"pwn-boot2root-webapp")[:24]`.

This mirrors `boot2root-linux/flag.py`. The scoreboard's `team_hmac` flag class
(content `pwn-boot2root-webapp`) recomputes and validates each team's flag on
submission; no static flag ships.

`entrypoint.sh` writes the derived flag to `/root/flag` (root:root, `400`),
scrubs `FLAG`/`CHALLENGE_SECRET`/`TEAM_SECRET` from the environment, then drops
to `www` (via `setpriv`) to serve the foothold. The flag is therefore never
baked into the image, never world-readable, and never in an env var reachable by
the service user.

## The privesc chain (intended)

Three deliberately _distinct_ techniques (no overlap with `boot2root-linux`,
which is cmd-injection -> SUID PATH-hijack -> sudo tar):

1. **Jinja2 SSTI -> `www`.** `/preview?note=` is compiled as a Jinja2 template
   (`Environment().from_string(note).render()`). The note body _is_ the
   template, so
   `{{ lipsum.__globals__.os.popen('id').read() }}`
   gives reflected code execution as `www`.
2. **SUID arg-injection -> `svc`.** `/usr/local/bin/notebackup` is SUID `svc`
   (`4755`); it `setreuid(svc,svc)` then concatenates its `<bundle>` argument
   into a `/bin/sh` command (`tar -czf /var/backups/notes-<bundle>.tgz ...`).
   A bundle of `x; sh /path #` runs an arbitrary command as `svc` (the trailing
   `#` comments out the `.tgz /srv/notes` tail).
3. **File capability -> `root`.** `/opt/maint/python3` carries `cap_setuid+ep`
   and is `root:svc` mode `0750` -- runnable **only** once you are `svc` (a
   world-executable copy would let `www` skip straight to root, so the group
   restriction is deliberate). As `svc`:
   `/opt/maint/python3 -c 'import os; os.setuid(0); print(open("/root/flag").read())'`
4. **Read `/root/flag`** as root (the win effect).

Enumeration cues: `find / -perm -4000 -type f 2>/dev/null` surfaces
`notebackup`; `getcap -r / 2>/dev/null` surfaces `/opt/maint/python3`.

See `solve.sh` for the automated run (drives all three stages through the
`/preview` SSTI, no interactive shell needed).

## Static verification (docker daemon unavailable in the build env)

Validated at the logic level without a container build:

- **SSTI gadget** -- `lipsum.__globals__.os.popen(...)` and
  `cycler.__init__.__globals__.os.popen(...)` both execute on the pinned
  jinja2 (3.1.6); confirmed end-to-end over HTTP against the live `snapnote.py`
  (`/preview` reflected `id` output).
- **Arg-injection** -- `notebackup.c` compiles; a bundle of
  `x; echo ... #` runs the injected command and the `#` swallows the trailing
  `.tgz /srv/notes`, as designed.
- **Capability step** -- standard `cap_setuid+ep` + `os.setuid(0)`; the file is
  `root:svc 0750` so only `svc` can invoke it.
- **flag.py** -- all three resolution paths produce the expected `NCTF{…}`.
- **solve.sh plumbing** -- the SSTI fire/read loop was integration-tested end to
  end with the privileged steps mocked; it recovers the planted flag.

A live `docker build` + `./solve.sh http://HOST:PORT` run is deferred to the
image-build phase (`deploy/local/build-images.sh boot2root-webapp`), where file
capabilities and SUID bits take effect for real.
