<!-- nctf-meta category="web" difficulty="medium" points="400" author="Hibris" stub="0" -->

# reseau-pyramide

**Category:** web · **Class:** business-logic / anti-fraud bypass (MLM economy)
· **Serving:** per-team Docker instance (`type: team_instance`), team_hmac flag.

## Idea

A fictional Togolese network-marketing platform, **KékéliCash**. You get a
distributor account `ROOT` seeded with 50 000 FCFA. Commissions (20 % / 8 % / 4 %
over three sponsor levels) are paid up the chain when a member buys. The house
keeps the rest of every purchase, so **legitimate play is a net loss** — and
because registration accepts any Togolese-looking phone number without
verification, you can create unlimited fake members, but self-funding a downline
still loses money (68 % leaks to the house each purchase). Volume alone gets you
nowhere; you must find a flaw that _creates_ money.

The flag is released on `GET /flag` once your balance clears the jackpot
(1 050 000 FCFA).

## The door (necessary, not sufficient)

`POST /api/register` accepts any `^(\+?228)?[0-9]{8}$` number — **no OTP, no
SMS**. Unlimited sybil members, each with its own referral code. This is what
lets you build controlled accounts, but it mints nothing by itself.

Patched decoy: `POST /api/buy` rejects `qty <= 0` — no negative-quantity trick.

## Two independent money-minting bugs

### A. Non-idempotent activation bonus (used by solve.py)

`POST /api/bonus/activation {filleul_code}` credits the sponsor a 3 000 FCFA
bonus **every time it is called** — nothing records that the bonus was already
paid. Register one filleul under ROOT, fund + activate it (one `starter`
purchase), then replay the bonus until ROOT clears the jackpot.

### B. Refund without commission clawback

`POST /api/buy` pays the buyer's sponsor a commission immediately; `POST
/api/refund` returns the purchase price to the buyer but **does not reverse the
commission**. With buyer and sponsor both yours (sybil), each
buy→refund→transfer-back cycle nets the un-clawed commission (e.g. 4 000 FCFA per
`vip` cycle), the price just round-trips between your accounts. Loop past the
jackpot.

Both are conserved-economy violations: A mints from nothing (idempotency), B
mints the commission (missing compensating transaction).

## Run the reference solver

```
python3 solution/solve.py http://HOST:PORT   # prints NCTF{…}
```

## Lessons

Idempotency of payment/bonus endpoints; compensating transactions on refund;
and why identity verification (OTP/KYC) matters in a referral economy — the
exact anti-fraud gaps behind real pyramid-scheme platforms.

## Verification status

Verified end-to-end **offline** (no Docker needed) against the shipped Flask app:

- `solve.py` drives ROOT past the jackpot via bug A and prints the flag equal to
  the instance's `/flag.txt` (team_hmac).
- Decoy confirmed: negative quantity → 400. Flag withheld until the jackpot.
- Bug B independently verified: +4 000 FCFA per `vip` cycle (commission not
  clawed back).

Docker/Lot-5 arena rehearsal still pending (Docker unavailable in the authoring
environment) — flip `state: visible` after `deploy/scripts/lot5.sh --only
web/reseau-pyramide` passes.
