<!-- nctf-meta category="crypto" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# commit-bias

## TL;DR

The CoinVault dealer commits to a per-round "draw" `Y_r ∈ F_p`, opens 48 rounds,
and seals a final **vault** round it never opens. The vault flag blob is XOR-
sealed under `key = SHA256(Y_vault)`, so the whole challenge is: **recover the
un-opened draw `Y_vault`.**

The dealer claims each draw is an independent fresh sample. It is not. The
opened draws are the output stream of a fixed **order-k linear recurrence over
`F_p`** with secret coefficients:

```
Y_r = ( c_1·Y_{r-1} + c_2·Y_{r-2} + ... + c_k·Y_{r-k} )   (mod p)
```

That is the bias. The draws are linearly dependent, so the commitments buy the
dealer nothing once you have enough opened rounds.

## Attack

1. **Parse** `ledger.coinvault` (see `../handout/SPEC.md`): read the prime `p`,
   the 48 opened draws `Y_0..Y_47`, and the vault line (`IDX`, commitment `C`,
   ciphertext `CT`). Recompute each opened commitment to confirm the encoding.

2. **Recover the recurrence.** Run **Berlekamp–Massey over `F_p`** on the opened
   draw stream. With 48 samples and order `k = 7`, the minimal recurrence is
   found unambiguously (BM needs only `2k` terms). Confirm the recovered
   coefficients reproduce every remaining opened draw.

3. **Extrapolate.** Iterate the recurrence forward past round 47 to compute the
   un-opened vault draw `Y_vault = Y_48`.

4. **Verify for free.** The vault line publishes `C = SHA256(Y_vault || 48)[:16]`.
   Recompute it from the predicted `Y_vault`; it matches, proving the prediction
   is exact — no guessing.

5. **Unseal.** `key = SHA256(Y_vault_bytes)`, generate the SHA-256 counter-mode
   keystream, XOR with `CT`, and read the flag.

Why this isn't brute force: `p` is 256-bit, so guessing `Y_vault` (or the key,
or the flag) directly is infeasible. The only way in is to notice the linear
dependence among the "independent" draws and solve for the hidden recurrence.

## Run

```
python3 solve.py            # defaults to ../handout/ledger.coinvault
python3 solve.py /path/to/ledger.coinvault
```

Output:

```
[*] parsed 48 opened draws over a 256-bit field; all commitments verify
[*] recovered a hidden order-7 linear recurrence over F_p
[*] recurrence reproduces all opened draws
[+] predicted sealed draw y_48 matches the vault commitment
[+] FLAG = NCTF{…}
```

## Files

- `../gen.py` — deterministic builder for the ledger + flag (not shipped).
- `../handout/ledger.coinvault`, `../handout/SPEC.md` — the player handout.
- `solve.py` — this reference solver (Python stdlib only, sub-second).
