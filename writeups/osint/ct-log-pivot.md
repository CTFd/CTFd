<!-- nctf-meta category="osint" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# ct-log-pivot

**Category:** osint · **Difficulty:** hard
**Flag:** `NCTF{…}`

## Summary

A certificate-transparency log leaks a `cert.tg` subdomain that never appears in
the public DNS zone. That shadow host's TXT record in the resolver cache is
base32 that decodes to the flag.

## Technique

Subdomain enumeration by pivoting on CT-log SANs, cross-referenced against the
published zone to isolate the host that was never meant to be public.

## Step by step

1. Parse `cert.tg.zone` for the set of published hostnames: `cert.tg`, `www`,
   `blog`, `mail`, `ns1`, `ns2`, `vpn`, `portail`.
2. In `ct-log.txt`, collect SANs ending in `cert.tg` from **valid** certificates
   only. Discard: the wildcard `*.cert.tg` (no specific label), the **expired**
   cert for `portail.cert.tg`, and unrelated domains like `togocom.tg`.
3. Subtract the zone hosts from the CT SANs. The only leftover is
   `mgmt-legacy.cert.tg` — the shadow host.
4. In `resolver_cache.txt`, find that host's TXT record: `nctf-b32=<base32>`.
   Base32-decode (standard RFC4648 alphabet). Decoy TXT records (`_dmarc`, `vpn`)
   decode to junk.
5. The decoded string is the flag.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
