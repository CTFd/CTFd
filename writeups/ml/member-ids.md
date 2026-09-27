<!-- nctf-meta category="ml" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# member-ids

**One-liner:** Members have distinctly low loss; read their tags in id order.

## Technique

Membership inference via a loss threshold. A model overfits/memorizes its
training data, so members score a much lower per-record loss than held-out
records. The loss distribution is bimodal with a clear gap.

## Steps

1. Load `record_id`, `loss`, `tag` from `shadow_eval.npz`.
2. Threshold the loss (members are the low cluster, `loss < 0.4`).
3. Take the member records, sort them by `record_id` ascending.
4. Concatenate their `tag` characters.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
