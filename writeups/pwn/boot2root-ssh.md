<!-- nctf-meta category="pwn" difficulty="medium" points="400" author="dagbanjaphet" stub="0" -->

# boot2root-ssh

**Challenge id:** `pwn-boot2root-ssh` · **Category:** pwn · **Difficulty:** medium
**Served:** yes (per-team container, `type: team_instance`, SSH entry on port 22)

An SSH-entry boot2root: the player is handed low-priv SSH access and must
escalate to root. Distinct privesc from the other boot2roots (this one is a
`sudo SETENV` + `LD_PRELOAD` policy hole).

## Flag derivation

Per-team, dynamic (same contract as the other served challenges). `entrypoint.sh`
plants the flag at `/root/flag` (root:root, `400`), sets the `ctf` login
password, scrubs the injected secrets, then execs `sshd`. `team_hmac` (content
`pwn-boot2root-ssh`) validates it.

## The privesc (intended)

1. **SSH in** as `ctf` (`ssh ctf@HOST -p PORT`, password `ctf`). Root login is
   disabled.
2. **`sudo -l`** shows: `ctf ALL=(root) NOPASSWD: SETENV: /usr/local/bin/healthcheck`.
   `healthcheck` is a normal dynamically-linked, **non-SUID** binary; the `SETENV`
   tag lets the caller keep environment variables on the command.
3. **`LD_PRELOAD` → root.** Because `healthcheck` is non-SUID and run as root via
   sudo, the dynamic linker honours a `LD_PRELOAD`ed library. Build a `.so` with
   a `__attribute__((constructor))` that `setuid(0)` and spawns a shell / reads
   the flag, then:
   `sudo LD_PRELOAD=/dev/shm/rootme.so /usr/local/bin/healthcheck`
4. **Read `/root/flag`** as root (the win effect).

`solve.sh HOST PORT` automates it (needs `sshpass`).

## Static verification (docker daemon unavailable in the build env)

- **LD_PRELOAD primitive** — confirmed live: `healthcheck` compiles as a
  dynamically-linked non-SUID ELF; a preloaded `.so`'s
  `__attribute__((constructor))` fires before `main` when `healthcheck` runs
  (`PRELOAD_CONSTRUCTOR_RAN uid=0`). Under `sudo SETENV` the process is root, so
  the constructor runs as root.
- **flag.py** — all three resolution paths produce the expected `NCTF{…}`.
- **sudoers** — `visudo -cf` validates the SETENV rule at build.

A live `docker build` + `./solve.sh HOST PORT` run (sshd + real sudo) is deferred
to the arena bring-up (`deploy/local/build-images.sh boot2root-ssh`).
