<!-- nctf-meta category="osint" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# wayback-diff

**Category:** osint · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

Five archived homepage captures. A developer comment carrying a base64 recovery
token was published in the 2021-03-19 capture and removed by 2021-04-02. Diffing
consecutive captures surfaces the deleted token; base64-decoding it is the flag.

## Technique

Web-archive diffing. The point is to look at what changed between captures, not
to read each in isolation — the secret only lives in one snapshot before being
scrubbed. A decoy base64 (`analytics token`) is present in every snapshot and
must be ignored precisely because it is never removed.

## Step by step

1. Extract all long base64-looking tokens from each snapshot.
2. For each consecutive pair, compute `tokens(older) - tokens(newer)` — tokens
   that were removed.
3. The scrubbed token appears between `snapshot_2021-03-19.html` (inside
   `<!-- TODO remove before prod: recovery=... -->`) and `snapshot_2021-04-02.html`.
4. Base64-decode it → the flag.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
