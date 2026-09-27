"""CMS Smuggle — a naive ingest parser that processes a pipelined smuggled request.

Design (served challenge, per-team flag):

  * The frontend caches page responses by path (``/page?p=``). ``/admin/flag`` is
    admin-only and returns 403 to ordinary callers.
  * ``/ingest`` accepts a raw body. Its hand-rolled parser splits the body and
    treats a trailing ``SMUGGLED GET <path>`` line as a *second, pipelined*
    request — and processes it with internal (trusted) privileges, caching its
    response under ``<path>``. This models a CL/TE desync: the backend sees a
    request the frontend never authorised.
  * The attacker smuggles ``GET /admin/flag``; its admin response is cached, then
    read back from the cache.

Intended path: ``/ingest`` a body containing ``SMUGGLED GET /admin/flag`` →
``/page?p=/admin/flag`` returns the poisoned (admin) response.

The flag at ``/flag.txt`` is served only to the internal/trusted request the
smuggling forges.
"""
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

CACHE = {}


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{flag-unavailable-in-dev}"


def _handle_internal(path):
    # Backend handling a trusted (internal) request.
    if path == "/admin/flag":
        return _flag()
    return f"internal: {path}"


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaCMS &middot; console d'ingestion</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#4f8cff;--ok:#3ddc97;--bad:#ff6b6b;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#14203a,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  header .logo{font-weight:700;letter-spacing:.5px}
  header .logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:960px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}
  .card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  input,textarea{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px}
  textarea{min-height:120px;resize:vertical;white-space:pre}
  button{margin-top:12px;background:var(--acc);color:#fff;border:0;border-radius:8px;
        padding:9px 16px;font-weight:600;cursor:pointer}
  button.ghost{background:transparent;border:1px solid var(--line);color:var(--ink)}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:720px){.grid{grid-template-columns:1fr}}
  .lock{color:var(--bad);font-size:13px}
  .muted{color:var(--mut);font-size:12px}
  code{font-family:var(--mono);color:#ffd479}
</style></head><body>
<header>
  <div class="logo"><b>Nova</b>CMS</div>
  <div class="tag">edge cache &amp; content ingest &middot; back-office</div>
</header>
<main>
  <div class="card">
    <h2>Passerelle d'ingestion de contenu</h2>
    <p class="h">Le front-office met en cache chaque page par chemin. Les lots de
       contenu bruts sont poussés au backend via <code>/ingest</code>, puis relus
       depuis le cache par <code>/page?p=&lt;chemin&gt;</code>.</p>
    <div class="grid">
      <div>
        <label>Corps du lot (brut)</label>
        <textarea id="body">POST /ingest
content=bonjour tout le monde
</textarea>
        <button onclick="ingest()">Pousser le lot</button>
        <pre id="ingOut" class="muted">&mdash;</pre>
      </div>
      <div>
        <label>Lire une page en cache</label>
        <input id="path" value="/page/accueil">
        <button class="ghost" onclick="readpage()">Lire depuis le cache</button>
        <pre id="pageOut" class="muted">&mdash;</pre>
      </div>
    </div>
  </div>
  <div class="card">
    <h2>Espace administrateur</h2>
    <p class="h">Réservé aux comptes internes de confiance.</p>
    <button class="ghost" onclick="adminFlag()">Ouvrir /admin/flag</button>
    <span class="lock" id="adminLock"></span>
    <pre id="adminOut" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function jreq(url, opts){const r=await fetch(url,opts);const t=await r.text();
  let j;try{j=JSON.parse(t)}catch(e){j=t}return {status:r.status,body:j};}
function show(id,o){document.getElementById(id).textContent=
  typeof o==='string'?o:JSON.stringify(o,null,2);}
async function ingest(){
  const b=document.getElementById('body').value;
  const r=await jreq('/ingest',{method:'POST',body:b});
  show('ingOut',r.body);}
async function readpage(){
  const p=document.getElementById('path').value;
  const r=await jreq('/page?p='+encodeURIComponent(p));
  show('pageOut',r.body);}
async function adminFlag(){
  const r=await jreq('/admin/flag');
  document.getElementById('adminLock').textContent = r.status===200?'':'— 403 accès refusé';
  show('adminOut',r.body);}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/ingest", methods=["POST"])
def ingest():
    body = request.get_data(as_text=True)
    poisoned = []
    for line in body.splitlines():
        line = line.strip()
        # BUG: a smuggled pipelined request is parsed and served as trusted.
        if line.startswith("SMUGGLED GET "):
            path = line[len("SMUGGLED GET ") :].strip()
            CACHE[path] = _handle_internal(path)
            poisoned.append(path)
    return jsonify({"ingested": True, "cache_poisoned": poisoned})


@app.route("/page")
def page():
    p = request.args.get("p", "")
    if p in CACHE:
        return jsonify({"path": p, "cached": CACHE[p]})
    return jsonify({"path": p, "cached": None})


@app.route("/admin/flag")
def admin_flag():
    # Direct external access is not admin.
    return jsonify({"error": "admin only"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
