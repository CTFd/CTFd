#!/usr/bin/env python3
"""KékéliCash — réseau de distribution (démo). SERVED per-team instance.

FICTION / SIMULATION. This is a deliberately vulnerable marketing-network
("MLM") sandbox. No real money, no SMS is ever sent: the phone number is only a
string. Your distributor account (`ROOT`) starts with a little seed capital.
The platform pays commissions up the sponsor chain when a member activates.

Goal: beat the economy. Grow your account balance past the jackpot threshold
and the platform hands you the flag. Legitimate play LOSES money (the house
keeps most of every purchase), so a naive strategy — even registering a horde
of fake members — nets nothing. You must find a *business-logic* flaw.

State is in-memory and per-container (ephemeral). Single-tenant: this instance
is yours.
"""
import os
import re
import threading

from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = os.urandom(16)

# --- economy constants (FCFA, integers) ------------------------------------
SEED = 50_000  # ROOT starting capital
JACKPOT = 1_000_000  # net gain over SEED that unlocks the flag
FLAG_AT = SEED + JACKPOT  # absolute balance that unlocks the flag
PRODUCTS = {"starter": 5_000, "vip": 20_000, "booster": 2_000}
RATES_PERMILLE = [200, 80, 40]  # L1 20% / L2 8% / L3 4% ; house keeps the rest
PRIME_ACTIVATION = 3_000  # sponsor bonus when a filleul activates
PHONE_RE = re.compile(r"^(\+?228)?[0-9]{8}$")  # "looks Togolese" — never verified

_LOCK = threading.Lock()
_ACCOUNTS = {}  # code -> account dict
_BY_PHONE = {}  # phone -> code
_SEQ = [0]


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{local-dev-flag}"


def _new_code(prefix="M"):
    _SEQ[0] += 1
    return f"{prefix}{_SEQ[0]:06d}"


def _mk(code, phone, sponsor, wallet=0):
    acc = {
        "code": code,
        "phone": phone,
        "sponsor": sponsor,  # sponsor code or None
        "wallet": wallet,
        "activated": False,
        "commissions": 0,  # stat only
        "orders": {},  # order_id -> {product, cost, refunded}
        "order_seq": 0,
    }
    _ACCOUNTS[code] = acc
    if phone:
        _BY_PHONE[phone] = code
    return acc


def _seed_root():
    if "ROOT" not in _ACCOUNTS:
        _mk("ROOT", "22890000000", None, wallet=SEED)
        _ACCOUNTS["ROOT"]["activated"] = True


_seed_root()


def _me():
    code = session.get("code")
    return _ACCOUNTS.get(code) if code else None


def _pay_commissions(buyer, cost):
    """Pay the sponsor chain of `buyer`, up to 3 levels."""
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


def _public(acc):
    return {
        "code": acc["code"],
        "phone": acc["phone"],
        "sponsor": acc["sponsor"],
        "wallet": acc["wallet"],
        "activated": acc["activated"],
        "commissions": acc["commissions"],
        "net_gain": acc["wallet"] - (SEED if acc["code"] == "ROOT" else 0),
    }


INDEX_HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KékéliCash — Réseau Fortune</title>
<style>
  :root{--green:#006a4e;--yellow:#ffce00;--red:#d21034;--ink:#14211d;--pane:#fff;--bg:#f3f6f4;--muted:#5c6b64}
  *{box-sizing:border-box}
  body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  .sim{background:var(--red);color:#fff;text-align:center;padding:.45rem;font-size:.85rem;font-weight:600}
  header{background:linear-gradient(135deg,var(--green),#00875f);color:#fff;padding:1.1rem 1rem;position:relative;overflow:hidden}
  header .tri{position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--green) 33%,var(--yellow) 33% 66%,var(--red) 66%)}
  header h1{margin:.2rem 0;font-size:1.5rem}
  header p{margin:0;opacity:.9;font-size:.9rem}
  .wrap{max-width:960px;margin:0 auto;padding:1rem}
  .card{background:var(--pane);border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:1rem;margin:.8rem 0}
  .grid{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
  h2{margin:.2rem 0 .6rem;font-size:1.1rem}
  label{display:block;font-size:.8rem;color:var(--muted);margin:.4rem 0 .15rem}
  input,select{width:100%;padding:.55rem;border:1px solid #cdd6d1;border-radius:8px;font-size:.95rem}
  button{background:var(--green);color:#fff;border:0;border-radius:8px;padding:.6rem .9rem;font-weight:600;cursor:pointer;font-size:.9rem}
  button.ghost{background:#eef2f0;color:var(--ink)}
  button:hover{filter:brightness(1.05)}
  .row{display:flex;gap:.5rem;flex-wrap:wrap;align-items:end}
  .stat{font-size:1.7rem;font-weight:800;color:var(--green)}
  .muted{color:var(--muted);font-size:.85rem}
  .prod{border:1px solid #e2e8e4;border-radius:10px;padding:.8rem;text-align:center}
  .prod .price{font-weight:800;color:var(--red);margin:.3rem 0}
  .bar{height:12px;background:#e6 ebe8;border-radius:99px;overflow:hidden;background:#e6ebe8}
  .bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--yellow),var(--red))}
  .flag{background:#062;color:#bfffe0;padding:.7rem;border-radius:8px;font-family:ui-monospace,monospace;word-break:break-all}
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
  <h1>KékéliCash 💡</h1>
  <p>Le réseau qui fait fructifier votre argent. Parrainez, activez, encaissez.</p>
</header>
<div class="wrap">

  <div id="auth">
    <div class="grid">
      <div class="card">
        <h2>Rejoindre le réseau</h2>
        <p class="muted">Il vous faut un numéro togolais et le code d'un parrain.</p>
        <label>Numéro de téléphone</label>
        <input id="r-phone" placeholder="+228 90 00 00 00">
        <label>Code de parrainage</label>
        <input id="r-parrain" value="ROOT">
        <div style="margin-top:.6rem"><button onclick="register()">Créer mon compte</button></div>
      </div>
      <div class="card">
        <h2>Se connecter</h2>
        <p class="muted">Votre compte distributeur de démonstration : <b>ROOT</b> (numéro 22890000000).</p>
        <label>Numéro de téléphone</label>
        <input id="l-phone" value="22890000000">
        <div style="margin-top:.6rem"><button onclick="login()">Connexion</button></div>
      </div>
    </div>
  </div>

  <div id="app" class="hidden">
    <div class="card">
      <div class="row" style="justify-content:space-between">
        <div>
          <div class="muted">Solde du portefeuille</div>
          <div class="stat"><span id="wallet">0</span> FCFA</div>
        </div>
        <div style="text-align:right">
          <div class="muted">Votre code de parrainage</div>
          <div class="stat" id="mycode" style="color:var(--red)">—</div>
          <button class="ghost" onclick="logout()">Se déconnecter</button>
        </div>
      </div>
      <div style="margin-top:.8rem">
        <div class="muted">Objectif Jackpot — <span id="jackpotpct">0</span>%</div>
        <div class="bar"><i id="jackpotbar" style="width:0%"></i></div>
        <div style="margin-top:.6rem"><button onclick="claimFlag()">🏆 Réclamer le bonus Jackpot</button>
          <span id="flagbox"></span></div>
      </div>
    </div>

    <div class="card">
      <h2>Boutique — activez votre compte, gonflez vos commissions</h2>
      <div class="grid" id="shop"></div>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Parrainer un filleul</h2>
        <p class="muted">Le numéro n'est pas vérifié — invitez qui vous voulez.</p>
        <label>Numéro du filleul</label>
        <input id="f-phone" placeholder="228…">
        <div style="margin-top:.6rem"><button onclick="sponsor()">Ajouter le filleul</button></div>
        <div id="filleuls" class="muted" style="margin-top:.6rem"></div>
      </div>
      <div class="card">
        <h2>Prime d'activation</h2>
        <p class="muted">Touchez la prime quand un filleul (activé) rejoint.</p>
        <label>Code du filleul</label>
        <input id="b-code" placeholder="M000001">
        <div style="margin-top:.6rem"><button onclick="bonus()">Encaisser la prime</button></div>
      </div>
      <div class="card">
        <h2>Transfert</h2>
        <label>Vers le code</label>
        <input id="t-code" placeholder="M000001">
        <label>Montant (FCFA)</label>
        <input id="t-amount" type="number" value="5000">
        <div style="margin-top:.6rem"><button onclick="transfer()">Envoyer</button></div>
      </div>
      <div class="card">
        <h2>Remboursement</h2>
        <p class="muted">Annulez une commande (n° affiché à l'achat).</p>
        <label>N° de commande</label>
        <input id="ref-order" type="number" placeholder="1">
        <div style="margin-top:.6rem"><button onclick="refund()">Rembourser</button></div>
      </div>
    </div>
  </div>

</div>
<footer>KékéliCash — plateforme de démonstration NCTF26. Contenu fictif.</footer>
<div id="toast" class="toast"></div>

<script>
const PRODUCTS = {starter:{n:"Pack Starter",p:5000,d:"Active votre compte et débloque les commissions."},
                  vip:{n:"Pack VIP",p:20000,d:"Commissions maximales sur votre lignée."},
                  booster:{n:"Booster",p:2000,d:"Un coup de pouce à votre visibilité."}};
let FILLEULS = [];
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200);}
async function api(path, body){
  const o={method:body?'POST':'GET',headers:{'Content-Type':'application/json'},credentials:'same-origin'};
  if(body)o.body=JSON.stringify(body);
  const r=await fetch(path,o); let j={}; try{j=await r.json()}catch(e){}
  return {ok:r.ok,status:r.status,j};
}
function renderShop(){
  document.getElementById('shop').innerHTML=Object.entries(PRODUCTS).map(([k,v])=>
    `<div class="prod"><div><b>${v.n}</b></div><div class="price">${v.p.toLocaleString('fr')} FCFA</div>
     <div class="muted">${v.d}</div><div style="margin-top:.5rem"><button onclick="buy('${k}')">Acheter</button></div></div>`).join('');
}
async function refresh(){
  const {ok,j}=await api('/api/me');
  if(!ok){show(false);return;}
  show(true);
  document.getElementById('wallet').textContent=(j.wallet||0).toLocaleString('fr');
  document.getElementById('mycode').textContent=j.code;
  const pct=Math.max(0,Math.min(100,Math.round((j.wallet/1050000)*100)));
  document.getElementById('jackpotpct').textContent=pct;
  document.getElementById('jackpotbar').style.width=pct+'%';
  document.getElementById('filleuls').innerHTML=FILLEULS.length?('Filleuls : '+FILLEULS.map(f=>`<code>${f}</code>`).join(' ')):'';
}
function show(logged){document.getElementById('app').classList.toggle('hidden',!logged);
  document.getElementById('auth').classList.toggle('hidden',logged);}
async function register(){
  const {ok,j}=await api('/api/register',{phone:document.getElementById('r-phone').value,parrain_code:document.getElementById('r-parrain').value});
  toast(ok?('Compte créé : '+j.code):(j.error||'échec'));
  if(ok){document.getElementById('l-phone').value=document.getElementById('r-phone').value;login();}
}
async function login(){
  const {ok,j}=await api('/api/login',{phone:document.getElementById('l-phone').value});
  toast(ok?('Connecté : '+j.code):(j.error||'numéro inconnu')); if(ok)refresh();
}
async function logout(){await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});FILLEULS=[];show(false);}
async function buy(k){const {ok,j}=await api('/api/buy',{product:k,qty:1});
  toast(ok?('Acheté — commande n°'+j.order_id):(j.error||'échec'));refresh();}
async function sponsor(){const {ok,j}=await api('/api/register',{phone:document.getElementById('f-phone').value,parrain_code:document.getElementById('mycode').textContent});
  if(ok){FILLEULS.push(j.code);toast('Filleul ajouté : '+j.code);}else toast(j.error||'échec');refresh();}
async function bonus(){const {ok,j}=await api('/api/bonus/activation',{filleul_code:document.getElementById('b-code').value});
  toast(ok?('+'+j.prime+' FCFA de prime'):(j.error||'échec'));refresh();}
async function transfer(){const {ok,j}=await api('/api/transfer',{to_code:document.getElementById('t-code').value,montant:parseInt(document.getElementById('t-amount').value,10)});
  toast(ok?'Transfert effectué':(j.error||'échec'));refresh();}
async function refund(){const {ok,j}=await api('/api/refund',{order_id:parseInt(document.getElementById('ref-order').value,10)});
  toast(ok?('Remboursé : '+j.refunded+' FCFA'):(j.error||'échec'));refresh();}
async function claimFlag(){const {ok,j}=await api('/flag');
  document.getElementById('flagbox').innerHTML=ok&&j.flag?(`<div class="flag">${j.flag}</div>`):`<span class="muted"> ${j.error||'pas encore'} (solde ${j.wallet||''}/${j.need||''})</span>`;}
renderShop();refresh();
</script>
</body>
</html>"""


# --- routes -----------------------------------------------------------------
@app.get("/")
def index():
    return INDEX_HTML


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or request.form
    phone = (data.get("phone") or "").strip()
    parrain = (data.get("parrain_code") or "").strip() or None
    # The number must "look" Togolese — but it is NEVER verified (no OTP/SMS).
    if not PHONE_RE.match(phone):
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
    # Quantity must be a positive integer. (Yes, we check this — no negative
    # quantity tricks here.)
    try:
        qty = int(data.get("qty", 1))
    except (TypeError, ValueError):
        return jsonify(error="quantité invalide"), 400
    if qty <= 0:
        return jsonify(error="quantité invalide"), 400
    price = PRODUCTS[product]
    cost = price * qty
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
        # Prime versée au parrain à l'activation d'un filleul.
        acc["wallet"] += PRIME_ACTIVATION
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
        acc["wallet"] += order["cost"]
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


@app.get("/flag")
def flag():
    acc = _me()
    if not acc:
        return jsonify(error="non connecté"), 401
    if acc["wallet"] >= FLAG_AT:
        return jsonify(ok=True, flag=_flag())
    return (
        jsonify(
            error="fonds insuffisants pour le jackpot",
            wallet=acc["wallet"],
            need=FLAG_AT,
        ),
        403,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
