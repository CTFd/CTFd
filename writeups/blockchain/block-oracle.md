<!-- nctf-meta category="blockchain" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# block-oracle

**Summary.** The lottery's "randomness" is `keccak256(timestamp, number,
prevrandao)`, all of which are public block header fields. The winning ticket
is fully predictable.

**Vuln / technique.** Weak on-chain randomness from block context. Note the
`abi.encodePacked` of three `uint256` values -- that is three 32-byte words
concatenated.

**Steps.**

1. Read `timestamp`, `number`, `prevrandao` from `draw.json`.
2. `winner = uint256(keccak256(pack32(timestamp) ++ pack32(number) ++
pack32(prevrandao)))`.
3. Seal key = `keystream(keccak256)` seeded by `winner` (32-byte big-endian);
   XOR into `cipher_hex`.

**Flag.** `NCTF{…}`
