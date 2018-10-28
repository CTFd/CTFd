from tests.helpers import *
from CTFd.utils.encoding import base64encode, base64decode

def test_base64encode():
    """The base64encode wrapper works properly"""
    if six.PY2:
        assert base64encode('abc123') == 'YWJjMTIz'
        assert base64encode(unicode('abc123')) == 'YWJjMTIz'
        assert base64encode(unicode
            ('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4')) == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ'
        assert base64encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8'
        assert base64encode('😆') == '8J-Yhg'
    else:
        assert base64encode('abc123') == 'YWJjMTIz'
        assert base64encode \
            ('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4') == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ'
        assert base64encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8'
        assert base64encode('😆') == '8J-Yhg'


def test_base64decode():
    """The base64decode wrapper works properly"""
    if six.PY2:
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode(unicode('YWJjMTIz')) == 'abc123'
        assert base64decode(unicode
            ('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ')) == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert base64decode('8J-Yhg') == '😆'
    else:
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode \
            ('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ') == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert base64decode('dXNlcit1c2VyQGN0ZmQuaW8') == 'user+user@ctfd.io'
        assert base64decode('8J-Yhg') == '😆'