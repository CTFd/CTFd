<!-- nctf-meta category="ml" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# poison-shift

**One-liner:** Poisoned rows are the large-residual outliers of a linear fit;
their tags in id order spell the flag.

## Technique

Data poisoning detection via residual/influence analysis. The clean rows lie
exactly on a hyperplane; the poisoned rows have labels pushed far off it, so
under a least-squares fit they stand out as extreme residuals.

## Steps

1. Load `record_id`, `X`, `y`, `tag` from `poisoned_train.npz`.
2. Fit `y ~ [X, 1]` by least squares and compute absolute residuals.
3. Flag rows whose residual is many MADs above the median (robust cutoff).
4. Sort the flagged rows by `record_id` ascending and read their `tag`
   characters.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
