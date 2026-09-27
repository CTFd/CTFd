<!-- nctf-meta category="networking" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# dns-chain

**Summary:** Parse the raw DNS message (with name compression), follow the CNAME
chain from the question name, and concatenate the TXT string at each hop.

## Technique

The artifact is a DNS response in RFC 1035 wire format:

- 12-byte header: id, flags, then QD/AN/NS/AR counts.
- Question: encoded name + qtype + qclass.
- Answer RRs: name, type(2), class(2), ttl(4), rdlength(2), rdata.

Names are **compressed**: a length byte with the top two bits set (`0xC0`) is a
14-bit pointer to an earlier offset in the message. The owner names all share the
`.flag.nctf` suffix via such pointers, so a parser that does not follow pointers
reads garbage.

The answer section contains, in shuffled order, a CNAME chain
(`h00 -> h01 -> ... -> h09`) and a TXT record for each name. Walking the chain
from the question name and collecting each name's TXT string reassembles the flag.

## Steps

1. Read `message.bin`.
2. Parse header, skip the question (reading its name).
3. For each answer RR, read the owner name (following compression), then by type
   record CNAME targets (type 5) and TXT strings (type 16).
4. Start at the question name; append its TXT, follow its CNAME, repeat.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
