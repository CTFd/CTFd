<!-- nctf-meta category="ml" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# tree-path

**One-liner:** Read the decision tree's leaf characters in root-to-leaf
path-index order.

## Technique

Rule/structure extraction from a serialized decision tree. The JSON stores each
node's children in a shuffled order, so a naive top-to-bottom read scrambles the
flag. Each leaf has a unique canonical position determined by its path from the
root.

## Steps

1. Parse `decision_tree.json`.
2. Depth-first walk from the root with a running index: root = 1, left child =
   `idx*2`, right child = `idx*2+1`.
3. At each leaf, record `(index, char)`.
4. Sort the leaves by index ascending and concatenate the characters.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
