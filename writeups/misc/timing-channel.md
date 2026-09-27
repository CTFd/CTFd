<!-- nctf-meta category="misc" difficulty="medium" points="300" author="ctf-team" stub="0" -->

# Heartbeat

**Flag:** `NCTF{…}`

## The trap

The handout `capture.pcap` is a one-directional stream of UDP heartbeat
datagrams from an agent (`192.0.2.50`) to a collector (`198.51.100.10:9999`).
Every datagram carries the same banner plus a monotonic `seq=` counter. The
bytes are deliberately information-free — decoding, XOR-ing, or diffing the
payloads leads nowhere, and the `seq=` counter is just `0,1,2,...`. The
description says as much: _the secret isn't in what was said._

The signal is **when** each datagram arrives.

## The channel

Look at the inter-arrival gaps between consecutive datagrams. They fall into
two tight clusters with an empty valley between them (a bimodal distribution):

- a **short** gap (~40 ms) = bit `0`
- a **long** gap (~180 ms) = bit `1`

You do not need to know the exact threshold: sort the gaps and cut at the widest
empty band (~110 ms here). Reading the bits in capture order, MSB-first, 8 bits
per byte, decodes straight to ASCII.

With N characters in the flag there are `8*N` gaps and `8*N + 1` datagrams
(the first datagram has no preceding gap and carries no bit).

## Run it

```
pip install scapy
python3 solve.py ../capture.pcap
```

Expected output:

```
[*] gaps            : 272
[*] inferred split  : 110.0 ms (short~40ms x125, long~179ms x147)
[*] decoded (MSB-first, 8 bits/char):
    NCTF{…}
[+] FLAG: NCTF{…}
```

## Rebuilding the handout

`gen.py` (one directory up) rebuilds `capture.pcap` deterministically from the
flag string and a fixed RNG seed. It is an author tool and is **not** shipped in
`files:`. No flag text appears anywhere in the delivered capture — it exists
only as the timing pattern.
