<!-- nctf-meta category="blockchain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# proxy-collision

**Summary.** `delegatecall` runs the logic contract's code against the
proxy's storage. `Logic.value` is at slot 0, which is the proxy's
`implementation` slot -- a classic storage collision. The clobbered slot 0
holds the note.

**Vuln / technique.** Delegatecall storage-layout collision. Match the slot
indices of both contracts:

- `Proxy`: slot0 `implementation`, slot1 `admin`, slot2 `paused`.
- `Logic`: slot0 `value`, slot1 `keeper`.

A `setValue` through the proxy writes proxy slot 0.

**Steps.**

1. Determine which proxy slot the logic write lands in: slot 0.
2. Read slot 0 from `proxy_storage.json` and ASCII-decode it (trim zero
   padding). Ignore the decoy string parked in slot 3.

**Flag.** `NCTF{…}`
