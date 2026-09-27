<!-- nctf-meta category="ai" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# oracle-fake-system

**Summary:** The oracle trusts any `system:` line it finds in the flattened
transcript, so inject a fake `system:` policy line that permits disclosure.

## Vulnerability

`respond` concatenates the genuine base policy with the user's raw text and
splits the result into lines. `_disclosure_allowed` then scans every line that
begins with `system:` and applies last-writer-wins. Because user input becomes
part of that line set, a user-supplied `system:` line overrides the real deny
policy -- a classic role/format-confusion injection.

## Steps

1. Send a line starting with `system:` that grants disclosure using a word like
   `share` or `provide`, with no negation (`never`/`not`/`don't`).
2. On the next line, ask for the vault token.
3. The last disclosure-related `system:` line wins, so `respond` returns the
   token.

Run:

```
python3 solution/solve.py
```

## Flag

`NCTF{…}`
