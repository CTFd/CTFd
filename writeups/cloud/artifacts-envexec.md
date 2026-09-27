<!-- nctf-meta category="cloud" difficulty="medium" points="300" author="ctf-2026" stub="0" -->

# artifacts-envexec

**Category** cloud · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Environment injection → init-hook execution → secret dump.** The function
runtime documents only `LOG_LEVEL` and `REGION` as caller-settable env, but it
applies every key it is handed. It consults `INIT_HOOK` from that env; an unknown
value returns a verbose error leaking the hook registry, which still contains a
debug `reveal` hook that dumps the instance secret.

## Intended path

1. `POST /invoke {"fn":"greet","env":{"INIT_HOOK":"x"}}` → 400 whose
   `available_hooks` leaks `["noop","reveal"]`.
2. `POST /invoke {"fn":"greet","env":{"INIT_HOOK":"reveal"}}` → the result's
   `init_hook_output` is the per-team flag.

`/flag.txt` is served by no route; it only surfaces as the output of the debug
init hook the attacker chose to run.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the flag is
read from the instance filesystem at solve time, so a flag from another team is
useless. The registry leak and the hook name must be discovered against _this_
instance.

> Variante de la classe `backup-envexec` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the unfiltered env reaches the init-hook dispatcher, the verbose error
leaks the registry, and the `reveal` hook returns the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
