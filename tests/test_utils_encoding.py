#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils.encoding import urlsafe_base64_decode, urlsafe_base64_encode
import six


def test_urlsafe_base64_encode():
    """The urlsafe_base64_encode wrapper works properly"""
    if six.PY2:
        assert urlsafe_base64_encode('abc123') == 'YWJjMTIz'
        assert urlsafe_base64_encode(unicode('abc123')) == 'YWJjMTIz'
        assert urlsafe_base64_encode(unicode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4')) == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ'
        assert urlsafe_base64_encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8'
        assert urlsafe_base64_encode('😆') == '8J-Yhg'
    else:
        assert urlsafe_base64_encode('abc123') == 'YWJjMTIz'
        assert urlsafe_base64_encode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4') == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ'
        assert urlsafe_base64_encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8'
        assert urlsafe_base64_encode('😆') == '8J-Yhg'


def test_urlsafe_base64_decode():
    """The urlsafe_base64_decode wrapper works properly"""
    if six.PY2:
        assert urlsafe_base64_decode('YWJjMTIz') == 'abc123'
        assert urlsafe_base64_decode(unicode('YWJjMTIz')) == 'abc123'
        assert urlsafe_base64_decode(unicode('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ')) == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert urlsafe_base64_decode('8J-Yhg==') == '😆'
        assert urlsafe_base64_decode('8J-Yhg') == '😆'
    else:
        assert urlsafe_base64_decode('YWJjMTIz') == 'abc123'
        assert urlsafe_base64_decode('YWJjMTIz') == 'abc123'
        assert urlsafe_base64_decode('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ') == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert urlsafe_base64_decode('dXNlcit1c2VyQGN0ZmQuaW8=') == 'user+user@ctfd.io'
        assert urlsafe_base64_decode('dXNlcit1c2VyQGN0ZmQuaW8') == 'user+user@ctfd.io'
        assert urlsafe_base64_decode('8J-Yhg==') == '😆'
        assert urlsafe_base64_decode('8J-Yhg') == '😆'