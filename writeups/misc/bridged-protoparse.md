<!-- nctf-meta category="misc" difficulty="medium" points="450" author="ctf-2026" stub="0" -->

# bridged-protoparse

**Category** misc · **Value** 450 · **Served** yes (per-team flag)

## Vulnerability

**Out-of-bounds read** in a homemade TLV parser. A record is
`[type:1][len:2 BE][value]`, and `/parse` reads `len` bytes from a backing buffer
laid out as `value || padding || FLAG`. The parser trusts the declared length
instead of clamping it to the real value length, so an over-declared length reads
past the value into the flag.

## Intended path

```
rec = 01 0200 41        # type=1, declared_len=0x0200 (512), value="A"
GET /parse?rec=<hex>    # echoed value = "A" + padding + NCTF{…}
```

A well-formed record (`len` == real value length) returns only the value and
leaks nothing.

## Reference solver

```
python3 solution/solve.py http://HOST:PORT   # -> NCTF{…}
```

## Why it resists AI one-shotting

Per-team HMAC flag on the live instance, no downloadable artifact; the flag sits
in _this_ instance's buffer only. The player must recognise the length-field
trust bug and over-read against the running service — nothing transfers between
teams.

> Variante de la classe `proto-fuzz-live` (même vulnérabilité, instance et flag par-équipe distincts).

## Verification status

Implemented. Verified end-to-end locally (Flask app + reference solver over
HTTP): the over-declared length leaks the exact per-team flag; a well-formed
record does not. **Docker/Lot-5 rehearsal is the remaining gate before
`state: visible`.**
