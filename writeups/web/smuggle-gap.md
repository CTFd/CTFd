<!-- nctf-meta category="web" difficulty="hard" points="500" author="ctf-2026" stub="0" -->

# smuggle-gap

## TL;DR

The edge proxy and the internal app disagree about where a request's body ends.
Smuggle a second request inside the body of an allowed one; the edge authorises
only the request it can see (`POST /submit`), while the internal app parses the
"body" as a fresh `GET /internal/flag` and serves the flag.

## The two-tier setup

- **Edge** (`app/front.py`, port 8080, the only exposed tier): forwards traffic
  to the internal app and answers management routes itself with `403`. Its ACL
  is hardened against case / percent-encoding / `..` / `//` / backslash tricks,
  so you cannot smuggle `/internal` into the _visible_ request line.
- **Internal app** (`app/backend.py`, loopback `127.0.0.1:9000`, not exposed):
  serves `GET /`, `GET /status`, `POST /submit`, and the management route
  `GET /internal/flag`, which returns the per-team flag to anyone who reaches
  it. It trusts the network boundary -- if a request arrives, the edge is
  assumed to have vetted it.

The edge and the app talk over a single **keep-alive** connection, so multiple
requests framed onto that connection are all served in order.

## The parsing gap (why it desyncs)

Both tiers frame request bodies, but by different rules (`app/framing.py`):

| Tier                           | How it sizes a body                                                                                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Edge** (`edge_body_length`)  | `Content-Length` only. It has no concept of chunked transfer -- `Transfer-Encoding` is just an opaque header it copies downstream.                       |
| **App** (`app_split_requests`) | If `Transfer-Encoding: chunked` is present, it frames the body as chunked and **ignores `Content-Length`**. Otherwise it falls back to `Content-Length`. |

Send a request that carries **both** headers with values that describe
different body lengths, and the two tiers cut the byte stream in different
places. This is a classic Content-Length / Transfer-Encoding request-smuggling
desync (here implemented in our own minimal, deterministic proxy -- no real CVE
involved).

## The payload

```
POST /submit HTTP/1.1\r\n
Host: edge\r\n
Content-Type: application/octet-stream\r\n
Transfer-Encoding: chunked\r\n
Content-Length: 48\r\n
\r\n
0\r\n
\r\n
GET /internal/flag HTTP/1.1\r\n
Host: internal\r\n
\r\n
```

`Content-Length` is set to the exact length of everything after the blank line
(`0\r\n\r\n` + the smuggled request). `solve.py` computes it programmatically so
it is always correct.

- **Edge reading:** `Content-Length: 48` -> the whole blob starting at `0\r\n...`
  is the body of one `POST /submit`. `/submit` is allowed, so the edge forwards
  all 48 body bytes verbatim to the app. The edge never sees a second request.
- **App reading:** `Transfer-Encoding: chunked` wins. `0\r\n\r\n` is a complete
  **empty** chunked body, so `POST /submit` ends there. The remaining bytes --
  `GET /internal/flag ...` -- are parsed as a **second** request on the same
  keep-alive connection, and the app serves the flag. The edge relays both app
  responses back to us; the flag is in the second one.

Because it is an empty chunked body (not a timing race), the result is
deterministic: it works on the first try, every time.

## Run it

```
python3 solution/solve.py http://HOST:PORT
```

Expected output:

```
[*] direct GET /internal/flag -> HTTP/1.1 403 Forbidden
[*] sending framing-gap payload (edge sees one request, app sees two)
[+] FLAG: NCTF{…}
```

## Decoys (each costs real effort to rule out, none is labelled)

- **ACL address tricks.** `/Internal/flag`, `/%2569nternal/flag`,
  `/internal/../internal/flag`, `/internal//flag`, `/internal\flag`, etc. all
  normalise back to `/internal` at the edge and stay `403`. Only bytes the edge
  cannot see as `/internal` get through -- i.e. the desync.
- **`X-Debug-Route` on `/status`.** Looks like an internal re-routing knob; it
  only echoes the requested route (`"dispatched": false`) and never dispatches
  or leaks the flag.

## Verification performed by the author

- Unit test of `framing.py`: `edge_take_one` frames the payload as **one**
  request (`POST /submit`), while `app_split_requests` frames it as **two**
  (`POST /submit`, then `GET /internal/flag`); a plain request frames
  identically on both tiers.
- End-to-end: ran `backend.py` + `front.py` on localhost and ran this solver.
  Direct `GET /internal/flag` returned `403`; the smuggling payload returned the
  per-instance flag, matching `flag.py`'s derivation
  (`NCTF{…}` for the demo `CHALLENGE_SECRET`).
- Confirmed every ACL normalisation bypass above is blocked.
