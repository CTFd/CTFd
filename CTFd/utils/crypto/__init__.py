import hashlib

from passlib.hash import bcrypt_sha256

from CTFd.utils import string_types


def hash_password(plaintext):
    return bcrypt_sha256.hash(str(plaintext))


def verify_password(plaintext, ciphertext):
    return bcrypt_sha256.verify(plaintext, ciphertext)


def sha256(p):
    if isinstance(p, string_types):
        p = p.encode("utf-8")
    return hashlib.sha256(p).hexdigest()
