<!-- nctf-meta category="crypto" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# twister-tell

## TL;DR

MT19937's tempering is invertible, so 624 consecutive outputs untemper into the
full internal state. Clone the generator and reproduce the next words — the
keystream that encrypted the flag.

## Technique

MT19937 keeps 624 words of state. Each output word `y` is produced by tempering:

```
y ^= y >> 11
y ^= (y << 7)  & 0x9D2C5680
y ^= (y << 15) & 0xEFC60000
y ^= y >> 18
```

Every step is a bijection over 32-bit words and can be inverted (the shift-right
and shift-left mixings are undone by iterating the same XOR until it converges).
Untempering 624 consecutive outputs gives the 624 state words. Loading them with
the index set to 624 makes the next `getrandbits(32)` trigger a twist and emit
exactly the same continuation the service used.

## Attack

1. Read the 624 leaked outputs and the hex ciphertext.
2. Untemper each of the 624 outputs to recover a state word.
3. Reload the state into an MT19937 (`setstate((3, state + (624,), None))`).
4. Generate 32-bit words as needed, turn them into keystream bytes (big-endian),
   and XOR with the ciphertext.

## Run

```
python3 solve.py            # defaults to ../outputs.txt and ../flag.enc
python3 solve.py /path/to/outputs.txt /path/to/flag.enc
```

Output:

```
[+] FLAG = NCTF{…}
```

## Files

- `../src/gen.py` — deterministic builder (not shipped).
- `../outputs.txt`, `../flag.enc` — the player handout.
- `solve.py` — this reference solver (Python stdlib only).
