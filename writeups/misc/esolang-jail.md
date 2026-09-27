<!-- nctf-meta category="misc" difficulty="medium" points="400" author="ctf-2026" stub="0" -->

# esolang-jail

## Summary

`esolang-jail` serves **Marble**, a tiny Forth-flavoured stack esolang, as an
interactive REPL over TCP (`nc host port`). The jail's premise: a Marble program
can compute freely but cannot touch the host -- no file word, no import, no
eval. The only bridge to host-provided helpers is the `SYS` gate, which is meant
to expose _only_ the Marble standard library (pure string/number helpers,
slots 0..7).

The escape is a **missing lower bound on the `SYS` index** (a negative-index /
opcode-confusion bug). `SYS` pops its index off the stack and dispatches into a
single Python list that holds the standard library **and** the interpreter's own
private host primitives:

```
DISPATCH = [ strlen, concat, substr, itoa, atoi, upper, ord, chr,  # 0..7 exposed
             env, read ]                                           # 8..9 hidden
SAFE_COUNT = 8
op_sys:  idx = pop_int();  if idx >= SAFE_COUNT: reject;  DISPATCH[idx](vm)
```

The guard rejects `idx >= 8` but never checks `idx < 0`. Python list indexing
wraps negative indices, so:

- `SYS -1` -> `DISPATCH[-1]` -> `read(path)` (arbitrary host file read)
- `SYS -2` -> `DISPATCH[-2]` -> `env(name)` (arbitrary host env lookup)

The tokenizer refuses negative _literals_ (`\d+` only), but Marble produces
negatives with ordinary arithmetic (`0 1 SUB`, or `1 NEG`) -- so the value is
easy to build, the bug is that `SYS` accepts it.

## Why the naive path is contained

- There is no file/import/eval word at all; the safe opcode set never touches
  the host.
- The 256-cell memory is bounds-checked on **both** sides
  (`5 999 STORE` -> error, `1 NEG LOAD` -> error), so the obvious OOB attempt is
  a genuine dead end.
- `SYS 8` / `SYS 9` (reaching the hidden natives by their real index) is
  rejected: `index out of exposed range (0..7)`.

A benign program stays contained:

```
2 3 ADD PRINT            -> 5
"hi" "!" 1 SYS PRINT     -> hi!      (concat, slot 1)
42 5 STORE 5 LOAD PRINT  -> 42
```

## The escape

Any of these single lines breaks out. The first needs no knowledge of the flag's
path or env var name -- it just reads the process environment:

```
"/proc/self/environ" 0 1 SUB SYS PRINT     # read() via SYS -1 -> FLAG=NCTF{…}
"FLAG" 0 2 SUB SYS PRINT                    # env("FLAG") via SYS -2
"/flag/flag.txt" 1 NEG SYS PRINT           # read() via SYS -1 -> flag file
```

Stack trace of the first line: push `"/proc/self/environ"`, push `0`, push `1`,
`SUB` -> `-1` on top, `SYS` pops `-1` and dispatches to `read`, which pops the
path, reads the file, and pushes its contents; `PRINT` outputs it. The env blob
contains `FLAG=NCTF{…}`.

## Flag derivation (served, per team)

The flag is **never** in a downloadable artifact and the interpreter source is
not shipped. `entrypoint.sh` computes it at runtime with `flag.py`:

```
FLAG = "NCTF{…}"
     = "NCTF{…}"
```

and places it in the interpreter process's environment and in `/flag/flag.txt`
(tmpfs). Both are reachable only through the escape above. The scoreboard's
`team_hmac` flag class (content `misc-esolang-jail`) recomputes and validates
each team's flag on submission.

## Run it

```
python3 solve.py <host> <port>
# e.g. python3 solve.py localhost 9301
```

`solve.py` connects, confirms `8 SYS` is rejected (naive path blocked), then
sends the escape lines and extracts `NCTF{…}`.

## Local verification (done by the author)

Verified two ways, both against the real interpreter (pure Python):

1. **Direct**, feeding programs to `app/interp.py` on stdin with a dummy flag in
   the environment and a dummy `flag.txt`: the benign programs print `5`,
   `hi!`, `42`; `8 SYS`/`9 SYS` are rejected; memory OOB is rejected both sides;
   and the three escape lines each recover the dummy flag (via env lookup, file
   read, and `/proc/self/environ`).
2. **End-to-end**, serving with the exact command from `entrypoint.sh`
   (`socat TCP-LISTEN:PORT,reuseaddr,fork EXEC:"python3 app/interp.py"`) with the
   flag derived by `flag.py` from a playtest `TEAM_SECRET`, then running
   `solution/solve.py` against it -- it recovered the derived flag via
   `/proc/self/environ`.

The full container/arena run is deferred to Lot 5.
