<!-- nctf-meta category="ml" difficulty="hard" points="500" author="dagbanjaphet" stub="0" -->

# adversarial-gate

**Category:** ml · **Difficulty:** hard · **Challenge ID:** `ml-adversarial-gate`

## TL;DR

White-box, targeted, L-inf-bounded adversarial example against a small CNN.
Craft a 32x32 badge within L-inf 8 of the shipped `DENIED` badge that the
classifier reads as `GRANTED`, wrap it in the invented **QGP1** container, and
POST it. The server verifies the _effect_ (epsilon bound + GRANTED
classification) and only then emits the per-team flag.

## The gate

`gatemodel.py` (shipped) is the exact classifier, in pure NumPy:

```
preprocess: (pixel/255 - 0.5)/0.5
conv1 1->8 3x3 pad1 + ReLU ; maxpool2
conv2 8->16 3x3 pad1 + ReLU ; maxpool2
flatten(1024) -> fc(6)
classes: 0 DENIED, 1 STAFF, 2 VISITOR, 3 CONTRACTOR, 4 AUDITOR, 5 GRANTED
```

It exposes `logits_and_input_grad(img, target)` returning the analytic gradient
of `logit[target]` with respect to the raw uint8 pixels — everything a
gradient-based attack needs, no autograd framework required. Because the server
runs this same NumPy code, a locally successful example transfers exactly.

## Step 1 — reverse the QGP1 container

`/submit` only accepts a QGP1 packet. The handout ships six `.gatepkt` samples
and two decoded `.npy`. Decoding a sample naively and diffing against its `.npy`
exposes three non-standard conventions (all confirmable from the corpus):

1. **rows are stored bottom-to-top** when `flags & 1` (every sample sets it) —
   the pixel plane is upside down;
2. **`hdr_sum` (bytes 8:10) checksums the header only** (`sum(bytes[0:8]) &
0xFFFF`), not the body;
3. **`rec_count` (bytes 10:12) counts records (== nrows)**, not bytes.

Each record is `[len=ncols][ncols pixel bytes]`. The encoder is ~15 lines
(`qgp1_encode` in `solve.py`). Get any of the three quirks wrong and the gate
replies with a specific decode error, which is a fast feedback loop.

## Step 2 — targeted, integer-projected PGD

The DENIED badge is confidently DENIED. Two traps:

- **Untargeted / single-step attacks land on STAFF, not GRANTED.** STAFF is the
  nearest decision boundary; increasing the loss walks you there. You must
  _target_ GRANTED (ascend `logit[GRANTED]`).
- **The epsilon check is on the integer pixel plane.** A float perturbation
  that is "just inside" epsilon before rounding can leave the ball or lose the
  attack after quantizing to uint8. Project to integers _inside_ the loop and
  keep a margin.

PGD that works:

```python
x = denied.astype(float)
for _ in range(200):
    xi = np.clip(np.round(x), 0, 255).astype(np.uint8)   # integer projection
    logits, g = model.logits_and_input_grad(xi, GRANTED)
    if xi is best-so-far and argmax==GRANTED: keep it
    x = np.clip(np.clip(x + np.sign(g), denied-8, denied+8), 0, 255)
```

This finds a badge with GRANTED margin ~17 at L-inf exactly 8.

## Step 3 — submit

`base64(qgp1_encode(adv))` to `POST /submit`. On GRANTED the server returns the
flag.

```
$ python3 solve.py http://HOST:8080
[*] denied badge classified as DENIED
[+] adversarial badge: class=GRANTED margin=17.49 Linf=8 (<= 8)
[*] server: {"flag":"NCTF{…}", "ok":true, "predicted":"GRANTED", ...}
```

## Why the server-side oracle matters

The flag is not in any downloadable file. `/submit` verifies an **effect** —
"a badge inside the epsilon ball is classified GRANTED by the real model" — not
a payload shape. There is no expected-payload string to match; any valid
adversarial example is accepted. The weights and DENIED badge are common to all
teams (the artifact is the challenge); only the flag is per-team:
`flag = "NCTF{…}"`.

## The decoy

Class **STAFF** is a genuine attractor: any untargeted or single-step FGSM
attempt within epsilon flips DENIED -> STAFF, which the gate refuses. It costs
no attempt (submissions are unlimited and unpenalised) and is refutable in one
submission — the response literally says `classified STAFF, not GRANTED` — but
it will fool a solver that forgets to target GRANTED specifically.

## Honest note on LLM/agent difficulty

Adversarial examples are squarely in an LLM's wheelhouse: a capable agent given
white-box weights will reach for PGD and, because the model is small and
near-linear in the epsilon ball, likely find a GRANTED example. This challenge
is **not** claiming that's infeasible. The friction is in _composing_ several
correct steps, each of which a one-prompt attempt tends to get wrong:

- assuming a standard image container and dumping raw pixels (QGP1 rejects it —
  bottom-to-top rows, header-only checksum, record-count length);
- running an **untargeted** attack and landing on the STAFF decoy;
- optimizing in float and submitting before an integer projection, so the
  quantized packet either exceeds epsilon or loses the flip;
- mismatching the `(x/255-0.5)/0.5` preprocessing if the model is reimplemented
  instead of using the shipped `gatemodel.py`.

A strong agent that reads the handout carefully will still solve it; a naive
"write me an FGSM attack on this model" prompt will not, because it will miss
the container, the target class, or the integer bound. The intended
discriminator at this difficulty is _careful assembly_, not a novel technique.

## Files

- `solve.py` — self-contained solver: QGP1 encoder + integer-projected targeted
  PGD, hits a live instance.
- Author asset builder: `../gen_assets.py` (not shipped to players) constructs
  the weights so a solution provably exists (the checkerboard badge `t` inside
  the epsilon ball is trained to score GRANTED) and confirms the STAFF decoy.
