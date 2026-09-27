<!-- nctf-meta category="blockchain" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# calldata-cache

**Summary.** The captured calldata is a standard ABI-encoded call to
`store(uint256,address,string)`. Decoding the dynamic `string` argument yields
the flag.

**Vuln / technique.** ABI calldata decoding. Layout after the 4-byte selector:

- word0: `id` (uint256)
- word1: `who` (address, left-padded)
- word2: offset (in bytes, from the start of the args) to the `string` tail
- at that offset: 32-byte length, then the UTF-8 bytes (right zero-padded)

**Steps.**

1. Strip the 4-byte selector (`0x00c63b11`).
2. Read word2 as the string offset, read the length there, then read that many
   bytes and UTF-8 decode.

**Flag.** `NCTF{…}`
