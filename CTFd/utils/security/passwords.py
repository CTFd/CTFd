from CTFd.utils import string_types
from passlib.hash import bcrypt_sha256
import hashlib


def hash_password(p):
    return bcrypt_sha256.encrypt(p)


def check_password(p, hash):
    return bcrypt_sha256.verify(p, hash)


def sha256(p):
    if isinstance(p, string_types):
        p = p.encode('utf-8')
    return hashlib.sha256(p).hexdigest()
