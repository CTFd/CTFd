<!-- nctf-meta category="osint" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# device-backup-geo

**Category:** osint · **Difficulty:** hard
**Flag:** `NCTF{…}`

## Summary

A phone backup of SQLite databases. An SMS confirms a rendezvous at a precise
UTC time; the GPS fix at that exact timestamp gives coordinates that key the
decryption of an encrypted self-note holding the flag.

## Technique

Cross-database correlation (messages ↔ location history) plus a coordinate-keyed
sha256-CTR decrypt. The photo geotagged in Kara and the "en route" fixes are
decoys.

## Step by step

1. Read the `sms` table in `messages.sqlite`. The message from `+22890114477`
   says `RDV confirme le 2025-07-12 14:32:00 UTC`. Convert to epoch (UTC).
2. In `location.sqlite`, select the `locations` row whose `ts` equals that epoch:
   `lat=6.130419, lon=1.222954` (Grand Marché, Lomé). `celltower.sqlite`
   corroborates the tower change at that time.
3. The `app_config` table in `messages.sqlite` documents the lock scheme:
   the key is the rendezvous GPS point formatted `"{lat:.6f},{lon:.6f}"` and the
   blob is a `sha256(key || counter_be32)` keystream XOR. So build the key string
   `"6.130419,1.222954"`.
4. The `notes` table holds the XOR-encrypted blob. Rebuild the keystream and
   decrypt, then read `token=NCTF{…}`.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
