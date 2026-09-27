<!-- nctf-meta category="supplychain" difficulty="medium" points="350" author="dagbanjaphet" stub="0" -->

# poisoned-pipeline

**Challenge id:** `supplychain-poisoned-pipeline` · **Category:** supplychain (new) · **Difficulty:** medium
**Served:** yes (per-team container, `type: team_instance`)

A CI/CD supply-chain challenge: an untrusted pipeline runs on a shared build
runner, and the deploy secret leaks because **log masking is treated as a
security boundary**.

## Flag derivation

Per-team, dynamic (same contract as the other served challenges): the instancier
injects `FLAG` / `CHALLENGE_SECRET`; flag body = `CHALLENGE_SECRET[:24]`. The
flag is the CI secret `DEPLOY_TOKEN`, injected only into deploy-stage steps and
masked from logs; never baked into the image. `team_hmac` (content
`supplychain-poisoned-pipeline`) validates it on submit.

## The attack (intended)

`POST /build` runs each pipeline step's `run:` on the runner.

1. `DEPLOY_TOKEN` is injected **only** into `deploy`-stage steps — a `build`-stage
   step never sees it.
2. A deploy step that `echo $DEPLOY_TOKEN` gets `***`: the runner redacts the
   **literal** secret from logs.
3. The mask only catches the literal, so a deploy step that **encodes** the
   secret first slips it through:
   `printf %s "$DEPLOY_TOKEN" | base64` (or `| rev`, `| xxd`). Decode the log →
   flag.

The runner scrubs its own `FLAG`/`CHALLENGE_SECRET`/`TEAM_SECRET` at startup, so
a step cannot read the secret from `/proc/<runner>/environ`; the only path is a
deploy-stage step past the mask.

`solve.py http://HOST:PORT` submits the base64 deploy step and decodes the flag.

## Static verification (docker daemon unavailable in the build env)

Validated at the logic level without a container build:

- **Stage-gating** — a `build`-stage step gets an empty `DEPLOY_TOKEN`; only
  `deploy` steps receive it.
- **Masking** — `echo $DEPLOY_TOKEN` in a deploy step returns `***`.
- **Env scrub** — a step reading `/proc/1/environ` finds no flag
  (`NO_FLAG_IN_PROC`).
- **Bypasses** — both `| base64` and `| rev` exfiltrate the value past the mask
  and decode/reverse back to the flag.
- **End-to-end** — `solve.py` recovers the flag against the live runner.
- **flag.py** — resolves `FLAG` / `CHALLENGE_SECRET` / dev fallback as expected.

A live `docker build` + `solve.py http://HOST:PORT` run is deferred to the arena
bring-up (`deploy/local/build-images.sh poisoned-pipeline`).
