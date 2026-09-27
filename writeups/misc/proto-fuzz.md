<!-- nctf-meta category="misc" difficulty="medium" points="350" author="ctf-2026" stub="0" -->

# proto-fuzz

**Category:** misc &nbsp; **Difficulty:** medium &nbsp; **Challenge id:** `misc-proto-fuzz`

## TL;DR

`FZLP/1` is a home-grown line protocol. Its `CFG <n>` command has an
**off-by-one on the length field**: it reads `n+1` entry lines and writes
channel index `i` for `i in range(n+1)`, never checking `i` against the
documented channel count (3 channels: 0,1,2). There is a fourth, undocumented
**maintenance** channel at index **3**. `n` is validated to `0..3`, so you can
never say `CFG 7` to reach index 3 directly -- but at the boundary `n == 3` the
off-by-one write lands _exactly_ on index 3. Arm it non-zero and the hidden
`DUMP` command unlocks and returns the flag.

Solve:

```
CFG 3
01
01
01
01        <- the 4th entry (off-by-one) arms channel 3 = maintenance
DUMP      <- now emits the flag
```

## Recon

The handout gives a partial spec (`PROTOCOL.md`) and a verbatim benign capture
(`session.log`). From the spec:

- Verbs: `PING`, `STAT`, `HELP`, `CFG <n>`.
- 3 channels (0,1,2). `CFG <n>`, `n` in `0..3`, reads `n` entry lines (hex byte
  per channel), replies `OK mask=0x..`.
- `DUMP` is mentioned only in a TODO: "stays locked unless the maintenance
  channel is armed ... Double check the entry loop bound before shipping."
- `STAT` reports `reserved_admin_ch=0x07`.

Poking the live service confirms the verbs. `DUMP` exists but returns
`ERR locked: maintenance channel not armed`. So the whole game is: **arm the
maintenance channel.**

## Two red herrings, quickly refuted

1. **`SU root`** looks like a privilege path. It always returns
   `ERR: SU disabled on this build`. Dead end -- one request to confirm.
2. **`reserved_admin_ch=0x07`** in `STAT` suggests a "channel 7". But `CFG 7`
   returns `ERR n out of range (expected 0..3)`, and nothing lets you address a
   channel 7. This is the intended decoy: refutable in one request. The real
   maintenance channel is **3**, not 7.

## The bug

The `session.log` capture has the tell. The operator sent:

```
> CFG 1
> 01
> STAT
< OK mask=0x01      <- and STAT produced NO reply
```

They typed `CFG 1`, one entry, then `STAT` -- but `STAT` got no reply, and the
`OK` came only after it. `CFG 1` consumed the `STAT` line as a config entry.
Spec says `CFG <n>` reads `n` entry lines; in reality it reads **one more**.

Confirm it directly by fuzzing the length field and watching how many lines get
eaten. `CFG 0` with zero declared entries still swallows your next line. The
loop bound is inclusive:

```python
for i in range(n + 1):          # BUG: should be range(n)
    entry = self.read_line()
    self.channels[i] = parse_hex_byte(entry)   # no check i < 3
```

The backing store has 4 slots. Index 3 is the maintenance channel, one past the
documented three. The only `i` that reaches 3 is when `range(n+1)` includes 3,
i.e. `n == 3`. And `n` is capped at 3, so `n == 3` is the _only_ value where the
off-by-one write hits the hidden channel. That is the "length field fuzzed into
an off-by-one state."

## Exploit

Send `CFG 3` and then **four** entry lines. The first three set channels 0/1/2;
the fourth (the off-by-one iteration) writes channel 3. Make it non-zero:

```
CFG 3
01
01
01
01
```

Server replies `OK mask=0x0f MAINT-ARMED (see HELP)`. `mask` now has bit 3
(`0x08`) set -- proof the hidden channel exists and is armed. `HELP` now also
lists `DUMP`. Run it:

```
DUMP
-> MAINT ok; flag follows
-> NCTF{…}
```

`solve.py` automates this:

```
python3 solve.py <host> <port>
```

## Why this is a server-side oracle / per-team

The flag is **never** in any downloadable file. The service derives it at
runtime from the injected `TEAM_SECRET`:

```
flag = "NCTF{…}"
```

`DUMP` emits it only after checking the **effect** (`channels[3] != 0`), not any
particular request byte-pattern -- so any route that genuinely arms maintenance
wins, and no offline reasoning over an artifact can produce the flag. See
`flag.py`.

## Honest note on LLM assistance

- **Where an LLM helps:** the moment it can _drive the socket_, an LLM is good
  at hypothesising "off-by-one on a length field" from the `session.log` anomaly
  and the spec's "check the entry loop bound" TODO, and at scripting the probe.
  This keeps it a _medium_, not a _hard_.
- **Where it does not solve it for free:** the flag is a server-side oracle, so
  there is no static artifact to grind offline all night -- solving _requires_
  live, iterative interaction with the per-team instance (rate-limited, logged).
  A single prompt over the handout cannot produce a flag; at minimum the solver
  must (a) notice CFG over-reads, (b) realise only the boundary `n == 3` reaches
  the hidden channel (not the `0x07` decoy), and (c) supply a non-zero 4th entry.
  Each is a small inference from evidence, but all three must actually be
  exercised against the server. The `0x07` decoy reliably wastes a first guess
  from anyone (human or model) who pattern-matches "admin = 7".

## Verified

Built and run locally; `solve.py` recovers the flag the server derives from
`TEAM_SECRET` (checked against `flag.py`). See the transcript in the challenge
notes.
