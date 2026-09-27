<!-- nctf-meta category="blockchain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# airdrop-forge

**Summary.** Given the full leaf set of a sorted-pair keccak Merkle tree, you
can construct the inclusion proof for any leaf yourself -- including the
high-value target. The sealed bonus is keyed by that proof.

**Vuln / technique.** Merkle airdrop proof construction. Leaves are
`keccak256(abi.encodePacked(address, uint256 amount))`; internal nodes are
`keccak256(sorted(left, right))`.

**Steps.**

1. Rebuild all leaves from `leaves` (or recompute the target leaf from its
   address/amount and confirm it matches index `3`).
2. Walk the tree bottom-up, collecting the sibling at each level -- that
   ordered list is the proof. Verify it hashes to `root`.
3. Seal key = `keystream(keccak256(concat(proof)))`; XOR into `cipher_hex`.

**Flag.** `NCTF{…}`
