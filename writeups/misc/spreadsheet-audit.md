<!-- nctf-meta category="misc" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# spreadsheet-audit

A hidden spreadsheet column holds the flag as Unicode code points.

## Technique

`ledger.xlsx` presents five ordinary columns of sales data. Column `F` (`chk`)
is marked hidden and shrunk to width 3, so it does not render in a casual view.
It stores one integer per row; each integer is a Unicode code point of the
flag, in row order. Storing code points rather than literal characters keeps
the flag out of the file as plaintext.

## Steps

1. Open the workbook and un-hide all columns (Format -> Unhide), or read it
   programmatically with `openpyxl`.
2. Read the hidden `chk` column top to bottom.
3. Apply `chr` to each integer and concatenate until you reach `}`.

Run `python3 solution/solve.py` (requires `openpyxl`).

## Flag

`NCTF{…}`
