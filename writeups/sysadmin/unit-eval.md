<!-- nctf-meta category="sysadmin" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# unit-eval

## TL;DR

A systemd template unit passes its instance name (`%i`) into a shell script that
`eval`s it and prints a report token derived from the config. Trace which
instance is enabled, read the config, and recompute the token the job emits.

## The misconfiguration

`report@.service` runs `genreport.sh %i` with the instance name unquoted, and
`genreport.sh` does `eval "label=report-$region-$SITE_ID"` where `region` is
that instance name. Feeding an instance name into `eval` is a command-injection
hazard: an attacker who can start `report@<payload>.service` gets arbitrary
shell in the job. For the _enabled_ instance the expansion is fixed, and the job
prints a deterministic token.

The token is a pure function of shipped inputs:

```
instance = main                      # report.timer -> Unit=report@main.service
label    = "report-" + instance + "-" + SITE_ID
token    = sha256(label + BUILD_KEY).hexdigest()[:16]
flag     = "NCTF{…}"
```

with `SITE_ID` and `BUILD_KEY` from `report.conf`.

## Attack

1. `report.timer` sets `Unit=report@main.service` → instance is `main`.
2. Read `SITE_ID=kekeli-prod-07` and `BUILD_KEY=dev-build-key-not-secret` from
   `report.conf`.
3. Build `label = "report-main-kekeli-prod-07"`, concatenate `BUILD_KEY` with no
   separator, sha256, take 16 hex chars.

You can also just run the shipped `genreport.sh main` (after pointing it at the
local `report.conf`) — it prints the same line.

## Run

```
python3 solve.py
```

Output:

```
[+] enabled instance: main
[+] SITE_ID=kekeli-prod-07  BUILD_KEY=dev-build-key-not-secret
[+] FLAG = NCTF{…}
```

## Files

- `../etc/systemd/system/report@.service`, `../etc/systemd/system/report.timer`
- `../usr/local/bin/genreport.sh`, `../etc/report/report.conf`
- `../src/gen.py` — deterministic builder.
- `solve.py` — reference solver (stdlib only).
