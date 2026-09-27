<!-- nctf-meta category="sysadmin" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# mask-slip

## TL;DR

GitHub Actions masks only the _literal_ secret string in logs. The workflow
pipes the secret through `xxd -p` (a hex dump) "for debugging", and that
transformed output is not masked. Find the leaked hex line buried in the long
`run.log`, hex-decode it, and you get the secret, which is the flag.

## The misconfiguration

Secret masking is a substring replacement: the runner scans each log line for
the exact registered secret and swaps it for `***`. It has no idea that `xxd`,
`base64`, `rev`, or a byte-splitting `echo` produce reversible encodings of the
same secret. The `Debug token (hex fingerprint)` step therefore prints the
secret verbatim in hex:

```yaml
- name: Debug token (hex fingerprint)
  run: |
    echo -n "$DEPLOY_TOKEN" | xxd -p | tr -d '\n'; echo
```

The direct-echo step correctly shows `using token: ***`; the hex step leaks.
(This run happens to use a hex dump rather than the classic `base64` mistake —
the root cause is identical: masking is literal, so _any_ encoding defeats it.
A naive `grep TkNURn` for a base64 flag prefix finds nothing here.)

## Attack

1. In `run.log` (a few hundred lines of npm/webpack/jest build noise), find the
   output of the step whose group header mentions `xxd`.
2. Hex-decode that long hex line.
3. The decoded bytes are the secret — here the flag itself.

## Run

```
python3 solve.py
```

Output:

```
[+] leaked hex in log: 4e4354467b63695f7365637265745f...
[+] FLAG = NCTF{…}
```

## Files

- `../.github/workflows/deploy.yml` — the CI pipeline.
- `../run.log` — the captured job log (several hundred lines).
- `../src/gen.py` — deterministic builder.
- `solve.py` — reference solver (stdlib only).
