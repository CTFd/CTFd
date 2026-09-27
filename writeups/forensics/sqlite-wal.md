<!-- nctf-meta category="forensics" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# sqlite-wal

**Category:** forensics · **Difficulty:** medium
**Flag:** `NCTF{…}` (static)

## One-line summary

The redaction lives only in the write-ahead log; the main `app.db` file was
never checkpointed, so opening it without its `-wal` reveals the original
(obfuscated) token — base64-decode and XOR it to get the flag.

## Technique

SQLite WAL divergence. The database was built like this:

1. Insert `recovery_token = NCTF{…}` and **checkpoint**, so the flag is written
   into the main `app.db` file and the WAL is emptied.
2. `UPDATE ... SET value = 'REDACTED...'` and commit, but **do not checkpoint**.
   That change is recorded only in a fresh `app.db-wal`.

So the two files disagree:

- `app.db` + `app.db-wal` together (the normal way SQLite opens it) -> SQLite
  replays the WAL and you read `REDACTED-by-dlp-policy`.
- `app.db` **alone** -> the un-checkpointed main file still contains the original
  `recovery_token` page.

That original page value is **not** the flag in cleartext. It is stored as
`base64(single-byte-XOR(flag))`, so `strings app.db | grep NCTF` finds nothing —
you must recover the old row _and_ undo the encoding.

## Step by step

1. `sqlite3 app.db "SELECT * FROM secrets"` shows the redacted token (the WAL is
   replayed).
2. Copy `app.db` into an empty directory, leaving `app.db-wal` behind.
3. Open that lone copy: `sqlite3 main.db "SELECT * FROM secrets"`. Now nothing
   replays the redaction and you get the original `recovery_token` — a base64
   blob, not the flag.
4. Base64-decode the blob, then brute-force the single XOR byte (0–255); the key
   whose output starts with `NCTF{…}`
