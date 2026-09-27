<!-- nctf-meta category="crypto" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# glue-and-extend

## TL;DR

The tag is `SHA256(secret || command)`. SHA-256 is a Merkle-Damgard hash, so its
output is its full internal state after the padded message. That lets us
continue the hash over an appended suffix without the secret — a length
extension — and forge the elevated command's tag, which is the sealing key.

## Technique

`token.txt` gives:

- `COMMAND` — `command1`
- `TAG` — `tag1 = SHA256(secret || command1)`
- `SUFFIX` — the admin bytes the gateway appended
- `SEALED` — the flag XORed with a SHA-256 counter-mode keystream keyed by
  `SHA256(secret || command1 || glue || suffix)`

Because the gateway hashed the original message, appended its SHA-256 glue
padding, then hashed the suffix, the elevated tag equals a continuation of
`tag1`. Loading `tag1` as the eight chaining words and processing
`suffix || final_padding` (with the total length set for
`secret || command1 || glue || suffix`) reproduces that digest — no secret
required.

## Attack

1. Parse the four fields from `token.txt`.
2. Brute-force the (small) secret length `L = 1..64`. For each:
   - compute `glue = md_padding(L + len(command1))`;
   - the bytes already hashed number `processed = L + len(command1) + len(glue)`
     (a multiple of 64);
   - continue SHA-256 from `tag1` over `suffix`, with the length field set for
     `processed + len(suffix)`, giving the forged digest;
   - derive `keystream = SHA256(digest || counter)...`, XOR with `SEALED`.
3. The correct guess yields `NCTF{…}`. (Any `L` whose glue lands in the same
   final block gives the same total length and thus the same tag, so the
   smallest matching `L` is enough.)

A self-contained, resumable SHA-256 is implemented in `solve.py` so the chaining
state can be injected.

## Run

```
python3 solve.py            # defaults to ../token.txt
python3 solve.py /path/to/token.txt
```

Output:

```
[+] forged elevated tag (assumed prefix length 1)
[+] FLAG = NCTF{…}
```

## Files

- `../src/gen.py` — deterministic builder (not shipped).
- `../token.txt` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
