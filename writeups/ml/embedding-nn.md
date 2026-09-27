<!-- nctf-meta category="ml" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# embedding-nn

**One-liner:** Each noisy query decodes to its nearest embedding row; the tokens
in order spell the flag.

## Technique

Embedding inversion by nearest-neighbour lookup. The queries are token
embeddings perturbed by small noise, and the embeddings are well separated, so
the closest table row is always the original token.

## Steps

1. Load `embeddings`, `token_char`, `queries` from `embed_table.npz`.
2. For each query, compute the squared Euclidean distance to every embedding row
   and take the `argmin`.
3. Map that row index to its `token_char` and turn it into a character.
4. Concatenate over all queries in order.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
