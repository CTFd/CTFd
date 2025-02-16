import os

from CTFd.cache import cache
from CTFd.exceptions.email import (
    UserConfirmTokenInvalidException,
    UserResetPasswordTokenInvalidException,
)
from CTFd.utils.encoding import hexencode


def generate_email_confirm_token(addr, timeout=1800):
    nonce = hexencode(os.urandom(32))
    cache.set(f"confirm_email_{nonce}", addr, timeout=timeout)
    return nonce


def verify_email_confirm_token(nonce):
    addr = cache.get(f"confirm_email_{nonce}")
    if addr is None:
        raise UserConfirmTokenInvalidException
    return addr


def remove_email_confirm_token(nonce):
    cache.delete(f"confirm_email_{nonce}")


def generate_password_reset_token(addr, timeout=1800):
    nonce = hexencode(os.urandom(32))
    cache.set(f"reset_password_{nonce}", addr, timeout=timeout)
    return nonce


def verify_reset_password_token(nonce):
    addr = cache.get(f"reset_password_{nonce}")
    if addr is None:
        raise UserResetPasswordTokenInvalidException
    return addr


def remove_reset_password_token(nonce):
    cache.delete(f"reset_password_{nonce}")
