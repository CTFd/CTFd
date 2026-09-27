<!-- nctf-meta category="ppc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# semiprime-sweep

Factor each shipped semiprime; the smaller prime of each (mod 256) is the
keystream that decrypts the flag.

## Technique

`semiprimes.txt` starts with `CIPHER <hex>`, then one semiprime `n = p*q` per
line with `10^4 <= p < q <= 10^6` (so `n <= ~10^12`). The flag was XOR-encrypted
with the keystream `smaller_prime % 256`, one byte per line, in order.

## Steps

1. Read the ciphertext and the list of semiprimes.
2. For each `n`, trial-divide by 2 then odd numbers up to `sqrt(n)`; the first
   divisor found is the smaller prime factor.
3. Keystream byte = `smaller_prime % 256`.
4. XOR the keystream against the ciphertext bytes.

Run `python3 solution/solve.py` (pure standard library; finishes in well under a
second).

## Complexity

`O(count * sqrt(n)) = ~40 * 10^6` divisions worst case — sub-second. Pollard's
rho would be faster but is unnecessary here.

## Flag

`NCTF{…}`
