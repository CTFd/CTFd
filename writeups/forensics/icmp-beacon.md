<!-- nctf-meta category="forensics" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# icmp-beacon

**Category:** forensics · **Difficulty:** medium
**Flag:** `NCTF{…}` (static)

## One-line summary

A covert channel hides one flag byte per ICMP echo request at payload offset 8;
order the requests to the covert host by ICMP sequence number and read the byte
out of each.

## Technique

ICMP data-payload exfiltration. Two hosts are pinged. `192.168.50.10` gets
ordinary pings whose payload is the normal `0x08 0x09 0x0a ...` filler pattern.
`192.168.50.200` gets pings whose payload is the same filler _except_ that byte
index 8 has been replaced with a printable flag character. The ICMP sequence
number (0..N) records each byte's position, and the packets are shuffled on the
wire, so sorting by sequence number is required.

## Step by step

1. In Wireshark: `icmp.type == 8 && ip.dst == 192.168.50.200` selects the covert
   echo requests (34 of them).
2. Sort by `icmp.seq`.
3. From each, take payload byte at offset 8 (the byte right after the 8-byte ICMP
   header, i.e. the 9th data byte). It is a printable ASCII character.
4. Concatenate in sequence order -> the flag.

The pings to `192.168.50.10` and the type-0 echo replies are noise.

## Reproducing / solver

Both `src/gen.py` (writer) and `solution/solve.py` are pure stdlib — the pcap is
built and parsed by hand, no scapy.

```
python3 solve.py ../icmp.pcap
```

## Flag

`NCTF{…}`
