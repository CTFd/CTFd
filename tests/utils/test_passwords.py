from CTFd.utils.security.passwords import sha256


def test_sha256():
    assert sha256('asdf') == 'f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b'
