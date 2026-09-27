<!-- nctf-meta category="forensics" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# http-body-exfil

**Category:** forensics · **Difficulty:** medium
**Flag:** `NCTF{…}` (static)

## One-line summary

A stolen note is split into base64 fragments POSTed out of order to a fake CDN;
sort the POST bodies by their `X-Seq` header, concatenate, and base64-decode.

## Technique

HTTP request-body exfiltration with reassembly. The victim `10.10.5.23` beacons
to `cdn-metrics.example` (`198.51.100.77`) with repeated
`POST /collect HTTP/1.1`. Each request body is one base64 fragment of a stolen
customer note, and each carries an `X-Seq: <n>` header giving its position. The
POSTs are emitted in random order on the wire, so naive "capture-order"
concatenation fails — you must order by `X-Seq`.

Distractors: benign `GET` traffic to example.com / jsdelivr / github, and a
single unrelated `POST /upload` to `paste.example` carrying `hello`.

## Step by step

1. Isolate the channel. Wireshark:
   `http.request.method == "POST" && http contains "cdn-metrics"`.
2. For each request read the `X-Seq` header and the body.
3. Sort bodies by `X-Seq` (0..N), concatenate into one base64 string.
4. `base64 -d` -> the plaintext note. The `exfil-token:` line is the flag.

## Reproducing / solver

`src/gen.py` writes the pcap with a tiny hand-rolled libpcap writer (no scapy).
The solver is also pure stdlib — it parses the pcap, Ethernet, IPv4 and TCP
headers itself:

```
python3 solve.py ../capture.pcap
```

## Flag

`NCTF{…}`
