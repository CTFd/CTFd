<!-- nctf-meta category="ai" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# oracle-multi-turn

**Summary:** The guard weakens across a session. A benign priming turn that
establishes an "authorized audit" context flips `primed`, after which a
properly phrased request is honoured.

## Vulnerability

`Session` keeps `primed` state between turns. `respond` refuses a token request
on a cold session, but `_is_priming` treats any message mentioning both
`authorized` and `audit` as establishing context and sets `primed=True`. A
later request that avoids the forbidden words (`flag`, `secret`, ...) and asks
for the `diagnostic token` is then answered. The 2-step ordering is the whole
puzzle: request-then-prime fails; prime-then-request succeeds.

## Steps

1. Create a `Session`.
2. Turn 1 (prime): send a benign message mentioning an "authorized" "audit".
3. Turn 2 (ask): request the "session diagnostic token", avoiding banned words.

Run:

```
python3 solution/solve.py
```

## Flag

`NCTF{…}`
