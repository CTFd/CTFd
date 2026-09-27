<!-- nctf-meta category="pwn" difficulty="hard" points="500" author="dagbanjaphet" stub="0" -->

# boot2root-c2

**Challenge id:** `pwn-boot2root-c2` · **Category:** pwn · **Difficulty:** hard
**Served:** yes (per-team container, `type: team_instance`)

Lore ties into the HIVE CONSULT / Operation Phantom Wire forensics universe:
the box is the ransomware crew's exposed C2 staging server, and the player is
the IR analyst taking it apart.

## Flag derivation

Per-team, dynamic. The instancier injects `FLAG` and `CHALLENGE_SECRET` (never
the team master secret). `flag.py` resolves, in order:

1. `FLAG` env -> verbatim;
2. else `CHALLENGE_SECRET` -> `"NCTF{…}"`;
3. else LOCAL DEV fallback `HMAC_SHA256(TEAM_SECRET or "local-dev-secret",
"pwn-boot2root-c2")[:24]`.

The scoreboard's `team_hmac` flag class (content `pwn-boot2root-c2`) recomputes
and validates each team's flag on submission; no static flag ships.
`entrypoint.sh` writes it to `/root/flag` (root:root, `400`), scrubs the
secrets, then drops to `www` (via `setpriv`).

## The privesc chain (intended)

Three deliberately _distinct_ techniques (no overlap with the other two boxes):

1. **Unsafe YAML deserialization -> `www`.** `POST /api/queue` parses the body
   with `yaml.load(body, Loader=yaml.Loader)`. PyYAML's full loader honours
   python object tags, so
   `!!python/object/apply:subprocess.check_output [["id","-un"]]`
   executes a process as `www`; the panel reflects the parsed value, so output
   comes straight back.
2. **SUID writable-config path -> `deploy`.** `/usr/local/bin/queuectl` is SUID
   `deploy` (`4755`); it execs the script named by `runner=` in
   `/etc/phantom/queue.conf`, and that config is world-writable (`0666`). Point
   `runner=` at your own script and run `queuectl` -> it runs as `deploy`.
3. **sudo + writable script dir -> `root`.** `deploy` may
   `sudo -n /usr/bin/python3 /opt/phantom/report.py`. `report.py` does
   `import phantomlib`, resolved from its own directory `/opt/phantom`, which is
   group-writable by `deploy` (`2775`). Drop a `phantomlib.py` there whose
   module-level code runs your payload; it executes as root when report.py is
   sudo-run. (report.py itself is root-owned `0644`; the hole is the writable
   _directory_.)
4. **Read `/root/flag`** as root (the win effect).

Enumeration cues: `find / -perm -4000 -type f 2>/dev/null` surfaces `queuectl`;
`ls -la /etc/phantom` shows the `0666` config; `sudo -l` shows the report.py
rule; `ls -ld /opt/phantom` shows the group-writable directory.

See `solve.sh` for the automated run (drives all three stages through the
`/api/queue` YAML RCE, no interactive shell needed).

## Static verification (docker daemon unavailable in the build env)

Validated at the logic level without a container build:

- **YAML gadget** -- `subprocess.check_output [["sh","-c",...]]` executes on the
  pinned PyYAML (6.0.x); confirmed end-to-end over HTTP against the live
  `panel.py` (reflected `id` output).
- **queuectl** -- compiles; against a real `/etc/phantom/queue.conf` it parses
  `runner=` and execs the named script after `setreuid`, as designed.
- **Module hijack** -- confirmed that running a script by absolute path puts its
  directory on `sys.path[0]`, so a planted `phantomlib.py` is imported and its
  module-level code runs (as root under sudo).
- **flag.py** -- all three resolution paths produce the expected `NCTF{…}`.
- **solve.sh plumbing** -- the YAML-RCE fire/read loop was integration-tested end
  to end with the privileged steps mocked; it recovers the planted flag.

A live `docker build` + `./solve.sh http://HOST:PORT` run is deferred to the
image-build phase (`deploy/local/build-images.sh boot2root-c2`), where the SUID
bit and sudo rule take effect for real.
