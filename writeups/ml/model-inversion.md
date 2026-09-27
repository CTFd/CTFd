<!-- nctf-meta category="ml" difficulty="hard" points="500" author="dagbanjaphet" stub="0" -->

# model-inversion

**Category:** ml · **Difficulty:** hard · **Challenge ID:** `ml-model-inversion`

## TL;DR

A confidence oracle leaks a **bilinear similarity** between your probe and a
sealed record `r` the model memorised. Invert the softmax to read the SEALED
logit, probe the `D=24` coordinate directions to read `u = M·(r/255)`, then solve
the linear system with the white-box metric `M = EᵀE` to get `r = 255·M⁻¹u`. Hand
`r` back to `/submit`; the server checks the _effect_ (does the returned record
match the memorised one within L-inf 2) and emits the per-team flag.

## The oracle

`model.py` (shipped, white-box) is the exact scorer, minus the record:

```
s(p)          = (p/255)ᵀ M (r/255) + C0        # M = EᵀE (24×24, symmetric PD), C0 = -1.5
P(SEALED | p) = softmax([0, s(p)])[1] = sigmoid(s(p))
```

`E` (40×24) ships in `weights.npz`; `M = EᵀE` is common to every team. The record
`r` (24 bytes, 0..255) is per-team, derived from the instance secret at start-up,
and **never** returned by `/query` or present in any file.

## The inversion

The SEALED logit is _linear in `r`_, so a handful of well-chosen probes pin it
down exactly.

1. **Invert the softmax.** For any probe, `s(p) = ln(P_SEALED / P_OTHER)` (the
   OTHER logit is fixed at 0). The API returns exact doubles, so this is noiseless.
2. **Cancel the bias.** A baseline probe `p = 0` gives `s(0) = C0`.
3. **Read one coordinate of `M·(r/255)` per probe.** Probe with `p = 255·eᵢ`
   (attribute `i` set to 255, the rest 0). Because `(p/255) = eᵢ`,
   `s(255 eᵢ) − s(0) = eᵢᵀ M (r/255) = (M·(r/255))ᵢ`. Twenty-four such probes plus
   the baseline (25 queries) give the whole vector `u = M·(r/255)`.
4. **Solve the linear system.** `M` is known white-box and positive definite, so
   `r = 255 · M⁻¹ u`. Round to the nearest byte, clip to 0..255. Recovery is
   **exact** (max error 0 in testing).

`solve.py` implements exactly this (`recover()` is ~8 lines) and then POSTs the
record to `/submit`.

## The trap

`u = M·(r/255)` is **not** `r/255`, because `M` is not diagonal — the confidence
mixes every attribute of the record together. A tempting shortcut is to treat the
per-coordinate probe response as that coordinate's value (i.e. assume the identity
metric and submit `round(255·u)`). That yields an L-inf error of **~200–250** from
the true record and is rejected. You must actually form `M = EᵀE` and invert it.
This is the intended discriminator: the "similarity, not readout" note in the
description and handout is the whole puzzle. Other one-shot mistakes that fail:

- forgetting the **baseline** subtraction (off by the bias `C0` on every coordinate);
- forgetting to **invert the softmax** and treating the probability as the logit;
- reimplementing the scorer with the wrong normalisation instead of using the
  shipped `model.py`.

## Offline soundness proof

I cannot run Docker here (live run = **Lot 5**), so the attack was verified
statically against the _actual_ server code:

```
$ python3 solve.py --offline
team alpha   : recovered L-inf=0 (<=2 unlocks) | identity-metric trap L-inf=201
team bravo   : recovered L-inf=0 (<=2 unlocks) | identity-metric trap L-inf=250
team charlie : recovered L-inf=0 (<=2 unlocks) | identity-metric trap L-inf=253
[offline] all teams recovered exactly, trap fails: True
```

`solve.py --offline` builds `Vault` from the real `weights.npz`, derives each
team's record with the server's own `derive_record`, uses `Vault.confidence` as
the oracle (identical to what `/query` calls), and confirms `recover()` returns
the record exactly for several distinct team secrets — while the identity-metric
shortcut fails by a wide margin.

The full HTTP path was also exercised via the Flask test client: `recover()`
against `/query` reproduced the instance's in-memory record exactly, `/submit`
returned `NCTF{…}` only for a matching record (and for a record perturbed by ≤2),
`/query` never contained the flag or record, and `flag.py` reproduced the
instance's flag from `TEAM_SECRET`.

## Live run (Lot 5)

```
docker compose up --build
python3 solution/solve.py http://localhost:8080
# -> [+] recovered record: [...]
# -> [*] server: {"flag":"NCTF{…}","linf":0,"ok":true, ...}
```

## Why the server-side oracle matters

The flag is in no downloadable file. `/submit` verifies an **effect** — "the
record you returned matches the memorised one" — not a payload shape. The
embedding/metric are common to all teams (the artifact is the challenge); only
the memorised record and the flag are per-team, both derived from
`CHALLENGE_SECRET`, and they are independent projections of it (the record is
`HMAC(secret, "model-inversion-record|i")`; the flag body is `CHALLENGE_SECRET[:24]`).
So a record lifted from another team's instance is worthless, and the flag can
only be obtained by actually inverting your own oracle.

## Files

- `solve.py` — self-contained solver: softmax inversion + coordinate probing +
  `M⁻¹` solve; hits a live instance, or `--offline` for the soundness proof.
- Model builder `../app/build_model.py` (also run at image build) constructs the
  team-common embedding deterministically; `../app/model.py` holds the exact
  scorer and the per-team record derivation.
