#!/usr/bin/env python3
"""Forum Authbypass — broken access control -> IDOR -> mass-assignment.

Design (served challenge, per-team flag):

  * ``/register`` creates a user (role=user) and returns a session token.
    ``/me`` reports your server-side role. ``/flag`` returns this instance's flag
    only when your session's role is ``admin``.
  * The admin API (``/admin/users`` and the update endpoint) is "protected" by a
    **client-supplied header** ``X-Account-Role: admin`` — broken access control:
    the server trusts a value the client sets.
  * ``/api/users/<id>`` (GET) is an IDOR: any user is readable with no authz.
  * ``POST /api/users/<id>`` (update) is a **mass-assignment**: it writes every
    field in the body, ``role`` included -- but only past the header gate.

Intended path: register → note your uid → send the update with the forged
``X-Account-Role: admin`` header and ``{"role":"admin"}`` to promote your own
account → ``/flag`` (which checks the real server-side role) returns the flag.

The flag at ``/flag.txt`` is exposed by no route without an admin session.
"""
import os
import secrets

from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = {1: {"id": 1, "name": "administrator", "role": "admin"}}
SESSIONS = {}
_next = [1000]


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{flag-unavailable-in-dev}"


def _admin_header() -> bool:
    # The flaw: authorization decided from a client-controlled header.
    return request.headers.get("X-Account-Role", "").lower() == "admin"


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kpakpato &middot; espace membre</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#ff5c8a;--ok:#3ddc97;--bad:#ff6b6b;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#331025,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:940px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:720px){.grid{grid-template-columns:1fr}}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  input{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px}
  button{margin-top:12px;background:var(--acc);color:#2b0714;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  button.ghost{background:transparent;border:1px solid var(--line);color:var(--ink)}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  .row{display:flex;gap:8px}.row>*{flex:1}
  .muted{color:var(--mut);font-size:12px}code{font-family:var(--mono);color:#ffd479}
</style></head><body>
<header><div class="logo"><b>Kpakpato</b>&nbsp;Forum</div>
  <div class="tag">espace membre &middot; comptes &amp; profils</div></header>
<main>
  <div class="grid">
    <div class="card">
      <h2>Créer un compte</h2>
      <p class="h">Un nouveau compte a le rôle <code>user</code>. Un jeton de session vous est remis.</p>
      <div class="row"><input id="ru" placeholder="pseudo" value="alice"><input id="rp" placeholder="mot de passe" value="pw"></div>
      <button onclick="reg()">S'inscrire</button>
      <pre id="regOut" class="muted">&mdash;</pre>
    </div>
    <div class="card">
      <h2>Mon profil</h2>
      <p class="h">Affiche le rôle vu côté serveur pour votre jeton.</p>
      <label>Jeton de session</label>
      <input id="tok" placeholder="collez votre jeton">
      <div class="row">
        <button class="ghost" onclick="me()">/me</button>
        <button onclick="getflag()">Récupérer le flag</button>
      </div>
      <pre id="meOut" class="muted">&mdash;</pre>
    </div>
  </div>
  <div class="card">
    <h2>Annuaire des membres</h2>
    <p class="h">Consulter la fiche publique d'un membre par identifiant.</p>
    <div class="row" style="max-width:320px"><input id="uid" value="1"><button class="ghost" onclick="lookup()">Voir la fiche</button></div>
    <pre id="uOut" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function j(url,opts){const r=await fetch(url,opts);let b;try{b=await r.json()}catch(e){b=await r.text()}return{status:r.status,body:b};}
function show(id,o){document.getElementById(id).textContent=typeof o.body==='string'?('['+o.status+'] '+o.body):('['+o.status+']\\n'+JSON.stringify(o.body,null,2));}
async function reg(){
  const u=encodeURIComponent(document.getElementById('ru').value);
  const p=encodeURIComponent(document.getElementById('rp').value);
  const o=await j('/register?user='+u+'&pass='+p);
  if(o.body&&o.body.token)document.getElementById('tok').value=o.body.token;
  show('regOut',o);}
async function me(){const t=encodeURIComponent(document.getElementById('tok').value);show('meOut',await j('/me?token='+t));}
async function getflag(){const t=encodeURIComponent(document.getElementById('tok').value);show('meOut',await j('/flag?token='+t));}
async function lookup(){const id=encodeURIComponent(document.getElementById('uid').value);show('uOut',await j('/api/users/'+id));}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/register")
def register():
    user = request.args.get("user", "")
    if not user:
        return jsonify({"error": "user required"}), 400
    uid = _next[0]
    _next[0] += 1
    USERS[uid] = {"id": uid, "name": user, "role": "user"}
    tok = secrets.token_hex(16)
    SESSIONS[tok] = uid
    return jsonify({"token": tok, "uid": uid})


@app.route("/me")
def me():
    uid = SESSIONS.get(request.args.get("token", ""))
    if uid is None:
        return jsonify({"error": "not logged in"}), 401
    return jsonify(USERS[uid])


@app.route("/admin/users")
def admin_users():
    if not _admin_header():
        return jsonify({"error": "admin only"}), 403
    return jsonify({"users": list(USERS.values())})


@app.route("/api/users/<int:uid>", methods=["GET", "POST"])
def api_users(uid):
    if request.method == "GET":
        u = USERS.get(uid)  # IDOR: no authz on read
        return (jsonify(u), 200) if u else (jsonify({"error": "no such user"}), 404)
    # update: gated only by the forgeable header, then mass-assigns every field.
    if not _admin_header():
        return jsonify({"error": "admin only"}), 403
    u = USERS.get(uid)
    if not u:
        return jsonify({"error": "no such user"}), 404
    patch = request.get_json(silent=True) or {}
    for k, v in patch.items():
        if k != "id":
            u[k] = v
    return jsonify(u)


@app.route("/flag")
def flag():
    uid = SESSIONS.get(request.args.get("token", ""))
    if uid is None:
        return jsonify({"error": "not logged in"}), 401
    if USERS[uid]["role"] != "admin":
        return jsonify({"error": "admin only", "role": USERS[uid]["role"]}), 403
    return jsonify({"flag": _flag()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
