#!/usr/bin/python
from passlib.hash import bcrypt_sha256

password = raw_input('Enter Password to hash: ')
hash = bcrypt_sha256.encrypt(password)
print(hash)
