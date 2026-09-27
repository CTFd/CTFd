<!-- nctf-meta category="ml" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# surrogate-fit

**One-liner:** Least-squares fit on the query log recovers the linear oracle's
weights, which are the flag's ASCII bytes.

## Technique

Model extraction. The oracle is a noise-free linear map `y = X @ w`. A captured
query/response log with more rows than dimensions and a full-rank design matrix
determines `w` uniquely.

## Steps

1. Load `X`, `y` from `query_log.npz`.
2. Solve `w = lstsq(X, y)`.
3. Round `w` to integers and read each entry as an ASCII code.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
