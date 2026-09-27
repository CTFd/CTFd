<!-- nctf-meta category="crypto" difficulty="medium" points="350" author="dagbanjaphet" stub="0" -->

# padding-oracle-lite

## TL;DR

A per-team TCP service exposes a classic **CBC padding oracle**, but wrapped in
a home-grown binary framing (POP1) instead of HTTP, and it never tells you that
the oracle _is_ a padding oracle. Speak the framing, discover that `VERIFY`
leaks PKCS#7 validity, run the standard byte-at-a-time attack to decrypt the
token, strip padding, and `SUBMIT` it. The server checks the effect (you
produced the true plaintext) and emits the per-team flag.

## Flag

Per team:

```
flag = "NCTF{…}"
```

emitted by the running instance after a correct `SUBMIT`. `flag.py` reproduces
it from `TEAM_SECRET` for CTFd validation.

## Solve path

### 1. Speak POP1

From `SPEC.md`: every frame is `0xAA | opcode | len16le(words) | payload |
xorck`, where `len` counts **2-byte words** (not bytes) and the checksum is the
XOR of the opcode and payload bytes. Getting the word-vs-byte length and the
checksum right is the first real hurdle -- a naive byte-length reader desyncs on
the very first server frame.

`build_frame` / `read_frame` in `solve.py` implement it.

### 2. Pull the ciphertext

`GETCT` -> the server replies `CT` with `IV(16) || ciphertext`. Here the
ciphertext is 48 bytes (three blocks), i.e. a 32-byte token plus a full block of
PKCS#7 padding.

### 3. Identify the oracle by evidence, not by name

The protocol deliberately does not say what `VERIFY` computes. You infer it:

- Feed it the real `IV||CT` -> status `1`.
- Feed it garbage or a random blob -> status `0`.
- Take the real blob and flip a single byte in the **second-to-last** ciphertext
  block -> status flips to `0` (you corrupted the padding of the last block),
  while flipping a byte in an earlier block leaves it `1`.

That behaviour -- a boolean that depends only on whether the _last decrypted
block_ has valid padding -- is the fingerprint of a PKCS#7 padding oracle. Once
you see it, the rest is textbook.

### 4. Byte-at-a-time recovery

For each ciphertext block `Ci` with predecessor `C(i-1)`, recover the
intermediate `I = D_K(Ci)` one byte at a time by forging the 16 bytes that play
the role of the preceding block and asking the oracle for valid padding of
lengths 1..16. Then `Pi = I XOR C(i-1)`. `recover_block` in `solve.py` does this,
including the standard `pad == 1` false-positive guard (flip the second-to-last
forged byte to confirm you really produced a `01` pad and not a longer one).

Recover all real blocks, concatenate, strip the trailing PKCS#7, and you have
the 32-byte token, e.g. `SESSION_ef2803316f2deb9a6a746650`.

### 5. Submit the effect

`SUBMIT` the 32 recovered bytes. The server compares them against the token it
actually encrypted and, on an exact match, replies `FLAG`. The flag is never in
any downloadable artifact and is only produced after this effect.

## Run it

```
# local
docker compose up --build          # or: TEAM_SECRET=... python3 app/server.py
python3 solution/solve.py 127.0.0.1 9007
```

Verified end-to-end locally: the solver recovers the token and the returned flag
equals `flag.py`'s output for the same `TEAM_SECRET`.

## The decoy

The banner advertises a "legacy default token"
(`SESSION_000000000000000000000000`). It is a rabbit hole: your instance's token
is random, so submitting the legacy value just returns `wrong token`. It is
refuted in a single `SUBMIT`, submissions are unlimited and unpenalised, so it
costs nothing.

## Honest note on LLM difficulty

Padding-oracle attacks are extremely well known, and a frontier LLM can write
the recovery loop from memory. This challenge does **not** try to hide the
technique; its friction is elsewhere and is genuine:

- **No HTTP.** Off-the-shelf tooling (padbuster, Burp) does not apply. The
  solver must be written against a custom binary framing with two deliberate
  convention violations (word-counted length, header-excluding XOR checksum). An
  LLM will still produce this, but it must get the framing byte-exact against a
  live socket, and a subtly wrong checksum or endianness silently desyncs.
- **The oracle is unlabelled.** The service returns an opaque 1-word code and
  never says "padding". The solver has to _establish_ that it is a padding
  oracle from probing behaviour rather than being told, which is real
  inference-from-evidence rather than pattern recall.
- **Server-side effect gate.** The flag only exists after a correct `SUBMIT`
  against the live per-team instance; there is no offline artifact to grind, so
  an autonomous agent cannot iterate all night without touching the service.

Net: a capable solver (human or AI-assisted) will get this in reasonable time --
it is a _medium_. What it resists is the one-prompt "paste the file, get the
flag" solve, because there is no file and the oracle must be characterised live.
