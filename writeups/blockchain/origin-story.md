<!-- nctf-meta category="blockchain" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# origin-story

**Summary.** `initialize(address)` has no initializer guard and no access
control, so anyone can set themselves as owner. The vault note is sealed with
the keccak256 of that exact winning calldata.

**Vuln / technique.** Unprotected initializer + `tx.origin` auth. The winning
transaction is `initialize(<your address>)`. Its calldata is the 4-byte
selector of `initialize(address)` followed by the 32-byte left-padded address.

**Steps.**

1. `selector = keccak256("initialize(address)")[:4] = 0xc4d66de8`.
2. `calldata = selector ++ leftpad32(attacker)` where attacker is
   `attacker_you_control` from `vault.json`.
3. `key seed = keccak256(calldata)`; rebuild the keystream and XOR
   `cipher_hex`.

**Flag.** `NCTF{…}`
