# Python UNIX Password Cracker

## Category: Basics


We will be testing your python scripting skills with this challenge.

In the past UNIX systems used to store all of their user information in `etc/passwd`, which included the username, hash+salt of password, user id, user group, name, home directory and what shell they prefer. Back then, computers were slow, so using a short hash was enough to keep the computer secure. Hashes in modern UNIX operating systems are stored in `etc/shadow`, and are much longer, and much less likely to have collisions, and are also much harder to crack (unless the password is in a wordlist).

Dictionary attacks, employ a list of passwords, and other criteria to narrow down the search of a password. `rockyou.txt` is probably the most famous password list out ther. If you would like to learn more about how it came about, you can read [here](https://www.cosmodiumcs.com/post/the-story-of-rockyou)

Kali (your VM) has the `rockyou.txt` saved in the `usr/share/wordlists` directory which you will use in your script.

Here is what you need to do:
1. Read in the supplied `passwd` file
2. Use the passwords in `rockyou.txt` to crack the hashes for all users
3. Your flag will be `prac-sec{studentpass-victimpass-rootpass}`, with the dashes.

A couple tips and hints:
- The first 2 characters of the given hashes is the salt
- `crypt.crypt()` may be useful
- Not everything in life is perfect when you use other people's stuff. You might encounter UTF-8 related issues with `rockyou.txt`, use `iconv -f utf-8 -t utf-8 -c rockyou.txt > new.txt` to resolve them.

Life tip: check your own passwords against the list.