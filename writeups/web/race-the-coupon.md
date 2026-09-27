<!-- nctf-meta category="web" difficulty="medium" points="400" author="ctf-2026" stub="0" -->

# race-the-coupon

**Category:** web · **Difficulty:** medium · **Challenge id:** `web-race-the-coupon`

## TL;DR

The single-use cash-out coupon is validated with a non-atomic check-then-act.
Fire ~15–30 concurrent `POST /api/coupon/redeem` requests; several pass the
"already redeemed? / balance ≥ 60?" check while the balance is still 100, then
each commits a 60-credit withdrawal, overdrawing the wallet. The server emits
the per-team flag once the persisted balance is `< 0`.

```
python3 solve.py http://HOST:PORT
```

## The bug

`POST /api/coupon/redeem` (`app.py`) does:

1. **CHECK** — read `redeemed` and `balance`; reject if already redeemed or
   `balance < 60`.
2. a processing window (`time.sleep`, models a call to the payment processor).
3. **ACT** — `balance -= 60`; `redeemed = True`.

There is no lock held from step 1 through step 3. Under concurrency, many
requests execute step 1 while `balance == 100` and `redeemed == False`, all pass,
then all execute step 3. The coupon is "single-use", yet N requests each
withdraw 60. Start 100, two commits → −20. Overdraft → flag.

A single honest client can only ever reach `balance == 40`, so the negative
balance is unreachable without genuine concurrency. Static reasoning about the
code tells you the bug exists, but the flag is only issued by the server after
it observes the effect (`balance < 0`) on the live per-team instance — there is
no expected payload and nothing to grep offline.

## Why concurrency is mandatory

- The flag string never appears in any downloadable artifact. It is derived in
  the container from `TEAM_SECRET` and returned by the API **only** when the
  persisted wallet balance is strictly negative.
- The success oracle checks the _effect_ (overdrawn wallet), not a request
  shape. Any interleaving that overdraws wins; there is no "correct payload".
- One request, or many _sequential_ requests, can never drive the balance below 40. You must win the read-then-write race.

## The decoy

`POST /api/promo/apply` is a legacy "promo engine" that looks injectable and
happily echoes an inflated `display_balance` (and jumps to 999999 if you throw
SQL-ish characters at it). It is a honeypot: it never reads or writes the real
wallet and never emits a flag. Refute it in seconds — hit it with any payload,
then `GET /api/wallet` and see the authoritative balance is unchanged and still
non-negative. Ignore it and race the coupon.

## Solve output (example)

```
[*] start balance: 100
[*] 4/20 redemptions committed (single-use coupon!)
[*] final balance: -140  withdrawals: 4
[+] FLAG: NCTF{…}
```

Number of committed redemptions varies run to run with scheduling; anything ≥ 2
overdraws. Use `POST /api/reset` (instant, no cooldown, does not change the
flag) to retry from a clean 100.

## What an LLM does well / badly here

- **Well:** reading `app.py` and naming the vulnerability class ("TOCTOU race
  on the coupon redemption") is immediate for any capable model, and it will
  write a correct threaded solver on the first try.
- **Badly / the actual work:** the flag cannot be produced by reasoning. It is
  gated behind an _effect on a live, per-team instance_, so the team must
  actually launch their instance, drive real concurrent traffic at it, and win a
  scheduling race under the server's threading model. A pure "paste the source,
  read back the flag" workflow yields nothing. An agent that is given network
  access to the instance and told to run the solver will solve it — this
  challenge is "costly, not impossible" per the guardrails: it removes the
  offline/one-prompt path, not the assisted path.

## Reproduce locally

```bash
docker build -t ctf-race-the-coupon:latest .
TEAM_SECRET=playtest docker compose up -d
python3 solution/solve.py http://localhost:8080
# expected flag: NCTF{…}
TEAM_SECRET=playtest python3 flag.py   # prints the same value
```
