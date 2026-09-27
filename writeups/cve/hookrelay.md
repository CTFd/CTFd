<!-- nctf-meta category="cve" difficulty="medium" points="350" author="ctf-2026" stub="0" -->

# hookrelay

**Category** cve · **Value** 350 (dynamic) · **Served** yes (per-team flag)

## The vulnerability

The mirror healthcheck runs **GitPython 3.1.29** and calls
`Repo.clone_from(user_url, tmp, ...)` with no validation of `user_url`. That is
**CVE-2022-24439**: GitPython < 3.1.30 passes the URL straight to `git`, so a URL
using git's **`ext::` remote transport** is executed as a command. The fix
(3.1.30) added `allow_unsafe_protocols` / `allow_unsafe_options`, both defaulting
to `False` — the paid hint points at that patch diff.

The image sets `git config --global protocol.ext.allow always`, standing in for a
real "internal mirrors allow ext transports" misconfiguration, so the helper
fires regardless of the git build.

## Intended path

1. Read the footer: `mirror-agent GitPython 3.1.29`. Look up that version's
   advisory → CVE-2022-24439 (URL not validated before reaching `git`).
2. The flag is in `/flag.txt`, served by no route. Use the CVE to run a command
   as the agent that drops the flag into the world-served scratch dir `/app/pub`,
   then read it back:

   ```
   repo = ext::sh -c cp${IFS}/flag.txt${IFS}/app/pub/loot
   ```

   then `GET /pub/loot`.

   `git-remote-ext` splits the string after `ext::` on spaces and `execvp`s it,
   so each argument is kept space-free and the inner `sh -c` re-introduces spaces
   via `$IFS`.

3. Alternate read channel (no `/pub` write): exfil to git's stderr, which the
   healthcheck prints back —
   `ext::sh -c cat${IFS}/flag.txt${IFS}1>&2`.

## Run the reference solver

```
python3 solution/solve.py http://HOST:PORT
# -> NCTF{…}
```

## Why it resists an agent more than a static challenge

- The flag is **per team** and lives only on the running instance — there is no
  downloadable artifact to paste into a chat.
- Success requires **live exploitation** of a real CVE against a stateful
  service, not recall of a writeup: the value is deriving the `ext::` payload and
  wiring a read channel, then doing it against _this_ instance.
- The CVE id is a **paid hint**, not in the description, so the research step is
  itself part of the challenge.

## Verification status

Static checks pass (imports, byte-compile, flag derivation, YAML). **Live
end-to-end exploit is a Lot 5 rehearsal gate** (needs Docker to build the image
and run the `ext::` transport), same as every served challenge. At the rehearsal:
`docker compose up --build` then `python3 solution/solve.py http://localhost:8080`
must print the instance flag; confirm the `ext::` helper fires on the arena's git
build (the `/pub` channel is git-version-independent; the stderr fallback is not).
