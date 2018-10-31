from CTFd.utils.security.passwords import sha256, hash_password, check_password


def test_hash_password():
    assert hash_password('asdf').startswith('$bcrypt-sha256')


def test_check_password():
    assert check_password('asdf', '$bcrypt-sha256$2b,12$I0CNXRkGD2Bi/lbC4vZ7Y.$1WoilsadKpOjXa/be9x3dyu7p.mslZ6') == True


def test_sha256():
    assert sha256('asdf') == 'f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b'
