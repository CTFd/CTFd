"""Forum Protopoll — a recursive merge that pollutes a shared config object.

Design (served challenge, per-team flag):

  * ``/settings`` deep-merges user JSON into a shared server-side config with no
    key allow-list. The merge can therefore reach keys the user never should,
    the server-side equivalent of prototype pollution.
  * The renderer consults ``config["render_hook"]`` before serving a page. That
    key is meant to stay empty, but a polluting merge sets it. The ``emit-flag``
    hook reads the instance secret.

Intended path: ``/settings`` merge ``{"render_hook":"emit-flag"}`` → ``/render``
runs the polluted hook.

The flag at ``/flag.txt`` is served by no route; it only appears as the output of
the render hook the pollution enabled.
"""
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# Shared config template. `render_hook` must never be set by a user.
CONFIG = {"theme": "light", "page_size": 20}


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{flag-unavailable-in-dev}"


def deep_merge(dst, src):
    for k, v in src.items():
        # BUG: no allow-list of merge keys; any key can be introduced/overwritten.
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


def run_hook(hook):
    if hook == "emit-flag":
        return _flag()
    return None


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Protopoll &middot; réglages</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#ff9f43;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#33230a,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:900px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:720px){.grid{grid-template-columns:1fr}}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  textarea{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px;min-height:120px;resize:vertical}
  button{margin-top:12px;background:var(--acc);color:#2b1c05;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  button.ghost{background:transparent;border:1px solid var(--line);color:var(--ink)}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  code{font-family:var(--mono);color:#ffd479}.muted{color:var(--mut);font-size:12px}
</style></head><body>
<header><div class="logo"><b>Proto</b>poll</div>
  <div class="tag">forum communautaire &middot; réglages d'affichage</div></header>
<main>
  <div class="grid">
    <div class="card">
      <h2>Réglages d'affichage</h2>
      <p class="h">Envoie un patch JSON&nbsp;: il est fusionné en profondeur dans la
         configuration du forum (thème, taille de page…).</p>
      <label>Patch de configuration (JSON)</label>
      <textarea id="cfg">{
  "theme": "dark",
  "page_size": 30
}</textarea>
      <button onclick="save()">Enregistrer</button>
      <pre id="cfgOut" class="muted">&mdash;</pre>
    </div>
    <div class="card">
      <h2>Aperçu de la page</h2>
      <p class="h">Rend la page d'accueil du forum avec la configuration courante.</p>
      <button class="ghost" onclick="render()">Rendre la page</button>
      <pre id="rOut" class="muted">&mdash;</pre>
    </div>
  </div>
</main>
<script>
async function save(){
  let obj;try{obj=JSON.parse(document.getElementById('cfg').value)}
  catch(e){document.getElementById('cfgOut').textContent='JSON invalide : '+e;return;}
  const r=await fetch('/settings',{method:'POST',
      headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});
  document.getElementById('cfgOut').textContent=JSON.stringify(await r.json(),null,2);}
async function render(){
  const r=await fetch('/render');
  document.getElementById('rOut').textContent=JSON.stringify(await r.json(),null,2);}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/settings", methods=["POST"])
def settings():
    body = request.get_json(silent=True) or {}
    deep_merge(CONFIG, body)
    return jsonify({"config_keys": sorted(CONFIG)})


@app.route("/render")
def render():
    out = run_hook(CONFIG.get("render_hook", ""))
    page = {"theme": CONFIG.get("theme"), "rendered": True}
    if out is not None:
        page["hook_output"] = out
    return jsonify(page)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
