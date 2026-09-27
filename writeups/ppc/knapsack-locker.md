<!-- nctf-meta category="ppc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# knapsack-locker

The optimal 0/1-knapsack value is the key that decrypts the shipped ciphertext
into the flag.

## Technique

`items.txt` has `CAP <W>`, `N <count>`, then one `weight value` line per item,
then `CIPHER <hex>`. The flag was XOR-encrypted with a SHA-256 keystream seeded
by the decimal string of the optimal achievable value. Any wrong value produces
a completely different keystream, so only the correct DP recovers the flag.

## Steps

1. Parse the capacity, the items, and the ciphertext bytes.
2. Solve 0/1 knapsack with the standard 1-D DP:
   `dp[c] = max(dp[c], dp[c - w] + v)`, scanning `c` downward for each item.
   The answer is `dp[CAP]`.
3. Build the keystream: repeatedly `SHA-256(str(V) + counter.to_bytes(4))`,
   incrementing the counter, until you have enough bytes.
4. XOR the keystream against the ciphertext.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

`O(N * CAP)` = 60 x 2000, instant.

## Flag

`NCTF{…}`
