<!-- nctf-meta category="ml" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# grad-leak

**One-liner:** A linear layer's weight gradient is rank one, so a row divided by
its `dL/dy` scalar rebuilds the private input.

## Technique

Gradient leakage (deep leakage from gradients). For `y = W @ x`, the weight
gradient is the outer product `dL/dW = (dL/dy) x^T`. Every row of `grad_W` is a
scalar multiple of the input `x`.

## Steps

1. Load `grad_W` and `dL_dy` from `leaked_grads.npz`.
2. Choose a row `i` with `dL_dy[i] != 0` (use the largest magnitude for
   stability).
3. Compute `x = grad_W[i] / dL_dy[i]`.
4. Round to integers and read as ASCII.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
