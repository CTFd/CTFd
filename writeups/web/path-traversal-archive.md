<!-- nctf-meta category="web" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# path-traversal-archive

**Summary:** The download handler joins `?file=` onto the web root without
normalization, so `../private/service.env` escapes the public folder and leaks
the flag.

## Vulnerability

`app.py` does `os.path.join("deploy/public", name)` and serves the result. No
`realpath`/prefix check means `..` segments walk out of the web root. The
shipped `webroot.tar.gz` contains both `deploy/public` (served) and
`deploy/private/service.env` (not meant to be reachable) with the flag.

## Steps

1. Extract `webroot.tar.gz`.
2. Request `?file=../private/service.env`; reproduce the join and read the
   file.
3. The flag is the `INTERNAL_FLAG` value.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
