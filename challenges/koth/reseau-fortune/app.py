#!/usr/bin/env python3
"""Réseau Fortune — shared MLM arena that is ALSO a King-of-the-Hill hill.

FICTION / SIMULATION. A deliberately vulnerable marketing-network ("MLM")
economy shared by all teams. No real money, no SMS (the phone is only a string).
Each team joins with its KotH token (from the CTFd "King of the Hill" page),
gets a distributor account seeded with a little capital, and competes to grow
the richest network. The scorer crowns whichever team is richest right now:

    GET /king   (header X-Scorer-Token: SCORER_SECRET)
      -> {"token": <richest team's KotH token>, "ts": <float>}

The KotH plugin polls /king every tick and awards points to the current holder,
so the team that stays richest longest wins. Legitimate play LOSES money (the
house keeps most of every purchase); registering fake members is free but nets
nothing. You must find a business-logic flaw that mints money faster than your
rivals, and keep the crown.

State is in-memory and per-container (ephemeral, shared across teams).
"""
import os
import re
import threading
import time

from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = os.urandom(16)

SCORER_SECRET = os.environ.get("SCORER_SECRET", "")
# Shared arena: a light per-IP rate limit on /api/* protects every team from one
# team flooding the box. Generous by default (does not hinder legit exploitation);
# lower RATE_PER_MIN in ops if needed. Also put a rate limit at the front proxy.
RATE_PER_MIN = int(os.environ.get("RATE_PER_MIN", "1200"))
_RATE = {}  # ip -> [window_start_min, count]

# --- economy constants (FCFA, integers) ------------------------------------
SEED = 50_000
PRODUCTS = {"starter": 5_000, "vip": 20_000, "booster": 2_000}
RATES_PERMILLE = [200, 80, 40]
PRIME_ACTIVATION = 3_000
PHONE_RE = re.compile(r"^(\+?228)?[0-9]{8}$")
TOKEN_RE = re.compile(r"^[0-9a-f]{16}$")  # KotH token shape (16 hex)

_LOCK = threading.Lock()
_ACCOUNTS = {}  # code -> account
_BY_PHONE = {}  # phone -> code
_ROOT_BY_TOKEN = {}  # koth token -> root code
_SEQ = [0]


def _new_code(prefix="M"):
    _SEQ[0] += 1
    return f"{prefix}{_SEQ[0]:06d}"


def _mk(code, phone, sponsor, wallet=0, token=None):
    acc = {
        "code": code,
        "phone": phone,
        "sponsor": sponsor,
        "wallet": wallet,
        "activated": False,
        "commissions": 0,
        "orders": {},
        "order_seq": 0,
        "token": token,  # set only on team root accounts
    }
    _ACCOUNTS[code] = acc
    if phone:
        _BY_PHONE[phone] = code
    return acc


def _me():
    code = session.get("code")
    return _ACCOUNTS.get(code) if code else None


def _pay_commissions(buyer, cost):
    sponsor_code = buyer["sponsor"]
    for rate in RATES_PERMILLE:
        if not sponsor_code:
            break
        sp = _ACCOUNTS.get(sponsor_code)
        if not sp:
            break
        amount = cost * rate // 1000
        sp["wallet"] += amount
        sp["commissions"] += amount
        sponsor_code = sp["sponsor"]


def _net_gain(acc):
    return acc["wallet"] - (SEED if acc.get("token") else 0)


def _public(acc):
    return {
        "code": acc["code"],
        "phone": acc["phone"],
        "sponsor": acc["sponsor"],
        "wallet": acc["wallet"],
        "activated": acc["activated"],
        "commissions": acc["commissions"],
        "net_gain": _net_gain(acc),
    }


@app.before_request
def _rate_limit():
    # Only throttle player API calls; leave "/", "/king" and static alone.
    if not request.path.startswith("/api/"):
        return None
    ip = (
        (request.headers.get("X-Forwarded-For", request.remote_addr or "?"))
        .split(",")[0]
        .strip()
    )
    window = int(time.time() // 60)
    with _LOCK:
        slot = _RATE.get(ip)
        if not slot or slot[0] != window:
            _RATE[ip] = [window, 0]
            slot = _RATE[ip]
        slot[1] += 1
        over = slot[1] > RATE_PER_MIN
    if over:
        return jsonify(error="trop de requêtes, réessaie dans une minute"), 429
    return None


INDEX_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Réseau Fortune — l'arène du plus riche</title>
<style>
  :root{--green:#006a4e;--yellow:#ffce00;--red:#d21034;--ink:#14211d;--pane:#fff;--bg:#f3f6f4;--muted:#5c6b64}
  *{box-sizing:border-box}
  body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  .sim{background:var(--red);color:#fff;text-align:center;padding:.45rem;font-size:.85rem;font-weight:600}
  header{background:linear-gradient(135deg,#7a1020,var(--red));color:#fff;padding:1.1rem 1rem;position:relative;overflow:hidden}
  header .tri{position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--green) 33%,var(--yellow) 33% 66%,var(--red) 66%)}
  header h1{margin:.2rem 0;font-size:1.5rem}
  header p{margin:0;opacity:.92;font-size:.9rem}
  .wrap{max-width:960px;margin:0 auto;padding:1rem}
  .card{background:var(--pane);border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:1rem;margin:.8rem 0}
  .grid{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
  h2{margin:.2rem 0 .6rem;font-size:1.1rem}
  label{display:block;font-size:.8rem;color:var(--muted);margin:.4rem 0 .15rem}
  input,select{width:100%;padding:.55rem;border:1px solid #cdd6d1;border-radius:8px;font-size:.95rem}
  button{background:var(--red);color:#fff;border:0;border-radius:8px;padding:.6rem .9rem;font-weight:600;cursor:pointer;font-size:.9rem}
  button.ghost{background:#eef2f0;color:var(--ink)}
  .stat{font-size:1.7rem;font-weight:800;color:var(--red)}
  .muted{color:var(--muted);font-size:.85rem}
  .row{display:flex;gap:.5rem;flex-wrap:wrap;align-items:end;justify-content:space-between}
  .prod{border:1px solid #e2e8e4;border-radius:10px;padding:.8rem;text-align:center}
  .prod .price{font-weight:800;color:var(--red);margin:.3rem 0}
  table{width:100%;border-collapse:collapse;font-size:.9rem}
  th,td{text-align:left;padding:.4rem;border-bottom:1px solid #eef2f0}
  .crown{color:var(--yellow)}
  .hidden{display:none}
  .toast{position:fixed;bottom:1rem;left:50%;transform:translateX(-50%);background:var(--ink);color:#fff;padding:.6rem 1rem;border-radius:8px;opacity:0;transition:.25s;font-size:.9rem}
  .toast.show{opacity:1}
  footer{text-align:center;color:var(--muted);font-size:.8rem;padding:1.5rem}
</style>
</head>
<body>
<div class="sim">⚠️ SIMULATION — argent fictif, aucune valeur réelle · aucun SMS n'est jamais envoyé</div>
<header>
  <div class="tri"></div>
  <h1>👑 Réseau Fortune</h1>
  <p>L'arène partagée : le réseau le plus riche tient la couronne et marque les points.</p>
</header>
<div class="wrap">

  <div id="join" class="card">
    <h2>Entrer dans l'arène</h2>
    <p class="muted">Collez votre <b>jeton KotH</b> (page « King of the Hill » de la plateforme, 16 caractères hex).</p>
    <label>Jeton KotH</label>
    <input id="j-token" placeholder="0123456789abcdef">
    <div style="margin-top:.6rem"><button onclick="join()">Rejoindre</button></div>
  </div>

  <div id="app" class="hidden">
    <div class="card">
      <div class="row">
        <div><div class="muted">Solde du réseau</div><div class="stat"><span id="wallet">0</span> FCFA</div></div>
        <div style="text-align:right"><div class="muted">Gain net (score)</div>
          <div class="stat" id="net">0</div>
          <div class="muted">code : <span id="mycode">—</span></div></div>
      </div>
    </div>

    <div class="card">
      <h2>🏁 Classement — le réseau le plus riche</h2>
      <table><thead><tr><th>#</th><th>Équipe</th><th>Gain net</th></tr></thead><tbody id="board"></tbody></table>
    </div>

    <div class="card">
      <h2>Boutique</h2>
      <div class="grid" id="shop"></div>
    </div>

    <div class="grid">
      <div class="card"><h2>Parrainer</h2><label>Numéro du filleul</label>
        <input id="f-phone" placeholder="228…"><div style="margin-top:.6rem"><button onclick="sponsor()">Ajouter</button></div>
        <div id="filleuls" class="muted" style="margin-top:.6rem"></div></div>
      <div class="card"><h2>Prime d'activation</h2><label>Code du filleul</label>
        <input id="b-code" placeholder="M000001"><div style="margin-top:.6rem"><button onclick="bonus()">Encaisser</button></div></div>
      <div class="card"><h2>Transfert</h2><label>Vers</label><input id="t-code" placeholder="M000001">
        <label>Montant</label><input id="t-amount" type="number" value="5000">
        <div style="margin-top:.6rem"><button onclick="transfer()">Envoyer</button></div></div>
      <div class="card"><h2>Remboursement</h2><label>N° commande</label><input id="ref-order" type="number" placeholder="1">
        <div style="margin-top:.6rem"><button onclick="refund()">Rembourser</button></div></div>
    </div>
  </div>

</div>
<footer>Réseau Fortune — arène de démonstration NCTF26. Contenu fictif.</footer>
<div id="toast" class="toast"></div>
<script>
const PRODUCTS={starter:{n:"Pack Starter",p:5000},vip:{n:"Pack VIP",p:20000},booster:{n:"Booster",p:2000}};
let FILLEULS=[];
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200);}
async function api(path,body){const o={method:body?'POST':'GET',headers:{'Content-Type':'application/json'},credentials:'same-origin'};
  if(body)o.body=JSON.stringify(body);const r=await fetch(path,o);let j={};try{j=await r.json()}catch(e){}return{ok:r.ok,status:r.status,j};}
function renderShop(){document.getElementById('shop').innerHTML=Object.entries(PRODUCTS).map(([k,v])=>
  `<div class="prod"><b>${v.n}</b><div class="price">${v.p.toLocaleString('fr')} FCFA</div><button onclick="buy('${k}')">Acheter</button></div>`).join('');}
async function join(){const {ok,j}=await api('/api/join',{token:document.getElementById('j-token').value.trim()});
  toast(ok?('Dans l\\'arène : '+j.code):(j.error||'jeton invalide'));if(ok){document.getElementById('join').classList.add('hidden');document.getElementById('app').classList.remove('hidden');refresh();}}
async function refresh(){const {ok,j}=await api('/api/me');if(ok){
  document.getElementById('wallet').textContent=(j.wallet||0).toLocaleString('fr');
  document.getElementById('net').textContent=(j.net_gain||0).toLocaleString('fr');
  document.getElementById('mycode').textContent=j.code;
  document.getElementById('filleuls').innerHTML=FILLEULS.length?('Filleuls : '+FILLEULS.map(f=>`<code>${f}</code>`).join(' ')):'';}
  const lb=await api('/api/leaderboard');
  if(lb.ok)document.getElementById('board').innerHTML=(lb.j||[]).map((r,i)=>
    `<tr><td>${i==0?'<span class=crown>👑</span>':(i+1)}</td><td>${r.team}</td><td>${(r.net_gain||0).toLocaleString('fr')}</td></tr>`).join('');
}
async function buy(k){const {ok,j}=await api('/api/buy',{product:k,qty:1});toast(ok?('Commande n°'+j.order_id):(j.error||'échec'));refresh();}
async function sponsor(){const {ok,j}=await api('/api/register',{phone:document.getElementById('f-phone').value,parrain_code:document.getElementById('mycode').textContent});
  if(ok){FILLEULS.push(j.code);toast('Filleul : '+j.code);}else toast(j.error||'échec');refresh();}
async function bonus(){const {ok,j}=await api('/api/bonus/activation',{filleul_code:document.getElementById('b-code').value});toast(ok?('+'+j.prime+' FCFA'):(j.error||'échec'));refresh();}
async function transfer(){const {ok,j}=await api('/api/transfer',{to_code:document.getElementById('t-code').value,montant:parseInt(document.getElementById('t-amount').value,10)});toast(ok?'Transfert OK':(j.error||'échec'));refresh();}
async function refund(){const {ok,j}=await api('/api/refund',{order_id:parseInt(document.getElementById('ref-order').value,10)});toast(ok?('Remboursé '+j.refunded):(j.error||'échec'));refresh();}
renderShop();setInterval(()=>{if(!document.getElementById('app').classList.contains('hidden'))refresh();},15000);
</script>
</body>
</html>"""


# --- routes -----------------------------------------------------------------
@app.get("/")
def index():
    return INDEX_HTML


@app.post("/api/join")
def join():
    data = request.get_json(silent=True) or request.form
    token = (data.get("token") or "").strip().lower()
    if not TOKEN_RE.match(token):
        return jsonify(error="jeton KotH invalide (16 hex)"), 400
    with _LOCK:
        code = _ROOT_BY_TOKEN.get(token)
        if not code:
            code = _new_code("T")
            acc = _mk(code, None, None, wallet=SEED, token=token)
            acc["activated"] = True
            _ROOT_BY_TOKEN[token] = code
    session["code"] = code
    return jsonify(ok=True, code=code, referral_code=code)


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or request.form
    phone = (data.get("phone") or "").strip()
    parrain = (data.get("parrain_code") or "").strip() or None
    if not PHONE_RE.match(phone):  # never verified: no OTP, no SMS
        return jsonify(error="numéro invalide (format +228XXXXXXXX)"), 400
    with _LOCK:
        if phone in _BY_PHONE:
            return jsonify(error="numéro déjà inscrit"), 409
        if parrain and parrain not in _ACCOUNTS:
            return jsonify(error="code de parrainage inconnu"), 400
        acc = _mk(_new_code(), phone, parrain)
    return jsonify(ok=True, code=acc["code"], parrain=parrain)


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or request.form
    phone = (data.get("phone") or "").strip()
    code = _BY_PHONE.get(phone)
    if not code:
        return jsonify(error="numéro inconnu"), 404
    session["code"] = code
    return jsonify(ok=True, code=code)


@app.get("/api/me")
def me():
    acc = _me()
    if not acc:
        return jsonify(error="non connecté"), 401
    return jsonify(_public(acc))


@app.post("/api/buy")
def buy():
    acc = _me()
    if not acc:
        return jsonify(error="non connecté"), 401
    data = request.get_json(silent=True) or request.form
    product = (data.get("product") or "").strip()
    if product not in PRODUCTS:
        return jsonify(error="produit inconnu"), 400
    try:
        qty = int(data.get("qty", 1))
    except (TypeError, ValueError):
        return jsonify(error="quantité invalide"), 400
    if qty <= 0:
        return jsonify(error="quantité invalide"), 400
    cost = PRODUCTS[product] * qty
    with _LOCK:
        if acc["wallet"] < cost:
            return jsonify(error="solde insuffisant"), 402
        acc["wallet"] -= cost
        acc["order_seq"] += 1
        oid = acc["order_seq"]
        acc["orders"][oid] = {"product": product, "cost": cost, "refunded": False}
        if product == "starter":
            acc["activated"] = True
        _pay_commissions(acc, cost)
    return jsonify(ok=True, order_id=oid, spent=cost, wallet=acc["wallet"])


@app.post("/api/bonus/activation")
def bonus_activation():
    acc = _me()
    if not acc:
        return jsonify(error="non connecté"), 401
    data = request.get_json(silent=True) or request.form
    filleul_code = (data.get("filleul_code") or "").strip()
    with _LOCK:
        f = _ACCOUNTS.get(filleul_code)
        if not f or f["sponsor"] != acc["code"]:
            return jsonify(error="ce n'est pas votre filleul"), 403
        if not f["activated"]:
            return jsonify(error="filleul non activé"), 400
        acc["wallet"] += PRIME_ACTIVATION  # BUG A: not idempotent
        acc["commissions"] += PRIME_ACTIVATION
    return jsonify(ok=True, prime=PRIME_ACTIVATION, wallet=acc["wallet"])


@app.post("/api/refund")
def refund():
    acc = _me()
    if not acc:
        return jsonify(error="non connecté"), 401
    data = request.get_json(silent=True) or request.form
    try:
        oid = int(data.get("order_id"))
    except (TypeError, ValueError):
        return jsonify(error="commande invalide"), 400
    with _LOCK:
        order = acc["orders"].get(oid)
        if not order:
            return jsonify(error="commande introuvable"), 404
        if order["refunded"]:
            return jsonify(error="déjà remboursée"), 400
        order["refunded"] = True
        acc["wallet"] += order["cost"]  # BUG B: commission never clawed back
    return jsonify(ok=True, refunded=order["cost"], wallet=acc["wallet"])


@app.post("/api/transfer")
def transfer():
    acc = _me()
    if not acc:
        return jsonify(error="non connecté"), 401
    data = request.get_json(silent=True) or request.form
    to_code = (data.get("to_code") or "").strip()
    try:
        montant = int(data.get("montant"))
    except (TypeError, ValueError):
        return jsonify(error="montant invalide"), 400
    if montant <= 0:
        return jsonify(error="montant invalide"), 400
    with _LOCK:
        dest = _ACCOUNTS.get(to_code)
        if not dest:
            return jsonify(error="destinataire inconnu"), 404
        if acc["wallet"] < montant:
            return jsonify(error="solde insuffisant"), 402
        acc["wallet"] -= montant
        dest["wallet"] += montant
    return jsonify(ok=True, wallet=acc["wallet"])


@app.get("/api/leaderboard")
def leaderboard():
    with _LOCK:
        rows = sorted(
            (
                {"team": _ACCOUNTS[c]["code"], "net_gain": _net_gain(_ACCOUNTS[c])}
                for c in _ROOT_BY_TOKEN.values()
            ),
            key=lambda r: r["net_gain"],
            reverse=True,
        )
    return jsonify(rows)


@app.get("/king")
def king():
    # Scorer-only. Returns the KotH token of the currently richest network.
    if not SCORER_SECRET or request.headers.get("X-Scorer-Token") != SCORER_SECRET:
        return jsonify(error="forbidden"), 403
    best_token, best_gain = "", None
    with _LOCK:
        for token, code in _ROOT_BY_TOKEN.items():
            g = _net_gain(_ACCOUNTS[code])
            if best_gain is None or g > best_gain:
                best_gain, best_token = g, token
    # Only crown a team that is actually ahead (positive net gain).
    if best_gain is None or best_gain <= 0:
        return jsonify(token="", ts=time.time())
    return jsonify(token=best_token, ts=time.time())


if __name__ == "__main__":
    if not SCORER_SECRET:
        raise SystemExit("SCORER_SECRET is required")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
