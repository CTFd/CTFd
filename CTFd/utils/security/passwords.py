from passlib.hash import bcrypt_sha256


def hash_password(p):
    return bcrypt_sha256.encrypt(p)


def check_password(p, hash):
    return bcrypt_sha256.verify(p, hash)
