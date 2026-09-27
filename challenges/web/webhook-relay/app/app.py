"""Webhook Relay — a callback validator that can be tricked into SSRF.

Design (served challenge, per-team flag):

  * ``/webhook/deliver?url=`` validates the callback URL then fetches it
    server-side. The validation is a substring check: the URL must *contain*
    ``hooks.partner.example`` (the allow-listed partner host). That is trivially
    bypassed — e.g. ``http://169.254.169.254/...#hooks.partner.example`` contains
    the string but resolves to the internal metadata host.
  * The internal metadata host mints a deploy token and, at
    ``/latest/meta-data/flag``, returns the instance secret. It is reachable only
    from the server.

Intended path: pass a URL that satisfies the substring check but points at the
internal metadata flag endpoint.

The flag at ``/flag.txt`` is exposed only through the internal metadata host the
relayed request reaches server-side.
"""
import os
from urllib.parse import urlparse

from flask import Flask, jsonify, request

app = Flask(__name__)

ALLOWED_SUBSTRING = "hooks.partner.example"


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{flag-unavailable-in-dev}"


def _server_fetch(url):
    # Server-side fetch. The internal metadata host is only reachable here.
    host = urlparse(url).hostname
    if host == "169.254.169.254":
        path = urlparse(url).path
        if path == "/latest/meta-data/flag":
            return _flag()
        if path == "/latest/meta-data/role":
            return "backup-restore"
        return "<metadata>"
    return "<partner webhook ack>"


INDEX_HTML = (
    """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RelayHook &middot; callbacks</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#f472b6;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#331025,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:880px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  input{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px}
  button{margin-top:12px;background:var(--acc);color:#2b0714;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap;word-break:break-all}
  code{font-family:var(--mono);color:#ffd479}.muted{color:var(--mut);font-size:12px}
  .badge{display:inline-block;background:#0c1120;border:1px solid var(--line);border-radius:20px;
        padding:2px 10px;font-size:12px;color:var(--mut)}
</style></head><body>
<header><div class="logo"><b>Relay</b>Hook</div>
  <div class="tag">livraison de webhooks partenaires</div></header>
<main>
  <div class="card">
    <h2>Tester une livraison de callback</h2>
    <p class="h">Le relais récupère votre URL de callback côté serveur et renvoie
       la réponse. Politique&nbsp;: l'URL doit référencer l'hôte partenaire
       <span class="badge">"""
    + ALLOWED_SUBSTRING
    + """</span>.</p>
    <label>URL de callback</label>
    <input id="url" value="https://hooks.partner.example/deliver/ack">
    <button onclick="deliver()">Livrer</button>
    <pre id="out" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function deliver(){
  const u=encodeURIComponent(document.getElementById('url').value);
  const r=await fetch('/webhook/deliver?url='+u);
  let b;try{b=await r.json()}catch(e){b=await r.text()}
  document.getElementById('out').textContent='['+r.status+']\\n'+
    (typeof b==='string'?b:JSON.stringify(b,null,2));}
</script>
</body></html>"""
)


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/webhook/deliver")
def deliver():
    url = request.args.get("url", "")
    # BUG: a substring check, not a host check — bypassable via fragment/userinfo.
    if ALLOWED_SUBSTRING not in url:
        return jsonify({"error": "callback host not allowed"}), 403
    return jsonify({"delivered": True, "response": _server_fetch(url)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
