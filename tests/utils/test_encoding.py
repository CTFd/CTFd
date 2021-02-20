# -*- coding: utf-8 -*-

import string

from CTFd.utils.encoding import base64decode, base64encode, hexdecode, hexencode


def test_hexencode():
    value = (
        "303132333435363738396162636465666768696a6b6c6d6e6f7071727374757677"
        "78797a4142434445464748494a4b4c4d4e4f505152535455565758595a21222324"
        "25262728292a2b2c2d2e2f3a3b3c3d3e3f405b5c5d5e5f607b7c7d7e20090a0d0b0c"
    )
    assert hexencode(string.printable) == value


def test_hexdecode():
    saved = (
        "303132333435363738396162636465666768696a6b6c6d6e6f7071727374757677"
        "78797a4142434445464748494a4b4c4d4e4f505152535455565758595a21222324"
        "25262728292a2b2c2d2e2f3a3b3c3d3e3f405b5c5d5e5f607b7c7d7e20090a0d0b0c"
    )
    assert hexdecode(saved) == string.printable


def test_base64encode():
    """The base64encode wrapper works properly"""
    assert base64encode("abc123") == "YWJjMTIz"
    assert (
        base64encode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4')
        == "InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ"
    )
    assert (
        base64encode("user+user@examplectf.com") == "dXNlcit1c2VyQGV4YW1wbGVjdGYuY29t"
    )
    assert base64encode("😆") == "8J-Yhg"


def test_base64decode():
    """The base64decode wrapper works properly"""
    assert base64decode("YWJjMTIz") == "abc123"
    assert (
        base64decode(
            "InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ"
        )
        == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
    )
    assert (
        base64decode("dXNlcit1c2VyQGV4YW1wbGVjdGYuY29t") == "user+user@examplectf.com"
    )
    assert base64decode("8J-Yhg") == "😆"
