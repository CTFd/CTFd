import base64
import hashlib
import re

from pwdlib import PasswordHash
from pwdlib.hashers import argon2, bcrypt

from CTFd.utils import string_types

# Passlib bcrypt-sha256 (v1.7.2): $bcrypt-sha256$2b,12$<salt>$<digest>
# Passlib bcrypt-sha256 (v1.7.4): $bcrypt-sha256$v=2,t=2b,r=12$<salt>$<digest>
_PASSLIB_V1_RE = re.compile(
    r"^\$bcrypt-sha256\$(2[ab]),(\d+)\$([A-Za-z0-9./]{22})\$([A-Za-z0-9./]{31})$"
)
_PASSLIB_V2_RE = re.compile(
    r"^\$bcrypt-sha256\$v=2,t=(2[ab]),r=(\d+)\$([A-Za-z0-9./]{22})\$([A-Za-z0-9./]{31})$"
)

_bcrypt = bcrypt.BcryptHasher()


class PasslibBcryptSha256Hasher:
    """Backwards-compatible hasher for passlib's bcrypt_sha256 hashes.

    passlib encoded these as `$bcrypt-sha256$...` and computed them by
    feeding `base64(sha256(password))` into bcrypt. This hasher can
    identify and verify such legacy hashes so that existing users can
    still log in after the migration to pwdlib.
    """

    @classmethod
    def identify(cls, hash: str | bytes) -> bool:
        if isinstance(hash, bytes):
            hash = hash.decode("utf-8")
        return hash.startswith("$bcrypt-sha256$")

    @staticmethod
    def _parse(hash: str) -> tuple[str, str, str, str] | None:
        """Return (ident, rounds, salt, digest) or *None*."""
        m = _PASSLIB_V1_RE.match(hash) or _PASSLIB_V2_RE.match(hash)
        if m is None:
            return None
        return m.group(1), m.group(2), m.group(3), m.group(4)

    def hash(self, password: str | bytes, *, salt: bytes | None = None) -> str:
        raise NotImplementedError(
            "PasslibBcryptSha256Hasher is verification-only, use Argon2Hasher for new hashes."
        )

    def verify(self, password: str | bytes, hash: str | bytes) -> bool:
        if isinstance(hash, bytes):
            hash = hash.decode("utf-8")
        if isinstance(password, bytes):
            password = password.decode("utf-8")

        parsed = self._parse(hash)
        if parsed is None:
            return False

        alg, cost, salt, digest = parsed
        bcrypt_hash = f"${alg}${cost}${salt}{digest}".encode("utf-8")
        # passlib used base64(sha256(password)) as bcrypt input
        sha256_digest = base64.b64encode(
            hashlib.sha256(password.encode("utf-8")).digest()
        )
        return _bcrypt.verify(sha256_digest, bcrypt_hash)

    # We don't actually use this method, but it may be useful in the future
    def check_needs_rehash(self, hash: str | bytes) -> bool:
        return True


# The first hasher is the default when using .hash(), subsequent hashers are
# for backwards-compatible verification only.
_password_hasher = PasswordHash((argon2.Argon2Hasher(), PasslibBcryptSha256Hasher()))


def hash_password(plaintext):
    return _password_hasher.hash(plaintext)


def verify_password(plaintext, ciphertext):
    return _password_hasher.verify(plaintext, ciphertext)


def sha256(p):
    if isinstance(p, string_types):
        p = p.encode("utf-8")
    return hashlib.sha256(p).hexdigest()
