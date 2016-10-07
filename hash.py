#!/usr/bin/python
import hashlib
import os

##### GENERATE SALT #####
with open('.ctfd_sha256_salt', 'a+') as secret:
    secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
    salt = secret.read()
    if not salt:
        salt = os.urandom(64)
        secret.write(salt)
        secret.flush()

password = raw_input('Enter Password to hash: ')
hash_object = hashlib.sha256(salt+password)
hex_dig = hash_object.hexdigest()
print(hex_dig)
