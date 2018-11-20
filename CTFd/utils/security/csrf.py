from CTFd.utils.encoding import hexencode
import os


def generate_nonce():
    return hexencode(os.urandom(32)).decode('utf-8')
