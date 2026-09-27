<!-- nctf-meta category="web" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# sqlite-union

**Summary:** The search endpoint concatenates `q` into a SQL string, so a
`UNION SELECT` reads a hidden `secrets` row out of the shipped `shop.db`. The
flag is stored encoded, so the UNION must pull two columns and XOR-decode them.

## Vulnerability

`app.py` builds:

```
SELECT id, name, price FROM products WHERE name LIKE '%<q>%'
```

with `<q>` taken verbatim from the request. Classic union-based SQL injection.
The database ships as `shop.db`, so the same query runs offline.

The flag is **not** stored in the clear (`strings shop.db | grep NCTF` finds
nothing). The hidden `secrets` table holds it as:

- `cipher` -- hex of `flag XOR repeat(xkey)`
- `xkey` -- the repeating XOR key, in a separate column

Neither column alone is the flag; you have to reach the row, combine both
columns, and decode. The `label` column states the scheme:
`xor(fromhex(cipher), repeat(xkey))`.

## Steps

1. Enumerate tables in `shop.db` (there is a `secrets` table alongside
   `products`).
2. Match the three-column shape of the outer query and combine both secret
   columns in one payload:
   `' UNION SELECT id, cipher || '|' || xkey, 0 FROM secrets -- `.
3. Execute the resulting SQL against `shop.db`; split the returned value on
   `|`, then XOR `bytes.fromhex(cipher)` with the repeating `xkey` to recover
   the flag.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
