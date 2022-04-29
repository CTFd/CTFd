#!/usr/bin/python3

from pwn import *

context.terminal = ['konsole','-e'] # replace this with your terminal of choice
#context.log_level = 'debug'
context.binary = './build/AAAAAAAAAAAAAAAA'

e = ELF('./build/AAAAAAAAAAAAAAAA')
rop = ROP('./build/AAAAAAAAAAAAAAAA')
if 'd' in sys.argv:
    p = e.debug()
elif 'r' in sys.argv:
    p = remote('localhost', 5000)
elif 's' in sys.argv:
    s = ssh(host='host', user='username', password='password')
    p = s.process('./build/AAAAAAAAAAAAAAAA', cwd='problemDir')
else:
    p = e.process()

payload = b'B' * 200

p.sendline(payload)
p.interactive()
