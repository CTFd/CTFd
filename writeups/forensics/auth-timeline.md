<!-- nctf-meta category="forensics" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# auth-timeline

**Category:** forensics · **Difficulty:** easy
**Flag:** `NCTF{…}` (static)

## One-line summary

Correlate a brute-force source IP with its successful login's sshd PID, follow
that PID to an `audit` command line, and base64-decode the argument.

## Technique

`auth.log` correlation. The log mixes benign scanning noise, three legitimate
key-based logins (with harmless base64 commands as decoys), and one real
intrusion. The intrusion is only findable by chaining three facts across
different log lines:

1. the source IP with an abnormal number of `Failed password` entries,
2. that IP's single `Accepted password for root` line, which reveals the sshd
   PID, and
3. the `audit[<PID>]` line whose `cmd="echo <base64> | base64 -d ..."` argument
   holds the flag.

## Step by step

1. Tally failures per IP:
   `grep 'Failed password' auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn`.
   `203.0.113.45` stands out with ~28 failures.
2. Find its success and PID:
   `grep '203.0.113.45' auth.log | grep Accepted` -> `sshd[<PID>]`.
3. Pull that session's command:
   `grep 'audit\[<PID>\]' auth.log`.
4. base64-decode the blob in `cmd=`; it yields `flag=NCTF{…}`.

The legitimate sessions' blobs decode to things like `systemctl restart nginx`,
so you must use the PID from the brute-forced login specifically.

## Run the reference solver

```
python3 solve.py ../auth.log
```

## Flag

`NCTF{…}`
