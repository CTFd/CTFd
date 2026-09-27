<!-- nctf-meta category="osint" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# social-export

**Category:** osint · **Difficulty:** easy
**Flag:** `NCTF{…}`

## Summary

Two social exports are linked by a reused email address. The matching Mastodon
handle is the XOR key for a hex "backup key" in a Telegram message.

## Technique

Cross-platform correlation on a shared identifier (email), then repeating-key
XOR decryption.

## Step by step

1. In `telegram_export.json`, the account's `email_on_file` is
   `s.scribe.228@mailtg.tg`, and message id 3 carries
   `backup key (ne pas perdre) hex=<ciphertext>`.
2. In `mastodon_export.json`, three accounts are listed. Only one,
   `shadowscribe`, has the same `email` (`s.scribe.228@mailtg.tg`). Its note even
   brags "je change de pseudo partout, mais jamais d'adresse mail."
3. Use the Mastodon `username` `shadowscribe` as a repeating XOR key over the
   hex bytes.
4. The plaintext is the flag.

Run `python3 solution/solve.py` to reproduce.

## Flag

`NCTF{…}`
