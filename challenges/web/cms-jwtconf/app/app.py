#!/usr/bin/env python3
"""JWT Relay — a homegrown-auth service with an algorithm-confusion flaw.

Design (served challenge, per-team flag):

  * On boot the service generates an RSA key pair. It signs session tokens with
    RS256 and *publishes the public key* at ``/pubkey`` — normal, a client needs
    it to verify tokens offline.
  * The token verifier is homegrown. It reads the ``alg`` header and picks the
    check accordingly, but it feeds the **same ``key`` value** to both branches:
    the RSA public key for RS256, and — the bug — that very public-key PEM as the
    HMAC secret for HS256. This is the classic RS256/HS256 confusion.
  * ``/`` mints a guest token (``role=guest``). ``/flag`` returns this instance's
    flag, but only to a token whose ``role`` is ``admin``.

Intended path: fetch the public key, forge ``{"role":"admin"}`` as an HS256 token
whose HMAC secret is the exact public-key PEM bytes, present it to ``/flag``.

The flag lives at ``/flag.txt`` (written by entrypoint.sh from the per-team
secret) and is served by no route other than the admin-gated ``/flag`` check —
there is no path that returns it without a valid admin token.
"""
import base64
import hashlib
import hmac
import json
import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from flask import Flask, jsonify, request

app = Flask(__name__)

# One RSA key pair per instance (per team). The public half is published; the
# private half signs guest tokens and never leaves the process.
_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUB_PEM = _KEY.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64url_dec(txt: str) -> bytes:
    pad = "=" * (-len(txt) % 4)
    return base64.urlsafe_b64decode(txt + pad)


def _sign_rs256(signing_input: bytes) -> bytes:
    return _KEY.sign(signing_input, padding.PKCS1v15(), hashes_sha256())


def hashes_sha256():
    from cryptography.hazmat.primitives import hashes

    return hashes.SHA256()


def issue(role: str) -> str:
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"role": role, "iss": "cms-jwtconf"}
    signing_input = (
        _b64url(json.dumps(header).encode())
        + "."
        + _b64url(json.dumps(payload).encode())
    ).encode()
    sig = _sign_rs256(signing_input)
    return signing_input.decode() + "." + _b64url(sig)


def verify(token: str):
    """Return the token payload if the signature checks out, else None.

    Homegrown, and deliberately confused: ``key`` is the RSA public key, used
    directly as the HMAC secret when the header says HS256.
    """
    try:
        h_b64, p_b64, s_b64 = token.split(".")
    except ValueError:
        return None
    signing_input = (h_b64 + "." + p_b64).encode()
    try:
        header = json.loads(_b64url_dec(h_b64))
        payload = json.loads(_b64url_dec(p_b64))
        sig = _b64url_dec(s_b64)
    except Exception:
        return None

    alg = header.get("alg")
    key = _PUB_PEM  # the one and only "key" this verifier knows about
    if alg == "RS256":
        try:
            _KEY.public_key().verify(
                sig, signing_input, padding.PKCS1v15(), hashes_sha256()
            )
        except InvalidSignature:
            return None
        return payload
    if alg == "HS256":
        expected = hmac.new(key, signing_input, hashlib.sha256).digest()
        if hmac.compare_digest(expected, sig):
            return payload
        return None
    return None


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>JWT Relay &middot; SSO</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#38bdf8;--ok:#3ddc97;--bad:#ff6b6b;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#0b2a3a,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:900px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  input,textarea{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:12.5px}
  textarea{min-height:70px;resize:vertical;word-break:break-all}
  button{margin-top:12px;background:var(--acc);color:#042330;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  button.ghost{background:transparent;border:1px solid var(--line);color:var(--ink)}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap;word-break:break-all}
  .row{display:flex;gap:8px}code{font-family:var(--mono);color:#ffd479}.muted{color:var(--mut);font-size:12px}
</style></head><body>
<header><div class="logo"><b>JWT</b> Relay</div>
  <div class="tag">SSO interne &middot; jetons RS256</div></header>
<main>
  <div class="card">
    <h2>Votre session</h2>
    <p class="h">Un jeton invité (<code>role=guest</code>) signé en RS256 vous est délivré.
       Vérifiez-le hors-ligne avec la clé publique publiée.</p>
    <label>Jeton courant</label>
    <textarea id="tok">__GUEST_TOKEN__</textarea>
    <div class="row">
      <button class="ghost" onclick="whoami()">/whoami</button>
      <button class="ghost" onclick="pubkey()">Voir /pubkey</button>
      <button onclick="getflag()">/flag</button>
    </div>
    <pre id="out" class="muted">&mdash;</pre>
  </div>
  <div class="card">
    <h2>Clé publique</h2>
    <p class="h">Le vérificateur maison lit l'entête <code>alg</code> du jeton.</p>
    <pre id="pk" class="muted">(cliquez « Voir /pubkey »)</pre>
  </div>
</main>
<script>
function bearer(){return document.getElementById('tok').value.trim();}
async function whoami(){
  const r=await fetch('/whoami',{headers:{Authorization:'Bearer '+bearer()}});
  document.getElementById('out').textContent='['+r.status+']\\n'+await r.text();}
async function getflag(){
  const r=await fetch('/flag',{headers:{Authorization:'Bearer '+bearer()}});
  document.getElementById('out').textContent='['+r.status+']\\n'+await r.text();}
async function pubkey(){
  const r=await fetch('/pubkey');document.getElementById('pk').textContent=await r.text();}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML.replace("__GUEST_TOKEN__", issue("guest"))


@app.route("/pubkey")
def pubkey():
    return app.response_class(_PUB_PEM, mimetype="text/plain")


def _bearer():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[len("Bearer ") :].strip()
    return request.args.get("token", "")


@app.route("/whoami")
def whoami():
    payload = verify(_bearer())
    if payload is None:
        return jsonify({"error": "invalid or missing token"}), 401
    return jsonify({"role": payload.get("role")})


@app.route("/flag")
def flag():
    payload = verify(_bearer())
    if payload is None:
        return jsonify({"error": "invalid or missing token"}), 401
    if payload.get("role") != "admin":
        return jsonify({"error": "admin only"}), 403
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return jsonify({"flag": fh.read().strip()})
    except OSError:
        return jsonify({"error": "flag unavailable"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
