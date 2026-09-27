<!-- nctf-meta category="networking" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# netflow-talker

**Summary:** Aggregate flows by source to find the top talker by bytes, then
decode that host's high destination ports (in time order) into the flag.

## Technique

NetFlow records are per-flow summaries. The intended analysis:

1. **Aggregate** the `octets` counter grouped by `src` and pick the maximum —
   that source is the top talker (an exfil host that dwarfs the background).
2. Its flows all go to one collector on **high destination ports**, one flow per
   character, encoded as `dport = 40000 + ord(char)`.
3. Order that host's flows by `first_ms` and map each port back:
   `chr(dport - 40000)`.

Background hosts also occasionally use ports in the 40000+ range as red herrings,
so you must first isolate the top talker, then decode only its flows.

## Steps

1. Parse `flows.csv`.
2. Sum `octets` per `src`; take the argmax.
3. Filter to that host's flows, sort by `first_ms`.
4. Concatenate `chr(dport - 40000)`.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
