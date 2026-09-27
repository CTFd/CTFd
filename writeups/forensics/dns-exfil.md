<!-- nctf-meta category="forensics" difficulty="medium" points="300" author="ctf-team" stub="0" -->

# DNS Exfil

**Category:** forensics · **Difficulty:** medium
**Challenge ID:** `forensics-dns-exfil`
**Flag:** `NCTF{…}` (static)

## Artifact

`capture.pcap` — a DNS capture from an infected workstation (`10.4.7.113`)
talking to its resolver (`10.4.7.1`). Mixed traffic: benign name lookups, an
exfiltration channel, and one decoy beacon.

## Intended solve path

1. **Isolate the exfil channel.** Filter DNS **TXT** queries whose name ends in
   `x.acme-updates.net`. In Wireshark:
   `dns.flags.response == 0 && dns.qry.type == 16 && dns.qry.name contains "acme-updates.net"`.

2. **Find the handshake.** One query is
   `init.<32-char-string>.x.acme-updates.net`. That 32-char string is the agent's
   **custom base32 alphabet** — a permutation of the RFC4648 set `A–Z2–7`. This is
   the whole trick: an off-the-shelf base32 decoder assumes `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`
   and will produce garbage. You must read the alphabet **from the capture**.

3. **Reassemble.** Every data query is `<seq>.<chunk>.x.acme-updates.net`, where
   `seq` is a 3-digit zero-padded index and `chunk` is up to 30 alphabet
   characters. The packets are shuffled on the wire and a few are duplicated
   (retransmissions). Sort by `seq`, de-duplicate, and **concatenate all chunks
   into one string.** The agent base32-encodes the _entire file once_ and only
   then slices it into labels, so decoding any single packet is meaningless —
   flag characters straddle label boundaries.

4. **Decode with the custom alphabet.** Bit packing is ordinary MSB-first 5-bit
   base32, and there is **no `=` padding** (trailing partial group is dropped).
   Map each character to its index in the announced alphabet, glue the 5-bit
   groups, and read off whole bytes.

5. **Read the note.** The decoded bytes are a plaintext "FIELD NOTES" memo. The
   line `recovery_token: NCTF{…}` is the flag.

Run the reference solver:

```
pip install scapy
python3 solve.py ../capture.pcap
```

## The decoy (one, refutable)

There is also an **A-record** beacon to `*.sync.telemetry-cdn.net` whose labels
are _standard_ base32. Decoding it yields
`NCTF{…}`. It is refutable from the brief
alone in under a minute:

- The brief and this writeup state the real channel is **DNS TXT** — the decoy is
  **A** records.
- Its content self-labels as an IDS **signature**, not the token.
- It decodes with the _stock_ alphabet, i.e. "too easily"; the real channel does
  not.

Submitting it is not required and does not cost an attempt in normal CTFd play,
but it is clearly marked wrong.

## Why the off-the-shelf approach fails

- A `base64.b32decode` / CyberChef "From Base32" over any single label fails
  (wrong alphabet, and each label is only a fragment of the stream).
- Even after fixing chunk reassembly, the stock alphabet gives noise — you must
  substitute the permuted alphabet discovered in the `init` packet.
- Sorting matters: the wire order is shuffled and duplicated, so naive
  "concatenate in capture order" produces the wrong stream.

## Honest note on LLM difficulty

An LLM handles the _ideas_ here well: it will recognise DNS-tunnelling, know
base32, and know that a custom alphabet needs a substitution. Where it tends to
stumble without carefully working the evidence:

- **Discovering the alphabet.** The permuted alphabet is not standard and cannot
  be guessed; the model has to actually notice and parse the `init` packet from
  the capture. A model that pattern-matches "base32 → stock decode" gets garbage
  and may hallucinate a flag.
- **Whole-stream vs per-packet.** The natural instinct is to decode each label.
  That never yields the flag; the model must infer that encoding happened over
  the concatenated stream. This is genuine inference from the failing per-packet
  attempt.
- **Ordering + dedup.** Retransmissions and shuffling mean "capture order" is
  wrong; the 3-digit sequence label is the real key.
- **The decoy** produces a plausible, flag-shaped string with the _stock_
  alphabet, which is exactly the answer an under-careful model will grab first.

So it is not one-prompt-solvable end to end from the raw pcap, but a careful,
tool-using agent that reads the `init` packet and reasons about the failing
per-packet decode will solve it. That is the intended medium difficulty.

## Reproducing the capture

`build/generate.py` deterministically rebuilds `capture.pcap` (fixed RNG seed):

```
pip install scapy
cd build && python3 generate.py     # writes ../capture.pcap
```

The custom alphabet, flag, and note text are defined at the top of that script.
Because the alphabet is already embedded in the capture (the `init` packet),
shipping the generator would leak nothing beyond the artifact itself — but it is
kept out of the player bundle (`files:` in challenge.yml lists only
`capture.pcap`).
