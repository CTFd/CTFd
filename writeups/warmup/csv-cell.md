<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# csv-cell

## TL;DR

The flag is one cell of `roster.csv`.

## Steps

```
grep -o 'NCTF{…}' roster.csv   # -> NCTF{…}
```

Or open it in any spreadsheet program and scan the `note` column.
Run `python3 solve.py`.

## Flag

`NCTF{…}`
