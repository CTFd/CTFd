from passlib.hash import bcrypt_sha256
import hashlib


def hash_password(p):
    return bcrypt_sha256.encrypt(p)


def check_password(p, hash):
    return bcrypt_sha256.verify(p, hash)


def sha256(p):
    return hashlib.sha256(p).hexdigest()
