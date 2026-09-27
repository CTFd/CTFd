<!-- nctf-meta category="networking" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# bgp-bestpath

**Summary:** Run the BGP best-path decision process per prefix, take the winning
route's `label`, and read them in prefix order.

## Technique

The RIB lists multiple routes per prefix. The winner is chosen by this trimmed
BGP decision process (applied as a sort key, first difference wins):

1. highest `local_pref`
2. shortest `as_path` length
3. lowest `origin` (igp < egp < incomplete)
4. lowest `med`
5. lowest `peer_id` (final tie-break)

The trap is step 1 vs step 2: some prefixes have a route with a longer AS path
but a higher LOCAL_PREF, which still wins. Sorting purely by AS-path length
gives the wrong answer.

## Steps

1. Parse `bgp_rib.json`.
2. For each prefix, select the route minimizing
   `(-local_pref, len(as_path), origin_code, med, peer_id)`.
3. Sort prefixes by numeric network address.
4. Concatenate the winners' `label` fields.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
