#!/usr/bin/env python3
"""Forum SQLi2 — a second-order SQL injection.

Design (served challenge, per-team flag):

  * ``/register`` and ``/login`` store and check the username with **parameterised
    queries** — safe. So a naive first-order injection at the login form fails.
  * ``/dashboard`` looks up the logged-in user's stored name and then builds a
    second query by **string-formatting that name into SQL** — the second-order
    flaw. The name was attacker-chosen at registration.
  * The per-team flag lives in a separate ``secret`` table, reachable only through
    that injected query.

Intended path: register a username that is a UNION payload
(`zzz' UNION SELECT flag FROM secret-- -`), log in with it (parameterised login
matches the stored row exactly), then open ``/dashboard`` — the stored payload is
now interpolated into SQL and the UNION returns the flag.

The flag at ``/flag.txt`` is loaded into ``secret`` and returned by no route
except through this injection.
"""
import os
import secrets
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)
_SESSIONS = {}


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{flag-unavailable-in-dev}"


# One in-memory DB for the whole process so registrations persist across requests.
_SHARED = sqlite3.connect(":memory:", check_same_thread=False)
_SHARED.execute(
    "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, pass TEXT, role TEXT)"
)
_SHARED.execute("CREATE TABLE secret(flag TEXT)")
_SHARED.execute("INSERT INTO secret(flag) VALUES (?)", (_flag(),))
_SHARED.execute(
    "INSERT INTO users(name, pass, role) VALUES ('admin', ?, 'admin')",
    (secrets.token_hex(16),),
)
_SHARED.commit()


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agora &middot; connexion</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#a78bfa;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#231a40,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:900px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:720px){.grid{grid-template-columns:1fr}}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  input{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px}
  button{margin-top:12px;background:var(--acc);color:#1c1233;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  button.ghost{background:transparent;border:1px solid var(--line);color:var(--ink)}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  .row{display:flex;gap:8px}.row>*{flex:1}.muted{color:var(--mut);font-size:12px}
</style></head><body>
<header><div class="logo"><b>Agora</b>&nbsp;Forum</div>
  <div class="tag">communauté &middot; connexion membre</div></header>
<main>
  <div class="grid">
    <div class="card">
      <h2>Inscription</h2>
      <p class="h">Choisissez un pseudo et un mot de passe.</p>
      <div class="row"><input id="ru" placeholder="pseudo" value="bob"><input id="rp" placeholder="mot de passe" value="pw123"></div>
      <button onclick="reg()">Créer le compte</button>
      <pre id="regOut" class="muted">&mdash;</pre>
    </div>
    <div class="card">
      <h2>Connexion</h2>
      <p class="h">Récupère un identifiant de session (<code>sid</code>).</p>
      <div class="row"><input id="lu" placeholder="pseudo" value="bob"><input id="lp" placeholder="mot de passe" value="pw123"></div>
      <button onclick="login()">Se connecter</button>
      <pre id="logOut" class="muted">&mdash;</pre>
    </div>
  </div>
  <div class="card">
    <h2>Mon tableau de bord</h2>
    <p class="h">Affiche votre rôle à partir de votre session.</p>
    <div class="row" style="max-width:420px"><input id="sid" placeholder="sid"><button class="ghost" onclick="dash()">Ouvrir</button></div>
    <pre id="dashOut" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function jg(path){const r=await fetch(path);let b;try{b=await r.json()}catch(e){b=await r.text()}return{status:r.status,body:b};}
function show(id,o){document.getElementById(id).textContent='['+o.status+']\\n'+(typeof o.body==='string'?o.body:JSON.stringify(o.body,null,2));}
function q(v){return encodeURIComponent(v);}
async function reg(){const o=await jg('/register?user='+q(ru.value)+'&pass='+q(rp.value));show('regOut',o);}
async function login(){const o=await jg('/login?user='+q(lu.value)+'&pass='+q(lp.value));if(o.body&&o.body.sid)sid.value=o.body.sid;show('logOut',o);}
async function dash(){show('dashOut',await jg('/dashboard?sid='+q(sid.value)));}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/register")
def register():
    user = request.args.get("user", "")
    pw = request.args.get("pass", "")
    if not user or not pw:
        return jsonify({"error": "user and pass required"}), 400
    # Safe: parameterised insert. The username is stored verbatim.
    _SHARED.execute(
        "INSERT INTO users(name, pass, role) VALUES (?, ?, 'user')", (user, pw)
    )
    _SHARED.commit()
    return jsonify({"ok": True, "user": user})


@app.route("/login")
def login():
    user = request.args.get("user", "")
    pw = request.args.get("pass", "")
    # Safe: parameterised. Matches the row whose name equals the exact string.
    row = _SHARED.execute(
        "SELECT id, name FROM users WHERE name = ? AND pass = ?", (user, pw)
    ).fetchone()
    if not row:
        return jsonify({"error": "bad credentials"}), 401
    sid = secrets.token_hex(16)
    _SESSIONS[sid] = row[1]  # store the (attacker-chosen) name
    return jsonify({"sid": sid})


@app.route("/dashboard")
def dashboard():
    sid = request.args.get("sid", "")
    name = _SESSIONS.get(sid)
    if name is None:
        return jsonify({"error": "not logged in"}), 401
    # BUG (second order): the stored name is interpolated straight into SQL.
    query = "SELECT role FROM users WHERE name = '%s'" % name
    try:
        rows = _SHARED.execute(query).fetchall()
    except sqlite3.Error as e:
        return jsonify({"error": "query failed", "detail": str(e)}), 400
    return jsonify({"roles": [r[0] for r in rows]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
