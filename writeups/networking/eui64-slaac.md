<!-- nctf-meta category="networking" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# eui64-slaac

**Summary:** Derive each host's SLAAC IPv6 address via the EUI-64 rule, sort by
address, and read the per-host `tag` characters in order.

## Technique

SLAAC forms the 64-bit interface identifier from a 48-bit MAC using **EUI-64**:

1. Split the MAC into OUI (bytes 0–2) and NIC (bytes 3–5).
2. Insert `0xFF 0xFE` between them.
3. Flip the **universal/local** bit (`0x02`) of the first octet.

The full address is `prefix (2001:db8:ac1d:64::/64)` + this interface id. All
hosts share one prefix, so ordering is determined entirely by the interface id.

## Steps

1. Parse `hosts.json`.
2. For each host, compute the EUI-64 interface id from the MAC and build the
   full 128-bit address.
3. Sort hosts ascending by address.
4. Concatenate each host's `tag` in sorted order.

Sorting by the raw MAC (skipping the bit flip / `ff:fe` insertion) yields a
different, wrong ordering — the bit flip is what the challenge tests.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
