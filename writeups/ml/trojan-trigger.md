<!-- nctf-meta category="ml" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# trojan-trigger

**One-liner:** Activation maximization reduces to `E @ x = m`; the least-squares
solution is the planted trigger, whose bytes are the flag.

## Technique

Backdoor/trojan trigger recovery by activation maximization. The score
`c - ||E @ x - m||^2` peaks where `E @ x = m`. Because `E` has full column rank,
the pseudo-inverse gives the exact trigger.

## Steps

1. Load `E`, `m` from `detector.npz`.
2. Compute `x = pinv(E) @ m`.
3. Round to integers and read as ASCII.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
