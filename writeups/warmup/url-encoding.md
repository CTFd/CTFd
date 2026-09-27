<!-- nctf-meta category="warmup" difficulty="warmup" points="50" author="dagbanjaphet" stub="0" -->

# url-encoding

## TL;DR

Percent-encoding (URL encoding). `%7B` = `{`, `%5F` = `_`, etc.

## Steps

```
python3 -c "import urllib.parse;print(urllib.parse.unquote(open('../encoded.txt').read().strip()))"
```

-> `NCTF{…}`

Or run `python3 solve.py`.

## Flag

`NCTF{…}`
