<!-- nctf-meta category="pwn" difficulty="" points="150" author="ctf-2026" stub="0" -->

# format-string-101

**Category:** pwn · **Difficulty:** easy · **Challenge id:** `pwn-format-string-101`

## TL;DR

A textbook format-string bug: `printf(user_input)`. Leak the stack to find the
argument offset of your input buffer, then use `%hn` to write this connection's
random `nonce` into the global `auth` cell. The service verifies the effect
(`auth == nonce`) server-side and only then prints the per-team flag.

## The bug

`chall.c`, inside the input loop:

```c
fgets(buf, sizeof(buf), stdin);
buf[strcspn(buf, "\n")] = '\0';
printf(buf);          /* <-- attacker-controlled format string */
```

`gcc` even warns: `format not a string literal ... [-Wformat-security]`.

Binary properties (intentional, to keep it "101"):

- `-no-pie` -> `auth` is at a fixed address. The service also prints
  `The write target 'auth' lives at 0x4035ec` so you don't even need `nm`.
- `-fno-stack-protector` -> no canary between `buf` and the saved frame.
- `-O0` -> simple, predictable stack layout.

## Per-connection dynamics (why you can't replay a payload)

Each connection prints a fresh random 32-bit target:

```
Make auth == 0x8bc0b737
```

The value changes every connection, so the `%n` write has to be built live from
the value the banner just gave you. There is nothing to copy-paste from a
previous run.

## Step 1 -- find your offset (the "leak")

Send a known 8-byte marker followed by positional reads and see where the marker
comes back:

```
MARKER!!|%1$p.%2$p.%3$p.%4$p.%5$p.%6$p. ...
```

Response:

```
MARKER!!|0x1.0x1.0x7.0x1.(nil).0x212152454b52414d. ...
                                ^^^^^^^^^^^^^^^^^^  == "MARKER!!" little-endian
```

`0x212152454b52414d` (`"MARKER!!"`) shows up at position **6**, so our buffer
begins at format argument offset **6**.

> Gotcha handled in the solver: one earlier slot leaks `(nil)`. If you match
> only `0x...` tokens you drop it and land on offset 5 (off-by-one, and the
> write silently misses). Map every `.`-separated token to its `%N$p` index.

## Step 2 -- write the nonce into `auth`

Write the 32-bit nonce as two 16-bit halves with `%hn` (short writes keep the
`%c` padding tiny and the payload far under the 256-byte buffer):

- low half -> `auth` (0x4035ec)
- high half -> `auth + 2` (0x4035ee)

Pad the format section to an 8-byte boundary, then append the two little-endian
pointers so they land on aligned stack slots. Solve for the fixpoint where the
pointer slots' argument index equals the index your `%N$hn` directives
reference. `solution/solve.py` (`build_write`) does exactly this.

Send it, and the service confirms the effect and hands over the flag:

```
[+] auth overwritten -- effect verified by the service.
[+] flag: NCTF{…}
```

## Running the solver

```bash
# against the live per-team instance
python3 solution/solve.py <host> <port>

# local playtest (compile first, provide a FLAG so it prints one)
make
FLAG='NCTF{…}' python3 solution/solve.py
```

The solver was verified end-to-end (3/3 runs) locally and over a TCP
socket against the containerised service; each run auto-detects offset 6 and
recovers the flag emitted from the container's `FLAG` env.

## The decoy

`chall.c` contains `debug_dump()`, which holds a hard-coded
`NCTF{…}`. It is **not** the flag and is refutable in
seconds:

1. Nothing calls `debug_dump()` -- it is dead code (kept only via
   `__attribute__((used))`).
2. The rules and the description state the flag is **per-team and
   server-issued** after the effect is verified. A static `NCTF{…}` sitting in
   a downloadable binary can never be a team's real flag.

Chasing it (e.g. trying to redirect control flow to it) is a dead end: even
reaching it prints the wrong string, and the real flag only comes from the
`auth == nonce` oracle.

## Why this resists one-prompt LLM solving (honest note)

- **The success oracle is server-side.** The flag is never in the binary; it is
  `HMAC(TEAM_SECRET, "pwn-format-string-101")` living only in the running
  service's env, emitted only after `auth == nonce`. An agent cannot grind the
  flag offline against the artifact -- it must interact with the live instance.
- **Per-connection nonce** defeats a memorised/replayed payload: the write value
  must be parsed from the banner and the payload rebuilt each connection.
- What an LLM _does_ do well here: it recognises the `printf(buf)` bug instantly,
  knows the `%n`/`%hn` technique, and can drive pwntools. This is a genuinely
  easy challenge -- the intended skill is "leak your offset, build a live write,
  interact with a service", not obscurity. The offset off-by-one from a `(nil)`
  leak, and the arg-index bookkeeping for the two `%hn` writes, are the small
  practical snags that trip up a naive first attempt (pwntools'
  `fmtstr_payload` with the obvious offset does **not** win for this layout --
  the solver builds the write explicitly).
