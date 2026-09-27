# Index des writeups — NCTF

**352 challenges** répartis sur **22 catégories**. Chaque challenge servi/statique a son writeup dans son dossier `solution/`.

> Les collines King-of-the-Hill (`challenges/koth/`) sont scorées par le plugin `koth` (Awards) et ne figurent pas dans ce tableau jeopardy ; voir `deploy/koth-ops.md`.

## ai (23)

| challenge                 | pts | type          | writeup                                         | résumé                                                                     |
| ------------------------- | --- | ------------- | ----------------------------------------------- | -------------------------------------------------------------------------- |
| `agent-tool-abuse`        | 500 | team_instance | [writeup](ai/agent-tool-abuse/solution/)        | Halcyon Vault Co. runs a two-agent automation. You chat with RELAY,        |
| `ai0-leaked-transcript`   | 100 | dynamic       | [writeup](ai/ai0-leaked-transcript/solution/)   | HelixDesk is Nimbus Robotics' internal support assistant. Someone          |
| `ai1-naive-guard`         | 300 | team_instance | [writeup](ai/ai1-naive-guard/solution/)         | Level 1 of the AI track. Nimbus Robotics wired up a quick support          |
| `ai2-output-filter`       | 350 | team_instance | [writeup](ai/ai2-output-filter/solution/)       | LEVEL 2 of the AI track. Same guard backend as Level 1 (a naive persona    |
| `ai3-tool-abuse`          | 500 | team_instance | [writeup](ai/ai3-tool-abuse/solution/)          | Level 3 of the AI track -- the heaviest. Meridian Freight runs an internal |
| `copilotsvc-guard`        | 550 | team_instance | [writeup](ai/copilotsvc-guard/solution/)        | This instance's flag is on the service's filesystem, served by no route.   |
| `copilotsvc-inject`       | 500 | team_instance | [writeup](ai/copilotsvc-inject/solution/)       | This instance's flag is on the service's filesystem, served by no route.   |
| `deskbot-guard`           | 550 | team_instance | [writeup](ai/deskbot-guard/solution/)           | This instance's flag is on the service's filesystem, served by no route.   |
| `deskbot-inject`          | 500 | team_instance | [writeup](ai/deskbot-inject/solution/)          | This instance's flag is on the service's filesystem, served by no route.   |
| `mcp-manifest-audit`      | 250 | dynamic       | [writeup](ai/mcp-manifest-audit/solution/)      | CERT.tg is vetting an internal MCP marketplace before wiring an assistant  |
| `oracle-canary-decoy`     | 300 | dynamic       | [writeup](ai/oracle-canary-decoy/solution/)     | ChannelBot ships as oracle.py (respond(prompt)). Ask it for the flag       |
| `oracle-doc-injection`    | 300 | dynamic       | [writeup](ai/oracle-doc-injection/solution/)    | SummarizerBot ships as oracle.py (respond(prompt)). It summarises a        |
| `oracle-encoding-smuggle` | 100 | dynamic       | [writeup](ai/oracle-encoding-smuggle/solution/) | SentinelBot is an offline support assistant shipped as a single Python     |
| `oracle-fake-system`      | 150 | dynamic       | [writeup](ai/oracle-fake-system/solution/)      | PolicyBot guards a vault token and ships as oracle.py with a               |
| `oracle-multi-turn`       | 450 | dynamic       | [writeup](ai/oracle-multi-turn/solution/)       | WardenBot ships as oracle.py with a Session class (and a respond           |
| `oracle-reverse-emit`     | 150 | dynamic       | [writeup](ai/oracle-reverse-emit/solution/)     | RedactBot ships as oracle.py with a respond(prompt) entry point. It        |
| `oracle-tool-args`        | 300 | dynamic       | [writeup](ai/oracle-tool-args/solution/)        | ToolBot ships as oracle.py (respond(prompt)) and exposes a                 |
| `prompt-pivot`            | 500 | team_instance | [writeup](ai/prompt-pivot/solution/)            | This instance's flag is on the service's filesystem, served by no route.   |
| `retriever-guard`         | 550 | team_instance | [writeup](ai/retriever-guard/solution/)         | This instance's flag is on the service's filesystem, served by no route.   |
| `retriever-inject`        | 500 | team_instance | [writeup](ai/retriever-inject/solution/)        | This instance's flag is on the service's filesystem, served by no route.   |
| `tool-ladder`             | 550 | team_instance | [writeup](ai/tool-ladder/solution/)             | This instance's flag is on the service's filesystem, served by no route.   |
| `triage-guard`            | 550 | team_instance | [writeup](ai/triage-guard/solution/)            | This instance's flag is on the service's filesystem, served by no route.   |
| `triage-inject`           | 500 | team_instance | [writeup](ai/triage-inject/solution/)           | This instance's flag is on the service's filesystem, served by no route.   |

## blockchain (27)

| challenge              | pts | type          | writeup                                              | résumé                                                                   |
| ---------------------- | --- | ------------- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| `airdrop-forge`        | 300 | dynamic       | [writeup](blockchain/airdrop-forge/solution/)        | You get a Merkle-root airdrop contract (MerkleAirdrop.sol) and           |
| `allowance-drift`      | 150 | dynamic       | [writeup](blockchain/allowance-drift/solution/)      | You get a hand-rolled ERC20 (DriftToken.sol) and tokenstate.json         |
| `block-oracle`         | 150 | dynamic       | [writeup](blockchain/block-oracle/solution/)         | A lottery seals its pot for whoever guesses the winning ticket. You      |
| `bridgepool-allowance` | 500 | team_instance | [writeup](blockchain/bridgepool-allowance/solution/) | This instance's flag is on the service's filesystem, served by no route. |
| `bridgepool-proxy`     | 500 | team_instance | [writeup](blockchain/bridgepool-proxy/solution/)     | This instance's flag is on the service's filesystem, served by no route. |
| `bridgepool-reentry`   | 550 | team_instance | [writeup](blockchain/bridgepool-reentry/solution/)   | This instance's flag is on the service's filesystem, served by no route. |
| `calldata-cache`       | 100 | dynamic       | [writeup](blockchain/calldata-cache/solution/)       | You captured one transaction's raw calldata (calldata.txt) and the       |
| `escrowd-allowance`    | 500 | team_instance | [writeup](blockchain/escrowd-allowance/solution/)    | This instance's flag is on the service's filesystem, served by no route. |
| `escrowd-proxy`        | 500 | team_instance | [writeup](blockchain/escrowd-proxy/solution/)        | This instance's flag is on the service's filesystem, served by no route. |
| `escrowd-reentry`      | 550 | team_instance | [writeup](blockchain/escrowd-reentry/solution/)      | This instance's flag is on the service's filesystem, served by no route. |
| `lender-allowance`     | 500 | team_instance | [writeup](blockchain/lender-allowance/solution/)     | This instance's flag is on the service's filesystem, served by no route. |
| `lender-proxy`         | 500 | team_instance | [writeup](blockchain/lender-proxy/solution/)         | This instance's flag is on the service's filesystem, served by no route. |
| `lender-reentry`       | 550 | team_instance | [writeup](blockchain/lender-reentry/solution/)       | This instance's flag is on the service's filesystem, served by no route. |
| `oraclefeed-allowance` | 500 | team_instance | [writeup](blockchain/oraclefeed-allowance/solution/) | This instance's flag is on the service's filesystem, served by no route. |
| `oraclefeed-proxy`     | 500 | team_instance | [writeup](blockchain/oraclefeed-proxy/solution/)     | This instance's flag is on the service's filesystem, served by no route. |
| `oraclefeed-reentry`   | 550 | team_instance | [writeup](blockchain/oraclefeed-reentry/solution/)   | This instance's flag is on the service's filesystem, served by no route. |
| `origin-story`         | 300 | dynamic       | [writeup](blockchain/origin-story/solution/)         | You get Vault.sol and vault.json (a sealed note cipherhex plus           |
| `overflow-mint`        | 300 | dynamic       | [writeup](blockchain/overflow-mint/solution/)        | You get the Solidity source of a token pre-sale (MintSale.sol) and       |
| `private-ledger`       | 150 | dynamic       | [writeup](blockchain/private-ledger/solution/)       | You are handed the Solidity source of an on-chain ledger and a raw       |
| `proxy-climb`          | 500 | team_instance | [writeup](blockchain/proxy-climb/solution/)          | This instance's flag is on the service's filesystem, served by no route. |
| `proxy-collision`      | 300 | dynamic       | [writeup](blockchain/proxy-collision/solution/)      | You get an upgradeable Proxy.sol, its Logic.sol implementation, and      |
| `reentrant-vault`      | 450 | team_instance | [writeup](blockchain/reentrant-vault/solution/)      | Reentrant Vault. (nouvelle catégorie : blockchain / EVM)                 |
| `reentry-chain`        | 550 | team_instance | [writeup](blockchain/reentry-chain/solution/)        | This instance's flag is on the service's filesystem, served by no route. |
| `replay-signer`        | 450 | dynamic       | [writeup](blockchain/replay-signer/solution/)        | You captured two withdrawal requests signed by the same treasury key     |
| `vaultdao-allowance`   | 500 | team_instance | [writeup](blockchain/vaultdao-allowance/solution/)   | This instance's flag is on the service's filesystem, served by no route. |
| `vaultdao-proxy`       | 500 | team_instance | [writeup](blockchain/vaultdao-proxy/solution/)       | This instance's flag is on the service's filesystem, served by no route. |
| `vaultdao-reentry`     | 550 | team_instance | [writeup](blockchain/vaultdao-reentry/solution/)     | This instance's flag is on the service's filesystem, served by no route. |

## chains (6)

| challenge    | pts | type          | writeup                                | résumé                                                                   |
| ------------ | --- | ------------- | -------------------------------------- | ------------------------------------------------------------------------ |
| `citadel`    | 600 | team_instance | [writeup](chains/citadel/solution/)    | This instance's flag is on the service's filesystem, served by no route. |
| `clinic`     | 450 | team_instance | [writeup](chains/clinic/solution/)     | This instance's flag is on the service's filesystem, served by no route. |
| `pipeline`   | 550 | team_instance | [writeup](chains/pipeline/solution/)   | This instance's flag is on the service's filesystem, served by no route. |
| `relay`      | 500 | team_instance | [writeup](chains/relay/solution/)      | This instance's flag is on the service's filesystem, served by no route. |
| `tokenforge` | 500 | team_instance | [writeup](chains/tokenforge/solution/) | This instance's flag is on the service's filesystem, served by no route. |
| `vaultboard` | 500 | team_instance | [writeup](chains/vaultboard/solution/) | This instance's flag is on the service's filesystem, served by no route. |

## cloud (14)

| challenge           | pts | type          | writeup                                      | résumé                                                                      |
| ------------------- | --- | ------------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| `artifacts-envexec` | 300 | team_instance | [writeup](cloud/artifacts-envexec/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `artifacts-imds`    | 300 | team_instance | [writeup](cloud/artifacts-imds/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `artifacts-oidc`    | 300 | team_instance | [writeup](cloud/artifacts-oidc/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `artifacts-prefix`  | 300 | team_instance | [writeup](cloud/artifacts-prefix/solution/)  | This instance's flag is on the service's filesystem, served by no route.    |
| `artifacts-presign` | 300 | team_instance | [writeup](cloud/artifacts-presign/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `breach-chain`      | 450 | team_instance | [writeup](cloud/breach-chain/solution/)      | Kékéli Cloud. Le service de prévisualisation média de Kékéli Cloud tourne   |
| `gcp-token-scope`   | 300 | dynamic       | [writeup](cloud/gcp-token-scope/solution/)   | A leaked GCP service-account key (sa-key.json) for a CI helper, the projec… |
| `imds-ssrf`         | 150 | dynamic       | [writeup](cloud/imds-ssrf/solution/)         | A proxy capture of an SSRF exploit against an EC2-hosted preview service    |
| `leaky-prefix`      | 100 | dynamic       | [writeup](cloud/leaky-prefix/solution/)      | A snapshot of the kekeli-media-prod S3 bucket: its live bucket policy       |
| `passrole-ladder`   | 450 | dynamic       | [writeup](cloud/passrole-ladder/solution/)   | An IAM dump from an AWS account: users (iam-users.json), roles              |
| `queue-poison`      | 500 | team_instance | [writeup](cloud/queue-poison/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `sas-forge`         | 450 | dynamic       | [writeup](cloud/sas-forge/solution/)         | An Azure Storage account key leaked into a backup (leaked-account-key.txt)… |
| `sub-wildcard`      | 150 | dynamic       | [writeup](cloud/sub-wildcard/solution/)      | The ci-deployer IAM role trusts GitHub Actions via OIDC. You have its trus… |
| `trail-of-keys`     | 300 | dynamic       | [writeup](cloud/trail-of-keys/solution/)     | A CloudTrail export (cloudtrail.json) from one busy hour on the             |

## crypto (19)

| challenge             | pts | type          | writeup                                         | résumé                                                                      |
| --------------------- | --- | ------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| `affine-relay`        | 100 | dynamic       | [writeup](crypto/affine-relay/solution/)        | We intercepted a single scrambled memo, cipher.txt. The courier ran every   |
| `commit-bias`         | 300 | dynamic       | [writeup](crypto/commit-bias/solution/)         | The CoinVault table runs a "provably fair" coin-flip game. Every round the  |
| `ecb-echo`            | 300 | dynamic       | [writeup](crypto/ecb-echo/solution/)            | We tapped a device that encrypts data for us on request and logged everyth… |
| `fermat-twins`        | 150 | dynamic       | [writeup](crypto/fermat-twins/solution/)        | A 1024-bit RSA public key pubkey.pem and a hex ciphertext ciphertext.txt.   |
| `glue-and-extend`     | 450 | dynamic       | [writeup](crypto/glue-and-extend/solution/)     | A gateway seals payloads under a key derived from a shared secret and the   |
| `keystream-reuse`     | 300 | dynamic       | [writeup](crypto/keystream-reuse/solution/)     | messages.txt holds 25 intercepted ciphertexts, one hex string per line. Th… |
| `lcg-casino`          | 500 | team_instance | [writeup](crypto/lcg-casino/solution/)          | A "provably fair" casino deals from a home-grown verifiable shuffle. It     |
| `modulus-siblings`    | 300 | dynamic       | [writeup](crypto/modulus-siblings/solution/)    | Two departments encrypted the very same memo for the same recipient, and w… |
| `nonce-sense`         | 150 | dynamic       | [writeup](crypto/nonce-sense/solution/)         | A hardware signing device produced a batch of ECDSA signatures over         |
| `notarysvc-ecb`       | 450 | team_instance | [writeup](crypto/notarysvc-ecb/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `notarysvc-kdf`       | 250 | team_instance | [writeup](crypto/notarysvc-kdf/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `notarysvc-nonce`     | 450 | team_instance | [writeup](crypto/notarysvc-nonce/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `notarysvc-padoracle` | 500 | team_instance | [writeup](crypto/notarysvc-padoracle/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `notarysvc-signext`   | 500 | team_instance | [writeup](crypto/notarysvc-signext/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `padding-oracle-lite` | 350 | team_instance | [writeup](crypto/padding-oracle-lite/solution/) | A decommissioned session service still answers on its own home-grown binar… |
| `sign-slip`           | 450 | team_instance | [writeup](crypto/sign-slip/solution/)           | This instance's flag is on the service's filesystem, served by no route.    |
| `tlv-vault`           | 350 | dynamic       | [writeup](crypto/tlv-vault/solution/)           | We recovered eight .vlt archives from a decommissioned "vault" service,     |
| `twister-tell`        | 300 | dynamic       | [writeup](crypto/twister-tell/solution/)        | A token service leaked a run of its random number generator's raw 32-bit    |
| `vigenere-drift`      | 150 | dynamic       | [writeup](crypto/vigenere-drift/solution/)      | cipher.txt is an intercepted English memorandum enciphered with a repeatin… |

## cve (1)

| challenge   | pts | type          | writeup                            | résumé                                                                   |
| ----------- | --- | ------------- | ---------------------------------- | ------------------------------------------------------------------------ |
| `hookrelay` | 350 | team_instance | [writeup](cve/hookrelay/solution/) | Hookrelay is the CI platform team's internal mirror healthcheck. Paste a |

## forensics (13)

| challenge          | pts | type    | writeup                                         | résumé                                                                      |
| ------------------ | --- | ------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| `Audio FSK`        | 500 | dynamic | [writeup](forensics/audio-fsk/solution/)        | Nous avons intercepté une courte liaison descendante RF et enregistré la b… |
| `auth-timeline`    | 150 | dynamic | [writeup](forensics/auth-timeline/solution/)    | A public-facing server was compromised overnight. All we salvaged before t… |
| `DNS Exfil`        | 300 | dynamic | [writeup](forensics/dns-exfil/solution/)        | Notre EDR a signalé un « agent de synchronisation » sur le poste d'un       |
| `Evasion Timeline` | 400 | dynamic | [writeup](forensics/evasion-timeline/solution/) | L'EDR d'un poste de la finance est resté silencieux pendant une tempête     |
| `gzip-tar-nest`    | 150 | dynamic | [writeup](forensics/gzip-tar-nest/solution/)    | A "parcel" (parcel.tar.gz) was intercepted leaving the network. It looks    |
| `http-body-exfil`  | 300 | dynamic | [writeup](forensics/http-body-exfil/solution/)  | A workstation kept "phoning home" to a metrics endpoint that our asset      |
| `icmp-beacon`      | 150 | dynamic | [writeup](forensics/icmp-beacon/solution/)      | During an incident, an analyst noticed a host on the network that "just wo… |
| `mem-struct`       | 300 | dynamic | [writeup](forensics/mem-struct/solution/)       | We captured a raw memory dump (memdump.bin) from a process that was holdin… |
| `png-magic-fix`    | 100 | dynamic | [writeup](forensics/png-magic-fix/solution/)    | A screenshot was pulled from a suspect's machine, but the file (evidence.p… |
| `sqlite-wal`       | 300 | dynamic | [writeup](forensics/sqlite-wal/solution/)       | We seized an application's SQLite database (app.db) plus its sidecar file   |
| `SRAM Retention`   | 350 | dynamic | [writeup](forensics/sram-retention/solution/)   | Nous avons extrait un vidage mémoire d'un microcontrôleur Aetheris AE-32    |
| `USB Keystrokes`   | 150 | dynamic | [writeup](forensics/usb-keystrokes/solution/)   | Nous avons mis sur écoute le bus USB pendant qu'un collègue se connectait … |
| `zip-carve`        | 150 | dynamic | [writeup](forensics/zip-carve/solution/)        | We recovered a ZIP archive (archive.zip) from a departing employee's USB    |

## hardware (8)

| challenge        | pts | type    | writeup                                      | résumé                                                                      |
| ---------------- | --- | ------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| `boot-rom`       | 450 | dynamic | [writeup](hardware/boot-rom/solution/)       | rom.bin is the boot ROM of a tiny custom 8-bit processor. ISA.md documents  |
| `firmware-blob`  | 150 | dynamic | [writeup](hardware/firmware-blob/solution/)  | We pulled firmware.bin off a device's flash chip. It starts with a small    |
| `i2c-sniff`      | 300 | dynamic | [writeup](hardware/i2c-sniff/solution/)      | We clipped a two-wire probe onto an I2C bus and captured SCL and SDA while  |
| `intel-hex`      | 100 | dynamic | [writeup](hardware/intel-hex/solution/)      | image.hex is a dump of a microcontroller's memory in a common text hex      |
| `manchester-ook` | 300 | dynamic | [writeup](hardware/manchester-ook/solution/) | We recorded the demodulated envelope of a short 433 MHz on-off-keyed burst… |
| `spi-eeprom`     | 150 | dynamic | [writeup](hardware/spi-eeprom/solution/)     | A logic analyzer captured the four SPI lines (CS, CLK, MOSI, MISO)          |
| `uart-capture`   | 100 | dynamic | [writeup](hardware/uart-capture/solution/)   | We tapped a serial line with a logic analyzer and dumped the samples to     |
| `vcd-fsm`        | 300 | dynamic | [writeup](hardware/vcd-fsm/solution/)        | trace.vcd is a Value Change Dump exported from a simulation of a small sta… |

## misc (16)

| challenge            | pts | type          | writeup                                      | résumé                                                                      |
| -------------------- | --- | ------------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| `brainfuck-cascade`  | 300 | dynamic       | [writeup](misc/brainfuck-cascade/solution/)  | All we recovered is one line of dense ASCII (cipher.txt). It decodes to     |
| `bridged-deser`      | 500 | team_instance | [writeup](misc/bridged-deser/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `bridged-envreuse`   | 450 | team_instance | [writeup](misc/bridged-envreuse/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `bridged-protoparse` | 450 | team_instance | [writeup](misc/bridged-protoparse/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `chunk-hunt`         | 150 | dynamic       | [writeup](misc/chunk-hunt/solution/)         | Someone exported a company badge as a PNG (badge.png). The picture itself … |
| `dfa-oracle`         | 300 | dynamic       | [writeup](misc/dfa-oracle/solution/)         | automaton.json describes a deterministic finite automaton: an alphabet, a   |
| `esolang-jail`       | 400 | team_instance | [writeup](misc/esolang-jail/solution/)       | Marble jail -- a tiny stack esoteric language, served over TCP as an        |
| `gf2-cipher`         | 450 | dynamic       | [writeup](misc/gf2-cipher/solution/)         | system.json gives you a square binary matrix A and a bit vector b. There    |
| `git-archaeology`    | 100 | dynamic       | [writeup](misc/git-archaeology/solution/)    | Our intern force-pushed away a mistake. "It's gone," they said.             |
| `Heartbeat`          | 300 | dynamic       | [writeup](misc/timing-channel/solution/)     | A status agent on an isolated segment "phones home" to a collector with a   |
| `json-sift`          | 100 | dynamic       | [writeup](misc/json-sift/solution/)          | We dumped 5000 telemetry events into a single JSON array (telemetry.json).  |
| `pbkdf2-crack`       | 150 | dynamic       | [writeup](misc/pbkdf2-crack/solution/)       | We pulled one account's password record out of a leaked database            |
| `polyglot-onion`     | 250 | dynamic       | [writeup](misc/polyglot-onion/solution/)     | A courier dropped off a single file and nothing else. It opens as an        |
| `proto-fuzz`         | 350 | team_instance | [writeup](misc/proto-fuzz/solution/)         | proto-fuzz -- a tiny home-grown line protocol, FZLP/1, served over          |
| `spreadsheet-audit`  | 150 | dynamic       | [writeup](misc/spreadsheet-audit/solution/)  | A finance intern swears the quarterly ledger (ledger.xlsx) is "just sales   |
| `wire-tap`           | 300 | dynamic       | [writeup](misc/wire-tap/solution/)           | We captured a single serialized message off the wire (message.bin) but the  |

## ml (21)

| challenge           | pts | type          | writeup                                   | résumé                                                                      |
| ------------------- | --- | ------------- | ----------------------------------------- | --------------------------------------------------------------------------- |
| `adv-flip`          | 450 | dynamic       | [writeup](ml/adv-flip/solution/)          | gate.npz ships a linear gate: weights w, bias b, and one base input         |
| `adversarial-gate`  | 500 | team_instance | [writeup](ml/adversarial-gate/solution/)  | SENTRY-6 badge gate. An access gate runs a small convolutional              |
| `embedding-nn`      | 150 | dynamic       | [writeup](ml/embedding-nn/solution/)      | embedtable.npz holds a token embedding table and a batch of query vectors.  |
| `feature-inject`    | 450 | team_instance | [writeup](ml/feature-inject/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `featurizer-pickle` | 500 | team_instance | [writeup](ml/featurizer-pickle/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `featurizer-poison` | 450 | team_instance | [writeup](ml/featurizer-poison/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `grad-leak`         | 300 | dynamic       | [writeup](ml/grad-leak/solution/)         | During distributed training a worker leaked the gradients from a single st… |
| `member-ids`        | 150 | dynamic       | [writeup](ml/member-ids/solution/)        | shadoweval.npz is an evaluation table for a model: for each record it list… |
| `model-inversion`   | 500 | team_instance | [writeup](ml/model-inversion/solution/)   | AEGIS-VAULT recall service. The vault has memorised one sealed record --    |
| `model-swap`        | 500 | team_instance | [writeup](ml/model-swap/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `modelhub-pickle`   | 500 | team_instance | [writeup](ml/modelhub-pickle/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `modelhub-poison`   | 450 | team_instance | [writeup](ml/modelhub-poison/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `pickle-rce`        | 350 | team_instance | [writeup](ml/pickle-rce/solution/)        | ModelHub is a model registry. Teams upload a serialized model and the       |
| `poison-shift`      | 300 | dynamic       | [writeup](ml/poison-shift/solution/)      | poisonedtrain.npz is a regression training set: features X, targets y,      |
| `scorer-pickle`     | 500 | team_instance | [writeup](ml/scorer-pickle/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `scorer-poison`     | 450 | team_instance | [writeup](ml/scorer-poison/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `surrogate-fit`     | 300 | dynamic       | [writeup](ml/surrogate-fit/solution/)     | A hidden model is a black box: you feed it a vector, it returns a number.   |
| `trainer-pickle`    | 500 | team_instance | [writeup](ml/trainer-pickle/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `trainer-poison`    | 450 | team_instance | [writeup](ml/trainer-poison/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `tree-path`         | 100 | dynamic       | [writeup](ml/tree-path/solution/)         | We recovered a trained binary decision tree from a classifier and dumped i… |
| `trojan-trigger`    | 450 | dynamic       | [writeup](ml/trojan-trigger/solution/)    | detector.npz ships a hidden "detector" unit that scores an input with       |

## mobile (8)

| challenge            | pts | type    | writeup                                        | résumé                                                                      |
| -------------------- | --- | ------- | ---------------------------------------------- | --------------------------------------------------------------------------- |
| `deeplink-guard`     | 300 | dynamic | [writeup](mobile/deeplink-guard/solution/)     | VaultApp.ipa registers a custom URL scheme and unlocks a "grant" screen on… |
| `keystore-alias`     | 450 | dynamic | [writeup](mobile/keystore-alias/solution/)     | entvault.apk ships a custom keystore blob (assets/vault.keystore) holding   |
| `native-xor`         | 150 | dynamic | [writeup](mobile/native-xor/solution/)         | nativegame.apk validates its flag in a bundled native library. We recovere… |
| `obfuscated-strings` | 150 | dynamic | [writeup](mobile/obfuscated-strings/solution/) | app.apk from the StashBox app builds a license string at runtime instead o… |
| `prefs-vault`        | 300 | dynamic | [writeup](mobile/prefs-vault/solution/)        | A backup of the QuickNotes app includes its SharedPreferences and the       |
| `root-gate`          | 150 | dynamic | [writeup](mobile/root-gate/solution/)          | securebank.apk refuses to show its unlock code on rooted devices. We do no… |
| `strings-goldmine`   | 100 | dynamic | [writeup](mobile/strings-goldmine/solution/)   | We pulled app-release.apk off a payments handset. Unzip it like any APK an… |
| `webview-bridge`     | 300 | dynamic | [writeup](mobile/webview-bridge/solution/)     | hybridshop.apk is a hybrid app: a WebView front-end talks to a native       |

## networking (9)

| challenge         | pts | type    | writeup                                         | résumé                                                                      |
| ----------------- | --- | ------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| `acl-firewall`    | 150 | dynamic | [writeup](networking/acl-firewall/solution/)    | You are handed a firewall's access-control list and a batch of candidate    |
| `bgp-bestpath`    | 150 | dynamic | [writeup](networking/bgp-bestpath/solution/)    | A router's incoming BGP table (bgprib.json) lists several candidate routes  |
| `dns-chain`       | 300 | dynamic | [writeup](networking/dns-chain/solution/)       | A single DNS response was captured as raw bytes (message.bin, with          |
| `eui64-slaac`     | 100 | dynamic | [writeup](networking/eui64-slaac/solution/)     | A stateless address-autoconfig (SLAAC) inventory (hosts.json) lists 29      |
| `framed-protocol` | 300 | dynamic | [writeup](networking/framed-protocol/solution/) | We captured the raw byte stream of an in-house application protocol         |
| `netflow-talker`  | 300 | dynamic | [writeup](networking/netflow-talker/solution/)  | A NetFlow collector exported a batch of flow records (flows.csv): one row … |
| `subnet-reach`    | 300 | dynamic | [writeup](networking/subnet-reach/solution/)    | You have a router's forwarding table and a batch of probe packets           |
| `tcp-reassembly`  | 450 | dynamic | [writeup](networking/tcp-reassembly/solution/)  | We logged one direction of a TCP conversation as a list of segments         |
| `tls-sni`         | 300 | dynamic | [writeup](networking/tls-sni/solution/)         | A single TLS ClientHello was captured as raw bytes (clienthello.bin, with   |

## os (5)

| challenge       | pts | type          | writeup                               | résumé                                                                   |
| --------------- | --- | ------------- | ------------------------------------- | ------------------------------------------------------------------------ |
| `nyx-allocator` | 550 | team_instance | [writeup](os/nyx-allocator/solution/) | This instance's flag is on the service's filesystem, served by no route. |
| `nyx-bootstrap` | 400 | team_instance | [writeup](os/nyx-bootstrap/solution/) | This instance's flag is on the service's filesystem, served by no route. |
| `nyx-scheduler` | 550 | team_instance | [writeup](os/nyx-scheduler/solution/) | This instance's flag is on the service's filesystem, served by no route. |
| `nyx-syscall`   | 500 | team_instance | [writeup](os/nyx-syscall/solution/)   | This instance's flag is on the service's filesystem, served by no route. |
| `nyx-vfs`       | 500 | team_instance | [writeup](os/nyx-vfs/solution/)       | This instance's flag is on the service's filesystem, served by no route. |

## osint (8)

| challenge            | pts | type    | writeup                                       | résumé                                                                      |
| -------------------- | --- | ------- | --------------------------------------------- | --------------------------------------------------------------------------- |
| `cred-reuse`         | 300 | dynamic | [writeup](osint/cred-reuse/solution/)         | Un forum communautaire togolais a été piraté et sa base de comptes          |
| `ct-log-pivot`       | 150 | dynamic | [writeup](osint/ct-log-pivot/solution/)       | Reconnaissance sur le domaine cert.tg. On vous remet la zone DNS publique   |
| `device-backup-geo`  | 450 | dynamic | [writeup](osint/device-backup-geo/solution/)  | Saisie d'un téléphone : la sauvegarde exportée contient plusieurs bases     |
| `doc-metadata`       | 150 | dynamic | [writeup](osint/doc-metadata/solution/)       | Six communiqués « officiels » (.docx) ont fuité. Ils sont tous signés       |
| `entity-graph`       | 150 | dynamic | [writeup](osint/entity-graph/solution/)       | Le CERT.tg a exporté son graphe d'enquête sur la fuite de données de la     |
| `exif-triangulation` | 300 | dynamic | [writeup](osint/exif-triangulation/solution/) | Quatre guetteurs ont photographié la même cible depuis des points différen… |
| `social-export`      | 150 | dynamic | [writeup](osint/social-export/solution/)      | Deux exports de comptes ont été saisis chez un suspect : un export Telegra… |
| `wayback-diff`       | 300 | dynamic | [writeup](osint/wayback-diff/solution/)       | Voici cinq captures archivées de la page d'accueil d'un portail, prises à … |

## ppc (9)

| challenge          | pts | type    | writeup                                   | résumé                                                                     |
| ------------------ | --- | ------- | ----------------------------------------- | -------------------------------------------------------------------------- |
| `congruence-vault` | 450 | dynamic | [writeup](ppc/congruence-vault/solution/) | system.txt starts with a CIPHER blob, then lists 160 lines of three        |
| `dijkstra-relay`   | 300 | dynamic | [writeup](ppc/dijkstra-relay/solution/)   | graph.txt describes a directed weighted graph: a header with node/edge     |
| `hull-cipher`      | 150 | dynamic | [writeup](ppc/hull-cipher/solution/)      | points.txt lists a few hundred 2-D points, each tagged with a single       |
| `knapsack-locker`  | 300 | dynamic | [writeup](ppc/knapsack-locker/solution/)  | items.txt gives a capacity, a list of items (each with a weight and a      |
| `life-decode`      | 450 | dynamic | [writeup](ppc/life-decode/solution/)      | grid.txt gives a board size and a step count, a CIPHER blob, and an        |
| `semiprime-sweep`  | 300 | dynamic | [writeup](ppc/semiprime-sweep/solution/)  | semiprimes.txt starts with a CIPHER blob and then lists several dozen      |
| `stack-machine`    | 300 | dynamic | [writeup](ppc/stack-machine/solution/)    | program.txt is source code for a tiny made-up machine: one instruction per |
| `sudoku-vault`     | 450 | dynamic | [writeup](ppc/sudoku-vault/solution/)     | puzzle.txt holds a CIPHER blob and a 9x9 Sudoku grid (0 marks an empty     |
| `z-locator`        | 150 | dynamic | [writeup](ppc/z-locator/solution/)        | data.txt has a short pattern on line 1 and a large blob of text on line 2. |

## pwn (63)

| challenge            | pts | type          | writeup                                     | résumé                                                                      |
| -------------------- | --- | ------------- | ------------------------------------------- | --------------------------------------------------------------------------- |
| `authd-canary`       | 500 | team_instance | [writeup](pwn/authd-canary/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `authd-fmt`          | 500 | team_instance | [writeup](pwn/authd-fmt/solution/)          | This instance's flag is on the service's filesystem, served by no route.    |
| `authd-heap`         | 550 | team_instance | [writeup](pwn/authd-heap/solution/)         | This instance's flag is on the service's filesystem, served by no route.    |
| `authd-sandbox`      | 600 | team_instance | [writeup](pwn/authd-sandbox/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `authd-uaf`          | 550 | team_instance | [writeup](pwn/authd-uaf/solution/)          | This instance's flag is on the service's filesystem, served by no route.    |
| `boot2root-c2`       | 500 | team_instance | [writeup](pwn/boot2root-c2/solution/)       | boot2root-c2 -- Phantom Wire staging server. During the HIVE CONSULT        |
| `boot2root-linux`    | 500 | team_instance | [writeup](pwn/boot2root-linux/solution/)    | boot2root-linux -- a full Linux box in a single per-team container. Get a   |
| `boot2root-ssh`      | 400 | team_instance | [writeup](pwn/boot2root-ssh/solution/)      | boot2root-ssh. Une box Linux complète, un conteneur par équipe. On te       |
| `boot2root-webapp`   | 500 | team_instance | [writeup](pwn/boot2root-webapp/solution/)   | boot2root-webapp -- SnapNote, a full Linux box in a single per-team         |
| `brokerd-canary`     | 500 | team_instance | [writeup](pwn/brokerd-canary/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `brokerd-fmt`        | 500 | team_instance | [writeup](pwn/brokerd-fmt/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `brokerd-heap`       | 550 | team_instance | [writeup](pwn/brokerd-heap/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `brokerd-sandbox`    | 600 | team_instance | [writeup](pwn/brokerd-sandbox/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `brokerd-uaf`        | 550 | team_instance | [writeup](pwn/brokerd-uaf/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `bss-admin-flip`     | 150 | dynamic       | [writeup](pwn/bss-admin-flip/solution/)     | You are given a single x86-64 Linux binary, chall. It asks you to register… |
| `cachesrv-canary`    | 500 | team_instance | [writeup](pwn/cachesrv-canary/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `cachesrv-fmt`       | 500 | team_instance | [writeup](pwn/cachesrv-fmt/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `cachesrv-heap`      | 550 | team_instance | [writeup](pwn/cachesrv-heap/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `cachesrv-sandbox`   | 600 | team_instance | [writeup](pwn/cachesrv-sandbox/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `cachesrv-uaf`       | 550 | team_instance | [writeup](pwn/cachesrv-uaf/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `fmt-key-leak`       | 300 | dynamic       | [writeup](pwn/fmt-key-leak/solution/)       | You are given a single x86-64 Linux binary, chall. It echoes a line you ty… |
| `format-pivot`       | 500 | team_instance | [writeup](pwn/format-pivot/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `format-string-101`  | 150 | team_instance | [writeup](pwn/format-string-101/solution/)  | format-string-101 -- a small networked service, served as                   |
| `heap-note`          | 350 | team_instance | [writeup](pwn/heap-note/solution/)          | A tiny note-taking service on a pinned glibc 2.31 (Ubuntu 20.04,            |
| `heap-relay`         | 550 | team_instance | [writeup](pwn/heap-relay/solution/)         | This instance's flag is on the service's filesystem, served by no route.    |
| `keyvault-canary`    | 500 | team_instance | [writeup](pwn/keyvault-canary/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `keyvault-fmt`       | 500 | team_instance | [writeup](pwn/keyvault-fmt/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `keyvault-heap`      | 550 | team_instance | [writeup](pwn/keyvault-heap/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `keyvault-sandbox`   | 600 | team_instance | [writeup](pwn/keyvault-sandbox/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `keyvault-uaf`       | 550 | team_instance | [writeup](pwn/keyvault-uaf/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `logd-canary`        | 500 | team_instance | [writeup](pwn/logd-canary/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `logd-fmt`           | 500 | team_instance | [writeup](pwn/logd-fmt/solution/)           | This instance's flag is on the service's filesystem, served by no route.    |
| `logd-heap`          | 550 | team_instance | [writeup](pwn/logd-heap/solution/)          | This instance's flag is on the service's filesystem, served by no route.    |
| `logd-sandbox`       | 600 | team_instance | [writeup](pwn/logd-sandbox/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `logd-uaf`           | 550 | team_instance | [writeup](pwn/logd-uaf/solution/)           | This instance's flag is on the service's filesystem, served by no route.    |
| `meshd-canary`       | 500 | team_instance | [writeup](pwn/meshd-canary/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `meshd-fmt`          | 500 | team_instance | [writeup](pwn/meshd-fmt/solution/)          | This instance's flag is on the service's filesystem, served by no route.    |
| `meshd-heap`         | 550 | team_instance | [writeup](pwn/meshd-heap/solution/)         | This instance's flag is on the service's filesystem, served by no route.    |
| `meshd-sandbox`      | 600 | team_instance | [writeup](pwn/meshd-sandbox/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `meshd-uaf`          | 550 | team_instance | [writeup](pwn/meshd-uaf/solution/)          | This instance's flag is on the service's filesystem, served by no route.    |
| `off-by-one-auth`    | 150 | dynamic       | [writeup](pwn/off-by-one-auth/solution/)    | You are given a single x86-64 Linux binary, chall. It asks how many bytes   |
| `parserd-canary`     | 500 | team_instance | [writeup](pwn/parserd-canary/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `parserd-fmt`        | 500 | team_instance | [writeup](pwn/parserd-fmt/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `parserd-heap`       | 550 | team_instance | [writeup](pwn/parserd-heap/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `parserd-sandbox`    | 600 | team_instance | [writeup](pwn/parserd-sandbox/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `parserd-uaf`        | 550 | team_instance | [writeup](pwn/parserd-uaf/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `relaybox-canary`    | 500 | team_instance | [writeup](pwn/relaybox-canary/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `relaybox-fmt`       | 500 | team_instance | [writeup](pwn/relaybox-fmt/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `relaybox-heap`      | 550 | team_instance | [writeup](pwn/relaybox-heap/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `relaybox-sandbox`   | 600 | team_instance | [writeup](pwn/relaybox-sandbox/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `relaybox-uaf`       | 550 | team_instance | [writeup](pwn/relaybox-uaf/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `ret2csu-ish`        | 500 | team_instance | [writeup](pwn/ret2csu-ish/solution/)        | ret2csu-ish -- a statically linked, no-PIE x86-64 binary with a stack       |
| `ret2win-keyed`      | 300 | dynamic       | [writeup](pwn/ret2win-keyed/solution/)      | You are given a single x86-64 Linux binary, chall. It prints a token that   |
| `rop-diner`          | 500 | team_instance | [writeup](pwn/rop-diner/solution/)          | This instance's flag is on the service's filesystem, served by no route.    |
| `sandbox-break`      | 600 | team_instance | [writeup](pwn/sandbox-break/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `sensorhub-canary`   | 500 | team_instance | [writeup](pwn/sensorhub-canary/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `sensorhub-fmt`      | 500 | team_instance | [writeup](pwn/sensorhub-fmt/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `sensorhub-heap`     | 550 | team_instance | [writeup](pwn/sensorhub-heap/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `sensorhub-sandbox`  | 600 | team_instance | [writeup](pwn/sensorhub-sandbox/solution/)  | This instance's flag is on the service's filesystem, served by no route.    |
| `sensorhub-uaf`      | 550 | team_instance | [writeup](pwn/sensorhub-uaf/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `shellcode-decoder`  | 300 | dynamic       | [writeup](pwn/shellcode-decoder/solution/)  | You are given a single x86-64 Linux binary, chall. It prints a couple of    |
| `stack-smash-reveal` | 100 | dynamic       | [writeup](pwn/stack-smash-reveal/solution/) | You are given a single x86-64 Linux binary, chall. It reads some input and  |
| `uaf-ladder`         | 550 | team_instance | [writeup](pwn/uaf-ladder/solution/)         | This instance's flag is on the service's filesystem, served by no route.    |

## reverse (29)

| challenge             | pts | type          | writeup                                          | résumé                                                                      |
| --------------------- | --- | ------------- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| `byte-drift`          | 100 | dynamic       | [writeup](reverse/byte-drift/solution/)          | We recovered a small lock program, chall. It asks for a passphrase and      |
| `crc-forge`           | 300 | dynamic       | [writeup](reverse/crc-forge/solution/)           | chall is a stripped x86-64 ELF. It reads a flag and answers "checksums      |
| `firmwarelet-license` | 450 | team_instance | [writeup](reverse/firmwarelet-license/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `firmwarelet-unpack`  | 500 | team_instance | [writeup](reverse/firmwarelet-unpack/solution/)  | This instance's flag is on the service's filesystem, served by no route.    |
| `firmwarelet-vmesc`   | 550 | team_instance | [writeup](reverse/firmwarelet-vmesc/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `java-cafe`           | 300 | dynamic       | [writeup](reverse/java-cafe/solution/)           | We recovered Vault.class, a compiled Java class. Run it with java Vault     |
| `keygen-me`           | 450 | dynamic       | [writeup](reverse/keygen-me/solution/)           | chall is a stripped x86-64 "ACME license validator". Give it a license key  |
| `license-forge`       | 450 | team_instance | [writeup](reverse/license-forge/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `licensed-license`    | 450 | team_instance | [writeup](reverse/licensed-license/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `licensed-unpack`     | 500 | team_instance | [writeup](reverse/licensed-unpack/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `licensed-vmesc`      | 550 | team_instance | [writeup](reverse/licensed-vmesc/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `maze-vm`             | 500 | dynamic       | [writeup](reverse/maze-vm/solution/)             | We recovered a small self-contained "gate" binary, chall. It refuses to     |
| `packed-vm-lite`      | 350 | dynamic       | [writeup](reverse/packed-vm-lite/solution/)      | We pulled a small license checker, vmcheck, off an embedded device. When y… |
| `packedsvc-license`   | 450 | team_instance | [writeup](reverse/packedsvc-license/solution/)   | This instance's flag is on the service's filesystem, served by no route.    |
| `packedsvc-unpack`    | 500 | team_instance | [writeup](reverse/packedsvc-unpack/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `packedsvc-vmesc`     | 550 | team_instance | [writeup](reverse/packedsvc-vmesc/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `protod-license`      | 450 | team_instance | [writeup](reverse/protod-license/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `protod-unpack`       | 500 | team_instance | [writeup](reverse/protod-unpack/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `protod-vmesc`        | 550 | team_instance | [writeup](reverse/protod-vmesc/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `pyc-ghost`           | 300 | dynamic       | [writeup](reverse/pyc-ghost/solution/)           | We recovered vault.pyc, a compiled Python module. Run it and it asks for t… |
| `shell-lock`          | 150 | dynamic       | [writeup](reverse/shell-lock/solution/)          | lock.sh is a small self-decrypting shell script. Run it with the right      |
| `stack-vm`            | 300 | dynamic       | [writeup](reverse/stack-vm/solution/)            | chall is a stripped x86-64 ELF. It asks for a key and either rejects it or  |
| `strings-lie`         | 150 | dynamic       | [writeup](reverse/strings-lie/solution/)         | We recovered a tiny "secret vault" binary, chall. Run it and it happily     |
| `synthvm`             | 500 | dynamic       | [writeup](reverse/synthvm/solution/)             | We pulled a "license core", synthvm, off a device. Enter the key it accept… |
| `triple-wrap`         | 150 | dynamic       | [writeup](reverse/triple-wrap/solution/)         | chall is a stripped x86-64 ELF that checks a flag. Run it and it prints a   |
| `vm-escape`           | 550 | team_instance | [writeup](reverse/vm-escape/solution/)           | This instance's flag is on the service's filesystem, served by no route.    |
| `vmcore-license`      | 450 | team_instance | [writeup](reverse/vmcore-license/solution/)      | This instance's flag is on the service's filesystem, served by no route.    |
| `vmcore-unpack`       | 500 | team_instance | [writeup](reverse/vmcore-unpack/solution/)       | This instance's flag is on the service's filesystem, served by no route.    |
| `vmcore-vmesc`        | 550 | team_instance | [writeup](reverse/vmcore-vmesc/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |

## stego (8)

| challenge         | pts | type    | writeup                                    | résumé                                                                      |
| ----------------- | --- | ------- | ------------------------------------------ | --------------------------------------------------------------------------- |
| `dtmf-dial`       | 450 | dynamic | [writeup](stego/dtmf-dial/solution/)       | We recorded someone dialling a phone and saved it as dial.wav. It is just … |
| `layered-png`     | 450 | dynamic | [writeup](stego/layered-png/solution/)     | layers.png is a plain RGB gradient — or so it appears. The name is a hint   |
| `lsb-bmp`         | 100 | dynamic | [writeup](stego/lsb-bmp/solution/)         | A friend mailed us this bitmap postcard and swears there is more to it tha… |
| `png-text-chunk`  | 150 | dynamic | [writeup](stego/png-text-chunk/solution/)  | Someone shared this sunset.png with a suspiciously chatty set of propertie… |
| `trailing-zip`    | 100 | dynamic | [writeup](stego/trailing-zip/solution/)    | This banner.bmp opens fine in any image viewer, but its file size seems fa… |
| `twin-palette`    | 300 | dynamic | [writeup](stego/twin-palette/solution/)    | mosaic.png is a small blocky picture built from a colour palette. It looks  |
| `wav-lsb`         | 300 | dynamic | [writeup](stego/wav-lsb/solution/)         | A short audio clip, tone.wav, just plays a dull two-note hum. Our analyst   |
| `zero-width-note` | 150 | dynamic | [writeup](stego/zero-width-note/solution/) | We intercepted this bland internal memo.txt. It reads like nothing, yet th… |

## supplychain (14)

| challenge                  | pts | type          | writeup                                                   | résumé                                                                      |
| -------------------------- | --- | ------------- | --------------------------------------------------------- | --------------------------------------------------------------------------- |
| `build-cache-poison`       | 150 | dynamic       | [writeup](supplychain/build-cache-poison/solution/)       | On vous donne le Makefile qui alimente le cache de build d'un projet, sa    |
| `buildfarm-artswap`        | 500 | team_instance | [writeup](supplychain/buildfarm-artswap/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `buildfarm-depconf`        | 550 | team_instance | [writeup](supplychain/buildfarm-depconf/solution/)        | This instance's flag is on the service's filesystem, served by no route.    |
| `buildfarm-postinstall`    | 500 | team_instance | [writeup](supplychain/buildfarm-postinstall/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `dependency-confusion`     | 300 | dynamic       | [writeup](supplychain/dependency-confusion/solution/)     | Notre chaîne de build a récupéré le paquet interne acme-telemetry — mais    |
| `git-repo-backdoor`        | 450 | dynamic       | [writeup](supplychain/git-repo-backdoor/solution/)        | On a exfiltré un dépôt Git interne, livré ici sous forme d'archive tar du   |
| `layered-image-leak`       | 450 | dynamic       | [writeup](supplychain/layered-image-leak/solution/)       | On vous donne une image conteneur exportée avec docker save (image.tar).    |
| `lockfile-integrity-drift` | 300 | dynamic       | [writeup](supplychain/lockfile-integrity-drift/solution/) | On vous fournit un package-lock.json et les archives .tgz qu'il verrouille… |
| `pip-postinstall-hook`     | 300 | dynamic       | [writeup](supplychain/pip-postinstall-hook/solution/)     | On vous remet une archive source Python (acme-license-check-1.0.0.tar.gz)   |
| `poisoned-pipeline`        | 350 | team_instance | [writeup](supplychain/poisoned-pipeline/solution/)        | MiniCI. Un runner de build partagé : http://{host}:{port}. N'importe qui    |
| `provenance-forgery`       | 300 | dynamic       | [writeup](supplychain/provenance-forgery/solution/)       | Chaque release de acme-app est accompagnée d'une attestation de provenance  |
| `sbom-component-swap`      | 150 | dynamic       | [writeup](supplychain/sbom-component-swap/solution/)      | On vous donne le SBOM CycloneDX d'une release (bom.json), les binaires de   |
| `tuf-rollback`             | 300 | dynamic       | [writeup](supplychain/tuf-rollback/solution/)             | On vous donne les métadonnées d'un dépôt de mises à jour façon TUF          |
| `typosquat-lockfile`       | 150 | dynamic       | [writeup](supplychain/typosquat-lockfile/solution/)       | On vous donne le package-lock.json d'un projet front-end et toutes les      |

## sysadmin (12)

| challenge        | pts | type          | writeup                                      | résumé                                                                      |
| ---------------- | --- | ------------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| `alias-slip`     | 150 | dynamic       | [writeup](sysadmin/alias-slip/solution/)     | A snapshot of a small nginx-served site: the site config nginx.conf and th… |
| `auditd-cap`     | 500 | team_instance | [writeup](sysadmin/auditd-cap/solution/)     | This instance's flag is on the service's filesystem, served by no route.    |
| `auditd-cron`    | 450 | team_instance | [writeup](sysadmin/auditd-cron/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `auditd-systemd` | 500 | team_instance | [writeup](sysadmin/auditd-systemd/solution/) | This instance's flag is on the service's filesystem, served by no route.    |
| `env-forge`      | 300 | dynamic       | [writeup](sysadmin/env-forge/solution/)      | A developer pushed a deploy bundle for an internal API to a public repo:    |
| `mask-slip`      | 100 | dynamic       | [writeup](sysadmin/mask-slip/solution/)      | A CI pipeline (.github/workflows/deploy.yml) and one of its job logs        |
| `rbac-reveal`    | 100 | dynamic       | [writeup](sysadmin/rbac-reveal/solution/)    | A Kubernetes manifest bundle: an RBAC Role/RoleBinding (rbac.yaml), a       |
| `rotate-root`    | 200 | dynamic       | [writeup](sysadmin/rotate-root/solution/)    | An ops bundle from a host (mirrored under fs/): a cron job, a logrotate     |
| `secret-slip`    | 450 | team_instance | [writeup](sysadmin/secret-slip/solution/)    | This instance's flag is on the service's filesystem, served by no route.    |
| `state-secret`   | 450 | dynamic       | [writeup](sysadmin/state-secret/solution/)   | A committed Terraform bundle: the config (main.tf), its state file          |
| `unit-eval`      | 300 | dynamic       | [writeup](sysadmin/unit-eval/solution/)      | A snapshot of a systemd-driven report job: a template unit                  |
| `vault-reuse`    | 450 | dynamic       | [writeup](sysadmin/vault-reuse/solution/)    | An Ansible project snapshot: ansible.cfg, inventory.ini, groupvars/         |

## warmup (16)

| challenge            | pts | type    | writeup                                        | résumé                                                                |
| -------------------- | --- | ------- | ---------------------------------------------- | --------------------------------------------------------------------- |
| `atbash-cipher`      | 50  | dynamic | [writeup](warmup/atbash-cipher/solution/)      | secret.txt was made by mirroring the alphabet: A swaps with Z,        |
| `base32-decode`      | 50  | dynamic | [writeup](warmup/base32-decode/solution/)      | secret.txt holds only UPPERCASE letters A-Z and the digits 2-7,       |
| `base64-decode`      | 50  | dynamic | [writeup](warmup/base64-decode/solution/)      | A friend swears this text is 'encrypted'. It only contains letters,   |
| `base85-decode`      | 50  | dynamic | [writeup](warmup/base85-decode/solution/)      | secret.txt looks like line noise: a dense mix of letters, digits and  |
| `binary-ascii`       | 50  | dynamic | [writeup](warmup/binary-ascii/solution/)       | bits.txt is nothing but groups of eight 0s and 1s separated by        |
| `csv-cell`           | 50  | dynamic | [writeup](warmup/csv-cell/solution/)           | roster.csv is a small spreadsheet of players. One cell, among all the |
| `hex-decode`         | 50  | dynamic | [writeup](warmup/hex-decode/solution/)         | secret.txt is one long string of the characters 0-9 and a-f.          |
| `html-entities`      | 50  | dynamic | [writeup](warmup/html-entities/solution/)      | pagesnippet.txt is a run of &NNN; codes -- the kind a web page        |
| `morse-code`         | 50  | dynamic | [writeup](warmup/morse-code/solution/)         | signal.txt is a line of dots (.) and dashes (-). Letters are          |
| `reverse-string`     | 50  | dynamic | [writeup](warmup/reverse-string/solution/)     | backwards.txt contains the flag written from right to left. Read it   |
| `rot13-decode`       | 50  | dynamic | [writeup](warmup/rot13-decode/solution/)       | secret.txt reads almost like the flag, but every letter has been      |
| `rot47-decode`       | 50  | dynamic | [writeup](warmup/rot47-decode/solution/)       | secret.txt is a jumble of visible punctuation and characters. It is   |
| `tap-code`           | 50  | dynamic | [writeup](warmup/tap-code/solution/)           | taps.txt is a list of two-digit numbers. Each number is a row then a  |
| `url-encoding`       | 50  | dynamic | [writeup](warmup/url-encoding/solution/)       | encoded.txt is a string full of % signs followed by two hex           |
| `vigenere-known-key` | 50  | dynamic | [writeup](warmup/vigenere-known-key/solution/) | cipher.txt was enciphered with a Vigenere cipher. The key is not a    |
| `zip-comment`        | 50  | dynamic | [writeup](warmup/zip-comment/solution/)        | archive.zip unzips to a single, unhelpful text file. The flag is not  |

## web (23)

| challenge                    | pts | type          | writeup                                             | résumé                                                                      |
| ---------------------------- | --- | ------------- | --------------------------------------------------- | --------------------------------------------------------------------------- |
| `cms-authbypass`             | 450 | team_instance | [writeup](web/cms-authbypass/solution/)             | This instance's flag is on the service's filesystem, served by no route.    |
| `cms-jwtconf`                | 400 | team_instance | [writeup](web/cms-jwtconf/solution/)                | This instance's flag is on the service's filesystem, served by no route.    |
| `cms-smuggle`                | 500 | team_instance | [writeup](web/cms-smuggle/solution/)                | This instance's flag is on the service's filesystem, served by no route.    |
| `cms-uploadssrf`             | 450 | team_instance | [writeup](web/cms-uploadssrf/solution/)             | This instance's flag is on the service's filesystem, served by no route.    |
| `flask-unsign`               | 150 | dynamic       | [writeup](web/flask-unsign/solution/)               | A small Members Panel ships as source, along with a session cookie          |
| `forum-protopoll`            | 500 | team_instance | [writeup](web/forum-protopoll/solution/)            | This instance's flag is on the service's filesystem, served by no route.    |
| `forum-sqli2`                | 450 | team_instance | [writeup](web/forum-sqli2/solution/)                | This instance's flag is on the service's filesystem, served by no route.    |
| `forum-xxe`                  | 450 | team_instance | [writeup](web/forum-xxe/solution/)                  | This instance's flag is on the service's filesystem, served by no route.    |
| `graph-climb`                | 450 | team_instance | [writeup](web/graph-climb/solution/)                | This instance's flag is on the service's filesystem, served by no route.    |
| `graphql-introspection-maze` | 500 | team_instance | [writeup](web/graphql-introspection-maze/solution/) | Atlas Ops exposes a single GraphQL endpoint at POST /graphql                |
| `jwt-cousin`                 | 150 | team_instance | [writeup](web/jwt-cousin/solution/)                 | "It's basically a JWT," said no one who read the code.                      |
| `jwt-forge`                  | 150 | dynamic       | [writeup](web/jwt-forge/solution/)                  | You have the full source of an internal Ops Console plus a leaked config    |
| `mass-assignment`            | 150 | dynamic       | [writeup](web/mass-assignment/solution/)            | A profile service ships as source, plus the user store and a captured requ… |
| `path-traversal-archive`     | 150 | dynamic       | [writeup](web/path-traversal-archive/solution/)     | An "Asset CDN" serves files from its public web root. You get the handler   |
| `php-unserialize`            | 300 | dynamic       | [writeup](web/php-unserialize/solution/)            | A legacy PHP portal ships as source, along with a session cookie captured   |
| `race-the-coupon`            | 400 | team_instance | [writeup](web/race-the-coupon/solution/)            | NimbusPay store wallet exposes a small JSON API. Every account starts       |
| `reseau-pyramide`            | 400 | team_instance | [writeup](web/reseau-pyramide/solution/)            | KékéliCash est une plateforme de marketing de réseau (« MLM »).             |
| `reset-token-lcg`            | 450 | dynamic       | [writeup](web/reset-token-lcg/solution/)            | A password-reset service ships as source, plus the server's reset log. Eac… |
| `smuggle-gap`                | 500 | team_instance | [writeup](web/smuggle-gap/solution/)                | Nimbus runs a tiny job service behind an edge proxy. The edge is the only   |
| `sqlite-union`               | 150 | dynamic       | [writeup](web/sqlite-union/solution/)               | A souvenir shop exposes a product search API. You get the handler source a… |
| `ssrf-metadata-decoy`        | 350 | team_instance | [writeup](web/ssrf-metadata-decoy/solution/)        | imgproxy is a company image-fetch proxy: give it a URL and it fetches the   |
| `ssti-jinja`                 | 300 | dynamic       | [writeup](web/ssti-jinja/solution/)                 | A greeting-card service ships as source, with a captured normal request. I… |
| `webhook-relay`              | 450 | team_instance | [writeup](web/webhook-relay/solution/)              | This instance's flag is on the service's filesystem, served by no route.    |
