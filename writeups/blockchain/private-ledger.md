<!-- nctf-meta category="blockchain" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# private-ledger

**Summary.** The flag sits in a `private` mapping. Solidity `private` only
means "no compiler-generated getter"; the bytes are still in plain storage.

**Vuln / technique.** Fixed-slot + mapping storage layout. For a mapping `m`
declared at slot `p`, the value for key `k` lives at
`keccak256(abi.encode(k, p))`. Nothing about it is hidden on-chain.

**Steps.**

1. Read the layout from `PrivateLedger.sol`: `vaultNotes` is the 5th state
   variable, so its base slot is `4`.
2. You control `0x00000000000000000000000000000000c0FFee01`. Compute the slot
   `keccak256(abi.encode(player, uint256(4)))`.
3. Look that slot up in `storage.json` and ASCII-decode the 32-byte word
   (trim trailing zero padding).

Watch out for the decoy string parked in `vaultNotes[owner]`.

**Flag.** `NCTF{…}`
