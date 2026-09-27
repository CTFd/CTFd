<!-- nctf-meta category="pwn" difficulty="hard" points="500" author="dagbanjaphet" stub="0" -->

# boot2root-linux

**Challenge id:** `pwn-boot2root-linux` · **Category:** pwn · **Difficulty:** hard
**Served:** yes (per-team container, `type: team_instance`)

## Flag derivation

Per-team, dynamic. The instancier injects `FLAG` and `CHALLENGE_SECRET`
(never the team master secret). `flag.py` resolves, in order:

1. `FLAG` env -> verbatim;
2. else `CHALLENGE_SECRET` -> `"NCTF{…}"`;
3. else LOCAL DEV fallback `HMAC_SHA256(TEAM_SECRET or "local-dev-secret",
"pwn-boot2root-linux")[:24]`.

This mirrors `format-string-101/flag.py` and `heap-note/flag.py` exactly. The
scoreboard's `team_hmac` flag class (content `pwn-boot2root-linux`) recomputes
and validates each team's flag on submission; no static flag ships.

`entrypoint.sh` writes the derived flag to `/root/flag` (root:root, `400`),
scrubs `FLAG` from the environment, then drops to `www` to serve the foothold.
The flag is therefore never baked into the image, never world-readable, and
never in an env var reachable by the service user.

## The privesc chain (intended)

1. **HTTP command injection -> `www`.** `/diag?target=` is concatenated into
   `getent hosts <target>` and run with `shell=True`.
2. **SUID PATH hijack -> `app`.** `/usr/local/bin/logsync` is SUID `app`
   (`4755`); it `setreuid(app,app)` then calls `ps`/`date` by relative name via
   `system()`, so a planted `ps` earlier in `$PATH` runs as `app`.
3. **sudo tar wildcard -> `root`.** `app` has
   `NOPASSWD: /usr/bin/tar -czf /var/backups/app-logs.tgz *`; the trailing `*`
   enables GTFOBins `--checkpoint-action=exec` root command execution.
4. **Read `/root/flag`** as root (the win effect).

See `solve.md` for exact commands and `solve.sh` for the automated run.

## Static verification (docker unavailable here; live run deferred to Lot 5)

Verified by reading the sources in this directory:

- **Foothold is reachable + exploitable.** `webstatus.py` binds `0.0.0.0:8080`
  (matches `internal_port`), and `/diag` runs `subprocess.run("getent hosts " +
target, shell=True)` with no sanitisation -> `;`/`|`/`$()` injection as `www`.
- **Service really runs as www, not root.** `entrypoint.sh` execs the server
  under `setpriv --reuid=www --regid=www --init-groups` (util-linux, present in
  ubuntu:22.04), reassigning real+eff+saved ids, so no residual root.
- **Stage-2 SUID is set up as described.** Dockerfile compiles `logsync.c` to
  `/usr/local/bin/logsync`, `chown app:app`, `chmod 4755` -> world-executable
  (www can run it), setuid `app`. `logsync.c` does `setreuid(geteuid(),
geteuid())` then `system("date")` / `system("ps ...")` -- relative names, no
  `PATH` scrub -> hijackable to an `app`-uid process.
- **Stage-3 sudo rule is present and valid.** Dockerfile writes
  `/etc/sudoers.d/app-backup` (`0440`) with the wildcard tar rule and runs
  `visudo -cf` at build to guarantee the syntax parses. `app` matches by real
  uid, which the stage-2 `setreuid` provides. `/usr/bin/tar` is the real tar on
  ubuntu 22.04 (usrmerge).
- **Flag is root-only and not leaked.** `/root/flag` is created `chmod 400`,
  `chown root:root`; `FLAG` is `unset` before dropping privileges; no `files:`
  handout ships the image contents; no flag string appears in any source file
  (`grep -R NCTF challenges/pwn/boot2root-linux` -> only doc/regex matches, no
  literal flag).
- **Chain is genuinely 3-stage across 3 identities.** `www` is not in sudoers;
  only `app` has the tar rule; only `root` can read the flag. No single stage
  reaches root.

**Deferred to the Lot 5 rehearsal:** live `docker build`, container boot,
running `solve.sh` against the instance end to end, and confirming
`cat /root/flag` returns the injected `NCTF{…}`.
