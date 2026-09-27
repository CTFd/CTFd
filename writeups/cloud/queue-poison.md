<!-- nctf-meta category="cloud" difficulty="hard" points="500" author="ctf-2026" stub="0" -->

# queue-poison

**Category** cloud · **Value** 500 · **Served** yes (per-team flag)

## Vulnerability chain

**Poisoned message → worker deserialization → gadget execution.** Queue messages
name their class in `__class__` and the worker instantiates it from a registry
with no allow-list. The registry still holds a debug `FlagDumper` gadget whose
construction reads the instance secret, so a poisoned message builds it.

## Intended path

1. `POST /enqueue {"__class__":"__nope__"}` → 400 whose `registry` leaks
   `["FlagDumper","Notification"]`.
2. `POST /enqueue {"__class__":"FlagDumper"}` → queue the poisoned message.
3. `POST /work` → the worker deserializes it, running the gadget.
4. `GET /results` → the last result is the per-team flag.

`/flag.txt` is served by no route; it only surfaces as the rendered output of the
gadget the poisoned message instantiated.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the gadget
reads the flag from _this_ instance's filesystem at solve time, so a flag from
another team is useless.

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the unrestricted deserializer builds the `FlagDumper` gadget from a
poisoned message and the worker's result carries the exact per-team flag.
**Docker/Lot-5 rehearsal is the remaining gate before `state: visible`.**
