<!-- nctf-meta category="blockchain" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# reentrant-vault

**Challenge id:** `blockchain-reentrant-vault` · **Category:** blockchain (new) · **Difficulty:** hard
**Served:** yes (per-team container, `type: team_instance`)

A smart-contract (EVM) challenge: drain a vault via a classic reentrancy bug.
Each team gets its own anvil chain, contract, and flag.

## Architecture

The container runs a local **anvil** (Foundry) node plus a launcher/oracle
(`src/oracle.py`) that:

- compiles + deploys `contracts/Vault.sol`, seeds it with honest deposits;
- funds a fresh **player** account and exposes its private key;
- serves ONE port: `POST /` proxies JSON-RPC to anvil, `GET /info` returns the
  RPC/keys/vault, `GET /flag` returns the team flag **iff the vault balance is
  0**.

## The bug + exploit

`Vault.withdraw()` sends ETH to the caller **before** zeroing their recorded
balance (checks-effects-interactions violated). An `Attacker` contract
(`solution/Attacker.sol`) re-enters `withdraw()` from its `receive()` hook while
the vault still holds funds, getting paid its deposit repeatedly until the vault
— seeded with other users' deposits — is empty. Draining it to 0 is the win
condition; `GET /flag` then returns the flag.

`solve.py http://HOST:PORT` runs the whole thing: read `/info`, compile + deploy
the Attacker with the funded key (locally-signed EIP-1559 txs over the proxied
RPC), `pwn()`, then `GET /flag`.

## Verification (real EVM, in-process; docker/anvil deferred)

The EVM logic was validated for real against an in-process py-evm chain
(`eth-tester`) with the pinned `solc 0.8.20` — not just reasoned about:

- **Reentrancy** — seed the vault (5 ETH), deposit 1 ETH from the attacker,
  reenter: the vault drains to **0** and the attacker nets ~5 ETH.
- **Oracle** — `setup_chain` deploys+seeds the vault and funds the player;
  `is_solved` returns False before and **True** after the drain.
- **Solver signing path** — `solve.py`'s local-key EIP-1559 signing deploys the
  Attacker and drains the vault to 0 via the funded player key (the exact code
  path the CLI uses).
- **flag.py** — resolves `FLAG` / `CHALLENGE_SECRET` / dev fallback as expected.

Deferred to arena bring-up: the anvil + Foundry image build and an end-to-end
`solve.py http://HOST:PORT` against the running launcher
(`deploy/local/build-images.sh reentrant-vault`). The on-chain behaviour is
identical to the eth-tester validation above (same solc, same bytecode).
