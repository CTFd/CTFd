<!-- nctf-meta category="blockchain" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# allowance-drift

**Summary.** `transferFrom` never decrements the allowance, so one approval is
reusable forever. The number of `transferFrom` calls needed to drain the
victim is the key.

**Vuln / technique.** ERC20 allowance not decremented. Each call moves at most
`your_allowance` tokens; the allowance survives, so drain in
`ceil(victim_balance / your_allowance)` calls.

**Steps.**

1. Read `victim_balance = 1000000` and `your_allowance =
3000` from `token_state.json`.
2. `num_calls = ceil(1000000 / 3000) = 334`.
3. Seal key = `keystream(keccak256)` seeded by `num_calls` (32-byte
   big-endian); XOR into `cipher_hex`.

**Flag.** `NCTF{…}`
