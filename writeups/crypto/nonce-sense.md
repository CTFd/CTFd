<!-- nctf-meta category="crypto" difficulty="medium" points="150" author="ctf-2026" stub="0" -->

# nonce-sense

**Category:** crypto · **Difficulty:** easy · **id:** `crypto-nonce-sense`
**Flag:** `NCTF{…}`

## What you get

`capture.json` contains, for secp256k1:

- the device public key `Q = d·G`,
- the group order `n`,
- 62 ECDSA signatures `(r, s)` over known messages, with
  `z = int(sha256(msg)) mod n`.

Goal: recover the private key `d`. The flag is
`NCTF{…}`.

## The bias (the actual vulnerability)

ECDSA: `s = k⁻¹ (z + r·d) mod n`, so for each signature

```
k = s⁻¹·z + s⁻¹·r·d  (mod n)  =  a + t·d  (mod n)
    with  a = s⁻¹·z,  t = s⁻¹·r.
```

The device's RNG is broken so that **every nonce `k` has its most significant
byte forced to zero**, i.e. `0 < k < 2²⁴⁸` on a 256-bit curve. You are not told
this; you infer it. Two cheap ways to notice:

- The challenge says the RNG is broken and hands you _many_ signatures — the
  textbook setup for the Hidden Number Problem (HNP), which only bites when the
  nonces are _small / partially known_.
- If you already know `d` for a test key you can confirm `k = a + t·d mod n`
  lands below `2²⁴⁸` every time; here the structure is what you solve _for_.

Knowing `k = a + t·d (mod n)` with `k` small is exactly HNP. With an 8-bit bias
you need more than `256/8 = 32` signatures for the target to become the shortest
lattice vector; the capture gives 60 usable ones so there is comfortable margin.

## The decoy (refute it in a minute)

Scan the `r` values: **two signatures share an identical `r`.** Identical `r` is
the classic tell for a _reused nonce_, which would let you solve instantly from
just those two signatures:

```
k = (z1 - z2) / (s1 - s2) mod n ;  d = (s1·k - z1) / r mod n
```

Do it and you get a `d'`. Check it against the public key: `d'·G ≠ Q`. **Refuted.**

Why it fails: `r = x(k·G)`, and `x(k·G) = x((n−k)·G)`. So two signatures whose
nonces are `k` and `n−k` produce the _same_ `r` while using _different_ nonces.
It is not a reused nonce, and those two nonces are full-range (top byte `0xff`
for `n−k`), so they are **not** biased — they must be dropped, not exploited.
The solver removes any `r` seen more than once and works on the remaining 60.

## The lattice

Pick sig 0 as reference, eliminate `d` via `d = (k₀ − a₀)·t₀⁻¹`:

```
k_i = c_i·k₀ + e_i (mod n),   c_i = t_i/t₀,  e_i = a_i − c_i·a₀.
```

Every `k_i` is `< 2²⁴⁸`, so recentering `k_i' = k_i − 2²⁴⁷` gives
`|k_i'| < 2²⁴⁷`. The vector `(k₀', k₁', …, k_{m-1}', K)` is a short vector of the
`(m+1)`-dimensional lattice with rows

```
R0  = [ 1,  c_1, c_2, …, c_{m-1},  0 ]
R_i = [ 0, … n at column i … ,      0 ]   (i = 1 … m-1)
R_e = [ 0,  e_1', e_2', …, e_{m-1}', K ]   (K = 2²⁴⁷, Kannan embedding)
```

Entries are only `~n` (≈2²⁵⁶), which keeps a pure-Python integer-LLL tractable.
Reduce, then for each short row read a candidate `k_i' `, undo the shift, compute
`d = (k_i − a_i)·t_i⁻¹ mod n`, and accept the one with `d·G = Q`.

## Solve

```
cd solution
python3 solve.py ../capture.json
```

`solve.py` is self-contained pure Python: secp256k1 arithmetic + a de Weger /
Cohen (Alg. 2.6.7) **integer LLL** with `δ = 0.99`. If `fpylll` is installed it
is used automatically and the reduction is sub-second; otherwise the bundled
integer-LLL runs (slower — tens of seconds to a few minutes depending on how
many signatures you feed it; `M=<n>` env var picks the subset size).

Expected output ends with:

```
[+] private key d = 0x690ba66683c56d39767739a1d314a86adea774001ead3aaceb43fb0304a338cb
[+] FLAG = NCTF{…}
```

## Honest note on LLM-assisted solving

"Biased-nonce ECDSA → HNP → LLL" is a pattern a strong LLM recognises
immediately, and it can usually emit a Sage/fpylll HNP solver. What this
challenge makes the solver _earn_:

1. **Identify the bias magnitude from evidence.** The word is only "broken RNG".
   The solver must determine it's a _high-bit_ bias of exactly 8 bits (top byte
   zero) and size the lattice accordingly. An 8-bit bias is near the boundary:
   too few signatures and LLL returns garbage, so the model has to reason about
   _how many_ signatures / what `δ` are needed, not just paste a template.
2. **Not fall for the decoy.** A one-shot "I see a repeated `r`, here's the
   nonce-reuse recovery" answer produces a wrong key. The correct move — repeated
   `r` means `k` and `n−k`, i.e. _not_ reuse, and those samples are non-biased and
   must be excluded — requires actually checking the candidate against `Q`.
3. **Ship a reduction that runs.** In an environment without fpylll/Sage the
   naive fraction-LLL an LLM tends to write is `O(n⁵)` and does not finish; a
   working solve needs an integer LLL. (We ship one.)

So it is not one-prompt-trivial, but a careful agent that verifies against the
public key will get it. That is the intended "easy" ceiling.
