# Hash Kitty

## Category: Cryptography

Here is a dump of 5 hashes. Can you crack them?

All I can tell you is that they are in the format `NCL-LTOX-` followed by 4 digits, meaning `NCL-LTOX-0000` could be a viable option.

Definitely don't do this by hand. Your VM has preinstalled tools called `hash-identifier` and `hashcat` that will be very helpful.

Your flag is `prac-sec{####-####-####-####}` where the `####` are the numbers at the end of the passwords, in increasing order. If hashes stood for `NCL-LTOX-0001`, `NCL-LTOX-0002`, `NCL-LTOX-0003` and `NCL-LTOX-0004`, then the flag would be `prac-sec{0001-0002-0003-0004}`.