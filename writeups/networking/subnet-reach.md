<!-- nctf-meta category="networking" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# subnet-reach

**Summary:** Longest-prefix-match each packet against the forwarding table; the
packets whose best route action is `local` reach the host. Read their tags in
`id` order.

## Technique

Routers select one route per packet by **longest prefix match**: among all
routes whose network contains the destination, the one with the largest
prefix length wins. Here the winning route's `action` decides fate:

- `local` — delivered onto the target host's segment (reaches the host)
- `gw:<ip>` — forwarded to a different next hop (does not reach)
- `null0` — black-holed / dropped

Overlapping prefixes make this non-trivial: `10.0.7.0/24` is `local`, but the
more specific `10.0.7.128/25` points at a gateway and `10.0.7.66/32` is a
black hole. So a naive "is it in the /24" test is wrong.

## Steps

1. Parse `routing.json`.
2. For each packet, find the route with the longest matching prefix.
3. Keep packets whose best action is `local`.
4. Sort by `id`, concatenate tags.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
