<!-- nctf-meta category="ml" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# adv-flip

**One-liner:** The minimum-norm perturbation that moves `x0` to the gate's
decision boundary lands exactly on the flag bytes.

## Technique

Adversarial example against a linear classifier. The closest point on the
boundary `s(x) = 0` to `x0` is reached by stepping along the weight vector `w`:

```
delta = -(s(x0) / (w . w)) * w
x_adv = x0 + delta
```

The gate was constructed so this closest boundary point is precisely the flag
vector.

## Steps

1. Load `w`, `b`, `x0` from `gate.npz`.
2. Compute `s0 = w . x0 + b`, then `delta = -(s0 / (w . w)) * w`.
3. `x_adv = x0 + delta`; round to integers and read as ASCII.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
