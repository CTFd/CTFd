<!-- nctf-meta category="crypto" difficulty="hard" points="500" author="dagbanjaphet" stub="0" -->

# lcg-casino

## TL;DR

The casino's "provably fair" shuffle is a **truncated LCG**. Each hand publishes
the top 24 bits of a 40-bit internal state, encoded as an 11-card permutation.
The LCG constants are public. Recover the full running state (including the
hidden low 16 bits) from two or three published shuffles, then compute every
future hand's high card and call it. Ten correct calls in a row → the service
pays the per-team flag.

## The setup

RNG (public, from the banner / `SPEC.md`):

```
state_{n+1} = (A*state_n + C) mod M
M = 2**40,  A = 2654435761,  C = 3039632973
```

Each hand advances the state once and publishes a **rank** = `state >> L`, decoded
into a permutation of `[0..10]` by a lexicographic factorial-base (Lehmer)
decode. The permutation inverts back to exactly one rank because `2**24 < 11!`.

Two things are **not** in the spec and must be inferred from `samples.json`:

- **L, the number of withheld low bits.** Decode each sample shuffle to a rank.
  You know `A, C, M`. For the correct `L`, there is a low-bit assignment making
  the ranks satisfy the LCG relation; every other `L` is inconsistent. It works
  out to `L = 16` (rank ∈ `[0, 2**24)`), which you can also just guess from
  `40 - 24`.
- **The "high card" rule.** In every sample hand `high_card == shuffle[0]`, i.e.
  the first card off the deck. One glance confirms it.

The published `commitment = SHA-256(seed)` is a **decoy**. Inverting it is
infeasible and pointless: you recover the _state_, never the seed.

## Recovering the state

Write each observed state as `state = (rank << L) | low`, `0 ≤ low < 2**L`.
For consecutive observed ranks `r0, r1`:

```
for low in range(2**L):            # 2**16 = 65536 candidates
    x1 = (r0 << L) | low
    x2 = (A*x1 + C) mod M
    if (x2 >> L) == r1:            # matches the next observed rank
        candidate state found
```

Two reveals already pin it uniquely in practice; a third confirms with
certainty. This is a plain brute force over the 16 hidden bits — no lattice
needed at these parameters (an LLL/Stern truncated-LCG attack also works and is
the general tool when fewer bits are revealed per step).

## Winning

Once you hold the running state `x` that matches the last observed hand:

```
x = (A*x + C) mod M                # next hand's state
call = decode_shuffle(x >> L)[0]   # its high card
```

Call that every hand. You throw away the first ~3 hands collecting observations
(they miss, streak stays 0), then win 10 straight → jackpot at about hand 13.
Because the miss penalty is only a streak reset with unlimited hands, the
observation phase is free.

## Run it

```
# local
docker compose up --build            # serves on :9021
python3 solution/solve.py 127.0.0.1 9021
```

Sample run against a local instance (`TEAM_SECRET=local-demo-team-secret`):

```
[+] recovered: L=16 state=728973484044
[*] hand 13: WIN streak=10
[+] FLAG: NCTF{…}
```

The flag equals `python3 flag.py local-demo-team-secret`; in production it is the
per-team HMAC the running instance emits after the streak.

## Honest note on LLM assistance

A frontier model will name "truncated LCG state recovery" immediately and can
sketch the brute force. What it does **not** get for free:

- The flag is only obtainable by driving the **live** service to a real 10-win
  streak. There is no offline artifact to grind against overnight; the effect is
  checked server-side, so an agent must implement and run a correct live client.
- The exact bit layout (`L`) and the high-card rule are **withheld** and must be
  pinned from the sample transcript. A model that assumes the wrong split (e.g.
  treats the rank as the full state, or picks the wrong high-card index) desyncs
  on the very first prediction and never streaks.
- The custom line-delimited framing plus the strict call-before-reveal ordering
  means stock tooling (padbuster/Burp/`curl`) is useless; the solver has to be
  written from the protocol.

So an agent that is _walked through_ it can solve it, but a one-prompt "here's a
netcat line, get the flag" will not: it has to reverse the encoding from evidence
and run a stateful live attack. That combination is why it is rated hard rather
than medium.
