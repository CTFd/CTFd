<!-- nctf-meta category="cloud" difficulty="medium" points="450" author="dagbanjaphet" stub="0" -->

# breach-chain

**Challenge id:** `cloud-breach-chain` · **Category:** cloud (new) · **Difficulty:** medium
**Served:** yes (per-team container, `type: team_instance`)

A realistic multi-stage cloud kill chain in a single container: web SSRF →
instance metadata (IMDS) → stolen temporary credentials → flag.

## Flag derivation

Per-team, dynamic (same contract as the other served challenges): the instancier
injects `FLAG` / `CHALLENGE_SECRET`; flag body = `CHALLENGE_SECRET[:24]`. The
flag is returned **only** by `/api/admin/secrets` when the correct stolen
`Token` is presented, and is never baked into the image. `team_hmac` flag class
(content `cloud-breach-chain`) validates it on submission.

## The chain (intended)

1. **SSRF → internal IMDS.** `/fetch?url=` fetches a URL server-side. It blocks
   the literals `127.0.0.1`, `localhost`, `::1` but not `0.0.0.0`, so
   `/fetch?url=http://0.0.0.0:8169/latest/meta-data/iam/security-credentials/`
   reaches the internal metadata service (bound to `127.0.0.1:8169`, otherwise
   unreachable).
2. **IMDS creds.** Read `.../kekeli-app-role` for the app role's temporary
   credentials. There is one **decoy** role (`legacy-backup-role`) whose token
   is expired and rejected — read the right one.
3. **Replay stolen creds.** `GET /api/admin/secrets` with header
   `X-App-Token: <Token>` returns the flag. The `Token` is unguessable and only
   obtainable via the SSRF→IMDS path, so using a correctly-stolen credential is
   the win condition.

`solve.py http://HOST:PORT` runs all three stages.

## Static verification (docker daemon unavailable in the build env)

Validated at the logic level without a container build:

- **SSRF filter + bypass** — the literal `127.0.0.1` is blocked (403); the
  `0.0.0.0` bypass reaches the internal IMDS and returns the role creds.
- **Credential gate** — `/api/admin/secrets` returns 401 without a token, 401
  with the decoy's expired token, and the flag only with the app-role `Token`.
- **End-to-end** — `solve.py` chains SSRF → parse `Token` → admin → flag against
  the live app.
- **flag.py** — resolves `FLAG` / `CHALLENGE_SECRET` / dev fallback as expected.

A live `docker build` + `solve.py http://HOST:PORT` run is deferred to the arena
bring-up (`deploy/local/build-images.sh breach-chain`).
