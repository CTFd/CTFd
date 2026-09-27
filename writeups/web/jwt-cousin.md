<!-- nctf-meta category="web" difficulty="easy" points="150" author="ctf-2026" stub="0" -->

# jwt-cousin

**Category:** web · **Difficulty:** easy · **challenge-id:** `web-jwt-cousin`

## TL;DR

The token is _not_ a JWT. It is `<payload>.<sig>` (no header). The signature is
a truncated HMAC over a **canonical claim string that the server rebuilds from
a fixed subset of the claims — and that subset does not include `role`**. So
you can take any valid token, change `role` to `admin` in the JSON payload, and
keep the original signature. It still verifies. Then you hit the admin-only
rotation endpoint, which performs the effect and returns the flag.

## Recon

Log in with the public account and look at what you get:

```
$ curl -s -X POST $URL/api/login -d '{"user":"guest","pass":"guest"}' -H 'Content-Type: application/json'
{"token":"eyJzdWIiOiJndWVzdCIsInJvbGUiOiJndWVzdCIsImV4cCI6...}.b15d480d52e040e8438691c9c1463132"}
```

Two segments, dot-separated. The first is base64url JSON:

```json
{ "sub": "guest", "role": "guest", "exp": 1789068927, "v": 1, "alg": "HS256" }
```

The second (`b15d...`) is 32 hex chars — a truncated HMAC.

### Why the JWT reflex fails (the decoy)

There is an `alg:"HS256"` claim, which baits every stock JWT attack:
`alg:none`, RS256→HS256 confusion, `jwt.io`. All of them fail here:

- There is **no header segment**, so JWT parsers choke or read the wrong bytes.
- The signature is **not** `HMAC(key, base64(header)+"."+base64(payload))`, so a
  JWT verifier signing those bytes never matches.
- The server **ignores `alg` entirely** — setting it to `none` or stripping the
  signature just yields `invalid token`.

You can refute the whole JWT line of attack in a couple of minutes: strip the
signature, set `alg:none`, and watch it get rejected. Move on.

## Finding the real signature scheme

You cannot recover the server key (per-instance, random), so forging by
_re-signing_ is out. The other question is: **what does the signature actually
cover?** Probe one claim at a time against the live oracle (`/api/whoami`
verifies without needing admin):

| mutation to a valid guest token | result       |
| ------------------------------- | ------------ |
| change `sub` (keep sig)         | invalid      |
| change `exp` (keep sig)         | invalid      |
| change `v` (keep sig)           | invalid      |
| change `alg` (keep sig)         | **verifies** |
| change `role` (keep sig)        | **verifies** |

`role` is outside the signed data. That is the whole bug: the canonical string
the server signs is `sub=<sub>;exp=<exp>;v=<v>` — `role` (the thing
authorization is decided on) is never signed.

## Exploit

1. Log in as `guest`, take the token.
2. Base64url-decode the payload, set `role` to `admin`, re-encode.
3. Re-attach the **original** signature.
4. POST it to `/api/admin/rotate`.

```
$ python3 solve.py $URL
[+] guest token: eyJ...guest....b15d...
[+] claims: {'sub': 'guest', 'role': 'guest', 'exp': ..., 'v': 1, 'alg': 'HS256'}
[+] forged admin token: eyJ...admin....b15d...
[+] rotate response: {'ok': True, 'rotations': 1, 'message': 'console rotated...', 'flag': 'NCTF{…}'}

FLAG: NCTF{…}
```

The endpoint only returns the flag after it actually flips server state
(`maintenance -> false`, rotation counter incremented) under an `admin` role —
the flag is emitted for the _effect_, not for any particular payload shape.

## Flag

Per-team: `flag = "NCTF{…}"`.
The running instance derives and returns it; `flag.py` reproduces it for
validation.

## Honest note on LLM assistance

An LLM is genuinely useful here and this is only an _easy_ challenge, so that's
expected. What an LLM does **badly**: its first instinct is JWT. Pasted into a
model cold, it burns effort on `alg:none`, key confusion, and jwt.io — all dead
ends, because there's no header and the signature isn't over the base64
segments. What an LLM does **well**, once it's told/notices this isn't a real
JWT: the "sign a subset, authorize on a field outside it" bug is a known class,
and with the live oracle to probe one claim at a time it will find that `role`
isn't covered fairly quickly. The resistance is entirely in _not_ being a JWT;
the payoff after that realization is small. It is intentionally sized as an
early-board web point, not a filter.
