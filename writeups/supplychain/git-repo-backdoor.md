<!-- nctf-meta category="supplychain" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# git-repo-backdoor

A second commit sneaks a versioned `post-checkout` hook into the repo; the hook
runs a base64 payload that decodes to the flag.

## Vulnerability

The bare repo's history has a benign initial import and a follow-up commit
`chore: add local dev hooks` that introduces `.githooks/post-checkout`. That
hook does `echo <base64> | base64 -d | sh` — arbitrary code that runs on every
checkout. The base64 blob decodes to a shell line exporting the flag.

## Solve

1. Untar the bare repo. Objects live at `objects/xx/yyyy…`, zlib-compressed;
   the header is `"<type> <len>\0"` and the sha1 of that raw buffer is the
   object id.
2. Resolve `HEAD` -> `refs/heads/main` to the tip commit and walk `parent`
   links.
3. Walk the tree to find `.githooks/post-checkout`.
4. Pull the base64 argument out of the hook, decode it, and read the flag.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
